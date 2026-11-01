"""Bouwt data/feed.json: het enige bestand dat de app leest.

Gebruik (vanuit de hoofdmap):
    python -m pipeline.build --provider feeds      # live ophalen (netwerk nodig)
    python -m pipeline.build --provider snapshot   # vastgelegde momentopname

Lagen:
    data/raw/<run>.json        ruw, ongewijzigd per run (alleen toevoegen)
    data/enrichment/<id>.json  verrijking per artikel (cache, één keer per publicatie)
    data/feed.json             klaar voor de app
"""
import argparse
import json
import math
import os
import sys
from collections import Counter, defaultdict
from datetime import datetime, timedelta, timezone

from . import config as cfg
from .dedupe import dedupe
from . import deepdives as deepdives_mod
from .digest import weekly_digests
from . import feedback as feedback_mod
from . import trends as trends_mod
from . import weekly as weekly_mod
from .terms import glossary
from . import interests as interests_mod
from . import runs as runs_mod
from . import enrich as enrich_mod
from .enrich import TEXT_FIELDS, attach, enrich_new, load_cached, validate
from .normalize import article_id, normalize, parse_date
from .providers import feeds, snapshot
from .score import daily_top, score_article

SCHEMA_VERSION = 1
DEFAULT_REPO = "tomasr91/data-ai-radar"  # op GitHub Actions komt dit uit GITHUB_REPOSITORY
PROVIDERS = {"feeds": feeds.collect, "snapshot": snapshot.collect}
ARCHIVE_DAYS = 60      # hoe lang een artikel in de feed kan blijven nadat het uit een bronfeed is verdwenen
QUEUE_MAX = 15         # max. aantal artikelen op de werklijst voor Claude
QUEUE_MIN_SCORE = 40   # voorlopige score die een onverwerkt artikel minstens moet hebben


def update_archive(items, now):
    """Bewaart elk opgehaald artikel (per bron + URL) zodat het niet verdwijnt zodra een
    bronfeed het niet meer toont. Alleen toevoegen; ouder dan ARCHIVE_DAYS valt eruit."""
    path = cfg.DATA / "archive.json"
    archive = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"items": {}}
    for it in items:
        try:
            key = f"{it['source_id']}:{article_id(it['url'])}"
        except (KeyError, AttributeError):
            continue
        archive["items"].setdefault(key, it)  # eerste versie (en eerste ophaaldatum) blijft staan
    cutoff = now - timedelta(days=ARCHIVE_DAYS)
    def keep(it):
        when = parse_date(it.get("published_raw")) or it.get("fetched_at")
        return when is None or datetime.fromisoformat(when.replace("Z", "+00:00")) >= cutoff
    archive["items"] = {k: v for k, v in archive["items"].items() if keep(v)}
    archive["updated_at"] = _iso(now)
    path.write_text(json.dumps(archive, ensure_ascii=False, indent=1), encoding="utf-8")
    return list(archive["items"].values())


def skipped_ids():
    """Artikelen die Claude niet kon verwerken (bijv. pagina onleesbaar) komen niet terug op de werklijst."""
    d = enrich_mod.CACHE / "skipped"
    return {p.stem for p in d.glob("*.json")} if d.exists() else set()


def _iso(dt):
    return dt.isoformat().replace("+00:00", "Z")


def reading_minutes(article):
    words = sum(len((article.get(f) or "").split()) for f in TEXT_FIELDS)
    words += sum(len(x.split()) for x in article.get("story", []) + article.get("key_facts", []))
    words += sum(len(x.split()) for x in article.get("limitations", []))
    return max(1, math.ceil(words / 200)) if words else None


def date_clusters(articles, window_hours=3, min_items=5):
    """Signaleert bronnen waar veel items binnen korte tijd 'gepubliceerd' zijn:
    vaak een herpublicatie of migratie, waardoor de datum misleidend kan zijn."""
    flags = []
    by_src = defaultdict(list)
    for a in articles:
        if a.get("published_at"):
            by_src[a["source_id"]].append(datetime.fromisoformat(a["published_at"].replace("Z", "+00:00")))
    for src, dates in by_src.items():
        dates.sort()
        for i in range(len(dates)):
            j = i
            while j + 1 < len(dates) and dates[j + 1] - dates[i] <= timedelta(hours=window_hours):
                j += 1
            if j - i + 1 >= min_items:
                flags.append({"source_id": src, "items": j - i + 1, "from": _iso(dates[i]), "to": _iso(dates[j]),
                              "message": f"{j - i + 1} items binnen {window_hours} uur gedateerd; mogelijk een herpublicatie, controleer de datum bij de bron."})
                break
    return flags


AREA_WINDOW_DAYS = 14


def area_of(article: dict, conf) -> str:
    """Gebied van een artikel: dat van het eerste onderwerp in Claudes volgorde."""
    main = (article.get("main_topics") or article.get("topics") or [None])[0]
    for a in conf.interests.get("interest_areas", []):
        if main in a.get("topics", []):
            return a["id"]
    return "overig"


def area_minimum(arts: list, shown: list, conf, now) -> list:
    extra = []
    have = Counter(area_of(a, conf) for a in shown)
    cutoff = now - timedelta(days=AREA_WINDOW_DAYS)

    def recent(a):
        iso = a.get("processed_at") or a.get("published_at") or a.get("fetched_at")
        try:
            return datetime.fromisoformat(str(iso).replace("Z", "+00:00")) >= cutoff
        except ValueError:
            return False
    for area in conf.interests.get("interest_areas", []):
        need = (area.get("min_articles") or 0) - have[area["id"]]
        if need <= 0:
            continue
        pool = sorted([a for a in arts if a not in shown and a not in extra and a["processing_status"] == "enriched"
                       and a["decision"] in ("below_threshold", "source_cap") and area_of(a, conf) == area["id"] and recent(a)],
                      key=lambda a: -a["relevance_score"])
        for a in pool[:need]:
            a["decision"] = "area_minimum"
            extra.append(a)
    return extra


def build(provider_name: str, out_path, max_enrich: int = 15, now=None, conf=None, provider_fn=None):
    now = now or datetime.now(timezone.utc)
    conf = conf or cfg.load()
    result = (provider_fn or PROVIDERS[provider_name])(conf)

    # Laag 1: ruw bewaren
    raw_dir = cfg.DATA / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)
    stamp = now.strftime("%Y%m%dT%H%M%SZ")
    (raw_dir / f"{stamp}-{provider_name}.json").write_text(json.dumps(
        {"provider": provider_name, "mode": result.mode, "items": result.items,
         "source_results": result.source_results}, ensure_ascii=False, indent=1), encoding="utf-8")

    # Niets opgehaald? Vorige feed behouden en als verouderd markeren.
    if result.mode == "failed" and out_path.exists():
        prev = json.loads(out_path.read_text(encoding="utf-8"))
        prev["mode"], prev["mode_note"] = "stale", "Ophalen mislukt; dit is de vorige feed. " + result.note
        prev["sources"] = _source_view(conf, result.source_results)
        prev["generated_at"] = _iso(now)
        prev["deepdives"], _ = deepdives_mod.load_all(set(conf.topics))
        prev["deepdive_options"], _ = deepdives_mod.load_options(set(conf.topics))
        out_path.write_text(json.dumps(prev, ensure_ascii=False, indent=1), encoding="utf-8")
        return prev

    # Laag 2: normaliseren, verrijking uit cache, ontdubbelen
    items = update_archive(result.items, now) if provider_name == "feeds" else result.items
    # Alleen artikelen van bronnen die (nog) in sources.yml staan en aan staan
    active = {s["id"] for s in conf.source_list if s.get("enabled")}
    items = [i for i in items if i.get("source_id") in active]
    # Weekoverzicht voor bronnen met veel kleine releases (zie digest.py)
    digests = weekly_digests(items, conf, now)
    digest_ids = {article_id(d["url"]) for d in digests}
    items = items + digests
    invalid_cache = []
    arts = []
    for raw in items:
        try:
            a = normalize(raw)
        except (KeyError, AttributeError):
            continue
        a["processing_status"] = "raw"
        cached = load_cached(a["id"])
        if cached:
            problems = validate(cached, set(conf.topics))
            if problems:  # een fout uitlegbestand komt niet in de app
                invalid_cache.append({"id": a["id"], "title": a["title"], "problems": problems})
            else:
                attach(a, cached)
        arts.append(a)
    sources_by_id = {s["id"]: s for s in conf.source_list}
    arts, merged = dedupe(arts, sources_by_id)

    # Laag 3: scoren, nieuwe artikelen verrijken (best scorende eerst), opnieuw scoren.
    # Jouw duimpjes (data/feedback.json) wegen mee; een duim omlaag haalt het artikel weg.
    fb_data = feedback_mod.load()
    fb_prefs = feedback_mod.preferences(fb_data, now)
    fb_votes = fb_data["votes"]
    for a in arts:
        score_article(a, conf, now, fb_prefs, fb_votes)
    # Relatief maken: het gemiddelde artikel dat in aanmerking komt is het nulpunt.
    pool = [a for a in arts if a["decision"] not in ("excluded", "no_topic") and a["processing_status"] == "enriched"]
    fb_prefs["offset"] = feedback_mod.mean_factor(pool, fb_prefs)
    for a in arts:
        score_article(a, conf, now, fb_prefs, fb_votes)
    candidates = sorted([a for a in arts if a["decision"] not in ("excluded", "no_topic")],
                        key=lambda a: -a["relevance_score"])
    enrich_report = enrich_new(candidates, set(conf.topics), max_enrich)
    for a in arts:
        score_article(a, conf, now, fb_prefs, fb_votes)

    # Werklijst voor Claude: beste onverwerkte artikelen die nog niet zijn overgeslagen
    skip = skipped_ids()
    # Volgorde: eerst hoe goed het onderwerp past, dan de totaalscore. Zo krijgt Claude ook oudere
    # artikelen over een kernonderwerp te zien; Claude beoordeelt daarna of ze de feed in mogen.
    # Weekoverzichten (zie digest.py) gaan voor: het zijn er hooguit een paar per week.
    # Gebieden onder hun ondergrens krijgen voorrang op de werklijst (na de weekoverzichten).
    have = Counter(area_of(a, conf) for a in arts if a["decision"] in ("included", "included_exceptional") and a["processing_status"] == "enriched")
    under = {x["id"] for x in conf.interests.get("interest_areas", []) if have[x["id"]] < (x.get("min_articles") or 0)}
    # Voorrang voor een gebied onder de ondergrens alleen bij een score boven de drempel: anders vult
    # marketing van een bron in dat gebied (bijv. "nu ook op Google Cloud") de werklijst.
    bar = conf.scoring.get("min_relevance_score", 0.6) * 100
    queue = [a for a in sorted(arts, key=lambda a: (a["id"] not in digest_ids, not (area_of(a, conf) in under and a["relevance_score"] >= bar),
                                                    -a["score_parts"]["topic"], -a["relevance_score"]))
             if a["processing_status"] != "enriched" and a["id"] not in skip
             and a["decision"] not in ("excluded", "no_topic") and a["relevance_score"] >= QUEUE_MIN_SCORE][:QUEUE_MAX]
    (cfg.DATA / "to_enrich.json").write_text(json.dumps({
        "generated_at": _iso(now),
        "instructions": "Zie taken/UITLEGGEN.md. Schrijf per artikel data/enrichment/<id>.json.",
        "items": [{"id": a["id"], "title": a["title"], "url": a["url"], "source_id": a["source_id"],
                   "source_name": sources_by_id.get(a["source_id"], {}).get("name", a["source_id"]),
                   "published_at": a.get("published_at"), "excerpt": a.get("excerpt", ""),
                   "preliminary_score": a["relevance_score"], "preliminary_topics": a["topics"]} for a in queue],
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    group_of = {t["id"]: t.get("feed_group", "overig") for t in conf.interests["topics"]}
    for a in arts:
        a["groups"] = list(dict.fromkeys(group_of.get(t, "overig") for t in a["topics"])) or ["overig"]
        a["reading_minutes"] = reading_minutes(a) if a["processing_status"] == "enriched" else None
        a.pop("canonical_url", None)

    # Alleen artikelen die Claude heeft uitgelegd komen in de app; de rest wacht op de werklijst.
    shown = sorted([a for a in arts if a["decision"] in ("included", "included_exceptional")
                    and a["processing_status"] == "enriched"],
                   key=lambda a: (-a["relevance_score"], a.get("published_at") or ""))
    # Maximum per bron: zo kan één bron de feed niet vullen. De hoogste scores blijven staan.
    # Plus een maximum per bron per publicatiedag, zodat een golf posts rond een evenement de feed niet overneemt.
    cap = conf.scoring.get("max_articles_per_source")
    day_cap = conf.scoring.get("max_articles_per_source_per_day")
    if cap or day_cap:
        per_src, per_day = Counter(), Counter()
        for a in shown:
            if fb_votes.get(a["id"], {}).get("v") == 1:
                continue   # wat je 👍 gaf blijft altijd staan en telt niet mee voor het maximum
            day = (a.get("published_at") or "")[:10]
            if day_cap and per_day[(a["source_id"], day)] >= day_cap:
                a["decision"] = "source_cap"
                continue
            per_src[a["source_id"]] += 1
            per_day[(a["source_id"], day)] += 1
            if cap and per_src[a["source_id"]] > cap:
                a["decision"] = "source_cap"
        shown = [a for a in shown if a["decision"] != "source_cap"]
    # Ondergrens per gebied (interest_areas.min_articles): aanvullen met de best scorende uitgelegde
    # artikelen van de laatste 14 dagen uit dat gebied, ook net onder de drempel of boven het maximum per bron.
    shown += area_minimum(arts, shown, conf, now)
    hidden = [a for a in arts if a not in shown]

    # Moment waarop een artikel in de app kwam: uitgelegd, anders opgehaald (zoals "Nieuw" in de app).
    fetched = [a.get("processed_at") or a["fetched_at"] for a in shown if a.get("processed_at") or a.get("fetched_at")]
    deepdives, invalid_deepdives = deepdives_mod.load_all(set(conf.topics))
    dd_options, invalid_options = deepdives_mod.load_options(set(conf.topics))
    trends, invalid_trends = trends_mod.load(set(conf.topics), shown)
    weekly, invalid_weekly = weekly_mod.load(shown)
    int_suggestions, invalid_suggestions = interests_mod.load_suggestions(set(conf.topics))
    feed = {
        "schema_version": SCHEMA_VERSION,
        "generated_at": _iso(now),
        "mode": result.mode,
        "mode_note": result.note,
        "last_article_added_at": max(fetched) if fetched else None,
        "last_successful_update": result.extra.get("captured_at") if result.mode == "snapshot" else _iso(now),
        "groups": conf.feed_groups,
        "topics": {t["id"]: {"name": t["name"], "priority": t["priority"], "group": t.get("feed_group", "overig"),
                             **({"learning": True} if t.get("learning") else {})}
                   for t in conf.interests["topics"]},
        "sources": _source_view(conf, result.source_results),
        "daily_top": daily_top(shown, size=5, per_group=min(2, conf.scoring.get("max_items_per_topic_per_feed", 3))),
        "articles": [_public(a) for a in shown],
        "deepdives": deepdives,
        "deepdive_options": dd_options,
        "trends": trends,
        "weekly": weekly,
        "glossary": glossary(shown, deepdives),
        "interests": interests_mod.view(conf),
        "interest_suggestions": int_suggestions,
        "interest_log": interests_mod.load_log(),
        "runs": runs_mod.latest(),
        "feedback": {**fb_prefs, "weight": feedback_mod.WEIGHT, "updated_at": fb_data.get("updated_at")},
        "repo": os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO),
        "quality_report": {
            "fetched_items": len(result.items),
            "unique_after_dedupe": len(arts),
            "merged_duplicates": merged,
            "shown": len(shown),
            "decisions": dict(Counter(a["decision"] for a in arts)),
            "processing": dict(Counter(a["processing_status"] for a in shown)),
            "without_date": sum(1 for a in shown if not a.get("published_at")),
            "per_group": dict(Counter(a["groups"][0] for a in shown)),
            "per_source": dict(Counter(a["source_id"] for a in shown)),
            "date_flags": date_clusters(arts),
            "enrichment": enrich_report,
            "queue_size": len(queue),
            "invalid_enrichment": invalid_cache,
            "invalid_deepdives": invalid_deepdives,
            "invalid_deepdive_options": invalid_options,
            "invalid_trends": invalid_trends,
            "invalid_weekly": invalid_weekly,
            "invalid_interest_suggestions": invalid_suggestions,
            "threshold": round(conf.scoring.get("min_relevance_score", 0.5) * 100),
            "max_per_source": conf.scoring.get("max_articles_per_source"),
            "not_shown": [{"title": a["title"], "source_id": a["source_id"], "url": a["url"],
                           "relevance_score": a["relevance_score"], "decision": a["decision"],
                           "excluded_by": a.get("excluded_by", [])}
                          for a in sorted(hidden, key=lambda a: -a["relevance_score"])][:60],
            "topics_without_source": [t["id"] for t in conf.topics.values()
                                      if not any(t["id"] in s.get("topics", []) for s in conf.source_list if s.get("enabled"))],
        },
    }
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(json.dumps(feed, ensure_ascii=False, indent=1), encoding="utf-8")
    return feed


PUBLIC_FIELDS = ["id", "title", "url", "source_id", "published_at", "date_note", "fetched_at", "summary",
                 "what_is_new", "simple_explanation", "practical_example", "personal_relevance",
                 "practical_application", "experiment", "limitations", "availability_status",
                 "official_docs", "topics", "groups", "relevance_score", "score_parts", "decision",
                 "processing_status", "processed_by", "processed_at", "reading_minutes", "also_reported_by", "excerpt",
                 "format_version", "headline", "story", "key_facts", "article_type", "author",
                 "showcase", "terms", "learning"]


def _public(a):
    out = {k: a.get(k) for k in PUBLIC_FIELDS if a.get(k) not in (None, "", [])}
    if a["processing_status"] == "enriched":
        out.pop("excerpt", None)  # de verrijking vervangt de feedtekst
    return out


def _source_view(conf, results):
    by_id = {r["source_id"]: r for r in results}
    view = []
    for s in conf.source_list:
        if not s.get("enabled"):
            continue
        r = by_id.get(s["id"], {"status": "not_fetched", "items": 0, "message": "Niet opgehaald."})
        view.append({"id": s["id"], "name": s["name"], "url": s["url"], "type": s["type"],
                     "trust_level": s["trust_level"], "priority": s.get("priority"),
                     "fetch_method": s["fetch_method"], **{k: r.get(k) for k in ("status", "items", "message", "checked_at")}})
    return view


def main(argv=None):
    p = argparse.ArgumentParser(description="Bouw data/feed.json voor de Data & AI Radar")
    p.add_argument("--provider", choices=sorted(PROVIDERS), default="feeds")
    p.add_argument("--out", default=str(cfg.DATA / "feed.json"))
    p.add_argument("--max-enrich", type=int, default=15, help="max. aantal nieuwe AI-verrijkingen per run")
    args = p.parse_args(argv)
    from pathlib import Path
    feed = build(args.provider, Path(args.out), args.max_enrich)
    q = feed.get("quality_report", {})
    print(f"modus: {feed['mode']} - {feed['mode_note']}")
    for s in feed["sources"]:
        print(f"  {s['status']:<13} {s['id']:<32} {s.get('message') or ''}")
    print(f"getoond: {q.get('shown')} | uniek: {q.get('unique_after_dedupe')} | samengevoegd: {q.get('merged_duplicates')} | beslissingen: {q.get('decisions')}")
    enr = q.get("enrichment", {})
    if enr and not enr.get("api_key_present"):
        print(f"  geen ANTHROPIC_API_KEY: {enr.get('skipped_no_key')} artikelen blijven onverwerkt")
    return 0


if __name__ == "__main__":
    sys.exit(main())

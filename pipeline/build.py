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
import re
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
from . import learn as learn_mod
from . import trends as trends_mod
from . import weekly as weekly_mod
from .terms import glossary
from . import interests as interests_mod
from . import runs as runs_mod
from . import enrich as enrich_mod
from .enrich import TEXT_FIELDS, attach, enrich_new, load_cached, validate
from .normalize import article_id, normalize, parse_date
from .providers import archive as archive_provider, feeds, snapshot
from .score import daily_top, score_article

SCHEMA_VERSION = 1
DEFAULT_REPO = "tomasr91/data-ai-radar"  # op GitHub Actions komt dit uit GITHUB_REPOSITORY
PROVIDERS = {"feeds": feeds.collect, "snapshot": snapshot.collect, "archive": archive_provider.collect}
FETCH_EVERY_HOURS = 12   # bij --provider auto: alleen ophalen als het langer geleden is (of als de nachttaak erom vraagt)
ARCHIVE_DAYS = 60      # hoe lang een artikel in de feed kan blijven nadat het uit een bronfeed is verdwenen
QUEUE_MAX = 40         # werklijst voor Claude: hooguit 10 per nacht uitleggen (vol of kort); de rest vult aan wat is overgeslagen (T, 5-11-2026)
FRESH_DAYS, FRESH_BONUS = 2, 10   # liefst actueel: artikelen van de laatste 2 dagen krijgen 10 punten voorrang op de werklijst
EXPLAIN_REQUESTS = cfg.DATA / "explain_requests.json"   # korte uitleg die T volledig wil (knop "Volledig uitleggen")
# Bronnen met queue_low: true in sources.yml (bijv. Fabric) komen achteraan op de werklijst, behalve
# als het om iets algemeen beschikbaars gaat of om de koppeling met Power BI of Databricks.
QUEUE_LOW_EXCEPT = re.compile(r"generally available|\bGA\b|now available|Power BI|Databricks", re.I)
QUEUE_MIN_SCORE = 35   # voorlopige score die een onverwerkt artikel minstens moet hebben (was 40; korte uitleg vanaf 45)
QUEUE_MAX_AGE_DAYS = 14   # alleen recente artikelen op de werklijst: een nieuwe bron levert geen weken achterstand op (T, 4-11-2026)
AREA_MAX_FACTOR = 1.5     # een gebied vult hooguit 1,5 x zijn richtwaarde van de feed (T, 4-11-2026)


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


RETRY_AFTER_DAYS = 7
RETRIED = cfg.DATA / "retried.json"


def skipped_ids(now=None):
    """Artikelen die Claude niet kon verwerken komen niet terug op de werklijst.
    Uitzondering: was de pagina niet te lezen, dan na een week nog één keer proberen. retried.json houdt bij
    wanneer een artikel die kans kreeg; schrijft Claude daarna opnieuw een overslag, dan blijft het weg."""
    d = enrich_mod.CACHE / "skipped"
    if not d.exists():
        return set()
    now = now or datetime.now(timezone.utc)
    try:
        retried = json.loads(RETRIED.read_text(encoding="utf-8"))
        retried = retried if isinstance(retried, dict) else {}
    except (OSError, ValueError):
        retried = {}
    skip, changed = set(), False
    for p in d.glob("*.json"):
        try:
            x = json.loads(p.read_text(encoding="utf-8"))
            reason = (x.get("reason") or "").lower()
            at = datetime.fromisoformat(str(x.get("checked_at")).replace("Z", "+00:00"))
        except (OSError, ValueError, TypeError):
            skip.add(p.stem); continue
        if p.stem in retried:
            if at > datetime.fromisoformat(retried[p.stem].replace("Z", "+00:00")):
                skip.add(p.stem)       # tweede poging ook mislukt: blijft weg
            continue                   # kans loopt nog
        unreadable = "niet te lezen" in reason or "geweigerd" in reason or "onleesbaar" in reason
        if unreadable and now - at >= timedelta(days=RETRY_AFTER_DAYS):
            retried[p.stem] = _iso(now); changed = True
        else:
            skip.add(p.stem)
    if changed:
        RETRIED.write_text(json.dumps(retried, indent=1, sort_keys=True), encoding="utf-8")
    return skip


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


def _age_days(a, now) -> float:
    try:
        return (now - datetime.fromisoformat(str(a.get("published_at")).replace("Z", "+00:00"))).days
    except ValueError:
        return 0.0   # geen datum: niet tegenhouden


def area_cap(shown: list, conf, votes: dict) -> list:
    """Hooguit AREA_MAX_FACTOR x de richtwaarde per gebied. De laagst scorende artikelen boven dat
    maximum vallen af (decision area_cap); wat je 👍 gaf blijft altijd staan."""
    n = len(shown)
    keep, count = [], Counter()
    share = {x["id"]: x.get("target_share") for x in conf.interests.get("interest_areas", [])}
    for a in sorted(shown, key=lambda a: -a["relevance_score"]):
        ar = area_of(a, conf)
        mx = math.ceil(AREA_MAX_FACTOR * share[ar] * n) if share.get(ar) else None
        if mx is not None and count[ar] >= mx and votes.get(a["id"], {}).get("v") != 1:
            a["decision"] = "area_cap"
            continue
        count[ar] += 1
        keep.append(a)
    return keep


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


FOLLOW_DAYS = 7


def follow_minimum(arts: list, shown: list, conf, now) -> list:
    """'Altijd volgen' (follow: true in interests.yml): verscheen er de afgelopen week iets over zo'n
    onderwerp, dan staat er minstens één uitgelegd artikel van in de feed, ook onder de drempel."""
    cutoff = now - timedelta(days=FOLLOW_DAYS)

    def recent(a):
        try:
            return datetime.fromisoformat(str(a.get("published_at")).replace("Z", "+00:00")) >= cutoff
        except ValueError:
            return False
    extra = []
    for t in conf.interests.get("topics", []):
        if not t.get("follow") or not t.get("enabled", True):
            continue
        if any(t["id"] in a["topics"][:2] and recent(a) for a in shown + extra):
            continue
        pool = sorted([a for a in arts if a not in shown and a not in extra and a["processing_status"] == "enriched"
                       and a["decision"] in ("below_threshold", "source_cap") and t["id"] in a["topics"][:2] and recent(a)],
                      key=lambda a: -a["relevance_score"])
        if pool:
            pool[0]["decision"] = "follow_minimum"
            extra.append(pool[0])
    return extra


TASTE = cfg.DATA / "taste.json"
TO_TAG = cfg.DATA / "to_tag.json"


def write_taste(fb_data: dict, by_id: dict, now, arts=()) -> None:
    """data/taste.json: je recente duimpjes en gelezen artikelen, voor Claudes oordeel 'past bij jou' (fit),
    met de score op het moment van de duim en de labels die al in gebruik zijn."""
    def row(aid, x, extra):
        a = by_id.get(aid, {})
        return {"id": aid, "title": x.get("title") or a.get("headline") or a.get("title", ""), "source_id": x.get("source_id", ""),
                "topics": x.get("topics", [])[:2], "soort": x.get("soort") or a.get("soort"),
                "labels": x.get("labels") or a.get("labels") or [], "score": x.get("s"), **extra}
    labels = Counter(lab for a in arts if a.get("processing_status") == "enriched" for lab in a.get("labels", []) or [])
    votes = sorted(fb_data["votes"].items(), key=lambda kv: kv[1].get("at", ""), reverse=True)[:20]
    reads = sorted([kv for kv in fb_data["reads"].items() if kv[0] not in fb_data["votes"]],
                   key=lambda kv: kv[1].get("at", ""), reverse=True)[:10]
    TASTE.write_text(json.dumps({
        "generated_at": _iso(now),
        "note": "Zie taken/UITLEGGEN.md, 'Past bij jou'. v: 1 = duim omhoog, -1 = duim omlaag; r = reden.",
        "votes": [row(k, x, {"v": x.get("v"), "r": x.get("r")}) for k, x in votes],
        "reads": [row(k, x, {}) for k, x in reads],
        "labels_in_use": [lab for lab, _ in labels.most_common(120)],
    }, ensure_ascii=False, indent=1), encoding="utf-8")


def write_to_tag(shown: list) -> None:
    """data/to_tag.json: uitgelegde artikelen in de feed zonder soort of fit; Claude vult ze 's nachts aan."""
    def missing(a):
        return [k for k in ("soort", "fit", "labels") if not a.get(k)] + ([] if a.get("project_checked") else ["project_ref"])
    todo = [{"id": a["id"], "title": a.get("headline") or a["title"], "missing": missing(a)}
            for a in shown if a["processing_status"] == "enriched" and missing(a)]
    TO_TAG.write_text(json.dumps({"items": todo[:20]}, ensure_ascii=False, indent=1), encoding="utf-8")


EFFECT_DAYS = 7
INCLUDED = ("included", "included_exceptional", "included_low")


def feedback_effect(arts: list, shown: list, conf, now) -> dict:
    """Wat je feedback deze week veranderde: artikelen die er alleen door je feedback in staan (erbij)
    en uitgelegde artikelen die zonder feedback wel in de feed hadden gestaan (eruit)."""
    shown_ids = {a["id"] for a in shown}
    cutoff = now - timedelta(days=EFFECT_DAYS)
    lifted, dropped = [], []
    for a in arts:
        if a["processing_status"] != "enriched" or not ({"feedback", "fit"} & set(a.get("score_parts", {}))):
            continue
        try:
            at = datetime.fromisoformat(str(a.get("processed_at") or a.get("published_at")).replace("Z", "+00:00"))
        except ValueError:
            continue
        if at < cutoff:
            continue
        base = score_article({**a, "score_parts": {}, "fit": None}, conf, now)   # zelfde artikel, zonder feedback en fit
        delta = a["relevance_score"] - base["relevance_score"]
        row = {"id": a["id"], "title": a.get("headline") or a["title"], "source_id": a["source_id"], "delta": delta}
        if a["id"] in shown_ids and a["decision"] in INCLUDED and base["decision"] not in INCLUDED:
            lifted.append(row)
        elif a["id"] not in shown_ids and a["decision"] == "below_threshold" and base["decision"] in INCLUDED:
            dropped.append({**row, "url": a["url"]})
    return {"days": EFFECT_DAYS, "lifted": sorted(lifted, key=lambda r: -r["delta"]),
            "dropped": sorted(dropped, key=lambda r: r["delta"])}


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
    by_id = {a["id"]: a for a in arts}
    for aid, x in list(fb_data["votes"].items()) + list(fb_data["reads"].items()):   # aanvullen (niet opgeslagen)
        a = by_id.get(aid)
        if not a:
            continue
        for k in ("soort", "labels"):
            if not x.get(k) and a.get(k):
                x[k] = a[k]
        if not x.get("text"):
            x["text"] = learn_mod.text_of(a)[:800]
        if not isinstance(x.get("s"), (int, float)):   # duim van vóór 5-11-2026: score zonder feedback als benadering
            x["s"] = score_article(dict(a), conf, now)["relevance_score"]
    fb_prefs = feedback_mod.preferences(fb_data, now)
    fb_prefs["model"] = learn_mod.model(fb_data, now)   # duim = correctie op de score (pipeline/learn.py)
    write_taste(fb_data, by_id, now, arts)
    fb_votes = fb_data["votes"]
    for a in arts:
        score_article(a, conf, now, fb_prefs, fb_votes)
    # Niet meer relatief (T, 1-11-2026): minder vaak 👍 mag een onderwerp niet omlaag duwen. offset blijft 0.
    fb_prefs["offset"] = 0.0
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
    have = Counter(area_of(a, conf) for a in arts if a["decision"] in INCLUDED and a["processing_status"] == "enriched")
    under = {x["id"] for x in conf.interests.get("interest_areas", []) if have[x["id"]] < (x.get("min_articles") or 0)}
    # Voorrang voor een gebied onder de ondergrens alleen bij een score boven de drempel: anders vult
    # marketing van een bron in dat gebied (bijv. "nu ook op Google Cloud") de werklijst.
    bar = conf.scoring.get("min_relevance_score", 0.6) * 100
    try:
        wanted = [x for x in json.loads(EXPLAIN_REQUESTS.read_text(encoding="utf-8")).get("ids", []) if isinstance(x, str)]
    except (OSError, ValueError):
        wanted = []
    full = [a for a in arts if a["id"] in wanted and a.get("diepte") == "kort"]   # nog kort: volledig uitleggen, vooraan
    if len(full) != len(wanted):   # al volledig uitgelegd of niet meer in de feed: van de lijst
        EXPLAIN_REQUESTS.write_text(json.dumps({"ids": [a["id"] for a in full]}, indent=1), encoding="utf-8")

    def low(a):
        return bool((sources_by_id.get(a["source_id"]) or {}).get("queue_low")) and not QUEUE_LOW_EXCEPT.search(a["title"])   # alleen de titel: in de tekst staat bijna altijd 'Power BI'
    # Volgorde (T, 5-11-2026): per nacht hooguit 10, liefst actueel; een ouder artikel met een hoge score mag voor.
    queue = [a for a in sorted(arts, key=lambda a: (a["id"] not in digest_ids, low(a), not (area_of(a, conf) in under and a["relevance_score"] >= bar),
                                                    -(a["relevance_score"] + (FRESH_BONUS if _age_days(a, now) <= FRESH_DAYS else 0))))
             if a["processing_status"] != "enriched" and a["id"] not in skip and (a["id"] in digest_ids or _age_days(a, now) <= QUEUE_MAX_AGE_DAYS)
             and a["decision"] not in ("excluded", "no_topic") and a["relevance_score"] >= QUEUE_MIN_SCORE][:QUEUE_MAX - len(full)]
    queue = full + queue
    (cfg.DATA / "to_enrich.json").write_text(json.dumps({
        "generated_at": _iso(now),
        "instructions": "Zie taken/UITLEGGEN.md. Schrijf per artikel data/enrichment/<id>.json.",
        "items": [{"id": a["id"], "title": a["title"], "url": a["url"], "source_id": a["source_id"],
                   "source_name": sources_by_id.get(a["source_id"], {}).get("name", a["source_id"]),
                   "published_at": a.get("published_at"), "excerpt": a.get("excerpt", ""),
                   "preliminary_score": a["relevance_score"], "preliminary_topics": a["topics"],
                   **({"volledig": True} if a in full else {})} for a in queue],
    }, ensure_ascii=False, indent=1), encoding="utf-8")

    group_of = {t["id"]: t.get("feed_group", "overig") for t in conf.interests["topics"]}
    for a in arts:
        a["groups"] = list(dict.fromkeys(group_of.get(t, "overig") for t in a["topics"])) or ["overig"]
        a["reading_minutes"] = reading_minutes(a) if a["processing_status"] == "enriched" else None
        a.pop("canonical_url", None)

    # Alleen artikelen die Claude heeft uitgelegd komen in de app; de rest wacht op de werklijst.
    shown = sorted([a for a in arts if a["decision"] in INCLUDED
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
    shown = area_cap(shown, conf, fb_votes)
    shown += area_minimum(arts, shown, conf, now)
    shown += follow_minimum(arts, shown, conf, now)
    write_to_tag(shown)
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
        "last_successful_update": (result.extra.get("captured_at") or _iso(now)) if provider_name != "feeds" else _iso(now),
        "groups": conf.feed_groups,
        "topics": {t["id"]: {"name": t["name"], "priority": t["priority"], "group": t.get("feed_group", "overig"),
                             **({"learning": True} if t.get("learning") else {}),
                             **({"follow": True} if t.get("follow") else {})}
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
        "rode_draad": {"name": enrich_mod.rode_draad().get("name"),
                       "phases": [{"fase": p["fase"], "name": p["name"]} for p in enrich_mod.rode_draad().get("phases", [])]},
        "interest_suggestions": int_suggestions,
        "interest_log": interests_mod.load_log(),
        "runs": runs_mod.latest(),
        "feedback": {**{k: v for k, v in fb_prefs.items() if k != "model"}, "weight": 1.0, "updated_at": fb_data.get("updated_at"),
                     **learn_mod.summary(fb_data, fb_prefs["model"], now),
                     "effect": feedback_effect(arts, shown, conf, now)},
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
                 "showcase", "terms", "learning", "soort", "fit", "labels", "fb_why", "diepte", "project_ref"]


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


def should_fetch(conf, now=None, feed_path=None, request_path=None) -> bool:
    """Voor --provider auto: ophalen als er nog geen feed is, als het langer dan FETCH_EVERY_HOURS
    geleden is, als de nachttaak er vandaag om vroeg (data/run-request) of als er een bron bij kwam."""
    now = now or datetime.now(timezone.utc)
    feed_path, request_path = feed_path or cfg.DATA / "feed.json", request_path or cfg.DATA / "run-request"
    try:
        prev = json.loads(feed_path.read_text(encoding="utf-8"))
        last = datetime.fromisoformat(prev["last_successful_update"].replace("Z", "+00:00"))
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        return True
    if now - last > timedelta(hours=FETCH_EVERY_HOURS):
        return True
    try:
        req = request_path.read_text(encoding="utf-8").strip().splitlines()[-1].strip()
        if req > last.strftime("%Y-%m-%d"):
            return True
    except (OSError, IndexError):
        pass
    enabled = {s["id"] for s in conf.source_list if s.get("enabled")}
    return not enabled <= {s.get("id") for s in prev.get("sources", [])}


def main(argv=None):
    p = argparse.ArgumentParser(description="Bouw data/feed.json voor de Data & AI Radar")
    p.add_argument("--provider", choices=sorted(PROVIDERS) + ["auto"], default="feeds")
    p.add_argument("--out", default=str(cfg.DATA / "feed.json"))
    p.add_argument("--max-enrich", type=int, default=15, help="max. aantal nieuwe AI-verrijkingen per run")
    args = p.parse_args(argv)
    from pathlib import Path
    provider = args.provider
    if provider == "auto":
        provider = "feeds" if should_fetch(cfg.load()) else "archive"
        print(f"auto: {'ophalen' if provider == 'feeds' else 'opnieuw samenstellen zonder ophalen'}")
    feed = build(provider, Path(args.out), args.max_enrich)
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

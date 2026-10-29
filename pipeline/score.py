"""Relevantiescore volgens context/interests.yml.

score (0-100) = 100 x ( 0.55 x onderwerp
                       + 0.20 x inhoudelijke kwaliteit
                       + 0.15 x actualiteit
                       + 0.10 x bron )

onderwerp    beste onderwerp (prioriteit / 5) x zekerheid van de match, plus een
             kleine bonus voor gerelateerde onderwerpen die ook geraakt worden.
             Zekerheid: verrijkt (AI heeft het artikel gelezen) 1.0; alleen
             trefwoorden: 1 trefwoord 0.5, 2 trefwoorden 0.8, 3 of meer 1.0.
             Zo telt een los genoemde productnaam ('Databricks') niet als
             volwaardige match.
actualiteit  halveert elke 14 dagen; zonder publicatiedatum 0.3
bron         bronprioriteit / 5 x betrouwbaarheid
kwaliteit    gemiddelde van diepgang, toepasbaarheid en nieuwheid uit de
             verrijking; onverwerkte artikelen krijgen 0.35

Regels uit interests.yml:
- min_relevance_score: onder de drempel geen plek in de feed, ook niet bij prioriteit 5
- exceptional_override: bij prioriteit 1-2 mag een uitzonderlijk artikel toch door
- excluded_topics: altijd eruit, ook via de uitzonderingsregel (trefwoorden of title_patterns)
"""
import math
import re
from datetime import datetime, timezone

TRUST = {"high": 1.0, "medium": 0.85, "low": 0.6}
HALF_LIFE_DAYS = 14
WEIGHTS = {"topic": 0.55, "quality": 0.20, "recency": 0.15, "source": 0.10}
RAW_QUALITY = 0.35


def match_certainty(n_hits: int) -> float:
    return 0.5 if n_hits <= 1 else 0.8 if n_hits == 2 else 1.0


def _norm(text: str) -> str:
    """'dbt_context_engineering', 'dbt-context-engineering' en 'dbt context engineering'
    worden hetzelfde, zodat schrijfwijzen elkaar niet mislopen."""
    return re.sub(r"\s+", " ", re.sub(r"[_\-/]+", " ", text.lower())).strip()


def _pattern(keyword: str):
    return re.compile(r"(?<!\w)" + re.escape(_norm(keyword)) + r"(?!\w)")


def match_keywords(text: str, entries: list) -> list:
    return list(keyword_hits(text, entries))


def excluded_by(title: str, text: str, entries: list) -> list:
    """Uitsluiting op trefwoorden (hele tekst) of op titelpatronen (reguliere expressies,
    hoofdletterongevoelig). Titelpatronen vangen vormen als 'v1.12.6' of
    'X connector is available in Beta' die met losse trefwoorden niet te pakken zijn."""
    hits = set(match_keywords(text, entries))
    for entry in entries:
        if any(re.search(p, title or "", re.I) for p in entry.get("title_patterns", [])):
            hits.add(entry["id"])
    return [e["id"] for e in entries if e["id"] in hits]


def keyword_hits(text: str, entries: list) -> dict:
    """{onderwerp-id: set van geraakte trefwoorden}"""
    text = _norm(text)
    hits = {}
    for entry in entries:
        found = {k.lower() for k in entry.get("keywords", []) if _pattern(k).search(text)}
        if found:
            hits[entry["id"]] = found
    return hits


def recency(published_at, now) -> float:
    if not published_at:
        return 0.3
    dt = datetime.fromisoformat(published_at.replace("Z", "+00:00"))
    age = max(0.0, (now - dt).total_seconds() / 86400)
    return math.pow(0.5, age / HALF_LIFE_DAYS)


def topic_score(topic_ids: list, topics: dict, related_weight: float, certainty: float = 1.0) -> float:
    direct = [t for t in topic_ids if t in topics]
    if not direct:
        return 0.0
    best = max(direct, key=lambda t: topics[t]["priority"])
    base = topics[best]["priority"] / 5 * certainty
    related = [t for t in direct if t != best and t in topics[best].get("related_topics", [])]
    return min(1.0, base + related_weight * 0.1 * len(related))


def score_article(article: dict, config, now=None, prefs=None, votes=None) -> dict:
    """prefs/votes: jouw duimpjes (zie feedback.py). Zonder feedback werkt alles als voorheen."""
    now = now or datetime.now(timezone.utc)
    topics = config.topics
    sc = config.scoring
    text = f"{article['title']} {article.get('headline', '')} {article.get('excerpt', '')} {article.get('summary', '')}"

    excluded = excluded_by(article["title"], text, config.excluded_topics)
    # Verrijkte artikelen hebben door AI gekozen onderwerpen; anders trefwoorden.
    if article.get("processing_status") == "enriched" and article.get("topics"):
        topic_ids, certainty = list(article["topics"]), 1.0
    else:
        hits = keyword_hits(text, list(topics.values()))
        topic_ids = list(hits)
        certainty = match_certainty(len(set().union(*hits.values())) if hits else 0)
    topic_ids = [t for t in topic_ids if t in topics]
    topic_ids.sort(key=lambda t: -topics[t]["priority"])

    src = config.source(article["source_id"])
    q = article.get("quality")
    parts = {
        "topic": topic_score(topic_ids, topics, sc.get("related_topic_weight", 0.5), certainty),
        "recency": recency(article.get("published_at"), now),
        "source": src.get("priority", 3) / 5 * TRUST.get(src.get("trust_level"), 0.6),
        "quality": (q["depth"] + q["practicality"] + q["novelty"]) / 3 if q else RAW_QUALITY,
    }
    total = sum(WEIGHTS[k] * v for k, v in parts.items())
    if prefs:
        from .feedback import WEIGHT as FB_WEIGHT, article_factor
        fb = article_factor({"topics": topic_ids, "source_id": article["source_id"]}, prefs)
        if fb:
            parts["feedback"] = fb
            total = min(1.0, max(0.0, total + FB_WEIGHT * fb))
    my_vote = (votes or {}).get(article.get("id"), {}).get("v")
    best_priority = topics[topic_ids[0]]["priority"] if topic_ids else 0

    override = sc.get("exceptional_override", {})
    threshold = sc.get("min_relevance_score", 0.5)
    if excluded:
        decision = "excluded"
    elif my_vote == -1:
        decision = "hidden_by_feedback"   # jij gaf een duim omlaag
    elif not topic_ids:
        decision = "no_topic"
    elif total >= threshold:
        decision = "included"
    elif (article.get("exceptional") and override.get("enabled")
          and best_priority in override.get("applies_to_priorities", [])):
        decision = "included_exceptional"
    else:
        decision = "below_threshold"

    article["topics"] = topic_ids
    article["relevance_score"] = round(total * 100)
    article["score_parts"] = {k: round(v, 2) for k, v in parts.items()}
    article["decision"] = decision
    article["excluded_by"] = excluded
    return article


def daily_top(articles: list, size: int = 5, per_group: int = 2) -> list:
    """Dagelijks overzicht: de hoogste scores, maar maximaal `per_group` per feedgroep."""
    chosen, counts = [], {}
    for a in sorted(articles, key=lambda a: -a["relevance_score"]):
        g = a["groups"][0] if a.get("groups") else "overig"
        if counts.get(g, 0) < per_group:
            chosen.append(a["id"])
            counts[g] = counts.get(g, 0) + 1
        if len(chosen) == size:
            break
    return chosen

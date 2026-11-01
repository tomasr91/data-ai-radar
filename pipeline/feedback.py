"""Jouw duimpjes (data/feedback.json) en wat de radar ervan leert.

- Per onderwerp, bron en soort artikel telt de radar je stemmen op (recente zwaarder, halveert
  elke 60 dagen). Dat geeft een voorkeur tussen -1 en +1.
- De voorkeur weegt mee in de relevantiescore, hooguit 15 punten erbij of eraf. Niet relatief
  (T, 1-11-2026, avond): 👍 en gelezen duwen omhoog; niets doen is neutraal. Alleen een 👎 met
  reden "geen interesse" of "niet mijn stack" verlaagt het onderwerp en de bron. Een 👎 zonder
  reden of om de kwaliteit (te basic, te vaag, oud nieuws) gaat over dat artikel: telt alleen
  tegen de soort artikel, en Claude ziet het in taste.json.
- Gewichten (T, 31-10-2026): 👍 telt 2 ("dit is echt interessant"), 👎 telt 1 de andere kant op,
  gelezen (tot onderaan, minstens 15 seconden open) telt 0,5: een benadering. Heb je een
  artikel ook beoordeeld, dan telt alleen je duim.
"""
import json
import math
from datetime import datetime, timezone

from .config import DATA

PATH = DATA / "feedback.json"
REASONS_DOWN = {"te_basic", "niet_mijn_stack", "oud_nieuws", "te_vaag", "geen_interesse"}
REASONS_UP = {"meer_hiervan", "praktisch", "goed_uitgelegd", "nieuw_voor_mij", "mijn_stack"}
REASONS = REASONS_DOWN | REASONS_UP
# 👎 om de kwaliteit van dít artikel: telt niet tegen het onderwerp of de bron, alleen tegen de soort
# (en Claude ziet het in taste.json). Alleen geen_interesse / niet_mijn_stack / zonder reden verlagen het onderwerp.
QUALITY_DOWN = {"te_basic", "te_vaag", "oud_nieuws"}
TOPIC_DOWN = {"geen_interesse", "niet_mijn_stack"}   # alleen deze 👎-redenen gaan over het onderwerp
HALF_LIFE_DAYS = 60
WEIGHT = 0.15          # maximaal effect op de totaalscore (0-1): 15 punten
SATURATION = 6.0       # na ~6 netto stemmen is de voorkeur ongeveer 0,76; zo blijft verschil zichtbaar tussen veel en weinig duimen (was 3)
UP_WEIGHT = 2.0        # duim omhoog telt dubbel
READ_WEIGHT = 0.5      # gelezen: een benadering, telt licht (T, 31-10-2026: 0,5 tegen 2 voor een duim)


def load(path=None) -> dict:
    path = path or PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    data.setdefault("format_version", 1)
    data.setdefault("votes", {})
    data.setdefault("reads", {})
    return data


def save(data: dict, path=None):
    path = path or PATH
    path.write_text(json.dumps(data, ensure_ascii=False, indent=1, sort_keys=True), encoding="utf-8")


def _age_weight(at: str, now: datetime) -> float:
    try:
        dt = datetime.fromisoformat(at.replace("Z", "+00:00"))
    except (AttributeError, ValueError):
        return 1.0
    return math.pow(0.5, max(0.0, (now - dt).days) / HALF_LIFE_DAYS)


def preferences(data: dict, now=None) -> dict:
    """{"topics": {id: -1..1}, "sources": {id: -1..1}, "votes": n}"""
    now = now or datetime.now(timezone.utc)
    topics, sources, kinds = {}, {}, {}
    for v in data.get("votes", {}).values():
        w = v.get("v", 0) * (UP_WEIGHT if v.get("v", 0) > 0 else 1.0) * _age_weight(v.get("at", ""), now)
        if w > 0 or v.get("r") in TOPIC_DOWN:
            for t in v.get("topics", [])[:2]:  # de twee belangrijkste onderwerpen van het artikel
                topics[t] = topics.get(t, 0.0) + w
            if v.get("source_id"):
                sources[v["source_id"]] = sources.get(v["source_id"], 0.0) + w
        if v.get("soort"):   # soort artikel: praktisch, aankondiging, ... (zie enrich.SOORTEN)
            kinds[v["soort"]] = kinds.get(v["soort"], 0.0) + w
    votes = data.get("votes", {})
    for aid, r in data.get("reads", {}).items():
        if aid in votes:
            continue
        w = READ_WEIGHT * _age_weight(r.get("at", ""), now)
        for t in r.get("topics", [])[:2]:
            topics[t] = topics.get(t, 0.0) + w
        if r.get("source_id"):
            sources[r["source_id"]] = sources.get(r["source_id"], 0.0) + w
        if r.get("soort"):
            kinds[r["soort"]] = kinds.get(r["soort"], 0.0) + w
    squash = lambda d: {k: round(math.tanh(x / SATURATION), 2) for k, x in d.items() if abs(x) > 1e-9}
    return {"topics": squash(topics), "sources": squash(sources), "kinds": squash(kinds), "votes": len(data.get("votes", {})),
            "reads": len(data.get("reads", {}))}


def article_factor(article: dict, prefs: dict) -> float:
    """-1..1: gemiddelde van de voorkeur voor de onderwerpen en de bron van dit artikel.
    None als je over geen van die onderwerpen of die bron feedback gaf: dan telt feedback niet mee
    (anders duwt het nulpunt artikelen waar je nooit iets van vond omlaag)."""
    vals = [prefs["topics"][t] for t in article.get("topics", [])[:2] if t in prefs.get("topics", {})]
    if article.get("source_id") in prefs.get("sources", {}):
        vals.append(prefs["sources"][article["source_id"]])
    if article.get("soort") in prefs.get("kinds", {}):
        vals.append(prefs["kinds"][article["soort"]])
    return round(sum(vals) / len(vals), 2) if vals else None


def mean_factor(articles: list, prefs: dict) -> float:
    """Gemiddelde voorkeur over de artikelen die in aanmerking komen: het nulpunt voor 'relatief'."""
    vals = [v for v in (article_factor(a, prefs) for a in articles) if v is not None]
    return round(sum(vals) / len(vals), 3) if vals else 0.0

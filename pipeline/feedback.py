"""Jouw duimpjes (data/feedback.json) en wat de radar ervan leert.

- 👎 op een artikel: dat artikel verdwijnt uit de app.
- Per onderwerp en per bron telt de radar je stemmen op (recente zwaarder, halveert elke
  60 dagen). Dat geeft een voorkeur tussen -1 en +1.
- De voorkeur weegt mee in de relevantiescore: hooguit 8 punten erbij of eraf. Zo stuur je
  bij zonder dat één duimpje alles omgooit. Je ziet het per artikel bij "Jouw feedback".
"""
import json
import math
from datetime import datetime, timezone

from .config import DATA

PATH = DATA / "feedback.json"
REASONS = {"te_basic", "niet_mijn_stack", "oud_nieuws", "te_vaag", "geen_interesse", "meer_hiervan"}
HALF_LIFE_DAYS = 60
WEIGHT = 0.08          # maximaal effect op de totaalscore (0-1)
SATURATION = 3.0       # na ~3 netto stemmen is de voorkeur ongeveer 0,76


def load(path=None) -> dict:
    path = path or PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    data.setdefault("format_version", 1)
    data.setdefault("votes", {})
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
    topics, sources = {}, {}
    for v in data.get("votes", {}).values():
        w = v.get("v", 0) * _age_weight(v.get("at", ""), now)
        for t in v.get("topics", [])[:2]:  # de twee belangrijkste onderwerpen van het artikel
            topics[t] = topics.get(t, 0.0) + w
        if v.get("source_id"):
            sources[v["source_id"]] = sources.get(v["source_id"], 0.0) + w
    squash = lambda d: {k: round(math.tanh(x / SATURATION), 2) for k, x in d.items() if abs(x) > 1e-9}
    return {"topics": squash(topics), "sources": squash(sources), "votes": len(data.get("votes", {}))}


def article_factor(article: dict, prefs: dict) -> float:
    """-1..1: gemiddelde van de voorkeur voor de onderwerpen en de bron van dit artikel."""
    vals = [prefs["topics"][t] for t in article.get("topics", [])[:2] if t in prefs.get("topics", {})]
    if article.get("source_id") in prefs.get("sources", {}):
        vals.append(prefs["sources"][article["source_id"]])
    return round(sum(vals) / len(vals), 2) if vals else 0.0

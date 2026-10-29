"""Trends: "Dit speelt nu". Ontwikkelingen waar meerdere bronnen tegelijk over schrijven.

De Claude-taak schrijft elke ochtend data/trends.json (hooguit 3 trends). Een trend bundelt
minstens 3 uitgelegde artikelen uit minstens 2 bronnen over dezelfde ontwikkeling of
techniek (niet een breed onderwerp als "AI-agents"). De pipeline controleert het bestand en
zet alleen trends met genoeg artikelen die nog in de app staan in feed.json.
"""
import json
from datetime import datetime

from .config import DATA

PATH = DATA / "trends.json"
MAX_TRENDS = 3
MIN_ARTICLES = 3
MIN_SOURCES = 2


def validate(data: dict, topic_ids: set) -> list:
    p = []
    trends = data.get("trends")
    if not isinstance(trends, list):
        return ["trends moet een lijst zijn"]
    if len(trends) > MAX_TRENDS:
        p.append(f"hooguit {MAX_TRENDS} trends")
    seen = set()
    for i, t in enumerate(trends):
        if not isinstance(t, dict):
            p.append(f"trends[{i}] is geen object")
            continue
        for f in ["id", "title", "summary"]:
            if not isinstance(t.get(f), str) or not t[f].strip():
                p.append(f"trends[{i}]: veld '{f}' ontbreekt")
        if len(t.get("title", "")) > 80:
            p.append(f"trends[{i}]: title is langer dan 80 tekens")
        if t.get("id") in seen:
            p.append(f"trends[{i}]: id dubbel")
        seen.add(t.get("id"))
        ids = t.get("article_ids")
        if not isinstance(ids, list) or len(ids) < MIN_ARTICLES:
            p.append(f"trends[{i}]: minstens {MIN_ARTICLES} article_ids")
        unknown = [x for x in t.get("topics", []) if x not in topic_ids]
        if unknown:
            p.append(f"trends[{i}]: onbekende topics {unknown}")
    try:
        datetime.fromisoformat(str(data.get("generated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        p.append("generated_at is geen ISO-datum")
    return p


def load(topic_ids: set, shown: list, path=None) -> tuple:
    """(trends voor de app, problemen). Artikelen die niet (meer) in de app staan vallen weg;
    een trend met te weinig artikelen of bronnen daarna ook."""
    path = path or PATH
    if not path.exists():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [], [f"trends.json is geen geldige JSON ({e})"]
    problems = validate(data, topic_ids)
    if problems:
        return [], problems
    by_id = {a["id"]: a for a in shown}
    out = []
    for t in data["trends"][:MAX_TRENDS]:
        ids = [x for x in dict.fromkeys(t["article_ids"]) if x in by_id]
        if len(ids) < MIN_ARTICLES or len({by_id[x]["source_id"] for x in ids}) < MIN_SOURCES:
            continue
        out.append({"id": t["id"], "title": t["title"], "summary": t["summary"],
                    "topics": t.get("topics", []), "article_ids": ids, "generated_at": data["generated_at"]})
    return out, []

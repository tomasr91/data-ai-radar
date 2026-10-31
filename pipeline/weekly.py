"""Jouw week: elke zondagochtend een kort overzicht (data/weekly.json).

De Claude-taak schrijft het op zondag: de 3 belangrijkste ontwikkelingen van de afgelopen week,
elk met de artikelen erbij, en één zin over waar T deze week op kan letten. De app vult dat aan
met wat alleen op het toestel staat: je quizscores, wat je moet herhalen, je Leren-voortgang en
hoeveel je las. Zo komt alles van die week op één plek terug.

Formaat:
{"week": "2026-W44", "generated_at": "...Z", "intro": "...",
 "highlights": [{"title": "...", "why": "...", "article_ids": ["<12 hex>", ...]}, ...],  # 1-3
 "focus": "..."}   # optioneel: één ding om deze week te doen of te proberen
"""
import json
import re
from datetime import datetime

from .config import DATA

PATH = DATA / "weekly.json"
MAX_HIGHLIGHTS = 3


def validate(data) -> list:
    p = []
    if not isinstance(data, dict):
        return ["weekly.json moet een object zijn"]
    if not re.fullmatch(r"\d{4}-W\d{2}", str(data.get("week", ""))):
        p.append("week moet de vorm 2026-W44 hebben")
    try:
        datetime.fromisoformat(str(data.get("generated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        p.append("generated_at is geen ISO-datum")
    if not isinstance(data.get("intro"), str) or not data["intro"].strip():
        p.append("intro ontbreekt")
    hl = data.get("highlights")
    if not isinstance(hl, list) or not 1 <= len(hl) <= MAX_HIGHLIGHTS:
        p.append(f"highlights moet 1 tot {MAX_HIGHLIGHTS} items hebben")
        hl = []
    for i, h in enumerate(hl):
        if not isinstance(h, dict):
            p.append(f"highlights[{i}] is geen object")
            continue
        for f in ["title", "why"]:
            if not isinstance(h.get(f), str) or not h[f].strip():
                p.append(f"highlights[{i}]: veld '{f}' ontbreekt")
        if len(h.get("title", "")) > 90:
            p.append(f"highlights[{i}]: title is langer dan 90 tekens")
        ids = h.get("article_ids")
        if not isinstance(ids, list) or not ids or not all(isinstance(x, str) and re.fullmatch(r"[0-9a-f]{12}", x) for x in ids):
            p.append(f"highlights[{i}]: article_ids moet een lijst met artikel-id's zijn")
    if "focus" in data and not (isinstance(data["focus"], str) and data["focus"].strip()):
        p.append("focus is leeg; laat het veld dan weg")
    return p


def load(shown: list, path=None) -> tuple:
    """(overzicht voor de app of None, problemen). Links naar artikelen die niet meer in de
    app staan vallen weg; de tekst van het hoogtepunt blijft staan."""
    path = path or PATH
    if not path.exists():
        return None, []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return None, [f"weekly.json is geen geldige JSON ({e})"]
    problems = validate(data)
    if problems:
        return None, problems
    have = {a["id"] for a in shown}
    out = {k: data[k] for k in ("week", "generated_at", "intro") }
    if data.get("focus"):
        out["focus"] = data["focus"]
    out["highlights"] = [{"title": h["title"], "why": h["why"],
                          "article_ids": [x for x in dict.fromkeys(h["article_ids"]) if x in have]}
                         for h in data["highlights"][:MAX_HIGHLIGHTS]]
    return out, []

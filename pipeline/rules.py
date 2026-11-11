"""Leerregels: wat T bij een duim in eigen woorden zei ("Waarom?") en Claude 's nachts omzette in een regel.

data/leerregels.json (Claude schrijft, zie taken/LEERREGELS.md):
  {"rules": [{"id": "einde-support", "text": "Einde van support voor versies", "richting": -1, "sterkte": 1.0,
              "keywords": ["end of support", "einde support"], "labels": [], "van": "<stem-id>", "at": "2026-11-12", "active": true}],
   "noted": {"<stem-id>": "einde-support" | null}}     # null = bekeken, geen regel gemaakt

Een regel raakt alleen artikelen waar een trefwoord in de titel/samenvatting staat of een label overeenkomt,
dus andere artikelen over hetzelfde onderwerp blijven ongemoeid. Effect: richting x sterkte x 15 punten
(hooguit +-15 samen). Een regel haalt nooit een artikel uit de feed; hij verlaagt of verhoogt de score.
"""
import json
import re

from .config import DATA
from .score import _norm, _pattern

PATH = DATA / "leerregels.json"
TODO = DATA / "notes_todo.json"
MAX_POINTS = 0.15       # maximaal effect van regels samen op de score (0-1)
NOTE_MAX = 200
STALE_DAYS = 90


def load(path=None) -> dict:
    path = path or PATH
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        data = {}
    data.setdefault("rules", [])
    data.setdefault("noted", {})
    return data


def save(data: dict, path=None):
    (path or PATH).write_text(json.dumps(data, ensure_ascii=False, indent=1), encoding="utf-8")


def validate(rule) -> list:
    """Fouten in één regel (lege lijst = goed)."""
    if not isinstance(rule, dict):
        return ["regel is geen object"]
    p = []
    if not re.fullmatch(r"[a-z0-9][a-z0-9\-]{1,40}", str(rule.get("id", ""))):
        p.append("id: kleine letters, cijfers en streepjes (2-41 tekens)")
    if not (isinstance(rule.get("text"), str) and 3 <= len(rule["text"]) <= 100):
        p.append("text: 3-100 tekens, in gewoon Nederlands")
    if rule.get("richting") not in (-1, 1):
        p.append("richting: -1 (lager) of 1 (hoger)")
    s = rule.get("sterkte")
    if not (isinstance(s, (int, float)) and 0.25 <= s <= 1.0):
        p.append("sterkte: 0.25-1.0 (0.5 bij twijfel over wat T bedoelt)")
    kw, lab = rule.get("keywords", []), rule.get("labels", [])
    if not (isinstance(kw, list) and isinstance(lab, list) and all(isinstance(x, str) and x.strip() for x in kw + lab)):
        p.append("keywords en labels: lijsten van tekst")
    elif not (kw or lab):
        p.append("minstens één trefwoord of label")
    elif len(kw) > 12 or any(len(_norm(k)) < 4 for k in kw):
        p.append("keywords: hooguit 12, elk minstens 4 tekens (geen losse korte woorden)")
    if not rule.get("van"):
        p.append("van: id van de duim waaruit de regel komt")
    return p


def active_rules(data: dict) -> list:
    """Geldige, actieve regels; een foute regel doet niet mee."""
    return [r for r in data.get("rules", []) if r.get("active", True) is not False and not validate(r)]


def _text(a: dict) -> str:
    return _norm(f"{a.get('title', '')} {a.get('headline', '')} {a.get('excerpt', '')} {a.get('summary', '')}")


def matches(rule: dict, article: dict) -> bool:
    labs = {x.lower() for x in article.get("labels") or []}
    if labs & {x.lower() for x in rule.get("labels", [])}:
        return True
    text = _text(article)
    return any(_pattern(k).search(text) for k in rule.get("keywords", []))


def effect(article: dict, rules: list):
    """(delta -0.15..0.15, [{"id","text","pts"}]) voor dit artikel; (0, []) als geen regel raakt."""
    hit = [(r, r["richting"] * r["sterkte"] * MAX_POINTS) for r in rules if matches(r, article)]
    if not hit:
        return 0.0, []
    total = max(-MAX_POINTS, min(MAX_POINTS, sum(d for _, d in hit)))
    return total, [{"id": r["id"], "text": r["text"], "pts": round(d * 100)} for r, d in hit]


def view(data: dict, arts: list, today: str) -> list:
    """Voor de app: actieve regels met het aantal artikelen dat ze nu raken."""
    from datetime import date
    out = []
    for r in active_rules(data):
        n = sum(1 for a in arts if a.get("decision") not in ("excluded", "no_topic") and matches(r, a))
        try:
            old = (date.fromisoformat(today) - date.fromisoformat(r.get("at", today))).days > STALE_DAYS
        except ValueError:
            old = False
        out.append({"id": r["id"], "text": r["text"], "richting": r["richting"], "sterkte": r["sterkte"], "hits": n,
                    **({"stale": True} if old and n == 0 else {})})
    return out


def write_todo(fb_data: dict, data: dict) -> int:
    """data/notes_todo.json: duimen met een toelichting die Claude nog niet bekeek."""
    done = set(data.get("noted", {}))
    items = []
    for vid, v in sorted(fb_data.get("votes", {}).items(), key=lambda kv: kv[1].get("at", "")):
        if v.get("n") and vid not in done:
            items.append({"id": vid, "v": v.get("v"), "r": v.get("r"), "note": v["n"], "title": v.get("title", ""),
                          "topics": v.get("topics", [])[:2], "labels": v.get("labels", []), "soort": v.get("soort")})
    TODO.write_text(json.dumps({"items": items[:15]}, ensure_ascii=False, indent=1), encoding="utf-8")
    return len(items)

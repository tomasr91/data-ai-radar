"""Mijn interesses: wat de radar als interessant voor T ziet, Claudes voorstellen en het logboek.

- feed.json "interests": gebieden met richtverdeling, onderwerpen (naam, omschrijving,
  prioriteit, leeronderwerp) en wat T niet wil zien. Komt uit context/interests.yml.
- data/interest_suggestions.json: hooguit 3 voorstellen van Claude (elke zondag), bijv.
    {"id": "data-contracts", "kind": "nieuw", "name": "Data contracts",
     "description": "...", "why": "Kwam deze maand in 5 artikelen terug ..."}
    {"id": "powerbi-omhoog", "kind": "belangrijker", "topic": "powerbi_semantic_models", "why": "..."}
  kind: nieuw | belangrijker | minder | weg
- data/interest_log.json: wat Claude op T's verzoek veranderde ({"at", "text"}), nieuwste eerst.

T reageert in de app (ja/nee op voorstellen; belangrijker/minder/weg per onderwerp; vrije tekst).
Dat gaat als één GitHub-issue "Interesses: ..." naar de repo; de Claude-taak verwerkt het 's nachts
(scripts/interest_requests.py, taken/OVERZICHT.md) en past alleen context/interests.yml aan.
"""
import json
import re
from datetime import datetime

from .config import DATA

SUGGESTIONS = DATA / "interest_suggestions.json"
LOG = DATA / "interest_log.json"
KINDS = {"nieuw", "belangrijker", "minder", "weg"}
MAX_SUGGESTIONS = 3
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")


def view(conf) -> dict:
    """Interesses zoals de app ze toont."""
    topics = conf.interests.get("topics", [])
    area_of = {}
    for a in conf.interests.get("interest_areas", []):
        for t in a.get("topics", []):
            area_of[t] = a["id"]
    return {
        "areas": [{"id": a["id"], "name": a.get("label", a["id"]), "share": a.get("target_share")}
                  for a in conf.interests.get("interest_areas", [])],
        "topics": [{"id": t["id"], "name": t["name"], "description": " ".join(str(t.get("description", "")).split()),
                    "priority": t.get("priority", 3), "area": area_of.get(t["id"], "overig"),
                    **({"learning": True} if t.get("learning") else {}),
                    **({"follow": True} if t.get("follow") else {})}
                   for t in topics if t.get("enabled", True)],
        "excluded": [{"id": x["id"], "name": x.get("name", x["id"])} for x in conf.interests.get("excluded_topics", [])],
        "updated": conf.interests.get("updated"),
    }


def validate_suggestions(data, topic_ids: set) -> list:
    p = []
    if not isinstance(data, dict) or not isinstance(data.get("suggestions"), list):
        return ["interest_suggestions.json moet een object met een lijst 'suggestions' zijn"]
    try:
        datetime.fromisoformat(str(data.get("generated_at", "")).replace("Z", "+00:00"))
    except ValueError:
        p.append("generated_at is geen ISO-datum")
    if len(data["suggestions"]) > MAX_SUGGESTIONS:
        p.append(f"hooguit {MAX_SUGGESTIONS} voorstellen")
    seen = set()
    for i, s in enumerate(data["suggestions"]):
        if not isinstance(s, dict):
            p.append(f"suggestions[{i}] is geen object")
            continue
        if not ID_RE.match(str(s.get("id", ""))) or s["id"] in seen:
            p.append(f"suggestions[{i}]: id ontbreekt, is ongeldig of dubbel")
        seen.add(s.get("id"))
        if s.get("kind") not in KINDS:
            p.append(f"suggestions[{i}]: kind moet een van {sorted(KINDS)} zijn")
        if not isinstance(s.get("why"), str) or not s["why"].strip():
            p.append(f"suggestions[{i}]: why ontbreekt")
        if s.get("kind") == "nieuw":
            for f in ["name", "description"]:
                if not isinstance(s.get(f), str) or not s[f].strip():
                    p.append(f"suggestions[{i}]: '{f}' ontbreekt bij een nieuw onderwerp")
        elif s.get("kind") in KINDS and s.get("topic") not in topic_ids:
            p.append(f"suggestions[{i}]: topic '{s.get('topic')}' bestaat niet in interests.yml")
    return p


def load_suggestions(topic_ids: set, path=None) -> tuple:
    path = path or SUGGESTIONS
    if not path.exists():
        return [], []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [], [f"interest_suggestions.json is geen geldige JSON ({e})"]
    problems = validate_suggestions(data, topic_ids)
    if problems:
        return [], problems
    keep = ["id", "kind", "name", "description", "topic", "why"]
    return [{k: s[k] for k in keep if k in s} | {"generated_at": data["generated_at"]} for s in data["suggestions"]], []


def load_log(path=None, limit: int = 10) -> list:
    path = path or LOG
    try:
        data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else []
    except json.JSONDecodeError:
        return []
    items = data.get("changes", []) if isinstance(data, dict) else data
    return [x for x in items if isinstance(x, dict) and x.get("at") and x.get("text")][:limit]

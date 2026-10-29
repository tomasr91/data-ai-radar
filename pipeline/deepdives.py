"""Verdiepingen: langere stukken over een onderwerp, los van de nieuwsfeed.

Werkwijze (dagelijks):
1. De Claude-taak zet elke ochtend 5 keuzes klaar in data/deepdive_options.json.
2. T kiest in de app één keuze. De app opent dan een GitHub-issue "Verdieping: <id>".
3. De volgende ochtend schrijft de Claude-taak die verdieping (data/deepdives/<id>.json),
   sluit het issue via de commit ("Closes #n") en zet 5 nieuwe keuzes klaar.

- Ideeënlijst en regels: context/verdieping.yml.
- De pipeline zet geldige verdiepingen en de huidige keuzes in feed.json.
"""
import json
import math
import re
from datetime import datetime

import yaml

from .config import CONTEXT, DATA

DIR = DATA / "deepdives"
PLAN = CONTEXT / "verdieping.yml"
OPTIONS = DATA / "deepdive_options.json"
OPTION_FIELDS = ["id", "title", "question", "why", "topics"]
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*$")
FIELDS = ["id", "plan_id", "headline", "summary", "sections", "experiment", "limitations",
          "further_reading", "currency_check", "topics", "written_at", "processed_by"]


def load_plan(path=PLAN) -> dict:
    return yaml.safe_load(path.read_text(encoding="utf-8")) if path.exists() else {"topics": []}


def _iso_ok(value) -> bool:
    try:
        datetime.fromisoformat(str(value).replace("Z", "+00:00"))
        return True
    except ValueError:
        return False


def validate(data: dict, topic_ids: set, plan_ids: set) -> list:
    """Geeft een lijst problemen; leeg = geldig."""
    p = []
    for f in ["id", "plan_id", "headline", "summary", "experiment", "currency_check", "written_at", "processed_by"]:
        if not isinstance(data.get(f), str) or not data[f].strip():
            p.append(f"veld '{f}' ontbreekt")
    if data.get("plan_id") and data["plan_id"] not in plan_ids:
        p.append(f"plan_id '{data['plan_id']}' staat niet in verdieping.yml of in de keuzes")
    if isinstance(data.get("headline"), str) and len(data["headline"]) > 90:
        p.append("headline is langer dan 90 tekens")
    secs = data.get("sections")
    if not isinstance(secs, list) or not 3 <= len(secs) <= 8:
        p.append("sections moet 3 tot 8 onderdelen hebben")
    else:
        for i, s in enumerate(secs):
            paras = s.get("paragraphs") if isinstance(s, dict) else None
            if not (isinstance(s, dict) and isinstance(s.get("heading"), str) and s["heading"].strip()
                    and isinstance(paras, list) and 1 <= len(paras) <= 6
                    and all(isinstance(x, str) and x.strip() for x in paras)):
                p.append(f"sections[{i}] moet een heading en 1 tot 6 alinea's hebben")
    reading = data.get("further_reading")
    if not isinstance(reading, list) or not 2 <= len(reading) <= 8:
        p.append("further_reading moet 2 tot 8 bronnen hebben")
    else:
        for r in reading:
            if not (isinstance(r, dict) and str(r.get("url", "")).startswith("https://") and r.get("label")):
                p.append(f"further_reading-item zonder label of https-link: {r}")
    if not isinstance(data.get("limitations", []), list):
        p.append("limitations moet een lijst zijn")
    unknown = [t for t in data.get("topics", []) if t not in topic_ids]
    if unknown:
        p.append(f"onbekende topics {unknown}")
    if not 1 <= len(data.get("topics", []) or []) <= 4:
        p.append("topics moet 1 tot 4 onderwerpen hebben")
    if data.get("written_at") and not _iso_ok(data["written_at"]):
        p.append("written_at is geen ISO-datum")
    return p


def reading_minutes(d: dict) -> int:
    words = sum(len(x.split()) for s in d.get("sections", []) for x in s.get("paragraphs", []))
    words += len(d.get("summary", "").split()) + len(d.get("experiment", "").split())
    return max(1, math.ceil(words / 200))


def load_all(topic_ids: set, plan: dict = None) -> tuple:
    """(geldige verdiepingen voor de feed, nieuwste eerst; lijst met fouten)"""
    plan = plan or load_plan()
    plan_ids = {t["id"] for t in plan.get("topics", [])} | set(known_options())
    good, bad = [], []
    for f in sorted(DIR.glob("*.json")) if DIR.exists() else []:
        try:
            d = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError as e:
            bad.append({"file": f.name, "problems": [f"geen geldige JSON ({e})"]})
            continue
        problems = validate(d, topic_ids, plan_ids)
        if d.get("id") and d["id"] != f.stem:
            problems.append(f"id '{d['id']}' past niet bij bestandsnaam '{f.stem}'")
        if problems:
            bad.append({"file": f.name, "problems": problems})
            continue
        out = {k: d[k] for k in FIELDS if k in d}
        out["reading_minutes"] = reading_minutes(d)
        good.append(out)
    good.sort(key=lambda d: d["written_at"], reverse=True)
    return good, bad


def next_topic(plan: dict = None):
    """Bovenste ingeschakelde onderwerp zonder verdieping, of None."""
    plan = plan or load_plan()
    done = set()
    for f in DIR.glob("*.json") if DIR.exists() else []:
        try:
            done.add(json.loads(f.read_text(encoding="utf-8")).get("plan_id"))
        except json.JSONDecodeError:
            pass
    return next((t for t in plan.get("topics", []) if t.get("enabled", True) and t["id"] not in done), None)


# ---- Dagelijkse keuzes ----

def written_plan_ids() -> set:
    done = set()
    for f in DIR.glob("*.json") if DIR.exists() else []:
        try:
            done.add(json.loads(f.read_text(encoding="utf-8")).get("plan_id"))
        except json.JSONDecodeError:
            pass
    return done


def _read_options(path=None) -> dict:
    path = path or OPTIONS
    try:
        return json.loads(path.read_text(encoding="utf-8")) if path.exists() else {}
    except json.JSONDecodeError:
        return {}


def known_options(path=None) -> dict:
    """Alle keuzes die ooit zijn aangeboden (huidige + geschiedenis), op id."""
    data = _read_options(path)
    out = {}
    for o in data.get("history", []) + data.get("options", []):
        if isinstance(o, dict) and o.get("id"):
            out[o["id"]] = o
    return out


def validate_options(data: dict, topic_ids: set, done: set) -> list:
    p = []
    opts = data.get("options")
    if not isinstance(opts, list) or len(opts) != 5:
        return ["options moet precies 5 keuzes hebben"]
    seen = set()
    for i, o in enumerate(opts):
        if not isinstance(o, dict):
            p.append(f"options[{i}] is geen object")
            continue
        for f in OPTION_FIELDS:
            if not o.get(f):
                p.append(f"options[{i}]: veld '{f}' ontbreekt")
        oid = o.get("id", "")
        if oid and not ID_RE.match(oid):
            p.append(f"options[{i}]: id '{oid}' mag alleen kleine letters, cijfers en koppeltekens bevatten")
        if oid in seen:
            p.append(f"options[{i}]: id '{oid}' komt dubbel voor")
        if oid in done:
            p.append(f"options[{i}]: over '{oid}' is al een verdieping geschreven")
        seen.add(oid)
        if len(o.get("title", "")) > 80:
            p.append(f"options[{i}]: title is langer dan 80 tekens")
        unknown = [t for t in o.get("topics", []) if t not in topic_ids]
        if unknown:
            p.append(f"options[{i}]: onbekende topics {unknown}")
    if not _iso_ok(data.get("generated_at", "")):
        p.append("generated_at is geen ISO-datum")
    return p


def load_options(topic_ids: set, path=None) -> tuple:
    """(keuzes voor de app of None, lijst met problemen)"""
    data = _read_options(path)
    if not data:
        return None, []
    problems = validate_options(data, topic_ids, written_plan_ids())
    if problems:
        return None, problems
    return {"generated_at": data["generated_at"],
            "options": [{k: o[k] for k in OPTION_FIELDS + ["area"] if k in o} for o in data["options"]]}, []

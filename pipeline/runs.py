"""Taakverslagen van de nachttaken (data/runs/<datum>-<taak>.json).

Elke nachttaak (uitleggen, verdiepen, overzicht, inhalen; zie taken/REGELS.md) schrijft aan het eind
een kort verslag. De app toont het verslag van de laatste nacht op de pagina Status, en
scripts/night_status.py gebruikt het om te zien wat de inhaalrun nog moet doen.
"""
import json
import re
from datetime import datetime

from .config import DATA

DIR = DATA / "runs"
TASKS = ["uitleggen", "verdiepen", "overzicht", "inhalen"]
STATUSES = {"ok", "deels", "mislukt"}
NAME_RE = re.compile(r"^(\d{4}-\d{2}-\d{2})-(uitleggen|verdiepen|overzicht|inhalen)\.json$")


def validate(data) -> list:
    p = []
    if not isinstance(data, dict):
        return ["verslag moet een object zijn"]
    if data.get("task") not in TASKS:
        p.append(f"task moet een van {TASKS} zijn")
    if data.get("status") not in STATUSES:
        p.append(f"status moet een van {sorted(STATUSES)} zijn")
    for f in ["started_at", "finished_at"]:
        try:
            datetime.fromisoformat(str(data.get(f, "")).replace("Z", "+00:00"))
        except ValueError:
            p.append(f"{f} is geen ISO-datum")
    if not isinstance(data.get("summary"), str) or not data["summary"].strip():
        p.append("summary ontbreekt")
    if not isinstance(data.get("problems", []), list):
        p.append("problems moet een lijst zijn")
    return p


def load_all(directory=None) -> dict:
    """{datum: {taak: verslag}} voor alle geldige verslagen."""
    directory = directory or DIR
    out = {}
    if not directory.exists():
        return out
    for f in directory.glob("*.json"):
        m = NAME_RE.match(f.name)
        if not m:
            continue
        try:
            data = json.loads(f.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            continue
        if not validate(data):
            out.setdefault(m.group(1), {})[m.group(2)] = data
    return out


def latest(directory=None) -> dict:
    """Verslag van de laatste nacht voor de app: {"date": ..., "tasks": {taak: {...}}}."""
    allr = load_all(directory)
    if not allr:
        return None
    day = max(allr)
    keep = ["status", "summary", "finished_at", "problems", "counts"]
    return {"date": day, "tasks": {t: {k: r[k] for k in keep if k in r} for t, r in allr[day].items()}}

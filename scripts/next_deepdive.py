"""Zegt of er vandaag een verdieping geschreven moet worden, en over welke keuze.

Gebruik: python scripts/next_deepdive.py

Werkwijze:
- T kiest in de app één van de 5 keuzes uit data/deepdive_options.json. De app opent
  dan een GitHub-issue met de titel "Verdieping: <id>".
- Dit script zoekt het oudste open issue van die vorm, alleen als de eigenaar van de
  repository het heeft aangemaakt (de repository is openbaar; anderen tellen niet mee).
- Uitvoer:
    SCHRIJVEN: <id> (issue #n)   + de gekozen keuze als JSON
    GEEN KEUZE                   T heeft niets gekozen; vandaag geen verdieping
    ONBEKEND                     GitHub niet bereikbaar; vandaag geen verdieping
- Eigen onderwerp: T zette iets op "Jouw lijst" in de app en koos "Maak hier een verdieping van".
  Het issue heet dan "Verdieping: eigen-<slug>" en de tekst bevat regels
  "Onderwerp: ...", "Notitie: ..." en "Gezien in: ...". Uitvoer: SCHRIJVEN met own: true.
  Daarna altijd: maak 5 nieuwe keuzes (zie TAAK_VERRIJKEN.md).
- Alleen 's nachts (00:00-09:00 Nederlandse tijd). Overdag (een extra run) zegt het script
  NIET NU: dan geen verdieping en geen nieuwe keuzes. Zo staat alles wat je kiest pas de
  volgende ochtend in de app (T, 1-11-2026).
- Per nacht: de gewone keuze (de oudste) én daarnaast hooguit 2 eigen voorstellen.
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import deepdives  # noqa: E402
from pipeline.build import DEFAULT_REPO  # noqa: E402

TITLE_RE = re.compile(r"^\s*Verdieping:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", re.I)


def repo_name() -> str:
    if os.environ.get("RADAR_REPO"):
        return os.environ["RADAR_REPO"]
    try:
        url = subprocess.run(["git", "remote", "get-url", "origin"], cwd=ROOT, capture_output=True, text=True).stdout
        m = re.search(r"([\w.-]+)/([\w.-]+?)(?:\.git)?/?\s*$", url)
        if m:
            return f"{m.group(1)}/{m.group(2)}"
    except OSError:
        pass
    return DEFAULT_REPO


def open_issues(repo: str) -> list:
    req = urllib.request.Request(f"https://api.github.com/repos/{repo}/issues?state=open&per_page=50&sort=created&direction=asc",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "data-ai-radar"})
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r)


FIELD_RE = {"title": re.compile(r"^Onderwerp:\s*(.+)$", re.M), "note": re.compile(r"^Notitie:\s*(.+)$", re.M),
            "seen_in": re.compile(r"^Gezien in:\s*(.+)$", re.M)}


def own_topic(oid: str, body: str) -> dict:
    """Keuze-object voor een eigen onderwerp, uit de issuetekst."""
    f = {k: (r.search(body or "") or [None, ""])[1].strip() for k, r in FIELD_RE.items()}
    title = f["title"] or oid.removeprefix("eigen-").replace("-", " ")
    return {"id": oid, "title": title[:120], "question": f["note"][:500], "seen_in": f["seen_in"][:300], "own": True}


def choices(issues: list, owner: str) -> list:
    """[(issue-nummer, keuze-id)] van de eigenaar, oudste eerst."""
    out = []
    for i in issues:
        if "pull_request" in i:
            continue
        if (i.get("user") or {}).get("login", "").lower() != owner.lower():
            continue
        m = TITLE_RE.match(i.get("title", ""))
        if m:
            out.append((i["number"], m.group(1).lower()))
    return sorted(out)


NIGHT = (0, 9)        # uren (Nederlandse tijd) waarin verdiepingen geschreven mogen worden
MAX_OWN = 2           # hooguit zoveel eigen voorstellen per nacht, naast de gewone keuze


def is_night(now=None) -> bool:
    now = (now or datetime.now(timezone.utc)).astimezone(ZoneInfo("Europe/Amsterdam"))
    return NIGHT[0] <= now.hour < NIGHT[1]


def plan(issues: list, owner: str, known: dict, done: set, now=None) -> list:
    """Regels voor de Claude-taak. Alleen 's nachts wordt er geschreven: de gewone keuze
    (de oudste) en daarnaast hooguit MAX_OWN eigen voorstellen ('eigen-...')."""
    if not is_night(now):
        return ["NIET NU: verdiepingen en nieuwe keuzes horen alleen bij de nachtrun (00:00-09:00 Nederlandse tijd). "
                "Schrijf in deze run GEEN verdieping en maak GEEN nieuwe keuzes; doe de rest van de taak wel."]
    out, regular, own = [], None, []
    bodies = {i["number"]: i.get("body") or "" for i in issues if "number" in i}
    for number, oid in choices(issues, owner):
        if oid in done:
            out.append(f"AL GESCHREVEN: '{oid}' (issue #{number}). Sluit dit issue met Closes #{number}; schrijf niets.")
        elif oid.startswith("eigen-"):
            if len(own) < MAX_OWN:
                own.append((number, oid))
            else:
                out.append(f"LATER: eigen voorstel '{oid}' (issue #{number}) komt een volgende nacht aan de beurt.")
        elif oid not in known:
            out.append(f"ONBEKENDE KEUZE: '{oid}' (issue #{number}) staat niet in de keuzes. Sla over en meld het.")
        elif regular is None:
            regular = (number, oid)
        else:
            out.append(f"LATER: keuze '{oid}' (issue #{number}) komt morgennacht aan de beurt (één gewone verdieping per nacht).")
    if regular:
        out.append(f"SCHRIJVEN: {regular[1]} (issue #{regular[0]})")
        out.append(json.dumps(known[regular[1]], ensure_ascii=False, indent=2))
    for number, oid in own:
        out.append(f"SCHRIJVEN: {oid} (issue #{number}) - eigen voorstel van T")
        out.append(json.dumps(own_topic(oid, bodies.get(number, "")), ensure_ascii=False, indent=2))
    if not regular and not own:
        out.append("GEEN KEUZE: er is niets gekozen. Vandaag geen verdieping.")
    out.append("\nDaarna: maak 5 nieuwe keuzes in data/deepdive_options.json (zie TAAK_VERRIJKEN.md).")
    return out


def main():
    repo = repo_name()
    if not is_night():
        print("\n".join(plan([], "", {}, set())))
        return
    try:
        issues = open_issues(repo)
    except Exception as e:  # noqa: BLE001
        print(f"ONBEKEND: GitHub-issues van {repo} niet bereikbaar ({str(e)[:100]}). Vandaag geen verdieping.")
        return
    print("\n".join(plan(issues, repo.split("/")[0], deepdives.known_options(), deepdives.written_plan_ids())))


if __name__ == "__main__":
    main()

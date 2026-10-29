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
  Daarna altijd: maak 5 nieuwe keuzes (zie TAAK_VERRIJKEN.md).
"""
import json
import os
import re
import subprocess
import sys
import urllib.request
from pathlib import Path

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


def main():
    repo = repo_name()
    try:
        issues = open_issues(repo)
    except Exception as e:  # noqa: BLE001
        print(f"ONBEKEND: GitHub-issues van {repo} niet bereikbaar ({str(e)[:100]}). Vandaag geen verdieping.")
        return
    known = deepdives.known_options()
    done = deepdives.written_plan_ids()
    picked = choices(issues, repo.split("/")[0])
    for number, oid in picked:
        if oid in done:
            print(f"AL GESCHREVEN: '{oid}' (issue #{number}). Sluit dit issue; schrijf niets.")
            continue
        if oid not in known:
            print(f"ONBEKENDE KEUZE: '{oid}' (issue #{number}) staat niet in de keuzes. Sla over en meld het.")
            continue
        print(f"SCHRIJVEN: {oid} (issue #{number})")
        print(json.dumps(known[oid], ensure_ascii=False, indent=2))
        break
    else:
        print("GEEN KEUZE: er is niets gekozen. Vandaag geen verdieping.")
    print("\nDaarna: maak 5 nieuwe keuzes in data/deepdive_options.json (zie TAAK_VERRIJKEN.md).")


if __name__ == "__main__":
    main()

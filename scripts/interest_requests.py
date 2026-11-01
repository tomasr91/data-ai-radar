"""Wat T in de app aan zijn interesses wil veranderen (issues "Interesses: ...").

Gebruik: python scripts/interest_requests.py

De app stuurt T's reacties als één GitHub-issue met een JSON-blok:
    {"answers": [{"id": "<voorstel-id>", "a": "ja" | "nee"}],
     "changes": [{"topic": "<onderwerp-id>", "c": "belangrijker" | "minder" | "weg" | "leren" | "niet_leren"}],
     "note": "vrije tekst"}
Dit script zet de open issues van de eigenaar (de repository is openbaar; anderen tellen niet)
om in een duidelijke werklijst voor de Claude-taak. Net als verdiepingen alleen 's nachts.
Uitvoer per issue: VERWERKEN: issue #n + de verzoeken; of GEEN VERZOEKEN / NIET NU / ONBEKEND.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from next_deepdive import is_night, open_issues, repo_name  # noqa: E402
from pipeline import interests  # noqa: E402

TITLE_RE = re.compile(r"^\s*Interesses:", re.I)
BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)
CHANGES = {"belangrijker", "minder", "weg", "leren", "niet_leren"}


def parse(body: str) -> dict:
    m = BLOCK_RE.search(body or "")
    try:
        data = json.loads(m.group(1)) if m else {}
    except json.JSONDecodeError:
        data = {}
    answers = [a for a in data.get("answers", []) if isinstance(a, dict) and a.get("a") in ("ja", "nee")
               and interests.ID_RE.match(str(a.get("id", "")))]
    changes = [c for c in data.get("changes", []) if isinstance(c, dict) and c.get("c") in CHANGES
               and re.fullmatch(r"[a-z0-9_]+", str(c.get("topic", "")))]
    note = str(data.get("note", "")).strip()[:1000]
    return {"answers": answers, "changes": changes, "note": note}


def requests(issues: list, owner: str) -> list:
    out = []
    for i in sorted(issues, key=lambda i: i.get("number", 0)):
        if "pull_request" in i or not TITLE_RE.match(i.get("title", "")):
            continue
        if (i.get("user") or {}).get("login", "").lower() != owner.lower():
            continue
        out.append((i["number"], parse(i.get("body", ""))))
    return out


def main():
    if not is_night():
        print("NIET NU: interesses worden alleen in de nachtrun aangepast. Verander niets aan interests.yml.")
        return
    repo = repo_name()
    try:
        issues = open_issues(repo)
    except Exception as e:  # noqa: BLE001
        print(f"ONBEKEND: GitHub-issues niet bereikbaar ({str(e)[:100]}). Verander niets aan interests.yml.")
        return
    todo = requests(issues, repo.split("/")[0])
    if not todo:
        print("GEEN VERZOEKEN: T heeft niets aan zijn interesses gevraagd.")
        return
    sugg = {}
    if interests.SUGGESTIONS.exists():
        sugg = {s["id"]: s for s in json.loads(interests.SUGGESTIONS.read_text(encoding="utf-8")).get("suggestions", [])}
    for number, req in todo:
        print(f"VERWERKEN: issue #{number} (sluit met Closes #{number})")
        for a in req["answers"]:
            s = sugg.get(a["id"])
            print(f"  voorstel {a['id']}: {a['a'].upper()}" + (f"  -> {json.dumps(s, ensure_ascii=False)}" if s else "  (voorstel niet meer gevonden)"))
        for c in req["changes"]:
            print(f"  onderwerp {c['topic']}: {c['c']}")
        if req["note"]:
            print(f"  in eigen woorden: {req['note']}")


if __name__ == "__main__":
    main()

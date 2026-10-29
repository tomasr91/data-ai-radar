"""Verwerkt duimpjes uit de app: GitHub-issues "Feedback: ..." -> data/feedback.json.

De app is een statische site. Je beoordelingen (👍/👎 met reden) worden daarom verstuurd als
één GitHub-issue met een JSON-blok. Deze stap (GitHub Actions) leest die issues, voegt de
stemmen toe aan data/feedback.json en sluit het issue met een korte reactie.

Alleen issues van de eigenaar van de repository tellen (de repository is openbaar).
Zonder GITHUB_TOKEN (bijv. lokaal) wordt er alleen gelezen, niets gesloten.

Gebruik: python scripts/collect_feedback.py
"""
import json
import os
import re
import sys
import urllib.request
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import feedback  # noqa: E402
from pipeline.build import DEFAULT_REPO  # noqa: E402

TITLE_RE = re.compile(r"^\s*Feedback:", re.I)
BLOCK_RE = re.compile(r"```json\s*(\{.*?\})\s*```", re.S)
API = "https://api.github.com"


def _req(url, token=None, method="GET", data=None):
    headers = {"Accept": "application/vnd.github+json", "User-Agent": "data-ai-radar"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data is not None else None
    req = urllib.request.Request(url, data=body, method=method, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.load(r) if r.status != 204 else None


def parse_votes(body: str) -> list:
    """Stemmen uit het JSON-blok in de issuetekst; ongeldige regels vallen weg."""
    m = BLOCK_RE.search(body or "")
    if not m:
        return []
    try:
        data = json.loads(m.group(1))
    except json.JSONDecodeError:
        return []
    out = []
    for v in data.get("votes", []):
        if not isinstance(v, dict):
            continue
        aid, vote = str(v.get("id", "")), v.get("v")
        if re.fullmatch(r"[0-9a-f]{12}", aid) and vote in (1, -1):
            reason = v.get("r") if v.get("r") in feedback.REASONS else None
            out.append({"id": aid, "v": vote, "r": reason})
    return out


def owner_issues(issues: list, owner: str) -> list:
    return [i for i in issues if "pull_request" not in i and TITLE_RE.match(i.get("title", ""))
            and (i.get("user") or {}).get("login", "").lower() == owner.lower()]


def main():
    repo = os.environ.get("GITHUB_REPOSITORY", DEFAULT_REPO)
    token = os.environ.get("GITHUB_TOKEN")
    try:
        issues = _req(f"{API}/repos/{repo}/issues?state=open&per_page=50", token)
    except Exception as e:  # noqa: BLE001
        print(f"Feedback: GitHub niet bereikbaar ({str(e)[:100]}); niets verwerkt.")
        return 0
    todo = owner_issues(issues, repo.split("/")[0])
    if not todo:
        print("Feedback: geen nieuwe beoordelingen.")
        return 0
    articles = {}
    feed_path = ROOT / "data" / "feed.json"
    if feed_path.exists():
        articles = {a["id"]: a for a in json.loads(feed_path.read_text(encoding="utf-8")).get("articles", [])}
    now = datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")
    store = feedback.load()
    total = 0
    for issue in todo:
        votes = parse_votes(issue.get("body", ""))
        for v in votes:
            a = articles.get(v["id"], {})
            prev = store["votes"].get(v["id"], {})
            store["votes"][v["id"]] = {
                "v": v["v"], "r": v["r"], "at": now, "issue": issue["number"],
                "title": a.get("headline") or a.get("title") or prev.get("title", ""),
                "topics": a.get("topics") or prev.get("topics", []),
                "source_id": a.get("source_id") or prev.get("source_id", ""),
            }
        total += len(votes)
        print(f"Feedback: issue #{issue['number']}: {len(votes)} beoordelingen")
        if token:
            msg = (f"Verwerkt: {len(votes)} beoordeling(en). De radar houdt er vanaf nu rekening mee."
                   if votes else "Geen leesbare beoordelingen gevonden in dit issue.")
            _req(f"{API}/repos/{repo}/issues/{issue['number']}/comments", token, "POST", {"body": msg})
            _req(f"{API}/repos/{repo}/issues/{issue['number']}", token, "PATCH", {"state": "closed", "state_reason": "completed"})
    store["updated_at"] = now
    feedback.save(store)
    print(f"Feedback: {total} beoordelingen verwerkt, {len(store['votes'])} in totaal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Wat moet de inhaalrun (taken/INHALEN.md) nog doen?

Gebruik: python scripts/night_status.py

Kijkt voor vandaag (datum in Europe/Amsterdam) per nachttaak of die gelukt is:
- uitleggen: verslag van vandaag met status ok;
- verdiepen: verslag ok, keuzes voor morgen van vandaag, en geen gekozen verdieping die nog geschreven moet;
- overzicht: verslag ok, en op zondag een Jouw week voor deze week.
Uitvoer: ONTBREEKT: <taak> (reden) per taak, of ALLES KLAAR.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "scripts"))
from pipeline import runs  # noqa: E402

AMS = ZoneInfo("Europe/Amsterdam")


def local_date(iso: str):
    try:
        return datetime.fromisoformat(str(iso).replace("Z", "+00:00")).astimezone(AMS).date()
    except ValueError:
        return None


def missing(now=None, data_dir=None, pending_deepdive=None) -> list:
    """[(taak, reden)] voor wat vannacht nog ontbreekt."""
    now = (now or datetime.now(timezone.utc)).astimezone(AMS)
    data_dir = data_dir or ROOT / "data"
    today = now.date()
    rep = runs.load_all(data_dir / "runs").get(today.isoformat(), {})
    out = []

    def ok(task):
        return rep.get(task, {}).get("status") == "ok"
    if not ok("uitleggen"):
        out.append(("uitleggen", "geen geslaagd verslag van vannacht"))
    reasons = []
    if not ok("verdiepen"):
        reasons.append("geen geslaagd verslag van vannacht")
    try:
        opts = json.loads((data_dir / "deepdive_options.json").read_text(encoding="utf-8"))
        if local_date(opts.get("generated_at")) != today:
            reasons.append("keuzes voor morgen zijn niet van vandaag")
    except (OSError, json.JSONDecodeError):
        reasons.append("keuzes voor morgen ontbreken")
    if pending_deepdive:
        reasons.append("een gekozen verdieping is nog niet geschreven")
    if reasons:
        out.append(("verdiepen", "; ".join(reasons)))
    reasons = []
    if not ok("overzicht"):
        reasons.append("geen geslaagd verslag van vannacht")
    if now.weekday() == 6:
        try:
            w = json.loads((data_dir / "weekly.json").read_text(encoding="utf-8")).get("week")
        except (OSError, json.JSONDecodeError):
            w = None
        y, wk, _ = today.isocalendar()
        if w != f"{y}-W{wk:02d}":
            reasons.append("Jouw week van deze week ontbreekt")
    if reasons:
        out.append(("overzicht", "; ".join(reasons)))
    return out


def main():
    pending = False
    try:
        import next_deepdive as nd
        if nd.is_night():
            issues = nd.open_issues(nd.repo_name())
            from pipeline import deepdives
            lines = nd.plan(issues, nd.repo_name().split("/")[0], deepdives.known_options(), deepdives.written_plan_ids())
            pending = any(line.startswith("SCHRIJVEN") for line in lines)
    except Exception:  # noqa: BLE001  GitHub niet bereikbaar: alleen op de verslagen afgaan
        pass
    todo = missing(pending_deepdive=pending)
    if not todo:
        print("ALLES KLAAR: alle nachttaken zijn gelukt.")
        return
    for task, why in todo:
        print(f"ONTBREEKT: {task} ({why})")


if __name__ == "__main__":
    main()

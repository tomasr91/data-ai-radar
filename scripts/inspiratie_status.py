"""Wat de nachttaak voor Inspiratie moet doen (taken/INSPIRATIE.md).

Gebruik: python scripts/inspiratie_status.py
- NIET NU: weekend, of de kaart van vandaag bestaat al.
- SCHRIJVEN: daarna de namen en links die al geweest zijn (niet herhalen) en T's duimpjes.
"""
import json
import sys
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import feedback, inspiratie  # noqa: E402


def main():
    today = datetime.now(ZoneInfo("Europe/Amsterdam"))
    day = today.date().isoformat()
    if today.weekday() >= 5:
        print("NIET NU: weekend, alleen op werkdagen.")
        return
    if (inspiratie.DIR / f"{day}.json").exists():
        print(f"NIET NU: data/inspiratie/{day}.json bestaat al.")
        return
    print(f"SCHRIJVEN: data/inspiratie/{day}.json")
    cards, _ = inspiratie.load_all(keep_days=100000)
    print("\nAl geweest (niet herhalen, ook niet hetzelfde product of dezelfde link):")
    for c in cards:
        for x in c["ideas"]:
            print(f"- {c['date']} [{x['cat']}] {x['naam']}" + (f" | {x['link']}" if x.get("link") else ""))
    if not cards:
        print("- (nog niets)")
    votes = feedback.load().get("inspiratie", {})
    print("\nDuimpjes van T (meer van 👍, minder van 👎):")
    for iid, v in sorted(votes.items()):
        print(f"- {'👍' if v['v'] == 1 else '👎'} {v.get('naam') or iid}")
    if not votes:
        print("- (nog geen)")


if __name__ == "__main__":
    main()

"""Zegt of er vandaag een verdieping geschreven moet worden, en over welk onderwerp.

Gebruik: python scripts/next_deepdive.py
Regel: een nieuwe verdieping als de nieuwste 3 dagen of ouder is (of er nog geen is).
Zo komen er ongeveer twee per week.
"""
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline import deepdives  # noqa: E402

MIN_DAYS = 3


def main():
    now = datetime.now(timezone.utc)
    dates = []
    for f in deepdives.DIR.glob("*.json") if deepdives.DIR.exists() else []:
        try:
            dates.append(datetime.fromisoformat(json.loads(f.read_text(encoding="utf-8"))["written_at"].replace("Z", "+00:00")))
        except (KeyError, ValueError, json.JSONDecodeError):
            pass
    last = max(dates) if dates else None
    days = (now - last).days if last else None
    topic = deepdives.next_topic()
    if topic is None:
        print("GEEN: geen open onderwerp in context/verdieping.yml")
    elif days is not None and days < MIN_DAYS:
        print(f"NIET VANDAAG: de nieuwste verdieping is {days} dag(en) oud (minimaal {MIN_DAYS})")
    else:
        print(f"SCHRIJVEN: {topic['id']}")
        print(json.dumps(topic, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()

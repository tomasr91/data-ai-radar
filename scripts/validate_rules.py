"""Controleert data/leerregels.json (zie pipeline/rules.py). Uitvoer: '<n> regels, <m> fouten'; exit 1 bij fouten."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from pipeline import rules  # noqa: E402


def main() -> int:
    data = rules.load()
    errors, ids = [], set()
    for r in data["rules"]:
        for p in rules.validate(r):
            errors.append(f"{r.get('id', '?')}: {p}")
        if r.get("id") in ids:
            errors.append(f"{r.get('id')}: dubbel id")
        ids.add(r.get("id"))
    for vid, rid in data["noted"].items():
        if rid is not None and rid not in ids:
            errors.append(f"noted {vid}: regel {rid} bestaat niet")
    for e in errors:
        print("FOUT", e)
    print(f"{len(data['rules'])} regels, {len(errors)} fouten")
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())

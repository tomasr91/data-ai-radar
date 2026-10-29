"""Controleert alle uitlegbestanden in data/enrichment/.

Gebruik: python scripts/validate_enrichment.py [bestand ...]
Zonder argumenten: alle bestanden. Exitcode 1 als er een fout bestand is.
Claude draait dit voordat het uitleg pusht; de workflow draait het ook.
"""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from pipeline.config import load  # noqa: E402
from pipeline.enrich import CACHE, validate  # noqa: E402
from pipeline.normalize import article_id  # noqa: E402
from pipeline import deepdives  # noqa: E402

META = ["article_id", "url", "processed_by", "processed_at"]


def check(path: Path, topics: set) -> list:
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        return [f"geen geldige JSON ({e})"]
    problems = validate(data, topics)
    problems += [f"veld '{m}' ontbreekt" for m in META if not data.get(m)]
    if data.get("article_id") and data["article_id"] != path.stem:
        problems.append(f"article_id '{data['article_id']}' past niet bij bestandsnaam '{path.stem}'")
    if data.get("url") and article_id(data["url"]) != path.stem:
        problems.append("url hoort niet bij deze article_id")
    for d in data.get("official_docs", []) or []:
        if not str(d.get("url", "")).startswith("https://"):
            problems.append(f"official_docs bevat geen https-link: {d}")
    return problems


def main(argv):
    topics = set(load().topics)
    files = [Path(a) for a in argv] or sorted(CACHE.glob("*.json"))
    bad = 0
    for f in files:
        problems = check(f, topics)
        if problems:
            bad += 1
            print(f"FOUT {f.name}: " + "; ".join(problems))
    skipped = CACHE / "skipped"
    for f in (sorted(skipped.glob("*.json")) if skipped.exists() and not argv else []):
        try:
            if not json.loads(f.read_text(encoding="utf-8")).get("reason"):
                bad += 1
                print(f"FOUT skipped/{f.name}: veld 'reason' ontbreekt")
        except json.JSONDecodeError:
            bad += 1
            print(f"FOUT skipped/{f.name}: geen geldige JSON")
    if not argv:
        good, wrong = deepdives.load_all(topics)
        for w in wrong:
            bad += 1
            print(f"FOUT deepdives/{w['file']}: " + "; ".join(w["problems"]))
        print(f"{len(good) + len(wrong)} verdiepingen gecontroleerd")
        if deepdives.OPTIONS.exists():
            opts, problems = deepdives.load_options(topics)
            for pr in problems:
                bad += 1
                print(f"FOUT deepdive_options.json: {pr}")
            if opts:
                print(f"{len(opts['options'])} keuzes voor morgen gecontroleerd")
        from pipeline import trends as trends_mod
        if trends_mod.PATH.exists():
            try:
                tdata = json.loads(trends_mod.PATH.read_text(encoding="utf-8"))
                tproblems = trends_mod.validate(tdata, topics)
            except json.JSONDecodeError as e:
                tdata, tproblems = {}, [f"geen geldige JSON ({e})"]
            for pr in tproblems:
                bad += 1
                print(f"FOUT trends.json: {pr}")
            if not tproblems:
                print(f"{len(tdata.get('trends', []))} trends gecontroleerd")
    print(f"{len(files)} uitlegbestanden gecontroleerd, {bad} fout")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

"""Leren door te zien: een optioneel blok bij een uitleg of verdieping.

showcase ("Zo ziet het eruit"): een klein stukje echte code met het resultaat eronder.
    {"caption": "...", "language": "sql|yaml|python|bash|json|text", "code": "...",
     "result": {"columns": [...], "rows": [[...], ...]},   # optioneel
     "note": "Waar komt dit vandaan / wat is nagebouwd"}

"""
LANGUAGES = {"sql", "yaml", "python", "bash", "json", "text"}
MAX_CODE = 2500
MAX_ROWS = 12


def _text(v) -> bool:
    return isinstance(v, str) and bool(v.strip())


def validate_showcase(s) -> list:
    if s is None:
        return []
    p = []
    if not isinstance(s, dict):
        return ["showcase moet een object zijn"]
    for f in ["caption", "code", "note"]:
        if not _text(s.get(f)):
            p.append(f"showcase.{f} ontbreekt")
    if s.get("language") not in LANGUAGES:
        p.append(f"showcase.language moet een van {sorted(LANGUAGES)} zijn")
    if isinstance(s.get("code"), str) and len(s["code"]) > MAX_CODE:
        p.append(f"showcase.code is langer dan {MAX_CODE} tekens; houd het voorbeeld klein")
    r = s.get("result")
    if r is not None:
        cols, rows = (r or {}).get("columns"), (r or {}).get("rows")
        if not (isinstance(cols, list) and cols and isinstance(rows, list) and 1 <= len(rows) <= MAX_ROWS
                and all(isinstance(x, list) and len(x) == len(cols) for x in rows)):
            p.append(f"showcase.result moet columns en 1 tot {MAX_ROWS} rows met evenveel waarden hebben")
    return p

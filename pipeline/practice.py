"""Leren door te zien en te doen: twee optionele blokken bij een uitleg of verdieping.

showcase ("Zo ziet het eruit"): een klein stukje echte code met het resultaat eronder.
    {"caption": "...", "language": "sql|yaml|python|bash|json|text", "code": "...",
     "result": {"columns": [...], "rows": [[...], ...]},   # optioneel
     "note": "Waar komt dit vandaan / wat is nagebouwd"}

exercise ("Oefen het zelf"): een SQL-opdracht die in de browser draait (DuckDB), op een kleine
verzonnen dataset. De app vergelijkt jouw uitkomst met die van de oplossing.
    {"title": "...", "task": "...", "setup_sql": "CREATE TABLE ...; INSERT ...",
     "starter_sql": "...", "solution_sql": "...", "hint": "...", "explanation": "...",
     "ordered": false}

De controle hieronder draait de oefening echt (Python-pakket duckdb), zodat er geen kapotte
oefening in de app komt. Zonder duckdb-pakket wordt alleen de vorm gecontroleerd.
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


def _run(con, sql):
    return con.execute(sql).fetchall()


def validate_exercise(e, run=True) -> list:
    if e is None:
        return []
    p = []
    if not isinstance(e, dict):
        return ["exercise moet een object zijn"]
    for f in ["title", "task", "setup_sql", "starter_sql", "solution_sql", "explanation"]:
        if not _text(e.get(f)):
            p.append(f"exercise.{f} ontbreekt")
    if p or not run:
        return p
    try:
        import duckdb  # noqa: PLC0415
    except ImportError:
        return p
    try:
        con = duckdb.connect(":memory:")
        con.execute(e["setup_sql"])
        rows = _run(con, e["solution_sql"])
        if not rows:
            p.append("exercise.solution_sql geeft geen rijen terug")
        elif len(rows) > 50:
            p.append("exercise.solution_sql geeft meer dan 50 rijen; houd het overzichtelijk")
    except Exception as ex:  # noqa: BLE001 - elke fout = kapotte oefening
        p.append(f"exercise draait niet in DuckDB: {str(ex).splitlines()[0][:160]}")
    return p

"""Browsertest voor 'Zo ziet het eruit' en 'Oefen het zelf' (DuckDB in de browser).

Gebruikt een lokale kopie van @duckdb/duckdb-wasm (zelfde versie als de app van jsdelivr laadt):
    mkdir -p /tmp/ddb && cd /tmp/ddb && npm init -y && npm install @duckdb/duckdb-wasm@1.32.0
Daarna: python tests/e2e_duckdb.py  (zonder die map wordt de test overgeslagen)
"""
import functools
import http.server
import json
import os
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
NM = Path(os.environ.get("DUCKDB_NODE_MODULES", "/tmp/ddb/node_modules"))
if not (NM / "@duckdb/duckdb-wasm/dist/duckdb-browser.mjs").exists():
    print("Overgeslagen: geen lokale @duckdb/duckdb-wasm gevonden in", NM)
    sys.exit(0)
sys.path.insert(0, str(ROOT))
from pipeline import config as cfg, deepdives as dd  # noqa: E402

feed = json.loads((ROOT / "data/feed.json").read_text(encoding="utf-8"))
T = set(cfg.load().topics)
feed["deepdives"], _ = dd.load_all(T)
# Artikel met oefening uit de cache erbij zetten (ook als feed.json nog niet opnieuw is gebouwd)
cached = json.loads((ROOT / "data/enrichment/60e7e131218f.json").read_text(encoding="utf-8"))
for a in feed["articles"]:
    if a["id"] == "60e7e131218f":
        a.update({k: cached[k] for k in ("showcase", "exercise")})
art = next(a for a in feed["articles"] if a["id"] == "60e7e131218f")

d = Path(tempfile.mkdtemp())
os.symlink(NM, d / "nm")
head = ('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
        '<script type="importmap">{"imports":{"apache-arrow":"/nm/apache-arrow/Arrow.dom.mjs",'
        '"tslib":"/nm/tslib/tslib.es6.mjs","flatbuffers":"/nm/flatbuffers/mjs/flatbuffers.js"}}</script>'
        '<script>window.RADAR_DUCKDB_MODULE="/nm/@duckdb/duckdb-wasm/dist/duckdb-browser.mjs";'
        'window.RADAR_DUCKDB_DIST=location.origin+"/nm/@duckdb/duckdb-wasm/dist/";</script>')
(d / "index.html").write_text(head + (ROOT / "app/index.html").read_text(encoding="utf-8"), encoding="utf-8")
(d / "feed.json").write_text(json.dumps(feed), encoding="utf-8")
http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
http.server.SimpleHTTPRequestHandler.extensions_map[".wasm"] = "application/wasm"
srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(d)))
threading.Thread(target=srv.serve_forever, daemon=True).start()
url = f"http://127.0.0.1:{srv.server_address[1]}/index.html"

results = []
def check(name, cond, detail=""):
    results.append(bool(cond))
    print(("OK   " if cond else "FOUT ") + name + (f"  ({detail})" if detail and not cond else ""))

with sync_playwright() as p:
    b = p.chromium.launch()
    pg = b.new_page(viewport={"width": 412, "height": 900})
    errors = []
    pg.on("pageerror", lambda e: errors.append(str(e)))
    pg.route("**/fonts.g*/**", lambda r: r.abort())
    pg.route("https://api.github.com/**", lambda r: r.fulfill(status=200, body="[]", headers={"Access-Control-Allow-Origin": "*"}))
    pg.goto(url + "#a-" + art["id"])
    pg.wait_for_selector("#reader:not([hidden]) .show")
    txt = pg.locator(".show").inner_text()
    check("Zo ziet het eruit: code en resultaattabel", "AVG(aantal) OVER" in txt and pg.locator(".show table.res tr").count() == 1 + len(art["showcase"]["result"]["rows"]))
    check("Oefenblok met startquery", "SUM(stand)" in pg.locator("#ex-sql").input_value())
    pg.click('[data-ex="run"]')
    pg.wait_for_selector("#ex-out .ex-msg.no, #ex-out .ex-msg.ok", timeout=60000)
    out = pg.locator("#ex-out").inner_text()
    check("startquery (optellen) is fout en toont de uitkomst", "Bijna" in out and pg.locator("#ex-out table.res").count() == 1, out[:120])
    out = pg.locator("#ex-out").inner_text()
    check("datum als datum getoond", "2026-10-05" in out, repr(out[-160:]))
    pg.click('[data-ex="hint"]')
    check("hint zichtbaar", "ROW_NUMBER" in pg.locator("#ex-out").inner_text())
    pg.click('[data-ex="solution"]'); pg.click('[data-ex="run"]')
    pg.wait_for_selector("#ex-out .ex-msg.ok", timeout=30000)
    check("oplossing geeft 'Klopt!'", "Klopt" in pg.locator("#ex-out").inner_text())
    pg.fill("#ex-sql", "SELECT * FROM bestaat_niet")
    pg.click('[data-ex="run"]')
    pg.wait_for_selector("#ex-out .ex-msg.no", timeout=30000)
    check("SQL-fout wordt netjes gemeld", "Fout in je SQL" in pg.locator("#ex-out").inner_text())
    # verdieping
    first = next(x for x in feed["deepdives"] if x["id"] == "evals-ai-assistent")
    if first.get("exercise"):
        pg.goto(url + "#v-" + first["id"]); pg.reload()
        pg.wait_for_selector("#reader:not([hidden]) #ex")
        pg.click('[data-ex="solution"]'); pg.click('[data-ex="run"]')
        pg.wait_for_selector("#ex-out .ex-msg.ok", timeout=60000)
        check("oefening in verdieping werkt", "75" in pg.locator("#ex-out").inner_text())
    check("geen JavaScript-fouten", not errors, "; ".join(errors))
    b.close()
print(f"\n{sum(results)} van {len(results)} controles geslaagd")
sys.exit(0 if all(results) else 1)

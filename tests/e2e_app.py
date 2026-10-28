"""End-to-end test van de app in headless Chromium (telefoonformaat).

Draaien: python tests/e2e_app.py   (vereist: pip install playwright && playwright install chromium)
Gebruikt data/feed.json; zet een kopie naast de app en start een lokale server.
"""
import functools
import http.server
import json
import shutil
import sys
import tempfile
import threading
from pathlib import Path

from playwright.sync_api import sync_playwright

ROOT = Path(__file__).resolve().parent.parent
SHOTS = Path(sys.argv[1]) if len(sys.argv) > 1 else None


def serve(directory):
    handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(directory))
    http.server.SimpleHTTPRequestHandler.log_message = lambda *a: None
    srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    return srv, f"http://127.0.0.1:{srv.server_address[1]}/index.html"


def site(feed_text=None):
    d = Path(tempfile.mkdtemp())
    # Bij publiceren zet het platform de pagina in een skelet met <meta charset>; lokaal bootsen we dat na.
    page = (ROOT / "app" / "index.html").read_text(encoding="utf-8")
    (d / "index.html").write_text('<!doctype html><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">' + page, encoding="utf-8")
    if feed_text is not None:
        (d / "feed.json").write_text(feed_text, encoding="utf-8")
    return d


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("OK   " if cond else "FOUT ") + name + (f"  ({detail})" if detail and not cond else ""))


feed = json.loads((ROOT / "data" / "feed.json").read_text(encoding="utf-8"))
arts = feed["articles"]

with sync_playwright() as p:
    browser = p.chromium.launch()
    phone = dict(viewport={"width": 412, "height": 915}, device_scale_factor=2, is_mobile=True, has_touch=True, locale="nl-NL")

    srv, url = serve(site(json.dumps(feed)))
    page = browser.new_page(**phone)
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and "fonts.g" not in m.text and "Failed to load resource" not in m.text and errors.append(m.text))
    page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    page.route("**/fonts.gstatic.com/**", lambda r: r.abort())

    # 1-2. App opent en laadt artikelen
    page.goto(url)
    page.wait_for_selector(".card")
    check("1. app opent en toont artikelen", page.locator(".card").count() == len(arts), f"{page.locator('.card').count()} kaarten")
    status = page.locator("#status").inner_text()
    check("2. status maakt modus zichtbaar", "Momentopname" in status if feed["mode"] == "snapshot" else feed["mode"] in status.lower(), status)
    ids = page.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
    check("10. geen dubbele artikelen in de lijst", len(ids) == len(set(ids)))
    check("    'Belangrijkst' toont max. 5", page.locator(".top5 li").count() == min(5, len(feed["daily_top"])))
    if SHOTS:
        page.screenshot(path=str(SHOTS / "1-feed.png"))

    # 3. Filteren op onderwerp
    for g in feed["groups"]:
        page.click(f'.chip[data-g="{g["id"]}"]')
        expected = sum(1 for a in arts if g["id"] in a["groups"])
        n = page.locator(".card").count()
        ok = n == expected and (expected > 0 or page.locator(".empty").count() == 1)
        check(f"3. filter '{g['label']}'", ok, f"{n} getoond, {expected} verwacht")
    page.click('.chip[data-g="all"]')

    # Zoeken en periode
    page.fill("#q", "Okta")
    page.wait_for_timeout(300)
    check("   zoeken op 'Okta'", page.locator(".card").count() == 1)
    page.fill("#q", "")
    page.wait_for_timeout(300)
    page.click('#seg-period button[data-v="week"]')
    week = page.locator(".card").count()
    check("   periodefilter 'Week' sluit artikelen zonder datum uit", 0 < week <= len(arts))
    page.click('#seg-period button[data-v="all"]')
    page.click('#seg-sort button[data-v="date"]')
    dates = page.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
    by = {a["id"]: a.get("published_at") or "" for a in arts}
    check("   sorteren op nieuwste", [by[i] for i in dates] == sorted([by[i] for i in dates], reverse=True))
    page.click('#seg-sort button[data-v="score"]')

    # 4-6. Artikel openen, uitleg, bron en link
    enriched = next(a for a in arts if a["processing_status"] == "enriched")
    page.click(f'.card[data-id="{enriched["id"]}"]')
    page.wait_for_selector("#reader:not([hidden]) article.full")
    reader = page.locator("#reader").inner_text()
    check("4. artikel opent", enriched["title"] in reader)
    check("5. uitleg zichtbaar", all(s in reader for s in ["Wat is er nieuw?", "Eenvoudig uitgelegd", "Waarom is dit relevant voor jou?", "Wat kun je ermee?"]))
    check("5. bronvermelding met datum", "Gepubliceerd" in reader and "Opgehaald" in reader)
    hrefs = page.eval_on_selector_all("#reader a.btn", "els => els.map(e => [e.href, e.target, e.rel])")
    check("6. link naar origineel klopt en opent in nieuw tabblad", any(h[0] == enriched["url"] and h[1] == "_blank" for h in hrefs), str(hrefs))
    if SHOTS:
        page.screenshot(path=str(SHOTS / "2-artikel.png"))
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    check("   terug naar de feed", page.locator(".card").count() == len(arts))

    raw = next((a for a in arts if a["processing_status"] == "raw"), None)
    if raw:
        page.goto(url + "#a-" + raw["id"])
        page.wait_for_selector("#reader:not([hidden])")
        check("   onverwerkt artikel is herkenbaar en heeft bronlink", "nog niet door AI uitgelegd" in page.locator("#reader").inner_text())

    # 7. Feedcontrole toont mislukte bronnen
    page.goto(url + "#feedcontrole")
    page.wait_for_selector("#reader .tbl")
    rows = page.locator("#reader .tbl").first.locator("tbody tr").count()
    check("7. feedcontrole toont alle bronnen met status", rows == len(feed["sources"]))
    failed = [s for s in feed["sources"] if s["status"] == "failed"]
    check("7. mislukte bronnen zichtbaar, rest geladen", (not failed or page.locator(".st.failed").count() == len(failed)) and len(arts) > 0)
    if SHOTS:
        page.screenshot(path=str(SHOTS / "3-feedcontrole.png"))

    # 8. Mobiel: geen horizontaal scrollen
    page.goto(url)
    page.wait_for_selector(".card")
    sw = page.evaluate("document.documentElement.scrollWidth - window.innerWidth")
    check("8. geen horizontaal scrollen op 412px", sw <= 0, f"{sw}px te breed")
    small = page.eval_on_selector_all(".chip, .seg button, .icon-btn", "els => els.filter(e => e.getBoundingClientRect().height < 28).length")
    check("8. knoppen groot genoeg voor aanraken", small == 0)
    page.emulate_media(color_scheme="dark")
    if SHOTS:
        page.screenshot(path=str(SHOTS / "4-donker.png"))
    bg = page.evaluate("getComputedStyle(document.body).backgroundColor")
    check("   donker thema actief", bg != "rgb(243, 244, 241)", bg)
    check("   geen JavaScript-fouten", not errors, "; ".join(errors))
    srv.shutdown()

    # 9. Kapotte of ontbrekende feed: nette foutmelding
    for label, text in [("ongeldige JSON", "{not json"), ("ontbrekend bestand", None),
                        ("verkeerde versie", json.dumps({"schema_version": 99, "articles": []}))]:
        srv, u = serve(site(text))
        pg = browser.new_page(**phone)
        errs = []
        pg.on("pageerror", lambda e: errs.append(str(e)))
        pg.route("**/fonts.g*/**", lambda r: r.abort())
        pg.goto(u)
        pg.wait_for_selector(".empty")
        txt = pg.locator("#status").inner_text()
        check(f"9. {label}: uitleg in plaats van crash", "kon niet worden geladen" in txt and not errs, txt[:80])
        pg.close()
        srv.shutdown()
    browser.close()

failed = [r for r in results if not r[1]]
print(f"\n{len(results) - len(failed)} van {len(results)} controles geslaagd")
sys.exit(1 if failed else 0)

"""End-to-end test van de app in headless Chromium (telefoonformaat).

Draaien: python tests/e2e_app.py   (vereist: pip install playwright && playwright install chromium)
Gebruikt data/feed.json; zet een kopie naast de app en start een lokale server.
"""
import re
import functools
import http.server
import json
import shutil
import sys
import tempfile
import threading
from datetime import datetime
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
    shutil.copytree(ROOT / "app" / "leren", d / "leren")
    return d


results = []


def check(name, cond, detail=""):
    results.append((name, bool(cond), detail))
    print(("OK   " if cond else "FOUT ") + name + (f"  ({detail})" if detail and not cond else ""))


feed = json.loads((ROOT / "data" / "feed.json").read_text(encoding="utf-8"))
arts = feed["articles"]
# Verdiepingen uit de repo gebruiken, ook als feed.json nog niet opnieuw is gebouwd.
sys.path.insert(0, str(ROOT))
from pipeline import config as _cfg, deepdives as _dd  # noqa: E402
feed["deepdives"], _ = _dd.load_all(set(_cfg.load().topics))
dds = feed["deepdives"]
feed["deepdive_options"], _ = _dd.load_options(set(_cfg.load().topics))
feed["repo"] = "tomasr91/data-ai-radar"
opts = feed["deepdive_options"]["options"]
# Nagebootste GitHub-API: de eigenaar koos de tweede keuze; een vreemde koos de eerste (telt niet).
# Nagebootste trend: drie artikelen uit minstens twee bronnen
_tr, _srcs = [], set()
for _a in arts:
    if len(_tr) < 3 and (len(_tr) < 2 or _a["source_id"] not in _srcs or len(_srcs) > 1):
        _tr.append(_a["id"]); _srcs.add(_a["source_id"])
feed["trends"] = [{"id": "test-trend", "title": "Testtrend", "summary": "Drie artikelen over hetzelfde.", "topics": [], "article_ids": _tr, "generated_at": "2026-10-29T06:00:00Z"}]
GH = {"issues": "[]"}  # eerst niets gekozen
FAKE_ISSUES = json.dumps([
    {"number": 7, "title": f"Verdieping: {opts[1]['id']}", "user": {"login": "tomasr91"}},
    {"number": 8, "title": f"Verdieping: {opts[0]['id']}", "user": {"login": "iemand-anders"}},
])

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
    page.route("https://api.github.com/**", lambda r: r.fulfill(status=200, content_type="application/json", body=GH["issues"], headers={"Access-Control-Allow-Origin": "*"}))

    # 1-2. App opent en laadt artikelen
    page.goto(url)
    page.wait_for_selector(".card")
    check("1. app opent en toont artikelen", page.locator(".card").count() == len(arts), f"{page.locator('.card').count()} kaarten")
    upd = page.locator("#upd").inner_text()
    check("2. laatste update met datum en tijd zichtbaar", "Nieuwe artikelen" in upd and re.search(r"\d{4}.*\d{2}:\d{2}", upd) is not None, upd)
    check("   geen zoekbalk, chips of periodekeuze meer", page.locator("#q, .chip, #seg-period, .top5").count() == 0)
    check("   filters Nieuw, Relevant en Trends", page.locator("#seg-sort button").all_inner_texts() == ["Nieuw", "Relevant", "Trends"])
    ids = page.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
    check("10. geen dubbele artikelen in de lijst", len(ids) == len(set(ids)))
    if SHOTS:
        page.screenshot(path=str(SHOTS / "1-feed.png"))

    page.click('#seg-sort button[data-v="date"]')
    dates = page.eval_on_selector_all(".card", "els => els.map(e => e.dataset.id)")
    # Nieuw = nieuw in de radar: moment van uitleg, anders van ophalen, anders publicatie.
    def added(a):
        iso = a.get("processed_at") or a.get("fetched_at") or a.get("published_at")
        return datetime.fromisoformat(iso.replace("Z", "+00:00")).timestamp() if iso else 0
    by = {a["id"]: added(a) for a in arts}
    check("   filter Nieuw sorteert op toegevoegd aan de radar", [by[i] for i in dates] == sorted([by[i] for i in dates], reverse=True))
    page.click('#seg-sort button[data-v="trends"]')
    check("13. Trends toont de trend met zijn artikelen", page.locator(".trend").count() == 1 and page.locator(".trend-list button").count() == len(_tr)
          and "Testtrend" in page.locator(".trend").inner_text())
    page.locator(".trend-list button").first.click()
    page.wait_for_selector("#reader:not([hidden]) article.full")
    check("   artikel uit een trend opent", page.locator("#reader").is_visible())
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    page.click('#seg-sort button[data-v="score"]')

    # 4-6. Artikel openen, uitleg, bron en link
    enriched = next(a for a in arts if a["processing_status"] == "enriched")
    page.click(f'.card[data-id="{enriched["id"]}"]')
    page.wait_for_selector("#reader:not([hidden]) article.full")
    reader = page.locator("#reader").inner_text()
    check("4. artikel opent", (enriched.get("headline") or enriched["title"]) in reader)
    if enriched.get("format_version") == 2:
        check("5. uitleg zichtbaar (nieuwe stijl), zonder bronfeiten", enriched["story"][0][:40] in reader and "Probeer dit" in reader
              and "Bronfeiten" not in reader and enriched["title"] in reader)
    else:
        check("5. uitleg zichtbaar", all(s in reader for s in ["Wat is er nieuw?", "Eenvoudig uitgelegd", "Waarom is dit relevant voor jou?", "Wat kun je ermee?"]))
    check("5. bron toont alleen publicatiedatum en datum in de app", "Gepubliceerd" in reader and "In de app sinds" in reader
          and "Opgehaald" not in reader and "Uitgelegd door" not in reader)
    check("5. scoreuitleg standaard verborgen", not page.locator("#score-dlg").is_visible())
    page.click("#score-btn")
    check("5. knop toont scoreuitleg in een venster", page.locator("#score-dlg").is_visible() and "Waarom deze score?" in page.locator("#score-dlg").inner_text())
    page.keyboard.press("Escape")
    check("5. Escape sluit eerst het venster, niet het artikel", not page.locator("#score-dlg").is_visible() and page.locator("#reader").is_visible())
    hrefs = page.eval_on_selector_all("#reader a.btn", "els => els.map(e => [e.href, e.target, e.rel])")
    check("6. link naar origineel klopt en opent in nieuw tabblad", any(h[0] == enriched["url"] and h[1] == "_blank" for h in hrefs), str(hrefs))
    if SHOTS:
        page.screenshot(path=str(SHOTS / "2-artikel.png"))
    # 16. Vraag het Claude
    page.evaluate("window.__opened = []; window.open = (u) => { window.__opened.push(u); return null; }")
    check("16. Vraag het Claude met snelle vragen", page.locator("#ask [data-ask]").count() == 4)
    page.locator("#ask [data-ask]").first.click()
    page.fill("#ask-q", "Werkt dit ook met Unity Catalog?")
    page.click("#ask-form button[type=submit]")
    opened = [u for u in page.evaluate("window.__opened") if isinstance(u, str)]
    from urllib.parse import unquote as _uq
    ok = len(opened) == 2 and all(u.startswith("https://claude.ai/new?q=") and len(u) < 7000 for u in opened)
    txt = _uq(opened[-1]) if opened else ""
    check("   opent Claude met artikel, bron en jouw vraag", ok and (enriched.get("headline") or enriched["title"]) in txt
          and enriched["url"] in txt and "Werkt dit ook met Unity Catalog?" in txt, f"{len(opened)} geopend, {max(map(len, opened)) if opened else 0} tekens")

    # 14. Duimpje
    check("14. duimpjes onderaan het artikel", page.locator("#fb [data-vote]").count() == 2)
    page.click('#fb [data-vote="-1"]')
    page.click('#fb [data-reason="te_basic"]')
    check("   reden te kiezen na duim omlaag", page.locator('#fb [data-reason="te_basic"][aria-pressed="true"]').count() == 1)
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    check("   artikel met duim omlaag verdwijnt uit de lijst", page.locator(f'.card[data-id="{enriched["id"]}"]').count() == 0
          and page.locator(".card[data-id]").count() == len(arts) - 1)
    sh = page.locator("#fb-send").get_attribute("href") or ""
    from urllib.parse import unquote
    body = unquote(sh)
    check("   versturen maakt een feedback-issue met de stem als JSON",
          "issues/new?title=Feedback" in sh and f'"id":"{enriched["id"]}","v":-1,"r":"te_basic"' in body, body[-160:])
    page.route("https://github.com/**", lambda r: r.abort())
    page.click("#fb-send")
    page.wait_for_timeout(500)
    check("   na versturen verdwijnt de knop", page.locator("#fb-send").count() == 0)
    page.evaluate("localStorage.removeItem('radar:fb')")
    page.evaluate("location.reload()")
    page.wait_for_selector(".card")
    check("   terug naar de feed", page.locator(".card").count() == len(arts))

    # 11. Tabblad Verdieping
    check("11. tabbladen Actueel, Verdieping en Leren", page.locator("#seg-view button").all_inner_texts() == ["Actueel", "Verdieping", "Leren"])
    page.click('#seg-view button[data-v="verdieping"]')
    page.wait_for_timeout(100)
    check("   Verdieping toont alleen verdiepingen", page.locator(".card[data-dd]").count() == len(dds) and page.locator(".card[data-id]").count() == 0)
    check("12. subtabjes Verdiepingen en Morgen", page.locator("#seg-dd button").all_inner_texts() == ["Verdiepingen", "Morgen"] and page.locator("#seg-dd").is_visible())
    ids = page.eval_on_selector_all(".card[data-dd]", "els => els.map(e => e.dataset.dd)")
    check("   verdiepingen op datum, nieuwste eerst", ids == [d["id"] for d in sorted(dds, key=lambda d: d["written_at"], reverse=True)])
    check("   geen keuzes op het tabje Verdiepingen", page.locator(".card.opt").count() == 0)
    page.click('#seg-dd button[data-v="morgen"]')
    check("   tabje Morgen toont vijf keuzes", page.locator("a.card.opt").count() == 5 and page.locator(".card[data-dd]").count() == 0)
    href = page.locator("a.card.opt").first.get_attribute("href")
    check("   keuze opent een GitHub-issue met de juiste titel",
          href.startswith("https://github.com/tomasr91/data-ai-radar/issues/new?title=") and f"Verdieping%3A%20{opts[0]['id']}" in href, href[:120])
    # Terug uit GitHub: de eigenaar heeft nu gekozen
    GH["issues"] = FAKE_ISSUES
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_selector(".card.opt.chosen", timeout=3000)
    chosen = page.eval_on_selector_all(".card.opt", "els => els.map(e => e.dataset.opt)")
    check("   na kiezen alleen de keuze van de eigenaar", chosen == [opts[1]["id"]], str(chosen))
    page.click('#seg-dd button[data-v="alle"]')
    check("   sorteerknoppen verborgen bij Verdieping", not page.locator("#seg-sort").is_visible())
    if dds:
        page.locator(".card[data-dd]").first.click()
        page.wait_for_selector("#reader:not([hidden]) article.dd")
        text = page.locator("#reader").inner_text()
        first = sorted(dds, key=lambda d: d["written_at"], reverse=True)[0]
        check("   verdieping opent met onderdelen en Verder lezen", first["headline"] in text and first["sections"][0]["heading"] in text and "Verder lezen" in text)
        if first.get("quiz"):
            q0 = first["quiz"][0]
            wrong = next(i for i in range(len(q0["options"])) if i != q0["answer"])
            check("15. Test jezelf met controlevragen", page.locator(".quiz .q").count() == len(first["quiz"]))
            page.locator(".quiz .q").first.locator(f'[data-opt-i="{wrong}"]').click()
            exp = page.locator(".quiz .q").first.inner_text()
            check("   fout antwoord: uitleg en 'komt over een week terug'", "Niet goed" in exp and "week terug" in exp)
            # een week later: vraag staat klaar als herhaling
            page.evaluate("""() => { const d = JSON.parse(localStorage.getItem('radar:quiz')); for (const k in d) d[k].due = '2000-01-01T00:00:00Z'; localStorage.setItem('radar:quiz', JSON.stringify(d)); }""")
        if SHOTS:
            page.screenshot(path=str(SHOTS / "3-verdieping.png"))
        page.click("#back")
        page.wait_for_selector("#reader", state="hidden")
        check("   terug naar de verdiepingen", page.locator(".card[data-dd]").count() == len(dds))
        if first.get("quiz"):
            page.click('#seg-view button[data-v="actueel"]'); page.click('#seg-view button[data-v="verdieping"]')
            check("   herhaling klaar bij Verdiepingen", "1 vraag om te herhalen" in page.locator("#content").inner_text())
            page.click('a[href="#herhaling"]')
            page.wait_for_selector("#reader:not([hidden]) .quiz .q")
            page.locator(".quiz .q").first.locator(f'[data-opt-i="{q0["answer"]}"]').click()
            check("   goed in de herhaling: klaar", "Goed." in page.locator(".quiz .q").first.inner_text()
                  and page.evaluate("JSON.parse(localStorage.getItem('radar:quiz'))[Object.keys(JSON.parse(localStorage.getItem('radar:quiz')))[0]].ok") is True)
            page.click("#back")
            page.wait_for_selector("#reader", state="hidden")
    page.click('#seg-view button[data-v="actueel"]')
    page.wait_for_timeout(100)
    check("   terug naar Actueel", page.locator(".card[data-id]").count() == len(arts))

    check("   onverwerkte artikelen staan niet in de app", all(a["processing_status"] == "enriched" for a in arts))
    raw = None
    if raw:
        page.goto(url + "#a-" + raw["id"])
        page.wait_for_selector("#reader:not([hidden])")
        check("   onverwerkt artikel is herkenbaar en heeft bronlink", "nog niet uitgelegd" in page.locator("#reader").inner_text())

    # 17. Leren: het Claude-examen in een venster
    page.goto(url)
    page.wait_for_selector(".card")
    page.click('#seg-view button[data-v="leren"]')
    page.wait_for_selector("#leren-frame")
    fr = page.frame_locator("#leren-frame")
    fr.locator(".cert").first.wait_for(timeout=15000)
    certs = fr.locator(".cert").all_inner_texts()
    check("17. Leren toont alleen examens met vragen: Associate en Developer", certs == ["Associate", "Developer"], str(certs))
    fr.locator('[data-act="start"]').first.click()
    fr.locator(".q .opt").first.wait_for(timeout=5000)
    for i in range(fr.locator(".q .opt").count()):
        if fr.locator('[data-act="check"]').is_enabled():
            break
        fr.locator(".q .opt").nth(i).click()
    fr.locator('[data-act="check"]').scroll_into_view_if_needed()
    y_check = fr.locator('[data-act="check"]').bounding_box()["y"]
    scroll0 = page.evaluate("window.scrollY")
    fr.locator('[data-act="check"]').click()
    fr.locator(".verdict-line").first.wait_for(timeout=5000)
    y_next = fr.locator('[data-act="next"]').bounding_box()["y"]
    check("   na controleren verspringt het scherm niet: Volgende staat waar Controleer stond",
          abs(y_next - y_check) < 4 and page.evaluate("window.scrollY") == scroll0, f"{y_check} -> {y_next}")
    # Met de uitleg open vóór het antwoorden: na controleren mag het scherm ook niet verspringen
    fr.locator('[data-act="next"]').click()
    fr.locator(".q .opt").first.wait_for(timeout=5000)
    if fr.locator('.q [data-act="explain"]').count():
        fr.locator('.q [data-act="explain"]').first.click()
        fr.locator(".explain.pre").wait_for(timeout=3000)
        for i in range(fr.locator(".q .opt").count()):
            if fr.locator('[data-act="check"]').is_enabled():
                break
            fr.locator(".q .opt").nth(i).click()
        fr.locator('[data-act="check"]').scroll_into_view_if_needed()
        yq, yc = fr.locator(".qtext").bounding_box()["y"], fr.locator('[data-act="check"]').bounding_box()["y"]
        fr.locator('[data-act="check"]').click()
        fr.locator(".verdict-line").first.wait_for(timeout=5000)
        yq2, yn = fr.locator(".qtext").bounding_box()["y"], fr.locator('[data-act="next"]').bounding_box()["y"]
        check("   met uitleg open: na controleren blijft alles staan", abs(yq2 - yq) < 4 and abs(yn - yc) < 4, f"vraag {yq}->{yq2}, knop {yc}->{yn}")
    # Volgende vraag: het vraagblok staat zo hoog mogelijk, direct onder de vaste tabbalk
    fr.locator('[data-act="next"]').click()
    fr.locator(".q .opt").first.wait_for(timeout=5000)
    page.wait_for_timeout(200)
    q_top = fr.locator(".q").bounding_box()["y"]
    bar = page.evaluate("document.querySelector('.filters').getBoundingClientRect().bottom")
    check("   volgende vraag: vraagblok direct onder de tabbalk", 0 <= q_top - bar <= 20, f"vraag {q_top}, tabbalk {bar}")
    saved = page.evaluate("JSON.parse(localStorage.getItem('cca-academy-v2') || 'null')")
    n = sum(c["total"]["n"] for c in saved["certs"].values()) if saved else 0
    check("   vraag beantwoorden werkt en wordt bewaard", n >= 1, str(n))
    fr.locator('[data-act="report"]').first.click()
    fr.locator("#reportBox").fill("Testmelding")
    page.evaluate("() => { const w = document.getElementById('leren-frame').contentWindow; w.__o = []; w.open = (u) => { w.__o.push(u); return null; }; }")
    fr.locator('[data-act="sendreport"]').first.click()
    opened = page.evaluate("document.getElementById('leren-frame').contentWindow.__o")
    check("   melding opent een GitHub-issue 'Examenmelding'", len(opened) == 1 and "issues/new?title=Examenmelding" in opened[0], str(opened)[:120])
    page.evaluate("localStorage.removeItem('cca-academy-v2')")
    page.reload(); page.wait_for_selector("#leren-frame")
    check("   Actueel en Verdieping verborgen, filters weg", not page.locator("#main").is_visible() and not page.locator("#seg-sort").is_visible() and not page.locator("#seg-dd").is_visible())
    bg = page.evaluate("getComputedStyle(document.getElementById('leren-frame').contentDocument.body).backgroundColor")
    check("   examen in het donkere Radar-thema", bg == "rgb(15, 18, 23)", bg)
    h = page.evaluate("document.getElementById('leren-frame').getBoundingClientRect().height")
    check("   venster groeit mee met de inhoud", h > 500, str(h))
    home = fr.locator("#app").inner_text()
    check("   rustig startscherm: geen uitleg, titel of opslagmelding", all(x not in home for x in ["Hoe werkt het herhalen", "Gebaseerd op", "Claude Certification Academy", "Rondes van 10"]) and "Begin met oefenen" in home and "Back-up" in home)
    page.click('#seg-view button[data-v="actueel"]')
    check("   terug naar Actueel werkt", page.locator(".card[data-id]").count() == len(arts) and page.locator("#leren").is_hidden())
    page.click('#seg-view button[data-v="leren"]')
    check("   examen blijft geladen bij terugkeren", page.locator("#leren-frame").count() == 1 and page.locator("#leren").is_visible())
    page.click('#seg-view button[data-v="actueel"]')

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
    small = page.eval_on_selector_all(".tabs button, .icon-btn", "els => els.filter(e => e.offsetParent !== null && e.getBoundingClientRect().height < 28).length")
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

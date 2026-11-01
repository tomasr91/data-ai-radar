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
# Een verdieping uit een eigen voorstel (Later): krijgt het label "jouw voorstel"
if dds:
    dds.append(dict(dds[-1], id="eigen-test-voorstel", plan_id="eigen-test-voorstel", written_at="2026-10-01T05:00:00Z"))
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
# Nagebootst weekoverzicht (Jouw week)
from datetime import datetime as _dt, timezone as _tz  # noqa: E402
feed["weekly"] = {"week": "2026-W44", "generated_at": _dt.now(_tz.utc).isoformat().replace("+00:00", "Z"),
                  "intro": "Een week vol semantische lagen.", "focus": "Probeer een metric view.",
                  "highlights": [{"title": "Hoogtepunt een", "why": "Daarom.", "article_ids": [arts[0]["id"], arts[1]["id"]]},
                                 {"title": "Hoogtepunt twee", "why": "Ook daarom.", "article_ids": [arts[2]["id"]]}]}
# Nagebootste begrippen in het eerste artikel met een verhaal, en de woordenlijst
_ta = next(a for a in arts if a.get("story"))
_tw = next(w.strip(".,:;()\"'") for w in " ".join(_ta["story"]).split() if len(w.strip(".,:;()\"'")) > 6)
_ta["terms"] = [{"term": _tw, "explanation": "Testuitleg van het begrip."}]
feed["glossary"] = [{"term": _tw, "explanation": "Testuitleg van het begrip.", "refs": [{"kind": "a", "id": _ta["id"], "title": _ta.get("headline") or _ta["title"]}]},
                    {"term": "Zzz-begrip", "explanation": "Nog een.", "refs": [{"kind": "a", "id": _ta["id"], "title": "x"}]}]
# Lampje: leeronderwerpen (de pipeline zet "learning" per artikel)
for _a in arts[:2]:
    _a["learning"] = "Data ingestion"
for _a in arts[2:]:
    _a.pop("learning", None)
_learn = [a["id"] for a in arts[:2]]
# Mijn interesses: uit interests.yml, met nagebootste voorstellen en logboek
from pipeline import interests as _int  # noqa: E402
feed["interests"] = _int.view(_cfg.load())
feed["interest_suggestions"] = [
    {"id": "data-contracts", "kind": "nieuw", "name": "Data contracts", "description": "Afspraken over vorm en kwaliteit van data tussen teams.", "why": "Kwam deze maand vaak terug.", "generated_at": "2026-11-01T04:00:00Z"},
    {"id": "powerbi-omhoog", "kind": "belangrijker", "topic": "powerbi_semantic_models", "why": "Je leest Power BI-artikelen helemaal.", "generated_at": "2026-11-01T04:00:00Z"}]
feed["interest_log"] = [{"at": "2026-10-31T04:30:00Z", "text": "Test-wijziging in het logboek."}]
# Nagebootste taakverslagen van de nacht
feed["runs"] = {"date": "2026-11-02", "tasks": {
    "uitleggen": {"status": "ok", "summary": "12 artikelen uitgelegd", "finished_at": "2026-11-02T03:58:00Z", "problems": []},
    "verdiepen": {"status": "deels", "summary": "1 verdieping, keuzes niet gelukt", "finished_at": "2026-11-02T04:40:00Z", "problems": ["tijd op"]}}}
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
    page.add_init_script("window.__radarReadMs = 300")
    errors = []
    page.on("pageerror", lambda e: errors.append(str(e)))
    page.on("console", lambda m: m.type == "error" and "fonts.g" not in m.text and "Failed to load resource" not in m.text and errors.append(m.text))
    page.route("**/fonts.googleapis.com/**", lambda r: r.abort())
    page.route("**/fonts.gstatic.com/**", lambda r: r.abort())
    page.route("https://api.github.com/**", lambda r: r.fulfill(status=200, content_type="application/json", body=GH["issues"], headers={"Access-Control-Allow-Origin": "*"}))

    # 1-2. App opent en laadt artikelen
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")
    check("1. app opent en toont artikelen", page.locator(".card").count() == len(arts), f"{page.locator('.card').count()} kaarten")
    upd = page.locator("#upd").inner_text()
    check("2. laatste update met datum en tijd zichtbaar", "Nieuwe artikelen" not in upd and re.search(r"\d{1,2} \w+.*\d{2}:\d{2}", upd, re.S) is not None, upd)
    check("   geen zoekbalk, chips of periodekeuze meer", page.locator("#q, .chip, #seg-period, .top5").count() == 0)
    # Verversen houdt tab en subtab; een nieuwe sessie (app opnieuw openen) begint bij Actueel
    page.click('#seg-view button[data-v="verdieping"]'); page.click('#seg-dd button[data-v="morgen"]')
    page.reload(); page.wait_for_selector("#seg-dd:not([hidden])")
    check("   verversen blijft op Verdieping > Morgen", page.locator('#seg-view button[aria-selected="true"]').inner_text() == "Verdieping"
          and page.locator('#seg-dd button[aria-pressed="true"]').inner_text() == "Morgen")
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()"); page.reload(); page.wait_for_timeout(1500)
    page.wait_for_selector(".card")
    check("   bij openen: Actueel en Nieuw", page.locator('#seg-view button[aria-selected="true"]').inner_text() == "Actueel"
          and page.locator('#seg-sort button[aria-pressed="true"]').inner_text() == "Nieuw")
    check("   filters Nieuw en Trends (Relevant is weg)", page.locator("#seg-sort button").all_inner_texts() == ["Nieuw", "Trends"])
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
    src = {a["id"]: a["source_id"] for a in arts}
    def spread(lst, mx=2):   # zelfde regel als de app: nooit meer dan 2 van dezelfde bron achter elkaar
        rest, out = list(lst), []
        while rest:
            run = src[out[-1]] if len(out) >= mx and all(src[x] == src[out[-1]] for x in out[-mx:]) else None
            i = next((k for k, x in enumerate(rest) if src[x] != run), 0) if run else 0
            out.append(rest.pop(i))
        return out
    check("   filter Nieuw sorteert op toegevoegd aan de radar", dates == spread(sorted(dates, key=lambda i: -by[i])))
    from itertools import groupby
    check("   nooit meer dan 2 kaarten van dezelfde bron achter elkaar", max(len(list(g)) for _, g in groupby(src[i] for i in dates)) <= 2
          or len({src[i] for i in dates}) == 1)
    page.click('#seg-sort button[data-v="trends"]')
    check("13. Trends toont de trend met zijn artikelen", page.locator(".trend").count() == 1 and page.locator(".trend-list button").count() == len(_tr)
          and "Testtrend" in page.locator(".trend").inner_text())
    page.locator(".trend-list button").first.click()
    page.wait_for_selector("#reader:not([hidden]) article.full")
    check("   artikel uit een trend opent", page.locator("#reader").is_visible())
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    page.click('#seg-sort button[data-v="date"]')

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
    check("16. Vraag het Claude met snelle vragen (ingeklapt tot je erop tikt)", page.locator("#ask [data-ask]").count() == 4 and not page.locator("#ask").is_visible())
    page.click("#ask-toggle")
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
    check("   artikel met duim omlaag blijft in de lijst", page.locator(f'.card[data-id="{enriched["id"]}"]').count() == 1
          and page.locator(".card[data-id]").count() == len(arts))
    sh = page.locator("#fb-send").get_attribute("href") or ""
    from urllib.parse import unquote
    body = unquote(sh)
    check("   issue begint met een link terug naar de app", "[↩ Terug naar de Data & AI Radar](http://127.0.0.1" in body)
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

    # 20. Lampje bij leeronderwerpen
    lamps = page.locator(".card .lamp").count()
    check("20. lampje alleen op kaarten over leeronderwerpen", lamps == len(_learn)
          and all(page.locator(f'.card[data-id="{i}"] > .lamp').count() == 1 for i in _learn), f"{lamps} vs {len(_learn)}")

    # 22. Ochtendronde: nieuw sinds je laatste bezoek, gelezen gedimd, Volgende, puntje op Verdieping
    by_added = sorted(arts, key=lambda a: a.get("processed_at") or a.get("fetched_at") or "", reverse=True)
    _times = sorted({a.get("processed_at") or a.get("fetched_at") or "" for a in arts}, reverse=True)
    mid = _times[1]
    page.evaluate(f"""() => {{ localStorage.setItem('radar:lastVisit', '{mid}'); sessionStorage.clear();
        localStorage.setItem('radar:read', JSON.stringify({{'a-{by_added[0]['id']}': {{at: new Date().toISOString(), sent: true}}}})); }}""")
    page.reload(); page.wait_for_selector(".card")
    n_new = sum(1 for a in arts if (a.get("processed_at") or a.get("fetched_at") or "") > mid)
    pos = page.evaluate("[...document.querySelectorAll('#content .cards > *')].findIndex(e => e.classList.contains('since-line'))")
    check("22. scheidslijn 'Eerder' na de nieuwe artikelen, geen telling erboven", page.locator(".since-head").count() == 0
          and page.locator(".since-line").count() == 1 and pos == n_new, f"{n_new} vs {pos}")
    check("   gelezen kaart gedimd met vinkje", page.locator(f'.card.read[data-id="{by_added[0]["id"]}"] .read-tick').count() == 1)
    page.click(f'.card[data-id="{by_added[0]["id"]}"]')
    page.wait_for_selector("#reader article.full")
    check("   geen 'Volgende' onder een artikel", page.locator("#reader .next-link").count() == 0)
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")
    check("   geen puntje op het tabblad Verdieping", "has-dot" not in (page.locator('#seg-view button[data-v="verdieping"]').get_attribute("class") or ""))
    page.evaluate("localStorage.removeItem('radar:read'); localStorage.removeItem('radar:lastVisit')")

    # 17. Gelezen en Jouw week
    check("17. Jouw week staat bovenaan Actueel", page.locator('a.fb-send[href="#week"]').count() == 1)
    page.click("#week-bar .week-x")
    page.wait_for_timeout(400)
    check("   × veegt Jouw week weg", page.locator("#week-bar").count() == 0 and page.url.endswith("index.html"))
    page.evaluate("location.reload()")
    page.wait_for_selector(".card")
    check("   en blijft weg na opnieuw openen", page.locator("#week-bar").count() == 0)
    page.evaluate("localStorage.removeItem('radar:weekGone')")
    page.evaluate("location.reload()")
    page.wait_for_selector("#week-bar")
    rid = arts[3]["id"]
    page.evaluate("localStorage.removeItem('radar:read')")
    page.goto(url + "#a-" + rid)
    page.wait_for_selector("#reader .read-end", state="attached")
    page.locator("#reader .read-end").scroll_into_view_if_needed()
    page.wait_for_timeout(700)
    check("   artikel tot onderaan gelezen telt als gelezen", page.evaluate(f"!!JSON.parse(localStorage.getItem('radar:read')||'{{}}')['a-{rid}']"))
    page.goto(url + "#week")
    page.wait_for_selector(".wk-list")
    wk = page.locator("#reader").inner_text()
    check("   Jouw week toont hoogtepunten, focus en leerweek", page.locator(".wk-list > li").count() == 2
          and "Deze week proberen" in wk and "Jouw leerweek" in wk and "Gelezen: 1 artikel" in wk, wk[:200])
    check("   hoogtepunt linkt naar zijn artikelen", page.locator(".wk-links a").count() == 3)
    check("   herinnering voor de back-up in Jouw week", "Nog geen back-up gemaakt" in page.locator("#bk-remind").inner_text())
    sh = unquote(page.locator("#reader #fb-send").get_attribute("href") or "")
    check("   gelezen gaat mee met de feedback", f'"reads":["{rid}"]' in sh and "1 gelezen" in sh, sh[-120:])
    page.click("#reader #fb-send")
    page.wait_for_timeout(500)
    check("   na versturen geen verstuurknop meer", page.locator("#reader #fb-send").count() == 0)
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")

    # 18. Begrippen
    page.goto(url + "#a-" + _ta["id"])
    page.wait_for_selector("#reader .story")
    check("18. begrip onderstreept in het verhaal", page.locator("#reader .story .term").count() == 1)
    check("   nieuw begrip is oranje", page.locator("#reader .story .term.new").count() == 1)
    page.locator("#reader .story .term").click()
    check("   na aantikken niet meer oranje", page.locator("#reader .story .term.new").count() == 0 and page.locator("#reader .story .term").count() == 1)
    check("   tik toont de uitleg", page.locator("#term-sheet").is_visible() and "Testuitleg" in page.locator("#term-sheet").inner_text())
    page.locator("#reader h1").click()
    check("   tik ernaast sluit de uitleg", not page.locator("#term-sheet").is_visible())
    page.locator("#reader .story .term").click()
    page.click("#term-sheet a")
    page.wait_for_selector("#reader .gl-item")
    check("   Alle begrippen opent de woordenlijst als pagina", page.locator("#reader .gl-item").count() == 2 and "Begrippen" in page.locator("#reader h1").inner_text())
    page.fill("#reader #gl-q", "zzz")
    check("   zoeken filtert de begrippen", page.locator("#reader .gl-item:not([hidden])").count() == 1)
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")
    check("   geen tabje Begrippen meer", "Begrippen" not in page.locator("#seg-dd").inner_text())
    page.click("#btn-menu")
    check("   tandwiel opent menu met Mijn interesses, Begrippen en Status", page.locator("#menu-sheet").is_visible()
          and [t.split("\n")[0] for t in page.locator("#menu-sheet a").all_inner_texts()] == ["Mijn interesses", "Begrippen", "Back-up", "Status"])
    page.click('#menu-sheet a[href="#begrippen"]')
    page.wait_for_selector("#reader .gl-item")
    check("   menu > Begrippen opent de woordenlijst, menu dicht", page.locator("#reader .gl-item").count() == 2 and not page.locator("#menu-sheet").is_visible())
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    page.click("#btn-menu")
    page.mouse.click(200, 500)
    check("   tik buiten het menu sluit het", not page.locator("#menu-sheet").is_visible())
    page.evaluate("localStorage.setItem('radar:view','actueel'); localStorage.setItem('radar:ddTab','alle')")
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")

    # 19. Later bekijken en Jouw lijst
    lid = arts[4]["id"]
    page.goto(url + "#a-" + lid)
    page.wait_for_selector('#later [data-later="open"]')
    page.click('#later [data-later="open"]')
    page.fill("#later-t", "dbt project evaluator")
    page.fill("#later-n", "Past dit bij onze silver-laag?")
    page.click('#later [data-later="save"]')
    check("19. Later bekijken zet het op je lijst", "staat op je lijst" in page.locator("#later").inner_text())
    page.click('#later a[href="#lijst"]')
    page.wait_for_selector(".later-item")
    item = page.locator(".later-item").inner_text()
    check("   lijst staat op het tabje Later, met notitie en bron", "dbt project evaluator" in item and "silver-laag" in item and "Gezien in" in item
          and page.locator('#seg-dd button[aria-pressed="true"]').inner_text() == "Later" and page.locator(".card.opt").count() == 0)
    href = unquote(page.locator("[data-later-pick]").get_attribute("href") or "")
    check("   verdieping maken opent een issue 'Verdieping: eigen-...'", "title=Verdieping: eigen-dbt-project-evaluator" in href and "Onderwerp: dbt project evaluator" in href
          and "Notitie: Past dit bij onze silver-laag?" in href, href[:160])
    page.click("[data-later-done]")
    check("   Klaar haalt het van de lijst", page.locator(".later-item").count() == 0 and "Nog niets bewaard" in page.locator("#content").inner_text())
    page.evaluate("localStorage.setItem('radar:view','actueel'); localStorage.setItem('radar:ddTab','alle')")
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")

    # 21. Mijn interesses
    check("21. puntje op het tandwiel bij nieuwe voorstellen", "has-dot" in (page.locator("#btn-menu").get_attribute("class") or ""))
    page.click("#btn-menu")
    page.click('#menu-sheet a[href="#interesses"]')
    page.wait_for_selector("#reader .int-topic")
    txt = page.locator("#reader").inner_text()
    check("   pagina toont voorstellen, onderwerpen per gebied, uitsluitingen en logboek", page.locator(".int-sugg").count() == 2
          and page.locator(".int-topic").count() == len(feed["interests"]["topics"]) and "Wat je niet wilt zien" in txt and "Test-wijziging" in txt
          and "30%" in txt)
    page.click('.int-sugg[data-sugg="data-contracts"] [data-int-ans="ja"]')
    page.click('.int-topic[data-topic="open_source_tools"] [data-int-chg="minder"]')
    page.click('.int-topic[data-topic="sql_spark_sql"] [data-int-learn]')
    check("   lampje aanzetten markeert het onderwerp als leeronderwerp", page.locator('.int-topic[data-topic="sql_spark_sql"] .row1 .int-lamp').count() == 1
          and "wordt leeronderwerp" in page.locator('.int-topic[data-topic="sql_spark_sql"]').inner_text())
    page.fill("#int-note", "Meer over Fabric")
    check("   op de pagina zelf alleen een verwijzing naar Actueel", page.locator("#int-to-send").count() == 1 and "Actueel" in page.locator("#int-to-send").inner_text())
    page.click("#int-to-send")
    page.wait_for_selector("#reader", state="hidden")
    sh = unquote(page.locator("#content #fb-send").get_attribute("href") or "")
    check("   één verstuurbalk op Actueel, met de interesses erin", "title=Feedback: 4 wijzigingen in je interesses" in sh and '"interests":' in sh
          and '{"topic":"sql_spark_sql","c":"leren"}' in sh and '{"id":"data-contracts","a":"ja"}' in sh
          and '{"topic":"open_source_tools","c":"minder"}' in sh and '"note":"Meer over Fabric"' in sh, sh[-220:])
    page.click("#content #fb-send")
    page.wait_for_timeout(500)
    page.goto(url + "#interesses")
    page.wait_for_selector("#reader .int-topic")
    check("   na versturen: niets meer klaar, voorstel op 'verstuurd'", page.locator("#int-to-send").count() == 0 and "Verstuurd: ja" in page.locator('.int-sugg[data-sugg="data-contracts"]').inner_text())
    page.click('.int-sugg[data-sugg="powerbi-omhoog"] [data-int-ans="nee"]')
    page.click("#back")
    page.wait_for_selector("#reader", state="hidden")
    check("   puntje weg als alle voorstellen beantwoord zijn", "has-dot" not in (page.locator("#btn-menu").get_attribute("class") or ""))
    page.evaluate("localStorage.removeItem('radar:int')")
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
    page.goto(url)
    page.wait_for_selector(".card")

    # 11. Tabblad Verdieping
    check("11. tabbladen Actueel, Verdieping en Leren", page.locator("#seg-view button").all_inner_texts() == ["Actueel", "Verdieping", "Leren"])
    page.click('#seg-view button[data-v="verdieping"]')
    page.wait_for_timeout(100)
    check("   Verdieping toont alleen verdiepingen", page.locator(".card[data-dd]").count() == len(dds) and page.locator(".card[data-id]").count() == 0)
    check("12. subtabjes Verdiepingen en Morgen", page.locator("#seg-dd button").all_inner_texts() == ["Verdiepingen", "Morgen", "Later"] and page.locator("#seg-dd").is_visible())
    ids = page.eval_on_selector_all(".card[data-dd]", "els => els.map(e => e.dataset.dd)")
    check("   verdiepingen op datum, nieuwste eerst", ids == [d["id"] for d in sorted(dds, key=lambda d: d["written_at"], reverse=True)])
    check("   geen keuzes op het tabje Verdiepingen", page.locator(".card.opt").count() == 0)
    check("   eigen voorstel herkenbaar aan 'jouw voorstel'", page.locator(".card[data-dd] .pill.eigen").count() == 1
          and page.locator('.card[data-dd="eigen-test-voorstel"] .pill.eigen').count() == 1)
    page.click('#seg-dd button[data-v="morgen"]')
    check("   tabje Morgen toont vijf keuzes", page.locator("a.card.opt").count() == 5 and page.locator(".card[data-dd]").count() == 0)
    href = page.locator("a.card.opt").first.get_attribute("href")
    check("   keuze opent een GitHub-issue met de juiste titel",
          href.startswith("https://github.com/tomasr91/data-ai-radar/issues/new?title=") and f"Verdieping%3A%20{opts[0]['id']}" in href, href[:120])
    # Eigen voorstel ingediend (Later): de 5 keuzes blijven staan, met een regel "Ook morgen"
    GH["issues"] = json.dumps([{"number": 9, "title": "Verdieping: eigen-dbt-project-evaluator", "user": {"login": "tomasr91"}}])
    page.evaluate("document.dispatchEvent(new Event('visibilitychange'))")
    page.wait_for_selector(".own-next", timeout=3000)
    check("   eigen voorstel laat de 5 keuzes staan, met 'Ook morgen'", page.locator("a.card.opt").count() == 5
          and "dbt project evaluator" in page.locator(".own-next").inner_text())
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
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
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
    q_top = fr.locator(".pbar").bounding_box()["y"]
    bar = page.evaluate("document.querySelector('.filters').getBoundingClientRect().bottom")
    check("   volgende vraag: voortgangsbolletjes en vraag direct onder de tabbalk", 0 <= q_top - bar <= 20 and fr.locator(".dots").is_visible(), f"bolletjes {q_top}, tabbalk {bar}")
    for i in range(fr.locator(".q .opt").count()):
        if fr.locator('[data-act="check"]').is_enabled():
            break
        fr.locator(".q .opt").nth(i).click()
    fr.locator('[data-act="check"]').click()
    fr.locator(".verdict-line").first.wait_for(timeout=5000)
    saved = page.evaluate("JSON.parse(localStorage.getItem('cca-academy-v2') || 'null')")
    n = sum(c["total"]["n"] for c in saved["certs"].values()) if saved else 0
    check("   vraag beantwoorden werkt en wordt bewaard", n >= 1, str(n))
    fr.locator('[data-act="report"]').first.click()
    fr.locator("#reportBox").fill("Testmelding")
    page.evaluate("() => { const w = document.getElementById('leren-frame').contentWindow; w.__o = []; w.open = (u) => { w.__o.push(u); return null; }; }")
    fr.locator('[data-act="sendreport"]').first.click()
    opened = page.evaluate("document.getElementById('leren-frame').contentWindow.__o")
    check("   melding opent een GitHub-issue 'Examenmelding'", len(opened) == 1 and "issues/new?title=Examenmelding" in opened[0], str(opened)[:120])
    fr.locator('[data-act="home"]').first.click()
    check("   geen eigen back-upblok meer in Leren", fr.locator('[data-act="download"]').count() == 0)
    # Back-up in de Radar (tandwiel > Back-up): bewaart Radar én examen, en zet het terug
    page.evaluate("localStorage.setItem('radar:later', JSON.stringify([{id:'eigen-x',title:'X'}]))")
    page.goto(url + "#backup")
    page.wait_for_selector("#bk-save")
    check("   back-up toont wat er op dit toestel staat", "1 onderwerpen" in page.locator("#reader .bk-list").inner_text()
          and "vragen geoefend" in page.locator("#reader .bk-list").inner_text())
    page.wait_for_function("document.getElementById('bk-persist').textContent.length > 0", timeout=3000)
    check("   back-up laat zien of de opslag blijvend is", "blijvend" in page.locator("#bk-persist").inner_text())
    with page.expect_download(timeout=5000) as dl:
        page.click("#bk-save")
    d = dl.value
    bk = Path(d.path()).read_text(encoding="utf-8")
    check("   Bewaren zet één bestand met Radar en examen in Downloads", d.suggested_filename.startswith("radar-backup-")
          and '"data-ai-radar-backup"' in bk and "cca-academy-v2" in bk and "radar:later" in bk, d.suggested_filename)
    page.evaluate("localStorage.removeItem('radar:later'); localStorage.removeItem('cca-academy-v2')")
    page.set_input_files("#bk-file", d.path())
    page.wait_for_selector("#bk-restore")
    page.click("#bk-restore")
    page.wait_for_selector("#seg-view")
    page.wait_for_timeout(500)
    check("   Terugzetten zet alles terug", page.evaluate("!!localStorage.getItem('cca-academy-v2') && JSON.parse(localStorage.getItem('radar:later')).length === 1"))
    page.evaluate("localStorage.removeItem('cca-academy-v2')")
    page.reload(); page.wait_for_selector("#seg-view"); page.click('#seg-view button[data-v="leren"]'); page.wait_for_selector("#leren-frame")
    check("   regel 'Nieuwe artikelen' alleen bij Actueel", not page.locator("#upd").is_visible())
    page.click('#seg-view button[data-v="actueel"]')
    y_a = page.evaluate("document.querySelector('svg.mark').getBoundingClientRect().y")
    page.click('#seg-view button[data-v="verdieping"]')
    y_v = page.evaluate("document.querySelector('svg.mark').getBoundingClientRect().y")
    check("   logo verspringt niet bij wisselen van tabblad", abs(y_a - y_v) < 0.5, f"{y_a} vs {y_v}")
    page.click('#seg-view button[data-v="leren"]')
    page.wait_for_timeout(300)
    check("   Actueel en Verdieping verborgen, filters weg", not page.locator("#main").is_visible() and not page.locator("#seg-sort").is_visible() and not page.locator("#seg-dd").is_visible())
    bg = page.evaluate("getComputedStyle(document.getElementById('leren-frame').contentDocument.body).backgroundColor")
    check("   examen in het donkere Radar-thema", bg == "rgb(15, 18, 23)", bg)
    h = page.evaluate("document.getElementById('leren-frame').getBoundingClientRect().height")
    check("   venster groeit mee met de inhoud", h > 500, str(h))
    home = fr.locator("#app").inner_text()
    check("   rustig startscherm: geen uitleg, titel of opslagmelding", all(x not in home for x in ["Hoe werkt het herhalen", "Gebaseerd op", "Claude Certification Academy", "Rondes van 10"]) and "Begin met oefenen" in home and "Back-up" not in home)
    page.click('#seg-view button[data-v="actueel"]')
    check("   terug naar Actueel werkt", page.locator(".card[data-id]").count() == len(arts) and page.locator("#leren").is_hidden())
    page.click('#seg-view button[data-v="leren"]')
    check("   examen blijft geladen bij terugkeren", page.locator("#leren-frame").count() == 1 and page.locator("#leren").is_visible())
    page.click('#seg-view button[data-v="actueel"]')

    # 7. Status (was Feedcontrole): één statusregel, alleen probleembronnen, net niet in de feed, alle bronnen ingeklapt
    page.goto(url + "#feedcontrole")
    page.wait_for_selector("#reader #run-status")
    st = page.locator("#run-status").inner_text()
    check("7. status toont de nachtrun in één regel", ("Laatste nachtrun" in st or "niet bijgewerkt" in st or "mislukt" in st), st)
    check("   status per nachttaak", page.locator("#reader .runs li").count() == 3 and "12 artikelen uitgelegd" in page.locator("#reader .runs").inner_text()
          and page.locator("#reader .runs li.deels").count() == 1 and "niet gedraaid" in page.locator("#reader .runs").inner_text())
    check("   alle bronnen ingeklapt, met status", page.locator("#reader details.all-src li").count() == len(feed["sources"])
          and not page.locator("#reader details.all-src li").first.is_visible())
    failed = [s for s in feed["sources"] if s["status"] == "failed"]
    check("7. mislukte bronnen zichtbaar, rest geladen", (not failed or "Bronnen met een probleem" in page.locator("#reader").inner_text()) and len(arts) > 0)
    check("   geen technische blokken meer", all(x not in page.locator("#reader").inner_text() for x in ["dubbel samengevoegd", "API-sleutel", "Verdeling over onderwerpen"]))
    if SHOTS:
        page.screenshot(path=str(SHOTS / "3-feedcontrole.png"))

    # 8. Mobiel: geen horizontaal scrollen
    page.evaluate("(() => { try { sessionStorage.clear(); } catch (e) {} })()")
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

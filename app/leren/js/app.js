/* Academy UI: rustig oefenen. Startscherm met één knop ("Verder oefenen"), rondes van 10 vragen,
   herkansing van wat nog niet lukte, en af en toe een mijlpaal. Geen dagdoelen of reeksen. */
(function () {
  const A = window.Academy, C = A.core;
  const app = document.getElementById("app");
  const esc = s => String(s == null ? "" : s).replace(/[&<>"']/g, ch => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" })[ch]);
  const LETTERS = "ABCDEFGH";
  const ROUND = 10;
  const fmtW = w => (Number.isInteger(w) ? w : w.toFixed(1).replace(".", ",")) + "%";
  const pct = x => Math.round(x * 100) + "%";
  const SHORT = { ccaof: "Associate", ccdvf: "Developer", ccarf: "Architect F", ccarp: "Architect P" };

  const ui = { view: "home", scope: null, cur: null, recent: [], round: [], retry: null, retryDone: null, roundMs: [], curMs: [], allWhy: false, pickOpen: false,
    open: {}, confirm: null, importText: "", importMsg: null, exportOpen: false, reportOpen: false, reportText: "", reportDone: null, explain: false };

  const cert = () => C.cert();
  const meter = (done, seen, label) => `<div class="meter" role="img" aria-label="${esc(label)}"><span class="m" style="width:${done * 100}%"></span><span class="s" style="width:${Math.max(0, seen - done) * 100}%"></span></div>`;
  const statMeter = s => meter(s.total ? s.mastered / s.total : 0, s.total ? s.seen / s.total : 0, s.mastered + " van " + s.total + " beheerst");
  const scopeLabel = sc => {
    const c = cert();
    if (!sc || sc.kind === "all") return "Alle onderwerpen";
    if (sc.kind === "weak") return "Verder oefenen";
    if (sc.kind === "hard") return "Lastige vragen";
    if (sc.kind === "domain") { const d = c.domains.find(x => x.id === sc.id); return "D" + d.n + " · " + (d.nl || d.name); }
    const s = C.subMap(c)[sc.id]; return s.nl || s.en;
  };
  const msText = m => m.kind === "sub" ? `${esc(m.sub.nl || m.sub.en)}: alle vragen beheerst`
    : m.kind === "dom" ? `Domein ${m.domain.n} (${esc(m.domain.nl || m.domain.name)}) helemaal beheerst`
    : `${m.pct}% van de examenstof beheerst`;
  const learningCount = () => cert().questions.filter(q => C.inLearning(C.cs().q[q.id])).length;

  /* ---------------- kop ---------------- */
  function head() {
    // In de Radar: alleen de keuze van de certificering (zonder titel, opslagmelding of nog lege certificeringen).
    const ids = A.order.filter(id => A.certs[id].questions.length);
    if (ids.length && !ids.includes(C.state.activeCert)) C.state.activeCert = ids[0];
    return ids.length > 1 ? `<nav class="certs" aria-label="Certificering">${ids.map(id => { const c = A.certs[id]; return `<button class="cert" data-act="cert" data-id="${id}" aria-pressed="${id === C.state.activeCert}">${SHORT[id] || c.short}</button>`; }).join("")}</nav>` : "";
  }

  /* ---------------- startscherm ---------------- */
  function vHome() {
    const c = cert(), ex = c.exam || {};
    const facts = [c.code, ex.items && ex.items + " vragen", ex.minutes && ex.minutes + " min", ex.cut && "slaaggrens " + ex.cut + " (schaalscore)"].filter(Boolean).join(" · ");
    let body;
    if (!c.questions.length) {
      body = `<div class="notice">De oefenvragen voor deze certificering zijn nog niet gemaakt. Hieronder staan de onderwerpen uit de officiële examengids, zodat je ziet wat er getoetst wordt.</div>
        <div class="card"><div class="topics">${c.domains.map(d => `<div class="topic"><div class="trow"><span class="n">D${d.n}</span><span class="nm"><b>${esc(d.name)}</b><span>${d.subs.length} onderwerpen</span></span><span class="cnt">${fmtW(d.weight)}</span></div></div>`).join("")}</div></div>`;
    } else {
      if (ui.ready) C.newMilestones(); // legt bij de eerste keer al behaalde mijlpalen stil vast
      const r = C.readiness(), all = C.stats(null, { kind: "all" }), last = C.lastMilestone(), hard = C.hardCount(), learning = learningCount();
      body = `<div class="card start">
          <div class="ready"><span class="big">${pct(r)}</span><span>van de examenstof beheerst</span></div>
          ${meter(r, all.total ? all.seen / all.total : 0, pct(r) + " van de examenstof beheerst")}
          ${last ? `<p class="small ms-line">✓ ${msText(last)}</p>` : ""}
          <button class="btn primary wide" data-act="start" data-kind="weak">${all.seen ? "Verder oefenen" : "Begin met oefenen"}</button>
        </div>
        <details class="pick" ${ui.pickOpen ? "open" : ""}><summary>Kies zelf wat je oefent</summary>
          <div class="card"><div class="topics">
            <button class="srow top-row" data-act="start" data-kind="all"><span><b>Alle onderwerpen gemengd</b><br><span class="small muted">volgens de examenweging</span></span><span class="cnt">${all.mastered}/${all.total}</span></button>
            ${hard ? `<button class="srow top-row" data-act="start" data-kind="hard"><span><b>Lastige vragen</b><br><span class="small muted">vaker fout, gegokt of nog in de leerfase</span></span><span class="cnt">${hard}</span></button>` : ""}
            ${c.domains.map(d => { const s = C.stats(null, { kind: "domain", id: d.id }); const open = ui.open[d.id];
              return `<div class="topic"><div class="trow"><span class="n">D${d.n}</span>
                <button class="nm" data-act="start" data-kind="domain" data-id="${d.id}"><b>${esc(d.name)}</b><span>${esc(d.nl || "")} · weging ${fmtW(d.weight)}</span></button>
                <span class="cnt">${s.mastered}/${s.total}</span>${statMeter(s)}
                <button class="toggle" data-act="toggle" data-id="${d.id}" aria-expanded="${!!open}">${open ? "▾ Verberg subonderwerpen" : "▸ " + d.subs.length + " subonderwerpen"}</button></div>
                ${open ? `<div class="subs">${d.subs.map(sb => { const x = C.stats(null, { kind: "sub", id: sb.id }); return `<button class="srow" data-act="start" data-kind="sub" data-id="${sb.id}"><span>${esc(sb.nl || sb.en)}</span><span class="cnt">${x.mastered}/${x.total}</span></button>`; }).join("")}</div>` : ""}</div>`; }).join("")}
          </div></div></details>`;
    }
    return `${head()}
      ${body}
      ${foot(c)}`;
  }
  function foot(c) {
    const m = C.store.mode, dl = !!C.store.downloads;
    const src = (c.sources || [])[0];
    return `<div class="foot">
      <details class="more"><summary>Back-up van je voortgang</summary>
        <div class="card">
          <p class="small">${m === "account" ? "Je voortgang staat privé in je Claude-account en als kopie in deze browser." : m === "browser" ? "Je voortgang staat op dit toestel, in de Radar-app. Maak af en toe een export als back-up." : "Opslaan is hier niet mogelijk; maak een export voordat je de pagina sluit."}</p>
          <div class="row"><button class="btn sm" data-act="export">${ui.exportOpen ? "Verberg export" : "Exporteer voortgang"}</button>${ui.exportOpen ? `<button class="btn sm" data-act="copy">Kopieer</button>${dl ? `<button class="btn sm" data-act="download">Opslaan als bestand</button>` : ""}` : ""}</div>
          ${ui.exportOpen ? `<textarea class="input" id="exportBox" readonly>${esc(C.exportJSON())}</textarea>` : ""}
          <label class="small" for="importBox">Importeer een eerdere export (vervangt je huidige voortgang)</label>
          <textarea class="input" id="importBox" placeholder="Plak hier je export…">${esc(ui.importText)}</textarea>
          <div class="row"><label class="btn sm" for="importFile">Kies bestand…</label><input type="file" id="importFile" accept=".json,application/json,text/plain" hidden><button class="btn sm" data-act="confirm" data-what="import" ${ui.importText.trim() ? "" : "disabled"}>Importeer</button>
            ${c.questions.length ? `<button class="btn sm danger" data-act="confirm" data-what="reset">Wis voortgang ${esc(SHORT[c.id] || "")}</button>` : ""}</div>
          ${ui.confirm === "import" ? `<div class="confirm"><b>Je huidige voortgang wordt vervangen.</b><div class="row"><button class="btn sm danger" data-act="doimport">Vervang</button><button class="btn sm" data-act="cancel">Annuleer</button></div></div>` : ""}
          ${ui.confirm === "reset" ? `<div class="confirm"><b>Alle voortgang voor ${esc(c.short)} wissen? Dit kan niet ongedaan worden gemaakt.</b><div class="row"><button class="btn sm danger" data-act="doreset">Wis</button><button class="btn sm" data-act="cancel">Annuleer</button></div></div>` : ""}
          ${ui.importMsg ? `<div class="notice ${ui.importMsg.ok ? "good" : "bad"}">${esc(ui.importMsg.text)}</div>` : ""}
        </div></details></div>`;
  }

  /* ---------------- oefenen ---------------- */
  function setCurrent(q) {
    const prev = C.cs().q[q.id];
    ui.cur = { qid: q.id, order: C.shuffle(q.o.map((_, i) => i)), sel: [], checked: false, ok: null, guess: false,
      status: !prev ? "new" : C.inLearning(prev) || prev.g ? "again" : "", newSub: C.stats(null, { kind: "sub", id: q.s }).seen === 0 };
    ui.reportOpen = false; ui.reportDone = null; ui.reportText = ""; ui.explain = false; ui.explainAbove = false; ui.allWhy = false; ui.curMs = [];
  }
  function newQuestion() {
    if (ui.retry) { setCurrent(C.qmap(cert())[ui.retry.queue[ui.retry.i]]); return; }
    const q = C.next(null, ui.scope, ui.recent);
    if (!q) { ui.cur = null; return; }
    setCurrent(q);
    ui.recent.push(q.id); if (ui.recent.length > ROUND) ui.recent.shift();
  }
  // Vragen uit deze ronde waarvan de laatste poging nog niet lukte (fout of gegokt).
  function retryList() {
    const last = {}; ui.round.forEach(it => last[it.qid] = it);
    return Object.values(last).filter(it => !it.ok || it.guess).map(it => it.qid);
  }
  function dots() {
    if (ui.retry) return `<span class="where">Herkansing ${Math.min(ui.retry.i + 1, ui.retry.queue.length)} van ${ui.retry.queue.length}</span>`;
    const items = ui.round, curIdx = ui.cur && !ui.cur.checked ? items.length : -1;
    return `<span class="dots" role="img" aria-label="Vraag ${Math.min(items.length + (curIdx >= 0 ? 1 : 0), ROUND)} van ${ROUND} in deze ronde">${Array.from({ length: ROUND }, (_, i) => {
      const it = items[i]; return `<i class="${it ? (it.ok && !it.guess ? "ok" : "no") : i === curIdx ? "cur" : ""}"></i>`; }).join("")}</span>`;
  }
  function vPractice() {
    const c = cert(), cur = ui.cur;
    if (!cur) return `${head()}<div class="card"><p>Geen vragen gevonden voor dit onderwerp.</p><button class="btn" data-act="home">Terug</button></div>`;
    const q = C.qmap(c)[cur.qid], sb = C.subMap(c)[q.s], d = sb.domain, multi = q.t === "m", need = q.a.length;
    const opts = cur.order.map((oi, pos) => {
      const sel = cur.sel.includes(oi), right = q.a.includes(oi);
      if (cur.checked) {
        const cls = right && sel ? "right" : right ? "missed" : sel ? "wrong" : "";
        const mk = right && sel ? "✓" : right ? "○" : sel ? "✗" : "";
        const v = right && sel ? "Juist" : right ? "Juist antwoord" : sel ? "Jouw keuze" : "";
        const showWhy = right || sel || ui.allWhy;
        // Radar: na controleren blijft het scherm gelijk; alleen goed/fout op de opties. De uitleg staat onder de knop.
        return `<div class="opt ${cls}"><span class="mk">${mk}</span><span><span class="key">${LETTERS[pos]}</span>${q.o[oi]}</span></div>`;
      }
      const dis = !sel && multi && cur.sel.length >= need;
      return `<label class="opt ${sel ? "sel" : ""}"><input type="${multi ? "checkbox" : "radio"}" name="opt" data-opt="${oi}" ${sel ? "checked" : ""} ${dis ? "disabled" : ""}><span><span class="key">${LETTERS[pos]}</span>${q.o[oi]}</span></label>`;
    }).join("");
    const mod = c.modules && c.modules[d.id], sec = mod && mod.sections.find(x => x.sub === q.s);
    // Radar: uitleg die vóór het antwoorden is geopend, blijft na controleren boven de vraag staan (scherm verspringt niet).
    const above = ui.explain && sec && (!cur.checked || ui.explainAbove);
    const explainHtml = sec ? `<div class="explain${above ? " pre" : ""}"><div class="spread"><span class="eyebrow">Uitleg · ${esc(sec.title)}</span>${above ? `<button class="linkbtn" data-act="explain">Verberg</button>` : ""}</div><div class="prose">${sec.body}</div></div>` : "";
    const lastOfRound = !ui.retry && ui.round.length >= ROUND, lastOfRetry = ui.retry && ui.retry.i >= ui.retry.queue.length - 1;
    const retryN = lastOfRound ? retryList().length : 0;
    const nextLabel = lastOfRound ? (retryN ? `Herkansing (${retryN}) →` : "Bekijk ronde →") : lastOfRetry ? "Bekijk ronde →" : "Volgende vraag →";
    const partial = multi && cur.sel.some(i => q.a.includes(i));
    const banner = cur.ok && cur.guess ? ["guess", "Goed gegokt. Hij komt nog even terug, zodat je hem echt leert."]
      : cur.ok ? ["ok", "Goed."]
      : ["no", (partial ? "Bijna: kies precies alle juiste opties. " : "Nog niet. ") + "Deze vraag komt over een paar vragen terug."];
    const hiddenWhy = q.o.some((_, i) => !q.a.includes(i) && !cur.sel.includes(i));
    const whyList = cur.checked ? cur.order.map((oi, pos) => {
      const show = q.a.includes(oi) || cur.sel.includes(oi) || ui.allWhy;
      const w = String(q.w[oi] || "").trim();
      return show && w && !/^Juist\.?$/.test(w) ? `<li><span class="key">${LETTERS[pos]}</span> ${q.w[oi]}</li>` : "";
    }).join("") : "";
    return `${head()}
      <div class="pbar"><button class="btn ghost" data-act="home">← Stoppen</button>${dots()}</div>
      ${ui.retry && ui.retry.i === 0 && !cur.checked ? `<div class="notice">Herkansing: de vragen uit deze ronde die nog niet lukten, nog één keer.</div>` : ""}
      <div class="q">
        <div class="qmeta"><span>D${d.n} · ${esc(sb.nl || sb.en)}</span>${multi ? '<span class="pill multi">Meerdere antwoorden</span>' : ""}${cur.status === "new" ? '<span class="pill new">Nieuw</span>' : cur.status === "again" ? '<span class="pill again">Herhaling</span>' : ""}${sec && cur.newSub ? `<button class="linkbtn" data-act="explain">${ui.explain ? "Verberg uitleg" : "Nieuw onderwerp: lees de uitleg"}</button>` : ""}</div>

        ${above ? explainHtml : ""}
        <div class="qtext">${q.q}</div>
        <div class="instr">${multi ? `Kies ${need} antwoorden.` : "Kies één antwoord."}${!cur.checked && multi ? ` <span class="muted" style="font-weight:500">(${cur.sel.length}/${need})</span>` : ""}</div>
        <div class="opts" role="${multi ? "group" : "radiogroup"}">${opts}</div>
        <div class="actions">
          ${cur.checked ? `<span class="verdict-line ${banner[0]}">${cur.ok ? (cur.guess ? "✓ Goed gegokt" : "✓ Goed") : partial ? "✗ Bijna" : "✗ Fout"}</span><button class="btn primary" data-act="next">${nextLabel}</button>`
            : `<span class="hint"><kbd>1</kbd>–<kbd>${q.o.length}</kbd> kiezen · <kbd>G</kbd> gok · <kbd>Enter</kbd> controleren</span><div class="right-actions">${sec && !cur.newSub ? `<button class="linkbtn" data-act="explain">${ui.explain ? "Verberg uitleg" : "Uitleg"}</button>` : ""}<button class="btn guessbtn" data-act="guess" aria-pressed="${cur.guess}" title="Weet je het niet zeker? Dan telt een goed antwoord niet als beheerst.">Ik gok</button><button class="btn primary" data-act="check" ${cur.sel.length === need ? "" : "disabled"}>Controleer</button></div>`}
        </div>
        ${cur.checked ? `<div class="after">
          ${ui.curMs.map(m => `<div class="milestone">✓ Mijlpaal: ${msText(m)}</div>`).join("")}
          ${banner[0] !== "ok" ? `<p class="small muted">${banner[1]}</p>` : ""}
          <div class="lesson"><span class="eyebrow">Kernles</span><span>${esc(q.ex)}</span></div>
          ${whyList ? `<ul class="whylist">${whyList}</ul>` : ""}
          <div class="extras">${!ui.allWhy && hiddenWhy ? `<button class="linkbtn" data-act="allwhy">Uitleg bij alle opties</button>` : ""}${sec ? `<button class="linkbtn" data-act="explain">${ui.explain ? "Verberg uitleg" : "Uitleg over dit onderwerp"}</button>` : ""}<button class="linkbtn" data-act="report">Klopt deze vraag niet?</button></div>
        </div>` : ""}
        ${ui.explain && sec && cur.checked && !above ? explainHtml : ""}
        ${cur.checked && ui.reportOpen ? `<div class="explain"><label class="small" for="reportBox">Wat klopt er niet? Bijvoorbeeld een verouderd feit, een dubbelzinnige vraag of meer dan één goed antwoord.</label>
          <textarea class="input" id="reportBox" style="font-family:var(--display);font-size:0.9rem">${esc(ui.reportText)}</textarea>
          <div class="row"><button class="btn sm" data-act="sendreport" ${ui.reportText.trim() ? "" : "disabled"}>Verstuur melding</button><button class="btn sm ghost" data-act="report">Annuleer</button></div></div>` : ""}
        ${ui.reportDone ? `<div class="notice good">${ui.reportDone}</div>` : ""}
      </div>`;
  }

  /* ---------------- einde van een ronde ---------------- */
  function vRound() {
    const c = cert(), items = ui.round, ok = items.filter(x => x.ok && !x.guess).length;
    const rt = ui.retryDone, learning = learningCount(), r = C.readiness();
    const missed = [], seen = new Set(); items.forEach(x => { if ((!x.ok || x.guess) && !seen.has(x.qid)) { seen.add(x.qid); missed.push(x.qid); } });
    return `${head()}
      <div class="pbar"><button class="btn ghost" data-act="home">← Startscherm</button><span class="where">${esc(scopeLabel(ui.scope))}</span></div>
      <div class="card round">
        <span class="eyebrow">Ronde klaar</span>
        <div class="ready"><span class="big">${ok} van ${items.length}</span><span>meteen goed${rt ? `<br><span class="small muted">herkansing: ${rt.ok} van ${rt.n} goed</span>` : ""}</span></div>
        ${ui.roundMs.length ? `<div class="mslist">${ui.roundMs.map(m => `<div class="milestone">✓ ${msText(m)}</div>`).join("")}</div>` : ""}
        <p class="small">Je beheerst nu ${pct(r)} van de examenstof.${learning ? ` ${learning === 1 ? "Eén vraag komt" : learning + " vragen komen"} vanzelf nog terug tot ${learning === 1 ? "hij goed zit" : "ze goed zitten"}.` : ""}</p>
        ${missed.length ? `<details class="more"><summary>Kernlessen van deze ronde (${missed.length})</summary><div class="rlist">${missed.map(id => { const q = C.qmap(c)[id]; return `<div class="ritem"><div class="qt">${q.q}</div>${q.a.map(i => `<div class="ans">${q.o[i]}</div>`).join("")}<div class="small muted">${esc(q.ex)}</div></div>`; }).join("")}</div></details>` : ""}
        <div class="row"><button class="btn primary" data-act="nextround">Volgende ronde →</button><button class="btn" data-act="home">Klaar voor nu</button></div>
      </div>`;
  }

  /* ---------------- render ---------------- */
  function render() { app.innerHTML = ui.view === "practice" ? vPractice() : ui.view === "round" ? vRound() : vHome(); }
  function setCert(id) {
    C.state.activeCert = id; C.save(); ui.view = "home"; ui.confirm = null; ui.importMsg = null;
    try { history.replaceState(null, "", "#" + id); } catch (e) {}
    render(); toTop();
  }
  function resetRound() { ui.round = []; ui.retry = null; ui.retryDone = null; ui.roundMs = []; }
  function start(kind, id) {
    ui.scope = kind === "all" || kind === "weak" || kind === "hard" ? { kind } : { kind, id };
    ui.recent = []; resetRound();
    newQuestion(); ui.view = "practice"; render(); toTop(".q");
  }
  /* Radar: het examen staat in een venster zonder eigen scrollbalk; de Radar-pagina scrolt.
     Zet het gevraagde blok (bijv. de vraag) zo hoog mogelijk, direct onder de vaste tabbladen van de Radar. */
  function toTop(sel) {
    const el = sel ? document.querySelector(sel) : null;
    try {
      if (window.parent !== window && window.frameElement) {
        const pdoc = window.parent.document, sticky = pdoc.querySelector(".filters");
        // Hoogte van de vaste tabbalk plus waar hij blijft plakken (veilige zone bovenaan het scherm)
        const off = sticky ? sticky.getBoundingClientRect().height + (parseFloat(window.parent.getComputedStyle(sticky).top) || 0) : 0;
        const y = window.frameElement.getBoundingClientRect().top + window.parent.scrollY + (el ? el.getBoundingClientRect().top : 0) - off - 10;
        window.parent.scrollTo(0, Math.max(0, y));
        return;
      }
    } catch (e) { /* ander domein: val terug op gewoon scrollen */ }
    if (el) el.scrollIntoView({ block: "start" }); else window.scrollTo(0, 0);
  }
  function check() {
    const cur = ui.cur; if (!cur || cur.checked) return;
    const q = C.qmap(cert())[cur.qid]; if (cur.sel.length !== q.a.length) return;
    cur.ok = C.answer(null, q, cur.sel, cur.guess); cur.checked = true;
    if (ui.retry) ui.retry.res.push(cur.ok && !cur.guess);
    else ui.round.push({ qid: q.id, ok: cur.ok, guess: cur.guess });
    ui.curMs = C.newMilestones(); ui.roundMs.push(...ui.curMs);
    render();
  }
  function showRound() {
    if (ui.retry) ui.retryDone = { n: ui.retry.queue.length, ok: ui.retry.res.filter(Boolean).length };
    ui.retry = null; ui.view = "round"; ui.cur = null; render(); toTop();
  }
  function next() {
    if (ui.retry) {
      if (ui.retry.i >= ui.retry.queue.length - 1) return showRound();
      ui.retry.i++; newQuestion(); render(); toTop(".q"); return;
    }
    if (ui.round.length >= ROUND) {
      const list = retryList();
      if (list.length) { ui.retry = { queue: C.shuffle(list), i: 0, res: [] }; newQuestion(); render(); toTop(".q"); return; }
      return showRound();
    }
    newQuestion(); render(); toTop(".q");
  }
  function nextRound() { resetRound(); ui.view = "practice"; newQuestion(); render(); toTop(".q"); }
  function flash(text) {
    let t = document.getElementById("toast");
    if (!t) { t = document.createElement("div"); t.id = "toast"; t.setAttribute("role", "status"); t.style.cssText = "position:fixed;left:50%;transform:translateX(-50%);bottom:calc(20px + env(safe-area-inset-bottom,0px));background:var(--ink);color:var(--paper);padding:10px 16px;border-radius:8px;font-size:0.9rem;z-index:40;max-width:calc(100% - 32px)"; document.body.appendChild(t); }
    t.textContent = text; t.hidden = false; clearTimeout(t._h); t._h = setTimeout(() => t.hidden = true, 2400);
  }

  const H = {
    cert: el => setCert(el.dataset.id),
    home: () => { ui.view = "home"; render(); toTop(); },
    start: el => start(el.dataset.kind, el.dataset.id),
    toggle: el => { ui.open[el.dataset.id] = !ui.open[el.dataset.id]; render(); },
    check, next, nextround: nextRound,
    guess: () => { if (ui.cur && !ui.cur.checked) { ui.cur.guess = !ui.cur.guess; render(); } },
    allwhy: () => { ui.allWhy = true; render(); },
    explain: () => { ui.explain = !ui.explain; if (!(ui.cur && ui.cur.checked)) ui.explainAbove = ui.explain; render(); if (ui.explain) { const ex = document.querySelector(".explain"); if (ex && ui.cur && ui.cur.checked) ex.scrollIntoView({ block: "nearest" }); } },
    report: () => { ui.reportOpen = !ui.reportOpen; ui.reportDone = null; render(); if (ui.reportOpen) { const b = document.getElementById("reportBox"); if (b) b.focus(); } },
    sendreport: async () => {
      const q = C.qmap(cert())[ui.cur.qid]; const text = ui.reportText; const where = await C.report(null, q, text);
      ui.reportOpen = false; ui.reportText = "";
      // In de Radar (GitHub Pages) gaat een melding als GitHub-issue naar de repository; de maandcontrole verwerkt die.
      if (where !== "account") { try { window.open(C.reportUrl(q, text), "_blank", "noopener"); } catch (e) {} }
      ui.reportDone = where === "account" ? "Gemeld. Deze melding wordt meegenomen bij de volgende update van de vragenbank."
        : "GitHub opent met je melding; tik daar op <b>Create</b>. De maandcontrole verwerkt hem. De melding staat ook in je export.";
      render();
    },
    export: () => { ui.exportOpen = !ui.exportOpen; render(); },
    copy: () => { const box = document.getElementById("exportBox"); const fb = () => { if (box) { box.focus(); box.select(); } };
      try { navigator.clipboard.writeText(C.exportJSON()).then(() => flash("Gekopieerd."), fb); } catch (e) { fb(); } },
    download: async () => { try { await C.store.downloads.save({ filename: "academy-voortgang-" + new Date().toISOString().slice(0, 10) + ".json", data: C.exportJSON() }); } catch (e) { flash("Opslaan als bestand lukte niet. Gebruik Kopieer."); } },
    confirm: el => { ui.confirm = el.dataset.what; ui.importMsg = null; render(); },
    cancel: () => { ui.confirm = null; render(); },
    doimport: () => { const r = C.importJSON(ui.importText); ui.confirm = null; ui.importMsg = r.ok ? { ok: true, text: "Voortgang geïmporteerd." } : { ok: false, text: r.msg }; if (r.ok) ui.importText = ""; render(); },
    doreset: () => { C.resetCert(C.state.activeCert); ui.confirm = null; render(); flash("Voortgang gewist."); }
  };

  document.addEventListener("click", e => { const el = e.target.closest("[data-act]"); if (!el || el.disabled) return; const h = H[el.dataset.act]; if (h) h(el, e); });
  document.addEventListener("toggle", e => { if (e.target.matches && e.target.matches("details.pick")) ui.pickOpen = e.target.open; }, true);
  document.addEventListener("change", e => {
    const t = e.target;
    if (t.matches("input[data-opt]") && ui.cur && !ui.cur.checked) {
      const q = C.qmap(cert())[ui.cur.qid], oi = +t.dataset.opt;
      if (q.t === "m") { if (t.checked) { if (!ui.cur.sel.includes(oi) && ui.cur.sel.length < q.a.length) ui.cur.sel.push(oi); } else ui.cur.sel = ui.cur.sel.filter(x => x !== oi); }
      else ui.cur.sel = [oi];
      render(); const f = document.querySelector('input[data-opt="' + oi + '"]'); if (f) f.focus();
    }
    if (t.id === "importFile" && t.files && t.files[0]) { const fr = new FileReader(); fr.onload = () => { ui.importText = String(fr.result || ""); ui.importMsg = null; render(); }; fr.readAsText(t.files[0]); }
  });
  document.addEventListener("input", e => {
    const t = e.target;
    if (t.id === "importBox") { ui.importText = t.value; const b = document.querySelector('[data-what="import"]'); if (b) b.disabled = !t.value.trim(); }
    if (t.id === "reportBox") { ui.reportText = t.value; const b = document.querySelector('[data-act="sendreport"]'); if (b) b.disabled = !t.value.trim(); }
  });
  document.addEventListener("keydown", e => {
    if (e.target.matches("textarea, input[type=text], select") || e.metaKey || e.ctrlKey || e.altKey) return;
    if (ui.view === "round" && e.key === "Enter" && !e.target.matches("button, a, summary")) { e.preventDefault(); nextRound(); return; }
    if (ui.view !== "practice" || !ui.cur) return;
    const cur = ui.cur, q = C.qmap(cert())[cur.qid];
    const n = parseInt(e.key, 10);
    if (!cur.checked && n >= 1 && n <= cur.order.length) {
      const oi = cur.order[n - 1];
      if (q.t === "m") { if (cur.sel.includes(oi)) cur.sel = cur.sel.filter(x => x !== oi); else if (cur.sel.length < q.a.length) cur.sel.push(oi); }
      else cur.sel = [oi];
      render();
    } else if (!cur.checked && (e.key === "g" || e.key === "G")) { cur.guess = !cur.guess; render();
    } else if (e.key === "Enter" && !e.target.matches("button, a, summary")) { e.preventDefault(); if (cur.checked) next(); else check(); }
  });

  /* ---------------- start ---------------- */
  // Opslagstatus bijwerken zonder het oefenscherm opnieuw te tekenen (dat zou een half beantwoorde vraag storen).
  C.store.onChange(() => {
    if (ui.view === "home" && !(document.activeElement && document.activeElement.matches("textarea"))) { render(); return; }
    const el = document.querySelector(".save"); if (!el) return;
    const m = C.store.mode; el.className = "save " + m;
    el.lastChild.textContent = m === "account" ? (C.store.error ? "Opslaan mislukt, opnieuw proberen…" : "Opgeslagen in je account") : m === "browser" ? "Opgeslagen op dit toestel" : "Niet opgeslagen";
  });
  let h = ""; try { h = (location.hash || "").slice(1); } catch (e) {}
  if (h && A.certs[h]) C.state.activeCert = h;
  render();
  C.init().then(() => {
    ui.ready = true;
    if (h && A.certs[h]) C.state.activeCert = h;
    if (!A.certs[C.state.activeCert]) C.state.activeCert = "ccaof";
    if (ui.view === "home") render();
  });
})();

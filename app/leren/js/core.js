/* Academy core: opslag, herhaalsysteem en vraagselectie. Geen DOM-code; los van de UI te testen.
   Per certificering een eigen voortgang. Elke vraag zit in een 'bak' (Leitner-systeem):
   goed → een bak hoger en later terug; fout → leerfase (zie hieronder) en snel terug. Beheerst = bak 2 of hoger. */
(function () {
  const A = window.Academy;
  const LS_KEY = "cca-academy-v2", LS_OLD = "cca-academy-state-v1";
  const DAY = 86400000;
  const INTERVAL_DAYS = [0, 1, 3, 7, 16, 35]; // wachttijd per bak
  const MAX_BOX = INTERVAL_DAYS.length - 1, MASTERED = 2;
  const now = () => Date.now();
  const rnd = arr => arr[Math.floor(Math.random() * arr.length)];
  const shuffle = arr => { const a = arr.slice(); for (let i = a.length - 1; i > 0; i--) { const j = Math.floor(Math.random() * (i + 1)); [a[i], a[j]] = [a[j], a[i]]; } return a; };

  /* ---------------- state ---------------- */
  const emptyCert = () => ({ q: {}, total: { n: 0, c: 0 }, reports: [] });
  let state = { v: 2, updatedAt: 0, activeCert: "ccaof", certs: {} };
  const valid = s => s && typeof s === "object" && s.v === 2 && s.certs && typeof s.certs === "object";
  function cs(id) {
    id = id || state.activeCert;
    if (!state.certs[id]) state.certs[id] = emptyCert();
    const c = state.certs[id]; for (const [k, v] of Object.entries(emptyCert())) if (c[k] === undefined) c[k] = v;
    return c;
  }
  // Voortgang uit versie 1 omzetten naar het herhaalsysteem.
  function migrate(old) {
    if (!old || old.v !== 1 || !old.certs) return null;
    const s = { v: 2, updatedAt: old.updatedAt || now(), activeCert: old.activeCert || "ccaof", certs: {} };
    for (const [cid, c] of Object.entries(old.certs)) {
      const n = emptyCert();
      for (const [qid, x] of Object.entries(c.q || {})) {
        const b = x.lastOk ? (x.c >= 2 ? 2 : 1) : 0;
        n.q[qid] = { b, due: (x.last || now()) + INTERVAL_DAYS[b] * DAY, n: x.n || 0, c: x.c || 0, last: x.last || 0, ok: !!x.lastOk };
        n.total.n += x.n || 0; n.total.c += x.c || 0;
      }
      s.certs[cid] = n;
    }
    return s;
  }

  /* ---------------- opslag ----------------
     Browser (localStorage) als snelle kopie; account (db-capability, privé per gebruiker) als bron
     wanneer beschikbaar; export/import als handmatige back-up. */
  const store = { mode: "none", docRef: null, db: null, downloads: null, writing: false, pending: false, timer: null, error: null, listeners: [],
    onChange(f) { this.listeners.push(f); }, emit() { this.listeners.forEach(f => { try { f(); } catch (e) {} }); } };
  const readJSON = k => { try { const r = localStorage.getItem(k); return r ? JSON.parse(r) : null; } catch (e) { return null; } };
  const writeLocal = () => { try { localStorage.setItem(LS_KEY, JSON.stringify(state)); return true; } catch (e) { return false; } };

  function parsePayload(data) {
    if (!data || typeof data.payload !== "string") return null;
    try { const s = JSON.parse(data.payload); return valid(s) ? s : migrate(s); } catch (e) { return null; }
  }
  async function init() {
    const local = readJSON(LS_KEY);
    if (valid(local)) state = local; else { const m = migrate(readJSON(LS_OLD)); if (m) state = m; }
    store.mode = writeLocal() ? "browser" : "none"; store.emit();
    try {
      if (!window.claude || typeof window.claude.use !== "function") return;
      const [db, user, downloads] = await Promise.all([window.claude.use("db"), window.claude.use("user"), window.claude.use("downloads")]);
      store.downloads = downloads;
      if (!db || !user) { store.emit(); return; }
      const uid = await user.id(); if (!uid) { store.emit(); return; }
      store.db = db; store.docRef = db.doc("data/users/" + uid + "/academy");
      const snap = await store.docRef.get();
      const remote = snap && snap.exists ? parsePayload(snap.data()) : null;
      store.mode = "account";
      if (remote && (remote.updatedAt || 0) >= (state.updatedAt || 0)) { state = remote; writeLocal(); }
      else if (state.updatedAt) await writeRemote();
      store.emit();
    } catch (e) { store.error = (e && e.code) || "unavailable"; store.emit(); }
  }
  async function writeRemote() {
    if (!store.docRef) return;
    if (store.writing) { store.pending = true; return; }
    store.writing = true;
    try { await store.docRef.set({ payload: JSON.stringify(state), updatedAt: state.updatedAt, v: 2 }); store.error = null; store.mode = "account"; }
    catch (e) { store.error = (e && e.code) || "unavailable"; }
    finally { store.writing = false; store.emit(); if (store.pending) { store.pending = false; writeRemote(); } }
  }
  function save() { state.updatedAt = now(); writeLocal(); clearTimeout(store.timer); store.timer = setTimeout(writeRemote, 800); }
  const exportJSON = () => JSON.stringify({ app: "claude-certification-academy", exportedAt: new Date().toISOString(), state }, null, 1);
  function importJSON(text) {
    let o; try { o = JSON.parse(text); } catch (e) { return { ok: false, msg: "Dit is geen geldige export. Plak de volledige tekst, inclusief de accolades aan begin en eind." }; }
    let s = o && o.state ? o.state : o; if (!valid(s)) s = migrate(s);
    if (!s) return { ok: false, msg: "Deze tekst bevat geen voortgang van deze app." };
    state = s; save(); store.emit(); return { ok: true };
  }
  function resetCert(id) { state.certs[id] = emptyCert(); save(); }

  /* ---------------- inhoud ---------------- */
  const cert = id => A.certs[id || state.activeCert];
  const domOf = q => q.s.split(".")[0];
  function qmap(c) { if (!c._qm) { c._qm = {}; c.questions.forEach(q => c._qm[q.id] = q); } return c._qm; }
  function subMap(c) { if (!c._sm) { c._sm = {}; c.domains.forEach(d => d.subs.forEach(s => c._sm[s.id] = Object.assign({ domain: d }, s))); } return c._sm; }
  // scope: { kind: "all" } | { kind: "domain", id } | { kind: "sub", id }
  function pool(c, scope, st) {
    if (!scope || scope.kind === "all" || scope.kind === "weak") return c.questions;
    if (scope.kind === "hard") { st = st || cs(c.id); return c.questions.filter(q => { const x = st.q[q.id]; return x && ((x.lap || 0) >= 2 || x.ls > 0 || x.g); }); }
    if (scope.kind === "domain") return c.questions.filter(q => domOf(q) === scope.id);
    return c.questions.filter(q => q.s === scope.id);
  }

  /* ---------------- statistiek ---------------- */
  function stats(certId, scope) {
    const c = cert(certId), st = cs(certId), qs = pool(c, scope, st), t = now();
    let seen = 0, mastered = 0, wrong = 0, due = 0;
    qs.forEach(q => { const x = st.q[q.id]; if (!x) return; seen++; if (x.b >= MASTERED) mastered++; if (!x.ok) wrong++; if (x.due <= t) due++; });
    return { total: qs.length, seen, mastered, wrong, due, unseen: qs.length - seen };
  }

  /* ---------------- beheersing en prioriteit ----------------
     Beheersing per vraag: beheerst = 1, gezien en laatst goed = 0,5, fout/gegokt/nieuw = 0.
     Prioriteit = examenweging × wat er nog te leren valt. Hoogste prioriteit = meeste winst op het examen. */
  const qScore = x => !x ? 0 : x.b >= MASTERED ? 1 : x.ok ? 0.5 : 0;
  function mastery(certId, scope) {
    const c = cert(certId), st = cs(certId), qs = pool(c, scope, st);
    return qs.length ? qs.reduce((a, q) => a + qScore(st.q[q.id]), 0) / qs.length : 0;
  }
  // Beheersing van de hele stof, gewogen naar de officiële domeinwegingen (0–1).
  function readiness(certId) {
    const c = cert(certId), doms = c.domains.filter(d => c.questions.some(q => domOf(q) === d.id));
    const tw = doms.reduce((a, d) => a + d.weight, 0);
    return tw ? doms.reduce((a, d) => a + d.weight * mastery(certId, { kind: "domain", id: d.id }), 0) / tw : 0;
  }
  function priorities(certId) {
    const c = cert(certId), out = [];
    c.domains.forEach(d => {
      const subs = d.subs.filter(s => c.questions.some(q => q.s === s.id)); if (!subs.length) return;
      subs.forEach(s => { const m = mastery(certId, { kind: "sub", id: s.id }); out.push({ sub: s, domain: d, m, p: d.weight / subs.length * (1 - m) }); });
    });
    return out.sort((a, b) => b.p - a.p);
  }

  /* ---------------- mijlpalen ----------------
     Eenmalige momenten: een subonderwerp of domein helemaal beheerst, of de gewogen beheersing over 25/50/75/90%.
     Bij de eerste keer worden al behaalde mijlpalen stil vastgelegd. */
  const READY_STEPS = [25, 50, 75, 90];
  function achieved(certId) {
    const c = cert(certId), st = cs(certId), out = [];
    c.domains.forEach(d => {
      const dq = c.questions.filter(q => domOf(q) === d.id); if (!dq.length) return;
      d.subs.forEach(s => { const sq = dq.filter(q => q.s === s.id); if (sq.length && sq.every(q => st.q[q.id] && st.q[q.id].b >= MASTERED)) out.push({ key: "sub:" + s.id, kind: "sub", sub: s, domain: d }); });
      if (dq.every(q => st.q[q.id] && st.q[q.id].b >= MASTERED)) out.push({ key: "dom:" + d.id, kind: "dom", domain: d });
    });
    const r = readiness(certId) * 100;
    READY_STEPS.forEach(p => { if (r >= p) out.push({ key: "ready:" + p, kind: "ready", pct: p }); });
    return out;
  }
  function newMilestones(certId) {
    const st = cs(certId), list = achieved(certId);
    if (!st.ms) { st.ms = {}; list.forEach(m => st.ms[m.key] = now()); save(); return []; }
    const fresh = list.filter(m => !st.ms[m.key]); fresh.forEach(m => st.ms[m.key] = now());
    if (fresh.length) save();
    return fresh;
  }
  function lastMilestone(certId) {
    const st = cs(certId); if (!st.ms) return null;
    const keys = Object.keys(st.ms).sort((a, b) => st.ms[b] - st.ms[a]); if (!keys.length) return null;
    return achieved(certId).find(m => m.key === keys[0]) || null;
  }

  /* ---------------- leerfase voor foute vragen ----------------
     Een fout (of gegokt) antwoord zet een vraag in de leerfase. Die telt in vragen, niet in dagen:
       stap 1: de vraag komt terug na ~4 andere vragen (en in de herkansing aan het eind van de ronde);
       stap 2: na één keer goed komt hij nog eens terug na ~10 vragen (ongeveer de volgende ronde);
       twee keer op rij goed in de leerfase → uit de leerfase, terug op 1 dag.
     Weer fout → opnieuw stap 1. Vragen die je vaker fout had (lap ≥ 2) krijgen daarna kortere wachttijden.
     Sluit je de app, dan staan vragen in de leerfase bij de volgende keer direct klaar. */
  const STEP_GAP = [0, 4, 10];
  const lapFactor = lap => lap >= 3 ? 0.4 : lap >= 2 ? 0.6 : 1;
  const inLearning = x => !!x && x.n > 0 && (x.ls > 0 || (!x.ok && x.b === 0 && x.ls == null));
  function hardCount(certId) { const st = cs(certId); return cert(certId).questions.filter(q => { const x = st.q[q.id]; return x && ((x.lap || 0) >= 2 || x.ls > 0 || x.g); }).length; }

  /* ---------------- volgende vraag ----------------
     1. Vraag in de leerfase die weer aan de beurt is (in aantal vragen) → altijd eerst.
     Daarna, met wat toeval: 2. eerder fout en weer aan de beurt  3. nog nooit gezien
     4. aan de beurt voor herhaling (laagste bak eerst)  5. de vraag die het eerst terugkomt.
     Recent gestelde vragen worden overgeslagen. */
  function learnDue(qs, st, recent) {
    const seq = st.seq || 0, last2 = new Set(recent.slice(-2));
    const cands = qs.filter(q => { const x = st.q[q.id]; return x && x.ls > 0 && x.dueSeq != null && x.dueSeq <= seq && !last2.has(q.id); });
    if (!cands.length) return null;
    cands.sort((a, b) => st.q[a.id].dueSeq - st.q[b.id].dueSeq); return cands[0];
  }
  function pickFrom(qs, st, recent) {
    const t = now(), rec = new Set(recent);
    let cands = qs.filter(q => !rec.has(q.id));
    if (!cands.length) cands = qs.filter(q => q.id !== recent[recent.length - 1]);
    if (!cands.length) cands = qs.slice();
    const info = q => st.q[q.id];
    const dueWrong = cands.filter(q => info(q) && !info(q).ok && info(q).due <= t);
    const unseen = cands.filter(q => !info(q));
    const due = cands.filter(q => info(q) && info(q).due <= t);
    if (dueWrong.length && Math.random() < 0.6) return rnd(dueWrong);
    if (unseen.length && (!due.length || Math.random() < 0.6)) return rnd(unseen);
    if (due.length) { due.sort((a, b) => info(a).b - info(b).b || info(a).due - info(b).due); return rnd(due.slice(0, 4)); }
    cands.sort((a, b) => info(a).due - info(b).due);
    return rnd(cands.slice(0, 4));
  }
  function next(certId, scope, recent) {
    const c = cert(certId), st = cs(certId); recent = recent || [];
    const ld = learnDue(pool(c, scope, st), st, recent); if (ld) return ld;
    if (scope && scope.kind === "weak") {
      // Zwakste punten: kies een subonderwerp naar prioriteit (gekwadrateerd, zodat de zwakste duidelijk vaker komen).
      const pr = priorities(certId).filter(x => x.p > 0);
      if (!pr.length) return next(certId, { kind: "all" }, recent);
      const w = pr.map(x => x.p * x.p), tot = w.reduce((a, b) => a + b, 0); let r = Math.random() * tot, pick = pr[0];
      for (let i = 0; i < pr.length; i++) { r -= w[i]; if (r <= 0) { pick = pr[i]; break; } }
      return pickFrom(pool(c, { kind: "sub", id: pick.sub.id }), st, recent);
    }
    if (!scope || scope.kind === "all") {
      // Kies eerst een domein naar officiële weging, daarna een vraag in dat domein.
      const doms = c.domains.filter(d => c.questions.some(q => domOf(q) === d.id));
      if (!doms.length) return null;
      const total = doms.reduce((a, d) => a + d.weight, 0); let r = Math.random() * total, pick = doms[0];
      for (const d of doms) { r -= d.weight; if (r <= 0) { pick = d; break; } }
      return pickFrom(pool(c, { kind: "domain", id: pick.id }), st, recent);
    }
    const qs = pool(c, scope, st); return qs.length ? pickFrom(qs, st, recent) : null;
  }
  const isCorrect = (q, sel) => sel.length === q.a.length && sel.every(i => q.a.includes(i));
  // guessed = de gebruiker gaf aan te gokken. Een gegokt goed antwoord telt voor de score als goed,
  // maar voor het herhaalsysteem als 'nog niet gekend': de vraag gaat (weer) de leerfase in.
  function answer(certId, q, sel, guessed) {
    const st = cs(certId), ok = isCorrect(q, sel), x = st.q[q.id] || { b: 0, due: 0, n: 0, c: 0, last: 0, ok: false };
    const known = ok && !guessed, t = now();
    st.seq = (st.seq || 0) + 1;
    if (!known) {
      if (!ok) x.lap = (x.lap || 0) + 1;
      x.b = 0; x.ls = 1; x.dueSeq = st.seq + STEP_GAP[1]; x.due = t;
    } else if (inLearning(x)) {
      if ((x.ls || 1) === 1) { x.ls = 2; x.dueSeq = st.seq + STEP_GAP[2]; x.due = t; x.b = 0; }
      else { x.ls = 0; x.dueSeq = null; x.b = 1; x.due = t + INTERVAL_DAYS[1] * DAY * lapFactor(x.lap || 0); }
    } else {
      // Goed beantwoord vóórdat de vraag weer aan de beurt was (doorlopend oefenen): hooguit tot 'beheerst'.
      // Hogere bakken alleen als je de vraag op het herhaalmoment nog steeds goed hebt.
      const early = x.due > t;
      x.b = early ? Math.max(x.b, Math.min(x.b + 1, MASTERED)) : Math.min(MAX_BOX, x.b + 1);
      x.due = t + INTERVAL_DAYS[x.b] * DAY * lapFactor(x.lap || 0);
    }
    x.n++; if (ok) x.c++; x.last = t; x.ok = known; x.g = !!(ok && guessed);
    st.q[q.id] = x; st.total.n++; if (ok) st.total.c++;
    save(); return ok;
  }

  /* ---------------- foutmeldingen bij vragen ---------------- */
  async function report(certId, q, text) {
    const item = { cert: certId, qid: q.id, text: String(text).slice(0, 2000), t: now(), guide: cert(certId).guideVersion || "" };
    cs(certId).reports.push(item); save();
    if (store.db) { try { await store.db.collection("reports").add(item); return "account"; } catch (e) { return "local"; } }
    return "local";
  }

  // Melding als GitHub-issue (Radar op GitHub Pages). Titel "Examenmelding: <cert> <vraag>"; de maandcontrole leest ze.
  const REPO = "tomasr91/data-ai-radar";
  function reportUrl(q, text) {
    const c = cert();
    const body = "Melding uit het Claude-examen in de Data & AI Radar. De maandcontrole verwerkt dit en sluit het issue.\n\n"
      + "**Certificering:** " + c.code + " (" + c.id + ")\n**Vraag:** " + q.id + " (" + q.s + ")\n**Examengids:** " + (c.guideVersion || "-") + "\n\n"
      + "> " + String(q.q).slice(0, 600) + "\n\n**Wat klopt er niet:**\n" + String(text).slice(0, 2000);
    return "https://github.com/" + REPO + "/issues/new?title=" + encodeURIComponent("Examenmelding: " + c.id + " " + q.id) + "&body=" + encodeURIComponent(body);
  }

  A.core = { get state() { return state; }, cs, cert, qmap, subMap, domOf, pool, stats, next, answer, isCorrect, report, reportUrl, shuffle,
    store, init, save, exportJSON, importJSON, resetCert, mastery, readiness, priorities, newMilestones, lastMilestone, hardCount, inLearning, constants: { INTERVAL_DAYS, MASTERED } };
})();

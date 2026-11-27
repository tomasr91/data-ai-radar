// Controleert de vragenbank van het Claude-examen (app/leren/content).
// Gebruik: node scripts/validate_leren.js   (exit 1 bij fouten)
//
// Regels (gelijk aan de maandcontrole):
// - unieke vraag-id's per certificering
// - t = "s" heeft precies één juist antwoord, t = "m" minstens twee
// - elk antwoord-index (a) bestaat in de opties (o)
// - de uitleg per optie (w) is even lang als de opties
// - elke vraag hoort bij een bestaand subonderwerp; elk subonderwerp heeft vragen
// - lengte verraadt het antwoord niet: juiste antwoord het langste bij 15–32% van de vragen,
//   en hooguit 15% 'duidelijk het langste' (meer dan 20% langer dan elke foute optie). Lengte zonder HTML-tags.
const fs = require("fs");
const path = require("path");
const vm = require("vm");

const root = path.join(__dirname, "..", "app", "leren");
const html = fs.readFileSync(path.join(root, "index.html"), "utf8");
const scripts = [...html.matchAll(/<script src="(content\/[^"]+)"><\/script>/g)].map((m) => m[1]);
const ctx = {};
ctx.window = ctx;   // zoals in de browser: window is het globale object
vm.createContext(ctx);
for (const s of scripts) {
  const code = fs.readFileSync(path.join(root, s), "utf8");
  vm.runInContext(code, ctx, { filename: s });
}
const A = ctx.window.Academy;
const errors = [], warnings = [];
let total = 0;
for (const id of A.order) {
  const c = A.certs[id];
  if (!c.questions.length) continue;
  const subs = new Set();
  (c.domains || []).forEach((d) => (d.subs || []).forEach((s) => subs.add(s.id)));
  const seen = new Set(), perSub = {};
  let longest = 0, clear = 0, single = 0;
  for (const q of c.questions) {
    const where = `${id}/${q.id}`;
    if (seen.has(q.id)) errors.push(`${where}: id komt dubbel voor`);
    seen.add(q.id);
    if (!subs.has(q.s)) errors.push(`${where}: onbekend subonderwerp '${q.s}'`);
    perSub[q.s] = (perSub[q.s] || 0) + 1;
    if (!Array.isArray(q.o) || q.o.length < 2) { errors.push(`${where}: te weinig opties`); continue; }
    if (!Array.isArray(q.a) || !q.a.length || q.a.some((i) => !Number.isInteger(i) || i < 0 || i >= q.o.length)) errors.push(`${where}: antwoord-index buiten bereik`);
    if (q.t === "s" && q.a.length !== 1) errors.push(`${where}: t="s" moet precies één juist antwoord hebben`);
    if (q.t === "m" && q.a.length < 2) errors.push(`${where}: t="m" moet minstens twee juiste antwoorden hebben`);
    if (q.t !== "s" && q.t !== "m") errors.push(`${where}: t moet "s" of "m" zijn`);
    if (!Array.isArray(q.w) || q.w.length !== q.o.length) errors.push(`${where}: w moet even lang zijn als o`);
    if (q.t === "s") {
      single++;
      const lens = q.o.map((x) => String(x).replace(/<[^>]+>/g, "").replace(/&[a-z]+;/g, "x").length);
      const k = lens[q.a[0]], rest = Math.max(...lens.filter((_, i) => i !== q.a[0]));
      if (k >= rest) longest++;
      if (k > rest * 1.2) clear++;
    }
  }
  for (const s of subs) if (!perSub[s]) errors.push(`${id}: subonderwerp ${s} heeft geen vragen`);
  const share = single ? longest / single : 0;
  if (share > 0.32 || share < 0.15) warnings.push(`${id}: bij ${Math.round(share * 100)}% van de vragen is het juiste antwoord het langste (hoort 15–32%)`);
  if (single && clear / single > 0.15) warnings.push(`${id}: bij ${Math.round(clear / single * 100)}% is het juiste antwoord duidelijk het langste (hooguit 15%)`);
  total += c.questions.length;
  console.log(`${id}: ${c.questions.length} vragen, ${subs.size} subonderwerpen, juiste antwoord langste bij ${Math.round(share * 100)}%`);
}
warnings.forEach((w) => console.log("WAARSCHUWING " + w));
errors.forEach((e) => console.log("FOUT " + e));
console.log(`${total} vragen gecontroleerd, ${errors.length} fouten, ${warnings.length} waarschuwingen`);
process.exit(errors.length ? 1 : 0);

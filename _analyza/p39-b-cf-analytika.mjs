// p39-b-cf-analytika.mjs — HISTORIE a MINUTOVÝ OBRAZ CPU conductora z Cloudflare
// Analytics pro P39 (READ-ONLY; jen GraphQL dotaz).
//
// PROČ VLASTNÍ (H166): `p38-b-cf-analytika.mjs` i `p38-a-obnova.mjs` zapisují do
// SVÝCH dokladů (`p38-b-cf-analytika-*-vystup.txt`, `p38-a-obnova-vystup.txt`).
// P39 už jednou cizí doklad přepsala (viz HANDOFF §70) — tenhle nástroj má
// VLASTNÍ jména, takže se to nemůže zopakovat. Navíc dělá v JEDNOM běhu to, co
// P38 dělala ve dvou (kvantily + minuty úmrtí), protože P39 potřebuje spojit
// „tik tiká každou minutu" s „nikde neumírá".
//
// POZOR NA JEDNOTKY: `sum.cpuTimeUs`, `quantiles.cpuTimeP50/P99`, `sum.wallTime`
// jsou v MIKROSEKUNDÁCH (kalibrace na konci výstupu).
// POZOR NA POLE: `sum.cpuTime` NEEXISTUJE (H: jména polí CF GraphQL se nehádají).
//
// Token se ČTE z konfigurace wrangleru (`oauth_token`), NIKDY se nevypisuje.
// Použití: node _analyza/p39-b-cf-analytika.mjs [hodin-zpet]
// Exit 0 = měřeno; 2 = token nenalezen; 3 = GraphQL vrátil chyby.

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONFIG = 'C:\\Users\\Ssevc\\AppData\\Roaming\\xdg.config\\.wrangler\\config\\default.toml';
const ACC = 'b19df1f89d07d2cb5b516c95ee8919e1';
const SCRIPT = 'forge-conductor';
const hodin = Number(process.argv[2] || 30);

// Hranice, od které P39 měří: nasazení #40 (P38) skončilo 18:39:44Z.
const PO_NASAZENI = '2026-10-11T18:40';

const cfg = readFileSync(CONFIG, 'utf8');
const m = cfg.match(/^\s*oauth_token\s*=\s*"([^"]+)"/m);
if (!m) { console.log('CHYBA: oauth_token v konfiguraci wrangleru nenalezen'); process.exit(2); }
const token = m[1];

const do_ = new Date();
const od = new Date(do_.getTime() - hodin * 3600 * 1000);

const dotaz = `
query Q($acc: String!, $script: String!, $od: Time!, $do: Time!) {
  viewer {
    accounts(filter: {accountTag: $acc}) {
      workersInvocationsAdaptive(limit: 10000, filter: {scriptName: $script, datetime_geq: $od, datetime_leq: $do}, orderBy: [datetime_ASC]) {
        dimensions { datetime status }
        sum { requests errors subrequests cpuTimeUs wallTime }
        quantiles { cpuTimeP50 cpuTimeP99 }
      }
    }
  }
}`;

const r = await fetch('https://api.cloudflare.com/client/v4/graphql', {
  method: 'POST',
  headers: { authorization: `Bearer ${token}`, 'content-type': 'application/json' },
  body: JSON.stringify({ query: dotaz, variables: { acc: ACC, script: SCRIPT, od: od.toISOString(), do: do_.toISOString() } }),
});
const j = await r.json();
const radky = j?.data?.viewer?.accounts?.[0]?.workersInvocationsAdaptive ?? [];
const raw = { mereno: do_.toISOString(), od: od.toISOString(), hodin, http_status: r.status, chyby: j.errors ?? null, radky };
writeFileSync(join(WS, '_analyza/p39-b-cf-analytika-raw-vystup.txt'), JSON.stringify(raw, null, 1) + '\n', 'utf8');

const radkyTxt = [];
const p = (x = '') => { radkyTxt.push(x); console.log(x); };
p(`# p39-b — Cloudflare Analytics conductora (${hodin} h) — ${do_.toISOString()}`);
if (j.errors) {
  p('CHYBY GraphQL: ' + JSON.stringify(j.errors).slice(0, 1200));
  writeFileSync(join(WS, '_analyza/p39-b-cf-analytika-vystup.txt'), radkyTxt.join('\n') + '\n', 'utf8');
  process.exit(3);
}
p(`# řádků z API: ${radky.length} (HTTP ${r.status}) · okno od ${od.toISOString()}`);
p('# POZOR na jednotky: `cpuTimeUs`, `cpuTimeP50/P99` a `wallTime` jsou v MIKROSEKUNDÁCH.');
p('');

// ---------- 1) podle statusu za celé okno -----------------------------------
const podle = new Map();
for (const x of radky) {
  const k = x.dimensions.status;
  const q = podle.get(k) || { requesty: 0, chyby: 0, cpu_us: 0 };
  q.requesty += x.sum.requests; q.chyby += x.sum.errors; q.cpu_us += x.sum.cpuTimeUs || 0;
  podle.set(k, q);
}
p('## PODLE STATUSU (celé okno)');
for (const [k, v] of [...podle].sort((a, b) => b[1].requesty - a[1].requesty)) {
  p(`   ${k.padEnd(20)} ${String(v.requesty).padStart(7)} invokací · ${String(v.chyby).padStart(5)} chyb · CPU celkem ${(v.cpu_us / 1000).toFixed(0)} ms · Ø ${v.requesty ? (v.cpu_us / v.requesty / 1000).toFixed(1) : '?'} ms`);
}
p('');

// ---------- 2) minuty: úmrtí vs. success ------------------------------------
const minuta = new Map();
for (const x of radky) {
  const k = x.dimensions.datetime;
  const q = minuta.get(k) || { success: 0, exceededResources: 0, jine: 0 };
  const st = x.dimensions.status;
  if (st === 'success') q.success += x.sum.requests;
  else if (st === 'exceededResources') q.exceededResources += x.sum.requests;
  else q.jine += x.sum.requests;
  minuta.set(k, q);
}
const klice = [...minuta.keys()].sort();
const umirajici = klice.filter((k) => minuta.get(k).exceededResources > 0);
const posledniUmirajici = umirajici.length ? umirajici[umirajici.length - 1] : null;

p('## MINUTY S UMÍRAJÍCÍ INVAKACÍ (`exceededResources`) — posledních 40');
for (const k of umirajici.slice(-40)) {
  p(`   ${k}  exceeded=${minuta.get(k).exceededResources}  success=${minuta.get(k).success}`);
}
p(`   → minut s úmrtím v okně: ${umirajici.length}`);
p(`   → POSLEDNÍ taková minuta: ${posledniUmirajici ?? '(žádná)'}`);
p('');

p(`## MINUTY PO NASAZENÍ #40 (od ${PO_NASAZENI}) — úmrtí a pokrytí tiku`);
let poN = 0, poNUmrti = 0, poNBezSuccess = 0;
for (const k of klice.filter((x) => x >= PO_NASAZENI)) {
  const mm = minuta.get(k);
  poN++;
  if (mm.exceededResources > 0) poNUmrti++;
  if (mm.success === 0) poNBezSuccess++;
  p(`   ${k}  success=${String(mm.success).padStart(3)}  exceeded=${String(mm.exceededResources).padStart(3)}  jine=${mm.jine}`);
}
p('');
p('## SOUHRN OBDOBÍ PO NASAZENÍ #40');
p(`   minut (vč. minuty nasazení): ${poN}`);
p(`   z toho s exceededResources:  ${poNUmrti}`);
p(`   z toho BEZ jediné success:   ${poNBezSuccess}  (díra v pokrytí — cron má tiknout každou minutu)`);
if (poNUmrti === 0) p('   ✓ OD NASAZENÍ NEUMŘELA ANI JEDNA INVAKACE');
else p(`   ✗ PO NASAZENÍ UMÍRALY INVAKACE v ${poNUmrti} minutách — obnova NENÍ úplná`);
p('');

// ---------- 3) po hodinách: kvantily podle statusu --------------------------
const hodiny = new Map();
for (const x of radky) {
  const h = x.dimensions.datetime.slice(0, 13);
  const st = x.dimensions.status;
  const q = hodiny.get(h) || { statusy: new Map(), podle_statusu: new Map() };
  q.statusy.set(st, (q.statusy.get(st) || 0) + x.sum.requests);
  const s = q.podle_statusu.get(st) || { cpu_us: 0, requesty: 0, p50: [], p99: [], wall_us: 0 };
  s.cpu_us += x.sum.cpuTimeUs || 0; s.requesty += x.sum.requests;
  s.wall_us += x.sum.wallTime || 0;
  if (x.quantiles?.cpuTimeP50 != null) s.p50.push(x.quantiles.cpuTimeP50);
  if (x.quantiles?.cpuTimeP99 != null) s.p99.push(x.quantiles.cpuTimeP99);
  q.podle_statusu.set(st, s);
  hodiny.set(h, q);
}
p('## PO HODINÁCH (UTC) — CPU v ms (`cpuTimeUs`/1000)');
p('   hodina        | success | exceededRes | jine | CPU Ø success | CPU Ø exceeded | P50 max success | P50 max exceeded | wall Ø exceeded');
for (const [h, q] of [...hodiny].sort()) {
  const succ = q.statusy.get('success') || 0;
  const exc = q.statusy.get('exceededResources') || 0;
  const jine = [...q.statusy].filter(([k]) => k !== 'success' && k !== 'exceededResources').reduce((a, b) => a + b[1], 0);
  const S = q.podle_statusu.get('success');
  const E = q.podle_statusu.get('exceededResources');
  const f = (v, n) => (v && n ? (v / n / 1000).toFixed(1) : '-');
  const pm = (s) => (s && s.p50.length ? (Math.max(...s.p50) / 1000).toFixed(1) : '-');
  const wm = (s) => (s && s.requesty ? (s.wall_us / s.requesty / 1000).toFixed(0) : '-');
  p(`   ${h} | ${String(succ).padStart(7)} | ${String(exc).padStart(11)} | ${String(jine).padStart(4)} | ${f(S?.cpu_us, S?.requesty).padStart(13)} | ${f(E?.cpu_us, E?.requesty).padStart(14)} | ${pm(S).padStart(15)} | ${pm(E).padStart(16)} | ${wm(E).padStart(12)}`);
}
p('');

// ---------- 4) kalibrace jednotky -------------------------------------------
const vsechnyP50 = radky.map((x) => x.quantiles?.cpuTimeP50).filter((x) => x != null);
if (vsechnyP50.length) {
  const s = [...vsechnyP50].sort((a, b) => a - b);
  const med = s[Math.floor(s.length / 2)];
  p('## KALIBRACE JEDNOTKY');
  p(`   medián cpuTimeP50 ze všech řádků = ${med} (raw)`);
  p(`   → když je to µs, je to ${(med / 1000).toFixed(1)} ms (živý tail hlásí cron 18–25 ms, /health 3–8 ms)`);
}

writeFileSync(join(WS, '_analyza/p39-b-cf-analytika-vystup.txt'), radkyTxt.join('\n') + '\n', 'utf8');
console.log('\n[zapsano] _analyza/p39-b-cf-analytika-vystup.txt');
process.exit(poNUmrti === 0 && posledniUmirajici ? 0 : 1);

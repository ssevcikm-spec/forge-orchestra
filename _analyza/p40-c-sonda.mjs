// p40-c-sonda.mjs — ŽIVÉ měření režie D1 a efektivního CPU limitu (zadání P40).
//
// PROČ: offline model (`p40-a`) umí změřit GitHub a logiku, ale NE režii
// prohlížeče D1 — a tik dělá 21–23 round-tripů. Právě tam může být těch
// ~11 ms, které v modelu chybí (model: 5,5 ms, živý tik: 16–20 ms).
//
// MĚŘÍ SE NA VLASTNÍM WORKERU `forge-probe` (viz `p40-probe/`), aby se
// NEDOTKLA nasazená verze conductora — tu je na konci potřeba ověřit
// (`Current Version ID` == `scriptVersion.id` živého tailu).
//
// Dva režimy:
//   node _analyza/p40-c-sonda.mjs --posli     # pošle označené požadavky (tail běží zvlášť)
//   node _analyza/p40-c-sonda.mjs             # rozbere raw tail + požadavky → doklad
//
// Výstupní cesty (H191 — vlastní jména, nikdy cizí doklad):
//   _analyza/p40-c-sonda-pozadavky-vystup.txt
//   _analyza/p40-c-sonda-vystup.txt

import { existsSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const BASE = 'https://forge-probe.ssevcikm.workers.dev';
const TAIL = join(WS, '_analyza', 'p40-probe-tail-raw.txt');
const POZ = join(WS, '_analyza', 'p40-c-sonda-pozadavky-vystup.txt');
const OUT = join(WS, '_analyza', 'p40-c-sonda-vystup.txt');
const TOKEN = 'p40-probe';

// ── plán požadavků: každý má ŠTÍTEK, aby se v tailu dal přiřadit ────────────
// DRUHÉ KOLO (P40): `f=` měří REŽII SUBREQUESTU (payload ~15 B), `d1=` totéž pro
// D1 — a v tailu je navíc **CRON s prázdným handlerem** = baseline invokace.
const PLAN = [
  ['baseline-1', 'd1=0'],
  ['baseline-2', 'd1=0'],
  ['f-1', 'f=1'],
  ['f-5', 'f=5'],
  ['f-10', 'f=10'],
  ['d1-20', 'd1=20'],
  ['batch-20', 'batch=20'],
];

if (process.argv.includes('--posli')) {
  const radky = [`# p40-c — označené požadavky na sondu — ${new Date().toISOString()}`];
  for (const [stitek, q] of PLAN) {
    const t0 = Date.now();
    let stav = 0;
    let telo = '';
    try {
      const r = await fetch(`${BASE}/?token=${TOKEN}&${q}`);
      stav = r.status;
      telo = await r.text();
    } catch (e) {
      telo = 'CHYBA: ' + String(e).slice(0, 120);
    }
    const radek = `${stitek} | HTTP ${stav} | ${Date.now() - t0} ms | /?${q} | ${telo.slice(0, 300)}`;
    radky.push(radek);
    console.log(radek);
    await new Promise((r) => setTimeout(r, 2500));
  }
  writeFileSync(POZ, radky.join('\n') + '\n', 'utf8');
  console.log(`\n[zapsano] ${POZ}`);
  process.exit(0);
}

// ── rozbor: z raw tailu se vezmou cpuTime/wallTime/outcome per invokace ─────
if (!existsSync(TAIL)) {
  console.log(`CHYBA: ${TAIL} neexistuje — pusť tail a pak --posli`);
  process.exit(2);
}
const raw = readFileSync(TAIL, 'utf8');

// `wrangler tail --format json` může psát buď jeden JSON na řádek, nebo pretty
// JSON (jako v P39). Čteme proto VYVAŽOVÁNÍM závorek — ne řádkováním.
const udalosti = [];
let hloubka = 0;
let zacatek = -1;
for (let i = 0; i < raw.length; i++) {
  const c = raw[i];
  if (c === '{') { if (hloubka === 0) zacatek = i; hloubka++; }
  else if (c === '}') {
    hloubka--;
    if (hloubka === 0 && zacatek >= 0) {
      const t = raw.slice(zacatek, i + 1);
      try { udalosti.push(JSON.parse(t)); } catch { /* neúplný objekt */ }
      zacatek = -1;
    }
  }
}

const stitky = [];
if (existsSync(POZ)) {
  for (const l of readFileSync(POZ, 'utf8').splitlines ? readFileSync(POZ, 'utf8').split(/\r?\n/) : []) {
    const m = l.match(/^(\S+) \| HTTP (\d+) \| (\d+) ms \| (\S+)/);
    if (m) stitky.push({ stitek: m[1], http: Number(m[2]), ms: Number(m[3]), q: m[4] });
  }
}

const radky = [];
const p = (x = '') => { radky.push(x); console.log(x); };
p(`# p40-c — ŽIVÁ SONDA: režie D1 a efektivní CPU limit — ${new Date().toISOString()}`);
p(`# worker: forge-probe (DOČASNÝ, vlastní verze — conductor nedotčen)`);
p(`# eventů v tailu: ${udalosti.length} · požadavků v dokladu: ${stitky.length}`);
p('');

p('## PER-INVOKACE (z wrangler tail)');
p('   cpuTime | wallTime | outcome | url (query)');
const podleUrl = [];
for (const u of udalosti) {
  const url = u?.event?.request?.url || u?.event?.request?.path || '(bez url)';
  const cpu = u?.event?.cpuTime ?? u?.cpuTime;
  const wall = u?.event?.wallTime ?? u?.wallTime;
  const outcome = u?.event?.outcome ?? u?.outcome ?? '?';
  const q = url.includes('?') ? url.slice(url.indexOf('?')) : '';
  podleUrl.push({ q, cpu, wall, outcome });
  p(`   ${String(cpu ?? '?').padStart(7)} | ${String(wall ?? '?').padStart(8)} | ${String(outcome).padEnd(16)} | ${q.slice(0, 60)}`);
}

// Párování: kdo má `burn=`/`d1=`/`json=` v query.
const najdi = (pred) => podleUrl.filter((x) => pred(x.q));
const cisla = (a) => a.map((x) => Number(x.cpu)).filter((x) => Number.isFinite(x));
const med = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : NaN; };

p('');
p('## ODPOVĚDI SONDY (co hlásila sama invokace)');
for (const l of readFileSync(POZ, 'utf8').split(/\r?\n/)) if (l.startsWith('baseline') || l.includes('HTTP 200')) p('   ' + l.slice(0, 220));

p('');
p('## ODVOZENÉ HODNOTY');
const podleStitku = new Map();
for (const x of podleUrl) {
  const q = x.q.replace(/^\?token=[^&]*&?/, '');
  const zn = PLAN.find(([, qq]) => qq === q);
  const k = zn ? zn[0] : '(nepřiřazeno: ' + q + ')';
  const a = podleStitku.get(k) || [];
  a.push(x);
  podleStitku.set(k, a);
}
// Párování podle PREFIXU štítku (iters-1 … iters-12)
const cpuStitku = (pred) => {
  const out = [];
  for (const [k, a] of podleStitku) if (pred(k)) out.push(...cisla(a));
  return out;
};
const b0 = [...cpuStitku((k) => k.startsWith('baseline')), ...cisla(najdi((q) => q === '?d1=0'))];
const seq20 = cisla(najdi((q) => q.includes('d1=20')));
const seq50 = cpuStitku((k) => k.startsWith('d1-50')).concat(cisla(najdi((q) => q.includes('d1=50'))));
p(`   baseline (žádná práce):        cpuTime ${b0.join(', ') || 'NEMĚŘENO'} ms (n=${b0.length})`);
p(`   d1=20 (20 round-tripů):       cpuTime ${seq20.join(', ') || 'NEMĚŘENO'} ms`);
p(`   d1=50 (50 round-tripů):       cpuTime ${seq50.join(', ') || 'NEMĚŘENO'} ms`);
let naR = NaN;
if (b0.length && seq50.length) {
  naR = (med(seq50) - med(b0)) / 50;
  p(`   → režie NA JEDEN D1 ROUND-TRIP ≈ ${naR.toFixed(3)} ms CPU`);
  p(`   → tik s 21 round-tripy:          ${(21 * naR).toFixed(2)} ms CPU`);
}
if (b0.length && seq20.length) {
  p(`   kontrola d1=20: ${((med(seq20) - med(b0)) / 20).toFixed(3)} ms na round-trip`);
}
// batch: N příkazů jedním voláním vs. N sekvenčních round-tripů
const bat20 = cisla(najdi((q) => q.includes('batch=20')));
const bat50 = cisla(najdi((q) => q.includes('batch=50')));
p('   `DB.batch()` — TVRZENÍ, NA KTERÉM STOJÍ ZLEVNĚNÍ:');
if (bat20.length && Number.isFinite(naR)) {
  p(`     batch(20) = 20 příkazů JEDNÍM voláním: cpuTime ${bat20.join(', ')} ms`
    + `  (proti 20 sekvenčním ≈ ${(20 * naR).toFixed(2)} ms)`);
}
if (bat50.length && Number.isFinite(naR)) {
  p(`     batch(50) = 50 příkazů JEDNÍM voláním: cpuTime ${bat50.join(', ')} ms`
    + `  (proti 50 sekvenčním ≈ ${(50 * naR).toFixed(2)} ms)`);
}
const ghRest = najdi((q) => q.includes('gh=rest'));
const ghGql = najdi((q) => q.includes('gh=gql'));
p('   reálná práce GITHUBu ve workerd (cpuTime):');
p(`     REST /pulls 600 kB:  ${ghRest.map((x) => x.cpu).join(', ') || 'NEMĚŘENO'} ms (${[...new Set(ghRest.map((x) => x.outcome))].join('/')})`);
p(`     GraphQL merged PR:  ${ghGql.map((x) => x.cpu).join(', ') || 'NEMĚŘENO'} ms (${[...new Set(ghGql.map((x) => x.outcome))].join('/')})`);
p('   iters (busy loop, jen CPU):');
for (const [k, a] of [...podleStitku].filter(([k]) => k.startsWith('iters'))) {
  if (a[0]) p(`     ${k}: cpuTime ${a.map((x) => x.cpu).join(',')} ms · wall ${a.map((x) => x.wall).join(',')} · ${a.map((x) => x.outcome).join('/')}`);
}
const jsonEv = podleStitku.get('json-600kb') || [];
p(`   JSON.parse 600 kB:             cpuTime ${jsonEv.map((x) => x.cpu).join(', ') || 'NEMĚŘENO'} ms`);
p(`   outcome všech invokací:        ${[...new Set(podleUrl.map((x) => x.outcome))].join(', ')}`);
p('');
p('## CO Z TOHO PLYNE PRO CONDUCTORA');
p('   Tik dělá 21–23 round-tripů na D1. Když je režie na round-trip výš než ~0,3 ms,');
p('   je to hlavní položka rozpočtu — a zlevnění znamená ŠKRTAT ROUND-TRIPY (batch),');
p('   ne „zrychlovat logiku“.');

writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
console.log(`\n[zapsano] ${OUT}`);
process.exit(0);

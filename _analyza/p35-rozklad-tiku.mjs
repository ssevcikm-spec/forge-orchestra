// p35-rozklad-tiku.mjs — ROZKLAD CPU TIKU: kolik stojí ta GITHUB část, kterou tik
// dělá KAŽDOU MINUTU.
//
// PROČ: živý profil (`p35-tail-rozbor.py`) naměřil, že `POST /tick` stojí
// 15–25 ms CPU a `cron` 27–36 ms, kdežto `/poll` (jeden SELECT a předčasný
// návrat) stojí 0 ms a `/health` 2–3 ms. Rozdíl je PRÁCE TIKU — a ta se skládá
// ze dvou druhů: D1 obraty a volání GitHubu. Tenhle skript měří TU DRUHOU
// polovinu **na živých datech**: stáhne TYTÉŽ endpointy, které tik volá
// (`/pulls?state=closed&per_page=100`, `/pulls?state=open&per_page=30`,
// `/contents/<roadmap>`), změří bajty a **čas `JSON.parse`** (medián z N běhů,
// stejný engine V8 jako Workers) — a řekne, jaký díl naměřeného CPU to je.
//
// ⚠ CO TENHLE SKRIPT NETVRDÍ: že `JSON.parse` v Node je PŘESNĚ totéž co CPU ve
// Workeru. Je to PROXY téhož výpočtu (parsování téhož textu týmž enginem) a je
// to tak i pojmenované ve výstupu. Síť se do CPU nepočítá (do wall time ano) —
// proto se měří parse, ne latence.
//
// Použití: node _analyza/p35-rozklad-tiku.mjs [--n 11] [--vystup x.txt]
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const argv = process.argv.slice(2);
const nIdx = argv.indexOf('--n');
const N = nIdx >= 0 ? Number(argv[nIdx + 1]) : 11;
const vIdx = argv.indexOf('--vystup');
const out = vIdx >= 0 ? argv[vIdx + 1] : '_analyza/p35-rozklad-tiku-vystup.txt';

const env = Object.fromEntries(
  readFileSync(join(WS, '.env'), 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }),
);
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { authorization: `Bearer ${PAT}`, accept: 'application/vnd.github+json', 'user-agent': 'forge-p35' };

const doklad = [];
const p = (x = '') => { console.log(x); doklad.push(x); };

const median = (a) => { const b = [...a].sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };

async function text(url) {
  const r = await fetch(url, { headers: H });
  const t = await r.text();
  return { status: r.status, text: t, bytes: Buffer.byteLength(t, 'utf8') };
}

function merParse(text, fn) {
  const casy = [];
  let hodnota = null;
  for (let i = 0; i < N; i++) {
    const t0 = process.hrtime.bigint();
    hodnota = fn(text);
    const t1 = process.hrtime.bigint();
    casy.push(Number(t1 - t0) / 1e6);
  }
  return { ms: median(casy), hodnota };
}

p(`# P35 — ROZKLAD GITHUB ČÁSTI TIKU — ${new Date().toISOString()}`);
p(`# měřeno na ŽIVÝCH datech (GitHub API), parsování: medián z ${N} běhů v Node (proxy CPU)`);
p('');

// Registr her si skript bere ŽIVĚ ze služby — kdyby se hra přepnula, měřil by
// jinam a tvrdil by to o téhle hře (past: odkaz na projekt se NEOPISUJE).
const h = await (await fetch(`${env.FORGE_URL}/health`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();
const hry = (h.targets || []).map((t) => ({ repo: t.repo }));
p(`# aktivní hry podle /health: ${hry.map((x) => x.repo).join(', ') || '(žádná)'}`);
p('');

let celkemMs = 0;
let celkemB = 0;
const radky = [];

for (const g of hry) {
  // 1) uzavřené PR (per_page=100) — tik je čte KAŽDOU MINUTU kvůli `merged_at`
  {
    const t = await text(`https://api.github.com/repos/${g.repo}/pulls?state=closed&per_page=100&sort=updated&direction=desc`);
    const m = merParse(t.text, (s) => JSON.parse(s));
    radky.push({ repo: g.repo, co: 'GET /pulls?state=closed&per_page=100', http: t.status, B: t.bytes, ms: m.ms, n: Array.isArray(m.hodnota) ? m.hodnota.length : null });
  }
  // 2) otevřené PR (per_page=30) — brána „čeká se na kontrolu X PR“
  {
    const t = await text(`https://api.github.com/repos/${g.repo}/pulls?state=open&per_page=30`);
    const m = merParse(t.text, (s) => JSON.parse(s));
    radky.push({ repo: g.repo, co: 'GET /pulls?state=open&per_page=30', http: t.status, B: t.bytes, ms: m.ms, n: Array.isArray(m.hodnota) ? m.hodnota.length : null });
  }
  // 3) soubor roadmapy (base64 → bajty → JSON.parse), přesně jako tik
  {
    const games = await (await fetch(`${env.FORGE_URL}/games`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();
    const soubor = (games.games || []).find((x) => x.repo === g.repo)?.roadmap_file || '.forge/roadmap.json';
    const t = await text(`https://api.github.com/repos/${g.repo}/contents/${soubor}`);
    const m = merParse(t.text, (s) => {
      const d = JSON.parse(s);
      const bytes = Uint8Array.from(atob(String(d.content || '').replace(/\n/g, '')), (c) => c.charCodeAt(0));
      return JSON.parse(new TextDecoder().decode(bytes));
    });
    const nb = Buffer.byteLength(t.text, 'utf8');
    radky.push({ repo: g.repo, co: `GET /contents/${soubor} (base64+parse)`, http: t.status, B: nb, ms: m.ms,
      n: Array.isArray(m.hodnota?.grains || m.hodnota?.tasks) ? (m.hodnota.grains || m.hodnota.tasks).length : null });
  }
}

p('## JEDNOTLIVÁ VOLÁNÍ (co tik dělá každou minutu)');
p('  repo                        | co                                          | HTTP |      B | parse ms | položek');
for (const r of radky) {
  p(`  ${r.repo.padEnd(27)} | ${r.co.padEnd(43)} | ${String(r.http).padEnd(4)} | ${String(r.B).padStart(6)} | ` +
    `${r.ms.toFixed(2).padStart(8)} | ${r.n ?? '—'}`);
  celkemMs += r.ms;
  celkemB += r.B;
}

p('');
p('## SOUHRN GITHUB ČÁSTI (jeden tik, jedna hra)');
p(`  volání na tik:            ${radky.length}`);
p(`  přenesených bajtů na tik: ${celkemB} B (${(celkemB / 1024).toFixed(0)} kB)`);
p(`  CPU na parsování na tik:  ${celkemMs.toFixed(2)} ms (medián z ${N} běhů, proxy CPU)`);
p('');
p('## SROVNÁNÍ S NAMĚŘENÝM CPU TIKU (z `_analyza/p35-tail-rozbor-data-vystup.txt`)');
try {
  const rozbor = JSON.parse(readFileSync(join(WS, '_analyza/p35-tail-rozbor-data-vystup.txt'), 'utf8'));
  const tick = rozbor.podle['POST /tick']?.cpu || [];
  const cron = rozbor.podle['cron(* * * * *)']?.cpu || [];
  if (tick.length) p(`  POST /tick  cpuTime: min=${Math.min(...tick)} med=${median(tick)} max=${Math.max(...tick)} (n=${tick.length})`);
  if (cron.length) p(`  cron        cpuTime: min=${Math.min(...cron)} med=${median(cron)} max=${Math.max(...cron)} (n=${cron.length})`);
  const ref = tick.length ? median(tick) : (cron.length ? median(cron) : null);
  if (ref) p(`  → GitHub parsování je ${(100 * celkemMs / ref).toFixed(0)} % naměřeného CPU tiku (${celkemMs.toFixed(2)} z ${ref} ms)`);
  else p('  NEZMĚŘENO: v rozboru tailu není cpuTime pro /tick ani cron');
} catch (e) {
  p(`  NEZMĚŘENO: rozbor tailu se nedá přečíst (${String(e).slice(0, 80)}) — spusť napřed p35-tail-rozbor.py`);
}
p('');
p(`[zapsano] ${out} (${doklad.join('\n').length} znaků)`);
writeFileSync(join(WS, out), doklad.join('\n') + '\n', 'utf8');

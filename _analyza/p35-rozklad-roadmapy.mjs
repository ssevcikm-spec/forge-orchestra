// p35-rozklad-roadmapy.mjs — ROZKLAD CENY ČTENÍ ROADMAPY (kde přesně mizí CPU).
//
// NAMĚŘENO (`p35-rozklad-tiku.mjs`): čtení `.forge/roadmap.json` (49 kB odpovědi)
// stojí **5,44 ms** parsování, kdežto 586 kB uzavřených PR jen **2,44 ms**.
// To je obráceně, než by člověk čekal — a znamená to, že drahá není velikost,
// ale CESTA: `github()` vrací obsah jako **base64** (media type `+json`) a kód
// ho dekóduje `Uint8Array.from(atob(...), c => c.charCodeAt(0))` — což je
// funkce VOLANÁ NA KAŽDÝ ZNAK. Tenhle skript měří obě cesty vedle sebe:
//   A) dnešní: `Accept: application/vnd.github+json` → JSON.parse → atob →
//      Uint8Array.from(mapFn) → TextDecoder → JSON.parse
//   B) `Accept: application/vnd.github.raw` → text → JSON.parse
// a rozloží A na jednotlivé kroky, aby bylo vidět, KTERÝ krok to stojí.
//
// Použití: node _analyza/p35-rozklad-roadmapy.mjs [--n 21] [--vystup x.txt]
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const argv = process.argv.slice(2);
const nIdx = argv.indexOf('--n');
const N = nIdx >= 0 ? Number(argv[nIdx + 1]) : 21;
const vIdx = argv.indexOf('--vystup');
const out = vIdx >= 0 ? argv[vIdx + 1] : '_analyza/p35-rozklad-roadmapy-vystup.txt';

const env = Object.fromEntries(
  readFileSync(join(WS, '.env'), 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }),
);
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const doklad = [];
const p = (x = '') => { console.log(x); doklad.push(x); };
const median = (a) => { const b = [...a].sort((x, y) => x - y); return b[Math.floor(b.length / 2)]; };
const mer = (fn) => { const c = []; let v = null; for (let i = 0; i < N; i++) { const t0 = process.hrtime.bigint(); v = fn(); c.push(Number(process.hrtime.bigint() - t0) / 1e6); } return { ms: median(c), v }; };

const h = await (await fetch(`${env.FORGE_URL}/health`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();
const repo = (h.targets || [])[0]?.repo;
if (!repo) { p('CHYBA: /health nehlásí žádnou aktivní hru — měřit není co'); process.exit(1); }
const games = await (await fetch(`${env.FORGE_URL}/games`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();
const soubor = (games.games || []).find((x) => x.repo === repo)?.roadmap_file || '.forge/roadmap.json';

p(`# P35 — ROZKLAD CENY ČTENÍ ROADMAPY — ${new Date().toISOString()}`);
p(`# hra: ${repo} · soubor: ${soubor} · medián z ${N} běhů`);
p('');

const url = `https://api.github.com/repos/${repo}/contents/${soubor}`;
const Hjson = { authorization: `Bearer ${PAT}`, accept: 'application/vnd.github+json', 'user-agent': 'forge-p35' };
const Hraw = { authorization: `Bearer ${PAT}`, accept: 'application/vnd.github.raw', 'user-agent': 'forge-p35' };

const aText = await (await fetch(url, { headers: Hjson })).text();
const bText = await (await fetch(url, { headers: Hraw })).text();
p(`## VELIKOST ODPOVĚDI`);
p(`  A) media type +json (base64): ${Buffer.byteLength(aText, 'utf8')} B`);
p(`  B) media type raw (text):     ${Buffer.byteLength(bText, 'utf8')} B`);
p('');

// ── A) dnešní cesta, rozložená na kroky ─────────────────────────────────────
let tree = null;
const k1 = mer(() => JSON.parse(aText));                    // obálka API (obsah base64)
const b64 = String(JSON.parse(aText).content || '').replace(/\n/g, '');
const k2 = mer(() => atob(b64));                            // base64 → binární řetězec
const bin = atob(b64);
const k3 = mer(() => Uint8Array.from(bin, (c) => c.charCodeAt(0)));   // ← funkce na KAŽDÝ znak
const byty = Uint8Array.from(bin, (c) => c.charCodeAt(0));
const k4 = mer(() => new TextDecoder().decode(byty));
const k5 = mer(() => JSON.parse(new TextDecoder().decode(byty)));
p('## A) DNEŠNÍ CESTA (media type +json, base64 přes `Uint8Array.from(mapFn)`)');
p(`  1. JSON.parse obálky API:              ${k1.ms.toFixed(2)} ms (${k1.v && Object.keys(k1.v).length} klíčů)`);
p(`  2. atob (base64 → binární řetězec):    ${k2.ms.toFixed(2)} ms (${bin.length} znaků)`);
p(`  3. Uint8Array.from(mapFn) PO ZNACÍCH:  ${k3.ms.toFixed(2)} ms  ← kandidát na vinu`);
p(`  4. TextDecoder.decode:                 ${k4.ms.toFixed(2)} ms`);
p(`  5. JSON.parse roadmapy:                ${k5.ms.toFixed(2)} ms`);
p(`  A CELKEM (součet kroků):               ${(k1.ms + k2.ms + k3.ms + k4.ms + k5.ms).toFixed(2)} ms`);
p('');

// ── A') táž cesta, ale dekódování INDEXOVANÝM CYKLEM (bez volání funkce na znak) ──
const k3b = mer(() => {
  const out8 = new Uint8Array(bin.length);
  for (let i = 0; i < bin.length; i++) out8[i] = bin.charCodeAt(i);
  return out8;
});
p(`## A') TÁŽ CESTA, ALE ` + '`for` cyklem místo `Uint8Array.from(mapFn)`');
p(`  3b. indexovaný cyklus:                 ${k3b.ms.toFixed(2)} ms`);
p(`  → úspora jen touhle záměnou:           ${(k3.ms - k3b.ms).toFixed(2)} ms`);
p('');

// ── B) cesta přes raw ───────────────────────────────────────────────────────
const k6 = mer(() => JSON.parse(bText));
p('## B) CESTA PŘES `Accept: application/vnd.github.raw`');
p(`  1. JSON.parse (žádné base64):          ${k6.ms.toFixed(2)} ms`);
const strom = k6.v;
p(`  položek v roadmapě: ${Array.isArray(strom?.grains || strom?.tasks) ? (strom.grains || strom.tasks).length : '—'}`);
p('');
const dnes = k1.ms + k2.ms + k3.ms + k4.ms + k5.ms;
p('## SROVNÁNÍ');
p(`  dnes (A):   ${dnes.toFixed(2)} ms`);
p(`  raw (B):    ${k6.ms.toFixed(2)} ms   → úspora ${(dnes - k6.ms).toFixed(2)} ms na tik`);
p(`  A s cyklem: ${(k1.ms + k2.ms + k3b.ms + k4.ms + k5.ms).toFixed(2)} ms (kdyby se měnil jen dekodér)`);
p('');
p(`[zapsano] ${out} (${doklad.join('\n').length} znaků)`);
writeFileSync(join(WS, out), doklad.join('\n') + '\n', 'utf8');

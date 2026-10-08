// P28/P29 — SONDA: SEDÍ FRONTA A CACHE NA SOUČASNOU ROADMAPU HRY?
//
// MĚŘÍ TŘI VĚCI (každá je tvrzení o stavu, proto se čte živě):
//   1) které granule má roadmapa v SOUBORU hry;
//   2) které má v CACHE (D1 `/roadmap`) — a které jsou v cache NAVÍC (osiřelé);
//   3) které ÚLOHY ve frontě patří granulím, jež v souboru UŽ NEJSOU.
// Přesně tyhle tři množiny rozhodují o tom, jestli orchestra „rozdává práci“,
// nebo spouští práci na granulích, které už neexistují.
//
// Použití: node _analyza/p29-sonda-fronta-vs-roadmapa.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const HRA = join(dirname(WS), 'uo-shadows');
const env = {};
for (const l of readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/)) {
  if (l.includes('=') && !l.trim().startsWith('#')) {
    const i = l.indexOf('=');
    env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
}
const URL = String(env.FORGE_URL || '').replace(/\/$/, '');
const volej = async (c) => (await fetch(URL + c, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();

const soubor = JSON.parse(readFileSync(join(HRA, '.forge', 'roadmap.json'), 'utf8')).grains || [];
const vSouboru = new Set(soubor.map((g) => g.id));

const cache = (await volej('/roadmap')).roadmap || [];
const vCache = new Set(cache.map((r) => r.item_id));

const fronta = (await volej('/queue')).tasks || [];

// ⚠ D1 ukládá `item_id` s prefixem hry (`uo-shadows/…`) — porovnává se holý název.
const holy = (x) => String(x || '').replace(/^[^/]+\//, '');

console.log('='.repeat(84));
console.log('1) ROADMAP Hry (SOUBOR): %d granul', soubor.length);
console.log('   ' + soubor.map((g) => g.id).join(', '));
console.log('\n2) CACHE D1 (/roadmap): %d řádků', cache.length);
const osirele = cache.filter((r) => !vSouboru.has(holy(r.item_id)));
console.log('   OSIŘELÉ (v cache, v souboru NE): %d', osirele.length);
for (const r of osirele) console.log(`      ${r.item_id}  status=${r.status} task=${r.task_id} pokusů=${r.attempts}`);
const chybejiciVCache = [...vSouboru].filter((id) => ![...vCache].some((c) => holy(c) === id));
console.log('   V SOUBORU, ale NE v cache: %d  %s', chybejiciVCache.length, chybejiciVCache.join(', ') || '—');

console.log('\n3) FRONTA /queue: %d úloh', fronta.length);
const podleStavu = {};
for (const t of fronta) podleStavu[t.status] = (podleStavu[t.status] || 0) + 1;
console.log('   stavy:', JSON.stringify(podleStavu));
// ⚠ POZOR (naměřeno 8. 10. 2026): `/queue` **nevrací `grain`** — jen id, title,
// kind, target, status, attempts, created_at. První verze téhle sondy čtla
// `t.grain` a hlásila „0 úloh na neexistující granule“ — **tichý falešný
// negativ** (kontrola, která nemá jak selhat). Granule se proto hledá
// v CACHE podle `task_id` → `item_id`; co se namapovat nedá, se VYPÍŠE.
const taskNaGrain = new Map();
for (const r of cache) if (r.task_id != null) taskNaGrain.set(r.task_id, holy(r.item_id));
const mimo = [];
let nenamapovano = 0;
for (const t of fronta) {
  const g = taskNaGrain.get(t.id);
  if (g === undefined) { nenamapovano++; continue; }
  if (!vSouboru.has(g)) mimo.push({ ...t, grain: g });
}
console.log('   úlohy NAMAPOVANÉ na granuli: %d z %d', fronta.length - nenamapovano, fronta.length);
console.log('   úlohy, které se namapovat NEDALY (nemají řádek v cache): %d %s',
  nenamapovano, nenamapovano ? '← to je taky nález, ne nula' : '');
console.log('   úlohy na granule, které V SOUBORU NEJSOU: %d', mimo.length);
for (const t of mimo.slice(0, 20)) {
  console.log(`      #${t.id} ${String(t.status).padEnd(8)} pokusů=${t.attempts ?? '—'}  ${t.grain}  ${String(t.title || '').slice(0, 40)}`);
}
const bezSize = soubor.filter((g) => g.size_lines === undefined || g.size_lines === null);
const bezModel = soubor.filter((g) => !g.model);
const bezAccept = soubor.filter((g) => !g.acceptance || !g.acceptance.length);
console.log('\n4) KONTRAKT ZADÁNÍ (co orchestra ke granuli potřebuje):');
console.log('   bez `size_lines`: %d/%d  %s', bezSize.length, soubor.length, bezSize.map((g) => g.id).join(', ') || '—');
console.log('   bez `model`:      %d/%d  %s', bezModel.length, soubor.length, bezModel.map((g) => g.id).join(', ') || '—');
console.log('   bez `acceptance`: %d/%d  %s', bezAccept.length, soubor.length, bezAccept.map((g) => g.id).join(', ') || '—');

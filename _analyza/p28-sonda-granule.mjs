// P28/P29 — SONDA: PROČ SELHÁVAJÍ GRANULE? (jen čtení: /failed, /queue, /roadmap)
//
// PROČ: „fronta nadále selhává granule“ je tvrzení o STAVU a musí se měřit živě
// (`AGENTS.md`). Tahle sonda vypíše u každé selhané úlohy její **granuli**,
// **payload**, počet pokusů a **konec `log_tail`** — tedy SKUTEČNÝ důvod, ne dohad.
// Zvlášť vypíše blokované granule a jejich pokusy (kvůli stropu `GRAIN_MAX_RUNS`).
//
// Použití: node _analyza/p28-sonda-granule.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const env = {};
const text = readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '');
for (const l of text.split(/\r?\n/)) {
  if (l.includes('=') && !l.trim().startsWith('#')) {
    const i = l.indexOf('=');
    env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
}
const URL = String(env.FORGE_URL || '').replace(/\/$/, '');
const TAJ = env.FORGE_SECRET;

async function volej(cesta) {
  const r = await fetch(URL + cesta, { headers: { 'User-Agent': 'forge-p28', 'x-forge-secret': TAJ } });
  const t = await r.text();
  try { return JSON.parse(t); } catch { return { chyba: r.status, telo: t.slice(0, 200) }; }
}

const f = await volej('/failed');
const ulohy = f.tasks || [];
console.log('='.repeat(86));
console.log('SELHANÉ ÚLOHY: %d   (každá = jeden pokus o granuli)', ulohy.length);
console.log('='.repeat(86));
for (const t of ulohy.slice(0, 12)) {
  const p = t.payload || {};
  console.log(`\n#${t.id}  ${String(t.title || '').slice(0, 60)}`);
  console.log(`     granule=${p.grain ?? p.item_id ?? '?'}  repo=${p.repo ?? '?'}  kind=${t.kind}  pokusů=${t.attempts}`);
  console.log(`     owns=${JSON.stringify(p.owns ?? null)}  size_lines=${p.size_lines ?? 'CHYBÍ'}  model=${p.model ?? 'CHYBÍ'}`);
  console.log(`     acceptance=${JSON.stringify(p.acceptance ?? null).slice(0, 100)}`);
  for (const r of (t.runs || []).slice(0, 2)) {
    const log = String(r.log_tail || '').split(/\r?\n/).filter((l) => l.trim());
    console.log(`     běh ${r.run_key} status=${r.status} pr=${r.pr_url ?? '—'}`);
    for (const l of log.slice(-6)) console.log(`        | ${l.slice(0, 150)}`);
  }
}

const q = await volej('/queue');
const podle = {};
for (const t of (q.tasks || [])) podle[t.status] = (podle[t.status] || 0) + 1;
console.log('\n' + '='.repeat(86));
console.log('FRONTA /queue: %d úloh  %s', (q.tasks || []).length, JSON.stringify(podle));
for (const t of (q.tasks || []).filter((x) => x.status !== 'done').slice(0, 15)) {
  console.log(`   #${t.id} ${String(t.status).padEnd(9)} pokusů=${t.attempts ?? '?'}  ${String(t.title || '').slice(0, 60)}`);
}

const rm = await volej('/roadmap');
const rows = rm.roadmap || [];
const st = {};
for (const r of rows) st[r.status] = (st[r.status] || 0) + 1;
console.log('\n' + '='.repeat(86));
console.log('ROADMAP (cache D1): %d granul  %s', rows.length, JSON.stringify(st));
for (const r of rows.filter((x) => x.status !== 'done')) {
  console.log(`   ${String(r.item_id).padEnd(28)} ${String(r.status).padEnd(9)} task=${r.task_id ?? '—'} stav_ulohy=${r.task_status ?? '—'} pokusů=${r.attempts ?? '—'}`);
}

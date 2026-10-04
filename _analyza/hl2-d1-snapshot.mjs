// Druhé kolo — zmrazení ŽIVÉHO stavu D1 přes endpointy conductora do JSON.
// Spuštění: node _analyza\hl2-d1-snapshot.mjs
// Vypisuje jen souhrny; plná data zapisuje do _analyza\hl2-d1-snapshot.json
import { readFileSync, writeFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
);
const BASE = env.FORGE_URL.replace(/\/$/, '');
const H = { 'x-forge-secret': env.FORGE_SECRET, accept: 'application/json' };

async function get(p) {
  const r = await fetch(BASE + p, { headers: H });
  const t = await r.text();
  try { return { status: r.status, j: JSON.parse(t) }; } catch { return { status: r.status, j: null, t: t.slice(0, 200) }; }
}

const ts = new Date().toISOString();
const snap = { mereno: ts, base: BASE };
for (const p of ['/health', '/games', '/roadmap', '/failed', '/queue', '/workers']) {
  const r = await get(p);
  snap[p] = r.j ?? r.t;
}
writeFileSync(`${WS}/_analyza/hl2-d1-snapshot.json`, JSON.stringify(snap, null, 2), 'utf8');

// ---- Souhrny ----
const rm = snap['/roadmap']?.roadmap ?? [];
const radkyD1 = rm.map((r) => ({ item: String(r.item_id).split('/').pop(), done: r.status, task: r.task_id, pokusy: r.attempts }));
const roadmapSoubor = JSON.parse(readFileSync(`${WS}/games/uo-shadows/.forge/roadmap.json`, 'utf8')).grains;

console.log(`# Snapshot ${ts}\n`);
console.log(`## D1 /roadmap: ${rm.length} řádků`);
console.log('   item                 D1.status   task  attempts');
for (const r of radkyD1) console.log(`   ${r.item.padEnd(20)} ${String(r.done).padEnd(11)} ${String(r.task).padEnd(5)} ${r.pokusy}`);
console.log(`   done v D1: ${rm.filter((r) => r.status === 'done').length}`);

console.log(`\n## roadmap.json: ${roadmapSoubor.length} granul`);
const doneSoubor = roadmapSoubor.filter((g) => g.done === true);
console.log(`   done:true v souboru: ${doneSoubor.length}`);

// ---- Porovnání: kdo je kde a kde se to rozchází ----
const d1 = new Map(radkyD1.map((r) => [r.item, r]));
const soubor = new Map(roadmapSoubor.map((g) => [g.id, g]));
const vsechny = [...new Set([...d1.keys(), ...soubor.keys()])].sort();

console.log('\n## POROVNÁNÍ soubor vs D1 vs main');
console.log('   granule               soubor   D1        shoda?');
let rozchodu = 0;
for (const id of vsechny) {
  const s = soubor.get(id);
  const d = d1.get(id);
  const sD = s ? (s.done === true ? 'done' : 'ne') : 'CHYBI';
  const dD = d ? d.done : 'CHYBI';
  const shoda = (sD === 'done' && dD === 'done') || (sD === 'ne' && dD !== 'done');
  if (!shoda) rozchodu++;
  console.log(`   ${id.padEnd(20)} ${sD.padEnd(8)} ${dD.padEnd(9)} ${shoda ? 'ok' : '<<< ROZCHOD'}`);
}
console.log(`\n   ROZCHODŮ: ${rozchodu} z ${vsechny.length} granul`);

// ---- Aktivní hra ----
console.log('\n## /games');
console.log('  ', JSON.stringify(snap['/games']?.games ?? snap['/games']));
console.log('\n## /queue tasky');
for (const t of snap['/queue']?.tasks ?? []) console.log(`   #${t.id} ${String(t.status).padEnd(8)} attempts=${t.attempts} ${String(t.title).slice(0, 45)}`);

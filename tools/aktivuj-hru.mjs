#!/usr/bin/env node
// AKTIVUJ HRU — přepne hru na aktivní a SLEDUJE, co conductor vydá.
//
// PROČ TO EXISTUJE (K4, 13. 10. 2026): hra se musí dát vypnout, aby ji plané
// tikání nespálilo pokusy (každý tik, který skončí `dispatch_failed`, je +1
// pokus granule — naměřeno: `world.coin` mělo `attempts: 5` za pět minut 403).
// A zase zapnout, až je cesta průchodná. Vypnutí i zapnutí dělá tenhle nástroj,
// aby to nebylo „ruční volání API, na které se zapomene“.
//
// CO DĚLÁ:
//   1) `POST /game/active {game_id, active:true}`,
//   2) sleduje `/health` (running/ready) a `/status` (nové běhy) — a jakmile
//      conductor něco vydá, vypíše to. Když vydá `dispatch_failed`, vypíše
//      DŮVOD (to je ta pojmenovaná příčina, kterou chceme vidět).
//
// POUŽITÍ:
//   node tools/aktivuj-hru.mjs --hra coin-picker            # aktivovat + sledovat 5 minut
//   node tools/aktivuj-hru.mjs --hra coin-picker --vypnout  # deaktivovat
//   node tools/aktivuj-hru.mjs --hra coin-picker --minuty 10

import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const ORCH = dirname(dirname(fileURLToPath(import.meta.url)));
const arg = (n, d = '') => { const i = process.argv.indexOf(n); return i >= 0 ? process.argv[i + 1] : d; };
const hra = arg('--hra');
const minuty = Number(arg('--minuty', '5'));
const vypnout = process.argv.includes('--vypnout');
if (!hra) { console.error('POUŽITÍ: node tools/aktivuj-hru.mjs --hra <game_id> [--vypnout] [--minuty N]'); process.exit(2); }

const env = Object.fromEntries(readFileSync(join(ORCH, '.env'), 'utf8').replace(/^\uFEFF/, '')
  .split(/\r?\n/).filter((l) => l.includes('='))
  .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]));
if (!env.FORGE_URL || !env.FORGE_SECRET) { console.error('CHYBA: .env neobsahuje FORGE_URL / FORGE_SECRET'); process.exit(2); }

const hlavicky = { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json' };
const api = (cesta, telo) => fetch(env.FORGE_URL + cesta, {
  method: telo ? 'POST' : 'GET',
  headers: telo ? hlavicky : { 'x-forge-secret': env.FORGE_SECRET },
  ...(telo ? { body: JSON.stringify(telo) } : {}),
}).then(async (r) => ({ stav: r.status, telo: await r.json().catch(() => ({})) }));

let r = await api('/game/active', { game_id: hra, active: !vypnout });
console.log(`POST /game/active {${hra}, active:${!vypnout}} → ${r.stav} ${JSON.stringify(r.telo)}`);
const stav = await api('/games');
for (const g of stav.telo.games || []) {
  console.log(`  ${String(g.game_id).padEnd(14)} active=${g.active} repo=${g.repo}`);
}
if (vypnout) process.exit(0);

console.log(`\nSleduji ${minuty} minut, co conductor vydá (Ctrl+C ukončí):`);
let videno = new Set();
const konec = Date.now() + minuty * 60_000;
while (Date.now() < konec) {
  const h = await (await fetch(`${env.FORGE_URL}/health`)).json();
  const s = await api('/status');
  const behy = (s.telo.runs || []).filter((x) => !videno.has(x.id));
  for (const b of behy) {
    videno.add(b.id);
    console.log(`  BĚH #${b.id} task=${b.task_id} "${b.title}" → ${b.status}`);
    if (b.summary) console.log(`      ${String(b.summary).slice(0, 220)}`);
    if (b.pr_url) console.log(`      PR: ${b.pr_url}`);
  }
  console.log(`  [${new Date().toISOString().slice(11, 19)}] tik=${h.last_cron_min}min ready=${h.ready} running=${h.running}`);
  if (behy.length) console.log('  → conductor VYDAL ÚLOHU (viz výš)');
  await new Promise((x) => setTimeout(x, 20_000));
}
console.log('\nHotovo. Nezapomeň: dokud hra běží, každý tik, který skončí dispatch_failed,'
  + ' spálí jeden pokus granule.');

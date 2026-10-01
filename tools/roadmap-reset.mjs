#!/usr/bin/env node
// Reset stavu roadmapy v conductoru (POST /roadmap/reset).
//
// Pouziti:
//   node orchestra\tools\roadmap-reset.mjs               # vsechny hry
//   node orchestra\tools\roadmap-reset.mjs uo-shadows    # jen jedna hra
//
// Kdy to potrebujes: kdyz se v repu hry zmeni ID granul v .forge/roadmap.json
// (napr. prechod default/* -> {game}/* po registraci hry). Stare radky
// v tabulce roadmap zustanou a conductor se jimi dal ridi, i kdyz v souboru
// uz nejsou -> orchestra pak pracuje na mrtvych granulich.
//
// Po resetu se stav obnovi sam v dalsim tiku (do 1 minuty).

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ORCH = join(HERE, '..');

const env = Object.fromEntries(
  readFileSync(join(ORCH, '.env'), 'utf8')
    .split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const game_id = process.argv[2];
const telo = game_id ? { game_id } : {};

const r = await fetch(`${env.FORGE_URL}/roadmap/reset`, {
  method: 'POST',
  headers: { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json' },
  body: JSON.stringify(telo),
});
const text = await r.text();
console.log(`POST /roadmap/reset ${game_id ? `(${game_id})` : '(vse)'} -> HTTP ${r.status}`);
console.log(text);
if (r.ok) {
  console.log('\nStav se obnovi v dalsim tiku conductora (do 1 minuty).');
  console.log('Zkontroluj: node orchestra\\tools\\status.mjs');
}

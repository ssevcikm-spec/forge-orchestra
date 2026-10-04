// Vypíše VŠECHNY řádky roadmapy z conductora (endpoint /roadmap vrací víc, než
// kolik jich stav-conductora.mjs ukáže). Čte se přes HTTP, ne z dokumentace.
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
);
const url = env.FORGE_URL.replace(/\/$/, '');
const r = await fetch(`${url}/roadmap`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
const j = await r.json();
const rows = j.roadmap ?? j.items ?? [];
console.log(`HTTP ${r.status} — řádků: ${rows.length}`);
console.log('grain'.padEnd(22) + 'status'.padEnd(10) + 'task_status'.padEnd(13) + 'pokusy  task   updated_at');
for (const x of rows.sort((a, b) => String(a.item_id).localeCompare(String(b.item_id)))) {
  const g = String(x.item_id).replace('uo-shadows/', '');
  console.log(
    g.padEnd(22) + String(x.status).padEnd(10) + String(x.task_status ?? '-').padEnd(13)
    + String(x.attempts ?? '-').padEnd(8) + String(x.task_id ?? '-').padEnd(7) + String(x.updated_at ?? '-'),
  );
}

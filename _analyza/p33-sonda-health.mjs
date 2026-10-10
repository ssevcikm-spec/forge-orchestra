// p33-sonda-health.mjs — ŽIVÝ TEP CRONU (Úkol B, nález H112).
//
// PROČ: brána „cron běží (čas)“ se do P33 ptala jen na `!!h.time`, tedy že
// služba odpovídá — o běhu cronu netvrdila nic, a když se 9. 10. 2026 tik
// zastavil, žádná brána to neohlásila. Sonda je KROK 4 důkazu: vezme ŽIVOU
// odpověď `/health`, ULOŽÍ ji (doklad pro pozdější přeměření) a zhodnotí ji
// **TÝMŽ predikátem, který používá brána** (`tools/cron-stav.mjs`) — ne jeho
// opisem (dvě implementace téhož = druhá pravda).
//
// Použití: node _analyza/p33-sonda-health.mjs [vystup.txt]
//   exit 0 = predikát OK (cron tiká), exit 1 = predikát hlásí vadu, exit 2 = chyba
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { zhodnotCron, VYCHOZI_LIMIT_MIN } from '../tools/cron-stav.mjs';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const out = process.argv[2] ?? '_analyza/p33-health-po-vystup.txt';

const env = Object.fromEntries(
  readFileSync(join(WS, '.env'), 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }),
);

let h;
try {
  const r = await fetch(`${env.FORGE_URL}/health`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  h = { http_status: r.status, ...(await r.json()) };
} catch (e) {
  console.log(`CHYBA /health se nepodařilo zavolat: ${String(e)}`);
  process.exit(2);
}

// Doklad se ukládá i s HTTP kódem — „HTTP 200 není důkaz“, ale chybět nemá.
writeFileSync(join(WS, out), JSON.stringify(h, null, 2) + '\n', 'utf8');

const v = zhodnotCron(h, Date.now(), VYCHOZI_LIMIT_MIN);
console.log(`# /health HTTP ${h.http_status} · doklad ${out} (${JSON.stringify(h).length} B)`);
console.log(`# last_tick=${h.last_tick ?? '—'} · zdroj=${h.last_tick_zdroj ?? '—'}`);
console.log(`${v.ok ? 'OK   ' : 'CHYBA'} ${v.duvod}`);
process.exit(v.ok ? 0 : 1);

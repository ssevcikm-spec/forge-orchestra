// p35-sonda-health.mjs — ŽIVÝ /health P35: posílá služba POKUS o tik? (Úkol A2)
//
// PROČ VLASTNÍ SONDA (a ne opis `p33-sonda-health.mjs`): P35 musí ověřit, že
// nasazená verze P34 posílá `last_cron_pokus` (+ `_min`) — tedy že vada
// „trigger NEDORAZIL“ a „tik NEDOBĚHL“ je na ŽIVÉ službě ROZLIŠITELNÁ.
// Sonda proto:
//   1. vezme ŽIVOU odpověď `/health` a ULOŽÍ ji celou (doklad pro přeměření),
//   2. ověří PŘÍTOMNOST obou polí (a že `last_cron` zůstal — zpětná kompatibilita),
//   3. zhodnotí ji TÝMŽ predikátem, který používá brána (`tools/cron-stav.mjs`),
//   4. když pokus tiká a `last_cron` je starý, ŘEKNE TO JAKO VÝPADEK (to je
//      přesně to, co má oprava P34 umět) — a vypíše, které jméno vady predikát
//      použil (dvě jména vady se nesmí splést).
//
// Použití: node _analyza/p35-sonda-health.mjs [vystup.txt]
//   exit 0 = predikát OK (tik dobíhá), exit 1 = predikát hlásí vadu (stav služby),
//   exit 2 = chyba měření (nedostupné /health)
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';
import { zhodnotCron, VYCHOZI_LIMIT_MIN } from '../tools/cron-stav.mjs';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const out = process.argv[2] ?? '_analyza/p35-health-vystup.txt';

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

writeFileSync(join(WS, out), JSON.stringify(h, null, 2) + '\n', 'utf8');

const maPokus = 'last_cron_pokus' in h && 'last_cron_pokus_min' in h;
const maTep = 'last_cron' in h && 'last_cron_min' in h;
const v = zhodnotCron(h, Date.now(), VYCHOZI_LIMIT_MIN);

console.log(`# /health HTTP ${h.http_status} · doklad ${out} (${JSON.stringify(h).length} B)`);
console.log(`# last_cron=${h.last_cron ?? '—'} (${h.last_cron_min ?? '—'} min) · ` +
  `last_cron_pokus=${h.last_cron_pokus ?? '—'} (${h.last_cron_pokus_min ?? '—'} min)`);
console.log(`# ready=${h.ready} running=${h.running} games=${h.games}`);
console.log(`${maPokus ? 'OK   ' : 'CHYBA'} /health posílá POKUS o tik (last_cron_pokus + _min)`);
console.log(`${maTep ? 'OK   ' : 'CHYBA'} /health posílá i DOKONČENÝ tep (last_cron + _min)`);
console.log(`${v.ok ? 'OK   ' : 'CHYBA'} predikát brány: ${v.duvod}`);
process.exit(!maPokus || !maTep ? 2 : (v.ok ? 0 : 1));

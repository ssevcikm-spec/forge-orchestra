// p35-profil-cpu.mjs — ŽIVÝ CPU PROFIL SLUŽBY: kolik CPU stojí KTERÝ endpoint.
//
// PROČ: `wrangler tail` hlásí u každé invokace `cpuTime`, ale cron tik je jedna
// velká černá skříňka. Služba má ale i MENŠÍ endpointy, jejichž práci známe
// z kódu (`/poll` = jeden SELECT a předčasný návrat; `/health` = 6 SELECTů +
// serializace; `/status`, `/queue`, … = čtecí dotazy). Když se tytéž endpointy
// zavolají ŽIVĚ a spárují se s eventy v tailu, dostane se **rozklad podle
// zdroje** — a teprve pak má smysl tvrdit, co tik zdržuje.
//
// CO NEDĚLÁ: nečte tail sám (doklad z tailu vzniká mimo, přes `cmd /c "… > soubor"`,
// protože PowerShell pipeline u wrangleru NEDODÁ data — H161). Tenhle skript
// jen ODVYSÍLÁ baterii požadavků a vypíše, co a kdy poslal; párování dělá
// `_analyza/p35-tail-rozbor.py` podle `event.request.url`.
//
// ⚠ `POST /tick` je ZÁSAH DO STAVU (dispatchuje práci a pálí kvótu) — proto se
// posílá jen s `--tik` a vypíše se to do dokladu. Když jsou všechny připravené
// granule nad stropem (`GRAIN_MAX_RUNS`), tik nevydá nic; to se z výstupu pozná.
//
// Použití: node _analyza/p35-profil-cpu.mjs [--tik] [--n 3] [--vystup x.txt]
import { readFileSync, writeFileSync, appendFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const argv = process.argv.slice(2);
const chciTik = argv.includes('--tik');
const nIdx = argv.indexOf('--n');
const N = nIdx >= 0 ? Number(argv[nIdx + 1]) : 3;
const vIdx = argv.indexOf('--vystup');
const out = vIdx >= 0 ? argv[vIdx + 1] : '_analyza/p35-profil-cpu-vystup.txt';

const env = Object.fromEntries(
  readFileSync(join(WS, '.env'), 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }),
);

const doklad = [];
const p = (x = '') => { console.log(x); doklad.push(x); };

p(`# P35 — živý CPU profil služby — ${new Date().toISOString()}`);
p(`# cíl: ${env.FORGE_URL}`);
p(`# opakování na endpoint: ${N}${chciTik ? ' · VČETNĚ POST /tick (zásah do stavu!)' : ' · bez /tick'}`);
p('');

const baterie = [
  { m: 'GET', c: '/health' },
  { m: 'GET', c: '/status' },
  { m: 'GET', c: '/queue' },
  { m: 'GET', c: '/roadmap' },
  { m: 'GET', c: '/workers' },
  { m: 'GET', c: '/games' },
  { m: 'POST', c: '/poll' },
];
if (chciTik) baterie.push({ m: 'POST', c: '/tick' });

p('## ODVYSÍLANÉ POŽADAVKY (klient)');
p('  # | metoda | cesta        | HTTP | klient ms | délka odpovědi');
let i = 0;
for (let kolo = 0; kolo < N; kolo++) {
  for (const b of baterie) {
    i++;
    const t0 = Date.now();
    let status = '?';
    let delka = 0;
    try {
      const r = await fetch(`${env.FORGE_URL}${b.c}`, {
        method: b.m,
        headers: { 'x-forge-secret': env.FORGE_SECRET },
      });
      const text = await r.text();
      status = r.status;
      delka = text.length;
    } catch (e) {
      status = `CHYBA ${String(e).slice(0, 60)}`;
    }
    p(`  ${String(i).padStart(2)} | ${b.m.padEnd(6)} | ${b.c.padEnd(12)} | ${String(status).padEnd(4)} | ` +
      `${String(Date.now() - t0).padStart(9)} | ${delka} B`);
  }
}
p('');
p('## JAK PÁROVAT (cpuTime není tady — je v tailu)');
p('  python _analyza/p35-tail-rozbor.py _analyza/p35-tail-raw-vystup.txt --od <ISO čas prvního požadavku>');
p('');
p(`[zapsano] ${out} (${doklad.join('\n').length} znaků)`);
writeFileSync(join(WS, out), doklad.join('\n') + '\n', 'utf8');

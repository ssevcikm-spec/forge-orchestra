// p34-sonda-cron-sleduj.mjs — SLEDOVÁNÍ TEPU CRONU V ČASE (P34, H156).
//
// PROČ: `wrangler tail` řekne, že cron event DORAZÍ a umře na CPU limitu.
// Otázka druhá je, jestli to dělá KAŽDÝ tik, nebo jen některý — a to se
// pozná z toho, jestli se `last_cron` v `/health` někdy pohne. Sonda proto
// každých `interval` sekund zapíše JEDEN ŘÁDEK s živými hodnotami; změna
// `last_cron` = tik DOBĚHL.
//
// Použití: node _analyza/p34-sonda-cron-sleduj.mjs [minuty] [interval-s] [vystup]
// ⚠ Třetí argument je cesta k dokladu — dá se tím zapsat MIMO strom, aby sonda
// mohla běžet i BĚHEM PLNÉHO BĚHU MĚŘIDLA (během něj se do stromu nepsuje, H154).
import { readFileSync, appendFileSync } from 'node:fs';
import { dirname, join, isAbsolute } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const minuty = Number(process.argv[2] || 20);
const interval = Number(process.argv[3] || 20);
const argVystup = process.argv[4] || '_analyza/p34-sledovani-tepu-vystup.txt';
const OUT = isAbsolute(argVystup) ? argVystup : join(WS, argVystup);

const env = Object.fromEntries(
  readFileSync(join(WS, '.env'), 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; }),
);

appendFileSync(OUT, `# start ${new Date().toISOString()} · ${minuty} min · interval ${interval} s\n`, 'utf8');
let predchozi = null;
const konec = Date.now() + minuty * 60000;
let pokusu = 0;
while (Date.now() < konec) {
  const cas = new Date().toISOString();
  let radek;
  try {
    const r = await fetch(`${env.FORGE_URL}/health`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
    const h = await r.json();
    radek = `${cas} http=${r.status} last_cron=${h.last_cron} min=${h.last_cron_min}`
      + ` zdroj=${h.last_tick_zdroj} ready=${h.ready} running=${h.running}`;
    if (predchozi && h.last_cron !== predchozi) {
      radek += `  <<< ZMENA: last_cron se pohnul (tik DOBEHL)`;
      console.log(radek);
    }
    predchozi = h.last_cron;
  } catch (e) {
    radek = `${cas} CHYBA ${String(e).slice(0, 120)}`;
  }
  appendFileSync(OUT, radek + '\n', 'utf8');
  pokusu++;
  await new Promise((s) => setTimeout(s, interval * 1000));
}
appendFileSync(OUT, `# konec ${new Date().toISOString()} · ${pokusu} vzorku\n`, 'utf8');
console.log(`# hotovo: ${pokusu} vzorku do ${OUT}`);

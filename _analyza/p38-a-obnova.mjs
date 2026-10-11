// p38-a-obnova.mjs — DOKLAD OBNOVY TIKU: kdy přesně přestaly invokace umírat (P38).
//
// PROČ: P37 naměřila, že cron tik umíral (`exceededCpu`), a P38 má ověřit a
// ZAPSAT obnovu. „Obnova" musí být POJMENOVANÁ NA MINUTU: Cloudflare Analytics
// (`workersInvocationsAdaptive`, rozměr `datetime` = 1 minuta) dá minuty, ve
// kterých invokace umíraly, a první minutu po nasazení #40 (`18:39:20Z`), ve
// které už neumírala ani jedna. To je jiný důkaz než „teď to běží".
//
// Vstup: `_analyza/p38-b-cf-analytika-raw-vystup.txt` (výstup p38-b-cf-analytika.mjs).
// Použití: node _analyza/p38-a-obnova.mjs
// Exit 0 = měřeno; 1 = vstup chybí/prázdný (měření NEPROBĚHLO).

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const VSTUP = join(WS, '_analyza', 'p38-b-cf-analytika-raw-vystup.txt');
const OUT = join(WS, '_analyza', 'p38-a-obnova-vystup.txt');
const NASZENI = '2026-10-11T18:39:20Z';   // created_at běhu deploy.yml #40 (GitHub API)
const NASZENI_DOKONCENO = '2026-10-11T18:39:44Z';

const radky = [];
const p = (x = '') => { radky.push(x); console.log(x); };

let raw;
try { raw = JSON.parse(readFileSync(VSTUP, 'utf8')); } catch (e) {
  console.log(`CHYBA: vstup ${VSTUP} nejde přečíst (${String(e).slice(0, 80)}) — měření NEPROBĚHLO`);
  process.exit(1);
}
const data = (raw.radky || []).filter((x) => x.dimensions?.datetime);
if (!data.length) { console.log('CHYBA: v datech nejsou žádné řádky — měření NEPROBĚHLO'); process.exit(1); }

p(`# p38-a — obnova tiku po nasazení #40 (${NASZENI}) — doklad vyroben ${new Date().toISOString()}`);
p(`# zdroj: ${VSTUP.split(/[\\/]/).pop()} (měřeno ${raw.mereno}, okno od ${raw.od}, ${raw.hodin} h)`);
p('');

const minuta = new Map();  // datetime -> {success, exceededResources, jine}
for (const x of data) {
  const m = minuta.get(x.dimensions.datetime) || { success: 0, exceededResources: 0, jine: 0 };
  const st = x.dimensions.status;
  if (st === 'success') m.success += x.sum.requests;
  else if (st === 'exceededResources') m.exceededResources += x.sum.requests;
  else m.jine += x.sum.requests;
  minuta.set(x.dimensions.datetime, m);
}

const klice = [...minuta.keys()].sort();
const umirajici = klice.filter((k) => minuta.get(k).exceededResources > 0);
const posledniUmirajici = umirajici.length ? umirajici[umirajici.length - 1] : null;

p('## MINUTY, VE KTERÝCH INVOKACE UMÍRALY (`exceededResources`) — POSLEDNÍCH 60');
for (const k of umirajici.slice(-60)) {
  p(`   ${k}  exceeded=${minuta.get(k).exceededResources}  success=${minuta.get(k).success}`);
}
p(`   → minut s umírající invokací v okně: ${umirajici.length}`);
p(`   → POSLEDNÍ taková minuta: ${posledniUmirajici ?? '(žádná)'}`);
p('');

p('## MINUTY PO NASAZENÍ #40 (18:36Z .. konec okna)');
let poNasazeni = 0, poNasazeniUmirajici = 0;
for (const k of klice.filter((k) => k >= '2026-10-11T18:36')) {
  const m = minuta.get(k);
  if (k >= NASZENI) {
    poNasazeni++;
    if (m.exceededResources > 0) poNasazeniUmirajici++;
  }
  p(`   ${k}  success=${String(m.success).padStart(3)}  exceeded=${String(m.exceededResources).padStart(3)}  jine=${m.jine}`);
}
p('');
p(`## SOUHRN`);
p(`   nasazení #40: created ${NASZENI}, dokončeno ${NASZENI_DOKONCENO}`);
p(`   minut od nasazení (vč. minuty nasazení): ${poNasazeni}, z toho s exceededResources: ${poNasazeniUmirajici}`);
if (poNasazeniUmirajici === 0 && posledniUmirajici) {
  p(`   ✓ PO NASAZENÍ NEUMŘELA ANI JEDNA INVAKACE (poslední úmrtí bylo ${posledniUmirajici})`);
} else if (!posledniUmirajici) {
  p('   ⚠ V CELÉM OKNĚ NENÍ ANI JEDNA UMÍRAJÍCÍ INVAKACE — to NENÍ důkaz obnovy,');
  p('     ale důkaz, že se okno netrefilo do výpadku (nula není úspěch, dokud není čeho si všimnout).');
} else {
  p(`   ✗ PO NASAZENÍ UMÍRALY INVAKACE JEŠTĚ ${poNasazeniUmirajici}× — obnova NENÍ úplná`);
}

// Kolik minut výpadku bylo a jak dlouho (souvislost)
if (umirajici.length) {
  p('');
  p('## ROZSAH VÝPADKU');
  p(`   od ${umirajici[0]} do ${posledniUmirajici}`);
  const rozestupy = [];
  for (let i = 1; i < umirajici.length; i++) {
    rozestupy.push((Date.parse(umirajici[i]) - Date.parse(umirajici[i - 1])) / 60000);
  }
  const diry = rozestupy.filter((d) => d > 1);
  p(`   minut celkem: ${umirajici.length}, děr (minut bez úmrtí uvnitř): ${diry.length}${diry.length ? ' → ' + diry.slice(0, 10).join(', ') + ' min' : ''}`);
}

writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
console.log(`\n[zapsano] ${OUT}`);
process.exit(poNasazeniUmirajici === 0 && posledniUmirajici ? 0 : 1);

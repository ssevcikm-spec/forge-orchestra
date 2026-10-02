#!/usr/bin/env node
// Hlídá, že soubory, které se KOPÍRUJÍ ze šablony orchestra do her, neujíždějí.
//
// PROČ TO EXISTUJE (naměřeno 30. 9. 2026): orchestra drží šablonu v
// `repo/.forge/` a `repo/.github/workflows/`, ale herní repa mají VLASTNÍ kopie
// (GitHub Actions čte soubory z repa hry). Když se opraví šablona a zapomene
// synchronizovat hra, běhy dál používají starou verzi – přesně to se stalo
// s `agent.yml` (chyběl import assetů) a `pick-provider.mjs`.
//
// Použití:
//   node orchestra\tools\kontrola-driftu.mjs
//   node orchestra\tools\kontrola-driftu.mjs --sync     # rovnou zkopíruje šablona → hra

import { readFileSync, existsSync, copyFileSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'C:/Users/Ssevc/Local-Deepseek';
const SABLONA = join(ROOT, 'orchestra/repo');

// Co se kopíruje ze šablony do hry. Klíč = cesta v šabloně i ve hře (stejná).
//
// POZOR – CO TU ZÁMĚRNĚ NENÍ (a proč). Tenhle seznam je zároveň DEKLARACE
// VLASTNICTVÍ: co v něm je, patří orchestře a hra to jen dostane; co v něm
// není, patří HŘE. Když sem někdo přidá soubor z druhého seznamu, přepíše
// hře její data – a to je přesně ta vada, kterou projekt řeší (S4/S5).
//
//   .forge/vision-profile.json  – profil je PER-GAME. Šablona má `hra: null`
//                                 a prázdný `popis_stylu`; hra má svoje.
//                                 Naměřeno 1. 10. 2026: šablona v sobě měla
//                                 natvrdo `uo-shadows` a dědila to každá nová
//                                 hra. Sync sem by hru o její profil připravil.
//   .forge/roadmap.json         – PLÁN JE HRY. Šablona má prázdný (`grains: []`),
//                                 hra má svoje granule. Sync by hru vymazal.
//   .forge/providers.json       – zdroj pravdy je ORCHESTRA a čte se za běhu
//                                 (fetch v `pick-provider.mjs`), lokální kopie
//                                 ve hře je jen záloha. Kopírovat ji sem by
//                                 z ní udělalo druhou pravdu.
//   .forge/check-schema.py      – v tomhle seznamu NENÍ, ale jeho shodu hlídá
//                                 `tools/test-check-schema.py` (porovnává hash
//                                 obou kopií) – ověřeno 1. 10. 2026: hashe
//                                 shodné. Tady chybí jen proto, že se sem
//                                 nepřidal; `--sync` by ho tedy nesjednotil.
//                                 Není to díra v ochraně, jen v pohodlí.
const SOUBORY = [
  '.forge/pick-provider.mjs',
  '.forge/files-to-edit.mjs',
  '.forge/node/provider-choice.mjs',
  '.forge/node/provider-choice.test.mjs',
  '.forge/node/worker.mjs',
  '.forge/check-assets.py',
  '.forge/check-wiring.py',
  '.forge/install-godot.sh',
  '.github/workflows/agent.yml',
  '.github/workflows/ci.yml',
  '.github/workflows/model-check.yml',
  'CONVENTIONS.md',
];

// Hry, které se kontrolují (klon v games/).
const HRY = ['uo-shadows'];

// U YAML se porovnává STRUKTURA, ne text. Hra má v komentářích konkrétní
// naměřené hodnoty a delší vysvětlivky (to je žádoucí), takže textové
// porovnání hlásilo „rozdíl" i když byly kroky a vstupy stejné. Zajímá nás,
// na čem skutečně záleží: jaké kroky workflow má, jaké má vstupy a co předává
// do prostředí.
const jeYaml = (f) => f.endsWith('.yml') || f.endsWith('.yaml');

/**
 * Vytáhne z workflow to podstatné: vstupy, názvy kroků a U KTERÉHO KROKU je
 * který klíč `env`.
 *
 *  ⚠ PROČ `envKlice` = MAPA `KLÍČ → [jména kroků]` (opraveno 2. 10. 2026):
 *  Do té doby se všechny klíče `env` sypaly do jednoho plochého pole. To je
 *  slepé k TOMU, NA ČEM NEJVÍC ZÁLEŽÍ — ke kterému kroku klíč patří, protože
 *  `env:` na úrovni kroku platí JEN pro ten krok. Naměřeno: `FORGE_ATTEMPT`
 *  byl v obou kopiích (33 výskytů, 16 unikátních klíčů — množiny SHODNÉ), ale
 *  v herním repu byl na kroku „Vyber bezplatného poskytovatele LLM" místo na
 *  „Spusť agenta". `pick-provider.mjs` (ř. 129, 132) ho přitom čte
 *  z `process.env`, takže rotace modelů podle čísla pokusu byla v herním repu
 *  MRTVÁ — a drift hlásil `OK (struktura)`. Táž třída jako S27: zelená nad
 *  tím, co se neměří.
 *
 *  Porovnává se proto podle KLÍČE, ne podle pozice kroku: kopie mají různý
 *  počet kroků (šablona má parsování a class_name jako dva kroky, hra je má
 *  v jednom), takže pořadí se posouvá a porovnání podle indexu hlásí falešné
 *  rozdíly u nesouvisejících kroků. Mapa „klíč → kde je" je na posunu nezávislá.
 *  Podle JMÉNA kroku se porovnávat nedá — kopie mají jména jiná i tam, kde
 *  dělají totéž („Kontrola parsování (rychlá brána)" vs. „… GDScriptu (…)").
 */
function strukturaWorkflow(text) {
  const radky = text.split('\n');
  const vstupy = [];
  const kroky = [];
  const envKlice = {}; // KLÍČ -> [jména kroků, které ho mají v env]
  let vVstupech = false;
  let vEnv = false;
  let aktualni = '(úvod)';
  for (const l of radky) {
    const bezKomentare = l.replace(/\s+#.*$/, '');
    if (/^\s{2,}workflow_dispatch:/.test(bezKomentare)) { vVstupech = true; vEnv = false; continue; }
    if (/^\s{2,}(permissions|concurrency|jobs):/.test(bezKomentare)) { vVstupech = false; }
    if (/^\s+- name:\s*(.+)$/.test(bezKomentare)) {
      aktualni = bezKomentare.replace(/^\s+- name:\s*/, '').trim();
      kroky.push(aktualni);
      vEnv = false;
      continue;
    }
    if (/^\s+env:\s*$/.test(bezKomentare)) { vEnv = true; continue; }
    if (vVstupech) {
      const m = /^\s{6}([a-z_]+):\s*$/.exec(bezKomentare);
      if (m) vstupy.push(m[1]);
    }
    if (vEnv) {
      const m = /^\s+([A-Z_]+):/.exec(bezKomentare);
      if (m) {
        if (!envKlice[m[1]]) envKlice[m[1]] = [];
        if (!envKlice[m[1]].includes(aktualni)) envKlice[m[1]].push(aktualni);
        continue;
      }
      if (/^\s+(run|uses|with):/.test(bezKomentare)) vEnv = false;
    }
  }
  return JSON.stringify({ vstupy, kroky, envKlice }, null, 1);
}

const sync = process.argv.includes('--sync');
const normalizuj = (cesta) =>
  readFileSync(cesta, 'utf8').replace(/\r\n/g, '\n'); // klon má CRLF, šablona LF

let rozdilu = 0;
let zkontrolovano = 0;

for (const hra of HRY) {
  const cil = join(ROOT, 'games', hra);
  if (!existsSync(cil)) {
    console.log(`\n${hra}: klon neexistuje (${cil}) – přeskakuji`);
    continue;
  }
  console.log(`\n=== ${hra} ===`);
  for (const f of SOUBORY) {
    const a = join(SABLONA, f);
    const b = join(cil, f);
    if (!existsSync(a)) { console.log(`  ? ${f}: v šabloně není`); continue; }
    if (!existsSync(b)) {
      console.log(`  CHYBÍ ve hře: ${f}`);
      rozdilu++;
      if (sync) { copyFileSync(a, b); console.log(`    → zkopírováno`); }
      continue;
    }
    zkontrolovano++;
    const stejne = jeYaml(f)
      ? strukturaWorkflow(normalizuj(a)) === strukturaWorkflow(normalizuj(b))
      : normalizuj(a) === normalizuj(b);
    if (stejne) {
      console.log(`  OK   ${f}${jeYaml(f) ? ' (struktura)' : ''}`);
    } else {
      rozdilu++;
      console.log(`  ROZDÍL ${f}`);
      if (jeYaml(f)) {
        // Ukaž, co konkrétně se liší – ať je vidět, jestli jde o práci, nebo šum.
        const sa = JSON.parse(strukturaWorkflow(normalizuj(a)));
        const sb = JSON.parse(strukturaWorkflow(normalizuj(b)));
        for (const klic of ['vstupy', 'kroky']) {
          const jenA = sa[klic].filter((x) => !sb[klic].includes(x));
          const jenB = sb[klic].filter((x) => !sa[klic].includes(x));
          if (jenA.length) console.log(`    jen v šabloně (${klic}): ${jenA.join(', ')}`);
          if (jenB.length) console.log(`    jen ve hře (${klic}): ${jenB.join(', ')}`);
        }
        // NOVÉ (2. 10. 2026): u každého klíče `env` se porovnává, NA KTERÉM
        // KROKU je. Do té doby byl `env` plochý seznam a přesun klíče na jiný
        // krok (který rozhoduje o tom, jestli ho skript dostane) zůstal
        // neviditelný. Porovnává se podle klíče, ne podle pozice kroku — obě
        // kopie mají různý počet kroků, takže indexy se posouvají.
        const kliceA = sa.envKlice, kliceB = sb.envKlice;
        for (const k of [...new Set([...Object.keys(kliceA), ...Object.keys(kliceB)])].sort()) {
          const kdeA = (kliceA[k] || []).join(' | ');
          const kdeB = (kliceB[k] || []).join(' | ');
          if (kdeA !== kdeB) {
            console.log(`    env ${k}:`);
            console.log(`      šablona: ${kdeA || '(nikde)'}`);
            console.log(`      hra:     ${kdeB || '(nikde)'}`);
          }
        }
      }
      if (sync) { copyFileSync(a, b); console.log(`    → přepsáno šablonou`); }
    }
  }
}

console.log(`\nZkontrolováno souborů: ${zkontrolovano}, rozdílů: ${rozdilu}`);
if (rozdilu && !sync) {
  console.log('Spusť s --sync pro sjednocení (šablona → hra), pak zkontroluj git diff.');
  process.exitCode = 1;
}

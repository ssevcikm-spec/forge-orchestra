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

/** Vytáhne z workflow to podstatné: vstupy, názvy kroků, klíče env. */
function strukturaWorkflow(text) {
  const radky = text.split('\n');
  const vstupy = [];
  const kroky = [];
  const envKlice = [];
  let vVstupech = false;
  let vEnv = false;
  for (const l of radky) {
    const bezKomentare = l.replace(/\s+#.*$/, '');
    if (/^\s{2,}workflow_dispatch:/.test(bezKomentare)) { vVstupech = true; vEnv = false; continue; }
    if (/^\s{2,}(permissions|concurrency|jobs):/.test(bezKomentare)) { vVstupech = false; }
    if (/^\s+- name:\s*(.+)$/.test(bezKomentare)) { kroky.push(RegExp.$1.trim()); vEnv = false; continue; }
    if (/^\s+env:\s*$/.test(bezKomentare)) { vEnv = true; continue; }
    if (vVstupech) {
      const m = /^\s{6}([a-z_]+):\s*$/.exec(bezKomentare);
      if (m) vstupy.push(m[1]);
    }
    if (vEnv) {
      const m = /^\s+([A-Z_]+):/.exec(bezKomentare);
      if (m) { envKlice.push(m[1]); continue; }
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
        for (const klic of ['vstupy', 'kroky', 'envKlice']) {
          const jenA = sa[klic].filter((x) => !sb[klic].includes(x));
          const jenB = sb[klic].filter((x) => !sa[klic].includes(x));
          if (jenA.length) console.log(`    jen v šabloně (${klic}): ${jenA.join(', ')}`);
          if (jenB.length) console.log(`    jen ve hře (${klic}): ${jenB.join(', ')}`);
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

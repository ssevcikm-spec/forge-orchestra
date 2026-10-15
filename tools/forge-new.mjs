#!/usr/bin/env node
// FORGE NEW — založí novou hru: orchestrační soubory ze šablony + herní skeleton.
//
// PROČ TO EXISTUJE (K4, 13. 10. 2026): hru Coin-Picker jsem musel postavit RUČNĚ
// — kopírovat `repo/`, psát `project.godot`, `main.tscn`, testy, assety a roadmapu.
// A naměřilo se při tom, že to ručně nejde dobře:
//   * `export_presets.cfg` v šabloně NEBYL, takže první hra spadla na posledním
//     kroku CI (export) — a to až po všech ostatních branách,
//   * šablona nemá skeleton, takže hra založená jen z `repo/` nemá co spustit
//     (`ci.yml` volá `tests/run_tests.gd` a `check-schema.py` čte `assets/spec.json`),
//   * nástroje v `.forge/node/` se musí do hry zkopírovat, ale drift je nehlídá.
//
// CO DĚLÁ:
//   1) zkontroluje název a cíl (neexistující nebo prázdný adresář),
//   2) zkopíruje `repo/` = orchestraci (.forge, .github, CONVENTIONS.md, CONVENTIONS/),
//   3) přepíše herní soubory ze `skeleton/` (projekt, scénu, skripty, testy, assety),
//   4) PŘEPÍŠE název hry ve všech textových souborech a RESETUJE roadmapu
//      (odstraní `done`/`_done` — nová hra nesmí tvrdit, že má hotové granule,
//      které dokončil pilot JINÉ hry; naměřeno: skeleton nese `_done` s číslem
//      PR z Coin-Pickeru a to je v nové hře nepravdivé tvrzení o stavu),
//   5) s `--kontrola` spustí brány hry (schéma, assety, zapojení, rozpočet granulí
//      a testy, když je Godot).
//
// POUŽITÍ:
//   node tools/forge-new.mjs --nazev moje-hra --cil E:\Workspaces\moje-hra
//   node tools/forge-new.mjs --nazev test --cil .tmp/test --kontrola --whatif
//
// NÁSLEDUJE (co nástroj NEDĚLÁ, protože to patří člověku nebo jinému nástroji):
//   * založit repo na GitHubu a pushnout (git init/push),
//   * vystavit secrety hry (FORGE_PAT, FORGE_WEBHOOK_SECRET, klíče poskytovatelů),
//   * zaregistrovat hru v conductoru (POST /game).

import { readFileSync, writeFileSync, mkdirSync, existsSync, readdirSync, copyFileSync, statSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname, basename } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(__dir);
const SABLONA = join(ORCH, 'repo');
const SKELETON = join(ORCH, 'skeleton');

// Co se NEKOPÍRUJE ze šablony: tajemství a cache.
const SKIP_NAZVY = new Set(['.env', 'provider.env', 'provider.json', '__pycache__', '.git']);

// ⚠ CO SE DO HRY NEVEZE, PROTOŽE TO MĚŘÍ ŠABLONU (K6, 14. 10. 2026 — naměřeno;
//   číslo u `core.game` OPRAVENO 14. 10. 2026 v K7 — HANDOFF.md §73.2, nález H206):
//   `priprava.test.mjs` má oddíl K3, který nad `roadmap.pilot.json` vyžaduje
//   `REQUEST_FITS` proti stropu groq (8 000 t). Pilotní granule ale vlastní
//   SKUTEČNÉ soubory (`scripts/player.gd`, `scripts/game.gd` …), takže rozpočet
//   závisí na velikosti stromu: v šabloně (téměř prázdné soubory) vyjde 5/5
//   `REQUEST_FITS`, na stromě hry `coin-picker` (stav `fc01255`) naměřeno 8 617 t
//   (`entity.player`) a 9 247 t (`core.game`) — pozor, je to HYBRID: pilotní
//   roadmapa je ze šablony, soubory jsou hry (v roadmapě hry ty granule NEJSOU).
//   → ty dvě kontroly NEMOHOU projít nikdy. Test je proto test ŠABLONY
//   (spouští ho `g3` nad `repo/`) a do hry se nekopíruje.
//   `roadmap.pilot.json` je jeho fixtura a nečte ji nikdo jiný — ve hře by ležela ladem.
//   (K6 uváděla 8 890 t; naměřeno K8 15. 10. 2026: to je STARŠÍ STAV TÉHOŽ STROMU,
//   ne kopie — `game.gd` měl do commitu `bcb675e` (PR #14, 14. 10. 11:09 UTC)
//   3 868 znaků = 8 890 t a ten commit padl DOVNITŘ okna, ve kterém K6 měřila;
//   číslo tedy zestárlo. Atribuci „měření kopie" (K7) doložit nelze.)
//   Přeměřeno nezávisle (K7 i K8): vlastním přepočtem i oficiálním
//   `rozpocet-granuli.mjs` nad skutečnými soubory hry.
const SKIP_SABLONOVE = new Set(['priprava.test.mjs', 'roadmap.pilot.json']);

const arg = (n, d = '') => {
  const i = process.argv.indexOf(n);
  return i >= 0 ? process.argv[i + 1] : d;
};
const nazev = arg('--nazev');
const cil = arg('--cil');
const whatif = process.argv.includes('--whatif');
const kontrola = process.argv.includes('--kontrola');
const force = process.argv.includes('--force');

if (!nazev || !cil) {
  console.error('POUŽITÍ: node tools/forge-new.mjs --nazev <nazev-hry> --cil <cesta> [--kontrola] [--whatif] [--force]');
  process.exit(2);
}
// Název je IDENTIFIKÁTOR (jde do `config/name`, do `product_name`, do game_id) —
// proto ASCII a malá písmena (konvence projektu: identifikátory anglicky/ASCII).
if (!/^[a-z][a-z0-9-]*$/.test(nazev)) {
  console.error(`CHYBA: název '${nazev}' musí být malými písmeny ASCII s pomlčkami (např. 'moje-hra')`);
  process.exit(2);
}
const NazevKrasne = nazev.split('-').map((c) => c.charAt(0).toUpperCase() + c.slice(1)).join('-');

for (const [co, cesta] of [['šablona', SABLONA], ['skeleton', SKELETON]]) {
  if (!existsSync(cesta)) { console.error(`CHYBA: ${co} ${cesta} neexistuje`); process.exit(2); }
}
if (existsSync(cil)) {
  const obsah = readdirSync(cil).filter((f) => f !== '.' && f !== '..');
  if (obsah.length && !force) {
    console.error(`CHYBA: cíl ${cil} není prázdný (${obsah.length} položek). Použij --force, nebo jiný cíl.`);
    process.exit(2);
  }
}
if (basename(cil) !== nazev) {
  console.log(`POZNÁMKA: cíl se jmenuje '${basename(cil)}', hra '${nazev}' — není to vada, ale u her na stanici platí, že složka = název hry (sourozenec orchestry).`);
}

const kopiruj = (odkud, kam, { prepsat = true } = {}) => {
  mkdirSync(kam, { recursive: true });
  for (const e of readdirSync(odkud, { withFileTypes: true })) {
    if (SKIP_NAZVY.has(e.name) || SKIP_SABLONOVE.has(e.name)) continue;
    const a = join(odkud, e.name);
    const b = join(kam, e.name);
    if (e.isDirectory()) kopiruj(a, b, { prepsat });
    else if (prepsat || !existsSync(b)) copyFileSync(a, b);
  }
};

console.log(`Forge new: hra '${nazev}' → ${cil}${whatif ? '  (SUCHÝ BĚH)' : ''}`);
if (!whatif) {
  mkdirSync(cil, { recursive: true });
  const stav = { souboru: 0, zmen: 0 };

  // 1) orchestrace ze šablony (roadmap.json šablony je PRÁZDNÝ a skeleton ho přepíše)
  kopiruj(SABLONA, cil);
  // 2) herní skeleton
  kopiruj(SKELETON, cil);

  // 3) název hry ve všech TEXTových souborech + reset roadmapy
  const TEXTY = ['.godot', '.tscn', '.cfg', '.json', '.gd', '.md', '.py', '.yml', '.sh'];
  const projdi = (slozka) => {
    for (const e of readdirSync(slozka, { withFileTypes: true })) {
      const p = join(slozka, e.name);
      if (e.isDirectory()) { projdi(p); continue; }
      if (!TEXTY.some((x) => e.name.endsWith(x))) continue;
      let t = readFileSync(p, 'utf8');
      const puvodni = t;
      t = t.replace(/Coin-Picker/g, NazevKrasne).replace(/coin-picker/g, nazev);
      if (t !== puvodni) { writeFileSync(p, t, 'utf8'); stav.zmen++; }
      stav.souboru++;
    }
  };
  projdi(cil);

  // Reset roadmapy: nová hra NESMÍ mít hotové granule po cizím pilotu.
  const rmCesta = join(cil, '.forge', 'roadmap.json');
  if (existsSync(rmCesta)) {
    const rm = JSON.parse(readFileSync(rmCesta, 'utf8'));
    let zruseno = 0;
    for (const g of rm.grains || []) {
      if (g.done !== undefined || g._done !== undefined) zruseno++;
      delete g.done;
      delete g._done;
    }
    rm._popis = [
      `Fronta granul hry ${NazevKrasne} — plán, který má orchestra dělat SAMA.`,
      '',
      'Skeleton vznikl z ověřené hry (K4, 13. 10. 2026) a je ZELENÝ: testy, schéma,',
      'assety i zapojení procházejí. Granule proto přidávají FUNKCE do běžící hry.',
      '',
      'BRÁNA PŘED ZÁPISEM: každá granule musí projít stropem poskytovatele:',
      '  node .forge/node/rozpocet-granuli.mjs --poskytovatel groq --model openai/gpt-oss-120b',
      '→ REQUEST_FITS. Co se nevejde, se NEPOŠLE.',
      '',
      'CO JE V KONVENCI GRANULE: `"konvence": ["01-typy", …]` — sekce z CONVENTIONS/,',
      'které granule dostane. Volba sekcí se MĚŘÍ: v K4 spadl první pilot na Godot 3',
      '`connect(...)`, protože ta granule neměla `05-godot3-konstanty`.',
    ];
    writeFileSync(rmCesta, JSON.stringify(rm, null, 2) + '\n', 'utf8');
    console.log(`  roadmapa: ${(rm.grains || []).length} granulí, zrušeno 'done' u ${zruseno}`
      + ` (nová hra nesmí tvrdit cizí hotovou práci)`);
  }
  console.log(`  zkopírováno a přejmenováno: ${stav.souboru} textových souborů, ${stav.zmen} změn názvu`);
}

// 4) volitelná kontrola: spustí brány hry na vygenerovaném stromě
if (kontrola && !whatif) {
  console.log('\n=== KONTROLA VYGENEROVANÉ HRY ===');
  const py = process.env.FORGE_PYTHON || 'python';
  const brany = [
    ['schéma', py, ['.forge/check-schema.py', '.']],
    ['assety', py, ['.forge/check-assets.py', '.']],
    ['zapojení', py, ['.forge/check-wiring.py', '.']],
    ['rozpočet granulí', process.execPath, ['.forge/node/rozpocet-granuli.mjs',
      '--roadmap', '.forge/roadmap.json', '--poskytovatel', 'groq', '--model', 'openai/gpt-oss-120b']],
  ];
  let chyb = 0;
  for (const [jmeno, cmd, args] of brany) {
    const r = spawnSync(cmd, args, { cwd: cil, encoding: 'utf8' });
    const ok = r.status === 0;
    if (!ok) chyb++;
    console.log(`  ${ok ? 'OK  ' : 'CHYBA'} ${jmeno} (exit=${r.status})`);
    if (!ok) console.log('        ' + String(r.stdout || r.stderr || '').split('\n').slice(-4).join('\n        '));
  }
  const godot = process.env.FORGE_GODOT || 'E:/Tools/godot/Godot_v4.7.2-stable_win64_console.exe';
  if (existsSync(godot)) {
    spawnSync(godot, ['--headless', '--path', '.', '--import'], { cwd: cil, encoding: 'utf8' });
    const r = spawnSync(godot, ['--headless', '--path', '.', '--script', 'res://tests/run_tests.gd'], { cwd: cil, encoding: 'utf8' });
    const radek = String(r.stdout || '').split('\n').find((l) => l.includes('kontrol,')) || '(bez souhrnu)';
    const ok = r.status === 0;
    if (!ok) chyb++;
    console.log(`  ${ok ? 'OK  ' : 'CHYBA'} testy hry → ${radek.trim()}`);
  } else {
    console.log(`  POZNÁMKA: Godot nenalezen (${godot}) – testy hry se nespustily (není to zelená)`);
  }
  if (chyb) { console.error(`\nCHYBA: ${chyb} bran(y) na vygenerované hře spadly`); process.exit(1); }
  console.log('  všechny brány vygenerované hry prošly');
}

console.log(`
HOTOVO. Další kroky (nástroj je NEDĚLÁ):
  1) git init -b main ; git add -A ; git commit -m "Forge: zaklad hry ${nazev}" ; git push
  2) secrety v repu hry: FORGE_PAT (fine-grained, Contents RW + Pull requests RW),
     FORGE_WEBHOOK_SECRET, a klíče poskytovatelů (mohou být i ve Variables)
  3) registrace v conductoru: POST /game {"game_id":"${nazev}","repo":"<owner>/${nazev}"}
     a přepnutí aktivní hry: POST /game/active {"game_id":"${nazev}","active":true}`);

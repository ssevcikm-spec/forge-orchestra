#!/usr/bin/env node
// TEST generátoru `tools/forge-new.mjs` — nová hra musí být po jednom příkazu
// ZELENÁ a musí o sobě tvrdit PRAVDU.
//
// PROČ: generátor je nástroj, na kterém stojí každá další hra. Kdyby tiše
// zkopíroval něco špatně, pozná se to až v CI nové hry (jako `export_presets.cfg`
// u první hry v K4). Test proto měří DVĚ věci:
//   * ŽE SE VYGENEROVANÁ HRA SKUTEČNĚ ZKOMPILUJE A PROJDE BRANAMI (spouští je),
//   * ŽE O SOBĚ NETVRDÍ NEPRAVDU: žádné `done: true` (nová hra nic hotové nemá),
//     nikde v textu nezůstalo jméno VZOROVÉ hry a název hry je opravdu přepsaný.
//
// Použití: node _analyza/test-forge-new.mjs
// Exit: 0 = všechny kontroly prošly, 1 = vada generátoru.

import { readFileSync, existsSync, rmSync, mkdtempSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { tmpdir } from 'node:os';

const __dir = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(__dir);
const GENERATOR = join(ORCH, 'tools', 'forge-new.mjs');
const SKELETON = join(ORCH, 'skeleton');

let kontrol = 0, chyb = 0;
const test = (nazev, ok, detail = '') => {
  kontrol++;
  if (ok) console.log(`ok     ${nazev}`);
  else { chyb++; console.log(`CHYBA  ${nazev}${detail ? `\n       ${detail}` : ''}`); }
};

const spust = (args, cwd = ORCH) => {
  const r = spawnSync(process.execPath, args, { cwd, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024 });
  return { kod: r.status, out: (r.stdout || '') + (r.stderr || '') };
};

// ── kontroly, které nepotřebují běh generátoru ──────────────────────────────
test('skeleton existuje', existsSync(SKELETON));
test('skeleton NEVEZE soubor, který má vyrobit granule (scripts/coin.gd)',
  !existsSync(join(SKELETON, 'scripts', 'coin.gd')),
  'kdyby vezl coin.gd, granule `world.coin` by v nové hře dělala hotovou práci');
test('skeleton nese export_presets.cfg (bez něj padá CI na exportu)',
  existsSync(join(SKELETON, 'export_presets.cfg')));

// ── kladný případ: vygeneruj, pusť brány, zkontroluj tvrzení ────────────────
const zaklad = mkdtempSync(join(tmpdir(), 'forge-new-'));
const nazev = 'testovaci-hra';
const cil = join(zaklad, nazev);
const r = spust([GENERATOR, '--nazev', nazev, '--cil', cil, '--kontrola']);
test('generátor na prázdný cíl projde (exit 0)', r.kod === 0, r.out.split('\n').slice(-12).join('\n       '));
test('generátor vykreslí výsledek bran (schéma/assety/zapojení/rozpočet)',
  /OK\s+schéma/.test(r.out) && /OK\s+assety/.test(r.out) && /OK\s+zapojení/.test(r.out)
  && /OK\s+rozpočet granulí/.test(r.out));
test('testy hry ve vygenerované hře projdou', /0 selhání/.test(r.out), r.out.split('\n').slice(-8).join('\n       '));
// Rozpočet si test spustí SÁM na vygenerovaném stromě — ne že uvěří tomu, co
// o sobě napsal generátor („brána, která se ptá na příslib, neměří“).
if (existsSync(cil)) {
  const rb = spawnSync(process.execPath, [join(cil, '.forge', 'node', 'rozpocet-granuli.mjs'),
    '--roadmap', '.forge/roadmap.json', '--poskytovatel', 'groq', '--model', 'openai/gpt-oss-120b'],
  { cwd: cil, encoding: 'utf8' });
  const vystup = (rb.stdout || '') + (rb.stderr || '');
  test('rozpočet granulí vygenerované hry: REQUEST_FITS u všech', rb.status === 0 && /REQUEST_FITS/.test(vystup),
    vystup.split('\n').slice(-4).join('\n       '));
}

if (existsSync(cil)) {
  const rm = JSON.parse(readFileSync(join(cil, '.forge', 'roadmap.json'), 'utf8'));
  test('nová hra netvrdí hotové granule (žádné done: true)',
    (rm.grains || []).every((g) => g.done !== true && g._done === undefined),
    JSON.stringify((rm.grains || []).filter((g) => g.done === true || g._done).map((g) => g.id)));
  test('roadmapa má granule (nezůstala prázdná po resetu)', (rm.grains || []).length >= 2,
    `granulí: ${(rm.grains || []).length}`);
  test('hráč má co dělat: chybí soubor první granule (scripts/coin.gd)',
    !existsSync(join(cil, 'scripts', 'coin.gd')));

  // Název hry musí být PŘEPSANÝ a jméno vzorové hry NESMÍ nikde zůstat.
  const texty = [];
  const projdi = (slozka) => {
    for (const e of readdirSync(slozka, { withFileTypes: true })) {
      if (['.git', '.godot', '__pycache__'].includes(e.name)) continue;
      const p = join(slozka, e.name);
      if (e.isDirectory()) { projdi(p); continue; }
      if (/\.(gd|godot|tscn|cfg|json|md|py|mjs|yml)$/.test(e.name)) texty.push(p);
    }
  };
  projdi(cil);
  const sVzorem = texty.filter((p) => /Coin-Picker|coin-picker/.test(readFileSync(p, 'utf8')));
  test('nikde nezůstalo jméno vzorové hry (Coin-Picker/coin-picker)', sVzorem.length === 0,
    sVzorem.map((p) => p.replace(cil, '')).join(', '));
  test('název hry je v project.godot',
    readFileSync(join(cil, 'project.godot'), 'utf8').includes(`config/name="${nazev}"`));
  test('název hry je ve vizuálním profilu',
    JSON.parse(readFileSync(join(cil, '.forge', 'vision-profile.json'), 'utf8')).hra === nazev);
  test('název hry je v exportním presetu',
    readFileSync(join(cil, 'export_presets.cfg'), 'utf8').includes(`application/product_name="${nazev}"`));
  test('hra má orchestraci ze šablony (.forge/node/rozpocet-granuli.mjs)',
    existsSync(join(cil, '.forge', 'node', 'rozpocet-granuli.mjs')));
  test('hra má sekce konvencí z šablony', existsSync(join(cil, 'CONVENTIONS', '01-typy.md')));
  test('do hry se NEZkopírovala tajemství (.env / provider.env)',
    !existsSync(join(cil, '.forge', 'node', '.env')) && !existsSync(join(cil, '.forge', 'provider.env')));
  // K6 (14. 10. 2026): testy, které měří ŠABLONU, se do hry nevezou. Dvě RŮZNÉ
  // vady, které se nesmí plést (rozlišeno v K7 — HANDOFF.md §73.2, nález H207):
  //   * `coin-picker` byl postaven RUČNĚ a dostal test BEZ fixtury → `ENOENT`,
  //     15 z 55 kontrol se nikdy nespustilo;
  //   * strom, kde fixtura JE (tak ho dodával starý generátor), test spustí
  //     a spadnou 2 kontroly K3: rozpočet pilotních granulí šablony nad
  //     SKUTEČNÝMI soubory hry — naměřeno 8 617 t (`entity.player`) a 9 247 t
  //     (`core.game`) proti stropu 8 000 t. POZOR: je to hybrid (pilotní
  //     roadmapa ze ŠABLONY, soubory z HRY; v roadmapě hry ty granule nejsou).
  //     (K6 uváděla 8 890 t; naměřeno K8 15. 10. 2026: je to STARŠÍ STAV TÉHOŽ
  //     STROMU, ne kopie — `game.gd` měl do `bcb675e` (PR #14, 14. 10. 11:09 UTC)
  //     3 868 znaků = 8 890 t a ten commit padl dovnitř okna K6; atribuci
  //     „měření kopie" doložit nelze.)
  test('do hry se NEveze test ŠABLONY (.forge/node/priprava.test.mjs)',
    !existsSync(join(cil, '.forge', 'node', 'priprava.test.mjs')));
  test('do hry se NEveze fixtura šablony (.forge/roadmap.pilot.json)',
    !existsSync(join(cil, '.forge', 'roadmap.pilot.json')));
  // Protizkouška: kdyby generátor přestal kopírovat VŠE, předchozí dva testy
  // projdou „soubor tu není" i nad prázdným stromem — a to by nebyla zelená,
  // ale slepá. Testy nástrojů, které do hry PATŘÍ, proto musí v cíli být.
  test('testy nástrojů, které do hry PATŘÍ, tam jsou (protizkouška)',
    existsSync(join(cil, '.forge', 'node', 'provider-choice.test.mjs')));
}

// ── záporné případy: musí SPADNOUT a POJMENOVAT to ──────────────────────────
const r2 = spust([GENERATOR, '--nazev', nazev, '--cil', cil]);
test('ne-prázdný cíl bez --force = chyba (exit 2)', r2.kod === 2, `exit=${r2.kod}`);
test('a je pojmenovaná', /není prázdný/.test(r2.out), r2.out.slice(0, 200));

const r3 = spust([GENERATOR, '--nazev', 'Moje Hra', '--cil', join(zaklad, 'x')]);
test('název s mezerou/velkými písmeny = chyba (identifikátor musí být ASCII)', r3.kod === 2, `exit=${r3.kod}`);
test('a je pojmenovaná', /musí být malými písmeny/.test(r3.out), r3.out.slice(0, 200));

const r4 = spust([GENERATOR]);
test('bez --nazev/--cil vypíše použití a skončí 2', r4.kod === 2 && /POUŽITÍ/.test(r4.out));

try { rmSync(zaklad, { recursive: true, force: true }); } catch { /* úklid není kritický */ }

console.log(`\n=== VYSLEDEK: ${kontrol - chyb}/${kontrol} kontrol, ${chyb} chyb ===`);
process.exit(chyb ? 1 : 0);

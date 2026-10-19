#!/usr/bin/env node
// K3 — OVERENI ROZDELENI `CONVENTIONS.md` NA SEKCE (12. 10. 2026).
//
// PROC TO EXISTUJE:
//   `K3` rozdelil jeden dokument (`repo/CONVENTIONS.md`, 3 893 t) na sekce
//   v `repo/CONVENTIONS/`, protoze se cely nevesel do stropu poskytovatele.
//   Pri takovem presunu se da snadno ZTRATIT text — a ztrata se nepozna,
//   protoze nikdo necte novy dokument proti staremu. Tenhle nastroj to
//   porovnava MECHANICKY:
//
//     1) originál bere z GITU (`git show <rev>:repo/CONVENTIONS.md`), ne
//        z pracovniho stromu — jinak by se novy soubor porovnaval sam se sebou
//        (pasta: „tvrzeni se cte z dokumentu, ktery brana nikdy neotevrela"),
//     2) rozpadne oba na bloky podle nadpisu `##`,
//     3) tvrdi, ze KAZDY blok originalu je PRAVE V JEDNE sekci (`CONVENTIONS/`),
//     4) tvrdi, ze v sekcich NENI zadny blok, ktery v originalu nebyl,
//     5) overi velikost: kazda sekce <= 1 200 t, index <= 600 t a index
//        NEOBSAHUJE zadny blok originalu (aby se cely dokument omylem neposilal),
//     6) vypise MAPOVANI `§ -> soubor` („ktere body zustaly" se overuje
//        hledanim, ne pameti).
//
// ZNAME ZMENY: text, ktery se pri deleni ZAMERNE prepsal, je vyjmenovany
// v `ZNAME_ZMENY` — a u kazde se overi DVE veci: (a) stary text uz nikde neni,
// (b) novy text v cile skutecne je. Jinak by seznam výjimek mohl zakryt
// i skutecnou ztratu.
//
// Pouziti:
//   node _analyza/k3-over-konvence-split.mjs
//   node _analyza/k3-over-konvence-split.mjs --rev 8495d8a   # jiny zaklad

import { readFileSync, readdirSync, existsSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { ZNAKU_NA_TOKEN } from '../repo/.forge/node/prompt-hygiene.mjs';
import { revizePredRozdelenim } from './_revize-konvenci.mjs';

const __dir = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(__dir);
const SEKCE_DIR = join(ORCH, 'repo', 'CONVENTIONS');
const INDEX = join(ORCH, 'repo', 'CONVENTIONS.md');

// Strop sekce je 1 200 t (metodika `game-developer` §4.1b: konvence jedné
// granule <= 1 200 t). Index se NEPOSÍLÁ, ale držíme ho pod stejným stropem:
// kdyby ho někdo omylem poslal přes `--read CONVENTIONS.md`, musí se vejít.
const LIMIT_SEKCE_T = 1200;
const LIMIT_INDEX_T = 1200;

function arg(n, d = '') {
  const i = process.argv.indexOf(n);
  return i >= 0 ? process.argv[i + 1] : d;
}
// ⚠ VÝCHOZÍ ZÁKLAD NENÍ `HEAD` (naměřeno 13. 10. 2026 hned po prvním commitu
// K3/K4): po commitu je v `HEAD` už ROZCESTNÍK, takže brána srovnávala index
// s indexem → „0 bloků originálu, 14 chyb“ a vypadalo to jako ztracený text.
// Revizi před rozdělením hledá společný helper (viz `_revize-konvenci.mjs`).
const REV = arg('--rev') || revizePredRozdelenim();
const tokeny = (text) => Math.ceil(text.length / ZNAKU_NA_TOKEN);

let kontrol = 0;
let chyb = 0;
const test = (nazev, ok, detail = '') => {
  kontrol++;
  if (ok) {
    console.log(`ok     ${nazev}`);
  } else {
    chyb++;
    console.log(`CHYBA  ${nazev}${detail ? `\n       ${detail}` : ''}`);
  }
};

/** Rozpadne dokument na bloky podle nadpisu `## <klic>. …`; vrati Map(klic -> telo). */
function bloky(text, { preskocUvodniCitaci = false } = {}) {
  const radky = text.replace(/\r\n/g, '\n').split('\n');
  const out = new Map();
  let klic = null;
  let telo = [];
  let vCitaci = preskocUvodniCitaci;
  const uloz = () => {
    if (klic === null) return;
    out.set(klic, telo.join('\n').trim());
  };
  for (const r of radky) {
    if (vCitaci) {
      // Preskoc uvodni blok citace (`> …`) nove sekce — je to jeji hlavicka,
      // ne text prebirany z originalu.
      if (/^\s*$/.test(r)) { vCitaci = false; }
      continue;
    }
    const m = /^##\s+([0-9]+[a-z]?)\.\s*(.*)$/.exec(r);
    // Nadpis do tela NEPATRI: shodu nadpisu uz vynucuje klic (Map). Telu se pak
    // da prepsat celym textem, aniz by se musel opsovat nadpis.
    if (m) { uloz(); klic = m[1]; telo = []; continue; }
    if (klic !== null) telo.push(r);
  }
  uloz();
  return out;
}

// ── ZNAME ZMENY (text, ktery se pri deleni zamerne prepsal) ─────────────────
const ZNAME_ZMENY = [
  {
    klic: '7',
    cely: true,
    novy: 'skutečný počet si přečti z výstupu běhu',
    duvod: 'počet testů je vlastnost HRY, ne šablony — do konvence nové hry nepatří',
  },
  {
    klic: '1e',
    stary: '(viz §6)',
    novy: '(viz sekce `08-meze-a-overeni`)',
    duvod: 'sekce jsou teď samostatné soubory, odkaz na § míří do jiného souboru',
  },
  // ── §1h: ZMĚNY K4/F11 (13. 10. 2026) — DOREGISTROVÁNO 14. 10. 2026 (K6) ───
  // K4 v F11 tenhle blok legitimně upravil (doplnil `empty()` -> `is_empty()`
  // a zkrátil ukázku i odstavce), ale NEPŘIDAL ho sem. Brána proto porovnávala
  // blok bajt na bajt s PŘED-rozdělovým originálem → `CHYBA blok §1h … (text
  // bajt na bajt)`, a to i když sama hlásila „0 ztracených“ (K5 §3, kořen C;
  // K5 §5.2 to nechala jako rozhodnutí, co má brána tvrdit).
  //
  // Rozhodnutí (K6): brána tvrdí dál TOTÉŽ — „text bloku je v sekci, až na
  // VYJMENOVANÉ změny“ — jen se sem změny dopisují. Není to povolení zelené:
  // každý pár se ověřuje OBOUSTRANNĚ (starý text musí být v originálu, nový
  // v sekci; viz `ocekavane`/`skutecne` níž), takže špatně opsaná výjimka bránu
  // shodí. Zbytek bloku se pořád srovnává bajt na bajt — cokoli jiného než tyhle
  // čtyři změny a jedno doplnění = chyba.
  {
    klic: '1h',
    stary: 'Model má v trénovacích datech spoustu Godotu 3 a píše jeho konstanty.',
    novy: 'Model má v datech spoustu Godotu 3 a píše jeho konstanty.',
    duvod: 'K4/F11: zkrácení úvodu (sekce se musí vejít do stropu 1 200 t)',
  },
  {
    klic: '1h',
    stary: 'je přejmenoval na delší a významově jiná jména – a **parse to odhalí**:',
    novy: 'je přejmenoval\n– a **parse to odhalí**:',
    duvod: 'K4/F11: zkrácení téhož úvodu (jen přelomení a vypuštěná vsuvka)',
  },
  {
    klic: '1h',
    stary: 'label.valign = Label.VALIGN_TOP\nlabel.autowrap = true\n\n# SPRÁVNĚ – Godot 4\n'
      + 'label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT\n'
      + 'label.vertical_alignment = VERTICAL_ALIGNMENT_TOP\n'
      + 'label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART',
    novy: '# SPRÁVNĚ – Godot 4: label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT',
    duvod: 'K4/F11: zkrácená ukázka (tabulka o pár řádků níž říká totéž)',
  },
  {
    klic: '1h',
    stary: '| `connect("signal", self, "_on_x")` | `signal.connect(_on_x)` |',
    novy: '| `connect("signal", self, "_on_x")` | `signal.connect(_on_x)` |\n'
      + '| `array.empty()` / `string.empty()` / `dict.empty()` | '
      + '`array.is_empty()` / `string.is_empty()` / `dict.is_empty()` |',
    duvod: 'K4/F11: DOPLNĚNÝ řádek `empty()` -> `is_empty()` — na tom spadla granule world.spawner',
  },
  {
    klic: '1h',
    stary: '**Naměřeno 1. 10. 2026:** granule `ui.hud` (běh #241) na tomhle spadla –',
    novy: '**Naměřeno 13. 10. 2026 (K4):** granule `world.spawner` (běh `Forge #249`) spadla\n'
      + 'na `Cannot find member "empty" in base "Array[Node]"` — model napsal\n'
      + '`pole.empty()` jako v Godotu 3. Sekce se posílala, řádek v tabulce ale **nebyl**.\n\n'
      + '**Naměřeno 1. 10. 2026:** granule `ui.hud` (běh #241) na tomhle spadla –',
    duvod: 'K4/F11: DOPLNĚNÝ měřený případ (doklad, proč řádek v tabulce přibyl)',
  },
  {
    klic: '1h',
    stary: '`Cannot find member "ALIGN_LEFT" in base "Label"` na `scripts/hud.gd:8` a\n'
      + '`VALIGN_TOP` na `:9`. Soubor se kvůli tomu **nikdy nedostal do repa** a HUD\n'
      + 'nemá stavovou lištu.',
    novy: '`Cannot find member "ALIGN_LEFT" in base "Label"` na `scripts/hud.gd:8`; soubor\n'
      + 'se kvůli tomu **nikdy nedostal do repa**.',
    duvod: 'K4/F11: zkrácení téhož měřeného případu (duplikovalo tabulku)',
  },
  // ── §1g: ZMĚNA 19. 10. 2026 (H231) — pravidlo `extends Node` platí jen pro
  // NOVÉ soubory. Naměřeno v běhu #398: model poslechl staré znění, přepsal
  // `game.gd` z `Node2D` na `Node` a rozbil 5 volání `get_viewport_rect()`.
  // Doregistrováno tady, protože brána jinak hlásí „text se rozešel“ u
  // změny, která je ZÁMĚRNÁ (a seznam výjimek se nesmí obejít bez důvodu).
  {
    klic: '1g',
    stary: '1. **Soubor začíná `extends Node`.** Když je to `Resource` nebo `RefCounted`,\n'
      + '   `new()` sice projde, ale instance není uzel – a uvolnění v testech (`free()`)\n'
      + '   na RefCounted vyhodí chybu, která **přeruší celý běh testů**.',
    novy: '1. **Nový soubor granule začíná `extends Node`.** Když je to `Resource` nebo\n'
      + '   `RefCounted`, `new()` sice projde, ale instance není uzel – a uvolnění\n'
      + '   v testech (`free()`) na RefCounted vyhodí chybu, která **přeruší celý běh\n'
      + '   testů**.\n'
      + '   **⚠ Když soubor GRANULE UŽ existuje a začíná jinak** (typicky `Node2D`\n'
      + '   scéna, `Area2D` hráč), **zachovej jeho stávající `extends`** — pravidlo\n'
      + '   platí pro NOVÉ soubory. Naměřeno 16. 10. 2026 (běh #398): model poslechl\n'
      + '   dřívější znění „soubor začíná `extends Node`“ a přepsal `scripts/game.gd`\n'
      + '   z `Node2D` na `Node`; rozbil tím 5 volání `get_viewport_rect()` a parse\n'
      + '   gate běh shodil. Takové soubory se přes `load(...).new()` neinstancují.',
    duvod: 'H231: pravidlo platí jen pro NOVÉ soubory; existující extends se zachovává '
      + '(naměřeno v běhu #398 — přepis Node2D→Node rozbil get_viewport_rect)',
  },
];

// ── 1) original z GITU ──────────────────────────────────────────────────────
const git = spawnSync('git', ['-C', ORCH, 'show', `${REV}:repo/CONVENTIONS.md`], {
  encoding: 'utf8', maxBuffer: 32 * 1024 * 1024,
});
if (git.status !== 0) {
  console.error(`CHYBA: original se z gitu prečíst nepodařilo (git show ${REV}:repo/CONVENTIONS.md)`);
  console.error(git.stderr || '');
  process.exit(2);
}
const original = git.stdout;
const blokyOrig = bloky(original);

// ── 2) nove sekce ───────────────────────────────────────────────────────────
if (!existsSync(SEKCE_DIR)) {
  console.error(`CHYBA: chybí složka ${SEKCE_DIR}`);
  process.exit(2);
}
const soubory = readdirSync(SEKCE_DIR).filter((f) => f.endsWith('.md')).sort();
test('sekce: složka CONVENTIONS/ obsahuje aspoň 4 soubory', soubory.length >= 4, `nalezeno ${soubory.length}`);

const kde = new Map();  // klic -> [soubor]
const noveBloky = new Map(); // "soubor|klic" -> telo
for (const f of soubory) {
  const text = readFileSync(join(SEKCE_DIR, f), 'utf8');
  const b = bloky(text, { preskocUvodniCitaci: true });
  for (const [k, telo] of b) {
    if (!kde.has(k)) kde.set(k, []);
    kde.get(k).push(f);
    noveBloky.set(`${f}|${k}`, telo);
  }
  const t = tokeny(text);
  test(`sekce ${f}: <= ${LIMIT_SEKCE_T} t`, t <= LIMIT_SEKCE_T, `naměřeno ${t} t`);
}

// ── 3) kazdy blok originalu prave v jedne sekci ─────────────────────────────
const A = '\u0000'; // oddelovac pro "nahrazeno"
const normalizuj = (s) => s.replace(/\s+/g, ' ').trim();
const zmenene = new Set(ZNAME_ZMENY.map((z) => z.klic));
const mapovani = [];
let ztraceno = 0;
for (const [k, telo] of blokyOrig) {
  const cile = kde.get(k) || [];
  if (cile.length !== 1) {
    ztraceno++;
    test(`blok §${k} je prave v jedne sekci`, false, `nalezen v: ${cile.join(', ') || '(nikde)'}`);
    continue;
  }
  const f = cile[0];
  const zmeny = ZNAME_ZMENY.filter((z) => z.klic === k);
  const skutecneTelo = noveBloky.get(`${f}|${k}`) ?? '';
  const cela = zmeny.find((z) => z.cely);
  if (cela) {
    // Cely blok se prepsal: (a) stary text uz v sekci NENI, (b) novy text v ni JE.
    // Kdyby se kontroloval jen (b), mohla by výjimka zakryt i ztratu zbytku.
    const staryJe = normalizuj(skutecneTelo).includes(normalizuj(telo).slice(0, 80));
    const novyJe = skutecneTelo.includes(cela.novy);
    test(`blok §${k} -> ${f} (cely prepsan, nova veta overena)`, !staryJe && novyJe,
      `stary text v sekci ${staryJe ? 'ZUSTAL' : 'neni'}, nova veta ${novyJe ? 'je' : 'CHYBI'}`);
    mapovani.push({ klic: k, soubor: f, znaku: telo.length, zmen: zmeny.length, cely: true });
    continue;
  }
  let ocekavane = telo;
  for (const z of zmeny) {
    if (!ocekavane.includes(z.stary)) {
      chyb++;
      kontrol++;
      console.log(`CHYBA  znamá změna §${k}: stary text v originalu NENI -> výjimka je zbytecna (nebo spatne opsana)`);
      console.log(`       hledano: ${JSON.stringify(z.stary)}`);
    }
    ocekavane = ocekavane.split(z.stary).join(A);
  }
  let skutecne = skutecneTelo;
  for (const z of zmeny) skutecne = skutecne.split(z.novy).join(A);
  const sedi = normalizuj(ocekavane) === normalizuj(skutecne);
  test(`blok §${k} -> ${f} (text bajt na bajt${zmeny.length ? ', kromě znamé zmeny' : ''})`, sedi,
    sedi ? '' : 'text se rozesel — bud se neco ztratilo, nebo pribylo');
  mapovani.push({ klic: k, soubor: f, znaku: telo.length, zmen: zmeny.length });
}

// ── 4) v sekcich neni blok, ktery v originalu nebyl ─────────────────────────
for (const [k, souboryK] of kde) {
  for (const f of souboryK) {
    const existuje = blokyOrig.has(k);
    test(`sekce ${f}: blok §${k} pochazi z originalu`, existuje, existuje ? '' : 'takovy blok v originalu NEBYL');
  }
}

// ── 5) index se neposila jako celek ─────────────────────────────────────────
// ⚠ VELIKOST OKNA SE VYPISUJE (ZMĚŘENO nize). Velkoryse okno neni opatrnost,
// je to slepota: naměřeno v projektu, že blok o 5 441 znacich kvůli sirokemu
// oknu umlcel cely oddil. 40 znaku je dost na to, aby to nebyla nahoda, a malo
// na to, aby se dala vlozit cela veta z originalu a kontrola to nevidela.
const OKNO = 40;
const indexText = readFileSync(INDEX, 'utf8');
const indexT = tokeny(indexText);
test(`index CONVENTIONS.md: <= ${LIMIT_INDEX_T} t`, indexT <= LIMIT_INDEX_T, `naměřeno ${indexT} t`);
const indexBloky = bloky(indexText);
// Nadpisy `###` v tabulce nejsou; `##` v indexu být nesmí — jinak by v něm byl text sekce.
test('index neobsahuje žádný blok `##` z originalu', indexBloky.size === 0,
  indexBloky.size ? `index má bloky: ${[...indexBloky.keys()].join(', ')}` : '');
// Index nesmí obsahovat text sekcí (kontrola proti omylem vlozenemu textu).
let vIndexu = 0;
const normalizovanyIndex = normalizuj(indexText);
for (const [k, telo] of blokyOrig) {
  const kus = normalizuj(telo).slice(0, OKNO);
  if (kus.length >= OKNO && normalizovanyIndex.includes(kus)) vIndexu++;
}
test('index neobsahuje text žádné sekce (neodesílal by se celý dokument)', vIndexu === 0,
  vIndexu ? `${vIndexu} bloků originalu je v indexu (okno ${OKNO} znaků)` : '');

// ── výstup ──────────────────────────────────────────────────────────────────
console.log('');
console.log(`=== MAPOVÁNÍ § -> soubor (${mapovani.length} bloků) ===`);
for (const m of mapovani.sort((a, b) => a.klic.localeCompare(b.klic))) {
  console.log(`  §${m.klic.padEnd(3)} -> ${m.soubor}${m.zmen ? `  (známá změna: ${m.zmen})` : ''}`);
}
const souboruSTextem = new Set(mapovani.map((m) => m.soubor));
const prazdne = soubory.filter((f) => !souboruSTextem.has(f));
if (prazdne.length) console.log(`  (sekce bez bloku z originalu: ${prazdne.join(', ')})`);
console.log('');
console.log(`ZMĚŘENO: ${kontrol} kontrol, ${chyb} chyb, ${blokyOrig.size} bloků originalu, `
  + `${soubory.length} sekcí, ${ztraceno} ztracených`);
console.log(`ZMĚŘENO: sekce celkem ${soubory.reduce((a, f) => a + tokeny(readFileSync(join(SEKCE_DIR, f), 'utf8')), 0)} t, `
  + `index ${indexT} t, originál ${tokeny(original)} t`);
console.log(`ZMĚŘENO: okno kontroly "text sekce v indexu" = ${OKNO} znaků (menší okno = ostřejší, ale náchylnější k falešnému poplachu)`);
process.exit(chyb ? 1 : 0);

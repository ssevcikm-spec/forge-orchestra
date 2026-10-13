#!/usr/bin/env node
// K3 (12. 10. 2026) — SUCHY BEH WORKFLOW + PROTIZKOUSKA.
//
// DVE VEci, KTERE SE NESMI PLEST:
//   A) SUCHY BEH — pro kazdou granuli pilotni roadmapy se spusti PRESNE ty
//      prikazy, ktere pousti `.github/workflows/agent.yml` (files-to-edit →
//      prompt-hygiene → request-budget) a overi se, ze verdikt je
//      REQUEST_FITS. Nemeni strom repa: vsechno se deje v KOPII v `.tmp/`
//      (proto se daji i „založit prazdne soubory“, jak to dela workflow).
//   B) PROTIZKOUSKA — hradlo, ktere nema jak selhat, neni hradlo. Dve ruzne
//      vady se do mereneho requestu vlozi ZAMERNE a MUSI skoncit
//      REQUEST_TOO_LARGE (exit 1):
//        P1 „nafouknutá deklarace“: granule deklaruje VSECHNY sekce a vlastni
//            monolit o 300 radcich — tedy to, co K3 zakazuje. Nove potrubi.
//        P2 „cesta v zadani“: zadani zminuje dokument a workflow ho PREDAL
//            pomocí `--cteni` (to je stav PRED K1, kdy si aider dokument
//            pripjal sam — naměřeno 9. 10. 2026: request 39 167 t). Overuje
//            se i to, ze HYGIENA tu cestu odstrani, takze v novem potrubi
//            vada nevznikne.
//
// Pouziti:
//   node _analyza/k3-suchy-beh.mjs
//   node _analyza/k3-suchy-beh.mjs --zachovat     # nemaže scratch

import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, copyFileSync, readdirSync } from 'node:fs';
import { spawnSync } from 'node:child_process';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(__dir);
const REPO = join(ORCH, 'repo');
const HRA = join(dirname(ORCH), 'uo-shadows');   // ZMRAZENA: jen cteme
const SCRATCH = join(ORCH, '.tmp', 'k3-suchy');
const ZACHOVAT = process.argv.includes('--zachovat');

const NODE = process.execPath;
let kontrol = 0;
let chyb = 0;
const test = (nazev, ok, detail = '') => {
  kontrol++;
  if (ok) console.log(`ok     ${nazev}`);
  else { chyb++; console.log(`CHYBA  ${nazev}${detail ? `\n       ${detail}` : ''}`); }
};

/** Spusti prikaz ve scratchi (jako workflow: cwd = koren repa hry). */
function sh(prikaz, argumenty, { vstup = null } = {}) {
  const r = spawnSync(prikaz, argumenty, {
    cwd: SCRATCH, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024, input: vstup ?? undefined,
  });
  return { kod: r.status, out: (r.stdout || '').trim(), err: (r.stderr || '').trim() };
}

// ── priprava scratch ────────────────────────────────────────────────────────
if (existsSync(SCRATCH)) rmSync(SCRATCH, { recursive: true, force: true });
mkdirSync(join(SCRATCH, 'docs'), { recursive: true });
mkdirSync(join(SCRATCH, 'scripts'), { recursive: true });

// Co workflow potrebuje: `.forge`, `.github`, `CONVENTIONS.md` a sekce.
// POZOR: `.forge/node/.env` a `provider.*` se NEKOPÍRUJÍ — obsahují klíče
// a v suchém běhu nejsou potřeba (a do `.tmp` nepatří ani omylem).
const SKIP = new Set(['.env', 'provider.env', 'provider.json', '__pycache__']);
function kopiruj(odkud, kam) {
  mkdirSync(kam, { recursive: true });
  for (const e of readdirSync(odkud, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const a = join(odkud, e.name);
    const b = join(kam, e.name);
    if (e.isDirectory()) kopiruj(a, b);
    else copyFileSync(a, b);
  }
}
kopiruj(join(REPO, '.forge'), join(SCRATCH, '.forge'));
kopiruj(join(REPO, '.github'), join(SCRATCH, '.github'));
kopiruj(join(REPO, 'CONVENTIONS'), join(SCRATCH, 'CONVENTIONS'));
copyFileSync(join(REPO, 'CONVENTIONS.md'), join(SCRATCH, 'CONVENTIONS.md'));
copyFileSync(join(REPO, '.forge', 'roadmap.pilot.json'), join(SCRATCH, '.forge', 'roadmap.json'));
// CELY dokument PRED K3 — z gitu, ne z pracovniho stromu (ten uz je rozdelany).
const orig = spawnSync('git', ['-C', ORCH, 'show', 'HEAD:repo/CONVENTIONS.md'], { encoding: 'utf8' });
if (orig.status !== 0) { console.error('CHYBA: nejde precist original CONVENTIONS.md z gitu'); process.exit(2); }
writeFileSync(join(SCRATCH, 'CONVENTIONS.cely.md'), orig.stdout, 'utf8');
// Realne dokumenty hry pro protizkousku P2 (jen cteme ze zmrazene hry).
for (const d of ['TDD.md', 'ARCHITEKTURA.md']) {
  const zdroj = join(HRA, 'docs', d);
  if (existsSync(zdroj)) copyFileSync(zdroj, join(SCRATCH, 'docs', d));
}
// Realny monolit hry — do P2 (tam selhalo 20 behu). NESMI se jmenovat
// `scripts/game.gd`: to je soubor granul `core.game`, ktery v pilotu vzniká
// PRAZDNY — kdyby v suchém běhu ležel v repu monolit, měřil by se jiný stav,
// než jaký pilot opravdu má (naměřeno: 4 066 t navíc a verdikt „na hraně“).
for (const s of ['game.gd']) {
  const zdroj = join(HRA, 'scripts', s);
  if (existsSync(zdroj)) copyFileSync(zdroj, join(SCRATCH, 'scripts', 'monolit-real.gd'));
}

const roadmap = JSON.parse(readFileSync(join(SCRATCH, '.forge', 'roadmap.json'), 'utf8'));
console.log(`Suchý běh v ${SCRATCH} | granulí: ${roadmap.grains.length} | `
  + `celý dokument před K3: ${orig.stdout.length} B | docs/TDD.md: `
  + `${existsSync(join(SCRATCH, 'docs', 'TDD.md')) ? readFileSync(join(SCRATCH, 'docs', 'TDD.md'), 'utf8').length + ' B' : 'CHYBÍ'}`);
console.log('');

// ── A) SUCHY BEH: workflow pro kazdou granuli ───────────────────────────────
const POSKYTOVATEL = ['--poskytovatel', 'groq', '--model', 'openai/gpt-oss-120b'];
const vysledky = [];
console.log('=== A) SUCHÝ BĚH WORKFLOW (files-to-edit → hygiena → rozpočet) ===');
for (const g of roadmap.grains) {
  const gid = g.id;
  // 1) soubory k editaci (owns) — jako workflow: neexistujici se ZALOZI PRAZDNY
  const doEditace = sh(NODE, ['.forge/files-to-edit.mjs', '--grain', gid]);
  for (const f of doEditace.out.split('\n').map((x) => x.trim()).filter(Boolean)) {
    if (!existsSync(join(SCRATCH, f))) writeFileSync(join(SCRATCH, f), '');
  }
  // 2) zavislosti ke cteni
  const cteni = sh(NODE, ['.forge/files-to-edit.mjs', '--grain', gid, '--read-deps']).out;
  // 3) hygiena zadani
  const hy = sh(NODE, ['.forge/node/prompt-hygiene.mjs', g.prompt]);
  // 4) K3: deklarovane sekce konvenci
  const konv = sh(NODE, ['.forge/files-to-edit.mjs', '--grain', gid, '--konvence']);
  // 5) rozpocet — presne to, co posila workflow
  const rozpocet = sh(NODE, ['.forge/node/request-budget.mjs', '--zadani-text', hy.out,
    '--soubory', doEditace.out, '--cteni', cteni, '--konvence', konv.out, ...POSKYTOVATEL]);
  const cisla = /ROZPOCET: ~(\d+) tokenu/.exec(rozpocet.out) || /~(\d+) tokenu/.exec(rozpocet.out);
  const trida = /TRIDA=REQUEST_(\w+)/.exec(rozpocet.out);
  const tridaHodnota = trida ? trida[1] : '(žádná)';
  test(`${gid}: workflow dá REQUEST_FITS`, rozpocet.kod === 0 && tridaHodnota === 'FITS',
    `exit=${rozpocet.kod}, třída=${tridaHodnota}\n${rozpocet.err.split('\n').slice(0, 3).join('\n       ')}`);
  test(`${gid}: deklarované sekce se posílají (--konvence není prázdné)`,
    konv.out.split('\n').filter(Boolean).length === (g.konvence || []).length,
    `deklarováno ${(g.konvence || []).length}, předáno ${konv.out.split('\n').filter(Boolean).length}`);
  vysledky.push({
    id: gid, celkem: cisla ? Number(cisla[1]) : null, trida: tridaHodnota,
    zadani_znaku: hy.out.length, souboru_k_editaci: doEditace.out.split('\n').filter(Boolean).length,
    sekce: konv.out.split('\n').filter(Boolean),
  });
}

// ── B) PROTIZKOUSKA P1: nafouknutá deklarace (nové potrubí) ─────────────────
console.log('');
console.log('=== B) PROTIZKOUŠKA P1: všechny sekce + monolit 300 řádků ===');
// Monolit, ktery zadna granule mit nema (K3 zakazuje „prepis 300 radku“).
writeFileSync(join(SCRATCH, 'scripts', 'monolit.gd'),
  Array.from({ length: 300 }, (_, i) => `func funkce_${i}(x: int) -> int:\n\treturn x + ${i}`).join('\n') + '\n', 'utf8');
const monolitB = readFileSync(join(SCRATCH, 'scripts', 'monolit.gd'), 'utf8').length;
const vsechnySekce = readdirSync(join(SCRATCH, 'CONVENTIONS')).filter((f) => f.endsWith('.md')).sort()
  .map((f) => `CONVENTIONS/${f}`).join('\n');
const zadaniP1 = 'Přepiš soubor v chatu tak, aby měl jen veřejné funkce s výslovnými typy. '
  + 'Zachovej všechny názvy funkcí a jejich návratové typy.';
const p1 = sh(NODE, ['.forge/node/request-budget.mjs', '--zadani-text', zadaniP1,
  '--soubory', 'scripts/monolit.gd', '--konvence', vsechnySekce, ...POSKYTOVATEL]);
test('P1: nafouknutá deklarace = REQUEST_TOO_LARGE (exit 1)',
  p1.kod === 1 && /REQUEST_TOO_LARGE/.test(p1.out + p1.err),
  `exit=${p1.kod}\n${p1.out}\n${p1.err.split('\n')[0] || ''}`);
const cislaP1 = /~(\d+) tokenu/.exec(p1.out);
console.log(`       (monolit ${monolitB} B + všech 9 sekcí → request ~${cislaP1 ? cislaP1[1] : '?'} t)`);

// P1b: TOTEZ pres branu cele roadmapy — vada musi byt pojmenovana i tam.
const fitRoadmapa = join(SCRATCH, '.forge', 'roadmap-p1.json');
const g0 = roadmap.grains[0];
writeFileSync(fitRoadmapa, JSON.stringify({ grains: [{ ...g0, id: 'kontrola.too-large', owns: ['scripts/monolit.gd'], size_lines: 300, konvence: [] }, {
  ...g0, id: 'kontrola.bez-konvenci', konvence: [],
}] }, null, 2), 'utf8');
const p1b = sh(NODE, ['.forge/node/rozpocet-granuli.mjs', '--roadmap', '.forge/roadmap-p1.json', ...POSKYTOVATEL]);
test('P1b: brána roadmapy vadu POJMENUJE (REQUEST_TOO_LARGE / chybějící konvence)',
  p1b.kod === 1 && /REQUEST_TOO_LARGE|nemá deklarované 'konvence'/.test(p1b.out),
  `exit=${p1b.kod}\n${p1b.out.split('\n').slice(-6).join('\n       ')}`);

// ── C) PROTIZKOUSKA P2: cesta v zadání (stav PŘED K1) ───────────────────────
console.log('');
console.log('=== C) PROTIZKOUŠKA P2: cesta k dokumentu v zadání ===');
const ZADANI_M0 = 'Přepiš scripts/game.gd (dnes monolit, 377 řádků) na KOSTRU podle docs/TDD.md §1.1. '
  + 'Komponenty hledají registr (naměřeno v hud.gd, save.gd, combat.gd). '
  + 'Aditivní migrace viz docs/ARCHITEKTURA.md §3. Neměň tests/, .forge/ ani project.godot.';
// P2a: presne to, co delalo potrubi PRED K1 — zadani s cestami a dokument predany
//      do requestu (aider si ho pripjal sam; doslo to k 39 167 t, beh #366).
const p2a = sh(NODE, ['.forge/node/request-budget.mjs', '--zadani-text', ZADANI_M0,
  '--soubory', 'scripts/monolit-real.gd', '--cteni', 'docs/TDD.md\ndocs/ARCHITEKTURA.md', ...POSKYTOVATEL]);
test('P2a: zadání s cestou + přiložené dokumenty = REQUEST_TOO_LARGE (exit 1)',
  p2a.kod === 1 && /REQUEST_TOO_LARGE/.test(p2a.out + p2a.err), `exit=${p2a.kod}\n${p2a.out}`);
const cislaP2 = /~(\d+) tokenu/.exec(p2a.out);
console.log(`       (request ~${cislaP2 ? cislaP2[1] : '?'} t; v CI to 9. 10. 2026 bylo 39 167 t)`);
// P2b: TOTEZ zadani po hygiene → dokument uz do requestu nepatri (nové potrubí).
const hyM0 = sh(NODE, ['.forge/node/prompt-hygiene.mjs', ZADANI_M0]);
test('P2b: hygiena z cesty udělá [dokument] (vada v novém potrubí nevznikne)',
  !/docs\/TDD\.md|docs\/ARCHITEKTURA\.md/.test(hyM0.out) && /\[dokument\]/.test(hyM0.out),
  hyM0.out);
const p2b = sh(NODE, ['.forge/node/request-budget.mjs', '--zadani-text', hyM0.out,
  '--soubory', 'scripts/monolit-real.gd', '--cteni', 'docs/TDD.md\ndocs/ARCHITEKTURA.md', ...POSKYTOVATEL]);
const cislaP2b = /~(\d+) tokenu/.exec(p2b.out);
console.log(`       (po hygiene, ale s dokumenty pořád v requestu: ~${cislaP2b ? cislaP2b[1] : '?'} t —`
  + ` což je přesně to, co K1 samo NEŘEŠÍ: hygiena zabrání PŘILOŽENÍ, ne tomu, co někdo předá ručně)`);

// ── vysledek ────────────────────────────────────────────────────────────────
console.log('');
console.log('=== SUCHÝ BĚH: čísla ===');
for (const v of vysledky) {
  console.log(`  ${v.id.padEnd(20)} ~${String(v.celkem).padStart(5)} t  ${v.trida.padEnd(12)} `
    + `zadání ${String(v.zadani_znaku).padStart(4)} znaků, sekce: ${v.sekce.join(', ')}`);
}
const report = join(SCRATCH, 'vysledek.json');
writeFileSync(report, JSON.stringify({
  kdy: new Date().toISOString(), scratch: SCRATCH, grains: vysledky,
  protizkouska: {
    P1: { exit: p1.kod, request_t: cislaP1 ? Number(cislaP1[1]) : null, strop: 8000, monolit_B: monolitB, sekci: 9 },
    P1b: { exit: p1b.kod },
    P2a: { exit: p2a.kod, request_t: cislaP2 ? Number(cislaP2[1]) : null },
    P2b: { exit: p2b.kod, request_t: cislaP2b ? Number(cislaP2b[1]) : null, zadani_po_hygiene: hyM0.out },
  },
  cely_dokument_B: orig.stdout.length,
}, null, 2), 'utf8');
console.log('');
console.log(`ZMĚŘENO: ${vysledky.length} granulí suchým během, ${vysledky.filter((v) => v.trida === 'FITS').length} FITS, `
  + `2 protizkoušky (P1 ${p1.kod === 1 ? 'SPADLA SPRÁVNĚ' : 'NESPADLA'}, P2a ${p2a.kod === 1 ? 'SPADLA SPRÁVNĚ' : 'NESPADLA'})`);
console.log(`ZMĚŘENO: ${kontrol} kontrol, ${chyb} chyb; report: ${report}`);
if (!ZACHOVAT) console.log(`(scratch zůstává v ${SCRATCH}; smaž ho ručně nebo použij --zachovat při dalším běhu)`);
process.exit(chyb ? 1 : 0);

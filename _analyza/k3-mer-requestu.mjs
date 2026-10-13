#!/usr/bin/env node
// K3 (12. 10. 2026) — MERENI REALNEHO REQUESTU AIDEREM (lokalne, bez kvoty).
//
// PROC: vsechny brany projektu pocitaji tokeny VZORCEM (`znaku / 3,03`). Vzorec
// je kalibrovany, ale je to porad MODEL — a K3 stoji na tom, ze se s deklarovanych
// sekci posle MALY request. Kdyby si aider k sekcim pripjal jeste neco (treba
// soubory zminene V TEXTU sekce), model by lhal a cela uprava by byla k nicemu.
// Jedine, co to rozhodne, je PUSTIT AIDERA a precist, co poslal.
//
// POSTUP: aider se spusti proti FALESNEMU poskytovateli na localhostu, ktery si
// zapise CELY request (presne jak to dela `.tmp/otukani/mer-rezii-aideru.mjs`
// z K1). Z requestu se secte:
//   - system prompt aideru (rezie),
//   - vsechny zpravy, ktere aider poslal (soubory v chatu + zadani),
//   - ktere soubory si aider pripjal ("Added ... to the chat").
//
// CTYRI BEHY (A/B/C/D) — kazdy odpovida na jinou otazku:
//   A) NOVE: pilotni granule `core.level`, zadani po hygiene, 2 deklarovane sekce
//      -> MUSI se vejit (a je to cislo, ktere ma pilot v CI).
//   B) STARE: totéž zadani, ale `--read CONVENTIONS.cely.md` (dokument pred K3)
//      -> kolik K3 usetri na TÉTO granuli.
//   C) M0-RAW: realne zadani M0 (s cestami k dokumentum) + cely dokument
//      -> tohle je stav, na kterem 9. 10. 2026 selhalo 20 behu.
//   D) M0-HYGIENA: totéž zadani po hygiene (K1)
//      -> kolik usetri hygiena (a ze dokument uz nepripne).
//
// Pouziti:
//   node _analyza/k3-mer-requestu.mjs
//   node _analyza/k3-mer-requestu.mjs --jen A

import { createServer } from 'node:http';
import { spawnSync, spawn } from 'node:child_process';
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync, copyFileSync, readdirSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { fileURLToPath } from 'node:url';
import { sanitizuj } from '../repo/.forge/node/prompt-hygiene.mjs';
import { ZNAKU_NA_TOKEN } from '../repo/.forge/node/prompt-hygiene.mjs';
import { rozpocet } from '../repo/.forge/node/request-budget.mjs';
import { celyDokumentPredRozdelenim } from './_revize-konvenci.mjs';

const __dir = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(__dir);
const REPO = join(ORCH, 'repo');
const HRA = join(dirname(ORCH), 'uo-shadows');   // ZMRAZENA: jen cteme
const SCRATCH = join(ORCH, '.tmp', 'k3-mer');
const VENV_PY = join(ORCH, '.tmp', 'otukani', 'venv', 'Scripts', 'python.exe');
const PORT = 8791;
const STROP = 8000;

const jen = (() => { const i = process.argv.indexOf('--jen'); return i >= 0 ? process.argv[i + 1] : ''; })();

if (!existsSync(VENV_PY)) {
  console.error(`CHYBA: chybí aider ve venv (${VENV_PY}) — merení nelze spustit.`);
  console.error('       (Je to MĚŘIDLO, ne brána: bez aideru se nespouští, ale to není zelená.)');
  process.exit(2);
}

// ── scratch: jen to, co aider uvidí ─────────────────────────────────────────
if (existsSync(SCRATCH)) rmSync(SCRATCH, { recursive: true, force: true });
mkdirSync(join(SCRATCH, 'scripts'), { recursive: true });
mkdirSync(join(SCRATCH, 'docs'), { recursive: true });
const SKIP = new Set(['.env', 'provider.env', 'provider.json', '__pycache__']);
function kopiruj(odkud, kam) {
  mkdirSync(kam, { recursive: true });
  for (const e of readdirSync(odkud, { withFileTypes: true })) {
    if (SKIP.has(e.name)) continue;
    const a = join(odkud, e.name); const b = join(kam, e.name);
    if (e.isDirectory()) kopiruj(a, b); else copyFileSync(a, b);
  }
}
kopiruj(join(REPO, '.forge'), join(SCRATCH, '.forge'));
kopiruj(join(REPO, 'CONVENTIONS'), join(SCRATCH, 'CONVENTIONS'));
copyFileSync(join(REPO, 'CONVENTIONS.md'), join(SCRATCH, 'CONVENTIONS.md'));
// POZOR: bere se revize PŘED rozdělením konvencí, ne `HEAD` — po commitu K3/K4
// je v HEAD už rozcestník a měření by jako „starý stav“ četlo 836 t místo
// celého dokumentu (3 802 t). Řeší společný helper.
const origText = celyDokumentPredRozdelenim();
if (!origText) { console.error('CHYBA: původní CONVENTIONS.md z gitu nejde přečíst'); process.exit(2); }
const orig = { stdout: origText };
writeFileSync(join(SCRATCH, 'CONVENTIONS.cely.md'), orig.stdout, 'utf8');
// Realne soubory zmrazene hry (jen cteme) — pro behy C a D.
for (const [z, c] of [['scripts/game.gd', 'scripts/monolit-real.gd'], ['scripts/registry.gd', 'scripts/registry.gd'],
  ['docs/TDD.md', 'docs/TDD.md'], ['docs/ARCHITEKTURA.md', 'docs/ARCHITEKTURA.md']]) {
  const zdroj = join(HRA, z);
  if (existsSync(zdroj)) copyFileSync(zdroj, join(SCRATCH, c));
}
// Soubor granul pilotu (workflow do neexistujiciho souboru zapise prazdny).
writeFileSync(join(SCRATCH, 'scripts', 'level.gd'), '', 'utf8');

// ⚠ GIT JE PODSTATNY: aider hleda soubory zminene v zadani (`get_file_mentions`)
// mezi TRACKED soubory repa. Bez gitu zadny seznam nema — a pak se cesta
// v zadani „nechyti“ a mereni by tvrdilo, ze vada neexistuje (presne to se
// stalo v prvnim behu: dokumenty se nepripjaly a behy C/D vysly temer stejne).
spawnSync('git', ['init', '-q'], { cwd: SCRATCH });
spawnSync('git', ['config', 'user.email', 'k3@localhost'], { cwd: SCRATCH });
spawnSync('git', ['config', 'user.name', 'K3'], { cwd: SCRATCH });
spawnSync('git', ['add', '-A'], { cwd: SCRATCH });
spawnSync('git', ['commit', '-q', '-m', 'scratch'], { cwd: SCRATCH });

// Fragment z realneho dokumentu (radek bez uvozovek, aby ho escapovani JSON
// nezmenilo) — podle nej se DOKAZUJE, ze si aider dokument pripjal sam.
// Bez toho by tvrzeni „pripjal“ bylo odvozeno z delky, ne z obsahu.
function fragment(soubor) {
  const p = join(SCRATCH, 'docs', soubor);
  if (!existsSync(p)) return null;
  const radek = readFileSync(p, 'utf8').split('\n')
    .find((l) => l.trim().length > 40 && !/["\\]/.test(l));
  return radek ? radek.trim().slice(0, 50) : null;
}
const FRAGMENTY = { 'docs/TDD.md': fragment('TDD.md'), 'docs/ARCHITEKTURA.md': fragment('ARCHITEKTURA.md') };

let zachycene = [];
const srv = createServer((req, res) => {
  let telo = '';
  req.on('data', (c) => { telo += c; });
  req.on('end', () => {
    if (req.url.endsWith('/models')) {
      res.writeHead(200, { 'content-type': 'application/json' });
      res.end(JSON.stringify({ data: [{ id: 'openai/gpt-oss-120b' }] }));
      return;
    }
    let zpravy = [];
    try { zpravy = JSON.parse(telo).messages || []; } catch { /* ignore */ }
    zachycene.push({
      celkem_znaku: telo.length,
      po_zpravach: zpravy.map((m) => ({ role: m.role, znaku: String(m.content || '').length })),
      v_requestu: Object.fromEntries(Object.entries(FRAGMENTY)
        .map(([n, f]) => [n, f ? telo.includes(f) : null])),
    });    res.writeHead(200, { 'content-type': 'application/json' });
    res.end(JSON.stringify({
      id: 'x', object: 'chat.completion', created: 1, model: 'openai/gpt-oss-120b',
      choices: [{ index: 0, message: { role: 'assistant', content: '' }, finish_reason: 'stop' }],
      usage: { prompt_tokens: 0, completion_tokens: 0, total_tokens: 0 },
    }));
  });
});
await new Promise((r) => srv.listen(PORT, '127.0.0.1', r));

function aider(args, zadani) {
  return new Promise((resolve) => {
    zachycene = [];
    const a = spawn(VENV_PY, ['-m', 'aider', '--model', 'openai/openai/gpt-oss-120b',
      ...args, '--map-tokens', '0', '--edit-format', 'diff', '--message', zadani,
      '--yes', '--no-auto-commits', '--no-stream', '--no-check-update',
    ], {
      cwd: SCRATCH,
      env: { ...process.env, OPENAI_API_BASE: `http://127.0.0.1:${PORT}/v1`, OPENAI_API_KEY: 'test' },
    });
    let vystup = '';
    a.stdout.on('data', (d) => { vystup += d; });
    a.stderr.on('data', (d) => { vystup += d; });
    a.on('close', () => resolve(vystup));
  });
}

// ── zadani ──────────────────────────────────────────────────────────────────
const ZADANI_M0 = 'Přepiš scripts/game.gd (dnes monolit, 377 řádků) na KOSTRU podle docs/TDD.md §1.1. '
  + 'Komponenty hledají registr (naměřeno v hud.gd, save.gd, combat.gd). '
  + 'Aditivní migrace viz docs/ARCHITEKTURA.md §3. Neměň tests/, .forge/ ani project.godot.';
const roadmap = JSON.parse(readFileSync(join(REPO, '.forge', 'roadmap.pilot.json'), 'utf8'));
const gLevel = roadmap.grains.find((g) => g.id === 'core.level');
const ZADANI_PILOT = sanitizuj(gLevel.prompt, { koren: SCRATCH }).text;
const ZADANI_M0_HYG = sanitizuj(ZADANI_M0, { koren: SCRATCH }).text;

// ── behy ────────────────────────────────────────────────────────────────────
const BEHY = [
  {
    id: 'A', nazev: 'NOVĚ: pilotní granule, 2 deklarované sekce',
    args: ['--read', 'CONVENTIONS/01-typy.md', '--read', 'CONVENTIONS/06-soubor-granule.md',
      '--file', 'scripts/level.gd'],
    zadani: ZADANI_PILOT,
    model: { soubory: ['scripts/level.gd'], cteni: [], konvence: ['CONVENTIONS/01-typy.md', 'CONVENTIONS/06-soubor-granule.md'] },
    srovnej: true,
    ceka: { max_t: 7000 },
  },
  {
    id: 'B', nazev: 'STARĚ: totéž zadání, celý dokument před K3',
    args: ['--read', 'CONVENTIONS.cely.md', '--file', 'scripts/level.gd'],
    zadani: ZADANI_PILOT,
    model: { soubory: ['scripts/level.gd'], cteni: [], konvence: ['CONVENTIONS.cely.md'] },
    srovnej: true,
    ceka: {},
  },
  {
    id: 'C', nazev: 'M0-RAW: zadání s cestami (stav před K1)',
    args: ['--read', 'CONVENTIONS.cely.md', '--read', 'scripts/registry.gd', '--file', 'scripts/monolit-real.gd'],
    zadani: ZADANI_M0,
    srovnej: false,   // model NEMŮŽE znát soubory, které si aider připne sám z cest
    ceka: { min_t: STROP + 1, pripnout: ['docs/TDD.md', 'docs/ARCHITEKTURA.md'] },
  },
  {
    id: 'D', nazev: 'M0-HYGIENA: totéž zadání po hygieně (K1)',
    args: ['--read', 'CONVENTIONS.cely.md', '--read', 'scripts/registry.gd', '--file', 'scripts/monolit-real.gd'],
    zadani: ZADANI_M0_HYG,
    model: { soubory: ['scripts/monolit-real.gd'], cteni: ['scripts/registry.gd'], konvence: ['CONVENTIONS.cely.md'] },
    srovnej: true,
    ceka: { pripnout: [] },
  },
];

let kontrol = 0; let chyb = 0;
const test = (n, ok, d = '') => { kontrol++; if (ok) console.log(`ok     ${n}`); else { chyb++; console.log(`CHYBA  ${n}${d ? `\n       ${d}` : ''}`); } };

console.log(`Měření aiderem ${readFileSync(VENV_PY.replace('Scripts\\python.exe', 'pyvenv.cfg'), 'utf8').match(/version = (.*)/)?.[1] || '?'}`
  + ` | scratch: ${SCRATCH} | strop: ${STROP} t | ${ZNAKU_NA_TOKEN} znaku/token`);
console.log('');
const vysledky = [];
for (const b of BEHY) {
  if (jen && b.id !== jen) continue;
  const vystup = await aider(b.args, b.zadani);
  const z = zachycene[0];
  const sys = (z?.po_zpravach || []).filter((x) => x.role === 'system').reduce((a, x) => a + x.znaku, 0);
  const usr = (z?.po_zpravach || []).filter((x) => x.role !== 'system').reduce((a, x) => a + x.znaku, 0);
  const celkemZnaku = z?.celkem_znaku ?? 0;
  const tokenu = Math.ceil(celkemZnaku / ZNAKU_NA_TOKEN);
  const pripnute = [...vystup.matchAll(/Added ([^\s]+) to the chat/g)].map((m) => m[1]);
  const vRequestu = z?.v_requestu || {};
  const vysledek = {
    id: b.id, nazev: b.nazev, znaku: celkemZnaku, tokenu, sysZnaku: sys, usrZnaku: usr, pripnute,
    zadani_znaku: b.zadani.length, v_requestu: vRequestu,
    zpravy: z?.po_zpravach || [],
    vystup_tail: vystup.split('\n').filter((l) => /Added|Warning|Skipping|error/.test(l)).slice(0, 12),
  };
  vysledky.push(vysledek);
  console.log(`── ${b.id}) ${b.nazev}`);
  console.log(`   request: ${celkemZnaku} znaků ~ ${tokenu} t (z toho systém ${sys} zn. ~ ${Math.ceil(sys / ZNAKU_NA_TOKEN)} t,`
    + ` zbytek ${usr} zn. ~ ${Math.ceil(usr / ZNAKU_NA_TOKEN)} t)`);
  console.log(`   aider si přidal do chatu: ${pripnute.length ? pripnute.join(', ') : '(nic)'}`);
  console.log(`   zprávy requestu: ${(z?.po_zpravach || []).map((x) => `${x.role}=${x.znaku}`).join(' ')}`);
  for (const l of vysledek.vystup_tail) console.log(`   aider> ${l.slice(0, 160)}`);
  if (b.ceka.max_t !== undefined) test(`${b.id}: request <= ${b.ceka.max_t} t`, tokenu <= b.ceka.max_t, `naměřeno ${tokenu} t`);
  if (b.ceka.min_t) test(`${b.id}: request > ${b.ceka.min_t - 1} t (vada se opravdu projeví)`, tokenu >= b.ceka.min_t, `naměřeno ${tokenu} t`);
  if (b.ceka.pripnout !== undefined) {
    for (const f of b.ceka.pripnout) {
      test(`${b.id}: ${f} je OPRAVDU v requestu (dokázáno obsahem, ne délkou)`, vRequestu[f] === true,
        `v requestu: ${JSON.stringify(vRequestu)}`);
    }
  }
  // SROVNANI MODELU S MERENIM: model musi byt KONZERVATIVNI (nikdy nizsi).
  if (b.srovnej && b.model) {
    const m = rozpocet({
      zadaniText: b.zadani, soubory: b.model.soubory.join('\n'), cteni: b.model.cteni.join('\n'),
      konvence: b.model.konvence.join('\n'), strop: STROP, koren: SCRATCH,
    });
    vysledek.model_t = m.celkem;
    console.log(`   model (request-budget.mjs): ${m.celkem} t vs naměřeno ${tokenu} t → `
      + `${m.celkem >= tokenu ? 'konzervativní' : 'OPTIMISTICKÝ'} o ${Math.abs(m.celkem - tokenu)} t`);
    test(`${b.id}: model je konzervativní (model >= naměřeno)`, m.celkem >= tokenu,
      `model ${m.celkem} t < naměřeno ${tokenu} t — konstanta obalu zadání je nízká`);
  }
  console.log('');
}

// ── souhrn a tvrzeni, ktera z mereni plynou ─────────────────────────────────
const A = vysledky.find((v) => v.id === 'A');
const B = vysledky.find((v) => v.id === 'B');
const C = vysledky.find((v) => v.id === 'C');
const D = vysledky.find((v) => v.id === 'D');
console.log('=== SOUHRN ===');
if (A && B) {
  console.log(`  A (deklarované sekce) vs B (celý dokument před K3): ~${A.tokenu} t vs ~${B.tokenu} t`
    + ` → úspora ~${B.tokenu - A.tokenu} t na jedné granulе`);
  test('A je menší než B (rozdělení konvencí něco ušetří)', A.tokenu < B.tokenu,
    `A=${A.tokenu}, B=${B.tokenu}`);
}
if (C) console.log(`  C (M0 s cestami, před K1): ~${C.tokenu} t → ${C.tokenu > STROP ? 'PŘES STROP (a to je ta vada)' : 'vešlo se'}`);
if (D) console.log(`  D (M0 po hygiene): ~${D.tokenu} t → ${D.tokenu > STROP ? 'POŘÁD přes strop: hygiena sama NESTAČÍ' : 'vešlo se'}`);
if (C && D) {
  console.log(`  hygiena ušetřila ~${C.tokenu - D.tokenu} t (připnuté dokumenty) —`
    + ` a přesto je D ${D.tokenu > STROP ? 'nad stropem' : 'pod stropem'}:`
    + ` zbývá monolit 377 řádků + celý dokument konvencí.`);
  test('D je menší než C (hygiena má měřitelný efekt)', D.tokenu < C.tokenu, `C=${C.tokenu}, D=${D.tokenu}`);
}
if (A) test('A: model počítá request věrně — naměřeno aiderem se vejde pod 7 000 t', A.tokenu <= 7000, `naměřeno ${A.tokenu} t`);

const report = join(SCRATCH, 'mer-requestu.json');
writeFileSync(report, JSON.stringify({
  kdy: new Date().toISOString(), strop: STROP, znaku_na_token: ZNAKU_NA_TOKEN,
  behy: vysledky,
  poznamka: 'tokeny = znaku requestu / 3,03 (stejná konstanta jako v request-budget.mjs); '
    + 'NENI to usage.prompt_tokens z API — je to velikost tela requestu, tedy horni odhad toho, co API vidi.',
}, null, 2), 'utf8');
console.log('');
console.log(`ZMĚŘENO: ${vysledky.length} běhů aiderem, ${kontrol} kontrol, ${chyb} chyb`);
console.log(`ZMĚŘENO: report ${report}`);
srv.close();
process.exit(chyb ? 1 : 0);

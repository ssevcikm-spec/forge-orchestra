import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Ověří CI workflow bez GitHubu: YAML je platný, kroky sedí, odkazy na soubory
// existují a pořadí kroků odpovídá tomu, co je potřeba.
//
// PROČ TO EXISTUJE: chyba v `ci.yml` se v provozu projeví jako „CI je červené"
// a nikdo nepozná proč. Tenhle test zkontroluje offline to, co se zkontrolovat
// dá: strukturu, existenci volaných souborů a kritické pořadí.
//
// POŘADÍ, KTERÉ SE KONTROLUJE (a proč):
//   1) import assetů  – bez něj Godot v --script režimu assety nenačte
//   2) kontrola schématu – vision nemá proti čemu měřit, když si hra odporuje
//   3) testy, assety, wiring, smoke
//   4) snímek hry     – vyrábí /tmp/frames/frame*.png
//   5) vision         – čte ten snímek, takže MUSÍ být po něm
//
// Spuštění: node orchestra/tools/test-ci-workflow.mjs
// Návratový kód: 0 = OK, 1 = chyba.

import { existsSync, readFileSync } from 'node:fs';

let ok = 0;
let chyb = 0;
function test(nazev, podminka, detail = '') {
  if (podminka) {
    console.log(`  OK   ${nazev}`);
    ok++;
  } else {
    console.log(`  FAIL ${nazev}${detail ? ` – ${detail}` : ''}`);
    chyb++;
  }
}

const CILE = [
  ['uo-shadows', join(PARENT, 'uo-shadows')],
  ['repo (šablona)', join(PARENT, 'repo')],
];

for (const [nazev, koren] of CILE) {
  console.log(`\n=== ${nazev} ===`);
  const ci = `${koren}/.github/workflows/ci.yml`;
  if (!existsSync(ci)) {
    test(`${nazev}: ci.yml existuje`, false, ci);
    continue;
  }
  const text = readFileSync(ci, 'utf8');

  // --- YAML: odsazení a struktura -------------------------------------------------
  test('nemá taby (YAML je zakazuje)', !/\t/.test(text));
  test('má právě jeden blok "jobs:"', (text.match(/^jobs:/gm) ?? []).length === 1);
  const kroky = [...text.matchAll(/^ {6}- name: (.+)$/gm)].map((m) => m[1]);
  test('kroků je rozumně (>= 8)', kroky.length >= 8, `nalezeno ${kroky.length}`);
  test('každý krok má "run:" nebo "uses:"',
    kroky.every((k, i) => {
      const od = text.indexOf(`      - name: ${k}`);
      const do2 = i + 1 < kroky.length
        ? text.indexOf(`      - name: ${kroky[i + 1]}`)
        : text.length;
      const blok = text.slice(od, do2);
      return /\n {8}(run|uses):/.test(blok);
    }));

  // --- odkazy na soubory musí existovat ------------------------------------------
  const volane = [...text.matchAll(/(?:python3|node|bash)\s+(\.forge\/[\w.\-]+)/g)]
    .map((m) => m[1]);
  for (const f of new Set(volane)) {
    test(`volaný soubor existuje: ${f}`, existsSync(`${koren}/${f}`), `${koren}/${f}`);
  }
  test('CI volá kontrolu schématu', volane.includes('.forge/check-schema.py'),
    volane.join(', '));
  test('CI volá vision', volane.includes('.forge/vision.mjs'), volane.join(', '));

  // --- pořadí: vision až po vyrobení snímku ---------------------------------------
  const iSnimek = text.indexOf('write-movie');
  const iVision = text.indexOf('.forge/vision.mjs');
  test('snímek se vyrábí PŘED vision', iSnimek >= 0 && iVision > iSnimek,
    `snimek@${iSnimek}, vision@${iVision}`);
  const iSchema = text.indexOf('check-schema.py');
  test('kontrola schématu je PŘED vision (vision potřebuje vědět, proti čemu měří)',
    iSchema >= 0 && iSchema < iVision, `schema@${iSchema}, vision@${iVision}`);
  const iImport = text.indexOf('--import');
  test('import assetů je PŘED kontrolou schématu', iImport >= 0 && iImport < iSchema,
    `import@${iImport}, schema@${iSchema}`);

  // --- vision NESMÍ blokovat ------------------------------------------------------
  // Blok se bere od `- name:` kroku s vision, ne od zmínky o souboru – jinak by
  // se do něj nevešlo `continue-on-error`, které je nad `run:`.
  const iVisionKrok = text.lastIndexOf('      - name:', iVision);
  const blokVision = text.slice(iVisionKrok, iVision + 1200);
  test('vision má continue-on-error (neblokuje slučování)',
    /continue-on-error:\s*true/.test(blokVision), blokVision.slice(0, 140));
  test('vision končí na "|| echo" (výpadek kvóty není chyba hry)',
    /\|\|\s*echo/.test(blokVision), blokVision.slice(0, 160));
  // Kontrola klíčů je v shellu jako `[ -z "$DEEPSEEK_API_KEY" ]` a v env jako
  // `secrets.DEEPSEEK_API_KEY` – hledá se obojí, protože řešení se může lišit.
  test('vision se přeskočí, když není klíč',
    /\[\s*-z\s+"?\$?\{?\{?\s*(secrets\.)?DEEPSEEK_API_KEY/.test(blokVision)
    && /GEMINI_API_KEY/.test(blokVision),
    'chybí kontrola klíčů před voláním');
}

console.log();
console.log(`Testů OK: ${ok}, chyb: ${chyb}`);
console.log(chyb === 0 ? 'VŠE OK' : 'NALEZENY CHYBY');
process.exit(chyb === 0 ? 0 : 1);

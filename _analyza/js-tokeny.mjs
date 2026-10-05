// Analyzátor JS/TS přes SKUTEČNÝ PARSER TypeScriptu — náhrada za ruční lexer.
//
// PROČ TO EXISTUJE (naměřeno 1. 10. 2026): ruční lexer v
// `_analyza/hl-neanglicky-v-kodu.py` měl heuristic na rozlišení dělení `/` od
// regulárního výrazu a **čtyřikrát za sebou selhal** na skutečném kódu:
//   1. český identifikátor v TS mu unikl (sbíral jen literály)
//   2. `/Kontroluji parsování|Agent nezměnil žádný/` → 690 falešných identifikátorů
//   3. obsah šablony (backtick) bral jako jména
//   4. `analyza-aktualni.mjs:30` má **neukončený** regex → heuristika se zahořila
//      uprostřed a `tvrdý` z dalšího řádku vyhlásila za identifikátor
//
// POUČENÍ 1: kde je po ruce skutečný nástroj, NEMÁ se psát vlastní.
// POUČENÍ 2 (druhé kolo): ani **scanner** TypeScriptu nestačí — jde token po
// tokenu a na syntakticky vadném souboru se **rozsype** (naměřeno: v
// `analyza-aktualni.mjs` vyrobil „řetězec" přes pět řádků, protože uvozovku
// v komentáři vzal jako začátek literálu a nenašel konec). **Parser** se naopak
// vzpamatuje: u vadného uzlu zapíše chybu a pokračuje dál. Proto se používá
// `ts.createSourceFile`, ne `ts.createScanner`.
//
// Použití:
//   node _analyza/js-tokeny.mjs <soubor> [<soubor>...]
// Výstup (stdout, JSON): [{ soubor, jazyk, chyba, syntaxErrors, tokeny }]
//   tokeny = [{ typ, text, radek, kontext }]
//     typ: "identifikator" | "retezec" | "sablona" | "regex"
//     kontext: deklarace / porovnání / klíč objektu / hodnota / volání / text

import { readFileSync } from 'node:fs';
import { createRequire } from 'node:module';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const require = createRequire(import.meta.url);
const KOREN = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');

let ts = null;
let tsChyba = null;
// ⚠ P13c (4. 10. 2026, táž třída jako H48/H52): tady stálo
// `path.join(KOREN, 'orchestra', 'conductor', 'node_modules', 'typescript')` —
// tedy cesta ze STARÉHO layoutu. Po přesunu na `E:` TypeScript **nebyl
// nalezen**, `ts` zůstal `null` a **všech 68 JS/TS souborů** skončilo
// v NEPOKRYTO („parser to nepřečetl"). Navenek to vypadalo, že skener
// „něco neměří" — a byl to jen rozbitý `require`.
//
// Cesta se proto ODVOZUJE z umístění tohohle souboru (`_analyza/..` = kořen
// repa) a hledá se na obvyklých místech; když se nenajde, řekne se to
// (`tsChyba`) — tichý `null` by znamenal 68 nezměřených souborů.
const KANDIDATI_TS = [
  path.join(KOREN, 'conductor', 'node_modules', 'typescript'),
  path.join(KOREN, 'node_modules', 'typescript'),
];
for (const kandidat of KANDIDATI_TS) {
  try {
    ts = require(kandidat);
    break;
  } catch (e) {
    tsChyba = `typescript nejde načíst z ${kandidat}: ${e.message}`;
  }
}

const neascii = (s) => /[^\x00-\x7F]/.test(s);

const POPIS_UZLU = {
  [ts?.SyntaxKind.VariableDeclaration ?? -1]: 'deklarace proměnné',
  [ts?.SyntaxKind.FunctionDeclaration ?? -1]: 'deklarace funkce',
  [ts?.SyntaxKind.ClassDeclaration ?? -1]: 'deklarace třídy',
  [ts?.SyntaxKind.Parameter ?? -1]: 'parametr funkce',
  [ts?.SyntaxKind.PropertyAssignment ?? -1]: 'klíč objektu',
  [ts?.SyntaxKind.PropertyDeclaration ?? -1]: 'klíč objektu (třída)',
  [ts?.SyntaxKind.MethodDeclaration ?? -1]: 'klíč objektu (metoda)',
  [ts?.SyntaxKind.BindingElement ?? -1]: 'rozbalené jméno',
  [ts?.SyntaxKind.ImportSpecifier ?? -1]: 'import',
  [ts?.SyntaxKind.PropertyAccessExpression ?? -1]: 'přístup k vlastnosti',
  [ts?.SyntaxKind.BinaryExpression ?? -1]: 'POROVNÁNÍ',
  [ts?.SyntaxKind.CaseClause ?? -1]: 'POROVNÁNÍ (case)',
  [ts?.SyntaxKind.CallExpression ?? -1]: 'volání funkce',
  [ts?.SyntaxKind.NewExpression ?? -1]: 'volání konstruktoru',
  [ts?.SyntaxKind.ExpressionStatement ?? -1]: 'výraz',
  [ts?.SyntaxKind.ReturnStatement ?? -1]: 'návratová hodnota',
  [ts?.SyntaxKind.ThrowStatement ?? -1]: 'vyhozená chyba',
  [ts?.SyntaxKind.JsxAttribute ?? -1]: 'atribut JSX',
};

/** Porovnávací operátory — u nich je literál ROZHODOVACÍ, ne popisný. */
const POROVNAVACI = new Set([
  ts?.SyntaxKind.EqualsEqualsToken, ts?.SyntaxKind.EqualsEqualsEqualsToken,
  ts?.SyntaxKind.ExclamationEqualsToken, ts?.SyntaxKind.ExclamationEqualsEqualsToken,
  ts?.SyntaxKind.LessThanToken, ts?.SyntaxKind.GreaterThanToken,
  ts?.SyntaxKind.LessThanEqualsToken, ts?.SyntaxKind.GreaterThanEqualsToken,
].filter((x) => x !== undefined));

function kontextUzlu(uzel) {
  let p = uzel.parent;
  while (p) {
    const popis = POPIS_UZLU[p.kind];
    if (popis) {
      if (popis === 'POROVNÁNÍ' && !POROVNAVACI.has(p.operatorToken?.kind)) {
        p = p.parent;          // `+`, `&&` … není porovnání
        continue;
      }
      return popis;
    }
    if (p.kind === ts.SyntaxKind.SourceFile) break;
    p = p.parent;
  }
  return 'nezařazeno';
}

/** Projde strom a vytáhne každý neanglický literál i jméno s kontextem. */
function projdi(uzel, kod, vystup, jeKlic) {
  const k = uzel.kind;
  const radek = (pozice) => kod.slice(0, pozice).split('\n').length;

  // JMÉNA (identifikátory) — včetně diakritiky
  if (k === ts.SyntaxKind.Identifier || k === ts.SyntaxKind.PrivateIdentifier) {
    if (neascii(uzel.text)) {
      vystup.push({ typ: 'identifikator', text: uzel.text,
                    radek: radek(uzel.getStart()), kontext: kontextUzlu(uzel) });
    }
  }

  // LITERÁLY
  const jeRetezec = k === ts.SyntaxKind.StringLiteral ||
                    k === ts.SyntaxKind.NoSubstitutionTemplateLiteral;
  const jeRegex = k === ts.SyntaxKind.RegularExpressionLiteral;

  if ((jeRetezec || jeRegex) && typeof uzel.text === 'string' && neascii(uzel.text)) {
    let ctx = kontextUzlu(uzel);
    // Klíč objektu: `{ "klíč": … }` — tam jde o identifikátor, ne o popis.
    if (jeRetezec && uzel.parent?.kind === ts.SyntaxKind.PropertyAssignment &&
        uzel.parent?.name === uzel) {
      ctx = 'KLÍČ OBJEKTU (může být identifikátor)';
    }
    vystup.push({ typ: jeRegex ? 'regex' : 'retezec', text: uzel.text,
                  radek: radek(uzel.getStart()), kontext: ctx });
  }

  // Obsah šablony: TemplateHead/Middle/Tail mají `.text` (část před ${}),
  // TemplateExpression text NEMÁ — proto se bere syrový zdroj a ${} se odřízne.
  const jeCastSablony = k === ts.SyntaxKind.TemplateHead ||
                        k === ts.SyntaxKind.TemplateMiddle ||
                        k === ts.SyntaxKind.TemplateTail ||
                        k === ts.SyntaxKind.NoSubstitutionTemplateLiteral;
  if (jeCastSablony) {
    const syrovy = kod.slice(uzel.getStart(), uzel.getEnd());
    const cisty = syrovy.replace(/^\$\{/, '').replace(/\}$/, '').replace(/^`|`$/g, '');
    if (neascii(cisty)) {
      vystup.push({ typ: 'sablona', text: cisty.slice(0, 200),
                    radek: radek(uzel.getStart()), kontext: kontextUzlu(uzel) });
    }
  }

  ts.forEachChild(uzel, (dite) => projdi(dite, kod, vystup, false));
}

const vysledek = [];

// Seznam souborů může přijít argumenty, nebo souborem (`--seznam <cesta>`) —
// 100+ cest naráz přesáhne limit příkazové řádky Windows.
let seznamCest = process.argv.slice(2);
const iSeznam = seznamCest.indexOf('--seznam');
if (iSeznam >= 0) {
  const souborSeznamu = seznamCest[iSeznam + 1];
  seznamCest = readFileSync(souborSeznamu, 'utf8')
    .split(/\r?\n/).map((s) => s.trim()).filter(Boolean);
}

for (const cesta of seznamCest) {
  if (cesta.endsWith('.gd')) {
    vysledek.push({ soubor: cesta, jazyk: 'gdscript',
                    chyba: 'TypeScript parser neumí GDScript — použij textovou analýzu' });
    continue;
  }
  if (!ts) {
    vysledek.push({ soubor: cesta, jazyk: 'js', chyba: tsChyba });
    continue;
  }
  let kod;
  try {
    kod = readFileSync(cesta, 'utf8');
  } catch (e) {
    vysledek.push({ soubor: cesta, chyba: `nejde přečíst: ${e.message}` });
    continue;
  }
  try {
    const zdrojak = ts.createSourceFile(cesta, kod, ts.ScriptTarget.Latest,
                                        /* setParentNodes */ true,
                                        cesta.endsWith('.ts') ? ts.ScriptKind.TS
                                                              : ts.ScriptKind.JS);
    const tokeny = [];
    projdi(zdrojak, kod, tokeny, false);
    // Syntaktické chyby se HLÁSÍ, nepolykají: bez toho by „0 nálezů"
    // u vadného souboru vypadalo jako změřená nula.
    const syntaxErrors = (zdrojak.parseDiagnostics ?? []).length;
    vysledek.push({ soubor: cesta,
                    jazyk: cesta.endsWith('.ts') ? 'typescript' : 'javascript',
                    chyba: null, syntaxErrors, tokeny });
  } catch (e) {
    vysledek.push({ soubor: cesta, chyba: `parser spadl: ${String(e.message).slice(0, 100)}` });
  }
}

process.stdout.write(JSON.stringify(vysledek));

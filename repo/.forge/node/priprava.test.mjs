#!/usr/bin/env node
// Test pripravy orchestry (K1 + K2): hygiena zadani, rozpocet requestu,
// klasifikace selhani. Bez site, bez klice, bez zapisu na disk.
//
// POZOR: test ZAMERNE obsahuje KALIBRACNI KONTROLU - pripad, ktery by podle
// STAREHO predpokladu ("znaky/4") prosel, ale podle namereneho (3,03) projit
// nesmi. Kdyby se konstanta vratila na 4, test SPADNE - jinak by jen tvrdil,
// ze neco prošlo, a to neni dukaz, ze to meri.
//
// Spousteni:  node .forge/node/priprava.test.mjs

import { sanitizuj } from './prompt-hygiene.mjs';
import { rozpocet, tokeny, rozhodni, REZIE_HARNESSU } from './request-budget.mjs';
import { klasifikuj, cislaZLogu, prvniChyba } from './classify-agent-log.mjs';

let kontroly = 0;
let chyb = 0;
const test = (nazev, skutecne, ocekavane) => {
  kontroly++;
  const ok = JSON.stringify(skutecne) === JSON.stringify(ocekavane);
  if (!ok) { chyb++; console.log(`CHYBA  ${nazev}\n       ocekavano: ${JSON.stringify(ocekavane)}\n       namereno:  ${JSON.stringify(skutecne)}`); }
  else console.log(`ok     ${nazev}`);
};

// ── K1a: hygiena zadani ───────────────────────────────────────────────────────
console.log('=== K1a: hygiena zadani (cesty se nesmi dostat k aideru) ===');
const ZADANI_M0 = 'Přepiš scripts/game.gd (dnes monolit, 377 řádků) na KOSTRU podle docs/TDD.md §1.1. '
  + 'Komponenty hledají registr (naměřeno v hud.gd, save.gd, combat.gd). '
  + 'Aditivní migrace viz docs/ARCHITEKTURA.md §3. Neměň tests/, .forge/ ani project.godot.';
const h = sanitizuj(ZADANI_M0, { koren: '.' });
test('hygiena: zadani uz neobsahuje cestu k dokumentu', /docs\/TDD\.md|docs\/ARCHITEKTURA\.md/.test(h.text), false);
test('hygiena: zadani uz neobsahuje cestu ke skriptu', /scripts\/game\.gd/.test(h.text), false);
test('hygiena: dokument je oznacen', h.text.includes('[dokument]'), true);
test('hygiena: soubor je oznacen', h.text.includes('[soubor]'), true);
test('hygiena: zminky jsou pojmenovane (doklad)', h.zminky.length >= 3, true);
test('hygiena: text zustal jinak doslova', h.text.includes('na KOSTRU'), true);
const ciste = sanitizuj('Vytvoř soubor pro výpočet a vrať true.', { koren: '.' });
test('hygiena: zadani bez cest se NEMENI', ciste.text, 'Vytvoř soubor pro výpočet a vrať true.');
test('hygiena: bez cest zadna zminka', ciste.zminky.length, 0);

// ── K1b: rozpocet requestu ────────────────────────────────────────────────────
console.log('\n=== K1b: rozpocet requestu (strop 8000 = Groq zdarma) ===');
test('kalibrace: 30 300 znaku = 10 000 tokenu (3,03 znaku/token)', tokeny(30300), 10000);
const maly = rozpocet({ zadaniText: 'ahoj', strop: 8000, rezije: 0 });
test('maly request se vejde', maly.vejde_se, true);
const velky = rozpocet({ zadaniText: 'x'.repeat(16000), strop: 8000, rezije: REZIE_HARNESSU });
test('KALIBRACNI KONTROLA: 16 000 znaku se pri 3,03 znaku/token NEVEJDE', velky.vejde_se, false);
test('KALIBRACNI KONTROLA: pritom stary odhad (znaky/4) by se vesel', 16000 / 4 + REZIE_HARNESSU <= 8000, true);
const skutecny = rozpocet({ zadaniText: 'x'.repeat(3200), strop: 8000, rezije: 0 });
test('rozpocet secte zadani + rezii', skutecny.celkem, tokeny(3200));
test('rozpocet vraci zbyvajici kvotu (vztah, ne hranicni hodnota)', rozpocet({ zadaniText: 'x'.repeat(3000), strop: 8000, rezije: 0 }).zbyva, 8000 - tokeny(3000));
// Brana: namereny strop se vynucuje, odhad jen varuje (jinak by nezmereny
// poskytovatel blokoval praci, kterou by zvladl).
const presStrop = rozpocet({ zadaniText: 'x'.repeat(30000), strop: 8000, rezije: 0 });
test('namereny strop pres strop = TOO_LARGE', rozhodni(presStrop, 'mereno'), 'TOO_LARGE');
test('rucni strop pres strop = TOO_LARGE', rozhodni(presStrop, 'rucni'), 'TOO_LARGE');
test('odhadnuty strop pres strop jen VARUJE', rozhodni(presStrop, 'odhad'), 'NEZNAMY_STROP');
test('vejit se = FITS', rozhodni(rozpocet({ zadaniText: 'x'.repeat(300), strop: 8000, rezije: 0 }), 'mereno'), 'FITS');

// ── K2: klasifikace selhani ───────────────────────────────────────────────────
console.log('\n=== K2: klasifikace selhani (realne texty z logu 9. 10.) ===');
const TOO_LARGE = 'litellm.RateLimitError: RateLimitError: OpenAIException - Request too large for model '
  + '`openai/gpt-oss-120b` ... tokens per minute (TPM): Limit 8000, Requested 27557, please reduce your '
  + 'message size. The API provider has rate limited you.';
const KVOTA = 'litellm.RateLimitError: RateLimitError: OpenAIException - Tokens per minute limit exceeded - '
  + 'too many tokens processed.';
const AUTH = 'litellm.AuthenticationError: OpenAIException - Incorrect API key provided: sk-***';
const DOWN = 'openai.APIConnectionError: APIConnectionError: Error code: 503 - upstream unavailable';
test('velky request = REQUEST_TOO_LARGE (ne kvota!)', klasifikuj({ log: TOO_LARGE, zmena: 'ne' }), 'REQUEST_TOO_LARGE');
test('vycerpany limit = QUOTA', klasifikuj({ log: KVOTA, zmena: 'ne' }), 'QUOTA');
test('spatny klic = AUTH', klasifikuj({ log: AUTH }), 'AUTH');
test('nedostupny poskytovatel = PROVIDER_DOWN', klasifikuj({ log: DOWN }), 'PROVIDER_DOWN');
test('nic v logu + zadna zmena = NOCHANGE', klasifikuj({ log: 'Aider v0.86.2\nModel: x', zmena: 'ne' }), 'NOCHANGE');
test('nic v logu + zmena = OK', klasifikuj({ log: 'Aider v0.86.2', zmena: 'ano' }), 'OK');
test('neparsuje se = PARSE', klasifikuj({ log: 'ok', parsovani: 'failure' }), 'PARSE');
test('testy spadly = TESTS', klasifikuj({ log: 'ok', testy: 'failure' }), 'TESTS');
test('preskoceny krok NENI selhani (jinak by conductor dostal jinou pricinu)', klasifikuj({ log: 'ok', parsovani: 'skipped', testy: 'skipped', zmena: 'ne' }), 'NOCHANGE');
test('hlaska brany rozpoctu = REQUEST_TOO_LARGE', klasifikuj({ log: 'REQUEST_TOO_LARGE: request ~12000 tokenu > strop 8000' }), 'REQUEST_TOO_LARGE');
test('SCRIPT ERROR v logu = SCRIPT_ERROR', klasifikuj({ log: 'SCRIPT ERROR: Parse Error: x', zmena: 'ano' }), 'SCRIPT_ERROR');
test('cisla z chyby: limit i requested', cislaZLogu(TOO_LARGE), { hodnoty: [8000, 27557], limit: 8000, requested: 27557 });
test('cisla z chyby: kdyz tam nejsou, nic se nevymysli', cislaZLogu(KVOTA), { hodnoty: [], limit: null, requested: null });
test('prvni chyba je pojmenovana', prvniChyba(TOO_LARGE).startsWith('RateLimitError: RateLimitError: OpenAIException - Request too large'), true);

console.log(`\n=== VYSLEDEK: ${kontroly - chyb}/${kontroly} kontrol, ${chyb} chyb ===`);
process.exit(chyb ? 1 : 0);

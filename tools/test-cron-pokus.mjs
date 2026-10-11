// tools/test-cron-pokus.mjs — OFFLINE TEST „dorazil trigger, nebo umřel tik?“ (H156, P34).
//
// PROČ TENHLE SOUBOR EXISTUJE: P33 naměřila VÝPADEK cronu (~5 h) a nechala
// otevřenou PŘÍČINU. P34 ji naměřila: cron trigger DORAZÍ každou minutu
// (`wrangler tail`: `event.cron = "* * * * *"`) a invocation umírá na CPU
// limitu free plánu (`outcome = "exceededCpu"`, `cpuTime = 10 ms`), takže
// `zapisTep()` se nikdy nezavolá a `last_cron` zestárne. Do té doby se v
// `/health` slévaly DVĚ RŮZNÉ VADY:
//   * trigger NEDORAZIL (nedoručený event / zastavený cron), nebo
//   * trigger DORAZIL a tik NEDOBĚHL (umřel na CPU limitu).
//
// Služba proto zapisuje `last_cron_pokus` PŘED tikem (jediný zápis, který smrt
// invocation přežije) a tenhle test ověřuje, že predikát brány ty dva stavy
// POJMENUJE RŮZNĚ. Bez toho by oprava byla jen dalším tichem.
//
// ⚠ Fixtury 1–2 se liší JEN v `last_cron_pokus` — to je celý diferenciál.
// ⚠ Fixtura 5 je ZPĚTNÁ KOMPATIBILITA: `/health` ze staršího nasazení pole
//    NEMÁ; nesmí se z toho stát „trigger dorazil“ (to by byla lež o stavu).
//
// Použití: node tools/test-cron-pokus.mjs

import { zhodnotCron, VYCHOZI_LIMIT_MIN } from './cron-stav.mjs';

const NYNI = Date.parse('2026-10-11T06:00:00.000Z');
const iso = (minZpet) => new Date(NYNI - minZpet * 60000).toISOString();

let kontrol = 0;
let chyb = 0;
const test = (nazev, podminka, detail = '') => {
  kontrol++;
  if (!podminka) chyb++;
  console.log(`  ${podminka ? 'OK  ' : 'CHYBA'} ${nazev}${detail ? `  — ${detail}` : ''}`);
};

console.log('════ CRON: dorazil trigger, nebo umřel tik? (fixtury, bez sítě) ════');
console.log(`  limit: ${VYCHOZI_LIMIT_MIN} min · "teď" = ${new Date(NYNI).toISOString()}`);

// 1) ŽIVÝ STAV P34: trigger doráží každou minutu, dokončený tep je 190 min starý
{
  const v = zhodnotCron({
    last_cron: iso(190), last_cron_pokus: iso(0.5),
    last_tick: iso(190), last_tick_zdroj: 'cron',
  }, NYNI);
  test('1 pokus čerstvý + tep 190 min → CHYBA', v.ok === false, v.duvod);
  test('1 a pojmenuje to jako „tik NEDOBÍHÁ“ (ne „cron NETIKÁ“)',
    /NEDOBÍHÁ/.test(v.duvod) && !/cron NETIKÁ/.test(v.duvod), v.duvod);
}
// 2) TÝŽ STAV BEZ POKUSU = trigger nedorazil
{
  const v = zhodnotCron({
    last_cron: iso(190), last_cron_pokus: iso(190),
    last_tick: iso(190), last_tick_zdroj: 'cron',
  }, NYNI);
  test('2 pokus i tep 190 min staré → CHYBA', v.ok === false, v.duvod);
  test('2 a pojmenuje to jako „cron NETIKÁ“ (trigger NEDORAZIL)',
    /cron NETIKÁ/.test(v.duvod) && !/NEDOBÍHÁ/.test(v.duvod), v.duvod);
}
// 3) zdravý stav: tik DOBĚHL
{
  const v = zhodnotCron({
    last_cron: iso(0.5), last_cron_pokus: iso(0.4),
    last_tick: iso(0.4), last_tick_zdroj: 'cron',
  }, NYNI);
  test('3 pokus i tep čerstvé → OK', v.ok === true, v.duvod);
}
// 4) pokus je daleko v BUDOUCNOSTI (rozešlé hodiny) — nesmí to vypadat jako „dorazil“
// ⚠ Tolerance je ±limit (stejně jako u `last_cron`): pokus 1 min „napřed“ je
// běžné rozejití hodin a bere se jako čerstvý. Fixtura proto bere 60 min.
{
  const v = zhodnotCron({
    last_cron: iso(190), last_cron_pokus: new Date(NYNI + 60 * 60000).toISOString(),
    last_tick_zdroj: 'cron',
  }, NYNI);
  test('4 pokus 60 min v budoucnosti se za „dorazil“ NEbere → CHYBA', v.ok === false, v.duvod);
  // ⚠ NAMĚŘENO PŘI PSANÍ TESTU (P34): první verze fixtury kontrolovala JEN
  // `ok === false`, takže prošla i s predikátem, který budoucnost četl jako
  // „trigger dorazí“ (`pokusMin = -1 <= limit`). Slabá kontrola = slepá.
  test('4 a NEPOJmenuje to jako „tik NEDOBÍHÁ“ — pojmenuje rozešlé hodiny',
    !/NEDOBÍHÁ/.test(v.duvod) && /BUDOUCNOSTI/.test(v.duvod), v.duvod);
}
// 5) starší nasazení: pole `last_cron_pokus` v `/health` VŮBEC NENÍ
{
  const v = zhodnotCron({ last_cron: iso(190), last_tick_zdroj: 'cron' }, NYNI);
  test('5 chybějící `last_cron_pokus` (starší deploy) → CHYBA, ne „dorazil“',
    v.ok === false && /cron NETIKÁ/.test(v.duvod), v.duvod);
}
// 6) pokus je NESMYSLNÝ text — taky nesmí tvrdit „dorazil“
{
  const v = zhodnotCron({ last_cron: iso(190), last_cron_pokus: 'vcera' }, NYNI);
  test('6 `last_cron_pokus` není čas → CHYBA', v.ok === false && /cron NETIKÁ/.test(v.duvod), v.duvod);
}

console.log(`\nVÝSLEDEK: ${kontrol} kontrol, ${chyb} chyb`);
process.exit(chyb === 0 ? 0 : 1);

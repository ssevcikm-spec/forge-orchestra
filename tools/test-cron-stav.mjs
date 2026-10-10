// tools/test-cron-stav.mjs — OFFLINE TEST predikátu „běží cron?“ (H112, P33).
//
// PROČ: `tools/cron-stav.mjs` je čistá funkce, ale to samo o sobě nic nedokazuje.
// Test tvrdí, že umí vrátit `ok: false` na KAŽDÉM stavu, který zelený být nesmí —
// jinak by šlo o bránu, která nemá jak selhat (přesně ta vada, kterou H112 zavírá).
//
// Fixtury: (1) čerstvý tep, (2) tep na hraně limitu, (3) STARÝ tep (cron stojí),
// (4) chybějící `last_cron` (starý deploy), (5) `last_cron` není čas, (6) `/health`
// neodpovědělo, (7) tep v budoucnosti (rozešlé hodiny), (8) ruční tik NEobnoví
// `last_cron` — tep je starý, i když `last_tick` je čerstvý (TO je jádro opravy).
//
// Použití: node tools/test-cron-stav.mjs

import { zhodnotCron, VYCHOZI_LIMIT_MIN } from './cron-stav.mjs';

// Pevný „teď“, aby test nebyl závislý na hodinách ani na pomalém stroji.
const NYNI = Date.parse('2026-10-09T21:00:00.000Z');
const iso = (minZpet) => new Date(NYNI - minZpet * 60000).toISOString();

let kontrol = 0;
let chyb = 0;
const test = (nazev, podminka, detail = '') => {
  kontrol++;
  if (!podminka) chyb++;
  console.log(`  ${podminka ? 'OK  ' : 'CHYBA'} ${nazev}${detail ? `  — ${detail}` : ''}`);
};

console.log('════ CRON: umí brána spadnout? (fixtury, bez sítě) ════');
console.log(`  limit: ${VYCHOZI_LIMIT_MIN} min · "teď" = ${new Date(NYNI).toISOString()}`);

// 1) zdravý stav
{
  const v = zhodnotCron(
    { last_cron: iso(0.5), last_tick: iso(0.5), last_tick_zdroj: 'cron' }, NYNI);
  test('1 čerstvý tep (0,5 min) → OK', v.ok === true, v.duvod);
}
// 2) hrana limitu — ještě OK
{
  const v = zhodnotCron(
    { last_cron: iso(VYCHOZI_LIMIT_MIN - 0.5), last_tick_zdroj: 'cron' }, NYNI);
  test(`2 tep na hraně (${VYCHOZI_LIMIT_MIN - 0.5} min) → OK`, v.ok === true, v.duvod);
}
// 3) STARÝ tep = cron stojí (vada, kterou nikdo neviděl)
{
  const v = zhodnotCron(
    { last_cron: iso(30), last_tick: iso(30), last_tick_zdroj: 'cron' }, NYNI);
  test('3 tep 30 min starý → CHYBA (cron NETIKÁ)', v.ok === false, v.duvod);
}
// 4) starý deploy: pole vůbec není
{
  const v = zhodnotCron({ ok: true, time: iso(0), ready: 0 }, NYNI);
  test('4 chybí `last_cron` → CHYBA (nedá se měřit, není to zelená)',
    v.ok === false, v.duvod);
}
// 5) rozbitý formát
{
  const v = zhodnotCron({ last_cron: 'vcera' }, NYNI);
  test('5 `last_cron` není čas → CHYBA', v.ok === false, v.duvod);
}
// 6) služba neodpověděla
{
  const v = zhodnotCron(null, NYNI);
  test('6 `/health` neodpovědělo → CHYBA', v.ok === false, v.duvod);
}
// 7) rozešlé hodiny
{
  const v = zhodnotCron({ last_cron: new Date(NYNI + 60 * 60000).toISOString() }, NYNI);
  test('7 tep v BUDOUCNOSTI (60 min) → CHYBA', v.ok === false, v.duvod);
}
// 8) JÁDRO OPRAVY: ruční tik `last_cron` neobnoví
{
  const v = zhodnotCron(
    { last_cron: iso(45), last_tick: iso(0.1), last_tick_zdroj: 'manual' }, NYNI);
  test('8 ruční tik neobnoví `last_cron` → CHYBA (brána měří cron, ne tlačítko)',
    v.ok === false, v.duvod);
}

console.log(`\nVÝSLEDEK: ${kontrol} kontrol, ${chyb} chyb`);
process.exit(chyb === 0 ? 0 : 1);

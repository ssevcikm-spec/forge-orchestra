// tools/cron-stav.mjs — ČISTÝ PREDIKÁT „běží cron?“ — aby se dal ověřit OFFLINE.
//
// PROČ TENHLE SOUBOR EXISTUJE (H112, P33): brána `validate-all.mjs` tvrdila
// „cron běží (čas)“ — a přitom měřila jen `!!h.time`, tedy že služba odpovídá
// na `/health`. O běhu cronu netvrdila NIC. Naměřeno 9. 10. 2026: tik se
// zastavil a žádná brána to neohlásila (brána, která nemá jak selhat).
//
// Oprava má DVĚ části a ty se nesmí slít:
//   1) SLUŽBA tep zapisuje a posílá ho v `/health` (`conductor/src/index.ts`),
//   2) BRÁNA tep hodnotí — a to je TENHLE soubor.
// Logika je proto vytažená do čisté funkce: dá se testovat fixturami
// (`tools/test-cron-stav.mjs`) a je vidět, že umí spadnout. Kdyby zůstala
// uvnitř `validate-all.mjs`, šla by ověřit jen proti ŽIVÉ službě — a zelená
// proti živé službě se od slepé brány nerozezná (skill `overovani` §7.13).
//
// ⚠ NENÍ to samostatná brána v `_analyza/g3-brany.py` — a je to VĚDOMÉ:
// přidat položku do `BRANY` by posunulo čítač `brán celkem: 49 → 50`, na kterém
// stojí tvrzení v `HANDOFF.md`, `KRONIKA-PROJEKTU.md` i v měřidlech P28/P30/P31/P32
// (H135 — „kdo přidá kontrolu, přeměří cizí tvrzení, které na tom čítači stojí“).
// Predikát se proto měří UVNITŘ existující brány `validate-all` (sekce A) a jeho
// offline test se pouští tamtéž.

export const VYCHOZI_LIMIT_MIN = 10;

import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

/**
 * Zhodnotí, jestli podle odpovědi `/health` tiká PLÁNOVANÝ cron.
 *
 * Rozhoduje `last_cron` (zapisuje ho jen `scheduled`, tedy cron trigger) —
 * `last_tick` se schválně NEbere: ten obnoví i ruční `POST /tick`, takže by
 * brána měřila tlačítko, ne cron.
 *
 * Stavy, které NEJSOU zelená (a musí být vidět):
 *   * `/health` neodpovědělo        → nelze měřit,
 *   * chybí `last_cron`             → služba tep neposílá (starý deploy),
 *   * `last_cron` není čas          → rozbitý formát,
 *   * tep je starší než limit       → cron NETIKÁ,
 *   * tep je v budoucnosti (> limit) → rozešlé hodiny.
 *
 * @param {any} h  odpověď `/health` (objekt), nebo cokoli jiného
 * @param {number} nyni  čas měření v ms (`Date.now()`)
 * @param {number} limitMin  kolik minut starý tep je ještě „běží“
 * @returns {{ok: boolean, duvod: string}}
 */
export function zhodnotCron(h, nyni = Date.now(), limitMin = VYCHOZI_LIMIT_MIN) {
  if (!h || typeof h !== 'object') {
    return { ok: false, duvod: '/health nevrátilo objekt — cron se NEDÁ změřit' };
  }
  const iso = h.last_cron;
  if (iso === null || iso === undefined || iso === '') {
    return {
      ok: false,
      duvod: '/health neposílá `last_cron` — tep cronu chybí (nasazený conductor ho neměří)',
    };
  }
  if (typeof iso !== 'string') {
    return { ok: false, duvod: `last_cron není řetězec: ${JSON.stringify(iso).slice(0, 40)}` };
  }
  const t = Date.parse(iso);
  if (!Number.isFinite(t)) {
    return { ok: false, duvod: `last_cron není čas: ${iso.slice(0, 40)}` };
  }
  const min = (nyni - t) / 60000;
  const zaokrouhleno = Math.round(min);
  const zdroj = h.last_tick_zdroj ?? '?';
  if (min > limitMin) {
    return {
      ok: false,
      duvod: `cron NETIKÁ: naposledy ${iso} (${zaokrouhleno} min, limit ${limitMin})`
        + ` · poslední tik zdrojem: ${zdroj}`,
    };
  }
  if (min < -limitMin) {
    return {
      ok: false,
      duvod: `last_cron je v BUDOUCNOSTI (${iso}, ${zaokrouhleno} min) — hodiny se rozešly`,
    };
  }
  return {
    ok: true,
    duvod: `last_cron ${iso} (${zaokrouhleno} min) · poslední tik zdrojem: ${zdroj}`,
  };
}

// ── CLI: `node tools/cron-stav.mjs <soubor-s-health.json>` ───────────────────
// Slouží k ručnímu měření (a k dokladu „brána umí spadnout“): nad ULOŽENOU
// odpovědí `/health` se dá změřit i to, co živá služba právě neposílá.
//
// ⚠ NAMĚŘENO PŘI PSANÍ (P33, vlastní omyl hned napoprvé): první verze se ptala
// `process.argv[1].endsWith("cron-stav.mjs")` — a to je PODŘETĚZCOVÁ podmínka,
// takže se nechala uspokojit i souborem `test-cron-stav.mjs` (obsahuje ji taky).
// Test se tím spustil jako CLI a spadl na `exit 2`. Je to TÁŽ TŘÍDA jako H140
// („kontrola se nechala uspokojit podřetězcem“); správně se porovnává CELÁ cesta.
if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url)) {
  const { readFileSync } = await import('node:fs');
  const cesta = process.argv[2];
  if (!cesta) {
    console.log('použití: node tools/cron-stav.mjs <soubor-s-health.json> [limit-min]');
    process.exit(2);
  }
  const h = JSON.parse(readFileSync(cesta, 'utf8'));
  const limit = process.argv[3] ? Number(process.argv[3]) : VYCHOZI_LIMIT_MIN;
  const v = zhodnotCron(h, Date.now(), limit);
  console.log(`${v.ok ? 'OK   ' : 'CHYBA'} ${v.duvod}`);
  process.exit(v.ok ? 0 : 1);
}

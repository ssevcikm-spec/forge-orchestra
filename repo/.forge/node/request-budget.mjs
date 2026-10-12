#!/usr/bin/env node
// K1b - ROZPOCET REQUESTU: spocti, kolik tokenu se posle, a odmítni to PRED volanim.
//
// PROC TO EXISTUJE (namereno 12. 10. 2026):
//   - Groq (jediny zdroj bez karty) ma strop 8 000 tokenu za minutu (hlavicka
//     `x-ratelimit-limit-tokens`; potvrzeno i telem chyby 413).
//   - nase requesty mely 25 065 / 27 557 / 39 167 tokenu (logy behu 350/366/349).
//   - do 9. 10. se to nikde NEMERILO: pick-provider posila "ping" s
//     max_tokens=8, takze "poskytovatel odpovida" a za minutu request spadne.
//
// CO DELA: secte zadani + soubory k editaci + soubory ke cteni + konvence,
// prida fixni rezii harnessu (aider) a porovna se stropem poskytovatele.
// Kdyz se to nevejde, skonci NENULOVE a pojmenuje to (REQUEST_TOO_LARGE) -
// jeste pred tim, nez se spali pokus a kvota.
//
// Pouziti:
//   node .forge/node/request-budget.mjs --zadani-text "$ZADANI" \
//     --soubory "$DO_EDITACE" --cteni "$CIT_DEPS" --konvence CONVENTIONS.md \
//     --poskytovatel groq --model openai/gpt-oss-120b
//   node .forge/node/request-budget.mjs --zadani-text "ahoj" --strop 8000 --json

import { readFileSync, existsSync } from 'node:fs';
import { join } from 'node:path';
import { ZNAKU_NA_TOKEN } from './prompt-hygiene.mjs';

// FIXNI REZIE HARNESSU - aider posila v kazdem requestu svuj systemovy prompt.
// ZMERENO 12. 10. 2026 lokalne (aider 0.86.2, stejna verze jako v CI): aider se
// pustil proti FALESNEMU poskytovateli na localhostu, ktery si zapsal cely
// request -> systemovy prompt 5 421 znaku = ~1 789 tokenu. Konstantu drzime
// o neco vyssi, aby rozpocet nelhal optimismem.
// (Dřívější odhad 4 000 byl ODEČTEN z rozdílu v CI a byl příliš vysoký; měření
//  ho nahradilo. Nástroj: .tmp/otukani/mer-rezii-aideru.mjs - v repu orchestry.)
export const REZIE_HARNESSU = 1800;

export const tokeny = (znaku) => Math.ceil(znaku / ZNAKU_NA_TOKEN);

/** Nacte strop z providers.json (blok `limits`), kdyz je k dispozici. */
export function stropPoskytovatele(soubor, nazev, model) {
  if (!soubor || !existsSync(soubor)) return null;
  try {
    const cfg = JSON.parse(readFileSync(soubor, 'utf8'));
    const p = (cfg.providers || []).find((x) => x.name === nazev);
    if (!p || !p.limits) return null;
    const l = p.limits;
    if (model && l.models && l.models[model]) return l.models[model].tpm ?? l.tpm ?? null;
    return l.tpm ?? null;
  } catch {
    return null;
  }
}

/** Secte velikosti souboru ze seznamu (oddělovačem je novy radek nebo mezera). */
export function velikosti(soubory, koren = process.cwd()) {
  const out = [];
  for (const f of String(soubory || '').split(/[\s\n]+/).filter(Boolean)) {
    const cisty = f.replace(/^--(file|read)$/, '');
    if (!cisty || cisty.startsWith('--')) continue;
    let znaku = 0;
    try {
      const p = join(koren, cisty);
      if (existsSync(p)) znaku = readFileSync(p, 'utf8').length;
    } catch { /* necitelny soubor = 0 a je to videt ve vypisu */ }
    out.push({ soubor: cisty, znaku, tokenu: tokeny(znaku) });
  }
  return out;
}

/** Vypocet rozpoctu - cista funkce, aby ji test VOLAL, ne opisoval. */
export function rozpocet({ zadaniText = '', soubory = '', cteni = '', konvence = '', strop, rezije = REZIE_HARNESSU, koren = process.cwd() }) {
  const zadani = { znaku: zadaniText.length, tokenu: tokeny(zadaniText.length) };
  const edit = velikosti(soubory, koren);
  const read = velikosti(cteni, koren);
  const konv = velikosti(konvence, koren);
  const soucet = zadani.tokenu + edit.reduce((a, x) => a + x.tokenu, 0)
    + read.reduce((a, x) => a + x.tokenu, 0) + konv.reduce((a, x) => a + x.tokenu, 0);
  const celkem = soucet + rezije;
  return {
    zadani, edit, read, konvence: konv, rezije,
    soucet_obsahu: soucet, celkem,
    strop: strop ?? null,
    vejde_se: strop ? celkem <= strop : null,
    zbyva: strop ? strop - celkem : null,
  };
}

/**
 * Rozhodnuti brany. NAMERENY strop se VYNUCUJE (request se neposle), odhad
 * jen VARUJE - jinak by nezmereny poskytovatel blokoval praci, kterou by
 * zvladl (a to je presne ta chyba, kterou hledame v opacnem smeru).
 */
export function rozhodni(r, zdroj) {
  if (r.vejde_se) return 'FITS';
  return zdroj === 'odhad' ? 'NEZNAMY_STROP' : 'TOO_LARGE';
}

function arg(n, d = '') { const i = process.argv.indexOf(n); return i >= 0 ? process.argv[i + 1] : d; }

function main() {
  const json = process.argv.includes('--json');
  const poskytovatel = arg('--poskytovatel');
  const model = arg('--model');
  const rucni = arg('--strop', '');
  const zProfilu = stropPoskytovatele(arg('--providers', '.forge/providers.json'), poskytovatel, model);
  const strop = Number(rucni || zProfilu || 32000);
  const zdroj = rucni ? 'rucni' : (zProfilu ? 'mereno' : 'odhad');
  const r = rozpocet({
    zadaniText: arg('--zadani-text'),
    soubory: arg('--soubory'),
    cteni: arg('--cteni'),
    konvence: arg('--konvence'),
    strop,
    rezije: Number(arg('--rezije', '') || REZIE_HARNESSU),
  });
  r.strop_zdroj = zdroj;
  const trida = rozhodni(r, zdroj);
  if (json) {
    console.log(JSON.stringify(r, null, 2));
    // POZOR: i JSON vetev musi koncit nenulove, jinak by se z ni stal "gate",
    // ktery nema jak selhat (vada, kterou projekt zna jako S27).
    if (trida === 'TOO_LARGE') process.exit(1);
  } else {
    console.log(`ROZPOCET: ~${r.celkem} tokenu (zadani ${r.zadani.tokenu} + editace ${r.edit.reduce((a, x) => a + x.tokenu, 0)}` +
      ` + cteni ${r.read.reduce((a, x) => a + x.tokenu, 0)} + konvence ${r.konvence.reduce((a, x) => a + x.tokenu, 0)} + rezie ${r.rezije})`);
    console.log(`STROP (${poskytovatel || 'rucni'}/${model || '-'}, ${zdroj}): ${strop} tokenu | zbyva ${r.zbyva}`);
    console.log(`TRIDA=REQUEST_${trida}`);
    if (trida === 'TOO_LARGE') {
      console.error(`::error::REQUEST_TOO_LARGE: request ~${r.celkem} tokenu > strop ${strop}. ` +
        `Zmensi kontext (mene souboru, kratsi zadani, konvence jen sekce), nebo vyber poskytovatele s vetsim stropem.`);
      process.exit(1);
    }
    if (trida === 'NEZNAMY_STROP') {
      console.error(`::warning::strop poskytovatele ${poskytovatel || '?'} NENI ZMERENY – request ~${r.celkem} tokenu ` +
        `posilam, ale muze spadnout. Zmer ho: .forge/node/probe-provider.mjs --jen ${poskytovatel || '<nazev>'}`);
    }
  }
}

if (process.argv[1] && import.meta.url === (await import('node:url')).pathToFileURL(process.argv[1]).href) {
  main();
}

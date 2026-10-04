// Přečte session logy DSH (multi-frame zstd) a vypíše, čím se session liší.
//
// PROČ TO EXISTUJE (2. 10. 2026): uživatel se ptal **„jak mám zavolat druhou
// session?"** a odpověď se nedala dát dojmem — v adresáři je **69 sessions**.
// Rozlišit je pro člověka jde jen podle **titulku** a **první uživatelské
// zprávy**, a ty jsou v logu.
//
// ⚠ TŘI PASTI FORMÁTU (každá mě stála jedno měření):
//   1. **Soubor je MULTI-FRAME zstd** — 1,3 MB logu = **997 rámců**, každý
//      záznam vlastní. `zstdDecompressSync(cely soubor)` vrátí **JEN PRVNÍ
//      rámec** (1 řádek = metadata `type:"session"`) a tvrdí úspěch.
//      `createZstdDecompress()` se zastaví taky. → rámce se hledají podle
//      magic `28 b5 2f fd` a dekódují se po jednom.
//   2. **Složka NENÍ session ID** — složka `7db45275-…` obsahuje session
//      `session-7db45275-…` (o prefix `session-` delší). Kdo hledá podle
//      názvu složky, dostane jiné ID.
//   3. **Sessions mají dva druhy**: `delegationDepth: 0` = skutečná session,
//      `1` = podagent. Podagenty nemají smysl „volat".
//
// Použití:
//   node _analyza/dsh-session-prehled.mjs [--vsechny] [--limit N] [--hledej TEXT]
// Bez přepínačů: posledních 24 h, jen skutečné session (hloubka 0).

import { readFileSync, readdirSync, existsSync, statSync } from 'node:fs';
import { zstdDecompressSync } from 'node:zlib';
import path from 'node:path';

const SESSIONS = 'E:\\DeepSeekHarness-data\\sessions\\--C-Users-Ssevc-Local-Deepseek--';
const vsechny = process.argv.includes('--vsechny');
const iLim = process.argv.indexOf('--limit');
const limit = iLim > 0 ? Number(process.argv[iLim + 1]) : 30;
const iHled = process.argv.indexOf('--hledej');
const hledej = iHled > 0 ? process.argv[iHled + 1].toLowerCase() : null;

const MAGIC = [0x28, 0xb5, 0x2f, 0xfd];

/** Dekóduje VŠECHNY zstd rámce v souboru (viz past 1 v hlavičce). */
function prectiVsechnyRamce(cesta) {
  const b = readFileSync(cesta);
  const pozice = [];
  for (let i = 0; i + 3 < b.length; i++) {
    if (b[i] === MAGIC[0] && b[i + 1] === MAGIC[1] && b[i + 2] === MAGIC[2] && b[i + 3] === MAGIC[3]) {
      pozice.push(i);
    }
  }
  if (!pozice.length) return b.toString('utf8');   // není zstd → prostý text
  const radky = [];
  for (let k = 0; k < pozice.length; k++) {
    const konec = k + 1 < pozice.length ? pozice[k + 1] : b.length;
    try {
      radky.push(...zstdDecompressSync(b.subarray(pozice[k], konec))
        .toString('utf8').split('\n').filter((r) => r.trim()));
    } catch { /* poškozený rámec se přeskočí, ne shodí celek */ }
  }
  return radky;
}

/** Vytáhne z řádků to, čím se session pozná: id, hloubku, titulky, první zprávu. */
function rozbor(radky) {
  const out = { id: null, hloubka: null, titulky: [], prvniZprava: null, zprav: 0, model: null };
  for (const r of radky) {
    let o;
    try { o = JSON.parse(r); } catch { continue; }
    if (o.type === 'session') { out.id = o.id; out.hloubka = o.delegationDepth ?? 0; }
    if (o.type === 'session/title' && o.data?.title) out.titulky.push(o.data.title);
    if (o.type === 'request/context' && o.data?.model) out.model = o.data.model;
    if (o.type === 'user/message') {
      out.zprav++;
      if (!out.prvniZprava) {
        let c = o.data?.content ?? o.data?.text ?? '';
        if (Array.isArray(c)) c = c.map((x) => (typeof x === 'string' ? x : x?.text ?? '')).join(' ');
        c = String(c).replace(/\s+/g, ' ').trim();
        if (c.length > 10) out.prvniZprava = c;
      }
    }
  }
  return out;
}

const prah = Date.now() - 24 * 3600 * 1000;
const sessions = [];
for (const jmeno of readdirSync(SESSIONS)) {
  const dir = path.join(SESSIONS, jmeno);
  let st;
  try { st = statSync(dir); } catch { continue; }
  if (!st.isDirectory()) continue;
  const log = path.join(dir, 'session.v4.jsonl.zstd');
  if (!existsSync(log)) continue;
  const mtime = statSync(log).mtimeMs;
  if (!vsechny && mtime < prah) continue;
  let info = { id: jmeno, hloubka: 0, titulky: [], prvniZprava: '(nepřečteno)', zprav: 0, model: null };
  try { info = { ...info, ...rozbor(prectiVsechnyRamce(log)) }; } catch (e) { info.prvniZprava = `(chyba: ${e.message.slice(0, 50)})`; }
  const titulek = info.titulky.length ? info.titulky[info.titulky.length - 1] : '(bez titulku)';
  const zaznam = {
    slozka: jmeno, mtime, ...info, titulek,
    hledanyText: `${jmeno} ${titulek} ${info.prvniZprava}`.toLowerCase(),
  };
  if (hledej && !zaznam.hledanyText.includes(hledej)) continue;
  sessions.push(zaznam);
}

sessions.sort((a, b) => b.mtime - a.mtime);
const hlavni = sessions.filter((s) => (s.hloubka ?? 0) === 0);
console.log(`Session v tomto workspace${vsechny ? '' : ' (posledních 24 h)'}: ${sessions.length}`);
console.log(`  z toho SKUTEČNÉ (hloubka 0): ${hlavni.length}   podagentů (hloubka 1): ${sessions.length - hlavni.length}\n`);

for (const s of sessions.slice(0, limit)) {
  const kdy = new Date(s.mtime).toISOString().replace('T', ' ').slice(0, 19);
  const znacka = (s.hloubka ?? 0) === 0 ? 'SESSION ' : 'podagent';
  console.log(`${kdy}  [${znacka}]  ${s.id}`);
  console.log(`   titulek : ${String(s.titulek).slice(0, 130)}`);
  if (s.hloubka === 0 && s.prvniZprava) {
    console.log(`   začátek: ${String(s.prvniZprava).slice(0, 130)}`);
    console.log(`   zpráv   : ${s.zprav}${s.model ? `   model: ${s.model}` : ''}`);
  }
  console.log();
}

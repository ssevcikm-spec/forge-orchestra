// p41-a-teplota-sonda.mjs — ŽIVÁ sonda: CRON (čerstvý izolát) vs RUČNÍ `POST /tick`
// (teplý izolát) a série `?faze=N` pro rozklad CPU po fázích.
//
// PROČ VZNIKL (P41, hlavní úkol ze zadání §1):
//   P40 zlevnila tik z 23 na 13 D1 round-tripů a payload z 665 kB na 47 kB —
//   `wallTime` spadl o 45 %, ale `cpuTime` se NEHL (18 → 19 ms, H197). Rozdíl
//   mezi offline modelem (2,5 ms) a živým tikem (19 ms) je ~7×, takže se musí
//   rozhodnout mezi dvěma hypotézami:
//     (a) „chybí model“ — cena je v něčem, co falešná D1 a stub GitHubu neplatí;
//     (b) „platí se start izolátu“ — cron dostává čerstvý izolát každou minutu.
//   Rozhoduje se MĚŘENÍM, ne dohadem:
//     · teplý izolát = několik `POST /tick` za sebou (sonda je posílá BEZ pauzy,
//       aby spojení i izolát zůstaly teplé),
//     · `?faze=N` — tik se zastaví po N-té fázi; CPU hlásí runtime jen za CELOU
//       invokaci, takže ROZDÍL cpuTime mezi `faze=N` a `faze=N+1` je cena fáze,
//     · `iso=` v logu řádku `tick-prof:` prozradí, které invokace šly v TÉMŽ
//       izolátu (modulová konstanta) — bez toho by se „teplý“ jen předpokládal.
//
// ⚠ cpuTime NENÍ v odpovědi — čte se z `wrangler tail` (doklad). Tahle sonda
//   proto píše jen to, co VIDĚLA: pořadí, stav, čas odpovědi a text zprávy.
//   V JEDNU CHVÍLI SE VEDE JEN JEDEN TAIL (H200 — dva si berou eventy).
//
// Použití: node _analyza/p41-a-teplota-sonda.mjs
// Výstup:  _analyza/p41-a-sonda-vystup.txt   (VLASTNÍ jméno — H191)

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p41-a-sonda-vystup.txt");
const BASE = "https://forge-conductor.ssevcikm.workers.dev";

// Tajemství jen ze souboru a NIKDY se nevypisuje (posílá se v hlavičce).
const sec = JSON.parse(readFileSync(join(WS, ".secrets", "cf-secrets.json"), "utf8").replace(/^\uFEFF/, ""));
const WEBHOOK = String(sec.WEBHOOK_SECRET || "").trim();
if (!WEBHOOK) {
  console.log("CHYBA: v .secrets/cf-secrets.json chybi WEBHOOK_SECRET");
  process.exit(1);
}

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const postTick = async (popis, faze) => {
  const url = faze === null ? `${BASE}/tick` : `${BASE}/tick?faze=${faze}`;
  const t0 = Date.now();
  let status = 0, text = "";
  try {
    const r = await fetch(url, {
      method: "POST",
      headers: { "x-forge-secret": WEBHOOK, "content-type": "application/json" },
      body: "{}",
    });
    status = r.status;
    text = await r.text();
  } catch (e) {
    text = `CHYBA site: ${String(e)}`;
  }
  const ms = Date.now() - t0;
  let msg = "";
  try { msg = String(JSON.parse(text)?.message ?? ""); } catch { msg = text.slice(0, 200); }
  zapis(`  ${String(popis).padEnd(22)} HTTP ${status}  ${String(ms).padStart(6)} ms  | ${msg.slice(0, 150)}`);
  return { popis, faze, status, ms, msg };
};

const vysledky = [];
const pockej = (ms) => new Promise((r) => setTimeout(r, ms));

zapis(`# p41-a — ŽIVÁ sonda: cron vs ruční POST /tick (teplý izolát) + rozklad ?faze=N`);
zapis(`# ${new Date().toISOString()}  ${BASE}`);
zapis(`# POZOR: cpuTime se ČTE Z TAILU — tahle sonda měří jen pořadí a wall time odpovědi.`);
zapis();

try {
  // ── 0) kontrola, že služba žije (a že tik tiká) ────────────────────────────
  zapis("## 0) GET /health (kontrola stavu před měřením)");
  const hr = await fetch(`${BASE}/health`);
  const hj = await hr.json();
  zapis(`  HTTP ${hr.status} ok=${hj.ok} ready=${hj.ready} running=${hj.running} games=${hj.games}`);
  zapis(`  last_cron=${hj.last_cron ?? "-"} (${hj.last_cron_min ?? "?"} min) zdroj=${hj.last_tick_zdroj ?? "-"}`);
  zapis();

  // ── 1) TEPLÝ IZOLÁT: šest plných tiků BEZ PAUZY ──────────────────────────
  // První z nich může být ještě čerstvý izolát — proto se jich dělá víc a
  // rozhoduje `iso=` v logu, ne pořadí.
  zapis("## 1) Teplý izolát: 6× plný `POST /tick` bez pauzy");
  for (let i = 1; i <= 6; i++) vysledky.push(await postTick(`plny tik #${i}`, null));
  zapis();

  // ── 2) ROZKLAD PO FÁZÍCH: `?faze=0..8`, DVĚ KOLA ─────────────────────────
  // `faze=0` = NULA práce → cena čerstvého izolátu a modulu (baseline).
  zapis("## 2) Rozklad CPU po fázích: `?faze=0..8` (dvě kola po sobě)");
  for (let kolo = 1; kolo <= 2; kolo++) {
    zapis(`### kolo ${kolo}`);
    for (let f = 0; f <= 8; f++) vysledky.push(await postTick(`faze=${f}`, f));
  }
  zapis();

  // ── 3) KONTROLA: levný endpoint (izolát nemá být „na nule“) ──────────────
  zapis("## 3) Kontrolní levný endpoint (má být řádově levnější)");
  {
    const t0 = Date.now();
    const r = await fetch(`${BASE}/health`);
    await r.text();
    zapis(`  GET /health            HTTP ${r.status}  ${String(Date.now() - t0).padStart(6)} ms`);
  }

  writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
  console.log(`\n# zapsano: ${OUT} (${radky.length} radku)`);
} catch (e) {
  zapis(`CHYBA: ${String(e)}`);
  writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
  process.exit(1);
}

// p37-tick-mereni.mjs — ZÁSAH: jeden ruční `POST /tick` + měření jeho ceny z tailu.
//
// PROČ (P37): cron tik umírá na `exceededCpu` (`cpuTime = 10`, free plán) —
// a to i když není co dispatchovat. Otázka, kterou jinak změřit nelze:
// **je přes rozpočet PRÁCE tiku, nebo CESTA, kterou se pouští?**
// Cron ji pouští přes `ctx.waitUntil(tick(env))` (tik běží PO odpovědi),
// kdežto `POST /tick` ji awaituje v běžném požadavku. Když ruční tik projde
// a cron umírá, je rozdíl v CESTĚ, ne v práci.
//
// ⚠ JE TO ZÁSAH DO STAVU (zadání P37 §4): tik zapíše tep zdrojem `manual`
// (což NEOBNOVÍ `last_cron` — H112) a může dispatchovat práci. Dnes
// dispatchovat NEMŮŽE: všechny tři `ready` granule jsou na stropu 8/8.
// Zásah se proto ZAPISUJE do záznamů.
//
// Použití: node _analyza/p37-tick-mereni.mjs
// Exit 0 = tik proběhl (i když vrátil chybu služby); 1 = HTTP chyba.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-tick-mereni-vystup.txt");
const TAIL = join(WS, "_analyza", "p37-tail-raw-vystup.txt");
const BASE = "https://forge-conductor.ssevcikm.workers.dev";

const sec = JSON.parse(readFileSync(join(WS, ".secrets", "cf-secrets.json"), "utf8").replace(/^\uFEFF/, ""));
const WEBHOOK = String(sec.WEBHOOK_SECRET || "").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const stavTailu = () => {
  try { return readFileSync(TAIL, "utf8").length; } catch { return 0; }
};

zapis(`# p37 — RUČNÍ TIK a jeho cena (ZÁSAH do stavu) — ${new Date().toISOString()}`);
zapis("# tik zapisuje tep zdrojem `manual` (NEOBNOVÍ `last_cron`, H112); dispatch dnes nemůže (strop 8/8)");

// ── stav PŘED ──────────────────────────────────────────────────────────────
const pred = await fetch(`${BASE}/health`).then((r) => r.json()).catch(() => null);
zapis("");
zapis("## STAV PŘED TIKEM (/health)");
if (pred) {
  zapis(`   ready=${pred.ready} running=${pred.running} games=${pred.games}`);
  zapis(`   last_tick=${pred.last_tick} (${pred.last_tick_zdroj}) · last_cron=${pred.last_cron} (${pred.last_cron_min} min) · last_cron_pokus=${pred.last_cron_pokus} (${pred.last_cron_pokus_min} min)`);
} else zapis("   (health neodpověděl)");

const delkaPred = stavTailu();
const casPred = Date.now();

// ── ZÁSAH: ruční tik ──────────────────────────────────────────────────────
zapis("");
zapis("## POST /tick (ZÁSAH)");
let odpoved = null;
try {
  const r = await fetch(`${BASE}/tick`, { method: "POST", headers: { "x-forge-secret": WEBHOOK } });
  odpoved = { status: r.status, text: await r.text() };
  zapis(`   HTTP ${r.status}`);
  zapis(`   ${odpoved.text.slice(0, 1200)}`);
} catch (e) {
  zapis(`   CHYBA: ${String(e).slice(0, 200)}`);
}
const ms = Date.now() - casPred;

// ── cena z tailu: event, který odpovídá tomuto tiku ───────────────────────
await new Promise((s) => setTimeout(s, 4000));
const celyTail = (() => { try { return readFileSync(TAIL, "utf8"); } catch { return ""; } })();
const novy = celyTail.slice(delkaPred);
zapis("");
zapis(`## CENA Z TAILU (nové bajty po tiku: ${novy.length})`);
const najdi = (vzor) => { const m = novy.match(vzor); return m ? m[1] : "?"; };
zapis(`   wallTime: ${najdi(/"wallTime":\s*(\d+)/)} ms · cpuTime: ${najdi(/"cpuTime":\s*(\d+)/)} ms · outcome: ${najdi(/"outcome":\s*"([^"]+)"/)}`);
zapis(`   HTTP odpověď /tick trvala: ${ms} ms (zahrnuje síť a D1, ne jen CPU)`);
if (!novy.length) zapis("   ⚠ v tailu nepřibyl žádný event — cena NEMĚŘENA (tail bufferuje, zkus odečíst později)");

// ── stav PO ────────────────────────────────────────────────────────────────
const po = await fetch(`${BASE}/health`).then((r) => r.json()).catch(() => null);
zapis("");
zapis("## STAV PO TIKU (/health)");
if (po) {
  zapis(`   ready=${po.ready} running=${po.running}`);
  zapis(`   last_tick=${po.last_tick} (${po.last_tick_zdroj}) · last_cron=${po.last_cron} (${po.last_cron_min} min) · last_cron_pokus=${po.last_cron_pokus} (${po.last_cron_pokus_min} min)`);
  if (po.last_tick_zdroj === "manual") {
    zapis("   ✓ tep se ZAPSAL jako `manual` — tik skutečně doběhl do konce (zápis tepu je POSLEDNÍ krok)");
  } else {
    zapis("   ⚠ tep NENÍ `manual` — tik doběhl jen po zápis tepu, nebo spadl");
  }
  if (po.last_cron === pred?.last_cron) zapis("   ✓ `last_cron` se NEZMNĚNIL — ruční tik ho neobnovil (H112 platí)");
} else zapis("   (health neodpověděl)");

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(0);

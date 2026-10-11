// p37-sluzba-sonda.mjs — ŽIVÝ stav služby conductor (READ-ONLY: jen GET endpointy).
//
// Zadání P37 §2.2 (VÝPADEK): „u conductoru zavolej živou službu“. Tenhle skript
// NEMĚNÍ stav: nevolá POST /tick, /poll ani /game. Čte:
//   /            — seznam endpointů (doklad, že služba odpovídá)
//   /health      — veřejné: tep cronu, cíl, běhy
//   /roadmap     — stav granulí (item_id, task_id, status, attempts)
//   /queue       — fronta úkolů
//   /status      — posledních 20 běhů
//
// Tajemství se čte z .secrets/cf-secrets.json (WEBHOOK_SECRET) a NIKDY se
// nevypisuje — jen se posílá v hlavičce `x-forge-secret`.
//
// Použití: node _analyza/p37-sluzba-sonda.mjs
// Exit 0 = měřeno; 1 = některé měření neproběhlo (pojmenuje se).

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-sluzba-sonda-vystup.txt");
const BASE = "https://forge-conductor.ssevcikm.workers.dev";

const sec = JSON.parse(readFileSync(join(WS, ".secrets", "cf-secrets.json"), "utf8").replace(/^\uFEFF/, ""));
const WEBHOOK = String(sec.WEBHOOK_SECRET || "").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };
let selhalo = 0;

const get = async (cesta, sTajemstvim = false) => {
  const hlavicky = sTajemstvim ? { "x-forge-secret": WEBHOOK } : {};
  const t0 = Date.now();
  const r = await fetch(`${BASE}${cesta}`, { headers: hlavicky });
  const ms = Date.now() - t0;
  const text = await r.text();
  let json = null;
  try { json = JSON.parse(text); } catch { /* není JSON */ }
  return { status: r.status, ms, text, json };
};

zapis(`# p37 — ŽIVÝ stav služby conductor (${BASE}) — ${new Date().toISOString()}`);
zapis("# READ-ONLY: volány jsou JEN GET endpointy. Žádný POST /tick.");

// ── / (seznam endpointů) ────────────────────────────────────────────────────
try {
  const r = await get("/");
  zapis("");
  zapis(`## GET / → HTTP ${r.status} (${r.ms} ms)`);
  zapis(`   ${r.text.replace(/\s+/g, " ").slice(0, 400)}`);
} catch (e) { selhalo++; zapis(`## GET / → CHYBA: ${String(e).slice(0, 200)}`); }

// ── /health (veřejné) ───────────────────────────────────────────────────────
try {
  const r = await get("/health");
  zapis("");
  zapis(`## GET /health → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json) {
    const h = r.json;
    zapis(`   ok: ${h.ok}`);
    zapis(`   ready: ${h.ready ?? h.tasks_ready ?? "?"} · running: ${h.running ?? "?"} · games: ${h.games ?? "?"}`);
    const tep = h.tep || h.tick || h;
    zapis(`   TEP: last_tick=${tep.last_tick ?? "-"} (${tep.last_tick_zdroj ?? "-"}) · ` +
      `last_cron=${tep.last_cron ?? "-"} (${tep.last_cron_min ?? "?"} min) · ` +
      `last_cron_pokus=${tep.last_cron_pokus ?? "-"} (${tep.last_cron_pokus_min ?? "?"} min)`);
    const cile = h.targets || h.cile || [];
    zapis(`   CÍLE (${Array.isArray(cile) ? cile.length : "?"}):`);
    for (const c of Array.isArray(cile) ? cile : []) {
      zapis(`     ${JSON.stringify(c).slice(0, 400)}`);
    }
    const ostatni = Object.keys(h).filter((k) => !["ok", "tep", "tick", "targets", "cile"].includes(k));
    zapis(`   další klíče: ${ostatni.join(", ")}`);
    for (const k of ostatni) {
      const v = h[k];
      if (v === null || typeof v !== "object") zapis(`     ${k} = ${v}`);
    }
  } else {
    zapis(`   (neJSON) ${r.text.slice(0, 300)}`);
  }
} catch (e) { selhalo++; zapis(`## GET /health → CHYBA: ${String(e).slice(0, 200)}`); }

// ── /roadmap (stav granulí) ─────────────────────────────────────────────────
try {
  const r = await get("/roadmap", true);
  zapis("");
  zapis(`## GET /roadmap → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json?.roadmap) {
    const rows = r.json.roadmap;
    zapis(`   řádků: ${rows.length}`);
    zapis("   item_id | task_id | task_status | attempts | status");
    for (const x of rows) {
      zapis(`   ${String(x.item_id).padEnd(28)} | ${String(x.task_id ?? "-").padStart(4)} | ` +
        `${String(x.task_status ?? "-").padEnd(9)} | ${String(x.attempts ?? "-").padStart(2)} | ${x.status}`);
    }
  } else if (r.status === 401) {
    zapis("   ⚠ HTTP 401 — tajemství nesedí (měření granulí NEPROBĚHLO)");
    selhalo++;
  } else {
    zapis(`   ${r.text.slice(0, 300)}`);
    selhalo++;
  }
} catch (e) { selhalo++; zapis(`## GET /roadmap → CHYBA: ${String(e).slice(0, 200)}`); }

// ── /queue (fronta) ─────────────────────────────────────────────────────────
try {
  const r = await get("/queue", true);
  zapis("");
  zapis(`## GET /queue → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json?.tasks) {
    zapis(`   úloh: ${r.json.tasks.length}`);
    zapis("   id | status | attempts | kind | title");
    for (const t of r.json.tasks.slice(0, 12)) {
      zapis(`   ${String(t.id).padStart(4)} | ${String(t.status).padEnd(8)} | ${String(t.attempts).padStart(2)} | ${String(t.kind).padEnd(8)} | ${String(t.title).slice(0, 60)}`);
    }
  } else { zapis(`   ${r.text.slice(0, 200)}`); }
} catch (e) { selhalo++; zapis(`## GET /queue → CHYBA: ${String(e).slice(0, 200)}`); }

// ── /status (poslední běhy) ─────────────────────────────────────────────────
try {
  const r = await get("/status", true);
  zapis("");
  zapis(`## GET /status → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json?.runs) {
    zapis(`   běhů: ${r.json.runs.length}`);
    zapis("   id | task | status | started_at | summary | pr_url");
    for (const x of r.json.runs) {
      zapis(`   ${String(x.id).padStart(4)} | ${String(x.task_id).padStart(3)} | ${String(x.status).padEnd(8)} | ` +
        `${String(x.started_at).slice(0, 19)} | ${String(x.summary ?? "-").slice(0, 40)} | ${x.pr_url ?? "-"}`);
    }
  } else { zapis(`   ${r.text.slice(0, 200)}`); }
} catch (e) { selhalo++; zapis(`## GET /status → CHYBA: ${String(e).slice(0, 200)}`); }

zapis("");
zapis(`SOUHRN: neproběhlých měření: ${selhalo}`);
writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(selhalo ? 1 : 0);

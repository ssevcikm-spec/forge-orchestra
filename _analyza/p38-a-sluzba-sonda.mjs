// p38-a-sluzba-sonda.mjs — ŽIVÝ stav služby conductor pro P38 (READ-ONLY: jen GET).
//
// ÚČEL P38: ověřit OBNOVU TIKU (H179 → zavřeno) a zapsat ji. Sonda se ptá na:
//   /health   — tep cronu (last_cron = DOKONČENÝ tik, cron_pokus = POKUS),
//               cíl (stav CI hry), ready/running
//   /roadmap  — stav granulí (item_id, status, attempts)
//
// P37 sonda `p37-sluzba-sonda.mjs` se NEPOUŽÍVÁ (H166: cizí sonda píše do
// cizího dokladu) — tenhle skript má VLASTNÍ výstupní jméno.
//
// Tajemství se čte z .secrets/cf-secrets.json (WEBHOOK_SECRET) a NIKDY se
// nevypisuje — jen se posílá v hlavičce `x-forge-secret`.
//
// Použití: node _analyza/p38-a-sluzba-sonda.mjs
// Exit 0 = obě měření proběhla; 1 = některé neproběhlo (pojmenuje se).

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p38-a-sluzba-vystup.txt");
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

zapis(`# p38-a — ŽIVÝ stav služby conductor (${BASE}) — ${new Date().toISOString()}`);
zapis("# READ-ONLY: volány jsou JEN GET endpointy. Žádný POST /tick.");

try {
  const r = await get("/health");
  zapis("");
  zapis(`## GET /health → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json) {
    const h = r.json;
    zapis(`   ok: ${h.ok} · time: ${h.time}`);
    zapis(`   ready: ${h.ready} · running: ${h.running} · games: ${h.games}`);
    zapis(`   TEP last_tick          = ${h.last_tick ?? "-"} (zdroj ${h.last_tick_zdroj ?? "-"})`);
    zapis(`   TEP last_cron          = ${h.last_cron ?? "-"} (${h.last_cron_min ?? "?"} min)`);
    zapis(`   TEP last_cron_pokus    = ${h.last_cron_pokus ?? "-"} (${h.last_cron_pokus_min ?? "?"} min)`);
    for (const c of Array.isArray(h.targets) ? h.targets : []) {
      zapis(`   CÍL: ${JSON.stringify(c).slice(0, 500)}`);
    }
  } else {
    zapis(`   (neJSON) ${r.text.slice(0, 300)}`);
    selhalo++;
  }
} catch (e) { selhalo++; zapis(`## GET /health → CHYBA: ${String(e).slice(0, 200)}`); }

try {
  const r = await get("/roadmap", true);
  zapis("");
  zapis(`## GET /roadmap → HTTP ${r.status} (${r.ms} ms)`);
  if (r.json?.roadmap) {
    const rows = r.json.roadmap;
    zapis(`   řádků: ${rows.length}`);
    const podle = new Map();
    for (const x of rows) podle.set(x.status, (podle.get(x.status) || 0) + 1);
    zapis(`   podle statusu: ${[...podle].map(([k, v]) => `${k}=${v}`).join(" · ")}`);
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

zapis("");
zapis(`SOUHRN: neproběhlých měření: ${selhalo}`);
writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(selhalo ? 1 : 0);

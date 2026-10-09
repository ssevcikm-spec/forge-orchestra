// p30-sonda-d1.mjs — PTEJ SE D1 NA TO, CO ŽIVÁ SLUŽBA NEVYDÁVÁ.
//
// PROČ: nález H111 („dispatch nic nespustí a neřekne proč") se měl rozhodnout
// mezi dvěma příčinami: (a) STROP GRANULE (`GRAIN_MAX_RUNS=8`), (b) ZÁMEK od
// úlohy, která zůstala v `tasks.status='running'`. Odpověď tiku to neřekne,
// když se dispatch nezastavil — a `runs`/`tasks` přes HTTP endpointy nemají
// ekvivalent. Tady se čtou PŘÍMO z D1 (jen SELECT, `--remote`).
//
// POZOR: `wrangler d1 execute --file=<víc dotazů>` přepne na IMPORT a výsledky
// SELECTů NEVYPÍŠE (naměřeno 9. 10. 2026) — proto se každý dotaz posílá zvlášť
// přes `--command` a čte se `--json`.
//
// Použití: node _analyza/p30-sonda-d1.mjs <jmeno-vystupu.txt>
import { execFileSync } from "node:child_process";
import { writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const WRANGLER = join(WS, "conductor", "node_modules", "wrangler", "bin", "wrangler.js");
const DB = "forge-conductor";
const out = process.argv[2] ?? "_analyza/p30-d1-vystup.txt";

const GRAIN = "(json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain'))";

const DOTAZY = [
  ["1) běhy na granuli (test stropu 8)",
   `SELECT ${GRAIN} AS item_id, COUNT(r.id) AS runs FROM runs r
      JOIN tasks t ON t.id = r.task_id
      JOIN roadmap rm ON rm.item_id = ${GRAIN}
     WHERE r.started_at IS NOT NULL AND r.started_at >= rm.created_at
     GROUP BY item_id ORDER BY runs DESC`],
  ["2) úlohy mimo terminální stav (zámek = running)",
   `SELECT id, status, attempts, substr(title,1,45) AS title, updated_at
      FROM tasks WHERE status IN ('running','ready') ORDER BY status, id`],
  ["3) počty úloh podle stavu", "SELECT status, COUNT(*) AS pocet FROM tasks GROUP BY status ORDER BY pocet DESC"],
  ["4) běhy úlohy #239 (osiřelá granule entity.enemy)",
   `SELECT r.id, r.task_id, r.status, r.started_at, r.finished_at, substr(r.summary,1,60) AS summary
      FROM runs r WHERE r.task_id = 239 ORDER BY r.id DESC LIMIT 15`],
  ["5) posledních 22 běhů (kdy se přestalo/začalo dispatchovat)",
   "SELECT id, task_id, status, started_at, finished_at FROM runs ORDER BY id DESC LIMIT 22"],
  ["6) řádky cache roadmapy", "SELECT item_id, task_id, status, created_at, updated_at FROM roadmap ORDER BY item_id"],
  ["7) H114: stopa po `entity.move.smooth`",
   `SELECT 'task' AS odkud, id AS cislo, status AS status, substr(title,1,50) AS text FROM tasks
     WHERE title LIKE '%smooth%' OR title LIKE '%plynul%'
    UNION ALL
    SELECT 'roadmap' AS odkud, task_id AS cislo, status AS status, item_id AS text FROM roadmap
     WHERE item_id LIKE '%move%'`],
  ["8) granule v souboru roadmapy vs. v cache (počet)",
   "SELECT (SELECT COUNT(*) FROM roadmap) AS radku_v_cache"],
  // ── 9–12) DODATEK: rozhodnutí H111 (strop vs. zámek) po úklidu cache ─────
  // Řádek `entity.enemy` v cache UŽ NENÍ (uklidil ho tik), takže se počet běhů
  // jeho granule musí počítat BEZ joinu na roadmap — jinak by úklid smazal důkaz.
  ["9) běhy granule `entity.enemy` (bez joinu na cache — jinak úklid smaže důkaz)",
   `SELECT COUNT(r.id) AS runs, MIN(r.started_at) AS od, MAX(r.started_at) AS do,
           COUNT(DISTINCT r.task_id) AS uholy
      FROM runs r JOIN tasks t ON t.id = r.task_id
     WHERE json_extract(t.payload, '$.grain') = 'entity.enemy' AND r.started_at IS NOT NULL`],
  ["10) všechny úlohy granule `entity.enemy` (i ty, co už v cache nejsou)",
   `SELECT t.id, t.status, t.attempts, substr(t.title,1,40) AS title, t.created_at
      FROM tasks t WHERE json_extract(t.payload, '$.grain') = 'entity.enemy' ORDER BY t.id`],
  ["11) KLÍČE ZÁMKU běžících úloh (hypotéza (b) u H111)",
   `SELECT id, status, attempts, json_extract(payload,'$.owns') AS owns,
           json_extract(payload,'$.grain') AS grain, updated_at
      FROM tasks WHERE status = 'running'`],
  ["13) časová osa běhů granule `entity.enemy` (pro výpočet počítadla stropu)",
   `SELECT r.id AS run, r.task_id, r.started_at, t.created_at AS task_vznikl
      FROM runs r JOIN tasks t ON t.id = r.task_id
     WHERE json_extract(t.payload, '$.grain') = 'entity.enemy' AND r.started_at IS NOT NULL
     ORDER BY r.started_at`],
  ["12) granule, které v cache NEJSOU, ale mají běhy (stopy po úklidu)",
   `SELECT json_extract(t.payload,'$.grain') AS grain, COUNT(r.id) AS runs
      FROM runs r JOIN tasks t ON t.id = r.task_id
     WHERE r.started_at IS NOT NULL
       AND (json_extract(t.payload,'$.game') || '/' || json_extract(t.payload,'$.grain'))
           NOT IN (SELECT item_id FROM roadmap)
     GROUP BY grain ORDER BY runs DESC`],
];

const chyby = [];
const vystup = [];
const p = (s) => { vystup.push(s); console.log(s); };

p(`# p30 sonda D1 — ${new Date().toISOString()} (jen SELECT, --remote)`);
p("");

for (const [nazev, sql] of DOTAZY) {
  p(`## ${nazev}`);
  let raw;
  try {
    raw = execFileSync(process.execPath, [WRANGLER, "d1", "execute", DB, "--remote", "--json", "--command", sql],
      { cwd: join(WS, "conductor"), encoding: "utf8", maxBuffer: 32 * 1024 * 1024, stdio: ["ignore", "pipe", "pipe"] });
  } catch (e) {
    const text = `${e.stdout ?? ""}${e.stderr ?? ""}`.slice(0, 800);
    p(`CHYBA spuštění: ${String(e.message).slice(0, 200)}`);
    p(text);
    chyby.push(nazev);
    p("");
    continue;
  }
  let data;
  try {
    // wrangler tiskne i řádky s ⛅️/🌀 — JSON začíná na prvním '[' na začátku řádku
    const i = raw.indexOf("\n[");
    data = JSON.parse(i >= 0 ? raw.slice(i + 1) : raw);
  } catch {
    p(`CHYBA parsování výstupu, syrový text níž:`);
    p(raw.slice(0, 1500));
    chyby.push(nazev);
    p("");
    continue;
  }
  const vysledky = data?.[0]?.results ?? [];
  p(JSON.stringify(vysledky, null, 1));
  p("");
}

p(chyby.length ? `CHYB: ${chyby.length} (${chyby.join(" | ")})` : "VŠE OK (0 chyb)");
writeFileSync(join(WS, out), vystup.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${out}`);
process.exit(chyby.length ? 1 : 0);

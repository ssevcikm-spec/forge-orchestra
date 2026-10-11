// p38-a-deploy.mjs — NASAZENÍ conductora TŘEMI KROKY (P38, H153: PLNÉ sha).
//
// KROK 1: push dorazil        → `git rev-list --count origin/main..HEAD` (dělá pwsh, ne tenhle skript)
// KROK 2: deploy.yml běžel na SPRÁVNÉM commitu → tenhle skript (GitHub API, `head_sha`)
// KROK 3: server posílá TU verzi → `Current Version ID` z LOGU běhu ==
//         `scriptVersion.id` ŽIVÉHO `wrangler tail` (H153: PLNÉ sha, ne zkrácené)
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
// Použití: node _analyza/p38-a-deploy.mjs [prefix-sha]
// Exit 0 = měřeno; 1 = HTTP chyba / verze z logu nenalezena.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p38-a-deploy-vystup.txt");
const REPO = "ssevcikm-spec/forge-orchestra";
const CHCEME = (process.argv[2] || "335fd8f").toLowerCase();
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: "application/vnd.github+json", "User-Agent": "forge-p38-sonda" },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status}`);
  return r.json();
};

zapis(`# p38-a — nasazení conductora (${REPO}, deploy.yml) — ${new Date().toISOString()}`);
zapis(`# hledaný commit (prefix): ${CHCEME}`);

const d = await api(`/repos/${REPO}/actions/workflows/deploy.yml/runs?per_page=15`);
zapis("");
zapis(`## POSLEDNÍCH ${d.workflow_runs.length} BĚHŮ deploy.yml (total_count=${d.total_count})`);
zapis("  #run | id       | created_at           | updated_at           | conclusion | head_sha");
for (const r of d.workflow_runs) {
  zapis(`  ${String(r.run_number).padStart(4)} | ${String(r.id).padStart(8)} | ${r.created_at} | ${r.updated_at} | ${String(r.conclusion ?? r.status).padEnd(10)} | ${r.head_sha}`);
}

const cil = d.workflow_runs.find((r) => r.head_sha.toLowerCase().startsWith(CHCEME));
if (!cil) {
  zapis("");
  zapis(`CHYBA: běh deploy.yml na commit ${CHCEME} v posledních 15 bězích NENÍ.`);
  writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
  console.log(`\n[zapsano] ${OUT}`);
  process.exit(1);
}

zapis("");
zapis(`## CÍLOVÝ BĚH #${cil.run_number} (id ${cil.id})`);
zapis(`   head_sha   = ${cil.head_sha}`);
zapis(`   head_branch= ${cil.head_branch}`);
zapis(`   created_at = ${cil.created_at} · updated_at = ${cil.updated_at}`);
zapis(`   status/conclusion = ${cil.status}/${cil.conclusion}`);
zapis(`   event      = ${cil.event}`);
zapis(`   url        = ${cil.html_url}`);

const jobs = await api(`/repos/${REPO}/actions/runs/${cil.id}/jobs`);
zapis("");
zapis(`## ÚLOHY BĚHU (${jobs.jobs.length})`);
for (const j of jobs.jobs) {
  zapis(`   ${String(j.name).padEnd(24)} | ${j.status}/${String(j.conclusion).padEnd(10)} | id=${j.id} | ${j.started_at} → ${j.completed_at}`);
}

const job = jobs.jobs[0];
if (!job) {
  zapis("CHYBA: běh nemá žádnou úlohu.");
  writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
  process.exit(1);
}

const lr = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, {
  headers: { Authorization: `Bearer ${PAT}`, "User-Agent": "forge-p38-sonda" },
  redirect: "follow",
});
const logText = (await lr.text()).replace(/\x1b\[[0-9;]*m/g, "");
// ⚠ JMÉNO DOKLADU MUSÍ MÍT `vystup.txt` — `.gitignore` zná v `_analyza/` JEN
// `*vystup.txt` (a `*.log`), takže `…-log.txt` by zůstal NETRACKOVANÝ a znečistil
// by strom i otisk vstupů inventáře.
const LOG_DOKLAD = "p38-a-deploy-raw-vystup.txt";
writeFileSync(join(WS, "_analyza", LOG_DOKLAD), logText, "utf8");
zapis("");
zapis(`## LOG ÚLOHY ${job.id} → HTTP ${lr.status}, ${logText.length} znaků (doklad: _analyza/${LOG_DOKLAD})`);

const verze = logText.match(/Current Version ID:\s*([0-9a-fA-F-]{36})/);
const nahrano = logText.match(/Uploaded\s+\S+\s+\(([\d.]+)\s*sec\)/);
zapis(`   Current Version ID = ${verze ? verze[1] : "NENALEZENO"}`);
zapis(`   Uploaded           = ${nahrano ? nahrano[0] : "NENALEZENO"}`);
const radkyTiku = logText.split(/\r?\n/).filter((l) => /Version ID|Uploaded|Deployed|workers\.dev|Total Upload|Your Worker/i.test(l));
zapis("   (řádky logu, které o nasazení něco tvrdí:)");
for (const l of radkyTiku.slice(0, 25)) zapis(`     ${l.replace(/\d{4}-\d\d-\d\dT[\d:.]+Z\s*/, "").trim().slice(0, 200)}`);

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(verze ? 0 : 1);

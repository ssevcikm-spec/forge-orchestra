// p37-deploy-behy.mjs — kdy se naposledy nasazoval CONDUCTOR (orchestra deploy.yml).
//
// Otázka P37: „tik umírá na CPU od ~13:58Z 11. 10. — co se v tom okně změnilo?“
// Tenhle skript vypíše běhy `deploy.yml` v repu ORCHESTRA (ssevcikm-spec/forge-orchestra)
// s `head_sha` a časem — tedy kdy a na jakém commitu se nasazovalo.
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
// Použití: node _analyza/p37-deploy-behy.mjs
// Exit 0 = měřeno; 1 = HTTP chyba.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p37-deploy-behy-vystup.txt");
const REPO = "ssevcikm-spec/forge-orchestra";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: "application/vnd.github+json", "User-Agent": "forge-p37-sonda" },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status}`);
  return r.json();
};

zapis(`# p37 — nasazení conductora (${REPO}, deploy.yml) — ${new Date().toISOString()}`);

const d = await api(`/repos/${REPO}/actions/workflows/deploy.yml/runs?per_page=15`);
zapis("");
zapis(`## POSLEDNÍCH ${d.workflow_runs.length} BĚHŮ deploy.yml (total_count=${d.total_count})`);
zapis("  #run | created_at           | conclusion | head_sha                                 | název");
for (const r of d.workflow_runs) {
  zapis(`  ${String(r.run_number).padStart(4)} | ${r.created_at} | ${String(r.conclusion ?? r.status).padEnd(10)} | ${r.head_sha} | ${String(r.display_title).slice(0, 50)}`);
}

zapis("");
zapis("## VŠECHNY WORKFLOW V REPU ORCHESTRA");
const w = await api(`/repos/${REPO}/actions/workflows`);
for (const x of w.workflows) zapis(`  ${x.path}  (${x.state})`);

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(0);

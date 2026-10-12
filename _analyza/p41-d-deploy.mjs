// p41-d-deploy.mjs — NASAZENÍ conductora (P41): `deploy.yml` na SPRÁVNÉM commitu
// + `Current Version ID` z LOGU (porovná se s `scriptVersion.id` živého tailu).
//
// PROČ VLASTNÍ KOPIE (H166/H191): sonda s PEVNÝM jménem výstupu přepíše cizí
// doklad — P39 si pustila P38inu sondu a přepsala `p38-a-sluzba-vystup.txt`.
// Tenhle nástroj má VLASTNÍ jména (`p41-d-deploy-vystup.txt`,
// `p41-d-deploy-raw-vystup.txt`) a TAIL DOKLAD SE MU PŘEDÁVÁ PARAMETREM, aby
// šel použít pro obě okna měření (H191: doklad nese jen poslední běh).
//
// KROKY OVĚŘENÍ NASAZENÍ (AGENTS.md):
//   1. push dorazil          → `git rev-list --count origin/main..HEAD` (dělá pwsh)
//   2. deploy.yml na SPRÁVNÉM commitu → tenhle skript (`head_sha`)
//   3. server posílá TU verzi → `Current Version ID` == `scriptVersion.id` tailu
//
// PAT se čte ze `.secrets/github_pat.txt` a NIKDY se nevypisuje.
// Použití: node _analyza/p41-d-deploy.mjs <prefix-sha> [tail-doklad.txt]
// Exit 0 = běh nalezen a verze přečtena; 1 = jinak.

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, "_analyza", "p41-d-deploy-vystup.txt");
const LOG_DOKLAD = "p41-d-deploy-raw-vystup.txt";
const REPO = "ssevcikm-spec/forge-orchestra";
const CHCEME = (process.argv[2] || "").toLowerCase();
const TAIL = process.argv[3] || "p41-e-tail-raw-vystup.txt";
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();

if (!CHCEME) {
  console.log("pouziti: node _analyza/p41-d-deploy.mjs <prefix-sha> [tail-doklad.txt]");
  process.exit(2);
}

const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };

const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: {
      Authorization: `Bearer ${PAT}`,
      Accept: "application/vnd.github+json",
      "User-Agent": "forge-p41-deploy",
    },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status}`);
  return r.json();
};

zapis(`# p41-d — nasazení conductora (${REPO}, deploy.yml) — ${new Date().toISOString()}`);
zapis(`# hledaný commit (prefix): ${CHCEME}`);
zapis(`# tail doklad pro 3. krok: _analyza/${TAIL}`);

const d = await api(`/repos/${REPO}/actions/workflows/deploy.yml/runs?per_page=15`);
zapis("");
zapis(`## POSLEDNÍCH ${d.workflow_runs.length} BĚHŮ deploy.yml (total_count=${d.total_count})`);
zapis("  #run | id       | created_at           | updated_at           | conclusion | head_sha");
for (const r of d.workflow_runs) {
  zapis(`  ${String(r.run_number).padStart(4)} | ${String(r.id).padStart(8)} | ${r.created_at} | `
    + `${r.updated_at} | ${String(r.conclusion ?? r.status).padEnd(10)} | ${r.head_sha}`);
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
  zapis(`   ${String(j.name).padEnd(24)} | ${j.status}/${String(j.conclusion).padEnd(10)} | `
    + `id=${j.id} | ${j.started_at} → ${j.completed_at}`);
}

const job = jobs.jobs[0];
if (!job) {
  zapis("CHYBA: běh nemá žádnou úlohu.");
  writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
  process.exit(1);
}
if (job.status !== "completed") {
  zapis("");
  zapis(`POZOR: úloha ještě NEDOBĚHLA (${job.status}) — verze z logu nemusí být konečná.`);
}

const lr = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, {
  headers: { Authorization: `Bearer ${PAT}`, "User-Agent": "forge-p41-deploy" },
  redirect: "follow",
});
const logText = (await lr.text()).replace(/\x1b\[[0-9;]*m/g, "");
writeFileSync(join(WS, "_analyza", LOG_DOKLAD), logText, "utf8");
zapis("");
zapis(`## LOG ÚLOHY ${job.id} → HTTP ${lr.status}, ${logText.length} znaků (doklad: _analyza/${LOG_DOKLAD})`);

const verze = logText.match(/Current Version ID:\s*([0-9a-fA-F-]{36})/);
const nahrano = logText.match(/Uploaded\s+\S+\s+\(([\d.]+)\s*sec\)/);
const upload = logText.match(/Total Upload:\s*([\d.]+\s*\w+)/);
zapis(`   Current Version ID = ${verze ? verze[1] : "NENALEZENO"}`);
zapis(`   Uploaded           = ${nahrano ? nahrano[0] : "NENALEZENO"}`);
zapis(`   Total Upload       = ${upload ? upload[1] : "NENALEZENO"}`);
zapis("   (řádky logu, které o nasazení něco tvrdí:)");
for (const l of logText.split(/\r?\n/).filter((l) => /Version ID|Uploaded|Deployed|workers\.dev|Total Upload|Your Worker/i.test(l)).slice(0, 25)) {
  zapis(`     ${l.replace(/\d{4}-\d\d-\d\dT[\d:.]+Z\s*/, "").trim().slice(0, 200)}`);
}

// ── TŘETÍ KROK: POROVNÁNÍ SE ŽIVÝM TAILEM ─────────────────────────────────
// `scriptVersion.id` z tailu se bere z RAW dokladu (když existuje) — a když
// existuje, POROVNÁ SE. „Verze z logu" bez protějšku v tailu není důkaz.
const tailRaw = join(WS, "_analyza", TAIL);
zapis("");
zapis("## SROVNÁNÍ S ŽIVÝM TAILEM (krok 3 ověření nasazení)");
try {
  const tail = readFileSync(tailRaw, "utf8");
  const vTailu = [...tail.matchAll(/"scriptVersion"\s*:\s*\{[^}]*?"id"\s*:\s*"([0-9a-fA-F-]{36})"/gs)]
    .map((m) => m[1]);
  const unikatni = [...new Set(vTailu)];
  zapis(`   tail: ${TAIL} · verzí v tailu: ${unikatni.length}`);
  for (const v of unikatni) zapis(`     tail scriptVersion.id = ${v}`);
  if (verze) {
    zapis(`   ${unikatni.length === 1 && unikatni[0] === verze[1] ? "✓ SHODA" : "✗ NESHODA"}:`
      + ` log ${verze[1]} vs tail ${unikatni.join(", ") || "(žádná)"}`);
  }
} catch {
  zapis("   tail zatím NENÍ (pustí se po nasazení) — porovnání proběhne potom.");
}

writeFileSync(OUT, radky.join("\n") + "\n", "utf8");
console.log(`\n[zapsano] ${OUT}`);
process.exit(verze ? 0 : 1);

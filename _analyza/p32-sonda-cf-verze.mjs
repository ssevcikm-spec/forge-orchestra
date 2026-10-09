// p32-sonda-cf-verze.mjs — KROK 3 ověření nasazení conductora: KTERÁ VERZE je nahraná?
//
// PROČ: u změny, která mění jen KOMENTÁŘE, není na chování služby co vidět
// (a „HTTP 200“ není důkaz — starý worker odpovídá taky). Dokladem nového
// artefaktu je proto **log nasazovacího běhu**: wrangler v něm vypisuje
// nahranou verzi (`Version ID`, `Uploaded`, `Deployed`).
//
// ⚠ `/actions/jobs/<id>/logs` PŘESMĚRUJE (302) na blob storage — Python
// `urllib` na tom padá a vypadá to jako neplatný PAT; Node `fetch` to zvládne.
// PAT se čte ze souboru a NIKDY se nevypisuje.
//
// Použití: node _analyza/p32-sonda-cf-verze.mjs <sha> [vystup.txt]
import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const sha = process.argv[2];
const out = process.argv[3] ?? "_analyza/p32-cf-verze-vystup.txt";
if (!sha) { console.log("CHYBA: chybí <sha> commitu, na kterém má nasazení běžet"); process.exit(2); }

const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();
const REPO = "ssevcikm-spec/forge-orchestra";
const H = { authorization: `Bearer ${PAT}`, accept: "application/vnd.github+json", "user-agent": "forge-p32" };
const radky = [];
const zapis = (x = "") => { radky.push(x); console.log(x); };
const uloz = () => writeFileSync(join(WS, out), radky.join("\n") + "\n", "utf8");
const json = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return { status: r.status, body: await r.json().catch(() => null) };
};

zapis(`# P32 — verze nasazeného conductora — ${new Date().toISOString()}`);
zapis(`# hledám běh deploy.yml na commitu ${sha} (repo ${REPO})`);

const runs = await json(`/repos/${REPO}/actions/workflows/deploy.yml/runs?head_sha=${sha}&per_page=5`);
const run = (runs.body?.workflow_runs ?? [])[0];
if (!run) {
  zapis(`CHYBA: na commitu ${sha} NENÍ žádný běh deploy.yml`);
  uloz();
  process.exit(1);
}
zapis(`# běh #${run.run_number} (id=${run.id}) status=${run.status}/${run.conclusion} created=${run.created_at}`);
zapis(`# ${run.html_url}`);

const jobs = await json(`/repos/${REPO}/actions/runs/${run.id}/jobs`);
const job = (jobs.body?.jobs ?? [])[0];
if (!job) { zapis("CHYBA: běh nemá žádný job"); uloz(); process.exit(1); }
zapis(`# job „${job.name}“ (id=${job.id}) status=${job.status}/${job.conclusion}`);

const r = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const raw = await r.text();
zapis(`# GET /actions/jobs/${job.id}/logs -> HTTP ${r.status} (${raw.length} B)`);

const text = raw.replace(/\x1b\[[0-9;]*m/g, "");
const zajimave = text.split(/\r?\n/).filter((l) =>
  /Version ID|Uploaded|Deployed|Current Version|worker|forge-conductor|Total Upload/i.test(l));
zapis("");
zapis("## ŘÁDKY Z LOGU, KTERÉ NESOU VERZI ARTEFAKTU");
for (const l of zajimave.slice(-30)) zapis("  " + l.trim().slice(0, 200));

uloz();
console.log(`\n[zapsano] ${out} (${radky.join("\n").length} znaku)`);
process.exit(r.status === 200 ? 0 : 1);

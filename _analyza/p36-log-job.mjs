// p36-log-job.mjs — stáhne CELÝ log jednoho jobu (job-level log NENÍ zip)
// a uloží ho do _analyza/p36-log-job-<id>-vystup.txt. Vypíše i řez okolo chyby.
//
// PROČ: 14 z 29 selhaných běhů agenta spadlo v jobu „Otevři pull request“ na
// `fatal: could not read Username for 'https://github.com'`. Filtrovaný log
// (jen řádky s „error“) ukáže NÁSLEDEK, ne PŘÍČINU — potřebuju vidět, co
// akce dělala předtím (jestli dostala token, nebo prázdný řetězec).
//
// Použití: node _analyza/p36-log-job.mjs <job_id> [hledany-vzor]

import { readFileSync, writeFileSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const PAT = readFileSync(join(WS, ".secrets", "github_pat.txt"), "utf8").trim();
const HRA = "ssevcikm-spec/uo-shadows";
const jobId = process.argv[2];
const vzor = process.argv[3] ? new RegExp(process.argv[3], "i") : null;
if (!jobId) { console.log("chybí job_id"); process.exit(2); }

const r = await fetch(`https://api.github.com/repos/${HRA}/actions/jobs/${jobId}/logs`, {
  headers: {
    Authorization: `Bearer ${PAT}`,
    Accept: "application/vnd.github+json",
    "User-Agent": "forge-p36-sonda",
  },
  redirect: "follow",
});
const text = await r.text();
if (!r.ok) { console.log(`HTTP ${r.status}: ${text.slice(0, 300)}`); process.exit(1); }

const cist = text.replace(/\x1b\[[0-9;]*m/g, "");
const radky = cist.split(/\r?\n/).map((l) => l.replace(/^\S+Z\s?/, "").trimEnd());
const out = join(WS, "_analyza", `p36-log-job-${jobId}-vystup.txt`);
writeFileSync(out, radky.join("\n") + "\n", "utf8");
console.log(`# ${radky.length} řádků -> ${out}`);

if (vzor) {
  const idx = radky.map((l, i) => (vzor.test(l) ? i : -1)).filter((i) => i >= 0);
  console.log(`# řádků odpovídajících ${vzor}: ${idx.length}`);
  for (const i of idx.slice(0, 10)) {
    console.log(`\n--- okolí řádku ${i} ---`);
    for (const l of radky.slice(Math.max(0, i - 12), i + 6)) console.log("  " + l);
  }
} else {
  for (const l of radky) console.log(l);
}

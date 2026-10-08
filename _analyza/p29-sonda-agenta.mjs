// P28/P29 — SONDA: CO DĚLAL AGENT UVNITŘ BĚHU (hledá v logu klíčové řádky)
//
// PROČ: „Agent nic nezměnil“ je verdikt WORKFLOW, ale ne důvod. Důvod je
// v logu kroku „Spusť agenta“ (aider): kolik toho dostal, co odpověděl,
// jestli změnil soubor. Tenhle skript vypíše jen řádky, které něco říkají.
//
// Použití: node _analyza/p29-sonda-agenta.mjs <run_id> [job_index]
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json',
  'User-Agent': 'forge-p28', 'X-GitHub-Api-Version': '2022-11-28' };
const REPO = 'ssevcikm-spec/uo-shadows';
const runId = process.argv[2];
if (!runId) { console.log('použití: node _analyza/p29-sonda-agenta.mjs <run_id>'); process.exit(1); }

const api = async (p) => (await fetch(`https://api.github.com${p}`, { headers: H })).json();

const jobs = await api(`/repos/${REPO}/actions/runs/${runId}/jobs`);
const job = (jobs.jobs || [])[Number(process.argv[3] || 0)];
if (!job) { console.log('job nenalezen'); process.exit(1); }
const r = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const raw = await r.text();
const radky = raw.replace(/\x1b\[[0-9;]*m/g, '')
  .split(/\r?\n/)
  .map((l) => l.replace(/^\d{4}-\d{2}-\d{2}T[\d:.]+Z\s*/, ''));

const SMETI = /(Collecting |Downloading |Using cached|Requirement already|Installing collected|Successfully installed|pip install|DEP0040|DEP0169|punycode|url\.parse|node:\d+\))/;
const ZAJIMAVE = /(Aider v|Model:|Tokens:|No changes|no changes|Applied edit|Committing|context window|Error|ERROR|Traceback|aider\.chat|> |#### |git diff|nic nezměnil|litellm|cerebras|rate limit|429|Warning for|Failed|refus)/;
console.log(`LOG BĚHU ${runId}, job ${job.name} (${job.conclusion}) — jen řádky, které něco říkají:`);
let n = 0;
for (const l of radky) {
  if (ZAJIMAVE.test(l) && !SMETI.test(l) && l.trim().length > 3) {
    console.log('  | ' + l.trim().slice(0, 200));
    if (++n > 160) { console.log('  … (ořezáno)'); break; }
  }
}
console.log(`\n(celkem řádků logu: ${radky.length}; vypsáno ${n})`);

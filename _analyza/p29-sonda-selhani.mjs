// P28/P29 — SONDA: PROC SELHAL AGENT? (log z GitHub Actions, jen čtení)
//
// PROČ: `/failed` vrací prázdný `log_tail`, takže důvod selhání v orchestra NENÍ.
// Autorita je log běhu `agent.yml` v repu hry. Skript čte poslední běhy a u
// POSLEDNÍHO SELHANÉHO vypíše konec logu bez ANSI barev.
//
// Použití: node _analyza/p29-sonda-selhani.mjs [pocet_behu]
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json',
  'User-Agent': 'forge-p28', 'X-GitHub-Api-Version': '2022-11-28' };
const REPO = 'ssevcikm-spec/uo-shadows';
const N = Number(process.argv[2] || 12);

const api = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return { status: r.status, body: await r.json().catch(() => null) };
};

const wf = await api(`/repos/${REPO}/actions/workflows`);
console.log('WORKFLOWY: ' + (wf.body?.workflows || []).map((w) => w.path).join(', '));

const runs = await api(`/repos/${REPO}/actions/runs?per_page=${N}`);
if (runs.status !== 200) {
  console.log('CHYBA čtení běhů:', runs.status);
  process.exit(1);
}
console.log('\nPOSLEDNÍ BĚHY (%d):', runs.body.workflow_runs.length);
for (const r of runs.body.workflow_runs) {
  console.log(`  ${String(r.id).padEnd(12)} ${String(r.name).slice(0, 22).padEnd(24)} ${String(r.status).padEnd(10)} ${String(r.conclusion).padEnd(9)} ${r.created_at} #${r.run_number} ${r.head_branch} ${r.event}`);
}

const selhany = runs.body.workflow_runs.find((r) => r.conclusion === 'failure');
if (!selhany) {
  console.log('\n(žádný selhaný běh v posledních %d — není co číst)', N);
  process.exit(0);
}
console.log(`\nSELHANÝ BĚH: id=${selhany.id} ${selhany.name} #${selhany.run_number} (${selhany.created_at})`);
const jobs = await api(`/repos/${REPO}/actions/runs/${selhany.id}/jobs`);
const job = (jobs.body?.jobs || [])[0];
if (!job) { console.log('  (běh nemá joby)'); process.exit(0); }
console.log(`  job: ${job.name} → ${job.conclusion} (id ${job.id}); kroky:`);
for (const s of job.steps || []) console.log(`     ${String(s.conclusion).padEnd(9)} ${s.name}`);

// ⚠ Log se přesměrovává na blob storage — `fetch` v Node redirecty sleduje sám.
const r = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const raw = await r.text();
const cisty = raw.replace(/\x1b\[[0-9;]*m/g, '').split(/\r?\n/).map((l) => l.replace(/^\S+\s/, ''));
console.log(`\nKONEC LOGU (posledních 45 řádků, bez ANSI a bez časových prefixů):`);
for (const l of cisty.filter((x) => x.trim()).slice(-45)) console.log('   | ' + l.slice(0, 170));

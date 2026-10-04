import { readFileSync, writeFileSync } from 'node:fs';
const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'h17' };
const beh = process.argv[2];
const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${beh}/jobs`, { headers: H })).json();
for (const j of jobs.jobs || []) {
  console.log(`JOB ${j.id}  ${j.name}  ${j.status}/${j.conclusion||'-'}  steps:`);
  for (const s of j.steps || []) console.log(`     ${s.number}. ${s.name}  -> ${s.conclusion}`);
}
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent')) || jobs.jobs[0];
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const txt = await lg.text();
writeFileSync(`_analyza/h17-log-${beh}.txt`, txt, 'utf8');
console.log(`\nlog ulozen: _analyza/h17-log-${beh}.txt  (${txt.length} znaku)`);

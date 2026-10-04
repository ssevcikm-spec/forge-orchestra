import { readFileSync } from 'node:fs';
const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'h17' };
const r = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=25`, { headers: H })).json();
console.log('total_count =', r.total_count);
for (const x of r.workflow_runs || []) {
  console.log(`#${x.run_number}  id=${x.id}  ${x.name}  ${x.status}/${x.conclusion || '-'}  head:${x.head_sha.slice(0,9)}  created=${x.created_at}  event=${x.event}`);
}
console.log('\n=== PRs ===');
const p = await (await fetch(`https://api.github.com/repos/${REPO}/pulls?state=all&per_page=15&sort=created&direction=desc`, { headers: H })).json();
for (const x of p) console.log(`PR #${x.number}  ${x.state}  merged=${x.merged_at || '-'}  head=${x.head.ref}  title=${x.title.slice(0,70)}`);

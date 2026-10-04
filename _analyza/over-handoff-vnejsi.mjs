// Ověří vnější tvrzení HANDOFF.md §9 a §8: CI na main, poslední běhy, PR #26/#27.
import fs from 'node:fs';

const pat = fs.readFileSync('orchestra/.secrets/github_pat.txt', 'utf8').trim();
const h = {
  Authorization: 'Bearer ' + pat,
  'User-Agent': 'forge-over',
  Accept: 'application/vnd.github+json',
};
const api = async (p) => {
  const r = await fetch('https://api.github.com' + p, { headers: h });
  return { status: r.status, json: r.ok ? await r.json() : null };
};

console.log('=== CI na main: je success na 807803e? (§9) ===');
{
  const { json } = await api(
    '/repos/ssevcikm-spec/uo-shadows/commits/807803e/check-runs?per_page=30',
  );
  for (const c of json?.check_runs ?? []) {
    console.log(`  ${(c.conclusion ?? c.status).padEnd(10)} ${c.name}`);
  }
}

console.log('\n=== PR #26 a #27 — sloučily se samy? (§8) ===');
for (const n of [26, 27]) {
  const { json } = await api(`/repos/ssevcikm-spec/uo-shadows/pulls/${n}`);
  if (!json) {
    console.log(`  PR #${n}: nenalezen`);
    continue;
  }
  console.log(
    `  PR #${n} ${json.state}/${json.merged ? 'MERGED' : 'ne-'} merge_commit:${json.merge_commit_sha?.slice(0, 7)} merged_by:${json.merged_by?.login ?? '?'} "${json.title}"`,
  );
}

console.log('\n=== Pocet behu agent.yml (§8 tvrdi "20 behu celkem, 4 uspechy") ===');
{
  const { json } = await api(
    '/repos/ssevcikm-spec/uo-shadows/actions/workflows/agent.yml/runs?per_page=100',
  );
  const runs = json?.workflow_runs ?? [];
  const podleVysledku = {};
  for (const r of runs) podleVysledku[r.conclusion ?? r.status] = (podleVysledku[r.conclusion ?? r.status] ?? 0) + 1;
  console.log('  celkem (total_count):', json?.total_count);
  console.log('  rozpad posledních', runs.length, ':', JSON.stringify(podleVysledku));
}

console.log('\n=== Behly po oprave Pillow dalsi práce? ===');
{
  const { json } = await api(
    '/repos/ssevcikm-spec/uo-shadows/actions/workflows/agent.yml/runs?per_page=6',
  );
  for (const r of json?.workflow_runs ?? []) {
    console.log(`  #${r.run_number} ${r.status}/${r.conclusion} ${r.created_at}`);
  }
}

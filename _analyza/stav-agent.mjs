// Poslední vydané granule = důkaz, že orchestra SKUTEČNĚ pracuje (ne jen že je zelená).
import fs from 'node:fs';

const pat = fs.readFileSync('orchestra/.secrets/github_pat.txt', 'utf8').trim();
const h = {
  Authorization: 'Bearer ' + pat,
  'User-Agent': 'forge-stav',
  Accept: 'application/vnd.github+json',
};

const url =
  'https://api.github.com/repos/ssevcikm-spec/uo-shadows/actions/workflows/agent.yml/runs?per_page=12';
const r = await fetch(url, { headers: h });
console.log('agent.yml -> HTTP', r.status);
const j = await r.json();
console.log('=== Posledni behy agenta (orchestra vydava granule) ===');
for (const w of j.workflow_runs || []) {
  const kdy = new Date(w.created_at);
  console.log(
    `#${String(w.run_number).padStart(4)} ${(w.status + '/' + w.conclusion).padEnd(22)} ${w.created_at}  ${(w.display_title ?? '').slice(0, 60)}`,
  );
}
console.log('celkem behu agent.yml:', j.total_count);

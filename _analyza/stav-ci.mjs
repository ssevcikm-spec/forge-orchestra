// Zjistí POSLEDNÍ BĚHY CI na `main` u obou repů (stav cíle, ne jen řídicího systému).
// Důvod: AGENTS.md — „Zelený řídicí systém není důkaz, že práce probíhá."
// PAT se čte ze souboru a NIKDY se nevypisuje.
import fs from 'node:fs';

const pat = fs.readFileSync('orchestra/.secrets/github_pat.txt', 'utf8').trim();
const h = {
  Authorization: 'Bearer ' + pat,
  'User-Agent': 'forge-stav',
  Accept: 'application/vnd.github+json',
};

async function behy(repo, workflow) {
  const url = `https://api.github.com/repos/ssevcikm-spec/${repo}/actions/workflows/${workflow}/runs?branch=main&per_page=6`;
  const r = await fetch(url, { headers: h });
  if (!r.ok) {
    console.log(`  ${repo}/${workflow}: HTTP ${r.status}`);
    return null;
  }
  const j = await r.json();
  console.log(`  ${repo}/${workflow}:`);
  for (const w of j.workflow_runs || []) {
    const verdikt = `${w.status}/${w.conclusion}`;
    console.log(
      `    #${w.run_number} ${verdikt.padEnd(22)} head:${w.head_sha.slice(0, 7)} ${w.created_at}  ${w.display_title?.slice(0, 50) ?? ''}`,
    );
  }
  return j.workflow_runs?.[0] ?? null;
}

console.log('=== Posledni behy na main ===');
for (const [repo, wf] of [
  ['uo-shadows', 'ci.yml'],
  ['uo-shadows', 'release.yml'],
  ['forge-orchestra', 'ci.yml'],
]) {
  await behy(repo, wf);
}

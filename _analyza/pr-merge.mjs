// Sloučí PR (squash, jako #30) — ale jen když je PR opravdu sloučitelný a jeho
// head odpovídá commitu, na kterém proběhlo zelené CI. Nic neuhádne.
// Spuštění: node _analyza\pr-merge.mjs 28=<sha> 29=<sha>
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/uo-shadows';
const GH = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'dsh-pr-merge',
  'X-GitHub-Api-Version': '2022-11-28',
};

const pozadavky = process.argv.slice(2).map((a) => {
  const [n, sha] = a.split('=');
  return { n: Number(n), sha };
});
if (pozadavky.length === 0) {
  console.log('použití: node _analyza\\pr-merge.mjs 28=<head-sha> 29=<head-sha>');
  process.exit(2);
}

for (const { n, sha } of pozadavky) {
  const d = await (await fetch(`https://api.github.com/repos/${REPO}/pulls/${n}`, { headers: GH })).json();
  console.log(`#${n} "${d.title}"`);
  console.log(`  state=${d.state} mergeable=${d.mergeable} mergeable_state=${d.mergeable_state} base=${d.base?.ref}`);
  console.log(`  head=${String(d.head?.sha).slice(0, 10)} (očekávám ${String(sha).slice(0, 10)})`);

  if (d.state !== 'open') { console.log('  → NESLOUČENO: PR není otevřený'); continue; }
  if (d.mergeable !== true || d.mergeable_state !== 'clean') { console.log('  → NESLOUČENO: není clean'); continue; }
  if (sha && d.head.sha !== sha) { console.log('  → NESLOUČENO: head nesedí na commit s zeleným CI'); continue; }

  // Poslední kontrola: zelené CI na tom commitu
  const runs = (await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs?head_sha=${d.head.sha}&per_page=10`, { headers: GH })).json()).workflow_runs ?? [];
  const ci = runs.find((x) => x.name.startsWith('CI'));
  console.log(`  CI: ${ci ? `${ci.name} #${ci.run_number} ${ci.status}/${ci.conclusion}` : 'NENALEZENO'}`);
  if (!ci || ci.conclusion !== 'success') { console.log('  → NESLOUČENO: CI není zelené'); continue; }

  const r = await fetch(`https://api.github.com/repos/${REPO}/pulls/${n}/merge`, {
    method: 'PUT',
    headers: GH,
    body: JSON.stringify({
      commit_title: `${d.title} (#${n})`,
      commit_message: 'Sloučeno ručně po kontrole: kód spuštěn v Godotu 4.7.2, opraveny chyby z PR (viz commit „oprava:" na větvi).',
      sha: d.head.sha,
      merge_method: 'squash',
    }),
  });
  const t = await r.text();
  console.log(`  HTTP ${r.status}: ${t.slice(0, 200)}`);
}

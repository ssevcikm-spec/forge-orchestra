// Detail PR + diff do souboru (diff je dlouhý, čte se read toolem).
// Spuštění: node _analyza\pr-detail.mjs 28 29 30
import { readFileSync, writeFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = 'ssevcikm-spec/uo-shadows';
const GH = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'dsh-pr-detail',
  'X-GitHub-Api-Version': '2022-11-28',
};
const cisla = process.argv.slice(2).filter((a) => /^\d+$/.test(a));

for (const n of cisla) {
  const r = await fetch(`https://api.github.com/repos/${REPO}/pulls/${n}`, { headers: GH });
  const d = await r.json();
  console.log(`=== #${n} ${d.title}`);
  console.log(`    state=${d.state} merged=${d.merged} merged_at=${d.merged_at} merged_by=${d.merged_by?.login ?? 'null'}`);
  console.log(`    merge_commit_sha=${d.merge_commit_sha}`);
  console.log(`    base_sha=${String(d.base?.sha).slice(0, 10)} head_sha=${String(d.head?.sha).slice(0, 10)}`);
  console.log(`    additions=${d.additions} deletions=${d.deletions} changed_files=${d.changed_files} commits=${d.commits}`);
  console.log(`    created=${d.created_at} updated=${d.updated_at}`);

  // merge commit — kdo a kdy (u sloučených)
  if (d.merge_commit_sha) {
    const c = await (await fetch(`https://api.github.com/repos/${REPO}/commits/${d.merge_commit_sha}`, { headers: GH })).json();
    console.log(`    merge commit: ${String(c.sha).slice(0, 10)} autor=${c.commit?.author?.name} <${c.commit?.author?.email}> datum=${c.commit?.author?.date}`);
    console.log(`      zpráva: ${String(c.commit?.message).split('\n')[0]}`);
    console.log(`      parents: ${(c.parents ?? []).map((p) => p.sha.slice(0, 10)).join(' + ')}`);
  }

  // PR komentáře (co psala orchestra / člověk)
  const cs = await (await fetch(`https://api.github.com/repos/${REPO}/issues/${n}/comments?per_page=50`, { headers: GH })).json();
  if (Array.isArray(cs) && cs.length) {
    console.log(`    komentářů: ${cs.length}`);
    for (const c of cs) console.log(`      [${c.created_at}] ${c.user?.login}: ${String(c.body).replace(/\s+/g, ' ').slice(0, 300)}`);
  }

  const dr = await fetch(`https://api.github.com/repos/${REPO}/pulls/${n}`, {
    headers: { ...GH, Accept: 'application/vnd.github.v3.diff' },
  });
  const diff = await dr.text();
  const out = `${WS}/_analyza/pr${n}.diff`;
  writeFileSync(out, diff, 'utf8');
  console.log(`    DIFF → _analyza/pr${n}.diff (${diff.length} B, ${diff.split('\n').length} řádků)\n`);
}

// Živý stav PR v herním repu — čte GitHub API, ne dokumentaci.
// Spuštění: node _analyza\pr-stav.mjs            (jen otevřené PR)
//           node _analyza\pr-stav.mjs --vsechny  (i zavřené/sloučené, posledních 15)
// PAT se čte ze souboru a NIKDY se nevypisuje.
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const PAT = readFileSync(`${WS}/orchestra/.secrets/github_pat.txt`, 'utf8').trim();
const REPO = process.argv.slice(2).find((a) => !a.startsWith('--')) ?? 'ssevcikm-spec/uo-shadows';
const VSECHNY = process.argv.includes('--vsechny');
const GH = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'dsh-pr-stav',
  'X-GitHub-Api-Version': '2022-11-28',
};

async function gh(path, accept) {
  const r = await fetch(`https://api.github.com${path}`, {
    headers: accept ? { ...GH, Accept: accept } : GH,
  });
  const t = await r.text();
  if (accept && accept.includes('diff')) return { status: r.status, text: t };
  try {
    return { status: r.status, j: JSON.parse(t) };
  } catch {
    return { status: r.status, j: null, text: t.slice(0, 300) };
  }
}

console.log(`# PR stav — ${new Date().toISOString()}`);
console.log(`# repo ${REPO}\n`);

// --- hlavní větev ---
const mainRef = await gh(`/repos/${REPO}/git/ref/heads/main`);
const mainSha = mainRef.j?.object?.sha;
console.log(`main = ${mainSha?.slice(0, 10)} (${mainRef.status})`);

const state = VSECHNY ? 'all' : 'open';
const prs = [];
for (let page = 1; page <= 3; page++) {
  const r = await gh(`/repos/${REPO}/pulls?state=${state}&per_page=100&page=${page}&sort=created&direction=desc`);
  if (!Array.isArray(r.j) || r.j.length === 0) break;
  prs.push(...r.j);
  if (r.j.length < 100) break;
}
const seznam = VSECHNY ? prs.slice(0, 15) : prs;
console.log(`PR (state=${state}): ${prs.length}${VSECHNY ? `, vypisuji ${seznam.length}` : ''}\n`);

for (const p of seznam) {
  // detail — seznam vrací mergeable_by null a mergeable jen v detailu
  let d = await gh(`/repos/${REPO}/pulls/${p.number}`);
  for (let i = 0; i < 5 && d.j?.mergeable === null; i++) {
    await new Promise((s) => setTimeout(s, 1200));
    d = await gh(`/repos/${REPO}/pulls/${p.number}`);
  }
  const det = d.j ?? {};
  console.log(`=== #${p.number}  ${p.title}`);
  console.log(`    stav=${p.state}${p.draft ? ' DRAFT' : ''} sloučeno=${p.merged_at ?? 'ne'} zavřeno=${p.closed_at ?? 'ne'}`);
  console.log(`    autor=${p.user?.login}  větev head=${p.head?.ref} ← base=${p.base?.ref}`);
  console.log(`    head=${String(p.head?.sha).slice(0, 10)}  base_sha=${String(p.base?.sha).slice(0, 10)}  ${p.base?.sha === mainSha ? '(base == main)' : '(base != main — VĚTEV JE POZADU)'}`);
  console.log(`    +${p.additions}/-${p.deletions} v ${p.changed_files} souborech  mergeable=${det.mergeable} mergeable_state=${det.mergeable_state}`);
  console.log(`    created=${p.created_at} updated=${p.updated_at} commits=${p.commits} comments=${p.comments} review_comments=${p.review_comments}`);

  // soubory
  const f = await gh(`/repos/${REPO}/pulls/${p.number}/files?per_page=100`);
  if (Array.isArray(f.j)) {
    for (const x of f.j) console.log(`      ${x.status.padEnd(9)} +${String(x.additions).padStart(4)}/-${String(x.deletions).padStart(4)}  ${x.filename}`);
  }

  // CI na head commitu
  const cr = await gh(`/repos/${REPO}/commits/${p.head.sha}/check-runs?per_page=100`);
  const runs = cr.j?.check_runs ?? [];
  console.log(`    CI check-runs na head: ${runs.length}`);
  for (const c of runs) console.log(`      [${c.status}/${c.conclusion}] ${c.name}`);
  const st = await gh(`/repos/${REPO}/commits/${p.head.sha}/status`);
  console.log(`    combined status: ${st.j?.state ?? '?'} (${st.j?.statuses?.length ?? 0} statuses)`);
  const wf = await gh(`/repos/${REPO}/actions/runs?head_sha=${p.head.sha}&per_page=20`);
  for (const r of wf.j?.workflow_runs ?? []) {
    console.log(`      workflow ${r.name} #${r.run_number} ${r.status}/${r.conclusion} event=${r.event}`);
  }

  // revize
  const rv = await gh(`/repos/${REPO}/pulls/${p.number}/reviews?per_page=50`);
  if (Array.isArray(rv.j) && rv.j.length) {
    for (const v of rv.j) console.log(`      review: ${v.user?.login} ${v.state} ${v.submitted_at}`);
  }
  console.log('');
}

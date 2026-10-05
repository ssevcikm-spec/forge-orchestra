import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Overi, zda behy pouzivaji nove razeni any/strong a preskakovani druheho pokusu.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'overeni' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const j = await gh(`/repos/${REPO}/actions/runs?per_page=12`);
const behy = (j.workflow_runs || []).filter((x) => /Forge #/.test(x.name || '') && x.conclusion);
console.log(`dokončených běhů k rozboru: ${behy.length}\n`);

const vzory = [
  /providers\.json: orchestra \+ routing/,
  /řazení podle štědrosti kvóty/,
  /silné modely až po slabých/,
  /zkouším v pořadí/,
  /vyčerpané kvótě – druhý poskytovatel se nezkouší/,
  /silných modelů posunuto podle run_key/,
];

for (const x of behy.slice(0, 5)) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) continue;
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const t = (await lg.text()).replace(/\x1b\[[0-9;]*m/g, '').replace(/^\S*Z\s?/gm, '');
  console.log(`── ${x.name.slice(0, 24)}  ${x.conclusion}  ${x.created_at.slice(11, 19)}`);
  let nalezeno = 0;
  for (const v of vzory) {
    const m = t.match(v);
    if (m) {
      const radek = t.split('\n').find((l) => v.test(l));
      console.log(`   ✓ ${radek.trim().slice(0, 130)}`);
      nalezeno++;
    }
  }
  if (!nalezeno) console.log('   (žádný z příznaků nového řazení – běh je z doby před nasazením)');
  console.log();
}

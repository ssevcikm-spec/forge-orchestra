import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vytahne logy z behu noveho DAG a najde pricinu selhani.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status };
};

// vezmi posledni selhany beh z kazdeho tasku 107-110
const runs = await gh(`/repos/${REPO}/actions/runs?per_page=100`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #1(07|08|09|10)\b/.test(x.name || ''));
const podleTasku = {};
for (const x of forge) {
  const id = Number(/Forge #(\d+)/.exec(x.name)[1]);
  if (!podleTasku[id]) podleTasku[id] = x;   // prvni = nejnovejsi
}

for (const [taskId, run] of Object.entries(podleTasku)) {
  console.log(`\n${'═'.repeat(70)}`);
  console.log(`TASK #${taskId}  run=${run.id}  ${run.conclusion}  ${run.created_at}`);
  console.log('═'.repeat(70));

  const jobs = await gh(`/repos/${REPO}/actions/runs/${run.id}/jobs`);
  for (const j of jobs.jobs || []) {
    console.log(`\n--- job: ${j.name} -> ${j.conclusion} ---`);
    for (const s of j.steps || []) {
      const znak = s.conclusion === 'success' ? 'ok' : s.conclusion === 'skipped' ? '--' : 'XX';
      console.log(`  ${znak} ${s.name}`);
    }
    if (j.conclusion === 'success') continue;

    const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${j.id}/logs`, { headers: H });
    if (!lg.ok) { console.log(`  (logy nedostupne: ${lg.status})`); continue; }
    const radky = (await lg.text()).split('\n');

    // hledej rozhodujici radky
    const vzory = /CHYBA|ERROR|Error|error|✗|✓|zkouším|odpovídá|Vybráno|nochange|no change|429|401|403|quota|exceeded|rate|limit|agent|aider|patch|FORGE_MODEL|FORGE_PROVIDER|forces|Applied edit|git diff|neplatn|neuspel|selhal|::error/;
    const zajimave = radky.filter((l) => vzory.test(l));
    console.log(`  [log ${radky.length} radku, filtrovano ${zajimave.length}]`);
    for (const l of zajimave.slice(-45)) console.log(`   | ${l.replace(/^\S*Z\s?/, '').trim().slice(0, 165)}`);
  }
}

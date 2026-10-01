// Zrusi zaseknute behy v hernim repu (stare tasky mimo soucasny DAG).
// Duvod: behy zustaly na GitHubu ve stavu in_progress a nikdy nedobehly.
// Drzi runner a conductor je vidi jako running.
//
// Pouziti:
//   node orchestra\tools\cancel-stale-runs.mjs            # dry-run (jen vypise)
//   node orchestra\tools\cancel-stale-runs.mjs --provest  # skutecne zrusi
//
// Co nedela: nesaha na behy se soucasnym DAG (task_id >= 107) ani na
// dokoncene behy. Seznam vzoru je v SOUCASNE níze.

import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));
const ORCH = join(HERE, '..');
const REPO = 'ssevcikm-spec/uo-shadows';

// Soucasny DAG ma tasky od tohoto cisla vys; vse nizsi je historie.
const SOUCASNE_OD = 107;

const provest = process.argv.includes('--provest');
const PAT = readFileSync(join(ORCH, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'orchestra-cancel' };

const r = await fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=50`, { headers: H });
const j = await r.json();
const aktivni = (j.workflow_runs || []).filter((x) => x.status !== 'completed');

console.log(`nedobehlych behu: ${aktivni.length}`);
const kZruseni = [];
for (const x of aktivni) {
  const m = /Forge #(\d+)/.exec(x.name || '');
  if (!m) {
    // NENI to beh agenta (napr. CI nebo Vydani hry) — ty se NIKDY nerusi.
    console.log(`  ${x.name.padEnd(46)} neni Forge beh -> nechat`);
    continue;
  }
  const taskId = Number(m[1]);
  const stary = taskId < SOUCASNE_OD;
  console.log(`  ${x.name.padEnd(46)} task=${taskId}  ${stary ? 'STARY -> zrusit' : 'soucasny -> nechat'}`);
  if (stary) kZruseni.push(x.id);
}

if (!kZruseni.length) { console.log('\nnic k zruseni'); process.exit(0); }
if (!provest) {
  console.log(`\nDRY-RUN: zrusil bych ${kZruseni.length} behu. Spust s --provest.`);
  process.exit(0);
}

for (const id of kZruseni) {
  const c = await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${id}/cancel`, {
    method: 'POST', headers: H,
  });
  console.log(`  cancel ${id} -> HTTP ${c.status}`);
}

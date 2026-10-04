import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Overi, ze nove behy (ulohy 115-118) obsahuji novy krok Kontrola parsovani.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const j = await gh(`/repos/${REPO}/actions/runs?per_page=25`);
const nove = (j.workflow_runs || []).filter((x) => /Forge #11[5-8]/.test(x.name || ''));
console.log(`behy novych uloh (115-118): ${nove.length}`);
for (const x of nove) console.log(`  ${x.created_at.slice(11, 19)}  ${String(x.conclusion ?? x.status).padEnd(12)} ${x.name}`);

const hotove = nove.filter((x) => x.conclusion);
console.log();
for (const x of hotove.slice(0, 2)) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) continue;
  console.log(`kroky jobu u ${x.name} (${x.conclusion}):`);
  for (const s of job.steps || []) {
    const znak = s.conclusion === 'success' ? 'ok' : s.conclusion === 'skipped' ? '--' : 'XX';
    console.log(`   ${znak} ${s.name}`);
  }
  // jestli probehla brana, vytahni jeji vystup
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (lg.ok) {
    const radky = (await lg.text()).split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, ''));
    const idx = radky.findIndex((l) => /Parsování v pořádku|Skript se neparsuje/.test(l));
    if (idx >= 0) {
      console.log('   --- vystup brany ---');
      for (const l of radky.slice(Math.max(0, idx - 3), idx + 10)) if (l.trim()) console.log(`   | ${l.trim().slice(0, 160)}`);
    }
  }
  console.log();
}

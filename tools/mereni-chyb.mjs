import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vytahne konkretni parse errory z poslednich behu (po nasazeni konvenci).
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'mereni' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const runs = await gh(`/repos/${REPO}/actions/runs?per_page=40`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #11[5-8]/.test(x.name || ''));
console.log(`behu novych granul: ${forge.length}\n`);

const chyby = new Map();
const soubory = new Map();
for (const x of forge.slice(0, 8)) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) continue;
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const t = (await lg.text()).replace(/\x1b\[[0-9;]*m/g, '');

  for (const m of t.matchAll(/SCRIPT ERROR: Parse Error: (.{0,120})/g)) {
    const c = m[1].trim();
    chyby.set(c, (chyby.get(c) || 0) + 1);
  }
  for (const m of t.matchAll(/Failed to load script "res:\/\/([^"]+)"/g)) {
    soubory.set(m[1], (soubory.get(m[1]) || 0) + 1);
  }
}

console.log('════ KONKRÉTNÍ PARSE ERRORY ════');
for (const [c, n] of [...chyby.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(2)}× ${c}`);
if (!chyby.size) console.log('  (žádné)');

console.log('\n════ SOUBORY, KTERÉ SE NEPARSUJÍ ════');
for (const [f, n] of [...soubory.entries()].sort((a, b) => b[1] - a[1])) console.log(`  ${String(n).padStart(2)}× ${f}`);
if (!soubory.size) console.log('  (žádné)');

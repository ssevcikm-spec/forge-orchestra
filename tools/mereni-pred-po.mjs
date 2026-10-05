import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Overi, zda behy PO nasazeni konvenci (commit e5f400f) maji jine chyby.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'mereni' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

// kdy byl nasazen commit s konvencemi
const c = await gh(`/repos/${REPO}/commits/e5f400f`);
const nasazeno = new Date(c.commit.committer.date);
console.log(`konvence nasazeny: ${nasazeno.toISOString()}\n`);

const runs = await gh(`/repos/${REPO}/actions/runs?per_page=40`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #/.test(x.name || ''));
const po = forge.filter((x) => new Date(x.created_at) > nasazeno);
const pred = forge.filter((x) => new Date(x.created_at) <= nasazeno);
console.log(`behu PO nasazeni: ${po.length}, PRED: ${pred.length}\n`);

async function rozbor(seznam, popis) {
  console.log(`════ ${popis} ════`);
  const chyby = new Map();
  let parseErr = 0, zkouseno = 0;
  for (const x of seznam.slice(0, 12)) {
    const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
    const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
    if (!job) continue;
    const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
    if (!lg.ok) continue;
    zkouseno++;
    const t = (await lg.text()).replace(/\x1b\[[0-9;]*m/g, '');
    const ma = /SCRIPT ERROR: Parse Error/.test(t);
    if (ma) parseErr++;
    for (const m of t.matchAll(/SCRIPT ERROR: Parse Error: (.{0,90})/g)) chyby.set(m[1].trim(), (chyby.get(m[1].trim()) || 0) + 1);
  }
  console.log(`  zkoumáno behu: ${zkouseno}, s parse errorem: ${parseErr}`);
  for (const [k, v] of [...chyby.entries()].sort((a, b) => b[1] - a[1])) console.log(`    ${String(v).padStart(2)}× ${k}`);
  if (!chyby.size) console.log('    (žádné parse errory)');
  console.log();
}

await rozbor(po, 'PO nasazení konvencí');
await rozbor(pred, 'PŘED nasazením');

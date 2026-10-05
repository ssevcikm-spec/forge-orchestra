import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Zmeri: ktery model/provider dostal jakou ulohu, jak dopadl a kolik spalil tokenu.
// Podklad pro rozhodnuti o paralelizaci a distribuci any/strong.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'mereni' };
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const runs = await gh(`/repos/${REPO}/actions/runs?per_page=60`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #/.test(x.name || ''));
console.log(`analyzuji ${forge.length} behu...\n`);

const data = [];
for (const x of forge.slice(0, 22)) {
  const jobs = await gh(`/repos/${REPO}/actions/runs/${x.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) continue;
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const t = await lg.text();
  const taskId = Number(/Forge #(\d+)/.exec(x.name)[1]);

  // vyskyty provideru/modelu (aider muze zkusit dva)
  const providery = [...t.matchAll(/FORGE_PROVIDER:\s*(\S+)/g)].map((m) => m[1]);
  const modely = [...t.matchAll(/FORGE_MODEL:\s*(\S+)/g)].map((m) => m[1]);
  const sent = [...t.matchAll(/Tokens:\s*([\d.]+)k sent/g)].map((m) => parseFloat(m[1]));
  const priznaky = {
    rateLimit: /RateLimitError|rate limit reached|exceeded your current quota|TPD\)/i.test(t),
    parseError: /SCRIPT ERROR: Parse Error/.test(t),
    nekonformni: /did not conform to the edit format/i.test(t),
    nochange: /Agent nezměnil žádný kód/.test(t),
    aplikoval: /Applied edit to/.test(t),
  };
  data.push({
    taskId,
    vysledek: x.conclusion ?? x.status,
    trvaniS: Math.round((new Date(x.updated_at) - new Date(x.created_at)) / 1000),
    provider: providery[0] ?? '?',
    provider2: providery[1] ?? '',
    model: modely[0] ?? '?',
    tokeny: sent,
    priznaky,
  });
}

console.log('════ BEH PO BEHU ════');
console.log('task   vysledek   pr.  model                    tok(k)  trvani  priznaky');
for (const d of data) {
  const pr = [d.provider, d.provider2].filter(Boolean).join('>');
  const p = Object.entries(d.priznaky).filter(([, v]) => v).map(([k]) => k).join(',');
  console.log(`#${String(d.taskId).padEnd(5)} ${String(d.vysledek).padEnd(10)} ${pr.padEnd(4)} ${d.model.padEnd(24)} ${String(d.tokeny.join('+') || '-').padEnd(7)} ${String(d.trvaniS + 's').padEnd(7)} ${p}`);
}

console.log('\n════ SOULRN PO POSKYTOVATELI ════');
const podleProv = {};
for (const d of data) {
  const p = d.provider;
  (podleProv[p] ||= { runs: 0, uspech: 0, tokeny: 0, rateLimit: 0, parseErr: 0, nekonf: 0, nochange: 0, aplikoval: 0 });
  const o = podleProv[p];
  o.runs++;
  if (d.vysledek === 'success') o.uspech++;
  o.tokeny += d.tokeny.reduce((a, b) => a + b, 0);
  if (d.priznaky.rateLimit) o.rateLimit++;
  if (d.priznaky.parseError) o.parseErr++;
  if (d.priznaky.nekonformni) o.nekonf++;
  if (d.priznaky.nochange) o.nochange++;
  if (d.priznaky.aplikoval) o.aplikoval++;
}
for (const [p, o] of Object.entries(podleProv).sort((a, b) => b[1].runs - a[1].runs)) {
  console.log(`  ${p.padEnd(11)} behu=${String(o.runs).padEnd(3)} uspech=${String(o.uspech).padEnd(3)} tokenu=${String(Math.round(o.tokeny)).padEnd(6)}`);
  console.log(`              rateLimit=${o.rateLimit}  parseError=${o.parseErr}  nekonformni=${o.nekonf}  nochange=${o.nochange}  aplikoval=${o.aplikoval}`);
}

console.log('\n════ CELKEM ════');
const celkemTok = data.reduce((a, d) => a + d.tokeny.reduce((x, y) => x + y, 0), 0);
const uspechy = data.filter((d) => d.vysledek === 'success').length;
console.log(`  behu: ${data.length}, uspechu: ${uspechy} (${Math.round(100 * uspechy / data.length)} %)`);
console.log(`  spáleno tokenů (jen "sent"): ${Math.round(celkemTok)}k`);
console.log(`  průměr na běh: ${Math.round(celkemTok / data.length)}k`);
console.log(`  rateLimit selhání: ${data.filter((d) => d.priznaky.rateLimit).length}`);
console.log(`  parse error: ${data.filter((d) => d.priznaky.parseError).length}`);
console.log(`  nekonformní formát: ${data.filter((d) => d.priznaky.nekonformni).length}`);
console.log(`  nochange: ${data.filter((d) => d.priznaky.nochange).length}`);
console.log(`  model aplikoval edit: ${data.filter((d) => d.priznaky.aplikoval).length}`);

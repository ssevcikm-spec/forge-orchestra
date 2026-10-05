import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Detail behu: co model delal, proc nezmenil nic, jake pokusy probehly.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const RUN = process.argv[2];

const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };
const jobs = await gh(`/repos/${REPO}/actions/runs/${RUN}/jobs`);
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const radky = (await lg.text()).split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, ''));

// najdi krok "Spusť agenta" a vypis jen jeho vystup (aider)
let i = radky.findIndex((l) => /##\[group\]Run .*spust_agenta|FORGE_PROMPT:/.test(l));
console.log(`=== vystup aideru (od radku ${i}) ===`);
let count = 0;
for (let k = i; k < radky.length && count < 70; k++) {
  const l = radky[k];
  if (/^\s*(shell:|env:|##\[endgroup\])/.test(l)) continue;
  if (/^\s{2}[A-Z_]+:/.test(l)) continue;
  if (!l.trim()) continue;
  if (/##\[group\]Run/.test(l) && count > 0) break;
  console.log(`${String(k).padStart(5)} | ${l.slice(0, 165)}`);
  count++;
}

console.log('\n=== klicove radky (model, tokeny, zmena) ===');
const vzory = /FORGE_MODEL:|FORGE_PROVIDER:|Tokens:|Applied edit|No changes|did not|Invalid|Error|error|Warning for|nochange|notice|změnil|cost|Cost:/i;
const videne = new Set();
for (const l of radky) {
  const c = l.trim();
  if (!vzory.test(c)) continue;
  if (videne.has(c) || c.length > 160) continue;
  videne.add(c);
  if (videne.size > 30) break;
  console.log(`  | ${c}`);
}

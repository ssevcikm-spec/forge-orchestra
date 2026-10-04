import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vypise konkretni usek logu behu podle regexu (od-do), bez filtrovani.
// Pouziti: node orchestra\tools\log-usek.mjs <runId> "<regexOd>" "<regexDo>" [maxRadku]
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const RUN = process.argv[2];
const OD = new RegExp(process.argv[3] || '.', 'i');
const DO = process.argv[4] ? new RegExp(process.argv[4], 'i') : null;
const MAX = Number(process.argv[5] || 120);

const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${RUN}/jobs`, { headers: H })).json();
const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
if (!job) { console.log('job Agent nenalezen'); process.exit(1); }
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
const radky = (await lg.text()).split('\n')
  .map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, '').replace(/^\s*\d{4}-\d{2}-\d{2}T\S+\s/, ''));

const i = radky.findIndex((l) => OD.test(l));
if (i < 0) { console.log(`(znacka ${OD} nenalezena; log ma ${radky.length} radku)`); process.exit(0); }
const j = DO ? radky.findIndex((l, k) => k > i && DO.test(l)) : -1;
const konec = j < 0 ? Math.min(radky.length, i + MAX) : j;
console.log(`--- radky ${i}..${konec} z ${radky.length} ---`);
for (let k = i; k < konec; k++) console.log(`${String(k).padStart(5)} | ${radky[k].slice(0, 170)}`);

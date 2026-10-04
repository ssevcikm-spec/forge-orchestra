// P18 — stáhne CELÝ log jobu z GitHubu (Node fetch; Python na redirectu padá
// na 401, PowerShell TLS nefunguje) a zapíše ho do `_analyza/p18-log-<id>.txt`.
//
// Použití:  node _analyza/p18-stahni-log.mjs <run_id>
import { readFileSync, writeFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'p18' };

const runId = process.argv[2];
if (!runId) { console.log('chybí run_id'); process.exit(2); }

const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${runId}/jobs`, { headers: H })).json();
const job = (jobs.jobs || []).find((j) => (j.name || '').startsWith('Agent'));
if (!job) { console.log('job Agent nenalezen'); process.exit(1); }

const r = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
console.log(`HTTP ${r.status}  content-encoding=${r.headers.get('content-encoding')}  content-type=${r.headers.get('content-type')}`);
const buf = Buffer.from(await r.arrayBuffer());
const out = `_analyza/p18-log-${runId}.txt`;
writeFileSync(out, buf);
console.log(`zapsáno: ${out}  (${buf.length} B)`);
console.log(`první 3 bajty: ${[...buf.slice(0, 3)].join(',')}`);

// Logy z /logs jsou někdy ZIP (PK\x03\x04) — pozná se to hned z prvních bajtů.
if (buf[0] === 0x50 && buf[1] === 0x4b) {
  console.log('POZOR: odpověď je ZIP archiv, ne text — je potřeba rozbalit.');
}

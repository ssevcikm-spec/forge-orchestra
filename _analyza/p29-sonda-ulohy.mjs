// P29 — SONDA: KTERÉ BĚHY PATŘÍ ÚLOHÁM #238–#243 A JAK SKONČILY? (jen čtení)
//
// PROČ VZNIKLA: `HANDOFF.md` §59.6 tvrdí „poslední 4 běhy agenta (#240–#243)
// skončily failure a ve všech čtyřech je `litellm.RateLimitError`". To se
// NEDÁ ověřit pořadím běhů — v názvu běhu je **ID ÚLOHY**, kdežto `run_number`
// je jiný čítač téhož jména (past „různé čítače nesou stejné jméno").
// Sonda proto čte běhy a páruje je podle **čísla úlohy v názvu**, ne podle
// pořadí, a u každého vypíše: conclusion, selhavší krok a počty výskytů
// `litellm.RateLimitError` a `agent nic nezměnil` v logu jobu.
//
// Použití: node _analyza/p29-sonda-ulohy.mjs [pocet_behu] [ulohy]
//   node _analyza/p29-sonda-ulohy.mjs 60 238,239,240,241,242,243
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json',
  'User-Agent': 'forge-p29', 'X-GitHub-Api-Version': '2022-11-28' };
const REPO = 'ssevcikm-spec/uo-shadows';
const N = Number(process.argv[2] || 60);
const CHCI = new Set(String(process.argv[3] || '238,239,240,241,242,243')
  .split(',').map((x) => x.trim()).filter(Boolean).map(Number));

const api = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return { status: r.status, body: await r.json().catch(() => null) };
};

const runs = await api(`/repos/${REPO}/actions/runs?per_page=${N}`);
if (runs.status !== 200) {
  console.log(JSON.stringify({ chyba: `cteni behu: HTTP ${runs.status}` }));
  process.exit(1);
}

const najdene = [];
for (const r of runs.body.workflow_runs) {
  const m = String(r.name || '').match(/Forge #(\d+)/);
  if (!m) continue;
  const uloha = Number(m[1]);
  if (!CHCI.has(uloha)) continue;
  najdene.push({ uloha, run_number: r.run_number, run_id: r.id, nazev: r.name,
    conclusion: r.conclusion, created_at: r.created_at,
    vetev: r.head_branch, event: r.event, pokus: r.run_attempt });
}

// Ke každému běhu: selhavší krok + počty klíčových vět v logu jobu.
for (const b of najdene) {
  const jobs = await api(`/repos/${REPO}/actions/runs/${b.run_id}/jobs`);
  const job = (jobs.body?.jobs || [])[0];
  b.job = job ? { nazev: job.name, conclusion: job.conclusion, id: job.id } : null;
  b.selhale_kroky = job ? (job.steps || []).filter((s) => s.conclusion === 'failure')
    .map((s) => s.name) : [];
  b.vsechny_kroky = job ? (job.steps || []).length : 0;
  if (!job) continue;
  const r = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  const raw = await r.text();
  const cisty = raw.replace(/\x1b\[[0-9;]*m/g, '');
  b.ratelimit = (cisty.match(/litellm\.RateLimitError/g) || []).length;
  b.tpm = (cisty.match(/Tokens per minute/g) || []).length;
  b.rtl = (cisty.match(/Request too large/g) || []).length;
  b.nezmenil = (cisty.match(/nic nezměnil|nezmenil zadny kod|nezmenil žádný kód/gi) || []).length;
  b.dvojprefix = (cisty.match(/openai\/openai\//g) || []).length;
  b.delka_logu = cisty.length;
}

console.log(JSON.stringify({
  repo: REPO, hledano_uloh: [...CHCI], nacteno_behu: runs.body.workflow_runs.length,
  nalezeno: najdene.length, behy: najdene,
}, null, 2));

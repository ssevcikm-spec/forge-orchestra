// Analyza posledniho behu kazdeho tasku: kdo odpovidal, kolik tokenu, zmenil neco,
// prosla brana na parsovani, ktere testy padly.
// Pouziti: node orchestra\tools\analyza-posledni.mjs [pocet_tasku]
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const KOLIK = Number(process.argv[2] || 6);

const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };

const runs = await gh(`/repos/${REPO}/actions/runs?per_page=100`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #\d+/.test(x.name || ''));
const podleTasku = new Map();
for (const x of forge) {
  const id = Number(/Forge #(\d+)/.exec(x.name)[1]);
  if (!podleTasku.has(id)) podleTasku.set(id, x);
}
const vybrane = [...podleTasku.entries()].sort((a, b) => b[0] - a[0]).slice(0, KOLIK);
console.log(`Tasku s behy: ${podleTasku.size}; analyzuji: ${vybrane.map(([id]) => '#' + id).join(', ')}\n`);

for (const [taskId, run] of vybrane) {
  console.log('='.repeat(78));
  console.log(`TASK #${taskId}  run=${run.id}  ${run.conclusion}  ${run.created_at}  (${run.html_url})`);
  console.log('='.repeat(78));
  const jobs = await gh(`/repos/${REPO}/actions/runs/${run.id}/jobs`);
  const job = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job) { console.log('  (job Agent nenalezen)\n'); continue; }
  console.log('  kroky: ' + (job.steps || []).map((s) => `${s.conclusion === 'success' ? 'ok' : s.conclusion === 'skipped' ? '--' : 'XX'} ${s.name}`).join(' | '));
  const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) { console.log(`  (logy nedostupne: ${lg.status})\n`); continue; }
  const radky = (await lg.text()).split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, '').trimEnd());

  const t = (re) => radky.filter((l) => re.test(l)).map((l) => l.trim());
  const uniq = (a, n = 12) => [...new Set(a)].slice(0, n);

  console.log('\n  --- vyber poskytovatele ---');
  for (const l of uniq(t(/zkou|Vybr|odpovíd|FORGE_PROVIDER|FORGE_MODEL|kvót|quota|429|401|403|přeskak|preskak|fail|Chyba|CHYBA/i), 18)) console.log(`    | ${l.slice(0, 160)}`);

  console.log('\n  --- aider (tokeny, editace) ---');
  for (const l of uniq(t(/Tokens:|Applied edit|No changes|did not conform|Invalid|Cost:|aider|Model:|repo map|Repo-map|repo-map|prompt tokens|Malformed|error/i), 22)) console.log(`    | ${l.slice(0, 160)}`);

  console.log('\n  --- brána na parsování ---');
  const gp = t(/Kontroluji parsování|Parse Error|check-only|\.gd$/i);
  for (const l of uniq(gp.filter((l) => !/^\s*$/.test(l)), 14)) console.log(`    | ${l.slice(0, 160)}`);

  console.log('\n  --- testy ---');
  for (const l of uniq(t(/\[test\]|SCRIPT ERROR|Parse Error|tvrdý limit|##\[error\]|status=/i), 16)) console.log(`    | ${l.slice(0, 160)}`);
  console.log();
}

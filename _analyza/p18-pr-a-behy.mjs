// P18 — ověří tři věci, které plánovací session nemá brát z handoffu:
//   1) existuje PR z běhů #142–#146? (handoff tvrdí: 0 z 31)
//   2) kolik běhů vzniklo PO 11:13 UTC (tj. nové pokusy #145/#146)?
//   3) `merged_by` u posledních PR — z DETAILU, ne ze seznamu (past z AGENTS.md)
//
// Použití: node _analyza/p18-pr-a-behy.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'p18' };
const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status };
};

console.log('════ A. OTEVŘENÉ PR ════');
const open = await gh(`/repos/${REPO}/pulls?state=open&per_page=100`);
console.log(`  otevřených PR: ${open.length}`);
for (const p of open) console.log(`   #${p.number} ${p.title}  created ${p.created_at}  head ${p.head.sha.slice(0, 9)}`);

console.log('\n════ B. POSLEDNÍ PR CELKEM (i sloučené/zavřené) ════');
const vsechny = await gh(`/repos/${REPO}/pulls?state=all&per_page=5&sort=created&direction=desc`);
for (const p of vsechny) {
  console.log(`  #${p.number} state=${p.state} merged_at=${p.merged_at} created=${p.created_at} head=${p.head.sha.slice(0, 9)}  ${p.title.slice(0, 50)}`);
}
// POZOR: v SEZNAMU je `merged_by` null i u sloučeného PR (naměřeno) → detail.
if (vsechny[0] && vsechny[0].merged_at) {
  const d = await gh(`/repos/${REPO}/pulls/${vsechny[0].number}`);
  console.log(`  (detail #${d.number}) merged_by = ${d.merged_by ? d.merged_by.login : 'null'}   ← z DETAILU, ne ze seznamu`);
}

console.log('\n════ C. BĚHY WORKFLOWU "Agent" — kdy vznikly ════');
const runs = await gh(`/repos/${REPO}/actions/runs?per_page=20`);
const ag = (runs.workflow_runs || []).filter((x) => /agent/i.test(x.name || ''));
console.log(`  běhů celkem v odpovědi: ${(runs.workflow_runs || []).length}, z toho "Agent": ${ag.length}`);
for (const r of ag.slice(0, 12)) {
  console.log(`   #${r.run_number} (id ${r.id}) ${r.status}/${r.conclusion || '-'}  head:${r.head_sha.slice(0, 9)}  created ${r.created_at}`);
}

console.log('\n════ D. NOVÉ BĚHY PO 11:13 UTC? ════');
const mez = '2026-10-02T11:13:07Z';
const nove = ag.filter((r) => r.created_at > mez);
console.log(`  běhů "Agent" po ${mez}: ${nove.length}`);
for (const r of nove) console.log(`   #${r.run_number} ${r.conclusion || r.status}  head:${r.head_sha.slice(0, 9)}  ${r.created_at}`);

console.log('\n════ E. STAV CONDUCTORA (fronta + TPM-relevantní úlohy) ════');
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const cond = async (p) => {
  const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  return r.ok ? r.json() : { chyba: r.status };
};
const q = await cond('/queue');
const fronta = Array.isArray(q) ? q : (q.tasks || []);
console.log(`  /queue: ${fronta.length} úloh`);
const failed = await cond('/failed');
console.log(`  /failed: ${JSON.stringify(failed).slice(0, 300)}`);

// P18b — jak se JMENUJÍ workflow běhy a kde jsou #142–#146?
//
// DŮVOD: `p18-pr-a-behy.mjs` filtroval podle `/agent/i.test(run.name)` a našel
// **0 z 20**. To je rozchod proti `h17-vsechny-behy.mjs`, který ty běhy čte
// přes ID. Rozdíl je v tom, co je v poli `name` — ověřuje se to tady.
//
// Použití: node _analyza/p18b-jmena-behu.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'p18b' };
const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status, telo: await r.text().catch(() => '') };
};

console.log('════ A. WORKFLOW DEFINICE V REPU ════');
const wf = await gh(`/repos/${REPO}/actions/workflows?per_page=50`);
for (const w of wf.workflows || []) console.log(`  id=${w.id}  name="${w.name}"  path=${w.path}  state=${w.state}`);
console.log(`  celkem workflow: ${(wf.workflows || []).length}`);

console.log('\n════ B. POSLEDNÍCH 20 BĚHŮ — jaká mají JMÉNA ════');
const runs = await gh(`/repos/${REPO}/actions/runs?per_page=20`);
console.log(`  total_count v odpovědi: ${runs.total_count}`);
for (const r of runs.workflow_runs || []) {
  console.log(`   #${String(r.run_number).padEnd(4)} name="${r.name}"  path=${r.path}  ${r.status}/${r.conclusion || '-'}  head:${r.head_sha.slice(0, 9)}  ${r.created_at}`);
}

console.log('\n════ C. KONKRÉTNÍ ID #142–#146 — existují ještě? ════');
const ID = [36999784822, 36999780638, 36999776851, 36999773646, 36999768712];
for (const id of ID) {
  const r = await gh(`/repos/${REPO}/actions/runs/${id}`);
  if (r.chyba) { console.log(`   id ${id}: CHYBA ${r.chyba}`); continue; }
  console.log(`   id ${id}: #${r.run_number} name="${r.name}" ${r.status}/${r.conclusion} head:${r.head_sha.slice(0, 9)} created ${r.created_at}`);
}

console.log('\n════ D. BĚHY NAD COMMITEM 194735d (HEAD herního repa) ════');
const nad = await gh(`/repos/${REPO}/actions/runs?head_sha=194735d9ba128490ef0b4d9cc139ed32fea4637d&per_page=30`);
console.log(`  total_count: ${nad.total_count}`);
for (const r of nad.workflow_runs || []) {
  console.log(`   #${r.run_number} name="${r.name}" ${r.status}/${r.conclusion || '-'} created ${r.created_at}`);
}

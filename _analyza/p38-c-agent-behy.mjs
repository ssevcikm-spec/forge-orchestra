// p38-c-agent-behy.mjs — běží dnes `agent.yml` ve hře? (P38, READ-ONLY GitHub API)
//
// PROČ: P37 naměřila H180 („čtyři příčiny P36 jsou SPÍCÍ, agent.yml neběžel od
// 9. 10. 19:42Z"). P38 musí ověřit, jestli se to po obnově tiku ZMĚNILO — tik
// totiž dispatchuje, takže by běhy mohly začít. Odpověď se nesmí převzít z P37.
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
// Použití: node _analyza/p38-c-agent-behy.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, '_analyza', 'p38-c-agent-behy-vystup.txt');
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();

const radky = [];
const p = (x = '') => { radky.push(x); console.log(x); };
const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-p38' },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status}`);
  return r.json();
};

p(`# p38-c — běhy agent.yml ve hře (${REPO}) — ${new Date().toISOString()}`);

const d = await api(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=5`);
p('');
p(`## POSLEDNÍCH ${d.workflow_runs.length} BĚHŮ agent.yml (total_count=${d.total_count})`);
for (const r of d.workflow_runs) {
  p(`  #${String(r.run_number).padStart(4)} | ${r.created_at} | ${String(r.conclusion ?? r.status).padEnd(9)} | ${r.display_title.slice(0, 50)} | head ${String(r.head_sha).slice(0, 8)}`);
}
const nejnovejsi = d.workflow_runs[0];
p('');
p(`## ČERSTVÉ BĚHY (vytvořené po 2026-10-09T20:00:00Z)`);
try {
  const f = await api(`/repos/${REPO}/actions/workflows/agent.yml/runs?created=%3E2026-10-09T20:00:00Z&per_page=100`);
  p(`   počet: ${f.total_count}`);
  for (const r of f.workflow_runs.slice(0, 20)) {
    p(`   #${r.run_number} ${r.created_at} ${r.conclusion}`);
  }
} catch (e) { p(`   CHYBA: ${String(e)}`); }

p('');
p(`SOUHRN: nejnovější běh #${nejnovejsi.run_number} z ${nejnovejsi.created_at} (${nejnovejsi.conclusion})`);
writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
console.log(`\n[zapsano] ${OUT}`);

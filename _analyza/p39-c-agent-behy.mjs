// p39-c-agent-behy.mjs — běží dnes `agent.yml` ve hře, a jaká je poslední stovka?
// (P39, READ-ONLY GitHub API)
//
// PROČ VLASTNÍ (H166 + omyl P39): `p38-c-agent-behy.mjs` zapisuje do P38ina
// dokladu. P39 potřebuje navíc HISTOGRAM poslední stovky běhů, protože na něm
// stojí ROZHODNUTÍ C (zvednout strop granulí 8/8, nebo ne).
//
// PAT se čte ze .secrets/github_pat.txt a NIKDY se nevypisuje.
// Použití: node _analyza/p39-c-agent-behy.mjs
import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const OUT = join(WS, '_analyza', 'p39-c-agent-behy-vystup.txt');
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();

const radky = [];
const p = (x = '') => { radky.push(x); console.log(x); };
const api = async (cesta) => {
  const r = await fetch(`https://api.github.com${cesta}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-p39' },
  });
  if (!r.ok) throw new Error(`${cesta} -> HTTP ${r.status}`);
  return r.json();
};

p(`# p39-c — běhy agent.yml ve hře (${REPO}) — ${new Date().toISOString()}`);

const d = await api(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=5`);
p('');
p(`## POSLEDNÍCH ${d.workflow_runs.length} BĚHŮ agent.yml (total_count=${d.total_count})`);
for (const r of d.workflow_runs) {
  p(`  #${String(r.run_number).padStart(4)} | ${r.created_at} | ${String(r.conclusion ?? r.status).padEnd(9)} | ${r.display_title.slice(0, 50)} | head ${String(r.head_sha).slice(0, 8)}`);
}
const nejnovejsi = d.workflow_runs[0];
p('');
p('## ČERSTVÉ BĚHY (vytvořené po 2026-10-09T20:00:00Z)');
try {
  const f = await api(`/repos/${REPO}/actions/workflows/agent.yml/runs?created=%3E2026-10-09T20:00:00Z&per_page=100`);
  p(`   počet: ${f.total_count}`);
  for (const r of f.workflow_runs.slice(0, 20)) {
    p(`   #${r.run_number} ${r.created_at} ${r.conclusion}`);
  }
} catch (e) { p(`   CHYBA: ${String(e)}`); }

// Poslední stovka běhů — histogram `conclusion` (to je číslo, o které se opírá
// ROZHODNUTÍ C: zvednout strop granulí znamená okamžitě spálit běhy).
p('');
p('## POSLEDNÍ STOVKA BĚHŮ agent.yml — histogram `conclusion`');
try {
  const s = await api(`/repos/${REPO}/actions/workflows/agent.yml/runs?per_page=100`);
  const hist = {};
  for (const r of s.workflow_runs) hist[r.conclusion ?? r.status] = (hist[r.conclusion ?? r.status] || 0) + 1;
  p(`   vzorek: ${s.workflow_runs.length} běhů (nejstarší v něm #${s.workflow_runs[s.workflow_runs.length - 1].run_number} z ${s.workflow_runs[s.workflow_runs.length - 1].created_at})`);
  for (const [k, v] of Object.entries(hist).sort((a, b) => b[1] - a[1])) p(`   ${String(v).padStart(4)}×  ${k}`);
  const uspech = s.workflow_runs.filter((r) => r.conclusion === 'success');
  if (uspech.length) p(`   poslední ÚSPĚCH: #${uspech[0].run_number} z ${uspech[0].created_at}`);
  else p('   poslední ÚSPĚCH: v té stovce ŽÁDNÝ');
} catch (e) { p(`   CHYBA: ${String(e)}`); }

p('');
p(`SOUHRN: nejnovější běh #${nejnovejsi.run_number} z ${nejnovejsi.created_at} (${nejnovejsi.conclusion})`);
writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
console.log(`\n[zapsano] ${OUT}`);

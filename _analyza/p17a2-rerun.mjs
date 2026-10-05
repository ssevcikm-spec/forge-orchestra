// P17/A2 — RESET běhů #117 a #78 na `44dd454` (Úkol A, krok 2)
//
// P17/A naměřila: Actions je `degraded_performance` (už ne `major_outage`),
// incident je ve stavu `investigating` s mitigací a výslovně říká
// „Queued jobs are clearing, new jobs are not delayed". To je důvod zkusit
// re-run: dokončit nasazení je smysl Úkolu A a bez běhu to nejde.
//
// Skript NEMĚNÍ kód a NEPUSHuje — jen spouští existující běhy znovu.
// Po spuštění se `runner_name` ověřuje ZVLÁŠŤ (až běh naběhne) — podle
// pravidla „Než začneš tvrdit, že to běží, ověř runner_name".

import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const REPO = 'ssevcikm-spec/uo-shadows';
const API = 'https://api.github.com';
const WS = dirname(dirname(fileURLToPath(import.meta.url)));
let PAT = '';
try {
  PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
} catch { /* bez PAT re-run neprojde */ }
const HLAVICKY = {
  accept: 'application/vnd.github+json',
  ...(PAT ? { authorization: `Bearer ${PAT}` } : {}),
};

console.log('='.repeat(78));
console.log('P17/A2 — re-run běhů na `44dd454`');
console.log(`běženo: ${new Date().toISOString()}`);
console.log('='.repeat(78));

// ── brzda: nespouštěj, dokud je Actions v major_outage ───────────────────
const comp = await fetch('https://www.githubstatus.com/api/v2/components.json')
  .then((r) => r.json()).catch(() => null);
const actions = comp?.components?.find((c) => c.name === 'Actions');
console.log(`Actions: ${actions?.status ?? '?'}`);
if (actions?.status === 'major_outage') {
  console.log('STOP: Actions je major_outage → běhy se NESPOUŠTĚJÍ (zadání, Úkol A1).');
  process.exit(0);
}

// ── najdi běhy na commitu ────────────────────────────────────────────────
const runs = await fetch(`${API}/repos/${REPO}/actions/runs?per_page=40`,
  { headers: HLAVICKY }).then((r) => r.json());
const naCommitu = (runs.workflow_runs ?? [])
  .filter((r) => r.head_sha === '44dd45446ed1ce4a418902eb4e81c50a8c2d5694');
console.log(`běhů na commitu: ${naCommitu.length}`);
const zaznam = [];
for (const r of naCommitu) {
  console.log(`  #${r.run_number} ${r.name}  ${r.status}/${r.conclusion} `
    + `attempt=${r.run_attempt}  id=${r.id}`);
  const res = await fetch(`${API}/repos/${REPO}/actions/runs/${r.id}/rerun`, {
    method: 'POST', headers: HLAVICKY,
  });
  let telo = null;
  try { telo = await res.json(); } catch { /* 201 bez těla */ }
  console.log(`      POST /rerun → HTTP ${res.status}`
    + `${telo?.message ? ` — ${telo.message}` : ''}`);
  zaznam.push({
    cislo: r.run_number, nazev: r.name, id: r.id,
    pred: `${r.status}/${r.conclusion}`, http: res.status,
    zprava: telo?.message ?? null,
  });
}

writeFileSync(join(WS, '_analyza', 'p17a2-rerun.json'),
  JSON.stringify({ kdy: new Date().toISOString(), actions: actions?.status ?? null,
    zaznam }, null, 2) + '\n', 'utf8');
console.log('\nzapsáno: _analyza/p17a2-rerun.json');
console.log('POZOR: stav běhů se ověřuje až za chvíli — `runner_name` je důkaz,'
  + ' ne „odeslal jsem požadavek".');

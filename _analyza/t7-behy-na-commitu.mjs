// Ověří, že na NOVÉM commitu herního repa běží workflow — a jak skončilo.
// POZOR: `head_sha` filtruje jen s PLNÝM 40znakovým sha (omyl 69); krátký
// vrátí `total_count: 0` a vypadá to jako „ještě nezačalo".
import { readFileSync } from 'node:fs';

const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync('orchestra/.secrets/github_pat.txt', 'utf8').trim();
const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, {
    headers: { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json' },
  });
  return r.json();
};

const sha = process.argv[2];
if (!sha || sha.length !== 40) {
  console.log('CHYBA: potreba PLNÝ 40znakovy sha (dostal jsem %s)', JSON.stringify(sha));
  process.exit(1);
}
const runs = await gh(`/repos/${REPO}/actions/runs?head_sha=${sha}&per_page=20`);
console.log('commit: %s', sha);
console.log('total_count: %d', runs.total_count);
for (const r of runs.workflow_runs ?? []) {
  // Pozor: Node `console.log` NEMÁ šířkové specifikátory jako Python
  // (`%-42s` vypíše doslova) — skládá se to ručně.
  const jmeno = String(r.name).padEnd(42).slice(0, 42);
  console.log(`  #${r.run_number}  ${jmeno}  ${r.status}/${r.conclusion ?? '-'}  head:${String(r.head_sha).slice(0, 9)}  ${r.created_at}`);
}
if (!runs.total_count) {
  console.log('  (zatim zadny beh — GitHub ma zpozdeni; zkus za chvili znovu)');
}

// Co dělal conductor PŘED a PO nasazení A1–A4 (deploy #31, 10:23 UTC).
//
// Otázka: mění se chování? Konkrétně
//   * zapisuje se `done` u nesloučeného PR? (A1)
//   * kolik pokusů mají nové granule? (rotace modelů = N3)
//   * které granule conductor vydal?
//
// Použití: node _analyza\po-deploy-stav.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'po-deploy' };
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const cond = async (p) => {
  const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  return r.ok ? r.json() : { chyba: r.status, telo: (await r.text()).slice(0, 120) };
};

console.log('════ A. ŽIVÝ CONDUCTOR ════');
console.log('  /health:', JSON.stringify(await cond('/health')));

console.log('\n════ B. /roadmap — stav granulí ════');
const rm = await cond('/roadmap');
const radky = rm.roadmap || [];
console.log(`  ${radky.length} řádků`);
for (const r of radky) {
  const id = String(r.item_id || '').replace('uo-shadows/', '');
  console.log(`    ${id.padEnd(22)} ${String(r.status || '?').padEnd(9)} task=${r.task ?? '-'} attempts=${r.attempts ?? '-'}`);
}

console.log('\n════ C. POSLEDNÍ BĚHY AGENTA VE HŘE (GitHub Actions) ════');
const behy = await (await fetch(
  'https://api.github.com/repos/ssevcikm-spec/uo-shadows/actions/runs?per_page=20', { headers: H })).json();
const forge = (behy.workflow_runs || []).filter((x) => /Forge/i.test(x.name || ''));
for (const r of forge.slice(0, 10)) {
  console.log(`  #${r.run_number} ${String(r.name).slice(0, 42).padEnd(44)} ${r.conclusion || r.status}  head:${r.head_sha.slice(0, 7)}  ${r.created_at}`);
}
console.log(`  (celkem Forge běhů v posledních 20: ${forge.length})`);

console.log('\n════ D. CO CONDUCTOR ZAPSAL DO D1 (endpointy) ════');
for (const p of ['/tasks', '/failed', '/status']) {
  const v = await cond(p);
  const souhrn = Array.isArray(v) ? `pole (${v.length})` : JSON.stringify(v).slice(0, 300);
  console.log(`  ${p.padEnd(10)} → ${souhrn}`);
}

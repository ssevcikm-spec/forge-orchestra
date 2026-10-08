// P27 — DOKLAD: nasazení conductora a stav živé služby (tři kroky ověření).
//
// PROČ: „HTTP 200 není důkaz“ (AGENTS.md). Nasazení se ověřuje takto:
//   1) push dorazil        -> `git ls-remote` (dělá PowerShell, ne tenhle skript)
//   2) build běžel na SPRÁVNÉM commitu -> Actions API (deploy.yml + head_sha)
//   3) služba odpovídá a chová se podle nové konfigurace -> /health, /roadmap, /queue
//
// Použití: node _analyza/p27-over-nasazeni.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-p27', 'X-GitHub-Api-Version': '2022-11-28' };

const env = {};
// ⚠ Node nezná `utf8-sig` (to je Python) — `.env` MÁ BOM, takže se ořezává ručně:
// klíč by jinak vyšel jako "\uFEFFFORGE_URL" a hledání by tiše selhalo (nález P27-H).
const envText = readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '');
for (const l of envText.split(/\r?\n/)) {
  if (l.includes('=') && !l.trim().startsWith('#')) {
    const i = l.indexOf('=');
    env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
}
const URL = (env.FORGE_URL || '').replace(/\/$/, '');
const TAJ = env.FORGE_SECRET;

const api = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return { status: r.status, body: await r.json().catch(() => null) };
};

console.log('='.repeat(78));
console.log('(2) BĚŽEL BUILD NA SPRÁVNÉM COMMITU? (Actions: deploy.yml)');
console.log('='.repeat(78));
const runs = await api('/repos/ssevcikm-spec/forge-orchestra/actions/workflows/deploy.yml/runs?per_page=5');
if (runs.status !== 200) {
  console.log(`  CHYBA čtení běhů: ${runs.status}`);
} else {
  for (const r of runs.body.workflow_runs) {
    console.log(`  ${r.head_sha.slice(0, 8)}  ${String(r.status).padEnd(11)} ${String(r.conclusion).padEnd(9)} ${r.created_at}  ${r.event}  #${r.run_number}`);
  }
}

const volej = async (cesta, secret = true) => {
  const h = { 'User-Agent': 'Mozilla/5.0 (forge-p27)' };
  if (secret) h['x-forge-secret'] = TAJ;
  const r = await fetch(URL + cesta, { headers: h });
  const t = await r.text();
  let b = null;
  try { b = JSON.parse(t); } catch { /* nech null */ }
  return { status: r.status, body: b };
};

console.log();
console.log('='.repeat(78));
console.log('(3) CHOVÁ SE ŽIVÁ SLUŽBA PODLE NOVÉ KONFIGURACE?');
console.log('='.repeat(78));
const zd = await volej('/health', false);
console.log(`  /health            -> ${zd.status}  ok=${zd.body?.ok} ready=${zd.body?.ready} running=${zd.body?.running} games=${zd.body?.games} cile=${zd.body?.targets?.length}`);
const rm = await volej('/roadmap');
const rows = rm.body?.roadmap || [];
const podle = {};
for (const r of rows) podle[r.status] = (podle[r.status] || 0) + 1;
console.log(`  /roadmap           -> ${rm.status}  granul=${rows.length}  stavy=${JSON.stringify(podle)}`);
const blokovane = rows.filter((r) => r.status === 'blocked');
for (const r of blokovane.slice(0, 10)) {
  console.log(`      BLOCKED ${r.item_id}  task=${r.task_id}  task_stav=${r.task_status}  pokusu=${r.attempts}`);
}
console.log(`  blokovaných granul: ${blokovane.length} (strop 8: blokovat se smí jen granule s >= 8 běhy)`);
const q = await volej('/queue');
const tasks = q.body?.tasks || [];
const tpodle = {};
for (const t of tasks) tpodle[t.status] = (tpodle[t.status] || 0) + 1;
console.log(`  /queue             -> ${q.status}  uloh=${tasks.length}  stavy=${JSON.stringify(tpodle)}`);
console.log();
console.log('Poznámka: ŽE strop opravdu zastaví granuli na 8 bězích, se na živé službě');
console.log('projeví, až taková granule vznikne (stejná mez acceptance jako u B3/B4).');

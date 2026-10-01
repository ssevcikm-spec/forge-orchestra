#!/usr/bin/env node
// Stav orchestra na jednom miste: conductor, registr her, fronta, modely, behy.
//
// Pouziti:
//   node orchestra\tools\status.mjs              # vse
//   node orchestra\tools\status.mjs --bez-behu   # preskoci GitHub behy (rychlejsi)
//
// Proc Node a ne PowerShell/curl: na teto stanici PowerShell i curl na HTTPS ven
// selzou (schannel: SEC_E_NO_CREDENTIALS). Node fetch funguje.
// Secret se cte z orchestra\.env, PAT z orchestra\.secrets\github_pat.txt.

import { readFileSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const HERE = dirname(fileURLToPath(import.meta.url));   // orchestra\tools
const ORCH = join(HERE, '..');                          // orchestra
const HERNA_REPO = 'ssevcikm-spec/uo-shadows';          // default; jinak viz /games

const bezBehu = process.argv.includes('--bez-behu');

// ---- nacti orchestra\.env ----
const envFile = join(ORCH, '.env');
const env = {};
if (existsSync(envFile)) {
  for (const line of readFileSync(envFile, 'utf8').split('\n')) {
    const t = line.trim();
    if (!t || t.startsWith('#')) continue;
    const i = t.indexOf('=');
    if (i > 0) env[t.slice(0, i).trim()] = t.slice(i + 1).trim();
  }
}
if (!env.FORGE_URL) {
  console.error('Chybi FORGE_URL v orchestra\\.env');
  process.exit(2);
}

const call = async (path, init = {}) => {
  const r = await fetch(`${env.FORGE_URL}${path}`, {
    ...init,
    headers: { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json', ...(init.headers || {}) },
  });
  const text = await r.text();
  try { return { status: r.status, json: JSON.parse(text) }; }
  catch { return { status: r.status, text }; }
};

const linka = (t) => console.log(`\n=== ${t} ===`);

// ---- 1. conductor ----
linka('CONDUCTOR /health');
const h = await call('/health');
if (h.json) {
  console.log(`  ok=${h.json.ok}  ready=${h.json.ready}  running=${h.json.running}  games=${h.json.games}`);
  for (const w of h.json.workers || []) {
    const stav = w.minutes_ago <= 5 ? 'AKTIVNI' : `off (${Math.round(w.minutes_ago / 60)} h)`;
    console.log(`  uzel ${w.name.padEnd(18)} ${stav}   [${w.kinds}]`);
  }
} else {
  console.log(`  HTTP ${h.status} ${String(h.text).slice(0, 200)}`);
}

// ---- 2. registr her ----
linka('REGISTR HER /games');
const g = await call('/games');
if (g.json?.games) {
  for (const x of g.json.games) {
    console.log(`  ${x.active ? 'AKTIVNI ' : 'vypnuta '} ${String(x.game_id).padEnd(18)} ${x.repo}`);
  }
  if (!g.json.games.some((x) => x.active)) {
    console.log('  POZOR: zadna hra neni aktivni -> orchestra nepracuje na nicem.');
  }
} else {
  console.log(`  HTTP ${g.status} ${String(g.text).slice(0, 200)}`);
}

// ---- 3. roadmapa ----
linka('ROADMAP /roadmap');
const rm = await call('/roadmap');
if (rm.json) {
  const items = Array.isArray(rm.json) ? rm.json : (rm.json.items || rm.json.grains || []);
  const podleHry = {};
  for (const it of items) {
    const hra = it.game_id || (it.item_id || '').split('/')[0] || '?';
    (podleHry[hra] ||= []).push(it);
  }
  for (const [hra, arr] of Object.entries(podleHry)) {
    const stavy = {};
    for (const it of arr) stavy[it.status || '?'] = (stavy[it.status || '?'] || 0) + 1;
    console.log(`  ${hra}: ${arr.length} granulí -> ${JSON.stringify(stavy)}`);
  }
  if (!items.length) console.log('  (prazdna)');
} else {
  console.log(`  HTTP ${rm.status} ${String(rm.text).slice(0, 200)}`);
}

// ---- 4. selhana fronta ----
linka('SELHANE /failed');
const f = await call('/failed');
const selhane = f.json?.tasks || [];
if (!selhane.length) console.log('  (zadne)');
for (const t of selhane.slice(0, 8)) {
  console.log(`  #${String(t.id).padEnd(4)} pokusu=${String(t.attempts ?? '?').padEnd(3)} ${String(t.title).slice(0, 60)}`);
}
if (selhane.length > 8) console.log(`  ... a dalsich ${selhane.length - 8}`);

// ---- 5. modely (lokalni kopie retezce) ----
linka('MODELOVY RETEZEC (lokalni sablona orchestra)');
try {
  const p = JSON.parse(readFileSync(join(ORCH, 'repo', '.forge', 'providers.json'), 'utf8'));
  for (const pr of p.providers) {
    const sil = pr.strongModels?.length ? ` strong=[${pr.strongModels.join(', ')}]` : '';
    console.log(`  ${pr.name.padEnd(11)} ${pr.models.join(', ')}${sil}`);
  }
} catch (e) {
  console.log(`  nelze precist: ${e.message}`);
}

// ---- 6. GitHub behy (volitelne) ----
if (!bezBehu) {
  const patFile = join(ORCH, '.secrets', 'github_pat.txt');
  if (existsSync(patFile)) {
    const PAT = readFileSync(patFile, 'utf8').trim();
    const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'orchestra-status' };
    linka(`BEHY ${HERNA_REPO}`);
    try {
      const r = await fetch(`https://api.github.com/repos/${HERNA_REPO}/actions/runs?per_page=6`, { headers: H });
      const j = await r.json();
      for (const x of j.workflow_runs || []) {
        const stav = String(x.conclusion ?? x.status).padEnd(12);
        console.log(`  ${x.created_at.slice(0, 19).replace('T', ' ')}  ${stav} ${x.name}`);
      }
    } catch (e) {
      console.log(`  chyba: ${e.message}`);
    }
    linka(`DEPLOY CONDUCTORA (${'ssevcikm-spec/forge-orchestra'})`);
    try {
      const r = await fetch('https://api.github.com/repos/ssevcikm-spec/forge-orchestra/actions/runs?per_page=3', { headers: H });
      const j = await r.json();
      for (const x of j.workflow_runs || []) {
        console.log(`  ${x.created_at.slice(0, 19).replace('T', ' ')}  ${String(x.conclusion ?? x.status).padEnd(12)} ${x.name}`);
      }
    } catch (e) {
      console.log(`  chyba: ${e.message}`);
    }
  }
}

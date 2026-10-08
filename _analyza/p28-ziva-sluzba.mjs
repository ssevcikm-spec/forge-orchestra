// P28 — ČTENÍ ŽIVÉ SLUŽBY (jen GET; `/tick` a `/poll` se NEVOLAJÍ — mění stav).
//
// PROČ SAMOSTATNĚ: měřidlo P28 nesmí přebírat tvrzení z měřidla P27, takže si
// živou službu čte vlastním skriptem a vypisuje STROJOVĚ ČITELNÝ JSON, který
// parsuje `p28-a-overeni.py`. Tři věci, které se tu měří:
//   1) `/health` BEZ tajemství (je veřejný kvůli monitoringu) — tvary ok/ready/
//      running/games + stav cíle (`targets`);
//   2) ŠEST chráněných endpointů: bez tajemství `401`, s tajemstvím `200`;
//   3) `/roadmap` a `/queue` — počty a stavy (podklad pro tvrzení o stropech).
//
// ⚠ `.env` MÁ BOM (nález P27-H) — Node `utf8-sig` nezná, takže se BOM ořezává
// ručně; bez toho klíč vyjde jako "\uFEFFFORGE_URL" a hledání TICHE selže.
//
// Použití: node _analyza/p28-ziva-sluzba.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));

function nactiEnv() {
  const env = {};
  let text;
  try {
    text = readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '');
  } catch (e) {
    return { env, chyba: String(e).slice(0, 200) };
  }
  for (const l of text.split(/\r?\n/)) {
    if (l.includes('=') && !l.trim().startsWith('#')) {
      const i = l.indexOf('=');
      env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
    }
  }
  return { env };
}

const { env, chyba } = nactiEnv();
const URL = String(env.FORGE_URL || '').replace(/\/$/, '');
const TAJ = env.FORGE_SECRET;
const vystup = { url: URL, ma_url: Boolean(URL), ma_tajemstvi: Boolean(TAJ), chyba_env: chyba || null };

async function volej(cesta, { secret = false } = {}) {
  const h = { 'User-Agent': 'forge-p28' };
  if (secret) h['x-forge-secret'] = TAJ;
  try {
    const r = await fetch(URL + cesta, { headers: h });
    const t = await r.text();
    let b = null;
    try { b = JSON.parse(t); } catch { /* nech null */ }
    return { status: r.status, body: b };
  } catch (e) {
    return { status: 0, body: null, chyba: String(e).slice(0, 200) };
  }
}

// 1) /health veřejně
const zd = await volej('/health');
vystup.health = {
  status: zd.status,
  ok: zd.body?.ok ?? null,
  ready: zd.body?.ready ?? null,
  running: zd.body?.running ?? null,
  games: zd.body?.games ?? null,
  cilu: Array.isArray(zd.body?.targets) ? zd.body.targets.length : null,
  cile_mereny: Array.isArray(zd.body?.targets)
    ? zd.body.targets.map((t) => ({ game_id: t?.game_id ?? null, ma_forge: Boolean(t?.forge),
        main_ci: t?.main_ci?.conclusion ?? null, error: t?.error ?? null }))
    : null,
};

// 2) šest chráněných endpointů: bez tajemství vs s tajemstvím
const CHRANENE = ['/queue', '/status', '/workers', '/games', '/failed', '/roadmap'];
vystup.chranene = {};
for (const c of CHRANENE) {
  const bez = await volej(c);
  const s = await volej(c, { secret: true });
  vystup.chranene[c] = { bez: bez.status, s: s.status };
}

// 3) /roadmap a /queue — počty a stavy
const rm = await volej('/roadmap', { secret: true });
const rows = rm.body?.roadmap || [];
const podle = {};
for (const r of rows) podle[r.status] = (podle[r.status] || 0) + 1;
vystup.roadmap = { status: rm.status, granul: rows.length, stavy: podle,
  blokovane: rows.filter((r) => r.status === 'blocked').length,
  max_pokusu: rows.reduce((m, r) => Math.max(m, Number(r.attempts) || 0), 0) };

const q = await volej('/queue', { secret: true });
const tasks = q.body?.tasks || [];
const tpodle = {};
for (const t of tasks) tpodle[t.status] = (tpodle[t.status] || 0) + 1;
vystup.queue = { status: q.status, uloh: tasks.length, stavy: tpodle };

console.log(JSON.stringify(vystup, null, 2));

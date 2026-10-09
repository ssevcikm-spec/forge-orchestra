// P29 — ŘÁDKY ŽIVÉ SLUŽBY (`/roadmap`, `/queue`) jako JSON. JEN ČTENÍ.
//
// PROČ SAMOSTATNĚ: měřidlo P29 potřebuje pro výpočet osiřelých řádků CELÉ řádky
// (item_id, status, task_id, attempts), kdežto `p28-ziva-sluzba.mjs` vrací jen
// počty. Čte se STEJNOU cestou jako on (Node `fetch`, protože TLS z PowerShellu
// na téhle stanici nefunguje) a nic se nezapisuje.
//
// Použití: node _analyza/p29-sluzba-rows.mjs
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));

function nactiEnv() {
  const env = {};
  for (const l of readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/)) {
    if (l.includes('=') && !l.trim().startsWith('#')) {
      const i = l.indexOf('=');
      env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
    }
  }
  return env;
}

const env = nactiEnv();
const URL = String(env.FORGE_URL || '').replace(/\/$/, '');
const volej = async (cesta) => {
  try {
    const r = await fetch(URL + cesta, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
    const b = await r.json().catch(() => null);
    return { status: r.status, body: b };
  } catch (e) {
    return { status: 0, body: null, chyba: String(e).slice(0, 200) };
  }
};

const rm = await volej('/roadmap');
const q = await volej('/queue');
const st = await volej('/status');
const h = await volej('/health');
const vystup = {
  url: URL,
  chyba: rm.body ? null : (rm.chyba || `HTTP ${rm.status}`),
  roadmap: rm.body?.roadmap ?? [],
  queue: q.body?.tasks ?? [],
  status: st.body ?? null,
  health: h.body ?? null,
  stavy: { roadmap_status: rm.status, queue_status: q.status, status_status: st.status,
    health_status: h.status },
};
console.log(JSON.stringify(vystup, null, 1));
// Volitelný zápis do souboru (UTF-8 bez BOM) — doklad pro měřidlo P29.
// ⚠ PowerShell `>` a `Out-File -Encoding utf8` píšou BOM (a `>` rovnou UTF-16LE),
// takže se doklad zapisuje TADY, ne shellem.
if (process.argv[2]) {
  const { writeFileSync } = await import('node:fs');
  writeFileSync(process.argv[2], JSON.stringify(vystup, null, 1) + '\n', 'utf8');
}

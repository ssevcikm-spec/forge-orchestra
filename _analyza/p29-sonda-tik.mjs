// P29 — SONDA ŽIVÉ SLUŽBY: osiřelé řádky (dry-run) a RUČNÍ TIK. Čte a (na vyžádání) tiká.
//
// PROČ: `/health` hlásí `ready=5 running=0`, ale poslední běh v `/status` je z
// 21:12 UTC — tedy ~2 h bez dispatche. Zadání P29 chce vadu UKÁZAT NA ODPOVĚDI
// ŽIVÉ SLUŽBY, ne ji odvodit z kódu. Dvě volání:
//   1) `POST /tasks/cleanup {dry_run:true}` — JEN ČTE (nic nemění) a řekne, kolik
//      je v cache osiřelých řádků a kolik úloh na ně visí;
//   2) `POST /tick` — RUČNÍ TIK. Ten NENÍ čtení: dispatchuje, co je připravené.
//      Proto se pouští jen s `--tik` a jeho následek se zapíše do záznamu.
//
// Použití:
//   node _analyza/p29-sonda-tik.mjs            # jen dry-run (nic se nemění)
//   node _analyza/p29-sonda-tik.mjs --tik      # navíc ruční tik
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const env = {};
for (const l of readFileSync(join(WS, '.env'), 'utf8').replace(/^\uFEFF/, '').split(/\r?\n/)) {
  if (l.includes('=') && !l.trim().startsWith('#')) {
    const i = l.indexOf('=');
    env[l.slice(0, i).trim()] = l.slice(i + 1).trim();
  }
}
const URL = String(env.FORGE_URL || '').replace(/\/$/, '');
const H = { 'x-forge-secret': env.FORGE_SECRET, 'content-type': 'application/json' };

const volej = async (cesta, telo) => {
  try {
    const r = await fetch(URL + cesta, {
      method: 'POST', headers: H, body: JSON.stringify(telo ?? {}),
    });
    const t = await r.text();
    let b = null;
    try { b = JSON.parse(t); } catch { b = t.slice(0, 400); }
    return { status: r.status, body: b };
  } catch (e) {
    return { status: 0, chyba: String(e).slice(0, 200) };
  }
};

const cas = new Date().toISOString();
const suche = await volej('/tasks/cleanup', { dry_run: true });
console.log(JSON.stringify({ cas, krok: 'cleanup dry_run (JEN CTE)', ...suche }, null, 1));

if (process.argv.includes('--tik')) {
  const tik = await volej('/tick', {});
  console.log(JSON.stringify({ cas: new Date().toISOString(), krok: 'R UCNI TIK (meni stav)',
    ...tik }, null, 1));
} else {
  console.log(JSON.stringify({ krok: 'tik', provedeno: false,
    poznamka: 'ruční tik se pouští jen s --tik (dispatchuje práci)' }, null, 1));
}

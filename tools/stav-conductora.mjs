import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Rychly pohled na conductor: health, roadmap (fronta), failed.
import { readFileSync } from 'node:fs';

const env = readFileSync(join(PARENT, '.env'), 'utf8').replace(/^\uFEFF/, '');
// POZOR 2: soubor začíná UTF-8 BOM (ef bb bf) – bez jeho odstranění první
// řádek nikdy nezačíná na 'FORGE_URL=' a URL zůstane prázdná.
const get = (k) => {
  // POZOR: .env má CRLF, takže se musí řádky nejdřív rozdělit – regex s '$'
  // na konci řádku v JS nepočítá s '\r' (jednou mě to vrátilo jen '/health').
  for (const radek of env.split(/\r?\n/)) {
    if (radek.startsWith(k + '=')) return radek.slice(k.length + 1).trim().replace(/^["']|["']$/g, '');
  }
  return '';
};
const URL = get('FORGE_URL');
const SEC = get('FORGE_SECRET');
const H = { 'x-forge-secret': SEC };

const call = async (p) => {
  const r = await fetch(URL + p, { headers: H });
  const t = await r.text();
  return { p, status: r.status, text: t };
};

const ukaz = (o) => {
  console.log(`--- ${o.p} -> ${o.status} ---`);
  let d;
  try { d = JSON.parse(o.text); } catch { console.log(o.text.slice(0, 400)); return; }
  console.log(JSON.stringify(d, null, 1).slice(0, 1500));
};

ukaz(await call('/health'));
ukaz(await call('/roadmap'));
ukaz(await call('/failed'));

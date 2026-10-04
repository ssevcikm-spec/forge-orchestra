import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vypise frontu ukolu z conductora: stav, pokusy, casy a granuli.
import { readFileSync } from 'node:fs';

const env = readFileSync(join(PARENT, '.env'), 'utf8').replace(/^\uFEFF/, '');
const get = (k) => {
  for (const r of env.split(/\r?\n/)) if (r.startsWith(k + '=')) return r.slice(k.length + 1).trim();
  return '';
};
const URL = get('FORGE_URL');
const SEC = get('FORGE_SECRET');
const H = { 'x-forge-secret': SEC };

const r = await fetch(`${URL}/queue`, { headers: H });
console.log('HTTP', r.status);
const d = await r.json();
const ukoly = d.queue || d.tasks || d.ukoly || d;
const seznam = Array.isArray(ukoly) ? ukoly : (ukoly.tasks || []);
console.log('ukolu:', seznam.length);
for (const t of seznam.slice(0, 14)) {
  const p = typeof t.payload === 'object' ? t.payload : {};
  console.log(
    '#' + String(t.id).padEnd(4),
    String(t.status).padEnd(9),
    'pokusu=' + String(t.attempts).padEnd(3),
    'grain=' + String(p.grain || '-').padEnd(16),
    'upd=' + String(t.updated_at || '-'),
  );
}

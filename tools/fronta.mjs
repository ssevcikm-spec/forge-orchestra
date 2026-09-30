// Vypise frontu ukolu z conductora: stav, pokusy, casy a granuli.
import { readFileSync } from 'node:fs';

const env = readFileSync('C:/Users/Ssevc/Local-Deepseek/orchestra/.env', 'utf8').replace(/^\uFEFF/, '');
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

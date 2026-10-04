import { fileURLToPath } from 'node:url';
import { dirname } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vypise tasky z conductoru vcetne payloadu (repo, grain, model).
import { readFileSync } from 'node:fs';

const env = Object.fromEntries(
  readFileSync(join(PARENT, '.env'), 'utf8')
    .split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const c = async (p) => (await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();

for (const [nazev, path] of [['QUEUE', '/queue'], ['FAILED', '/failed']]) {
  const j = await c(path);
  const tasks = j.tasks || [];
  console.log(`\n=== ${nazev} (${tasks.length}) ===`);
  for (const t of tasks.slice(0, 10)) {
    let p = t.payload;
    if (typeof p === 'string') { try { p = JSON.parse(p); } catch { p = {}; } }
    p = p || {};
    console.log(`  #${String(t.id).padEnd(5)} ${String(t.status).padEnd(9)} attempts=${String(t.attempts ?? '?').padEnd(3)} grain=${String(p.grain || '?').padEnd(20)} model=${String(p.model || '-').padEnd(7)} repo=${p.repo || '?'}`);
  }
}

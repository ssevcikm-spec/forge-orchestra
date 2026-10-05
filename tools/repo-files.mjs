import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Vypise vsechny markdown soubory v repu orchestra (co prezilo smazani gameforge).
import { readFileSync } from 'node:fs';

const PAT = readFileSync(join(PARENT, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'forge-check' };

const r = await fetch('https://api.github.com/repos/ssevcikm-spec/forge-orchestra/git/trees/main?recursive=1', { headers: H });
const t = await r.json();
if (!t.tree) { console.log('CHYBA:', JSON.stringify(t).slice(0, 300)); process.exit(1); }

const md = t.tree.filter((x) => x.type === 'blob' && x.path.endsWith('.md'));
console.log(`markdown souboru v repu orchestra: ${md.length}`);
for (const f of md) console.log(`  ${String(f.size).padStart(7)} B  ${f.path}`);

console.log('\nvsechny soubory v repu (mimo conductor/node_modules):');
for (const f of t.tree.filter((x) => x.type === 'blob' && !x.path.includes('node_modules'))) {
  console.log(`  ${String(f.size).padStart(8)} B  ${f.path}`);
}

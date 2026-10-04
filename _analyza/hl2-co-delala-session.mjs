// Co dělala jiná session — přečte její log a vypíše, které soubory zapsala.
// Spuštění: node _analyza\hl2-co-delala-session.mjs <session-id>
// Nedělá nic destruktivního, jen čte.
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';

const ROOT = 'C:/Users/Ssevc/.dsh/sessions/--C-Users-Ssevc-Local-Deepseek--';
const hledany = process.argv[2];
if (!hledany) { console.error('pouzij: node hl2-co-delala-session.mjs <session-id>'); process.exit(1); }

const dirs = readdirSync(ROOT).filter((d) => d.includes(hledany));
if (!dirs.length) { console.error('session nenalezena'); process.exit(1); }

for (const d of dirs) {
  const dir = join(ROOT, d);
  console.log(`# session ${d}\n`);
  for (const f of readdirSync(dir)) {
    const p = join(dir, f);
    const st = statSync(p);
    if (st.isDirectory()) { console.log(`  [dir] ${f}`); continue; }
    if (!f.endsWith('.jsonl') && !f.endsWith('.json')) { console.log(`  [jin] ${f} ${st.size} B`); continue; }
    console.log(`  ${f}  ${st.size} B`);
    if (st.size > 40_000_000) { console.log('    (prilis velke, preskakuji)'); continue; }
    const radky = readFileSync(p, 'utf8').split(/\r?\n/).filter(Boolean);
    console.log(`    radku: ${radky.length}`);
    // Hledej zapisy souboru a prikazy
    const zapisy = new Set();
    const prikazy = [];
    for (const l of radky) {
      let o; try { o = JSON.parse(l); } catch { continue; }
      const s = JSON.stringify(o);
      for (const m of s.matchAll(/"(?:file_path|path)":"([^"]+)"/g)) {
        if (/tool|write|edit/i.test(s)) zapisy.add(m[1]);
      }
      for (const m of s.matchAll(/"(?:command)":"((?:[^"\\]|\\.){0,300})"/g)) prikazy.push(m[1]);
    }
    if (zapisy.size) { console.log('    ZMINENE CESTY:'); for (const z of [...zapisy].sort()) console.log('      ' + z); }
    if (prikazy.length) {
      console.log('    PRIKAZY (poslednich 15):');
      for (const c of prikazy.slice(-15)) console.log('      ' + c.replace(/\\n/g, ' ').slice(0, 160));
    }
  }
}

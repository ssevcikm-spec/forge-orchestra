// H17 — čím TAJLE session skutečně běží (model, reasoningEffort, okno).
//
// PROČ: `dsh-usage` měří cenu, ale `reasoningEffort` se do jeho reportu
// nedostane. Odpověď na „ušetří nižší effort?" potřebuje nejdřív vědět,
// NA ČEM se jede — a to je v `request/header` session logu.
//
// POZOR: log je `session.v4.jsonl.zstd` s VÍCE rámci; `zstdDecompressSync`
// přečte jen první (past z `_analyza\hl2-rozbal-session2.mjs`).
import { readFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { zstdDecompressSync } from 'node:zlib';

function dec(buf) {
  const s = [0];
  for (let k = 2; k < buf.length - 3; k++) {
    if (buf[k] === 0x28 && buf[k + 1] === 0xb5 && buf[k + 2] === 0x2f && buf[k + 3] === 0xfd) s.push(k);
  }
  s.push(buf.length);
  let o = '';
  for (let k = 0; k < s.length - 1; k++) {
    try { o += zstdDecompressSync(buf.subarray(s[k], s[k + 1])).toString('utf8'); } catch { /* rám */ }
  }
  return o;
}

function soubory(d) {
  const out = [];
  for (const e of readdirSync(d, { withFileTypes: true })) {
    const p = join(d, e.name);
    if (e.isDirectory()) out.push(...soubory(p));
    else if (/^session(\.v\d+)?\.jsonl\.zstd$/.test(e.name)) out.push(p);
  }
  return out;
}

for (const dir of process.argv.slice(2)) {
  console.log('='.repeat(78));
  console.log(dir);
  console.log('='.repeat(78));
  for (const f of soubory(dir)) {
    const txt = dec(readFileSync(f));
    const modely = new Map(), efforty = new Map(), okna = new Map();
    let headeru = 0;
    for (const line of txt.split('\n')) {
      if (!line.trim()) continue;
      let o; try { o = JSON.parse(line); } catch { continue; }
      if (o.type !== 'request/header') continue;
      headeru++;
      const h = o.data?.header ?? {};
      const c = h.config ?? {};
      const model = c.model ?? h.model ?? '?';
      modely.set(model, (modely.get(model) || 0) + 1);
      if (c.reasoningEffort) efforty.set(c.reasoningEffort, (efforty.get(c.reasoningEffort) || 0) + 1);
      const w = h.contextWindow ?? c.contextWindow;
      if (w) okna.set(String(w), (okna.get(String(w)) || 0) + 1);
      if (c.maxTokens) okna.set('maxTokens=' + c.maxTokens, (okna.get('maxTokens=' + c.maxTokens) || 0) + 1);
    }
    const fmt = (m) => [...m.entries()].sort((a, b) => b[1] - a[1]).map(([k, v]) => `${k} ×${v}`).join('   ') || '(nic)';
    console.log(`  ${f.split(/[\\/]/).slice(-2)[0]}  (hlaviček: ${headeru})`);
    console.log(`    model:            ${fmt(modely)}`);
    console.log(`    reasoningEffort:  ${fmt(eforty)}`);
    console.log(`    okno / maxTokens: ${fmt(okna)}`);
  }
}

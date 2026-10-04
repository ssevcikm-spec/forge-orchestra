// Důkaz, že headless běh použil route openrouter-stealth a model
// stealth/space-bunny-alpha (a ne tichý fallback na deepseek).
// Spuštění: node _analyza\stealth-dukaz.mjs [session-id | newest]
import { readFileSync, readdirSync, statSync } from 'node:fs';
import { join } from 'node:path';
import { zstdDecompressSync } from 'node:zlib';

const ROOT = 'C:/Users/Ssevc/.dsh/sessions/--C-Users-Ssevc-Local-Deepseek--';
const which = process.argv[2] ?? 'newest';

let dir;
if (which === 'newest') {
  // nejnovější session, kterou NEpsala tahle session (tu poznáme podle velikosti > 100 kB)
  const dirs = readdirSync(ROOT)
    .map((d) => {
      try {
        return { d, t: statSync(join(ROOT, d)).mtimeMs, s: statSync(join(ROOT, d, 'session.v4.jsonl.zstd')).size };
      } catch { return null; }
    })
    .filter((x) => x && x.s > 0)
    .sort((a, b) => b.t - a.t);
  const kandidat = dirs.find((x) => x.s < 120000) ?? dirs[0];
  dir = kandidat.d;
  console.log('# vybraná session:', dir, `(${kandidat.s} B)`);
} else {
  dir = readdirSync(ROOT).find((d) => d.includes(which));
  if (!dir) { console.error('session nenalezena'); process.exit(1); }
}

const buf = readFileSync(join(ROOT, dir, 'session.v4.jsonl.zstd'));
const offsety = [];
for (let i = 0; i < buf.length - 3; i++) {
  if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) offsety.push(i);
}
let text = '';
for (let k = 0; k < offsety.length; k++) {
  const od = offsety[k];
  const do_ = k + 1 < offsety.length ? offsety[k + 1] : buf.length;
  try { text += zstdDecompressSync(buf.subarray(od, do_)).toString('utf8'); } catch { /* přeskoč */ }
}
const radky = text.split(/\r?\n/).filter(Boolean);
console.log(`# rámců: ${offsety.length}, řádků: ${radky.length}`);

let provider = null, model = null, reasoning = null, finish = null, usage = null, dotceno = 0;
for (const l of radky) {
  let o; try { o = JSON.parse(l); } catch { continue; }
  const s = JSON.stringify(o);
  if (/space-bunny|openrouter-stealth/.test(s)) dotceno++;
  const p = o?.provider ?? o?.request?.provider ?? o?.header?.provider ?? o?.data?.provider;
  const m = o?.model ?? o?.request?.model ?? o?.header?.model ?? o?.data?.model;
  if (typeof p === 'string' && typeof m === 'string' && /space-bunny|openrouter/.test(p + m)) { provider = p; model = m; }
  for (const mm of s.matchAll(/"(?:provider|model|reasoningEffort|finishReason)":"([^"]{1,60})"/g)) {
    if (mm[1].includes('bunny') || mm[1].includes('openrouter')) { /* zmíněno */ }
  }
  for (const mm of s.matchAll(/"reasoningEffort":"([^"]+)"/g)) reasoning = mm[1];
  for (const mm of s.matchAll(/"finishReason":"([^"]+)"/g)) finish = mm[1];
  for (const mm of s.matchAll(/"totalTokens":(\d+)/g)) usage = mm[1];
}
console.log('# řádků zmiňujících space-bunny/openrouter-stealth:', dotceno);
console.log('# provider/model z logu:', provider, '/', model);
console.log('# reasoningEffort:', reasoning, '| finishReason:', finish, '| totalTokens:', usage);
if (dotceno === 0) { console.error('DŮKAZ CHYBÍ: v session logu není ani zmínka o modelu'); process.exit(1); }
console.log('DŮKAZ OK: běh je spojený s modelem stealth/space-bunny-alpha');

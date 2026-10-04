// Session log: zstd s více rámci. Streamovaný dekodér se taky zasekne na prvním.
// Tohle dekóduje rámec po rámci a spojí je.
// Spuštění: node _analyza\hl2-rozbal-session2.mjs <session-id>
import { readFileSync, writeFileSync, readdirSync } from 'node:fs';
import { join } from 'node:path';
import { zstdDecompressSync } from 'node:zlib';

const ROOT = 'C:/Users/Ssevc/.dsh/sessions/--C-Users-Ssevc-Local-Deepseek--';
const WS = _STANICE;
const hledany = process.argv[2];
if (!hledany) { console.error('pouzij: node hl2-rozbal-session2.mjs <session-id>'); process.exit(1); }

const dir = readdirSync(ROOT).find((d) => d.includes(hledany));
if (!dir) { console.error('session nenalezena'); process.exit(1); }
const buf = readFileSync(join(ROOT, dir, 'session.v4.jsonl.zstd'));

// Najdi offsety všech rámců (magic 28 b5 2f fd)
const offsety = [];
for (let i = 0; i < buf.length - 3; i++) {
  if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) offsety.push(i);
}
console.log(`# ramcu: ${offsety.length}`);

// Dekóduj každý rámec zvlášť; konec rámce = začátek dalšího
let text = '';
let ok = 0, chyb = 0;
for (let k = 0; k < offsety.length; k++) {
  const od = offsety[k];
  const do_ = k + 1 < offsety.length ? offsety[k + 1] : buf.length;
  try {
    text += zstdDecompressSync(buf.subarray(od, do_)).toString('utf8');
    ok++;
  } catch {
    // zkus delší konec (rámec může mít trailing)
    let hotovo = false;
    for (let end = do_ + 4; end <= Math.min(do_ + 64, buf.length) && !hotovo; end += 4) {
      try { text += zstdDecompressSync(buf.subarray(od, end)).toString('utf8'); ok++; hotovo = true; } catch { /* zkus dalsi */ }
    }
    if (!hotovo) chyb++;
  }
}
console.log(`# dekodovano ramcu: ${ok}, selhalo: ${chyb}`);
console.log(`# vysledny text: ${text.length} znaku`);

const out = join(WS, '_analyza', `tmp-session-${hledany}.jsonl`);
writeFileSync(out, text, 'utf8');
const radky = text.split(/\r?\n/).filter(Boolean);
console.log(`# radku: ${radky.length} -> ${out}\n`);

const pocet = {};
const cesty = new Set();
const prikazy = [];
for (const l of radky) {
  let o; try { o = JSON.parse(l); } catch { continue; }
  const s = JSON.stringify(o);
  for (const m of s.matchAll(/"(?:name|toolName|tool)":"(write|edit|read|pwsh|grep|glob|present|create_goal|update_goal|todo_write|subagent|skill|ask_user_question|job_output|list_agents|send_message)"/g)) {
    pocet[m[1]] = (pocet[m[1]] || 0) + 1;
  }
  for (const m of s.matchAll(/"file_path":"([^"]+)"/g)) cesty.add(m[1]);
  for (const m of s.matchAll(/"command":"((?:[^"\\]|\\.){0,400})"/g)) prikazy.push(m[1]);
}
console.log('## Nastroje (pocty)');
for (const [k, v] of Object.entries(pocet).sort((a, b) => b[1] - a[1])) console.log(`   ${String(v).padStart(3)}x  ${k}`);
if (cesty.size) {
  console.log('\n## Cesty');
  for (const c of [...cesty].sort()) console.log('   ' + c);
}
if (prikazy.length) {
  console.log(`\n## Prikazy (${prikazy.length}, poslednich 20)`);
  for (const c of prikazy.slice(-20)) console.log('   ' + c.replace(/\\n/g, ' ').slice(0, 150));
}

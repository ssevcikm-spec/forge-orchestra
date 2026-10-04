// Session log je zstd s MNOHO RAMCI (naměřeno: 1081 v jednom souboru).
// zstdDecompressSync precte jen PRVNI ramec -> 212 bajtu a ticho.
// Tohle pouzije streamovany dekoder, ktery projde vsechny.
// Spuštění: node _analyza\hl2-rozbal-session.mjs <session-id>
import { readFileSync, writeFileSync, readdirSync, createWriteStream } from 'node:fs';
import { join } from 'node:path';
import { createZstdDecompress } from 'node:zlib';
import { pipeline } from 'node:stream/promises';
import { Readable } from 'node:stream';

const ROOT = 'C:/Users/Ssevc/.dsh/sessions/--C-Users-Ssevc-Local-Deepseek--';
const WS = 'C:/Users/Ssevc/Local-Deepseek';
const hledany = process.argv[2];
if (!hledany) { console.error('pouzij: node hl2-rozbal-session.mjs <session-id>'); process.exit(1); }

const dir = readdirSync(ROOT).find((d) => d.includes(hledany));
if (!dir) { console.error('session nenalezena'); process.exit(1); }

const soubor = join(ROOT, dir, 'session.v4.jsonl.zstd');
const buf = readFileSync(soubor);
let frames = 0;
for (let i = 0; i < buf.length - 3; i++) {
  if (buf[i] === 0x28 && buf[i + 1] === 0xb5 && buf[i + 2] === 0x2f && buf[i + 3] === 0xfd) frames++;
}

const out = join(WS, '_analyza', `tmp-session-${hledany}.jsonl`);
try {
  await pipeline(Readable.from(buf), createZstdDecompress(), createWriteStream(out));
} catch (e) {
  console.error('streamovany zstd selhal:', e.message);
  process.exit(1);
}
const text = readFileSync(out, 'utf8');
const radky = text.split(/\r?\n/).filter(Boolean);
console.log(`# session ${dir}`);
console.log(`# zstd ramcu v souboru: ${frames} (proto stacilo zstdDecompressSync jen na prvni)`);
console.log(`# rozbaleno: ${text.length} znaku, ${radky.length} radku -> ${out}\n`);

const pocet = {};
const cesty = new Set();
const prikazy = [];
for (const l of radky) {
  let o; try { o = JSON.parse(l); } catch { continue; }
  const s = JSON.stringify(o);
  for (const m of s.matchAll(/"(?:name|toolName|tool)":"(write|edit|read|pwsh|grep|glob|present|create_goal|update_goal|todo_write|subagent|skill|ask_user_question|job_output|list_agents|send_message)"/g)) {
    pocet[m[1]] = (pocet[m[1]] || 0) + 1;
  }
  for (const m of s.matchAll(/"file_path":"([^"]+)"/g)) cesty.add(m[1].replace(/\\\\/g, '\\'));
  for (const m of s.matchAll(/"command":"((?:[^"\\]|\\.){0,400})"/g)) prikazy.push(m[1]);
}
console.log('## Nastroje (pocty)');
for (const [k, v] of Object.entries(pocet).sort((a, b) => b[1] - a[1])) console.log(`   ${String(v).padStart(3)}x  ${k}`);
if (cesty.size) {
  console.log('\n## Cesty zminene v tool callech');
  for (const c of [...cesty].sort()) console.log('   ' + c);
}
if (prikazy.length) {
  console.log(`\n## Prikazy (${prikazy.length}, poslednich 25)`);
  for (const c of prikazy.slice(-25)) console.log('   ' + c.replace(/\\n/g, ' ').slice(0, 150));
}

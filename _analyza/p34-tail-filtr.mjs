// p34-tail-filtr.mjs — filtr pro `wrangler tail --format json` (P34).
//
// PROČ: `wrangler tail` sype celé hlavičky požadavků (jeden event = stovky
// řádků). Pro měření poměru `outcome`/`cpuTime` u cron eventů potřebuju
// JEDEN ŘÁDEK na event. Filtr čte stdin, skládá TOP-LEVEL JSON objekty
// (stavový automat nad hloubkou závorek, mimo řetězce) a tiskne souhrn;
// plné objekty zapisuje do JSONL dokladu (gitignorované jméno `*vystup.txt`).
//
// Použití:
//   node conductor/node_modules/wrangler/bin/wrangler.js tail forge-conductor --format json |
//     node _analyza/p34-tail-filtr.mjs > _analyza/p34-tail-cron-vystup.txt
import { appendFileSync } from 'node:fs';

const FULL = '_analyza/p34-tail-cron-plny-vystup.txt';
let buf = '';

function zpracuj(text) {
  let o;
  try { o = JSON.parse(text); } catch { return; }
  const ev = o.event || {};
  const druh = ev.cron !== undefined ? `CRON ${ev.cron}`
    : (ev.request ? `HTTP ${ev.request.method} ${String(ev.request.url).replace('https://forge-conductor.ssevcikm.workers.dev', '')}`
      : Object.keys(ev).join(','));
  const logs = (o.logs || []).map((l) => (Array.isArray(l.message) ? l.message.join(' ') : String(l.message)));
  const ts = o.eventTimestamp ? new Date(o.eventTimestamp).toISOString() : '?';
  console.log(`${ts} | ${druh} | outcome=${o.outcome} | cpu=${o.cpuTime}ms | wall=${o.wallTime}ms`
    + ` | ver=${(o.scriptVersion || {}).id}`
    + (logs.length ? ` | LOG: ${logs.slice(0, 3).join(' ; ').slice(0, 300)}` : '')
    + ((o.exceptions || []).length ? ` | EXC: ${JSON.stringify(o.exceptions).slice(0, 300)}` : ''));
  appendFileSync(FULL, JSON.stringify(o) + '\n', 'utf8');
}

function skenuj() {
  let i = 0, hloubka = 0, vRetezci = false, escape = false, start = -1;
  while (i < buf.length) {
    const ch = buf[i];
    if (vRetezci) {
      if (escape) escape = false;
      else if (ch === '\\') escape = true;
      else if (ch === '"') vRetezci = false;
    } else if (ch === '"') vRetezci = true;
    else if (ch === '{') { if (hloubka === 0) start = i; hloubka++; }
    else if (ch === '}') {
      hloubka--;
      if (hloubka === 0 && start >= 0) {
        zpracuj(buf.slice(start, i + 1));
        buf = buf.slice(i + 1);
        i = 0; start = -1;
        continue;
      }
    }
    i++;
  }
}

process.stdin.setEncoding('utf8');
process.stdin.on('data', (chunk) => { buf += chunk; skenuj(); });
process.stdin.on('end', () => console.log('# tail ukoncen'));

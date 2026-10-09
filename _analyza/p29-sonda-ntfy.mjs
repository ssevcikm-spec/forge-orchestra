// P29 — SONDA: CO HLÁSIL WATCHDOG? (ntfy, jen čtení)
//
// PROČ: tik hlásí „spusteno: 0 úloh“ a přitom je 5 úloh `ready` — a /roadmap
// NEVYDÁVÁ počítadlo spálených běhů na granuli. To počítadlo je přitom jediná
// známá podmínka, která úlohu v `find()` zahodí tiše. Watchdog (B3a) posílá
// zprávu „Forge: granule se nedari“ — takže se dá PŘEČÍST, co naměřil.
//
// Použití: node _analyza/p29-sonda-ntfy.mjs [hodin]
import { readFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const cfg = JSON.parse(readFileSync(join(WS, '.secrets', 'cf-secrets.json'), 'utf8')
  .replace(/^\uFEFF/, ''));
const topic = cfg.NTFY_TOPIC;
const hodin = Number(process.argv[2] || 24);
if (!topic) {
  console.log(JSON.stringify({ chyba: 'NTFY_TOPIC v .secrets/cf-secrets.json není' }));
  process.exit(1);
}

// ⚠ Téma se NIKDY nevypisuje (nese ho tajemství); do výstupu jde jen jeho DÉLKA.
const url = `https://ntfy.sh/${topic}/json?poll=1&since=${hodin}h`;
const r = await fetch(url);
const raw = await r.text();
const zpravy = raw.split(/\r?\n/).filter((l) => l.trim()).map((l) => {
  try { return JSON.parse(l); } catch { return { chyba: 'neni JSON', raw: l.slice(0, 120) }; }
});
const zajimave = zpravy.filter((z) => /granule|nedari|watchdog|strop|zastavena/i
  .test(String(z.title || '') + ' ' + String(z.message || '')));
console.log(JSON.stringify({
  http: r.status,
  topic_delka: topic.length,
  zprav_celkem: zpravy.length,
  zajimavych: zajimave.length,
  zpravy: zajimave.map((z) => ({
    cas: z.time ? new Date(z.time * 1000).toISOString() : null,
    title: z.title, message: z.message,
  })),
  poslednich_5: zpravy.slice(-5).map((z) => ({
    cas: z.time ? new Date(z.time * 1000).toISOString() : null, title: z.title,
    message: String(z.message || '').slice(0, 120),
  })),
}, null, 1));

// Druhé kolo hloubkové analýzy — živý stav conductora.
// Spuštění: node _analyza\hl2-live.mjs
// Síť jen Node fetch (TLS z PowerShellu na téhle stanici nefunguje).
// Secret se ze souboru načítá, ale NIKDY nevypisuje.
import { readFileSync } from 'node:fs';

const WS = 'C:/Users/Ssevc/Local-Deepseek';
const env = Object.fromEntries(
  readFileSync(`${WS}/orchestra/.env`, 'utf8').split(/\r?\n/)
    .filter((l) => l.includes('=') && !l.trim().startsWith('#'))
    .map((l) => [l.slice(0, l.indexOf('=')).trim(), l.slice(l.indexOf('=') + 1).trim()]),
);
const BASE = env.FORGE_URL.replace(/\/$/, '');
const H = { 'x-forge-secret': env.FORGE_SECRET };

async function get(cesta, h = H) {
  const t0 = Date.now();
  try {
    const r = await fetch(BASE + cesta, { headers: { accept: 'application/json', ...h } });
    const text = await r.text();
    let json = null;
    try { json = JSON.parse(text); } catch { /* */ }
    return { cesta, status: r.status, ms: Date.now() - t0, json, text: json ? null : text.slice(0, 300) };
  } catch (e) {
    return { cesta, status: null, ms: Date.now() - t0, error: String(e.message || e) };
  }
}

console.log(`# Živý stav conductora — ${new Date().toISOString()}`);
console.log(`# BASE = ${BASE}`);
console.log(`# secret: ${H['x-forge-secret'] ? 'nacten (nevypisuji)' : 'CHYBI'}\n`);

const vysledky = [];
for (const e of ['/games', '/roadmap', '/failed', '/queue', '/workers']) {
  vysledky.push(await get(e));
}

for (const v of vysledky) {
  console.log(`## ${v.cesta}  →  status=${v.status}  (${v.ms} ms)`);
  if (v.error) { console.log(`   CHYBA: ${v.error}\n`); continue; }
  if (v.text !== null) { console.log(`   (ne-JSON) ${v.text.replace(/\s+/g, ' ')}\n`); continue; }
  console.log(JSON.stringify(v.json, null, 2).slice(0, 9000));
  console.log();
}

// ---- Souhrn, který se dá citovat ----
const najdi = (c) => vysledky.find((v) => v.cesta === c)?.json;
const rm = najdi('/roadmap');
console.log('=== SOUHRN: roadmap řádky ===');
const radky = Array.isArray(rm) ? rm : (rm?.roadmap ?? rm?.rows ?? rm?.items ?? null);
if (radky) {
  console.log(`řádků: ${radky.length}`);
  const hotove = radky.filter((r) => r.done === 1 || r.done === true);
  console.log(`done: ${hotove.length}`);
  console.log('item_id | done | task_id | status | updated_at');
  for (const r of radky) {
    console.log(`  ${String(r.item_id).padEnd(20)} done=${String(r.done).padEnd(5)} task_id=${String(r.task_id).padEnd(6)} ${String(r.status ?? '-').padEnd(9)} ${r.updated_at ?? '-'}`);
  }
} else if (rm) {
  console.log('(neznámý tvar)', JSON.stringify(rm).slice(0, 800));
}

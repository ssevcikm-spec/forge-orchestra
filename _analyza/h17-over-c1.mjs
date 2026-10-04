// H17 — NEZÁVISLÉ ověření měřidla C1 (`a3-kontrola.mjs`, sekce D).
//
// PROČ VLASTNÍ MĚŘIDLO: ověřit, že cizí měřidlo umí selhat, se nedá udělat
// tím, že si přečtu jeho kód. Tenhle skript dělá TOTÉŽ ROZHODNUTÍ (je `/queue`
// parsovatelný seznam úloh?) a spouští se nad DVĚMA adresami:
//   1) živý conductor        → musí projít (exit 0)
//   2) podvržený conductor   → musí SPADNOUT (exit 1)
// Teprve když obojí vyjde, je doložené, že ta podmínka umí selhat.
//
// Použití:  node _analyza/h17-over-c1.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const ZAJIMAVE = ['world.nodes', 'entity.player.api', 'persist.save.state', 'engine.shell'];

async function zmer(url, popis) {
  const cond = async (p) => {
    const r = await fetch(`${url}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
    return r.ok ? r.json() : { chyba: r.status };
  };
  console.log(`\n${'='.repeat(74)}\nMĚŘENÍ: ${popis}   (${url})\n${'='.repeat(74)}`);
  let chyb = 0;
  const h = await cond('/health');
  console.log(`  /health ok=${h.ok}`);
  if (h.ok !== true) { chyb++; console.log('  CHYBA conductor neodpovídá'); }

  const rm = await cond('/roadmap');
  const r = rm.roadmap || [];
  const rq = await cond('/queue');
  const fronta = Array.isArray(rq) ? rq : (rq.tasks || []);
  const frontaOk = Array.isArray(fronta) && fronta.length > 0;
  console.log(`  /queue vrátil ${fronta.length} úloh, /roadmap ${r.length} řádků`);
  if (!frontaOk) {
    chyb++;
    console.log(`  CHYBA /queue nevrátil parsovatelný seznam úloh: ${JSON.stringify(rq).slice(0, 200)}`);
  }
  const rmap = new Map();
  for (const row of r) rmap.set(String(row.item_id || '').replace('uo-shadows/', ''), row);
  for (const g of ZAJIMAVE) {
    const row = rmap.get(g);
    if (!row) { console.log(`  ${g.padEnd(22)} v /roadmap NENÍ`); continue; }
    const tid = row.task_id;
    if (tid === null || tid === undefined) { console.log(`  ${g.padEnd(22)} task_id=null`); continue; }
    const u = fronta.find((x) => Number(x.id) === Number(tid));
    if (!u) { console.log(`  ${g.padEnd(22)} task_id=${tid} — v /queue NENÍ (fronta ${fronta.length})`); continue; }
    console.log(`  ${g.padEnd(22)} roadmap=${row.status}  úloha #${u.id} stav=${u.status} pokusů=${u.attempts}`);
  }
  console.log(`  → ${chyb === 0 ? '✓ VŠE V POŘÁDKU' : `✗ NALEZENO ${chyb} PROBLÉMŮ`}   (exit=${chyb === 0 ? 0 : 1})`);
  return chyb;
}

const zivy = await zmer(env.FORGE_URL, '1) ŽIVÝ CONDUCTOR — musí projít');
const podvrhUrl = process.argv[2] || 'http://127.0.0.1:8791';
let podvrh = null;
try {
  podvrh = await zmer(podvrhUrl, '2) PODVRH — /queue vrací rozcestník, MUSÍ SPADNOUT');
} catch (e) {
  console.log(`\nCHYBA: podvrh na ${podvrhUrl} neběží (${e.message})`);
  process.exit(2);
}

console.log(`\n${'='.repeat(74)}\nVYHODNOCENÍ\n${'='.repeat(74)}`);
console.log(`  živý conductor: ${zivy === 0 ? 'prošel (očekáváno)' : `SPADL (${zivy} problémů) — neočekáváno`}`);
console.log(`  podvrh:         ${podvrh > 0 ? `spadl (${podvrh} problémů) — očekáváno` : 'PROŠEL — měřidlo je slepé!'}`);
if (zivy === 0 && podvrh > 0) {
  console.log('\n  ✓ PODMÍNKA UMÍ SELHAT — měřidlo C1 měří (vlastní měření, ne opsané číslo)');
  process.exit(0);
}
console.log('\n  ✗ NELZE TVRDIT, ŽE MĚŘIDLO MĚŘÍ');
process.exit(1);

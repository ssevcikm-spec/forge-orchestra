// P18c — stav úloh #145 a #146 v /queue (jsou v cooldownu? kolik pokusů?).
//
// PROČ: `HANDOFF.md` §16.7 tvrdí, že obě úlohy jsou „zpátky ready s attempts=1"
// a drží je cooldown `RETRY_HOURS` (3 h). To je tvrzení o STAVU, které se musí
// měřit živě — a `a3-kontrola.mjs` ho sice zobrazuje, ale jen počty pokusů.
//
// Použití: node _analyza/p18c-stav-uloh.mjs
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
if (!env.FORGE_URL) { console.log('CHYBA: .env neobsahuje FORGE_URL'); process.exit(2); }

const get = async (p) => {
  const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  return r.ok ? r.json() : { chyba: r.status };
};

const q = await get('/queue');
const fronta = Array.isArray(q) ? q : (q.tasks || []);
const rm = await get('/roadmap');
const roadmap = rm.roadmap || [];

console.log('════ ÚLOHY #145 a #146 ════');
for (const id of [145, 146]) {
  const u = fronta.find((x) => Number(x.id) === id);
  if (!u) { console.log(`  #${id}: v /queue NENÍ`); continue; }
  console.log(`  #${id}:`);
  for (const [k, v] of Object.entries(u)) {
    const s = typeof v === 'string' ? v.replace(/\n/g, ' ⏎ ') : JSON.stringify(v);
    console.log(`      ${k} = ${String(s).slice(0, 220)}`);
  }
}

console.log('\n════ TÁŽ ÚLOHA V /roadmap ════');
for (const r of roadmap) {
  if ([145, 146].includes(Number(r.task_id))) {
    console.log(`  ${r.item_id}  status=${r.status}  task_id=${r.task_id}` +
      `  naposledy_selhalo=${r.naposledy_selhalo ?? '(sloupec v /roadmap není)'}  updated_at=${r.updated_at}`);
  }
}

console.log('\n════ /failed ════');
const f = await get('/failed');
const ft = f.tasks || f;
console.log(`  položek: ${Array.isArray(ft) ? ft.length : '?'}`);
for (const t of (Array.isArray(ft) ? ft : [])) {
  console.log(`   #${t.id} ${String(t.title || '').slice(0, 40)}  attempts=${t.attempts ?? '?'}`);
}

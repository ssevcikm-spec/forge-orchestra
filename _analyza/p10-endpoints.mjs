// P10 — existuje endpoint `/tasks`? Co vrací? A co `/queue` (kde úlohy OPRAVDU jsou)?
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const cond = async (p) => {
  const x = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  return { stav: x.status, typ: x.headers.get('content-type'), telo: await x.text() };
};

for (const cesta of ['/tasks', '/queue', '/failed']) {
  const v = await cond(cesta);
  console.log(`\n=== ${cesta} ===`);
  console.log(`HTTP ${v.stav}  ${v.typ}`);
  console.log(v.telo.length > 700 ? v.telo.slice(0, 700) + ' …(zkráceno)' : v.telo);
}

const q = await cond('/queue');
try {
  const d = JSON.parse(q.telo);
  const seznam = d.tasks || [];
  console.log(`\n=== /queue: ${seznam.length} úloh — hledám nové granule ===`);
  for (const g of ['world.nodes', 'entity.player.api', 'persist.save.state', 'engine.shell']) {
    const x = seznam.filter((u) => JSON.stringify(u).includes(g));
    console.log(`  ${g.padEnd(20)} ${x.length ? x.map((u) => `id=${u.id} status=${u.status} attempts=${u.attempts}`).join(' | ') : '(žádná úloha)'}`);
  }
  console.log('  --- všech ' + seznam.length + ' úloh (id/status/title) ---');
  for (const u of seznam) console.log(`    ${String(u.id).padStart(4)} ${String(u.status).padEnd(9)} ${String(u.title).slice(0, 70)}`);
} catch (e) {
  console.log('  /queue se nedá parsovat:', e.message);
}

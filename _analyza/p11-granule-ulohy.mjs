// P11 — mapování granule → úloha v D1 přes `/roadmap` + `/queue`.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const cond = async (p) => (await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();

const rm = await cond('/roadmap');
const qu = await cond('/queue');
const podleId = new Map((qu.tasks || []).map((t) => [t.id, t]));

console.log('=== /roadmap: item_id → task_id → co o úloze ví /queue ===');
for (const r of rm.roadmap || []) {
  const k = String(r.item_id).replace('uo-shadows/', '');
  const t = r.task_id ? podleId.get(r.task_id) : null;
  const u = t ? `úloha #${t.id} status=${t.status} attempts=${t.attempts}` : (r.task_id ? `úloha #${r.task_id} NENÍ v /queue (limit 50)` : 'bez úlohy');
  console.log(`  ${k.padEnd(20)} roadmap=${String(r.status).padEnd(8)} task_status=${String(r.task_status).padEnd(8)} ${u}`);
}
console.log(`\n  /roadmap řádků: ${(rm.roadmap || []).length}, /queue úloh: ${(qu.tasks || []).length}`);

console.log('\n=== hledám granule, které A3 označila za "bez úlohy" ===');
for (const g of ['world.nodes', 'entity.player.api', 'persist.save.state', 'engine.shell']) {
  const r = (rm.roadmap || []).find((x) => String(x.item_id).includes(g));
  const t = r?.task_id ? podleId.get(r.task_id) : null;
  console.log(`  ${g.padEnd(20)} ${r ? `roadmap=${r.status} task_id=${r.task_id} task_status=${r.task_status}` : 'V /roadmap VŮBEC NENÍ'}`
    + (t ? ` → /queue: #${t.id} „${String(t.title).slice(0, 55)}" status=${t.status} attempts=${t.attempts}` : ''));
}

// P9 — zive mereni: cas serveru GitHubu (kontrola hodin), /health, /failed, /tasks.
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const r = await fetch('https://api.github.com/rate_limit',
  { headers: { Authorization: `Bearer ${PAT}`, 'User-Agent': 'p9', Accept: 'application/vnd.github+json' } });
console.log('GitHub server Date :', r.headers.get('date'));
console.log('Localni cas (ISO)  :', new Date().toISOString());
await r.json();

const cond = async (p) => {
  const x = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  const t = await x.text();
  return { stav: x.status, telo: t };
};

for (const cesta of ['/health', '/failed', '/roadmap']) {
  const v = await cond(cesta);
  const t = v.telo.length > 900 ? v.telo.slice(0, 900) + '…' : v.telo;
  console.log(`\n${cesta}  [HTTP ${v.stav}]  ${t}`);
}

const t = await cond('/tasks');
try {
  const d = JSON.parse(t.telo);
  const seznam = Array.isArray(d) ? d : (d.tasks || []);
  console.log(`\n/tasks: ${seznam.length} úloh`);
  for (const g of ['world.nodes', 'entity.player.api', 'persist.save.state', 'engine.shell', 'entity.enemy']) {
    const x = seznam.filter((u) => String(u.item_id || '').includes(g));
    console.log(`  ${g.padEnd(20)} ${x.length ? x.map((u) => `id=${u.id} ${u.status} attempts=${u.attempts}`).join(' | ') : '(žádná úloha)'}`);
  }
} catch (e) {
  console.log('  /tasks se nedá parsovat:', t.telo.slice(0, 200));
}

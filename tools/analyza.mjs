import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Analyza orchestra: stav, churn behu, PR a prubeh prace.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status, telo: (await r.text()).slice(0, 200) };
};
const cond = async (p) => {
  const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
  return r.ok ? r.json() : { chyba: r.status };
};

console.log('════ 1. CONDUCTOR ════');
const h = await cond('/health');
console.log(`ready=${h.ready} running=${h.running} games=${h.games}`);
for (const w of h.workers || []) {
  console.log(`  uzel ${w.name}: ${w.minutes_ago <= 5 ? 'AKTIVNI' : `off ${Math.round(w.minutes_ago / 60)} h`} [${w.kinds}]`);
}

console.log('\n════ 2. REGISTR HER ════');
const g = await cond('/games');
for (const x of g.games || []) console.log(`  ${x.active ? 'AKTIVNI' : 'vypnuta'} ${x.game_id} -> ${x.repo} (roadmapa ${x.roadmap_file})`);

console.log('\n════ 3. ROADMAPA V D1 ════');
const rm = await cond('/roadmap');
const items = rm.roadmap || [];
const podleStavu = {};
for (const it of items) (podleStavu[it.status] ||= []).push(it.item_id);
for (const [s, arr] of Object.entries(podleStavu)) console.log(`  ${s.padEnd(10)} ${arr.length}  ${arr.slice(0, 8).join(', ')}${arr.length > 8 ? ' …' : ''}`);

console.log('\n════ 4. FRONTA (vsechny stavy) ════');
const q = await cond('/queue');
const tasks = q.tasks || [];
const stavy = {};
for (const t of tasks) (stavy[t.status] ||= []).push(t);
for (const [s, arr] of Object.entries(stavy)) {
  console.log(`  ${s.padEnd(10)} ${arr.length}`);
  for (const t of arr.slice(0, 5)) {
    let p = t.payload; if (typeof p === 'string') { try { p = JSON.parse(p); } catch { p = {}; } }
    p = p || {};
    console.log(`      #${String(t.id).padEnd(5)} a=${String(t.attempts).padEnd(3)} grain=${String(p.grain || '?').padEnd(18)} model=${String(p.model || '-').padEnd(7)} ${String(t.title).slice(0, 40)}`);
  }
}

console.log('\n════ 5. CHURN: behy na ukol (GitHub) ════');
const runs = await gh(`/repos/${REPO}/actions/runs?per_page=100`);
const forge = (runs.workflow_runs || []).filter((x) => /Forge #/.test(x.name || ''));
const podleTasku = {};
for (const x of forge) {
  const m = /Forge #(\d+)/.exec(x.name);
  const id = Number(m[1]);
  (podleTasku[id] ||= []).push(x);
}
console.log(`  Forge behu v posledních 100: ${forge.length}, unikátních úkolů: ${Object.keys(podleTasku).length}`);
for (const [id, arr] of Object.entries(podleTasku).sort((a, b) => b[1].length - a[1].length)) {
  const vysledky = {};
  for (const x of arr) vysledky[x.conclusion ?? x.status] = (vysledky[x.conclusion ?? x.status] || 0) + 1;
  console.log(`  task #${String(id).padEnd(5)} behu=${String(arr.length).padEnd(3)} ${JSON.stringify(vysledky)}`);
}

console.log('\n════ 6. PR STAV ════');
const prs = await gh(`/repos/${REPO}/pulls?state=all&per_page=30&sort=created&direction=desc`);
if (Array.isArray(prs)) {
  console.log(`  PR celkem (posledních 30): ${prs.length}`);
  for (const p of prs.slice(0, 12)) {
    const stav = p.merged_at ? 'MERGED' : p.state.toUpperCase();
    console.log(`  #${String(p.number).padEnd(4)} ${stav.padEnd(7)} ${(p.created_at || '').slice(5, 16)} ${String(p.title).slice(0, 60)}`);
  }
} else console.log('  ' + JSON.stringify(prs).slice(0, 200));

console.log('\n════ 7. POSLEDNI BEHY (detail) ════');
for (const x of forge.slice(0, 10)) {
  console.log(`  ${x.created_at.slice(11, 19)}  ${String(x.conclusion ?? x.status).padEnd(12)} ${x.name}  pokus=${x.run_attempt}`);
}

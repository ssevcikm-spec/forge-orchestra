import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Souhrnná analýza: kde orchestra stojí, kolik pokusů spálila a na čem.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

// 1) Co je v roadmapě hotové (stav v D1, ne v souboru).
const env = readFileSync(`${ORCH}/.env`, 'utf8').replace(/^\uFEFF/, '');
const get = (k) => {
  for (const r of env.split(/\r?\n/)) if (r.startsWith(k + '=')) return r.slice(k.length + 1).trim();
  return '';
};
const rm = await (await fetch(`${get('FORGE_URL')}/roadmap`, {
  headers: { 'x-forge-secret': get('FORGE_SECRET') },
})).json();

const podleStavu = new Map();
for (const r of rm.roadmap || []) {
  const g = String(r.item_id).split('/')[1];
  podleStavu.set(g, { stav: r.status, pokusu: r.attempts, task: r.task_id, upd: r.updated_at });
}

// 2) Kolik běhů a jakých modelů se na každé granulí spálilo.
const runs = await (await fetch(
  `https://api.github.com/repos/${REPO}/actions/runs?per_page=60`, { headers: H })).json();
const forge = (runs.workflow_runs || []).filter((x) => /Forge #\d+/.test(x.name || ''));

const taskNaGrain = new Map();
for (const [g, info] of podleStavu) if (info.task) taskNaGrain.set(info.task, g);

const behyNaGrain = new Map();
for (const x of forge) {
  const t = Number(/Forge #(\d+)/.exec(x.name)[1]);
  const g = taskNaGrain.get(t);
  if (!g) continue;
  if (!behyNaGrain.has(g)) behyNaGrain.set(g, []);
  behyNaGrain.get(g).push(x);
}

console.log('=== STAV PODLE ROADMAPY (D1) ===');
const poradi = ['done', 'failed', 'queued', 'running'];
const seskup = new Map();
for (const [g, i] of podleStavu) {
  if (!seskup.has(i.stav)) seskup.set(i.stav, []);
  seskup.get(i.stav).push({ g, ...i });
}
for (const stav of poradi) {
  const sez = seskup.get(stav) || [];
  if (!sez.length) continue;
  console.log(`\n${stav.toUpperCase()} (${sez.length}):`);
  for (const x of sez.sort((a, b) => a.pokusu - b.pokusu)) {
    const behy = behyNaGrain.get(x.g) || [];
    const uspech = behy.filter((b) => b.conclusion === 'success').length;
    console.log(`  ${x.g.padEnd(16)} task=#${String(x.task).padEnd(4)} `
      + `pokusů=${String(x.pokusu).padEnd(3)} běhů=${String(behy.length).padEnd(3)} `
      + `úspěchů=${uspech}  naposledy=${x.upd || '-'}`);
  }
}

// 3) Souhrn.
let hotovo = 0, selhalo = 0, ostatni = 0;
for (const [, i] of podleStavu) {
  if (i.stav === 'done') hotovo++;
  else if (i.stav === 'failed') selhalo++;
  else ostatni++;
}
console.log(`\n=== SOUHRN ===`);
console.log(`  hotovo:  ${hotovo}`);
console.log(`  selhalo: ${selhalo}  (čeká na cooldown, pak zkusí znovu)`);
console.log(`  ostatní: ${ostatni}`);
console.log(`  celkem běhů Forge v historii (posledních 60): ${forge.length}`);
console.log(`  z toho úspěšných: ${forge.filter((x) => x.conclusion === 'success').length}`);

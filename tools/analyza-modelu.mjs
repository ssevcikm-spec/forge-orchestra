import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Spravne mapovani: /roadmap da task_id -> item_id ({game}/{grain}),
// roadmap.json z repa da grain -> modelova trida. Tim se overi, ze silne
// granule dostaly silny model.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);
const cond = async (p) => (await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } })).json();

// 1) roadmapa z repa: grain -> trida
const rm = await (await fetch(`https://raw.githubusercontent.com/${REPO}/main/.forge/roadmap.json`)).json();
const trida = {};
for (const g of rm.grains) trida[g.id] = g.model === 'strong' ? 'strong' : 'any';
console.log(`roadmapa z repa: ${rm.grains.length} granulí`);
const strong = Object.entries(trida).filter(([, v]) => v === 'strong').map(([k]) => k);
console.log(`  strong (${strong.length}): ${strong.join(', ')}`);

// 2) conductor: task_id -> grain
const road = await cond('/roadmap');
const taskGrain = {};
for (const r of road.roadmap || []) {
  const grain = (r.item_id || '').split('/').slice(1).join('/');
  if (r.task_id) taskGrain[r.task_id] = grain;
}
console.log(`\nconductor zná ${Object.keys(taskGrain).length} granul s task_id`);

// 3) behy + jejich model z logu
const runs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs?per_page=100`, { headers: H })).json();
const forge = (runs.workflow_runs || []).filter((x) => /Forge #/.test(x.name || ''));
console.log(`\n${'─'.repeat(96)}`);
console.log('task   granule             roadmapa  provider   model                  výsledek');
console.log('─'.repeat(96));

const videno = new Set();
for (const x of forge) {
  const id = Number(/Forge #(\d+)/.exec(x.name)[1]);
  const grain = taskGrain[id] || '(mimo DAG)';
  const trida_hodnota = trida[grain] || '';   // PRÁZDNÁ hodnota = „neurčeno"
  const poz = trida_hodnota || '—';           // '—' je JEN výplň pro tisk
  const jobs = await (await fetch(`https://api.github.com/repos/${REPO}/actions/runs/${x.id}/jobs`, { headers: H })).json();
  const j = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
  let prov = '?', mod = '?';
  if (j) {
    const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${j.id}/logs`, { headers: H });
    if (lg.ok) {
      const t = await lg.text();
      prov = /FORGE_PROVIDER:\s*(\S+)/.exec(t)?.[1] ?? '?';
      mod = /FORGE_MODEL:\s*(\S+)/.exec(t)?.[1] ?? '?';
    }
  }
  const vysl = x.conclusion ?? x.status;
  // Rozhoduje se podle HODNOTY (`trida_hodnota`), ne podle vytištěného textu.
  // `trida` je hodnota z reportu; `'—'` je jen VÝPLŇ pro prázdnou hodnotu,
  // kterou si tenhle skript sám vykresluje (viz `poz.padEnd` níž). Porovnávat
  // logiku s výplní znamená, že změna výplně (jiná pomlčka, '?', '-') tiše
  // rozjede rozhodování.
  const trida_ok = trida_hodnota === '' || trida_hodnota === 'any'
    ? ''
    : (['codestral-latest', 'gpt-oss-120b', 'openai/gpt-oss-120b'].includes(mod) ? ' [strong OK]' : ' [!!! strong granule na slabém modelu]');
  console.log(`#${String(id).padEnd(5)} ${grain.padEnd(19)} ${poz.padEnd(9)} ${prov.padEnd(10)} ${mod.padEnd(22)} ${vysl}${trida_ok}`);
  if (videno.size > 24) break;
  videno.add(id);
}

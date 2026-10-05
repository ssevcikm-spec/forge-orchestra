import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Kteří poskytovatelé a modely se skutečně potkali s opakovanými pokusy téhož tasku.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

const runs = await (await fetch(
  `https://api.github.com/repos/${REPO}/actions/runs?per_page=40`, { headers: H })).json();
const forge = (runs.workflow_runs || []).filter((x) => /Forge #\d+/.test(x.name || ''));

const podleTasku = new Map();
for (const x of forge) {
  const t = Number(/Forge #(\d+)/.exec(x.name)[1]);
  if (!podleTasku.has(t)) podleTasku.set(t, []);
  podleTasku.get(t).push(x);
}

const zajimave = [128, 131, 124, 125, 127].filter((t) => podleTasku.has(t));
for (const t of zajimave) {
  const sez = podleTasku.get(t).sort((a, b) => new Date(a.created_at) - new Date(b.created_at));
  console.log(`\n=== task #${t} (${sez.length} běhů) ===`);
  const modely = [];
  for (const x of sez) {
    const j = await (await fetch(
      `https://api.github.com/repos/${REPO}/actions/runs/${x.id}/jobs`, { headers: H })).json();
    const job = (j.jobs || []).find((z) => z.name.startsWith('Agent'));
    if (!job) continue;
    const lg = await fetch(
      `https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
    let vyber = '(log nedostupný)';
    if (lg.ok) {
      const radky = (await lg.text()).split('\n')
        .map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, '').trim());
      const volby = radky.filter((l) => /^Vybráno:/.test(l)).map((l) => l.replace('Vybráno: ', ''));
      vyber = volby.length ? volby.join('  →  ') : '(žádná volba)';
      for (const v of volby) modely.push(v);
    }
    const cas = x.created_at.slice(11, 19);
    console.log(`  ${cas}  ${String(x.conclusion).padEnd(8)} ${vyber}`);
  }
  const unikatni = [...new Set(modely)];
  console.log(`  -> použitých modelů: ${unikatni.length} z ${modely.length} pokusů`);
  if (modely.length > 1 && unikatni.length < modely.length) {
    const pocet = {};
    for (const m of modely) pocet[m] = (pocet[m] || 0) + 1;
    const opakovane = Object.entries(pocet).filter(([, n]) => n > 1);
    if (opakovane.length) {
      console.log(`  -> OPAKOVANĚ se stejným modelem: ${opakovane.map(([m, n]) => `${m} ${n}x`).join(', ')}`);
    }
  }
}

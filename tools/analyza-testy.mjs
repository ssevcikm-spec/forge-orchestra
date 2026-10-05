import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Preskoci instalacni kroky, najdi skutecny vystup testu a pricinu selhani.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };
const RUN = process.argv[2];

const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };
const jobs = await gh(`/repos/${REPO}/actions/runs/${RUN}/jobs`);
const j = (jobs.jobs || []).find((z) => z.name.startsWith('Agent'));
const lg = await fetch(`https://api.github.com/repos/${REPO}/actions/jobs/${j.id}/logs`, { headers: H });
const radky = (await lg.text()).split('\n').map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, ''));

// najdi radek, kde zacina krok "Testy hry"
let start = radky.findIndex((l) => /##\[group\]Run .*timeout 150|Testy hry \(Godot/.test(l));
if (start < 0) start = radky.findIndex((l) => /spust_testy|\[test\] OK/.test(l));
console.log(`start testu na radku ${start} z ${radky.length}\n`);

// vypis od zacatku testu, ale bez instalacnich bloku
let count = 0;
for (let i = start; i < radky.length && count < 120; i++) {
  const l = radky[i];
  if (/^\s*(\[command\]|Warning:|Cache|pythonLocation|Python_ROOT|LD_LIBRARY|PKG_CONFIG|XDG_DATA|npm |added \d+ packages)/.test(l)) continue;
  if (!l.trim()) continue;
  console.log(`${String(i).padStart(5)} | ${l.slice(0, 168)}`);
  count++;
}

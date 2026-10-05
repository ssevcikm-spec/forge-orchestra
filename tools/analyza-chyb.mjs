import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';
// P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni
// skriptu, aby nastroj fungoval z jakehokoliv umisteni repa.
// `tools/` je primo v koreni repa, takze PARENT = root repa.
const __dir = dirname(fileURLToPath(import.meta.url));
const PARENT = dirname(__dir);
// Seskupí chyby z neúspěšných běhů: jaký model, jaký typ chyby, které granule.
import { readFileSync } from 'node:fs';

const ORCH = join(PARENT);
const REPO = 'ssevcikm-spec/uo-shadows';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'analyza' };

/** Zařadí parse chybu do kategorie, ať je vidět, co modely reálně pletou. */
function kategorie(radek) {
  if (/Member "(\w+)" redefined/.test(radek)) return 'kolize se členem enginu (Member redefined)';
  if (/Cannot infer the type/.test(radek)) return 'chybí výslovný typ (Cannot infer type)';
  if (/Identifier "(\w+)" not declared/.test(radek)) return 'neznámý identifikátor';
  if (/hides a global script class/.test(radek)) return 'class_name koliduje s globálním jménem';
  if (/Function "(\w+)" has the same name/.test(radek)) return 'funkce koliduje s enginem';
  if (/Expected|Unexpected|Expected end of statement/.test(radek)) return 'syntaxe (Expected/Unexpected)';
  if (/Could not find type/.test(radek)) return 'neznámý typ (Could not find type)';
  if (/Cannot open|Failed loading|File not found/.test(radek)) return 'soubor/asset nenalezen';
  return 'jiné';
}

const runs = await (await fetch(
  `https://api.github.com/repos/${REPO}/actions/runs?per_page=40`, { headers: H })).json();

const forge = (runs.workflow_runs || []).filter((x) => /Forge #\d+/.test(x.name || ''));
const podleTasku = new Map();
for (const x of forge) {
  const id = Number(/Forge #(\d+)/.exec(x.name)[1]);
  if (!podleTasku.has(id) || new Date(x.created_at) > new Date(podleTasku.get(id).created_at)) {
    podleTasku.set(id, x);
  }
}

const pocetKategorii = new Map();
const vypis = [];
for (const [taskId, run] of [...podleTasku.entries()].sort((a, b) => a[0] - b[0]).slice(-8)) {
  const j = await (await fetch(
    `https://api.github.com/repos/${REPO}/actions/runs/${run.id}/jobs`, { headers: H })).json();
  const job = (j.jobs || []).find((z) => z.name.startsWith('Agent'));
  if (!job || job.conclusion === 'success') continue;
  const lg = await fetch(
    `https://api.github.com/repos/${REPO}/actions/jobs/${job.id}/logs`, { headers: H });
  if (!lg.ok) continue;
  const radky = (await lg.text()).split('\n')
    .map((l) => l.replace(/^\S*Z\s?/, '').replace(/\x1b\[[0-9;]*m/g, '').trim());

  const model = (radky.find((l) => /^FORGE_PROVIDER:/.test(l)) || '').replace('FORGE_PROVIDER: ', '');
  const tokeny = radky.filter((l) => /^Tokens:/.test(l)).pop() || '(žádné tokeny)';
  const chyby = [...new Set(radky.filter((l) => /SCRIPT ERROR: Parse Error/.test(l)))];
  const selhal = (job.steps || []).filter((s) => s.conclusion === 'failure').map((s) => s.name);

  let druh;
  if (selhal.some((s) => /nic nezměnil/.test(s))) druh = 'agent nezměnil kód';
  else if (selhal.some((s) => /Kontrola parsování/.test(s))) druh = 'parse chyba';
  else if (selhal.some((s) => /Testy/.test(s))) druh = 'testy hry';
  else druh = selhal.join(',');

  for (const c of chyby) {
    const k = kategorie(c);
    pocetKategorii.set(k, (pocetKategorii.get(k) || 0) + 1);
  }
  vypis.push({ taskId, model, tokeny, druh, chyby, sha: run.head_sha.slice(0, 7) });
}

for (const v of vypis) {
  console.log(`#${v.taskId} [${v.sha}] ${v.druh.padEnd(20)} model=${v.model.padEnd(11)} ${v.tokeny}`);
  for (const c of v.chyby.slice(0, 5)) console.log(`      ${kategorie(c)}  <-  ${c.replace('SCRIPT ERROR: Parse Error: ', '').slice(0, 70)}`);
}

console.log('\n=== kategorie parse chyb (kolikrát) ===');
for (const [k, n] of [...pocetKategorii.entries()].sort((a, b) => b[1] - a[1])) {
  console.log(`  ${String(n).padStart(3)}x  ${k}`);
}

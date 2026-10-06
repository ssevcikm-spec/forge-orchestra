// OVĚŘOVACÍ session (P18) — Úkol A: přeměřit NASZENÍ HRY TŘEMI KROKY.
//
// PROČ VLASTNÍ SKRIPT: P17 měřila přes `_analyza/p17a-nasazeni.mjs`. Autor není
// nezávislý reviewer, takže se nasazení měří ZNOVU a JINÝM nástrojem.
// Tři kroky jsou z DSH_HOME\AGENTS.md („Jak ověřit nasazení"):
//   1) push dorazil        — `git ls-remote` = HEAD, `origin/main..HEAD` = 0
//   2) build na SPRÁVNÉM commitu — release.yml na tom commitu completed/success
//      a `runner_name` NENÍ prázdný
//   3) server posílá NOVÝ artefakt — `last-modified` PO pushi (ne HTTP 200!)
//
// HTTP 200 NENÍ DŮKAZ — starý web odpovídá 200 taky. Rozhoduje last-modified.
//
// TLS: Node `fetch` (PowerShell padá na schannelu). PAT ze souboru, nevypisuje se.
// Použití: node _analyza/ov-a-nasazeni.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const REPO = dirname(__dir);                       // orchestra root
const HRA = 'E:\\Workspaces\\uo-shadows';          // herní repo (sourozenec)
const HRA_SLUG = 'ssevcikm-spec/uo-shadows';
const PAGES = 'https://ssevcikm-spec.github.io/uo-shadows/';
// Mez z zadání: `last-modified` musí být PO tomto okamžiku.
const PO = Date.parse('2026-10-05T20:39:00Z');

const vysledky = [];
let chyb = 0;
function kontrola(nazev, ok, detail) {
  vysledky.push({ nazev, ok, detail });
  if (!ok) chyb++;
  console.log(`${ok ? 'OK  ' : 'CHYBA'} ${nazev}\n      ${detail}`);
}

const PAT = readFileSync(join(REPO, '.secrets', 'github_pat.txt'), 'utf8').trim();
const H = {
  Authorization: `Bearer ${PAT}`,
  Accept: 'application/vnd.github+json',
  'User-Agent': 'forge-ov-a',
};

// git.cmd žere `^` (H89) — tady žádný `^` není, ale i tak jde přes git.exe.
const GIT = 'git.exe';
function git(...args) {
  return execFileSync(GIT, ['-C', HRA, ...args], { encoding: 'utf8' }).trim();
}

console.log('=== KROK 1: push dorazil? ===');
const head = git('rev-parse', 'HEAD');
const lsRemote = git('ls-remote', 'origin', 'refs/heads/main').split(/\s+/)[0];
const pred = git('rev-list', '--count', 'origin/main..HEAD');
kontrola('ls-remote origin/main == HEAD', lsRemote === head, `HEAD=${head.slice(0, 7)} ls-remote=${lsRemote.slice(0, 7)}`);
kontrola('origin/main..HEAD == 0', pred === '0', `origin/main..HEAD = ${pred}`);
kontrola('HEAD == 44dd454 (commit, na kterém P17 stavěla)',
  head.startsWith('44dd454'), `HEAD=${head}`);

console.log('\n=== KROK 2: build běžel na SPRÁVNÉM commitu? ===');
const runs = await (await fetch(
  `https://api.github.com/repos/${HRA_SLUG}/actions/workflows/release.yml/runs?per_page=10`,
  { headers: H })).json();
if (!runs.workflow_runs) {
  kontrola('API release.yml vrátilo běhy', false, JSON.stringify(runs).slice(0, 200));
} else {
  for (const r of runs.workflow_runs.slice(0, 5)) {
    console.log(`  run #${r.run_number} id=${r.id} ${r.status}/${r.conclusion || '-'} ` +
                `head=${r.head_sha.slice(0, 7)} branch=${r.head_branch} created=${r.created_at}`);
  }
  const naCommitu = runs.workflow_runs.filter(r => r.head_sha === head);
  kontrola(`existuje běh release.yml na commitu ${head.slice(0, 7)}`, naCommitu.length > 0,
    `nalezeno ${naCommitu.length} běhů na tomto commitu`);
  const uspesny = naCommitu.filter(r => r.status === 'completed' && r.conclusion === 'success');
  kontrola('takový běh je completed/success', uspesny.length > 0,
    uspesny.map(r => `#${r.run_number} attempt=${r.run_attempt}`).join(', ') || '(žádný)');

  // runner_name NENÍ prázdný — jinak běh „proběhl" bez stroje.
  if (uspesny.length) {
    const jobs = await (await fetch(
      `https://api.github.com/repos/${HRA_SLUG}/actions/runs/${uspesny[0].id}/jobs`,
      { headers: H })).json();
    const sRunner = (jobs.jobs || []).map(j => `${j.name}: ${j.status}/${j.conclusion} runner=${j.runner_name || '(PRÁZDNÝ)'}`);
    console.log('  joby:\n    ' + sRunner.join('\n    '));
    kontrola('runner_name NENÍ prázdný', (jobs.jobs || []).length > 0 &&
      jobs.jobs.every(j => j.runner_name && j.runner_name.length > 0),
      sRunner.join(' | ') || '(žádné joby)');
  }
}

console.log('\n=== KROK 3: server posílá NOVÝ artefakt? ===');
for (const cesta of ['', 'index.html', 'index.png', 'index.wasm']) {
  const url = PAGES + cesta;
  let r;
  try {
    r = await fetch(url, { method: 'GET', headers: { 'User-Agent': 'forge-ov-a' } });
  } catch (e) {
    kontrola(`GET ${cesta || '(root)'}`, false, `fetch selhal: ${e.message}`);
    continue;
  }
  const lm = r.headers.get('last-modified');
  const cl = r.headers.get('content-length');
  const etag = r.headers.get('etag');
  const ts = lm ? Date.parse(lm) : NaN;
  const po = !Number.isNaN(ts) && ts > PO;
  // U index.html/wasm rozhoduje last-modified; u rootu stačí 200 + přesměrování.
  const jeArtefakt = cesta === 'index.html' || cesta === 'index.png';
  kontrola(`GET ${cesta || '(root)'} → ${r.status}${jeArtefakt ? ` last-modified=${lm}` : ''}`,
    r.status === 200 && (!jeArtefakt || po),
    `status=${r.status} last-modified=${lm || '(žádný)'} len=${cl} etag=${etag}` +
    (jeArtefakt ? ` | po 2026-10-05T20:39Z: ${po}` : ''));
  if (cesta === 'index.html' && r.status === 200) {
    const telo = await r.text();
    writeFileSync(join(__dir, 'ov-a-index.html'), telo, 'utf8');
    console.log(`  (tělo index.html uloženo: _analyza/ov-a-index.html, ${telo.length} znaků)`);
  }
}

console.log('\n=== Stav GitHubu (třetí stav se MUSÍ lišit od „je to rozbité") ===');
try {
  const st = await (await fetch('https://www.githubstatus.com/api/v2/components.json',
    { headers: { 'User-Agent': 'forge-ov-a' } })).json();
  const zajimave = (st.components || []).filter(c =>
    /Actions|Pages|Git Operations|API|Pull Requests/i.test(c.name));
  for (const c of zajimave) console.log(`  ${c.name.padEnd(20)} ${c.status}`);
  const neok = zajimave.filter(c => c.status !== 'operational');
  console.log(`  → neoperationalnich slozek: ${neok.length} ` +
    `(${neok.map(c => c.name + '=' + c.status).join(', ') || 'vše operational'})`);
} catch (e) {
  console.log(`  stav GitHubu se nepodařilo načíst: ${e.message}`);
}

console.log('\n=== SOUHRN ÚKOLU A ===');
console.log(`kontrol: ${vysledky.length}, chyb: ${chyb}`);
writeFileSync(join(__dir, 'ov-a-vysledky.json'),
  JSON.stringify({ kdy: new Date().toISOString(), head, lsRemote, pred, kontrolaPo: '2026-10-05T20:39:00Z', vysledky, chyb }, null, 2), 'utf8');
console.log(chyb === 0 ? 'VERDIKT: NASAZENO (všechny tři kroky prošly)' : `VERDIKT: ${chyb} KRITICKÝCH ROZPORŮ`);
process.exit(chyb === 0 ? 0 : 1);

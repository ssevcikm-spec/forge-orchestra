// ROZHODOVACÍ session (P19) — Úkol A: ověření TOHOTO pushu (orchestra) třemi kroky.
//
// PROČ VLASTNÍ SKRIPT: P18 měřila nasazení HRY (`ov-a-nasazeni.mjs`). Tenhle push
// je ale jiný objekt: pushuje se ORCHESTRA, a ta žádnou webovou stránku nemá.
// Tři kroky z DSH_HOME\AGENTS.md se proto musí namapovat poctivě:
//   1) push dorazil            — ls-remote == HEAD, origin/main..HEAD == 0
//   2) build na SPRÁVNÉM commitu — a tady je odpověď „žádný build se nespouští“,
//      která se musí DOKÁZAT: `deploy.yml` má filtr `paths: conductor/**`
//      a diff pushnutých commitů má v `conductor/` NULA souborů.
//      ⚠ Aby to nebylo tiché: jako POZITIVNÍ KONTROLA se ověří, že API vůbec
//      nějaké běhy orchestry vrací (jinak by „žádný běh na HEAD“ mohlo být
//      jen prázdné API).
//   3) server posílá artefakt   — publikovaný obsah se TIMTO pushem nezměnil
//      (diff nemá `repo/**` ani nic, z čeho se staví web), takže se ověří, že
//      artefakt hry je POŘÁD ten z 44dd454 — a že hra je na 44dd454 i teď.
//
// HTTP 200 NENÍ DŮKAZ. TLS: Node `fetch` (PowerShell padá na schannelu).
// PAT ze souboru, do výstupu se nedostane.
// Použití: node _analyza/p19-a-push-overeni.mjs

import { readFileSync, writeFileSync } from 'node:fs';
import { execFileSync } from 'node:child_process';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const __dir = dirname(fileURLToPath(import.meta.url));
const REPO = dirname(__dir);
const HRA = 'E:\\Workspaces\\uo-shadows';
const ORCH_SLUG = 'ssevcikm-spec/forge-orchestra';
const HRA_SLUG = 'ssevcikm-spec/uo-shadows';
const PAGES_HRA = 'https://ssevcikm-spec.github.io/uo-shadows/';
// Kotva měření: commit, ze kterého se pushovalo (stav PŘED pushem).
const PRED = 'ce49234';
// Publikovaný artefakt hry, jak ho naměřila P18 (nesmí se změnit, když se
// nepushovalo do hry).
const ARTEFAKT_P18 = 'Mon, 05 Oct 2026 21:38:16 GMT';

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
  'User-Agent': 'forge-p19-a',
};
// git.cmd žere `^` (H89) — proto git.exe přímo a jen `~1`, žádné `^`.
function git(repo, ...args) {
  return execFileSync('git.exe', ['-C', repo, ...args], { encoding: 'utf8' }).trim();
}

console.log('=== KROK 1: push dorazil? ===');
const head = git(REPO, 'rev-parse', 'HEAD');
const lsRemote = git(REPO, 'ls-remote', 'origin', 'refs/heads/main').split(/\s+/)[0];
const pred = git(REPO, 'rev-list', '--count', 'origin/main..HEAD');
const rozsah = git(REPO, 'log', '--oneline', `${PRED}..HEAD`).split('\n');
kontrola('ls-remote origin/main == HEAD (živě, ne tracking ref)',
  lsRemote === head, `HEAD=${head.slice(0, 7)} ls-remote=${lsRemote.slice(0, 7)}`);
kontrola('origin/main..HEAD == 0', pred === '0', `origin/main..HEAD = ${pred}`);
kontrola(`pushnuto 6 commitů nad ${PRED}`, rozsah.length === 6,
  `${rozsah.length} commitů: ${rozsah.map(r => r.split(' ')[0]).join(' ')}`);
// Pozitivní kontrola na měřidlo: `PRED` musí být SKUTEČNĚ jiný commit (H89).
const rodic = git(REPO, 'rev-parse', '--short', `${PRED}~1`);
kontrola('kotva měření je ověřená přes `~1` (ne `^`)', rodic !== PRED,
  `${PRED}~1 = ${rodic} (kdyby vyšlo ${PRED}, bylo by to o měřidle)`);

console.log('\n=== KROK 2: běžel build na SPRÁVNÉM commitu? ===');
// (a) Co push změnil — měřeno z gitu, ne z yaml.
const zmenene = git(REPO, 'diff', '--name-only', `${PRED}..HEAD`).split('\n').filter(Boolean);
const conductor = zmenene.filter(f => f.startsWith('conductor/'));
kontrola('push se NEDOTKL conductor/** (filtr deploy.yml)', conductor.length === 0,
  `conductor/** = ${conductor.length} souborů z ${zmenene.length} změněných`);
// (b) Filtr se čte ze SKUTEČNÉHO souboru, ne z předpokladu.
const deployYml = readFileSync(join(REPO, '.github', 'workflows', 'deploy.yml'), 'utf8');
const maFiltr = /paths:\s*[\s\S]{0,80}conductor\/\*\*/.test(deployYml);
kontrola('deploy.yml skutečně filtruje na conductor/**', maFiltr,
  `nalezen filtr: ${(deployYml.match(/paths:[\s\S]{0,60}/) || ['(žádný)'])[0].replace(/\n/g, ' ')}`);
// (c) POZITIVNÍ KONTROLA: API musí vracet běhy orchestry — jinak je „žádný běh
//     na HEAD“ prázdné API, ne měření.
const oRuns = await (await fetch(
  `https://api.github.com/repos/${ORCH_SLUG}/actions/runs?per_page=10`, { headers: H })).json();
if (!oRuns.workflow_runs) {
  kontrola('API orchestry vrací běhy (pozitivní kontrola)', false,
    JSON.stringify(oRuns).slice(0, 200));
} else {
  console.log(`  běhů orchestry v API: ${oRuns.total_count} (celkem v repu)`);
  for (const r of oRuns.workflow_runs.slice(0, 5)) {
    console.log(`    #${r.run_number} ${r.name} ${r.status}/${r.conclusion || '-'} ` +
                `head=${r.head_sha.slice(0, 7)} ${r.created_at}`);
  }
  kontrola('API orchestry vrací běhy (pozitivní kontrola)', oRuns.workflow_runs.length > 0,
    `${oRuns.workflow_runs.length} běhů v odpovědi`);
  const naHead = oRuns.workflow_runs.filter(r => r.head_sha === head);
  kontrola('na tomto commitu NEBĚŽÍ žádný workflow (a je to správně)', naHead.length === 0,
    naHead.map(r => `#${r.run_number} ${r.name} ${r.status}`).join(', ') ||
    `0 běhů s head_sha=${head.slice(0, 7)} — protože conductor/** se nezměnil`);
}
// (d) Nasazení, které na tom ZÁLEŽÍ (hra) — musí pořád platit.
const hRuns = await (await fetch(
  `https://api.github.com/repos/${HRA_SLUG}/actions/workflows/release.yml/runs?per_page=5`,
  { headers: H })).json();
const hHead = git(HRA, 'rev-parse', 'HEAD');
const hPred = git(HRA, 'rev-list', '--count', 'origin/main..HEAD');
kontrola('hra je v sync (nic k pushi)', hPred === '0', `origin/main..HEAD = ${hPred}`);
if (hRuns.workflow_runs) {
  const naHHead = hRuns.workflow_runs.filter(r => r.head_sha === hHead);
  const ok = naHHead.filter(r => r.status === 'completed' && r.conclusion === 'success');
  kontrola('release.yml na commitu hry je completed/success', ok.length > 0,
    ok.map(r => `#${r.run_number} attempt=${r.run_attempt} ${r.created_at}`).join(', ') ||
    '(žádný)');
  if (ok.length) {
    const jobs = await (await fetch(
      `https://api.github.com/repos/${HRA_SLUG}/actions/runs/${ok[0].id}/jobs`,
      { headers: H })).json();
    const j = (jobs.jobs || []).map(x => `${x.name}: ${x.status}/${x.conclusion} runner=${x.runner_name || '(PRÁZDNÝ)'}`);
    kontrola('runner_name NENÍ prázdný', (jobs.jobs || []).length > 0 &&
      jobs.jobs.every(x => x.runner_name), j.join(' | ') || '(žádné joby)');
  }
}

console.log('\n=== KROK 3: server posílá artefakt — a má se vůbec změnit? ===');
// Publikuje se jen z herního repa; orchestra žádné Pages nemá (kontrola níž).
// ⚠ POZOR (omyl 186, naměřeno tady): v TĚLE odpovědi je `status` ŘETĚZEC
// ("404"), kdežto HTTP stav je číslo. Porovnání `body.status === 404` je proto
// VŽDY nepravdivé — a vypadá to jako nález o cizím repu. Autorita je HTTP stav.
const orchPagesR = await fetch(`https://api.github.com/repos/${ORCH_SLUG}/pages`, { headers: H });
const orchPages = await orchPagesR.json();
kontrola('orchestra NEMÁ Pages (třetí krok se ho netýká)', orchPagesR.status === 404,
  `GET /repos/${ORCH_SLUG}/pages → HTTP ${orchPagesR.status}` +
  ` (tělo: status="${orchPages.status}" ${orchPages.message || orchPages.html_url || ''})`);
for (const cesta of ['', 'index.html', 'index.png']) {
  const r = await fetch(PAGES_HRA + cesta, { headers: { 'User-Agent': 'forge-p19-a' } });
  const lm = r.headers.get('last-modified');
  const jeArtefakt = cesta === 'index.html' || cesta === 'index.png';
  kontrola(`GET ${cesta || '(root)'} → ${r.status}${jeArtefakt ? ` last-modified=${lm}` : ''}`,
    r.status === 200 && (!jeArtefakt || lm === ARTEFAKT_P18),
    jeArtefakt
      ? `last-modified=${lm} | P18 naměřila ${ARTEFAKT_P18} → ${lm === ARTEFAKT_P18 ? 'NEOVLIVNĚNO (správně: do hry se nepushovalo)' : 'ZMĚNA — pozor'}`
      : `status=${r.status}`);
}

console.log('\n=== SOUHRN ÚKOLU A ===');
console.log(`kontrol: ${vysledky.length}, chyb: ${chyb}`);
writeFileSync(join(__dir, 'p19-a-push-vysledky.json'),
  JSON.stringify({ kdy: new Date().toISOString(), head, lsRemote, pred,
    rozsah: rozsah.map(r => r.split(' ')[0]), zmeneneSouboru: zmenene.length,
    conductorZmen: conductor.length, vysledky, chyb }, null, 2), 'utf8');
console.log(chyb === 0
  ? 'VERDIKT: PUSH DORAZIL; build se nespouští (conductor/** se nezměnil) a artefakt hry je neovlivněný'
  : `VERDIKT: ${chyb} KRITICKÝCH ROZPORŮ`);
process.exit(chyb === 0 ? 0 : 1);

// A3 — ověření, že PUSH orchestra dorazil a NASADIL SE (deploy conductora).
//
// PROČ VLASTNÍ SKRIPT: `validate-all.mjs` kontroluje deploy, ale spouští se
// ručně a ptá se na „poslední deploy" bez vztahu k právě pushnutému commitu.
// Tady se ptáme na KONKRÉTNÍ commit (be41964) — jinak by zelená mohla být
// z deploye, který proběhl před pushem.
//
// Použití: node _analyza/a3-kontrola.mjs [<sha>]
import { readFileSync } from 'node:fs';

const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';
const ORCHREPO = 'ssevcikm-spec/forge-orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'a3-kontrola' };
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const cekany = process.argv[2] || null;
const gh = async (p) => { const r = await fetch(`https://api.github.com${p}`, { headers: H }); return r.ok ? r.json() : { chyba: r.status }; };
const cond = async (p) => { const r = await fetch(`${env.FORGE_URL}${p}`, { headers: { 'x-forge-secret': env.FORGE_SECRET } }); return r.ok ? r.json() : { chyba: r.status }; };

let chyb = 0;
const test = (n, ok, d = '') => { if (!ok) chyb++; console.log(`  ${ok ? 'OK  ' : 'CHYBA'} ${n}${d ? '  — ' + d : ''}`); };

console.log('════ A. PUSH DORAZIL ════');
const hlavni = await gh(`/repos/${ORCHREPO}/commits/main`);
const shaMain = hlavni.sha;
console.log(`  GitHub main = ${shaMain?.slice(0, 9)}  (${hlavni.commit?.message?.split('\n')[0]?.slice(0, 60)})`);
if (cekany) test('GitHub main = očekávaný commit', shaMain === cekany, `${shaMain?.slice(0, 9)} vs ${cekany.slice(0, 9)}`);

console.log('\n════ B. DEPLOY CONDUCTORA NA TOM COMMITU ════');
const behy = await gh(`/repos/${ORCHREPO}/actions/runs?per_page=30`);
const nas = (behy.workflow_runs || []).filter((x) => /Deploy conductor/i.test(x.name || ''));
for (const r of nas.slice(0, 5)) {
  console.log(`  #${r.run_number} ${r.status}/${r.conclusion || '-'} head:${r.head_sha.slice(0, 9)} ${r.created_at}`);
}
const naMain = nas.find((r) => r.head_sha === shaMain);
// POZOR: deploy má `paths: conductor/**`, takže push, který měnil JEN repo/
// nebo tools/, deploy SPRÁVNĚ nespustí. Hledá se proto poslední deploy, jehož
// commit je tentýž nebo novější než poslední změna conductor/.
const zmenaConductoru = await gh(`/repos/${ORCHREPO}/commits?path=conductor/src/index.ts&per_page=1`);
const shaConductoru = zmenaConductoru[0]?.sha;
console.log(`  poslední změna conductor/src/index.ts = ${shaConductoru?.slice(0, 9)}`);
const posledni = nas[0];
test('existuje deploy se stavem success',
  nas.some((r) => r.conclusion === 'success'),
  posledni ? `#${posledni.run_number} ${posledni.conclusion} head:${posledni.head_sha.slice(0, 9)}` : 'žádný deploy');
const obsahujeKod = nas.some((r) => r.head_sha === shaConductoru && r.conclusion === 'success');
test('kód conductora z main je nasazený (deploy na témž commitu)', obsahujeKod,
  `hledán head:${shaConductoru?.slice(0, 9)}`);
if (naMain) test('deploy proběhl i na dnešním pushi', naMain.conclusion === 'success', `#${naMain.run_number} ${naMain.conclusion}`);
else console.log(`  INFO  na commitu ${shaMain?.slice(0, 9)} deploy neběžel — správně, pokud push nezměnil conductor/**`);

console.log('\n════ C. CO CONDUCTOR TVRDÍ (živý stav) ════');
const h = await cond('/health');
console.log(`  /health  ${JSON.stringify(h)}`);
test('conductor odpovídá', h.ok === true);

const rm = await cond('/roadmap');
const r = rm.roadmap || [];
console.log(`\n  /roadmap: ${r.length} řádků`);
const zajimave = ['world.nodes', 'entity.player.api', 'persist.save.state', 'engine.shell'];
for (const row of r) {
  const kratke = String(row.item_id || '').replace('uo-shadows/', '');
  const znacka = zajimave.includes(kratke) ? '  <<< NOVÁ' : '';
  console.log(`    ${kratke.padEnd(22)} ${String(row.status || '?').padEnd(9)} ${znacka}`);
}

console.log('\n════ D. D1: STAVY ÚLOH NOVÝCH GRANULÍ ════');
// D1 je zdroj pravdy o tom, co conductor OPRAVDU udělal (nejen co si myslí cache).
const tasks = await cond('/tasks');
const seznam = Array.isArray(tasks) ? tasks : (tasks.tasks || []);
for (const g of zajimave) {
  const t = seznam.filter((x) => String(x.item_id || '').includes(g));
  if (!t.length) { console.log(`  ${g.padEnd(22)} (žádná úloha)`); continue; }
  for (const u of t.slice(-3)) console.log(`  ${g.padEnd(22)} id=${u.id} stav=${u.status} pokusů=${u.attempts} run=${String(u.run_key || '').slice(0, 12)}`);
}

console.log(`\n${chyb === 0 ? '✓ VŠE V POŘÁDKU' : `✗ NALEZENO ${chyb} PROBLÉMŮ`}`);
process.exitCode = chyb === 0 ? 0 : 1;

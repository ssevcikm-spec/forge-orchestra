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
//
// ⚠ POZOR — `/tasks` NENÍ ENDPOINT (naměřeno 2. 10. 2026). Vrací HTTP 200
// a ROZCESTNÍK SLUŽBY: `{"service":"forge-conductor","endpoints":[...]}`.
// Původní verze z něj četla `tasks || []`, takže dostala VŽDY prázdné pole
// a u každé granule vypsala „(žádná úloha)" — a vypadalo to jako naměřený
// stav. Úlohy jsou v `/queue`; na granule se mapují přes `/roadmap`
// (`item_id`, `status`, `task_id`), protože `/queue` `item_id` NEOBSAHUJE.
const rq = await cond('/queue');
const fronta = Array.isArray(rq) ? rq : (rq.tasks || []);
const frontaOk = Array.isArray(fronta) && fronta.length > 0;
const rmap = new Map();
for (const row of r) rmap.set(String(row.item_id || '').replace('uo-shadows/', ''), row);
console.log(`  /queue vrátil ${fronta.length} úloh, /roadmap ${r.length} řádků`);
if (!frontaOk) {
  // Nula a nezměřeno nejsou úspěch: musí to být vidět (AGENTS.md).
  console.log(`  CHYBA /queue nevrátil parsovatelný seznam úloh: ${JSON.stringify(rq).slice(0, 200)}`);
  chyb++;
}
for (const g of zajimave) {
  const row = rmap.get(g);
  if (!row) { console.log(`  ${g.padEnd(22)} v /roadmap NENÍ (granule ještě není založená)`); continue; }
  const tid = row.task_id;
  if (tid === null || tid === undefined) {
    console.log(`  ${g.padEnd(22)} roadmap=${row.status}  task_id=null (úloha se ještě nezaložila)`);
    continue;
  }
  const u = fronta.find((x) => Number(x.id) === Number(tid));
  if (!u) {
    console.log(`  ${g.padEnd(22)} roadmap=${row.status}  task_id=${tid} — v /queue NENÍ (fronta ${fronta.length} úloh)`);
    continue;
  }
  console.log(`  ${g.padEnd(22)} roadmap=${row.status}  úloha #${u.id} stav=${u.status} pokusů=${u.attempts}`);
}

console.log(`\n${chyb === 0 ? '✓ VŠE V POŘÁDKU' : `✗ NALEZENO ${chyb} PROBLÉMŮ`}`);
process.exitCode = chyb === 0 ? 0 : 1;

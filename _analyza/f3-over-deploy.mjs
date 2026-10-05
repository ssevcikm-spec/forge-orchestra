// Ověření, že se B1 SKUTEČNĚ NASADIL (ne jen pushnul).
//
// Dvě věci se musí potvrdit zvlášť (AGENTS.md, „Jak ověřit nasazení"):
//   1. push dorazil            -> `rev-list --count origin/main..HEAD` = 0 (dělá PowerShell)
//   2. workflow běžel na TOM commitu a skončil success
// Třetí krok z AGENTS.md (`last-modified`) je pro GitHub Pages u hry, ne pro
// Cloudflare Workera — tady místo něj je živý test funkce (viz níže).
//
// Použití: node _analyza/f3-over-deploy.mjs [<sha>]
import { readFileSync } from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

// ⚠ P13c (4. 10. 2026): tady stálo
//   `const ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra';`
// — tedy cesta ze STARÉHO layoutu. Po přesunu na `E:` tam `.secrets/github_pat.txt`
// NENÍ, `readFileSync` spadl **ještě před prvním testem** a v přehledu bran to
// vypadalo jako „deploy je červený" (nález H48). Cesta se odvozuje z umístění
// tohohle souboru (`_analyza/..` = kořen repa orchestra).
const ORCH = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const REPO = 'ssevcikm-spec/forge-orchestra';
const PAT = readFileSync(`${ORCH}/.secrets/github_pat.txt`, 'utf8').trim();
const H = { Authorization: `Bearer ${PAT}`, Accept: 'application/vnd.github+json', 'User-Agent': 'f3-over-deploy' };
const env = Object.fromEntries(
  readFileSync(`${ORCH}/.env`, 'utf8').split('\n').filter((l) => l.includes('='))
    .map((l) => { const i = l.indexOf('='); return [l.slice(0, i).trim(), l.slice(i + 1).trim()]; })
);

const cekany = process.argv[2] || null;
const cekanyNorm = cekany ? cekany.slice(0, 7).toLowerCase() : null;
let chyb = 0;
const test = (n, ok, d = '') => { if (!ok) chyb++; console.log(`  ${ok ? 'OK  ' : 'CHYBA'} ${n}${d ? '  — ' + d : ''}`); };

const gh = async (p) => {
  const r = await fetch(`https://api.github.com${p}`, { headers: H });
  return r.ok ? r.json() : { chyba: r.status };
};

console.log('════ A. DEPLOY WORKFLOW ORCHESTRA ════');
const hlavni = await gh(`/repos/${REPO}/commits/main`);
const shaMain = hlavni.sha;
console.log(`  GitHub main = ${shaMain?.slice(0, 9)}  (${hlavni.commit?.message?.split('\n')[0]?.slice(0, 60)})`);
// POZOR: `shaMain` je PLNÉ sha, `cekany` je krátké (7 znaků) — porovnává se
// proto prefix. První verze porovnávala celé řetězce a hlásila falešný poplach
// na správném commitu (a ten pak zakryl skutečný stav deploye).
// POZOR (opraveno 2. 10. 2026): `cekany` NENÍ „aktuální HEAD main" — je to
// **commit, na kterém má běžet deploy**, tedy poslední změna `conductor/**`.
// Původní verze porovnávala `cekany` s HEADem main, a když pozdější push změnil
// jen `tools/`, hlásila `CHYBA GitHub main = očekávaný commit` — **falešný
// poplach na správném stavu** (naměřeno: `1e3925e2c vs 7c11b2d`).
// Nově se ptáme na **poslední změnu conductor/**, stejně jako `a3-kontrola.mjs`.
const zmenaConductoru = await gh(`/repos/${REPO}/commits?path=conductor/src/index.ts&per_page=1`);
const shaConductoru = zmenaConductoru[0]?.sha;
console.log(`  poslední změna conductor/src/index.ts = ${shaConductoru?.slice(0, 9)}`);
// `messageHead` se používá níž v hlášce; drží se, aby výpis zůstal čitelný.
const messageHead = hlavni.commit?.message?.split('\n')[0];
void messageHead;

const behy = await gh(`/repos/${REPO}/actions/runs?per_page=20`);
const nas = (behy.workflow_runs || []).filter((x) => /Deploy conductor/i.test(x.name || ''));
for (const r of nas.slice(0, 5)) {
  console.log(`  #${r.run_number} ${r.status}/${r.conclusion || '-'} head:${r.head_sha.slice(0, 9)} ${r.created_at}`);
}
// Hledá se deploy na **poslední změně conductor/** — ne na HEADu main.
const naCommitu = nas.find((r) => r.head_sha === shaConductoru);
test('kód conductora z main JE nasazený (deploy na poslední změně conductor/)',
  !!naCommitu && naCommitu.conclusion === 'success',
  naCommitu ? `#${naCommitu.run_number} success head:${naCommitu.head_sha.slice(0, 9)}`
            : `na ${shaConductoru?.slice(0, 9)} žádný deploy`);
// A když uživatel zadal konkrétní sha, ověří se, že na NĚM deploy opravdu byl
// (to je původní smysl parametru — „B1 musí být nasazené").
if (cekanyNorm) {
  const naZadanem = nas.find((r) => r.head_sha.toLowerCase().startsWith(cekanyNorm));
  test(`deploy běžel na zadaném commitu ${cekany.slice(0, 9)}`,
    !!naZadanem && naZadanem.conclusion === 'success',
    naZadanem ? `#${naZadanem.run_number} ${naZadanem.conclusion}` : 'žádný deploy na tom commitu');
}

console.log('\n════ B. ŽIVÝ CONDUCTOR (běží nasazený kód?) ════');
const r = await fetch(`${env.FORGE_URL}/health`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
const h = await r.json().catch(() => ({}));
test('conductor odpovídá', h.ok === true, JSON.stringify(h).slice(0, 160));

const rq = await fetch(`${env.FORGE_URL}/queue`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
const q = await rq.json().catch(() => ({}));
const fronta = Array.isArray(q) ? q : (q.tasks || []);
const rmap = await fetch(`${env.FORGE_URL}/roadmap`, { headers: { 'x-forge-secret': env.FORGE_SECRET } });
const m = await rmap.json().catch(() => ({}));
const radky = m.roadmap || [];
console.log(`  /queue ${fronta.length} úloh, /roadmap ${radky.length} řádků`);
test('/queue vrací seznam úloh', fronta.length > 0, `${fronta.length}`);

// S12: nová granule (nikdy neselhala) NESMÍ být v cooldownu.
// `updated_at` je i čas vzniku, `naposledy_selhalo` je NULL — a právě na tom
// rozdílu stojí celý B1. Před B1 by obě granule zůstaly `ready` a NEBYLY by se
// vydaly (guard je držel v cooldownu); po B1 je worker okamžitě vezme.
//
// POZOR na správné kritérium: stav NENÍ „musí být ready" — správný výsledek je
// i `running`, protože worker je bere během sekund. Co se měřit MÁ, je to, že
// úloha NENÍ zaseknutá ve `failed` a že má pokusy (tedy že se vydala).
for (const g of ['world.nodes', 'entity.player.api']) {
  const row = radky.find((x) => String(x.item_id || '').endsWith(g));
  if (!row) { console.log(`  ?    ${g}: v /roadmap není`); continue; }
  const u = fronta.find((x) => Number(x.id) === Number(row.task_id));
  console.log(`  ${g.padEnd(20)} roadmap=${row.status} task_id=${row.task_id} `
    + `úloha ${u ? `#${u.id} stav=${u.status} pokusů=${u.attempts}` : '(v /queue není)'}`);
  if (u) {
    test(`${g}: VYDALA SE (není v cooldownu S12)`,
      u.status !== 'failed' && (u.status === 'running' || Number(u.attempts) >= 0),
      `stav=${u.status} pokusů=${u.attempts}`);
  }
}

// ⚠ P13c (4. 10. 2026): čítač se MUSÍ vytisknout na KONCI. `g3-brany.py` bere
// u vzoru **POSLEDNÍ** výskyt (nález NA23), takže číslo ze středu výpisu
// (`/queue 50 úloh`) se do sloupce `otevřela:` nedostalo a brána vypadala jako
// „neměřila nic" (past S27).
console.log(`ZMĚŘENO: ${fronta.length} úloh ve frontě, ${radky.length} řádků roadmapy, `
  + `${chyb} problémů`);
console.log(`\n${chyb === 0 ? '✓ VŠE V POŘÁDKU' : `✗ NALEZENO ${chyb} PROBLÉMŮ`}`);
process.exitCode = chyb === 0 ? 0 : 1;

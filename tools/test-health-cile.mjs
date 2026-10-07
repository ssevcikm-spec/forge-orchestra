// Offline test pro N0.3 — „/health musí hlásit stav CÍLE, ne jen že služba žije".
//
// PROČ TENHLE TEST EXISTUJE
// -------------------------
// Naměřeno 1. 10. 2026 (S18): conductor hlásil `ok: true`, `/failed` prázdné,
// a přesto 7,5 h nevydal ani granuli — protože `main` cílové hry měl červené CI.
// Naměřeno ZNOVU 6. 10. 2026 (tatáž třída, jiná příčina): od 5. 10. 22:02
// selhalo 9 běhů v řadě a `/health` pořád hlásilo `ok: true`; fronta se přitom
// točila na dvou granulích, které ani jednou neprošly.
//
// JAK TO TESTOVÁ (a proč je to důvěryhodné)
// -----------------------------------------
// Conductor se NEOPISUJE. Test si nechá `conductor/src/index.ts` ZBUNDLOVAT
// skutečným `wrangler deploy --dry-run` (bez sítě a bez přihlášení — nic se
// nenasadí) a pak zavolá SKUTEČNÝ handler `default.fetch('/health')`
// s falešnou D1 a stubovaným GitHub API. Měří tedy tutéž cestu, kterou běží
// živá služba — ne její kopii.
//
// Test má assert i nenulový exit kód. Bez toho by „zelený" nic neznamenal
// (naměřeno: `test-cooldown.py` vypisoval CHYBA a končil s exit 0).
//
// CO TEST TVRDÍ (a co by ho shodilo):
//   1. stav CI cíle (`main_ci`) se v /health OPRAVDU objeví — ne jen že funkce
//      existuje (to je past „brána se ptá na přítomnost, ne na chování"),
//   2. `forge.ok` je `false` při selhaném posledním běhu a `null`, když běhy
//      nejsou — „nezměřeno" se NESMÍ číst jako „v pořádku",
//   3. `selhani_v_rade` počítá souvislou řadu selhání (dnes 9),
//   4. když GitHub neodpoví, je to VIDĚT (`error` + `null`), ne ticho,
//   5. dotazuje se repa AKTIVNÍ hry (ne `GITHUB_REPO` z env),
//   6. cache drží (druhý dotaz v TTL nevolá GitHub znovu),
//   7. `ok` zůstává „služba žije" — N0.3 nesmí rozbít monitoring dostupnosti.

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(HERE); // tools/ -> koren repa
const CONDUCTOR = join(ORCH, 'conductor');
const SCRATCH = join(ORCH, '_analyza', 'n03-scratch');
const BUNDLE = join(SCRATCH, 'index.js');

let checks = 0;
let errors = 0;

function check(desc, actual, expected) {
  checks++;
  const a = JSON.stringify(actual);
  const e = JSON.stringify(expected);
  if (a === e) {
    console.log(`  OK    ${desc}`);
  } else {
    errors++;
    console.log(`  CHYBA ${desc}\n        cekano: ${e}\n        dáno:   ${a}`);
  }
}

// ---------------------------------------------------------------- build ----
function build() {
  mkdirSync(SCRATCH, { recursive: true });
  const wrangler = join(CONDUCTOR, 'node_modules', 'wrangler', 'bin', 'wrangler.js');
  if (!existsSync(wrangler)) {
    console.log(`CHYBA: chybi wrangler (${wrangler}) — test nemá čím bundlovat.`);
    process.exit(1);
  }
  const r = spawnSync(process.execPath,
    [wrangler, 'deploy', '--dry-run', '--outdir', SCRATCH],
    { cwd: CONDUCTOR, encoding: 'utf8' });
  if (r.status !== 0) {
    console.log('CHYBA: `wrangler deploy --dry-run` spadl:');
    console.log(String(r.stderr || r.stdout || '').slice(-1500));
    process.exit(1);
  }
  if (!existsSync(BUNDLE)) {
    console.log(`CHYBA: bundle nevznikl (${BUNDLE})`);
    process.exit(1);
  }
}

// ------------------------------------------------------------ fake svet ----
function fakeDb(game) {
  const api = (sql) => ({
    first: async () => {
      if (sql.includes("FROM tasks WHERE status='ready'")) return { n: 1 };
      if (sql.includes("FROM runs WHERE status='running'")) return { n: 0 };
      if (sql.includes('COUNT(*) AS n FROM games')) return { n: 1 };
      return null;
    },
    all: async () => {
      if (sql.includes('FROM workers')) {
        return { results: [{ name: 'oracle-frankfurt', kinds: 'test,build', last_seen: '2026-10-06 21:00:00', minutes_ago: 0 }] };
      }
      if (sql.includes('FROM games WHERE active=1')) return { results: [game] };
      return { results: [] };
    },
    run: async () => ({ meta: { changes: 0 } }),
  });
  return {
    prepare(sql) {
      const a = api(String(sql));
      return { ...a, bind: () => a };
    },
  };
}

function envFor(game) {
  return {
    DB: fakeDb(game),
    GITHUB_TOKEN: 'test-token',
    GITHUB_REPO: 'fallback/nesmi-se-pouzit',
    GITHUB_REF: 'main',
    WORKFLOW_FILE: 'agent.yml',
    CI_WORKFLOW_FILE: 'ci.yml',
    WEBHOOK_SECRET: 'test',
    NTFY_TOPIC: 'test',
  };
}

const game = (repo) => ({ game_id: 'uo-shadows', repo, roadmap_file: '.forge/roadmap.json', active: 1 });

function jsonResponse(data) {
  return new Response(JSON.stringify(data), { status: 200, headers: { 'content-type': 'application/json' } });
}

// Stub GitHubu: zaznamená URL a vrátí připravené odpovědi. Neznámá URL = chyba
// (kdyby /health začal volat něco jiného, test to musí vidět).
function stubGithub(plan, calls) {
  globalThis.fetch = async (url) => {
    const u = String(url);
    calls.push(u);
    if (plan.reject) throw new Error(plan.reject);
    if (u.includes('/actions/workflows/ci.yml/runs')) return jsonResponse(plan.ci);
    if (u.includes('/actions/workflows/agent.yml/runs')) return jsonResponse(plan.agent);
    throw new Error(`necekana URL: ${u}`);
  };
}

const run = (n, conclusion, created = '2026-10-06T19:37:00Z') => ({
  run_number: n, status: 'completed', conclusion, created_at: created,
  head_sha: 'deadbeef', html_url: `https://github.com/x/y/actions/runs/${n}`,
});

async function health(mod, env) {
  const res = await mod.default.fetch(new Request('https://conductor.test/health'), env);
  return { status: res.status, body: await res.json() };
}

// ---------------------------------------------------------------- main ----
const vysledky = [];

async function main() {
  console.log('=== N0.3: stav cíle v /health ===');
  build();
  // Cache v modulu přežívá mezi importy téhož souboru → cache-bust, ať každý
  // scénář začíná na čistém stavu.
  const mod = await import(`${pathToFileURL(BUNDLE).href}?v=${Date.now()}`);

  // --- A) cíl je mrtvý: CI failure + tři běhy agenta v řadě failure ---------
  {
    const calls = [];
    stubGithub({
      ci: { workflow_runs: [run(117, 'failure')] },
      agent: { workflow_runs: [run(313, 'failure'), run(312, 'failure'), run(311, 'failure'), run(310, 'success')] },
    }, calls);
    const env = envFor(game('test/hra-a'));
    const { status, body } = await health(mod, env);
    const t = (body.targets || [])[0] || {};
    check('A: HTTP 200', status, 200);
    check('A: `ok` zůstává „služba žije"', body.ok, true);
    check('A: /health publikuje právě jeden cíl', (body.targets || []).length, 1);
    check('A: main_ci.conclusion = failure (to je „Hotovo znamená" N0.3)', t.main_ci?.conclusion, 'failure');
    check('A: forge.ok = false', t.forge?.ok, false);
    check('A: forge.selhani_v_rade = 3', t.forge?.selhani_v_rade, 3);
    check('A: chyba není (stav JE naměřen)', t.error, null);
    check('A: ptá se repa aktivní hry, ne GITHUB_REPO',
      calls.length === 2 && calls.every((u) => u.includes('test/hra-a')) && !calls.some((u) => u.includes('fallback/nesmi-se-pouzit')), true);
    check('A: ptá se na oba workflows (ci.yml i agent.yml)',
      calls.some((u) => u.includes('/workflows/ci.yml/runs')) && calls.some((u) => u.includes('/workflows/agent.yml/runs')), true);
    vysledky.push(`A: ${JSON.stringify({ main_ci: t.main_ci?.conclusion, forge: t.forge?.ok, vRade: t.forge?.selhani_v_rade })}`);
  }

  // --- B) cíl je zdravý -----------------------------------------------------
  {
    const calls = [];
    stubGithub({
      ci: { workflow_runs: [run(118, 'success')] },
      agent: { workflow_runs: [run(320, 'success'), run(319, 'failure')] },
    }, calls);
    const { body } = await health(mod, envFor(game('test/hra-b')));
    const t = (body.targets || [])[0] || {};
    check('B: main_ci.conclusion = success', t.main_ci?.conclusion, 'success');
    check('B: forge.ok = true', t.forge?.ok, true);
    check('B: selhani_v_rade = 0', t.forge?.selhani_v_rade, 0);
  }

  // --- C) GitHub neodpoví → „nezměřeno" MUSÍ být vidět ----------------------
  {
    const calls = [];
    stubGithub({ reject: 'GitHub 503' }, calls);
    const { body } = await health(mod, envFor(game('test/hra-c')));
    const t = (body.targets || [])[0] || {};
    check('C: main_ci = null (nezměřeno, ne „ok")', t.main_ci, null);
    check('C: forge = null', t.forge, null);
    check('C: error je VYPLNĚNÝ (ticho by vypadalo jako zdraví)', typeof t.error === 'string' && t.error.length > 0, true);
    check('C: `ok` zůstává true — dostupnost služby to nezměnilo', body.ok, true);
  }

  // --- D) běhy existují, ale žádný není dokončený → ok = null, ne true ------
  {
    const calls = [];
    stubGithub({
      ci: { workflow_runs: [] },
      agent: { workflow_runs: [{ run_number: 321, status: 'in_progress', conclusion: null, created_at: '2026-10-06T20:00:00Z', html_url: 'u' }] },
    }, calls);
    const { body } = await health(mod, envFor(game('test/hra-d')));
    const t = (body.targets || [])[0] || {};
    check('D: main_ci = null, když CI běh není', t.main_ci, null);
    check('D: forge.ok = null (nedokončený běh není úspěch)', t.forge?.ok, null);
    check('D: selhani_v_rade = 0', t.forge?.selhani_v_rade, 0);
  }

  // --- E) cache: druhý dotaz v TTL nesmí volat GitHub znovu ----------------
  {
    const calls = [];
    stubGithub({
      ci: { workflow_runs: [run(118, 'success')] },
      agent: { workflow_runs: [run(320, 'success')] },
    }, calls);
    const env = envFor(game('test/hra-e'));
    await health(mod, env);
    const poPrvnim = calls.length;
    await health(mod, env);
    const poDruhem = calls.length;
    check('E: první dotaz = 2 volání GitHubu', poPrvnim, 2);
    check('E: druhý dotaz v TTL = 0 dalších volání (cache drží)', poDruhem, poPrvnim);
  }

  console.log();
  for (const v of vysledky) console.log(`  ${v}`);
  console.log();
  if (errors) {
    console.log(`VYSLEDEK: ${checks} kontrol, ${errors} CHYB`);
    return 1;
  }
  console.log(`VYSLEDEK: ${checks} kontrol, 0 chyb`);
  return 0;
}

process.exit(await main());

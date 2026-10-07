// Offline test ROZHODOVACÍ LOGIKY conductora — volá SKUTEČNÝ `POST /tick`.
//
// PROČ TENHLE TEST EXISTUJE
// -------------------------
// Projekt o sobě sám přiznává: **„Conductor nemá test své rozhodovací logiky.
// Dva `.py` testy logiku OPISUJÍ a `mock-conductor.mjs` neumí `/tick` — když se
// v conductoru změní SQL, neozve se nic."** Naměřeno 6. 10. 2026: i brána `B4`
// kontrolovala `listGames` a guardy jen **staticky** — a „staticky to tam je"
// není totéž jako „tik to neudělá" (dispatch smyčka čte úlohy z D1).
//
// A hlavně: **v `pollRuns` bydlely dvě z nejdražších vad projektu** — B1
// (cooldown se ptal na `updated_at`, takže nová granule se 3 h nevydala)
// a A1 (`done` se zapsalo i u PR, které se NESLOUČILO). Ani jedna neměla test,
// který by zavolal kód; testy je opisovaly.
//
// JAK TO TESTOVÁ (a proč je to důvěryhodné)
// -----------------------------------------
// Conductor se NEOPISUJE: `wrangler deploy --dry-run` ho zbundluje (bez sítě
// a bez přihlášení) a test zavolá **skutečný handler** `default.fetch('/tick')`
// s falešnou D1 a stubovaným GitHub API. Falešná D1 má **router podle SQL**,
// **zapisuje si provedené dotazy** (na nich stojí tvrzení o chování) a na
// NEZNÁMÝ dotaz **spadne** — kdyby conductor začal dělat nový dotaz, test to
// řekne, místo aby tiše měřil něco jiného.
//
// CO TVRDÍ:
//   A) registr bez AKTIVNÍ hry → tik nedispatchuje, roadmapu ani nečte
//   B) aktivní hra + připravená granule → dispatch PRÁVĚ JEDNOU, úloha claimnuta
//   C) jiný běh už běží → `MAX_CONCURRENT` další dispatch nepustí
//   D) **/poll**: běh na GitHubu selhal → úloha zpět na `ready` a **cooldown
//      se zapíše** (`naposledy_selhalo` — vada B1)
//   E) **/poll**: běh uspěl a PR je SLOUČENÝ → úloha i granule `done`
//   F) **/poll**: běh uspěl, ale PR sloučený NENÍ → `awaiting_human`, NE `done`
//      (vada A1: „hotovo" bez práce v `main`)
//   G) **stale-recovery**: zaseknutý běh se ukončí a úloha se vrátí do fronty
//      JEN dokud má pokusy (`attempts < ?`); bez zaseknutých běhů se nesahá na nic
//   H) **/report**: selhání s pokusy → úloha zpět na `ready` a **cooldown se
//      zapíše** (`naposledy_selhalo`), granule se NEoznačí `failed`
//   I) **/report**: poslední pokus → úloha i granule `failed`
//   J) **/report**: úspěch → úloha i granule `done`
//   K) **/report**: neznámý `run_key` → 404 a **žádné zápisy**
//   L) **/report**: špatné tajemství → 401 a **žádné zápisy**
//   M) **/report**: `blocked`/`done` je TERMINÁLNÍ — report ho nesmí vzkřísit

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const HERE = dirname(fileURLToPath(import.meta.url));
const ORCH = dirname(HERE);
const CONDUCTOR = join(ORCH, 'conductor');
const SCRATCH = join(ORCH, '_analyza', 'tick-scratch');
const BUNDLE = join(SCRATCH, 'index.js');

const SECRET = 'tajemstvi-testu';
const GRAIN = { id: 'grain.jedna', title: 'Testovací granule', kind: 'code', prompt: 'neco' };
const RUN_KEY = 'klic-behu-1';

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
    console.log(`CHYBA: chybi wrangler (${wrangler})`);
    process.exit(1);
  }
  const r = spawnSync(process.execPath,
    [wrangler, 'deploy', '--dry-run', '--outdir', SCRATCH],
    { cwd: CONDUCTOR, encoding: 'utf8' });
  if (r.status !== 0 || !existsSync(BUNDLE)) {
    console.log('CHYBA: `wrangler deploy --dry-run` selhal:');
    console.log(String(r.stderr || r.stdout || '').slice(-1500));
    process.exit(1);
  }
}

// ------------------------------------------------------------ fake svet ----
/**
 * Falešná D1: router podle SQL, který si každý dotaz ZAPAMATUJE.
 * Neznámý dotaz = CHYBA (test nesmí tiše měřit něco jiného, než si myslí).
 */
function fakeDb(cfg) {
  const log = [];
  const stav = {
    taskStatus: cfg.taskStatus || 'ready',
    taskClaimed: 0,
    runy: 0,
    bezi: cfg.bezi || 0,
    attempts: cfg.attempts ?? 0,
  };
  const zapis = (sql) => log.push(String(sql).replace(/\s+/g, ' ').trim());

  const first = async (sql) => {
    zapis(sql);
    if (sql.includes("FROM tasks WHERE status='ready'")) return { n: 1 };
    if (sql.includes("FROM runs WHERE status='running'")) return { n: stav.bezi };
    if (sql.includes('COUNT(*) AS n FROM games')) return { n: cfg.aktivniHra ? 1 : 0 };
    // `/report` hledá běh podle run_key a čte pokusy úlohy
    if (sql.includes('FROM runs WHERE run_key')) return cfg.reportRun ?? null;
    if (sql.includes('SELECT attempts')) return { attempts: stav.attempts, status: cfg.reportTaskStatus };
    throw new Error('fakeDb.first: neznámý dotaz → ' + sql.replace(/\s+/g, ' ').slice(0, 120));
  };

  const all = async (sql) => {
    zapis(sql);
    // pollRuns: které cloudové běhy mám vysledovat
    if (sql.includes('FROM runs r JOIN tasks t') && sql.includes("r.status = 'running'")) {
      return { results: cfg.sledovanyRun ? [cfg.sledovanyRun] : [] };
    }
    if (sql.includes('FROM games')) {
      return { results: cfg.aktivniHra
        ? [{ game_id: 'test', repo: 'test/hra', roadmap_file: '.forge/roadmap.json', active: 1 }]
        : [] };
    }
    if (sql.includes('FROM roadmap') && sql.includes('eskalovano')) return { results: [] };
    if (sql.includes('GROUP BY item_id')) return { results: [] };
    if (sql.includes('FROM roadmap r LEFT JOIN tasks t')) return { results: [] };
    if (sql.includes("SELECT payload FROM tasks WHERE status='running'")) return { results: [] };
    if (sql.includes("SELECT * FROM tasks WHERE status='ready'")) {
      return { results: stav.taskStatus === 'ready'
        ? [{ id: 1, title: GRAIN.title, kind: 'code', target: 'cloud',
             prompt: GRAIN.prompt, payload: JSON.stringify({ game: 'test', grain: GRAIN.id,
               repo: 'test/hra', owns: ['scripts/x.gd'], max_lines: 60, model: 'any' }),
             status: 'ready', attempts: 0 }]
        : [] };
    }
    throw new Error('fakeDb.all: neznámý dotaz → ' + sql.replace(/\s+/g, ' ').slice(0, 120));
  };

  const run = async (sql) => {
    zapis(sql);
    if (sql.startsWith('ALTER TABLE roadmap')) return { meta: { changes: 0 } };
    if (sql.includes("UPDATE runs SET status='timeout'")) {
      return { meta: { changes: cfg.zaseknuteBehy ?? 0 } };
    }
    if (sql.includes("UPDATE tasks SET status='running'")) {
      stav.taskClaimed++;
      if (stav.taskStatus !== 'ready') return { meta: { changes: 0 } };
      stav.taskStatus = 'running';
      stav.bezi++;
      return { meta: { changes: 1 } };
    }
    if (sql.includes('INSERT INTO runs')) { stav.runy++; return { meta: { changes: 1 } }; }
    if (sql.includes('INSERT INTO tasks')) return { meta: { changes: 1, last_row_id: 42 } };
    if (sql.startsWith('INSERT INTO roadmap') || sql.startsWith('UPDATE roadmap')
        || sql.startsWith('UPDATE tasks') || sql.startsWith('UPDATE runs')) {
      return { meta: { changes: 0 } };
    }
    throw new Error('fakeDb.run: neznámý dotaz → ' + sql.replace(/\s+/g, ' ').slice(0, 120));
  };

  const api = (sql) => ({
    first: () => first(sql), all: () => all(sql), run: () => run(sql),
    bind: () => api(sql),
  });
  return { DB: { prepare: (sql) => api(String(sql)) }, stav, log };
}

function envFor(cfg) {
  const db = fakeDb(cfg);
  return {
    env: {
      DB: db.DB,
      GITHUB_TOKEN: 'test-token',
      GITHUB_REPO: 'fallback/nesmi-se-pouzit',
      GITHUB_REF: 'main',
      WORKFLOW_FILE: 'agent.yml',
      WEBHOOK_SECRET: SECRET,
      ROADMAP_MAX_PRS: '5',
      MAX_CONCURRENT: '1',
      RETRY_HOURS: '3',
      MAX_ATTEMPTS: '5',
      ESCALATE_AFTER: '3',
      GRAIN_MAX_RUNS: '0',
      STALE_MINUTES: '90',
      ROADMAP_FILE: '.forge/roadmap.json',
    },
    stav: db.stav,
    log: db.log,
  };
}

/** Stub GitHubu — ZAZNAMENÁVÁ volání; neznámou URL hlásí. */
function stubGithub(calls, cfg) {
  globalThis.fetch = async (url) => {
    const u = String(url);
    calls.push(u);
    const json = (data, status = 200) =>
      new Response(JSON.stringify(data), { status, headers: { 'content-type': 'application/json' } });
    if (u.includes('/actions/workflows/') && u.includes('/dispatches')) return new Response(null, { status: 204 });
    // pollRuns: výsledek běhu se hledá podle `run_key` ve jméně
    if (u.includes('/actions/runs?event=workflow_dispatch')) {
      return json({ workflow_runs: cfg.behNaGithubu ? [cfg.behNaGithubu] : [] });
    }
    if (u.includes('/pulls?head=')) return json(cfg.pull ? [cfg.pull] : []);
    if (u.includes('/pulls?')) return json([]);
    if (u.includes('/contents/') && cfg.aktivniHra) {
      const doc = { grains: [GRAIN] };
      return json({ content: Buffer.from(JSON.stringify(doc), 'utf8').toString('base64'), encoding: 'base64' });
    }
    if (u.includes('/git/trees/')) return json({ tree: [] });
    throw new Error('necekana URL: ' + u);
  };
}

async function tick(mod, env) {
  const res = await mod.default.fetch(new Request('https://conductor.test/tick', {
    method: 'POST', headers: { 'x-forge-secret': SECRET },
  }), env);
  return { status: res.status, body: await res.json() };
}

const jeDispatch = (u) => u.includes('/dispatches');
const bylZapis = (log, vzor) => log.some((s) => vzor.test(s));

/** POST /report — skutečný endpoint (tajemství v hlavičce stačí, HMAC je volitelný). */
async function report(mod, env, body, { secret = SECRET } = {}) {
  const res = await mod.default.fetch(new Request('https://conductor.test/report', {
    method: 'POST',
    headers: { 'content-type': 'application/json', 'x-forge-secret': secret },
    body: JSON.stringify(body),
  }), env);
  return { status: res.status, body: await res.json() };
}

/** Jeden sledovaný běh (pollRuns) — payload nese hru i granuli. */
const sledovanyRun = {
  run_id: 7, run_key: RUN_KEY, task_id: 1, title: GRAIN.title,
  payload: JSON.stringify({ game: 'test', grain: GRAIN.id, repo: 'test/hra' }),
};
const behNaGithubu = (conclusion) => ({
  name: `Forge #1 [${RUN_KEY}]`, status: 'completed', conclusion,
  html_url: 'https://github.com/test/hra/actions/runs/1',
});

/** Řádek běhu pro `/report` (worker: null → statistiky uzlu se přeskočí). */
const behRow = () => ({ id: 1, task_id: 1, worker: null });

// ---------------------------------------------------------------- main ----
async function main() {
  console.log('=== tik conductora offline: rozhodovací logika ===');
  build();
  const mod = await import(`${pathToFileURL(BUNDLE).href}?v=${Date.now()}`);

  // ── A) registr BEZ aktivní hry → žádný dispatch a ani čtení roadmapy ──────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: false });
    const { env } = envFor({ aktivniHra: false });
    const { status, body } = await tick(mod, env);
    const zprava = String(body.message || '');
    check('A: /tick odpoví 200', status, 200);
    check('A: tik hlásí, že není aktivní hra', /žádná aktivní hra/i.test(zprava), true);
    check('A: tik hlásí „spusteno: 0 úloh"', /spusteno: 0 úloh/.test(zprava), true);
    check('A: NEDISPATCHOVALO se', calls.filter(jeDispatch).length, 0);
    check('A: tik hlásí, že roadmapu NEŘEŠIL', /roadmapu neřeším/.test(zprava), true);
    check('A: roadmapa se ani nečetla', calls.some((u) => u.includes('/contents/')), false);
  }

  // ── B) aktivní hra + jedna připravená granule → PRÁVĚ JEDEN dispatch ─────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav } = envFor({ aktivniHra: true });
    const { body } = await tick(mod, env);
    check('B: dispatch proběhl PRÁVĚ JEDNOU', calls.filter(jeDispatch).length, 1);
    check('B: dispatch míří na workflow z env', calls.some((u) => u.includes('/workflows/agent.yml/dispatches')), true);
    check('B: úloha byla claimnuta', stav.taskClaimed, 1);
    check('B: vznikl jeden běh', stav.runy, 1);
    check('B: tik hlásí „spusteno: 1 úloh"', /spusteno: 1 úloh/.test(String(body.message || '')), true);
  }

  // ── C) jiný běh už běží → MAX_CONCURRENT brzdí nový dispatch ─────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav } = envFor({ aktivniHra: true, bezi: 1 });
    const { body } = await tick(mod, env);
    check('C: běžící úloha brzdí další dispatch (MAX_CONCURRENT=1)', calls.filter(jeDispatch).length, 0);
    check('C: tik hlásí „spusteno: 0 úloh"', /spusteno: 0 úloh/.test(String(body.message || '')), true);
  }

  // ── D) /poll: běh SELHAL → úloha zpět na ready + COOLDOWN (vada B1) ──────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, sledovanyRun, behNaGithubu: behNaGithubu('failure') });
    const { env, log } = envFor({ aktivniHra: true, sledovanyRun, attempts: 2 });
    const { body } = await tick(mod, env);
    check('D: polling ohlásil jednu aktualizaci', /aktualizovano behu: 1/.test(String(body.message || '')), true);
    check('D: úloha se vrátila na `ready` (má pokusy)',
      bylZapis(log, /UPDATE tasks SET status=\?.*WHERE id=\?/), true);
    check('D: běh dostal výsledek z GitHubu', bylZapis(log, /UPDATE runs SET status=\?/), true);
    check('D: COOLDOWN se zapsal (`naposledy_selhalo`) — to je vada B1',
      bylZapis(log, /UPDATE roadmap SET status = \?.*naposledy_selhalo/), true);
  }

  // ── E) /poll: běh USPĚL a PR je SLOUČENÝ → done (úloha i granule) ────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, sledovanyRun, behNaGithubu: behNaGithubu('success'),
                        pull: { html_url: 'https://github.com/test/hra/pull/1', merged_at: '2026-10-06T20:00:00Z' } });
    const { env, log } = envFor({ aktivniHra: true, sledovanyRun });
    await tick(mod, env);
    check('E: úloha je `done` (běh i PR sloučený)',
      bylZapis(log, /UPDATE tasks SET status='done'/), true);
    check('E: i granule je `done`', bylZapis(log, /UPDATE roadmap SET status='done'/), true);
  }

  // ── F) /poll: běh USPĚL, ale PR sloučený NENÍ → awaiting_human (vada A1) ─
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, sledovanyRun, behNaGithubu: behNaGithubu('success'),
                        pull: { html_url: 'https://github.com/test/hra/pull/2', merged_at: null } });
    const { env, log } = envFor({ aktivniHra: true, sledovanyRun });
    await tick(mod, env);
    check('F: úloha čeká na člověka (`awaiting_human`), NE `done`',
      bylZapis(log, /UPDATE tasks SET status='awaiting_human'/), true);
    check('F: `done` se v tomhle případě NEZAPSALO',
      bylZapis(log, /UPDATE tasks SET status='done'/), false);
  }

  // ── G) stale-recovery: zaseknutý běh se ukončí, úloha zpět JEN s pokusy ──
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, zaseknuteBehy: 1 });
    await tick(mod, env);
    check('G: zaseknutý běh se ukončí jako `timeout`',
      bylZapis(log, /UPDATE runs SET status='timeout'/), true);
    check('G: úloha se vrací do fronty JEN s pokusy (`attempts < ?`)',
      bylZapis(log, /UPDATE tasks SET status='ready'.*attempts < \?/), true);
    check('G: a co pokusy nemá, jde na `failed`',
      bylZapis(log, /UPDATE tasks SET status='failed'/), true);
  }

  // ── G2) bez zaseknutých běhů se na úlohy NESAHÁ ──────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, zaseknuteBehy: 0 });
    await tick(mod, env);
    check('G2: bez zaseknutých běhů se stav úloh nemění',
      bylZapis(log, /UPDATE tasks SET status='ready'.*attempts < \?/), false);
  }

  // ── H) /report: SELHÁNÍ s pokusy → úloha na ready + COOLDOWN (vada B1) ───
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, attempts: 2, reportRun: behRow() });
    const { status } = await report(mod, env, { run_key: RUN_KEY, status: 'failure', summary: 'spadlo' });
    check('H: /report odpoví 200', status, 200);
    check('H: úloha se vrátí na `ready`', bylZapis(log, /UPDATE tasks SET status=\?/), true);
    check('H: COOLDOWN se zapíše (`naposledy_selhalo`) — vada B1',
      bylZapis(log, /UPDATE roadmap SET naposledy_selhalo/), true);
    check('H: granule se NEOZNAČÍ jako `failed` (má ještě pokusy)',
      bylZapis(log, /UPDATE roadmap SET status='failed'/), false);
  }

  // ── I) /report: poslední pokus → `failed` ────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, attempts: 5, reportRun: behRow() });
    await report(mod, env, { run_key: RUN_KEY, status: 'failure' });
    check('I: úloha jde na `failed` (vyčerpané pokusy)',
      bylZapis(log, /UPDATE tasks SET status=\?/), true);
    check('I: granule jde na `failed`', bylZapis(log, /UPDATE roadmap SET status='failed'/), true);
    check('I: a čas selhání se zapíše taky', bylZapis(log, /naposledy_selhalo/), true);
  }

  // ── J) /report: ÚSPĚCH → done ────────────────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, reportRun: behRow() });
    await report(mod, env, { run_key: RUN_KEY, status: 'success', pr_url: 'https://x/1' });
    check('J: úloha je `done`', bylZapis(log, /UPDATE tasks SET status='done'/), true);
    check('J: i granule je `done`', bylZapis(log, /UPDATE roadmap SET status='done'/), true);
  }

  // ── K) /report: neznámý run_key → 404 a ŽÁDNÉ zápisy ─────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, reportRun: null });
    const { status } = await report(mod, env, { run_key: 'neexistuje', status: 'failure' });
    check('K: neznámý run_key → 404', status, 404);
    check('K: a nic se nezapsalo', log.some((s) => /^UPDATE /.test(s)), false);
  }

  // ── L) /report: špatné tajemství → 401 ───────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, reportRun: behRow() });
    const { status } = await report(mod, env, { run_key: RUN_KEY, status: 'failure' }, { secret: 'spatne' });
    check('L: špatné tajemství → 401', status, 401);
    check('L: a nic se nezapsalo', log.some((s) => /^UPDATE /.test(s)), false);
  }

  // ── M) /report: `blocked`/`done` je TERMINÁLNÍ (nesmí ho vzkřísit) ───────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, attempts: 2, reportRun: behRow(),
                                  reportTaskStatus: 'blocked' });
    const { status, body } = await report(mod, env, { run_key: RUN_KEY, status: 'failure' });
    check('M: odpoví 200 s poznámkou', status === 200 && typeof body.poznamka === 'string', true);
    check('M: stav úlohy se NEMĚNÍ (blocked je terminální)',
      bylZapis(log, /UPDATE tasks SET status=\?/), false);
  }

  console.log();
  if (errors) {
    console.log(`VYSLEDEK: ${checks} kontrol, ${errors} CHYB`);
    return 1;
  }
  console.log(`VYSLEDEK: ${checks} kontrol, 0 chyb`);
  return 0;
}

process.exit(await main());

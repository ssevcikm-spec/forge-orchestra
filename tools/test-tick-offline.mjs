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
//
// P27 / Úkol B1 — SEDM ENDPOINTŮ, KTERÉ NEVOLAL ŽÁDNÝ TEST (X–AD níž):
//   X)  **/health** — stav SLUŽBY (`ok`, `ready`, `running`, `games`, `workers`)
//       ZVLÁŠŤ od stavu CÍLE (`targets[].main_ci`, `forge.ok`,
//       `forge.selhani_v_rade`). Veřejný (monitoring dostupnosti), takže se
//       testuje GETem BEZ tajemství; „nezměřeno" (`error`) musí být VIDĚT.
//   Y)  **/queue** — fronta úloh i se `status`/`attempts`
//   Z)  **/roadmap** — cache roadmapy (LEFT JOIN, aby byly vidět i granule bez úkolu)
//   AA) **/failed** — selhané úlohy s ROZBALENÝM `payload` a běhy přiřazenými
//       podle `task_id` (podklad pro `forge replan`)
//   AB) **/status** — běhy s `title` z JOINu
//   AC) **/workers** — registrované uzly (podle nich se přiděluje práce)
//   AD) **/games** — registr her VČETNĚ VYPNUTÝCH (na rozdíl od `/health`)
//
// Proč právě tyhle: P24 zavřela pět cest a P25 tři zapisující, ale tyhle
// ČTECÍ endpointy — které orchestra používá pro diagnostiku i pro člověka —
// nevolal NIKDO (naměřeno 7. 10. 2026: `post(mod, env, '/health'|…)` → 0×).
// Test u každého tvrdí **TVAR i OBSAH** odpovědi, ne jen `status === 200`
// (jinak by prošel i nad prázdným `{ tasks: null }`); doklad je
// `_analyza/p27-a-overeni.py` etapa A3.

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
  const vazby = [];   // P25/B1: vázané hodnoty (co se opravdu posílá do D1)
  const stav = {
    taskStatus: cfg.taskStatus || 'ready',
    taskClaimed: 0,
    runy: 0,
    bezi: cfg.bezi || 0,
    attempts: cfg.attempts ?? 0,
    // ── P24 / Úkol B3: čítače pro endpointy, které dřív netestoval NIC ──────
    heartbeaty: 0,      // `/heartbeat`
    smazaneRadky: 0,    // `/tasks/cleanup` (mazání osiřelých řádků cache)
    blocked: 0,         // `/tasks/cleanup` (označeno `blocked`)
    abandoned: 0,       // `/tasks/cleanup` (dorovnání běhů)
    resetSmazano: 0,    // `/roadmap/reset` (smazané granule)
    // ── P25 / Úkol B1: registr her (`/game`, `/game/active`) ────────────────
    hryZapsany: 0,      // INSERT do `games`
    prepnutoHry: 0,     // UPDATE `games.active`
    posledniActive: undefined,  // čím se naposledy přepnulo (undefined = nic)
  };
  const zapis = (sql) => log.push(String(sql).replace(/\s+/g, ' ').trim());

  const first = async (sql) => {
    zapis(sql);
    // `readyCount`: počet připravených úloh je v `/health` TVRZENÍ O STAVU —
    // s natvrdo zapsanou 1 by kontrola „ready je z D1" nemohla nikdy spadnout.
    if (sql.includes("FROM tasks WHERE status='ready'")) return { n: cfg.readyCount ?? 1 };
    if (sql.includes("FROM runs WHERE status='running'")) return { n: stav.bezi };
    if (sql.includes('COUNT(*) AS n FROM games')) {
      return { n: cfg.gamesCount ?? (cfg.aktivniHra ? 1 : 0) };
    }
    // `/claim`: hledá úlohu pro domácí uzel (`target='lan'` a druhy)
    if (sql.includes("target='lan'")) return cfg.claimTask ?? null;
    // `/roadmap/reset`: ověření, že hra existuje
    if (sql.includes('SELECT game_id FROM games WHERE game_id')) return cfg.resetGame ?? null;
    // `/tasks/cleanup` (dry_run) a `/roadmap/reset` (dry_run): počty
    if (sql.includes('COUNT(*) AS n FROM roadmap')) return { n: cfg.resetPocet ?? 0 };
    if (sql.includes("FROM tasks WHERE status='failed'")) return { n: cfg.resetUkolu ?? 0 };
    if (sql.includes('COUNT(*) AS n FROM tasks')) return { n: cfg.cleanupCount ?? 0 };
    // `/report` hledá běh podle run_key a čte pokusy úlohy
    if (sql.includes('FROM runs WHERE run_key')) return cfg.reportRun ?? null;
    if (sql.includes('SELECT attempts')) return { attempts: stav.attempts, status: cfg.reportTaskStatus };
    throw new Error('fakeDb.first: neznámý dotaz → ' + sql.replace(/\s+/g, ' ').slice(0, 120));
  };

  const all = async (sql) => {
    zapis(sql);
    // ── P27 / Úkol B1: ČTECÍ ENDPOINTY ────────────────────────────────────
    // ⚠ POŘADÍ JE PODSTATNÉ: konkrétní vzory musí být PŘED obecným
    // `sql.includes('FROM games')` níž — jinak by `/games` (registr)
    // dostal řádek aktivní hry a test by měřil jiný dotaz, než si myslí.
    if (sql.includes('SELECT * FROM games')) {
      return { results: cfg.gamesRadky ?? [] };          // `/games`
    }
    if (sql.includes('SELECT * FROM workers')) {
      return { results: cfg.workersVse ?? [] };          // `/workers`
    }
    if (sql.includes('SELECT name, kinds, last_seen')) {
      return { results: cfg.workersRadky ?? [] };        // `/health`
    }
    if (sql.includes('FROM tasks ORDER BY id DESC LIMIT 50')) {
      return { results: cfg.queueRadky ?? [] };          // `/queue`
    }
    if (sql.includes("FROM tasks WHERE status='failed'")) {
      return { results: cfg.failedRadky ?? [] };         // `/failed`
    }
    if (sql.includes('FROM runs WHERE status NOT IN')) {
      return { results: cfg.failedRuny ?? [] };          // `/failed`
    }
    if (sql.includes('FROM runs r LEFT JOIN tasks t')) {
      return { results: cfg.statusRuny ?? [] };          // `/status`
    }
    // pollRuns: které cloudové běhy mám vysledovat
    if (sql.includes('FROM runs r JOIN tasks t') && sql.includes("r.status = 'running'")) {
      return { results: cfg.sledovanyRun ? [cfg.sledovanyRun] : [] };
    }
    // ⚠ `hryRadky` umí přepsat REPO aktivní hry — a to je nutné pro `/health`:
    // `targetState` má TTL cache 2 minuty klíčovanou REPEM, takže by druhý
    // scénář měření cíle dostal odpověď z cache prvního a měřil by NIC
    // (naměřeno 7. 10. 2026 při psaní těchhle testů).
    if (sql.includes('FROM games')) {
      return { results: cfg.hryRadky ?? (cfg.aktivniHra ? [GAME_ROW] : []) };
    }
    // `/tasks/cleanup`: co je v cache roadmapy (podle toho se hledají osiřelé)
    if (sql.includes('SELECT item_id, task_id FROM roadmap')) {
      return { results: cfg.roadmapRadky ?? [] };
    }
    // P29/B6: kolik běhů spálila KTERÁ granule (`grainRuns` → strop `GRAIN_MAX_RUNS`).
    // Bez tohohle přepínače se scénář „granule nad stropem se POJMENUJE“ nedá
    // sestrojit — a `find()` by se zase jen tvrdil z kódu.
    if (sql.includes('GROUP BY item_id')) return { results: cfg.granuleRuns ?? [] };
    // P29/B6: úlohy, které drží cooldown. SQL je vyfiltruje DŘÍV, než je vidí
    // `find()`, takže tik musí umět říct, kolik jich bylo (jinak zůstane „0 úloh“).
    if (sql.includes('JOIN roadmap rm ON rm.task_id = t.id')) {
      return { results: cfg.cooldownUlohy ?? [] };
    }
    // `/tasks/cleanup` (dry_run): ukázka úloh bez vazby
    if (sql.includes('SELECT id, title, status FROM tasks')) {
      return { results: cfg.ukazkaUkolu ?? [] };
    }
    if (sql.includes('FROM roadmap') && sql.includes('eskalovano')) return { results: [] };
    if (sql.includes('FROM roadmap r LEFT JOIN tasks t')) {
      return { results: cfg.roadmapRadky ?? [] };       // `/roadmap`
    }
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

  const run = async (sql, args) => {
    zapis(sql);
    if (sql.startsWith('ALTER TABLE roadmap')) return { meta: { changes: 0 } };
    if (sql.includes("UPDATE runs SET status='timeout'")) {
      return { meta: { changes: cfg.zaseknuteBehy ?? 0 } };
    }
    // `/claim` (domácí uzel) I dispatch claim v tiku mají TÝŽ tvar:
    // `UPDATE tasks SET status='running', attempts=attempts+1 …`.
    // ⚠ STAV ÚLOHY SE MUSÍ PŘEPNOUT NA `running` — jinak by smyčka dispatche
    // viděla tutéž úlohu pořád jako `ready` a **zacyklila se** (naměřeno
    // 7. 10. 2026: s mutací M2 spadl Node na `exit 134`, tedy „brána nespadla
    // podle kritéria“, protože výstup neobsahoval `CHYBA`).
    if (sql.includes('attempts=attempts+1')) {
      const ch = cfg.claimChanges ?? 1;
      if (ch) {
        stav.taskClaimed++;
        stav.bezi++;
        stav.taskStatus = 'running';
      }
      return { meta: { changes: ch } };
    }
    if (sql.includes("UPDATE tasks SET status='running'")) {
      stav.taskClaimed++;
      if (stav.taskStatus !== 'ready') return { meta: { changes: 0 } };
      stav.taskStatus = 'running';
      stav.bezi++;
      return { meta: { changes: 1 } };
    }
    // `/heartbeat`: zápis uzlu (INSERT … ON CONFLICT)
    if (sql.includes('INSERT INTO workers')) {
      stav.heartbeaty++;
      return { meta: { changes: 1 } };
    }
    // `/tasks/cleanup` a `/roadmap/reset`: co se opravdu smazalo / zablokovalo
    if (sql.includes('DELETE FROM roadmap WHERE item_id = ?')) {
      stav.smazaneRadky++;
      return { meta: { changes: 1 } };
    }
    if (sql.includes('DELETE FROM roadmap')) {
      stav.resetSmazano = cfg.resetPocet ?? 0;
      return { meta: { changes: cfg.resetPocet ?? 0 } };
    }
    if (sql.includes("UPDATE tasks SET status='blocked'")) {
      stav.blocked += cfg.cleanupCount ?? 0;
      return { meta: { changes: cfg.cleanupCount ?? 0 } };
    }
    if (sql.includes("UPDATE runs SET status='abandoned'")) {
      stav.abandoned++;
      return { meta: { changes: cfg.abandoned ?? 0 } };
    }
    if (sql.includes('INSERT INTO runs')) { stav.runy++; return { meta: { changes: 1 } }; }
    if (sql.includes('INSERT INTO tasks')) return { meta: { changes: 1, last_row_id: 42 } };
    // ── P25 / Úkol B1: REGISTR HER. Tenhle zápis mění, CO orchestra dělá —
    // `/game` hru zapne (`active = 1`) a `/game/active` ji vypne/zapne.
    // `cfg.aktivniHra` je proto ŽIVÝ stav falešného světa: přepnutí hry se
    // v něm projeví, takže jde ověřit, že další `/tick` opravdu needispatchuje.
    if (sql.includes('INSERT INTO games')) {
      stav.hryZapsany++;
      return { meta: { changes: cfg.gameChanges ?? 1 } };
    }
    if (sql.includes('UPDATE games SET active')) {
      const ch = cfg.gameChanges ?? 1;
      if (ch) {
        const aktivni = Number(args?.[0]) === 1;
        stav.prepnutoHry++;
        stav.posledniActive = aktivni;
        cfg.aktivniHra = aktivni;
      }
      return { meta: { changes: ch } };
    }
    if (sql.startsWith('INSERT INTO roadmap') || sql.startsWith('UPDATE roadmap')
        || sql.startsWith('UPDATE tasks') || sql.startsWith('UPDATE runs')) {
      return { meta: { changes: 0 } };
    }
    throw new Error('fakeDb.run: neznámý dotaz → ' + sql.replace(/\s+/g, ' ').slice(0, 120));
  };

  // ⚠ `bind` SE ZAZNAMENÁVÁ (P25/B1): kontroly typu „jde do DB opravdu 0, ne 1"
  // se nedají udělat z textu SQL — hodnoty jsou v `bind()`. Bez toho by test
  // tvrdil jen to, že se dotaz TVAROVĚ podobá (`overovani`: přítomnost ≠ chování).
  const api = (sql, args) => ({
    first: () => first(sql, args), all: () => all(sql, args), run: () => run(sql, args),
    bind: (...a) => {
      vazby.push({ sql: String(sql).replace(/\s+/g, ' ').trim(), args: a });
      return api(sql, a);
    },
  });
  return { DB: { prepare: (sql) => api(String(sql)) }, stav, log, vazby };
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
      // P29/B6: strop granule musí jít v testu ZAPNOUT i vypnout (scénář AE3).
      GRAIN_MAX_RUNS: cfg.grainMaxRuns ?? '0',
      STALE_MINUTES: '90',
      ROADMAP_FILE: '.forge/roadmap.json',
    },
    stav: db.stav,
    log: db.log,
    vazby: db.vazby,
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
    // P27 / Úkol B1: stav CÍLE pro `/health` (`targetState`). Do 7. 10. 2026
    // tenhle stub na tuhle URL spadal (`necekana URL`), takže `/health` šel
    // testovat JEN s chybou měření — a „nezměřeno" se nedalo odlišit od
    // „naměřeno". `ciChyba` tu chybu umí vyrobit SCHVÁLNĚ.
    if (u.includes('/actions/workflows/') && u.includes('/runs?')) {
      if (cfg.ciChyba && u.includes('ci.yml')) {
        return new Response('rozbito', { status: 500 });
      }
      return json({ workflow_runs: u.includes('ci.yml')
        ? (cfg.ciRuny ?? []) : (cfg.agentRuny ?? []) });
    }
    // pollRuns: výsledek běhu se hledá podle `run_key` ve jméně
    if (u.includes('/actions/runs?event=workflow_dispatch')) {
      return json({ workflow_runs: cfg.behNaGithubu ? [cfg.behNaGithubu] : [] });
    }
    if (u.includes('/pulls?head=')) return json(cfg.pull ? [cfg.pull] : []);
    if (u.includes('/pulls?')) return json([]);
    // `/tasks/cleanup` čte roadmapu ze SUROVÉHO GitHubu (raw), ne z API —
    // a to je přesně ta cesta, kterou dřív netestoval žádný test. `roadmapChyba`
    // umí vrátit 404, aby se dala ověřit bezpečnostní pojistka „radši nemažu“.
    if (u.includes('raw.githubusercontent.com')) {
      if (cfg.roadmapChyba) return new Response('neni', { status: 404 });
      return json({ grains: cfg.grainsSoubor ?? [GRAIN] });
    }
    if (u.includes('/contents/') && cfg.aktivniHra) {
      // P29/B6: `contentsChyba` umí čtení roadmapy hry ZVÝŠIT (HTTP 500) —
      // právě na tom stojí pojistka „nenačtená roadmapa NESMÍ mazat osiřelé
      // řádky cache“ (scénář AE2). Bez tohohle přepínače by se pojistka
      // testovat nedala a tvrdila by se jen z kódu.
      if (cfg.contentsChyba) return new Response('rozbito', { status: 500 });
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

/**
 * Obecné POST na SKUTEČNÝ endpoint conductora (P24, Úkol B3).
 *
 * PROČ: do 7. 10. 2026 procházely handlerem jen `/tick` a `/report`; `/poll`,
 * `/claim`, `/heartbeat`, `/tasks/cleanup` a `/roadmap/reset` netestoval
 * NIKDO — a to je ta část rozhodovací logiky, kde bydlí mazání a blokování.
 */
async function post(mod, env, cesta, { telo, hlavicky = {}, secret = SECRET } = {}) {
  const h = { 'content-type': 'application/json', ...hlavicky };
  if (secret !== null) h['x-forge-secret'] = secret;
  const res = await mod.default.fetch(new Request(`https://conductor.test${cesta}`, {
    method: 'POST', headers: h,
    body: telo === undefined ? undefined : JSON.stringify(telo),
  }), env);
  let b = null;
  try { b = await res.json(); } catch { b = null; }
  return { status: res.status, body: b };
}

/**
 * Obecný GET na SKUTEČNÝ endpoint conductora (P27, Úkol B1).
 *
 * PROČ ZVLÁŠŤ: `/health` je **veřejný** (hlídá ho monitoring dostupnosti)
 * a čte se **GETem** — test, který by ho volal POSTem s tajemstvím, by
 * netvrdil nic o tom, co používá monitoring.
 */
async function get(mod, env, cesta, { hlavicky = {} } = {}) {
  const res = await mod.default.fetch(new Request(`https://conductor.test${cesta}`, {
    method: 'GET', headers: hlavicky,
  }), env);
  let b = null;
  try { b = await res.json(); } catch { b = null; }
  return { status: res.status, body: b };
}

/** Jeden sledovaný běh (pollRuns) — payload nese hru i granuli. */const sledovanyRun = {
  run_id: 7, run_key: RUN_KEY, task_id: 1, title: GRAIN.title,
  payload: JSON.stringify({ game: 'test', grain: GRAIN.id, repo: 'test/hra' }),
};
const behNaGithubu = (conclusion) => ({
  name: `Forge #1 [${RUN_KEY}]`, status: 'completed', conclusion,
  html_url: 'https://github.com/test/hra/actions/runs/1',
});

/** Řádek běhu pro `/report` (worker: null → statistiky uzlu se přeskočí). */
const behRow = () => ({ id: 1, task_id: 1, worker: null });

// ── P27 / Úkol B1: FIXTURY PRO ČTECÍ ENDPOINTY ────────────────────────────
// Hodnoty jsou ZÁMĚRNĚ nenulové a rozlišitelné: test, který tvrdí jen
// `status === 200`, projde i nad prázdnou odpovědí — a to je přesně ta vada,
// kvůli které tyhle testy vznikají (`overovani`: přítomnost ≠ chování).
const TASK_ROW = {
  id: 11, title: 'Hotová úloha', kind: 'code', target: 'cloud',
  status: 'ready', attempts: 2, created_at: '2026-10-07T10:00:00Z',
};
const ROADMAP_ROW = {
  item_id: 'test/grain.jedna', task_id: 11, status: 'queued',
  created_at: '2026-10-07T09:00:00Z', updated_at: '2026-10-07T10:00:00Z',
  task_status: 'ready', attempts: 2,
};
const FAILED_TASK = {
  id: 12, title: 'Selhaná úloha', kind: 'code', target: 'cloud',
  prompt: 'neco', payload: '{"game":"test","grain":"x"}',
  status: 'failed', attempts: 5, created_at: '2026-10-07T08:00:00Z',
};
// `log_tail` je delší než strop v handleru (2000) — jinak by se zkrácení
// nedalo změřit a kontrola by tvrdila jen to, že text „nějaký“ je.
const FAILED_RUN = {
  task_id: 12, run_key: 'klic-selhal', status: 'failed', summary: 'spadlo',
  log_tail: 'x'.repeat(2500), pr_url: null, finished_at: '2026-10-07T08:10:00Z',
};
const STATUS_RUN = {
  id: 3, task_id: 11, title: 'Hotová úloha', status: 'success', worker: 'pc-domaci',
  started_at: '2026-10-07T10:00:00Z', finished_at: '2026-10-07T10:05:00Z',
  summary: 'ok', pr_url: 'https://x/1',
};
const WORKER_ROW = {
  name: 'pc-domaci', kinds: 'assets,test', last_seen: '2026-10-07T16:00:00Z', info: '{}',
};
const GAME_ROW = {
  game_id: 'test', repo: 'test/hra', roadmap_file: '.forge/roadmap.json', active: 1,
};
// VYPNUTÁ hra: v registru být MUSÍ (`/games`), v `/health` být NESMÍ.
const GAME_OFF = {
  game_id: 'stara', repo: 'test/stara', roadmap_file: '.forge/roadmap.json', active: 0,
};

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

  // ══════════════════════════════════════════════════════════════════════════
  // P24 / Úkol B3 — ENDPOINTY, KTERÉ DOSUD NETESTOVAL ŽÁDNÝ TEST
  // (`/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`)
  // ══════════════════════════════════════════════════════════════════════════

  // ── N) /poll: sám endpoint (dřív šel jen omylem přes /tick) ──────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, sledovanyRun, behNaGithubu: behNaGithubu('failure') });
    const { env, log } = envFor({ aktivniHra: true, sledovanyRun, attempts: 2 });
    const { status, body } = await post(mod, env, '/poll');
    check('N: /poll odpoví 200', status, 200);
    check('N: /poll ohlásí aktualizovaný běh',
      /aktualizovano behu: 1/.test(String(body.message || '')), true);
    check('N: /poll zapíše cooldown (`naposledy_selhalo`)',
      bylZapis(log, /UPDATE roadmap SET status = \?.*naposledy_selhalo/), true);
  }

  // ── N2) /poll: špatné tajemství → 401 a ŽÁDNÉ volání GitHubu ─────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/poll', { secret: 'spatne' });
    check('N2: /poll se špatným tajemstvím → 401', status, 401);
    check('N2: a na GitHub se vůbec nešlo', calls.length, 0);
  }

  // ── O) /claim: domácí uzel si vyzvedne LAN úlohu ─────────────────────────
  {
    const lanUloha = { id: 5, title: 'LAN úloha', kind: 'test', target: 'lan', attempts: 0 };
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, stav } = envFor({ aktivniHra: true, claimTask: lanUloha });
    const { status, body } = await post(mod, env, '/claim', {
      telo: { kinds: ['test'] }, hlavicky: { 'x-forge-worker': 'pc-domaci' },
    });
    check('O: /claim odpoví 200', status, 200);
    check('O: /claim vrátí úlohu', body?.task?.id, 5);
    check('O: /claim vrátí `run_key`', typeof body?.run_key, 'string');
    check('O: úloha se zamkla OPTIMISTICKY (`attempts=attempts+1`)',
      bylZapis(log, /attempts=attempts\+1/), true);
    check('O: vznikl běh s uzlem v `worker`',
      bylZapis(log, /INSERT INTO runs .*worker/s), true);
    check('O: čítač úloh se zvedl', stav.taskClaimed, 1);
  }

  // ── O2) /claim: žádná úloha → `task: null` a ŽÁDNÝ zápis běhu ────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, stav } = envFor({ aktivniHra: true, claimTask: null });
    const { status, body } = await post(mod, env, '/claim', {
      telo: { kinds: ['test'] }, hlavici: {}, hlavicky: { 'x-forge-worker': 'pc-domaci' },
    });
    check('O2: /claim bez úlohy → 200 a `task: null`',
      status === 200 && body?.task === null, true);
    check('O2: a NEZALOŽIL se běh', stav.runy, 0);
    check('O2: a nezapsalo se nic do úloh', bylZapis(log, /UPDATE tasks SET status='running'/), false);
  }

  // ── O3) /claim: prohrátý optimistický zámek → `task: null` bez běhu ──────
  {
    const lanUloha = { id: 5, title: 'LAN úloha', kind: 'test', target: 'lan', attempts: 0 };
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav, log } = envFor({ aktivniHra: true, claimTask: lanUloha, claimChanges: 0 });
    const { body } = await post(mod, env, '/claim', {
      telo: { kinds: ['test'] }, hlavicky: { 'x-forge-worker': 'pc-domaci' },
    });
    check('O3: prohraný zámek → `task: null` s poznámkou',
      body?.task === null && typeof body?.note === 'string', true);
    check('O3: a běh se NEZALOŽIL (jinak by úlohu dělali dva uzly)', stav.runy, 0);
    check('O3: a nic se neoznačilo `blocked`', stav.blocked, 0);
  }

  // ── O4) /claim bez hlavičky uzlu → 400 (jinak by úlohu vzal „nikdo“) ─────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/claim', { telo: { kinds: ['test'] } });
    check('O4: /claim bez `x-forge-worker` → 400', status, 400);
    check('O4: a nic se nevyzvedlo', bylZapis(log, /attempts=attempts\+1/), false);
  }

  // ── P) /heartbeat: uzel se zapíše i s druhy a informacemi ────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav, log } = envFor({ aktivniHra: true });
    const { status, body } = await post(mod, env, '/heartbeat', {
      telo: { kinds: ['assets', 'test'], platform: 'win32', info: { godot: '4.7.2' } },
      hlavicky: { 'x-forge-worker': 'pc-domaci' },
    });
    check('P: /heartbeat odpoví 200', status, 200);
    check('P: /heartbeat vrátí jméno uzlu', body?.name, 'pc-domaci');
    check('P: uzel se ZAPSAL (INSERT … ON CONFLICT)', stav.heartbeaty, 1);
    check('P: zápis je UPSERT, ne jen INSERT',
      bylZapis(log, /ON CONFLICT\(name\) DO UPDATE/), true);
    // Bez obnovení `last_seen` by zdravý uzel vypadal mrtvý — a to je celý
    // smysl heartbeatu (čte ho `/health` i `/workers`).
    check('P: a OBNOVÍ `last_seen`', bylZapis(log, /info = excluded\.info, last_seen = datetime\('now'\)/), true);
  }

  // ── P2) /heartbeat bez hlavičky uzlu → 400 a ŽÁDNÝ zápis ─────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/heartbeat', { telo: { kinds: ['test'] } });
    check('P2: /heartbeat bez `x-forge-worker` → 400', status, 400);
    check('P2: a uzel se nezapsal', stav.heartbeaty, 0);
  }

  // ── Q) /tasks/cleanup (dry_run): spočítá, ale NEMAŽE ─────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, stav } = envFor({
      aktivniHra: true, cleanupCount: 4, roadmapRadky: [{ item_id: 'test/stara', task_id: 9 }],
    });
    const { status, body } = await post(mod, env, '/tasks/cleanup', { telo: { dry_run: true } });
    check('Q: dry_run odpoví 200', status, 200);
    check('Q: dry_run hlásí `dry_run: true`', body?.dry_run, true);
    check('Q: dry_run vidí platné granule ze SOUBORU',
      body?.platnych_granuli_v_souborech, 1);
    check('Q: dry_run vidí osiřelý řádek cache', body?.osirelych_radku, 1);
    check('Q: dry_run NEMAŽE řádky roadmapy', stav.smazaneRadky, 0);
    check('Q: dry_run NEBLOKUJE úlohy', stav.blocked, 0);
    check('Q: dry_run nezapsal ani DELETE', bylZapis(log, /DELETE FROM roadmap/), false);
  }

  // ── Q2) /tasks/cleanup: roadmapa se NEDÁ načíst → 503 a NEMAZAT ──────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, roadmapChyba: true });
    const { env, log, stav } = envFor({
      aktivniHra: true, cleanupCount: 4, roadmapRadky: [{ item_id: 'test/stara', task_id: 9 }],
    });
    const { status, body } = await post(mod, env, '/tasks/cleanup', { telo: {} });
    check('Q2: nenačtená roadmapa → 503', status, 503);
    // ⚠ MUSÍ SE OVĚŘIT KONKRÉTNÍ DŮVOD, ne jen „nemažu“: obě pojistky
    // (`hryBezSouboru` i prázdné `platne`) vrací 503 a slovo „nemažu“ je v OBOU
    // hláškách — takže kontrola „obsahuje nemažu“ zelenala i s vypnutou první
    // pojistkou (naměřeno 7. 10. 2026: mutace M13 tím prošla).
    check('Q2: a řekne PROČ („roadmapa se nedá načíst“)',
      /roadmapa se nedá načíst/.test(String(body?.error || '')), true);
    check('Q2: a NEplete si to s prázdnou roadmapou',
      /žádná platná granule/.test(String(body?.error || '')), false);
    check('Q2: a hlavně NEMAZALO', stav.smazaneRadky, 0);
    check('Q2: a neblokovalo', stav.blocked, 0);
    check('Q2: a nezapsalo DELETE', bylZapis(log, /DELETE FROM roadmap/), false);
  }

  // ── Q3) /tasks/cleanup: prázdná roadmapa → 503 (nemaže se naslepo) ───────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, grainsSoubor: [] });
    const { env, stav } = envFor({ aktivniHra: true, cleanupCount: 4 });
    const { status, body } = await post(mod, env, '/tasks/cleanup', { telo: {} });
    check('Q3: prázdná roadmapa → 503', status, 503);
    check('Q3: a řekne, že nemaže', /nemažu/.test(String(body?.error || '')), true);
    check('Q3: a NEMAZALO', stav.smazaneRadky, 0);
  }

  // ── Q4) /tasks/cleanup: ostrý běh → zablokuje osiřelé a smaže cache ──────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, stav } = envFor({
      aktivniHra: true, cleanupCount: 4, abandoned: 2,
      roadmapRadky: [{ item_id: 'test/stara', task_id: 9 }, { item_id: 'test/grain.jedna', task_id: 1 }],
    });
    const { status, body } = await post(mod, env, '/tasks/cleanup', { telo: {} });
    check('Q4: ostrý úklid odpoví 200', status, 200);
    check('Q4: zablokoval osiřelé úlohy z řádků cache', body?.zablokovano_z_radku, 4);
    check('Q4: smazal JEN osiřelý řádek (platná granule zůstává)', stav.smazaneRadky, 1);
    check('Q4: dorovnal běhy, které zůstaly viset', body?.dorazeno_behu, 2);
    check('Q4: a úlohy bez vazby označil `blocked`',
      bylZapis(log, /UPDATE tasks SET status='blocked'/), true);
  }

  // ── R) /roadmap/reset (dry_run): spočítá, ale NEMAŽE ─────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, stav } = envFor({ aktivniHra: true, resetPocet: 7, resetUkolu: 2 });
    const { status, body } = await post(mod, env, '/roadmap/reset', { telo: { dry_run: true } });
    check('R: reset dry_run → 200', status, 200);
    check('R: hlásí, kolik granul by smazal', body?.smazal_bych_granuli, 7);
    check('R: hlásí, kolika úkolů by se dotkl', body?.dotklo_bych_se_ukolu, 2);
    check('R: a NEMAZAL', stav.resetSmazano, 0);
    check('R: a nezapsal DELETE', bylZapis(log, /DELETE FROM roadmap/), false);
  }

  // ── R2) /roadmap/reset: neznámá hra → 404 a NEMAZAT ──────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav } = envFor({ aktivniHra: true, resetGame: null, resetPocet: 7 });
    const { status, body } = await post(mod, env, '/roadmap/reset',
      { telo: { game_id: 'neexistuje' } });
    check('R2: neznámá hra → 404', status, 404);
    check('R2: a řekne kterou', body?.game_id, 'neexistuje');
    check('R2: a NEMAZAL', stav.resetSmazano, 0);
  }

  // ── R3) /roadmap/reset: ostrý běh smaže cache (frontu postaví další tik) ─
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, body, stav } = envFor({ aktivniHra: true, resetPocet: 7 });
    const vysledek = await post(mod, env, '/roadmap/reset', { telo: {} });
    check('R3: ostrý reset → 200', vysledek.status, 200);
    check('R3: hlásí smazané granule', vysledek.body?.smazano_granuli, 7);
    check('R3: cache se OPRAVDU smazala', stav.resetSmazano, 7);
    check('R3: a odpověď říká, že fronta přijde v dalším tiku',
      /znovu postaví v dalším tiku/.test(String(vysledek.body?.poznamka || '')), true);
  }

  // ── S) tajemství: všechny chráněné endpointy ho VYŽADUJÍ ─────────────────
  // ⚠ `/health` tu ZÁMĚRNĚ NENÍ: je veřejný (hlídá ho monitoring dostupnosti)
  // a jeho veřejnost testuje blok X.
  {
    const chranene = ['/poll', '/claim', '/heartbeat', '/tasks/cleanup', '/roadmap/reset',
                      '/queue', '/roadmap', '/failed', '/status', '/workers', '/games'];
    const bez = [];
    for (const cesta of chranene) {
      const calls = [];
      stubGithub(calls, { aktivniHra: true });
      const { env } = envFor({ aktivniHra: true });
      const { status } = await post(mod, env, cesta, { telo: {}, secret: 'spatne' });
      if (status !== 401) bez.push(`${cesta} → ${status}`);
    }
    check('S: každý chráněný endpoint vrátí bez tajemství 401', bez, []);
  }

  // ══════════════════════════════════════════════════════════════════════════
  // P25 / Úkol B1 — ENDPOINTY, KTERÉ ZAPISUJÍ DO D1 A MĚNÍ CHOVÁNÍ SLUŽBY
  // (`POST /task`, `POST /game`, `POST /game/active`)
  //
  // PROČ PRÁVĚ TYHLE: P24 zavřela pět cest, které netestoval nikdo — ale
  // `/task` ZAKLÁDÁ ÚLOHU a `/game` + `/game/active` mění REGISTR HER, tedy to,
  // co orchestra vůbec dělá (vypnutá hra = orchestra nedispatchuje). „Vada,
  // kterou nikdo nezměří, se pozná až tím, že se něco stane."
  // ══════════════════════════════════════════════════════════════════════════

  // ── T) /task: založí úlohu (a co se opravdu posílá do D1) ────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, vazby } = envFor({ aktivniHra: true });
    const { status, body } = await post(mod, env, '/task', {
      telo: { title: 'Nová granule', kind: 'test', prompt: 'neco',
              payload: { game: 'test', grain: 'x' } },
    });
    check('T: /task odpoví 200', status, 200);
    check('T: /task vrátí id nové úlohy', body?.id, 42);
    check('T: /task vrátí target `cloud` (výchozí)', body?.target, 'cloud');
    check('T: INSERT do `tasks` proběhl', bylZapis(log, /INSERT INTO tasks/), true);
    const v = vazby.find((x) => /INSERT INTO tasks/.test(x.sql));
    check('T: INSERT nese 5 hodnot (title, kind, target, prompt, payload)',
      Array.isArray(v?.args) ? v.args.length : null, 5);
    check('T: `title` jde do INSERTu', v?.args?.[0], 'Nová granule');
    check('T: `kind` jde do INSERTu', v?.args?.[1], 'test');
    // Payload se musí uložit jako ŘETĚZEC: kdyby šel objekt, D1 by dostal
    // `[object Object]` a granule by přišla o `game`/`grain` (dispatch by ji
    // nevydal nebo by ji vydal bez klíče).
    check('T: payload se ukládá jako JSON ŘETĚZEC (ne objekt)',
      typeof v?.args?.[4], 'string');
    check('T: a v payloadu je skutečný obsah',
      JSON.parse(String(v?.args?.[4] || '{}')).grain, 'x');
  }

  // ── T2) /task s `target: "lan"` → fronta domácího uzlu ───────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, vazby } = envFor({ aktivniHra: true });
    const { body } = await post(mod, env, '/task', {
      telo: { title: 'LAN úloha', prompt: 'x', target: 'lan' },
    });
    check('T2: /task vrátí target `lan`', body?.target, 'lan');
    const v = vazby.find((x) => /INSERT INTO tasks/.test(x.sql));
    check('T2: a do INSERTu jde `lan` (ne `cloud`)', v?.args?.[2], 'lan');
  }

  // ── T3) /task bez `title` → 400 a ŽÁDNÝ INSERT ──────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/task',
      { telo: { prompt: 'bez titulku' } });
    check('T3: /task bez `title` → 400', status, 400);
    check('T3: a NEZALOŽIL úlohu', bylZapis(log, /INSERT INTO tasks/), false);
  }

  // ── T4) /task s neznámým target → `cloud` (žádný tichý nesmysl) ─────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, vazby } = envFor({ aktivniHra: true });
    const { body } = await post(mod, env, '/task', {
      telo: { title: 'x', prompt: 'y', target: 'neexistuje' },
    });
    check('T4: neznámý target se srazí na `cloud`', body?.target, 'cloud');
    const v = vazby.find((x) => /INSERT INTO tasks/.test(x.sql));
    check('T4: a do INSERTu jde `cloud`', v?.args?.[2], 'cloud');
  }

  // ── T5) /task se špatným tajemstvím → 401 a ŽÁDNÝ INSERT ────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/task',
      { telo: { title: 'x', prompt: 'y' }, secret: 'spatne' });
    check('T5: /task se špatným tajemstvím → 401', status, 401);
    check('T5: a nic se nezaložilo', bylZapis(log, /INSERT INTO tasks/), false);
  }

  // ── U) /game: registrace hry ji ZAPNE (`active = 1`) ────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, vazby } = envFor({ aktivniHra: true });
    const { status, body } = await post(mod, env, '/game',
      { telo: { game_id: 'test', repo: 'test/hra' } });
    check('U: /game odpoví 200', status, 200);
    check('U: /game vrátí `ok: true` a hru', [body?.ok, body?.game_id], [true, 'test']);
    check('U: zápis je UPSERT (ne pád na duplicitní klíč)',
      bylZapis(log, /INSERT INTO games .*ON CONFLICT\(game_id\) DO UPDATE/s), true);
    // ⚠ TOHLE JE TO PODSTATNÉ: registrace musí hru ZAPNOUT — jinak by nová hra
    //    zůstala `active = 0` a orchestra by na ní nikdy nezačala pracovat.
    check('U: a registrace hru ZAPNE (`active = 1`)',
      bylZapis(log, /ON CONFLICT\(game_id\) DO UPDATE SET[\s\S]*active = 1/), true);
    const v = vazby.find((x) => /INSERT INTO games/.test(x.sql));
    check('U: `game_id` a `repo` jdou do INSERTu',
      [v?.args?.[0], v?.args?.[1]], ['test', 'test/hra']);
    check('U: výchozí `roadmap_file` je `.forge/roadmap.json`',
      v?.args?.[2], '.forge/roadmap.json');
  }

  // ── U2) /game bez `repo` → 400 a ŽÁDNÝ zápis ────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/game', { telo: { game_id: 'test' } });
    check('U2: /game bez `repo` → 400', status, 400);
    check('U2: a nic se nezapsalo', bylZapis(log, /INSERT INTO games/), false);
  }

  // ── U3) /game se špatným tajemstvím → 401 a ŽÁDNÝ zápis ─────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/game',
      { telo: { game_id: 'test', repo: 'test/hra' }, secret: 'spatne' });
    check('U3: /game se špatným tajemstvím → 401', status, 401);
    check('U3: a nic se nezapsalo', bylZapis(log, /INSERT INTO games/), false);
  }

  // ── V) /game/active: VYPNUTÍ hry (`active: false`) ──────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log, vazby } = envFor({ aktivniHra: true });
    const { status, body } = await post(mod, env, '/game/active',
      { telo: { game_id: 'test', active: false } });
    check('V: /game/active odpoví 200', status, 200);
    check('V: a vrátí `active: 0`', body?.active, 0);
    check('V: UPDATE do `games` proběhl', bylZapis(log, /UPDATE games SET active/), true);
    const v = vazby.find((x) => /UPDATE games SET active/.test(x.sql));
    check('V: do DB jde `active = 0` (ne 1)', v?.args?.[0], 0);
    check('V: a hra se hledá podle `game_id`', v?.args?.[1], 'test');
  }

  // ── V2) /game/active BEZ `active` → ZAPNE (výchozí 1) ───────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, vazby } = envFor({ aktivniHra: true });
    const { body } = await post(mod, env, '/game/active', { telo: { game_id: 'test' } });
    check('V2: bez `active` se hra ZAPNE (`active: 1`)', body?.active, 1);
    const v = vazby.find((x) => /UPDATE games SET active/.test(x.sql));
    check('V2: a do DB jde 1', v?.args?.[0], 1);
  }

  // ── V3) /game/active: neznámá hra → 404 a stav se NEPŘEPNE ──────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav } = envFor({ aktivniHra: true, gameChanges: 0 });
    const { status, body } = await post(mod, env, '/game/active',
      { telo: { game_id: 'neexistuje', active: false } });
    check('V3: neznámá hra → 404', status, 404);
    check('V3: a odpověď řekne kterou hru', body?.game_id, 'neexistuje');
    check('V3: a stav hry se NEZMĚNIL (0 změněných řádků ≠ přepnuto)',
      stav.posledniActive, undefined);
  }

  // ── V4) /game/active bez `game_id` → 400 ────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/game/active', { telo: { active: false } });
    check('V4: /game/active bez `game_id` → 400', status, 400);
    check('V4: a nic se nepřepnulo', bylZapis(log, /UPDATE games SET active/), false);
  }

  // ── V5) /game/active se špatným tajemstvím → 401 ────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true });
    const { status } = await post(mod, env, '/game/active',
      { telo: { game_id: 'test', active: false }, secret: 'spatne' });
    check('V5: /game/active se špatným tajemstvím → 401', status, 401);
    check('V5: a nic se nepřepnulo', bylZapis(log, /UPDATE games SET active/), false);
  }

  // ── W) INTEGRACE: vypnutá hra → tik NEDISPATCHUJE; zapnutá → dispatchuje ─
  // Tohle je smysl celého `/game/active`: registr her není „data", je to
  // ROZHODNUTÍ o tom, co orchestra dělá. Test to měří na CHOVÁNÍ tiku.
  {
    const cfg = { aktivniHra: true };
    const calls = [];
    stubGithub(calls, cfg);
    const { env, stav } = envFor(cfg);
    const vyp = await post(mod, env, '/game/active',
      { telo: { game_id: 'test', active: false } });
    check('W: hru jde vypnout (`/game/active false`)', vyp.body?.active, 0);
    await tick(mod, env);
    check('W: po VYPNUTÍ hry tik NEDISPATCHUJE', calls.filter(jeDispatch).length, 0);
    const zap = await post(mod, env, '/game/active', { telo: { game_id: 'test' } });
    check('W: hru jde zase zapnout', zap.body?.active, 1);
    const calls2 = [];
    stubGithub(calls2, cfg);
    await tick(mod, env);
    check('W: po ZAPNUTÍ hry tik dispatchuje PRÁVĚ JEDNOU',
      calls2.filter(jeDispatch).length, 1);
    check('W: přepnutí hry proběhla právě 2×', stav.prepnutoHry, 2);
  }

  // ══════════════════════════════════════════════════════════════════════════
  // P27 / Úkol B1 — SEDM ENDPOINTŮ, KTERÉ NEVOLAL ŽÁDNÝ TEST
  // (`/health`, `/queue`, `/roadmap`, `/failed`, `/status`, `/workers`, `/games`)
  //
  // PROČ: do 7. 10. 2026 je nevolal NIKDO (naměřeno: `post(mod, env, '/health'|…)`
  // → 0 výskytů) — a to jsou endpointy, které orchestra používá pro diagnostiku
  // i pro člověka. „Vada, kterou nikdo nezměří, se pozná až tím, že se něco
  // stane." Každý blok tvrdí **TVAR i OBSAH** odpovědi, ne jen `status === 200`.
  // ══════════════════════════════════════════════════════════════════════════

  // ── X) /health: stav SLUŽBY zvlášť od stavu CÍLE (N0.3) ──────────────────
  {
    const calls = [];
    const hra = { ...GAME_ROW, repo: 'test/hra1' };
    stubGithub(calls, {
      aktivniHra: true, hryRadky: [hra],
      ciRuny: [{ status: 'completed', conclusion: 'success', head_sha: 'abc',
                 run_number: 5, html_url: 'https://x/ci' }],
      // 2 selhání, pak úspěch, pak nedokončený → `selhani_v_rade` musí být 2
      // a `ok` musí být `false` (tvrzení o POSLEDNÍM DOKONČENÉM běhu).
      agentRuny: [
        { status: 'completed', conclusion: 'failure', run_number: 323, html_url: 'https://x/a1' },
        { status: 'completed', conclusion: 'failure', run_number: 322, html_url: 'https://x/a2' },
        { status: 'completed', conclusion: 'success', run_number: 321, html_url: 'https://x/a3' },
        { status: 'in_progress', conclusion: null, run_number: 324, html_url: 'https://x/a4' },
      ],
    });
    const { env } = envFor({ aktivniHra: true, readyCount: 4, bezi: 2,
                             hryRadky: [hra], workersRadky: [WORKER_ROW] });
    const { status, body } = await get(mod, env, '/health');
    check('X: /health jde BEZ tajemství (veřejný pro monitoring)', status, 200);
    check('X: /health hlásí `ok: true` (služba žije)', body?.ok, true);
    check('X: `ready` je z D1 (ne zapečená 1)', body?.ready, 4);
    check('X: `running` je z D1', body?.running, 2);
    check('X: `games` = počet AKTIVNÍCH her z D1', body?.games, 1);
    check('X: /health vrací uzly i s `kinds` a `last_seen`',
      [body?.workers?.[0]?.name, body?.workers?.[0]?.kinds,
       typeof body?.workers?.[0]?.last_seen],
      ['pc-domaci', 'assets,test', 'string']);
    check('X: stav CÍLE je v `targets` (ne v `ok`)', body?.targets?.[0]?.game_id, 'test');
    check('X: a míří na REPO z D1', body?.targets?.[0]?.repo, 'test/hra1');
    check('X: poslední CI cíle je naměřené (conclusion)',
      body?.targets?.[0]?.main_ci?.conclusion, 'success');
    check('X: `forge.ok` je tvrzení o POSLEDNÍM DOKONČENÉM běhu',
      body?.targets?.[0]?.forge?.ok, false);
    check('X: `selhani_v_rade` počítá do prvního ÚSPĚCHU (2, ne 3)',
      body?.targets?.[0]?.forge?.selhani_v_rade, 2);
    check('X: a cíl je NAMĚŘENÝ (`error` je null)', body?.targets?.[0]?.error, null);
  }

  // ── X2) /health: TTL cache stavu cíle (jinak by to byl GitHub provoz) ────
  {
    const calls = [];
    const hra = { ...GAME_ROW, repo: 'test/hra2' };
    stubGithub(calls, { aktivniHra: true, hryRadky: [hra], ciRuny: [], agentRuny: [] });
    const { env } = envFor({ aktivniHra: true, hryRadky: [hra] });
    const prvni = await get(mod, env, '/health');
    const druhe = await get(mod, env, '/health');
    check('X2: druhé volání /health nezatíží GitHub znovu (cache)',
      calls.filter((u) => u.includes('/actions/workflows/')).length, 2);
    check('X2: a obě odpovědi nesou TÝŽ stav cíle',
      JSON.stringify(prvni.body?.targets), JSON.stringify(druhe.body?.targets));
  }

  // ── X3) /health: cíl NEJDE změřit → „nezměřeno“ musí být VIDĚT ───────────
  {
    const calls = [];
    const hra = { ...GAME_ROW, repo: 'test/hra3' };
    stubGithub(calls, { aktivniHra: true, hryRadky: [hra], ciChyba: true });
    const { env } = envFor({ aktivniHra: true, hryRadky: [hra] });
    const { status, body } = await get(mod, env, '/health');
    check('X3: /health odpoví 200 i když cíl nejde změřit', status, 200);
    check('X3: `main_ci` zůstane null (nezměřeno ≠ zelená)',
      body?.targets?.[0]?.main_ci, null);
    check('X3: `forge` zůstane null', body?.targets?.[0]?.forge, null);
    check('X3: a JE VIDĚT důvod (`error` není null)',
      typeof body?.targets?.[0]?.error, 'string');
    check('X3: `ok` služby tím NENÍ dotčeno', body?.ok, true);
  }

  // ── Y) /queue: fronta úloh i se stavem a pokusy ──────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, queueRadky: [TASK_ROW] });
    const { status, body } = await post(mod, env, '/queue');
    check('Y: /queue odpoví 200', status, 200);
    check('Y: /queue vrací úlohy z D1 (ne prázdno)', body?.tasks?.length, 1);
    check('Y: a nese STAV i POKUSY (bez nich se fronta ladit nedá)',
      [body?.tasks?.[0]?.status, body?.tasks?.[0]?.attempts], ['ready', 2]);
    check('Y: a `title`/`kind`/`target` jdou z D1',
      [body?.tasks?.[0]?.title, body?.tasks?.[0]?.kind, body?.tasks?.[0]?.target],
      ['Hotová úloha', 'code', 'cloud']);
    check('Y: čte se LIMIT 50 od NEJNOVĚJŠÍCH',
      bylZapis(log, /FROM tasks ORDER BY id DESC LIMIT 50/), true);
  }

  // ── Y2) /queue: prázdná fronta je `[]`, ne `null` (tvar pro klienta) ────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, queueRadky: [] });
    const { status, body } = await post(mod, env, '/queue');
    check('Y2: prázdná fronta → 200 a `tasks: []`',
      [status, body?.tasks], [200, []]);
  }

  // ── Y3) /queue GET se špatným tajemstvím → 401 a ŽÁDNÝ dotaz do D1 ───────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, queueRadky: [TASK_ROW] });
    const { status } = await get(mod, env, '/queue',
      { hlavicky: { 'x-forge-secret': 'spatne' } });
    check('Y3: /queue GET se špatným tajemstvím → 401', status, 401);
    check('Y3: a do D1 se vůbec nešlo', log.length, 0);
  }

  // ── Z) /roadmap: cache roadmapy (LEFT JOIN, aby byly vidět i osiřelé) ────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, roadmapRadky: [ROADMAP_ROW] });
    const { status, body } = await post(mod, env, '/roadmap');
    check('Z: /roadmap odpoví 200', status, 200);
    check('Z: vrací granuli i se stavem ÚKOLU (z JOINu)',
      [body?.roadmap?.[0]?.item_id, body?.roadmap?.[0]?.status,
       body?.roadmap?.[0]?.task_status],
      ['test/grain.jedna', 'queued', 'ready']);
    check('Z: a s POKUSY (podle nich se pozná zaseknutá granule)',
      body?.roadmap?.[0]?.attempts, 2);
    check('Z: dotaz je LEFT JOIN — i granule BEZ úkolu musí být vidět',
      bylZapis(log, /FROM roadmap r LEFT JOIN tasks t/), true);
  }

  // ── Z2) /roadmap: prázdná cache je `[]` ─────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, roadmapRadky: [] });
    const { body } = await post(mod, env, '/roadmap');
    check('Z2: prázdná roadmapa → `roadmap: []`', body?.roadmap, []);
  }

  // ── AA) /failed: podklad pro `forge replan` ──────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, failedRadky: [FAILED_TASK],
                                  failedRuny: [FAILED_RUN] });
    const { status, body } = await post(mod, env, '/failed');
    check('AA: /failed odpoví 200', status, 200);
    check('AA: vrací SELHANOU úlohu', body?.tasks?.[0]?.id, 12);
    check('AA: `payload` je ROZBALENÝ objekt (klient nemá parsovat řetězec)',
      typeof body?.tasks?.[0]?.payload, 'object');
    check('AA: a nese repo i grain',
      [body?.tasks?.[0]?.payload?.game, body?.tasks?.[0]?.payload?.grain],
      ['test', 'x']);
    check('AA: běh je PŘIŘAZENÝ podle `task_id` (ne podle jména)',
      body?.tasks?.[0]?.runs?.[0]?.run_key, 'klic-selhal');
    // Strop 2000 znaků: bez něj by odpověď nesla celý log a `log_tail` by
    // přestal být „ocásek" (a klient by dostal megabajty).
    check('AA: `log_tail` je ZKRÁCENÝ na 2000 znaků',
      body?.tasks?.[0]?.runs?.[0]?.log_tail?.length, 2000);
    check('AA: úloha BEZ běhů má `runs: []` (ne `undefined`)',
      Array.isArray(body?.tasks?.[0]?.runs), true);
    check('AA: čtou se jen NEDOKONČENÉ a NEÚSPĚŠNÉ běhy',
      bylZapis(log, /FROM runs WHERE status NOT IN \('success', 'running'\)/), true);
  }

  // ── AA2) /failed: úloha s nesmyslným `payload` neshodí endpoint ──────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, failedRuny: [],
                             failedRadky: [{ ...FAILED_TASK, id: 13, payload: 'neni-json' }] });
    const { status, body } = await post(mod, env, '/failed');
    check('AA2: rozbitý `payload` neshodí endpoint', status, 200);
    check('AA2: a vrátí `{}`, ne pád', body?.tasks?.[0]?.payload, {});
  }

  // ── AA3) /failed: prázdno → `tasks: []` ─────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, failedRadky: [], failedRuny: [] });
    const { body } = await post(mod, env, '/failed');
    check('AA3: žádné selhané úlohy → `tasks: []`', body?.tasks, []);
  }

  // ── AB) /status: běhy i s titulem úlohy (JOIN) ───────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, statusRuny: [STATUS_RUN] });
    const { status, body } = await post(mod, env, '/status');
    check('AB: /status odpoví 200', status, 200);
    check('AB: vrací běh i s `title` z JOINu a uzlem',
      [body?.runs?.[0]?.title, body?.runs?.[0]?.status, body?.runs?.[0]?.worker],
      ['Hotová úloha', 'success', 'pc-domaci']);
    check('AB: a s odkazem na PR', body?.runs?.[0]?.pr_url, 'https://x/1');
    check('AB: čte se 20 nejnovějších běhů',
      bylZapis(log, /FROM runs r LEFT JOIN tasks t .*LIMIT 20/), true);
  }

  // ── AB2) /status: prázdno → `runs: []` ──────────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, statusRuny: [] });
    const { body } = await post(mod, env, '/status');
    check('AB2: žádné běhy → `runs: []`', body?.runs, []);
  }

  // ── AC) /workers: registrované uzly (podle nich se přiděluje práce) ──────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, workersVse: [WORKER_ROW] });
    const { status, body } = await post(mod, env, '/workers');
    check('AC: /workers odpoví 200', status, 200);
    check('AC: vrací uzly z D1 včetně `last_seen`',
      [body?.workers?.[0]?.name, body?.workers?.[0]?.last_seen],
      ['pc-domaci', '2026-10-07T16:00:00Z']);
    check('AC: a `kinds` (bez nich uzel žádnou práci nedostane)',
      body?.workers?.[0]?.kinds, 'assets,test');
    check('AC: čte se CELÝ řádek (`SELECT *`), ne vybrané sloupce',
      bylZapis(log, /SELECT \* FROM workers ORDER BY last_seen DESC/), true);
  }

  // ── AC2) /workers: prázdno → `workers: []` ──────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, workersVse: [] });
    const { body } = await post(mod, env, '/workers');
    check('AC2: žádné uzly → `workers: []`', body?.workers, []);
  }

  // ── AD) /games: registr her VČETNĚ VYPNUTÝCH ────────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, log } = envFor({ aktivniHra: true, gamesRadky: [GAME_ROW, GAME_OFF] });
    const { status, body } = await post(mod, env, '/games');
    check('AD: /games odpoví 200', status, 200);
    // ⚠ ROZDÍL PROTI `/health`: `/health` vidí JEN aktivní hry, registr vidí
    // i VYPNUTÉ — kdyby `/games` filtroval `active=1`, vypnutá hra by
    // z administrace ZMIZELA (a nešla by znovu zapnout).
    check('AD: registr vrací I VYPNUTOU hru',
      body?.games?.map((g) => g.game_id), ['test', 'stara']);
    check('AD: a `active` u každé hry', body?.games?.map((g) => g.active), [1, 0]);
    check('AD: čte se BEZ filtru na `active`',
      bylZapis(log, /SELECT \* FROM games ORDER BY game_id/), true);
    check('AD: a filtr `active=1` v tom dotazu NENÍ',
      bylZapis(log, /SELECT \* FROM games[^;]*active=1/), false);
  }

  // ── AD2) /games: prázdný registr → `games: []` ──────────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({ aktivniHra: true, gamesRadky: [] });
    const { body } = await post(mod, env, '/games');
    check('AD2: prázdný registr → `games: []`', body?.games, []);
  }

  // ── AE) P29/B6: OSIŘELÉ ŘÁDKY CACHE SE UKLÍZEJÍ SAMY ─────────────────────
  // Naměřeno ŽIVĚ 9. 10. 2026 (`POST /tasks/cleanup?dry_run`): 21 granulí
  // v souborech, **25 řádků v cache, 5 osiřelých** — z toho `entity.enemy`
  // s úlohou **#239 `ready`**. Ruční úklid existoval, ale nikdo ho nevolal.
  {
    const ORPHAN = {
      item_id: 'test/stara', task_id: 9, rstatus: 'queued', tstatus: 'ready',
      rupd: '2026-10-07T10:00:00Z',
    };
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env, stav, vazby } = envFor({
      aktivniHra: true, roadmapRadky: [ROADMAP_ROW, ORPHAN],
    });
    const { body } = await tick(mod, env);
    check('AE: osiřelý řádek cache se SMAŽE', stav.smazaneRadky, 1);
    check('AE: a maže se KONKRÉTNÍ item_id (ne naslepo)',
      vazby.filter((v) => /DELETE FROM roadmap WHERE item_id = \?/.test(v.sql))
        .map((v) => v.args[0]), ['test/stara']);
    check('AE: řádek, jehož granule V SOUBORU JE, se NEMAŽE',
      vazby.some((v) => v.args?.[0] === 'test/grain.jedna'), false);
    check('AE: tik počet uklizených řádků VYPÍŠE (jinak je úklid tichý)',
      /osiřelých řádků uklizeno: 1/.test(String(body?.message || '')), true);
  }

  // ── AE2) POJISTKA: nenačtená roadmapa NESMÍ mazat ───────────────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true, contentsChyba: true });
    const { env, stav, log } = envFor({
      aktivniHra: true,
      roadmapRadky: [ROADMAP_ROW, { item_id: 'test/stara', task_id: 9 }],
    });
    await tick(mod, env);
    check('AE2: roadmapu hry jsme se OPRAVDU pokusili přečíst',
      calls.some((u) => u.includes('/contents/')), true);
    check('AE2: nenačtená roadmapa → ŽÁDNÉ mazání', stav.smazaneRadky, 0);
    check('AE2: a v logu není ani DELETE', bylZapis(log, /DELETE FROM roadmap/), false);
  }

  // ── AE3) STROP GRANULE SE POJMENUJE (dřív `find()` mlčel) ───────────────
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({
      aktivniHra: true, roadmapRadky: [ROADMAP_ROW], grainMaxRuns: '8',
      granuleRuns: [{ item_id: 'test/grain.jedna', runs: 9 }],
    });
    const { body } = await tick(mod, env);
    const zprava = String(body?.message || '');
    check('AE3: granule nad stropem se NEVYDÁ', /spusteno: 0 úloh/.test(zprava), true);
    check('AE3: a tik strop POJMENUJE i s číslem (dřív ticho)',
      /STROP GRANULE 9\/8 \(test\/grain\.jedna\)/.test(zprava), true);
  }

  // ── AE4) COOLDOWN SE POJMENUJE (SQL ho vyfiltruje dřív, než ho `find()` vidí)
  {
    const calls = [];
    stubGithub(calls, { aktivniHra: true });
    const { env } = envFor({
      aktivniHra: true, roadmapRadky: [ROADMAP_ROW], taskStatus: 'failed',
      cooldownUlohy: [{ id: 7 }, { id: 8 }],
    });
    const { body } = await tick(mod, env);
    check('AE4: tik vypíše, KOLIK úloh drží cooldown a které',
      /v cooldownu 2 úloh: #7, #8/.test(String(body?.message || '')), true);
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

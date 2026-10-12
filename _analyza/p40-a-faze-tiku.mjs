// p40-a-faze-tiku.mjs — ROZKLAD CENY TIKU PO FÁZÍCH (zadání P40, krok 1).
//
// PROČ VLASTNÍ NÁSTROJ (H191): sonda s PEVNÝM jménem výstupu přepíše cizí
// doklad. Tenhle má vlastní jména (`p40-a-faze-tiku-vystup.txt`, `p40-data/`).
//
// CO MĚŘÍ:
//   1. REÁLNÝ HANDLER: `wrangler deploy --dry-run` zbundluje conductor a nástroj
//      zavolá SKUTEČNÝ `scheduled()` (cron tik) i SKUTEČNÝ `POST /tick`.
//      Logika se NEOPISUJE — měří se skutečná práce tiku.
//   2. REÁLNÉ PAYLOADY: odpovědi GitHubu se stáhnou ŽIVĚ (`--zive`) a uloží do
//      `_analyza/p40-data/`; falešný GitHub je vrací BAJT NA BAJT, takže
//      `JSON.parse` měří skutečná data (Node = týž engine V8 jako Workers).
//   3. DISJUNKTNÍ FÁZE: obalí se `JSON.parse`, `atob`, `TextDecoder.decode`,
//      každý dotaz D1 a každé volání `fetch`. Buckety se NEPŘEKRÝVAJÍ, takže
//      součet je rozklad a zbytek je pojmenovaný („logika + JIT“).
//
// ⚠ METODIKA (bez ní čísla lžou — naměřeno 12. 10. 2026):
//   * `process.cpuUsage()` má na Windows kvantum ~16 ms → na fáze se NEPOUŽÍVÁ
//     (první verze hlásila u všech fází 0.00 ms). Měří se `hrtime`.
//   * Každý tik se pouští v ČERSTVÉM modulu (import s novým klíčem) — v produkci
//     dostane cron tik čerstvý izolát (H178), takže modulové cache (`schemaMigrovan`)
//     jsou studené. První iterace se zahazuje (JIT), reportuje se MEDIÁN ze zbytku.
//   * Falešná D1 je SYNCHRONNÍ (žádné I/O) → její wall time je režie `await` +
//     Promise. Skutečnou režii prohlížeče D1 měří živá sonda `p40-probe`.
//
// Použití:
//   node _analyza/p40-a-faze-tiku.mjs            # z cache payloadů
//   node _analyza/p40-a-faze-tiku.mjs --zive     # znovu stáhne payloady z GitHubu
//   node _analyza/p40-a-faze-tiku.mjs -n 25      # počet iterací (default 15)
// Exit 0 = změřeno; 1 = build/payload selhal.

import { spawnSync } from 'node:child_process';
import { existsSync, mkdirSync, readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';

const WS = dirname(dirname(fileURLToPath(import.meta.url)));
const CONDUCTOR = join(WS, 'conductor');
const SCRATCH = join(WS, '_analyza', 'p40-tick-scratch');
const BUNDLE = join(SCRATCH, 'index.js');
const DATA = join(WS, '_analyza', 'p40-data');
const OUT = join(WS, '_analyza', 'p40-a-faze-tiku-vystup.txt');
const REPO = 'ssevcikm-spec/uo-shadows';
const ROADMAP = '.forge/roadmap.json';
const PAT = readFileSync(join(WS, '.secrets', 'github_pat.txt'), 'utf8').trim();
const SECRET = 'tajemstvi-p40';
const N = (() => { const i = process.argv.indexOf('-n'); return i > 0 ? Number(process.argv[i + 1]) : 15; })();

const radky = [];
const zapis = (x = '') => { radky.push(x); console.log(x); };
const median = (a) => { const s = [...a].sort((x, y) => x - y); return s.length ? s[Math.floor(s.length / 2)] : NaN; };
const ms = (ns) => Number(ns) / 1e6;
const zaokr = (x, n = 2) => (Number.isFinite(x) ? Number(x).toFixed(n) : '?');

// ─────────────────────────────────────────────────────────── build ──────────
function build() {
  mkdirSync(SCRATCH, { recursive: true });
  const wrangler = join(CONDUCTOR, 'node_modules', 'wrangler', 'bin', 'wrangler.js');
  if (!existsSync(wrangler)) { console.log(`CHYBA: chybi wrangler (${wrangler})`); process.exit(1); }
  const r = spawnSync(process.execPath,
    [wrangler, 'deploy', '--dry-run', '--outdir', SCRATCH],
    { cwd: CONDUCTOR, encoding: 'utf8' });
  if (r.status !== 0 || !existsSync(BUNDLE)) {
    console.log('CHYBA: `wrangler deploy --dry-run` selhal:');
    console.log(String(r.stderr || r.stdout || '').slice(-1500));
    process.exit(1);
  }
}

// ─────────────────────────────────────────────── živé payloady GitHubu ──────
const CESTY = [
  '/pulls?state=closed&per_page=100&sort=updated&direction=desc',
  '/pulls?state=open&per_page=30',
  `/contents/${ROADMAP}`,
  '/actions/runs?event=workflow_dispatch&per_page=50',
  '/git/trees/origin%2Fmain?recursive=1',
];

async function stahni(zive) {
  mkdirSync(DATA, { recursive: true });
  const cache = join(DATA, 'payloady.json');
  if (!zive && existsSync(cache)) return JSON.parse(readFileSync(cache, 'utf8'));
  const HLAV = {
    Authorization: `Bearer ${PAT}`,
    Accept: 'application/vnd.github+json',
    'X-GitHub-Api-Version': '2022-11-28',
    'User-Agent': 'forge-conductor',
  };
  const out = {};
  for (const cesta of CESTY) {
    const r = await fetch(`https://api.github.com/repos/${REPO}${cesta}`, { headers: HLAV });
    const text = await r.text();
    out[cesta] = { status: r.status, text, bajtu: Buffer.byteLength(text, 'utf8') };
  }
  const raw = await fetch(`https://raw.githubusercontent.com/${REPO}/main/${ROADMAP}`);
  const rawText = await raw.text();
  out['RAW ' + ROADMAP] = { status: raw.status, text: rawText, bajtu: Buffer.byteLength(rawText, 'utf8') };
  // GraphQL varianta téhož dotazu (kandidát na zlevnění — viz p40-d)
  const gql = await fetch('https://api.github.com/graphql', {
    method: 'POST',
    headers: { ...HLAV, 'content-type': 'application/json' },
    body: JSON.stringify({
      query: 'query($owner: String!, $name: String!) { repository(owner: $owner, name: $name) { pullRequests(states: MERGED, last: 100, orderBy: {field: UPDATED_AT, direction: DESC}) { nodes { title headRefName } } } }',
      variables: { owner: REPO.split('/')[0], name: REPO.split('/')[1] },
    }),
  });
  const gqlText = await gql.text();
  out['GRAPHQL'] = { status: gql.status, text: gqlText, bajtu: Buffer.byteLength(gqlText, 'utf8') };
  writeFileSync(cache, JSON.stringify(out), 'utf8');
  return out;
}

// ─────────────────── měřidla: disjunktní buckety (obalují reálný kód) ───────
function meraky() {
  const ucty = { json: 0, atob: 0, decode: 0, d1: 0, fetch: 0, batchVolani: 0, roundtrips: 0 };
  const podleJson = new Map();
  let jsonHloubka = 0;
  const puvodniParse = JSON.parse;
  const puvodniAtob = globalThis.atob;
  const puvodniDecode = TextDecoder.prototype.decode;
  const puvodniFetch = globalThis.fetch;

  let url = '';
  JSON.parse = function (...a) {
    // Vnořený JSON.parse uvnitř jiného (např. res.json() → parse) se počítá jen JEDNOU.
    if (jsonHloubka > 0) return puvodniParse.apply(this, a);
    const t = process.hrtime.bigint();
    jsonHloubka++;
    try { return puvodniParse.apply(this, a); }
    finally {
      jsonHloubka--;
      const c = ms(process.hrtime.bigint() - t);
      ucty.json += c;
      const k = url || '(přímý JSON.parse)';
      podleJson.set(k, (podleJson.get(k) || 0) + c);
    }
  };
  globalThis.atob = function (...a) {
    const t = process.hrtime.bigint();
    try { return puvodniAtob.apply(this, a); }
    finally { ucty.atob += ms(process.hrtime.bigint() - t); }
  };
  TextDecoder.prototype.decode = function (...a) {
    const t = process.hrtime.bigint();
    try { return puvodniDecode.apply(this, a); }
    finally { ucty.decode += ms(process.hrtime.bigint() - t); }
  };
  return {
    ucty, podleJson,
    obalFetch(f) { globalThis.fetch = async (u, init) => { url = String(u); const t = process.hrtime.bigint(); try { return await f(u, init); } finally { ucty.fetch += ms(process.hrtime.bigint() - t); } }; },
    vrat() {
      JSON.parse = puvodniParse; globalThis.atob = puvodniAtob;
      TextDecoder.prototype.decode = puvodniDecode; globalThis.fetch = puvodniFetch;
    },
  };
}

// ─────────────────────────────── falešná D1 (měří každý dotaz zvlášť) ───────
function fakeSvet(payloady, ucty) {
  const roadmapDoc = JSON.parse(Buffer.from(
    JSON.parse(payloady[`/contents/${ROADMAP}`].text).content.replace(/\n/g, ''), 'base64').toString('utf8'));
  const grains = roadmapDoc.grains || [];
  const hotove = grains.filter((g) => g.done === true).map((g) => g.id);
  const cekajici = grains.filter((g) => g.done !== true).map((g) => g.id);
  const taskId = { 'engine.input': 244, 'world.bodies': 245, 'engine.shell': 246 };
  const itemId = (id) => `uo-shadows/${id}`;
  const roadmapRadky = grains.map((g) => ({
    item_id: itemId(g.id),
    task_id: hotove.includes(g.id) ? null : (taskId[g.id] ?? null),
    rstatus: hotove.includes(g.id) ? 'done' : 'queued',
    rupd: '2026-10-11T18:00:00Z',
    rfail: null,
    tstatus: hotove.includes(g.id) ? 'done' : 'ready',
    tupd: '2026-10-11T18:00:00Z',
  }));

  const log = [];
  const nezname = [];
  const strop = new Map(cekajici.map((id) => [itemId(id), 8]));   // GRAIN_MAX_RUNS=8
  const normal = (s) => String(s).replace(/\s+/g, ' ').trim();

  const first = (sql) => {
    if (/COUNT\(\*\) AS n FROM runs WHERE status='running'/.test(sql)) return { n: 0 };
    if (/COUNT\(\*\) AS n FROM games/.test(sql)) return { n: 1 };
    if (/updated_at, naposledy_selhalo, eskalovano FROM roadmap/.test(sql)) {
      return { updated_at: 'x', naposledy_selhalo: null, eskalovano: null };
    }
    if (/SELECT attempts/.test(sql)) return { attempts: 3, status: 'ready' };
    nezname.push('first: ' + normal(sql).slice(0, 90));
    return null;
  };
  const all = (sql) => {
    if (/FROM runs r JOIN tasks t/.test(sql)) return { results: [] };
    if (/GROUP BY item_id/.test(sql)) {
      return { results: [...strop.entries()].map(([item_id, runs]) => ({ item_id, runs })) };
    }
    if (/SELECT game_id, repo, roadmap_file, active FROM games/.test(sql)) {
      return { results: [{ game_id: 'uo-shadows', repo: REPO, roadmap_file: ROADMAP, active: 1 }] };
    }
    if (/FROM roadmap WHERE status <> 'done'/.test(sql)) return { results: [] };
    if (/FROM roadmap r LEFT JOIN tasks t/.test(sql)) return { results: roadmapRadky };
    if (/SELECT payload FROM tasks WHERE status='running'/.test(sql)) return { results: [] };
    if (/SELECT \* FROM tasks WHERE status='ready'/.test(sql)) {
      return {
        results: ['engine.input', 'world.bodies', 'engine.shell'].map((g, i) => ({
          id: 244 + i, title: g, kind: 'code', target: 'cloud', prompt: 'x',
          payload: JSON.stringify({ game: 'uo-shadows', grain: g, repo: REPO, owns: [`scripts/${g}.gd`], max_lines: 60, model: 'any' }),
          status: 'ready', attempts: 3,
        })),
      };
    }
    if (/SELECT k, v FROM state/.test(sql)) return { results: [] };
    if (/SELECT item_id, task_id FROM roadmap/.test(sql)) return { results: roadmapRadky };
    if (/JOIN roadmap rm ON rm.task_id = t.id/.test(sql)) return { results: [] };
    nezname.push('all: ' + normal(sql).slice(0, 90));
    return { results: [] };
  };
  const run = (sql) => {
    if (/ALTER TABLE roadmap/.test(sql)) throw new Error('D1_ERROR: duplicate column name');
    if (/CREATE TABLE IF NOT EXISTS state/.test(sql)) return { meta: { changes: 0 } };
    if (/INSERT INTO state/.test(sql)) return { meta: { changes: 1 } };
    if (/UPDATE runs SET status='timeout'/.test(sql)) return { meta: { changes: 0 } };
    if (/UPDATE tasks SET status='blocked'/.test(sql)) return { meta: { changes: 0 } };
    if (/DELETE FROM roadmap/.test(sql)) return { meta: { changes: 0 } };
    if (/^(INSERT|UPDATE) /.test(normal(sql))) return { meta: { changes: 0, last_row_id: 1 } };
    nezname.push('run: ' + normal(sql).slice(0, 90));
    return { meta: { changes: 0 } };
  };

  const mereno = (sql, f) => {
    const t = process.hrtime.bigint();
    const v = f();
    const cas = ms(process.hrtime.bigint() - t);
    log.push({ sql: normal(sql), cas });
    ucty.d1 += cas;
    ucty.roundtrips++;
    return Promise.resolve(v);
  };
  const api = (sql) => {
    const spust = () => first(sql);
    return {
      first: () => mereno(sql, () => first(sql)),
      all: () => mereno(sql, () => all(sql)),
      run: () => mereno(sql, () => run(sql)),
      bind: () => api(String(sql)),
      // `batch()` = JEDEN round-trip: do logu jde jeden záznam na příkaz.
      // ⚠ `_sql()` vrací SUROVÝ text (NE normalizovaný): router `all()`/`run()`
      // rozhoduje podle mezer a nových řádků — `FROM runs r JOIN tasks t` nesmí
      // sednout na agregaci granulí, která má `JOIN` až na dalším řádku
      // (naměřeno 12. 10. 2026: normalizace způsobila, že počítadlo granulí
      // vrátilo prázdno → dispatch smyčka se zacyklila → OOM).
      _sql: () => String(sql),
      _spust: spust,
    };
  };
  const DB = {
    prepare: (sql) => api(String(sql)),
    batch: async (stmts) => {
      // Pojistka proti ZACYCLENÍ: smyčka dispatche se musí zastavit. Kdyby
      // model světa neodpovídal, tick by se točil — a to je vada HARNESU.
      if (++ucty.batchVolani > 40) {
        throw new Error(`HARNES: batch() zavolán ${ucty.batchVolani}× — tick se zacyklil; `
          + `poslední: ${stmts.map((s) => s._sql().slice(0, 50)).join(' | ')}`);
      }
      const t = process.hrtime.bigint();
      const vysledky = stmts.map((s, i) => {
        // první/poslední příkaz se pozná podle tvaru; `all()` zvládne i `first` tvary
        const sql = s._sql();
        log.push({ sql: `[batch ${i + 1}/${stmts.length}] ` + sql.slice(0, 62), cas: 0 });
        const jeRun = /^(UPDATE|INSERT|DELETE|CREATE|ALTER)/.test(sql);
        return jeRun ? run(sql) : all(sql);
      });
      ucty.d1 += ms(process.hrtime.bigint() - t);
      ucty.roundtrips++;   // CELÝ batch = JEDEN round-trip
      log.push({ sql: `[batch CELKEM] ${stmts.length} příkazů = 1 round-trip`, cas: 0 });
      return vysledky.map((v) => ({ results: v.results, meta: v.meta ?? { changes: 0 }, success: true }));
    },
  };
  return { DB, log, nezname };
}

function stubGithub(payloady, volani) {
  // ⚠ ZÁMĚRNĚ NE `new Response(...)`: v Node je `Response` z undici a jeho
  // konstrukce dělá `toUSVString` nad 600 kB textem (naměřeno: 7,4 ms self-time
  // v profilu) — to workerd NEDĚLÁ, takže by model měřil Node, ne conductora.
  // Lehká náhrada má jen to, co conductor opravdu používá (`ok`, `status`,
  // `headers`, `text()`, `json()`); `json()` volá `JSON.parse`, který je obalený
  // měřidlem, takže cena parsování zůstává změřená.
  return async (u) => {
    const s = String(u);
    if (s.includes('api.telegram.org') || s.includes('ntfy.sh') || s.includes('discord')) {
      return { ok: true, status: 200, headers: new Headers(), text: async () => '{}', json: async () => ({}) };
    }
    const cesta = s.replace(`https://api.github.com/repos/${REPO}`, '');
    const klid = s.includes('raw.githubusercontent.com') ? ('RAW ' + ROADMAP)
      : (s.includes('/graphql') ? 'GRAPHQL' : cesta);
    const p = payloady[klid];
    volani.push({ url: s, klid, bajtu: p?.bajtu ?? 0, status: p?.status ?? 0 });
    const status = p?.status ?? 404;
    const text = p?.text ?? 'neni';
    return {
      ok: status >= 200 && status < 300,
      status,
      headers: new Headers({ 'content-type': 'application/json' }),
      text: async () => text,
      json: async () => JSON.parse(text),
    };
  };
}

// ─────────────────────────────────────────────── jeden tik (čerstvý modul) ──
async function jedenTick(payloady, cesta, i, modPredan) {
  const m = meraky();
  const volani = [];
  const svet = fakeSvet(payloady, m.ucty);
  m.obalFetch(stubGithub(payloady, volani));
  const mod = modPredan || await import(`${pathToFileURL(BUNDLE).href}?v=${i}-${Math.random()}`);
  const env = {
    DB: svet.DB, GITHUB_TOKEN: 'test', GITHUB_REPO: REPO, GITHUB_REF: 'main',
    WORKFLOW_FILE: 'agent.yml', WEBHOOK_SECRET: SECRET, ROADMAP_MAX_PRS: '5',
    MAX_CONCURRENT: '5', RETRY_HOURS: '3', MAX_ATTEMPTS: '5', ESCALATE_AFTER: '3',
    GRAIN_MAX_RUNS: '8', STALE_MINUTES: '90', ROADMAP_FILE: ROADMAP,
  };
  const t0 = process.hrtime.bigint();
  let zprava = '';
  if (cesta === 'scheduled') {
    let cekajici = null;
    mod.default.scheduled({ cron: '* * * * *' }, env, { waitUntil: (p) => { cekajici = p; } });
    await cekajici;
    zprava = '(cron — zpráva jde do logu)';
  } else {
    const res = await mod.default.fetch(new Request('https://conductor.test/tick', {
      method: 'POST', headers: { 'x-forge-secret': SECRET },
    }), env);
    const telo = await res.json();
    zprava = String(telo?.message || '');
  }
  const celkem = ms(process.hrtime.bigint() - t0);
  m.vrat();
  // `m.ucty` je týž objekt, do kterého měřidla přičítala — po tiku se z něj čte.
  const faze = { json: m.ucty.json, atob: m.ucty.atob, decode: m.ucty.decode, d1: m.ucty.d1, fetch: m.ucty.fetch };
  return { celkem, ...faze, d1_log: svet.log, d1_pocet: m.ucty.roundtrips, volani, zprava, podleJson: m.podleJson, nezname: svet.nezname };
}

// ────────────────────────────────────────────────────────────── main ───────
async function main() {
  console.log('=== p40-a — rozklad ceny tiku po fázích ===');
  build();
  const payloady = await stahni(process.argv.includes('--zive'));

  const behy = { scheduled: [], tick: [] };
  // `--teplo`: modul se importuje JEDNOU (teplý JIT) — to je model BĚŽNÉHO CPU,
  // protože kompilace skriptu se v produkci účtuje jako `startup`, ne do invokace.
  const teplo = process.argv.includes('--teplo');
  const modTeplo = teplo ? await import(`${pathToFileURL(BUNDLE).href}?v=teplo-${Math.random()}`) : null;

  // Předehřev (3 kola na cestu) — nezapočítává se; jinak by medián míchal JIT.
  for (const cesta of ['scheduled', 'tick']) {
    for (let i = 0; i < 3; i++) await jedenTick(payloady, cesta, i, modTeplo);
  }

  // `--profil <soubor>`: V8 CPU profil POUZE okolo měřených tiků (ne buildu!).
  const iP = process.argv.indexOf('--profil');
  let session = null;
  if (iP > 0) {
    const { Session } = await import('node:inspector');
    session = new Session();
    session.connect();
    const post = (m, p) => new Promise((res, rej) => session.post(m, p, (e, r) => (e ? rej(e) : res(r))));
    await post('Profiler.enable');
    await post('Profiler.setSamplingInterval', { interval: 100 });
    await post('Profiler.start');
    session._post = post;
  }

  for (const cesta of ['scheduled', 'tick']) {
    for (let i = 0; i < N; i++) {
      if (process.env.P40_DEBUG) console.log(`  [debug] ${cesta} #${i} …`);
      behy[cesta].push(await jedenTick(payloady, cesta, i, modTeplo));
      if (process.env.P40_DEBUG) console.log(`  [debug] ${cesta} #${i} hotovo, d1=${behy[cesta][behy[cesta].length - 1].d1_pocet}, volani=${behy[cesta][behy[cesta].length - 1].volani.length}`);
    }
  }

  if (session) {
    const { profile } = await session._post('Profiler.stop');
    writeFileSync(process.argv[iP + 1], JSON.stringify(profile), 'utf8');
    console.log(`[profil] ${process.argv[iP + 1]}`);
  }

  zapis(`# p40-a — ROZKLAD CENY TIKU PODLE FÁZÍ — ${new Date().toISOString()}`);
  zapis('# conductor: SKUTEČNÝ handler (`scheduled` i `POST /tick`) z bundle `wrangler deploy --dry-run`');
  zapis(`# payloady GitHubu: ${process.argv.includes('--zive') ? 'stažené ŽIVĚ TEĎ' : 'z cache'} (${REPO})`);
  zapis(`# iterací na cestu: ${N} (první se zahazuje kvůli JIT), každá v ČERSTVÉM modulu (jako čerstvý izolát)`);
  zapis('# měřeno `hrtime` (na Windows má `cpuUsage` kvantum ~16 ms — na fáze se nehodí)');
  zapis('# ⚠ Falešná D1 NENÍ D1: režie round-tripu je tady DOLNÍ ODHAD (await + Promise)');
  zapis('');

  for (const cesta of ['scheduled', 'tick']) {
    const b = behy[cesta];
    if (!b.length) continue;
    const med = (k) => median(b.map((x) => x[k]));
    const celkem = med('celkem');
    const soucet = med('json') + med('atob') + med('decode') + med('d1') + med('fetch');
    zapis(`## ${cesta === 'scheduled' ? 'CRON (scheduled)' : 'RUČNÍ POST /tick'} — medián z ${b.length} běhů`);
    zapis(`   CELKEM tik:                ${zaokr(celkem)} ms`);
    zapis(`     GitHub JSON.parse:       ${zaokr(med('json'))} ms`);
    zapis(`     base64 (atob):           ${zaokr(med('atob'))} ms`);
    zapis(`     TextDecoder.decode:      ${zaokr(med('decode'))} ms`);
    zapis(`     D1 (${b[0].d1_pocet} round-tripů):       ${zaokr(med('d1'))} ms`);
    zapis(`     fetch (obal):            ${zaokr(med('fetch'))} ms`);
    zapis(`   SOUČET FÁZÍ:               ${zaokr(soucet)} ms`);
    zapis(`   ZBYTEK (logika kódu + JIT): ${zaokr(celkem - soucet)} ms`);
    zapis('');
    // per-URL JSON.parse
    const podle = new Map();
    for (const x of b) for (const [k, v] of x.podleJson) {
      const a = podle.get(k) || { soucet: 0, n: 0 };
      a.soucet += v; a.n++;
      podle.set(k, a);
    }
    zapis('   `JSON.parse` podle odpovědi (medián na běh):');
    for (const [k, a] of [...podle.entries()].sort((x, y) => y[1].soucet - x[1].soucet)) {
      const p = payloady[k.replace(/^https:\/\/api\.github\.com\/repos\/[^/]+\/[^/]+/, '')] || payloady[k];
      zapis(`     ${zaokr(a.soucet / a.n).padStart(7)} ms  ${String(p?.bajtu ?? '').padStart(8)} B  ${k.replace(`https://api.github.com/repos/${REPO}`, '').slice(0, 60)}`);
    }
    zapis('');
    // D1 podle dotazu
    const podleSql = new Map();
    for (const x of b) for (const l of x.d1_log) {
      const a = podleSql.get(l.sql.slice(0, 74)) || { n: 0, cas: 0 };
      a.n++; a.cas += l.cas;
      podleSql.set(l.sql.slice(0, 74), a);
    }
    zapis(`   D1 podle dotazu (${b[0].d1_pocet} round-tripů, ${podleSql.size} různých):`);
    for (const [k, a] of [...podleSql.entries()].sort((x, y) => y[1].cas - x[1].cas)) {
      zapis(`     ${String(Math.round(a.n / b.length)).padStart(3)}× ${zaokr(a.cas / b.length).padStart(6)} ms | ${k}`);
    }
    if (b[0].nezname.length) zapis(`   ⚠ NEMODELOVANÉ dotazy: ${[...new Set(b[0].nezname)].join(' | ')}`);
    zapis(`   zpráva tiku: ${b[0].zprava.slice(0, 220)}`);
    zapis('');
  }

  // ── kandidáti na zlevnění (měřeno na TÝCHŽ živých datech) ────────────────
  zapis('## KANDIDÁTI NA ZLEVNĚNÍ (měřeno na živých datech, medián z 15 běhů)');
  const base64 = JSON.parse(payloady[`/contents/${ROADMAP}`].text).content;
  const rawP = payloady['RAW ' + ROADMAP];
  const prTxt = payloady['/pulls?state=closed&per_page=100&sort=updated&direction=desc'].text;
  const pr30 = JSON.stringify(JSON.parse(prTxt).slice(0, 30));
  const mer = (f) => { const a = []; for (let i = 0; i < 15; i++) { const t = process.hrtime.bigint(); f(); a.push(ms(process.hrtime.bigint() - t)); } return median(a); };
  const cDek = mer(() => {
    const bin = atob(String(base64).replace(/\n/g, ''));
    const bytes = new Uint8Array(bin.length);
    for (let j = 0; j < bin.length; j++) bytes[j] = bin.charCodeAt(j);
    JSON.parse(new TextDecoder().decode(bytes));
  });
  const cRaw = mer(() => { JSON.parse(rawP.text); });
  const cPr = mer(() => { JSON.parse(prTxt); });
  const cPr30 = mer(() => { JSON.parse(pr30); });
  zapis(`   base64 roadmapa → JSON:            ${zaokr(cDek)} ms  (${base64.length} znaků base64)`);
  zapis(`   SYROVÁ roadmapa (raw) → JSON:      ${zaokr(cRaw)} ms  (${rawP.bajtu} B) → úspora ${zaokr(cDek - cRaw)} ms`);
  zapis(`   /pulls closed 100 PR (600 kB):     ${zaokr(cPr)} ms`);
  zapis(`   /pulls closed  30 PR (~180 kB):    ${zaokr(cPr30)} ms → úspora ${zaokr(cPr - cPr30)} ms`);
  zapis('');
  const cron = behy.scheduled[0];
  zapis('## CO Z TOHO PLYNE');
  zapis(`   živý cron tik: 16–20 ms CPU (měřeno tailem, 11 eventů) · offline model: ${zaokr(median(behy.scheduled.map((x) => x.celkem)))} ms`);
  zapis(`   GitHub (3 volání, 665 441 B) = ${zaokr(median(behy.scheduled.map((x) => x.json)))} ms · D1 ${cron.d1_pocet} round-tripů · zbytek logika`);
  zapis('   → pod 10 ms vede přes ŠKRTNUTÍ ROUND-TRIPŮ a PARSOVÁNÍ, ne „zrychlením logiky“.');

  writeFileSync(OUT, radky.join('\n') + '\n', 'utf8');
  console.log(`\n[zapsano] ${OUT}`);
  process.exit(0);
}

main();


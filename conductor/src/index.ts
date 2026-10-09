// Conductor – mozek orchestra. Běží na Cloudflare Workers (free plán), takže
// funguje i když je domácí počítač vypnutý.
//
// Dvě cesty, kterými se úkol dostane ke zpracování:
//   target='cloud' → conductor spustí GitHub Actions (workflow_dispatch)
//   target='lan'   → úkol si vyzvedne pull-worker (telefon, PC) přes POST /claim
//
// Pull-workery místo self-hosted runnerů: GitHub výslovně varuje, že runner
// u VEŘEJNÉHO repa může přes fork PR spustit cizí kód na tvém zařízení.
// Pull-worker se sám ptá po HTTPS, takže se nic neotvírá do internetu.

export interface Env {
  DB: D1Database;
  GITHUB_TOKEN: string;
  GITHUB_REPO: string;        // "vlastnik/repo"
  GITHUB_REF: string;         // větev, ze které se workflow spouští (main)
  NTFY_TOPIC: string;
  NTFY_SERVER?: string;       // výchozí https://ntfy.sh
  TELEGRAM_BOT_TOKEN?: string; // doporučený kanál (ntfy.sh rate-limituje Cloudflare IP)
  TELEGRAM_CHAT_ID?: string;
  DISCORD_WEBHOOK?: string;
  WEBHOOK_SECRET: string;     // sdílené tajemství pro /task, /report, /claim, /heartbeat
  MAX_CONCURRENT?: string;    // kolik cloudových úloh smí běžet zároveň (výchozí 1)
  STALE_MINUTES?: string;     // po kolika minutách se zaseknutá úloha ukončí
  WORKFLOW_FILE?: string;     // který workflow spouštět
  ROADMAP_FILE?: string;      // odkud brát úkoly, když je fronta prázdná
  ROADMAP_MAX_PRS?: string;   // kolik otevřených PR od agenta tolerovat (výchozí 3)
  RETRY_HOURS?: string;       // po kolika hodinách smí selhaná granule znovu do fronty (výchozí 6)
  MAX_ATTEMPTS?: string;      // kolik pokusů smí ÚKOL mít, než zůstane 'failed' (výchozí 5)
  CI_WORKFLOW_FILE?: string;  // který workflow je „CI cíle“ pro /health (výchozí ci.yml)
  // Po kolika spálených pokusech se GRANULE ohlásí (Telegram). Nic se
  // nevypíná – jen notifikace (strop je druhý krok, B3b). Musí být POD
  // `MAX_ATTEMPTS`: prah nad stropem je prah, který nikdy nepřijde.
  // ⚠ Do 6. 10. 2026 tu stálo, že se `MAX_ATTEMPTS` v provozu nepoužívá —
  // NAMĚŘENO NEPRAVDA: čte se v `pollRuns` (strop úkolu), v `/report`
  // i v `attempts < ?` v dispatch dotazu. Nepoužívaný nebyl strop, ale
  // WATCHDOG (prah nad stropem a počítání po úkolech) — opraveno v B3a.
  ESCALATE_AFTER?: string;
  // Strop na GRANULI (B3b): kolik běhů smí granule spálit, než se přestane
  // vydávat. **Prázdné/`0` = strop vypnutý** — nasazuje se druhým krokem,
  // až po ověření watchdogu (viz `grainCap`).
  GRAIN_MAX_RUNS?: string;
}

const JSON_HEADERS = { "content-type": "application/json; charset=utf-8" };

function json(data: unknown, status = 200): Response {
  return new Response(JSON.stringify(data, null, 2), { status, headers: JSON_HEADERS });
}

// ---------------------------------------------------------------- util ----
function timingSafeEqual(a: string, b: string): boolean {
  const ab = new TextEncoder().encode(a);
  const bb = new TextEncoder().encode(b);
  if (ab.length !== bb.length) return false;
  let diff = 0;
  for (let i = 0; i < ab.length; i++) diff |= ab[i] ^ bb[i];
  return diff === 0;
}

async function hmacHex(secret: string, body: string): Promise<string> {
  const key = await crypto.subtle.importKey(
    "raw", new TextEncoder().encode(secret),
    { name: "HMAC", hash: "SHA-256" }, false, ["sign"],
  );
  const sig = await crypto.subtle.sign("HMAC", key, new TextEncoder().encode(body));
  return [...new Uint8Array(sig)].map((b) => b.toString(16).padStart(2, "0")).join("");
}

function secretOk(request: Request, env: Env): boolean {
  return timingSafeEqual(request.headers.get("x-forge-secret") || "", env.WEBHOOK_SECRET);
}

// Notifikační fetch s timeoutem: bez něj ntfy/Telegram umí viset a blokovat
// odpověď endpointu (naměřeno: /game vracel odpověď až po ~20 s). Když kanál
// nestihne odpovědět, abortne se a pokračuje se dál.
async function fetchTimeout(url: string, init: RequestInit, ms = 6000): Promise<Response> {
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), ms);
  try {
    return await fetch(url, { ...init, signal: ctrl.signal });
  } finally {
    clearTimeout(timer);
  }
}

async function notify(env: Env, title: string, message: string, tags = "robot"): Promise<void> {
  // Notifikace jde do VŠECH nastavených kanálů. Je to schválně: ntfy.sh vrací
  // z Cloudflare často 429 (Workery sdílejí IP adresy a ntfy podle IP limituje),
  // takže Telegram nebo Discord jsou spolehlivější a pořád zdarma.
  const jobs: Promise<void>[] = [];

  const tgToken = (env.TELEGRAM_BOT_TOKEN || "").trim();
  const tgChat = (env.TELEGRAM_CHAT_ID || "").trim();
  if (tgToken && tgChat) {
    jobs.push((async () => {
      try {
        const res = await fetchTimeout(`https://api.telegram.org/bot${tgToken}/sendMessage`, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({
            chat_id: tgChat,
            text: `${title}\n${message}`,
            disable_web_page_preview: true,
          }),
        });
        console.log(`telegram: HTTP ${res.status} (${title})`);
      } catch (e) {
        console.log("telegram selhalo:", String(e));
      }
    })());
  }

  const discord = (env.DISCORD_WEBHOOK || "").trim();
  if (discord) {
    jobs.push((async () => {
      try {
        const res = await fetchTimeout(discord, {
          method: "POST",
          headers: { "content-type": "application/json" },
          body: JSON.stringify({ content: `${title}\n${message}`.slice(0, 1900) }),
        });
        console.log(`discord: HTTP ${res.status} (${title})`);
      } catch (e) {
        console.log("discord selhalo:", String(e));
      }
    })());
  }

  const topic = (env.NTFY_TOPIC || "").trim();
  if (topic) {
    const server = (env.NTFY_SERVER || "https://ntfy.sh").replace(/\/$/, "");
    jobs.push((async () => {
      try {
        const res = await fetchTimeout(`${server}/${topic}`, {
          method: "POST",
          // ntfy vyžaduje ASCII hlavičky – titulky proto držíme bez diakritiky
          headers: { Title: title, Tags: tags, Priority: "default" },
          body: message,
        });
        console.log(`ntfy: HTTP ${res.status} na ${server}/${topic} (${title})`);
      } catch (e) {
        console.log("ntfy selhalo:", String(e));
      }
    })());
  }

  if (!jobs.length) {
    console.log("notify: není nastavený žádný kanál (ntfy/telegram/discord)");
    return;
  }
  await Promise.all(jobs);
}

// --------------------------------------------------------------- GitHub ----
/** Limit velikosti granule: ze size_lines ("<= 120") číslo, jinak výchozích 60. */
function maxLinesOf(sizeLines: string | null | undefined): number {
  const m = String(sizeLines || "").match(/\d+/);
  const n = m ? Number(m[0]) : 0;
  return n > 0 ? n : 60;
}

/** Z payloadu úkolu: modelová třída granule ("any" | "strong"). */
function modelOf(payload: string | null): string {
  try {
    const p = JSON.parse(payload || "{}");
    return typeof p.model === "string" && p.model ? p.model : "any";
  } catch { return "any"; }
}

/**
 * Z payloadu úkolu: ID granule v roadmapě (např. "core.skills").
 *
 * Workflow podle něj hledá `owns` granule a ty soubory předá aideru jako
 * `--file` (editovatelné). Bez toho je agent dostal jen přes repo-mapu
 * (read-only) a model odmítl editovat – root cause 0% úspěšnosti.
 */
function grainOf(payload: string | null): string {
  try {
    const p = JSON.parse(payload || "{}");
    return typeof p.grain === "string" ? p.grain : "";
  } catch { return ""; }
}

async function dispatchWorkflow(env: Env, task: Task, runKey: string, attempt: number): Promise<void> {
  const workflow = env.WORKFLOW_FILE || "agent.yml";
  const repo = repoOf(task.payload, env);
  // max_lines a model se berou z granule roadmapy (payload) – brána auto-merge
  // v workflow pak posuzuje velikost podle deklarace granule, ne globálně.
  const maxLines = (() => {
    try {
      const p = JSON.parse(task.payload || "{}");
      const n = Number(p.max_lines);
      return Number.isFinite(n) && n > 0 ? n : 60;
    } catch { return 60; }
  })();
  const url = `https://api.github.com/repos/${repo}/actions/workflows/${workflow}/dispatches`;
  const res = await fetch(url, {
    method: "POST",
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "forge-conductor",
      "content-type": "application/json",
    },
    body: JSON.stringify({
      ref: env.GITHUB_REF || "main",
      inputs: {
        task_id: String(task.id),
        run_key: runKey,
        kind: task.kind,
        title: task.title,
        prompt: task.prompt,
        max_lines: String(maxLines),
        model: modelOf(task.payload),
        // ID granule v roadmapě (payload ho nese jako `grain`). Workflow podle
        // něj najde `owns` a předá ty soubory aideru jako `--file`, tedy
        // EDITOVATELNÉ. Bez toho měl agent soubory jen v repo-mapě (read-only)
        // a model správně odmítl editovat – což byl root cause 0% úspěšnosti
        // (naměřeno 30. 9. 2026: mistral i cerebras odpovídaly „please add the
        // file to the chat", granule upravující existující soubor selhaly vždy).
        grain: grainOf(task.payload),
        // Číslo pokusu: workflow podle něj posune pořadí modelů, aby opakovaný
        // pokus nezkoušel stejný model jako ten, co právě selhal. Naměřeno
        // 30. 9. 2026: task #128 i #131 zkoušely 5× po sobě mistral/codestral
        // a selhaly pokaždé stejně – rotace se u granulí `any` nepoužívala.
        attempt: String(attempt),
      },
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub dispatch ${res.status}: ${text.slice(0, 300)}`);
  }
}

/**
 * Watchdog na GRANULI (B3a, 6. 10. 2026) — ohlásí granuli, která spálila příliš
 * mnoho pokusů, a počítá je PŘES VŠECHNY JEJÍ ÚKOLY.
 *
 * PROČ SE TO PŘEPISOVALO (naměřeno na ŽIVÉ službě 6. 10. 2026):
 * `MAX_ATTEMPTS` platí na ÚKOL, ale smyčka je na GRANULI — každý retry zakládá
 * nový úkol s `attempts=0`. `entity.npc` proto spálil **8 pokusů** (5 v #228
 * + 3 v #234), `entity.enemy` **5**, a conductor je vydával dál. Starý watchdog
 * počítal běhy JEDNOHO úkolu (`r.task_id = t.id`) a měl prah 8 > strop 5, takže
 * se **nikdy nemohl spustit** — ověřeno: v `payload` žádné úlohy není
 * `eskalovano`. Značka navíc žila v payloadu úkolu, který retry zahodí, takže
 * kdyby se spustil, spammoval by při každém novém úkolu.
 *
 * CO SE ZMĚNILO:
 *   · počítá se `COUNT(runs)` na klíči `{game}/{grain}` napříč úkoly
 *     (`SQL_GRANULE_RUNS`); klíč se skládá na JEDNOM místě (`GRAIN_KEY_SQL`) —
 *     dva tvary téhož klíče je vada, kterou žádný test nevidí (invariant 17),
 *   · prah je `ESCALATE_AFTER` (výchozí **3**, tedy POD stropem `MAX_ATTEMPTS=5`,
 *     protože prah nad stropem je prah, který nikdy nepřijde),
 *   · značka „už ohlášeno“ je v `roadmap.eskalovano`, takže přežije retry;
 *     `roadmap-reset` ji smaže — to je cesta, jak granuli po stropu vrátit.
 *
 * ZÁMĚRNĚ SE NIC NEVYPÍNÁ: jen se to řekne. Strop (B3b) je druhý krok.
 *
 * @returns text pro tik — vždy se říká, CO se měřilo (i „NEZMĚŘENO“)
 */
const GRAIN_KEY_SQL =
  `(json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain'))`;

const SQL_GRANULE_RUNS = `
  SELECT ${GRAIN_KEY_SQL} AS item_id, COUNT(r.id) AS runs
    FROM runs r
    JOIN tasks t ON t.id = r.task_id
    JOIN roadmap rm ON rm.item_id = ${GRAIN_KEY_SQL}
   WHERE r.started_at IS NOT NULL
     AND r.started_at >= rm.created_at
   GROUP BY item_id`;

/** Spálené běhy na granuli od založení jejího řádku. `null` = NEZMĚŘENO. */
async function grainRuns(env: Env): Promise<Map<string, number> | null> {
  try {
    const rows = await env.DB.prepare(SQL_GRANULE_RUNS)
      .all<{ item_id: string; runs: number }>();
    const m = new Map<string, number>();
    for (const r of rows.results || []) m.set(String(r.item_id), Number(r.runs) || 0);
    return m;
  } catch (e) {
    // „nezměřeno“ se NESMÍ číst jako nula (pravidlo projektu): vrací se `null`
    // a tik to vypíše. Watchdog pak mlčí — radši nehlásit než hlásit nesmysl.
    console.log(`pocitadlo granulí nejde nacist: ${String(e).slice(0, 160)}`);
    return null;
  }
}

/**
 * Rozhodnutí watchdogu: má se granule ohlásit?
 *
 * Je to SAMOSTATNÁ čistá funkce schválně — test (`tools/test-watchdog-granule.py`)
 * ji vytáhne ze zdrojáku a ZAVOLÁ, místo aby si rozhodnutí opsal. „Test, který
 * opisuje logiku" je v tomhle projektu pojmenovaná vada (starý `test-eskalace.py`).
 * `undefined` (granule bez řádku v roadmapě) NENÍ nula, která se hlásí.
 */
function shouldEscalate(runs: number | undefined, threshold: number): boolean {
  return (runs ?? 0) >= threshold;
}

/**
 * Strop na GRANULI (B3b, 6. 10. 2026): kolik běhů smí granule spálit, než se
 * přestane vydávat.
 *
 * **Výchozí `0` = strop VYPNUTÝ** (když proměnná chybí), ale `wrangler.toml` ho
 * od **8. 10. 2026** nasazuje **ZAPNUTÝ na `"8"`**: plán žádal nasazovat po
 * částech — první deploy přinesl **watchdog** (B3a, jen hlásí), teprve další
 * krok strop **zastaví** vydávání. **Proč 8:** musí být VÍC než `MAX_ATTEMPTS`
 * (5), jinak jen opisuje pokusový strop; a `ESCALATE_AFTER` (3) zůstává pod ním,
 * aby watchdog ohlásil dřív, než se granule zastaví.
 *
 * Nesmysl v konfiguraci (`""`, `"abc"`, záporné číslo) se bere jako **vypnuto** —
 * „strop, který se nedá přečíst“ nesmí tiše zastavit celou orchestra.
 */
function grainCap(env: Env): number {
  const n = Number(env.GRAIN_MAX_RUNS || "0");
  return Number.isFinite(n) && n > 0 ? n : 0;
}

/** Rozhodnutí o stropu — čistá funkce, aby ji test VOLAL, neopisoval. */
function grainCapped(runs: number | undefined, cap: number): boolean {
  return cap > 0 && (runs ?? 0) >= cap;
}

/**
 * Klíč granule z payloadu úkolu — `{game}/{grain}`.
 *
 * ⚠ MUSÍ SEDĚT s `GRAIN_KEY_SQL` (SQL si klíč skládá sám). Dva tvary téhož klíče
 * je vada, kterou žádný test nevidí (invariant 17) — proto na shodu existuje
 * kontrola v `tools/test-grain-cap.py`.
 */
function grainKeyOf(payload: string | null): string | null {
  try {
    const p = JSON.parse(payload || "{}");
    if (typeof p?.game === "string" && typeof p?.grain === "string" && p.game && p.grain) {
      return `${p.game}/${p.grain}`;
    }
  } catch { /* */ }
  return null;
}

async function escalateStuckTasks(env: Env, runs: Map<string, number> | null): Promise<string> {
  const prah = Number(env.ESCALATE_AFTER || "3");
  if (runs === null) return "NEZMĚŘENO (počítadlo granulí nejde načíst)";
  let notified = 0;
  try {
    const rows = await env.DB.prepare(
      `SELECT item_id, task_id, status FROM roadmap
        WHERE status <> 'done' AND (eskalovano IS NULL OR eskalovano = '')
        ORDER BY item_id LIMIT 200`,
    ).all<{ item_id: string; task_id: number | null; status: string }>();

    for (const r of rows.results || []) {
      const spalenych = runs.get(r.item_id);
      if (!shouldEscalate(spalenych, prah)) continue;
      await notify(
        env,
        "Forge: granule se nedari",
        `${r.item_id} (stav ${r.status})\n`
        + `spáleno ${spalenych} pokusů na TÉHLE granulí (prah ${prah})\n`
        + `počítá se přes všechny její úkoly — retry zakládá nový úkol\n`
        + `běh pokračuje dál – nic se nevypíná, jen na vědomí`,
        "warning",
      );
      await env.DB.prepare("UPDATE roadmap SET eskalovano = datetime('now') WHERE item_id = ?")
        .bind(r.item_id).run().catch(() => undefined);
      notified++;
    }
  } catch (e) {
    console.log("eskalace selhala:", String(e).slice(0, 160));
  }
  return `${notified} ohlášeno (prah ${prah})`;
}

// ------------------------------------------------------- polling běhů ----
// PROČ POLLING A NE REPORT Z WORKFLOWU:
//   1) nejsou potřeba další tajemství v repu (GitHub → conductor),
//   2) conductor uvidí i běh, který spadne dřív, než by stihl poslat report,
//   3) conductor tak pozná výsledek i z pull requestu, který agent otevřel.
// Workflow proto má v `run-name` své run_key a conductor ho podle toho najde.
function repoOf(payload: string | null, env: Env): string {
  // Repo se u úkolu drží v payload JSON. Bez něj se bere defaultní GITHUB_REPO
  // (zpětná kompatibilita s dobou, kdy orchestr obsluhoval jediné repo).
  try {
    const p = JSON.parse(payload || "{}");
    if (typeof p.repo === "string" && p.repo) return p.repo;
  } catch { /* */ }
  return env.GITHUB_REPO;
}

function lockKeys(payload: string | null, env: Env): string[] {
  // Zámky souborů scoped na repo: dvě hry se stejným jménem souboru (obě mají
  // scripts/game.gd) se NESMÍ blokovat navzájem – proto klíč "{repo}/{soubor}".
  try {
    const p = JSON.parse(payload || "{}");
    const repo = typeof p.repo === "string" && p.repo ? p.repo : env.GITHUB_REPO;
    return (p.owns || []).map((f: string) => `${repo}/${f}`);
  } catch { return []; }
}

async function github(env: Env, repo: string, path: string): Promise<any> {
  const res = await fetch(`https://api.github.com/repos/${repo}${path}`, {
    headers: {
      Authorization: `Bearer ${env.GITHUB_TOKEN}`,
      Accept: "application/vnd.github+json",
      "X-GitHub-Api-Version": "2022-11-28",
      "User-Agent": "forge-conductor",
    },
  });
  if (!res.ok) {
    throw new Error(`GitHub ${path} → ${res.status}: ${(await res.text()).slice(0, 200)}`);
  }
  return res.json();
}

// ------------------------------------------------- stav CÍLE v /health (N0.3) ----
// PROČ: naměřeno 1. 10. 2026 (S18) — conductor hlásil `ok: true`, `/failed`
// prázdné, a přesto **7,5 h nevydal ani granuli**, protože `main` cílové hry
// měl červené CI. Naměřeno ZNOVU 6. 10. 2026 (tatáž třída, jiná příčina):
// od 5. 10. 22:02 selhalo **9 běhů v řadě** a `/health` pořád hlásilo `ok`.
//
// `ok` zůstává „služba žije“ (hlídá ho monitoring dostupnosti) — stav cíle se
// proto hlásí ZVLÁŠŤ v `targets`, aby se „dostupnost“ a „cíl maká“ nedaly
// splést. To je celý smysl N0.3: zelený conductor nad mrtvým cílem musí být
// vidět na jednom místě.
//
// Cache je nutná: `/health` může volat kdokoli a často; bez TTL by to byl
// GitHub API provoz na každý dotaz. Chyba se needspiruje na plnou dobu.
const targetCache = new Map<string, { data: Record<string, unknown>; expiruje: number }>();
const TARGET_TTL_MS = 2 * 60 * 1000;        // naměřeno → platí 2 minuty
const TARGET_TTL_CHYBA_MS = 30 * 1000;      // nezměřeno → zkusit dřív

async function targetState(env: Env, g: Game): Promise<Record<string, unknown>> {
  const ted = Date.now();
  const vCache = targetCache.get(g.repo);
  if (vCache && vCache.expiruje > ted) return vCache.data;

  const ref = env.GITHUB_REF || "main";
  const ven: Record<string, unknown> = {
    game_id: g.game_id,
    repo: g.repo,
    branch: ref,
    main_ci: null,
    forge: null,
    measured_at: new Date().toISOString(),
    // „nezměřeno“ NENÍ „v pořádku“ (pravidlo projektu: nula a nezměřeno musí
    // být vidět). Když GitHub neodpoví, zůstane tady důvod a `null` výš.
    error: null,
  };
  try {
    const [ci, agent] = await Promise.all([
      github(env, g.repo,
        `/actions/workflows/${env.CI_WORKFLOW_FILE || "ci.yml"}/runs?branch=${ref}&per_page=1`),
      github(env, g.repo,
        `/actions/workflows/${env.WORKFLOW_FILE || "agent.yml"}/runs?branch=${ref}&per_page=20`),
    ]);

    const beh = (ci?.workflow_runs || [])[0];
    if (beh) {
      ven.main_ci = {
        workflow: env.CI_WORKFLOW_FILE || "ci.yml",
        status: beh.status,
        conclusion: beh.conclusion,
        created_at: beh.created_at,
        head_sha: beh.head_sha,
        run_number: beh.run_number,
        url: beh.html_url,
      };
    }

    const hotove = (agent?.workflow_runs || []).filter((r: any) => r?.status === "completed");
    let vRade = 0;
    for (const r of hotove) {
      if (r.conclusion === "success") break;
      vRade++;
    }
    ven.forge = {
      // `ok` je tvrzení o POSLEDNÍM běhu, ne o náladě: když běhy nejsou, je null.
      ok: hotove.length ? hotove[0].conclusion === "success" : null,
      selhani_v_rade: vRade,
      posledni: hotove.slice(0, 5).map((r: any) => ({
        run_number: r.run_number, conclusion: r.conclusion,
        created_at: r.created_at, url: r.html_url,
      })),
    };
  } catch (e) {
    ven.error = String(e).slice(0, 200);
    targetCache.set(g.repo, { data: ven, expiruje: ted + TARGET_TTL_CHYBA_MS });
    console.log(`stav cile ${g.repo} nejde zjistit: ${ven.error}`);
    return ven;
  }
  targetCache.set(g.repo, { data: ven, expiruje: ted + TARGET_TTL_MS });
  return ven;
}

async function pollRuns(env: Env): Promise<string> {
  const maxAttempts = Number(env.MAX_ATTEMPTS || "5");
  const rows = await env.DB.prepare(
    `SELECT r.id AS run_id, r.run_key, r.task_id, t.title, t.payload
       FROM runs r JOIN tasks t ON t.id = r.task_id
      WHERE r.status = 'running' AND r.worker IS NULL
      ORDER BY r.id LIMIT 25`,
  ).all<{ run_id: number; run_key: string; task_id: number; title: string; payload: string | null }>();
  if (!rows.results?.length) return "zadny cloudovy beh nebezi";

  // GitHub API se volá jednou na repo, ne na každý běh.
  const cache = new Map<string, any[]>();
  async function runsOf(repo: string): Promise<any[]> {
    if (cache.has(repo)) return cache.get(repo)!;
    try {
      const data = await github(env, repo, "/actions/runs?event=workflow_dispatch&per_page=50");
      cache.set(repo, data.workflow_runs || []);
    } catch (e) {
      console.log(`GitHub ${repo} se neozval: ${String(e).slice(0, 120)}`);
      cache.set(repo, []);
    }
    return cache.get(repo)!;
  }

  let updated = 0;
  for (const row of rows.results) {
    const repo = repoOf(row.payload, env);
    const owner = repo.split("/")[0];
    const runs = await runsOf(repo);

    // Běh hledáme podle run_key, který workflow dostane a vloží do svého jména
    // (`run-name`). Kontrolujeme obě pole: `name` i `display_title`. Dokud běh
    // stojí ve frontě, GitHub ještě jméno nemusí mít vyplněné – když sledujeme
    // jen jedno pole, výsledek se pak „ztratí" a úkol zbytečně vyprší.
    const run = runs.find((r) => String(r.name || "").includes(row.run_key)
                              || String(r.display_title || "").includes(row.run_key));
    if (!run || run.status !== "completed") continue;

    const ok = run.conclusion === "success";
    let prUrl: string | null = null;
    let merged = false;
    if (ok) {
      try {
        const prs = await github(env, repo, `/pulls?head=${owner}:forge/task-${row.task_id}&state=all`);
        prUrl = prs?.[0]?.html_url ?? null;
        // `run.status === completed` znamená, že doběhl CELÝ workflow – tedy
        // i krok automatického sloučení. Proto je stav `merged_at` v tuhle
        // chvíli KONEČNÝ (nezmění se až po přečtení) – to je jediné, co z toho
        // plyne. NEPLYNE z toho, že se PR opravdu sloučilo: krok auto-merge
        // může skončit jen komentářem.
        //
        // POZOR (opraveno 2. 10. 2026, A1): `conclusion === "success"` NENÍ totéž
        // co „sloučeno". Workflow posílá `success` hned po VZNIKU PR (krok
        // „Vytvoř pull request"), zatímco auto-merge je samostatný krok za ním –
        // a když pravidla neprojdou, jen založí komentář. Naměřeno 2. 10. 2026:
        // `persist.save` (#139), `ui.hud` (#140), `sim.mining` (#136) byly
        // v D1 `done`, ale všechny tři PR měly `merged_at: null` a ani jeden
        // soubor (`save.gd`, `hud.gd`, `mining.gd`) nebyl v `origin/main`.
        // Proto o `done` rozhoduje `ok && merged`, ne `ok` samo.
        merged = Boolean(prs?.[0]?.merged_at);
      } catch { /* PR nemusí existovat, to není chyba běhu */ }
    }

    await env.DB.prepare(
      `UPDATE runs SET status=?, finished_at=datetime('now'), summary=?, pr_url=?
        WHERE id=?`,
    ).bind(ok ? "success" : String(run.conclusion || "failed"),
           `GitHub Actions: ${run.conclusion}`, prUrl, row.run_id).run();

    // A1: `done` se zapíše JEN když běh uspěl A PR je sloučený. Když PR
    // vzniklo, ale nesloučilo se (gate ho poslal k ruční kontrole), úkol
    // zůstane `awaiting_human` – práce není v `main`, takže „hotovo" by bylo
    // tvrzení bez protějšku (S29/S31/S33).
    if (ok && merged) {
      await env.DB.prepare("UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?")
        .bind(row.task_id).run();
      await env.DB.prepare(
        "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE task_id=?",
      ).bind(row.task_id).run().catch(() => undefined);
    } else if (ok) {
      // Běh uspěl, ale PR není sloučený: čeká se na člověka. NENÍ to selhání
      // (agent svou práci udělal), takže se NEPOČÍTÁ pokus a nezvyšuje se
      // `attempts` – jinak by granule po `maxAttempts` zbytečně přešla do
      // `failed` za to, že si ji nikdo nepřečetl.
      // `awaiting_human` žije JEN v D1 (`tasks.status`); do `roadmap.json` se
      // nepropisuje – soubor je autorita plánu, ne stavu běhu (analýza §⑨).
      await env.DB.prepare("UPDATE tasks SET status='awaiting_human', updated_at=datetime('now') WHERE id=?")
        .bind(row.task_id).run();
      await env.DB.prepare(
        "UPDATE roadmap SET status='awaiting_human', updated_at=datetime('now') WHERE task_id=?",
      ).bind(row.task_id).run().catch(() => undefined);
    } else {
      const t = await env.DB.prepare("SELECT attempts FROM tasks WHERE id=?")
        .bind(row.task_id).first<{ attempts: number }>();
      const nextStatus = (t?.attempts ?? 0) >= maxAttempts ? "failed" : "ready";
      await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
        .bind(nextStatus, row.task_id).run();
      // ROADMAP SE MUSÍ AKTUALIZOVAT PŘI KAŽDÉM SELHÁNÍ, ne jen u posledního
      // pokusu (opraveno 30. 9. 2026). Dřív se `roadmap.updated_at` zapsal jen
      // když úkol přešel do `failed`; u běžného selhání zůstal starý, takže
      // dispatch smyčka (která cooldown čte z roadmapy) považovala granuli za
      // odpočatou a vydala ji znovu za 2 minuty místo za RETRY_HOURS.
      // Naměřeno: běhy #128–#130 se opakovaly každé ~2 minuty.
      // B1: tohle je SELHÁNÍ — proto se plní `naposledy_selhalo` (z něj čte
      // cooldown). `updated_at` se plní dál, ale cooldown ho už nečte.
      await env.DB.prepare(
        `UPDATE roadmap SET status = ?, updated_at = datetime('now'),
           naposledy_selhalo = datetime('now') WHERE task_id = ?`,
      ).bind(nextStatus === "failed" ? "failed" : "queued", row.task_id).run().catch(() => undefined);
    }

    const prNote = prUrl
      ? (merged ? "\n(sloučeno automaticky)" : "\n(čeká na tvé sloučení – nesplnilo pravidla)")
      : "";
    // A1: nadpis notifikace musí odpovídat SKUTEČNÉMU stavu. Dřív se posílalo
    // „Forge: hotovo" i u PR, které se nesloučilo – a to je totéž tvrzení bez
    // protějšku, jen v jiné vrstvě (S33/S35).
    const titulek = ok && merged ? "Forge: hotovo"
      : ok ? "Forge: čeká na tvé sloučení"
      : "Forge: selhalo";
    await notify(env, titulek,
      `#${row.task_id} ${row.title}\n${run.conclusion}${prUrl ? `\n${prUrl}` : ""}${prNote}`,
      ok && merged ? "white_check_mark" : ok ? "hourglass_flowing_sand" : "warning");
    updated++;
  }
  return updated ? `aktualizovano behu: ${updated}` : "zadna zmena";
}

// -------------------------------------------------- roadmapa (vlastní práce) ----
// Když nemá orchestr nic od uživatele, vezme si další položku z roadmapy
// (.forge/roadmap.json v repu). Díky tomu pracuje na hře i bez zadání – ale
// jen po jedné položce a jen dokud uživatel nezkontroluje otevřené PR.
// Každá položka se udělá právě jednou (drží se to v tabulce roadmap).
interface RoadmapItem {
  id: string;
  title: string;
  prompt: string;
  kind?: string;
  depends_on?: string[];  // id granulí, které musejí být sloučené dřív (v rámci hry)
  owns?: string[];        // soubory, které granule smí měnit (zámek souběhu)
  size_lines?: string;    // deklarace velikosti granule, např. "<= 120"; bez ní 60
  model?: string;         // "strong" = vydat jen silnému modelu; jinak any
  done?: boolean;         // explicitní „už hotovo" – granule se přeskočí
}

interface Game {
  game_id: string;
  repo: string;
  roadmap_file: string;
  active: number;
}

// A2: soubor je autorita plánu, ale `done: true` v něm je TVRZENÍ, které nikdo
// neporovnává s realitou (S36). Než se z něj zapíše `done` do D1, ověří se, že
// aspoň jeden soubor z `owns` opravdu existuje v `origin/main` hry.
//
// Cache je nutná: `roadmapTick` běží každou minutu (`* * * * *`, wrangler.toml).
// Bez cache by to bylo až 18 granul × 1–3 soubory × 1440 tiků denně – na free
// plánu reálné riziko.
//
// POZOR NA STÁŘÍ CACHE (a je to táž past, jakou popisuje N1 v
// `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md`): modulová proměnná žije tak dlouho
// jako izolát, ne jako tik — a Cloudflare izolát recykluje, ale **nezaručuje
// kdy**. Cache bez expirace by tedy mohla sloužit strom `origin/main` libovolně
// dlouho po sloučení PR. Proto má **TTL** a nikdy se nepoužije napořád.
const originMainCache = new Map<string, { strom: Set<string> | null; expiruje: number }>();
const ORIGIN_MAIN_TTL_MS = 10 * 60 * 1000; // TTL // 10 minut

async function filesInOriginMain(env: Env, repo: string): Promise<Set<string> | null> {
  const ted = Date.now();
  const vCache = originMainCache.get(repo);
  if (vCache && vCache.expiruje > ted) return vCache.strom;
  let strom: Set<string> | null = null;
  try {
    // Celý strom naráz (1 volání), ne dotaz na každý soubor zvlášť.
    const data = await github(env, repo, "/git/trees/origin%2Fmain?recursive=1");
    if (Array.isArray(data?.tree)) {
      strom = new Set<string>(data.tree.filter((e: any) => e?.type === "blob").map((e: any) => String(e.path)));
    }
  } catch (e) {
    // Když se strom nepodaří načíst, je `null` = NEVÍME. Nesmí se to zaměnit
    // s prázdným setem („v mainu není nic“) – to by zastavilo celou roadmapu.
    // Neúspěch se needspiruje na plnou dobu – zkusí se dřív.
    console.log(`origin/main ${repo} nejde přečíst: ${String(e).slice(0, 120)}`);
    originMainCache.set(repo, { strom: null, expiruje: ted + 60 * 1000 });
    return null;
  }
  originMainCache.set(repo, { strom, expiruje: ted + ORIGIN_MAIN_TTL_MS });
  return strom;
}

async function listGames(env: Env): Promise<Game[]> {
  const rows = await env.DB.prepare(
    "SELECT game_id, repo, roadmap_file, active FROM games WHERE active = 1 ORDER BY game_id",
  ).all<Game>();
  if (rows.results?.length) return rows.results;

  // B4 (6. 10. 2026): ŽÁDNÝ FALLBACK NA `env.GITHUB_REPO`.
  //
  // Dřív tu stálo „zpětná kompatibilita: žádná registrovaná hra = jeden defaultní
  // repo“ — a to znamenalo, že **vypnutí poslední hry orchestra nezastaví**
  // (invariant 18): registr nemá aktivní hru, `listGames` vrátí `GITHUB_REPO`
  // a dispatch jede dál na hře, kterou uživatel právě vypnul.
  // Naměřeno 6. 10. 2026 bránou `tools/test-listgames.py` (PŘED opravou
  // `7 kontrol, 3 CHYB`): vypnutá hra → `[{game_id: "default", repo: <GITHUB_REPO>}]`.
  //
  // Nově: žádná aktivní hra = **žádná práce** (plán to označuje jako zamýšlené —
  // „radši nemakat“). Kdo chce orchestra rozjet, zaregistruje hru přes
  // `POST /game`; to je dokumentovaný postup od F0. Ticho by ale bylo past,
  // proto se to hlásí do logu (a tik to řekne ve své odpovědi).
  console.log("registr her: žádná AKTIVNÍ hra – conductor nedělá nic (B4)");
  return [];
}

async function roadmapTick(
  env: Env,
  retryH: number,
  runs: Map<string, number> | null,
  cap: number,
): Promise<string> {
  const games = await listGames(env);

  // Samomigrace schématu (idempotentní): roadmap.updated_at přibyl kvůli
  // cooldownu retry. Stará D1 sloupec nemá; CREATE TABLE IF NOT EXISTS v
  // schema.sql ho tam nepřidá, proto se to dělá tady – když už existuje,
  // ALTER selže s „duplicate column name" a to se tiše polkne.
  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN updated_at TEXT")
    .run().catch((e) => console.log("roadmap.updated_at: " + String(e).slice(0, 100)));
  await env.DB.prepare("UPDATE roadmap SET updated_at = created_at WHERE updated_at IS NULL")
    .run().catch(() => undefined);
  // B1 (2. 10. 2026): cooldown se ptá na `naposledy_selhalo`, ne na `updated_at`.
  // Sloupec se přidává stejnou idempotentní cestou; `NULL` znamená „ještě
  // neselhala", takže čerstvá granule NENÍ v cooldownu (vada S12).
  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN naposledy_selhalo TEXT")
    .run().catch((e) => console.log("roadmap.naposledy_selhalo: " + String(e).slice(0, 100)));
  // B3a (6. 10. 2026): značka „watchdog už tuhle granuli ohlásil“. Patří na
  // ŘÁDEK GRANULE, ne do payloadu úkolu — retry zakládá nový úkol, takže by se
  // značka ztratila a notifikace by chodila při každém tiku.
  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN eskalovano TEXT")
    .run().catch((e) => console.log("roadmap.eskalovano: " + String(e).slice(0, 100)));

  // Stav granulí drží tabulka roadmap (item_id = {game_id}/{grain_id}).
  // Řádek sám o sobě nestačí – je vidět i stav úlohy (LEFT JOIN tasks).
  interface GrainRow {
    item_id: string;
    task_id: number | null;
    rstatus: string | null;
    rupd: string | null;
    rfail: string | null;
    tstatus: string | null;
    tupd: string | null;
  }
  const rows = await env.DB.prepare(
    `SELECT r.item_id, r.task_id, r.status AS rstatus, r.updated_at AS rupd,
            r.naposledy_selhalo AS rfail,
            t.status AS tstatus, t.updated_at AS tupd
       FROM roadmap r LEFT JOIN tasks t ON t.id = r.task_id`,
  ).all<GrainRow>();

  // Sloučené PR agentů: granule, jejíž úkol má sloučené PR, je hotová, i kdyby
  // úkol sám skončil jinak (typicky „agent nic nezměnil", protože práci stihl
  // sloučit paralelní pokus – přesně to se stalo u world.level 29. 9.).
  // Větve PR se jmenují forge/task-{id}; navíc se páruje i NÁZEV PR s názvem
  // granule (titulky jsou v rámci hry jedinečné), protože starší úkoly mohly
  // vzniknout pod jiným item_id (přechod default → registrovaná hra).
  const mergedTasks = new Set<number>();
  const mergedTitlesByRepo = new Map<string, Set<string>>();
  for (const g of games) {
    const titles = new Set<string>();
    try {
      const closed = await github(env, g.repo,
        "/pulls?state=closed&per_page=100&sort=updated&direction=desc");
      for (const pr of closed || []) {
        const m = String(pr.head?.ref || "").match(/^forge\/task-(\d+)$/);
        if (pr.merged_at) {
          if (m) mergedTasks.add(Number(m[1]));
          const t = String(pr.title || "").replace(/^Forge #\d+:\s*/, "");
          if (t) titles.add(t);
        }
      }
    } catch { /* stav PR se nepodařilo zjistit – pokračuje se bez něj */ }
    mergedTitlesByRepo.set(g.repo, titles);
  }
  if (mergedTasks.size) {
    const ph = [...mergedTasks].map(() => "?").join(",");
    await env.DB.prepare(
      `UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id IN (${ph})`,
    ).bind(...[...mergedTasks]).run().catch(() => undefined);
    await env.DB.prepare(
      `UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE task_id IN (${ph})`,
    ).bind(...[...mergedTasks]).run().catch(() => undefined);
  }

  // Hotové / zablokované granule podle stavu úloh.
  // SELHANÁ granule smí znovu do fronty až po cooldownu (RETRY_HOURS): free
  // modely mají denní limity a okamžitý retry by jen pálil pokusy
  // (naměřeno 29. 9. – 429 ze všech providerů naráz).
  const done = new Set<string>();
  const blocked = new Set<string>();
  for (const r of rows.results || []) {
    const failed = r.tstatus === "failed" || r.rstatus === "failed";
    const finished = r.tstatus === "done" || r.rstatus === "done"
      || (r.task_id != null && mergedTasks.has(r.task_id));
    if (finished) { done.add(r.item_id); continue; }
    if (!failed) { blocked.add(r.item_id); continue; }
    // B1 (2. 10. 2026): rozhoduje `naposledy_selhalo`, NE `updated_at`.
    // `updated_at` je i čas VZNIKU řádku, takže nová granule vypadala jako
    // „právě selhala" a RETRY_HOURS se na ni vztáhl, i když nikdy neselhala
    // (vada S12, naměřeno `tools/test-cooldown.py`). `tupd` zůstává jako
    // záložní cesta pro řádky, u kterých sloupec ještě není vyplněný.
    const ts = r.rfail || r.tupd || null;
    const stale = !ts
      || (Date.now() - Date.parse(String(ts).replace(" ", "T") + "Z") > retryH * 3600e3);
    if (!stale) blocked.add(r.item_id);
  }

  // Nezahrnout uživatele hromadou pull requestů (limit se hlídá přes všechny hry).
  const maxPrs = Number(env.ROADMAP_MAX_PRS || "3");
  try {
    let open = 0;
    for (const g of games) {
      try {
        const prs = await github(env, g.repo, "/pulls?state=open&per_page=30");
        if (Array.isArray(prs)) open += prs.length;
      } catch { /* */ }
    }
    if (open >= maxPrs) return `čeká se na kontrolu ${open} otevřených PR (limit ${maxPrs})`;
  } catch {
    /* když se stav PR nepodaří zjistit, radši pokračujeme */
  }

  // Soubory uzamčené běžícími úlohami — dvě granule se nesmí dotýkat stejného souboru.
  const runningRows = await env.DB.prepare(
    "SELECT payload FROM tasks WHERE status='running' AND target='cloud'",
  ).all<{ payload: string | null }>();
  const locked = new Set<string>();
  for (const r of runningRows.results || []) {
    for (const k of lockKeys(r.payload, env)) locked.add(k);
  }

  let created = 0;
  const createdKeys: string[] = [];
  // P29/B6: kolik osiřelých řádků se uklidilo (viz blok níž) — tik to hlásí.
  let smazanoOsirelych = 0;

  for (const g of games) {
    let items: RoadmapItem[] = [];
    try {
      const data = await github(env, g.repo, `/contents/${g.roadmap_file}`);
      // Obsah chodí v base64; přes bajty se správně dekóduje i čeština.
      const bytes = Uint8Array.from(
        atob(String(data.content || "").replace(/\n/g, "")),
        (c) => c.charCodeAt(0),
      );
      // DAG se čte z `grains`; zpětná kompatibilita: starý formát měl `tasks`.
      const parsed = JSON.parse(new TextDecoder().decode(bytes));
      items = (parsed.grains || parsed.tasks || []) as RoadmapItem[];
    } catch (e) {
      console.log(`roadmapa ${g.game_id} nejde přečíst: ${String(e).slice(0, 120)}`);
      continue; // hra bez čitelné roadmapy se přeskakuje, ostatní jedou dál
    }
    if (!items.length) continue;

    // ── P29/B6: OSIŘELÉ ŘÁDKY CACHE SE UKLÍZEJÍ SAMY ──────────────────────
    // `roadmap` je jen CACHE toho, co conductor vydal. Když soubor granulí
    // změní (architekt přepíše roadmapu), staré řádky v cache zůstanou — a jejich
    // úlohy pak vypadají jako legitimní práce, i když je granule v souboru dávno
    // není. Naměřeno 9. 10. 2026 (`POST /tasks/cleanup?dry_run`): 21 granulí
    // v souborech, 25 řádků v cache, **5 osiřelých** — z toho `entity.enemy`
    // s úlohou **#239 `ready`**. Ruční úklid (`/tasks/cleanup`) to uměl, ale
    // NIKDO HO NEVOLAL, takže se stav jen ručně opravoval a vracel.
    // Tady se uklidí sám — v tiku, který roadmapu stejně čte.
    // ⚠ Úloha se tady NEBLOKUJE: udělá to invariant „úkol bez řádku v roadmapě“
    // níž v témže tiku. Jedno místo, ne dvě.
    const platneKlice = new Set(items.map((i) => `${g.game_id}/${i.id}`));
    const osireleRadky = (rows.results || []).filter(
      (r) => r.item_id.startsWith(`${g.game_id}/`) && !platneKlice.has(r.item_id));
    for (const r of osireleRadky) {
      const del = await env.DB.prepare("DELETE FROM roadmap WHERE item_id = ?")
        .bind(r.item_id).run().catch(() => undefined);
      smazanoOsirelych += del?.meta?.changes ?? 0;
    }

    // Granule, jejichž PR (podle názvu) už je sloučené, se označí hotové –
    // pokryje to i staré úkoly pod jiným item_id (přechod default → hra).
    // Explicitně hotové granule (roadmapa: done: true) se počítají jako hotové
    // i pro ZÁVISLOSTI – ať na ně nečeká nic, až jejich PR vypadne z posledních
    // 100 zavřených PR (titulkový matching by je pak nenašel a DAG by se zasekl).
    const slouceneTituly = mergedTitlesByRepo.get(g.repo) ?? new Set<string>();
    // A2: strom `origin/main` se načte jednou na hru a jen když je potřeba
    // (líně uvnitř smyčky) – hra, která žádné `done: true` nemá, nezaplatí nic.
    let stromMain: Set<string> | null | undefined;
    // Granule, u kterých soubor v `origin/main` chybí – hlásí se jednou za tik.
    const bezPrace: string[] = [];
    for (const i of items) {
      const key = `${g.game_id}/${i.id}`;
      if (i.done === true) {
        if (!done.has(key)) {
          // A2: `done: true` v souboru NENÍ důkaz, že práce je v `main`
          // (S29/S36). Ověřuje se proti `origin/main`; granule bez `owns`
          // (dokumentační) se ověřit nedá a bere se jako hotová.
          if (stromMain === undefined) stromMain = await filesInOriginMain(env, g.repo);
          const owns = i.owns || [];
          const overitelna = stromMain !== null && owns.length > 0;
          const maPraci = overitelna && owns.some((f) => stromMain!.has(f));
          if (overitelna && !maPraci) {
            // Soubor v `main` není → `done` se NEZAPÍŠE a granule se NEVYDÁ.
            // (Chybějící řádek v D1 ji zablokuje i pro závislosti – to je
            // přesně stav, který dřív vznikal tichým no-op UPDATE.)
            bezPrace.push(i.id);
            continue;
          }
          // UPSERT, ne UPDATE (opraveno 30. 9. 2026). `done: true` v souboru je
          // tvrzení „hotovo" a musí mít řádek v D1 – jinak se závislosti
          // nemají čeho chytit. Dřív tu byl jen UPDATE: když řádek chyběl,
          // neudělal NIC (tichý no-op) a `done.add(key)` přesto proběhl, takže
          // se stav v paměti rozešel s databází.
          // Naměřeno: `core.attributes` a `entity.item` řádek neměly a DAG
          // držel pohromadě jen díky záložní cestě (kontrola `done: true`
          // v souboru) – tedy šťastnou shodou okolností, ne konstrukcí.
          await env.DB.prepare(
            `INSERT INTO roadmap (item_id, task_id, status, updated_at)
             VALUES (?, NULL, 'done', datetime('now'))
             ON CONFLICT(item_id) DO UPDATE SET status='done', updated_at=datetime('now')`,
          ).bind(key).run().catch(() => undefined);
          done.add(key);
        }
        continue;
      }
      if (slouceneTituly.has(i.title) && !done.has(key)) {
        await env.DB.prepare(
          "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE item_id=?",
        ).bind(key).run().catch(() => undefined);
        done.add(key);
      }
    }

    // B3b (6. 10. 2026): STROP — granule, která spálila víc než strop běhů, se
    // přestane vydávat. `runs === null` (nezměřeno) strop NESMÍ uplatnit:
    // „nezměřeno“ není nula a tiché zastavení práce kvůli nezměřenému počítadlu
    // by bylo horší než pár spálených pokusů.
    // Značka je `status='blocked'` (řádek se nevydává) a notifikace se pošle
    // JEN když zápis něco změnil — jinak by chodila při každém tiku.
    if (cap > 0 && runs) {
      for (const i of items) {
        const key = `${g.game_id}/${i.id}`;
        if (i.done === true || done.has(key) || blocked.has(key)) continue;
        if (!grainCapped(runs.get(key), cap)) continue;
        const zm = await env.DB.prepare(
          `UPDATE roadmap SET status='blocked', updated_at=datetime('now')
            WHERE item_id=? AND status <> 'blocked'`,
        ).bind(key).run().catch(() => undefined);
        blocked.add(key);
        if (zm?.meta?.changes) {
          await notify(env, "Forge: granule ZASTAVENA (strop)",
            `${key}: spáleno ${runs.get(key)} běhů (strop ${cap}) – přestávám ji vydávat.\n`
            + `Zpět ji pustíš přes POST /roadmap/reset (smaže stav) nebo opravou granule.`,
            "warning").catch(() => undefined);
        }
      }
    }

    // Připravené granule: ne-hotové, depends_on hotové, owns volné a bez
    // čekajícího cooldownu po selhání. Zámek je scoped na repo ({repo}/{soubor}),
    // ať se dvě hry neblokují.
    const ready = items.filter((i) =>
      i.done !== true
      && !done.has(`${g.game_id}/${i.id}`)
      && !blocked.has(`${g.game_id}/${i.id}`)
      && !grainCapped(runs?.get(`${g.game_id}/${i.id}`), cap)
      && (i.depends_on || []).every((d) => done.has(`${g.game_id}/${d}`))
      && !(i.owns || []).some((f) => locked.has(`${g.repo}/${f}`)),
    );
    if (!ready.length) continue;

    // A2: `done: true` bez práce v `origin/main` se musí VIDĚT – jinak je to
    // tichý stav, který vypadá jako hotovo (S35: soubor si varování napíše sám
    // a sám ho ignoruje). Hlásí se jednou za tik, ne za granuli.
    if (bezPrace.length) {
      console.log(`roadmapa ${g.game_id}: done:true bez prace v origin/main: ${bezPrace.join(", ")}`);
      await notify(env, "Forge: done bez práce v main",
        `${g.game_id}: ${bezPrace.length} granulí je v roadmapě 'done: true', `
        + `ale jejich soubory v origin/main nejsou – nezapisuji 'done' a nevydávám je:\n`
        + bezPrace.join(", "), "warning").catch(() => undefined);
    }

    for (const grain of ready) {
      const key = `${g.game_id}/${grain.id}`;
      // Payload nese i velikost a modelovou třídu granule: dispatch je předá
      // workflowu (inputs.max_lines / inputs.model) a brána auto-merge pak
      // posuzuje limit podle granule, ne podle jedné globální konstanty.
      const res = await env.DB.prepare(
        "INSERT INTO tasks (title, kind, target, prompt, payload) VALUES (?, ?, 'cloud', ?, ?)",
      ).bind(grain.title, grain.kind || "code", grain.prompt,
             JSON.stringify({
               owns: grain.owns || [], grain: grain.id, repo: g.repo, game: g.game_id,
               max_lines: maxLinesOf(grain.size_lines), model: grain.model || "any",
             })).run();
      // Starý řádek téže granule (např. selhaný pokus) se přepíše na nový úkol.
      await env.DB.prepare(
        `INSERT INTO roadmap (item_id, task_id, status, updated_at)
         VALUES (?, ?, 'queued', datetime('now'))
         ON CONFLICT(item_id) DO UPDATE SET task_id=excluded.task_id,
           status='queued', updated_at=datetime('now')`,
      ).bind(key, res.meta.last_row_id).run();
      created++;
      createdKeys.push(key);
    }
  }

  if (smazanoOsirelych) {
    await notify(env, "Forge: osiřelé granule uklizeny",
      `${smazanoOsirelych} řádků cache bylo mimo aktuální roadmapu — jejich úlohy\n`
      + `zablokuje invariant „úkol bez řádku v roadmapě“ v témže tiku.`,
      "warning").catch(() => undefined);
  }
  const osirMsg = smazanoOsirelych ? `; osiřelých řádků uklizeno: ${smazanoOsirelych}` : "";
  if (!created) return "roadmapa je hotová (nebo čeká na závislosti / cooldown)" + osirMsg;
  await notify(env, "Forge: z roadmapy",
    `založeno ${created} granulí: ${createdKeys.join(", ")}`, "clipboard");
  return `z roadmapy založeno ${created} granulí` + osirMsg;
}

// ----------------------------------------------------------------- typy ----
interface Task {
  id: number;
  title: string;
  kind: string;
  target: string;
  prompt: string;
  payload: string | null;
  status: string;
  attempts: number;
}

// ------------------------------------------------- tep (heartbeat) cronu ----
// PROČ (H112, P33): `/health` umělo říct jen „služba žije“ (`time`), ale o tom,
// jestli se cron opravdu spouští, netvrdilo NIC — a brána `validate-all` na tom
// stála (`!!h.time`). Naměřeno 9. 10. 2026: tik se zastavil a žádná brána to
// neohlásila. Tep se proto ZAPISUJE a rozlišuje ZDROJ:
//   * `last_cron` — jen PLÁNOVANÝ tik (cron trigger, `scheduled`),
//   * `last_tick` — jakýkoli tik (i ruční `POST /tick`), se zdrojem v `last_tick_zdroj`.
// Ruční tik `last_cron` NEOBNOVÍ, takže brána „cron běží“ se nedá uspokojit
// ručním zavoláním — to je celý rozdíl mezi bránou a tlačítkem.
//
// ⚠ Tabulka `state` se zakládá TADY (idempotentní `CREATE TABLE IF NOT EXISTS`),
// NE v `schema.sql`: `ag-over-cisla.py` měří počet tabulek/sloupců PRÁVĚ
// v `schema.sql` proti číslu v `AGENTS.md`, takže nová tabulka tam by shodila
// trvalá pravidla (H135 — „kdo přidá kontrolu, přeměří cizí tvrzení, které na
// tom čítači stojí“). Stejný vzor už v kódu je: `roadmapTick` přidává sloupce
// přes idempotentní `ALTER` a chybu „duplicate column“ tiše polkne.
let tepTabulkaHotova = false;

async function zapisTep(env: Env, zdroj: "cron" | "manual"): Promise<void> {
  if (!tepTabulkaHotova) {
    await env.DB.prepare("CREATE TABLE IF NOT EXISTS state (k TEXT PRIMARY KEY, v TEXT)").run();
    tepTabulkaHotova = true;
  }
  const ted = new Date().toISOString();
  const uloz = (k: string, v: string) =>
    env.DB.prepare(
      `INSERT INTO state (k, v) VALUES (?, ?)
         ON CONFLICT(k) DO UPDATE SET v = excluded.v`,
    ).bind(k, v).run();
  await uloz("last_tick", ted);
  await uloz("last_tick_zdroj", zdroj);
  if (zdroj === "cron") await uloz("last_cron", ted);
}

// ------------------------------------------------------------------ tick ----
async function tick(env: Env): Promise<string> {
  const maxConcurrent = Number(env.MAX_CONCURRENT || "1");
  const staleMin = Number(env.STALE_MINUTES || "90");
  // Strop pokusů. Slabé free modely mají úspěšnost kolem 10 %, takže tři pokusy
  // jsou málo (naměřeno 30. 9. 2026: po třech selháních čekala granule 6 h,
  // i když šlo jen o syntaktickou chybu v jednom souboru). Pět pokusů s kratším
  // cooldownem drží postup, ale pořád to není nekonečná smyčka.
  const maxAttempts = Number(env.MAX_ATTEMPTS || "5");
  // Cooldown, po kterou selhaná granule nesmí znovu do fronty (RETRY_HOURS).
  // Předává se do roadmapTick, protože ho potřebuje jak skládání `blocked`
  // množiny, tak dispatch smyčka. Ta ho vynucuje i u úloh, které se do `ready`
  // vrátily přes polling: pollRuns roadmapu neaktualizuje, takže bez téhle
  // pojistky se selhaná granule vydala znovu za 2 minuty místo za RETRY_HOURS
  // a spálila všech 5 pokusů (naměřeno 30. 9. 2026, běhy #128–#130).
  const retryH = Number(env.RETRY_HOURS || "6");

  // 0) nejdřív si vyzvedni výsledky běžících cloudových úloh z GitHubu
  const polled = await pollRuns(env).catch((e) => `polling selhal: ${String(e)}`);

  // 0b) watchdog: granule, která spálila příliš mnoho pokusů, se OHLÁSÍ.
  //     B3a jen HLÁSÍ; strop (B3b, `GRAIN_MAX_RUNS`) je od 8. 10. 2026
  //     ZAPNUTÝ na 8 — viz `grainCap`. Počítadlo se měří JEDNOU za tik
  //     a používá se na třech místech (watchdog, roadmapa, dispatch), aby
  //     všechny tři soudily podle TÉHOŽ čísla.
  const grainRunsMap = await grainRuns(env);
  const cap = grainCap(env);
  const eskalovano = await escalateStuckTasks(env, grainRunsMap);

  // 1) zaseknuté úlohy (runner umřel, Actions zrušily job, worker se odpojil)
  const stale = await env.DB.prepare(
    `UPDATE runs SET status='timeout', finished_at=datetime('now'),
       summary='prekrocen casovy limit'
     WHERE status='running' AND started_at < datetime('now', ?)`,
  ).bind(`-${staleMin} minutes`).run();
  if (stale.meta.changes) {
    // Úkol se vrací do fronty, ale JEN dokud má pokusy. Bez téhle podmínky
    // vznikala smyčka: úloha spadla (attempts=3), stale-recovery ji vrátila
    // jako 'ready', dispatch přidal čtvrtý pokus a běh zůstal navěky
    // 'running' — naměřeno 30. 9. 2026 (#107/#108/#109 měly attempts 3 a
    // přesto jely dál). Strop drží `maxAttempts`.
    await env.DB.prepare(
      `UPDATE tasks SET status='ready', updated_at=datetime('now')
        WHERE status='running' AND attempts < ?
          AND id IN (SELECT task_id FROM runs WHERE status='timeout')`,
    ).bind(maxAttempts).run().catch((e) => console.log("requeue po timeoutu selhal:", String(e)));
    await env.DB.prepare(
      `UPDATE tasks SET status='failed', updated_at=datetime('now')
        WHERE status='running'
          AND id IN (SELECT task_id FROM runs WHERE status='timeout')`,
    ).run().catch(() => undefined);
  }
  // Blocked úkoly, které stale-recovery přesto vrátila do fronty, srovnat zpět.
  // (Běží po každém tiku, takže se stav sám uzdraví i bez ručního úklidu.)
  await env.DB.prepare(
    `UPDATE tasks SET status='blocked', updated_at=datetime('now')
      WHERE status IN ('ready','running')
        AND id NOT IN (SELECT task_id FROM roadmap WHERE task_id IS NOT NULL)
        AND id IN (SELECT task_id FROM runs WHERE status='abandoned')`,
  ).run().catch(() => undefined);

  // 1a) B4: REGISTR HER JE ZDROJ PRAVDY O TOM, CO SE SMÍ DISPATCHOVAT.
  // Bez aktivní hry se nedispatchuje NIC — dřív se tady bral `env.GITHUB_REPO`
  // jako fallback a vypnutá hra jela dál (invariant 18). Naměřeno bránou
  // `tools/test-listgames.py` (7 kontrol) — viz `listGames`.
  const aktivniHry = await listGames(env);

  // 1b) doplň připravené granule z roadmapy (závislosti hotové, owns volné).
  // Počítají se jen CLOUDOVÉ úlohy – úkol pro domácí uzel (telefon/PC) nemá
  // blokovat práci, kterou dělá GitHub Actions.
  const roadmapMsg = aktivniHry.length
    ? await roadmapTick(env, retryH, grainRunsMap, cap).catch((e) => `roadmapa selhala: ${String(e)}`)
    : "žádná aktivní hra – roadmapu neřeším (B4)";

  // 1c) INVARIANT: úkol, na který neodkazuje žádný řádek `roadmap`, je zombie.
  // Vzniká po resetu cache, po ručním zásahu nebo po změně ID granulí — a je
  // nebezpečný: conductor ho dispatchuje souběžně s novým úkolem na tutéž
  // granuli, takže se stejná práce dělá dvakrát (naměřeno 30. 9. 2026:
  // #115–#118 jely paralelně s #119–#122).
  //
  // Zdroj pravdy je tabulka `roadmap` — do ní zapisuje VÝHRADNĚ `roadmapTick`
  // (viz INSERT na jednom místě), takže „nemá řádek v roadmap" = „nevydal ho
  // orchestr". Běží po každém tiku, takže se stav sám uzdraví do minuty;
  // ruční úklid (@see /tasks/cleanup) je jen pro okamžitý zásah.
  const zombie = await env.DB.prepare(
    `UPDATE tasks SET status='blocked', updated_at=datetime('now')
      WHERE status IN ('ready','failed','running')
        AND id NOT IN (SELECT task_id FROM roadmap WHERE task_id IS NOT NULL)`,
  ).run().catch(() => undefined);
  if (zombie?.meta.changes) {
    await env.DB.prepare(
      `UPDATE runs SET status='abandoned', finished_at=datetime('now'),
                       summary='invariant: úkol nemá řádek v roadmapě'
        WHERE status='running'
          AND task_id IN (SELECT id FROM tasks WHERE status='blocked')`,
    ).run().catch(() => undefined);
  }
  const zombieMsg = zombie?.meta.changes ? `, zombie zablokováno: ${zombie.meta.changes}` : "";
  // Stav watchdogu se hlásí VŽDYCKY (i s nulou), aby bylo z odpovědi tiku vidět,
  // že opravdu běžel a s jakým prahem – jinak by se jeho výpadek poznal jen
  // tak, že by chyběla notifikace, což se snadno přehlédne.
  const eskalMsg = `, watchdog: ${eskalovano}`;

  // 2) dispatch smyčka: dokud je kapacita a je připravená úloha s volnými owns,
  //    spusť ji. Tím se v jedné vlně rozeběhne víc nezávislých granulí naráz.
  // P29/B6: „spusteno: 0“ musí být VYSVĚTLENÉ. Naměřeno 9. 10. 2026: ruční
  // tik vrátil „spusteno: 0 úloh“ a přitom bylo 5 úloh `ready` — a z odpovědi
  // se NEDALO zjistit, která a proč se přeskočila (`find()` je zahazoval tiše).
  // „Nula a nezměřeno nejsou úspěch.“
  // ⚠ Deklarace je SCHVÁLNĚ NAD `const started`: brány `tools/test-listgames.py`
  // a `_analyza/b4-mutace.py` hledají v kódu dvojici `const started … while (true) {`
  // a vložený řádek MEZI ně by z nich udělal slepé kontroly (naměřeno 9. 10. 2026).
  const preskoceno: string[] = [];
  const started: number[] = [];
  while (true) {
    // B4: bez AKTIVNÍ hry se nedispatchuje (registr her je zdroj pravdy).
    if (!aktivniHry.length) break;
    const running = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM runs WHERE status='running' AND worker IS NULL",
    ).first<{ n: number }>();
    if ((running?.n ?? 0) >= maxConcurrent) break;

    // soubory uzamčené běžícími úlohami
    //
    // POZOR – TADY BYLA VADA (opraveno 1. 10. 2026, invariant 17):
    // `locked` se plnilo HOLÝMI jmény souborů (`locked.add(f)`), ale porovnání
    // níž jde proti `lockKeys()`, což jsou klíče `"{repo}/{soubor}"`. Množiny se
    // tedy NIKDY nemohly protnout a zámek neblokoval nic – dvě granule se
    // stejnými `owns` se rozjely paralelně. Dnes to nemělo následek (roadmapa
    // hry kolizi `owns` nemá), ale při `MAX_CONCURRENT=5` je to tikající bomba:
    // dva agenti si přepíšou tentýž soubor a auto-merge to slije jako cizí práci.
    // Klíč se proto bere z TÉHOŽ místa jako při porovnání.
    const runningRows = await env.DB.prepare(
      "SELECT payload FROM tasks WHERE status='running' AND target='cloud'",
    ).all<{ payload: string | null }>();
    const locked = new Set<string>();
    for (const r of runningRows.results || []) {
      for (const k of lockKeys(r.payload, env)) locked.add(k);
    }

    // nejstarší připravené úlohy; vyber první, jehož owns nekoliduje s běžícími
    //
    // POZOR – COOLDOWN SE MUSÍ VYNUTIT I TADY (opraveno 30. 9. 2026):
    // `ready` úloha se nesmí vydat, dokud její granule čeká cooldown. Jinak se
    // obchází pojistka proti pálení kvóty: polling (pollRuns) vrací selhaný
    // úkol rovnou na `ready`, ale roadmapu neaktualizuje – takže se stejná
    // granule vydala znovu za 2 minuty místo za 3 hodiny a spálila všech
    // 5 pokusů (naměřeno: #128 měl 5 pokusů za 16 minut, #124/#125/#127 za
    // čtvrt hodiny, zatímco RETRY_HOURS=3 a MAX_ATTEMPTS=5).
    //
    // POZOR 2 (druhá iterace téže opravy): podmínka NESMÍ filtrovat podle
    // `rm.status`. První verze se ptala na `rm.status = 'failed'`, jenže
    // pollRuns u ještě-opakovatelného selhání zapisuje `'queued'` (failed až
    // u posledního pokusu) – guard se tak vůbec neuplatnil a díra zůstala.
    // B1 (2. 10. 2026): rozhoduje `naposledy_selhalo`, ne `updated_at`.
    // Původní úvaha („čas poslední změny řádku je spolehlivý nositel cooldownu")
    // platila jen do chvíle, než se do téhož sloupce začal psát i VZNIK granule:
    // `INSERT … status='queued', updated_at=datetime('now')`. Od té chvíle byla
    // nová granule v cooldownu, i když nikdy neselhala (vada S12).
    // Dispatch smyčka se ptá jen na úlohy, které už jsou `ready`.
    const readyAll = await env.DB.prepare(
      `SELECT * FROM tasks WHERE status='ready' AND target='cloud'
         AND NOT EXISTS (
           SELECT 1 FROM roadmap rm
            WHERE rm.task_id = tasks.id
              AND rm.naposledy_selhalo > datetime('now', ?)
         )
        ORDER BY id LIMIT 25`,
    ).bind(`-${retryH} hours`).all<Task>();
    const task = (readyAll.results || []).find((t) => {
      // B3b: zastavenou granuli nevydávej — i kdyby jí v D1 zůstal úkol 'ready'
      // (cooldown i strop se musí ptát na TÝŽ klíč: `grainKeyOf` × `GRAIN_KEY_SQL`).
      // P29/B6: každé `return false` se POJMENUJE — viz `preskoceno` výš.
      // ⚠ KONTROLA STROPU MUSÍ ZŮSTAT JEDNOŘÁDKOVÁ a BEZ `;` PŘED SEBOU:
      // brána `tools/test-grain-cap.py` vytahuje úsek `const task = (readyAll…`
      // až po první `;` a hledá v něm `grainCapped(` i `grainKeyOf(` — pomocná
      // proměnná s `;` by úsek ukončila dřív a kontrola by byla slepá.
      if (grainCapped(grainRunsMap?.get(grainKeyOf(t.payload) || ""), cap)) {
        preskoceno.push(`#${t.id} STROP GRANULE `
          + `${grainRunsMap?.get(grainKeyOf(t.payload) || "")}/${cap} `
          + `(${grainKeyOf(t.payload)})`);
        return false;
      }
      const kolize = lockKeys(t.payload, env).filter((k) => locked.has(k));
      if (kolize.length) {
        preskoceno.push(`#${t.id} ZÁMEK ${kolize.join(", ")}`);
        return false;
      }
      return true;
    });
    if (!task) break;

    const runKey = crypto.randomUUID();
    const workflow = env.WORKFLOW_FILE || "agent.yml";

    const claimed = await env.DB.prepare(
      `UPDATE tasks SET status='running', attempts=attempts+1, updated_at=datetime('now')
        WHERE id=? AND status='ready'`,
    ).bind(task.id).run();
    if (!claimed.meta.changes) continue; // vzal ji mezitím jiný běh

    await env.DB.prepare(
      "INSERT INTO runs (task_id, run_key, workflow, status) VALUES (?, ?, ?, 'running')",
    ).bind(task.id, runKey, workflow).run();

    try {
      // `attempts` se právě zvýšilo (claim výše), takže je to číslo TOHOTO pokusu.
      await dispatchWorkflow(env, task, runKey, (task.attempts ?? 0) + 1);
    } catch (e) {
      await env.DB.batch([
        env.DB.prepare(
          "UPDATE runs SET status='dispatch_failed', finished_at=datetime('now'), summary=? WHERE run_key=?",
        ).bind(String(e).slice(0, 500), runKey),
        env.DB.prepare("UPDATE tasks SET status='ready', updated_at=datetime('now') WHERE id=?")
          .bind(task.id),
      ]);
      await notify(env, "Forge: dispatch failed", `Task #${task.id}: ${String(e)}`, "warning");
      break; // neúspěšný dispatch se zkusí příští tik
    }

    await notify(env, "Forge: task started",
      `#${task.id} ${task.title}\nkind: ${task.kind}\nrun: ${runKey}`, "rocket");
    started.push(task.id);
  }

  const preskocenoMsg = preskoceno.length
    ? ` | přeskočeno: ${[...new Set(preskoceno)].slice(0, 6).join("; ")}` : "";
  // Cooldown vyfiltruje SQL JEŠTĚ PŘED `find()`, takže ho `preskoceno` nevidí.
  // Když se nic nespustilo, musí být vidět i on — jinak zůstane „0 úloh“ tiché.
  let cooldownMsg = "";
  if (!started.length) {
    // ⚠ FORMULACE JE SCHVÁLNĚ JINÁ, NEž MÁ PŮVODNÍ DOTAZ VÝŠ: `_analyza/b2-mutace.py`
    // mutuje porovnání `naposledy_selhalo` s `datetime('now', ?)` v původním dotazu
    // a svou kotvu potřebuje v souboru PRÁVĚ JEDNOU — kdyby tu byla dvakrát
    // (i v komentáři!), mutace by se neprovedla (naměřeno 9. 10. 2026: „kotva je
    // v souboru 2×“). `julianday` je navíc robustnější na tvar uloženého času
    // a při `NULL` vyjde NULL (tedy „není v cooldownu“) — stejná sémantika.
    const cd = await env.DB.prepare(
      `SELECT t.id FROM tasks t JOIN roadmap rm ON rm.task_id = t.id
        WHERE t.status='ready' AND t.target='cloud'
          AND julianday(rm.naposledy_selhalo) > julianday('now', ?)
        ORDER BY t.id LIMIT 10`,
    ).bind(`-${retryH} hours`).all<{ id: number }>().catch(() => null);
    const ids = (cd?.results || []).map((r) => `#${r.id}`);
    if (ids.length) cooldownMsg = ` | v cooldownu ${ids.length} úloh: ${ids.join(", ")}`;
  }
  return `spusteno: ${started.length} úloh; polling: ${polled}; ${roadmapMsg}${zombieMsg}${eskalMsg}${cooldownMsg}${preskocenoMsg}`
    + (aktivniHry.length ? "" : " | POZOR: žádná AKTIVNÍ hra → nedispatchuji (B4)");
}

// ---------------------------------------------------- claim pro domácí uzly ----
async function claim(env: Env, worker: string, kinds: string[]): Promise<Response> {
  const wanted = kinds.length ? kinds : ["test"];
  const placeholders = wanted.map(() => "?").join(",");

  const task = await env.DB.prepare(
    `SELECT * FROM tasks
      WHERE status='ready' AND target='lan' AND kind IN (${placeholders})
      ORDER BY id LIMIT 1`,
  ).bind(...wanted).first<Task>();
  if (!task) return json({ task: null });

  // Optimistický zámek: kdyby úkol mezitím vzal jiný uzel, změny = 0.
  const claimed = await env.DB.prepare(
    `UPDATE tasks SET status='running', attempts=attempts+1, updated_at=datetime('now')
      WHERE id=? AND status='ready'`,
  ).bind(task.id).run();
  if (!claimed.meta.changes) return json({ task: null, note: "prave si to vzal jiny uzel" });

  const runKey = crypto.randomUUID();
  await env.DB.prepare(
    "INSERT INTO runs (task_id, run_key, workflow, worker, status) VALUES (?, ?, ?, ?, 'running')",
  ).bind(task.id, runKey, `worker:${worker}`, worker).run();

  return json({ task, run_key: runKey });
}

// --------------------------------------------------------------- handler ----
export default {
  async scheduled(_event: ScheduledController, env: Env, ctx: ExecutionContext): Promise<void> {
    // H112 (P33): tep se zapisuje AŽ PO DOKONČENÍ tiku — kdyby tik spadl,
    // `last_cron` zestárne a brána to řekne. Zapisuje se tu, ne v `tick()`,
    // aby se zdroj (cron vs. ruční tik) nedal splést.
    ctx.waitUntil(
      tick(env)
        .then((msg) => {
          console.log("tick:", msg);
          return zapisTep(env, "cron").catch((e) => console.log("tep cronu selhal:", String(e)));
        })
        .catch((e) => console.log("tik selhal:", String(e))),
    );
  },

  async fetch(request: Request, env: Env): Promise<Response> {
    const url = new URL(request.url);
    const path = url.pathname.replace(/\/+$/, "") || "/";

    if (path === "/health") {
      const t = await env.DB.prepare("SELECT COUNT(*) AS n FROM tasks WHERE status='ready'")
        .first<{ n: number }>();
      const r = await env.DB.prepare("SELECT COUNT(*) AS n FROM runs WHERE status='running'")
        .first<{ n: number }>();
      const g = await env.DB.prepare("SELECT COUNT(*) AS n FROM games WHERE active=1")
        .first<{ n: number }>();
      const w = await env.DB.prepare(
        `SELECT name, kinds, last_seen,
                CAST((julianday('now') - julianday(last_seen)) * 1440 AS INTEGER) AS minutes_ago
           FROM workers ORDER BY last_seen DESC LIMIT 10`,
      ).all();
      // N0.3: STAV CÍLE zvlášť od stavu služby. `ok` výš zůstává „služba žije“
      // (hlídá ho monitoring dostupnosti) – ale conductor tímhle přestává lhát
      // o tom, že „nic nemá dělat“, když cíl ve skutečnosti nemaká.
      const hry = await env.DB.prepare(
        "SELECT game_id, repo, roadmap_file, active FROM games WHERE active=1 ORDER BY game_id",
      ).all<Game>();
      const targets = await Promise.all(
        (hry.results || []).map((h) => targetState(env, h).catch((e) => ({
          game_id: h.game_id, repo: h.repo,
          error: String(e).slice(0, 200), measured_at: new Date().toISOString(),
        }))),
      );
      // H112 (P33): TEP CRONU. Když tabulka `state` ještě není (starý deploy),
      // vrátí se `null` — a brána to hlásí jako VADU. „Neměřeno“ se nesmí tvářit
      // jako zelená; to je přesně vada, kterou tenhle tep zavírá.
      let tep: {
        last_tick: string | null; last_tick_zdroj: string | null;
        last_cron: string | null; last_cron_min: number | null;
      } = { last_tick: null, last_tick_zdroj: null, last_cron: null, last_cron_min: null };
      try {
        const st = await env.DB.prepare(
          "SELECT k, v FROM state WHERE k IN ('last_tick','last_tick_zdroj','last_cron')",
        ).all<{ k: string; v: string }>();
        const mapa = new Map((st.results || []).map((r) => [r.k, r.v] as const));
        const iso = (k: string): string | null => mapa.get(k) ?? null;
        const stari = (t: string | null): number | null => {
          const ms = t ? Date.parse(t) : NaN;
          return Number.isFinite(ms) ? Math.round((Date.now() - ms) / 60000) : null;
        };
        const cron = iso("last_cron");
        tep = { last_tick: iso("last_tick"), last_tick_zdroj: iso("last_tick_zdroj"),
                last_cron: cron, last_cron_min: stari(cron) };
      } catch (e) {
        console.log("tep cronu nelze precist: " + String(e).slice(0, 120));
      }
      return json({ ok: true, time: new Date().toISOString(), ready: t?.n ?? 0,
                    running: r?.n ?? 0, games: g?.n ?? 0, workers: w.results,
                    targets, ...tep });
    }

    // Ruční tik (testování i externí budík typu cron-job.org)
    if (path === "/tick" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const msg = await tick(env);
      // H112 (P33): ruční tik se ZAPÍŠE taky, ale jako `manual` — `last_cron`
      // neobnoví, takže brána „cron běží (čas)“ se nedá uspokojit ručním tiky.
      await zapisTep(env, "manual").catch((e) => console.log("tep (manual) selhal:", String(e)));
      return json({ message: msg });
    }

    // Ruční vyzvednutí výsledků z GitHubu (jinak to dělá tik každých 15 min)
    if (path === "/poll" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      return json({ message: await pollRuns(env) });
    }

    // Fronta, běhy a uzly obsahují zadání úkolů – proto je chráníme tajemstvím.
    // Veřejné je jen /health (kvůli hlídání dostupnosti). /report má vlastní
    // kontrolu (HMAC podpis z Actions, nebo hlavička s tajemstvím od workera).
    if ((path === "/queue" || path === "/status" || path === "/workers"
         || path === "/games" || path === "/failed" || path === "/roadmap")
        && !secretOk(request, env)) {
      return json({ error: "bad secret" }, 401);
    }

    if (path === "/queue") {
      const tasks = await env.DB.prepare(
        "SELECT id, title, kind, target, status, attempts, created_at FROM tasks ORDER BY id DESC LIMIT 50",
      ).all();
      return json({ tasks: tasks.results });
    }

    if (path === "/roadmap") {
      // Stav granulí podle D1 – item_id, úkol a status. Slouží k ladění
      // orchestrů (např. proč granule čeká). Chráněné tajemstvím jako /queue.
      const rows = await env.DB.prepare(
        `SELECT r.item_id, r.task_id, r.status, r.created_at, r.updated_at,
                t.status AS task_status, t.attempts
           FROM roadmap r LEFT JOIN tasks t ON t.id = r.task_id
          ORDER BY r.item_id`,
      ).all();
      return json({ roadmap: rows.results });
    }

    if (path === "/failed") {
      // Podklad pro `forge replan` (plánovač v2): selhané úkoly i s promptem,
      // payloadem (repo + grain id) a běhy s log_tail – ať klient nemusí nic
      // párovat podle názvu. Chráněné tajemstvím jako /queue.
      const tasks = await env.DB.prepare(
        `SELECT id, title, kind, target, prompt, payload, status, attempts, created_at
           FROM tasks WHERE status='failed' ORDER BY id DESC LIMIT 30`,
      ).all();
      const runs = await env.DB.prepare(
        `SELECT task_id, run_key, status, summary, log_tail, pr_url, finished_at
           FROM runs WHERE status NOT IN ('success', 'running')
          ORDER BY id DESC LIMIT 120`,
      ).all();
      const poUlohach = new Map<number, Record<string, unknown>[]>();
      for (const r of (runs.results || []) as {
        task_id: number; run_key: string; status: string;
        summary: string | null; log_tail: string | null;
        pr_url: string | null; finished_at: string | null;
      }[]) {
        const seznam = poUlohach.get(r.task_id) || [];
        seznam.push({
          run_key: r.run_key, status: r.status, summary: r.summary,
          log_tail: (r.log_tail || "").slice(0, 2000), pr_url: r.pr_url,
          finished_at: r.finished_at,
        });
        poUlohach.set(r.task_id, seznam);
      }
      const ven = (tasks.results || []).map((t) => {
        let payload: Record<string, unknown> = {};
        try { payload = JSON.parse(String((t as { payload?: string | null }).payload || "{}")); }
        catch { payload = {}; }
        return { ...t, payload, runs: poUlohach.get((t as { id: number }).id) || [] };
      });
      return json({ tasks: ven });
    }

    if (path === "/status") {
      const runs = await env.DB.prepare(
        `SELECT r.id, r.task_id, t.title, r.status, r.worker, r.started_at, r.finished_at,
                r.summary, r.pr_url
           FROM runs r LEFT JOIN tasks t ON t.id = r.task_id
          ORDER BY r.id DESC LIMIT 20`,
      ).all();
      return json({ runs: runs.results });
    }

    if (path === "/workers") {
      const workers = await env.DB.prepare("SELECT * FROM workers ORDER BY last_seen DESC").all();
      return json({ workers: workers.results });
    }

    // Registr her: seznam + přihlášení. Herní dokument (DESIGN.md + roadmap.json)
    // v novém repu se do orchestra přihlásí přes POST /game — pak si conductor
    // roadmapu sám najde a začne na hře pracovat.
    if (path === "/games") {
      const games = await env.DB.prepare("SELECT * FROM games ORDER BY game_id").all();
      return json({ games: games.results });
    }

    if (path === "/game" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ game_id?: string; repo?: string; roadmap_file?: string }>();
      if (!body.game_id || !body.repo) return json({ error: "chybi game_id nebo repo" }, 400);
      await env.DB.prepare(
        `INSERT INTO games (game_id, repo, roadmap_file) VALUES (?, ?, ?)
         ON CONFLICT(game_id) DO UPDATE SET
           repo = excluded.repo, roadmap_file = excluded.roadmap_file, active = 1`,
      ).bind(body.game_id, body.repo, body.roadmap_file || ".forge/roadmap.json").run();
      await notify(env, "Forge: hra zaregistrovaná", `${body.game_id} → ${body.repo}`, "game_die");
      return json({ ok: true, game_id: body.game_id, repo: body.repo });
    }

    // Přepnutí aktivní hry. Orchestr je jeden projekt, který se přepíná mezi
    // hrami – tohle je to přepínání. Deaktivace je potřeba, když se hra opustí:
    // bez ní zůstane v `games` s active=1 a její roadmapa se pořád dispatchuje
    // (naměřeno 30. 9. 2026: opuštěná hra pálila free kvótu každou minutu).
    // Pozor: deaktivace hry NEuklízí její granule v tabulce `roadmap` – ty
    // zůstávají a při opětovném zapnutí se na ně naváže.
    if (path === "/game/active" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ game_id?: string; active?: boolean }>();
      if (!body.game_id) return json({ error: "chybi game_id" }, 400);
      const active = body.active === false ? 0 : 1;
      const res = await env.DB.prepare(
        "UPDATE games SET active = ? WHERE game_id = ?",
      ).bind(active, body.game_id).run();
      if (!res.meta.changes) return json({ error: "hra nenalezena", game_id: body.game_id }, 404);
      await notify(env, active ? "Forge: hra zapnutá" : "Forge: hra vypnutá",
                   body.game_id, active ? "game_die" : "game_off");
      return json({ ok: true, game_id: body.game_id, active });
    }

    // Reset stavu roadmapy. Potřebné, když se změní ID granulí v souboru
    // roadmapy (např. přechod `default/*` → `{game}/*` po registraci hry):
    // staré řádky zůstanou v tabulce a conductor se jimi dál řídí, i když
    // v souboru už nejsou. Naměřeno 30. 9. 2026: 81 starých řádků drželo
    // orchestra na mrtvých granulích a granule s `model: strong` se pouštěly
    // slabým modelům (úloha #103 měla 15 pokusů).
    //
    // Co dělá: VYPRAZDNÍ CACHE — smaže řádky v `roadmap` (pro jednu hru, nebo
    // všechny). Frontu postaví znovu až další tik (`roadmapTick`) z AKTUÁLNÍHO
    // souboru roadmapy; tenhle endpoint úkoly do fronty NEVRACÍ.
    // ⚠ OPRAVENO 9. 10. 2026 (nález H128): dřív tu stálo „vrátí jejich selhané
    // úkoly do fronty (status='ready', attempts=0)". To platilo pro PRVNÍ verzi
    // a od 30. 9. 2026 je to NEPRAVDA — vracení úkolů vyrábělo ZOMBIE úlohy
    // (stejná práce jela dvakrát: #115–#118 paralelně s #119–#122). Podrobně to
    // vysvětluje komentář u samotného DELETE níž („POZOR — historie a proč to je
    // takhle“), se kterým byl tenhle odstavec v ROZPORU.
    // Co NEDĚLÁ: nemaže úkoly ani běhy (historie zůstává) a nemaže `games`.
    //
    // Po resetu se stav obnoví sám: conductor si v dalším tiku načte roadmapu
    // z repa a založí granule znovu, se správným `{game_id}/{grain_id}`.
    if (path === "/roadmap/reset" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ game_id?: string; dry_run?: boolean }>()
        .catch(() => ({} as { game_id?: string; dry_run?: boolean }));

      const filtr = body.game_id ? " WHERE item_id LIKE ?" : "";
      const vazba = body.game_id ? " WHERE item_id LIKE ? AND task_id IS NOT NULL"
                                 : " WHERE task_id IS NOT NULL";
      const bindy = body.game_id ? [`${body.game_id}/%`] : [];

      if (body.game_id) {
        const g = await env.DB.prepare("SELECT game_id FROM games WHERE game_id = ?")
          .bind(body.game_id).first();
        if (!g) return json({ error: "hra nenalezena", game_id: body.game_id }, 404);
      }

      // dry_run: jen spočítá, co by se stalo — pro ověření SQL před zásahem.
      if (body.dry_run) {
        const gr = await env.DB.prepare(`SELECT COUNT(*) AS n FROM roadmap${filtr}`)
          .bind(...bindy).first<{ n: number }>();
        const ta = await env.DB.prepare(
          `SELECT COUNT(*) AS n FROM tasks WHERE status='failed' AND id IN (
             SELECT task_id FROM roadmap${vazba})`,
        ).bind(...bindy).first<{ n: number }>();
        return json({ ok: true, dry_run: true, game_id: body.game_id ?? "(vse)",
                      smazal_bych_granuli: gr?.n ?? 0, dotklo_bych_se_ukolu: ta?.n ?? 0 });
      }

      // POZOR — historie a proč to je takhle (opraveno 30. 9. 2026):
      // První verze nejdřív vrátila selhané úkoly do fronty ('ready',
      // attempts=0) a PAK smazala řádky roadmapy. Tím se ale úkoly staly
      // osiřelými — a osiřelý úkol se v dalším tiku rozjede jako zombie
      // souběžně s novým. Naměřeno: po resetu jely #115–#118 paralelně
      // s novými #119–#122, tedy dvakrát stejná práce.
      //
      // Reset teď dělá JEDNU věc: vyprázdní cache. Frontu postaví znovu
      // `roadmapTick` z aktuálního souboru (nové úkoly = čisté `attempts`).
      // Staré úkoly řeší invariant v tiku (viz `syncWithRoadmap`).
      const del = await env.DB.prepare(`DELETE FROM roadmap${filtr}`).bind(...bindy).run();

      return json({ ok: true, game_id: body.game_id ?? "(vse)",
                    smazano_granuli: del.meta.changes,
                    poznamka: "fronta se znovu postaví v dalším tiku (do 1 minuty)" });
    }

    // Úklid osiřelých úkolů. Vznikají, když se změní ID granulí v roadmapě:
    // staré úkoly zůstanou ve frontě `ready`, ale žádný řádek v `roadmap` už
    // na ně neodkazuje — takže je conductor pořád dispatchuje, i když je
    // v aktuální roadmapě nemá. Naměřeno 30. 9. 2026: po resetu roadmapy se
    // probudily úkoly #11–#98 z éry GameForge a začaly se dispatchovat
    // paralelně s novými (#107+), což pálilo free kvótu na dvakrát.
    //
    // Úkoly se NEMAŽOU, jen se označí `blocked`: tabulka `runs` má
    // `task_id REFERENCES tasks(id)`, takže DELETE padá na cizím klíči
    // (Worker pak vrátí 500). `blocked` úlohy conductor nedispatchuje a `claim`
    // je taky nebere — a historie běhů zůstane dohledatelná.
    //
    // Co označí: úkoly ve stavu `ready`/`failed`, na které neodkazuje žádný
    // řádek `roadmap` a které nejsou zrovna `running`.
    // Co NEDĚLÁ: nesahá na běžící ani hotové úkoly, nemaže běhy.
    //
    // ⚠ SPRÁVNÉ POŘADÍ (opraveno 9. 10. 2026, nález H128): **nejdřív PUSH**
    // (roadmapa se čte z `main` v GitHubu — odtud, řádek s `raw.githubusercontent.com`),
    // **pak cleanup — a hru NECH ZAPNUTOU**. Dřív tu stálo „nejdřív se hra vypne
    // (`/game/active` false), pak cleanup, pak se hra zapne“; to je
    // NEPROVEDITELNÉ, protože `listGames` vrací jen hry `active = 1`: s vypnutou
    // hrou je seznam her prázdný → `platne` prázdné → endpoint vrátí **503**
    // („žádná platná granule – roadmapy jsou prázdné, nemažu“) a neudělá NIC.
    // Naměřeno na živé službě 9. 10. 2026: hra vypnutá → 503, hra zapnutá → 200.
    if (path === "/tasks/cleanup" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ dry_run?: boolean }>()
        .catch(() => ({} as { dry_run?: boolean }));

      // ── KROK A: srovnat tabulku `roadmap` se SOUBORY roadmap v repech ──
      // `roadmap` je jen cache toho, co conductor vydal. Když se soubor změní
      // (granule se přejmenují nebo vypadnou), staré řádky v cache zůstanou
      // a conductor se jimi dál řídí — dispatchuje práci, kterou soubor nezná.
      // Naměřeno 30. 9. 2026: v cache bylo 81 řádků z éry GameForge, soubor má
      // 18 granulí. Sedm starých úloh (#14–#59) tím zabíralo ~44 % kapacity.
      const games = await listGames(env);
      const platne = new Set<string>();
      const hryBezSouboru: string[] = [];
      for (const g of games) {
        try {
          const url = `https://raw.githubusercontent.com/${g.repo}/main/${g.roadmap_file}`;
          const r = await fetch(url);
          if (!r.ok) { hryBezSouboru.push(`${g.game_id} (HTTP ${r.status})`); continue; }
          const doc = await r.json<{ grains?: { id?: string }[]; tasks?: { id?: string }[] }>();
          for (const it of doc.grains || doc.tasks || []) {
            if (it?.id) platne.add(`${g.game_id}/${it.id}`);
          }
        } catch (e) {
          hryBezSouboru.push(`${g.game_id} (${String(e).slice(0, 60)})`);
        }
      }
      // Bezpečnostní pojistka: kdyby se roadmapa nepodařila načíst, NEMAŽ.
      if (hryBezSouboru.length) {
        return json({ error: "roadmapa se nedá načíst, radši nemažu", hry: hryBezSouboru }, 503);
      }
      if (!platne.size) {
        return json({ error: "žádná platná granule – roadmapy jsou prázdné, nemažu" }, 503);
      }

      const vsechnyRadky = await env.DB.prepare("SELECT item_id, task_id FROM roadmap").all<{ item_id: string; task_id: number | null }>();
      const osirele = (vsechnyRadky.results || []).filter((r) => !platne.has(r.item_id));
      const osireleTaskIds = osirele.map((r) => r.task_id).filter((x): x is number => typeof x === "number");

      // ── KROK B: úlohy bez vazby na roadmapu (starý význam) ──
      const podminka = `status IN ('ready','failed')
          AND id NOT IN (SELECT task_id FROM roadmap WHERE task_id IS NOT NULL)`;

      if (body.dry_run) {
        const n = await env.DB.prepare(`SELECT COUNT(*) AS n FROM tasks WHERE ${podminka}`)
          .first<{ n: number }>();
        const ukazka = await env.DB.prepare(
          `SELECT id, title, status FROM tasks WHERE ${podminka} ORDER BY id LIMIT 10`).all();
        return json({
          ok: true, dry_run: true,
          platnych_granuli_v_souborech: platne.size,
          radku_v_cache: (vsechnyRadky.results || []).length,
          osirelych_radku: osirele.length,
          osirele_ukoly: osireleTaskIds.length,
          ukoly_bez_vazby: n?.n ?? 0,
          ukazka_osirelych: osirele.slice(0, 10).map((r) => r.item_id),
          ukazka_bez_vazby: ukazka.results,
        });
      }

      // Úlohy z osiřelých řádků zablokovat (jinak by běžely dál jako zombie).
      let zablokovanoZRadku = 0;
      for (let i = 0; i < osireleTaskIds.length; i += 25) {
        const davka = osireleTaskIds.slice(i, i + 25);
        const r = await env.DB.prepare(
          `UPDATE tasks SET status='blocked', updated_at=datetime('now')
            WHERE id IN (${davka.map(() => "?").join(",")})
              AND status NOT IN ('done','blocked')`,
        ).bind(...davka).run();
        zablokovanoZRadku += r.meta.changes ?? 0;
      }
      // A teprve pak smazat osiřelé řádky cache (po dávkách – DELETE s velkým
      // IN naráží na CPU limit Workeru, 10 ms).
      let smazanoRadku = 0;
      for (const r of osirele) {
        const res = await env.DB.prepare("DELETE FROM roadmap WHERE item_id = ?")
          .bind(r.item_id).run();
        smazanoRadku += res.meta.changes ?? 0;
      }

      const upd = await env.DB.prepare(
        `UPDATE tasks SET status='blocked', updated_at=datetime('now') WHERE ${podminka}`,
      ).run();

      // Navíc: dorazí běhy, které zůstaly navěky `running`, i když jejich úkol
      // je už `blocked`. Bez toho je stale-recovery (STALE_MINUTES) pořád
      // vrací do fronty — a protože vrací `WHERE status='running'` bez ohledu
      // na `blocked`, úloha se resurrectuje a dispatchuje dokola.
      // Naměřeno 30. 9. 2026: běhy #14/#24/#35/#44/#58/#59 se obnovovaly
      // každé ~2 minuty a pálily free kvótu na mrtvých granulích.
      const doraz = await env.DB.prepare(
        `UPDATE runs SET status='abandoned', finished_at=datetime('now'),
                         summary='úklid: úkol byl označen blocked'
          WHERE status='running'
            AND task_id IN (SELECT id FROM tasks WHERE status='blocked')`,
      ).run();

      // Pojistka: kdyby některá blocked úloha zůstala ve stavu running
      // (stale-recovery ji stihla přeskočit), srovnat i ji.
      const srovnej = await env.DB.prepare(
        `UPDATE tasks SET status='blocked', updated_at=datetime('now')
          WHERE status='running'
            AND id NOT IN (SELECT task_id FROM runs WHERE status='running')`,
      ).run();

      // ── KROK C: úlohy, které vypadly z cache roadmapy ──
      // Po resetu roadmapy (nebo po srovnání cache se souborem) zůstanou úlohy,
      // na které žádný řádek `roadmap` neodkazuje. Když doběhnou, `/report` je
      // označí `failed` — a protože je nemá co vrátit do fronty, zůstanou
      // navěky mrtvé a conductor je může znovu vydat jako duplicitní granuli.
      // Naměřeno 30. 9. 2026: #107–#110 běžely souběžně s novými #111–#114,
      // tedy dvakrát stejná práce.
      const vypadle = await env.DB.prepare(
        `UPDATE tasks SET status='blocked', updated_at=datetime('now')
          WHERE status IN ('ready','failed','running')
            AND id NOT IN (SELECT task_id FROM roadmap WHERE task_id IS NOT NULL)`,
      ).run();
      const dorazVypadlych = await env.DB.prepare(
        `UPDATE runs SET status='abandoned', finished_at=datetime('now'),
                         summary='úklid: úloha vypadla z cache roadmapy'
          WHERE status='running'
            AND task_id IN (SELECT id FROM tasks WHERE status='blocked')`,
      ).run();

      return json({ ok: true,
                    smazano_osirelych_radku: smazanoRadku,
                    zablokovano_z_radku: zablokovanoZRadku,
                    oznaceno_blocked: upd.meta.changes,
                    dorazeno_behu: doraz.meta.changes,
                    srovnano_tasku: srovnej.meta.changes,
                    vypadlych_z_cache: vypadle.meta.changes,
                    dorazeno_vypadlych: dorazVypadlych.meta.changes });
    }

    // Heartbeat domácího uzlu – podle něj je vidět, že uzel žije
    if (path === "/heartbeat" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const name = request.headers.get("x-forge-worker") || "";
      if (!name) return json({ error: "chybi hlavicka x-forge-worker" }, 400);
      const body = await request.json<{ kinds?: string[]; info?: unknown; platform?: string }>();
      await env.DB.prepare(
        `INSERT INTO workers (name, kinds, info, last_seen) VALUES (?, ?, ?, datetime('now'))
         ON CONFLICT(name) DO UPDATE SET
           kinds = excluded.kinds, info = excluded.info, last_seen = datetime('now')`,
      ).bind(name, (body.kinds || []).join(","),
             JSON.stringify({ tools: body.info, platform: body.platform })).run();
      return json({ ok: true, name });
    }

    // Vyzvednutí úkolu domácím uzlem (pull-worker)
    if (path === "/claim" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const name = request.headers.get("x-forge-worker") || "";
      if (!name) return json({ error: "chybi hlavicka x-forge-worker" }, 400);
      const body = await request.json<{ kinds?: string[] }>().catch(() => ({ kinds: [] }));
      return claim(env, name, body.kinds || []);
    }

    // Založení úkolu (z telefonu, z CI nebo ručně)
    if (path === "/task" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{
        title?: string; kind?: string; target?: string; prompt?: string; payload?: unknown;
      }>();
      if (!body.prompt || !body.title) return json({ error: "chybi title nebo prompt" }, 400);
      const target = body.target === "lan" ? "lan" : "cloud";
      const res = await env.DB.prepare(
        "INSERT INTO tasks (title, kind, target, prompt, payload) VALUES (?, ?, ?, ?, ?)",
      ).bind(body.title, body.kind || "code", target, body.prompt,
             body.payload ? JSON.stringify(body.payload) : null).run();
      await notify(env, "Forge: task queued",
        `${body.title} (${body.kind || "code"}, ${target})`, "memo");
      return json({ ok: true, id: res.meta.last_row_id, target });
    }

    // Report z GitHub Actions nebo z domácího uzlu.
    // Actions posílá HMAC podpis (tajemství se tak neobjeví v logu jobu),
    // domácí uzel pošle hlavičku x-forge-secret. Obojí je přijatelné.
    if (path === "/report" && request.method === "POST") {
      const raw = await request.text();
      const sig = request.headers.get("x-forge-signature") || "";
      const expected = await hmacHex(env.WEBHOOK_SECRET, raw);
      const bySignature = sig.length > 0 && timingSafeEqual(sig, expected);
      if (!bySignature && !secretOk(request, env)) {
        return json({ error: "bad signature or secret" }, 401);
      }

      const body = JSON.parse(raw) as {
        run_key?: string; status?: string; summary?: string;
        pr_url?: string; log_tail?: string; artifacts?: unknown;
      };
      if (!body.run_key || !body.status) return json({ error: "chybi run_key/status" }, 400);

      const run = await env.DB.prepare("SELECT * FROM runs WHERE run_key = ?")
        .bind(body.run_key).first<{ id: number; task_id: number; worker: string | null }>();
      if (!run) return json({ error: "neznamy run_key" }, 404);

      const artifacts = body.artifacts ? JSON.stringify(body.artifacts).slice(0, 4000) : null;
      await env.DB.prepare(
        `UPDATE runs SET status=?, finished_at=datetime('now'), summary=?, pr_url=?,
                          log_tail=?, artifacts=?
          WHERE run_key=?`,
      ).bind(body.status, body.summary || null, body.pr_url || null,
             (body.log_tail || "").slice(0, 8000), artifacts, body.run_key).run();

      // Úspěch = hotovo. Selhání se vrací do fronty, dokud jsou pokusy.
      if (body.status === "success") {
        await env.DB.prepare("UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?")
          .bind(run.task_id).run();
        await env.DB.prepare(
          "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE task_id=?",
        ).bind(run.task_id).run().catch(() => undefined);
      } else {
        const t = await env.DB.prepare("SELECT attempts, status FROM tasks WHERE id=?")
          .bind(run.task_id).first<{ attempts: number; status: string }>();
        // `blocked` je terminální (úklid) – report ho nesmí vzkřísit na 'ready'.
        // `done` taky ne: běh mohl doběhnout pozdě, po úspěšnějším pokusu.
        if (t?.status === "blocked" || t?.status === "done") {
          return json({ ok: true, task_id: run.task_id, poznamka: `stav '${t.status}' se nemění` });
        }
        const nextStatus = (t?.attempts ?? 0) >= Number(env.MAX_ATTEMPTS || "5") ? "failed" : "ready";
        await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
          .bind(nextStatus, run.task_id).run();
        // B1: `naposledy_selhalo` se plní při KAŽDÉM selhání, ne jen u
        // posledního pokusu — cooldown se ptá na něj, takže kdyby tu chybělo,
        // granule by se po opakovatelném selhání vydala okamžitě.
        if (nextStatus === "failed") {
          await env.DB.prepare(
            `UPDATE roadmap SET status='failed', updated_at=datetime('now'),
               naposledy_selhalo = datetime('now') WHERE task_id=?`,
          ).bind(run.task_id).run().catch(() => undefined);
        } else {
          await env.DB.prepare(
            `UPDATE roadmap SET naposledy_selhalo = datetime('now') WHERE task_id=?`,
          ).bind(run.task_id).run().catch(() => undefined);
        }
      }

      // Statistiky uzlu – podle nich je vidět, který stroj se osvědčil
      if (run.worker) {
        const col = body.status === "success" ? "jobs_done" : "jobs_failed";
        await env.DB.prepare(`UPDATE workers SET ${col} = ${col} + 1 WHERE name = ?`)
          .bind(run.worker).run().catch(() => undefined);
      }

      const icon = body.status === "success" ? "white_check_mark" : "warning";
      await notify(env, `Forge: ${body.status}`,
        `${body.summary || ""}\n${body.pr_url || ""}`.trim(), icon);
      return json({ ok: true });
    }

    return json({
      service: "forge-conductor",
      endpoints: ["/health", "/tick", "/poll", "/queue", "/status", "/workers",
                  "/games", "/game", "/heartbeat", "/claim", "/task", "/report",
                  "/failed"],
    });
  },
};

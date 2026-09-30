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
  MAX_ATTEMPTS?: string;      // kolik pokusů smí úloha mít, než zůstane 'failed' (výchozí 5)
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

async function dispatchWorkflow(env: Env, task: Task, runKey: string): Promise<void> {
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
      },
    }),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`GitHub dispatch ${res.status}: ${text.slice(0, 300)}`);
  }
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
        // i krok automatického sloučení. Stav mergnutí je proto v tuhle chvíli
        // už konečný a dá se věřit.
        merged = Boolean(prs?.[0]?.merged_at);
      } catch { /* PR nemusí existovat, to není chyba běhu */ }
    }

    await env.DB.prepare(
      `UPDATE runs SET status=?, finished_at=datetime('now'), summary=?, pr_url=?
        WHERE id=?`,
    ).bind(ok ? "success" : String(run.conclusion || "failed"),
           `GitHub Actions: ${run.conclusion}`, prUrl, row.run_id).run();

    if (ok) {
      await env.DB.prepare("UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?")
        .bind(row.task_id).run();
      await env.DB.prepare(
        "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE task_id=?",
      ).bind(row.task_id).run().catch(() => undefined);
    } else {
      const t = await env.DB.prepare("SELECT attempts FROM tasks WHERE id=?")
        .bind(row.task_id).first<{ attempts: number }>();
      const nextStatus = (t?.attempts ?? 0) >= maxAttempts ? "failed" : "ready";
      await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
        .bind(nextStatus, row.task_id).run();
      // Když úkol definitivně selhal, označíme i položku roadmapy. Jinak by
      // zůstala navěky ve stavu „queued" a nebylo by poznat, že se nepovedla.
      // updated_at slouží jako čas posledního pokusu – od něj se počítá
      // cooldown, po kterém smí granule znovu do fronty.
      if (nextStatus === "failed") {
        await env.DB.prepare(
          "UPDATE roadmap SET status='failed', updated_at=datetime('now') WHERE task_id=?",
        ).bind(row.task_id).run().catch(() => undefined);
      }
    }

    const prNote = prUrl
      ? (merged ? "\n(sloučeno automaticky)" : "\n(čeká na tvé sloučení – nesplnilo pravidla)")
      : "";
    await notify(env, ok ? "Forge: hotovo" : "Forge: selhalo",
      `#${row.task_id} ${row.title}\n${run.conclusion}${prUrl ? `\n${prUrl}` : ""}${prNote}`,
      ok ? "white_check_mark" : "warning");
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

async function listGames(env: Env): Promise<Game[]> {
  const rows = await env.DB.prepare(
    "SELECT game_id, repo, roadmap_file, active FROM games WHERE active = 1 ORDER BY game_id",
  ).all<Game>();
  if (rows.results?.length) return rows.results;
  // Zpětná kompatibilita: žádná registrovaná hra = jeden defaultní repo, jako dřív.
  return [{
    game_id: "default",
    repo: env.GITHUB_REPO,
    roadmap_file: env.ROADMAP_FILE || ".forge/roadmap.json",
    active: 1,
  }];
}

async function roadmapTick(env: Env): Promise<string> {
  const games = await listGames(env);

  // Samomigrace schématu (idempotentní): roadmap.updated_at přibyl kvůli
  // cooldownu retry. Stará D1 sloupec nemá; CREATE TABLE IF NOT EXISTS v
  // schema.sql ho tam nepřidá, proto se to dělá tady – když už existuje,
  // ALTER selže s „duplicate column name" a to se tiše polkne.
  await env.DB.prepare("ALTER TABLE roadmap ADD COLUMN updated_at TEXT")
    .run().catch((e) => console.log("roadmap.updated_at: " + String(e).slice(0, 100)));
  await env.DB.prepare("UPDATE roadmap SET updated_at = created_at WHERE updated_at IS NULL")
    .run().catch(() => undefined);

  // Stav granulí drží tabulka roadmap (item_id = {game_id}/{grain_id}).
  // Řádek sám o sobě nestačí – je vidět i stav úlohy (LEFT JOIN tasks).
  interface GrainRow {
    item_id: string;
    task_id: number | null;
    rstatus: string | null;
    rupd: string | null;
    tstatus: string | null;
    tupd: string | null;
  }
  const rows = await env.DB.prepare(
    `SELECT r.item_id, r.task_id, r.status AS rstatus, r.updated_at AS rupd,
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
  const retryH = Number(env.RETRY_HOURS || "6");
  for (const r of rows.results || []) {
    const failed = r.tstatus === "failed" || r.rstatus === "failed";
    const finished = r.tstatus === "done" || r.rstatus === "done"
      || (r.task_id != null && mergedTasks.has(r.task_id));
    if (finished) { done.add(r.item_id); continue; }
    if (!failed) { blocked.add(r.item_id); continue; }
    const ts = r.tupd || r.rupd || null;
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

    // Granule, jejichž PR (podle názvu) už je sloučené, se označí hotové –
    // pokryje to i staré úkoly pod jiným item_id (přechod default → hra).
    // Explicitně hotové granule (roadmapa: done: true) se počítají jako hotové
    // i pro ZÁVISLOSTI – ať na ně nečeká nic, až jejich PR vypadne z posledních
    // 100 zavřených PR (titulkový matching by je pak nenašel a DAG by se zasekl).
    const slouceneTituly = mergedTitlesByRepo.get(g.repo) ?? new Set<string>();
    for (const i of items) {
      const key = `${g.game_id}/${i.id}`;
      if (i.done === true) {
        if (!done.has(key)) {
          await env.DB.prepare(
            "UPDATE roadmap SET status='done', updated_at=datetime('now') WHERE item_id=?",
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

    // Připravené granule: ne-hotové, depends_on hotové, owns volné a bez
    // čekajícího cooldownu po selhání. Zámek je scoped na repo ({repo}/{soubor}),
    // ať se dvě hry neblokují.
    const ready = items.filter((i) =>
      i.done !== true
      && !done.has(`${g.game_id}/${i.id}`)
      && !blocked.has(`${g.game_id}/${i.id}`)
      && (i.depends_on || []).every((d) => done.has(`${g.game_id}/${d}`))
      && !(i.owns || []).some((f) => locked.has(`${g.repo}/${f}`)),
    );
    if (!ready.length) continue;

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

  if (!created) return "roadmapa je hotová (nebo čeká na závislosti / cooldown)";
  await notify(env, "Forge: z roadmapy",
    `založeno ${created} granulí: ${createdKeys.join(", ")}`, "clipboard");
  return `z roadmapy založeno ${created} granulí`;
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

// ------------------------------------------------------------------ tick ----
async function tick(env: Env): Promise<string> {
  const maxConcurrent = Number(env.MAX_CONCURRENT || "1");
  const staleMin = Number(env.STALE_MINUTES || "90");
  // Strop pokusů. Slabé free modely mají úspěšnost kolem 10 %, takže tři pokusy
  // jsou málo (naměřeno 30. 9. 2026: po třech selháních čekala granule 6 h,
  // i když šlo jen o syntaktickou chybu v jednom souboru). Pět pokusů s kratším
  // cooldownem drží postup, ale pořád to není nekonečná smyčka.
  const maxAttempts = Number(env.MAX_ATTEMPTS || "5");

  // 0) nejdřív si vyzvedni výsledky běžících cloudových úloh z GitHubu
  const polled = await pollRuns(env).catch((e) => `polling selhal: ${String(e)}`);

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

  // 1b) doplň připravené granule z roadmapy (závislosti hotové, owns volné).
  // Počítají se jen CLOUDOVÉ úlohy – úkol pro domácí uzel (telefon/PC) nemá
  // blokovat práci, kterou dělá GitHub Actions.
  const roadmapMsg = await roadmapTick(env).catch((e) => `roadmapa selhala: ${String(e)}`);

  // 2) dispatch smyčka: dokud je kapacita a je připravená úloha s volnými owns,
  //    spusť ji. Tím se v jedné vlně rozeběhne víc nezávislých granulí naráz.
  const started: number[] = [];
  while (true) {
    const running = await env.DB.prepare(
      "SELECT COUNT(*) AS n FROM runs WHERE status='running' AND worker IS NULL",
    ).first<{ n: number }>();
    if ((running?.n ?? 0) >= maxConcurrent) break;

    // soubory uzamčené běžícími úlohami
    const runningRows = await env.DB.prepare(
      "SELECT payload FROM tasks WHERE status='running' AND target='cloud'",
    ).all<{ payload: string | null }>();
    const locked = new Set<string>();
    for (const r of runningRows.results || []) {
      try { for (const f of (JSON.parse(r.payload || "{}").owns || [])) locked.add(f); } catch { /* */ }
    }

    // nejstarší připravené úlohy; vyber první, jehož owns nekoliduje s běžícími
    const readyAll = await env.DB.prepare(
      "SELECT * FROM tasks WHERE status='ready' AND target='cloud' ORDER BY id LIMIT 25",
    ).all<Task>();
    const task = (readyAll.results || []).find((t) => {
      return !lockKeys(t.payload, env).some((k) => locked.has(k));
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
      await dispatchWorkflow(env, task, runKey);
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

  return `spusteno: ${started.length} úloh; polling: ${polled}; ${roadmapMsg}`;
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
    ctx.waitUntil(tick(env).then((msg) => console.log("tick:", msg)));
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
      return json({ ok: true, time: new Date().toISOString(), ready: t?.n ?? 0,
                    running: r?.n ?? 0, games: g?.n ?? 0, workers: w.results });
    }

    // Ruční tik (testování i externí budík typu cron-job.org)
    if (path === "/tick" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      return json({ message: await tick(env) });
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
    // Co dělá:
    //   - smaže řádky v `roadmap` (pro jednu hru, nebo všechny),
    //   - vrátí jejich selhané úkoly do fronty (status='ready', attempts=0),
    //     aby se rozjely znovu — už se správným modelem z roadmapy.
    // Co NEDĚLÁ: nemaže úkoly ani běhy (historie zůstává) a nemaže `games`.
    //
    // Po resetu se stav obnoví sám: conductor si v dalším tiku načte roadmapu
    // z repa a založí granule znovu, se správným `{game_id}/{grain_id}`.
    if (path === "/roadmap/reset" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ game_id?: string; dry_run?: boolean }>().catch(() => ({}));

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
                      smazal_bych_granuli: gr?.n ?? 0, vratil_bych_do_fronty: ta?.n ?? 0 });
      }

      // POZOR na pořadí: úkoly se hledají PŘES tabulku roadmap, takže se musí
      // přečíst dřív, než se řádky smažou.
      const upd = await env.DB.prepare(
        `UPDATE tasks SET status='ready', attempts=0, updated_at=datetime('now')
          WHERE status='failed' AND id IN (
            SELECT task_id FROM roadmap${vazba}
          )`,
      ).bind(...bindy).run();
      const del = await env.DB.prepare(`DELETE FROM roadmap${filtr}`).bind(...bindy).run();

      return json({ ok: true, game_id: body.game_id ?? "(vse)",
                    smazano_granuli: del.meta.changes, vraceno_do_fronty: upd.meta.changes });
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
    // Doporučený postup: nejdřív se hra vypne (`/game/active` false), pak
    // cleanup, pak se hra zapne — tiky mezitím nezakládají nové úkoly.
    if (path === "/tasks/cleanup" && request.method === "POST") {
      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);
      const body = await request.json<{ dry_run?: boolean }>().catch(() => ({}));

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
        const nextStatus = (t?.attempts ?? 0) >= maxAttempts ? "failed" : "ready";
        await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
          .bind(nextStatus, run.task_id).run();
        if (nextStatus === "failed") {
          await env.DB.prepare(
            "UPDATE roadmap SET status='failed', updated_at=datetime('now') WHERE task_id=?",
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

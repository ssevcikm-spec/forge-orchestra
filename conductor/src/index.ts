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
        const res = await fetch(`https://api.telegram.org/bot${tgToken}/sendMessage`, {
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
        const res = await fetch(discord, {
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
        const res = await fetch(`${server}/${topic}`, {
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
async function dispatchWorkflow(env: Env, task: Task, runKey: string): Promise<void> {
  const workflow = env.WORKFLOW_FILE || "agent.yml";
  const url = `https://api.github.com/repos/${env.GITHUB_REPO}/actions/workflows/${workflow}/dispatches`;
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
async function github(env: Env, path: string): Promise<any> {
  const res = await fetch(`https://api.github.com/repos/${env.GITHUB_REPO}${path}`, {
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
  const rows = await env.DB.prepare(
    `SELECT r.id AS run_id, r.run_key, r.task_id, t.title
       FROM runs r JOIN tasks t ON t.id = r.task_id
      WHERE r.status = 'running' AND r.worker IS NULL
      ORDER BY r.id LIMIT 10`,
  ).all<{ run_id: number; run_key: string; task_id: number; title: string }>();
  if (!rows.results?.length) return "zadny cloudovy beh nebezi";

  let runs: any[];
  try {
    const data = await github(env, "/actions/runs?event=workflow_dispatch&per_page=50");
    runs = data.workflow_runs || [];
  } catch (e) {
    return `GitHub se neozval: ${String(e).slice(0, 120)}`;
  }

  const owner = env.GITHUB_REPO.split("/")[0];
  let updated = 0;

  for (const row of rows.results) {
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
        const prs = await github(env,
          `/pulls?head=${owner}:forge/task-${row.task_id}&state=all`);
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
    } else {
      const t = await env.DB.prepare("SELECT attempts FROM tasks WHERE id=?")
        .bind(row.task_id).first<{ attempts: number }>();
      const nextStatus = (t?.attempts ?? 0) >= 3 ? "failed" : "ready";
      await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
        .bind(nextStatus, row.task_id).run();
      // Když úkol definitivně selhal, označíme i položku roadmapy. Jinak by
      // zůstala navěky ve stavu „queued" a nebylo by poznat, že se nepovedla.
      if (nextStatus === "failed") {
        await env.DB.prepare("UPDATE roadmap SET status='failed' WHERE task_id=?")
          .bind(row.task_id).run().catch(() => undefined);
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
  depends_on?: string[];  // id granulí, které musejí být sloučené dřív
  owns?: string[];        // soubory, které granule smí měnit (zámek souběhu)
}

async function roadmapTick(env: Env): Promise<string> {
  const file = env.ROADMAP_FILE || ".forge/roadmap.json";

  let items: RoadmapItem[] = [];
  try {
    const data = await github(env, `/contents/${file}`);
    // Obsah chodí v base64; přes bajty se správně dekóduje i čeština.
    const bytes = Uint8Array.from(
      atob(String(data.content || "").replace(/\n/g, "")),
      (c) => c.charCodeAt(0),
    );
    // DAG se čte z `grains`; zpětná kompatibilita: starý formát měl `tasks`.
    const parsed = JSON.parse(new TextDecoder().decode(bytes));
    items = (parsed.grains || parsed.tasks || []) as RoadmapItem[];
  } catch (e) {
    return `roadmapu nejde přečíst: ${String(e).slice(0, 120)}`;
  }
  if (!items.length) return "roadmapa je prázdná";

  // „Hotové" = granule, jejichž úloha je done (sloučená). „Dispatchnuté" = cokoli,
  // co už je v tabulce roadmap (abychom granuli nezaložili dvakrát, i když se
  // její úloha ještě vrací do fronty na pokus).
  const doneRows = await env.DB.prepare(
    "SELECT r.item_id FROM roadmap r JOIN tasks t ON t.id = r.task_id WHERE t.status = 'done'",
  ).all<{ item_id: string }>();
  const done = new Set((doneRows.results || []).map((r) => r.item_id));
  const allRows = await env.DB.prepare("SELECT item_id FROM roadmap").all<{ item_id: string }>();
  const dispatched = new Set((allRows.results || []).map((r) => r.item_id));

  // Nezahrnout uživatele hromadou pull requestů, které zatím nikdo nezkontroloval.
  const maxPrs = Number(env.ROADMAP_MAX_PRS || "3");
  try {
    const prs = await github(env, "/pulls?state=open&per_page=30");
    if (Array.isArray(prs) && prs.length >= maxPrs) {
      return `čeká se na kontrolu ${prs.length} otevřených PR (limit ${maxPrs})`;
    }
  } catch {
    /* když se stav PR nepodaří zjistit, radši pokračujeme */
  }

  // Soubory uzamčené běžícími úlohami — dvě granule se nesmí dotýkat stejného souboru.
  const runningRows = await env.DB.prepare(
    "SELECT payload FROM tasks WHERE status='running' AND target='cloud'",
  ).all<{ payload: string | null }>();
  const locked = new Set<string>();
  for (const r of runningRows.results || []) {
    try { for (const f of (JSON.parse(r.payload || "{}").owns || [])) locked.add(f); } catch { /* */ }
  }

  // Připravené granule: ne-dispatchnuté, všechny depends_on hotové, owns volné.
  const ready = items.filter((i) =>
    !dispatched.has(i.id)
    && (i.depends_on || []).every((d) => done.has(d))
    && !(i.owns || []).some((f) => locked.has(f)),
  );
  if (!ready.length) return "roadmapa je hotová (nebo čeká na závislosti)";

  let created = 0;
  for (const g of ready) {
    const res = await env.DB.prepare(
      "INSERT INTO tasks (title, kind, target, prompt, payload) VALUES (?, ?, 'cloud', ?, ?)",
    ).bind(g.title, g.kind || "code", g.prompt,
           JSON.stringify({ owns: g.owns || [], grain: g.id })).run();
    await env.DB.prepare("INSERT INTO roadmap (item_id, task_id) VALUES (?, ?)")
      .bind(g.id, res.meta.last_row_id).run();
    created++;
  }

  await notify(env, "Forge: z roadmapy",
    `založeno ${created} granulí: ${ready.map((g) => g.id).join(", ")}`, "clipboard");
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

  // 0) nejdřív si vyzvedni výsledky běžících cloudových úloh z GitHubu
  const polled = await pollRuns(env).catch((e) => `polling selhal: ${String(e)}`);

  // 1) zaseknuté úlohy (runner umřel, Actions zrušily job, worker se odpojil)
  const stale = await env.DB.prepare(
    `UPDATE runs SET status='timeout', finished_at=datetime('now'),
       summary='prekrocen casovy limit'
     WHERE status='running' AND started_at < datetime('now', ?)`,
  ).bind(`-${staleMin} minutes`).run();
  if (stale.meta.changes) {
    // úkol se vrací do fronty; po třech pokusech už ne (řeší /report i claim)
    await env.DB.prepare(
      `UPDATE tasks SET status='ready', updated_at=datetime('now')
        WHERE status='running' AND attempts < 3
          AND id IN (SELECT task_id FROM runs WHERE status='timeout')`,
    ).run().catch((e) => console.log("requeue po timeoutu selhal:", String(e)));
    await env.DB.prepare(
      `UPDATE tasks SET status='failed', updated_at=datetime('now')
        WHERE status='running'
          AND id IN (SELECT task_id FROM runs WHERE status='timeout')`,
    ).run().catch(() => undefined);
  }

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
      try { return !(JSON.parse(t.payload || "{}").owns || []).some((f: string) => locked.has(f)); }
      catch { return true; }
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
      const w = await env.DB.prepare(
        `SELECT name, kinds, last_seen,
                CAST((julianday('now') - julianday(last_seen)) * 1440 AS INTEGER) AS minutes_ago
           FROM workers ORDER BY last_seen DESC LIMIT 10`,
      ).all();
      return json({ ok: true, time: new Date().toISOString(), ready: t?.n ?? 0,
                    running: r?.n ?? 0, workers: w.results });
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
    if ((path === "/queue" || path === "/status" || path === "/workers")
        && !secretOk(request, env)) {
      return json({ error: "bad secret" }, 401);
    }

    if (path === "/queue") {
      const tasks = await env.DB.prepare(
        "SELECT id, title, kind, target, status, attempts, created_at FROM tasks ORDER BY id DESC LIMIT 50",
      ).all();
      return json({ tasks: tasks.results });
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
      } else {
        const t = await env.DB.prepare("SELECT attempts FROM tasks WHERE id=?")
          .bind(run.task_id).first<{ attempts: number }>();
        const nextStatus = (t?.attempts ?? 0) >= 3 ? "failed" : "ready";
        await env.DB.prepare("UPDATE tasks SET status=?, updated_at=datetime('now') WHERE id=?")
          .bind(nextStatus, run.task_id).run();
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
                  "/heartbeat", "/claim", "/task", "/report"],
    });
  },
};

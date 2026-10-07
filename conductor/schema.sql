-- Schéma stavu orchestra (Cloudflare D1).
-- Aplikace:  npx wrangler d1 execute forge-conductor --remote --file=./schema.sql
--
-- Dvě cesty, kterými se úkol dostane ke zpracování:
--   target='cloud' → conductor spustí GitHub Actions (workflow_dispatch)
--   target='lan'   → úkol si vyzvedne pull-worker (telefon, případně PC) přes POST /claim

CREATE TABLE IF NOT EXISTS tasks (
  id          INTEGER PRIMARY KEY AUTOINCREMENT,
  title       TEXT NOT NULL,
  kind        TEXT NOT NULL DEFAULT 'code',    -- code | test | build | assets | research | shell
  target      TEXT NOT NULL DEFAULT 'cloud',   -- cloud = GitHub Actions, lan = pull-worker
  prompt      TEXT NOT NULL,                   -- zadání pro agenta
  payload     TEXT,                            -- volitelná JSON data (např. seznam kroků)
  status      TEXT NOT NULL DEFAULT 'ready',   -- ready | running | done | failed | blocked
  attempts    INTEGER NOT NULL DEFAULT 0,
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_tasks_status ON tasks (status, target, id);

CREATE TABLE IF NOT EXISTS runs (
  id              INTEGER PRIMARY KEY AUTOINCREMENT,
  task_id         INTEGER NOT NULL REFERENCES tasks (id),
  run_key         TEXT NOT NULL UNIQUE,        -- UUID, které dostane vykonavatel
  workflow        TEXT NOT NULL,               -- název workflow, nebo 'worker:<jmeno>'
  worker          TEXT,                        -- který uzel to vyzvedl (u pull-workerů)
  status          TEXT NOT NULL DEFAULT 'running',
  started_at      TEXT NOT NULL DEFAULT (datetime('now')),
  finished_at     TEXT,
  summary         TEXT,
  pr_url          TEXT,
  log_tail        TEXT,
  artifacts       TEXT                         -- JSON se seznamem výstupů (u domácích uzlů)
);

CREATE INDEX IF NOT EXISTS idx_runs_status ON runs (status);
CREATE INDEX IF NOT EXISTS idx_runs_task   ON runs (task_id, id DESC);

-- Domácí uzly (telefon, PC), které se hlásí conductorovi.
-- Slouží k tomu, aby bylo v /health vidět, že uzel žije, a s jakými schopnostmi.
CREATE TABLE IF NOT EXISTS workers (
  name        TEXT PRIMARY KEY,
  kinds       TEXT NOT NULL DEFAULT '',        -- čárkou oddělené druhy úkolů, které umí
  info        TEXT,                            -- JSON: verze nástrojů, platforma…
  first_seen  TEXT NOT NULL DEFAULT (datetime('now')),
  last_seen   TEXT NOT NULL DEFAULT (datetime('now')),
  jobs_done   INTEGER NOT NULL DEFAULT 0,
  jobs_failed INTEGER NOT NULL DEFAULT 0
);

-- Co už orchestr vzal z roadmapy (.forge/roadmap.json v repu).
-- Díky tomu umí sám pokračovat v práci, i když mu nikdo nezadá úkol –
-- a zároveň se každá položka udělá jen jednou.
-- item_id je ve tvaru "{game_id}/{grain_id}", aby se granule dvou her nesrazily.
CREATE TABLE IF NOT EXISTS roadmap (
  item_id     TEXT PRIMARY KEY,
  task_id     INTEGER,
  status      TEXT NOT NULL DEFAULT 'queued',  -- queued | done | failed
  created_at  TEXT NOT NULL DEFAULT (datetime('now')),
  updated_at  TEXT NOT NULL DEFAULT (datetime('now')),  -- poslední změna řádku
  -- KDY NAPOSLEDY SELHALA (B1, 2. 10. 2026). Do té doby se cooldown ptal na
  -- `updated_at`, což je ale i čas VZNIKU řádku — nová granule proto vypadala
  -- jako „právě selhala" a RETRY_HOURS se na ni vztáhl (vada S12). NULL =
  -- ještě neselhala.
  naposledy_selhalo TEXT
  -- KDY SE WATCHDOG OZVVAL (B3a, 6. 10. 2026). NULL = ještě ne. Drží se na
  -- řádku GRANULE, protože retry zakládá nový ÚKOL — v payloadu úkolu by se
  -- značka ztratila a notifikace by chodila při každém tiku.
  eskalovano TEXT
);

-- Migrace starých tabulek: roadmap.updated_at přibyl kvůli cooldownu
-- opakovaných pokusů selhaných granulí (RETRY_HOURS).
-- ALTER TABLE roadmap ADD COLUMN updated_at TEXT NOT NULL DEFAULT (datetime('now'));
-- B1 (2. 10. 2026): cooldown se ptá na `naposledy_selhalo`, ne na `updated_at`.
-- ALTER TABLE roadmap ADD COLUMN naposledy_selhalo TEXT;
-- B3a (6. 10. 2026): značka watchdogu na řádku granule.
-- ALTER TABLE roadmap ADD COLUMN eskalovano TEXT;

-- Registr her, na kterých orchestr pracuje. Když je prázdný, orchestr jede na
-- jednom repu (GITHUB_REPO), přesně jako dřív – zpětná kompatibilita.
-- Herní dokument (DESIGN.md + roadmap.json) se do orchestra přihlásí přes
-- POST /game; pak si conductor roadmapu najde sám a začne na hře pracovat.
CREATE TABLE IF NOT EXISTS games (
  game_id      TEXT PRIMARY KEY,               -- např. "uo-shadows"
  repo         TEXT NOT NULL,                  -- "vlastnik/repo"
  roadmap_file TEXT NOT NULL DEFAULT '.forge/roadmap.json',
  active       INTEGER NOT NULL DEFAULT 1,
  created_at   TEXT NOT NULL DEFAULT (datetime('now'))
);

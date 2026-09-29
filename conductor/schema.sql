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
CREATE TABLE IF NOT EXISTS roadmap (
  item_id     TEXT PRIMARY KEY,
  task_id     INTEGER,
  status      TEXT NOT NULL DEFAULT 'queued',  -- queued | done | failed
  created_at  TEXT NOT NULL DEFAULT (datetime('now'))
);

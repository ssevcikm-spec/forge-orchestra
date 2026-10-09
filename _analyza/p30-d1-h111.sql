-- p30-d1-h111.sql — MĚŘENÍ D1 pro rozhodnutí nálezu H111 (proč dispatch stojí).
-- Jen SELECT: nic se nemění.
-- Spuštění: node conductor\node_modules\wrangler\bin\wrangler.js d1 execute forge-conductor --remote --file=_analyza/p30-d1-h111.sql

-- 1) KOLIK BĚHŮ SPÁLILA KTERÁ GRANULE (od založení řádku v cache) — test stropu 8
SELECT (json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain')) AS item_id,
       COUNT(r.id) AS runs
  FROM runs r
  JOIN tasks t ON t.id = r.task_id
  JOIN roadmap rm ON rm.item_id = (json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain'))
 WHERE r.started_at IS NOT NULL AND r.started_at >= rm.created_at
 GROUP BY item_id
 ORDER BY runs DESC;

-- 2) ÚLOHY, KTERÉ NEJSOU V TERMINÁLNÍM STAVU (zámek = 'running')
SELECT id, status, attempts, substr(title, 1, 40) AS title, updated_at
  FROM tasks WHERE status IN ('running', 'ready') ORDER BY status, id;

-- 3) POČTY ÚLOH PODLE STAVU
SELECT status, COUNT(*) AS pocet FROM tasks GROUP BY status ORDER BY pocet DESC;

-- 4) BĚHY ÚLOHY #239 (osiřelá granule entity.enemy)
SELECT r.id, r.task_id, r.status, r.started_at, r.finished_at, substr(r.summary, 1, 60) AS summary
  FROM runs r WHERE r.task_id = 239 ORDER BY r.id DESC LIMIT 15;

-- 5) POSLEDNÍCH 20 BĚHŮ VŮBEC (kdy se přestalo/začalo dispatchovat)
SELECT r.id, r.task_id, r.status, r.started_at, r.finished_at
  FROM runs r ORDER BY r.id DESC LIMIT 20;

-- 6) ŘÁDKY CACHE ROADMAPY (kolik a jaké)
SELECT item_id, task_id, status, created_at, updated_at FROM roadmap ORDER BY item_id;

-- 7) H114: má `entity.move.smooth` úlohu nebo řádek?
SELECT 'task' AS odkud, id AS cislo, status, substr(title, 1, 50) AS text FROM tasks
 WHERE title LIKE '%smooth%' OR title LIKE '%pohyb%'
UNION ALL
SELECT 'roadmap' AS odkud, task_id AS cislo, status, item_id AS text FROM roadmap
 WHERE item_id LIKE '%move%';

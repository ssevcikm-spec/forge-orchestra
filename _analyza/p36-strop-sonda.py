# -*- coding: utf-8 -*-
r"""P36 — SONDA D1 ke STROPU GRANULE (READ-ONLY).

PROČ VLASTNÍ SONDA: zadání P36 §2.1 (Úkol A) žádá VLASTNÍ měřidlo
(`p36-*`) a §2.2 (Úkol B) je hlavní stopa „práce se nevydává kvůli
STROPU GRANULE 8/8“. Tahle sonda odpovídá na jedinou otázku:

    KTERÉ BĚHY ty tři granule spálily — a jak skončily?

Používá TYTÉŽ SQL jako živý conductor (`SQL_GRANULE_RUNS` v
`conductor/src/index.ts`), aby se číslo z tiku dalo reprodukovat
nezávisle; liší-li se, je to nález.

Příkaz jde přes `wrangler d1 execute --remote --json --command '<SQL>'`
— POUZE SELECT (žádný zápis do D1).

Použití:  python _analyza\p36-strop-sonda.py
Exit 0 = změřeno a zapsáno · 2 = měření NEPROBĚHLO (nesmí se číst jako nula).
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
WRANGLER = WS / "conductor" / "node_modules" / "wrangler" / "bin" / "wrangler.js"
DB = "forge-conductor"
DOKLAD = WS / "_analyza" / "p36-strop-vystup.txt"

GRAIN_KEY_SQL = (
    "(json_extract(t.payload, '$.game') || '/' || json_extract(t.payload, '$.grain'))"
)

STUCK = ("uo-shadows/engine.input", "uo-shadows/world.bodies", "uo-shadows/engine.shell")

DOTAZY = [
    ("granule_runs", f"""
        SELECT {GRAIN_KEY_SQL} AS item_id, COUNT(r.id) AS runs
          FROM runs r
          JOIN tasks t ON t.id = r.task_id
          JOIN roadmap rm ON rm.item_id = {GRAIN_KEY_SQL}
         WHERE r.started_at IS NOT NULL
           AND r.started_at >= rm.created_at
         GROUP BY item_id
         ORDER BY runs DESC"""),
    ("tasks_otevrene", """
        SELECT id, status, attempts, target, kind, title,
               substr(COALESCE(payload,''),1,200) AS payload
          FROM tasks
         WHERE status IN ('ready','running','failed','blocked')
         ORDER BY status, id"""),
    ("roadmap", """
        SELECT item_id, task_id, status, created_at, updated_at,
               naposledy_selhalo, eskalovano
          FROM roadmap ORDER BY item_id"""),
    ("behy_zaseknute", f"""
        SELECT r.id, r.task_id, r.status, r.started_at, r.finished_at,
               substr(COALESCE(r.summary,''),1,300) AS summary,
               substr(COALESCE(r.log_tail,''),1,600) AS log_tail,
               COALESCE(r.pr_url,'') AS pr_url, r.workflow
          FROM runs r JOIN tasks t ON t.id = r.task_id
         WHERE {GRAIN_KEY_SQL} IN ('{STUCK[0]}','{STUCK[1]}','{STUCK[2]}')
         ORDER BY r.task_id, r.id"""),
    ("behy_status", """
        SELECT status, COUNT(*) AS n, MIN(started_at) AS od, MAX(started_at) AS do
          FROM runs GROUP BY status ORDER BY n DESC"""),
    ("behy_od_9", """
        SELECT date(started_at) AS den, status, COUNT(*) AS n
          FROM runs WHERE started_at >= '2026-10-08'
         GROUP BY den, status ORDER BY den, status"""),
]


def spust_dotaz(sql):
    r = subprocess.run(
        ["node", str(WRANGLER), "d1", "execute", DB, "--remote", "--json",
         "--command", sql],
        cwd=str(WS / "conductor"), capture_output=True, timeout=300,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    m = re.search(r"\[\s*\{.*\}\s*\]", out, re.S)
    if not m:
        return None, "exit=%d, v výstupu není JSON: %s" % (r.returncode, out[:300])
    data = json.loads(m.group(0))
    if not data or not data[0].get("success"):
        return None, "wrangler hlásí success=false: %s" % json.dumps(data)[:300]
    return (data[0].get("results") or []), None


def main():
    if not WRANGLER.is_file():
        print("CHYBA: wrangler nenalezen (%s)" % WRANGLER)
        return 2
    doklad = {
        "co": "P36 — proč se práce nevydává: běhy spálené na granulích nad stropem",
        "mereno": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "db": DB,
        "dotazy": {},
        "chyby": {},
    }
    chyby = 0
    for nazev, sql in DOTAZY:
        radky, chyba = spust_dotaz(sql)
        if chyba:
            doklad["chyby"][nazev] = chyba
            chyby += 1
            print("CHYBA dotaz %s: %s" % (nazev, chyba))
            continue
        doklad["dotazy"][nazev] = radky
        print("%-16s %d řádků" % (nazev, len(radky)))

    if chyby:
        print("!! %d z %d dotazů NEPROBĚHLO — měření je NEÚPLNÉ (není to nula)"
              % (chyby, len(DOTAZY)))

    # ── lidské shrnutí toho podstatného ─────────────────────────────────────
    print("\n== BĚHY NA ZASEKNUTÝCH GRANULÍCH ==")
    for r in doklad["dotazy"].get("behy_zaseknute", []):
        print("  run #%-5s task #%-4s %-11s %s -> %s | %s"
              % (r["id"], r["task_id"], r["status"], r["started_at"],
                 r["finished_at"] or "-", (r["summary"] or "")[:90]))
    print("\n== POČET BĚHŮ NA GRANULI (SQL z conductora) ==")
    for r in doklad["dotazy"].get("granule_runs", []):
        print("  %-32s %s" % (r["item_id"], r["runs"]))

    DOKLAD.write_bytes(
        (json.dumps(doklad, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    print("\ndoklad: %s (%d B)" % (DOKLAD.name, DOKLAD.stat().st_size))
    return 2 if chyby else 0


if __name__ == "__main__":
    sys.exit(main())

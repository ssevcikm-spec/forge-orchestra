# -*- coding: utf-8 -*-
"""Sonda: proč test-cooldown po B1 tvrdí „vydá se=True" u scénáře v cooldownu?

Postup je TOTÉŽ jako v testu (`vytahni_guard_sql` + `priprav` + `vloz` + `vydane`),
jen s výpisem mezivýsledků. Nic se nemění.
"""

import pathlib
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KONDUKTOR = pathlib.Path(__file__).resolve().parent.parent / "orchestra" / "conductor" / "src" / "index.ts"
RETRY_H = 3

zdroj = KONDUKTOR.read_text(encoding="utf-8")
i = zdroj.find("SELECT * FROM tasks WHERE status='ready' AND target='cloud'")
zacatek = zdroj.rindex("`", 0, i) + 1
konec = zdroj.index("`", i)
sql = re.sub(r"\$\{[^}]*\}", "?", zdroj[zacatek:konec]).strip()
print("=== SQL, které test opravdu používá ===")
print(sql)
print()

db = sqlite3.connect(":memory:")
db.executescript(
    """
    CREATE TABLE tasks (id INTEGER PRIMARY KEY, status TEXT, target TEXT, payload TEXT);
    CREATE TABLE roadmap (
        item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT,
        updated_at TEXT, naposledy_selhalo TEXT
    );
    """
)

# scénář 2: selhalo před 10 min
db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (1, "ready", "cloud", "{}"))
db.execute(
    "INSERT INTO roadmap (item_id, task_id, status, updated_at, naposledy_selhalo)"
    " VALUES (?,?,?,datetime('now', ?),?)",
    ("hra/g1", 1, "queued", "-60 minutes", "-10 minutes"),
)
db.commit()

print("=== řádek v roadmapě ===")
for radek in db.execute("SELECT item_id, task_id, status, updated_at, naposledy_selhalo FROM roadmap"):
    print("   ", radek)
print("    datetime('now')      =", db.execute("SELECT datetime('now')").fetchone()[0])
print("    datetime('now','-3 hours') =", db.execute("SELECT datetime('now','-3 hours')").fetchone()[0])
print("    podminka v NOT EXISTS =",
      db.execute("SELECT naposledy_selhalo > datetime('now', ?) FROM roadmap", (f"-{RETRY_H} hours",)).fetchone()[0])
print()
print("=== vydané úkoly ===")
vyd = [r[0] for r in db.execute(sql, (f"-{RETRY_H} hours",)).fetchall()]
print("   ", vyd)
print("    1 in vydané →", 1 in vyd)
print()
print("=== a co kdyby test bindoval '-3 hours' bez minus? ===")
print("    '-3 hours' =", f"-{RETRY_H} hours")

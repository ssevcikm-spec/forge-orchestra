"""Ověří SQL logiku cooldownu z conductora na vzorové databázi.

Proč: oprava cooldownu se nasazuje pushnutím a testuje se na živém provozu, kde
každý neúspěšný pokus stojí kvótu free modelu. Tenhle test ověří obě varianty
podmínky offline, bez jediného volání LLM:

  A) STARÁ (děravá):  ... AND rm.status='failed' AND rm.updated_at > now-retryH
  B) NOVÁ             ... AND rm.updated_at > now-retryH
"""

import sqlite3

RETRY_H = 3


def priprav():
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, status TEXT, target TEXT, payload TEXT);
        CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT, updated_at TEXT);
        """
    )
    return db


def vloz(db, task_id, stav_roadmapy, minuty_zpet):
    """Úkol je 'ready'; řádek roadmapy se změnil před `minuty_zpet` minutami."""
    db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (task_id, "ready", "cloud", "{}"))
    db.execute(
        "INSERT INTO roadmap VALUES (?,?,?,datetime('now', ?))",
        (f"hra/g{task_id}", task_id, stav_roadmapy, f"-{minuty_zpet} minutes"),
    )
    db.commit()


def vydane(db, varianta):
    if varianta == "stara":
        podminka = "rm.status = 'failed' AND rm.updated_at > datetime('now', ?)"
    else:
        podminka = "rm.updated_at > datetime('now', ?)"
    sql = f"""
        SELECT id FROM tasks WHERE status='ready' AND target='cloud'
          AND NOT EXISTS (SELECT 1 FROM roadmap rm
                           WHERE rm.task_id = tasks.id AND {podminka})
        ORDER BY id"""
    return [r[0] for r in db.execute(sql, (f"-{RETRY_H} hours",)).fetchall()]


# Scénáře: (popis, stav řádku v roadmapě, minuty od poslední změny, má se vydat?)
scenare = [
    ("selhalo před 2 min (retriable -> 'queued')", "queued", 2, False),
    ("selhalo před 2 min (poslední pokus -> 'failed')", "failed", 2, False),
    ("selhalo před 10 min", "queued", 10, False),
    ("selhalo před 4 h (cooldown vypršel)", "queued", 240, True),
    ("selhalo před 4 h (failed)", "failed", 240, True),
    ("řádek je 'done' (nemá se vydat, ale úkol není ready)", "queued", 0, False),
]

print(f"{'scénář':<48} {'stav':<8} {'min':>5} {'čekáno':>7} {'STARÁ':>7} {'NOVÁ':>7}")
print("-" * 92)
for popis, stav, minuty, ma_se_vydat in scenare:
    db = priprav()
    vloz(db, 1, stav, minuty)
    stara = 1 in vydane(db, "stara")
    nova = 1 in vydane(db, "nova")
    ok_stara = "OK" if stara == ma_se_vydat else "CHYBA"
    ok_nova = "OK" if nova == ma_se_vydat else "CHYBA"
    print(f"{popis:<48} {stav:<8} {minuty:>5} {str(ma_se_vydat):>7} "
          f"{str(stara):>4} {ok_stara:<2} {str(nova):>4} {ok_nova:<2}")

print()
print("Legenda: True = úkol se VYDÁ (dispatch), False = zůstane blokovaný.")
print("Očekávání: selhání mladší než RETRY_HOURS se nesmí vydat, po vypršení ano.")

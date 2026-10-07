# ⚠ ZASTARALÉ OD 6. 10. 2026 — TENHLE TEST MĚŘÍ ODSTRANĚNOU LOGIKU.
#
# Testuje watchdog, který počítal běhy JEDNOHO úkolu (`r.task_id = t.id`) a měl
# `PRAH = 8` **natvrdo**. Naměřeno 6. 10. 2026 na živé službě: takový watchdog se
# **nikdy nemohl spustit** (prah 8 > strop `MAX_ATTEMPTS` 5) — testoval tedy stav,
# který conductor neumí vyrobit (`ANALYZA-ARCHITEKTURY-ORCHESTRA.md` ř. 500).
#
# Logiku nahradil watchdog na GRANULI (**B3a**, `conductor/src/index.ts`) a ten
# měří `tools/test-watchdog-granule.py` (**17 kontrol**; vytahuje prah, SQL
# i rozhodnutí **ze zdrojáku**, místo aby si je opisoval) s mutačním důkazem
# `_analyza/b3-mutace.py` (**11 kontrol**, 5 vrat → 5× spadne).
#
# Soubor zůstává jen proto, že na něj odkazuje 20+ dokumentů a brána
# `hl-rizika-jazyka.py`; **smazat/přepsat ho patří do C2** (plán fáze C).
"""Ověří logiku eskalace (watchdog na spálené pokusy) bez sítě a bez LLM.

Proč offline test: eskalace se v provozu nedá vyzkoušet bez toho, aby granule
opravdu spálila 8 pokusů (~1 den běhů a kvóty). Přitom jde o to, aby notifikace
nepřišla ani příliš brzo (každý přechodný výpad), ani opakovaně při každém tiku
(to by z Telegramu udělalo spam).

Test simuluje to, co dělá `escalateStuckTasks` v conductoru:
  - spočítá RUNY úkolu (skutečně spálené pokusy),
  - když je počet >= prah a úkol ještě není označený, pošle notifikaci
    a označí `payload.eskalovano = true`,
  - pod prahem nedělá nic.
"""

import json
import sqlite3
import sys

PRAH = 8


def priprav():
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, title TEXT, status TEXT, payload TEXT);
        CREATE TABLE runs (id INTEGER PRIMARY KEY, task_id INTEGER, status TEXT);
        """
    )
    return db


def pridej_ukol(db, task_id, stav, runu, eskalovano=False):
    payload = {"grain": f"g{task_id}", "owns": [f"scripts/g{task_id}.gd"]}
    if eskalovano:
        payload["eskalovano"] = True
    db.execute("INSERT INTO tasks VALUES (?,?,?,?)",
               (task_id, f"Granule {task_id}", stav, json.dumps(payload)))
    for i in range(runu):
        db.execute("INSERT INTO runs (task_id, status) VALUES (?,?)", (task_id, "failure"))
    db.commit()


def watchdog(db):
    """Zjednodušená kopie logiky z conductora; vrací (notified, značky)."""
    rows = db.execute(
        """SELECT t.id, t.title, t.payload,
                  (SELECT COUNT(*) FROM runs r WHERE r.task_id = t.id) AS pokusu
             FROM tasks t
            WHERE t.status IN ('ready','failed')
            ORDER BY t.id DESC LIMIT 50"""
    ).fetchall()

    notified = []
    for tid, title, payload, pokusu in rows:
        if (pokusu or 0) < PRAH:
            continue
        p = json.loads(payload or "{}")
        if p.get("eskalovano") is True:
            continue
        notified.append((tid, pokusu))
        p["eskalovano"] = True
        p["eskalovano_pokusu"] = pokusu
        db.execute("UPDATE tasks SET payload=? WHERE id=?", (json.dumps(p), tid))
    db.commit()
    return notified


scenare = [
    # (popis, stav úkolu, runů, už označeno, očekává se notifikace?)
    ("3 pokusy – přechodný výpadek, nehlásit", "ready", 3, False, False),
    ("7 pokusů – ještě pod prahem", "ready", 7, False, False),
    ("přesně 8 pokusů – prah dosažen", "failed", 8, False, True),
    ("12 pokusů – dávno přes prah", "failed", 12, False, True),
    ("8 pokusů, ale už ohlášeno – neopakovat", "failed", 8, True, False),
    ("20 pokusů, už ohlášeno – neopakovat", "ready", 20, True, False),
    ("hotový úkol (done) se nehlásí", "done", 0, False, False),
]

print(f"{'scénář':<44} {'stav':<8} {'runů':>5} {'označeno':>9} {'čekáno':>7} {'výsledek':>9}")
print("-" * 92)
vse_ok = True
for popis, stav, runu, ozn, cekano in scenare:
    db = priprav()
    pridej_ukol(db, 1, stav, runu, ozn)
    vysledek = len(watchdog(db)) > 0
    ok = vysledek == cekano
    vse_ok = vse_ok and ok
    print(f"{popis:<44} {stav:<8} {runu:>5} {str(ozn):>9} {str(cekano):>7} "
          f"{('OK' if ok else 'CHYBA'):>9}")

# Druhý tik nesmí poslat totéž znovu (jinak by Telegram spammoval každou minutu).
db = priprav()
pridej_ukol(db, 1, "failed", 9)
prvni = watchdog(db)
druhy = watchdog(db)
treti = watchdog(db)
print()
print(f"opakované tiky: 1. tik ohlásil {len(prvni)}x, 2. tik {len(druhy)}x, 3. tik {len(treti)}x")
if len(prvni) == 1 and len(druhy) == 0 and len(treti) == 0:
    print("  OK   notifikace se neopakuje (označeno payload.eskalovano)")
else:
    print("  CHYBA notifikace by se opakovala – to je spam")
    vse_ok = False

# Více granul naráz: ohlásí se každá jednou.
db = priprav()
for i in range(1, 5):
    pridej_ukol(db, i, "failed", 8 + i)
hromadne = watchdog(db)
print()
print(f"čtyři problémové granule naráz -> ohlášeno {len(hromadne)}")
if len(hromadne) == 4:
    print("  OK   každá granule se ohlásí právě jednou")
else:
    print("  CHYBA očekávány 4 notifikace")
    vse_ok = False

print()
print("VŠE OK" if vse_ok else "NALEZENY CHYBY")
sys.exit(0 if vse_ok else 1)

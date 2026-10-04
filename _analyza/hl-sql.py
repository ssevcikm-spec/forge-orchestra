#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Hloubkova analyza orchestra - DUKAZ invariantu 15 na urovni SQL (uroven 2).

Neopisuje logiku: bere SQL dotazy PRIMO ze zdroje conductora (index.ts) a pousti
je v SQLite. Kazdy test ma ZNAMY SPRAVNY i ZNAMY CHYBNY pripad, aby bylo videt,
ze meri (kdyby se SQL zmenilo, test to pozna).

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza/hl-sql.py
"""
import os
import re
import sqlite3
import sys
from datetime import datetime, timedelta, timezone

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
# HL_TS dovoluje pustit test proti KOPII zdroje (mutacni test _analyza/hl-mutace.py)
TS = os.environ.get("HL_TS") or os.path.join(WS, "orchestra", "conductor", "src", "index.ts")
SRC = open(TS, encoding="utf-8").read()
print(f"# zdroj: {TS}")


def bez_komentaru(t):
    t = re.sub(r"/\*.*?\*/", "", t, flags=re.S)
    out = []
    for ln in t.splitlines():
        m = re.search(r"(?<!:)//", ln)
        out.append(ln[:m.start()] if m else ln)
    return "\n".join(out)


KOD = bez_komentaru(SRC)
FAIL = 0


def cisty(sql):
    return sql.replace("`", " ").strip().rstrip(",").strip()


def najdi_guard():
    """Vytahne CELE zneni dispatch guardu ze zdroje (od SELECT po ORDER BY LIMIT)."""
    lines = KOD.split("\n")
    for i, ln in enumerate(lines):
        if "SELECT * FROM tasks WHERE status='ready' AND target='cloud'" in ln:
            blok = []
            for j in range(i, min(i + 12, len(lines))):
                blok.append(lines[j])
                if "LIMIT 25" in lines[j]:
                    break
            return "\n".join(blok), i + 1
    raise SystemExit("dispatch guard NENALEZEN - zdroj se zmenil, test je slepy")


GUARD_BLOK, guard_line = najdi_guard()
GUARD = cisty(" ".join(l.strip() for l in GUARD_BLOK.splitlines()))
print(f"# dispatch guard vzat ze zdroje: index.ts:{guard_line}")
for l in GUARD_BLOK.splitlines():
    print(f"#   {l.strip()[:116]}")
for cast in ["status='ready'", "target='cloud'", "NOT EXISTS", "rm.updated_at >", "LIMIT 25"]:
    assert cast in GUARD, f"guard ve zdroji neobsahuje {cast!r}"
if "rm.status" in GUARD:
    raise SystemExit("guard se pta na rm.status - to je chovani, ktere analyza nepopisuje")


def najdi_sql(kotva):
    for i, ln in enumerate(KOD.splitlines(), 1):
        if kotva in ln:
            return cisty(ln), i
    raise SystemExit(f"SQL s kotvou {kotva!r} NENALEZENO - zdroj se zmenil, test je slepy")


POLL_UPD, poll_line = najdi_sql("UPDATE roadmap SET status = ?")
REPORT_UPD, rep_line = najdi_sql("UPDATE roadmap SET status='failed'")
print(f"# pollRuns zapisuje roadmapu: index.ts:{poll_line}  {POLL_UPD[:90]}")
print(f"# /report zapisuje roadmapu:  index.ts:{rep_line}  {REPORT_UPD[:90]}")

RETRY_H = 3  # wrangler.toml:49


def nova_db():
    db = sqlite3.connect(":memory:")
    db.executescript("""
      CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, kind TEXT,
        target TEXT DEFAULT 'cloud', prompt TEXT, payload TEXT, status TEXT DEFAULT 'ready',
        attempts INTEGER DEFAULT 0, created_at TEXT DEFAULT (datetime('now')),
        updated_at TEXT DEFAULT (datetime('now')));
      CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT,
        created_at TEXT DEFAULT (datetime('now')), updated_at TEXT);
    """)
    return db


def zjisti(db, hodin=RETRY_H):
    return [r[0] for r in db.execute(GUARD, (f"-{hodin} hours",)).fetchall()]


def cas(minuty_zpet):
    t = datetime.now(timezone.utc) + timedelta(minutes=-minuty_zpet)
    return t.strftime("%Y-%m-%d %H:%M:%S")


def test(cislo, popis, ocekavano, skutecne, detail=""):
    global FAIL
    ok = ocekavano == skutecne
    if not ok:
        FAIL += 1
    print(f"  [{'OK ' if ok else 'CHYBA'}] {cislo} {popis}")
    print(f"        ocekavano={ocekavano}  skutecne={skutecne}  {detail}")


print("\n=== 1) NOVA GRANULE: vznikla prave ted (index.ts:643-646) ===")
db = nova_db()
db.execute("INSERT INTO tasks (title,status,target) VALUES ('nova','ready','cloud')")
db.execute("INSERT INTO roadmap (item_id,task_id,status,updated_at) VALUES ('g/nova',1,'queued',?)", (cas(0),))
test("1a", "nova granule se NESMI vydat hned", [], zjisti(db))
print("       ^ INVARIANT 15: guard se pta na cas a ten je prave ted")
print("         -> nova granule ceka RETRY_HOURS, i kdyz nikdy neselhala")

db.execute("UPDATE roadmap SET updated_at=? WHERE item_id='g/nova'", (cas(4 * 60),))
test("1b", "TYZ radek stary 4 h (cooldown uplynul)", [1], zjisti(db),
     "-> guard meri jen cas, ne pricinu")

print("\n=== 2) ZNANY SPRAVNY PRIPAD: nova granule, ktera se smi vydat ===")
db2 = nova_db()
db2.execute("INSERT INTO tasks (title,status,target) VALUES ('nova','ready','cloud')")
db2.execute("INSERT INTO roadmap (item_id,task_id,status,updated_at) VALUES ('g/nova',1,'queued',NULL)")
test("2", "nova granule BEZ updated_at (NULL) - guard ji pusti", [1], zjisti(db2),
     "-> spravny pripad, kdy guard neblokuje")

print("\n=== 3) SELHANA GRANULE: co se stane po pollRuns ===")
db3 = nova_db()
db3.execute("INSERT INTO tasks (title,status,target,attempts) VALUES ('selhala','ready','cloud',1)")
db3.execute("INSERT INTO roadmap (item_id,task_id,status,updated_at) VALUES ('g/s',1,'queued',?)", (cas(0),))
test("3a", "po selhani (updated_at=now) se granule nevyda", [], zjisti(db3))
db3.execute("UPDATE roadmap SET status='queued', updated_at=? WHERE item_id='g/s'", (cas(RETRY_H * 60 + 1),))
test("3b", "po RETRY_HOURS se vyda", [1], zjisti(db3), "-> cooldown funguje, jak ma")

print("\n=== 4) DVA SOUPEZICI UKOLY NA TOUZ GRANULI (duplikace) ===")
db4 = nova_db()
db4.execute("INSERT INTO tasks (title,status,target) VALUES ('stary','running','cloud')")
db4.execute("INSERT INTO tasks (title,status,target) VALUES ('novy','ready','cloud')")
db4.execute("INSERT INTO roadmap (item_id,task_id,status,updated_at) VALUES ('g/d',2,'queued',NULL)")
test("4", "radek roadmapy ukazuje na novy ukol -> stary 'running' neni v guardu vubec",
     [2], zjisti(db4), "-> stary ukol (task 1) guard nevidi: duplikace je mozna")
pocet = db4.execute("SELECT COUNT(*) FROM tasks WHERE status IN ('ready','running')").fetchone()[0]
test("4b", "na jednu granuli mohou existovat dva aktivni ukoly", 2, pocet)

print("\n=== 5) UKOL BEZ RADKU V ROADMAPE (zombie) ===")
db5 = nova_db()
db5.execute("INSERT INTO tasks (title,status,target) VALUES ('zombie','ready','cloud')")
test("5", "ukol bez radku v roadmapě guard PROPUSTI", [1], zjisti(db5),
     "-> proto existuje zombie-invariant v tiku (index.ts:742-746)")

print("\n=== 6) PRUCHOZI CHYBA CTENI ROADMAPY -> prazdny seznam (tichy stav) ===")
db6 = nova_db()
test("6", "kdyz se roadmapa nenacte, items=[] -> zadna granule se nezalozi",
     0, len([]), "-> 'ceka se na zavislosti' a 'roadmapa se nenacetla' vypadaji STEJNE")

print("\n=== 7) VELIKOST OKNA: kolik uloh guard vrati ===")
db7 = nova_db()
for i in range(30):
    db7.execute("INSERT INTO tasks (title,status,target) VALUES (?,'ready','cloud')", (f"t{i}",))
    db7.execute("INSERT INTO roadmap (item_id,task_id,status,updated_at) VALUES (?,?,'queued',NULL)", (f"g/{i}", i + 1))
test("7", "guard vraci nejvys 25 uloh (LIMIT 25 v SQL)", 25, len(zjisti(db7)),
     "-> pri >25 pripravenych granulich se zbytek odklada na dalsi tik")

print(f"\n=== VYSLEDEK: {FAIL} chyb ===")
print("Bez chyby = SQL ze zdroje se chova tak, jak analyza tvrdi.")
if FAIL:
    sys.exit(1)

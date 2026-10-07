"""Brána pro B2: selhání přes `/report` MUSÍ založit cooldown (vada S13).

PROČ TENHLE TEST EXISTUJE
-------------------------
`/report` posílá workflow z GitHub Actions, když běh selže. Původně zapsal jen
`tasks`, ale `roadmap` NE — takže se selhaná granule vrátila do fronty
**okamžitě** (guard se ptal na `roadmap`) a spálila všechny pokusy za čtvrt
hodiny. Naměřeno 30. 9. 2026: `#128` měl 5 pokusů za 16 minut, `#124/#125/#127`
za čtvrt hodiny. Opravil to krok **B1** (`roadmap.naposledy_selhalo`), ale
**nikdo to neměřil** — `tools/test-cooldown.py` kryje cestu dispatche, ne
zápis z `/report`.

CO SE NEOPISUJE
---------------
Test si **vytáhne ze zdrojáku conductora** obě SQL, o která jde:
  1. zápis z `/report` (opakovatelné selhání: `UPDATE roadmap SET naposledy_selhalo …`),
  2. zápis z `/report` (poslední pokus: `status='failed'` + `naposledy_selhalo`),
  3. **dispatch guard** (`NOT EXISTS (… rm.naposledy_selhalo > datetime('now', ?))`),
a k tomu `RETRY_HOURS` z `wrangler.toml`. Kdyby se SQL v conductoru změnilo,
test použije novou verzi — a když se změní tak, že cooldown přestane platit,
spadne.

CO TVRDÍ (Hotovo znamená plánu: „simulované selhání přes `/report` → granule se
nevydá dřív než za `RETRY_HOURS`"):
  A) po čerstvém selhání přes `/report` guard úkol **NEVYDÁ**,
  B) po uplynutí `RETRY_HOURS` ho **VYDÁ** (cooldown je okno, ne vězení),
  C) totéž platí pro **poslední pokus** (`status='failed'`),
  D) **známý chybný případ:** bez zápisu `naposledy_selhalo` (tj. stav před B1)
     guard úkol vydá **okamžitě** — to je přesně vada S13,
  E) guard nevydá úkol, který není `ready` (běžící úkol se nesmí vydat dvakrát).

Test má assert i nenulový exit kód (bez toho by „zelený" nic neznamenal).
"""

import pathlib
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
CONDUCTOR = WS / "conductor" / "src" / "index.ts"
WRANGLER = WS / "conductor" / "wrangler.toml"

checks = 0
errors = 0


def check(desc: str, actual, expected) -> None:
    global checks, errors
    checks += 1
    if actual == expected:
        print(f"  OK    {desc}")
    else:
        errors += 1
        print(f"  CHYBA {desc}\n        cekano: {expected!r}\n        dáno:   {actual!r}")


def templates(src: str) -> list:
    return re.findall(r"`([^`]*)`", src, flags=re.S)


def pick(src: str, *musts: str) -> str:
    """Najde template literal, který obsahuje VŠECHNY zadané podřetězce."""
    for t in templates(src):
        if all(m in t for m in musts):
            return t
    raise SystemExit(f"CHYBA: ve zdroji není SQL obsahující {musts!r}")


def toml_var(text: str, name: str) -> str:
    m = re.search(rf'^{name}\s*=\s*"([^"]*)"', text, flags=re.M)
    return m.group(1) if m else ""


def prepare():
    db = sqlite3.connect(":memory:")
    db.executescript(
        """
        CREATE TABLE tasks (id INTEGER PRIMARY KEY, status TEXT, target TEXT,
                            attempts INTEGER, updated_at TEXT);
        CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT,
                              created_at TEXT, updated_at TEXT,
                              naposledy_selhalo TEXT);
        """
    )
    db.execute("INSERT INTO roadmap (item_id, task_id, status, created_at, updated_at)"
               " VALUES ('test/hra', 1, 'queued', datetime('now'), datetime('now'))")
    db.execute("INSERT INTO tasks (id, status, target, attempts, updated_at)"
               " VALUES (1, 'ready', 'cloud', 1, datetime('now'))")
    db.commit()
    return db


def vydane(db, guard_sql: str, okno: str) -> list:
    """Kolik úkolů dispatch guard vydá (váže se okno cooldownu jako `-N hours`)."""
    return [r[0] for r in db.execute(guard_sql, (f"-{okno} hours",)).fetchall()]


def main() -> int:
    global checks, errors
    print(f"=== zdroj: {CONDUCTOR.name} + {WRANGLER.name} ===")
    if not CONDUCTOR.is_file():
        print(f"CHYBA: chybí {CONDUCTOR}")
        return 1
    src = CONDUCTOR.read_text(encoding="utf-8")
    wtext = WRANGLER.read_text(encoding="utf-8") if WRANGLER.is_file() else ""

    sql_report = pick(src, "UPDATE roadmap SET naposledy_selhalo")
    sql_report_final = pick(src, "UPDATE roadmap SET status='failed'", "naposledy_selhalo")
    sql_guard = pick(src, "NOT EXISTS", "naposledy_selhalo")
    okno = toml_var(wtext, "RETRY_HOURS")
    print(f"=== RETRY_HOURS z wrangler.toml: {okno!r} h ===")
    if not okno.isdigit() or int(okno) <= 0:
        print(f"CHYBA: RETRY_HOURS není kladné číslo ({okno!r})")
        return 1

    # A) čerstvé selhání přes /report → guard úkol NEVYDÁ
    db = prepare()
    db.execute(sql_report, (1,))
    check("A: po selhání přes /report guard NEVYDÁ úkol", vydane(db, sql_guard, okno), [])

    # D) známý chybný případ: BEZ zápisu naposledy_selhalo (stav před B1) → vydá ho
    db = prepare()
    check("D: bez zápisu naposledy_selhalo (stav před B1) guard VYDÁ úkol OKAMŽITĚ",
          vydane(db, sql_guard, okno), [1])

    # B) cooldown je OKNO: po RETRY_HOURS (a víc) guard úkol vydá
    db = prepare()
    db.execute(sql_report, (1,))
    db.execute("UPDATE roadmap SET naposledy_selhalo = datetime('now', ?)",
               (f"-{int(okno) + 1} hours",))
    db.commit()
    check("B: po uplynutí RETRY_HOURS guard úkol VYDÁ", vydane(db, sql_guard, okno), [1])

    # B2) těsně před vypršením ještě ne
    db = prepare()
    db.execute(sql_report, (1,))
    db.execute("UPDATE roadmap SET naposledy_selhalo = datetime('now', ?)",
               (f"-{max(int(okno) - 1, 0)} hours",))
    db.commit()
    check("B: hodinu PŘED vypršením cooldownu guard ještě NEVYDÁ", vydane(db, sql_guard, okno), [])

    # C) poslední pokus (status='failed') zakládá cooldown taky
    db = prepare()
    db.execute(sql_report_final, (1,))
    stav = db.execute("SELECT status, naposledy_selhalo IS NOT NULL FROM roadmap").fetchone()
    check("C: poslední pokus zapíše status='failed'", stav[0], "failed")
    check("C: poslední pokus zapíše i naposledy_selhalo", stav[1], 1)
    check("C: po posledním pokusu guard NEVYDÁ úkol", vydane(db, sql_guard, okno), [])

    # E) guard nevydá úkol, který není 'ready' (běžící se nesmí vydat dvakrát)
    db = prepare()
    db.execute("UPDATE tasks SET status='running' WHERE id=1")
    db.commit()
    check("E: běžící úkol guard nevydá", vydane(db, sql_guard, okno), [])

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())

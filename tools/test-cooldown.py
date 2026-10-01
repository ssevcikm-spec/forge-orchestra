"""Offline test cooldown-guardu v dispatch smyčce conductora.

PROČ TENHLE TEST EXISTUJE (a co bylo špatně na tom starém)
----------------------------------------------------------
Do 1. 10. 2026 tu byl `test-cooldown.py`, který měl DVĚ vady a obě ho dělaly
bezcenným:

  1. **SQL si OPSAL.** Měl vlastní kopii podmínky (a dokonce i tu STAROU, děravou
     variantu s `rm.status='failed'`) – takže když se SQL v conductoru změnilo,
     test dál měřil svoji kopii a nic nezachytil.
  2. **Neměl `assert` ani `sys.exit`.** Vypisoval `CHYBA` a **skončil `exit 0`**
     – na pohled i v CI zelený. Naměřeno opakovaně.

Navíc **posvěcoval vadu**: scénář „řádek je `done`" podával jako správné
chování to, co je ve skutečnosti důsledek přetíženého `updated_at`.

JAK TO TESTOVÁ (a proč je to důvěryhodné)
-----------------------------------------
`SQL` se **NEOPISUJE** – vytáhne se **ze zdrojáku conductora** (mezi zpětnými
apostrofy u `env.DB.prepare(`) a spustí se v SQLite na vzorové databázi.
Když se SQL v conductoru změní, test použije novou verzi. Vzor je
`test-zamek-owns.py` (`bez_komentaru()`, vytahování ze zdrojáku).

Test má **assert i nenulový exit kód**. Každá kontrola vypíše, co naměřila.

CO DNES CHCE VĚDĚT (a co z toho vychází)
----------------------------------------
Test měří **chování, které je dnes v kódu** – ne to, které by mělo být. Proto
u jednoho scénáře vychází VADA, a to je správný výsledek: je to přesně ta vada,
kterou analýza naměřila jako **S12** a kterou má opravit krok **B1**
(`naposledy_selhalo` místo `updated_at`). **Až se B1 udělá, scénář se otočí**
a test donutí jeho očekávání přepsat – tím je zaručené, že test nezůstane
viset na staré pravdě.

Naměřená vada:
  * **nová granule se 3 h nevydá** (S12) – guard se ptá na `updated_at`, což je
    i čas VZNIKU řádku, takže nová granule vypadá jako „právě selhala".

Co test naopak POTVRDILO jako správné (a dřívější test to měl špatně):
  * řádek `done` **neblokuje** nový `ready` úkol – guard čte jen čas a řádek je
    starý, takže se úkol vydá. (Starý test tenhle případ podával jako „nemá se
    vydat", což bylo posvěcování vady z přetíženého `updated_at`.)
  * `rm.status` se v guardu **nečte** (invariant 13) – ověřeno zvlášť, protože
    první verze opravy filtrovala podle `rm.status='failed'` a tím se guard
    neuplatnil vůbec.
"""

import pathlib
import re
import sqlite3
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KONDUKTOR = pathlib.Path(__file__).resolve().parents[1] / "conductor" / "src" / "index.ts"
RETRY_H = 3

kontrol = 0
chyb = 0


def test(nazev: str, podminka: bool, detail: str = "") -> None:
    """Zaznamená kontrolu. Bez `assert`-like chování by test nic neměřil."""
    global kontrol, chyb
    kontrol += 1
    if not podminka:
        chyb += 1
    stav = "OK  " if podminka else "CHYBA"
    print(f"  {stav} {nazev}" + (f"  — {detail}" if detail else ""))


def vytahni_guard_sql(zdroj: str) -> str:
    """Vytáhne SQL dispatch guardu ze zdrojáku conductora.

    Bere text mezi prvními zpětnými apostrofy za `env.DB.prepare(` a posledními
    před `.bind(`. Nahradí `${...}` za `?` (v SQL to jsou bind parametry).
    """
    i = zdroj.find("SELECT * FROM tasks WHERE status='ready' AND target='cloud'")
    if i < 0:
        raise SystemExit(
            f"CHYBA: dispatch guard v {KONDUKTOR} nenalezen — test je slepý, "
            "nesmí projít. Zkontroluj, že SQL v conductoru začíná stejně."
        )
    # POZOR: otevírací zpětný apostrof je PŘED začátkem SQL (`prepare(`\n `SELECT…`),
    # takže se hledá ZPĚT od `i`, ne dopředu. První verze hledala dopředu a našla
    # apostrof, kterým literál ZAVÍRÁ → vytáhla 2 řádky a test spadl na syntaxi.
    zacatek = zdroj.rindex("`", 0, i) + 1
    konec = zdroj.index("`", i)
    sql = zdroj[zacatek:konec]
    # ${retryH} a podobné -> bind parametr
    sql = re.sub(r"\$\{[^}]*\}", "?", sql)
    return sql.strip()


def priprav() -> sqlite3.Connection:
    """Vzorová databáze se STEJNÝM schématem, jaké guard potřebuje.

    `naposledy_selhalo` je tu proto, aby test fungoval PŘED i PO kroku B1 –
    kdyby sloupec po B1 chyběl, spadl by na `no such column` a vypadalo by to
    jako vada testu, ne jako změna schématu.
    """
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
    return db


def vloz(
    db: sqlite3.Connection,
    task_id: int,
    stav: str,
    vznikl_pred_min: int,
    selhal_pred_min: int | None,
) -> None:
    """Vloží `ready` úkol a řádek roadmapy.

    `vznikl_pred_min` = kolik minut zpět vznikl řádek (guard dnes čte TENHLE čas).
    `selhal_pred_min` = kolik minut zpět naposledy selhal (None = neselhal).
    """
    db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (task_id, "ready", "cloud", "{}"))
    db.execute(
        "INSERT INTO roadmap (item_id, task_id, status, updated_at, naposledy_selhalo)"
        " VALUES (?,?,?,datetime('now', ?),?)",
        (
            f"hra/g{task_id}",
            task_id,
            stav,
            f"-{vznikl_pred_min} minutes",
            None if selhal_pred_min is None else f"-{selhal_pred_min} minutes",
        ),
    )
    db.commit()


def vydane(db: sqlite3.Connection, sql: str) -> list:
    """Spustí SKUTEČNÝ SQL guardu (s parametrem retry hours)."""
    return [r[0] for r in db.execute(sql, (f"-{RETRY_H} hours",)).fetchall()]


# ── 1. Extrakce SQL ze zdrojáku ───────────────────────────────────────────────
print("=== 1. Extrakce guardu ze zdrojáku conductora ===")
zdroj = KONDUKTOR.read_text(encoding="utf-8")
sql = vytahni_guard_sql(zdroj)
radku = len(sql.splitlines())
print(f"  zdroj: {KONDUKTOR}")
print(f"  vytaženo: {radku} řádků SQL")
test("SQL guardu se podařilo vytáhnout ze zdrojáku", radku >= 5, f"{radku} řádků")
test("SQL obsahuje NOT EXISTS (guard blokuje, ne že by jen třídil)", "NOT EXISTS" in sql)
test("SQL čte tabulku roadmap", "roadmap" in sql)
test("SQL má bind parametr pro retry hours", "datetime('now', ?)" in sql)
# Tohle je invariant 13: první verze opravy filtrovala podle `rm.status='failed'`,
# ale pollRuns u opakovatelného selhání zapisuje 'queued' → guard se neuplatnil.
test(
    "SQL NEFILTRUJE podle rm.status (invariant 13 — jinak se cooldown neuplatní)",
    "rm.status" not in sql and "rm. status" not in sql,
)

# ── 2. Chování na scénářích ───────────────────────────────────────────────────
print()
print("=== 2. Chování guardu (skutečný SQL z conductora) ===")
print(f"  {'scénář':<52} {'čekáno':>7} {'naměřeno':>9}  výsledek")
print("  " + "-" * 84)

# (popis, stav řádku, vznikl před min, selhal před min, MÁ se vydat?, je to vada?)
scenare = [
    ("NOVÁ granule (vznikla teď, neselhal)", "queued", 0, None, True, True),
    ("selhalo před 10 min (v cooldownu)", "queued", 60, 10, False, False),
    ("selhalo před 4 h (cooldown vypršel)", "queued", 300, 240, True, False),
    ("řádek 'done' + nový ready úkol", "done", 600, None, True, True),
    ("selhalo před 2 min, 'failed' (poslední pokus)", "failed", 60, 2, False, False),
]

vad = []
for popis, stav, vznikl, selhal, ma_se_vydat, je_vada in scenare:
    db = priprav()
    vloz(db, 1, stav, vznikl, selhal)
    vydal_se = 1 in vydane(db, sql)
    ok = vydal_se == ma_se_vydat
    if not ok and je_vada:
        vad.append((popis, ma_se_vydat, vydal_se))
    print(
        f"  {popis:<52} {str(ma_se_vydat):>7} {str(vydal_se):>9}  "
        f"{'OK' if ok else 'VADA (známá, opraví B1)'}"
    )
    test(f"scénář: {popis}", ok, f"čekáno={ma_se_vydat}, naměřeno={vydal_se}")

# ── 3. Závěr ──────────────────────────────────────────────────────────────────
print()
if vad:
    print("ZNÁMÉ VADY (nejsou to vady testu — měří skutečný kód):")
    for popis, ma, je in vad:
        print(f"  * {popis}: má se vydat={ma}, vydá se={je}")
    print("  → opravuje krok B1 plánu (`naposledy_selhalo` místo `updated_at`).")
    print("    Po B1 test zčervená v OPAČNÉM směru a donutí scénář přepsat.")
print()
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print("NALEZENY CHYBY (viz výše — jde o naměřené vady kódu, ne testu)")
    sys.exit(1)
print("VŠE OK")
sys.exit(0)

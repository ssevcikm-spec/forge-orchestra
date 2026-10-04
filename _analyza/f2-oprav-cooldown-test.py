#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Úkol F — `test-cooldown.py` po kroku B1: fixture + přepsaná očekávání.

DVOJÍ ZMĚNA, obojí vynucená a obojí doložená:

1) VADA FIXTURE (naměřeno 2. 10. 2026, `_analyza\\f2-sonda-cooldown.py`)
   `vloz()` používal
       "INSERT INTO roadmap (…, naposledy_selhalo) VALUES (…, datetime('now', ?),?)"
       ("…", f"-{selhal_pred_min} minutes")
   jenže `?` je tam ARGUMENTEM funkce `datetime()`, ne hodnotou sloupce — SQLite
   tedy uložil **doslovný řetězec** `'-10 minutes'`:
       ('hra/g1', 1, 'queued', '2026-10-02 10:05:32', '-10 minutes')
   Řetězec se v porovnání `> datetime('now','-3 hours')` chová jako 0, takže
   scénář „v cooldownu" VYCHÁZEL jako „má se vydat". Do B1 to nebylo vidět,
   protože se `naposledy_selhalo` vůbec nečetlo.
   → Oprava: čas se počítá v Pythonu a vkládá se jako hodnota.

2) OTOČENÁ OČEKÁVÁNÍ (to je přesně to, co test sám ohlašoval)
   Před B1: „NOVÁ granule" → VADA (guard se ptal na `updated_at`, což je i čas
   vzniku). Po B1: nová granule se VYDÁ a oba scénáře s cooldownem drží.
   Hlavička testu se přepisuje, aby nelhala o tom, co měří.

Použití:
    python _analyza\\f2-oprav-cooldown-test.py
    python _analyza\\f2-oprav-cooldown-test.py --zpet
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
WS = ANALYZA.parent
CIL = WS / "orchestra" / "tools" / "test-cooldown.py"
ZALOHA = ANALYZA / "f2-test-cooldown-puvodni.py"

# ─────────────────────────────────────────────────────────── 1) FIXTURE ──────
FIX_STARY = '''    db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (task_id, "ready", "cloud", "{}"))
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
    db.commit()'''

FIX_NOVY = '''    db.execute("INSERT INTO tasks VALUES (?,?,?,?)", (task_id, "ready", "cloud", "{}"))
    # ⚠ ČASY SE POČÍTAJÍ V PYTHONU, NE PŘES `datetime('now', ?)`.
    # Naměřeno 2. 10. 2026 (`_analyza\\f2-sonda-cooldown.py`): dokud byl `?`
    # ARGUMENTEM funkce `datetime()`, SQLite uložil DOSLOVNÝ ŘETEZEC
    # `'-10 minutes'` místo času — a ten se v porovnání `>` chová jako 0.
    # Scénář „v cooldownu" pak vycházel jako „má se vydat" a vypadalo to jako
    # vada guardu, i když byla vada fixture. Do B1 to nebylo vidět, protože se
    # `naposledy_selhalo` vůbec nečetlo.
    db.execute(
        "INSERT INTO roadmap (item_id, task_id, status, updated_at, naposledy_selhalo)"
        " VALUES (?,?,?,?,?)",
        (
            f"hra/g{task_id}",
            task_id,
            stav,
            _cas_pred(vznikl_pred_min),
            None if selhal_pred_min is None else _cas_pred(selhal_pred_min),
        ),
    )
    db.commit()'''

# ────────────────────────────────────────────── pomocník pro výpočet času ────
POMOC_STARY = '''def vloz(
    db: sqlite3.Connection,'''

POMOC_NOVY = '''def _cas_pred(minut: int) -> str:
    """Čas `minut` zpět ve tvaru, který SQLite porovnává jako datum.

    POZOR: musí to být SKUTEČNÝ čas, ne řetězec `-10 minutes` — přesně na tom
    padala první verze fixture (viz komentář ve `vloz`).
    """
    return datetime.datetime.fromtimestamp(
        time.time() - minut * 60, tz=datetime.timezone.utc
    ).strftime("%Y-%m-%d %H:%M:%S")


def vloz(
    db: sqlite3.Connection,'''

IMPORT_STARY = """import pathlib
import re
import sqlite3
import sys
"""
IMPORT_NOVY = """import datetime
import pathlib
import re
import sqlite3
import sys
import time
"""

# ─────────────────────────────────────────────────────── 2) OČEKÁVÁNÍ ────────
SCEN_STARY = '''# (popis, stav řádku, vznikl před min, selhal před min, MÁ se vydat?, je to vada?)
scenare = [
    ("NOVÁ granule (vznikla teď, neselhal)", "queued", 0, None, True, True),
    ("selhalo před 10 min (v cooldownu)", "queued", 60, 10, False, False),
    ("selhalo před 4 h (cooldown vypršel)", "queued", 300, 240, True, False),
    ("řádek 'done' + nový ready úkol", "done", 600, None, True, True),
    ("selhalo před 2 min, 'failed' (poslední pokus)", "failed", 60, 2, False, False),
]'''

SCEN_NOVY = '''# (popis, stav řádku, vznikl před min, selhal před min, MÁ se vydat?, je to vada?)
#
# PO B1 (2. 10. 2026): guard se ptá na `naposledy_selhalo`, ne na `updated_at`.
# Očekávání se tím OTOČILO u „NOVÉ granule" — dřív se nevydala (vada S12),
# teď se vydat MÁ, protože nikdy neselhala. Zbylé scénáře drží:
#   * selhalo před 10 min  → cooldown 3 h běží → NEVYDÁ se,
#   * selhalo před 4 h     → cooldown vypršel  → VYDÁ se,
#   * řádek 'done'         → nový ready úkol se vydá,
#   * 'failed' před 2 min  → terminální selhání v cooldownu → NEVYDÁ se.
scenare = [
    ("NOVÁ granule (vznikla teď, neselhal)", "queued", 0, None, True, False),
    ("selhalo před 10 min (v cooldownu)", "queued", 60, 10, False, False),
    ("selhalo před 4 h (cooldown vypršel)", "queued", 300, 240, True, False),
    ("řádek 'done' + nový ready úkol", "done", 600, None, True, False),
    ("selhalo před 2 min, 'failed' (poslední pokus)", "failed", 60, 2, False, False),
]'''

# ─────────────────────────────────────────────────────────── 3) HLAVIČKA ────
HLAV_STARY = '''CO DNES CHCE VĚDĚT (a co z toho vychází)
----------------------------------------
Test měří **chování, které je dnes v kódu** – ne to, které by mělo být. Proto
u jednoho scénáře vychází VADA, a to je správný výsledek: je to přesně ta vada,
kterou analýza naměřila jako **S12** a kterou má opravit krok **B1**
(`naposledy_selhalo` místo `updated_at`). **Až se B1 udělá, scénář se otočí**
a test donutí jeho očekávání přepsat – tím je zaručené, že test nezůstane
viset na staré pravdě.

Naměřená vada:
  * **nová granule se 3 h nevydá** (S12) – guard se ptá na `updated_at`, což je
    i čas VZNIKU řádku, takže nová granule vypadá jako „právě selhala".'''

HLAV_NOVY = '''CO DNES CHCE VĚDĚT (a co z toho vychází)
----------------------------------------
**STAV PO B1 (2. 10. 2026): všech 5 scénářů je OK.** Guard se ptá na
`naposledy_selhalo` — čas posledního SELHÁNÍ, ne čas poslední změny řádku.

Historie (aby se neopakovalo): do B1 vycházel scénář „NOVÁ granule" jako VADA.
Guard se ptal na `updated_at`, což je ale i čas VZNIKU řádku, takže nová granule
vypadala jako „právě selhala" a `RETRY_HOURS` se na ni vztáhl (vada **S12**).
Test to hlásil jako naměřenou vadu kódu — a přesně tím si vynutil opravu.

⚠ V TÉTO FIXTURE BYLA DRUHÁ VADA (odhalila se až po B1, naměřeno 2. 10. 2026):
`vloz()` plnil `naposledy_selhalo` přes `datetime('now', ?)`, jenže `?` je tam
argumentem FUNKCE, ne hodnotou sloupce — SQLite uložil doslovný řetězec
`'-10 minutes'`, který se v porovnání `>` chová jako 0. Scénář „v cooldownu" pak
vycházel jako „má se vydat". Do B1 to nebylo vidět, protože se sloupec nečetl.
Časy se proto počítají v Pythonu (`_cas_pred`).'''

ZMENA_STARY = '''    print("  → opravuje krok B1 plánu (`naposledy_selhalo` místo `updated_at`).")
    print("    Po B1 test zčervená v OPAČNÉM směru a donutí scénář přepsat.")'''

ZMENA_NOVY = '''    print("  → tohle je naměřená vada KÓDU, ne testu.")'''

KOMENT_STARY = '''# Tohle je invariant 13: první verze opravy filtrovala podle `rm.status='failed'`,
# ale pollRuns u opakovatelného selhání zapisuje 'queued' → guard se neuplatnil.'''
KOMENT_NOVY = '''# Tohle je invariant 13: první verze opravy filtrovala podle `rm.status='failed'`,
# ale pollRuns u opakovatelného selhání zapisuje 'queued' → guard se neuplatnil.
# PO B1 (2. 10. 2026) guard čte `naposledy_selhalo`; kdyby někdo vrátil
# `updated_at`, scénář „NOVÁ granule" zčervená — je to tedy regresní test na S12.'''


def zmen(text: str, stary: str, novy: str, popis: str) -> str:
    pocet = text.count(stary)
    if pocet != 1:
        print("CHYBA: %s — nalezeno %d×, očekávám 1×" % (popis, pocet))
        sys.exit(2)
    out = text.replace(stary, novy, 1)
    assert out != text, "MUTACE NEPROBĚHLA: %s" % popis
    return out


def main() -> int:
    zpet = "--zpet" in sys.argv
    if zpet:
        if not ZALOHA.is_file():
            print("CHYBA: záloha %s není" % ZALOHA)
            return 2
        CIL.write_bytes(ZALOHA.read_bytes())
        print("vráceno: %s" % CIL)
        return 0

    t = CIL.read_text(encoding="utf-8")
    if "_cas_pred" in t:
        print("OK: oprava už v souboru je")
        return 0

    if not ZALOHA.is_file():
        ZALOHA.write_bytes(t.encode("utf-8"))
        print("záloha: %s" % ZALOHA.name)

    n = zmen(t, IMPORT_STARY, IMPORT_NOVY, "importy")
    n = zmen(n, POMOC_STARY, POMOC_NOVY, "pomocník _cas_pred")
    n = zmen(n, FIX_STARY, FIX_NOVY, "fixture vloz()")
    n = zmen(n, SCEN_STARY, SCEN_NOVY, "očekávání scénářů")
    n = zmen(n, HLAV_STARY, HLAV_NOVY, "hlavička testu")
    n = zmen(n, ZMENA_STARY, ZMENA_NOVY, "text u známých vad")
    n = zmen(n, KOMENT_STARY, KOMENT_NOVY, "komentář invariantu 13")

    CIL.write_bytes(n.encode("utf-8"))
    z5 = CIL.read_text(encoding="utf-8")
    assert z5 == n, "zapsaný obsah nesedí"
    # POZOR: `'-10 minutes'` je i v komentáři, který vadu popisuje — kontroluje
    # se proto KÓD bez komentářů (jinak by pojistka hlásila falešný poplach).
    kod = "\n".join(r for r in z5.splitlines() if not r.lstrip().startswith("#"))
    assert "'-10 minutes'" not in kod, "v KÓDU fixture zůstal řetězcový čas"
    assert "datetime('now', ?),?)" not in z5, "starý INSERT zůstal"
    assert "_cas_pred(" in z5, "pomocník _cas_pred se nevložil"
    assert '("NOVÁ granule (vznikla teď, neselhal)", "queued", 0, None, True, False)' in z5
    print("OK: %s přepsán (%d → %d znaků)" % (CIL.name, len(t), len(z5)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 — MUTAČNÍ TEST VLASTNÍHO MĚŘIDLA `p14a-g3-nezavisle.py`.

PROČ: `overovani` §7.9 a checklist §3.4 — „napsal jsi bránu? Vrať do ní vadu
a podívej se, že spadne. Test bez toho není zelená, je slepá."

Měří se na **FIXTUŘE** (vlastní mini-repo v `_p14-overovani/fixtura-a/`), ne na
živém repu — takže se do orchestra nic nezapisuje. Fixtura má:
  * `hello.py`, `druhy.py`            … soubory, na které brány míří,
  * `_analyza/g3-brany.py`            … mini `BRANY` o 2 prvcích,
  * `_analyza/g3-brany-vystup.txt`    … výpis se 2 sekcemi `### … (exit=0)`.

PŘÍPADY (každý musí dát jiný důvod, ne jen „spadlo"):
  ZDRAVÝ   → exit 0
  M1 `<NEZNAMA>` v příkazu            → „ostrá závorka" (nedosazený záznamník)
  M2 ubrání prvku z BRANY             → počet AST ≠ počet sekcí
  M3 příkaz míří na neexistující soubor→ „neexistujících cest"
  M4 prázdné tělo sekce               → „prázdné tělo"
  M5 `can't open file` v těle sekce   → „podpis soubor neexistuje"

Každá mutace se ověří DVĚMA způsoby (`overovani` §7.9, §7.12):
  (1) že se soubor na disku OPRAVDU změnil (bajtově), a
  (2) že PŘESTALA PLATIT měřená podmínka (assert na konkrétní text).
Soubor se vrací v `finally` a návrat se ověřuje bajt na bajt.
"""
from __future__ import annotations

import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = pathlib.Path(__file__).resolve().parent
FIX = HERE / "fixtura-a"
MERIDLO = HERE / "p14a-g3-nezavisle.py"

G3_ZDRAVY = '''# -*- coding: utf-8 -*-
"""Mini g3 pro fixturu."""
BRANY = [
    ("prvni brana", ["python", "hello.py"], r"(\\d+) kontrol"),
    ("druha brana", ["python", "druhy.py"], r"(\\d+) kontrol"),
]
'''
VYPIS_ZDRAVY = """==============================================================================
### prvni brana   (exit=0)
==============================================================================
ZMERENO: 3 kontrol, 0 chyb
==============================================================================
### druha brana   (exit=0)
==============================================================================
ZMERENO: 5 kontrol, 0 chyb
"""

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if detail and not ok:
        print(f"        {detail}")


def vytvor_fixturu() -> None:
    if FIX.exists():
        shutil.rmtree(FIX)
    (FIX / "_analyza").mkdir(parents=True)
    # ZÁPIS BAJTŮ, ne textu: `write_text()` by na Windows přeložil `\n` na
    # `\r\n` a kotvy v mutacích by pak neseděly (`dsh-prostredi` §7.2).
    (FIX / "hello.py").write_bytes("print('ahoj')\n".encode("utf-8"))
    (FIX / "druhy.py").write_bytes("print('ahoj2')\n".encode("utf-8"))
    (FIX / "_analyza" / "g3-brany.py").write_bytes(G3_ZDRAVY.encode("utf-8"))
    (FIX / "_analyza" / "g3-brany-vystup.txt").write_bytes(VYPIS_ZDRAVY.encode("utf-8"))


def spust() -> tuple[int, str]:
    import os
    env = dict(os.environ)
    env["FORGE_WS"] = str(FIX)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(MERIDLO)], capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def mutuj(relace: str, popis: str, *,
          novy_text: str | None = None,
          hledej: str | None = None,
          nehledej: str | None = None,
          ocekavany_exit: int,
          ocekavany_text: str) -> None:
    """Provede jednu mutaci, spustí měřidlo, ověří PROVEDENÍ i výsledek."""
    cil = FIX / relace
    orig = cil.read_bytes()
    assert orig, f"fixtura {cil} je prázdná"
    try:
        kodovani = "utf-8"
        if novy_text is not None:
            novy = novy_text.encode(kodovani)
        else:
            assert hledej is not None, "mutace bez `hledej` i `novy_text`"
            kotva = hledej.encode(kodovani)
            pocet = orig.count(kotva)
            assert pocet == 1, f"kotva {hledej!r} je v souboru {pocet}×  (musí být 1×)"
            novy = orig.replace(kotva, nehledej.encode(kodovani))
        # (1) MUTACE SE OPRAVDU PROVEDLA — na disku, ne jen v proměnné
        assert novy != orig, "MUTACE NEPROBĚHLA (bajty jsou stejné)"
        cil.write_bytes(novy)
        zpet = cil.read_bytes()
        assert zpet == novy, "mutace se nepropsala na disk"
        # (2) PŘESTALA PLATIT MĚŘENÁ PODMÍNKA
        if hledej is not None:
            assert kotva not in zpet, f"měřená podmínka pořád platí: {hledej!r}"
        kod, vystup = spust()
        zkontroluj(f"{popis}: exit={kod} (čekáno {ocekavany_exit})",
                   kod == ocekavany_exit, vystup[-900:])
        zkontroluj(f"{popis}: výstup obsahuje {ocekavany_text!r}",
                   ocekavany_text in vystup, vystup[-900:])
    finally:
        cil.write_bytes(orig)
        assert cil.read_bytes() == orig, f"SOUBOR NEVRÁCEN: {cil}"


print("=" * 84)
print("MUTAČNÍ TEST VLASTNÍHO MĚŘIDLA `p14a-g3-nezavisle.py` (fixtura, ne živé repo)")
print("=" * 84)

vytvor_fixturu()
kod, vystup = spust()
zkontroluj(f"ZDRAVÝ případ fixtury: exit={kod} (čekáno 0)", kod == 0, vystup[-1200:])
zkontroluj("ZDRAVÝ případ: 2 = 2 a 0 neexistujících cest",
           "bran v BRANY (AST) = 2" in vystup and "neexistujících cest = 0" in vystup,
           vystup[-1200:])
zkontroluj("ZDRAVÝ případ NENÍ slepý: měřidlo vykázalo počet kontrol",
           re.search(r"ZMĚŘENO: \d+ kontrol", vystup) is not None, vystup[:400])

print()
mutuj("_analyza/g3-brany.py", "M1 nedosazený záznamník <NEZNAMA>",
      hledej='["python", "hello.py"]', nehledej='["python", "<NEZNAMA>/hello.py"]',
      ocekavany_exit=1, ocekavany_text="CHYBA po dosazení nezůstala ostrá závorka")

print()
mutuj("_analyza/g3-brany.py", "M2 v BRANY chybí jedna brána",
      hledej='    ("druha brana", ["python", "druhy.py"], r"(\\d+) kontrol"),\n',
      nehledej="",
      ocekavany_exit=1, ocekavany_text="CHYBA počet bran v AST")

print()
mutuj("_analyza/g3-brany.py", "M3 příkaz míří na neexistující soubor",
      hledej='"druhy.py"', nehledej='"druhy-NEEXISTUJE.py"',
      ocekavany_exit=1, ocekavany_text="CHYBA neexistujících cest")

print()
mutuj("_analyza/g3-brany-vystup.txt", "M4 prázdné tělo sekce",
      hledej="ZMERENO: 5 kontrol, 0 chyb\n", nehledej="",
      ocekavany_exit=1, ocekavany_text="CHYBA žádná sekce nemá PRÁZDNÉ tělo")

print()
mutuj("_analyza/g3-brany-vystup.txt", "M5 podpis „soubor neexistuje“ v těle",
      hledej="ZMERENO: 3 kontrol, 0 chyb",
      nehledej="python: can't open file 'hello.py': [Errno 2] No such file or directory",
      ocekavany_exit=1, ocekavany_text="CHYBA žádná sekce nenese podpis")

print()
print("=" * 84)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
shutil.rmtree(FIX, ignore_errors=True)
if chyb:
    print(f"CHYBA: {chyb} — vlastní měřidlo NEMĚŘÍ")
    sys.exit(1)
print("VLASTNÍ MĚŘIDLO MĚŘÍ: zdravý případ projde, každá z 5 vad ho shodí.")
sys.exit(0)

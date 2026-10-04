#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""H17 — VLASTNÍ ověření měřidla C2 (N1: nástroj čte zastaralý inventář).

Tvrzení k ověření: „`hl-rizika-jazyka.py` pozná ZASTARALÝ inventář a skončí
nenulově" (dřív četl snapshot z 08:01 a hlásil 7 vad, které už byly opravené).

Metoda (nezávislá na `c2-mutace.py`): přepíše se `otisk_vstupu.sha256`
v `_analyza\_inventar.json`, ale v NEuzavřeném tvaru — a ověří se, že to
nástroj pozná. Testuje se i to, že úklid je BAJT NA BAJT (jinak by test
zanechal v repu změnu, která vypadá jako práce session).

Běhy:
  1) zdravý inventář                     → musí projít (exit 0)
  2) otisk přepsán na neexistující sha   → musí SPADNOUT (exit 1) + říct to
  3) návrat na bajt (sha256 před/po)     → musí projít (exit 0)

Použití:  python _analyza\h17-over-c2.py
"""

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
INV = WS / "_analyza" / "_inventar.json"
TOOL = WS / "_analyza" / "hl-rizika-jazyka.py"

assert INV.is_file(), "inventar neexistuje"
assert TOOL.is_file(), "nastroj neexistuje"

PUVODNI_BAJTY = INV.read_bytes()
PUVODNI_SHA = hashlib.sha256(PUVODNI_BAJTY).hexdigest()
print("=" * 78)
print("H17 — C2: pozná nástroj ZASTARALÝ inventář?")
print("=" * 78)
print("  inventář: %s  (%d B, sha256 %s)"
      % (INV.name, len(PUVODNI_BAJTY), PUVODNI_SHA[:16]))


def spust() -> tuple:
    r = subprocess.run([sys.executable, str(TOOL)], capture_output=True, cwd=str(WS))
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return r.returncode, v


def klic_radky(vystup: str) -> list:
    return [l.strip() for l in vystup.splitlines()
            if "otisk" in l.lower() or "ZASTARAL" in l or "NELZE" in l
            or "stáří" in l or "INVENTÁŘ" in l or "PŘEJEDNANÝCH" in l]


vysledky = {}


def obnov() -> None:
    INV.write_bytes(PUVODNI_BAJTY)
    sha = hashlib.sha256(INV.read_bytes()).hexdigest()
    assert sha == PUVODNI_SHA, "OBNOVA NESEDI — inventář není bajt na bajt!"


try:
    # --- 1) zdravý stav -----------------------------------------------------
    print()
    print("-" * 78)
    print("BĚH 1: zdravý inventář (kontrola, že nástroj vůbec měří)")
    print("-" * 78)
    kod, vystup = spust()
    vysledky["1-zdravy"] = kod
    for l in klic_radky(vystup)[:5]:
        print("    " + l[:150])
    print("    → exit=%d" % kod)

    # --- 2) podvrh: přepíšu otisk vstupů ------------------------------------
    print()
    print("-" * 78)
    print("BĚH 2: otisk vstupů PŘEPSÁN (kód se od vzniku inventáře změnil)")
    print("-" * 78)
    data = json.loads(PUVODNI_BAJTY.decode("utf-8"))
    stary = data.get("otisk_vstupu")
    assert isinstance(stary, dict) and "sha256" in stary, \
        "inventář nemá otisk_vstupu — N1 by se nedal ověřit"
    print("    otisk v inventáři: %s  (%s souborů)"
          % (str(stary.get("sha256"))[:16], stary.get("souboru")))
    data["otisk_vstupu"] = dict(stary)
    data["otisk_vstupu"]["sha256"] = "0" * 64
    nove = json.dumps(data, ensure_ascii=False, indent=2).encode("utf-8")
    assert nove != PUVODNI_BAJTY, "MUTACE NEPROBEHLA"
    INV.write_bytes(nove)
    # POJISTKA (past overovani §7.14): měřená PODMÍNKA musí přestat platit.
    na_disku = json.loads(INV.read_bytes().decode("utf-8"))["otisk_vstupu"]["sha256"]
    assert na_disku == "0" * 64 and na_disku != stary["sha256"], \
        "PODMINKA PORAD PLATI — mutace nic nezmenila"
    print("    [mutace zapsána a ověřena z disku: %s → %s]"
          % (str(stary.get("sha256"))[:16], na_disku[:16]))

    kod2, vystup2 = spust()
    vysledky["2-podvrh"] = kod2
    for l in klic_radky(vystup2)[:8]:
        print("    " + l[:150])
    print("    → exit=%d" % kod2)

    # --- 3) obnova ----------------------------------------------------------
    obnov()
    print()
    print("-" * 78)
    print("BĚH 3: návrat na původní bajty")
    print("-" * 78)
    kod3, vystup3 = spust()
    vysledky["3-obnova"] = kod3
    for l in klic_radky(vystup3)[:4]:
        print("    " + l[:150])
    print("    → exit=%d" % kod3)
finally:
    obnov()
    print()
    print("  [úklid: inventář vrácen — sha256 %s]"
          % hashlib.sha256(INV.read_bytes()).hexdigest()[:16])

print()
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
for k, v in vysledky.items():
    print("  %-12s exit=%s" % (k, v))
chyby = []
if vysledky.get("1-zdravy") != 0:
    chyby.append("zdravý inventář neskončil 0 — nástroj neměří")
if vysledky.get("2-podvrh") == 0:
    chyby.append("PODVRH PROŠEL (exit 0) — měřidlo je slepé na zastaralost")
if vysledky.get("3-obnova") != 0:
    chyby.append("po obnově nástroj neskončil 0 — úklid nebo nástroj je vadný")
print()
if chyby:
    print("NALEZENO %d PROBLÉMŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE SEDÍ — měřidlo C2 pozná zastaralý inventář (vlastní měření)")
sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MUTAČNÍ TEST Úkolu C2 (nález N1) — umí nástroj spadnout na zastaralém inventáři?

ZADÁNÍ: „mutační test, že se starým inventářem nástroj OHLÁSÍ STÁŘÍ a neprojde
jako ‚0 vrácených'".

CO SE MĚŘÍ (čtyři běhy, pořadí je závazné — první je kontrola, že brána umí projít):
  1. ZDRAVÝ                        → exit 0
  2. otisk v inventáři PŘEPSÁN    → exit 1  (simuluje, že se kód po vzniku změnil)
  3. inventář BEZ otisku          → exit 1  (starší formát — nezměřeno není zelená)
  4. inventář SMAZÁN              → exit 1 + obnova (bez `write_text` v nástroji)
  5. návrat do zdravého stavu     → exit 0  (a inventář je bajt na bajt zpátky)

POZOR NA PAST: smazání souboru v sandboxu vypadá jako „nástroj neumí obnovit",
ale je to prostředí (skill `dsh-prostredi` §4). Skript proto při `WinError 5`
řekne, že šlo o oprávnění, a NE o vadu nástroje.

Použití: python _analyza\\c2-mutace.py
"""

import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
INVENTAR = ANALYZA / "_inventar.json"
NASTROJ = ANALYZA / "hl-rizika-jazyka.py"
ZALOHA = ANALYZA / "c2-mutace-zaloha.json"


def spust() -> tuple:
    r = subprocess.run([sys.executable, str(NASTROJ)], capture_output=True,
                       cwd=str(WS), timeout=1800)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return r.returncode, v


def vypis_zajimave(v: str, kod: int) -> None:
    for radek in v.splitlines():
        if any(k in radek for k in ("stáří", "otisk", "CHYBA", "ZASTARALÝ",
                                    "0 vrácených", "SEZNAM SEDÍ", "nezměřeno",
                                    "NELZE ověřit", "Obnov", "inventář")):
            print("      " + radek.strip()[:150])
    print("      → exit=%d" % kod)


def zalohuj() -> str:
    puvodni = INVENTAR.read_bytes()
    ZALOHA.write_bytes(puvodni)
    return hashlib.sha256(puvodni).hexdigest()


def obnov(otisk: str) -> bool:
    INVENTAR.write_bytes(ZALOHA.read_bytes())
    zpet = hashlib.sha256(INVENTAR.read_bytes()).hexdigest()
    return zpet == otisk


def zmen_inventar(uprav) -> None:
    d = json.loads(INVENTAR.read_text(encoding="utf-8"))
    uprav(d)
    INVENTAR.write_bytes(
        json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8"))


def main() -> int:
    if not INVENTAR.is_file() or not NASTROJ.is_file():
        print("CHYBA: chybí %s nebo %s" % (INVENTAR, NASTROJ))
        return 2

    otisk_zdroje = zalohuj()
    vysledky = []

    # ── 1) zdravý stav ────────────────────────────────────────────────────
    print("=" * 76)
    print("1) ZDRAVÝ INVENTÁŘ (musí projít, jinak další mutace nic nedokazují)")
    print("=" * 76)
    kod, v = spust()
    vypis_zajimave(v, kod)
    vysledky.append(("zdravý", kod, 0))
    if kod != 0:
        print("   → brána neprojde ani ve zdravém stavu; končím")
        obnov(otisk_zdroje)
        return 2

    # ── 2) otisk přepsán (simulace: kód se změnil) ────────────────────────
    print()
    print("=" * 76)
    print("2) OTSK V INVENTÁŘI PŘEPSÁN (kód se od jeho vzniku změnil)")
    print("=" * 76)
    zmen_inventar(lambda d: d["otisk_vstupu"].__setitem__("sha256", "0" * 64))
    kod, v = spust()
    vypis_zajimave(v, kod)
    vysledky.append(("přepsaný otisk", kod, 1))
    obnov(otisk_zdroje)

    # ── 3) inventář bez otisku (starší formát) ────────────────────────────
    print()
    print("=" * 76)
    print("3) INVENTÁŘ BEZ OTISKU (starší formát — stáří se NEDÁ ověřit)")
    print("=" * 76)
    zmen_inventar(lambda d: d.pop("otisk_vstupu", None))
    kod, v = spust()
    vypis_zajimave(v, kod)
    vysledky.append(("bez otisku", kod, 1))
    obnov(otisk_zdroje)

    # ── 4) inventář smazán ────────────────────────────────────────────────
    print()
    print("=" * 76)
    print("4) INVENTÁŘ SMAZÁN (nástroj ho má obnovit sám, bez zápisu ve svém zdroji)")
    print("=" * 76)
    try:
        os.remove(INVENTAR)
    except PermissionError as e:
        print("   POZOR: smazání selhalo na oprávněních (%s) — to je PROSTŘEDÍ,"
              % type(e).__name__)
        print("          ne vada nástroje. Tenhle krok se přeskočí.")
        obnov(otisk_zdroje)
    else:
        kod, v = spust()
        vypis_zajimave(v, kod)
        vysledky.append(("smazaný inventář", kod, 0))
        if INVENTAR.is_file():
            obnov(otisk_zdroje)

    # ── 5) návrat ─────────────────────────────────────────────────────────
    print()
    print("=" * 76)
    print("5) NÁVRAT DO ZDRAVÉHO STAVU")
    print("=" * 76)
    if not obnov(otisk_zdroje):
        print("   CHYBA: inventář se nevrátil bajt na bajt!")
        return 2
    kod, v = spust()
    vypis_zajimave(v, kod)
    vysledky.append(("návrat", kod, 0))

    # ── souhrn ────────────────────────────────────────────────────────────
    print()
    print("=" * 76)
    spatne = 0
    for jmeno, kod, ocekavano in vysledky:
        ok = kod == ocekavano
        if not ok:
            spatne += 1
        print("  %-20s exit=%d  (očekáváno %d)  %s"
              % (jmeno, kod, ocekavano, "OK" if ok else "!! NESEDÍ"))
    print("=" * 76)
    print("VÝSLEDEK: %s" % ("brána měří — zastaralý i nezměřený inventář SHODÍ nástroj"
                            if spatne == 0 else "NĚCO NESEDÍ (%d)" % spatne))
    return 0 if spatne == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

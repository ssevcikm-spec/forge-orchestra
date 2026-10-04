#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Vytáhne starý blok (`run_tests.gd:834–840`) do `_analyza\\a-stary-blok.gd`.

PROČ: patcher porovnává blok **bajt na bajt**. Když ho napíšu ručně, snadno
se spletu v `\\"` (přesně to se stalo první verzi) a „oprava" se tichounce
neprovede. Tady se blok opíše z repa, takže sedí vždy.

Použití: python _analyza\\a-vyrob-stary-blok.py
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
ZDROJ = ANALYZA.parent / "games" / "uo-shadows" / "tests" / "run_tests.gd"
CIL = ANALYZA / "a-stary-blok.gd"

PRVNI = "# Drift iso_position: hráč smí volat izo projekci jen na světě (world),"

radky = ZDROJ.read_text(encoding="utf-8").splitlines(keepends=True)

# Najdi začátek podle textu (ne podle čísla řádku — to se může posunout).
start = None
for i, r in enumerate(radky):
    if PRVNI in r:
        start = i
        break
if start is None:
    print("CHYBA: komentář %r v %s není" % (PRVNI, ZDROJ))
    sys.exit(2)

# Blok končí řádkem s `"player volá izo projekci přes world, ne přes level")`
konec = None
for j in range(start, len(radky)):
    if "player volá izo projekci přes world, ne přes level" in radky[j]:
        konec = j
        break
if konec is None:
    print("CHYBA: konec bloku (řádek s hláškou) nenalezen")
    sys.exit(2)

blok = "".join(radky[start:konec + 1])
if not blok.endswith("\n"):
    print("CHYBA: blok nekončí newline — další řádek by se přilepil")
    sys.exit(2)

# Pojistky na to, co musí blok obsahovat (jinak by patcher porovnával něco jiného)
for klic in ('player.has_method("move")', "level.iso_position", '\\"iso_position\\"'):
    if klic not in blok:
        print("CHYBA: v bloku chybí %r — vytažený blok není ten správný" % klic)
        sys.exit(2)

CIL.write_bytes(blok.encode("utf-8"))
print("OK: %s (%d řádků, %d znaků)" % (CIL, konec - start + 1, len(blok)))
for r in blok.splitlines():
    print("   " + r)

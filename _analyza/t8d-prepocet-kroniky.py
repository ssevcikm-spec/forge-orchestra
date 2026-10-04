# -*- coding: utf-8 -*-
r"""Prepocte kroniku po pridani omylu 80: blok 8h 8 -> 9, celkem 74 -> 75.

Dela se to JEDNIM pruchodem a s pojistkou na konci: kdyz kterekoli cislo
nesedi, soubor se VUBEC nezapise (jinak by vznikla pulka zmeny — namereno
2. 10. 2026: skript spadl v pulce a `8h` zustalo na 8, zatimco souhrn uz
tvrdil 75).
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
P = WS / "KRONIKA-PROJEKTU.md"
s = P.read_text(encoding="utf-8")
puvodni = s

ZMENY = [
    # --- tabulka po blocích v §3 (tvar, ktery brána čte) ---
    ("| **8h** | akční 2. 10. 16:1x | **8** | **8** | **4** |",
     "| **8h** | akční 2. 10. 16:1x | **9** | **9** | **5** |"),
    ("| **celkem** | **8 bloků, 17 sessions** | **74** | **58 = 78 %** | **31** |",
     "| **celkem** | **8 bloků, 17 sessions** | **75** | **59 = 79 %** | **32** |"),
    # --- souhrn nad tabulkou ---
    ("| **omylů celkem** | **74** |", "| **omylů celkem** | **75** |"),
    ("| **z toho vad MĚŘIDLA** | **58 = 78 %** |", "| **z toho vad MĚŘIDLA** | **59 = 79 %** |"),
    ("| **z toho vypadalo jako nález o CIZÍM kódu** | **31** |",
     "| **z toho vypadalo jako nález o CIZÍM kódu** | **32** |"),
    # --- text o trendu ---
    ("a blok **8h** má dokonce **8 z 8**\n> (100 %)",
     "a blok **8h** má dokonce **9 z 9**\n> (100 %)"),
    ("**opakuje i po 74 zaznamenaných omylech**", "**opakuje i po 75 zaznamenaných omylech**"),
    # --- radek session 17 v §1 ---
    ("| **72–79** |", "| **72–80** |"),
]

for stary, novy in ZMENY:
    pocet = s.count(stary)
    assert pocet == 1, "vzor %r je v souboru %dx, cekal jsem 1x" % (stary[:60], pocet)
    s = s.replace(stary, novy, 1)
    print("OK  %s" % novy[:62])

# --- POJISTKA: vsechna cisla musi sedet, jinak se nezapisuje ---
assert s != puvodni, "NAHRADA NEPROBEHLA"
assert "| **8h** | akční 2. 10. 16:1x | **9** | **9** | **5** |" in s, "radek 8h nema 9"
assert "| **celkem** | **8 bloků, 17 sessions** | **75** | **59 = 79 %** | **32** |" in s, "celkem nema 75"
assert "**8 z 8**" not in s, "zustalo 8 z 8"
assert "**72–79**" not in s, "zustal stary rozsah omylu"
assert "**74** |" not in s.split("## 3. Počty omylů")[1][:2500], "v sekci 3 zustalo 74"

P.write_bytes(s.encode("utf-8"))
zpet = P.read_text(encoding="utf-8")
assert zpet == s, "zapsany obsah nesedi"
print()
print("KRONIKA prepoctena (overeno ctenim z disku): 8h = 9, celkem = 75")

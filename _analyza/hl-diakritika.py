#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Rucni kontrola diakritiky u dokumentu, ktere kontrola-diakritiky.py NESLEDUJE.

PROC tohle existuje: `orchestra/tools/kontrola-diakritiky.py` ma PEVNY seznam
22 souboru (17 cest v workspace + 5 skillu). Novy dokument se do nej musi pridat
rucne - a dokud se to nestane, gate o nem vi stejne jako o souboru, ktery
neexistuje. Tenhle skript dela to, co by delala gate, kdyby scanovala cely
workspace.

POZOR: seznam rozbitych znaku se CTE ZE GATE, neopisuje se. Kdyby se v gate
zmenil, tenhle skript to dostane taky - a zaroven se tim do dokumentace
nedostanou doslovne ukazky rozbiteho kódování (AGENTS.md to zakazuje).

Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl-diakritika.py
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
GATE = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
TEXT = GATE.read_text(encoding="utf-8")

# seznam rozbitych znaku se cte z gate (binarni set, aby se nevypisoval)
m = re.search(r"ROZBITE\s*=\s*\[([^\]]*)\]", TEXT)
if not m:
    print("CHYBA: v gate se nenasel seznam ROZBITE - skript je slepy, koncim")
    sys.exit(2)
ROZBITE = [z for z in re.findall(r'"([^"]*)"', m.group(1))]
print(f"# vzor prevzat z gate: {len(ROZBITE)} znaku (nevypisuji se - viz AGENTS.md)")

# soubory, ktere jsem v teto session vytvoril nebo zmenil
MOJE = [
    WS / "ANALYZA-HLOUBKOVA-ORCHESTRA.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI.md",
    WS / "OTEVRENA-TEMATA.md",
]
sledovane = re.findall(r'WS / "([^"]+)"', TEXT)

chyb = 0
print("\n=== moje dokumenty (kontrola rucne, stejnym vzorem jako gate) ===")
for f in MOJE:
    if not f.exists():
        print(f"  CHYBA {f.name}: neexistuje")
        chyb += 1
        continue
    s = f.read_text(encoding="utf-8")
    n = [z for z in ROZBITE if z in s]
    if n:
        chyb += 1
    print(f"  {'OK  ' if not n else 'CHYBA'} {f.name:38} {len(s):7} znaku  "
          f"rozbito: {'ANO (' + str(len(n)) + ' druhu)' if n else 'ne'}")

print(f"\n=== co sleduje gate ({len(sledovane)} cest v workspace) ===")
for x in sledovane:
    print(f"   {x}")
vSeznamu = any("HLOUBKOVA-ORCHESTRA" in x for x in sledovane)
print(f"\n   muj novy dokument je v seznamu gate: {'ANO' if vSeznamu else 'NE'}")

print(f"\nVYSLEDEK: {chyb} chyb")
if chyb:
    sys.exit(1)
if not vSeznamu:
    print("POZNAMKA: dokument je v poradku, ale gate ho NESLEDUJE - "
          "dokud se neprida do seznamu, jeho kontrola je jen tahle rucni.")

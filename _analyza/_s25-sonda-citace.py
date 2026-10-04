# -*- coding: utf-8 -*-
"""SONDA 6 (jednorázová) — proč u `HANDOFF.md:743` nevychází CITACE.

Sahá na funkci z nástroje (import), ne na její opis — `overovani` §10.5:
„ověřovatel musí měřit TÝMŽ oknem jako nástroj".
"""
import importlib.util
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
radek_c = 743

radky = CIL.read_text(encoding="utf-8").splitlines()
radek = radky[radek_c - 1]
print("=" * 100)
print("  ŘÁDEK HANDOFF.md:%d" % radek_c)
print("=" * 100)
print(repr(radek[:340]))
print()

i = radek.find("32 sloupc")
print("  pozice '32 sloupc' v řádku: %d" % i)
print("  znak na té pozici: %r" % radek[i])
print("  120 znaků PŘED: %r" % radek[max(0, i - 120):i])
print()

# Sken zleva doprava — přesně jak to dělá nástroj
UVOZOVKY = [("„", "“"), ("„", '"'), ('"', '"'), ("`", "`"), ("*„", "“")]
otevreno = []
k = 0
print("  PRŮBĚH SKENU (jen do pozice čísla):")
while k < len(radek):
    if otevreno and otevreno[-1] == "`":
        if radek.startswith("„", k):
            otevreno.append("“")
            print("    %3d: OTEVÍRÁ „ (v backticku) → zásobník %s" % (k, otevreno))
            k += 1
            continue
        if k == i:
            print("    %3d: ← TADY JE ČÍSLO, zásobník = %s" % (k, otevreno))
        k += 1
        continue
    if otevreno:
        if radek.startswith(otevreno[-1], k):
            print("    %3d: ZAVÍRÁ %r → zásobník %s" % (k, otevreno[-1], otevreno[:-1]))
            k += len(otevreno.pop())
        else:
            if k == i:
                print("    %3d: ← TADY JE ČÍSLO, zásobník = %s" % (k, otevreno))
            k += 1
        continue
    for otev, zavr in UVOZOVKY:
        if radek.startswith(otev, k):
            otevreno.append(zavr)
            print("    %3d: OTEVÍRÁ %r → zásobník %s" % (k, otev, otevreno))
            k += len(otev)
            break
    else:
        if k == i:
            print("    %3d: ← TADY JE ČÍSLO, zásobník = %s" % (k, otevreno))
        k += 1
print()
print("  ZÁVĚR SKENU na pozici čísla: zásobník = %s → citace = %s"
      % (otevreno, bool(otevreno)))

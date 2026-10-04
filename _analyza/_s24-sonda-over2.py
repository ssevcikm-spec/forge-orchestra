# -*- coding: utf-8 -*-
"""SONDA 2 — jak přesně `audit2b` vypisuje řádky s `granulí`?

Sonda 1 nenašla ani jeden hlášený řádek, protože její vzor neodpovídal
skutečnému formátu výpisu (`overovani` §8.4: **vypiš si OKOLÍ**, nehádej vzor).
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable

v = subprocess.run([PY, "_analyza/audit2b-cisla-proti-zdroji.py"],
                   cwd=str(WS), capture_output=True, timeout=600)
out = v.stdout.decode("utf-8", "replace")
radky = out.splitlines()

print("1) všechny řádky výpisu, které obsahují 'granulí' (řádek po řádku):")
for i, l in enumerate(radky, 1):
    if "granulí" in l:
        print("   %4d | %s" % (i, l[:120]))

print("\n2) okolí hlavičky ROZCHODY / ZÁZNAMY:")
for i, l in enumerate(radky, 1):
    if "ROZCHODY (tvrzení bez známky minulosti)" in l:
        for j in range(i - 1, min(i + 4, len(radky))):
            print("   %4d | %s" % (j + 1, radky[j][:120]))
    if "ZÁZNAMY A CITACE MINULOSTI" in l:
        for j in range(i - 1, min(i + 4, len(radky))):
            print("   %4d | %s" % (j + 1, radky[j][:120]))

print("\n3) hledám kotvu '21 granul' ve výpisu:")
for i, l in enumerate(radky, 1):
    if "21 granul" in l or "16 řádků" in l:
        print("   %4d | %s" % (i, l[:130]))

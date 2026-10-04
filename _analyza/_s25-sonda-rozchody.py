# -*- coding: utf-8 -*-
"""SONDA (jednorázová, 2. 10. 2026) — vypíše OKOLÍ každého rozchodu z `audit2b`.

PROČ: `overovani` §8.4 — „než změníš vzor, vypiš si OKOLÍ toho místa".
Než začnu měřit, KTERÝ zdroj které číslo vydal, musím vidět, co na těch
řádcích skutečně stojí (a co je nad nimi v nadpisu oddílu).

Nic nemění, jen čte.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent

# Přesně ty rozchody, které vypsal běh `_analyza\_s25-audit2b-pred.txt`
# (dvojice soubor:řádek, veličina) — načtou se z výpisu, ne opisem.
VYSTUP = WS / "_analyza" / "_s25-audit2b-pred.txt"
VZOR = re.compile(r"^\s+(\S+\.md)\s+:(\d+)\s+(\S+)\s+tvrdí\s+(\S+)\s+zdroj\s+(\S+)")

text = VYSTUP.read_text(encoding="utf-8", errors="replace")
v_rozchodech = False
nalezy = []
for l in text.splitlines():
    if l.startswith("  ROZCHODY ("):
        v_rozchodech = True
        continue
    if l.startswith("  ZÁZNAMY A CITACE"):
        v_rozchodech = False
        continue
    if not v_rozchodech:
        continue
    m = VZOR.match(l)
    if m:
        nalezy.append((m.group(1), int(m.group(2)), m.group(3),
                       int(m.group(4)), int(m.group(5))))

print("=" * 100)
print("  OKOLÍ %d ROZCHODŮ (ze výpisu `_s25-audit2b-pred.txt`)" % len(nalezy))
print("=" * 100)

predchozi_soubor = None
cache = {}
for jmeno, radek, velicina, tvrzeno, zdroj in nalezy:
    if jmeno not in cache:
        cache[jmeno] = (WS / jmeno).read_text(encoding="utf-8").splitlines()
    radky = cache[jmeno]
    if jmeno != predchozi_soubor:
        print()
        predchozi_soubor = jmeno
    # nadpis oddílu `## ` nad tímto řádkem
    nadpis = ""
    for k in range(min(radek - 1, len(radky) - 1), -1, -1):
        if radky[k].startswith("## "):
            nadpis = radky[k]
            break
    obsah = radky[radek - 1] if radek - 1 < len(radky) else "(řádek mimo soubor!)"
    print("-" * 100)
    print("  %s:%d   veličina=%s  tvrdí %d  zdroj %d" % (jmeno, radek, velicina,
                                                          tvrzeno, zdroj))
    print("    oddíl: %s" % nadpis[:96])
    print("    řádek: %s" % obsah.strip()[:190])

print()
print("=" * 100)
print("  SHRNUTÍ: rozchodů=%d" % len(nalezy))

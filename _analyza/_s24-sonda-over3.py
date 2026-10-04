# -*- coding: utf-8 -*-
"""SONDA 3 — je kotva „21 granul" ve výpisu `audit2b` VŮBEC?

Sonda 2 hledala `granulí` a `21 granul` a **nenašla kotvu** — jen `AGENTS.md`.
To je podezřelé: `audit2b-over.py` tvrdí, že kotva má číslo řádku **1201**.
Sonda proto vypíše **všechny** řádky výpisu, které obsahují `HANDOFF.md`,
a u každého číslo řádku i veličinu.
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

print("1) VŠECHNY hlášené řádky HANDOFF.md (obě sekce):")
n = 0
for l in out.splitlines():
    if "HANDOFF.md" in l and ":" in l and "tvrdí" in l:
        n += 1
        print("   %s" % l.strip()[:118])
print("   celkem: %d" % n)

print("\n2) hledám '1201' a '16 řádků' kdekoliv ve výpisu:")
for i, l in enumerate(out.splitlines(), 1):
    if "1201" in l or "16 řádků" in l:
        print("   %4d | %s" % (i, l.strip()[:118]))

print("\n3) kde je v souboru kotva a co vrací stejná funkce jako v nástroji:")
s = (WS / "HANDOFF.md").read_text(encoding="utf-8")
KOTVA = "- **D1 má 16 řádků na 21 granul**"
i = s.find(KOTVA)
print("   find() = %d -> řádek %d" % (i, s[:i].count("\n") + 1))
radky = s.splitlines()
cislo = s[:i].count("\n") + 1
print("   splitlines()[%d] = %s" % (cislo - 1, radky[cislo - 1][:100]))

print("\n4) jak by kotvu viděl blok(): začátek řádku")
print("   lstrip().startswith('|') : %s" % radky[cislo - 1].lstrip().startswith("|"))
ZACATEK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\||#)")
print("   ZACATEK.match(řádek)     : %s" % bool(ZACATEK.match(radky[cislo - 1])))

print("\n5) nejbližší nadpisy NAD kotvou (co vrací nadpis_oddilu):")
for k in range(cislo - 1, -1, -1):
    if radky[k].startswith("## "):
        print("   ##  (r.%d) %s" % (k + 1, radky[k][:88]))
        break

print("\n6) co je na řádcích 1195-1205 (kontext kotvy):")
for k in range(cislo - 7, cislo + 5):
    print("   %4d | %s" % (k + 1, radky[k][:104]))

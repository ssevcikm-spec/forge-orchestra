# -*- coding: utf-8 -*-
"""SONDA 4 — jaký vzor `audit2b` SKUTEČNĚ používá pro `granulí`?

Odpovídá na `overovani` §10.5: **vypiš vzor, ne popis vzoru.**
Vzor se čte **ze zdrojáku nástroje** (aby se neopisoval) a zkouší se
na skutečných řádcích dokumentu.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
zdroj = (WS / "_analyza" / "audit2b-cisla-proti-zdroji.py").read_text(encoding="utf-8")

# vytáhni VZORY ze zdrojáku
i = zdroj.find("VZORY = {")
j = zdroj.find("}", i)
blok = zdroj[i:j + 1]
print("VZORY ve zdrojáku:")
for radek in blok.splitlines():
    if ":" in radek:
        print("   %s" % radek.strip()[:110])

m = re.search(r'"granulí":\s*r"([^"]*)"', zdroj)
print("\nvzor pro `granulí` = %r" % (m.group(1) if m else "NENALEZEN"))
vzor = m.group(1) if m else ""
try:
    rx = re.compile(vzor)
    print("kompiluje se: ANO")
except re.error as e:
    print("kompiluje se: NE — %s" % e)
    sys.exit(1)

print("\nzkouším na skutečných řádcích:")
kandidati = [
    ("HANDOFF.md kotva", "- **D1 má 16 řádků na 21 granul** — chybí"),
    ("HANDOFF.md jiný", "na 21 granul**ích"),
    ("AGENTS.md", "**31 granul smazané hry**"),
    ("AGENTS.md jiný", "**31 granul** smazané hry"),
    ("s cyrilským e", "22 granulе"),
    ("prostý tvar", "22 granulí"),
]
for jmeno, radek in kandidati:
    mm = rx.search(radek)
    print("   %-18s %-42s -> %s" % (jmeno, radek[:42], mm.group(0) if mm else "NIC"))

print("\nkolik výskytů v celém HANDOFF.md: %d"
      % len(list(rx.finditer((WS / "HANDOFF.md").read_text(encoding="utf-8")))))
print("kolik výskytů v celém AGENTS.md: %d"
      % len(list(rx.finditer((WS / "AGENTS.md").read_text(encoding="utf-8")))))

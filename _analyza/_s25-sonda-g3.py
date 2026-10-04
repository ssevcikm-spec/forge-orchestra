# -*- coding: utf-8 -*-
"""SONDA 10 — proč `g3` u `validate-all` pořád vypisuje `3` (nález NA23).

Měří TÝMŽ vzorem a TÝMŽ souborem, jaký `g3-brany.py` skutečně má —
a vypíše, co `finditer` v bloku `validate-all (CELEK)` najde.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
G3 = WS / "_analyza" / "g3-brany.py"
VYSTUP = WS / "_analyza" / "g3-brany-vystup.txt"

z = G3.read_text(encoding="utf-8")
# Vytáhni vzor přesně tak, jak je v seznamu BRANY u validate-all
m = re.search(r'\("validate-all \(CELEK\)",\s*\[[^\]]*\],\s*\n?\s*(r"[^"]*")\)', z)
print("  vzor nalezený ve zdroji: %s" % (m.group(1) if m else "NENALEZEN"))
vzor = eval(m.group(1)) if m else ""
print("  vzor jako hodnota:       %r" % vzor)

v = VYSTUP.read_text(encoding="utf-8", errors="replace")
i = v.find("### validate-all (CELEK)")
print("  blok začíná na pozici:   %d (z %d)" % (i, len(v)))
blok = v[i:]
print("  blok má znaků:           %d" % len(blok))

nalezy = list(re.finditer(vzor, blok))
print("  výskytů vzoru v bloku:   %d" % len(nalezy))
for k, mm in enumerate(nalezy):
    print("      %d) %r  skupiny=%s" % (k, mm.group(0)[:40], mm.groups()))

print()
print("  → nástroj bere POSLEDNÍ z nich: %r"
      % (nalezy[-1].group(0)[:40] if nalezy else "—"))
if nalezy:
    skupiny = [g for g in nalezy[-1].groups() if g]
    print("  → do výpisu by šlo: %r" % (" / ".join(skupiny) if skupiny else "—"))

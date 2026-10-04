# -*- coding: utf-8 -*-
"""SONDA 11 — co `audit2b` řekne o `AGENTS.md:62`, když se z citace stane tvrzení.

Dělá TOTÉŽ co mutace M3 v `audit2b-over.py`, ale vypíše u toho **výpisní cestu**
nástroje (řádek ze ZÁZNAMŮ i z ROZCHODŮ) — `overovani` §8.4: než začnu
opravovat, vypiš si OKOLÍ a VÝPISNÍ CESTU.
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
AGENTS = WS / "AGENTS.md"
orig = AGENTS.read_bytes()

KOTVA = '`AGENTS.md` tvrdil u `conductor/schema.sql` **„32 sloupců"**'
NAHRAD = '`AGENTS.md` tvrdil u `conductor/schema.sql` **32 sloupců**'

t = orig.decode("utf-8")
print("  kotva v souboru: %dx" % t.count(KOTVA))
assert t.count(KOTVA) == 1

zmut = t.replace(KOTVA, NAHRAD, 1)
assert zmut != t, "MUTACE NEPROBĚHLA"
# měřená podmínka: uvozovky u čísla už NEJSOU
i = zmut.index(NAHRAD)
print("  po mutaci na tom místě: %r" % zmut[i:i + 60])
assert "„32 sloupců" not in zmut, "v souboru pořád jsou uvozovky!"


def spust():
    r = subprocess.run([sys.executable, "_analyza/audit2b-cisla-proti-zdroji.py"],
                       capture_output=True, cwd=str(WS))
    return (r.stdout.decode("utf-8", "replace")
            + r.stderr.decode("utf-8", "replace"))


try:
    AGENTS.write_text(zmut, encoding="utf-8", newline="")
    v = spust()
finally:
    AGENTS.write_bytes(orig)
    assert AGENTS.read_bytes() == orig, "AGENTS.md NEVRACEN!"

print()
print("  ── řádky výpisu s AGENTS.md a sloupců ──")
for l in v.splitlines():
    if "AGENTS.md" in l and "sloupc" in l:
        print("   %s" % l.strip()[:170])
print()
for l in v.splitlines():
    if l.startswith("  ROZCHODŮ:") or l.startswith("  shod s živým"):
        print("  %s" % l)

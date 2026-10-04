# -*- coding: utf-8 -*-
"""SONDA 9b — spustí CELÝ nástroj jako podproces a podstrčí mu řádky.

Místo vyřezávání funkcí ze zdroje (což je křehké a už jednou selhalo) se
měří **hotový nástroj**: do dokumentu se vloží zkušební řádky a sleduje se,
jak je nástroj zařadí. Je to `overovani` §7.14 — měřená PODMÍNKA se musí
obrátit, ne jen text změnit.
"""
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "MOZNOSTI-AGENTA.md"          # dokument v JÁDRU, mimo append-only
ORIG = CIL.read_bytes()

VZORKY = [
    "TEST-A: 39 kontrol, 0 selhání",                     # čítač brány (má projít)
    "TEST-B: 23 kontrol). Bez něj nic",                  # čítač brány
    "TEST-C: tabulka mi vyšla jako 0 řádků",             # NENÍ počet
    "TEST-D: má 2 kontrolní vzorky",                     # NENÍ počet
    "TEST-E: 8 dokument správně | Ne",                   # číslo patří jinam
    "TEST-F: celkem 57 dokumentů",                       # seznam brány
]

print("=" * 100)
print("  ZKUŠEBNÍ ŘÁDKY VLOŽENÉ DO %s" % CIL.name)
print("=" * 100)
zmut = ORIG.decode("utf-8") + "\n\n<!-- SONDA -->\n" + "\n".join(VZORKY) + "\n"
try:
    CIL.write_bytes(zmut.encode("utf-8"))
    assert CIL.read_bytes() != ORIG, "MUTACE NEPROBĚHLA"
    r = subprocess.run([sys.executable, "_analyza/audit2b-cisla-proti-zdroji.py"],
                       capture_output=True, cwd=str(WS))
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
finally:
    CIL.write_bytes(ORIG)
    assert CIL.read_bytes() == ORIG, "SOUBOR NEVRÁCEN!"

print()
for radek in v.splitlines():
    if "TEST-" in radek or "MOZNOSTI" in radek:
        print("  %s" % radek.strip()[:150])
print()
for radek in v.splitlines():
    if radek.startswith("  ROZCHODŮ:") or radek.startswith("  shod s živým"):
        print("  %s" % radek)

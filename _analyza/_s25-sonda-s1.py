# -*- coding: utf-8 -*-
"""SONDA 12 — proč sonda v `AGENTS.md` nevychází ani v ROZCHODECH, ani v ZÁZNAMECH.

Vloží sondu do `AGENTS.md`, spustí `audit2b` a vypíše VŠECHNY jeho řádky
s „sloupc" — aby bylo vidět, jestli výskyt zmizel, nebo se jen jinak zařadil.
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
AGENTS = WS / "AGENTS.md"
orig = AGENTS.read_bytes()

SONDA = "| **S1** | sonda: hodnota **„32 sloupců“** |"
t = orig.decode("utf-8")
print("  řádků v AGENTS.md: %d" % len(t.splitlines()))
print("  sonda už tam je?   %s" % (SONDA in t))

zmut = t + "\n" + SONDA + "\n"
assert zmut != t
try:
    AGENTS.write_text(zmut, encoding="utf-8", newline="")
    obsah = AGENTS.read_text(encoding="utf-8")
    assert SONDA in obsah, "SONDA V SOUBORU NENÍ!"
    radek = len(obsah.splitlines())
    print("  sonda vložena na řádek ~%d" % radek)
    r = subprocess.run([sys.executable, "_analyza/audit2b-cisla-proti-zdroji.py"],
                       capture_output=True, cwd=str(WS))
    v = (r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace"))
finally:
    AGENTS.write_bytes(orig)
    assert AGENTS.read_bytes() == orig, "AGENTS.md NEVRACEN!"

print()
print("  ── řádky výpisu se 'sonda' nebo 'S1' ──")
n = 0
for l in v.splitlines():
    if "sonda" in l or "S1" in l:
        n += 1
        print("   %s" % l.strip()[:150])
print("  celkem: %d" % n)
print()
print("  ── řádky výpisu s AGENTS.md a sloupc ──")
for l in v.splitlines():
    if "AGENTS.md" in l and "sloupc" in l:
        print("   %s" % l.strip()[:150])
print()
for l in v.splitlines():
    if l.startswith("  ZMĚŘENO") or l.startswith("  ROZCHODŮ"):
        print("  %s" % l)

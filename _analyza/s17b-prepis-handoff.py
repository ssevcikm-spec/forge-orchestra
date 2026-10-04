# -*- coding: utf-8 -*-
r"""Nahradí §17.11 v `HANDOFF.md` finální verzí (doplněné body 5 a 6)."""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s17b-doplneni.md"

ZAC = "### 17.11 Doplněno na konci session"
puvodni = CIL.read_text(encoding="utf-8")
novy = NOVY.read_text(encoding="utf-8").lstrip("\n")

if puvodni.count(ZAC) != 1:
    print("CHYBA: kotva %r je %d×, potřebuji 1×" % (ZAC, puvodni.count(ZAC)))
    sys.exit(2)

i = puvodni.index(ZAC)
j = len(puvodni)          # §17.11 je POSLEDNÍ oddíl → výřez jde na konec
stary = puvodni[i:]

spojeny = puvodni[:i] + novy
if not spojeny.endswith("\n"):
    spojeny += "\n"
assert spojeny.startswith(puvodni[:i]), "PREDEK SE ZMENIL"
assert spojeny.count(ZAC) == 1, "dva oddily 17.11!"

CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  HANDOFF.md: %d -> %d znaků (%+d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  starý §17.11: %d znaků → nový: %d znaků" % (len(stary), len(novy)))
print("  sha256: %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

KLICE = ["## 8. Vlastní omyly", "### 8f. Omyly PLÁNOVACÍ",
         "## 9. Co už otevřené NENÍ", "## 16. Provedeno 2. 10. 2026",
         "## 17. Ověření práce", "### 17.9", "### 17.11",
         "omyl 50", "| **59** |", "4f3d76c133c4d9c6"]
chybi = [k for k in KLICE if k not in zpet]
print("  kontrolovaných klíčů: %d, chybí: %d" % (len(KLICE), len(chybi)))
for k in chybi:
    print("    CHYBI: %s" % k)
sys.exit(1 if chybi else 0)

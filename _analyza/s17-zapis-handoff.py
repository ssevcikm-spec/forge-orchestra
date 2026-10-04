# -*- coding: utf-8 -*-
"""Připojí nový oddíl do `HANDOFF.md` (bajt na bajt, bez přepisu zbytku).

PROČ SKRIPTEM: `HANDOFF.md` má 1762 řádků a překlep v ruční editaci by smazal
historii. Tenhle nástroj jen PŘIDÁVÁ na konec a před/po ověří:
  * délka vzrostla o očekávaný počet znaků,
  * PŮVODNÍ obsah je stále PREFIXEM nového souboru (nic nezmizelo),
  * hledané klíčové body jsou v novém souboru.
"""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s17-novy-oddil.md"

puvodni = CIL.read_text(encoding="utf-8")
novy = NOVY.read_text(encoding="utf-8")

if "## 17. Ověření práce AKČNÍ session" in puvodni:
    print("CHYBA: oddíl §17 už v HANDOFF.md je — nebudu ho vkládat dvakrát")
    sys.exit(2)

# Oddělovač: původní soubor končí newline, nový oddíl začíná `---`.
spojeny = puvodni.rstrip("\n") + "\n\n" + novy.lstrip("\n")
if not spojeny.endswith("\n"):
    spojeny += "\n"

assert spojeny.startswith(puvodni.rstrip("\n")), "PUVODNI OBSAH NENI PREFIXEM"
CIL.write_bytes(spojeny.encode("utf-8"))

zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"
assert zpet.startswith(puvodni.rstrip("\n")), "PO ZAPISE NENI PUVODNI OBSAH PREFIXEM"

print("  HANDOFF.md: %d -> %d znaků (+%d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  sha256 před: %s" % hashlib.sha256(puvodni.encode("utf-8")).hexdigest()[:16])
print("  sha256 po:   %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

# Nic nezmizelo: klíčové body původního dokumentu.
KLICE = [
    "omyl 50", "## 16. Provedeno 2. 10. 2026", "### 8e. Omyly AKČNÍ session",
    "### 16.7 Úkol F", "### 16.10 Co je NUTNÉ ověřit",
    "## 8. Vlastní omyly", "## 2. Co je OTEVŘENÉ",
    "## 17. Ověření práce AKČNÍ session",
]
chybi = [k for k in KLICE if k not in zpet]
print("  kontrolovaných klíčů: %d, chybí: %d" % (len(KLICE), len(chybi)))
if chybi:
    for k in chybi:
        print("    CHYBI: %s" % k)
    sys.exit(1)
print("  VSE OK — původní obsah zůstal, oddíl §17 přidán")

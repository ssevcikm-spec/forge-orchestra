# -*- coding: utf-8 -*-
"""Připojí §17.11 do `HANDOFF.md` (bajt na bajt, bez přepisu zbytku)."""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s17b-doplneni.md"

puvodni = CIL.read_text(encoding="utf-8")
novy = NOVY.read_text(encoding="utf-8")

if "### 17.11" in puvodni:
    print("CHYBA: §17.11 už tam je — nepřidávám dvakrát")
    sys.exit(2)

spojeny = puvodni.rstrip("\n") + "\n\n" + novy.lstrip("\n")
if not spojeny.endswith("\n"):
    spojeny += "\n"
assert spojeny.startswith(puvodni.rstrip("\n")), "PUVODNI OBSAH NENI PREFIXEM"
CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  HANDOFF.md: %d -> %d znaků (+%d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  sha256: %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

for k in ["## 17. Ověření práce", "### 17.9", "### 17.11",
          "### 8f. Omyly PLÁNOVACÍ", "## 9. Co už otevřené NENÍ",
          "## 16. Provedeno 2. 10. 2026", "omyl 50"]:
    print("  %-28s %s" % (k, "OK" if k in zpet else "CHYBI"))

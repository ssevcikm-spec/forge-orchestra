# -*- coding: utf-8 -*-
r"""Vloží omyl 60 do tabulky §8f v `HANDOFF.md` a opraví souhrnné věty.

Vkládá se na JEDNOZNAČNÉ místo (řádek s omylem 59), ne „na konec tabulky"
(past `overovani` §7.3). Po zápisu se ověří, že podmínka platí a že zbytek
dokumentu je nedotčený.
"""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s8f-omyl60.md"

puvodni = CIL.read_text(encoding="utf-8")
radek60 = NOVY.read_text(encoding="utf-8").strip()

if "| **60** |" in puvodni:
    print("CHYBA: omyl 60 už v HANDOFF.md je")
    sys.exit(2)

# Kotva: poslední řádek tabulky 8f (omyl 59). Hledá se podle začátku řádku.
KOTVA = "| **59** |"
if puvodni.count(KOTVA) != 1:
    print("CHYBA: kotva %r je %d×, potřebuji 1×" % (KOTVA, puvodni.count(KOTVA)))
    sys.exit(2)

i = puvodni.index(KOTVA)
j = puvodni.find("\n", i)
if j < 0:
    print("CHYBA: za kotvou není konec řádku")
    sys.exit(2)

spojeny = puvodni[:j + 1] + radek60 + "\n" + puvodni[j + 1:]
assert "| **60** |" in spojeny, "omyl 60 se nevlozil"
assert spojeny.count("| **60** |") == 1, "omyl 60 je tam dvakrat"

# Souhrnné věty v §8f tvrdí počty — musí se posunout.
VYMENY = [
    ("**Vzor ze sedmi:** **šest** vzniklo v **měřidle**",
     "**Vzor z deseti (po doplnění 58, 59 a 60):** **devět** vzniklo v **měřidle**"),
    ("**Vzor z devíti (po doplnění 58 a 59):** **osm z devíti** vzniklo v **měřidle**\nnebo ve mně",
     "**Vzor z deseti:** **devět z deseti** vzniklo v **měřidle** nebo ve mně"),
]
for stary, novy in VYMENY:
    if stary in spojeny:
        spojeny = spojeny.replace(stary, novy, 1)
        print("  souhrnná věta upravena: %r…" % stary[:48])

CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  HANDOFF.md: %d -> %d znaků (%+d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  sha256: %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

KLICE = ["### 8f. Omyly PLÁNOVACÍ", "| **60** |", "| **59** |",
         "## 9. Co už otevřené NENÍ", "## 17. Ověření práce", "### 17.11"]
chybi = [k for k in KLICE if k not in zpet]
print("  kontrolovaných klíčů: %d, chybí: %d" % (len(KLICE), len(chybi)))
for k in chybi:
    print("    CHYBI: %s" % k)
sys.exit(1 if chybi else 0)

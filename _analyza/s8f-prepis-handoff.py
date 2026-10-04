# -*- coding: utf-8 -*-
r"""Nahradí oddíl `8f` v `HANDOFF.md` opravenou verzí (omyly 58 a 59).

PROČ NAHRAZOVAT A NE VKLÁDAT: omyl 58 a 59 vznikl **až po** prvním zápisu §8f
(doplnění skriptu a přegenerování inventáře). Vkládat druhý `### 8f` by
znamenalo **dvě sekce téhož jména** — a to je přesně ta vada, kterou
`AGENTS.md` popisuje u „dvou čítačů téhož jména".

Bezpečnost: nahrazuje se **výřez mezi dvěma jednoznačnými kotvami**
(`### 8f.` … `## 9.`), ne „odhadnutý konec sekce" (past `overovani` §7.3).
Před i po se ověří, že **zbytek dokumentu je bajt na bajt stejný**.
"""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s8f-novy-oddil.md"

ZAC = "### 8f. Omyly PLÁNOVACÍ"
KON = "## 9. Co už otevřené NENÍ"

puvodni = CIL.read_text(encoding="utf-8")
novy = NOVY.read_text(encoding="utf-8").lstrip("\n")

for kotva in (ZAC, KON):
    if puvodni.count(kotva) != 1:
        print("CHYBA: kotva %r je v souboru %d×, potřebuji právě 1×"
              % (kotva, puvodni.count(kotva)))
        sys.exit(2)

i = puvodni.index(ZAC)
j = puvodni.index(KON)
stary_vyrez = puvodni[i:j]

spojeny = puvodni[:i] + novy + puvodni[j:]
if not spojeny.endswith("\n"):
    spojeny += "\n"
assert spojeny.startswith(puvodni[:i]), "PREDEK SE ZMENIL"
assert spojeny.endswith(puvodni[j:]), "ZBYTEK SE ZMENIL"
assert "### 8f. Omyly PLÁNOVACÍ" in spojeny
assert spojeny.count(ZAC) == 1, "dva oddily 8f!"

CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  HANDOFF.md: %d -> %d znaků (%+d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  starý výřez 8f: %d znaků → nový: %d znaků" % (len(stary_vyrez), len(novy)))
print("  sha256: %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

KLICE = ["## 8. Vlastní omyly", "### 8b.", "### 8c.", "### 8d.", "### 8e.",
         "### 8f. Omyly PLÁNOVACÍ", "## 9. Co už otevřené NENÍ",
         "## 16. Provedeno 2. 10. 2026", "## 17. Ověření práce",
         "### 17.11", "omyl 50", "| **59** |"]
chybi = [k for k in KLICE if k not in zpet]
print("  kontrolovaných klíčů: %d, chybí: %d" % (len(KLICE), len(chybi)))
for k in chybi:
    print("    CHYBI: %s" % k)
sys.exit(1 if chybi else 0)

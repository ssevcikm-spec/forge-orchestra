# -*- coding: utf-8 -*-
r"""Vloží oddíl `8f` do `HANDOFF.md` PŘED `## 9. Co už otevřené NENÍ`.

PROČ VKLÁDAT, A NE PŘIPOJIT: `8f` patří k omylům (`§8`), ne na konec —
kdo hledá vlastní omyly, čte §8. Vkládá se na JEDNOZNAČNÉ místo (nadpis
`## 9.`), ne „na konec sekce" (past z `overovani` §7.3).
"""

import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "HANDOFF.md"
NOVY = WS / "_analyza" / "s8f-novy-oddil.md"
KOTVA = "## 9. Co už otevřené NENÍ"

puvodni = CIL.read_text(encoding="utf-8")
novy = NOVY.read_text(encoding="utf-8")

if "### 8f. Omyly PLÁNOVACÍ" in puvodni:
    print("CHYBA: oddíl 8f už tam je — nevkládám dvakrát")
    sys.exit(2)
if puvodni.count(KOTVA) != 1:
    print("CHYBA: kotva %r je v souboru %d×, potřebuji právě 1×"
          % (KOTVA, puvodni.count(KOTVA)))
    sys.exit(2)

i = puvodni.index(KOTVA)
spojeny = puvodni[:i] + novy.lstrip("\n") + puvodni[i:]

# POJISTKA (past §7.14): měřená PODMÍNKA musí po zápisu platit.
assert "### 8f. Omyly PLÁNOVACÍ" in spojeny, "oddil 8f v novem textu neni"
assert spojeny.replace(novy.lstrip("\n"), "") == puvodni, \
    "VLOZENIM SE ZMENIL NECO JINY NEZ VLOZENY TEXT"

CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  HANDOFF.md: %d -> %d znaků (+%d)"
      % (len(puvodni), len(zpet), len(zpet) - len(puvodni)))
print("  sha256 po: %s" % hashlib.sha256(zpet.encode("utf-8")).hexdigest()[:16])

# Nic nezmizelo: klíčové body obou částí dokumentu.
KLICE = [
    "## 8. Vlastní omyly", "### 8b.", "### 8c.", "### 8d.", "### 8e.",
    "### 8f. Omyly PLÁNOVACÍ", "## 9. Co už otevřené NENÍ",
    "## 16. Provedeno 2. 10. 2026", "## 17. Ověření práce AKČNÍ session",
    "omyl 50", "### 16.10 Co je NUTNÉ ověřit",
]
chybi = [k for k in KLICE if k not in zpet]
print("  kontrolovaných klíčů: %d, chybí: %d" % (len(KLICE), len(chybi)))
if chybi:
    for k in chybi:
        print("    CHYBI: %s" % k)
    sys.exit(1)
print("  VSE OK — 8f vložen, zbytek dokumentu nedotčen")

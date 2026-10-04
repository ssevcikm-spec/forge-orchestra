# -*- coding: utf-8 -*-
"""AUDIT 4 — CO NEPATŘÍ NA SVÉ MÍSTO (místo, ne obsah).

Zadání (plán, fáze 4): znalost je správná, ale leží na špatném místě — a proto
ji **nikdo nenajde** nebo **zestárne**.

Kritérium (plán): *„Najde to session, která to bude potřebovat — a to bez toho,
aby jí to někdo řekl?"*

Ten skript to mění na měřitelné tři otázky:
  1. **Cituje to jádro?** (`odkazu_v_jadru > 0`)
  2. **Je to v RUČNÍM seznamu brány?** (ne jen v projití složky)
  3. **Říká to samo o sobě, čím je a do kdy platí?** (hlavička)

Když je odpověď na všechny tři NE, dokument je na špatném místě: existuje,
ale session na něj nenarazí.
"""

import json
import pathlib
import sys
from collections import Counter

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
inv = json.loads((WS / "_analyza" / "audit-inventar.json").read_text(encoding="utf-8"))
D = inv["dokumenty"]

SKUPINY = [
    ("PLAN-* (plán, nebo archiv plánů?)", lambda z: z["cesta"].startswith("PLAN-")),
    ("ANALYZA-* (analýza, nebo snapshot?)", lambda z: z["cesta"].startswith("ANALYZA-")),
    ("IMPLEMENTACE-* (zadání, nebo záznam?)", lambda z: z["cesta"].startswith("IMPLEMENTACE-")),
    ("_analyza\\*.md (pracovní stůl, nebo skladiště?)",
     lambda z: z["cesta"].startswith("_analyza\\") and z["cesta"].count("\\") == 1),
]

print("=" * 100)
print("AUDIT 4 — CO JE NA ŠPATNÉM MÍSTĚ")
print("=" * 100)
print()
print("  %-52s %8s %6s %5s %-22s %s"
      % ("dokument", "bajtů", "řádků", "jádro", "ruční brána", "hlavička"))
print("  " + "-" * 96)

for titulek, filtr in SKUPINY:
    skupina = [z for z in D if filtr(z)]
    if not skupina:
        continue
    print()
    print("  ── %s — %d dokumentů, %d bajtů" %
          (titulek, len(skupina), sum(z["bajtu"] or 0 for z in skupina)))
    for z in sorted(skupina, key=lambda x: -(x["bajtu"] or 0)):
        print("  %-52s %8d %6s %5d %-22s %s"
              % (z["cesta"][:52], z["bajtu"], z["radku"], z["odkazu_v_jadru"],
                 z["otevira_brana"][:22], z["hlavicka"][:26]))

# ── Zvláštní kandidáti z plánu §4 ──────────────────────────────────────────
print()
print("=" * 100)
print("  ZVLÁŠTNÍ KANDIDÁTI (plán §4)")
print("=" * 100)
for jmeno in ("MOZNOSTI-AGENTA.md", "OTEVRENA-TEMATA.md", "SKILLY-AKTUALIZACE.md"):
    z = next((x for x in D if x["cesta"] == jmeno), None)
    if not z:
        print("  %s — NENALEZEN v inventáři" % jmeno)
        continue
    print()
    print("  %s  (%d B, %s řádků)" % (jmeno, z["bajtu"], z["radku"]))
    print("      druh podle dokumentu : %s  (určeno z: %s)" % (z["druh"], z["druh_odkud"]))
    print("      citováno v jádru     : %d×  (%s)" % (z["odkazu_v_jadru"], z["odkazu_v_jadru_kdo"][:60]))
    print("      v ručním seznamu brány: %s" % z["otevira_brana"])
    print("      hlavička             : %s" % z["hlavicka"])
    print("      naposledy změněn     : %s" % z["zmenen"])

# ── _analyza: kolik z toho je zapojené ────────────────────────────────────
print()
print("=" * 100)
print("  _analyza\\ — PRACOVNÍ STŮL, NEBO SKLADIŠTĚ?")
print("=" * 100)
analyza = [z for z in D if z["cesta"].startswith("_analyza\\") and z["cesta"].count("\\") == 1]
v_rucni = [z for z in analyza if z["otevira_brana"] != "—"]
citovane = [z for z in analyza if z["odkazu_v_jadru"] > 0]
print("  .md souborů v _analyza (bez podsložek): %d" % len(analyza))
print("  z toho v RUČNÍM seznamu nějaké brány  : %d" % len(v_rucni))
print("  z toho citovaných v jádru             : %d" % len(citovane))
print("  druhy (z názvu):")
for druh, n in Counter(z["druh"] for z in analyza).most_common():
    print("      %-28s %d" % (druh, n))

# Skripty vs dokumenty
skripty = [p for p in (WS / "_analyza").glob("*")
           if p.is_file() and p.suffix in (".py", ".mjs")]
print()
print("  skriptů (.py/.mjs) v _analyza (bez podsložek): %d" % len(skripty))

# -*- coding: utf-8 -*-
"""Pomocná sonda k inventáři: které KOŘENOVÉ dokumenty jádro necituje.

PROČ: plán auditu tvrdí „dokumenty nikde nezmíněné: 4" (ANALYZA-VYVOJ-APLIKACI-A-HER,
README, RESEARCH-public-repos, ZADANI-CREATOR-INDIKATORY). Inventář měří jiná
čísla — a rozdíl je potřeba vysvětlit, ne přejít (AGENTS.md: „než označíš cizí
číslo za nepravdivé, zkus ho zopakovat týmž postupem").

Vypíše i KDE přesně se to jméno v jádru bere, aby bylo vidět, jestli je to
skutečná zmínka, nebo náhodný podřetězec.
"""

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
JADRO = ["AGENTS.md", "HANDOFF.md", "PREDAVANI-SESSION.md", "KRONIKA-PROJEKTU.md",
         "PLAN-DALSI-KROK.md", "NEXT-SESSION-INSTRUKCE.md", "MOZNOSTI-AGENTA.md",
         "OTEVRENA-TEMATA.md"]

inv = json.loads((WS / "_analyza" / "audit-inventar.json").read_text(encoding="utf-8"))
koren = [z for z in inv["dokumenty"] if z["kategorie"] == "koren"]

print("=" * 96)
print("KOŘENOVÉ DOKUMENTY PODLE ZMÍNEK V JÁDRU  (jádro = %d dokumentů)" % len(JADRO))
print("=" * 96)
print("  %-52s %6s  %s" % ("dokument", "jádro", "kde (soubor×počet)"))
print("  " + "-" * 92)
for z in sorted(koren, key=lambda x: (x["odkazu_v_jadru"], x["cesta"])):
    print("  %-52s %6d  %s" % (z["cesta"][:52], z["odkazu_v_jadru"],
                               z["odkazu_v_jadru_kdo"][:38]))
print()

# ── Kontrola tvrzení plánu: čtyři „nikde nezmíněné" ────────────────────────
TVRZENE_SIROTKY = ["ANALYZA-VYVOJ-APLIKACI-A-HER.md", "README.md",
                   "RESEARCH-public-repos.md", "ZADANI-CREATOR-INDIKATORY.md"]
obsahy = {j: (WS / j).read_text(encoding="utf-8") for j in JADRO}

print("=" * 96)
print("KONTROLA TVRZENÍ PLÁNU: „tyhle čtyři nejsou zmíněné nikde v jádru\"")
print("=" * 96)
for jmeno in TVRZENE_SIROTKY:
    kmen = pathlib.Path(jmeno).stem
    nalezy = []
    for j, s in obsahy.items():
        if s.count(kmen):
            # Vypiš i KONTEXT, aby bylo vidět, je-li to zmínka nebo podřetězec.
            for m in re.finditer(re.escape(kmen), s):
                radek = s[:m.start()].count("\n") + 1
                kontext = s[max(0, m.start() - 45):m.start() + len(kmen) + 30]
                kontext = kontext.replace("\n", " ")
                nalezy.append((j, radek, kontext))
    print()
    print("  %s  (%d znaků)" % (jmeno, len(obsahy.get(jmeno, ""))))
    if not nalezy:
        print("      → V JÁDRU SE OPRAVDU NEVYSKYTUJE ANI JEDNOU")
    else:
        for j, radek, kontext in nalezy[:6]:
            print("      %s:%d  …%s…" % (j, radek, kontext))
        if len(nalezy) > 6:
            print("      … a dalších %d výskytů" % (len(nalezy) - 6))

# -*- coding: utf-8 -*-
"""AUDIT 3 — NADBYTEČNOST: tatáž znalost na víc místech (+ kolik z HANDOFFu je historie).

Zadání (plán, fáze 3): pro každé pravidlo (definované vzorem) vypsat VŠECHNA
místa a určit jednu autoritu. Duplikát se nemá mazat, ale zkrátit na odkaz —
protože **duplikát zestárne jinde než autorita**.

Navíc (plán §2.3): `HANDOFF.md` je append-only a roste. Otázka zní, **kolik
z něj je ještě živé a kolik je příběh**. Tenhle skript to změří po oddílech.

⚠ Pozor na výklad: „víc výskytů" NENÍ automaticky vada. Pravidlo se na víc
místech cituje i proto, že si ho má přečíst ten, kdo zrovna čte ten dokument.
Nález je jen tam, kde **duplikát nese číslo nebo stav** — ten zestárne.
"""

import pathlib
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent

DOKUMENTY = ([WS / "AGENTS.md", WS / "HANDOFF.md", WS / "PREDAVANI-SESSION.md",
              WS / "KRONIKA-PROJEKTU.md", WS / "PLAN-DALSI-KROK.md",
              WS / "NEXT-SESSION-INSTRUKCE.md", WS / "MOZNOSTI-AGENTA.md",
              WS / "OTEVRENA-TEMATA.md", WS / "SKILLY-AKTUALIZACE.md",
              WS / "JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md"]
             + sorted((WS / "_analyza").glob("*.md"))
             + sorted(pathlib.Path.home().glob(".dsh/skills/*/SKILL.md")))

# Pravidla a vzory, která plán auditu označil za opakovaná (a pár dalších).
PRAVIDLA = [
    ("přegeneruj inventář", r"hl-neanglicky-v-kodu\.py|přegener\w*\s+inventář|inventář je zastaral"),
    ("83 klíčových bodů", r"83/83|\b83\b\s*(?:klíč|bod)"),
    ("brána musí umět spadnout", r"mutačn\w+\s+test|umět spadnout|nemá jak selhat|slepá brána"),
    ("S27 ruční seznam", r"S27|ruční seznam|projití složky"),
    ("nesmí zmizet z handoffu", r"nesmí zmizet|nic nesmí zmizet"),
    ("N9 čísla v AGENTS", r"N9|32 sloupců|přeměřit"),
    ("datum spotřeby", r"DATUM SPOTŘEBY|datum spotřeby"),
    ("dvě kopie se stejným hashem", r"obě kopie|shodný hash|kontrola-driftu"),
]


def main() -> int:
    obsahy = {}
    for f in DOKUMENTY:
        try:
            obsahy[f] = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue

    # ── 1. Duplikace pravidel ──────────────────────────────────────────────
    print("=" * 96)
    print("AUDIT 3 — NADBYTEČNOST PRAVIDEL")
    print("=" * 96)
    print("  prohledáno dokumentů: %d" % len(obsahy))
    print()
    for jmeno, vzor in PRAVIDLA:
        mista = []
        for f, s in obsahy.items():
            n = len(re.findall(vzor, s, re.I))
            if n:
                popis = str(f.relative_to(WS)) if WS in f.parents else "skill: " + f.parent.name
                mista.append((popis, n))
        mista.sort(key=lambda x: -x[1])
        print("  %-28s %2d výskytů v %2d dokumentech" % (jmeno, sum(n for _, n in mista),
                                                         len(mista)))
        for popis, n in mista[:6]:
            print("        %-46s %d×" % (popis[:46], n))
        if len(mista) > 6:
            print("        … a dalších %d dokumentů" % (len(mista) - 6))
        print()

    # ── 2. Kolik z HANDOFFu je historie ────────────────────────────────────
    h = obsahy.get(WS / "HANDOFF.md")
    if not h:
        print("  HANDOFF.md se nepodařilo přečíst — oddíly se neměří")
        return 0
    radky = h.splitlines()
    oddily = [(i, L) for i, L in enumerate(radky) if re.match(r"^## ", L)]
    print("=" * 96)
    print("  HANDOFF.md — KOLIK JE ŽIVÝ STAV A KOLIK PŘÍBĚH")
    print("=" * 96)
    print("  celkem řádků: %d, oddílů: %d" % (len(radky), len(oddily)))
    print()
    print("  %-58s %7s %7s" % ("oddíl", "řádků", "% z celku"))
    print("  " + "-" * 76)
    for idx, (i, L) in enumerate(oddily):
        konec = oddily[idx + 1][0] if idx + 1 < len(oddily) else len(radky)
        n = konec - i
        print("  %-58s %7d %6.1f%%" % (L[3:60], n, 100.0 * n / len(radky)))
    posledni = len(radky) - oddily[-1][0] if oddily else len(radky)
    print("  " + "-" * 76)
    print("  POSLEDNÍ oddíl („%s…“): %d řádků = %.1f %% dokumentu"
          % (oddily[-1][1][3:34], posledni, 100.0 * posledni / len(radky)))
    print("  ZBYTEK (1–%d): %d řádků = %.1f %% dokumentu"
          % (len(oddily) - 1, len(radky) - posledni,
             100.0 * (len(radky) - posledni) / len(radky)))
    print()
    print("  → Agent, který potřebuje ZNÁT STAV, musí přečíst celý dokument,")
    print("    protože nepozná, kde stav končí a historie začíná (oddíly jsou")
    print("    číslované chronologicky, ale bez data v nadpisu by to nešlo).")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
"""Ověření tvrzení, na kterých stojí ZADANI-DOKONCENI-AUDITU.md.

PROČ SAMOSTATNÝ SKRIPT: zadání tvrdí konkrétní čísla („`40 sloupců` je
v `AGENTS.md` jednou", „`21 granul` je v `HANDOFF.md` na deseti místech").
Když ta čísla nejsou pravda, zadání lže — a to je přesně vada, kterou audit
vytýká `NEXT-SESSION-INSTRUKCE.md` (nález R2).

⚠ PROČ NE `python -c`: české znaky v argumentu PowerShell rozbijí
(`dsh-prostredi` §3d). Proto soubor.

Použití:  python _analyza/audit7-overeni-zadani.py
Návrat:   1 = některé tvrzení zadání nesedí (a je VIDĚT které)
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
agents = (WS / "AGENTS.md").read_text(encoding="utf-8")
handoff = (WS / "HANDOFF.md").read_text(encoding="utf-8")
kronika = (WS / "KRONIKA-PROJEKTU.md").read_text(encoding="utf-8")

problemy = []


def zkontroluj(tvrzeni, skutecnost, ocekavano, kde):
    ok = skutecnost == ocekavano
    print("  %-4s %s" % ("OK" if ok else "CHYBA", tvrzeni))
    print("        %s → naměřeno %s, zadání tvrdí %s"
          % (kde, skutecnost, ocekavano))
    if not ok:
        problemy.append(tvrzeni)
    return ok


def vyskyty(text, vzor):
    return [(text[:m.start()].count("\n") + 1, m.group(0))
            for m in re.finditer(re.escape(vzor), text)]


print("=" * 92)
print("OVĚŘENÍ TVRZENÍ ZADÁNÍ  (%s)" % WS.name)
print("=" * 92)
print()

# ── Úkol 2: kotevní řetězec pro ag-mutace.py ──────────────────────────────
print("ÚKOL 2 — kotevní řetězec musí být v dokumentu PRAVĚ JEDNOU")
a40 = vyskyty(agents, "40 sloupců")
a39 = vyskyty(agents, "39 sloupců")
zkontroluj("v AGENTS.md je `40 sloupců` právě 1×", len(a40), 1, "AGENTS.md")
for r, _ in a40:
    print("        řádek %d" % r)
zkontroluj("v AGENTS.md je `39 sloupců` 0× (proto dnešní mutace neproběhne)",
           len(a39), 0, "AGENTS.md")
print()

# ── Úkol 4: kolik míst tvrdí 21 a kolik 22 ────────────────────────────────
print("ÚKOL 4 — kolik míst v HANDOFF.md tvrdí který počet granulí")
h21 = vyskyty(handoff, "21 granul")
h22 = vyskyty(handoff, "22 granul")
print("        `21 granul` → %d míst: %s" % (len(h21), [r for r, _ in h21]))
print("        `22 granul` → %d míst: %s" % (len(h22), [r for r, _ in h22]))
print()
print("        ⚠ ROZPOR JE UVNITŘ `HANDOFF.md`: starší oddíly tvrdí 21,")
print("          novější (§22) už 22. Není to tedy jedna vada, ale DVĚ:")
print("          (a) historické záznamy — tam je 21 SPRÁVNĚ (A2),")
print("          (b) dnešní stav — ten musí být 22 nebo se značkou času.")
print()

# Ve kterém oddílu ta místa leží? (aby se dalo rozlišit (a) od (b))
radky = handoff.splitlines()
oddily = [(i + 1, L) for i, L in enumerate(radky) if L.startswith("## ")]


def oddil_pro(radek):
    jmeno = "?"
    for i, L in oddily:
        if i <= radek:
            jmeno = L[3:60]
        else:
            break
    return jmeno


print("        Kde přesně (oddíl, do kterého místo patří):")
for r, _ in h21:
    print("          řádek %-5d  § %s" % (r, oddil_pro(r)))
print()
for r, _ in h22:
    print("          řádek %-5d  § %s   (souhlasí s živým zdrojem)" % (r, oddil_pro(r)))
print()

# ── Zdroj: kolik granul je živě ───────────────────────────────────────────
import json
roadmap = WS / "games" / "uo-shadows" / ".forge" / "roadmap.json"
granul = None
if roadmap.is_file():
    d = json.loads(roadmap.read_text(encoding="utf-8"))
    granul = len(d.get("grains", d))
print("ŽIVÝ ZDROJ — `roadmap.json` → `grains`: %s" % granul)
zkontroluj("živých granul je 22", granul, 22, "roadmap.json")
print()

# ── Úkol 2b: je ag-mutace.py v g3-brany.py? ───────────────────────────────
g3 = (WS / "_analyza" / "g3-brany.py").read_text(encoding="utf-8")
print("ÚKOL 2b — mutační testy, které `g3-brany.py` SPOUŠTÍ:")
for t in ("ag-mutace", "a1-a2-mutace", "a3-mutace", "n8-mutace",
          "zadani-mutace", "mutace-testu", "h17-mutace"):
    print("        %-18s v g3: %s" % (t, "ANO" if t in g3 else "NE"))
zkontroluj("ag-mutace.py NENÍ v g3-brany.py (proto exit 1 nikdo nevidí)",
           "ag-mutace" in g3, False, "g3-brany.py")
print()

# ── Souhrn ────────────────────────────────────────────────────────────────
print("=" * 92)
if problemy:
    print("  ZADÁNÍ JE NA %d MÍSTĚ NEPŘESNÉ:" % len(problemy))
    for p in problemy:
        print("      - %s" % p)
else:
    print("  Všechna ověřená tvrzení zadání SEDÍ na skutečnost.")
print("=" * 92)
sys.exit(1 if problemy else 0)

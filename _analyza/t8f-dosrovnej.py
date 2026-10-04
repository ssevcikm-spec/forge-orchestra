# -*- coding: utf-8 -*-
r"""Dosrovna posledni ctyri zminky stareho poctu omylu (74 -> 75, osm -> devet)."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
PLAN = WS / "PLAN-DALSI-KROK.md"

z = ZADANI.read_text(encoding="utf-8")
p = PLAN.read_text(encoding="utf-8")

zmeny_z = [
    ("(74 omylů, NE 66)", "(75 omylů, NE 66)"),
    ("**74 omylů, 17 nálezů, 17 sessions, 15 odkazů**",
     "**75 omylů, 17 nálezů, 17 sessions, 15 odkazů**"),
    ("tahle session naměřila **osm** omylů (§8h)", "tahle session naměřila **devět** omylů (§8h)"),
]
zmeny_p = [
    ("**74 omylů, 17 nálezů, 17 sessions**", "**75 omylů, 17 nálezů, 17 sessions**"),
]

for stary, novy in zmeny_z:
    assert z.count(stary) == 1, "v zadani: %r je %dx" % (stary[:50], z.count(stary))
    z = z.replace(stary, novy, 1)
    print("OK  zadani: %s" % novy[:60])
for stary, novy in zmeny_p:
    assert p.count(stary) == 1, "v planu: %r je %dx" % (stary[:50], p.count(stary))
    p = p.replace(stary, novy, 1)
    print("OK  plan:   %s" % novy[:60])

# Kontrola: nikde uz nema zustat stary pocet u omylu.
for jmeno, text in (("zadani", z), ("plan", p)):
    zbyle = [i + 1 for i, L in enumerate(text.splitlines())
             if "74 omyl" in L or "osm** omylů" in L or "58 = 78" in L]
    assert not zbyle, "%s: zustaly stare pocty na radcich %s" % (jmeno, zbyle)
    print("OK  %s: zadne stare pocty" % jmeno)

ZADANI.write_bytes(z.encode("utf-8"))
PLAN.write_bytes(p.encode("utf-8"))
assert ZADANI.read_text(encoding="utf-8") == z and PLAN.read_text(encoding="utf-8") == p
print()
print("HOTOVO — oba soubory zapsany a overeny ctenim z disku")

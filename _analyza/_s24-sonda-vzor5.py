# -*- coding: utf-8 -*-
"""SONDA 5 — který vzor je SPRÁVNÝ? Měří se na všech reálných tvarech.

Místo hádání (a místo dalšího slepého kola) se **každý kandidátní vzor** zkusí
na **všech** tvarech slova, které v dokumentech opravdu jsou. Vzory se píšou
**ASCII escape sekvencemi**, aby je nerozbila příkazová řádka
(`dsh-prostredi` §3d).
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = (WS / "HANDOFF.md").read_text(encoding="utf-8")
A = (WS / "AGENTS.md").read_text(encoding="utf-8")
oba = H + "\n" + A

KANDIDATI = {
    "puvodni  (\\d+)\\s+granul": r"(\d+)\s+granul",
    "tolerantni (jen hvezdicky)": r"(\d+)\s*\**\s*granul",
    "tolerantni + konec slova": r"(\d+)\s*\**\s*granul\**\s*(?:[\u00edi]|\u0435|ch|\b)",
}

# reálné tvary: vezmi okolí každého výskytu 'granul' v obou dokumentech
tvary = {}
for m in re.finditer(r"\d+\s*\**\s*granul\S{0,8}", oba):
    tvary.setdefault(m.group(0), 0)
    tvary[m.group(0)] += 1

print("REÁLNÉ TVARY v HANDOFF.md + AGENTS.md (%d různých):" % len(tvary))
for t, n in sorted(tvary.items(), key=lambda kv: -kv[1]):
    print("   %-34s %3d×" % (repr(t), n))

print("\nVÝSLEDKY KANDIDÁTŮ:")
for jmeno, vzor in KANDIDATI.items():
    rx = re.compile(vzor)
    chycene = {}
    for t in tvary:
        ok = bool(rx.search(t))
        chycene[t] = ok
    pocet = sum(1 for v in chycene.values() if v)
    print("\n   %s" % jmeno)
    print("      chytí %d z %d tvarů" % (pocet, len(tvary)))
    for t, ok in sorted(chycene.items(), key=lambda kv: -tvary[kv[0]]):
        print("         %s %-32s %3d×" % ("OK " if ok else "   ", repr(t), tvary[t]))

print("\nKOLIK VÝSKYTŮ V CELÉM HANDOFF.md:")
for jmeno, vzor in KANDIDATI.items():
    print("   %-30s %d" % (jmeno, len(list(re.compile(vzor).finditer(H)))))

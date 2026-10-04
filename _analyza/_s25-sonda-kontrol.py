# -*- coding: utf-8 -*-
"""SONDA 2 (jednorázová) — jaké hodnoty u „N kontrol" jsou v jádru a kde.

PROČ: než zavedu registr „kolik kontrol hlásí která brána", musím vědět,
KTERÉ hodnoty se v dokumentech vůbec vyskytují. Jinak bych stavěl registr
naslepo a mohl jím umlčet skutečné rozchody (`overovani` §9.6).
"""
import collections
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
JADRO = ["AGENTS.md", "HANDOFF.md", "PREDAVANI-SESSION.md", "KRONIKA-PROJEKTU.md",
         "PLAN-DALSI-KROK.md", "NEXT-SESSION-INSTRUKCE.md", "MOZNOSTI-AGENTA.md",
         "OTEVRENA-TEMATA.md"]

VZOR = re.compile(r"(\d+)\s+kontrol")

c = collections.Counter()
kde = collections.defaultdict(list)
for j in JADRO:
    p = WS / j
    if not p.is_file():
        continue
    s = p.read_text(encoding="utf-8")
    for i, l in enumerate(s.splitlines(), 1):
        for m in VZOR.finditer(l):
            c[int(m.group(1))] += 1
            kde[int(m.group(1))].append((j, i, l.strip()[:120]))

print("=" * 96)
print("  VŠECHNY HODNOTY u „N kontrol“ V JÁDRU")
print("=" * 96)
for k, v in sorted(c.items()):
    print("   %5d  %2dx" % (k, v))

print()
print("=" * 96)
print("  KDE JE KTERÁ HODNOTA (pro rozhodnutí, který zdroj ji vydal)")
print("=" * 96)
for k in sorted(c):
    print()
    print("  ── %d ──" % k)
    for j, i, l in kde[k]:
        print("     %-24s :%-5d %s" % (j, i, l))

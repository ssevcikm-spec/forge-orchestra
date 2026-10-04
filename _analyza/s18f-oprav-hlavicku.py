# -*- coding: utf-8 -*-
r"""Opraví hlavičku `NEXT-SESSION-INSTRUKCE.md` po doplnění omylu 68 a L13.

PROČ: hlavička tvrdila „62 omylů" a „12 poučení" — obojí přestalo platit
**vlastní prací téhle session** (omyl 68 se přidal na konci, L13 taky).
Zapsat do zadání číslo, které si odporuje s `KRONIKA-PROJEKTU.md`, je přesně
to, co `AGENTS.md` zakazuje („číslo bez postupu se nedá ověřit").

Použití:  python _analyza\s18f-oprav-hlavicku.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ZAPIS = "--zapis" in sys.argv

t = ZADANI.read_text(encoding="utf-8")

# Dvojice (co je v souboru, čím to nahradit). Hledá se na KRÁTKÝCH ASCII
# kotvách, aby se do skriptu nemusely psát české uvozovky (ty rozbily
# předchozí verzi — past z `dsh-prostredi` §3d).
ZMENY = [
    ("15 sessions, **62 omyl", "15 sessions, **63 omyl"),
    ("v měřidle), 12 nález", "v měřidle), 12 nález"),
    ("(H1–H12), 12 poučení", "(H1–H12), 13 poučení"),
    ("omyly 61–67)", "omyly 61–68)"),
    ("**62 omylů**", "**63 omylů**"),
]

print("=" * 78)
print("OPRAVA HLAVIČKY ZADÁNÍ — čísla musí odpovídat kronice")
print("=" * 78)
for stary, novy in ZMENY:
    n = t.count(stary)
    print("  %-34s %dx -> %s" % (repr(stary)[:34], n, repr(novy)[:30]))

novy_text = t
for stary, novy in ZMENY:
    if stary != novy:
        novy_text = novy_text.replace(stary, novy)

if novy_text == t:
    print()
    print("  beze změny (hlavička už sedí)")
else:
    assert novy_text != t, "MUTACE NEPROBĚHLA"
    assert "62 omyl" not in novy_text, "PODMÍNKA POŘÁD PLATÍ (62 omylů tam je)"
    assert "63 omyl" in novy_text, "nové číslo se nevepsalo"
    assert "13 poučení" in novy_text, "poučení se neopravila"
    if ZAPIS:
        ZADANI.write_bytes(novy_text.encode("utf-8"))
        print()
        print("  ZAPSÁNO: %d -> %d B"
              % (len(t.encode("utf-8")), len(novy_text.encode("utf-8"))))
    else:
        print()
        print("  (dry-run — spusť s --zapis)")

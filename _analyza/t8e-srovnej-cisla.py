# -*- coding: utf-8 -*-
r"""Srovna cisla v zadani a planu po pridani omylu 80 (74 -> 75 omylu)."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ZMENY = {
    "NEXT-SESSION-INSTRUKCE.md": [
        ("**74 omylů** (58 = 78 % v měřidle)", "**75 omylů** (59 = 79 % v měřidle)"),
        ("**§8h** (vlastní omyly **72–79**)", "**§8h** (vlastní omyly **72–80**)"),
        ("`kronika-kontrola.py`            # musí vyjít exit 0 (74 omylů, NE 66)",
         "`kronika-kontrola.py`            # musí vyjít exit 0 (75 omylů, NE 66)"),
        ("**omylů je 74** (ne 66)", "**omylů je 75** (ne 66)"),
        ("přidal **osm** omylů a **všech osm bylo\nv měřidle**",
         "přidala **devět** omylů a **všech devět bylo\nv měřidle**"),
    ],
    "PLAN-DALSI-KROK.md": [
        ("**74 omylů, z toho 58 (78 %) v měřidle**", "**75 omylů, z toho 59 (79 %) v měřidle**"),
        ("ani po 74\nzáznamech. Tahle session k tomu přidala **osm** omylů a **všech osm bylo\nv měřidle**",
         "ani po 75\nzáznamech. Tahle session k tomu přidala **devět** omylů a **všech devět bylo\nv měřidle**"),
        ("a **blok 8h má 8 z 8 (100 %)**", "a **blok 8h má 9 z 9 (100 %)**"),
    ],
}

for jmeno, zmeny in ZMENY.items():
    P = WS / jmeno
    s = P.read_text(encoding="utf-8")
    print("── %s ──" % jmeno)
    for stary, novy in zmeny:
        if stary not in s:
            print("   --  vzor uz je srovnany: %r" % stary[:50])
            continue
        s = s.replace(stary, novy, 1)
        print("   OK  %r -> %r" % (stary[:40], novy[:40]))
    P.write_bytes(s.encode("utf-8"))
    assert P.read_text(encoding="utf-8") == s, "zapsany obsah nesedi u %s" % jmeno
print()
print("HOTOVO")

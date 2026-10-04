# -*- coding: utf-8 -*-
"""Sonda: jak PRESNĚ vypadá souhrn na konci §8g v HANDOFF.md?"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

t = open("HANDOFF.md", encoding="utf-8").read()
for kotva in ("Vzor z těch sedmi", "v měřidle", "měřidle", "v **měřidle**"):
    print("%-22s %dx" % (repr(kotva), t.count(kotva)))
i = t.find("Vzor z těch sedmi")
print()
print("okoli (repr, 200 znaku):")
print(repr(t[i:i + 200]))

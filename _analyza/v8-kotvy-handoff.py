#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Jednoznačnost kotev pro VKLÁDÁNÍ do HANDOFF.md (past omylu 76).

Než něco vložím na kotevní text, musím vědět, kolikrát je v souboru.
Kotva, která je tam 2×, vloží text jinam, než chci — a vypadá to jako
„vložilo se to, ale nefunguje to".

Použití:  python _analyza\v8-kotvy-handoff.py
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"
t = H.read_text(encoding="utf-8")

KOTVY = [
    "## 18. Ověření práce AKČNÍ session — PLÁNOVACÍ session 2. 10. 2026 (12:2x–13:3x UTC)",
    "### 8h. Omyly AKČNÍ session",
    "## 21. Provedeno 2. 10. 2026",
    "k21e-dokonci-75.py",
    "| **80** | **„Skript na commit je hotový, stačí ho spustit\"**",
]

print("=" * 78)
print("JEDNOZNAČNOST KOTEV v HANDOFF.md (%d řádků)" % len(t.splitlines()))
print("=" * 78)
for k in KOTVY:
    n = t.count(k)
    na_radku = sum(1 for l in t.splitlines() if l.startswith(k))
    print("  kdekoliv %2dx · na začátku řádku %2dx  %r" % (n, na_radku, k[:66]))
print()
print("  Konec souboru (posledních 5 řádků):")
for l in t.splitlines()[-5:]:
    print("    %s" % l[:100])

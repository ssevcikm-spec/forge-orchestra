#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Kolik má soubor ŘÁDKŮ? — tři metody, které dávají různá čísla.

PROČ: `HANDOFF.md` §21.2 tvrdí, že `tests/run_tests.gd` má **1 205 řádků**.
`AGENTS.md` přitom varuje před konkrétní pastí: `split("\n")` dá u souboru
končícího newline **o jeden prvek víc** (naměřeno: `ci.yml` 183 místo 182)
a správně se má použít `splitlines()`. Rozdíl 1 204 vs. 1 205 je přesně tenhle
případ — takže se to musí změřit, ne hádat.

Použití:  python _analyza\v5-radky-souboru.py [cesta ...]
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
CESTY = sys.argv[1:] or [
    "games/uo-shadows/tests/run_tests.gd",
    "games/uo-shadows/scripts/combat.gd",
    "HANDOFF.md",
]

print("=" * 78)
print("POČET ŘÁDKŮ — tři metody vedle sebe")
print("=" * 78)
print()
print("  %-44s %7s %7s %7s %6s %s"
      % ("SOUBOR", "split-", "split-", "BAJTŮ", "KONČÍ", "SPRÁVNĚ"))
print("  %-44s %7s %7s %7s %6s" % ("", "lines()", "\\n", "", "\\n?"))
print("  " + "-" * 76)
for c in CESTY:
    f = WS / c
    t = f.read_text(encoding="utf-8")
    raw = f.read_bytes()
    a = len(t.splitlines())
    b = len(t.split("\n"))
    konec = raw.endswith(b"\n")
    print("  %-44s %7d %7d %7d %6s %d"
          % (c, a, b, len(raw), "ano" if konec else "NE", a))
print()
print("  `splitlines()` = počet řádků (a je to i to, co ukáže editor).")
print("  `split('\\n')` dá u souboru končícího newline o 1 VÍC — prázdný prvek na konci.")
print("  To je past z `AGENTS.md` (naměřeno na `ci.yml`: 183 vs. 182).")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""KTERÉ DOKUMENTY KTERÁ BRÁNA KRYJE (a kolik jich je).

PROČ: `HANDOFF.md` §21.3 tvrdí, že „ruční seznamy jsou nahrazeny projitím
složky". To je pravda pro `g1-diakritika-novych.py` (celý strom) a pro SKILLY
v `kontrola-diakritiky.py`. Otázka zůstává: **kryje `kontrola-diakritiky.py`
i dokumenty v kořeni workspace?** Odpověď se měří, nehádá.

Použití:  python _analyza\v7-krytí-dokumentu.py
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
OVER = WS / "orchestra" / "tools" / "over-dokumentaci.py"

print("=" * 78)
print("KTERÉ DOKUMENTY KTERÁ BRÁNA KRYJE")
print("=" * 78)

root_md = sorted(p.name for p in WS.glob("*.md"))
print()
print("  *.md v kořeni workspace (ty prochází `g1-diakritika-novych.py`): %d" % len(root_md))

for popis, f in (("kontrola-diakritiky.py", BRANA), ("over-dokumentaci.py", OVER)):
    t = f.read_text(encoding="utf-8")
    lit = sorted(set(re.findall(r'"([A-Za-z0-9_\-]+\.md)"', t)))
    chybi = [m for m in root_md if m not in lit]
    print()
    print("  %s:" % popis)
    print("    ručně vyjmenovaných .md v kódu: %d" % len(lit))
    print("    z kořene workspace jich NEKONTROLUJE: %d z %d" % (len(chybi), len(root_md)))
    if chybi:
        print("      (např. %s%s)" % (", ".join(chybi[:4]),
                                      ", …" if len(chybi) > 4 else ""))
    # Má brána projití složky?
    ma_glob = "glob(" in t
    print("    používá projití složky (`glob`): %s" % ("ANO" if ma_glob else "NE"))
    for m in re.finditer(r"^.*glob\(.*$", t, re.M):
        print("      %s" % m.group(0).strip()[:90])

print()
print("  ZÁVĚR: co kryje `g1` (celý strom), nemusí krýt `kontrola-diakritiky.py`")
print("  (ruční seznam). Díra je zavřená JINOU branou, ne tou samou — a to je")
print("  jiná věta než „ruční seznamy jsou zrušeny“.")

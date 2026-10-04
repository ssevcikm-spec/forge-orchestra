#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H17 — `lint-roadmapa` beze změny počtu varování? (tvrzení z §16.2)

Tvrzení: „11× `[5]`, 13 z 21 — ověřeno proti stromu s původní roadmapou."

Tenhle skript to měří pořádně: spustí lint nad DVĚMA stromy —
  (A) `_analyza\\h17-klidna` = čistý `origin/main` (roadmapa PŘED Úkolem B),
  (B) pracovní strom klonu        (roadmapa PO Úkolu B),
a porovná nejen souhrn, ale i MNOŽINU varování. Kdyby se změnil počet
u kterékoli kategorie, je to nález.

Použití:  python _analyza\\h17-lint-roadmapa.py
"""

import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
KLON = KOREN / "games" / "uo-shadows"
KLIDNA = KOREN / "_analyza" / "h17-klidna"
LINT = KOREN / "orchestra" / "tools" / "lint-roadmapa.py"


def spust(cesta: Path):
    r = subprocess.run([sys.executable, str(LINT), str(cesta / ".forge" / "roadmap.json")],
                       capture_output=True)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    p5 = re.findall(r"^\s*\[5\]", v, re.M)
    p3 = re.findall(r"^\s*\[3\]", v, re.M)
    m = re.search(r"Nalezeno problémů: (\d+)", v)
    g = re.search(r"Granulí: (\d+) \| hotových: (\d+)", v)
    sl = re.search(r"^\s*(\d+) z (\d+):", v, re.M)
    radky5 = sorted(l.strip() for l in v.splitlines() if l.strip().startswith("[5]"))
    radky3 = sorted(l.strip() for l in v.splitlines() if l.strip().startswith("[3]"))
    return {"exit": r.returncode, "vse": v, "pocet5": len(p5), "pocet3": len(p3),
            "problem": int(m.group(1)) if m else None,
            "granuli": g.groups() if g else None,
            "size_lines": sl.groups() if sl else None,
            "radky5": radky5, "radky3": radky3}


assert LINT.is_file(), "lint-roadmapa.py neni"
assert (KLIDNA / ".forge" / "roadmap.json").is_file(), \
    "chybi klidny strom %s (vytvor ho pres git worktree)" % KLIDNA

print("=" * 78)
print("H17 — lint-roadmapa nad DVEMA stromy")
print("=" * 78)
a = spust(KLIDNA)
b = spust(KLON)

for popis, v in (("A) origin/main (roadmapa PRED Úkolem B)", a),
                 ("B) pracovni strom klonu (roadmapa PO Úkolu B)", b)):
    print()
    print("  %s" % popis)
    print("    exit=%d  problémů=%s  granulí/hotových=%s  size_lines=%s"
          % (v["exit"], v["problem"], v["granuli"], v["size_lines"]))
    print("    [3] řádků: %d   [5] řádků: %d" % (v["pocet3"], v["pocet5"]))

print()
print("=" * 78)
print("ROZDÍL (množinový, ne jen počet)")
print("=" * 78)
jen_a5 = [l for l in a["radky5"] if l not in b["radky5"]]
jen_b5 = [l for l in b["radky5"] if l not in a["radky5"]]
jen_a3 = [l for l in a["radky3"] if l not in b["radky3"]]
jen_b3 = [l for l in b["radky3"] if l not in a["radky3"]]
for popis, sez in (("jen v A [5]", jen_a5), ("jen v B [5]", jen_b5),
                   ("jen v A [3]", jen_a3), ("jen v B [3]", jen_b3)):
    print("  %-12s %d" % (popis, len(sez)))
    for l in sez:
        print("      %s" % l[:170])

print()
if a["pocet5"] == b["pocet5"] and a["pocet3"] == b["pocet3"] \
        and not jen_a5 and not jen_b5 and not jen_a3 and not jen_b3:
    print("VYSLEDEK: SEDÍ — lint dává ve OBOU stromech TOTÉŽ (i množinově).")
    print("  [5]: %d   [3]: %d   problémů: %s vs %s"
          % (a["pocet5"], a["pocet3"], a["problem"], b["problem"]))
    sys.exit(0)
print("VYSLEDEK: ROZCHOD — lint se mezi stromy liší (viz výš).")
sys.exit(1)

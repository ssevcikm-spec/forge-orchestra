# -*- coding: utf-8 -*-
"""Sonda: proč mutace combat.gd projde, i když by měla spadnout?

Zjišťuje tři věci:
  1. je v `tests/run_tests.gd` (ve scratch) blok s `combat.resolve()`?
  2. je v `scripts/combat.gd` (ve scratch) vada po mutaci?
  3. co test vypíše — a kolik kontrol má?
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SCRATCH = WS / "_analyza" / "a-ukol-scratch"
TESTS = SCRATCH / "tests" / "run_tests.gd"
COMBAT = SCRATCH / "scripts" / "combat.gd"
KLIC = "combat.resolve() umí zásah i minutí"

t = TESTS.read_text(encoding="utf-8")
print("=== 1) BLOK V TESTECH (scratch) ===")
print("   obsahuje %r: %s" % (KLIC, KLIC in t))
print("   obsahuje 'zásah: damage =': %s" % ("zásah: damage =" in t))
print("   počet kontrol v souboru (_check volání): %d" % len(re.findall(r"_check\(", t)))
print("   řádků: %d" % len(t.splitlines()))

print()
print("=== 2) TESTOVACÍ SOUBOR V KLONU vs SCRATCH ===")
klon = WS / "games" / "uo-shadows" / "tests" / "run_tests.gd"
kt = klon.read_text(encoding="utf-8")
print("   klon:    %d znaků, obsahuje blok: %s" % (len(kt), KLIC in kt))
print("   scratch: %d znaků, obsahuje blok: %s" % (len(t), KLIC in t))
print("   shodné: %s" % (kt == t))

print()
print("=== 3) COMBAT.GD VE SCRATCH ===")
c = COMBAT.read_text(encoding="utf-8")
print("   znaků: %d" % len(c))
for i, l in enumerate(c.splitlines(), 1):
    if ".has(" in l or "armor_rating" in l or '"damage" in' in l:
        print("   %3d: %s" % (i, l))

# -*- coding: utf-8 -*-
"""Sonda: proč dá scratch 65/1, když klon dává 64/0?

Postup: srovnej OBA soubory (`combat.gd`, `tests/run_tests.gd`) mezi klonem
a scartchem, pak spusť testy v obou a vypiš, které kontroly se LIŠÍ.
"""

import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GODOT = WS / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
SCRATCH = WS / "_analyza" / "a-ukol-scratch"
KLON = WS / "games" / "uo-shadows"


def spust(cesta: pathlib.Path) -> list:
    env = dict(os.environ)
    env["APPDATA"] = str(WS / "_analyza" / "a-godot-user")
    r = subprocess.run([str(GODOT), "--headless", "--path", str(cesta),
                        "--script", "res://tests/run_tests.gd"],
                       capture_output=True, env=env, timeout=300)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return [l.strip() for l in v.splitlines() if l.strip().startswith("[test]")]


print("=== SOUBORY: klon vs scratch ===")
for rel in ("scripts/combat.gd", "tests/run_tests.gd", "scripts/player.gd"):
    a = (KLON / rel).read_bytes()
    b = (SCRATCH / rel).read_bytes()
    print("  %-22s klon %6d B  scratch %6d B  shodné: %s"
          % (rel, len(a), len(b), a == b))

print()
print("=== BĚH: klon ===")
kl = spust(KLON)
print("  " + [l for l in kl if "kontrol," in l][-1])

print()
print("=== BĚH: scratch ===")
sc = spust(SCRATCH)
print("  " + [l for l in sc if "kontrol," in l][-1])

print()
print("=== ROZDÍL (co je jen v jednom) ===")
jen_klon = [l for l in kl if l not in sc]
jen_scratch = [l for l in sc if l not in kl]
for l in jen_klon:
    print("  jen v KLONU:    " + l[:120])
for l in jen_scratch:
    print("  jen ve SCRATCH: " + l[:120])

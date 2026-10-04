"""Ověří, že připravená větev = přesně to, co leží v pracovním stromu klonu.

U každého souboru se porovnávají BAJTY blobu větve a souboru na disku.
U roadmapy se čeká jediný rozdíl: provedené srovnání se skutečností
(5 náhrad done_note/done) — proto se vypíše, co konkrétně se liší.
"""
import difflib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
Klon = WS / "games" / "uo-shadows"
GIT = str(WS / "orchestra" / "tools" / "git.cmd")
VETEV = "priprava/srovnani-roadmapy"

SOUBORY = [
    ".forge/check-schema.py",
    ".forge/roadmap.json",
    ".forge/vision.mjs",
    ".github/workflows/agent.yml",
    "scripts/assist.gd",
    "scripts/level.gd",
    "tools/make_iso_tiles.py",
]

rozdily = 0
for f in SOUBORY:
    p = subprocess.run([GIT, "-C", str(Klon), "show", f"{VETEV}:{f}"], capture_output=True, shell=True)
    if p.returncode != 0 or not p.stdout:
        print(f"MĚŘENÍ NEPROBĚHLO u {f} (rc={p.returncode})")
        sys.exit(1)
    blob = p.stdout.decode("utf-8")
    disk = (Klon / f).read_text(encoding="utf-8")
    if blob == disk:
        print(f"  stejné    {f}")
        continue
    rozdily += 1
    print(f"  LIŠÍ SE   {f}")
    for radek in difflib.unified_diff(disk.splitlines(), blob.splitlines(),
                                      fromfile="klon (disk)", tofile="větev", lineterm="", n=0):
        if radek.startswith(("+", "-")) and not radek.startswith(("+++", "---")):
            print(f"      {radek[:160]}")

print(f"\nSouborů, které se liší: {rozdily} (očekáváno 1 – roadmapa)")

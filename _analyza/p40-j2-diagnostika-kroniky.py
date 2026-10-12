# p40-j2-diagnostika-kroniky.py — DIAGNOSTIKA po neúspěšné opravě (nic nemění).
# Vypíše: kolik řádků má pracovní soubor a HEAD, jak vypadá konec vloženého
# řádku 55 a začátek řádku 54 v HEAD — aby se dalo rozhodnout, podle čeho
# je opravit (a kde je rozdíl znaků).
#
# Použití: python _analyza/p40-j2-diagnostika-kroniky.py

import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = pathlib.Path(__file__).resolve().parents[1]
GIT = str(WS / "tools" / "git.cmd")

head = subprocess.run([GIT, "-C", str(WS), "show", "HEAD:KRONIKA-PROJEKTU.md"],
                      capture_output=True, shell=True)
hr = (head.stdout or b"").decode("utf-8", "replace").splitlines()
p = (WS / "KRONIKA-PROJEKTU.md").read_text(encoding="utf-8").splitlines()

i55 = [i for i, l in enumerate(p) if l.startswith("| **55** | **12. 10. 2026**")]
i54 = [i for i, l in enumerate(hr) if l.startswith("| **54** |")]
print(f"pracovních řádků: {len(p)} · HEAD řádků: {len(hr)}")
print(f"index 55 v pracovním: {i55} · index 54 v HEAD: {i54}")
if i55:
    radek = p[i55[0]]
    print(f"\nPRACOVNÍ řádek {i55[0] + 1}: {len(radek)} znaků")
    print("  začátek:", repr(radek[:90]))
    print("  konec  :", repr(radek[-200:]))
    # hledej v něm marker zbytku řádku 54
    for marker in ("TIK TIKÁ", "REGRESE (Úkol 1)", "PLÁN ÚČTU JE FREE", "regrese tiku DVĚMA"):
        print(f"  obsahuje {marker!r}: {marker in radek} (pozice {radek.find(marker)})")
if i54:
    radek54 = hr[i54[0]]
    print(f"\nHEAD řádek 54: {len(radek54)} znaků")
    print("  začátek:", repr(radek54[:90]))
    print("  znaky 88–170:", repr(radek54[88:170]))

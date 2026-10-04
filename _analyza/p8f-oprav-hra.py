"""P8f — oprava dvou zbytkovych self-assignmentu na `HRA`.

Naměřeno skenem `p8e-najdi-nedoresene.py`:
  a3-mutace.py:30     HRA = HRA /  ".github" / "workflows" / "agent.yml"
  n8-zastarala-analyza.py:38  AGENT_HRA = HRA /  ".github" / ...

`HRA` neni definovana (hlavicka definuje `_HRA`), takze obe brany spadnou
`NameError` — a to je pro ne fatalni pri kazdem behu.

⚠ PROC PRESNE NAHRAZOVAT (a ne regexem): regex `HRA = HRA /` na tyhle radky
NESEDL, protoze za `/` jsou v souboru DVE mezery. Doslovna nahrada řetězce ten
problem nema — a kdyz vzor nenajde, musi to SKONCIT CHYBOU, ne tichem.
"""
from __future__ import annotations

import ast
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(r"E:\Workspaces\forge-orchestra\_analyza")

OPRAVY = [
    ("a3-mutace.py",
     'HRA = HRA /  ".github" / "workflows" / "agent.yml"',
     'HRA = _HRA / ".github" / "workflows" / "agent.yml"'),
    ("n8-zastarala-analyza.py",
     'AGENT_HRA = HRA /  ".github" / "workflows" / "agent.yml"',
     'AGENT_HRA = _HRA / ".github" / "workflows" / "agent.yml"'),
]


def main() -> int:
    chyby = 0
    for jmeno, stary, novy in OPRAVY:
        p = ANALYZA / jmeno
        t = p.read_text(encoding="utf-8")
        pocet = t.count(stary)
        if pocet != 1:
            print(f"CHYBA: {jmeno}: vzor nalezen {pocet}x (cekam 1) — needituji")
            chyby += 1
            continue
        p.write_text(t.replace(stary, novy), encoding="utf-8", newline="")
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            print(f"CHYBA: {jmeno} po oprave neparsuje: {e}")
            chyby += 1
            continue
        print(f"OK: {jmeno} — nahrazeno 1x")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main())

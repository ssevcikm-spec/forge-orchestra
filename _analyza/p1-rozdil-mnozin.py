"""Ktera konkretni soubory tvori rozdil `_analyza/` 117 (plan) vs 118 (dnes)?

PROC: cislo se neshoduje -> musi se VYSVETLIT, ne prepsat. Skript pocita
MNOZINU souboru, ne pocet, a vypise rozdil obema smery. Pocita se DVEMA
filtry, aby se ukazalo, ktery rozdil dela co:

  filtr A ("plan"):  SKIP obsahuje snapshoty dokumentace, NEobsahuje `_archiv`
  filtr B ("dnes"):  SKIP obsahuje `_archiv`, NEobsahuje snapshoty

Soubor se do poctu bere, kdyz obsahuje `Local-Deepseek` a ma suffix KODU.
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
ANALYZA = WS / "_analyza"
KOD = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}
SKIP_A = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__",
          ".tmp", ".wrangler", "snapshot-20261002-183213",
          "snapshot-20261002-181237"}
SKIP_B = dict.fromkeys(SKIP_A)
SKIP_B = set(SKIP_A) | {"_archiv"}


def mnozina(skip: set[str]) -> set[str]:
    out = set()
    for p in ANALYZA.rglob("*"):
        if any(d in p.parts for d in skip):
            continue
        if not p.is_file() or p.suffix.lower() not in KOD:
            continue
        if p.stat().st_size > 3_000_000:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "Local-Deepseek" in t:
            out.add(str(p.relative_to(ANALYZA)))
    return out


def main() -> int:
    a, b = mnozina(SKIP_A), mnozina(SKIP_B)
    print(f"filtr A (jako plan, bez _archiv):  {len(a)}")
    print(f"filtr B (dnes, s _archiv):         {len(b)}")
    print()
    print(f"--- v A, ne v B ({len(a - b)}) ---")
    for s in sorted(a - b):
        print(f"  {s}")
    print(f"--- v B, ne v A ({len(b - a)}) ---")
    for s in sorted(b - a):
        print(f"  {s}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

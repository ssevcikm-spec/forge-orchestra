"""Ktere 3 soubory pocita jeden filtr a druhy ne? (118 z p1-inventura vs 121)

PROC: dva skripty, stejny filtr, ruzne cislo = vada v jednom z nich. Tohle
je PRIMO porovna tuplem kodem, ktery se pro oba pouzije.

Vypise i duvod, proc se soubor mohl preskocit (velikost, dekodovani).
"""
from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
ANALYZA = WS / "_analyza"
KOD = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}
SKIP = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__",
        ".tmp", ".wrangler", "snapshot-20261002-183213",
        "snapshot-20261002-181237", "_archiv"}


def projdi() -> list[Path]:
    out = []
    for p in ANALYZA.rglob("*"):
        if any(d in p.parts for d in SKIP):
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
            out.append(p)
    return out


def main() -> int:
    soubory = projdi()
    print(f"projito: {len(soubory)}")
    # vytahni, co ma P1-INVENTURA-CEST.md zapsane
    inv = (ANALYZA / "P1-INVENTURA-CEST.md").read_text(encoding="utf-8")
    chybi = []
    for p in soubory:
        rel = str(p.relative_to(WS))
        if f"`{rel}`" not in inv:
            chybi.append(rel)
    print(f"v inventure NENI zapsano: {len(chybi)}")
    for c in sorted(chybi):
        print(f"  {c}   ({Path(c).stat().st_size} B)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

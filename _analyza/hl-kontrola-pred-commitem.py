#!/usr/bin/env python
"""Kontrola bajtů u souborů, které jdou do commitu (BOM + konce řádků).

PROČ TO EXISTUJE — naměřeno 1. 10. 2026: `git status` v orchestra hlásil
u tří souborů `LF will be replaced by CRLF the next time Git touches it`
(`core.autocrlf=true`). To je informativní hláška o NORMALIZACI v indexu, ne
vada — ale bez kontroly by se z ní nedalo poznat, jestli se do commitu neveze
i nechtěná změna konců řádků (přesně ta třída chyby, kterou řešil
`_analyza\\hl-konce-radku.py` a `hl-bom.py`).

Použití:
    python _analyza\\hl-kontrola-pred-commitem.py <repo> <soubor> [<soubor>...]
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = pathlib.Path(sys.argv[1]).resolve()
SOUBORY = sys.argv[2:]

if not SOUBORY:
    raise SystemExit("CHYBA: zadej aspoň jeden soubor")

git = pathlib.Path(__file__).resolve().parents[1] / "orchestra" / "tools" / "git.cmd"

print(f"repo: {REPO}")
print(f"{'soubor':<45} {'BOM':<5} {'CRLF':>6} {'LF':>6} {'bajtů':>8}  {'v indexu':>9}")
print("-" * 92)

vad = 0
for s in SOUBORY:
    cesta = REPO / s
    if not cesta.is_file():
        print(f"{s:<45} CHYBI SOUBOR")
        vad += 1
        continue
    b = cesta.read_bytes()
    bom = b[:3] == b"\xef\xbb\xbf"
    crlf = b.count(b"\r\n")
    lf = b.count(b"\n") - crlf
    # velikost blobu v indexu = co se skutečně commitne (po normalizaci)
    r = subprocess.run(
        [str(git), "cat-file", "-s", f":{s}"], cwd=REPO,
        capture_output=True, text=True, errors="replace",
    )
    v_indexu = r.stdout.strip() or f"(bez indexu: {r.stderr.strip()[:30]})"
    print(f"{s:<45} {str(bom):<5} {crlf:>6} {lf:>6} {len(b):>8}  {v_indexu:>9}")

print()
if vad:
    print(f"NALEZENO {vad} PROBLÉMŮ")
    sys.exit(1)
print("VŠE OK — soubory existují, bajty vypsané (BOM/konce řádků viditelné)")
sys.exit(0)

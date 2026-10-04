#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r"""Srovna konce radku a BOM u souboru, ktere jsem editoval.

PROC: editor zapsal CRLF tam, kde projekt pouziva LF (`*.py`, `*.mjs`, `*.gd`
jsou v `.gitattributes` nastavene na `text eol=lf`) a u `level.gd` zahodil BOM.
Git si to pri commitu normalizuje, ale pracovni strom ma jinou podobu nez
zbytek repa - a to je zbytecny sum v diffu i past pro pristi session.

Zapisuje se BAJTY (ne text), aby se nic neprekladalo podruhe.
PRED spustenim si soubor precti - skript prepisuje obsah.
Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza\hl-konce-radku.py
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

BOM = bytes([0xEF, 0xBB, 0xBF])
WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")

# (cesta, chce BOM?)
SOUBORY = [
    (WS / "games" / "uo-shadows" / "scripts" / "level.gd", True),
    (WS / "games" / "uo-shadows" / ".forge" / "check-schema.py", False),
    (WS / "orchestra" / "repo" / ".forge" / "check-schema.py", False),
    (WS / "orchestra" / "tools" / "validate-all.mjs", False),
    (WS / "orchestra" / "tools" / "test-cooldown.py", False),
]

for cesta, chce_bom in SOUBORY:
    if not cesta.exists():
        print(f"  CHYBI {cesta.name}")
        continue
    b = cesta.read_bytes()
    puvodni = (b[:3] == BOM, b.count(b"\r\n"))
    # 1) sjednotit na LF
    b2 = b.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    # 2) BOM
    ma_bom = b2[:3] == BOM
    if chce_bom and not ma_bom:
        b2 = BOM + b2
    elif not chce_bom and ma_bom:
        b2 = b2[3:]
    if b2 == b:
        print(f"  OK    {cesta.name:22} beze zmeny (BOM={'ANO' if puvodni[0] else 'ne'}, CRLF={puvodni[1]})")
        continue
    cesta.write_bytes(b2)
    print(f"  OPRAVA {cesta.name:22} BOM {puvodni[0]}→{b2[:3] == BOM}, "
          f"CRLF {puvodni[1]}→{b2.count(bytes([13, 10]))}, {len(b)}→{len(b2)} B")
print("\nHotovo. Overeni: python _analyza/hl-bom.py")

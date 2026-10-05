#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""H79 — najdi VŠECHNY neplatné escape sekvence v `.py` obou repů.

PROČ TO EXISTUJE: `python -W error::SyntaxWarning` nad repem **skončí na PRVNÍ**
sekvenci (warning se změní na chybu), takže se z něj nedá zjistit, **kolik jich
je**. A skener `hl-neanglicky-v-kodu.py` je hlásil **bez jména souboru**
(`ast.parse(text)` bez `filename` → `<unknown>:21`), takže se nedaly dohledat.

Tenble nástroj:
  1. projde oba repy (a `_analyza/`, což je uvnitř repa orchestra),
  2. každý `.py` načte **jako text** a zavolá `ast.parse(text, filename=...)`
     se `warnings.catch_warnings(record=True)` → posbírá **všechny**
     `SyntaxWarning` i s **řádkem a sloupcem**,
  3. vypíše `soubor:řádek:sloupec: sekvence` a čítač.

Návratový kód: 0 = 0 varování, 1 = nějaká jsou (a pak je to vada k opravě).
Použití:  python _analyza\h79-escape-sken.py
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
REPA = [("orchestra", WS), ("hra", WS.parent / "uo-shadows")]
SKIP = {".git", "node_modules", "_archiv", "__pycache__"}

vse: list[tuple[str, int, str]] = []
souboru = 0
chyb_parsovani = 0

for jmeno, koren in REPA:
    if not koren.is_dir():
        print(f"CHYBA: {jmeno} ({koren}) není adresář")
        chyb_parsovani += 1
        continue
    for p in sorted(koren.rglob("*.py")):
        if any(cast in SKIP for cast in p.parts):
            continue
        souboru += 1
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            try:
                text = p.read_text(encoding="utf-8-sig")
            except (UnicodeDecodeError, OSError):
                continue
        with warnings.catch_warnings(record=True) as zaznamy:
            warnings.simplefilter("always")
            try:
                ast.parse(text, filename=str(p))
            except SyntaxError as e:
                print(f"  CHYBA syntaxe: {p} — {e}")
                chyb_parsovani += 1
                continue
        for z in zaznamy:
            if issubclass(z.category, SyntaxWarning):
                vse.append((str(p.relative_to(koren.parent)), z.lineno or 0,
                            str(z.message)))

print("=" * 88)
print("H79 — NEPLATNÉ ESCAPE SEKVENCE (`SyntaxWarning` z `ast.parse`)")
print("=" * 88)
print(f"  prošlé soubory: {souboru}   (skip: {', '.join(sorted(SKIP))})")
print()
if vse:
    for cesta, radek, text in vse:
        print(f"  {cesta}:{radek}   {text}")
    print()
    if chyb_parsovani:
        print(f"  + {chyb_parsovani} souborů se nedalo zpracovat")
    # JEDEN kanonický čítač pro `g3` (ten bere POSLEDNÍ výskyt vzoru).
    print(f"ZMĚŘENO: {len(vse)} neplatných escape sekvencí "
          f"({souboru} souborů prošlo)")
    sys.exit(1)
if chyb_parsovani:
    print(f"ZMĚŘENO: {chyb_parsovani} souborů se nedalo zpracovat "
          f"({souboru} souborů prošlo)")
    sys.exit(1)
print(f"ZMĚŘENO: 0 neplatných escape sekvencí ({souboru} souborů prošlo)")
sys.exit(0)

# -*- coding: utf-8 -*-
"""Najde v mých skriptech NEASCII identifikátory (jména proměnných/funkcí).

`AGENTS.md` („Jazyk"): identifikátory jsou ASCII anglicky. `hl-rizika-jazyka.py`
kvůli jednomu takovému jménu spadl a strhl s sebou `validate-all` i dvě brány
(`n1-over-inventar`, `C2: mutace N1`). Tenhle skener to najde PŘED během.
"""
import ast
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
HERE = pathlib.Path(__file__).resolve().parent
soubory = sorted(list(HERE.glob("p14*.py")) + list(HERE.glob("test-p14*.py"))
                 + list(HERE.glob("_vypis-*.py")))
nalezy = []
kontrol = 0
for f in soubory:
    strom = ast.parse(f.read_text(encoding="utf-8"))
    for uzel in ast.walk(strom):
        jmena = []
        if isinstance(uzel, ast.Name):
            jmena = [uzel.id]
        elif isinstance(uzel, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            jmena = [uzel.name]
        elif isinstance(uzel, ast.arg):
            jmena = [uzel.arg]
        elif isinstance(uzel, ast.Attribute):
            jmena = [uzel.attr]
        elif isinstance(uzel, ast.keyword) and uzel.arg:
            jmena = [uzel.arg]
        for j in jmena:
            kontrol += 1
            if any(ord(c) > 127 for c in j):
                nalezy.append((f.name, getattr(uzel, "lineno", 0), j))

print(f"  souborů: {len(soubory)}, identifikátorů zkontrolováno: {kontrol}")
if nalezy:
    for n, r, j in nalezy:
        print(f"  CHYBA {n}:{r}  identifikátor s diakritikou: {j!r}")
    sys.exit(1)
print("  OK — všechny identifikátory v mých skriptech jsou ASCII")

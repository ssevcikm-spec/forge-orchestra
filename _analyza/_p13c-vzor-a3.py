# -*- coding: utf-8 -*-
"""P13c: opraví v `g3-brany.py` vzor čítače u brány `a3-over`.

DŮVOD (naměřeno): vzor byl holé `r"(\\d+)"` — „první číslo ve výstupu". To NENÍ
čítač: naměřeno `otevřela: 1`, což bylo **první číslo v mezeře za slovem `job`**
(`job 'auto-merge'` — díra). Je to táž past jako NA23 u `validate-all`
(`overovani` §10.1: ptej se, KTERÝ výskyt vzor trefí).

Navíc vzor nesmí být citlivý na to, jestli soubor diakritiku má (`ZMĚŘENO`) —
jinak se z vady diakritiky stane „brána neměří". Hledá se proto tolerantně.
"""
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\_analyza\g3-brany.py")
t = P.read_text(encoding="utf-8")

STARY = '''    ("C1: a3-over (náhrada za a3-kontrola.mjs)", ["python", "<ANALYZA>/a3-over.py"],
     r"(\\d+)"),'''
NOVY = '''    ("C1: a3-over (náhrada za a3-kontrola.mjs)", ["python", "<ANALYZA>/a3-over.py"],
     r"ZM.\\u0158ENO:\\s*(\\d+) kontrol"),'''

assert t.count(STARY) == 1, f"kotva nalezena {t.count(STARY)}x, očekávána 1x"
t2 = t.replace(STARY, NOVY, 1)
assert t2 != t
P.write_text(t2, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
assert r'r"ZM.\u0158ENO:\s*(\d+) kontrol"' in zpet, "nový vzor v souboru NENÍ"
print("vzor u a3-over opraven")

import ast
ast.parse(zpet)
print("AST OK")

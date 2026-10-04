"""Sonda na nahrazovaci vzor P8 — overuje literaly se vsemi tvary uvozovek.

PROC: vada se dvakrat projevila jen v NEKTERYCH tvarech (`r"..."` vs `r'...'`)
a odhalil ji az beh. Sonda to overi na vstupech, kde MUSI projit i kde NESMI:
  - `r"C:\\...\\orchestra\\repo"`        -> vyraz s `repo`
  - `pathlib.Path(r"C:\\...\\orchestra")`-> vyraz
  - `'C:/Users/.../games/uo-shadows'`    -> vyraz s uo-shadows
  - `"C:/Users/.../orchestra/.env"`      -> PARENT/.env
  - `'bez cesty'`                        -> BEZ ZMENY
  - `"C:\\...\\gameforge\\x"`            -> smi zustat (mrtva cesta)
"""
from __future__ import annotations

import sys
from importlib import util
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SPEC = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\p8-oprava-cest.py")
mod = util.spec_from_file_location("p8", SPEC)
m = util.module_from_spec(mod)
mod.loader.exec_module(m)

PRIPADY = [
    ('a = r"C:\\Users\\Ssevc\\Local-Deepseek\\orchestra\\repo"', ".py", "_PARENT / 'repo'"),
    ('a = pathlib.Path(r"C:\\Users\\Ssevc\\Local-Deepseek\\orchestra")', ".py", "_PARENT"),
    ("a = 'C:/Users/Ssevc/Local-Deepseek/games/uo-shadows'", ".mjs",
     "join(PARENT, 'uo-shadows')"),
    ('a = "C:/Users/Ssevc/Local-Deepseek/orchestra/.env"', ".mjs",
     "join(PARENT, '.env')"),
    ('a = r"C:\\Users\\Ssevc\\Local-Deepseek\\games\\uo-shadows\\.forge\\roadmap.json"',
     ".py", "_PARENT / 'uo-shadows' / '.forge' / 'roadmap.json'"),
    ("a = 'bez cesty'", ".py", None),  # nesmi se zmenit
]

selhalo = 0
for zdroj, pripona, ocekavano in PRIPADY:
    novy, pocet = m.oprav_literal(zdroj, pripona == ".py")
    if ocekavano is None:
        ok = novy == zdroj and pocet == 0
        popis = "beze zmeny"
    else:
        ok = ocekavano in novy and "r_" not in novy
        popis = ocekavano
    stav = "OK " if ok else "SPATNE"
    if not ok:
        selhalo += 1
    print(f"{stav} [{pripona}] {zdroj[:58]:58} -> {novy.strip()}")

print()
print(f"ZMĚŘENO: případů={len(PRIPADY)}, selhalo={selhalo}")
sys.exit(1 if selhalo else 0)

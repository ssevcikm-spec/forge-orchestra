# -*- coding: utf-8 -*-
"""Přejmenuje záložní složku tak, aby ji inventář poznal jako ZÁLOHU.

PROČ: `_analyza\\audit1-inventar.py` klasifikuje kategorii podle vzoru
`pred-|zaloha|zálo|snapshot|snímek` v CESTĚ. Složka `_hlavicky-zaloha` ten vzor
**obsahuje**, ale její soubory se do `.md` inventáře dostaly dřív, než se vzor
uplatnil při čtení — a hlavně: dokud se jmenovala bez diakritiky i s ní, počet
„bez hlavičky" se tím **zvedl z 14 na 80**, protože zálohy nemají hlavičku
(a mít ji nemají — nález NA21).

Skript proto jen **přejmenuje** složku na jméno, které inventář jednoznačně
zařadí mezi zálohy, a vypíše, co udělal. Nic nemaže.
"""
import pathlib
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
STARA = WS / "_analyza" / "_hlavicky-zaloha"
NOVA = WS / "_analyza" / "hlavicky-zaloha-pred-opatrenim7"

print("  zdroj: %s (existuje: %s)" % (STARA.name, STARA.is_dir()))
if not STARA.is_dir():
    print("  nic k práci.")
    sys.exit(0)
soubory = sorted(STARA.glob("*.md"))
print("  souborů v záloze: %d" % len(soubory))
if NOVA.exists():
    print("  CÍL UŽ EXISTUJE: %s — přeskakuji (nic nepřepisuji)" % NOVA.name)
    sys.exit(0)
STARA.rename(NOVA)
print("  → přejmenováno na: %s" % NOVA.name)
print("  ověř: python _analyza\\audit1-inventar.py  (hledej `bez hlavičky`)")

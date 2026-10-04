# -*- coding: utf-8 -*-
"""Sonda: pozná `ast.parse` rozbitou českou uvozovku?

PROČ TENHLE SOUBOR EXISTUJE (a proč vznikl až 2. 10. 2026 podruhé):
byl zapsaný v `HANDOFF.md` §16.11 a v seznamu `_analyza\\g1-diakritika-novych.py`
jako nástroj C2 — ale na disku **NEBYL** (naměřeno 2. 10. 2026 v plánovací
session: `Test-Path` → False, a brána `g1` kvůli tomu končila `exit 1`
s hláškou „NEEXISTUJE"). Byl to tedy **doklad, který se ztratil** — a to je
horší než chybějící nástroj, protože na něj odkazují dva dokumenty.

Co měří (nezávisle na `c2-oprava-uvozovek.py`):
  1. řádek s otevřenou českou uvozovkou a zavřenou ASCII uvozovkou
     se NEPARSUJE (doklad omylu 48),
  2. `c2-oprava-uvozovek.py` ho opraví (výstup se parsuje),
  3. a kontrola, že se to nestalo omylem — správně uzavřený řádek
     se parsuje i PŘED opravou (jinak by sonda měřila něco jiného).

Použití:  python _analyza\\c2-sonda-uvozovky.py
"""

import ast
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
OPRAVA = WS / "_analyza" / "c2-oprava-uvozovek.py"

OTEV = "\u201e"   # česká otevírací
ZAVR = "\u201c"   # česká zavírací
ASCII = '"'

# ── VZORKY ───────────────────────────────────────────────────────────────────
# Vzorek 1 je VADNÝ: uvnitř f-stringu se otevře česká uvozovka a zavře ASCII,
# takže řetězec skončí dřív a závorka zůstane otevřená.
VZOREK_VADNY = (
    'def f():\n'
    '    return f"text {OTEV}popis{ASCII} a dál"\n'
).replace("{OTEV}", OTEV).replace("{ASCII}", ASCII)

# Vzorek 2 je SPRÁVNÝ (kontrolní): obě uvozovky české.
VZOREK_SPRAVNY = (
    'def f():\n'
    '    return f"text {OTEV}popis{ZAVR} a dál"\n'
).replace("{OTEV}", OTEV).replace("{ZAVR}", ZAVR)

chyby = []
print("=" * 78)
print("SONDA: pozná `ast.parse` rozbitou českou uvozovku?")
print("=" * 78)

# 1) vadný vzorek se NESMÍ parsovat
try:
    ast.parse(VZOREK_VADNY)
    stav = "PARSOVAL SE — sonda neměří nic"
    chyby.append("vadný vzorek se parsoval")
except SyntaxError as e:
    stav = "SyntaxError: %s (řádek %s)" % (e.msg, e.lineno)
print("  1) vadný vzorek ............ %s" % stav)
print("     %s" % VZOREK_VADNY.splitlines()[1].strip()[:90])

# 2) správný vzorek se parsovat MUSÍ (jinak sonda hlásí vadu na správném kódu)
try:
    ast.parse(VZOREK_SPRAVNY)
    print("  2) správný vzorek .......... parsuje se OK (kontrolní případ)")
except SyntaxError as e:
    chyby.append("správný vzorek se neparsoval — falešný poplach")
    print("  2) správný vzorek .......... CHYBA: %s" % e.msg)

# 3) opravný nástroj na tom vadném vzorku něco změní a výsledek se parsuje
#
# ⚠ POZOR: `import` toho modulu se NESMÍ použít — jeho kód na úrovni modulu
# sám PŘEPISUJE `c2-oprav-n1.py` a `hl-rizika-jazyka.py` (naměřeno při psaní
# téhle sondy: import vypsal „beze změny", ale v jiném stavu by zapsal).
# Sonda proto vytáhne jen FUNKCI `oprav_radky` a spustí ji v izolaci.
_zdroj = OPRAVA.read_text(encoding="utf-8")
_i = _zdroj.find("def oprav_radky(")
_j = _zdroj.find("\ncelkem = 0", _i)
assert _i >= 0 and _j > _i, "z %s se nepodařilo vytáhnout oprav_radky()" % OPRAVA.name
_ns = {"OTEV": OTEV, "ZAVR": ZAVR, "ASCII": ASCII}
exec(compile(_zdroj[_i:_j], str(OPRAVA), "exec"), _ns)   # jen definice funkce
oprav_radky = _ns["oprav_radky"]

opraveny, zmeny = oprav_radky(VZOREK_VADNY)
print("  3) oprav_radky() ........... změn: %d" % len(zmeny))
if opraveny == VZOREK_VADNY:
    chyby.append("oprav_radky() nic nezměnil — sonda o opravě nic netvrdí")
    print("     OPRAVA NIC NEZMENILA")
else:
    try:
        ast.parse(opraveny)
        print("     opravený vzorek se parsuje OK")
    except SyntaxError as e:
        chyby.append("opravený vzorek se pořád neparsuje: %s" % e.msg)
        print("     CHYBA: pořád se neparsuje — %s" % e.msg)

# 4) pojistka z overovani §7.14: měřená PODMÍNKA musí přestat platit
podminka_pred = VZOREK_VADNY.count(OTEV) > VZOREK_VADNY.count(ZAVR)
podminka_po = opraveny.count(OTEV) > opraveny.count(ZAVR)
print("  4) nevyvážené uvozovky ..... před=%s po=%s" % (podminka_pred, podminka_po))
if not podminka_pred or podminka_po:
    chyby.append("podmínka nevyváženosti se neobrátila — mutace/sonda nic nemění")

print()
if chyby:
    print("NALEZENO %d PROBLÉMŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE SEDÍ — `ast.parse` rozbitou uvozovku pozná a `oprav_radky()` ji opraví.")
sys.exit(0)

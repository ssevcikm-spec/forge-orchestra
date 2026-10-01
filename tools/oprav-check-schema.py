"""Jednorázová oprava: BOM-safe čtení JSON + výchozí cesta v .forge/check-schema.py.

PROČ SKRIPTEM A NE EDITOREM: `check-schema.py` byl do obou repozitářů ZKOPÍROVANÝ,
takže se musí upravit na dvou místech stejně. Ruční editace dvou kopií je přesně
ten způsob, jak vznikne drift, kvůli kterému tenhle nástroj vůbec existuje.

Použití: python orchestra/tools/oprav-check-schema.py
"""
from __future__ import annotations

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOPIE = [
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.forge\check-schema.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\check-schema.py"),
    # zdrojový nástroj v orchestra/tools je tentýž soubor
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\tools\kontrola-schematu.py"),
]

# 1) BOM-safe čtení JSON. PowerShell i editory na Windows přidávají UTF-8 BOM
#    a `json.loads` na něm spadne – nástroj by hlásil neplatnou konfiguraci,
#    i když je soubor v pořádku.
STARE_CTENI = '''def _nacti_json(cesta: Path):
    try:
        return json.loads(cesta.read_text(encoding="utf-8"))
    except Exception as e:
        return {"_chyba": str(e)}'''

NOVE_CTENI = '''def _nacti_json(cesta: Path):
    try:
        # `utf-8-sig` odstraňuje BOM. PowerShell (`Set-Content -Encoding UTF8`)
        # i některé editory na Windows ho přidávají na začátek souboru a
        # `json.loads` na něm spadne s nesrozumitelnou hláškou. Stejná past už
        # jednou potkala `orchestra/.env` (viz orchestra/README.md).
        return json.loads(cesta.read_text(encoding="utf-8-sig"))
    except Exception as e:
        return {"_chyba": str(e)}'''

# 2) Cesta k repu jako volitelný argument – v CI se pouští z kořene hry,
#    takže `python .forge/check-schema.py` bez argumentu musí fungovat.
STARE_ARG = '''    ap.add_argument("repo", help="cesta k repu hry (kořen s assets/spec.json)")'''
NOVE_ARG = '''    ap.add_argument("repo", nargs="?", default=".",
                    help="cesta k repu hry (výchozí: aktuální složka)")'''

upraveno = 0
for cesta in KOPIE:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje, přeskakuji")
        continue
    t = cesta.read_text(encoding="utf-8")
    zmen = []
    if STARE_CTENI in t:
        t = t.replace(STARE_CTENI, NOVE_CTENI)
        zmen.append("BOM-safe JSON")
    if STARE_ARG in t:
        t = t.replace(STARE_ARG, NOVE_ARG)
        zmen.append("volitelná cesta")
    if zmen:
        cesta.write_text(t, encoding="utf-8")
        upraveno += 1
        print(f"  OK   {cesta.parent.parent.name}\\{cesta.name}: {', '.join(zmen)}")
    else:
        print(f"  --   {cesta.parent.parent.name}\\{cesta.name}: už upraveno")

print()
print(f"Upraveno souborů: {upraveno}")

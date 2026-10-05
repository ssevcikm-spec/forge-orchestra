#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Test pro NÁLEZ H71 — klasifikátor „brána vůbec nezačala" v `g3-brany.py`.

CO BYLO VADNÉ (naměřeno P14 5. 10. 2026)
----------------------------------------
`g3` se ptal na `exit=2` + **žádný čítač** + **výstup < 500 B**. To je měření
**DÉLKY, ne obsahu**: `C2: mutace N1` **proběhla**, **řekla to** („→ brána
neprojde ani ve zdravém stavu; končím") a měla **476 B** → byla vykázána jako
„BRÁNY, KTERÉ VŮBEC NEZAČALY (1)". **Falešný nález o funkční bráně.**

JAK SE TO MĚŘÍ — a proč se NEMUTUJE živý soubor
-----------------------------------------------
Test vezme **živý `g3-brany.py` jako ZDROJ**, ve zkopírovaném textu nahradí
**jen `BRANY`** za tři fixturové brány a kopii spustí. Tím se:
  * **zavolá skutečný klasifikátor** (`je_neotevrena()` přes `spust()`),
  * **nezapisuje se do živého `g3-brany-vystup.txt`** (to je záznam běhu),
  * **nemutuje živý soubor** — mutace je druhá kopie téhož zdroje s vrácenou vadou.

Tři fixturové brány (všechny `exit=2`, všechny bez čítače — tedy přesně ten tvar,
který klasifikátor rozhoduje):
  1. **vlastní krátké hlášení** („CHYBA … končím") → brána BĚŽELA, nesmí být
     mezi nezačatými (to je celý H71),
  2. **exit=2 bez výstupu** → podle kritéria zadání „nezačala",
  3. **neexistující soubor** → interpret hlásí chybějící soubor → „nezačala".

MUTACE: do zdroje se vrátí původní podmínka (`len(v) < 500`) — a test **musí
zčervenat** (fixtura 1 se objeví mezi nezačatými).

Použití:  python _analyza\test-h71-klasifikator.py
"""
from __future__ import annotations

import json
import pathlib
import os
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
FIX = ANALYZA / "fixtura-h71"
PY = sys.executable

NOVA_PODMINKA = "je_neotevrena(r.returncode, nalezeno, v)"
STARA_PODMINKA = 'r.returncode == 2 and nalezeno.startswith("\u2014") and len(v) < 500'

POPIS_HLASENI = "fixtura: exit=2 s VLASTNIM hlasenim"
POPIS_TICHA = "fixtura: exit=2 BEZ vystupu"
POPIS_CHYBI = "fixtura: neexistujici soubor"

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:18]:
            print(f"        {r}")


def zapis_g3(zdroj: str, brany: list[tuple[str, list[str]]]) -> pathlib.Path:
    """Zapíše kopii `g3` se stejnou logikou, ale s fixturovými `BRANY`."""
    i0 = zdroj.index("BRANY = [")
    i1 = zdroj.index("\n]\n\nvse = []", i0)
    blok = "BRANY = [\n"
    for popis, prikaz in brany:
        argumenty = ", ".join(json.dumps(str(a)) for a in prikaz)
        blok += f"    ({json.dumps(popis)}, [{argumenty}], None),\n"
    blok += "]"
    cil = FIX / "_analyza" / "g3-brany.py"
    cil.write_text(zdroj[:i0] + blok + zdroj[i1 + 2:], encoding="utf-8", newline="")
    return cil


def spust_g3(cesta: pathlib.Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([PY, str(cesta)], cwd=str(FIX), capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def nezacaly(vystup: str) -> list[str]:
    """Vytáhne sekci „BRÁNY, KTERÉ VŮBEC NEZAČALY“ (nebo vrátí prázdno)."""
    m = re.search(r"BRÁNY, KTERÉ VŮBEC NEZAČALY \((\d+)\)[^\n]*\n((?:   [^\n]*\n)*)",
                  vystup)
    if not m:
        return []
    return [l.strip().split("  (")[0] for l in m.group(2).splitlines() if l.strip()]


print("=" * 92)
print("NÁLEZ H71 — umí `g3` poznat, že brána BĚŽELA (a neříct „nezačala“)?")
print("=" * 92)
print(f"  zdroj  = {G3}")
print(f"  fixtura= {FIX}  (vzniká a uklidí se; živý soubor se NEMUTUJE)")
print()

zdroj = G3.read_text(encoding="utf-8")
zkontroluj("živý `g3-brany.py` volá nový klasifikátor `je_neotevrena(...)` 1×",
           zdroj.count(NOVA_PODMINKA) == 1, f"výskytů: {zdroj.count(NOVA_PODMINKA)}")
zkontroluj("živý `g3-brany.py` UŽ NEOBSAHUJE vadnou podmínku `len(v) < 500`",
           "len(v) < 500" not in zdroj)
zkontroluj("klasifikátor je pojmenovaná funkce (dá se volat a měnit zvlášť)",
           "def je_neotevrena(" in zdroj)

if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "_analyza").mkdir(parents=True)

# Fixturové brány: každá dělá právě jednu věc, kterou klasifikátor rozhoduje.
(FIX / "brana-kratka.py").write_text(
    "# -*- coding: utf-8 -*-\n"
    "import sys\n"
    'print("CHYBA: fixtura — zdravý inventář neprošel; končím")\n'
    "sys.exit(2)\n", encoding="utf-8", newline="")
(FIX / "brana-ticha.py").write_text(
    "# -*- coding: utf-8 -*-\nimport sys\nsys.exit(2)\n",
    encoding="utf-8", newline="")

brany = [
    (POPIS_HLASENI, [PY, FIX / "brana-kratka.py"]),
    (POPIS_TICHA, [PY, FIX / "brana-ticha.py"]),
    (POPIS_CHYBI, [PY, FIX / "neexistuje.py"]),
]

try:
    # ── 1) ZDRAVÝ ZDROJ: správné zařazení ──────────────────────────────────
    print("── 1) ZDRAVÝ ZDROJ — tři fixturové brány s `exit=2` ──────────────────")
    cil = zapis_g3(zdroj, brany)
    zkontroluj("fixtura: kopie `g3` vznikla a má fixturové BRANY",
               cil.is_file() and POPIS_HLASENI in cil.read_text(encoding="utf-8"))
    kod, v = spust_g3(cil)
    zdrava_kopie = cil.read_bytes()          # NEŽ se přepíše mutantem
    print(f"      g3 na fixtuře: exit={kod}")
    for radek in v.splitlines():
        if "otevřela:" in radek or "NEZAČALY" in radek or "nezačaly" in radek or \
           "   fixtura" in radek or "plný výstup" in radek:
            print(f"      | {radek.rstrip()}")
    zkontroluj("fixtura: `g3` vykázal 3 brány",
               re.search(r"brán celkem:\s*3,", v) is not None, v[-1200:])
    seznam = nezacaly(v)
    print(f"      nezačaly podle g3: {seznam}")
    zkontroluj("falešný poplach JE OPRAVEN: brána s vlastním hlášením NENÍ "
               "mezi nezačatými", POPIS_HLASENI not in seznam, v[-1500:])
    zkontroluj("a přesto: neexistující soubor MEZI NEZAČATÝMI JE",
               POPIS_CHYBI in seznam, v[-1500:])
    zkontroluj("a brána s prázdným výstupem je tam taky (kritérium zadání)",
               POPIS_TICHA in seznam, v[-1500:])
    zkontroluj("seznam nezačatých má právě 2 položky (ne 3 — to byl H71)",
               len(seznam) == 2, str(seznam))

    # ── 2) MUTACE: vrácení původní podmínky ────────────────────────────────
    print()
    print("── 2) MUTACE: vrácena původní podmínka `len(v) < 500` ────────────────")
    mut = zdroj.replace(NOVA_PODMINKA, STARA_PODMINKA)
    zkontroluj("mutace se provedla v TEXTU (nová podmínka v mutantu není)",
               mut != zdroj and NOVA_PODMINKA not in mut)
    zkontroluj("a měřená podmínka se vrátila (stará je v mutantu 1×)",
               mut.count(STARA_PODMINKA) == 1)
    cil_m = zapis_g3(mut, brany)
    zkontroluj("mutant je na disku a liší se od zdravé kopie",
               cil_m.read_bytes() != zdrava_kopie)
    kod_m, v_m = spust_g3(cil_m)
    seznam_m = nezacaly(v_m)
    print(f"      mutant: exit={kod_m}, nezačaly: {seznam_m}")
    zkontroluj("MUTACE: brána s vlastním hlášením SE OBAVÍ mezi nezačatými "
               "(to je přesně H71 — test by ZČERVENAL)",
               POPIS_HLASENI in seznam_m, v_m[-1500:])
    zkontroluj("MUTACE: seznam nezačatých má 3 položky místo 2",
               len(seznam_m) == 3, str(seznam_m))
finally:
    shutil.rmtree(FIX, ignore_errors=True)
    zkontroluj("fixtura uklizena (živý `g3` ani jeho výstup se nedotkly)",
               not FIX.exists())

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"CHYBA: {chyb} — H71 NENÍ dokázané")
    sys.exit(1)
print("H71 JE OPRAVENO A DOKÁZÁNO: běžící brána se nezařadí mezi nezačaté "
      "a chybějící soubor se zařadí.")
sys.exit(0)

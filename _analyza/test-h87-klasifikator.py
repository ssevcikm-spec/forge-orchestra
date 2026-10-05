#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Test pro NÁLEZ H87 — klasifikátor `g3` rozhoduje podle SLOVNÍKU markerů.

CO BYLO VADNÉ (naměřeno P16 5. 10. 2026)
----------------------------------------
`je_neotevrena()` se ptala, jestli výstup obsahuje jeden z **12 markerů**
(`končím`, `CHYBA`, `ZMĚŘENO`, …). Brána, která skončila `exit=2` s KRÁTKÝM
VLASTNÍM HLÁŠENÍM bez markeru, propadla na `len(_radky) <= 1` a vykázala se
jako **„VŮBEC NEZAČALA"** — FALEŠNÝ NÁLEZ O FUNKČNÍ BRÁNĚ (táž třída jako H71).

JAK SE TO MĚŘÍ — a proč se NEMUTUJE živý soubor
----------------------------------------------
Test vezme **živý `g3-brany.py` jako ZDROJ**, v kopii nahradí **jen `BRANY`**
a kopii spustí. Živý soubor ani `g3-brany-vystup.txt` se nedotkne.

Fixtury jsou **doklady P16**, které zadání jmenuje
(`_analyza/p16a2-brana-bezmarkeru.py`, `p16a2-brana-hlaseni.py`,
`p16a2-brana-ticha.py`) — test si je NEVYRÁBÍ, ale ani je nemění. Když některá
chybí, test to **ohlásí** (chybějící doklad nesmí vypadat jako zelená).

ROZHODUJE CHOVÁNÍ:
  * `bezmarkeru` (exit=2, 1 řádek bez markeru) → BĚŽELA (třetí stav), NE „nezačala"
  * `hlaseni`    (exit=2, 1 řádek s markerem)   → BĚŽELA (třetí stav)
  * `ticha`      (exit=2, prázdný výstup)       → NEZAČALA
  * `neexistuje` (interpret hlásí chybějící soubor) → NEZAČALA

MUTACE: vrátí se stará podmínka `len(...) <= 1` — a test **musí zčervenat**
(`bezmarkeru` se objeví mezi nezačatými).

Použití:  python _analyza\test-h87-klasifikator.py
"""

import json
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
FIX = ANALYZA / "fixtura-h87"
PY = sys.executable

# Fixtury P16 (doklady) — NEMĚNÍ SE.
F_BEZMARKERU = ANALYZA / "p16a2-brana-bezmarkeru.py"
F_HLASENI = ANALYZA / "p16a2-brana-hlaseni.py"
F_TICHA = ANALYZA / "p16a2-brana-ticha.py"

P_BEZMARKERU = "fixtura: exit=2 s hlasenim BEZ markeru"
P_HLASENI = "fixtura: exit=2 s hlasenim S markerem"
P_TICHA = "fixtura: exit=2 BEZ vystupu"
P_CHYBI = "fixtura: neexistujici soubor"

# Vzor, který v žádném výstupu nic nenajde → `nalezeno` zůstane „—" (bez čítače).
# Tím se fixtura dostane do stavu, který klasifikátor rozhoduje.
VZOR = r"__NIC_NENAJDE__(\d+)"

NOVA_POSLEDNI = "    return any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU)"
STARA_POSLEDNI = (
    "    if any(z in text for z in _PODPIS_CHYBEJICIHO_SOUBORU):\n"
    "        return True\n"
    "    return len([l for l in text.splitlines() if l.strip()]) <= 1"
)

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
        blok += f"    ({json.dumps(popis)}, [{argumenty}], {VZOR!r}),\n"
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


def _sekce(vystup: str, nadpis_re: str) -> list[str]:
    # ⚠ `nadpis_re` sám obsahuje skupinu `(\\d+)` (počet), takže SEZNAM položek
    # je skupina **2**, ne 1. (Past `overovani` §10.1: „vzor něco našel" a
    # „vzor našel to, co hledám" jsou dvě věty.)
    m = re.search(nadpis_re + r"[^\n]*\n((?:   [^\n]*\n)*)", vystup)
    if not m:
        return []
    return [l.strip().split("  (")[0] for l in m.group(2).splitlines() if l.strip()]


def bez_komentaru(text: str) -> str:
    """Odstraní komentářové řádky.

    ⚠ Bez toho se kontrola chytí do pasti `dsh-prostredi` §1: `_VLASTNI_HLASENI`
    je v `g3` ZMÍNĚN v komentáři, který vadu popisuje — hledání v celém souboru
    by našlo **komentář**, ne kód, a kontrola by prošla i s vrácenou vadou.
    """
    return "\n".join(l for l in text.splitlines() if not l.lstrip().startswith("#"))


def nezacaly(vystup: str) -> list[str]:
    return _sekce(vystup, r"BRÁNY, KTERÉ VŮBEC NEZAČALY \((\d+)\)")


def bez_citace(vystup: str) -> list[str]:
    return _sekce(vystup, r"BRÁNY, KTERÉ BĚŽELY, ALE NEVYKÁZALY ČÍTAČ \((\d+)\)")


print("=" * 92)
print("NÁLEZ H87 — rozhoduje `g3` podle CHOVÁNÍ, nebo podle slovníku markerů?")
print("=" * 92)

chybejici = [p for p in (F_BEZMARKERU, F_HLASENI, F_TICHA) if not p.is_file()]
zkontroluj("fixtury P16 na disku existují (doklady, ne výroba v testu)",
           not chybejici, ", ".join(p.name for p in chybejici))
if chybejici:
    print("\nVÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    sys.exit(1)

zdroj = G3.read_text(encoding="utf-8")
kod = bez_komentaru(zdroj)
zkontroluj("živý `g3` UŽ NEOBSAHUJE whitelist markerů `_VLASTNI_HLASENI` (v KÓDU)",
           "_VLASTNI_HLASENI" not in kod)
zkontroluj("klasifikátor rozhoduje podle podpisu chybějícího souboru",
           "_PODPIS_CHYBEJICIHO_SOUBORU" in kod)
zkontroluj("živý `g3` má jen JEDNU poslední větev klasifikátoru (žádné `len(...) <= 1`)",
           kod.count(NOVA_POSLEDNI) == 1 and "text.splitlines()" not in kod)

if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "_analyza").mkdir(parents=True)

brany = [
    (P_BEZMARKERU, [PY, F_BEZMARKERU]),
    (P_HLASENI, [PY, F_HLASENI]),
    (P_TICHA, [PY, F_TICHA]),
    (P_CHYBI, [PY, FIX / "neexistuje.py"]),
]

try:
    # ── 1) ZDRAVÝ ZDROJ ────────────────────────────────────────────────────
    print("\n── 1) ZDRAVÝ ZDROJ — čtyři fixtury s `exit=2` a bez čítače ──────────")
    cil = zapis_g3(zdroj, brany)
    zdrava_kopie = cil.read_bytes()
    kod, v = spust_g3(cil)
    print(f"      g3 na fixtuře: exit={kod}")
    for radek in v.splitlines():
        if "otevřela:" in radek or "NEZAČALY" in radek or "NEVYKÁZALY" in radek \
           or "nezačaly" in radek or "   fixtura" in radek:
            print(f"      | {radek.rstrip()}")
    zkontroluj("fixtura: `g3` vykázal 4 brány",
               re.search(r"brán celkem:\s*4,", v) is not None, v[-1500:])

    nz = nezacaly(v)
    bc = bez_citace(v)
    print(f"      nezačaly: {nz}")
    print(f"      běžely bez čítače: {bc}")

    # ── H87 jádro: bez markeru NENÍ „nezačala" ────────────────────────────
    zkontroluj("H87 OPRAVENO: brána s hlášením BEZ markeru NENÍ mezi nezačatými",
               P_BEZMARKERU not in nz, str(nz))
    zkontroluj("brána s hlášením S markerem taky není mezi nezačatými",
               P_HLASENI not in nz, str(nz))
    # ── a obě správné klasifikace zůstaly ─────────────────────────────────
    zkontroluj("exit=2 BEZ výstupu JE mezi nezačatými (nezchladlo)",
               P_TICHA in nz, str(nz))
    zkontroluj("neexistující soubor JE mezi nezačatými (nezchladlo)",
               P_CHYBI in nz, str(nz))
    zkontroluj("nezačaté jsou PRÁVĚ 2 (ne 4)", len(nz) == 2, str(nz))
    # ── třetí stav je vidět ───────────────────────────────────────────────
    # ⚠ Sekce „BĚŽELY, ALE NEVYKÁZALY ČÍTAČ" má jiný formát položky než sekce
    # „NEZAČALY" (`popis → exit=…, důvod`), takže se hledá podřetězcem.
    zkontroluj("TŘETÍ STAV existuje: obě běžící brány bez čítače jsou vykázané",
               any(P_BEZMARKERU in x for x in bc)
               and any(P_HLASENI in x for x in bc), str(bc))
    zkontroluj("a nezačaté v něm NEJSOU",
               not any(P_TICHA in x for x in bc)
               and not any(P_CHYBI in x for x in bc), str(bc))

    # ── 2) MUTACE: vrácení staré podmínky `len(...) <= 1` ──────────────────
    print()
    print("── 2) MUTACE: vrácena stará podmínka `len(...) <= 1` ─────────────────")
    mut = zdroj.replace(NOVA_POSLEDNI, STARA_POSLEDNI)
    zkontroluj("mutace se provedla v TEXTU (nová větev v mutantu není)",
               mut != zdroj and NOVA_POSLEDNI not in mut)
    zkontroluj("a stará podmínka se vrátila (je v mutantu 1×)",
               mut.count(STARA_POSLEDNI) == 1)
    cil_m = zapis_g3(mut, brany)
    zkontroluj("mutant je na disku a liší se od zdravé kopie",
               cil_m.read_bytes() != zdrava_kopie)
    kod_m, v_m = spust_g3(cil_m)
    nz_m = nezacaly(v_m)
    print(f"      mutant: exit={kod_m}, nezačaly: {nz_m}")
    zkontroluj("MUTACE: brána BEZ markeru SE OBAVÍ mezi nezačatými "
               "(to je přesně H87 — test by ZČERVENAL)",
               P_BEZMARKERU in nz_m, v_m[-1500:])
    # ⚠ Počet v mutantu je 4, ne 3: mutant vrací jen `len(...) <= 1`, ale
    # `_VLASTNI_HLASENI` už v živém `g3` NENÍ (byl celý smazán), takže se mezi
    # nezačaté objeví i fixtura S markerem. Kdyby tu stálo „== 3", test by
    # měřil něco jiného, než co mutant skutečně dělá.
    zkontroluj("MUTACE: nezačatých je VÍC než 2 (stará podmínka je zpátky)",
               len(nz_m) > 2, str(nz_m))
finally:
    shutil.rmtree(FIX, ignore_errors=True)
    zkontroluj("fixtura uklizena (živý `g3` ani jeho výstup se nedotkly)",
               not FIX.exists())

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"CHYBA: {chyb} — H87 NENÍ dokázané")
    sys.exit(1)
print("H87 JE OPRAVENO A DOKÁZÁNO: rozhoduje CHOVÁNÍ, ne seznam markerů — "
      "běžící brána bez markeru se mezi nezačaté nezařadí a třetí stav je vidět.")
sys.exit(0)

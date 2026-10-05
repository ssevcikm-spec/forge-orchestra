#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Test pro NÁLEZ H70 — bezpečnostní síť v `zadani-kontrola.py` MUSÍ BÝT ZAVOLANÁ.

PROČ TO EXISTUJE (H70, naměřeno P14 5. 10. 2026)
------------------------------------------------
`zadani-kontrola.py` má od P13c větev: „tvrzení z hlavičky, která se nepodařilo
přiřadit k repu, se VYPÍŠOU jako varování". Ta větev se ve zdravém stavu **nikdy
nezavolá** (všechna tvrzení se přiřadí) — a **při prvním skutečném použití
spadla**:

    for j, _ in zivy      # `zivy` je SLOVNÍK → iterace dává řetězce
    ValueError: too many values to unpack (expected 2)

Přesně na tuhle třídu vady platí `overovani` §7.15: **„co je »zavolala«, se musí
DOKÁZAT"**. Tenhle test proto tu větev ZAVOLÁ — a to **fixturou**, ne mutací
živého `NEXT-SESSION-INSTRUKCE.md`.

CO SE MĚŘÍ (tři běhy, každý na SVÉM vstupu)
-------------------------------------------
  1. **KONTROLNÍ** fixtura: hlavička jmenuje oba repy a jejich ŽIVÉ HEADy →
     `exit 0`, a text „nepodařilo přiřadit" v ní **není**.
  2. **VADA** fixtura: hlavička navíc tvrdí `neznamy-repo` → brána musí dát
     `exit 1` **a** text „nepodařilo přiřadit k repu" — **NE traceback**.
  3. **MUTACE**: do ŽIVÉHO `zadani-kontrola.py` se vrátí původní tvar
     (`for j, _ in zivy`), běh 2 se zopakuje a **musí zčervenat** (objeví se
     `ValueError` / `Traceback`, hlášení zmizí). Soubor se vrací **bajt na bajt**
     v `try/finally` a na konci se ověří SHA-256.

Bez kroku 3 by test byl jen „prošlo to" — a to podle `overovani` §1 nic neznamená.

Použití:  python _analyza\test-h70-vetev.py
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
GIT = WS / "tools" / "git.cmd"
BRANA = ANALYZA / "zadani-kontrola.py"
FIX = ANALYZA / "fixtura-h70"
PY = sys.executable

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:16]:
            print(f"        {r}")


def git(cesta: pathlib.Path, *args: str) -> str:
    r = subprocess.run([str(GIT), "-C", str(cesta), *args],
                       capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust(fixtura: pathlib.Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([PY, str(BRANA), "--soubor", str(fixtura)],
                       cwd=str(WS), capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def fixtura(cesta: pathlib.Path, radky_stavu: str) -> pathlib.Path:
    """Zapíše minimální „zadání" s hlavičkou, kterou brána čte."""
    cesta.write_text(
        "# Fixtura pro test H70 — NENÍ zadání, je to jen VSTUP pro `zadani-kontrola.py`\n"
        "\n"
        f"**Zkontrolováno při:** `{sha_orch}` (fixtura pro test H70)\n"
        f"**Stav obou repů při psaní:** {radky_stavu}\n"
        "\n"
        "Fixtura. Nic dalšího v dokumentu není.\n",
        encoding="utf-8", newline="")
    return cesta


print("=" * 92)
print("NÁLEZ H70 — volá se bezpečnostní síť v `zadani-kontrola.py`?")
print("=" * 92)
print(f"  brána  = {BRANA}")
print(f"  WS     = {WS}")
print(f"  fixtura= {FIX}  (vzniká a uklidí se, do živého zadání se nesahá)")
print()

sha_orch = git(WS, "rev-parse", "HEAD")
sha_hra = git(HRA, "rev-parse", "HEAD")
zkontroluj(f"znám ŽIVÉ HEADy obou repů (orchestra {sha_orch[:9]}, hra {sha_hra[:9]})",
           len(sha_orch) == 40 and len(sha_hra) == 40,
           f"orchestra={sha_orch!r} hra={sha_hra!r}")

if FIX.exists():
    shutil.rmtree(FIX)
FIX.mkdir(parents=True)
try:
    # ── 1) KONTROLNÍ PŘÍPAD: tvrzení se VŠECHNA přiřadí ─────────────────────
    print("── 1) KONTROLNÍ PŘÍPAD: hlavička jmenuje jen známé repy ──────────────")
    fx_zdrava = fixtura(FIX / "zdrava.md",
                        f"`forge-orchestra` = `{sha_orch}` · `uo-shadows` = `{sha_hra}`")
    kod, v = spust(fx_zdrava)
    zkontroluj(f"zdravá fixtura: exit 0 (je {kod})", kod == 0, v[-900:])
    zkontroluj("zdravá fixtura: brána vykázala, že je zadání POUŽITELNÉ",
               "VÝSLEDEK: zadání je použitelné" in v, v[-900:])
    zkontroluj("zdravá fixtura: větev „nepodařilo přiřadit“ se NEVOLALA "
               "(to je ten důvod, proč vadu nikdo neviděl)",
               "nepodařilo přiřadit" not in v, v[-900:])

    # ── 2) VADA: hlavička tvrdí repo, které skript nezná ────────────────────
    print()
    print("── 2) VADA: hlavička tvrdí `neznamy-repo` (tudy vede ta větev) ────────")
    fx_vada = fixtura(FIX / "neznama.md",
                      f"`forge-orchestra` = `{sha_orch}` · `uo-shadows` = `{sha_hra}`"
                      f" · `neznamy-repo` = `{sha_orch}`")
    kod_v, v_v = spust(fx_vada)
    zkontroluj(f"vadná fixtura: exit 1 (je {kod_v})", kod_v == 1, v_v[-900:])
    zkontroluj("vadná fixtura: brána VYPÍŠE „nepodařilo přiřadit k repu“",
               "nepodařilo přiřadit k repu" in v_v, v_v[-900:])
    zkontroluj("vadná fixtura: brána pojmenuje NEPŘIŘAZENÉ tvrzení (`neznamy-repo`)",
               "neznamy-repo" in v_v, v_v[-900:])
    zkontroluj("vadná fixtura: místo hlášení NENÍ traceback (to byla vada H70)",
               "Traceback" not in v_v and "ValueError" not in v_v, v_v[-900:])
    zkontroluj("vadná fixtura: brána řekne, že je zadání ZASTARALÉ/NEPOUŽITELNÉ",
               "VÝSLEDEK: zadání je ZASTARALÉ NEBO NEPOUŽITELNÉ" in v_v, v_v[-900:])

    # ── 3) MUTACE: vrátí se PŮVODNÍ tvar a test MUSÍ zčervenat ─────────────
    print()
    print("── 3) MUTACE: do živé brány se vrací `for j, _ in zivy` ───────────────")
    orig = BRANA.read_bytes()
    orig_sha = hashlib.sha256(orig).hexdigest()[:16]
    KOTVA = b"_mozna_jmena(j) or j in k for j in zivy)}"
    VADA = b"_mozna_jmena(j) or j in k for j, _ in zivy)}"
    pocet = orig.count(KOTVA)
    zkontroluj("kotva `… for j in zivy)}` je v bráně 1× (mutace je jednoznačná)",
               pocet == 1, f"výskytů: {pocet}")
    try:
        BRANA.write_bytes(orig.replace(KOTVA, VADA))
        zpet = BRANA.read_bytes()
        zkontroluj("mutace se propsala NA DISK", zpet != orig)
        zkontroluj("měřená PODMÍNKA přestala platit (kotva v souboru není)",
                   KOTVA not in zpet)
        kod_m, v_m = spust(fx_vada)
        zkontroluj("MUTACE: brána spadne na `ValueError` / traceback "
                   "(důkaz, že test měří právě tu opravu)",
                   "ValueError" in v_m or "Traceback" in v_m, v_m[-900:])
        zkontroluj("MUTACE: hlášení „nepodařilo přiřadit“ SE ZTRATILO "
                   "(bez opravy brána nic neřekne)",
                   "nepodařilo přiřadit" not in v_m, v_m[-900:])
        # Kontrolní případ musí zůstat zelený i s vrácenou vadou — jinak by test
        # neprokazoval, že vada je v TÉ větvi, a ne v celé bráně.
        kod_mz, v_mz = spust(fx_zdrava)
        zkontroluj("MUTACE: KONTROLNÍ případ zůstává `exit 0` "
                   "(vada je v záchranné větvi, ne v celé bráně)",
                   kod_mz == 0, v_mz[-900:])
    finally:
        BRANA.write_bytes(orig)
    zkontroluj(f"brána vrácena bajt na bajt (sha {orig_sha})",
               hashlib.sha256(BRANA.read_bytes()).hexdigest()[:16] == orig_sha)

    # Po návratu musí vada znovu HLÁSIT, ne spadnout.
    kod_p, v_p = spust(fx_vada)
    zkontroluj("po návratu: brána znovu hlásí (exit 1 a text, ne traceback)",
               kod_p == 1 and "nepodařilo přiřadit k repu" in v_p
               and "ValueError" not in v_p, v_p[-900:])
finally:
    shutil.rmtree(FIX, ignore_errors=True)
    zkontroluj("fixtura uklizena (v repu nezůstal žádný soubor navíc)",
               not FIX.exists())

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"CHYBA: {chyb} — větev H70 NENÍ dokázaná")
    sys.exit(1)
print("H70 JE OPRAVENO A DOKÁZÁNO: větev se ZAVOLÁ, hlásí, a s vrácenou vadou test zčervená.")
sys.exit(0)

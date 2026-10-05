# -*- coding: utf-8 -*-
r"""P13c: archivace jednorázovek P8/P9 (nález H55, dokončení D5).

PROČ: přesun na `E:` je HOTOVÝ. Nástroje, které pracovaly na STARÉM stromě
(`p8-oprava-cest.py` opravoval cesty PŘED přesunem, `p8b-archivace.py` dělal
archivaci, `p9-presun-dokumentu.py` přesunul dokumenty), **nemají co dělat** —
jen zůstaly v `_analyza/` a drží v sobě vzorky starých cest.

⚠ CO SE NEMAŽE A PROČ:
  * `_analyza/_archiv/` a `_analyza/_zaloha*` — záznamy (D5),
  * `p1-inventura-cest.py`, `p1b-odvozene-cesty.py`, `p8-inventura-cest-v-kodu.py`,
    `p8-sonda-vzor.py` — obsahují `Local-Deepseek` **jako VZOREK (regex)**.
    To je SPRÁVNĚ: jsou to **měřidla cest**, ne vady (zadání to říká výslovně),
  * `sken-vazeb.py`, `hl2-*`, `js-tokeny.mjs`, `test-neanglicky-skener.py`,
    `over-okno.mjs`, `z8-probe.py` — ŽIVÉ nástroje dle `CO-SE-ARCHIVOVALO.md`.

⚠ A JEDNA VĚC, KTERÁ SE NESMÍ STÁT: přesunout nástroj, na který sahá živá brána.
Před přesunem se proto každý soubor **prohledá** v živých souborech
(`g3-brany.py`, `validate-all.mjs`, `AGENTS.md`) — když na něj někdo sahá,
skript to ŘEKNE a nic nepřesune (`overovani` §7: mrtvá větev je slepé místo).

Použití: python _analyza\p13c-archivuj-p8.py
Návrat:  0 = přesunuto | 2 = nález (nic se nepřesunulo)
"""

import pathlib
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
ARCHIV = ANALYZA / "_archiv"

# Jednorázovky P8/P9 — pracují na STARÉM stromě, přesun je hotový.
ARCHIVOVAT = [
    "p1-kdo-chybi.py", "p1-rozdil-mnozin.py", "p1-rozdil-proti-planu.py",
    "p5-presun.py", "p8-oprava-cest.py", "p8b-oprava-analyza.py",
    "p8b-zjisti-zive.py", "p8d-oprava-skladanych-cest.py",
    # ── doplněno měřením (H55): tytéž jednorázovky, jen je zadání nejmenovalo ──
    "p8b-archivace.py", "p8c-sjednot-hlavicky.py", "p8e-najdi-nedoresene.py",
    "p8f-oprav-hra.py", "p8m-kontrola-promennych.py", "p9-presun-dokumentu.py",
]

# Živé soubory, ve kterých se hledá odkaz na archivovaný nástroj.
ZIVE = ["_analyza/g3-brany.py", "tools/validate-all.mjs", "AGENTS.md",
        "tools/verify-setup.py", "_analyza/hl-rizika-jazyka.py",
        "_analyza/kronika-kontrola.py", "tools/over-dokumentaci.py"]


def main() -> int:
    # 1) KONTROLA: existuje zdroj, neexistuje cíl, nikdo na něj nesahá.
    nalezy = []
    for n in ARCHIVOVAT:
        zdroj = ANALYZA / n
        cil = ARCHIV / n
        if not zdroj.is_file():
            if cil.is_file():
                print(f"  (už archivováno: {n})")
                continue
            nalezy.append(f"{n}: NENÍ ani v _analyza/, ani v _archiv/")
            continue
        if cil.exists():
            nalezy.append(f"{n}: v _archiv/ UŽ JE — přesun by přepsal záznam")
            continue
        # Sahá na něj nějaký živý soubor?
        for z in ZIVE:
            p = WS / z
            if not p.is_file():
                continue
            if n in p.read_text(encoding="utf-8", errors="replace"):
                nalezy.append(f"{n}: zmiňuje ho ŽIVÝ soubor {z} — nearchivuji")
    if nalezy:
        print("NÁLEZY PŘED PŘESUNEM (nepřesouvám nic):")
        for x in nalezy:
            print("  " + x)
        return 2

    # 2) PŘESUN (kopie + ověření + smazání zdroje).
    presunuto = []
    for n in ARCHIVOVAT:
        zdroj = ANALYZA / n
        cil = ARCHIV / n
        if not zdroj.is_file():
            continue
        puvodni = zdroj.read_bytes()
        shutil.copy2(zdroj, cil)
        assert cil.read_bytes() == puvodni, f"{n}: kopie NESOUHLASÍ s originálem"
        zdroj.unlink()
        assert not zdroj.exists(), f"{n}: zdroj po přesunu ZŮSTAL"
        assert (ARCHIV / n).is_file(), f"{n}: v archivu NENÍ"
        presunuto.append(n)
        print(f"  archivováno: {n}  ({len(puvodni)} B)")

    print()
    print(f"VÝSLEDEK: {len(presunuto)} jednorázovek P8/P9 přesunuto do _analyza/_archiv/")
    print("          (záznam o archivaci: _analyza/_archiv/CO-SE-ARCHIVOVALO.md)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

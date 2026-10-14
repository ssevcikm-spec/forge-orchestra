#!/usr/bin/env python3
"""K6: testy nastroju, ktere lezi v HRACH, se musi opravdu spustit a byt zelene.

PROC TO EXISTUJE (namereno 14. 10. 2026, session K6):
  Orchestra kopiruje `.forge/node/*` i do her (`tools/forge-new.mjs` kopiruje
  cely `repo/`, K4). Jenze testy, ktere se tim do hry dostanou, v hre NIKDO
  nespousti: herni `ci.yml` pousti Godot testy, `check-schema.py`,
  `check-assets.py`, `check-wiring.py` a vision - ale zadny `*.test.mjs`.
  V orchestre je pritom hlida `g3` (v SABLONE) - takze v hre je to mrtva kopie,
  ktera vypada jako brana. Presne trida "brana, ktera neprobehne, neni brana".

  A jedna z tech kopii se v hre ani NEDA spustit: namereno 14. 10. 2026 v
  `coin-picker` - `.forge/node/priprava.test.mjs:130` cte
  `.forge/roadmap.pilot.json`, ale ten se do hry nikdy nezkopiroval (fixtura
  bydlela jen v sablone `repo/.forge/`). Test proto spadl na ENOENT a vsechny
  kontroly za radkem 130 (cely oddil K3 + P42, 15 z 55) se nikdy nespustily.

CO BRANA MERI:
  Pro kazdou hru (sourozenec repa orchestra) vezme VSEchny `.forge/node/*.test.mjs`,
  ktere v ni lezi, SPUSTI je a pozaduje `exit 0`. Hra se objevi ve vystupu
  i tehdy, kdyz ma testu nula - aby "0 testu" nebylo k nerozeznani od "hru jsem
  nenasel".

  Kdyz test spadne na chybejici soubor, vypise se JMENO toho souboru - to je
  konkretni vada (chybejici fixtura), ne "neco spadlo".

  ⚠ DVE PRAVIDLA PRIBÝLA 14. 10. 2026 (K7) - obe z MERENI, ne z dojmu:

  1) Zeleny test musi hlasit ASPON JEDNU NENULOVOU kontrolu. Namereno (K7,
     falesna hra): test, ktery si chybejici vstup TISE preskoci a vypise
     "PRESKOCENO: 0/0 kontrol", koncil `exit 0` a brana ho brala jako zeleny -
     pritom je to tataz trida jako H203 (kontroly se nikdy nespustily), jen se
     test nerozbil, ale preskocil. "0/0" neni zelená, je to neměřeno.
  2) Test ve VNORENE slozce (`.forge/node/sub/x.test.mjs`) je CHYBA, ne ticho.
     `glob` je nerekurzivni, takze takovy test brana vubec nevidela. Dnes
     (zmereno 14. 10. 2026) nema vnoreny test ani sablona, ani `coin-picker`,
     ani `uo-shadows` - pravidlo tedy nic nevyhazuje, jen zavira tichou diru.

POUZITI:
  python _analyza/k6-over-testy-nastroju.py                 # auto-discovery
  python _analyza/k6-over-testy-nastroju.py --hry <c1>;<c2> # kalibrace

NAVRATOVY KOD: 0 = vsechny testy zeleny; 1 = aspon jeden spadl / nic se nemerilo.
"""

import argparse
import pathlib
import re
import subprocess
import sys

WS = pathlib.Path(__file__).resolve().parent.parent   # koren repa orchestra
RODIC = WS.parent                                     # E:\Workspaces
VZOR_SOUBORU = "*.test.mjs"


def hry_ze_stromu(rodic: pathlib.Path) -> list[pathlib.Path]:
    """Sourozenecke adresare, ktere v sobe maji `.forge/node/*.test.mjs`."""
    hry = []
    if not rodic.is_dir():
        return hry
    for d in sorted(rodic.iterdir()):
        if not d.is_dir():
            continue
        if list((d / ".forge" / "node").glob(VZOR_SOUBORU)):
            hry.append(d)
    return hry


def prvni_zajimavy_radek(text: str) -> str:
    """Z chyboveho vystupu vytahni DUVOD (ne radek zdrojaku ze stacku).

    ⚠ Namereno 14. 10. 2026 (vlastni omyl): prvni verze brala proste prvni
    "nerusive" radek - a tim byl `return binding.readFileUtf8(...)`, tedy radek
    KODU z Node stacku. Vypadalo to jako duvod, ale JMENO chybejiciho souboru
    v nem nebylo; kalibracni test to chytil (`nález jmenuje CHYBĚJÍCÍ soubor`).
    Proto se nejdriv hleda radek s chybou, a teprve pak obecny fallback.
    """
    radky = [r.strip() for r in text.splitlines()]
    for r in radky:
        if re.match(r"^(?:[A-Za-z]*Error|ENOENT|EACCES|EPERM|Cannot find|Cannot read)\b", r):
            return r
    for r in radky:
        if not r or r == "^":
            continue
        if r.startswith(("at ", "node:", "return ", "throw ", "}", "{", ")", "(")):
            continue
        if re.fullmatch(r"[)\]};\s]+", r):
            continue
        return r
    return "(prazdny vystup)"


def ma_merene_kontroly(radek: str) -> bool:
    """Hlasi zeleny test aspon JEDNU skutecne provedenou kontrolu?

    ⚠ Namereno 14. 10. 2026 (K7) na falesne hre: test, ktery si chybejici vstup
    tise preskoci, vypise "PRESKOCENO: fixtura neni, 0/0 kontrol" a skonci
    `exit 0` - a brana ho hlasila jako zeleny. Vsechna cisla v souhrnu jsou
    proto druha podminka zelene: aspon jedno musi byt NENULOVE.
    (Kdyby souhrn cisla nemel vubec, je to taky "neměřeno" - brana pak hlasi
    "souhrn nehlasí ani jednu kontrolu" a to je presne to, co ma videt.)
    """
    return any(int(n) > 0 for n in re.findall(r"\d+", radek or ""))


def spust_test(hra: pathlib.Path, test: pathlib.Path) -> dict:
    rel = test.relative_to(hra).as_posix()
    try:
        r = subprocess.run(
            ["node", rel], cwd=str(hra), capture_output=True, text=True,
            encoding="utf-8", errors="replace", timeout=600,
        )
    except FileNotFoundError:
        return {"soubor": rel, "exit": None, "radek": "node nenalezen v PATH"}
    except subprocess.TimeoutExpired:
        return {"soubor": rel, "exit": None, "radek": "test neubehl do 600 s"}
    vystup = (r.stdout or "") + "\n" + (r.stderr or "")
    posledni = ""
    if r.returncode == 0:
        # U zeleneho testu hledej SOUHRN (posledni radek s cislem a slovem
        # "kontrol"/"chyb"/"vysledek"), ne prvni radek s cislem.
        for radek in (r.stdout or "").splitlines():
            if re.search(r"\d", radek) and any(
                k in radek.lower() for k in ("vysledek", "výsledek", "kontrol", "testů", "testu", "selhani", "chyb")
            ):
                posledni = radek.strip()
    # U cerveneho testu je zajimavy DUVOD (stderr), ne posledni odskrtnuta
    # kontrola - jinak by vada vypadala jako "ok ...".
    if not posledni:
        posledni = prvni_zajimavy_radek(r.stderr or vystup)
    return {
        "soubor": rel,
        "exit": r.returncode,
        "radek": posledni or prvni_zajimavy_radek(vystup),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--hry", default=None,
                    help="strednikem oddelene cesty her; jinak auto-discovery sourozencu")
    args = ap.parse_args()

    if args.hry:
        hry = [pathlib.Path(p) for p in args.hry.split(";") if p.strip()]
    else:
        hry = hry_ze_stromu(RODIC)

    print("=" * 78)
    print("K6: TESTY NASTROJU VE HRACH - spusti se a musi byt zelene")
    print("=" * 78)
    print(f"  koren her: {RODIC}" if not args.hry else "  hry zadane rucne")

    celkem = 0
    zelenych = 0
    chyb = 0
    bez_testu = []

    for hra in hry:
        zaklad = hra / ".forge" / "node"
        testy = sorted(zaklad.glob(VZOR_SOUBORU))
        vnorene = sorted(p for p in zaklad.rglob(VZOR_SOUBORU) if p.parent != zaklad)
        print(f"\n--- {hra.name} ({hra}) ---")
        if not testy and not vnorene:
            print("  ⚠ ZADNE testy (`.forge/node/*.test.mjs` tu nejsou)")
            bez_testu.append(hra.name)
            continue
        for t in testy:
            celkem += 1
            v = spust_test(hra, t)
            if v["exit"] == 0 and ma_merene_kontroly(v["radek"]):
                zelenych += 1
                print(f"  ok     {v['soubor']}: {v['radek']}")
            else:
                chyb += 1
                if v["exit"] == 0:
                    print(f"  CHYBA  {v['soubor']}: exit 0, ale souhrn nehlasi ANI "
                          f"JEDNU kontrolu (nemeneno, ne zelena) | {v['radek']}")
                else:
                    print(f"  CHYBA  {v['soubor']}: exit {v['exit']} | {v['radek']}")
        for p in vnorene:
            celkem += 1
            chyb += 1
            print(f"  CHYBA  {p.relative_to(hra).as_posix()}: test lezi ve VNORENE "
                  f"slozce -> brana ho nespousti; presun ho na uroven `.forge/node/`")

    print()
    print(f"ZMĚŘENO: {zelenych}/{celkem} testů zelených, {chyb} chyb "
          f"({len(hry)} her, z toho bez testů: {len(bez_testu)})")
    if bez_testu:
        print(f"  hry bez testů: {', '.join(bez_testu)}")

    if celkem == 0:
        print("\nCHYBA: nenašel se ANI JEDEN test nástrojů - to není zelená,")
        print("       to je neměřený stav (spatne --hry, nebo se strom prestehoval).")
        return 1
    if chyb:
        print("\nCHYBA: test nástrojů ve hře spadl - viz 'CHYBA' řádky výš.")
        print("       (Nejcastejsi pricina: test existuje, ale jeho fixtura ne.)")
        return 1
    print("\nVŠE OK: všechny testy nástrojů, které v hrách leží, se spustily a jsou zelené.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

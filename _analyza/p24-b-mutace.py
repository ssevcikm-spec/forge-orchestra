# -*- coding: utf-8 -*-
r"""P24 — ÚKOL A, DRUHÁ POLOVINA: MŮŽE TO MĚŘIDLO VŮBEC SPADNOUT?

PROČ TENHLE TEST EXISTUJE
-------------------------
Zadání P24 §2.1 to žádá výslovně: doklad musí **umět selhat** — *„mutační test:
uber v kopii dokumentu jeden nadpis a sleduj, že skript spadne“*. Bez toho by
`p24-a-overeni.py` mohl být jen dalším „zeleným nad ničím“ (past S27/H71/H87).

Test proto **mutuje KOPIE dokumentů** (živé soubory nechává být) a po každé
mutaci vyžaduje, aby měřidlo **spadlo**:

  1. kontrola tvaru — nemutované kopie musí dát `exit 0` (jinak by „spadlo po
     mutaci“ mohlo znamenat jen to, že je rozbité pořád),
  2. ubrání řádku `| **N0.3** |` z plánu agentů,
  3. ubrání hlavičky `Fáze B` z plánu rozvoje,
  4. ubrání řádku `| **B4** |` z plánu rozvoje,
  5. neexistující dokument,
  6. **ČÍSLO**: `(21/0)` → `(99/0)` — bez tohohle by kontroly čítačů mohly být
     prázdné a nikdo by to nepoznal (proto je tady `--jen-a6 --jen-brana`).

⚠ Mutace jdou přes knihovnu `_analyza/_mutace.py` (pravidlo projektu): kotva
musí být v souboru **právě 1×**, text se musí **skutečně změnit** a soubor se
**vždy vrátí** — a test to po každém případu ověří hashem.

Použití: python _analyza/p24-b-mutace.py
"""

import hashlib
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj                                            # noqa: E402

MERIDLO = ANALYZA / "p24-a-overeni.py"
SCRATCH = ANALYZA / "p24-scratch"

kontrol = 0
chyb = 0


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n          čekáno: %r\n          dáno:   %r"
          % (popis, ocekavano, zjisteno))
    return False


def spust_meridlo(*argumenty):
    """Vrátí (exit, výstup) měřidla spuštěného v kopii stromu."""
    r = subprocess.run([sys.executable, "-B", str(MERIDLO)] + list(argumenty),
                       cwd=str(WS), capture_output=True, timeout=900)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def citac(vystup):
    """Přečte `N kontrol, M chyb` z výstupu měřidla."""
    import re
    posledni = None
    for posledni in re.finditer(r"(\d+) kontrol, (\d+) chyb", vystup):
        pass
    return (int(posledni.group(1)), int(posledni.group(2))) if posledni else None


def main() -> int:
    print("=" * 78)
    print("P24/B — MUTAČNÍ TEST MĚŘIDLA p24-a-overeni.py")
    print("=" * 78)

    if not MERIDLO.is_file():
        print("CHYBA: chybí %s" % MERIDLO)
        return 1

    if SCRATCH.exists():
        shutil.rmtree(SCRATCH)
    SCRATCH.mkdir(parents=True)

    # Kopie dokumentů — měřidlo se na živé soubory neplete.
    kopie = {}
    for nazev in ("PLAN-ORCHESTRA-AI-AGENTI.md", "PLAN-ROZVOJ-ORCHESTRA.md"):
        cil = SCRATCH / nazev
        shutil.copyfile(WS / nazev, cil)
        kopie[nazev] = cil
    print("  kopie v %s" % SCRATCH.name)

    agr = ["--plan-agenti", str(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"]),
           "--plan-rozvoj", str(kopie["PLAN-ROZVOJ-ORCHESTRA.md"])]
    jen_agr = ["--plan-agenti", str(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"]),
               "--plan-rozvoj", str(kopie["PLAN-ROZVOJ-ORCHESTRA.md"])]

    # ── 0) KONTROLA ─────────────────────────────────────────────────────────
    kod, v = spust_meridlo("--jen-dokumenty", *agr)
    c = citac(v)
    check("0 KONTROLA: nemutované kopie → exit 0", kod, 0)
    check("0 KONTROLA: měřidlo vykázalo čítač", c is not None, True)
    check("0 KONTROLA: čítač má aspoň 8 kontrol (měřilo se něco)",
          (c[0] >= 8) if c else False, True)

    # ── 1) ubrat řádek N0.3 ─────────────────────────────────────────────────
    try:
        with mutuj(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"], "| **N0.3** |", "") as m:
            kod, v = spust_meridlo("--jen-dokumenty", *agr)
        check("1 změna souboru opravdu proběhla (hash před != po mutaci)",
              m.hash_pred != m.hash_po_mutaci, True)
        check("1 po UBRÁNÍ řádku N0.3 měřidlo SPADLO", kod != 0, True)
    except ValueError as e:
        check("1 mutace se provedla (%s)" % e, False, True)
    check("1 kopie je po mutaci vrácena bajt na bajt",
          hashlib.sha256(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"].read_bytes()).hexdigest(),
          hashlib.sha256((WS / "PLAN-ORCHESTRA-AI-AGENTI.md").read_bytes()).hexdigest())

    # ── 2) ubrat hlavičku fáze B ────────────────────────────────────────────
    # ⚠ KOTVA MUSÍ BÝT DELŠÍ NEŽ „Fáze B“: ta je v dokumentu 2× (nadpis oddílu
    # a věta „Fáze B znamená deploy conductora“), takže by knihovna mutaci
    # SPRÁVNĚ odmítla — a test by hlásil chybu u dokumentu, který je v pořádku.
    HLAVICKA_B = "### Fáze B — Tři vady conductoru (hodiny; zásah do běžícího systému)"
    try:
        with mutuj(kopie["PLAN-ROZVOJ-ORCHESTRA.md"], HLAVICKA_B,
                   "### Tři vady conductoru") as m:
            kod, v = spust_meridlo("--jen-dokumenty", *agr)
        check("2 změna souboru opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("2 po UBRÁNÍ hlavičky 'Fáze B' měřidlo SPADLO", kod != 0, True)
    except ValueError as e:
        check("2 mutace se provedla (%s)" % e, False, True)

    # ── 3) ubrat řádek B4 ───────────────────────────────────────────────────
    try:
        with mutuj(kopie["PLAN-ROZVOJ-ORCHESTRA.md"], "| **B4** |", "") as m:
            kod, v = spust_meridlo("--jen-dokumenty", *agr)
        check("3 změna souboru opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("3 po UBRÁNÍ řádku B4 měřidlo SPADLO", kod != 0, True)
    except ValueError as e:
        check("3 mutace se provedla (%s)" % e, False, True)

    # ── 4) neexistující dokument ────────────────────────────────────────────
    kod, v = spust_meridlo("--jen-dokumenty",
                           "--plan-agenti", str(SCRATCH / "neexistuje.md"),
                           "--plan-rozvoj", str(kopie["PLAN-ROZVOJ-ORCHESTRA.md"]))
    check("4 neexistující dokument → měřidlo SPADLO", kod != 0, True)

    # ── 5) KONTROLA ČÍSEL (musí projít na správném dokumentu) ───────────────
    kod, v = spust_meridlo("--jen-a6", "--jen-brana", "test-health-cile", *jen_agr)
    c = citac(v)
    check("5 KONTROLA: správné kopie → kontrola ČÍSEL je zelená (exit 0)", kod, 0)
    check("5 KONTROLA: kontrola čísel opravdu proběhla (má čítač)", c is not None, True)

    # ── 6) ČÍSLO v dokumentu je jiné, než co brána naměří ───────────────────
    try:
        with mutuj(kopie["PLAN-ORCHESTRA-AI-AGENTI.md"], "(21/0)", "(99/0)") as m:
            kod, v = spust_meridlo("--jen-a6", "--jen-brana", "test-health-cile",
                                   *jen_agr)
        check("6 změna ČÍSLA v dokumentu opravdu proběhla",
              m.hash_pred != m.hash_po_mutaci, True)
        check("6 po změně čísla (21/0 → 99/0) měřidlo SPADLO", kod != 0, True)
        check("6 důvod je TVRZENÍ O ČÍSLE (ne něco jiného)",
              "tvrdí naměřené" in v, True)
    except ValueError as e:
        check("6 mutace se provedla (%s)" % e, False, True)

    # ── úklid ───────────────────────────────────────────────────────────────
    shutil.rmtree(SCRATCH, ignore_errors=True)
    check("7 scratch uklizen", SCRATCH.exists(), False)

    print()
    if chyb:
        print("VÝSLEDEK: %d kontrol, %d CHYB" % (kontrol, chyb))
        return 1
    print("VÝSLEDEK: %d kontrol, 0 chyb" % kontrol)
    return 0


if __name__ == "__main__":
    sys.exit(main())

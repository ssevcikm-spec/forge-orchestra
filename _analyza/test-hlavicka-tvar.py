#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST: TVAR HLAVIČKY ZADÁNÍ je živá kontrola (ne jen komentář).

PROČ TO EXISTUJE
----------------
`_analyza/zadani-kontrola.py` čte dvojice `` `<repo>` = `<sha>` `` z **jednoho
konkrétního řádku** — z toho, který nese klíč „Stav obou repů". Když je popis
a dvojice na **dvou řádcích**, stará verze vypsala „zadání netvrdí žádný
commit" — a to **vypadá jako vada brány**, ale je to **vada ZÁPISU** (naměřeno
6. 10. 2026 archivovaným nástrojem `zadani-hlavicka-tvar.py`; od 7. 10. 2026 to
brána pojmenuje jako `TVAR HLAVIČKY: VADA`).

CO TEST MĚŘÍ (na fixturách, pět případů, opačné výsledky)
--------------------------------------------------------
  1. SPRÁVNÝ TVAR — dvojice na řádku s klíčem, tvrzené commity = živé HEADy
     → `exit 0`
  2. ZVÝRAZNĚNÍ `**` ve dvojicích → `exit 0` (falešný poplach se NESMÍ konat)
  3. DVOJICE O ŘÁDEK NÍŽ — přesně ta vada zápisu → `exit 1`
     **a ve výstupu je vidět `TVAR HLAVIČKY: VADA`** (ne dva otazníky u repů)
  4. ŘÁDEK S KLÍČEM CHYBÍ → `exit 1` a „NEMÁ řádek s klíčem"
  5. SABOTÁŽ BRÁNY — kontrola tvaru se z KÓDU odstraní a test **musí spadnout**
     (jinak test neměří nic). Nástroj se vrací **bajt na bajt**.

⚠ ČÍM SE LIŠÍ OD `test-zadani-kontrola.py`: ten mutuje **živé zadání**
(`NEXT-SESSION-INSTRUKCE.md`) a ověřuje **stárnutí** (tvrzený commit vs. HEAD).
Tenhle test mutuje **jen fixtury ve svém scratchi** a ověřuje **TVAR** — mimo
jiné proto, že živé zadání má od 7. 10. 2026 **necommitnutou práci session P24**
a sahat do ní se nesmí. Scratch se uklízí v `finally`.

Použití: python _analyza\test-hlavicka-tvar.py     (spouští se RUČNĚ)
Návrat:  0 = kontrola měří správně | 1 = nález | 2 = test sám selhal
"""

import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "zadani-kontrola.py"
SCRATCH = WS / "_analyza" / "_scratch-hlavicka"
GIT = WS / "tools" / "git.cmd"
HRA = WS.parent / "uo-shadows"

# ⚠ KOTVA SABOTÁŽE: `elif not dvojice:` je v bráně PRÁVĚ JEDNOU (kdyby se
# přesunula, `mutuj`-podmínka níž to řekne — místo tichého „test prošel").
KOTVA_TVARU = "elif not dvojice:"
SABOTAZ_TVARU = "elif False:  # SABOTAZ: kontrola tvaru vypnuta"

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}")
        if detail:
            for radek in detail.splitlines():
                print(f"        {radek}")


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), *args],
                       capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust_branu(soubor: pathlib.Path) -> tuple:
    r = subprocess.run([sys.executable, str(BRANA), "--soubor", str(soubor)],
                       capture_output=True, cwd=str(WS), timeout=300)
    v = ((r.stdout or b"").decode("utf-8", "replace")
         + (r.stderr or b"").decode("utf-8", "replace"))
    return r.returncode, v


def fixtura(jmeno: str, hlavicka: str, zbytek: str = "Zbytek zadání.\n") -> pathlib.Path:
    cesta = SCRATCH / jmeno
    cesta.write_text(f"# ZADÁNÍ (fixtura testu tvaru)\n\n{hlavicka}\n\n{zbytek}",
                     encoding="utf-8", newline="")
    return cesta


def main() -> int:
    if not BRANA.is_file():
        print(f"CHYBA: brána {BRANA} neexistuje")
        return 2

    head_orch = git(WS, "rev-parse", "--short", "HEAD")
    head_hra = git(HRA, "rev-parse", "--short", "HEAD")
    if not head_orch or not head_hra:
        print("CHYBA: nepodařilo se přečíst živé HEADy obou repů")
        return 2

    shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    puvodni_brana = BRANA.read_bytes()
    try:
        print("=" * 74)
        print("TEST TVARU HLAVIČKY: měří `zadani-kontrola.py` tvar, nebo mlčí?")
        print("=" * 74)
        print(f"  živé HEADy: forge-orchestra={head_orch}  uo-shadows={head_hra}")
        print(f"  scratch:    {SCRATCH}  (živé zadání se NEMUTUJE)")
        print()

        dvojice = (f"`forge-orchestra` = `{head_orch}` · "
                   f"`uo-shadows` = `{head_hra}`")

        # ── 1) SPRÁVNÝ TVAR ─────────────────────────────────────────────────
        print("--- 1) dvojice na řádku s klíčem → očekávám exit 0 ---")
        dobra = fixtura("dobra.md", f"**Stav obou repů při psaní:** {dvojice}")
        kod, v = spust_branu(dobra)
        zkontroluj("správný tvar → exit 0", kod == 0, f"exit={kod}")
        zkontroluj("brána tvar vysloví jako OK",
                   "TVAR HLAVIČKY: OK" in v,
                   "\n".join(l.strip() for l in v.splitlines() if "TVAR" in l))
        zkontroluj("dvojice se SKUTEČNĚ přečtou (2, ne 0)",
                   "dvojic `<repo>` = `<sha>` na tom řádku: 2" in v,
                   "\n".join(l.strip() for l in v.splitlines() if "dvojic" in l))

        # ── 2) ZVÝRAZNĚNÍ `**` (falešný poplach se nesmí konat) ─────────────
        print()
        print("--- 2) dvojice se zvýrazněním `**` → očekávám exit 0 ---")
        zvyraznena = fixtura(
            "zvyraznena.md",
            f"**Stav obou repů při psaní:** `forge-orchestra` = **`{head_orch}`** · "
            f"**`uo-shadows`** = **`{head_hra}`**")
        kod, v = spust_branu(zvyraznena)
        zkontroluj("dvojice se zvýrazněním `**` → exit 0", kod == 0, f"exit={kod}")
        zkontroluj("vzor zvýraznění PŘEŽIL (2 dvojice, ne 0)",
                   "dvojic `<repo>` = `<sha>` na tom řádku: 2" in v,
                   "\n".join(l.strip() for l in v.splitlines() if "dvojic" in l))

        # ── 3) DVOJICE O ŘÁDEK NÍŽ — přesně ta vada zápisu ──────────────────
        print()
        print("--- 3) dvojice o řádek níž → očekávám exit 1 a TVAR: VADA ---")
        posunuta = fixtura(
            "posunuta.md",
            f"**Stav obou repů při psaní:**\n{dvojice}")
        kod, v = spust_branu(posunuta)
        zkontroluj("dvojice o řádek níž → exit 1", kod == 1, f"exit={kod}")
        zkontroluj("brána to pojmenuje jako VADU TVARU (ne dva otazníky u repů)",
                   "TVAR HLAVIČKY: VADA" in v,
                   "\n".join(l.strip() for l in v.splitlines()
                             if "TVAR" in l or "netvrdí" in l))
        zkontroluj("a vysvětlí, že je to vada ZÁPISU",
                   "VADA ZÁPISU, NE NESHODA COMMITŮ" in v,
                   "\n".join(l.strip() for l in v.splitlines()
                             if "ZÁPISU" in l or "HLAVIČKU" in l))

        # ── 4) ŘÁDEK S KLÍČEM CHYBÍ ─────────────────────────────────────────
        print()
        print("--- 4) hlavička bez klíčového řádku → očekávám exit 1 ---")
        bez_klice = fixtura("bez-klice.md", "**Napsáno:** 7. 10. 2026")
        kod, v = spust_branu(bez_klice)
        zkontroluj("chybějící řádek s klíčem → exit 1", kod == 1, f"exit={kod}")
        zkontroluj("a je pojmenovaný (NEMÁ řádek s klíčem)",
                   "NEMÁ řádek s klíčem" in v,
                   "\n".join(l.strip() for l in v.splitlines() if "TVAR" in l))

        # ── 5) SABOTÁŽ BRÁNY: bez kontroly tvaru musí test SPADNOUT ─────────
        print()
        print("--- 5) sabotáž: kontrola tvaru se z brány ODSTRANÍ ---")
        pocet = puvodni_brana.decode("utf-8").count(KOTVA_TVARU)
        zkontroluj("kotva sabotáže je v bráně PRÁVĚ 1×", pocet == 1,
                   f"nalezeno {pocet}× — sabotáž by se tiše neprovedla")
        if pocet == 1:
            zmutovana = puvodni_brana.decode("utf-8").replace(
                KOTVA_TVARU, SABOTAZ_TVARU).encode("utf-8")
            zkontroluj("mutace změnila text (ne jen bajty)",
                       zmutovana != puvodni_brana and SABOTAZ_TVARU.encode() in zmutovana)
            try:
                BRANA.write_bytes(zmutovana)
                zkontroluj("mutace se PROPSALA na disk",
                           BRANA.read_bytes() == zmutovana)
                kod, v = spust_branu(posunuta)
                zkontroluj("se sabotovanou bránou případ 3 NEPROJDE",
                           "TVAR HLAVIČKY: VADA" not in v,
                           "\n".join(l.strip() for l in v.splitlines()
                                     if "TVAR" in l or "netvrdí" in l))
            finally:
                BRANA.write_bytes(puvodni_brana)
            zkontroluj("brána vrácena BAJT NA BAJT",
                       BRANA.read_bytes() == puvodni_brana)
            # a po návratu musí platit to, co předtím (test není jednorázový)
            kod, v = spust_branu(posunuta)
            zkontroluj("po návratu brána vadu zase VIDÍ", kod == 1
                       and "TVAR HLAVIČKY: VADA" in v, f"exit={kod}")
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        if BRANA.read_bytes() != puvodni_brana:
            BRANA.write_bytes(puvodni_brana)
            print("  ⚠ brána vrácena v `finally` (sabotáž zůstala nedokončená)")
        assert BRANA.read_bytes() == puvodni_brana, "BRÁNA NEVRÁCENA BAJT NA BAJT!"

    print()
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb   (scratch uklizen, brána vrácena)")
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

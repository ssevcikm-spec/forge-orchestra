#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P40 / H195 — TEST: fixtura po PŘERUŠENÍ nezůstane v repu HRY.

PROČ TO EXISTUJE (H195, naměřeno P39, opraveno P40)
---------------------------------------------------
`_analyza/p20-b2-kontroly.py` si vyrábí fixturu **v CIZÍM REPU HRY**
(`E:\Workspaces\uo-shadows\scripts\_p20_b2_necitelny.py`) — a do P40 ji uklízel
až na **konci skriptu**, tedy mimo `try/finally`. Přerušený běh (výjimka,
Ctrl-C) tam nechal **nečitelný `.py` v `scripts/`** — a dávka
`p20-d-doklady.py` ten skript **pouští**. Navíc by další běh měřil jiný stav.

CO TEST MĚŘÍ (jádro je krok 2)
------------------------------
  1. PLNÝ NORMÁLNÍ BĚH (bez přepínače) → `exit 0` (jako P39), fixtura NENÍ,
     strom hry ČISTÝ. (Oprava nesmí rozbít zdravý běh.)
  2. PŘERUŠENÍ: běh s `--vynut-vyjimku` vyhodí výjimku UVNITŘ `try` →
     `exit != 0` a text výjimky je ve výstupu (důkaz, že se NEPOLKLA),
     **fixtura v repu hry NENÍ** a strom hry je ČISTÝ. ← TOHLE JE H195.
  3. Totéž přes `P40_H195_VYNUT=1` (druhá cesta k témuž; přepínač, který se
     tiše ignoruje, by dělal test slepým).
  4. MUTACE: do ŽIVÉ brány se vrátí VADA (úklid mimo `finally`) →
     s přerušením **fixtura ZŮSTANE** (test by na kroku 2 SPADL),
     ale NORMÁLNÍ běh se uklidí i s vadou (vada je v PŘERUŠENÉ cestě).
     Fixtura se po mutantovi ručně uklidí a strom se ověří.
  5. Po vrácení brány (bajt na bajt, sha256) krok 2 zase platí.

⚠ Do `E:\Workspaces\uo-shadows` se sahá JEN fixturou brány samotné (to je
jediná výjimka povolená zadáním) + `git status`, který nic nemění. Fixtura se
po každém kroku ověřuje a uklízí i v `finally` TOHOTO testu.

Použití: python _analyza\p40-h195-test.py
Návrat:  0 = úklid měří správně | 1 = nález | 2 = test sám selhal
"""

import hashlib
import os
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
BRANA = ANALYZA / "p20-b2-kontroly.py"
HRA = WS.parent / "uo-shadows"
FIXTURA = HRA / "scripts" / "_p20_b2_necitelny.py"
GIT = str(WS / "tools" / "git.cmd")
PY = sys.executable

# ⚠ KOTVA MUTACE = přesně ta vada H195: úklid je MIMO `finally`. Mutace dá do
# `finally` `pass` a `unlink` postaví ZA blok — přesně stav do P40.
# (Kotva je JEDEN řádek včetně odsazení: mezi `finally:` a úklidem jsou
# v bráně ještě dva komentáře, takže kotva přes tři řádky by nenašla nic —
# a `_mutace.mutuj` by to řekl nahlas, ne tiše.)
KOTVA_VADY = "    FIXTURA.unlink(missing_ok=True)"
VADA = ("    pass  # H195-MUTACE: uklid ODSUD VEN (puvodni vada)\n"
        "FIXTURA.unlink(missing_ok=True)")

sys.path.insert(0, str(ANALYZA))
try:
    from _mutace import mutuj
except ImportError as _e:  # instalace projektu, ne test
    print(f"CHYBA: knihovna `_mutace` není k dispozici ({_e})")
    sys.exit(2)

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
            for l in str(detail).splitlines()[-14:]:
                print(f"        {l}")


def git_status() -> str:
    r = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                       capture_output=True, shell=True, timeout=120)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust(*, vynut: bool, env_vynut: bool = False) -> tuple:
    """Spustí ŽIVOU bránu. `vynut` = přepínač, `env_vynut` = proměnná prostředí."""
    prikaz = [PY, "-B", str(BRANA)]
    env = dict(os.environ)
    if vynut:
        prikaz.append("--vynut-vyjimku")
    if env_vynut:
        env["P40_H195_VYNUT"] = "1"
    r = subprocess.run(prikaz, capture_output=True, cwd=str(WS), env=env,
                       timeout=900)
    v = ((r.stdout or b"").decode("utf-8", "replace")
         + (r.stderr or b"").decode("utf-8", "replace"))
    return r.returncode, v


def main() -> int:
    global chyb
    if not BRANA.is_file():
        print(f"CHYBA: brána {BRANA} neexistuje")
        return 2

    puvodni = BRANA.read_bytes()
    puvodni_sha = hashlib.sha256(puvodni).hexdigest()
    zaklad = git_status()

    print("=" * 78)
    print("P40 / H195 — zůstane fixtura po PŘERUŠENÍ v repu hry?")
    print("=" * 78)
    print(f"  brána:   {BRANA}")
    print(f"  fixtura: {FIXTURA}   (repo hry = CIZÍ)")
    print(f"  strom hry na začátku: {zaklad!r}")
    print(f"  sha256 brány: {puvodni_sha[:16]}")
    print()

    try:
        # ── 0) VÝCHOZÍ STAV ────────────────────────────────────────────────
        print("--- 0) výchozí stav: fixtura tam NENÍ a strom je čistý ---------")
        zkontroluj("na začátku v repu hry fixtura NENÍ", not FIXTURA.exists(),
                   f"existuje={FIXTURA.exists()}")
        zkontroluj("a strom hry je ČISTÝ (jinak by test měřil cizí změny)",
                   zaklad == "", f"git status:\n{zaklad}")

        # ── 1) PLNÝ NORMÁLNÍ BĚH ───────────────────────────────────────────
        print()
        print("--- 1) PLNÝ normální běh (bez přepínače) → exit 0 -----------------")
        rc1, v1 = spust(vynut=False)
        zkontroluj("normální běh → exit 0 (jako P39: zdravý strom)", rc1 == 0,
                   f"exit={rc1}\n" + "\n".join(v1.splitlines()[-6:]))
        zkontroluj("fixtura po normálním běhu NENÍ", not FIXTURA.exists())
        zkontroluj("strom hry je po normálním běhu ČISTÝ", git_status() == zaklad,
                   repr(git_status()))

        # ── 2) PŘERUŠENÍ — JÁDRO H195 ──────────────────────────────────────
        print()
        print("--- 2) PŘERUŠENÍ uvnitř `try` → výjimka, ale ÚKLID -------------")
        rc2, v2 = spust(vynut=True)
        zkontroluj("přerušený běh → exit != 0 (výjimka NEBYLA spolknutá)",
                   rc2 != 0, f"exit={rc2}")
        zkontroluj("výstup nese vynucenou výjimku (přepínač funguje, není tichý)",
                   "vynucená výjimka UVNITŘ" in v2 and "RuntimeError" in v2,
                   "\n".join(v2.splitlines()[-8:]))
        zkontroluj("H195: po PŘERUŠENÍ fixtura v repu hry NENÍ",
                   not FIXTURA.exists(), f"existuje={FIXTURA.exists()} ({FIXTURA})")
        zkontroluj("H195: strom hry je po PŘERUŠENÍ ČISTÝ",
                   git_status() == zaklad, repr(git_status()))

        # ── 3) DRUHÁ CESTA: proměnná prostředí ─────────────────────────────
        print()
        print("--- 3) totéž přes `P40_H195_VYNUT=1` -----------------------------")
        rc3, v3 = spust(vynut=False, env_vynut=True)
        zkontroluj("env proměnná vyvolá výjimku (exit != 0)", rc3 != 0, f"exit={rc3}")
        zkontroluj("a fixtura po ní NENÍ", not FIXTURA.exists())
        zkontroluj("ani po ní nezůstala změna ve stromě hry",
                   git_status() == zaklad, repr(git_status()))

        # ── 4) MUTACE: úklid mimo `finally` ───────────────────────────────
        print()
        print("--- 4) MUTACE: úklid se vytlačí MIMO `finally` -------------------")
        try:
            with mutuj(BRANA, KOTVA_VADY, VADA) as m:
                zkontroluj("mutace se PROPSALA (hash se změnil)",
                           m.hash_po_mutaci != m.hash_pred)
                zkontroluj("kotva vady (úklid mimo finally) je v souboru",
                           "H195-MUTACE" in BRANA.read_text(encoding="utf-8"))
                # 4a) PŘERUŠENÝ běh s vrácenou vadou → fixtura MUSÍ ZŮSTAT
                rc4, v4 = spust(vynut=True)
                zustala = FIXTURA.exists()
                zkontroluj("MUTACE: přerušený běh pořád spadne (exit != 0)",
                           rc4 != 0, f"exit={rc4}")
                zkontroluj("MUTACE: fixtura po PŘERUŠENÍ ZŮSTALA "
                           "(= test by na kroku 2 SPADL)",
                           zustala, f"existuje={zustala} ({FIXTURA})")
                zkontroluj("MUTACE: strom hry je tím PONIČENÝ "
                           "(přesně to je vada H195)",
                           git_status() != zaklad,
                           "git status: " + repr(git_status()))
                # ⚠ úklid po mutantovi — jinak by test nechal cizí repo špinavé
                FIXTURA.unlink(missing_ok=True)
                zkontroluj("po ručním úklidu je strom hry zase ČISTÝ",
                           git_status() == zaklad, repr(git_status()))
                # 4b) NORMÁLNÍ běh s vrácenou vadou → uklidí se i tak
                #     (vada je v PŘERUŠENÉ cestě, ne v celé bráně)
                rc5, v5 = spust(vynut=False)
                zkontroluj("MUTACE: NORMÁLNÍ běh se uklidí i s vadou "
                           "(vada je v přerušené cestě)",
                           not FIXTURA.exists() and git_status() == zaklad,
                           f"existuje={FIXTURA.exists()}\n" + "\n".join(v5.splitlines()[-6:]))
            zkontroluj("brána vrácena BAJT NA BAJT (sha256)",
                       hashlib.sha256(BRANA.read_bytes()).hexdigest() == puvodni_sha)
        except ValueError as e:
            zkontroluj("mutace se provedla a soubor vrátila", False, f"{e}")

        # ── 5) PO VRÁCENÍ ─────────────────────────────────────────────────
        print()
        print("--- 5) po vrácení brány krok 2 zase platí -----------------------")
        rc6, v6 = spust(vynut=True)
        zkontroluj("po vrácení: přerušený běh spadne a fixtura NENÍ",
                   rc6 != 0 and not FIXTURA.exists(), f"exit={rc6}")
        zkontroluj("a strom hry je ČISTÝ", git_status() == zaklad, repr(git_status()))
    finally:
        # ⚠ POJISTKA TOHOTO TESTU: kdyby cokoli výš selhalo (i Ctrl-C), fixtura
        # v CIZÍM repu nesmí zůstat.
        if FIXTURA.exists():
            FIXTURA.unlink(missing_ok=True)
            print("  ⚠ fixtura uklizena v `finally` TESTU (běh zůstal nedokončený)")
        if BRANA.read_bytes() != puvodni:
            BRANA.write_bytes(puvodni)
            print("  ⚠ brána vrácena v `finally` (mutace zůstala nedokončená)")
        if git_status() != zaklad:
            print(f"  ⚠ POZOR: strom hry se liší od výchozího stavu! {git_status()!r}")

    # ── TVRDÉ PODMÍNKY ─────────────────────────────────────────────────────
    if FIXTURA.exists():
        chyb += 1
        print("  CHYBA fixtura v repu hry ZŮSTALA!")
    if BRANA.read_bytes() != puvodni:
        chyb += 1
        print("  CHYBA brána NENÍ vrácena bajt na bajt!")
    assert not FIXTURA.exists(), "FIXTURA ZŮSTALA V REPU HRY!"
    assert hashlib.sha256(BRANA.read_bytes()).hexdigest() == puvodni_sha, \
        "BRÁNA NEVRÁCENA BAJT NA BAJT!"

    print()
    print("=" * 78)
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb   "
          f"(fixtura uklizena, brána vrácena, strom hry {git_status()!r})")
    print("=" * 78)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

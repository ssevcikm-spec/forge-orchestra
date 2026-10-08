# -*- coding: utf-8 -*-
r"""P28 — OBNOVA SMAZANÉHO ZÁZNAMU V KRONICE (řádek session **24**).

CO SE NAMĚŘILO (8. 10. 2026, P28):
  * `KRONIKA-PROJEKTU.md` má **41 řádků session** s id **1..42** — **id 24 CHYBÍ**;
  * `git show c3ee946 -- KRONIKA-PROJEKTU.md` ukazuje, že ten commit řádek
    **`-| **24** | 4. 10. 2026 17:0x–20:1x | plánovací (validační) | Přesun
    obecných pravidel do DSH_HOME …`** **SMAZAL** a na jeho místo vložil řádek 25;
  * text smazaného řádku se v živé kronice **nevyskytuje** (fráze „obecných
    pravidel" → **0 výskytů**), ale je **dohledatelný v gitu** (`411f0bb`);
  * **žádná brána to neviděla**: `kronika-kontrola.py` kontroluje počet řádků
    (≥ 10), datum a typ — **kontinuitu id NE** (nález P28-E).

CO TENHLE SKRIPT DĚLÁ: vrátí řádek **24** na jeho místo (mezi 23 a 25) **bajt na
bajt tak, jak byl** v `411f0bb`, a nic jiného nemění. Je **idempotentní**:
když řádek 24 v kronice je, jen to ověří a skončí.

⚠ PROČ SKRIPTEM A NE RUČNĚ: řádky kroniky mají **přes 2000 znaků** a kotva
načtená z řádku ho zkrátí (omyly **194** a **206**). Skript proto pracuje
s **bajty** a ověřuje **sha256** vloženého řádku proti gitu.

Použití:
    python _analyza/p28-obnov-kroniku.py            # obnoví (nebo ověří)
    python _analyza/p28-obnov-kroniku.py --kontrola # jen ověří, nic nezapíše
"""
import argparse
import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
GIT = WS / "tools" / "git.cmd"
PRVNI_COMMIT = "411f0bb"      # commit, který řádek 24 PŘIDAL (je v něm celý text)
SMAZANY_COMMIT = "c3ee946"    # commit, který ho SMAZAL (doklad nálezu P28-E)
RADEK_ID = re.compile(r"^\|\s*\*\*(\d+)\*\*\s*\|")

kontrol = 0
chyb = 0


def k(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
    else:
        chyb += 1
        print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
              % (popis, ocekavano, zjisteno))


def git_show(rev, cesta):
    # ⚠ `git.cmd` je batka → potřebuje shell; cesty se proto QUOTUJÍ.
    cmd = '"%s" -C "%s" show %s:%s' % (GIT, WS, rev, cesta)
    r = subprocess.run(cmd, capture_output=True, shell=True, timeout=300)
    if r.returncode != 0:
        return None
    return r.stdout


def radky_session(text):
    return [l for l in text.splitlines() if RADEK_ID.match(l)]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true", help="jen ověřit, nezapisovat")
    args = ap.parse_args()

    print("=" * 78)
    print("P28 — obnova smazaného řádku session 24 v kronice")
    print("=" * 78)
    puvodni = KRONIKA.read_bytes()
    text = puvodni.decode("utf-8")
    k("kronika je LF (žádné CRLF)", text.count("\r\n"), 0)

    dnes = radky_session(text)
    ids = [int(RADEK_ID.match(l).group(1)) for l in dnes]
    chybejici = [i for i in range(1, max(ids) + 1) if i not in ids]
    print("      dnes: %d řádků, chybějící id: %s" % (len(dnes), chybejici or "(žádné)"))

    stary = git_show(PRVNI_COMMIT, "KRONIKA-PROJEKTU.md")
    if stary is None:
        print("  ??    NEMĚŘENO: `git show %s:KRONIKA-PROJEKTU.md` selhalo" % PRVNI_COMMIT)
        return 1
    stary_text = stary.decode("utf-8")
    radky24 = [l for l in stary_text.splitlines() if RADEK_ID.match(l)
               and RADEK_ID.match(l).group(1) == "24"]
    k("řádek 24 existuje v commitu %s právě 1×" % PRVNI_COMMIT, len(radky24), 1)
    if len(radky24) != 1:
        return 1
    radek24 = radky24[0]
    print("      řádek 24: %d znaků, začátek: %s" % (len(radek24), radek24[:90]))

    if 24 in ids:
        k("řádek 24 už v kronice JE (obnova není potřeba)", True, True)
        k("a jeho text je SHODNÝ s gitem", 24 in ids and
          any(RADEK_ID.match(l).group(1) == "24" and l == radek24 for l in dnes), True)
        return 0 if chyb == 0 else 1

    # ── kam vložit: hned za řádek 23 (tabulka je řazená podle id) ───────────
    m23 = None
    for l in dnes:
        if RADEK_ID.match(l).group(1) == "23":
            m23 = l
    if m23 is None:
        print("  ??    NEMĚŘENO: řádek 23 v kronice není — nevím, kam vložit")
        return 1
    k("kotva (řádek 23) je v souboru právě 1×", text.count(m23), 1)
    if text.count(m23) != 1:
        return 1

    novy = text.replace(m23, m23 + "\n" + radek24, 1)
    if not args.kontrola:
        KRONIKA.write_bytes(novy.encode("utf-8"))
        zpet = KRONIKA.read_bytes().decode("utf-8")
        k("zápis proběhl a řádek 24 je v souboru", bool(
            [l for l in radky_session(zpet) if RADEK_ID.match(l).group(1) == "24"]), True)
        vlozeny = [l for l in radky_session(zpet) if RADEK_ID.match(l).group(1) == "24"][0]
        k("vložený řádek je BAJT NA BAJT původní (sha256)",
          hashlib.sha256(vlozeny.encode("utf-8")).hexdigest(),
          hashlib.sha256(radek24.encode("utf-8")).hexdigest())
        nove_ids = [int(RADEK_ID.match(l).group(1)) for l in radky_session(zpet)]
        k("id jsou po obnově 1..N BEZ DĚR",
          [i for i in range(1, max(nove_ids) + 1) if i not in nove_ids], [])
        k("počet řádků vzrostl PRÁVĚ o 1", len(nove_ids), len(ids) + 1)
        # nic jiného se nesmí změnit: rozdíl musí být JEDEN přidaný řádek
        stary_set = set(dnes)
        nove_set = set(radky_session(zpet))
        k("žádný jiný řádek se nezměnil ani nezmizel", sorted(nove_set - stary_set), [radek24])
        k("a nic neubylo", sorted(stary_set - nove_set), [])
    else:
        print("      (--kontrola: nic se nezapsalo)")

    print("\nVÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

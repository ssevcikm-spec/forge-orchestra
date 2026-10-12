#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P40 / H189 — TEST: brána `zadani-kontrola.py` čte dvojice z CELÉHO BLOKU.

PROČ TO EXISTUJE (H189, naměřeno P38/P39, opraveno P40)
-------------------------------------------------------
`_analyza/zadani-kontrola.py` čítal dvojice `` `<repo>` = `<sha>` `` **jen
z JEDNOHO řádku** — z toho s klíčem „Stav obou repů". Zalomená hlavička dala na
ten řádek jen `forge-orchestra` a `uo-shadows` skončilo na dalším → **tvrzení
o HŘE se neporovnalo VŮBEC** (naměřeno P38: `dvojic = 1`). A protože `g3` má
`zadání kontrola` v `OCEKAVANE_NENULOVE`, červená byla „deklarovaná" a vada se
nikdy neprojevila.

CO TEST MĚŘÍ (fixtury, které si sám vyrábí a uklízí)
---------------------------------------------------
  1. JEDNOŘÁDKOVÁ hlavička (obě dvojice na řádku s klíčem) → `exit 0`,
     okno = 1 řádek, obě dvojice porovnané. (Chování jako dnes.)
  2. DVOUŘÁDKOVÁ hlavička (druhé repo na dalším řádku) → **`exit 0` a hra se
     SKUTEČNĚ POROVNÁ** — to je jádro H189. Na řádku s klíčem je dvojice 1,
     v CELÉM BLOKU 2.
  3. DVOUŘÁDKOVÁ hlavička se STAROU sha hry → `exit 1` a **pojmenovaný rozchod
     hry** (kdyby se hra neporovnávala, tohle by nevyšlo).
  4. HLAVIČKA BEZ KLÍČE → `exit 1` + „NEMÁ řádek s klíčem", okno = 0 řádků.
  5. KLÍČ BEZ DVOJIC (a nic na dalším řádku) → `exit 1` + `TVAR HLAVIČKY: VADA`
     (význam staré kontroly tvaru se NESMÍ ztratit).
  6. TERMINÁTORY: `Kotva pro měření` i `Zkontrolováno při` nesou dvojice
     v TÉMŽ TVARU — ale se STAROU sha. Kdyby se do bloku připletly, přebily by
     živé tvrzení → test proto čeká `exit 0` (blok končí PRVNÍM z nich).
  7. KONFLIKT v bloku (týž repo 2× s různou sha) → `exit 1` a hlášení
     „je DVAKRÁT s různou sha" (tichý přepis je horší než hlasitá vada).

  + MUTACE: do ŽIVÉ brány se vrátí VADA (dvojice se čtou z jednoho řádku)
    a test na případu 2 **MUSÍ ZČERVENAT** (hra se neporovná). Soubor se vrací
    bajt na bajt v `try/finally` a na konci se ověří SHA-256.

Do ŽIVÉHO `NEXT-SESSION-INSTRUKCE.md` se NESAHÁ (patří této session); používají
se fixtury v `_analyza/_scratch-h189/`, které se v `finally` uklidí.

Použití: python _analyza\p40-h189-test.py
Návrat:  0 = brána měří správně | 1 = nález | 2 = test sám selhal
"""

import hashlib
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
BRANA = ANALYZA / "zadani-kontrola.py"
SCRATCH = ANALYZA / "_scratch-h189"
GIT = WS / "tools" / "git.cmd"
HRA = WS.parent / "uo-shadows"
PY = sys.executable

# ⚠ KOTVA MUTACE: `dvojice_bloku` se čte z CELÉHO bloku (oprava H189).
# Mutace vrátí PŮVODNÍ vadu: čte se z jednoho řádku.
KOTVA_MUTACE = "dvojice_bloku = VZOR_DVOJICE.findall(text_bloku)"
VADA_MUTACE = ('dvojice_bloku = VZOR_DVOJICE.findall('
               'radek_stavu if radek_stavu else "")')

kontrol = 0
chyb = 0

# ⚠ Knihovna mutací se importuje odsud (ne vlastním `replace()`): hlídá, že
# kotva je v souboru právě 1×, že se text skutečně změnil a že se soubor VŽDY
# vrátí bajt na bajt. Bez ní by test mohl „projít" nad nezměněným souborem.
sys.path.insert(0, str(ANALYZA))
try:
    from _mutace import mutuj
except ImportError as _e:  # pragma: no cover — instalace projektu, ne test
    print(f"CHYBA: knihovna `_mutace` není k dispozici ({_e}) — test nemá čím měřit")
    sys.exit(2)


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK    {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}")
        if detail:
            for radek in str(detail).splitlines()[:12]:
                print(f"        {radek}")


def git(repo: pathlib.Path, *args: str) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), *args],
                       capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust(fixtura: pathlib.Path) -> tuple:
    """Spustí ŽIVOU bránu nad fixturou; vrací (exit, stdout+stderr)."""
    r = subprocess.run([PY, "-B", str(BRANA), "--soubor", str(fixtura)],
                       capture_output=True, cwd=str(WS), timeout=300)
    v = ((r.stdout or b"").decode("utf-8", "replace")
         + (r.stderr or b"").decode("utf-8", "replace"))
    return r.returncode, v


def fixtura(jmeno: str, obsah: str) -> pathlib.Path:
    cesta = SCRATCH / jmeno
    cesta.write_text(obsah, encoding="utf-8", newline="")
    return cesta


def show(v: str) -> str:
    """Jen řádky, které nesou rozhodnutí — do detailu u chyby."""
    return "\n".join(l.strip() for l in v.splitlines()
                     if any(k in l for k in ("dvojic", "OKNO", "TVAR", "OK  ",
                                             "⚠", "?", "VÝSLEDEK")))


def main() -> int:
    global chyb  # `chyb` se zvyšuje i v „TVRDÝCH PODMÍNKÁCH" na konci
    if not BRANA.is_file():
        print(f"CHYBA: brána {BRANA} neexistuje")
        return 2

    head_orch = git(WS, "rev-parse", "--short", "HEAD")
    head_hra = git(HRA, "rev-parse", "--short", "HEAD")
    stara_hra = git(HRA, "rev-parse", "--short", "HEAD~1")
    stara_orch = git(WS, "rev-parse", "--short", "HEAD~1")
    if not (head_orch and head_hra and stara_hra and stara_orch):
        print("CHYBA: nepodařilo se přečíst živé HEADy (nebo jejich rodiče)")
        return 2
    if stara_hra == head_hra and stara_orch == head_orch:
        print("CHYBA: 'starý' sha je shodný s živým HEADem — test by neměřil nic")
        return 2

    puvodni = BRANA.read_bytes()
    puvodni_sha = hashlib.sha256(puvodni).hexdigest()

    shutil.rmtree(SCRATCH, ignore_errors=True)
    SCRATCH.mkdir(parents=True, exist_ok=True)
    try:
        print("=" * 78)
        print("P40 / H189 — čte brána dvojice z CELÉHO BLOKU HLAVIČKY?")
        print("=" * 78)
        print(f"  živé HEADy: orchestra={head_orch}  hra={head_hra}")
        print(f"  staré sha:  orchestra={stara_orch}  hra={stara_hra}")
        print(f"  scratch:    {SCRATCH}  (živé zadání se NEMUTUJE)")
        print()

        # ── 1) JEDNOŘÁDKOVÁ HLAVIČKA ────────────────────────────────────────
        print("--- 1) jednořádková hlavička (obě dvojice na řádku s klíčem) ---")
        f1 = fixtura("jednoradkova.md",
                     "# FIXTURA P40/H189 — jednořádková hlavička\n\n"
                     f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}`"
                     f" · `uo-shadows` = `{head_hra}`\n\n"
                     "Zbytek fixtury.\n")
        rc1, v1 = spust(f1)
        zkontroluj("jednořádková hlavička → exit 0", rc1 == 0, show(v1))
        zkontroluj("na řádku s klíčem jsou 2 dvojice",
                   "dvojic `<repo>` = `<sha>` na tom řádku: 2" in v1, show(v1))
        zkontroluj("v CELÉM BLOKU jsou 2 dvojice",
                   "dvojic `<repo>` = `<sha>` v CELÉM BLOKU: 2" in v1, show(v1))
        zkontroluj("OKNO HLAVIČKY je pojmenované a hlásí 1 řádek",
                   "velikost okna: řádků 1," in v1, show(v1))
        zkontroluj("obě dvojice se POROVNALY (orchestra i hra)",
                   f"OK   forge-orchestra: tvrzený {head_orch}" in v1
                   and f"OK   uo-shadows: tvrzený {head_hra}" in v1, show(v1))

        # ── 2) DVOUŘÁDKOVÁ HLAVIČKA — JÁDRO H189 ────────────────────────────
        print()
        print("--- 2) dvouřádková hlavička (2. repo na DALŠÍM řádku) -----------")
        print("       (tohle je přesně stav, na kterém brána dřív oslepla)")
        f2 = fixtura("dvouradkova.md",
                     "# FIXTURA P40/H189 — dvouřádková hlavička\n\n"
                     f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}` ·\n"
                     f"`uo-shadows` = `{head_hra}`\n\n"
                     "Zbytek fixtury.\n")
        rc2, v2 = spust(f2)
        zkontroluj("dvouřádková hlavička → exit 0", rc2 == 0, show(v2))
        zkontroluj("na řádku s klíčem je jen 1 dvojice (druhá je o řádek níž)",
                   "dvojic `<repo>` = `<sha>` na tom řádku: 1" in v2, show(v2))
        zkontroluj("v CELÉM BLOKU jsou 2 dvojice (okno je 2 řádky)",
                   "dvojic `<repo>` = `<sha>` v CELÉM BLOKU: 2" in v2
                   and "velikost okna: řádků 2," in v2, show(v2))
        zkontroluj("HRA SE SKUTEČNĚ POROVNALA (H189) — `OK uo-shadows` ve výstupu",
                   f"OK   uo-shadows: tvrzený {head_hra} = skutečný HEAD" in v2,
                   show(v2))
        zkontroluj("a nezůstalo tam „netvrdí žádný commit“",
                   "netvrdí žádný commit" not in v2, show(v2))

        # ── 3) DVOUŘÁDKOVÁ HLAVIČKA + STARÁ sha HRY ─────────────────────────
        print()
        print("--- 3) dvouřádková hlavička se STAROU sha hry → rozchod hry -----")
        f3 = fixtura("dvouradkova-stara.md",
                     "# FIXTURA P40/H189 — dvouřádková, stará sha hry\n\n"
                     f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}` ·\n"
                     f"`uo-shadows` = `{stara_hra}`\n\n"
                     "Zbytek fixtury.\n")
        rc3, v3 = spust(f3)
        zkontroluj("stará sha hry → exit 1", rc3 == 1, show(v3))
        zkontroluj("rozchod je POJMENOVANÝ u hry (ne přeskočený)",
                   "uo-shadows: zadání tvrdí" in v3, show(v3))
        zkontroluj("a není to „nepodařilo přiřadit“ (dvojice se našla)",
                   "nepodařilo přiřadit" not in v3, show(v3))

        # ── 4) BEZ KLÍČE ────────────────────────────────────────────────────
        print()
        print("--- 4) hlavička BEZ klíče → vada tvaru --------------------------")
        f4 = fixtura("bez-klice.md",
                     "# FIXTURA P40/H189 — bez klíče\n\n"
                     f"**Napsáno:** 12. 10. 2026 · `forge-orchestra` = `{head_orch}`\n\n"
                     "Zbytek fixtury.\n")
        rc4, v4 = spust(f4)
        zkontroluj("bez klíče → exit 1", rc4 == 1, show(v4))
        zkontroluj("vada je pojmenovaná (NEMÁ řádek s klíčem)",
                   "NEMÁ řádek s klíčem" in v4, show(v4))
        zkontroluj("okno je vykázané i v nule (řádků 0)",
                   "velikost okna: řádků 0," in v4, show(v4))

        # ── 5) KLÍČ BEZ DVOJIC (význam staré kontroly tvaru) ────────────────
        print()
        print("--- 5) klíč bez dvojic → TVAR: VADA (starý význam zachován) -----")
        f5 = fixtura("klic-bez-dvojic.md",
                     "# FIXTURA P40/H189 — klíč bez dvojic\n\n"
                     "**Stav obou repů při psaní:**\n\n"
                     "Zbytek fixtury.\n")
        rc5, v5 = spust(f5)
        zkontroluj("klíč bez dvojic → exit 1", rc5 == 1, show(v5))
        zkontroluj("TVAR HLAVIČKY: VADA je ve výstupu",
                   "TVAR HLAVIČKY: VADA" in v5, show(v5))
        zkontroluj("a je to pojmenované jako VADA ZÁPISU (ne neshoda commitů)",
                   "VADA ZÁPISU, NE NESHODA COMMITŮ" in v5, show(v5))

        # ── 6) TERMINÁTORY: stará sha za „Kotva pro měření“ NESMÍ přebít ────
        print()
        print("--- 6) terminátory bloku (`Kotva pro měření`, `Zkontrolováno při`)")
        for jmeno, termin in (("terminator-kotva.md", "Kotva pro měření"),
                              ("terminator-zkontrolovano.md", "Zkontrolováno při")):
            f6 = fixtura(jmeno,
                         f"# FIXTURA P40/H189 — terminátor {termin}\n\n"
                         f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}` ·\n"
                         f"`uo-shadows` = `{head_hra}`\n"
                         f"**{termin}:** `forge-orchestra` = `{stara_orch}`"
                         f" · `uo-shadows` = `{stara_hra}`\n\n"
                         "Zbytek fixtury.\n")
            rc6, v6 = spust(f6)
            zkontroluj(f"„{termin}“ UKONČIL blok → stará sha nepřebila živou (exit 0)",
                       rc6 == 0, show(v6))
            zkontroluj(f"„{termin}“: blok má 2 řádky (ne 3)",
                       "velikost okna: řádků 2," in v6, show(v6))

        # ── 7) KONFLIKT v bloku ────────────────────────────────────────────
        print()
        print("--- 7) týž repo 2× v bloku s RŮZNOU sha → konflikt --------------")
        f7 = fixtura("konflikt.md",
                     "# FIXTURA P40/H189 — konflikt v bloku\n\n"
                     f"**Stav obou repů při psaní:** `forge-orchestra` = `{head_orch}` ·\n"
                     f"`forge-orchestra` = `{stara_orch}` · `uo-shadows` = `{head_hra}`\n\n"
                     "Zbytek fixtury.\n")
        rc7, v7 = spust(f7)
        zkontroluj("konflikt (týž repo 2× s různou sha) → exit 1", rc7 == 1, show(v7))
        zkontroluj("a je POJMENOVANÝ (tichý přepis je horší než vada)",
                   "je DVAKRÁT s různou sha" in v7, show(v7))

        # ── 8) MUTACE: vrátí se vada (čtení z JEDNOHO řádku) ────────────────
        print()
        print("--- 8) MUTACE: do živé brány se vrací čtení z JEDNOHO řádku -----")
        pocet = puvodni.decode("utf-8").count(KOTVA_MUTACE)
        zkontroluj("kotva mutace je v bráně PRÁVĚ 1×", pocet == 1,
                   f"nalezeno {pocet}× — mutace by se tiše neprovedla")
        try:
            with mutuj(BRANA, KOTVA_MUTACE, VADA_MUTACE) as m:
                zkontroluj("mutace se PROPSALA (hash se změnil)",
                           m.hash_po_mutaci != m.hash_pred)
                rc8, v8 = spust(f2)
                # ⚠ TADY SE ROZHODUJE: s vrácenou vadou musí tytéž kontroly
                # (jako v případu 2) PŘESTAT PLATIT — jinak test neměří nic.
                hra_porovnana = f"OK   uo-shadows: tvrzený {head_hra}" in v8
                zkontroluj("MUTACE: hra se NEporovnala (to je vada H189)",
                           not hra_porovnana, show(v8))
                zkontroluj("MUTACE: exit NENÍ 0 (test by na případu 2 SPADL)",
                           rc8 != 0, f"exit={rc8}\n" + show(v8))
                zkontroluj("MUTACE: výstup to řekne nahlas („netvrdí žádný commit“)",
                           "netvrdí žádný commit" in v8, show(v8))
            zkontroluj("brána vrácena BAJT NA BAJT (sha256)",
                       hashlib.sha256(BRANA.read_bytes()).hexdigest() == puvodni_sha)
        except ValueError as e:
            zkontroluj(f"mutace se provedla a soubor vrátila (jinak test nic neměří)",
                       False, f"{e}")

        # ── 9) PO NÁVRATU musí brána měřit zase (test není jednorázový) ────
        print()
        print("--- 9) po vrácení mutace brána zase vidí obě dvojice ------------")
        rc9, v9 = spust(f2)
        zkontroluj("po vrácení: dvouřádková hlavička → exit 0 a hra porovnaná",
                   rc9 == 0 and f"OK   uo-shadows: tvrzený {head_hra}" in v9,
                   show(v9))
    finally:
        shutil.rmtree(SCRATCH, ignore_errors=True)
        if BRANA.read_bytes() != puvodni:
            BRANA.write_bytes(puvodni)
            print("  ⚠ brána vrácena v `finally` (mutace zůstala nedokončená)")

    # ── TVRDÉ PODMÍNKY: musí platit i když se výš něco rozbilo ─────────────
    if BRANA.read_bytes() != puvodni:
        chyb += 1
        print("  CHYBA brána NENÍ vrácena bajt na bajt!")
    if SCRATCH.exists():
        chyb += 1
        print("  CHYBA scratch po testu zůstal na disku!")
    assert hashlib.sha256(BRANA.read_bytes()).hexdigest() == puvodni_sha, \
        "BRÁNA NEVRÁCENA BAJT NA BAJT!"

    print()
    print("=" * 78)
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb   "
          f"(fixtury uklizeny, brána vrácena)")
    print("=" * 78)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

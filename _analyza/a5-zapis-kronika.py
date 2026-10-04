"""Doplní `KRONIKA-PROJEKTU.md` o tuhle session (přehledová tabulka §1 + řádek v §3).

CO SE ZÁMĚRNĚ NEDĚLÁ (a je to rozhodnutí, ne opomenutí): nemění se souhrnný
řádek `| **celkem** | … |` ani `BLOKY` v `_analyza\\kronika-kontrola.py`.
Zadání `ZADANI-A-KONEC-MERIDEL.md` §5 to zakazuje dvakrát: „NEOPRAVUJ MĚŘIDLA,
NA KTERÁ NARAZÍŠ — ani kroniku" a „NEDOPLŇUJ … seznamy v branách".

DŮSLEDEK, KTERÝ SE MUSÍ ŘÍCT NAHLAS: `kronika-kontrola.py` má **pevný seznam
bloků** (`BLOKY`), takže nový blok omylů `8n` **nebude počítat** a bude dál
hlásit „omylů celkem: 107". To je **přesně vada, kterou popisuje sám blok `8n`**
(„pevný seznam bloků znamená, že každý nový blok vypadne z počtu") — a je to
**záměrná mez téhle session**, ne přehlédnutí. Proto se sem zapisuje:
  * řádek bloku `8n` v tabulce §3 (aby byl vidět),
  * a součet zůstává **107**, takže **řádky tabulky dají víc než „celkem"** —
    nesoulad je vidět na první pohled a další session ho musí rozhodnout.

Zapisuje se `write_bytes` s LF (`KRONIKA` je LF-only, ověřeno).
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KRONIKA = Path(__file__).resolve().parent.parent / "KRONIKA-PROJEKTU.md"

# Kotva: řádek bloku `8m` v podrobné tabulce §3.
KOTVA_TABULKA = ("| **8m** | akční 2. 10. 20:1x (oprava měřidel) | **8** | **7** | **0** |")
NOVY_RADEK = KOTVA_TABULKA + "\n" + (
    '| **8n** | akční **3. 10.** (typ A: „konec měřidel", práce na hře) | **11** | **8** | **3** |')

# Kotva: poslední řádek přehledové tabulky §1 (session #21).
KOTVA_PREHLED = "| **21** | 2. 10. 2026 20:1x | **akční** |"
NOVY_PREHLED = (
    '\n| **22** | **3. 10. 2026** | **akční (typ A)** | **„Konec měřidel, práce na hře"** '
    "(`ZADANI-A-KONEC-MERIDEL.md`): stav hráče, který jiné komponenty **už volaly** "
    "(`assist.gd`, `economy.gd`), oživení mrtvé kontroly nad hráčem, srovnání roadmapy "
    's `origin/main`, měření hypotézy „bez měřidla = 0–2 omyly" | '
    "testy hry **65 → 89 kontrol, 0 selhání**; `_dukaz-assist.gd` **exit 1 → 0**; "
    "**mrtvá izometrická větev** — hráč chodil **1:1 podle obrazovky** (sklon 0) "
    "místo **2:1 po dlaždicích** (sklon **0,5**), rozhodl uživatel; roadmapa: "
    "**2 falešná `done`** opravena, **2 chybějící** doplněna, **5 `size_lines`**; "
    "**hypotéza NEPOTVRZENA: 11 omylů** (čekalo se 0–2) | **113–123** |")

# Kotva pro poznámku o neúplném součtu — hned za tabulku bloků.
KOTVA_CELKEM = "| **celkem** | **13 bloků, 21 sessions** | **107** | **90 = 84 %** | **31** |"
POZNAMKA = KOTVA_CELKEM + """

> **⚠ SOUČET NENÍ DNEŠNÍ — a je to ZÁMĚRNÉ (doplněno 3. 10. 2026).**
> Session **22** připsala blok omylů **`8n`** (**11 omylů: 113–123**) a jeho
> řádek je v tabulce výš — ale **souhrnný řádek `celkem` i `BLOKY`
> v `_analyza\\kronika-kontrola.py` zůstaly na `107` / `13 blocích`**, protože
> zadání `ZADANI-A-KONEC-MERIDEL.md` §5 to té session **zakazovalo** („NEOPRAVUJ
> MĚŘIDLA … ani kroniku" a „NEDOPLŇUJ … seznamy v branách"). **Naměřený důsledek:**
> `python _analyza\\kronika-kontrola.py` dál hlásí **„omylů celkem: 107"**, ačkoli
> součet řádků tabulky je **118**. **Součet řádků je větší než „celkem" — nesoulad
> je vidět na první pohled** a je to přesně ta vada, kterou popisuje sám blok `8n`
> („pevný seznam bloků znamená, že každý nový blok omylů vypadne z počtu").
> **Co má udělat příští session:** doplnit `("8n", "### 8n. Omyly AKČNÍ session")`
> do `BLOKY`, přepočítat souhrn a ověřit, že řádky tabulky dávají totéž co brána.
> Do té doby platí: **součet řádků je 118**; „107" je **stav před blokem `8n`**
> (ve svém čase správný)."""


def main() -> int:
    orig = KRONIKA.read_bytes()
    if b"\r\n" in orig:
        print("CHYBA: kronika ma CRLF, ocekavam LF")
        return 2
    text = orig.decode("utf-8")

    for kotva, popis in [(KOTVA_TABULKA, "radek 8m v §3"),
                         (KOTVA_PREHLED, "posledni radek §1"),
                         (KOTVA_CELKEM, "radek celkem v §3")]:
        n = text.count(kotva)
        if n != 1:
            print("CHYBA: kotva '%s' (%s) je v souboru %dx" % (kotva[:40], popis, n))
            return 2

    if "| **8n** |" in text:
        print("CHYBA: radek 8n uz v kronice je")
        return 2

    text = text.replace(KOTVA_TABULKA, NOVY_RADEK, 1)
    text = text.replace(KOTVA_PREHLED, KOTVA_PREHLED + NOVY_PREHLED, 1)
    text = text.replace(KOTVA_CELKEM, POZNAMKA, 1)

    KRONIKA.write_bytes(text.encode("utf-8"))

    zpet = KRONIKA.read_bytes()
    assert zpet != orig, "kronika se nezmenila"
    assert b"\r\n" not in zpet, "zapsaly se CRLF!"
    t2 = zpet.decode("utf-8")
    for kont in ["| **8n** |", "| **22** | **3. 10. 2026**", "113–123"]:
        assert kont in t2, "po zapisu chybi: %s" % kont
    assert t2.count("| **celkem** |") == 1, "radek celkem se rozbil"

    print("ZAPSANO do KRONIKA-PROJEKTU.md")
    print("  pred : %d radku" % len(orig.decode('utf-8').splitlines()))
    print("  po   : %d radku" % len(t2.splitlines()))
    print("  radek bloku 8n : %s" % ("JE" if "| **8n** |" in t2 else "CHYBI"))
    print("  radek session 22: %s" % ("JE" if "| **22** |" in t2 else "CHYBI"))
    print("  soucet 'celkem' ZAMERNE nedotcen (viz poznamka v dokumentu)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
r"""P31 — DOPLNĚNÍ ZÁZNAMŮ O H138 (dávka dokladů přesto přepisovala dokumenty).

PROČ ZVLÁŠŤ: `p31-zapis-zaznamu.py` už záznamy zapsal a je **idempotentní**
(druhý běh nic nemění). H138 se ale naměřil **až po něm** (tři běhy dávky
`p20-d-doklady.py`), takže se doplňuje **tímtéž způsobem** — bajtovou náhradou
s kontrolou, že kotva je v souboru právě 1× a že se nic neztratilo.

Použití: python _analyza\p31-dopln-zaznamu.py [--kontrola]
"""

import argparse
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
PLAN = WS / "PLAN-DALSI-KROK.md"

kontrol = 0
chyb = 0


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
          % (popis, ocekavano, zjisteno))
    return False


def vymen(text, stary, novy, popis):
    n = text.count(stary)
    if not check("%s: kotva je v souboru právě 1× (%d×)" % (popis, n), n, 1):
        return text
    return text.replace(stary, novy, 1)


HANDOFF_MAP_STARY = "> registr (50 bran) a shodil `ag-over-cisla.py`."
HANDOFF_MAP_NOVY = ("> registr (50 bran) a shodil `ag-over-cisla.py` ·\n"
                    "> H138 = dávka dokladů PŘESTO přepisovala dokumenty (a pojistka\n"
                    "> neříkala KOHO) — tři viníci opraveni, TŘETÍ běh dávky je zelený.")

HANDOFF_A4_STARY = ("* **A4 — H130** (dávka dokladů nepíše do dokumentů): samostatný běh\n"
                    "  `--jen A4` — viz 62.4.")
HANDOFF_A4_NOVY = ("* **A4 — H130** (dávka dokladů nepíše do dokumentů): **TŘI běhy**\n"
                   "  `--jen A4`; teprve **třetí je zelený** — „žádný z 4 sledovaných\n"
                   "  dokumentů se nezměnil“ (2149 s). První dva našly **čtyři viníky**\n"
                   "  (H138) — viz 62.4.")

HANDOFF_H138 = r"""
* **H138 — dávka dokladů PŘESTO přepisovala dokumenty (a pojistka neříkala KOHO).**
  První běh A4 našel jediný změněný soubor (`_analyza/_registr-bran.json`) —
  a **nebylo vidět, který doklad ho zapsal**. Pojistka se proto nově ptá
  **PO KAŽDÉM DOKLADU** a viníka vypíše; druhý běh pak ukázal **čtyři**:
  `ov-d-klasifikator.py` a `p20-a-kontroly.py` (harness `g3` bez
  `FORGE_BEZ_REGISTRU` → **zapsaly ŽIVÝ registr svým seznamem**; naměřeno:
  `bran_celkem: 5` a v něm `D-fixtura A…`) a `p27-oprav-datum.py` (zapsal
  `HANDOFF.md` i `KRONIKA-PROJEKTU.md` — jednorázový patcher, který P30
  do `PRESKIP` **nedala**, protože viděla jen ČISTÝ VÝSLEDEK po
  `p30-oprav-datum.py`, a ten ho hned vrátil). **Náprava:** šest nástrojů dostalo
  `FORGE_BEZ_REGISTRU=1` (`ov-d-klasifikator`, `p20-a-kontroly`, `p25-a`,
  `p26-a`, `p27-a`, `p29-a`), `p27-oprav-datum.py` je v `PRESKIP` a **živý
  registr se opravil `g3`** (49 bran). **Třetí běh dávky (2149 s): „žádný
  z 4 sledovaných dokumentů se nezměnil“** — teprve tím je **H130 doložené**
  (H136); bez toho by se „opraveno“ četlo z čistého výsledku, který vyráběl
  jiný nástroj.

"""

KRONIKA_H138 = r"""| **H138** | **DÁVKA DOKLADŮ PŘESTO PŘEPISOVALA DOKUMENTY — A POJISTKA NEŘEKLA KOHO.** Druhá polovina H130: běh `p20-d-doklady.py` zapsal **`HANDOFF.md` i `KRONIKA-PROJEKTU.md`** (netto to vidět nebylo — `p30-oprav-datum.py` je hned vrátil z `HEAD`) a **`_analyza/_registr-bran.json`**; pojistka hlásila jen „ZMĚNĚN“, ne **který skript**. Náprava: (1) pojistka se ptá **PO KAŽDÉM DOKLADU** a viníka VYPÍŠE — naměřeno: `ov-d-klasifikator.py` a `p20-a-kontroly.py` zapisovaly registr svým harnessem `g3` (bez `FORGE_BEZ_REGISTRU`) a `p27-oprav-datum.py` psal dokumenty, které `p30-oprav-datum.py` vracel; (2) **šest nástrojů** dostalo `FORGE_BEZ_REGISTRU=1` a `p27-oprav-datum.py` je v `PRESKIP`; (3) **živý registr byl KONTAMINOVANÝ** (`bran_celkem: 5`, „D-fixtura A…“) → náprava = pustit `g3` (49 bran). **Třetí běh dávky: „žádný z 4 sledovaných dokumentů se nezměnil“** (2149 s) — teprve tím je H130 doložené. | `_analyza/p31-a4-davka-vystup.txt` (tři běhy: viníci + zelený výsledek), `_analyza/p31-a4-druhy-vystup.txt`, `_analyza/p31-a4-treti-vystup.txt`, `_analyza/p20-d-doklady.py` (pojistka po každém dokladu), `_analyza/p31-g3-oprava2-vystup.txt` |
"""

RADEK_STARY = "**PLÁN:** dodatek P31 | **—**"
RADEK_NOVY = (
    "**H138** dávka dokladů PŘESTO přepisovala dokumenty a pojistka neříkala "
    "KOHO — nová pojistka se ptá PO KAŽDÉM DOKLADU a viníka VYPÍŠE; našla "
    "`ov-d-klasifikator.py` + `p20-a-kontroly.py` (harness `g3` bez "
    "`FORGE_BEZ_REGISTRU` → živý registr s fixturou, `bran_celkem: 5`) a "
    "`p27-oprav-datum.py` (psal dokumenty; `p30-oprav-datum.py` je hned vracel) "
    "→ šest nástrojů má guard, `p27-oprav-datum.py` je v `PRESKIP`, registr "
    "opraven `g3` (49 bran) a **TŘETÍ běh dávky je zelený** (2149 s). "
    "**PLÁN:** dodatek P31 | **—**")

PLAN_STARY = ("**P30 je přeměřená** (`p31-a-overeni.py` → 54/1/2 ROZDÍLY, 0 NEZMĚŘENO);\n"
              "jediná neshoda je `p30-a` **35/0 → 32/3** (H135: dvě příčiny z opravy C2,\n"
              "jedna dobová kontrola nasazení na živém HEAD).")
PLAN_NOVY = ("**P30 je přeměřená** (`p31-a-overeni.py` → 54/1/2 ROZDÍLY, 0 NEZMĚŘENO);\n"
             "jediná neshoda je `p30-a` **35/0 → 32/3** (H135: dvě příčiny z opravy C2,\n"
             "jedna dobová kontrola nasazení na živém HEAD). **H130 je doložené až\n"
             "TŘETÍM během dávky** (H138: pojistka nově jmenuje viníka; šest nástrojů\n"
             "dostalo `FORGE_BEZ_REGISTRU`, `p27-oprav-datum.py` je v `PRESKIP`) —\n"
             "a teprve pak platí „žádný z 4 sledovaných dokumentů se nezměnil“.")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true")
    args = ap.parse_args()

    h = HANDOFF.read_text(encoding="utf-8")
    k = KRONIKA.read_text(encoding="utf-8")
    p = PLAN.read_text(encoding="utf-8")

    uz = "H138" in k and "H138" in h
    if uz:
        print("  OK    H138 UŽ JE zapsaný (HANDOFF §62 i KRONIKA §2.24) — idempotentní běh")
        print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
        return 0 if chyb == 0 else 1

    check("HANDOFF §62 existuje", "## 62. P31" in h, True)
    check("KRONIKA řádek 46 existuje", bool(re.search(r"^\|\s*\*\*46\*\*\s*\|", k, re.M)), True)
    check("KRONIKA má řádek H137 (kotva pro H138)",
          bool(re.search(r"^\|\s*\*\*H137\*\*\s*\|", k, re.M)), True)
    check("H138 ještě není v kronice", "H138" in k, False)

    h_new = vymen(h, HANDOFF_MAP_STARY, HANDOFF_MAP_NOVY, "HANDOFF: mapovací seznam")
    h_new = vymen(h_new, HANDOFF_A4_STARY, HANDOFF_A4_NOVY, "HANDOFF: odstavec A4")
    h_new = vymen(h_new, "\n### 62.5 Živý stav při zápisu",
                  HANDOFF_H138 + "### 62.5 Živý stav při zápisu",
                  "HANDOFF: vložení H138 před 62.5")
    k_new = vymen(k, "\n## 3. Počty omylů", "\n" + KRONIKA_H138 + "\n## 3. Počty omylů",
                  "KRONIKA: vložení H138 před §3")
    k_new = vymen(k_new, RADEK_STARY, RADEK_NOVY, "KRONIKA: doplnění řádku 46")
    p_new = vymen(p, PLAN_STARY, PLAN_NOVY, "PLAN: doplnění dodatku P31")

    check("HANDOFF: H138 je v mapovacím seznamu", "H138 = dávka dokladů" in h_new, True)
    check("HANDOFF: H138 odstavec je vložen", "**H138 — dávka dokladů" in h_new, True)
    check("HANDOFF: A4 už netvrdí „samostatný běh“", "samostatný běh" in h_new, False)
    check("HANDOFF: řádků neubylo", len(h_new.splitlines()) >= len(h.splitlines()), True)
    check("HANDOFF: NEPŘIBYL tabulkový řádek `| **Hxx** |`",
          len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h_new, re.M)),
          len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h, re.M)))
    check("KRONIKA: H138 řádek je vložen",
          bool(re.search(r"^\|\s*\*\*H138\*\*\s*\|", k_new, re.M)), True)
    check("KRONIKA: řádek 46 zmínil H138", "H138" in RADEK_NOVY, True)
    check("KRONIKA: id 1..46 bez děr",
          [n for n in range(1, 47)
           if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k_new, re.M)], [])
    check("PLAN: doplněn o H130/H138", "H138" in p_new, True)
    check("nic neubylo (všechny tři soubory narostly)",
          len(h_new) > len(h) and len(k_new) > len(k) and len(p_new) > len(p), True)

    if args.kontrola:
        print("KONTROLA OK — nic se nezapsalo (--kontrola)")
        return 0 if chyb == 0 else 1
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb)" % chyb)
        return 1

    HANDOFF.write_bytes(h_new.encode("utf-8"))
    KRONIKA.write_bytes(k_new.encode("utf-8"))
    PLAN.write_bytes(p_new.encode("utf-8"))
    print("  zapsáno: H138 do HANDOFF §62, KRONIKY §2.24 a řádku 46 + PLAN")
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

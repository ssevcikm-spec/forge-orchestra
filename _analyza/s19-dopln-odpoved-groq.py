# -*- coding: utf-8 -*-
r"""Doplní §18.17 a opraví TŘI místa v `HANDOFF.md`, kde je číslo podáno jako
„14 398" (jedno), ačkoli log má tři různá.

CO SE OPRAVUJE:
  1. §18.7 nad tabulkou: „Groq free TPM = 8 000 (… Requested 14398, 9×)"
     → doplnit, že `Requested` má **tři různá** čísla (14 398 / 14 377 / 14 402)
     a že jde o **`Request too large`** (limit na REQUEST), ne o minutovou kvótu.
  2. §18.7 tabulka: řádek „Groq free TPM = 8 000" — doplnit totéž.
  3. §18.8 tabulka: řádek `TPM: Limit 8000, Requested 14398` označit jako
     **zpřesněný** (tři čísla), ne jen „OK".

Použití:  python _analyza\s19-dopln-odpoved-groq.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

NOVE = (WS / "_analyza" / "s19-oddil-groq.md").read_text(encoding="utf-8").strip()
assert NOVE.startswith("### 18.17"), "oddíl nemá správný nadpis"

text = HANDOFF.read_text(encoding="utf-8")

# ── 1) vložit §18.17 PŘED §18.16 (kotva se hledá v PŮVODNÍM textu) ──────────
KOTVA = "### 18.16 Vlastní omyl"
assert text.count(KOTVA) == 1, "kotva §18.16 není právě 1×"
assert "### 18.17" not in text, "§18.17 už v souboru je"
i = text.find(KOTVA)
novy = text[:i] + NOVE + "\n\n" + text[i:]
assert novy.count("### 18.17") == 1 and novy.count(KOTVA) == 1
assert novy.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"
print("  1) §18.17 vložen před §18.16")

# ── 2) OPRAVY ČÍSEL ────────────────────────────────────────────────────────
# Každá dvojice = (co je v souboru, čím nahradit). Kotvy jsou krátké a ASCII,
# aby se do skriptu nemusely psát české uvozovky (ty tuhle session rozbily 5×).
OPRAVY = [
    # (a) §18.7 — VĚTA O GROQU V SOUBORU VŮBEC NENÍ (naměřeno 2. 10. 2026 při
    # téhle opravě: `grep 'Groq free TPM'` → 0 výskytů). Spadla při dřívějším
    # vkládání oddílů. Doplňuje se proto CELÁ — a rovnou ve správném znění:
    # `Requested` má **tři různá** čísla a jde o `Request too large` na JEDEN
    # request, ne o minutovou kvótu.
    ("**Srovnání s limity poskytovatelů:**",
     "**Naměřeno v logu #146 (je to `Request too large` — limit na JEDEN request,\n"
     "ne minutová kvóta; `Requested` má tři různá čísla: 14 398, 14 377, 14 402,\n"
     "tedy request je ~14,4 tisíce tokenů — viz §18.17):** `Limit 8000`, **9×**.\n\n"
     "**Srovnání s limity poskytovatelů:**"),
    # (b) §18.7 tabulka poskytovatelů
    ("| **groq** | **TPM 8 000** | **NAMĚŘENO** v logu #146 | **NE** |",
     "| **groq** | **TPM 8 000** | **NAMĚŘENO** v logu #146 (9×) | **NE** — "
     "request má **~14 400** tokenů (§18.17) |"),
    # (c) §18.8 tabulka tvrzení
    ("| „`TPM: Limit 8000, Requested 14398`\" | **`Limit 8000, Requested 14398`** (v logu 9×) | **OK** |",
     "| „`TPM: Limit 8000, Requested 14398`\" | **`Limit 8000`** 9×; `Requested` "
     "**14 398** (4×), **14 377** (2×), **14 402** (2×) | **zpřesněno** — jedno "
     "číslo bylo nepřesné, viz **§18.17** |"),
]

for stary, novy_t in OPRAVY:
    pocet = novy.count(stary)
    print("  %-46s %dx" % (repr(stary)[:46], pocet))
    if pocet == 1:
        novy = novy.replace(stary, novy_t, 1)
        print("       → OPRAVENO")
    elif pocet == 0:
        print("       → už opraveno (kotva tam není) — přeskakuji")
    else:
        print("       → CHYBA: kotva je %dx, neopravuji" % pocet)
        sys.exit(1)

assert novy != text, "ŽÁDNÁ OPRAVA NEPROBĚHLA"
assert novy.count("### 18.17") == 1, "§18.17 není právě 1×"

if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

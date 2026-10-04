# -*- coding: utf-8 -*-
r"""Vloží omyl **68** do tabulky §8g a **§18.16** před nadpis §18 v `HANDOFF.md`.

PROČ SKRIPTEM A S TEXTEM V SOUBORECH: `HANDOFF.md` má 2 800+ řádků a „nic se
nesmí ztratit". Vkládaný text se proto drží v `_analyza\s18c-*.md`
(**bajt na bajt**) a skript jen dělá **dvě cílené náhrady**, každou **ověří**.

⚠ PROČ NE APPEND: oddíl 8g ani §18 nejsou na konci souboru (append přidal
§18.16 za ně) — a **přesně na tomhle spadl předchozí pokus** (omyl 68:
dvojité vložení appendem). Skript proto kontroluje, že každá kotva je
v souboru **právě jednou**, a teprve pak zapisuje.

Použití:  python _analyza\s18c-dopln-omyl68.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

text = HANDOFF.read_text(encoding="utf-8")
radek68 = (WS / "_analyza" / "s18c-omyl68-radek.md").read_text(encoding="utf-8").strip()
oddil1816 = (WS / "_analyza" / "s18c-doplneni.md").read_text(encoding="utf-8").strip()

# Krátké ASCII kotvy (žádné české uvozovky — ty rozbily předchozí verzi skriptu).
# ⚠ Kotva na konec tabulky §8g je **poslední řádek TABULKY**, ne souhrn pod ní:
# naměřeno při psaní — první verze hledala „pět z šesti vzniklo v měřidle",
# což je text z DŘÍVĚJŠÍ verze oddílu (po doplnění omylu 67 se změnil na
# „šest ze sedmi"), takže kotva našla **0** a skript správně skončil `exit 2`.
# Hledá se proto na řádku omylu 67, který je v tabulce poslední.
KOTVA_TABULKY = "| **67** |"
KOTVA_18 = "## 18. Ověření práce AKČNÍ session"
KOTVA_1816 = "### 18.16 Vlastní omyl"

print("=" * 78)
print("DOPLNĚNÍ HANDOFF.md — omyl 68 a §18.16 (cílené vložení, ne append)")
print("=" * 78)

for popis, kotva, ocekavano in (("poslední řádek tabulky §8g (omyl 67)", KOTVA_TABULKY, 1),
                                ("nadpis §18", KOTVA_18, 1),
                                ("§18.16 (nesmí tam být)", KOTVA_1816, 0)):
    pocet = text.count(kotva)
    stav = "OK  " if pocet == ocekavano else "CHYBA"
    print("  %s %-24s %dx (očekáváno %d)" % (stav, popis, pocet, ocekavano))
    if pocet != ocekavano:
        print("  → končím, soubor nevypadá jako po prvním vložení")
        sys.exit(2)

# 1) omyl 68 na konec TABULKY §8g (tabulka končí řádkem s „pět z šesti…")
i = text.find(KOTVA_TABULKY)
konec_radku = text.find("\n", i)
assert konec_radku > i, "řádek se souhrnem 8g nemá konec"
novy = text[:konec_radku + 1] + radek68 + "\n" + text[konec_radku + 1:]
assert novy != text, "VLOŽENÍ OMYLU 68 NEPROBĚHLO"

# 2) §18.16 hned před nadpis §18
j = novy.find(KOTVA_18)
assert j > 0, "po vložení omylu 68 se §18 nenašel"
novy2 = novy[:j] + oddil1816 + "\n\n" + novy[j:]
assert novy2.count(KOTVA_18) == 1, "kotva §18 není právě 1×"
assert novy2.count("| **68** |") == 1, "omyl 68 není právě 1×"
assert novy2.count(KOTVA_1816) == 1, "§18.16 není právě 1×"
assert novy2.count("| **67** |") == 1, "omyl 67 se ztratil nebo zdvojil"
assert novy2.startswith(text[:4096]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"

print()
print("  omyl 68:  na konec tabulky §8g")
print("  §18.16:   před nadpis §18")

if ZAPIS:
    HANDOFF.write_bytes(novy2.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B" % (len(text.encode("utf-8")), len(novy2.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

# -*- coding: utf-8 -*-
r"""Nastaví souhrn bloku **8g** v `HANDOFF.md` na SPRÁVNÉ hodnoty.

⚠ CO BYLO ŠPATNĚ (vlastní omyl, naměřeno 2. 10. 2026): předchozí verze počítala
„v měřidle" jako `pocet_radku - 1`. To je **vzorec, ne měření** — a vyšlo
**9 z 11**, což je samo o sobě nesmysl (blok má **10** řádků). Správně je
**8 z 10**: měřidlo je vevenile **61, 62, 63, 64, 65, 67, 69, 70** (osm),
kdežto **66** (špatný interpret) a **68** (append bez pojistky) jsou omyl
**postupu**, ne měřidla.

**Pravidlo, které z toho plyne:** souhrn se **NESMÍ odvozovat vzorcem** z počtu
řádků. Buď je **přečtený ze souhrnu, který napsala session** (to dělá
`s18-prepocitej-omyly.py`), nebo se **nepíše vůbec** (`—` = nezměřeno).

Použití:  python _analyza\s19i-souhrn-oprava.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

text = HANDOFF.read_text(encoding="utf-8")

# (co je v souboru, čím nahradit) — jen V BLOKU 8g, ne v celém dokumentu.
ZMENY = [
    ("**Vzor z těch jedenácti:**", "**Vzor z těch deseti:**"),
    ("**devíti z jedenácti** vzniklo v **měřidle**",
     "**osmi z deseti** vzniklo v **měřidle**"),
]

i8g = text.find("### 8g. Omyly PLÁNOVACÍ")
i18 = text.find("## 18. Ověření práce AKČNÍ session", i8g)
assert i8g > 0 and i18 > i8g, "blok 8g nejde vymezit"
blok = text[i8g:i18]

print("=" * 78)
print("OPRAVA SOUHRNU 8g -- 9 z 11 bylo spatne, spravne 8 z 10")
print("=" * 78)
novy_blok = blok
for stary, novy in ZMENY:
    pocet = novy_blok.count(stary)
    print("  %-46s %dx" % (repr(stary)[:46], pocet))
    if pocet == 1:
        novy_blok = novy_blok.replace(stary, novy, 1)
    elif pocet == 0:
        print("     → už opraveno")
    else:
        print("     → CHYBA: kotva je %dx" % pocet)
        sys.exit(1)

assert novy_blok != blok, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
# POJISTKY: staré (nesmyslné) znění tam nesmí být, nové ano.
assert "jedenácti" not in novy_blok, "v bloku 8g zůstalo 'jedenácti'"
assert "osmi z deseti** vzniklo v **měřidle**" in novy_blok
assert "Vzor z těch deseti" in novy_blok

novy = text[:i8g] + novy_blok + text[i18:]
if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

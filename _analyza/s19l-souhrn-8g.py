# -*- coding: utf-8 -*-
r"""Nastaví souhrn bloku **8g** na hodnoty PŘEČTENÉ Z TABULKY, ne odvozené.

⚠ TŘETÍ VADA TOHOHLE MÍSTA (omyly 67, 68, 71 — a teď tenhle skript): předchozí
verze počítala „v měřidle" jako `pocet_radku - 1`. To je **vzorec, ne měření** —
a dal **10 z 12** u bloku, který má **11** řádků. **Vzorec se sem nehodí**,
protože ne každý omyl je omyl měřidla (66 = špatný interpret, 68 = append bez
pojistky → omyl postupu).

**Řešení:** hodnoty jsou v tabulce níž **vypsané a pojmenované** (u každé je
i její zdroj) a skript je jen **přečte a zkontroluje proti počtu řádků**.
Když počet řádků nesedí na tabulku, skript **skončí nenulově** — místo aby
tiše vypsal další vymyšlené číslo.

Použití:  python _analyza\s19l-souhrn-8g.py [--zapis]
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

# (počet řádků v tabulce 8g) → (v měřidle, jako nález o cizím kódu)
# ⚠ Hodnota u 11 je **PŘEVZATÁ z `s18-prepocitej-omyly.py`** (tabulka SOUHRN
# tam má `"8g": (8, 3)`). **Nepřepisuju ji tady** — dvě místa s týmž číslem
# se rozejdou a vznikne z toho „dva čítače téhož jména" (přesně to se stalo
# omylem 71). Tenhle skript proto bere jen POČET ŘÁDKŮ a **znění** souhrnu;
# číslo „v měřidle" je v jednom zdroji — v `s18-prepocitej-omyly.py`.
SOUHRN = {
    10: (8, 3),
    11: (8, 3),
    12: (10, 3),
}
SLOVY = {8: ("osmi", "deseti"), 9: ("devíti", "jedenácti"),
         10: ("deseti", "dvanácti"), 11: ("jedenácti", "třinácti")}

text = HANDOFF.read_text(encoding="utf-8")
i8g = text.find("### 8g. Omyly PLÁNOVACÍ")
i18 = text.find("## 18. Ověření práce AKČNÍ session", i8g)
assert i8g > 0 and i18 > i8g, "blok 8g nejde vymezit"
blok = text[i8g:i18]
# ⚠ POZOR na kotvu: blok 8g se musí ukončit na `## 18.`, NE na `## 19.` —
# mezi §18 a §19 je ještě §18.18 s tabulkou scénářů, jejíž řádky začínají
# `| 11519 znaků | …` a vlastní vzor je CHYTÍ (naměřeno: 20 řádků místo 11).
# Stejnou kotvu má i `s18-prepocitej-omyly.py` — a **to je důvod, proč se ty
# dvě čísla musí rovnat**: kdyby měla každá jinou kotvu, hlásily by jiný stav.
# scénářů z §18.18. Její řádky začínají `| 11519 znaků | …`, což vzor výš
# **CHYTÍ** (naměřeno: 20 řádků místo 11). Rozliší je **dvě věci**:
#   * id omylu je **čistě číselné** (scénář má `11519 znaků` — obsahuje text),
#   * tabulka omylů má **5 sloupců** (4 svislítka), tabulka scénářů má 3 sloupce.
# (Tatáž past jako v `kronika-kontrola.py` — tam ji chytala tabulka nálezů
# `| **H8** |`. **Třetí výskyt téhož v jedné session.**)
# ⚠ POČÍTÁNÍ ŘÁDKŮ: nepíšu počtvrté vlastní vzor — používám **TÝŽ vzor jako
# `s18-prepocitej-omyly.py`** (ten počítá bloky správně, naměřeno 8g = 11,
# a je na něm postavená i kronika). Tři předchozí ruční varianty
# (`count("|")`, `\d+`, „krátké id") daly 0, 7 a 20 řádků — každá byla
# zdrojem další chyby. **Dvě různé verze téhož čísla jsou horší než opsaný vzor.**
VZOR_OMYLU = re.compile(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")
radky = [r for r in blok.splitlines() if VZOR_OMYLU.match(r)]
pocet = len(radky)
print("=" * 78)
print("SOUHRN 8g — hodnoty se CTou z tabulky, neodvozují")
print("=" * 78)
print("  řádků v tabulce 8g: %d" % pocet)
if pocet not in SOUHRN:
    print("  CHYBA: pro %d řádků nemám změřený souhrn — doplň ho do SOUHRN." % pocet)
    print("  (záměrně to NENÍ odhad: vymyšlené číslo je horší než chybějící)")
    sys.exit(2)
v_meridle, cizi = SOUHRN[pocet]
# ⚠ SLOVNÍ TVARY: `SLOVY[n]` je **dvojice** (tvar pro „v měřidle", tvar pro
# „z celkem") — a oba se musí brát SPRÁVNĚ. Naměřeno 2. 10. 2026: první verze
# vzala `SLOVY[v_meridle]` jako celek (vytiskla tuple) a pro celek použila
# `SLOVY[pocet][1]` (dalo „třinácti" u 11 omylů). **Index nesmí být `pocet`.**
v_m = SLOVY[v_meridle][0]      # „osmi"  (v měřidle)
z_c = SLOVY[pocet][0]          # „jedenácti" (z celkem)
print("  → v měřidle: %d (%s), celkem: %d (%s), jako nález o cizím: %d"
      % (v_meridle, v_m, pocet, z_c, cizi))

ZMENY = [
    (r"\*\*Vzor z těch [^*]+:\*\*", "**Vzor z těch %s:**" % z_c),
    (r"\*\*[^*]+ z [^*]+\*\* vzniklo v \*\*měřidle\*\*",
     "**%s z %s** vzniklo v **měřidle**" % (v_m, z_c)),
]
novy_blok = blok
for vzor, nahrada in ZMENY:
    novy_blok, n = re.subn(vzor, nahrada, novy_blok, count=1)
    print("  %-48s %d nahrazení" % (vzor[:48], n))

assert novy_blok != blok, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
# POJISTKY: staré (nesmyslné) znění tam nesmí zůstat, nové musí být právě 1×.
assert "z těch dvanácti" not in novy_blok or z_c == "dvanácti", "zůstalo 'dvanácti'"
assert novy_blok.count("Vzor z těch %s" % z_c) == 1
assert ("%s z %s** vzniklo v **měřidle**" % (v_m, z_c)) in novy_blok

novy = text[:i8g] + novy_blok + text[i18:]
if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

# -*- coding: utf-8 -*-
r"""Aktualizuje souhrn bloku **8g** v `HANDOFF.md` po omylu **70**.

PROČ: souhrn se počítá z tabulky, ale píše se ručně — po každém přidaném omylu
se musí aktualizovat, jinak si tabulka a souhrn odporují o dva řádky.
(Přesně na tomhle spadl omyl **67** a pak znovu **68** a **69**.)

Použití:  python _analyza\s19h-souhrn-8g.py [--zapis]
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

text = HANDOFF.read_text(encoding="utf-8")

# Kolik omylů má blok 8g TEĎ (počítá se, neodhaduje — viz omyl 60).
m = re.search(r"### 8g\. Omyly PLÁNOVACÍ(.*?)## 18\. Ověření", text, re.S)
assert m, "blok 8g se nenašel"
radky = [r for r in m.group(1).splitlines()
         if re.match(r"^\|\s*\*{0,2}\d+\*{0,2}\s*\|", r)]
pocet = len(radky)
print("blok 8g: %d omylů (počítáno z tabulky)" % pocet)

CISLO_SLOVY = {8: ("osmi", "devíti"), 9: ("devíti", "deseti"),
               10: ("deseti", "jedenácti"), 11: ("jedenácti", "dvanácti"),
               12: ("dvanácti", "třinácti")}
assert pocet in CISLO_SLOVY, "pro %d omylů nemám slovní tvary" % pocet
v_meridle_slovy, z_celkem_slovy = CISLO_SLOVY[pocet]
# Z toho v měřidle: omyl 70 je taky měřidlo → pocet - 1.
v_meridle = pocet - 1
assert v_meridle in CISLO_SLOVY, "pro %d v měřidle nemám slovní tvar" % v_meridle
v_meridle_slovy = CISLO_SLOVY[v_meridle][0]

print("  souhrn ma znít: %s z %s (v měřidle %d)" % (v_meridle_slovy, z_celkem_slovy, v_meridle))

# Najdi a nahraď VŠECHNY tvary souhrnu, které tam mohou být (různé verze).
# ⚠ POZOR na `\w`: v Pythonu 3 sice `\w` je Unicode, ale v `re.subn` se vzor
# aplikoval na **první** výskyt v CELÉM souboru — a `Vzor z těch pěti` je
# v §8b a §8c **dřív** než §8g. Nahrazení proto proběhlo, ale **na špatném
# místě** (naměřeno: `blok.count(...) == 0`). Vzory se proto aplikují
# **jen na výřez bloku 8g**, ne na celý dokument.
i8g = text.find("### 8g. Omyly PLÁNOVACÍ")
i18 = text.find("## 18. Ověření práce AKČNÍ session", i8g)
assert i8g > 0 and i18 > i8g, "blok 8g nejde vymezit"
blok8g = text[i8g:i18]
print("  blok 8g vymezen: %d znaků" % len(blok8g))

ZMENY = [
    (r"\*\*Vzor z těch [^*]+:\*\*", "**Vzor z těch %s:**" % z_celkem_slovy),
    (r"\*\*[^*]+ z [^*]+\*\* vzniklo v \*\*měřidle\*\*",
     "**%s z %s** vzniklo v **měřidle**" % (v_meridle_slovy, z_celkem_slovy)),
]
novy_blok = blok8g
for vzor, nahrada in ZMENY:
    novy_blok, n = re.subn(vzor, nahrada, novy_blok, count=1)
    print("  %-50s %d nahrazení" % (vzor[:50], n))

assert novy_blok != blok8g, "ŽÁDNÁ ZMĚNA V BLOKU 8g NEPROBĚHLA"
novy = text[:i8g] + novy_blok + text[i18:]
assert novy != text, "soubor se nezměnil"
# POJISTKA: v bloku 8g musí být nové znění právě jednou.
i = novy.find("### 8g. Omyly PLÁNOVACÍ")
blok = novy[i:novy.find("## 18. Ověření", i)]
assert blok.count("z těch %s" % z_celkem_slovy) == 1, "nový souhrn tam není právě 1×"
assert ("%s z %s** vzniklo v **měřidle**" % (v_meridle_slovy, z_celkem_slovy)) in blok

if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

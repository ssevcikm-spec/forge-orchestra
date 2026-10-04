# -*- coding: utf-8 -*-
r"""Doplní do `HANDOFF.md` omyl 69 do souhrnu §8g a přepočítá kroniku §3.

PROČ: omyl **69** se přidal do tabulky §8g **až po** tom, co se napsal souhrn
(„sedm z osmi"). Nechat to být znamená, že si tabulka a souhrn odporují o dva
řádky — a to je přesně to, co tahle session řeší pořád dokola.

Použití:  python _analyza\s19b-dopln-souhrn.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

text = HANDOFF.read_text(encoding="utf-8")

ZMENY = [
    ("Vzor z těch osmi", "Vzor z těch devíti"),
    ("sedm z osmi** vzniklo v **měřidle**", "osm z devíti** vzniklo v **měřidle**"),
    # věta o tom, co zachránilo které omyly — doplnit 69 (last-modified)
    ("u **67** **mutační test**, který ukázal, že brána po",
     "u **67** **mutační test** a u **69** **`last-modified` z GitHub Pages** "
     "(ne můj čekací skript). Ten ukázal, že brána po"),
]

print("=" * 78)
print("DOPLNĚNÍ SOUHRNU §8g — po omylu 69")
print("=" * 78)
for stary, novy in ZMENY:
    print("  %-46s %dx" % (repr(stary)[:46], text.count(stary)))

novy_text = text
for stary, novy in ZMENY:
    if novy_text.count(stary) == 1:
        novy_text = novy_text.replace(stary, novy, 1)
        print("     → OPRAVENO: %s" % repr(stary)[:40])
    elif novy_text.count(stary) == 0:
        print("     → už opraveno / kotva tam není")
    else:
        print("     → CHYBA: kotva je %dx" % novy_text.count(stary))
        sys.exit(1)

assert novy_text != text, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
assert "sedm z osmi" not in novy_text, "PODMÍNKA POŘÁD PLATÍ (sedm z osmi tam je)"
assert "osm z devíti" in novy_text, "nové znění se nevepsalo"

if ZAPIS:
    HANDOFF.write_bytes(novy_text.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy_text.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

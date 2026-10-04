# -*- coding: utf-8 -*-
r"""Zapíše do `HANDOFF.md` §19.2 (vada měřidla `f3-over-deploy.mjs`) a omyl **70**.

Postup je stejný jako u §19.1: texty jsou v `_analyza\s19g-*.md` (bajt na bajt),
omyl se vkládá na konec tabulky §8g, oddíl na konec souboru. Každá kotva se
ověří PŘED zápisem — to je poučení z omylu 68 (dvojité vložení).

Použití:  python _analyza\s19g-zapis.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

ODDIL = (WS / "_analyza" / "s19g-oddil-deploy.md").read_text(encoding="utf-8").strip()
OMYL = (WS / "_analyza" / "s19g-omyl70-radek.md").read_text(encoding="utf-8").strip()
assert ODDIL.startswith("### 19.2"), "oddíl nemá správný nadpis"
assert OMYL.startswith("| **70** |"), "omyl 70 nemá správný tvar"
assert OMYL.count("\n") == 0, "omyl 70 musí být JEDEN řádek tabulky"

text = HANDOFF.read_text(encoding="utf-8")

# ── 1) omyl 70 za omyl 69 ──────────────────────────────────────────────────
KOTVA69 = "| **69** |"
assert text.count(KOTVA69) == 1, "kotva omylu 69 není právě 1×"
i = text.find(KOTVA69)
konec = text.find("\n", i)
assert konec > i, "řádek omylu 69 nemá konec"
novy = text[:konec + 1] + OMYL + "\n" + text[konec + 1:]
assert novy.count("| **70** |") == 1, "omyl 70 není právě 1×"
assert novy.count(KOTVA69) == 1, "omyl 69 se ztratil nebo zdvojil"
print("  1) omyl 70 vložen za omyl 69")

# ── 2) §19.2 na konec souboru ──────────────────────────────────────────────
assert "### 19.2" not in novy, "§19.2 už v souboru je"
novy2 = novy.rstrip("\n") + "\n\n" + ODDIL + "\n"
assert novy2.count("### 19.2") == 1 and novy2.count("### 19.1") == 1
assert novy2.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"
print("  2) §19.2 vložen na konec souboru")

print()
print("  PŘED: %d B" % len(text.encode("utf-8")))
print("  PO:   %d B" % len(novy2.encode("utf-8")))

if ZAPIS:
    HANDOFF.write_bytes(novy2.encode("utf-8"))
    print("  ZAPSÁNO.")
else:
    print("  (dry-run — spusť s --zapis)")

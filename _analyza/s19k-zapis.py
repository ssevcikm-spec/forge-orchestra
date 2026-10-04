# -*- coding: utf-8 -*-
r"""Zapíše do `HANDOFF.md` §18.18 (menší granule / sekvenčně) a omyl **71**.

Postup jako u §19: texty jsou v `_analyza\s19k-*.md` (bajt na bajt), omyl se
vkládá na konec tabulky §8g, oddíl **před** `## 19.` (patří do §18). Každá
kotva se ověří PŘED zápisem — poučení z omylu 68.

Použití:  python _analyza\s19k-zapis.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

ODDIL = (WS / "_analyza" / "s19k-oddil-granule.md").read_text(encoding="utf-8").strip()
OMYL = (WS / "_analyza" / "s19k-omyl71-radek.md").read_text(encoding="utf-8").strip()
assert ODDIL.startswith("### 18.18"), "oddíl nemá správný nadpis"
assert OMYL.startswith("| **71** |"), "omyl 71 nemá správný tvar"
assert OMYL.count("\n") == 0, "omyl 71 musí být JEDEN řádek tabulky"

text = HANDOFF.read_text(encoding="utf-8")

# ── 1) omyl 71 za omyl 70 ──────────────────────────────────────────────────
KOTVA = "| **70** |"
assert text.count(KOTVA) == 1, "kotva omylu 70 není právě 1×"
i = text.find(KOTVA)
konec = text.find("\n", i)
assert konec > i, "řádek omylu 70 nemá konec"
novy = text[:konec + 1] + OMYL + "\n" + text[konec + 1:]
assert novy.count("| **71** |") == 1 and novy.count(KOTVA) == 1
print("  1) omyl 71 vložen za omyl 70")

# ── 2) §18.18 PŘED „## 19." (patří do §18, ne na konec) ────────────────────
K19 = "## 19. Provedeno 2. 10. 2026 (13:16 UTC) — PUSH obou repů"
assert novy.count(K19) == 1, "kotva §19 není právě 1×"
assert "### 18.18" not in novy, "§18.18 už v souboru je"
j = novy.find(K19)
novy2 = novy[:j] + ODDIL + "\n\n" + novy[j:]
assert novy2.count("### 18.18") == 1, "§18.18 není právě 1×"
assert novy2.count("### 18.17") == 1, "§18.17 se ztratil"
assert novy2.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"
print("  2) §18.18 vložen před §19 (do §18)")
print()
print("  PŘED: %d B" % len(text.encode("utf-8")))
print("  PO:   %d B" % len(novy2.encode("utf-8")))

if ZAPIS:
    HANDOFF.write_bytes(novy2.encode("utf-8"))
    print("  ZAPSÁNO.")
else:
    print("  (dry-run — spusť s --zapis)")

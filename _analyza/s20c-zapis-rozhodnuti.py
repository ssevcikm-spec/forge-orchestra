# -*- coding: utf-8 -*-
r"""Zapíše rozhodnutí o Groqu: `HANDOFF.md` §20 a `KRONIKA-PROJEKTU.md` NA16.

Texty jsou v `_analyza\s20-*.md` (bajt na bajt) — české uvozovky v Python
literálech rozbily v téhle session **osm** skriptů (past `dsh-prostredi` §3d).
Každá kotva se ověří PŘED zápisem (poučení z omylu 68 — dvojité vložení).

Použití:  python _analyza\s20c-zapis-rozhodnuti.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ZAPIS = "--zapis" in sys.argv

ODDIL = (WS / "_analyza" / "s20-oddil-odlozeno.md").read_text(encoding="utf-8").strip()
NA16 = (WS / "_analyza" / "s20-na16-radek.md").read_text(encoding="utf-8").strip()
assert ODDIL.startswith("## 20."), "oddíl nemá správný nadpis"
assert NA16.startswith("| **NA16** |"), "NA16 nemá správný tvar"
assert NA16.count("\n") == 0, "NA16 musí být JEDEN řádek tabulky"

# ── 1) HANDOFF: §20 na konec souboru (je to nejnovější událost) ─────────────
hand = HANDOFF.read_text(encoding="utf-8")
assert "## 20. Rozhodnutí uživatele" not in hand, "§20 už v souboru je"
novy_hand = hand.rstrip("\n") + "\n\n" + ODDIL + "\n"
assert novy_hand.count("## 20. Rozhodnutí uživatele") == 1
assert novy_hand.count("## 19. Provedeno") == 1, "§19 se ztratil"
assert novy_hand.startswith(hand[:8192]), "PŘEDCHOZÍ OBSAH HANDOFFU SE ZMĚNIL"
print("  1) HANDOFF.md §20 vloženo (%d -> %d B)"
      % (len(hand.encode("utf-8")), len(novy_hand.encode("utf-8"))))

# ── 2) KRONIKA: NA16 za NA15 ──────────────────────────────────────────────
kron = KRONIKA.read_text(encoding="utf-8")
radky = kron.split("\n")
idx = [i for i, r in enumerate(radky) if r.startswith("| **NA15** |")]
assert len(idx) == 1, "řádek NA15 není právě 1× (%d)" % len(idx)
assert radky[idx[0]].rstrip().endswith("|"), "řádek NA15 nevypadá jako tabulka"
radky.insert(idx[0] + 1, NA16)
nova_kron = "\n".join(radky)
assert nova_kron.count("| **NA16** |") == 1, "NA16 není právě 1×"
assert nova_kron.count("| **NA15** |") == 1, "NA15 se ztratil"
assert nova_kron != kron, "ZÁZNAM DO KRONIKY NEPROBĚHL"
print("  2) KRONIKA-PROJEKTU.md NA16 vloženo za NA15")

if ZAPIS:
    HANDOFF.write_bytes(novy_hand.encode("utf-8"))
    KRONIKA.write_bytes(nova_kron.encode("utf-8"))
    print()
    print("  ZAPSÁNO: HANDOFF %d B, KRONIKA %d B"
          % (len(novy_hand.encode("utf-8")), len(nova_kron.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

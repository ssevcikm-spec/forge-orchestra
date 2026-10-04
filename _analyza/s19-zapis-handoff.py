# -*- coding: utf-8 -*-
r"""Zapíše do `HANDOFF.md` §19 (push obou repů) a omyl **69** do §8g.

PROČ SKRIPTEM A S TEXTEM V SOUBORECH: `HANDOFF.md` má 2 800+ řádků a „nic se
nesmí ztratit". Text oddílu i řádku omylu jsou proto v `_analyza\s19-*.md`
(**bajt na bajt**) — české uvozovky v Python literálech rozbily v téhle session
**pět** skriptů (past `dsh-prostredi` §3d).

Použití:  python _analyza\s19-zapis-handoff.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

ODDIL = (WS / "_analyza" / "s19-push-oddil.md").read_text(encoding="utf-8").strip()
OMYL = (WS / "_analyza" / "s19-omyl69-radek.md").read_text(encoding="utf-8").strip()
assert ODDIL.startswith("### 19.1"), "oddíl §19 nemá správný nadpis"
assert OMYL.startswith("| **69** |"), "řádek omylu 69 nemá správný tvar"
assert OMYL.count("\n") == 0, "omyl 69 musí být JEDEN řádek tabulky"

text = HANDOFF.read_text(encoding="utf-8")

# ── 1) omyl 69 na konec tabulky §8g (poslední řádek je omyl 68) ─────────────
KOTVA68 = "| **68** |"
assert text.count(KOTVA68) == 1, "kotva omylu 68 není právě 1× (nalezeno %d)" % text.count(KOTVA68)
i68 = text.find(KOTVA68)
konec68 = text.find("\n", i68)
assert konec68 > i68, "řádek omylu 68 nemá konec"
novy = text[:konec68 + 1] + OMYL + "\n" + text[konec68 + 1:]
assert novy.count("| **69** |") == 1, "omyl 69 není právě 1×"
assert novy.count(KOTVA68) == 1, "omyl 68 se ztratil nebo zdvojil"
print("  1) omyl 69 vložen za omyl 68 (do tabulky §8g)")

# ── 2) §19 na KONEC souboru (je to nejnovější událost) ─────────────────────
assert "### 19.1" not in novy, "§19 už v souboru je"
novy2 = novy.rstrip("\n") + "\n\n---\n\n## 19. Provedeno 2. 10. 2026 (13:16 UTC) — PUSH obou repů\n\n" + ODDIL + "\n"
assert novy2.count("## 19. Provedeno") == 1, "§19 není právě 1×"
assert novy2.count("### 19.1") == 1, "§19.1 není právě 1×"
assert novy2.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"
assert len(novy2) > len(text), "soubor se nezvětšil"
print("  2) §19 vložen na konec souboru")

print()
print("  PŘED: %d B, %d řádků" % (len(text.encode("utf-8")), len(text.splitlines())))
print("  PO:   %d B, %d řádků" % (len(novy2.encode("utf-8")), len(novy2.splitlines())))

if ZAPIS:
    HANDOFF.write_bytes(novy2.encode("utf-8"))
    print("  ZAPSÁNO.")
else:
    print("  (dry-run — spusť s --zapis)")

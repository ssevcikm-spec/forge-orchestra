# -*- coding: utf-8 -*-
r"""Doplní do `KRONIKA-PROJEKTU.md`:
  * řádek **16** do tabulky §1 (push obou repů + odpověď na otázku o Groqu),
  * nález **H13** do §2.2 (rozpor: `providers.json` tvrdí ~6k/běh, měřeno ~14,4k),
  * poučení **L14** do §4 (krátký sha ve filtru `head_sha`).

Texty jsou v `_analyza\s19c-*.md` (bajt na bajt) — české uvozovky v Python
literálech rozbily v téhle session šest skriptů (past `dsh-prostredi` §3d).

Použití:  python _analyza\s19c-dopln-kroniku.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ZAPIS = "--zapis" in sys.argv

RADEK16 = (WS / "_analyza" / "s19c-radek16.md").read_text(encoding="utf-8").strip()
H13 = (WS / "_analyza" / "s19c-h13.md").read_text(encoding="utf-8").strip()
L14 = (WS / "_analyza" / "s19c-l14.md").read_text(encoding="utf-8").strip()

for popis, text, predpona in (("řádek 16", RADEK16, "| **16** |"),
                              ("H13", H13, "| **H13** |"),
                              ("L14", L14, "| **L14** |")):
    assert text.startswith(predpona), "%s nezačíná %r" % (popis, predpona)
    assert text.count("\n") == 0, "%s musí být JEDEN řádek tabulky" % popis

kron = KRONIKA.read_text(encoding="utf-8")
radky = kron.split("\n")


def vloz_za(kotva: str, novy: str, popis: str) -> None:
    """Vloží `novy` ZA řádek začínající `kotva` (kotva musí být právě 1×)."""
    idx = [i for i, r in enumerate(radky) if r.startswith(kotva)]
    assert len(idx) == 1, "%s: kotva %r je %dx, ne 1×" % (popis, kotva, len(idx))
    assert radky[idx[0]].rstrip().endswith("|"), "%s: řádek nevypadá jako tabulka" % popis
    radky.insert(idx[0] + 1, novy)
    print("  %-14s vloženo za řádek %d" % (popis, idx[0] + 1))


print("=" * 78)
print("DOPLNĚNÍ KRONIKY — řádek 16, nález H13, poučení L14")
print("=" * 78)
vloz_za("| **15** |", RADEK16, "řádek 16")
vloz_za("| **H12** |", H13, "nález H13")
vloz_za("| **L13** |", L14, "poučení L14")

nova = "\n".join(radky)
assert nova != kron, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
for popis, kotva in (("řádek 16", "| **16** |"), ("H13", "| **H13** |"),
                     ("L14", "| **L14** |"), ("řádek 15", "| **15** |"),
                     ("H12", "| **H12** |"), ("L13", "| **L13** |")):
    pocet = nova.count(kotva)
    assert pocet == 1, "%s: %dx (má být 1×)" % (popis, pocet)
    print("  kontrola: %-10s 1x OK" % popis)

if ZAPIS:
    KRONIKA.write_bytes(nova.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(kron.encode("utf-8")), len(nova.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

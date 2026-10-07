# -*- coding: utf-8 -*-
r"""P26 — SONDA (jednorázová): KDE VŠUDE žijí řádky tabulek Hxx a co v nich je?

PROČ: nález P25-K tvrdí, že `ov-g-neovereno.py` čte jen `HANDOFF.md`, a proto
místo 99 řádků měří 1. Sonda to měří **nezávisle na tom měřidle**: projde
VŠECHNY soubory `HANDOFF*.md` ve stromě (včetně `_analyza/` a snapshotů),
spočítá řádky `| **Hxx** |` a u každého zvlášť
  (a) výskyt textu `NEOVĚŘENO` KDEKKOLI na řádku (co dělá dnešní měřidlo),
  (b) výskyt ve DRUHÉ buňce („popis") a ve TŘETÍ („doklad") — aby bylo vidět,
      jestli by naivní rozšíření rozsahu nechytilo CITACI místo TVRZENÍ.

Je to SONDA: odpovídá na jednu otázku, není to brána. Do `g3` nepatří.
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
RADEK = re.compile(r"^\|\s*\*\*(H\d+)\*\*\s*\|")


def bunky(radek):
    """Buňky řádku tabulky (bez prázdných krajních)."""
    c = radek.split("|")
    return [x.strip() for x in c[1:-1]]


def main():
    print("=" * 92)
    print("P26 SONDA — rozsah tabulek Hxx ve VŠECH `HANDOFF*.md` stromu")
    print("=" * 92)
    print("  %-52s %6s %8s %8s %8s" % ("soubor", "řádků", "NEOVř", "popis", "doklad"))
    celkem = [0, 0, 0, 0]
    for p in sorted(WS.rglob("HANDOFF*.md")):
        if ".git" in p.parts:
            continue
        try:
            radky = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError as e:
            print("  %-52s  CHYBA CTENI: %s" % (str(p.relative_to(WS))[:52], e))
            continue
        h = [(i, l) for i, l in enumerate(radky, 1) if RADEK.match(l)]
        if not h:
            continue
        nev = sum(1 for _, l in h if "NEOVĚŘENO" in l)
        vpop = sum(1 for _, l in h
                   if len(bunky(l)) > 1 and "NEOVĚŘENO" in bunky(l)[1])
        vdok = sum(1 for _, l in h
                   if len(bunky(l)) > 2 and "NEOVĚŘENO" in bunky(l)[2])
        rel = str(p.relative_to(WS))
        print("  %-52s %6d %8d %8d %8d" % (rel[:52], len(h), nev, vpop, vdok))
        if rel in ("HANDOFF.md", "_archiv/HANDOFF-HISTORIE.md"):
            celkem[0] += len(h)
            celkem[1] += nev
            celkem[2] += vpop
            celkem[3] += vdok
    print("-" * 92)
    print("  ŽIVÉ ZDROJE (HANDOFF.md + _archiv/HANDOFF-HISTORIE.md): "
          "řádků=%d NEOVĚŘENO=%d (popis=%d, doklad=%d)"
          % (celkem[0], celkem[1], celkem[2], celkem[3]))
    print("=" * 92)
    return 0


if __name__ == "__main__":
    sys.exit(main())

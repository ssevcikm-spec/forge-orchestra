"""Změří SKLON hranice mezi šedou místností a červenou zdí na snímku hry.

PROČ PRÁVĚ TENHLE TEST: dlaždice jsou buď
  • KOSOČTVERCE (izometrie 2:1) – hranice oblasti se schoduje po 2 px vodorovně
    a 1 px svisle (sklon 1:2), protože se skládá z hran kosočtverců,
  • ČTVERCE – hranice místnosti je rovná VODOROVNÁ nebo SVISLÁ čára.

Měření: pro každý řádek se najde x, kde nastane přechod šedá↔červená, a sleduje
se, jak se to x mění mezi řádky (dx/dy). U izometrie vyjde |dx/dy| ≈ 2.

POZOR: měří se jen v ÚZKÉM pruhu, kde hranice není zakrytá postavami ani HUD.
"""
from __future__ import annotations

import sys
from pathlib import Path

from PIL import Image

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def je_seda(px) -> bool:
    r, g, b = px
    # šedá místnost: kanály blízko sebe, střední jas
    return abs(r - g) < 22 and abs(g - b) < 22 and 60 < r < 175


def je_cervena(px) -> bool:
    r, g, b = px
    # červená zeď: r výrazně nad g i b
    return r > g + 25 and r > b + 25


def main() -> int:
    if len(sys.argv) < 2:
        print("Použití: python orchestra/tools/mer-sklon-hranice.py <obrazek.png>")
        return 2
    cesta = Path(sys.argv[1])
    with Image.open(cesta) as im:
        rgb = im.convert("RGB")
        W, H = rgb.size
        px = rgb.load()

        # Pro každý řádek najdi VŠECHNY přechody šedá→červená a zpět.
        prechody: list[tuple[int, int]] = []   # (y, x)
        for y in range(int(H * 0.15), int(H * 0.85)):
            for x in range(2, W - 2):
                a, b = px[x - 1, y], px[x, y]
                if (je_seda(a) and je_cervena(b)) or (je_cervena(a) and je_seda(b)):
                    prechody.append((y, x))

    print(f"Snímek {W}×{H}, přechodů šedá↔červená: {len(prechody)}")
    if len(prechody) < 20:
        print("Málo přechodů – nedá se měřit (hranice je zakrytá nebo jiné barvy).")
        return 1

    # Poskládej přechody do stop: v jednom řádku může být víc přechodů, proto se
    # spojují jen ty, které na sebe navazují v x (do ±6 px) mezi sousedními řádky.
    podle_y: dict[int, list[int]] = {}
    for y, x in prechody:
        podle_y.setdefault(y, []).append(x)

    sklony: list[float] = []
    for y in sorted(podle_y):
        if y + 1 not in podle_y:
            continue
        for xa in podle_y[y]:
            # najdi nejbližší přechod v dalším řádku
            kandidati = [xb for xb in podle_y[y + 1] if abs(xb - xa) <= 4]
            if kandidati:
                xb = min(kandidati, key=lambda v: abs(v - xa))
                dx = xb - xa
                if dx != 0:
                    sklony.append(abs(dx))   # dx na 1 řádek = sklon

    if not sklony:
        print("Nenašly se navazující přechody mezi řádky – hranice není spojitá.")
        return 1

    from collections import Counter
    citac = Counter(sklony)
    print(f"Naměřených kroků (dx na 1 řádek): {len(sklony)}")
    print("Nejčastější kroky:")
    for krok, pocet in citac.most_common(6):
        print(f"  dx={krok}px  {pocet}×  ({100 * pocet / len(sklony):.0f} %)")

    # Podíl kroků odpovídajících izometrii 2:1 (dx ≈ 2) proti osovým (dx = 0,
    # ty se sem nedostanou, protože dx=0 se zahazuje → rovná hranice = málo dat)
    iso = sum(p for k, p in citac.items() if k == 2)
    male = sum(p for k, p in citac.items() if k == 1)
    print()
    print(f"  krok 2 px (izometrie 2:1) : {iso}  ({100 * iso / len(sklony):.0f} %)")
    print(f"  krok 1 px (mírný sklon)   : {male}  ({100 * male / len(sklony):.0f} %)")
    if iso / len(sklony) >= 0.5:
        print("  → HRANICE SE SCHODUJE PO 2 px = odpovídá IZOMETRII 2:1")
    elif male / len(sklony) >= 0.5:
        print("  → HRANICE SE SCHODUJE PO 1 px = spíš přerušovaná/neizometrická")
    else:
        print("  → SKLON NEODPOVÍDÁ jednoznačně ani jednomu; hranice je zubatá")
    return 0


if __name__ == "__main__":
    sys.exit(main())

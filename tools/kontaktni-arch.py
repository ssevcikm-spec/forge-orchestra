#!/usr/bin/env python
r"""Sestaví kontaktní arch spritů – jeden PNG, na který se dá podívat jedním pohledem.

PROČ TO EXISTUJE: brány měří ("mince je 0,67x truhly", "v truhle prosvítá díra"),
ale nepoznají OBSAH – že postavě chybí obličej, že meč je z jiné hry, že je sprite
useknutý. Na to se musí někdo podívat. U ruční kontroly 258 souborů to ale nikdo
dělat nebude, takže se udělá jeden arch.

Agent v DSH se na něj podívá vestavěným nástrojem `read_image` (zdarma, okamžitě).
V CI runneru `read_image` není – tam stejný arch poslouží `.forge/vision.mjs`
s klíčem Gemini.

Použití:
    python orchestra/tools/kontaktni-arch.py <slozka> [-o arch.png]
    python orchestra/tools/kontaktni-arch.py games/uo-shadows/tools/blender/sprites \
        --recurse --cell 64 --cols 16 --label
Návratový kód: 0 = arch zapsán, 2 = chyba vstupu.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

from PIL import Image, ImageDraw

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# Podklad, na kterém je vidět i bílý a i černý sprite. Šachovnice je standard:
# kdyby byl podklad jednolitý, splyne s ním buď bílá, nebo černá část spritu
# a "chybí obličej" by se schovalo.
SVETLA = (210, 210, 214)
TMAVA = (168, 168, 174)


def _podklad(w: int, h: int, krok: int = 8) -> Image.Image:
    img = Image.new("RGBA", (w, h), SVETLA + (255,))
    d = ImageDraw.Draw(img)
    for y in range(0, h, krok):
        for x in range(0, w, krok):
            if (x // krok + y // krok) % 2:
                d.rectangle([x, y, x + krok - 1, y + krok - 1], fill=TMAVA + (255,))
    return img


def sestav(slozka: Path, out: Path, cell: int, cols: int, label: bool,
           recurse: bool, filtr: str) -> int:
    vzor = "**/*.png" if recurse else "*.png"
    soubory = sorted(
        p for p in slozka.glob(vzor)
        if p.is_file() and not p.name.startswith("_") and filtr in p.name
    )
    if not soubory:
        print(f"CHYBA: ve {slozka} nejsou žádné PNG (filtr '{filtr}')")
        return 2

    popisek = 11 if label else 0
    vyska_cell = cell + popisek
    radku = (len(soubory) + cols - 1) // cols
    arch = _podklad(cols * cell, radku * vyska_cell)
    draw = ImageDraw.Draw(arch)

    for i, f in enumerate(soubory):
        cx = (i % cols) * cell
        cy = (i // cols) * vyska_cell
        try:
            sp = Image.open(f).convert("RGBA")
        except Exception as e:  # poškozený soubor nesmí shodit celý arch
            draw.rectangle([cx, cy, cx + cell - 1, cy + cell - 1], outline=(255, 0, 0, 255))
            print(f"  VAROVANI: {f.name} se nenačetl ({e})")
            continue

        # Zmenšení na celu se ZACHOVÁNÍM poměru stran – natažení by zkreslilo
        # přesně to, co chceme posoudit (proporce postavy).
        sp.thumbnail((cell, cell), Image.LANCZOS)
        arch.alpha_composite(sp, (cx + (cell - sp.width) // 2, cy + (cell - sp.height) // 2))

        if label:
            jmeno = f.stem if len(f.stem) <= 14 else f.stem[:13] + "."
            draw.text((cx + 2, cy + cell + 1), jmeno, fill=(20, 20, 20, 255))

    # Mřížka odděluje cely, aby se sousední sprity nepletly dohromady.
    for x in range(0, arch.width + 1, cell):
        draw.line([(x, 0), (x, arch.height)], fill=(120, 120, 126, 255))
    for y in range(0, arch.height + 1, vyska_cell):
        draw.line([(0, y), (arch.width, y)], fill=(120, 120, 126, 255))

    out.parent.mkdir(parents=True, exist_ok=True)
    arch.convert("RGB").save(out, "PNG", optimize=True)
    print(f"Kontaktní arch: {out}")
    print(f"  spritů {len(soubory)}, mřížka {cols}×{radku}, cela {cell} px, "
          f"arch {arch.width}×{arch.height} px")
    print(f"  Teď se na něj podívej: read_image \"{out}\"")
    return 0


def main() -> int:
    ap = argparse.ArgumentParser(description="Kontaktní arch spritů pro vizuální kontrolu")
    ap.add_argument("slozka", help="složka s PNG sprity")
    ap.add_argument("-o", "--out", default=None, help="výstupní PNG (výchozí <slozka>/_kontaktni-arch.png)")
    ap.add_argument("--cell", type=int, default=64, help="velikost jedné cely v px (výchozí 64)")
    ap.add_argument("--cols", type=int, default=12, help="počet sloupců (výchozí 12)")
    ap.add_argument("--label", action="store_true", help="popisky názvů pod sprity")
    ap.add_argument("--recurse", action="store_true", help="i podsložky")
    ap.add_argument("--filter", dest="filtr", default="", help="jen soubory obsahující text")
    args = ap.parse_args()

    slozka = Path(args.slozka)
    if not slozka.is_dir():
        print(f"CHYBA: {slozka} není složka")
        return 2

    # Výstup začínající podtržítkem se do archu nebere (jinak by sebral sám sebe
    # při dalším spuštění) – proto i výchozí název začíná podtržítkem.
    out = Path(args.out) if args.out else slozka / "_kontaktni-arch.png"
    return sestav(slozka, out, args.cell, args.cols, args.label, args.recurse, args.filtr)

if __name__ == "__main__":
    sys.exit(main())

"""Kontrola schématu musí číst KÓD, ne komentáře.

PROČ: `level.gd` má v hlavičce komentář, který cituje STARÝ chybný vzorec jako
historii („dřív tu bylo `s.position = offset + Vector2(x*cell, y*cell)` …").
Kontrola hledala ten vzorec v celém textu, našla ho v komentáři a hlásila vadu
i po opravě.

To je klasická past statických kontrol: **komentář popisující vadu vypadá pro
regex jako vada.** Řešení je odstranit komentáře (a docstringy) PŘED hledáním.

V GDScriptu začíná komentář `#`, takže stačí odříznout vše od prvního `#` na
řádku. Řetězce s `#` uvnitř (např. barva "#fff") by to rozbilo, ale v tomhle
souboru žádné nejsou – a kdyby byly, je to vidět v testech.

Použití: python orchestra/tools/oprav-check-schema-komentare.py
"""
from __future__ import annotations

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOPIE = [
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.forge\check-schema.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\check-schema.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\tools\kontrola-schematu.py"),
]

STARE = '''        t = lg.read_text(encoding="utf-8", errors="replace")
        data["level_gd"] = {}'''

NOVE = '''        t = lg.read_text(encoding="utf-8", errors="replace")
        # KOMENTÁŘE SE ODSTRANÍ, NEŽ SE HLEDAJÍ VZORCE. Soubor v hlavičce cituje
        # STARÝ chybný vzorec jako historii – a statická kontrola ho pak najde
        # a hlásí vadu i po opravě (přesně to se stalo). Komentář popisující
        # vadu nesmí vypadat jako vada.
        t = "\\n".join(radek.split("#", 1)[0] for radek in t.splitlines())
        data["level_gd"] = {}'''

upraveno = 0
for cesta in KOPIE:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje")
        continue
    t = cesta.read_text(encoding="utf-8")
    if "KOMENTÁŘE SE ODSTRANÍ" in t:
        print(f"  --   {cesta.parent.parent.name}\\{cesta.name}: už upraveno")
        continue
    if STARE not in t:
        print(f"  CHYBA {cesta.parent.parent.name}\\{cesta.name}: nenalezen blok")
        continue
    cesta.write_text(t.replace(STARE, NOVE, 1), encoding="utf-8")
    upraveno += 1
    print(f"  OK   {cesta.parent.parent.name}\\{cesta.name}: komentáře se nehledají")

print()
print(f"Upraveno: {upraveno}")

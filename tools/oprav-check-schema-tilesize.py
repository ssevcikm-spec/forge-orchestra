"""Oprava kontroly schématu: `tile_size` může být ČÍSLO i SEZNAM.

PROČ: `check-schema.py` vznikl, když dlaždice byly čtverce 32×32 a manifest měl
`"tile_size": 32` (číslo). Izometrická dlaždice je ale kosočtverec, takže nový
generátor zapisuje `"tile_size": [96, 48]`. Kontrola na to spadla:

    TypeError: int() argument must be ... not 'list'

Je to poučné: **kontrola, která spadne, není totéž jako kontrola, která našla
vadu** – a kdyby tenhle pád nikdo neviděl, vypadal by skoro jako „něco je
špatně". Nástroj proto musí zvládat oba tvary, ne předpokládat jeden.

Upravuje všechny tři kopie (šablona, herní repo, zdroj v tools) –
aby nevznikl drift, kvůli kterému ten nástroj vůbec existuje.

Použití: python orchestra/tools/oprav-check-schema-tilesize.py
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

STARE = '''    tm = repo / "assets" / "tiles" / "manifest.json"
    if tm.is_file():
        d = _nacti_json(tm)
        ts = d.get("tile_size")
        data["tiles_manifest"] = {"tile_size": ts}
        if ts and tile_w and int(ts) != int(tile_w) and int(ts) != int(tile_h or 0):
            vady.append(
                f"assets/tiles/manifest.json: tile_size {ts}px, spec deklaruje "
                f"{tile_w}×{tile_h} – dlaždice se ve hře škálují")
    else:
        poznamky.append("assets/tiles/manifest.json není – dlaždice nelze ověřit")'''

NOVE = '''    tm = repo / "assets" / "tiles" / "manifest.json"
    if tm.is_file():
        d = _nacti_json(tm)
        ts = d.get("tile_size")
        data["tiles_manifest"] = {"tile_size": ts}
        # `tile_size` může být ČÍSLO (čtvercová dlaždice: 32) i SEZNAM
        # (kosočtverec: [96, 48]). První verze kontroly počítala jen s číslem
        # a na seznam spadla na TypeError – což je něco jiného než „našla vadu".
        if isinstance(ts, (list, tuple)):
            ts_w = int(ts[0]) if len(ts) > 0 else None
            ts_h = int(ts[1]) if len(ts) > 1 else ts_w
        elif ts is not None:
            ts_w = ts_h = int(ts)
        else:
            ts_w = ts_h = None
        if ts_w and tile_w and tile_h:
            if ts_w != int(tile_w) or ts_h != int(tile_h):
                vady.append(
                    f"assets/tiles/manifest.json: tile_size {ts_w}×{ts_h}, spec "
                    f"deklaruje {tile_w}×{tile_h} – dlaždice se ve hře škálují")
    else:
        poznamky.append("assets/tiles/manifest.json není – dlaždice nelze ověřit")'''

upraveno = 0
for cesta in KOPIE:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje, přeskakuji")
        continue
    t = cesta.read_text(encoding="utf-8")
    if NOVE in t:
        print(f"  --   {cesta.parent.parent.name}\\{cesta.name}: už upraveno")
        continue
    if STARE not in t:
        print(f"  CHYBA {cesta.parent.parent.name}\\{cesta.name}: nenalezen blok k výměně")
        continue
    cesta.write_text(t.replace(STARE, NOVE, 1), encoding="utf-8")
    upraveno += 1
    print(f"  OK   {cesta.parent.parent.name}\\{cesta.name}: tile_size číslo i seznam")

print()
print(f"Upraveno: {upraveno}")

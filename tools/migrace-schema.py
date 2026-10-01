"""Migrace hry uo-shadows na schéma z spec.json.

CO SE MĚNÍ (a proč):
  project.godot   480×270 → 960×540. `spec.json` deklaruje viewport 960×540,
                  ale hra renderovala do 480×270. Sprites (128 px plátno,
                  96 px postava) byly pro 480×270 dvojnásobně velké → dlaždice
                  96×48 by přes ně přetékaly.
  main.json       `cell` 16 → 96 (velikost dlaždice ze specu), viewport 960×540.
                  Mřížka (30×16 znaků) se NEMĚNÍ – je projekčně neutrální.
  manifest.json   tile_size 16 → 96/48, doplněna projekce.
  game.gd         volání `vystredni_na_spawn`, aby hráč viděl sám sebe.

Zapisuje se Pythonem (ne PowerShellem) – ten soubory s diakritikou jednou
poškodil (viz HANDOFF.md).

Použití: python orchestra/tools/migrace-schema.py
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HRA = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows")

zmeny: list[str] = []


def uprav(cesta: pathlib.Path, stary: str, novy: str, popis: str) -> None:
    t = cesta.read_text(encoding="utf-8")
    if stary not in t:
        if novy in t:
            zmeny.append(f"  --   {popis}: už hotovo")
        else:
            zmeny.append(f"  CHYBA {popis}: nenalezeno {stary!r}")
        return
    cesta.write_text(t.replace(stary, novy, 1), encoding="utf-8")
    zmeny.append(f"  OK   {popis}")


# ------------------------------------------------------------- project.godot --
pg = HRA / "project.godot"
uprav(pg, "window/size/viewport_width=480", "window/size/viewport_width=960",
      "project.godot: šířka viewportu 480 → 960")
uprav(pg, "window/size/viewport_height=270", "window/size/viewport_height=540",
      "project.godot: výška viewportu 270 → 540")

# ---------------------------------------------------------------- main.json --
mp = HRA / "assets" / "levels" / "main.json"
d = json.loads(mp.read_text(encoding="utf-8-sig"))
if d.get("cell") != 96:
    d["cell"] = 96
    zmeny.append(f"  OK   main.json: cell → 96 (bylo {d.get('cell')})")
else:
    zmeny.append("  --   main.json: cell už 96")
if list(d.get("viewport", [])) != [960, 540]:
    d["viewport"] = [960, 540]
    zmeny.append("  OK   main.json: viewport → 960×540")
else:
    zmeny.append("  --   main.json: viewport už 960×540")
# Komentář k projekci – aby bylo z dat poznat, že mřížka je neutrální.
d["_projekce"] = ("izometricka – mřížka je jen znaky, projekci určuje "
                  "assets/spec.json a scripts/level.gd")
mp.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# ------------------------------------------------------- levels/manifest.json --
lm = HRA / "assets" / "levels" / "manifest.json"
if lm.is_file():
    m = json.loads(lm.read_text(encoding="utf-8-sig"))
    for lvl in m.get("levels", []):
        if lvl.get("name") == "main":
            lvl["cell"] = 96
    m["note"] = ("mřížka je text (0=zeď, 1=místnost, 2=chodba); buňka 96 px "
                 "podle assets/spec.json; spawn a mince jsou středy místností, "
                 "průchodnost ověřená flood fillemp")
    lm.write_text(json.dumps(m, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    zmeny.append("  OK   levels/manifest.json: cell → 96")
else:
    zmeny.append("  --   levels/manifest.json: není")

# ------------------------------------------------------------------- game.gd --
gg = HRA / "scripts" / "game.gd"
t = gg.read_text(encoding="utf-8")
if "vystredni_na_spawn" in t:
    zmeny.append("  --   game.gd: vystredni_na_spawn už je volané")
else:
    # Vloží se hned po `level.build()` – tehdy už je známý viewport i spawn.
    vzor = re.compile(r"(\tlevel\.build\(\))")
    if vzor.search(t):
        t = vzor.sub(
            r"\1\n\t# Mapa se vystředí na spawn: bez toho je spawn (17,7)\n"
            r"\t# v izometrii na y = 576, tedy POD obrazovkou (viewport je 540).\n"
            r"\tlevel.vystredni_na_spawn(get_viewport_rect().size)\n"
            r"\tlevel.build()", t, count=1)
        gg.write_text(t, encoding="utf-8")
        zmeny.append("  OK   game.gd: vystředění na spawn (před build)")
    else:
        zmeny.append("  CHYBA game.gd: nenalezeno `level.build()`")

print("Migrace schématu uo-shadows:")
for z in zmeny:
    print(z)
chyb = [z for z in zmeny if "CHYBA" in z]
print()
print("HOTOVO" if not chyb else f"NALEZENO {len(chyb)} CHYB")
sys.exit(1 if chyb else 0)

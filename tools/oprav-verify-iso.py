"""Naučí `verify-level-render.py` izometrickou projekci (a hlavně ji NEHÁDAT).

PROČ: kontrola porovnává snímek hry s mapou v JSON a počítá střed buňky jako
`off + x*cell + cell/2`. To platí pro obdélníkovou mřížku. Po migraci na
izometrii se dlaždice kreslí na `((x-y)*w/2, (x+y)*h/2)` – a navíc se mapa
VYSTŘEĎUJE NA SPAWN, takže `offset` v datech nezná skutečné posunutí.

CO SE MĚNÍ:
  1. Střed buňky se počítá podle projekce (izo vs. obdélník) a dlaždice může
     mít jinou šířku a výšku (96×48 = kosočtverec).
  2. Offset se pro izometrii POČÍTÁ z dat: `viewport/2 − spawn_iso`, tedy přesně
     to, co dělá `level.gd::vystredni_na_spawn`. Hledání posunutí to pak jen
     doladí (třes obrazovky).

Bez toho by kontrola po migraci hlásila „mapa se nevykreslila podle JSON",
i kdyby byla vykreslená správně – což je přesně ten falešný poplach, kterým
už jednou prošla kontrola schématu.

Použití: python orchestra/tools/oprav-verify-iso.py
"""
from __future__ import annotations

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOPIE = [
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\verify-level-render.py"),
    pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.forge\verify-level-render.py"),
]

# --- 1) porovnej(): střed buňky podle projekce --------------------------------
STARE_SIG = '''def porovnej(img, grid, cell, off_x, off_y, want, palety, ignorovat, marker_cells,
             wrong_limit: int = 8):'''
NOVE_SIG = '''def stred_bunky(x: int, y: int, projekce: str, cell: int, cell_h: int,
                off_x: float, off_y: float) -> tuple[int, int]:
    """Střed dlaždice (x, y) na snímku – podle projekce, ne natvrdo čtvercově.

    Izometrie kreslí na ((x-y)*w/2, (x+y)*h/2); obdélník na (x*w, y*h).
    Když se to splete, kontrola hlásí chybu na SPRÁVNĚ vykreslené mapě.
    """
    if projekce.startswith("izo"):
        return (int(round(off_x + (x - y) * cell / 2.0)),
                int(round(off_y + (x + y) * cell_h / 2.0)))
    return (int(off_x + x * cell + cell / 2.0),
            int(off_y + y * cell_h + cell_h / 2.0))


def porovnej(img, grid, cell, off_x, off_y, want, palety, ignorovat, marker_cells,
             wrong_limit: int = 8, projekce: str = "ctvercova", cell_h: int = 0):'''
STARE_STRED = '''            px = int(off_x + x * cell + cell / 2)
            py = int(off_y + y * cell + cell / 2)'''
NOVE_STRED = '''            px, py = stred_bunky(x, y, projekce, cell, cell_h or cell, off_x, off_y)'''

# --- 2) main(): projekce, cell_h a dopočet offsetu pro izometrii --------------
STARE_MAIN = '''    grid = level["grid"]
    cell = int(level["cell"])
    off_x, off_y = level.get("offset", [0, 0])'''
NOVE_MAIN = '''    grid = level["grid"]
    # PROJEKCE SE ČTE ZE SPECU HRY, ne z levelu: schéma je vlastnost hry.
    spec_cesta = level_path.parent.parent / "spec.json"
    projekce, cell, cell_h = "ctvercova", int(level["cell"]), 0
    if spec_cesta.is_file():
        try:
            spec = json.loads(spec_cesta.read_text(encoding="utf-8-sig"))
            proj = spec.get("projekce", {})
            tile = spec.get("tile", {})
            projekce = str(proj.get("typ") or "").lower()
            cw = proj.get("dlazdice_sirka") or tile.get("sirka")
            ch = proj.get("dlazdice_vyska") or tile.get("vyska")
            if cw:
                cell = int(cw)
            if ch:
                cell_h = int(ch)
            if not projekce:
                projekce = "izometricka" if cell != cell_h else "ctvercova"
        except Exception as e:
            print(f"VAROVÁNÍ: {spec_cesta} nejde přečíst ({e}) – beru obdélníkovou mřížku")
    if not cell_h:
        cell_h = cell

    off_x, off_y = level.get("offset", [0, 0])
    # IZOMETRICKÝ OFFSET SE POČÍTÁ, NEHÁDÁ: hra mapu vystřeďuje na spawn
    # (`level.gd::vystredni_na_spawn`), takže `offset` v datech nezná skutečné
    # posunutí. Bere se stejný vzorec jako ve hře – a hledání posunutí níž ho
    # jen doladí (třes obrazovky).
    if projekce.startswith("izo"):
        spawn = None
        for m in level.get("markers", []):
            if str(m.get("type")) == "spawn":
                spawn = (int(m["cell"][0]), int(m["cell"][1]))
        vp = spec.get("viewport") if spec_cesta.is_file() else None
        if spawn and vp:
            sx = (spawn[0] - spawn[1]) * cell / 2.0
            sy = (spawn[0] + spawn[1]) * cell_h / 2.0
            off_x = int(vp[0]) / 2.0 - sx
            off_y = int(vp[1]) / 2.0 - sy
            print(f"Izometrie: offset počítán z viewportu a spawnu {spawn} "
                  f"→ ({off_x:.0f}, {off_y:.0f})")'''

# --- 3) volání porovnej s projekcí -------------------------------------------
STARE_VOLANI = '''            v = porovnej(img, grid, cell, off_x + dx, off_y + dy, want, palety,
                         ignorovat, marker_cells)'''
NOVE_VOLANI = '''            v = porovnej(img, grid, cell, off_x + dx, off_y + dy, want, palety,
                         ignorovat, marker_cells, projekce=projekce, cell_h=cell_h)'''

# --- 4) výpis ----------------------------------------------------------------
STARE_VYPIS = '''    print(f"Snímek {img.width}×{img.height}, úroveň {len(grid[0])}×{len(grid)} "
          f"po {cell}px, offset {[off_x + ddx, off_y + ddy]}")'''
NOVE_VYPIS = '''    rozmer = f"{cell}×{cell_h}px" if cell != cell_h else f"{cell}px"
    print(f"Snímek {img.width}×{img.height}, úroveň {len(grid[0])}×{len(grid)} "
          f"{projekce} po {rozmer}, offset {[round(off_x + ddx), round(off_y + ddy)]}")'''

ZAMENY = [
    (STARE_SIG, NOVE_SIG, "střed buňky podle projekce"),
    (STARE_STRED, NOVE_STRED, "výpočet px/py"),
    (STARE_MAIN, NOVE_MAIN, "projekce + dopočet izo offsetu"),
    (STARE_VOLANI, NOVE_VOLANI, "předání projekce do porovnej"),
    (STARE_VYPIS, NOVE_VYPIS, "výpis rozměru dlaždice"),
]

for cesta in KOPIE:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje, přeskakuji")
        continue
    t = cesta.read_text(encoding="utf-8")
    if "stred_bunky" in t:
        print(f"  --   {cesta.parent.parent.name}: už upraveno")
        continue
    chybi = [popis for stare, _, popis in ZAMENY if stare not in t]
    if chybi:
        print(f"  CHYBA {cesta.parent.parent.name}: nenalezeno – {', '.join(chybi)}")
        continue
    for stare, nove, _ in ZAMENY:
        t = t.replace(stare, nove, 1)
    cesta.write_text(t, encoding="utf-8")
    print(f"  OK   {cesta.parent.parent.name}: 5 úprav (izo projekce)")

from __future__ import annotations

import pathlib as _pl

# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.
# `tools/` je primo v koreni repa, takze _PARENT = root repa.
_PARENT = _pl.Path(__file__).resolve().parents[1]
"""Diagnostika čtyř selhání v baseline testech – tiskne SKUTEČNÉ hodnoty."""
import sys
import tempfile
from pathlib import Path

sys.path.insert(0, str(_PARENT / 'repo' / '.forge'))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

import baseline as B  # noqa: E402
from PIL import Image  # noqa: E402

tmp = Path(tempfile.mkdtemp(prefix="diag-"))
(tmp / ".forge").mkdir(parents=True)
sp = tmp / "assets" / "sprites"
sp.mkdir(parents=True)

B._png_barva(sp / "hrdina.png", (200, 30, 30))
B._png_barva(sp / "mince.png", (240, 200, 40))
B._png_barva(sp / "_nahléd.png", (10, 10, 10))
B._png_barva(tmp / "tools" / "blender" / "sprites" / "body_d0_f0.png", (30, 200, 30))


def vypis(nazev, hodnota):
    print(f"{nazev:22} {hodnota}")


print("=== 1) které soubory se berou ===")
for p in B.sledovane_soubory(tmp):
    print(f"   {B.klic(tmp, p)}   (name={p.name!r}, startswith_={p.name.startswith('_')})")

print()
print("=== 2) phash červené vs modré ===")
cesta = sp / "hrdina.png"
ph_cervena = B.phash(cesta)
print(f"   červená {ph_cervena}")
B._png_barva(cesta, (30, 30, 210))
ph_modra = B.phash(cesta)
print(f"   modrá   {ph_modra}")
print(f"   liší se? {ph_cervena != ph_modra}")
B._png_barva(cesta, (200, 30, 30))  # zpět na červenou

print()
print("=== 3) co vrací kontrola pro různé stavy ===")
ev = B.Evidence(tmp)
for p in B.sledovane_soubory(tmp):
    B.zapis_polozky(ev, p, "clovek", "test")
ev.baseline["schvaleno"] = B.cas()
ev.uloz()
print(f"   zapsané klíče: {sorted(ev.baseline['polozky'].keys())}")
print(f"   kontrola(hrdina)  = {ev.kontrola(cesta)}")
print(f"   klic(tmp, cesta)  = {B.klic(tmp, cesta)!r}")

print()
print("=== 4) co vypisuje CLI ===")
import subprocess
v = subprocess.run(
    [sys.executable, str(Path(B.__file__).resolve()), "--koren", str(tmp),
     "--json", "kontrola", "assets/sprites/mince.png"],
    capture_output=True, text=True, encoding="utf-8")
print(f"   returncode={v.returncode}")
print(f"   STDOUT={v.stdout!r}")
print(f"   STDERR={v.stderr[:300]!r}")
print(f"   tmp={tmp}")

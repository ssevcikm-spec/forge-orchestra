"""Co je na stanici k dispozici pro práci s obrázkem a viděním.

PROČ TO EXISTUJE: plán vizuální kontroly nesmí stát na knihovnách, které tu
nejsou. Tenhle skript je inventura – dá se kdykoli zopakovat a je vidět, co
přibylo nebo zmizelo.

Použití:  python orchestra/tools/inventura-vize.py
"""
from __future__ import annotations

import importlib
import shutil
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# (modul, k čemu by byl)
MODULY = [
    ("PIL", "Pillow – načtení, změna velikosti, skládání archů (už se používá)"),
    ("numpy", "matice pixelů – metriky, průměry, histogramy"),
    ("scipy", "binary_fill_holes, filtry, vzdálenostní transformace"),
    ("skimage", "SSIM, strukturální podobnost, prahování, kontury"),
    ("cv2", "OpenCV – template matching, ORB/feature matching, optický tok"),
    ("imagehash", "perceptual hash (pHash/dHash) – pozná, že se obrázek nezměnil"),
    ("rembg", "odstranění pozadí neuronkou (U2-Net) místo podle barvy"),
    ("torch", "běh lokálních modelů (CLIP, VLM) na GPU"),
    ("transformers", "HuggingFace – CLIP, BLIP, Qwen-VL"),
    ("onnxruntime", "ONNX modely bez PyTorche"),
    ("pytesseract", "OCR – čtení textu ze screenshotu (HUD, chyby)"),
]

# (nástroj na PATH, k čemu by byl)
NASTROJE = [
    ("blender", "3D → 2D render (mimo PATH, viz MOZNOSTI-AGENTA.md)"),
    ("godot", "vykreslení scény do PNG (mimo PATH)"),
    ("magick", "ImageMagick – dávkové úpravy, montáže, diffs"),
    ("ffmpeg", "video/GIF z framů chůze (kontrola animace okem)"),
    ("tesseract", "OCR z příkazové řádky"),
    ("python", "skripty"),
]

print("=== Python moduly ===")
ma, chybi = [], []
for m, popis in MODULY:
    try:
        mod = importlib.import_module(m)
        verze = getattr(mod, "__version__", "?")
        print(f"  JE     {m:15} {str(verze):12} {popis}")
        ma.append(m)
    except Exception as e:
        print(f"  CHYBI  {m:15} {'':12} {popis}  ({type(e).__name__})")
        chybi.append(m)

print()
print("=== Nástroje na PATH ===")
for n, popis in NASTROJE:
    cesta = shutil.which(n)
    print(f"  {'JE    ' if cesta else 'CHYBI '} {n:12} {(cesta or '')[:55]}")

print()
print(f"Modulů je: {len(ma)}, chybí: {len(chybi)}")
if chybi:
    print("Doplnit (pip install): " + " ".join(chybi))

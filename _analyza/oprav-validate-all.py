r"""Opraví drobné vady v sekci L `orchestra/tools/validate-all.mjs`.

Vznikly při psaní sekce: překlep v textu a zbytek po špatně zapsané závorce.
Skript je idempotentní a po zápisu ověří syntaxi (`node --check`).

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\oprav-validate-all.py
"""
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CIL = pathlib.Path("orchestra/tools/validate-all.mjs")
text = CIL.read_text(encoding="utf-8")
puvodni = text

# 1) překlep: „nesp uštěna" -> „nespuštěna"
text = text.replace("žádná brána nesp uštěna", "žádná brána nesp uštěna".replace("nesp u", "nespu"))

# 2) odstranit případný ladicí řádek, který tam nepatří
text = text.replace("\nconsole.log('HOTOVO');", "")

# 3) sjednotit konec bloku: přesně `  }\n}` na konci sekce L
text = text.replace(
    "    console.log('  ?    žádná brána nespuštěna — zkontroluj, že `_analyza\\\\` existuje');  }",
    "    console.log('  ?    žádná brána nespuštěna — zkontroluj, že `_analyza\\\\` existuje');\n  }",
)

if text != puvodni:
    CIL.write_text(text, encoding="utf-8", newline="")
    print("zapsány opravy")
else:
    print("beze změny")

# ── OVĚŘENÍ SYNTAXE (jinak by validátor přestal fungovat) ────────────────────
r = subprocess.run(["node", "--check", str(CIL)], capture_output=True, shell=True)
kod = r.returncode
chyba = (r.stderr or b"").decode("utf-8", "replace").strip()
print(f"node --check: exit={kod}" + (f"\n{chyba[:500]}" if chyba else " (syntaxe v pořádku)"))

# ── UKÁZAT VÝSLEDNOU SEKC I ─────────────────────────────────────────────────
radky = CIL.read_text(encoding="utf-8").splitlines()
start = next(i for i, l in enumerate(radky) if "L. BRÁNY A1/A2/A3" in l)
for i in range(start - 1, min(len(radky), start + 45)):
    print(f"{i+1:4} | {radky[i]}")

sys.exit(0 if kod == 0 else 1)

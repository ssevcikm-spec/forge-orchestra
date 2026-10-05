# -*- coding: utf-8 -*-
"""P16/G — přehození dvou řádků kroniky (MOJE chyba při zápisu, ne nález).

Při zápisu řádku **30** do přehledové tabulky kroniky jsem ho vložil **PŘED**
řádek **29**. Tabulka je chronologická, takže se musí prohodit. Skript:
  1. najde řádky začínající `| **30** |` a `| **29** |`,
  2. ověří, že každý je v souboru právě JEDNOU a že jsou HNED VEDLE SEBE,
  3. prohodí je **bajt na bajt** (jen pořadí řádků, žádný jiný znak),
  4. ověří, že se změnily právě dva řádky a nic jiného.

Nic jiného nemění (žádný jiný soubor, žádný jiný řádek).
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

K = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.split("\n")

i30 = [i for i, l in enumerate(radky) if l.startswith("| **30** |")]
i29 = [i for i, l in enumerate(radky) if l.startswith("| **29** |")]
print(f"  řádek 30 nalezen {len(i30)}×, řádek 29 {len(i29)}×")
assert len(i30) == 1 and len(i29) == 1, "každý řádek musí být právě jednou"
assert abs(i30[0] - i29[0]) == 1, "řádky nejsou vedle sebe — neprohazuji"
assert i30[0] < i29[0], "řádek 30 už je za 29 — není co prohazovat"

a, b = i30[0], i29[0]
radky[a], radky[b] = radky[b], radky[a]
novy = "\n".join(radky)
assert len(novy) == len(text), "délka souboru se změnila — to není přehození"
K.write_bytes(novy.encode("utf-8"))

# ověření: mění se PRÁVĚ dva řádky a nic jiného
po = K.read_bytes().decode("utf-8")
stare_r = text.split("\n")
nove_r = po.split("\n")
zmenene = [(i + 1, s[:60], n[:60]) for i, (s, n) in enumerate(zip(stare_r, nove_r))
           if s != n]
print(f"  změněných řádků: {len(zmenene)}")
for i, s, n in zmenene:
    print(f"      r.{i}: {s!r} → {n!r}")
assert len(zmenene) == 2, "změnit se měly právě dva řádky"
assert len(nove_r) == len(stare_r), "počet řádků se změnil"
print("  OK — prohozeno, nic jiného se nezměnilo")
sys.exit(0)

# -*- coding: utf-8 -*-
"""P16/B2 — IDEMPOTENCE plného běhu bran: kdo rozbíjí inventář?

NAMĚŘENO v Úkolu B: třetí běh všech 34 bran skončil se **3 nenulovými exity**
(`C2: mutace N1` = 2, `n1-over-inventar` = 2, `validate-all (CELEK)` = 1),
ačkoli uložený běh P15 měl všech 34 nulových. Otázka zní, **čí to je vina**:
kódu, prostředí, nebo TOHO, ŽE BĚH SÁM MĚNÍ STROM, jehož otisk inventář hlídá.

Postup (izolace po jedné bráně, návratové kódy se čtou v Pythonu, ne
z PowerShellu — `$LASTEXITCODE` v pipeline měří jinou věc):
  1. regeneruj inventář → `n1-over-inventar` (musí být 0),
  2. `n1` znovu (je stabilní?),
  3. `C2: mutace N1`,
  4. `n1` znovu — a pokud se rozešel, VYPIS, které soubory se změnily.
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
A = WS / "_analyza"


def spust(rel, *args):
    r = subprocess.run([sys.executable, str(A / rel), *args], capture_output=True,
                       cwd=str(WS))
    v = (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, v


def tisk(popis, kod, v, vzor=("VÝSLEDEK", "CHYBA", "otisk", "ZMĚŘENO", "→")):
    print(f"\n--- {popis}: exit={kod}")
    for l in v.splitlines():
        if any(z in l for z in vzor):
            print(f"      {l.strip()[:104]}")


print("=" * 78)
print("P16/B2 — idempotence: mění běh bran strom, který inventář hlídá?")
print("=" * 78)

kod, v = spust("hl-neanglicky-v-kodu.py", "--json", str(A / "_inventar.json"))
print(f"\n--- 0) regenerace inventáře: exit={kod}")
for l in v.splitlines()[-2:]:
    print(f"      {l.strip()[:100]}")

k1, v1 = spust("n1-over-inventar.py")
tisk("1) n1 HNED po regeneraci", k1, v1)

k2, v2 = spust("n1-over-inventar.py")
tisk("2) n1 podruhé (stabilita)", k2, v2)

k3, v3 = spust("c2-mutace.py")
tisk("3) C2: mutace N1", k3, v3)

k4, v4 = spust("n1-over-inventar.py")
tisk("4) n1 PO C2 (bez regenerace)", k4, v4)

# co se ve stromu změnilo (git status --porcelain) — jen se vypíše
r = subprocess.run([str(WS / "tools" / "git.cmd"), "-C", str(WS), "status",
                    "--porcelain"], capture_output=True, shell=True)
zmeny = [l for l in (r.stdout or b"").decode("utf-8", "replace").splitlines()
         if l.strip()]
print(f"\n--- 5) `git status --porcelain`: {len(zmeny)} řádků")
for l in zmeny[:14]:
    print(f"      {l}")

print("\n" + "=" * 78)
print("ZÁVĚR (měřený, ne odhadnutý):")
print(f"  n1 po regeneraci: exit={k1};  podruhé: exit={k2};  "
      f"po C2: exit={k4} (C2 exit={k3})")
if k1 == 0 and k2 == 0 and k4 != 0:
    print("  → NENÍ to vada kódu ani zastaralý inventář na začátku: **běh sám**")
    print("    (brána `C2: mutace N1`) zapíše do stromu, a tím zneplatní otisk,")
    print("    který hlídá `n1-over-inventar` i `validate-all`.")
    print("  → Důsledek: PLNÝ běh bran NEMŮŽE skončit se všemi nulovými exity,")
    print("    pokud některá brána zapisuje do sledovaného stromu.")
else:
    print("  → mechanika je jiná, než se čekalo — viz čísla výš")
print("=" * 78)

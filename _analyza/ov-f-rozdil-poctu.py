# P18 — proč NA32 vidí 176 a vlastní skener 162? (měřeno, bez překlepů)
import pathlib
from collections import Counter

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
REPA = [("orchestra", WS), ("hra", HRA)]

# Filtr NA32 (živý strom, mimo _archiv a .git)
NA32_SKIP = {".git"}
# Filtr mého skeneru B1 (přísnější)
B1_SKIP = {".git", "node_modules", "__pycache__", ".godot", ".tmp", ".wrangler",
           ".venv", "snapshot-20261002-183213", "snapshot-20261002-181237"}


def sb(skip, split_archiv=True):
    zive, arch = [], []
    for jm, koren in REPA:
        for p in sorted(koren.rglob("*.py")):
            if any(c in p.parts for c in skip):
                continue
            if "_archiv" in p.parts:
                if split_archiv:
                    arch.append(p)
                continue
            zive.append(p)
    return zive, arch


n_zive, n_arch = sb(NA32_SKIP)
b_zive, _ = sb(B1_SKIP)
print(f"filtr NA32  (skip={sorted(NA32_SKIP)}): živých {len(n_zive)}")
print(f"filtr B1    (skip={len(B1_SKIP)} položek): živých {len(b_zive)}")
print(f"_archiv: {len(n_arch)}")
print(f"ROZDÍL: {len(n_zive) - len(b_zive)}")
navic = [p for p in n_zive if p not in set(b_zive)]
print(f"\nsoubory, které NA32 počítá a B1 ne ({len(navic)}):")
for k, v in sorted(Counter(str(p.parent.relative_to(WS.parent)) for p in navic).items()):
    print(f"  {v:3}x  {k}")
print("\n=== kompilují se? ===")
ch = []
for p in navic:
    try:
        compile(p.read_text(encoding="utf-8-sig"), str(p), "exec")
    except SyntaxError as e:
        ch.append(f"{p}:{e.lineno} {e.msg}")
print(f"  nekompilovatelných mezi nimi: {len(ch)}")
for c in ch:
    print("   !!", c)

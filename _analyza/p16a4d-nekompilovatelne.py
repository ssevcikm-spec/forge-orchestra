# -*- coding: utf-8 -*-
"""P16/A4d — soubory, které NEJDOU ZKOMPILOVAT (měřeno `compile()`, ne okem).

Vzniklo to tak, že měřidlo A4 našlo v `_archiv` 3 soubory se `SyntaxError`
a **svůj výpis si zkrátilo na první tři** — takže živý strom vypadal čistý.
Tenhle skript vypisuje VŠECHNY nálezy a rozděluje je na živý strom a `_archiv`.

Nic nemění.
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"

zive, archiv, ostatni = [], [], []
souboru = 0
for koren in (WS, HRA):
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        souboru += 1
        t = p.read_text(encoding="utf-8", errors="replace")
        try:
            compile(t, str(p), "exec")
        except SyntaxError as e:
            zaznam = (str(p.relative_to(koren)), e.lineno, e.msg)
            if "_archiv" in p.parts:
                archiv.append(zaznam)
            elif p.name.startswith("p16"):
                ostatni.append(zaznam)
            else:
                zive.append(zaznam)

print("=" * 78)
print(f"P16/A4d — nekompilovatelné .py soubory ({souboru} proskenováno)")
print("=" * 78)
print(f"\n--- ŽIVÝ STROM (mimo `_archiv`): {len(zive)} -------------------------")
for f, ln, m in zive:
    print(f"  {f}:{ln}  {m}")
    p = (WS / f) if (WS / f).is_file() else (HRA / f)
    radky = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(0, ln - 2), min(len(radky), ln + 1)):
        print(f"        r.{i + 1}: {radky[i][:88]}")

print(f"\n--- `_archiv` (není živý kód): {len(archiv)} --------------------------")
for f, ln, m in archiv:
    print(f"  {f}:{ln}  {m}")

print(f"\n--- moje vlastní `p16*`: {len(ostatni)} ---------------------------------")
for f, ln, m in ostatni:
    print(f"  {f}:{ln}  {m}")

print("\n--- ověření: jde ten soubor VŮBEC SPUSTIT? ---------------------------")
for f, ln, m in zive:
    p = (WS / f) if (WS / f).is_file() else (HRA / f)
    r = subprocess.run([sys.executable, str(p), "--help"], capture_output=True,
                       cwd=str(WS), timeout=60)
    v = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    prvni = [l for l in v.splitlines() if l.strip()][:2]
    print(f"  {f}: exit={r.returncode}  {prvni}")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: živých nekompilovatelných souborů: {len(zive)}")
print("=" * 78)
sys.exit(1 if zive else 0)

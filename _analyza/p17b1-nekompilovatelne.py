# -*- coding: utf-8 -*-
"""P17/B1 — soubory, které NEJDOU ZKOMPILOVAT (`compile()`, ne okem).

PROČ ZNOVU: P16/A4d tohle naměřila (6 živých), ale (a) její výpis má vestavěné
krácení na první tři nálezy u `_archiv` — což je omyl **164** — a (b) je to
MĚŘIDLO P16, ne dnešní stav. Úkol B1 chce měření VLASTNÍ a VŠECHNY nálezy.

Rozdíl proti `p16a4d`: nic se nekrátí, kategorie se určují podle CESTY (ne podle
jména souboru — jinak by měřidla P16/P17 spadla do „živý strom" a brána by
tvrdila, že měří kód, který neměří), a vypisuje se i to, kolik souborů se
opravdu přečetlo (aby „0 nálezů" neznamenalo „0 přečtených").

Nic nemění. Použití: python _analyza/p17b1-nekompilovatelne.py
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
nectene = []

for koren in (WS, HRA):
    if not koren.is_dir():
        nectene.append((str(koren), "kořen neexistuje"))
        continue
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        souboru += 1
        try:
            t = p.read_text(encoding="utf-8")
        except Exception as e:                            # noqa: BLE001
            nectene.append((str(p), repr(e)))
            continue
        try:
            compile(t, str(p), "exec")
        except SyntaxError as e:
            # relativní cesta se bere VŮČI TOMU repu, ve kterém soubor je
            try:
                rel = str(p.relative_to(koren))
            except ValueError:
                rel = str(p)
            zaznam = (rel, e.lineno, e.msg)
            if "_archiv" in p.parts:
                archiv.append(zaznam)
            elif p.name.startswith(("p16", "p17")):
                ostatni.append(zaznam)
            else:
                zive.append(zaznam)

print("=" * 78)
print(f"P17/B1 — nekompilovatelné .py soubory ({souboru} přečteno)")
print("=" * 78)
print(f"kořeny: {WS}")
print(f"        {HRA}")

print(f"\n--- ŽIVÝ STROM (mimo `_archiv`, mimo měřidla p16*/p17*): {len(zive)} ---")
for f, ln, m in zive:
    print(f"  {f}:{ln}  {m}")
    p = (WS / f) if (WS / f).is_file() else (HRA / f)
    radky = p.read_text(encoding="utf-8", errors="replace").splitlines()
    for i in range(max(0, ln - 3), min(len(radky), ln + 1)):
        print(f"        r.{i + 1}: {radky[i][:88]}")

print(f"\n--- `_archiv` (není živý kód): {len(archiv)} --------------------------")
for f, ln, m in archiv:
    print(f"  {f}:{ln}  {m}")

print(f"\n--- měřidla p16*/p17* (doklady, ne živý kód): {len(ostatni)} ---------")
for f, ln, m in ostatni:
    print(f"  {f}:{ln}  {m}")

if nectene:
    print(f"\n--- NEPŘEČTENÉ ({len(nectene)}) — nezměřeno NENÍ nula -----------------")
    for f, d in nectene:
        print(f"  {f}: {d}")

print("\n--- ověření: jde ten soubor VŮBEC SPUSTIT? ---------------------------")
for f, ln, m in zive:
    p = (WS / f) if (WS / f).is_file() else (HRA / f)
    try:
        r = subprocess.run([sys.executable, str(p), "--help"], capture_output=True,
                           cwd=str(WS), timeout=60)
        v = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
        prvni = [l for l in v.splitlines() if l.strip()][:2]
        print(f"  {f}: exit={r.returncode}  {prvni}")
    except Exception as e:                                # noqa: BLE001
        print(f"  {f}: NEPODAŘILO SE SPUSTIT: {e!r}")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: přečteno {souboru} .py, živých nekompilovatelných {len(zive)}, "
      f"v _archiv {len(archiv)}, měřidel {len(ostatni)}, nepřečtených {len(nectene)}")
print("=" * 78)
sys.exit(1 if (zive or nectene) else 0)

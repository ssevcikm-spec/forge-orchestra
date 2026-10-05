# -*- coding: utf-8 -*-
"""N32 — BRÁNA: každý ŽIVÝ `.py` se dá ZKOMPILOVAT.

PROČ TO EXISTUJE (nález **H85**, naměřeno P16 5. 10. 2026 a potvrzeno P17):
šest živých souborů mělo `from __future__ import annotations` až pod preludiem
z P8b, takže **nešlo vůbec zkompilovat** — a nikdo si toho nevšiml, protože
žádná brána kompilovatelnost neměřila. Soubor, který nejde zkompilovat, se
nespustí; jeho vady (i ty runtime) tedy zůstávají **neviditelné**.

PROČ `compile()` A NE `ast.parse()`: `ast.parse()` bere jen SYNTAXI a
`from __future__` na špatném místě **PŘIJME** (je to omezení kompilátoru, ne
gramatiky). Naměřeno: `ast.parse` nad šesti vadnými soubory → **0 chyb**,
`compile()` nad týmiž → **6 chyb**. Brána nad `ast.parse` by tedy byla zelená
nad kódem, který se nikdy nespustí (past „brána, která nemá jak selhat").

CO SE VYLUČUJE A PROČ:
  * `_archiv/` — archiv se **nespouští** (je to doklad, ne živý kód). Vyloučené
    soubory se ale **VYKAZUJÍ** (aby vyloučení nebylo tiché) a jejich nálezy
    se vypíšou jako poznámka, ne jako vada.
  * `.git/` — interní objekty gitu nejsou zdrojový kód.

CO BRÁNA VYKAZUJE: počet zkontrolovaných souborů (jinak je `exit 0` ticho, ne
zelená — past S27). Nula zkontrolovaných souborů je CHYBA, ne úspěch.

Použití: python _analyza/n32-kompilovatelnost.py
Návratový kód: 0 = všechny živé soubory se kompilují, 1 = nález, 2 = neměřilo se.
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
REPA = [("orchestra", WS), ("hra", HRA)]

zive = []          # (repo, relativni cesta, radek, hlaska)
archiv = []        # tytez udaje, ale pro _archiv
nectene = []
vyloucene = 0
zkontrolovano = 0

for jmeno, koren in REPA:
    if not koren.is_dir():
        nectene.append((jmeno, str(koren), "kořen neexistuje"))
        continue
    for p in sorted(koren.rglob("*.py")):
        casti = set(p.parts)
        if ".git" in casti:
            continue
        if "_archiv" in casti:
            vyloucene += 1
            try:
                compile(p.read_text(encoding="utf-8"), str(p), "exec")
            except SyntaxError as e:
                archiv.append((jmeno, str(p.relative_to(koren)), e.lineno, e.msg))
            except Exception as e:                        # noqa: BLE001
                archiv.append((jmeno, str(p.relative_to(koren)), None, repr(e)))
            continue
        zkontrolovano += 1
        try:
            t = p.read_text(encoding="utf-8")
        except Exception as e:                            # noqa: BLE001
            nectene.append((jmeno, str(p.relative_to(koren)), repr(e)))
            continue
        try:
            compile(t, str(p), "exec")
        except SyntaxError as e:
            zive.append((jmeno, str(p.relative_to(koren)), e.lineno, e.msg))
        except ValueError as e:
            # napr. source code string cannot contain null bytes
            zive.append((jmeno, str(p.relative_to(koren)), None, repr(e)))

print("=" * 78)
print("N32 — každý živý `.py` se dá zkompilovat (`compile()`, ne `ast.parse`)")
print("=" * 78)
print(f"  kořeny: {WS}")
print(f"          {HRA}")

if zive:
    print(f"\n--- NEKOMPILOVATELNÉ ŽIVÉ SOUBORY: {len(zive)} -------------------")
    for jmeno, rel, ln, m in zive:
        print(f"  [{jmeno}] {rel}:{ln}  {m}")
else:
    print("\n--- nekompilovatelné živé soubory: 0 ------------------------------")

if nectene:
    print(f"\n--- NEPŘEČTENÉ ({len(nectene)}) — nezměřeno NENÍ nula --------------")
    for jmeno, rel, d in nectene:
        print(f"  [{jmeno}] {rel}: {d}")

if archiv:
    print(f"\n--- poznámka: `_archiv` (NENÍ živý kód, nespouští se): {len(archiv)} ---")
    for jmeno, rel, ln, m in archiv:
        print(f"  [{jmeno}] {rel}:{ln}  {m}")

print()
print(f"ZMĚŘENO: {zkontrolovano} souborů, {len(zive)} nekompilovatelných, "
      f"{vyloucene} vyloučeno (_archiv), {len(nectene)} nepřečteno")
print("=" * 78)

if zkontrolovano == 0:
    print("CHYBA: nezkontroloval se ANI JEDEN soubor — to není zelená.")
    sys.exit(2)
sys.exit(1 if (zive or nectene) else 0)

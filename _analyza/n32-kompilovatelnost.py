# -*- coding: utf-8 -*-
r"""N32 — BRÁNA: každý ŽIVÝ `.py` se dá ZKOMPILOVAT.

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
  * `snapshot-*/` — **zmrazené kopie dokumentace** (gitignored). NáleZ **H93**:
    do P19 (6. 10. 2026) se počítaly jako ŽIVÝ kód, takže vadný soubor ve
    zmrazeném dokladu by bránu **zčervenal** — a „opravit" by se dal jen tím,
    že se editne doklad, což pravidla zakazují. Dnes se vylučují a VYKAZUJÍ.
  * `*-scratch/` — **pracovní kopie** (worktree pro mutační brány, fixtury).
    Nález **H98**: naměřeno 19 souborů v `_analyza/a-ukol-scratch/**` +
    `_analyza/p19-scratch/**`, které se počítaly jako živé; **13 z nich je
    bajt na bajt shodných s živými soubory HRY**, 1 se liší jen konci řádků
    a 4 jsou fixtury bez protějšku. Kopie se nemá měřit jako živý kód —
    a kdyby v ní mutační brána nechala vadu, hlásila by ji jako vadu kódu.
  ⚠ Vyloučení NENÍ tiché: každá kategorie má VLASTNÍ ČÍTAČ v souhrnu a nálezy
  v ní se vypíšou jako poznámka (vzor, který měl `_archiv` od začátku).

CO BRÁNA VYKAZUJE: počet zkontrolovaných souborů (jinak je `exit 0` ticho, ne
zelená — past S27). Nula zkontrolovaných souborů je CHYBA, ne úspěch.
⚠ Souhrn MUSÍ začínat `ZMĚŘENO: <n> souborů, <m> nekompilovatelných` — bere ho
jako čítač `g3-brany.py` (vzor `ZMĚŘENO:\s*(\d+) souborů, (\d+) nekompilovatelných`).
Rozšíření smí být jen ZA tím.

Použití: python _analyza/n32-kompilovatelnost.py
Návratový kód: 0 = všechny živé soubory se kompilují, 1 = nález, 2 = neměřilo se.
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
REPA = [("orchestra", WS), ("hra", HRA)]

# Vylučované kategorie: (klíč, test na část cesty, popis do souhrnu).
# POŘADÍ ROZHODUJE — bere se PRVNÍ shoda, aby byl soubor počítaný právě jednou.
SNAP_RE = re.compile(r"^snapshot-\d")
SCRATCH_RE = re.compile(r".*-scratch$")
KATEGORIE = [
    ("_archiv", lambda c: c == "_archiv", "_archiv"),
    ("snapshot-*", lambda c: bool(SNAP_RE.search(c)), "snapshot-*"),
    ("*-scratch", lambda c: bool(SCRATCH_RE.search(c)), "*-scratch"),
]


def vyloucena_kategorie(p: pathlib.Path):
    """Vrátí klíč vylučované kategorie, nebo None (= živý kód)."""
    for klic, test, _ in KATEGORIE:
        if any(test(c) for c in p.parts):
            return klic
    return None


zive = []          # (repo, relativni cesta, radek, hlaska)
nectene = []
vyloucene_soubory = {klic: [] for klic, _, _ in KATEGORIE}   # klic -> nalezy
vyloucene_pocty = {klic: 0 for klic, _, _ in KATEGORIE}
zkontrolovano = 0

for jmeno, koren in REPA:
    if not koren.is_dir():
        nectene.append((jmeno, str(koren), "kořen neexistuje"))
        continue
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        klic = vyloucena_kategorie(p)
        if klic is not None:
            vyloucene_pocty[klic] += 1
            try:
                compile(p.read_text(encoding="utf-8"), str(p), "exec")
            except SyntaxError as e:
                vyloucene_soubory[klic].append(
                    (jmeno, str(p.relative_to(koren)), e.lineno, e.msg))
            except Exception as e:                        # noqa: BLE001
                vyloucene_soubory[klic].append(
                    (jmeno, str(p.relative_to(koren)), None, repr(e)))
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

if any(vyloucene_soubory.values()):
    print("\n--- poznámka: VYLOUČENÉ kategorie (NENÍ živý kód, nespouští se) ---")
    for klic, _, popis in KATEGORIE:
        nalezy = vyloucene_soubory[klic]
        if not nalezy:
            continue
        print(f"  [{popis}] nálezů: {len(nalezy)} (z {vyloucene_pocty[klic]} souborů)")
        for jmeno, rel, ln, m in nalezy:
            print(f"    [{jmeno}] {rel}:{ln}  {m}")

print()
print(f"ZMĚŘENO: {zkontrolovano} souborů, {len(zive)} nekompilovatelných, "
      + ", ".join(f"{vyloucene_pocty[klic]} vyloučeno ({popis})"
                  for klic, _, popis in KATEGORIE)
      + f", {len(nectene)} nepřečteno")
print("=" * 78)

if zkontrolovano == 0:
    print("CHYBA: nezkontroloval se ANI JEDEN soubor — to není zelená.")
    sys.exit(2)
sys.exit(1 if (zive or nectene) else 0)

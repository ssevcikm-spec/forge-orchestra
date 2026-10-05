#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""H79 — najdi VŠECHNY neplatné escape sekvence v `.py` obou repů.

PROČ TO EXISTUJE: `python -W error::SyntaxWarning` nad repem **skončí na PRVNÍ**
sekvenci (warning se změní na chybu), takže se z něj nedá zjistit, **kolik jich
je**. A skener `hl-neanglicky-v-kodu.py` je hlásil **bez jména souboru**
(`ast.parse(text)` bez `filename` → `<unknown>:21`), takže se nedaly dohledat.

Tenble nástroj:
  1. projde oba repy (a `_analyza/`, což je uvnitř repa orchestra),
  2. každý `.py` načte **jako text** a zavolá `ast.parse(text, filename=...)`
     se `warnings.catch_warnings(record=True)` → posbírá **všechny**
     `SyntaxWarning` i s **řádkem a sloupcem**,
  3. vypíše `soubor:řádek:sloupec: sekvence` a čítač.

⚠ NÁLEZ **H86** (P16, 5. 10. 2026; OPRAVENO P17): dřív se `_archiv` **vylučoval
POTICHU** — vypsal se jen jako položka v `skip`, ale jeho nálezy se nikde
neobjevily. Tvrzení „`_analyza/` má **0** neplatných escape sekvencí" tedy
**neřeklo svou mez**: platilo pro SKENOVANÝCH 158 souborů, ne pro `_analyza/`
jako celek (`_archiv` má 5 `SyntaxWarning`). **Číslo bez meze mate.**
Nově se `_archiv` **skenuje taky** a jeho nálezy se vypíšou jako **POZNÁMKA**
(archiv se **nespouští**, takže to není vada) — a **kanonický čítač nese mez**:
kolik živých souborů prošlo a kolik jich je v `_archiv`.

Návratový kód: 0 = 0 varování v ŽIVÉM stromě, 1 = nějaká tam jsou (vada
k opravě). Nálezy v `_archiv` `exit` NEMĚNÍ — jsou to poznámky, ne vady.

Použití:  python _analyza\h79-escape-sken.py
"""
from __future__ import annotations

import ast
import os
import pathlib
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
REPA = [("orchestra", WS), ("hra", WS.parent / "uo-shadows")]
# ⚠ `_archiv` tu ZÁMĚRNĚ NENÍ (H86): skenuje se taky, ale jeho nálezy jdou
# do jiné přihrádky. Kdyby tu zůstal, vyloučení by bylo zase tiché.
SKIP = {".git", "node_modules", "__pycache__"}

zive: list[tuple[str, int, str]] = []
archiv: list[tuple[str, int, str]] = []
souboru = 0
souboru_archiv = 0
chyb_parsovani = 0
chyb_parsovani_archiv = 0

for jmeno, koren in REPA:
    if not koren.is_dir():
        print(f"CHYBA: {jmeno} ({koren}) není adresář")
        chyb_parsovani += 1
        continue
    for p in sorted(koren.rglob("*.py")):
        if any(cast in SKIP for cast in p.parts):
            continue
        do_archivu = "_archiv" in p.parts
        if do_archivu:
            souboru_archiv += 1
        else:
            souboru += 1
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            try:
                text = p.read_text(encoding="utf-8-sig")
            except (UnicodeDecodeError, OSError):
                continue
        with warnings.catch_warnings(record=True) as zaznamy:
            warnings.simplefilter("always")
            try:
                ast.parse(text, filename=str(p))
            except SyntaxError as e:
                # ⚠ Nálezy v `_archiv` `exit` NEMĚNÍ (H86): archiv se nespouští,
                # takže nesoubor s vadnou syntaxí je POZNÁMKA, ne vada živého
                # stromu. Do opravy tohle rozlišení chybělo a jediný archívní
                # soubor (BOM `U+FEFF`) shazoval `exit` celého skenu.
                if do_archivu:
                    chyb_parsovani_archiv += 1
                else:
                    print(f"  CHYBA syntaxe: {p} — {e}")
                    chyb_parsovani += 1
                continue
        for z in zaznamy:
            if issubclass(z.category, SyntaxWarning):
                cil = archiv if do_archivu else zive
                cil.append((str(p.relative_to(koren.parent)), z.lineno or 0,
                            str(z.message)))

print("=" * 88)
print("H79 — NEPLATNÉ ESCAPE SEKVENCE (`SyntaxWarning` z `ast.parse`)")
print("=" * 88)
print(f"  prošlé ŽIVÉ soubory: {souboru}   (skip: {', '.join(sorted(SKIP))})")
print(f"  prošlé soubory v `_archiv` (NENÍ živý kód, nespouští se): {souboru_archiv}")
print()
if zive:
    print(f"--- ŽIVÝ STROM: {len(zive)} neplatných sekvencí ----------------------")
    for cesta, radek, text in zive:
        print(f"  {cesta}:{radek}   {text}")
    print()
else:
    print("--- ŽIVÝ STROM: 0 neplatných sekvencí ------------------------------")

if archiv:
    print(f"--- POZNÁMKA: `_archiv` má {len(archiv)} neplatných sekvencí "
          f"({souboru_archiv} souborů) ---")
    print("    Archiv se NESPOUŠTÍ, takže je to poznámka, ne vada (H86).")
    for cesta, radek, text in archiv:
        print(f"  {cesta}:{radek}   {text}")
    print()

if chyb_parsovani_archiv:
    print(f"  poznámka: {chyb_parsovani_archiv} souborů v `_archiv` se nedalo "
          f"zpracovat (archiv se nespouští)")

if chyb_parsovani:
    print(f"  + {chyb_parsovani} ŽIVÝCH souborů se nedalo zpracovat")

# JEDEN kanonický čítač pro `g3` (ten bere POSLEDNÍ výskyt vzoru). Nese MEZ
# (H86): kolik ŽIVÝCH souborů prošlo a kolik jich je v `_archiv`.
print(f"ZMĚŘENO: {len(zive)} neplatných escape sekvencí ve SKENOVANÝCH "
      f"{souboru} živých souborech (mimo `_archiv`: {souboru_archiv} souborů, "
      f"{len(archiv)} sekvencí)")

sys.exit(1 if (zive or chyb_parsovani) else 0)

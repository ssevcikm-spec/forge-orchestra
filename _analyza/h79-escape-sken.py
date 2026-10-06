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
# ⚠ P19 (6. 10. 2026), nález **H98**: stejná díra jako v `n32-kompilovatelnost.py`.
# `snapshot-*/` (zmrazené doklady) a `*-scratch/` (pracovní kopie pro mutace)
# se počítaly jako ŽIVÝ strom — takže vada v KOPII by zčervenala jako vada kódu.
# Vylučují se proto taky, ale KAŽDÁ kategorie má VLASTNÍ ČÍTAČ a vlastní
# poznámku: vyloučení nesmí být tiché (vzor, který má `_archiv` od H86).
import re  # noqa: E402  (drženo u seznamu, ať je vidět, k čemu patří)
SNAP_RE = re.compile(r"^snapshot-\d")
SCRATCH_RE = re.compile(r".*-scratch$")


def _kategorie(p: pathlib.Path):
    """`archiv` / `snapshot` / `scratch` / `zive` — podle CESTY, ne podle obsahu."""
    casti = p.parts
    if "_archiv" in casti:
        return "archiv"
    if any(SNAP_RE.search(c) for c in casti):
        return "snapshot"
    if any(SCRATCH_RE.search(c) for c in casti):
        return "scratch"
    return "zive"


zive: list[tuple[str, int, str]] = []
archiv: list[tuple[str, int, str]] = []
snapshot: list[tuple[str, int, str]] = []
scratch: list[tuple[str, int, str]] = []
souboru = 0
souboru_archiv = 0
souboru_snapshot = 0
souboru_scratch = 0
chyb_parsovani = 0
chyb_parsovani_archiv = 0
# ⚠ NÁLEZ H101 (P20, 6. 10. 2026): NEPŘEČTENÉ soubory se do P20 **TIŠE
# VYNECHÁVALY** (`continue`). Naměřeno: nečitelný `.py` v živém stromě →
# H79 `exit 0` **a soubor ve výstupu vůbec nebyl**, kdežto `n32-kompilovatelnost.py`
# tentýž soubor vykázal (`1 nepřečteno`) a skončil `exit 1`. Dvě brány tedy
# vydaly o TÉMŽ stromě RŮZNÝ verdikt — a to je horší než nepřesnost, protože
# „0 neplatných sekvencí“ se čte jako změřená nula, i když se část nezměřila.
# Nově se počítají a jsou POJMENOVANÉ (vzor, který má `_archiv` od H86).
nectene: list[tuple[str, str]] = []
# ⚠ A druhá polovina téhož nálezu: fallback `utf-8` → `utf-8-sig` **nemá co
# zachránit**. `utf-8-sig` je striktní NADMNOŽINA `utf-8` (BOM se v `utf-8`
# dekóduje na U+FEFF, nepadá), takže každý soubor, který přečte `utf-8-sig`,
# přečte i `utf-8`. Ověřeno na pěti vzorcích (`_analyza/p20-b2-necitelne.py`):
# ani jeden případ, kde by fallback pomohl. Je proto ODEBRANÝ — mrtvá větev
# vypadá jako pokrytí a nechytá nic (táž třída jako H94 v klasifikátoru `g3`).

for jmeno, koren in REPA:
    if not koren.is_dir():
        print(f"CHYBA: {jmeno} ({koren}) není adresář")
        chyb_parsovani += 1
        continue
    for p in sorted(koren.rglob("*.py")):
        if any(cast in SKIP for cast in p.parts):
            continue
        kat = _kategorie(p)
        if kat == "archiv":
            souboru_archiv += 1
        elif kat == "snapshot":
            souboru_snapshot += 1
        elif kat == "scratch":
            souboru_scratch += 1
        else:
            souboru += 1
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError) as e:
            # ⚠ H101 (P20): dřív tu byl `continue` a fallback na `utf-8-sig`.
            # Fallback je pryč (nemá co zachránit — viz komentář u `nectene`)
            # a nečitelný soubor se VYKÁŽE. `exit` se nemění: je to DOKLAD,
            # ne živý kód k opravě — ale tichý být nesmí.
            nectene.append((kat, f"{p} — {type(e).__name__}: {e}"))
            continue
        with warnings.catch_warnings(record=True) as zaznamy:
            warnings.simplefilter("always")
            try:
                ast.parse(text, filename=str(p))
            except SyntaxError as e:
                # ⚠ Nálezy MIMO ŽIVÝ strom `exit` NEMĚNÍ (H86 + H98): archiv
                # ani zmrazené/pracovní kopie se nespouští, takže soubor
                # s vadnou syntaxí je POZNÁMKA, ne vada živého kódu.
                if kat == "archiv":
                    chyb_parsovani_archiv += 1
                elif kat != "zive":
                    print(f"  poznámka ({kat}, nespouští se): {p} — {e}")
                else:
                    print(f"  CHYBA syntaxe: {p} — {e}")
                    chyb_parsovani += 1
                continue
        for z in zaznamy:
            if issubclass(z.category, SyntaxWarning):
                cil = {"archiv": archiv, "snapshot": snapshot,
                       "scratch": scratch, "zive": zive}[kat]
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

# ⚠ H98: i zmrazené a pracovní kopie se VYKAZUJÍ, jen nemění verdikt.
for nazev, obsah, pocet in (("snapshot-*", snapshot, souboru_snapshot),
                            ("*-scratch", scratch, souboru_scratch)):
    if obsah:
        print(f"--- POZNÁMKA: `{nazev}` má {len(obsah)} neplatných sekvencí "
              f"({pocet} souborů) ---")
        print("    Je to KOPIE (doklad / pracovní strom), nespouští se → "
              "poznámka, ne vada (H98).")
        for cesta, radek, text in obsah:
            print(f"  {cesta}:{radek}   {text}")
        print()

if chyb_parsovani_archiv:
    print(f"  poznámka: {chyb_parsovani_archiv} souborů v `_archiv` se nedalo "
          f"zpracovat (archiv se nespouští)")

if chyb_parsovani:
    print(f"  + {chyb_parsovani} ŽIVÝCH souborů se nedalo zpracovat")

# ⚠ H101 (P20): NEČITELNÉ soubory se VYPISUJÍ — do P20 zmizely bez slova a brána
# o nich tvrdila „0 neplatných sekvencí“. Vypisují se VŠECHNY kategorie, protože
# i nečitelný doklad je něco, o čem se má vědět.
if nectene:
    print()
    print(f"--- POZNÁMKA: {len(nectene)} souborů se NEDALO PŘEČÍST "
          f"(nejsou v číslech výš!) ---")
    for kat, popis in nectene:
        print(f"  ({kat}) {popis}")
    print("    Nezměřeno NENÍ nula: soubor se nenačetl, takže o jeho escape")
    print("    sekvencích tahle brána NETVRDÍ NIC. Když je v živém stromě,")
    print("    je to vada k opravě — a uvidí ji `n32-kompilovatelnost.py`.")

# JEDEN kanonický čítač pro `g3` (ten bere POSLEDNÍ výskyt vzoru). Nese MEZ
# (H86 + H98 + H101): kolik ŽIVÝCH souborů prošlo, kolik jich je v každé
# vyloučené kategorii a kolik se jich NEDALO PŘEČÍST. Začátek řádku se NESMÍ
# změnit — `g3` ho čte vzorem `ZMĚŘENO:\s*(\d+) neplatných`.
# ⚠ POLE `nečitelných` JE ZÁMĚRNĚ NA KONCI: `p19-b2-kontroly-h79.py` (a starší
# doklady) matchují tentýž řádek vzorem, který končí na `*-scratch`; vložení
# doprostřed by je rozbilo a doklad by přestal měřit.
print(f"ZMĚŘENO: {len(zive)} neplatných escape sekvencí ve SKENOVANÝCH "
      f"{souboru} živých souborech (mimo živý strom: `_archiv` {souboru_archiv} "
      f"souborů/{len(archiv)} sekvencí, `snapshot-*` {souboru_snapshot}/"
      f"{len(snapshot)}, `*-scratch` {souboru_scratch}/{len(scratch)}, "
      f"{len(nectene)} nečitelných)")

sys.exit(1 if (zive or chyb_parsovani) else 0)

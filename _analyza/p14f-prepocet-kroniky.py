#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 — PŘEPOČET souhrnného řádku `celkem` v KRONIZE §3 (měřením, ne odhadem).

PROČ: `KRONIKA-PROJEKTU.md` §3 má podrobnou tabulku po blocích a pod ní řádek
`celkem`. Ten se ale **neaktualizoval** s každým novým blokem (naposledy zůstal
na `16 bloků, 24 sessions / 129 / 107 = 83 % / 34`, ačkoli tabulka má víc řádků).
Součet se proto **spočítá z řádků tabulky** a vedle se vypíše, co tvrdí řádek
`celkem` — aby se dalo rozhodnout, co je stav a co záznam (A2).

Použití: python p14f-prepocet-kroniky.py [KRONIKA.md]
"""
from __future__ import annotations

import os
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

K = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else \
    pathlib.Path(os.environ.get("FORGE_WS")
                 or pathlib.Path(__file__).resolve().parents[1]) / "KRONIKA-PROJEKTU.md"
text = K.read_text(encoding="utf-8")

# tabulka po blocích je mezi nadpisem „Podrobná tabulka po blocích" a `celkem`
i = text.find("Podrobná tabulka po blocích")
j = text.find("| **celkem**", i)
if i < 0 or j < 0:
    print("CHYBA: nenašel jsem tabulku po blocích nebo řádek `celkem`")
    sys.exit(1)
blok = text[i:j]

VZOR = re.compile(
    r"^\|\s*\*\*(?P<blok>[^*|]+)\*\*\s*\|\s*(?P<popis>[^|]*)\|\s*"
    r"\*\*(?P<omylu>\d+)\*\*\s*\|\s*\*\*(?P<meridla>\d+)\*\*\s*\|\s*"
    # ⚠ Sloupec „vypadalo jako nález o CIZÍM kódu" má u bloku `1–13` POMLČKU,
    # ne číslo (`| — |`). První verze vzoru to vyhodila → součet dal **130
    # a 18 bloků** místo 143 a 19 (a vypadalo to jako nález o datech).
    r"(?:\*\*(?P<cizi>\d+)\*\*|(?P<pomlcka>—))\s*\|")
radky = []
for radek in blok.splitlines():
    m = VZOR.match(radek)
    if m:
        r = {"blok": m.group("blok").strip(), "popis": m.group("popis").strip(),
             "omylu": int(m.group("omylu")), "meridla": int(m.group("meridla")),
             "cizi": int(m.group("cizi")) if m.group("cizi") else 0}
        radky.append(r)

print("=" * 88)
print("PŘEPOČET SOUHRNU V KRONIZE §3 (z řádků tabulky, ne odhadem)")
print("=" * 88)
print(f"  soubor: {K}")
print(f"  řádků s blokem omylů: {len(radky)}")
print()
print(f"  {'blok':<8} {'omylů':>6} {'měřidla':>8} {'cizí kód':>9}")
for r in radky:
    print(f"  {r['blok']:<8} {r['omylu']:>6} {r['meridla']:>8} {r['cizi']:>9}")
sum_o = sum(r["omylu"] for r in radky)
sum_m = sum(r["meridla"] for r in radky)
sum_c = sum(r["cizi"] for r in radky)
print(f"  {'SOUČET':<8} {sum_o:>6} {sum_m:>8} {sum_c:>9}")

# kolik je sessions v tabulce §1
v1 = text[text.find("## 1. Přehledová tabulka"):text.find("## 2.")]
sessions = [r for r in v1.splitlines() if re.match(r"^\|\s*\*\*\d+\*\*\s*\|", r)]
print()
print(f"  sessions v tabulce §1: {len(sessions)}")
print(f"  podíl vad měřidla: {sum_m} / {sum_o} = {100 * sum_m / sum_o:.1f} %")

radek_celkem = text[j:text.find("\n", j)]
print()
print(f"  CO TVRDÍ ŘÁDEK `celkem` DNES:")
print(f"      {radek_celkem}")
print()
print("  → správně (měřením):")
print(f"      | **celkem** | **{len(radky)} bloků, {len(sessions)} sessions** | "
      f"**{sum_o}** | **{sum_m} = {round(100 * sum_m / sum_o)} %** | **{sum_c}** |")

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Ověření tvrzení o `component()` registru v herním repu (Python walk).

PROČ: `grep` tool i `Select-String` umí tiše přeskočit soubory (skill
`dsh-prostredi` §1). Tady jde o tvrzení „nikdo v repu neposkytuje
`component(id)`" — to se musí měřit walkem, ne grepem.

Měří:
  1. které soubory v `scripts/` DEKLARUJÍ `func component(`,
  2. které soubory v `scripts/` ji VOLAJÍ,
  3. jestli `game.gd` (kostra) registr má,
  4. co říká `.forge/roadmap.json` o stavu `engine.shell`.
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
HRA = KOREN / "games" / "uo-shadows"

DEKLARACE = re.compile(r"^\s*func\s+component\s*\(", re.M)
VOLANI = re.compile(r"\bcomponent\s*\(")

print("=" * 78)
print("KDO V HERNÍM REPU POSKYTUJE A KDO VOLÁ `component(id)`")
print("=" * 78)

poskytuji = []
volaji = []
skripty = sorted((HRA / "scripts").rglob("*.gd"))
for cesta in skripty:
    text = cesta.read_text(encoding="utf-8")
    # komentáře pryč — jinak by komentář popisující vzor vypadal jako vzor
    bez_kom = re.sub(r"#[^\n]*", "", text)
    if DEKLARACE.search(bez_kom):
        poskytuji.append(cesta.name)
    # rozliš deklaraci od volání: deklarace má `func` před jménem
    for m in VOLANI.finditer(bez_kom):
        pred = bez_kom[max(0, m.start() - 20):m.start()]
        if "func" in pred:
            continue
        volaji.append(cesta.name)
        break

print("\n-- soubory v scripts/, které DEKLARUJÍ `func component(` --")
print("   %s" % (poskytuji if poskytuji else "ŽÁDNÝ"))

print("\n-- soubory v scripts/, které `component(` VOLAJÍ --")
print("   %s" % (volaji if volaji else "ŽÁDNÝ"))

print("\n-- game.gd (kostra) --")
game = (HRA / "scripts" / "game.gd").read_text(encoding="utf-8")
print("   deklaruje `func component(`: %s" % bool(DEKLARACE.search(re.sub(r"#[^\n]*", "", game))))

print("\n-- .forge/roadmap.json: stav engine.shell --")
road = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
for g in road["grains"]:
    if g["id"] == "engine.shell":
        print("   id=%s done=%s owns=%s" % (g["id"], g.get("done"), g.get("owns")))

print("\n-- testy: kdo používá TestKostra (atrapa registru) --")
testy = (HRA / "tests" / "run_tests.gd").read_text(encoding="utf-8")
print("   výskytů 'TestKostra': %d" % testy.count("TestKostra"))
print("   výskytů 'component(':  %d" % len(re.findall(r"component\(", re.sub(r"#[^\n]*", "", testy))))

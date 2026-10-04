#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Kontrola JEDNOZNAČNOSTI kotvy před mutací (past omylu 76).

Proč samostatný soubor: kotva, která je v souboru víckrát, se `replace(...,1)`
trefí jinam, než chceš — a vypadá to jako "brána je slepá". Tohle je měřidlo,
které to řekne PŘED mutací.

Použití:  python _analyza\\v1-kotvy.py
Návrat:   0 = všechny kotvy jednoznačné | 1 = některá není
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
TESTY = KOREN / "games" / "uo-shadows" / "tests" / "run_tests.gd"

# Kotvy, které chci v testu nahrazovat / ověřovat.
#   (popis, kotva, očekávaný počet v DNEŠNÍM souboru)
#
# ⚠ PAST, DO KTERÉ JSEM SPADL: kotva, která v dnešním souboru být NEMÁ
# („> 0" z původní verze), není vada souboru — je to jiný STAV. Kdyby ji
# měřidlo hlásilo jako vadu, vyrobí falešný poplach na správném souboru
# (tatáž třída jako omyly 72 a 80). Proto má každá kotva SVŮJ očekávaný počet.
KOTVY = [
    ("rovnost 13 (lék H12)", 'int(pres_hodnota.get("damage", -1)) == 13', 1),
    ("cely _check rovnost 13", 'pres_hodnota != null and int(pres_hodnota.get("damage", -1)) == 13', 1),
    ("citas vetev_hodnota", "atr_h.vetev_hodnota >= 1", 1),
    ("atrapa TestAtributyHodnota", "class TestAtributyHodnota:", 1),
    ("atrapa TestSkillyHodnota", "class TestSkillyHodnota:", 1),
    ("atrapa TestAtributy (stara)", "class TestAtributy:", 1),
    # Tyhle v DNEŠNÍM souboru být NESMÍ — jsou to kotvy PŮVODNÍ verze
    # (v `c40bdd5`). Očekávaný počet 0, a to je v pořádku.
    ("PUVODNI `> 0` (nesmi tu byt)", 'int(pres_hodnota.get("damage", 0)) > 0', 0),
    ("PUVODNI atrapa TestAtributyHodnota", "class TestAtributyHodnota", 1),
]

print("=" * 78)
print("JEDNOZNAČNOST KOTEV v %s" % TESTY.relative_to(KOREN))
print("=" * 78)

text = TESTY.read_text(encoding="utf-8")
print("  soubor: %d B, %d řádků (splitlines)" % (len(text.encode("utf-8")), len(text.splitlines())))
print()

vad = 0
for popis, kotva, ocekavano in KOTVY:
    n = text.count(kotva)
    if n == ocekavano:
        stav = "OK "
    elif n == 0 and ocekavano > 0:
        stav = "CHYBI"
    else:
        stav = "JINAK"
    if n != ocekavano:
        vad += 1
    print("  %-6s očekáváno %dx, naměřeno %dx  %-32s %r"
          % (stav, ocekavano, n, popis, kotva[:52]))

print()
if vad:
    print("NALEZENO %d KOTEV, KTERE NEJSOU JEDNOZNACNE" % vad)
    sys.exit(1)
print("VŠECHNY KOTVY JEDNOZNAČNÉ — mutace se trefí tam, kam má.")
sys.exit(0)

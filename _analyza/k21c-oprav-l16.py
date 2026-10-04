# -*- coding: utf-8 -*-
r"""Posledni oprava kroniky: L16 mela doslovnou ukazku rozbiteho znaku."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(__file__).resolve().parent.parent / "KRONIKA-PROJEKTU.md"
s = P.read_text(encoding="utf-8")

# Znak se sklada z kodoveho bodu: doslovna ukazka rozbiteho kódování je
# v tomhle workspace ZAKAZANA (AGENTS.md) a `g1-diakritika-novych.py` ji
# hlasi jako vadu souboru.
ZNAK = chr(0xC3)
STARY = ("a půlparser `bez_komentaru()` selhal na **jednosloupcových uvozovkách** (`\""
         + ZNAK + "\"` je literál).")
NOVY = ("a půlparser `bez_komentaru()` selhal na **jednoznakových uvozovkách** "
        "(uvozovka u jednoho znaku je sama literál, takže se párovala špatně).")

assert s.count(STARY) == 1, "vzor nenalezen (%dx)" % s.count(STARY)
s2 = s.replace(STARY, NOVY, 1)
assert s2 != s, "NAHRADA NEPROBEHLA"
R = (chr(0xC3), chr(0xC4), chr(0xC5))
zbyle = [i + 1 for i, L in enumerate(s2.splitlines()) if any(z in L for z in R)]
assert not zbyle, "v kronice zustaly rozbite znaky na radcich %s" % zbyle
P.write_bytes(s2.encode("utf-8"))
print("OK: L16 popsan slovem, v kronice 0 rozbitych znaku")

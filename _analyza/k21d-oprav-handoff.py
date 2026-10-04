# -*- coding: utf-8 -*-
r"""Opravi dva radky omylu 74/75 v HANDOFFu — doslovna ukazka rozbiteho kódování
je tam z prvniho vlozeni; nahradi se popisem SLOVEM (zakazuje to AGENTS.md)."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

H = pathlib.Path(__file__).resolve().parent.parent / "HANDOFF.md"
h = H.read_text(encoding="utf-8")
R = (chr(0xC3), chr(0xC4), chr(0xC5))


def oprav(radek: int, popis: str) -> None:
    """V radku c. `radek` (1-based) nahradi KAZDY rozbity znak popisem."""
    global h
    radky = h.split("\n")
    puvodni = radky[radek - 1]
    assert any(z in puvodni for z in R), \
        "%s: na radku %d uz zadny rozbity znak neni" % (popis, radek)
    novy = puvodni
    for z in R:
        novy = novy.replace(z, "")
    assert not any(z in novy for z in R), "%s: rozbite znaky zustaly" % popis
    radky[radek - 1] = novy
    h = "\n".join(radky)
    print("OK  %s: radek %d ocisten (%d -> %d znaku)" % (popis, radek, len(puvodni), len(novy)))


# Radek 2423 = omyl 74 (doslovna ukazka uvozovek), 2424 = omyl 75 (mojibake).
oprav(2423, "omyl 74")
oprav(2424, "omyl 75")

# Po ocisteni zustane v obou radcich nedokoncena veta — dokonci se popisem.
DOPLNENI = [
    ("má `\"` jako **jednoznakový literál**, takže se uvozovky spárovaly špatně a `` zůstalo „v kódu\"",
     "uvozovka u **jednoznakového literálu** je sama literál, takže se párovala špatně "
     "a hledaný znak zůstal „v kódu\""),
    ("`Get-Content` vypsal `` a vypadalo to jako vada souboru | **Soubor je UTF-8 a v pořádku** "
     "(`read_bytes().decode('utf-8')` projde, `` v něm není ani jednou).",
     "`Get-Content` vypsal české slovo jako posloupnost rozbitých znaků a vypadalo to jako vada "
     "souboru | **Soubor je UTF-8 a v pořádku** (`read_bytes().decode('utf-8')` projde, rozbitý "
     "znak v něm není ani jednou). *(Doslovnou ukázku sem záměrně nepíšu — zakazuje to `AGENTS.md` "
     "a `g1-diakritika-novych.py` to hlásí jako vadu souboru.)*"),
]
for stary, novy in DOPLNENI:
    if stary in h:
        h = h.replace(stary, novy, 1)
        print("OK  dokoncena veta: %r..." % novy[:50])
    else:
        print("--  vzor k dokonceni nenalezen (uz je hotovo)")

zbyle = [i + 1 for i, L in enumerate(h.splitlines()) if any(z in L for z in R)]
assert not zbyle, "v HANDOFFu zustaly rozbite znaky na radcich %s" % zbyle
assert "Jednoznakový" not in h and "jednoznakového literálu" in h, "popis omylu 74 chybi"
H.write_bytes(h.encode("utf-8"))
print("OK  HANDOFF.md: 0 rozbitych znaku, oba omyly popsany slovem")

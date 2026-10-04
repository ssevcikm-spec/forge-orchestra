# -*- coding: utf-8 -*-
r"""Dokonci radek omylu 75 v HANDOFFu — po ocisteni zustaly fragmenty."""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

H = pathlib.Path(__file__).resolve().parent.parent / "HANDOFF.md"
h = H.read_text(encoding="utf-8")
R = (chr(0xC3), chr(0xC4), chr(0xC5))
assert not any(z in h for z in R), "v HANDOFFu jeste jsou rozbite znaky"

FRAGMENTY = [
    # (co tam zbylo, cim to nahradit)
    ("`Get-Content` vypsal `MUTAŒN TEST` a vypadalo to jako vada souboru",
     "`Get-Content` vypsal české slovo jako posloupnost rozbitých znaků a vypadalo to jako vada souboru"),
    ("(`read_bytes().decode('utf-8')` projde, `` v něm není ani jednou)",
     "(`read_bytes().decode('utf-8')` projde, rozbitý znak v něm není ani jednou)"),
    ("a `MUTAŒN TEST` zůstalo",
     "a české slovo se rozsypalo"),
]
zmen = 0
for stary, novy in FRAGMENTY:
    if stary in h:
        h = h.replace(stary, novy, 1)
        zmen += 1
        print("OK  %r -> %r" % (stary[:45], novy[:45]))
print("   zmen: %d" % zmen)

# Doslovna ukazka se dopise SLOVEM (a je to pouceni, ne jen kosmetika).
DOPLNIT_ZA = "(`read_bytes().decode('utf-8')` projde, rozbitý znak v něm není ani jednou)"
DOPLNIT = (DOPLNIT_ZA + ". *(Doslovnou ukázku sem záměrně nepíšu — zakazuje to `AGENTS.md` "
           "a `g1-diakritika-novych.py` to hlásí jako vadu souboru.)*")
if DOPLNIT_ZA in h and "Doslovnou ukázku sem záměrně nepíšu" not in h:
    h = h.replace(DOPLNIT_ZA, DOPLNIT, 1)
    print("OK  doplneno pouceni o doslovne ukazce")

assert "MUTA" not in h or "MUTA" not in h.split("| **75** |")[1][:400], "fragment MUTA zustal"
zbyle = [i + 1 for i, L in enumerate(h.splitlines()) if any(z in L for z in R)]
assert not zbyle, "rozbite znaky na radcich %s" % zbyle
H.write_bytes(h.encode("utf-8"))
print()
print("--- radek omylu 75 ---")
for L in h.splitlines():
    if L.startswith("| **75** |"):
        print(L[:420])

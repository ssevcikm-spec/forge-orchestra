# -*- coding: utf-8 -*-
"""SONDA: proč `HANDOFF.md:1201` (kotva „21 granul") NENÍ v ZÁZNAMECH?

Diagnóza podle `overovani` §10.5: **vypiš, KTERÉ pravidlo rozhodlo a jaké
okno použilo** — nehádej, která vrstva je špatně.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KOTVA = "- **D1 má 16 řádků na 21 granul**"

text = (WS / "HANDOFF.md").read_text(encoding="utf-8")
radky = text.splitlines()

DATUM = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")
ZNAKY = ("provedeno", "ověření", "ověřeno", "záznam",
         "měření", "měřeno", "kontrola", "závěr", "souhrn")
ZACATEK = re.compile(r"^\s*(?:[-*+]\s|\d+\.\s|\||#)")

# najdi výskyt kotvy
i = text.find(KOTVA)
print("kotva nalezena na znaku: %d" % i)
idx = text[:i].count("\n")
print("řádek (0-based %d, 1-based %d):" % (idx, idx + 1))
print("   %s" % radky[idx][:110])

# okno jako v nástroji
if radky[idx].lstrip().startswith("|"):
    okno = radky[idx]
else:
    a = idx
    while a > 0 and radky[a - 1].strip() and not ZACATEK.match(radky[a - 1]):
        a -= 1
    if a > 0 and radky[a - 1].strip() and ZACATEK.match(radky[a - 1]):
        a -= 1
    b = idx
    while (b + 1 < len(radky) and radky[b + 1].strip()
           and not ZACATEK.match(radky[b + 1])):
        b += 1
    okno = "\n".join(radky[a:b + 1])

print("\nOKNO (ř. %d–%d, %d znaků):" % (a + 1, b + 1, len(okno)))
for radek in okno.splitlines():
    print("   | %s" % radek[:104])

print("\nROZHODNUTÍ:")
print("  datum v okně      : %s" % bool(DATUM.search(okno)))
# nadpis oddilu
nadpis = ""
for k in range(min(idx, len(radky) - 1), -1, -1):
    if radky[k].startswith("## "):
        nadpis = radky[k]
        break
print("  nadpis oddílu     : %s" % nadpis[:86])
print("  nadpis.lower()    : %s" % nadpis.lower()[:86])
print("  znaky v nadpisu   : %s" % [z for z in ZNAKY if z in nadpis.lower()])
print("  datum v nadpisu   : %s" % bool(DATUM.search(nadpis)))

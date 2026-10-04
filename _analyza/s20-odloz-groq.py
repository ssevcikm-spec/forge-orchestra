# -*- coding: utf-8 -*-
r"""Zapíše do `PLAN-DALSI-KROK.md` rozhodnutí uživatele:

    ODLOŽENO — Groq limit 8k tokenů —
    dynamicky assignovat/redukovat balíček pro omezené modely

CO SE MĚNÍ: §3.1 bylo „ROZHODNOUT o Groqu (čeká na uživatele)". Uživatel
rozhodl **ODLOŽIT** a dal k tomu i **směr řešení** (dynamická úprava balíčku
podle modelu). Sekce se proto přepisuje na `ODLOŽENO` a **zůstává v plánu** —
s podmínkou, co ji má znovu otevřít.

Použití:  python _analyza\s20-odloz-groq.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PLAN = WS / "PLAN-DALSI-KROK.md"
ZAPIS = "--zapis" in sys.argv

NOVE = (WS / "_analyza" / "s20-plan-31.md").read_text(encoding="utf-8").strip()
assert NOVE.startswith("### 3.1"), "nová §3.1 nemá správný nadpis"

text = PLAN.read_text(encoding="utf-8")

# Vymezí se CELÁ sekce 3.1 (od jejího nadpisu po nadpis 3.2) a nahradí se.
OD = "### 3.1 ROZHODNOUT o Groqu"
DO = "### 3.2 COMMIT a PUSH obou repů"
i = text.find(OD)
j = text.find(DO)
assert i > 0 and j > i, "sekci 3.1 nejde vymezit (od=%d, do=%d)" % (i, j)

stara = text[i:j]
assert "3.1.1" in stara, "vymezená sekce nevypadá jako 3.1"
assert len(stara) > 500, "vymezená sekce je podezřele krátká"

novy = text[:i] + NOVE + "\n\n" + text[j:]
assert novy != text, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
assert novy.count("### 3.1 ") == 1, "§3.1 není právě 1× (pozor: '3.1b' se počítá zvlášť)"
assert "ODLOŽENO" in novy, "slovo ODLOŽENO se nevepsalo"
assert novy.startswith(text[:4096]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"

print("=" * 78)
print("PLAN-DALSI-KROK.md — §3.1 se přepisuje na ODLOŽENO")
print("=" * 78)
print("  stará sekce: %d znaků" % len(stara))
print("  nová sekce:  %d znaků" % len(NOVE))
print("  PŘED: %d B   PO: %d B"
      % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))

if ZAPIS:
    PLAN.write_bytes(novy.encode("utf-8"))
    print("  ZAPSÁNO.")
else:
    print("  (dry-run — spusť s --zapis)")

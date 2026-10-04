# -*- coding: utf-8 -*-
"""Kontrola: je NEXT-SESSION-INSTRUKCE.md opravdu UTF-8, nebo se rozbil zápis?

POZOR: PowerShell v tomhle okně vypisuje české znaky jako mojibake (cp1252),
takže `Get-Content` NENÍ důkaz. Rozhoduje **bajt** (AGENTS.md).
"""
import sys
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

p = "NEXT-SESSION-INSTRUKCE.md"
b = open(p, "rb").read()
print("soubor: %s (%d B)" % (p, len(b)))
print("prvni 3 bajty: %s" % list(b[:3]))

# 1) dá se dekódovat jako UTF-8?
try:
    t = b.decode("utf-8")
    print("UTF-8 dekodovani: OK (%d znaku)" % len(t))
except UnicodeDecodeError as e:
    print("UTF-8 dekodovani: CHYBA %s" % e)
    sys.exit(1)

# 2) obsahuje náhradní znak? (tím se projeví dvojí kódování)
print("nahradnich znaku U+FFFD: %d" % t.count("\ufffd"))

# 3) obsahuje trojici znaků dvojitého kódování UTF-8 -> Windows-1250?
ROZBITE = [chr(0x00C3), chr(0x00C4), chr(0x00C5)]
nalezene = [(z, t.count(z)) for z in ROZBITE if z in t]
print("znaky dvojiteho kodovani: %s" % (nalezene if nalezene else "zadne"))

# 4) první řádek — jak vypadá opravdu
print()
print("prvni radek: %r" % t.splitlines()[0])
print("druhy radek:  %r" % t.splitlines()[1])

# 5) sonda na konkrétní slova, která MUSÍ být správně
for slovo in ("ZADÁNÍ PRO AKČNÍ SESSION", "Zkontrolováno při", "ověření",
              "změřen", "nálezů", "§8g", "čísla"):
    print("  %-28s %s" % (slovo, "JE" if slovo in t else "NENÍ"))

print()
print("VERDIKT: %s" % ("SOUBOR JE V PORADKU (mojibake byl jen ve vypisu PowerShellu)"
                       if not nalezene and t.count("\ufffd") == 0
                       else "SOUBOR JE ROZBIT"))

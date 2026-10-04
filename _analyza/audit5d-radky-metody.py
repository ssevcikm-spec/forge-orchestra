# -*- coding: utf-8 -*-
"""Proč „počet řádků skillů" vyšel třikrát jinak (3 392 / 3 678 / 3 832).

`AGENTS.md` varuje, že **různé čítače nesou stejné jméno**. Tohle je přesně
ten případ a je lepší ho změřit než hádat: tři metody na TÉŽE soubory.
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKILLS = pathlib.Path.home() / ".dsh" / "skills"
files = sorted(SKILLS.glob("*/SKILL.md"))

print("=" * 88)
print("TŘI METODY NA TOTÉŽ: kolik řádků mají skilly")
print("=" * 88)
print()
print("  %-22s %8s %8s %8s %8s %6s" % ("skill", "splitlines", "\\n", "\\r\\n", "CR", "BOM"))
print("  " + "-" * 70)
t1 = t2 = t3 = 0
for f in files:
    b = f.read_bytes()
    s = b.decode("utf-8")
    a = len(s.splitlines())
    n = s.count("\n")
    r = b.count(b"\r\n")
    cr = b.count(b"\r")
    bom = "ANO" if b.startswith(b"\xef\xbb\xbf") else "ne"
    t1 += a
    t2 += n
    t3 += r
    print("  %-22s %8d %8d %8d %8d %6s" % (f.parent.name, a, n, r, cr, bom))
print("  " + "-" * 70)
print("  %-22s %8d %8d %8d" % ("SOUČET", t1, t2, t3))
print()
print("  Metoda 1 `splitlines()`     : %d" % t1)
print("  Metoda 2 počet znaků '\\n'   : %d" % t2)
print("  Metoda 3 počet '\\r\\n'       : %d" % t3)
print()
print("  ROZDÍL 1-2 = %d  → tolik souborů KONČÍ newline, ale splitlines()")
print("  nepočítá prázdný prvek na konci (soubor 'a\\n' má splitlines()==1, \\n==1).")
print("  Rozdíl tedy dělá KONCOVÝ newline u souboru, který jím NEkončí.")
print()
print("  A metoda 3 je menší proto, že soubory mají LF, ne CRLF.")
print()
print("  ⚠ POUČENÍ PRO AUDIT: plán uvádí 3 392, PowerShell 3 678, Python 3 832.")
print("    Ani jedno číslo není „nepravdivé“, jen každé odpovídá na jinou")
print("    otázku. Do dokumentu patří číslo S POSTUPEM (`AGENTS.md`).")

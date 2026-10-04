# -*- coding: utf-8 -*-
"""SONDA k `audit2b-over.py`: jaký řádek nástroj hlásí a co je v seznamech?

Nástroj tvrdí, že kotva „D1 má 16 řádků na 21 granul" NENÍ v ZÁZNAMECH.
Sonda vypíše:
  · co vrátí `radek_s_textem` (a jak ho nástroj počítá),
  · KTERÉ řádky s `granulí` jsou v ROZCHODECH a KTERÉ v ZÁZNAMECH,
  · a jestli mezi nimi kotva vůbec je.
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PY = sys.executable


def radek_s_textem(text, hledany):
    """KOPIE funkce z `audit2b-over.py` — MUSÍ BÝT SHODNÁ (`overovani` §10.5)."""
    i = text.find(hledany)
    if i < 0:
        return -1
    return text[:i].count("\n") + 1


KOTVA = "- **D1 má 16 řádků na 21 granul**"
s = (WS / "HANDOFF.md").read_text(encoding="utf-8")
r = radek_s_textem(s, KOTVA)
print("1) radek_s_textem(%r) = %s" % (KOTVA[:34], r))
radky = s.splitlines()
print("   soubor má %d řádků · na ř. %d je: %s" % (len(radky), r, radky[r - 1][:96]))
print("   obsahuje ta řádka 'granulí'? %s" % ("granulí" in radky[r - 1]))

print("\n2) co nástroj skutečně vypsal:")
v = subprocess.run([PY, "_analyza/audit2b-cisla-proti-zdroji.py"],
                   cwd=str(WS), capture_output=True, timeout=600)
out = v.stdout.decode("utf-8", "replace")

# sekce ROZCHODY vs ZÁZNAMY
i_roz = out.find("ROZCHODY (tvrzení bez známky minulosti)")
i_zaz = out.find("ZÁZNAMY A CITACE MINULOSTI")
print("   (indexy sekcí: rozchody=%d, záznamy=%d)" % (i_roz, i_zaz))

wzor = re.compile(r"^\s+(HANDOFF\.md)\s+:(\d+)\s+(\S+)\s+tvrdí", re.M)
roz = [(m.group(1), int(m.group(2)), m.group(3)) for m in wzor.finditer(out)
       if i_zaz < 0 or m.start() < i_zaz]
vse = [(m.group(1), int(m.group(2)), m.group(3)) for m in wzor.finditer(out)]

print("\n3) řádky s `granulí` v ROZCHODECH:")
for j, n, k in roz:
    if k == "granulí":
        print("      %s :%d" % (j, n))
print("   řádky s `granulí` ve VÝPISU (rozchody i záznamy):")
for j, n, k in vse:
    if k == "granulí":
        print("      %s :%d" % (j, n))

print("\n4) je kotva (%d) v některém z nich? %s"
      % (r, "ANO" if any(n == r for _, n, k in vse if k == "granulí") else "NE"))
print("   nejbližší hlášené řádky s `granulí` kolem kotvy: %s"
      % sorted(n for _, n, k in vse if k == "granulí" and abs(n - r) < 200))

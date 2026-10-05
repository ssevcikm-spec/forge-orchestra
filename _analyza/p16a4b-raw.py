# -*- coding: utf-8 -*-
"""P16/A4b — které soubory dostaly v `ce49234` RAW string (tvrzení D z §33).

Zadání i §33 mluví o „třech řetězcích převedených na raw string". Tohle je
přímé měření: najdi v diffu `ce49234~1..ce49234` řádky, které přidávají
`r\"\"\"` / `r'''`, a k nim soubor. Nic nemění.
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = str(WS / "tools" / "git.cmd")
PRE = "ce49234~1"


def git(*args):
    r = subprocess.run([GIT, "-C", str(WS), *args], capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace")


zmenene = [f for f in git("diff", "--name-only", PRE, "ce49234").splitlines() if f.strip()]
print(f"souborů změněných v ce49234: {len(zmenene)}")

raw_zaveden = []
for f in zmenene:
    if not f.endswith(".py"):
        continue
    d = git("diff", "--unified=0", PRE, "ce49234", "--", f)
    for l in d.splitlines():
        if l.startswith("+") and not l.startswith("+++") and re.match(r"\+\s*r(\"\"\"|''')", l):
            raw_zaveden.append((f, l.strip()[:70]))
print(f"\n--- soubory, kde diff PŘIDÁVÁ raw docstring: {len(raw_zaveden)}")
for f, l in raw_zaveden:
    print(f"  {f}\n      {l}")

print("\n--- všechny .py v _analyza, které dnes mají raw docstring na začátku")
n = 0
for p in sorted((WS / "_analyza").glob("*.py")):
    prvni = p.read_text(encoding="utf-8", errors="replace").splitlines()[:1]
    if prvni and re.match(r"\s*r(\"\"\"|''')", prvni[0]):
        n += 1
        print(f"  {p.name}: {prvni[0][:60]}")
print(f"  celkem: {n}")

print("\n--- p1b: kde je v něm neplatná escape sekvence? (KÓD, ne komentář)")
for f in ("_analyza/p1-inventura-cest.py", "_analyza/p1b-odvozene-cesty.py"):
    pre = git("show", f"{PRE}:{f}").splitlines()
    po = (WS / f).read_text(encoding="utf-8", errors="replace").splitlines()
    print(f"  {f}: pre {len(pre)} řádků, po {len(po)} řádků")
    spatne_pre = [(i + 1, l) for i, l in enumerate(pre)
                  if re.search(r'\\[^\\\'"abfnrtv0-7xuUN\n]', l) and not l.lstrip().startswith("#")]
    print(f"    řádky s NEplatnou escape sekvencí (mimo komentáře): {len(spatne_pre)}")
    for i, l in spatne_pre[:6]:
        print(f"      ř.{i}: {l[:88]}")
sys.exit(0)

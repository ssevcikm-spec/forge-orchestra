# -*- coding: utf-8 -*-
"""P16/A4c — H79: změnil raw string JEDINÝ ZNAK? (měřeno na KONSTANTÁCH)

Tvrzení P15: „tři řetězce převedeny na raw string … konstanty **shodné s HEAD**".
⚠ „Shodné s HEAD" je podezřelé: soubor je v HEADu **po** převodu, takže test
porovnává soubor **sám se sebou** (třída H60, samoodkaz měřidla). Tohle měřidlo
proto bere **blob z commitu PŘED** (`ce49234~1`) — ten obsahuje NERAW docstring —
a porovnává **hodnoty konstant** (AST), ne text.

⚠ Co se z gitu získat NEDÁ: stav přesně před P15 (P13c, P14 i P15 se commitly
společně jako `ce49234`). `ce49234~1` = `c620a06` = P13b — je to NEJBLIŽŠÍ
dostupný „před“, ale u souborů, které P13c/P14 měnily, se musí rozdíl přiznat,
ne zamlčet.
"""

import ast
import pathlib
import re
import subprocess
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = str(WS / "tools" / "git.cmd")
PRE = "ce49234~1"
SOUBORY = ["_analyza/p1-inventura-cest.py", "_analyza/ps1-bom-crlf.py",
           "_analyza/sken-vazeb.py"]

kontrol = 0
chyb = 0


def zk(ok, popis, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def git(*args):
    r = subprocess.run([GIT, "-C", str(WS), *args], capture_output=True, shell=True)
    return (r.returncode, (r.stdout or b"").decode("utf-8", "replace"))


def varovani(text: str):
    with warnings.catch_warnings(record=True) as w:
        warnings.simplefilter("always")
        try:
            compile(text, "<kontrola>", "exec")
        except SyntaxError as e:
            return [f"SyntaxError: {e.msg}"]
        return [f"{x.lineno}: {x.message}" for x in w
                if issubclass(x.category, SyntaxWarning)]


def docstringy(text: str):
    """Všechny řetězcové konstanty (jméno → hodnota) — včetně docstringů."""
    out = {}
    strom = ast.parse(text)
    for n in ast.walk(strom):
        if isinstance(n, ast.Constant) and isinstance(n.value, str):
            out.setdefault(n.value, n.lineno)
    return out


print("=" * 78)
print("P16/A4c — H79: obsah řetězců před/po převodu na raw string")
print("=" * 78)
print(f"  „před“ = {PRE} (POZOR: je to P13b, ne stav před P15 — viz docstring)")

for rel in SOUBORY:
    print(f"\n--- {rel}")
    kod, pre = git("show", f"{PRE}:{rel}")
    if kod != 0 or not pre.strip():
        zk(False, f"{rel} v {PRE} NENÍ → „před“ se pro tenhle soubor měřit nedá")
        continue
    po = (WS / rel).read_text(encoding="utf-8", errors="replace")
    v_pre, v_po = varovani(pre), varovani(po)
    print(f"  SyntaxWarning: před {len(v_pre)} {v_pre}")
    print(f"                 po   {len(v_po)} {v_po}")
    pr = pre.splitlines()[:1]
    po1 = po.splitlines()[:1]
    print(f"  první řádek před: {pr[0][:70] if pr else '—'}")
    print(f"  první řádek po  : {po1[0][:70] if po1 else '—'}")
    zk(len(v_po) == 0, f"{rel}: DNES nemá ani jedno SyntaxWarning")
    if v_pre:
        zk(len(v_pre) > 0, f"{rel}: PŘED převodem varování BYLA ({len(v_pre)}) "
           "→ raw string měl co opravit")
    # porovnání KONSTANT
    try:
        k_pre, k_po = docstringy(pre), docstringy(po)
    except SyntaxError as e:
        zk(False, f"{rel}: blob před P15 se nedá parsovat", str(e)[:60])
        continue
    chybejici = [s for s in k_pre if s not in k_po]
    pribyle = [s for s in k_po if s not in k_pre]
    print(f"  konstant: před {len(k_pre)}, po {len(k_po)}, "
          f"zmizelo {len(chybejici)}, přibylo {len(pribyle)}")
    for s in chybejici[:2]:
        print(f"      ZMIZELO (r. {k_pre[s]}): {s[:70]!r}")
    for s in pribyle[:2]:
        print(f"      PŘIBYLO (r. {k_po[s]}): {s[:70]!r}")
    zk(not chybejici and not pribyle,
       f"{rel}: MNOŽINA konstant je proti `{PRE}` SHODNÁ "
       f"(raw string nezměnil jediný znak)")
    if chybejici or pribyle:
        print("      ⚠ ROZDÍL SE MUSÍ PŘIZNAT: mezi {0} a ce49234 je i práce "
              "P13c/P14 — ne každý rozdíl je vina převodu na raw string".format(PRE))

print("\n--- co s tím dělá test P15 (`test-h79-escape.py`) ---------------------")
t15 = (WS / "_analyza" / "test-h79-escape.py").read_text(encoding="utf-8")
for l in t15.splitlines():
    if "HEAD" in l or "git" in l.lower():
        print(f"      {l.strip()[:96]}")
zk("HEAD" in t15, "test P15 porovnává proti `HEAD` (tj. proti stavu PO převodu)",
   "samoodkaz — viz závěr níž")
print("      ⚠ DŮSLEDEK: test P15 porovnává soubor s tím, co je v HEADu DNES. "
      "Kdyby převod na raw string obsah změnil a byl commitnutý, test to "
      "NEVIDÍ — nezávislý důkaz je jen proti blobu PŘED (tohle měřidlo).")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)

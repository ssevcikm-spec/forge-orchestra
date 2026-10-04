# -*- coding: utf-8 -*-
"""Ověření, že oprava `test-cooldown.py` (Úkol F) je v souboru SKUTEČNĚ zapsaná.

Patcher `f2-oprav-cooldown-test.py` se při druhém spuštění ukončí hned
(`oprava už v souboru je`), takže jeho `assert`-y se podruhé neprovedou.
Ten skript je proto dělá znovu a samostatně — a navíc pouští test, aby
se nehodnotil jen text, ale i chování.
"""

import ast
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "orchestra" / "tools" / "test-cooldown.py"
TEST = WS / "orchestra" / "tools" / "test-cooldown.py"

t = CIL.read_text(encoding="utf-8")


def bez_textu(zdroj: str) -> str:
    """Zdroj bez komentářů A BEZ DOKUMENTAČNÍCH ŘETĚZCŮ.

    PROČ NE jen `startswith('#')`: vada je popsaná i v docstringu (`\"\"\"…\"\"\"`),
    a ten není komentář — filtr podle `#` by ten text nechal a pojistka by
    hlásila falešný poplach na dokumentaci, která vadu POPISUJE.
    (Přesně na to jsem napoprvé naletěl.)
    """
    strom = ast.parse(zdroj)
    for uzel in ast.walk(strom):
        if isinstance(uzel, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                             ast.ClassDef)):
            telo = uzel.body
            if (telo and isinstance(telo[0], ast.Expr)
                    and isinstance(telo[0].value, ast.Constant)
                    and isinstance(telo[0].value.value, str)):
                telo.pop(0)
    return ast.unparse(strom)


kod = bez_textu(t)

kontroly = [
    ("fixture nekrmí sloupec řetězcem '-10 minutes'", "'-10 minutes'" not in kod),
    ("starý INSERT s datetime('now', ?) je pryč", "datetime('now', ?),?)" not in t),
    ("pomocník _cas_pred je v souboru", "_cas_pred(" in kod),
    ("časy se počítají v Pythonu (datetime.fromtimestamp)",
     "datetime.datetime.fromtimestamp" in kod),
    ("nová granule se MÁ vydat (True, False)",
     '("NOVÁ granule (vznikla teď, neselhal)", "queued", 0, None, True, False)' in t),
    ("hlavička nelže: mluví o STAVU PO B1", "STAV PO B1" in t),
    ("hlavička přiznává vadu fixture", "V TÉTO FIXTURE BYLA DRUHÁ VADA" in t),
    ("regresní poznámka u invariantu 13", "regresní test na S12" in t),
]

chyb = 0
for popis, ok in kontroly:
    if not ok:
        chyb += 1
    print("  %s %s" % ("OK  " if ok else "CHYBA", popis))

# A hlavně: spusť test a čti VÝSLEDEK (ne jen text souboru).
r = subprocess.run([sys.executable, str(TEST)], capture_output=True, cwd=str(WS))
v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
m = re.search(r"VÝSLEDEK: (\d+) kontrol, (\d+) chyb", v)
print()
if not m:
    print("  CHYBA: test nevypsal VÝSLEDEK — nedoběhl")
    print(v[-1500:])
    sys.exit(1)
kontrol, chyb_testu = int(m.group(1)), int(m.group(2))
print("  běh testu: %d kontrol, %d chyb, exit=%d" % (kontrol, chyb_testu, r.returncode))
if chyb_testu != 0 or r.returncode != 0:
    print("  CHYBA: test neprošel")
    for radek in v.splitlines():
        if "CHYBA" in radek or "VADA" in radek:
            print("     " + radek.strip())
    chyb += 1
if "VŠE OK" not in v:
    print("  CHYBA: v výstupu není 'VŠE OK'")
    chyb += 1

print()
print("VÝSLEDEK: %s" % ("oprava je zapsaná a test prochází 10/10"
                        if chyb == 0 else "NĚCO NESEDÍ (%d)" % chyb))
sys.exit(0 if chyb == 0 else 1)

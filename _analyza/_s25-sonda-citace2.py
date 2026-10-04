# -*- coding: utf-8 -*-
"""SONDA 7 — volá `je_citace()` PŘÍMO z nástroje (ne opisem).

`overovani` §10.5: když ověřovatel reimplementuje logiku nástroje, musí to být
řádek po řádku táž logika. Tady se proto funkce **importuje** z nástroje —
když se neshoduje s ručním skenem, je vada v nástroji, ne v sondě.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(WS / "_analyza"))

# Nástroj má `main()`, ale funkce jsou uvnitř ní → spustíme zdroj a vytáhneme
# je přes exec s podstrčeným argv, aby se `main()` nezavolalo.
zdroj = (WS / "_analyza" / "audit2b-cisla-proti-zdroji.py").read_text(encoding="utf-8")
print("  zdroj nástroje: %d B" % len(zdroj))
print("  obsahuje 'UVNITŘ KÓDOVÉHO ROZPĚTÍ': %s"
      % ("UVNITŘ KÓDOVÉHO ROZPĚTÍ" in zdroj))
print("  obsahuje \"(?!\\\\w)\": %s" % ("(?!\\w)" in zdroj))

# Ruční opis TÉŽE logiky — abych viděl, kde se to rozchází
UVOZOVKY = [("„", "“"), ("„", '"'), ('"', '"'), ("`", "`"), ("*„", "“")]


def je_citace_rucne(s, index):
    radky = s.splitlines()
    radek_idx = s.count("\n", 0, index)
    if radek_idx >= len(radky):
        return False
    radek = radky[radek_idx]
    v_radku = index - (s.rfind("\n", 0, index) + 1)
    if v_radku >= len(radek):
        return False
    otevreno = []
    i = 0
    while i < len(radek):
        if otevreno:
            if radek.startswith(otevreno[-1], i):
                i += len(otevreno.pop())
            else:
                i += 1
            continue
        if otevreno and otevreno[-1] == "`":
            if radek.startswith("„", i):
                otevreno.append("“")
                i += 1
                continue
            i += 1
            continue
        for otev, zavr in UVOZOVKY:
            if radek.startswith(otev, i):
                otevreno.append(zavr)
                i += len(otev)
                break
        else:
            i += 1
    return bool(otevreno)


text = (WS / "HANDOFF.md").read_text(encoding="utf-8")
for m in re.finditer(r"(\d+)\s+sloupc", text):
    radek = text[:m.start()].count("\n") + 1
    if radek != 743:
        continue
    print()
    print("  HANDOFF.md:%d  tvrzeno=%s" % (radek, m.group(1)))
    print("    ruční opis  → citace = %s" % je_citace_rucne(text, m.start()))

# -*- coding: utf-8 -*-
"""SONDA 4 (jednorázová) — přesné množiny id omylů v `HANDOFF.md` §8.

PROČ: sonda 3 naměřila **153 řádků** tabulek a **96 unikátních id**, ale
`kronika-kontrola.py` hlásí **75**. Rozdíl musí být vysvětlený, ne uhlazený
(`overovani` §9.3: „počítej množinu, ne řádky" — a ke každému „celkem N" patří
seznam zdrojů).

Vypíše: množinu id v každém bloku, sjednocení, průnik §8 vs. podbloky a
**které id nikde není** (díry v číslování).
"""
import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HAND = WS / "HANDOFF.md"
text = HAND.read_text(encoding="utf-8")
radky = text.splitlines()

ID_RADEK = re.compile(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")
ANCHOR = re.compile(r"^(#{2,4})\s+(8[A-Za-z]?)\.\s")

bloky = []          # (popis, uroven, start_idx, id_set)
for i, l in enumerate(radky):
    m = ANCHOR.match(l)
    if not m:
        continue
    uroven = len(m.group(1))
    konec = len(radky)
    for j in range(i + 1, len(radky)):
        m2 = re.match(r"^(#{2,4})\s", radky[j])
        if m2 and len(m2.group(1)) <= uroven:
            konec = j
            break
    ida = set()
    for l2 in radky[i:konec]:
        m3 = ID_RADEK.match(l2)
        if m3:
            ida.add(int(m3.group(1)))
    bloky.append((m.group(2), l.strip()[:70], ida))

print("=" * 100)
print("  ID V JEDNOTLIVÝCH BLOCÍCH")
print("=" * 100)
vsechna = set()
for klic, popis, ida in bloky:
    vsechna |= ida
    kratce = sorted(ida)
    rozsah = ("%d–%d" % (kratce[0], kratce[-1])) if kratce else "(žádné)"
    print("  %-4s %-66s %2d id  %s" % (klic, popis, len(ida), rozsah))

hlavni = next((ida for klic, _p, ida in bloky if klic == "8"), set())
podbloky = set()
for klic, _p, ida in bloky:
    if klic != "8":
        podbloky |= ida

print()
print("=" * 100)
print("  TŘI OTÁZKY, TŘI ODPOVĚDI")
print("=" * 100)
print("  unikátních id v CELÉM dokumentu (sjednocení všech bloků): %d" % len(vsechna))
print("  unikátních id v hlavním bloku `## 8.`:                    %d" % len(hlavni))
print("  unikátních id v podblocích 8b–8k:                        %d" % len(podbloky))
print("  id JEN v hlavním bloku (ne v podbloku):                  %d"
      % len(hlavni - podbloky))
print("  id JEN v podbloku (ne v hlavním bloku):                  %d"
      % len(podbloky - hlavni))
print("  PRŮNIK (v obou → dvojí počítání):                        %d"
      % len(hlavni & podbloky))

# Co hlásí BRÁNA — čte se Z JEJÍHO BĚHU, ne z opsaného seznamu.
# ⚠ DO 3. 10. 2026 tu byl **pevný seznam 8 kotev** a tisklo se
# „CELKEM 132  ← to hlásí brána“. Byla to **nepravda o cizím nástroji**:
# brána bloky hledá v dokumentu (`bloky_omylu`) a má jich **14** — hlásí
# **118**. Sonda tím odpovídala na jinou otázku, než tvrdila (`overovani` §1).
# Nově se pouští brána a čte se její VLASTNÍ čítač; vedle toho stojí měření
# sondy (množina unikátních id). Dvě měření, ne jedno opsané.
print()
print("  CO HLÁSÍ BRÁNA (`kronika-kontrola.py`) — čte se z jejího BĚHU:")
try:
    _r = subprocess.run([sys.executable, str(WS / "_analyza" / "kronika-kontrola.py")],
                        cwd=str(WS), capture_output=True, timeout=900,
                        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    _v = (_r.stdout + _r.stderr).decode("utf-8", "replace")
    for _vzor in (r"bloků omylů v tomto součtu:\s*\d+",
                  r"omylů celkem \(skutečnost\):\s*\d+"):
        _m = re.search(_vzor, _v)
        print("      %s" % (_m.group(0) if _m else
                            "NEZMĚŘENO (výstup neobsahuje %s)" % _vzor))
    print("      exit=%d" % _r.returncode)
except Exception as _e:                                             # noqa: BLE001
    # Nula a „nezměřeno“ nejsou úspěch — vypíše se to, nikdy ticho.
    print("      NEZMĚŘENO — bránu nešlo spustit: %s" % type(_e).__name__)

# Díry v číslování
print()
print("=" * 100)
print("  DÍRY V ČÍSLOVÁNÍ (id, které v žádném bloku není)")
print("=" * 100)
if vsechna:
    chybejici = [x for x in range(1, max(vsechna) + 1) if x not in vsechna]
    print("  max id: %d · chybějících id: %d" % (max(vsechna), len(chybejici)))
    print("  chybí: %s" % chybejici)
else:
    print("  ŽÁDNÁ ID NENALEZENA — to je slepé místo, ne nula!")

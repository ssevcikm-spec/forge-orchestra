# -*- coding: utf-8 -*-
r"""Mutační test `kronika-kontrola.py` — umí ta brána vůbec spadnout?

PROČ: „Prošlo to" bez odpovědi na „umí to spadnout?" neznamená nic
(`AGENTS.md`, skill `overovani` §1). Kontrola kroniky **už jednou** v praxi
zabrala (našla dva skutečné rozchody — viz omyl **60** v `HANDOFF.md` §8f),
ale to je **jeden** případ. Tohle je **systematické** ověření.

Mutace se dělají v **KOPII** kroniky (`_analyza\h17-kronika-kopie.md`), takže
se originálu **nesáhne** — a to je záměr: kdyby test zapisoval do
`KRONIKA-PROJEKTU.md`, mohl by ji poškodit (past `overovani` §2.1: „zálohuj
kopií, ne prevencí gitu").

CO SE MUTUJE (každá mutace míří na JINOU podmínku brány):
  M1  počet omylů u bloku 8e (10 → 99)      → musí spadnout na kontrole A
  M2  nález H5 se přejmenuje na H99         → musí spadnout na kontrole B
  M3  řádek session ztratí datum            → musí spadnout na kontrole C
  M4  odkaz na neexistující dokument        → musí spadnout na kontrole D
  M5  zdravá kopie                          → musí projít (kontrolní případ)

Použití:  python _analyza\h17-kronika-mutace.py
"""

import importlib.util
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
KOPIE = WS / "_analyza" / "h17-kronika-kopie.md"
BRANA = WS / "_analyza" / "kronika-kontrola.py"

assert KRONIKA.is_file() and BRANA.is_file()
PUVODNI = KRONIKA.read_bytes()
print("=" * 78)
print("MUTAČNÍ TEST `kronika-kontrola.py`")
print("=" * 78)

# Brána má cestu ke kronice NApevno (WS / "KRONIKA-PROJEKTU.md"). Aby šla
# spustit nad kopií, vytáhne se z ní zdroj a přepíše se jen konstanta —
# nic se needituje v souboru samém.
zdroj = BRANA.read_text(encoding="utf-8")
assert 'KRONIKA = WS / "KRONIKA-PROJEKTU.md"' in zdroj, \
    "v bráně se nenašla konstanta KRONIKA — mutace by měřila jiný soubor"


def spust_nad(text_kroniky: str) -> tuple:
    """Spustí bránu nad ZADANÝM textem kroniky. Vrací (exit, výstup)."""
    KOPIE.write_bytes(text_kroniky.encode("utf-8"))
    docasny = WS / "_analyza" / "_h17-brana-nad-kopii.py"
    docasny.write_bytes(
        zdroj.replace('KRONIKA = WS / "KRONIKA-PROJEKTU.md"',
                      'KRONIKA = WS / "_analyza" / "h17-kronika-kopie.md"')
        .encode("utf-8"))
    r = subprocess.run([sys.executable, str(docasny)], capture_output=True, cwd=str(WS))
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    docasny.unlink(missing_ok=True)
    return r.returncode, v


MUTACE = []

# M1 — přehozený počet omylů u bloku 8e
t = PUVODNI.decode("utf-8")
radky = t.split("\n")
for i, r in enumerate(radky):
    if re.match(r"^\|\s*\*\*8e\*\*\s*\|", r):
        novy = re.sub(r"\|\s*\*\*11\*\*\s*\|", "| **99** |", r, count=1)
        assert novy != r, "M1: vzor `**11**` v řádku 8e není"
        radky[i] = novy
        break
else:
    raise AssertionError("M1: řádek bloku 8e se nenašel")
MUTACE.append(("M1 počet omylů 8e: 11 → 99", "\n".join(radky), "A"))

# M2 — nález H5 přejmenován (v tabulce §2.1)
assert "**H5**" in t, "M2: nález H5 v kronice není"
MUTACE.append(("M2 nález H5 → H99", t.replace("**H5**", "**H99**", 1), "B"))

# M3 — řádek session bez data
radky = t.split("\n")
for i, r in enumerate(radky):
    if re.match(r"^\|\s*\*\*1\*\*\s*\|", r):
        novy = re.sub(r"(0?[0-9]|[12][0-9]|3[01])\.\s*(0?[0-9]|1[0-2])\.\s*20\d\d",
                      "datum smazán", r, count=1)
        assert novy != r, "M3: v řádku session 1 žádné datum není"
        radky[i] = novy
        break
else:
    raise AssertionError("M3: řádek session 1 se nenašel")
MUTACE.append(("M3 řádek session bez data", "\n".join(radky), "C"))

# M4 — odkaz na neexistující dokument
MUTACE.append(("M4 odkaz na neexistující `NEJEDU-TAM.md`",
               t.replace("`HANDOFF.md`", "`NEJEDU-TAM.md`", 1), "D"))

vysledky = []
print()
print("-" * 78)
print("M5: KONTROLNÍ PŘÍPAD — zdravá kopie kroniky (musí projít)")
print("-" * 78)
kod, v = spust_nad(PUVODNI.decode("utf-8"))
print("  exit=%d   %s" % (kod, [l for l in v.splitlines() if "KRONIKA SEDÍ" in l or "NALEZENO" in l][:1]))
vysledky.append(("M5 zdravá kopie (kontrolní)", kod, 0))

for popis, text, ocekavana in MUTACE:
    print()
    print("-" * 78)
    print("%s   (má spadnout na kontrole %s)" % (popis, ocekavana))
    print("-" * 78)
    kod, v = spust_nad(text)
    radky_chyb = [l.strip() for l in v.splitlines() if l.strip().startswith("CHYBA")]
    print("  exit=%d" % kod)
    for l in radky_chyb[:4]:
        print("    %s" % l[:130])
    vysledky.append((popis, kod, 1))

KOPIE.unlink(missing_ok=True)
assert KRONIKA.read_bytes() == PUVODNI, "KRONIKA SE ZMENILA — test nesmí sahat na originál"
print()
print("  [úklid: kopie smazána, KRONIKA-PROJEKTU.md bajt na bajt stejná]")

print()
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
chyby = []
for popis, kod, ocekavany in vysledky:
    ok = (kod != 0) if ocekavany else (kod == 0)
    print("  %-38s exit=%-3d %s" % (popis, kod, "OK" if ok else "ROZCHOD"))
    if not ok:
        chyby.append("%s: exit=%d, očekáváno %s"
                     % (popis, kod, "nenulový" if ocekavany else "0"))

print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE SEDÍ — brána projde nad zdravou kronikou a SPADNE na každé ze 4 vad.")
sys.exit(0)

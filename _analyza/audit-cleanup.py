# -*- coding: utf-8 -*-
"""Úklid po auditu: soubory, které PowerShell zapsal v UTF-16LE, převést na UTF-8.

PROČ TO EXISTUJE (a je to poučení, ne formalita):
  Výstupy jsem ukládal přes `python ... > _analyza\\audit1-vystup.txt 2>&1`.
  PowerShell **přesměruje výstup jako UTF-16LE** — a brána diakritiky takový
  soubor nepřečte. Naměřeno: `g1-diakritika-novych.py` skončil `exit 1` a
  jediná vada byla **`audit-g1-vystup.txt` — tedy můj vlastní výstupní soubor**.
  Ostatní přesměrované soubory brána **tiše přeskočila jako binární**, což je
  horší varianta téhož: vypadají jako „nic tam není".

  Je to táž past, na kterou upozorňuje `dsh-prostredi` §5b
  (`git show > soubor` v PowerShellu = UTF-16LE), jen o vrstvu jinde.

CO DĚLÁ: každý `_analyza\\*-vystup*.txt`, který není UTF-8, převede na UTF-8;
soubor, který vznikl jako výstup té brány, smaže (je to self-referenční artefakt).
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"

# Tenhle soubor vznikl jako výstup brány, která ho pak četla — smazat.
SMAZAT = ["audit-g1-vystup.txt"]

print("=" * 88)
print("ÚKLID — PŘEVOD VÝSTUPŮ Z UTF-16LE NA UTF-8")
print("=" * 88)
print()

for jmeno in SMAZAT:
    p = ANALYZA / jmeno
    if p.is_file():
        p.unlink()
        print("  SMAZÁNO  %s  (self-referenční výstup brány)" % jmeno)
    else:
        print("  (už není) %s" % jmeno)
print()

prevadene, ok, selhalo = 0, 0, []
for p in sorted(ANALYZA.glob("*vystup*.txt")):
    b = p.read_bytes()
    try:
        b.decode("utf-8")
        ok += 1
        continue                     # už je UTF-8 — nic se nedělá
    except UnicodeDecodeError:
        pass
    for enc in ("utf-16", "utf-16-le", "cp1250", "cp1252"):
        try:
            text = b.decode(enc)
            break
        except (UnicodeDecodeError, UnicodeError):
            continue
    else:
        selhalo.append(p.name)
        continue
    p.write_bytes(text.encode("utf-8"))
    prevadene += 1
    print("  PŘEVEDENO %-34s z %s → utf-8 (%d znaků)" % (p.name, enc, len(text)))

print()
print("  už v UTF-8 : %d" % ok)
print("  převedeno  : %d" % prevadene)
if selhalo:
    print("  NEPOVEDLO SE PŘEČÍST: %s" % ", ".join(selhalo))
print()
print("  Teď musí `g1-diakritika-novych.py` projít bez vady na těchto souborech.")

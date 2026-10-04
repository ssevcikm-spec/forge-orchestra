# -*- coding: utf-8 -*-
"""Souhrn běhu `g3-brany.py` — VŠECHNY brány a co která OTEVŘELA (past S27).

Čte `_analyza\g3-s24-vystup.txt`. ⚠ PowerShell přesměruje výstup jako
**UTF-16LE** (`dsh-prostredi` §5b) — proto se konvertuje, ne čte naslepo.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
P = WS / "_analyza" / "g3-s24-vystup.txt"

b = P.read_bytes()
if b[:2] in (b"\xff\xfe", b"\xfe\xff"):
    P.write_bytes(b.decode("utf-16").encode("utf-8"))
    print("(výstup byl UTF-16LE — převeden na UTF-8)")

text = P.read_text(encoding="utf-8")
radky = text.splitlines()

print("=" * 92)
print("BRÁNY A CO KTERÁ OTEVŘELA")
print("=" * 92)
prazdne, bran = [], 0
for l in radky:
    if "otevřela:" in l:
        bran += 1
        hodnota = l.split("otevřela:", 1)[1].strip()
        if not hodnota:
            prazdne.append(l.strip())
        print("  %s" % l.rstrip())

print()
for l in radky:
    if "brán celkem" in l or l.strip().startswith("CHYBA"):
        print("  %s" % l.strip())

print()
print("  bran s výpisem: %d · s PRÁZDNÝM `otevřela:`: %d" % (bran, len(prazdne)))
for p in prazdne:
    print("      %s" % p[:100])
print("  délka plného výstupu: %d znaků" % len(text))

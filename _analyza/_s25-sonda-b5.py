# -*- coding: utf-8 -*-
"""SONDA 13 — proč přejmenování `filesInOriginMain` NEZměnilo verdikt 3 v `b5`.

Vypíše stav souboru i to, co z něj brána čte — `overovani` §8.4 („vypiš si
OKOLÍ a VÝPISNÍ CESTU nástroje, ne jeho výsledek").
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
CIL = WS / "orchestra" / "conductor" / "src" / "index.ts"
BRANA = WS / "_analyza" / "b5-over-tvrzeni.py"
IDENT = "filesInOriginMain"

orig = CIL.read_bytes()
t = orig.decode("utf-8")
print("  soubor: %s" % CIL)
print("  velikost: %d B" % len(orig))
print("  výskytů %r (hranice slova): %d"
      % (IDENT, len(re.findall(r"\b%s\b" % IDENT, t))))

# Co dělá brána: bez_komentaru_ts
def bez_komentaru_ts(s):
    s = re.sub(r"/\*.*?\*/", "", s, flags=re.S)
    return re.sub(r"^\s*//.*$", "", s, flags=re.M)


try:
    zmut = re.sub(r"\b%s\b" % IDENT, IDENT + "XX", t)
    assert zmut != t, "MUTACE NEPROBĚHLA"
    CIL.write_text(zmut, encoding="utf-8", newline="")
    zpet = CIL.read_text(encoding="utf-8")
    print("  PO ZÁPISU: výskytů %r: %d" % (IDENT, len(re.findall(r"\b%s\b" % IDENT, zpet))))
    print("  PO ZÁPISU: výskytů %rXX: %d" % (IDENT, len(re.findall(r"\b%sXX\b" % IDENT, zpet))))
    print("  KOD (bez komentářů) obsahuje %r: %s"
          % (IDENT, IDENT in bez_komentaru_ts(zpet)))
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True, cwd=str(WS))
    v = (r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace"))
finally:
    CIL.write_bytes(orig)
    assert CIL.read_bytes() == orig, "NEVRÁCENO!"

print("  exit brány po mutaci: %d" % r.returncode)
print()
print("  ── verdikty z výstupu ──")
for l in v.splitlines():
    if "->" in l or "zastaralých" in l or "VYSLEDEK" in l:
        print("   %s" % l.strip()[:120])

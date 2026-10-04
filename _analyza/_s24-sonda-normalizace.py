# -*- coding: utf-8 -*-
"""Proč `"granulí" in řádek` vrací False, když tam slovo viditelně je?

Hypotéza: **jiná normalizace** (precomposed `U+00ED` vs. rozložené `i` + `U+0301`)
— a to je past, kterou textový editor ani `read` neukáže.
"""
import pathlib
import sys
import unicodedata

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

s = pathlib.Path(__file__).resolve().parent.parent.joinpath("HANDOFF.md").read_text(encoding="utf-8")
radky = s.splitlines()
l = radky[1200]

print("řádek 1201 (repr, prvních 70 znaků):")
print("  %r" % l[:70])
print()
print("  'granulí' (precomposed) v řádku : %s" % ("granulí" in l))
print("  'granul' (bez diakritiky)        : %s" % ("granul" in l))

i = l.find("granul")
print("  index 'granul'                   : %d" % i)
if i >= 0:
    kus = l[i:i + 7]
    print("  znaky po 'granul'                : %s" % [hex(ord(c)) for c in kus])
    print("  jejich jména                     : %s"
          % [unicodedata.name(c, "?") for c in kus])

print()
print("  v CELÉM souboru: 'granulí' = %d · 'granul' = %d"
      % (s.count("granulí"), s.count("granul")))

# najdi všechny varianty slova granul* v souboru
import collections
var = collections.Counter()
for m in __import__("re").finditer(r"granul\w*", s):
    var[m.group(0)] += 1
print("  varianty slova 'granul*':")
for k, v in var.most_common():
    print("      %-14s %4d  (znaky: %s)" % (k, v, [hex(ord(c)) for c in k[6:]]))

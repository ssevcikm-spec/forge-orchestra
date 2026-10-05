# -*- coding: utf-8 -*-
"""Přesná sonda na vzor artefaktů + na to, co skener opravdu vyhodí."""
import importlib.util
import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SRC = pathlib.Path(r"E:\Workspaces\forge-orchestra\_analyza\hl-neanglicky-v-kodu.py")
text = SRC.read_text(encoding="utf-8")

# Vytáhni DOSLOVNĚ blok ARTEFAKT_RE = re.compile(...) ze zdroje a spusť ho.
i = text.index("ARTEFAKT_RE = re.compile(")
j = text.index("\n)\n", i) + 3
blok = text[i:j]
print("--- blok ze zdroje ---")
print(blok)
ns = {}
exec("import re\n" + blok, ns)
RE = ns["ARTEFAKT_RE"]

for f in ["_analyza/_test-h52-untracked.py",
          "_analyza/_inventar.json",
          "_analyza/_registr-bran.json",
          "_analyza/_tokeny.json",
          "_analyza/_sonda-inv.json",
          "_analyza/g3-brany-vystup.txt",
          "tools/verify-setup.py",
          "_analyza/p13c-sonda-h52.py"]:
    m = RE.search(f)
    print(f"  {f:42s} -> {bool(m)}  {m.group(0) if m else ''}")

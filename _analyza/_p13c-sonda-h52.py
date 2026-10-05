# -*- coding: utf-8 -*-
"""Sonda: který soubor vrací skener v E2 (a proč artefakt vzor nesedl)."""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"E:\Workspaces\forge-orchestra")
A = WS / "_analyza"
SOUBOR = A / "_test-h52-untracked.py"
SOUBOR2 = A / "_test-h52-untracked.py"
INV = A / "_sonda-inv.json"

OBSAH = ("# -*- coding: utf-8 -*-\n"
         "def zm\u011b\u0159_n\u011bco() -> int:\n"
         "    return 1\n")

SOUBOR.write_bytes(OBSAH.encode("utf-8"))
SOUBOR2.write_bytes(OBSAH.encode("utf-8"))
try:
    r = subprocess.run([sys.executable, str(A / "hl-neanglicky-v-kodu.py"),
                        "--json", str(INV)], capture_output=True, cwd=str(WS))
    print("exit:", r.returncode)
    d = json.loads(INV.read_text(encoding="utf-8"))
    print("nalezy se 'h52':")
    for n in d["nalezy"]:
        if "h52" in n["soubor"]:
            print("   ", n["soubor"], n["radek"], n["kontext"], n["text"][:40])
    print("nepokryto s 'h52':",
          [x for x in d["nepokryto"] if "h52" in str(x)])
    print("vyloucene_artefakty:", d.get("vyloucene_artefakty"))
    print("netrackovane keys:", {k: len(v) for k, v in d.get("netrackovane", {}).items()})
    print("je _test-h52 v netrackovane?",
          any("_test-h52" in s for sez in d.get("netrackovane", {}).values() for s in sez))
finally:
    for p in (SOUBOR, SOUBOR2, INV):
        if p.exists():
            p.unlink()

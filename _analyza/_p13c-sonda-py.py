# -*- coding: utf-8 -*-
"""Sonda: dokáže vzor artefaktů vyloučit i NETRACKOVANÝ .py soubor?"""
import json
import pathlib
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"E:\Workspaces\forge-orchestra")
A = WS / "_analyza"
F = A / "_test-h52-untracked.py"
INV = A / "_sonda-inv.json"

F.write_bytes(("# -*- coding: utf-8 -*-\n"
               "def zm\u011b\u0159_n\u011bco() -> int:\n"
               "    return 1\n").encode("utf-8"))
try:
    r = subprocess.run([sys.executable, str(A / "hl-neanglicky-v-kodu.py"),
                        "--json", str(INV)], capture_output=True, cwd=str(WS))
    print("skener exit:", r.returncode)
    d = json.loads(INV.read_text(encoding="utf-8"))
    nt = [s for sez in d.get("netrackovane", {}).values() for s in sez]
    print("je _test-h52 v netrackovane?", any("_test-h52" in s for s in nt))
    print("je _test-h52 v nalezech?", any("_test-h52" in n["soubor"] for n in d["nalezy"]))
    print("pocet netrackovanych:", len(nt))
    print("vyloucene_artefakty:", d.get("vyloucene_artefakty"))
finally:
    for p in (F, INV):
        if p.exists():
            p.unlink()

"""P8d — dokonceni opravy cest v zivych nastrojich `_analyza/`.

P8b/P8c opravily LITERALY cest, ale minuly cesty SKLADANE pres `WS / "..."`,
ktere po presunu miri do neexistujicich mist:

  WS / "conductor" / ...   -> orchestra JE root repa -> WS / "conductor" / ...
  WS / "repo" / ...        -> zustava  WS / "repo" / ...
  WS / "tools" / ...       -> WS / "tools" / ...
  WS                       -> WS   (samotny rep)
  HRA /  ...      -> HRA / ...   (sourozenec, ne potomek)
  HRA            -> HRA

Dokud se to neopravi, brany hlasi `... neexistuje` — coz je SPRAVNE chovani
(rozbiti nahlas), ale znamena to, ze po presunu nemeri.

Pouziti: python p8d-oprava-skladanych-cest.py [--kontrola]
"""
from __future__ import annotations

import ast
import re
import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(r"E:\Workspaces\forge-orchestra\_analyza")
ZALOHA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\zaloha-p8d")

# poradi je zavazne (od nejkonkretejsiho)
NAHRADY = [
    ('HRA / ', 'HRA / '),
    ('HRA', 'HRA'),
    ('WS / "repo" /', 'WS / "repo" /'),
    ('WS / "conductor" /', 'WS / "conductor" /'),
    ('WS / "tools" /', 'WS / "tools" /'),
    ('WS / ', 'WS / '),
    ('WS', 'WS'),
    ('HRA.parent / ', 'HRA.parent / '),
    ('HRA.parent', 'HRA.parent'),
]


def main(argv: list[str]) -> int:
    kontrola = "--kontrola" in argv
    ZALOHA.mkdir(parents=True, exist_ok=True)
    zmenene, chyby = [], []
    for p in sorted(ANALYZA.glob("*.py")):
        t = p.read_text(encoding="utf-8")
        if "_REPO = _pl.Path" not in t:
            continue  # jen nastroje s novou hlavickou
        novy, pocet = t, 0
        for vzor, cim in NAHRADY:
            if vzor in novy:
                pocet += novy.count(vzor)
                novy = novy.replace(vzor, cim)
        if pocet == 0:
            continue
        # oprava poradi hlavicky: `from __future__` musi byt prvni
        radky = novy.splitlines(keepends=True)
        if radky and radky[0].startswith("from __future__"):
            i = 1
            while i < len(radky) and (radky[i].strip() == ""
                                      or radky[i].startswith("import")
                                      or radky[i].startswith("from ")
                                      or radky[i].startswith("#")):
                i += 1
            budouci = radky[0]
            novy = "".join(radky[1:i]) + budouci + "".join(radky[i:])
        if kontrola:
            print(f"  {p.name}: {pocet} nahrad (KONTROLA)")
            continue
        zal = ZALOHA / p.name
        shutil.copy2(p, zal)
        p.write_text(novy, encoding="utf-8", newline="")
        try:
            ast.parse(p.read_text(encoding="utf-8"))
        except SyntaxError as e:
            shutil.copy2(zal, p)
            print(f"  ✗ {p.name}: VRÁCENO ({e})")
            chyby.append(p.name)
            continue
        zmenene.append(p.name)
        print(f"  ✓ {p.name}: {pocet} nahrad")
    print(f"\nzmeneno: {len(zmenene)}, chyb: {len(chyby)}")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

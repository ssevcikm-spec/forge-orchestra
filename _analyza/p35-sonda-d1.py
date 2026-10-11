# -*- coding: utf-8 -*-
r"""P35 — SONDA D1 `state` (READ-ONLY): jaký tep má služba ULOŽENÝ.

PROČ VLASTNÍ SONDA a ne `p34-sonda-d1.py`: ta P34 píše do PEVNÉHO dokladu
`_analyza/p34-d1-state-vystup.txt` — a ten je gitignorovaný (tedy NEVRATNÝ).
Naměřeno v P35: spuštění cizího měřidla bez přesměrování výstupu přepsalo dva
doklady P34 (H166). P35 proto píše do VLASTNÍHO jména a doklady P34 nechává být.

Příkaz je TÝŽ jako v P34 (proto se dá porovnat): `wrangler d1 execute
forge-conductor --remote --command 'SELECT k, v FROM state'` — jen ke ČTENÍ.

Použití: python _analyza\p35-sonda-d1.py
Exit 0 = doklad zapsán; 2 = měření neproběhlo (a to se NESMÍ tvářit jako nula).
"""

import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
WRANGLER = WS / "conductor" / "node_modules" / "wrangler" / "bin" / "wrangler.js"
DB = "forge-conductor"
DOKLAD = WS / "_analyza" / "p35-d1-state-vystup.txt"


def main():
    if not WRANGLER.is_file():
        print("CHYBA: wrangler nenalezen (%s)" % WRANGLER)
        return 2
    r = subprocess.run(
        ["node", str(WRANGLER), "d1", "execute", DB, "--remote", "--json",
         "--command", "SELECT k, v FROM state"],
        cwd=str(WS / "conductor"), capture_output=True, timeout=300,
        env=dict(os.environ, PYTHONIOENCODING="utf-8"))
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    m = re.search(r"\[\s*\{.*\}\s*\]", out, re.S)
    if not m:
        print("CHYBA: ve výstupu wrangleru není JSON (exit=%d)" % r.returncode)
        print(out[:600])
        return 2
    data = json.loads(m.group(0))
    radky = (data[0] or {}).get("results", []) if data else []
    doklad = {
        "co": "D1 `state` — uložený tep cronu (čte ho /health)",
        "mereno": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "prikaz": "wrangler d1 execute %s --remote --command 'SELECT k, v FROM state'" % DB,
        "exit_wrangleru": r.returncode,
        "radky": radky,
        "meta": (data[0] or {}).get("meta") if data else None,
    }
    DOKLAD.write_bytes((json.dumps(doklad, ensure_ascii=False, indent=2) + "\n").encode("utf-8"))
    stav = {x["k"]: x["v"] for x in radky}
    print("D1 `state`: %s" % json.dumps(stav, ensure_ascii=False))
    print("doklad: %s (%d B)" % (DOKLAD.name, DOKLAD.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())

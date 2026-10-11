# -*- coding: utf-8 -*-
r"""p34-sonda-kotvy.py — TEST PŘÍČINY: rozbil offline harness MŮJ kód, nebo P33?

PROČ: `tools/test-tick-offline.mjs` má FALEŠNOU D1, která zná jen určité SQL.
Když kód conductora přidá dotaz, který fake DB nezná, throwne — a brány
(`validate-all`, `p29-a`, `p30-mutace`, `p32-mutace`) zčervenají. Otázka je,
ČÍ změna to způsobila. Sonda proto:
  1. odloží MŮJ `conductor/src/index.ts` mimo strom,
  2. zapíše do něj verzi z `HEAD` (stav před P34) — bajty, ne PowerShellem,
  3. spustí offline harness NAD STAVEM PŘED P34 a změří čítač,
  4. vrátí MŮJ soubor zpět (bajt na bajt) a spustí harness znovu,
  5. oba čítače vypíše — rozdíl je odpověď.

Použití: python _analyza\p34-sonda-kotvy.py
"""
import hashlib
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = WS / "tools" / "git.cmd"
SOUBOR = WS / "conductor" / "src" / "index.ts"
ODLOZENY = WS / "_analyza" / "p34-index-moje-odlozeno.ts"
ENV = dict(__import__("os").environ, PYTHONIOENCODING="utf-8")


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


def harness():
    r = subprocess.run(["node", str(WS / "tools" / "test-tick-offline.mjs")], cwd=str(WS),
                       capture_output=True, timeout=1800, env=ENV)
    out = ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")
    m = list(re.finditer(r"VYSLEDEK:\s*(\d+) kontrol,\s*(\d+) CHYB", out))
    chyby = [x.strip() for x in out.splitlines() if "CHYBA" in x]
    return r.returncode, (m[-1].groups() if m else None), chyby[:6], out


def main():
    pred = sha(SOUBOR)
    ODLOZENY.write_bytes(SOUBOR.read_bytes())
    print("můj soubor odložen: %s (sha %s)" % (ODLOZENY.name, pred[:12]))
    r = subprocess.run([str(GIT), "-C", str(WS), "show", "HEAD:conductor/src/index.ts"],
                       capture_output=True, shell=True, timeout=300)
    stary = r.stdout
    if not stary:
        print("CHYBA: z gitu se nepodařilo přečíst HEAD:conductor/src/index.ts")
        return 2
    SOUBOR.write_bytes(stary)
    print("zapsán stav z HEAD (%d B, sha %s)" % (len(stary), sha(SOUBOR)[:12]))
    try:
        kod, citac, chyby, _ = harness()
        print("=== NAD STAVEM PŘED P34 (z HEAD): exit=%d, čítač=%s" % (kod, citac))
        for c in chyby:
            print("   %s" % c[:150])
    finally:
        SOUBOR.write_bytes(ODLOZENY.read_bytes())
    print("můj soubor vrácen: sha %s (původní %s) → %s"
          % (sha(SOUBOR)[:12], pred[:12], "SHODA" if sha(SOUBOR) == pred else "ROZDÍL!"))
    kod, citac, chyby, out = harness()
    print("=== NAD STAVEM P34 (můj kód): exit=%d, čítač=%s" % (kod, citac))
    for c in chyby:
        print("   %s" % c[:150])
    (WS / "_analyza" / "p34-sonda-kotvy-vystup.txt").write_bytes(out.encode("utf-8"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

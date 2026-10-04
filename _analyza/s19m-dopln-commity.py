# -*- coding: utf-8 -*-
r"""Doplní do `HANDOFF.md` §19.1 seznam VŠECH commitů, které push obsahoval.

PROČ: §19.1 vznikl po prvním pushi (`593e25c`, `c40bdd5`) a zapsal dva commity.
Po něm následovaly **tři další** (`1e3925e`, `cc53c47`, `34667ad`) — všechny
pushnuté. Nechat v dokumentu jen první dva znamená, že **dokument tvrdí o stavu
něco, co už neplatí** (`AGENTS.md`: „tvrzení o stavu se ověřuje živě").

Použití:  python _analyza\s19m-dopln-commity.py [--zapis]
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv


def log(repo: pathlib.Path, n: int = 6) -> list:
    r = subprocess.run([str(GIT), "-C", str(repo), "log", "--oneline", "-%d" % n],
                       capture_output=True)
    return [l.strip() for l in r.stdout.decode("utf-8", "replace").splitlines() if l.strip()]


orch = log(WS / "orchestra")
hra = log(WS / "games" / "uo-shadows", 3)
print("orchestra (posledních %d):" % len(orch))
for l in orch:
    print("   %s" % l[:80])
print("uo-shadows:")
for l in hra:
    print("   %s" % l[:80])

text = HANDOFF.read_text(encoding="utf-8")

# Vloží se za odstavec, který popisuje push — hledá se na krátké ASCII kotvě.
KOTVA = "**Co se tím uzavřelo:**"
assert text.count(KOTVA) == 1, "kotva 'Co se tím uzavřelo' není právě 1×"

DOPLNENI = (
    "**Všechny commity, které push obsahoval** (dopsáno 2. 10. 2026 ve 13:5x UTC,\n"
    "když po prvním zápisu přišly další — `AGENTS.md`: tvrzení o stavu se ověřuje živě):\n\n"
    "| Repo | Commity |\n|---|---|\n"
    "| `orchestra` | %s |\n"
    "| `uo-shadows` | %s |\n\n"
    % (" · ".join("`%s`" % l.split()[0] for l in orch[:5]),
       " · ".join("`%s`" % l.split()[0] for l in hra[:2]))
)

i = text.find(KOTVA)
novy = text[:i] + DOPLNENI + text[i:]
assert novy != text, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
assert novy.count("Všechny commity, které push obsahoval") == 1
# POJISTKA: v doplnění musí být i nejnovější commit orchestra.
assert orch[0].split()[0] in novy, "v doplnění chybí nejnovější commit orchestra"
assert novy.startswith(text[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"

print()
print("  doplněn seznam commitů do §19.1")
if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print("  ZAPSÁNO: %d -> %d B"
          % (len(text.encode("utf-8")), len(novy.encode("utf-8"))))
else:
    print("  (dry-run — spusť s --zapis)")

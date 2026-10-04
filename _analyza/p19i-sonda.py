# -*- coding: utf-8 -*-
r"""Sonda: co přesně počítá `radky` v `p19i-co-zmensit.py`?

Podezření: scénář „kdyby CONVENTIONS.md byl menší" hlásí nemožná čísla
(u prázdného CONVENTIONS.md „12 z 21"). Vypíšu skutečné hodnoty.
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HRA = WS / "games" / "uo-shadows"
LIMIT = 8000
OBAL = 5357

road = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
grains = road.get("grains") or road.get("tasks") or []
index = {g.get("id"): g for g in grains}
z_conv = len((HRA / "CONVENTIONS.md").read_text(encoding="utf-8"))
t_conv = int(z_conv / 3.0)


def zn(rel: str) -> int:
    p = HRA / rel
    return len(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else 0


def zbytek(g) -> int:
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = sorted({f for d in (g.get("depends_on") or [])
                   for f in ((index.get(d) or {}).get("owns") or [])
                   if (HRA / f).is_file()})
    return (z_conv + sum(zn(f) for f in owns) + sum(zn(f) for f in deps)
            + len(str(g.get("prompt") or "")))


radky = sorted(((g.get("id"), int(zbytek(g) / 3.0)) for g in grains),
               key=lambda x: x[1])

print("z_conv = %d znaků, t_conv = %d tokenů, OBAL = %d" % (z_conv, t_conv, OBAL))
print()
print("%-22s %10s %10s %10s" % ("granule", "zbytek(t)", "t_conv", "zbytek - t_conv"))
for gid, t in radky[:6]:
    print("%-22s %10d %10d %10d" % (gid, t, t_conv, t - t_conv))

print()
print("scénáře (spravny vzorec: (zbytek - t_conv) + cil_t + OBAL <= LIMIT):")
for cil_znaku in (z_conv, 6000, 3000, 1500, 0):
    cil_t = int(cil_znaku / 3.0)
    pevna = cil_t + OBAL
    vejde = [(gid, (t - t_conv) + pevna) for gid, t in radky
             if (t - t_conv) + pevna <= LIMIT]
    print("  CONVENTIONS %5d znaků (%4d t.), pevná %5d  → %2d z %d"
          % (cil_znaku, cil_t, pevna, len(vejde), len(radky)))
    for gid, celkem in vejde[:3]:
        print("        %-22s %d" % (gid, celkem))

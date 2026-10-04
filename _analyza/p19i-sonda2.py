# -*- coding: utf-8 -*-
r"""Sonda 2: proč se `p19i-co-zmensit.py` a `p19i-sonda.py` ROZCHÁZEJÍ?

`p19i-sonda.py` (přepsaný vzorec) hlásí u prázdného CONVENTIONS.md **12 z 21**,
ale `zbytek - t_conv + OBAL` pro nejmenší granuli je **5 693** — což je POD
limitem 8 000, takže by se vejít MĚLA. Zdá se tedy, že **sonda počítá dobře**
a můj předpoklad („nevejde se ani s prázdným CONVENTIONS") je špatný.

Klíčová kontrola: **co je `own` část granulе v TOKENECH** (bez CONVENTIONS)?
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


print("CONVENTIONS.md: %d znaků = %d tokenů" % (z_conv, t_conv))
print("OBAL (dopočet):  %d tokenů" % OBAL)
print("LIMIT:           %d tokenů" % LIMIT)
print()
print("%-22s %8s %8s %8s %8s   %s" % ("granule", "own zn.", "own tok.", "+CONV", "+OBAL", "vejde se?"))
for g in sorted(grains, key=lambda x: x.get("id")):
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = sorted({f for d in (g.get("depends_on") or [])
                   for f in ((index.get(d) or {}).get("owns") or [])
                   if (HRA / f).is_file()})
    z_own = (sum(zn(f) for f in owns) + sum(zn(f) for f in deps)
             + len(str(g.get("prompt") or "")))
    t_own = int(z_own / 3.0)
    s_conv = t_own + t_conv
    s_obal = s_conv + OBAL
    print("%-22s %8d %8d %8d %8d   %s"
          % (g.get("id"), z_own, t_own, s_conv, s_obal,
             "ANO" if s_obal <= LIMIT else "NE"))

print()
print("A) S DNEŠNÍM CONVENTIONS.md (pevná %d):" % (t_conv + OBAL))
n = sum(1 for g in grains
        if int((sum(zn(f) for f in (g.get("owns") or []) if (HRA / f).is_file())
                + sum(zn(f) for d in (g.get("depends_on") or [])
                      for f in ((index.get(d) or {}).get("owns") or [])
                      if (HRA / f).is_file())
                + len(str(g.get("prompt") or ""))) / 3.0) + t_conv + OBAL <= LIMIT)
print("   vejde se: %d z %d" % (n, len(grains)))

print()
print("B) KDYBY CONVENTIONS.md NEBYL VŮBEC (pevná = jen obal %d):" % OBAL)
n2 = 0
for g in grains:
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = sorted({f for d in (g.get("depends_on") or [])
                   for f in ((index.get(d) or {}).get("owns") or [])
                   if (HRA / f).is_file()})
    t_own = int((sum(zn(f) for f in owns) + sum(zn(f) for f in deps)
                 + len(str(g.get("prompt") or ""))) / 3.0)
    if t_own + OBAL <= LIMIT:
        n2 += 1
print("   vejde se: %d z %d" % (n2, len(grains)))
print()
print("→ ZÁVĚR: i bez CONVENTIONS.md se vejde %d granulí, protože obal sám" % n2)
print("  (%d) plus vlastní část granulе musí být pod %d." % (OBAL, LIMIT))

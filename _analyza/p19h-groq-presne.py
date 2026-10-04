# -*- coding: utf-8 -*-
r"""P19h — PŘESNÁ odpověď: vejde se do Groqova limitu NĚJAKÁ granule?

PROČ DRUHÝ SKRIPT: `p19g` použil pro Aiderův systémový prompt **ODHAD**
(6 500 znaků). Pak ho dopočítal z **reálného běhu** — a vyšlo **~5 357 tokenů**,
tedy **2,5× víc**, než odhad. S odhadem „vejde se 10 granulí", se skutečným
obalem **ani jedna**. **Rozdíl je tak velký, že mění odpověď** — a to je přesně
důvod, proč se má měřit, ne odhadovat.

⚠ **PŘIZNANÁ MEZ:** obal **5 357 tokenů** je **DOPOČET z jednoho běhu**
(`entity.player.api`, Groq 14 398 − moje znaková část 9 041). Není to měření
obalu samotného — je to **zbytek po odečtení**. Může v sobě mít i to, co
nepočítám (obal chatu, main.md, atd.). Proto se počítá **dvěma způsoby** a
**oba se vypíšou**; rozhodnutí se dělá podle toho **většího**.

Použití:  python _analyza\p19h-groq-presne.py
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HRA = WS / "games" / "uo-shadows"
LIMIT = 8000

OBAL_ODHAD_T = 2166      # tokenů: 6 500 znaků ÷ 3 (původní odhad)
OBAL_DOPOCET_T = 5357    # tokenů: dopočteno z reálného běhu #146 (viz P19g)

road = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
grains = road.get("grains") or road.get("tasks") or []
index = {g.get("id"): g for g in grains}
Z_CONV = len((HRA / "CONVENTIONS.md").read_text(encoding="utf-8"))
T_CONV = int(Z_CONV / 3.0)


def zn(rel: str) -> int:
    p = HRA / rel
    return len(p.read_text(encoding="utf-8", errors="replace")) if p.is_file() else 0


def zbytek(g) -> int:
    """Znaky granule: CONVENTIONS.md + --read závislosti + --file owns + prompt."""
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = sorted({f for d in (g.get("depends_on") or [])
                   for f in ((index.get(d) or {}).get("owns") or [])
                   if (HRA / f).is_file()})
    return (Z_CONV + sum(zn(f) for f in owns) + sum(zn(f) for f in deps)
            + len(str(g.get("prompt") or "")))


radky = []
for g in grains:
    z = zbytek(g)
    t_zbytek = int(z / 3.0)
    radky.append({
        "id": g.get("id"), "size_lines": g.get("size_lines"),
        "t_zbytek": t_zbytek,
        "odhad": t_zbytek + OBAL_ODHAD_T,
        "dopocet": t_zbytek + OBAL_DOPOCET_T,
    })
radky.sort(key=lambda r: r["dopocet"])

print("=" * 78)
print("P19h — PŘESNÁ ODPOVĚĎ: vejde se NĚJAKÁ granule do %d tokenů?" % LIMIT)
print("=" * 78)
print("  CONVENTIONS.md (--read, PEVNÉ):        %5d znaků  ≈ %5d tokenů" % (Z_CONV, T_CONV))
print("  Aiderův systémový prompt — ODHAD:               ≈ %5d tokenů" % OBAL_ODHAD_T)
print("  Aiderův systémový prompt — DOPOČET z běhu:      ≈ %5d tokenů" % OBAL_DOPOCET_T)
print()
print("  pevná část (CONVENTIONS + obal):")
print("     s ODHADEM:   ≈ %5d tokenů  → %s limitu"
      % (T_CONV + OBAL_ODHAD_T,
         "POD" if T_CONV + OBAL_ODHAD_T < LIMIT else "NAD"))
print("     s DOPOČTEM:  ≈ %5d tokenů  → %s limitu  ← ROZHODUJÍCÍ"
      % (T_CONV + OBAL_DOPOCET_T,
         "POD" if T_CONV + OBAL_DOPOCET_T < LIMIT else "NAD"))

print()
print("A) VŠECHNY GRANULE SEŘAZENÉ OD NEJMENŠÍ")
print("-" * 78)
print("  %-22s %-10s %10s %10s  %s" % ("granule", "size_lines", "s odhadem", "s dopoctem", "vejde se?"))
for r in radky:
    o = "ANO" if r["odhad"] <= LIMIT else "NE"
    d = "ANO" if r["dopocet"] <= LIMIT else "NE"
    print("  %-22s %-10s %10d %10d  odhad=%s  dopocet=%s"
          % (r["id"], str(r["size_lines"] or "—"), r["odhad"], r["dopocet"], o, d))

pod_odhadem = [r for r in radky if r["odhad"] <= LIMIT]
pod_dopoctem = [r for r in radky if r["dopocet"] <= LIMIT]
print()
print("  vejde se s ODHADEM:   %2d z %d" % (len(pod_odhadem), len(radky)))
print("  vejde se s DOPOČTEM:  %2d z %d   ← podle tohohle se rozhoduje"
      % (len(pod_dopoctem), len(radky)))

print()
print("B) CO BY SE MUSELO ZMENŠIT, ABY SE GRANULE VEŠLY")
print("-" * 78)
nejmensi = radky[0]
print("  nejmenší granule: %s → %d tokenů (dopočet)" % (nejmensi["id"], nejmensi["dopocet"]))
print("  její vlastní část (bez pevné): %d tokenů" % nejmensi["t_zbytek"])
print("  → aby se vešla, musí pevná část klesnout pod %d tokenů" % (LIMIT - nejmensi["t_zbytek"]))
print("     (dnes je %d) — tedy o %d tokenů = %.0f %%"
      % (T_CONV + OBAL_DOPOCET_T, T_CONV + OBAL_DOPOCET_T - (LIMIT - nejmensi["t_zbytek"]),
         100.0 * (1 - (LIMIT - nejmensi["t_zbytek"]) / float(T_CONV + OBAL_DOPOCET_T))))
print()
for cil_obal in (2166, 3000, 1500, 0):
    pevna = T_CONV + cil_obal
    vejde = sum(1 for r in radky if r["t_zbytek"] + pevna <= LIMIT)
    print("  kdyby byl obal %5d tokenů (pevná %5d) → vešlo by se %2d z %d granulí"
          % (cil_obal, pevna, vejde, len(radky)))

print()
print("=" * 78)
print("ODPOVĚĎ")
print("=" * 78)
if pod_dopoctem:
    print("  Do limitu se vejde %d granulí (podle dopočtu): %s"
          % (len(pod_dopoctem), ", ".join(r["id"] for r in pod_dopoctem)))
else:
    print("  NE — podle DOPOČTU se nevejde ANI JEDNA granule.")
    print("  Nejmenší (%s, size_lines=%s) má %d tokenů, limit je %d."
          % (nejmensi["id"], nejmensi["size_lines"] or "—", nejmensi["dopocet"], LIMIT))
    print("  A to i kdyby granule neměla ANI JEDEN soubor a ANI prompt:")
    print("     pevná část (CONVENTIONS.md + obal) = %d tokenů = %.0f %% limitu."
          % (T_CONV + OBAL_DOPOCET_T, 100.0 * (T_CONV + OBAL_DOPOCET_T) / LIMIT))
print()
print("  VÝHRADA: %d tokenů obalu je DOPOČET, ne měření obalu samého."
      % OBAL_DOPOCET_T)
print("  Kdyby byl obal jen %d tokenů (původní odhad), vešlo by se %d granulí."
      % (OBAL_ODHAD_T, len(pod_odhadem)))
print("  Přesné číslo obalu dá jediné: spustit Aidera a přečíst jeho vlastní")
print("  \"Tokens: … sent\" — což v logu #146 NEBYLO (naměřeno 0 výskytů).")

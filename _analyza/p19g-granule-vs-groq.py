# -*- coding: utf-8 -*-
r"""P19g — vejde se NĚKTERÁ granule do Groqova limitu 8 000 tokenů?

OTÁZKA UŽIVATELE (2. 10. 2026): „Groq se nedá použít tedy ani na menší granule
nebo sekvenčně?"

CO SE MĚŘÍ: pro **každou** granuli v roadmapě se spočítá **přesně to, co jde do
chatu Aideru** (podle `agent.yml:224–235`):

    --read CONVENTIONS.md          obsah souboru
    --read <owns závislých granul> obsah těch souborů, které existují
    --file <owns téhle granule>    obsah těch souborů
    --message "<prompt granule>"   text promptu

…a k tomu **pevný obal**: Aiderův systémový prompt. Ten se **nedá změřit
offline** — bere se proto **dvěma způsoby** a oba se vypíšou:
  * ODHAD 2 166 tokenů (= 6 500 znaků ÷ 3) — konzervativní,
  * DOPOČET z reálného běhu: Groq naměřil **14 400** pro granuli, jejíž ostatní
    části dají dohromady X → obal ≈ 14 400 − X (to je **naměřený** údaj).

„SEKVENČNĚ" se odpovídá taky: limit je **`Request too large`** (na JEDEN
request), ne minutová kvóta — takže **dělení requestu na části nepomůže**,
protože Aider posílá kontext v jednom requestu. Ověřeno v `p19-sonda-groq.py`.

Použití:  python _analyza\p19g-granule-vs-groq.py
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HRA = WS / "games" / "uo-shadows"
LIMIT = 8000

# Naměřeno Groqem v běhu #146 (litellm.RateLimitError) — tři různá čísla.
GROQ_NAMERENO = [14398, 14377, 14402]


def tokeny(znaku: int) -> int:
    """Odhad tokenů ze znaků. ⚠ NENÍ to tokenizer — je to **dolní odhad**
    (naměřeno: znaky÷3 dalo 11 207, Groq naměřil ~14 400 pro tutéž granuli).
    Používá se proto jen na POROVNÁNÍ granul mezi sebou, ne jako absolutní číslo.
    """
    return int(znaku / 3.0)


road = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
grains = road.get("grains") or road.get("tasks") or []
index = {g.get("id"): g for g in grains}

conv = (HRA / "CONVENTIONS.md").read_text(encoding="utf-8")
Z_CONV = len(conv)
OBAL_ODHAD = 6500    # znaků; Aiderův systémový prompt — ODHAD, viz docstring


def znaky_souboru(rel: str) -> int:
    p = HRA / rel
    if not p.is_file():
        return 0
    return len(p.read_text(encoding="utf-8", errors="replace"))


print("=" * 78)
print("P19g — VEJDE SE NĚKTERÁ GRANULE DO GROQOVA LIMITU %d TOKENŮ?" % LIMIT)
print("=" * 78)
print("  CONVENTIONS.md (pevné, --read): %d znaků ≈ %d tokenů"
      % (Z_CONV, tokeny(Z_CONV)))
print("  Aiderův systémový prompt: ODHAD %d znaků ≈ %d tokenů"
      % (OBAL_ODHAD, tokeny(OBAL_ODHAD)))
print("  pevná část CELKEM (odhad): %d znaků ≈ %d tokenů"
      % (Z_CONV + OBAL_ODHAD, tokeny(Z_CONV + OBAL_ODHAD)))

radky = []
for g in grains:
    gid = g.get("id")
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = []
    for d in g.get("depends_on") or []:
        zav = index.get(d) or {}
        for f in zav.get("owns") or []:
            if (HRA / f).is_file():
                deps.append(f)
    deps = sorted(set(deps))

    z_owns = sum(znaky_souboru(f) for f in owns)
    z_deps = sum(znaky_souboru(f) for f in deps)
    z_prompt = len(str(g.get("prompt") or ""))
    celkem = Z_CONV + OBAL_ODHAD + z_owns + z_deps + z_prompt
    radky.append({
        "id": gid, "size_lines": g.get("size_lines"), "model": g.get("model"),
        "owns": len(owns), "deps": len(deps), "z_owns": z_owns,
        "z_deps": z_deps, "z_prompt": z_prompt, "znaku": celkem,
        "tokenu": tokeny(celkem), "vejde": tokeny(celkem) <= LIMIT,
    })

radky.sort(key=lambda r: r["tokenu"])
print()
print("A) OD NEJMENŠÍ GRANULE — vejde se do %d tokenů?" % LIMIT)
print("-" * 78)
print("  %-22s %-10s %6s %6s %7s %8s  %s"
      % ("granule", "size_lines", "owns", "deps", "znaků", "≈tokenů", "vejde se?"))
for r in radky:
    print("  %-22s %-10s %6d %6d %7d %8d  %s"
          % (r["id"], str(r["size_lines"] or "—"), r["owns"], r["deps"],
             r["znaku"], r["tokenu"], "ANO" if r["vejde"] else "NE"))

vejde = [r for r in radky if r["vejde"]]
print()
print("  granuli celkem: %d · vejde se do %d tokenů: %d"
      % (len(radky), LIMIT, len(vejde)))

# ── B) co je NEJMENŠÍ MOŽNÝ vstup (nula souborů, prázdný prompt) ────────────
print()
print("B) NEJMENŠÍ MOŽNÝ VSTUP (kdyby granule neměla ani soubor, ani prompt)")
print("-" * 78)
print("  pevná část (CONVENTIONS.md + obal, odhad): %d tokenů"
      % tokeny(Z_CONV + OBAL_ODHAD))
print("  → i tak je to %.0f %% limitu. Obal se ZMNIT nedá, CONVENTIONS.md ano."
      % (100.0 * tokeny(Z_CONV + OBAL_ODHAD) / LIMIT))
print("  CONVENTIONS.md sám: %d tokenů (%.0f %% limitu)"
      % (tokeny(Z_CONV), 100.0 * tokeny(Z_CONV) / LIMIT))

# ── C) DOPOČET obalu z REÁLNÉHO běhu (naměřené číslo, ne odhad) ─────────────
print()
print("C) DOPOČET OBALU Z REÁLNÉHO BĚHU (naměřeno Groqem: %s)" % GROQ_NAMERENO)
print("-" * 78)
cil = index.get("entity.player.api")
if cil:
    owns = [f for f in (cil.get("owns") or []) if (HRA / f).is_file()]
    deps = []
    for d in cil.get("depends_on") or []:
        zav = index.get(d) or {}
        for f in zav.get("owns") or []:
            if (HRA / f).is_file():
                deps.append(f)
    z_ostatni = (Z_CONV + sum(znaky_souboru(f) for f in owns)
                 + sum(znaky_souboru(f) for f in sorted(set(deps)))
                 + len(str(cil.get("prompt") or "")))
    print("  granule entity.player.api, všechno KROMĚ systémového promptu:")
    print("     %.0f znaků ≈ %d tokenů" % (z_ostatni, tokeny(z_ostatni)))
    for nam in GROQ_NAMERENO:
        print("     Groq naměřil %d  →  obal ≈ %d tokenů (%.0f znaků)"
              % (nam, nam - tokeny(z_ostatni), (nam - tokeny(z_ostatni)) * 3.0))
    obal_dopocet = GROQ_NAMERENO[0] - tokeny(z_ostatni)
    print()
    print("  → SKUTEČNÝ obal je ~%d tokenů, ne odhad %d. Pevná část je tedy"
          % (obal_dopocet, tokeny(OBAL_ODHAD)))
    print("     ~%d tokenů = %.0f %% limitu 8 000."
          % (obal_dopocet + tokeny(Z_CONV), 100.0 * (obal_dopocet + tokeny(Z_CONV)) / LIMIT))

# ── D) odpověď na „sekvenčně" ──────────────────────────────────────────────
print()
print("D) ŠLO BY TO SEKVENČNĚ (rozdělit request na části)?")
print("-" * 78)
print("  Limit je `Request too large` — tedy na JEDEN request, ne minutová kvóta.")
print("  Aider posílá CELÝ kontext (CONVENTIONS.md + soubory + prompt) v JEDNOM")
print("  requestu. Rozdělení souborů do víc běhů by znamenalo, že agent nevidí")
print("  celek — a přesně na tom padaly granulе dřív („add the file to the chat\").")
print("  → SEKVENČNĚ to nejde bez změny zadání granulе.")

print()
print("=" * 78)
print("ODPOVĚĎ")
print("=" * 78)
if vejde:
    print("  ANO — do limitu se vejde %d granuli: %s"
          % (len(vejde), ", ".join(r["id"] for r in vejde)))
else:
    print("  NE — do limitu se nevejde ANI JEDNA granule (nejmenší má %d tokenů)."
          % (radky[0]["tokenu"] if radky else -1))
    print("  Nejpříznivější je `%s` s %d tokeny — a to je pořád o %d %% nad limitem."
          % (radky[0]["id"], radky[0]["tokenu"],
             round(100.0 * radky[0]["tokenu"] / LIMIT) - 100))

# -*- coding: utf-8 -*-
r"""P19i — CO KONKRÉTNĚ by se muselo zmenšit, aby Groq šel použít?

P19h dal odpověď „nevejde se ani jedna granule": pevná část (CONVENTIONS.md +
obal Aideru) je **9 196 tokenů** a limit je **8 000**. Tenhle skript dopočítá
**kolik** by muselo ubrat — a **u čeho**, protože to jsou různé páky:

  * `CONVENTIONS.md` — soubor v repu, dá se upravit (je to `--read`, 3 839 t.)
  * obal Aideru — NEDÁ se upravit (je v nástroji)

⚠ Všechna čísla jsou **odhady ze znaků** (znaky ÷ 3) s výjimkou obalu, který je
**dopočet z reálného běhu** (5 357 t.). Skript to u každého čísla řekne.

Použití:  python _analyza\p19i-co-zmensit.py
"""

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HRA = WS / "games" / "uo-shadows"
LIMIT = 8000
OBAL = 5357              # tokenů — DOPOČET z běhu #146

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


# POZN.: `radky` (celkové vstupy včetně pevné části) se už nepoužívá — viz `vlastni`.

print("=" * 78)
print("P19i — CO BY SE MUSELO ZMENŠIT, ABY SE GRANULE VEŠLY DO %d TOKENŮ" % LIMIT)
print("=" * 78)
print("  Granule mají DVĚ složky:")
print("    A) PEVNOU  = CONVENTIONS.md (%d t., měřeno ze znaků) + obal Aideru (%d t., dopočet)"
      % (t_conv, OBAL))
print("       → dohromady %d tokenů (to platí pro KAŽDOU granuli)" % (t_conv + OBAL))
print("    B) VLASTNÍ = soubory granule + její prompt (mění se granule od granule)")

# ── VLASTNÍ část granulе (bez CONVENTIONS.md i bez obalu) ───────────────────
# ⚠ SEM jsem se nejdřív spletl: `zbytek(g)` CONVENTIONS.md OBSAHUJE, takže
# rozdíl `zbytek - t_conv` sice vypadá jako „vlastní část", ale je to
# **vlastní část v TOKENECH** — a ta je u malých granulí **stovky**, ne tisíce
# (core.attributes: 1 007 znaků = 335 tokenů). Naměřeno `p19i-sonda2.py`.
def vlastni_tokenu(g) -> int:
    owns = [f for f in (g.get("owns") or []) if (HRA / f).is_file()]
    deps = sorted({f for d in (g.get("depends_on") or [])
                   for f in ((index.get(d) or {}).get("owns") or [])
                   if (HRA / f).is_file()})
    return int((sum(zn(f) for f in owns) + sum(zn(f) for f in deps)
                + len(str(g.get("prompt") or ""))) / 3.0)


vlastni = sorted(((g.get("id"), vlastni_tokenu(g)) for g in grains), key=lambda x: x[1])
nejmensi_id, nejmensi_t = vlastni[0]

print()
print("A) PÁKA 1: ZMENŠIT `CONVENTIONS.md` (jediná, kterou jde ovlivnit)")
print("-" * 78)
print("  dnes: %d znaků = %d tokenů (%.0f %% limitu)" % (z_conv, t_conv, 100.0 * t_conv / LIMIT))
print("  vlastní část NEJMENŠÍ granulе (%s): %d tokenů" % (nejmensi_id, nejmensi_t))
print()
print("  %-30s %8s %8s  %s" % ("kdyby CONVENTIONS.md měl", "tokenů", "pevná", "vešlo by se"))
for cil_znaku in (z_conv, 9000, 6000, 4500, 3000, 1500, 0):
    cil_t = int(cil_znaku / 3.0)
    pevna = cil_t + OBAL
    vejde = sum(1 for _, t in vlastni if t + pevna <= LIMIT)
    print("  %-30s %8d %8d  %2d z %d"
          % ("%d znaků%s" % (cil_znaku, " (dnes)" if cil_znaku == z_conv else ""),
             cil_t, pevna, vejde, len(vlastni)))

# Kde je zlom: nejmenší granule se vejde, když pevná <= LIMIT - vlastní
max_pevna = LIMIT - nejmensi_t
max_conv_t = max_pevna - OBAL
print()
print("  Zlom pro NEJMENŠÍ granuli (%s, %d t.): pevná část smí být max %d tokenů."
      % (nejmensi_id, nejmensi_t, max_pevna))
if max_conv_t > 0:
    print("  → CONVENTIONS.md smí mít max %d tokenů ≈ **%d znaků** (dnes %d)."
          % (max_conv_t, max_conv_t * 3, z_conv))
    print("     To je **%.0f %% dnešní velikosti** — tedy zmenšit na %.0f %%."
          % (100.0 * max_conv_t * 3 / z_conv, 100.0 * max_conv_t * 3 / z_conv))
else:
    print("  → CONVENTIONS.md by musel mít NEGATIVNÍ velikost — nejde.")
print()
print("  POZOR: to je zlom pro tu NEJMENŠÍ. Ostatní granulе mají vlastní část")
print("  větší, takže potřebují CONVENTIONS.md menší ještě víc:")
for cil_znaku in (3000, 1500):
    cil_t = int(cil_znaku / 3.0)
    pevna = cil_t + OBAL
    vejde = [(gid, t) for gid, t in vlastni if t + pevna <= LIMIT]
    print("     při %d znacích (%d t., pevná %d) → %d z %d"
          % (cil_znaku, cil_t, pevna, len(vejde), len(vlastni)))

print()
print("B) PÁKA 2: ZMENŠIT OBAL AIDERU — **NEDÁ SE**")
print("-" * 78)
print("  Obal je uvnitř nástroje (Aiderův systémový prompt + obal chatu).")
print("  Z workflow se dá ovlivnit jen `--map-tokens 0` (už je nastaveno,")
print("  `agent.yml:231`) — víc pák tam není.")

print()
print("C) PÁKA 3: ZMĚNIT GRANULI (aby měla méně souborů) — **POMŮŽE JEN U MALÝCH**")
print("-" * 78)
print("  Vlastní část granulе je dnes %d–%d tokenů (nejmenší %s, největší engine.shell)."
      % (vlastni[0][1], vlastni[-1][1], vlastni[0][0]))
print("  I ta NEJMENŠÍ potřebuje pevnou část pod %d tokenů — dnes je %d."
      % (LIMIT - vlastni[0][1], t_conv + OBAL))

print()
print("=" * 78)
print("ODPOVED NA OTazku: MENSI GRANULE NEBO SEKVENCne?")
print("=" * 78)
print("  MENŠÍ GRANULE SAMOTNÉ: **nepomohou.**")
print("     Nejmenší granule (%s) má vlastní část %d t., ale PEVNÁ část je %d t."
      % (vlastni[0][0], vlastni[0][1], t_conv + OBAL))
print("     → dohromady %d t. = %.0f %% limitu %d."
      % (vlastni[0][1] + t_conv + OBAL,
         100.0 * (vlastni[0][1] + t_conv + OBAL) / LIMIT, LIMIT))
print()
print("  SEKVENČNĚ: **nepomůže.** Limit je `Request too large` na JEDEN request,")
print("     ne minutová kvóta — Aider posílá celý kontext naráz a rozdělení")
print("     by znamenalo, že agent nevidí celek (a přesně na tom padaly granulе).")
print()
print("  CO POMŮŽE (a je to jediná páka): **ZMENŠIT `CONVENTIONS.md`**")
print("     je `--read` do KAŽDÉHO běhu, takže platí pro všechny granulе.")
if max_conv_t > 0:
    print("     Aby se vešla nejmenší granule, smí mít max %d znaků (dnes %d)."
          % (max_conv_t * 3, z_conv))
    print("     Při 3 000 znacích by se vešlo %d z %d granulí."
          % (sum(1 for _, t in vlastni if t + int(3000 / 3.0) + OBAL <= LIMIT), len(vlastni)))
else:
    print("     ⚠ Ani to nestačí: i PRÁZDNÝ CONVENTIONS.md nechává pevnou část")
    print("     %d t. proti limitu %d — obal Aideru sám je větší." % (OBAL, LIMIT))

print()
print("  ⚠ VÝHRADA: obal %d tokenů je **DOPOČET z jednoho běhu**, ne měření" % OBAL)
print("     obalu samého (viz `p19h-groq-presne.py`). Přesné číslo dá jen běh")
print("     Aidera s vypsaným \"Tokens: … sent\" — což v logu #146 NEBYLO.")

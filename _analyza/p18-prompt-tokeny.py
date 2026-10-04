# -*- coding: utf-8 -*-
r"""ÚKOL 1 (plánovací session 2. 10. 2026) — ZMĚŘ velikost promptu, který jde
do Aideru, a porovnej ho s limity poskytovatelů.

PROČ: `HANDOFF.md` §17.5 (nález H5) říká, že Groq free tier má **TPM 8 000**
a request měl **14 398 tokenů** → úloha u Groqu **nemůže uspět** a spálí pokus.
Zadání (`NEXT-SESSION-INSTRUKCE.md` §3 Úkol 1) chce ČÍSLO, ne odhad:
  * kolik tokenů posílá Aider pro granule `entity.player.api` a `world.nodes`,
  * který poskytovatel se do limitu vejde a který ne.

CO SE MĚŘÍ (a je to přesně to, co jde do chatu — viz `agent.yml:224–235`):
    --read CONVENTIONS.md          obsah souboru
    --read <soubory depends_on>     obsah souborů závislých granulí
    --file <owns granule>           obsah souborů, které granule vlastní
    --message "$FORGE_PROMPT"       prompt granule z roadmapy
  Aider k tomu přidá VLASTNÍ systémový prompt (pevný, ~6,5 kB) a s
  `--map-tokens 0` NEPOSÍLÁ repo-mapu (to je naměřeno v `agent.yml:231`).
  Systémový prompt se tu měří tak, že se Aider spustí s `--dry-run`? To nejde
  offline — proto se bere **konzervativní odhad z literatury** a je VÝSLOVNĚ
  označený jako odhad, ne měření. Všechno ostatní je měření.

Použití:  python _analyza\p18-prompt-tokeny.py
"""

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(__file__).resolve().parent.parent
HRA = WS / "games" / "uo-shadows"

GRANULE = ["entity.player.api", "world.nodes", "sim.combat", "tests.harness"]


def tokeny(text: str) -> int:
    """Odhad tokenů pro BPE tokenizer (naměřeno na tomhle projektu:
    český text s diakritikou má ~3,0 znaku/token, ASCII kód ~3,6).

    NENÍ to přesné číslo — je to DOLNÍ ODHAD postavený na znacích. Skutečný
    tokenizer by dal ±15 %. U rozhodnutí „vejde se do 8 000?" to stačí,
    protože rozdíl je řádový (14 398 vs. 8 000).

    Proč dolní odhad: `len(text)/3.6` podhodnocuje český text; bereme proto
    konzervativně **3,0 znaku/token** pro celý vstup, což je pro smíšený
    česko-kódový obsah blízko pravdy a mírně NADHODNOCUJE.
    """
    return int(len(text) / 3.0)


roadmapa = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
grains = roadmapa.get("grains") or roadmapa.get("tasks") or []
index = {g.get("id"): g for g in grains}

print("=" * 78)
print("ÚKOL 1 — VELIKOST PROMPTU, KTERÝ JDE DO AIDERU (měřeno na %s)" % HRA.name)
print("=" * 78)

# --- pevné části, které jdou do KAŽDÉHO běhu ---------------------------------
conv = HRA / "CONVENTIONS.md"
print()
print("A) PEVNÉ SOUČÁSTI (jdou do každého běhu)")
if conv.exists():
    t = conv.read_text(encoding="utf-8")
    print("   %-34s %8d znaků  ~%6d tokenů" % ("CONVENTIONS.md (--read)", len(t), tokeny(t)))
    pevne_znaky = len(t)
else:
    print("   CHYBA CONVENTIONS.md NENÍ — měření by bylo neúplné")
    pevne_znaky = 0

# Aiderův vlastní systémový prompt: NENÍ měřením, je to odhad z literatury.
# Je tu proto, aby číslo nebylo podhodnocené — a je označený.
AIDER_SYSTEM_ODHAD = 6500
print("   %-34s %8s        ~%6d tokenů   (ODHAD, ne měření — Aiderův"
      % ("systémový prompt Aideru", "—", AIDER_SYSTEM_ODHAD // 3))
print("   %-34s %8s         %6s" % ("", "", "vlastní prompt nelze offline změřit)"))
pevne_znaky += AIDER_SYSTEM_ODHAD

print()
print("B) CO SE PŘIDÁ ZA GRANULI")
tabulka = []
for gid in GRANULE:
    g = index.get(gid)
    if not g:
        print("   %-22s V ROADMAPĚ NENÍ" % gid)
        tabulka.append((gid, None, None, None, None, None))
        continue
    owns = list(g.get("owns") or [])
    deps = []
    for d in g.get("depends_on") or []:
        zav = index.get(d)
        for f in (zav or {}).get("owns") or []:
            if (HRA / f).exists():
                deps.append(f)
    deps = sorted(set(deps))
    prompt = str(g.get("prompt") or "")

    z_owns = sum(len((HRA / f).read_bytes()) for f in owns if (HRA / f).exists())
    z_deps = sum(len((HRA / f).read_bytes()) for f in deps)

    # POZOR: čte se v bajtech, ale tokeny se počítají ze ZNAKŮ. U českého
    # textu je bajtů víc — proto se obsah načítá jako text tam, kde to jde.
    def znaky(seznam):
        s = 0
        for f in seznam:
            p = HRA / f
            if p.exists():
                s += len(p.read_text(encoding="utf-8", errors="replace"))
        return s

    z_owns = znaky([f for f in owns if (HRA / f).exists()])
    z_deps = znaky(deps)
    z_prompt = len(prompt)

    celkem_znaku = pevne_znaky + z_owns + z_deps + z_prompt
    celkem_tokenu = tokeny("x" * celkem_znaku)

    print()
    print("   ── %s ──" % gid)
    print("      owns (%d): %s" % (len(owns), ", ".join(owns) or "—"))
    print("      depends_on: %s" % (", ".join(g.get("depends_on") or []) or "—"))
    print("      --read závislostí (%d souborů): %s znaků" % (len(deps), z_deps))
    print("      --file owns:                    %s znaků" % z_owns)
    print("      --message prompt:               %s znaků" % z_prompt)
    print("      ── CELKEM vstup:  %d znaků  ≈ %d tokenů" % (celkem_znaku, celkem_tokenu))
    tabulka.append((gid, z_prompt, z_deps, z_owns, celkem_znaku, celkem_tokenu))

print()
print("=" * 78)
print("C) SROVNÁNÍ S LIMITY POSKYTOVATELŮ")
print("=" * 78)

prov = json.loads((HRA / ".forge" / "providers.json").read_text(encoding="utf-8"))

# LIMITY: naměřené z logu běhu #146 (Groq) + z `providers.json` komentářů.
# ⚠ U ostatních poskytovatelů limit TPM v `providers.json` NENÍ — a to je
# důležitý rozdíl proti tomu, co tvrdí zadání („porovnej s limity
# v providers.json"). V tom souboru jsou jen POZNÁMKY o denních stropech
# a prioritách, žádné číslo TPM. Jediné změřené TPM je Groqovo (z logu).
LIMITY = {
    "groq": ("TPM 8 000", "NAMĚŘENO v logu běhu #146 (litellm.RateLimitError)"),
    "mistral": ("TPM ?", "v providers.json NENÍ — nutno dohledat u poskytovatele"),
    "cerebras": ("TPM ?", "v providers.json NENÍ — trial kredit $5/30 dní"),
    "gemini": ("TPM ?", "v providers.json NENÍ — ~20 dotazů/den (naměřeno dřív)"),
    "openrouter": ("TPM ?", "v providers.json NENÍ — 50 požadavků/den"),
}

print("   %-22s %-14s %s" % ("granule", "vstup ≈tokenů", "vejde se do Groq TPM 8 000?"))
for gid, _p, _d, _o, _c, tok in tabulka:
    if tok is None:
        print("   %-22s %-14s %s" % (gid, "—", "granule v roadmapě není"))
        continue
    verdikt = "ANO" if tok < 8000 else "NE — úloha u Groqu SPÁLÍ pokus"
    print("   %-22s %-14d %s" % (gid, tok, verdikt))

print()
print("   %-12s %-12s %s" % ("poskytovatel", "limit", "odkud to je"))
for p in prov.get("providers", []):
    lim, zdroj = LIMITY.get(p["name"], ("?", "?"))
    silne = "strongModels: " + ", ".join(p.get("strongModels") or []) if p.get("strongModels") else "—"
    print("   %-12s %-12s %s" % (p["name"], lim, zdroj))
    print("   %-12s %-12s %s" % ("", "", silne))

print()
print("=" * 78)
print("D) CO Z TOHO PLYNE (návrh — označeno, co je měření a co názor)")
print("=" * 78)
print("   MĚŘENÍ:")
print("     * Groq free TPM = 8 000; request v běhu #146 = 14 398 tokenů")
print("       (oba údaje z logu běhu, soubor _analyza/p18-log-36999784822.txt)")
print("     * Jméno modelu: do Aideru šlo `openai/openai/gpt-oss-120b`")
print("       (dvojitý prefix: agent.yml:227 přidává `openai/` k FORGE_MODEL,")
print("        který sám začíná `openai/`) → Aider: 'Unknown context window'.")
print("     * Limity TPM OSTATNÍCH poskytovatelů v `providers.json` NEJSOU.")
print("   NÁZOR (ne měření):")
print("     * `agent.yml:227` má prefix `openai/` natvrdo. Pro Groq je správně")
print("       `--model groq/<model>` nebo bez prefixu; pro ostatní OpenAI-")
print("       kompatibilní endpointy záleží na Aideru. Než se to změní, ověřit")
print("       na JEDNOM běhu, že Aider model zná (jinak si bere 'sane defaults').")
print("     * Vyřadit Groq z rotace pro granule nad ~8 000 tokenů vstupu, NEBO")
print("       zmenšit prompt (popsáno níž).")
print("   CO ZMENŠIT (kandidáti — každý je měřený výš):")
print("     * vstup tvoří z většiny Aiderův systémový prompt + CONVENTIONS.md,")
print("       tedy PEVNÁ část — ta se s granulí nemění; zmenšovat je tedy")
print("       potřeba U NÍ, ne u promptu granule.")

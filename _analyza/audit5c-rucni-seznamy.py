# -*- coding: utf-8 -*-
"""AUDIT 5c — RUČNÍ SEZNAMY A SKLADIŠTĚ (zbývající čísla pro fázi 5).

Měří tři věci, které plán označil za kandidáty na „zdržuje":
  1. kolik cest je v RUČNÍM seznamu brány diakritiky (a kolik z toho je _analyza),
  2. kolik z 270 skriptů v _analyza je zapojeno do NĚJAKÉ brány,
  3. kolik řádků mají skilly dohromady.
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SKILLS = pathlib.Path.home() / ".dsh" / "skills"

# ── 1. Ruční seznam v bráně diakritiky ────────────────────────────────────
kd = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"
s = kd.read_text(encoding="utf-8")
blok = s[s.find("SOUBORY = ["):s.find("]", s.find("SOUBORY = ["))]
cesty = re.findall(r'WS\s*/\s*((?:"[^"]+"\s*/?\s*)+)', blok)
jmena = [re.findall(r'"([^"]+)"', c) for c in cesty]
jmena = ["/".join(j) for j in jmena]

print("=" * 92)
print("AUDIT 5c — RUČNÍ SEZNAMY A SKLADIŠTĚ")
print("=" * 92)
print()
print("  1) RUČNÍ SEZNAM v orchestra/tools/kontrola-diakritiky.py")
print("     cest v seznamu SOUBORY : %d" % len(jmena))
analyza_v = [j for j in jmena if j.startswith("_analyza")]
print("     z toho v _analyza       : %d" % len(analyza_v))
print("     z toho v kořeni         : %d" % len([j for j in jmena if "/" not in j]))
print("     z toho v orchestra/     : %d" % len([j for j in jmena if j.startswith("orchestra")]))
print()
print("     ⚠ Tenhle seznam se musí doplňovat RUČNĚ při každém novém dokumentu.")
print("       Naměřeno v projektu: stalo se to 12× (vada S27) a komentáře v tom")
print("       souboru to samy přiznávají — přes 40 řádků komentářů je o tom,")
print("       že se to zapomnělo. Seznam se přitom dá NAHRADIT projitím složky")
print("       (`g1-diakritika-novych.py` to tak od 2. 10. 2026 dělá).")
komentare = len([l for l in blok.splitlines() if l.strip().startswith("#")])
print("     řádků komentářů uvnitř seznamu: %d z %d" % (komentare, len(blok.splitlines())))
print()

# ── 2. Kolik skriptů je zapojeno do bran ──────────────────────────────────
g3 = (WS / "_analyza" / "g3-brany.py").read_text(encoding="utf-8")
zapojene = set(re.findall(r'_analyza/([\w.\-]+\.(?:py|mjs))', g3))
skripty = sorted(p.name for p in (WS / "_analyza").glob("*")
                 if p.is_file() and p.suffix in (".py", ".mjs"))
print("  2) SKLADIŠTĚ _analyza")
print("     skriptů (.py/.mjs) v _analyza      : %d" % len(skripty))
print("     z toho v g3-brany.py (29 bran)     : %d" % len(zapojene))
print("     z toho NIKDE v g3                  : %d" % (len(skripty) - len(zapojene)))
print("     podíl zapojených                   : %.1f %%"
      % (100.0 * len(zapojene) / len(skripty)))
print()
print("     (Pozor na výklad: nezapojený skript NENÍ smetí — je to jednorázová")
print("      sonda, kterou nějaká session potřebovala. Otázka fáze 4 ale je,")
print("      jestli je session NAJDE, až je bude potřebovat.)")
print()

# ── 3. Skilly ─────────────────────────────────────────────────────────────
print("  3) SKILLY")
radky = 0
for f in sorted(SKILLS.glob("*/SKILL.md")):
    t = f.read_text(encoding="utf-8")
    radky += len(t.splitlines())
print("     skillů : %d" % len(list(SKILLS.glob("*/SKILL.md"))))
print("     řádků  : %d" % radky)
print("     bajtů  : %d" % sum(f.stat().st_size for f in SKILLS.glob("*/SKILL.md")))
print()

# ── 4. Dokumenty mimo git ─────────────────────────────────────────────────
print("  4) VERZOVÁNÍ DOKUMENTŮ")
print("     Workspace root JE git repo? %s" % (WS / ".git").exists())
print("     Repozitáře: orchestra, games/uo-shadows — oba obsahují jen svůj strom.")
print("     → VŠECH 97 inventovaných dokumentů je MIMO verzovací systém.")
print("       Znamená to: žádná historie změn dokumentace, žádné `git diff`,")
print("       žádné vrácení omylem přepsaného dokumentu.")

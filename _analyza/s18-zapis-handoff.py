# -*- coding: utf-8 -*-
r"""Zapíše §18 (výsledky ověření) a §8g (vlastní omyly) do `HANDOFF.md`.

PROČ SKRIPTEM: `HANDOFF.md` je 2 369 řádků a musí se jen PŘIDAT (nic nemazat).
Text se proto drží v samostatných `.md` souborech a vkládá se **appendem**
(na konec souboru, ne „na konec objektu" — to je past z `overovani` §7.3).

Použití:  python _analyza\s18-zapis-handoff.py
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
# ⚠ ZÁLOHA, ze které se dá vrátit — a je to POVINNÉ, protože tenhle skript
# **není idempotentní**: druhé spuštění vloží oddíly ZNOVU (naměřeno
# 2. 10. 2026: `HANDOFF.md` vyskočil z 202 443 B na 234 375 B a oddíly 8g/18
# byly v souboru dvakrát). Pojistka níž to teď odmítne.
ZALOHA = WS / "_analyza" / "handoff-pred-s18.md"
PRED = HANDOFF.read_bytes()

# POJISTKA PROTI DVOJÍMU VLOŽENÍ: každý oddíl smí být v souboru jen JEDNOU.
# Kontroluje se PŘED zápisem (kdyby se to zjistilo až po, je soubor rozbitý).
for jmeno, kotva in (("s8g", "### 8g. Omyly PLÁNOVACÍ"),
                     ("s18", "## 18. Ověření práce AKČNÍ session"),
                     ("s18b", "### 18.15 Vada měřidla")):
    pocet = HANDOFF.read_text(encoding="utf-8").count(kotva)
    if pocet:
        print("ODMÍTNUTO: kotva %r je v HANDOFF.md už %dx — oddíly se vkládají JEN JEDNOU."
              % (kotva, pocet))
        print("  Vrať soubor ze zálohy: %s" % ZALOHA)
        sys.exit(2)

print("PŘED: HANDOFF.md je %d B, %d řádků"
      % (len(PRED), len(PRED.decode("utf-8").splitlines())))

for jmeno in ("s8g-novy-oddil.md", "s18-novy-oddil.md", "s18b-doplneni.md"):
    cesta = WS / "_analyza" / jmeno
    assert cesta.is_file(), "chybí %s" % cesta
    text = cesta.read_text(encoding="utf-8")
    # POJISTKA: vkládaný oddíl musí mít NADPIS `###`/`##` (oddíly začínají
    # oddělovačem `---`, takže se hledá kdekoliv na začátku, ne na prvním znaku).
    # Naměřeno při psaní: DVĚ verze týhle pojistky spadly na správném souboru —
    # (1) `startswith("#")` minulo oddíl začínající `---`,
    # (2) `"\n## " in …` minulo nadpis `### 8g.` (hledal DVĚ křížky, soubor má tři).
    # Falešný poplach na správném vstupu je stejná vada jako slepá kontrola.
    zahlavi = "\n".join(text.splitlines()[:6])
    assert any(l.startswith("#") for l in zahlavi.splitlines()), \
        "%s nemá v první šestici řádků nadpis: %r" % (jmeno, zahlavi[:120])
    assert len(text) > 1500, "%s je podezřele krátký (%d B)" % (jmeno, len(text))
    with HANDOFF.open("a", encoding="utf-8", newline="") as f:
        f.write("\n")
        f.write(text if text.endswith("\n") else text + "\n")
    print("  přidán %s (%d B)" % (jmeno, len(text)))

PO = HANDOFF.read_bytes()
print("PO:   HANDOFF.md je %d B, %d řádků"
      % (len(PO), len(PO.decode("utf-8").splitlines())))
assert len(PO) > len(PRED), "soubor se nezvětšil — zápis neproběhl"
assert PO.startswith(PRED[:4096]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL (append není append)"
print("OK — obsah se jen přidal (prvních 4 096 B je shodných)")

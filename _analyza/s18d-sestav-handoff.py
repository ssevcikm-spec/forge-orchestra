# -*- coding: utf-8 -*-
r"""Vrátí `HANDOFF.md` ze zálohy `_analyza\handoff-pred-s18.md` a vloží
`§8g` + `§18` + `§18b` + omyl 68 + §18.16 — **každé právě jednou**.

PROČ ZNOVU A CELÉ: dvě předchozí vložení byla vadná (omyl 68 v `HANDOFF.md`
§8g): (1) **dvojitý append** — oddíly 8g a 18 byly v souboru dvakrát;
(2) **dvojité vložení §18.16** — skript vkládal „před nadpis §18", ale kotva
`## 18.` je i **uvnitř nově vloženého textu** (odkaz „§18.15"), takže se po
prvním vložení posunula a druhá náhrada přidala oddíl znovu.

**Pravidlo, které z toho plyne:** když vkládáš text, který sám sebe zmiňuje,
**nesmí být kotva hledaná v TOMTÉMŽ textu** — hledej ji **před** vložením
(v původním souboru) a vkládej **na index**, ne opakovaným `find` po zápisu.

Použití:  python _analyza\s18d-sestav-handoff.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZALOHA = WS / "_analyza" / "handoff-pred-s18.md"
ZAPIS = "--zapis" in sys.argv

assert ZALOHA.is_file(), "chybí záloha %s" % ZALOHA
zaklad = ZALOHA.read_text(encoding="utf-8")
print("=" * 78)
print("SESTAVENÍ HANDOFF.md — ze zálohy, každý oddíl PRÁVĚ JEDNOU")
print("=" * 78)
print("  základ (záloha): %d B, %d řádků"
      % (len(zaklad.encode("utf-8")), len(zaklad.splitlines())))

# ── VSTUPY ──────────────────────────────────────────────────────────────────
S8G = (WS / "_analyza" / "s8g-novy-oddil.md").read_text(encoding="utf-8").strip()
# Omyl 68 patří do TABULKY §8g — vloží se na její konec (před souhrn).
OMYL68 = (WS / "_analyza" / "s18c-omyl68-radek.md").read_text(encoding="utf-8").strip()
S18 = (WS / "_analyza" / "s18-novy-oddil.md").read_text(encoding="utf-8").strip()
S18B = (WS / "_analyza" / "s18b-doplneni.md").read_text(encoding="utf-8").strip()
S1816 = (WS / "_analyza" / "s18c-doplneni.md").read_text(encoding="utf-8").strip()

assert OMYL68.startswith("| **68** |"), "řádek omylu 68 nemá správný tvar"
assert OMYL68.count("\n") == 0, "omyl 68 musí být JEDEN řádek tabulky"
assert S1816.startswith("### 18.16"), "§18.16 nemá správný nadpis"

# Kotva pro omyl 68 = poslední řádek tabulky §8g (omyl 67) — a ten je
# v souboru `s8g-novy-oddil.md`, ne v záloze (ta vznikla PŘED vložením §8g).
KOTVA67 = "| **67** |"
i67 = S8G.find(KOTVA67)
assert i67 > 0, "v §8g není omyl 67"
konec67 = S8G.find("\n", i67)
assert konec67 > i67, "řádek omylu 67 nemá konec"

# ── KROK 1: §8g — omyl 68 hned za omyl 67 (oba v TÉŽE tabulce) ──────────────
s8g_s_omylem = S8G[:konec67 + 1] + OMYL68 + "\n" + S8G[konec67 + 1:]
assert s8g_s_omylem != S8G, "omyl 68 se do §8g nevepsal"
assert s8g_s_omylem.count("| **68** |") == 1, "omyl 68 v §8g není právě 1×"
assert s8g_s_omylem.count("| **67** |") == 1, "omyl 67 v §8g není právě 1×"

# ── KROK 2: §18 + dodatek + §18.16 (vše PŘED vložením dohromady) ────────────
# ⚠ TADY je ta oprava: `## 18.` se hledá JEN v `S18B` (kde je odkaz „§18.15"),
# a to **jen kvůli kontrole**. Vkládá se spojením řetězců, ne dalším `find`.
assert "## 18. Ověření práce" not in S18B, \
    "dodatek §18b obsahuje nadpis §18 — vkládal by se rekurzivně"
blok18 = "\n\n".join([S18, S18B, S1816])

# ── SESTAVENÍ: základ + §8g + blok18 ────────────────────────────────────────
novy = zaklad + "\n" + s8g_s_omylem + "\n\n" + blok18 + "\n"

# ── KONTROLY PŘED ZÁPISEM (každá kotva právě jednou, nic se neztratilo) ─────
for kotva, ocekavano in (("### 8g. Omyly PLÁNOVACÍ", 1),
                         ("| **68** |", 1),
                         ("| **67** |", 1),
                         ("## 18. Ověření práce AKČNÍ session", 1),
                         ("### 18.15 Vada měřidla", 1),
                         ("### 18.16 Vlastní omyl", 1),
                         ("## 17. Ověření práce AKČNÍ session", 1)):
    pocet = novy.count(kotva)
    stav = "OK  " if pocet == ocekavano else "CHYBA"
    print("  %s %-40s %dx (očekáváno %d)" % (stav, kotva, pocet, ocekavano))
    assert pocet == ocekavano, "kotva %r: %d, očekáváno %d" % (kotva, pocet, ocekavano)

assert novy.startswith(zaklad[:8192]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"
assert len(novy) > len(zaklad), "soubor se nezvětšil"

print()
print("  základ:  %d B" % len(zaklad.encode("utf-8")))
print("  + §8g:   %d B (s omylem 68)" % len(s8g_s_omylem.encode("utf-8")))
print("  + §18:   %d B (§18 + §18b + §18.16)" % len(blok18.encode("utf-8")))
print("  = CELKEM %d B, %d řádků" % (len(novy.encode("utf-8")), len(novy.splitlines())))

if ZAPIS:
    HANDOFF.write_bytes(novy.encode("utf-8"))
    print()
    print("  ZAPSÁNO.")
else:
    print()
    print("  (dry-run — spusť s --zapis)")

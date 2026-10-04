# -*- coding: utf-8 -*-
"""AUDIT 5b — CENA POVINNÉHO ČTENÍ (a kolik povinných kroků to je).

PROČ: podnětem k auditu je, že práce agenta trvá půl hodiny místo pár minut.
Brány se NAMĚŘILY na **40,75 s** (`audit5-cas-bran.py`) — takže „dokonalá
metodika bran" to být nemůže. Zbývá druhá hypotéza: **cena vstupu**, tedy
kolik toho agent MUSÍ přečíst a vykonat, než smí začít pracovat.

CO SE MĚŘÍ:
  * povinný čtecí balík podle `NEXT-SESSION-INSTRUKCE.md` §1 (co zadání
    doslova přikazuje přečíst),
  * tytéž dokumenty i s tím, co AGENTS.md označuje za povinné na začátku,
  * počet povinných příkazů v zadání.

⚠ O ZNAČCE „tokeny": NEMĚŘÍM tokeny, měřím ZNAKY. Přepočet na tokeny je
  HEURISTIKA (u českého textu s diakritikou zhruba 2,5–3,5 znaku na token)
  a je tak i označený. Kdo potřebuje skutečná čísla, ať je vezme z živé
  session (`dsh-usage`), ne odsud — `AGENTS.md`: různé čítače nesou stejné
  jméno a číslo bez postupu se nedá ověřit.
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SKILLS = pathlib.Path.home() / ".dsh" / "skills"

# ── Povinný čtecí balík podle NEXT-SESSION-INSTRUKCE.md §1 ─────────────────
# (zkopírováno z bodů 1 a 2 toho zadání; není to odhad)
POVINNE = [
    ("PREDAVANI-SESSION.md", WS / "PREDAVANI-SESSION.md", "celý (§6.2 je minimum)"),
    ("AGENTS.md", WS / "AGENTS.md", "celý"),
    ("HANDOFF.md", WS / "HANDOFF.md", "§22 + §8i (zadání)"),
    ("PLAN-DALSI-KROK.md", WS / "PLAN-DALSI-KROK.md", "celý (zadání)"),
    ("NEXT-SESSION-INSTRUKCE.md", WS / "NEXT-SESSION-INSTRUKCE.md", "sám sebe"),
    ("skill dsh-prostredi", SKILLS / "dsh-prostredi" / "SKILL.md", "celý"),
    ("skill overovani", SKILLS / "overovani" / "SKILL.md", "celý"),
]
# Co AGENTS.md navíc označuje za povinné („Než začneš").
NAVIC = [
    ("KRONIKA-PROJEKTU.md", WS / "KRONIKA-PROJEKTU.md", "odkaz z AGENTS.md „Kam pro co\""),
    ("MOZNOSTI-AGENTA.md", WS / "MOZNOSTI-AGENTA.md", "AGENTS.md: zdroj pravdy o schopnostech"),
    ("OTEVRENA-TEMATA.md", WS / "OTEVRENA-TEMATA.md", "skill otevrena-temata"),
]


def zmer(polozky):
    radky = []
    soucet_b, soucet_r, soucet_z = 0, 0, 0
    for jmeno, cesta, proc in polozky:
        if not cesta.is_file():
            radky.append((jmeno, None, None, None, "CHYBA: neexistuje"))
            continue
        s = cesta.read_text(encoding="utf-8")
        b = cesta.stat().st_size
        r = len(s.splitlines())          # splitlines(), ne split("\n")
        z = len(s)
        soucet_b += b
        soucet_r += r
        soucet_z += z
        radky.append((jmeno, b, r, z, proc))
    return radky, soucet_b, soucet_r, soucet_z


def vypis(titulek, polozky):
    radky, b, r, z = zmer(polozky)
    print("-" * 92)
    print("  %s" % titulek)
    print("-" * 92)
    print("  %-30s %10s %8s %10s  %s" % ("dokument", "bajtů", "řádků", "znaků", "proč"))
    for jmeno, bb, rr, zz, proc in radky:
        if bb is None:
            print("  %-30s %10s %8s %10s  %s" % (jmeno, "—", "—", "—", proc))
        else:
            print("  %-30s %10d %8d %10d  %s" % (jmeno, bb, rr, zz, proc))
    print("  " + "-" * 88)
    print("  %-30s %10d %8d %10d" % ("SOUČET", b, r, z))
    print("  %-30s %10s %8s %10s  (÷3 znaky/token: ~%d tis. tokenů)"
          % ("odhad tokenů", "", "", "", z / 3 / 1000))
    return b, r, z


print("=" * 92)
print("AUDIT 5b — CENA POVINNÉHO ČTENÍ")
print("=" * 92)
print()

b1, r1, z1 = vypis("POVINNÉ podle NEXT-SESSION-INSTRUKCE.md §1 (než smíš začít)", POVINNE)
print()
b2, r2, z2 = vypis("NAVÍC co AGENTS.md označuje za povinné", NAVIC)
print()
print("=" * 92)
print("  CELKEM vstupu před první prací: %d bajtů, %d řádků, %d znaků"
      % (b1 + b2, r1 + r2, z1 + z2))
print("  (v tom jen jádro bez skillů: %d bajtů)" % (b1 - (30556 + 30080)))
print()

# ── Kolik povinných KROKŮ zadání ukládá ───────────────────────────────────
zad = (WS / "NEXT-SESSION-INSTRUKCE.md").read_text(encoding="utf-8")
blok = zad[zad.find("## 1. Než začneš"):zad.find("## 2.")]
prikazy = re.findall(r"^\s*(?:\d+\.\s+)?((?:python|node|&\s*orchestra)[^\n]*)",
                     blok, re.M)
print("-" * 92)
print("  POVINNÉ PŘÍKAZY v §1 zadání: %d" % len(prikazy))
for p in prikazy:
    print("      %s" % p.strip()[:88])
print()

# ── Kolik z toho je čistě administrativa ──────────────────────────────────
print("-" * 92)
print("  Kolik dokumentů musí agent ZNÁT, aby směl pracovat: %d" % (len(POVINNE) + len(NAVIC)))
print("  Kolik bran musí spustit a ověřit:  7 (viz §1 zadání)")
print("  Kolik bran existuje celkem:       29 (g3-brany.py)")
print()
print("  ⚠ SROVNÁNÍ S NAMĚŘENÝM ČASEM:")
print("      všechny brány dohromady   :  40,75 s   (audit5-cas-bran.py)")
print("      povinné čtení             :  %d znaků  (≈ %d tis. tokenů)"
      % (z1 + z2, (z1 + z2) / 3 / 1000))
print("      → čas tedy NENÍ v běhu bran. Je ve ZPRACOVÁNÍ VSTUPU.")

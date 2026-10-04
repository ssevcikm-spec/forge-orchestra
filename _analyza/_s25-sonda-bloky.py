# -*- coding: utf-8 -*-
"""SONDA 3 (jednorázová) — bloky omylů v `HANDOFF.md`: kolik jich je a co v nich.

PROČ: nález **NA17** tvrdí, že brána `kronika-kontrola.py` zná **8 bloků** a vidí
**75** omylů, kdežto v dokumentu je bloků víc. Než bránu rozšířím, musím vědět
TŘI různá čísla, každé na jinou otázku (`overovani` §9.3):
  (a) kolik je ŘÁDKŮ tabulek,
  (b) kolik je UNIKÁTNÍCH id,
  (c) kolik z toho vidí brána.
A taky které nadpisy jsou NESTABILNÍ (nesou jméno session) — na těch se seznam
kotev v bráně láme.

Nic nemění, jen čte.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HAND = WS / "HANDOFF.md"
KRON = WS / "KRONIKA-PROJEKTU.md"

text = HAND.read_text(encoding="utf-8")
radky = text.splitlines()

# Všechny nadpisy `## 8.` / `### 8x.` — v pořadí, v jakém v dokumentu jsou.
ANCHOR = re.compile(r"^(#{2,4})\s+(8[A-Za-z]?)\.\s", re.M)
vsechny = []
for i, l in enumerate(radky):
    m = ANCHOR.match(l)
    if m:
        vsechny.append((i, len(m.group(1)), m.group(0).strip(), l.strip()))

print("=" * 100)
print("  NADPISY BLOKŮ OMYLŮ V HANDOFF.md (v pořadí v dokumentu)")
print("=" * 100)
for i, uroven, kotva, cely in vsechny:
    print("  ř.%-6d %-3s %s" % (i + 1, "#" * uroven, cely[:110]))

# Rozsekání na bloky: blok začíná na svém nadpisu a končí na nejbližším
# nadpisu STEJNÉ NEBO VYŠŠÍ úrovně (což je přesně to, co dělá brána).
print()
print("=" * 100)
print("  CO JE V KTERÉM BLOKU")
print("=" * 100)
ID_RADEK = re.compile(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")
vsechna_id = {}
radku_celkem = 0
for idx, (i, uroven, kotva, cely) in enumerate(vsechny):
    konec = len(radky)
    for j in range(i + 1, len(radky)):
        m = re.match(r"^(#{2,4})\s", radky[j])
        if m and len(m.group(1)) <= uroven:
            konec = j
            break
    telo = radky[i:konec]
    ida = []
    for l in telo:
        m = ID_RADEK.match(l)
        if m:
            ida.append(int(m.group(1)))
    radku_celkem += len(ida)
    for x in ida:
        vsechna_id.setdefault(x, []).append(cely.strip()[:44])
    print("  %-72s řádků: %3d" % (cely.strip()[:72], len(ida)))
    if ida:
        print("      %s" % ("id %d–%d" % (min(ida), max(ida))))

print()
print("=" * 100)
print("  TŘI ČÍSLA, TŘI OTÁZKY (`overovani` §9.3)")
print("=" * 100)
print("  (a) řádků tabulek omylů celkem:      %d" % radku_celkem)
print("  (b) unikátních id celkem:            %d" % len(vsechna_id))
dupl = {k: v for k, v in vsechna_id.items() if len(v) > 1}
print("      z toho id ve VÍC blokách:        %d  %s"
      % (len(dupl), sorted(dupl) if dupl else ""))
for k in sorted(dupl):
    print("         id %d: %s" % (k, dupl[k]))

# Co vidí brána DNES (seznam 8 kotev z `kronika-kontrola.py`)
BLOKY_BRANY = ["## 8. Vlastní omyly", "### 8b. Omyly ověřovací session",
               "### 8c. Omyly session 2. 10. 2026", "### 8d. Omyly PLÁNOVACÍ session",
               "### 8e. Omyly AKČNÍ session", "### 8f. Omyly PLÁNOVACÍ",
               "### 8g. Omyly PLÁNOVACÍ", "### 8h. Omyly AKČNÍ session"]
print()
print("  (c) co vidí brána dnes (8 kotev):")
soucet = 0
for kotva in BLOKY_BRANY:
    if kotva not in text:
        print("      %-40s KOTVA V DOKUMENTU NENÍ" % kotva)
        continue
    i = next(k for k, l in enumerate(radky) if l.startswith(kotva))
    uroven = len(kotva) - len(kotva.lstrip("#"))
    konec = len(radky)
    for j in range(i + 1, len(radky)):
        m = re.match(r"^(#{2,4})\s", radky[j])
        if m and len(m.group(1)) <= uroven:
            konec = j
            break
    n = sum(1 for l in radky[i:konec] if ID_RADEK.match(l))
    soucet += n
    print("      %-40s %3d" % (kotva, n))
print("      %-40s %3d" % ("CELKEM (co vidí brána)", soucet))
print()
print("  MIMO seznam brány:")
for i, uroven, kotva, cely in vsechny:
    if not any(cely.startswith(k) for k in BLOKY_BRANY):
        print("      %s" % cely[:110])

# ── Kde jsou v DOKUMENTECH čísla o omylech (kvůli Úkolu 2c/2) ─────────────
print()
print("=" * 100)
print("  KDE VŠUDE JE V DOKUMENTECH ČÍSLO O OMYLECH")
print("=" * 100)
VZOR = re.compile(r"(\d+)\s+omyl")
for jmeno in ("KRONIKA-PROJEKTU.md", "AGENTS.md", "HANDOFF.md"):
    p = WS / jmeno
    if not p.is_file():
        continue
    for i, l in enumerate(p.read_text(encoding="utf-8").splitlines(), 1):
        for m in VZOR.finditer(l):
            print("  %-22s :%-5d %s" % (jmeno, i, l.strip()[:150]))

# -*- coding: utf-8 -*-
"""SONDA 5 (jednorázová) — kolik omylů má HLAVNÍ tabulka §8 a kolik z ní brána čte.

PROČ: `kronika-kontrola.py` hlásí u bloku „1–13" třináct omylů — a přitom
tabulka pod `## 8. Vlastní omyly` má podle sondy 3 **70 řádků s id 1–101**.
Blok tedy končí na nadpisu `### 8b.` (což je správně, aby se nepočítaly dvakrát),
ale **do součtu se tím ze 70 řádků dostane 13** — a nikde to není vidět.

Tohle měření rozhoduje, KOLIK má být v `BLOKY` položek a co se má o tom vypsat.
Nic nemění.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
radky = (WS / "HANDOFF.md").read_text(encoding="utf-8").splitlines()

# Přesná kopie `pocet_omylu()` z brány — jinak bych měřil jiným predikátem
# (`overovani` §9.4: brána se musí ptát TÍMŽ predikátem, kterým hledá).
ID_RADEK = re.compile(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|")

start = next(i for i, l in enumerate(radky) if l.startswith("## 8. Vlastní omyly"))
konec = next(i for i, l in enumerate(radky) if i > start and l.startswith("### 8b."))

print("=" * 96)
print("  HLAVNÍ TABULKA §8 — co v ní je a co z ní brána počítá")
print("=" * 96)
print("  `## 8.` začíná na řádku:      %d" % (start + 1))
print("  `### 8b.` (konec bloku):      %d" % (konec + 1))
print("  řádků v bloku:                %d" % (konec - start))

v_bloku = [l for l in radky[start:konec] if ID_RADEK.match(l)]
print("  řádků tabulky v bloku:        %d" % len(v_bloku))

# A co je ZA koncem bloku — tam jsou id 14–101 „ve společné tabulce"?
mimo = [l for l in radky[konec:] if ID_RADEK.match(l)]
print("  řádků tabulky ZA blokem:      %d" % len(mimo))

ida_v = [int(ID_RADEK.match(l).group(1)) for l in v_bloku]
ida_m = [int(ID_RADEK.match(l).group(1)) for l in mimo]
print()
print("  id v bloku `## 8.` – `### 8b.`: %s … %s  (%d)"
      % (ida_v[:6], ida_v[-4:], len(ida_v)))
print("  id za blokem (do konce souboru): %s … %s  (%d)"
      % (ida_m[:6], ida_m[-4:], len(ida_m)))

print()
print("=" * 96)
print("  CO Z TOHO PLYNE PRO `BLOKY`")
print("=" * 96)
print("  * Blok „1–13“ = řádky MEZI `## 8.` a `### 8b.` — brána je počítá správně (%d)." % len(ida_v))
print("  * Zbytek hlavní tabulky (id %d–%d) leží **mezi podbloky** a brána ho" % (min(ida_m), max(ida_m)))
print("    **nepočítá vůbec** — a nikde to nevypisuje. To je slepé místo, ne úmysl.")
print("  * Bloky `8b`–`8j` se počítají zvlášť a jejich id se s hlavní tabulkou")
print("    **NESMÍ sčítat** (naměřeno: 57 id je v obou) — jinak vznikne dvojí počítání.")

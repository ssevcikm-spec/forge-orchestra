# -*- coding: utf-8 -*-
"""Vloží oddíl §24 na konec `HANDOFF.md` a blok omylů `8k` za `8j`.

⚠ Zapisuje se **jedním** `write_bytes` (append-only dokument, `HANDOFF.md` není
v gitu — záloha je kopie souboru). Před zápisem i po něm se kontroluje, že se
**původní obsah nezměnil** (A2): nový text musí původní **obsahovat celý**.
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"

orig = H.read_bytes()
text = orig.decode("utf-8")

oddil24 = (WS / "_analyza" / "s24-oddil.md").read_text(encoding="utf-8")
blok8k = (WS / "_analyza" / "s24-oddil-8k.md").read_text(encoding="utf-8")

# ── 1) §8k patří ZA blok `8j`, PŘED `## 9.` ────────────────────────────────
KOTVA = "\n## 9. Co už otevřené NENÍ\n"
assert text.count(KOTVA) == 1, "kotva `## 9.` je v souboru %dx" % text.count(KOTVA)
assert "### 8k." not in text, "blok 8k už v souboru je — nezdvojovat"

novy = text.replace(KOTVA, blok8k + KOTVA, 1)

# ── 2) §24 na KONEC ────────────────────────────────────────────────────────
assert "## 24. Ověření práce §23" not in novy, "oddíl 24 už v souboru je"
if not novy.endswith("\n"):
    novy += "\n"
novy += oddil24

# ── 3) KONTROLA, ŽE NIC NEZMIZELO (A2) ─────────────────────────────────────
chyby = []
for radek in text.splitlines():
    if radek.strip() and radek not in novy:
        chyby.append(radek[:100])
if chyby:
    print("CHYBA: %d řádků původního textu v novém NENÍ:" % len(chyby))
    for c in chyby[:15]:
        print("   %s" % c)
    sys.exit(1)

print("kontrola A2: všech %d neprázdných řádků původního textu je v novém"
      % len([l for l in text.splitlines() if l.strip()]))
print("  původně : %d B, %d řádků" % (len(orig), len(text.splitlines())))
print("  nově    : %d B, %d řádků" % (len(novy.encode("utf-8")), len(novy.splitlines())))
print("  připsáno: +%d B" % (len(novy.encode("utf-8")) - len(orig)))

H.write_bytes(novy.encode("utf-8"))
zpet = H.read_bytes()
print("  zapsáno : %d B · kontrola zápisu: %s"
      % (len(zpet), "OK" if zpet == novy.encode("utf-8") else "CHYBA"))

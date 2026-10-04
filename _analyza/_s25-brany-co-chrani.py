# -*- coding: utf-8 -*-
"""Klasifikuje brány podle toho, CO CHRÁNÍ — a je to odpověď na otázku
„zajišťuje měřicí vrstva kvalitu?".

Otázka, na kterou to odpovídá (`overovani` §1.1 — „měří ta veličina vůbec to,
na co se ptám?"): **kolik z 30 bran by zabránilo vadě, která se dostane
k uživateli — a kolik z nich měří jen dokumentaci a sebe sama?**

Kdyby většina měřila dokumentaci, pak vrstva **nevyrábí kvalitu** — vyrábí
jen jistotu o tvrzeních, a to je jiná věc.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
t = (WS / "_analyza" / "g3-brany.py").read_text(encoding="utf-8")
i = t.index("BRANY = [")
j = t.index("\nvse = []", i)
blok = t[i:j]

# popis brány a její příkaz (první dva řetězce v tuple)
brany = re.findall(r'\(\s*"([^"]+)",\s*\[([^\]]*)\]', blok)
print("bran celkem v g3: %d" % len(brany))

# Co je „dodávaný artefakt": hra, conductor, šablona, deploy.
ARTEFAKT = ("godot", "run_tests", "combat", "schema.sql", "cooldown", "tsc",
            "validate-all", "check-schema", "lint-roadmapa", "deploy",
            "baseline", "vision.test", "test-check", "check-assets",
            "kontrola-driftu", "sjednot-sablonu", "test-eskalace")
# Co je „dokumentace a proces": .md soubory, handoff, kronika, zadání, skilly.
DOKUMENT = (".md", "handoff", "kronika", "zadani", "diakritik",
            "over-dokumentaci", "over-skilly", "inventar", "snapshot")

chrani, dokument, smisene = [], [], []
for popis, prikaz in brany:
    p = prikaz.lower()
    a = any(k in p for k in ARTEFAKT)
    d = any(k in p for k in DOKUMENT)
    if a and d:
        smisene.append((popis, prikaz.strip()[:60]))
    elif a:
        chrani.append(popis)
    elif d:
        dokument.append(popis)
    else:
        smisene.append((popis, prikaz.strip()[:60]))

print()
print("=" * 92)
print("  BRÁNY, KTERÉ CHRÁNÍ DODÁVANÝ ARTEFAKT (hra / conductor / šablona): %d"
      % len(chrani))
print("=" * 92)
for b in chrani:
    print("   " + b)

print()
print("=" * 92)
print("  BRÁNY, KTERÉ MĚŘÍ DOKUMENTACI NEBO PROCES: %d" % len(dokument))
print("=" * 92)
for b in dokument:
    print("   " + b)

print()
print("=" * 92)
print("  NEZAŘAZENÉ (měřidla měřidel a ostatní): %d" % len(smisene))
print("=" * 92)
for b, p in smisene:
    print("   %-34s %s" % (b[:34], p))

print()
print("=" * 92)
print("  ZMĚŘENO: chrání artefakt=%d · měří dokumentaci=%d · ostatní=%d"
      % (len(chrani), len(dokument), len(smisene)))
if brany:
    print("  podíl bran chránících artefakt: %.0f %%"
          % (100.0 * len(chrani) / len(brany)))

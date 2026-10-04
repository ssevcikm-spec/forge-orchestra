"""Ověří, že soubory zmiňované v novém dokumentu opravdu existují.

Vlastní pokyn v dokumentu (§7) říká: „odkazy na soubory musí existovat
(Test-Path), jinak je to tvrzení, které nikdo neověří." Tohle je jeho kontrola —
jinak by to bylo pravidlo, které se samo nedodržuje.
"""
import re
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
DOKUMENT = WS / "JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md"
text = DOKUMENT.read_text(encoding="utf-8")


def _ceka_na_granuli(cisty: str) -> str:
    """Vrátí id granule, která soubor vlastní (a ještě ho nedodala), jinak ''.

    Zdroj je roadmapa hry (`owns`), takže se sem nedostane ruční výjimka —
    kdyby granule soubor nedodala, zmizí to z roadmapy a kontrola začne znovu
    hlásit chybu."""
    import json
    roadmapa = WS / "games" / "uo-shadows" / ".forge" / "roadmap.json"
    if not roadmapa.exists():
        return ""
    data = json.loads(roadmapa.read_text(encoding="utf-8"))
    klic = cisty.replace("\\", "/").lstrip("./")
    nalezy = []
    for g in data.get("grains", []):
        for own in g.get("owns", []):
            if own.replace("\\", "/").lstrip("./").endswith(klic):
                nalezy.append(g)
    if not nalezy:
        return ""
    # Přednostně ta, která soubor JEŠTĚ nemá dodaný (není `done`) — jinak by
    # výpis tvrdil, že soubor čeká na granuli, která je dávno hotová.
    for g in nalezy:
        if not g.get("done"):
            return g["id"]
    return nalezy[0]["id"]


# Zajímají nás názvy souborů v backticích (ne příkazy): bereme jen takové,
# které vypadají jako cesta k souboru (obsahují příponu nebo lomítko).
kandidati = set()
for m in re.finditer(r"`([^`\n]+)`", text):
    s = m.group(1).strip()
    if s.startswith(("-", "git ", "python ", "node ", "godot ", "& ")):
        continue
    if not re.search(r"\.(md|py|mjs|json|gd|godot|tscn|yml|ps1|diff|txt)$", s):
        continue
    if s.startswith("http"):
        continue
    kandidati.add(s)

chybi = []
preskoceno = []
for s in sorted(kandidati):
    cisty = s.split()[0].strip("(),;:")
    if "*" in cisty:
        preskoceno.append((cisty, "vzor s * (kontrola neumí)"))
        continue
    HRA = WS / "games" / "uo-shadows"
    if cisty.startswith("docs/"):
        kandidati_cest = [HRA / cisty]
    elif cisty.startswith(("assets/", "scripts/", "tests/")):
        kandidati_cest = [HRA / cisty]
    elif "/" in cisty:
        kandidati_cest = [WS / cisty, HRA / cisty]
    else:
        # Holé jméno: hledej v rootu workspace, v repu hry (i v podsložkách,
        # kde soubory opravdu jsou: scripts/, tests/, assets/data/, .forge/)
        # a v orchestra\tools.
        kandidati_cest = [
            WS / cisty, HRA / cisty, HRA / "scripts" / cisty,
            HRA / "tests" / cisty, HRA / "assets" / "data" / cisty,
            HRA / ".forge" / cisty,
            WS / "orchestra" / "tools" / cisty, HRA / "docs" / cisty,
        ]
    nalezeno = next((c for c in kandidati_cest if c.exists()), None)
    if nalezeno is not None:
        print(f"  OK    {cisty}")
    elif _ceka_na_granuli(cisty):
        # Není to vada dokumentu: soubor je deklarovaný jako výstup granule,
        # která ještě neproběhla. Bere se to z ROADMAPY, ne z ruční výjimky.
        print(f"  ČEKÁ  {cisty}   (vlastní ho granule {_ceka_na_granuli(cisty)} – ještě nevzniklo)")
    else:
        # Soubor, který má teprve VZNIKNOUT (granule ho vlastní), tu chybí
        # právem — hlásíme to zvlášť, ať to nevypadá jako vada dokumentu.
        print(f"  CHYBI {cisty}   (hledáno: {', '.join(str(c) for c in kandidati_cest[:3])})")
        chybi.append(cisty)

for c, duvod in preskoceno:
    print(f"  SKIP  {c}  ({duvod})")

print(f"\nOdkazů na soubory: {len(kandidati)}, chybí: {len(chybi)}, přeskočeno: {len(preskoceno)}")
if chybi:
    print("Chybějící: " + ", ".join(chybi))
sys.exit(1 if chybi else 0)

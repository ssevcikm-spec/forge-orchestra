"""Zpřesní dvě `done_note` v roadmapě podle NOVÉHO měření (2. 10. 2026).

Proč: první verze tvrdila, že `scripts/world.gd` byl „smazán" — naměřeno ale
`git show --stat c651368` → `{scripts => _retired}/world.gd | 0`, tedy **přesun**
(a to záměrný: nesl druhé číslo mřížky). Slovem „smazán" by se ztratilo, že kód
existuje a je použitelný jako základ.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\merge-scratch\.forge\roadmap.json")

NAHRADY = [
    (
        '"done_note": "POZOR: PR #21 sloučené 30. 9., ale scripts/world.gd byl smazán při izometrické migraci (c651368) – v main dnes není (měřeno 2. 10. 2026; hlásí to i check-schema.py jako mrtvou větev)",',
        '"done_note": "POZOR: PR #21 sloučené 30. 9.; kód je v _retired/world.gd (c651368 ho přesunul jako mrtvý kód s druhým číslem mřížky – izo projekce správně přešla do level.gd). Uzly surovin, gather() ani respawn ale nikde nejsou (level.gd je nemá) – práce v main není. Měřeno 2. 10. 2026",',
        "world.map: přesun do _retired (ne smazání) + co chybí",
    ),
    (
        '"done_note": "POZOR: PR #25 sloučené 1. 10. změnil jen project.godot – move(), inventář ani die() v scripts/player.gd nikdy nebyly (měřeno 2. 10. 2026: historie toho souboru žádný func move nezná)",',
        '"done_note": "POZOR: PR #25 sloučené 1. 10. změnil JEN project.godot; move(), inventář ani die() nebyly nikdy v žádné větvi (git log -S napříč refs). Jiné komponenty je už volají: assist.gd čte hp/max_hp/mana/max_mana/target, economy.gd volá add_item/remove_item. Měřeno 2. 10. 2026",',
        "entity.player: co přesně chybí + kdo to už volá",
    ),
]

text = CESTA.read_text(encoding="utf-8")
chyby = 0
for stary, novy, popis in NAHRADY:
    pocet = text.count(stary)
    if pocet != 1:
        print(f"CHYBA: {popis} — vzor nalezen {pocet}× (musí být 1×)")
        chyby += 1
        continue
    text = text.replace(stary, novy)
    print(f"OK    {popis}")

if chyby:
    print("NIC SE NEZAPSALO")
    sys.exit(1)

CESTA.write_text(text, encoding="utf-8", newline="")
json.loads(text)
print("\nJSON je validní.")

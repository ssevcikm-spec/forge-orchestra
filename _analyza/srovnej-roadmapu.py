"""Srovná roadmapu hry se SKUTEČNOSTÍ (naměřeno 2. 10. 2026).

Každá náhrada musí sednout PRÁVĚ JEDNOU — jinak skript skončí nenulově.
(Tichá náhrada, která neproběhne, tvrdí totéž co úspěšná; viz `overovani` §7.9.)
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\merge-scratch\.forge\roadmap.json")

NAHRADY = [
    # sim.mining: PR #30 sloučené, ale soubor neměl `done` → soubor říkal jiný stav než D1
    (
        '      "depends_on": ["core.skills", "world.map", "data.content"],\n      "acceptance": ["tests", "wiring"],',
        '      "depends_on": ["core.skills", "world.map", "data.content"],\n'
        '      "done": true,\n'
        '      "done_note": "PR #30 sloučené 2. 10. 2026; oprava (registr komponent místo /root, Godot 4 API) v PR #31",\n'
        '      "acceptance": ["tests", "wiring"],',
        "sim.mining dostal done + done_note",
    ),
    # persist.save: PR #28 je sloučené (dřív výhrada „PR NENÍ sloučené")
    (
        '"done_note": "POZOR: v D1 hotovo (task 139), ale PR NENÍ sloučené – práce není v main",',
        '"done_note": "PR #28 sloučené 2. 10. 2026 (oprava: registr komponent místo skupin, Godot 4 API)",',
        "persist.save: note odpovídá stavu",
    ),
    # ui.hud: PR #29 je sloučené
    (
        '"done_note": "POZOR: v D1 hotovo (task 140), ale PR NENÍ sloučené – práce není v main",',
        '"done_note": "PR #29 sloučené 2. 10. 2026 (oprava: Godot 4 API margin_* → offset_*, registr komponent)",',
        "ui.hud: note odpovídá stavu",
    ),
    # world.map: soubor byl smazán při izometrické migraci
    (
        '"done_note": "PR #21 sloučené 30. 9.",',
        '"done_note": "POZOR: PR #21 sloučené 30. 9., ale scripts/world.gd byl smazán při izometrické migraci (c651368)'
        ' – v main dnes není (měřeno 2. 10. 2026; hlásí to i check-schema.py jako mrtvou větev)",',
        "world.map: přiznáno, že soubor v main není",
    ),
    # entity.player: PR #25 změnil jen project.godot
    (
        '"done_note": "PR #25 sloučené 1. 10.",',
        '"done_note": "POZOR: PR #25 sloučené 1. 10. změnil jen project.godot – move(), inventář ani die()'
        ' v scripts/player.gd nikdy nebyly (měřeno 2. 10. 2026: historie toho souboru žádný func move nezná)",',
        "entity.player: přiznáno, že práce v main není",
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
    print("NIC SE NEZAPSALO — oprav vzory")
    sys.exit(1)

CESTA.write_text(text, encoding="utf-8", newline="")   # newline="" → nepřepisovat konce řádků
json.loads(text)                                        # validní JSON, jinak orchestra na hře nepracuje
print("\nJSON je validní.")

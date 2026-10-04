"""Vydá granule znovu — TŘI NOVÉ (rozhodnutí uživatele 2. 10. 2026).

Proč nová id a ne „od-done" u `world.map`/`entity.player`: D1 má u obou `done`
řádek a chování `roadmapTick` při rozporu „soubor ne-done / D1 done" není
naměřené. Nová id dostanou čerstvé řádky a jedou normálně.

POZOR na formát: soubor drží krátká pole na JEDNOM řádku (`"owns": ["a", "b"]`),
takže `json.dumps(indent=2)` by přeformátoval celý dokument (naměřeno: round-trip
se rozešel už na řádku 21). Proto se vkládá TEXTEM a formát zůstává.
"""
import json
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\merge-scratch\.forge\roadmap.json")
text = CESTA.read_text(encoding="utf-8")
data = json.loads(text)

NOVE = [
    {
        "id": "world.nodes",
        "title": "Svět — uzly surovin, těžba a respawn (náhrada za přesunutý _retired/world.gd)",
        "owns": ["scripts/world.gd", "assets/levels/main.json"],
        "depends_on": ["world.level", "data.content"],
        "size_lines": "<= 140",
        "acceptance": ["tests", "wiring"],
        "prompt": (
            "Vytvoř scripts/world.gd jako komponentu Svět (soubor začíná `extends Node`, žádné class_name, "
            "_init() bez povinného argumentu). SMLOUVA — přesně tohle volají jiné komponenty, nic víc: "
            "(1) gather(cell: Vector2i) -> bool — označí uzel v tom poli za vytěžený a vrátí true; pro totéž pole "
            "podruhé vrátí false. Volá ji scripts/mining.gd. "
            "(2) is_walkable(pos: Vector2) -> bool — nevytěžený uzel suroviny není průchozí, vytěžený je. "
            "(3) Uzel se po RESPAWN_TIME (konstanta 60.0) obnoví: čas porovnávej při dotazu přes Time.get_ticks_msec() "
            "(žádný Timer navíc, žádné await). "
            "(4) nodes() -> Array — kopie seznamu uzlů (pro HUD a ukládání). "
            "(5) snapshot() -> Array a restore(stav: Array) -> void — stav pro ukládání: jen slovníky, čísla a řetězce, "
            "NIKDY objekty (ConfigFile je neumí). "
            "KAŽDÝ uzel v nodes() MUSÍ mít vlastnosti resource_id: String, difficulty: int, cell: Vector2i — "
            "mining.gd je čte jako node.resource_id / node.difficulty / node.cell (nebo přes gettery get_resource_id() "
            "a get_difficulty()). "
            "ODKUD BERE UZLY: z mapy. Do assets/levels/main.json přidej 8–12 markerů ve tvaru "
            "{\"type\": \"resource\", \"resource_id\": \"iron_ore\", \"cell\": [x, y]} — resource_id ber z "
            "assets/data/materials.json (iron_ore obtížnost 1, wood 1, stone 2; iron_ingot je meziprodukt, ten se netěží) "
            "a obtížnost si vezmi odtud, neopisuj ji do kódu. Markery dávej na PRŮCHODNÁ pole (testy kontrolují, že každá "
            "značka leží na průchozím poli). "
            "PROJEKCI NEŘEŠ: izometrii má scripts/level.gd (cell_center, cell_at) — neopisuj ji sem a nezaváděj vlastní "
            "konstantu velikosti buňky; přesně kvůli druhému číslu mřížky byl starý world.gd přesunut do _retired/. "
            "Služby ber z registru rodiče: get_parent().component(id) — vzor je v scripts/mining.gd — a nikdy ne z /root/ "
            "(žádný autoload v projektu není). Neměň tests/, .forge/ ani project.godot."
        ),
    },
    {
        "id": "entity.player.api",
        "title": "Hráč — stav (hp/mana/cíl), move() a inventář (co už volají jiné komponenty)",
        "owns": ["scripts/player.gd"],
        "depends_on": ["core.attributes", "core.skills", "entity.item", "world.level"],
        "size_lines": "<= 180",
        "acceptance": ["tests", "wiring"],
        "prompt": (
            "Rozšiř scripts/player.gd (dnes umí jen pohyb klávesami přes _physics_process + _step a flash()). "
            "DOPLŇ PŘESNĚ TOHLE — jiné komponenty to už volají, nic víc: "
            "(1) move(dir: Vector2) -> void — posun o dir; izometrické osy ber z levelu, ne z vlastní konstanty "
            "(get_tree().get_first_node_in_group(\"level\") a jeho is_walkable_at; vzor je v _physics_process). "
            "(2) Stav: hp: int, max_hp: int, mana: int, max_mana: int, target (uzel nebo null) — čte je scripts/assist.gd. "
            "(3) Inventář: inventory: Array, add_item(item) -> void, remove_item(item) -> void a equipped "
            "(vybavená zbraň/zbroj) — volá je scripts/economy.gd (add_item/remove_item) a čte scripts/hud.gd (equipped). "
            "(4) die() -> void — vytvoří mrtvolu (Area2D se jménem Corpse ve skupině corpse) s předměty z těla, hráč zahodí "
            "výbavu a inventář, přijde o všechno na těle a přesune se na spawn (level.spawn_cell přes cell_center). "
            "(5) ZACHOVEJ beze změny: _step(target: Vector2) -> Vector2, _physics_process, flash(), signál collected "
            "a add_to_group(\"player\") v _ready() — testy je volají přímo. "
            "Struktura: začni `extends Area2D` (tak to je dnes), _init() bez povinného argumentu (CONVENTIONS.md §1f/§1g). "
            "Služby (atributy, skilly, předměty) ber z registru rodiče: get_parent().component(id) — vzor je "
            "v scripts/mining.gd; nikdy ne z /root/ (žádný autoload v projektu není). Neměň tests/, .forge/ ani project.godot."
        ),
    },
    {
        "id": "persist.save.state",
        "title": "Ukládání — inventář hráče a stav uzlů světa (co dnes uložit nelze)",
        "owns": ["scripts/save.gd"],
        "depends_on": ["persist.save", "entity.player.api", "world.nodes"],
        "size_lines": "<= 140",
        "acceptance": ["tests", "wiring"],
        "prompt": (
            "Rozši scripts/save.gd. Dnes ukládá atributy, dovednosti, zlato a pozici hráče (viz hlavička souboru) "
            "a když není co uložit, vrací false — to ZACHOVEJ. Přidej: "
            "(1) Inventář hráče a výbavu: player.inventory je pole předmětů; z každého ukládej jen DATA, ne objekt — "
            "slovník {\"id\": ..., \"trvanlivost\": ..., \"kvalita\": ...} (ConfigFile neumí ukládat objekty, spadlo by to "
            "až při ukládání). Při load() předměty znovu postav přes scripts/item.gd (GameItem) a vlož hráči add_item(); "
            "u vybavené zbraně/zbroje obnov, co hráč drží. "
            "(2) Stav uzlů světa: component(\"World\").snapshot() do sekce world a při load() restore(data). "
            "(3) Když komponenta chybí, ulož jen to, co jde, a OHLAS to přes push_warning (tichý úspěch je v tomhle "
            "souboru zakázaný — byl to nález z 2. 10. 2026). "
            "Zachovej save() -> bool a load() -> bool a chování bez registru (vrací false). "
            "Služby ber z registru rodiče: get_parent().component(id) (vzor v scripts/mining.gd), nikdy ne z /root/. "
            "Neměň tests/, .forge/ ani project.godot."
        ),
    },
]

def granule_text(g: dict) -> str:
    """Granule ve stylu souboru: 2 mezery na klíč, krátká pole na jednom řádku."""
    j = lambda v: json.dumps(v, ensure_ascii=False)
    return "\n".join([
        "    {",
        f'      "id": {j(g["id"])},',
        f'      "title": {j(g["title"])},',
        '      "kind": "code",',
        f'      "owns": {j(g["owns"])},',
        f'      "depends_on": {j(g["depends_on"])},',
        f'      "size_lines": {j(g["size_lines"])},',
        '      "model": "strong",',
        f'      "acceptance": {j(g["acceptance"])},',
        f'      "prompt": {j(g["prompt"])}',
        "    }",
    ])

# --- kontroly PŘED zápisem ---------------------------------------------------
existujici = {g["id"] for g in data["grains"]}
for g in NOVE:
    if g["id"] in existujici:
        print(f"CHYBA: {g['id']} už v roadmapě je")
        sys.exit(1)

vlastnici_main = [g["id"] for g in data["grains"] if "assets/levels/main.json" in g.get("owns", [])]
print(f"main.json dnes vlastní: {vlastnici_main or 'nikdo'} (nová granule ho dostane)")

# --- 1) vložit nové granule před konec pole grains ---------------------------
konec = text.rstrip()
if not konec.endswith("}\n  ]\n}") and not konec.endswith("}\n  ]\n}\n"):
    # posledný znak pole grains: '    }\n  ]\n}'
    if "\n  ]\n}" not in konec:
        print("CHYBA: nenašel jsem konec pole grains")
        sys.exit(1)
misto = konec.rindex("\n  ]\n}")
nove_text = ",\n" + ",\n".join(granule_text(g) for g in NOVE)
text = konec[:misto] + nove_text + konec[misto:] + "\n"

# --- 2) engine.shell: závislosti + odkaz na přesunutou izo projekci ----------
data2 = json.loads(text)
shell = next((g for g in data2["grains"] if g["id"] == "engine.shell"), None)
if shell is None:
    print("CHYBA: engine.shell v roadmapě není")
    sys.exit(1)

stare_deps = json.dumps(shell["depends_on"], ensure_ascii=False)
nove_deps = json.dumps(shell["depends_on"] + ["world.nodes", "entity.player.api"], ensure_ascii=False)
if text.count(f'"depends_on": {stare_deps},') != 1:
    print("CHYBA: řádek depends_on u engine.shell nenalezen 1×")
    sys.exit(1)
text = text.replace(f'"depends_on": {stare_deps},', f'"depends_on": {nove_deps},')
print("OK    engine.shell čeká i na world.nodes a entity.player.api")

STARE_API = "world.iso_position, level.cell_center, player.move"
NOVE_API = "level.cell_center (izometrie je v level.gd), player.move, world.is_walkable"
if text.count(STARE_API) != 1:
    print("CHYBA: v zadání engine.shell jsem nenašel seznam API 1×")
    sys.exit(1)
text = text.replace(STARE_API, NOVE_API)
print("OK    engine.shell: opraven odkaz na world.iso_position (přesunutý world.gd)")

# --- 3) validace a zápis -----------------------------------------------------
data3 = json.loads(text)
nove_ids = {g["id"] for g in data3["grains"]}
for g in NOVE:
    if g["id"] not in nove_ids:
        print(f"CHYBA: {g['id']} po zápise není v JSON")
        sys.exit(1)
CESTA.write_text(text, encoding="utf-8", newline="")
print(f"\nZapsáno: {len(text.encode('utf-8'))} B, granul celkem {len(data3['grains'])}")

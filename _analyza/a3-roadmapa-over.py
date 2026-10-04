"""ÚKOL 3: ověří každou granuli roadmapy proti `origin/main`.

PROČ PROTI BLOBU, NE PROTI DISKU: pracovní strom má necommitnuté změny
(`player.gd` z Úkolu 1/2), takže disk NENÍ to, co je v repu. `AGENTS.md`:
„Hotovo = soubor je v `main` A brána jeho funkci zavolala." Tohle měří přesně
tu první polovinu — a u API i druhou (hledá ji v TOM souboru, ne kdekoli).

CO SE MĚŘÍ (tři úrovně, každá jinak silná):
  1. `soubor`   — je `owns` v `origin/main`? (slabé, ale nutné)
  2. `api`      — je v TOM souboru deklarace smluvního API?
  3. `volajici` — volá to někdo jiný? (u granulí, které něco poskytují)

Výstup je tabulka pro zápis do `roadmap.json`; skript NIC nemění.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
HRA = KOREN / "games" / "uo-shadows"
GIT = KOREN / "orchestra" / "tools" / "git.cmd"


def blob(cesta: str) -> str | None:
    """Obsah souboru z `origin/main`, nebo None (v repu není)."""
    v = subprocess.run([str(GIT), "-C", str(HRA), "show", "origin/main:%s" % cesta],
                       capture_output=True, shell=True)
    if v.returncode != 0:
        return None
    return v.stdout.decode("utf-8", "replace")


def main() -> int:
    road = json.loads((HRA / ".forge" / "roadmap.json").read_text(encoding="utf-8"))
    grains = road["grains"]

    # Všechny soubory v origin/main (pro hledání volajících).
    v = subprocess.run([str(GIT), "-C", str(HRA), "ls-tree", "-r", "--name-only",
                        "origin/main", "--", "scripts", "tests"],
                       capture_output=True, shell=True)
    seznam = v.stdout.decode("utf-8", "replace").splitlines()
    strom = {}
    for c in seznam:
        if c.endswith(".gd"):
            strom[c] = blob(c) or ""

    print("souboru .gd v origin/main: %d\n" % len(strom))

    # Smluvní API, které granule slibuje (z jejího promptu / z ARCHITEKTURA.md).
    API = {
        "data.content": ("assets/data/skills.json", ['"tezba"', '"kovarstvi"']),
        "core.attributes": ("scripts/attributes.gd", ["func hodnota", "func derived", "var Str"]),
        "core.skills": ("scripts/skills.gd", ["func add", "func hodnota", "dovednosti"]),
        "world.level": ("scripts/level.gd", ["func load_file", "func is_walkable_cell",
                                             "func cell_center", "func reachable_count"]),
        "world.map": ("scripts/world.gd", ["func iso_position", "func gather", "func is_walkable"]),
        "entity.item": ("scripts/item.gd", ["func use", "func repair", "func broken"]),
        "entity.player": ("scripts/player.gd", ["func move", "func add_item", "func die"]),
        "sim.combat": ("scripts/combat.gd", ["func resolve"]),
        "sim.mining": ("scripts/mining.gd", ["func gather"]),
        "sim.crafting": ("scripts/crafting.gd", ["func smelt", "func forge", "func repair"]),
        "sim.economy": ("scripts/economy.gd", ["func price", "func buy", "func sell", "func gold"]),
        "entity.npc": ("scripts/npc.gd", ["func trade"]),
        "entity.enemy": ("scripts/enemy.gd", ["func attack", "func drop_loot"]),
        "sim.offline": ("scripts/offline.gd", ["func resolve"]),
        "sim.assist": ("scripts/assist.gd", ["func add_rule", "func evaluate"]),
        "persist.save": ("scripts/save.gd", ["func save", "func load"]),
        "ui.hud": ("scripts/hud.gd", ["func update"]),
        "engine.shell": ("scripts/game.gd", ["func component"]),
        "world.nodes": ("scripts/world.gd", ["func gather", "func is_walkable", "func snapshot"]),
        "entity.player.api": ("scripts/player.gd", ["func move", "func add_item", "func die"]),
        "tests.harness": ("tests/run_tests.gd", ["kontrol,", "selhání"]),
        "persist.save.state": ("scripts/save.gd", ["inventory", "snapshot"]),
    }

    for g in grains:
        gid = g["id"]
        owns = g.get("owns", [])
        cesta, klice = API.get(gid, (None, []))

        chybejici_soubory = [o for o in owns if o not in strom and blob(o) is None]
        obsah = blob(cesta) if cesta else None
        chybejici_api = []
        if obsah is None:
            chybejici_api = ["<SOUBOR V REPU NENI>"]
        else:
            chybejici_api = [k for k in klice if k not in obsah]

        # Volající: hledá se jméno poslední metody API v OSTATNÍCH souborech.
        volajici = []
        if obsah is not None and klice:
            jmena = [k.replace("func ", "") for k in klice if k.startswith("func ")]
            for jm in jmena:
                for c, t in strom.items():
                    if c == cesta:
                        continue
                    if re.search(r"[.\s]%s\s*\(" % re.escape(jm), t):
                        volajici.append("%s.%s" % (c.split("/")[-1], jm))

        stav = "OK" if not chybejici_soubory and not chybejici_api else "CHYBI"
        print("%-20s %-6s %s" % (gid, stav, "deklarovano: done=%s" % g.get("done")))
        print("      owns v repu : %s" % ("VSECHNY" if not chybejici_soubory
                                          else "CHYBI %s" % chybejici_soubory))
        print("      smluvni API : %s" % ("VSECHNY (%d)" % len(klice) if not chybejici_api
                                          else "CHYBI %s" % chybejici_api))
        print("      vola to nekdo: %s" % (", ".join(sorted(set(volajici))[:6]) or "NIKDO"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

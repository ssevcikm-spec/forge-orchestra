import pathlib as _pl

# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.
# Soubor je v `tools/`, takze `parents[1]` = `tools/..` = **ROOT REPA**.
# ⚠ H92/P18: `_PARENT` je tedy ROOT REPA (ne jeho rodič) — sourozenec repa
# (hra) se bere jako `_PARENT.parent / 'uo-shadows'`, NE `_PARENT / 'uo-shadows'`.
_PARENT = _pl.Path(__file__).resolve().parents[1]
"""Simulace DAG: co odblokuje dokončení které granule.

Odpovídá na „dá se zlepšit úspěšnost" z pohledu plánu: ukáže, jaké je pořadí
podle dopadu, ne podle pořadí v souboru. Bere v potaz, že některé granule jsou
hotové (buď v souboru `done: true`, nebo protože je conductor má jako 'done').
"""

import json
import pathlib
import sys

ROADMAP = pathlib.Path(
    _PARENT.parent / 'uo-shadows' / '.forge' / 'roadmap.json')
# ⚠ H92 (opraveno P18, 6. 10. 2026): tady stálo `_PARENT / 'uo-shadows'`.
# `_PARENT` je u souboru v `tools/` **ROOT REPA** (`parents[1]` = `tools/..`),
# takže cesta mířila na `...\forge-orchestra\uo-shadows` — a ta **NEEXISTUJE**
# (naměřeno P18: `FileNotFoundError`, nástroj tedy **vůbec neměřil**).
# SOUROZENEC repa je `_PARENT.parent / 'uo-shadows'` = `E:\Workspaces\uo-shadows`.
# Je to táž vada a táž oprava jako v `tools/lint-roadmapa.py` (H61).

# Hotovo podle conductora (D1) – granule, jejichž PR se sloučil.
HOTOVE_V_D1 = {"core.attributes", "entity.item", "sim.economy", "world.map"}


def nacti():
    return json.loads(ROADMAP.read_text(encoding="utf-8"))["grains"]


def simuluj(grains, hotove):
    """Vrací seznam granulí, které jsou po dokončení `hotove` připravené."""
    pripravene = []
    for g in grains:
        if g["id"] in hotove or g.get("done"):
            continue
        if all(d in hotove or next((x.get("done") for x in grains if x["id"] == d), False)
               for d in g.get("depends_on", [])):
            pripravene.append(g["id"])
    return pripravene


def main() -> int:
    grains = nacti()
    vsechny = {g["id"] for g in grains}

    # Výchozí stav: co je hotové (soubor + D1).
    hotove = {g["id"] for g in grains if g.get("done")} | HOTOVE_V_D1
    hotove &= vsechny

    print(f"Hotových: {len(hotove)}/{len(vsechny)}")
    print()

    # Připravené teď.
    ted = simuluj(grains, hotove)
    print(f"PŘIPRAVENÉ TEĎ ({len(ted)}): {', '.join(ted) or '(žádné)'}")
    print()

    # Co odblokuje každá připravená granule.
    print("DOPAD DOKONČENÍ (kolik granulí se odblokuje):")
    dopady = []
    for gid in ted:
        po = simuluj(grains, hotove | {gid})
        nove = [x for x in po if x not in ted]
        dopady.append((len(nove), gid, nove))

    for pocet, gid, nove in sorted(dopady, reverse=True):
        g = next(x for x in grains if x["id"] == gid)
        model = g.get("model", "any")
        print(f"  {gid:<16} model={model:<7} odblokuje {pocet}: {', '.join(nove) or '-'}")

    print()
    # Nejdelsi cesta DAG (co určuje celkovou dobu).
    def hloubka(gid, cache=None):
        if cache is None:
            cache = {}
        if gid in cache:
            return cache[gid]
        g = next((x for x in grains if x["id"] == gid), None)
        if not g:
            return 0
        deps = g.get("depends_on", [])
        cache[gid] = 1 + (max((hloubka(d, cache) for d in deps), default=0))
        return cache[gid]

    kriticka = sorted(((hloubka(gid), gid) for gid in vsechny), reverse=True)[:5]
    print("NEJDELŠÍ ZÁVISLOSTNÍ ŘETĚZY (určují celkovou dobu):")
    for h, gid in kriticka:
        g = next(x for x in grains if x["id"] == gid)
        print(f"  {gid:<16} hloubka={h}  model={g.get('model','any')}  "
              f"čeká na {len(g.get('depends_on', []))} granulí")
    return 0


if __name__ == "__main__":
    sys.exit(main())

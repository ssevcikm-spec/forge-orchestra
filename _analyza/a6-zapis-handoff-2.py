"""Doplní do `HANDOFF.md` §2.9 dva NOVÉ otevřené body z práce typu A (3. 10. 2026).

PROČ ZVLÁŠŤ: §26.6 je **záznam o provedení** (co session udělala). Otevřené body
mají podle konvence handoffu žít v **§2 „Co je OTEVŘENÉ"** — jinak je příští
session nenajde tam, kde je hledá (`AGENTS.md`: „Přepisuješ-li `HANDOFF.md`,
nic nesmí zmizet… otevřené body jsou nejdražší chyba předání").

Vkládá se PŘED kotvu `## 3. Nové nálezy N1–N9` — tedy na konec §2.
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HANDOFF = Path(__file__).resolve().parent.parent / "HANDOFF.md"
KOTVA = "## 3. Nové nálezy N1–N9 — kde jsou a co z nich plyne"

NOVE = """### 2.9 Dva nové otevřené body z práce typu A (3. 10. 2026)

**Oba vznikly tím, že se práce na hře udělala pořádně** — a nejsou to vady
měřidel, jsou to **důsledky dodání kódu**. Zapsané proto, aby se na ně
nezapomnělo: každý z nich **blokuje** něco jiného.

#### A) `entity.player` závisí na `world.map`, která NIKDY hotová nebyla

**Naměřeno** (`_analyza\\a3-roadmapa-over.py`, proti blobům v `origin/main`):

- `entity.player` má v `depends_on` **`world.map`** — a ta je od 3. 10. 2026
  **`done: false`**, protože její práce (`scripts/world.gd`, `gather()`,
  respawn) v `main` **nikdy nebyla** (`c651368` ho přesunul do `_retired/`).
- **Důsledek:** conductor `entity.player` **nevydá** — čeká na granuli, která
  hotová není.
- **A přitom lze vydat hned:** `entity.player.api` (granule, která stejnou práci
  dodává) čeká na `core.attributes`, `core.skills`, `entity.item`, `world.level`
  — **všechny čtyři jsou `done: true`**.

**Co rozhodnout:** má stará granule `entity.player` mít `world.map`
v závislostech dál? Práce, kterou dodává `entity.player.api`, `world.map`
**nepotřebuje** (bere `level.is_walkable_at`, tedy `world.level`).
**Je to ale zásah do DAG** — rozhodnout vědomě, ne mimochodem.

#### B) `persist.save.state` — kdo vlastní POZICI hráče

**Naměřeno** (nový stav vznikl prací typu A):

- `scripts/save.gd:52` ukládá pozici **podmíněně** `if hrac != null and
  "position" in hrac:` a `:84` ji stejně podmíněně načítá.
- **Do 3. 10. 2026 tenhle test nikdy neprošel** — hráč pozici neměl „viditelnou"
  tak, jak kód čekal. **Teď projde**, protože `player.gd` stav dostal.
- **Následek:** `load()` **přepíše spawn** pozicí ze souboru. To je změna
  chování ukládání, kterou nikdo nenaplánoval.

**Co rozhodnout:** vlastní pozici `player.gd` (a `save.gd` ji jen ukládá), nebo
se má hráč po načtení vracet na `level.spawn_cell`? **Patří to do smlouvy**
(`ARCHITEKTURA.md` §2.1), ne do kódu potichu.

"""


def main() -> int:
    if not HANDOFF.exists():
        print("CHYBA: %s neexistuje" % HANDOFF)
        return 2
    puvodni = HANDOFF.read_text(encoding="utf-8")
    if "### 2.9 Dva nové otevřené body" in puvodni:
        print("CHYBA: §2.9 uz v dokumentu je")
        return 2
    if puvodni.count(KOTVA) != 1:
        print("CHYBA: kotva je %dx" % puvodni.count(KOTVA))
        return 2

    novy = puvodni.replace(KOTVA, NOVE + KOTVA, 1)
    HANDOFF.write_text(novy, encoding="utf-8", newline="")

    zpet = HANDOFF.read_text(encoding="utf-8")
    for kont in ["### 2.9 Dva nové otevřené body",
                 "entity.player` závisí na `world.map`",
                 "kdo vlastní POZICI hráče"]:
        assert kont in zpet, "po zapisu chybi: %s" % kont
    assert zpet.count("### 2.9 ") == 1, "§2.9 je tam vickrat"
    assert KOTVA in zpet, "kotva §3 zmizela!"
    assert len(zpet) > len(puvodni), "dokument se nezvetsil"

    print("ZAPSANO do HANDOFF.md (§2.9)")
    print("  pred : %d radku" % len(puvodni.splitlines()))
    print("  po   : %d radku" % len(zpet.splitlines()))
    return 0


if __name__ == "__main__":
    sys.exit(main())

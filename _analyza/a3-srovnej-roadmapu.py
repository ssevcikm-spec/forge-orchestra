"""ÚKOL 3 (druhá verze): srovná `.forge/roadmap.json` se stavem `origin/main`.

PROČ DRUHÁ VERZE: první verze soubor NAČETLA A ZNOVU SERIALIZOVALA
(`json.dumps`) — a tím přeformátovala celý dokument: `"owns"` a `depends_on`
byly na jednom řádku, po zápisu se roztáhly na jeden prvek na řádek.
Naměřeno: `git diff --stat` hlásil **350 změněných řádků** za pět přidaných
hodnot. V takovém diffu se skutečná změna (`done`) nedá najít — a to je přesně
to, před čím varuje `overovani` §7.3 („nástroj, který jen přidá řádek, umí
rozvrátit soubor").

PROTO SE TEĎ MUTUJE TEXT, NE DATOVÁ STRUKTURA: každá náhrada je doslovná,
s assertem na POČET výskytů (`overovani` §9.8 — kotva bývá v souboru víckrát),
a JSON se po zápisu ZNOVU PARSuje. Zapisuje se `write_bytes` s LF — soubor je
v `.gitattributes` na `*.json text eol=lf` a `write_text` by LF přepsal na CRLF
(past z `dsh-prostredi` §5b).

CO SE OPRAVUJE A ČÍM JE TO DOLOŽENÉ (každé číslo naměřené, ne odhad):

A) `done: true` U PRÁCE, KTERÁ V `main` NENÍ:
   * `world.map` — `scripts/world.gd` v `origin/main` VŮBEC NENÍ
     (`git ls-tree -r origin/main -- scripts` ho neuvádí; `c651368` ho přesunul
     do `_retired/`). `gather()`/`is_walkable()`/respawn nejsou nikde.
   * `entity.player` — soubor v `main` JE (71 řádků), ale smluvní API `move()`,
     `add_item()`, `remove_item()`, `die()` v něm NEJSOU — a `economy.gd:39,47`
     je volá. Soubor existuje, práce ne.

B) `done` CHYBÍ U PRÁCE, KTERÁ V `main` JE (conductor ji proto vydá znovu):
   * `core.attributes` — `attributes.gd` (416 B) s `hodnota()` a `derived()`;
     PR #19 (`738a77d`).
   * `entity.item` — `item.gd` (1111 B) s `use()`/`repair()`/`broken()`;
     PR #20 (`f1e2899`).

C) `size_lines` U GRANULÍ, JEJICHŽ SOUBOR JE VĚTŠÍ NEŽ VÝCHOZÍCH 60:
   naměřeno 2. 10. 2026 — `save.gd` (+91), `hud.gd` (+77) a `mining.gd` (+67)
   skončily jako visící PR, protože granule velikost nedeklarovala a gate
   auto-merge použil výchozích 60. Hodnoty jsou ZMĚŘENÉ VELIKOSTI v `main`
   (`splitlines()`), `model` zůstává `any` — deklaruje se VELIKOST.

CO SE ZÁMĚRNĚ NEMĚNÍ: `size_lines` u granulí, které ho nemají a mají zůstat
bez něj. `lint-roadmapa.py:104-110` říká, že `size_lines` mají jen granule pro
silný model a u slabého je výchozích 60 SPRÁVNĚ — plošné doplnění by o granuli
tvrdilo něco, co neplatí.
"""
import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROADMAP = (Path(__file__).resolve().parent.parent
           / "games" / "uo-shadows" / ".forge" / "roadmap.json")

# (popis, doslovný text v souboru, čím se nahradí, očekávaný počet výskytů)
ZMENY = [
    ('world.map: done true -> false', '"id": "world.map",', None, 0),
    ('entity.player: done true -> false', '"id": "entity.player",', None, 0),
    ('core.attributes: doplnit done true', '"id": "core.attributes",', None, 0),
    ('entity.item: doplnit done true', '"id": "entity.item",', None, 0),
]


def zmen_done(text: str, gid: str, hodnota: bool) -> tuple[str, str]:
    """Změní/nastaví `done` U KONKRÉTNÍ GRANULE (ne první výskyt v souboru).

    Past `overovani` §7.11: `re.search` na „první výskyt" měří něco jiného.
    Tady se okno vymezí řádkem s `"id": "<gid>"` a hledá se jen do konce toho
    objektu — proto se `done` nedá splést s `done` jiné granule.
    """
    kotva = '"id": "%s",' % gid
    if text.count(kotva) != 1:
        return text, "CHYBA: kotva '%s' je v souboru %dx" % (kotva, text.count(kotva))
    i = text.index(kotva)
    konec = text.index("\n    },", i)          # konec objektu granule
    usek = text[i:konec]
    cil = '"done": %s,' % ("true" if hodnota else "false")

    if '"done": true,' in usek:
        if not hodnota:
            novy = usek.replace('"done": true,', '"done": false,', 1)
            return text[:i] + novy + text[konec:], "done true -> false"
        return text, "done uz je true (beze zmeny)"
    if '"done": false,' in usek:
        if hodnota:
            novy = usek.replace('"done": false,', '"done": true,', 1)
            return text[:i] + novy + text[konec:], "done false -> true"
        return text, "done uz je false (beze zmeny)"
    # `done` tam není — vloží se za `depends_on`, aby pořadí klíčů zůstalo
    if not hodnota:
        return text, "done chybi a ma zustat false (beze zmeny)"
    m = usek.index("\n      \"acceptance\"")
    novy = usek[:m] + '\n      "done": true,' + usek[m:]
    return text[:i] + novy + text[konec:], "done VLOZENO true"


def pridej_size(text: str, gid: str, hodnota: str) -> tuple[str, str]:
    """Doplní `size_lines` do granule `gid` (za `model`, nebo za `owns`)."""
    kotva = '"id": "%s",' % gid
    if text.count(kotva) != 1:
        return text, "CHYBA: kotva '%s' je %dx" % (kotva, text.count(kotva))
    i = text.index(kotva)
    konec = text.index("\n    },", i)
    usek = text[i:konec]
    if '"size_lines"' in usek:
        return text, "size_lines uz je (beze zmeny)"
    novy_radek = '\n      "size_lines": "%s",' % hodnota
    if '\n      "model": "any",' in usek:
        m = usek.index('\n      "model": "any",') + len('\n      "model": "any",')
        novy = usek[:m] + novy_radek + usek[m:]
    else:
        m = usek.index('\n      "acceptance"')
        novy = usek[:m] + novy_radek + usek[m:]
    return text[:i] + novy + text[konec:], "size_lines %s VLOZENO" % hodnota


def main() -> int:
    orig = ROADMAP.read_bytes()
    if b"\r\n" in orig:
        print("CHYBA: soubor ma CRLF, ale .gitattributes chce LF")
        return 2
    text = orig.decode("utf-8")

    chyby = 0
    print("=== A) done U PRACE, KTERA V main NENI ===")
    for gid in ["world.map", "entity.player"]:
        text, co = zmen_done(text, gid, False)
        chyby += "CHYBA" in co
        print("  %-18s %s" % (gid, co))

    print("\n=== B) done U PRACE, KTERA V main JE ===")
    for gid in ["core.attributes", "entity.item"]:
        text, co = zmen_done(text, gid, True)
        chyby += "CHYBA" in co
        print("  %-18s %s" % (gid, co))

    print("\n=== C) size_lines (zmerene velikosti v main) ===")
    for gid, hodn in [("world.level", "<= 300"), ("ui.hud", "<= 100"),
                      ("persist.save", "<= 100"), ("sim.mining", "<= 80"),
                      ("sim.combat", "<= 130")]:
        text, co = pridej_size(text, gid, hodn)
        chyby += "CHYBA" in co
        print("  %-18s %s" % (gid, co))

    if chyby:
        print("\nNIC SE NEZAPISUJE — %d chyb v kotvách" % chyby)
        return 2

    ROADMAP.write_bytes(text.encode("utf-8"))

    # Po zápisu ZNOVU PARSOVAT a ověřit OBSAH, ne jen že soubor vznikl.
    zpet = json.loads(ROADMAP.read_bytes().decode("utf-8"))
    podle_id = {g["id"]: g for g in zpet["grains"]}
    assert len(zpet["grains"]) == 22, "pocet granulí se zmenil: %d" % len(zpet["grains"])
    for gid, ocekavane in [("world.map", False), ("entity.player", False),
                           ("core.attributes", True), ("entity.item", True)]:
        assert podle_id[gid].get("done") is ocekavane, "%s.done nesedi" % gid
    for gid in ["world.level", "ui.hud", "persist.save", "sim.mining", "sim.combat"]:
        assert podle_id[gid].get("size_lines"), "%s.size_lines chybi" % gid

    b = ROADMAP.read_bytes()
    assert b"\r\n" not in b, "zapsaly se CRLF!"

    hotove = [g["id"] for g in zpet["grains"] if g.get("done") is True]
    bez_vel = [g["id"] for g in zpet["grains"] if not g.get("size_lines")]
    print("\n=== STAV PO ZAPISE ===")
    print("  granulí        : %d (JSON znovu naparsovan: OK)" % len(zpet["grains"]))
    print("  done=true      : %d" % len(hotove))
    print("  done=false     : %s" % [g["id"] for g in zpet["grains"] if g.get("done") is False])
    print("  bez size_lines : %d (model any = výchozích 60 je SPRÁVNĚ)" % len(bez_vel))
    print("  konce řádků    : LF (dle .gitattributes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())

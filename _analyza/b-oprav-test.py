#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Úkol B — vloží do `tests/run_tests.gd` test, který `combat.resolve()` ZAVOLÁ.

Zamění blok, který se ptal jen na PŘÍTOMNOST metody:

    var combat_sc = load("res://scripts/combat.gd")
    if combat_sc != null:
        var cb = _instantiate("boj", "res://scripts/combat.gd")
        _check(cb.has_method("resolve"), "combat.gd poskytuje resolve(att, def)")
        _zavri(cb)

…za blok, který `resolve()` zavolá a ověří `{hit, damage}` (a přidá k tomu
atrapy `TestBojovnik` a `TestZbran`).

Starý blok se VYTÁHNE ZE SOUBORU (`_analyza\\b-stary-blok-boj.gd`) — neopisuje
se ručně. U Úkolu A se ruční opis `\\"` vymstil: patcher pak blok nenašel
a „oprava" se tichounce neprovedla.

Použití:
    python _analyza\\b-oprav-test.py <cesta-ke-klonu>
    python _analyza\\b-oprav-test.py <cesta-ke-klonu> --zpet
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
SOUBOR_BLOK = ANALYZA / "b-novy-blok-boj.gd"
SOUBOR_ATRAPA = ANALYZA / "b-nova-atrapa-zbran.gd"

KLIC_STARY = 'cb.has_method("resolve")'
KLIC_NOVY = 'combat.resolve() umí zásah i minutí'


def vytahni_stary(cesta: Path) -> str:
    """Vytáhne starý blok `combat` (od `var combat_sc = load(...)` po `_zavri(cb)`)."""
    radky = cesta.read_text(encoding="utf-8").splitlines(keepends=True)
    start = konec = None
    for i, r in enumerate(radky):
        if start is None and 'var combat_sc = load("res://scripts/combat.gd")' in r:
            start = i
        elif start is not None and r.strip() == "_zavri(cb)":
            konec = i
            break
    if start is None or konec is None:
        return ""
    return "".join(radky[start:konec + 1])


def main() -> int:
    if len(sys.argv) < 2:
        print("použití: python _analyza\\b-oprav-test.py <cesta-ke-klonu> [--zpet]")
        return 2
    zaklad = Path(sys.argv[1]).resolve()
    zpet = "--zpet" in sys.argv
    cesta = zaklad / "tests" / "run_tests.gd"
    if not cesta.exists():
        print("CHYBA: %s neexistuje" % cesta)
        return 2
    for s in (SOUBOR_BLOK, SOUBOR_ATRAPA):
        if not s.exists():
            print("CHYBA: chybí %s" % s)
            return 2

    text = cesta.read_text(encoding="utf-8")
    novy_blok = SOUBOR_BLOK.read_text(encoding="utf-8")
    atrapa = SOUBOR_ATRAPA.read_text(encoding="utf-8")

    # ------------------------------------------------------------- zpět ------
    if zpet:
        stary = (ANALYZA / "b-stary-blok-boj.gd")
        if not stary.exists():
            print("CHYBA: chybí %s (vyrob ho přes --vyrob-stary)" % stary)
            return 2
        stary_text = stary.read_text(encoding="utf-8")
        if stary_text in text:
            print("OK: soubor už je v původním stavu")
            return 0
        if novy_blok not in text or atrapa.strip() not in text:
            print("CHYBA: nový blok nenalezen — nelze vrátit")
            return 2
        v = text.replace(novy_blok, stary_text, 1)
        if atrapa in v:
            v = v.replace(atrapa, "", 1)
        elif atrapa.strip() in v:
            # atrapa byla vložena bez úvodních prázdných řádků
            v = v.replace("\n\n" + atrapa.strip() + "\n", "\n", 1)
        assert v != text, "MUTACE NEPROBĚHLA"
        cesta.write_bytes(v.encode("utf-8"))
        k = cesta.read_text(encoding="utf-8")
        assert KLIC_STARY in k and KLIC_NOVY not in k
        print("OK: %s vrácen (%d znaků)" % (cesta, len(k)))
        return 0

    # ---------------------------------------------------------- dopředu -----
    if KLIC_NOVY in text:
        print("OK: oprava už v souboru je")
        return 0

    stary_blok = vytahni_stary(cesta)
    if not stary_blok:
        print("CHYBA: starý blok `combat` v %s nenalezen" % cesta)
        return 2
    if KLIC_STARY not in stary_blok:
        print("CHYBA: vytažený blok neobsahuje %r" % KLIC_STARY)
        return 2
    if text.count(stary_blok) != 1:
        print("CHYBA: starý blok nalezen %d× — očekávám 1×" % text.count(stary_blok))
        return 2
    # ulož si ho pro --zpet
    (ANALYZA / "b-stary-blok-boj.gd").write_bytes(stary_blok.encode("utf-8"))

    v = text.replace(stary_blok, novy_blok, 1)
    if not v.endswith("\n"):
        v += "\n"
    v += atrapa

    assert v != text, "MUTACE NEPROBĚHLA"
    cesta.write_bytes(v.encode("utf-8"))

    k = cesta.read_text(encoding="utf-8")
    assert k == v, "zapsaný obsah nesedí"
    assert KLIC_STARY not in k, "stará kontrola v souboru zůstala"
    assert KLIC_NOVY in k, "nový blok se nevložil"
    assert "TestBojovnik" in k and "TestZbran" in k, "atrapy se nevložily"
    if "\\t" in k:
        print("CHYBA: v souboru je literální '\\t' místo tabulátoru — Godot by spadl")
        return 2
    print("OK: %s přepsán (%d → %d znaků)" % (cesta, len(text), len(k)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

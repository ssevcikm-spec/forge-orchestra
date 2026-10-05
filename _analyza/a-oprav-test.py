#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Oprava Úkolu A v souboru `tests/run_tests.gd` (klon nebo pracovní strom).

Zamění statickou kontrolu (hledá řetězec `level.iso_position` v CELÉM souboru
`player.gd`) za kontrolu, která `move()` ZAVOLÁ a změří, na kom se ptala na izo
projekci. Přidá k tomu atrapu úrovně `TestUrovenBezIzo`.

PROČ SOUBOREM A NE `-replace` V POWERSHELLU:
  blok obsahuje `\\"`, tabulátory a české znaky. V PowerShellu se taková mutace
  tiche neprovede (skill `overovani` §7.9 a §7.12) a výsledek pak vypadá jako
  „kontrola je slepá", i když se jen nezměnil soubor.

PROČ SE BLOKY ČTOU Z `.gd` SOUBORŮ:
  první verze měla bloky zapsané v Python literálech — a `\\t` v nich zůstalo
  dvěma znaky (`\\` + `t`) místo tabulátoru, takže Godot ohlásil
  `Parse Error: Unexpected "extends" in class body` a **testy nedoběhly vůbec**.
  Přesně to je past, před kterou varuje `AGENTS.md`: „brána, která neproběhla,
  není červená — je nezměřená". Bloky proto leží ve `_analyza\\a-novy-blok.gd`
  a `_analyza\\a-nova-atrapa.gd`, odkud se čtou **bajt na bajt**.

Použití:
    python _analyza\\a-oprav-test.py <cesta-ke-klonu>
    python _analyza\\a-oprav-test.py <cesta-ke-klonu> --zpet
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
SOUBOR_BLOK = ANALYZA / "a-novy-blok.gd"
SOUBOR_ATRAPA = ANALYZA / "a-nova-atrapa.gd"

# Starý blok — opsán z `run_tests.gd:834–840` (bajt na bajt, včetně `\"`).
# Čte se ze souboru, ne z literálu: escapování uvozovek v Pythonu je přesně to,
# co se dá snadno napsat špatně a co pak tichounce mine.
SOUBOR_STARY = ANALYZA / "a-stary-blok.gd"


def main() -> int:
    if len(sys.argv) < 2:
        print("použití: python _analyza\\a-oprav-test.py <cesta-ke-klonu> [--zpet]")
        return 2
    zaklad = Path(sys.argv[1]).resolve()
    zpet = "--zpet" in sys.argv
    cesta = zaklad / "tests" / "run_tests.gd"
    if not cesta.exists():
        print("CHYBA: %s neexistuje" % cesta)
        return 2

    for s in (SOUBOR_BLOK, SOUBOR_ATRAPA, SOUBOR_STARY):
        if not s.exists():
            print("CHYBA: chybí %s" % s)
            return 2

    stara = SOUBOR_STARY.read_text(encoding="utf-8")
    nova = SOUBOR_BLOK.read_text(encoding="utf-8")
    atrapa = SOUBOR_ATRAPA.read_text(encoding="utf-8")

    text = cesta.read_text(encoding="utf-8")

    if zpet:
        if stara in text:
            print("OK: soubor už je v původním stavu, není co vracet")
            return 0
        if nova not in text or atrapa.strip() not in text:
            print("CHYBA: nový blok v souboru nenalezen — nelze vrátit")
            return 2
        novy = text.replace(nova, stara, 1).replace(atrapa, "", 1)
        assert novy != text, "MUTACE NEPROBĚHLA"
        cesta.write_bytes(novy.encode("utf-8"))
        kontrola = cesta.read_text(encoding="utf-8")
        assert kontrola == novy, "zapsaný obsah nesedí"
        assert stara in kontrola and "TestUrovenBezIzo" not in kontrola
        print("OK: %s vrácen do původního stavu (%d znaků)" % (cesta, len(kontrola)))
        return 0

    # ------------------------------------------------------------------ dopředu
    if nova in text:
        print("OK: oprava už v souboru je, není co dělat")
        return 0
    pocet = text.count(stara)
    if pocet != 1:
        print("CHYBA: stará kontrola nalezena %d× — očekávám právě 1×." % pocet)
        print("       (Kdybych to nezkontroloval, 'oprava' by se tiche neprovedla.)")
        return 2

    novy = text.replace(stara, nova, 1)
    if not novy.endswith("\n"):
        novy += "\n"
    novy += atrapa

    assert novy != text, "MUTACE NEPROBĚHLA (text se nezměnil)"
    cesta.write_bytes(novy.encode("utf-8"))

    z5 = cesta.read_text(encoding="utf-8")
    assert z5 == novy, "zapsaný obsah nesedí se zamýšleným"
    assert "player_zdroj" not in z5, "stará kontrola v souboru zůstala"
    assert "TestUrovenBezIzo" in z5, "nová atrapa se nevložila"
    # Pojistka proti přesně té vadě, kterou měla první verze patcheru:
    # `\t` jako dva znaky místo tabulátoru → Godot spadne na parse error.
    if "\\t" in z5:
        print("CHYBA: v souboru je literální '\\t' místo tabulátoru — Godot by spadl")
        return 2
    print("OK: %s přepsán (%d → %d znaků)" % (cesta, len(text), len(z5)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

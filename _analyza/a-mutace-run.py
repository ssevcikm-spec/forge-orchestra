#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Mutační běhy pro Úkol A — testy hry nad klonem repa v `_analyza\\a-ukol-scratch`.

PROČ TO EXISTUJE (a proč to není `python -c`):
  * `python -c` s českým textem v PowerShellu rozbije diakritiku (skill
    `dsh-prostredi` §3d) — mutace se pak TICHE NEPROVEDE a test „projde"
    na nezměněném souboru (skill `overovani` §7.9 a §7.12).
  * Proto: mutace se zapisují **soubor od souboru, v Pythonu, s `encoding='utf-8'`**
    a po každém zápisu se **ověří, že text na disku je skutečně jiný**
    (`assert`). Když se mutace neprovede, skript skončí nenulově.

Použití:
    $env:PYTHONIOENCODING='utf-8'
    python _analyza\\a-mutace-run.py zaklad
    python _analyza\\a-mutace-run.py pres-level
    python _analyza\\a-mutace-run.py pres-world
    python _analyza\\a-mutace-run.py bez-move
"""

import os
import re
import subprocess
import sys
from pathlib import Path

KOREN = Path(__file__).resolve().parent.parent
SCRATCH = KOREN / "_analyza" / "a-ukol-scratch"
GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
USER_DIR = KOREN / "_analyza" / "a-godot-user"

PLAYER = SCRATCH / "scripts" / "player.gd"
TESTS = SCRATCH / "tests" / "run_tests.gd"

# Kotva, na kterou se vkládá `move()` — hned za `_step(...)`.
KOTVA = "func flash() -> void:"

MOVE_PRES_LEVEL = '''
func move(dir: Vector2) -> void:
	"""MUTACE M1: `move()` se ptá na izo projekci ÚROVNĚ.

	Tohle je přesně vada, kterou má kontrola chytit. `TestUrovenBezIzo`
	`iso_position` nemá (stejně jako `level.gd`), takže se ptáme přes
	`ma_iso()` — atrapa to počítá a vrátí false.
	"""
	var d := dir
	if level != null and level.has_method("ma_iso") and level.ma_iso():
		var iso := Vector2((d.x - d.y) * 0.5, (d.x + d.y) * 0.25)
		if iso.length() > 0:
			iso = iso.normalized()
		d = iso * SPEED
	position = _step(position + d * 0.016)


'''

MOVE_ZDRAVY = '''
func move(dir: Vector2) -> void:
	"""ZDRAVÁ implementace: `move()` se izo projekce na úrovni VŮBEC neptá.

	Izometrii řeší `_step()` přes `is_walkable_at` — tedy průchodnost,
	ne projekci. Přesně to smí dělat i bez registru komponent.
	"""
	var d := dir
	if d.length() > 0:
		d = d.normalized()
	position = _step(position + d * SPEED * 0.016)


'''


def precti(cesta: Path) -> str:
    return cesta.read_text(encoding="utf-8")


def zapis_a_over(cesta: Path, novy: str, popis: str) -> None:
    """Zapíše soubor a OVĚŘÍ, že na disku je skutečně to, co jsme zamýšleli."""
    stary = precti(cesta)
    if novy == stary:
        print("CHYBA: %s — obsah se nezměnil, mutace by se tiche neprovedla" % popis)
        sys.exit(2)
    cesta.write_bytes(novy.encode("utf-8"))
    na_disku = precti(cesta)
    if na_disku != novy:
        print("CHYBA: %s — zapsaný obsah nesedí s zamýšleným" % popis)
        sys.exit(2)
    print("  mutace zapsaná a ověřená: %s (%d → %d znaků)"
          % (popis, len(stary), len(novy)))


def vloz_move(blok: str, popis: str) -> None:
    text = precti(PLAYER)
    if "func move(" in text:
        print("CHYBA: v %s už `move()` je — scratch není čistý" % PLAYER)
        sys.exit(2)
    if KOTVA not in text:
        print("CHYBA: v %s není kotva %r" % (PLAYER, KOTVA))
        sys.exit(2)
    zapis_a_over(PLAYER, text.replace(KOTVA, blok.lstrip("\n") + KOTVA, 1), popis)


def zahod_zmeny() -> None:
    """Vrátí PRACOVNÍ STROM scratch do stavu HEAD (patch i mutace pryč).

    Pozor: tohle není `obnov()` — to by smazalo i opravený test.

    ⚠ PROČ SE `tests/run_tests.gd` Z KLONU NESYNCUJE (a `combat.gd` ano):
    v klonu je už i **blok Úkolu B** (`combat.resolve()`), a ten volá
    `cb.resolve(...)`, což v holém scratchi bez `combat.gd` z Úkolu B spadne —
    testy pak dají `exit 2` a měření Úkolu A je popsané špatně.
    Tenhle runner proto testuje **jen Úkol A**: `combat.gd` bere z klonu
    (aby soubor odpovídal repu), ale testy si staví sám patchem
    `a-oprav-test.py`. Úkol B má vlastní runner `b-mutace.py`.
    """
    r = subprocess.run(
        [str(KOREN / "orchestra" / "tools" / "git.cmd"), "-C", str(SCRATCH),
         "checkout", "--", "."],
        capture_output=True, shell=True,
    )
    if r.returncode != 0:
        print("CHYBA: návrat scratch nezdařil:\n%s" % r.stderr.decode("utf-8", "replace"))
        sys.exit(2)
    import shutil
    for rel in ("scripts/combat.gd",):
        zdroj = KOREN / "games" / "uo-shadows" / rel
        cil = SCRATCH / rel
        if zdroj.is_file() and cil.parent.is_dir():
            shutil.copyfile(zdroj, cil)


def oprav_test() -> None:
    """Nasadí opravu testu (Úkol A) do scratch, pokud tam ještě není."""
    r = subprocess.run(
        [sys.executable, str(KOREN / "_analyza" / "a-oprav-test.py"), str(SCRATCH)],
        capture_output=True,
    )
    vystup = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    print("  a-oprav-test.py: %s" % vystup.strip().splitlines()[-1] if vystup.strip() else "")
    if r.returncode != 0:
        print(vystup)
        sys.exit(2)
    if "TestUrovenBezIzo" not in precti(TESTS):
        print("CHYBA: oprava testu se nepropsala do %s" % TESTS)
        sys.exit(2)


def spust_testy(popis: str) -> int:
    USER_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(USER_DIR)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        [str(GODOT), "--headless", "--path", str(SCRATCH),
         "--script", "res://tests/run_tests.gd"],
        capture_output=True, env=env, timeout=180,
    )
    vystup = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    print("\n" + "=" * 78)
    print("BĚH: %s   (exit=%d)" % (popis, r.returncode))
    print("=" * 78)
    for radek in vystup.splitlines():
        if "[test]" in radek:
            print(radek)
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", vystup)
    if m:
        print("  → SOUHRN: %s kontrol, %s selhání" % (m.group(1), m.group(2)))
    else:
        print("  → SOUHRN: NENALEZEN (běh nedoběhl k _finish) — celý výstup:")
        print(vystup[-3000:])
    return r.returncode


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    rezim = sys.argv[1]
    if not PLAYER.exists():
        print("CHYBA: scratch neexistuje na %s" % PLAYER)
        return 2

    # Každý režim začíná z ČISTÉHO stavu HEAD (žádná mutace, PŮVODNÍ test).
    zahod_zmeny()
    if "func move(" in precti(PLAYER) or "TestUrovenBezIzo" in precti(TESTS):
        print("CHYBA: scratch není čistý ani po checkoutu")
        return 2

    if rezim == "pred-opravou":
        # Kontrolní běh: dnešní test bez jakékoli změny. Musí dát 59/0.
        print("BĚH: dnešní testy na origin/main (BEZ opravy Úkolu A)")

    elif rezim in ("bez-move", "pres-level", "zdravy"):
        oprav_test()
        if rezim == "pres-level":
            vloz_move(MOVE_PRES_LEVEL, "M1: move() se ptá na izo projekci úrovně")
            print("BĚH: OPRAVENÝ test + M1 (move() přes úroveň) → očekávám 1 SELHÁNÍ")
        elif rezim == "zdravy":
            vloz_move(MOVE_ZDRAVY, "M2: zdravé move() (izo projekci úrovně neřeší)")
            print("BĚH: OPRAVENÝ test + M2 (zdravá implementace) → očekávám 0 selhání")
        else:
            print("BĚH: OPRAVENÝ test, `move()` v repu NENÍ → očekávám 59/0 + poznámku")

    elif rezim == "stary-test-pres-level":
        # PROTI-DŮKAZ: vrací vadu do kódu a nechává PŮVODNÍ test. Musí projít
        # (tedy: původní test vadu NEVIDÍ, i když je v kódu).
        vloz_move(MOVE_PRES_LEVEL, "M1 do kódu, ale test zůstává PŮVODNÍ")
        print("BĚH: PŮVODNÍ test + M1 v kódu → když projde, původní test vadu nevidí")

    else:
        print("neznámý režim: %s" % rezim)
        print(__doc__)
        return 2

    return spust_testy(rezim)


if __name__ == "__main__":
    sys.exit(main())

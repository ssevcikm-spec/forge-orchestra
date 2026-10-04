#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MUTAČNÍ TEST Úkolu B — umí nový test spadnout na vrácené vadě?

Vrací do `combat.gd` přesně tu vadu, která tam byla naměřená 2. 10. 2026:

  M1  `"armor_rating" in defender`  ->  `defender.has("armor_rating")`
      (Godot 3 API — v Godotu 4 `Object.has()` NEEXISTUJE)
  M2  `"damage" in zbran`           ->  `zbran.has("damage")`

OBĚ jsou UVNITŘ `if hit:` (M2 navíc jen když má útočník zbraň), takže vada je
PRAVDĚPODOBNOSTNÍ: bez hledání zásahu by test mohl projít i s vrácenou vadou.
Proto test hledá zásah mezi semínky 1..40.

PROČ SOUBOREM A NE `-replace` V POWERSHELLU: mutace se musí ověřit na výstupu
(`assert` po přečtení z disku) — jinak „test prošel" znamená jen to, že se
mutace tiche neprovedla (skill `overovani` §7.9 a §7.12).

Použití:
    python _analyza\\b-mutace.py <cesta-ke-scratch>            # spustí obě mutace
    python _analyza\\b-mutace.py <cesta-ke-scratch> --jen M1
"""

import os
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
USER_DIR = KOREN / "_analyza" / "a-godot-user"

MUTACE = {
    "M1": {
        "popis": 'zbroj: "armor_rating" in defender -> defender.has("armor_rating")',
        "najdi": 'if typeof(defender) == TYPE_OBJECT and "armor_rating" in defender:\n\t\tzbroj = int(defender.armor_rating)',
        "nahrad": 'if typeof(defender) == TYPE_OBJECT and defender.has("armor_rating"):\n\t\tzbroj = int(defender.armor_rating)',
    },
    "M2": {
        "popis": 'zbraň: "damage" in zbran -> zbran.has("damage")',
        "najdi": 'if zbran != null and "damage" in zbran:\n\t\tzbran_poskozeni = int(zbran.damage)',
        "nahrad": 'if zbran != null and zbran.has("damage"):\n\t\tzbran_poskozeni = int(zbran.damage)',
    },
}


def spust(cesta_a: Path) -> tuple:
    USER_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(USER_DIR)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run(
        [str(GODOT), "--headless", "--path", str(cesta_a),
         "--script", "res://tests/run_tests.gd"],
        capture_output=True, env=env, timeout=300,
    )
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", v)
    if not m:
        return (None, None, v)
    return (int(m.group(1)), int(m.group(2)), v)


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    scratch = Path(sys.argv[1]).resolve()
    combat = scratch / "scripts" / "combat.gd"
    if not combat.exists():
        print("CHYBA: %s neexistuje" % combat)
        return 2

    # ⚠ Pracovní strom se musí NEJDŘÍV synchronizovat s klonem — a to OBA
    # soubory: `combat.gd` I `tests/run_tests.gd`. Když se synchronizuje jen
    # jeden, testy neobsahují blok s `resolve()` a mutace PROJDE, protože se
    # nic nevolá. Přesně to se stalo 2. 10. 2026 a vypadalo to jako
    # „slepá brána" — přitom to byla slepá SYNCHRONIZACE.
    # (Obecné pravidlo: než označíš bránu za slepou, ověř, že ta kontrola
    #  vůbec JE v souboru, který se spustil.)
    #
    # ⚠ A DRUHÁ PAST: runner Úkolu A (`a-mutace-run.py`) dělá na začátku
    # `git checkout -- .`, takže testy v scratchi vrátí na verzi bez bloku B.
    # Tenhle skript proto NESMÍ spoléhat na stav, který tam nechal někdo jiný —
    # synchronizuje si oba soubory sám na začátku (a `git checkout` nevolá).
    import shutil
    for rel in ("scripts/combat.gd", "tests/run_tests.gd", "scripts/player.gd"):
        zdroj = KOREN / "games" / "uo-shadows" / rel
        cil = scratch / rel
        if zdroj.is_file() and cil.parent.is_dir() and zdroj.read_bytes() != cil.read_bytes():
            shutil.copyfile(zdroj, cil)
            print("synchronizováno z klonu: %s" % rel)

    # Kontrola, že testovací blok je opravdu v tom, co se spustí.
    testy = (scratch / "tests" / "run_tests.gd").read_text(encoding="utf-8")
    if "combat.resolve() umí zásah i minutí" not in testy:
        print("CHYBA: v %s není blok s `combat.resolve()` — mutace by měřila něco jiného"
              % (scratch / "tests" / "run_tests.gd"))
        return 2

    # import cache (`.godot/`) — bez ní se nenačtou assety a testy dají 57/3
    zdroj_godot = KOREN / "games" / "uo-shadows" / ".godot"
    if zdroj_godot.is_dir() and not (scratch / ".godot").is_dir():
        shutil.copytree(zdroj_godot, scratch / ".godot")
        print("zkopírována import cache (.godot)")

    jen = None
    if "--jen" in sys.argv:
        jen = sys.argv[sys.argv.index("--jen") + 1]

    puvodni = combat.read_text(encoding="utf-8")
    # Pozor: `Dictionary.has()` je LEGITIMNÍ a v souboru je (větev pro slovník).
    # Proto se čistota nepozná podle `.has(`, ale podle PŘESNÉHO textu mutací.
    for jmeno, mut in MUTACE.items():
        if mut["nahrad"] in puvodni:
            print("CHYBA: scratch už vadu %s obsahuje — není čistý" % jmeno)
            return 2

    # 1) kontrola: zdravý kód musí projít
    kontroly, selhani, _ = spust(scratch)
    print("ZDRAVÝ KÓD:        %s kontrol, %s selhání  %s"
          % (kontroly, selhani, "OK" if selhani == 0 else "!! CHYBA"))
    if selhani != 0:
        print("   → brána neprojde ani na zdravém kódu; mutace by nic nedokázala")
        return 2

    vysledky = []
    for jmeno, mut in MUTACE.items():
        if jen and jmeno != jen:
            continue
        if mut["najdi"] not in puvodni:
            print("CHYBA: %s — hledaný text v combat.gd není:" % jmeno)
            print(repr(mut["najdi"]))
            return 2
        if puvodni.count(mut["najdi"]) != 1:
            print("CHYBA: %s — text nalezen %d×, očekávám 1×"
                  % (jmeno, puvodni.count(mut["najdi"])))
            return 2

        zmutovany = puvodni.replace(mut["najdi"], mut["nahrad"], 1)
        assert zmutovany != puvodni, "MUTACE NEPROBĚHLA"
        combat.write_bytes(zmutovany.encode("utf-8"))

        # OVĚŘ Z DISKU, že vada tam skutečně je (ne jen v paměti)
        z5 = combat.read_text(encoding="utf-8")
        assert z5 == zmutovany, "zapsaný obsah nesedí"
        if mut["nahrad"] not in z5:
            print("CHYBA: %s — vada se do souboru nezapsala" % jmeno)
            return 2
        print("\n%s: %s" % (jmeno, mut["popis"]))
        print("   ověřeno na disku: vada je v %s" % combat.name)

        kontroly, selhani, vystup = spust(scratch)
        print("   VÝSLEDEK: %s kontrol, %s selhání" % (kontroly, selhani))
        for radek in vystup.splitlines():
            if "[test] FAIL" in radek or "SCRIPT ERROR" in radek:
                print("   " + radek.strip())
        vysledky.append((jmeno, kontroly, selhani))

        # vrať zpět
        combat.write_bytes(puvodni.encode("utf-8"))
        assert combat.read_text(encoding="utf-8") == puvodni, "návrat se nezdařil"

    print("\n" + "=" * 70)
    chyceno = sum(1 for _, _, s in vysledky if s and s > 0)
    for jmeno, k, s in vysledky:
        print("  %s: %s kontrol, %s selhání  → %s"
              % (jmeno, k, s, "CHYCENO" if s and s > 0 else "PROŠLO (slepá brána!)"))
    print("  chyceno %d z %d" % (chyceno, len(vysledky)))
    return 0 if chyceno == len(vysledky) and vysledky else 1


if __name__ == "__main__":
    sys.exit(main())

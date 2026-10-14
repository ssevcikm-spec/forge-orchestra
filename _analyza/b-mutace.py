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
# P13c (4. 10. 2026): Godot je od D7 OBECNÝ NÁSTROJ STANICE (`E:\Tools\godot\`),
# ne součást repa. Cesta se hledá: FORGE_GODOT -> E:\Tools\godot -> staré místo.
def _najdi_godot() -> Path:
    kandidati = []
    if os.environ.get("FORGE_GODOT"):
        kandidati.append(Path(os.environ["FORGE_GODOT"]))
    kandidati += [
        KOREN.parent.parent / "Tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe",
        # Obvyklá místa obecného nástroje stanice (D7). Bere se PRVNÍ, které
        # existuje; override je `FORGE_GODOT`. Pořadí je shodné s `g3-brany.py`.
        Path(r"E:\Tools\godot") / "Godot_v4.7.2-stable_win64_console.exe",
        Path(r"C:\Users\Ssevc\Local-Deepseek\_tools\godot")
        / "Godot_v4.7.2-stable_win64_console.exe",
    ]
    for k in kandidati:
        if k.is_file():
            return k
    return kandidati[0]


GODOT = _najdi_godot()
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
    # ⚠ PŘEMĚŘENO 14. 10. 2026 (K6): synchronizovat TŘI VYJMENOVANÉ soubory
    # NESTAČÍ. Fixtura `a-ukol-scratch` je snímek hry z doby Úkolu A; hra se od té
    # doby hnula (přibyl `scripts/registry.gd` s granulí `engine.registry`) a testy
    # (synchronizované z klonu) ho začaly volat → „ZDRAVÝ KÓD: 92 kontrol, 1 selhání“
    # a brána SPRÁVNĚ odmítla měřit (mutace by nic nedokázala). Naměřeno v `g3`:
    # `mutace B (combat)` → exit 2, „běžela, ale vzor nic nenašel“ (119 B).
    # Poučení: brána nad ZASTARALOU fixturou neměří kód, ale minulost — a vypadá
    # to jako mrtvá brána. Fixtura se proto synchronizuje CELÁ (`scripts/` a
    # `tests/` z klonu), ne tři soubory; když hra dostane další soubor, sedne to
    # samo (a `git clone` by v sandboxu nešel — viz `dsh-prostredi`).
    import shutil
    zdroj_repo = KOREN.parent / "uo-shadows"
    synchronizovano = 0
    for pod in ("scripts", "tests"):
        zdroj_dir = zdroj_repo / pod
        cil_dir = scratch / pod
        if not (zdroj_dir.is_dir() and cil_dir.is_dir()):
            continue
        for zdroj in sorted(zdroj_dir.rglob("*")):
            if not zdroj.is_file() or zdroj.suffix not in (".gd", ".uid"):
                continue
            cil = cil_dir / zdroj.relative_to(zdroj_dir)
            cil.parent.mkdir(parents=True, exist_ok=True)
            if not cil.is_file() or zdroj.read_bytes() != cil.read_bytes():
                shutil.copyfile(zdroj, cil)
                synchronizovano += 1
    print("synchronizováno z klonu: %d souborů (scripts/ + tests/, .gd/.uid)"
          % synchronizovano)

    # Kontrola, že testovací blok je opravdu v tom, co se spustí.
    testy = (scratch / "tests" / "run_tests.gd").read_text(encoding="utf-8")
    if "combat.resolve() umí zásah i minutí" not in testy:
        print("CHYBA: v %s není blok s `combat.resolve()` — mutace by měřila něco jiného"
              % (scratch / "tests" / "run_tests.gd"))
        return 2

    # import cache (`.godot/`) — bez ní se nenačtou assety a testy dají 57/3
    zdroj_godot = KOREN.parent / "uo-shadows" / ".godot"
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

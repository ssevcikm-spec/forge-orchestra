# -*- coding: utf-8 -*-
r"""P13c: opraví STARÉ cesty v nástrojích, které se vrátily z archivu (nález H48).

PROČ SAMOSTATNÝ SKRIPT A NE `-replace` V POWERSHELLU:
  PowerShell rozbije diakritiku i zpětné apostrofy v `python -c` (skill
  `dsh-prostredi` §3d/§3e), mutace se pak **tiche neprovede** a vypadá to jako
  hotová oprava (skill `overovani` §7.9). Tady se proto:
    * soubor čte i zapisuje **bajtově** (`read_bytes`/`write_bytes`),
    * u KAŽDÉ náhrady se **spočítá počet výskytů a assertuje** očekávaný počet,
    * po zápisu se soubor **znovu přečte z disku** a ověří, že text zmizel.

Použití: python _analyza\p13c-oprav-cesty.py
Návrat:  0 = všechny náhrady provedené a ověřené | 2 = něco nesedí (nic se nezapisuje)
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HRA = WS.parent / "uo-shadows"

# ── NÁHRADY ──────────────────────────────────────────────────────────────────
# (soubor, starý text, nový text, očekávaný počet výskytů)
#
# Odvození GODOTu se vkládá jako HOTOVÝ BLOK (ne jen cesta), protože Godot je od
# D7 obecný nástroj stanice (`E:\Tools\godot\`) a jeho cesta se musí hledat —
# natvrdo zapsaná cesta by při dalším stěhování selhala znovu.
BLOK_GODOT = (
    '# P13c (4. 10. 2026): Godot je od D7 OBECNÝ NÁSTROJ STANICE (`E:\\Tools\\godot\\`),\n'
    '# ne součást repa. Cesta se hledá: FORGE_GODOT -> E:\\Tools\\godot -> staré místo.\n'
    'def _najdi_godot() -> Path:\n'
    '    kandidati = []\n'
    '    if os.environ.get("FORGE_GODOT"):\n'
    '        kandidati.append(Path(os.environ["FORGE_GODOT"]))\n'
    '    kandidati += [\n'
    '        KOREN.parent.parent / "Tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe",\n'
    '        Path(r"E:\\Tools\\godot") / "Godot_v4.7.2-stable_win64_console.exe",\n'
    '    ]\n'
    '    for k in kandidati:\n'
    '        if k.is_file():\n'
    '            return k\n'
    '    return kandidati[0]\n'
    '\n'
    '\n'
    'GODOT = _najdi_godot()'
)

NAHRADY = [
    # ── a-mutace-run.py ─────────────────────────────────────────────────────
    ("a-mutace-run.py",
     'GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"',
     BLOK_GODOT, 1),
    ("a-mutace-run.py",
     '[str(KOREN / "orchestra" / "tools" / "git.cmd"), "-C", str(SCRATCH),',
     '[str(KOREN / "tools" / "git.cmd"), "-C", str(SCRATCH),', 1),
    ("a-mutace-run.py",
     'zdroj = KOREN / "games" / "uo-shadows" / rel',
     'zdroj = KOREN.parent / "uo-shadows" / rel', 1),
    # ── b-mutace.py ─────────────────────────────────────────────────────────
    ("b-mutace.py",
     'GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"',
     BLOK_GODOT, 1),
    ("b-mutace.py",
     'zdroj = KOREN / "games" / "uo-shadows" / rel',
     'zdroj = KOREN.parent / "uo-shadows" / rel', 1),
    ("b-mutace.py",
     'zdroj_godot = KOREN / "games" / "uo-shadows" / ".godot"',
     'zdroj_godot = KOREN.parent / "uo-shadows" / ".godot"', 1),
    # ── g1-mutace-diakritika.py ─────────────────────────────────────────────
    ("g1-mutace-diakritika.py",
     'BRANA = WS / "orchestra" / "tools" / "kontrola-diakritiky.py"',
     'BRANA = WS / "tools" / "kontrola-diakritiky.py"', 1),
    # ── g1-diakritika-novych.py ─────────────────────────────────────────────
    ("g1-diakritika-novych.py",
     '    (WS / "orchestra" / "tools", ["*.py", "*.mjs"]),',
     '    (WS / "tools", ["*.py", "*.mjs"]),', 1),
    # ── f2-over-cooldown.py ─────────────────────────────────────────────────
    ("f2-over-cooldown.py",
     'CIL = WS / "orchestra" / "tools" / "test-cooldown.py"',
     'CIL = WS / "tools" / "test-cooldown.py"', 1),
    ("f2-over-cooldown.py",
     'TEST = WS / "orchestra" / "tools" / "test-cooldown.py"',
     'TEST = WS / "tools" / "test-cooldown.py"', 1),
    # ── _registr-bran.py ────────────────────────────────────────────────────
    ("_registr-bran.py",
     'GODOT = WS / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"',
     'GODOT = WS.parent.parent / "Tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"', 1),
    ("_registr-bran.py",
     'str(WS / "games" / "uo-shadows"),',
     'str(WS.parent / "uo-shadows"),', 1),
    ("_registr-bran.py",
     '("over-dokumentaci", ["python", "orchestra/tools/over-dokumentaci.py"],',
     '("over-dokumentaci", ["python", str(WS / "tools" / "over-dokumentaci.py")],', 1),
    ("_registr-bran.py",
     '("test-cooldown", ["python", "orchestra/tools/test-cooldown.py"],',
     '("test-cooldown", ["python", str(WS / "tools" / "test-cooldown.py")],', 1),
    ("_registr-bran.py",
     '("vision.test.mjs", ["node", "orchestra/repo/.forge/node/vision.test.mjs"],',
     '("vision.test.mjs", ["node", str(WS / "repo" / ".forge" / "node" / "vision.test.mjs")],', 1),
    ("_registr-bran.py",
     '("baseline.py testy", ["python", "orchestra/repo/.forge/baseline.py", "testy"],',
     '("baseline.py testy", ["python", str(WS / "repo" / ".forge" / "baseline.py"), "testy"],', 1),
]


def main() -> int:
    # 1) FÁZE KONTROLY: nic se nezapisuje, dokud všechny náhrady nesedí.
    podle_souboru: dict[str, list] = {}
    for soubor, stary, novy, pocet in NAHRADY:
        podle_souboru.setdefault(soubor, []).append((stary, novy, pocet))

    chyby = []
    for soubor, zmeny in podle_souboru.items():
        cesta = WS / "_analyza" / soubor
        if not cesta.is_file():
            chyby.append("CHYBI soubor: %s" % cesta)
            continue
        text = cesta.read_text(encoding="utf-8")
        for stary, novy, pocet in zmeny:
            skutecne = text.count(stary)
            if skutecne != pocet:
                chyby.append("%s: hledany text je %dx, ocekavano %dx:\n     %r"
                             % (soubor, skutecne, pocet, stary[:110]))
    if chyby:
        print("CHYBY PRED ZAPISEM (nezapisuji nic):")
        for c in chyby:
            print("  " + c)
        return 2

    # 2) FÁZE ZÁPISU: bajtově (žádné překódování, žádné změny konců řádků).
    for soubor, zmeny in podle_souboru.items():
        cesta = WS / "_analyza" / soubor
        puvodni_bajty = cesta.read_bytes()
        text = puvodni_bajty.decode("utf-8")
        for stary, novy, _ in zmeny:
            text = text.replace(stary, novy)
        cesta.write_bytes(text.encode("utf-8"))
        # 3) FÁZE OVĚŘENÍ: přečti Z DISKU a zkontroluj, že staré texty zmizely.
        zpet = cesta.read_bytes().decode("utf-8")
        assert zpet != puvodni_bajty.decode("utf-8"), "%s se nezmenil!" % soubor
        for stary, _, _ in zmeny:
            assert stary not in zpet, "%s: stary text zustal: %r" % (soubor, stary[:80])
        print("  %-28s %d náhrad, %d B -> %d B"
              % (soubor, len(zmeny), len(puvodni_bajty), len(zpet.encode("utf-8"))))

    print()
    print("VÝSLEDEK: %d souborů opraveno a ověřeno čtením z disku." % len(podle_souboru))
    return 0


if __name__ == "__main__":
    sys.exit(main())

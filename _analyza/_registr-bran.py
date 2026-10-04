# -*- coding: utf-8 -*-
"""REGISTR BRAN — kolik KONTROL hlásí která brána (živé měření, ne odhad).

PROČ TENHLE SKRIPT EXISTUJE
===========================
`audit2b-cisla-proti-zdroji.py` do 2. 10. 2026 srovnával **jedno** číslo
(„kontrol" = běh Godotu nad hrou) se **všemi** výskyty `(\\d+)\\s+kontrol`
v jádru. Naměřeno (2. 10. 2026, tato session): z **15** rozchodů u `kontrol`
jich **11** vzniklo tak, že dokument správně citoval **jinou bránu**
(`a1-a2-over` 23 · skener 23 · `over-dokumentaci` 63 · `test-check-schema` 17 ·
`vision.test.mjs` 36 · `test-cooldown` 10 …).

  NEBYLA TO VADA DOKUMENTU — BYLA TO VADA MĚŘIDLA.
  Různé brány hlásí různé počty kontrol **SPRÁVNĚ** (měří různé věci).

CO SE TÍM ALE NESMÍ STÁT (a jak je to hlídáno)
=============================================
Registr je **uzavřená množina NAMĚŘENÝCH hodnot**, ne „vše, co uznám".
  * Každá hodnota má **jméno brány, příkaz a popis**, kterým vznikla —
    a `audit2b` je vypíše (nález NA17: „celkem N" bez seznamu zdrojů
    je neověřitelné).
  * Když brána **spadne** (sandbox, chybějící závislost), zapíše se
    `None` s důvodem — **nevymyslí se náhradní hodnota**.
  * Když se číslo brány **změní** (testy hry 64 → 65), stará hodnota
    v registru **zůstane jen jako komentář** (`--stare`), takže se
    dokument s `64` pořád ohlásí jako rozchod. Registr **neroste sám**.

Výstup: `_analyza/_registr-bran.json` (+ lidský výpis na obrazovku).
Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza/_registr-bran.py
"""
import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GODOT = WS / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
VYSTUP = WS / "_analyza" / "_registr-bran.json"
USER_DIR = WS / "_analyza" / "a-godot-user"

# (jméno brány, příkaz, co najít ve výstupu)
# ⚠ SEM SE PŘIDÁVÁ JEN BRÁNA, KTERÁ SKUTEČNĚ HLÁSÍ „N kontrol".
#   Když přestane hlásit, uvidí se to jako `None` — ne jako ticho.
BRANY = [
    ("testy hry (Godot)", [str(GODOT), "--headless", "--path",
                           str(WS / "games" / "uo-shadows"),
                           "--script", "res://tests/run_tests.gd"],
     r"\[test\]\s+(\d+)\s+kontrol"),
    ("a1-a2-over", ["python", "_analyza/a1-a2-over.py"], r"Kontrol:\s+(\d+)"),
    # ⚠ `(?!\w)` — naměřeno 2. 10. 2026: vzor `(\d+)\s+kontrol` zabral na
    # „**2 kontrolní** vzorky" (`b5-over-tvrzeni.py`) a vyrobil z registru
    # hodnotu **2**, která žádný počet kontrol není. „kontrolní" NENÍ čítač.
    ("test-neanglicky-skener", ["python", "_analyza/test-neanglicky-skener.py"],
     r"(\d+)\s+kontrol(?!\w)"),
    ("over-dokumentaci", ["python", "orchestra/tools/over-dokumentaci.py"],
     r"Kontrol:\s*(\d+)"),
    ("test-cooldown", ["python", "orchestra/tools/test-cooldown.py"],
     r"(\d+)\s+kontrol(?!\w)"),
    ("b5-over-tvrzeni", ["python", "_analyza/b5-over-tvrzeni.py"],
     r"(\d+)\s+kontrol(?!\w)"),
    # Šablona orchestra — dva testy, které měří i `g3-brany.py` (jsou v jeho
    # seznamu BRANY). V sandboxu `workspace-write` padají na `spawn EPERM`
    # (jsou to Node skripty, které pouští podproces s piped stdio) — což je
    # třetí stav „neproběhlo (prostředí)", ne vada. Registr to musí říct,
    # ne zamlčet (`overovani` §7.13).
    ("vision.test.mjs", ["node", "orchestra/repo/.forge/node/vision.test.mjs"],
     r"(\d+)\s+kontrol(?!\w)"),
    ("baseline.py testy", ["python", "orchestra/repo/.forge/baseline.py", "testy"],
     r"(\d+)\s+kontrol(?!\w)"),
]

# ⚠ HODNOTY Z BĚHŮ, KTERÉ SE TADY SPUSTIT NEDAJÍ (a přiznaně, ne potichu).
# Každá je z **konkrétního běhu**, ne z dokumentace:
#   `_analyza/g3-brany-vystup.txt` = výstup posledního `g3-brany.py`
#   (tamtéž je i `exit=` a celý text, takže se dá ověřit).
STARE_Z_BEHU = {
    "mutace A (5 běhů)": (59, "_analyza/a-mutace-run.py pred-opravou → g3-brany-vystup.txt"),
    "mutace A: pres-level": (61, "_analyza/a-mutace-run.py pres-level → g3-brany-vystup.txt"),
    "mutace B (combat)": (65, "_analyza/b-mutace.py → g3-brany-vystup.txt"),
    "f2 over cooldown": (10, "_analyza/f2-over-cooldown.py → g3-brany-vystup.txt"),
}


def spust(jmeno, prikaz, vzor):
    """Spustí bránu a vytáhne počet kontrol. Když číslo není, řekne PROČ."""
    env = None
    if "godot" in prikaz[0].lower():
        env = dict(os.environ)
        env["APPDATA"] = str(USER_DIR)
        USER_DIR.mkdir(parents=True, exist_ok=True)
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env,
                           timeout=1800)
    except Exception as e:                                        # noqa: BLE001
        return None, "nepodařilo se spustit: %s" % type(e).__name__, ""
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    m = None
    for m in re.finditer(vzor, v):
        pass                       # POSLEDNÍ výskyt = souhrn, ne dílčí řádek
    if not m:
        # Rozliš „brána spadla" od „brána číslo nehlásí" — obojí je nález.
        if r.returncode != 0:
            return None, "exit=%d a výstup neobsahuje hledaný čítač" % r.returncode, ""
        return None, ("exit=0, ale výstup NEOBSAHUJE hledaný čítač "
                      "(brána přestala měřit?)"), ""
    if r.returncode != 0:
        return None, "exit=%d (číslo %s je z NEDOKONČENÉHO běhu)" % (
            r.returncode, m.group(1)), m.group(0)
    return int(m.group(1)), "exit=0", m.group(0)


def main():
    print("=" * 96)
    print("  REGISTR BRAN — kolik kontrol která brána hlásí (ŽIVÉ měření)")
    print("=" * 96)
    zaznamy = {}
    for jmeno, prikaz, vzor in BRANY:
        hodnota, poznamka, doklad = spust(jmeno, prikaz, vzor)
        zaznamy[jmeno] = {"kontrol": hodnota, "poznamka": poznamka,
                          "prikaz": " ".join(prikaz[:3]) + (" …" if len(prikaz) > 3 else ""),
                          "doklad": doklad}
        print("  %-26s %-8s %s" % (jmeno, hodnota if hodnota is not None else "—",
                                   poznamka))
    print()
    print("  Z BĚHŮ, KTERÉ SE TADY SPUSTIT NEDAJÍ (přiznaně, s dokladem):")
    for jmeno, (hodnota, odkud) in STARE_Z_BEHU.items():
        zaznamy[jmeno] = {"kontrol": hodnota, "poznamka": "z dřívějšího běhu",
                          "prikaz": odkud, "doklad": ""}
        print("  %-26s %-8s %s" % (jmeno, hodnota, odkud))

    hodnoty = sorted({z["kontrol"] for z in zaznamy.values()
                      if z["kontrol"] is not None}, reverse=True)
    VYSTUP.write_text(json.dumps({
        "kdy": time.strftime("%Y-%m-%d %H:%M:%S"),
        "hodnoty": hodnoty,
        "brany": zaznamy,
    }, ensure_ascii=False, indent=2), encoding="utf-8", newline="")

    print()
    print("  MNOŽINA HODNOT (3–65 kontrol) — s tím se smí srovnávat:")
    print("      %s" % hodnoty)
    print("  NEZMĚŘENÉ brány: %d z %d"
          % (len([1 for z in zaznamy.values() if z["kontrol"] is None]),
             len(zaznamy)))
    print()
    print("  zapsáno: %s (%d B)" % (VYSTUP.name, VYSTUP.stat().st_size))
    if not hodnoty:
        print("\n  CHYBA: registr je PRÁZDNÝ — to není „hotovo\", to je slepé místo.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

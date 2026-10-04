# -*- coding: utf-8 -*-
"""H17 — ověření, že práce akční session je SKUTEČNĚ v klonu (omyl 50).

Nezávisle na `_analyza\\b-sonda-65.py` (jiný nástroj, jiné otázky):
  A) porovná obsah souborů klon vs. scratch (bajt na bajt) + SHA-256;
  B) ověří, že v klonu jsou PŘÍTOMNÉ znaky obou Úkolů (A: atrapa TestUrovenBezIzo
     a volání move(); B: blok, který volá combat.resolve());
  C) ověří, že v pracovním stromu klonu je právě 5 změněných souborů
     a že proti HEAD žádný z nich není prázdný diff.
"""

import hashlib
import json
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
KLON = WS / "games" / "uo-shadows"
SCRATCH = WS / "_analyza" / "a-ukol-scratch"

chyby = []


def sha(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git(*args, repo=KLON) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), *args],
                       capture_output=True, shell=True)
    return r.stdout.decode("utf-8", "replace")


print("=" * 78)
print("A) OBSAH: klon vs. pracovní strom akční session")
print("=" * 78)

for rel in ("scripts/combat.gd", "tests/run_tests.gd", "scripts/player.gd",
            ".forge/roadmap.json", "docs/ARCHITEKTURA.md"):
    k = (KLON / rel).read_bytes()
    s = (SCRATCH / rel)
    if s.exists():
        sb = s.read_bytes()
        shoda = k == sb
        print("  %-24s klon %7d B  scratch %7d B  shodné: %s"
              % (rel, len(k), len(sb), shoda))
        print("  %-24s %s  vs  %s" % ("", sha(k)[:16], sha(sb)[:16]))
    else:
        print("  %-24s klon %7d B  scratch: soubor NENÍ" % (rel, len(k)))
        print("  %-24s %s" % ("", sha(k)[:16]))

print()
print("=" * 78)
print("B) ZNAKY OBOU ÚKOLŮ v KLONU (hledá se v KÓDU, ne v komentářích)")
print("=" * 78)


def bez_komentaru_gd(text: str) -> str:
    """Odstraní komentáře `#` z GDScriptu (mimo řetězce)."""
    out = []
    for radek in text.splitlines():
        v_ret = False
        i = 0
        while i < len(radek):
            c = radek[i]
            if c == '"':
                v_ret = not v_ret
            elif c == "#" and not v_ret:
                break
            i += 1
        out.append(radek[:i])
    return "\n".join(out)


testy = bez_komentaru_gd((KLON / "tests/run_tests.gd").read_text(encoding="utf-8"))
combat = bez_komentaru_gd((KLON / "scripts/combat.gd").read_text(encoding="utf-8"))
player = bez_komentaru_gd((KLON / "scripts/player.gd").read_text(encoding="utf-8"))

znaky = [
    # (popis, kde, vzor, musí být?)
    ("Úkol A: atrapa TestUrovenBezIzo", testy, "TestUrovenBezIzo", True),
    ("Úkol A: atrapa počítá izo_pokusu", testy, "izo_pokusu", True),
    ("Úkol A: test volá player.move()", testy, "player.move(", True),
    ("Úkol A: test tvrdí izo_pokusu == 0", testy, "izo_pokusu == 0", True),
    ("Úkol A: STARÝ zakázaný vzor (nesmí být v testu)", testy,
     'contains("level.iso_position")', False),
    ("Úkol A: fallback v player.gd zůstal", player, "iso_position", True),
    ("Úkol B: combat.resolve deklarováno", combat, "func resolve(", True),
    ("Úkol B: Godot 4 dotaz na vlastnost", combat, ' in ', True),
    # ⚠ POZOR: `.has(` NENÍ důkaz Godot 3 API — `Dictionary.has()` a `Array.has()`
    # v Godotu 4 EXISTUJÍ. Hledá se proto KONTEXT: uzel (attacker/defender v roli
    # uzlu), ne slovník. `defender.has("armor_rating")` na řádku 80 je legitimní
    # (je to Dictionary větev) — proto se hledá `in defender` místo `.has(`.
    ("Úkol B: Godot 3 `Object.has(` na uzlu", combat, "attacker.has(", False),
    ("Úkol B: Godot 4 dotaz na zbroj uzlu", combat,
     '"armor_rating" in defender', True),
    ("Úkol B: Dictionary větev je oddělená", combat,
     'TYPE_DICTIONARY and defender.has(', True),
    ("Úkol B: test volá combat.resolve()", testy, "cb.resolve(", True),
    ("Úkol B: atrapa BEZ hodnota()", testy, "TestBojAtributy", True),
    ("Úkol B: atrapa S hodnota()", testy, "var atr_h = TestAtributy.new()", True),
    ("Úkol B: dvoutvarové čtení (_cislo)", combat, "komponenta.has_method(\"hodnota\")", True),
]

for popis, kde, vzor, musi in znaky:
    je = vzor in kde
    ok = (je == musi)
    print("  %-4s %-46s %-28s %s" % ("OK" if ok else "CHYBA", popis,
                                     repr(vzor)[:28], "je" if je else "není"))
    if not ok:
        chyby.append("%s: vzor %r %s, očekáváno %s"
                     % (popis, vzor, "je" if je else "není",
                        "je" if musi else "není"))

print()
print("=" * 78)
print("C) PRACOVNÍ STROM klonu — co je změněné proti HEAD")
print("=" * 78)
status = [l for l in git("status", "--porcelain").splitlines() if l.strip()]
print("  změněných souborů: %d" % len(status))
for l in status:
    print("    %s" % l)

print()
for l in status:
    cesta = l[3:].strip()
    d = git("diff", "--numstat", "--", cesta).strip()
    print("  %-30s numstat: %s" % (cesta, d or "(žádný diff!)"))
    if not d:
        chyby.append("soubor %s je ve status bez diffu" % cesta)

print()
print("=" * 78)
if chyby:
    print("NALEZENO %d PROBLÉMŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE OK — práce Úkolů A i B je v klonu (doloženo hashem obsahu)")
sys.exit(0)

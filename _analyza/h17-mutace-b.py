#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H17 — VLASTNÍ ověření Úkolu B (`combat.gd`) — nezávisle na `b-mutace.py`.

Běží nad pracovním stromem `_analyza\\h17-kladna`, který se před každým během
vrátí na `origin/main` a pak se do něj nakopíruje **celý obsah klonu**
(`combat.gd` I `tests/run_tests.gd`), takže se měří TO, CO JE V REPU — ne co
umí patcher (omyl 50).

Mutace (vracím vady, které akční session popsala jako opravené):
  M1  `"armor_rating" in defender`      -> `defender.has("armor_rating")`  (Godot 3 API)
  M2  `"damage" in zbran`               -> `zbran.has("damage")`           (Godot 3 API)
  M3  `komponenta.has_method("hodnota")`-> vypuštěno (jen vlastnost)       (tvar smlouvy)
  M4  `1 + sila / 10`                   -> `1 + sila / 5`                  (vzorec damage)

Použití:  python _analyza\\h17-mutace-b.py
"""

import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
GIT = KOREN / "orchestra" / "tools" / "git.cmd"
GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
USER_DIR = KOREN / "_analyza" / "a-godot-user"
KLON = KOREN / "games" / "uo-shadows"
WT = KOREN / "_analyza" / "h17-kladna"
COMBAT = WT / "scripts" / "combat.gd"
TESTY = WT / "tests" / "run_tests.gd"

MUTACE = [
    ("M1 armor_rating pres has()",
     '"armor_rating" in defender', 'defender.has("armor_rating")'),
    # Pozor: `"damage" in zbran` je v souboru 2x (resolve i _vybrana_zbran).
    # Kotva je proto řádek, kde se damage SKUTEČNĚ čte.
    ("M2 cteni damage pres has()",
     'zbran_poskozeni = int(zbran.damage)', 'zbran_poskozeni = int(zbran.has("damage"))'),
    ("M3 hodnota() se nezkousi",
     'if komponenta.has_method("hodnota"):\n\t\treturn int(komponenta.hodnota(klic))\n\t',
     ''),
    ("M4 vzorec damage (Str/10 -> Str/5)",
     'var zaklad: int = 1 + sila / 10', 'var zaklad: int = 1 + sila / 5'),
    ("M5 zbroj se ignoruje",
     'zbroj = int(defender.armor_rating)', 'zbroj = 0'),
]

vysledky = {}


def cti(c: Path) -> str:
    return c.read_text(encoding="utf-8")


def reset() -> None:
    r = subprocess.run([str(GIT), "-C", str(WT), "checkout", "--", "."],
                       capture_output=True, shell=True)
    assert r.returncode == 0, "navrat worktree selhal"
    for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
        shutil.copyfile(KLON / rel, WT / rel)
        assert cti(KLON / rel) == cti(WT / rel), "kopie %s nesedi" % rel


def spust(popis: str):
    USER_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(USER_DIR)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([str(GODOT), "--headless", "--path", str(WT),
                        "--script", "res://tests/run_tests.gd"],
                       capture_output=True, env=env, timeout=300)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", v)
    if not m:
        print("    !! testy NEDOBEHly — exit=%d" % r.returncode)
        print(v[-2500:])
        return None
    k, s = int(m.group(1)), int(m.group(2))
    fail = [l.strip() for l in v.splitlines() if l.strip().startswith("[test] FAIL")]
    err = [l.strip() for l in v.splitlines()
           if "Nonexistent function" in l or "Invalid call" in l]
    print("    SOUHRN: %d kontrol, %d selhání   (exit=%d)" % (k, s, r.returncode))
    for l in fail[:8]:
        print("    FAIL: %s" % l[:150])
    for l in err[:3]:
        print("    CHYBA GODOTU: %s" % l[:150])
    return {"kontrol": k, "selhani": s, "exit": r.returncode, "fail": fail, "err": err}


print("=" * 78)
print("H17 — Úkol B (`combat.gd`), vlastní mutační běhy")
print("=" * 78)

print()
print("-" * 78)
print("BĚH zdravy: combat.gd + testy PŘESNĚ z klonu (co je v repu)")
print("-" * 78)
reset()
assert cti(COMBAT) == cti(KLON / "scripts" / "combat.gd")
print("    [overeno: combat.gd i run_tests.gd jsou bajt na bajt z klonu]")
vysledky["zdravy"] = spust("zdravy")

for popis, najdi, nahrad in MUTACE:
    print()
    print("-" * 78)
    print("BĚH %s" % popis)
    print("-" * 78)
    reset()
    t = cti(COMBAT)
    if najdi not in t:
        print("    CHYBA: vzor k mutaci v combat.gd NENI: %r" % najdi[:60])
        vysledky[popis] = None
        continue
    assert t.count(najdi) == 1, "vzor je v souboru %dx, ne 1x" % t.count(najdi)
    novy = t.replace(najdi, nahrad, 1)
    assert novy != t, "MUTACE NEPROBEHLA"
    COMBAT.write_bytes(novy.encode("utf-8"))
    assert cti(COMBAT) == novy, "zapsany obsah nesedi"
    assert najdi not in cti(COMBAT), "PODMINKA PORAD PLATI — mutace nic nezmenila"
    print("    [mutace zapsana a overena z disku: %d -> %d znaku]"
          % (len(t), len(novy)))
    vysledky[popis] = spust(popis)

print()
print("=" * 78)
print("VYHODNOCENI")
print("=" * 78)
chyby = []
z = vysledky.get("zdravy")
print("  %-32s %s" % ("zdravy (klon)", ("%d kontrol, %d selhání"
                                       % (z["kontrol"], z["selhani"])) if z else "NEDOBEHL"))
if z is None or z["selhani"] != 0:
    chyby.append("zdravy kod neprosel — mutace by nemela co merit")
for popis, _, _ in MUTACE:
    v = vysledky.get(popis)
    if v is None:
        chyby.append("%s: testy nedobehly nebo se mutace neprovedla" % popis)
        print("  %-32s NEDOBEHL / NEPROVEDLA SE" % popis)
        continue
    print("  %-32s %d kontrol, %d selhání   %s"
          % (popis, v["kontrol"], v["selhani"],
             "CHYCENO" if v["selhani"] > 0 else "!!! NECHYCENO !!!"))
    if v["selhani"] == 0:
        chyby.append("%s: NECHYCENO (0 selhani)" % popis)

print()
if chyby:
    print("NALEZENO %d ROZCHODU:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE SEDÍ — každá vrácená vada v combat.gd shodí testy")
sys.exit(0)

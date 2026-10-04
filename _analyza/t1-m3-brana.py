#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""ÚKOL 1 — důkaz, že test umí SPADNOUT na mutaci M3 (vypuštění větve hodnota()).

PROČ SAMOSTATNÝ SOUBOR: `h17-mutace-b.py` (plánovací session) měřil M3 nad
worktree `_analyza\h17-kladna`, který byl pak odstraněn — a jeho verdikt byl
„M3 NECHYCENA" (nález H2/H12). Tenhle skript měří TOTÉŽ, ale:

  1. zakládá si VLASTNÍ worktree `_analyza\t1-kladna` (nesahá na klon
     uživatele ani na `a-ukol-scratch`, který používá `g3-brany.py`),
  2. bere do něj **PRÁVĚ UPRAVENÝ `run_tests.gd` z klonu** (ne z gitu),
  3. a hlavně: **ověřuje měřenou podmínku PŘED během i PO něm.** Mutace,
     která se tiše neprovede, tvrdí totéž co mutace, která projde
     (`overovani` §7.9/§7.14) — a testy samy si `combat.gd` needitují, takže
     stačí ověření na začátku. Ověření na konci je tam proto, aby se to
     netvrdilo bez důkazu.

CO SE MĚŘÍ (tři běhy, každý s jiným obsahem `combat.gd`):
  A) zdravý kód (bajt na bajt z klonu)          → musí dát 0 selhání
  B) M3: vypuštěná větev `hodnota(attr)`        → musí SPADNOUT (nález H12)
  C) návrat zdravého kódu                       → musí dát 0 selhání znovu
     (kdyby C neprošlo, není to důkaz o bráně, ale o neuklizeném stromě)

Použití:  python _analyza\t1-m3-brana.py
Návrat:   0 = brána měří | 1 = rozchod (vypíše který)
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
WT = KOREN / "_analyza" / "t1-kladna"
COMBAT = WT / "scripts" / "combat.gd"
TESTY_Z_KLONU = KLON / "tests" / "run_tests.gd"

# Mutace M3 = vrátí se vada, kterou Úkol B opravil: `_cislo()` zkusí JEN
# vlastnost, větev `hodnota(klic)` vypadne. Kotva je PŘESNĚ ta z `combat.gd`.
M3_NAJDI = 'if komponenta.has_method("hodnota"):\n\t\treturn int(komponenta.hodnota(klic))\n\t'
M3_NAHRAD = ''


def cti(c: Path) -> str:
    return c.read_text(encoding="utf-8")


def priprav_worktree() -> None:
    """Založí worktree na `origin/main` a nakopíruje do něj testy Z KLONU."""
    if WT.is_dir():
        r = subprocess.run([str(GIT), "-C", str(WT), "checkout", "--", "."],
                           capture_output=True, shell=True)
        assert r.returncode == 0, "navrat worktree selhal"
    else:
        r = subprocess.run([str(GIT), "-C", str(KLON), "worktree", "add",
                            "--detach", str(WT), "origin/main"],
                           capture_output=True, shell=True)
        aus = (r.stdout + r.stderr).decode("utf-8", "replace")
        assert r.returncode == 0, "worktree add selhal:\n%s" % aus[-1500:]
    # .godot NENÍ v gitu (past dsh-prostredi §4c) — bez import cache dávají
    # testy 57/3 místo 65/0 a vypadá to jako regrese.
    if (KLON / ".godot").is_dir() and not (WT / ".godot").is_dir():
        shutil.copytree(KLON / ".godot", WT / ".godot")
    # Testy se berou Z KLONU (tj. to, co jsem právě upravil), ne z gitu.
    for rel in ("tests/run_tests.gd", "scripts/combat.gd"):
        shutil.copyfile(KLON / rel, WT / rel)
        assert cti(KLON / rel) == cti(WT / rel), "kopie %s nesedi" % rel


def spust() -> dict:
    USER_DIR.mkdir(parents=True, exist_ok=True)
    env = dict(os.environ)
    env["APPDATA"] = str(USER_DIR)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([str(GODOT), "--headless", "--path", str(WT),
                        "--script", "res://tests/run_tests.gd"],
                       capture_output=True, env=env, timeout=300)
    v = (r.stdout.decode("utf-8", "replace")
         + r.stderr.decode("utf-8", "replace"))
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", v)
    if not m:
        print("    !! testy NEDOBEHly — exit=%d" % r.returncode)
        print(v[-2500:])
        return {"kontrol": None, "selhani": None, "exit": r.returncode, "fail": []}
    fail = [l.strip() for l in v.splitlines() if l.strip().startswith("[test] FAIL")]
    return {"kontrol": int(m.group(1)), "selhani": int(m.group(2)),
            "exit": r.returncode, "fail": fail}


def vypis(vys: dict) -> None:
    if vys["kontrol"] is None:
        print("    SOUHRN: NEDOBEHL")
        return
    print("    SOUHRN: %d kontrol, %d selhání   (exit=%d)"
          % (vys["kontrol"], vys["selhani"], vys["exit"]))
    for l in vys["fail"][:8]:
        print("    FAIL: %s" % l[:160])


print("=" * 78)
print("ÚKOL 1 — umí test SPADNOUT na mutaci M3 (vypuštění větve hodnota())?")
print("=" * 78)

priprav_worktree()
print()
print("  worktree: %s" % WT)
print("  testy vzaty z klonu: %s (%d B)"
      % (TESTY_Z_KLONU.name, TESTY_Z_KLONU.stat().st_size))
assert "TestAtributyHodnota" in cti(WT / "tests" / "run_tests.gd"), \
    "v testech NENÍ nová atrapa — měřil bych starý soubor"

vysledky = {}

# ------------------------------------------------------------------ A) zdravý
print()
print("-" * 78)
print("A) ZDRAVÝ KÓD — `combat.gd` bajt na bajt z klonu")
print("-" * 78)
assert cti(COMBAT) == cti(KLON / "scripts" / "combat.gd"), "combat.gd neni z klonu"
vysledky["A-zdravy"] = spust()
vypis(vysledky["A-zdravy"])

# ---------------------------------------------------------------------- B) M3
print()
print("-" * 78)
print("B) M3 — vypuštěná větev `if komponenta.has_method(\"hodnota\")`")
print("-" * 78)
t = cti(COMBAT)
assert M3_NAJDI in t, "KOTVA M3 V combat.gd NENI — mutace by se neprovedla"
assert t.count(M3_NAJDI) == 1, "kotva M3 je v souboru %dx, ne 1x" % t.count(M3_NAJDI)
novy = t.replace(M3_NAJDI, M3_NAHRAD, 1)
assert novy != t, "MUTACE NEPROBEHLA (text se nezmenil)"
COMBAT.write_bytes(novy.encode("utf-8"))
# POJISTKA (past overovani 7.14): musí přestat platit MĚŘENÁ PODMÍNKA,
# ne jen „soubor se změnil".
assert cti(COMBAT) == novy, "zapsany obsah nesedi s tim, co jsem zapsal"
assert M3_NAJDI not in cti(COMBAT), "PODMINKA PORAD PLATI — mutace nic nezmenila"
print("  [mutace zapsána a ověřena Z DISKU: %d -> %d znaků]" % (len(t), len(novy)))
vysledky["B-M3"] = spust()
vypis(vysledky["B-M3"])

# ---------------------------------------------------------- kontrola po běhu
assert M3_NAJDI not in cti(COMBAT), \
    "PO BĚHU: měřená podmínka se vrátila — testy si combat.gd přepsaly?"
print("  [po běhu ověřeno z disku: větev `hodnota()` v combat.gd pořád NENÍ]")

# ------------------------------------------------------------------- C) návrat
print()
print("-" * 78)
print("C) NÁVRAT ZDRAVÉHO KÓDU — musí zase projít (jinak to není o bráně)")
print("-" * 78)
shutil.copyfile(KLON / "scripts" / "combat.gd", COMBAT)
assert cti(COMBAT) == cti(KLON / "scripts" / "combat.gd"), "navrat combat.gd nesedi"
vysledky["C-navrat"] = spust()
vypis(vysledky["C-navrat"])

# ----------------------------------------------------------------- vyhodnoceni
print()
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
chyby = []
a, b, c = vysledky["A-zdravy"], vysledky["B-M3"], vysledky["C-navrat"]

if a["kontrol"] is None or a["selhani"] != 0:
    chyby.append("A (zdravý kód) neprošel — mutace by neměla co měřit")
if b["kontrol"] is None:
    chyby.append("B (M3) NEDOBEHL — testy spadly dřív, než mohly hlásit výsledek")
elif b["selhani"] == 0:
    chyby.append("B (M3) NECHYCENO — 0 selhání, nález H12 by zůstal otevřený")
if c["kontrol"] is None or c["selhani"] != 0:
    chyby.append("C (návrat) neprošel — rozchod je ve stromě, ne v bráně")

for popis, v in (("A zdravý kód", a), ("B M3 (větev vypuštěna)", b), ("C návrat zdravého", c)):
    if v["kontrol"] is None:
        print("  %-26s NEDOBEHL" % popis)
    else:
        print("  %-26s %d kontrol, %d selhání   exit=%d"
              % (popis, v["kontrol"], v["selhani"], v["exit"]))

print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for ch in chyby:
        print("  CHYBA %s" % ch)
    sys.exit(1)
print("BRÁNA MĚŘÍ — zdravý kód %d/0, s vrácenou vadou M3 %d/%d (SPADLA), po návratu %d/0."
      % (a["kontrol"], b["kontrol"], b["selhani"], c["kontrol"]))
sys.exit(0)

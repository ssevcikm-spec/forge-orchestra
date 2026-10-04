#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""ÚKOL 1.2 (plánovací session) — ROZKLAD LÉKU NA M3: rovnost 13, nebo čítač?

ZADÁNÍ TVRDÍ (`NEXT-SESSION-INSTRUKCE.md` §3, bod 1.2):
    „s `> 0` musí M3 **projít** (0 selhání) — to je důkaz, že lék je rovnost,
     ne ‚něco navíc'."

TOHLE MĚŘIDLO TO ZKOUŠÍ VYVRÁTIT. `HANDOFF.md` §21.2 totiž tvrdí, že lék má
DVĚ části: (a) rovnost 13 a (b) čítač `vetev_hodnota >= 1`. Když platí (b),
musí M3 spadnout I S vráceným `> 0` — a pak zadání nemá pravdu.

ROZKLAD (5 variant testu × 2 varianty `combat.gd`):
    T-eq     rovnost 13  + čítač >= 1   (= dnešní klon)
    T-gt     > 0         + čítač >= 1   (rovnost vrácena, čítač ZŮSTÁVÁ)
    T-nocnt  rovnost 13  + čítač >= 0   (čítač neutralizován, rovnost zůstává)
    T-old    PŮVODNÍ test z `c40bdd5`   (> 0 a bez čítače i bez nových atrap)

Každá varianta se před během i po něm ověří: musí přestat platit MĚŘENÁ
PODMÍNKA, ne jen „soubor se změnil" (`overovani` §7.14).

Použití:  python _analyza\\v2-m3-lek.py
Návrat:   0 = měření proběhlo a je konzistentní s tím, co tvrdím
          1 = něco nesedí (vypíše co)
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
WT = KOREN / "_analyza" / "v2-kladna"
COMBAT = WT / "scripts" / "combat.gd"
TESTY = WT / "tests" / "run_tests.gd"
PREDCHOBCE = "c40bdd5"          # commit PŘED lékem na M3 (ověřeno: 279f584)

# --- kotvy, které se v souboru musí vyskytovat PRÁVĚ JEDNOU (past omylu 76) --
K_ROVNOST = 'int(pres_hodnota.get("damage", -1)) == 13'
K_GT = 'int(pres_hodnota.get("damage", 0)) > 0'
K_CITAC = "atr_h.vetev_hodnota >= 1"

# M3 = vypuštění větve `hodnota()` z `_cislo()` (kotva přesně z combat.gd)
M3_NAJDI = 'if komponenta.has_method("hodnota"):\n\t\treturn int(komponenta.hodnota(klic))\n\t'
M3_NAHRAD = ""


def cti(c: Path) -> str:
    return c.read_text(encoding="utf-8")


def git_show(rev: str, cesta: str) -> str:
    """Obsah blobu z gitu jako TEXT (ne přes PowerShell → UTF-16LE, §5b)."""
    r = subprocess.run([str(GIT), "-C", str(KLON), "show", "%s:%s" % (rev, cesta)],
                       capture_output=True, shell=True)
    assert r.returncode == 0, "git show %s:%s selhal: %s" % (
        rev, cesta, (r.stdout + r.stderr).decode("utf-8", "replace")[-800:])
    return r.stdout.decode("utf-8")


def priprav_worktree() -> None:
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
    # .godot NENÍ v gitu (dsh-prostredi §4c) — bez import cache 57/3 místo 65/0
    if (KLON / ".godot").is_dir() and not (WT / ".godot").is_dir():
        shutil.copytree(KLON / ".godot", WT / ".godot")


def spust(popis: str) -> dict:
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
        print("    !! %s NEDOBEHL (exit=%d)" % (popis, r.returncode))
        print(v[-2000:])
        return {"kontrol": None, "selhani": None, "exit": r.returncode, "fail": []}
    fail = [l.strip() for l in v.splitlines() if l.strip().startswith("[test] FAIL")]
    return {"kontrol": int(m.group(1)), "selhani": int(m.group(2)),
            "exit": r.returncode, "fail": fail}


def postav_test(varianta: str, klon_testy: str, stary_testy: str) -> None:
    """Zapíše do worktree variantu testu a OVĚŘÍ z disku, že podmínka platí."""
    if varianta == "T-eq":
        text = klon_testy
    elif varianta == "T-gt":
        assert klon_testy.count(K_ROVNOST) == 1, "kotva rovnosti není 1x"
        text = klon_testy.replace(K_ROVNOST, K_GT, 1)
    elif varianta == "T-nocnt":
        assert klon_testy.count(K_CITAC) == 1, "kotva čítače není 1x"
        text = klon_testy.replace(K_CITAC, "atr_h.vetev_hodnota >= 0", 1)
    elif varianta == "T-old":
        text = stary_testy
    else:
        raise AssertionError("neznámá varianta %s" % varianta)

    TESTY.write_bytes(text.encode("utf-8"))
    # --- OVĚŘENÍ MĚŘENÉ PODMÍNKY Z DISKU (ne z proměnné v paměti) ----------
    na_disku = cti(TESTY)
    assert na_disku == text, "%s: zapsaný obsah nesedí" % varianta
    if varianta == "T-eq":
        assert na_disku.count(K_ROVNOST) == 1 and na_disku.count(K_CITAC) == 1
    elif varianta == "T-gt":
        assert na_disku.count(K_ROVNOST) == 0, "rovnost tam POŘÁD JE"
        assert na_disku.count(K_GT) == 1 and na_disku.count(K_CITAC) == 1
    elif varianta == "T-nocnt":
        assert na_disku.count(K_ROVNOST) == 1
        assert na_disku.count(K_CITAC) == 0, "čítač tam POŘÁD JE"
    elif varianta == "T-old":
        assert na_disku.count(K_ROVNOST) == 0 and na_disku.count(K_CITAC) == 0
        assert "class TestAtributyHodnota:" not in na_disku, "starý test má novou atrapu"
        assert na_disku.count(K_GT) == 1, "starý test nemá `> 0`"


def postav_combat(mutace: bool, klon_combat: str) -> None:
    if mutace:
        t = cti(COMBAT)
        assert t.count(M3_NAJDI) == 1, "kotva M3 v combat.gd není 1x (%d)" % t.count(M3_NAJDI)
        novy = t.replace(M3_NAJDI, M3_NAHRAD, 1)
        assert novy != t, "MUTACE NEPROBĚHLA"
        COMBAT.write_bytes(novy.encode("utf-8"))
        assert M3_NAJDI not in cti(COMBAT), "PODMÍNKA POŘÁD PLATÍ — mutace nic nezměnila"
        print("    [M3 zapsána a ověřena Z DISKU: %d → %d znaků]" % (len(t), len(novy)))
    else:
        COMBAT.write_bytes(klon_combat.encode("utf-8"))
        assert cti(COMBAT) == klon_combat, "zdravý combat.gd nesedí s klonem"


print("=" * 78)
print("ÚKOL 1.2 — JE LÉKEM NA M3 ROVNOST 13, NEBO ČÍTAČ? (rozklad na části)")
print("=" * 78)

priprav_worktree()
klon_testy = cti(KLON / "tests" / "run_tests.gd")
klon_combat = cti(KLON / "scripts" / "combat.gd")
stary_testy = git_show(PREDCHOBCE, "tests/run_tests.gd")

print("  worktree:      %s" % WT)
print("  klon testy:    %d B (dnešní, s lékem)" % len(klon_testy.encode('utf-8')))
print("  %s testy:   %d B (PŘED lékem)" % (PREDCHOBCE, len(stary_testy.encode('utf-8'))))
print("  klon combat:   %d B" % len(klon_combat.encode('utf-8')))
print()
print("  kotvy v dnešním testu: rovnost 13 = %dx · čítač >= 1 = %dx"
      % (klon_testy.count(K_ROVNOST), klon_testy.count(K_CITAC)))
print("  kotvy ve starém testu: rovnost 13 = %dx · `> 0` = %dx"
      % (stary_testy.count(K_ROVNOST), stary_testy.count(K_GT)))

VARIANTY = ["T-eq", "T-gt", "T-nocnt", "T-old"]
vysledky = {}

for varianta in VARIANTY:
    for mutace in (False, True):
        popis = "%s / %s" % (varianta, "M3" if mutace else "zdravý")
        print()
        print("-" * 78)
        print("BĚH: %s" % popis)
        print("-" * 78)
        postav_test(varianta, klon_testy, stary_testy)
        postav_combat(mutace, klon_combat)
        v = spust(popis)
        vysledky[(varianta, mutace)] = v
        if v["kontrol"] is None:
            print("    SOUHRN: NEDOBEHL")
        else:
            print("    SOUHRN: %d kontrol, %d selhání  (exit=%d)"
                  % (v["kontrol"], v["selhani"], v["exit"]))
        for l in v["fail"][:4]:
            print("    FAIL: %s" % l[:150])
        if mutace:
            assert M3_NAJDI not in cti(COMBAT), "po běhu se mutace vrátila"

print()
print("=" * 78)
print("TABULKA — co který lék chytá")
print("=" * 78)
print()
print("  %-9s %-9s %-10s %s" % ("TEST", "COMBAT", "VÝSLEDEK", "CO CHYTLO"))
print("  " + "-" * 70)
chyby = []
for varianta in VARIANTY:
    for mutace in (False, True):
        v = vysledky[(varianta, mutace)]
        if v["kontrol"] is None:
            print("  %-9s %-9s %-10s" % (varianta, "M3" if mutace else "zdravý", "NEDOBEHL"))
            chyby.append("%s/%s nedoběhl" % (varianta, mutace))
            continue
        popis_fail = " · ".join(f[:70] for f in v["fail"]) or "—"
        print("  %-9s %-9s %-10s %s"
              % (varianta, "M3" if mutace else "zdravý",
                 "%d/%d" % (v["kontrol"], v["selhani"]), popis_fail))

print()
print("=" * 78)
print("VYHODNOCENÍ HYPOTÉZY ZE ZADÁNÍ")
print("=" * 78)
gt_m3 = vysledky[("T-gt", True)]
eq_m3 = vysledky[("T-eq", True)]
old_m3 = vysledky[("T-old", True)]
nocnt_m3 = vysledky[("T-nocnt", True)]
gt_zd = vysledky[("T-gt", False)]
eq_zd = vysledky[("T-eq", False)]
old_zd = vysledky[("T-old", False)]

print()
print("  a) kontrola zdravého kódu (každá varianta musí dát 0 selhání):")
for popis, v in (("T-eq", eq_zd), ("T-gt", gt_zd), ("T-old", old_zd)):
    print("       %-6s %s/%s" % (popis, v["kontrol"], v["selhani"]))
    if v["selhani"] != 0:
        chyby.append("%s na zdravém kódu hlásí %d selhání" % (popis, v["selhani"]))

print()
print("  b) M3 s DNEŠNÍM testem (rovnost + čítač):  %s/%s"
      % (eq_m3["kontrol"], eq_m3["selhani"]))
print("  c) M3 s vráceným `> 0`, čítač ZŮSTÁVÁ:      %s/%s"
      % (gt_m3["kontrol"], gt_m3["selhani"]))
print("  d) M3 s rovností, čítač neutralizován:     %s/%s"
      % (nocnt_m3["kontrol"], nocnt_m3["selhani"]))
print("  e) M3 s PŮVODNÍM testem z %s:          %s/%s"
      % (PREDCHOBCE, old_m3["kontrol"], old_m3["selhani"]))
print()

verdikt_zadani = (gt_m3["selhani"] == 0)
verdikt_handoffu = (gt_m3["selhani"] is not None and gt_m3["selhani"] > 0)
print("  ZADÁNÍ tvrdí:  s `> 0` M3 PROJDE (0 selhání)  → %s"
      % ("PLATÍ" if verdikt_zadani else "NEPLATÍ — naměřeno %s selhání" % gt_m3["selhani"]))
print("  HANDOFF tvrdí: lék má DVĚ části (rovnost + čítač) → %s"
      % ("PLATÍ" if verdikt_handoffu else "NEPLATÍ"))
print()
print("  H12 reprodukován (původní test + M3 = 0 selhání): %s"
      % ("ANO" if old_m3["selhani"] == 0 else "NE (%s)" % old_m3["selhani"]))

# --- co je skutečně měřená podmínka (aby se nepletl tvar s významem) --------
if old_m3["selhani"] != 0:
    chyby.append("nepodařilo se reprodukovat H12 — původní test M3 chytil")
if eq_m3["selhani"] == 0:
    chyby.append("dnešní test M3 NECHYTIL — lék nefunguje")
if gt_zd["selhani"] != 0:
    chyby.append("varianta `> 0` na zdravém kódu neprošla — měření je vadné")

print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for ch in chyby:
        print("  CHYBA %s" % ch)
    sys.exit(1)
print("MĚŘENÍ PROBĚHLO A JE KONZISTENTNÍ.")
sys.exit(0)

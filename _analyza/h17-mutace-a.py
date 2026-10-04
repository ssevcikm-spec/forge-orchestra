#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""⚠ TENTO TEST DNES NEPROBĚHNE — `exit 1` ODSUD NENÍ NÁLEZ O KÓDU.

Zařazeno 2. 10. 2026 (Úkol 3 zadání `ZADANI-DOKONCENI-AUDITU.md`, nález **R6**).
Je to **třetí stav** podle skillu `overovani` §7.13: není zelená a **není ani
červená** — je to **NEPROBĚHLO**. Kdo ho povede v seznamu jako „červený",
tvrdí o něm něco, co se nikdy neměřilo.

CO JE TO ZA TEST
  Vlastní (na `a-mutace-run.py` nezávislé) ověření **Úkolu A**: vkládá `move()`
  do `player.gd` ve **třech podobách** a měří, jestli se tím v testech hry
  opravdu zapne kontrola „nebere izo projekci z úrovně". Běží nad **čerstvým
  pracovním stromem** `_analyza\\h17-kladna` (odvozeným z `origin/main`), aby
  se klon uživatele neměnil. Je to přesně ten druh důkazu, který `AGENTS.md`
  vyžaduje: „vlož do kopie minimální artefakt a sleduj, které kontroly se
  tím zapnou" — bez něj `exit 0` nerozliší slepou bránu od zelené.

PROČ DNES NEPROBĚHNE (naměřeno 2. 10. 2026, 18:2x)
  ```
  $ python _analyza\\h17-mutace-a.py        → exit 1
  Traceback (most recent call last):
    File "...\\_analyza\\h17-mutace-a.py", line 151, in <module>
      assert WT.is_dir(), "worktree neexistuje"
  AssertionError: worktree neexistuje
  ```
  `_analyza\\h17-kladna` **neexistuje** (`Test-Path` → `False`;
  `git worktree list` v `games\\uo-shadows` hlásí jen
  `_analyza/a-ukol-scratch` a hlavní klon). Test spadne **na 151. řádku**,
  tedy **dřív, než spustí jediný běh** — naměřeno: ve výstupu není ani jeden
  souhrn `[test] N kontrol, M selhání`. **Nula změřených běhů.**

CO BY HO ZPROVOZNILO (návrh — `NEOVĚŘENO`, sám jsem to nespouštěl)
  Založit ten pracovní strom **z `origin/main`** a dát mu import cache:
  ```powershell
  & orchestra\\tools\\git.cmd -C games\\uo-shadows worktree add --detach `
      "$PWD\\_analyza\\h17-kladna" origin/main
  Copy-Item games\\uo-shadows\\.godot _analyza\\h17-kladna\\.godot -Recurse -Force
  ```
  **Kopírovat `.godot` je povinné**, ne kosmetika: `.godot/` je v `.gitignore`,
  takže se do worktree nedostane a Godot v režimu `--script` **neimportuje
  assety** → naměřeno jinde **57 kontrol, 3 selhání** místo **59/0**, což
  **vypadá jako regrese kódu, ale je to měření nezměřeného stromu**
  (`dsh-prostredi` §4c). A pozor: **`git worktree remove --force`** po sobě
  uklidí, ale **větev v klonu zůstane** — to je zamýšlené (`dsh-prostredi` §4b).
  Tři předpoklady testu na `origin/main` jsem **ověřil** už teď: `scripts/player.gd`
  **nemá** `func move(` ✓, **má** kotvu `func flash() -> void:` ✓ a `game\\uo-shadows\\.godot`
  v klonu existuje ✓. Zbytek je neověřený.

⚠ PROČ SE TO NEMÁ SMAZAT (A1, A7): test je **hotový nástroj**, jen mu chybí
vstupní stav — a ten se dá kdykoli založit dvěma příkazy výš. Smazat ho by
znamenalo zahodit i ten postup.

---

H17 — VLASTNÍ ověření Úkolu A (nezávisle na `a-mutace-run.py`).

Běží nad ČERSTVÝM pracovním stromem `_analyza\\h17-kladna` (origin/main),
takže se klon uživatele nemění. Na rozdíl od `a-mutace-run.py`:
  * testy se neberou patchem, ale **celý soubor z klonu** (proto je to
    důkaz o tom, co je v repu — ne o tom, co umí patcher);
  * `move()` se vkládá **na tři různé způsoby** a u každého se měří, jestli
    se `izo_pokusu` opravdu zvýšil (to je ta podmínka, kterou má brána měřit);
  * každá mutace se po zápisu **přečte z disku a porovná** (past §7.12).

Použití:  python _analyza\\h17-mutace-a.py
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

PLAYER = WT / "scripts" / "player.gd"
TESTY = WT / "tests" / "run_tests.gd"
KOTVA = "func flash() -> void:"

# Tři podoby `move()` — liší se JEN v tom, jestli se ptá úrovně.
MOVE_PRES_LEVEL = '''
func move(dir: Vector2) -> void:
	var d := dir
	if level != null and level.has_method("ma_iso") and level.ma_iso():
		d = Vector2((d.x - d.y) * 0.5, (d.x + d.y) * 0.25)
	position = _step(position + d * SPEED * 0.016)


'''

MOVE_ZDRAVY = '''
func move(dir: Vector2) -> void:
	var d := dir
	if d.length() > 0:
		d = d.normalized()
	position = _step(position + d * SPEED * 0.016)


'''

# Třetí podoba: ptá se úrovně, ale NIKOLI na izo projekci (ptá se na
# průchodnost). Test na tuhle podobu spadnout NEMÁ — kdyby spadl, měřil by
# „něco jiného", ne izo projekci.
MOVE_PRES_WALK = '''
func move(dir: Vector2) -> void:
	var d := dir
	if level != null and level.has_method("is_walkable_at"):
		level.is_walkable_at(position + d)
	position = _step(position + d * SPEED * 0.016)


'''

REZIMY = {
    "1-baseline":        (None, None, "origin/main: PUVODNI test, zadny move()"),
    "2-opraveny-test":   ("klon", None, "opraveny test z klonu, move() v repu NENI"),
    "3-pres-level":      ("klon", MOVE_PRES_LEVEL, "opraveny test + move() se ptá ÚROVNĚ na izo"),
    "4-zdravy":          ("klon", MOVE_ZDRAVY, "opraveny test + zdrave move() (izo neresí)"),
    "5-pres-walk":       ("klon", MOVE_PRES_WALK, "opraveny test + move() se ptá úrovně na PRUCHODNOST"),
    "6-stary-pres-level": (None, MOVE_PRES_LEVEL, "PUVODNI test + move() se ptá ÚROVNĚ na izo"),
}

vysledky = {}


def cti(c: Path) -> str:
    return c.read_text(encoding="utf-8")


def zapis(c: Path, text: str, popis: str) -> None:
    stary = cti(c)
    assert text != stary, "MUTACE NEPROBEHLA (obsah stejny): %s" % popis
    c.write_bytes(text.encode("utf-8"))
    assert cti(c) == text, "ZAPSANY OBSAH NESEDI: %s" % popis
    print("    [zapis OK, overeno z disku: %d -> %d znaku]" % (len(stary), len(text)))


def reset() -> None:
    r = subprocess.run([str(GIT), "-C", str(WT), "checkout", "--", "."],
                       capture_output=True, shell=True)
    assert r.returncode == 0, "navrat worktree selhal"
    # ⚠ PAST, kterou jsem sám potkal (obdoba omylu 46 u akční session):
    # `origin/main` má PŮVODNÍ `combat.gd` (volá Godot 3 `has()`), ale opravený
    # test z klonu obsahuje i BLOK ÚKOLU B, který `resolve()` VOLÁ. Bez
    # synchronizace `combat.gd` z klonu spadne i „zdravé" move() — a vypadá to
    # jako vada testu Úkolu A. Naměřeno: 60 kontrol, 1 selhání místo 60/0.
    shutil.copyfile(KLON / "scripts" / "combat.gd", WT / "scripts" / "combat.gd")
    assert (cti(KLON / "scripts/combat.gd")
            == cti(WT / "scripts/combat.gd")), "combat.gd se nezkopiroval"


def vloz_move(blok: str, popis: str) -> None:
    t = cti(PLAYER)
    assert "func move(" not in t, "ve worktree uz move() je — neni cisty"
    assert KOTVA in t, "chybi kotva %r" % KOTVA
    zapis(PLAYER, t.replace(KOTVA, blok.lstrip("\n") + KOTVA, 1), popis)


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
    # ⚠ POZOR: „izo projekce" je i v LEGITIMNÍ kontrole `izo projekce 2:1`
    # (level.gd). Hledá se proto přesná věta z kontroly Úkolu A — jinak by
    # detektor hlásil nález i tam, kde žádný není (vlastní past, naměřeno).
    izo = [l.strip() for l in v.splitlines() if "nebere izo projekci z úrovně" in l]
    poz = [l.strip() for l in v.splitlines() if "move()` v player.gd není" in l]
    selh = [l.strip() for l in v.splitlines() if l.strip().startswith("[test] FAIL")]
    if not m:
        print("    !! testy NEDOBEHly (zadny souhrn) — exit=%d" % r.returncode)
        print(v[-2000:])
        return None
    k, s = int(m.group(1)), int(m.group(2))
    print("    SOUHRN: %d kontrol, %d selhání   (exit=%d)" % (k, s, r.returncode))
    for l in selh:
        print("    FAIL: %s" % l[:150])
    for l in izo:
        print("    IZO-KONTROLA: %s" % l[:150])
    for l in poz:
        print("    POZNÁMKA: %s" % l[:150])
    return {"kontrol": k, "selhani": s, "exit": r.returncode,
            "izo_radky": izo, "poznamka": poz, "fail": selh}


print("=" * 78)
print("H17 — Úkol A, vlastní mutační běhy nad %s" % WT)
print("=" * 78)
assert WT.is_dir(), "worktree neexistuje"

for nazev, (zdroj_testu, move_blok, popis) in REZIMY.items():
    print()
    print("-" * 78)
    print("BĚH %s: %s" % (nazev, popis))
    print("-" * 78)
    reset()
    if zdroj_testu == "klon":
        shutil.copyfile(KLON / "tests" / "run_tests.gd", TESTY)
        assert cti(TESTY) == cti(KLON / "tests" / "run_tests.gd"), "kopie testu nesedi"
        print("    test prenesen Z KLONU (celej soubor, ne patch)")
    else:
        assert "TestUrovenBezIzo" not in cti(TESTY), "worktree nema puvodni test"
        print("    test je PUVODNI z origin/main")
    if move_blok:
        vloz_move(move_blok, "move() do player.gd")
    else:
        assert "func move(" not in cti(PLAYER), "player.gd ma move(), ma byt bez"
        print("    player.gd bez move() (tak je v orign/main)")
    vysledky[nazev] = spust(nazev)

# ---- vyhodnoceni -----------------------------------------------------------
print()
print("=" * 78)
print("VYHODNOCENI — co ktery beh DOKAZUE")
print("=" * 78)
chyby = []


def ocekavej(nazev, kontroly, selhani, izo_pokusu=None, poznamka=False,
             fail_vzor=None):
    v = vysledky.get(nazev)
    if v is None:
        chyby.append("%s: testy nedobehly" % nazev)
        return
    if v["kontrol"] != kontroly or v["selhani"] != selhani:
        chyby.append("%s: cekano %d/%d, namereno %d/%d"
                     % (nazev, kontroly, selhani, v["kontrol"], v["selhani"]))
    # `izo_pokusu` = přesně ta PODMÍNKA, kterou má brána měřit (past §7.14).
    if izo_pokusu is not None:
        if not v["izo_radky"]:
            chyby.append("%s: kontrola izo projekce se vubec nevypisuje" % nazev)
        else:
            m = re.search(r"pokusů: (\d+)", v["izo_radky"][0])
            if not m:
                chyby.append("%s: z radku nejde precist pocet pokusu" % nazev)
            elif int(m.group(1)) != izo_pokusu:
                chyby.append("%s: izo_pokusu=%s, cekano %d"
                             % (nazev, m.group(1), izo_pokusu))
    if poznamka and not v["poznamka"]:
        chyby.append("%s: poznamka o chybejicim move() se nevypisuje" % nazev)
    if fail_vzor and not any(fail_vzor in l for l in v["fail"]):
        chyby.append("%s: ve FAIL neni %r — chytilo to neco jineho"
                     % (nazev, fail_vzor))


# ČÍSLA NÍŽ NEJSOU OPSANÁ Z HANDOFFU — jsou to MOJE naměřené hodnoty.
# Pozor na rozdíl proti `a-mutace-run.py`: ten běží nad SCRA TCHEM, kde je
# z Úkolu B jen `combat.gd` a NE i blok v testech → 60/61 kontrol. Tady běží
# CELÝ soubor testů z klonu (Úkol A i B) → čísla jsou o 4–5 vyšší, protože
# starý blok Úkolu B volá `resolve()` a ten v `origin/main` spadne na `has()`.
ocekavej("1-baseline", 59, 0)
ocekavej("2-opraveny-test", 64, 0, izo_pokusu=None, poznamka=True)
ocekavej("3-pres-level", 65, 1, izo_pokusu=1,
         fail_vzor="player.move() nebere izo projekci z úrovně")
ocekavej("4-zdravy", 65, 0, izo_pokusu=0)
# KLÍČOVÝ BĚH: `move()` SE úrovně ptá (na průchodnost) — a přesto musí projít.
# Kdyby spadl, brána by měřila „ptá se úrovně", ne „bere izo projekci".
ocekavej("5-pres-walk", 65, 0, izo_pokusu=0)
ocekavej("6-stary-pres-level", 60, 1,
         fail_vzor="player volá izo projekci přes world, ne přes level")

print()
for nazev in REZIMY:
    v = vysledky.get(nazev)
    print("  %-20s %s" % (nazev, ("%d kontrol, %d selhání"
                                  % (v["kontrol"], v["selhani"])) if v else "NEDOBEHL"))

print()
if chyby:
    print("NALEZENO %d ROZCHODU:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("VŠE SEDÍ — oba směry mutace doloženy VLASTNÍM spuštěním")
sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""H17 — měří, KTEROU VĚTEV `_cislo()` test Úkolu B skutečně cvičí.

Nález z `h17-mutace-b.py`: mutace M3 (odebrání větve `hodnota()`) testy
NESHODÍ. Tenhle skript zjišťuje, čím to je — a rozlišuje tři možné příčiny:

  (a) větev `hodnota()` se v testu vůbec nevolá (test ji needvidí), nebo
  (b) volá se, ale obě větve vracejí TOTÉŽ číslo (test je necitlivý), nebo
  (c) mutace se neprovedla.

Metoda: `_cislo()` se dočasně OZNAČÍ (přidá se čítač větví) a testy se spustí.
Když čítač větve `hodnota()` zůstane 0, platí (a).

Použití:  python _analyza\\h17-sonda-vetve.py
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

# Sonda: přidá čítače OBOU větví a vypíše je na konci každého volání.
PUVODNI_CISLO = 'if komponenta.has_method("hodnota"):\n\t\treturn int(komponenta.hodnota(klic))'
SONDA_CISLO = (
    'if komponenta.has_method("hodnota"):\n'
    '\t\t_cisla_vetev_a += 1\n'
    '\t\tprint("[sonda] vetev A (hodnota) pro ", klic)\n'
    '\t\treturn int(komponenta.hodnota(klic))\n'
    '\tif klic in komponenta:\n'
    '\t\t_cisla_vetev_b += 1\n'
    '\t\tprint("[sonda] vetev B (vlastnost) pro ", klic)'
)

SONDA_PROM = 'var _cisla_vetev_a := 0\nvar _cisla_vetev_b := 0\n'


def cti(c: Path) -> str:
    return c.read_text(encoding="utf-8")


def reset() -> None:
    r = subprocess.run([str(GIT), "-C", str(WT), "checkout", "--", "."],
                       capture_output=True, shell=True)
    assert r.returncode == 0
    for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
        shutil.copyfile(KLON / rel, WT / rel)


def spust():
    env = dict(os.environ)
    env["APPDATA"] = str(USER_DIR)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([str(GODOT), "--headless", "--path", str(WT),
                        "--script", "res://tests/run_tests.gd"],
                       capture_output=True, env=env, timeout=300)
    return (r.stdout.decode("utf-8", "replace")
            + r.stderr.decode("utf-8", "replace"))


reset()
t = cti(COMBAT)
assert PUVODNI_CISLO in t, "kotva pro sondu v combat.gd neni"
assert SONDA_PROM.splitlines()[0] not in t, "sonda uz tam je"
t2 = t.replace("const ZAKLADNI_SANCE := 0.5", SONDA_PROM + "const ZAKLADNI_SANCE := 0.5", 1)
assert t2 != t
t3 = t2.replace(PUVODNI_CISLO, SONDA_CISLO, 1)
assert t3 != t2, "MUTACE (sonda) NEPROBEHLA"
# POJISTKA (past overovani 7.14): měřená podmínka musí přestat platit.
assert 'if klic in komponenta:' in t3, "vetev B v sonde chybi"
COMBAT.write_bytes(t3.encode("utf-8"))
assert cti(COMBAT) == t3

print("=" * 78)
print("SONDA — která větev `_cislo()` se v testech volá")
print("=" * 78)
v = spust()
m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", v)
print("  SOUHRN: %s" % (m.group(0) if m else "NEDOBEHL"))
print()
vetev_a = [l.strip() for l in v.splitlines() if "vetev A" in l]
vetev_b = [l.strip() for l in v.splitlines() if "vetev B" in l]
print("  volání větve A (`hodnota(attr)`) : %d" % len(vetev_a))
for l in vetev_a[:10]:
    print("      %s" % l)
print("  volání větve B (vlastnost)       : %d" % len(vetev_b))
for l in vetev_b[:10]:
    print("      %s" % l)

reset()
assert "sonda" not in cti(COMBAT), "uklid sondy selhal"

# ---------------------------------------------------------------------------
# DRUHÁ SONDAA: umí test VŮBEC rozlišit „větev A napřed" od „větev B napřed"?
# Vloží se atrapa, kde `hodnota("Str")` vrací NĚCO JINÉHO než vlastnost `Str`
# (100 vs. 10). Kdyby test větve rozlišoval, musí se to projevit v damage.
# ---------------------------------------------------------------------------
ATRAPA = '''
class TestAtributyNecitlive:
	extends Node
	var Str := 10
	var Dex := 10

	func hodnota(klic: String) -> int:
		if klic == "Str":
			return 100
		if klic == "Dex":
			return 100
		return 0


'''
KOTVA_TRIDY = "class TestBojAtributy:"
KOTVA_TESTU = '''			var atr_h = TestAtributy.new()'''
VLOZ_TEST = '''			# SONDA: atributy, kde je `hodnota()` v ROZPORU s vlastnostmi.
			var atr_n = TestAtributyNecitlive.new()
			atr_n.Str = 10
			atr_n.Dex = 10
			kostra_b.add_child(atr_n)
			kostra_b.pridej("Attributes", atr_n)
			var skl_n = TestBojSkilly.new()
			kostra_b.add_child(skl_n)
			kostra_b.pridej("Skills", skl_n)
			var pres_rozpor = null
			for s2 in range(1, 41):
				seed(s2)
				var v4 = cb.resolve(utocnik_b, obrance_b)
				if v4.get("hit", false):
					pres_rozpor = v4
					break
			print("[sonda2] resolve() s rozpornymi atributy vraci: ", str(pres_rozpor))
'''
TESTY = WT / "tests" / "run_tests.gd"
te = cti(TESTY)
assert KOTVA_TRIDY in te, "kotva tridy neni"
te2 = te.replace(KOTVA_TRIDY, ATRAPA.lstrip("\n") + KOTVA_TRIDY, 1)
assert te2 != te
assert KOTVA_TESTU in te2, "kotva testu neni"
te3 = te2.replace(KOTVA_TESTU, VLOZ_TEST + KOTVA_TESTU, 1)
assert te3 != te2, "vlozeni sondy2 se neprovedlo"
TESTY.write_bytes(te3.encode("utf-8"))
assert cti(TESTY) == te3

print()
print("=" * 78)
print("SONDA 2 — jak se chová resolve(), když je `hodnota()` v ROZPORU s vlastností")
print("=" * 78)
for popis, zmutuj in (("S větví A (hodnota napřed)", False),
                      ("BEZ větve A (jen vlastnost)", True)):
    reset()
    # reset() přepsal i testy → sondu2 je nutné vložit znovu
    te = cti(TESTY)
    te2 = te.replace(KOTVA_TRIDY, ATRAPA.lstrip("\n") + KOTVA_TRIDY, 1)
    te3 = te2.replace(KOTVA_TESTU, VLOZ_TEST + KOTVA_TESTU, 1)
    TESTY.write_bytes(te3.encode("utf-8"))
    if zmutuj:
        c = cti(COMBAT)
        assert PUVODNI_CISLO in c
        c2 = c.replace(PUVODNI_CISLO, 'if false:', 1)
        assert c2 != c, "MUTACE NEPROBEHLA"
        assert PUVODNI_CISLO not in c2, "PODMINKA PORAD PLATI"
        COMBAT.write_bytes(c2.encode("utf-8"))
    v = spust()
    radky = [l.strip() for l in v.splitlines() if "sonda2" in l]
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", v)
    print("  %-30s %s" % (popis, m.group(0) if m else "NEDOBEHL"))
    for l in radky:
        print("      %s" % l)

reset()
assert "sonda" not in cti(COMBAT) and "TestAtributyNecitlive" not in cti(TESTY)
print()
print("  [uklizeno: combat.gd i run_tests.gd jsou zpet z klonu]")
print()
print("  [uklizeno: combat.gd je zpet z klonu]")
print()
if not vetev_a:
    print("ZÁVĚR: větev `hodnota()` se v testech NEVOLÁ ANI JEDNOU →")
    print("       test ji nemůže ochránit (mutace M3 proto nechycená).")
elif not vetev_b:
    print("ZÁVĚR: větev `vlastnost` se nevolá → test chrání jen `hodnota()`.")
else:
    print("ZÁVĚR: volají se OBĚ větve (A=%d, B=%d) — necitlivost je v číslech."
          % (len(vetev_a), len(vetev_b)))

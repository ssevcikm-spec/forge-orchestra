#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST `kronika-kontrola.py` NA FIXTUŘE — včetně tabulky NÁLEZŮ.

PROČ VZNIKL (nález **H12** → návrh **NA15**): `h17-kronika-mutace.py` testoval
tuhle bránu **jen na ŽIVÉ kronice**, a proto mu **prošla vada**, kterou pak
brána udělala v praxi: do výřezu bloku omylů se dostala **tabulka nálezů**
(řádky `| **H8** | …`) a brána hlásila **54 omylů místo 10**. Živý dokument
takový tvar v době testu neměl — **fixtura ho vyrobí řízeně**, a to je celý
rozdíl mezi „test, který projde" a „test, který měří".

CO SE TESTOVÁ (každá mutace míří na JINOU podmínku brány):

  A) KONTROLNÍ PŘÍPAD — fixtura bez vady musí PROJÍT (`exit 0`).
     Bez toho by každé spadnutí níž mohlo znamenat „fixtura je rozbitá".

  M1 počítání řádků omylů: `| **7** |` → `| **9** |`   → rozchod v části A
  M2 KOTVA BLOKU: konec bloku `8g` se vrátí na starou podobu („do konce
     souboru") a spolkne tabulku nálezů                     → rozchod v části A
  M3 KRITÉRIUM TVARU: filtr `radek.count("|") != 4` (tři neúspěšné opravy!)  →
     brána vrátí **0 omylů** a musí to být vidět jako rozchod
  M4 NÁLEZ: `H2` se v HANDOFFu přejmenuje na `H99`         → rozchod v části B
  M5 NÁLEZ V TABULCE NÁLEZŮ SE NESMÍ POČÍTAT JAKO OMYL: fixtura se rozšíří
     tak, aby tabulka nálezů stála NA KONCI bloku — a brána to musí ustát
     (kdyby ji počítala, je to táž vada jako v praxi)
  M6 NOVÝ BLOK OMYLŮ v dokumentu bez řádku v kronice §3 → ROZCHOD
     (se starým pevným seznamem by prošel zeleně — nález NA17)
  M7 ŘÁDEK V KRONICE bez bloku v dokumentu → ROZCHOD (opačný směr, dřív
     se neměřil vůbec)

⚠ KAŽDÁ MUTACE OVĚŘUJE DVĚ VĚCI (`overovani` §7.9 a §7.14):
  1. že se text SKUTEČNĚ změnil (`assert novy != puvodni`),
  2. že přestala platit MĚŘENÁ PODMÍNKA (např. `assert "| **7** |" not in novy`).
  Mutace, která se tiše neprovede, tvrdí totéž co mutace, která projde.

Použití:  python _analyza\t3-kronika-mutace.py
Návrat:   0 = brána měří (projde na zdravé fixtuře, spadne na každé z 5 vad)
"""

import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "kronika-kontrola.py"
DOCASNE = WS / "_analyza" / "_t3"
KRONIKA = DOCASNE / "KRONIKA-fixtura.md"
HANDOFF = DOCASNE / "HANDOFF-fixtura.md"

assert BRANA.is_file(), "brána %s není" % BRANA

# ---------------------------------------------------------------------- fixtura
# KRONIKA: sekce §1 (sessions), §2 (nálezy H), §3 (počty omylů), §4, §5.
# POZOR: v buňkách tabulek NEJSOU odkazy na .md soubory — část D brány hledá
# `[A-Za-z0-9][A-Za-z0-9_\-/]*\.md` v celém dokumentu a neexistující odkaz by
# shodil fixturu z důvodu, který s testovanou vadou nesouvisí (falešný poplach).
KRONIKA_FIXTURA = """# KRONIKA — FIXTURA pro mutační test

## 1. Přehledová tabulka — celý projekt

| # | Datum | Typ session | Co se stalo |
|---|---|---|---|
| **1** | 1. 10. 2026 | akční | první session |
| **2** | 2. 10. 2026 | plánovací | druhá session |
| **3** | 2. 10. 2026 | ověřovací | třetí session |
| **4** | 2. 10. 2026 | akční | čtvrtá session |
| **5** | 2. 10. 2026 | plánovací | pátá session |
| **6** | 2. 10. 2026 | ověřovací | šestá session |
| **7** | 2. 10. 2026 | akční | sedmá session |
| **8** | 2. 10. 2026 | plánovací | osmá session |
| **9** | 2. 10. 2026 | ověřovací | devátá session |
| **10** | 2. 10. 2026 | akční | desátá session |

## 2. Evidence nálezů

### 2.1 Nálezy H1–H7

| # | Co | Kde |
|---|---|---|
| **H1** | první nález | §16 |
| **H2** | druhy nález | §17 |
| **H3** | třetí nález | §17 |

## 3. Počty omylů — jediné místo, kde je vidět TREND

| Blok | Session | Počet omylů | Z toho vad MĚŘIDLA |
|---|---|---|---|
| **1–13** | první blok | **13** | hotovo |
| **8b** | druhy blok | **10** | hotovo |
| **8c** | třetí blok | **5** | hotovo |
| **8d** | čtvrtý blok | **6** | hotovo |
| **8e** | pátý blok | **11** | hotovo |
| **8f** | šestý blok | **10** | hotovo |
| **8g** | sedmý blok | **11** | hotovo |
| **8h** | osmý blok | **8** | hotovo |
| **8i** | devátý blok | **6** | hotovo |
| **8j** | desátý blok | **10** | hotovo |
| **8k** | jedenáctý blok | **5** | hotovo |
| **8l** | dvanáctý blok | **3** | hotovo |
| **8m** | třináctý blok | **8** | hotovo |

## 4. Poučení

Text poučení.

## 5. Návrhy

| # | Návrh | Stav |
|---|---|---|
| **NA1** | první návrh | APLIKOVÁNO |
"""

# HANDOFF: bloky omylů 8, 8b–8f (vzor z živého dokumentu) a 8g ZA §17 —
# přesně ten tvar, na kterém brána minula (kotva „do konce souboru" by spolkla
# tabulku nálezů níž). Plus tabulka nálezů a oddíly, které brána používá.
HANDOFF_FIXTURA = """# HANDOFF — FIXTURA

## 8. Vlastní omyly

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **1** | omyl jedna | pravda | měřidlo |
| **2** | omyl dva | pravda | měřidlo |
| **3** | omyl tři | pravda | měřidlo |
| **4** | omyl čtyři | pravda | měřidlo |
| **5** | omyl pět | pravda | měřidlo |
| **6** | omyl šest | pravda | měřidlo |
| **7** | omyl sedm | pravda | měřidlo |
| **8** | omyl osm | pravda | měřidlo |
| **9** | omyl devět | pravda | měřidlo |
| **10** | omyl deset | pravda | měřidlo |
| **11** | omyl jedenáct | pravda | měřidlo |
| **12** | omyl dvanáct | pravda | měřidlo |
| **13** | omyl třináct | pravda | měřidlo |

### 8b. Omyly ověřovací session

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **14** | omyl čtrnáct | pravda | měřidlo |
| **15** | omyl patnáct | pravda | měřidlo |
| **16** | omyl šestnáct | pravda | měřidlo |
| **17** | omyl sedmnáct | pravda | měřidlo |
| **18** | omyl osmnáct | pravda | měřidlo |
| **19** | omyl devatenáct | pravda | měřidlo |
| **20** | omyl dvacet | pravda | měřidlo |
| **21** | omyl dvacet jedna | pravda | měřidlo |
| **22** | omyl dvacet dva | pravda | měřidlo |
| **23** | omyl dvacet tři | pravda | měřidlo |

### 8c. Omyly session 2. 10. 2026 — FIXTURA

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **24** | omyl dvacet čtyři | pravda | měřidlo |
| **25** | omyl dvacet pět | pravda | měřidlo |
| **26** | omyl dvacet šest | pravda | měřidlo |
| **27** | omyl dvacet sedm | pravda | měřidlo |
| **28** | omyl dvacet osm | pravda | měřidlo |

### 8d. Omyly PLÁNOVACÍ session

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **29** | omyl dvacet devět | pravda | měřidlo |
| **30** | omyl třicet | pravda | měřidlo |
| **31** | omyl třicet jedna | pravda | měřidlo |
| **32** | omyl třicet dva | pravda | měřidlo |
| **33** | omyl třicet tři | pravda | měřidlo |
| **34** | omyl třicet čtyři | pravda | měřidlo |

### 8e. Omyly AKČNÍ session

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **35** | omyl třicet pět | pravda | měřidlo |
| **36** | omyl třicet šest | pravda | měřidlo |
| **37** | omyl třicet sedm | pravda | měřidlo |
| **38** | omyl třicet osm | pravda | měřidlo |
| **39** | omyl třicet devět | pravda | měřidlo |
| **40** | omyl čtyřicet | pravda | měřidlo |
| **41** | omyl čtyřicet jedna | pravda | měřidlo |
| **42** | omyl čtyřicet dva | pravda | měřidlo |
| **43** | omyl čtyřicet tři | pravda | měřidlo |
| **44** | omyl čtyřicet čtyři | pravda | měřidlo |
| **45** | omyl čtyřicet pět | pravda | měřidlo |

### 8f. Omyly PLÁNOVACÍ 2. 10. 2026 — FIXTURA

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **46** | omyl čtyřicet šest | pravda | měřidlo |
| **47** | omyl čtyřicet sedm | pravda | měřidlo |
| **48** | omyl čtyřicet osm | pravda | měřidlo |
| **49** | omyl čtyřicet devět | pravda | měřidlo |
| **50** | omyl padesát | pravda | měřidlo |
| **51** | omyl padesát jedna | pravda | měřidlo |
| **52** | omyl padesát dva | pravda | měřidlo |
| **53** | omyl padesát tři | pravda | měřidlo |
| **54** | omyl padesát čtyři | pravda | měřidlo |
| **55** | omyl padesát pět | pravda | měřidlo |

## 9. Co už otevřené NENÍ

Text oddílu 9 — na tenhle nadpis končí výřez bloku 8f (kotva v bráně).

## 15. Ověření práce

Text oddílu 15.

## 17. Ověření práce AKČNÍ session

Text oddílu 17.

### 8g. Omyly PLÁNOVACÍ 2. 10. 2026 — FIXTURA (blok 8g)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **56** | omyl padesát šest | pravda | měřidlo |
| **57** | omyl padesát sedm | pravda | měřidlo |
| **58** | omyl padesát osm | pravda | měřidlo |
| **59** | omyl padesát devět | pravda | měřidlo |
| **60** | omyl šedesát | pravda | měřidlo |
| **61** | omyl šedesát jedna | pravda | měřidlo |
| **62** | omyl šedesát dva | pravda | měřidlo |
| **63** | omyl šedesát tři | pravda | měřidlo |
| **64** | omyl šedesát čtyři | pravda | měřidlo |
| **65** | omyl šedesát pět | pravda | měřidlo |
| **66** | omyl šedesát šest | pravda | měřidlo |

### 8h. Omyly AKČNÍ session 2. 10. 2026 — FIXTURA (blok 8h)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **67** | omyl šedesát sedm | pravda | měřidlo |
| **68** | omyl šedesát osm | pravda | měřidlo |
| **69** | omyl šedesát devět | pravda | měřidlo |
| **70** | omyl sedmdesát | pravda | měřidlo |
| **71** | omyl sedmdesát jedna | pravda | měřidlo |
| **72** | omyl sedmdesát dva | pravda | měřidlo |
| **73** | omyl sedmdesát tři | pravda | měřidlo |
| **74** | omyl sedmdesát čtyři | pravda | měřidlo |

### 8i. Omyly PLÁNOVACÍ — FIXTURA (blok 8i)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **75** | omyl sedmdesát pět | pravda | měřidlo |
| **76** | omyl sedmdesát šest | pravda | měřidlo |
| **77** | omyl sedmdesát sedm | pravda | měřidlo |
| **78** | omyl sedmdesát osm | pravda | měřidlo |
| **79** | omyl sedmdesát devět | pravda | měřidlo |
| **80** | omyl osmdesát | pravda | měřidlo |

### 8j. Omyly AKČNÍ session — FIXTURA (blok 8j)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **81** | omyl osmdesát jedna | pravda | měřidlo |
| **82** | omyl osmdesát dva | pravda | měřidlo |
| **83** | omyl osmdesát tři | pravda | měřidlo |
| **84** | omyl osmdesát čtyři | pravda | měřidlo |
| **85** | omyl osmdesát pět | pravda | měřidlo |
| **86** | omyl osmdesát šest | pravda | měřidlo |
| **87** | omyl osmdesát sedm | pravda | měřidlo |
| **88** | omyl osmdesát osm | pravda | měřidlo |
| **89** | omyl osmdesát devět | pravda | měřidlo |
| **90** | omyl devadesát | pravda | měřidlo |

### 8k. Omyly PLÁNOVACÍ — FIXTURA (blok 8k)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **91** | omyl devadesát jedna | pravda | měřidlo |
| **92** | omyl devadesát dva | pravda | měřidlo |
| **93** | omyl devadesát tři | pravda | měřidlo |
| **94** | omyl devadesát čtyři | pravda | měřidlo |
| **95** | omyl devadesát pět | pravda | měřidlo |

### 8l. Omyly AKČNÍ session — FIXTURA (blok 8l)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **96** | omyl devadesát šest | pravda | měřidlo |
| **97** | omyl devadesát sedm | pravda | měřidlo |
| **98** | omyl devadesát osm | pravda | měřidlo |

### 8m. Omyly AKČNÍ session — FIXTURA (blok 8m)

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **99** | omyl devadesát devět | pravda | měřidlo |
| **100** | omyl sto | pravda | měřidlo |
| **101** | omyl sto jedna | pravda | měřidlo |
| **102** | omyl sto dva | pravda | měřidlo |
| **103** | omyl sto tři | pravda | měřidlo |
| **104** | omyl sto čtyři | pravda | měřidlo |
| **105** | omyl sto pět | pravda | měřidlo |
| **106** | omyl sto šest | pravda | měřidlo |

## 18. Ověření práce AKČNÍ session

### 18.1 Nálezy téhle session

| # | Co zadání tvrdilo | Naměřeno | Proč to je nález |
|---|---|---|---|
| **H1** | první tvrzení | pravda | nález |
| **H2** | druhe tvrzení | pravda | nález |
| **H3** | třetí tvrzení | pravda | nález |
| **H8** | osme tvrzení | pravda | nález |
| **H9** | devate tvrzení | pravda | nález |
| **H10** | desate tvrzení | pravda | nález |
| **H11** | jedenacte tvrzení | pravda | nález |
| **H12** | dvanacte tvrzení | pravda | nález |
| **H13** | trinacte tvrzení | pravda | nález |
"""


def spust(kronika: str, handoff: str):
    """Spustí bránu nad ZADANÝMI texty. Vrací (exit, výstup)."""
    KRONIKA.write_bytes(kronika.encode("utf-8"))
    HANDOFF.write_bytes(handoff.encode("utf-8"))
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    # Živé měření session se ve fixtuře vypíná: `dsh-usage` je pomalý a jeho
    # číslo s fixturou nesouvisí. Vypnuté měření se VYPÍŠE jako poznámka —
    # nikdy jako ticho (skill `overovani` §2.3).
    env["KRONIKA_BEZ_ZIVEHO"] = "1"
    r = subprocess.run([sys.executable, str(BRANA), str(KRONIKA), str(HANDOFF)],
                       capture_output=True, cwd=str(WS), env=env)
    v = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, v


DOCASNE.mkdir(parents=True, exist_ok=True)
# ⚠ ÚKLID MUSÍ BÝT I NA CHYBOVÉ CESTĚ — naměřeno 2. 10. 2026 (21:2x UTC):
# `shutil.rmtree(DOCASNE)` bylo **až na konci skriptu** (ř. 472), ale skript má
# **tři `sys.exit`** (2 při rozbité fixtuře, 1 při rozchodu, 0 na konci).
# Když spadl na `sys.exit(2)`, úklid se **nikdy nespustil** a ve `_analyza\_t3`
# **zůstaly fixtury** `KRONIKA-fixtura.md` a `HANDOFF-fixtura.md`.
# **Následek, který to odhalil:** `audit1-inventar.py` je začal počítat jako
# **dokumenty bez hlavičky** (14 → 16) — tedy **brána si vyrobila vlastní
# falešný nález** tím, že po sobě neuklidila.
# Je to táž třída jako `overovani` §10.6 („mutace, která spadne mezi zápisem
# a návratem, nechá dokument zmutovaný") — jen u **dočasných souborů**.
# Řešení: úklid v `finally`, ne na konci.
import atexit                                                   # noqa: E402

atexit.register(lambda: shutil.rmtree(DOCASNE, ignore_errors=True))

print("=" * 78)
print("MUTAČNÍ TEST `kronika-kontrola.py` NA FIXTUŘE (s tabulkou nálezů)")
print("=" * 78)

# Kotvy se ČTOU Z BRÁNY, neopisují se — kdyby se změnily, test musí padnout
# na tom, že je nenašel, ne měřit něco jiného (past `overovani` §7.11).
#
# ⚠ OD 2. 10. 2026 MÁ SEZNAM JINÝ TVAR: `BLOKY` je **dvojice (název, kotva)**
# a konec bloku se hledá **nadpisem** (`blok_do_nadpisu`), protože poziční
# kotvy přestaly rozlišovat bloky, jakmile se `8h` vložil mezi `8g` a `## 18.`.
# Test to ověřuje — jinak by „test prošel" znamenalo, že měří starý kontrakt.
zdroj = BRANA.read_text(encoding="utf-8")
# ⚠ OD 3. 10. 2026 MÁ BRÁNA JINÝ KONTRAKT: bloky omylů **hledá v dokumentu**
# (`bloky_omylu`), ne v pevném seznamu kotev. Test to musí ověřovat — jinak by
# „test prošel“ znamenalo, že měří starý kontrakt (`overovani` §7.11).
# Byl to **pátý** výskyt téhož vzorce (NA17): `8i`–`8n` postupně vznikaly
# a pevný seznam je neznal, takže brána počítala staré číslo a nebylo to vidět.
assert "def bloky_omylu(" in zdroj and "BLOKY = bloky_omylu(hand)" in zdroj, \
    "brána nehledá bloky omylů v dokumentu — test by měřil jiný kontrakt"
assert not re.search(r"^BLOKY\s*=\s*\[", zdroj, re.M), \
    "brána má ZNOVU pevný seznam BLOKY — test by měřil jiný kontrakt"
assert "klice_bloku" in zdroj, \
    "brána neměří opačný směr (řádek v kronice bez bloku) — test měří jiný kontrakt"
assert "blok_do_nadpisu(hand, od, dalsi)" in zdroj, \
    "brána nepoužívá hledání konce bloku nadpisem — test měří jiný kontrakt"
assert "najdi_radek_nadpisu(text, od)" in zdroj, \
    "brána nehledá kotvu po ŘÁDCÍCH — test měří jiný kontrakt"

vysledky = []

# Co která značka znamená — JEDINÉ místo, kde se to rozhoduje.
#   KONTROLNI = fixtura/kotva je v pořádku → brána MUSÍ projít (exit 0)
#   VADA      = vrácená vada              → brána MUSÍ spadnout (nenulový exit)
OCEKAVANY_EXIT = {
    "KONTROLNI": 0,
    "KONTROLNI-kotva": 0,
    "VADA": 1,
    "VADA-tvar": 1,
}

# ------------------------------------------------------------------ A) kontrola
print()
print("-" * 78)
print("A) KONTROLNÍ PŘÍPAD — fixtura BEZ vady (musí projít)")
print("-" * 78)
kod, v = spust(KRONIKA_FIXTURA, HANDOFF_FIXTURA)
radky = [l for l in v.splitlines() if "skutečný počet omylů" in l or "omylů celkem" in l]
for l in radky:
    print("   " + l.strip())
print("   exit=%d %s" % (kod, "OK" if kod == 0 else "!! fixtura je rozbitá, ne brána"))
if kod != 0:
    print("   --- výstup brány ---")
    for l in v.splitlines()[-30:]:
        print("   " + l)
    sys.exit(2)
vysledky.append(("A kontrolní případ (zdravá fixtura)", kod, 0))

# ------------------------------------------------------------------ M1 až M5
MUTACE = []

# M1 — přehozený počet omylů v části A (kronika tvrdí jinak než HANDOFF)
t = KRONIKA_FIXTURA
assert "| **8g** | sedmý blok | **11** | hotovo |" in t, "M1: řádek 8g v kronize není"
m1 = t.replace("| **8g** | sedmý blok | **11** | hotovo |",
               "| **8g** | sedmý blok | **7** | hotovo |", 1)
assert m1 != t and "| **8g** | sedmý blok | **7** |" in m1, "M1: mutace se neprovedla"
MUTACE.append(("M1 počet omylů 8g: 11 -> 7", m1, HANDOFF_FIXTURA, "VADA"))

# M2 — PŘEJMENOVANÝ KONEC NADPISU. Není to vada: kotva v bráně je
#      `### 8d. Omyly PLÁNOVACÍ session` a je to **PREFIX**, takže text ZA ní
#      („2. 10. 2026 …") se smí měnit — a to je dobře, protože `HANDOFF.md`
#      se pořád připisuje a nadpisy dostávají data. Test to měří **jako
#      nezávislý případ**: počet omylů bloku 8d musí zůstat **6**.
#      (Kdyby se kotva musela shodovat CELÁ, brána by po každém doplnění
#      nadpisu měřila nulu — a to je přesně „naměřená nula s jiným důvodem".)
m2_najdi = "### 8d. Omyly PLÁNOVACÍ session\n\n| # | Co jsem si myslel"
m2_nahrad = "### 8d. Omyly PLÁNOVACÍ session 2. 10. 2026 — doplněno\n\n| # | Co jsem si myslel"
assert m2_najdi in HANDOFF_FIXTURA, "M2: kotva bloku 8d ve fixtuře není"
m2 = HANDOFF_FIXTURA.replace(m2_najdi, m2_nahrad, 1)
assert m2 != HANDOFF_FIXTURA and "— doplněno" in m2, "M2: mutace se neprovedla"
MUTACE.append(("M2 doplněný konec nadpisu 8d (prefix kotvy to ustojí, 6 omylů)",
               KRONIKA_FIXTURA, m2, "KONTROLNI"))

# M3 — KRITÉRIUM TVARU `count("|") != 4` (tři neúspěšné opravy v praxi): tímhle
#      filtrem brána vrátila **0 omylů**. Tady se vkládá do KOPIE brány.
#      Fixtura dokazuje, že kritérium tvaru na SPRÁVNÉM vstupu selže — proto
#      se ptáme na VÝZNAM sloupce (číslo), ne na počet oddělovačů.
m3 = KRONIKA_FIXTURA
MUTACE.append(("M3 kritérium tvaru count('|') != 4 (vpraveno do brány)",
               m3, HANDOFF_FIXTURA, "VADA-tvar"))

# M4 — nález H2 přejmenován v HANDOFFu
h4 = HANDOFF_FIXTURA
assert "| **H2** | druhe tvrzení |" in h4, "M4: řádek nálezu H2 v HANDOFFu není"
m4 = h4.replace("| **H2** | druhe tvrzení |", "| **H99** | druhe tvrzení |", 1)
assert m4 != h4 and "| **H2** |" not in m4, "M4: mutace se neprovedla"
MUTACE.append(("M4 nález H2 -> H99 v HANDOFFu", KRONIKA_FIXTURA, m4, "VADA"))

# M5 — DVĚ tabulky za blokem 8g: nejdřív skutečné omyly, pak tabulka nálezů.
#      Tohle je nejtvrdší případ — kotva „do konce souboru" i kotva na `## 18.`
#      mají pořád co najít, ale správná odpověď je **68**, ne 77. Kdyby brána
#      počítala i nálezy, vyjde jiné číslo (a ROZCHOD v části A).
m5 = HANDOFF_FIXTURA.replace(
    "## 18. Ověření práce AKČNÍ session",
    "## 18. Ověření práce AKČNÍ session\n\n"
    "### 18.0 Nálezy, které se do omylů NESMÍ počítat\n\n"
    "| # | Co zadání tvrdilo | Naměřeno | Proč to je nález |\n"
    "|---|---|---|---|\n"
    "| **H20** | prvni | pravda | nález |\n"
    "| **H21** | druhy | pravda | nález |\n"
    "| **H22** | treti | pravda | nález |\n", 1)
assert m5 != HANDOFF_FIXTURA and "| **H20** |" in m5, "M5: mutace se neprovedla"
MUTACE.append(("M5 dvě tabulky za blokem 8g (omylů 11 + nálezů 3, čekej 11)",
               KRONIKA_FIXTURA, m5, "KONTROLNI"))

# M6 — NOVÝ BLOK OMYLŮ V DOKUMENTU, KTERÝ V KRONICE ŘÁDEK NEMÁ.
#      Přesně to je nález NA17: bloky `8i`–`8n` postupně vznikaly a **pevný
#      seznam v bráně je neznal** → brána počítala staré číslo a NIC nehlásila.
#      Se starou bránou tenhle případ skončí ZELENĚ; s novou (bloky z dokumentu)
#      musí spadnout jako ROZCHOD. Proto je to mutace, ne kosmetika.
m6_najdi = "\n## 9. Co už otevřené NENÍ\n"
m6_nahrad = ("\n### 8z. Omyly AKČNÍ session — FIXTURA (blok, který v kronice není)\n\n"
             "| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |\n"
             "|---|---|---|---|\n"
             "| **107** | omyl sto sedm | pravda | měřidlo |\n"
             "| **108** | omyl sto osm | pravda | měřidlo |\n"
             "\n## 9. Co už otevřené NENÍ\n")
assert m6_najdi in HANDOFF_FIXTURA, "M6: oddíl 9 ve fixtuře není"
m6 = HANDOFF_FIXTURA.replace(m6_najdi, m6_nahrad, 1)
assert m6 != HANDOFF_FIXTURA and "### 8z." in m6, "M6: mutace se neprovedla"
MUTACE.append(("M6 nový blok 8z v dokumentu bez řádku v kronice", KRONIKA_FIXTURA, m6, "VADA"))

# M7 — OPAČNÝ SMĚR: řádek v kronice §3, pro který v dokumentu NENÍ blok.
#      Do 3. 10. 2026 se tenhle směr neměřil VŮBEC — a je to stejná vada jako
#      M6, jen obráceně: v trendu je číslo, které v `HANDOFF.md` nejde dohledat.
m7_najdi = "| **8m** | třináctý blok | **8** | hotovo |\n"
m7_nahrad = (m7_najdi +
             "| **8y** | blok, který v HANDOFFu NENÍ | **4** | hotovo |\n")
assert m7_najdi in KRONIKA_FIXTURA, "M7: řádek 8m v kronice fixtury není"
m7 = KRONIKA_FIXTURA.replace(m7_najdi, m7_nahrad, 1)
assert m7 != KRONIKA_FIXTURA and "| **8y** |" in m7, "M7: mutace se neprovedla"
MUTACE.append(("M7 řádek 8y v kronice bez bloku v dokumentu", m7, HANDOFF_FIXTURA, "VADA"))

for popis, kron, hand, ocekavana in MUTACE:
    print()
    print("-" * 78)
    print("%s   [%s]" % (popis, ocekavana))
    print("-" * 78)
    if ocekavana == "VADA-tvar":
        # M3: do KOPIE brány se vloží kritérium tvaru — přesně to, co třikrát
        # selhalo v praxi (brána pak hlásila 0 omylů, tedy „naměřenou nulu").
        docasna_brana = WS / "_analyza" / "_t3-brana-tvar.py"
        puvodni = '        m = re.match(r"^\\|\\s*\\*{0,2}(\\d+)\\*{0,2}\\s*\\|", radek)'
        assert puvodni in zdroj, "M3: v bráně se nenašel řádek s kritériem id"
        nova = ('        if radek.count("|") != 4:\n'
                '            continue\n' + puvodni)
        tvar = zdroj.replace(puvodni, nova, 1)
        assert tvar != zdroj and 'radek.count("|") != 4' in tvar, "M3: mutace se neprovedla"
        docasna_brana.write_bytes(tvar.encode("utf-8"))
        KRONIKA.write_bytes(KRONIKA_FIXTURA.encode("utf-8"))
        HANDOFF.write_bytes(HANDOFF_FIXTURA.encode("utf-8"))
        env = dict(os.environ)
        env["PYTHONIOENCODING"] = "utf-8"
        env["KRONIKA_BEZ_ZIVEHO"] = "1"
        r = subprocess.run([sys.executable, str(docasna_brana), str(KRONIKA), str(HANDOFF)],
                           capture_output=True, cwd=str(WS), env=env)
        kod = r.returncode
        v = (r.stdout + r.stderr).decode("utf-8", "replace")
        docasna_brana.unlink(missing_ok=True)
    else:
        kod, v = spust(kron, hand)
    chyb = [l.strip() for l in v.splitlines() if l.strip().startswith("CHYBA")]
    print("   exit=%d" % kod)
    for l in chyb[:5]:
        print("     %s" % l[:130])
    if not chyb:
        print("     (žádná CHYBA v části A/B — brána vadu neviděla)")
    # Význam značky se čte Z JEDNOHO MÍSTA (tabulka níž) — jinak se snadno
    # stane, že test hlásí ROZCHOD na případu, který sám označil za vadný
    # (naměřeno při psaní: tři různé podmínky `==`/`!=` na jednom řádku).
    vysledky.append((popis, kod, OCEKAVANY_EXIT[ocekavana]))

# ---------------------------------------------------------------------- závěr
shutil.rmtree(DOCASNE, ignore_errors=True)
print()
print("  [úklid: dočasná složka %s smazána]" % DOCASNE.name)
print()
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
chyby = []
for popis, kod, ocekavany in vysledky:
    ok = (kod != 0) if ocekavany else (kod == 0)
    print("  %-52s exit=%-3d %s" % (popis, kod, "OK" if ok else "ROZCHOD"))
    if not ok:
        chyby.append("%s: exit=%d, očekáváno %s"
                     % (popis, kod, "nenulový" if ocekavany else "0"))
print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("BRÁNA MĚŘÍ — projde na zdravé fixtuře (i na doplněném nadpisu bloku)")
print("a SPADNE na každé vrácené vadě; jejich počet je na řádku níž. Číslo se sem")
print("ZÁMĚRNĚ nepsalo — dřív tu stálo „3“, což po přidání M6/M7 zestaralo.")
print("Fixtura má i tabulku NÁLEZŮ — tvar, který živý dokument v době starého")
print("testu neměl, a proto ta vada prošla.")
# Strojově čitelný počet: nadřazený `g3-brany.py` z něj bere, CO brána otevřela
# (past S27) — bez tohohle řádku vypadal běh jako „otevřela: 0“, tedy jako by
# se nic nezměřilo, ačkoli proběhlo 6 případů.
print("PŘÍPADŮ CELKEM: %d (kontrolních %d, vad %d)"
      % (len(vysledky),
         sum(1 for _p, _k, o in vysledky if o == 0),
         sum(1 for _p, _k, o in vysledky if o != 0)))
sys.exit(0)

# -*- coding: utf-8 -*-
r"""P20 — Úkol C: mají opakovatelné ověřovací skripty vstoupit do `g3`?

ZADÁNÍ: u každého kandidáta změřit, **jak dlouho běží** a **co měří**
(stav? mutaci? obojí?), a rozhodnout, které se zařazují (a s jakým ČÍTAČEM
do `BRANY`) a které zůstávají doklady — a proč.

⚠ Brána bez čítače = `g3` dnes SPADNE (`OCEKAVANE_BEZ_CITACE`). Každý zařazený
skript tedy MUSÍ vykazovat číslo — a to se tady měří, ne odhaduje.

CO SE MĚŘÍ PRO KAŽDÉHO KANDIDÁTA:
  * `exit`,
  * doba běhu,
  * má výstup řádek s čítačem? (a jaký — `VÝSLEDEK:`/`ZMĚŘENO:`/`KONTROL`),
  * sahá na ŽIVÝ soubor (mutuje)? (staticky: hledá `write_bytes`/`write_text`
    nad cestou ve `WS`/`HRA`),
  * je závislý na STAVU (deployment, jednorázový patch)?

Použití: python _analyza/p20-c-kandidati.py
"""

import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"

# (soubor, co od něj zadání očekává) — seznam je ZADÁNÍ, ne nález.
KANDIDATI = [
    "ov-b1-compile.py",
    "ov-e-h79-mez.py",
    "ov-g-h92-sken.py",
    "ov-g-neovereno.py",
    "p19-b-kontroly.py",
    "p19-b2-kontroly-h79.py",
    "p19-c-h94-podpisy.py",
    "p19-d-kontroly.py",
]

# Vzory čítačů, které `g3` umí přečíst (bere POSLEDNÍ výskyt).
VZORY_CITACU = [
    (r"VÝSLEDEK:\s*(\d+) kontrol, (\d+) chyb", "VÝSLEDEK: N kontrol, M chyb"),
    (r"ZMĚŘENO:\s*(\d+)", "ZMĚŘENO: N"),
    (r"Kontrol:\s*(\d+)", "Kontrol: N"),
    (r"(\d+) kontrol, (\d+) chyb", "N kontrol, M chyb"),
    (r"(\d+)/(\d+)", "N/M"),
]

print("=" * 78)
print("P20/C — kandidáti na zařazení do `g3`: co měří a jak dlouho běží")
print("=" * 78)

radky = []
for jmeno in KANDIDATI:
    f = ANALYZA / jmeno
    if not f.is_file():
        print(f"\n  ⚠ {jmeno} NEEXISTUJE — kandidát ze zadání, ale soubor není")
        radky.append((jmeno, "NEEXISTUJE", "", "", ""))
        continue
    text = f.read_text(encoding="utf-8", errors="replace")
    # Staticky: sahá na ŽIVÝ soubor? (mutace se pozná podle zápisu)
    zapisuje = bool(re.search(r"\.write_(bytes|text)\(", text))
    # Dynamicky: spustit a změřit
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-B", str(f)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           cwd=str(WS), timeout=900)
        kod = r.returncode
        v = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        kod, v = "TIMEOUT", ""
    trvani = time.time() - t0
    # Který čítač výstup nese (POSLEDNÍ výskyt, jako to dělá g3)
    citac = "— (žádný)"
    for vzor, popis in VZORY_CITACU:
        posledni = None
        for posledni in re.finditer(vzor, v):
            pass
        if posledni:
            skup = [g for g in posledni.groups() if g]
            citac = popis + "  →  " + " / ".join(skup)
            break
    posledni_radky = [l.strip() for l in v.splitlines() if l.strip()][-2:]
    print(f"\n--- {jmeno} ------------------------------------------")
    print(f"    exit={kod}   doba={trvani:.1f} s   zápis do souboru: {zapisuje}")
    print(f"    čítač: {citac}")
    for l in posledni_radky:
        print(f"      | {l[:150]}")
    radky.append((jmeno, kod, f"{trvani:.1f}s", citac,
                  "zapisuje" if zapisuje else "jen čte"))

print("\n" + "=" * 78)
print("SOUHRN")
print("=" * 78)
print(f"  {'skript':32} {'exit':>7} {'doba':>7}  zápis")
for jmeno, kod, doba, citac, zapis in radky:
    print(f"  {jmeno:32} {str(kod):>7} {doba:>7}  {zapis}")
print("=" * 78)

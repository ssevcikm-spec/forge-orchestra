# -*- coding: utf-8 -*-
r"""P20 — Úkol D (část): SPUSTÍ VŠECHNY DOKLADY `_analyza/` a vypíše, které projdou.

PROČ: doklady jsou důkazy a **nesmí tiše shnít**. Session, která mění brány,
musí vědět, které doklady tím rozbila — jinak zůstanou červené a nikdo nepozná,
jestli je vada v bráně, nebo v dokladu (`overovani` §10.1: `exit 1` ze špatného
důvodu vypadá jako správný nález).

⚠ NENÍ to náhrada `g3`: `g3` pouští jen VYBRANÉ brány. Tohle pouští i DOKLADY,
které v `g3` záměrně nejsou (jsou jednorázové nebo stavové) — proto se výsledek
nevydává za stav bran.

Použití: python _analyza/p20-d-doklady.py
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
VZOR = re.compile(r"^(ov-|p1[6-9]-|p20-)")

# Sonda `p20-sonda-*` a `p20-c-kandidati` jsou JEDNORÁZOVÉ diagnostiky —
# spouštět je znovu nemá smysl (a `p20-c-kandidati` pouští ostatní doklady).
# ⚠ `p20-sonda-klicu.py` si navíc staví VLASTNÍ harness z živého `g3` a sahá
# přitom na `p20-scratch`; pouštět ho v dávce je zbytečné riziko.
PRESKOCIT = {"p20-sonda-jmena.py", "p20-sonda-klicu.py", "p20-c-kandidati.py",
             "p20-d-doklady.py"}

skripty = sorted(p for p in ANALYZA.glob("*.py")
                 if VZOR.match(p.name) and p.name not in PRESKOCIT)

print("=" * 78)
print("P20/D — všechny doklady `_analyza/`: projdou ještě?")
print("=" * 78)
print(f"  skriptů: {len(skripty)}\n")

vysledky = []
for p in skripty:
    t0 = time.time()
    try:
        r = subprocess.run([sys.executable, "-B", str(p)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           cwd=str(WS), timeout=1800)
        kod = r.returncode
        v = (r.stdout or "") + (r.stderr or "")
    except subprocess.TimeoutExpired:
        kod, v = "TIMEOUT", ""
    trvani = time.time() - t0
    m = None
    for m in re.finditer(r"VÝSLEDEK[^\n]*?(\d+) kontrol, (\d+) chyb", v):
        pass
    citac = f"{m.group(1)}/{m.group(2)}" if m else "—"
    vysledky.append((p.name, kod, trvani, citac, v))
    stav = "OK   " if kod == 0 else f"exit={kod}"
    print(f"  {stav:8} {p.name:34} {trvani:6.1f}s  kontroly: {citac}")

selhale = [x for x in vysledky if x[1] != 0]
print("\n" + "=" * 78)
print(f"SOUHRN: {len(vysledky)} dokladů, {len(selhale)} s nenulovým exit")
print("=" * 78)
for jmeno, kod, trvani, citac, v in selhale:
    print(f"\n--- {jmeno}  (exit={kod}) ---")
    chyby = [l.strip() for l in v.splitlines() if "CHYBA" in l]
    for l in chyby[:8]:
        print(f"    {l[:160]}")
    if not chyby:
        for l in [x for x in v.splitlines() if x.strip()][-6:]:
            print(f"    | {l[:160]}")

sys.exit(1 if selhale else 0)

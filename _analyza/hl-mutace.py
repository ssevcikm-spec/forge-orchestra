#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""MUTACNI TEST mericího skriptu _analyza/hl-sql.py.

Otazka: umi ten test vubec spadnout? Vlozi do KOPIE zdroje conductora vady,
o kterych vime, ze byly v historii skutecne, a overi, ze na kazdou z nich
hl-sql.py zareaguje (jinak je test slepy, ne zeleny).

Nic nemeni v orchestra - pracuje s kopii v _analyza/tmp-mutace/.
Spusteni: $env:PYTHONIOENCODING='utf-8'; python _analyza/hl-mutace.py
"""
import os
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = r"C:\Users\Ssevc\Local-Deepseek"
ORCH = os.path.join(WS, "orchestra")
TMP = os.path.join(WS, "_analyza", "tmp-mutace")
SRC_TS = os.path.join(ORCH, "conductor", "src", "index.ts")
SKRIPT = os.path.join(WS, "_analyza", "hl-sql.py")

# VADY: (popis, co najit, cim nahradit) - vsechny skutecne existovaly v historii
VADY = [
    ("guard se prehlédne pres rm.status (vada z 30. 9., 'prvni verze opravy')",
     "AND rm.updated_at > datetime('now', ?)",
     "AND rm.status = 'failed'"),
    ("guard kontroluje jen status, ne cas (cooldown se vubec neuplatni)",
     "AND rm.updated_at > datetime('now', ?)",
     "AND 1=1"),
    ("guard bez LIMIT 25 (dispatchne vsechno naraz)",
     "ORDER BY id LIMIT 25",
     "ORDER BY id"),
]

if not os.path.exists(os.path.join(TMP, "orchestra", "conductor", "src")):
    os.makedirs(os.path.join(TMP, "orchestra", "conductor", "src"), exist_ok=True)


def spust_hl_sql(cesta_ts):
    """Spusti hl-sql.py proti zadanemu index.ts (pres docasny symlink/ kopii)."""
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    env["HL_TS"] = cesta_ts
    r = subprocess.run([sys.executable, SKRIPT], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", env=env)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


# 1) zdrava predloha
zdrava = os.path.join(TMP, "orchestra", "conductor", "src", "index.ts")
shutil.copyfile(SRC_TS, zdrava)
kod, vystup = spust_hl_sql(zdrava)
print(f"=== 0) ZDRAVY KOD: exit={kod} (ocekavano 0) ===")
if kod != 0:
    print(vystup[-1500:])
    sys.exit("zdravy kod neprosel - test je rozbity, ne slaby")

obsah = open(SRC_TS, encoding="utf-8").read()
selhalo = 0
for i, (popis, najdi, nahrad) in enumerate(VADY, 1):
    if najdi not in obsah:
        print(f"=== {i}) PRESKOCENO: v source NENI {najdi!r} ===")
        selhalo += 1
        continue
    vadny = obsah.replace(najdi, nahrad, 1)
    p = os.path.join(TMP, "orchestra", "conductor", "src", "index.ts")
    open(p, "w", encoding="utf-8", newline="").write(vadny)
    kod, vystup = spust_hl_sql(p)
    chytil = kod != 0
    print(f"=== {i}) {popis} ===")
    print(f"    exit={kod}  → {'CHYCENO (test ma zuby)' if chytil else 'NECHYCENO – test je slepy!'}")
    if not chytil:
        selhalo += 1
        print("    " + vystup[-800:].replace("\n", "\n    "))

print(f"\n=== VYSLEDEK MUTACNIHO TESTU: {len(VADY) - selhalo}/{len(VADY)} vad chyceno ===")
print("(vada = zmena, kterou by test MEL odhalit; 0 chycenych znamena slepy test)")
shutil.rmtree(TMP, ignore_errors=True)
if selhalo:
    sys.exit(1)

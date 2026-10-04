"""Ověří, že v origin/main jsou OPRAVENÉ soubory (bajt po bajtu proti tomu,
co jsem měřil v Godotu) — a že se to shoduje s prací na větvích.

Autorita je blob v gitu, ne velikost souboru na disku (past §5b skillu).
"""
import hashlib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
REPO = WS / "games" / "uo-shadows"
GIT = str(WS / "orchestra" / "tools" / "git.cmd")

DVOJICE = [
    ("scripts/save.gd", WS / "_analyza" / "fixcheck" / "save.gd", "139"),
    ("scripts/hud.gd", WS / "_analyza" / "fixcheck" / "hud.gd", "140"),
    ("scripts/mining.gd", WS / "_analyza" / "fixcheck" / "mining.gd", None),
]

for cesta, opraveny, vetev in DVOJICE:
    p = subprocess.run([GIT, "-C", str(REPO), "show", f"origin/main:{cesta}"],
                       capture_output=True, shell=True)
    blob = p.stdout
    # POJISTKA: prázdný výstup znamená, že se měření NEPOVEDLO (špatná cesta,
    # spadlý git) — nesmí se to vypsat jako "neshoda".
    if p.returncode != 0 or not blob:
        print(f"{cesta}: MĚŘENÍ NEPROBĚHLO (rc={p.returncode}, {len(blob)} B)"
              f" → {p.stderr.decode('utf-8', 'replace')[:120]}")
        continue
    lokalni = opraveny.read_bytes()
    h = lambda b: hashlib.sha256(b).hexdigest()[:16]
    print(f"{cesta}")
    print(f"  origin/main            {len(blob):5} B  {h(blob)}")
    print(f"  opraveny (měřený)      {len(lokalni):5} B  {h(lokalni)}")
    print(f"  main == opraveny?      {'ANO' if blob == lokalni else 'NE — v main je něco jiného!'}")
    if vetev:
        chyba = subprocess.run([GIT, "-C", str(REPO), "show", f"origin/forge/task-{vetev}:{cesta}"],
                               capture_output=True, shell=True).stdout
        print(f"  větev PR == main?      {'ANO' if blob == chyba else 'NE'}")

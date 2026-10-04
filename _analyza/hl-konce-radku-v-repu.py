#!/usr/bin/env python
"""Které trackované soubory mají v pracovním stromě CRLF (a jak je má blob).

PROČ TO EXISTUJE — naměřeno 1. 10. 2026 (před commitem fáze A + D1):
`core.autocrlf=true` a **žádný `.gitattributes`** znamenají, že se konce řádků
rozhodují implicitně. `git status` pak u LF souborů hlásí
`LF will be replaced by CRLF the next time Git touches it` — což je informativní,
ale **nedá se z něj poznat, jestli soubor nebude při dalším checkoutu jiný**.
Tenhle skript to porovná bajt po bajtu: pracovní strom vs. blob v HEAD.

Použití:
    python _analyza\\hl-konce-radku-v-repu.py <repo>
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

git = pathlib.Path(__file__).resolve().parents[1] / "orchestra" / "tools" / "git.cmd"
REPO = pathlib.Path(sys.argv[1]).resolve() if len(sys.argv) > 1 else pathlib.Path.cwd()


def g(*args: str) -> str:
    r = subprocess.run([str(git), *args], cwd=REPO, capture_output=True, text=True,
                       errors="replace")
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: git {' '.join(args)} → {r.stderr.strip()}")
    return r.stdout


soubory = [s for s in g("ls-files").splitlines() if s.strip()]
print(f"repo: {REPO}")
print(f"trackovaných souborů: {len(soubory)}")

strom_crlf = strom_lf = 0
nesouhlas = []
for s in soubory:
    cesta = REPO / s
    if not cesta.is_file():
        continue
    b = cesta.read_bytes()
    ma_crlf = b"\r\n" in b
    blob = subprocess.run([str(git), "cat-file", "blob", f"HEAD:{s}"], cwd=REPO,
                          capture_output=True).stdout
    blob_crlf = b"\r\n" in blob
    if ma_crlf:
        strom_crlf += 1
    else:
        strom_lf += 1
    # NESOUHLAS = soubor se při dalším checkoutu změní (jádro pasti s autocrlf)
    if ma_crlf != blob_crlf:
        nesouhlas.append((s, "strom=CRLF blob=LF" if ma_crlf else "strom=LF blob=CRLF"))

print(f"  pracovní strom: CRLF={strom_crlf}, LF={strom_lf}")
print(f"  NESOUHLAS strom vs. blob v HEAD: {len(nesouhlas)}")
for s, popis in nesouhlas:
    print(f"    - {s}: {popis}")
if not nesouhlas:
    print("  → ŽÁDNÝ soubor se při dalším checkoutu nezmění (konce řádků sedí).")
sys.exit(1 if nesouhlas else 0)

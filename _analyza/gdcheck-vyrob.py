"""Vytáhne soubory z PR větví (bajt po bajtu) do zkušebního projektu.

Proč přes Python a `shell=True`: `git show > soubor` v PowerShellu zapíše
UTF-16LE (past ze skillu dsh-prostredi §5b) — a pak se „nenačte" z jiného
důvodu, než se měří. Tady se zapisují BAJTY z blobu.
"""
import hashlib
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
REPO = WS / "games" / "uo-shadows"
GIT = str(WS / "orchestra" / "tools" / "git.cmd")
DST = WS / "_analyza" / "gdcheck"
DST.mkdir(parents=True, exist_ok=True)

# (ref, cesta v repu, kam zapsat)
SOUBORY = [
    ("origin/forge/task-139", "scripts/save.gd", "save.gd"),
    ("origin/forge/task-140", "scripts/hud.gd", "hud.gd"),
    # kontrolní vzorek: soubor, který v repu JE a je součástí main
    ("origin/main", "scripts/skills.gd", "skills_main.gd"),
    # už sloučená granule sim.mining (#30) — ověření, že její cesta ke službám
    # v projektu neexistuje (project.godot nemá žádný autoload)
    ("origin/main", "scripts/mining.gd", "mining.gd"),
]

for ref, cesta, cil in SOUBORY:
    p = subprocess.run(
        [GIT, "-C", str(REPO), "show", f"{ref}:{cesta}"],
        capture_output=True, shell=True,
    )
    if p.returncode != 0:
        print(f"CHYBA: {ref}:{cesta} → {p.stderr.decode('utf-8', 'replace')[:200]}")
        sys.exit(1)
    bajty = p.stdout
    (DST / cil).write_bytes(bajty)
    print(f"{cil:16} {len(bajty):6} B  sha256={hashlib.sha256(bajty).hexdigest()[:16]}  ({ref})")
    print(f"                 začátek: {bajty[:40]!r}")
    print(f"                 BOM={bajty[:3] == b'\xef\xbb\xbf'}  CRLF={bajty.count(b'\r\n')}")

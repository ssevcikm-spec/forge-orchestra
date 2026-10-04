"""Doplní do worktree soubory, které přidávají PR větve (.uid) — bajt po bajtu.

`.uid` soubory se nekopírují z disku (v pracovním stromu nejsou), ale z blobů
větví; `git show` do PowerShellu by zapsal UTF-16LE (past §5b skillu).
"""
import subprocess
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
REPO = WS / "games" / "uo-shadows"
GIT = str(WS / "orchestra" / "tools" / "git.cmd")
SCRATCH = WS / "_analyza" / "merge-scratch"

for ref, cesta in [
    ("origin/forge/task-139", "scripts/save.gd.uid"),
    ("origin/forge/task-140", "scripts/hud.gd.uid"),
]:
    p = subprocess.run([GIT, "-C", str(REPO), "show", f"{ref}:{cesta}"], capture_output=True, shell=True)
    if p.returncode != 0:
        print(f"CHYBA: {ref}:{cesta} → {p.stderr.decode('utf-8', 'replace')[:200]}")
        sys.exit(1)
    cil = SCRATCH / cesta
    cil.parent.mkdir(parents=True, exist_ok=True)
    cil.write_bytes(p.stdout)
    print(f"{cesta:26} {len(p.stdout):4} B  obsah={p.stdout.decode().strip()!r}  (z {ref})")

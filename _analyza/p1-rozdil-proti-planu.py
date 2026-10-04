"""Rozdil proti planu: 177 (namereno) vs 176 (tvrdi plan) a 118 vs 117.

PROC: cislo, ktere se neshoduje, se nesmi "srovnat" přepsáním — musi se
VYSVETLIT. Tenhle skript vypise kandidaty na rozdil: soubory v `_analyza\\`,
ktere v sobe maji `Local-Deepseek` a maji suffix KODU, a u kazdeho rekne,
jestli ho plan mohl pocitat (existoval v 20:0x) nebo vznikl pozdeji.

Vystup: seznam s casem zmeny.
"""
from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
ANALYZA = WS / "_analyza"
KOD = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}
SKIP = {"__pycache__", "_archiv"}
# plan meril 4. 10. 2026 20:0x UTC
MEZ_UTC = datetime(2026, 10, 4, 20, 30)


def main() -> int:
    nalezy = []
    for p in ANALYZA.rglob("*"):
        if any(d in p.parts for d in SKIP):
            continue
        if not p.is_file() or p.suffix.lower() not in KOD:
            continue
        if p.stat().st_size > 3_000_000:
            continue
        try:
            t = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if "Local-Deepseek" in t:
            mtime = datetime.fromtimestamp(p.stat().st_mtime)
            nalezy.append((p.name, mtime))

    nalezy.sort(key=lambda x: x[1])
    nove = [n for n in nalezy if n[1] > MEZ_UTC]
    print(f"KOD souboru v _analyza/ s 'Local-Deepseek': {len(nalezy)}")
    print(f"z toho zmenenych PO 4. 10. 2026 20:30 (plan meril 20:0x): {len(nove)}")
    print()
    print("--- vsechny, od nejnovejsiho ---")
    for jmeno, mt in reversed(nalezy[-12:]):
        print(f"  {mt:%Y-%m-%d %H:%M}  {jmeno}")
    print()
    print("--- jen ty nove/zmenene po mereni planu ---")
    for jmeno, mt in nove:
        print(f"  {mt:%Y-%m-%d %H:%M}  {jmeno}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

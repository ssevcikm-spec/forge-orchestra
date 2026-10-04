"""P8m — kontrola: pouziva soubor derivovanou promennou, kterou NEMA definovanou?

PROC: opravy se delaly po castech (P8, P8b..P8l) a kazda cast mohla nechat
pouziti bez definice. `PARENT` v `kontrola-driftu.mjs` je presne ten pripad:
nahrada `const ROOT = ...` se neprovedla, ale jinde se `PARENT` uz pouziva.

Tohle je staticka kontrola, ktera se ptá na DEFINICI vs. POUZITI — tedy na to,
co `ast.parse` ani `node --check` neodhali (syntaxe je v poradku, jmeno chybi).

Vystup: seznam (soubor, promenna, definovana?).
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(r"E:\Workspaces\forge-orchestra")
HRA = Path(r"E:\Workspaces\uo-shadows")

# promenne, ktere zavedly opravy P8*
PROMENNE = ["PARENT", "_PARENT", "_REPO", "REPO", "STANICE", "_STANICE",
            "HRA", "_HRA", "KOREN_HER", "HRA_JMENO", "_HRA_JMENO"]
SKIP = {".git", "node_modules", ".godot", "__pycache__", ".wrangler",
        "_archiv", "zaloha-p8", "zaloha-p8b", "zaloha-p8d", "zaloha-p8l"}
KOD = {".py", ".mjs", ".js"}


def zkontroluj(p: Path) -> list[str]:
    t = p.read_text(encoding="utf-8", errors="replace")
    vady = []
    for jm in PROMENNE:
        # pouziti: jmeno jako samostatny token
        pouziti = len(re.findall(rf"(?<![\w.]){re.escape(jm)}(?![\w])", t))
        if pouziti == 0:
            continue
        if p.suffix == ".py":
            definice = len(re.findall(
                rf"(?m)^\s*{re.escape(jm)}\s*(?::[^=]+)?=", t))
        else:
            definice = len(re.findall(
                rf"(?:const|let|var)\s+{re.escape(jm)}\s*=", t))
        if definice == 0:
            vady.append(f"{jm} ({pouziti}x pouzita, 0x definovana)")
    return vady


def main() -> int:
    nalezy = []
    for zaklad in (REPO, HRA):
        for p in sorted(zaklad.rglob("*")):
            if any(d in p.parts for d in SKIP):
                continue
            if not p.is_file() or p.suffix.lower() not in KOD:
                continue
            vady = zkontroluj(p)
            if vady:
                nalezy.append((str(p.relative_to(zaklad)), vady))
    if not nalezy:
        print("OK — kazda pouzita derivovana promenna je i definovana.")
        return 0
    print(f"SOUBORU s pouzitim bez definice: {len(nalezy)}")
    for rel, vady in nalezy:
        print(f"\n  {rel}")
        for v in vady:
            print(f"    - {v}")
    return 1


if __name__ == "__main__":
    sys.exit(main())

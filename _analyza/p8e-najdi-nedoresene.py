"""P8e — Najdi VSECHNY zbyle cesty v zivych nastrojich, ktere po presunu miri mimo.

PROC: P8b–P8d opravovaly po jednom typu vady a po kazde oprave se nasla dalsi
(`WS / "orchestra"`, pak `HRA` vs `_HRA`). To je drahe a nekonci to. Tenhle
skript proto projde vsechny zive nastroje a vypise KAZDE misto, kde zbyva
konstrukce odkazujici na stary tvar — deterministicky, textove.

Hledane vzory (kazdy je po presunu vada):
  WS / "orchestra"        orchestra JE root repa
  WS / "games"            hra je sourozenec
  '_STANICE] / '           a podobne skladani
  HRA /                   promenna, ktera v hlavicce je jako `_HRA`
  'orchestra'             holé jmeno slozky v ceste
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(r"E:\Workspaces\forge-orchestra\_analyza")

PATTERNY = [
    ("WS/orchestra", re.compile(r'WS\s*/\s*"orchestra"')),
    ("WS/games", re.compile(r'WS\s*/\s*"games"')),
    ("HRA(promenna)", re.compile(r"(?<![_\w])HRA\b")),
    ("_STANICE?", re.compile(r"_STANICE\?")),
    ("orchestra-v-ceste", re.compile(r'["\']orchestra[\\/]')),
    ("games-v-ceste", re.compile(r'["\']games[\\/]')),
]


def main(argv: list[str]) -> int:
    zive = sys.argv[1:] if len(sys.argv) > 1 else None
    nalezy: dict[str, list[tuple[int, str, str]]] = {}
    for p in sorted(ANALYZA.glob("*")):
        if not p.is_file() or p.suffix.lower() not in (".py", ".mjs", ".js"):
            continue
        if p.name.startswith("p8") or "zaloha" in p.name:
            continue
        t = p.read_text(encoding="utf-8")
        if "_REPO = _pl.Path" not in t and "_STANICE" not in t:
            continue
        for jmeno, vzor in PATTERNY:
            for m in vzor.finditer(t):
                radek = t[:m.start()].count("\n") + 1
                obsah = t.splitlines()[radek - 1].strip()[:95]
                nalezy.setdefault(p.name, []).append((radek, jmeno, obsah))
    if not nalezy:
        print("ZADNE ZBYTKY — vsechny zive nastroje odkazuji na novy tvar.")
        return 0
    print(f"SOUBORU se zbytkem: {len(nalezy)}")
    for f, hity in sorted(nalezy.items()):
        print(f"\n{f}")
        for radek, jmeno, obsah in hity[:6]:
            print(f"  {radek:4} [{jmeno}] {obsah}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

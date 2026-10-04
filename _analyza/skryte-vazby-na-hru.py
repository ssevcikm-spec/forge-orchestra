# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Ktere nastroje orchestra sahaji na hru - a ZAPISUJI do ni?

VERZE 2 (po tom, co verze 1 namerala '0 zapisu' a to bylo slepota):
  v1 hledal klicova slova ZAPIS na STEJNEM radku jako cesta k hre.
  `sync-sablona-hra.py` ma 'games/uo-shadows' na radku 20 a
  'shutil.copyfile(zdroj, cil)' na radku 45 - dva rádky od sebe.
  V1 tedy ohlásil 'zapisu nikdo', coz je presne 'nula neni uspech'.

  v2 meri jine, ale spravnejsi: soubor, ktery ZMINI hru a ZAPISUJE nekde.
  To neni jiste 'zapis do hry' - proto se vypise jako kandidati k rucni
  kontrole, ne jako zmereni.

Pozor na past: 'grep' tool preskakuje skryte slozky, proto Python walk.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

ORCH = Path(_REPO)

ZMINA = re.compile(r"games[\\/]|uo-shadows", re.I)
ZAPIS = re.compile(
    r"(copyfile|copytree|copy2|shutil\.(copy|move)|mkdir|makedirs|write_text|write_bytes|"
    r"open\s*\([^)]*['\"][wa]|rmtree|unlink|Copy-Item)", re.I)

SKIP = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__", ".test", ".state"}


def main() -> int:
    zmineni: list[tuple[str, int]] = []          # (soubor, radku) - kde se zmini hra
    kandidati: dict[str, list[str]] = {}        # soubor -> priklady zapisu
    for p in ORCH.rglob("*"):
        if any(d in p.parts for d in SKIP):
            continue
        if not p.is_file() or p.suffix.lower() not in {".mjs", ".py", ".ps1", ".cmd", ".yml", ".json"}:
            continue
        try:
            radky = p.read_text(encoding="utf-8", errors="replace").splitlines()
        except OSError:
            continue
        mine = [i for i, r in enumerate(radky, 1) if ZMINA.search(r)]
        if not mine:
            continue
        rel = str(p.relative_to(ORCH))
        zmineni.extend((rel, i) for i in mine)
        zapis = [(i, r.strip()[:100]) for i, r in enumerate(radky, 1) if ZAPIS.search(r)]
        if zapis:
            kandidati[rel] = [f":{i}: {r}" for i, r in zapis[:3]]

    if not zmineni:
        print("NIC NENALEZENO - to neni uspech, ale vada skenu. Postup:")
        print(f"  prohledano: {ORCH} (Python walk, preskoceno {sorted(SKIP)})")
        return 2

    print(f"Zmini hru: {len(zmineni)} radku v {len({n[0] for n in zmineni})} souborech")
    print(f"Z nich ZAPISUJE nekde: {len(kandidati)} souboru (kandidati, ne potvrzeno)")
    print()
    for s, priklady in sorted(kandidati.items()):
        print(f"  {s}")
        for r in priklady:
            print(f"      {r}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
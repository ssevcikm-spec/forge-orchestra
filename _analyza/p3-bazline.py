# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""P3 — BAZSLINE PRED PRESUNEM: pocet souboru a velikost obou stromu.

PROC: cisla v planu §10.4 P3 jsou ZASTARALA (plan tvrdil orchestra ~4 692 /
~1,07 GB, hra 1 577 / 15,5 MB; validace 20:0x namerila 5 447 / 1 176,4 MB a
1 787 / 16,1 MB). Bez cerstveho bazline se po presunu neda rict, co se
rozbilo — a "po = pred" je jedine meritelne "Hotovo znamena" kroku P5.

Vystup: JSON, aby se dal porovnat s merenim PO presunu programem.
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(_STANICE)
STROMY = {
    "orchestra": WS,
    "hra": HRA,
    "godot": WS / "tools" / "godot",
}
VYSTUP = WS / "_analyza" / "p3-bazline.json"


def zmer(p: Path) -> dict:
    if not p.exists():
        return {"existuje": False}
    soubory = 0
    bajty = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                soubory += 1
                bajty += f.stat().st_size
        except OSError:
            continue
    return {"existuje": True, "souboru": soubory,
            "bajtu": bajty, "MB": round(bajty / 1024 / 1024, 1)}


def main() -> int:
    vysledek = {}
    for jmeno, cesta in STROMY.items():
        m = zmer(cesta)
        vysledek[jmeno] = {"cesta": str(cesta), **m}
        if m["existuje"]:
            print(f"{jmeno:12} {m['souboru']:6} souboru  {m['MB']:9.1f} MB   {cesta}")
        else:
            print(f"{jmeno:12} NEEXISTUJE   {cesta}")

    # strom orchestra BEZ godotu (to je to, co se ma presunout jako repo)
    if vysledek["orchestra"].get("existuje") and vysledek["godot"].get("existuje"):
        vysledek["orchestra_bez_godotu"] = {
            "souboru": vysledek["orchestra"]["souboru"] - vysledek["godot"]["souboru"],
            "MB": round(vysledek["orchestra"]["MB"] - vysledek["godot"]["MB"], 1),
        }
        print(f"\norchestra bez godotu: "
              f"{vysledek['orchestra_bez_godotu']['souboru']} souboru, "
              f"{vysledek['orchestra_bez_godotu']['MB']} MB")

    VYSTUP.write_text(json.dumps(vysledek, ensure_ascii=False, indent=2) + "\n",
                      encoding="utf-8", newline="\n")
    print(f"\nzapsano: {VYSTUP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

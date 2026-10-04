"""P5 — PRESUN NA E: (kopie -> overeni -> smazani zdroje).

PROC NE `robocopy /MOVE`: /MOVE maze PRUBEZNE, takze selhani uprostred necha
strom na OBOU mistech a neda se rict, co je kde. Takhle je zdroj nedotceny,
dokud cil nesedi na POCET SOUBORU i na BAJTY — dva nezavisle pohledy.

PROC PYTHON A NE POWERSELL: `shutil.copytree` vi, co prenesl, a pocita se to
týmz kodem pred i po. U robocopy se exit kody (0-7 = uspech) spatne cte.

Bezpecnostni pravidla:
  - cil musi existovat a byt PRAZDNY (jinak se neprepisuje nic)
  - zdroj se maze JEN kdyz pocet souboru I bajty sedi presne
  - kazdy krok se loguje do souboru

Pouziti: python _analyza/p5-presun.py [--jen-godot] [--bez-mazani]
"""
from __future__ import annotations

import shutil
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
LOG = WS / "_analyza" / "p5-presun-log.txt"

KROKY = [
    ("godot", WS / "orchestra" / "tools" / "godot", Path(r"E:\Tools\godot")),
    ("orchestra", WS / "orchestra", Path(r"E:\Workspaces\forge-orchestra")),
    ("hra", WS / "games" / "uo-shadows", Path(r"E:\Workspaces\uo-shadows")),
]

radky: list[str] = []


def zapis(t: str) -> None:
    print(t)
    radky.append(t)


def zmer(p: Path) -> tuple[int, int]:
    """(pocet souboru, bajty) — pocita se týmž kodem pred i po."""
    if not p.exists():
        return (-1, -1)
    souboru = 0
    bajtu = 0
    for f in p.rglob("*"):
        try:
            if f.is_file():
                souboru += 1
                bajtu += f.stat().st_size
        except OSError:
            continue
    return (souboru, bajtu)


def presun(jmeno: str, zdroj: Path, cil: Path, mazat: bool) -> bool:
    zapis(f"=== {jmeno} ===")
    zapis(f"  zdroj: {zdroj}")
    zapis(f"  cil:   {cil}")

    if not zdroj.exists():
        zapis("  CHYBA: zdroj neexistuje")
        return False
    if cil.exists():
        obsah = list(cil.iterdir())
        if obsah:
            zapis(f"  CHYBA: cil neni prazdny ({len(obsah)} polozek)")
            return False
    else:
        cil.mkdir(parents=True, exist_ok=True)
        zapis("  (cil vytvoren)")

    pred = zmer(zdroj)
    zapis(f"  PRED: {pred[0]} souboru, {pred[1] / 1024 / 1024:.1f} MB")

    shutil.copytree(zdroj, cil, dirs_exist_ok=True, symlinks=False)

    po = zmer(cil)
    zapis(f"  PO:   {po[0]} souboru, {po[1] / 1024 / 1024:.1f} MB")

    if po[0] != pred[0]:
        zapis(f"  CHYBA: pocet souboru nesedi ({pred[0]} -> {po[0]}) — ZDROJ SE NEMAZE")
        return False
    if po[1] != pred[1]:
        zapis(f"  CHYBA: bajty nesedi ({pred[1]} -> {po[1]}) — ZDROJ SE NEMAZE")
        return False
    zapis("  OVERENO: pocet souboru I bajty sedi")

    if not mazat:
        zapis("  (--bez-mazani: zdroj zustava)")
        return True

    shutil.rmtree(zdroj)
    if zdroj.exists():
        zapis(f"  CHYBA: zdroj se nepodarilo smazat: {zdroj}")
        return False
    zapis(f"  zdroj smazan: {zdroj}")
    zapis("")
    return True


def main(argv: list[str]) -> int:
    jen_godot = "--jen-godot" in argv
    mazat = "--bez-mazani" not in argv
    ok = True
    for jmeno, zdroj, cil in KROKY:
        if not presun(jmeno, zdroj, cil, mazat):
            ok = False
            break
        if jen_godot:
            break
    zapis("")
    zapis("VYSLEDEK: " + ("HOTOVO" if ok else "SELHALO — viz vys"))
    LOG.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

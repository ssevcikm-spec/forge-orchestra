#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""DŮKAZ, že opravená sekce D umí SELHAT (Úkol C1).

Zadání žádá: „je doloženo, co nástroj vypíše, když endpoint neexistuje
(nesmí to být ‚žádná úloha')". Původní nástroj nad neexistujícím `/tasks`
vypsal u každé granule „(žádná úloha)" a skončil `exit 0` — tedy zelená nad
ničím. Tenhle skript to ověří u OPRAVENÉHO nástroje:

  1. zdravý běh                       -> musí dát exit 0
  2. `/queue` přejmenované na neexistující cestu -> musí dát nenulový exit
     a výslovně říct, že seznam úloh NENÍ
  3. soubor se vrátí bajt na bajt

Použití: python _analyza\\c1-dukaz-selhani.py
"""

import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
CIL = ANALYZA / "a3-kontrola.mjs"
PODVRH = "/queue-neexistuje-tahle-cesta"


def spust() -> tuple:
    r = subprocess.run(["node", str(CIL)], capture_output=True, timeout=180)
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    return r.returncode, v


def hlavni() -> int:
    puvodni = CIL.read_text(encoding="utf-8")

    print("=" * 74)
    print("1) ZDRAVÝ BĚH (endpoint existuje)")
    print("=" * 74)
    kod, v = spust()
    for radek in v.splitlines():
        if "world.nodes" in radek or "entity.player.api" in radek or "queue vrátil" in radek:
            print("   " + radek.strip())
    print("   exit=%d  %s" % (kod, "OK" if kod == 0 else "!! očekávám 0"))
    if kod != 0:
        print("   → zdravý běh neskončil 0; další měření by nic nedokázala")
        return 2

    print()
    print("=" * 74)
    print("2) PODVRH: `/queue` nahrazeno za neexistující cestu")
    print("=" * 74)
    # Nahraď JEN volání v sekci D (nikoli komentář s vysvětlením).
    vada = puvodni.replace("const rq = await cond('/queue');",
                           "const rq = await cond('%s');" % PODVRH, 1)
    if vada == puvodni:
        print("   CHYBA: podvrh se neprovedl (text nenalezen)")
        return 2
    CIL.write_bytes(vada.encode("utf-8"))
    z5 = CIL.read_text(encoding="utf-8")
    assert PODVRH in z5, "podvrh se do souboru nezapsal"
    print("   ověřeno na disku: volání míří na %s" % PODVRH)

    try:
        kod2, v2 = spust()
        for radek in v2.splitlines():
            if ("queue" in radek.lower() or "CHYBA" in radek
                    or "world.nodes" in radek or "entity.player.api" in radek
                    or "NALEZENO" in radek or "V POŘÁDKU" in radek):
                print("   " + radek.strip())
        print("   exit=%d" % kod2)
    finally:
        CIL.write_bytes(puvodni.encode("utf-8"))
        assert CIL.read_text(encoding="utf-8") == puvodni, "návrat se nezdařil"
        print("   soubor vrácen bajt na bajt")

    print()
    print("=" * 74)
    uspech = kod2 != 0
    print("VÝSLEDEK: %s" % ("CHYCENO — nástroj nad neexistujícím endpointem"
                            " hlásí chybu a končí nenulově" if uspech
                            else "SLEPÉ — nástroj prošel i s neexistujícím endpointem!"))
    print("=" * 74)
    return 0 if uspech else 1


if __name__ == "__main__":
    sys.exit(hlavni())

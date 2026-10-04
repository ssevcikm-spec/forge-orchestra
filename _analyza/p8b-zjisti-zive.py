"""ZIVE nastroje v `_analyza\\` — ODVOZENE z korenoveho AGENTS.md, ne z dojmu.

PROC: D5 rozhodlo "archivovat 99, opravit 18 zivych". Rozhodnuti `opravit`
vs. `archivovat` nesmi stat na mem seznamu — musi stat na tom, co dokument
SKUTECNE spousti. Kandidati v poradi sily dukazu:

  A) `AGENTS.md` (root, projektova pravidla, vzdy nacitana) uvadi soubor
     v sekci "Kam pro co" jako ZIVY NASTROJ -> silny dukaz.
  B) `AGENTS.md` obsahuje spustitelny prikaz `python _analyza\\X.py` nebo
     `node _analyza\\X.mjs` -> silny dukaz (nastroj se ma spoustet).
  C) `_analyza\\_registr-bran.json` zna branu timto prikazem -> stredni dukaz.

Vse ostatni = kandidat na ARCHIVACI (jednorazovka z 2. 10.).

Vystup: JSON + souhrn. JSON je vstup pro p1-inventura-cest.py (at se seznam
neopisuje rucne dvakrat).
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(r"C:\Users\Ssevc\Local-Deepseek")
AGENTS = WS / "AGENTS.md"
REGISTR = WS / "_analyza" / "_registr-bran.json"
VYSTUP = WS / "_analyza" / "p8b-zive.json"

# prikaz v dokumentu: python _analyza\x.py / node _analyza\x.mjs / `_analyza\x.py`
PRIKAZ = re.compile(r"(?:python|node|py)\s+_analyza[\\/](?P<jmeno>[A-Za-z0-9_.\-]+\.(?:py|mjs))", re.I)
ZMINKA = re.compile(r"`_analyza[\\/](?P<jmeno>[A-Za-z0-9_.\-]+\.(?:py|mjs|json))`")


def main() -> int:
    if not AGENTS.exists():
        print(f"CHYBI: {AGENTS} — bez nej se seznam zivych neda merit")
        return 2
    text = AGENTS.read_text(encoding="utf-8", errors="replace")

    spoustene = {m.group("jmeno") for m in PRIKAZ.finditer(text)}
    zminene = {m.group("jmeno") for m in ZMINKA.finditer(text)}

    z_registru: set[str] = set()
    if REGISTR.exists():
        d = json.loads(REGISTR.read_text(encoding="utf-8", errors="replace"))
        for b in d.get("brany", {}).values():
            m = PRIKAZ.search(str(b.get("prikaz", "")))
            if m:
                z_registru.add(m.group("jmeno"))

    zive = sorted(spoustene | zminene | z_registru)
    na_disku = {p.name for p in (WS / "_analyza").iterdir() if p.is_file()}

    VYSTUP.write_text(json.dumps({
        "zive": zive,
        "jen_spoustene": sorted(spoustene),
        "jen_zminene": sorted(zminene),
        "z_registru_bran": sorted(z_registru),
        "zdroj": "AGENTS.md + _registr-bran.json",
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")

    print(f"spoustene prikazem v AGENTS.md: {len(spoustene)}")
    print(f"zminene v AGENTS.md:            {len(zminene)}")
    print(f"v _registr-bran.json:           {len(z_registru)}")
    print(f"ZIVE celkem:                    {len(zive)}")
    print(f"  z toho na disku:              {len([z for z in zive if z in na_disku])}")
    print(f"  z toho NENI na disku:         {len([z for z in zive if z not in na_disku])}")
    print()
    for z in zive:
        kde = []
        if z in spoustene:
            kde.append("AGENTS:spousteny")
        if z in zminene:
            kde.append("AGENTS:zmineny")
        if z in z_registru:
            kde.append("registr")
        if z not in na_disku:
            kde.append("!!! NENI NA DISKU")
        print(f"  {z:36} {', '.join(kde)}")
    print(f"\nzapsano: {VYSTUP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

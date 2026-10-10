# -*- coding: utf-8 -*-
r"""P33 — SONDA: KTERÝ SOUBOR ROZEŠEL OTISK VSTUPŮ INVENTÁŘE?

PROČ: `hl-rizika-jazyka.py` umí říct jen **že** je inventář zastaralý a kolik
souborů přibylo (`1192 → 1193`) — ne **který** soubor to způsobil. Naměřeno
9. 10. 2026 v P33: stal se to **vlastní diagnostický skript** session
(`_analyza/_p33-probe4.py`), napsaný až PO přegenerování inventáře; `g3`
i `validate-all` pak hlásily pojmenovaný stav „zastaralý inventář" a vypadalo
to jako vada bran. Dohledat viníka trvalo čtvrt hodiny — tenhle nástroj to
řekne na jeden běh.

⚠ NENÍ to brána: nic netvrdí o stavu projektu. Je to **diagnostika** — pouští
skener znovu (do jiného souboru) a porovná seznamy vstupů. Proto je v `PRESKIP`
dávky dokladů (`p20-d-doklady.py`).

Použití: python _analyza\p33-sonda-inventar.py
"""
import json
import os
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ZIVY = WS / "_analyza" / "_inventar.json"
DIAG = WS / "_analyza" / "_p33-sonda-inventar-diag.json"


def nacti_mnozinu(cesta):
    d = json.loads(cesta.read_text(encoding="utf-8"))
    otisk = d.get("otisk_vstupu") or {}
    out = {}
    for rep in otisk.get("repozitare") or []:
        for f in rep.get("soubory") or []:
            out[(rep["repo"], f["cesta"])] = f.get("bajtu")
    return out, otisk


def main():
    if not ZIVY.is_file():
        print("CHYBA: %s není — není s čím porovnávat" % ZIVY.name)
        return 2
    r = subprocess.run([sys.executable, str(WS / "_analyza" / "hl-neanglicky-v-kodu.py"),
                        "--json", str(DIAG)], cwd=str(WS), env=dict(os.environ), capture_output=True)
    if r.returncode != 0 or not DIAG.is_file():
        print("CHYBA: skener neproběhl (exit %d): %s"
              % (r.returncode, (r.stdout or b"")[-300:].decode("utf-8", "replace")))
        return 2
    stary, ot_stary = nacti_mnozinu(ZIVY)
    novy, ot_novy = nacti_mnozinu(DIAG)
    DIAG.unlink(missing_ok=True)
    print("=" * 78)
    print("P33 — CO ROZEŠLO OTISK VSTUPŮ INVENTÁŘE (živý vs. přepočet TEĎ)")
    print("=" * 78)
    print("  souborů: v inventáři %d, teď %d" % (len(stary), len(novy)))
    print("  otisk:   v inventáři %s, teď %s"
          % (str(ot_stary.get("sha256"))[:16], str(ot_novy.get("sha256"))[:16]))
    nove = sorted(set(novy) - set(stary))
    zmizele = sorted(set(stary) - set(novy))
    zmenene = sorted(k for k in set(stary) & set(novy) if stary[k] != novy[k])
    print("\n  NOVÉ SOUBORY (%d) — nejčastější viník:" % len(nove))
    for k in nove:
        print("    + %s · %s (%s B)" % (k[0], k[1], novy[k]))
    print("\n  ZMIZELÉ SOUBORY (%d):" % len(zmizele))
    for k in zmizele:
        print("    - %s · %s" % k)
    print("\n  ZMĚNĚNÁ VELIKOST (%d) — obsah se mohl změnit i beze změny velikosti:" % len(zmenene))
    for k in zmenene:
        print("    ~ %s · %s (%s → %s B)" % (k[0], k[1], stary[k], novy[k]))
    print("\n  Náprava:  python _analyza\\hl-neanglicky-v-kodu.py --json _analyza\\_inventar.json")
    return 0 if (not nove and not zmizele and not zmenene) else 1


if __name__ == "__main__":
    sys.exit(main())

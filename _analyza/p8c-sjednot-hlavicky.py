"""P8c — Sjednoceni hlavicky v zivych nastrojich `_analyza/`.

NAMERENA VADA: `p8b-oprava-analyza.py` vlozil do opravenych nastroju hlavicku
s `_STANICE = C:\\Users\\Ssevc\\Local-Deepseek` (koren stanice). Tim se ale
`WS` u 26 nastroju prepojilo z "korene, kde jsou projektove dokumenty" na
"koren stanice" — a protoze se `HANDOFF.md`, `KRONIKA-PROJEKTU.md` a `_analyza/`
presunuly DO REPA, kazaly by ty nastroje do JINEHO stromu, nez maji.

  `WS` v tech nastrojich znamenalo "koren s projektovymi dokumenty"
  → po presunu je to REPO, ne STANICE.

Postup: `_STANICE` se predefinuje na `_REPO` (dokumenty projektu jsou v repu)
a soubory, ktere SKUTECNE potrebuji dokumenty, jez zustaly stanici
(MOZNOSTI-AGENTA.md, OTEVRENA-TEMATA.md, README.md), dostanou navic
`_STANICE_DOKUMENTY` s absolutni cestou.

Po zmene se kazdy nastroj SPUSTI a vysledek se zapise — co nesmi, je tiche
prepojeni na jiný strom.
"""
from __future__ import annotations

import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(r"E:\Workspaces\forge-orchestra\_analyza")

# dokumenty, ktere zustaly stanici a jsou v tech nastrojich skutecne potreba
STANICNI_DOKUMENTY = ("MOZNOSTI-AGENTA.md", "OTEVRENA-TEMATA.md",
                      "PREDAVANI-SESSION.md", "README.md")

VYSTUP = ANALYZA / "P8C-BRANY-PO-OPRAVE.md"

# nastroje, ktere se po oprave maji dat spustit (zive brany) — jen ty, ktere
# nemaji externi zavislost (GitHub, sit)
BRANY = [
    "zadani-kontrola.py",
    "kronika-kontrola.py",
    "handoff-kontrola-uplnost.py",
    "n8-zastarala-analyza.py",
    "n8-mutace.py",
    "a3-over.py",
    "a3-mutace.py",
    "n1-over-inventar.py",
    "ag-over-cisla.py",
    "ag-mutace.py",
    "b5-over-tvrzeni.py",
    "hl2-kontrola.py",
    "hl2-mutace-kontrola.py",
    "hl2-kostra-test.py",
    "sken-vazeb.py",
    "skryte-vazby-na-hru.py",
]


def main() -> int:
    zmenene = []
    for p in sorted(ANALYZA.glob("*.py")):
        t = p.read_text(encoding="utf-8")
        if "_STANICE = _pl.Path" not in t:
            continue
        novy = t
        # 1) predefinuj _STANICE na REPO (projektove dokumenty jsou v repu)
        novy = novy.replace(
            '_STANICE = _pl.Path(r"C:\\Users\\Ssevc\\Local-Deepseek")',
            "_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)")
        novy = novy.replace(
            '#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)',
            '#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)')
        # 2) soubory potrebujici skutecne stanicni dokumenty dostanou druhou promennou
        if any(d in novy for d in STANICNI_DOKUMENTY):
            if "_STANICE_DOKUMENTY" not in novy:
                novy = novy.replace(
                    "_HRA = _REPO.parent / \"uo-shadows\"",
                    "_HRA = _REPO.parent / \"uo-shadows\"\n"
                    "# Dokumenty, ktere zustaly STANICI (D6): na ty se saha absolutne.\n"
                    "_STANICE_DOKUMENTY = _pl.Path(r\"C:\\Users\\Ssevc\\Local-Deepseek\")")
        if novy != t:
            p.write_text(novy, encoding="utf-8", newline="")
            zmenene.append(p.name)

    radky = ["# P8c — BRÁNY SPUŠTĚNÉ Z NOVÉHO MÍSTA", "",
             f"**Upraveno hlaviček:** {len(zmenene)}", ""]
    for z in zmenene:
        print(f"  hlavicka: {z}")

    print("\n=== spousteni bran z noveho mista ===")
    for jmeno in BRANY:
        p = ANALYZA / jmeno
        if not p.exists():
            radky.append(f"| `{jmeno}` | — | **CHYBI** |")
            continue
        r = subprocess.run([sys.executable, str(p)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace",
                           cwd=str(ANALYZA), timeout=300)
        vystup = (r.stdout or "") + (r.stderr or "")
        prvni = [l for l in vystup.splitlines() if l.strip()][:1]
        ukazka = prvni[0][:90] if prvni else "(prazdny vystup)"
        stav = "OK" if r.returncode == 0 else f"exit {r.returncode}"
        print(f"  {jmeno:32} {stav:10} {ukazka}")
        radky.append(f"| `{jmeno}` | {stav} | {ukazka} |")
        if r.returncode != 0 and "__" not in jmeno:
            # uloz detail pro ladeni
            det = ANALYZA / f"p8c-log-{jmeno}.txt"
            det.write_text(vystup[-4000:], encoding="utf-8", newline="\n")

    VYSTUP.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
    print(f"\nzapsano: {VYSTUP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

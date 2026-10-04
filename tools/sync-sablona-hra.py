"""Dosynchronizuje soubory mezi šablonou orchestra a klonem hry – SPRÁVNÝM směrem.

Drift šel na obě strany, takže „zkopíruj šablonu do hry" nestačí:
  - `CONVENTIONS.md`  hra > šablona (hra má §1g a zpřesnění z dnešní session)
  - `worker.mjs`      šablona > hra (šablona má o ~70 řádků víc)
  - `agent.yml`       obojí – šablona měla plnější bránu, hra kvótní guard

Tenhle skript řeší jen první dva (jednosměrné) a je idempotentní.
`agent.yml` se sjednocuje zvlášť (tools/sjednot-sablonu.py), protože se do něj
zasahuje po blocích.
"""

import hashlib
import pathlib
import os
import shutil
import sys

# P8l (presun na E:, 4. 10. 2026): hra je SOUROZENEC repa (D4).
# Poradi: FORGE_HRA (env) > vychozi sourozenec `../uo-shadows`.
_REPO = pathlib.Path(__file__).resolve().parents[1]
_HRA_JMENO = os.environ.get("FORGE_HRA", "uo-shadows")
_HRA = _REPO.parent / _HRA_JMENO
REPO = _REPO
SABLONA = _REPO / "repo"
HRA = _HRA

# (relativní cesta, směr)  směr: "do_hry" = šablona → hra, "do_sablony" = hra → šablona
PRENOSY = [
    ("CONVENTIONS.md", "do_sablony"),          # hra je novější (má §1g)
    (".forge/node/worker.mjs", "do_hry"),      # šablona je novější
]


def normalizuj(cesta: pathlib.Path) -> str:
    return cesta.read_text(encoding="utf-8").replace("\r\n", "\n")


def main() -> int:
    zmeny = []
    for rel, smer in PRENOSY:
        a = SABLONA / rel
        b = HRA / rel
        if not a.exists() or not b.exists():
            print(f"  ? {rel}: chybí na jedné straně (šablona={a.exists()}, hra={b.exists()})")
            continue
        if normalizuj(a) == normalizuj(b):
            print(f"  OK   {rel} (shodné)")
            continue
        zdroj, cil = (b, a) if smer == "do_sablony" else (a, b)
        shutil.copyfile(zdroj, cil)
        zmeny.append(f"{rel} ({smer})")
        print(f"  PŘENESENO {rel}: {smer}")

    print()
    if zmeny:
        print("Změněno:", ", ".join(zmeny))
        print("Zkontroluj 'git diff' a pak spusť tools/kontrola-driftu.mjs.")
    else:
        print("Nic k přenosu.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

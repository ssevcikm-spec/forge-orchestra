"""Spustí příkaz a zapíše jeho stdout+stderr do DOKLADU (UTF-8, LF).

PROČ VZNIKL (P41, H191/H161):
  · `wrangler tail` přes PowerShell pipeline NEDODÁ data (H161) — doklad se musí
    psát PŘESMĚROVÁNÍM, ne trubkou; a `>` v PowerShellu mění kódování.
  · Doklad s PEVNÝM jménem výstupu nese jen POSLEDNÍ běh (H191) — proto si
    každé měření píše VLASTNÍ soubor a tenhle nástroj mu ho založí.
  · Projekt má ve zvyku, že si měřidlo píše výstup samo (`write_text`), ne že ho
    zachytává shell. Tohle je jedna cesta pro všechny příkazy.

Použití:
    python _analyza/p41-run-doklad.py _analyza/p41-b-mutace-vystup.txt ^
        python _analyza/tick-mutace.py

Návratový kód = návratový kód spouštěného příkazu (doklad se zapíše VŽDY,
i když příkaz spadne — jinak by chyběl právě ten zajímavý případ).
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]


def main() -> int:
    if len(sys.argv) < 3:
        print("pouziti: p41-run-doklad.py <doklad.txt> <prikaz> [args...]")
        return 2
    doklad = pathlib.Path(sys.argv[1])
    if not doklad.is_absolute():
        doklad = WS / doklad
    prikaz = sys.argv[2:]

    r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    telo = (r.stdout or "") + (r.stderr or "")
    zahlavi = (f"# doklad: {' '.join(prikaz)}\n"
               f"# exit={r.returncode}\n"
               f"# (zapsal _analyza/p41-run-doklad.py)\n")
    doklad.parent.mkdir(parents=True, exist_ok=True)
    with open(doklad, "w", encoding="utf-8", newline="\n") as f:
        f.write(zahlavi + telo)
    print(zahlavi + telo, end="")
    print(f"\n[doklad zapsan: {doklad} ({len(telo)} B)]")
    return r.returncode


if __name__ == "__main__":
    sys.exit(main())

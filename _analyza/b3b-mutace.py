"""Mutační důkaz brány `tools/test-grain-cap.py` (B3b — strop na granuli).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána měří strop i shodu obou tvarů klíče. Jenže to samo ještě neznamená, že měří
to, co si myslí — proto se do zdrojáku vrací PĚT vad a po každé se vyžaduje, aby
brána SPADLA:

  M1 `grainCapped` vždy `true` (zastavilo by i granuli bez řádku)   → B
  M2 `grainCap` vrátí i nesmysl/záporné číslo (tiše by zastavil)    → A
  M3 `grainKeyOf` skládá klíč JINAK než SQL (`_` místo `/`)          → C
  M4 filtr `ready` bez stropu (granule by se vydávala dál)           → D
  M5 `roadmapTick` dostane `null, 0` místo skutečného počítadla      → D

MUTACE SE NEPROVÁDÍ VLASTNÍM `replace()`, ale knihovnou `_mutace.mutuj`
(kotva právě 1×, text se skutečně změní, nový neobsahuje starý, soubor se VŽDY
vrátí bajt na bajt).

Test má assert i nenulový exit kód.
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from _mutace import mutuj  # noqa: E402

WS = pathlib.Path(__file__).resolve().parents[1]
CONDUCTOR = WS / "conductor" / "src" / "index.ts"
BRANA = WS / "tools" / "test-grain-cap.py"

MUTATIONS = [
    ("M1 grainCapped vzdy true",
     CONDUCTOR,
     "return cap > 0 && (runs ?? 0) >= cap;",
     "return true;"),
    ("M2 grainCap prijme i nesmysl",
     CONDUCTOR,
     "return Number.isFinite(n) && n > 0 ? n : 0;",
     "return n;"),
    ("M3 grainKeyOf sklada klíč jinak než SQL",
     CONDUCTOR,
     "return `${p.game}/${p.grain}`;",
     "return `${p.game}_${p.grain}`;"),
    ("M4 filtr ready bez stropu",
     CONDUCTOR,
     "      && !grainCapped(runs?.get(`${g.game_id}/${i.id}`), cap)\n",
     ""),
    ("M5 roadmapTick dostane null, 0",
     CONDUCTOR,
     "roadmapTick(env, retryH, grainRunsMap, cap)",
     "roadmapTick(env, retryH, null, 0)"),
]

checks = 0
errors = 0


def check(desc: str, actual, expected) -> None:
    global checks, errors
    checks += 1
    if actual == expected:
        print(f"  OK    {desc}")
    else:
        errors += 1
        print(f"  CHYBA {desc}\n        cekano: {expected!r}\n        dáno:   {actual!r}")


def run_gate() -> tuple[int, str]:
    r = subprocess.run(
        [sys.executable, str(BRANA)],
        cwd=str(WS), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    global checks, errors
    print(f"=== mutacni test brany: {BRANA.name} ===")
    for p in (CONDUCTOR, BRANA):
        if not p.is_file():
            print(f"CHYBA: chybi {p}")
            return 1

    code, out = run_gate()
    check("KONTROLA: nemutovana brana je zelena (exit 0)", code, 0)
    if code != 0:
        print("        (výstup brány:)")
        print("        " + "\n        ".join(out.strip().splitlines()[-10:]))

    for name, soubor, old, new in MUTATIONS:
        try:
            with mutuj(soubor, old, new) as m:
                code, out = run_gate()
        except ValueError as e:
            checks += 1
            errors += 1
            print(f"  CHYBA {name}: mutace se neprovedla — {e}")
            continue
        red = code != 0 and "CHYBA" in out
        check(f"{name} → brana SPADLA", red, True)
        if not red:
            print("        (výstup brány:)")
            print("        " + "\n        ".join(out.strip().splitlines()[-10:]))
        check(f"{name} → soubor vracen bajt na bajt", m.hash_po_navratu, m.hash_pred)

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())

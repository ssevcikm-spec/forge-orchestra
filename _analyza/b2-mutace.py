"""Mutační důkaz brány `tools/test-report-cooldown.py` (B2 — `/report` a cooldown).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána simuluje selhání přes `/report` a ptá se skutečného dispatch guardu. Jenže
to samo ještě neznamená, že měří to, co si myslí: kdyby porovnávala špatné místo,
zůstala by zelená i s vrácenou vadou (vada S13).

Test proto vrací do `conductor/src/index.ts` (a do `wrangler.toml`) ČTYŘI vady,
z nichž každá ruší jinou část slibu B2, a po každé vyžaduje, aby brána SPADLA.

MUTACE SE NEPROVÁDÍ VLASTNÍM `replace()`, ale knihovnou `_mutace.mutuj`
(pravidlo projektu): kotva musí být v souboru právě 1×, text se musí skutečně
změnit, nový text nesmí obsahovat starý jako podřetězec a soubor se VŽDY vrátí —
bajt na bajt (`sha256`).

CO SE MUTUJE (a co to má shodit):
  M1 `/report` nezapíše `naposledy_selhalo` (stav před B1)   → A: guard NEVYDÁ úkol
  M2 guard porovnává opačně (`<` místo `>`)                  → A/B/D
  M3 `RETRY_HOURS = 0`                                       → brána to odmítne
  M4 poslední pokus nezapíše `naposledy_selhalo`             → C: cooldown po posledním pokusu

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
WRANGLER = WS / "conductor" / "wrangler.toml"
BRANA = WS / "tools" / "test-report-cooldown.py"

MUTATIONS = [
    ("M1 /report nezapise naposledy_selhalo",
     CONDUCTOR,
     "UPDATE roadmap SET naposledy_selhalo = datetime('now') WHERE task_id=?",
     "UPDATE roadmap SET updated_at = datetime('now') WHERE task_id=?"),
    ("M2 guard porovnava opacne",
     CONDUCTOR,
     "AND rm.naposledy_selhalo > datetime('now', ?)",
     "AND rm.naposledy_selhalo < datetime('now', ?)"),
    ("M3 RETRY_HOURS = 0",
     WRANGLER,
     'RETRY_HOURS = "3"',
     'RETRY_HOURS = "0"'),
    ("M4 posledni pokus nezapise naposledy_selhalo",
     CONDUCTOR,
     "UPDATE roadmap SET status='failed', updated_at=datetime('now'),\n"
     "               naposledy_selhalo = datetime('now') WHERE task_id=?",
     "UPDATE roadmap SET status='failed', updated_at=datetime('now') WHERE task_id=?"),
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
    for p in (CONDUCTOR, WRANGLER, BRANA):
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

"""Mutační důkaz brány `tools/test-watchdog-granule.py` (B3a — watchdog na granuli).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána, která nemá jak selhat, není brána. Nová brána čte SQL i rozhodnutí
**ze zdrojáku conductora**, ale to samo ještě neznamená, že měří to, co si myslí:
kdyby porovnávala špatnou věc, zůstala by zelená i s vrácenou vadou.

Test proto vrací do `conductor/src/index.ts` (a do `wrangler.toml`) PĚT vad,
z nichž každá ruší jinou část slibu B3a, a po každé vyžaduje, aby brána SPADLA.

MUTACE SE NEPROVÁDÍ VLASTNÍM `replace()`, ale knihovnou `_mutace.mutuj`
(pravidlo projektu): kotva musí být v souboru právě 1×, text se musí skutečně
změnit, nový text nesmí obsahovat starý jako podřetězec a soubor se VŽDY vrátí —
bajt na bajt (`sha256`).

CO SE MUTUJE (a co to má shodit):
  M1 počítadlo počítá ÚKOLY místo BĚHŮ      → A: 5+3 = 8
  M2 vypuštěný časový filtr (reset)         → B: po resetu jen 1
  M3 vypuštěná značka „už ohlášeno"         → D: ohlášená granule není kandidát
  M4 `shouldEscalate` vždy `true`           → E: 2 běhy pod prahem → NEhlásit
  M5 prah ve `wrangler.toml` nad stropem    → F: prah < MAX_ATTEMPTS

Test má assert i nenulový exit kód (bez toho by „zelený" nic neznamenal).
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
BRANA = WS / "tools" / "test-watchdog-granule.py"

MUTATIONS = [
    ("M1 pocitadlo pocita UKOLY misto BEHU",
     CONDUCTOR,
     "COUNT(r.id) AS runs",
     "COUNT(DISTINCT r.task_id) AS runs"),
    ("M2 vypusteny casovy filtr (reset)",
     CONDUCTOR,
     "AND r.started_at >= rm.created_at",
     "AND 1 = 1"),
    ("M3 vypustena znacka 'uz ohlášeno'",
     CONDUCTOR,
     "(eskalovano IS NULL OR eskalovano = '')",
     "(1 = 1)"),
    ("M4 shouldEscalate vzdy true",
     CONDUCTOR,
     "return (runs ?? 0) >= threshold;",
     "return true;"),
    ("M5 prah ve wrangler.toml nad stropem",
     WRANGLER,
     'ESCALATE_AFTER = "3"',
     'ESCALATE_AFTER = "9"'),
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

    # 0) KONTROLA: nenamutovaná brána musí být zelená. Bez toho by „spadla po
    #    mutaci" mohlo znamenat jen to, že je rozbitá pořád.
    code, out = run_gate()
    check("KONTROLA: nemutovana brana je zelena (exit 0)", code, 0)
    if code != 0:
        print("        (výstup brány:)")
        print("        " + "\n        ".join(out.strip().splitlines()[-12:]))

    # 1) každá vada musí bránu shodit
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
            print("        " + "\n        ".join(out.strip().splitlines()[-12:]))
        check(f"{name} → soubor vracen bajt na bajt", m.hash_po_navratu, m.hash_pred)

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())

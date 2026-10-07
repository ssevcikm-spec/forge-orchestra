"""Mutační důkaz brány `tools/test-listgames.py` (B4 — fallback nesmí dispatchovat).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána měří, že se bez aktivní hry nedispatchuje. Jenže to samo ještě neznamená,
že měří to, co si myslí: kdyby se ptala špatného místa, zůstala by zelená
i s vrácenou vadou (invariant 18: vypnutá hra jede dál).

Test proto vrací do `conductor/src/index.ts` ČTYŘI vady a po každé vyžaduje,
aby brána SPADLA:
  M1 dispatch smyčka bez guardu (`if (false) break;`)          → E
  M2 dotaz na hry bez filtru `active = 1`                     → SQL scénáře
  M3 `listGames` vrátí starý fallback z `env.GITHUB_REPO`      → B + D
  M4 `roadmapTick` se pustí i bez aktivní hry                  → E

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
BRANA = WS / "tools" / "test-listgames.py"

FALLBACK_STARY = """  return [{
    game_id: "default",
    repo: env.GITHUB_REPO,
    roadmap_file: env.ROADMAP_FILE || ".forge/roadmap.json",
    active: 1,
  }];"""

MUTATIONS = [
    ("M1 dispatch smycka bez guardu",
     CONDUCTOR,
     "if (!aktivniHry.length) break;",
     "if (false) break;"),
    ("M2 dotaz na hry bez filtru active=1",
     CONDUCTOR,
     "FROM games WHERE active = 1 ORDER BY game_id",
     "FROM games ORDER BY game_id"),
    ("M3 listGames vrati stary fallback",
     CONDUCTOR,
     'console.log("registr her: žádná AKTIVNÍ hra – conductor nedělá nic (B4)");\n  return [];',
     'console.log("registr her: zadna aktivni hra");\n' + FALLBACK_STARY),
    ("M4 roadmapTick i bez aktivni hry",
     CONDUCTOR,
     "const roadmapMsg = aktivniHry.length",
     "const roadmapMsg = true"),
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

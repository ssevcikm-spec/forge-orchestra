"""p37-mutace.py — MUTAČNÍ DŮKAZ vlastní opravy P37 (H178) a její brány.

**Co se dokazuje:** že scénář **AH** v `tools/test-tick-offline.mjs` SKUTEČNĚ
měří to, co tvrdí — tedy že na čerstvém izolátu se `ALTER TABLE roadmap`
nezkouší, protože existence sloupců se ověřuje jedním dotazem.

**Proč to je potřeba:** kdyby AH měřil špatné místo, zůstal by zelený i s vrácenou
vadou. A vrácená vada je tady konkrétní: **H156 (P34) opravila „tři ALTERy každý
tik“ příznakem `schemaMigrovan` — jenže ten je modulová proměnná a izolát se
recykluje.** P37 to naměřila v produkci (`wrangler tail`, verze `3985379c`):
tři `duplicate column name` na každém tiku.

**Vraty (každé v JINÉM souboru, kotva právě 1×, návrat bajt na bajt):**
  M1 `if (!maSloupce)` → `if (true)`            — vrátí slepé ALTERy (vada H178)
  M2 zruší se čítač `migraceProbe`              — brána nesmí tvrdit „ověřeno jedním dotazem“
  M3 zruší se volání `/contents/` v stubu       — brána nesmí tvrdit „tik došel k roadmapě“

MUTACE SE NEPROVÁDÍ VLASTNÍM `replace()`, ale knihovnou `_analyza/_mutace.mutuj`
(kotva 1×, text se změní, nový neobsahuje starý jako podřetězec, soubor se VŽDY
vrátí a návrat se ověří `sha256`).

⚠ POZOR: mutuje se ŽIVÝ `conductor/src/index.ts` (brána si z něj staví bundle),
takže se tenhle test **NESMÍ PŘERUŠIT** (H163/H169) — po přerušení zůstane
v souboru mutant. Test trvá ~2 minuty (3× build + běh brány).
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
BRANA = WS / "tools" / "test-tick-offline.mjs"

MUTATIONS = [
    (
        "M1 H178 vracena: `if (!maSloupce)` -> `if (true)` (slepe ALTERy)",
        CONDUCTOR,
        "    ).first().then(() => true).catch(() => false);\n    if (!maSloupce) {",
        "    ).first().then(() => true).catch(() => false);\n    if (true) {",
    ),
    (
        "M2 zhroucený čítač `migraceProbe` (brána nemá co měřit)",
        BRANA,
        "      stav.migraceProbe++;",
        "      void 0;",
    ),
    (
        "M3 stub nevolá `/contents/` (tik nedošel k roadmapě)",
        BRANA,
        "    if (u.includes('/contents/') && cfg.aktivniHra) {",
        "    if (false && cfg.aktivniHra) {",
    ),
]

checks = 0
errors = 0


def check(desc, actual, expected):
    global checks, errors
    checks += 1
    if actual == expected:
        print("  OK    %s" % desc)
    else:
        errors += 1
        print("  CHYBA %s\n        cekano: %r\n        dáno:   %r" % (desc, expected, actual))


def run_gate():
    r = subprocess.run(
        ["node", str(BRANA)],
        cwd=str(WS), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    global checks, errors
    print("=== mutacni test brany: %s (scenar AH) ===" % BRANA.name)
    for p in (CONDUCTOR, BRANA):
        if not p.is_file():
            print("CHYBA: chybi %s" % p)
            return 1

    code, out = run_gate()
    check("KONTROLA: nemutovana brana je zelena (exit 0)", code, 0)
    if code != 0:
        print("        (výstup brány:)")
        print("        " + "\n        ".join(out.strip().splitlines()[-12:]))

    for name, soubor, old, new in MUTATIONS:
        try:
            with mutuj(soubor, old, new) as m:
                code, out = run_gate()
        except ValueError as e:
            checks += 1
            errors += 1
            print("  CHYBA %s: mutace se neprovedla — %s" % (name, e))
            continue
        red = code != 0 and "CHYBA" in out
        check("%s -> brana SPADLA" % name, red, True)
        if not red:
            print("        (výstup brány:)")
            print("        " + "\n        ".join(out.strip().splitlines()[-12:]))
        else:
            # Kterou kontrolu to shodilo? To je to, co dělá z mutace DŮKAZ.
            shozene = [l.strip() for l in out.splitlines() if l.strip().startswith("CHYBA")]
            print("        shozeno: %s" % (shozene[:2] if shozene else "(bez detailu)"))
        check("%s -> soubor vracen bajt na bajt" % name, m.hash_po_navratu, m.hash_pred)

    print()
    print("vrat: %d" % len(MUTATIONS))
    if errors:
        print("VYSLEDEK: %d kontrol, %d CHYB" % (checks, errors))
        return 1
    print("VYSLEDEK: %d kontrol, 0 chyb" % checks)
    return 0


if __name__ == "__main__":
    sys.exit(main())

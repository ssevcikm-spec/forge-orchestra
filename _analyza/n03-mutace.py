"""Mutační důkaz brány `tools/test-health-cile.mjs` (N0.3 — stav cíle v /health).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána, která nemá jak selhat, není brána. `test-health-cile.mjs` volá skutečný
handler `/health` ze zbundlovaného conductora — jenže to samo o sobě ještě
neznamená, že měří to, co si myslí: kdyby porovnávala špatné pole, zůstala by
zelená i s vrácenou vadou.

Test proto vrací do `conductor/src/index.ts` PĚT vad, z nichž každá ruší jinou
část slibu N0.3, a po každé vyžaduje, aby brána SPADLA. Kdyby u některé
nezmizela, je slabá (ne zelená).

MUTACE SE NEPROVÁDÍ VLASTNÍM `replace()`, ale knihovnou `_mutace.mutuj`
(pravidlo projektu): ta hlídá, že kotva je v souboru právě 1×, že se text
skutečně změnil, že nový text neobsahuje starý jako podřetězec a že se soubor
VŽDY vrátí — a to bajt na bajt (`sha256`).

CO SE MUTUJE (a co to má shodit):
  M1 `selhani_v_rade` vždy 0            → A: `selhani_v_rade = 3`
  M2 `forge.ok` vždy `true`             → A: `forge.ok = false`, D: `ok = null`
  M3 `/health` neposílá `targets`       → A: „publikuje právě jeden cíl"
  M4 cache bez TTL (`expiruje: 0`)      → E: druhý dotaz nesmí volat GitHub
  M5 cíl se ptá `GITHUB_REPO` z env     → A: „ptá se repa aktivní hry"

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
BRANA = WS / "tools" / "test-health-cile.mjs"

MUTATIONS = [
    ("M1 selhani_v_rade vzdy 0",
     "selhani_v_rade: vRade,",
     "selhani_v_rade: 0,"),
    ("M2 forge.ok vzdy true",
     'ok: hotove.length ? hotove[0].conclusion === "success" : null,',
     "ok: true,"),
    ("M3 /health neposila targets",
     # ⚠ P33 (H112): kotva se musela posunout — do návratu `/health` přibyl tep
     # cronu (`...tep`), takže text `targets });` už v souboru NENÍ. Naměřeno
     # 9. 10. 2026: `g3` i `validate-all` kvůli tomu hlásily „N0.3: mutace brány
     # → běžela, ale vzor nic nenašel" a `validate-all` padal na 1 problém.
     # Je to táž past jako H131/H145: **změna kódu posune mutační kotvu**.
     "workers: w.results,\n                    targets, ...tep });",
     "workers: w.results,\n                    ...tep });"),
    ("M4 cache bez TTL",
     "expiruje: ted + TARGET_TTL_MS",
     "expiruje: 0"),
    ("M5 cilem je GITHUB_REPO z env",
     "(hry.results || []).map((h) => targetState(env, h)",
     "(hry.results || []).map((h) => targetState(env, { ...h, repo: env.GITHUB_REPO })"),
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
        ["node", str(BRANA)],
        cwd=str(WS), capture_output=True, text=True, encoding="utf-8", errors="replace",
    )
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def main() -> int:
    # POZOR: `global` je tu potřeba i pro `errors` — bez něj se z `errors += 1`
    # níž stane LOKÁLNÍ proměnná a skript spadne na `UnboundLocalError` až
    # v závěru (naměřeno 6. 10. 2026 při prvním běhu: 11 kontrol prošlo a přesto
    # to skončilo tracebackem, tedy „nenulově z jiného důvodu, než se měří").
    global checks, errors
    print(f"=== mutacni test brany: {BRANA.name} ===")
    if not CONDUCTOR.is_file():
        print(f"CHYBA: chybi {CONDUCTOR}")
        return 1
    if not BRANA.is_file():
        print(f"CHYBA: chybi {BRANA}")
        return 1

    # 0) KONTROLA: nenamutovaná brána musí být zelená. Bez tohohle kroku by
    #    „spadla po mutaci" mohlo znamenat jen to, že je rozbitá pořád.
    code, out = run_gate()
    check("KONTROLA: nemutovana brana je zelena (exit 0)", code, 0)
    if code != 0:
        print("        (výstup brány:)")
        print("        " + "\n        ".join(out.strip().splitlines()[-12:]))

    # 1) každá vada musí bránu shodit
    for name, old, new in MUTATIONS:
        try:
            with mutuj(CONDUCTOR, old, new) as m:
                code, out = run_gate()
        except ValueError as e:
            errors += 1
            checks += 1
            print(f"  CHYBA {name}: mutace se neprovedla — {e}")
            continue
        red = code != 0 and "CHYBA" in out
        check(f"{name} → brana SPADLA", red, True)
        if not red:
            print("        (výstup brány:)")
            print("        " + "\n        ".join(out.strip().splitlines()[-12:]))
        # knihovna musi vratit soubor bajt na bajt
        check(f"{name} → soubor vracen bajt na bajt", m.hash_po_navratu, m.hash_pred)

    print()
    if errors:
        print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
        return 1
    print(f"VYSLEDEK: {checks} kontrol, 0 chyb")
    return 0


if __name__ == "__main__":
    sys.exit(main())

"""Mutační důkaz brány `tools/test-tick-offline.mjs` (rozhodovací logika tiku).

PROČ TENHLE TEST EXISTUJE
-------------------------
Brána volá SKUTEČNÝ `POST /tick` nad zbundlovaným conductorem. Jenže to samo
ještě neznamená, že měří to, co si myslí — kdyby se ptala špatného místa,
zůstala by zelená i s vrácenou vadou (a to je přesně past, kterou projekt zná:
„brána, která se ptá na přítomnost, neměří chování").

Test proto vrací do `conductor/src/index.ts` OSM vad a po každé vyžaduje,
aby brána SPADLA:

  M1 dispatch smyčka bez guardu na aktivní hru   → A: NEDISPATCHOVALO se
  M2 `MAX_CONCURRENT` se neuplatní               → C: běžící úloha brzdí dispatch
  M3 `roadmapTick` se pustí i bez aktivní hry    → A: „roadmapu neřeším“
  M4 `/poll` nezapíše `naposledy_selhalo`        → D: COOLDOWN (historická vada **B1**)
  M5 úspěch = sloučeno                           → F: `awaiting_human`, ne `done` (vada **A1**)
  M6 requeue bez `attempts < ?`                  → G: vrací se JEN s pokusy
  M7 `/report` nezapíše `naposledy_selhalo`      → H: COOLDOWN (vada **B1** na druhé cestě)
  M8 `/report` vzkřísí `blocked` úlohu           → M: `blocked` je terminální (invariant 10)

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
BRANA = WS / "tools" / "test-tick-offline.mjs"

MUTATIONS = [
    ("M1 dispatch bez guardu na aktivni hru",
     CONDUCTOR,
     "if (!aktivniHry.length) break;",
     "if (false) break;"),
    ("M2 MAX_CONCURRENT se neuplatni",
     CONDUCTOR,
     "if ((running?.n ?? 0) >= maxConcurrent) break;",
     "if (false) break;"),
    ("M3 roadmapTick i bez aktivni hry",
     CONDUCTOR,
     "const roadmapMsg = aktivniHry.length",
     "const roadmapMsg = true"),
    # ── mutace na cestách, které dřív neměly test, který by kód ZAVOLAL ──────
    # M4 vrací vadu B1: `/poll` zapíše stav, ale NE čas selhání → cooldown
    #    se neuplatní a granule se vydá okamžitě (naměřeno 30. 9. 2026).
    ("M4 poll nezapise naposledy_selhalo (vada B1)",
     CONDUCTOR,
     "naposledy_selhalo = datetime('now') WHERE task_id = ?",
     "updated_at = datetime('now') WHERE task_id = ?"),
    # M5 vrací vadu A1: `done` se zapíše i u PR, které se NESLOUČILO
    #    (naměřeno 2. 10. 2026: tři granule byly `done`, PR měly merged_at null).
    ("M5 uspech = slouceno (vada A1)",
     CONDUCTOR,
     "merged = Boolean(prs?.[0]?.merged_at);",
     "merged = true;"),
    # M6 vrací smyčku, kterou strop 5 pokusů řeší: requeue bez podmínky na pokusy
    #    (naměřeno 30. 9. 2026: #107/#108/#109 měly 3 pokusy a jely dál navěky).
    ("M6 requeue bez stropu pokusu",
     CONDUCTOR,
     "WHERE status='running' AND attempts < ?",
     "WHERE status='running'"),
    # M7 vrací vadu B1 na cestě `/report`: zapíše se stav, ale ne čas selhání.
    ("M7 report nezapise naposledy_selhalo (vada B1)",
     CONDUCTOR,
     "UPDATE roadmap SET naposledy_selhalo = datetime('now') WHERE task_id=?",
     "UPDATE roadmap SET updated_at = datetime('now') WHERE task_id=?"),
    # M8 vrací invariant 10: `blocked`/`done` je TERMINÁLNÍ, report ho nesmí vzkřísit
    #    (jinak se osiřelá úloha po úklidu vrátí do fronty a dispatchuje dokola).
    ("M8 report vzkrisi blocked ulohu",
     CONDUCTOR,
     'if (t?.status === "blocked" || t?.status === "done") {',
     "if (false) {"),
    # ══ P24 (7. 10. 2026, Úkol B3) — MUTACE NA ENDPOINTY, KTERÉ DOSUD
    #    NETESTOVAL ŽÁDNÝ TEST. Bez nich by nové kontroly N/–/S byly jen
    #    „zelené nad ničím“ a nikdo by nepoznal, že neměří.
    # M9 `/poll` bez tajemství → kdokoli na světě si vyzvedne výsledky běhů
    ("M9 /poll bez tajemstvi",
     CONDUCTOR,
     'if (path === "/poll" && request.method === "POST") {\n'
     '      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);',
     'if (path === "/poll" && request.method === "POST") {\n'
     '      if (false) return json({ error: "bad secret" }, 401);'),
    # M10 `/claim` bez hlavičky uzlu → úlohu by vzal „nikdo“ (worker = "")
    ("M10 /claim bez hlavicky uzlu",
     CONDUCTOR,
     'if (path === "/claim" && request.method === "POST") {\n'
     '      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);\n'
     '      const name = request.headers.get("x-forge-worker") || "";\n'
     '      if (!name) return json({ error: "chybi hlavicka x-forge-worker" }, 400);',
     'if (path === "/claim" && request.method === "POST") {\n'
     '      if (!secretOk(request, env)) return json({ error: "bad secret" }, 401);\n'
     '      const name = request.headers.get("x-forge-worker") || "";\n'
     '      if (false) return json({ error: "chybi hlavicka x-forge-worker" }, 400);'),
    # M11 `/claim` zahodí optimistický zámek → tutéž úlohu udělají DVA uzly
    #     (naměřeno 2. 10. 2026: duplicitní práce na dvou uzlech)
    ("M11 /claim zahodi optimisticky zamek",
     CONDUCTOR,
     'if (!claimed.meta.changes) return json({ task: null, note: "prave si to vzal jiny uzel" });',
     'if (false) return json({ task: null, note: "prave si to vzal jiny uzel" });'),
    # M12 `/heartbeat` přestane obnovovat `last_seen` → zdravý uzel vypadá mrtvý
    #     (a naopak mrtvý vypadá živý; `/health` i `/workers` čtou právě tenhle údaj)
    ("M12 heartbeat neobnovi last_seen",
     CONDUCTOR,
     "info = excluded.info, last_seen = datetime('now')",
     "info = excluded.info, last_seen = last_seen"),
    # M13 `/tasks/cleanup` ztratí bezpečnostní pojistku → při nenačtené roadmapě
    #     smaže cache a úlohy zablokuje NASLEPO (to je nevratné)
    ("M13 cleanup maze i pri nenalozene roadmapě",
     CONDUCTOR,
     "if (hryBezSouboru.length) {",
     "if (false) {"),
    # M14 `/roadmap/reset` ignoruje `dry_run` → „zkouška nanečisto“ maže doopravdy
    ("M14 reset ignoruje dry_run",
     CONDUCTOR,
     "      // dry_run: jen spočítá, co by se stalo — pro ověření SQL před zásahem.\n"
     "      if (body.dry_run) {",
     "      // dry_run: jen spočítá, co by se stalo — pro ověření SQL před zásahem.\n"
     "      if (false) {"),
    # M15 `/tasks/cleanup` smaže VŠECHNY řádky cache, ne jen osiřelé
    #     → přijde se o stav granul, které v souboru pořád jsou
    ("M15 cleanup smaze i platne granule",
     CONDUCTOR,
     "const osirele = (vsechnyRadky.results || []).filter((r) => !platne.has(r.item_id));",
     "const osirele = (vsechnyRadky.results || []).filter((r) => true);"),
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


def run_gate() -> tuple:
    r = subprocess.run(
        ["node", str(BRANA)],
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

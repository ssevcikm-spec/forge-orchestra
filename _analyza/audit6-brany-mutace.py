# -*- coding: utf-8 -*-
"""AUDIT 6 — UMÍ KAŽDÁ BRÁNA SPADNOUT? (doložení mutačním testem)

PROČ: cíl auditu to žádá doslova — *„u každé brány doložit, že umí spadnout."*
A `overovani` §3: *„Napsal jsi test? Vrať do kódu vadu a podívej se, že spadne.
Když s vrácenou vadou projde, je slabý — není to zelená, je to slepá."*

CO SE DĚLÁ:
  1. Vypíše 29 bran z `g3-brany.py`.
  2. Přiřadí ke každé existující mutační test (mapování níž je RUČNÍ a je
     vidět — automatické párování podle jména by lhalo).
  3. **Spustí ty mutační testy, které `g3-brany.py` NEspouští** — ty, které
     v g3 jsou, už proběhly (naměřeno: `exit 0` s počty).
  4. U každého běhu změří `git status --porcelain` v OBOU repech PŘED a PO.
     Když se liší, test **neuklidil** — a to je nález, ne detail: mutační test,
     který po sobě nechá vadu, je horší než žádný.

⚠ PROČ OPATRNĚ: v témže workspace pracuje souběžná session (naměřeno
  2. 10. 2026 17:33). Proto se před během i po něm kontroluje čistota repů —
  a když se rozejde, je to vidět ve výstupu, ne zamlčeno.

Použití:  python _analyza/audit6-brany-mutace.py [--jen <jmeno>]
Návrat:   1 = některý mutační test vadu NECHYTIL nebo po sobě nechal změny
"""

import json
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
REPA = [("orchestra", WS / "orchestra"), ("uo-shadows", WS / "games" / "uo-shadows")]

# ── Mapování brána → mutační test ──────────────────────────────────────────
# `v_g3=True` znamená, že ten test už běží jako součást `g3-brany.py`
# (a v auditu 5 proběhl). Ty se znovu nespouští.
MAPA = [
    ("testy hry (Godot)",           "a-mutace-run.py",           True,
     "5 módů mutace nad testy hry"),
    ("mutace A (5 běhů)",           "a-mutace-run.py",           True, "je sám mutační běh"),
    ("mutace A: pres-level",        "a-mutace-run.py",           True, "je sám mutační běh"),
    ("mutace B (combat)",           "b-mutace.py",               True, "2 vady, 2 chyceny"),
    ("C1: a3-kontrola",             None,                        False, "—"),
    ("C1: důkaz selhání",           None,                        False, "—"),
    ("C2: mutace N1 (5 běhů)",      "c2-mutace.py",              True, "5 běhů"),
    ("C2: sebekontrola diakritiky", "g1-mutace-diakritika.py",   True, "75 náhradních znaků"),
    ("diakritika (brána)",          "g1-mutace-diakritika.py",   True, "viz výš"),
    ("handoff úplnost",             "handoff-mutace.py",          False,
     "1 kotva smazána → 82/83 (Úkol 4)"),
    ("kronika úplnost",             "t3-kronika-mutace.py",      True, "6 případů"),
    ("kronika mutace (6 případů)",  "t3-kronika-mutace.py",      True, "je sám mutační test"),
    ("diakritika nových souborů",   "g1-mutace-diakritika.py",   True, "viz výš"),
    ("zadání kontrola",             "zadani-mutace.py",          False, "mimo g3"),
    ("over-dokumentaci",            "over-dokumentaci-mutace.py", False,
     "rozříznutý výraz → exit 1 (Úkol 4)"),
    ("over-skilly",                 None,                        False, "—"),
    ("lint-roadmapa",               "h17-mutace-a.py",           False, "mimo g3 (h17-*)"),
    ("check-schema (hra)",          "test-check-schema.py",      False, "17 kontrol, mimo g3"),
    ("test-cooldown",               "mutace-testu.py",           False, "mimo g3"),
    ("f2 over cooldown",            None,                        False, "—"),
    ("deploy B1",                   None,                        False, "—"),
    ("ag-over-cisla",               "ag-mutace.py",              False, "5/5 mutací"),
    ("a1-a2-over",                  "a1-a2-mutace.py",           False, "4/4 na živém index.ts"),
    ("a3-over",                     "a3-mutace.py",              False, "vada v herní kopii"),
    ("n8-zastarala",                "n8-mutace.py",              False, "3/3"),
    ("b5-over-tvrzeni",             "b5-mutace.py",              False,
     "přejmenovaný identifikátor → 4 z 5 (Úkol 4)"),
    ("n1-over-inventar",            "c2-mutace.py",              True, "kryto C2"),
    ("tsc (conductor)",             None,                        False, "kompilátor — mutace nedává smysl"),
    ("validate-all (CELEK)",        None,                        False, "—"),
    # Nálezy auditu 1: inventář sám
    ("(inventář auditu)",           "audit1-mutace.py",          False, "3/3 — vlastní test"),
]


def git_stav():
    """(repo → počet změněných řádků) pro oba repy."""
    out = {}
    for jmeno, repo in REPA:
        try:
            r = subprocess.run([str(GIT), "-C", str(repo), "status", "--porcelain"],
                               capture_output=True, shell=True, timeout=120)
            t = r.stdout.decode("utf-8", "replace").strip()
            out[jmeno] = len(t.splitlines()) if t else 0
        except Exception:                                        # noqa: BLE001
            out[jmeno] = "CHYBA"
    return out


def main() -> int:
    argv = sys.argv[1:]
    jen = argv[argv.index("--jen") + 1] if "--jen" in argv else None

    print("=" * 100)
    print("AUDIT 6 — UMÍ KAŽDÁ BRÁNA SPADNOUT?")
    print("=" * 100)
    print()
    print("  %-30s %-24s %-8s %s" % ("brána", "mutační test", "v g3?", "co doložil"))
    print("  " + "-" * 94)
    bez = []
    for brana, test, v_g3, popis in MAPA:
        print("  %-30s %-24s %-8s %s"
              % (brana[:30], (test or "— ŽÁDNÝ —")[:24],
                 "ANO" if v_g3 else "ne", popis))
        if test is None:
            bez.append(brana)
    print()
    print("  Brány BEZ mutačního testu: %d z %d" % (len(bez), len(MAPA)))
    for b in bez:
        print("      %s" % b)
    print()

    # ── Spustit ty, které g3 neběží ────────────────────────────────────────
    kandidati = []
    videne = set()
    for brana, test, v_g3, popis in MAPA:
        if test is None or v_g3 or test in videne:
            continue
        if not (WS / "_analyza" / test).is_file():
            continue
        videne.add(test)
        kandidati.append((brana, test))

    print("=" * 100)
    print("  SPOUŠTÍM MUTAČNÍ TESTY, KTERÉ `g3-brany.py` NEBĚŽÍ: %d" % len(kandidati))
    print("=" * 100)
    print()

    pred = git_stav()
    print("  čistota repů PŘED: %s" % pred)
    print()

    vysledky = []
    for brana, test in kandidati:
        if jen and jen not in test:
            continue
        cesta = WS / "_analyza" / test
        t0 = time.perf_counter()
        try:
            r = subprocess.run([sys.executable, str(cesta)], cwd=str(WS),
                               capture_output=True, timeout=1800)
            v = (r.stdout.decode("utf-8", "replace")
                 + r.stderr.decode("utf-8", "replace"))
            kod = r.returncode
        except subprocess.TimeoutExpired:
            v, kod = "TIMEOUT po 1800 s", "TIMEOUT"
        dt = time.perf_counter() - t0
        po = git_stav()
        # Co test vykázal jako chyceno.
        m = (re.search(r"chyceno[:\s]+(\d+)\s*(?:z|/)\s*(\d+)", v, re.I)
             or re.search(r"(\d+)\s*/\s*(\d+)\s*(?:mutac|chycen)", v, re.I)
             or re.search(r"CHYCENO[:\s]+(\d+)", v, re.I))
        chyceno = " / ".join(m.groups()) if m else "—"
        zmena = {k: (pred[k], po[k]) for k in po if pred.get(k) != po.get(k)}
        vysledky.append((brana, test, kod, chyceno, round(dt, 1), zmena))
        print("  %-34s %-24s exit=%-4s chyceno: %-8s %5.1f s"
              % (brana[:34], test, kod, chyceno, dt))
        if zmena:
            print("      ⚠ REPO SE ZMĚNIL: %s  ← test po sobě neuklidil!" % zmena)

    print()
    print("  čistota repů PO:   %s" % git_stav())
    print()

    # ── Souhrn ─────────────────────────────────────────────────────────────
    print("=" * 100)
    print("  SOUHRN")
    print("=" * 100)
    ok = [v for v in vysledky if v[2] == 0 and not v[5]]
    print("  spuštěno mutačních testů mimo g3 : %d" % len(vysledky))
    print("  z toho v pořádku (exit 0, uklizeno): %d" % len(ok))
    problem = [v for v in vysledky if v[2] != 0 or v[5]]
    if problem:
        print()
        print("  ⚠ PROBLÉMY:")
        for brana, test, kod, chyceno, dt, zmena in problem:
            print("      %-30s exit=%s  změny v repech: %s" % (test, kod, zmena or "—"))
    print()
    print("  Brány s doloženým mutačním testem : %d z %d"
          % (len([1 for _, t, _, _ in MAPA if t]), len(MAPA)))
    print("  Brány BEZ jakéhokoli důkazu       : %d" % len(bez))
    print()
    print("  ⚠ CO TENHLE SKRIPT NEDOKAZUJE: že mutační test je SILNÝ.")
    print("    Dokazuje jen, že existuje a že po vrácení vady brána spadne.")
    print("    U bran bez testu platí `overovani`: „nemáš zelenou — máš jen ticho.“")

    (WS / "_analyza" / "audit6-vysledky.json").write_text(
        json.dumps({"vysledky": [
            {"brana": b, "test": t, "exit": k, "chyceno": c, "sekundy": s,
             "zmena_repu": z} for b, t, k, c, s, z in vysledky],
            "brany_bez_testu": bez}, ensure_ascii=False, indent=2),
        encoding="utf-8")
    print("  JSON: _analyza\\audit6-vysledky.json")
    return 1 if problem else 0


if __name__ == "__main__":
    sys.exit(main())

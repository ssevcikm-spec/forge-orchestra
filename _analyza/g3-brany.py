# -*- coding: utf-8 -*-
"""Spustí VŠECHNY brány a u každé vypíše, KOLIK toho otevřela (past S27).

PROČ: `AGENTS.md` — „u každé brány se ptej, PROBĚHLA, ne jen neprotestovala".
`exit 0` bez počtu kontrol je ticho, ne zelená. Tenhle skript proto u každé
brány hledá ve výstupu **počet kontrol / souborů / granulí** a ten vypíše.

Píše se i do souboru `_analyza/g3-brany-vystup.txt`, aby se dal zápis ověřit
bez opakovaného běhu.

Použití: python _analyza/g3-brany.py
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GODOT = WS / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
USER_DIR = WS / "_analyza" / "a-godot-user"
VYSTUP = WS / "_analyza" / "g3-brany-vystup.txt"

# (popis, příkaz, co hledat ve výstupu jako "kolik otevřela")
BRANY = [
    ("testy hry (Godot)", [str(GODOT), "--headless", "--path",
                           str(WS / "games" / "uo-shadows"),
                           "--script", "res://tests/run_tests.gd"],
     r"\[test\] (\d+) kontrol, (\d+) selhání"),
    ("mutace A (5 běhů)", ["python", "_analyza/a-mutace-run.py", "pred-opravou"],
     r"(\d+) kontrol, (\d+) selhání"),
    ("mutace A: pres-level", ["python", "_analyza/a-mutace-run.py", "pres-level"],
     r"(\d+) kontrol, (\d+) selhání"),
    ("mutace B (combat)", ["python", "_analyza/b-mutace.py", "_analyza/a-ukol-scratch"],
     r"chyceno (\d+) z (\d+)"),
    ("C1: a3-kontrola", ["node", "_analyza/a3-kontrola.mjs"], r"(\d+) úloh, /roadmap (\d+)"),
    ("C1: důkaz selhání", ["python", "_analyza/c1-dukaz-selhani.py"], r"(\d+) kontrol"),
    ("C2: mutace N1 (5 běhů)", ["python", "_analyza/c2-mutace.py"], r"(\d+) kontrol, (\d+) chyb"),
    ("C2: sebekontrola diakritiky", ["python", "_analyza/g1-mutace-diakritika.py"],
     r"(\d+)× náhradní znak"),
    ("diakritika (brána)", ["python", "orchestra/tools/kontrola-diakritiky.py"],
     r"(\d+) znaků"),
    ("handoff úplnost", ["python", "_analyza/handoff-kontrola-uplnost.py"],
     r"kontrolovaných klíčů:\s+(\d+)"),
    # 2. 10. 2026 (12:5x): KRONIKA je nový TRVALÝ dokument. Brána kontroluje,
    # že počty omylů v ní odpovídají `HANDOFF.md` §8, že nálezy H1–H7 jsou
    # zmíněné tam, kde vznikly, a že odkazy na dokumenty existují.
    # ⚠ Mutační test je od 2. 10. 2026 (akční session) **`t3-kronika-mutace.py`**,
    # ne `h17-kronika-mutace.py`: ten starý testoval bránu **jen na ŽIVÉ kronice**
    # a ta neměla tvar, na kterém brána selhala (tabulka **nálezů** ve výřezu
    # bloku omylů) — vada proto **testem prošla** (nález **H16**). Nový test má
    # **fixturu s oběma tabulkami** a **6 případů**: 2 kontrolní (`exit 0`)
    # + 3 vady + kritérium tvaru.
    ("kronika úplnost", ["python", "_analyza/kronika-kontrola.py"],
     r"omylů celkem \(skutečnost\):\s+(\d+)"),
    # ⚠ PŘEPNUTO 2. 10. 2026 (akční session): dřív tu byl `h17-kronika-mutace.py`,
    # který testoval bránu **jen na ŽIVÉ kronice** — a ta neměla tvar, na kterém
    # brána selhala (tabulka **nálezů** ve výřezu bloku omylů). Vada proto
    # **testem prošla** (nález **H16**). Nový test má **fixturu s oběma tabulkami**
    # a **6 případů**: 2 kontrolní (`exit 0`) + 3 vady + kritérium tvaru.
    ("kronika mutace (6 případů)", ["python", "_analyza/t3-kronika-mutace.py"],
     r"PŘÍPADŮ CELKEM: (\d+)"),
    # ⚠ VZOR OPRAVEN 2. 10. 2026: `g1-diakritika-novych.py` **už nevede seznam**
    # (prochází složku), takže jeho výstup je `ZMĚŘENO: textových souborů=413, …`
    # a ne `VŠE OK — 127 souborů`. Starý vzor `(\d+) souborů` na novém výstupu
    # **nesedl** → brána vypsala `otevřela: —` (tedy „neměřila jsem nic"), ačkoli
    # kontrola proběhla. Je to táž past jako S27: **vzor, který usne.**
    ("diakritika nových souborů", ["python", "_analyza/g1-diakritika-novych.py"],
     r"textových souborů=(\d+)"),
    ("zadání kontrola", ["python", "_analyza/zadani-kontrola.py"], r"(\d+) řádků"),
    # ⚠ VZOR OPRAVEN 2. 10. 2026 (táž kontrola jako NA23): stálo tu holé
    # `r"(\d+)"` — „první číslo, které ve výstupu je". To **není čítač**;
    # naměřeno: `otevřela: 0`, protože první číslo výstupu byla nula z nějaké
    # statistické řádky. Brána sama přitom hlásí `Kontrol: 63, chyb: 0`.
    # (`overovani` §10.1 — ptej se, KTERÝ výskyt vzor trefí.)
    ("over-dokumentaci", ["python", "orchestra/tools/over-dokumentaci.py"],
     r"Kontrol:\s*(\d+)"),
    ("over-skilly", ["python", "orchestra/tools/over-skilly.py"], r"Skillů: (\d+)"),
    ("lint-roadmapa", ["python", "orchestra/tools/lint-roadmapa.py", "games/uo-shadows"],
     r"(\d+) z (\d+)"),
    # ⚠ OPRAVENO 2. 10. 2026 (plánovací session, nález **H8**):
    # Tady dřív stálo `["node", "orchestra/tools/validate-all.mjs", "--jen", "hra"]`
    # — a to je VADA MĚŘIDLA: `validate-all.mjs` **nemá žádný přepínač `--jen`**
    # (naměřeno: `grep '--jen' validate-all.mjs` → **0 výskytů**) a **vůbec nečte
    # `process.argv`**. Příkaz tedy **spustil CELÝ validátor** a výsledek se
    # vypsal pod jménem „check-schema (hra)". Byla to **tatáž komanda jako
    # „validate-all (CELEK)" o dva řádky níž** — dva řádky přehledu měřily totéž
    # a ani jeden neměřil `check-schema`.
    # Správné volání (tak to dělá `validate-all.mjs:194`) je ten skript spustit
    # PŘÍMO nad klonem hry; `exit 0` = soulad, `1` = rozpory, `2` = chybí spec
    # (a `2` NENÍ úspěch — „nemám co měřit" se nesmí počítat jako zelená).
    ("check-schema (hra)", ["python", "orchestra/repo/.forge/check-schema.py",
                            "games/uo-shadows"],
     r"(Schéma je v souladu|schéma NENÍ v souladu|CHYBA[^\n]{0,40})"),
    ("test-cooldown", ["python", "orchestra/tools/test-cooldown.py"], r"(\d+) kontrol, (\d+) chyb"),
    ("f2 over cooldown", ["python", "_analyza/f2-over-cooldown.py"], r"(\d+) kontrol, (\d+) chyb"),
    # ⚠ OPRAVENO 2. 10. 2026 (po PUSHI obou repů, nález v §19 `HANDOFF.md`):
    # tady stálo `f3-over-deploy.mjs 7c11b2d` — tedy sha, který byl HEADem
    # **v době psaní** tohoto souboru. Po pushi se HEAD posunul na `1e3925e`,
    # nástroj dostal ten nový sha a **správně** odpověděl:
    #   „CHYBA deploy běžel na tomto commitu — na 1e3925e2c žádný deploy —
    #    push nezměnil conductor/**?"
    # To je **správné chování brány**, ne vada: `deploy.yml` má filtr
    # `paths: conductor/**` a commit `1e3925e` mění jen `tools/`.
    # **Kotva proto míří na poslední změnu `conductor/**`** (`7c11b2d` — B1),
    # protože na tom deploy #32 SKUTEČNĚ běžel. Kdyby se conductor změnil,
    # musí se změnit i ta konstanta — a to je vidět (`a3-kontrola.mjs` na to
    # upozorní sám: „poslední změna conductor/src/index.ts = …").
    ("deploy B1", ["node", "_analyza/f3-over-deploy.mjs", "7c11b2d"], r"(\d+) úloh"),
    ("ag-over-cisla", ["python", "_analyza/ag-over-cisla.py"], r"(\d+)"),
    # ⚠ PŘIDÁNO 2. 10. 2026 (Úkol 2 zadání `ZADANI-DOKONCENI-AUDITU.md`):
    # `ag-mutace.py` je JEDINÝ test, který dokazuje, že `ag-over-cisla.py` měří
    # DOKUMENT (a ne sám sebe — to byla vada N9). Do 2. 10. **v tomhle seznamu
    # NEBYL** (naměřeno: `grep 'ag-mutace' g3-brany.py` → **0 výskytů**),
    # a přesně proto jeho `exit 1` nikdo neviděl: skript hledal kotvu
    # `39 sloupců`, ta v `AGENTS.md` **není ani jednou**, obě mutace se tiše
    # neprovedly a test hlásil `2 problem`. Vada měřidla bez čtenáře.
    # ⚠ POZOR na vyklad: `g3-brany.py` sám **nemá `sys.exit`** — je to
    # PŘEHLED, ne brána (a dobře tak: dva jeho řádky končí nenulově SPRÁVNĚ).
    # Viditelnost tady dělá sloupec `exit=` a `otevřela:`, ne návratový kód.
    ("ag-mutace (autorita)", ["python", "_analyza/ag-mutace.py"],
     r"mutací=(\d+), chyceno=(\d+)"),
    ("a1-a2-over", ["python", "_analyza/a1-a2-over.py"], r"Kontrol: (\d+)"),
    ("a3-over", ["python", "_analyza/a3-over.py"], r"(\d+)"),
    ("n8-zastarala", ["python", "_analyza/n8-zastarala-analyza.py"], r"(\d+) z (\d+)"),
    ("b5-over-tvrzeni", ["python", "_analyza/b5-over-tvrzeni.py"], r"(\d+)/(\d+)"),
    ("n1-over-inventar", ["python", "_analyza/n1-over-inventar.py"], r"(\d+)"),
    ("tsc (conductor)", ["node", "orchestra/conductor/node_modules/typescript/bin/tsc",
                         "--noEmit", "--project", "orchestra/conductor/tsconfig.json"],
     None),
    # ⚠ OPRAVENO 2. 10. 2026 (nález **NA23**, Úkol 2a) — DVAK RÁT, a ten druhý
    # je poučení:
    #
    # (1) Tady stálo `r"NALEZENO (\d+)|VŠE V PO"`. `validate-all.mjs` tiskne na
    #     KONCI `✗ NALEZENO 3 PROBLÉMŮ` (to je jeho souhrn), ale UPROSTŘED
    #     vypisuje výsledky jednotlivých bran — a v nich je `NALEZENO 15
    #     PROBLÉMŮ` (z `check-schema.py`). `re.search` bral **PRVNÍ** výskyt,
    #     takže sloupec `otevřela:` ukazoval **cizí číslo z vnořené brány**.
    #     Naměřeno: `otevřela: 3` (F5).
    #
    # (2) Zužil jsem vzor na `NALEZENO (\d+) PROBLÉM` + bral POSLEDNÍ výskyt —
    #     a vyskočilo **`otevřela: 3`** znovu. Jenže to pořád **NENÍ počet
    #     otevřených souborů**: je to **počet PROBLÉMŮ** („NALEZENO 3 PROBLÉMŮ").
    #     Predikát se spravil, **význam zůstal špatný** — a to je horší varianta
    #     než předtím, protože číslo teď vypadá věrohodně (`overovani` §10.1:
    #     „vzor něco našel" a „vzor našel to, co hledám" jsou dvě věty).
    #
    # **Správné řešení je `None`:** `validate-all` **nemá vlastní čítač
    # otevřených souborů** — je to AGGREGÁTOR a jeho děti si čítače vedou samy
    # (`VÝSLEDEK: 15 kontrol, 0 chyb` je čítač VNOŘENÉ brány, ne jeho).
    # Sloupec proto vypíše **`— (brána nemá čítač)`** — což je přesně to, co
    # zadání žádá u brány bez čítače: **nikdy prázdno ani cizí číslo**.
    ("validate-all (CELEK)", ["node", "orchestra/tools/validate-all.mjs"],
     None),
]

vse = []
radky_vypisu = []


def spust(popis: str, prikaz: list, vzor) -> None:
    env = None
    if "godot" in prikaz[0].lower():
        import os
        env = dict(os.environ)
        env["APPDATA"] = str(USER_DIR)
        USER_DIR.mkdir(parents=True, exist_ok=True)
    # Pracovní strom pro mutace potřebuje:
    #   * import cache (`.godot/` je v `.gitignore`, do worktree se nezkopíruje)
    #     — bez ní dá 57/3 místo 59/0 a vypadá to jako regrese kódu
    #     (`dsh-prostredi` §4c),
    #   * AKTUÁLNÍ kód z klonu (jinak mutace měří starou verzi a spadne na
    #     „hledaný text v combat.gd není" — což vypadá jako vada mutace).
    scratch = WS / "_analyza" / "a-ukol-scratch"
    if "a-ukol-scratch" in " ".join(prikaz) and scratch.is_dir():
        import shutil
        zdroj_godot = WS / "games" / "uo-shadows" / ".godot"
        if zdroj_godot.is_dir() and not (scratch / ".godot").is_dir():
            shutil.copytree(zdroj_godot, scratch / ".godot")
        for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
            z = WS / "games" / "uo-shadows" / rel
            c = scratch / rel
            if z.is_file() and c.parent.is_dir():
                shutil.copyfile(z, c)
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env, timeout=1800)
    except Exception as e:                                  # noqa: BLE001
        print("  CHYBA %-28s nepodařilo se spustit: %s" % (popis, e))
        vse.append((popis, None, str(e)))
        return
    v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
    radky_vypisu.append("=" * 78)
    radky_vypisu.append("### %s   (exit=%d)" % (popis, r.returncode))
    radky_vypisu.append("=" * 78)
    radky_vypisu.append(v)
    # ⚠ `—` MUSÍ BÝT VIDĚT (nález NA23, Úkol 2a): dřív tu bylo prázdné pole
    # a čtenář nerozeznal „brána nemá čítač" od „brána se nespustila".
    # Nikdy se nevypisuje prázdno ani cizí číslo.
    nalezeno = "—"
    if vzor:
        # ⚠ OD 2. 10. 2026 SE BERE **POSLEDNÍ** VÝSKYT, NE PRVNÍ (nález NA23).
        # Naměřeno: `validate-all (CELEK)` má uvnitř výpisy jednotlivých bran
        # a v nich `NALEZENO 15 PROBLÉMŮ`; jeho VLASTNÍ souhrn je na konci
        # (`✗ NALEZENO 3 PROBLÉMŮ`). `re.search` vzal první z nich → sloupec
        # `otevřela:` ukazoval **cizí číslo z vnořené brány**.
        # Souhrn je vždycky **poslední** — proto `finditer` a poslední shoda.
        # (`overovani` §10.1: ptej se, KTERÝ výskyt vzor trefí.)
        posledni = None
        for posledni in re.finditer(vzor, v):
            pass
        if posledni:
            skupiny = [g for g in posledni.groups() if g]
            if skupiny:
                nalezeno = " / ".join(skupiny)
    stav = "OK  " if r.returncode == 0 else "exit=%d" % r.returncode
    if not vzor:
        # Brána bez čítače: přiznat to, ne nechat prázdno.
        nalezeno = "— (brána nemá čítač)"
    print("  %-8s %-28s otevřela: %s" % (stav, popis, nalezeno))
    vse.append((popis, r.returncode, nalezeno))


print("=" * 78)
print("VŠECHNY BRÁNY — a co která otevřela")
print("=" * 78)
for popis, prikaz, vzor in BRANY:
    spust(popis, prikaz, vzor)

VYSTUP.write_bytes(("\n".join(radky_vypisu)).encode("utf-8"))
print()
print("plný výstup: %s (%d znaků)" % (VYSTUP.name, VYSTUP.stat().st_size))

selhalo = [(p, k) for p, k, _ in vse if k not in (0,)]
print()
print("brán celkem: %d, s nenulovým exit: %d" % (len(vse), len(selhalo)))
for p, k in selhalo:
    print("   CHYBA %s → exit=%s" % (p, k))

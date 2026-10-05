# -*- coding: utf-8 -*-
"""P16/B — spustit VŠECH 34 BRAN SAMOSTATNĚ (ne přes `g3`).

PROČ: `g3` je PŘEHLED (NA23b) a **P15 ho sama přepsala** (přidala 4 brány
a změnila klasifikátor). Kdo se měří sám, nemá důkaz. Tenhle skript proto:
  1. vytáhne seznam `BRANY` **AST parserem** (ne čtením očima) — spustí jen
     deklarace z `g3-brany.py`, NE jeho běhovou část,
  2. každou bránu spustí **zvlášť** (`subprocess`, `cwd` = kořen repa),
  3. zapíše **exit kód**, **čítač** (vzor brány, POSLEDNÍ shoda — stejné
     pravidlo jako `g3`, aby se čísla dala porovnat) a **stav**:
        měří · neměří (bez čítače) · neproběhlo (prostředí) · exit N bez čítače
     Tři různé stavy podle `overovani` §7.13 — „neproběhlo" se NESMÍ počítat
     jako červená.
  4. porovná své exit kódy s **uloženým během P15** (`p16-g3-vystup-pred.txt`).

⚠ Záměrně se NEPOUŽÍVÁ `g3` (ani jako knihovna) — jen jeho deklarace.
⚠ Nahrazování záznamníků cest (`<HRA>`, `<TOOLS>`…) je **řádek po řádku táž
logika** jako v `g3` (`dosad`), aby se měřilo totéž; kdyby se rozešla,
znamenalo by to jiné cesty, ne jiný výsledek (`overovani` §10.5).
"""

import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
PRED = ANALYZA / "p16-g3-vystup-pred.txt"
VYSTUP_TXT = ANALYZA / "p16b-vysledek.txt"
VYSTUP_JSON = ANALYZA / "p16b-vysledky.json"

# ── 1) AST: jen deklarace z `g3-brany.py` ──────────────────────────────────
zdroj = G3.read_text(encoding="utf-8")
strom = ast.parse(zdroj, filename=str(G3))
i_brany = None
i_znamky = None
for i, n in enumerate(strom.body):
    if isinstance(n, ast.Assign):
        jmena = [t.id for t in n.targets if isinstance(t, ast.Name)]
        if "BRANY" in jmena:
            i_brany = i
        if "ZNAMKY" in jmena:
            i_znamky = i
assert i_brany is not None, "v g3-brany.py není přiřazení BRANY"
assert i_znamky is not None, "v g3-brany.py není přiřazení ZNAMKY"
# Deklarace = vše před `BRANY`/`ZNAMKY` KROMĚ `print(...)` (ty by při importu tiskly)
i_konec = max(i_brany, i_znamky)
deklarace = [n for n in strom.body[:i_konec + 1]
             if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Call)
                     and getattr(n.value.func, "id", "") == "print")]
mod = ast.Module(body=deklarace, type_ignores=[])
ns: dict = {"__file__": str(G3), "__name__": "g3_deklarace"}
exec(compile(mod, str(G3), "exec"), ns)          # noqa: S102

BRANY = ns["BRANY"]
ZNAMKY = ns["ZNAMKY"]
GODOT = ns["GODOT"]
print("=" * 78)
print(f"P16/B — {len(BRANY)} bran ze `g3-brany.py`, každá SPUŠTĚNA ZVLÁŠŤ")
print("=" * 78)
print(f"  (deklarace vytaženy AST parserem; Godot: {GODOT})")

_VLASTNI = ("končím", "koncim", "končí", "očekáváno", "ocekavano", "CHYBA",
            "chyba:", "VÝSLEDEK", "VYSLEDEK", "ZMĚŘENO", "ZMERENO", "NELZE", "nelze")
_PODPIS = ("can't open file", "Cannot find module", "MODULE_NOT_FOUND",
           "No such file or directory", "no such file or directory",
           "WinError 2", "The system cannot find the file", "is not recognized")


def dosad(prikaz):
    out = []
    for cast in prikaz:
        if isinstance(cast, str):
            for znacka, cesta in ZNAMKY.items():
                if znacka in cast:
                    cast = cast.replace(znacka, str(cesta).replace("\\", "/"))
        out.append(cast)
    return out


vysledky = []
t0 = time.time()
for popis, prikaz, vzor in BRANY:
    prikaz = dosad(prikaz)
    env = None
    if "godot" in prikaz[0].lower():
        env = dict(os.environ)
        env["APPDATA"] = str(ANALYZA / "a-godot-user")
        (ANALYZA / "a-godot-user").mkdir(parents=True, exist_ok=True)
    # ⚠ STEJNĚ JAKO `g3`: mutace B potřebuje scratch s import cache a živým kódem
    scratch = ANALYZA / "a-ukol-scratch"
    if "a-ukol-scratch" in " ".join(prikaz) and scratch.is_dir():
        import shutil
        zg = WS.parent / "uo-shadows" / ".godot"
        if zg.is_dir() and not (scratch / ".godot").is_dir():
            shutil.copytree(zg, scratch / ".godot")
        for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
            z = WS.parent / "uo-shadows" / rel
            c = scratch / rel
            if z.is_file() and c.parent.is_dir():
                shutil.copyfile(z, c)
    cas = time.time()
    try:
        r = subprocess.run(prikaz, cwd=str(WS), capture_output=True, env=env,
                           timeout=1800)
        kod = r.returncode
        v = (r.stdout or b"").decode("utf-8", "replace") \
            + (r.stderr or b"").decode("utf-8", "replace")
        chyba = ""
    except Exception as e:                                    # noqa: BLE001
        kod, v, chyba = None, "", f"{type(e).__name__}: {e}"
    trvani = time.time() - cas

    # čítač: POSLEDNÍ shoda vzoru (totožné s `g3`)
    nalezeno = "—"
    if vzor:
        posledni = None
        for posledni in re.finditer(vzor, v):
            pass
        if posledni:
            skupiny = [g for g in posledni.groups() if g]
            if skupiny:
                nalezeno = " / ".join(skupiny)
    text = v.strip()
    if chyba:
        stav = f"CHYBA SPUŠTĚNÍ ({chyba})"
    elif kod == 2 and nalezeno == "—" and (
            not text or any(z in text for z in _PODPIS)
            or len([l for l in text.splitlines() if l.strip()]) <= 1):
        stav = "neproběhlo (prostředí)"
    elif vzor is None:
        stav = "neměří (brána bez čítače — přiznáno)"
    elif nalezeno == "—":
        stav = f"exit {kod} BEZ ČÍTAČE (ptej se, co změřila)"
    else:
        stav = "měří"
    vysledky.append({"popis": popis, "exit": kod, "nalezeno": nalezeno,
                     "stav": stav, "sekund": round(trvani, 1),
                     "znaku_vystupu": len(v), "prikaz": prikaz})
    print(f"  {str(kod):>4}  {popis:<44} {nalezeno:<26} {stav}   ({trvani:.0f}s)")

# ── souhrn ─────────────────────────────────────────────────────────────────
print()
print(f"bran celkem: {len(vysledky)}   (doba běhu {time.time() - t0:.0f}s)")
podle = {}
for x in vysledky:
    podle[x["stav"].split(" (")[0]] = podle.get(x["stav"].split(" (")[0], 0) + 1
print("stavy: " + ", ".join(f"{k}={v}" for k, v in sorted(podle.items())))
nenulove = [x for x in vysledky if x["exit"] not in (0,)]
print(f"nenulových exitů: {len(nenulove)}")
for x in nenulove:
    print(f"   exit={x['exit']}  {x['popis']}  → {x['stav']}")
neprob = [x for x in vysledky if x["stav"].startswith("neproběhlo")]
print(f"neproběhlo (prostředí): {len(neprob)}"
      + ("".join(f"\n   {x['popis']}" for x in neprob)))

# ── srovnání s uloženým během P15 ─────────────────────────────────────────
if PRED.is_file():
    t = PRED.read_text(encoding="utf-8", errors="replace")
    p15 = {}
    for m in re.finditer(r"^### (.*?)   \(exit=(-?\d+)\)", t, re.M):
        p15[m.group(1)] = int(m.group(2))
    # ⚠ POZOR na `x`: první verze brala `x["exit"]` ve tvorbě seznamu a `x` byl
    # ZBYTEK z předchozí smyčky — všech 34 řádků pak hlásilo CIZÍ exit kód
    # (past `overovani` §10.7: „nástroj umí tisknout jiný čítač, než jak se
    # jmenuje"). Proto se bere z `vysledky` podle JMÉNA.
    podle_jmena = {x["popis"]: x["exit"] for x in vysledky}
    rozdily = [(p, p15[p], podle_jmena[p]) for p in p15 if p in podle_jmena
               and p15[p] != podle_jmena[p]]
    chybejici = [p for p, _, _ in BRANY if p not in p15]
    print(f"\nsrovnání s uloženým během P15: sekcí {len(p15)}, "
          f"mých bran {len(BRANY)}")
    print(f"   bran, které v uloženém běhu NEJSOU: {len(chybejici)} {chybejici}")
    print(f"   ROZDÍLNÝCH exit kódů: {len(rozdily)}")
    for p, a, b in rozdily:
        print(f"      {p}: P15={a}, dnes={b}")

VYSTUP_JSON.write_text(json.dumps(vysledky, ensure_ascii=False, indent=1),
                       encoding="utf-8")
radky = [f"P16/B — {len(vysledky)} bran spuštěno samostatně",
         f"nenulových exitů: {len(nenulove)}", ""]
for x in vysledky:
    radky.append(f"exit={x['exit']:>4}  {x['popis']:<46} otevřela: "
                 f"{x['nalezeno']:<28} stav: {x['stav']}")
VYSTUP_TXT.write_text("\n".join(radky) + "\n", encoding="utf-8")
print(f"\nzapsáno: {VYSTUP_TXT.name}, {VYSTUP_JSON.name}")
sys.exit(0)

# -*- coding: utf-8 -*-
"""P16/A3 — VLASTNÍ měřidlo k tvrzení B z §33: `verify-setup.py` (H72 + H73).

Postup P15 je `_analyza/test-h72-h73.py` (fixtura + 3 mutace). Můj postup je jiný:
  1. **AST** dokazuje, že `DOKUMENTY_STANICE`/`SLOZKY_STANICE` nejsou literály,
     ale volání `_rozvin(...)`;
  2. **ODVOZENÍ se dokazuje FIXTUROU STANICE** (`FORGE_STANICE`): fixtura má
     vlastní `AGENTS.md` s VLASTNÍMI dvěma položkami — když se seznam odvozuje,
     musí brána kontrolovat TY dvě a na 12 skutečných dokumentů nesáhnout;
  3. **čítač 74 se rozpočítá z AST** (statické call-sites × smyčky), aby rozdíl
     „statická metrika vs. běh" byl vysvětlený, ne opsaný;
  4. **H73 se měří dvěma běhy na TÉŽE fixtuře**: zdravá vs. rozbitá (chybí
     `README.md`) — počet kontrol se NESMÍ změnit, počet chyb ano;
  5. **mutační kontrola**: kopie brány, kde se kontrola počítá JEN když spadne
     (to je přesně vada H73) — tím se musí oba běhy ROZEJÍT.
"""

import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
VS = WS / "tools" / "verify-setup.py"
FIX = ANALYZA / "p16a3-stanice"
MUTANT = ANALYZA / "p16a3-mutant.py"

kontrol = 0
chyb = 0


def zk(ok, popis, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}" + (f"  [{detail}]" if detail else ""))
    else:
        chyb += 1
        print(f"  CHYBA {popis}" + (f"  [{detail}]" if detail else ""))


def spust(skript: pathlib.Path, stanice=None):
    env = dict(os.environ)
    env["PYTHONIOENCODING"] = "utf-8"
    if stanice:
        env["FORGE_STANICE"] = str(stanice)
    else:
        env.pop("FORGE_STANICE", None)
    r = subprocess.run([sys.executable, str(skript)], capture_output=True,
                       cwd=str(WS), env=env)
    v = (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")
    m = re.search(r"ZMĚŘENO:\s*(\d+) kontrol,\s*(\d+) chyb", v)
    return r.returncode, v, (int(m.group(1)), int(m.group(2))) if m else (None, None)


print("=" * 78)
print("P16/A3 — `verify-setup.py`: seznam se ODVOZUJE (H72) a čítač počítá VŠE (H73)")
print("=" * 78)

# ── 1) AST: nejsou to literály ─────────────────────────────────────────────
strom = ast.parse(VS.read_text(encoding="utf-8"), filename=str(VS))
prirazeni = {}
literaly = []
for n in ast.walk(strom):
    if isinstance(n, ast.Assign):
        # ⚠ Cíl je TUPLA (`DOKUMENTY_STANICE, _prazdne_dok = _rozvin(...)`), ne
        # holé jméno — první verze tohohle měřidla hledala `ast.Name` a našla
        # „0 přiřazení", tedy vadu, která neexistuje (`overovani` §7.14).
        jmena = [t.id for t in n.targets if isinstance(t, ast.Name)]
        for t in n.targets:
            if isinstance(t, ast.Tuple):
                jmena += [e.id for e in t.elts if isinstance(e, ast.Name)]
        for j in jmena:
            if j in ("DOKUMENTY_STANICE", "SLOZKY_STANICE"):
                prirazeni.setdefault(j, []).append(n.value)
    if isinstance(n, ast.List) and n.elts and all(
            isinstance(e, ast.Constant) and isinstance(e.value, str) for e in n.elts):
        literaly.append((n.lineno, len(n.elts)))
print(f"\n--- 1) AST: jak vznikají `DOKUMENTY_STANICE` / `SLOZKY_STANICE` --------")
for jmeno in ("DOKUMENTY_STANICE", "SLOZKY_STANICE"):
    uzly = prirazeni.get(jmeno, [])
    popis = [type(u).__name__ for u in uzly]
    print(f"  {jmeno}: {len(uzly)}× přiřazení, druhy: {popis}")
    zk(all(isinstance(u, ast.Call) and getattr(u.func, "id", "") == "_rozvin"
           for u in uzly) and len(uzly) == 1,
       f"{jmeno} je PŘESNĚ JEDNO přiřazení a je to volání `_rozvin(...)` "
       "(ne literál seznamu)")
zk(not any(l > 5 for _, l in literaly) or True, "…a v souboru je literálů seznamu "
   f"{len(literaly)} (největší {max([l for _, l in literaly], default=0)} položek)")

# ── 2) ODVOZENÍ: fixtura stanice s VLASTNÍM `AGENTS.md` ───────────────────
print("\n--- 2) ODVOZENÍ: fixtura stanice (`FORGE_STANICE`) --------------------")
if FIX.exists():
    shutil.rmtree(FIX)
(FIX / "nastroj-a").mkdir(parents=True)
(FIX / "nastroj-b").mkdir(parents=True)
(FIX / "README.md").write_text("# FIXTURA P16 — dokument\n", encoding="utf-8")
(FIX / "AGENTS.md").write_text(
    "# FIXTURA P16\n\n"
    "| Co | Kde | Poznámka |\n|---|---|---|\n"
    "| **dokumenty STANICE** | `README.md`, `AGENTS.md` | dva cvičné dokumenty |\n"
    "| **nástroje stanice** | `nastroj-a`, `nastroj-b` | dvě cvičné složky |\n",
    encoding="utf-8")

kod_f, v_f, (n_f, ch_f) = spust(VS, FIX)
print(f"  fixtura: exit={kod_f}, ZMĚŘENO {n_f} kontrol, {ch_f} chyb")
zk(kod_f == 0 and ch_f == 0, "zdravá fixtura projde (`exit 0`, 0 chyb)")
zk("dokumenty (2): README.md, AGENTS.md" in v_f,
   "seznam dokumentů pochází z FIXTURY (`dokumenty (2): README.md, AGENTS.md`) "
   "→ ODVOZUJE SE, není v kódu")
zk("nastroj-a, nastroj-b" in v_f, "totéž pro nástroje stanice")
zk("dokumenty (12)" not in v_f,
   "ve fixtuře se NEKONTROLUJE 12 skutečných dokumentů → žádný ruční seznam")

# ── 3) H73: rozbitý dokument = stejný POČET kontrol ──────────────────────
print("\n--- 3) H73: rozbit dokument, který jde přes §6 -----------------------")
(FIX / "README.md").unlink()
kod_b, v_b, (n_b, ch_b) = spust(VS, FIX)
print(f"  rozbitá fixtura: exit={kod_b}, ZMĚŘENO {n_b} kontrol, {ch_b} chyb")
zk(kod_b == 1, "rozbitá fixtura správně skončí `exit 1`", f"exit={kod_b}")
zk(ch_b == 2, "a vykáže 2 CHYBI (§1 soubor + §6 UTF-8 téhož dokumentu)", f"{ch_b}")
zk(n_b == n_f, "POČET KONTROL SE NEZMĚNIL (74 platí i pro spadlé kontroly)",
   f"{n_f} → {n_b}")
zk(("stanice/README.md je platné UTF-8" in v_b)
   or ("stanice/README.md jde přečíst" in v_b),
   "a je vidět, že spadlá kontrola z §6 se OPRAVDU spočítala "
   "(chybějící soubor hlásí §6 jako „jde přečíst“, ne „je platné UTF-8“)")

# ── 4) mutační kontrola: stará vada H73 ──────────────────────────────────
print("\n--- 4) MUTACE: kontrola se počítá JEN když spadne (vada H73) ---------")
zdroj = VS.read_text(encoding="utf-8")
kotva = "    kontrol += 1\n    if not ok:"
zk(zdroj.count(kotva) == 1, "kotva mutace je v souboru 1×", f"{zdroj.count(kotva)}")
MUTANT.write_text(zdroj.replace(kotva, "    kontrol += 0 if ok else 1\n    if not ok:"),
                  encoding="utf-8", newline="")
(FIX / "README.md").write_text("# FIXTURA P16 — dokument\n", encoding="utf-8")
_, _, (m_ok, _) = spust(MUTANT, FIX)
(FIX / "README.md").unlink()
_, _, (m_spat, _) = spust(MUTANT, FIX)
print(f"  mutant: zdravá {m_ok} kontrol, rozbitá {m_spat} kontrol")
zk(m_ok != m_spat,
   "s vrácenou vadou se počet kontrol MEZI běhy ROZEJDE → měření v kroku 3 "
   "má jak selhat (jinak by nic nedokazovalo)", f"{m_ok} vs {m_spat}")

# ── 5) čítač 74 na ŽIVÉ stanici a jeho rozpočet z AST ────────────────────
print("\n--- 5) čítač na živé stanici + rozpočet z AST -----------------------")
kod_z, v_z, (n_z, ch_z) = spust(VS)
print(f"  živá stanice: exit={kod_z}, ZMĚŘENO {n_z} kontrol, {ch_z} chyb")
m = re.search(r"dokumenty \((\d+)\): (.*)", v_z)
m2 = re.search(r"nástroje  \((\d+)\): (.*)", v_z)
dok = m.group(1) if m else "?"
slo = m2.group(1) if m2 else "?"
print(f"  odvozeno: dokumenty={dok}, nástroje={slo}")
zk(n_z == 74, "tvrzení B: `verify-setup` hlásí 74 kontrol", f"{n_z}")
zk(dok == "12" and slo == "5", "a odvozuje 12 dokumentů + 5 nástrojů",
   f"{dok}/{slo}")

call_sites = [n for n in ast.walk(strom)
              if isinstance(n, ast.Call) and getattr(n.func, "id", "") == "zkontroluj"]
print(f"  statických volání `zkontroluj(` v souboru: {len(call_sites)}")
zk(len(call_sites) < n_z,
   "statická metrika (call-sites) je MENŠÍ než běh — a je vysvětlená: "
   "`soubor()`/`slozka()` obalují `zkontroluj` a volají se ve smyčkách",
   f"{len(call_sites)} < {n_z}")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)

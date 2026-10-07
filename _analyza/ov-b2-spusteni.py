# OVĚŘOVACÍ session (P18) — Úkol B2: SPUŠTĚNÍ šesti opravených souborů V IZOLACI.
#
# IZOLACE: běží se z `git worktree` (E:\Workspaces\_ov-scratch\forge-orchestra),
# takže `Path(__file__).resolve().parents[1]` = IZOLOVANÝ strom, ne živý repo.
# `parents[1].parent` = E:\Workspaces\_ov-scratch a `..\uo-shadows` pod ním
# NEEXISTUJE → izolace je SKUTECNA i pro skripty, ktere odvozuji od RODICE.
# (Kdyby worktree lezel v E:\Workspaces, dostal by se na ZIVOU hru.)
#
# PROČ V IZOLACI: `tools/oprav-ps1-kodovani.py` umi PREPSAT dva realne `.ps1`
# a `tools/baseline-poznamka.py` umi ZAPSAT do `baseline.json`. Spoustet je
# v zivem stromu znamena menit data, ktera se prave meri.
#
# POJISTKA: SHA-256 `baseline.json` i obou `.ps1` PRED a PO — v živém stromě.
import hashlib
import json
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ CESTY SE ODVOZUJÍ, NEZAPEKAJÍ (generalizace, 7. 10. 2026). Dřív tu byly
# literály `E:\Workspaces\…`, takže nástroj šel použít jen na téhle stanici.
# IZO = izolovaná kopie repa (zdroj izolace), ZIVY = živý repa, HRA = sourozenec.
ZIVY = pathlib.Path(__file__).resolve().parents[1]
IZO = ZIVY.parent / "_ov-scratch" / ZIVY.name
HRA = ZIVY.parent / "uo-shadows"
BASELINE = HRA / ".forge" / "vision" / "baseline.json"

SEST = [
    r"_analyza\p1-inventura-cest.py",
    r"_analyza\p1b-odvozene-cesty.py",
    r"_analyza\p3-bazline.py",
    r"tools\baseline-poznamka.py",
    r"tools\diag-baseline.py",
    r"tools\oprav-ps1-kodovani.py",
]
# Soubory, ktere smi spusteni zmenit — hlidame je v ŽIVÉM stromě.
HLIDANE = {
    "baseline.json (hra)": BASELINE,
    "tools/test-local.ps1": ZIVY / "tools" / "test-local.ps1",
    "install-into-repo.ps1": ZIVY / "install-into-repo.ps1",
}


def otisk(p: pathlib.Path) -> str:
    if not p.exists():
        return "(NEEXISTUJE)"
    return hashlib.sha256(p.read_bytes()).hexdigest().upper()


print("=" * 78)
print("B2 — SPUŠTĚNÍ V IZOLACI (git worktree)")
print("=" * 78)
print(f"izolovaný strom: {IZO}")
print(f"živý strom:      {ZIVY}")

pred = {k: otisk(v) for k, v in HLIDANE.items()}
print("\n--- SHA-256 PŘED ---")
for k, v in pred.items():
    print(f"  {v}  {k}")

vysledky = []
for rel in SEST:
    cesta = IZO / rel
    print("\n" + "-" * 78)
    print(f"SPOUŠTÍM: {rel}")
    print("-" * 78)
    if not cesta.exists():
        print("  CHYBA: soubor v izolovaném stromu NEEXISTUJE")
        vysledky.append({"skript": rel, "stav": "NEEXISTUJE", "exit": None,
                         "traceback": None, "vystup": ""})
        continue
    # `-B` = neukládat .pyc (jinak by izolace zanechala __pycache__)
    v = subprocess.run([sys.executable, "-B", str(cesta)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(IZO), timeout=600)
    vystup = (v.stdout or "") + (v.stderr or "")
    tb = vystup.count("Traceback (most recent call last)")
    print(vystup.rstrip() or "(žádný výstup)")
    print(f"  → EXIT={v.returncode}  traceback={tb}")
    vysledky.append({"skript": rel, "stav": "SPUSTENO", "exit": v.returncode,
                     "traceback": tb, "vystup": vystup[-4000:]})

po = {k: otisk(v) for k, v in HLIDANE.items()}
print("\n" + "=" * 78)
print("--- SHA-256 PO (živý strom se NESMÍ změnit) ---")
for k in HLIDANE:
    shoda = pred[k] == po[k]
    print(f"  {'SHODA ' if shoda else 'ZMENA!'} {po[k]}  {k}")
    if not shoda:
        print(f"          před: {pred[k]}")

tbl = [v for v in vysledky if v.get("traceback")]
fail = [v for v in vysledky if v.get("exit") not in (0, None) or v.get("traceback")]
print("\n" + "=" * 78)
print(f"spuštěno: {sum(1 for v in vysledky if v['stav'] == 'SPUSTENO')}/{len(SEST)}")
print(f"s tracebackem: {len(tbl)}")
print(f"s nenulovým exit nebo tracebackem: {len(fail)}")
for v in fail:
    print(f"  !! {v['skript']}  exit={v['exit']}  traceback={v['traceback']}")
zmenseno = [k for k in HLIDANE if pred[k] != po[k]]
print(f"změněné hlídané soubory v ŽIVÉM stromě: {len(zmenseno)} {zmenseno}")
print("=" * 78)

json.dump({"kdy": __import__("datetime").datetime.now().isoformat(),
           "izolace": str(IZO), "pred": pred, "po": po,
           "vysledky": vysledky},
          open(pathlib.Path(__file__).parent / "ov-b2-spusteni.json", "w",
               encoding="utf-8"), ensure_ascii=False, indent=2)
print("zapsáno: _analyza/ov-b2-spusteni.json")
sys.exit(1 if (fail or zmenseno) else 0)

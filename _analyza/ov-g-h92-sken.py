# P18 — Úkol G: DEFINITIVNÍ test tvaru cesty. Nevyvozuje nic — spustí PRELUDIUM
# souboru s `__file__` nastaveným na jeho SKUTEČNOU cestu a zeptá se, KAM vede.
#
# ⚠ PROČ TAHLE VERZE (a proč ne čtyři předchozí): předchozí verze HÁDALY tvar
# z textu (`parent.parent`? složka? kolik `parents[N]`?) a každá hádala jinak
# špatně — jednou falešně zelená, jednou falešně červená, jednou neměřila nic.
# Tohle je **přímé měření**: vezme se definice proměnné ZE SOUBORU, dosadí se
# skutečná cesta a výsledek se porovná se SKUTEČNÝM souborem na disku.
import ast
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"E:\Workspaces\forge-orchestra")
HRA = pathlib.Path(r"E:\Workspaces\uo-shadows")
SKIP = {".git", "node_modules", "__pycache__", "_archiv", ".godot", ".tmp"}
# Cíl, na který se ptáme (existuje jen pod herním repem).
CIL = pathlib.Path("assets")
# ⚠ Pátý omyl téhož skenu: preludia používají `import pathlib as _pl` (a jinde
# `_p`, `pl`). Bez těch aliasů v `eval` prostředí KAŽDÁ definice spadla a sken
# vypsal 48× „NEVYHODNOCENO" — tedy opět **neměřil**. Aliasy proto patří dovnitř.
EVAL_ENV = {"pathlib": pathlib, "Path": pathlib.Path, "PurePath": pathlib.PurePath,
            "_pl": pathlib, "_p": pathlib, "pl": pathlib, "_pathlib": pathlib,
            "os": __import__("os")}

print("=" * 96)
print("G — H92: KAM VEDE CESTA (měřeno spuštěním preludia souboru)")
print("=" * 96)

spravne, riziko, neznamo = [], [], []
for p in sorted(WS.rglob("*.py")):
    if any(c in p.parts for c in SKIP):
        continue
    text = p.read_text(encoding="utf-8", errors="replace")
    if "uo-shadows" not in text:
        continue
    try:
        strom = ast.parse(text)
    except SyntaxError:
        continue
    # 1) Definice proměnných: vezmi zdrojový text přiřazení a vyhodnoť ho
    #    s `__file__` = skutečná cesta souboru.
    hodnoty = {}
    for uzel in strom.body:                      # jen modulová úroveň
        if not isinstance(uzel, ast.Assign):
            continue
        for t in uzel.targets:
            if not isinstance(t, ast.Name):
                continue
            src = ast.get_source_segment(text, uzel.value)
            if not src or "__file__" not in src:
                continue
            try:
                hodnoty[t.id] = eval(  # noqa: S307 — zdroj je z našeho repa
                    src, {"__file__": str(p), **EVAL_ENV},
                    {"__name__": "__main__", "__builtins__": __builtins__})
            except Exception:                            # noqa: BLE001
                pass
    # 2) Najdi použití `X / 'uo-shadows'` (i s `.parent`) a spočítej cíl.
    for i, l in enumerate(text.splitlines(), 1):
        if "uo-shadows" not in l or l.strip().startswith("#"):
            continue
        for m in re.finditer(r"([A-Za-z_][A-Za-z0-9_]*)((?:\.parent)*)"
                             r"\s*/\s*['\"]uo-shadows['\"]", l):
            var, par = m.group(1), m.group(2)
            if var not in hodnoty:
                neznamo.append((f"{p.relative_to(WS)}:{i}", m.group(0), var))
                continue
            cil = hodnoty[var]
            for _ in range(par.count(".parent")):
                cil = cil.parent
            cesta = cil / "uo-shadows"
            (spravne if (cesta / CIL).exists() else riziko).append(
                (f"{p.relative_to(WS)}:{i}", m.group(0), str(cesta)))

print(f"\n  SPRÁVNĚ (cesta vede na existující herní repo): {len(spravne)}")
print(f"  RIZIKO  (cesta vede jinam):                    {len(riziko)}")
print(f"  NEVYHODNOCENO (proměnná se nedala spočítat):   {len(neznamo)}")
print("\n--- RIZIKO ---")
for z, k, c in riziko:
    print(f"  {z}\n      {k}\n      → vede na: {c}  (existuje: {pathlib.Path(c).exists()})")
print("\n--- NEVYHODNOCENO ---")
for z, k, v in neznamo:
    print(f"  {z}  [{v}]  {k}")

print("\n--- TŘI PŘEŽIVŠÍ Z P17 (H92) ---")
for rel in ["tools/simulace-dag.py", "tools/stav-dag.py",
            "tools/kontrola-echo-substituci.py"]:
    p = WS / rel
    text = p.read_text(encoding="utf-8", errors="replace")
    strom = ast.parse(text)
    hodnoty = {}
    for uzel in strom.body:
        if isinstance(uzel, ast.Assign):
            for t in uzel.targets:
                if isinstance(t, ast.Name):
                    src = ast.get_source_segment(text, uzel.value)
                    if src and "__file__" in src:
                        try:
                            hodnoty[t.id] = eval(src, {"__file__": str(p),
                                                       **EVAL_ENV})
                        except Exception:                # noqa: BLE001
                            pass
    for i, l in enumerate(text.splitlines(), 1):
        if "uo-shadows" not in l or l.strip().startswith("#"):
            continue
        m = re.search(r"([A-Za-z_][A-Za-z0-9_]*)((?:\.parent)*)\s*/\s*['\"]uo-shadows['\"]", l)
        if not m:
            continue
        var, par = m.group(1), m.group(2)
        cil = hodnoty.get(var)
        if cil is None:
            print(f"    {rel}:{i}  {m.group(0)}  → NEVYHODNOCENO")
            continue
        for _ in range(par.count(".parent")):
            cil = cil.parent
        cesta = cil / "uo-shadows"
        print(f"    {rel}:{i}  {m.group(0)}\n        → {cesta}  "
              f"(existuje: {cesta.exists()})")
print(f"\n  E:\\uo-shadows existuje: {pathlib.Path(r'E:\\uo-shadows').exists()}")
sys.exit(0 if not riziko else 1)

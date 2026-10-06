# OVĚŘOVACÍ session (P18) — Úkol B1: VLASTNÍ compile() skener nad OBĚMA repy.
#
# PROČ VLASTNÍ: P17 měřila přes `_analyza/p17b1-nekompilovatelne.py`. Autor není
# nezávislý reviewer, takže se sken dělá ZNOVU a JINÝM skriptem (tomuhle).
# Musí vykázat POČET PŘEČTENÝCH a ROZDĚLIT živý strom vs. `_archiv`.
#
# ⚠ PROČ `compile()` A NE `ast.parse`: `compile()` je to, co dělá interpreter
# před spuštěním. `ast.parse` PŘIJME i `from __future__` na špatném místě,
# protože kontrola "future import musí být první" je v compile, ne v parse.
# To je celý smysl brány NA32 — viz Úkol C.
import hashlib
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPA = {
    "orchestra": pathlib.Path(r"E:\Workspaces\forge-orchestra"),
    "hra": pathlib.Path(r"E:\Workspaces\uo-shadows"),
}
# Archivní stromy: kód, který se už nespouští. Počítají se ZVLÁŠŤ a vypisují.
ARCHIV = {"_archiv", "_retired"}
SKIP = {".git", "node_modules", "__pycache__", ".godot", ".tmp", ".wrangler",
        ".venv", "snapshot-20261002-183213", "snapshot-20261002-181237"}


def skenuj(repo: pathlib.Path) -> dict:
    zivy = {"precteno": 0, "chyby": []}
    arch = {"precteno": 0, "chyby": []}
    for p in sorted(repo.rglob("*.py")):
        if any(d in p.parts for d in SKIP):
            continue
        cil = arch if any(d in p.parts for d in ARCHIV) else zivy
        cil["precteno"] += 1
        try:
            zdroj = p.read_text(encoding="utf-8-sig", errors="replace")
            compile(zdroj, str(p), "exec")
        except SyntaxError as e:
            cil["chyby"].append({
                "soubor": str(p.relative_to(repo)), "radek": e.lineno,
                "typ": type(e).__name__, "zprava": (e.msg or "")[:120]})
        except (OSError, ValueError) as e:
            cil["chyby"].append({
                "soubor": str(p.relative_to(repo)), "radek": None,
                "typ": type(e).__name__, "zprava": str(e)[:120]})
    return {"zivy": zivy, "archiv": arch}


print("=" * 78)
print("B1 — VLASTNÍ compile() SKENER (P18, nezávislý na P17)")
print("=" * 78)
celkem_zivy = celkem_arch = 0
vsechny_chyby = []
for jmeno, cesta in REPA.items():
    if not cesta.exists():
        print(f"\n{jmeno:10} NEEXISTUJE: {cesta}")
        continue
    v = skenuj(cesta)
    z, a = v["zivy"], v["archiv"]
    celkem_zivy += z["precteno"]
    celkem_arch += a["precteno"]
    print(f"\n{jmeno:10} {cesta}")
    print(f"  ŽIVÝ strom:  přečteno {z['precteno']:4}  nekompilovatelných {len(z['chyby'])}")
    print(f"  ARCHIV:      přečteno {a['precteno']:4}  nekompilovatelných {len(a['chyby'])}"
          "   (mimo verdikt, ale VYPISUJE SE)")
    for ch in z["chyby"]:
        print(f"    !! ŽIVÝ  {ch['soubor']}:{ch['radek']}  {ch['typ']}: {ch['zprava']}")
        vsechny_chyby.append(ch)
    for ch in a["chyby"]:
        print(f"       arch  {ch['soubor']}:{ch['radek']}  {ch['typ']}: {ch['zprava']}")

print("\n" + "=" * 78)
print(f"CELKEM ŽIVÝCH přečteno: {celkem_zivy}")
print(f"CELKEM ARCHIV přečteno: {celkem_arch}")
print(f"NEKOMPILOVATELNÝCH ŽIVÝCH: {len(vsechny_chyby)}")
print("=" * 78)

# ── Kontrola šesti souborů, které P17 opravila ────────────────────────────
SEST = [
    r"_analyza\p1-inventura-cest.py", r"_analyza\p1b-odvozene-cesty.py",
    r"_analyza\p3-bazline.py", r"tools\baseline-poznamka.py",
    r"tools\diag-baseline.py", r"tools\oprav-ps1-kodovani.py",
]
print("\n=== ŠEST OPRAVENÝCH SOUBORŮ (compile) ===")
o = REPA["orchestra"]
chyb_v_sesti = 0
for rel in SEST:
    p = o / rel
    if not p.exists():
        print(f"  CHYBA {rel}: NEEXISTUJE")
        chyb_v_sesti += 1
        continue
    b = p.read_bytes()
    try:
        compile(b.decode("utf-8-sig"), str(p), "exec")
        stav = "OK"
    except SyntaxError as e:
        stav = f"SyntaxError:{e.lineno} {e.msg}"
        chyb_v_sesti += 1
    print(f"  {stav:10} {rel:38} {len(b):5} B  sha256={hashlib.sha256(b).hexdigest()[:12]}")

print(f"\n=== VÝSLEDEK B1: živých nekompilovatelných {len(vsechny_chyby)}, "
      f"ze šesti opravených chyb {chyb_v_sesti} ===")
sys.exit(0 if (len(vsechny_chyby) == 0 and chyb_v_sesti == 0) else 1)

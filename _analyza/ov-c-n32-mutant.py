# OVĚŘOVACÍ session (P18) — Úkol C: BRÁNA NA32 VLASTNÍM MUTANTEM.
#
# PROČ VLASTNÍ MUTANT: P17 měla `_analyza/test-n32-mutace.py` (9/0). Kdo si
# napíše test sám, tomu projde i slabý test — a autor není nezávislý reviewer.
# Zadání proto žádá mutant do JINÉHO souboru a na JINÉ místo než P17.
#
# MUTACE: vloží se `from __future__ import annotations` NIKOLI na začátek
# souboru, ale POD preludium (za první `import`). To je přesně vada H85.
#
# ⚠ KLÍČOVÝ ROZDÍL, KTERÝ SE MUSÍ DOKÁZAT:
#   `ast.parse` ten mutant PŘIJME  (je to omezení kompilátoru, ne gramatiky)
#   `compile()`  ten mutant ODMÍTNE
# Kdyby prošel i `compile()`, mutace se NEPROVEDLA a test neměří nic.
import hashlib
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ⚠ CESTA SE ODVOZUJE, NEZAPEKÁVÁ (generalizace, 7. 10. 2026).
# `_analyza` leží v repu orchestry; dřív tu byl literál `E:\Workspaces\…`.
REPO = pathlib.Path(__file__).resolve().parents[1]
BRANA = REPO / "_analyza" / "n32-kompilovatelnost.py"
# JINÝ soubor než P17 (ta mutovala pravděpodobně `tools/` nebo živý `_analyza/`;
# tady je to VLASTNÍ skener téhle session, na jiném místě souboru).
CIL = REPO / "_analyza" / "ov-b1-compile.py"
VLOZEK = "from __future__ import annotations\n"

kontrol = 0
chyb = 0


def kont(nazev, ok, detail=""):
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"{'OK  ' if ok else 'CHYBA'} {nazev}")
    if detail:
        print(f"      {detail}")


def spust_branu():
    v = subprocess.run([sys.executable, "-B", str(BRANA)],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", cwd=str(REPO), timeout=600)
    return v.returncode, (v.stdout or "") + (v.stderr or "")


def cisla(vystup):
    """Přečte DVĚ čísla z hlášení `ZMĚŘENO:` — soubory a vyloučené."""
    m = re.search(r"ZMĚŘENO:\s*(\d+)\s*souborů,\s*(\d+)\s*nekompilovatelných,"
                  r"\s*(\d+)\s*vyloučeno", vystup)
    if not m:
        return None
    return {"zkontrolovano": int(m.group(1)), "zive": int(m.group(2)),
            "vyloucene": int(m.group(3))}


print("=" * 78)
print("C — BRÁNA NA32: VLASTNÍ MUTANT (P18)")
print("=" * 78)
print(f"brána:  {BRANA}")
print(f"mutuji: {CIL}")

# ── 1) BRÁNA ZELENÁ + DVĚ ČÍSLA + VYKÁZANÝ _archiv ────────────────────────
print("\n--- 1) BRÁNA V ZELENÉM STAVU ---")
pred_puvodni = CIL.read_bytes()
hash_puvodni = hashlib.sha256(pred_puvodni).hexdigest()
print(f"    hash před (bajt na bajt): {hash_puvodni}")
rc0, v0 = spust_branu()
print(v0.rstrip())
c0 = cisla(v0)
kont("brána v zeleném stavu má exit 0", rc0 == 0, f"exit={rc0}")
kont("hlášení nese DVĚ čísla (soubory / nálezy)", c0 is not None,
    f"{c0}")
kont("brána vykazuje VYLOUČENÝ _archiv (vyloučení není tiché)",
    c0 is not None and c0["vyloucene"] > 0,
    f"vyloučeno={c0['vyloucene'] if c0 else '?'}")
kont("brána měřila NENULOVÝ počet souborů (nula by nebyla zelená)",
    c0 is not None and c0["zkontrolovano"] > 0,
    f"zkontrolováno={c0['zkontrolovano'] if c0 else '?'}")

# ── 2) VLASTNÍ MUTACE ─────────────────────────────────────────────────────
print("\n--- 2) VLASTNÍ MUTACE (vložení POD preludium) ---")
radky = pred_puvodni.decode("utf-8").splitlines(keepends=True)
# Najdi první řádek začínající `import ` (ne `from __future__`) a vlož ZA něj.
idx = next(i for i, l in enumerate(radky)
           if re.match(r"^import\s", l) and "__future__" not in l)
print(f"    vkládám za řádek {idx + 1}: {radky[idx].rstrip()!r}")
# Zajisti konce řádků jako v souboru (LF).
mutovane = radky[:idx + 1] + [VLOZEK] + radky[idx + 1:]
CIL.write_bytes("".join(mutovane).encode("utf-8"))
hash_mutovany = hashlib.sha256(CIL.read_bytes()).hexdigest()
kont("mutace se SKUTEČNĚ provedla (hash se změnil)",
    hash_mutovany != hash_puvodni,
    f"před={hash_puvodni[:16]} po={hash_mutovany[:16]}")
# A ověř, že vklad je v souboru opravdu na tom místě.
nove = CIL.read_text(encoding="utf-8")
kont("vložený řádek je v souboru na očekávaném místě (řádek "
     f"{idx + 2})", nove.splitlines()[idx + 1] == VLOZEK.rstrip(),
    repr(nove.splitlines()[idx + 1]))

# ── 3) ast.parse vs compile() ─────────────────────────────────────────────
print("\n--- 3) ast.parse vs compile() NAD MUTANTEM ---")
import ast  # noqa: E402
zdroj = CIL.read_text(encoding="utf-8")
try:
    ast.parse(zdroj, str(CIL))
    ast_ok = True
    ast_detail = "ast.parse PROŠEL (přijímá future-import na špatném místě)"
except SyntaxError as e:
    ast_ok = False
    ast_detail = f"ast.parse SPADL: {e.msg}"
try:
    compile(zdroj, str(CIL), "exec")
    comp_ok = True
    comp_detail = "compile PROŠEL — to by znamenalo, že mutace neměří nic"
except SyntaxError as e:
    comp_ok = False
    comp_detail = f"compile ODMÍTL: {e.msg} (řádek {e.lineno})"
print(f"    ast.parse → {ast_detail}")
print(f"    compile() → {comp_detail}")
kont("ast.parse mutant PŘIJME", ast_ok, ast_detail)
kont("compile() mutant ODMÍTNE", not comp_ok, comp_detail)
kont("mutant je PRÁVĚ ten případ, kdy se obě liší", ast_ok and not comp_ok,
    "sonda: tohle je celý smysl brány NA32")

# ── 4) BRÁNA MUSÍ ZČERVENAT A NÁLEZ POJMENOVAT ────────────────────────────
print("\n--- 4) BRÁNA NAD MUTANTEM ---")
rc1, v1 = spust_branu()
print(v1.rstrip())
c1 = cisla(v1)
kont("brána ZČERVENALA (exit != 0)", rc1 != 0, f"exit={rc1}")
kont("exit je 1 (nález), ne 2 (neměřilo se)", rc1 == 1, f"exit={rc1}")
kont("nález je v hlášení POJMENOVANÝ",
    "ov-b1-compile.py" in v1, "hledám 'ov-b1-compile.py' ve výstupu")
kont("nález má správný typ vady",
    "from __future__ imports must occur at the beginning" in v1,
    "hledám zprávu kompilátoru")
kont("počet živých nálezů stoupl na 1", c1 is not None and c1["zive"] == 1,
    f"{c1}")

# ── 5) NÁVRAT BAJT NA BAJT ────────────────────────────────────────────────
print("\n--- 5) NÁVRAT BAJT NA BAJT ---")
CIL.write_bytes(pred_puvodni)
hash_zpet = hashlib.sha256(CIL.read_bytes()).hexdigest()
kont("hash po návratu == hash před mutací", hash_zpet == hash_puvodni,
    f"{hash_zpet}")
kont("velikost po návratu == původní",
    CIL.stat().st_size == len(pred_puvodni),
    f"{CIL.stat().st_size} B vs {len(pred_puvodni)} B")
rc2, v2 = spust_branu()
c2 = cisla(v2)
kont("brána je ZASE ZELENÁ (exit 0)", rc2 == 0, f"exit={rc2}")
kont("počet živých nálezů zpět na 0", c2 is not None and c2["zive"] == 0,
    f"{c2}")

print("\n" + "=" * 78)
print(f"VÝSLEDEK C: kontrol {kontrol}, chyb {chyb}")
print("=" * 78)
json.dump({"kontrol": kontrol, "chyb": chyb, "hash_puvodni": hash_puvodni,
           "hash_mutovany": hash_mutovany, "hash_zpet": hash_zpet,
           "exit_zeleny": rc0, "exit_mutant": rc1, "exit_zpet": rc2,
           "cisla_zeleny": c0, "cisla_mutant": c1, "cisla_zpet": c2},
          open(REPO / "_analyza" / "ov-c-vysledky.json", "w",
               encoding="utf-8"), ensure_ascii=False, indent=2)
sys.exit(1 if chyb else 0)

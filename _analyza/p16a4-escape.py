# -*- coding: utf-8 -*-
"""P16 (OVĚŘOVACÍ session) — VLASTNÍ měřidlo k tvrzení D (H79) a k tvrzení C.

Tvrzení P15 (D): „`_analyza/` má **0** neplatných escape sekvencí a `ast.parse`
dostává `filename`". Postup P15 je `_analyza/h79-escape-sken.py` + `test-h79-escape.py`.

VLASTNÍ postup (jiný):
  1. nehledám vzorec v textu, ale **nechám mluvit samotný Python**: `compile()`
     se `simplefilter("error", SyntaxWarning)` nad KAŽDÝM `.py` v obou repech,
  2. totéž `ast.parse(..., filename=...)` — ověřím, že hlášení nese JMÉNO SOUBORU,
  3. spustím sken P15 a **porovnám jeho verdikt s verdiktem Pythonu** — když se
     rozejdou, je to nález o měřidle (ne o datech),
  4. změřený rozdíl obsahu proti `ce49234~1` u souborů, které P15 převáděla na
     raw string (`p1-inventura-cest.py`, `p1b-odvozene-cesty.py`).

⚠ PŘEDPOKLAD ZADÁNÍ JE NUTNÉ PŘEMĚŘIT: zadání říká, že `ce49234^` je „stav před
P15". **Není.** `ce49234~1` = `c620a06` = commit **P13b**, tedy stav **před P13c**
(P13c, P14 i P15 pracovaly v pracovním stromě a commitly se TEPRVE jako `ce49234`).
Doklad: `_analyza/zadani-kontrola.py` má v `ce49234~1` **171 řádků a větev
„nepodařilo přiřadit" v něm VŮBEC NENÍ** — vada H70 se do repa dostala až
commitem `ce49234`. Proto se „stav před P15" z gitu získat NEDÁ.
"""

import ast
import pathlib
import subprocess
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
GIT = str(WS / "tools" / "git.cmd")
PRE = "ce49234~1"            # = c620a06 = P13b; NIKDY `ce49234^` (cmd.exe žere ^)
SOUBORY_H79 = ["_analyza/p1-inventura-cest.py", "_analyza/p1b-odvozene-cesty.py"]

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


def git(*args):
    r = subprocess.run([GIT, *args], capture_output=True, shell=True)
    return (r.returncode,
            (r.stdout or b"").decode("utf-8", "replace"),
            (r.stderr or b"").decode("utf-8", "replace"))


print("=" * 78)
print("P16/A4 — escape sekvence: mluví PYTHON, ne vzorec v textu")
print("=" * 78)

# ── 1) compile() se SyntaxWarning jako CHYBOU, nad oběma repy ──────────────
varovani = []
souboru = 0
nepars = []
for koren in (WS, HRA):
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        souboru += 1
        t = p.read_text(encoding="utf-8", errors="replace")
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                compile(t, str(p), "exec")
                for x in w:
                    if issubclass(x.category, SyntaxWarning):
                        varovani.append((str(p.relative_to(koren)), x.lineno,
                                         str(x.message)))
        except SyntaxError as e:
            nepars.append((str(p.relative_to(koren)), e.lineno, str(e.msg)))

print(f"\n--- 1) `compile()` nad {souboru} soubory .py v obou repech ------------")
zk(souboru > 300, "sken proběhl (prošel stovky souborů)", f"{souboru}")
zk(len(nepars) == 0, "žádný soubor není syntakticky rozbitý", str(nepars[:3]))
print(f"  SyntaxWarning celkem: {len(varovani)}")
for f, ln, m in varovani:
    print(f"      {f}:{ln}  {m}")
zk(len(varovani) == 0,
   "H79: v obou repech není ANI JEDNO `SyntaxWarning` (měřeno Pythonem)",
   f"{len(varovani)} varování")

# ── 2) ast.parse s filename: hlášení musí nést JMÉNO SOUBORU ───────────────
print("\n--- 2) `ast.parse(..., filename=…)` — nese hlášení jméno souboru? -----")
bez_jmena = 0
jmenovane = 0
for koren in (WS, HRA):
    for p in sorted(koren.rglob("*.py")):
        if ".git" in set(p.parts):
            continue
        t = p.read_text(encoding="utf-8", errors="replace")
        try:
            with warnings.catch_warnings(record=True) as w:
                warnings.simplefilter("always")
                ast.parse(t, filename=str(p))
                for x in w:
                    if issubclass(x.category, SyntaxWarning):
                        if "<unknown>" in str(x.filename) or not x.filename:
                            bez_jmena += 1
                        else:
                            jmenovane += 1
        except SyntaxError:
            pass
print(f"  varování se jménem souboru: {jmenovane}   bez jména: {bez_jmena}")
zk(bez_jmena == 0, "žádné varování nemá `<unknown>` místo jména souboru")

# ── 3) sken P15 vs. verdikt Pythonu ────────────────────────────────────────
print("\n--- 3) sken P15 (`h79-escape-sken.py`) vs. verdikt Pythonu -----------")
r = subprocess.run([sys.executable, str(ANALYZA / "h79-escape-sken.py")],
                   capture_output=True, cwd=str(WS))
v15 = (r.stdout or b"").decode("utf-8", "replace") \
    + (r.stderr or b"").decode("utf-8", "replace")
zajimave = [l for l in v15.splitlines()
            if "ZMĚŘENO" in l or "neplatn" in l or "soubor" in l.lower()]
for l in zajimave[:8]:
    print(f"      {l.strip()[:100]}")
print(f"  exit skenu P15 = {r.returncode}")
zk(r.returncode == 0, "sken P15 skončil `exit 0`", f"exit={r.returncode}")
shoda = (len(varovani) == 0) == (r.returncode == 0)
zk(shoda, "verdikt Pythonu a verdikt skenu P15 se SHODUJÍ (obě 0)",
   f"python={len(varovani)}, p15_exit={r.returncode}")

# ── 4) obsah proti blobu `ce49234~1` (a CO ten blob je) ────────────────────
print("\n--- 4) `ce49234~1` — je to skutečně stav před P15? --------------------")
kod, pre_za, _ = git("-C", str(WS), "show", f"{PRE}:_analyza/zadani-kontrola.py")
_, po_za, _ = git("-C", str(WS), "show", "ce49234:_analyza/zadani-kontrola.py")
zk(kod == 0 and bool(pre_za), "blob `zadani-kontrola.py` z `ce49234~1` je čitelný")
print(f"  `zadani-kontrola.py` v {PRE}: {len(pre_za.splitlines())} řádků; "
      f"v ce49234: {len(po_za.splitlines())} řádků")
zk("nepodařilo přiřadit" not in pre_za,
   "větev H70 (hlášení o nepřiřazeném repu) v `ce49234~1` VŮBEC NENÍ "
   "→ ten blob NENÍ stav před P15, ale před P13c")
zk(pre_za.count("for j, _ in zivy") == 0 and po_za.count("for j, _ in zivy") >= 2,
   "…a proto nelze dva výskyty H80 z gitu doložit — jsou jen v komentářích P15")

print("\n--- 5) soubory převedené na raw string: co se změnilo? ---------------")
for rel in SOUBORY_H79:
    kod, diff, err = git("-C", str(WS), "diff", "--unified=0", PRE, "ce49234", "--", rel)
    if kod != 0 or not diff.strip():
        zk(False, f"{rel}: mezi {PRE} a ce49234 NENÍ žádný rozdíl", err.strip()[:60])
        continue
    zmeny = [l for l in diff.splitlines()
             if (l.startswith("+") or l.startswith("-"))
             and not l.startswith(("+++", "---"))]
    print(f"  {rel}: {len(zmeny)} změněných řádků")
    for l in zmeny[:8]:
        print(f"      {l[:96]}")
    # obsah KÓDU (AST bez docstringů) musí být shodný
    _, pre_t, _ = git("-C", str(WS), "show", f"{PRE}:{rel}")
    po_t = (WS / rel).read_text(encoding="utf-8", errors="replace")

    def bez_docstringu(t):
        strom = ast.parse(t)
        for n in ast.walk(strom):
            if isinstance(n, (ast.Module, ast.FunctionDef, ast.AsyncFunctionDef,
                              ast.ClassDef)) and n.body \
                    and isinstance(n.body[0], ast.Expr) \
                    and isinstance(n.body[0].value, ast.Constant) \
                    and isinstance(n.body[0].value.value, str):
                n.body[0].value.value = ""
        return ast.dump(strom, include_attributes=False)

    try:
        a, b = bez_docstringu(pre_t), bez_docstringu(po_t)
        zk(a == b, f"{rel}: KÓD (AST bez docstringů) je proti `{PRE}` SHODNÝ",
           "shodné" if a == b else "ROZEŠLO SE")
    except SyntaxError as e:
        zk(False, f"{rel}: nepodařilo se parsovat", str(e)[:60])

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)

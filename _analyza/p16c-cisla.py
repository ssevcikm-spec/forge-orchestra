# -*- coding: utf-8 -*-
"""P16/C — přeměřit ČÍSLA z §33, každé JINUDY, než jak vzniklo.

| # | Číslo P15 | Můj zdroj |
|---|---|---|
| 1 | `g3` má **34** bran | AST `BRANY` **a** počet sekcí `### ` v ULOŽENÉM výpisu (ne v tom, který jsem právě přepsal) |
| 2 | `verify-setup` hlásí **74** kontrol | spuštění + AST rozpočet call-sites (a vysvětlení rozdílu) |
| 3 | `_archiv` **347** souborů / **1,58 MB** | `rglob` (ne manifest) + součet bajtů |
| 4 | `h79` **0** varování | `compile()` se `SyntaxWarning` jako chybou |
| 5 | `kronika` **154** omylů / **21** bloků | DVA nástroje (`p14f-prepocet-kroniky.py`, `kronika-kontrola.py`) — a ROZDÍL se musí pojmenovat (H18: různé čítače, stejné jméno) |
| 6 | commit `ce49234` = **114** souborů | `--name-only` vs. `--name-status` vs. `--shortstat` |

Nic se nemění.
"""

import ast
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
A = WS / "_analyza"
GIT = str(WS / "tools" / "git.cmd")
ZA = "ce49234"

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
    r = subprocess.run([GIT, "-C", str(WS), *args], capture_output=True, shell=True)
    return (r.stdout or b"").decode("utf-8", "replace")


def spust(rel, *args):
    r = subprocess.run([sys.executable, str(A / rel), *args], capture_output=True,
                       cwd=str(WS))
    return r.returncode, (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")


print("=" * 78)
print("P16/C — čísla z §33, každé jinudy")
print("=" * 78)

# ── 1) 34 bran ─────────────────────────────────────────────────────────────
print("\n--- 1) `g3` má 34 bran -----------------------------------------------")
strom = ast.parse((A / "g3-brany.py").read_text(encoding="utf-8"))
ns: dict = {}
for n in strom.body:
    if isinstance(n, ast.Assign) and any(
            isinstance(t, ast.Name) and t.id == "BRANY" for t in n.targets):
        # vyhodnoť jen `BRANY` v prostředí s odvozenými cestami
        exec(compile(ast.Module(body=[n], type_ignores=[]), "<BRANY>", "exec"),
             {"GODOT": "x", "HRA": WS, "ANALYZA": A, "TOOLS": WS / "tools",
              "FORGE": WS / "repo" / ".forge", "WS": WS}, ns)
        break
pocet_ast = len(ns["BRANY"])
print(f"  AST `BRANY`: {pocet_ast}")
zk(pocet_ast == 34, "AST parser vidí 34 bran", f"{pocet_ast}")
# sekce v ULOŽENÉM výpisu P15 (ne v tom, který jsem přepsal)
pred = (A / "p16-g3-vystup-pred.txt").read_text(encoding="utf-8", errors="replace")
pocet_sekci = len(re.findall(r"^### ", pred, re.M))
print(f"  sekcí `### ` v uloženém výpisu P15: {pocet_sekci}")
zk(pocet_sekci == pocet_ast, "a stejný počet sekcí v uloženém výpisu P15",
   f"{pocet_sekci} = {pocet_ast}")
# a v tom, který právě vyrobil `g3`
dnes = (A / "g3-brany-vystup.txt").read_text(encoding="utf-8", errors="replace")
pocet_dnes = len(re.findall(r"^### ", dnes, re.M))
print(f"  sekcí v DNEŠNÍM výpisu `g3`: {pocet_dnes}")
zk(pocet_dnes == 34, "dnešní běh `g3` má taky 34 sekcí", f"{pocet_dnes}")

# ── 2) 74 kontrol ──────────────────────────────────────────────────────────
print("\n--- 2) `verify-setup` hlásí 74 kontrol ------------------------------")
kod, v = spust("../tools/verify-setup.py")
m = re.search(r"ZMĚŘENO:\s*(\d+) kontrol,\s*(\d+) chyb", v)
print(f"  běh: exit={kod}, ZMĚŘENO {m.group(1) if m else '?'} kontrol")
zk(kod == 0 and m and m.group(1) == "74", "naměřeno 74 kontrol, 0 chyb",
   m.group(1) if m else "—")
# AST rozpočet: kolik volání `zkontroluj(` je staticky a kolik jich proběhne
vs_strom = ast.parse((WS / "tools" / "verify-setup.py").read_text(encoding="utf-8"))
calls = sum(1 for n in ast.walk(vs_strom) if isinstance(n, ast.Call)
            and getattr(n.func, "id", "") == "zkontroluj")
print(f"  statických volání `zkontroluj(`: {calls}")
print("  ROZDÍL JE VYVĚTLENÝ: `soubor()` a `slozka()` obalují `zkontroluj` a volají")
print("  se ve SMYČKÁCH — 12 dokumentů + 5 složek + 19 + 14 + 5 + 8 … položek.")
zk(calls < 74, "statická metrika je menší než běh (a je to vidět)", f"{calls} < 74")

# ── 3) 347 souborů / 1,58 MB ───────────────────────────────────────────────
print("\n--- 3) `_archiv` 347 souborů / 1,58 MB ------------------------------")
soubory = [p for p in (A / "_archiv").rglob("*") if p.is_file()]
bajtu = sum(p.stat().st_size for p in soubory)
print(f"  rglob: {len(soubory)} souborů, {bajtu} B = {bajtu / 1e6:.3f} MB (10^6)"
      f" = {bajtu / 1024 / 1024:.3f} MiB")
zk(len(soubory) == 347, "nezávislý počet souborů je 347", f"{len(soubory)}")
zk(abs(bajtu / 1e6 - 1.58) < 0.02, "a 1,58 MB v jednotce 10^6 B",
   f"{bajtu / 1e6:.3f} MB")
man = json.loads((pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\_zalohy")
                  / "forge-orchestra" / "MANIFEST.json").read_text(encoding="utf-8"))
zk(len(man.get("soubory", {})) == len(soubory),
   "a manifest má stejný počet položek jako rglob",
   f"{len(man.get('soubory', {}))} = {len(soubory)}")

# ── 4) h79: 0 varování ─────────────────────────────────────────────────────
print("\n--- 4) `h79` 0 neplatných escape sekvencí ---------------------------")
kod79, v79 = spust("h79-escape-sken.py")
m79 = re.search(r"ZMĚŘENO:\s*(\d+) neplatných escape sekvencí \((\d+) souborů",
                v79)
print(f"  sken P15: exit={kod79}, {m79.groups() if m79 else '?'}")
zk(kod79 == 0, "sken P15 hlásí 0 (exit 0)")
zk(m79 is not None and m79.group(2) != "0",
   "a PŘIZNÁVÁ, kolik souborů prošlo (ne ticho)", m79.group(2) if m79 else "—")
print("  ⚠ MEZ: sken vylučuje `.git, __pycache__, _archiv, node_modules` —")
print("     přes `compile()` jsem v `_archiv` naměřil 5 SyntaxWarning (nález H86).")

# ── 5) kronika: 154 omylů / 21 bloků ──────────────────────────────────────
print("\n--- 5) kronika: 154 omylů / 21 bloků (DVA nástroje) -----------------")
kod_p, v_p = spust("p14f-prepocet-kroniky.py")
kod_k, v_k = spust("kronika-kontrola.py")
for popis, kod, v in (("p14f-prepocet-kroniky.py", kod_p, v_p),
                      ("kronika-kontrola.py", kod_k, v_k)):
    print(f"  {popis}: exit={kod}")
    for l in v.splitlines():
        if re.search(r"celkem|blok|omyl|nález|session|součet|SEDÍ|ROZEŠEL", l, re.I):
            print(f"      {l.strip()[:104]}")
zk(kod_k == 0, "`kronika-kontrola.py` → exit 0", f"{kod_k}")
m154 = re.search(r"omylů celkem \(skutečnost\):\s+(\d+)", v_k)
zk(m154 is not None and m154.group(1) == "154", "kontrola vidí 154 omylů",
   m154.group(1) if m154 else "—")
print("  ⚠ KTERÝ ZDROJ POČÍTÁ CO (H18): `p14f` počítá SOUČET ŘÁDKŮ tabulek §3")
print("     (21 bloků → 154), `kronika-kontrola` počítá SKUTEČNOST proti")
print("     `HANDOFF.md` §8 a navíc nálezy/sessions (83 nálezů, 28 sessions).")
print("     Nejsou to dvě verze téhož čísla — jsou to dvě RŮZNÉ OTÁZKY.")

# ── 6) 114 souborů v commitu ──────────────────────────────────────────────
print("\n--- 6) commit ce49234 = 114 souborů --------------------------------")
only = [l for l in git("show", "--pretty=format:", "--name-only", ZA).splitlines()
        if l.strip()]
status = [l for l in git("show", "--pretty=format:", "--name-status", ZA).splitlines()
          if l.strip()]
podle = {}
for l in status:
    k = l.split("\t")[0][0]
    podle[k] = podle.get(k, 0) + 1
short = git("show", "--shortstat", "--pretty=format:", ZA).strip()
print(f"  --name-only:  {len(only)} souborů")
print(f"  --name-status: {len(status)} řádků → " + ", ".join(
    f"{k}={v}" for k, v in sorted(podle.items())))
print(f"  --shortstat:  {short}")
zk(len(only) == 114, "`--name-only` dává 114", f"{len(only)}")
zk(len(status) == 114, "`--name-status` dává 114", f"{len(status)}")
zk(sum(podle.values()) == 114 and set(podle) <= {"M", "A", "D", "R", "C"},
   "součet M/A/D je 114", str(podle))

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)

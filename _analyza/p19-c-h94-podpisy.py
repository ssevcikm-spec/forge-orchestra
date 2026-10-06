# -*- coding: utf-8 -*-
r"""P19 — Úkol C (nález H94): KTERÉ podpisy chybějícího souboru jsou ŽIVÉ.

ZADÁNÍ: „Přeměř to sám — spusť `python` i `node` nad neexistující cestou
a porovnej SKUTEČNÝ výstup se seznamem. Nevěř P18."

PROČ TAKHLE: seznam 8 podpisů v `g3-brany.py` rozhoduje o tom, jestli se brána
vykáže jako „VŮBEC NEZAČALA" (třetí stav), nebo jako „běžela". Mrtvý podpis
v seznamu vypadá jako pokrytí a nechytá nic.

Skript dělá tři věci:
  1) spustí SKUTEČNÉ interprety nad neexistující cestou a vypíše, které podpisy
     v jejich výstupu skutečně jsou (a které ne) — proti CELÉMU seznamu,
  2) ověří tvrzení zadání, že `can't open file` a `No such file or directory`
     chytají TENTÝŽ případ (oba v jednom výstupu),
  3) přes ŽIVÝ `g3-brany.py` (jako zdroj, vymění se jen `BRANY`) změří, co která
     mutace seznamu udělá s KLASIFIKACÍ — včetně toho, že odebrání JEDNOHO
     z dvojice nic nezmění a odebrání VŠECH živých změní.

Živý `g3-brany.py` se NEMUTUJE — pracuje se na kopii v `_analyza/p19-scratch/`.
Použití: python _analyza/p19-c-h94-podpisy.py
"""

import ast
import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
SCRATCH = ANALYZA / "p19-scratch"
FIX = SCRATCH / "c-fixtury"
HARNESS = SCRATCH / "p19-c-harness.py"
CHYBEJICI = FIX / "neexistuje.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def bez_komentaru(text: str) -> str:
    """KÓD bez komentářů a docstringů — kontrola nesmí číst popis vady."""
    strom = ast.parse(text)
    for uzel in ast.walk(strom):
        if isinstance(uzel, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef,
                             ast.Module)) and uzel.body:
            d = uzel.body[0]
            if (isinstance(d, ast.Expr) and isinstance(d.value, ast.Constant)
                    and isinstance(d.value.value, str)):
                d.value.value = ""
    return ast.unparse(strom)


def podpisy_ze_zdroje(text: str):
    """Přečte n-tici `_PODPIS_CHYBEJICIHO_SOUBORU` (formátování nerozhoduje)."""
    m = re.search(r"_PODPIS_CHYBEJICIHO_SOUBORU = (\(.*?\n\))\n", text, re.S)
    return list(ast.literal_eval(m.group(1))) if m else []


def nahrad_seznam(text: str, nove) -> str:
    """Přepíše CELÝ seznam podpisů (řádkové mazání nefunguje — 3 na řádku)."""
    m = re.search(r"_PODPIS_CHYBEJICIHO_SOUBORU = \(.*?\n\)\n", text, re.S)
    novy = ("_PODPIS_CHYBEJICIHO_SOUBORU = (\n"
            + "".join(f'    "{p}",\n' for p in nove) + ")\n")
    return text[:m.start()] + novy + text[m.end():]


print("=" * 78)
print("P19/C — H94: které podpisy chybějícího souboru jsou na této stanici ŽIVÉ")
print("=" * 78)

zdroj = G3.read_text(encoding="utf-8")
hash_pred = hashlib.sha256(G3.read_bytes()).hexdigest()
podpisy = podpisy_ze_zdroje(zdroj)
zk(len(podpisy) >= 2, "ze živého g3 se přečetl seznam podpisů z KÓDU",
   f"{len(podpisy)}: {podpisy}")
# ⚠ Tohle je PO ROZHODNUTÍ (P19 seznam zúžil): invariantem je, že v seznamu
# NENÍ ani jeden mrtvý podpis. Kdyby se v budoucnu přidal, spadne to tady.
ZNAME_MRTVE = ["no such file or directory", "WinError 2",
               "The system cannot find the file", "is not recognized"]

# ── 1) SKUTEČNÉ VÝSTUPY INTERPRETŮ ────────────────────────────────────────
print("\n--- 1) skutečné výstupy interpretů nad NEEXISTUJÍCÍ cestou ---------")
FIX.mkdir(parents=True, exist_ok=True)
CHYBEJICI.unlink(missing_ok=True)          # ať je opravdu neexistující

prikazy = {
    "python <chybí>.py": [sys.executable, "-B", str(CHYBEJICI)],
    "node <chybí>.js": ["node", str(CHYBEJICI)],
    "node -e require(<chybí>)": ["node", "-e", f"require({str(CHYBEJICI)!r})"],
    "python -c import <chybí modul>": [sys.executable, "-c",
                                       "import p19_neexistujici_modul"],
    # PowerShell a cmd sem patří proto, aby se DALO změřit, že „is not recognized"
    # ani „The system cannot find the file" z interpretů níž nepochází.
    "powershell <chybí>": ["powershell", "-NoProfile", "-Command",
                           str(CHYBEJICI)],
    "cmd /c <chybí>": ["cmd", "/c", str(CHYBEJICI)],
}
vystupy = {}
for jmeno, cmd in prikazy.items():
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8",
                           errors="replace", timeout=120)
        vystupy[jmeno] = {"exit": r.returncode,
                          "text": (r.stdout or "") + (r.stderr or "")}
    except Exception as e:                                        # noqa: BLE001
        vystupy[jmeno] = {"exit": None, "text": f"<nepodařilo se spustit: {e}>"}

zk(len(vystupy) >= 4, "spustilo se víc než 3 příkazy", f"{len(vystupy)}")
zk(all(v["exit"] is not None for v in vystupy.values()),
   "každý příkaz se SKUTEČNĚ spustil (žádné tiché přeskočení)",
   ", ".join(f"{k}={v['exit']}" for k, v in vystupy.items()))

print("\n  naměřené výstupy (první 2 řádky):")
for jmeno, v in vystupy.items():
    prvni = [l for l in v["text"].splitlines() if l.strip()][:2]
    print(f"    {jmeno}  (exit={v['exit']})")
    for l in prvni:
        print(f"        {l.strip()[:110]}")

print("\n--- 2) KTERÉ PODPISY SE V KTERÉM VÝSTUPU OBJEVUJÍ ------------------")
zive, mrtve = [], []
for p in podpisy:
    kde = [jmeno for jmeno, v in vystupy.items() if p in v["text"]]
    (zive if kde else mrtve).append(p)
    print(f"    {'ŽIVÝ ' if kde else 'MRTVÝ'} {p!r:44} {', '.join(kde) if kde else ''}")
print(f"    → živých {len(zive)}, mrtvých {len(mrtve)}")
zk(len(zive) >= 1, "aspoň jeden podpis je ŽIVÝ (seznam není celý mrtvý)", f"{zive}")
# ── ROZHODNUTÍ P19: v seznamu nesmí zůstat mrtvý podpis ───────────────────
zk(not mrtve, "v SEZNAMU (kódu) nezůstal ani jeden MRTVÝ podpis",
   f"mrtvé v kódu: {mrtve if mrtve else 'žádné'}")
kod = bez_komentaru(zdroj)
zk(all(z not in kod for z in ZNAME_MRTVE),
   "odebrané podpisy NEJSOU v KÓDU (kontrola čte kód, ne komentář)",
   "kdyby byly v kódu, zúžení se neprovedlo")
zk(all(z in zdroj for z in ZNAME_MRTVE),
   "odebrané podpisy JSOU v textu POJMENOVANÉ (znalost se nesmazala)",
   f"hledám v komentáři: {ZNAME_MRTVE}")

# Tvrzení zadání: dvojice chytá TENTÝŽ případ.
python_vystup = vystupy["python <chybí>.py"]["text"]
dvojice = [p for p in ("can't open file", "No such file or directory")
           if p in python_vystup]
zk(len(dvojice) == 2,
   "TVRZENÍ ZADÁNÍ: `can't open file` i `No such file or directory` jsou v JEDNOM výstupu",
   f"oba ve výstupu pythonu: {dvojice}")
zk(not any(p in vystupy["python <chybí>.py"]["text"] for p in
           ("WinError 2", "The system cannot find the file", "is not recognized",
            "no such file or directory")),
   "zbylé 4 podpisy se ve výstupu PYTHONU neobjevují",
   "kdyby se objevily, nejsou mrtvé")

# ── 3) HARNESS: ŽIVÝ g3 JAKO ZDROJ, VYMĚNĚNÉ JEN `BRANY` ──────────────────
print("\n--- 3) sestavení harnessu ze ŽIVÉHO g3 -----------------------------")
(FIX / "c-a-bez-markeru.py").write_text(
    'print("P19: hotovo, vse na svem miste")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")
(FIX / "c-c-bez-vystupu.py").write_text("raise SystemExit(2)\n",
                                        encoding="utf-8", newline="\n")
ME_FIXTURY = '''BRANY = [
    ("C-fixtura A: exit=2 s VLASTNÍM hlášením BEZ markeru",
     ["python", "<ANALYZA>/p19-scratch/c-fixtury/c-a-bez-markeru.py"],
     r"(\\\\d+) kontrol"),
    ("C-fixtura C: exit=2 BEZ výstupu",
     ["python", "<ANALYZA>/p19-scratch/c-fixtury/c-c-bez-vystupu.py"],
     r"(\\\\d+) kontrol"),
    ("C-fixtura D: NEEXISTUJÍCÍ soubor",
     ["python", "<ANALYZA>/p19-scratch/c-fixtury/neexistuje.py"],
     r"(\\\\d+) kontrol"),
]
'''
m = re.search(r"^BRANY = \[.*?^\]\n", zdroj, re.M | re.S)
zk(m is not None, "v živém g3 se našel blok `BRANY`")
h = zdroj[:m.start()] + ME_FIXTURY + zdroj[m.end():]
h = h.replace('VYSTUP = ANALYZA / "g3-brany-vystup.txt"',
              'VYSTUP = ANALYZA / "p19-scratch" / "p19-c-harness-vystup.txt"')
# ⚠ OMyl 191 (naměřeno tady): harness leží v `_analyza/p19-scratch/`, takže jeho
# `WS = ...parents[1]` ukazuje na `_analyza`, ne na root repa — fixtures sice
# proběhly, ale souhrn spadl na `FileNotFoundError` a klasifikace vyšla PRÁZDNÁ
# (a každá mutace pak vypadala „odhalená"). Je to táž past, kterou má P18
# zapsanou u izolace (`worktree` musí ležet ve správné hloubce). Řešení: do
# KOPIE se vloží ABSOLUTNÍ root — kopie se tím liší od živého g3 jen tím, co
# test sám deklaruje.
h = h.replace("WS = pathlib.Path(__file__).resolve().parent.parent",
              f'WS = pathlib.Path(r"{WS}")')
zk(f'WS = pathlib.Path(r"{WS}")' in h,
   "harness má VLOŽENÝ absolutní root (cesty se neodvozují z jeho umístění)",
   str(WS))
zk(h != zdroj and h.count("C-fixtura") == 3,
   "harness má MOJE tři fixtury a liší se od živého g3",
   f"fixtur: {h.count('C-fixtura')}")
h = nahrad_seznam(h, podpisy)          # normalizuj formát seznamu
ast.parse(h)
zk(True, "harness se dá zkompilovat")


def spust_harness(text: str) -> dict:
    HARNESS.write_text(text, encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", str(HARNESS)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=900)
    o = (r.stdout or "") + (r.stderr or "")
    b1 = re.search(r"BRÁNY, KTERÉ VŮBEC NEZAČALY \(\d+\)[^\n]*\n(.*?)(?=\n\n|\Z)",
                   o, re.S)
    b2 = re.search(r"NEVYKÁZALY ČÍTAČ \(\d+\)[^\n]*\n(.*?)(?=\n\n|\Z)", o, re.S)
    return {"nezacaly": set(re.findall(r"^\s+(C-fixtura [A-D])", b1.group(1), re.M))
            if b1 else set(),
            "bez_citace": set(re.findall(r"^\s+(C-fixtura [A-D])", b2.group(1), re.M))
            if b2 else set(),
            "exit": r.returncode, "vystup": o}


ZDRAVY = {"nezacaly": {"C-fixtura C", "C-fixtura D"},
          "bez_citace": {"C-fixtura A"}}

print("\n--- 4) BĚH: klasifikace se SEZNAMEM, JAK JE DNES -------------------")
r0 = spust_harness(h)
print(f"    harness exit={r0['exit']}")
print(f"    nezačaly={sorted(r0['nezacaly'])}  bez_čitače={sorted(r0['bez_citace'])}")
if not (r0["nezacaly"] or r0["bez_citace"]):
    print("    --- výstup harnessu (posledních 25 řádků) ---")
    for l in r0["vystup"].strip().splitlines()[-25:]:
        print(f"      {l}")
# ⚠ GUARD (past „každá mutace je odhalena, když čtení nefunguje"): nejdřív se
# musí dokázat, že SE ČTE. Bez toho by prázdné množiny vypadaly jako nález.
zk(r0["exit"] == 0, "harness doběhl bez chyby", f"exit={r0['exit']}")
zk(bool(r0["nezacaly"] or r0["bez_citace"]),
   "ČTENÍ VÝSTUPU FUNGUJE — klasifikace není prázdná (jinak by každá mutace „prošla“)",
   f"nezačaly={sorted(r0['nezacaly'])}, bez_čitače={sorted(r0['bez_citace'])}")
zk(r0["nezacaly"] == ZDRAVY["nezacaly"],
   "dnešní seznam dává OČEKÁVANOU klasifikaci (C a D nezačaly)",
   f"{sorted(r0['nezacaly'])}")
zk(r0["bez_citace"] == ZDRAVY["bez_citace"],
   "fixtura A je ve třetím stavu (běžela, ale nevykázala čítač)",
   f"{sorted(r0['bez_citace'])}")

print("\n--- 5) MUTACE SEZNAMU (rozhoduje ZAŘAZENÍ, ne součet) --------------")
vysledky = {}
for jmeno, nove in [
        ("M1: odebrány VŠECHNY živé", [p for p in podpisy if p not in zive]),
        ("M2: odebrán JEN `can't open file`",
         [p for p in podpisy if p != "can't open file"]),
        ("M3: odebrán JEN `No such file or directory`",
         [p for p in podpisy if p != "No such file or directory"]),
]:
    h2 = nahrad_seznam(h, nove)
    zk(h2 != h, f"{jmeno} — text se SKUTEČNĚ změnil",
       f"podpisů {len(podpisy)} → {len(nove)}")
    r2 = spust_harness(h2)
    # ⚠ OMyl 192: srovnávat `sorted(list)` se `set` je VŽDY nepravda — první
    # verze proto hlásila „mutace odhalena" i tam, kde se nic nezměnilo.
    # Uvnitř se proto drží MNOŽINY, tiskne se setříděný seznam.
    vysledky[jmeno] = {"nezacaly": r2["nezacaly"],
                       "bez_citace": r2["bez_citace"]}
    print(f"    {jmeno}: nezačaly={sorted(r2['nezacaly'])}")

m1 = vysledky["M1: odebrány VŠECHNY živé"]
zk(m1["nezacaly"] != ZDRAVY["nezacaly"],
   "M1 je ODHALENA — bez živých podpisů se klasifikace změní",
   f"zdravý={sorted(ZDRAVY['nezacaly'])} vs M1={sorted(m1['nezacaly'])}")
zk("C-fixtura D" not in m1["nezacaly"],
   "M1 — fixtura D (chybějící soubor) propadne mezi „běžela\"",
   "to je přesně to slepé místo, které mrtvé podpisy předstírají")
for druhy in ("M2: odebrán JEN `can't open file`",
              "M3: odebrán JEN `No such file or directory`"):
    r = vysledky[druhy]
    zk(r["nezacaly"] == ZDRAVY["nezacaly"],
       f"{druhy} — klasifikace se NEZMĚNÍ (dvojice se kryje)",
       f"{sorted(r['nezacaly'])} vs zdravý {sorted(ZDRAVY['nezacaly'])}")

print("\n--- 6) ŽIVÝ g3 SE NESMÍ ZMĚNIT ------------------------------------")
hash_po = hashlib.sha256(G3.read_bytes()).hexdigest()
zk(hash_po == hash_pred, "živý `g3-brany.py` je bajt na bajt nezměněný", hash_po[:16])
HARNESS.unlink(missing_ok=True)

print("\n--- SOUHRN ---")
print(f"  ŽIVÉ podpisy ({len(zive)}): " + ", ".join(repr(p) for p in zive))
print(f"  MRTVÉ podpisy ({len(mrtve)}): " + ", ".join(repr(p) for p in mrtve))
chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

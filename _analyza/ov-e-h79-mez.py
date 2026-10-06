# OVĚŘOVACÍ session (P18) — Úkol E: MEZ SKENU H79.
#
# P17 tvrdí (H86): „ZMĚŘENO: 0 … ve SKENOVANÝCH 164 živých (mimo _archiv: 260
# souborů, 5 sekvencí)" a že nálezy v `_archiv` NEMĚNÍ `exit`.
#
# Ověřuje se TŘEMI věcmi:
#   1) VLASTNÍ počet souborů (Python walk) — souhlasí s číslem ve výstupu?
#   2) VLASTNÍ sken escape sekvencí (`ast.parse` + `warnings`) — souhlasí počty?
#   3) MUTACE OBĚMA SMĚRY: vlož vadný soubor do `_archiv` → `exit` se NESMÍ
#      změnit; vlož TOTÉŽ do živého stromu → `exit` se změnit MUSÍ.
#      Bez druhého směru by „exit se nezměnil" mohlo znamenat jen to, že sken
#      nález vůbec nevidí.
#
# ⚠ Vlastní omyl P18: `_archiv` je v `.gitignore`, takže do něj smím založit
# dočasný soubor a zase ho smazat — `git status` se přitom nezmění. Doklad
# (výpisy) jde do `_analyza/`, což JE verzované.
import ast
import hashlib
import json
import pathlib
import re
import subprocess
import sys
import warnings

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"E:\Workspaces\forge-orchestra")
HRA = pathlib.Path(r"E:\Workspaces\uo-shadows")
SKEN = WS / "_analyza" / "h79-escape-sken.py"
ARCHIV = WS / "_analyza" / "_archiv"
SKIP = {".git", "node_modules", "__pycache__"}

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


def spust_sken() -> tuple:
    v = subprocess.run([sys.executable, "-B", str(SKEN)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=1800)
    return v.returncode, (v.stdout or "") + (v.stderr or "")


def vytahni(out: str) -> dict:
    m = re.search(r"ZMĚŘENO:\s*(\d+)\s*neplatných escape sekvencí ve SKENOVANÝCH\s*"
                  r"(\d+)\s*živých souborech \(mimo `_archiv`:\s*(\d+)\s*souborů,\s*"
                  r"(\d+)\s*sekvencí\)", out)
    if not m:
        return {}
    return {"zive_sekvence": int(m.group(1)), "zive_souboru": int(m.group(2)),
            "archiv_souboru": int(m.group(3)), "archiv_sekvence": int(m.group(4))}


print("=" * 88)
print("E — MEZ SKENU H79 (P18, vlastní měřidlo)")
print("=" * 88)

# ── 1) VLASTNÍ POČET SOUBORŮ ──────────────────────────────────────────────
print("\n--- 1) VLASTNÍ POČET SOUBORŮ (Python walk, stejný filtr jako sken) ---")
vlastni = {}
for jm, koren in [("orchestra", WS), ("hra", HRA)]:
    z = a = 0
    for p in koren.rglob("*.py"):
        if any(c in SKIP for c in p.parts):
            continue
        if "_archiv" in p.parts:
            a += 1
        else:
            z += 1
    vlastni[jm] = {"zive": z, "archiv": a}
    print(f"    {jm:10} živých {z:4}   v _archiv {a:4}")
v_zive = sum(v["zive"] for v in vlastni.values())
v_arch = sum(v["archiv"] for v in vlastni.values())
print(f"    CELKEM     živých {v_zive:4}   v _archiv {v_arch:4}")

rc0, out0 = spust_sken()
c0 = vytahni(out0)
print("\n--- výstup skenu (hlášení s mezí) ---")
for r in out0.splitlines():
    if "ZMĚŘENO" in r or "prošlé" in r or "POZNÁMKA" in r:
        print("   ", r.strip())
kont("sken vypsal kanonický čítač s MEZÍ (H86)", bool(c0), f"{c0}")
kont("počet ŽIVÝCH souborů ve skenu == VLASTNÍ počet", c0.get("zive_souboru") == v_zive,
    f"sken={c0.get('zive_souboru')} vlastní={v_zive}")
kont("počet souborů v _archiv == VLASTNÍ počet", c0.get("archiv_souboru") == v_arch,
    f"sken={c0.get('archiv_souboru')} vlastní={v_arch}")
kont("mez je VIDĚT ve výstupu (vyloučení není tiché)",
    "mimo `_archiv`" in out0 and "živých souborech" in out0,
    "hlášení obsahuje obě čísla")

# ── 2) VLASTNÍ SKEN ESCAPE SEKVENCÍ ───────────────────────────────────────
print("\n--- 2) VLASTNÍ SKEN (ast.parse + warnings) ---")
vlastni_zive = []
vlastni_arch = []
for jm, koren in [("orchestra", WS), ("hra", HRA)]:
    for p in sorted(koren.rglob("*.py")):
        if any(c in SKIP for c in p.parts):
            continue
        try:
            text = p.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        with warnings.catch_warnings(record=True) as zaz:
            warnings.simplefilter("always")
            try:
                ast.parse(text, filename=str(p))
            except SyntaxError:
                continue
        for z in zaz:
            if issubclass(z.category, SyntaxWarning):
                (vlastni_arch if "_archiv" in p.parts else vlastni_zive).append(
                    (str(p.relative_to(koren.parent)), z.lineno or 0, str(z.message)))
print(f"    vlastní: živých sekvencí {len(vlastni_zive)}, "
      f"v _archiv {len(vlastni_arch)}")
for c, l, t in vlastni_zive:
    print(f"      ŽIVÝ  {c}:{l}  {t}")
kont("počet ŽIVÝCH sekvencí == čítač skenu", len(vlastni_zive) == c0.get("zive_sekvence"),
    f"vlastní={len(vlastni_zive)} sken={c0.get('zive_sekvence')}")
kont("počet sekvencí v _archiv == čítač skenu", len(vlastni_arch) == c0.get("archiv_sekvence"),
    f"vlastní={len(vlastni_arch)} sken={c0.get('archiv_sekvence')}")
kont("vlastní sken NĚCO vidí v _archiv (jinak by srovnání bylo 0==0 naprázdno)",
    len(vlastni_arch) > 0, f"{len(vlastni_arch)} sekvencí v _archiv")

# ── 3) MUTACE OBĚMA SMĚRY ─────────────────────────────────────────────────
print("\n--- 3) MUTACE: vadný soubor v `_archiv` vs v ŽIVÉM stromě ---")
# Vadný soubor = `from __future__` na špatném místě → SyntaxError při parsování.
VADNY = ('"""P18 docasny mutant."""\n'
         "import os\n"
         "from __future__ import annotations\n")
# Druhý druh vady: neplatná escape sekvence → SyntaxWarning (to je to, co H79 měří).
VADNY_WARN = ('"""P18 docasny mutant s neplatnou escape sekvenci."""\n'
              'X = "C:\\Users\\nekdo\\cesta"\n')
# BOM na začátku → `ast.parse` textu s U+FEFF spadne (to byl nález P17).
VADNY_BOM = "\ufeff" + '"""P18 docasny mutant s BOM."""\nX = 1\n'

mut_arch = ARCHIV / "ov-e-mutant-archiv.py"
ARCHIV.mkdir(parents=True, exist_ok=True)
mut_arch.write_text(VADNY_BOM, encoding="utf-8", newline="\n")
print(f"    založen (do _archiv, gitignorováno): {mut_arch.name}")
rc1, out1 = spust_sken()
c1 = vytahni(out1)
print(f"    exit={rc1}  čítač={c1}")
kont("vadný soubor v `_archiv` NEMĚNÍ exit (zůstává 0)", rc1 == 0,
    f"exit={rc1} (zdravý stav {rc0})")
kont("vadný soubor v `_archiv` se PŘESTO VYPÍŠE (není tichý)",
    "nedalo" in out1 or "zpracovat" in out1 or c1.get("archiv_souboru") == v_arch + 1,
    f"archiv_souboru {c0.get('archiv_souboru')} → {c1.get('archiv_souboru')}")
kont("sken si vadného souboru v `_archiv` VŠIML (počet souborů stoupl)",
    c1.get("archiv_souboru") == v_arch + 1,
    f"{v_arch} → {c1.get('archiv_souboru')}")

# Teď TOTÉŽ do živého stromu — exit se změnit MUSÍ (jinak sken neměří nic).
mut_ziv = WS / "_analyza" / "ov-e-mutant-zivy.py"
mut_ziv.write_text(VADNY_WARN, encoding="utf-8", newline="\n")
print(f"    založen (živý strom): {mut_ziv.name}")
rc2, out2 = spust_sken()
c2 = vytahni(out2)
print(f"    exit={rc2}  čítač={c2}")
kont("TOTÉŽ ve ŽIVÉM stromě exit MĚNÍ (sken má jak selhat)", rc2 != 0,
    f"exit={rc2}")
kont("a nález je POJMENOVANÝ", "ov-e-mutant-zivy.py" in out2,
    "hledám jméno souboru ve výstupu")
kont("souborů v _archiv se to netýkalo (izolace přihrádek)",
    c2.get("archiv_souboru") == v_arch + 1, f"{c2.get('archiv_souboru')}")
mut_ziv.unlink()

# A ještě BOM ve ŽIVÉM stromě (P17 tvrdila, že BOM v `_archiv` dřív shazoval exit).
mut_bom = WS / "_analyza" / "ov-e-mutant-bom.py"
mut_bom.write_text(VADNY_BOM, encoding="utf-8", newline="\n")
rc3, out3 = spust_sken()
print(f"    BOM ve živém stromě: exit={rc3}")
kont("BOM v ŽIVÉM stromě je VADA (exit != 0)", rc3 != 0, f"exit={rc3}")
mut_bom.unlink()
mut_arch.unlink()

# ── 4) NÁVRAT DO ZDRAVÉHO STAVU ───────────────────────────────────────────
print("\n--- 4) NÁVRAT DO ZDRAVÉHO STAVU ---")
rc9, out9 = spust_sken()
c9 = vytahni(out9)
kont("po úklidu je sken zase ve zdravém stavu (exit 0)", rc9 == rc0, f"exit={rc9}")
kont("čítač je shodný s výchozím", c9 == c0, f"{c0} vs {c9}")
kont("žádný mutant nezůstal ve stromě",
    not mut_arch.exists() and not mut_ziv.exists() and not mut_bom.exists(),
    "oba dočasné soubory smazány")

print("\n" + "=" * 88)
print(f"VÝSLEDEK E: kontrol {kontrol}, chyb {chyb}")
print("=" * 88)
json.dump({"kontrol": kontrol, "chyb": chyb, "vlastni_pocty": vlastni,
           "vlastni_zive_sekvence": len(vlastni_zive),
           "vlastni_archiv_sekvence": len(vlastni_arch),
           "citac_zdravy": c0, "citac_archiv_mutant": c1,
           "citac_zivy_mutant": c2, "exit_zdravy": rc0,
           "exit_archiv_mutant": rc1, "exit_zivy_mutant": rc2},
          open(WS / "_analyza" / "ov-e-vysledky.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=2)
sys.exit(1 if chyb else 0)

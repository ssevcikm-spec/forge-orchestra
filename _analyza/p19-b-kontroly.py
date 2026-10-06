# -*- coding: utf-8 -*-
r"""P19 — Úkol B: DŮKAZ, ŽE ÚPRAVA BRÁNY NA32 MĚŘÍ SPRÁVNĚ (a ne tiše víc/míň).

Co se mění (P19): `n32-kompilovatelnost.py` nově vylučuje i `snapshot-*/`
(nález **H93**) a `*-scratch/` (nález **H98**) a KAŽDOU kategorii vykazuje
vlastním čítačem. Tenhle skript to ověřuje mutacemi OBĚMA SMĚRY:

  1) KONTROLNÍ stav: `exit 0` a čítače, které odpovídají NEZÁVISLÉMU počtu
     (vlastní walk) — ne hardcoded číslům.
  2) ČÍTAČ, KTERÝ ČTE P18: na nový souhrn se pustí DOSLOVNÝ regex z P18
     (`ov-c-n32-mutant.py`) — ověří se, KTERÝ výskyt trefí (past „který výskyt").
  3) MUTANT VE SNAPSHOTU → brána NESMÍ zčervenat, ale nález MUSÍ být VIDĚT.
  4) MUTANT VE SCRATCHI → totéž.
  5) MUTANT V ŽIVÉM STROMĚ → brána MUSÍ zčervenat a nález POJMENOVAT.
  6) VŠE ZPĚT BAJT NA BAJT (SHA-256) + brána zase zelená.
  7) BOM: měří se DVĚ RŮZNÉ OTÁZKY — „jde to spustit?" (`python`) vs.
     „je to zkompilovatelné?" (`compile`). Nález **H99** (zapsaný, neměněný).

Všechny oběti se vrací ve `finally` — i kdyby skript spadl uprostřed.
Použití: python _analyza/p19-b-kontroly.py
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
HRA = WS.parent / "uo-shadows"
BRANA = WS / "_analyza" / "n32-kompilovatelnost.py"
REPA = [("orchestra", WS), ("hra", HRA)]

# Oběti mutací — každá z JINÉ kategorie.
OBET_SNAPSHOT = WS / "_analyza" / "snapshot-20261002-181237" / "skill" / "overovani" / "zmen.py"
OBET_SCRATCH = WS / "_analyza" / "a-ukol-scratch" / "ov-d-fixtury" / "ovd-c-bez-vystupu.py"
FIXTURA_ZIVA = WS / "_analyza" / "p19-b-fixtura-ziva.py"
FIXTURA_BOM = WS / "_analyza" / "p19-b-fixtura-bom.py"

VLOZEK = "from __future__ import annotations\n"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def spust_branu():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=600)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def cisla(vystup: dict) -> dict:
    """Přečte VŠECHNY čítače nového souhrnu (pojmenovanými vzory)."""
    m = re.search(
        r"ZMĚŘENO:\s*(?P<souboru>\d+)\s*souborů,\s*(?P<nalezu>\d+)\s*nekompilovatelných,"
        r"\s*(?P<archiv>\d+)\s*vyloučeno\s*\(_archiv\),"
        r"\s*(?P<snap>\d+)\s*vyloučeno\s*\(snapshot-\*\),"
        r"\s*(?P<scratch>\d+)\s*vyloučeno\s*\(\*-scratch\)", vystup)
    if not m:
        return {}
    return {k: int(v) for k, v in m.groupdict().items()}


def p18_vyloucene(vystup: str):
    """DOSLOVNÝ regex z P18 (`ov-c-n32-mutant.py`), ať se ví, co P18 přečte."""
    m = re.search(r"ZMĚŘENO:\s*(\d+)\s*souborů,\s*(\d+)\s*nekompilovatelných,"
                  r"\s*(\d+)\s*vyloučeno", vystup)
    return int(m.group(3)) if m else None


def vlastni_pocet(predikat) -> int:
    """Nezávislý počet `.py` (vlastní walk) pro kategorii."""
    n = 0
    for _, koren in REPA:
        for p in koren.rglob("*.py"):
            if ".git" in set(p.parts):
                continue
            if predikat(p):
                n += 1
    return n


def zmutuj(p: pathlib.Path):
    """Vloží `from __future__` ZA první SKUTEČNÝ PŘÍKAZ — vada H85 (jako P17/P18).

    ⚠ OMyl 190 (naměřeno tady): první verze brala první řádek, který nezačíná
    `#` ani třemi uvozovkami — jenže řádek UVNITŘ docstringu taky nezačíná,
    takže se mutace vložila DO ŘETĚZCE a **vůbec se neprojevila** (`compile`
    ji přijal). Test pak „prošel" ze špatného důvodu. Správně se bere první
    TOP-LEVEL příkaz z `ast` (ne docstring) a vkládá se za jeho `end_lineno`.
    Pojistka zůstává: `compile` musí mutant ODMÍTNOUT, jinak to test hlásí
    jako chybu (mutace, která se tiše neprovede, tvrdí totéž co ta, co projde).
    Vrací (puvodni_bajty, popis|None).
    """
    puvodni = p.read_bytes()
    zdroj = puvodni.decode("utf-8")
    radky = zdroj.splitlines(keepends=True)
    strom = ast.parse(zdroj, str(p))
    prikazy = [n for n in strom.body
               if not (isinstance(n, ast.Expr) and isinstance(n.value, ast.Constant)
                       and isinstance(n.value.value, str))]
    if not prikazy:
        return puvodni, None
    konec = prikazy[0].end_lineno                 # 1-based poslední řádek příkazu
    move = "".join(radky[:konec] + [VLOZEK] + radky[konec:])
    # ⚠ Mutace se musí SKUTEČNĚ projevit — jinak tvrdí totéž co slepá mutace.
    ast_prijme = True
    try:
        ast.parse(move, str(p))
    except SyntaxError:
        ast_prijme = False
    try:
        compile(move, str(p), "exec")
        comp_odmitne = False
    except SyntaxError:
        comp_odmitne = True
    p.write_bytes(move.encode("utf-8"))
    popis = (f"vloženo za řádek {konec} ({radky[konec - 1].strip()[:40]!r}); "
             f"ast.parse přijme={ast_prijme}, compile odmítne={comp_odmitne}")
    return puvodni, (popis, ast_prijme, comp_odmitne)


def vrat(p: pathlib.Path, puvodni: bytes) -> str:
    p.write_bytes(puvodni)
    return hashlib.sha256(p.read_bytes()).hexdigest()


print("=" * 78)
print("P19/B — ověření úpravy brány NA32 (H93 snapshot-* + H98 *-scratch)")
print("=" * 78)

snap_walk = vlastni_pocet(lambda p: any(re.search(r"^snapshot-\d", c) for c in p.parts))
scr_walk = vlastni_pocet(lambda p: any(re.search(r".*-scratch$", c) for c in p.parts))

# ── 1) KONTROLNÍ STAV ─────────────────────────────────────────────────────
print("\n--- 1) kontrolní stav (zdravý strom) -------------------------------")
rc0, v0 = spust_branu()
c0 = cisla(v0)
zk(rc0 == 0, "zdravý strom → exit 0", f"exit={rc0}")
zk(bool(c0), "souhrn má VŠECHNY tři vylučovací čítače", f"{c0}")
zk(c0.get("snap") == snap_walk,
   "čítač `snapshot-*` == nezávislý walk", f"brána={c0.get('snap')} walk={snap_walk}")
zk(c0.get("scratch") == scr_walk,
   "čítač `*-scratch` == nezávislý walk", f"brána={c0.get('scratch')} walk={scr_walk}")
zk(c0.get("souboru", 0) > 0, "brána měřila NENULOVÝ počet živých souborů",
   f"živých={c0.get('souboru')}")
vsechny_walk = vlastni_pocet(lambda p: True)      # všechny .py mimo `.git`
zk(c0.get("souboru", 0) + c0.get("snap", 0) + c0.get("scratch", 0)
   == vsechny_walk - c0.get("archiv", 0),
   "součet čítačů (živé + snapshot + scratch) == nezávislý počet mimo `_archiv`",
   f"{c0.get('souboru', 0)} + {c0.get('snap', 0)} + {c0.get('scratch', 0)} "
   f"= {c0.get('souboru', 0) + c0.get('snap', 0) + c0.get('scratch', 0)}; "
   f"walk {vsechny_walk} − _archiv {c0.get('archiv', 0)} = "
   f"{vsechny_walk - c0.get('archiv', 0)}")

# ── 2) CO Z TOHO PŘEČTE P18 ───────────────────────────────────────────────
print("\n--- 2) čítač, který čte P18 (doslovný regex) -----------------------")
p18 = p18_vyloucene(v0)
zk(p18 == c0.get("archiv"),
   "P18 regex trefí PRVNÍ `vyloučeno` = `_archiv` (ne jiný čítač)",
   f"P18 přečte {p18}, `_archiv` je {c0.get('archiv')}, "
   f"snapshot {c0.get('snap')}, scratch {c0.get('scratch')}")

# ── 3) MUTANT VE SNAPSHOTU ────────────────────────────────────────────────
print("\n--- 3) mutant ve SNAPSHOTU (nesmí zčervenat) -----------------------")
puv_snap = None
sha_snap_pred = hashlib.sha256(OBET_SNAPSHOT.read_bytes()).hexdigest()
try:
    puv_snap, popis = zmutuj(OBET_SNAPSHOT)
    zk(popis is not None, "mutace se provedla", popis[0] if popis else "—")
    if popis:
        zk(popis[1] and popis[2], "mutant je případ, kde se ast.parse a compile LIŠÍ", popis[0])
    rc1, v1 = spust_branu()
    c1 = cisla(v1)
    zk(rc1 == 0, "brána zůstala ZELENÁ (exit 0) — snapshot není živý kód", f"exit={rc1}")
    zk(c1.get("snap") == snap_walk, "čítač `snapshot-*` se nezměnil",
       f"{c1.get('snap')} vs {snap_walk}")
    rel = str(OBET_SNAPSHOT.relative_to(WS))
    zk(rel in v1, "nález je VIDĚT v poznámce (vyloučení není tiché)", rel)
    zk(c1.get("nalezu") == c0.get("nalezu"),
       "počet ŽIVÝCH nálezů se nezměnil", f"{c1.get('nalezu')} vs {c0.get('nalezu')}")
finally:
    if puv_snap is not None:
        h = vrat(OBET_SNAPSHOT, puv_snap)
        zk(h == sha_snap_pred, "snapshot vrácen BAJT NA BAJT (SHA-256 shodný)",
           f"{h[:16]}… vs {sha_snap_pred[:16]}…")

# ── 4) MUTANT VE SCRATCHI ─────────────────────────────────────────────────
print("\n--- 4) mutant ve SCRATCHI (nesmí zčervenat) ------------------------")
puv_scr = None
sha_scr_pred = hashlib.sha256(OBET_SCRATCH.read_bytes()).hexdigest()
try:
    puv_scr, popis = zmutuj(OBET_SCRATCH)
    zk(popis is not None, "mutace se provedla", popis[0] if popis else "—")
    rc2, v2 = spust_branu()
    c2 = cisla(v2)
    zk(rc2 == 0, "brána zůstala ZELENÁ (exit 0) — pracovní kopie není živý kód",
       f"exit={rc2}")
    zk(c2.get("scratch") == scr_walk, "čítač `*-scratch` se nezměnil",
       f"{c2.get('scratch')} vs {scr_walk}")
    rel = str(OBET_SCRATCH.relative_to(WS))
    zk(rel in v2, "nález je VIDĚT v poznámce", rel)
finally:
    if puv_scr is not None:
        h = vrat(OBET_SCRATCH, puv_scr)
        zk(h == sha_scr_pred, "scratch vrácen BAJT NA BAJT (SHA-256 shodný)",
           f"{h[:16]}… vs {sha_scr_pred[:16]}…")

# ── 5) MUTANT V ŽIVÉM STROMĚ ──────────────────────────────────────────────
print("\n--- 5) mutant v ŽIVÉM stromě (MUSÍ zčervenat) ----------------------")
FIXTURA_ZIVA.write_text("import sys\nprint('fixtura P19')\n", encoding="utf-8")
try:
    _, popis = zmutuj(FIXTURA_ZIVA)
    rc3, v3 = spust_branu()
    c3 = cisla(v3)
    zk(rc3 == 1, "brána ZČERVENALA (exit 1, ne 2)", f"exit={rc3}")
    zk(FIXTURA_ZIVA.name in v3, "nález je POJMENOVANÝ",
       f"hledám {FIXTURA_ZIVA.name}")
    zk(c3.get("nalezu") == c0.get("nalezu", 0) + 1, "počet živých nálezů stoupl o 1",
       f"{c3.get('nalezu')} vs {c0.get('nalezu')}")
    zk(c3.get("souboru") == c0.get("souboru", 0) + 1,
       "nový NETRACKOVANÝ živý soubor je vidět (past H52)",
       f"{c3.get('souboru')} vs {c0.get('souboru')}")
finally:
    FIXTURA_ZIVA.unlink(missing_ok=True)

# ── 6) BOM: DVĚ RŮZNÉ OTÁZKY ──────────────────────────────────────────────
print("\n--- 6) BOM: „jde spustit?“ vs „jde zkompilovat?“ (H99) ------------")
FIXTURA_BOM.write_bytes("\ufeffprint('BOM fixtura P19')\n".encode("utf-8"))
try:
    r = subprocess.run([sys.executable, str(FIXTURA_BOM)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace", timeout=120)
    zk(r.returncode == 0, "`python <soubor s BOM>` soubor SPUSTÍ (exit 0)",
       f"exit={r.returncode}, stdout={(r.stdout or '').strip()!r}")
    rc4, v4 = spust_branu()
    c4 = cisla(v4)
    zk(rc4 == 1 and FIXTURA_BOM.name in v4,
       "brána NA32 tentýž soubor hlásí jako NEKOMPILOVATELNÝ (exit 1)",
       f"exit={rc4}, jméno ve výstupu={FIXTURA_BOM.name in v4}")
    zk(c4.get("nalezu") == c0.get("nalezu", 0) + 1, "nálezů je o 1 víc",
       f"{c4.get('nalezu')} vs {c0.get('nalezu')}")
    print("      → DVĚ RŮZNÉ OTÁZKY: spustitelnost (ANO) vs kompilovatelnost (NE).")
    print("        Zapsáno jako H99; NEMĚNÍ se (rozhodnutí o BOM v .py je věc projektu).")
finally:
    FIXTURA_BOM.unlink(missing_ok=True)

# ── 7) NÁVRAT DO ZELENÉHO STAVU ───────────────────────────────────────────
print("\n--- 7) po úklidu musí být stav SHODNÝ s kontrolním ------------------")
rc5, v5 = spust_branu()
c5 = cisla(v5)
zk(rc5 == 0, "brána je zase ZELENÁ", f"exit={rc5}")
zk(c5 == c0, "VŠECHNY čítače jsou shodné s kontrolním stavem",
   f"{c5} vs {c0}")
zk(not FIXTURA_ZIVA.exists() and not FIXTURA_BOM.exists(),
   "dočasné fixtury jsou SMAZANÉ",
   f"{FIXTURA_ZIVA.name}={FIXTURA_ZIVA.exists()}, {FIXTURA_BOM.name}={FIXTURA_BOM.exists()}")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

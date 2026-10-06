# -*- coding: utf-8 -*-
r"""P19 — Úkol B (pokračování): DŮKAZ PRO BRÁNU H79 (`h79-escape-sken.py`).

PROČ ZVLÁŠŤ: při měření H93/H98 se ukázalo, že **stejnou díru má i H79** —
počítala jako „živé" i `snapshot-*/` a `*-scratch/`. Opraveno stejně jako NA32,
takže se to musí dokázat STEJNÝM postupem: mutant v kopii bránu **nesmí**
zčervenat, mutant v živém stromě **musí**.

Vada pro H79 = NEPLATNÁ ESCAPE SEKVENCE (`X = "\d"` → `SyntaxWarning`), tedy
přesně to, co brána hledá. Soubory se vrací ve `finally` a hash se POROVNÁVÁ
(ne jen vypisuje).
Použití: python _analyza/p19-b2-kontroly-h79.py
"""

import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
BRANA = WS / "_analyza" / "h79-escape-sken.py"
REPA = [("orchestra", WS), ("hra", HRA)]

OBET_SNAPSHOT = WS / "_analyza" / "snapshot-20261002-183213" / "skill" / "overovani" / "zmen.py"
OBET_SCRATCH = WS / "_analyza" / "a-ukol-scratch" / "ov-d-fixtury" / "ovd-a-bez-markeru.py"
FIXTURA_ZIVA = WS / "_analyza" / "p19-b2-fixtura-ziva.py"

# ⚠ Vada musí být NEPLATNÁ ESCAPE SEKVENCE — ne cokoli, co spadne. Kdyby se
# vložil řádek, který warning nevyrobí, mutant by se tiše neprojevil.
VADA = 'X_BOD = "\\d"\n'

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def spust():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=900)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


SNAP_RE = re.compile(r"^snapshot-\d")
SCRATCH_RE = re.compile(r".*-scratch$")


def pocet_walk(predikat) -> int:
    n = 0
    for _, koren in REPA:
        for p in koren.rglob("*.py"):
            casti = p.parts
            if any(c in {".git", "node_modules", "__pycache__"} for c in casti):
                continue
            if "_archiv" in casti:
                continue
            if predikat(casti):
                n += 1
    return n


def citac(vystup: str) -> dict:
    m = re.search(r"ZMĚŘENO:\s*(?P<nalezu>\d+)\s*neplatných escape sekvencí ve "
                  r"SKENOVANÝCH\s*(?P<zivych>\d+)\s*živých souborech"
                  r".*?`snapshot-\*`\s*(?P<snap>\d+)/(?P<snapsek>\d+)"
                  r".*?`\*-scratch`\s*(?P<scratch>\d+)/(?P<scrscratchsek>\d+)",
                  vystup, re.S)
    return {k: int(v) for k, v in m.groupdict().items()} if m else {}


def sekce(blok_vystup: str, nazev: str) -> str:
    """Vrátí text sekce '--- POZNÁMKA: `<nazev>` ...' (jen tělo)."""
    m = re.search(r"--- POZNÁMKA: `" + re.escape(nazev) + r"`[^\n]*\n(.*?)(?=\n\n|\Z)",
                  blok_vystup, re.S)
    return m.group(1) if m else ""


print("=" * 78)
print("P19/B2 — ověření úpravy brány H79 (H98: snapshot-* + *-scratch)")
print("=" * 78)

zivych_walk = pocet_walk(lambda c: not any(SNAP_RE.search(x) for x in c)
                         and not any(SCRATCH_RE.search(x) for x in c))
snap_walk = pocet_walk(lambda c: any(SNAP_RE.search(x) for x in c))
scr_walk = pocet_walk(lambda c: any(SCRATCH_RE.search(x) for x in c))

print("\n--- 1) kontrolní stav ----------------------------------------------")
rc0, v0 = spust()
c0 = citac(v0)
zk(rc0 == 0, "zdravý strom → exit 0", f"exit={rc0}")
zk(bool(c0), "kanonický čítač nese VŠECHNY kategorie", f"{c0}")
zk(c0.get("zivych") == zivych_walk, "počet živých souborů == nezávislý walk",
   f"brána={c0.get('zivych')} walk={zivych_walk}")
zk(c0.get("snap") == snap_walk and c0.get("scratch") == scr_walk,
   "počty snapshot/scratch == nezávislý walk",
   f"snap {c0.get('snap')}/{snap_walk}, scratch {c0.get('scratch')}/{scr_walk}")
zk(c0.get("nalezu") == 0, "ve živém stromě 0 nálezů", f"{c0.get('nalezu')}")

print("\n--- 2) mutant ve SNAPSHOTU (nesmí zčervenat) ----------------------")
puv = None
sha_pred = hashlib.sha256(OBET_SNAPSHOT.read_bytes()).hexdigest()
try:
    puv = OBET_SNAPSHOT.read_bytes()
    OBET_SNAPSHOT.write_bytes(puv + VADA.encode("utf-8"))
    zk(hashlib.sha256(OBET_SNAPSHOT.read_bytes()).hexdigest() != sha_pred,
       "mutace se SKUTEČNĚ provedla (hash se změnil)", f"{OBET_SNAPSHOT.name}")
    rc1, v1 = spust()
    c1 = citac(v1)
    zk(rc1 == 0, "brána zůstala ZELENÁ (exit 0)", f"exit={rc1}")
    zk(OBET_SNAPSHOT.name in sekce(v1, "snapshot-*"),
       "nález je VIDĚT v poznámce `snapshot-*` (není tichý)", OBET_SNAPSHOT.name)
    zk(c1.get("snapsek") == 1, "sekvencí ve snapshotu je 1", f"{c1.get('snapsek')}")
    zk(c1.get("nalezu") == 0, "ŽIVÝCH nálezů je pořád 0", f"{c1.get('nalezu')}")
finally:
    if puv is not None:
        OBET_SNAPSHOT.write_bytes(puv)
        h = hashlib.sha256(OBET_SNAPSHOT.read_bytes()).hexdigest()
        zk(h == sha_pred, "snapshot vrácen BAJT NA BAJT", f"{h[:16]}…")

print("\n--- 3) mutant ve SCRATCHI (nesmí zčervenat) -----------------------")
puv = None
sha_pred = hashlib.sha256(OBET_SCRATCH.read_bytes()).hexdigest()
try:
    puv = OBET_SCRATCH.read_bytes()
    OBET_SCRATCH.write_bytes(puv + VADA.encode("utf-8"))
    rc2, v2 = spust()
    c2 = citac(v2)
    zk(rc2 == 0, "brána zůstala ZELENÁ (exit 0)", f"exit={rc2}")
    zk(OBET_SCRATCH.name in sekce(v2, "*-scratch"),
       "nález je VIDĚT v poznámce `*-scratch`", OBET_SCRATCH.name)
    zk(c2.get("scrscratchsek") == 1, "sekvencí ve scratchi je 1",
       f"{c2.get('scrscratchsek')}")
finally:
    if puv is not None:
        OBET_SCRATCH.write_bytes(puv)
        h = hashlib.sha256(OBET_SCRATCH.read_bytes()).hexdigest()
        zk(h == sha_pred, "scratch vrácen BAJT NA BAJT", f"{h[:16]}…")

print("\n--- 4) mutant v ŽIVÉM stromě (MUSÍ zčervenat) ---------------------")
FIXTURA_ZIVA.write_bytes(('Y_BOD = 1\n' + VADA).encode("utf-8"))
try:
    rc3, v3 = spust()
    c3 = citac(v3)
    zk(rc3 == 1, "brána ZČERVENALA (exit 1)", f"exit={rc3}")
    zk(FIXTURA_ZIVA.name in v3, "nález je POJMENOVANÝ", FIXTURA_ZIVA.name)
    zk(c3.get("nalezu") == 1, "ŽIVÝCH nálezů je 1", f"{c3.get('nalezu')}")
    zk(c3.get("zivych") == zivych_walk + 1, "nový netrackovaný soubor je vidět (H52)",
       f"{c3.get('zivych')} vs {zivych_walk}")
    # Proti kontrole: i sám Python to hlásí (nezávislé měřidlo, ne jen brána).
    r = subprocess.run([sys.executable, "-W", "error::SyntaxWarning", "-c",
                        "import ast,pathlib;ast.parse(pathlib.Path(r'%s').read_text())"
                        % FIXTURA_ZIVA], capture_output=True, text=True,
                       encoding="utf-8", errors="replace", timeout=60)
    zk(r.returncode != 0, "nezávisle: `python -W error::SyntaxWarning` na tom souboru SPADNE",
       (r.stderr or "").strip().splitlines()[-1] if r.stderr else f"exit={r.returncode}")
finally:
    FIXTURA_ZIVA.unlink(missing_ok=True)

print("\n--- 5) po úklidu shodný stav ---------------------------------------")
rc4, v4 = spust()
c4 = citac(v4)
zk(rc4 == 0, "brána je zase ZELENÁ", f"exit={rc4}")
zk(c4 == c0, "čítače jsou shodné s kontrolním stavem", f"{c4} vs {c0}")
zk(not FIXTURA_ZIVA.exists(), "dočasná fixtura je SMAZANÁ")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

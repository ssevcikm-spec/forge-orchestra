# -*- coding: utf-8 -*-
r"""K7: DOKLAD — umí brána `_analyza/test-forge-new.mjs` vůbec spadnout?

PROČ TO EXISTUJE: session K6 přidala do generátoru `SKIP_SABLONOVE` (do nové hry
se neveze `priprava.test.mjs` ani jeho fixtura) a brána `test-forge-new.mjs` to
hlídá. **Jenže se nikdy neověřilo, že ta brána umí SPADNOUT** — nezávislý
verifikátor K7 to označil za NEOVĚŘENÉ. Doklad vrací do generátoru **přesně tu
vadu, kterou K6 opravila** (ignoruje `SKIP_SABLONOVE`), a měří, co brána udělá.

NAMĚŘENO 14. 10. 2026 (K7): kontrolní běh **25/25**, s vrácenou vadou
**23/25 + 2 pojmenované chyby** (`exit 1`), po návratu souboru `git status`
čistý. Soubor se vrací **bajt na bajt** (sha256 hlídá knihovna `_mutace.py`).

⚠ NENÍ V `g3` — vědomé rozhodnutí K7 (`HANDOFF.md` §73.3 bod 3 a §73.6 bod 8):
spuštění trvá minuty (generátor + Godot) a `g3` má 58 bran. Kdo ho tam chce,
přidá ho do `BRANY` v `_analyza/g3-brany.py` a **přeměří číslo v `AGENTS.md`**.

⚠ NESPOUŠTĚT současně s `g3` ani `validate-all` — mutuje ŽIVÝ `tools/forge-new.mjs`.

Použití: python _analyza/k7-mutace-generatoru.py
Exit: 0 = brána umí spadnout i po návratu zelená; 1 = doklad neprošel.
"""

import hashlib
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / "_analyza"))
from _mutace import mutuj  # noqa: E402

GEN = WS / "tools" / "forge-new.mjs"
GATE = WS / "_analyza" / "test-forge-new.mjs"
KOTVA = "if (SKIP_NAZVY.has(e.name) || SKIP_SABLONOVE.has(e.name)) continue;"


def spust_gate() -> tuple[int, str]:
    r = subprocess.run(["node", str(GATE)], cwd=str(WS),
                       capture_output=True, timeout=1800)
    return r.returncode, (r.stdout + r.stderr).decode("utf-8", "replace")


def souhrn(vystup: str) -> list[str]:
    return [l.strip() for l in vystup.splitlines()
            if "VYSLEDEK" in l or l.strip().startswith("CHYBA")][:8]


print("=" * 78)
print("K7: UMÍ BRÁNA `test-forge-new.mjs` SPADNOUT? (mutace SKIP_SABLONOVE)")
print("=" * 78)

kontroly = []

print("\n--- 1) kontrolní běh (zdravý generátor) ------------------------------------")
pred_hash = hashlib.sha256(GEN.read_bytes()).hexdigest()
k0, v0 = spust_gate()
print("exit:", k0)
for l in souhrn(v0):
    print("  ", l)
kontroly.append((k0 == 0, "zdravý generátor → brána zelená (exit 0)", k0))

print("\n--- 2) MUTACE: generátor ignoruje SKIP_SABLONOVE ---------------------------")
with mutuj(GEN, KOTVA, "if (SKIP_NAZVY.has(e.name)) continue;"):
    k1, v1 = spust_gate()
    print("exit:", k1)
    for l in souhrn(v1):
        print("  ", l)
kontroly.append((k1 == 1, "s vrácenou vadou → brána SPADNE (exit 1)", k1))
kontroly.append(("priprava.test.mjs" in v1,
                 "nález JMENUJE vrácenou vadu (priprava.test.mjs)", ""))

print("\n--- 3) po mutaci: soubor vrácen BAJT NA BAJT -------------------------------")
# ⚠ Porovnává se s hashem PŘED během, NE s `git status` proti HEAD: soubor je
# v pracovním stromě legitimně změněný (K7 v něm opravovala komentář), takže
# „špinavý proti HEAD" NENÍ vada. Zajímá nás jen to, že MUTACE nic nezměnila.
po_hash = hashlib.sha256(GEN.read_bytes()).hexdigest()
print(f"sha256 před: {pred_hash[:16]}…  po: {po_hash[:16]}…")
kontroly.append((po_hash == pred_hash,
                 "soubor je po mutaci shodný s tím, čím byl PŘED ní (sha256)", po_hash[:16]))

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST brány `_analyza/b5-over-tvrzeni.py` — Úkol 4 zadání.

CO TA BRÁNA DĚLÁ: ověřuje **nezávisle na `n8-zastarala-analyza.py`** pět tvrzení
analyzy `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` — a `exit 0` dá **jen tehdy, když
jsou zastaralá právě pět**. Je to tedy **počítadlo**, ne kontrola.

CO SE DOKAZUJE (`overovani` §3): že to počítadlo **umí spadnout**, když se
skutečnost změní. Do 2. 10. 2026 žádný mutační test neměla (naměřeno
`audit6-brany-mutace.py`: „Brány BEZ jakéhokoli důvodu: 10").

POSTUP:
  1. **KONTROLNÍ PŮL** — dnes musí projít (`exit 0`, `5 z 5`).
  2. **MUTACE** — v `orchestra/conductor/src/index.ts` se **přejmenuje
     identifikátor** `filesInOriginMain` (na `filesInOriginMainXX`) **na všech
     výskytech**. Tím tvrzení č. 3 („`roadmap.status='done'` se neověřuje proti
     `origin/main`") **přestane být zastaralé** → zastaralých bude **4** →
     brána musí skončit **nenulově**.
  3. **NÁVRAT** — `try/finally` vrátí soubor **bajt po bajtu**.

⚠ PROČ PŘEJMENOVAT VŠECHNY VÝSKYTY (a je to naměřená past — omyl **18**):
  kdyby se přejmenoval jen jeden, v souboru by **zůstal podřetězec**
  `filesInOriginMain` (uvnitř `filesInOriginMainXX`) a brána by hledala
  **podřetězec** → rozdíl by **neviděla** a test by tvrdil „brána je slepá",
  ačkoli by měřil neprovedenou mutaci.
  Používá se proto `re.sub` s **hranicí slova** a ověřuje se, že v souboru
  po mutaci **není ani jeden** výskyt.

⚠ PROČ SE NEMUTUJE `git checkout`EM: `index.ts` má **necommitnuté změny**
  (naměřeno: `M tools/kontrola-diakritiky.py` v `orchestra`, a `index.ts` je
  součástí živé práce) — `git checkout` by je **smazal**.

Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza\b5-mutace.py
Návrat:   0 = brána měří | 1 = neměří (a vypíše, co konkrétně)
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "b5-over-tvrzeni.py"
CIL = WS / "orchestra" / "conductor" / "src" / "index.ts"

assert BRANA.is_file(), "brána %s není" % BRANA
assert CIL.is_file(), "soubor %s není" % CIL

IDENT = "filesInOriginMain"
# ⚠ NOVÉ JMÉNO NESMÍ OBSAHOVAT TO STARÉ — a to je **naměřená past** (omyl
# **18**, 2. 10. 2026), do které tenhle test **spadl napoprvé**:
# první verze přejmenovala na `filesInOriginMainXX` — jenže brána se ptá
# **podřetězcem** (`"filesInOriginMain" in KOD`) a `filesInOriginMainXX`
# ten podřetězec **obsahuje** → verdikt se **nepřeklopil**, počítadlo zůstalo
# na 5 a test hlásil „brána NEMĚŘÍ (počítadlo nerozlišilo 5 od skutečnosti)".
# **Nebyla to vada brány — byla to neprovedená mutace.**
# Nové jméno je proto **úplně jiné** (`loadMainTree`), přesně jak to má
# zapsané `AGENTS.md` u omylu 18.
NOVY = "loadMainTree"


def spust():
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True, cwd=str(WS))
    v = (r.stdout.decode("utf-8", "replace")
         + r.stderr.decode("utf-8", "replace"))
    m = re.search(r"zastaralých \(nezávisle\):\s*(\d+)\s*z\s*(\d+)", v)
    return r.returncode, v, (int(m.group(1)), int(m.group(2))) if m else None


chyby = []
print("=" * 92)
print("MUTAČNÍ TEST `b5-over-tvrzeni.py` — přejmenovaný identifikátor")
print("=" * 92)

# ── 0) brána ten identifikátor OPRAVDU hledá ──────────────────────────────
zdroj = BRANA.read_text(encoding="utf-8")
print("\n  0) brána hledá %r: %s" % (IDENT, "ANO" if IDENT in zdroj else "NE"))
if IDENT not in zdroj:
    print("\n  CHYBA: brána ten identifikátor nehledá — test by měřil jiné místo")
    sys.exit(1)

# ── 1) kontrolní půl ──────────────────────────────────────────────────────
print("\n  1) KONTROLNÍ PŮL — brána nad dnešním kódem")
kod0, v0, c0 = spust()
print("     exit=%d · %s" % (kod0, ("zastaralých %d z %d" % c0) if c0 else "čítač se nenašel"))
if kod0 != 0:
    chyby.append("brána NEPROŠLA nad dnešním kódem (exit=%d) — "
                 "to je nález o kódu, ne o testu" % kod0)
if c0 is None:
    chyby.append("ve výstupu není čítač „zastaralých (nezávisle)“ — test by měřil naslepo")
elif c0[0] != 5:
    chyby.append("dnešní stav hlásí %d zastaralých, čekáno 5" % c0[0])

# ── 2) mutace ─────────────────────────────────────────────────────────────
orig = CIL.read_bytes()
t = orig.decode("utf-8")
pocet = len(re.findall(r"\b%s\b" % IDENT, t))
print("\n  2) MUTACE — v %s se %r přejmenuje na %r" % (CIL.name, IDENT, NOVY))
print("     výskytů (s hranicí slova): %dx" % pocet)
if pocet < 1:
    chyby.append("%r v %s není — mutace by nic nezměnila" % (IDENT, CIL.name))
try:
    zmut = re.sub(r"\b%s\b" % IDENT, NOVY, t)
    assert zmut != t, "MUTACE NEPROBĚHLA (text se nezměnil)"
    # ⚠ I NOVÉ JMÉNO SE KONTROLUJE: nesmí obsahovat to staré, jinak je mutace
    # neviditelná pro bránu, která hledá PODŘETĚZEC (omyl 18).
    assert IDENT not in NOVY, ("nové jméno %r OBSAHUJE staré %r — brána hledá "
                               "podřetězec a mutaci neuvidí!" % (NOVY, IDENT))
    CIL.write_text(zmut, encoding="utf-8", newline="")
    # ⚠ DVĚ OVĚŘENÍ, ŽE MUTACE SKUTEČNĚ PROBĚHLA — a to druhé je to podstatné
    # (omyl 18): původní identifikátor nesmí v souboru zůstat ANI JEDNOU.
    _zpet = CIL.read_text(encoding="utf-8")
    _zbyle = len(re.findall(r"\b%s\b" % IDENT, _zpet))
    assert _zbyle == 0, "MUTACE NEPROBĚHLA — %r je v souboru ještě %dx!" % (IDENT, _zbyle)
    kod1, v1, c1 = spust()
    print("     exit=%d · %s" % (kod1, ("zastaralých %d z %d" % c1) if c1 else "čítač se nenašel"))
    for l in v1.splitlines():
        if l.strip().startswith(("VYSLEDEK", "zastaralých")):
            print("        %s" % l.strip()[:110])
    if kod1 == 0:
        chyby.append("M: brána po mutaci skončila exit 0 — NEMĚŘÍ (počítadlo "
                     "nerozlišilo 5 od skutečnosti)")
    else:
        print("     → exit=%d (SPRÁVNĚ — počet zastaralých se změnil)" % kod1)
    if c1 is None:
        chyby.append("M: po mutaci ve výstupu není čítač")
    else:
        print("     → hlásí %d z %d (čekáno 4 z 5)" % c1)
        if c1[0] == c0[0]:
            chyby.append("M: počet zastaralých se NEZMĚNIL (%d) — mutace "
                         "nezměnila měřenou podmínku" % c1[0])
        if c1[1] != 5:
            chyby.append("M: počet TVRZENÍ se změnil (%d, čekáno 5) — mutace "
                         "sáhla i na seznam, ne jen na kód" % c1[1])
finally:
    CIL.write_bytes(orig)
    assert CIL.read_bytes() == orig, "%s NEVRÁCEN!" % CIL.name

# ── 3) soubor musí být zpátky ─────────────────────────────────────────────
print("\n  3) %s po testu" % CIL.name)
kod2, v2, c2 = spust()
print("     exit=%d · %s" % (kod2, ("zastaralých %d z %d" % c2) if c2 else "?"))
if kod2 != 0:
    chyby.append("po návratu souboru brána NEPROCHÁZÍ (exit=%d)" % kod2)

print()
print("=" * 92)
print("  ZMĚŘENO: běhů brány=3, mutací=1, chyb=%d" % len(chyby))
if chyby:
    print()
    for c in chyby:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: brána NEMĚŘÍ podle očekávání → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: brána MĚŘÍ — dnes `exit 0` (5 zastaralých), po přejmenování")
print("          identifikátoru se počet změní a brána skončí nenulově.")
print("          Soubor vrácen bajt po bajtu. exit 0")
sys.exit(0)

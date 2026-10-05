# -*- coding: utf-8 -*-
"""P16/A2 — VLASTNÍ měřidlo k tvrzení C z §33: klasifikátor „brána nezačala" (H71).

P15 to dělá TAK, že si vyrobí **kopii** `g3-brany.py`, vymění v ní `BRANY` a tu
kopii spustí. Já to dělám jinak: **dočasně vyměním `BRANY` v ŽIVÉM souboru**
a v `finally` ho vrátím **bajt na bajt** (a ověřím to). Důvod, proč to jde:
měří se tak **skutečný živý klasifikátor** včetně celého zbytku skriptu, ne
jeho kopie.

⚠ RIZIKO, KTERÉ SE MUSÍ OŠETŘIT: kdyby skript spadl mezi zápisem a návratem,
zůstane živý `g3-brany.py` zmutovaný. Proto:
  * záloha se píše PŘED mutací do `p16a2-g3-zaloha.py.bin`,
  * návrat je v `finally` + `assert` na shodu bajtů,
  * na STARTU se kontroluje, jestli tam z minula neleží marker `P16 FIXTURA`
    — kdyby ano, soubor se ze zálohy vrátí DŘÍV, než se cokoli měří.

Tři běhy:
  1. ŽIVÝ klasifikátor + 4 fixturové brány,
  2. ŽIVÝ klasifikátor + **mutace klasifikátoru na staré pravidlo podle DÉLKY**
     (`len(vystup) < 500`) — důkaz, že měření umí rozdíl ZACHRYTIT,
  3. kontrola, že po obou bězích je živý soubor bajt na bajt původní.
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
ZALOHA = ANALYZA / "p16a2-g3-zaloha.py.bin"
MARKER = "P16 FIXTURA"
BRANY1 = 'BRANY = [   # P16 FIXTURA'
BRANY2 = "]              # P16 FIXTURA konec"

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


def zpet():
    """Vrátí živý `g3-brany.py` ze zálohy (bajt na bajt)."""
    if ZALOHA.is_file():
        G3.write_bytes(ZALOHA.read_bytes())


# ── 0) POJISTKA: nezůstal tu mutant z minula? ───────────────────────────────
if ZALOHA.is_file() and MARKER in G3.read_text(encoding="utf-8", errors="replace"):
    print("  ⚠ v živém `g3-brany.py` je marker z minula — vracím ze zálohy")
    zpet()

print("=" * 78)
print("P16/A2 — klasifikátor „brána vůbec nezačala“: ŽIVÝ soubor, ne kopie")
print("=" * 78)

puvodni = G3.read_bytes()
ZALOHA.write_bytes(puvodni)
zk(not ZALOHA.is_file() or ZALOHA.read_bytes() == puvodni, "záloha živého souboru je zapsaná")

# ── 1) fixturové brány ─────────────────────────────────────────────────────
FIX = [
    ("fixtura: exit=2 s VLASTNIM hlasenim",
     [sys.executable, str(ANALYZA / "p16a2-brana-hlaseni.py")]),
    ("fixtura: exit=2 BEZ vystupu",
     [sys.executable, str(ANALYZA / "p16a2-brana-ticha.py")]),
    ("fixtura: neexistujici soubor",
     [sys.executable, str(ANALYZA / "p16a2-NEEXISTUJE.py")]),
    ("fixtura: exit=2 s hlasenim BEZ markeru",
     [sys.executable, str(ANALYZA / "p16a2-brana-bezmarkeru.py")]),
]
(ANALYZA / "p16a2-brana-hlaseni.py").write_text(
    "# -*- coding: utf-8 -*-\n"
    "import sys\n"
    "print('ZMĚŘENO: 0 granul — končím, není co měřit')\n"
    "sys.exit(2)\n", encoding="utf-8")
(ANALYZA / "p16a2-brana-ticha.py").write_text(
    "# -*- coding: utf-8 -*-\nimport sys\nsys.exit(2)\n", encoding="utf-8")
(ANALYZA / "p16a2-brana-bezmarkeru.py").write_text(
    "# -*- coding: utf-8 -*-\n"
    "import sys\n"
    "print('P16: hotovo, vse na svem miste')\n"
    "sys.exit(2)\n", encoding="utf-8")

fixtura = (BRANY1 + "\n" + "".join(
    "    (%r, %r, None),\n" % (p, c) for p, c in FIX) + BRANY2 + "\n")


def vymen_brany(text: str) -> str:
    radky = text.splitlines(keepends=True)
    i = next(i for i, l in enumerate(radky) if l.startswith("BRANY = ["))
    j = next(j for j in range(i + 1, len(radky)) if radky[j].rstrip("\r\n") == "]")
    return "".join(radky[:i]) + fixtura + "".join(radky[j + 1:])


def bez_klasifikatoru(text: str) -> str:
    """MUTACE: klasifikátor se vrací k pravidlu podle DÉLKY výstupu (vada H71)."""
    kotva = "    if any(z in text for z in _VLASTNI_HLASENI):"
    assert text.count(kotva) == 1, "kotva mutace je %dx" % text.count(kotva)
    return text.replace(
        kotva,
        "    return len(vystup) < 500      # P16 MUTACE: staré pravidlo podle DÉLKY\n"
        + kotva)


def spust_g3(popis: str):
    r = subprocess.run([sys.executable, str(G3)], capture_output=True, cwd=str(WS))
    v = (r.stdout or b"").decode("utf-8", "replace") \
        + (r.stderr or b"").decode("utf-8", "replace")
    print(f"\n  --- {popis}: exit={r.returncode}")
    for l in v.splitlines():
        if "BRÁNY, KTERÉ VŮBEC NEZAČALY" in l or l.strip().startswith("fixtura:"):
            print("      " + l.strip())
    m = re.search(r"BRÁNY, KTERÉ VŮBEC NEZAČALY \((\d+)\)", v)
    jmena = re.findall(r"^   (fixtura[^\s].*?)  \(", v, re.M)
    if not jmena:
        jmena = [l.strip().split("  (")[0] for l in v.splitlines()
                 if l.strip().startswith("fixtura:") and "  (" in l]
    return v, (int(m.group(1)) if m else 0), jmena


try:
    # ── BĚH 1: živý klasifikátor ───────────────────────────────────────────
    try:
        G3.write_text(vymen_brany(puvodni.decode("utf-8")), encoding="utf-8", newline="")
        zk(MARKER in G3.read_text(encoding="utf-8"), "fixtura je v živém souboru ZAPSANÁ")
        v1, n1, jmena1 = spust_g3("BĚH 1: ŽIVÝ klasifikátor (podle OBSAHU)")
    finally:
        zpet()
    zk(G3.read_bytes() == puvodni, "po běhu 1 je živý soubor bajt na bajt původní")

    a = [j for j in jmena1 if "VLASTNIM hlasenim" in j]
    b = [j for j in jmena1 if "BEZ vystupu" in j]
    c = [j for j in jmena1 if "neexistujici" in j]
    d = [j for j in jmena1 if "BEZ markeru" in j]
    zk(not a, "brána s `exit=2` a KRÁTKÝM VLASTNÍM hlášením NENÍ mezi nezačatými "
       "(to je jádro H71)")
    zk(bool(b), "brána s `exit=2` a PRÁZDNÝM výstupem mezi nezačatými JE")
    zk(bool(c), "NEEXISTUJÍCÍ soubor je mezi nezačatými")
    zk(n1 == 3, "nezačaté podle živého klasifikátoru: 3 z MÝCH 4 fixtur "
       "(P15 měla 3 fixtury a vyšly jí 2 — rozdíl je moje 4. fixtura, PROBA "
       "whitelistu; bez ní je to 2 a číslo P15 tím SEDÍ)", f"{n1}")
    print(f"  ⚠ PROBA whitelistu: hlášení bez markeru je mezi nezačatými: {bool(d)} "
          f"→ {'ANO (mez měřidla)' if d else 'ne'}")

    # ── BĚH 2: mutace na pravidlo podle DÉLKY (stará vada H71) ─────────────
    try:
        G3.write_text(bez_klasifikatoru(vymen_brany(puvodni.decode("utf-8"))),
                      encoding="utf-8", newline="")
        zk("P16 MUTACE" in G3.read_text(encoding="utf-8"), "mutace je ZAPSANÁ")
        v2, n2, jmena2 = spust_g3("BĚH 2: MUTACE — pravidlo podle DÉLKY (vada H71)")
    finally:
        zpet()
    zk(G3.read_bytes() == puvodni, "po běhu 2 je živý soubor bajt na bajt původní")

    a2 = [j for j in jmena2 if "VLASTNIM hlasenim" in j]
    zk(bool(a2), "S V RÁCENOU VADOU se brána s vlastním hlášením MEZI NEZAČATÉ "
       "DOSTANE → měření má jak selhat (jinak by nic nedokazovalo)")
    zk(n2 == n1 + 1, "a počet nezačatých se změní 3 → 4", f"{n1} → {n2}")
finally:
    zpet()

zk(G3.read_bytes() == puvodni,
   "ŽIVÝ `g3-brany.py` je na konci bajt na bajt původní (i při výpadku)")
print(f"  (záloha zůstává: {ZALOHA.name})")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
print("=" * 78)
sys.exit(1 if chyb else 0)

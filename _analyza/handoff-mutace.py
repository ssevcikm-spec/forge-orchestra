# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST brány `handoff-kontrola-uplnost.py` — Úkol 4 zadání.

CO SE DOKAZUJE (`overovani` §3): *„Napsal jsi test? Vrať do kódu vadu a podívej
se, že spadne."* Brána do 2. 10. 2026 **žádný mutační test neměla** — naměřeno
`_analyza\audit6-brany-mutace.py`: „Brány BEZ jakéhokoli důvodu: 10".

POSTUP (a proč právě tenhle):
  1. **KONTROLNÍ PŮL** — brána nad ŽIVÝM `HANDOFF.md` musí projít (`exit 0`,
     `83/83`). Bez toho by každé spadnutí níž mohlo znamenat „brána je
     rozbitá", ne „brána měří".
  2. **MUTACE** — z **KOPIE** `HANDOFF.md` se smaže **jedna kotva** (klíč
     `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`, kategorie „technické").
     Brána musí hlásit **82/83** a skončit **nenulově**.
  3. **NÁVRAT** — `try/finally` vrátí kopii a **assertuje**, že se vrátila.

⚠ PROČ SE NEMUTUJE ŽIVÝ `HANDOFF.md` (a je to poučení):
  V témže workspace pracuje **souběžná session** a `HANDOFF.md` **není v gitu**
  (zálohou je jen kopie souboru). Mutovat živý dokument by znamenalo, že při
  výpadku uprostřed zůstane **331 kB dokumentu bez jednoho klíčového bodu** —
  a to je přesně ta „nejdražší chyba předání", před kterou varuje `AGENTS.md`.
  Fixtura měří **totéž**: seznam klíčů je pevný, mění se jen dokument
  (cesta se bráně předává argumentem).

⚠ CO SE OVĚŘUJE U MUTACE (`overovani` §7.9, §7.14, §10.6):
  1. že mutace **proběhla** (`assert` na změnu textu i na to, že kotva v souboru
     po zápisu **není**),
  2. že **měřená podmínka přestala platit** — tj. kotva v obsahu opravdu chybí,
  3. že se **počet změnil** (82 vs 83) — ne jen exit kód.

Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza\handoff-mutace.py
Návrat:   0 = brána měří (projde na živém a spadne na chybějící kotvě)
"""

import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "_analyza" / "handoff-kontrola-uplnost.py"
ZIVY = WS / "HANDOFF.md"
DOCASNE = WS / "_analyza" / "_handoff-mutace"
FIXTURA = DOCASNE / "HANDOFF-fixtura.md"

assert BRANA.is_file(), "brána %s není" % BRANA
assert ZIVY.is_file(), "živý %s není" % ZIVY

# Kotva se ČTE Z BRÁNY, neopisuje se — kdyby zmizela ze seznamu, test to musí
# říct, ne měřit něco jiného (`overovani` §7.11).
KOTVA = "ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md"


def spust(cesta: pathlib.Path):
    """Spustí bránu nad daným dokumentem. Vrací (exit, výstup)."""
    r = subprocess.run([sys.executable, str(BRANA), str(cesta)],
                       capture_output=True, cwd=str(WS))
    v = (r.stdout.decode("utf-8", "replace")
         + r.stderr.decode("utf-8", "replace"))
    return r.returncode, v


def pocty(vystup: str):
    """(kontrolovaných, nalezených, chybí) — z výstupu brány, ne odhadem."""
    m = re.search(r"kontrolovaných klíčů:\s+(\d+)", vystup)
    n = re.search(r"nalezených:\s+(\d+)", vystup)
    c = re.search(r"CHYBÍ:\s+(\d+)", vystup)
    if not (m and n and c):
        return None
    return int(m.group(1)), int(n.group(1)), int(c.group(1))


chyby = []
print("=" * 92)
print("MUTAČNÍ TEST `handoff-kontrola-uplnost.py` — smaž jednu kotvu")
print("=" * 92)

# ── 0) kotva musí být v seznamu brány ─────────────────────────────────────
zdroj = BRANA.read_text(encoding="utf-8")
print("\n  0) kotva %r je v seznamu brány: %s"
      % (KOTVA, "ANO" if KOTVA in zdroj else "NE"))
if KOTVA not in zdroj:
    chyby.append("kotva %r v bráně není — test by měřil jiné místo" % KOTVA)

# ── 1) KONTROLNÍ PŮL: živý dokument musí projít ───────────────────────────
print("\n  1) KONTROLNÍ PŮL — brána nad ŽIVÝM HANDOFF.md")
kod0, v0 = spust(ZIVY)
p0 = pocty(v0)
print("     exit=%d · %s" % (kod0, ("%d/%d, chybí %d" % p0) if p0 else "čítače se nenašly"))
if kod0 != 0:
    chyby.append("brána NEPROŠLA nad živým HANDOFF.md (exit=%d) — "
                 "to je nález o dokumentu, ne o testu" % kod0)
if p0 is None:
    chyby.append("ve výstupu brány nejsou čítače — test by měřil naslepo")
elif p0[2] != 0:
    chyby.append("živý HANDOFF.md hlásí %d chybějících klíčů" % p0[2])
else:
    print("     → živý dokument je ÚPLNÝ (%d/%d)" % (p0[1], p0[0]))

# ── 2) MUTACE: z KOPIE se smaže jedna kotva ───────────────────────────────
print("\n  2) MUTACE — z kopie se smaže kotva %r" % KOTVA)
DOCASNE.mkdir(parents=True, exist_ok=True)
shutil.copyfile(ZIVY, FIXTURA)
orig = FIXTURA.read_bytes()
t = orig.decode("utf-8")
pocet_v_orig = t.count(KOTVA)
print("     kotva v kopii: %dx" % pocet_v_orig)
if pocet_v_orig != 1:
    chyby.append("kotva %r je v kopii %dx (čekáno 1) — mutace by nebyla "
                 "jednoznačná" % (KOTVA, pocet_v_orig))
try:
    zmut = t.replace(KOTVA, "(kotva smazána mutací)", 1)
    assert zmut != t, "MUTACE NEPROBĚHLA (text se nezměnil)"
    FIXTURA.write_text(zmut, encoding="utf-8", newline="")
    # 2 ověření, že mutace SKUTEČNĚ proběhla (ne jen že se něco zapsalo):
    _zpet = FIXTURA.read_text(encoding="utf-8")
    assert KOTVA not in _zpet, "MUTACE NEPROBĚHLA — kotva je v souboru pořád!"
    kod1, v1 = spust(FIXTURA)
    p1 = pocty(v1)
    print("     exit=%d · %s" % (kod1, ("%d/%d, chybí %d" % p1) if p1 else "čítače se nenašly"))
    for l in v1.splitlines():
        if l.strip().startswith("✗"):
            print("        %s" % l.strip()[:110])
    if p1 is None:
        chyby.append("M: ve výstupu po mutaci nejsou čítače")
    else:
        if p1[2] != 1:
            chyby.append("M: brána hlásí %d chybějících, čekáno 1" % p1[2])
        if p1[1] != p1[0] - 1:
            chyby.append("M: nalezených=%d z %d — neubyly právě jedny"
                         % (p1[1], p1[0]))
        print("     → hlásí %d/%d (čekáno 82/83)" % (p1[1], p1[0]))
    if kod1 == 0:
        chyby.append("M: brána po smazání kotvy skončila exit 0 — NEMĚŘÍ")
    else:
        print("     → exit=%d (SPRÁVNĚ — chybějící bod je vada)" % kod1)
finally:
    FIXTURA.write_bytes(orig)
    assert FIXTURA.read_bytes() == orig, "FIXTURA NEVRÁCENA!"
shutil.rmtree(DOCASNE, ignore_errors=True)

# ── 3) živý dokument se NESMÍ změnit ──────────────────────────────────────
print("\n  3) živý HANDOFF.md po testu")
kod2, v2 = spust(ZIVY)
p2 = pocty(v2)
print("     exit=%d · %s" % (kod2, ("%d/%d, chybí %d" % p2) if p2 else "?"))
if kod2 != 0:
    chyby.append("živý HANDOFF.md po testu NEPROCHÁZÍ (exit=%d)" % kod2)

print()
print("=" * 92)
print("  ZMĚŘENO: běhů brány=3, mutací=1, chyb=%d" % len(chyby))
if chyby:
    print()
    for c in chyby:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: brána NEMĚŘÍ podle očekávání → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: brána MĚŘÍ — na živém dokumentu 83/83, po smazání jedné")
print("          kotvy hlásí 82/83 a skončí nenulově. Fixtura vrácena. exit 0")
sys.exit(0)

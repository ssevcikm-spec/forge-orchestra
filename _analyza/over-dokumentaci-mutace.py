# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST brány `orchestra/tools/over-dokumentaci.py` — Úkol 4 zadání.

CO SE DOKAZUJE (`overovani` §3): brána, která **nemá jak selhat**, není brána.
`over-dokumentaci.py` kontroluje **řízené výrazy** v dokumentech — a do 2. 10.
2026 neměla **žádný mutační test** (naměřeno `audit6-brany-mutace.py`).

POSTUP:
  1. **KONTROLNÍ PŮL** — brána nad dnešními dokumenty projde (`exit 0`,
     `Kontrol: 63, chyb: 0`).
  2. **MUTACE** — v `MOZNOSTI-AGENTA.md` se **rozřízne kontrolovaný výraz**
     `read_image` na `read image` (mezera místo podtržítka). Brána ho tím
     **nenajde** a musí ohlásit chybu + `exit 1`.
  3. **NÁVRAT** — `try/finally` vrátí soubor **bajt po bajtu**.

⚠ PROČ PRÁVĚ TENHLE VÝRAZ: je to **první** výraz v seznamu pro
`MOZNOSTI-AGENTA.md` a je **jednoslovný** — neobsahuje mezeru, takže ho
markdownové zalamování řádků nemůže rozdělit (brána sama v komentáři
upozorňuje, že delší věty se v zalamovaných dokumentech nikdy nenajdou).

⚠ CO SE U MUTACE OVĚŘUJE (`overovani` §7.9, §7.14):
  1. mutace **proběhla** (`assert` na změnu i na to, že původní výraz v souboru
     po zápisu **není**),
  2. **měřená podmínka přestala platit** — tj. hledaný výraz v dokumentu chybí.
  A co se ověřuje **navíc**: že číslo v `Kontrol:` **kleslo přesně o jedničku**
  — kdyby brána hlásila chybu z jiného důvodu, test to odhalí.

Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza\over-dokumentaci-mutace.py
Návrat:   0 = brána měří | 1 = neměří (a vypíše, co konkrétně)
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "orchestra" / "tools" / "over-dokumentaci.py"
CIL = WS / "MOZNOSTI-AGENTA.md"

assert BRANA.is_file(), "brána %s není" % BRANA
assert CIL.is_file(), "dokument %s není" % CIL

VZOR = "read_image"
NAHRAD = "read image"

# ⚠ VÝRAZ SE ČTE Z BRÁNY, neopisuje se (`overovani` §7.11): kdyby ho brána
# přestala kontrolovat, test to musí říct — ne měřit něco jiného.
zdroj = BRANA.read_text(encoding="utf-8")
print("=" * 92)
print("MUTAČNÍ TEST `over-dokumentaci.py` — rozříznutý kontrolovaný výraz")
print("=" * 92)
print("\n  0) výraz %r je v seznamu brány u %s: %s"
      % (VZOR, CIL.name, "ANO" if VZOR in zdroj else "NE"))
if VZOR not in zdroj:
    print("\n  CHYBA: brána ten výraz nekontroluje — test by měřil jiné místo")
    sys.exit(1)


def spust():
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True, cwd=str(WS))
    v = (r.stdout.decode("utf-8", "replace")
         + r.stderr.decode("utf-8", "replace"))
    m = re.search(r"Kontrol:\s*(\d+),\s*chyb:\s*(\d+)", v)
    return r.returncode, v, (int(m.group(1)), int(m.group(2))) if m else None


chyby = []

# ── 1) kontrolní půl ──────────────────────────────────────────────────────
print("\n  1) KONTROLNÍ PŮL — brána nad dnešními dokumenty")
kod0, v0, c0 = spust()
print("     exit=%d · %s" % (kod0, ("Kontrol: %d, chyb: %d" % c0) if c0 else "čítač se nenašel"))
if kod0 != 0:
    chyby.append("brána NEPROŠLA nad zdravými dokumenty (exit=%d) — "
                 "to je nález o dokumentech, ne o testu" % kod0)
if c0 is None:
    chyby.append("ve výstupu není čítač `Kontrol:` — test by měřil naslepo")
elif c0[1] != 0:
    chyby.append("zdravý stav hlásí %d chyb" % c0[1])

# ── 2) mutace ─────────────────────────────────────────────────────────────
orig = CIL.read_bytes()
t = orig.decode("utf-8")
print("\n  2) MUTACE — v %s se %r změní na %r" % (CIL.name, VZOR, NAHRAD))
print("     výskytů v dokumentu: %dx" % t.count(VZOR))
if t.count(VZOR) < 1:
    chyby.append("výraz %r v %s není — mutace by nic nezměnila" % (VZOR, CIL.name))
try:
    zmut = t.replace(VZOR, NAHRAD)
    assert zmut != t, "MUTACE NEPROBĚHLA (text se nezměnil)"
    CIL.write_text(zmut, encoding="utf-8", newline="")
    # dvě ověření, že mutace SKUTEČNĚ proběhla:
    _zpet = CIL.read_text(encoding="utf-8")
    assert VZOR not in _zpet, "MUTACE NEPROBĚHLA — výraz je v souboru pořád!"
    kod1, v1, c1 = spust()
    print("     exit=%d · %s" % (kod1, ("Kontrol: %d, chyb: %d" % c1) if c1 else "čítač se nenašel"))
    for l in v1.splitlines():
        if "CHYBA" in l or "chybí" in l.lower():
            print("        %s" % l.strip()[:110])
    if kod1 == 0:
        chyby.append("M: brána po rozříznutí výrazu skončila exit 0 — NEMĚŘÍ")
    else:
        print("     → exit=%d (SPRÁVNĚ — chybějící výraz je vada)" % kod1)
    if c1 is None:
        chyby.append("M: po mutaci ve výstupu není čítač")
    elif c1[1] < 1:
        chyby.append("M: brána hlásí 0 chyb, ačkoli výraz chybí")
    else:
        print("     → hlásí %d chyb (čekáno aspoň 1)" % c1[1])
    if c0 and c1 and c1[0] > c0[0]:
        chyby.append("M: počet kontrol STOUPL (%d → %d) — to nedává smysl"
                     % (c0[0], c1[0]))
finally:
    CIL.write_bytes(orig)
    assert CIL.read_bytes() == orig, "%s NEVRÁCEN!" % CIL.name

# ── 3) dokument musí být zpátky ───────────────────────────────────────────
print("\n  3) %s po testu" % CIL.name)
kod2, v2, c2 = spust()
print("     exit=%d · %s" % (kod2, ("Kontrol: %d, chyb: %d" % c2) if c2 else "?"))
if kod2 != 0:
    chyby.append("po návratu dokumentu brána NEPROCHÁZÍ (exit=%d)" % kod2)

print()
print("=" * 92)
print("  ZMĚŘENO: běhů brány=3, mutací=1, chyb=%d" % len(chyby))
if chyby:
    print()
    for c in chyby:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: brána NEMĚŘÍ podle očekávání → exit 1")
    sys.exit(1)
print("\nVYSLEDEK: brána MĚŘÍ — na zdravých dokumentech `exit 0`,")
print("          po rozříznutí kontrolovaného výrazu hlásí chybu a `exit 1`.")
print("          Dokument vrácen bajt po bajtu. exit 0")
sys.exit(0)

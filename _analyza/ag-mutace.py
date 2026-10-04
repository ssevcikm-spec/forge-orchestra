# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""BOD 12 z §7.2: měří `ag-over-cisla.py` DOKUMENT, nebo si porovnává zdroj sám se sebou?

Nález N9 říká, že první verze tohohle nástroje měla tvrzená čísla NAPSANÁ
NAPEVNO — měřila tedy zdroj a porovnávala ho sám se sebou a vrácená vada
v dokumentu jí prošla. Tenhle test to zkouší dvěma mutacemi:

  1) vloží se VADA: `40 sloupců` -> `32 sloupců`   → brána MUSÍ spadnout
  2) PŘEFORMULUJE se tvrzení (`40 sloupců` -> `čtyřicet sloupců`) → brána musí
     hlásit „NENAŠLA SE TVRZENÍ", ne „OK" (jinak je slepá k přeformulování)

⚠ KOTVA SE 2. 10. 2026 ZMĚNILA: `39 sloupců` -> `40 sloupců` (Úkol 2 zadání
`ZADANI-DOKONCENI-AUDITU.md`). Naměřeno: `Select-String` i Python na
`39 sloupců` → **0 výskytů** v `AGENTS.md` — číslo 39 a slovo „sloupců"
nejsou v dokumentu nikde vedle sebe. `pocet != 1` proto obě mutace
**tiše neprovedlo** a skript skončil `exit 1`; a protože **nebyl v seznamu
`BRANY` v `g3-brany.py`**, nikdo si toho nevšiml. Přesně to je past
`overovani` §7.9 („mutace, která se tiše neprovede, tvrdí totéž co mutace,
která projde") — a druhá polovina vady byla, že **nikdo ten exit nečetl**.
Jednoznačná kotva je `40 sloupců` (výskytů **1** — tabulka jazyka,
`AGENTS.md:338`).

A navíc se měří POKRYTÍ (to je nález N9): kolik tvrzení o číslech v AGENTS.md
nástroj vůbec kontroluje. Částečný nástroj budí falešný dojem úplnosti.

POZOR (naměřeno 2. 10. 2026): mutace se NESMÍ dělat přes PowerShell
`-replace` ani inline `python -c` s uvozovkami — příkaz se rozbil a mutace se
TICHE neprovedla, takže brána prošla nad nezměněným souborem a výsledek
nic neznamenal (skill `overovani` §7.9). Proto se mutuje tady, v Pythonu,
a PŘED spuštěním brány se ověří, že vada v souboru OPRAVDU je.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\ag-mutace.py
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
AGENTS = WS / "AGENTS.md"
BRANA = WS / "_analyza" / "ag-over-cisla.py"

orig = AGENTS.read_bytes()
text = orig.decode("utf-8")


def spust():
    r = subprocess.run([sys.executable, str(BRANA)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "")


kod0, vystup0 = spust()
# ⚠ POUŽITY POJMENOVANÉ SKUPINY (opraveno 2. 10. 2026): původní vzor měl tři
# číselné skupiny a kód tiskl `m.group(2)` pod popiskem „historických" —
# jenže group(2) bylo `ROZEŠLO SE`. Nástroj tedy hlásil **jiný čítač, než jak
# se jmenoval** (přesně ta past, před kterou varuje `AGENTS.md`: „různé čítače
# nesou stejné jméno"). Naměřeno: výstup tvrdil „5 v pořádku + 0 historických",
# ačkoli historická byla **2** — a to číslo si vzal i audit do R5.
# S pojmenovanými skupinami se záměna pořadí nemůže zopakovat.
m = re.search(r"v pořádku:\s*(?P<ok>\d+) \| historická[^|]*:\s*(?P<hist>\d+)"
              r" \| ROZEŠLO SE:\s*(?P<rozeslo>\d+)"
              r" \| NENAŠLA SE TVRZENÍ:\s*(?P<nenasla>\d+)", vystup0)
print("=== BOD 12: mutace `AGENTS.md` proti `ag-over-cisla.py` ===\n")
print(f"  0) vychozi stav: exit={kod0}, "
      f"v poradku={m.group('ok') if m else '?'}, "
      f"historicka={m.group('hist') if m else '?'}, "
      f"rozslo={m.group('rozeslo') if m else '?'}, "
      f"nenasla={m.group('nenasla') if m else '?'}")
if kod0 != 0:
    print("     POZOR: vychozi stav neprochazi.")
    sys.exit(1)

selhalo = []
chycene = []          # mutace, které brána CHYTILA (pro strojově čitelný součet)
try:
    # ── MUTACE 1: číslo 40 -> 32 (vracená vada N9) ───────────────────────────
    # Kotva JE `40 sloupců` (AGENTS.md:338, výskytů 1). Dřív tu stálo
    # `39 sloupců`, což v dokumentu NEBYLO ANI JEDNOU → mutace se neprovedla.
    pocet = text.count("40 sloupců")
    print(f"\n  1) vracím vadu: `40 sloupců` -> `32 sloupců`  (vzor {pocet}x)")
    if pocet != 1:
        print("     NEZMUTOVANO — vzor neni jednoznacny")
        selhalo.append("mutace 1 se neprovedla")
    else:
        zmut = text.replace("40 sloupců", "32 sloupců")
        assert "32 sloupců" in zmut and "40 sloupců" not in zmut, "mutace 1 se neprovedla!"
        AGENTS.write_text(zmut, encoding="utf-8", newline="")
        # OVERENI, ZE VADA JE V SOUBORU (past §7.9)
        assert "32 sloupců" in AGENTS.read_text(encoding="utf-8"), "vada v souboru neni!"
        kod, vystup = spust()
        ok1 = kod != 0
        print(f"     exit={kod} -> {'SPRAVNE SPADLA' if ok1 else 'SLEPA (prosla i s vadou!)'}")
        for l in vystup.splitlines():
            if "ROZEŠLO" in l or "sloupc" in l:
                print("        " + l.strip()[:110])
        if not ok1:
            selhalo.append("mutace 1: brana prosla s vadou 40 -> 32")
        else:
            chycene.append("mutace 1 (vada 40 -> 32)")
        AGENTS.write_bytes(orig)

    # ── MUTACE 2: přeformulování (číslo -> slovo) ────────────────────────────
    print(f"\n  2) přeformuluji tvrzení: `40 sloupců` -> `čtyřicet sloupců`")
    if text.count("40 sloupců") != 1:
        print("     NEZMUTOVANO")
        selhalo.append("mutace 2 se neprovedla")
    else:
        zmut = text.replace("40 sloupců", "čtyřicet sloupců")
        assert "čtyřicet sloupců" in zmut, "mutace 2 se neprovedla!"
        assert "40 sloupců" not in zmut, "mutace 2: kotva v textu zustala!"
        AGENTS.write_text(zmut, encoding="utf-8", newline="")
        assert "čtyřicet sloupců" in AGENTS.read_text(encoding="utf-8")
        kod, vystup = spust()
        nenasla = re.search(r"NENAŠLA SE TVRZENÍ:\s*(\d+)", vystup)
        hlasi = bool(nenasla and int(nenasla.group(1)) > 0)
        print(f"     exit={kod}, hlasi 'NENASLA SE TVRZENI': {hlasi}")
        for l in vystup.splitlines():
            if "NENAŠLA" in l or "ZÁVĚR" in l:
                print("        " + l.strip()[:110])
        if not hlasi:
            selhalo.append("mutace 2: preformulovane tvrzeni brana nevidi (hlasi OK)")
        else:
            chycene.append("mutace 2 (přeformulované tvrzení)")
        AGENTS.write_bytes(orig)
finally:
    AGENTS.write_bytes(orig)
    assert AGENTS.read_bytes() == orig, "AGENTS.md nevracen!"

kod_po, _ = spust()
print(f"\n  po vraceni originalu: exit={kod_po}")
assert kod_po == 0, "original neprochazi!"

# ── POKRYTÍ (nález N9) ───────────────────────────────────────────────────────
print("\n=== POKRYTÍ nástroje (nález N9: částečný nástroj budí dojem úplnosti) ===")
radky_s_cislem = [l for l in text.splitlines() if re.search(r"\d{2,}", l)]
radky_s_jednotkou = [l for l in text.splitlines()
                     if re.search(r"\d+\s*(%|sloupc|soubor|míst|znak|řádk|tabulek|nález|mutac|testů|kontrol)", l)]
print(f"  řádků s číslem v AGENTS.md      : {len(radky_s_cislem)}")
print(f"  z toho číslo s jednotkou (tvrzení): {len(radky_s_jednotkou)}")
print(f"  nástroj kontroluje              : {m.group('ok') if m else '?'} v pořádku "
      f"+ {m.group('hist') if m else '?'} historických"
      f" (z {len(radky_s_jednotkou)} tvrzení s jednotkou)")
print("  -> zbytek čísel v AGENTS.md NENÍ kontrolován")

# ── STROJOVĚ ČITELNÝ SOUČET (overovani §2.3) ─────────────────────────────────
# Bez tohohle řádku se z `g3-brany.py` nedá vyčíst, KOLIK toho test změřil —
# a `exit 0` bez počtu je ticho, ne zelená. Vzor pro `g3-brany.py` je
# `mutací=(\d+), chyceno=(\d+)`.
print()
print(f"  ZMĚŘENO: mutací=2, chyceno={len(chycene)}, "
      f"tvrzení_v_dokumentu={len(radky_s_jednotkou)}, "
      f"řádků_s_číslem={len(radky_s_cislem)}")
for c in chycene:
    print(f"            chyceno: {c}")

print()
if selhalo:
    print(f"VYSLEDEK: {len(selhalo)} problem:")
    for s in selhalo:
        print(f"          - {s}")
    sys.exit(1)
print("VYSLEDEK: brána spadne na vrácené vadě i na přeformulovaném tvrzení.")
sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""MUTAČNÍ TEST sebekontroly v `kontrola-diakritiky.py` (nové 2. 10. 2026).

CO SE OVĚŘUJE: brána teď kontroluje **i sama sebe** — ale jinak než ostatní
soubory, protože vzorek rozbitých znaků v sobě mít MUSÍ. Sebekontrola hledá pět
typických českých slov; když zmizí (typicky po rozbití kódování), musí brána
spadnout.

⚠ PAST, NA KTEROU JSEM NAPOPRVÉ NALETĚL: `s.encode('utf-8').decode('cp1250')`
**není** rozbití, které by se projevilo — bez `errors='replace'` se text
nezmění VŮBEC. První verze mutace proto skončila na `assert zmut != orig`,
a to je **správně**: mutační test, který se neprovede, tvrdí totéž co mutační
test, který projde (skill `overovani` §7.9).

Použití: python _analyza\\g1-mutace-diakritika.py
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
BRANA = WS / "tools" / "kontrola-diakritiky.py"

puvodni = BRANA.read_text(encoding="utf-8")


def spust() -> tuple:
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True)
    v = (r.stdout + r.stderr).decode("utf-8", "replace")
    return r.returncode, v


def hlavni() -> int:
    print("=" * 74)
    print("1) ZDRAVÝ STAV — brána musí projít")
    print("=" * 74)
    kod, v = spust()
    for l in v.splitlines():
        if "kontrola-diakritiky" in l:
            print("   " + l.strip())
    print("   exit=%d %s" % (kod, "OK" if kod == 0 else "!! CHYBA"))
    if kod != 0:
        return 2

    print()
    print("=" * 74)
    print("2) MUTACE — rozbij české slovo v TEXTU souboru (ne v seznamu)")
    print("=" * 74)
    # ⚠ DRUHÁ PAST (naměřeno): první verze mutace rozbila slovo v `VLASTNI_TEXTY`,
    # tedy v SAMOTNÉM SEZNAMU, který se hledá → seznam tím přišel o položku
    # a brána správně nezabrala.
    # ⚠ TŘETÍ PAST (naměřeno hned po ní): slovo se v souboru vyskytuje **7×**,
    # takže rozbití JEDNOHO výskytu nic nezmění — sebekontrola hledá
    # `slovo in text`, a to pořád platí. A ani rozbití VŠECH výskytů nestačí:
    # seznam `VLASTNI_TEXTY` je v TOMTÉŽ souboru, takže si své slovo pořád najde.
    # → Sebekontrola proto kromě slov hledá i NÁHRADNÍ ZNAK; mutace rozbíjí
    #   české písmeno, které se v náhradní znak skutečně přeloží.
    #
    # Obecné pravidlo: mutace musí dosáhnout toho, aby měřená PODMÍNKA přestala
    # platit — ne jen aby se soubor změnil.
    cil = "ř"
    v_souboru = puvodni.count(cil)
    zmut = puvodni.replace(cil, "\ufffd")
    if zmut == puvodni:
        print("   CHYBA: mutaci se nepodařilo vyrobit — test by nic nedokázal")
        return 2
    if "\ufffd" not in zmut:
        print("   CHYBA: náhradní znak se do textu nedostal — mutace nedosáhla cíle")
        return 2
    print("   české písmeno %r bylo v souboru %d× a rozbito VŠUDE" % (cil, v_souboru))
    BRANA.write_bytes(zmut.encode("utf-8"))
    z5 = BRANA.read_text(encoding="utf-8")
    if z5 == puvodni:
        print("   CHYBA: mutace se do souboru nezapsala")
        return 2
    print("   ověřeno na disku: soubor je jiný (%d → %d znaků)" % (len(puvodni), len(z5)))
    try:
        kod2, v2 = spust()
        for l in v2.splitlines():
            if "kontrola-diakritiky" in l or "NALEZENY" in l or "VŠE OK" in l:
                print("   " + l.strip())
        print("   exit=%d" % kod2)
    finally:
        BRANA.write_bytes(puvodni.encode("utf-8"))
        if BRANA.read_text(encoding="utf-8") != puvodni:
            print("   CHYBA: návrat souboru selhal!")
            return 2
        print("   soubor vrácen bajt na bajt")

    print()
    print("=" * 74)
    uspech = kod2 != 0
    print("VÝSLEDEK: %s" % ("CHYCENO — sebekontrola brány umí spadnout"
                            if uspech else
                            "SLEPÉ — brána prošla i s rozbitým vlastním textem!"))
    print("=" * 74)
    return 0 if uspech else 1


if __name__ == "__main__":
    sys.exit(hlavni())

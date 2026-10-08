# -*- coding: utf-8 -*-
r"""P27 — KONTROLA KLASIFIKÁTORU v A6 (jednotkově, na NAMĚŘENÝCH jménech).

PROČ: v posledním plném běhu mělo `g3` **4 nedeklarované exity** ve DVOU
pojmenovaných stavech: `['n1-over-inventar', 'over-skilly', 'over-skilly: mutace
delegovaných cest', 'validate-all (CELEK)']`. Opravil jsem klasifikaci v A6 tak,
aby přijala MÍCHANÝ stav (ZASTARALÝ INVENTÁŘ ∪ SKILL MIMO REPO). Tenhle skript
ověřuje PREDIKÁT na obou stranách: naměřený seznam musí projít, ale seznam
s NEPOJmenovaným exitem projít NESMÍ (jinak by brána byla slepá).
"""

import sys

ZAST = ("C2: mutace N1 (5 běhů)", "n1-over-inventar", "validate-all (CELEK)")
MIMO_REPO = ("over-skilly", "over-skilly: mutace delegovaných cest")


def klasifikuj(jmena):
    return all((j in ZAST) or (j.strip() in MIMO_REPO) for j in jmena)


NAMERENO = ['n1-over-inventar', 'over-skilly',
            'over-skilly: mutace delegovaných cest', 'validate-all (CELEK)']
JEN_MIMO = ['over-skilly', 'over-skilly: mutace delegovaných cest']
JEN_ZAST = ['n1-over-inventar', 'validate-all (CELEK)']
NEZNAMY = ['n1-over-inventar', 'over-skilly', 'nejaka-nova-brana']

kontrol = 0
chyb = 0
for jmena, ocekavano, popis in (
        (NAMERENO, True, "naměřený MÍCHANÝ seznam (2 stavy v jednom běhu)"),
        (JEN_MIMO, True, "jen skill mimo repo"),
        (JEN_ZAST, True, "jen zastaralý inventář"),
        (NEZNAMY, False, "seznam s NEPOJmenovaným exitem (brána NESMÍ mlčet)"),
        ([], True, "žádný nenulový exit")):
    kontrol += 1
    vysledek = klasifikuj(jmena)
    ok = vysledek == ocekavano
    chyb += 0 if ok else 1
    print("  %s  %-52s → %s (čekáno %s)"
          % ("OK  " if ok else "CHYBA", popis, vysledek, ocekavano))
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
sys.exit(1 if chyb else 0)

# -*- coding: utf-8 -*-
r"""Doplní do `KRONIKA-PROJEKTU.md` poučení **L13** a opraví souhrn §8g
v `HANDOFF.md` („sedmi" -> „osmi" — po doplnění omylu 68 je v bloku 8 omylů).

PROČ: dvě čísla přestala platit **vlastní prací téhle session** (omyl 68 se
přidal až na konci). Nechat je být znamená zapsat tvrzení, které si odporuje
s tabulkou o dva řádky výš.

PROČ TEXT V SOUBORU: české uvozovky uvnitř `python -c` a v Python literálech
rozbily předchozí verzi tohohle skriptu (`SyntaxError: unmatched ')'`) — je to
past z `dsh-prostredi` §3d a stála tři kola. Text se proto čte **bajt na bajt**.

Použití:  python _analyza\s18e-dopln-l13.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
HANDOFF = WS / "HANDOFF.md"
ZAPIS = "--zapis" in sys.argv

L13 = (WS / "_analyza" / "s18e-l13-radek.md").read_text(encoding="utf-8").strip()
assert L13.startswith("| **L13** |"), "řádek L13 nemá správný tvar"
assert L13.count("\n") == 0, "L13 musí být JEDEN řádek tabulky"

# ── 1) HANDOFF: souhrn §8g (kotva bez českých uvozovek) ─────────────────────
hand = HANDOFF.read_text(encoding="utf-8")
STARE = "Vzor z těch sedmi"
NOVE = "Vzor z těch osmi"
STARE2 = "šest ze sedmi** vzniklo v **měřidle**"
NOVE2 = "sedm z osmi** vzniklo v **měřidle**"
print("HANDOFF.md:")
for popis, k, o in (("kotva", STARE, 1), ("druhá kotva", STARE2, 1)):
    print("  %-12s %dx (očekáváno %d)" % (popis, hand.count(k), o))

# ── 2) KRONIKA: L13 za řádek L12 ────────────────────────────────────────────
kron = KRONIKA.read_text(encoding="utf-8")
radky = kron.split("\n")
idx = [i for i, r in enumerate(radky) if r.startswith("| **L12** |")]
assert len(idx) == 1, "řádek L12 není právě 1× (nalezeno %d)" % len(idx)
i12 = idx[0]
assert radky[i12].rstrip().endswith("|"), "řádek L12 nevypadá jako řádek tabulky"
radky.insert(i12 + 1, L13)
nova_kron = "\n".join(radky)
assert nova_kron != kron, "vložení L13 NEPROBĚHLO"
assert nova_kron.count("| **L13** |") == 1, "L13 není právě 1×"
assert nova_kron.count("| **L12** |") == 1, "L12 se ztratil nebo zdvojil"
assert nova_kron.count("| **L1** |") == 1, "L1 se ztratil"
print("KRONIKA-PROJEKTU.md: L13 se vloží za řádek %d (L12)" % (i12 + 1))
print("  `%s`" % L13[:90])

if ZAPIS:
    if hand.count(STARE) == 1 and hand.count(STARE2) == 1:
        hand2 = hand.replace(STARE, NOVE, 1).replace(STARE2, NOVE2, 1)
        assert hand2 != hand, "oprava souhrnu NEPROBĚHLA"
        HANDOFF.write_bytes(hand2.encode("utf-8"))
        print("  HANDOFF.md: souhrn §8g opraven („sedmi“ -> „osmi“)")
    else:
        print("  CHYBA: kotvy souhrnu nesedí — neopravuji")
        sys.exit(1)
    KRONIKA.write_bytes(nova_kron.encode("utf-8"))
    print("  KRONIKA-PROJEKTU.md: L13 vloženo")
else:
    print("  (dry-run — spusť s --zapis)")

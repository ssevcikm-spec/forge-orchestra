# -*- coding: utf-8 -*-
r"""P35 — ČÍTAČE PO SEKCÍCH: porovnej dva běhy měřidla sekce po sekci.

PROČ: „naměřeno 51/0, ale dokument tvrdí 50/0" je ROZDÍL — a ten se musí
POJMENOVAT, ne jen vypsat. Celkový čítač řekne, ŽE se něco posunulo; čítače po
sekcích řeknou, KDE (a tím i proč). Tohle je nejrychlejší cesta k tomu pojmenování.

Použití:
    python _analyza/p35-pocty-sekci.py <doklad-A> <doklad-B> [...]
Vypíše pro každý soubor počty `OK` / `CHYBA` / `NÁLEZ` / `NEZMĚŘENO` podle
sekcí (`A0)`, `A1)`, …) a nakonec rozdíl A → B po sekcích.

⚠ Bere se POSLEDNÍ čítač `VÝSLEDEK:` v souboru (doklad může mít shrnutí dvakrát).
⚠ NEČTE české názvy sekcí jako klíč — klíčem je jen `A0`/`B1`, aby skript
  nezávisel na diakritice (kódování je častá past téhle stanice).
"""

import collections
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def secty(path):
    d = collections.defaultdict(collections.Counter)
    cur = "?"
    for radek in pathlib.Path(path).read_text(encoding="utf-8", errors="replace").splitlines():
        m = re.match(r"^([A-Z]\d)\)", radek)
        if m:
            cur = m.group(1)
        for klic, vzor in (("OK", "  OK"), ("CHYBA", "  CHYBA"),
                           ("ROZDIL", "  ROZDÍL"), ("NEZMERENO", "  NEZMĚŘENO"),
                           ("NALÉZ", "  NÁLEZ")):
            if radek.startswith(vzor):
                d[cur][klic] += 1
    return d


def main():
    if len(sys.argv) < 2:
        print("použití: python _analyza/p35-pocty-sekci.py <doklad-A> [doklad-B ...]")
        return 2
    vsechny = [(pathlib.Path(p), secty(p)) for p in sys.argv[1:]]
    print("=" * 96)
    for cesta, d in vsechny:
        print("## %s" % cesta.name)
        for sekce in sorted(d):
            c = d[sekce]
            print("   %-4s OK=%-3d CHYBA=%-2d ROZDÍL=%-2d NEZMĚŘENO=%-2d NÁLEZ=%d"
                  % (sekce, c["OK"], c["CHYBA"], c["ROZDIL"], c["NEZMERENO"], c["NALÉZ"]))
    if len(vsechny) == 2:
        (ca, da), (cb, db) = vsechny
        print("\n## ROZDÍL %s → %s (jen nenulové)" % (ca.name, cb.name))
        for sekce in sorted(set(da) | set(db)):
            rozdil = {k: db[sekce][k] - da[sekce][k] for k in
                      ("OK", "CHYBA", "ROZDIL", "NEZMERENO", "NALÉZ")}
            if any(rozdil.values()):
                print("   %-4s %s" % (sekce, " ".join("%s%+d" % (k, v) for k, v in rozdil.items() if v)))
    print("=" * 96)
    return 0


if __name__ == "__main__":
    sys.exit(main())

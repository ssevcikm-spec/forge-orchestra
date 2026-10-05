# -*- coding: utf-8 -*-
r"""P13c: opraví ZTRACENOU DIAKRITIKU ve slově `ZMĚŘENO` (a dalším).

CO SE STALO (naměřeno, ne odhad):
  Do některých souborů se dostalo `ZMĚŘENO` — **`Ě` chybí**. Je to **přesně ta
  třída vady, před kterou varuje `dsh-prostredi` §2b**, jen obráceně: *výpis*
  vypadal dobře a **vadný byl soubor**.

  Odhalil to až **mutační test**, který hledal `ZMĚŘENO` a nenašel ho.
  (Poučení: metrika, která se ptá na konkrétní řetězec, je zároveň kontrola
  diakritiky — když se neshoduje, může to být vada DAT, ne metriky.)

Použití: python _analyza\p13c-oprav-diakritiku.py
Návrat:  0 = hotovo (něco opraveno nebo už správně) | 2 = nález (nikde ani jedno)
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent

VADNY = "ZME\u0158ENO"       # ZMĚŘENO — chybí Ě
SPRAVNY = "ZM\u011a\u0158ENO"  # ZMĚŘENO

# Soubory, které to slovo používají (kód i dokumenty, které je citují).
SOUBORY = [
    "tools/verify-setup.py",
    "tools/lint-roadmapa.py",
    "_analyza/a3-over.py",
    "_analyza/g3-brany.py",
    "_analyza/f3-over-deploy.mjs",
    "_analyza/test-p13c-oprav.py",
    "_analyza/p13c-oprav-diakritiku.py",
    "HANDOFF.md",
]


def main() -> int:
    opraveno = 0
    spravne = 0
    for rel in SOUBORY:
        p = WS / rel
        if not p.is_file():
            print(f"  ?     {rel}: NENÍ")
            continue
        t = p.read_text(encoding="utf-8")
        pocet_vadny = t.count(VADNY)
        if pocet_vadny:
            t2 = t.replace(VADNY, SPRAVNY)
            assert t2 != t, f"{rel}: náhrada nic nezměnila"
            p.write_text(t2, encoding="utf-8", newline="")
            zpet = p.read_text(encoding="utf-8")
            assert VADNY not in zpet, f"{rel}: vadný text ZŮSTAL"
            print(f"  OPRAVENO {rel}: {pocet_vadny}×")
            opraveno += pocet_vadny
        if SPRAVNY in t or pocet_vadny:
            spravne += 1
        else:
            print(f"  POZOR {rel}: není tam ani vadný, ani správný tvar")

    print()
    print(f"VÝSLEDEK: {opraveno} výskytů opraveno, {spravne} souborů má správný tvar")
    return 0 if (opraveno or spravne) else 2


if __name__ == "__main__":
    sys.exit(main())

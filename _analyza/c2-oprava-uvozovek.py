# -*- coding: utf-8 -*-
"""Oprava VŠECH rozbitých českých uvozovek v `c2-oprav-n1.py` a výstupu.

Vzor vady: otevře se česká uvozovka `„`, ale zavře se ASCII `"`. Uvnitř
řetězce to řetězec ukončí a Python ohlásí `unterminated string literal` /
`'(' was never closed` na řádku, který vypadá správně (naměřeno 2. 10. 2026).

Postup: projdi řádek po řádku, spočítej české uvozovky. Když je otevíracích
`„` víc než zavíracích `“`, nahraď v tom řádku ASCII `"`, které následuje za
`„`, za `“`. Nic jiného se nemění.
"""

import ast
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
OTEV = "\u201e"   # „
ZAVR = "\u201c"   # “
ASCII = '"'

CILOVE = [
    WS / "_analyza" / "c2-oprav-n1.py",
    WS / "_analyza" / "hl-rizika-jazyka.py",
]


def oprav_radky(text: str) -> tuple[str, list]:
    """Vrátí (nový text, seznam oprav) — opravuje jen NEBALANCED řádky."""
    zmeny = []
    vysledek = []
    for i, radek in enumerate(text.splitlines(keepends=True), 1):
        if radek.count(OTEV) > radek.count(ZAVR):
            novy = radek
            # Nahraď ASCII uvozovku, která stojí ZA otevírací českou.
            for _ in range(radek.count(OTEV) - radek.count(ZAVR)):
                idx = -1
                hledat = 0
                while True:
                    o = novy.find(OTEV, hledat)
                    if o < 0:
                        break
                    a = novy.find(ASCII, o + 1)
                    if a >= 0:
                        idx = a
                        break
                    hledat = o + 1
                if idx < 0:
                    break
                novy = novy[:idx] + ZAVR + novy[idx + 1:]
            if novy != radek:
                zmeny.append((i, radek.strip()[:80]))
                radek = novy
        vysledek.append(radek)
    return "".join(vysledek), zmeny


celkem = 0
for cesta in CILOVE:
    if not cesta.is_file():
        print("CHYBA: %s neexistuje" % cesta)
        sys.exit(2)
    t = cesta.read_text(encoding="utf-8")
    novy, zmeny = oprav_radky(t)
    if novy == t:
        print("  %-24s beze změny" % cesta.name)
        continue
    cesta.write_bytes(novy.encode("utf-8"))
    z5 = cesta.read_text(encoding="utf-8")
    assert z5 == novy, "zápis nesedí"
    print("  %-24s opraveno %d řádků" % (cesta.name, len(zmeny)))
    for i, ukazka in zmeny:
        print("      %4d: %s" % (i, ukazka))
    celkem += len(zmeny)

print("\nopravených řádků celkem: %d" % celkem)
for cesta in CILOVE:
    try:
        ast.parse(cesta.read_text(encoding="utf-8"))
        print("  parsuje se OK: %s" % cesta.name)
    except SyntaxError as e:
        print("  CHYBA: %s — %s (řádek %s)" % (cesta.name, e.msg, e.lineno))
        sys.exit(1)

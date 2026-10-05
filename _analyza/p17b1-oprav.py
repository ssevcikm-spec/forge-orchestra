# -*- coding: utf-8 -*-
"""P17/B1 — OPRAVA: presun `from __future__ import annotations` pred preludium.

PROC TO TAKHLE: v tech sestech souborech stoji preludium z P8b
(`import pathlib as _pl` + odvozeni cest z `__file__`) NAD docstringem, a
`from __future__` je az pod docstringem. Python pozaduje, aby `from __future__`
byl prvni PRIKAZ souboru (pred nim smi byt jen docstring a komentare) — takze
jedina legalni pozice je PRED preludiem.

Zadani rika „na prvni radek po docstringu"; to by ale znamenalo prestehovat i
docstring a preludium, tedy vetsi zásah do kazdeho souboru. Zvolena je varianta
s MINIMALNI zmenou, ktera je funkcne shodna: `from __future__` se presune
i s nasledujicim prazdnym radkem PRED preludium. Docstring zustava tam, kde byl
(dnes taky NENI modulovy docstring, protože je za prikazy — `__doc__` je None)
a chovani souboru se tim nemeni.

BEZPECNOST: transformace se overi tremi nezavislymi zpusoby:
  1) multiset radku PRED a PO je shodny (jen se presouvaji, nic se neztraci),
  2) `compile()` vysledku projde,
  3) zapis jde BAJTECH a zachova BOM i konce radku (past `dsh-prostredi` §5b).

Pouziti: python _analyza/p17b1-oprav.py            (dry-run)
         python _analyza/p17b1-oprav.py --provest   (zapis)
"""

import collections
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
SOUBORY = [
    WS / "_analyza" / "p1-inventura-cest.py",
    WS / "_analyza" / "p1b-odvozene-cesty.py",
    WS / "_analyza" / "p3-bazline.py",
    WS / "tools" / "baseline-poznamka.py",
    WS / "tools" / "diag-baseline.py",
    WS / "tools" / "oprav-ps1-kodovani.py",
]
FUTURE = "from __future__ import annotations"
RE_IMPORT = re.compile(r"^\s*(import|from)\s")

provest = "--provest" in sys.argv
print("=" * 78)
print(f"P17/B1 — oprava `from __future__` ({'ZAPIS' if provest else 'DRY-RUN'})")
print("=" * 78)

chyby = 0
for cesta in SOUBORY:
    if not cesta.is_file():
        print(f"  CHYBA {cesta} neexistuje")
        chyby += 1
        continue
    raw = cesta.read_bytes()
    bom = b"\xef\xbb\xbf"
    ma_bom = raw.startswith(bom)
    text = raw[len(bom):].decode("utf-8") if ma_bom else raw.decode("utf-8")
    if "\r\n" in text:
        eol = "\r\n"
    else:
        eol = "\n"
    radky = text.splitlines(keepends=True)

    i_import = next((i for i, l in enumerate(radky) if RE_IMPORT.match(l)), None)
    i_future = next((i for i, l in enumerate(radky) if l.strip() == FUTURE), None)
    if i_import is None or i_future is None:
        print(f"  CHYBA {cesta.name}: import={i_import}, future={i_future} — přeskočeno")
        chyby += 1
        continue
    if i_import > i_future:
        print(f"  CHYBA {cesta.name}: future je UŽ před importem — nic se nemění")
        chyby += 1
        continue

    # blok = řádek future + jeden následující prázdný (pokud je)
    konec = i_future + 1
    if konec < len(radky) and radky[konec].strip() == "":
        konec += 1
    blok = radky[i_future:konec]
    zbytek = radky[:i_future] + radky[konec:]
    nove = zbytek[:i_import] + blok + zbytek[i_import:]

    # (1) multiset musí sedět — přesouvá se, neztrací
    if collections.Counter(radky) != collections.Counter(nove):
        print(f"  CHYBA {cesta.name}: multiset řádků se liší — NEZAPISUJI")
        chyby += 1
        continue
    novy_text = "".join(nove)
    if len(nove) != len(radky):
        print(f"  CHYBA {cesta.name}: změnil se počet řádků {len(radky)} → {len(nove)}")
        chyby += 1
        continue

    # (2) compile() musí projít
    try:
        compile(novy_text, str(cesta), "exec")
    except SyntaxError as e:
        print(f"  CHYBA {cesta.name}: po přesunu stále SyntaxError: {e}")
        chyby += 1
        continue

    out = (bom if ma_bom else b"") + novy_text.encode("utf-8")
    print(f"  OK    {cesta.relative_to(WS)}")
    print(f"        řádek {i_future + 1} → {i_import + 1}"
          f"   (blok {len(blok)} řádků, BOM={'ano' if ma_bom else 'ne'},"
          f" EOL={'CRLF' if eol == chr(13) + chr(10) else 'LF'})")
    if provest:
        cesta.write_bytes(out)
        # (3) ověření zápisu: bajty na disku musí dát tentýž text
        zpet = cesta.read_bytes()
        if zpet != out:
            print(f"        CHYBA: zápis na disk nesedí!")
            chyby += 1

print()
print("=" * 78)
print(f"VÝSLEDEK: {len(SOUBORY)} souborů, chyb {chyby}"
      f"{'' if provest else '  (dry-run — nic se nezapsalo)'}")
print("=" * 78)
sys.exit(1 if chyby else 0)

from __future__ import annotations

import pathlib as _pl

# P8 (presun na E:, 4. 10. 2026): cesta se ODVOZUJE z umisteni skriptu.
# `tools/` je primo v koreni repa, takze _PARENT = root repa.
_PARENT = _pl.Path(__file__).resolve().parents[1]
"""Opraví kódování PowerShell skriptu: UTF-8 BOM + JEDNOTNÉ konce řádků.

PROČ TO EXISTUJE — dvě chyby, které dokážou rozbít .ps1 tak, že to vypadá jako
chyba logiky:

  1) **Chybějící BOM.** PowerShell bez BOM čte soubor jako Windows-1252, české
     znaky se rozbijí (z jednoho písmene s diakritikou se stanou dva znaky)
     a parser hlásí nesmysly — v hlášce se místo českého slova objeví rozbité
     jméno. Ukázku sem ZÁMĚRNĚ nepíšu doslovnými znaky: zakazuje to `AGENTS.md`
     a `g1-diakritika-novych.py` to hlásí jako vadu souboru (naměřeno
     2. 10. 2026 — tenhle docstring byl jedno ze dvou takových míst).

  2) **Zdvojené konce řádků `\\r\\r\\n`.** Vzniknou, když se text s `\\r\\n`
     zapíše Pythonem bez `newline=''` – Python přeloží `\\n` na `\\r\\n` a druhé
     `\\r` zůstane. Naměřeno 1. 10. 2026: `test-local.ps1` měl po takovém zápisu
     **220 řádků místo 110** a parser hlásil chyby na řádku 167 (v souboru o 110
     řádcích), což poslalo diagnostiku úplně jinam. Prázdné řádky navíc přerušily
     i pokračování příkazu backtickem.

Vyřeší se to zápisem BAJTŮ: žádná tichá konverze konců řádků.

Použití: python orchestra/tools/oprav-ps1-kodovani.py
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SOUBORY = [
    pathlib.Path(_PARENT / 'tools' / 'test-local.ps1'),
    pathlib.Path(_PARENT / 'install-into-repo.ps1'),
]

BOM = b"\xef\xbb\xbf"

for cesta in SOUBORY:
    if not cesta.is_file():
        print(f"  --   {cesta.name}: neexistuje")
        continue

    b = cesta.read_bytes()
    puvodni = len(b)

    # 1) dekóduj (BOM se odstraní)
    text = b.decode("utf-8-sig")
    radku_pred = len(text.splitlines())

    # 2) sjednoť konce řádků: CRLF, a to PRÁVĚ JEDNO
    text = text.replace("\r\r\n", "\r\n").replace("\r\r", "\r")
    text = text.replace("\r\n", "\n").replace("\r", "\n")   # vše na LF
    text = text.replace("\n", "\r\n")                        # a zpět na CRLF

    # 3) zapiš BAJTY: BOM + obsah. Žádná konverze konců řádků.
    cesta.write_bytes(BOM + text.encode("utf-8"))

    b2 = cesta.read_bytes()
    ma_bom = b2.startswith(BOM)
    zdvojene = b2.count(b"\r\r")
    rozbito = [z for z in ("Ã", "Ä", "Å") if z in b2.decode("utf-8", "replace")]
    radku_po = len(b2.decode("utf-8-sig").splitlines())

    stav = "OK  " if (ma_bom and not zdvojene and not rozbito) else "CHYBA"
    print(f"  {stav} {cesta.name}: {puvodni} → {len(b2)} B, "
          f"řádků {radku_pred} → {radku_po}, "
          f"BOM={'ano' if ma_bom else 'NE'}, "
          f"zdvojené konce={zdvojene}, "
          f"dvojité kódování={rozbito or 'ne'}")

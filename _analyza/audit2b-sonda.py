r"""Sonda: do kterého ODDÍLKU (`## …`) patří každé číslo+„granul" a co je
v jeho okolí. Podklad pro opravu `audit2b-cisla-proti-zdroji.py` (Úkol 4).

PROČ: `audit2b` rozhoduje o tom, je-li výskyt „záznam", nebo „rozchod", jen
podle **řádku** (`CITACE` regex nad okolím řádku). Datum ale bývá v **nadpisu
oddílu** — a ten je nejsilnější znak minulosti (nález R3). Než něco přepíšu,
musím vidět, do kterého oddílu každý výskyt patří; jinak bych jen vyměnil
jeden slepý vzor za druhý (`overovani` §8.3: ptej se na VÝZNAM, ne na TVAR).

Sonda nic nemění.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
VZOR = re.compile(r"(\d+)\s+granul")
DATUM = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")
ZNAKY = ("Provedeno", "Ověření", "PROVEDENO", "OVĚŘENO", "Záznam", "záznam",
         "Omyly", "omylů")

for jmeno in ("AGENTS.md", "HANDOFF.md", "KRONIKA-PROJEKTU.md",
              "OTEVRENA-TEMATA.md", "NEXT-SESSION-INSTRUKCE.md",
              "PLAN-DALSI-KROK.md"):
    cesta = WS / jmeno
    if not cesta.is_file():
        continue
    s = cesta.read_text(encoding="utf-8")
    radky = s.splitlines()
    nalezy = list(VZOR.finditer(s))
    if not nalezy:
        continue
    print("=" * 100)
    print("%s — %d výskytů čísla+„granul" % (jmeno, len(nalezy)))
    print("=" * 100)
    for m in nalezy:
        radek = s[:m.start()].count("\n") + 1
        nadpis = "—— ŽÁDNÝ ## NAD TÍM ——"
        for i in range(radek - 1, -1, -1):
            if radky[i].startswith("## "):
                nadpis = radky[i]
                break
        znacky = [z for z in ZNAKY if z in nadpis]
        datum_v_nadpisu = bool(DATUM.search(nadpis))
        radek_text = radky[radek - 1] if radek - 1 < len(radky) else ""
        datum_na_radku = bool(DATUM.search(radek_text))
        print("\n  ř.%d  tvrdí %-4s | oddíl: %s" % (radek, m.group(1), nadpis[:74]))
        print("        nadpis: datum=%s znaky=%s | řádek: datum=%s"
              % ("ANO" if datum_v_nadpisu else "ne",
                 ",".join(znacky) if znacky else "—",
                 "ANO" if datum_na_radku else "ne"))
        print("        …%s…" % re.sub(r"\s+", " ", radek_text).strip()[:104])
    print()

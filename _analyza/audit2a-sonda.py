r"""Sonda: K ČEMU patří každé číslo+„sloupc" v dokumentech (podklad pro opravu
`audit2a-schema.py`).

Motivace (naměřeno 2. 10. 2026): brána `audit2a-schema.py` hlásí 6 „ROZCHODŮ",
ale ani jeden z nich není tvrzení o DNEŠKU:
  * 3× je to CITACE dřívějšího chybného tvrzení („AGENTS.md tvrdil „32 sloupců"")
  * 2× je to DATOVANÝ ZÁZNAM (39 sloupců, než B1 přidal sloupec)
  * 1× je to tabulka s živým číslem 40 (SOUHLASÍ)
A skutečné tvrzení, které R1 popisuje („správně je **39**"), brána
**vůbec nevidí** — vzor `(\d+)\s+sloupc` potřebuje slovo „sloupců" hned za
číslem, a v té větě stojí „**39** — a schéma…".

Sonda nic nemění — jen vypisuje okolí a nadpis oddílu.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
VZOR = re.compile(r"(\d+)\s+sloupc")

for jmeno in ("AGENTS.md", "KRONIKA-PROJEKTU.md", "HANDOFF.md"):
    cesta = WS / jmeno
    if not cesta.is_file():
        continue
    s = cesta.read_text(encoding="utf-8")
    radky = s.splitlines()
    print("=" * 96)
    print(jmeno)
    print("=" * 96)
    for m in VZOR.finditer(s):
        radek = s[:m.start()].count("\n") + 1
        # nadpis oddilu: posledni radek zacatek "## " nad timto radkem
        nadpis = "—"
        for i in range(radek - 1, -1, -1):
            if radky[i].startswith("## "):
                nadpis = radky[i][:88]
                break
        kontext = s[max(0, m.start() - 110):m.end() + 70].replace("\n", " ")
        print("\n  řádek %-4d tvrdí %-3s" % (radek, m.group(1)))
        print("    oddíl  : %s" % nadpis)
        print("    kontext: …%s…" % kontext)
    print()

# -*- coding: utf-8 -*-
"""Doplní do `HANDOFF.md` §24.4 naměřený výsledek porovnání se snapshotem.

⚠ `edit` tool na `HANDOFF.md` hlásí „file changed since it was read" — do
souboru sáhly **mutační testy** téhle session (a vrátily ho bit po bitu).
Zapisuje se **jedním** `write_bytes` a ověřuje se **A2** (nic nezmizelo).
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"

orig = H.read_bytes()
text = orig.decode("utf-8")

KOTVA = """> **Druhý výskyt téhož nálezu H28 v jedné session** — a důkaz, že NA20 není
> formalita: kdo se ptá na `mtime`, řekne „pracuje v tom jiná session".
"""

DOPLNENI = KOTVA + """
> **A naměřeno POTŘETÍ, nezávislým nástrojem:**
> `python _analyza\\audit-snapshot.py --jen-kontrola --proti _analyza\\snapshot-20261002-183213`
> → `zmenenych OBSAHEM=6 · pridanych=2 · odebranych=0 · jen mtime=6`.
> **Obsahem** se změnilo **6** (což je **3 soubory ve dvou pohledech** —
> `jadro/` a `koren/`, past, kterou zadání správně označilo za kosmetiku):
> `HANDOFF.md`, `KRONIKA-PROJEKTU.md`, `PLAN-DALSI-KROK.md` — a to je **práce
> téhle session**. **Jen `mtime`** se změnil u **tří dalších**: `AGENTS.md`,
> `NEXT-SESSION-INSTRUKCE.md` a `PREDAVANI-SESSION.md`.
>
> **A u `AGENTS.md` je to doložené hashem:** `3204ca59c33b260a64ee91c0…`,
> **42 173 B** — **shodný se snapshotem**. Tedy **žádná mutace nezůstala
> neočištěná**: `ag-mutace.py` i `audit2a-mutace.py` vrátily soubor **bit po
> bitu**, jen mu **posunuly `mtime`**. **Kdyby se session ptala na `mtime`,
> hlásila by tři „změněné" dokumenty, které se nezměnily ani o bajt** —
> a kdyby se ptala jen na počet, **spletla by 6 změn s 3 soubory**.

"""

if "zmenenych OBSAHEM=6" in text:
    print("odstavec už v HANDOFF.md je — nic se nemění.")
    sys.exit(0)

assert text.count(KOTVA) == 1, "kotva je v souboru %dx" % text.count(KOTVA)

novy = text.replace(KOTVA, DOPLNENI, 1)
chyby = [l[:90] for l in text.splitlines() if l.strip() and l not in novy]
if chyby:
    print("CHYBA: %d řádků původního textu v novém NENÍ:" % len(chyby))
    for c in chyby[:10]:
        print("   %s" % c)
    sys.exit(1)

H.write_bytes(novy.encode("utf-8"))
zpet = H.read_bytes()
print("původně : %d B · nově: %d B (+%d)" % (len(orig), len(zpet), len(zpet) - len(orig)))
print("kontrola A2: všech %d neprázdných řádků původního textu zůstalo"
      % len([l for l in text.splitlines() if l.strip()]))
print("zápis   : %s" % ("OK" if zpet == novy.encode("utf-8") else "CHYBA"))

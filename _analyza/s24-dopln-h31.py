# -*- coding: utf-8 -*-
"""Doplní do `HANDOFF.md` §24.7 odstavec o nálezu **H31** (přiznaná mez).

Důvod samostatného skriptu: `HANDOFF.md` je 325 kB a `edit` tool hlásí
„file changed since it was read", protože do souboru sáhly **mutační testy**
téhle session (a vrátily ho bit po bitu — proto je hash pořád stejný).
Zapisuje se **jedním** `write_bytes` a před i po zápisu se ověřuje **A2**:
původní obsah musí být v novém CELÝ.
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"

orig = H.read_bytes()
text = orig.decode("utf-8")

KOTVA = """**Je to počtvrté, co se to stalo** — a poučení je: **výstup brány nepatří
do složky, kterou brána prochází**; ukládej ho mimo, nebo ho před dalším
během ukliď.
"""

DOPLNENI = KOTVA + """
> **A jeden nález, který k tomu patří a je PŘIZNANOU MEZÍ (H31):** oprava
> opatření 6 (projití složky) **musí** vyloučit **zálohy a snapshoty** — jinak
> by brána hlásila vadu na souborech, které **mají právo být rozbité** (jsou to
> snímky stavu PŘED opravou). Vylučuje se ale podle **JMÉNA** (`_zaloha*`,
> `*-pred-*`, `snapshot-*`) — a to je **ruční seznam o vrstvu níž**
> (`overovani` §9.5: výjimka klíčovaná jménem je ruční seznam). **Naměřeno:
> vyloučeno 8 souborů** a **počet se vypisuje**, takže to **není slepota** —
> ale je to **mez**: kdyby se zálohy začaly pojmenovávat jinak, brána začne
> hlásit **falešné poplachy**. Zapsáno v `KRONIKA-PROJEKTU.md` §2.5.
"""

if "H31" in text:
    print("H31 už v HANDOFF.md je — nic se nemění.")
    sys.exit(0)

assert text.count(KOTVA) == 1, "kotva je v souboru %dx" % text.count(KOTVA)

novy = text.replace(KOTVA, DOPLNENI, 1)

# A2: nic nesmí zmizet
chyby = [l[:90] for l in text.splitlines() if l.strip() and l not in novy]
if chyby:
    print("CHYBA: %d řádků původního textu v novém NENÍ:" % len(chyby))
    for c in chyby[:10]:
        print("   %s" % c)
    sys.exit(1)

H.write_bytes(novy.encode("utf-8"))
zpet = H.read_bytes()
print("původně : %d B" % len(orig))
print("nově    : %d B (+%d)" % (len(zpet), len(zpet) - len(orig)))
print("kontrola A2: všech %d neprázdných řádků původního textu zůstalo"
      % len([l for l in text.splitlines() if l.strip()]))
print("zápis   : %s" % ("OK" if zpet == novy.encode("utf-8") else "CHYBA"))
print("výskytů H31: %d" % zpet.count(b"H31"))

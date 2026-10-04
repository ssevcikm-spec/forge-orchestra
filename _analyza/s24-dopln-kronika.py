# -*- coding: utf-8 -*-
"""Doplní do `KRONIKA-PROJEKTU.md` nález **H32** a aktualizuje řádek #20.

Kronika je **append-only** — nic se nepřepisuje, jen se doplňuje.
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
K = WS / "KRONIKA-PROJEKTU.md"
orig = K.read_bytes()
text = orig.decode("utf-8")

# ── 1) H32 za H31 ──────────────────────────────────────────────────────────
KOTVA_H31 = "| **H31** | **PŘIZNANÁ MEZ opravy opatření 6"
i = text.find(KOTVA_H31)
assert i >= 0, "kotva H31 nenalezena"
konec_radku = text.find("\n", i)
assert konec_radku > 0

H32 = """
| **H32** | **`audit2b` měl ZKRÁCENÝ VÝPIS (`histor[:40]`) a shazoval tím svého ověřovatele.** Když session připsala do `HANDOFF.md` §24, spadl `audit2b-over.py` na `exit 1` s hláškou „HANDOFF.md:1201 `granulí` NENÍ v ZÁZNAMECH". **Nebyla to pravda.** Kotva je na **ř. 1201**, tedy **za** hranicí 40 záznamů, které nástroj vypisuje — **v ZÁZNAMECH JE, jen se to nevypíše**, a ověřovatel parsuje **stdout**. **Trvalo PĚT měření, než se příčina našla** (čtyři „opravy" mířily vedle: nadpisy `###`, velká písmena, vzor, filtr). Je to **táž past, kterou táž session zapsala o hodinu dřív jako vlastní omyl 97** — a spadla do ní znovu, v **cizím** nástroji. **Opraveno:** nový přepínač `--vsezáznamy`/`--vsechny-zaznamy` (mění **jen výpis, ne měření**), ověřovatel ho použije a **vypíše, že to bylo zkrácením**; `audit2b-over.py` → `exit 0` | **opraveno** — a zapsáno jako past: *měřidlo nesmí mít v cestě zkrácení, aniž to řekne*; kdo ho ověřuje, **čte nejdřív jeho VÝPISNÍ CESTU** | tato session |
"""

if "| **H32** |" not in text:
    text = text[:konec_radku + 1] + H32 + text[konec_radku + 1:]

# ── 2) řádek #20 — doplnit H32 a opravu měřidla ────────────────────────────
STARY = """| **20** | 2. 10. 2026 16:4x | **plánovací (ověřovací)** |"""
i20 = text.find(STARY)
assert i20 >= 0, "řádek #20 nenalezen"
k20 = text.find("\n", i20)

DOPLNEK = (" **Navíc naměřeno a opraveno:** `audit2b` měl **zkrácený výpis** "
           "(`histor[:40]`) a shazoval tím svého ověřovatele (**H32**, omyly "
           "**102–104**, pět měření na jednu příčinu); vzor pro `granulí` "
           "chytal **12 ze 14** reálných tvarů → **14 ze 14**.")

if "H32" not in text[i20:k20]:
    text = text[:k20] + DOPLNEK + text[k20:]

novy = text.encode("utf-8")
chyby = [l[:90] for l in orig.decode("utf-8").splitlines()
         if l.strip() and l not in text]
if chyby:
    print("CHYBA: %d řádků původního textu v novém NENÍ:" % len(chyby))
    for c in chyby[:10]:
        print("   %s" % c)
    sys.exit(1)

K.write_bytes(novy)
zpet = K.read_bytes()
print("původně : %d B · nově: %d B (+%d)"
      % (len(orig), len(zpet), len(zpet) - len(orig)))
print("kontrola A2: všech %d neprázdných řádků původního textu zůstalo"
      % len([l for l in orig.decode("utf-8").splitlines() if l.strip()]))
print("zápis   : %s" % ("OK" if zpet == novy else "CHYBA"))
print("H32: %d" % zpet.count(b"H32"))

# -*- coding: utf-8 -*-
"""Připíše do `HANDOFF.md` samostatný blok **§24.15 + §8k (102–104)**.

⚠ Vědomé rozhodnutí: **needituje se doprostřed** existujících odstavců
(předchozí pokus rozbil řádek a A2 kontrola ho správně zastavila) — připisuje
se **na konec**, což je pro append-only dokument bezpečné a přesně to, co A2
vyžaduje.
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"
orig = H.read_bytes()
text = orig.decode("utf-8")

BLOK = """
### 24.15 ⚠ NÁLEZ **H32** — `audit2b` měl ZKRÁCENÝ VÝPIS a shazoval tím svého ověřovatele

*(Dopsáno na konec §24, protože vkládání doprostřed odstavců rozbíjí řádky —
A2 kontrola to správně zastavila.)*

**Naměřeno 2. 10. 2026 (20:0x).** Když tahle session připsala do `HANDOFF.md`
§24, spadl `audit2b-over.py` na **`exit 1`** s hláškou
*„HANDOFF.md:1201 `granulí` NENÍ v ZÁZNAMECH"*. **Nebyla to pravda** — a trvalo
**pět měření**, než se našla skutečná příčina:

| # | Co jsem zkusil | Co to udělalo |
|---|---|---|
| 1 | rozšířit `nadpis_oddilu` na `### ` | **zhoršilo** (31 → **127** rozchodů): `###` nadpisy v `HANDOFF.md` nesou texty omylů a tabulek |
| 2 | doplnit `ZNAKY_ODDILU` o další slova | neškodné, ale **nebyla to příčina** |
| 3 | upravit vzor pro `granulí` (hvězdičky) | **správné zlepšení** — `(\\d+)\\s*\\**\\s*granul` chytí **14 ze 14** reálných tvarů proti **12 ze 14** — ale **taky to nebyla příčina** |
| 4 | filtrovat kotvu jiným slovem | neškodné — **nebyla to příčina** |
| **5** | **přečíst, co nástroj SKUTEČNĚ vypisuje** | **PŘÍČINA: `histor[:40]`.** Nástroj tiskne ze ZÁZNAMŮ jen **prvních 40**; kotva je na **ř. 1201**, tedy **za** hranicí. **V ZÁZNAMECH JE — jen se to nevypíše**, a ověřovatel parsuje **stdout**. |

**Je to táž past, kterou táž session zapsala o hodinu dřív jako vlastní omyl 97**
(„měřil jsem podle výpisu, a výpis je zkrácený") — a **spadla do ní znovu**,
tentokrát v **cizím** nástroji.

> **Pravidlo:** *měřidlo, které má předat stav, nesmí mít v cestě zkrácení,
> aniž to řekne* — a kdo ho ověřuje, musí si **nejdřív přečíst jeho VÝPISNÍ
> CESTU**, ne jeho výsledek.

**Oprava (provedena):** `audit2b-cisla-proti-zdroji.py` má nový přepínač
**`--vsechny-zaznamy`** — mění **jen výpis, ne měření** — a `audit2b-over.py`
ho použije, když kotvu v parsovaném výpisu nenajde, a **vypíše, že to bylo
zkrácením**. **Ověřeno: `audit2b-over.py` → `exit 0`, 0 chyb.**

### 24.16 Vlastní omyly 102–104 (dopsané k témuž nálezu)

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **102** | **„Přesnější" není totéž co „lepší"** | do `nadpis_oddilu()` v `audit2b` jsem rozšířil hledání nadpisu z `## ` na `## ` **i `### `** s odůvodněním „nejbližší nadpis je přesnější" | **běh hned ukázal opak:** rozchodů **31 → 127** | **Vráceno** a do kódu zapsáno s čísly. `overovani` §9.7: opravuješ-li měřidlo, **mutačně ověř OPRAVU** |
| **103** | **Pět měření na jednu příčinu — čtyři mířila vedle** | `audit2b-over.py` hlásil „kotva není v ZÁZNAMECH"; opravil jsem postupně **čtyři různé vrstvy**, než jsem **přečetl, co nástroj vypisuje** | Příčina byla **pátá**: `histor[:40]` | **Pravidlo (`overovani` §10.5 a §8.4):** než začnu opravovat, **vypiš si OKOLÍ a VÝPISNÍ CESTU** nástroje. „Vypadá to jako vada" není diagnóza |
| **104** | **Spadl jsem do pasti, kterou jsem SI SÁM zapsal o hodinu dřív** | omyl **97** téže session zní *„měřil jsem podle VÝPISU, a výpis je zkrácený"* — a stalo se to znovu, jen v **cizím** nástroji | `audit2b-over.py` parsuje **stdout** a kotva je **za** hranicí 40 záznamů | **Zapsáno jako H32.** Když si session zapíše past, **musí ji hledat i u cizích nástrojů** — ne jen u svých |

**Trend se tím nemění k lepšímu:** omyl **103** je **čtvrtý** výskyt téže třídy
(„měřidlo/ověřovatel odpovídá na jinou otázku") v jedné session — po **97**
(zkrácený výpis), **98** (neměřená část) a **99** (třikrát špatný směr kontroly).
"""

if "24.15" in text:
    print("§24.15 už v dokumentu je — nic se nemění.")
    sys.exit(0)

novy_text = text.rstrip("\n") + "\n" + BLOK
novy = novy_text.encode("utf-8")

# A2: každý neprázdný řádek původního textu musí v novém zůstat
chyby = [l[:90] for l in text.splitlines() if l.strip() and l not in novy_text]
if chyby:
    print("CHYBA: %d řádků původního textu v novém NENÍ:" % len(chyby))
    for c in chyby[:10]:
        print("   %s" % c)
    sys.exit(1)

H.write_bytes(novy)
zpet = H.read_bytes()
print("původně : %d B · nově: %d B (+%d)"
      % (len(orig), len(zpet), len(zpet) - len(orig)))
print("kontrola A2: všech %d neprázdných řádků původního textu zůstalo"
      % len([l for l in text.splitlines() if l.strip()]))
print("zápis   : %s" % ("OK" if zpet == novy else "CHYBA"))
print("H32: %d · omyl 102: %d · omyl 104: %d"
      % (zpet.count(b"H32"), zpet.count(b"| **102** |"), zpet.count(b"| **104** |")))

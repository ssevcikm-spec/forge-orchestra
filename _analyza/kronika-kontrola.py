# -*- coding: utf-8 -*-
r"""Kontrola KRONIKY — je skutečně úplná, nebo si to jen říká?

PROČ: `KRONIKA-PROJEKTU.md` tvrdí, že je **jediné místo s celým příběhem**.
Takový nárok se musí dát ověřit, jinak je to jen další dokument, který
„vypadá jako přehled" (táž třída jako brána, která nic neotevřela — S27).

CO KONTROLUJE (každý bod je čitelný z výstupu):

  A) **Počty omylů podle bloků** — tvrzení v kronice §3 vs. skutečný počet
     řádků v tabulkách `HANDOFF.md`. Počítá se **počet omylů**, ne počet znaků.
     ⚠ **Bloky se od 3. 10. 2026 HLEDAJÍ V DOKUMENTU** (`bloky_omylu`), ne
     v pevném seznamu — pevný seznam byl **pětkrát** důvodem téhož nálezu
     (NA17: nový blok omylů vypadl z počtu a nikde to nebylo vidět).
     Měří se **oba směry**: blok bez řádku v kronice i řádek v kronice bez bloku.
  B) **Nálezy H1–H7** — každý musí být zmíněný v `HANDOFF.md` (odkud vzešel).
  C) **Sessions v tabulce §1** — musí být aspoň tolik, kolik je bloků omylů
     + hlavní sessions podle `HANDOFF.md` §17; a každá musí mít datum.
  D) **Odkazy na zdroje** — každý dokument zmíněný v §1–§4 musí existovat.
  E) **Počet session z živého měření** — kontrola, že číslo „108 sessions"
     není vymyšlené (bere se z `dsh-usage`, ne z kroniky).

Použití:  python _analyza\kronika-kontrola.py
          python _analyza\kronika-kontrola.py <KRONIKA.md> <HANDOFF.md>   (fixtura)

Návrat:   0 = vše sedí | 1 = rozchod (co a kde se vypíše)

⚠ PROČ JDE ZADAT CESTY (doplněno 2. 10. 2026): bez toho se brána dala testovat
jen na ŽIVÉ kronice — a to nestačí. Vada, kterou hledáme (počítání cizí
tabulky), vzniká **jen na určitém tvaru dokumentu**: blok omylů musí
následovat hned za tabulkou nálezů. Fixtura takový tvar vyrobí **řízeně**;
živý dokument se mění a test by závisel na jeho dnešní podobě.
(Je to táž zásada jako u `overovani` §2.3: brána má vypsat, CO změřila —
a mít fixturu, kde musí hlásit vadu, i kde nesmí.)
"""

import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
# P8 (presun na E:, 4. 10. 2026): hra je SOUROZENEC repa, ne potomek
# (`games/uo-shadows` uz neexistuje). Kronika na ni odkazuje relativnimi
# cestami (`docs/ARCHITEKTURA.md`), takze se existence overuje v ni.
_HRA = WS.parent / "uo-shadows"
# Cesty lze přebít argumenty — používá to `t3-kronika-mutace.py`.
KRONIKA = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else WS / "KRONIKA-PROJEKTU.md"
HANDOFF = pathlib.Path(sys.argv[2]) if len(sys.argv) > 2 else WS / "HANDOFF.md"

chyby = []
pokud = []

if not KRONIKA.is_file():
    print("CHYBA: %s neexistuje" % KRONIKA)
    sys.exit(1)

kron = KRONIKA.read_text(encoding="utf-8")

# ⚠ OD 7. 10. 2026 JE HISTORIE PŘESUNUTÁ (optimalizace KB, Úkol C, měřeno):
# z `HANDOFF.md` (674 723 znaků, 93,8 % historie) se do `_archiv\` přesunuly
# oddíly **§8 (omyly)** a **§10–§39 (záznamy session)** — **bajt na bajt**
# (dokázáno: 0 chybějících řádků v multimnožině a shodné sha256 bloků,
# `_kb\over-presun-historie.py`). Tahle brána z HANDOFFu čte **tabulky omylů
# (bloky `8xx`), nálezy H1–H7 a sessions §17** — tedy přesně to, co se
# přesunulo. Proto se dívá do `HANDOFF.md` **I DO ARCHIVŮ**; jinak by hlásila
# „nález v kronice, ale v HANDOFF.md není" u ~40 nálezů, které se jen přesunuly
# (naměřeno po přesunu: `exit 1` ze špatného důvodu).
#
# ⚠ PŘI MUTAČNÍM BĚHU (fixtura jako 2. argument) SE ARCHIVY NEČTOU: `t3-kronika-mutace.py`
# maže kotvu z fixtury a chce vidět, že to brána POZNÁ. Kdyby jí archiv pomohl,
# test by byl slepý přesně v tom, co měří.
if len(sys.argv) > 2:
    _zdroje = [HANDOFF]
else:
    _zdroje = [HANDOFF] + sorted((WS / "_archiv").glob("HANDOFF-*.md"))
hand = "\n".join(p.read_text(encoding="utf-8") for p in _zdroje if p.is_file())


def blok(text: str, od: str, do: str | None) -> str:
    """Vrátí výřez dokumentu mezi dvěma kotvami (jednoznačnými nadpisy)."""
    i = text.find(od)
    if i < 0:
        return ""
    if do is None:
        return text[i:]
    j = text.find(do, i + len(od))
    return text[i:j] if j > 0 else text[i:]


def najdi_radek_nadpisu(text: str, od: str) -> int:
    """Index znaku, kde začíná ŘÁDEK, jehož text začíná na `od`. Jinak -1.

    ⚠ PROČ NE `text.find(od)` (naměřeno 2. 10. 2026, stálo to tři kola):
    `find()` najde i **zmínku o kotvě uvnitř textu**. Konkrétně: `### 8g. Omyly
    PLÁNOVACÍ` je v `HANDOFF.md` **dvakrát** — jednou jako nadpis a podruhé
    **v próze omylu 76** („mutační test si vzal kotvu `(\"8g\", …)`"). A ještě
    horší varianta téhož: `## 8. Vlastní omyly` leží na **prvním řádku** souboru
    v tom smyslu, že `rfind("\\n", 0, i)` vrátí **-1** → `radek_zacatek` se
    dostal na **0**, regex nad celým prefixem nenašel nic a funkce tiše vrátila
    **celý zbytek dokumentu** (200 kB místo 1 kB). Počty pak vyšly
    **135 místo 13** — a to vypadá jako nález o datech.

    Hledá se proto **po řádcích** a porovnává se **začátek řádku**. Když se
    nenajde, funkce to řekne (`-1`), místo aby vrátila něco jiného.
    """
    pozice = 0
    for radek in text.splitlines(keepends=True):
        if radek.startswith(od):
            return pozice
        pozice += len(radek)
    return -1


def blok_do_nadpisu(text: str, od: str, dalsi: list | None = None) -> str:
    """Výřez od kotvy `od` po nejbližší KONEC bloku.

    Konec bloku je nejbližší z:
      * nadpis **stejné nebo vyšší úrovně** (méně nebo stejně křížků), než má
        nadpis, kterým blok začíná, NEBO
      * nadpis kteréhokoli **následujícího bloku omylů** (`dalsi`) — protože
        bloky mají různou úroveň (`## 8.` vs. `### 8b.`), samotná úroveň na
        oddělení nestačí.

    ⚠ PROČ TO EXISTUJE (naměřeno 2. 10. 2026):
    bloky omylů se do `HANDOFF.md` **připisují na různá místa** — `8g` je za
    §17, `8h` se vložil mezi `8g` a `## 18.`. **Poziční kotva („do `## 18.`")
    tím přestala rozlišovat bloky**: okno `8g` spolklo celý `8h`
    (**19 omylů místo 11**). A kotva na text se taky nedá použít — uzavírací
    odstavec bloku `8g` je **citovaný v próze bloku `8h`**, takže `find()` na
    něj sáhne uvnitř `8h`. **Nadpis je jediná kotva, která znamená totéž
    v každém uspořádání.**
    """
    i = najdi_radek_nadpisu(text, od)
    if i < 0:
        return ""
    m = re.match(r"(#+)\s", od)
    if not m:
        return text[i:]
    uroven = len(m.group(1))
    kandidati = list(dalsi or [])
    konec = len(text)
    pozice = i + len(od)
    for radek in text[pozice:].splitlines(keepends=True):
        m2 = re.match(r"(#+)\s", radek)
        if m2 and (len(m2.group(1)) <= uroven or any(radek.startswith(k) for k in kandidati)):
            konec = pozice
            break
        pozice += len(radek)
    return text[i:konec]


def pocet_omylu(vyrez: str) -> int:
    """Počet řádků tabulky, které začínají číslem omylu ve sloupci `| **N** |`.

    POZOR: musí to být **řádek tabulky omylů**, ne každý výskyt `| **N** |`
    v dokumentu — jinak by se počítaly i odkazy v textu (past: „dva čítače
    téhož jména"). Proto se hledá na ZAČÁTKU řádku.

    ⚠ A nestačí ani to — naměřeno 2. 10. 2026: v bloku `8f` se počítalo **54**
    místo **10**, protože do výřezu spadla tabulka **nálezů** v §18.11
    (`| **H8** | … |`) a ta má na začátku taky `| **N**`. Proto se navíc
    vyžaduje **ČISTĚ ČÍSELNÉ id** (žádné písmeno — `H8` neprojde).

    ⚠ A POZOR na „chytré" kritérium: první oprava se ptala na `radek.count("|")`,
    jenže buňky obsahují znak `|` **uvnitř kódu i v escapované podobě** (řádek 50
    jich má **5**, řádek omylu 44 taky **5**) → oprava vyhodila **všechny** řádky
    a brána hlásila 0 omylů. **Počet oddělovačů není identifikátor řádku.**
    Falešný poplach na správném vstupu je stejná vada jako slepá kontrola.
    """
    n = 0
    for radek in vyrez.splitlines():
        # ⚠ POZOR na tuhle kotvu: nesmí se ptát na `\|` na konci id, protože
        # tabulka je psaná **bez mezer** (`| **50** |`, kde je `50` hned mezi
        # hvězdičkami a svislítkem) — první verze opravy to udělala a vrátila 0.
        m = re.match(r"^\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", radek)
        if m:
            n += 1
    return n


print("=" * 78)
print("KONTROLA KRONIKY — je úplná, nebo si to jen říká?")
print("=" * 78)

# ---------------------------------------------------------------- A) omyly
print()
print("A) POČTY OMYLŮ — kronika §3 vs. skutečné tabulky v HANDOFF.md")
print("-" * 78)

# ═══════════════════════════════════════════════════════════════════════════
# BLOKY SE HLEDAJÍ V DOKUMENTU — PEVNÝ SEZNAM JE ZRUŠEN (3. 10. 2026)
#
# Do 3. 10. 2026 tu byl **pevný seznam kotev** (`BLOKY = [...]`) a byl to
# **pětkrát** důvod téhož nálezu (**NA17**, `HANDOFF.md` §22.5 / H18): `8i`,
# `8j`, `8k`, `8l`, `8m` — a po každém připsání nového bloku omylů počítala
# brána **staré číslo** a nebylo to nikde vidět. Naposledy `8n`: brána hlásila
# **107**, kdežto součet řádků tabulky v kronice §3 byl **118**.
#
# **Je to táž vada, kterou projekt řeší jinde jako S27** („ruční seznam místo
# projití složky“) — jen o patro výš: ne ruční seznam SOUBORŮ, ale ruční seznam
# BLOKŮ. Náprava je proto stejná jako u `kontrola-diakritiky.py`: **projít
# dokument**, ne seznam. Odhalila to kontrola v `s24-meridla-over.py`, která se
# ptala **naopak** („má každý nadpis v dokumentu kotvu v bráně?“) a byla kvůli
# `8n` červená.
#
# **Co to mění a co ne:** počítá se pořád **počet řádků tabulky** v bloku
# (stejná funkce `pocet_omylu`), jen se bloky berou z dokumentu. Nový blok
# omylů tím **nelze vynechat** — a když v kronice §3 chybí jeho řádek, brána
# to **ohlásí** (opačný směr, ten dřív chyběl úplně).
# ═══════════════════════════════════════════════════════════════════════════
VZOR_BLOKU = re.compile(r"^(#{2,3})\s+(8[a-z]{0,2})\.\s")
# Klíč `1–13` NENÍ název bloku — je to v kronice §3 označení SPOLEČNÉ tabulky
# omylů („řádky mezi `## 8.` a `### 8b.`“). Nadpis se jmenuje `## 8.`, takže
# se klíč mapuje; jinak by brána u základního bloku hledala řádek `8`.
KLIC_ZAKLADNIHO_BLOKU = "1–13"


def bloky_omylu(text: str) -> list:
    """Vrátí `[(klíč, nadpis)]` pro VŠECHNY bloky omylů v dokumentu.

    Hledá se **na začátku řádku** (stejný predikát jako `najdi_radek_nadpisu`
    níž) — nikdy `text.find()`, protože kotva `### 8g. Omyly PLÁNOVACÍ` je
    v dokumentu i **citovaná v próze** (naměřeno: omyl 76). Pořadí je **pořadí
    v dokumentu**, protože právě to potřebuje `blok_do_nadpisu` pro `dalsi`.
    """
    out = []
    for radek in text.splitlines():
        m = VZOR_BLOKU.match(radek)
        if m:
            klic = KLIC_ZAKLADNIHO_BLOKU if m.group(2) == "8" else m.group(2)
            out.append((klic, radek.strip()))
    return out


BLOKY = bloky_omylu(hand)
if not BLOKY:
    # Nula a „nezměřeno“ nejsou úspěch: bez jediného nadpisu by součet vyšel 0
    # a vypadal by jako NAMĚŘENÁ NULA (přesně to řešil nález H17).
    chyby.append("v HANDOFF.md není ANI JEDEN nadpis bloku omylů (%r) — "
                 "počet omylů je NEZMĚŘENÝ" % VZOR_BLOKU.pattern)
    print("  CHYBA: žádný nadpis bloku omylů nenalezen → počet omylů NEZMĚŘEN")

# ⚠ KONCE BLOKŮ SE NEURČUJE KOTVOU, ALE NADPISEM (2. 10. 2026).
# Do téhle session měl každý blok **dvojici kotva-od / kotva-do** a byla to
# past, která se projevila **třikrát**:
#   1. „do konce souboru" u `8f` spolklo tabulky §15–§18 (naměřeno **10 místo 7**),
#   2. „do `## 18.`" u `8g` spolklo celý nový blok `8h` (**19 místo 11**),
#   3. kotva na uzavírací odstavec bloku `8g` se nedala použít — ten odstavec je
#      **citovaný v próze bloku `8h`**, takže `find()` sáhl uvnitř `8h`.
# **Proč to tak je:** oddíly se do `HANDOFF.md` **připisují na různá místa**
# (nové bloky omylů jdou za tabulku, výsledky na konec), takže **pořadí ani
# sousedství není stabilní**. Nadpis je jediná kotva, která znamená totéž
# v každém uspořádání → `blok_do_nadpisu()`.
skutecne = {}
_VSE_ANCHORY = [od for _n, od in BLOKY]
for _idx, (nazev, od) in enumerate(BLOKY):
    # Následující bloky (jejich nadpisy blok ukončují i na nižší úrovni).
    dalsi = _VSE_ANCHORY[_idx + 1:]
    # ⚠ TŘI STAVY, ne dva (naměřeno 2. 10. 2026, fixtura `t3-kronika-mutace.py`):
    # když se kotva (nadpis bloku) v `HANDOFF.md` nenajde, výřez je `""`
    # a `pocet_omylu("")` vrátí **0**. To se pak vypíše jako
    # „skutečný počet omylů: 0" — tedy jako NAMĚŘENÁ NULA. Přitom je to
    # NEZMĚŘENO. A protože kronika tvrdí 6, rozdíl 6 vs. 0 vypadá jako nález
    # o datech, ne o bráně. (Tatáž past, na kterou upozorňuje `AGENTS.md`:
    # „nula a »nezměřeno« nejsou úspěch".) Proto se přítomnost NADPISU měří
    # zvlášť a nepřítomnost se hlásí jako `None` = nezměřeno.
    if najdi_radek_nadpisu(hand, od) < 0:
        # ⚠ TÝŽ PREDIKÁT, KTERÝM SE PAK HLEDÁ (poučení **L18**, `HANDOFF.md`
        # §22.6): dřív se na přítomnost ptalo `od in hand` (kdekoliv v textu),
        # ale výřez bral `radek.startswith(od)` (začátek řádku) — u kotvy
        # citované v próze to vypsalo „naměřenou nulu“. Kotvy se teď berou
        # z dokumentu, takže se rozejít nemohou; predikát zůstává SHODNÝ schválně.
        chyby.append("v HANDOFF.md NENÍ nadpis bloku omylů %r — "
                     "počet omylů se NEZMĚŘIL" % od)
        print("  %-8s nadpis bloku NENALEZEN → NEZMĚŘENO (kotva %r)" % (nazev, od))
        continue
    v = blok_do_nadpisu(hand, od, dalsi)
    skutecne[nazev] = pocet_omylu(v)
    print("  %-8s skutečný počet omylů: %3d" % (nazev, skutecne[nazev]))

# Tvrzení z kroniky §3 (tabulka počtů omylů).
# ⚠ SEKCE SE V TÉHLE SESSION PŘEČÍSLOVALA (2. 10. 2026, akční session):
# tabulka počtů se přesunula z §4 do nové **§3 „Počty omylů"**, aby ji každá
# session viděla jako první. Kdyby tu zůstalo `## 4.`, brána by četla okno
# **Evidence omylů** (kde tabulka už není) → `tvrzene` prázdné → a hlásila by
# „v kronice §3 řádek NEMÁ" u **všech osmi** bloků. Naměřeno: **přesně to se
# stalo** a je to táž past jako „kotva, která usne".
#
# ⚠ A DRUHÁ VĚC TÉHOŽ KROKU (stojí za zapsání): formát tabulky **není
# libovolný** — vzor níž vyžaduje `| **<blok>** | <popis> | **<počet>** |`.
# Když jsem tabulku přepsal s jiným pořadím sloupců, brána ji nepřečetla.
# **Opravil se dokument, ne měřidlo.**
v3 = blok(kron, "## 3. Počty omylů", "## 4.")
tvrzene = {}
for radek in v3.splitlines():
    # ⚠ POVOLEN I BLOK `8k` (doplněno 2. 10. 2026 s NA17): vzor znal jen
    # `8[b-z]`, což `8k` ještě bere — ale **`8l` a dál už ne**. Kotva je proto
    # `8[a-z]+`, aby se strop neposunul na další session.
    m = re.match(r"^\|\s*\*{0,2}(\d+[–-]\d+|8[a-z]+)\*{0,2}\s*\|\s*([^|]*)\|\s*\*{0,2}(\d+)\*{0,2}\s*\|", radek)
    if m:
        tvrzene[m.group(1)] = int(m.group(3))

print()
for nazev, _od in BLOKY:
    s = skutecne.get(nazev)
    if nazev not in tvrzene:
        # ⚠ SMĚR, KTERÝ DŘÍV CHYBĚL (naměřeno 2. 10. 2026 při psaní fixturového
        # testu `t3-kronika-mutace.py`): dřív se tu dělalo jen `continue`.
        # Když je blok omylů v `HANDOFF.md`, ale v tabulce kroniky §3 **řádek
        # nemá**, je to ROZCHOD — a tiše se přeskočil. Přitom je to přesně ta
        # vada, kterou kronika hlídá: `HANDOFF.md` se **přepisuje** a kronika je
        # jediné místo, kde příběh přežije; ne zapsaný omyl se ztratí navždy.
        # Ticho tady znamená „neměřeno", ne „v pořádku".
        chyby.append("blok %s je v HANDOFF.md (%s omylů), ale v tabulce kroniky §3 "
                     "řádek NEMÁ — nepočítal by se" % (nazev, s if s is not None else "?"))
        print("  %-8s v HANDOFF.md: %s   ale v kronice §3 CHYBÍ → ROZCHOD"
              % (nazev, s if s is not None else "?"))
        continue
    t = tvrzene[nazev]
    ok = (t == s)
    print("  %-8s kronika tvrdí %3d · skutečnost %3d   %s"
          % (nazev, t, s if s is not None else -1, "OK" if ok else "ROZCHOD"))
    if not ok:
        # ⚠ `s` může být `None` (blok se v HANDOFFu nenašel) — a `%d` na `None`
        # vyhodí TypeError, takže brána SPADNE místo aby rozchod vypsala.
        # Naměřeno 2. 10. 2026 na fixtuře (`t3-kronika-mutace.py`): chybějící
        # blok `8d` shodil bránu tracebackem a VLASTNÍ nález se ztratil v něm.
        # Brána, která na nález spadne, hlásí míň než brána, která ho vypíše.
        chyby.append("blok %s: kronika tvrdí %d omylů, v HANDOFF.md je %s"
                     % (nazev, t, "NEZMĚŘENO (blok se nenašel)" if s is None else str(s)))

# ⚠ OPAČNÝ SMĚR (doplněno 3. 10. 2026) — a do té doby chyběl ÚPLNĚ.
# Kontroly výš se ptají jen „má každý blok z dokumentu řádek v kronice?“. Jenže
# kronika §3 je **append-only záznam o projektu** a může v ní zůstat řádek,
# pro který v `HANDOFF.md` **nadpis bloku není** (přejmenovaný, sloučený nebo
# nikdy nezapsaný blok). Pak se počítá do trendu něco, co v dokumentu není —
# a to je stejná vada jako vynechaný blok, jen v opačném směru: **číslo, které
# nejde dohledat**. Naměřeno 3. 10. 2026: `8n` chyběl v bráně a opačná kontrola
# v `s24-meridla-over.py` byla kvůli tomu červená — proto se ten směr měří tady.
klice_bloku = {n for n, _od in BLOKY}
for _klic in tvrzene:
    if _klic not in klice_bloku:
        chyby.append("kronika §3 má řádek %r, ale v HANDOFF.md pro něj NENÍ "
                     "nadpis bloku omylů — číslo nejde dohledat" % _klic)
        print("  %-8s v kronice §3 JE, ale v HANDOFF.md nadpis bloku NENÍ → ROZCHOD"
              % _klic)

# ------------------------------------------------------- B) nálezy H1–H7
print()
print("B) NÁLEZY H1–H7 — jsou zmíněné tam, kde vznikly?")
print("-" * 78)
v2 = blok(kron, "### 2.1 Nálezy H1–H7", "## 3.")
hacek = sorted(set(re.findall(r"\*\*(H\d+)\*\*", v2)))
for h in hacek:
    je = h in hand
    print("  %-5s v HANDOFF.md: %s" % (h, "ANO" if je else "NE"))
    if not je:
        chyby.append("nález %s je v kronice, ale v HANDOFF.md není" % h)
print("  nálezů v kronice: %d" % len(hacek))
if not hacek:
    chyby.append("v kronice §2.1 nejsou žádné nálezy H — buď chybí, nebo se nepřečetly")

# ------------------------------------------------- C) sessions v tabulce
print()
print("C) TABULKA SESSIONS (§1) — má každá řádek s datem?")
print("-" * 78)
v1 = blok(kron, "## 1. Přehledová tabulka", "## 2.")
radky = [r for r in v1.splitlines() if re.match(r"^\|\s*\*\*\d+\*\*\s*\|", r)]
print("  řádků sessions: %d" % len(radky))
bez_data = [r for r in radky if not re.search(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}", r)]
if bez_data:
    for r in bez_data:
        chyby.append("řádek session bez data: %s" % r[:70])
    print("  bez data: %d" % len(bez_data))
else:
    print("  bez data: 0")
if len(radky) < 10:
    chyby.append("tabulka sessions má jen %d řádků — projekt měl víc session" % len(radky))
# každá session musí mít typ
# ⚠ P19 (6. 10. 2026): přidán typ **`rozhodovací`**. Do té doby tu byly jen
# `akční`/`plánovací`/`ověřovací`/`analýza` — a session, jejímž obsahem je
# **rozhodnutí o nálezech** (P19: push, H93, H94, `g3`), se musela vydávat za
# něco jiného. Zadání i `HANDOFF` ji jmenují **„ROZHODOVACÍ session"**, takže
# je to **rozšíření slovníku o deklarovaný typ**, ne oslabení kontroly:
# kontrola pořád vyžaduje, aby typ byl **uvedený**, a `bez_typu` se počítá dál.
# (Ověřeno mutací: řádek s vymyšleným typem kontrola pořád hlásí.)
typy = {"akční", "plánovací", "ověřovací", "analýza", "rozhodovací"}
bez_typu = [r for r in radky if not any(t in r for t in typy)]
print("  bez typu (akční/plánovací/ověřovací/analýza/rozhodovací): %d" % len(bez_typu))
if bez_typu:
    chyby.append("%d řádků session nemá uvedený typ" % len(bez_typu))

# ⚠ P28-E (8. 10. 2026): KONTINUITA ID — chybějící záznam je TICHO, ne rozchod.
# Naměřeno: kronika měla **41 řádků** s id 1..42 — **id 24 CHYBĚLO**. Commit
# `c3ee946` ten řádek SMAZAL (a na jeho místo vložil 25); text se v živé kronice
# nevyskytoval, dohledatelný byl jen v gitu (`411f0bb`). Do dneška to brána
# neviděla, protože kontrolovala jen POČET řádků (≥ 10), datum a typ — a přesně
# na tuhle třídu upozorňuje poučení P22: „chybějící záznam není rozchod, je to
# ticho; kdo to chce chytit, musí se ptát NAOPAK“. Obnoveno nástrojem
# `_analyza/p28-obnov-kroniku.py`; tenhle blok je pojistka proti dalšímu.
_ids = [int(re.match(r"^\|\s*\*\*(\d+)\*\*\s*\|", r).group(1)) for r in radky]
chybejici_id = [i for i in range(1, max(_ids) + 1) if i not in _ids] if _ids else []
print("  chybějící id v řadě 1..%s: %s"
      % (max(_ids) if _ids else "—", chybejici_id or "(žádné)"))
if chybejici_id:
    chyby.append("v tabulce sessions CHYBÍ id %s — záznam session se ztratil "
                 "(obnova: `_analyza/p28-obnov-kroniku.py`)" % chybejici_id)

# ----------------------------------------------------- D) odkazy na zdroje
print()
print("D) ODKAZY NA ZDROJE — existují soubory, na které kronika odkazuje?")
print("-" * 78)
# POZOR: vzor musí vyloučit zadní část delšího jména. Naměřeno při psaní:
# `([A-Za-z0-9_\-]+\.md)` roztrhlo `ANALYZA-HLOUBKOVA-ORCHESTRA.md, -2.md` na
# dva „odkazy" a druhý z nich (`-2.md`) neexistuje → **falešný poplach**.
# Souborová jména proto začínají písmenem nebo číslicí, ne pomlčkou.
#
# ⚠ A druhá vada téhož vzoru, naměřeno 2. 10. 2026: bez lomítka **odřízl
# `docs/` z cesty** — z `docs/ARCHITEKTURA.md` udělal „ARCHITEKTURA.md",
# hledal ho ve workspace a hlásil „CHYBI". Vypadalo to jako chybějící
# dokument; přitom je to **relativní cesta uvnitř herního repa**. Lomítko
# je proto součástí vzoru a hledá se i v `games/uo-shadows/`.
odkazy = sorted(set(re.findall(r"`([A-Za-z0-9][A-Za-z0-9_\-/]*\.md)`", kron)))
SKILLY = ("dsh-prostredi", "overovani", "orchestra", "game-developer",
          "game-assets", "vision", "dsh-usage", "hlouchkova-analyza",
          "imagegen", "imagegen-local", "otevrena-temata", "session-handoff")
chybejici = []
# ⚠ PŘESUN NA E: (4. 10. 2026) — kronika odkazuje na TRI ruzna mista a kazde
# ma po presunu jiny koren. Kdo je slije do jednoho, hlasi chybu u dokumentu,
# ktery je v poradku (naměřeno: 5 falešných chyb).
#   REPO   = root repa (orchestra)  — projektove dokumenty se presunuly sem
#   HRA    = E:\Workspaces\uo-shadows — sourozenec; `docs/...` je UVNITR ni
#   STANICE= C:\Users\Ssevc\Local-Deepseek — dokumenty, ktere zustaly stanici (D6)
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
SKILLY_DIR = pathlib.Path.home() / ".dsh" / "skills"
for o in odkazy:
    if (WS / o).is_file():                 # v repu orchestra
        continue
    if (_HRA / o).is_file():               # relativni cesta v hernim repu
        continue
    if (WS / "repo" / o).is_file():         # sablona herniho repa
        continue
    if (STANICE / o).is_file():            # dokument zustal stanici (D6)
        continue
    # ⚠ HISTORICKÁ CITACE (4. 10. 2026): kronika je ZÁZNAM a nepřepisuje se —
    # takže v ní PO PRÁVU zůstávají cesty, které po přesunu na E: už neplatí
    # (`games/uo-shadows/docs/ARCHITEKTURA.md`). Pravidlo projektu je jasné:
    # „historická čísla a citace se nepřepisují". Kontrola se proto ptá, jestli
    # soubor existuje na dněšním místě — NE jestli sedí starý literál.
    if o.startswith("games/uo-shadows/"):
        zbytek = o[len("games/uo-shadows/"):]
        if (_HRA / zbytek).is_file() or (WS / zbytek).is_file():
            continue
    if o == "SKILL.md" and all(
            (SKILLY_DIR / d / "SKILL.md").is_file() for d in SKILLY):
        continue
    chybejici.append(o)
print("  různých .md odkazů: %d, z toho chybí: %d" % (len(odkazy), len(chybejici)))
for o in chybejici:
    print("    CHYBI: %s" % o)
    chyby.append("kronika odkazuje na neexistující %s" % o)

# -------------------------------------------- E) živé číslo počtu session
print()
print("E) ŽIVÉ MĚŘENÍ — počet session (aby číslo nebylo vymyšlené)")
print("-" * 78)
zive = None
# `KRONIKA_BEZ_ZIVEHO=1` vypne živé měření — používá to fixturový mutační test
# (`t3-kronika-mutace.py`): `dsh-usage` je pomalý a jeho číslo s fixturou
# nesouvisí. Vypnuté měření se VYPÍŠE jako poznámka, nikdy jako ticho.
if os.environ.get("KRONIKA_BEZ_ZIVEHO"):
    print("  POZNÁMKA: živé měření VYPNUTO (KRONIKA_BEZ_ZIVEHO=1 — běží fixtura)")
    pokud.append("počet session nezměřen (vypnuto pro fixturu)")
else:
    try:
        r = subprocess.run([str(pathlib.Path.home() / ".dsh" / "skills" / "dsh-usage" / "run.cmd"),
                            "--json"], capture_output=True, timeout=600)
        vystup = r.stdout.decode("utf-8", "replace")
        m = re.search(r'"sessions"\s*:\s*(\d+)', vystup)
        if m:
            zive = int(m.group(1))
    except Exception as e:                                       # noqa: BLE001
        print("  (dsh-usage se nepodařilo spustit: %s)" % type(e).__name__)
if zive is None:
    # Nula a „nezměřeno" nejsou úspěch — ale ani vada kroniky.
    print("  POZNÁMKA: počet session NEZMĚŘEN (dsh-usage nedostupný)")
    pokud.append("počet session nezměřen")
else:
    print("  dsh-usage hlásí sessionů celkem: %d" % zive)
    if zive < len(radky):
        chyby.append("dsh-usage hlásí %d session, ale kronika má %d řádků"
                     % (zive, len(radky)))

# ------------------------------------------------------------------ závěr
print()
print("=" * 78)
print("VYHODNOCENÍ")
print("=" * 78)
# ⚠ NA17 (Úkol 2c): „celkem N" bez seznamu zdrojů je neověřitelné. Brána proto
# VYPISUJE, KTERÉ BLOKY do součtu zahrnula — a co naopak nechala stranou.
# Kdyby to nevypisovala, čtenář nemá jak poznat, že se do počtu nějaký blok
# nevešel (přesně to se stalo: `8i` a `8j` chyběly a nikde to nebylo vidět).
print("  bloků omylů v tomto součtu: %d" % len(skutecne))
print("      %s" % ", ".join("%s (%d)" % (n, p) for n, p in skutecne.items()))
if len(skutecne) != len(BLOKY):
    chyby.append("do součtu se dostalo %d z %d bloků — chybějící se NEPOČÍTALY"
                 % (len(skutecne), len(BLOKY)))
print("  omylů celkem (skutečnost): %d" % sum(skutecne.values()))
print("  nálezů H v kronice:        %d" % len(hacek))
print("  sessions v kronice:        %d" % len(radky))
print("  odkazů na .md:             %d" % len(odkazy))
if pokud:
    for p in pokud:
        print("  POZNÁMKA: %s" % p)
print()
if chyby:
    print("NALEZENO %d ROZCHODŮ:" % len(chyby))
    for c in chyby:
        print("  CHYBA %s" % c)
    sys.exit(1)
print("KRONIKA SEDÍ — počty omylů odpovídají HANDOFF.md, nálezy i odkazy existují.")
sys.exit(0)

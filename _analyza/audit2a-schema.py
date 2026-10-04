# -*- coding: utf-8 -*-
"""Nezávislé přeměření počtu sloupců v `conductor/schema.sql`
A ROZLIŠENÍ „tvrzení o dnešku" od „záznamu" a „citace".

CO SE 2. 10. 2026 ZMĚNILO A PROČ (naměřeno, ne dojem)
=====================================================
Původní verze porovnávala KAŽDÝ výskyt vzoru `(\\d+)\\s+sloupc` s živým zdrojem
a každý rozdíl zapsala jako „ROZCHOD". Naměřeno po opravě `AGENTS.md:62`
(zadání `ZADANI-DOKONCENI-AUDITU.md`, Úkol 1): **stále `exit 1`, 6 „rozchodů"**
— a **ani jeden z nich nebyl tvrzení o dnešku**:

  | # | Kde | Co to je | Proč NENÍ rozchod |
  |---|---|---|---|
  | 1 | `AGENTS.md:62` „**„32 sloupců"**" | **CITACE** dřívějšího chybného tvrzení | 32 nebylo nikdy správně; je to popis vady, ne tvrzení |
  | 2 | `KRONIKA-PROJEKTU.md:36` „39 sloupců, ne 32" | **ZÁZNAM** (append-only kronika) | 2. 10. 2026 bylo 39 správně (A2) |
  | 3 | `HANDOFF.md:127` „tvrdil „32 sloupců"" | **CITACE** + záznam nálezu N9 | totéž |
  | 4 | `HANDOFF.md:558` „tvrdí 32 sloupců" | **CITACE** v tabulce omylů | totéž |
  | 5 | `HANDOFF.md:581` „`'39 sloupců'`" | **CITACE** v kódovém rozpětí | totéž |
  | 6 | `HANDOFF.md:628` „u „32 sloupců"" | **CITACE** | totéž |

**A ta horší polovina (to je jádro opravy):** původní vzor `(\\d+)\\s+sloupc`
potřebuje slovo „sloupců" **hned za číslem**. Věta, která R1 skutečně
popisovala — „správně je **39** — a schéma se přitom…" — tedy **vůbec
neodpovídala vzoru**. Naměřeno: brána u `AGENTS.md:62` hlásila „tvrdí 32",
tedy četla **citaci**, a **skutečné tvrzení o dnešku neviděla**.
Byla to táž vada, jakou audit popsal u `audit2b` (nález R3): *měřidlo
neumí rozeznat tvrzení od záznamu* — a navíc měřilo jen to, co vzor trefil.

NOVÉ PRAVIDLO (a je to poučení z R3: „u každého čísla se ptej, K ČEMU patří")
----------------------------------------------------------------------------
  * **`AGENTS.md` = AUTORITA, mluví v přítomném čase.** Jen ona může odporovat
    živému zdroji. Každé její tvrzení se proto kontroluje — včetně tvrzení
    v próze (`správně je **39**`), které starý vzor neviděl.
  * **`HANDOFF.md` a `KRONIKA-PROJEKTU.md` = APPEND-ONLY ZÁZNAMY.** `AGENTS.md`
    o nich sám říká „píše každá session, **nic se nemaže**" a „**nikdy se
    nepřepisuje, jen doplňuje**". Staré číslo v nich je **ve svém čase
    správné** (A2) — a audit to doložil na R3: 11× „21 granul" bylo správně.
    Vypisují se proto jako `[záznam]`, ale **nepočítají se jako rozchod**.
  * **CITACE** = číslo je v uvozovkách nebo v kódovém rozpětí (cituje cizí
    slova, ne tvrdí nic o dnešku).
  * **ZÁZNAM SE ZNAČKOU ČASU** = u čísla stojí „stav před…", „před B1",
    „dříve", nebo datum → je to hodnota označená jako minulá, ne dnešní.
    Přesně to je oprava `AGENTS.md:62` z Úkolu 1: `**39** (stav před B1;
    dnes **40**)`.
  * **ROZCHOD** = zbytek. Jen ten skončí `exit 1`.

⚠ CO TENHLE NÁSTROJ NEUMÍ (přiznaná mez, ne zamlčení)
-----------------------------------------------------
  V append-only dokumentech **nehlídá nové chybné číslo** — kdyby někdo
  napsal do `HANDOFF.md` „45 sloupců", brána to vypíše jako `[záznam]`
  a nepadne. Je to vědomá daň za to, že se přestalo křičet na datované
  záznamy (falešný poplach se hledá hůř než slepé místo — `overovani` §9.5).
  Kdo chce hlídat i záznamy, ať použije `ag-over-cisla.py` (ten čte tvrzení
  z `AGENTS.md` a je mutačně ověřený).

⚠ PAST, DO KTERÉ PŮVODNÍ VERZE SPADLA (a je to poučení, ne detail)
-----------------------------------------------------------------
  Neodstraňovala SQL komentáře — a blok `CREATE TABLE roadmap` má uvnitř
  ČTYŘI komentářové řádky (vysvětlují sloupec `naposledy_selhalo`). Vyšlo
  **44** místo **40**, protože se komentář počítal jako sloupec. A protože
  OBĚ „metody" v tom skriptu používaly tentýž blokový regex, shodly se na
  stejné chybě a skript napsal „obě metody se SHODUJÍ, číslo je spolehlivé".
  **Dvě metody nad jedním vadným vstupem nejsou dvě metody** (`overovani`
  §1.1). Proto se teď komentáře odstraňují PŘED hledáním bloků a výsledek
  se navíc vypisuje PO TABULKÁCH, aby se dal přečíst ručně.

PROČ JE 39 i 40 „SPRÁVNĚ": Dnes je správně **40**. Číslo **39** bylo správné
DO 2. 10. 2026 — pak B1 přidal sloupec `naposledy_selhalo` (aby se cooldown
neptal na `updated_at`, což byla vada S12). Rozdíl je tedy **čas**, ne
nepravda (`AGENTS.md` A2).

Mutační test: `_analyza\\audit2a-mutace.py`.
"""
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SQL = WS / "orchestra" / "conductor" / "schema.sql"
OMEZENI = ("primary", "foreign", "unique", "check", "constraint", "key")

# Dokumenty, které jsou podle vlastního popisu v `AGENTS.md` APPEND-ONLY
# ZÁZNAMY: „píše každá session, nic se nemaže" / „nikdy se nepřepisuje, jen
# doplňuje". Staré číslo v nich je ve svém čase správné (A2) — nález R3.
ZAZNAMOVE = ("HANDOFF.md", "KRONIKA-PROJEKTU.md")

# Tvrzení v próze, která starý vzor NEVIDĚL (slovo „sloupců" u nich nestojí).
# Naměřeno na `AGENTS.md:62`: „správně je **39**" a „dnes **40**".
VZOR_TVRZENI = re.compile(r"(?:správně je|správně|dnes|nyní|aktuálně|má)\s+\**(\d+)\**")

# Značky času u čísla → hodnota je označená jako MINULÁ, ne dnešní.
ZNAKY_CASU = ("stav před", "před B1", "dříve", "dřív", "v té době", "bývalo")
VZOR_DATUM = re.compile(r"\d{1,2}\.\s*\d{1,2}\.\s*\d{4}")

VZOR_SLOUPCU = re.compile(r"(\d+)\s+sloupc")
VZOR_UVOZOVKY = (("„", "“"), ("„", '"'), ("`", "`"), ("'", "'"))


def v_uvozovkach(text: str, i: int, j: int) -> bool:
    """Je rozsah text[i:j] uvnitř uvozovek nebo kódového rozpětí?

    Hledá se LOKÁLNĚ (±60 znaků), ne stavovým automatem přes celý dokument —
    ten by se rozbil o jedinou neuzavřenou uvozovku kdekoliv jinde.
    """
    pred = text[max(0, i - 60):i]
    po = text[j:j + 60]
    for otev, zavr in VZOR_UVOZOVKY:
        k = pred.rfind(otev)
        if k < 0:
            continue
        if zavr in pred[k + 1:]:      # uvozovka se uzavřela PŘED číslem
            continue
        if zavr in po:
            return True
    return False


def ma_znacku_casu(text: str, i: int, j: int) -> str:
    """Vrátí značku času PŘIPOJENOU k číslu, nebo prázdný řetězec.

    ⚠ PAST, KTEROU NAŠEL AŽ MUTAČNÍ TEST (M2, 2. 10. 2026) — a je to poučení:
    první verze hledala značku kdekoliv v okně ±60 znaků. Tím se ale značka
    od **sousedního** tvrzení přilepila k číslu, které žádnou nemá:
    `**32 sloupců**, správně je **39** (stav před B1…)` → číslo 32 dostalo
    značku „stav před" z třicetidevítky a brána ho vyhodnotila jako `[záznam]`.
    **Brána pak byla slepá přesně k tomu, co má hlídat** (vada R1) — a
    odhalil to jen mutační test, ne čtení kódu (`overovani` §9.7).
    Proto se teď značka bere JEN DOPŘEDU a jen když mezi číslem a značkou
    **není jiné číslo** — tedy značka patří TOMUHLE číslu, ne sousedovi.
    """
    po = text[j:j + 60]
    for z in ZNAKY_CASU:
        k = po.find(z)
        if k >= 0 and not any(ch.isdigit() for ch in po[:k]):
            return z
    m = VZOR_DATUM.search(po)
    if m and not any(ch.isdigit() for ch in po[:m.start()]):
        return m.group(0)
    return ""


if not SQL.is_file():
    print("CHYBA: %s neexistuje — není co měřit" % SQL)
    sys.exit(2)

sql_hruby = SQL.read_text(encoding="utf-8")
# Komentáře se odstraní PRVNÍ — jinak se počítají jako sloupce (naměřeno: 44 vs 40).
sql = re.sub(r"--[^\n]*", "", sql_hruby)

bloky = re.findall(r"CREATE TABLE IF NOT EXISTS\s+(\w+)\s*\((.*?)\n\);", sql, re.S)

print("=" * 92)
print("NEZÁVISLÉ PŘEMĚŘENÍ SLOUPCŮ: orchestra/conductor/schema.sql")
print("=" * 92)
print("  soubor: %s  (%d B, %d řádků)"
      % (SQL.name, SQL.stat().st_size, len(sql_hruby.splitlines())))
print()

celkem = 0
for jmeno, telo in bloky:
    sloupce = [l.strip().rstrip(",") for l in telo.splitlines() if l.strip()]
    celkem += len(sloupce)
    print("  %-10s sloupců: %2d   %s" % (jmeno, len(sloupce),
                                         ", ".join(s.split()[0] for s in sloupce)))
print("  " + "-" * 78)
print("  TABULEK: %d     SLOUPCŮ CELKEM: %d" % (len(bloky), celkem))
print()

print("  Kontrola vysvětlení „39 vs 40\": sloupec `naposledy_selhalo` je v roadmapě")
print("  a podle komentáře ho přidal B1 (2. 10. 2026). Odečte-li se, vyjde:")
print("      %d - 1 = %d   ← to je to „39\" z `AGENTS.md`" % (celkem, celkem - 1))
print()

# ── Co o tom tvrdí dokumenty ──────────────────────────────────────────────
print("=" * 92)
print("CO O TOM TVRDÍ DOKUMENTY — a K ČEMU to patří")
print("=" * 92)
print("  (R3: „u každého čísla se ptej, K ČEMU patří\" — záznam ≠ tvrzení)")
print()

pocet_tvrzeni = 0
pocet_zaznamu = 0
pocet_citaci = 0
rozchody = []

for jmeno in ("AGENTS.md", "KRONIKA-PROJEKTU.md", "HANDOFF.md"):
    cesta = WS / jmeno
    if not cesta.is_file():
        continue
    s = cesta.read_text(encoding="utf-8")
    je_zaznamovy = jmeno in ZAZNAMOVE
    print("  %s%s" % (jmeno, "   (append-only záznam — A2)" if je_zaznamovy else
                            "   (AUTORITA — mluví v přítomném čase)"))
    if je_zaznamovy:
        print("    %s" % ("Staré číslo je tu ve svém čase SPRÁVNÉ. Vypisuje se"
                          " kvůli úplnosti, ne jako rozchod."))

    # 1) čísla připoutaná ke slovu „sloupců"  2) + tvrzení v próze na týchž
    #    řádcích, která starý vzor minul (naměřeno: „správně je **39**").
    nalezy = []          # (index, konec, hodnota, druh_vzoru)
    for m in VZOR_SLOUPCU.finditer(s):
        nalezy.append((m.start(), m.end(), int(m.group(1)), "číslo u slova"))
    radky_s_sloupc = {s[:m.start()].count("\n") for m in VZOR_SLOUPCU.finditer(s)}
    for m in VZOR_TVRZENI.finditer(s):
        radek = s[:m.start()].count("\n")
        if radek not in radky_s_sloupc:
            continue
        if any(a <= m.start(1) < b for a, b, _, _ in nalezy):
            continue
        nalezy.append((m.start(1), m.end(1), int(m.group(1)), "tvrzení v próze"))
    nalezy.sort()

    if not nalezy:
        print("    ⚠ NENAŠLO SE ŽÁDNÉ TVRZENÍ — to není „v pořádku\", to je slepé místo.")
        rozchody.append("%s: nenašlo se žádné tvrzení" % jmeno)
        print()
        continue

    for i, j, tvrzeno, druh in nalezy:
        radek = s[:i].count("\n") + 1
        kontext = s[max(0, i - 85):j + 45].replace("\n", " ").strip()
        citace = v_uvozovkach(s, i, j)
        znacka = ma_znacku_casu(s, i, j)

        if tvrzeno == celkem:
            verdikt, sbornik = "SOUHLASÍ s živým zdrojem", "souhlas"
        elif citace and not je_zaznamovy:
            verdikt, sbornik = "[citace] — cituje cizí slova, netvrdí o dnešku", "citace"
        elif znacka and not je_zaznamovy:
            verdikt, sbornik = ("[záznam] značka času „%s\" — ve svém čase správné"
                                % znacka), "zaznam"
        elif je_zaznamovy:
            verdikt, sbornik = "[záznam] append-only dokument (A2)", "zaznam"
        else:
            verdikt = "ROZCHOD (živý zdroj = %d)" % celkem
            sbornik = "rozchod"

        print("    %-6s tvrdí %2d  %-52s %s" % ("ř.%d" % radek, tvrzeno, verdikt, druh))
        print("           …%s…" % kontext[:120])
        if sbornik == "souhlas":
            pocet_tvrzeni += 1
        elif sbornik == "zaznam":
            pocet_zaznamu += 1
        elif sbornik == "citace":
            pocet_citaci += 1
        else:
            rozchody.append("%s:%d tvrdí %d" % (jmeno, radek, tvrzeno))
    print()

print("=" * 92)
print("  ZMĚŘENO: výskytů celkem=%d  (souhlasí=%d, záznamů=%d, citací=%d, ROZCHODŮ=%d)"
      % (pocet_tvrzeni + pocet_zaznamu + pocet_citaci + len(rozchody),
         pocet_tvrzeni, pocet_zaznamu, pocet_citaci, len(rozchody)))
print("  Proti živému zdroji (%d sloupců) se měří %s."
      % (celkem, "AUTORITA `AGENTS.md` včetně tvrzení v próze"
         if pocet_tvrzeni else "— NIC, to je vada měřidla"))
if rozchody:
    print()
    for r in rozchody:
        print("  ROZCHOD: %s" % r)
    print("\n  → exit 1: některé TVRZENÍ O DNEŠKU nesedí na živý zdroj.")
    sys.exit(1)
print("\n  → exit 0: žádné tvrzení o dnešku se nerozešlo se zdrojem.")
sys.exit(0)

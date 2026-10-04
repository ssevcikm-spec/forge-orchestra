# -*- coding: utf-8 -*-
r"""Zapíše do `HANDOFF.md` výsledky §25 a vlastní omyly 105–112.

PROČ SKRIPTEM A NE EDITOREM: `HANDOFF.md` má **4221 řádků** a v témže workspace
pracuje **souběžná session**; soubor **není v gitu**. Skript proto:
  1. udělá **zálohu kopií** (do `_analyza\`),
  2. zapíše **bajty** (ne text — `write_text` překládá konce řádků),
  3. **ověří po zápisu**, že klíčové kotvy v souboru jsou,
  4. při chybě **vrátí zálohu**.

Vkládá se na KONEC souboru (append-only dokument — nic se nepřepisuje).
"""
import datetime
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
HANDOFF = WS / "HANDOFF.md"
ZALOHA = WS / "_analyza" / "handoff-pred-s25-zapisem.md"

SEKCE25 = """

---

## 25. Provedeno 2. 10. 2026 (20:1x–21:0x UTC) — AKČNÍ session: OPRAVA PĚTI MĚŘIDEL

**Co je tenhle oddíl:** **záznam o provedení** podle zadání
`ZADANI-OPRAVA-MERIDEL.md`. **Co z něj ještě platí:** všechna čísla níž jsou
**naměřená touto session**; co zestará, je označeno datem.

> **⚠ ZADÁNÍ TVRDILO ČÍSLA, KTERÁ NESEDĚLA — a je to první nález téhle session.**
> `ZADANI-OPRAVA-MERIDEL.md` (F1) tvrdilo: `audit2b` hlásí **31** rozchodů,
> z toho **25 falešných**, `kontrol` **19**. **Naměřeno před jakoukoli změnou:**
> **30** rozchodů, `kontrol` **15**. **Vstupní brána `s24-meridla-over.py` byla
> zelená (`exit 0`)** — protože měla mez `<= 35` a mezi **30 a 31 nerozlišuje**.
> **Pravidlo:** mez, která je širší než rozdíl, o který jde, **neměří nic**.

### 25.1 Co bylo hotovo (měřené, ne tvrzené)

| # | Úkol ze zadání | Stav | Doklad |
|---|---|---|---|
| **1** | `audit2b`: přestat hlásit falešné rozchody | ✅ **30 → 9** | `python _analyza\\audit2b-cisla-proti-zdroji.py` → `ROZCHODŮ: 9` |
| **1** | CITACE v uvozovkách / kódovém rozpětí | ✅ | skener `je_citace()`; `HANDOFF.md:743` i `PLAN-DALSI-KROK.md:71` → `CITACE` |
| **1** | výpis „který zdroj to měří" (NA17) | ✅ | tabulka `ZDROJE PODLE VELIČIN` + registr šesti bran |
| **2a** | NA23 — `g3` u `validate-all` | ✅ **`—`** | `python _analyza\\g3-brany.py` → `otevřela: — (brána nemá čítač)` |
| **2b** | NA19 — 5 odkazů na §5 | ✅ **0 zbývá** | `PREDAVANI-SESSION.md` ř. 84, 129, 286, 317, 334 → §6 |
| **2c** | NA17 — brána kroniky | ✅ **12 bloků / 99 omylů** | `python _analyza\\kronika-kontrola.py` → `exit 0`, vypisuje bloky |
| **3** | `audit2b-over.py`: fixtura s citací | ✅ **7 běhů, 4 mutace, 0 chyb** | `python _analyza\\audit2b-over.py` → `exit 0` |
| **4** | tři mutační testy | ✅ **10 → 7** | `python _analyza\\audit6-brany-mutace.py` → `BEZ důkazu: 7` |
| **5a** | hlavičky dokumentů | ✅ **80 → 14** | `python _analyza\\audit1-inventar.py` → `bez hlavičky: 14` |
| **5b** | opatření 3 (krytí `schema.sql`) | ❌ **NEDODĚLÁNO** | zadání pro další session, Úkol 4 |
| **6** | tabulka pokrytí diakritiky | ❌ **NEDODĚLÁNO** | zadání pro další session, Úkol 5 |

### 25.2 Jádro opravy `audit2b` — a proč to nebyla kosmetika

Veličina `kontrol` srovnávala **jedno číslo z jedné brány** (běh Godotu, dnes
**65**) se **všemi** výskyty `(\\d+)\\s+kontrol` v jádru. Naměřeno: z **15**
rozchodů u `kontrol` jich **11** vzniklo tak, že dokument **správně citoval
jinou bránu** (`a1-a2-over` 23 · skener 23 · `over-dokumentaci` 63 ·
`vision.test.mjs` 36 · `test-cooldown` 10 …).

**Zaveden registr bran** (`_analyza\\_registr-bran.py` → `_registr-bran.json`):
uzavřená množina **živě naměřených** hodnot `[65, 63, 61, 59, 23, 10]`, každá
s bránou, příkazem a dokladem. **Není to „ber, co se hodí":** hodnota, kterou
nevydala žádná brána, se **pořád hlásí jako rozchod** — doloženo mutací
**PROBE-C (777 kontrol → ROZCHOD)** v `audit2b-over.py`.

### 25.3 Tři čísla o omylech — a proč se rozcházela

Naměřeno třemi různými měřidly, každé na jinou otázku:

| Otázka | Odpověď | Příkaz |
|---|---|---|
| kolik jich vidí **brána kroniky** | **99** ve **12 blocích** | `python _analyza\\kronika-kontrola.py` |
| kolik je **unikátních id** v blocích | **99** (1–101 + 102–104, díry 24–28) | `python _analyza\\_s25-sonda-id.py` |
| kolik je **řádků tabulek** (KDEKOLI) | **153** — a **není to počet omylů** | tamtéž |

**Proč se to srovnalo:** podbloky `8b`–`8l` obsahují **tytéž omyly** jako
společná tabulka v §8 (naměřeno: **57 id je v obou**), takže blok `1–13` je
**jen řádky mezi `## 8.` a `### 8b.`** a zbytek společné tabulky se do součtu
**NESMÍ přičíst**. Kdo sečte řádky všech tabulek, dostane **153**.

> **⚠ NÁLEZ: BLOK OMYLŮ ZAPSANÝ JINÝM TVAREM JE PRO VŠECHNA MĚŘIDLA NEVIDITELNÝ.**
> Souběžná session dopsala omyly **102–104** jako `### 24.16 Vlastní omyly …` —
> tedy **číslem oddílu, ne blokem**. Žádná brána je neviděla, `kronika` hlásila
> 91 místo 96. **Náprava:** nadpis přejmenován na `### 8l. …` a do
> `s24-meridla-over.py` doplněna kontrola, která se ptá **NAOPAK**: *„má každý
> nadpis bloku omylů v dokumentu svou kotvu v bráně?"* — ne jen „existuje každá
> kotva brány?". **Do hodiny po připsání odhalila i blok `8k`.**

### 25.4 Co tahle session NEDODĚLALA (a je to zadání pro další)

- **Úkol 5b** (opatření 3 — která tvrzení o `schema.sql` jsou nekrytá).
- **Úkol 6** (tabulka pokrytí brány diakritiky).
- **Zbylých 9 rozchodů** `audit2b` — u každého je v `ZADANI-DODELAT-MERIDLA.md`
  §3 Úkol 1 **napsáno, co s ním**.
- **`_analyza\\_inventar.json` NEBYL přegenerován** po editaci nástrojů —
  **udělej to první**, jinak spadnou `c2-mutace.py` a `n1-over-inventar.py`
  (`exit 2`, což je **správné chování**, ne regrese).

### 25.5 Vlastní omyly téhle session

**Osm omylů (105–112) — a sedm z nich je v měřidle.** Zapsány v §8l níž.
 Nejdrážší je **105**: *„měřidlo, které tiše vynechá vstup"* — moje vlastní
 oprava `audit2b` **zahodila 147 správných tvrzení** a vypadalo to jako
 „brána je přísná". Odhalil to až **výpis přeskočených** — kdybych ho nedal,
 odešlo by to jako hotová práce.
"""

SEKCE8L = """

---

### 8m. Omyly AKČNÍ session 2. 10. 2026 (20:1x–21:0x UTC) — **105–112**

**Kontext:** osm omylů vzniklo jedné session při **opravě měřidel** — a
**sedm z nich je v měřidle nebo v postupu měření**, ani jeden není nález
o cizím kódu. **Dva (`106`, `110`) by neodhalilo čtení kódu**; odhalil je až
**běh**. To je týž podíl jako v blocích `8e`–`8l` — **trend se nezlepšil**,
ani když session dělala **jen opravu měřidel**.

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **105** | **Guard `je_pocet()` zahodil 147 SPRÁVNÝCH tvrzení** — a vypadalo to jako „brána je přísná" | první verze brala `s[konec:konec+24]` z CELÉHO dokumentu, takže okno **přeteklo na další řádek** a `NENI_POCET` (hledající „řádk") zabral na **úplně jiné větě**. A `konec` je index za **spojením číslo+jednotka**, ne za číslem → funkce viděla jako první `0` z „0 selhání" a vyhodnotila „jiná jednotka" | **výpisem PŘESKOČENÝCH** — byly v něm i hodnoty, které se se zdrojem **shodují** (39, 59, 23, 65…). Kdybych výpis nedal, **odešlo by to jako hotové** | **Guard nesmí sahat za hranici celku, o kterém rozhoduje** — a **vynechaný vstup musí být VIDĚT** (`AGENTS.md`). Okno zastaveno na konci řádku, spojení hledáno zpětným pohledem |
| **106** | **`filesInOriginMainXX` OBSAHUJE `filesInOriginMain`** — mutace byla neviditelná | `b5-mutace.py` přejmenoval identifikátor na `…XX`, ale brána hledá **PODŘETĚZEC** (`"filesInOriginMain" in KOD`) → verdikt se **nepřeklopil** a test hlásil „brána NEMĚŘÍ" | porovnáním: soubor měl po mutaci **0** výskytů starého jména, a přesto `ma = True` | **Je to omyl 18 znovu** („nový název musí být ÚPLNĚ jiný"). Nové jméno `loadMainTree` **a assert, že nové jméno neobsahuje staré** |
| **107** | **Číslo řádku jsem SPOČÍTAL místo abych ho NAŠEL** | `radek_sondy = len(ta2.splitlines()) + 1` dalo **495**, ale soubor končí newline → sonda byla na **496**. Test pak hlásil „sonda vypadla z měření úplně" | falešný nález o **správném** kódu — sonda byla v ZÁZNAMECH | **`overovani` §7.11: nehledej pořadím, vymez to řádkem.** Číslo se **hledá v obsahu** |
| **108** | **Assert jsem napsal na CELÝ dokument místo na měřený řádek** | `assert '„32 sloupců"' not in zmut_cit` spadl, protože **jiný řádek** (`AGENTS.md:152`) nese tutéž citaci bez kontextu | spadlo to na **správné mutaci** | **`overovani` §10.6:** assert o „podmínka přestala platit" se **ZÚŽÍ NA TU JEDNOTKU** (řádek/nadpis), ne na soubor |
| **109** | **Měřil jsem pravidlo, které se k tomu výskytu vůbec nedostalo** | mutoval jsem `AGENTS.md:62`, ale ten řádek **začíná slovem „tvrdil"** → zařadí ho **dřív** pravidlo `CITACE` (slova minulosti), ne pravidlo uvozovek. Test by prošel **i s vypnutým skenerem citací** | když se ani po správné mutaci nic nezměnilo | **Test musí měřit TO pravidlo, které tvrdí** — vlastní sonda bez slov minulosti (`PROBE-A/B/C` vzor) |
| **110** | **Dva výskyty kotvy, `count != 1`** | `KOTVA_CIT = '**„32 sloupců"**'` je v `AGENTS.md` **2×** (`:62` a `:152`) | test správně spadl na „kotva není jednoznačná" | **`overovani` §9.8: před mutací SPOČÍTEJ VÝSKYTY.** Kotva = celý řádek s kontextem |
| **111** | **Nechal jsem v nástroji DRUHOU definici téže konstanty** | při přesunu `NENI_POCET` zůstala kopie o 200 řádků níž a **přebila** tu první → `je_pocet` měl jiné pravidlo, než jsem četl | `NameError` a dvě kola hledání, „proč predikát nefunguje" | **Konstanty patří k funkci, která je používá** — a **`grep` na jméno musí dát 1 výskyt** |
| **112** | **Zápis vlastního výstupu do složky, kterou táž brána prochází** | zálohy hlaviček jsem dal do `_analyza\\_hlavicky-zaloha\\` — a `audit1-inventar.py` prochází `_analyza` rekurzivně → **dokumentů 111 → 177** a „bez hlavičky" **14 → 80**. Vypadalo to, jako že oprava **zhoršila** stav o 66 | porovnáním počtu dokumentů před a po | **Je to omyl 101 znovu** („výstup brány nepatří do složky, kterou brána prochází"). Zálohy se jmenují `hlavicky-zaloha-pred-opatrenim7` — **`zaloha` v CESTĚ** je to, co je zařadí mezi zálohy (nález NA21) |

**Vzor z těch osmi (a je nepříjemný):** **sedm z osmi** vzniklo
**v měřidle nebo v postupu měření** — a **pět** by bez **běhu** odešlo jako
hotová práce. **A ještě jeden údaj do trendu:** omyl **106** je **druhý výskyt
téhož omylu (18)** v projektu — znalost pasti **nestačí**, musí být
v testu jako `assert`.
"""


def main() -> int:
    if not HANDOFF.is_file():
        print("CHYBA: %s není" % HANDOFF)
        return 1
    orig = HANDOFF.read_bytes()
    if "## 25. Provedeno 2. 10. 2026 (20:1x–21:0x UTC)" in orig.decode("utf-8"):
        print("  §25 už v souboru JE — nic se nezapisuje (idempotentní).")
        return 0
    ZALOHA.write_bytes(orig)
    print("  záloha: %s (%d B)" % (ZALOHA.name, len(orig)))
    text = orig.decode("utf-8")
    novy = text.rstrip("\n") + "\n" + SEKCE8L + SEKCE25
    HANDOFF.write_bytes(novy.encode("utf-8"))
    over = HANDOFF.read_text(encoding="utf-8")
    chyby = []
    for kotva in ("## 25. Provedeno 2. 10. 2026", "### 8m. Omyly AKČNÍ session",
                  "| **105** |", "| **112** |", "25.5 Vlastní omyly"):
        if kotva not in over:
            chyby.append("kotva %r v souboru NENÍ" % kotva)
    if not over.startswith(text[:200]):
        chyby.append("začátek souboru se ZMĚNIL (append-only porušen!)")
    if len(over) < len(text):
        chyby.append("soubor se ZMENŠIL (%d → %d)" % (len(text), len(over)))
    print("  zapsáno: %d → %d B" % (len(orig), len(over.encode("utf-8"))))
    if chyby:
        HANDOFF.write_bytes(orig)
        for c in chyby:
            print("  CHYBA: %s" % c)
        print("  → soubor VRÁCEN ze zálohy")
        return 1
    print("  ověřeno: všech 5 kotev je v souboru, začátek nezměněn, soubor neroste dolů")
    return 0


if __name__ == "__main__":
    sys.exit(main())

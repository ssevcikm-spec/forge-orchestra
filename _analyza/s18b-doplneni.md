
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
---

### 18.15 Vada měřidla, kterou jsem sám vyrobil — a její TŘI neúspěšné opravy

**Co se stalo:** `kronika-kontrola.py` počítá omyl v každém bloku `HANDOFF.md`
§8 jako **řádek tabulky** `| **N** | …`. Po zapsání §18 do `HANDOFF.md` začal
u bloku **8f** hlásit **54 omylů místo 10** a celkem **105 místo 55**.

**Příčina (naměřeno, ne odhadnuto):** do výřezu bloku 8f spadla **tabulka
NÁLEZŮ z §18.11**, jejíž řádky začínají taky `| **H8** | …` — a kotva „do"
(`## 9.`) je v souboru **až za §13–§18**, protože nové oddíly se přidávají
**appendem na konec**. **Kontrola tedy měřila cizí tabulku a tvrdila o ní, že
jsou to omyly.**

**A pak se to zhoršilo — tři neúspěšné opravy téhož:**

| # | Co jsem udělal | Co to způsobilo |
|---|---|---|
| 1 | Zúžil jsem kotvu `## 9. …` (správně) | Počty sedly — **ale jen pro tenhle soubor v tenhle okamžik**; křehkost zůstala |
| 2 | Přidal jsem filtr `radek.count("\|") != 4` („tabulka omylů má 4 oddělovače") | **Vyhodil VŠECHNY řádky** → brána hlásila **0 omylů** a **7 ROZCHODŮ**. Buňky totiž obsahují znak `\|` **uvnitř kódu** — řádek omylu 50 jich má **5**, stejně jako řádek nálezu H8 |
| 3 | `re.match(r"…\d+\|", radek)` (id musí končit svislítkem) | **Taky 0** — tabulka je psaná **bez mezer** (`\| **50** \|`), takže id je mezi hvězdičkami a svislítkem |

**Co to opravilo (a je to jiné kritérium než všechny tři výš):** id musí být
**čistě číselné** — `(\d+)` v capture group a `**` kolem něj **volitelné**.
Řádek nálezu `| **H8** |` tím neprojde, protože `H` není číslice. Ověřeno
**na pěti vzorcích** (řádek omylu, řádek nálezu, řádek bez hvězdiček, řádek
s `8b`, text s odkazem uprostřed).

> **⚠ POUČENÍ, které patří do skillu `overovani` (a je to jeho čtvrtá variace
> téhož):** **počet oddělovačů v řádku není identifikátor řádku** — buňky
> tabulky obsahují `|` jako **obsah**. Kdo se ptá na **tvar** místo na
> **význam sloupce**, dostane 0 nebo 54 a **v obou případech to vypadá jako
> nález o datech**. A druhý, dražší důsledek: **každá z těch tří oprav spadla
> na SPRÁVNÉM souboru** — falešný poplach na správném vstupu je stejná vada
> jako slepá kontrola, jen se hůř hledá.

**Vedlejší nález téhož běhu:** kontrola hlásila **„CHYBI: ARCHITEKTURA.md"**,
protože vzor pro odkazy **odřízl `docs/` z cesty**. V dokumentu je
`docs/ARCHITEKTURA.md` (relativní cesta **uvnitř herního repa**), ale regex
bral jen `[A-Za-z0-9_-]+\.md` bez lomítka → hledal soubor ve workspace.
**Opraveno** (lomítko je součástí vzoru a hledá se i v `games/uo-shadows/`)
a **jedno holé odvolání v textu jsem přepsal na plnou cestu**, aby kontrola
nemusela hádat. **Je to falešný poplach na existujícím souboru** — tedy třetí
vada téhož měřidla v jednom kroku.

**Stav po opravě:** `kronika-kontrola.py` → **`KRONIKA SEDÍ`, `exit 0`**,
omylů **61** (13 + 10 + 5 + 6 + 11 + 10 + 6), nálezů **12** (H1–H12),
sessions **15**, odkazů **14**. A **mutační test `h17-kronika-mutace.py`
4/4** (zdravá kopie projde, každá ze 4 vrácených vad shodí) — bez něj by
„zelená" znamenala jen ticho.


> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 18.18 Odpověď na „menší granule nebo sekvenčně?" — a TŘETÍ vada v mém měření

**Otázka uživatele (2. 10. 2026):** *„Groq se nedá použít tedy ani na menší
granule nebo sekvenčně?"*

**Odpověď: menší granule samotné NEPOMOHOU a „sekvenčně" NEJDE. Jediná páka je
zmenšit `CONVENTIONS.md` — na ~60 % dnešní velikosti.**

Nástroje: `python _analyza\p19g-granule-vs-groq.py` (všechny granule),
`python _analyza\p19h-groq-presne.py` (přesný výpočet),
`python _analyza\p19i-co-zmensit.py` (co zmenšit).

**Vstup se skládá ze DVOU částí a to je celý trik:**

| Složka | Co to je | Kolik |
|---|---|---|
| **PEVNÁ** | `CONVENTIONS.md` (`--read` do každého běhu) + **obal Aideru** | **9 196 tokenů** |
| **VLASTNÍ** | soubory granule + její prompt | **335 – 15 475 tokenů** |

**Pevná část platí pro KAŽDOU granuli** — a **9 196 > 8 000**, tedy **nad limitem
dřív, než se přidá cokoli z granule.** To je odpověď na „menší granule".

**Kolik by `CONVENTIONS.md` musel mít** (je to jediná ovlivnitelná páka):

| `CONVENTIONS.md` | tokenů | pevná část | vešlo by se granulí |
|---|---|---|---|
| **11 519 znaků (dnes)** | 3 839 | **9 196** | **0 z 21** |
| 9 000 znaků | 3 000 | 8 357 | 0 z 21 |
| 6 000 znaků | 2 000 | 7 357 | **2 z 21** |
| 4 500 znaků | 1 500 | 6 857 | 4 z 21 |
| **3 000 znaků** | 1 000 | 6 357 | **10 z 21** |
| 1 500 znaků | 500 | 5 857 | 10 z 21 |
| 0 znaků | 0 | 5 357 | 12 z 21 |

→ **Zlom pro nejmenší granuli (`core.attributes`, vlastní část 335 t.):**
`CONVENTIONS.md` smí mít **max ~6 924 znaků** — tedy **60 % dnešní velikosti**.

**„Sekvenčně" nejde** — a je to doložené z textu hlášky: limit je **`Request too
large`** (na **JEDEN request**), ne minutová kvóta. Aider posílá **celý kontext
v jednom requestu**; rozdělení na víc běhů by znamenalo, že agent nevidí celek
— a přesně na tom padaly granulе dřív („add the file to the chat",
`agent.yml:167–180`).

> **⚠ TŘETÍ VADA V MÉM MĚŘENÍ (omyl 71, §8g):** první verze `p19i-co-zmensit.py`
> hlásila u **prázdného** `CONVENTIONS.md`, že se vejde **12 z 21** granulí —
> a přitom sama o řádek výš tvrdila, že se nevejde ani jedna. **Počítal jsem
> `zbytek - t_conv`**, kde `zbytek` **už `CONVENTIONS.md` obsahuje** — takže
> mi vyšla „vlastní část" **4 175 tokenů** místo skutečných **335**. Rozdíl je
> **12×** a měnil odpověď. **Odhalil to `p19i-sonda2.py`** (nezávislý přepis
> téhož výpočtu), ne moje pozornost.
>
> **A druhá věc téhož:** v hlavičce skriptu zůstala **stará proměnná** a psala
> „nejmenší granule: vlastní část 4 175 tokenů" — tedy **totéž číslo, které jsem
> právě opravil**. To je přesně past „dva čítače téhož jména": **jedno jméno
> (`nejmensi_t`) znamenalo dvě různé veličiny** (včetně pevné části / bez ní).
>
> **Poučení:** když výpočet dává **číslo, které si odporuje s jiným řádkem téhož
> výstupu**, je to **vada měření** — ne „zajímavý výsledek". A **druhý přepis
> téhož vzorce** je nejrychlejší způsob, jak to najít.

**VÝHRADA, která platí pro celou tuhle odpověď:** obal **5 357 tokenů** je
**DOPOČET** z jednoho reálného běhu (Groq naměřil 14 398 − moje znaková část
9 041), **ne měření obalu samého**. Kdyby byl obal menší, vešlo by se granulí
víc — při původním **odhadu 2 166 t.** by se vešlo **10 z 21** i s dnešním
`CONVENTIONS.md`. **Přesné číslo obalu dá jediné:** spustit Aidera a přečíst
jeho vlastní `Tokens: … sent` — což v logu #146 **nebylo** (naměřeno 0 výskytů,
Aider tam jen hlásí `Unknown context window size … using sane defaults`,
protože model `openai/openai/gpt-oss-120b` nezná).

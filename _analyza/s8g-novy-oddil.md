
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
---

### 8g. Omyly PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (12:2x–13:3x UTC)

> **Pět z šesti** omylů vzniklo v **měřidle nebo ve mně** — a **dva z nich
> vypadaly jako nález o cizím kódu** (jeden málem zapsal nepravdivé „číslo 14 398
> v logu není"; druhý málem ohlásil, že běhy z GitHubu zmizely).
> **Plný popis je v §18**; tady je tabulka ve stejném tvaru jako 8b–8f.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **61** | **„Číslo 14 398 v logu běhu #146 NENÍ — je tam `Requested 2026`."** Málem jsem to zapsal jako **vyvrácení hlavního nálezu §17.5**. | **Je tam.** Log má 9× `Limit 8000, Requested` na jednom řádku a **`14398, please reduce…` až na DALŠÍM** — GitHub každý řádek prefixuje časovým razítkem a hláška je **zalomená**. Můj regex `Requested\s+(\d+)` přes newline **nesáhl** a `\s+` spadlo na **rok `2026` z časového razítka dalšího řádku** | Napsal jsem regex na **jednořádkový** tvar hlášky, ale **zdroj je víceřádkový**. Naměřeno na **111 435 B staženého logu**: `Requested[\s\S]{0,60}?(\d{2,7})` → **9× `14398`**. **Poučení:** když hláška vypadá „jinak, než jsem čekal", **nejdřív si vypiš okolí** (`surove[i-260:i+160]`), teprve pak měň vzor |
| **62** | **„Běhy #142–#146 na GitHubu zmizely"** — filtr našel `0 z 20` a vypadalo to, že byly smazané (retence?) | **Jsou tam.** Workflow se jmenuje **`"Forge agent"`** a běh sám **`"Forge #146 [uuid]"`** — a já filtroval `/agent/i.test(run.name)`, což je **case-insensitive substring**, který `"Forge agent"` **nemá** (slovo „agent" tam v tomhle pořadí… je, ale s „Forge" před ním — a `name` běhu je `Forge #146 […]`, **bez slova agent**). Běhy jsem nakonec našel přes **konkrétní ID**: `run_number` **#265–#269** | Filtr **jménem** místo **ID**. A hned vedle toho druhý omyl téhož druhu: **`#146` v názvu běhu je ID ÚLOHY CONDUCTORA**, kdežto `run_number` téhož běhu je **269** — **přesně ta past, před kterou `AGENTS.md` varuje** („různé čítače nesou stejné jméno") |
| **63** | **„Python na tahle data stačí"** — napsal jsem `p18-sonda-tpm.py` s `urllib.request` na `/actions/jobs/<id>/logs` | `HTTP Error 401: Server failed to authenticate the request` **po přesměrování** (302 na blob storage). **Není to problém přístupu na GitHub** — PAT fungoval na `/runs`, `/jobs` i `/pulls`. Python přesměrování na tenhle blob nezvládl | **Tatáž past, kterou `AGENTS.md` popisuje u TLS z PowerShellu — jen o vrstvu jinde:** „na síť jdi **Node `fetch`**". Napsal jsem si ji znovu, protože jsem řešil „log", ne „síť". Opraveno `p18-stahni-log.mjs`; k tomu navíc **ANSI escape sekvence** v logu (řešeno `re.sub(r"\x1b\[[0-9;]*m", "", …)`) |
| **64** | **„Graf `g3-brany.py` má bránu na `check-schema`"** — a myslel jsem, že je zelená, protože ta brána existuje | Ta brána volala `validate-all.mjs --jen hra`, a **`--jen` není přepínač** (v souboru **0 výskytů**, validátor **nečte `process.argv`**). Spustil se **celý validátor** — **tatáž komanda jako „validate-all (CELEK)" o dva řádky níž** | Bral jsem **NÁZEV brány** jako popis toho, co měří (`AGENTS.md`: „u brány se ptej, PROBĚHLA a CO změřila"). **Nebyl to omyl ve čtení — byl to nález (H8)**, který jsem **opravil**: brána teď volá `check-schema.py` přímo nad hrou a dává `exit 0` / „Schéma je v souladu" |
| **65** | **„Druhy omyl v `h17-vsechny-behy.mjs` je jen kosmetický"** — ale týž skript hlásil u ostatních čtyř běhů `TPM=-` a já to nechal být | **Správně `-`:** ty čtyři běhy **na TPM vůbec nedošly** (spadly na parsování) — takže „žádná hodnota" je **naměřená nula s rozlišeným důvodem**, ne ticho. Ale **já jsem si to musel ověřit**, protože by to mohlo být i „regex nenašel" | Nerozlišil jsem **dvě příčiny téhož výstupu** (`-` = nedošlo k tomu vs. `-` = nenašel jsem to). Ověřeno čtením **kroků jobu** (`job.steps`) — u #145–#142 je `failure` krok **„Kontrola parsování (rychlá brána)"**, u #146 **„Agent nic nezměnil"** |
| **66** | **`python _analyza\h17-vsechny-behy.mjs`** (místo `node`) | `SyntaxError: invalid character '—' (U+2014)` — **Node skript spuštěný Pythonem**; vypadalo to jako rozbitý soubor s diakritikou | Spustil jsem `.mjs` špatným interpretem a chybová zpráva **ukazovala na český znak v komentáři**, ne na příčinu. **Poučení:** chyba na **prvním řádku** souboru, který je jinak v pořádku, je skoro vždycky **špatný nástroj**, ne vadný soubor |

| **67** | **„Přepočet omylů z `HANDOFF.md` je hotový"** — a pak jsem **třikrát** opravoval totéž měřidlo, pokaždé jinak špatně | **Tři různé vady v jednom kroku** (podrobně `HANDOFF.md` §18.15): (1) blok `8f` počítal **54 místo 10**, protože do výřezu spadla **tabulka nálezů** z §18.11 (řádky začínající `H8`); (2) oprava přes „řádek má 4 oddělovače" vyhodila **VŠECHNY** řádky — buňky mají znak svislítka **uvnitř kódu** (řádek omylu 50 jich má **5**) → **0 omylů, 7 ROZCHODŮ**; (3) vzor vyžadující svislítko **hned za id** vrátil taky **0**, protože tabulka je psaná **bez mezer**. Opravilo to až kritérium **„id je čistě číselné"** | **Tři falešné poplachy na SPRÁVNÉM souboru** a jedno **slepé místo** (0 omylů = „nic tam není"). Kdybych se ptal na **tvar** řádku místo na **význam sloupce**, zůstalo by to. Odhalil to **mutační test** (`h17-kronika-mutace.py`), ne moje pozornost |

**Vzor z těch osmi:** **sedm z osmi** vzniklo v **měřidle** (regex přes
místo obsahu, nerozlišené `-`, tři vady přepočtu omylů) — a **tři vypadaly jako
nález o cizím kódu nebo datech** („číslo tam není", „běhy zmizely", „kronika
lže o 50 omylů").
**Ani jeden z těch tří nebyl nález o datech.** Je to týž vzor jako 8b–8f, jen
o kolo dál — a **zachránilo to pokaždé něco jiného než moje pozornost**:
u **61** **vypsání okolí** místo dalšího hádání vzoru, u **62** hledání podle
**ID** místo podle jména, u **67** **mutační test**, který ukázal, že brána po
„opravě" hlásí **0 omylů** — což je nemožné, a je to vidět.

> **⚠ A poučení, které stojí za zapsání zvlášť (protože se týká ZADÁNÍ, ne mě):**
> **tři čísla ze `HANDOFF.md` §17 jsem přeměřil a jedno z nich bylo jiné** —
> počet `litellm.RateLimitError` je **9**, ne 8. **Není to nepravda** (8 bylo
> naměřeno jiným nástrojem v jiném čase), ale **je to přesně ten důvod, proč se
> čísla přeměřují** a proč se k nim píše **postup**. Kdo je čte bez postupu, buď
> jim uvěří, nebo je „opraví" špatně.

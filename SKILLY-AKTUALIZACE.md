# Návrh aktualizací dokumentace a skillů (30. 9. 2026)

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

## ➕ VLNA 13 — 1. 10. 2026 (večer): ověřování cizí práce a stavová vrstva

> **STAV: APLIKOVÁNO.** Tahle vlna **nevznikla psaním nového** — vznikla
> **ověřováním hotového**. Uživatel dal tři zadání: projít plán a handoff →
> aktualizovat skilly a dokumentaci → připravit plán implementace pro nový chat.
>
> **Co se u toho našlo (a je to hlavní hodnota vlny):**
>
> | Co | Naměřeno |
> |---|---|
> | **`HANDOFF.md` lhal ve čtyřech bodech** | „77 řádků `git status`" → **0**; „Pillow není commitnutý" → **je**; „běhy #355–#362" → **#235–#241**; „20 běhů celkem" → **`total_count` 241**; „PR se sloučily samy" → **`merged_by` = člověk** |
> | **F0.5 je hotové** (plán i handoff tvrdily „odloženo") | commit **`525d45b`** smazal **8** souborů; `oprav-ps1-kodovani.py` zůstal (živý nástroj) |
> | **NOVÝ NÁLEZ: `NAZEV-REPA`** | Šablona vydává release s **doslovným** `NAZEV-REPA`; `release.yml:82,143` jsou literály v `echo`, instalátor kopíruje `.github` bez substituce. **Simulace `Copy-Item` → v novém repu zůstane 3×** |
> | **`validate-all.mjs` vrací vždy `exit 0`** i při „✗ NALEZENO" — a volá **starou slepou kopii** brány | spuštěno pod sandboxem i s širším oprávněním |
> | **Ze 13 doporučení analýzy jsou hotová 2** (L4, L5) | `_analyza\stav-doporuceni.mjs` |
>
> ### Zapsané změny
>
> | Co | Kam |
> |---|---|
> | **Z1** „brána, která nemá jak selhat, není brána" (vzorec ze 3 případů) | `AGENTS.md` |
> | **Z2** „šablona nesmí tvrdit nic o konkrétním projektu" + testovací otázka | `AGENTS.md` |
> | **Z3** „před smazáním kódu ověř, že jeho znalost je zapečená — v obou kopiích" | `AGENTS.md` |
> | pasti: `git show \| Measure-Object -Line` (166 vs 182), „různé čítače nesou stejné jméno", „statická metrika, která nic nespustí" | `AGENTS.md` + skill `dsh-prostredi` |
> | **Z4** §8 dodatek se **S17** (model nepozná verzi enginu) a **S18** (zelený řídicí systém nad červeným cílem) | `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` |
> | **Z5** sabotér jako měřená schopnost | `MOZNOSTI-AGENTA.md` |
> | **Z6** diagnostika „orchestra nic nedělá" (5 kroků, začíná **stavem CI cílové hry**) | skill `orchestra` |
> | **Z7** past „dvě jména téhož pole" | skill `game-developer` |
> | **§3.5 implementační plán** (fáze A–D) + §6 stav rozhodnutí O1–O10 | `PLAN-ROZVOJ-ORCHESTRA.md` |
> | **Nový dokument se stavem doporučení** | `ORCHESTRA-STAV-A-ANALYZA.md` |
> | Rámeček „Stav obálky" převeden na **uzavřený** (F0) | `orchestra/README.md` |
>
> ### Dvě chyby, které tahle vlna přiznává
>
> **1. Můj falešný poplach (CH14).** Staticky jsem spočítal volání `test(`
> v `vision.test.mjs` (**42**) a uzavřel, že handoff lže o počtu testů
> (**36/36**). **Po spuštění: šablona 36/36, hra 28/28, root 5 OK / 23 chyb** —
> handoff měl pravdu do puntíku. **Statická metrika, která nic nespustí, je
> stejně slabá jako kontrola čtoucí komentáře** — a svádí k „opravě" správného
> dokumentu.
>
> **2. `orchestra/README.md` tvrdilo „0 výskytů gameforge v conductoru"** —
> neplatí, jsou tam **2 komentáře** (`:1104`, `:1127`). Vzniklo to hledáním
> **case-sensitive** (`gameforge` vs `GameForge`). Opraveno slovem i měřením.
>
> ### Ověřeno
>
> - `over-dokumentaci.py` → **63 kontrol, 0 chyb**; `over-skilly.py` → **11
>   skillů, 0 chyb**; `kontrola-diakritiky.py` → **VŠE OK**
> - `over-handoff-nic-nezmizelo.py` → **29 kontrolovaných bodů, 0 chybějících**
>   (kontrola, že přepis handoffu nic neztratil — **a našla 3 chybějící, které
>   se doplnily**)
> - `vision.test.mjs` spuštěn na všech **třech** kopiích (36/36, 28/28, 5/23)
> - `baseline.py testy` **24/24**, `test-check-schema.py` **17/17**
>
> ### Co tahle vlna vědomě NEUDĚLALA
>
> **Neimplementovala žádnou opravu orchestra.** Kód conductora i nástrojů je
> **nedotčený** — `validate-all.mjs`, `test-cooldown.py`, `NAZEV-REPA`
> i tři vady conductoru **čekají na fázi A–D** (`PLAN-ROZVOJ-ORCHESTRA.md` §3.5).
> Je to záměr: tahle session ověřovala a dokumentovala, ne opravovala.

---

## ➕ VLNA 12 — 1. 10. 2026: měření, které odpovídá na jinou otázku

> **STAV: APLIKOVÁNO.** Vzniklo z **incidentu při migraci dat z `E:\DSH`**
> (vlna 11 níž) — kde jsem „opravou" podle jednoho měření **přepsal 14
> skutečných souborů**. Data se vrátila z karantény, ale ta lekce patří
> do skillů: je obecná a stála reálná data.
>
> | Co | Kde | Z čeho |
> |---|---|---|
> | **Třetí otázka: „umí ta veličina odpovědět na moji otázku?"** | `overovani` §1 | `Target`/`readlinkSync` má **různý význam podle typu objektu**: u junctiony cíl vazby, u **hardlinku cestu souboru samotného**. Kód, který se ptá „kam vede tento cíl?", dostane u hardlinku cestu k sobě — a přepíše data |
> | **Měření může lhát OBĚMA směry** | `overovani` §1.2 | `Test-Path "$link\soubor"` u junctiony na soubor vrací `False` i když funguje (falešný poplach); `existsSync` u smyčky vrací `ELOOP` (falešná chyba). Když oba výsledky vypadají stejně, měření neříká nic |
> | **Dva nové anti-vzory** | `overovani` §5 | „opravovat podle jedné vlastnosti, která má víc významů" a „operace pokračuje po částečném selhání" |
> | **`Target` u hardlinku** + pravidlo „ověř dvěma způsoby, než přepíšeš" | `dsh-prostredi` §3b | Konkrétní okolnosti (PowerShell/Windows) |
> | **Popis skillu rozšířen** o destruktivní operace | `overovani` frontmatter | Aby se skill načetl i tehdy, když nejde o test, ale o přepis dat (470/500 znaků) |
>
> ### Princip, který z toho plyne
>
> **„Ověřeno měřením" není totéž jako „ověřeno".** Dosud měl skill `overovani`
> dvě otázky — *proběhla brána?* (pokrytí) a *umí spadnout?* (síla).
> Chyběla třetí: ***je ta veličina vůbec schopná odpovědět na moji otázku?***
>
> A z ní plyne pravidlo pro zápis: **jeden zdroj pravdy stačí na čtení;
> na mazání a přepisování nestačí.** Než přepíšu cokoli, co může být skutečný
> soubor, ověřím **dvěma nezávislými způsoby**, co to je.
>
> ### Ověřeno
>
> - `over-skilly.py` → **11 skillů, 0 chyb**; `overovani` description 470 znaků (strop 500)
> - `kontrola-diakritiky.py` → VŠE OK; **0 cizích (CJK) znaků** v obou skillech
> - Struktura: `overovani` §1.1 a §1.2 sedí pod §1; `dsh-prostredi` nová podsekce v §3b
> - **Žádný nový skill nevznikl** — katalog skillů je prefix, každý záznam
>   zdržuje každý request

---

## ➕ VLNA 11 — 1. 10. 2026: migrace dat z `E:\DSH` a dvě pasti junctionů

> **STAV: APLIKOVÁNO.** Zadání uživatele: *„E:\DSH je zastaralá složka
> předchozí verze harnessu… bude za týden smazaná. Zapiš, že se nemá používat,
> nebo rovnou připrav její smazání."*
>
> **Ukázalo se, že to není zastaralá složka.** `E:\DSH\data` byl **živý
> `DSH_HOME` běžící aplikace** — API klíče, 86 session logů, 11 skillů, profily
> — přes junction `C:\Users\Ssevc\.dsh`. Smazání by je nenávratně zničilo.
> Mrtvé bylo jen `E:\DSH\app` (byla to bývalá aplikace; běží z `E:\DeepSeekHarness`).
>
> **Výsledek:** data migrována na `E:\DeepSeekHarness-data`, stará data
> i `roaming` v `E:\DSH-quarantine\20261001-144747\`, `E:\DSH` smazáno.
> Aplikace po celou dobu běžela — ověřeno zápisem 12 s po smazání.
>
> | Co | Kde | Z čeho |
> |---|---|---|
> | **`migrate-dsh-data.ps1`** | `dsh-consolidation\cleanup\` | Chybějící krok: `cleanup-dsh.ps1` vede `E:\DSH\data` jako živý (ř. 46) a **nikdy se ho nedotkne**, takže data by po smazání `E:\DSH` zmizela. Dry-run default, tvrdé guardy, rollback jeden příkaz |
> | **`test-migrace.ps1`** | tamtéž | Syntetický strom se smyčkou junctionů **a junctionou na soubor**. Mutačně ověřen |
> | **Pravidlo v `AGENTS.md`** | §„Co nikdy" | Zapsáno jako varování **před** migrací; po ní přepsáno na stav + poučení |
> | **`POZOR-E-DSH-NEMAZAT.md`** | root | Co bylo živé, časová osa selhání, pasti, rollback |
> | **Oprava 16 skriptů** | `_analyza\*.mjs` (14×), `dsh-usage\report.mjs`, `analyza.mjs` | Konstanta `E:\DSH\data\sessions` natvrdo. Byla **redundantní** — `~\.dsh\sessions` je junction na totéž místo |
>
> ### Dvě pasti junctionů, které stály reálná data
>
> **1. `New-Item -ItemType Junction` umí jen cíl typu ADRESÁŘ.** Sedm junctionů
> v `attachments` míří na **soubor** (`file-objects\X` → `files\X\soubor.zip`).
> Ostrá migrace proto obnovila **1 z 15** junctionů. Řešení: **`mklink /J`**
> (zvládá obojí a nevyžaduje existující cíl).
>
> **2. Junctiona na soubor se NEDÁ ověřit přes `Test-Path "$link\soubor"`.**
> Vrací `False` i u funkční junctiony — Windows se pod junctionou na soubor
> neprochází jako pod adresářem. Ověřuj `Test-Path $link` **a shodu `Target`**.
> Tahle past mě málem donutila „opravovat" správný kód.
>
> A třetí, obecnější: **v `attachments` je citační smyčka** (`file-objects` ↔
> `files`) — `robocopy` bez `/XJ` se na ní zacyklí.
>
> ### Princip, který z toho plyne (a je nejcennější)
>
> **Skript, který pokračuje po částečném selhání, je horší než skript, který
> spadne.** Ta migrace obnovila 1 z 15 junctionů, **zbytek jen vypsala jako
> chybu a jela dál** — přepnula junction a ohlásila `HOTOVO`. Chybějící vazba
> se přitom neprojeví hned, ale až když na ni něco sáhne.
> **Pravidlo: částečný neúspěch musí operaci zastavit PŘED nevratným krokem**,
> ne se jen zapsat do logu.
>
> ### Ověřeno
>
> - Reálná kopie: **8 150 = 8 150 souborů**, 381 MB, kritické soubory shodné
> - Nový store: **15/15 junctionů živých, 0 visících** (před opravou 1/15)
> - `test-migrace.ps1`: správná verze **exit 0**, mutace (`New-Item` zpět)
>   **exit 1** — test není slepý
> - Po smazání `E:\DSH`: aplikace běží, zápis do nového store **12 s** po smazání,
>   `~\.dsh` → `E:\DeepSeekHarness-data`, 11 skillů, 86 sessions, credentials OK
> - Brány: diakritika, `over-dokumentaci.py` **63/0**, `over-skilly.py` **11/0**
>
> ### Poučení mimo migraci
>
> **Nepravdivé tvrzení o stavu se čte jako fakt a plánuje se podle něj.**
> „`E:\DSH` je zastaralá složka" bylo míněno jako kontext, ale kdyby se podle
> něj jednalo, přišlo by se o klíče a celou historii. **Než se něco smaže,
> ověř, co v tom je** — a to i když to říká uživatel, protože i on může mít
> zastaralou informaci z dřívější migrace.

---

## ➕ VLNA 10 — 1. 10. 2026: nasazení indikátorů a čtyři zjištění, která opravila dokumenty

> **STAV: APLIKOVÁNO.** Zadání uživatele: *„Cílem je nyní instalovat pluginy
> a skilly za účelem optimalizace výkonu a ceny provozu"* a poté *„Jestli máš
> co zapsání do skillů, či dokumentace, zapiš."*
>
> Tahle vlna **není o novém kódu** — bundle i skripty byly hotové z dřívějška.
> Je o tom, co se ukázalo při jejich **nasazení a ověřování**: čtyři tvrzení
> v dokumentaci byla nepravdivá a jedno číslo jsem si sám nafoukl.
>
> | Co | Kde | Z čeho |
> |---|---|---|
> | **Bundle nainstalován** | `plugin_manager install_bundle` → `@local/dsh-tarif-indikator` | `application: "applied"`, `warnings: []`. Klientská polovina živá: `Slots.listSubTree` na `conversation.composer.dock` vrací `{id:"tarif-indikator", order:40, active:true}` vedle `stats` |
> | **Skill nainstalován** | `~\.dsh\skills\otevrena-temata\SKILL.md` | SHA-256 shodný se zdrojem (`7457BC48…97D1`); `over-skilly.py` → **11 skillů, 0 chyb**. Zkopírován **jen `SKILL.md`**, ne `kontrola-temat.mjs` — ten počítá root workspace z vlastní cesty |
> | **Nepravda 1: „Creator mód je potřeba"** | `ZADANI-CREATOR-INDIKATORY.md`, `index.js` | `plugin_manager` i `cordis_inspect_query` fungují **v běžné session**. Potřeba je **schválení** (`danger-full-access`), ne jiný preset. Zadání stavělo celý postup na tom, že do Creator módu „se nedá přepnout" — což je pravda, ale irelevantní |
> | **Nepravda 2: `contextPressure{pressureTokens, projectedTokens, contextWindow}`** | `ZADANI-CREATOR-INDIKATORY.md` §3B, `index.js` | **V DSH neexistuje.** `TokenMeasurement` má `logRevision`, `baseline`, `surfaceDeltaTokens`, `totalTokens`, `surfaceTokens`, `nodes`. `contextWindow` je ve `RequestContext` (`session.requestContext()`) |
> | **Nepravda 3: „smazat 188 visících junctionů"** | `OTEVRENA-TEMATA.md` | Naměřeno: **1 junction, 0 visících** — migrace z `E:\DSH` už proběhla. A v tom jediném visí **nově nainstalovaný indikátor**, takže splnění toho pokynu by bundle odinstalovalo. **Položka „uklidit node_modules" se sama stala rizikem** |
> | **Nepravda 4: `scoop install main/ast-grep`** | `OTEVRENA-TEMATA.md` | `scoop` ani `choco` na stanici **nejsou**; je jen `winget` a `npm`. Ověřeno, že to jde: `@ast-grep/cli` 0.45.3 má prebuilt `win32-x64-msvc` |
> | **Nafouknuté číslo: cache-bust $3,86** | `~\.dsh\skills\dsh-usage\SKILL.md` | $3,86 platí na **přepis systémového promptu** (61 případů, 46 v jedné session), **ne** na vložení zprávy — tam jde o přírůstek od bodu vložení, ~**$0,01** při 130k. Rozdíl ~2 řády. Odmítal jsem kvůli tomu levnou operaci špatným nákladem |
>
> ### Principy, které z toho plynou
>
> **1. „Čeká na dodělání" a „vědomě se nedělá" vypadají v ledgeru stejně.**
> První z toho plánuje práci, která nemá přínos. Rozdíl je potřeba **zapsat**,
> nebo se to řeší znovu. (Téma „upozornění pro model" bylo přesně tohle:
> ověřením padl důvod „nejde to ověřit" — a tím padl i důvod to stavět.)
>
> **2. Cena není argument, dokud není změřeno, ČEHO se cena týká.**
> „Cache-bust je drahý" je pravda o systémovém promptu a nepravda o vložené
> zprávě. Špatně přiřazené číslo **zakáže levnou operaci** a vypadá přitom
> jako rozpočtová zodpovědnost.
>
> **3. U junctionů nelže `Target` ani `LinkType` — věř jen `realpathSync`.**
> Tři různé druhy nepravdy naměřené v jedné session: `Target` na neexistující
> cestu (`C:\DSH\data\skills`, přitom `Test-Path C:\DSH` = False), `LinkType`
> prázdný u skutečného junctionu, `LinkType` vyplněný správně. **Důsledek
> s zuby:** `~\.dsh\sessions` a `E:\DSH\data\sessions` vypadají jako dvě cesty
> a jsou to **tytéž soubory** — bez `realpath` dedup se každá session počítá dvakrát.
>
> **4. Dokumentace, která popírá vlastní nástroje, je horší než žádná.**
> Čtyři nepravdy výš měly společný podpis: vedly k postupu, který **nejde
> provést** (Creator mód) nebo k **neexistujícímu API** (`contextPressure`).
> Každá z nich by stála samostatnou session.
>
> ### Ověřeno
>
> - Bundle: `include:tarif-indikator` → `enabled:true`, `fiberPhase:active`; slot `tarif-indikator` `active:true`
> - Skill: SHA-256 shodný se zdrojem, 4 823 B; `over-skilly.py` → **11/0**
> - `test-tarif.mjs` **40 kontrol, 0 chyb** (i po editaci `index.js`); `kontrola-temat --test` **8/0**
> - `kontrola-diakritiky.py`, `over-dokumentaci.py` (63/0), `over-skilly.py` → **VŠE OK**
> - Ledger: **3 otevřené, 10 uzavřených**, verdikt 🟢
> - `_analyza\over-okno.mjs` — nový skript: `contextWindow` z `request/context`.
>   `deepseek-flash`/`-v4-flash`/`-v4-pro` = **1 000 000** (předpoklad
>   `PK = 800000` v `report.mjs` **platí**), ale `-v4-flash-free` = **200 000**
>   a `assistant` = **262 144** → na těch by prahy ležely **nad oknem**
> - **Přiznaná mez:** vizuální důkaz indikátoru **nebyl pořízen** — není
>   ovládání prohlížeče. Doloženo je, že entita je zaregistrovaná a `active`,
>   **ne** že je vidět

---

## ➕ VLNA 9 — 1. 10. 2026: šablona je obecná, hra konkrétní

> **STAV: APLIKOVÁNO.** Zadání uživatele: *„Staré granule promazat. Vše
> v orchestra má být obecné, hra konkrétní — tedy vision nemá hledět na UO,
> ale má být přepínatelný, když na ní orchestra pracuje."*
>
> To je **princip**, ne dva soubory — a je zapsaný tak, aby platil dál:
>
> | Co | Kde | Z čeho |
> |---|---|---|
> | **Roadmapa šablony: 31 → 0 granul** | `orchestra/repo/.forge/roadmap.json` | Byl tu plán JINÉ, smazané hry (`chest-unlock2`, `minimap`, …) a `install-into-repo.ps1` ho kopíruje do každé nové hry. Zároveň opraven `_popis`, který lhal ve **třech** bodech: „pracuje se po jedné" (proti `MAX_CONCURRENT=5`), „až je zkontroluješ" (auto-merge to dělá sám), „Plánovač (`forge plan`)" (GameForge smazán) |
> | **Vision profil šablony: žádná data o hře** | `orchestra/repo/.forge/vision-profile.json` | `hra: "uo-shadows"` → **`null`**; UO `styl_popis` → **`popis_stylu: ""`** s pokynem; zákazy 3 UO-specifické → 1 obecný. Obecné věci o **kontrole** (`poskytovatele`, `self_consistency`, `cache`, `stropy`) zůstaly; doplněno `strict_poskytovatele`, které v šabloně chybělo, i když ho kód čte |
> | **Dvoujmenny fallback** | `vision.mjs` (obě kopie) | Šablona psala `popis_stylu`, kód četl **jen** `styl_popis` → hra s novým jménem by o styl **tiše** přišla. Čtou se obě jména. **+2 testy (34 → 36):** „profil s `popis_stylu` styl NESMÍ ztratit" a „profil bez stylu nespadne" |
> | **Deklarace vlastnictví** | `orchestra/tools/kontrola-driftu.mjs` | Přidán seznam souborů, které se **záměrně nesynchronizují**, s důvodem u každého: `vision-profile.json` a `roadmap.json` **patří hře**, `providers.json` má zdroj pravdy v orchestra. Kdyby je někdo přidal do `--sync`, **přepsal by hře její data** |
>
> ### Princip, který z toho plyne (a je použitelný dál)
>
> **`orchestra/repo/` je šablona: nesmí v ní být nic, co platí jen pro jednu
> hru.** Když se do šablony dostane konkrétní hodnota, zdědí ji každá nová hra
> — a to je přesně mechanismus, kterým se „pozůstatky staré hry" šíří.
> **Test:** polož si otázku „platí to i pro hru, která ještě neexistuje?"
> Když ne, patří to do hry, ne do šablony.
>
> ### Ověřeno
>
> - `grains` → **0**; `hra` → **null**; JSON obojí validní
> - `vision.test.mjs` **36/36** v šabloně **i ve hře**
> - **Herní profil a herní roadmapa NEDOTČENÉ** — hra má `hra: uo-shadows`, UO styl, 3 zákazy, **18 granul**
> - `vision.mjs` má v obou kopiích **shodný hash**
> - `kontrola-driftu.mjs` → 1 rozdíl (jen `agent.yml`, kde má hra obě kontroly spojené v jednom kroku – **není to chybějící brána**, ověřeno čtením)
> - `check-schema.py`, `check-wiring.py`, testy hry → **VŠE OK**

---

## ➕ VLNA 8 — 1. 10. 2026: dvě nové konvence a dva nové nástroje z naměřených chyb

> **STAV: APLIKOVÁNO.** Tahle vlna vznikla z **oživeného provozu** — orchestra po
> opravě Pillow začala pracovat a hned vyrobila tři nové nálezy.
>
> | Co | Kam | Z čeho vzniklo |
> |---|---|---|
> | **§1h: Godot 3 konstanty v Godotu 4 neexistují** | `orchestra/repo/CONVENTIONS.md` **i** `games/uo-shadows/CONVENTIONS.md` (shodný hash) | Běh #241, granule `ui.hud`: `Cannot find member "ALIGN_LEFT" in base "Label"` → **`hud.gd` se nikdy nedostal do repa**. Tabulka Godot 3 → 4 (ALIGN/VALIGN, autowrap, connect/yield, export/onready, `OS.get_ticks_msec`, `instance`, `Pool*Array`) + pravidlo „nepoužij konstantu, kterou jsi neviděl v tomto repu" |
> | **`echo` ve workflowech bez substitucí** | oba `agent.yml` | Běh #241: v logu se místo skutečné chyby vysypalo `var: command not found` a `syntax error near unexpected token` — **text z TIP ech**. Skutečná příčina (`ALIGN_LEFT`) se v tom šumu ztratila |
> | **`kontrola-echo-substituci.py`** (nový) | `orchestra/tools/` | Aby se to nevrátilo. **Rozlišuje vadu od záměru:** neescapovaný apostrof = vada, `\`` = bezpečné, `$( )` = obvykle záměr |
> | **`test-gitignore-tajemstvi.py`** (nový) | `orchestra/tools/` | `install-into-repo.ps1` kopíruje do hry `.env` s reálným `FORGE_SECRET`, a `.gitignore` hry ho **neignoroval** (`git check-ignore` → nic) |
>
> ### Dvě věci, které tahle vlna musí přiznat
>
> **1. První verze `kontrola-echo-substituci.py` dávala falešný poplach.** Hlásila
> každý zpětný apostrof v `echo` — včetně **escapovaných** `\`` v `release.yml`,
> které jsou bezpečné, a legitimních `$(echo … | wc -l)`. To je přesně to, před
> čím varuje `AGENTS.md`: *falešný poplach nutí „opravovat" správný kód.* Nástroj
> byl přepsán tak, aby rozlišoval.
>
> **2. Že šum v logu způsobily PRÁVĚ zpětné apostrofy, jsem NEDOKÁZAL.** Mechanismus
> jsem nereprodukoval (`echo "\`text\`"` sám o sobě v bash syntax error nevyhodí).
> Je to **silná indicie, ne důkaz** — a je to tak zapsané v hlavičce nástroje.
> Oprava je správná tak jako tak, ale kdyby se šum objevil znovu, hledej i jinde.
>
> ### Ověřeno
>
> - `test-gitignore-tajemstvi.py` → **15 kontrol, 0 chyb**; **mutační test** (odstraň `.env` z herního `.gitignore`) → **5 chyb, exit 1**
> - `kontrola-echo-substituci.py` → **0 vad**, 6 k posouzení (všechno záměr)
> - `CONVENTIONS.md` šablona vs. hra → **shodný hash**; `kontrola-driftu.mjs` → bez rozdílu
> - Oba nástroje zapojeny do `validate-all.mjs`

---

## ➕ VLNA 7 — 1. 10. 2026: zobecnění, aby na to DSH dosáhlo samo

> **STAV: APLIKOVÁNO.** Zadání uživatele: *„Zobecni co jde zobecnit a to tak,
> aby si DSH na to mohl sáhnout sám, třeba skrze skilly."*
>
> **Klíčové rozhodnutí: zobecnil jsem NÁSTROJE, ne jen texty.** Text si každá
> session přečte a zapomene; spustitelný nástroj dělá totéž pořád stejně.
> Proto mají obě změny níž **spustitelný kód**, ne jen návod.
>
> | Co | Kam | Co to je |
> |---|---|---|
> | **Skill `overovani`** (nový, 10. skill) | `~\.dsh\skills\overovani\` | Metodika ověřování bran + **dva spustitelné nástroje** |
> | ↳ `sabotuj.mjs` + `sabotuj.cmd` | tamtéž | Ověří, že brána **umí spadnout**: projde na zdravém kódu → vloží vadu → **musí** spadnout → uklidí. Rozlišuje tři různé vady (brána / sabotáž / slepá brána) |
> | ↳ `zmen.py` | tamtéž | Výroba vady pro sabotáž. Doslovná (ne regex), ověří počet výskytů, čte JSON jako `utf-8-sig` (PowerShell píše BOM) |
> | **`analyza.mjs`** (nový) | `~\.dsh\skills\dsh-usage\` | Doplňuje, co `dsh-usage` **sám přiznává, že neumí**: rozpad ceny podle modelu a effortu, a co plní kontext (velikosti výsledků podle nástroje) |
>
> ### Co ta generalizace odhalila (a je to silnější než ona sama)
>
> **1. Původní jednorázové skripty měřily špatnou věc.** `_analyza\context-fill.mjs`
> bral `JSON.stringify(o.data)` ze záznamu `tool/result` — jenže data jsou
> **zanořená** (`data.message.content[].content[].text`). Měřil tedy **celý obal
> včetně metadat**, a protože jméno nástroje hledal na špatném místě, spadly mu
> **všechny** výsledky pod klíč `?`. Jeho čísla o „velikosti výsledků podle
> nástroje" nebyla o nástrojích. Opraveno a v kódu popsané.
>
> **2. Sabotér při prvním použití odhalil vadu v sobě i ve mně.** Nejdřív spadl
> na `SyntaxError` (české uvozovky uvnitř f-stringu) a **ohlásil to jako „brána
> je slepá"** — špatná diagnóza. Opraveno: sabotér teď rozlišuje „selhala
> sabotáž" od „brána je slepá" a sám to řekne.
>
> **3. A ta drahá věc: `--uklid "git checkout -- <soubor>"` smazal hotovou
> opravu conductora.** `git checkout` vrací soubor do **commitu**, ne do stavu
> před sabotáží. Ztratil jsem necommitnutou práci a musel ji psát znovu.
> Sabotér na to teď upozorňuje; správný postup je **záloha kopií** (a commit
> před sabotáží).
>
> **4. Vlastní nástroj mě donutil opravit si `zmen.py`:** PowerShell píše JSON
> s BOM → `json.load` spadne. Čte se `utf-8-sig`. (Tatáž past jako u `.ps1`.)
>
> ### Ověřeno
>
> - `over-skilly.py` → **10 skillů, 0 chyb** (nový skill se načte a má frontmatter)
> - Skill `overovani` **je v katalogu DSH** (potvrzeno aktualizací katalogu)
> - `sabotuj.mjs` **end-to-end na skutečném případu**: brána `test-zamek-owns.py`
>   prošla na zdravém kódu, spadla na vrácené vadě → *„brána měří"* (exit 0)
> - `sabotuj.cmd` funguje (exit 2 při chybějících argumentech = správně)
> - `analyza.mjs` na 82 session logech: `web_fetch` 35,3 % objemu výsledků,
>   `read` 29,4 % — a **DSH ořezává velké výsledky na 50 000 znaků**
>
> ### Co jsem vědomě NEzobecnil
>
> `verify-setup.py` se seznamem 9 sourozeneckých složek, tři různé
> `vision.test.mjs`, absolutní cesty v 59 souborech. **To nejsou zdroje, to je
> dluh** — a jeho místo je `PLAN-SEPARACE-WORKSPACE.md`, ne skill.

---

## ➕ VLNA 6 — 1. 10. 2026 (odpoledne): tři zobecnění z vlastních chyb

> **STAV: APLIKOVÁNO.** Tahle vlna **nevznikla z auditu, ale z toho, že jsem
> sám dvakrát napsal slabý test** a jednou převzal nepravdivé tvrzení o stavu.
> Proto jsou pravidla níž **obecná** (patří do `AGENTS.md`, ne do jednoho
> projektu) — každé má za sebou konkrétní naměřenou chybu.
>
> | Co | Kam | Proč vzniklo (měření) |
> |---|---|---|
> | **`grep` tool → 80 ku 0** + pravidlo „na plošné skeny Python walk" | `AGENTS.md`, `~\.dsh\skills\dsh-prostredi\SKILL.md` | `grep` nad `orchestra/` → **0** absolutních cest; Python walk → **80 v 59 souborech**. Rozdíl mezi „nikde to není" a „je to v 59 souborech" |
> | **Statická kontrola musí číst KÓD, ne komentáře — a pozor na opačný případ** | `AGENTS.md`, `dsh-prostredi` | Můj test hledal `locked.add(lockKeys(...))` v celém souboru a **našel ho v komentáři, který vadu popisuje** → prošel i s vrácenou vadou. Odhalil to až mutační test |
> | **Test bez `assert` a bez `sys.exit` není test** + **mutační test jako důkaz** | `AGENTS.md`, `dsh-prostredi` | `tools\test-cooldown.py` vypsal `CHYBA` a skončil **`exit 0`** — naměřeno spuštěním |
> | **Tvrzení o STAVU ověřuj živě, ne z handoffu** | `AGENTS.md` | Handoff tvrdil „nic není pushnuto"; GitHub API vrátilo `0519d1a` jako **HEAD repa**. Přišlo to na dvě session |
> | **Zelený řídicí systém není důkaz, že práce probíhá** | `AGENTS.md` | Conductor: `/health` → `ok: true`, `ready: 7`, `/failed` prázdné — a přitom **7,5 h nevydal ani granuli** (`main` hry měl červené CI) |
> | **Invariant 17 přepsán (zámek opraven) + nový invariant 19 (brána si musí dovézt závislosti)** | `~\.dsh\skills\orchestra\SKILL.md` | Oprava `conductor/src/index.ts` + nový regresní test `tools\test-zamek-owns.py` (8 kontrol, ověřen mutačním testem) |
>
> Ověřeno: `over-skilly.py` → **9 skillů, 0 chyb**; `kontrola-diakritiky.py`
> → **VŠE OK**; `over-dokumentaci.py` → **63 kontrol, 0 chyb**.
>
> **Co tahle vlna vědomě NEOPRAVILA:** `tools\test-cooldown.py` a
> `tools\test-eskalace.py` **stále lžou zelenou**. Je to nález, ne oprava —
> patří to do rozhodnutí uživatele (analýza L16). Vzor, jak to udělat správně,
> je nově k dispozici: `tools\test-zamek-owns.py`.

---

# Návrh aktualizací dokumentace a skillů (30. 9. 2026) — vlna 5

> **STAV: APLIKOVÁNO** (uživatel povolil zápis 30. 9. 2026 ve 19:1x).
>
> | Co | Kam | Stav |
> |---|---|---|
> | 3 nové sekce (jak agent dostane soubory, opakované pokusy + cooldown + watchdog, nástroje) | `orchestra/README.md` | **zapsáno**, commit `a860830` |
> | Past „podmíněný test, který nikdy nezapne" | `~\.dsh\skills\game-developer\SKILL.md` | **zapsáno** |
> | 6 úprav (cooldown 3 h, invarianty 12–14, nástroje, co orchestra nemá, kam pro detaily) | `~\.dsh\skills\orchestra\SKILL.md` | **zapsáno** |
>
> Ověřeno: `orchestra\tools\over-dokumentaci.py` (8/8 OK — frontmatter,
> diakritika, hledané texty) a `orchestra\tools\over-skilly.py` (8/8 skillů
> se načte). Zapisovalo se Pythonem, protože PowerShell soubory s diakritikou
> jednou poškodil.
>
> Texty níž zůstávají jako záznam, co a proč se měnilo.

---

## 1. `orchestra/README.md` — tři doplněné sekce

Dopsáno za sekci „Modely (řetězec free LLM)". Obsah odpovídá tomu, co je
v README skutečně zapsané (ověřeno `over-dokumentaci.py`):

- **Jak agent dostane soubory** — `--read` vs `--file`, doslovné znění pravidla
  z aideru, `files-to-edit.mjs`, zakládání prázdného souboru, `--map-tokens 0`.
- **Opakované pokusy: každý zkusí jiný model** — naměřená tabulka (#128, #131),
  `inputs.attempt`, cooldown na dvou místech a proč se nesmí filtrovat podle
  `status`, watchdog `ESCALATE_AFTER`.
- **Nástroje pro analýzu (30. 9. 2026)** — 14 nástrojů s popisem.

## 2. Skill `game-developer` — past v §3

Do „Testy jako spustitelná smlouva" přidána podsekce **„Past: podmíněný test,
který NIKDY nezapne, je tiše zelený"** s pěti pravidly a pomocnými funkcemi
`_instantiate` / `_zavri`.

## 3. Skill `orchestra` — šest úprav

| Kde | Změna |
|---|---|
| Architektura | dispatch nese i `grain` a `attempt`; cooldown **3 h** (bylo 6 h) |
| Invarianty | nové **12** (soubor v editovatelném chatu), **13** (cooldown časem, ne statusem), **14** (`MAX_ATTEMPTS` mrtvý kód) |
| Klíčové cesty | odkaz na analytické nástroje |
| Nová sekce | **Analýza a diagnostika** — tabulka nástrojů + tři užitečné postupy |
| Co orchestra NEMÁ | **strop pokusů** — watchdog jen notifikuje |
| Kam pro detaily | README, CONVENTIONS §1g, HANDOFF.md, game-developer |

---

## 4. Revize „co agent umí" (30. 9. 2026, druhá vlna)

Druhá revize vznikla z upozornění uživatele: **agent umí věci, které dokumentace
popírala.** Ověřeno měřením, ne převzato.

| Možnost | Co dokumentace tvrdila | Realita (důkaz) |
|---|---|---|
| **Čtení obrázků** | „Agent obrázky **nevidí** … `read_image` selže" (skilly `imagegen`, `imagegen-local`, popis skillu `vision`) | `read_image` **funguje** — PNG/JPEG/WebP/GIF i bez přípony; ověřeno na 1024×1024 ilustraci a 512×512 Blender renderu |
| **Blender** | jen řádek v tabulce; k tomu živé cesty `gameforge\tools\godot\`, `gameforge\tools\venv\python.exe`, `gameforge\forge.cmd` | **Blender 5.2.1 LTS** headless funguje (`--background --python`); pipeline `tools\blender\build_character.py` je hotová (258 spritů). Cesty `gameforge\...` **neexistují** |

### Zapsané změny

| Soubor | Změna |
|---|---|
| `~\.dsh\skills\vision\SKILL.md` | přepsán úvod na „**Nejdřív zkuste `read_image`**" + tabulka, kdy má skill smysl; `description`/`whenToUse`; sekce o použití v CI; křížová kontrola |
| `~\.dsh\skills\imagegen\SKILL.md` | „Nedívej se na výsledek očima" → „**Podívej se**, `read_image` funguje" (+ že čísla pořád potřebuješ) |
| `~\.dsh\skills\imagegen-local\SKILL.md` | „Ověřování výsledku": místo „agent obrázky nevidí" postup se `read_image` |
| `~\.dsh\skills\game-assets\SKILL.md` | opravená tabulka nástrojů, nová sekce „Blender headless — jak se pouští" (včetně pasti s exit kódem 0), workflow rozšířen na 7 kroků, mrtvé `gameforge\` cesty označeny, **slepé místo brány** |
| `~\.dsh\skills\game-developer\SKILL.md` | nový řádek brány „**vzhled (lidská)**" + „**Brány měří, ale nevidí**"; „(GameForge)" → „(Forge orchestra)" |
| `~\.dsh\skills\orchestra\SKILL.md` | nová sekce „**Assety a „oči" orchestra**" — check-assets vs. vision.mjs, co je v CI a co ne, Blender na uzlu, **slepá místa brány** (animace, hudba, `kind`) |
| `MOZNOSTI-AGENTA.md` (workspace) | **NOVÝ** — zdroj pravdy o schopnostech, s důkazy, ověřenými cestami a známými hranicemi |
| `FORGE-ORCHESTRA-MOZNOSTI.md` (workspace) | **NOVÝ** — jak to zapojit do orchestra (4 návrhy, co nejde, 6 nálezů, pořadí) |
| `orchestra\tools\kontaktni-arch.py` | **NOVÝ NÁSTROJ** — kontaktní arch spritů pro `read_image` (ověřeno na 256 spritech) |
| `orchestra\tools\over-dokumentaci.py` | **ROZŠÍŘEN** na 30 kontrol — hlídá i to, že skilly netvrdí staré nepravdy |

### Nález, který vznikl až měřením (a je nejcennější)

Při ověřování tvrzení „brána nepozná, že postavě chybí obličej" jsem zjistil
**dvě věci, které to tvrzení vyvracejí** — a jednu, která ho nahrazuje:

1. **Postava z primitiv je ZÁMĚR, ne vada.** `games/uo-shadows/assets/spec.json`,
   `_stav`: „MILNÍK 1 (cesta A) **SCHVÁLEN 5/5**: lidská postava z primitiv + rig
   14 kostí, chůze 8 framů přes 2-kostní IK…" V UO stylu se postava skládá
   z vrstev (`slot_poradi`: body, legs, torso, cloak, **head**…) a obličej přijde
   jako vrstva `head`. Skilly to teď říkají správně.
2. **`check-assets.py` na `uo-shadows` prochází** — „Vše v pořádku: assety
   odpovídají specu" (player 38×95 px, 1103 barev, 0 děr, okraj 0 %). Brána je
   tedy spokojená a o obsahu neříká nic — což je přesně pointa.
3. **Skutečná vada je jinde: brána animace se NIKDY neuplatní.** Hledá
   `assets/sprites/walk_*.png` — tam je **0** takových souborů; chůze je
   rozložená po vrstvách v `tools/blender/sprites/body_d0_f*.png`. Brána to
   poctivě ohlásí jako poznámku, ale kontrola `min_silhouette_iou: 0.80` ze
   specu se neuplatní, i když spec deklaruje `framy: 8`. **Změřeno ručně:**
   IoU 0.834–0.908, posun těžiště 0.46–0.99 px (limit 3.0) → animace je
   v pořádku; jde o **slepé místo brány**, ne o vadu hry. Kdyby se chůze
   rozbila, CI to nepozná.

**Poučení do skillů:** „brána nic nehlásí" může znamenat „brána se na to
nedívá". Zelená od brány není důkaz, že kontrola proběhla.

**Proč jsou kontroly v `over-dokumentaci.py` důležité:** dokumentace, která
popírá vlastní nástroje, se vrátí — někdo (i agent) ji napíše znovu, protože
„to tak bylo". Kontrola na konkrétní věty je pojistka **proti regresi znalosti**:
kdyby někdo zmínku o `read_image` ze skillu `vision` zase odstranil, skript
spadne.

### Past při spouštění ověřovacích skriptů

Na téhle stanici padají na **vlastním výstupu** (`UnicodeEncodeError: 'charmap'
codec can't encode character`) — konzole je cp1252 a skripty tisknou „řádků".
Bez zásahu do skriptu:

```powershell
$env:PYTHONIOENCODING='utf-8'
python orchestra\tools\over-skilly.py       # 8 skillů, 0 chyb
python orchestra\tools\over-dokumentaci.py  # 27 kontrol, 0 chyb
```

### Co zůstává na rozhodnutí

Změny, které by potřebovaly zásah do kódu orchestra a nasazení — detail
v `FORGE-ORCHESTRA-MOZNOSTI.md`:

1. Zapnout uzel `pc-domaci` (bez něj jsou Blender i lokální generátor mimo hru).
2. Zapojit `.forge/vision.mjs` do `ci.yml` — nástroj existuje a **nikdo ho nevolá**.
3. Krok `blender:` v `worker.mjs` (dnes jen `shell:`, který se vždy ptá y/N).
4. Mrtvý default `FORGE_CMD` v `worker.mjs` (míří na smazaný `forge.cmd`).
5. `kind` nic neřídí — `agent.yml` ho použije jen v šabloně PR komentáře.
6. Smí se assety slučovat samy, bez vizuální kontroly?

**Poučení z téhle vlny:** skill, který leží mimo workspace, se nedá
aktualizovat „až někdy". Buď je na něj oprávnění, nebo znalost zestárne a začne
lhát — přesně to se stalo u `vision`, který půl dne tvrdil, že agent nevidí,
a přitom viděl.

---

## 5. Vision a schéma: schváleno, část hotová (30. 9. 2026, třetí vlna)

Uživatel schválil `PLAN-VISION-ORCHESTRA.md` a rozhodl klíčovou věc:
**schéma je specifické pro každou hru** — ne každá bude izometrická. Autorita
je `assets/spec.json` té které hry, nástroje v něm nesmí mít nic zadrátované.

### Zapsané změny

| Soubor | Změna |
|---|---|
| `~\.dsh\skills\orchestra\SKILL.md` | sekce „Assety a „oči" orchestra" rozšířena o `check-schema.py`, `vision-profile.json`, `vision.test.mjs`, **rozdělení tvrdá vs. poradní kontrola** a pořadí kroků v CI |
| `MOZNOSTI-AGENTA.md` | inventura nástrojů pro vision (`orchestra\tools\inventura-vize.py`) |
| `FORGE-ORCHESTRA-MOZNOSTI.md` | nález 7 (rozpor schématu) + stav řešení |
| `PLAN-VISION-ORCHESTRA.md` | nová kap. 13 „Co je HOTOVÉ", přepsaná kap. 4.2b (per-game), rozhodnutí |
| `orchestra\tools\kontrola-schematu.py` | **NOVÝ** — kontrola schématu (6 rozporů na `uo-shadows`) |
| `orchestra\tools\inventura-vize.py` | **NOVÝ** — co je na stanici pro práci s obrázkem |
| `orchestra\tools\test-ci-workflow.mjs` | **NOVÝ** — 36 testů CI struktury a pořadí kroků |
| `orchestra\tools\oprav-check-schema.py` | **NOVÝ** — jednorázová oprava kopií (aby nevznikl drift) |

### Chyby, které odhalily až testy (a jsou poučením)

1. **Deadlock.** Mock API ve stejném procesu + `execFileSync` = rodič blokuje
   event loop, dítě čeká na rodiče. Test visel 3× a vypadal jako pomalý.
   → asynchronní `execFile`.
2. **`fetch` bez timeoutu** — v CI by spálil celý krok. → 60s timeout.
3. **BOM v JSON.** PowerShell píše UTF-8 BOM, `JSON.parse` na něm spadne.
   Stejná past už potkala `orchestra/.env`. → `utf-8-sig`.
4. **Chybný test, ne chybný nástroj.** Test čekal `5× floor / 3× wall`,
   ale `'0011' + '1111'` je 6 a 2. Než se začne „opravovat" nástroj, musí se
   rozlišit, co je špatně — to je celý smysl toho, že testy píše někdo jiný
   než ten, kdo měří.

---

## 6. Baseline, LGTM cache a dvě mezery `phash` (30. 9. 2026, čtvrtá vlna)

Doplněny fáze **F0b** a **F2** z `PLAN-VISION-ORCHESTRA.md`.

### Zapsané změny

| Soubor | Změna |
|---|---|
| `~\.dsh\skills\orchestra\SKILL.md` | tabulka „Assety a „oči" orchestra" má **`baseline.py`** a **dvě mezery `phash`**; testů vision 28 → **34** |
| `orchestra\repo\.forge\baseline.py` | **NOVÝ** — schvalování (LGTM), cache, historie verdiktů, 24 offline testů |
| `orchestra\repo\.forge\vision.mjs` | **cache** (schválené se neposílá), `--force`, zaznamenání důvodu u selhání interpretu, `kontroly` ve výstupu |
| `orchestra\repo\.forge\node\vision.test.mjs` | +6 testů cache (doklad **0 volání modelu**) |
| `orchestra\tools\validate-all.mjs` | sekce K rozšířena o baseline |
| `PLAN-VISION-ORCHESTRA.md` | kap. 13: F0b a F2 hotové; tabulka dvou mezer `phash` |

### Dvě mezery `phash` — nejcennější nález

`phash` je DCT přes **odstupňovou škálu**, takže má dvě tiché chyby. Obě by
způsobily, že **změněný asset projde jako nezměněný** — tedy přesně to, čemu
má baseline bránit:

| Mezera | Naměřeno | Řešení |
|---|---|---|
| **Slepý na barvu** | červená i modrá se stejnými bloky → `f8f8f8f0f0070707` | **barevný podpis** (průměrné RGB 4×4); cache chce shodu obojího |
| **Degeneruje u jednolitého** | plná červená i modrá → `8000000000000000` | `phash()` vrátí `None` → porovná se **přesný `sha256`** |

Přebarvení (týmové barvy, jiný materiál) je v herní grafice běžná věc, takže
mezera č. 1 by se v provozu skoro jistě projevila.

**Poučení:** hash není důkaz, že se nic nezměnilo. Je to nástroj, jehož meze se
musí změřit — a tichá chyba je horší než žádná cache.

### Pět chyb, které odhalily až testy (všechny v testech)

1. Assertion hledal `_` kdekoliv v cestě → selhával na `body_d0_f0.png`, který
   podtržítka legitimně má (oddělovače směrů/framů).
2. Test „přeuložené PNG zůstane v cache" použil soubor, který předchozí test
   záměrně přebarvil.
3. CLI test parsoval jen poslední řádek víceřádkového JSONu.
4. Test cache neměl v dočasné hře `baseline.py` ani `assets/sprites`.
5. `python3` na Windows je stub Microsoft Store a chyba se spolkla bez důvodu →
   `vCache` teď důvod každého neúspěchu zaznamená.

**Vzor, který stojí za zapamatování:** čtyři z pěti chyb vznikly tím, že test
tvrdil něco o **prostředí** (kde soubor leží, co znamená jméno), ne o logice.
Než se „opraví nástroj", musí se rozlišit, jestli je špatně nástroj, nebo
předpoklad testu.

---

## 7. Ověření poznámek a pátá vlna (1. 10. 2026)

Tahle vlna nevznikla z návrhu, ale z **ověřování návrhu**: uživatel dal nové
instanci blok textu z předchozí session a chtěl ověřit, že poznámky platí.
Většina z nich **platila a byla už zapsaná** — a při ověřování se našlo, že
jedna zavedená brána **přestala měřit**. To je ta nejcennější část.

### Co se ověřilo měřením (a co z toho bylo už hotové)

| Tvrzení z poznámek | Výsledek |
|---|---|
| `read_image` funguje | **OVĚŘENO** — přečten `assets/tiles/tileset.png` (576×48, 6 izometrických kosočtverců) |
| Blender 5.2.1 LTS headless | **OVĚŘENO** — `--version` i `BLENDER_OK 5.2.1 LTS` |
| `forge-quest` je živá hra s Pages | **OVĚŘENO** — GitHub API: `forge-quest` i `uo-shadows` Pages ANO, `uo-sandbox` 404; `…/uo-shadows/` vrací HTTP 200 |
| orchestra skill: sekce „Sousední hry jsou ŽIVÉ" | **už zapsané** |
| `MOZNOSTI-AGENTA.md`: „Co agent neumí" + hranice | **už zapsané** |
| `FORGE-ORCHESTRA-MOZNOSTI.md`: nálezy 8–10 | **už zapsané** (jen §10 měl zastaralý popisek `vision.mjs` = „nezapojené") |
| `PLAN-VISION-ORCHESTRA.md`: kap. 13 vč. migrace a `phash` | **už zapsané** (kap. 13 měla 28 testů vision místo 34 — opraveno) |
| `SKILLY-AKTUALIZACE.md`: čtvrtá vlna | **už zapsané** (kap. 6) |
| `vision` skill: režimy, cache, self-consistency | **NEBYLO** — doplněno (0 výskytů) |
| `game-developer`: řádek „schéma", „brána neproběhne", vizuální změna | **NEBYLO** — doplněno |
| `game-assets`: past „hash nestačí", past metrika, izodlaždice | **NEBYLO** — doplněno |
| `AGENTS.md` | **NEBYLO** — založeno |
| nový skill `dsh-prostredi` | **NEBYLO** — založeno |

### NÁLEZ: brána, která po migraci přestala měřit

`check-schema.py` (tvrdá brána v CI, F-1) hledal výchozí buňku v `level.gd`
vzorcem `var cell := 16`. Migrace na izometrii z toho udělala
`const CELL_W_DEFAULT := 96` + `CELL_H_DEFAULT := 48`. Regexy nenašly **nic**,
cyklus proběhl nad **prázdným seznamem** — a brána hlásila „Schéma je
v souladu". Prozrazoval to jediný řádek:

```
level.gd: výchozí cell=[], fallback=[]
```

`[]` přitom vypadá jako **naměřená nula**, tedy jako úspěch.

**Oprava (`games/uo-shadows/.forge/check-schema.py` + stejná kopie v šabloně):**

- měří **oba tvary** deklarace (starý `var cell := 16` i dnešní
  `const CELL_W_DEFAULT := 96`), osu určuje podle **jména**, ne křehkým
  lookaheadem;
- když buňku přečíst nelze, hlásí **vadu** („kontrola NEPROBĚHLA" není totéž
  jako „je to v pořádku"); když v kódu není fallback, je to jen poznámka;
- rozlišuje **šířku a výšku** (u izometrie 96×48 se liší);
- pojmenovává **mrtvé větve** — po přesunu `world.gd` do `_retired/` se
  kontroly na něj už nikdy nespustí;
- výpis prázdna je `nezměřeno (v kódu není)`, nikdy `[]`.

**Pojistka:** `orchestra/tools/test-check-schema.py` — **17 offline testů** se
známým správným i chybným repem, zapojeno do `validate-all.mjs`.

### Čtyři chyby, které odhalily až ty testy (všechny v mém vlastním regexu)

1. **Case sensitivity.** `\w*cell\w*` nechytilo `CELL_W_DEFAULT` → kontrola
   zase neměřila. Řešení: `re.IGNORECASE`.
2. **Záměna os.** `cell\w*` chytilo i `cell_h` → výška se hlásila jako šířka
   (96×48 se četlo jako 48×48). Řešení: osa podle **jména deklarace**.
3. **První vs. poslední deklarace.** Bral se první výskyt, ale v GDScriptu
   platí pozdější → kdyby soubor nesl historii i dnešní stav, hlásila by
   kontrola vadu i po opravě (falešný poplach).
4. **`\b` po podtržítku neplatí.** Podtržítko je „word char", takže `(?!_h\b)`
   propustilo `_H`. Řešení: `(?!\w)`, a ještě lépe se lookaheadu úplně vyhnout.

**A jedna skutečná vada projektu:** test odhalil **drift mezi šablonou
`orchestra/repo/` a herním repem** — opravil jsem jednu kopii a druhá zůstala
rozbitá. Test proto hlídá i **shodný hash** obou kopií.

### Prostředí: pasti, které vypadají jako chyba logiky

Vznikly **čtyři** případy v jedné session, proto na ně vznikl samostatný skill
`~\.dsh\skills\dsh-prostredi\SKILL.md`:

| Past | Co udělá |
|---|---|
| `Select-String -SimpleMatch` | tiše přeskočí soubory → falešný negativ |
| chybějící UTF-8 BOM v `.ps1` | parser hlásí `Missing closing '}'` |
| zdvojené konce řádků (dvoje `\r`) | parser hlásí chybu na řádku, který v souboru není |
| konzole `cp1252` | ověřovací skripty padají na **vlastním výstupu** (`UnicodeEncodeError`) |
| **sandbox `workspace-write`** (nové, naměřeno dnes) | podprocesy s piped stdio → `EPERM`; zápis do přesměrovaného tempu → `PermissionError WinError 5`. `baseline.py testy` a `vision.test.mjs` tím spadnou, ale **nejsou rozbité** |
| Godot bez `--user-data-dir` | `Could not open 'user://'` |

### Zapsané změny v této vlně

| Soubor | Změna |
|---|---|
| `~\.dsh\skills\dsh-prostredi\SKILL.md` | **NOVÝ SKILL** — pasti prostředí + kontrolní seznam při podivné chybě |
| `~\.dsh\skills\game-developer\SKILL.md` | řádek brány „**schéma** (tvrdá)", podsekce „**Brána, která neproběhne, není brána**" (5 pravidel + povinnost offline testu), „**Vizuální změna se neověřuje testy**", „statická kontrola čte kód, ne komentáře" |
| `~\.dsh\skills\game-assets\SKILL.md` | „**hash není důkaz**" (dvě mezery `phash`), „**metrika, která měří něco jiného**" (4 verze metriky švu), „**Izometrické dlaždice — jak se generují**" |
| `~\.dsh\skills\vision\SKILL.md` | režimy `presence`/`diff`, **self-consistency** (neshoda = signál nejistoty, ne chyba), **cache + `--force`**, pravidlo „neposílat hodnocení, posílat očekávání" (a počítat ho z dat hry) |
| `~\.dsh\skills\orchestra\SKILL.md` | do sekce o „očích" přidán **celý příběh brány, která přestala měřit**, včetně odkazů na test a na to, že oprava patří do commitu |
| `AGENTS.md` (workspace) | **NOVÝ** — trvalá pravidla napříč session (ověřování, prostředí, dokumentace, co nikdy) |
| `README.md` (workspace) | odkazy na `AGENTS.md` a na to, že `forge-quest` je **živá** hra |
| `FORGE-ORCHESTRA-MOZNOSTI.md` | **nález 11** (brána přestala měřit), opravený zastaralý popisek `vision.mjs` a doplněné nástroje |
| `PLAN-VISION-ORCHESTRA.md` | **past 4** v migraci, F-1 s upozorněním, testy vision 28 → **34** |
| `games/uo-shadows/.forge/check-schema.py` + `orchestra/repo/.forge/check-schema.py` | **OPRAVA BRÁNY** (shodný hash obou kopií) |
| `orchestra/tools/test-check-schema.py` | **NOVÝ NÁSTROJ** — 17 offline testů brány |
| `orchestra/tools/validate-all.mjs` | sekce K volá nový test |

**Poučení z téhle vlny:** poznámky z předchozí session byly **z 90 % správné**
— a přesto se vyplatilo je ověřovat, protože právě při ověřování se ukázalo,
že jedna zavedená brána **nic neměří**. Kdyby se poznámky jen zapsaly, zapsala
by se i důvěra v bránu, která lže.

---

## 8. Doplnění po pushi: co session použila, ale nezapsala (1. 10. 2026)

Po pushi a při psaní zadání pro analýzu architektury se ukázalo, že session
použila **čtyři postupy, které nikde zapsané nebyly**. Doplněny tam, kde je
příští instance najde.

| Co se používalo | Kam je to zapsané |
|---|---|
| **Ověření nasazení na Pages** — HTTP 200 není důkaz; `last-modified` z `index.png` přes Node `HEAD` je | `AGENTS.md` (nová sekce) + `~\.dsh\skills\orchestra\SKILL.md` |
| **Nástroj zapíše do tempu a NIC neřekne** (Godot `--write-movie` doběhl úspěšně, framy nevznikly) | `AGENTS.md` + `~\.dsh\skills\dsh-prostredi\SKILL.md` |
| **„Není to vada" je taky výsledek, ale musí být doložený** (`--resolution 480x270` vs. 960×540) | `AGENTS.md` |
| **Přepis `HANDOFF.md` nesmí ztratit otevřené body** | `AGENTS.md` |
| **Kdy práce patří do nové session** (nezávislost pohledu, ne tokeny) + jak psát zadání | `AGENTS.md` (nová sekce) |

**Proč je to samostatná sekce a ne součást sedmé vlny:** sedmá vlna byla o tom,
co se **ověřilo a opravilo**. Tahle je o tom, co session **použila, ale
nezapsala** — a to je jiný druh chyby: znalost zůstala jen v session a při
předání by zmizela. Proto se kontrolní seznam `over-dokumentaci.py` rozšířil
z **57 na 63 kontrol** — nové věty se nedají tiše smazat.

**Meta-poučení:** hodnota nevznikla jen psaním textů, ale **psaním zadání pro
novou session**. Formulovat „na co se zeptat" donutilo dohledat fakta, která
v session nikdo neměl — například že `agent.yml` driftuje a že šablona
orchestra je v gitu **neúplná** (nové brány jsou netrackované). **Psaní zadání
je způsob, jak najít díry ve vlastním díle.**

**A jedno pravidlo o „shodě", které stojí za zapamatování:** šest souborů
(`check-schema.py`, `baseline.py`, `vision.mjs`, `verify-level-render.py`,
`vision-profile.json`, `check-assets.py`) je v šabloně i ve hře **shodných** —
ale proto, že je někdo dnes ručně zkopíroval, **ne proto, že by to někdo
vynucoval**. Driftová kontrola je nezná. **Shoda, kterou nic nehlídá, je náhoda
s dobrým jménem.**

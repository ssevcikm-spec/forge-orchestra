# HANDOFF — VLASTNÍ OMYLY (bloky `8a`–`8zz`), přesunuto 7. 10. 2026

**Co tenhle soubor JE:** **archiv** — tabulky omylů všech session, které do
7. 10. 2026 bydlely v `HANDOFF.md` §8. Je to **záznam**: jen se doplňuje,
nepřepisuje.

**Proč se přesunul:** `HANDOFF.md` měl **674 723 znaků**, z toho **93,8 %
historie**. Stav se v něm kvůli tomu hledal špatně. Přesunuto **bajt na bajt** —
nic se nezmazalo; ověřuje to `_analyza\handoff-kontrola-uplnost.py` (hledá
i tady) a `_analyza\kronika-kontrola.py` (počty omylů proti kronice §3 čte
odtud).

**Proč zrovna sem a ne do `KRONIKA-PROJEKTU.md`:** kronika §3 je **jediné místo,
kde je vidět trend** a `kronika-kontrola.py` ji **porovnává s tabulkami omylů**.
Kdyby tabulky ležely v kronice, brána by porovnávala soubor **sám se sebou** —
což je přesně ta vada, kterou `DSH_HOME\AGENTS.md` popisuje („měřidlo měřilo
zdroj a porovnávalo ho sám se sebou"). Archiv je proto **jiný soubor**.

---

## 8. Vlastní omyly (všech session — tabulka je společná)

> **Autorství:** `7cd67c66` = analýza (S31–S37) · `7db45275` = jazyk ·
> **`eb127abd` = tahle session (provedení A1–A4, Z1–Z8)**.

| # | Kdo | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|---|
| 1 | `7cd67c66` | `sim.mining` má `size_lines` → „vyvracím 1. kolo" | **Nemá** (patří `sim.crafting`); hypotéza 1. kola **platí pro všechny tři** | Přehlédl jsem řádek v tabulce, kterou jsem si sám vypsal |
| 2 | `7cd67c66` | lint o chybějícím `size_lines` **mlčí** | **Varuje** (7× `[5]`), ale `exit 0` a text **zastaralý** | Přečetl jsem jen „vady 1–4: žádné" |
| 3 | `7cd67c66` | Mutační test mé kontroly umí spadnout | **První verze byla slepá** — mutace přes `-replace` s em-dash se **tiše neprovedla** | Diakritika v konzoli |
| 4 | `7db45275` | Druhá session převzala mou §10 „beze změny" | **Převzala jen část** — §8.2 (mandát) jí chybělo | Souběh dvou session nad jedním `HANDOFF.md` |
| **5** | **`eb127abd`** | **„Prompt k hluboké kontrole nedorazil"** | **Byl v repu a byl splněný (9/9)** | **Převzal jsem tvrzení z `HANDOFF.md` §8.4, aniž jsem soubor otevřel.** Označil jsem za chybějící něco, co jsem nezkontroloval |
| **6** | **`eb127abd`** | Cache `origin/main` „drží výsledek na dobu jednoho tiku" | **Modulová proměnná bez TTL** žije, dokud žije izolát — **libovolně dlouho** | Napsal jsem komentář, který tvrdil chování, a **neověřil ho**. Našel to až druhý pohled na vlastní diff, **ne test** |
| **7** | **`eb127abd`** | Kontrola A1 je hotová | **Hlásila falešný poplach na správném kódu** — `if (ok) {` je v souboru 2× a ta první je správná | Test hledal vzorec **bez kontextu**; opraveno vázáním na `UPDATE tasks status='done'` |
| **8** | **`eb127abd`** | Inventář jazyka je měření | **Je to meziprodukt, který zestaral** → hlásil **7 vad, které už byly opravené** | Nástroj si ho generuje jen když **chybí** (nález **N1**) |
| **9** | **`eb127abd`** | Můj skript na zastaralost analýzy měří | **Měl obrácenou podmínku** → hlásil „0 zastaralých" u kódu, který jsem **sám změnil** | Odhalilo se **jen tím, že jsem znal správný výsledek** — „známý chybný případ" z `AGENTS.md` |
| **10** | **`eb127abd`** | Diakritika brána nad novým dokumentem nic nehlásí | **Skutečný výsledek byl `exit=-1`** (artefakt PowerShell pipeline), správně **`exit=1` + jméno souboru** | Měřil jsem přes `Select-String` v pipeline; **musel jsem to změřit znovu pořádně** |
| **11** | **`eb127abd`** | `split("\n")` mi dá počet řádků blobu | **Dal 183 u souboru, který má 182** (končí newline → prázdný prvek na konci). **`AGENTS.md` měl pravdu, skript ne** | Je to **tatáž past**, před kterou `AGENTS.md` varuje u `Measure-Object -Line` (166 vs 182) — a **spadl jsem do ní znovu**, vlastním nástrojem, který měl `AGENTS.md` kontrolovat |
| **12** | **`eb127abd`** | Můj nástroj `ag-over-cisla.py` kontroluje čísla v `AGENTS.md` | **Tvrzená čísla měl NAPSANÁ NAPEVNO** → měřil zdroj a porovnával ho **sám se sebou**; vrácená vada v dokumentu (39 → 32) mu **prošla** (`exit 0`) | **Brána zelená nad dokumentem, který nikdy neotevřela (S27) — v nástroji, který měl S27 hlídat.** Odhalil to až **mutační test** |
| **13** | **`eb127abd`** | `AGENTS.md` tvrdí 32 sloupců → našel jsem chybu v autoritě | **Bylo to 39 a `AGENTS.md` jsem opravil — správně.** Ale **původní závěr „32" jsem nejdřív převzal jako fakt** a označil ho za chybu **až po přeměření**; do té doby to byl jen dojem z jednoho grepu | Postup byl správný, **ale jen náhodou** — kdybych měřil špatně (jako v omylu 11), „opravil" bych správný dokument (přesně ta past, před kterou varuje `AGENTS.md`) |

**Vzor, který je vidět napříč všemi třinácti:** každý omyl vypadal jako
**nález o systému** („chybí zadání", „kód je slepý", „analýza je v pořádku")
a **většina z nich byla vada měření.** A **devět ze třinácti** je z téhle session —
což je přesně to, co `AGENTS.md` předpovídá: *„počítej, že i tvoje první číslo
bude někde mimo."*

---

### 8b. Omyly ověřovací session (2. 10. 2026, podle `PROMPT-NOVA-SESSION.md`)

> **Devět z deseti bylo vadou MĚŘENÍ, ne nálezem o systému** — a **šest z nich
> vzniklo v mnou napsaném testovacím skriptu**. Týž vzor, jen o kolo dál.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **14** | V workspace je git repo → `git status` ochrání dokumenty | **Není.** `fatal: not a git repository`; pod gitem je jen `orchestra\`. `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` **není verzovaný** | Zjistil jsem to **těsně před** spuštěním `hl2-mutace-kontrola.py`, který ten dokument přepisuje na místo a bez zálohy. Kdyby spadl uprostřed, **není ho odkud vzít** |
| **15** | „Nepodařilo se mutovat" = „brána je slepá" | **Dvě různé věci.** Dvakrát se mutace neprovedla a harness to **rovným dílem** nahlásil jako slepou bránu | Slil jsem „vada testovacího skriptu" a „vada brány" do jednoho výsledku → **falešný nález o cizím kódu** |
| **16** | `re.compile("if (ok && merged) {")` hledá ten řetězec | **Hledá `if ok && merged {`** — závorky jsou **skupina**, ne literál. Vzor hlásil „0× v souboru", **přitom tam byl** | Neescapoval jsem vzory ve svých harnessech, **ačkoli skripty projektu to dělají správně**. Stálo to ~8 diagnostických běhů a málem vyrobilo „nález", že se soubory nevracejí |
| **17** | `re.findall` vrací počet shod | **Vrací capture groupy.** U vzoru se skupinou vrátil `['ok && merged']` → `len()` **není** počet shod | Počítal jsem shody funkcí, která vrací obsah. Správně `finditer` |
| **18** | Mutace `filesInOriginMain` → `…XX` změní jméno | **Ne.** `filesInOriginMainXX` **obsahuje** `filesInOriginMain` → skript hledající podřetězec rozdíl nevidí; **já** jsem to nahlásil jako „skript nereaguje" | Nový název musí být **úplně jiný** (`loadMainTree`) — jinak testuješ něco jiného, než si myslíš |
| **19** | Harness na `n8-*` mám hotový napoprvé | **Tři kola oprav:** (a) `spust()` vracel 2 hodnoty, rozbaloval jsem 3; (b) mutace (a2) měnila **totéž** co mutace 1 → **nebyl to nezávislý test**; (c) vzor `exit 1` s 10 mezerami je v souboru **2×** | Každou vadu odhalil **až běh**, ne čtení |
| **20** | Mutace `AGENTS.md` přes `python -c "…'39 sloupců'…"` proběhne | **Neproběhla** — PowerShell rozbil f-string (`SyntaxError`), soubor zůstal netknutý a brána vrátila `exit 0`. **Málem jsem to zapsal jako „brána je slepá"** | Tatáž past, před kterou varuje skill `overovani` §7.9: **mutace, která se tiše neprovede, tvrdí totéž co mutace, která projde.** Odhalilo to jen porovnání hashe před/po |
| **21** | „35 souborů" v bráně diakritiky = 35 dokumentů | **Dva z těch 35 jsou vnořené soubory projektu** (`.forge\check-schema.py`, `.forge\vision-profile.json`) → **33 dokumentů + 2 soubory projektu** | Počet **řádků výstupu** jsem použil jako počet **dokumentů** — dva čítače téhož jména |
| **22** | `Get-Content` přečte UTF-8 dokument správně | **Ne** — načetl ho jako **cp1252**, rozbil diakritiku, vzor nenašel a **tabulka mi vyšla jako 0 řádků** | Vypadalo to jako nález („dokument má prázdnou tabulku"); správně je **16 datových řádků**. Číst přes `[System.IO.File]::ReadAllBytes` + UTF-8 |
| **23** | „9 z 9 bodů" znamená, že analýza je v pořádku | **Neznamená.** Brána projde nad **12,5 % dokumentu** s `\| **Cena** \| X \|` místo obsahu | Nebyl to omyl ve **výpočtu**, ale v tom, **co to číslo tvrdí** — a to je horší druh, protože se neprojeví jako chyba |

**Vzor, který je z těch deseti vidět:** šest (**16, 17, 18, 19, 20, 21**) bylo
v **mém vlastním měřidle** — a **každé vypadalo jako nález o cizím kódu**
(„brána je slepá", „skript nereaguje", „dokument má prázdnou tabulku").
`PROMPT-NOVA-SESSION.md` předpovídá, že *„většina z nich bude vada měření"* —
**potvrdilo se to i na mě.**

---

### 8c. Omyly session 2. 10. 2026 (11:3x–12:0x UTC) — push, granule, N1/N3

> **Tři z pěti vznikly ve MĚŘIDLE a jeden z nich málem vedl ke zbytečnému
> zásahu do herního repa.** Týž vzor, jen o kolo dál.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **29** | **„V herním repu chybí 2 brány, které šablona má"** — a nabídl jsem to uživateli jako možnost k rozhodnutí | **Hra je MÁ.** Kontrolu stínění `class_name` má **uvnitř** kroku parsování (`agent.yml:344–373`) a **navíc** tip na konstanty Godotu 3 (`:337–339`). Drift hlásí „jen v šabloně" proto, že porovnává **jména kroků** — a hra má kroky sloučené a pojmenované jinak | **Přečetl jsem výstup měřidla (drift) jako popis skutečnosti**, místo abych otevřel soubor. Přesně to, před čím varuje `AGENTS.md` („převezmeš tvrzení, aniž soubor otevřeš") — a stalo se to **znovu**, po omylu č. 5 |
| **30** | Oprava driftu „porovnávat `env` po krocích podle pozice" je správná | **Byla slepá na posun:** kopie mají **různý počet kroků** (šablona 21, hra 20), takže indexy nesedí a nástroj hlásil **4 falešné rozdíly** u kroků, které s věcí nesouvisí (`Report při selhání`, `Ulož patch a log`, …) | Odhalil to až **mutační test** — bez něj bych odevzdal měřidlo, které sice chytí hledanou vadu, ale utopí ji v šumu. Opraveno na porovnání **podle klíče**, ne podle pozice |
| **31** | Když jsem viděl, že nový nástroj vrací 4 `CHYBA`, byl jsem hotový s výčtem | **Nebyl jsem:** musel jsem rozlišit **příčinu** — tři selhání jsou **pre-existující** (dokázáno spuštěním téhož nástroje nad čistým `be41964` v `git worktree`), jedno je **sandbox** (`PermissionError WinError 5` na přesměrovaném tempu), a `test-cooldown.py` je **červený správně** (měří vadu S12) | Málem jsem je shrnul jako „brány neprošly" — což by bylo tvrzení o cizím kódu, které jsem neměl čím doložit |
| **32** | „Přesun `FORGE_ATTEMPT`" je jednoduchý `edit` | **Čtyři editace za sebou nic neopravily** — tool hlásil úspěch, ale výsledek byl pořád rozbitý (překlep „nesp uštěna", závorka na špatném místě). Opravil to až **skript, který po zápisu ověří syntaxi** (`node --check`) | **Tatáž past jako u V1** („čtyřikrát jsem upravoval kontrolu, kterou jsem sám přidal") — a poučení je stejné: **ověřuj VÝSTUP, ne návratovou hodnotu nástroje** |
| **33** | Když mi podagent poslal „C2 HOTOVO", mohl jsem se zeptat, co našel | **Musel jsem si to ověřit sám** — a jeho klíčový nález (`player.gd:40` obsahuje řetězec, který test zakazuje, takže po dodání `move()` test spadne) jsem **nezávisle potvrdil mutací** (59/0 → 60/1) | Není to omyl, je to **nález**: dva nezávislé pohledy (čtení kódu vs. spuštění) daly totéž. Kdyby se rozešly, byl by to výsledek — ne chyba |

**Vzor z těch pěti:** **čtyři z pěti** byly v **měřidle nebo v jeho výstupu** —
a **dva vypadaly jako nález o cizím kódu** („chybí brány" → nechybí; „brány
neprošly" → prošly jindy a jinde). A ten první **málem vedl k zápisu do herního
repa podle nesprávného závěru** — zachránilo to jen to, že jsem se zeptal
a uživatel zvolil širší variantu, u které se vada **musela** ověřovat čtením
souboru.

---

### 8d. Omyly PLÁNOVACÍ session 2. 10. 2026 (10:1x–10:3x UTC) — ověření 11 tvrzení

> **Dva z pěti vypadaly jako nález o cizím kódu a jeden málem odešel jako
> „červená brána".** Týž vzor, jen o kolo dál — a znovu to, co předpovídá
> `AGENTS.md`: *„počítej, že i tvoje první číslo bude někde mimo."*

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **34** | **„Brána `check-schema.py` je červená i v šabloně"** (`exit 1`, „chybí `assets/spec.json`") | **Není to vada.** `validate-all.mjs:194` ji pouští **nad hrou** (`games/uo-shadows`), ne nad šablonou — ta žádné assety nemá a mít nemá. Nad hrou vychází `exit 0` | Spustil jsem nástroj s vlastním argumentem, aniž jsem se podíval, **jak ho pouští ten, kdo ho zná**. Falešný nález o cizím kódu — a odhalilo to až dohledání volání, ne test |
| **35** | Můj mutační skript `p7-mutace-pojistky.py` je hotový | **Dvakrát spadl na `sha(<bytes>)`** — vypisoval `AttributeError` **po** provedené mutaci. Kdybych věřil návratové hodnotě, vypadalo by to jako „mutace se nepovedla" | Chyba byla v **mém** nástroji, ne v měřeném. Zachytil to `assert`, že se text skutečně změnil (past z `overovani` §7.9) — bez něj bych měl „nález o bráně", který je o mně |
| **36** | Když brána padá i s `TMP` ve workspace, blokuje sandbox i workspace | **Neblokuje.** Skutečná příčina je `os.mkdir(p, 0o700)` (což `tempfile.mkdtemp()` používá) → adresář, do kterého nejde zapsat ani ho smazat. Prokázalo to až **oddělené** měření `0700` vs. výchozích `0777` | Měřil jsem **dvě věci naráz** (přesměrovaný temp + chování nástroje) a první vysvětlení jsem málem zapsal jako nález o prostředí |
| **37** | Pro sondy stačí `_analyza\tmp-sandbox` | **Zůstaly v něm 3 adresáře, které NEJDE smazat** (`c700`, `schema-test-*`, `probe2-*`) — `Remove-Item`, `cmd /c rd`, `takeown` i `icacls` hlásí „Access is denied" | Sondoval jsem past **tím, že jsem ji vyrobil** — a to, že po sobě nezůstane uklizeno, je její součást. Zapsáno jako nález (P3) i s tím, že po sobě zanechává odpad |
| **38** | „9 výskytů `.has(`" ze zadání je měření | **Je jich 10** (`scripts/*.gd`) a **18** v celém herním repu. Zadání vypisuje 2 vady + 6 Dictionary/Array + 2 komentáře = **10**, ale součet uvádí **9** | Sečetl jsem položky, které zadání samo vyjmenovalo — rozpor je **uvnitř zadání**, ne v kódu. (Týž postup jako u „32 sloupců": číslo bez postupu se nedá ověřit.) |
| **39** | Do nového zadání můžu napsat, **jak vypadají znaky rozbitého kódování** (jako ukázku vzoru, kterým jsem dokument kontroloval) | **Brána diakritiky to ohlásila jako vadu dokumentu** — `NALEZENY CHYBY (1)`, přesně podle `AGENTS.md` („ukázku rozbitého kódování popisuj **slovem**"). Opraveno slovy | Znal jsem to pravidlo a **přesto ho porušil** — protože jsem psal o *nástroji*, ne o *textu*. A je to zároveň důkaz, že brána ten nový dokument **otevřela** (což „exit 0" netvrdí) |

**Vzor z těch pěti:** **pět z pěti** byly v **měřidle nebo ve mně** — a **dva
vypadaly jako nález o cizím kódu** („brána je červená" → není; „sandbox blokuje
i workspace" → neblokuje). U **34** to zachránilo jen to, že jsem si našel, jak
nástroj pouští někdo jiný.

---

### 8e. Omyly AKČNÍ session 2. 10. 2026 (11:0x–12:0x UTC) — Úkoly A–D a B1

> **Devět z deseti** omylů vzniklo v **měřidle nebo ve mně**, ne v měřeném kódu —
> a **čtyři z nich vypadaly jako nález o cizím kódu**. Dva mě málem přivedly
> k „opravě" správné věci. **Plný popis s příkazy je v §16.8**; tady je tabulka
> ve stejném tvaru jako 8b–8d.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **40** | „Opravený test spadne, protože jsem ho blbě vložil" | **Patcher zapisoval literální `\t` místo tabulátoru** → Godot `Parse Error: Unexpected "extends" in class body`, testy **nedoběhly vůbec**. Nález o **patcheru**, ne o testu | GDScript bloky jsem měl v **Python literálech**; `\\t` v nich zůstalo dvěma znaky. Opraveno: bloky leží v `_analyza\*.gd` a čtou se **bajt na bajt** |
| **41** | „Kontrola se tiše přeskakuje" | **Přeskakovala se, ale ne tiše** — moje poznámka se **nevypisovala**, protože ji minul **filtr výpisu**, kterým jsem hledal. Chyba byla ve filtru | Hledal jsem v cizím výstupu podle vzoru a neověřil, že vzor odpovídá tomu, co jsem sám psal |
| **42** | „`move()` přes úroveň test nechytí" (podezření na slepou bránu) | **Chytí** — a **starý test taky** (`60 kontrol, 1 selhání`). Rozdíl je v tom, že starý hledá **text**, nový **chování** | Chtěl jsem dokázat, že nový test je lepší; pravda je, že **oba** tuhle vadu chytí a nový je lepší jen tím, že nezakazuje legitimní kód |
| **43** | „Po B1 je `test-cooldown` červený v opačném směru — přepíšu očekávání" | **Byla v něm i VADA FIXTURE:** `vloz()` plnil `naposledy_selhalo` přes `datetime('now', ?)`, jenže `?` je tam **argumentem funkce**, ne hodnotou sloupce → SQLite uložil **doslovný řetězec** `'-10 minutes'`, který se v `>` chová jako **0**. Scénář „v cooldownu" vycházel jako „má se vydat" a **vypadalo to jako vada guardu** | Do B1 se sloupec **nečetl**, takže vada fixture byla **neviditelná**. Odhalila ji až sonda `_analyza\f2-sonda-cooldown.py`, ne čtení testu |
| **44** | „`test-cooldown.py` je červený → B1 není hotové" | Test hlásil **2 chyby**: jedna byla ta fixture (43), druhá **skutečná** (guard v **dispatch smyčce**, který jsem opravil taky). **Nebyly to jeden problém, ale dva** | Spojil jsem „test je červený" s „oprava je špatná", místo abych si přečetl **které scénáře** a proč |
| **45** | „Registr `component()` v `game.gd` existuje" (převzato z promptu granule) | **Neexistuje** — `scripts/` ji **nikde nedeklaruje**, ale `hud.gd`, `mining.gd` a `save.gd` ji **volají**. Ověřil jsem to **až poté**, co jsem na tom postavil úvahu o „cestě přes `world`" | Vzal jsem tvrzení z **promptu granule** (popisuje cílový stav) jako popis **dneška** — přesně to, před čím varuje `AGENTS.md` |
| **46** | „V `_analyza\a-ukol-scratch` dám stejné testy jako v hlavním klonu" | **`57 kontrol, 3 selhání`** — v čerstvém `git worktree` **chybí `.godot/`** (je v `.gitignore`), takže se nenačtou assety. Vypadalo to jako **regrese kódu** | Neuvědomil jsem si, že import cache není v gitu. Řešení: zkopírovat `.godot` (574 souborů) → **59/0** |
| **47** | „Ve výpisu validátoru jsou dvě `CHYBA`, tedy dva problémy" | Souhrn hlásil **1 PROBLÉM** — jedna z těch dvou `CHYBA` je **očekávaný výstup běžícího testu** (scénář, který má být `False`) | Počítal jsem **řádky** ve výstupu místo **souhrnu**; táž past jako „různé čítače nesou stejné jméno" |
| **48** | „Mutace se provedla" (u ověření patcheru pro C2) | Patcher prošel, ale výsledný soubor měl **rozbitou českou uvozovku** (zavírací se zapsala jako ASCII) → `SyntaxError: '(' was never closed` na řádku, který vypadal správně | **Tatáž past, před kterou sám varuju** (skill `dsh-prostredi` §3d). Odhalil to až `ast.parse`; textová kontrola by ji minula |
| **49** | „Filtruju komentáře, takže komentář popisující vadu nezpůsobí falešný poplach" | Filtr `startswith('#')` **nestačí** — vada byla popsaná i v **docstringu**, a ten **není komentář**. Pojistka hlásila falešný poplach na **dokumentaci** | Znal jsem pravidlo „statická kontrola musí číst KÓD, ne komentáře" a implementoval ho **polovičně**. Opraveno přes `ast` |

| **50** | „**Úkol B je hotový** — test `resolve()` volá, doloženo mutací 2/2" | **Úkol B nebyl v repu.** Blok s `combat.resolve()` jsem aplikoval **jen do pracovního stromu** `_analyza\a-ukol-scratch` a **zapomněl ho vložit do `games\uo-shadows`**. Naměřeno (`_analyza\b-sonda-65.py`): klon **60 kontrol, 0 selhání**, scratch **64/0** | Dvě měření nad **dvěma stromy** a vydávání jednoho za druhé. Zachránila to jen kontrola „zdravý kód musí projít" v mutačním runneru — **ne** moje pozornost |

**Vzor:** **deset z deseti** omylů vzniklo v **měřidle nebo ve mně** (patcher,
filtr, sonda, fixture, synchronizace) — a **pět** vypadalo jako nález o cizím
kódu (41 „tiše se přeskakuje", 43 „guard je vadný", 46 „regrese kódu",
48 „Python neumí české uvozovky", 50 „mutace prošla = slepá brána").
Ani jeden z těch pěti **nebyl** nález o cizím kódu.

**A jeden omyl, který se NEPOVEDLO napravit:** schválené **pozastavení úlohy
#146** jsem neprovedl, protože na to conductor **nemá endpoint** a do D1 se
odsud zapsat nedá (údaje k Cloudflare jsou v GitHub Secrets). Není to
opomenutí, je to **nález** — a je zapsaný v §16.7 i s rizikem, které z toho
plyne (worker si #146 vzal **před** opravou testu).

---

---

### 8f. Omyly PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (11:4x–12:4x UTC)

> **Šest ze sedmi** omylů vzniklo v **měřidle nebo ve mně** — a **čtyři z nich
> vypadaly jako nález o cizím kódu**. Dva mě málem přivedly k „opravě" správné
> věci (jednou k opravě `run_tests.gd`, jednou k opravě `combat.gd`).
> **Plný popis s příkazy je v §17**; tady je tabulka ve stejném tvaru jako 8b–8e.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **51** | **„Úkol B má v `combat.gd` pořád Godot 3 API"** — můj skript `h17-kontrola-klonu.py` hlásil `CHYBA: STARÉ Godot 3 API .has( v combat.gd` | **Nebyla to vada.** Vzor `.has(` chytil **`Dictionary.has()`** (řádky 80 a 113), což je **platné Godot 4 API**. Vada by byla jen `Object.has()` na **uzlu** | Hledal jsem **textový vzor bez kontextu** — přesně ta past, před kterou varuje `AGENTS.md`. Opraveno na kontextové vzory (`attacker.has(`, `"armor_rating" in defender`) |
| **52** | **„Oprava testu se do klonu nepropsala"** — běh 2 mých mutací dal `60 kontrol, 1 selhání` místo očekávaných `60/0` | **Bylo to jinak:** v čistém worktree je **původní `combat.gd`** (z `origin/main`), a ten při **prvním zásahu** spadne na `has()`. Test tedy **správně** hlásil vadu — jen to nebyla vada testu Úkolu A, ale **chybějící synchronizace `combat.gd`** | **Tatáž past jako omyl 46** u akční session („chybí `.godot/`") — **měřil jsem neúplný strom a číslo jsem připsal jiné příčině.** Po dosynchronizování `combat.gd` z klonu: `64/0` |
| **53** | **„Čísla 60/61/64 z §16.1 musím naměřit stejně"** | **Nemusím a nemohu:** akční session měřila nad **scratchem**, kde je z Úkolu B jen `combat.gd` a **ne** blok v testech. Já jsem měřil **celý soubor testů z klonu** — proto **64/65** místo 60/61. **Obě čísla jsou správná**, protože odpovídají na jinou otázku | Opsal jsem **očekávaná čísla z cizího zadání** místo abych si nejdřív **vysvětlil rozdíl**. Zachytil to až `assert` v mém vlastním runneru (9 rozchodů) |
| **54** | **„Řádek s `izo projekce` znamená, že se kontrola Úkolu A spustila"** | **Neznamená** — `izo projekce 2:1` je **jiná, legitimní kontrola** (`level.gd`). Detektor proto hlásil nález i tam, kde žádný není | Hledal jsem **krátký podřetězec**, který je i v jiné kontrole. Opraveno na přesnou větu `nebere izo projekci z úrovně` |
| **55** | **„Mutace M3 (vypuštění větve `hodnota()`) je jen práce navíc, kterou test nemusí krýt"** — málem jsem ji zapsal jako „zbytečná složitost v `combat.gd`" | **Je to NÁLEZ o bráně, ne o kódu:** M3 **není chycena** (0 selhání), ačkoli se větev **volá** (2×). Obě větve vracejí totéž číslo, takže test **nedokáže rozlišit pořadí** | Chtěl jsem odpovědět na otázku ze zadání („je dvojí tvar práce navíc?") **dojmem z kódu**. Odpověď dala až **sonda s čítači** (`h17-sonda-vetve.py`) — a je opačná |
| **56** | **„`zmena=false` v mém souhrnu běhů znamená, že agent nic nezměnil"** | U **pěti ze šesti** běhů to bylo **pravda i nepravda zároveň**: hledaný řetězec je i v `echo` kroku, který se do logu **vypisuje** → skript hlásil `true` i tam, kde se na ten krok vůbec nedošlo | Hledal jsem text, který se v logu vyskytuje **dvakrát z různých důvodů**. Opraveno na `##[error]` + hledaný text |
| **57** | **„Do souboru pro Node zapíšu český text přes `Set-Content`"** | **Brána diakritiky to ohlásila jako vadu** — z českého písmene se stal **náhradní znak** a soubor `h17-vsechny-behy.mjs` měl „rozbito: ANO" | Znal jsem pravidlo (`dsh-prostredi` §3d: „piš skript do souboru") a **přesto** jsem here-string poslal přes PowerShell. Odhalila to až brána — a to je zároveň **doklad, že ten soubor opravdu otevřela** |
| **58** | **„Oddíl §17.11 už mám zapsaný"** — soubor jsem pojmenoval `s17b-doplneni.md`, ale v `python -c` jsem ho hledal jako `s17b-doplněni.md` (s diakritikou) | `FileNotFoundError`. **Nic se nezapsalo** — a to je dobře: kdyby skript pokračoval dál, vložil by do `HANDOFF.md` **prázdný oddíl** | **Tatáž past jako omyl 57** (kódování a diakritika v příkazu) a **znovu v jednom kroku**: český text v `python -c`. Opraveno **skriptem v souboru** (`s17b-zapis-handoff.py`) — což je přesně ten postup, který jsem předtím **dvakrát** poradil a **jednou sám nedodržel** |
| **59** | **„Inventář jazyka je v pořádku, vždyť jsem ho nechal být"** — po editaci `kontrola-diakritiky.py` a `~\.dsh\skills\overovani\SKILL.md` jsem čekal `g3-brany.py` zelené | **Dvě brány spadly na `exit 2`** (`c2-mutace.py` → „ZDRAVÝ INVENTÁŘ … CHYBA: INVENTÁŘ JE ZASTARALÝ"; `n1-over-inventar.py`). **Bylo to SPRÁVNĚ** — oba soubory jsou vstupy skeneru | **Nebyl to omyl měření, ale omyl OČEKÁVÁNÍ:** zapomněl jsem, že **edituju i soubory, které skener čte**, ne jen ty, které „jsou kód“. Opraveno přegenerováním (`--json _analyza\_inventar.json` → 2 075 nálezů) a **zapsáno jako §17.11/1** — je to totiž **nejlepší argument pro pravidlo do `AGENTS.md`** (§17.9/5) |
| **60** | **„Počty omylů v blocích 8b–8f znám"** — do kroniky jsem je napsal **odhadem z přečteného textu** (8d = 5, 8e = 10, celkem 52) | **Bylo to špatně:** 8d má **6** omylů (34–39) a 8e **11** (40–50), celkem **54**. **Odhalila to až kontrola kroniky** (`_analyza\kronika-kontrola.py`), kterou jsem psal **ve stejné session** — ne moje pozornost | **Tentýž vzor jako všechno ostatní v tabulce omylů: vada MĚŘENÍ, ne nález o projektu.** Napsal jsem číslo, které jsem **nespočítal**. A je to **ironie, která patří do kroniky:** první verze dokumentu o tom, že 79 % omylů vzniká v měřidle, obsahovala **omyl v měřidle** — a zachytilo ho **měřidlo postavené na to, aby tu kroniku kontrolovalo** (§3 kroniky, `KRONIKA-PROJEKTU.md`) |

**Vzor z deseti (po doplnění 58, 59 a 60):** **devět** vzniklo v **měřidle** (vzor bez kontextu, neúplný
strom, opsaná očekávání, krátký podřetězec, text dvakrát, kódování)
a **čtyři vypadaly jako nález o cizím kódu** (51 „kód má Godot 3 API",
52 „oprava není v klonu", 54 „kontrola proběhla", 56 „agent nic nezměnil").
**Ani jeden z těch čtyř nebyl nález o cizím kódu.** Je to týž vzor jako 8b–8e,
jen o kolo dál — a potvrzuje, co predikuje `AGENTS.md`: *„počítej, že i tvoje
první číslo bude někde mimo."*

**Vzor z devíti (po doplnění 58 a 59):** **osm z devíti** vzniklo v **měřidle
nebo ve mně** a **čtyři vypadaly jako nález o cizím kódu**. Navíc **57 a 58
jsou TÁŽ past dvakrát za sebou v jednom kroku** (český text v příkazu místo
v souboru) — což je nejlepší doklad toho, že **znalost pasti nestačí**;
rozhoduje **postup**.

**A jeden nález, který se NEPOVEDLO uzavřít:** `HANDOFF.md` §16.11 a
`_analyza\g1-diakritika-novych.py` odkazovaly na `_analyza\c2-sonda-uvozovky.py`,
který **na disku nebyl** (nález **H1**, §17.8). Soubor jsem **obnovil**
a ověřil vlastním spuštěním — ale **nevím, jestli byl smazaný omylem, nebo
úmyslně**; kdyby úmyslně, je jeho obnova zásahem proti rozhodnutí, které
jsem nenašel. Zapsáno jako otevřený bod.

### 8j. Omyly AKČNÍ session 2. 10. 2026 (dokončení auditu dokumentace) — **87–96**

**Kontext:** sedm omylů vzniklo jedné session při **opravě měřidel podle
auditu** (`ZADANI-DOKONCENI-AUDITU.md`). **Všech sedm je v měřidlech nebo
v postupu měření** — ani jeden není nález o cizím kódu. **Dva z nich (`87`,
`88`) by neodhalilo čtení kódu**; odhalil je až **mutační test**.

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **87** | **Mutační skript spadl na přehnaně přísném assertu** — a mohl nechat `HANDOFF.md` zmutovaný | `assert "Provedeno 2. 10. 2026" not in zmut` kontroloval **celý dokument**, ale ten řetězec je i v **§16** a **§21** | `AssertionError` **na správné mutaci**; škoda nevznikla jen tím, že assert byl **PŘED** zápisem | Assert o „podmínka přestala platit" **zúžit na měřenou jednotku** (ten nadpis, ten řádek), ne na soubor. A **každou mutaci obal `try/finally`**, které soubor vrátí. *(Obě pravidla zapsána do `overovani` §10.6)* |
| **88** | **Značka času se mi přilepila od SOUSEDNÍHO tvrzení** | má funkce `ma_znacku_casu()` hledala „stav před" **kdekoliv v okně ±60 znaků** | **mutační test M2**: číslo `32` dostalo značku od třicetidevítky (`**„32 sloupců"**, správně je **39** (stav před B1…)`) → brána ho zařadila jako `[záznam]` a byla **slepá přesně k vadě R1** | Značka musí být k číslu **PŘIPOJENÁ**: mezi číslem a značkou nesmí být **jiné číslo**. *(→ `overovani` §10.3)* |
| **89** | **Okno „blok výskytu" jsem vzal 5 441 znaků** | první verze brala „souvislý běh neprázdných řádků" | **mutační test M2** — a jen proto, že jsem **vypisoval velikost okna**. V `AGENTS.md` je oddíl „## Jak dokumentovat" **jeden blok o 5 441 znacích se sedmi daty** → jediné datum kdekoli v něm **umlčelo celá oddíl** | Okno **zastavit na začátku dalšího celku** (odrážka, tabulka, nadpis) → **824 znaků**. A **zúžení ZVÝŠILO pokrytí** (26 → 27 rozchodů): **velkorysé okno není opatrnost, je to slepota.** *(→ §10.4)* |
| **90** | **Můj ověřovatel měřil JINÝM OKNEM než nástroj** | v `audit2b-over.py` jsem blok spočítal znovu — jako „souvislé neprázdné řádky" (5 441 znaků), kdežto nástroj už používal **jednu odrážku** (824) | výpis ověřovatele ukazoval **čísla z jiného okna, než jaké se měřilo** — a přitom vypadal jako důkaz | Když ověřovatel reimplementuje logiku nástroje, musí to být **řádek po řádku táž logika** + komentář „MUSÍ BÝT SHODNÉ S…". Je to **§9.2 znovu, o vrstvu níž**. *(→ §10.5)* |
| **91** | **Zálohu jsem udělal u `audit2a-schema.py`, ale NE u `audit2b-cisla-proti-zdroji.py`** | `Copy-Item` jsem použil u prvního souboru a u druhého jsem rovnou přepsal | Naštěstí **nic nevzniklo** — měl jsem celé původní znění z čtení. Ale `overovani` §2.1 říká **„zálohuj kopií"** a u souboru, který **není v gitu**, je to jediná cesta zpět | **Záloha PŘED prvním zápisem**, ne před druhým. A týž den se to málem vymstilo i u `HANDOFF.md` (omyl 87) |
| **92** | **Snapshot sám sobě zneplatnil baseline inventáře** | `audit-snapshot.py` (Úkol 0) kopíruje dokumentaci do `_analyza\snapshot-<čas>\` — a `audit1-inventar.py` ty **kopie začal počítat jako dokumenty** | `audit1-inventar.py` po prvním snapshotu: **159 dokumentů místo 98**, **66 záloh místo 8**, „bez hlavičky" **116 z 159** místo **62 z 98** | Vyloučit předponu `snapshot-` (doplněno do `audit1-inventar.py`). **Obecné poučení: opatření, které něco KOPÍRUJE, musí říct všem měřidlům, že je to kopie** — jinak si příští session přečte vlastní snapshot jako stav dokumentace |
| **93** | **První dojem z rozdílu proti baseline byl „regrese"** | `audit6-brany-mutace.py` i `g3-brany.py` hlásily proti auditu **jiná čísla** (`validate-all (CELEK)` `exit 1` → `exit 0`) | Než jsem to zapsal, všiml jsem si, že audit to vedl jako **„NEPROBĚHLO — PROSTŘEDÍ"** — a teď je sandbox **`danger-full-access`** | Je to **§7.13**: „neproběhlo" se pod širším oprávněním **změní na zelenou** a **není to oprava kódu**. Do zápisu patří **obojí**: co se změnilo a **čím to bylo** |

**Vzor z těch sedmi (a je nepříjemný):** **sedm ze sedmi** vzniklo
**v měřidle nebo v postupu**, a **dva** z nich by bez **mutačního testu**
odešly jako hotová práce. To je týž podíl jako v předchozích blocích — **trend
se nezlepšil**, i když session dělala právě opravu měřidel. Nejlepší vysvětlení,
které pro to mám: **oprava měřidla je sama měření**, takže na ni platí tytéž
pasti — a kdo je nezná, projde jimi znovu.

| **94** | **Můj ověřovatel „nic nezmizelo" vyrobil FALEŠNÝ POPLACH** — ohlásil, že v kronize zmizely **4 řádky** | v `s23-kronika.py` jsem po zápisu porovnával, že každý neprázdný řádek původního textu je i v novém. Jenže **čtyři řádky se aktualizovaly ZÁMĚRNĚ** — nesou stará čísla (`86` / `65` / `9` / `81`) a v nové verzi mít **nemají** | `CHYBI: | **omylů celkem v HANDOFF.md (unikátní id)** | **86** | …` a tři další | Je to `overovani` **§9.6**: **očekávaná nepřítomnost není vada.** Kontrola „nic nezmizelo" musí mít **seznam záměrných změn** a odečíst ho; jinak hlásí ztrátu tam, kde proběhla plánovaná aktualizace — a takový poplach se hledá hůř než slepé místo |

| **95** | **Dokumentovat vadu v `AGENTS.md` ROZBILO mutační test, který tu vadu vrací** | přidal jsem do `AGENTS.md` odstavec, který vadu R1 **popisuje** — a v něm je `„32 sloupců"` **citované podruhé**. Tím se kotva testu `audit2a-mutace.py` (M2) stala **dvojznačnou** | `CHYBA: M2 se neprovedla (kotva 2x)` — test to **správně odmítl** a spadl. Odhalil to až **společný běh všech bran na konci session**, ne čtení | Kotvu **zúžit na jednoznačné okolí** (`**„32 sloupců"**, správně je`) — a **po každé editaci dokumentu, který je kotvou někde jinde, spustit i testy, které na něj míří**. Je to `overovani` **§9.8**, kterou jsem si do skillu zapsal **v téže session** — a přesto jsem do ní spadl |
| **96** | **Kontrola, která žádala SHODNÝ HASH u APPEND-ONLY dokumentu** | `audit2b-over.py` ověřoval „`HANDOFF.md` je nedotčený" **rovností SHA-256** se snapshotem Úkolu 0. Jenže **toutéž session do něj bylo legitimně připsáno** (§8j a §23 — přímý požadavek zadání, Úkol 6c) | `CHYBA: HANDOFF.md se od Úkolu 0 ZMĚNIL — nález R3 se nemá opravovat v datech!` a `HANDOFF.md:1143 granulí NENÍ v ZÁZNAMECH` — **druhá chyba byla jen posun řádků** (kotva se připsáním posunula na **1174**) | U **append-only** dokumentu se neptej „je stejný?", ale **„je původní stav pořád celý uvnitř?"** — to je A2. A **kotvu hledej podle OBSAHU, ne podle čísla řádku**: číslo se posune vždy, když se dokument doplní. *(Obě pravidla zapsána do `overovani` — viz návrh NA24)* |

**A jeden údaj, který tomu nasvědčuje:** omyl **88** je **třetí výskyt téže
třídy** („měřidlo odpovídá na jinou otázku") v jedné session — po omylu **89**
(okno) a **90** (jiné okno v ověřovateli). Všechny tři mají stejný podpis jako
nálezy z 1. 10. a přesto se opakovaly.

### 8k. Omyly PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (16:4x–17:1x UTC) — **97–101**

**Kontext:** pět omylů vzniklo jedné session při **ověřování cizí práce** —
a **všechny jsou v měřidlech nebo v postupu měření**, ani jeden není nález
o cizím kódu. **Dva z nich (`99`, `100`) by neodhalilo čtení kódu**; odhalil je
až **mutační test**. To je týž podíl jako v blocích `8e`–`8j` — **trend se
nezlepšil**, ani když session dělala **jen ověřování**.

| # | Co jsem udělal | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **97** | **Měřil jsem „brána to nehlásí" podle VÝPISU, a výpis je zkrácený** | `s24-slepota-audit2b.py` usoudil „`audit2b` vložené tvrzení nevidí", protože ho nenašel ve výstupu | Ručně jsem došel na to, že `audit2b` tiskne ze ZÁZNAMŮ jen **prvních 40** (`histor[:40]`) — takže „není ve výpisu" **není** „nevidí to" | Měřit **ČÍTAČ ze souhrnu** (`ROZCHODŮ: N`), ne výskyt ve výpisu. Vzniklo `s24-slepota-audit2b-presne.py`. Je to `overovani` **§9.4**: *naměřeno 0 má tři různé významy* |
| **98** | **Nechal jsem si ověřovatele spočítat jen ČÁST měření** | v hrubé verzi jsem kontroloval jen `ROZCHODŮ`, ale tvrdil jsem něco o **klasifikaci** (záznam vs. tvrzení) | Tentýž běh: tvrzení se ve výpisu objevilo, ale **nebylo v rozchodech** — a moje zpráva to nerozlišila | Oddělit **dvě otázky**: (a) *vidí to brána?* (b) *zařadila to správně?* — a ptát se na každou **jiným měřením**. Obě jsou teď v přesné verzi |
| **99** | **Tři neúspěšné verze jedné kontroly — a každá SELHALA JINAK** | do nové brány `s24-meridla-over.py` jsem psal kontrolu „kolik bloků omylů je mimo kotvy brány" | **M1:** vzor `### 8[a-z]` — mutace `8h-test` mu **vyhověla** → kontrola nereagovala. **M2:** „padni, když odpovídá VŠE" — mutace shodu **snížila** (10 → 7) → taky nereagovala, **a navíc padala na zdravém stavu** (`8i`/`8j`). **M3 (správně):** kotva brány musí v dokumentu **existovat** | `overovani` **§7.14**: mutace musí obrátit **MĚŘENOU PODMÍNKU**, ne jen změnit soubor — a **směr podmínky se musí ověřit na OBOU stranách** (zdravý stav musí projít, vada musí spadnout). Cena: **tři kola**, každé odhalil až mutační test |
| **100** | **Použil jsem NEAKTUÁLNÍ předpoklad o cizím nástroji** | do brány jsem napsal, že `validate-all` má `otevřela:` **prázdné** (tak to bylo v auditu) | Běh ukázal **`otevřela: 3`** — a to **není počet souborů, ale `NALEZENO 3 PROBLÉMŮ`**. Past **zůstala**, jen **změnila projev** | Ověřovat **živý stav**, ne zápis v auditu; a **vzor, který umí trefit chybovou hlášku, je vada i tehdy, když vypadá jako číslo**. Zapsáno do `HANDOFF.md` §24.6 a do zadání jako Úkol 2a |
| **101** | **Zápis vlastního výstupu do složky, kterou táž brána prochází** | `python _analyza\g1-…py > _analyza\_tmp-g1.txt` — PowerShell zapsal **UTF-16LE** | `g1` ohlásil **`exit 1`** s jedinou vadou: `_tmp-g1.txt … NELZE PŘEČÍST: UnicodeDecodeError` → **vadou byl můj vlastní soubor** | Nástroj **`audit-cleanup.py`** na to existuje **od auditu** a audit tuhle past **sám zapsal** („první běh `g1` skončil `exit 1` a jediná vada byl můj vlastní výstupní soubor"). **Je to počtvrté** → zapsáno jako nález **H30** |

**Vzor z těch pěti (a je nepříjemný):** **pět z pěti** vzniklo
**v měřidle nebo v postupu**, a **dva** by bez **mutačního testu** odešly jako
hotová práce. **A ještě jeden údaj do trendu:** omyl **97** je **třetí výskyt
téže třídy** („měřidlo odpovídá na jinou otázku") v jedné session — po **98**
(nezměřená část) a **99** (třikrát špatný směr kontroly).

---

### 8q. Omyly 132–137 — AKČNÍ session 4. 10. 2026 (PŘESUN NA `E:`)

**Šest omylů, a všech šest je v MĚŘIDLE OPRAVY, ne v datech.** Záznam:
`PLAN-SEPARACE-WORKSPACE.md` **§11.4**.

| # | Co jsem si myslel | Jak to vzniklo | Jak se to poznalo | Správně |
|---|---|---|---|---|
| **132** | „Nahradím literály cest výrazem — je to jen substituce." | první verze `p8-oprava-cest.py` vložila `join(PARENT, 'repo')` **dovnitř uvozovek** | **až parser po zápisu**: `SyntaxError: Unexpected identifier 'uo'` | Nahrazovat se musí **celý literál včetně uvozovek**. Po každém zápisu se parsuje a při chybě se soubor **vrací ze zálohy**. Cena: 4 kola opravy skriptu |
| **133** | „Když to projde parserem, je to správně." | `r`-prefix z literálu `r"C:\..."` zůstal před výrazem → vzniklo jméno proměnné **`r_PARENT`** | **pohledem na výstup** (až po zápisu), ne parserem | `r_PARENT / 'repo'` je **platný Python** — `ast.parse` ho PUSTÍ a vada se projeví až `NameError` **za běhu**. **Syntaxe ≠ smysl.** Musela přibýt kontrola podezřelých jmen. Nález **H42** |
| **134** | „`HRA` prostě nahradím." | v `a3-mutace.py` vzniklo **`HRA = HRA / ...`** — proměnná se definuje **sama sebou** | `NameError` za běhu; `node --check` ani `ast.parse` to **nevidí** | Nahrazovat **jen volání**, ne definici. Vznikla kontrola „použitá vs. definovaná proměnná" (`p8m`) |
| **135** | „Mrtvé cesty stačí ohlásit, ať je vidět." | ochrana před `gameforge\...` byla napsaná **ZA** nahrazováním, takže se mrtvá cesta **stihla změnit** na `rSTANICE` | **pohledem na výstup** — vzniklo `Image.open(rSTANICE)` | Mrtvá cesta se musí **vyloučit PŘED** nahradou. Muselo se to opravit zvlášť (`p8k`) |
| **136** | „Hlavička s `_STANICE = koren stanice` je ta správná." | `p8b` vložil do 29 nástrojů `_STANICE = C:\Users\Ssevc\Local-Deepseek` | **spuštěním brány**: `ag-over-cisla.py` hlásil „AGENTS.md neexistuje" — hledal ho **na stanici**, ale `HANDOFF.md` se přesunul **do repa** | `WS` v těch nástrojích znamenalo **„kořen s projektovými dokumenty"** — a ten je **REPO**. Kdyby zůstalo, **26 nástrojů by tiše četlo jiný strom**. Opraveno `p8c` |
| **137** | „Česky píšu pořád, to je v tomhle projektu správně." | psal jsem `def změř(...)` v `p3-bazline.py` a `p5-presun.py` | **brána `hl-rizika-jazyka.py`** — ne já: `IDENTIFIKÁTOR (jméno funkce/třídy) změř` | Pravidlo zní **identifikátory = ASCII**; diakritika patří do **komentářů a dokumentace**. Přejmenováno na `zmer`. **Tatáž session přitom opravila cyrilské `е` v cizím nástroji (H46)** — a svého vlastního přehlédnutí si nevšimla |

**Vzor z těch šesti (jiný než u 97–101):** **pět ze šesti** odhalil **až POHLED
NA VÝSTUP nebo SPUŠTĚNÁ BRÁNA** — ne parser, ne `node --check`, ne čtení kódu.
To je přesně past **H42**: *syntaktická kontrola je slepá k smyslu.* **A jeden
(137) našla brána, ne autor** — což je argument pro to, proč brány po přesunu
**musely** být spuštěné, ne jen „měly by být zelené".

---

### 8r. Omyly 138–143 — PLÁNOVACÍ (ověřovací) session 4. 10. 2026 (OVĚŘENÍ PŘESUNU)

**Šest omylů, a všechny mají stejný podpis: měřil jsem něco jiného, než jsem
si myslel.** Záznam: `HANDOFF.md` **§30.16**. **Čtyři z prvních pěti** (138, 139,
140, 141) vznikly **v prostředku měření**, ne v datech — a **každý z nich by
vyrobil falešný nález o CIZÍ práci**, kdybych se zastavil u prvního výsledku.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **138** | „Vložím vadu do `tools/over-skilly.py` hledáním `#!`." | **Soubor `#!` nemá** → `replace` neudělal nic → `AssertionError: MUTACE SE NEPROVEDLA` | **Neprovedená mutace vypadá jako úspěch** (`overovani` §7.9). Napsal jsem mutaci podle **předpokládaného** tvaru souboru, ne podle jeho **obsahu** |
| **139** | „Skener `hl-neanglicky-v-kodu.py` nevidí `def změř(...)` → je SLEPÝ." | **Soubor nebyl v GITU** — skener čte `git ls-files`, takže ho **vůbec nezpracoval**. Po vložení do **trackovaného** souboru brána **spadla správně** (`z toho IDENTIFIKÁTORY: 1`, `exit 1`) | **Slepota byla v mé mutaci, ne v bráně** (`overovani` §7.14). A stal se z toho **nález H52** — tedy aspoň něco: měřidlo má **skutečnou mezeru v pokrytí**, jen jinou, než jsem tvrdil |
| **140** | „`hra.cmd` v repu **neexistuje** → rozhodnutí **D7 nesedí**." | **Existuje** — v repu **HRY** (`E:\Workspaces\uo-shadows\hra.cmd`, git-trackovaný) a **funguje** (spuštěno, Godot naběhl). **Hledal jsem jen v repu orchestra** | **Nehledal jsem v obou repech**, i když zadání před ním výslovně varuje („nezaměňovat oba repy"). Byl jsem **jeden krok od falešného nálezu** o práci, která je v pořádku — a to je **nejdražší druh falešného poplachu** |
| **141** | „`Get-PSDrive E:` hlásí nulu → návrh **NA25 potvrzuji**." | **Hlásí správně** (`Free=869273522176`). Nula je **vlastnost omezeného oprávnění** (`ConstrainedLanguage`), **ne stanice** | Přebíral jsem **závěr z dokumentu** místo vlastního měření. Kdybych NA25 potvrdil, zapsal bych do skillu **nepravdivé pravidlo** — a to je horší než žádné (`AGENTS.md`). Opraveno na **H56** s přesnějším zněním |
| **142** | „§29.5 tvrdí `exit 0` u všech 12 bran, ale `kontrola-driftu` má `exit 1` → nález o nepravdivém čísle." | **Je to nepřesnost NADPISU, ne nepravdivé číslo** — nástroj má `exit 1` **správně** (hlásí rozdíl). Číslo `12 souborů, 1 rozdíl` i verdikt „není regrese" **sedí** | Než jsem číslo označil za nepravdivé, **nepřečetl jsem, co ta věta tvrdí** (`overovani` §10.1: „vzor našel" ≠ „vzor našel to, co hledám"). Výsledkem je **H54**, ale **menší**: drobná nepřesnost dokumentu, ne vada práce |
| **143** | „Do `HANDOFF.md` opíšu starou cestu tak, jak ji vypsal nástroj — je to citace výstupu." | **Brána `kronika-kontrola.py` ji ohlásila jako NEEXISTUJÍCÍ ODKAZ** (`CHYBA kronika odkazuje na neexistující …`), protože jsem ji vysázel **ve zpětných apostrofech** — a její vzor nerozliší **odkaz** od **citace cesty** | **Tatáž past, před kterou `AGENTS.md` varuje u ukázky rozbitého kódování** („popisuj ji slovem") — jen u **cesty** místo znaku. Odhalila to **brána**, ne já; opraveno **popisem slova** („README orchestra"). Je to **falešný poplach na správném dokumentu** — a ten se hledá hůř než slepé místo |

**Vzor z těch šesti (a je poučnější než u 132–137):** akční session měla
**pět ze šesti** omylů odhalených **až spuštěním**. Tahle session měla
**čtyři z šesti** omylů ve **vlastním měřidle** — a **tři z nich** (139, 140, 141)
by vedly k **nepravdivému nálezu o cizí práci**. **A jeden (143) našla brána,
ne autor** — stejně jako u akční session (137). Rozdíl je v tom, že ověřovatel
**pracuje s cizími čísly a nemá je jak poznat** — proto musí být každé jeho
tvrzení **měřené, ne převzaté**, a proto má **mutace dokazovat i to, že se
skutečně provedla** (138).

---

### 8s. Omyly 144–148 — AKČNÍ session 5. 10. 2026 (P13c: OPRAVA PĚTI MĚŘIDEL)

**Pět omylů, a všechny mají stejný podpis jako předchozí sekce: měřil jsem
něco jiného, než jsem si myslel.** Záznam: `HANDOFF.md` **§31.8**.
**Tři z nich (144, 145, 148) vznikly ve VLASTNÍM MĚŘIDLE** — a dva z nich
(147, 148) by vedly k **nepravdivému nálezu o správném kódu**.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **144** | „Vrátím do `g3` STARÝ literál cesty (`orchestra/tools/over-skilly.py`) — to je přece vada H48." | **Není.** Vada H48 je **nedosazený ZÁZNAMNÍK** (`<TOOLS>`), ne jiná (neexistující) cesta. `dosad()` s takovým textem nemá co dělat a `NEDOSAZENÉ CESTY` **správně mlčelo** | **Měřená podmínka se musí obrátit, ne jen „něco změnit"** (`overovani` §7.14). Oprava: mutace **vypíná substituci** — záznamník zůstane v příkazu a soubor s ostrými závorkami neexistuje |
| **145** | „S vadou se v zachyceném výstupu objeví `can't open file` — na to se dá ptát." | **Neobjeví.** PowerShell spouštěl neexistující cestu a spadl **sám** (`WinError 2`); v `capture_output` nebylo NIC z toho, co jsem hledal. Test proto hlásil „brána vadu nevidí" | **Predikát mířil na TEXT interpretu, ne na VÝSLEDEK.** Oprava: signál = `exit=2` **a zároveň** žádný čítač **a zároveň** krátký výstup. (A je to táž past, jakou zadání samo používá: `can't open file` je text **Pythonu**, ne stav.) |
| **146** | „Mutace `install-into-repo.ps1` je jen náhrada textu — kódování neřeším." | Zápis **zahodil UTF-8 BOM** (soubor ho má), a `blok_generatoru()` čte `utf-8-sig` → mutace by měřila **jiný jev** | **Zapisuj ve stejném kódování, v jakém čteš** (`dsh-prostredi` §5b). Oprava: BOM se detekuje, zapisuje se s ním a po zápisu se **jeho přítomnost ověří** |
| **147** | „Když soubor obsahuje `ZMĚŘENO`, najdu to vzorem `ZMĚŘENO`." | **Ve třech souborech bylo `ZMEŘENO`** — chybělo `Ě` (`verify-setup.py`, `lint-roadmapa.py`, `f3-over-deploy.mjs`). **Výpis vypadal dobře, vadný byl SOUBOR** | **Přesně obrácená past, než popisuje `dsh-prostredi` §2b** (tam vypadá vadně soubor, a je to výpis). Našel to **mutační test**; opraveno `_analyza/p13c-oprav-diakritiku.py` a ověřeno **čtením z disku** |
| **148** | „Sken na chybějící importy hlásí 57 souborů — to je velký nález." | **Většina byla falešných.** Vzor `\bjoin\s*\(` chytal i **`arr.join(',')`** (metoda pole). `conductor/src/index.ts` má 9× `Array.join` a `join()` z `node:path` **nikdy nevolá** | **Falešný poplach nutí „opravovat" správný kód** (`overovani` §9.5) — a tady by přidal **import, který soubor nepotřebuje**. Oprava: předpona `.`/`?.`/`\w` volání vylučuje; `resolve` se **vůbec nehlídá** (`new Promise((resolve) => …)` je jiné `resolve`) |

**Vzor z těch pěti (a je poučnější než u 138–143):** u **třech** z nich šlo
o to, že **měřidlo měřilo samo sebe nebo svůj text** — a **všechny tři** by
vyrobily **nepravdivý závěr o bráně** („je slepá", „neměří", „má 57 nálezů").
**Dva (144, 145) odhalil až běh testu, ne čtení kódu** — což je týž závěr jako
u předchozích sekcí: **mutace, která se tiše neprovede nebo míří na jinou
podmínku, tvrdí totéž co mutace, která projde.**

---

### 8t. Omyly 149–155 — OVĚŘOVACÍ session 5. 10. 2026 (P14: PŘEMĚŘENÍ OPRAV P13c)

**Sedm omylů, a všechny mají tentýž podpis jako celá tahle kronika: měřil jsem
něco jiného, než jsem si myslel.** Záznam: `HANDOFF.md` **§32.8**.
**Dva z nich (149 a 152) by daly NEPRAVDIVÝ NÁLEZ o cizím kódu nebo o datech** —
a jeden (149) **shodil tři cizí brány**, přičemž to chvíli vypadalo jako vada
orchestra.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **149** | „Píšu jen ověřovací nástroj, jazyk neřeším." | V `_analyza/p14d-verify-setup-sonda.py` bylo jméno proměnné **`okolí`** (s diakritikou) → `hl-rizika-jazyka.py` **exit 1** → `validate-all.mjs` **1 PROBLÉM** → `n1-over-inventar` a `C2: mutace N1` **exit 2**. **Tři červené brány z jedné mojí proměnné** | **Našla to brána projektu, ne já** — a přesně proto existuje. Oprava: `okolí` → `okoli`; a protože to málem stálo celé měření, vznikl **`_analyza/_sonda-identifikatory.py`** (AST nad mými skripty: 3 446 identifikátorů, 0 nálezů) |
| **150** | „Mutační test prošel → měřidlo měří." | Test čekal text `ostrá závorka`, což je **podřetězec i v řádku `OK`**. Prošel by **i nad slepým měřidlem** | **Popisek kontroly není její výsledek** (`overovani` §10.1: „vzor něco našel" ≠ „vzor našel to, co hledám"). Oprava: očekávaný text má předponu **`CHYBA …`** |
| **151** | „Když je tělo sekce prázdné, moje měřidlo to pozná." | **Nepoznalo.** Tělo začínalo oddělovačem `====`, takže „prázdné" tělo mělo po `strip()` **78 znaků** | Odhalil to **mutační test M4 mého vlastního měřidla**. Oprava: oddělovač se z těla odstraní **před** měřením prázdnoty |
| **152** | „Součet řádků tabulky v kronice §3 je **130** a bloků **18**." | **143 a 19.** Vzor vyžadoval `\| **N** \|` i v posledním sloupci, ale blok `1–13` má tam **pomlčku** → jeho řádek se tiše vynechal | **Kdybych to zapsal, byl by to nepravdivý nález o datech kroniky.** Oprava: poslední sloupec smí být `—`; součet se navíc křížově ověřil proti `kronika-kontrola.py` (**143**) |
| **153** | „Kotva `\n.env\n` v `.ps1` souboru funguje." | **Nefunguje** — `install-into-repo.ps1` má **195× CRLF a 0× osamocené LF**. Mutace by se **tiše neprovedla** a test by hlásil „brána je slepá" | Ověřeno **měřením bajtů PŘED během** (`overovani` §7.9). Kdyby se to neudělalo, byl by to **falešný nález o bráně** |
| **154** | „Heredoc `python - <<'PY'` mi ušetří psaní skriptu." | PowerShell ho **nemá** (`The '<' operator is reserved for future use`) a **zbytek skriptu rozparsuje jako PowerShell** → chyby míří na řádky, které s příčinou nesouvisí | `dsh-prostredi` §3f to říká **doslova** — a stejně jsem to udělal. Oprava: skript **do souboru** (`write`), ne do `-c` ani do heredocu |
| **155** | „Ověřím, že kód nikde nečte `AGENTS.md`" (o ručním seznamu v `verify-setup.py`) | **Nepravda** — brána `AGENTS.md` **čte** (kontroluje jeho UTF-8 v §6). Správné tvrzení je **užší**: seznam se z něj **neodvozuje** | **Příliš široké tvrzení je taky nepravda** (a je to stejná třída jako „brána čte citaci místo tvrzení"). Oprava: kontrola se ptá na **kód před seznamem** a na **AST literál**, ne na „zmínku v souboru" |

> **⚠ POUČENÍ, KTERÉ JE CENNĚJŠÍ NEŽ TĚCH SEDM OMYLŮ:** **omyl 149 odhalila
> brána projektu, ne já** — a to je poprvé v téhle kronice, co se vada měřidla
> našeho vlastního ověřovatele projevila **jako červená cizí brány**.
> Kdybych `validate-all` nespustil, **zapsal bych „3 nenulové exity" jako stav
> orchestra** a byla by to lež — vyrobená ověřovatelem.
> **A druhá polovina téhož:** kdybych měřil **jen** podle `g3`, uviděl bych
> „0 nenulových exitů" a **nic bych nezjistil** — rozdíl je v tom, že jsem každou
> bránu spouštěl **sám** (`p14b`) a **PTAL SE, KDO JE ČERVENÝ**.

### 8u. Omyly 156–159 — AKČNÍ session 5. 10. 2026 (P15: OPRAVA NÁLEZŮ H70–H79 Z P14)

**Čtyři omyly — a tři z nich jsou v MĚŘIDLE, ne v opravovaném kódu.** Záznam:
`HANDOFF.md` **§33**. Všechny čtyři mají tentýž podpis jako celá kronika:
**měřil jsem něco jiného, než jsem si myslel.**

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **156** | „Očekávaný text brány znám — stojí v zadání i v `HANDOFF.md` §32.5." | `zadani-kontrola.py` hlásí **„nepodařilo přiřadit k repu"**, ale test hledal **„nepodařilo se přiřadit k repu"** → hlásil **CHYBU na SPRÁVNÉ bráně** | Text jsem **opsal ze ZÁZNAMU, ne ze ZDROJE**. `HANDOFF.md` i zadání píší „nepodařilo se přiřadit" — to je **popis záměru**, ne výstup brány. Oprava: konstanta ze **zdroje** (`grep` v bráně). Odhalil to běh testu |
| **157** | „Rychlá kontrola přes `python -c` mi ušetří psaní souboru." | `python -c` s českým textem **rozbil diakritiku** → skript tvrdil **„ten řetězec v souboru není"**, ačkoli v něm je | `dsh-prostredi` **§3d to říká doslova** („kde je český text, piš skript do souboru") — a stejně jsem to udělal. Vzniklo z toho hledání **vady souboru, která neexistovala** |
| **158** | „Když hlavička tvrdí neznámé jméno repa, brána spadne na TÉ větvi." | Fixtura **neměla soubory na disku**, takže `exit 1` šlo z §6 („`README.md` neexistuje"), **ne** z chybějícího tvrzení. A mutace M1 vypadala, že **NEFUNGUJE** — protože brána spadla i s ní | `overovani` **§10.1**: `exit 1` **ze špatného důvodu**. Oprava: fixtura má soubory na disku **a** přibyla kontrola „a NENÍ to kvůli chybějícímu souboru" |
| **159** | „Ověřím, že se mutant liší od zdravé kopie." | Porovnal jsem **soubor sám se sebou** — obě strany čtly tentýž (už přepsaný) soubor → **falešná CHYBA** | Obsah zdravé kopie se musí uložit **PŘED** přepsáním. Táž třída jako „dvě měření z téhož místa" (`overovani` §9.2) |

> **⚠ POUČENÍ, KTERÉ JE CENNĚJŠÍ NEŽ TY ČTYŘI:** **test H70 našel DRUHÝ výskyt
> téže vady, který neznal ani P14, ani zadání** — na **řádku 210**
> (`', '.join(j for j, _ in zivy)`). Kdo vadu hledá **čtením**, najde jedno
> místo; kdo ji **ZAVOLÁ**, najde obě. To je celý smysl věty „test musí tu
> větev ZAVOLAT" — a je to zapsané jako nález **H80** (§2.9 kroniky).

### 8v. Omyly 160–168 — OVĚŘOVACÍ session 5. 10. 2026 (P16: PŘEMĚŘENÍ OPRAV P15)

**Devět omylů a osm z nich je v MĚŘIDLE, které jsem si psal sám** — třikrát
jsem kvůli nim málem zapsal **nález o cizím kódu, který neexistoval**. Záznam:
**§34**. Podpis je tentýž jako u celé kroniky: **měřil jsem něco jiného, než
jsem si myslel** — a počtvrté za sebou to bylo **proto, že jsem nezkontroloval,
KTERÝ výskyt vzor trefí**.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **160** | „Napíšu skript s českými uvozovkami v hlášení." | `SyntaxError: unterminated string literal` — **čtyřikrát** ve **třech** různých skriptech (A2, A3, A5). Pokaždé jsem opravoval jednu konkrétní řádku místo aby mě napadlo, že je to systémová past | Česká **zavírací** uvozovka se mi při psaní nahradila **obyčejnou** `"` → ta řetězec ukončí. `dsh-prostredi` **§4d** to popisuje („česká uvozovka v patcheru vypadá jako syntaktická chyba Pythonu") — a stejně mě to chytilo 4×. **Náprava, která fungovala:** po každém zápisu `ast.parse(..., filename=…)` jako první krok |
| **161** | „Plošný sken mi řekne, kolik výskytů vady `for j, _ in zivy` v stromě je." | Sken našel **4 soubory** — a **ani jeden** nebyl vada: byly to **komentáře, které vadu popisují**, moje vlastní mutantní kopie a syntetická fixtura | `overovani` **§3**: statická kontrola musí číst **KÓD, ne komentáře**. Oprava: `tokenize` rozdělí výskyty na komentáře/řetězce vs. kód, `ast` hledá smyčky. **Falešný poplach na správném kódu** je horší než slepé místo |
| **162** | „Když vadu vrátím do kopie a sken ji nenajde, je sken slepý." | Sken našel **0** — protože obě opravená místa jsou **generátorové výrazy** (`any(… for j in zivy)`, `join(j for j in zivy)`), tj. `ast.GeneratorExp`, a já hledal jen `ast.For`. **S vrácenou vadou bych tvrdil „vada zmizela"** | `overovani` **§7.14**: mutace musí změnit **měřenou podmínku**. Oprava: `ast.walk` musí vidět i `comprehension`. **Druhá polovina téhož:** první verze **vůbec nerozpoznala**, že mutant vadu má — a vypadalo to jako zelená |
| **163** | „Když `ast.parse` soubor přijme, soubor je v pořádku." | **6 živých `.py` souborů NEJDE ZKOMPILOVAT** (`from __future__ import annotations` po jiných příkazech) — a `ast.parse` je **přijme**, protože kontrolu umístění `__future__` dělá až **kompilátor**, ne parser | Nález **H85** vznikl **náhodou**, když jsem na ty soubory pustil `compile()`. Do té doby jsem měl „syntakticky v pořádku" z AST — což je **slabší predikát**, než jsem si myslel |
| **164** | „Vypíšu prvních pár nálezů, zbytek je stejný." | `str(nepars[:3])` **zamlčelo** tři další nekompilovatelné soubory — a já málem zapsal „živý strom je čistý, vadné jsou jen v `_archiv`" | **Zkrácený výpis měřidla je tichá lež.** Oprava: nový skript `p16a4d-nekompilovatelne.py` vypisuje **všechny** nálezy a rozděluje živý strom vs. `_archiv` |
| **165** | „Srovnám své exit kódy s uloženým během P15." | Všech **34** řádků hlásilo **cizí** exit kód (`dnes=1` u každé brány) — ve členu seznamu jsem použil `x["exit"]`, kde `x` byl **zbytek z předchozí smyčky** | `overovani` **§10.7** („nástroj umí tisknout jiný čítač, než jak se jmenuje"). Oprava: brát z `{popis: exit}` **podle jména**. **A poučení:** rozdíl „34 z 34" byl **falešný** — po opravě jsou rozdíly **tři** |
| **166** | „Gates jsou zelené od P15, takže červená `n1`/`validate-all` je nález o projektu." | Byl to **můj vlastní identifikátor**: v `p16e-zaznamy.py` jsem měl proměnnou **`okolí`** (s diakritikou) → `hl-rizika-jazyka.py` správně spadl na „IDENTIFIKÁTOR (pravidlo je zakazuje): 1" → a s ním `n1-over-inventar` i `validate-all` | **Téměř jsem z toho udělal nález o neidempotenci běhu bran.** Zachránila to **izolace po jedné bráně** (`_analyza/p16b2-idempotence.py`): po přejmenování na `text_kolem` je `hl-rizika-jazyka` **exit 0**, `n1` **exit 0**, `validate-all` **✓ VŠE V POŘÁDKU**. **Vlastní stopa v cizím stromě vypadá jako vada cizího kódu** |
| **167** | „1,58 MB je 1,58 MiB." | Nezávislý součet dal **1,503 MiB**, ale **1,576 MB (10⁶)** — tvrzení P15 je v **desetinné** jednotce a **je správné** | Málem **falešný nález o čísle**. `overovani` §9.4: „naměřeno 0" i „naměřeno jinak" mají víc významů. Oprava: měřidlo vypisuje **obě jednotky** |
| **168** | „`git show ce49234^:soubor` mi dá stav před P15 — zadání to tak říká." | `git.cmd` (batce přes `cmd.exe`) **žere `^`**: `ce49234^` se tiše změní na `ce49234` → vrátí stav **PO** commitu a rozdíl „0 změn" je **pravdivý omylem** | Nález **H89**. Zachytil jsem to **před** použitím (`rev-parse --short` dal `ce49234`, `git.exe` dal `c620a06`). **Kdyby ne, zapsal bych „konstanty jsou shodné s HEAD" na základě srovnání souboru se sebou samým** — přesně vada, kterou jsem u testu P15 kritizoval. Správně `~1` nebo `git.exe` |

> **⚠ A JEDNA VĚC, KTERÁ OMYL NENÍ, ALE VYPADÁ JAKO ON:** dva meziběhy `g3`
> skončily s **nenulovými exity** (`n1-over-inventar` = 2, `validate-all` = 1).
> **Příčina byla zastaralý inventář** — a ten byl zastaralý **proto, že jsem do
> stromu přidal své skripty** (H60/NA1: otisk je z OBSAHU). Po regeneraci
> inventáře a po opravě omylu **166** je `g3` **34 bran / 0 nenulových** a
> `validate-all` **✓ VŠE V POŘÁDKU**. **Kdo měří cizí strom, musí nejdřív
> pojmenovat svou vlastní stopu v něm.**

### 8w. Omyly 169–172 — AKČNÍ session 5. 10. 2026 (P17: OPRAVA NÁLEZŮ H84–H89)

**Čtyři omyly a všechny čtyři jsou v MĚŘIDLE, které jsem si psal sám** — a tři
z nich v **jednom** souboru (`_analyza/test-h87-klasifikator.py`). Záznam:
**§35**. Podpis je stejný jako u §8v: **nezkontroloval jsem, co moje vlastní
měřidlo doopravdy dělá** — a málem jsem podle toho zapsal, že brána **H87 není
opravená**, ačkoli opravená byla.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **169** | „Napíšu skript s českými uvozovkami v hlášení — vždyť je to jen text." | `SyntaxError: unterminated string literal` v `_analyza/p17b1-nekompilovatelne.py:82` (a spadlo to **hned při prvním spuštění**) | **Tatáž past jako omyl 160** (P16) — a zapsaná je i v `dsh-prostredi` §4d. Česká **zavírací** uvozovka se při psaní nahradila **obyčejnou** `"`, ta ukončila f-string. Zachytil to `ast.parse` **před** spuštěním — což je přesně ta náprava, kterou si P16 zapsala. **Pravidlo tedy funguje; nefungovalo moje použití** |
| **170** | „Test mi řekne, které brány jsou mezi nezačatými." | Test hlásil **7 chyb** na bráně, která byla v pořádku — protože `_sekce()` bral `m.group(1)`, a to je v `nadpis_re` **POČET** (`(\d+)`), ne seznam položek | **Skupina 2, ne 1** — `nadpis_re + r"[^\n]*\n((?: …)*)"` má **dvě** skupiny. Zapsané to je v `test-h71-klasifikator.py:97` (a je to i v `AGENTS.md` jako past „nástroj umí tisknout jiný čítač, než jak se jmenuje"). **Opsal jsem techniku a nedovodil jsem, co má kolik skupin** |
| **171** | „Ověřím, že živý `g3` už whitelist neobsahuje, hledáním v souboru." | Našlo se to — **v komentáři, který vadu popisuje** (`# … (`_VLASTNI_HLASENI`)`). Test proto hlásil chybu **nad správným kódem** | `dsh-prostredi` §1 a `overovani` §3: **statická kontrola musí číst KÓD, ne komentáře.** Oprava: `bez_komentaru()` odstraní komentářové řádky **před** hledáním. **Ironie:** týž soubor o dvě kontroly výš použil `bez_komentaru`-logiku jen mimochodem — a stejně mě to chytilo |
| **172** | „Když vrátím starou podmínku, mutant vykáže **3** nezačaté (2 správné + fixtura bez markeru)." | Mutant vykázal **4** — protože v živém `g3` už konstanta `_VLASTNI_HLASENI` **není** (smazal jsem ji), takže mutant vrací jen `len(...) <= 1` **bez whitelistu** a mezi nezačaté se objeví i fixtura **s markerem** | **Mutace, která nedělá to, co jsem si myslel.** Oprava kritéria: `len(nz_m) > 2` (a důvod je v komentáři u kontroly). Poučení: **když mutuju kód, musím mutovat proti JEHO dnešnímu stavu** — ne proti stavu, který jsem měl v hlavě |

> **⚠ A jedna věc, která omyl NENÍ, ale vypadá jako on:** `g3` po opravě hlásí
> **`? BRÁNY, KTERÉ BĚŽELY, ALE NEVYKÁZALY ČÍTAČ (1)`** — kdežto P16 měřila
> **2**. Není to regrese: zavedl jsem **třetí stav** (NA33) a **zúžil** jeho
> definici na `nalezeno == "—"` (brána, jejíž **vzor nic nenašel**). Brány se
> **vzorem `None`** (`validate-all`, `tsc`) hlásí `— (brána nemá čítač)`, což je
> **přiznaný stav**, ne vada (nález NA23 z 2. 10. 2026) — a do třetího stavu
> proto **nepatří**. Rozdíl je ve **definici**, ne ve stavu projektu.

### 8x. Omyly 173–185 — OVĚŘOVACÍ session 6. 10. 2026 (P18: PŘEMĚŘENÍ PRÁCE P17)

**Třináct omylů a DESET z nich je v MĚŘIDLE, které jsem si psal sám** — a pět
z nich v **jednom** souboru (`_analyza/ov-g-h92-sken.py`, který měl pět verzí).
Záznam: **§36**. Podpis je stejný jako u §8v a §8w: **nezkontroloval jsem, co
moje vlastní měřidlo doopravdy dělá.** Dva z nich (`174`, `181`) málem vedly
k zápisu, že **P17 má vadu** — a přitom vada byla **moje**. A **`184` je regrese
naopak: rozbil jsem bránu, která do té chvíle procházela** — chytil to `g3`.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **173** | „Vyměním v klasifikátoru `g3` poslední větev za délkové pravidlo a test zčervená." | Chování se **nezměnilo** a test hlásil „mutace NEDETEKOVÁNA" — protože jsem **jen přejmenoval seznam podpisů** (`_PODPIS_CHYBEJICIHO_SOUBORU` → `_MUT`) a **přejmenoval i jeho použití** | **Mutace, která se neprovedla, tvrdí totéž co mutace, která projde.** Oprava: před každou mutací ověřit, že se text SKUTEČNĚ změnil (`h2 != h`) **a** že mutuju CHOVÁNÍ |
| **174** | „Když uberu podpis `No such file or directory` ze seznamu, fixtura D propadne mezi »běžela«." | Neubralo se **nic** — seznam podpisů **není jeden na řádek**, v živém `g3` jsou **tři podpisy na jednom řádku** | Dvě verze mazání (naivní `replace` s 4 mezerami i regex `^\s*"…",\n`) odebraly **NULA** položek. **A i kdyby jeden ubrat šlo, nestačilo by to:** výstup Pythonu nese **dva** živé podpisy současně (`can't open file` **i** `No such file or directory`) — naměřeno |
| **175** | „`_PARENT` je RODIČ repa, takže `_PARENT / 'uo-shadows'` vede na sourozence — H92 je falešný popis a ty tři soubory jsou v pořádku." | **Není.** U souboru v `tools/` je `parents[1]` = `tools/..` = **ROOT REPA**, ne jeho rodič. Naměřeno instrumentovaně: `_PARENT = E:\Workspaces\forge-orchestra`, a `_PARENT / 'uo-shadows'` = `…\forge-orchestra\uo-shadows` → **NEEXISTUJE** | **Přečetl jsem KOMENTÁŘ v preludiu** („`tools/` je primo v koreni repa, takze _PARENT = root repa"), vyložil jsem si ho **obráceně** a **nechal se jím utvrdit** — místo abych proměnnou změřil. O dva odstavce výš jsem si přitom sám napsal, že se hodnota má měřit. **Komentář, který si odporuje s kódem, je horší než žádný** → komentáře v těch třech souborech jsou teď opravené |
| **176** | „Izoluju běh `git worktree` do `E:\Workspaces\_ov-scratch`." | Tím jsem **kontaminoval vlastní počty**: `rglob` z `E:\Workspaces\forge-orchestra` vidí i `\_ov-scratch\forge-orchestra` (vnořený pracovní strom), takže se strom **počítá dvakrát** | Naměřeno: brána NA32 hlásila **167** souborů, kdežto můj skener **163** — zdroj rozdílu jsem musel dohledat. Worktree patří **MIMO měřený strom** (a do gitignorované `*-scratch/`) |
| **177** | „Test zčervená, když se změní výsledek klasifikátoru." | Nezčervenal: porovnával jsem **POČET** „nezačalých" (**2 vs 2**), ale mutace **přesunula JINOU bránu** mezi stavy | Táž past jako „klíč je v kopii, ale na jiném kroku": **neporovnávej součty, porovnávej PRVKY.** Oprava: množiny `nezacaly`/`bez_citace` místo čísel |
| **178** | „Stav návrhu NA23 přečtu jako 4. sloupec tabulky." | NA23 je **`APLIKOVÁNO`**, ale můj parser řekl „bez stavu" — protože **buňky samy obsahují `\|`** (vzor `NALEZENO (\d+)\|VŠE V PO`), takže `split('\|')` posune indexy | **Falešný nález o správném záznamu** (přesně to, před čím varuje `overovani`). Oprava: stav hledat v **celém řádku**; `NEOVĚŘENO` vyhrává |
| **179** | „Napíšu sken H92 s hledáním `.parent.parent / 'uo-shadows'`." | **0 nálezů a 57× „SPRÁVNĚ"** — hledaná věc je `_PARENT.parent` (proměnná), ne `.parent`, takže vzor nemohl zabrat | **Falešně ZELENÝ sken** (1. verze). Kdybych mu věřil, zapsal bych „H92 je vyřešený" |
| **180** | „Když je to v `tools/`, je `_PARENT / 'uo-shadows'` vada." | Označil jsem za vadu **i správné cesty** (`g3-brany.py`, `n32-kompilovatelnost.py`) — `_REPO`, `WS` a `KOREN` **nejsou totéž** co `_PARENT` | **Falešně ČERVENÝ sken** (2. verze). Obecné pravidlo „podle složky" neexistuje; rozhoduje **hodnota proměnné v tom kterém souboru** |
| **181** | „Když proměnnou vyhodnotím z její definice, mám jistotu." | Dvě další verze **neměřily nic**: `ast.walk` nad `BinOp` dal **62× „NEVYHODNOCENO"**, a `eval` preludia spadl u **všech** definic, protože prostředí nemělo **alias `_pl`** (`import pathlib as _pl`) → **48× „NEVYHODNOCENO"** | **Pátá verze** (eval preludia s aliasy) teprve měří. Poučení: **u skenu se počet „nezměřeno" počítá jako výsledek** — 62 nezměřených není „čistý strom" |
| **182** | „Změřím počty souborů jedním `python -c`." | Vyšlo **176 vs 176** (rozdíl 0) — protože jsem měl v množině překlep **`' .git'` s mezerou**, takže se `.git` nefiltroval a oba filtry daly totéž | Překlep, který **vypadal jako vyvrácení hypotézy**. Správně: rozdíl dělaly **2 soubory v `snapshot-*/`** (NA32 je počítá jako živé, protože vylučuje jen `_archiv`). Dvakrát jsem přitom sáhl po `python - <<'PY'` (heredoc v PowerShellu **neexistuje**) a po `python -c` s regexy (rozbije parser) — obojí je zapsané v `dsh-prostredi` §3f/§5b |

> **⚠ A co omyl NENÍ, i když to tak vypadá:** `diag-baseline.py` vypisuje
> `phash → None` pro červenou i modrou. **Není to vada:** `repo/.forge/baseline.py`
> má v docstringu naměřeno, že **jednolité obrázky** (std < 1,0) DCT zdegeneruje,
> a proto se u nich vrací `None` a porovnává se přesným `sha256`. Fixtura je
> 1×1 px plná barva — tedy přesně ten dokumentovaný případ. Zapsáno jako
> **neškodné, ale matoucí**.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **183** | „Doplním řádek 32 do tabulky sessions." | `edit` našel jako `old_string` **řádek `8x` v tabulce OMYLŮ** (§4), ne v tabulce sessions — takže **řádek 32 se vložil do tabulky omylů** (7 sloupců místo 5) **a souhrnný řádek `\| **celkem** \| …` se připojil NA KONEC řádku 32** (tedy **zmizel**) | **Dvě vady jedním zápisem** a **obojí tiché**: tabulka se nerozbila viditelně, jen měla o řádek víc a jiný počet sloupců; a `kronika-kontrola.py` to **nechytil** (počítal bloky omylů, ne řádky tabulky sessions). Našel to až **vlastní přepočet** (`| **celkem** |` se ztratilo). Oprava: `_analyza/ov-fix-kronika.py` (řádek 32 rozdělen, vrácen do tabulky sessions, `celkem` obnoven). **Poučení: `old_string` musí být na řádku JEDNOZNAČNÝ** — stejný text bývá ve dvou tabulkách |
| **184** | „Přepíšu zadání a hotovo." | **Přepsané zadání SHODILO bránu `zadání kontrola`** (`exit=1`), která předtím procházela (**P17: `OK`, otevřela 296**) — a to je **REGRESE, kterou jsem zavedl sám**. Příčina: do řádku „Stav obou repů při psaní:" jsem napsal `` `origin/main` = ce49234 ``, a parser té brány čte z TOHO řádku dvojice **`repo = <sha>`** → vylovil **vymyšlený repozitář `main`** a ohlásil „tvrzení, které se nepodařilo přiřadit k repu" | Chytil to **`g3`**, ne já — a to je přesně to, k čemu brány jsou. Oprava: řádek přeformulován (žádné `= <sha>` u `origin/main`); brána je **zase `OK`** a parsuje **právě dva** repy (`forge-orchestra`, `uo-shadows`). **Poučení: text, který vypadá jako strojově čitelný, strojově čitelný JE** — a vymyšlené jméno v něm brána vidí jako tvrzení o repu |
| **185** | „Vrátím zadání na stav z HEAD, aby byl strom konzistentní a ověřený." | `git checkout -- NEXT-SESSION-INSTRUKCE.md` **ZAHODIL EDITaci, která byla lepší než stav v HEAD** — přeformulované místo **„ověř `origin/main..HEAD` ŽIVĚ"** (to je ta verze, která **nestárne**) zpět na **„`origin/main..HEAD = 4`"** (to je ta, která **zastará dalším commitem**). Zahodil jsem tedy **správnou** verzi a nechal **zastaralou** | **Záměna „necommitnuté" za „throwaway".** `git checkout --` je **destruktivní**: neřeší, jestli je ta změna lepší nebo horší — jen ji smaže. Vzniklo to honbou za **konzistencí inventáře** (která je **obnovitelná** jedním příkazem), obětovanou za **ztrátu lepší formulace** (která obnovitelná nebyla). **Poučení: než zahodíš necommitnutou změnu, zeptej se, čím je ta změna HORŠÍ — a když není, commitni ji a přegeneruj inventář.** Cena konzistence je jeden příkaz; cena ztracené formulace je přemýšlet znovu |

### 8y. Omyly 186–193 — ROZHODOVACÍ session 6. 10. 2026 (P19: PUSH, H93, H94, ROZHODNUTÍ O `g3`)

**Devět omylů a VŠECHNY jsou v MĚŘIDLE, které jsem si psal sám** (proto je sloupec
„vypadalo jako nález o cizím kódu" nulový — nikoho cizího jsem neobvinil).
Záznam: **§37**. Podpis je stejný jako u §8v–§8x: **nezkontroloval jsem, co moje
vlastní měřidlo doopravdy dělá** — a tentokrát to bylo dražší, protože celá
session byla *měření cizí práce*. Tři věci stojí za zmínku zvlášť:
**`187` je přesně ta vada, kterou jsem v P18 kritizoval u P17** (kategorie
„tiše prázdná" → číslo vypadá jako měření), **`189` vyrobil soubor, který
nešel zkompilovat — a odhalila to brána NA32, kterou jsem měřil** — a **`194`
je táž vada zápisu, jakou má P18 zapsanou jako omyl 183** (edit trefil jinou
tabulku / jiný řádek, než měl).

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **186** | „Orchestra NEMÁ Pages — kontrola to potvrdí." | Kontrola hlásila **CHYBA**, i když orchestra Pages skutečně nemá: v **těle** odpovědi GitHubu je `status` **řetězec** (`"404"`), kdežto HTTP stav je **číslo**. Porovnání `body.status === 404` je proto **vždy nepravdivé** | **Falešný nález o cizím repu** (a nejcennější druhý půl: vypadal jako vada nasazení, ne měřidla). Oprava: rozhoduje **HTTP status z `fetch`**, ne pole v JSONu; tělo se vypisuje jako doplněk |
| **187** | „Kategorie `*-scratch` je prázdná — v pracovních kopiích žádné `.py` nejsou." | Bylo jich **19**. Vzor `-scratch$` přes **`re.match`** nesedne NIKDY ( `match` kotví na **začátek** ), takže kategorie zůstala prázdná a **19 souborů se tiše počítalo jako ŽIVÉ** | **Tichý falešný negativ uvnitř mého vlastního měřidla** — a to jsem v P18 u P17 kritizoval. Odhalilo to **křížové měření jiným nástrojem** (`Get-ChildItem … -Filter *.py` dal 18, můj skript 0). Oprava: `re.search` s explicitní kotvou; **a číslo kategorie se porovnává s nezávislým walkem** |
| **188** | „Kopie v scratchi se od živého souboru LIŠÍ (13 783 B vs 14 096 B)." | **Obsah je SHODNÝ** — rozdíl **313 bajtů = 313 konců řádků** (LF vs CRLF); `sha256` po sjednocení konců je **totožný** (`f67d2309e057f92b`). `git diff --no-index` byl **tichý**, což bylo první vodítko | **„Kdo měří na disku, najde vady, které neexistují"** — táž past, kterou má `AGENTS.md` u `core.autocrlf` („autorita je blob, ne velikost souboru"). Oprava: porovnávat **obsah s `\r\n` → `\n`** a rozdíl konců řádků **vypsat jako vysvětlení**, ne jako nález |
| **189** | „Odstraním z skriptu nepoužitý `import shutil`." | PowerShellové `Set-Content -Encoding utf8` zapsalo do **`.py` BOM** → soubor přestal být zkompilovatelný (`invalid non-printable character U+FEFF`) a **NA32 ho právem vykázala jako živý nekompilovatelný soubor**. Navíc můj regex na odstranění řádku **nesedl**, protože soubor má konce řádků LF a vzor měl `\r\n` (řádek tam zůstal) | **Nástroj na editaci se stal zdrojem vady kódu.** Pravidlo „do `.ps1` patří BOM" platí **obráceně pro `.py`** — a `Set-Content` **není** bezpečný editor kódu. Oprava: zápis zpět přes `edit` (bez BOM) + **sonda na první tři bajty**. **A je to důkaz, že NA32 funguje** — chytila to hned |
| **190** | „Vložím mutant za první řádek, který nezačíná `#` ani třemi uvozovkami." | Mutace se vložila **DOVNITŘ docstringu** (řádek uvnitř řetězce taky nezačíná `#`) → `compile()` ji **přijal**, tj. **mutace se vůbec neprovedla** a test „prošel" ze špatného důvodu | Pojistka `compile` musí mutant **ODMÍTNOUT** to zachytila (`compile odmítne=False`). Oprava: brát **první TOP-LEVEL příkaz z `ast`** a vkládat za jeho `end_lineno` |
| **191** | „Vygenerovaný harness dám do `_analyza/p19-scratch/`." | Harness si cesty odvozuje z **umístění souboru** (`WS = parents[1]`), takže v podadresáři ukazovalo `WS` na `_analyza` a souhrn spadl na `FileNotFoundError` → **klasifikace vyšla PRÁZDNÁ** a **každá mutace pak vypadala „odhalená"** | Táž past, kterou má **P18** zapsanou u izolace („worktree musí ležet ve správné hloubce, jinak se změní `_REPO.parent`"). Zachytil to **guard „čtení výstupu funguje"**, který jsem si tam dal — bez něj bych zapsal, že mutace měření prokázaly |
| **192** | „Porovnám výsledek mutace se zdravým stavem." | Porovnával jsem **`sorted(list) != set`**, což je **VŽDY pravda** → „mutace odhalena" prošlo i tam, kde se nic nezměnilo. Druhá polovina téhož: smyčka pro M2/M3 měla **jeden** prvek se dvěma jmény, takže kontrolovala **jen M3** a M2 se nezměřila vůbec | **Dvě vady v jednom testu**, obě tiché. Oprava: uvnitř držet **množiny** (tisknout setříděné seznamy) a smyčku psát po jednom jménu |
| **193** | „Do generovaného harnessu vložím vzor čítače `r\"(\\d+) kontrol\"`." | Do kopie se zapsalo `r"(\\d+) kontrol"` — vzor na **literální zpětné lomítko**, který nikdy nesedne. Zdravá brána s čítačem pak vypadala jako **brána bez čítače** a `g3` (správně, podle nového pravidla) skončil `exit 1` | **Tři úrovně escapování** (Python řetězec → zápis do souboru → regex). Zachytil to **test sám** (kontrola „zdravý stav → exit 0" zčervenala). Oprava: vzor skládat z **raw** řetězce, kde je vidět, kolik lomítek vznikne |

| **194** | „Doplním řádek 33 do tabulky sessions v kronize." | Místo **vložení nového řádku** jsem **nahradil začátek řádku 32** — čímž vznikl **jeden obří řádek** (33 + zbytek 32) a **řádek 32 zmizel**; navíc vyšlo pořadí **33 před 32** | **Táž třída jako omyl P18 `183`** (edit trefil jinou tabulku / jiný řádek). Zachytil to **vlastní přepočet** (`| **32** | …` na řádku chybělo a řádek měl 8 sloupců místo 7). Oprava: **nejdřív vrátit prefix řádku 32**, pak **vložit 33 ZA jeho konec** (kotva = unikátní konec předchozího řádku). **Poučení: „vložit řádek" není „nahradit řádek" — a kotva musí být KONEC předchozího, ne začátek následujícího** |

> **⚠ A co omyl NENÍ, i když to tak vypadá:** `zadání kontrola` končí v `g3`
> **`exit=1`** — a **není to vada**: zadání je **záměrně zakotvené na commitu,
> na kterém se měřilo** (nález **NA31**), takže po každém novém commitu hlásí
> „přibylo commitů". Zapsáno jako **očekávaný nenulový exit** (a je to přesně
> ten případ, kvůli kterému `g3` o červených branách **nerozhoduje** — §37.4).

### 8za. Omyly **211–213** — ROZHODOVACÍ session 6. 10. 2026 (P22: DOPSÁNÍ ZÁZNAMŮ, KTERÉ P22 NEZAPSALA)

**Tyhle tři omyly NEVZNIKLY v kódu — vznikly v ZÁPISU do kroniky** (a to je
téma, kterým se P22 celou dobu zabývala). Všechny tři odhalila **brána**
(`kronika-kontrola.py`), **ne autor** — a to je i důvod, proč se sem dopisují
až teď: bez zápisu by nebyly vidět vůbec.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **211** | „Typ session `prováděcí` brána uzná.“ | `kronika-kontrola.py:374` zná **pět** typů (`akční`, `plánovací`, `ověřovací`, `analýza`, `rozhodovací`) a `prováděcí` mezi nimi **není** → `2 řádků session nemá uvedený typ`, `exit 1` | **Slovník brány jsem neotevřel.** Vymyslel jsem si typ podle sebe a zapsal ho jako fakt — táž třída jako „předpoklad zapsaný jako kontrola“ (omyl **195**) |
| **212** | „Název sekce si v zápisovém skriptu napíšu z hlavy (`## 4. Evidence omylů`).“ | Sekce se v P19 **přečíslovala** (`§3 Počty omylů` / `§4 Evidence omylů`); skript hledal kotvu, která **v dokumentu je**, ale **ne tam, kde jsem myslel** — a zapsal jinam, než měl | **Kotva opsaná z paměti místo z dokumentu.** Naměřeno už dřív jako past „kotva, která usne“ (§21.4) — a stejně se to stalo znovu |
| **213** | „Skript si živý soubor načte sám, je to jedno.“ | Skript dostal **cestu argumentem** (fixtura), ale **vždy četl živý soubor** — takže měřil něco jiného, než co mu bylo zadáno, a **na fixtuře by hlásil o živém stromě** | **Vstupy se mají číst TAM, KAM UKAZUJÍ, ne tam, kde je po ruce.** Táž třída jako `kronika-kontrola.py`, který bere cesty argumenty právě proto (ř. 52) |

**Poučení (a je to totéž, co hlásá `REVIZE-PRACOVNIHO-RITUALU.md` §3.4):**
**zápisy do dokumentů se dělají PROGRAMOVĚ** (`p21-zapis-kroniky.py` obstál
napoprvé) — ruční editace řádků delších, než je okno čtení, vyrobí chybu, kterou
**vidí jen brána**. Dvě z těch tří chyb (211, 212) jsou přesně to.

### 8z. Omyly 195–210 — ROZHODOVACÍ session 6. 10. 2026 (P20: `g3` SOUDÍ ČERVENÉ, BOM V `.py`, TICHÁ DÍRA V H79)

**Jedenáct omylů a DESET z nich je v MĚŘIDLE, které jsem si psal sám** (sloupec
„vypadalo jako nález o cizím kódu" je proto **nulový** — nikoho cizího jsem
neobvinil). Záznam: **§38**. Podpis je stejný jako u §8v–§8y: **nezkontroloval
jsem, co moje vlastní měřidlo doopravdy dělá** — a tentokrát se to projevilo
**čtyřikrát na TÉŽE věci**: neshodě mezi tím, co jsem si myslel, že brána měří,
a tím, co měřila.

**Tři věci stojí za zmínku zvlášť:**

* **`195` je PŘEDPOKLAD místo měření** — do měřidla jsem napsal, že
  `ast.parse()` BOM **přijme**, protože to „přece dělá tokenizér jinak než
  `compile()`“. Naměřeno: **odmítne ho stejně**. Kdybych to nechal projít,
  zapsal bych do projektu nepravdu o chování Pythonu a příští session by
  hledala rozdíl mezi NA32 a H79 na **špatném místě**.
* **`201` je vada, kterou našel STARŠÍ doklad, ne můj nový test** — do svého
  verdiktu nad červenými jsem započítal i brány **deklarované** jako „běžela bez
  čítače“. Odhalil to `p19-d-kontroly.py` (P19). **To je přesně důvod, proč se
  doklady nemažou** — a proč má smysl, že je P20 musela opravit, ne zahodit.
* **`206` je TÁŽ VADA ZÁPISU, jakou má P19 zapsanou jako omyl `194`** (a P18
  jako `183`): do kroniky jsem vkládal řádek **přes kotvu, která se mi načetla
  ZKRÁCENÁ** (2000 znaků), takže jsem **nahradil celý řádek 33 zkráceným textem**
  a pak do něj „vrátil“ druhý výskyt téhož (řádek narostl z **4286 na 6149**
  znaků). Opraveno **programově z blobu v `HEAD`** — a to je poučení: **když je
  řádek delší, než se vejde do kontextu, nesmí se použít jako kotva.**

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **195** | „`ast.parse()` BOM PŘIJME, jen `compile()` ho odmítne — v tom je rozdíl mezi NA32 a H79." | **Obě ho odmítnou** (`invalid non-printable character U+FEFF`) — jdou přes **týž tokenizér** (`ast.parse` = `compile(..., PyCF_ONLY_AST)`). Rozdíl mezi branami tedy **nevzniká tam** | **Předpoklad zapsaný jako kontrola** (`zk(chyba_ast is None, …)`) — spadla mi vlastní kontrola (1 chyba z 9). Oprava: tvrzení **přeměřit** a teprve pak zapsat; rozdíl se hledá ve **ČTENÍ souboru** (`utf-8` vs `utf-8-sig`), ne v parseru |
| **196** | „Zkontroluju, že je fixtura vykázaná v kategorii `*-scratch`." | `„*-scratch“ in zmineno`, kde `zmineno` byl **SEZNAM** (`[l for l in …]`) — test na **prvek seznamu**, který **nemůže projít** | **Kontrola, která nemá jak projít** (obráceně S27). Vypadala jako nález o správném kódu. Oprava: `in` nad **řádkem**, ne nad seznamem |
| **197** | „Fixturu zadání složím v `python -c`." | **Zpětný apostrof je v PowerShellu ESCAPE znak** — z `` `forge-orchestra` `` se stalo `orge-orchestra`, takže brána **správně** hlásila „zadání netvrdí žádný commit“ | **Vada ZÁPISU, která vypadá jako vada BRÁNY.** Dvě kola jsem hledal chybu v kódu, který fungoval. Pravidlo `dsh-prostredi`: skript patří do **SOUBORU** |
| **198** | „Vzor na kotvu napíšu jako `r\"\\`\"`." | Zpětný apostrof **žádnou escape sekvenci NEMÁ** → v řetězci zůstaly **dva znaky** a vzor hledal text, který v dokumentu není; `re.sub` **nic nenahradil** a měřil se ORIGINÁL | **Tichá nula uvnitř mutačního testu.** Zachytila to až kontrola „mutace se SKUTEČNĚ provedla“ |
| **199** | „Změním kotvu na živý `HEAD`." | Změnil jsem jen **PRVNÍ** výskyt na řádku — ale ten řádek nese i `origin/main` = **`19a2195`**, takže vzniklo zadání s **dvěma rozcházejícími se tvrzeními** | Opět bych „opravoval“ bránu, která měřila správně. Fixtura musí být **CELÁ a vlastní** |
| **200** | „V testu nahradím blok `BRANY` svými fixturami." | Nahradil jsem `BRANY`, ale **nechal deklaraci** `OCEKAVANE_NENULOVE` s `zadání kontrola` → ta se stala **VISUTOU** a `g3` skončil `exit 1` **z jiného důvodu, než test měří** | `overovani` §10.1: `exit 1` ze špatného důvodu. Opraveno v `p20-a-kontroly.py` **i ve třech dokladech P19** |
| **201** | „Verdikt nad červenými postavím nad `selhalo`." | `selhalo` je **KAŽDÝ** nenulový exit — takže sem spadne i brána **deklarovaná** (`OCEKAVANE_BEZ_CITACE`) a brána, která **vůbec nezačala**; `g3` pak padal **za to, co sám deklaroval** | **Vada v PRODUKČNÍM kódu** — a našel ji **starší doklad P19**, ne můj nový test. Oprava: brány pokryté jinou sekcí se z posuzování **odečítají** |
| **202** | „Jméno brány do deklarace opíšu." | Jméno se **programově vytahovalo z téhož literálu** — a přesto nesedělo (dvě kola hledání). Řešení: klíč brát **z téhož literálu, který jde do `BRANY`**, a porovnávat **po kódových bodech** | **Dva řetězce, které vypadají stejně, stejné nejsou.** „Vypadá to stejně“ není měření |
| **203** | „Opravím řádek v `.py` přes `Set-Content`." | Zastavil jsem se **v poslední chvíli** — zadání to výslovně zakazuje a je to **omyl 189 z P19** (BOM → nekompilovatelný živý soubor) | Omyl **„v poslední chvíli“**; zapsaný proto, že pravidlo bylo **v zadání, ne v hlavě** |
| **204** | „Sloupec ‚kontroly‘ v přehledu dokladů se načte vzorem." | Vzor `VÝSLEDEK: N kontrol, M chyb` **neodpovídá** formátu `VÝSLEDEK D: kontrol 39, chyb 0` → u **všech 19** dokladů vyšlo `—` | **Metrika, která tiše nic neměří, vypadá jako naměřená nula.** Oprava: číst POSLEDNÍ výskyt kteréhokoli ze známých tvarů |
| **205** | „Porovnám klíče tím, že si je vypíšu vedle sebe." | Dvě kola jsem je porovnával **OČIMA** (`repr` vedle sebe). Teprve výpis **kódových bodů** (`U+%04X`) ukázal, že klíče jsou **SHODNÉ** — a vada je jinde | **„Vypadá to stejně“ není měření.** Porovnání řetězců patří programátorovi, ne oku |
| **206** | „Vložím řádek 34 do kroniky s kotvou na řádek 33." | Řádek 33 se mi načetl **ZKRÁCENÝ** (2000 znaků), takže jsem **nahradil celý řádek** zkráceným textem a „vrácením“ do něj vložil **druhý výskyt téhož** (4286 → **6149** znaků) | **Táž třída jako P19 `194` a P18 `183`.** Oprava: řádek vzít **z blobu v `HEAD`** a vložit programově; **kotva nesmí být řádek delší, než se vejde do kontextu** |
| **207** | „Řádek 33 je `head_lines[32]` — vždyť je to session 33." | `head_lines[32]` je **session 2**. **Číslo session NENÍ číslo řádku** | **Táž třída jako „různé čítače nesou stejné jméno“** (`dsh-prostredi` §5). Zastavil to **assert uvnitř skriptu**. Oprava: hledá se **podle OBSAHU** |
| **208** | „Zkontroluju, že se změnil jen řádek 33 — porovnám `soucasne[i]` s `po[i]`." | Hlásilo **650 změněných řádků**. Řádky se nezměnily — byly **POSUNUTÉ** o vložený řádek; indexové srovnání je mimo o jedna | **Hromadné „poškození dokumentu“, které neexistuje** — a kdybych mu uvěřil, „opravoval“ bych zdravou kroniku. Oprava: srovnávat se **správným posunem** |
| **209** | „Kotvu zadání do dokladu napíšu natvrdo (`19a2195`)." | Po přepsání zadání na nový živý `HEAD` (`b781c84`) doklad spadl **na SPRÁVNĚ aktualizovaném dokumentu** | **Táž třída jako H102** (doklad tvrdící zastaralé číslo). Oprava: kotva se **VYTAHUJE Z DOKUMENTU**, neopisuje. Doklad **8/0** |
| **210** | „Doklad je hotový, když projde." | Po přepisu zadání hlásil `p20-d-doklady.py` **2 červené místo 1** — a ten druhý byl **můj vlastní doklad** (209), ne H103 | Doklad závislý na **STAVU dokumentu** zastará **spolu s ním**. To se má **čekat**, ne „opravovat“ dokument zpátky |


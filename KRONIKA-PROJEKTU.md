# KRONIKA PROJEKTU — celý příběh, jak se co našlo, pokazilo a opravilo

**Co tenhle dokument JE:** **jediné trvalé místo, kde žije CELÝ příběh projektu**
— session po sessioni, nález po nálezu, omyl po omylu. Je to **paměť**, ne stav.
**Co NENÍ:**

| Dokument | Co je | Vztah ke kronice |
|---|---|---|
| `HANDOFF.md` | **stav** jedné session — při každém předání se přepisuje | kronika se **nikdy nepřepisuje**, jen doplňuje |
| `PREDAVANI-SESSION.md` | **postup** předávání | kronika je **důkaz**, že se postup dodržel |
| `SKILLY-AKTUALIZACE.md` | **co se zapsalo** do skillů (vlny 1–13) | kronika se na něj **odkazuje**, neopisuje ho |
| `NEXT-SESSION-INSTRUKCE.md` | **zadání** pro příští session | kronika je **historie zadání** |
| `PLAN-DALSI-KROK.md` | **plán** | kronika je **historie plánů** |

> **PROČ TO EXISTUJE (naměřeno 2. 10. 2026):** do téhle chvíle se příběh projektu
> dal přečíst **jen z `HANDOFF.md`, který se přepisuje** — takže „co se stalo"
> přežilo **jen v odkazech a v `SKILLY-AKTUALIZACE.md`**. Uživatel to pojmenoval
> přesně: *„vím, že už se něco částečně dělá, ale nemám přehled."*
> **Přehled nebyl nikde na jednom místě — a to je vada předávání, ne dojem.**

**Pravidlo údržby:** **každá session na konci doplní JEDEN řádek** do tabulky
níž (datum · session · co udělala · co naměřila · co pokazila) a **případné
nové nálezy/omyl/poučení** do příslušné evidence. **Nic se nemaže.**
Kontrolu provádí `_analyza\kronika-kontrola.py`.

---

## 1. Přehledová tabulka — celý projekt (řádek = jedna session)

| # | Datum (UTC) | Session | Typ | Co udělala | Co naměřila (hlavní číslo) | Omyly |
|---|---|---|---|---|---|---|
| **1** | 30. 9. 2026 | (před řetězem) | akční | Vznik orchestra: conductor + agenti, F0, hra `uo-shadows`, PR #17–#26 | — | 1–4 |
| **2** | 1. 10. 2026 dop. | `7cd67c66`+ | analýza | **Hloubková analýza architektury orchestra** — třídy selhání **S1–S18**, 16 oddílů | `grep` tool **0** vs. Python walk **80** absolutních cest v 59 souborech | — |
| **3** | 1. 10. 2026 | migrace | akční | Migrace datového adresáře `E:\DSH` → `E:\DeepSeekHarness-data` | **14 souborů přepsáno** junctionami (past `Target` u hardlinku) — obnoveno z karantény | 14 |
| **4** | 1. 10. 2026 odpoledne | ověřovací | ověření | Ověření práce podle `PROMPT-NOVA-SESSION.md` — 10 měřitelných bodů | „42 volání `test(`" vs. skutečných **36/36 testů** — statická metrika lhala | 14–23 |
| **5** | 1. 10. 2026 večer | `eb127abd`-1 | akční | **A1–A4** (ukotvení stavu: `done` jen při `ok && merged`), **Z1–Z8** (hranice jazyka) | schéma `conductor` **39 sloupců**, ne 32; přejmenováno **11 míst** | 5–13 |
| **6** | 2. 10. 2026 05:45 | `7cd67c66` | analýza | **2. kolo hloubkové analýzy** — „stav, který si systém hlásí sám", **S31–S37** | 5 tvrzení analýzy **zastaralo** vlastní prací session (nález N8) | — |
| **7** | 2. 10. 2026 06:26 | `7db45275` | akční | Zápis jazykových změn, commit, `SKILLY-AKTUALIZACE` | inventář jazyka: **2 002 nálezů** | 24–28 |
| **8** | 2. 10. 2026 07:11 | `eb127abd`-2 | akční | Dotažení A1–A4/Z1–Z8, brány `a1-a2-over`, `a3-over`, `n8-*`, **F0.5** | `a1-a2-over` chytila **2 z 5** vad → přepsána na **23 kontrol** | 5–13 |
| **9** | 2. 10. 2026 08:39 | `8b85a526` | akční | Sloučení PR #28–#31 (HUD, ukládání, těžba) | otevřených PR **0 z 31** | 29–33 |
| **10** | 2. 10. 2026 09:18 | `365e06eb` | ověřovací | Ověření zadání analýzy; 12/12 bodů §7.2 | → vznik `PREDAVANI-SESSION.md` (dva kroky: plánovací → akční) | 34–39 |
| **11** | 2. 10. 2026 10:12 | `84bb93e1` | akční | Push orchestra, ověření granulí **A3/A5**, nálezy **N1/N3** | `FORGE_ATTEMPT` je v herním repu na **jiném kroku** než v šabloně | 29–33 |
| **12** | 2. 10. 2026 10:33 | `79a47900` | plánovací | Ověření **11 tvrzení** akční session, plán | „brána `check-schema` je červená" → **není**, jen se špatně volala | 34–39 |
| **13** | 2. 10. 2026 11:31 | `df1cbb23` | akční | **Úkoly A–D + B1**: falešný poplach v testech, `combat.gd`, C1 `a3-kontrola`, C2 inventář, dvě brány mimo sandbox, **B1 nasazen** (deploy #32) | testy **59 → 64 kontrol, 0 selhání**; cooldown **10/0** | 40–50 |
| **14** | 2. 10. 2026 12:17 | `9717c52c` | **plánovací** | **Ověření práce #13 vlastním měřením** (Úkoly 1–6) + 5 rozhodnutí + tahle kronika | Úkol A: **59/0 → 64/0 → 65/1 → 65/0**; M3 **NECHYCENA**; **#146 nepadla na testu, ale na TPM 8000 < 14 398** | **51–59** |

| **15** | 2. 10. 2026 13:0x | **plánovací** | **Ověření práce #13** (hlavní úkol: jsou změny v klonu?) + **Úkol 1 zadání** (změřen prompt vs. TPM) + oprava měřidla `g3` | Úkol A: **59/0 → 64/0 → 65/1 → 65/0** (vlastní běh); Úkol B: **M1/M2/M4/M5 chyceny, M3 ne**; vstup do Aideru **≈ 11 207 tokenů** vs. Groq **TPM 8 000**; `validate-all` **✓ VŠE V POŘÁDKU** | **61–68** |
| **16** | 2. 10. 2026 13:29 | (pokračování #15) | **plánovací → akční** | **Push obou repů** (rozhodnutí uživatele) + **odpověď na otázku „není 8k málo?"** — a dvě vady, které ta otázka odhalila | `orchestra` **`593e25c`**, `uo-shadows` **`c40bdd5`**; `release.yml` **#69 success**, CI **#102 success**, Pages `last-modified` **13:18:06**; **tři různá `Requested`** (14 398 / 14 377 / 14 402) místo jednoho | **69** |

| **17** | 2. 10. 2026 16:1x | **akční** | **Granule `tests.harness`** (rozhodnutí uživatele) + lék na **H12**: atrapa v rozporu → **M3 chycena**; ruční seznamy nahrazeny **projitím složky**; úklid worktree | M3 s vrácenou vadou: **65/2** (dřív **nechycena**); projití složky **405 souborů** (dřív 127 ze seznamu); skilly **12 z 12** (dřív 5); roadmapa **22 granul**, lint beze změny (**14 problémů**) | **72–80** |
| **18** | 2. 10. 2026 14:5x UTC | **plánovací** | **Ověření práce #17** — její **dvě nová měřidla a jedno přepsané**; 5 měření z §3 zadání + nezávislý přepočet + posouzení H14–H17 | základ `pres-level` je **61/0 a 61/1** (ne 65 — jiný čítač); s vráceným `> 0` M3 **NEPROJDE** (**65/1** — lék má **dvě nezávislé části**, zadání se mýlilo); `g1` vidí nový soubor (**419 → 422**); brána kroniky spadne na kopii (**99 vs. 9**); nálezy **H18–H22** | **81–86** |

| **19** | 2. 10. 2026 18:1x | **akční** | **Dokončení auditu dokumentace** (`ZADANI-DOKONCENI-AUDITU.md`): snapshot, tři vady a jejich měřidla, sběrný běh všech bran | `HANDOFF.md` **NEDOTČENÝ** (SHA-256 shodný se snapshotem, jen `mtime`); `ag-mutace.py` **2/2 chyceno** a **nově v `g3`** (29 → **30 bran**); `audit2b` **0 rozchodů u `granulí`** (bylo 11 falešných); `audit2a-schema.py` → **`exit 0`** — **ale kritérium zadání bylo nesplnitelné, viz H24** | **87–96** |

| **20** | 2. 10. 2026 16:4x | **plánovací (ověřovací)** | **Ověření práce #19** — 9 tvrzení ze zadání spuštěním, **13 opatření** z auditu (stav + vlastník), rozhodnutí **NA17–NA23** | **7 z 9 tvrzení sedí**, 1 **zastaralé** (hash `HANDOFF.md`), 1 **nepřesné** (`g3` má **2** nenulové exity, ne 1); **hlavní riziko VYVRÁCENO**: `audit2b` **NENÍ slepý** na append-only (mutačně: rozchody **29 → 30** v nedatovaném oddílu); **nový nález H29**: `audit2b` má **25 falešných rozchodů z 31** a u `„32 sloupců"` si **odporuje s `audit2a`**; opatření **9 z 13 nehotovo**, **2 nemají vlastníka** (H26); brána diakritiky **57 → 305** souborů (opatření 6) | **97–101** | **Navíc naměřeno a opraveno:** `audit2b` měl **zkrácený výpis** (`histor[:40]`) a shazoval tím svého ověřovatele (**H32**, omyly **102–104**, pět měření na jednu příčinu); vzor pro `granulí` chytal **12 ze 14** reálných tvarů → **14 ze 14**.

| **21** | 2. 10. 2026 20:1x | **akční** |
| **22** | **3. 10. 2026** | **akční (typ A)** | **„Konec měřidel, práce na hře"** (`ZADANI-A-KONEC-MERIDEL.md`): stav hráče, který jiné komponenty **už volaly** (`assist.gd`, `economy.gd`), oživení mrtvé kontroly nad hráčem, srovnání roadmapy s `origin/main`, měření hypotézy „bez měřidla = 0–2 omyly" | testy hry **65 → 89 kontrol, 0 selhání**; `_dukaz-assist.gd` **exit 1 → 0**; **mrtvá izometrická větev** — hráč chodil **1:1 podle obrazovky** (sklon 0) místo **2:1 po dlaždicích** (sklon **0,5**), rozhodl uživatel; roadmapa: **2 falešná `done`** opravena, **2 chybějící** doplněna, **5 `size_lines`**; **hypotéza NEPOTVRZENA: 11 omylů** (čekalo se 0–2) | **113–123** | **Oprava pěti měřidel** (`ZADANI-OPRAVA-MERIDEL.md`): `audit2b` **30 → 9 rozchodů** (registr bran, citace v uvozovkách, guard počtu), `g3` u `validate-all` → **`—`**, **13 bloků omylů** v bráně kroniky, **tři mutační testy** (bran bez důkazu **10 → 7**), hlavičky dokumentů **80 → 14** | Zadání tvrdilo **31** rozchodů a **25** falešných; naměřeno **30**, falešných **21** (a jinak rozdělených) — vstupní brána byla zelená, protože má mez `<= 35`; **8 vlastních omylů (105–112), 7 v měřidle** | **105–112** | **Nález navíc:** blok omylů zapsaný jako `### 24.16` (místo `### 8x.`) **neviděla žádná brána**; opraveno přejmenováním na `8l` a **kontrolou, která se ptá naopak** („má každý nadpis v dokumentu kotvu v bráně?") — ta do hodiny odhalila i blok `8k` |
| **23** | 3. 10. 2026 20:5x | **akční (typ B)** | **„DAG, kronika a souběh s granulami“** (`ZADANI-B-DALSI-SESSION.md`): commit a push práce z minulé session, rozhodnutí DAG u `entity.player`, **zrušení pevného seznamu bloků** v bráně kroniky, smlouva o pozici hráče | Push: `uo-shadows` `279f584` → **`ffe9bd8`**, `orchestra` `d1cde9b` → **`c2f730f`**; `CI (testy a build)` **#112 success**, `release.yml` **#75 success**, Pages `last-modified` **21:09:15**; **rebase bez konfliktu vyrobil rozbitý soubor** (2× `hp`, 2× `move()`, 2× `die()`) → vráceno ze zálohy (**H34**); brána kroniky **107/13 → 118/14** a už **nehledá bloky v pevném seznamu**; `s24` **12/12**, `t3` **8 případů** (nové mutace M6/M7); smlouva **§2.3** + `push_warning` v `save.gd`; testy hry **91/0** | **124–128** | **Nález H33:** orchestra dodala `world.nodes` jako **PRÁZDNÝ soubor** (0 B) a CI to nechytilo · **H35:** `_s25-sonda-id.py` tvrdila o bráně něco jiného, než brána hlásila („132“ vs. **118**) · **H36:** zadání tvrdilo, že `entity.player.api` závisí na `world.map` — **nezávisí** |
| **25** | **4. 10. 2026** 21:0x–23:4x | **akční (prováděcí)** | **PŘESUN NA `E:`** (kroky P0–P12 zadání): orchestra → `E:\Workspaces\forge-orchestra`, hra → `E:\Workspaces\uo-shadows` (sourozenec), Godot → `E:\Tools\godot\` (D7), projektové dokumenty + `_analyza\` **do repa a commitnuté** (D3), dokumenty stanice zůstaly (D6), **žádná junctiona** (P7). Cesty v kódu se **ODVOZUJÍ** (`__file__` / `import.meta.url`), ne přepisují; tři nástroje zapisující do hry mají `FORGE_HRA` s výchozí `..\uo-shadows` (D4). `AGENTS.md` **do obou repů** (P9) — orchestra ho neměla (`.git` True / `AGENTS.md` False) | orchestra **5 450 / 1 003,7 MB** · hra **1 787 / 16,1 MB** · Godot **2 / 172,7 MB** — **vše na bajt** (kopie → ověření → smazání zdroje, ne `/MOVE`); oba `.git` na nové cestě, stromy čisté, historie nedotčená · **12 bran z nového místa `exit 0`** (`over-dokumentaci` **67/0**, `kontrola-diakritiky` *otevřeno 150 z 194*, `over-skilly` **13/0**, `hl-rizika-jazyka` **0 vrácených**, `ag-over-cisla` **5/0**, `kronika-kontrola` **SEDÍ**, `handoff-uplnost` **83/83**, `hl2-kontrola` **10/10**) · `kontrola-driftu` **12 souborů, 1 známý rozdíl** (není regrese) · archivováno **317** jednorázovek do `_analyza\_archiv\` (D5) | **132–137** | **Nálezy H40–H47:** měřidlo, které měří práci, **měří i sebe** (176 → 177–182, roste s prací) · odvozené cesty jsou **většinou bezpečné** (255 souborů, jen **21** rizikových, z toho většina jen komentář) · **`r_PARENT` je platný Python** a `ast.parse` ho pustí (syntaxe ≠ smysl) · archivace rozbila **ruční seznam** brány (44 falešných chyb `neexistuje`) · **změna rozsahu měření vypadá jako vada kódu** (68 non-ASCII názvů byly jen stažené CI logy; ve zdrojovém kódu **0**) · brána měřila víc, než pravidlo říká (padala i na **porovnávaných literálech**) · **cyrilské `е` (U+0435)** v názvu proměnné (neviditelný homoglyf) · **jeden root pro tři různá místa** (kronika) · **vlastní omyl 137:** psal jsem česky **v identifikátorech** — našla to **brána**, ne já |
| **26** | **4. 10. 2026** 22:5x–23:5x | **plánovací (ověřovací)** | **OVĚŘENÍ PŘESUNU NA `E:`** (`NEXT-SESSION-INSTRUKCE.md` pro plánovací session): **10 tvrzení o stavu přeměřeno spuštěním**, **12 bran znovu spuštěno**, **4 mutační testy měřidel** (§2.3 zadání), **D1–D9 ověřena jako dodržená**, plošný sken cest (Python walk, ne grep) | **Hlavička NESEDĚLA:** orchestra `c3ee946` vs. živý **`dea6f5c`** (o **2 commity** napřed, `origin/main..HEAD` 4 → **6**) → **přeměřeno všech 10 tvrzení** · **jádro přesunu obstálo:** staré cesty **False**, `games\` **prázdný a bez vazby**, `.git`+`AGENTS.md` v obou repech, archiv **gitignorovaný** (`git ls-files` → **0**), `.secrets` **mimo git**, D7 `hra.cmd` **spuštěn — Godot naběhl** bez `FORGE_GODOT`, `FORGE_HRA` ve **3** nástrojích, `STANICE` **není mrtvá proměnná** (4/2/1 použití) · **11 z 12 bran `exit 0`** (jedno číslo časové: `149 z 193` vs. `150 z 194` kvůli `dea6f5c`) · **4 mutační testy: 4× brána SPADLA** → měřidla **nejsou oslepené** · **archiv 333 souborů** | **138–142** | **Nálezy H48–H56:** **`g3-brany.py` spouští 15 z 29 bran po STARÝCH cestách** (`orchestra/tools/...`) → **neběží**, a `exit=2` se čte jako „červená" · `tools\test-gitignore-tajemstvi.py` **ROZBITÝ** (`STANICE` nedefinovaná → `NameError`) a **v žádné bráně** · `tools\verify-setup.py` **pevná cesta na starý kořen** (6× CHYBI; **předpovězeno v N8, nikdo neměřil**) · **21 bran `g3` „červených" i s plným oprávněním** — 5 z nich chybějící `node_modules` · **skener čte jen `git ls-files`** → netrackovaný kód **nevidí** · `zadani-kontrola.py` **slepý na orchestra** (`"orchestra"` vs. `forge-orchestra`) → `exit 1` **ze špatného důvodu** · §29.5 **„vše `exit 0`"** vs. `kontrola-driftu` **`exit 1`** (správně) · **`Local-Deepseek` v 15 živých kódových souborech** (5 legit. D6 / 8 jednorázovek / 1 komentář / 1 vada) — §29.7 tvrdilo „1 soubor" · **`Get-PSDrive` je nespolehlivý v OMEZENÉM sandboxu, ne rozbitý** (s plným oprávněním hlásí správně) · **NA24–NA26 ROZHODNUTY** (potvrzeno / nepřevzato / potvrzeno) |



**Jak číst tabulku:** „Omyly" odkazuje na `HANDOFF.md` **§8** (tabulka je
společná všem sessionám, číslování jde průběžně). **Sloupec „Co naměřila"**
není hodnocení — je to **číslo, které šlo zopakovat**; u každého je v `HANDOFF.md`
příkaz, kterým vzniklo.

---

## 2. Evidence nálezů (N, H, S, V, P) — kde jsou a co s nimi

**Nálezy mají předpony podle toho, KDE vznikly** — a to je záměr, aby se daly
dohledat:

| Předpona | Kde vzniká | Kde je seznam | Stav |
|---|---|---|---|
| **S1–S37** | třídy selhání z hloubkových analýz | `ANALYZA-HLOUBKOVA-ORCHESTRA.md`, `-2.md` | část opravena (A1–A4, B1, Z1–Z8) |
| **N1–N10** | nové nálezy z provádění A1–A4/Z1–Z8 | `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` | N1, N3, N5, N7, N9 **opraveny**; N2, N4, N6, N8, N10 **otevřené** |
| **V1–V3** | vady **měřidel** nalezené při ověřování | `HANDOFF.md` §13 | opraveny |
| **P1–P3** | pasti prostředí (sandbox, temp) | `HANDOFF.md` §16.5, skill `dsh-prostredi` | P2, P3 vyřešeny |
| **H1–H7** | nálezy **této** řady ověřování (2. 10. 12:xx) | `HANDOFF.md` **§17.8** | H1 **uzavřen** (viz 2.2), H2/H3/H4/H5/H7 **otevřené** |
| **H8–H17** | nálezy dalších kol ověřování a provádění (2. 10. 13:xx a 16:xx) | `HANDOFF.md` **§18.11** a **§21** | H8, **H12, H14–H17 opraveny**; H9, H11, H13 **uzavřeny**; H10 **otevřeno** (blokuje NA14) |
| **H18–H22** | nálezy **ověření práce #17** (2. 10. 2026 14:5x) — tři z nich jsou **rezidua oprav H14/H15/H17** | `HANDOFF.md` **§22.5** | **všechny otevřené** — zadány akční session (`NEXT-SESSION-INSTRUKCE.md`) |

### 2.1 Nálezy H1–H7 (nejnovější, z ověření práce `df1cbb23`)

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H1** | `_analyza\c2-sonda-uvozovky.py` **neexistoval**, ačkoli na něj odkazovaly dva dokumenty (doklad, který se ztratil) | **obnoven** ověřovací session; nejasné, zda nebyl smazán úmyslně | akční session ověří |
| **H2** | Test Úkolu B **nedokáže rozlišit** „metoda první" od „vlastnost první" (mutace M3 nechycena) | **otevřeno** — lék změřen | granule `tests.harness` |
| **H3** | **Pět úloh v jednom tiku, všech pět selhalo** (#142–#146) | otevřeno | akční session (Úkol 1) |
| **H4** | `FORGE_PROVIDER: groq` + `FORGE_MODEL: openai/gpt-oss-120b` → Aider dostane `openai/openai/gpt-oss-120b` | otevřeno | akční session (Úkol 1) |
| **H5** | **Groq free TPM 8 000 < prompt 14 398 tokenů** → úloha u Groqu **nemůže uspět** | otevřeno, **nejdražší** (pálí pokusy) | akční session (Úkol 1) |
| **H6** | `HANDOFF.md` §16.9 tvrdilo „neproběhlo (prostředí): už nic" — a `baseline.py testy` v tom výčtu nebyl | **opraveno** v §17.5 | — |
| **H7** | Tvar smlouvy je v **nepushnutém** `docs/ARCHITEKTURA.md`, ale prompt granulе na něj agenta posílá | **zpřesněno** — prompt na ten dokument **neodkazuje** (H11); platí, že `games/uo-shadows/docs/ARCHITEKTURA.md` §2.1 je jen v pracovním stromě a `roadmap.json:3` se na něj odvolává | uživatel (push) |

### 2.2 Nálezy H8–H17 (z ověřování 2. 10., dvě kola: 13:xx a 16:xx)

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H8** | **`g3-brany.py` měl dvě brány, které měřily TOTÉŽ** — „check-schema (hra)" volala `validate-all.mjs --jen hra`, ale **`--jen` není přepínač** (0 výskytů v souboru, validátor **nečte `process.argv`**) → spustil se celý validátor, tedy **tatáž komanda jako „validate-all (CELEK)"** | **OPRAVENO** — brána teď volá `python orchestra/repo/.forge/check-schema.py games/uo-shadows` (jako `validate-all.mjs:194`) → `exit 0`, „Schéma je v souladu" | hotovo |
| **H9** | **Zadání i `HANDOFF.md` míchají „nepushnuto" a „necommitnuto"**: `uo-shadows` **JE pushnuté** (`194735d` na `origin/main`); 4 změněné soubory jsou **necommitnuté úpravy** | otevřeno — **push nestačí, musí se nejdřív commitnout** | uživatel (rozhodnutí o commitu) |
| **H10** | **Zadání „porovnej s limity poskytovatelů v `providers.json`" se nedá splnit** — v tom souboru **žádné TPM není**, jen poznámky o denních stropech. Jediné změřené TPM je **Groqovo (8 000)**, z logu běhu | otevřeno — **u ostatních poskytovatelů se „vejde / nevejde" tvrdit nedá** | uživatel / doplnit do `providers.json` |
| **H11** | **Prompt granulе `entity.player.api` NEODKAZUJE na `docs/ARCHITEKTURA.md`** (naměřeno: `grep` → 0), ačkoli to tvrdí zadání §2.4 i §17.8/H7. Smlouvu nese **prompt v roadmapě**, tedy **v repu** | **zpřesněno** — push je blokátor **dokumentace**, ne smlouvy | akční session |
| **H12** | **M3 zůstává nechycená** (mutace vypuštění větve `hodnota()` → 0 selhání), ačkoli se větev volá **2×**; obě větve vracejí totéž číslo | **potvrzeno vlastním měřením** (sonda: A 2×, B 9×; s rozpornou atrapou `damage = 13` vs. `33/1`) | granule `tests.harness` |
| **H14** | **Dvě brány měly v docstringu DOSLOVNOU ukázku rozbitého kódování** — a `AGENTS.md` to zakazuje (pravidlo vzniklo právě kvůli tomu). `oprav-ps1-kodovani.py` ji měl v hlášce, `over-dokumentaci.py` v docstringu | **OPRAVENO** — ukázky popsané **slovem** („z jednoho písmene s diakritikou se stanou dva znaky"). Našlo to **projití složky** v `g1-diakritika-novych.py` | hotovo |
| **H15** | **Brána diakritiky kontrolovala 5 z 12 skillů** — ruční seznam cest. Chyběl i `overovani`, do kterého táž session psala | **OPRAVENO** — skilly se procházejí (`~/.dsh/skills/*/SKILL.md`); **naměřeno 12 na disku = 12 otevřených** | hotovo |
| **H16** | **Mutační test kroniky neměl fixturu s tabulkou NÁLEZŮ** — testoval jen živý dokument, a ten ten tvar v době testu neměl → vada (54 omylů místo 10) **prošla testem** | **OPRAVENO** — `_analyza\t3-kronika-mutace.py`: fixtura má obě tabulky, **6 případů** (2 kontrolní + 3 vady + tvar); navíc našel **dvě další vady brány** (viz H17) | hotovo |
| **H17** | **`kronika-kontrola.py` měřila NULU tam, kde neměřila nic:** chybějící nadpis bloku → `blok()` vrátí `""` → `pocet_omylu("")` vrátí **0**, a to se vypsalo jako „skutečný počet omylů: 0". A blok, který v kronice **řádek nemá**, se tiše přeskakoval (`continue`) | **OPRAVENO** — tři stavy: chybějící **nadpis** i **koncová kotva** = `NEZMĚŘENO`; blok v `HANDOFF.md`, který v kronice chybí, je **ROZCHOD**. `%d` na `None` už neshazuje bránu tracebackem | hotovo |
| **H13** | **`providers.json` má o Groqu číslo, které už neplatí:** tvrdí *„jeden běh spálí ~6k"* → *„~33 běhů/den"*. **Naměřeno: ~14,4 tisíce na běh** (2,4× víc) → reálný odhad je **~13–14 běhů/den** | **otevřeno** — číslo v repu je **zastaralé měření** (táž třída jako N1) | akční session (§18.17) |

### 2.3 Nálezy H18–H23 (z ověření práce #17, 2. 10. 2026 14:5x UTC)

**Všechny jsou to vady MĚŘIDEL nebo DOKLADU — a všechny jsou doložené spuštěním**
(`HANDOFF.md` **§22.5**). Tři z nich (H18, H19, H20) jsou **rezidua oprav, které
byly prohlášeny za hotové** (H14, H15, H17) — to je nový a nepříjemný vzorec:
**oprava měřidla má taky slepá místa a nikdo je neměří.**

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H18** | **„Ruční seznam místo projití složky" zůstal ve DVOU branách, které #17 upravovala.** (a) `kronika-kontrola.py` má **pevný seznam 8 kotev** → omyly **24–28** (zapsané v `HANDOFF.md` **§13.2**) **nevidí**: brána i kronika hlásí **75**, dokument má **80 unikátních** — a po §8i **86**. (b) `kontrola-diakritiky.py` prochází **jen skilly**; dokumenty má v **ručním seznamu 54 cest** → **11 z 37** kořenových `*.md` **neotevře** (díru zavírá **jiná** brána, `g1`) | **otevřeno** — a proto je verdikt `NA15 = APLIKOVÁNO — celé` **nepřesný** | akční session |
| **H19** | **Reziduum H17: brána testuje PŘÍTOMNOST kotvy jiným predikátem, než jakým ji PAK HLEDÁ** (`od in hand` = kdekoliv v textu vs. `radek.startswith(od)` = začátek řádku). Když je kotva jen **citovaná v próze** (což se v tomhle projektu děje — omyl 76), vrátí brána prázdný výřez a vypíše **„v HANDOFF.md je 0"** — naměřenou nulu tam, kde blok **je**. Dosažitelné u bloků **8d** a **8g** (obě kotvy jsou v dokumentu **2×**) | **otevřeno** — naměřeno `v3-kronika-stavy.py`, případ `C5` | akční session |
| **H20** | **Reziduum H14: výjimka „soubor se vzorkem" je klíčovaná JMÉNEM seznamu a RUČNÍM seznamem souborů.** Vzor je `(ROZBITE\|rozbito)\s*=` (tedy `=` hned po jménu) plus `SAMOKONTROLA` = 3 ručně vyjmenované soubory. Naměřeno: legitimní definice vzorku pod jménem `VZOREK_SPATNE` **i** `ROZBITE_DVOJICE` → **`CHYBA … ANO (3 znaků)`, `exit 1`** — **falešný poplach na správném souboru** | **otevřeno** | akční session |
| **H21** | **Tři čísla v dokladu §21 a v `NA15` se nedají zopakovat:** (a) §21.6 „`mutace A (5 běhů)` → **61**" — ta brána spouští **JEDEN** mód a dává **59/0** (popisek „5 běhů" je nepřesný); (b) „**2 kontrolní**" případy → nástroj tiskne **3**; (c) „soubor má **1 205** řádků" → **1 204** (`split("\n")` past z `AGENTS.md`) | **otevřeno** — čísla se **nepřepisují**, jen se k nim píše správná hodnota | akční session |
| **H22** | **Čas v hlavičce zadání je mimo realitu o ~4,4 h:** tvrdí „**19:2x UTC**", soubor zapsán **14:48 UTC**. Táž záměna je v §21.8 („16:4x UTC" pro commit s časem **14:43+02:00**), ale **měřený** čas pushe (`14:43:10 UTC`) je správný | **otevřeno** — pravidlo „čas piš s měřením, ne odhadem" | akční session |
| **H23** | **Sedm odkazů ukazuje na špatnou sekci kroniky:** tabulka návrhů je v **§6**, ale **5 odkazů v `PREDAVANI-SESSION.md`** (řádky 84, 129, 286, 317, 334) a **2 v kronize** (§7 „Návrhy, které ještě nikdo neschválil", §8 „Nový návrh →") posílají do **§5** — což je **„Poučení"**. Session, která by postupovala podle §6.2 D, by návrh zapsala **do špatné tabulky** | **částečně opraveno** — 2 ukazatele v kronize opraveny touto session; 5 v `PREDAVANI-SESSION.md` čeká na rozhodnutí (**NA19**) | akční session |

### 2.4 Nálezy H24–H28 (z dokončení auditu dokumentace, 2. 10. 2026 18:1x–19:0x)

**Všechny jsou to vady MĚŘIDEL, DOKLADU nebo OPATŘENÍ — a všechny jsou
doložené spuštěním** (`HANDOFF.md` **§23**). Dva z nich (H24, H28) jsou
**vady ZADÁNÍ**, které se projevily až při provádění — a to je nový vzorec:
**zadání je taky měřidlo** (říká, co je „hotovo") a má tytéž pasti.

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H24** | **Zadání mělo u Úkolu 1 NESPLNITELNÉ kritérium a mířilo vedle.** Tvrdí: „číslo 39 je tam v přítomném čase a bez značky času → `audit2a-schema.py` je `exit 1`". **Naměřeno po provedení předepsané opravy: `exit 1` zůstal a 6 „rozchodů" — a ANI JEDEN nebyl tvrzení o dnešku** (1× citace `„32 sloupců"` v `AGENTS.md`, 1× datovaný záznam v kronize, 4× citace v tabulkách omylů `HANDOFF.md`). **A ta horší polovina:** vzor `(\d+)\s+sloupc` potřebuje jednotku **hned za číslem**, takže na skutečné tvrzení („správně je **39**") **vůbec nedosáhl** — brána u `AGENTS.md:62` hlásila „tvrdí 32", tedy četla **citaci**, a **vadu R1 nikdy neměřila**. `exit 1` byl **správný výsledek ze špatného důvodu** | **opraveno** — měřidlo přepsáno (mutačně **4/4**, vč. vrácení `39` bez značky času) a `audit2a-schema.py` → `exit 0`; **zapsáno jako past** (`AGENTS.md`, `overovani` §10.1–10.2) | tato session |
| **H25** | **`audit2b` má sám vadu, kterou vytýká `audit2-rozpory.py`.** Veličina `kontrol` (`(\d+)\s+kontrol`) srovnává čísla z **RŮZNÝCH BRAN**, které hlásí různé počty kontrol **SPRÁVNĚ** (23, 59, 60, 61, 65…) → **27 „rozchodů", z toho většina falešných**. Je to přesně ta past, kterou audit popsal u `audit2-rozpory.py` („různé brány hlásí různé počty kontrol správně") — a `audit2b`, který měl být tou lepší variantou, ji má taky | **otevřeno** — zadání žádalo opravit jen `granulí`; zbytek je **návrh NA22** | příští session |
| **H26** | **Dvě opatření auditu nebyla zadáním PŘIDĚLENA ŽÁDNÉ session.** `ZADANI-DOKONCENI-AUDITU.md` §6 posílá do session B opatření **6, 7, 8**, do C **4, 5**, do D **10, 12** — **opatření 2** (popisek v `ag-over-cisla.py`) a **3** (rozšířit `ag-over-cisla.py` na řádek 62) v tom výčtu **nejsou**. Opatření tedy **nejsou zamítnutá, jen bez vlastníka** — a to je horší, protože je nikdo neudělá a nikdo si toho nevšimne. **Opatření 2 jsem provedl** (patří k R1); **opatření 3 zůstává otevřené** | **opatření 2 hotové**, opatření 3 **otevřeno** | tato session (2) / příští (3) |
| **H27** | **Snapshot (opatření 9) ZNE Platnil baseline inventáře — sám sobě.** `audit-snapshot.py` kopíruje dokumentaci do `_analyza\snapshot-<čas>\`; `audit1-inventar.py` ty **kopie začal počítat jako dokumenty**: naměřeno **159 dokumentů místo 98**, **66 záloh místo 8**, „bez hlavičky" **116 z 159** místo **62 z 98**. Kdo by ta čísla četl jako stav dokumentace, **čte vlastní snapshot**. **Je to omyl 92** (vlastní) a zároveň **obecný nález**: opatření, které něco kopíruje, musí říct všem měřidlům, že je to kopie | **opraveno** — `audit1-inventar.py` vylučuje předponu `snapshot-`; inventář zpět na **101 dokumentů / 8 záloh** (101 = 98 + 2 nové dokumenty + 1 oddílový soubor) | tato session |
| **H28** | **Kritérium „porovnej `mtime` s 17:38" dalo NEPRAVDIVOU odpověď.** Zadání podle něj mělo rozhodnout, zda v `NEXT-SESSION-INSTRUKCE.md` pracuje jiná session. **Naměřeno:** `mtime` se změnil (17:38:17 → 18:32:22), **ale SHA-256 obsahu je ve DVOU snapshotech i na disku shodný** (`9c05c6b434d5d026…`, 17 841 B). `mtime` hnul **mutační test** `_analyza\zadani-mutace.py:50` (zapisuje a řádky 100/115/129 vrací), který spouští `audit6-brany-mutace.py`. **Kritérium by tedy tvrdilo „pracuje v tom souboru jiná session", což není pravda** — a žádná jiná session aktivní není | **zapsáno** — rozhodnutí se opřelo o **hash obsahu**; `NEXT-SESSION-INSTRUKCE.md` zůstal **nedotčený**, zadání je v novém souboru (`HANDOFF.md` §23.7). **Návrh NA20** | příští session |

### 2.5 Nálezy H29–H31 (z ověření práce #19, 2. 10. 2026 16:4x–17:1x)

**Všechny tři jsou nálezy o MĚŘIDLECH a o DOKLADECH** a všechny jsou doložené
spuštěním (`HANDOFF.md` **§24**). **H29 je nejcennější:** je to vada, kterou
audit vytkl jednomu nástroji — a **druhý nástroj, který měl být tou lepší
variantou, ji má taky**.

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H29** | **`audit2b` má 25 falešných rozchodů z 31 — a u téhož čísla si odporuje s `audit2a`.** Veličina `kontrol` (`(\d+)\s+kontrol`) srovnává **jedno číslo z jedné brány** (**65**, běh Godotu) se **všemi** výskyty v jádru — a jiné brány **správně** hlásí 19, 23, 38, 60, 63. **Naměřeno: `kontrol` 19 rozchodů, z toho 19 falešných.** A **4 rozchody u `sloupců`** jsou **citace** `„32 sloupců"`. **Rozhodující důkaz:** `PREDAVANI-SESSION.md:193` zní *„naměřeno u „32 sloupců" v `AGENTS.md`, nález N9"* — tedy **citace**; `audit2a-schema.py` **tentýž řádek** správně zařadí jako `[citace]` (citací=3), ale `audit2b` ho hlásí jako **ROZCHOD** (sloupců=4). **Dvě měřidla téhož čísla si odporují** — a to je **horší než jedno slepé**, protože není poznat, kterému věřit. Je to **přesně vada, kterou audit vytkl `audit2-rozpory.py`** | **otevřeno** — oprava je **Úkol 1** zadání `ZADANI-OPRAVA-MERIDEL.md`; **návrh NA22 potvrzen měřením** | akční session |
| **H30** | **`exit 1` brány nad VLASTNÍM VÝSTUPNÍM SOUBOREM — počtvrté.** `g1-diakritika-novych.py` skončil `exit 1` s jedinou vadou: `_tmp-g1.txt … NELZE PŘEČÍST: UnicodeDecodeError`. **Vadou byl výstupní soubor téže session** — PowerShell přesměruje výstup jako **UTF-16LE** (`dsh-prostredi` §5b) a `g1` ho **ohlásí jako vadu dokumentu**. **Audit tuhle past zná a má na ni nástroj** (`audit-cleanup.py`) a **sám ji zapsal** („první běh `g1` skončil `exit 1` a jediná vada byl můj vlastní výstupní soubor") — přesto se to stalo **znovu** | **zapsáno** — pravidlo: **výstup brány nepatří do složky, kterou brána prochází**; soubory uklizeny | každá session |
| **H31** | **PŘIZNANÁ MEZ opravy opatření 6: „co je záloha" se pozná podle JMÉNA, ne obsahu.** Při nahrazení ručního seznamu projitím složky (`kontrola-diakritiky.py`) se musí vyloučit **zálohy a snapshoty** — jinak by brána hlásila vadu na souborech, které **mají právo být rozbité** (jsou to snímky stavu PŘED opravou). Vylučuje se proto podle **jména** (`_zaloha*`, `*-pred-*`, `snapshot-*`) — a to je **ruční seznam o vrstvu níž** (`overovani` §9.5: výjimka klíčovaná jménem je ruční seznam). **Naměřeno:** vyloučeno **8 souborů**, viditelně ve výpisu. **Není to slepota** (brána počet vypisuje), ale **je to mez** a patří do zápisu | **zapsáno jako mez** — kdyby se zálohy začaly pojmenovávat jinak, brána **začne hlásit falešné poplachy** | každá session |

| **H32** | **`audit2b` měl ZKRÁCENÝ VÝPIS (`histor[:40]`) a shazoval tím svého ověřovatele.** Když session připsala do `HANDOFF.md` §24, spadl `audit2b-over.py` na `exit 1` s hláškou „HANDOFF.md:1201 `granulí` NENÍ v ZÁZNAMECH". **Nebyla to pravda.** Kotva je na **ř. 1201**, tedy **za** hranicí 40 záznamů, které nástroj vypisuje — **v ZÁZNAMECH JE, jen se to nevypíše**, a ověřovatel parsuje **stdout**. **Trvalo PĚT měření, než se příčina našla** (čtyři „opravy" mířily vedle: nadpisy `###`, velká písmena, vzor, filtr). Je to **táž past, kterou táž session zapsala o hodinu dřív jako vlastní omyl 97** — a spadla do ní znovu, v **cizím** nástroji. **Opraveno:** nový přepínač `--vsezáznamy`/`--vsechny-zaznamy` (mění **jen výpis, ne měření**), ověřovatel ho použije a **vypíše, že to bylo zkrácením**; `audit2b-over.py` → `exit 0` | **opraveno** — a zapsáno jako past: *měřidlo nesmí mít v cestě zkrácení, aniž to řekne*; kdo ho ověřuje, **čte nejdřív jeho VÝPISNÍ CESTU** | tato session |

### 2.6 Nálezy H33–H36 (z akční session 23, 3. 10. 2026 20:5x–22:0x UTC)

**Všechny čtyři jsou o DOKLADECH a MĚŘIDLECH** a každý je doložený spuštěním
(`HANDOFF.md` **§27**). Dva z nich (**H33**, **H35**) vypadaly jako „systém je
v pořádku“ — a byly to vady toho, čím se to měřilo.

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H33** | **Granule může být „dodaná“ a doručit PRÁZDNÝ soubor.** Granule `world.nodes` (PR **#32**, sloučeno 2. 10. 2026 18:12) doručila `scripts/world.gd` o **0 B a 0 řádcích** — `gather()`, `is_walkable()`, `nodes()`, `snapshot()` v něm **nejsou** a v `assets/levels/main.json` nejsou markery surovin. **CI to nechytilo**, protože prázdný soubor nemá žádné funkce, takže `check-wiring.py` **nemá co kontrolovat** (a `check-schema.py` se na `world.gd` neptá). `done` z toho, že se PR sloučil, tedy **není důkaz, že práce existuje** — je to tvrzení | **měřeno a zapsáno** — `world.nodes` i `world.map` mají v roadmape `done: false` a `done_note` s tímto měřením; **práce nezačata** | další session (implementace `world.gd`) |
| **H34** | **Rebase bez konfliktu umí vyrobit NEKOMPILOVATELNÝ soubor.** Obě strany měnily `scripts/player.gd`; git je sloučil **textově** a vznikly **duplicitní deklarace** (2× `hp`, 2× `move()`, 2× `die()`, 2× `add_item`) → v GDScriptu **parse error**. Rebase přitom hlásil `Successfully rebased`. Odhalila to až **kontrola duplicitních deklarací** (`^var\|^func\|^const` přes `scripts/*.gd`) — ne git a ne testy (ty by spadly až po commitu) | **opraveno** — soubor vrácen ze zálohy `zaloha-0e96d4a`, commit amendnut (`d6a0fd6` → **`ffe9bd8`**). **Pravidlo: „rebase prošel bez konfliktu“ u souboru, který měnily OBĚ strany, znamená „git to slepil“, ne „je to v pořádku“** | každá session, která slučuje |
| **H35** | **Měřidlo umí tvrdit nepravdu o JINÉM měřidle.** `_s25-sonda-id.py` měla **vlastní pevný seznam 8 kotev** a tiskla `CELKEM 132  ← to hlásí brána` — jenže brána bloky hledá v dokumentu (**14 bloků**) a hlásila **118**. Sonda tedy odpovídala na jinou otázku, než tvrdila, a číslo „132“ se tvářilo jako výstup brány | **opraveno** — sonda **pouští bránu a čte její čítač z běhu**; vedle toho staví své měření (množina unikátních id = **118**) | hotovo |
| **H36** | **Zadání tvrdilo něco, co v datech není.** `ZADANI-B-DALSI-SESSION.md` §2 píše, že `entity.player` **i** `entity.player.api` mají v `depends_on` `world.map`. `entity.player.api` má `core.attributes, core.skills, entity.item, world.level` — **`world.map` tam není**. Kdo by to nezkontroloval, „opravoval“ by **správná** data (tatáž past jako „32 sloupců“ v `AGENTS.md`) | **zapsáno** — opravený údaj je v `HANDOFF.md` §27.7; ověřeno parserem, ne čtením | hotovo |


---

### 2.6 Nálezy H37–H39 a past P4 (validace plánu separace, 4. 10. 2026)

**Všechny čtyři jsou naměřené spuštěním** — a tři z nich **mění tvar plánu**
přesunu na `E:`. Plný záznam: `PLAN-SEPARACE-WORKSPACE.md` **§10.7**.

| # | Nález | Stav | Kdo to řeší |
|---|---|---|---|
| **H37** | **ODVOZENÁ cesta je pro sken přímých cest NEVIDITELNÁ — a nástroje na ní stojí.** `install-into-repo.ps1:34` i `tools\test-local.ps1:39` berou `$ProjDir` z **rodiče repa** (`Split-Path $PSScriptRoot -Parent`) → `…\Local-Deepseek\projects\<Projekt>`, a **`projects\` v workspace NEEXISTUJE** (nikde ve stromě) → **oba nástroje dnes neběží vůbec**. Po přesunu by hledaly `E:\Workspaces\projects\` — **jinam, a pořád tiše** | **otevřeno** — rozhodnout `opravit` / `smazat`, **samostatně** (ne během přesunu); do zadání přesunu patří jako **nový krok P1b** (dohledat odvozené cesty) | uživatel + akční session |
| **H38** | **„Cena přesunu" byla měřená v jiné jednotce, než v jaké se práce dělá.** Sken počítá **výskyty** (208) — ale pracuje se **po souborech**: naměřeno **176 souborů** (117 `_analyza/`, 51 `orchestra/`, 5 root, 2 stanice, 1 hra, 1,2 výskytu na soubor). A **ani jedno krajní číslo není cena:** volný vzor **počítá prózu** (208), přísný (`Local-Deepseek` + oddělovač) **mine kořenové cesty** `Path(r"C:\…\Local-Deepseek")` (100) | **otevřeno** — P1 dělat **po souborech**; obě krajní čísla jsou v plánu §10.2b, aby je nikdo nebral jako jedinou pravdu | akční session (P1) |
| **H39** | **Plán navrhoval opravu, která by launcher ROZBILA.** `hra.cmd:13` má fallback na Godot v orchestra; plán ho chtěl nahradit `FORGE_GODOT` s odůvodněním „ta už existuje v `.forge\node\.env`". **Naměřeno:** existuje **jen v šabloně** (`orchestra\repo\.forge\node\.env`); **hra `.env` NEMÁ** (`.forge\node\` má 8 souborů, `.env` mezi nimi není) a `hra.cmd` **.env vůbec nečte** → v čerstvém klonu by proměnná byla prázdná a `hra.cmd` by skončil „Godot nenalezen" | **vyřešeno rozhodnutím** — Godot se stává **obecným nástrojem** `E:\Tools\godot\` a `hra.cmd` dostane **funkční fallback** + `FORGE_GODOT` jako override | rozhodnuto (D7) |
| **P4** | **`Get-PSDrive` u této stanice LHÁ o volném místě.** `Get-PSDrive E` → `Free=0 / Used=0`, kdežto `New-Object System.IO.DriveInfo('E')` → **810,8 GB**. A `Get-CimInstance Win32_LogicalDisk` i `Get-Volume` jsou v sandboxu **`Access denied`** — takže **vypadají jako potvrzení nuly**. Málem z toho byl blokující nález „přesun je nemožný" | **past prostředí** → patří do skillu `dsh-prostredi`; volné místo měř `System.IO.DriveInfo` | akční session + skill |
| **H40** | **Měřidlo, které měří práci, MĚŘÍ I SEBE.** Inventura cest měla dát „176 souborů" — naměřeno **177–182**, a číslo **roste s prací**: skripty této session samy obsahují `Local-Deepseek` (konstanta `_STANICE`). Každý nový nástroj si **připočte sebe**. „176" je proto **časové číslo**, ne vlastnost repa | **otevřeno** — počet se musí číst s časem a se seznamem vyloučených souborů | přesun na `E:` |
| **H41** | **Odvozené cesty jsou většinou BEZPEČNÉ — a plán to tvrdil obráceně.** `__file__` a `import.meta.url` odvozují od **souboru, který se přesunul s repem**, takže po přesunu sedí. Riziko je jen odvození **od rodiče repa** (`$PSScriptRoot\..`, `Split-Path -Parent`, `parents[>2]`). Naměřeno: **255 souborů** s odvozenou cestou, z toho **21 rizikových** — a z těch je většina jen **zmínka v komentáři** | **vyřešeno měřením** — krok P1b zúžen na „od rodiče" | přesun na `E:` |
| **H42** | **`r_PARENT` je PLATNÝ PYTHON a `ast.parse` ho PUSTÍ.** Nahrazení literálu `r"C:\..."` výrazem nechalo před výrazem viset prefix `r` → vzniklo **jméno proměnné** `r_PARENT`. **Syntaktická kontrola to NEODHALÍ** (syntaxe je v pořádku) — vada se projeví až `NameError` **za běhu**. Musela přibýt kontrola **podezřelých jmen** (a stejná past s `HRA = HRA / ...`, self-assignment) | **vyřešeno** — `p8m-kontrola-promennych.py` (použitá vs. definovaná proměnná); pravidlo: *syntaxe ≠ smysl* | přesun na `E:` |
| **H43** | **Archivace rozbila RUČNÍ SEZNAM brány.** `kontrola-diakritiky.py` má pevný seznam a jmenoval i **44 archivovaných** nástrojů → **44 chyb `neexistuje`** u souborů, které jsou v pořádku. Brána teď archivované **přeskočí a VYPÍŠE** (`ZMĚŘENO: otevřeno 150 z 194`) — ticho by bylo vada S27 | **vyřešeno** — viditelný přeskočený vstup, ne tichý | přesun na `E:` |
| **H44** | **Změna ROZSAHU MĚŘENÍ vypadá jako vada kódu.** `ag-over-cisla.py` měřil `rglob("*")` = vše na disku; po přesunu do repa do toho spadly **stažené CI logy** (`ci-rozbal*`, gitignorované) → hlásil **68 non-ASCII názvů** jako vadu orchestra. Ve **zdrojovém kódu** (1444 souborů) je **0**; v **gitu** (652) **0** | **vyřešeno** — měřidlo se ptá na zdrojový kód, ne na cokoli na disku | přesun na `E:` |
| **H45** | **Brána měřila VÍC, než pravidlo říká.** `hl-rizika-jazyka.py` padal na **každý** neočekávaný nález — tedy i na **porovnávané literály** (`x[2] == "granulí"`) a texty hlášek, které diakritiku mít **MAJÍ**. Pravidlo přitom zakazuje jen **identifikátory** | **vyřešeno** — padá jen na skutečných identifikátorech; textové nálezy hlásí zvlášť | přesun na `E:` |
| **H46** | **CYRILSKÉ `е` (U+0435) v názvu proměnné.** `hl-neanglicky-v-kodu.py` měl `v_tridе` — poslední znak **cyrilský**, tedy **neviditelný homoglyf**, který vypadá přesně jako latinské `e`. Kód fungoval (definice i použití měly týž znak), ale jméno **není ASCII** | **vyřešeno** — přejmenováno na `v_tride` | přesun na `E:` |
| **H47** | **Jeden root pro TŘI různá místa.** `kronika-kontrola.py` ověřoval všechny `.md` odkazy pod jedním kořenem, ale kronika odkazuje na **tři** místa: **repo** orchestra, **hru** (sourozenec) a **stanici** (dokumenty, které zůstaly). Po přesunu → **5 falešných chyb** `neexistuje`. A historické citace (`games/uo-shadows/docs/...`) se **NEPŘEPISUJÍ** — jsou to záznamy | **vyřešeno** — tři kořeny + historická citace se ověřuje na **dnešním** místě | přesun na `E:` |

### 2.7 Nálezy H48–H56 (z OVĚŘENÍ přesunu, 4. 10. 2026 22:5x–23:5x, plánovací session)

> **Všechny naměřené, žádný odhad.** Záznam s důkazy: `HANDOFF.md` **§30**.
> **Pět z nich (H48–H53, H55) je OTEVŘENÝCH** — opravuje je akční session
> podle `NEXT-SESSION-INSTRUKCE.md` (Úkoly A–F).

| # | Nález | Stav |
|---|---|---|
| **H48** | **`_analyza/g3-brany.py` spouští 15 z 29 bran po STARÝCH cestách.** `WS` je dnes kořen repa, ale seznam `BRANY` má **11 literálů** `orchestra/tools/...` z doby, kdy orchestra bydlela v podsložce. Brány tedy **vůbec neběží** a `exit=2` (z `can't open file`) se čte jako „červená". **Důkaz:** `g3-brany-vystup.txt` obsahuje 15 sekcí s `python: can't open file 'E:\Workspaces\forge-orchestra\orchestra\tools\...'`. **Proč to nikdo neviděl:** `g3` je **přehled, ne brána** (nemá `sys.exit`), a §29.5 spustilo 12 bran **přímo**, ne přes `g3` | **otevřeno** — Úkol A |
| **H49** | **`tools/test-gitignore-tajemstvi.py` je po přesunu ROZBITÝ.** `WS = pathlib.Path(STANICE)` → **`NameError: name 'STANICE' is not defined`** (řádek 43). Soubor má na řádku 5 správně odvozenou `_PARENT`, ale **nikde ji nepoužívá** — P8 přepsal hlavičku a **zapomněl přejmenovat použití**. Cesty níž jsou navíc ve starém tvaru (`WS / "orchestra" / ...`, `WS / "games" / ...`). **A není v žádné bráně** — `git grep` v `g3`, `validate-all.mjs` i `over-dokumentaci.py` → **0 výskytů**. Je to omyl **133/H42** („syntaxe ≠ smysl") **znovu**, protože kontrola podezřelých jmen (`p8m`) je **jednorázová, ne trvalá** | **otevřeno** — Úkol B |
| **H50** | **`tools/verify-setup.py` má pevnou cestu na starý kořen.** `W = r"C:\Users\Ssevc\Local-Deepseek"` → `orchestra`, `games`, `games/uo-shadows` hlásí **CHYBI**; `HANDOFF.md`, README orchestra a `.forge/roadmap.json` → `No such file`; **`NEJAKE PROBLEMY`**. **⚠ Předpovězeno v §2.6 (N8) a nikdo to neměřil:** *„po separaci by hlásil 6× CHYBI"* — **stalo se přesně to**, ale protože nástroj **není v žádné bráně**, zůstalo to jen v textu. **Předpověď bez měření po provedení je jen text** | **otevřeno** — Úkol C |
| **H51** | **21 bran `g3` je „červených" i s PLNÝM oprávněním — a není to kód.** Po opravě H48 bude potřeba rozlišit **skutečnou vadu** od **„neproběhlo (prostředí)"** (`overovani` §7.13). Už dnes je vidět, že **5 z nich** padá na `node:internal/modules/cjs/loader:1433 \| throw err` — tedy **chybějící `node_modules`**, ne vada kódu. Kdo je bude opravovat jako kód, opravuje **něco, co nikdo neměřil** | **zapsáno** — rozlišit při opravě A |
| **H52** | **Skener `hl-neanglicky-v-kodu.py` čte JEN soubory z gitu** (`soubory(repo)` = `git ls-files`). **Netrackovaný kód je pro jazykovou bránu neviditelný.** Doloženo: dočasný soubor v kořeni repa s `def změř(...)` dal **0 nálezů** (v inventáři o něm **ani slovo**). **Proč je to vada:** brána se používá **před commitem** — a kontrolovat se má **právě to, co v gitu ještě není**. Naměřeno na vlastním příkladu: **omyl 137** (`def změř`) našla brána **až po commitu**. **Druhá polovina téhož:** mutace vložená do **netrackovaného** souboru **změří nulu** a vypadá jako slepá brána (stal se mně — **omyl 139**) | **otevřeno** — Úkol E |
| **H53** | **`_analyza/zadani-kontrola.py` je SLEPÝ na orchestra.** Slovník z hlavičky staví **správně** (`{'forge-orchestra': 'c3ee946', 'uo-shadows': '869dce8'}`), ale srovnává ho s klíčem **`"orchestra"`** (`REPA`). `tvrzene_head.get("orchestra")` → **`None`** → vypíše `? orchestra: zadání netvrdí žádný commit` a **orchestra se vůbec neporovná**. **Past, která se nesmí splést:** skončil `exit 1` a jeho verdikt („zadání je zastaralé") byl **náhodou správný** — ale **ne z toho důvodu, kvůli kterému existuje**; se **správnou** hlavičkou by spadl stejně. Je to `overovani` §10.1: **`exit 1` ze špatného důvodu** — a protože byl červený, **nikdo nehledal, že je slepý** | **otevřeno** — Úkol D |
| **H54** | **§29.5 má nadpis „vše `exit 0`", ale `tools/kontrola-driftu.mjs` končí `exit 1`.** Je to **správně** — nástroj hlásí rozdíl („Spusť s `--sync`"). **Číslo `12 souborů, 1 rozdíl` i verdikt „není regrese" sedí.** Nesedí jen **společný nadpis** tabulky — táž třída jako „jeden čítač nese jiné jméno". **Není to vada práce, je to nepřesnost dokumentu** | **zapsáno** — zpřesnit v §29.5 |
| **H55** | **`Local-Deepseek` je v 15 ŽIVÝCH KÓDOVÝCH souborech, ne v 1.** §29.7 tvrdí *„zbývá 1 soubor: `install-into-repo.ps1`"*. **Přeměřeno** (git-trackované, kódové přípony, zvlášť archiv): **5 legitimních** (`STANICE` = kořen stanice — D6), **8 jednorázovek P8** (`p1-*`, `p5-presun.py`, `p8*`), **1 komentář** (`install-into-repo.ps1` — §29.7 to popsalo **přesně**), **1 vada** (`verify-setup.py` → H50). **Číslo „1" tedy není nepravdivé o `install-into-repo.ps1`, ale je neúplné jako tvrzení o stromě** — chyběla **klasifikace**. **Pozor na druhou past:** `p1-inventura-cest.py` a `p1b-odvozene-cesty.py` mají `Local-Deepseek` **jako vzorek (regex)** — to je správně a nemazat | **otevřeno** — Úkol F |
| **H56** | **`Get-PSDrive` NENÍ rozbitý nástroj — je nespolehlivý v OMEZENÉM sandboxu.** Návrh **NA25** tvrdil, že `Get-PSDrive E:` hlásí `Free=0 / Used=0`. **V dnešním prostředí (plný přístup, `FullLanguage`) to NEPLATÍ:** `Free=869273522176`, `DriveInfo` → **809,6 GB**. **Přesné znění:** v režimu jen pro čtení běží PowerShell v **`ConstrainedLanguage`**, kde `.NET` statické volání **nejde** a číslo je **nula**; se širším oprávněním hlásí **správně**. **Není to vlastnost stanice, ale vlastnost OPRÁVNĚNÍ** — a poučení: *u měření závislého na oprávnění se musí zapsat i to oprávnění* (totéž jako NA23b: baseline nenulových exitů závisí na sandboxu) | **vyřešeno měřením** — mění NA25 |

---

## 3. Počty omylů — jediné místo, kde je vidět TREND

**Proč to tu je zvlášť:** `AGENTS.md` říká *„počítej, že i tvoje první číslo bude
někde mimo."* Tahle sekce to **dokládá čísly** — a je to jediné místo, kde je
vidět, **jestli se podíl vad měřidla zlepšuje**.

| Co | Naměřeno | Odkud |
|---|---|---|
| **omylů ve blocích, které brána ZNÁ** | **123** | `python _analyza\kronika-kontrola.py` — **15 bloků** (`1–13`, `8b`–`8o`); od 3. 10. 2026 je brána **hledá v dokumentu** (`bloky_omylu`), pevný seznam v ní **není**. ⚠ Do 2. 10. 2026, 20:3x UTC to bylo **75 v 8 blocích** — brána neznala `8i`/`8j` (nález **H18**, návrh **NA17**); čísla **75**, **91**, **96** i **99** byla **ve svém čase správná** (A2) |
| **omylů v blocích, které v dokumentu JSOU** | **123** | `python _analyza\s24-meridla-over.py` (sekce F4) — **15 bloků**; brána je hledá v dokumentu a kontrola se ptá **obousměrně** (blok bez řádku v kronice i řádek v kronice bez bloku). ⚠ Do 3. 10. 2026 tu stálo „13/13, 0 mimo kotvu“ — a **nebyla to pravda**: `8n` kotvu neměl (kontrola to hlásila `exit 1`) |
| **omylů celkem v `HANDOFF.md` (unikátní id)** | **123** | `python _analyza\_s25-sonda-id.py` — **množina id**, ne řádky. ⚠ Dřív **96**; **+3** dodal blok `8l` (102–104) a **+8** blok `8m` (105–112), **+11** blok `8n` (113–123), **+5** blok `8o` (124–128). ⚠ Sonda od 3. 10. 2026 **čte čítač brány z jejího BĚHU** — dřív měla vlastní pevný seznam 8 kotev a tiskla „CELKEM 132 ← to hlásí brána“, což o bráně **nebyla pravda** (brána hlásí 118) |
| **z toho vad MĚŘIDLA** | **101 = 82 %** | ruční klasifikace u každého omylu (sloupec „Jak to vzniklo") — **aktualizováno 3. 10. 2026** (bylo 90 = 84 % ze 107; předtím 75 = 82 % z 91); **není to mechanické číslo**, je to ruční čtení |
| **z toho vypadalo jako nález o CIZÍM kódu** | **34** | tamtéž — bloky `8k`, `8l` i `8m` měly **0** a blok `8n` měl **3** (obě session dělaly ověřování a opravu měřidel, ne vývoj) |
| **bloků omylů** | **18** (`1–13`, `8b`–**8r**) | tamtéž; **+ §13.2** (omylů 24–28) je **mimo tuhle tabulku** — viz odstavec níž |
| **omylů ve blocích, které brána ZNÁ** — měřeno **4. 10. 2026** | **137** | `python _analyza\kronika-kontrola.py` — **18 bloků**; **+5** dodal blok **`8r`** (138–142, plánovací ověřovací session) a **+9** bloky H40–H47 · ⚠ Číslo **123** v řádcích výš bylo **ve svém čase správné** (3. 10. 2026, 15 bloků) — **nepřepisuje se**, jen se vedle něj staví dnešní (A2) |

> **⚠ DATUM SPOTŘEBY TOHOHLE ODSTAVCE (doplněno 2. 10. 2026, 20:3x UTC):**
> Čísla **75**, **85**, **91**, **96**, **10 bloků** a **8 bloků** v odstavcích
> níž jsou **ve svém čase správná** (A2) — naměřená 2. 10. 2026 dopoledne
> a odpoledne. **Nepřepisují se** (kronika je append-only záznam), ale **nejsou
> dnešní stav**: dnes je to **12 bloků / 99 omylů**. Historii nechte být
> a dnešní číslo berte z tabulky výš.

> **⚠ TŘI RŮZNÁ ČÍSLA TÉHOŽ JMÉNA (a je to nález H18, ne kosmetika).**
> „Kolik je omylů" má **tři odpovědi** a každá je správná na jinou otázku.
> **Naměřeno znovu 2. 10. 2026 ve 20:3x UTC zadáním `ZADANI-OPRAVA-MERIDEL.md`
> (Úkol 2c), a to KAŽDÝM Z TOU TROJICE ZVLÁŠŤ:**
> **99** = kolik jich vidí brána (**12 bloků**, seznam `BLOKY` v bráně),
> **99** = součet počtů v tabulce níž (**12 bloků**),
> **99** = kolik je **unikátních id** v blocích (1–101 + 102–104, díry 24–28).
> **Že vyšla stejná tři čísla, NENÍ náhoda ani důkaz — je to konstrukce:**
> podbloky `8b`–`8l` obsahují **tytéž omyly** jako společná tabulka v §8
> (naměřeno: **57 id je v obou**), takže blok `1–13` je **jen řádky mezi
> `## 8.` a `### 8b.`** a zbytek společné tabulky se do součtu **NESMÍ přičíst**.
> **Kdo sečte řádky všech tabulek, dostane 153** — tedy číslo, které
> neodpovídá na žádnou z těch tří otázek (omyl **86**: součet řádků není počet).
> **Původní (a dnes už neplatná) trojice** z 2. 10. 2026 dopoledne zněla
> **75 / 81 / 86** — rozdíl je **čas a tři neviditelné bloky**, ne nepravda.

> **⚠ POČTY SE POČÍTAJÍ, NEODHADUJÍ.** Naměřeno 2. 10. 2026 (omyl **60**):
> první verze tabulky níž měla u bloků **8d** a **8e** čísla **5** a **10** —
> byla to **špatná čísla**, protože je session napsala **odhadem z přečteného
> textu**. Odhalila to až **kontrola kroniky**, ne pozornost. Nástroj na
> přepočet: `python _analyza\s18-prepocitej-omyly.py --zapis`.
> **A podruhé totéž 2. 10. 2026 (ověření #17):** plán i zadání čekaly **74**,
> správně je **75** — číslo zestaralo o jeden omyl (**80**), ne že by bylo lživé.

**Podrobná tabulka po blocích** (číslování bloků odpovídá `HANDOFF.md` §8, 8b–**8r**):

| Blok | Session (kdy a jaká) | Počet omylů | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| **1–13** | 30. 9. – 1. 10. | **13** | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **8h** | akční 2. 10. 16:1x | **9** | **9** | **5** |
| **8i** | plánovací (ověřovací) 2. 10. 14:5x | **6** | **6** | **5** |
| **8j** | akční (dokončení auditu) 2. 10. 18:1x | **10** | **10** | **0** |
| **8k** | plánovací (ověřovací) 2. 10. 16:4x | **5** | **5** | **0** |
| **8l** | akční 2. 10. 20:0x | **3** | **3** | **0** |
| **8m** | akční 2. 10. 20:1x (oprava měřidel) | **8** | **7** | **0** |
| **8n** | akční **3. 10.** (typ A: „konec měřidel", práce na hře) | **11** | **8** | **3** |
| **8o** | akční **3. 10.** 20:5x (typ B: DAG, kronika, souběh s granulami) | **5** | **3** | **0** |
| **8p** | plánovací (validační) **4. 10.** (přesun pravidel + validace plánu separace) | **3** | **3** | **0** |
| **8q** | akční (prováděcí) **4. 10.** 21:0x–23:4x (**PŘESUN NA `E:`**) | **6** | **6** | **0** |
| **8r** | plánovací (ověřovací) **4. 10.** 22:5x–23:5x (**OVĚŘENÍ PŘESUNU NA `E:`**) | **5** | **5** | **3** |
| **celkem** | **16 bloků, 24 sessions** | **129** | **107 = 83 %** | **34** |

> **✅ VYŘEŠENO 3. 10. 2026 (session 23) — text níž je ZÁZNAM VADY, ne dnešní stav.**
> **Co z něj ještě platí:** popis příčiny (pevný seznam bloků) i zadání pro další
> session. ✅ **Obojí je provedeno:** brána bloky **hledá v dokumentu**
> (`bloky_omylu(hand)`), hlásí **118 ve 14 blocích**, `BLOKY = [...]` v ní **není**
> a `s24-meridla-over.py` je zelená (`exit 0`). A co je důležitější: **nový blok
> omylů teď z počtu vypadnout NEMŮŽE** — a když v téhle tabulce chybí jeho řádek,
> brána to ohlásí (dřív se ten směr neměřil vůbec).
>
> **⚠ SOUČET NENÍ DNEŠNÍ — a je to ZÁMĚRNÉ (doplněno 3. 10. 2026).**
> Session **22** připsala blok omylů **`8n`** (**11 omylů: 113–123**) a jeho
> řádek je v tabulce výš — ale **souhrnný řádek `celkem` i `BLOKY`
> v `_analyza\kronika-kontrola.py` zůstaly na `107` / `13 blocích`**, protože
> zadání `ZADANI-A-KONEC-MERIDEL.md` §5 to té session **zakazovalo** („NEOPRAVUJ
> MĚŘIDLA … ani kroniku" a „NEDOPLŇUJ … seznamy v branách"). **Naměřený důsledek:**
> `python _analyza\kronika-kontrola.py` dál hlásí **„omylů celkem: 107"**, ačkoli
> součet řádků tabulky je **118**. **Součet řádků je větší než „celkem" — nesoulad
> je vidět na první pohled** a je to přesně ta vada, kterou popisuje sám blok `8n`
> („pevný seznam bloků znamená, že každý nový blok omylů vypadne z počtu").
> **Co má udělat příští session:** doplnit `("8n", "### 8n. Omyly AKČNÍ session")`
> do `BLOKY`, přepočítat souhrn a ověřit, že řádky tabulky dávají totéž co brána.
> Do té doby platí: **součet řádků je 118**; „107" je **stav před blokem `8n`**
> (ve svém čase správný).

> **⚠ ŘÁDKY `8k` A `8l` BYLY DOPLNĚNY 2. 10. 2026 VE 20:3x UTC — a je to
> přesně to, co má návrh NA17 hlídat.** Obě čísla **v dokumentu byla**, ale
> **v téhle tabulce ne** — takže je **nepočítala žádná brána** a „celkem"
> hlásilo **91**. Není to kosmetika: blok **`8l`** (omylů 102–104) navíc
> nebyl zapsaný jako blok omylů, ale jako `### 24.16`, takže ho neviděl
> **nikdo** (omyl **105**). Náprava: nadpis přejmenován na `### 8l. …`,
> řádky doplněny sem a do `BLOKY` v `kronika-kontrola.py` — **a brána to
> teď umí říct sama** (vypisuje, které bloky sečetla, a spadne, když blok
> v `HANDOFF.md` řádek v téhle tabulce nemá).

> **⚠ A JEŠTĚ JEDNO ČÍSLO, KTERÉ SEM PATŘÍ (H18):** v `HANDOFF.md` je **§13.2
> „Vlastní omyly při těch opravách (č. 24–28)"** — tedy **blok omylů mimo tuhle
> tabulku**. ⚠ **Stav 2. 10. 2026, 20:3x UTC:** blok `8l` je **už v `BLOKY`**
> i v tabulce výš, takže „co brána nevidí" se zúžilo na **§13.2** — a to je
> **měřená mez, ne ticho**: omyly **24–28** jsou v dokumentu, ale **nejsou
> v žádném z 12 bloků** (díry v číslování, naměřeno `_analyza\_s25-sonda-id.py`).
> **Původní znění z 2. 10. 2026 dopoledne (ve svém čase správné, A2):**
> „Brána ho nevidí (pevný seznam 8 kotev), takže »omylů celkem 75« není počet
> omylů v dokumentu. Správně: **80 unikátních** před touhle session, **86** po ní."

> **⚠ FORMAT TABULKY NENÍ LIBOVOLNÝ — čte ji brána.** `kronika-kontrola.py`
> hledá řádek tvaru `| **<blok>** | <popis> | **<počet>** |`. Když jsem
> v téhle session tabulku přepsal s jiným pořadím sloupců, brána ji
> **nepřečetla** a hlásila „v kronice §3 řádek NEMÁ" u **všech osmi** bloků —
> tedy **falešný poplach na správných datech**. **Opravil se dokument, ne
> měřidlo** (vzor je kanonický a všechna předchozí vydání ho měla).

> **⚠ TREND, KTERÝ JE VIDĚT A JE NEPŘÍJEMNÝ:** podíl omylů **v měřidle**
> **neklesá** — drží se kolem **80 %**, a bloky **8h** i **8i** mají dokonce
> **9 z 9** a **6 z 6** (100 %). To **není** náhodný šum: znamená to, že
> **nejrizikovější část práce není „napsat opravu", ale „změřit, že oprava
> funguje"**. A že se to **opakuje i po 81 zaznamenaných omylech** — tedy že
> **znalost pasti sama nestačí** (nejlépe to dokládají omyly 72–74: **tři kola**
> hledání správného kritéria na jednom souboru).
>
> **⚠ A NOVÝ VZOREC, NAMĚŘENÝ 2. 10. 2026 (H18–H20): OPRAVA MĚŘIDLA MÁ TAKY
> SLEPÁ MÍSTA — a nikdo je neměří.** Tři nálezy z ověření #17 jsou **rezidua
> oprav, které byly prohlášeny za hotové**: H14 (výjimka klíčovaná jménem),
> H15 (ruční seznam dokumentů zůstal), H17 (predikát přítomnosti ≠ predikát
> extrakce). **Poučení: když se opravuje měřidlo, musí se mutačně ověřit
> OPRAVA, ne jen původní vada** — jinak se „hotovo" čte z toho, že starý test
> projde.
>
> **A druhé měření téhož dne, které patří sem:** ověřovací session udělala
> **6 vlastních omylů** (81–86) a **5 z nich vypadalo jako nález o CIZÍM kódu** —
> přesto, že měla hotová pravidla, nezávislý pohled a vědomí všech pastí.
> **Znalost pastí tedy nestačí; rozhoduje tvar ověření.**
>
> **Co z toho plyne pro proces:** investovat do **měřidel**, ne do varování.
> Konkrétně: každá brána má mít **mutační test**, každé porovnání **hash**,
> každá mutace **`assert`, že se provedla** — a **každé „celkem N" musí říct,
> KTERÉ zdroje do toho N zahrnulo** (H18: tři různá čísla téhož jména).

**Tři nejdražší omyly celého projektu** (každý stál data nebo falešný nález):

| # | Co se stalo | Cena |
|---|---|---|
| **14 souborů** (1. 10.) | „Oprava" podle `Target` u hardlinku → junctiony místo souborů | obnoveno **jen z karantény**; pravidlo do skillu |
| **omyl 50** (2. 10.) | Úkol B aplikován **jen do pracovního stromu**, hlášen jako hotový | málem se ztratila celá práce; zachránil ji **assert v runneru**, ne pozornost |
| **omyl 51** (2. 10.) | Vzor `.has(` bez kontextu → „kód má Godot 3 API" | málem „oprava" **správného** `combat.gd`; chytilo se to **dřív, než se zapsalo** |

---

## 4. Evidence omylů — nejcennější část kroniky

**Proč to tu je zvlášť:** `AGENTS.md` říká *„počítej, že i tvoje první číslo bude
někde mimo."* Kronika to **dokládá čísly** — a je to jediné místo, kde je vidět
**trend**.

> **⚠ Proč je tabulka s počty omylů ve zvláštní sekci §3:**
> je to **jediné místo, které se musí přepočítat po KAŽDÉ session**, a když
> leželo tady uprostřed, snadno se zapomnělo. Počítá ho nástroj, ne člověk.

> **⚠ PŘESNOST TOHOHLE ČÍSLA — a proč je to poučení samo o sobě:**
> první verze kroniky tvrdila u **8d „5"** a u **8e „10"**. Bylo to **špatně**
> (správně **6** a **11**) a **odhalila to až kontrola kroniky**
> (`_analyza\kronika-kontrola.py`), ne moje pozornost — čísla jsem napsal
> **odhadem z přečteného textu**, místo abych je **spočítal**.
> Je to **omyl č. 60** (viz `HANDOFF.md` §8f) a je to **tentýž vzor** jako
> všechno ostatní v týhle tabulce: **vada měření, ne nález o projektu.**

> **⚠ PŘESNOST TOHOHLE ČÍSLA — a proč je to poučení samo o sobě:**
> první verze kroniky tvrdila u **8d „5"** a u **8e „10"**. Bylo to **špatně**
> (správně **6** a **11**) a **odhalila to až kontrola kroniky**
> (`_analyza\kronika-kontrola.py`), ne moje pozornost — čísla jsem napsal
> **odhadem z přečteného textu**, místo abych je **spočítal**.
> Je to **omyl č. 60** (viz `HANDOFF.md` §8f) a je to **tentýž vzor** jako
> všechno ostatní v týhle tabulce: **vada měření, ne nález o projektu.**
>

> **⚠ TREND, KTERÝ JE VIDĚT A JE NEPŘÍJEMNÝ:** podíl omylů **v měřidle**
> neklesá — drží se kolem **80 %**. To **není** náhodný šum: znamená to, že
> **nejrizikovější část práce není „napsat opravu", ale „změřit, že oprava
> funguje"**. A že se to **opakuje i po 52 zaznamenaných omylech** — tedy že
> **znalost pasti sama nestačí** (nejlépe to dokládá omyl 57 a 58: **táž past
> dvakrát v jednom kroku**).
>
> **Co z toho plyne pro proces:** investovat do **měřidel**, ne do varování.
> Konkrétně: každá brána má mít **mutační test**, každé porovnání **hash**,
> každá mutace **`assert`, že se provedla**.

**Tři nejdražší omyly celého projektu** (každý stál data nebo falešný nález):

| # | Co se stalo | Cena |
|---|---|---|
| **14 souborů** (1. 10.) | „Oprava" podle `Target` u hardlinku → junctiony místo souborů | obnoveno **jen z karantény**; pravidlo do skillu |
| **omyl 50** (2. 10.) | Úkol B aplikován **jen do pracovního stromu**, hlášen jako hotový | málem se ztratila celá práce; zachránil ji **assert v runneru**, ne pozornost |
| **omyl 51** (2. 10.) | Vzor `.has(` bez kontextu → „kód má Godot 3 API" | málem „oprava" **správného** `combat.gd`; chytilo se to **dřív, než se zapsalo** |

---

## 5. Poučení (lessons learned) — průběžně, s odkazem na zdroj

**Pravidlo: poučení bez naměřeného případu sem nepatří** (`AGENTS.md`:
„Znalost patří k naměřenému příkladu, ne k pravidlu"). Každý řádek má **zdroj**.

| # | Poučení | Naměřený případ | Kde je zapsané |
|---|---|---|---|
| **L1** | **Brána, která nemá jak selhat, není brána** | `check-schema.py` prošel nad prázdným seznamem; `test-cooldown.py` vypsal CHYBA a skončil `exit 0`; statická kontrola našla vadu **v komentáři** | `AGENTS.md`, `overovani` §5 |
| **L2** | **Mutace, která se tiše neprovede, tvrdí totéž co mutace, která projde** | 3× naměřeno (em-dash v PowerShellu, zpětné apostrofy, `\t` v Python literálu) | `overovani` §7.9, §7.12 |
| **L3** | **„Hotovo" je tvrzení, ne důkaz** — a staví se na něm celý DAG | `world.map` i `entity.player` byly `done`, ale práce v repu nebyla | `AGENTS.md` |
| **L4** | **Brána, která se ptá na PŘÍTOMNOST, neměří CHOVÁNÍ** | 3 PR prošla zeleným CI (39 kontrol, 0 selhání) a `save()` uložil 35 B | `AGENTS.md` |
| **L5** | **Brána, která NEPROBĚHLA, není červená — je NEZMĚŘENÁ** | `test-check-schema.py` 0 kontrol v sandboxu, **17/0** mimo | `overovani` §7.13 |
| **L6** | **„Vydalo se" není „podařilo se"** | pět úloh `running` → za pár minut `ready, attempts=1`; všech pět selhalo | `overovani` **§8.1** |
| **L7** | **Běh může selhat způsobem, který není zelený ani červený** (TPM limit, parse error, žádná změna, neproběhlo) | `#146`: `TPM Limit 8000, Requested 14398`, `[test] 59/0` = baseline | `overovani` **§8.2** |
| **L8** | **Edituješ-li kód, musíš přegenerovat inventář — a možná dvakrát** | dvě brány spadly na `exit 2` po editaci `kontrola-diakritiky.py` a `SKILL.md` | `HANDOFF.md` §17.11 |
| **L9** | **Ukázku rozbitého kódování v dokumentu popisuj SLOVEM** | brána diakritiky ohlásila vadu dokumentu, který ji jen vyjmenovával | `AGENTS.md`, `overovani` §7.5 |
| **L10** | **Ruční seznam místo projití složky je vada (S27) — a opakuje se** | **po jedenácté**: v bráně diakritiky bylo **5 z 12 skillů** (chyběl i `overovani`) | `HANDOFF.md` §17.11/3 |
| **L11** | **`reasoningEffort` je GLOBÁLNÍ nastavení profilu — „jiný effort pro jinou činnost" dnes není k dispozici** | naměřeno 2. 10. 2026: `profiles/desktop/cordis.patch.yml:27–28` → `model: deepseek-flash`, `reasoningEffort: max`; v `request/header` **této** session pole `reasoningEffort` **NENÍ** (jen `model`), takže se effort **ze session logu nedá změřit** — je jen v profilu. A DSH ho **nepředává subagentům** (skill `dsh-usage`). **Přepnutí tedy znamená přepnout profil pro VŠE**, ne pro jednu činnost | `KRONIKA-PROJEKTU.md` §5 NA7, `ANALYZA-EFEKTIVITY-DSH.md` §6 |
| **L12** | **Náklad reasoningu není jednorázový — vrací se v každém dalším requestu z cache** | naměřeno (`ANALYZA-EFEKTIVITY-DSH.md` §2.6): každý vyprodukovaný reasoning token se průměrně **přečte 196–232×**; Flash sessions platí thinking **dvakrát** — jako výstup ($1,95) a znovu z cache ($2,30) = **$4,25 = 22,8 % účtu** | `dsh-usage` („Omezení"), `ANALYZA-EFEKTIVITY-DSH.md` §2.6 |
| **L13** | **Vkládáš-li text, který sám sebe zmiňuje, nesmí být kotva hledaná v TOMTÉMŽ textu** — jinak se vloží dvakrát | naměřeno 2. 10. 2026 (omyl **68**): skript vkládal §18.16 „před nadpis `## 18.`", ale ta kotva je i **uvnitř nově vloženého textu** (odkaz „§18.15") → po prvním vložení se posunula a druhá náhrada přidala oddíl **znovu**; `HANDOFF.md` měl `## 18.` **3×** a `### 8g.` **2×**. Předtím **dvojitý append** nafoukl soubor z 202 443 B na 234 375 B. **Řešení:** hledej kotvu **v původním souboru** a skládej **spojením řetězců**, ne dalším hledáním po zápisu; a měj **zálohu kopií** (`overovani` §2.1) | `HANDOFF.md` §18.16, `_analyza\s18d-sestav-handoff.py` |
| **L15** | **Nula a „nezměřeno" nejsou úspěch — a v bráně to musí být VIDĚT** | naměřeno 2. 10. 2026 (omyl **78**, nález **H17**): `kronika-kontrola.py` vypsala u bloku bez nadpisu „skutečný počet omylů: **0**" — tedy **naměřenou nulu**. Přitom neměřila nic; a protože kronika tvrdila 6, rozdíl vypadal jako **nález o datech**. Druhá polovina téhož: blok, který v kronice **řádek nemá**, se tiše přeskakoval (`continue`) — a ne zapsaný omyl se ztratí navždy. **Opraveno:** chybějící nadpis i koncová kotva = `NEZMĚŘENO`, chybějící řádek v kronice = **ROZCHOD** | `HANDOFF.md` §21.4, `_analyza\kronika-kontrola.py` |
| **L16** | **Když brána sama obsahuje VZOREK hledané vady, musí se odlišit VÝZNAMEM, ne TVAREM** | naměřeno 2. 10. 2026 (omyl **72–74**): projití složky ohlásilo rozbitou diakritiku ve **třech správných branách** — ty mají vzorek rozbitých znaků **jako literál** (musí, jinak by neměly co hledat). Kritérium „dva znaky po sobě" selhalo (hlásilo i hlášku ve správném souboru) a půlparser `bez_komentaru()` selhal na **jednoznakových uvozovkách** (uvozovka u jednoho znaku je sama literál, takže se spárovaly špatně). Opravilo to až **významové** kritérium: rozbité znaky smí být jen na řádku, který vzorek **definuje nebo používá**. **Čtvrtá variace téže pasti** jako `overovani` §8.3 | `overovani` §8.3, `_analyza\g1-diakritika-novych.py` |
| **L17** | **Mutační test bez fixtury ve TVARU, který vadu způsobil, je slepý** | naměřeno 2. 10. 2026 (nález **H16**): `h17-kronika-mutace.py` testoval bránu **jen na živé kronice**, a ta v době testu neměla ve výřezu **tabulku nálezů** → vada (54 omylů místo 10) **testem prošla** a projevila se až v praxi. Fixtura, která ten tvar vyrobí **řízeně** (`t3-kronika-mutace.py`), našla **dvě další vady brány** (H17). **Obecně: test na živém dokumentu měří dnešní podobu dokumentu, ne odolnost brány** | `HANDOFF.md` §21.4, `_analyza\t3-kronika-mutace.py` |
| **L14** | **Filtr, který dostane KRÁTKÝ sha, vrátí PRÁZDNO — a prázdno vypadá jako „ještě nic"** | naměřeno 2. 10. 2026 (omyl **69**): `GET /actions/runs?head_sha=c40bdd5` → **`total_count: 0`**, a já **26 minut** čekal na workflow, který **už skončil** (`completed/success`). Se **plným** sha (`c40bdd556b67f9ac95a82b6c1c8798f926f431fd`) vrátí **2 běhy**, oba `success`. Skutečný důkaz nasazení přišel z **`last-modified`** (13:18:06 vs. push 13:16:50), ne z čekacího skriptu | `HANDOFF.md` §19.1, `_analyza\p19b-cekej-pages.mjs` |
| **L18** | **Brána musí ptát se na PŘÍTOMNOST vstupu TÍMŽ predikátem, kterým ho pak HLEDÁ** — jinak vypíše „naměřenou nulu" u bloku, který v dokumentu je | naměřeno 2. 10. 2026 (H19): `kronika-kontrola.py` testuje `od in hand` (**kdekoliv v textu**), ale výřez bere `radek.startswith(od)` (**začátek řádku**). Kotva `### 8g. Omyly PLÁNOVACÍ` je v `HANDOFF.md` **2×** (jednou nadpis, jednou citace v próze omylu 76) → nadpis pryč, citace zůstala ⇒ brána vypsala **„v HANDOFF.md je 0"**. Je to **reziduum opravy H17**, kterou táž session označila za hotovou | `HANDOFF.md` §22.4 (případ C5), §22.6; `_analyza\v3-kronika-stavy.py` |
| **L19** | **„Přejít na projití složky" je třeba udělat CELÉ — jinak zůstane ruční seznam uvnitř** | naměřeno 2. 10. 2026 (H18): (a) `kronika-kontrola.py` má **pevný seznam 8 kotev** → omyly **24–28** zapsané v **§13.2** nevidí; brána hlásí **75**, dokument má **80 unikátních** (a po §8i **86**). (b) `kontrola-diakritiky.py` prochází **skilly**, ale dokumenty má v **ručním seznamu 54 cest** → **11 z 37** kořenových `*.md` neotevře. **Verdikt `NA15 = APLIKOVÁNO — celé` byl proto nepřesný** | `HANDOFF.md` §22.5 (H18), `_analyza\v4-omyly-nezavisle.py`, `_analyza\v7-kryti-dokumentu.py` |
| **L20** | **Výjimka klíčovaná JMÉNEM nebo RUČNÍM SEZNAMEM je stejná vada jako ruční seznam cest** — a projeví se jako falešný poplach na správném souboru | naměřeno 2. 10. 2026 (H20): `g1-diakritika-novych.py` povoluje rozbité znaky na řádku, kde je `(ROZBITE\|rozbito)\s*=` (tedy `=` **hned** po jménu), a jen u **3 ručně vyjmenovaných** souborů (`SAMOKONTROLA`). Legitimní definice vzorku pod jménem `VZOREK_SPATNE` **i** `ROZBITE_DVOJICE` ⇒ **`CHYBA … ANO (3 znaků)`, `exit 1`**. **Reziduum opravy H14** | `HANDOFF.md` §22.5 (H20), §22.6 |

| **L21** | **Brána může číst CITACI místo TVRZENÍ — a mít `exit 1` ze špatného důvodu.** Vzor rozhoduje o tom, CO se vůbec přečte; „vzor něco našel" a „vzor našel to, co hledám" jsou dvě různé věty | naměřeno 2. 10. 2026 (H24): `audit2a-schema.py` hledal `(\d+)\s+sloupc`, takže zabral na **„32 sloupců"** (citace dřívějšího chybného tvrzení) a skutečné tvrzení „správně je **39**" **neměřil vůbec** — jednotka u něj nestojí. Brána hlásila 6 rozchodů a **ani jeden nebyl tvrzení o dnešku** | `AGENTS.md` („Jak ověřovat"), `overovani` **§10.1–10.2** |
| **L22** | **Měřidlo musí VYPISOVAT VELIKOST OKNA, které použilo — velkorysé okno není opatrnost, je to slepota** | naměřeno 2. 10. 2026 (omyl **89**): první verze brala „blok" jako souvislý běh neprázdných řádků; v `AGENTS.md` je oddíl „## Jak dokumentovat" **jeden blok o 5 441 znacích se sedmi daty** → jediné datum kdekoli v něm **umlčelo celá oddíl**. Zúžení na jednu odrážku (**824 znaků**) **ZVÝŠILO pokrytí** (26 → 27 rozchodů). Odhalil to až mutační test — a jen proto, že se velikost okna vypisovala | `overovani` **§10.4–10.5** |
| **L23** | **Nástroj, který KOPÍRUJE dokumenty, musí měřidlům říct, že je to kopie** — jinak si příští session přečte vlastní snapshot jako stav dokumentace | naměřeno 2. 10. 2026 (H27, omyl **92**): `audit-snapshot.py` (opatření 9) zkopíroval dokumentaci do `_analyza\snapshot-<čas>\` a `audit1-inventar.py` ji začal počítat jako dokumenty → **159 místo 98**, **66 záloh místo 8**. Je to **nález o OPATŘENÍ**, ne o nástroji: opatření samo sobě zneplatnilo baseline | `AGENTS.md` („Jak ověřovat"), `_analyza\audit1-inventar.py` |
| **L24** | **`mtime` není obsah — a mutační test `mtime` MĚNÍ.** Kritérium „změnil se soubor?" se musí ptát na **hash**, ne na časovou značku | naměřeno 2. 10. 2026 (H28): zadání mělo podle `mtime` proti 17:38 rozhodnout, zda v `NEXT-SESSION-INSTRUKCE.md` pracuje jiná session. `mtime` se změnil (→ 18:32:22), **ale SHA-256 obsahu je shodný ve dvou snapshotech i na disku** (`9c05c6b4…`, 17 841 B) — hnul jím `_analyza\zadani-mutace.py`, který soubor zapisuje a vrací. **Kritérium tvrdilo nepravdu.** Totéž platí pro `HANDOFF.md`: je označený jako **„jen mtime"**, obsah beze změny | `HANDOFF.md` §23.1, §23.7 |
| **L25** | **Měřidlo musí mít JEDNOTKU PRÁCE — „počet výskytů" není „počet souborů, které se musí opravit".** A krajní zpřesnění není řešení: **volný** vzor počítá prózu, **přísný** mine kořenové cesty | naměřeno 4. 10. 2026 (H38): plán přesunu tvrdil cenu **208 výskytů** v kódu. Naměřeno: **176 SOUBORŮ** je pracovní jednotka (1,2 výskytu na soubor), volný vzor **208** (počítá i zmínky v próze), přísný vzor „`Local-Deepseek` + oddělovač" **100** — a mine `Path(r"C:\…\Local-Deepseek")`, což je v `_analyza\` **většina** případů. **Obě krajní čísla jsou špatná** a obě vypadají jako zpřesnění | `PLAN-SEPARACE-WORKSPACE.md` §10.2b |
| **L26** | **Nástroj, který si cestu ODVOZUJE, není automaticky přenosný — záleží, Z ČEHO ji odvozuje.** `PSScriptRoot`/`__file__` je bezpečné; **rodič repa je vazba na umístění**, ne na projekt | naměřeno 4. 10. 2026 (H37): `install-into-repo.ps1:34` bere `$ProjDir` z `Split-Path $PSScriptRoot -Parent` → `…\Local-Deepseek\projects\`, a **`projects\` neexistuje** → nástroj **neběží**. **Sken přímých cest to nemůže vidět** (žádný literál `Local-Deepseek` tam není). Do přesunu proto patří **dohledání odvozených cest** jako samostatný krok | `PLAN-SEPARACE-WORKSPACE.md` §10.4 (P1b) |

---

## 6. Návrhy na zlepšení — od session, ke schválení PŘÍŠTÍ session

> **Dvoukrokový proces (rozhodnutí uživatele, 2. 10. 2026):**
> **Session návrh ZAPÍŠE ihned** (aby se neztratil kontext), ale **označí ho
> jako `NEOVĚŘENO`**. **Následující session ho při ověřování buď POTVRDÍ
> a aplikuje, nebo ZAMÍTNE** — a napíše proč. Důvod: autor není nezávislý
> reviewer (`AGENTS.md`), ale **odklad ztrácí kontext**; tenhle postup řeší obojí.
>
> **Stavy:** `NEOVĚŘENO` → `APLIKOVÁNO` / `ZAMÍTNUTO` / `ODLOŽENO`.

| # | Návrh | Zdroj (naměřený) | Stav | Rozhodl |
|---|---|---|---|---|
| **NA1** | Zapsat do `AGENTS.md` pravidlo „kdo mění kód, přegeneruje inventář" | L8: dvě brány na `exit 2` | **`APLIKOVÁNO`** — pravidlo je v `AGENTS.md` („Jak ověřovat") **i** v `PREDAVANI-SESSION.md` §6.2 **D1**; `ag-over-cisla.py` → 0 rozchodů | plánovací session 2. 10. 13:xx |
| **NA2** | Každá session na konci **jednořádkové hodnocení stavu** (známka + kde jsme) | požadavek uživatele | **`APLIKOVÁNO`** — `PREDAVANI-SESSION.md` §2.1 (stavový řádek 🟢/🟡/🔴) | uživatel |
| **NA3** | **Závěrečná validační session** + cyklus validace/oprav, pak shrnutí a revize nástrojů | požadavek uživatele | **`APLIKOVÁNO`** — `PREDAVANI-SESSION.md` §2.3 + `PLAN-DALSI-KROK.md` §6 | uživatel |
| **NA4** | Vyřadit Groq z rotace pro velké granule (nebo zmenšit prompt) | H5: TPM 8 000 < 14 398 | **`POTVRZENO` — a naměřeno ostřeji:** vlastní měření dává vstup **≈ 11 207 tokenů** pro `entity.player.api` a **≈ 11 026** pro `world.nodes`; i `sim.combat` má **8 772**. **Groq je pod tím u VŠECH nových granulí.** Zmenšit prompt nepomůže — **pevná část** (`CONVENTIONS.md` 3 839 + systémový prompt Aideru ~2 166) je **většina** vstupu. **Provedení čeká na schválení** (zadání zakazuje měnit `agent.yml` bez něj) | plánovací session 2. 10. 13:xx |
| **NA5** | Opravit skládání jména modelu (`provider/model`) | H4: `openai/openai/gpt-oss-120b` | **`POTVRZENO`** — naměřeno v logu: `agent.yml:227` skládá `--model "openai/${FORGE_MODEL}"`, a `FORGE_MODEL` už `openai/` **obsahuje** → Aider dostal `openai/openai/gpt-oss-120b` a varoval `Unknown context window size and costs` (tedy si bere „sane defaults"). **Změna `agent.yml` čeká na schválení** | plánovací session 2. 10. 13:xx |
| **NA6** | Přidat do granule `tests.harness` atrapu v rozporu s vlastností | H2: M3 nechycena | **`POTVRZENO`** — potvrzeno **vlastním** spuštěním: sonda dala A **2×** / B **9×** a s rozpornou atrapou `damage = 13` vs. `bez větve A → 33/1`. **Zadání pro akční session** | plánovací session 2. 10. 13:xx |
| **NA7** | Zvážit nižší `reasoningEffort` pro mechanickou práci (a změřit to řízeně) | `ANALYZA-EFEKTIVITY-DSH.md` §6, §7 krok 0 | **`ODLOŽENO`** — blokuje to **vlastnost nástroje, ne rozhodnutí**: `reasoningEffort` je **globální nastavení profilu** a DSH ho **nepředává subagentům** (§17.12/L11), takže „jiný effort pro jinou činnost" **dnes není k dispozici**. Změřit se dá jen přepnutím profilu pro **vše** — a to je jiné rozhodnutí. **Návrh zůstává, nezaniká** | plánovací session 2. 10. 13:xx |
| **NA8** | **Přidat nový skill do brány diakritiky vždy, když vznikne** (dnes ruční seznam) — nebo lépe: **projít složku `~\.dsh\skills\*` místo seznamu** | L10: 5 z 12 skillů; **po jedenácté** táž vada S27 | **`POTVRZENO` — a je to po DVANÁCTÉ.** Dnes se do obou bran doplňovalo **6 nových souborů ručně** (`p18-*`). **Naměřený důkaz, že ruční seznam je vada:** `g1-diakritika-novych.py` sám sebe popisuje jako „neptá se seznamu", a přesto **seznam má**. **Doporučení: projít složku** (u skillů `~\.dsh\skills\*`, u `_analyza` glob `p*-*.py`) — zadání pro akční session | plánovací session 2. 10. 13:xx |
| **NA9** | **Každá session na konci řádek do kroniky** (jinak historie zmizí s `HANDOFF.md`) | požadavek uživatele 2. 10. 2026; zapsáno do `PREDAVANI-SESSION.md` §2 | `APLIKOVÁNO` (do postupu) | uživatel |
| **NA10** | **Stavový řádek 🟢/🟡/🔴 na konci session** | požadavek uživatele; zapsáno do `PREDAVANI-SESSION.md` §2.1 | `APLIKOVÁNO` (do postupu) | uživatel |
| **NA11** | **Závěrečná fáze Z1–Z3** (validace → cyklus oprav → shrnutí a revize nástrojů) | požadavek uživatele; zapsáno do `PREDAVANI-SESSION.md` §2.3 a `PLAN-DALSI-KROK.md` §6 | `APLIKOVÁNO` (do postupu) | uživatel |
| **NA12** | **Návrh na změnu pravidla zapíše session, ale rozhodne až příští** | požadavek uživatele; zapsáno do `PREDAVANI-SESSION.md` §2.2. **Zdůvodnění z dat:** 76 % omylů projektu vzniklo v měřidle (§3) → „mně to přijde správné" je důkaz, který tu opakovaně selhal | `APLIKOVÁNO` (do postupu) | uživatel |
| **NA13** | **Přidat do conductora endpoint na změnu stavu úlohy** (`POST /task/state`) | §16.7 + §18.10: výčet endpointů z kódu i z živého rozcestníku — `pause`/`block task` tam **není** | **`ZAMÍTNUTO`** — **3. 10. 2026 (akční session).** Důvod **není** „nejde to", ale **„už to není potřeba"**: jediný konkrétní důvod pozastavení (**#146**) **zanikl** — Úkol A ten test opravil a opravený test projde i bez `move()` (naměřeno **64/0**, dnes **65/0**), takže **není co pozastavovat**. Zavádět do živého conductora **nový stavový endpoint** bez jediného případu použití by bylo **riziko bez užitku** (`PLAN-DALSI-KROK.md` §4 zákaz č. 6). **Kdyby vyvstal konkrétní případ, návrh se vrací** — naměřená fakta (které endpointy nejsou a co dělají ty stávající) zůstávají v §18.10 | akční session 2. 10. 2026 |
| **NA14** | **Doplnit do `providers.json` změřené TPM limity** | H10: v `providers.json` **žádné TPM není**; jediné změřené (Groq 8 000) je z logu běhu | **`ODLOŽENO` — a je to ZÁVAZNÉ, ne dobrovolné.** Dva důvody, každý měřený: (1) **Doplnit se dnes dá JEDINÉ Groqovo číslo** — u mistralu, cerebrasu, gemini a openrouteru **TPM nikdo nezměřil** a v repu není (§18.12, „co se ověřit NEDALO"); doplnit `?` do živého konfigurace by znamenalo **zapsat nezměřené jako změřené**. (2) **`providers.json` je konfigurace conductora** a uživatel 2. 10. 2026 rozhodl, že se **nemění** („Groq ODLOŽEN", `HANDOFF.md` §20). **Návrh platí, ale je zablokovaný měřením, ne rozhodnutím** — otevře se spolu s NA16, až bude potřeba | akční session 2. 10. 2026 |
| **NA15** | **Nahradit ruční seznam v `kronika-kontrola.py` / `kontrola-diakritiky.py` za projití složky** a **zavést pro ně mutační test s fixturou, ve které je i tabulka nálezů** | §18.15: kontrola kroniky minula **dvakrát** (54 místo 10) a tři opravy téhož selhaly (dvě vrátily **0 omylů**) | **`APLIKOVÁNO`** — **3. 10. 2026 (akční session), celé:** (1) `g1-diakritika-novych.py` **prochází složku** — seznam **190 cest zrušen**, naměřeno **405 souborů, 5 binárních přeskočeno (vypsáno), vad 0**; (2) `kontrola-diakritiky.py` **prochází `~/.dsh/skills/*/SKILL.md`** — **12 z 12** (dřív 5 ručních, chyběl i `overovani`); (3) nový **`_analyza\t3-kronika-mutace.py`** — fixtura s **tabulkou nálezů** i **tabulkou omylů**, **6 případů** (2 kontrolní + 3 vady + kritérium tvaru), `exit 0`. **A našel dvě další vady brány (H17).** Cena: **tři kola** hledání správného kritéria (omyly 72–74) | akční session 2. 10. 2026 |
| **NA16** | **Dynamicky assignovat / redukovat balíček pro omezené modely** (spočítat velikost vstupu PŘED výběrem poskytovatele a poslat úlohu jen tomu, do jehož limitu se vejde; případně zmenšit, co se posílá) | **Uživatel 2. 10. 2026** („Zatím zapiš do plánu ODLOŽENO — Groq limit 8k tokenů — dynamicky assignovat/redukovat balíček pro omezené modely"); naměřeno: pevná část **9 196 t.** (CONVENTIONS 3 839 + obal Aideru 5 357) vs. limit **8 000** → **0 z 21 granulí**, při CONVENTIONS 3 000 znacích **10 z 21** | `ODLOŽENO` (rozhodl uživatel) | uživatel — **potvrzeno 2. 10. 2026 i akční session: s Groqem se NEDĚLALO NIC** (neměnil se `CONVENTIONS.md` ani `agent.yml`, Groq zůstal v rotaci) |
| **NA17** | **Každé měřidlo, které tvrdí „celkem N", musí vypsat, KTERÉ zdroje do toho N zahrnulo** (seznam bloků/souborů) — a brána kroniky má přejít z **pevného seznamu 8 kotev** na hledání bloků omylů **podle tvaru nadpisu** (jako `g1` u souborů) | **H18**: tři různá čísla téhož jména (**75** zná brána, **81** součet řádků, **86** unikátních id) a omyly **24–28** v **§13.2** nevidí žádná brána; `NA15` přitom tvrdilo „projití složky — celé" | **`APLIKOVÁNO` (v rozsahu) — 2. 10. 2026, plánovací session.** **Naměřeno znovu:** brána zná **8 bloků** (75 omylů), ale v `HANDOFF.md` je **10 bloků** = **85**; rozdíl **10** je přesně to, co nevidí — `### 8i.` (6 omylů) a `### 8j.` (10). **Provedeno:** nová brána `_analyza\s24-meridla-over.py` **vypisuje u každého měření, které zdroje sečetla** (a je **mutačně ověřena 2/2**, `s24-meridla-mutace.py`) a v kronize **§3 jsou teď tři čísla s uvedeným zdrojem každého**. **Zúžení rozsahu (a proč):** „hledání bloků podle tvaru nadpisu" **zavrhuji** — naměřeno, že by to **bylo slepé** (omyl **99**: vzor `### 8[a-z]` nerozliší `8h` od `8h-test`) a shodu s kotvami **nejde ověřit uvnitř téhož nástroje**. **Co zůstává:** rozšířit kotvy brány o `8i`/`8j` je **Úkol 2c** zadání `ZADANI-OPRAVA-MERIDEL.md` | plánovací session 2. 10. 2026 |
| **NA18** | **Čas v hlavičkách a dokladech se zapisuje MĚŘENÝM údajem a se ZÓNOU** (`(Get-Date).ToUniversalTime()`, `git log --format=%cI`) — nikdy odhadem z průběhu session | **H22**: hlavička zadání tvrdí **19:2x UTC**, soubor zapsán **14:48 UTC** (posun ~4,4 h); §21.8 píše „16:4x UTC" k commitu s časem **14:43+02:00**, ale **měřený** čas pushe (`14:43:10 UTC`) má správně | **`APLIKOVÁNO` (zúžené) — 2. 10. 2026, plánovací session.** **Měřená část se plní:** hlavičky `ZADANI-OPRAVA-MERIDEL.md` i `PLAN-DALSI-KROK.md` mají čas z **`datetime.now(timezone.utc)`**, ne odhad, a u commitů je **`git log --format=%cI`**. **Co ZAMÍTÁM:** „zóna u **každého** údaje" — u **historických** zápisů v `HANDOFF.md`/`KRONIKA` by to znamenalo **přepisovat stará čísla**, což A2 zakazuje (rozdíl je **čas**, ne nepravda). **Pravidlo platí pro NOVÉ zápisy** | plánovací session 2. 10. 2026 |
| **NA19** | **Sjednotit číslování sekcí kroniky u návrhů:** tabulka návrhů je v **§6**, ale **7 odkazů** ukazuje na **§5** („Poučení") — 5 v `PREDAVANI-SESSION.md` (řádky 84, 129, 286, 317, 334) a 2 v kronize (§7 a §8). Náprava: **opravit ukazatele**, ne přečíslovat sekce | **H23** — naměřeno 2. 10. 2026; je to **tatáž třída** jako přečíslování §3/§4, na kterém už jednou spadla brána kroniky (§21.4) | **`APLIKOVÁNO` — 2. 10. 2026, plánovací session.** **Přeměřeno:** odkazů na **kroniku** §5 je **6** (5 původních + 1 nový v ř. **157**, který vznikl touhle session) — plus **jeden správný** odkaz na `PLAN-DALSI-KROK.md` §5 (jiný dokument). **Měření je součástí brány** `s24-meridla-over.py` (sekce F7 ji **vypíše i s řádky**), takže se nedá „splnit" omylem. Náprava = **opravit 6 ukazatelů**, ne přečíslovat sekce | plánovací session 2. 10. 2026 |

| **NA20** | **Kritérium „změnil se soubor?" přepnout z `mtime` na SHA-256 obsahu** — v zadáních i v nástrojích. Kde je po ruce snapshot (Úkol 0), porovnávat proti němu; `mtime` používat jen jako **upozornění k dohledání** | **H28**: `mtime` `NEXT-SESSION-INSTRUKCE.md` se změnil (17:38:17 → 18:32:22), ale hash obsahu je **shodný ve dvou snapshotech i na disku**; hnul jím `_analyza\zadani-mutace.py`. Kritérium zadání („porovnej `mtime` s 17:38") by dalo **nepravdivou odpověď** | **`APLIKOVÁNO` (úzce) — 2. 10. 2026, plánovací session.** **Návrh se potvrdil DVAKRÁT v jedné session** (ne jednou): (1) `NEXT-SESSION-INSTRUKCE.md` — `mtime` **18:48 → 19:01**, hash **shodný** `9c05c6b434d5d026…`; (2) **vlastní `HANDOFF.md`** — `mtime` **18:44 → 19:32**, hash **shodný** `fb266565a52ef976…` (hnuly jím **mutační testy téhle session**). **Kdo se ptá na `mtime`, řekne dvakrát „pracuje v tom jiná session" — a ani jednou to není pravda.** **Zúžení:** přepis **všech** nástrojů **zamítám** (u `.py`/`.gd` je `mtime` levná nápověda); **hash se používá tam, kde se podle výsledku ROZHODUJE** — a tam je to i v nových nástrojích (`s24-*` ověřují návrat **bajtovou shodou**) | plánovací session 2. 10. 2026 |
| **NA21** | **Každý nástroj, který KOPÍRUJE dokumenty do workspace, musí být zapsán ve vyloučených složkách všech inventářů** — nebo to mít v docstringu jako deklaraci. Konkrétně: `snapshot-*` v `audit1-inventar.py` (**hotovo**) a totéž pro `kronika-kontrola.py` a `v7-kryti-dokumentu.py` | **H27**: snapshot zvedl inventář z **98 na 159 dokumentů** a ze **8 na 66 záloh**; opatření 9 tak zneplatnilo baseline auditu | **`APLIKOVÁNO` — 2. 10. 2026, plánovací session.** Vyloučení **ověřeno měřením**: `audit1-inventar.py` → **104 dokumentů** (ne 159) a **8 záloh** (ne 66) — tedy **kopie snapshotů se do inventáře nedostaly**, i když na disku jsou **dva** snapshoty s **71 soubory**. **A rozšířeno na další místo, kde to chybělo:** `kontrola-diakritiky.py` teď při projití složky vylučuje `snapshot-*` i zálohy — a **počet vyloučených VYPISUJE** (8 souborů), takže výjimka není tichá. **Zbývá:** `v7-kryti-dokumentu.py` (neměřeno, soubor se nepoužil) | plánovací session 2. 10. 2026 |
| **NA22** | **`audit2b`: u každé veličiny doložit, KTERÝ ZDROJ to číslo měří.** Veličina `kontrol` dnes srovnává čísla z různých bran (23, 59, 60, 61, 65…) a hlásí **27 rozchodů, z toho většinu falešných**. Buď ji rozpadnout na `kontrol:<brána>`, nebo ji z nástroje **vyřadit** a přiznat to v docstringu (jako se to udělalo u `audit2-rozpory.py`) | **H25**: `audit2b` má sám vadu, kterou audit vytkl `audit2-rozpory.py` („různé brány hlásí různé počty kontrol SPRÁVNĚ") | **`APLIKOVÁNO` — 2. 10. 2026, plánovací session.** **Potvrzeno a ZPŘESNĚNO měřením** (nález **H29**): rozchodů je dnes **31**, z toho **25 falešných** — a rozpad je změřený: `kontrol` **19/19 falešných**, `sloupců` **4/4** (citace), `dokumentů` 3/3, `omylů` 3/3. **Rozhodující důkaz, že to není názor:** `PREDAVANI-SESSION.md:193` je **citace** — `audit2a-schema.py` ji **správně** zařadí jako `[citace]`, `audit2b` ji hlásí jako **ROZCHOD**. **Dvě měřidla téhož čísla si odporují** (horší než jedno slepé). Oprava je **Úkol 1** zadání `ZADANI-OPRAVA-MERIDEL.md` — **cesta (A) rozpadnout na `kontrol:<brána>` je preferovaná**, protože (B) vyřazení **ztratí pokrytí** | akční session (Úkol 1) |
| **NA23** | **`g3-brany.py`: (a) u brány bez čítače vypsat `—` nebo `NEZMĚŘENO`, nikdy prázdný řetězec** — dnes má `validate-all (CELEK)` `otevřela:` **prázdné**, protože vzor `NALEZENO (\d+)|VŠE V PO` má druhou alternativu **bez skupiny**. **(b) Zvážit baseline očekávaných nenulových exitů** — dnes `g3` **nemá `sys.exit`** a je to **přehled**, ne brána; kdyby se měl stát blokujícím, musí znát **které** nenulové exity jsou správné (dnes `mutace A: pres-level`), ne jen jejich počet | naměřeno 2. 10. 2026: `g3-brany.py` skončil **`exit 0`** i s jedním nenulovým řádkem; `validate-all` vypsal prázdno; past zapsána do `overovani` §10.8 | **`APLIKOVÁNO` (obě části) — 2. 10. 2026, plánovací session.** **(a) Vada ZŮSTALA, jen změnila projev** (a je **horší**, než audit viděl): `validate-all` už **není prázdný** — vypisuje **`otevřela: 3`**, což je **`NALEZENO 3 PROBLÉMŮ`**, tedy **cizí číslo vydávané za počet otevřených souborů**. To je táž třída jako „čítač s cizím jménem". **(b) Potvrzeno a rozšířeno:** nenulové exity jsou dnes **2**, ne 1 — `mutace A: pres-level` (**správně**) a `validate-all` (**neproběhlo — prostředí**). **Baseline tedy závisí na OPRÁVNĚNÍ sandboxu** (`workspace-write` → „neproběhlo"; `danger-full-access` → zelená, jak správně poznamenal §23.3), takže blokující `g3` by musel znát **dvojici** (brána, očekávaný exit **pod daným oprávněním**). Oprava je **Úkol 2a** zadání `ZADANI-OPRAVA-MERIDEL.md` | akční session (Úkol 2a) |
| **NA24** | **`_analyza\sken-cest-celek.py` má vypisovat SOUBORY, ne (jen) výskyty** — u každé oblasti počet souborů a rozpad `souborů / výskytů / na soubor`, a **u `_analyza` navíc seznam souborů**, ne jen 4 příklady. Dnes se rozpad musel počítat jednorázově zvlášť | **H38**: plán přesunu měl cenu v **výskytech** (208) a pracovní jednotka je **176 souborů**; rozdíl rozhoduje o tom, jak drahý přesun je. Nástroj, který vydává výskyty za práci, **mění odhad ceny** | **`POTVRZENO` — 4. 10. 2026, plánovací (ověřovací) session.** **Naměřeno, že rozdíl je rozhodující:** `_analyza` má **135 výskytů v 33 souborech** (jeden soubor **46×** — snapshot manifest, další **12×** — `p8-oprava-cest.py`), takže **kdo čte výskyty jako práci, nadhodnotí ji 4×**. ⚠ **A jedna korekce provedení:** nástroj `sken-cest-celek.py` **je v `_analyza\_archiv`** (D5) — návrh se proto plní **v živém nástroji**, ne obnovou archivu (jinak by vznikl živý nástroj z archivu, což je opak D5) | plánovací session 4. 10. 2026 |
| **NA25** | **Doplnit do skillu `dsh-prostredi` past: `Get-PSDrive` na této stanici hlásí u `E:` `Free=0 / Used=0`** — a `Get-CimInstance`/`Get-Volume` jsou v sandboxu `Access denied`, takže nula vypadá potvrzeně. Volné místo měř **`System.IO.DriveInfo`** | **P4** (omyl **130**): `Get-PSDrive E` → **0 GB**, `DriveInfo` → **810,8 GB**. Málem z toho byl **blokující nález** o nemožnosti přesunu | **`NEPOTVRZENO` v této podobě — 4. 10. 2026, plánovací (ověřovací) session; PŘEFormulováno a zapsáno do skillu.** **Naměřeno (nález H56):** `Get-PSDrive E:` → **`Free=869273522176`** a `DriveInfo` → **809,6 GB** — tedy **žádná nula**. Nula je **vlastnost OMEZENÉHO OPRÁVNĚNÍ** (v režimu jen pro čtení běží PowerShell v **`ConstrainedLanguage`**, kde `.NET` statické volání nejde), **ne vlastnost stanice**. **Původní formulace by byla NEPRAVDIVÉ PRAVIDLO** — platilo by jen v sandboxu a mimo něj by mátlo. Do `dsh-prostredi` zapsáno **přesnější znění** včetně oprávnění, pod kterým platí | plánovací session 4. 10. 2026 |
| **NA26** | **Zavést trvalou kontrolu ODVOZENÝCH cest** (`PSScriptRoot`, `Split-Path … -Parent`, `import.meta.url`, `__file__`, `parents[1]`) — vedle skenu přímých cest. U každého nálezu vypsat, **kam odvozuje** | **H37** + **L26**: `install-into-repo.ps1:34` a `test-local.ps1:39` odvozují `projects\` z rodiče repa, ta složka **neexistuje** a oba nástroje jsou **mimo provoz** — a žádný sken přímých cest to nevidí | **`POTVRZENO` — 4. 10. 2026, plánovací (ověřovací) session; potřeba je teď DOLOŽENÁ.** **Dvě vady téhož druhu za jednu session** (nálezy **H49**, **H50**): `tools\test-gitignore-tajemstvi.py` má `_PARENT` **definovanou a nepoužitou** a `STANICE` **nedefinovanou** → `NameError`; `tools\verify-setup.py` má **pevnou cestu na starý kořen** → 6× CHYBI. **A žádná brána je nespouští** — `git grep` v `g3-brany.py`, `validate-all.mjs` i `over-dokumentaci.py` → **0 výskytů**. Návrh předpověděl přesně to, co se stalo | plánovací session 4. 10. 2026 |


---

## 7. Kam se zapisuje co (aby se to nehledalo)

| Chci vědět | Jdu do |
|---|---|
| **Co se stalo v celém projektu** | **tenhle dokument** |
| Co je teď hotové a co otevřené | `HANDOFF.md` (sekce „Co je OTEVŘENÉ") |
| Jak se předává mezi sessionami | `PREDAVANI-SESSION.md` |
| Jaká pravidla platí napříč sessionami | `AGENTS.md` |
| Jaké jsou pasti prostředí | skill `dsh-prostredi` |
| Jak ověřit, že brána měří | skill `overovani` |
| Co se zapsalo do skillů a kdy | `SKILLY-AKTUALIZACE.md` |
| Které číslo je z jakého měření | `HANDOFF.md` §17 / §16 (u každého je příkaz) |
| Návrhy, které ještě nikdo neschválil | **§6 tohohle dokumentu** |

---

## 8. Jak kroniku udržovat (závazné pro každou session)

1. **Na konci session přidej JEDEN řádek** do tabulky §1 — datum, označení
   session, typ, co udělala, **hlavní naměřené číslo**, rozsah omylů.
2. **Nový nález** → řádek do §2 (s předponou podle místa vzniku).
3. **Nový omyl** → do `HANDOFF.md` §8 (tabulka je společná) **a** přepočítej
   řádek svého bloku v §3.
4. **Nové poučení** → §4, **jen s naměřeným případem**; když je to past
   prostředí, patří **i do skillu**.
5. **Nový návrh** → **§6** se stavem `NEOVĚŘENO`; **následující session** ho
   potvrdí, zamítne nebo odloží.
6. **Nic nemaž.** Historická čísla se **nepřepisují** — když zestarají, označí
   se jako „ve svém čase správná" (`AGENTS.md`).

**Ověření:** `python _analyza\kronika-kontrola.py` — zkontroluje, že tabulka §1
má řádek pro každou session z `HANDOFF.md` §17, že počty omylů v §3 sedí na
tabulku v `HANDOFF.md` §8 a že každý nález z §2 je zmíněný v `HANDOFF.md`.

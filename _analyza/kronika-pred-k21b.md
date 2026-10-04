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

| **17** | 2. 10. 2026 16:1x | **akční** | **Granule `tests.harness`** (rozhodnutí uživatele) + lék na **H12**: atrapa v rozporu → **M3 chycena**; ruční seznamy nahrazeny **projitím složky**; úklid worktree | M3 s vrácenou vadou: **65/2** (dřív **nechycena**); projití složky **405 souborů** (dřív 127 ze seznamu); skilly **12 z 12** (dřív 5); roadmapa **22 granul**, lint beze změny (**14 problémů**) | **72–79** |

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

---

## 3. Počty omylů — jediné místo, kde je vidět TREND

**Proč to tu je zvlášť:** `AGENTS.md` říká *„počítej, že i tvoje první číslo bude
někde mimo."* Tahle sekce to **dokládá čísly** — a je to jediné místo, kde je
vidět, **jestli se podíl vad měřidla zlepšuje**.

| Co | Naměřeno | Odkud |
|---|---|---|
| **omylů celkem** | **74** | `python _analyza\kronika-kontrola.py` — počítá řádky tabulek omylů v `HANDOFF.md` §8, 8b–8h |
| **z toho vad MĚŘIDLA** | **58 = 78 %** | ruční klasifikace u každého omylu (sloupec „Jak to vzniklo") |
| **z toho vypadalo jako nález o CIZÍM kódu** | **31** | tamtéž |
| **bloků omylů** | **8** (1–13, 8b–8h) | tamtéž |

> **⚠ POČTY SE POČÍTAJÍ, NEODHADUJÍ.** Naměřeno 2. 10. 2026 (omyl **60**):
> první verze tabulky níž měla u bloků **8d** a **8e** čísla **5** a **10** —
> byla to **špatná čísla**, protože je session napsala **odhadem z přečteného
> textu**. Odhalila to až **kontrola kroniky**, ne pozornost. Nástroj na
> přepočet: `python _analyza\s18-prepocitej-omyly.py --zapis`.

**Podrobná tabulka po blocích** (číslování bloků odpovídá `HANDOFF.md` §8, 8b–8h):

| Blok | Session | Počet | Z toho vad MĚŘIDLA | Z toho vypadalo jako nález o CIZÍM kódu |
|---|---|---|---|---|
| 1–13 | 30. 9. – 1. 10. | 13 | **9** | — |
| **8b** | ověřovací 1. 10. | **10** | **6** | **5** |
| **8c** | akční 2. 10. 11:3x | **5** | **4** | **2** |
| **8d** | plánovací 2. 10. 10:1x | **6** | **5** | **2** |
| **8e** | akční 2. 10. 11:0x | **11** | **9** | **5** |
| **8f** | plánovací 2. 10. 12:1x | **10** | **9** | **4** |
| **8g** | plánovací 2. 10. 13:0x | **11** | **8** | **3** |
| **8h** | akční 2. 10. 16:1x | **8** | **8** | **4** |
| **celkem** | | **74** | **58 = 78 %** | **31** |

> **⚠ TREND, KTERÝ JE VIDĚT A JE NEPŘÍJEMNÝ:** podíl omylů **v měřidle**
> **neklesá** — drží se kolem **80 %**, a blok **8h** má dokonce **8 z 8**
> (100 %). To **není** náhodný šum: znamená to, že **nejrizikovější část práce
> není „napsat opravu", ale „změřit, že oprava funguje"**. A že se to
> **opakuje i po 74 zaznamenaných omylech** — tedy že **znalost pasti sama
> nestačí** (nejlépe to dokládají omyly 72–74: **tři kola** hledání správného
> kritéria na jednom souboru).
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
| **L16** | **Když brána sama obsahuje VZOREK hledané vady, musí se odlišit VÝZNAMEM, ne TVAREM** | naměřeno 2. 10. 2026 (omyl **72–74**): projití složky ohlásilo rozbitou diakritiku ve **třech správných branách** — ty mají vzorek rozbitých znaků **jako literál** (musí, jinak by neměly co hledat). Kritérium „dva znaky po sobě" selhalo (hlásilo i hlášku ve správném souboru) a půlparser `bez_komentaru()` selhal na **jednosloupcových uvozovkách** (`"Ã"` je literál). Opravilo to až **významové** kritérium: rozbité znaky smí být jen na řádku, který vzorek **definuje nebo používá**. **Čtvrtá variace téže pasti** jako `overovani` §8.3 | `overovani` §8.3, `_analyza\g1-diakritika-novych.py` |
| **L17** | **Mutační test bez fixtury ve TVARU, který vadu způsobil, je slepý** | naměřeno 2. 10. 2026 (nález **H16**): `h17-kronika-mutace.py` testoval bránu **jen na živé kronice**, a ta v době testu neměla ve výřezu **tabulku nálezů** → vada (54 omylů místo 10) **testem prošla** a projevila se až v praxi. Fixtura, která ten tvar vyrobí **řízeně** (`t3-kronika-mutace.py`), našla **dvě další vady brány** (H17). **Obecně: test na živém dokumentu měří dnešní podobu dokumentu, ne odolnost brány** | `HANDOFF.md` §21.4, `_analyza\t3-kronika-mutace.py` |
| **L14** | **Filtr, který dostane KRÁTKÝ sha, vrátí PRÁZDNO — a prázdno vypadá jako „ještě nic"** | naměřeno 2. 10. 2026 (omyl **69**): `GET /actions/runs?head_sha=c40bdd5` → **`total_count: 0`**, a já **26 minut** čekal na workflow, který **už skončil** (`completed/success`). Se **plným** sha (`c40bdd556b67f9ac95a82b6c1c8798f926f431fd`) vrátí **2 běhy**, oba `success`. Skutečný důkaz nasazení přišel z **`last-modified`** (13:18:06 vs. push 13:16:50), ne z čekacího skriptu | `HANDOFF.md` §19.1, `_analyza\p19b-cekej-pages.mjs` |

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
| Návrhy, které ještě nikdo neschválil | **§5 tohohle dokumentu** |

---

## 8. Jak kroniku udržovat (závazné pro každou session)

1. **Na konci session přidej JEDEN řádek** do tabulky §1 — datum, označení
   session, typ, co udělala, **hlavní naměřené číslo**, rozsah omylů.
2. **Nový nález** → řádek do §2 (s předponou podle místa vzniku).
3. **Nový omyl** → do `HANDOFF.md` §8 (tabulka je společná) **a** přepočítej
   řádek svého bloku v §3.
4. **Nové poučení** → §4, **jen s naměřeným případem**; když je to past
   prostředí, patří **i do skillu**.
5. **Nový návrh** → §5 se stavem `NEOVĚŘENO`; **následující session** ho
   potvrdí, zamítne nebo odloží.
6. **Nic nemaž.** Historická čísla se **nepřepisují** — když zestarají, označí
   se jako „ve svém čase správná" (`AGENTS.md`).

**Ověření:** `python _analyza\kronika-kontrola.py` — zkontroluje, že tabulka §1
má řádek pro každou session z `HANDOFF.md` §17, že počty omylů v §3 sedí na
tabulku v `HANDOFF.md` §8 a že každý nález z §2 je zmíněný v `HANDOFF.md`.

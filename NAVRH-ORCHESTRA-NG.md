# NAVRH-ORCHESTRA-NG — technický návrh nové generace orchestra

> **Co tenhle dokument JE:** **návrh architektury** (design), ne stav a ne zadání.
> Popisuje, jak má vypadat orchestra, která **není vázaná na jednu technologii**,
> **přizpůsobuje se dostupným modelům** a **spolehlivě vyvíjí kvalitní produkt**.
> Neříká, co je dnes hotové — to je v `HANDOFF.md`.
>
> **Co tenhle dokument NENÍ:** není to záznam o provedení (nic se podle něj ještě
> nedělalo) a není to závazek. Je to **návrh, který se dá odmítnout** — včetně
> tří variant a měřitelných podmínek, za kterých je návrh špatný.
>
> **Datum vzniku:** 5. 10. 2026 (session P15, psaná v `C:\Users\Ssevc\Local-Deepseek`).
> **Datum spotřeby:** **návrh se spotřebovává rozhodnutím** o variantě (§14).
> Do té doby platí celý; po rozhodnutí platí jen zvolená varianta a kapitoly,
> na které odkazuje implementační plán `PLAN-ORCHESTRA-NG.md`.
> **Až se podle návrhu začne stavět, doplň sem, co z něj bylo provedeno** —
> jinak se za dva dny čte jako popis dneška (past `dokumentace` §1.2).
>
> **Odkud brát současný stav:** `E:\Workspaces\forge-orchestra\HANDOFF.md`
> (stav) + živé měření (`git`, `/health`, `/roadmap`). **Tenhle dokument žádný
> stav netvrdí** — kapitola §2 nese čísla **s datem a zdrojem**, protože bez
> toho se z měření stane dojem.

**Podklady, ze kterých se vychází** (všechno naměřené, ne odhadované):

| Dokument | Co z něj je | Datum měření |
|---|---|---|
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` | třídy selhání **S1–S16**, S17/S18, tři strukturální místa tichých selhání, ekonomie změny, „co analýza nezjistila" | 1. 10. 2026 |
| `ANALYZA-HLOUBKOVA-ORCHESTRA.md` | **S19–S30**, skutečný šev systému, dvě varianty návrhu | 1. 10. 2026 |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` | **S31–S37**, dvě vrstvy mechanismu selhání | 2. 10. 2026 (snapshot 05:45) |
| `FORGE-ORCHESTRA-MOZNOSTI.md`, `ORCHESTRA-STAV-A-ANALYZA.md` | rejstřík návrhů **L1–L17 / ST1–ST10** a jejich stav | 30. 9. – 1. 10. 2026 |
| `conductor/src/index.ts`, `conductor/schema.sql`, `repo/.forge/*`, `repo/.github/workflows/*` | **přímé čtení kódu** (řádky níž jsou z tohoto čtení) | 5. 10. 2026 |
| `PLAN-ROZVOJ-ORCHESTRA.md`, `PLAN-ORCHESTRA-AI-AGENTI.md`, `PLAN-VISION-ORCHESTRA.md`, `PLAN-DALSI-KROK.md` | co už bylo navrženo, rozhodnuto a zamítnuto | 1.–2. 10. 2026 |
| `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` | naměřené vady **designu a plánování** (smlouvy bez tvaru dat) | 2. 10. 2026 |
| `C:\Users\Ssevc\Local-Deepseek\{ANALYZA-VYVOJ-APLIKACI-A-HER,ANALYZA-EFEKTIVITY-DSH,RESEARCH-public-repos,MOZNOSTI-AGENTA}.md` | ekonomika, meze agenta, poučení z cizích projektů | 30. 9. – 2. 10. 2026 |

> **⚠ Kvalifikátor, který platí pro celý dokument:** většina čísel v §2 vznikla
> **měřením jiných session** a je převzatá **s uvedeným zdrojem**. Co jsem
> ověřil **vlastním čtením kódu**, je označené **(vlastní čtení 5. 10. 2026)**.
> Co ověřené není, je označené jako *nepřevzaté* — a v §18 je k tomu tabulka.

---

# ČÁST I — VÝCHODISKA

## 1. Verdikt v pěti větách

*(Napsán na začátek a zopakován na konec v §20 — když se nezmění, je to taky
výsledek.)*

1. **Jádro orchestra je technologicky neutrální už dnes** — v `conductor/src/index.ts`
   (1 497 řádků) je jediná zmínka o Godotu a jsou to **dva komentáře** (ř. `304`,
   `384`, *vlastní čtení*); veškerá vazba na stack bydlí ve workflow a v branách.
2. **Skutečný šev tedy není „orchestra × hra", ale „orchestrace × engine"** —
   a vede **dovnitř `.forge/`** (3 brány neutrální, 3 godot-specifické,
   2 infrastruktura enginu); projekt dosud investoval do švu, který není ten
   pravý (šablona, `game_id`, registr her).
3. **Modelová vrstva se neadaptuje — jen zkouší pořadí.** `providers.json` je
   ručně udržovaný seznam s lidskými odhady (`anyPriority`, `skromny`), probe je
   `ping` s `max_tokens: 8` (`pick-provider.mjs:138–166`, *vlastní čtení*), takže
   měří **dostupnost, ne způsobilost**; systém se z žádného výsledku neučí.
4. **Důsledek je naměřený a drahý:** úspěšnost free modelů **28 z 247 běhů
   (11,3 %)**, jedna úspěšná granule stojí **~9 běhů**, orchestra je **82,7 %
   času mrtvá** a **55 % selhaných běhů skončilo do 30 s** — tedy na překážce,
   která se dala poznat před dispatchí.
5. **Nová generace nemá být přepis, ale přesun těžiště:** zachovat dvanáct
   nosných konstrukcí, které jsou dnes správně (pull-worker, polling,
   `done = ok && merged`, řádkové zámky, `null ≠ []`), a **přidat tři vrstvy,
   které chybí** — **kontrakt** (deklarovaný stack a smlouvy), **paměť modelů**
   (měřená způsobilost místo seznamu) a **jednotný verdikt brány**
   (`pass/fail/not_run/unknown`), ze kterého se nedá tiše vyklouznout.

---

## 2. Co je dnes naměřeno (a co z toho plyne)

**Každé číslo má zdroj a datum.** Kde je zdroj „vlastní čtení", je u toho řádek.

### 2.1 Ekonomika a propustnost

| Veličina | Naměřeno | Zdroj | Co z toho plyne pro návrh |
|---|---|---|---|
| Úspěšnost běhů agenta | **28 / 247 = 11,3 %** | `hl-priciny.mjs` (247 běhů) | rozhoduje **ocas**, ne průměr: 20 úloh uspělo na 1. běh, 3 potřebovaly **9** |
| Běhů na jednu úspěšnou granuli | **~9** | tamtéž | 8 z 9 běhů se dá **nevyrobit** (kdyby se poznala příčina předem) |
| Selhané běhy do 30 s | **55 %** | tamtéž | to nejsou „těžké granule", to jsou **nefeasibilní dispatche** |
| „Agent nic nezměnil" | **95×** | tamtéž | to je **vada editovatelné plochy nebo promptu**, ne modelu |
| Selhání na testech | **82×** | tamtéž | to je **vada zadání nebo brány**, ne modelu |
| Selhání na parsování | **27×** | tamtéž | formát odpovědi je **kontrakt**, dnes není vynucený |
| Využití orchestra | **6,86 h z 49,35 h = 13,9 %** (mrtvá 82,7 %) | `hl-vytizeni.mjs` | orchestra čeká víc, než pracuje — a **není to kvůli červenému CI** |
| Prompt běhu | **~14,4 tis. tokenů** (tři různá čísla: 14 398 / 14 377 / 14 402) | `§18.17`, log #146 | pevná část (3 839 t. `CONVENTIONS.md` + ~2 166 t. systémový prompt) je **většina vstupu** |
| Volání modelu na běh | **1** | `ANALYZA-HLOUBKOVA-ORCHESTRA.md` Q3 | pokus je „jeden výstřel" — proto je drahé ho spálit |
| Denní kapacita free řetězce | gemini **~20/den**, openrouter **50/den**, cerebras **$5/30 dní**, groq efektivně **~13–14 běhů/den** | `providers.json` + `§18.17` | **kvóta je vzácnější než čas** — plánovat podle ní, ne podle minut |
| Silné granule | **9 z 22** (`model: strong`), ale silné modely má jen mistral, cerebras a groq — **a groq se do limitu nevejde** | `.forge/roadmap.json`, §18.17 | kapacita silné třídy je **fakticky mistral + cerebras**; to je úzké hrdlo |
| Náklady DSH na vývoj her | **$31,27 / 15 sessions** (50,1 % účtu na 36 % requestů) | `ANALYZA-VYVOJ-APLIKACI-A-HER.md` §2 | orchestra na free modelech je **cenová páka**, ne projekt pro zábavu |

### 2.2 Modelový řetězec — jak rozhoduje dnes

| Co | Kde | Jak to funguje | Mezera |
|---|---|---|---|
| Zdroj pravdy o modelech | `repo/.forge/providers.json` | ruční seznam 5 poskytovatelů; strojově čitelná jsou **jen** `name/baseUrl/keyEnv/models/strongModels/skromny/anyPriority` | **limity jsou jen v komentářích** (`_popis`, `_anyPriority`) — žádné TPM, žádné okno kontextu |
| Volba poskytovatele | `pick-provider.mjs:197–213` | `probe()` = `POST /chat/completions` s textem `ping`, `max_tokens: 8`, timeout 45 s; **první `ok` vyhrává** | **měří dostupnost, ne způsobilost** — „odpoví na ping" ≠ „zvládne 14k prompt" (naměřeno: gemini 429 v běhu #61) |
| Silná třída | `FORGE_MIN_STRONG=strong` → `strongProviders()` (`provider-choice.mjs:65–69`) | **přepíše `models` na `strongModels`** | „strong" je **vlastnost poskytovatele**, ne měřená způsobilost na konkrétní úloze |
| Rotace u `strong` | `orderProviders(providers, run_key)` → `fnv1a` | posun podle `run_key` | hash, ne informace — nerozlišuje, **na čem** model minule selhal |
| Rotace u `any` | `rotateByAttempt(štědré, FORGE_ATTEMPT)` | posun mezi štědrými | totéž |
| Když selže | `agent.yml:254` | obsahuje-li log rate-limit vzorec, **druhý poskytovatel se nezkouší** | šetří kvótu, ale **nerozlišuje příčinu** — u `nochange` je rotace k ničemu (naměřeno: 3× a 5× stejné selhání) |
| Evidence mrtvého modelu | `providers-check.mjs` (denně 06:00 UTC) | `GET /models` + ping, `classify()` rozliší 429/503/404/401/403 | výsledek jde **jen do GitHub issue**; `providers.json` se needituje a **nikdo si toho nemusí všimnout** |
| Trvalá paměť | `provider.json` | **poslední vybraný** poskytovatel | **žádná historie výsledků** — systém se neučí |

### 2.3 Stavový automat — naměřené díry

*(Tohle je jádro „spolehlivosti": nejsou to kosmetické vady, ale místa, kde stav
lže nebo utíká.)*

| # | Co je naměřeno | Kde | Mechanismus |
|---|---|---|---|
| **S12** | Nová granule se 3 h nevydá | `index.ts:643–646` + guard | **OPRAVENO v kódu (B1, 2. 10. 2026)** — `ts = r.rfail \|\| r.tupd` (`index.ts:618`) a `naposledy_selhalo` je při vzniku `NULL` |
| **S13** | Cooldown se obchází přes `/report` | `index.ts:1329–1336` | **OPRAVENO** — `/report` dnes píše `naposledy_selhalo` v **obou** větvích (`:1464–1472`, *vlastní čtení*) |
| **S14** | Strop pokusů váže **úkol**, ne **granuli**; watchdog `ESCALATE_AFTER=8 > MAX_ATTEMPTS=5` se **nikdy nespustí** | `index.ts:246`, `:328`, `:394`, `:679`, `:709`, `:751` | `roadmapTick` zakládá pro každý retry **nový úkol s `attempts=0`** |
| **S15** | Zámek `owns` v dispatch smyčce neblokoval nic | `index.ts:302–310` vs. `:774–776` | **OPRAVENO** (`6d2a856` + regresní test 8 kontrol) |
| **S38** | **Nová třída (vlastní čtení 5. 10. 2026):** cesta přes timeout **obchází strop pokusů** — `stale-recovery` nastaví `tasks.status='failed'` a `updated_at=now` (`index.ts:829–833`), ale **`roadmap.naposledy_selhalo` nezapíše**; guard pak padne na fallback `r.rfail \|\| r.tupd` (`:618`) → řádek je „mladý" → blok na `RETRY_HOURS` → po 3 h `roadmapTick` založí **nový úkol s `attempts=0`** (`:751`) → **granule jede donekonečna** | `index.ts:618`, `:829–833`, `:751` | **dva zapisovatelé téhož stavu, jeden z nich neukotví protějšek** — přesně rodina S29–S36 |
| **S39** | `FORGE_MIN_STRONG=only` **nevypne strong filtr, ale obě rotace**; komentář `pick-provider.mjs:106` tvrdí opak | `pick-provider.mjs:95`, `:184` | stav, jehož jméno neodpovídá chování |
| **S40** | `max_lines` se **nedostane do promptu** — model neví, kolik řádků smí; limit se měří až v auto-merge gate | `agent.yml:233` vs. `:642` | rozhodnutí je **brána**, ne **zadání** |
| **S41** | `size_lines` a `model` se **nikde nekříží**; pravidlo „`size_lines > 60` ⇒ `strong`" je jen komentář v `providers.json:27–30` | `index.ts:149–153`, `:156–161` | nepodložené tvrzení v dokumentaci vydávané za invariant |
| **S42** | `maxLinesOf` bere z `size_lines` **první číslo** — `"60-120"` → **60**; formát není validován | `index.ts:149–153` | tichá změna významu vstupu |
| **S43** | Párování běhu je **přes `run-name` workflow** (řetězec v názvu běhu); když ho workflow nevyrobí, běh se **nikdy nespáruje** → timeout → S38 | `index.ts:361–362` vs. `agent.yml:6` | smlouva **mezi systémy**, kterou drží jen dohoda |
| **S44** | `kind` granule **nic neřídí** (jen notifikace) — dispatch nerozlišuje druh práce | `roadmap.json:19` vs. `agent.yml` | klasifikace bez čtenáře |
| **S45** | `catch { }` polyká chybu a **není vidět v odpovědi tiku** (např. párování podle titulků, `:588`) | `index.ts:588`, `:506`, `:548–550`, `:604` | tichý výpad schopnosti |

> **Číslování navazuje na S1–S37.** Řada **S19–S28** nebyla v podkladech
> k dispozici (její plné znění je v `ANALYZA-HLOUBKOVA-ORCHESTRA.md`, 1. kolo) —
> **může se stát, že některá z tříd S38–S45 je tam už pojmenovaná.** Pak platí
> **starší číslo** a tenhle záznam se jen doplní. Neoznačuji to za nové, dokud
> se to neporovná.

### 2.4 Brány — kde měřily a kde přestaly

| Co | Naměřeno | Zdroj |
|---|---|---|
| Kontrola **proběhla?** se nevykazuje u celku | `gates_run/total` neexistuje; přeskočená kontrola není v souhrnu vidět | S3, S27 |
| `check-wiring.py` nad **0 souborů** hlásí „Vše v pořádku" s `exit 0` | `check-wiring.py:73`, `:169` | skill `orchestra` |
| `check-assets.py` hledá animaci v `assets/sprites/walk_*.png`, kde je **0 souborů** → `min_silhouette_iou: 0.80` se **nikdy neuplatní** | `check-assets.py:232–252` | tamtéž |
| `check-schema.py` **tiše přestal měřit** výchozí buňku (regexy nenašly nic → cyklus nad prázdným seznamem → zelená) | naměřeno 1. 10. 2026 | tamtéž |
| Brány měřily **přímost metod**, ne chování: `has_method(...)`, `if load(...) != null:` → prošly **tři PR, která nemohla fungovat** (`hud.gd` spadl v `_ready()`, `save.gd` uložil **35 B** a vrátil `true`, `mining.gd` spadl na Godot 3 API) a CI hlásilo **39 kontrol, 0 selhání** | `OTEVRENA-TEMATA.md` ř. 70–84 | 2. 10. 2026 |
| `acceptance` a `provides` z roadmapy mají **0 čtenářů v kódu** | HLOUBKOVA-2 §3.1 | 2. 10. 2026 |
| `merged` je **mrtvá hodnota** — systém ji načte a zahodí (rozhoduje jen `ok`) | `index.ts:367`, `:375`, `:386`, `:409` | **OPRAVENO A1** (`ok && merged`) |
| `validate-all.mjs` je **PŘEHLED, ne brána** (nemá `sys.exit`) | NA23b | platí dál |
| 5 bran **nemá offline test** (`agent.yml`, `check-assets.py`, `check-wiring.py`, `verify-level-render.py`, `install-into-repo.ps1`) | ARCHITEKTURY §7 | 1. 10. 2026 |

### 2.5 Tichá selhání — tři strukturální místa a dvě vrstvy mechanismu

**Tři strukturální místa, kde se chyba ztrácí** (`ANALYZE-ARCHITEKTURY` §1):

1. **Rozchod mezi „co je na disku" a „co je v gitu"** — naměřeno: 8 změněných
   trackovaných + **4 důležité soubory vůbec netrackované**.
2. **Nástroje se množily místo aby se nahrazovaly** — dvě verze téhož pravidla
   a ověřovací nástroj měří **tu starou a slepou**.
3. **Chybějící onboarding nové hry** — cesta, kterou se zakládá nová hra, je
   **nefunkční** (vyžaduje `projects/`, které neexistuje; posílá na smazaný
   `forge.cmd`), takže se hra zakládá ručním kopírováním a **dědí pozůstatky**
   (31 granul cizí hry, `FORGE_SECRET` v `.env`, odkaz na jinou hru).

**Dvě vrstvy mechanismu** (`ANALYZA-HLOUBKOVA-ORCHESTRA-2` §O5) — a to je
nejcennější věta z celé analýzy:

| Vrstva | Co se ztratí | Projev | Kdo si toho všimne |
|---|---|---|---|
| **Staré (S1–S18)** | **měření** | **zelená nad prázdnem** | nikdo, dokud se nepodívá |
| **Nové (S29–S36)** | **protějšek** | **zelená nad nepravdou** | **nikdo, protože není proti čemu** |

> **Tohle je zadání pro návrh, ne nález:** nová orchestra musí mít
> **u každého stavu jeho protějšek** a **u každého měření jeho „proběhlo?"**.
> Cokoli jiného je kosmetika.

### 2.6 Meze prostředí, které návrh musí respektovat (nemění se návrhem)

| Mez | Naměřeno | Důsledek pro návrh |
|---|---|---|
| `read_image` **není v GitHub Actions** | agent v CI se na artefakt **nemůže podívat**; je tam jen `.forge/vision.mjs` (Gemini, kvóta) | vizuální ověření musí být **schopnost uzlu**, ne předpoklad CI |
| Blender **není v CI runneru** (instalace ~300 MB) | render jen **lokálně** nebo commitovat hotové | „render" je **druh práce**, ne krok každého běhu |
| Subagenti mají **`maxDepth: 1`** | orchestrace musí být **vlastní smyčka**, ne rekurze agentů | řízení je **stavový automat**, ne „agent, který si zavolá agenta" |
| Free klíče jsou **per repo** (GitHub ToS) | druhá hra **nezdvojnásobí kapacitu**, jen si ji rozdělí | plánovat **kvótu per klíč**, ne „běhy per hra" |
| Instrukční rozpočet `AGENTS.md` **65 536 B** na celý řetězec | širší soubor se **zahodí dřív**, než zkrátí konkrétnější | orchestra si **nesmí vozit pravidla v promptu**, ale v **kontraktech v repu** |
| Sandbox blokuje podprocesy s piped stdio (`EPERM`) | testy, které tím spadnou, **nejsou rozbité** | brány musí umět běžet **bez síťových podprocesů**, nebo to říct |

---

## 3. Katalog: co je dnes dobré a musí se zachovat

**Tohle není seznam detailů — jsou to nosné konstrukce s naměřeným
zdůvodněním v kódu.** Návrh, který je zahodí, zopakuje chyby, které už jsou
jednou zaplacené.

| # | Konstrukce | Kde | Proč se nesmí ztratit |
|---|---|---|---|
| 1 | **Pull-worker místo self-hosted runneru** | `index.ts:8–10`, `worker.mjs:8–12` | telefon za NAT, žádné otevírání portů, GitHub varuje u veřejného repa |
| 2 | **Polling místo reportu z workflowu** | `index.ts:287–291` | conductor vidí i běh, který spadne **dřív**, než by poslal report; v repu hry nejsou další tajemství |
| 3 | **Dva joby: klíče vs. zápis** | `agent.yml:13–16` | klíč z LLM jobu se **nemůže** dostat do commitu |
| 4 | **`done` jen když `ok && merged`** | `index.ts:385`, `:400–405` | „hotovo" má **protějšek v `main`**; naměřeno na #139/#140/#136 |
| 5 | **`done: true` v souboru je tvrzení, ne fakt** — ověřuje se proti `origin/main`, `null ≠ []` | `index.ts:479–516`, `:684–711` | „nevíme" se nesmí zaměnit s „nic tam není" |
| 6 | **Optimistický zámek na claim** (`UPDATE … WHERE status='ready'`) | `index.ts:942–946`, `:988–992` | souběh je řešený **v DB**, ne v aplikaci |
| 7 | **Zámky `owns` scoped na repo** (`{repo}/{soubor}`) | `index.ts:302–310` | dvě hry se stejným `scripts/game.gd` se neblokují |
| 8 | **`blocked` je terminální** a `DELETE FROM tasks` nejde | `index.ts:1324–1327` | cizí klíč `runs → tasks`; mazání by rozbilo běhy |
| 9 | **Brána musí mít jak selhat** (`exit 1` v auto-merge) | `agent.yml:698` | bez toho je „nesloučeno" **zelený běh** |
| 10 | **Agent nesmí měnit vlastní brány** (`tests/`, `.github/`, `.forge/`, `project.godot`) | `agent.yml:625–631` | princip je přenositelný, i když cesty ne |
| 11 | **Nezávislé potvrzení CI** (ne jen agent sám) | `agent.yml:647–674` | stejný princip jako „autor není reviewer" |
| 12 | **Poctivost měření**: `null ≠ []`, „kontrola NEPROBĚHLA" jako vada, mrtvá větev se pojmenuje, komentáře se před hledáním vzorců odstraní | `check-schema.py:43–49`, `:257–262`, `:353–361`, `:221–225` | **nejcennější přenositelná znalost v celém projektu** |
| 13 | **Rotace modelů jako čistá funkce bez sítě** | `provider-choice.mjs` + test | jediná část modelové vrstvy, která je **testovatelná offline** |
| 14 | **Konfigurace modelů na jednom místě**, ne v kopiích her | `pick-provider.mjs:27–30` | mrtvý model se opraví **jednou** |

> **Pozor na č. 14:** dnešní provedení má **vědomý kompromis** — seznam modelů
> z orchestra, ale **směrovací metadata VŽDY z lokální kopie** (`pick-provider.mjs:32–38`),
> protože `raw.githubusercontent` má CDN cache. To je **příznak**, že „jeden zdroj
> pravdy" je dnes ve skutečnosti **dva**: konfigurace se distribuuje kopírováním
> a cache rozhoduje, která verze platí. Návrh to řeší **verzovaným kontraktem**
> (§8.6), ne dalším kompromisem.

---

## 4. Skutečný šev (a proč je jinde, než si projekt myslí)

**Projekt si myslí, že šev je „mezi orchestrou a hrou"** — proto šablona, proto
`game_id`, proto registr her, proto dva synchronizační nástroje.

**Naměřeno je ale tohle:**

| Vrstva | Kolik | Vazba na engine |
|---|---|---|
| `conductor/src/index.ts` | 1 497 řádků | **0** — Godot jen ve **dvou komentářích** (ř. `304`, `384`, *vlastní čtení*) |
| `.forge/` šablony | 24 souborů | **17 neutrálních**, 3 godot-specifické (`check-wiring.py`, `check-schema.py`, `verify-level-render.py`), 2 infrastruktura enginu (`install-godot.sh`, `files-to-edit.mjs`) |
| **vazba na stack** | `.github/workflows/ci.yml`, `agent.yml`, `release.yml` | **tady** — `FORGE_GODOT`, cache `forge-godot-4.7.2` na 3 místech, `res://tests/run_tests.gd`, `--write-movie`, export presety `Linux`/`Web`/`Windows Desktop` |
| **agent (editor)** | `agent.yml:226–235` | **aider** s `--edit-format diff`, `--map-tokens 0`, `--file`/`--read` |

> **Verdikt:** šev je **„orchestrace × engine"** a vede **dovnitř `.forge/`
> a dovnitř workflow**. To je dobrá zpráva: **jádro se měnit nemusí** —
> měnit se musí **to, co je kolem něj**, a to je přesně to, co nová generace
> dělá (adapter + deklarace projektu).

**Druhý šev — „conductor × GitHub Actions" — není šev, je to díra:**
conductor se ptá na `conclusion` **celého workflow**, takže nevidí, co se stalo
v jobu `auto-merge` (S32/S33). Návrh to řeší **stavem s protějškem** (§11),
ne dalším dotazem.

---

## 5. Co znamená „kvalitní produkt" (a proč to dnes nejde změřit)

Dnešní definice hotového je **„PR je sloučený"**. To je nutná, ale **zdaleka
ne postačující** podmínka — a je to **naměřené**:

| Co prošlo, a přitom to nebylo hotové | Čím to prošlo |
|---|---|
| `hud.gd` se v `_ready()` rozbil, label se nikdy nepřidal | `has_method("update")` |
| `save.gd` uložil **35 B** a vrátil `true` | `has_method("save")` |
| `mining.gd` spadl na Godot 3 API | podmíněný test, který se přeskočil |
| `world.nodes` dodán jako **prázdný soubor (0 B)** | CI to nechytilo |
| `world.map` a `entity.player` byly `done`, ale práce v `main` nebyla | stav v plánu bez protějšku v repu |
| tři PR prošla zeleným CI a **nemohla fungovat** | brány měřily **přítomnost**, ne **chování** |

**Poučení, které se v projektu opakuje třikrát:** *hotovo = soubor je v `main`
**a** brána jeho funkci **ZAVOLALA*** — a soubor, který součástí být **MÁ**, musí
při nenačtení **SELHAT**.

**A druhá polovina, kterou je potřeba přiznat:** orchestra **neumí posoudit
obsah** — `check-assets.py` je spokojený (38×95 px, 1103 barev, 0 děr) a
**neumí říct, jestli je na spritu to, co má být**. Naměřeno 30. 9. 2026:
při migraci na izometrii byl **hráč překrytý dlaždicemi** a testy, schéma
i assety byly zelené — chybu našel až **pohled na snímek**.

> **Z toho plyne závazek návrhu, ne přání:** „kvalita produktu" musí být
> **deklarovaná jako seznam ověřitelných tvrzení o produktu** (ne o kódu),
> z nichž každé má **svůj nástroj nebo svého nositele** — a **co nástroj nemá,
> musí být vidět jako „čeká na člověka"**, ne tiše odškrtnuté.

---

## 6. Co je dnes rozhodnutí a co historický nános

**Rozhodnutí (má zdůvodnění v kódu a drží) — zachovat:**

1. Tvrdá brána vs. poradní kontrola (vision **neblokuje** záměrně: falešný
   poplach je dražší než přehlédnutí).
2. Dva joby v `agent.yml` (klíče vs. zápis).
3. Soubory granule jako `--file`, závislosti jako `--read` — vzniklo z naměřené
   0% úspěšnosti (**aider odmítne editovat soubor, který v chatu není**).
4. Rotace modelů podle `run_key`/`attempt`.
5. Cooldown vynucený **časem**, ne `status`em.
6. `providers.json` rozdělený na „čerstvé" a „směrovací".
7. `blocked` je terminální.

**Historický nános (přežilo svůj důvod) — návrh s tím nepočítá:**

1. `install-into-repo.ps1` — celý postavený na `projects/<Projekt>` a `forge.cmd`
   (GameForge smazána 30. 9. 2026). **Hlavní onboardingová cesta je mrtvá větev.**
2. `repo/.forge/roadmap.json` — **31 granul hry, která se už nevyvíjí** *(po
   opravě L4 je 0 granul — nános je ale v tom, že to nikdo nehlídá)*.
3. `bin/task.mjs`, `wrangler.cmd`, `tools/test-local.ps1` — cesty `gameforge\…`.
4. `tools/kontrola-schematu.py` — **stará, slepá** verze brány; `validate-all.mjs:186`
   pouštěl **ji**, ne tu v `.forge/` (dvě verze téhož pravidla, S1).
5. `worker.mjs:83` — `FORGE_CMD` default na smazaný `forge.cmd`; krok `forge:`
   je nepoužitelný a krok `blender:` **neexistuje**.
6. `release.yml` v gitu — odkaz na `forge-quest` (**jiná živá hra**). Na disku
   opraveno, necommitnuto.
7. `done_note` — pole, které říká „v D1 hotovo, ale PR není sloučené", a **0 čtenářů**.
   **Nemazat** — je to jediné čitelné svědectví o S29; má se začít **číst**.

---
# ČÁST II — NÁVRH

## 7. Dvanáct principů, na kterých návrh stojí

*(Každý princip je odpověď na **naměřenou** vadu z části I. Co princip nemá
příklad v měření, sem nepatří.)*

| # | Princip | Na jakou vadu odpovídá |
|---|---|---|
| **P1** | **Stav bez protějšku je zakázaný.** Každý stav musí mít **zařízení** (device), které ho dokáže vyvrátit: `done` → commit v `main` obsahuje `owns`; `pr_open` → číslo PR; `blocked` → důvod + `retry_at`. | S29–S36 („zelená nad nepravdou") |
| **P2** | **Měření musí říct, že proběhlo.** Každá brána vrací **jeden ze čtyř stavů** — `pass / fail / not_run / unknown` — a k tomu **počty**. `ran < declared` je vidět v každém výsledku. | S3, S27, „brána, která neproběhne" |
| **P3** | **Rozhodnutí se měří, netvrdí.** „Silný model" je **naměřená způsobilost**, ne položka v seznamu; „limit modelu" je **naměřený limit**, ne odhad v komentáři. | S41, S46, NA14 |
| **P4** | **Před opakováním se diagnostikuje.** Opakování je **funkce třídy selhání**, ne času ani rotace. | 95× „nic nezměnil", 3×/5× stejné selhání |
| **P5** | **Jeden zdroj pravdy na jeden údaj — a je deklarovaný.** Co je dnes ve třech ručních seznamech, je v jednom souboru projektu. | S1, S5, S27 |
| **P6** | **Jádro nezná technologii; technologie se deklaruje.** Rozhodovací logika je čistá funkce bez I/O; stack, engine a schopnosti uzlu jsou **data**. | skutečný šev (§4) |
| **P7** | **Každý stav má vlastníka a termín.** Žádné „čeká se" bez `deadline` a bez toho, kdo ho posune. | `awaiting_human` bez úklidu, S12/S38 |
| **P8** | **Chyba se polyká jen s událostí.** `catch` bez záznamu je vada; tichý výpad schopnosti je horší než pád. | S45 |
| **P9** | **Kontrakt nese tvar dat a přijímací kritérium** — ne jen jméno. A **někdo ho čte**; deklarace bez čtenáře je mrtvá brána. | S22 (`acceptance` 0 čtenářů) |
| **P10** | **Zdraví řídicího systému není zdraví cíle.** `/health` odpovídá i na „co dělá cíl". | S18 (7,5 h zelený conductor nad červeným repem) |
| **P11** | **Hotovo = artefakt v `main` + brána ZAVOLALA chování.** Ne „PR je sloučené", ne „test prošel". | `hud.gd`, `save.gd` (35 B), `mining.gd` |
| **P12** | **Co neumí stroj, musí být vidět jako „čeká na člověka".** Nikdy tiše odškrtnuté. | obsah spritu, hratelnost, kontaktní arch |

---

## 8. Vrstvy a kontrakty

### 8.1 Šest vrstev (a co je mezi nimi)

```
┌──────────────────────────────────────────────────────────────────────┐
│ 1. PLÁN            cíl → požadavek → schopnost → kontrakt → granule   │
│                    (data v repu projektu, verzovaná)                  │
└───────────────┬──────────────────────────────────────────────────────┘
                │  PLAN (DAG granulí + smlouvy + přijímací kritéria)
┌───────────────▼──────────────────────────────────────────────────────┐
│ 2. ŘÍZENÍ (jádro)  čisté funkce: fronta, leases, routing, klasifikace │
│                    BEZ I/O — testovatelné offline, přenositelné       │
└───┬───────────┬──────────────┬───────────────┬───────────────────────┘
    │ PORTS     │              │               │
┌───▼─────┐ ┌───▼──────┐ ┌─────▼──────┐ ┌──────▼──────┐
│ STAV    │ │ RUNNER   │ │ SCM        │ │ MODEL       │
│ (store) │ │ (host)   │ │ (git/PR)   │ │ (providers) │
│ SQLite/ │ │ Actions/ │ │ GitHub/git │ │ OpenAI /    │
│ D1/PG/  │ │ local/   │ │            │ │ Anthropic / │
│ files   │ │ docker   │ │            │ │ Gemini /    │
│         │ │          │ │            │ │ Ollama      │
│         │ │          │ │            │ │ + LEDGER    │
└─────────┘ └────┬─────┘ └────────────┘ └─────────────┘
                 │ WORK ORDER
┌────────────────▼─────────────────────────────────────────────────────┐
│ 3. VYKONÁNÍ   agent driver (aider | dsh | api-loop | cli)             │
│               + SCHOPNOSTI UZLU (capability host): test, build,       │
│                 screenshot, render, vision, read_image                │
└────────────────┬─────────────────────────────────────────────────────┘
                 │ ARTEFAKT (změna v repu)
┌────────────────▼─────────────────────────────────────────────────────┐
│ 4. OVĚŘENÍ    brány (gate protocol) + nezávislé potvrzení + coverage  │
└────────────────┬─────────────────────────────────────────────────────┘
                 │ VERDIKT (4 stavy + počty + důkazy)
┌────────────────▼─────────────────────────────────────────────────────┐
│ 5. PRODUKT    přijímací kritéria produktu + lidská fitness funkce     │
│               (milníky, ne každý PR)                                  │
└──────────────────────────────────────────────────────────────────────┘

Napříč: 6. ZÁZNAM — události (append-only) → projekce stavu; každá změna
        stavu má `cause` a každý stav má `device`.
```

**Proč zrovna takhle:** vrstvy 1, 2 a 5 dnes **neexistují jako kontrakty**.
Vrstva 1 je próza + konvence, vrstva 2 je promíchaná s I/O v jednom souboru
(`index.ts`, 1 497 řádků), vrstva 5 neexistuje vůbec. Vrstvy 3 a 4 existují
a jsou dobré — návrh je **nemění, jen jim dá rozhraní**.

### 8.2 Co je jádro a co obálka (měřitelné kritérium)

| Vrstva | Kde bydlí | Mění se při přidání technologie? |
|---|---|---|
| **Jádro** (rozhodování) | `core/` — čisté funkce, žádné `fetch`, žádný `DB` | **ne** |
| **Porty** (rozhraní) | `core/ports/*.ts` — typy, žádná implementace | ne |
| **Hostitelé** (I/O) | `hosts/worker/`, `hosts/local/`, `hosts/ci/` | ne (přidává se hostitel) |
| **Adaptéry stacku** | `adapters/<stack>/` | **ano — a jen tady** |
| **Deklarace projektu** | `.forge/project.json` v repu projektu | **ano — a jen tady** |
| **Brány** | `gates/` (obecné) + `adapters/<stack>/gates/` | ano, jen v adaptéru |

> **Měřitelné kritérium švu (a zároveň falzifikátor návrhu):**
> **přidání druhého stacku nesmí sáhnout na víc než 5 souborů mimo
> `adapters/<nový stack>/` a `.forge/project.json`.** Když jich je víc, šev
> není tam, kde si návrh myslí — a to se pozná **měřením**, ne dojmem.

### 8.3 `project.json` — jediná deklarace projektu

**Dnes:** cesty, brány, přípony a ochranná pravidla jsou **konstanty v nástrojích**
(`check-wiring.py:73`, `check-schema.py:212–218`, `baseline.py:60`,
`verify-level-render.py:209`, `agent.yml:625–631`) nebo **ve třech ručních
seznamech** pro synchronizaci (`kontrola-driftu.mjs` 12 souborů,
`sync-sablona-hra.py` 2 soubory, `sjednot-sablonu.py` textové náhrady).

**Nově:** jeden soubor v repu projektu. Návrh rozšiřuje `forge.config.json`
z `PLAN-ROZVOJ` F3.3 (který byl navržen a nedošel) o to, co se mezitím naměřilo
jako potřeba — **modelovou politiku**, **schopnosti uzlu** a **definici hotovo**.

```jsonc
{
  "schema": "forge.project/2",
  "project_id": "uo-shadows",
  "stack": { "adapter": "godot4", "version": "4.7.2",
             "languages": ["gdscript"], "engine_version_source": "project.godot" },

  // Co kde je — jedna deklarace místo konstant v šesti nástrojích.
  "paths": {
    "sources": ["scripts/"], "tests": ["tests/run_tests.gd"],
    "spec": "assets/spec.json", "levels": "assets/levels/",
    "sprites": "assets/sprites/", "audio": "assets/audio/"
  },

  // Příkazy. `null` = adaptér to neumí a MUSÍ to říct (ne mlčet).
  "commands": {
    "deps":    "pip install --quiet pillow",
    "prepare": "$FORGE_ENGINE --headless --path . --import",
    "syntax":  "$FORGE_ENGINE --headless --path . --check-only --script {file}",
    "test":    "$FORGE_ENGINE --headless --path . --script res://tests/run_tests.gd",
    "build":   "$FORGE_ENGINE --headless --path . --export-release {preset} {out}",
    "run":     "$FORGE_ENGINE --path . --rendering-driver opengl3",
    "screenshot": "$FORGE_ENGINE --path . --write-movie {out}/frame.png --quit-after {n}"
  },

  // Kdo smí co zapsat. Nahrazuje adresářovou konvenci zadrátovanou v agent.yml.
  "ownership": {
    "agent_writable": ["scripts/**", "assets/**"],
    "agent_forbidden": ["tests/**", ".forge/**", ".github/**", "project.godot",
                        "assets/spec.json"],
    "human_only": ["assets/spec.json", ".forge/project.json"]
  },

  // BRÁNY: deklarovaný seznam, ne objevený. Neúplnost se hlásí OBĚMA směry.
  "gates": [
    { "name": "schema",   "cmd": "forge-gate-schema",  "severity": "hard" },
    { "name": "wiring",   "cmd": "forge-gate-wiring",  "severity": "hard" },
    { "name": "assets",   "cmd": "forge-gate-assets",  "severity": "hard",
      "config": { "roles_source": "spec.json#roles" } },
    { "name": "render",   "cmd": "forge-gate-render",  "severity": "hard" },
    { "name": "behaviour","cmd": "adapters/godot4/gates/behaviour", "severity": "hard" },
    { "name": "vision",   "cmd": "forge-gate-vision",  "severity": "advisory",
      "requires": ["capability:vision"] }
  ],

  // DEFINICE HOTOVO — pro granuli i pro produkt.
  "definition_of_done": {
    "grain":   ["artifact_in_main", "gate_called_behaviour", "acceptance_all_pass"],
    "product": ["builds", "runs_without_script_error",
                "screenshot_reviewed_by_human", "acceptance_of_milestone"]
  },

  // MODELOVÁ POLITIKA: co projekt potřebuje, ne který model se použije.
  "model_policy": {
    "prompt_budget_tokens": 12000,
    "escalate_after_attempts": 3,
    "refuse_when_infeasible": true
  }
}
```

> **Tři věci, které tím zmizí:** (1) konstanty v branách, (2) tři ruční
> synchronizační seznamy, (3) adresářová konvence zadrátovaná ve workflow.
> **A jedna, která vznikne:** nový soubor musí být **v jednom** seznamu —
> a to se dá **vynutit testem** (onboarding jako test, `PLAN-ROZVOJ` F4.1).

### 8.4 `plan.json` — plán, který je strom, ne seznam

**Dnes:** `roadmap.json` má `grains`, kde je `title` + `prompt` (próza) + volitelné
`owns/depends_on/size_lines/model/acceptance`. Naměřeno: `acceptance`
a `provides` **0 čtenářů**; `size_lines` chybí u **13 z 18** granul; „size_lines >
60 ⇒ strong" je jen komentář.

**Nově:** plán je **strom s povinnou stopovatelností** a granule je **list**:

```jsonc
{
  "schema": "forge.plan/2",
  "goal": { "id": "g1", "text": "…co hráč dělá a jaký je zážitek…",
            "acceptance": ["hratelnost: hráč se pohne a nasbírá rudu"] },
  "requirements": [ { "id": "r1", "goal": "g1", "text": "…" } ],
  "capabilities": [ { "id": "c1", "requirement": "r1", "text": "hráč vytěží rudu" } ],
  "contracts": { "Skills.add": { "provides": "Skills",
                                 "sig": "add(skill: String, n: int) -> void",
                                 "data": { "skill": "String", "n": "int" },
                                 "called_by": ["sim.mining"] } },
  "grains": [{
    "id": "sim.mining",
    "capability": "c1",                  // POVINNÉ — jinak je to drift
    "title": "…", "kind": "code",
    "owns": ["scripts/mining.gd"],
    "depends_on": ["world.nodes"],
    "provides": ["Skills.add"], "consumes": ["Skills.add"],
    "acceptance": [                       // STRUKTUROVANÉ, ne ["tests","wiring"]
      { "gate": "behaviour", "call": "gather(uzel, 5)", "expect": "== 6" },
      { "gate": "wiring",    "expect": "mining.gd volá Skills.add" }
    ],
    "size_lines": 60, "model": "any",    // POVINNÉ, ne volitelné
    "non_goals": ["neřeš animaci těžby"]
  }]
}
```

**Vynucení (to je ta část, která dnes chybí):**

| Pravidlo | Kdy se poruší | Co se stane |
|---|---|---|
| Každá granule má `capability` s předkem v `goal` | vždy při driftu | **plánovací brána `fail`** — granule se nevydá |
| Každá granule má `size_lines` a `model` | dnes u 13 z 18 | `fail` (dnes jen varování s `exit 0`) |
| `size_lines > 60` ⇒ `model: strong` | dnes nikde | `fail` — **a je to poprvé vynucené, ne popsané** |
| Každá `acceptance` má `gate`, který **existuje** v `project.json` | — | `fail` (dnes `acceptance` nikdo nečte) |
| Každý `provides` má smlouvu **s tvarem dat** | dnes 0× | `fail` |
| `owns` jsou disjunktní v rámci vlny | dnes hlídá zámek, ale až za běhu | `fail` **před** dispatchem |

> **Tohle je odpověď na `JAK-PSAT-DESIGN`:** design popisuje **vrstvy, ne
> smlouvy** — a plán z něj dělá **smlouvy s tvarem dat a přijímacím kritériem**.
> Bez toho agent nemá co číst a vymyslí si rozhraní (naměřeno: `mining.gd` čte
> `resource_id`/`difficulty`/`cell`, mapa nemá markery surovin — **0**).

### 8.5 `WORK ORDER` — co dostane vykonavatel

**Dnes** jde do workflow payload `{owns, grain, repo, game, max_lines, model}`
a prompt je **próza**. Naměřeno: `max_lines` se **nedostane do promptu** (S40);
model tedy neví, kolik řádků smí.

**Nově** je zadání **strukturovaný dokument** a prompt je z něj **generovaný**
(ne ručně psaný — `game-developer` §4.5):

```jsonc
{
  "schema": "forge.work/1",
  "work_id": "w-…", "project_id": "uo-shadows", "grain_id": "sim.mining",
  "attempt": 2, "lease_expires_at": "…",
  "task": { "title": "…", "kind": "code",
            "contract": { "provides": [ … ], "consumes": [ … ] },
            "acceptance": [ … ], "non_goals": [ … ] },
  "edit_surface": {                       // NUTNÉ pro driver, který potřebuje soubor v kontextu
    "writable":  ["scripts/mining.gd"],
    "readable":  ["scripts/skills.gd", "CONVENTIONS.md"],
    "forbidden": ["tests/**", ".forge/**", ".github/**"] },
  "budget": { "max_changed_lines": 60, "max_prompt_tokens": 12000,
              "max_output_tokens": 4000, "deadline_s": 1800 },
  "model_policy": { "tier": "any", "require": ["text"], "forbid_providers": [] },
  "engine": { "id": "godot4", "version": "4.7.2",
              "forbidden_api": ["Label.ALIGN_LEFT", "Node.has()"] },
  "required_gates": ["schema", "wiring", "behaviour"],
  "report": { "kind": "poll|callback", "run_key": "…" }
}
```

> **Pozor na `budget.max_changed_lines`:** dnes je limit **jen brána** (auto-merge
> změří `additions+deletions`). V návrhu je **zároveň zadání** — jde do promptu.
> To je celý rozdíl mezi „nesmíš" a „víš, kolik smíš".

### 8.6 `VERDIKT` — jednotný výsledek brány i běhu

**Tohle je nejdůležitější kontrakt celého návrhu.** Dnes má každá brána vlastní
formát (text, `exit` kód, `::warning`), a proto se „neproběhla" nedá odlišit od
„prošla".

```jsonc
// Výstup JEDNÉ brány (stdout, JSON, vždy exit 0; nenulový exit = brána spadla)
{ "schema": "forge.gate/1", "gate": "behaviour",
  "state": "pass",                       // pass | fail | not_run | unknown
  "measured": { "items": 7, "checked": 7, "calls": 12 },   // POVINNÉ
  "findings": [ { "severity": "error|warn|note", "where": "scripts/mining.gd:41",
                  "what": "…", "why_it_matters": "…" } ],
  "evidence": [ "artifacts/gate-behaviour.json" ],
  "reason": null }                        // POVINNÉ, když state != pass
```

**Pravidla, jejichž porušení je vada brány (a testuje se to):**

1. `state` je **vždy** vyplněný a je jedním ze čtyř.
2. `measured.items == 0` ⇒ `state` **nesmí** být `pass` (nejvýš `not_run`
   s důvodem). **Tohle jediné pravidlo zavírá S3** („zelená nad prázdným seznamem").
3. `state ∈ {not_run, unknown}` ⇒ `reason` je povinný a **pojmenovaný**
   („kontrola NEPROBĚHLA, protože v projektu není `assets/sprites/walk_*.png`").
4. Brána, která **spadne** (nenulový exit / timeout), se hlásí jako `unknown`,
   **nikdy** jako `pass`. A `unknown` **není totéž** co `not_run`.
5. Brána, která **nemá co měřit**, to řekne — místo aby mlčela.

**Souhrn běhu** (to, co dnes chybí a co zavírá S27 oběma směry):

```jsonc
"gates": { "declared": 6, "ran": 5, "passed": 4, "failed": 1,
           "not_run": [ { "gate": "vision", "reason": "uzel nedeklaruje capability:vision" } ],
           "unknown": [] }
```

> **Rozhodovací pravidlo:** je-li mezi `not_run`/`unknown` brána se
> `severity: hard`, **výsledek nemůže být `merged`** — a to i kdyby všechny
> ostatní brány prošly. To je přesně to, co dnes nejde: `check-wiring.py` nad
> **nulou souborů** vrátí zelenou.

### 8.7 Porty (rozhraní mezi jádrem a světem)

```ts
// core/ports — jen typy, žádná implementace. Jádro díky tomu testuješ offline.
interface StateStore  { append(e: Event): Promise<void>;
                        project(q: Query): Promise<StateView>;
                        claim(workId, holder, ttl): Promise<Lease | null>; }
interface Runner      { capabilities(): Capability[];
                        dispatch(w: WorkOrder): Promise<RunRef>;
                        poll(r: RunRef): Promise<RunResult>; }
interface Scm         { tree(ref): Promise<Set<string> | null>;   // null = NEVÍME
                        mergeState(prRef): Promise<'merged'|'open'|'closed'|null>;
                        openPr(change): Promise<PrRef>; }
interface ModelGateway{ list(): Promise<ModelInfo[]>;             // + naučené limity
                        attempt(w: WorkOrder, choice: ModelChoice): Promise<Attempt>; }
interface GateRunner  { run(gate: GateRef, ctx: GateCtx): Promise<GateVerdict>; }
interface CapabilityHost { has(c: Capability): boolean;           // vision, blender, …
                           run(c: Capability, args): Promise<Artifact>; }
```

> **`null` znamená „nevíme"** a je to **povinná** hodnota rozhraní (dnes to
> `index.ts:506–512` dělá správně u stromu `origin/main` — návrh to zobecňuje
> na **každý** dotaz na vnější svět).

---

## 9. Modelová adaptace — jak se orchestra učí z toho, co má

**Tohle je jádro zadání („umí se přizpůsobit dostupným modelům").** Kapitola je
proto konkrétní: datový model, algoritmus, třídy selhání a co se stane, když
model není.

### 9.1 Co je dnes špatně (shrnutí z §2.2)

1. **Zdroj pravdy je ruční seznam** s lidskými odhady (`anyPriority`, `skromny`).
2. **Probe měří dostupnost, ne způsobilost** — `ping`, `max_tokens: 8`.
3. **Limity jsou v komentářích** — model s limitem 8 000 TPM se zařadí do řetězce
   a **spálí pokus** (naměřeno: Groq `Request too large: Limit 8000, Requested 14 398`).
4. **Rotace je slepá** — hash podle `run_key` / číslo pokusu; nerozlišuje,
   **na čem** model selhal (naměřeno: 3× a 5× stejné selhání týmž modelem).
5. **Není paměť** — systém se z žádného výsledku neučí; `provider.json` drží
   jen „posledního vybraného".
6. **Rozhodnutí o velikosti se k modelu nedostane** (S40) — model neví, kolik smí.

### 9.2 Kniha způsobilosti (capability ledger)

**Append-only** záznam o **každém** pokusu. Není to log pro člověka — je to
**vstup rozhodování**.

```jsonc
// tabulka/JSONL `model_attempts` — jeden řádek = jeden pokus
{ "at": "2026-10-05T18:22:11Z",
  "provider": "groq", "model": "openai/gpt-oss-120b",
  "signature": "code|godot4|gdscript|p12k|lines60|tools0|vision0",
  "prompt_tokens": 14398, "output_tokens": 812, "latency_ms": 41000,
  "outcome": "failed",
  "failure_class": "tpm_limit",
  "evidence": { "run": "…#146", "log_sha256": "…", "patch_sha256": null },
  "work_id": "w-…", "grain_id": "entity.player.api", "attempt": 1 }
```

**Signatura úlohy** (`signature`) je **odvozená z work orderu**, ne ručně psaná —
aby se dala spočítat **před** dispatchem:

```
kind | stack | language | prompt_bucket | expected_lines_bucket | needs_tools | needs_vision
```

**Co se z knihy počítá** (a co nahrazuje dnešní odhady):

| Veličina | Jak se počítá | Čím nahrazuje |
|---|---|---|
| `p_success(model, class)` | podíl úspěchů, ale **dolní mez Wilsonova intervalu** (ne podíl!) | `strongModels` (binární seznam) |
| `limit_prompt_max_ok(model)` | největší `prompt_tokens` s `outcome: success` | odhad v komentáři |
| `limit_prompt_min_fail(model)` | nejmenší `prompt_tokens` se selháním `tpm_limit`/`context_too_large` | nic (dnes se to neví) |
| `quota_left(provider, window)` | úspěchy + 429 za okno vs. změřený strop | `skromny: true` (boolean) |
| `fault_histogram(model, class)` | četnost tříd selhání | nic (dnes rotace naslepo) |

> **Proč dolní mez a ne podíl:** u malých vzorků je podíl **lichotivý**.
> Model s 1 úspěchem ze 2 má podíl 50 % a dolní mez ~9 %. Návrh **záměrně
> podhodnocuje** — protože chyba „poslal jsem to špatnému modelu" je dražší
> (spálená kvóta, ušlý běh) než „poslal jsem to lepšímu, než bylo nutné".

### 9.3 Směrování (router) — konkrétní algoritmus

```
vstup:  work order W  +  kniha  +  deklarované limity
výstup: ModelChoice | REFUSE(reason, komu se to hlásí)

1. HARD FILTRY (binární, měřené)
   a) modalita:   potřebuje W vision?  → model musí umět vision
   b) klíč:       je klíč poskytovatele k dispozici? (jinak přeskoč)
   c) karanténa:  je poskytovatel v karanténě (rate_limit do …)?
   d) FEASIBILITA PROMPTU:  odhad_prompt_tokens(W) ≤ limit(model)
        limit = min(deklarovaný, změřený_max_ok)   // tvrdší z obou
      → KDYŽ SE NEVEJDE: buď ZMENŠI PROMPT (budgeter, §9.5),
        nebo model VYLOUČ.  Nikdy „zkus to a uvidíme".
   e) kvóta:      quota_left(provider, okno) > 0

2. SKÓRE (na kandidátech, kteří prošli)
   p    = p_success_lower_bound(model, signatura)
   cena = spotřeba_kvóty_normalizovaná (vzácnost zdroje) + očekávané tokeny
   skóre = p − λ · cena            // λ podle třídy granule

3. PRAH A ÚSPORNOST
   vyber NEJLEVNĚJŠÍ TIER, jehož p ≥ prah(signatura)
   → „strong" modely se neutrácejí na to, co zvládne slabý
   → ale kdyby slabý neměl p ≥ prah, NEposílá se (dnes se pošle a spálí)

4. KDYŽ NIKDO NEPROŠEL
   REFUSE s pojmenovaným důvodem:
     - "všichni kandidáti mají prompt > limit" → návrh: rozděl granuli
     - "kvóta vyčerpána do 06:00 UTC"         → návrh: odlož (ne spal)
     - "žádný model nemá p ≥ prah"            → návrh: člověk / silnější zdroj
   REFUSE je UDÁLOST, ne ticho. Dnes by se pokus spálil.
```

> **Co tím systém získá, měřeno proti dnešku:** 55 % běhů umíralo do 30 s
> (nefeasibilní dispatche) a na jednu úspěšnou granuli bylo potřeba ~9 běhů.
> Router umí **nevyrobit** běh, o kterém kniha říká, že nemá šanci — a to je
> celý rozdíl mezi „sedm pokusů" a „dva pokusy".

### 9.4 Klasifikace selhání — rozhoduje, CO se opakuje

**Pravidlo P4:** opakování je funkce **třídy selhání**. Dnes je funkcí času
a rotace — a to je naměřeně špatně.

| Třída | Jak se pozná | Co se opakuje | Co se **NEopakuje** |
|---|---|---|---|
| `tpm_limit` / `context_too_large` | text chyby + `prompt_tokens` | **zmenšený prompt** nebo jiný model | stejný prompt týmž modelem |
| `rate_limit` | HTTP 429 / text | jiný poskytovatel; tento do karantény | nic se nepálí |
| `no_change` | patch prázdný | **jiná editovatelná plocha nebo ostřejší zadání** | rotace modelu (naměřeno: 3× a 5× stejně) |
| `parse_error` | formát odpovědi | **jiný driver** nebo přísnější formát | totéž znovu |
| `wrong_api` | compile/parse chyba s cizí konstantou | **kontext enginu** (verze + zakázané API) | nic — dokud kontext nedorazí |
| `test_failure` | brána `fail` | **vyšší tier modelu** | stejný tier |
| `gate_not_run` / `unknown` | verdikt | **oprava uzlu nebo brány** | model (není to jeho vina) |
| `timeout` | lease vypršela | kratší zadání / delší deadline | totéž |
| `empty_artifact` | artefakt 0 B | **brána na prázdný artefakt** + znovu | tichý `success` |
| `human_required` | politika | nic | pokus (počítal by se jako selhání modelu) |

> **Tabulka je zároveň kontrolní seznam pro implementaci:** každá třída musí být
> **pojmenovatelná z logu** (`failure_class`), jinak je klasifikace dojem.

### 9.5 Rozpočet promptu (budgeter) — protože 14,4k se do 8k nevejde

Naměřeno: prompt je **~14,4 tis. tokenů**, z toho **pevná část** ~6 tis.
(`CONVENTIONS.md` 3 839 + systémový prompt ~2 166). **Zmenšit granuli nepomůže —
pevná část je většina vstupu.**

Návrh proto **skládá** prompt z deklarovaných částí a umí ho **zmenšit**:

| Úroveň | Co obsahuje | Odhad |
|---|---|---|
| L0 — minimum | smlouva granule + `acceptance` + zakázané API + editovatelná plocha | ~2–3 k |
| L1 — + konvence **podle druhu granule** | jen relevantní sekce `CONVENTIONS.md` (dnes se posílá celý) | ~4–6 k |
| L2 — + kontext závislostí | jen `provides`, které granule `consumes` | ~6–9 k |
| L3 — + plné soubory | celé `owns` | 10 k+ |

**Router volí úroveň tak, aby se vešel** do limitu zvoleného modelu. Tím se
z modelu s limitem 8 000 stane **použitelný zdroj pro malé granule** místo
dnešního „zařadí se a spálí se". *(To je odpověď na `NA16` „dynamicky assignovat
balíček pro omezené modely" — návrh to **neodmítá**, ale dělá to **měřením**:
rozhoduje se podle změřeného limitu, ne podle jména providera.)*

### 9.6 Karanténa, kvóta a comeback

- **Karanténa** je **časované** omezení poskytovatele (`until`), zapsané jako
  událost s důvodem. Není to mazání ze seznamu — je to „teď ne".
- **Kvóta patří klíči, ne repu** (GitHub ToS): `quota_left(key, window)` se vede
  **per klíč**, protože druhý projekt kapacitu **nezdvojnásobí, jen rozdělí**.
- **Comeback:** po vypršení karantény se poskytovatel vrací **napřed na malé
  granule** (kde je riziko spálení pokusu nejmenší) — a teprve po úspěchu dostane
  větší. Tohle je „učení", které dnes chybí.
- **Denní zpráva o modelech:** kontrola z katalogu (`GET /models` + minimální
  ping) zůstává — ale její výstup **není jen issue**: je to **událost do knihy**,
  která mění směrování. *(Dnešní stav: mrtvý model založí issue a `providers.json`
  se needituje.)*

### 9.7 Limity: kde se berou a jak se zapisují

**Respektuji rozhodnutí NA14** („nezapisovat nezměřené jako změřené") a
**řeším jeho důvod** — `providers.json` se neměnil proto, že by se tam psalo `?`.
Návrh proto **zavádí místo pro měření i pro „nevíme"**:

```jsonc
"limits": {
  "tpm":            { "value": 8000, "source": "observed",
                      "observed_at": "2026-10-01", "evidence": "run #146" },
  "context_window": { "value": null, "source": "unknown" }
}
```

**Pravidla:** `source ∈ {declared, observed, unknown}`; `value: null` je
**platná hodnota** a znamená „nevíme" — a router s ní pracuje **opatrně**
(nepovažuje model za neomezený). Nic se nepředstírá.

### 9.8 Co se stane, když model není (a je to nejčastější stav)

Free řetězec má denní strop. Návrh proto **není postaven na tom, že model je**:

| Situace | Co systém udělá |
|---|---|
| Všichni kandidáti v karanténě | **odloží** práci s `retry_at` = konec okna; nezapisuje selhání modelu |
| Granule potřebuje `strong`, ale žádný silný není | **nechá ji ve frontě** a **viditelně** hlásí „čeká na silný model"; plánovač dostane signál **přerozložit** granuli na ≤ 60 řádků |
| Kvóta došla uprostřed vlny | doběhne, co je rozpracované; nové **nevydá** (dnes by spálilo pokusy) |
| Model vrací `no_change` pořád | **není to model** — eskaluje se na **zadání** (ostřejší smlouva, jiná plocha) |
| Není žádný model ani po odložení | `human_required` — úloha jde do „čeká na člověka" **s pojmenovaným důvodem** |

> **Tohle je odpověď na „umí se přizpůsobit dostupným modelům":** přizpůsobení
> není „zkusit jiný model", ale **vědět, co který umí, co stojí, co mu nesmím
> dát — a umět neposlat nic**, když to nemá smysl.

---

## 10. Technologická neutralita — adaptéry a deklarace

### 10.1 Co je dnes vázané (a kde přesně)

| Vrstva | Vazba | Kde |
|---|---|---|
| Jádro | **žádná** — 0 zmínek o enginu v kódu (2 komentáře) | `index.ts:304`, `:384` |
| Workflow | **silná** — `FORGE_GODOT`, cache `forge-godot-4.7.2` (3×), `res://tests/run_tests.gd`, `--write-movie`, export presety | `ci.yml`, `agent.yml`, `release.yml` |
| Brány | **střední** — GDScript regex, `scripts/*.gd`, jména `level.gd`/`world.gd`, role `coin/chest/player` v kódu | `check-wiring.py:73`, `check-schema.py:212–218`, `check-assets.py:222–223` |
| Uzel | **střední** — kroky `godot-import/test/export`, `FORGE_CMD` na smazaný `forge.cmd` | `worker.mjs:207–233`, `:83` |
| Driver | **silná** — aider s `--edit-format diff`, `--map-tokens 0` | `agent.yml:226–235` |
| Model | **střední** — tvrdě OpenAI-kompatibilní `/chat/completions` | `pick-provider.mjs:142` |

> **Tohle je „mapa díry":** neutralita jádra je **skutečná a cenná**, ale
> **nepoužitelná**, protože **všechno kolem je vázané**. Přidat druhý stack dnes
> znamená **vyměnit obálku** — a ta je rozesetá v sedmi souborech a desítkách
> konstant.

### 10.2 Rozhraní adaptéru stacku

Adaptér je **spustitelný soubor s podpříkazy**, který **vrací JSON na stdout**.
Není to plugin systém ani dynamické načítání — je to **CLI s kontraktem**
(nejmenší možná abstrakce; `PLAN-ROZVOJ` §1.5 zamítl plugin systém jako
předčasný a **návrh to respektuje**).

```
forge-adapter probe                 → { "adapter":"godot4","version":"4.7.2",
                                        "capabilities":["test","build","screenshot",
                                                        "syntax","import","export"] }
forge-adapter deps                  → { "ok": true, "installed": [ … ] }
forge-adapter prepare               → { "ok": true }        # import assetů
forge-adapter syntax  --file F      → GATE VERDICT (jeden soubor)
forge-adapter test                  → GATE VERDICT + { "counts": {"checks":89,"failures":0} }
forge-adapter build   --preset P    → { "ok": true, "artifacts": [ … ] }
forge-adapter screenshot --out D    → { "ok": true, "artifacts": ["D/frame.png"] }
forge-adapter gates                 → seznam bran, které adaptér přináší
```

**Pravidla (každé řeší naměřenou vadu):**

1. **Co adaptér neumí, MUSÍ říct** (`capabilities` bez dané položky) — ne mlčet.
   *(Dnešní `check-wiring.py` nad 0 souborů hlásí zelenou.)*
2. **Každý podpříkaz vrací VERDIKT** (§8.6), ne text. *(Dnešní brány mají tři formáty.)*
3. **Verze enginu je datem, ne konvencí** — adaptér ji **přečte** z projektu
   a předá do work orderu. *(S17: model psal Godot 3 konstanty do Godotu 4.)*
4. **Zakázané API je deklarované adaptérem** (např. `Label.ALIGN_LEFT`),
   takže se dostane **do promptu** — ne do konverzace po selhání.
5. **Adaptér se testuje sám**: `forge-adapter probe` v CI; adaptér bez `probe`
   se odmítne nasadit.

### 10.3 Gate kit — brány jako přenositelná sada, ne jako skripty pro jednu hru

**Obecné brány (neutrální, dnes existují a jsou dobré):**

| Brána | Co měří | Co je v ní dnes potřeba zobecnit |
|---|---|---|
| `schema` | deklarace vs. skutečnost (spec ↔ mapa ↔ vykreslování ↔ dlaždice) | jména souborů (`level.gd`, `world.gd`) → z `project.json` |
| `assets` | poměry, díry v siluetě, barvy, IoU siluet framů, hudba z manifestu | role `coin/chest/player` → ze `spec.json#roles` |
| `wiring` | každá funkce je odněkud volaná; `_on_*` připojené | přípona a složka → z `project.json`; **a vyloučit `tests/`** (dnes se testy počítají jako volající) |
| `render` | snímek odpovídá mapě | cesty → z `project.json` |
| `vision` | obsah (je to ta postava? sedí styl?) | zůstává **advisory**, dokud se nezměří přesnost |
| `behaviour` | **volá** API a měří výsledek (ne `has_method`) | **nová a povinná** — dnes existuje jen jako podmíněné kontroly |
| `coverage` | `declared vs ran` u všech bran | **nová** — hlídá brány samotné |

**Tři pravidla pro každou bránu (bez nich se návrh nevydá):**

1. **Offline self-test se dvěma známými případy** — správný a chybný.
   *(`PLAN-ROZVOJ` ST5; dnes to nemá 5 bran.)*
2. **Prázdný případ** — fixture, kde brána **nemá co měřit**; musí vrátit
   `not_run` s důvodem, **nikdy** `pass`. *(Tohle je test na S3.)*
3. **Mutace** — vrácení vady do kódu; brána musí spadnout. Když nespadne,
   **není zelená, je slepá**.

### 10.4 Dva hostitelé, jedno jádro (a jak to řeší `read_image` v CI)

**Naměřená mez:** `read_image` **není** v GitHub Actions; Blender tam taky není.
Dnešní důsledek: vizuální ověření je **buď** Gemini (kvóta, chybovost),
**nebo** ruční.

**Návrh to neobchází — deklaruje to jako schopnost:**

```jsonc
// hosts/local/host.json
{ "host": "pc-domaci", "runner": "local",
  "capabilities": ["test","build","screenshot","blender","vision","read_image","human_inbox"] }
// hosts/actions/host.json
{ "host": "github-actions", "runner": "actions",
  "capabilities": ["test","build","screenshot"] }
```

- Granule, která **vyžaduje** `read_image`, se **nevydá** do CI — čeká na uzel,
  který to umí.
- `vision` brána s `requires: ["capability:vision"]` se v CI hlásí jako
  **`not_run` s důvodem** (ne jako zelená) — a protože je `advisory`, **sloučení
  neblokuje**.
- **Lidská fitness funkce** je `capability: human_inbox` — fronta, která **není**
  chyba ani čekání: je to **pojmenovaný stav s vlastníkem (člověkem)**.

> **Tohle je jediná část návrhu, která přidává schopnost, kterou dnes orchestra
> nemá** — a je to **schválně vidět**: „obsah posoudí člověk" se stává
> **deklarovaným krokem**, ne tichým nedodělkem.

---

## 11. Spolehlivost — stav, který se nedá obejít

### 11.1 Události a projekce (místo dvou zapisovatelů do jednoho sloupce)

**Naměřeno:** `roadmap.updated_at` nesl **dva významy** („vzniklo" i „naposledy
selhalo") a oprava jednoho významu rozbila druhý (S12 → B1 → **S38**).
A `/report` vs. `pollRuns` píší týž stav **dvěma cestami** (S13).

**Návrh:** stav je **projekce append-only logu událostí** a **každá změna stavu
má `cause`**:

```jsonc
{ "at": "...", "work_id": "w-…", "grain_id": "sim.mining",
  "type": "attempt_failed",                     // uzavřený výčet typů
  "cause": { "class": "test_failure", "gate": "behaviour",
             "detail": "gather() vrátil 4, očekáváno 6", "evidence": ["run#241"] },
  "attempt": 2,
  "policy": { "next_attempt_at": "...", "next_tier": "strong",
              "reason": "test_failure → vyšší tier" } }
```

- **Dva zápisové body se sloučí do jednoho** — obě cesty (`poll` i `report`)
  produkují **tentýž typ události**; projekce je jedna funkce.
- **Zákaz:** stav se **nesmí** měnit `UPDATE`em bez události. To je
  **kontrolovatelné staticky** (a má to být brána nad jádrem).

### 11.2 Leases místo cooldownu

| Dnes | Návrh |
|---|---|
| `ready → running` optimistickým `UPDATE` (dobré, zachovat) | **lease s TTL a heartbeatem**; držitel je pojmenovaný |
| „zaseknuté" se pozná podle `started_at < now-90min` | **vypršená lease** je událost s třídou `lease_expired` |
| retry se řídí **časem** (`RETRY_HOURS`) | retry se řídí **třídou selhání** (§9.4) + `next_attempt_at` z politiky |
| `MAX_ATTEMPTS` na **úkol** → obejitelné (S14, S38) | **strop a watchdog na GRANULI** (`grain_id`), ne na úkol — a jsou to **dvě různé věci**: strop zastaví, watchdog eskaluje |
| watchdog jen **notifikuje** a prah je nedosažitelný | watchdog **jedná**: po `escalate_after_attempts` → (1) vyšší tier, (2) **rozděl granuli**, (3) `human_required` |

### 11.3 Invarianty (kontrolovatelné, ne dokumentované)

Každý invariant má **test**, který ho ověří **nad zdrojákem jádra** (vzor:
`tools/test-zamek-owns.py` — vytahuje `lockKeys()` ze `index.ts` a spouští
**skutečný text funkce**; to je jediný správný vzor v celém projektu, S14/L16).

| # | Invariant | Jak se ověří |
|---|---|---|
| I1 | `done` ⇒ artefakt je v `main` **a** obsahuje `owns` | dotaz na SCM + porovnání množin |
| I2 | Žádný stav bez události (`cause`) | sken projekce vs. log |
| I3 | `merged` jen když **všechny `hard` brány** jsou `pass` | z verdiktu; ne z `conclusion` workflow |
| I4 | Lease má TTL a držitele; vypršení je událost | test nad jádrem |
| I5 | Strop pokusů je na **granuli** | test nad jádrem |
| I6 | Zámek `owns` je **jeden klíč** (dva tvary téhož klíče = vada) | test (existuje: 8 kontrol) |
| I7 | Každý `catch` produkuje událost | statická kontrola nad jádrem |
| I8 | `not_run` u `hard` brány ⇒ nelze `merged` | test nad vyhodnocením verdiktu |
| I9 | Plán: každá granule má `capability`, `size_lines`, `model`, `acceptance` | plánovací brána |
| I10 | `declared vs ran` u bran je **vždy** vykázáno | z verdiktu |

### 11.4 Zdraví cíle, ne řidiče (S18)

```jsonc
GET /health
{ "controller": { "ok": true, "version": "…", "tick_age_s": 12 },
  "targets": [ { "project": "uo-shadows",
                 "ci_main": "success",          // ← TOHLE DNES CHYBÍ
                 "ci_main_at": "…",
                 "last_merged_pr": { "n": 34, "at": "…" },
                 "queue": { "ready": 3, "oldest_ready_age_s": 5400 },
                 "gates_coverage_last_run": "5/6 (vision: not_run)" } ],
  "models": { "feasible_now": ["mistral/codestral"],
              "quarantined": [ { "provider": "groq", "until": "…",
                                 "reason": "tpm_limit" } ],
              "quota_hint": { "gemini": "~12/20 used today" } },
  "refusals": [ { "grain": "entity.player", "reason": "prompt > limit všech kandidátů",
                  "suggested_action": "rozdělit granuli" } ] }
```

> **Test, který to ověří (a je to falzifikátor S18):** postav `main` do stavu
> `failure` a **`/health` musí hlásit `ci_main: failure`** — dnes hlásí `ok: true`.
> A druhý směr: dokud je CI červené, nesmí dispatchnout **novou** granuli
> (dnes dispatchuje a pálí pokusy).

---

## 12. Kvalita produktu — co je „hotovo" pro produkt, ne pro PR

### 12.1 Tři úrovně hotovosti (a každá má svého nositele)

| Úroveň | Co znamená | Kdo to potvrzuje |
|---|---|---|
| **Granule** | artefakt je v `main` **a** brána **zavolala** chování **a** `acceptance` prošla | stroj (brány) |
| **Milník** | schopnosti milníku existují **a** produkt se **spustí** bez tichých chyb **a** snímek **prošel pohledem** | stroj + **člověk** (u snímku) |
| **Produkt** | cíl z `plan.goal.acceptance` platí — hráč dělá, co cíl říká | **člověk** (hratelnost) |

### 12.2 Co se musí změnit, aby „hotovo" něco znamenalo

1. **`acceptance` se čte.** Dnes **0 čtenářů** (S22). V návrhu je to **vstup
   brány** `behaviour`: každá položka `acceptance` je **volání + očekávání**
   a brána je **spustí**.
2. **Soubor, který součástí být MÁ, musí při nenačtení SELHAT.** Dnes
   `if load(...) != null:` **tiše přeskočí** → prošla tři PR, která nemohla
   fungovat.
3. **Prázdný artefakt je vada.** `world.nodes` dodán jako **0 B** a CI to
   nechytilo → nová kontrola: artefakt v `owns`, který je **prázdný**, je
   `fail` (ne `pass`).
4. **Vizuální změna má snímek a snímek má nositele.** Buď jej posoudí
   `capability: vision` (advisory), nebo `human_inbox` (blokuje milník).
5. **Produktová `acceptance` se spouští na milnících**, ne na každém PR —
   jinak se z ní stane brána, která blokuje (a to je naměřený antipattern:
   „brána na nezměřené metrice").

### 12.3 Stopovatelnost (a její vynucení)

```
cíl g1 ──► požadavek r1 ──► schopnost c1 ──► granule sim.mining ──► brána behaviour
   ▲                                                                     │
   └──────────────── acceptance produktu ◄── milník M1 ◄── snímek ◄──────┘
```

- **Každá granule má předka**; granule bez předka je **drift** → plánovací brána
  ji odmítne. *(To je jediná obrana proti „z kódu se rodí plán".)*
- **Každý požadavek má aspoň jednu granuli**; požadavek bez granulí je
  **viditelná díra** (ne ticho).

### 12.4 Index kvality (jedno číslo, které se dá číst i zkazit)

Návrh **zavádí** souhrn, ale **sám ho označuje za nebezpečný**:

| Složka | Co měří |
|---|---|
| pokrytí stopovatelnosti (granule s předkem / všechny) | plán |
| pokrytí bran (`ran / declared`) | že se měřilo |
| podíl **chování** vs. **přítomnost** v testech | sílu bran |
| `not_run` a `unknown` u `hard` bran | **viditelná slepá místa** |
| otevřená `human_inbox` | **práci, kterou stroj neumí** |
| čas od poslední sloučené granule | **skutečnou propustnost** |

> **⚠ Goodhart:** `PLAN-VISION` §9 to pojmenoval správně — *systém se naučí
> procházet kontrolou*. Proto index **není cíl** (nesmí být v `acceptance`
> žádné granule) a **musí být rozpadnutý**; jedno číslo se smí používat jen
> ke srovnání **dvou období téhož projektu**, nikdy k rozhodnutí „je to dobré".

---

## 13. Provoz — kde to běží a jak se to nasazuje

### 13.1 Jedenáct věcí, které se v provozu nesmí změnit

*(Jsou to naměřená rozhodnutí, ne vkus — §3.)*

1. Pull-worker místo self-hosted runneru. 2. Polling místo reportu.
3. Dva joby (klíče vs. zápis). 4. Optimistický claim. 5. Zámky scoped na repo.
6. `blocked` je terminální. 7. `done` jen s protějškem. 8. `null ≠ []`.
9. Konfigurace modelů na jednom místě. 10. Rotace jako čistá funkce.
11. Brána, která má jak selhat.

### 13.2 Nasazení a ověření (tři kroky, beze změny)

Push dorazil → build běžel na **správném commitu** → server posílá **nový**
artefakt. `HTTP 200 není důkaz`. Deploy conductora **jen z gitu**
(lokální `wrangler deploy` nefunguje — vypršelý token; v sandboxu `EPERM`).

**Nově navíc (protože S18 je naměřená):** po každém nasazení se ověří
**i to, že `/health` umí zčervenat** — sabotáž: dočasně nastavit `ci_main`
na `failure` a ověřit, že se to projeví. *Brána, která neumí zčervenat, není
brána — a to platí i pro health endpoint.*

### 13.3 Pozorovatelnost bez tokenů

**Pravidlo z `ANALYZA-EFEKTIVITY-DSH`:** *„indikátory pro MODEL jsou drahé;
užitečná je cesta měřit a zobrazovat **člověku** — čte se z logu, stojí 0 tokenů
a nemůže halucinovat."*

Návrh proto **nedává orchestraci nic do promptu** (žádné „jsi ve špičce"),
ale staví **jednu stránku stavu** z událostí: fronta, pokusy podle tříd selhání,
co je v karanténě, co čeká na člověka, propustnost. **Nulové náklady, nulová
halucinace.**

---
# ČÁST III — VARIANTY A ROZHODNUTÍ

## 14. Tři varianty (a co každá NEDĚLÁ)

> **Proč tři a ne jedna:** jednovariantní návrh je **rozhodnutí vydávané za
> návrh**. Každá varianta má **cenu, riziko a to, co nedělá** — a **měřitelnou
> podmínku, kdy selhala**.

### 14.1 Varianta A — „Zalátat a změřit" (evoluce stávajícího conductora)

**Co to je:** zůstává `index.ts` jako jediné jádro; přidají se **tři vrstvy
postupně** — (1) kniha způsobilosti + router jako funkce **uvnitř** conductora,
(2) verdikt bran jako **další pole** v payloadu, (3) `project.json` čtený
branami místo konstant.

| | |
|---|---|
| **Cena** | **1–2 týdny**; ~600–900 řádků v `index.ts`, `agent.yml` a třech branách |
| **Riziko** | **nízké** — nic se nepřesouvá, orchestra běží dál |
| **Co NEDĚLÁ** | **Neřeší dvouzápis stavu** (S38 zůstává), **nesjednocuje verdikt** (jen ho přidá na jedno místo), **nezvládne druhý stack** (konstanty zůstanou v obálce), **jádro zůstane netestovatelné** (I/O dál promíchané s rozhodováním) |
| **Kdy je správná** | když je prioritou **nevypnout orchestra ani na den** a stačí zvednout úspěšnost z 11,3 % |
| **Kdy selhala** | **když po dvou týdnech není v `index.ts` ani jedna čistá funkce, kterou by šlo testovat bez databáze** |

### 14.2 Varianta B — „Nové jádro, staří hostitelé" (DOPORUČENÁ)

**Co to je:** rozhodovací logika se **vytáhne z `index.ts` do `core/`** jako
čisté funkce (`planFrontier`, `eligible`, `route`, `classify`, `evaluateGates`),
I/O zůstane v **hostitelích** (`hosts/worker` = dnešní D1 + cron, `hosts/local` =
uzel, `hosts/ci` = workflow). K tomu **čtyři kontrakty** (§8.3–§8.6) a **jeden
adaptér** (`adapters/godot4`). Migrace je **strangler**: nové jádro nejdřív
**jen počítá** a **rozhodnutí se porovnávají** s živým conductorem (shadow mode),
teprve pak se přepne dispatch.

| | |
|---|---|
| **Cena** | **3–6 týdnů**; `core/` ~1 500 řádků (většina je **přesun**, ne nový kód), `hosts/worker` ~600, kontrakty ~300, adaptér godot4 ~400 (většina je **přesun** existujících bran) |
| **Riziko** | **střední** — dva systémy vedle sebe po dobu shadow mode; riziko je v **migraci stavu**, ne v návrhu (proto shadow mode a proto se **nic nemaže**, dokud se neshodují) |
| **Co NEDĚLÁ** | **Nebuduje druhou technologii** (jen ji umožní), **nezavádí plugin systém** (adaptér je CLI, ne dynamické načítání), **nemění herní repo** (migrace šablony je samostatná fáze), **nepřináší nové brány** (jen jim dá jednotný verdikt) |
| **Kdy je správná** | když se má orchestra **učit z výsledků** a **přežít výměnu technologie** — což je přesně zadání |
| **Kdy selhala** | **když přidání druhého stacku sáhne na víc než 5 souborů** mimo `adapters/<stack>/` a `project.json` (§8.2) — nebo když se `core/` nevejde do ~1 500 řádků, protože do něj prosáklo I/O |

> **⚠ Konfrontace se zamítnutím (`PLAN-ROZVOJ` §1.5):** projekt **vědomě zamítl
> „plugin systém pro enginy"** s odůvodněním *„předčasné, až bude druhý engine"*
> a `PLAN-ROZVOJ` §5 dodává *„když F5 nepřijde do rozumné doby, F3.5 se nedělá"*.
> **Návrh to neobchází — souhlasí s tím a jde jinudy:**
>
> | Zamítnuté | Co navrhuje varianta B | Rozdíl |
> |---|---|---|
> | plugin systém, registr bran, abstrakce nad enginy | **jeden** adaptér (`godot4`) + CLI kontrakt + deklarace v `project.json` | **žádná dynamika, žádný registr, žádné načítání** — jen jeden soubor, který se dá spustit a otestovat |
> | abstrakce „až s druhou hrou" | abstrakce **jako kontrakt** hned, **druhý adaptér až později** | kontrakt **bez druhého konzumenta** je hypotéza — proto je **falzifikátor** (≤ 5 souborů), ne víra |
> | `core/` + `tools/<engine>/` = „poslední krok F3" | `core/` je **první** krok, protože do něj patří **učící se směrování** | důvod není modularita pro krásu, ale **měřitelnost a paměť** |
>
> **Zbývá riziko, které je potřeba vyslovit:** i s jedním adaptérem je kontrakt
> **hypotéza**. Proto návrh **netvrdí, že je správný** — tvrdí, **jak se to pozná**.

### 14.3 Varianta C — „Přepsat od nuly" (nové schéma, nový jazyk, čistý start)

| | |
|---|---|
| **Cena** | **2–4 měsíce** |
| **Riziko** | **vysoké** — zahodí se 14 nosných konstrukcí (§3) a nahradí **hypotézami** |
| **Co NEDĚLÁ** | **Nepřenese naměřené poznatky** (ty jsou z velké části v **komentářích u kódu**, který by zmizel — `index.ts` má v komentářích čísla běhů a data); **nevydá ani jednu granuli** po dobu přepisu; a hlavně — **zopakuje chyby, které už jsou jednou zaplacené** |
| **Kdy je správná** | **nikdy v této situaci** — orchestra dnes **funguje** (30 bran zelených, `validate-all` zelený) a její vady jsou **pojmenované a lokalizované**, ne strukturální nepořádek |
| **Kdy selhala** | **selhává už svým zadáním** — nemá měřitelnou podmínku úspěchu, protože „nové" není vlastnost, která se dá změřit |

> **Poznámka k „dokonalé orchestra":** zadání znělo *„nová, dokonalá orchestra"*.
> **Dokonalost není vlastnost, která se dá dodat** — je to **seznam podmínek,
> které se dají vyvrátit.** Proto jsou v §16 falzifikátory a proto návrh
> **nekončí tvrzením, že je správný.**

### 14.4 Srovnání na jednom místě

| Kritérium | A (zalátat) | **B (jádro + adaptéry)** | C (přepsat) |
|---|---|---|---|
| Zastaví orchestra? | ne | **ne** (shadow mode) | **ano, na měsíce** |
| Naučí se z výsledků? | částečně | **ano** | muselo by se dodělat znovu |
| Přežije výměnu technologie? | ne | **ano** (§8.2 to měří) | ano, ale draze |
| Odstraní dvouzápis stavu (S38)? | **ne** | **ano** | ano |
| Přenese naměřené poznatky? | ano | **ano** | **ne** |
| Cena | 1–2 týdny | **3–6 týdnů** | 2–4 měsíce |
| Riziko | nízké | **střední** | vysoké |

**Doporučení: B** — a to **po fázích**, s **měřitelnými branami mezi nimi**
(`PLAN-ORCHESTRA-NG.md`). Když se v průběhu ukáže, že `core/` potřebuje víc než
~1 500 řádků nebo že šev netěsní (≤ 5 souborů), **varianta B se zastaví
a přejde se na A** — což je **platný výsledek**, ne neúspěch.

---

## 15. Co NEDĚLAT (anti-goals návrhu)

*(Každé „ne" je odpověď na konkrétní naměřenou vadu nebo na dřívější zamítnutí.)*

**Architektura a rozsah**

1. **Nedělat plugin systém, marketplace ani „platformu".** Adaptér je **CLI**.
   *(Zamítnuto v `PLAN-ROZVOJ` §1.5; `PLAN-ORCHESTRA-AI` §10.3 A1.)*
2. **Nezavádět vlastní DSL pro plán.** Zůstává JSON s validací.
3. **Nepřidávat druhý stack dřív, než je hotový první adaptér a falzifikátor
   švu** — jinak se staví abstrakce pro neexistujícího konzumenta.
4. **Nezvyšovat paralelismus dřív, než jsou leases a zámky v jádře** —
   dnes je `MAX_CONCURRENT=5` **neodvozené z měření**.
5. **Nedávat orchestraci do promptu žádný stav** (špička, kontext) —
   *měřeno: indikátory pro model jsou drahé a nevedou k rozhodnutí*.
6. **Nepřesouvat `HANDOFF.md` §10–§22** ani nic jiného „uklízet" v rámci této
   práce (`PLAN-DALSI-KROK` §3/1: **nejvyšší riziko**).

**Stav a spolehlivost**

7. **Nezapisovat stav dvěma cestami.** Dnes `/report` a `pollRuns` — a přesně
   v tom je S13 a S38.
8. **Nedovolit stav bez protějšku** (`done` bez `merged_at`, `blocked` bez
   důvodu, `awaiting_human` bez termínu a vlastníka).
9. **Nepolykat chyby** (`catch {}` bez události). Není to „robustnost",
   je to **tichý výpad schopnosti**.
10. **Nedělat strop pokusů na úkolu** — musí být na **granuli** (S14, S38).
11. **Neopravovat bránu dřív, než je jasné, co je špatně** — nástroj, nebo
    předpoklad testu.

**Brány a měření**

12. **Nepostavit bránu na nezměřené metrice** (vision blokující sloučení).
    *(`PLAN-ORCHESTRA-AI` §10.3 A2 — přesně chyba, kterou `AGENTS.md` zakazuje.)*
13. **Nepřidávat bránu, dokud předchozí umí selhat** — *„nová brána nad zeleným
    systémem nic nezmění"* (HLOUBKOVA-2 §⑨ bod 5).
14. **Nepřenášet skilly ani nástroje hromadně** — katalog je prefix a mění se
    jím cache; *naměřeno: 61 cache-bustů, 26,2 mil. tokenů za plnou cenu*.
15. **Neslibovat, co není naměřené** — `ptc` úsporu, přesnou příčinu cache-bustů,
    funkčnost cizích pluginů.
16. **Nemazat metriku, která nic nevykazuje, bez mutačního testu PŘED smazáním**
    (`PLAN-DALSI-KROK` §3/4). Nefunkční metriku **smazat**, ale až po důkazu.

**Data a záznamy**

17. **Nepřepisovat historická čísla** — označit „ve svém čase správná".
18. **Nemazat `done_note`** — je to jediné čitelné svědectví o S29;
    má se **začít číst**, ne smazat.
19. **Nemazat `_analyza/_archiv/`** (jediná cesta zpět, **není zálohovaný**) —
    a to ani až vznikne záloha, dokud se záloha neověří **obnovou**.
20. **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen doplňovat.
21. **Nemazat `sken-vazeb.py`, `p1-inventura-cest.py`, `p1b-odvozene-cesty.py`** —
    obsahují `Local-Deepseek` jako **VZOREK regexu**; kdo je „vyčistí", rozbije měřidlo.
22. **Nedělat junctionu na staré místo** — cesty mají **spadnout nahlas**.

**Provoz a rozhodnutí**

23. **Nepushovat bez vyžádání** a **nepřejímat rozhodnutí o směru za uživatele**.
24. **Nesázet na placený model** bez měření — orchestra dnes platí **0**
    a vyměnit nulu za nulu je nejdražší způsob, jak to zjistit.
25. **Nedělat z indexu kvality cíl** — Goodhart.

---

## 16. Jak se pozná, že návrh SELHAL (měřitelné falzifikátory)

> **Tohle je nejdůležitější kapitola pro toho, kdo se podle návrhu rozhoduje.**
> Návrh, který nemá jak selhat, není návrh.

| # | Podmínka | Kdy se měří | Co to znamená |
|---|---|---|---|
| **F1** | Přidání druhého stacku sáhne na **> 5 souborů** mimo `adapters/<stack>/` + `project.json` | fáze 7 | **šev netěsní** — abstrakce je na špatném místě; vrací se k variantě A |
| **F2** | `core/` potřebuje **> ~1 500 řádků** nebo obsahuje **jediné volání `fetch`/`DB`** | fáze 2 | do jádra prosáklo I/O → **rozhodování se nedá testovat offline** |
| **F3** | Router na **přehrání historie** (247 běhů) nevyřadí **aspoň polovinu** běhů, které umíraly do 30 s | fáze 4 | **kniha způsobilosti nic neumí** — je to jen log |
| **F4** | Po fázi 5 existuje **cesta, jak se stav změní bez události** | fáze 5 | stavový model selhal (S38 se vrátí v jiné podobě) |
| **F5** | Existuje brána, která se **přeskočí, aniž to je vidět** v `gates.ran < declared` | fáze 6 | vrstva verdiktů selhala (S27 se vrátí) |
| **F6** | Do 30 dnů po nasazení **není žádná granule sloučená s `p_success` > 0,5** u modelu, který měl dřív 0 | fáze 8 | systém se **neučí**, jen měří |
| **F7** | `human_inbox` roste a **nikdo ji nečte** | průběžně | „čeká na člověka" se stalo **smetištěm** — což je táž vada, kterou nahrazuje |
| **F8** | Počet **`not_run` u `hard` bran** roste, ale **nikdo neopravuje důvod** | průběžně | viditelnost bez následku — brány se učí být ignorovány |

> **A jeden falzifikátor, který platí pro celý dokument:** kdyby se ukázalo, že
> **`core/` nepotřebuje oddělit**, protože se dá dosáhnout téhož **uvnitř
> `index.ts`** (např. tím, že se rozhodovací funkce vytáhnou jako exportované
> čisté funkce **v témž souboru**) — pak je celá vrstva `core/` **zbytečná**
> a návrh je v tom bodě **špatný**.

---

# ČÁST IV — POCTIVOST

## 17. Co tenhle návrh NEZJISTIL a co neověřil

*(Povinná část. Co není přiznané, se čte jako tvrzení.)*

1. **Neměřil jsem živý stav orchestra.** Nezavolal jsem `/health`, `/roadmap`
   ani `/failed`; **stav D1, fronty a běhů neznám**. Všechna čísla o provozu
   jsou **převzatá s uvedeným zdrojem a datem** (§2).
2. **Nespustil jsem ani jednu bránu.** Čísla o branách („`check-wiring.py` nad
   0 souborů hlásí zelenou") jsou **citace** z analýz, ne moje měření — ověřil
   jsem jen to, co je výslovně označené **(vlastní čtení 5. 10. 2026)**.
3. **Vlastním čtením jsem ověřil jen `conductor/src/index.ts`** — konkrétně:
   nepřítomnost vazby na engine (`:304`, `:384`), `maxLinesOf`/`modelOf`
   (`:149–161`), dispatch payload (`:754–757`), guard cooldownu (`:613–621`),
   dispatch smyčku (`:925–946`), `stale-recovery` (`:813–834`), zombie invariant
   (`:859–871`) a `/report` (`:1444–1473`). **Zbytek kódu jsem nečetl.**
4. **Ekonomie „přidat providera" není nikde naměřená** — návrh v §8.2 proto
   **netvrdí**, kolik souborů stojí přidání providera; uvádí jen podmínku
   pro **stack** (≤ 5 souborů), kde je měření k dispozici z dřívějška.
5. **Návrh nepředpovídá zlepšení propustnosti.** Neuvádím „z 11,3 % na X %" —
   **nemám to z čeho spočítat** a vymyslet to by bylo to nejhorší, co tenhle
   dokument může udělat. Místo toho je v §16 **F3 a F6**: jak se to změří.
6. **Nevím, jestli je `core/` v TypeScriptu správná volba.** Zvolil jsem ho,
   protože **conductor už v TS je** a přesun je levnější než přepis; kdyby se
   ukázalo, že jádro má být jinde, je to **změna, ne vada návrhu**.
7. **S19–S28 nebyly v podkladech k dispozici** — plné znění je v
   `ANALYZA-HLOUBKOVA-ORCHESTRA.md` (1. kolo). Může se stát, že některá
   z tříd **S38–S45** je tam už pojmenovaná; pak platí **starší číslo**.
8. **Návrh neřeší**: LGTM/272 položek, přesnost vision, Blender na uzlu,
   CLIP drift, `kind`, druhou hru, `prepisy.json` jako samostatnou věc
   (pohltil ho `project.json`), a **nemění herní repo**.
9. **Neověřil jsem, že `HANDOFF.md` je v gitu** ani že 8 commitů je skutečně
   nepushnutých — **přebírám to** z `NEXT-SESSION-INSTRUKCE.md` a z měření
   podagentů (ti `git` spouštěli).
10. **Návrh je psaný v session s cwd ve stanici** (`C:\Users\Ssevc\Local-Deepseek`),
    takže se do ní **nenačetla projektová pravidla orchestra**
    (`E:\Workspaces\forge-orchestra\AGENTS.md`) — **přečetl jsem je explicitně**,
    ale je to přesně ten stav, který `PLAN-SEPARACE` D2 označuje za chybu
    (kdo navrhuje orchestra, má být rootovaný v repu).

---

## 18. Tabulka tvrzení → důkaz

*(U tvrzení, na kterých stojí rozhodnutí. „Druh" je úroveň důkazu:
**vlastní** = ověřil jsem čtením; **převzaté** = citace s uvedeným zdrojem
a datem; **odvozené** = plyne z jiných tvrzení.)*

| # | Tvrzení | Druh | Důkaz |
|---|---|---|---|
| T1 | Conductor nezná engine (2 zmínky, obě komentáře) | **vlastní** | `index.ts:304`, `:384`; hledání `godot`/`.gd`/`tscn` nad celým souborem → 2 nálezy |
| T2 | `size_lines` a `model` se nikde nekříží | **vlastní** | `index.ts:149–153` (jen → `max_lines`), `:156–161` (jen → tier), `:754–757` (payload) |
| T3 | Vazba na stack je ve workflow, ne v jádru | **vlastní + převzaté** | vlastní: T1; převzaté: `ci.yml:24–31`, `agent.yml:78–85`, `release.yml:40–47` |
| T4 | Modelový probe měří dostupnost, ne způsobilost | **vlastní** | `pick-provider.mjs:138–166` — `ping`, `max_tokens: 8`, timeout 45 s |
| T5 | Limity modelů jsou jen v komentářích | **vlastní** | `providers.json:2–31` (`_popis`, `_anyPriority`), strojová pole jen `skromny`/`anyPriority` |
| T6 | Cesta přes timeout obchází strop pokusů (S38) | **vlastní** | `index.ts:829–833` (nezapíše `naposledy_selhalo`) + `:618` (fallback na `tupd`) + `:751` (nový úkol s `attempts=0`) |
| T7 | `/report` dnes cooldown **neobchází** (S13 opraveno) | **vlastní** | `index.ts:1464–1472` — obě větve píší `naposledy_selhalo` |
| T8 | `done` je vázáno na `ok && merged` | **převzaté** | `index.ts:385`, `:400–405`; záznam opravy A1 (2. 10. 2026) |
| T9 | Úspěšnost free modelů 11,3 % (28/247), ~9 běhů na granuli | **převzaté** | `hl-priciny.mjs`, 247 běhů (`ANALYZA-HLOUBKOVA-ORCHESTRA.md` §0.3) |
| T10 | Orchestra je 82,7 % času mrtvá | **převzaté** | `hl-vytizeni.mjs`, 49,35 h (`ANALYZA-HLOUBKOVA-ORCHESTRA.md`) |
| T11 | Prompt ~14,4 tis. tokenů; Groq TPM 8 000 → nevejde se | **převzaté** | `HANDOFF` §18.17 (log #146), `_analyza\p18-prompt-tokeny.py` |
| T12 | Brány měřily přítomnost, ne chování; 3 PR prošla zeleným CI | **převzaté** | `OTEVRENA-TEMATA.md` ř. 70–84 (2. 10. 2026) |
| T13 | `acceptance`/`provides`: 0 čtenářů v kódu | **převzaté** | `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` §3.1 |
| T14 | Skutečný šev je „orchestrace × engine" uvnitř `.forge/` | **převzaté** | `ANALYZA-HLOUBKOVA-ORCHESTRA.md` §O4 (3 brány neutrální, 3 godot, 2 infra) |
| T15 | 17 z 24 souborů `.forge` je engine-independent | **převzaté** | `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` §1.1 |
| T16 | `read_image` a Blender nejsou v CI | **převzaté** | `MOZNOSTI-AGENTA.md` §6 |
| T17 | Dvě vrstvy mechanismu (měření vs. protějšek) | **převzaté** | `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` §O5 |
| T18 | Plugin systém pro enginy byl zamítnut jako předčasný | **převzaté** | `PLAN-ROZVOJ-ORCHESTRA.md` §1.5, §5 |
| T19 | `NA14` (TPM do `providers.json`) odloženo, protože nezměřené ≠ změřené | **převzaté** | `KRONIKA-PROJEKTU.md` §6 |
| T20 | Přidání stacku je dnes „výměna obálky v sedmi souborech" | **odvozené** | z T1 + T3 + `check-wiring.py:73`, `check-schema.py:212–218`, `check-assets.py:222–223`, `worker.mjs:207–233`, `files-to-edit.mjs:42` |

---

## 19. Co by tenhle návrh vyvrátilo

*(Konkrétní pozorování, ne obecná opatrnost.)*

1. **Kdyby `conductor/src/index.ts` obsahoval víc než dvě zmínky o enginu** —
   padá T1 a s ním i tvrzení „jádro je neutrální" (a celý smysl varianty B).
   *Ověřeno: 2 nálezy, oba komentáře.*
2. **Kdyby `/report` nepsal `naposledy_selhalo`** — padá T7 a S13 by zůstalo
   otevřené. *Ověřeno: píše, v obou větvích (`:1464–1472`).*
3. **Kdyby `stale-recovery` zapisoval do `roadmap`** — padá **S38**, tedy
   nejcennější vlastní nález tohoto dokumentu. *Ověřeno: nezapisuje
   (`:829–833` aktualizuje jen `tasks`).*
4. **Kdyby router nad historií nevyřadil ani 10 % běhů** — padá celá kapitola
   o modelové adaptaci (§9) a stačí zůstat u rotace.
5. **Kdyby přidání stacku nakonec stálo ≤ 5 souborů i bez `project.json`** —
   pak je deklarace zbytečná a návrh přidává soubor, který nic neřeší.
6. **Kdyby se ukázalo, že `HANDOFF.md` a `KRONIKA` jsou spolehlivé a úplné** —
   pak je část §11 (události a protějšky) přehnaná formalizace.
7. **Kdyby `read_image` v CI bylo možné** (např. jiný runner s vision) — padá
   část §10.4 o deklarovaných schopnostech jako *jediný* způsob, jak to řešit.
8. **Kdyby orchestr uvolnil placený model s velkým limitem** — pak je budgeter
   (§9.5) optimalizace, ne podmínka, a priorita se mění.

---

## 20. Verdikt znovu (na konci, aby se dal srovnat s §1)

1. **Jádro orchestra je neutrální už dnes** — a to je nejcennější, co projekt
   má; návrh ho **nepřepisuje, ale vysvobozuje** z obálky, kde je vazba na
   technologii rozesetá.
2. **Skutečný šev je „orchestrace × engine"** — návrh ho **pojmenovává
   kontraktem** (`project.json` + adaptér + gate kit) a dává mu **měřitelnou
   zkoušku** (≤ 5 souborů), místo aby tvrdil, že je správný.
3. **Modelová vrstva se musí naučit měřit a pamatovat si** — kniha způsobilosti,
   feasibilita promptu, klasifikace selhání a **umění neposlat nic** jsou
   odpověď na naměřených 11,3 % a ~9 běhů na granuli.
4. **Spolehlivost není „víc kontrol", ale „žádný stav bez protějšku"** —
   události, leases, invarianty s testy a `/health`, které **umí zčervenat**.
5. **Kvalita produktu se musí deklarovat zvlášť** — protože orchestra naměřeně
   **neumí posoudit obsah** a protože „PR je sloučené" už třikrát znamenalo
   „hotovo" u práce, která nefungovala.

> **Co se nezměnilo proti §1:** všech pět bodů platí ve stejné podobě.
> **Co se změnilo:** jsou u nich **konkrétní kontrakty, cena, riziko
> a falzifikátory** — tedy to, bez čeho je verdikt jen názor.

---

**Konec návrhu.** Pokračování je v `PLAN-ORCHESTRA-NG.md` (implementační plán:
fáze, brány mezi nimi, „hotovo znamená" a co z toho může začít hned).

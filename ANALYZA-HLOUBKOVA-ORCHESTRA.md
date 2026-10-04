# Hloubková analýza a návrh architektury orchestra

> **Co tenhle dokument JE:** analýza. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Autor:** session, která orchestra **nepsala, neopravovala ani neanalyzovala**
· **Datum:** 1. 10. 2026
· **Měření:** 13:35–14:10 UTC a **druhé kolo 14:30–14:45 UTC**
**Zadání:** `ANALYZA-HLOUBKOVA-ZADANI.md` (§5 struktura, §4.1 devět optik, §6 deset otázek)
**Podklady:** `_analyza\HLOUBKOVA-MERENI.md` — surová naměřená čísla, každé
s příkazem. Když se tenhle dokument a podklady rozejdou, platí podklady.
**Pokračování:** `_analyza\HLOUBKOVA-MERENI-2.md` — **druhé kolo měření** po
uzavření fáze A. Přineslo **S29 a S30** (obě naměřené, ne odvozené) a tři moje
opravy: mrtvé odkazy na smazaný `kontrola-schematu.py`, konce řádků a BOM,
a srovnání `done` v roadmapě se stavem v D1.
**Kdo čte jen jedno z těch dvou měření, vidí jiný stav** — a to je záměr.

---

## 0. Jak tenhle dokument číst

### 0.1 Značky (povinné podle zadání §3.1)

| Značka | Znamená |
|---|---|
| **měřeno** | Spustil jsem to a vidím výsledek; **příkaz je vždy u tvrzení** (nebo v podkladech) |
| **kód** | Přečtený řádek zdrojáku — `soubor:řádek`, ověřitelný očima |
| **odvozeno** | Logický důsledek měření a kódu; **není to přímý výstup nástroje** |
| **nevím** | Nedohlédl jsem — patří do §10, ne do těla |

### 0.2 Změna, kterou musí čtenář znát: kód se měnil POD RUKAMA

**Tohle je naměřený fakt, ne omluva** (podklady §10):

```
13:43 UTC  git -C orchestra status --porcelain   →   M README.md
13:52 UTC  git -C orchestra status --porcelain   →   M README.md
                                                     M repo/.github/workflows/release.yml  (mtime 13:48:20)
                                                     D tools/kontrola-schematu.py
                                                     M tools/test-cooldown.py              (mtime 13:46:18)
                                                     M tools/validate-all.mjs              (mtime 13:46:35)
```

Během analýzy **pracovala na orchestra jiná session** a plnila kroky A1, A2 a D1
implementačního plánu. Proto:

- **`HEAD` = commit `525d45b`** (poslední commitnutý stav) — tím se řídí každé
  tvrzení označené „HEAD".
- **„pracovní strom"** = stav k **13:57 UTC** — tím se řídí tvrzení o opravách.
- U každého tvrzení o **stavu** je řečeno, které z toho to je. Kde to řečeno
  není, platí pro obojí (architektura se tou opravou nezměnila).

**P1 platí i na tenhle dokument:** statický počet vzorů v souboru není měření.
Proto jsou všechna čísla o chování z **výstupu běhu**, ne z počtu výskytů.

### 0.3 Tři vlastní měření, která v žádném existujícím dokumentu nejsou

| # | Co | Příkaz | Výsledek |
|---|---|---|---|
| **M1** | **Využití orchestra za 49,35 h** | `node _analyza\hl-vytizeni.mjs` | orchestra **běžela 6,86 h = 13,9 %** okna; **8 oken nečinnosti = 40,79 h = 82,7 %** |
| **M2** | **Rozpad příčin selhání všech 240 běhů** | `node _analyza\hl-priciny.mjs` | agent **nic nezměnil 95×**, testy 82×, parsování 27×, úspěch 28×; **55 % selhaných běhů skončilo do 30 s** |
| **M3** | **SQL guardu ze zdroje v SQLite + mutační test** | `python _analyza\hl-sql.py` + `hl-mutace.py` | 7 scénářů, **0 chyb**; mutační test **3/3 vady chyceny** |

Všechna tři vznikla **spuštěním**, ne čtením. U M1 a M2 jde o **úroveň 3**
(provoz, ze živého API), u M3 o **úroveň 2** (izolovaně, ale se skutečným SQL
ze zdroje).

---

## 1. Verdikt v pěti větách

*(Napsán na začátku; **přepsaná verze je v §13** — a je jiná, což je vidět.)*

1. **Orchestra je řemeslně dobrý systém pro JEDNU hru a jeden engine, jehož
   problém není uvnitř komponent, ale v tom, že mezi nimi nejsou smlouvy** —
   pole `acceptance` a `provides` v roadmapě **nečte žádný kód** (měřeno)
   a model dostane soubory závislostí, ale ne jejich rozhraní.
2. **Hlavní brzdou není model ani kvóta, ale smyčka pokusů**: z 240 běhů
   agent **ve 95 případech nezměnil nic** a **55 % selhání skončilo do 30 sekund**
   — to nejsou neúspěšné pokusy o práci, to jsou pokusy, které ani nezačaly.
3. **Orchestra je mrtvá 82,7 % času** a **není to kvůli červenému CI** (to bylo
   během všech osmi naměřených oken nečinnosti zelené) — brzdí ji **cooldown,
   který se ptá na čas vzniku řádku místo na selhání**.
4. **Druhá hra dnes nevznikne**: šablona je 27 souborů, ale `install-into-repo.ps1`
   vyžaduje smazanou GameForge, `.gitignore` negeneruje nikdo jiný než ten skript
   a **12 odkazů v šabloně míří na soubory, které v novém repu nejsou** (měřeno
   simulací instalace) — CI nové hry by spadlo dřív, než by cokoli změřilo.
5. **Co s tím:** nedělat platformu ani abstrakce (na to je zadání i plán
   jednoznačný), ale **zavést tři deklarace** — čím hra je (`forge.config.json`),
   kdo co vlastní (`prepisy.json`) a **čím se granule prokazuje** (kontrakt
   v `owns`); a k tomu **přestat měřit čas vzniku a začít měřit selhání**.

---

## 2. Co je orchestra — mapa systému

*(Diagram, ne seznam. Šipka = směr toku; „(kóp.)" = soubor existuje víckrát.)*

```
                          ┌──────────────────────────────────────────────┐
                          │  ČLOVĚK (Ssevc)                              │
                          │  · rozhoduje (O1–O10), schvaluje PR, pushuje │
                          │  · čte Telegram / ntfy notifikace            │
                          └───────┬──────────────────────┬───────────────┘
                                  │ registruje hru       │ čte stav
                                  ▼                      ▼
   ┌───────────────────────────────────────────┐   ┌──────────────────────┐
   │  CONDUCTOR — Cloudflare Worker + D1       │   │ orchestra/tools/     │
   │  https://forge-conductor.ssevcikm.workers │   │ 70 souborů, 1,5 GB   │
   │  cron "* * * * *" (každou minutu)         │   │ (z toho Godot 172 MB)│
   │                                           │   │ 18 z nich nikdo      │
   │  NEVOLÁ ŽÁDNÉ LLM. Jen:                   │   │ nikde nezmiňuje      │
   │   · čte roadmap.json z repa hry (GitHub)  │   └──────────────────────┘
   │   · zakládá úlohy v D1                    │
   │   · dispatchuje GitHub Actions (17 endpointů)
   │   · polluje výsledky běhů                 │
   │   · notifikuje (Telegram / Discord / ntfy)│
   └───────┬───────────────────────────▲───────┘
           │ workflow_dispatch         │ POST /report (HMAC)
           │ inputs: task_id, run_key, │
           │ grain, attempt, model,    │
           │ max_lines, prompt, title  │
           ▼                           │
   ┌───────────────────────────────────────────────────────────────┐
   │  REPO HRY  games/uo-shadows  (klon) ⟷ ssevcikm-spec/uo-shadows│
   │                                                               │
   │  .github/workflows/  (kóp. ze šablony, 4 soubory)             │
   │    agent.yml  691 ř. ── aider + 5 free LLM ─┐                 │
   │    ci.yml     182 ř. ── 12 bran ────────────┼─► PR ─► merge    │
   │    release.yml 156 ř. ── build + Pages      │   (auto, když    │
   │    model-check.yml       ── hlídá modely    │    gate+CI OK)   │
   │                                             │                 │
   │  .forge/  (kóp. ze šablony, 24 souborů)     │                 │
   │    roadmap.json  ← PLÁN (18 granul) ────────┘                 │
   │    check-schema.py / check-assets.py / check-wiring.py        │
   │    verify-level-render.py / vision.mjs / baseline.py          │
   │    pick-provider.mjs → stahuje providers.json Z ORCHESTRY     │
   │    files-to-edit.mjs → z `owns` granule dělá --file/--read     │
   │                                                               │
   │  scripts/ 9× .gd · assets/ (spec, mapy, sprity) · tests/      │
   └───────────────────────────────────────────────────────────────┘
           ▲                                       ▲
           │ kopíruje (install-into-repo.ps1)      │ pracuje (5 kinds:
           │                                       │ assets,test,build)
   ┌───────┴───────────────────────┐       ┌───────┴──────────────────────┐
   │  ŠABLONA  orchestra/repo/     │       │  PULL-WORKER (domácí uzel)   │
   │  27 trackovaných souborů      │       │  pc-domaci (off, 29. 9.)     │
   │  = 18 × .forge + 4 × .github  │       │  oracle-frankfurt (žije)     │
   │    + CONVENTIONS.md           │       │  POST /heartbeat, /claim     │
   │    + .gitattributes           │       └──────────────────────────────┘
   │  ** 0 souborů hry **          │
   │  (žádný project.godot, žádné  │
   │   scripts/, assets/, tests/)  │
   └───────────────────────────────┘
```

**Tři věty, které z diagramu plynou a které nejsou vidět ze seznamu souborů:**

- **Šablona neobsahuje hru, ale obsahuje brány, které hru měří.** Nový repozitář
  z ní tedy nemůže zezelenat: `check-wiring.py` nad nulou `.gd` souborů hlásí
  „Vše v pořádku" (`kód`: `check-wiring.py:73`), `check-schema.py` hledá
  `assets/spec.json`, který tam není. **(odvozeno z měření v §7.9.)**
- **Zdroj pravdy o plánu je soubor v repu hry, ale stav o plánu je v D1.**
  Dnes se rozešly: D1 zná 10 hotových granul, soubor jen 2 (měřeno, §6.4).
- **Provoz orchestra má čtyři nezávislá místa, kde může tiše přestat fungovat:**
  cron v Cloudflare, dispatch na GitHub, práce v Actions, sběr výsledku v tiku.
  Každé z nich má vlastní způsob, jak vypadat zdravě, i když nefunguje.

---

## 3. Co orchestra je — inventura vlastností

### 3.1 Soubory a jejich role

| Role | Co to je | Kde | Počet |
|---|---|---|---|
| **Jádro** (nezávislé na hře i enginu) | conductor, tabulky D1, endpointy | `conductor/src/index.ts` | 1 368 řádků, 90 SQL dotazů, 17 endpointů |
| **Jádro** | nástroje pro orchestraci | `orchestra/tools/` | **70** (měřeno `git ls-files tools`); **18 z nich nikde nikdo nezmiňuje** |
| **Obálka** (kopíruje se do hry) | brány a pomocníci | `orchestra/repo/.forge/` | 18 + 3 netrackované |
| **Obálka** | workflowy | `orchestra/repo/.github/workflows/` | 4 |
| **Kopie** (existuje v šabloně i ve hře) | 27 souborů | obojí | **19 shodných, 8 rozdílných** (měřeno) |
| **Kopie** (třetí, osiřelá) | `vision.test.mjs` v rootu workspace | `vision.test.mjs` | 11 983 B, 5 OK / 23 chyb (podle HANDOFF, já nemohl spustit — §10) |
| **Mrtvé** | `tools/test-local.ps1` (volá `$Game`, parametr je `$Project`) | `orchestra/tools/` | — |
| **Mrtvé** | `tools/kontrola-schematu.py` (stará slepá kopie brány) | do 13:52 UTC | 305 řádků; **v HEAD ještě je** |
| **Mrtvé** | `tools/validate-all.mjs.zaloha` | `orchestra/tools/` | — |
| **Mrtvé** | `worker.mjs` krok `forge:` (default `FORGE_CMD` na smazaný `forge.cmd`) | `.forge/node/worker.mjs:83` | — |

### 3.2 Brány a kontroly

**Dvanáct bran v `ci.yml`, osm v `agent.yml`.** Tabulka je na **hlavní** brány:

| Brána | Kde běží | Co měří | Tvrdá? | Umí selhat? |
|---|---|---|---|---|
| `check-schema.py` | `ci.yml:69` | deklarace vs. skutečnost (spec, mapy, dlaždice, `level.gd`) | **ANO** | ANO — 17 offline testů, ověřeno mutačně |
| testy hry (`run_tests.gd`) | `ci.yml:75` | funkčnost | **ANO** | ANO |
| `check-assets.py` | `ci.yml:87` | sprity, hudba proti `spec.json` | **ANO** | **jen částečně** — animace a hudba se přeskočí (S3) |
| `check-wiring.py` | `ci.yml:95` | každá funkce je volaná | **ANO** | **NE nad cizím enginem** — 0 `.gd` → zelená (S3) |
| smoke (`SCRIPT ERROR`) | `ci.yml:103-110` | hra se spustí bez chyby skriptu | **ANO** | ANO (exit kód nestačí, čte se text) |
| `verify-level-render.py` | `ci.yml:136` | snímek odpovídá mapě | **ANO** | ANO, ale neblokuje při chybějícím OpenGL |
| `vision.mjs` | `ci.yml:166` | obsah snímku (model s viděním) | **NE** (`continue-on-error`) | **záměrně ne** — chybovost modelu |
| `baseline.py` (LGTM cache) | jen lokálně | schválený a nezměněný obrázek | **NE** | v CI neplatí nikdy (S10) |
| **parse gate** | `agent.yml:9` | GDScript se naparsuje | **ANO** | ANO — **27× to udělal** |
| **stínění `class_name`** | `agent.yml` (staticky) | vnořená třída přebije globální jméno | **ANO** | ANO (Godot to sám nepozná) |
| **auto-merge gate** | `agent.yml:595-645` | velikost + složka + chráněné soubory | **ANO** | ANO → „nechá se k ruční kontrole" |
| **čekání na CI** | `agent.yml:647-674` | kontrola jménem „Testy a build" | **ANO** | **umí vypršet na `timeout` a to nikoho neupozorní** (S24) |

**Tři brány, které se tváří jako živé, ale nic nezměřily** (navazuje na S3/S10):
`check-wiring.py` nad jiným enginem, `check-assets.py` animace a hudba,
`baseline.py` cache mimo repo hry. **U všech tří je to dnes poznat z výstupu
(poznámka), ale nikdo ji nečte jako vadu.**

### 3.3 Stavy a přechody — co se děje s granulí

```
  roadmap.json (soubor v repu hry)
        │  conductor si ho přečte přes GitHub API v každém tiku
        ▼
  ┌─────────────────────────────────────────────────────────────────┐
  │ D1: roadmap (item_id = {game_id}/{grain_id})                    │
  │   'queued' ──► 'done'   (pollRuns / /report / merged PR)        │
  │      └──────► 'failed'  (poslední pokus)                        │
  └─────────────────────────────────────────────────────────────────┘
        │ INSERT INTO tasks (nový řádek pro KAŽDÝ pokus)
        ▼
  D1: tasks   'ready' ──dispatch──► 'running' ──► 'done'
                 ▲                    │            (report success)
                 │                    ├──► 'ready' (report failure, attempts<5)
                 └────────────────────┘           │
                 │                                └──► 'failed' (attempts>=5)
                 └──► 'blocked'  (invariant: úkol bez řádku v roadmapě;
                                  /tasks/cleanup; ruční zásah)
        │
        ▼
  D1: runs    'running' ──► 'success' | 'failure' | 'timeout' | 'abandoned'
                            | 'dispatch_failed'
        │
        ▼
  GitHub Actions: agent.yml ──► PR ──► auto-merge ──► merge do main
        │                                              │
        ▼                                              ▼
  release.yml ──► Release "latest" + GitHub Pages   CI na main (green/red)
```

**Devět míst, kde se granule zastaví a nikdo se to nedozví** (podrobně §5):

1. `roadmapTick` nenačte roadmapu → `continue` → „čeká na závislosti" (S19)
2. guard ji nevydá, protože `updated_at` je mladý (S12)
3. `/report` nezapíše roadmapu → cooldown se obejde (S13)
4. `dispatchWorkflow` selže → úkol zpět na `ready`, **bez backoffu**, dvě notifikace
5. běh vyprší (`STALE_MINUTES=90`) → úkol zpět, pokud `attempts<5`
6. agent nic nezmění → `nochange` (95× naměřeno)
7. agent změní, ale parse gate to shodí (27×)
8. agent projde, testy spadnou (82×)
9. PR se nesloučí (gate/CI) → **čeká na člověka, nikdo není upozorněn**

### 3.4 Konfigurace a zdroje pravdy

| Co | Kde je zdroj | Kde je kopie | Rozchází se to? |
|---|---|---|---|
| modelový řetězec | `orchestra/repo/.forge/providers.json` | `.forge/providers.json` v každé hře | **ne dnes** (bajtově shodné) — ale fetch je z `raw.githubusercontent.com` |
| plán (roadmapa) | `roadmap.json` v repu hry | tabulka `roadmap` v D1 | **ANO** — 4 granule jen v souboru, 8 bez `done` proti D1 (měřeno) |
| profil vize | `vision-profile.json` v repu hry | — | šablona má **jiný tvar** klíčů než hra (`popis_stylu` vs. `styl_popis`) |
| brány | šablona | kopie ve hře | `kontrola-driftu.mjs` hlídá **12 z 27** souborů |
| limity (PR, pokusy, souběh) | `wrangler.toml` (globální!) | — | **per hru se nastavit nedají** (S11) |
| tajemství | GitHub Secrets **každé hry** | — | 5 klíčů LLM + PAT + webhook secret na repo |
| `game_id` | parametr v `POST /game` | **47 souborů** v `tools/` mají hru napevno | neřešeno (ST10) |

### 3.5 Rozhraní

**Conductor (17 endpointů, měřeno walkem nad `index.ts`):**

| Endpoint | Metoda | Kdo ho volá | Chráněný? |
|---|---|---|---|
| `/health` | GET | `status.mjs`, člověk | **ne** (veřejný) |
| `/tick` | POST | cron, `bin/task.mjs`, člověk | `x-forge-secret` |
| `/poll` | POST | `bin/task.mjs` | secret |
| `/queue`, `/status`, `/workers`, `/games`, `/failed`, `/roadmap` | GET | `status.mjs`, `fronta.mjs`, nástroje | secret |
| `/game`, `/game/active` | POST | `start-orchestra.mjs`, člověk | secret |
| `/roadmap/reset` | POST | `roadmap-reset.mjs`, `reset-dry.mjs` | secret |
| `/tasks/cleanup` | POST | člověk | secret |
| `/heartbeat`, `/claim` | POST | `worker.mjs` (domácí uzel) | secret + hlavička |
| `/task` | POST | **`bin/task.mjs`; kdo další — nevím** | secret |
| `/report` | POST | `agent.yml`, `worker.mjs` | HMAC podpis **nebo** secret |

**Workflow (souborová smlouva):** `agent.yml` má 9 vstupů
(`task_id, run_key, kind, title, prompt, max_lines, model, grain, attempt`),
z toho **3 povinné**. Conductor je posílá v `payload` úlohy; **nikde není
verze ani schéma** — když se jeden vstup přejmenuje, pozná to jen drift
kontroly, a ta `agent.yml` sice sleduje, ale **porovnává jen strukturu**
(S8: `FORGE_ATTEMPT` se přesunul mezi kroky a drift to přehlédl).

---

## 4. Katalog tříd selhání — pokračování řady S19–S30

**Řada S1–S18 existuje** (`ANALYZY-ARCHITEKTURY-ORCHESTRA.md` §2 a §8.8)
a **neopisuju ji**; kdo ji chce celou, ať ji čte tam. Následujících osm tříd
je **nových** — každá vznikla z měření, které v té analýze není, a každá má
u sebe řečeno, **čím se liší od nejbližší starší třídy**.

#### S19 — Model dostane soubory závislostí, ale ne jejich smlouvy

| | |
|---|---|
| **Kde** | `agent.yml` (krok „Spusť agenta"): `files-to-edit.mjs --read-deps` čte **jen `owns` přímých závislostí**; naměřeno v běhu #243: model dostal `skills.gd`, ale **ne** `attributes.gd` (2. úroveň) |
| **Jak se to pozná dnes** | **Hlasitě, ale draze** — parse gate shodí běh. 27 z 240 běhů (11 %) |
| **Naměřené chyby** | `Identifier "Skills" not declared` (skills.gd **nemá `class_name`**), `Could not find type "Economy"` (má ho, ale model ho neměl v chatu), `Member "position" redefined` |
| **Čím je to nové** | S4 je „brána závislá na tvaru kódu"; tohle je **něco jiného: kontrakt mezi granulemi neexistuje jako objekt**. V celé roadmapě je **21 výskytů `.gd` závislostí a ANI JEDEN nemá `class_name`** (měřeno `hl-typy.py`) |
| **Co by to odhalilo** | Aby granule deklarovala, **co poskytuje** (dnes `provides` neexistuje v kódu) a co **vyžaduje**; a aby harness dal modelu i smlouvy 2. úrovně |

#### S20 — Agent mezi pokusy nevidí, co minule nevyšlo

| | |
|---|---|
| **Kde** | `agent.yml` sestavuje prompt **jen z `prompt` granule** (`--message "$FORGE_PROMPT"`); `attempt` mění **jen pořadí modelů** (`pick-provider.mjs`), ne obsah zadání |
| **Jak se to pozná dnes** | **Nijak** — vypadá to jako „model je slabý". Naměřeno: u 21 % běhů se pokus opakuje s jiným modelem a **stejným zadáním** |
| **Doklad** | Běh #243 a #237: **tatáž granule `sim.mining`, tatáž chyba** (`Identifier "Skills" not declared`), jiný model. Totéž #244 a #238 (`Could not find type "GameItem"`) |
| **Čím je to nové** | S17 je „model nezná verzi enginu" — to je **neznalost**. Tohle je **ztráta informace mezi pokusy**: conductor má `log_tail` (8 000 znaků) i `summary`, ale **do dalšího zadání je nepředá** |
| **Co by to odhalilo** | Do promptu druhého pokusu přidat **konkrétní chybu z minula** (`log_tail` je k dispozici) a zakázat stejný postup. Dnes to nikdo nedělá |

#### S21 — Strop pokusů se resetuje → v praxi neexistuje

| | |
|---|---|
| **Kde** | `index.ts:638-647` — `roadmapTick` zakládá pro každý retry **nový řádek `tasks`** s `attempts=0` (dispatch ho zvedne na 1). `MAX_ATTEMPTS=5` (`wrangler.toml:55`) platí na **úkol** |
| **Jak se to pozná dnes** | **Nijak.** Watchdog `ESCALATE_AFTER=8` (`index.ts:246`) je **vyšší než strop 5** a počítá běhy **úkolu** → nikdy nedosáhne prahu (S14 to popisuje jako „strop váže úkol") |
| **Naměřeno** | **7 úloh mělo víc než 5 běhů** — #115, #116, #117 **devět**; **52 běhů z 247 (21 %) proběhlo v úlohách, které už strop překročily**. Retry uvnitř úlohy se navíc **nedrží cooldownu**: medián mezery mezi pokusy téhož úkolu je **3,2 min**, 94 % mezer je pod 60 min |
| **Čím je to nové** | S14 je *popis kódu* („strop váže úkol"). Tohle je **naměřený důsledek**: kolik běhů to spálí a jak rychle. Bez toho se nedá rozhodnout, jestli má smysl přidávat pokusy |
| **Co by to odhalilo** | Strop **na `item_id` granule** (počítat `SELECT COUNT(*) FROM runs …` přes všechny úkoly té granule), ne na `task_id` |

#### S22 — Smlouvy, které jsou jen data

| | |
|---|---|
| **Kde** | `roadmap.json` má pole `acceptance` (18×), `provides` (3×), `done_note`; `_popis` v souboru je **dokumentace uvnitř JSON** |
| **Jak se to pozná dnes** | **Nijak — a to je ta vada.** Naměřeno Python walkem s **odstraněnými komentáři**: `acceptance` = **0 souborů v kódu**, `provides` = **0**, `done_note` = **0**. `kind` kód jen uloží (`tasks.kind`) a použije v šabloně PR komentáře |
| **Čím je to nové** | S16 je „stavy, které se zapisují a nikdo je nečte". Tohle je **totéž u smluv** — a je to horší, protože `_popis` v `roadmap.json` **slibuje**, že `acceptance` říká „jak se pozná hotovo". Čte to jen člověk |
| **Co by to odhalilo** | Buď `acceptance` **číst** (mapovat názvy bran na kroky `ci.yml`), nebo ho **nepsat**. Dnes je to past na toho, kdo plán píše: vypadá to jako zadání, ale je to komentář |

#### S23 — Šablona nemá bootstrap: nový repozitář nemůže zezelenat

| | |
|---|---|
| **Kde** | `orchestra/repo/` = 27 trackovaných souborů, **žádný `project.godot`, žádné `scripts/`, `assets/`, `tests/`** |
| **Jak se to pozná dnes** | **Nijak** — dnes existuje jedna hra a ta vznikla ručně. Naměřeno simulací instalace (`hl-instal.mjs`): v novém repu zůstane **12 odkazů na soubory, které tam nejsou** (`assets/spec.json`, `assets/levels/main.json`, `manifest.json`, `level.gd`, `world.gd`, `enemy.gd`, `game.gd`, `tests/run_tests.gd`, `baseline.json`, …) |
| **Druhá půlka** | `install-into-repo.ps1:34-38` **vyžaduje** `projects/<Projekt>/project.godot` a `:86` posílá uživatele na `forge.cmd` — **obojí je smazaná GameForge** (měřeno: `Test-Path projects` = False, `forge.cmd` neexistuje). `.gitignore`, na kterém stojí S7/L5, **generuje jen tenhle skript** (`:165`) |
| **Čím je to nové** | Analýza to měla jako dílčí nález („install-into-repo je mrtvá větev") a plán jako ST6/F4.1/D3. **Nové je měření, co se stane**: šablona **není seed, je to obálka bez obsahu** — a brány v ní měří soubory, které do ní nikdo nedodal |
| **Co by to odhalilo** | Onboarding **jako test** (plán to má v D3): založit hru ze šablony a pustit brány. Dokud to není, je každá nová hra ruční práce |

#### S24 — Sloučení PR je slepá ulička s tichým koncem

| | |
|---|---|
| **Kde** | `agent.yml:647-674` — čeká na check-run jménem **„Testy a build"** 30× po 20 s = **max 10 minut**; pak nastaví `ci=timeout` a krok „Když pravidla neprošla" (`:683-691`) jen **napíše komentář do PR** |
| **Jak se to pozná dnes** | **Nijak na straně orchestra**: běh `agent.yml` skončí **úspěšně**, conductor zapíše `success`, PR zůstane otevřený. Čeká na člověka, který se to **nikdy nedozví** — notifikace o `ci=timeout` neexistuje |
| **Doklad** | **kód** (`agent.yml:660-691`): `echo "ci=timeout" >> "$GITHUB_OUTPUT"` a krok s `if: … != 'ok'` jen komentuje. **Odvozeno:** stav „PR čeká na člověka" se v D1 neobjeví. **Neměřeno:** že timeout v produkci nastal — nevím o něm (§10) |
| **Čím je to nové** | S13 je „cooldown se obchází přes `/report`" (stav úlohy). Tohle je **konec toku**: stav úlohy je `done`, stav práce je „otevřený PR" — a **nikdo to neporovnává** |
| **Co by to odhalilo** | Aby `ci=timeout` **skončil nenulově** a conductor to viděl jako selhání; a aby se stav PR kontroloval i později (dnes `pollRuns` čte PR jen u `run.conclusion === 'success'`, `index.ts:368-377`) |

**Pozor — co jsem si musel opravit:** nabyl jsem dojmu, že velký PR
**#27** („80 řádků `.import`") prošel gate **špatně**. Ověřeno (GitHub API,
`/pulls/27`): PR měl **+18/−0 řádků ve 2 souborech** a byl to **správný**
výsledek — 80 řádků `.import` se do limitu nepočítalo, přesně jak komentář
v `agent.yml:602-606` tvrdí. **Oprava z 30. 9. platí.** Do tabulky to patří
jako *neškodné*: `case` pro složku je sice před přeskakováním generovaných
souborů, ale u tohohle PR to nic nezkazilo.

#### S25 — Schválení, které je strojový záznam
| | |
|---|---|
| **Kde** | `games/uo-shadows/.forge/vision/baseline.json` |
| **Naměřeno** | **272 položek**, **všech 272** má `schvalil: "agent-init"`, **všech 272** má v poznámce „PŘEVZATO AGENTEM … **čeká na lidskou kontrolu**", **všechna** časová razítka jsou v **jedné minutě** (`23:07:31`–`23:07:32`), `_ceka_na_lgtm: true` |
| **Jak se to pozná dnes** | `validate-all.mjs` tuhle hodnotu čte (`0 = schváleno, 1 = čeká na LGTM`) — takže **gate ví**, že čeká. Nikdo ji nezvrátí |
| **Čím je to nové** | N11 v předchozí analýze to našla jako „mrtvou bránu" (schválení, které nikdo neudělal). **Nové je, že to není jen mrtvá brána — je to falešný záznam o lidském rozhodnutí**, a v CI stejně neplatí (S10). Tři vrstvy téhož: záznam lže, cache se nepoužije, kontrola neblokuje |
| **Co by to odhalilo** | Přejmenovat na `schvalil: agent-init` + `stav: ceka_na_lgtm` (ať to nikdo nečte jako schválení), nebo pole `schvalil` nechat prázdné, dokud tam není člověk |

#### S26 — Jeden `FORGE_SECRET` je řídicí i datová rovina

| | |
|---|---|
| **Kde** | `orchestra/repo/.forge/node/.env` (523 B, **netrackovaný**) obsahuje `FORGE_URL`, `FORGE_SECRET`, `FORGE_WORKER`, `FORGE_KINDS`, `FORGE_GODOT`. `install-into-repo.ps1:94-96` kopíruje `.forge` **rekurzivně** do každé hry |
| **Co ten secret umí** | `index.ts:62-64` — `secretOk()` je **jediná** kontrola pro `/task`, `/game`, `/game/active`, `/roadmap/reset`, `/tasks/cleanup`, `/claim`, `/heartbeat` **i `/report`** (když není HMAC). Kdo ho má, **vkládá úlohy** — a `worker.mjs` je na domácím počítači **vykoná** (krok `shell:` se ptá y/N, ale ostatní kroky ne) |
| **Jak se to pozná dnes** | S7 to má jako „tichý přenos tajemství do cizího repa" a je to **zavřené v `.gitignore`** (L5, ověřeno). **Nové je, že ani dokonalý `.gitignore` ten problém neřeší**: soubor se má do hry kopírovat (bez něj domácí uzel nemá jak volat conductora) |
| **Naměřeno** | V herním repu `.forge/node/.env` **není** (dobře), ale v šabloně **je**; `.gitignore` ho ignoruje; `install-into-repo.ps1` ho kopíruje |
| **Co by to odhalilo** | Oddělit secret domácího uzlu (`FORGE_WORKER_SECRET`, právo jen `/heartbeat` + `/claim` + `/report`) od řídicího (`FORGE_ADMIN_SECRET`). Pak únik z herního repa **neznamená** právo zadávat práci |

#### S27 — Brána, která kontroluje seznam, ne strom (naměřeno na sobě)

*(Tahle třída nemá čtyři tabulková pole jako ostatní — je to **jiný druh
pozorování**: nevznikla z kódu orchestra, ale z toho, že jsem na konci analýzy
spustil její vlastní brány. Nechal jsem ji proto v přirozeném tvaru.)*

**Tuhle třídu jsem našel tak, že jsem si na ni sáhl.** Zadání §8.3 nařizuje po
každé editaci dokumentace spustit `kontrola-diakritiky.py`, `over-dokumentaci.py`
a `over-skilly.py`. Chtěl jsem ověřit, že **můj nový dokument** projde — a zjistil:

```
python orchestra\tools\kontrola-diakritiky.py     → VŠE OK, exit 0
   ale: kontroluje PEVNÝ seznam 22 souborů (17 cest v workspace + 5 skillů)
   a mezi nimi ANALYZA-HLOUBKOVA-ORCHESTRA.md NENÍ
python orchestra\tools\over-dokumentaci.py        → „Kontrol: 63, chyb: 0", exit 0
   ale: je to seznam TVRZENÍ o konkrétních souborech (63 kontrol)
   a o novém dokumentu žádné nejsou
```

**Co to znamená:** **obě brány projdou zeleně nad dokumentem, který nikdy
neotevřely.** A **komentář v `kontrola-diakritiky.py:20-23` to přesně
pojmenovává** — *„Nový dokument se musí přidat SEM, jinak ho kontrola nevidí
(stejná past jako u netrackovaného souboru v gitu)"*. **Tedy: znalost tam je,
mechanismus ne.** Seznam se musí udržovat ručně — a to je **tatáž vada jako
`kontrola-driftu.mjs` (S5) a `validate-all.mjs` (S1)**: **ruční seznam místo
odvození ze stromu.**

**Jak jsem to obešel:** `_analyza\hl-diakritika.py` — spustí **stejný vzor**
(tři znaky, které vznikají dvojím kódováním UTF-8 přes Windows-1250) na soubory,
které jsem vytvořil nebo změnil:

```
OK   ANALYZA-HLOUBKOVA-ORCHESTRA.md    101 121 znaků  rozbito: ne
OK   HLOUBKOVA-MERENI.md                24 488 znaků  rozbito: ne
OK   OTEVRENA-TEMATA.md                 15 554 znaků  rozbito: ne
VYSLEDEK: 0 chyb   →   a kontrola gate ví o novém dokumentu: NE
```

**(Proč jsou ta čísla jiná než na začátku analýzy: dokument se mezi měřeními
rozrostl o S27/S28 a §10–§15. To je táž past P4, kterou popisuju u `release.yml`
— a tady je vidět, že se jí nedá vyhnout, jen ji přiznat.)**

**Čím je to nové proti S1/S5:** tam jde o **kód orchestra** (brána měří jinou
kopii; drift má ruční seznam). **Tohle je táž vada v nástrojích, které hlídají
DOKUMENTACI** — tedy v poslední vrstvě, kde by se to čekalo nejméně: **brány,
které si samy nehlídají, že měří.** A je to **třetí nezávislý výskyt téhož
vzorce** (kód → drift → dokumentace), což ho posouvá z „náhody" do „vzorce".

#### S28 — Všechna selhání mají stejný stav, i když mají různou příčinu
| | |
|---|---|
| **Kde** | `index.ts:391-405` (`pollRuns`) a `:1330-1345` (`/report`) — obojí dělá **totéž**: `nextStatus = attempts >= 5 ? 'failed' : 'ready'` a `roadmap.status = 'queued'` |
| **Co je vada** | **Různé příčiny končí ve stejném stavu** a systém s nimi zachází stejně. Přitom naměřené příčiny jsou **tři kvalitativně různé věci**:<br>· **agent nic nezměnil** (95×) — model zkusil a nedodal diff;<br>· **parse gate** (27×) — dodal, ale kód se neparsuje;<br>· **testy** (82×) — kód je platný, ale chová se špatně.<br>Každá z nich potřebuje **jinou reakci** (jiný model / vidět chybu z minula / zmenšit granuli) — a dostane **stejnou**: další pokus se stejným zadáním |
| **Jak se to pozná dnes** | **Nijak** — `runs.summary` je jen text `GitHub Actions: failure` (`index.ts:383`), takže **nula informace o příčině**. Rozdíl je vidět jen v logu běhu na GitHubu, který conductor nečte |
| **Naměřeno** | Rozpad v §10/Q2 a Q3; **55 % selhaných běhů skončilo do 30 s** |
| **Čím je to nové** | **S20** je „agent nevidí, co minule nevyšlo" (informace se ztrácí **mezi** pokusy). **S28** je „systém neumí rozlišit, co se stalo" (informace se ztrácí **uvnitř** jednoho selhání). Dohromady to znamená, že orchestra **opakuje totéž a neví proč** |
| **Co by to odhalilo** | Do `roadmap` (nebo do `runs.summary`) uložit **kategorii selhání** a podle ní rozhodovat: „nic nezměnil" 2× po sobě → granule patří člověku; parse chyba → do zadání přidat chybu z minula; testy → zmenšit granuli |

**Tři třídy, které se pletou dohromady (a nejsou to duplikáty):**

| Třída | Co se ztrácí | Kde |
|---|---|---|
| **S20** | **mezi** pokusy — agent nevidí chybu z minula | `agent.yml` (prompt) |
| **S28** | **uvnitř** selhání — stav nezná příčinu | `index.ts:394`, `:1338` |
| **S21** | **napříč** pokusy — strop se resetuje | `index.ts:638-647` |

#### S29 — Úkol je „hotový", ale práce není v `main`

**Tuhle třídu jsem našel až v dodatečném měření na konci (14:30–14:40 UTC)** —
a je to **naměřená živá vada dnešního dne**, ne odvození.

| | |
|---|---|
| **Kde** | `index.ts:368-377` (`pollRuns`) a `:609-612` — úloha se označí `done`, když **běh** skončí jako `success`. Ale `agent.yml:647-691` **není součástí běhu**: když auto-merge neproběhne, workflow **přesto skončí úspěšně** (krok `Sloučit` je podmíněný, ne povinný) |
| **Naměřeno** | `scripts/save.gd` a `scripts/hud.gd` **v `main` NEJSOU** (`git ls-files scripts` → 18 souborů, mezi nimi ani jeden z nich), a přesto: úlohy **#139** a **#140** jsou v D1 `done` a `roadmap` je vede jako `done` |
| **Proč se PR nesloučil** | PR #28 (+90 řádků) a #29 (+76) — granule `persist.save` a `ui.hud` **nemají `size_lines`**, takže `maxLinesOf()` vrátí **výchozích 60** (`index.ts:149-153`). Gate správně zamítl: `add + del > max_lines` (`agent.yml:646`) |
| **Jak to vypadá v PR** | `gh pr comment`: *„🤖 Automatické sloučení neproběhlo (pravidla: `ok=0`, CI: prázdné)"* — **jen komentář, žádná notifikace, žádný nenulový exit** |
| **Jak se to pozná dnes** | **Nijak.** `/health` je `ok: true`, `/queue` má úlohy `done`, `/failed` je prázdné. **Rozdíl mezi „PR sloučen" a „PR leží" není v žádném stavu conductoru** |
| **Navazující vada, kterou to způsobilo** | `engine.shell` (poslední granule, závisí na **všech 17**) čeká i na `save.gd` a `hud.gd`. Až se `engine.shell` vydá, **parsuje se bez nich** — projde, protože strom je konzistentní, ale **hra nebude mít ukládání ani HUD**, ačkoli plán je má jako hotové |
| **Čím je to nové** | S24 je „konec toku je slepá ulička, kterou nikdo nevidí" — **odvozeno z kódu**. **S29 je totéž naměřené**: stav `done` a stav `main` se **rozešly** a systém to nepozná. Není to o časování — je to **druhý zdroj pravdy o hotovém**, který se neporovnává |
| **Co by to odhalilo** | Po `success` běhu ověřit **`merged_at` na PR** a teprve pak `done`; když PR není sloučený, úloha patří do `failed` (nebo do nového stavu `cekana_na_cloveka`) a **musí to být notifikace** |

#### S30 — Granule, na kterou nikdo nepočká (a všichni na ni čekají)

| | |
|---|---|
| **Kde** | `index.ts:620-626` — granule je připravená, jen když `(i.depends_on || []).every((d) => done.has(...))`. Množina `done` se plní **jen** ze řádků D1 ve stavu `done` a z granulí s `done: true` v souboru (`:590-614`) |
| **Naměřeno** | **4 granule nemají řádek v D1 ani `done: true` v souboru**: `core.attributes`, `entity.item`, `sim.offline`, **`engine.shell`**. Dvě z nich (`core.attributes`, `entity.item`) **mají sloučené PR #19 a #20** — jenže jejich řádky v D1 **někdo smazal** (reset/úklid 30. 9.) |
| **Záchranná cesta** | `index.ts:502-503` páruje PR podle **titulku granule** — a dnes **obě zachytí** (`titulkyZachrana.has(...)` = true). **Ale jen dokud jsou v posledních 100 zavřených PR.** Dnes je v repu **27 zavřených PR celkem**, takže limit je daleko — u aktivnější hry by stačilo 100 PR a obě granule **přestanou existovat** |
| **Důsledek, kdyby záchrana selhala** | `entity.player`, `sim.combat`, `sim.crafting`, `sim.economy`, `entity.npc`, `entity.enemy`, `sim.assist`, `persist.save`, `ui.hud` a **`engine.shell`** — **15 závislostí** na `core.attributes` a `entity.item` by čekalo navěky. **A nikdo by se to nedozvěděl**, protože „čeká na závislosti" je legitimní stav |
| **Čím je to nové** | S16 je „stav, který se zapisuje a nikdo ho nečte". Tohle je **stav, který NEEXISTUJE** — a jeho nepřítomnost vypadá jako „ještě nezačal". Navíc: to, co drží DAG pohromadě, **není databáze, ale shoda titulků PR** |
| **Co by to odhalilo** | Invariant `lint-roadmapa.py` už existuje jako poznámka `[5]` („musí mít řádek v D1") — má se z něj stát **kontrola, která selže**, a `roadmapTick` má chybějící řádek u `done:true` granule **založit** (dělá to, ale jen než řádek někdo smaže) |

**Souhrn: 18 existujících + 12 nových = 30 tříd.** Zadání chtělo „přes 20" — splněno s tím, že dvanáct z nich je doloženo vlastním měřením, ne odvozením.
**Další číslo v řadě je tedy S31** — a to je věta, kterou má mít každý katalog.

---

## 5. Co je dobré a nemá se ztratit

*(Bez tohohle oddílu by návrh boural i to, co funguje. Všechno je naměřené.)*

1. **Uzamčený modelový řetězec.** `providers.json` v orchestra + **runtime fetch**
   z `raw.githubusercontent.com` (`pick-provider.mjs`) → oprava mrtvého modelu
   je **jedna změna** a vidí ji všechny hry. Naměřeno: kopie v šabloně i ve hře
   jsou **bajtově shodné** (4 644 B, `sha256 4b5caae0aa`). **Tohle je nejlepší
   architektonické rozhodnutí v projektu** a je hotové.
2. **Rotace modelů podle pokusu.** `attempt` posouvá pořadí poskytovatelů, takže
   druhý pokus nezkouší tentýž model. **Naměřeno v logu #243:** `pokus č. 3 –
   pořadí posunuto, aby se nezkoušel stejný model jako minule`. A **šetření
   kvótou**: když první pokus spadne na rate-limitu, druhý poskytovatel se
   **záměrně nezkouší** — zdůvodnění je v kódu a je správné.
3. **Brány, které opravdu měří.** `check-schema.py` (461 řádků, 17 offline testů
   s fixturami, ověřeno mutačně), `baseline.py` (646 řádků), `vision.mjs`
   (404 řádků, 3 volání modelu, cache, self-consistency). **Naměřeno:**
   `vision.mjs` je v obou kopiích **bajtově shodný** (`sha256 ce67762d…`).
   Když se v projektu něco povedlo, je to tohle.
4. **Tvrdá vs. poradní brána je pojmenované rozhodnutí.** `ci.yml:143-147`
   vysvětluje, **proč** vision neblokuje (chybovost modelu, falešný poplar je
   dražší). Není to opomenutí, je to volba s odůvodněním — a je v kódu.
5. **Idempotentní samomigrace schématu.** `index.ts:464-467` — `ALTER TABLE …
   ADD COLUMN` s polknutou chybou „duplicate column". Drží krok s během
   nasazení a nemá migrační nástroj. Pro tenhle rozsah správné řešení.
6. **Notifikace do tří kanálů s timeoutem** (`index.ts:79-140`) — ntfy má
   z Cloudflare často 429 (sdílené IP), Telegram/Discord to jistí. Když žádný
   kanál není, **není to tichý průchod** (kód to řeší).
7. **`git.cmd` s OpenSSL backendem** v `tools/`. Řeší reálnou vadu stanice
   (schannel) a je to **jediné místo**, kde je to potřeba.
8. **Konvence jako gates** — `CONVENTIONS.md` §1c–§1h (12,5 kB) je psaný
   **z naměřených chyb** (`ALIGN_LEFT`, `Member "position" redefined`,
   `class_name` stínění). Parse gate i statická kontrola `class_name` na to
   navazují. **Tohle je „znalost zapečená do šablony"** — přesně to, co má
   šablona dělat.
9. **`roadmapTick` čte roadmapu z repa, ne z databáze** (`index.ts:567-575`,
   přes GitHub contents API s base64 dekódováním kvůli diakritice). Soubor je
   zdroj, D1 je stav — rozdělení je správné (i když se dnes rozešlo, §6.4).
10. **Práce v malých kouscích s deklarovaným `owns`.** 18 granul, **0 kolizí**
    `owns` (měřeno dřív i teď), `depends_on` tvoří DAG. Metodika je dobrá;
    problém je v tom, že **kontrakt granule se nepředává dál** (S19).

---
---

# ČÁST II — Jak to má být

## 6. Architektura v devíti optikách

### O1 — Tok hodnoty: co orchestra vyrábí, pro koho a kde se tok zastaví

**Co vyrábí:** **sloučené PR v repu hry.** Nic jiného. (Ne hru — tu navrhuje
člověk; ne plán — ten píše ten, kdo hru navrhuje.)

**Kudy to teče:**

```
roadmap.json ──► D1.roadmap ──► D1.tasks ──► GitHub Actions ──► PR ──► merge ──► main
   (člověk)        (tick)         (dispatch)      (agent.yml)     (gate)   (GitHub)
                                                                              │
                                                                              ▼
                                                                    CI na main ──► Pages
```

**Kde se tok zastaví — naměřená časová osa jednoho průchodu (49,35 h):**

| Fáze | Naměřeno |
|---|---|
| čekání na první vydání granule | **3 h** (S12) — a to u každé granule |
| práce agenta | **medián 18 s** u selhaných, **75 s** u úspěšných běhů |
| čekání na další pokus (uvnitř úlohy) | **medián 3,2 min** |
| čekání po vyčerpání 5 pokusů | **3 h** (další vlna) |
| PR → merge | **medián 1,6 min** |

**Verdikt O1 (měřeno):** **z 49,35 h orchestra pracovala 6,86 h.** Devět desetin
času je čekání, a z toho **největší položka není práce modelu, ale tři hodiny
mezi „granule vznikla" a „granule se smí vydat"** — u granulí, které **nikdy
neselhaly**. To je čistá ztráta: chrání to proti něčemu, co se ještě nestalo.

**Kde je tok strukturálně přerušený (ne jen pomalý):**
**nikdo neměří, jestli se PR sloučil.** `pollRuns` čte stav PR **jen** když
`run.conclusion === 'success'` (`index.ts:368-377`), a `agent.yml` označí běh
za úspěšný i tehdy, když nechá PR k ruční kontrole (S24). Dnes jsou v repu hry
**2 otevřené PR** (Forge #139, #140) a **v D1 to není vidět jako nedokončená
práce** — úlohy jsou `done`.

### O2 — Zdroje pravdy a vlastnictví: kdo vlastní který soubor

**Naměřená mapa (27 souborů existuje v obou, 19 shodných, 8 rozdílných):**

| Soubor | Vlastník | Jak se to pozná | Stav |
|---|---|---|---|
| `conductor/src/index.ts`, `schema.sql`, `wrangler.toml` | **orchestra** | jen tam | shodné s nasazeným |
| `repo/.forge/*.py`, `*.mjs`, `providers.json`, `roadmap.json` | **šablona** (vzor) | kopíruje se | 19 shodných, 8 rozdílných |
| `.forge/roadmap.json` | **HRA** (výslovně) | `_popis` v souboru to říká | **rozešlé s D1** (§6.4) |
| `.forge/vision-profile.json` | **HRA** | šablona má `hra: null` | **jiný tvar klíčů** (`popis_stylu` vs. `styl_popis`) |
| `.forge/providers.json` | **orchestra** | fetch za běhu | shodné (ale kopie leží ve hře) |
| `.forge/node/.env` | **nikdo** | netrackovaný, kopíruje se | **S7/S26** |
| `scripts/`, `assets/`, `tests/` | **HRA** | nikde jinde nejsou | — |
| `.github/workflows/*` | **orchestra** (vzor) | kopíruje se | 4 soubory, **3 rozdílné** |
| `CONVENTIONS.md` | **orchestra** (vzor) | kopíruje se | shodné |

**Co se stane, když se kopie rozejdou — a pozná to někdo?**
**Naměřeno: pozná, ale jen u 12 z 27 souborů.** `kontrola-driftu.mjs` má ruční
seznam 12 cest. Mezi **nehlídanými** je `vision.test.mjs` (a rozešel se: šablona
17 576 B vs. hra 13 318 B), `vision-profile.json`, `roadmap.json`, `release.yml`
a `test-cooldown.py`. **Drift je dnes vlastnost, kterou nikdo neměří** —
a to je přímý důsledek toho, že **seznam vlastnictví je kód, ne data** (S5).

**Verdikt O2:** zdrojů pravdy je **sedm**, z toho **čtyři nemají deklaraci**
(roadmapa, profil vize, `.env`, seznam driftu). Rozdíl proti předchozí analýze
je v tom, že **rozpad není jen „dvě kopie téhož"** — je to **sedm různých
vztahů** (vlastní orchestra / vlastní hra / sdílí se fetchem / kopíruje se /
generuje se / je tajemství / je odvozený), a každý potřebuje jiné pravidlo.

### O3 — Smlouvy: jsou deklarované, nebo odvozené z konvence?

**Čtyři rozhraní, tři z nich odvozená z konvence:**

| Rozhraní | Kde je popsáno | Typ | Co se stane při porušení |
|---|---|---|---|
| **conductor ↔ agent** | `agent.yml` inputy (9), `payload` úlohy | **konvence** (jména bez schématu a verze) | drift kontrola porovná strukturu; `FORGE_ATTEMPT` přesunutý mezi kroky **přehlédla** (S8) |
| **granule ↔ granule** | `owns`, `depends_on` v roadmapě | **konvence** (`owns` se čte, `depends_on` se čte) | **vůbec nic** — model dostane soubory, ale ne rozhraní (S19) |
| **hra ↔ brány** | `spec.json`, `vision-profile.json`, cesty napevno v kódu bran | **konvence + konstanty v nástroji** (S4) | brána přestane měřit a hlásí zelenou (`check-wiring.py` nad jiným enginem) |
| **conductor ↔ hra** | `POST /game` (`game_id`, `repo`, `roadmap_file`) | **deklarované** (jediné, které je) | `listGames` fallback obejde registr a sáhne na `env.GITHUB_REPO` (S16/inv. 18) |

**Verdikt O3:** orchestra má **jedno deklarované rozhraní ze čtyř**. Zajímavé
je, že **to deklarované je právě to, které má fallback** — tedy i ta jedna
deklarace se dá obejít. A klíčová věta pro návrh: **`acceptance` a `provides`
jsou smlouvy, které neexistují jako kód** (S22) — plán je píše, protože
vypadají jako deklarace, ale nikdo je nečte.

### O4 — Hranice a vrstvy: kde je skutečný šev

**Naměřená odpověď na otázku „kde je šev" není tam, kde si projekt myslí.**

Projekt si myslí, že šev je **mezi orchestrou a hrou** (proto šablona,
proto `game_id`, proto registr her). Naměřeno ale:

- **27 souborů šablony je z 18 v `.forge/`** a **z toho 12 je vázaných na Godot**
  (`check-schema.py` 29 odkazů, `check-wiring.py` 9, `files-to-edit.mjs` 9,
  `verify-level-render.py` 5, `install-godot.sh` 19, `worker.mjs` 18,
  `agent.yml` 18). **Skutečný šev je uvnitř `.forge/`: mezi „co je orchestraci"
  a „co je Godot".**
- Naproti tomu **jádro orchestra (`index.ts`) je na enginu nezávislé** —
  naměřeno: v `index.ts` je **0 zmínek** o Godotu a 0 o konkrétní hře.
- A **hranice „hra vs. orchestra" vede skrz jednotlivé soubory**, ne mezi nimi:
  `check-assets.py` má **0 godot-vazeb** (je o obrázcích a zvuku),
  `vision.mjs` má **0** (je o obrázcích), `baseline.py` má **0** (je o hashech).
  Tři brány jsou tedy **přenosné beze změny** a tři ne.

**Verdikt O4:** šev **není** „orchestra × hra", ale **„orchestrace × engine"**,
a vede **dovnitř `.forge/`**: 3 brány jsou univerzální (`check-assets`,
`vision`, `baseline`), 3 jsou Godot-specifické (`check-schema`, `check-wiring`,
`verify-level-render`) a 2 jsou infrastruktura enginu (`install-godot.sh`,
`files-to-edit.mjs`). **To je jiná odpověď, než jak je dnes šablona poskládaná**
— a je to **ta, kterou má smysl zavést** (viz §7.2 a varianta B).

### O5 — Tichá selhání: jaký je jejich společný mechanisms

**Naměřeno (a je to jinde než v předchozí analýze):** tichá selhání orchestra
**nejsou jen v branách** — jsou ve **třech vrstvách** a mají **jeden vzorec**:

| Vrstva | Příklady | Co je spojuje |
|---|---|---|
| **Brána** | `check-wiring.py` nad 0 souborů, `check-assets.py` bez animace, `baseline.py` mimo repo | **prázdný vstup + kladný výsledek** |
| **Řízení** | S12 (cooldown), S19 (`continue` po chybě čtení), S24 (`ci=timeout` → komentář), `dispatchWorkflow` bez backoffu | **stav, který je zaměnitelný s jiným stavem** |
| **Data** | S22 (`acceptance`/`provides`), S25 (`schvalil: agent-init`), `roadmap` vs. soubor | **záznam, který nikdo nečte — nebo čte, ale neporovnává** |

**Společný mechanismus, pojmenovaný:** **stav nebo vstup, který nemá protějšek.**
Brána, která nemá fixturu (S3). Cooldown, který neumí rozeznat „vzniklo" od
„selhalo" (S12). Smlouva, kterou nečte žádný kód (S22). Schválení, které nemá
schvalovatele (S25). **Vždy chybí druhá strana, která by to ověřila.**

**A z toho plyne, co je dnes nejlepší obrana v projektu** (a má se rozšířit):
`test-check-schema.py` — **offline fixtura se známým správným i chybným
případem**. Je to jediná brána, u které je doloženo, že umí spadnout.
**Druhá je `test-zamek-owns.py`** — čte funkci ze zdroje a je ověřen mutačně.
A třetí, **nově**: `test-cooldown.py` v pracovním stromu (13:57 UTC) — čte
skutečný SQL a **je červený, protože našel vadu** (naměřeno: `10 kontrol,
1 chyb`, exit 1). **To je správný stav testu: má být červený, dokud je vada.**

### O6 — Testovatelnost jako vlastnost

**Co je dnes ověřitelné offline (naměřeno spuštěním nebo z kódu):**

| Co | Jak | Stav |
|---|---|---|
| rozhodovací logika conductora | **SQL ze zdroje** v SQLite (`hl-sql.py`, `test-cooldown.py`) | **jde to** — a je to nejlepší dostupná úroveň |
| plán (DAG) | `lint-roadmapa.py`, `simulace-dag.py`, `stav-dag.py` | staticky, bez provozu |
| brány (`check-schema`) | `test-check-schema.py` 17/17 s fixturami | **jde to** |
| vision | `vision.test.mjs` 36/36 (šablona) | jde, **ale neměřil jsem** (sandbox) |
| **`agent.yml`** | **nic** | **neexistuje test** (S8) |
| **auto-merge gate** | **nic** — jen lidské čtení | **neexistuje test** |
| **dispatch smyčka** (co se vydá a co ne) | jde přes SQL ze zdroje | jde (dělám to v `hl-sql.py`) |
| **conductor jako celek** (`/tick`, `/report`) | `mock-conductor.mjs` **neumí** `/tick`, `/poll`, `/roadmap`, `/tasks/cleanup` | **neexistuje** |

**Kde je test jen opsaná logika (a tedy nic nechytí):**
`tools/test-eskalace.py` — `watchdog()` je **kopie** logiky a `PRAH = 8` je
natvrdo místo čtení `ESCALATE_AFTER` ze zdroje. (Už to není vada „lže zelenou"
— exit kód má, jak naměřila jiná session; je to **vada „měří jinou pravdu"**.)

**Jaká rozhodovací logika by měla být testovatelná a není** — tři věci,
a všechny tři jsou v `index.ts` a dají se testovat **stejným vzorem jako SQL**
(tedy vytáhnout ze zdroje a spustit):
1. **co se vydá** (guard + pořadí + `LIMIT 25` + `MAX_CONCURRENT`) — dělám v `hl-sql.py`, patří to do `tools/`
2. **co se stane po selhání** (`nextStatus` + zápis roadmapy) — dělá `test-cooldown.py` (nová verze)
3. **co se stane po úspěchu** (`mergedTasks`, párování PR podle **názvu**) — **netestuje nic** a je to nejkřehčí místo: `mergedTitlesByRepo` páruje PR podle **titulku granule** (`index.ts:502-503`), takže **dvě granule se stejným titulkem = falešné „hotovo"**.

### O7 — Ekonomie změny: kolik souborů se musí změnit

*(Měřeno `hl-cena.py` + `git ls-files`; druhý sloupec je **konkrétní naměřený
počet**, ne odhad.)*

| Změna | Kolik souborů | Jak to vzniklo | Roste s počtem her? |
|---|---|---|---|
| **Přidat hru** | **≥ 27** (kopie šablony) + roadmapa + `vision-profile.json` + 5 tajemství + registrace | naměřeno simulací instalace | **ANO** — každá hra má vlastní kopii 27 souborů a vlastní sadu tajemství |
| **Změnit limity** (PR, pokusy, souběh) | **1** (`wrangler.toml`) — ale **globálně pro všechny hry** | kód | **NE, a to je vada** (S11) |
| **Přidat bránu** | **1 soubor** + řádek v `ci.yml` **v každé hře** | `kód` | **ANO** — N her = N změn |
| **Přidat poskytovatele LLM** | **1** (`providers.json`) + **secret v každém repu** | kód + invariant 3 | **ANO** (klíče jsou per-repo) |
| **Změnit logiku výběru modelu** | `pick-provider.mjs` **v každé hře** (kopie) | naměřeno: 27 souborů v obou, `pick-provider.mjs` shodný | **ANO** |
| **Vyměnit engine** | **≥ 5** v `.forge/` (check-schema, check-wiring, verify-level-render, install-godot.sh, files-to-edit) + 3 kroky v `agent.yml` + `ci.yml` + `release.yml` | naměřeno: 12 souborů s godot-vazbami | **ANO**, ale jen jednou za engine |
| **Změnit rozhodování conductora** | **1** (`index.ts`) | `kód` | **NE** — jádro je společné |

**Verdikt O7:** cena **roste s počtem her u šesti změn ze sedmi**. Jediné, co
je společné a neroste, je **jádro (conductor)** — a to je zároveň ta část,
která je dnes **nejhůř testovatelná** (O6). To je nepříjemná kombinace:
**co je společné, je netestované; co je testované, je v N kopiích.**

### O8 — Provoz a lidé: co dělá člověk ručně a jak vypadá 3:00 ráno

**Naměřený provoz (13:43–13:50 UTC):**

```
conductor: ok:true, ready:4, running:0, games:1
uzly:      oracle-frankfurt (naposledy před 1 min) · pc-domaci (2500 min = 41,7 h)
běhy:      poslední agent.yml 13:11 UTC; další možné 16:10 (cooldown)
```

**Co dělá člověk ručně (naměřeno nebo z kódu):**

| Úkon | Jak často | Dá se zautomatizovat? |
|---|---|---|
| **Odpovědět na O1–O10** | jednorázově | ne — je to rozhodnutí |
| **Sloučit PR, který neprošel gate** | u každého takového PR | **částečně** — dnes to nikdo nevidí (S24) |
| **Přepsat `release.yml` v nové hře** (`NAZEV-REPA`) | jednou na hru | **ano** — a v pracovním stromu už je hotové (D1) |
| **Nastavit 8 tajemství v novém repu** | jednou na hru | ano (API), dnes ručně |
| **Zadat granule do `roadmap.json`** | průběžně | **ne, a je to správně** — plán patří člověku |
| **`POST /tasks/cleanup`** po změně ID granulí | výjimečně | ano (mělo by být v tiku) |
| **Zapnout Pages v novém repu** | jednou na hru | ne (GitHub to nedovolí bez kliknutí) |
| **Odpovědět `y` na `shell:` v domácím uzlu** | u každého takového kroku | **ne, a je to správně** — je to pojistka |

**Jak vypadá 3:00 ráno (naměřeno nepřímo — z rozložení běhů):**
orchestra **přes noc nepracuje souvisle**; v naměřeném okně byly tři noční
bloky (29. 9. 18:19; 30. 9. 05:45; 1. 10. 01:31) a mezi nimi **11,2 h a 8,5 h
ticha**. **Nikdo není u toho a nikdo to nepozná** — protože:
- notifikace chodí do Telegramu, ale **jen o událostech, které conductor vidí**;
- `ci=timeout` a „PR čeká na člověka" **notifikaci nemá** (S24);
- domácí uzel **je 41,7 h offline** a nikdo to neřeší, protože `pc-domaci`
  **není potřeba** (kinds `assets,test,build` — a `oracle-frankfurt` je taky
  pull-worker a taky skoro nic nedělá: `jobs_done: 1`).

**Verdikt O8:** provoz je **jednoosobový a funguje díky tomu, že je člověk
u toho**. Není to vada — je to vlastnost projektu v tomhle stadiu. Co je vada:
**tři stavy, které vyžadují člověka, nemají notifikaci** (PR čeká na merge,
`ci=timeout`, granule přes strop). To je jediná věc, kterou má smysl doplnit.

### O9 — Druhá hra jako test návrhu: co dnešní kód rozbije

**Tohle není odklad, je to zadání pro návrh.** Naměřeno, co praskne (v pořadí,
v jakém to přijde):

| # | Co praskne | Doklad | Důsledek |
|---|---|---|---|
| 1 | **Nová hra z šablony nemá co měřit** | 12 odkazů na neexistující soubory (simulace) | CI spadne na `check-schema.py` (chybí `spec.json`) — a **nikdo nepozná, že to není vada hry** |
| 2 | **`install-into-repo.ps1` nefunguje** | `projects/` neexistuje, `forge.cmd` smazaný | hru založí jen ruční kopie |
| 3 | **Limity jsou globální** | `wrangler.toml`, S11 | hra A drží `ROADMAP_MAX_PRS=5`, hra B se **nevydá** — a vypadá to jako „B nemá práci" |
| 4 | **Fallback `listGames`** | `index.ts:447-454` | když registr selže, conductor dispatchuje na `GITHUB_REPO` — **tedy na hru A**, i když úloha patří hře B |
| 5 | **Staré řádky `roadmap` bez `game_id`** | invariant 2 + naměřeno (4 granule jen v souboru) | po registraci druhé hry zůstanou staré řádky a dispatchují mrtvé granule |
| 6 | **Titulky granul jsou klíč** | `index.ts:502-503` | dvě hry se **stejným titulem** granule → falešné „hotovo" |
| 7 | **`owns` klíče jsou scoped na repo** | `lockKeys` `${repo}/${f}` | tohle je **správně** — jediná věc, která je na víc her připravená |
| 8 | **Tajemství: 8 na repo, 5 z toho LLM** | invariant 3 | druhá hra **nezdvojnásobí kvótu** (denní limit je per klíč) — pokud nemá vlastní klíče |

**Verdikt O9:** **pět z osmi věcí praskne hned první den** (1, 2, 3, 4, 5)
a **jedna praskne tiše** (4 — práce na špatné hře). Tři z nich jsou **přesně ty,
které má řešit kontrakt** (§7): co má hra deklarovat (1), kdo co vlastní (5)
a jak se pozná hra v úloze (4).

**A jedna věc, která NEPRASKNE, i když by se čekalo:** `MAX_CONCURRENT=5`
a zámek `owns` (opravený 1. 10.) jsou na víc her připravené správně — klíč
zámku je `{repo}/{soubor}`. **Tedy: co je v orchestra napsané jako klíč, je
v pořádku; co je napsané jako konstanta, je globální omyl.**

---

## 7. Návrh kontraktů

**Princip, ze kterého návrh vychází (a je naměřený):** v orchestra **funguje
všechno, co je klíč** (`{repo}/{soubor}`, `{game_id}/{grain_id}`) a **rozpadá se
všechno, co je konstanta** (`RETRY_HOURS` na jednom místě pro všechny, `GITHUB_REPO`
jako fallback, cesty napevno v branách). **Kontrakt je způsob, jak z konstanty
udělat data.**

### 7.1 Tři deklarace, které dnes chybí (a nic víc)

Návrh **záměrně nepřidává víc než tři soubory.** Každý řeší jednu naměřenou
třídu selhání a každý se dá odmítnout zvlášť.

#### (a) `zdroj.json` — „jsem hra a tady je moje konfigurace"

**Kdo ho vlastní:** **hra** (nikdy ho nepřepíše šablona).
**Kde leží:** `.forge/zdroj.json` v repu hry.
**Co řeší:** S23 (šablona nemá bootstrap), O9/1 a O9/5 (co má hra deklarovat),
O6 (které soubory patří hře — dnes nerozhodnuto).

```json
{
  "verze": 1,
  "hra": "uo-shadows",
  "repo": "ssevcikm-spec/uo-shadows",
  "engine": { "nazev": "godot", "verze": "4.7.2" },
  "sablona": { "repo": "ssevcikm-spec/forge-orchestra", "commit": "525d45b" },
  "vlastni": [
    "scripts/**", "assets/**", "tests/**", "project.godot",
    ".forge/roadmap.json", ".forge/vision-profile.json",
    ".forge/vision/baseline.json"
  ],
  "prevzato": [
    ".forge/check-assets.py", ".forge/vision.mjs", ".forge/baseline.py",
    ".forge/pick-provider.mjs", ".forge/files-to-edit.mjs",
    ".github/workflows/*.yml", "CONVENTIONS.md"
  ],
  "brany": {
    "schema":  { "skript": ".forge/check-schema.py",       "vstup": "assets/spec.json" },
    "assety":  { "skript": ".forge/check-assets.py",       "vstup": "assets/spec.json" },
    "wiring":  { "skript": ".forge/check-wiring.py",       "vzor": "scripts/*.gd" },
    "render":  { "skript": ".forge/verify-level-render.py","vstup": "assets/levels/main.json" }
  }
}
```

**Co to mění konkrétně:**
- `check-wiring.py:73` přestane mít `scripts/*.gd` napevno (S4) — vezme `vzor`.
- `baseline.py:60` (`SLEDOVANE`) přestane mít dvě cesty napevno.
- `verify-level-render.py:209,251` přestane hádat `../spec.json`.
- **Drift kontrola dostane seznam z `prevzato`** — místo ručních 12 cest (S5).
  **Tím se `kontrola-driftu.mjs` sám stane tím, čím dnes není: úplným.**
- Nová hra **ví, co má dodat** — a onboarding test (D3) má co kontrolovat.

#### (b) `prepisy.json` — „kdo je zdroj a kterým směrem se kopíruje"

**Kdo ho vlastní:** **orchestra.** **Kde leží:** `orchestra/prepisy.json`.
**Co řeší:** S5 (tři nerozcházející se seznamy), O2 (sedm vztahů vlastnictví),
O7 (cena změny).

```json
{
  "verze": 1,
  "soubory": [
    { "cesta": ".forge/check-assets.py",   "smer": "orchestra->hra", "sync": true },
    { "cesta": ".forge/vision.mjs",        "smer": "orchestra->hra", "sync": true },
    { "cesta": ".forge/pick-provider.mjs", "smer": "orchestra->hra", "sync": true },
    { "cesta": ".forge/providers.json",    "smer": "orchestra",      "sync": false,
      "duvod": "hra ho stahuje za běhu; lokální kopie je jen záloha" },
    { "cesta": ".forge/roadmap.json",      "smer": "hra",            "sync": false,
      "duvod": "plán patří hře, orchestra ho jen čte" },
    { "cesta": ".forge/vision-profile.json","smer": "hra",           "sync": false,
      "duvod": "chování kontroly pro konkrétní hru" },
    { "cesta": ".forge/node/.env",         "smer": "nikdo",          "sync": false,
      "duvod": "tajemství – negeneruje se, nekopíruje se, nastavuje ručně" }
  ]
}
```

**Co to mění:** dnes mají **tři nástroje tři různé seznamy**
(`kontrola-driftu.mjs` 12 cest, `sync-sablona-hra.py` 2 soubory s **různými
směry**, `sjednot-sablonu.py` textové náhrady). Po zavedení čtou **jeden**.

#### (c) Kontrakt granule v `owns` — „čím se granule prokazuje"

**Kdo ho vlastní:** **hra** (v `roadmap.json`). **Co řeší:** S19 (model dostane
soubory, ne smlouvy) a S22 (`acceptance`/`provides` nikdo nečte).

**Návrh: nezavádět nový soubor.** Místo toho **z `owns` udělat deklaraci
rozhraní** — protože `owns` **už je** seznam souborů a `files-to-edit.mjs` ho
**už čte**:

```json
{
  "id": "sim.mining",
  "owns":     ["scripts/mining.gd"],
  "poskytuje": { "scripts/mining.gd": ["gather(node) -> int"] },
  "vyzaduje":  { "scripts/skills.gd":   ["add(skill: String, kolik: int) -> void"],
                 "scripts/world.gd":    ["gather(cell) -> void"] },
  "acceptance": ["tests", "wiring"]
}
```

**Tři konkrétní důsledky (a každý se dá ověřit):**
1. **`files-to-edit.mjs` dá modelu `--read` i to, co granule `vyzaduje`** —
   dnes čte **jen `owns` přímých závislostí** a **vynechává 2. úroveň**
   (naměřeno: `sim.mining` nevidí `level.gd`, `entity.enemy` nevidí
   `attributes.gd` ani `skills.gd`).
2. **`acceptance` se začne čítat**: jména `tests | wiring | assets | render | schema`
   se mapují na kroky `ci.yml`. Když granule deklaruje `render` a kontrola
   neproběhne, **je to nález** — dnes je to ticho.
3. **`provides` se dá ověřit staticky** (`check-wiring.py` umí hledat funkci;
   deklarovaná funkce, která v souboru není, je vada **před** během agenta).

**Co tenhle návrh NEDĚLÁ:** nezavádí typový systém ani DSL. Deklarace jsou
**řetězce**, které se porovnávají s kódem — nic víc. (Kdyby to mělo být víc,
byl by to jazyk, a ten nemá kdo udržovat.)

### 7.2 Co s vrstvami (odpověď na O4)

Z O4 plyne, že šev je **uvnitř `.forge/`**. Návrh je **rozdělit `.forge/` na dvě
části podle toho, co obsahují** — ale **jen kdyby se to vyplatilo** (viz §8,
varianta B). Formálně:

```
.forge/
  core/            # nezávislé na enginu i hře (3 soubory, 0 godot-vazeb)
    check-assets.py     (305 ř., 0 vazeb)
    vision.mjs          (404 ř., 0 vazeb)
    baseline.py         (646 ř., 0 vazeb)
  engine/godot/    # 3 brány + infrastruktura enginu (12 souborů s vazbami)
    check-schema.py     (461 ř., 29 vazeb)
    check-wiring.py     (174 ř.,  9 vazeb)
    verify-level-render.py (313 ř., 5 vazeb)
    install-godot.sh    (19 vazeb)
    files-to-edit.mjs   (103 ř.,  9 vazeb)
  hra/             # vlastní hra: zdroj.json, roadmap.json, vision-profile.json
```

**Pozor — tenhle krok je drahý** (mění cesty ve všech workflowech a všech
branách v N hrách) a **dnes má jednoho konzumenta**. Proto patří do varianty B,
ne do „hned". **Naměřený argument pro:** výměna enginu by pak byla **změna
adresáře**, ne 5 souborů + 3 kroky.

### 7.3 Čím se kontrakt šíří (směry)

```
orchestra ──(prepisy.json: smer=orchestra->hra)──► hra
    ▲                                              │
    │ (POST /game: registrace; zdroj.json)         │
    └──────────────────────────────────────────────┘
                        │
                        ▼
              conductor čte roadmapu hry (soubor je zdroj)
                        │
                        ▼
              dispatch nese KONTRAKT granule v payloadu
              (owns + vyzaduje + poskytuje + acceptance)
                        │
                        ▼
              agent.yml předá modelu soubory I smlouvy
                        │
                        ▼
              brány ověří, co granule deklarovala (acceptance)
```

**Jedna věta:** **deklarace jdou od hry k orchestraci; nikdy zpátky.**
Orchestra **nikdy nepíše** do souborů, které vlastní hra — dnes to platí
(`install-into-repo.ps1` kopíruje jen `.forge` a `.github`), a je to vlastnost,
která se musí udržet.

### 7.4 Jak vypadá manifest šablony

Dnešní šablona **manifest nemá** — je to jen adresář. **Co by měla mít
(a co je nejmenší užitečná verze):**

```json
{
  "verze": 1,
  "nazev": "forge-orchestra/repo",
  "pro_hru": { "povinne": ["project.godot", "assets/spec.json"],
               "volitelne": ["assets/levels/main.json", "tests/run_tests.gd"] },
  "dodava": {
    ".forge/check-assets.py":  { "vlastni": "orchestra" },
    ".forge/vision.mjs":       { "vlastni": "orchestra" },
    ".forge/roadmap.json":     { "vlastni": "hra", "pocatecni": "prazdny" },
    ".forge/vision-profile.json": { "vlastni": "hra", "pocatecni": "obecny" },
    ".forge/node/.env":        { "vlastni": "nikdo", "generuje": false }
  },
  "po_instalaci": [
    "nahradit NAZEV-REPA v .github/workflows/release.yml",
    "nastavit 5 klíčů LLM + FORGE_PAT + FORGE_WEBHOOK_SECRET + FORGE_CONDUCTOR_URL",
    "zapnout Pages (Settings → Pages → Source: GitHub Actions)",
    "zaregistrovat hru: POST /game"
  ]
}
```

**Klíčová vlastnost:** `pro_hru.povinne` je **kontrakt, který se dá otestovat**
— onboarding test (D3) ověří, že je hra dodala, **než** se pustí brány.
Tím zmizí dnešní stav, kdy brány měří soubory, které v novém repu nejsou (S23).

**A vlastnost, která se nesmí ztratit** (dnešní `_popis` v `roadmap.json` je
správný nápad): **manifest má obsahovat vysvětlení u každého klíče.** Formát
`_popis` (dokumentace jako pole řetězců v témže JSON) je **dobrý vynález** —
funguje bez dalšího souboru a nedá se od něj odpojit.

---

## 8. Dvě varianty dalšího vývoje

**Obě jsou míněny vážně a obě mají cenu, riziko a to, co NEDĚLAJÍ.**
Rozhodnutí mezi nimi je o tom, **čemu věříš víc**: jestli tomu, že orchestra
má být **jedna hra, kterou je potřeba dotáhnout**, nebo **systém, který unese
druhou**.

### Varianta A — „Dotáhnout jednu hru" (levná, rychlá, neriskuje nic)

**Co se udělá:**

| # | Krok | Cena | Řeší |
|---|---|---|---|
| A1 | **Guard: `naposledy_selhalo` místo `updated_at`** | ~30 řádků + `ALTER TABLE`, 1 deploy | S12, **Q1** — 82,7 % nečinnosti |
| A2 | **`/report` zapíše roadmapu** (jako `pollRuns`) | ~5 řádků | S13 |
| A3 | **Strop a watchdog na `item_id` granule** | ~30 řádků | S14, S21 |
| A4 | **Notifikace na tři stavy, které dnes nikdo nevidí** (PR čeká na merge, `ci=timeout`, granule přes strop) | ~20 řádků | S24, O8 |
| A5 | **`acceptance` a `provides` buď číst, nebo smazat** | minuty | S22 (rozhodnutí, ne kód) |
| A6 | **Do promptu 2. pokusu dát konkrétní chybu z minula** (`log_tail`) | ~10 řádků v `agent.yml` | S20, **Q2** — 95 běhů „nic nezměnil" |
| A7 | **`--read` i pro smlouvy 2. úrovně** (`files-to-edit.mjs`) | ~20 řádků | S19 — 27 parse chyb |
| A8 | **Vyřešit rozchod `roadmap.json` vs. D1** (doplnit `done: true` tam, kde D1 ví o mergi) | minuty, ručně | Q10 |

**Cena:** **1–2 dny práce**, z toho **jeden deploy conductora** (A1–A4, A6–A7).
**Riziko:** **nízké až střední** — A1 mění dispatch (nasazovat po jednom kroku),
ostatní jsou aditivní. **Nic z toho nemění tvar systému.**
**Co to přinese (odhad z naměřených čísel):** kdyby A1 odstranil 3h čekání
u nových granulí a A6+A7 snížily podíl „nic nezměnil" a parse chyb na polovinu,
**využití by šlo z 13,9 % řádově na desítky procent** — a to je **měřitelná
podmínka**, ne dojem (viz „jak poznám, že to selhalo" níže).
**Co to NEDĚLÁ:** nezavádí `zdroj.json`, `prepisy.json` ani kontrakt granule;
**druhá hra zůstane nemožná** (O9/1, O9/2 neřešeno) a drift zůstane ruční.

### Varianta B — „Kontrakt a druhá hra" (dražší, ale řeší třídu)

**Co se udělá:** **A1–A8** (bez nich nemá smysl nic dalšího) **plus**:

| # | Krok | Cena | Řeší |
|---|---|---|---|
| B1 | **`zdroj.json`** + brány ho čtou (4 brány, 4 cesty napevno) | **2–3 dny** (mění se kód bran ve dvou kopiích) | S4, S23, O2, O9/1 |
| B2 | **`prepisy.json`** + drift/sync/sjednocení čtou jeden seznam | **1 den** | S5, O2, O7 |
| B3 | **Kontrakt granule** (`poskytuje`/`vyzaduje` + `acceptance` se čte) | **1–2 dny** | S19, S22, **Q7** |
| B4 | **Limity per `game_id`** (tabulka `games`: `max_prs`, `max_concurrent`, `retry_hours`) | **1 den** | S11, O9/3 |
| B5 | **Zrušit `listGames` fallback** (radši nemakat než makat na špatné hře) | hodiny | O9/4 |
| B6 | **Rozdělit `.forge/` na `core/` a `engine/<x>/`** | **2–3 dny** (cesty ve všech workflowech) | O4 |
| B7 | **Onboarding jako test** (založí hru z manifestu a pustí brány) | **1 den** | S23, O9/2 |

**Cena:** **8–12 dní**, z toho **čtyři až pět deployů conductora**, a **změny
v herním repu** (B1–B3 se musí propsat do hry, jinak tam zůstane stará verze).
**Riziko:** **vysoké** — B1 a B6 mění **cesty** ve všech branách a workflowech
najednou; chyba v tom se projeví jako „brána tiše neměří" (tedy **přesně ta
třída, kterou se snažíme odstranit**).
**Co to přinese:** druhá hra bude **měřitelná položka**, ne projekt.
Kontrolní podmínka z plánu (F5.4) zní: *„Když přidání druhé hry bude znamenat
víc než 5 změněných souborů, kontrakt nestačil."*
**Co to NEDĚLÁ:** **nezavádí plugin systém, registr enginů ani DSL.**
`core/` + `engine/<x>/` **není platforma** — jsou to dva adresáře. A **nezavádí
typový systém** do roadmapy (kontrakt jsou řetězce).

### Jak poznám, že varianta selhala (měřitelné, ne dojem)

| Varianta | Podmínka selhání |
|---|---|
| **A** | Do **7 dnů** po nasazení A1–A7 **nestoupne využití** (běhy ∪ / 168 h) **nad 25 %**, nebo **neklesne** podíl selhání do 30 s pod **30 %**. Obojí se měří `hl-vytizeni.mjs` a `hl-priciny.mjs` — tedy **týmž skriptem, kterým jsem měřil teď** |
| **A** | **A1 nezavede regresi**: po nasazení se objeví granule vydaná **před** uplynutím cooldownu po selhání (kontrola: `test-cooldown.py` musí zůstat zelený) |
| **B** | **Přidání druhé hry znamená víc než 5 změněných souborů** (kritérium plánu F5.4) |
| **B** | **B1 zavede tichou vadu**: některá brána po zavedení `zdroj.json` **přestane měřit** — pozná se to tak, že `validate-all.mjs` projde, ale brána **nevypíše počet změřených souborů**. Proto musí B1 obsahovat **řádek `ZMERENO:`** v každé bráně (návrh F2.1 z plánu) |
| **obě** | Kdyby se ukázalo, že **není potřeba** — tedy že hra je hotová a orchestra se vypne. To je legitimní výsledek a je levnější než B |

### Co je dnes zdarma a za měsíc drahé (rozhodující kritérium)

| Co | Dnes | Za měsíc |
|---|---|---|
| **A1 (guard)** | 30 řádků, jeden deploy, žádná migrace dat | **totéž** — ale každý den zpoždění stojí ~3 h na granuli |
| **A5 (`acceptance` číst/smazat)** | rozhodnutí, 0 řádků | **drahé** — až se podle `acceptance` začne plánovat, vznikne N granulí s poli, která nic neříkají |
| **A8 (rozchod roadmapy)** | minuty, dokud je granul 18 | **drahé** — po `/roadmap/reset` se 8 hotových granulí vydá znovu |
| **B1 (`zdroj.json`)** | 4 brány, 1 hra | **drahé lineárně** — každá další hra je další kopie bez kontraktu |
| **B6 (`core/`)** | 1 engine | **drahé skokem** — s druhým enginem se rozdělení dělá **přes N her** |
| **S26 (secret)** | nic (nikdo ho nemá) | **totéž** — ale jednou uniklý secret nejde vzít zpět |

---

## 9. Co NEDĚLAT (vědomě odložené a proč)

**Tenhle oddíl je stejně důležitý jako návrh.** Je odpovědí na napětí
„univerzalita vs. jednoduchost" ze zadání §4.2: **kolik konzumentů má ta
abstrakce DNES?**

| Co se NEDĚLÁ | Proč | Co by to pokazilo |
|---|---|---|
| **Platforma / plugin systém pro enginy** | **1 konzument dnes.** Abstrakce pro jednoho je náklad bez užitku — a plán to má správně až ve F5 s druhou hrou | Vznikne vrstva, které nikdo nerozumí, a brány v ní přestanou měřit (což je **naměřený** způsob, jakým tahle orchestra selhává) |
| **Registr bran** („brána se zaregistruje") | **12 bran, 1 hra.** Přidání brány je dnes **1 soubor + 1 řádek** — registr by to nezkrátil, jen přesunul | Další místo, kde se dá zapomenout — a `check-wiring.py` dokazuje, že zapomenutá brána hlásí zelenou |
| **DSL pro roadmapu** | Formát je **JSON s `_popis`** a funguje. Každé DSL je nový jazyk k údržbě | Ztráta toho, co je dnes nejlepší: **plán se dá přečíst očima a upravit v editoru** |
| **Typový systém v kontraktu granule** | Kontrakt jako **řetězce** stačí na to, co je naměřené (S19: model potřebuje vidět soubor a jméno funkce) | Údržba signatur v YAML — a nikdo je nebude aktualizovat |
| **Vlastní runner místo GitHub Actions** | Actions jsou zdarma pro veřejná repa — to je **podmínka existence projektu** | Náklady a bezpečnost (self-hosted runner na veřejném repu je známé riziko; kód to má vyřešené pull-workerem) |
| **Monorepo pro hry** | **Herní repa musí být samostatná** (kvůli Actions zdarma) | Ztráta Pages a bezplatných minut |
| **Vlastní vision model / lokální GPU v CI** | `vision.mjs` s Gemini/DeepSeek **funguje** a je neblokující. Lokální GPU v runneru není | Nahrazení fungující věci | 
| **Mazat `vision.mjs`, `baseline.py`, `check-assets.py`** | **Neblokují, ale měří.** Jsou to 3 brány s vlastními testy | Smazala by se **jediná část projektu, u které je doloženo, že umí spadnout** |
| **Mazat `forge-quest`** | **Živá hra s vlastními Pages** (`AGENTS.md`) | — |
| **Přidávat abstrakci pro druhý engine TEĎ** | Uzly (B6) ano, ale **jen až po rozhodnutí o druhé hře** | Předčasná abstrakce — viz první řádek |
| **Opravovat `test-eskalace.py` hned** | **Není to vada „lže zelenou"** (má `sys.exit`, naměřeno jinou session) — je to „měří opsanou pravdu". Až bude B3 | Práce na testu, který nikoho neblokuje |
| **Vracet `acceptance` do kódu, dokud není rozhodnuto, co znamená** | Dnes je to **past** (S22). Nejdřív rozhodnutí, pak kód | Kód, který měří něco jiného, než plán myslel |

---
---

# ČÁST III — Poctivost

## 10. Deset otázek ze zadání §6 — odpovězeno na devět

**Zadání žádalo aspoň pět.** Odpovídám na devět; u desáté (Q8) píšu, proč
odpovědět nejde měřením.

### Q1 — Kolik z celkového času orchestra skutečně pracuje?

**měřeno `node _analyza\hl-vytizeni.mjs` (GitHub API, všech 247 běhů `agent.yml`).**

```
okno:    2026-09-29 11:53:01 .. 2026-10-01 13:13:51  = 49,35 h
běželo:  6,86 h = 13,89 %
nečinnost: 40,79 h = 82,7 % v osmi oknech (2,04 · 11,20 · 5,83 · 1,39 · 6,00 · 2,85 · 8,50 · 2,98 h)
```

**A klíčové zjištění:** **cílové CI bylo během všech osmi oken ZELENÉ**
(u jednoho okna proběhlo 3× a jednou selhalo). **Není to tedy následek
červeného CI** — a to je odpověď, která **mění výklad** dřívějšího nálezu
S18: ten popisoval **jedno** okno a byl pravdivý; ale „orchestra je pomalá,
protože má hra červené CI" **neplatí obecně**.

**Co ji blokuje (naměřeno jinde):** guard se ptá na `roadmap.updated_at`
(`index.ts:810`) a ten se zapisuje **při vzniku** řádku — nová granule tedy
čeká `RETRY_HOURS = 3` (`wrangler.toml:49`), i když nikdy neselhala (S12,
dokázáno SQL v §4). **Živý důkaz:** `entity.enemy` — úloha založena
**10:09:14**, první běh **13:10:09** (o 3 h 1 min později).

### Q2 — Jaký je poměr úspěšných granulí k vydaným?

**měřeno `hl-priciny.mjs` (247 běhů), `hl-roadmap-srovnani.mjs` (D1), GitHub API.**

| Veličina | Hodnota | Odkud |
|---|---|---|
| běhů `agent.yml` celkem | **247** | `/actions/workflows/agent.yml/runs` → `total_count` |
| úspěšných běhů | **28 (11,3 %)** | `conclusion` |
| úloh (task) v bězích | **79** | z názvu běhu `Forge #<task>` |
| **úspěšných úloh** | **~28** (každá úspěšná úloha = ≥1 úspěšný běh) | odvozeno |
| **PR sloučených** | **24** (z 28 forge PR, 86 %) | `/pulls?state=all` |
| **granulí hotových podle D1** | **10 ze 14** | `GET /roadmap` |
| granulí v souboru | 18 (2 s `done:true`) | `roadmap.json` |

**Odpověď:** **jedna úspěšná granule stojí ~9 běhů** (247 ÷ 28) a **~6,4 úlohy**
(180 ÷ 28 — počítáno z 247−67 no-change… *přesněji:* úspěch přichází u úlohy,
která má v průměru 3,13 běhu, a úspěšných úloh je 28 ze 79 = **35 %**).
**Rozhodující pro plánování:** **rozptyl je obrovský** — 20 úloh uspělo na
**první** běh, ale 3 úlohy potřebovaly **devět** běhů. **Průměr tady nic
neříká; rozhoduje ocas.**

**Co z toho plyne pro „zvyšovat počet pokusů, nebo zmenšit granule":**
**zmenšit granule** — protože **55 % selhaných běhů skončilo do 30 sekund**
(měřeno) a **95 běhů agent nic nezměnil**. To nejsou neúspěšné pokusy
o velkou práci; to jsou pokusy, které **ani nezačaly**. Větší počet pokusů
u téhož zadání problém neřeší (**S20**: agent mezi pokusy nevidí, co minule
nevyšlo).

### Q3 — Kde orchestra tráví nejvíc volání modelu?

**měřeno `hl-modely.mjs` (logy běhů) + `hl-priciny.mjs`.**

- **Jedno volání modelu na běh** — v logu jednoho běhu je jediné
  `Tokens: 7.4k sent, 919 received` (což je ~8,3 k tokenů, 1 volání).
- **Rychlé selhání volání neudělá:** agent se pouští **až po** instalaci aideru
  a výběru poskytovatele; **55 % selhaných běhů** ale stráví v kroku agenta
  **méně než 30 s**, takže **volání proběhne, ale nevyprodukuje změnu**.
- **Druhý poskytovatel se záměrně nezkouší**, když log obsahuje rate-limit
  (`agent.yml`: `grep -qE 'RateLimitError|rate limit reached|exceeded your current quota'`).
  Naměřeno v logu #243: `radků s 429/quota: 6` — a přesto **jedno** volání.
- **Kam tedy volání jdou:** do **opakovaných pokusů téhož zadání**, ne do
  složitosti. **Odhad (odvozeno, ne měřeno):** z 247 běhů jich **117 z 211
  selhaných** (55 %) skončilo do 30 s → **kdyby se ta polovina neopakovala,
  ušetří se víc než polovina volání.**

**Pozor — co jsem NEměřil:** **tokeny se v logu vyskytují jen jednou** (formát
aideru se změnil a `Tokens:` není v každém běhu). Číslo **8,3 k tokenů na běh**
je tedy **jedno měření, ne průměr** — a víc z logů vytáhnout nešlo (§11).

### Q4 — Co se stane, když se registr her rozbije?

**měřeno `node _analyza\hl-registr.mjs` (jen čtení a `dry_run`, nic se neměnilo).**

Fallback v kódu (`index.ts:447-454`):
```ts
if (rows.results?.length) return rows.results;
return [{ game_id: "default", repo: env.GITHUB_REPO,
          roadmap_file: env.ROADMAP_FILE || ".forge/roadmap.json", active: 1 }];
```

**Co to dnes znamená konkrétně:**

| Situace | Co conductor udělá | Důsledek |
|---|---|---|
| registr prázdný (`games` bez aktivní hry) | vrátí **jednu falešnou hru** `game_id: "default"` na `env.GITHUB_REPO` | **dispatchuje dál** — orchestra se nedá vypnout (inv. 18) |
| `item_id` pak je `default/<grain>` | **jiný klíč** než `uo-shadows/<grain>` | vzniknou **nové řádky v roadmap**, staré zůstanou → **dvojí práce** (naměřeno 30. 9.: #115–#118 jely s #119–#122) |
| s **druhou** hrou (O9/4) | fallback míří na `GITHUB_REPO` = **jedna konkrétní hra** | práce pro hru B se **odevzdá hře A** |
| `/tasks/cleanup` s vypnutou hrou | `listGames` vrátí prázdno → `platne` je prázdné → kód **odmítne mazat** (`503`, `index.ts:1149-1151`) | **bezpečné** — ale s vypnutou hrou **smaže cache roadmapy** (inv. 18) |

**Bezpečná část (naměřeno `dry_run`):**
```
POST /tasks/cleanup {dry_run:true} → HTTP 200
  platnych_granuli_v_souborech: 18, radku_v_cache: 14,
  osirelych_radku: 0, osirelych_ukolu: 0, ukoly_bez_vazby: 0
POST /roadmap/reset {game_id, dry_run:true} → HTTP 200
  smazal_bych_granuli: 14, dotklo_bych_se_ukolu: 0
```

**Verdikt Q4:** registr dnes **není jednobodová porucha** — rozbitý registr
**nezastaví** orchestra, **přesměruje** ji. To je horší varianta: tichá práce
na špatném místě místo viditelného zastavení. **Priorita fallbacku je tedy
vyšší, než jak ji vidí plán** (B4/L15 v plánu je „střední riziko"; naměřený
důsledek je „dvojí práce" a „práce na cizí hře").

### Q5 — Je šablona `repo/` nezávislá na hře?

**měřeno `node _analyza\hl-instal.mjs` (simulace instalace, 32 souborů).**

| Co | Naměřeno |
|---|---|
| `uo-shadows` v šabloně | **6 souborů, 12 výskytů** — `baseline.py` 1×, `check-schema.py` **4×**, `vision-profile.json` **2×**, `agent.yml` **2×**, 2× `__pycache__` (netrackované `.pyc`) |
| `NAZEV-REPA` | 2 soubory, **5 výskytů** (`release.yml` 3×, `termux-setup.sh` 2×) — **v HEAD** |
| `forge-quest` | 1 soubor, 2 výskyty — **text o opravě**, ne vada |
| `ssevcikm-spec` | 3 soubory, 4 výskyty |
| absolutní cesty na tuto stanici | **3** (`.forge/node/.env` 1×, 2× `.pyc`) |
| odkazy na soubory, které v novém repu nejsou | **12** |

**Odpověď: NE — šablona nezávislá není.** A to ve **třech různých významech**,
které je potřeba odlišit — **a ověřil jsem to řádek po řádku** (ne jen počtem):

```
agent.yml:379   # Naměřeno 30. 9. 2026 (hra uo-shadows): bez importu padaly testy VŽDY   → komentář
agent.yml:617   # … (např. tools/blender/, kde jich u uo-shadows bylo 260)               → komentář
check-schema.py:4    PROČ TO EXISTUJE — naměřeno … na `uo-shadows`, kde se rozešly ČTYŘI  → komentář
check-schema.py:162  # A) `tile: {sirka, vyska}` + `viewport`   (uo-shadows)              → komentář
check-schema.py:250  # `uo-shadows` je případ (b): …                                      → komentář
check-schema.py:23   python orchestra/tools/kontrola-schematu.py games/uo-shadows --json  → MRTVÝ ODKAZ
baseline.py:109      naměřeno na `uo-shadows`: dlaždice std 12–41                         → komentář
vision-profile.json:7   „bylo natvrdo hra: uo-shadows a popis UO stylu…"                  → komentář
vision-profile.json:31  „_hra": „DOPLŇ NÁZEV TÉTO HRY…"                                   → šablona dokumentace
```

1. **Zbytky konkrétní hry** (12 výskytů `uo-shadows`): **všechny jsou
   v komentářích nebo v dokumentaci** — tedy **past P2**: kdo je smaže, smaže
   vysvětlení, proč brána měří to, co měří. **Jediná výjimka je
   `check-schema.py:23`** — odkaz na `orchestra/tools/kontrola-schematu.py`,
   soubor, který **v pracovním stromu už neexistuje** (smazán 13:52 UTC).
   To je **mrtvý návod**, ne zbytek hry.
2. **`NAZEV-REPA`** (5 výskytů): **to není zbytek, to je nefunkční odkaz**
   — a v pracovním stromu je opravený (D1, 13:48 UTC).
3. **`__pycache__` v šabloně** (netrackované `.pyc` soubory): **to skutečně
   patří do koše** — binárky z lokálního spuštění bran, které by se kopírovaly
   do každé hry.

**Doplněk, který je pro návrh důležitější než ty tři:** šablona **není neúplná
jen „skrytými vazbami" — je neúplná bootstrapem** (S23): `install-into-repo.ps1`
vyžaduje `projects/<Projekt>/project.godot` a `.gitignore` **generuje jen on**.

### Q6 — Které soubory v šabloně se v nové hře NIKDY nepoužijí?

**měřeno simulací instalace + analýzou odkazů.**

| Soubor | Použije se? | Doklad |
|---|---|---|
| `.forge/node/.env` | **NIKDY jako obsah** — je to tajemství pro konkrétní stanici (`FORGE_GODOT` míří na `C:\Users\Ssevc\…\Godot_v4.7.2…exe`) | absolutní cesta **uvnitř** souboru; v nové hře **neplatná** |
| `.forge/provider.env`, `.forge/provider.json` | **NIKDY** — generuje je `pick-provider.mjs` za běhu, jsou gitignorované | `kód`: `.gitignore` je má |
| `.forge/node/termux-setup.sh` | **jen pro Termux** (jiné zařízení) | obsahuje `NAZEV-REPA` jako **návod pro člověka** |
| **12 odkazovaných souborů** (`assets/spec.json`, `assets/levels/main.json`, `level.gd`, `world.gd`, `enemy.gd`, `game.gd`, `tests/run_tests.gd`, `manifest.json`, `baseline.json`, …) | **v novém repu NEEXISTUJÍ** — brány na ně sahají | naměřeno: `CHYBI v novem repu: 12` |
| `__pycache__/*.pyc` | **NIKDY** — binárky z lokálního běhu | netrackované, ale **kopírují se** (`Copy-Item` bere disk, ne git) |

**Odpověď:** **čtyři soubory a jeden adresář** jsou mrtvá váha, kterou každá
hra dědí (`.env`, `provider.env`, `provider.json`, `termux-setup.sh`,
`__pycache__/`) — a **dvanáct odkazů** je váha opačná: brány, které v nové hře
**nemají co měřit**. První je drobnost; **druhé je S23** a je to důvod, proč
dnes nová hra nemůže zezelenat.

### Q7 — Co dělá agent, když dostane granuli, které nerozumí?

**měřeno `hl-chyby.mjs` (27 běhů, které spadly na parse gate) + `hl-typy.py`.**

**Odpověď ve třech krocích, každý doložený:**

1. **Domyslí si rozhraní, které neviděl.** Agent dostane soubory závislostí
   **jen 1. úroveň** a **jen `owns`**. Naměřeno: granule `sim.mining` **nevidí**
   `level.gd`; `entity.enemy` nevidí `attributes.gd` ani `skills.gd`.
   Model tedy **použije typ, který v projektu neexistuje** — a to je
   **55 % všech parse chyb** (15 ze 27 běhů): `Identifier "Skills" not declared`,
   `Identifier "World" not declared`, `Could not find type "Economy"`.
   **A ve 21 případech ze 21 nemá soubor závislosti `class_name`** — model tedy
   **ani nemohl** uhodnout správný název typu (měřeno `hl-typy.py`).
2. **Opakuje stejnou chybu s jiným modelem.** Běh #243 a #237: **tatáž granule,
   tatáž chyba**; #244 a #238: totéž. `attempt` mění **jen model**.
3. **Nedozví se to.** Selhání skončí v `log_tail` (8 000 znaků) a `summary`
   v D1 — a **do dalšího zadání se nic z toho nepředá** (S20).

**A co dělá orchestra:** parse gate to **správně** shodí (to je její účel),
úkol se vrátí do fronty, za 3,2 minuty (medián) přijde další pokus
**s tímtéž zadáním a jiným modelem**.

### Q8 — Jak vypadá orchestrace, když pracuje na DVOU hrách zároveň?

**NEODPOVÍDÁM MĚŘENÍM — a je to přiznaná mez.** Nikdy nenastalo
(registr má **1 hru**, měřeno `GET /games`) a **nedá se to bezpečně vyvolat**:
založení druhé hry by znamenalo zásah do živého systému, který zadání zakazuje.

**Co k tomu říct lze (a je to označené):**
- **odvozeno** (z kódu): pět z osmi věcí praskne první den — tabelováno v **O9**.
- **měřeno** jsou jen **předpoklady** toho testu: registr má 1 hru; limity jsou
  globální (`wrangler.toml`); fallback míří na jednu hru; `owns` klíče jsou
  scoped na repo (správně); klíče LLM jsou per-repo.
- **Co by to ověřilo:** založit **druhou hru bez granulí** (prázdná roadmapa) —
  to je **nejmenší bezpečný test**: conductor by ji registroval, `roadmapTick`
  by pro ni nenašel nic a **jediné, co by se dalo měřit, je chování registru,
  fallbacku a `/health`**. Ani to jsem neudělal, protože mění živý stav.

### Q9 — Kolik z `tools/` (70 souborů) je živých?

**měřeno `hl-vazby.py` (Python walk celého workspace, mimo `_analyza/`).**

```
nástrojů v tools/ (soubory): 70
z toho zmíněných někde jinde: 52
NIKDE nezmíněných:            18  (26 %)
   analyza-aider, analyza-aktualni, analyza-logu, analyza-modelu, analyza-testy,
   analyza-verdikt, detail-behu, diag-baseline, dopln-attempt, mer-sklon-hranice,
   mereni-chyb, mereni-modelu, mereni-pltvani, mereni-pred-po, overit-razeni,
   pridej-eskalaci, repo-files, telegram-chat-id
```

**Nejživější (počet referencí mimo `tools/`):**
`validate-all.mjs` 15× · `kontrola-schematu.py` 11× · `git.cmd` 10× ·
`test-check-schema.py` 10× · `kontrola-driftu.mjs` 9× · `over-skilly.py` 9× ·
`zjisti-pages.mjs` 9× · `lint-roadmapa.py` 8× · `over-dokumentaci.py` 8×.

**Dvě čísla, která tomu dávají smysl:**
- **`validate-all.mjs` je nejživější nástroj — a v `HEAD` vždy vrací `exit 0`
  i při „✗ NALEZENO 3 PROBLÉMŮ"** (ověřeno čtením HEAD verze: **0 výskytů
  `process.exitCode`**, `:186` volá starou kopii brány). V pracovním stromu
  (13:46 UTC) už vrací `1`, naměřeno.
- **18 mrtvých nástrojů není náhoda** — je to **důsledek toho, že nástroje
  vznikaly pro konkrétní poruchu** (`analyza-*`, `mereni-*`), a když porucha
  pominula, nástroj zůstal. **`AGENTS.md` k tomu má pravidlo**
  („Nefunkční metriku smazat, ne nechat ležet — budí důvěru").

**Odpověď:** **52 živých, 18 mrtvých (26 %)** — a **u 15 z 52 je „živý" jen
to, že je zmíněn v dokumentaci**, ne že ho někdo spouští. **Skutečně
spouštěných** (z `validate-all.mjs`, CI nebo skillu) je **kolem 12**.

### Q10 — Kde je zdroj pravdy o roadmapě: soubor, nebo D1?

**měřeno `node _analyza\hl-roadmap-srovnani.mjs` (soubor vs. `GET /roadmap`).**

```
D1: 14 řádků, z toho 10 'done'      soubor: 18 granul, z toho 2 s done:true
jen v D1: 0                          jen v souboru (nemá řádek v D1): 4
   → core.attributes, entity.item, sim.offline, engine.shell
```

**Odpověď: soubor je zdroj PRAVDY o plánu, D1 je zdroj STAVU — a dnes to
v praxi znamená, že stav je jen v D1** (8 granul je v D1 `done`, ale soubor
o tom neví).

| Kde co žije | Soubor | D1 |
|---|---|---|
| které granule existují | **ANO** (18) | 14 (po resetu by se stavěly znovu) |
| co granule obsahuje (prompt, `owns`, `depends_on`) | **ANO** | kopie v `tasks.payload` |
| hotovo / selhalo | 2× `done:true` | **ANO** (10× `done`) |
| kolik pokusů | **NE** | **ANO** |
| kdo vlastní soubory | `owns` v souboru | kopie v payloadu |

**A co z toho plyne konkrétně (naměřeno `dry_run`):**
```
POST /roadmap/reset {game_id:'uo-shadows', dry_run:true}
   → smazal_bych_granuli: 14, dotklo_bych_se_ukolu: 0
```
**Po takovém resetu by D1 o stav přišel a stavěl by ho znovu ze souboru.**
U **8 granul**, které jsou dnes `done` jen v D1, by se spoléhalo na záchrannou
cestu: `roadmapTick` párování **podle názvu sloučeného PR** (`index.ts:502-503`).
To je **jediná pojistka** — a je **křehká**: funguje jen dokud je PR
v **posledních 100 zavřených** a dokud se **titulky granul neopakují**.

**Verdikt Q10:** synchronizace je **ruční** (dopsat `done: true` do souboru)
a **nikdo ji nehlídá**. Nejmenší správná oprava není nový nástroj, ale
**doplnit `done` tam, kde D1 ví o mergi** — a **udělat z toho invariant**
(„co je v D1 `done`, musí být v souboru `done: true`, jinak je to nález").

---

## 11. Co analýza NEZJISTILA

**Tohle je povinný oddíl a je myšlený vážně.** Všechno níž je **nevím** —
a u každého je řečeno, **co by to změnilo**.

### 11.1 Co jsem nemohl změřit kvůli prostředí (ne kvůli sobě)

| Co | Proč | Co s tím |
|---|---|---|
| **`vision.test.mjs` 36/36 a 28/28** | sandbox `workspace-write` → **`EPERM` (spawn)** v obou kopiích | podklad z `HANDOFF.md`; **nepřebírám jako fakt**, ale ani nevyvracím. Tabulka statických počtů v podkladech §3.9 je **nekonzistentní** (regex `test(` počítá i volání ve víceřádkovém tvaru) — **statický počet není měření** (past P1) |
| **`baseline.py testy` 24/24** | `PermissionError WinError 5` na přesměrovaném tempu | totéž |
| **Godot testy hry** (`run_tests.gd`) | `--headless` testy bych spustil, ale **měnily by stav workspace** a k analýze nic nepřidají | — |
| **`/tick`** | **Záměrně jsem ho nezavolal** — spustil by dispatch a tím bych změnil stav živého systému. Zadání to zakazuje („neměnit kód orchestra ani her" → a dispatch mění stav) | stav jsem četl z `/health`, `/queue`, `/roadmap`, `/failed` |

### 11.2 Co jsem nedohlédl v kódu

1. **Proč `/queue` v 13:43 ukazoval 4 `ready` úlohy a `running: 0`, když cron
   tika každou minutu.** Vysvětlení, které mám, je **odvozené**: guard je
   nevydá, protože `updated_at` je mladší než 3 h (a **to sedí na minutu**:
   `entity.npc` 13:10:54 + 3 h = 16:10:54). **Nemám to ale z conductoru
   potvrzené** — `/tick` by to řekl a nevolal jsem ho. **Kdyby se ukázalo, že
   `roadmapTick` v tiku vůbec neběží**, padá tím část vysvětlení Q1 (a S12 by
   byla jiná vada).
2. **Kdo volá `POST /task`** (kromě `bin/task.mjs`). Nenašel jsem volajícího
   v repu; možná ho volá něco mimo workspace.
3. **Proč je `attempts` u tří úloh 9, když je strop 5.** Vím, že `roadmapTick`
   zakládá nový úkol (S21) a že 30. 9. proběhl `/roadmap/reset` a úklid
   (invariant 10) — tedy **dvojí práce na téže granuli** (#115–#118 vs
   #119–#122). **Nedokázal jsem to ale přiřadit k jednomu konkrétnímu
   mechanismu** a víc než 9 běhů na úlohu jsem nenašel.
4. **Co je v `runs.log_tail` a `artifacts`** — čtu jen to, co conductor vrátí
   v `/failed` (a to je dnes prázdné). **Historie 247 běhů v D1 je pro mě
   nedostupná** (D1 přes REST nejde, viz skill `orchestra`).
5. **Proč `agent.yml` v šabloně obsahuje `uo-shadows` 2×** — našel jsem to
   měřením, ale **neotevřel jsem ty dva řádky**, takže **nevím, jestli je to
   komentář, nebo vada**.

### 11.3 Kde je moje tvrzení jen odvozené (a mohu se splést)

| Tvrzení | Značka | Co by ho vyvrátilo |
|---|---|---|
| „55 % selhaných běhů nezačalo pracovat" | **odvozeno** z doby kroku agenta < 30 s | kdyby krok zahrnoval i instalaci aideru (nezahrnuje — ta je jinde) **nebo** kdyby model odpovídal do 30 s a přesto nic nezměnil (to je jev, který jsem viděl: 10–14 s u „nic nezměnil") |
| „cooldown je příčina 82,7 % nečinnosti" | **odvozeno** z časů (`roadmap.updated_at` + 3 h) | kdyby se ukázalo, že cron tika neběžel (viz 11.2/1) |
| „nová hra nemůže zezelenat" | **odvozeno** ze simulace instalace | kdyby měl někdo šablonu, která už `project.godot` obsahuje — **nemá** (měřeno: v `repo/` je 27 souborů, žádný z nich) |
| „`acceptance` je past" | **odvozeno** z měření (0 čtení v kódu) | kdyby ho četl **agent** (model) v promptu — to jsem neměřil; v promptu granule **není** (prompt je text z `prompt` pole), ale **model vidí celý `roadmap.json`? Ne** — `files-to-edit.mjs` mu dává jen `owns` soubory. Tedy ne |
| „`provides` nic nečte" | **měřeno** (0 souborů) | nic — je to měření |

### 11.4 Kde jsem se spletl JÁ (a je to vidět)

**Tohle patří do analýzy, protože jinak by vypadalo, že jsem se nespletl.**

| # | Co jsem si myslel | Co naměřeno | Jak to vzniklo |
|---|---|---|---|
| 1 | „`merged_by` je `null` → GitHub nevrací autora mergu" | **Vrací**: `/pulls/27` → `merged_by: ssevcikm-spec`. **Seznam** `/pulls?state=closed` vrací `null`, **detail** ne | **Past P5**: dva endpointy, stejné jméno pole, různá odpověď. Opravil jsem to **týmž postupem, jakým vzniklo původní číslo** (detail PR), ne hádáním |
| 2 | „PR #27 prošel gate špatně, protože má 80 řádků `.import`" | PR měl **+18/−0 ve 2 souborech**; gate fungoval správně | přečetl jsem **komentář v kódu** a udělal z něj závěr. **Přesně past, na kterou upozorňuje `AGENTS.md`** |
| 3 | „`release.yml` má 5 výskytů `NAZEV-REPA`" (druhé měření) | V **HEAD** jsou **3**; pracovní strom má **0** | měřil jsem **dvakrát v různých časech** a jinou session to mezitím opravila — **past P4**. Obě čísla jsou správně, každé pro jiný čas |
| 4 | „`vision.mjs` nečte `DEEPSEEK_API_KEY`" | **Čte** (`vision.mjs:210-213`, volá `api.deepseek.com`) | můj test měl **špatný předpoklad**, ne kód |
| 5 | „`providers.json` se nečte za běhu" (první test) | **Čte** — v `pick-provider.mjs`, ne v `provider-choice.mjs`, který jsem testoval | hledal jsem **v jednom souboru** a udělal závěr o celku |

**Pět omylů, všechny nalezené vlastním měřením.** To je podle zadání (§3.5)
**podmínka, že analýza není hotová předem** — a je to zároveň **nejlepší
doklad toho, jak vypadají pasti P1–P5 v praxi**, ne v tabulce.

### 11.5 Co je mimo dosah téhle analýzy úplně

- **Ekonomika v penězích.** Všechny modely jsou free; cena je **kvóta**, ne
  koruny. **Neměřil jsem**, kolik z denní kvóty orchestra spotřebuje —
  z logů to nejde (tokeny jsou jen v jednom běhu).
- **Kvalita výstupu agenta.** Vím, že PR **projde gate a CI** (24 z 28
  sloučených). **Nevím, jestli je hra dobrá** — to je ruční fitness funkce
  a je správné, že zůstala člověku.
- **Bezpečnost mimo S26.** Nezkoumal jsem, co všechno umí `FORGE_PAT`
  (fine-grained PAT) a jestli je jeho rozsah minimální.
- **Chování pod zátěží.** `MAX_CONCURRENT=5`, ale naměřené maximum souběžných
  běhů bylo menší (běhy chodí po vlnách). **Netestoval jsem**, co se stane
  při 5 souběžných PR — jen že to kód umožňuje.
- **Druhá hra** (Q8) — vysvětleno výše.
- **Historie před 29. 9. 2026.** Repo hry bylo založeno **29. 9. 2026**
  (GitHub API) a orchestra taky. **Cokoli staršího je jiný projekt**
  (GameForge, `forge-quest`, `idle-realms`, `IdleFantasy_Bart`) a nezkoumal
  jsem to — kromě toho, že **`forge-quest` je živá hra** (ověřeno: `has_pages:
  true`, push 30. 9.).

---

## 12. Čím je každé tvrzení doložené (tabulka tvrzení → důkaz)

**Ne u všech — u těch, na kterých stojí rozhodnutí.**

| # | Tvrzení | Značka | Důkaz (příkaz / soubor:řádek) | Kdy měřeno |
|---|---|---|---|---|
| 1 | Orchestra běžela **6,86 h z 49,35 h (13,9 %)** | měřeno | `node _analyza\hl-vytizeni.mjs`, GitHub API, 247 běhů | 1. 10. 13:47 UTC |
| 2 | **8 oken nečinnosti = 40,79 h (82,7 %)** a CI cíle bylo **zelené** | měřeno | `node _analyza\hl-okna.mjs` (kříží běhy `agent.yml` s běhy `ci.yml`) | 1. 10. 13:48 UTC |
| 3 | Nová granule čeká **3 h** | měřeno (SQL ze zdroje) | `python _analyza\hl-sql.py` — guard `index.ts:786-792` v SQLite, scénář 1a | 1. 10. 13:53 UTC |
| 4 | Test #3 **umí spadnout** | měřeno | `python _analyza\hl-mutace.py` → **3/3 vady chyceny** | 1. 10. 13:54 UTC |
| 5 | Živý důkaz #3: `entity.enemy` 10:09:14 → 13:10:09 | měřeno | `GET /roadmap` + `/actions/workflows/agent.yml/runs` | 1. 10. 13:45 UTC |
| 6 | **95× „agent nic nezměnil", 82× testy, 27× parsování, 28× úspěch** | měřeno | `node _analyza\hl-priciny.mjs` (joby a kroky všech 240 běhů) | 1. 10. 13:52 UTC |
| 7 | **55 % selhaných běhů < 30 s** v kroku agenta | měřeno | totéž (časy kroků z GitHub API) | 1. 10. 13:52 UTC |
| 8 | **7 úloh překročilo `MAX_ATTEMPTS=5`** (#115–#117 devět běhů) | měřeno | `node _analyza\hl-strop.mjs` | 1. 10. 13:50 UTC |
| 9 | Retry uvnitř úlohy: **medián 3,2 min**, 94 % pod 60 min | měřeno | `hl-vytizeni.mjs` (mezery mezi běhy téhož tasku) | 1. 10. 13:47 UTC |
| 10 | `acceptance` a `provides` **nečte žádný kód** | měřeno | `python _analyza\hl-smlouvy.py` (komentáře odstraněny) | 1. 10. 13:49 UTC |
| 11 | V novém repu zůstane **12 odkazů na neexistující soubory** a **5× `NAZEV-REPA`** | měřeno | `node _analyza\hl-instal.mjs` (simulace `Copy-Item`) | 1. 10. 13:35 UTC (HEAD) |
| 12 | **21 výskytů `.gd` v závislostech, ani jeden nemá `class_name`** | měřeno | `python _analyza\hl-typy.py` | 1. 10. 13:51 UTC |
| 13 | Guard je **jediná** kontrola pro 7 endpointů včetně `/task` | kód | `index.ts:62-64`, `:1008`, `:1027`, `:1056`, `:1119`, `:1254`, `:1269`, `:1278` | 1. 10. |
| 14 | `agent.yml` čeká na CI **max 10 min** a timeout **jen okomentuje** | kód | `agent.yml:660-691` | 1. 10. |
| 15 | `listGames` fallback míří na `env.GITHUB_REPO` | měřeno + kód | `node _analyza\hl-registr.mjs` (dry_run) + `index.ts:447-454` | 1. 10. 14:00 UTC |
| 16 | `validate-all.mjs` v **HEAD** vždy `exit 0` | měřeno | `git show HEAD:tools/validate-all.mjs` → **0× `process.exitCode`**, `:186` volá starou bránu | 1. 10. 13:59 UTC |
| 17 | `validate-all.mjs` v **pracovním stromu** vrací **1** | měřeno | `node tools\validate-all.mjs` → „✗ NALEZENO 4 PROBLÉMŮ", exit 1 | 1. 10. 13:57 UTC |
| 18 | `test-cooldown.py` (nová verze) **je červený a měří SQL ze zdroje** | měřeno | `python tools\test-cooldown.py` → „10 kontrol, 1 chyb", exit 1 | 1. 10. 13:57 UTC |
| 19 | LGTM baseline: **272 položek, všech 272 `agent-init`, jediná minuta** | měřeno | `node _analyza\hl-baseline.mjs` | 1. 10. 13:55 UTC |
| 20 | Soubor vs. D1: **4 granule chybí v D1, 8 `done` jen v D1** | měřeno | `node _analyza\hl-roadmap-srovnani.mjs` | 1. 10. 13:56 UTC |
| 21 | **18 z 70 nástrojů** nikdo nikde nezmiňuje | měřeno | `python _analyza\hl-vazby.py` (Python walk) | 1. 10. 13:46 UTC |
| 22 | `release.yml` v HEAD: **3× `NAZEV-REPA`**, 0× `github.repository` | měřeno | `git show HEAD:…release.yml` + `git cat-file -s` (6464 B) | 1. 10. 13:59 UTC |
| 23 | 27 souborů v šabloně i ve hře, **19 shodných, 8 rozdílných** | měřeno | `python _analyza\hl-cena.py` | 1. 10. 13:54 UTC |
| 24 | Drift kontrola hlídá **12 z 27** souborů | měřeno + kód | `hl-cena.py` + `kontrola-driftu.mjs` | 1. 10. 13:54 UTC |
| 25 | `pc-domaci` je **41,7 h offline**, `oracle-frankfurt` žije | měřeno | `GET /health` → `minutes_ago: 2517 / 0` | 1. 10. 14:00 UTC |
| 26 | `index.ts` = **1 368 řádků**, **90 SQL dotazů**, **17 endpointů** | měřeno | `python _analyza\hl-conductor.py` + `hl-vazby.py` | 1. 10. 13:44 UTC |
| 27 | Nasazený conductor = zdroj v gitu | měřeno | `node _analyza\hl-deploy.mjs` → sha256 shodné; poslední deploy #30 `success` 10:04:35 UTC | 1. 10. 13:47 UTC |
| 28 | `ci=timeout` v produkci **nenastal** (nevím o něm) | nevím | — | — |

---

## 13. Co by tuhle analýzu vyvrátilo

*(Nejtěžší oddíl. Píšu konkrétní pozorování, ne „mohl bych se mýlit".)**

| # | Kdyby platilo tohle | Padá tím |
|---|---|---|
| 1 | **Cron v Cloudflare netiká každou minutu** (nebo `roadmapTick` v tiku neběží) | **celé vysvětlení Q1 i S12.** Osm oken nečinnosti by nebyl cooldown, ale mrtvý tik — a to je **jiná vada s jinou opravou**. Jak to poznám: `POST /tick` a srovnání `ready` před/po; nebo Cloudflare logy. **Neudělal jsem to, protože to mění stav** |
| 2 | **`RETRY_HOURS` v produkci není 3** (někdo ho změnil v CF dashboardu, ne v `wrangler.toml`) | časová osa `entity.enemy` (3 h 1 min) by byla náhoda. **Jak to poznám:** `/tick` to hlásí (`watchdog: N ohlášeno (prah …)`), ale `RETRY_HOURS` v odpovědi **není** — což je samo nález |
| 3 | **Model v kroku „Spusť agenta" nemá dost času** (timeout, kvóta, síť) | „55 % běhů do 30 s" by nebyl problém zadání, ale infrastruktury. **Jak to poznám:** v logu #243 je **jedno** `Tokens: 7.4k sent` — tedy **volání proběhlo**; ale u běhů, kde `Tokens:` **není**, to nevím (§11.2) |
| 4 | **Agent v CI dostane kontext, který jsem přehlédl** (např. celý `roadmap.json`) | S19 („model si vymyslel typ") by nebyla vada kontraktu, ale modelu. **Jak to poznám:** `agent.yml` volá `aider --message "$FORGE_PROMPT"` a `files-to-edit.mjs --grain …` → jen `owns`. **Ověřeno v logu #243**: „Added scripts/mining.gd to the chat" + 7 read-only. Celý `roadmap.json` tam **není** |
| 5 | **Druhá hra už někdy běžela** (třeba `idle-realms`) | O9 by nebyla predikce, ale popis. **Jak to poznám:** registr má 1 hru (`GET /games`); ale `idle-realms` a `IdleFantasy_Bart` **existují a mají push 30. 9.** — **jestli na nich orchestra někdy pracovala, nevím** (§11.5) |
| 6 | **BRÁNY v CI se nikdy nespouštěly** (např. `ci.yml` se nikdy nespustil na PR) | „27 parse chyb" a „82 selhání testů" by nebyly o hře, ale o prostředí. **Jak to poznám:** `ci.yml` běžel **60×** na main a **19 z posledních 20 úspěšně** — takže běhá |
| 7 | **`merged_by: ssevcikm-spec` je robot, ne člověk** | „PR se slučují samy" by platilo. **Jak to poznám:** v `git log` mají **všechny** commity (i ty od agenta) autora `ssevcikm-spec` — tedy **jméno nic nedokazuje**. Rozhodující je, že merge dělá `gh pr merge` **jen** když projde gate+CI (auto) a jinak to dělá člověk — **a v datech mám 24 sloučených z 28, ale nerozlišil jsem, které sloučil kdo** |
| 8 | **Šablona `repo/` je jen ZRCADLO hry** (ne vzor) | S23 by nebyla vada — jen by se hra do šablony nekopírovala. **Jak to poznám:** `install-into-repo.ps1:94-96` kopíruje `repo\.forge` → cíl, tedy **vzor → hra**; směr je jasný |
| 9 | **„13,9 % využití" je špatná metrika** (třeba proto, že běhů je málo a dlouho trvají) | závěr „orchestra je mrtvá 83 % času" by neplatil. **Jak to poznám:** metrika měří **sjednocení intervalů běhů**, ne počet — i kdyby běhů bylo 10× víc, poměr se nezmění, dokud se nezmění rozložení v čase. **Slabé místo je jinde:** co kdyby orchestra **pracovala mimo `agent.yml`** (např. domácí uzel)? Naměřeno: `pc-domaci jobs_done: 4` za celou historii → **zanedbatelné** |
| 10 | **Někdo mezitím opravil všechny tři vady conductoru** | Celá varianta A by byla hotová. **Jak to poznám:** `git -C orchestra status` a `conductor/src/index.ts:786-792` — **v 13:52 UTC byla změna `index.ts` NULA** (změněny byly jiné soubory) |

**Dvě věci, které bych považoval za vyvrácení i kdyby čísla seděla:**
- **Kdyby se ukázalo, že `acceptance` a `provides` jsou v roadmapě proto, že je
  čte MODEL** (a ne kód) — pak by S22 nebyla vada, ale nezvyklý, ale funkční
  způsob, jak zadat smlouvu. **Netestoval jsem to** a je to nejslabší místo
  mé argumentace o smlouvách.
- **Kdyby platilo, že 3h cooldown je záměr i pro nové granule** (např. aby se
  nevyčerpala kvóta na začátku dne) — pak by S12 nebyla vada, ale vlastnost.
  **V kódu pro to ale nic není** (komentář `index.ts:790-804` mluví jen
  o selháních) a **`README`/plán to jako vlastnost neuvádí**.

---

## 14. Hotovo znamená — kontrola proti zadání §9

*(Zadání má deset měřitelných bodů. Procházím je po jednom a u každého píšu,
**čím je splněn** — nebo že splněn není.)*

| # | Bod ze zadání §9 | Stav | Doklad |
|---|---|---|---|
| 1 | Existuje dokument se **všemi 12 oddíly** z §5 | **SPLNĚNO** | §1–§5 (Část I), §6–§9 (Část II), §10–§12 (Část III) + §0 (rámec), §13 (přepsaný verdikt), §14 (tenhle oddíl) |
| 2 | **Každé tvrzení o chování** má značku | **SPLNĚNO** | značky **měřeno / kód / odvozeno / nevím** jsou v celém textu; „nevím" je soustředěné v §10–§11 (podle zadání) a v §13 |
| 3 | **Aspoň 5 nových tříd selhání** nad S1–S18 | **SPLNĚNO** — **12** | §4: **S19–S30**, každá s polem „čím je to nové" proti nejbližší starší třídě |
| 4 | **Aspoň 3 vlastní měření**, která v existujících dokumentech nejsou | **SPLNĚNO** — 3 hlavní + 27 dílčích | §0.3 (M1, M2, M3) + §12 (28 řádků s příkazem); podklady `_analyza\HLOUBKOVA-MERENI.md`; **31 souborů `_analyza\hl-*`** |
| 5 | **Aspoň 1 tvrzení z dokumentace vyvráceno nebo zpřesněno** | **SPLNĚNO** — 5 vlastních omylů + 3 zpřesnění cizích | §11.4 (5×) + §11.1 (36/36 nepřebírám) + §4/S24 (PR #27 — **neškodné**) + §13/7 (`merged_by`) |
| 6 | Odpovězeno na **aspoň 5 z 10 otázek** | **SPLNĚNO** — **9** | §10: Q1–Q7, Q9, Q10; **Q8 je přiznaně neodpovězená** |
| 7 | Návrh má **aspoň 2 varianty** s cenou, rizikem a tím, co nedělá | **SPLNĚNO** | §8: **A** (1–2 dny, nízké riziko) a **B** (8–12 dní, vysoké); každá má vlastní odstavec „Co to NEDĚLÁ" |
| 8 | Je napsané, **co by analýzu vyvrátilo** | **SPLNĚNO** | §13: 10 konkrétních pozorování + 2 „i kdyby čísla seděla" |
| 9 | Je napsané, **co analýza nezjistila** — a nejsou to fráze | **SPLNĚNO** | §11: čtyři pododdíly — co nešlo změřit (s důvodem), co jsem nedohlédl (5 bodů), co je odvozené (5 tvrzení), **kde jsem se spletl já** (5 omylů) |
| 10 | **Nula změn v obou repech orchestra a hry** | **SPLNĚNO S VÝHRADOU — viz níže** | `git status` v orchestra: **5 změněných/smazaných souborů**, ale **žádný z nich jsem nezměnil já** (změny vznikly 13:46–13:48 UTC v jiné session). `games\uo-shadows`: **strom čistý** |

### K bodu 10 podrobně (protože je to jediný sporný bod)

**Naměřeno v 13:43 UTC** (na začátku analýzy):
```
git -C orchestra status --porcelain  →   M README.md          (1 soubor)
git -C games\uo-shadows status       →   (prázdné)            (čistý strom)
```

**Naměřeno v 13:52 UTC** (během analýzy):
```
git -C orchestra status --porcelain
 M README.md
 M repo/.github/workflows/release.yml     (mtime 13:48:20)
 D tools/kontrola-schematu.py
 M tools/test-cooldown.py                 (mtime 13:46:18)
 M tools/validate-all.mjs                 (mtime 13:46:35)
```

**Co z toho plyne:** čtyři z těch pěti změn **vznikly během analýzy a nejsou
moje** — patří session, která souběžně plnila kroky **A1, A2 a D1**
implementačního plánu. **Já jsem do obou repů nezapsal nic** (jediné soubory,
které jsem vytvořil, jsou v `_analyza/`, což je mimo oba repy).

**Přesto bod 10 splněn „s výhradou", ne čistě** — protože **zadání
předpokládalo, že se repy nehnou**, a one se hýbaly. **Důsledek pro čtenáře:**
číslo u každého tvrzení o stavu je **bod v čase**, ne trvalý fakt. Kdo tuhle
analýzu čte později, musí **nejdřív zkontrolovat `git status`** a teprve pak
věřit tomu, co je v textu označené „HEAD" nebo „pracovní strom".

---

## 15. Přepsaný verdikt (na konci, po všem měření)

*(Zadání §5.1 to žádá: napsat na začátek a přepsat na konec. **Verdikt se
změnil** — proto je tady i nová verze, ne jen odkaz.)*

**Co se změnilo proti §1:** na začátku jsem si myslel, že hlavní problém
orchestra je **„chybějící kontrakt"** a že druhá hra je ta páka. Po měření
si myslím, že to je **pravda, ale ne to první** — protože:

1. **Hra má 2 dny** (repo založeno 29. 9., 61 commitů) a **jednoho vývojáře**.
   Návrh „zavést kontrakty pro druhou hru" je v tomhle stavu **investice
   do budoucnosti, která nemusí přijít** — a plán to sám říká („když F5
   nepřijde do rozumné doby, F3.5 se nedělá").
2. **Zároveň je naměřené, že orchestra 83 % času nic nedělá** — a příčina
   **není v kontraktech, ale v pěti místech kódu** (guard, `/report`, strop,
   notifikace, chybějící kontext mezi pokusy). **Ty se dají opravit za dva dny
   a bez rozhodnutí o architektuře.**
3. **A kontrakt, který bych zaváděl, není ten, o kterém mluví plán.**
   Plán chce `forge.config.json` a `prepisy.json` (co je kde). **Měření
   ale ukazuje, že bolest je jinde: v tom, že granule nemá čím prokázat, co
   poskytuje** (§7.1c) — a to plán neřeší vůbec.

**Verdikt v pěti větách (konečný):**

1. **Orchestra je funkční řemeslo pro jednu hru a jeden engine** — 24 sloučených
   PR, 10 hotových granul, zelené CI, nasazený conductor, který odpovídá
   na 17 endpointech.
2. **Její hlavní problém je čas, ne chyba:** běží **13,9 % času** a **83 %
   prostoje vzniká v kódu, který se ptá na špatnou věc** — na čas vzniku
   řádku místo na selhání.
3. **Druhý problém je, že agent neumí navázat:** 95 běhů nezmění nic,
   55 % selhání skončí do 30 s a **27 běhů spadne na to, že model uhodl
   rozhraní, které mu nikdo nedal** — protože **z 21 závislostí nemá ani jedna
   `class_name`**.
4. **Třetí problém je, že tři smlouvy existují jen jako text** (`acceptance`,
   `provides`, `schvalil: agent-init`) — a text, který nikdo nečte, vypadá
   jako hotová věc.
5. **Co s tím:** **opravit pět míst v kódu (varianta A, 1–2 dny)** a **teprve
   pak** rozhodnout, jestli orchestra má unést druhou hru — protože **kontrakt
   bez druhé hry je abstrakce pro jednoho konzumenta** a ta se v tomhle
   projektu už jednou nevyplatila (GameForge).

**A jedna věta, která se nezměnila:** orchestra **není** rozbitá. Je to systém,
který **dělá přesně to, co má napsané** — a to napsané je na pěti místech
špatně. To je ta lepší varianta: **vady jsou v rozhodnutích, ne v řemesle.**

---

**Konec dokumentu.** Surová měření: `_analyza\HLOUBKOVA-MERENI.md`.
Skripty: `_analyza\hl-*.{py,mjs}` (23 souborů, všechny spustitelné znovu).




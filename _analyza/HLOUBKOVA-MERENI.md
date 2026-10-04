# Podklady k ANALYZA-HLOUBKOVA-ORCHESTRA.md — naměřená čísla

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Co to je:** strojový výpis měření, o která se opírá hloubková analýza.
Každý řádek je **surový výstup skriptu**, ne jeho interpretace. Když se analýza
a tenhle soubor rozejdou, platí tenhle soubor (dá se spustit znovu).

**Datum měření:** 1. 10. 2026, 13:35–14:10 UTC (= 15:35–16:10 SELČ).
**Oprávnění:** sandbox `workspace-write` (testy vyžadující podprocesy s piped
stdio padají na `EPERM` — je to vidět u každého takového měření).
**Zdroj (bod v čase):** `orchestra` HEAD **`525d45b`** + pracovní strom
(v průběhu měření ho měnila jiná session — viz §0.2 analýzy).

---

## 1. Měřicí skripty (spustitelné, v `_analyza/`)

| skript | co měří | odpovídá na |
|---|---|---|
| `inv-orchestra.py` | inventura stromu, git ls-files vs. disk | O2, O4, Q9 |
| `hl-vazby.py` | mapa endpointů, kdo co volá, kdo čte roadmapu, živost `tools/` | O3, O5, Q9 |
| `hl-conductor.py` | statická analýza `index.ts` (SQL, konstanty, tabulky) | O3, O5 |
| `hl-live.mjs` | živý conductor + GitHub API | Q1–Q4 |
| `hl-vytizeni.mjs` | všech 247 běhů `agent.yml`, využití, mezery | Q1, Q2 |
| `hl-okna.mjs` | okna nečinnosti vs. stav CI cíle | Q1 |
| `hl-strop.mjs` | tasky, které překročily `MAX_ATTEMPTS` | S14, S21 |
| `hl-priciny.mjs` | **první selhaný krok** u všech 240 běhů | Q2, Q3, Q7 |
| `hl-chyby.mjs` | text parse errorů u 27 běhů | Q7, S19 |
| `hl-log.mjs`, `hl-krok.mjs` | detail jednoho běhu po krocích | Q7 |
| `hl-modely.mjs` | model, tokeny, časy kroků z logů | Q3 |
| `hl-instal.mjs` | **simulace instalace šablony do nového repa** | Q5, Q6, S23 |
| `hl-konfig.py` | konfigurační soubory, mrtvé klíče | O2, O3 |
| `hl-smlouvy.py` | která pole granule se čtou v kódu | O3, S22 |
| `hl-typy.py` | `class_name` u závislostí, co agent dostane | S19 |
| `hl-kopie.py` | tři kopie `vision.test.mjs`, .env soubory | S8, O2 |
| `hl-deploy.mjs` | nasazený conductor vs. git | O2 |
| `hl-roadmap-srovnani.mjs` | soubor vs. D1 | Q10 |
| `hl-sql.py` | **SQL guardu ze zdroje v SQLite** (7 scénářů) | Q1, S12 |
| `hl-mutace.py` | **mutační test `hl-sql.py`** (3 vady) | důkaz, že test měří |
| `hl-baseline.mjs` | LGTM baseline (272 položek) | S25 |
| `hl-cena.py` | cena změny (hra/engine/brána/provider) | O7 |
| `hl-overeni.mjs`, `hl-overeni2.mjs` | ověření tvrzení z dokumentace | §11, §12 |
| `hl-diakritika.py` | **kontrola diakritiky u dokumentů, které gate nesleduje** | S27 |
| `hl-registr.mjs` | co dělá conductor s rozbitým registrem (jen `dry_run`) | Q4 |

**Celkem 31 souborů `_analyza\hl-*`** (29 skriptů + 2 JSON s pracovními daty).

---

## 2. Živý stav (13:43 UTC)

```
GET /health  {"ok":true,"time":"2026-10-01T13:43:28.084Z","ready":4,"running":0,"games":1,
              "workers":[{"name":"oracle-frankfurt",...,"minutes_ago":1},
                         {"name":"pc-domaci",...,"minutes_ago":2500}]}
GET /games   games=[{game_id:"uo-shadows",repo:"ssevcikm-spec/uo-shadows",
                     roadmap_file:".forge/roadmap.json",active:1}]
GET /roadmap 14 řádků: {"done":10,"queued":4}; stáří updated_at: min 0,01 h / median 0,50 h / max 19,64 h
GET /failed  0 úloh
GET /queue   50 úloh (LIMIT 50): {"ready":4,"done":10,"blocked":36}
GET /workers oracle-frankfurt (žije, jobs_done=1), pc-domaci (naposledy 29. 9. 20:03, jobs_done=4)
```

**`/queue` — čtyři `ready` úlohy, které v 13:43 nešly vydat (všechny v cooldownu):**

| task | attempts | created_at | granule |
|---|---|---|---|
| 141 | 1 | 2026-10-01 10:09:14 | entity.enemy |
| 137 | 3 | 2026-09-30 22:33:51 | sim.crafting |
| 136 | 3 | 2026-09-30 22:33:50 | sim.mining |
| 132 | 4 | 2026-09-30 19:29:50 | entity.npc |

**`/roadmap` (D1) — 14 řádků, 4 v cooldownu:**

| item_id | rstatus | task | tstatus | attempts | updated_at | stáří |
|---|---|---|---|---|---|---|
| core.skills | done | 133 | done | 1 | 13:44:53 | 0,01 h |
| data.content | done | — | — | — | 2026-09-30 18:04:49 | 19,67 h |
| **entity.enemy** | **queued** | 141 | **ready** | 1 | 13:14:54 | 0,51 h |
| **entity.npc** | **queued** | 132 | **ready** | 4 | 13:10:54 | 0,57 h |
| entity.player | done | 134 | done | 1 | 13:44:53 | 0,01 h |
| persist.save | done | 139 | done | 2 | 13:12:23 | 0,55 h |
| sim.assist | done | 138 | done | 1 | 13:44:53 | 0,01 h |
| sim.combat | done | 135 | done | 2 | 13:44:53 | 0,01 h |
| **sim.crafting** | **queued** | 137 | **ready** | 3 | 13:12:54 | 0,54 h |
| sim.economy | done | 130 | done | 4 | 13:44:53 | 0,01 h |
| **sim.mining** | **queued** | 136 | **ready** | 3 | 13:11:53 | 0,56 h |
| ui.hud | done | 140 | done | 2 | 13:13:34 | 0,53 h |
| world.level | done | — | — | — | 2026-09-30 18:04:50 | 19,67 h |
| world.map | done | 129 | done | 4 | 13:44:53 | 0,01 h |

**Klíčové:** všechny čtyři `ready` úlohy mají `roadmap.updated_at` mladší
než `RETRY_HOURS = 3` → **guard je nevydá**. Nejbližší možný dispatch:
`entity.npc` **16:10:54**, `entity.enemy` **16:14:54**.

---

## 3. GitHub API (13:45–13:50 UTC), repo `ssevcikm-spec/uo-shadows`

```
repos/uo-shadows                     pushed_at=2026-10-01T13:13:31Z, default=main
actions/runs?per_page=100            total_count=400  (VŠECHNY běhy repa)
actions/workflows/agent.yml/runs     total_count=247  (běhy orchestra)
   posledních 100 podle conclusion: {"success":10,"failure":90}
   VŠECH 247: {"failure":211,"success":28,"cancelled":8}  → 11,3 % success
   rozsah: 2026-09-29T11:53:01Z .. 2026-10-01T13:11:08Z
   po dnech: 29. 9. 65/14 · 30. 9. 164/9 · 1. 10. 18/5
ci.yml/runs?branch=main              posledních 20: {"success":19,"failure":1}
   #88 success 10:44:43 807803e | #87 10:35:52 7a60d4e | #86 10:32:13 91b7e46
   #85 10:09:47 ec8f829 | #84 10:08:54 3016b39
   VŠECH 60 běhů ci.yml: 4 failure → #1 29. 9. 10:41 d8fbbcf · #2 29. 9. 11:58 b069d09
                                    #3 29. 9. 12:11 1bfa9e4 · #80 1. 10. 07:06 0519d1a
release.yml/runs                     #61 success 10:44:43 807803e (na témž commitu jako CI #88)
PR (posledních 27 zavřených)         24 sloučených, 2 zavřené bez sloučení, 2 otevřené
   merged_by: 24× null (GitHub nevrací u mergu přes GITHUB_TOKEN/API)
   nejnovější: Forge #138/#135/#134/#133/#130
větve hry                            main, forge/task-82, forge/task-134, forge/task-139, forge/task-140
```

### 3.1 Využití orchestry (Q1)

Metoda: sjednocení intervalů `[created_at, updated_at]` všech 247 běhů `agent.yml`.

```
okno:    2026-09-29 11:53:01 .. 2026-10-01 13:13:51  = 49,35 h
běželo:  6,86 h  = 13,89 % okna
bloků:   66 (souvislých časových úseků, kdy běžel aspoň jeden běh)
```

**Okna nečinnosti (> 0,5 h) a stav CI cíle v tu dobu:**

| # | od | do | hodin | stav CI na začátku | běhy CI během okna |
|---|---|---|---|---|---|
| 1 | 29. 9. 16:16 | 29. 9. 18:19 | 2,04 | #34 success | — |
| 2 | 29. 9. 18:32 | 30. 9. 05:45 | **11,20** | #36 success | #37–#41 success |
| 3 | 30. 9. 05:59 | 30. 9. 11:49 | **5,83** | #41 success | #42, #43 success |
| 4 | 30. 9. 12:11 | 30. 9. 13:34 | 1,39 | #43 success | #44 success |
| 5 | 30. 9. 16:30 | 30. 9. 22:29 | **6,00** | #71 success | #72, #73, #75 success |
| 6 | 30. 9. 22:41 | 1. 10. 01:31 | 2,85 | #75 success | — |
| 7 | 1. 10. 01:35 | 1. 10. 10:06 | **8,50** | #77 success | #79 success, **#80 failure**, #81 success |
| 8 | 1. 10. 10:10 | 1. 10. 13:08 | 2,98 | #84 success | #86, #87, #88 success |

```
součet oken nečinnosti: 40,79 h z 49,35 h = 82,7 %
```

**Nejdůležitější výsledek:** **cílové CI bylo během všech osmi oken ZELENÉ**
(v jednom okně proběhlo 3× a jednou selhalo, ale další běh byl zelený).
Vysvětlení „orchestra nic nedělá, protože má hra červené CI" tedy **pro tato
okna neplatí**. Co je blokovalo, je vidět v §2: **cooldown 3 h na granulích**.

### 3.2 Rozpad příčin selhání (Q2, Q3, Q7)

Metoda: u všech 240 běhů staženy joby a nalezen **první krok s `failure`**.

```
  95×  Agent nic nezměnil → hlásíme neúspěch
  82×  Testy hry (Godot headless)
  28×  USPECH (žádný krok neselhal)
  27×  Kontrola parsování (rychlá brána)
   7×  jiný: failure
   1×  jiný: cancelled
```

**Čas v kroku „Spusť agenta":**

```
úspěšné běhy (28):  průměr 139 s,  medián  75 s
selhané běhy (211): průměr  70 s,  medián  18 s
selhané běhy s krokem agenta < 30 s: 117 z 211 = 55 %
```

### 3.3 Kolik běhů na úlohu (Q2, S21)

```
úloh (task) celkem: 79;  běhů: 247;  průměr 3,13 běhu na úlohu
rozdělení (běhů na úlohu : počet úloh): {"1":20,"2":8,"3":29,"4":3,"5":12,"6":3,"7":1,"9":3}
úlohy s ≥ 3 běhy: 51; jejich běhů: 211 = 85 % všech běhů
MAX_ATTEMPTS = 5 (wrangler.toml:55) — úloh s VÍC než 5 běhy: 7
běhů v úlohách s > 5 běhy: 52 z 247 = 21 %
```

**Tasky překračující strop (detail):**

| task | běhů | od → do | výsledky |
|---|---|---|---|
| #85 | 6 | 29. 9. 15:51 → 16:13 | 3× cancelled, 3× failure |
| #86 | 6 | 29. 9. 15:51 → 16:11 | 3× cancelled, 3× failure |
| #109 | 6 | 30. 9. 14:02 → 14:28 | 6× failure |
| **#115** | **9** | 30. 9. 14:27 → 15:08 | 9× failure |
| **#116** | **9** | 30. 9. 14:28 → 15:10 | 9× failure |
| **#117** | **9** | 30. 9. 14:28 → 15:11 | 9× failure |
| #118 | 7 | 30. 9. 14:28 → 15:09 | 7× failure |

### 3.4 Mezery mezi pokusy téhož tasku (S21)

```
n = 168 mezer;  min 1,4 min · medián 3,2 min · max 514,1 min
mezer < 60 min: 158 (94 %)   mezer < 180 min: 158 (94 %)
nejkratší: #115 1,4 min (po failure), #119 1,5 min, #87 1,6 min (po cancelled)
```

**Tedy: retry uvnitř úlohy se nedrží `RETRY_HOURS` — běží v řádu minut.**

### 3.5 Ekonomie (Q3)

```
PR: 28 forge PR, 24 sloučených (86 %), 2 otevřené (Forge #139, #140), 2 zavřené bez sloučení (Forge #71, #82)
čas od PR k mergi: min 1,2 min · medián 1,6 min · max 169,1 min
```

**Volání modelu v jednom běhu (z logu):** `Tokens: 7.4k sent, 919 received` —
**jedno** volání na běh. Retry s druhým poskytovatelem se spouští jen když
`agent.log` **neobsahuje** rate-limit; jinak se kvóta šetří.

### 3.6 Parse gate — co modelu chybí (Q7, S19)

**Rozpad typů chyb u 27 běhů, které spadly na bráně parsování:**

| typ chyby | čeho se týká |
|---|---|
| `Identifier "Skills" not declared` | `scripts/skills.gd` **nemá `class_name`** — model si typ vymyslel |
| `Identifier "World" not declared` | `scripts/world.gd` v době běhu existoval, ale jako uzel, ne typ |
| `Could not find type "Economy"` | `economy.gd` **má** `class_name Economy`, ale model ho použil v souboru, který ho neměl načtený |
| `Could not find type "GameItem"` | `item.gd` **má** `class_name GameItem` — stejný případ |
| `Member "position" redefined (original in native class 'Area2D')` | konvence `CONVENTIONS.md` §1f — model ji nedodržel |
| `Cannot find member "ALIGN_LEFT" in base "Label"` | konstanta z Godotu 3 (běh #241) |
| `Invalid argument for "connect()" ... should be "Callable"` | Godot 3 → 4 |

**`class_name` v `games/uo-shadows/scripts/` (9 souborů):**

```
assist.gd       (ZADNY)   extends Node      2 func
attributes.gd   (ZADNY)   extends Node      2 func
combat.gd       (ZADNY)   extends (nic)     1 func
economy.gd      Economy   extends Node      4 func
game.gd         (ZADNY)   extends Node2D   23 func
item.gd         GameItem  extends Node      4 func
level.gd        (ZADNY)   extends (nic)    17 func
player.gd       (ZADNY)   extends Area2D    4 func
skills.gd       (ZADNY)   extends Node      3 func
```

**Kolik závislostí má `class_name` (tj. použitelnou smlouvu):**

```
ZMERENO: .gd souborů v závislostech granul = 21 výskytů,
         z toho BEZ class_name = 21
   level.gd (world.map ← world.level), attributes.gd ×5, skills.gd ×5,
   combat.gd ×2, player.gd ×3
```

**A co agent dostane (1. úroveň `owns` závislostí), vs. co existuje (2. úroveň):**

| granule | edituje | čte (1. úroveň) | NEČTE (2. úroveň) |
|---|---|---|---|
| sim.mining | mining.gd | skills.gd, world.gd, 5× json | level.gd |
| sim.crafting | crafting.gd | attributes.gd, item.gd, skills.gd, 5× json | — |
| entity.npc | npc.gd | economy.gd, item.gd | 5× json |
| entity.enemy | enemy.gd | combat.gd, item.gd | attributes.gd, skills.gd, 5× json |
| sim.offline | offline.gd | combat.gd, crafting.gd, mining.gd, skills.gd | attributes.gd, item.gd, world.gd, 5× json |
| persist.save | save.gd | attributes.gd, economy.gd, player.gd, skills.gd, world.gd | item.gd, level.gd, 5× json |

### 3.7 Model: zdvojený prefix (S26)

```
workflow posílá:  aider --model "openai/${FORGE_MODEL}"
FORGE_MODEL:      openai/gpt-oss-120b   (z providers.json)
→ aider dostane:  openai/openai/gpt-oss-120b
log aideru:       Warning for openai/openai/gpt-oss-120b:
                  Unknown context window size and costs, using sane defaults.
```

### 3.8 Roadmapa: soubor vs. D1 (Q10)

```
D1 (GET /roadmap): 14 řádků, z toho 10 'done'
soubor (roadmap.json): 18 granul, z toho 2 s done:true
jen v D1: 0     jen v souboru (nemá řádek v D1): 4
   → core.attributes, entity.item, sim.offline, engine.shell
```

### 3.9 Instalace šablony do nového repa (Q5, Q6, S23)

Simulace `Copy-Item repo\.forge\* → cíl` + `repo\.github\*` + kořenové soubory
(32 souborů):

```
NAZEV-REPA    2 soubory, 5 výskytů   (.forge/node/termux-setup.sh ×2, .github/workflows/release.yml ×3)
uo-shadows    6 souborů, 12 výskytů  (baseline.py, check-schema.py ×4, vision-profile.json ×2,
                                      agent.yml ×2, 2× __pycache__)
forge-quest   1 soubor,  2 výskyty   (release.yml — text o opravě)
ssevcikm-spec 3 soubory, 4 výskyty   (termux-setup.sh, pick-provider.mjs, release.yml ×2)
gameforge     0

absolutní cesty v novém repu: 3 (.forge/node/.env 1×, 2× __pycache__)
odkazů na soubory, které v novém repu NEJSOU: 12
   assets/spec.json, assets/levels/main.json, manifest.json, level.gd, world.gd,
   enemy.gd, game.gd, tests/run_tests.gd, scripts/neco.gd, baseline.json, spec.json, main.json

roadmap.json v novém repu: grains = 0
vision-profile.json: 9 dokumentačních klíčů (_x) + 11 konfiguračních, hra = null
.gitignore: GENERUJE ho instalátor (Set-Content :165), v repu není
```

**release.yml v novém repu (řádky 82, 86, 143):**
`echo "- v prohlížeči: https://ssevcikm-spec.github.io/NAZEV-REPA/"`
`echo "> V \`NAZEV-REPA\` musí být název TOHOHLE repa …"`
`run: echo "Web se nasadí na https://ssevcikm-spec.github.io/NAZEV-REPA/"`

### 3.10 Soubory existující v šabloně i ve hře (O2, O7)

```
ZMERENO: souborů existujících v obou = 27
         bajtově SHODNÝCH = 19,  ROZDÍLNÝCH = 8
ROZDÍLNÉ: termux-setup.sh (4641/4591 B), vision.test.mjs (17576/13318 B),
          roadmap.json (3140/16270 B), vision-profile.json (4380/2588 B),
          agent.yml (34819/34870 B), ci.yml (8825/8729 B),
          release.yml (6464/6185 B), .gitattributes (787/…)
kontrola-driftu.mjs hlídá 12 cest z těch 27
```

### 3.11 Inventura (Q9, O4)

```
git ls-files orchestra        = 114
git ls-files orchestra/repo   =  27   (šablona: .forge 18, .github 4, .gitattributes, CONVENTIONS.md)
git ls-files tools            =  70
na disku (mimo generované)    = 126 → netrackováno 12:
   .env, 6× .secrets/, repo/.forge/node/.env, provider.env, provider.json, 2× Godot .exe
nástrojů v tools/ (soubory)   =  70;  z toho NIKDE nezminěných = 18:
   analyza-aider, analyza-aktualni, analyza-logu, analyza-modelu, analyza-testy,
   analyza-verdikt, detail-behu, diag-baseline, dopln-attempt, mer-sklon-hranice,
   mereni-chyb, mereni-modelu, mereni-pltvani, mereni-pred-po, overit-razeni,
   pridej-eskalaci, repo-files, telegram-chat-id
absolutní cesty ve stromu orchestra: 73 výskytů v 55 souborech
endpointů conductora          =  17
SQL řádků v index.ts          =  90
index.ts                      = 1368 řádků, 67 776 B, sha256 08d1748dff8d
```

---

## 4. SQL důkaz (úroveň 2) — invariant 15

`python _analyza/hl-sql.py` — bere **doslovné znění dotazu ze zdroje**:

```
guard (index.ts:786-792):
  SELECT * FROM tasks WHERE status='ready' AND target='cloud'
    AND NOT EXISTS (SELECT 1 FROM roadmap rm
                    WHERE rm.task_id = tasks.id
                      AND rm.updated_at > datetime('now', ?))
   ORDER BY id LIMIT 25
```

| # | scénář | očekáváno | naměřeno |
|---|---|---|---|
| 1a | nová granule (`updated_at = now`) | `[]` | `[]` |
| 1b | týž řádek starý 4 h | `[1]` | `[1]` |
| 2 | nová granule s `updated_at = NULL` | `[1]` | `[1]` |
| 3a | selhalo (updated_at = now) | `[]` | `[]` |
| 3b | selhalo před 3 h 1 min | `[1]` | `[1]` |
| 4 | řádek roadmapy ukazuje na nový úkol, starý je `running` | guard vidí **jen nový** | `[2]` |
| 4b | na jednu granuli dva aktivní úkoly | 2 | 2 |
| 5 | úkol bez řádku v roadmapě | guard ho **propustí** | `[1]` |
| 7 | 30 připravených úloh | `LIMIT 25` → 25 | 25 |

```
VÝSLEDEK: 0 chyb
```

**Mutační test (`python _analyza/hl-mutace.py`) — umí ten test spadnout?**

```
0) zdravý kód                       exit=0  (očekáváno 0)
1) guard se ptá na rm.status        exit=1  → CHYCENO
2) guard kontroluje jen status      exit=1  → CHYCENO
3) guard bez LIMIT 25               exit=1  → CHYCENO
VÝSLEDEK: 3/3 vad chyceno
```

### 4.1 Živý důkaz invariantu 15 (13:43 UTC)

`entity.enemy`: úloha **#141 založena 10:09:14**, první (a jediné) běh
**#245 v 13:10:09**, tedy **o 3 h 1 min později**. Mezitím byly 10:10–13:08
**2,98 h bez jediného běhu** a CI cíle bylo celou dobu zelené (§3.1, okno 8).

---

## 5. Konfigurace (O2, O3, S22)

```
vision-profile.json — klíče, které KÓD čte (vision.mjs):
   čte:    hra, popis_stylu / styl_popis, ocekavany_obsah, zakazy_v_promptu /
           zakazy, poskytovatele, cache, self_consistency, strict_poskytovatele
   nečte:  stropy (0× ve vision.mjs)
   šablona má 9 dokumentačních klíčů (_popis, _hra, _mapa, …) vedle konfiguračních
   hra má jiný tvar: styl_popis místo popis_stylu, žádné zakazy (má zakazy_v_promptu)

mrtvá pole granule v KÓDU (komentáře odstraněny):
   acceptance   0 souborů
   provides     0 souborů (v souboru hry je 3× jen jako data)
   done_note    0 souborů
   kind         conductor ho jen uloží do tasks.kind a pošle do workflow;
                agent.yml ho použije jen v šabloně PR komentáře

providers.json: šablona i hra bajtově SHODNÉ (4644 B, sha 4b5caae0aa)
   hra ho stahuje za běhu: raw.githubusercontent.com/ssevcikm-spec/forge-orchestra/
                           main/repo/.forge/providers.json  (pick-provider.mjs)

.env soubory:
   orchestra/repo/.forge/node/.env    523 B  (FORGE_URL, FORGE_SECRET, FORGE_WORKER,
                                              FORGE_KINDS, FORGE_GODOT) — NETRACKOVANÝ
   orchestra/repo/.forge/provider.env 196 B  — NETRACKOVANÝ
   orchestra/repo/.forge/provider.json 177 B — NETRACKOVANÝ
   games/uo-shadows/.forge/node/.env  NEEXISTUJE
   games/uo-shadows/.forge/provider.env NEEXISTUJE
```

---

## 6. Brány a workflowy

```
ci.yml (182 řádků, 15 kroků, 2× continue-on-error)
   name: CI (testy a build) — jobs.test-and-build.name: "Testy a build"
   TVRDÉ: import → check-schema (Pillow!) → testy → check-assets (Pillow)
          → check-wiring → smoke ("SCRIPT ERROR") → verify-level-render
   PORADNÍ: vision (continue-on-error, || echo), upload artifact
   on: push main, pull_request, workflow_dispatch — BEZ paths filtrů

agent.yml (691 řádků, 27 kroků, 2× continue-on-error)
   inputy: task_id, run_key, kind, title, prompt, max_lines, model, grain, attempt
   auto-merge gate (krok :595-645):
       1) cesta musí být scripts/* nebo assets/* → jinak ok=0
       2) tests/*, .github/*, .forge/*, project.godot → ok=0
       3) *.import|*.uid se PŘESKAKUJÍ (dřív než kontrola složky) — ale case pro
          složku je PŘED tím, takže .import v tools/ nastaví ok=0
       4) add+del > inputs.max_lines → ok=0
       5) "Počkej, až testy nezávisle potvrdí CI" — hledá check-run
          jménem "Testy a build", 30× po 20 s = max 10 min, pak ci=timeout
       6) Sloučit: jen když gate.ok=1 && ci=ok
```

```
release.yml v HEAD (6464 B): NAZEV-REPA 3×
release.yml v pracovním stromu (7901 B, mtime 13:48:20 UTC): NAZEV-REPA 0×,
   github.repository 5×  → opravila jiná session, NECOMMITNUTO
```

---

## 7. LGTM baseline (S25)

```
verze=1, schváleno=2026-09-30T23:07:32+00:00, prompt_verze=null
_ceka_na_lgtm=true
_stav="PŘEVZATO AGENTEM 30. 9. 2026 – čeká na lidskou kontrolu. …"
položek = 272
podle složky: assets/sprites 16, tools/blender 256
schvalil: {"agent-init": 272}      ← všechny položky, jediná hodnota
čas schválení: 2026-09-30T23:07:31 .. 23:07:32  (jediná minuta)
položek s poznámkou "čeká na lidskou kontrolu": 272
```

**A kde se cache použije:** `baseline.py:203` vrací `{"v_cache": false,
"duvod": "mimo repo hry"}`, když obrázek není v repu; `ci.yml:128` píše snímek
do `/tmp/frames` → **v CI cache neplatí nikdy** (to už je v analýze jako S10).

---

## 8. Ověření tvrzení z dokumentace — kde jsem se spletl já

| # | tvrzení | zdroj | naměřeno | verdikt |
|---|---|---|---|---|
| A | „main hry byl 7,5 h červený" | skill `orchestra` inv. 19 | poslední okno červeného CI: #80 (1. 10. 07:06) → **2,96 h**; dřívější: **1,53 / 0,25 / 0,04 h** | **nepotvrzeno** (nejdelší naměřené okno je 2,96 h) |
| B | zdroj pravdy o roadmapě | — | D1 14 řádků / soubor 18 granul / 4 chybí v D1 / 8 bez `done` | nové měření |
| D | „providers.json se čte za běhu" | skill `orchestra` | `pick-provider.mjs` **ANO** (raw.githubusercontent.com) | **potvrzeno** (můj první test hledal v jiném souboru) |
| E | „release.yml odvozuje odkaz z názvu repa (F0)" | skill `orchestra`, HEAD `525d45b` | **HEAD má `NAZEV-REPA` 3×**, `github.repository` 0×; pracovní strom má 0×/5× | **v HEAD neplatí**, opraveno necommitnutě 13:48 |
| F | „zámek `owns` opraven (`locked.add(lockKeys…)`)" | skill inv. 17 | řádky s `lockKeys(`: **282, 538, 765, 795**; přesné znění se liší od citace v dokumentaci | **potvrzeno**, citace v dokumentaci je nepřesná |
| I | „vision je jen v ci.yml, agent ho nedostane" | vlastní domněnka | `vision.mjs:210-213` čte `DEEPSEEK_API_KEY` a volá `api.deepseek.com` | **moje domněnka byla chybná**, kód je složitější |
| K | LGTM baseline: 272 položek, samé sprity | skill `orchestra` | 272 = 16 spritů + **256** z `tools/blender/sprites` | **potvrzeno** |
| — | „36/36 vision testů v šabloně" | HANDOFF | v sandboxu `workspace-write` **EPERM** (`spawn`) — neměřeno | **neměřeno** (viz §10 analýzy) |

---

## 9. Co se v sandboxu `workspace-write` NEDALO změřit

```
games/uo-shadows  → node .forge/node/vision.test.mjs   EPERM (spawn)   [HANDOFF: 28/28]
orchestra/repo    → node .forge/node/vision.test.mjs   EPERM (spawn)   [HANDOFF: 36/36]
orchestra/repo/.forge/baseline.py testy                PermissionError WinError 5
                                                       (temp dsh-DqwvpS) [HANDOFF: 24/24]
```

Podle `AGENTS.md` to **není vada testů** — potřebují širší oprávnění.
V analýze jsou tato čísla **označena jako neměřená**, nepřebírám je jako fakt.

---

## 10. Změny, které v průběhu měření provedla JINÁ session

```
13:43 UTC  git status orchestra:  M README.md
13:52 UTC  git status orchestra:  M README.md
                                  M repo/.github/workflows/release.yml   (mtime 13:48:20)
                                  D tools/kontrola-schematu.py           (smazán)
                                  M tools/test-cooldown.py               (mtime 13:46:18)
                                  M tools/validate-all.mjs               (mtime 13:46:35)
```

**Ověřeno spuštěním (13:57 UTC, pracovní strom):**

```
node tools/validate-all.mjs → "✗ NALEZENO 4 PROBLÉMŮ", exit=1     (HEAD: vždy exit 0)
python tools/test-cooldown.py → "VÝSLEDEK: 10 kontrol, 1 chyb", exit=1
                                (čte skutečný SQL ze zdroje; 1 chyba = S12, známá vada)
```

**Důsledek pro analýzu:** vše, co je v analýze označeno **„HEAD"**, platí pro
commit `525d45b`. Co je označeno **„pracovní strom"**, platí k 13:57 UTC.
Analýza u každého tvrzení o stavu uvádí, které z toho to je.

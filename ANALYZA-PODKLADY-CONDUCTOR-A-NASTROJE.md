# Podklady k analýze architektury orchestra

> **Co tenhle dokument JE:** analýza. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Co to je:** surové, samostatně použitelné výsledky dvou hloubkových auditů,
které byly podkladem pro `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`. Ten dokument
cituje nálezy odsud; tenhle soubor je drží **celé**, aby se při předání
neztratily.

**Kdo to dělal:** session z 1. 10. 2026 (stejná jako hlavní analýza).
Audity běžely **paralelně jako podagenti** a pak byly nejsilnější nálezy
**nezávisle reprodukovány** v hlavní session. Nic nebylo změněno ani
pushnuto; vše je čtení a offline měření.

**Proč odděleně:** hlavní dokument má být rozhodnutí, ne inventura. Tenhle
soubor je inventura — a má ji být vidět, protože **každý nález je ověřitelný
jen s tím, na kterém řádku stojí**.

---

## Část 1 — Conductor (`orchestra/conductor/src/index.ts`, 1359 řádků)

### 1.1 Pořadí kroků v jednom tiku (`tick`, `:672`)

| # | Řádky | Co dělá |
|---|---|---|
| 0 | `:689` | `pollRuns` — výsledky běžících cloudových úloh z GitHubu |
| 0b | `:693` | `escalateStuckTasks` — watchdog (jen notifikuje) |
| 1 | `:696-700` | běhy `running` starší než `STALE_MINUTES` → `timeout` |
| 1 | `:707-711` | jejich úkoly zpět na `ready`, **jen dokud `attempts < maxAttempts`** |
| 1 | `:712-716` | zbytek → `failed` |
| 1a | `:720-725` | re-block úloh, jejichž běh je `abandoned` |
| 1b | `:730` | `roadmapTick` — doplní granule z roadmap všech aktivních her |
| 1c | `:742-746` | zombie invariant: úkol bez řádku v `roadmap` → `blocked` |
| 2 | `:764-841` | dispatch smyčka (kapacita `MAX_CONCURRENT`, zámky, cooldown, claim) |

Dispatch na GitHub: `:189` `POST /repos/{repo}/actions/workflows/{workflow}/dispatches`.

### 1.2 Naměřené vady (reprodukované v hlavní session)

**N1 — nová granule se 3 h nevydá.** `roadmapTick:643-646` zakládá řádek
roadmapy s `updated_at = datetime('now')`; dispatch `:796-804` se ptá **jen na
čas**:

```sql
SELECT * FROM tasks WHERE status='ready' AND target='cloud'
   AND NOT EXISTS (
     SELECT 1 FROM roadmap rm
      WHERE rm.task_id = tasks.id
        AND rm.updated_at > datetime('now', ?)     -- bind: -3 hours
   )
 ORDER BY id LIMIT 25
```

Replika obojího SQL v SQLite — **celý skript** (bez sítě, bez orchestra,
spustitelný kdekoli s Pythonem; při analýze byl v `.tmp\cooldown-test.py`
a po ověření uklizen, proto je zde):

```python
import sqlite3
db = sqlite3.connect(":memory:")
db.executescript("""
CREATE TABLE tasks (id INTEGER PRIMARY KEY AUTOINCREMENT, status TEXT DEFAULT 'ready',
                    target TEXT DEFAULT 'cloud', attempts INTEGER DEFAULT 0);
CREATE TABLE roadmap (item_id TEXT PRIMARY KEY, task_id INTEGER, status TEXT DEFAULT 'queued',
                      updated_at TEXT);
""")
RETRY_H = 3
def dispatch():
    return db.execute("""
      SELECT id FROM tasks WHERE status='ready' AND target='cloud'
        AND NOT EXISTS (SELECT 1 FROM roadmap rm WHERE rm.task_id = tasks.id
                          AND rm.updated_at > datetime('now', ?))
       ORDER BY id LIMIT 25""", (f"-{RETRY_H} hours",)).fetchall()

# A) přesně to, co dělá roadmapTick (:643-646)
db.execute("INSERT INTO tasks (status) VALUES ('ready')")
db.execute("INSERT INTO roadmap (item_id, task_id, status, updated_at)"
           " VALUES ('h/g1', 1, 'queued', datetime('now'))")
print("A) NOVA granule -> dispatch:", dispatch())

# B) týž řádek starý 4 hodiny
db.execute("UPDATE roadmap SET updated_at = datetime('now','-4 hours') WHERE item_id='h/g1'")
print("B) stary 4 h     -> dispatch:", dispatch())

# C) /report: opakovatelné selhání -> jen tasks, roadmapy se NEDOTKNE (:1329-1336)
db.execute("UPDATE tasks SET status='ready', attempts=attempts+1 WHERE id=1")
print("C) po /report    -> dispatch:", dispatch())
```

| stav | výsledek |
|---|---|
| A) nový úkol + řádek roadmapy založený jako v `roadmapTick` | `[]` — **nevydá se** |
| B) týž řádek posunutý o 4 h zpět | `[(1,)]` — vydá se |
| C) po `/report` u opakovatelného selhání | `[(1,)]` — **cooldown se obchází** |

Vzniklo opravou `621c312` (30. 9. 2026), která z guardu odstranila
`rm.status = 'failed'` — to bylo správné (polling zapisuje `'queued'`), ale
guard tím začal chytat i **čas založení** řádku.

**N2 — `/report` cooldown neobnoví.** `:1329-1336`: u opakovatelného selhání
se zapíše **jen `tasks`**; `roadmap.updated_at` se zapíše jen v terminální
větvi (`nextStatus === 'failed'`). `pollRuns` totéž dělá správně (`:403-405`).

**N3 — strop a watchdog jsou na špatné entitě.** `MAX_ATTEMPTS` se čte na
`:328`, `:394`, `:679`, `:709`, `:1329` → **není mrtvý kód** (komentáře
`:31-33` a `:233-235` tvrdí opak a jsou zastaralé). Ale `roadmapTick` zakládá
pro každý retry **nový úkol s `attempts = 0`** (`:634-640`; `attempts` se
nikde nepřenáší). Watchdog `ESCALATE_AFTER = 8` (`:246`) > `MAX_ATTEMPTS = 5`
a počítá **běhy úkolu** (`:251`) → **nikdy nedosáhne prahu**.

**Rozbitý zámek.** `:774-776` staví `locked` z **holých jmen**:

```js
for (const r of runningRows.results || []) {
  for (const f of (JSON.parse(r.payload || "{}").owns || [])) locked.add(f);
}
```

ale `:806` porovnává s **repo-scoped** klíči:

```js
!lockKeys(t.payload, env).some((k) => locked.has(k))   // lockKeys → `${repo}/${f}` (`:308`)
```

`"owner/repo/scripts/x.gd"` nikdy nenajde `"scripts/x.gd"` → **zámek
neblokuje nic**. V `roadmapTick` je tatáž dvojice správně (`:558` vs. `:625`).

### 1.3 Další cesty, kde může úloha tiše zůstat viset

| Místo | Co se stane |
|---|---|
| `:707-711` | poddotaz na `runs.status='timeout'` **není časově omezený** → vyprší-li jinde jiný běh, přepíše se i úkol, jehož současný běh běží → duplicitní dispatch |
| `:826-833` | neúspěšný dispatch → úkol `ready` **bez ohledu na `attempts`**, běh `dispatch_failed`, který `pollRuns` nečte (`:332`) → opakuje se každý tik bez stropu |
| `:813` vs `:819` | tik umře mezi claimem a insertem běhu → úkol `running` **bez běhu** navěky (uklidí jen ruční `/tasks/cleanup`, `:1208-1212`) |
| `:624,627,653` | granule, která nikdy nesplní `depends_on`, není hlídaná nikde (watchdog vidí jen existující úkoly) |
| `:386,395` | `pollRuns` **nekontroluje `blocked`/`done`** (na rozdíl od `/report:1326` a `:1327`) |
| `:1315-1320` | úspěch se zpracuje **dřív** než guard `blocked`/`done` (`:1326` je jen v `else` větvi) → pozdní úspěch přepne `blocked` úlohu na `done` |
| `:342` | `per_page=50` bez stránkování |
| `:943-945` | `/failed` čte `status='failed'`, ale zombie invariant úlohy přesouvá na `blocked` → **fronta selhání se po ~3 h sama vyprázdní** |

**Co naopak díra NENÍ** (aby nevznikaly falešné poplachy): `runs.status='running'`
nemůže zůstat navěky (`:696-700` ho po 90 min přepíše); `blocked` úloha se
nedispatchuje (dispatch i `claim` filtrují `status='ready'`).

### 1.4 Co je vázané na jednu hru

- `repoOf` fallback `:292-300` → `env.GITHUB_REPO`; totéž `lockKeys:307`.
- `listGames` fallback `:447-454` → `[{game_id:"default", repo: env.GITHUB_REPO}]`,
  když je registr prázdný. **Důsledek:** vypnutí poslední registrované hry
  orchestra nezastaví; a `/tasks/cleanup` (`:1120,1130,1174,1184`) pak bere
  jen aktivní hry → **smaže cache roadmapy** (`:1184`) a zablokuje úlohy —
  přestože `:1107-1108` radí právě „nejdřív hru vypni, pak cleanup, pak zapni".
- `ROADMAP_MAX_PRS` je **součet přes všechny hry** (`:538-547`).
- Globální: `MAX_CONCURRENT`, `RETRY_HOURS`, `STALE_MINUTES`, `MAX_ATTEMPTS`,
  `ESCALATE_AFTER`, `WORKFLOW_FILE` (tabulka `games` sloupec `workflow` nemá,
  `schema.sql:73-79`).
- Watchdog (`:263-271`) a `/roadmap` (`:930-936`) nenesou `game_id`.
- `/tasks/cleanup` čte roadmapu z natvrdo `main` (`:1125`), ignoruje `GITHUB_REF`.

**V pořádku:** `item_id = {game_id}/{grain_id}` (`:589,630`), `mergedTitlesByRepo`
(`:492,507`), zámky v `roadmapTick` (`:625`), přeskočení nečitelné roadmapy
jedné hry (`:576-579`).

### 1.5 Mrtvé reference a stavy, které nikdo nečte

- `:1083` odkazuje na **`syncWithRoadmap`** — funkce v repu **neexistuje**.
- `roadmap.status='queued'` (`:646`) — **nikde se nečte**.
- `runs.status='dispatch_failed'` (`:829`) — jen text v `/status`.
- Zastaralé komentáře: `:1039-1041` (reset úkolů — implementace jen maže),
  `:419-423` („jen po jedné položce" — smyčka zakládá všechny připravené),
  `:905` („tik každých 15 min" — cron je každou minutu),
  `:1352-1357` (výčet endpointů neúplný).
- `gameforge` / `forge-quest` / `uo-sandbox` / `forge.cmd` / `--router`
  v `index.ts` **nejsou** (jen dva komentáře s naměřenými čísly: `:1095`, `:1118`).

### 1.6 Co conductor neměří o sobě

- `tools/test-cooldown.py` — SQL **opsané jako řetězce** (`:39` obsahuje
  i starou verzi `rm.status = 'failed'`), **žádný assert ani `sys.exit`** →
  končí vždy 0; scénář `:57` tvrdí „řádek je done", ale vkládá `queued`.
  Nerozlišuje „řádek je mladý, protože selhal" od „řádek je mladý, protože
  vznikl" → **vůči N1 slepý** a scénářem 6 ho posvěcuje.
- `tools/test-eskalace.py` — `:19` `PRAH = 8` natvrdo, `:45` „Zjednodušená
  kopie logiky z conductora"; scénáře `:69-78` podávají 8–20 běhů na úkol =
  **nedosažitelný stav** → N3 nechytí.
- `tools/mock-conductor.mjs` — neumí `/tick`, `/poll`, `/roadmap`,
  `/roadmap/reset`, `/tasks/cleanup`; jeho `/report` (`:126`) nemá strop ani
  ochranu `blocked`/`done`.
- `validate-all.mjs` se na `index.ts` dívá **jen bajtovým porovnáním**
  s kopií v repu (`:58-70`), ne logikou; z konfigurace kontroluje jen
  **přítomnost** (`:53-54`, `ESCALATE_AFTER` tam není vůbec).
- Ani jeden z těch dvou `.py` testů **není součástí žádné brány** — spouští
  se ručně.

---

## Část 2 — Nástroje orchestra (`orchestra/tools/`)

### 2.1 Inventura a git

**měřeno:** `git ls-files tools/` = **24 trackovaných**;
`git status --porcelain tools/` = **51 untracked** + 3 modifikované;
celkem **75 souborů** (40 `.mjs`, 32 `.py`, `git.cmd`, `gitconfig`,
`test-local.ps1`) + `tools/godot/` (2 binárky, 181 MB, untracked správně).

`git log --diff-filter=D -- tools/` = prázdný → **nikdy v gitu nebyly**.
`git ls-remote origin` = jediná větev `main` @ `a860830` = lokální HEAD →
**nejsou ani na GitHubu**.

**24 untracked, ale trvalých nástrojů** (nález — projekt je používá nebo je
dokumentace předepisuje): `git.cmd`, `gitconfig`, `status.mjs`,
`validate-all.mjs`, `kontrola-schematu.py`, `test-check-schema.py`,
`check-licence.py`, `test-licence.py`, `asset-fetch.mjs`, `zjisti-pages.mjs`,
`oprav-ps1-kodovani.py`, `kontrola-diakritiky.py`, `test-ci-workflow.mjs`,
`cancel-stale-runs.mjs`, `roadmap-reset.mjs`, `tasks.mjs`, `stahni-patch.mjs`,
`log-usek.mjs`, `compare-game.mjs`, `stav-conductora.mjs`,
`kontaktni-arch.py`, `start-orchestra.mjs`, `push-conductor.mjs`,
`inventura-vize.py`.

**27 untracked jednorázových** (osm `analyza-*`, čtyři `oprav-check-schema*`,
`mereni-*`, `overit-*`, `migrace-schema.py`, …).

**Stejná vada mimo `tools/`:** untracked jsou i `repo/.forge/check-schema.py`,
`repo/.forge/baseline.py`, `repo/.forge/vision-profile.json`,
`repo/.forge/node/vision.test.mjs`, `assets/asset-registry.json`,
`ASSETY.md`, `ASSETY-PLAN.md`.

### 2.2 Jsou jednorázové záplaty ještě potřeba?

**Ani jedna z deseti nesahá na neexistující soubor** (`Test-Path` všech
14 cílových cest). Všechny jsou idempotentní (mají guard) — **kromě
`migrace-schema.py`**, které `main.json` (`:54-68`) a `levels/manifest.json`
(`:71-81`) přepisuje **vždy**; dnes je to no-op jen díky tomu, že soubory už
v tom formátu jsou. → **Všech deset je hotových a má se smazat.**

**Zásadní nález:** premisa záplat „tři kopie téhož souboru" **neplatí**.

| soubor | hash | řádků |
|---|---|---|
| `orchestra/repo/.forge/check-schema.py` | `F304E787…` | 461 |
| `games/uo-shadows/.forge/check-schema.py` | `F304E787…` | 461 |
| `orchestra/tools/kontrola-schematu.py` | `20741E2B…` | **305** |

Kopie v `tools/` je **jiná a starší** — chybí jí `_popis_bunky`,
`_deklarace_cell`, `_cisla_wh_z_gd` i hlášení mrtvé větve `world.gd`.
Komentář `oprav-check-schema.py:20` („zdrojový nástroj v orchestra/tools je
tentýž soubor") je **nepravda** — kdo by podle něj „sjednotil tři kopie", může
z `tools/` přetáhnout starší chování a zahodit hlášení mrtvé větve.
**A přesně tuhle starou kopii pouští `validate-all.mjs:186`.**

### 2.3 Mrtvé odkazy a historické zbytky

- **`forge-quest` (10 výskytů v 5 souborech) — žádný mrtvý odkaz.**
  `zjisti-pages.mjs:47-48` je **funkční API dotaz s ošetřeným 404**;
  `verify-setup.py:18-22,30` a `over-dokumentaci.py:273` jsou záměrné;
  `install-into-repo.ps1:13-15` a `release.yml:88,141` jsou komentáře
  vysvětlující opravu. (V **gitu** je ale `release.yml:82,135` ještě stará
  verze — viz hlavní analýza S2.)
- **`gameforge` (7):** `tools/git.cmd:4` — **jediná nápověda k použití je mrtvá
  cesta**; `over-dokumentaci.py:120,152` — kontrola **vyžaduje**, aby
  dokumentace mrtvou cestu zmiňovala (brání úklidu);
  `test-local.ps1:34-36` je **mrtvý předpoklad layoutu** (z `$forge` počítá
  `:39` a `:54`), ne jen komentář.
- **`forge.cmd`:** `install-into-repo.ps1:86` — **mrtvý návod v chybové
  hlášce** (posílá člověka zachránit práci agenta neexistujícím příkazem);
  `test-local.ps1:42` + `:39,54-57,61` — mrtvé cesty, skript spadne dřív, než
  něco udělá, **a je v gitu**.
- **`--router`: 0 výskytů.** `verify-setup.py:11,75` ale vede `router` mezi
  **očekávanými** složkami.
- **`worker.mjs:83`** (šablona i hra): `FORGE_CMD` default míří na
  `C:\Users\Ssevc\Local-Deepseek\forge.cmd` (neexistuje; `path.join` čtvrté
  `..` nezkrátí) → krok `forge:` (`:228`) je nepoužitelný.
- **Absolutní cesty:** 76 výskytů — 68 v `tools/` (35 souborů), 2 v komentáři
  `install-into-repo.ps1`, **0 v `bin/`, `conductor/`, `repo/` a ve všech
  `*.md`**. **Nepřenosných je 57 ze 72 skriptů.** Dále 4 soubory míří na
  `C:\Users\Ssevc\.dsh\skills` (`kontrola-diakritiky.py:27-31`,
  `over-skilly.py:9`, `over-dokumentaci.py:12`, `zapis-dokumentaci.py:15`).
- `prehled-pokusu.mjs` čte `.tmp/tasky.json` — **soubor neexistuje**.

### 2.4 Kolik nástrojů je vázaných na jednu hru

**Pipeline je čistá:** v `conductor/` jen `wrangler.toml:28` + komentář
`schema.sql:74`; v `repo/` (šablona) **0 výskytů** `uo-shadows`.

**Lokální nástroje: 47 ze 75 souborů má hru zapsanou v kódu.**

| kategorie | příklady | cena opravy |
|---|---|---|
| triviální (1–3 řádky) | `analyza-*.mjs` (11), `mereni-*`, `overit-*`, `detail-behu`, `log-usek`, `stahni-patch`, `compare-game:7,8`, `prehled-pokusu:5` | vzít z argv/registru |
| jednostavové seznamy | `kontrola-driftu.mjs:37`, `sync-sablona-hra.py:20`, `test-ci-workflow.mjs:33`, `verify-setup.py:11,46`, `test-check-schema.py:44`, `lint-roadmapa.py:23`, `simulace-dag.py:13`, `stav-dag.py:11`, `kontrola-diakritiky.py:24` | 1–2 řádky |
| **tiché lži, když se neudělají** | `validate-all.mjs:5-8` (+9 míst), `zjisti-pages.mjs:63,77,89`, `start-orchestra.mjs:6,46,52`, `reset-dry.mjs:24` | parametrizovat — jinak by ověření druhé hry tvrdilo, že měří `uo-shadows` |
| záměrně zatvrzelé | `oprav-check-schema*.py`, `oprav-verify-iso.py:30`, `oprav-testy-get.py:24`, `oprav-prompt-skills.py:13`, `migrace-schema.py:28` | nechat (a smazat) |

**Vzor, jak to má vypadat:** `status.mjs:18` — hru má jako **pojmenovaný
default** a registr čte z conductora.

---

## Část 3 — Domácí uzel (`orchestra/repo/.forge/node/worker.mjs`, 415 řádků)

### 3.1 Kroky, které worker umí

| krok | co dělá | řádky | dnes použitelné |
|---|---|---|---|
| `shell:<cmd>` | libovolný příkaz, **vždy se ptá y/N** | `:211-212, 300-310` | ano (interaktivně) |
| `godot-import` | `--headless --path . --import` | `:213-214` | ano |
| `godot-test` | `--script res://tests/run_tests.gd` | `:215-216` | jen když hra ten skript má |
| `godot-export:<preset>:<out>` | `--export-release` | `:217-223` | neověřeno |
| `python:<arg>` | `python` / `python3` | `:224-225` | ano |
| `forge:<arg>` | `FORGE_CMD <arg>` | `:226-228` | **NE — mrtvé** |
| `make-dir:<slozka>` | mkdir v klonu | `:292-296` | ano |
| `blender:` | — | **neexistuje** (výčet `:210-232`) | skládá se přes `shell:` (a ten se ptá) |

### 3.2 Nálezy

- **`FORGE_CMD`** = `process.env.FORGE_CMD || join(HERE,'..','..','..','..','forge.cmd')`
  (`:83`) → `C:\Users\Ssevc\Local-Deepseek\forge.cmd`, **neexistuje**
  (ověřeno `Test-Path`; `gameforge\` je jen v komentáři `:28,80-82`, složka
  taky neexistuje). Krok `forge:` je nepoužitelný a `--info` (`:382`) vypisuje
  neexistující cestu.
- **Bezpečnost:** `shell:` se vždy ptá (`:300-310`); `--no-shell` ho přeskočí
  a úkol **shodí** (`:301-303`), nikdy nespustí. Ale kdokoli se `FORGE_SECRET`
  může zařadit úkol s `kind` z `FORGE_KINDS` a krokem `python:`/`godot-test`
  → spustí kód **bez potvrzení** (`FORGE_KINDS` filtruje druh, ne kroky).
  A v bezobslužném běhu `ask()` **visí navěky** (čeká na stdin).
- **Chyby:** `fail()` (`:264-265`) se volá na `:285,303,308,317,321`; report
  se posílá vždy (`:360-369`). **Když report selže, není retry** — `api()`
  hodí (`:164`), `cycle()` spadne, `--once` skončí **s kódem 0** (`:403-406`).
  Úloha zůstane `running`, ale conductor ji po `STALE_MINUTES` (90 min) vrátí
  → **nevisí věčně, jen se práce dělá znovu**.
- **Timeouty:** `runCmd` default **1 h** (`:170`), volán bez argumentu (`:311`);
  SIGTERM zabije jen shell (`:174-176`), ne potomky. **`api()`/`fetch` timeout
  NEMÁ** (`:155-166`) → nedostupný conductor = worker visí navěky.
- **Konfigurace:** `.env` vedle skriptu (`:55-64`), prostředí má přednost.
  Chybí-li `FORGE_URL`/`FORGE_SECRET` → `exit(2)` (`:394-398`) — správně.
  Ostatní mají tiché defaulty; `--interval` bez čísla dá `NaN` (`:91`).
- **Mrtvé zbytky v `worker.mjs` samém: žádné** `gameforge`/`forge-quest`/
  `router`. Mrtvý je jen default `FORGE_CMD` a komentář `:80-82`, který o jeho
  umístění lže.
- **Testy:** `self-test.mjs` testuje **jen happy path** (`make-dir` +
  `status === 'success'`); consent, neznámé kroky, selhání kroku a timeouty
  netestuje nic. `provider-choice.test.mjs` testuje modul, který worker
  **neimportuje**. `test-local.ps1` je rozbitý (`$Game` vs. `$Project`).
  **Worker nemá test své logiky.**

### 3.3 Vedlejší nález (bezpečnost)

`install-into-repo.ps1:94-97` kopíruje `.forge` **rekurzivně a bez filtru**,
tedy i `.forge/node/.env` s **reálným `FORGE_SECRET`** (soubor existuje,
`git ls-files` ho nezná). `.gitignore` hry (generovaný `:116-145`) `.env`
**neobsahuje** — ověřeno `git check-ignore` → nenalezeno. V herním repu dnes
`.forge/node/.env` **není**, takže k úniku ještě nedošlo; `git add -A`
v agentovi by ho ale vzal do patche i do PR.

---

## Část 4 — Nejsilnější nálezy v jedné tabulce

| # | Nález | Kde | Druh důkazu |
|---|---|---|---|
| 1 | Nová granule se **3 h** nevydá | `index.ts:646` vs `:796-804` | **naměřeno** (SQLite replika) |
| 2 | `/report` **obchází cooldown** | `index.ts:1329-1336` vs `:403-405` | **naměřeno** (SQLite replika) |
| 3 | Strop pokusů váže **úkol**, ne granuli → watchdog se nikdy nespustí | `:634-640`, `:246`, `:251` | kód + aritmetika prahů |
| 4 | Zámek souborů **neblokuje nic** | `:774-776` vs `:806` (`lockKeys:308`) | kód (nerovnost klíčů) |
| 5 | `validate-all.mjs` pouští **starou kopii** brány schématu | `validate-all.mjs:186` vs `ci.yml:53` | **naměřeno** (`cell=[], fallback=[]` + exit 0) |
| 6 | `validate-all.mjs` končí **exit 0** i při `✗ NALEZENO 3 PROBLÉMŮ` | `:252-253` | **naměřeno** |
| 7 | Šablona v gitu **není to, co je na disku** (8 změněných + 4 netrackované) | `git diff --stat repo/` | **naměřeno** |
| 8 | `release.yml` **v gitu** odkazuje na `forge-quest` | `git show HEAD:…:82,135` | **naměřeno** |
| 9 | `roadmap.json` šablony = **31 granul staré hry** | `repo/.forge/roadmap.json` | **naměřeno** |
| 10 | `install-into-repo.ps1` je **mrtvá větev** (`projects/` neexistuje) | `:36-38`, `:86` | **naměřeno** (`Test-Path`) |
| 11 | `.env` s reálným secretem se kopíruje do hry, která ho neignoruje | `install-into-repo.ps1:94-97` + `.gitignore` hry | **naměřeno** (`git check-ignore`) |
| 12 | `kontrola-driftu.mjs` **přehlédne** chybu `FORGE_ATTEMPT` v jiném kroku | `:44-71` | **naměřeno** (drift hlásí jen „kroky", ne env pozice) |
| 13 | `agent.yml` **nemá žádný test** (`test-ci-workflow.mjs` čte jen `ci.yml`) | `test-ci-workflow.mjs:39` | **naměřeno** |
| 14 | `MAX_ATTEMPTS` **není mrtvý kód** — mrtvý je komentář, který to tvrdí (i skill) | `index.ts:31,233` vs `:328,394,679,709,1329` | kód |
| 15 | Ovládací soubory `tools/` **nejsou v gitu** (51 untracked, 24 trvalých nástrojů) | `git ls-files tools/` | **naměřeno** |
| 16 | **57 ze 72** skriptů má absolutní cestu → orchestra je nepřenosná | `tools/` | **naměřeno** |
| 17 | `test-cooldown.py` nemá assert, vždy exit 0, a **posvěcuje** vadu 1 | `:39,57` | kód |
| 18 | `check-wiring.py` na jiném enginu **hlásí zelenou nad 0 soubory** | `:73-75` | kód |
| 19 | Animační brána se **nikdy neuplatní** (0 souborů `walk_*`) | `check-assets.py:232,252` | **naměřeno** |
| 20 | LGTM cache **v CI nikdy neplatí** (snímek je mimo repo) | `baseline.py:252` + `ci.yml:109` | **naměřeno** |

---

## Část 5 — Co ani tyhle audity nezjistily

- **Živý stav D1 a fronty** — volat Cloudflare/GitHub je mimo rozsah, takže
  nálezy 1 a 2 jsou doložené **replikou SQL**, ne pozorováním v provozu.
- **Záměr u nálezu 1** — komentáře říkají, že cooldown je o **selhaných**
  granulích; nelze vyloučit, že 3h rozestup mezi vlnami je chtěný. Je to
  **rozpor kódu s komentářem**, ne jistota o úmyslu.
- **Chování GitHub API** při dispatchi s nedeklarovaným vstupem (předpoklad:
  chyba → cesta „dispatch se opakuje bez stropu"); přímý doklad nedohledán.
- **Kdo dnes volá `POST /task`** — dopad nálezu „úloha mimo roadmapu je
  zablokovaná zombie invariantem" závisí na klientech mimo workspace.
- **Zda opravdu umírá Godot po SIGTERM** od `worker.mjs:174-176` (netestováno;
  vyžadovalo by běh s nekonečnou smyčkou).
- **Které konkrétní soubory by přeformátovala** záplata zapisující
  `write_text` bez `newline=''` (9 z 10; vyžadovalo by běh se zápisem).
- **Roadmapy ostatních her** (`forge-quest`, `idle-realms`, `IdleFantasy_Bart`)
  — jestli v nich jsou kolize `owns`, tedy jestli se rozbitý zámek (nález 4)
  někde projeví.
- **Obsah `orchestra/.github/workflows/deploy.yml`** — nečetl se, takže
  **nevím, které z těch 120 offline testů běží v CI orchestra**.

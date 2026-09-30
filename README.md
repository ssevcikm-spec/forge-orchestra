# Forge Orchestra

Samostatný orchestr, který **vyvíjí hry** — plánuje, zadává úkoly bezplatným
modelům v GitHub Actions, testuje a bezpečné změny sloučuje. Hra je pro něj jen
**herní dokument** (DESIGN.md + roadmapa), ne součást orchestra.

**Je to jeden projekt, který se přepíná mezi vyvíjenými hrami.** Nemá žádnou
vlastní hru — hry se registrují do registru her (`games` v D1) a kdykoli se dá
přepnout na jinou. Aktuálně jede na `uo-shadows`.

> **Historie:** orchestra vznikala současně s GameForge (lokální pipeline
> `forge.cmd`), která byla 30. 9. 2026 **zrušena a smazána**. Orchestra po ní
> nezdědila nic než pár historických cest v dokumentaci — a ty byly opraveny.
> Kdykoli narazíš na zmínku o GameForge, je to historie, ne závislost.

## Struktura

| Cesta | Co to je |
|---|---|
| `conductor/` | Mozek orchestra — Cloudflare Worker + cron + D1 (deployuje se sem) |
| `repo/` | Šablona, která se kopíruje do herních repů (`.forge/` + `.github/`) |
| `bin/task.mjs` | Ovládání orchestra z příkazové řádky |
| `tools/status.mjs` | **Stav na jednom místě** — conductor, registr her, fronta, modely, běhy |
| `tools/roadmap-reset.mjs` | Reset stavu roadmapy (když se změní ID granulí) |
| `tools/cancel-stale-runs.mjs` | Zruší zaseknuté běhy starých úloh (dry-run default) |
| `tools/tasks.mjs` | Výpis úloh s granulemi a repem |
| `tools/git.cmd` | Git s OpenSSL backendem (schannel na téhle stanici padá) |
| `tools/godot/` | Godot konzole pro domácí uzel (testy a buildy na PC) |
| `install-into-repo.ps1` | Připraví herní repo (nakopíruje `.forge` a workflowy) |
| `../games/<nazev>/` | Klony her, na kterých orchestra pracuje (mimo orchestra) |

## Údržba stavu (když se něco rozjede)

Dvě věci, které se v orchestra rozbily a mají teď vlastní endpoint:

**1. Změna ID granulí v roadmapě** → staré řádky v D1 zůstanou a conductor se
jimi dál řídí. Projeví se to tak, že se dispatchují granule, které v souboru už
nejsou (nebo se granule `model: strong` pustí slabému modelu).

```powershell
node orchestra\tools\roadmap-reset.mjs          # smaže stav, další tik ho znovu postaví
node orchestra\tools\status.mjs                 # kontrola
```

**2. Osiřelé úlohy** → po resetu zůstanou ve frontě `ready` úlohy, na které už
neodkazuje žádný řádek `roadmap`. Conductor je dispatchuje, i když je v aktuální
roadmapě nemá.

```powershell
# pozastavit hru, ať tik mezitím nezakládá nové úlohy
POST /game/active  {"game_id": "uo-shadows", "active": false}
# úklid (dry_run: true = jen spočítá)
POST /tasks/cleanup {}
# zase zapnout
POST /game/active  {"game_id": "uo-shadows", "active": true}
```

`/tasks/cleanup` úlohy **nemaže** (tabulka `runs` má cizí klíč na `tasks`, takže
`DELETE` padá na 500) — označí je `blocked`, což je terminální stav, který
stale-recovery respektuje. Historii běhů to nechá být.

**Poznámka k běhům na GitHubu:** zůstane-li běh navěky `in_progress`, je to
zaseknutý job na straně GitHubu (runner umřel, aniž by cokoliv poslal).
`node orchestra\tools\cancel-stale-runs.mjs --provest` ho zruší — cron ale
NIKDY neruší (skript sahá jen na běhy pojmenované `Forge #N`).

## Deploy

Conductor se nasazuje **automaticky z gitu**: push do `main` ve složce
`conductor/` spustí `.github/workflows/deploy.yml` (wrangler-action) a nasadí
na Cloudflare. Potřebuje dvě GitHub Secrets:

- `CLOUDFLARE_API_TOKEN` — token s právy Workers Scripts → Edit a D1 → Edit
- `CLOUDFLARE_ACCOUNT_ID` — ID účtu z Cloudflare dashboardu

Runtime tajemství conductora (`WEBHOOK_SECRET`, `GITHUB_TOKEN`,
`TELEGRAM_BOT_TOKEN`, `NTFY_TOPIC`, …) **žijí v Cloudflare** (`wrangler secret
put`), nikdy v gitu — deployem se nemažou.

> ⚠️ **Lokální `wrangler.cmd deploy` na této stanici NEFUNGUJE.** Uložené
> `wrangler login` má vypršelý token a Cloudflare vrací „Invalid access token"
> (ověřeno 30. 9. 2026). Nasadit umí jen GitHub Actions, které mají vlastní
> `CLOUDFLARE_API_TOKEN` — **cestou je tedy push do gitu**.
> Navíc wrangler v agentním sandboxu spadne na `spawn EPERM`.
> Registr her a granule se čtou přes HTTP endpointy conductora, ne z D1.

## Modely (řetězec free LLM)

`repo/.forge/providers.json` je **jediný zdroj pravdy** pro řetězec bezplatných
poskytovatelů. Herní repy si ho **stahují za běhu** (`pick-provider.mjs` fetchně
čerstvou verzi z `raw.githubusercontent.com`), lokální kopie v repu hry je jen
záloha. Mrtvý model se proto opraví **jednou tady** a všechny hry ho uvidí.

Zkouší se **popořadě** (štědré rotované podle `run_key`, skromný gemini nakonec)
a první, kdo odpoví, vyhrává — nikoli paralelně.

**Silné modely** (`strongModels` u providera): granule roadmapy s
`model: strong` (size_lines > 60) smí zpracovat jen model z tohohle seznamu.
Conductor pošle `model` do workflowu, ten nastaví `FORGE_MIN_STRONG=strong`
a `pick-provider.mjs` vybírá jen z strongModels — slabý model silnou granuli
nikdy nedostane, i kdyby fronta stála.

- **Kontrola zdraví**: `node repo/.forge/node/providers-check.mjs`
- **Pravidelná kontrola**: `repo/.github/workflows/model-check.yml` (denně,
  založí issue, když model zmizí z katalogu)
- **Návrh pouček z chyb**: `tools/suggest-conventions.mjs`
- **Test volby providera** (bez sítě): `node repo/.forge/node/provider-choice.test.mjs`

## Jak agent dostane soubory

Workflow **nepředává** aideru jen zadání — předává mu i soubory. Rozdíl mezi
`--read` a `--file` je přitom rozdíl mezi úspěchem a neúspěchem:

| Přepínač | Co udělá | K čemu |
|---|---|---|
| `--file <cesta>` | soubor je v chatu **EDITOVATELNÝ** | `owns` granule — soubory, které smí agent měnit |
| `--read <cesta>` | soubor je v chatu jen **KE ČTENÍ** | `owns` granulí z `depends_on` — jejich smlouvy |

Aider má v systémovém promptu pravidlo: *„But if you need to propose edits to
existing files not already added to the chat, you MUST tell the user their full
path names and ask them to add the files to the chat. End your reply and wait
for their approval."* Když tedy soubor v chatu **není**, model **správně**
odmítne editovat a odpoví žádostí o vložení souboru — 17–200 tokenů a žádná
změna. Přesně to se dělo u všech modelů (mistral i cerebras) a vypadalo to jako
„slabý model". Vysvětluje to i vzorec úspěch/neúspěch: granule, které soubor jen
**vytvářely**, procházely (na nový soubor není SEARCH blok potřeba); granule,
které existující soubor **upravovaly**, selhávaly vždy.

Soubory vybírá `.forge/files-to-edit.mjs`:
- `--grain <id>` → `owns` granule z `.forge/roadmap.json`,
- `--read-deps` → `owns` všech granulí z `depends_on` (jen ty, co v projektu jsou),
- fallback → cesty vytáhnuté ze zadání.

Neexistující soubor se **založí prázdný** a předá jako `--file` — i granule, která
soubor teprve vytváří, ho musí mít v chatu, jinak model odmítne navrhnout cokoli.

Navíc se pouští `--map-tokens 0`: repo-mapa stojí ~1k tokenů kontextu a dokumentace
aideru varuje, že slabé modely „se v ní snaží editovat" — tedy generují
SEARCH/REPLACE bloky pro soubory, jejichž obsah nikdy nedostaly.

## Opakované pokusy: každý zkusí jiný model

Granule `any` se řadí podle štědrosti kvóty (`mistral → cerebras → groq →
gemini → openrouter`) a **rotace podle `run_key` se u nich nepoužívá** — pořadí
je důležitější než rozmanitost. Důsledek ale byl, že opakované pokusy zkoušely
**pořád stejný model**:

    task #128 (core.skills)  5 běhů → mistral/codestral 5×
    task #131 (entity.npc)   5 běhů → mistral/codestral 5×

Když model na granulí selže, další pokus se stejným modelem selže skoro jistě.
Conductor proto posílá `inputs.attempt` (číslo pokusu) a `pick-provider.mjs`
podle něj **posune pořadí** — ale jen mezi štědrými; skromné (gemini ~20/den,
openrouter 50/den) zůstávají na konci. Ověřeno testy: tři pokusy po sobě zkusí
tři různé modely (`mistral → cerebras → groq`).

**Cooldown.** `RETRY_HOURS` (3 h) drží selhanou granuli mimo frontu, aby se
kvóta nepálila okamžitým retry. Vynucuje se na **dvou místech**, protože
selhání zapisují dvě cesty:

- `pollRuns` (polling GitHubu) vrací úkol na `ready` a **aktualizuje i roadmapu**
  (čas posledního pokusu je nositel cooldownu),
- dispatch smyčka **nevydá** `ready` úkol, jehož řádek v roadmapě se změnil
  v posledních `RETRY_HOURS`. Podmínka se ptá **výhradně na čas**, ne na
  `status` — první verze opravy filtrovala `rm.status='failed'`, jenže polling
  u opakovatelného selhání zapisuje `'queued'`, takže se guard vůbec neuplatnil
  a běhy se opakovaly každé 2 minuty místo za 3 h.

**Watchdog (`ESCALATE_AFTER`, výchozí 8).** `MAX_ATTEMPTS` je v provozu mrtvý
kód — rozhoduje `pollRuns`, který strop nezná, takže úkol může pokračovat
donekonečna (5 pokusů / 3 h ≈ 40 pokusů za den na jednu granuli). Watchdog
v tiku proto počítá **spálené runy** a po dosažení prahu pošle notifikaci
(Telegram/Discord/ntfy podle konfigurace). **Nic nevypíná** — granule se zkouší
dál, může jít o přechodný výpadek. Aby se notifikace neopakovala při každém
tiku, označí úkol `payload.eskalovano`.

Stav watchdogu je vidět v odpovědi `/tick` vždy, i s nulou:
`watchdog: 0 ohlášeno (prah 8)`.

## Nástroje pro analýzu (30. 9. 2026)

| Nástroj | K čemu |
|---|---|
| `tools/stav-conductora.mjs` | health + roadmap + failed (řeší BOM v `.env`) |
| `tools/fronta.mjs` | fronta úkolů: stav, pokusy, granule |
| `tools/analyza-posledni.mjs` | poslední běh každého tasku: model, tokeny, brána, testy |
| `tools/analyza-chyb.mjs` | kategorizace parse chyb napříč běhy |
| `tools/analyza-stavu.mjs` | souhrn: hotové/selhané, poměr úspěchů |
| `tools/analyza-modelu-pokusu.mjs` | kdo se potkal s opakovaným pokusem (rotace modelů) |
| `tools/log-usek.mjs` | vytáhne úsek logu z běhu podle regexu |
| `tools/stahni-patch.mjs` | stáhne `agent.patch` z běhu (co agent napsal) |
| `tools/kontrola-driftu.mjs` | šablona vs. klon hry; u YAML porovnává STRUKTURU |
| `tools/lint-roadmapa.py` | statický lint plánu (8 druhů vad DAG) |
| `tools/simulace-dag.py` | co odblokuje dokončení které granule (kritická cesta) |
| `tools/test-cooldown.py` | offline test SQL logiky cooldownu (6 scénářů) |
| `tools/test-eskalace.py` | offline test watchdogu (10 scénářů) |
| `tools/mereni-poskytovatelu.mjs` | změří dostupnost a velikost výstupu providerů |

## Conductor (API)

Runtime endpointy: `/health` (veřejný), `/tick`, `/poll`, `/queue`, `/roadmap`
(stav granulí v D1), `/failed`, `/status`, `/workers`, `/games`, `/game`,
`/game/active`, `/heartbeat`, `/claim`, `/task`, `/report`,
`/roadmap/reset`, `/tasks/cleanup` — vše kromě `/health` a `/report` (HMAC)
chráněné `x-forge-secret`.

## Přepnutí hry

Orchestra se přepíná mezi hrami přes registr her. Dvě operace:

```bash
# přihlášení / opětovné zapnutí hry (idempotentní, nastaví active = 1)
POST /game         {"game_id": "uo-shadows", "repo": "ssevcikm-spec/uo-shadows", "roadmap_file": ".forge/roadmap.json"}

# vypnutí hry (když se hra opustí)
POST /game/active  {"game_id": "uo-shadows", "active": false}

# stav registru
GET  /games
```

**Při opuštění hry ji vždy vypni.** Naměřeno 30. 9. 2026: opuštěná hra zůstala
s `active = 1`, její roadmapa měla 49 granulí ve frontě a conductor na ní
dispatchoval běh každou minutu — pálil free kvótu na hře, o kterou už nikdo
nestál. Zakázat workflow v repu hry stačí jen napůl, conductor se to nedozví.

Vypnutí **neuklízí** granule v tabulce `roadmap` (ty zůstávají pro návrat)
a neodregistruje domácí uzly.

### Aktuální stav

| Hra | Repo | Aktivní |
|---|---|---|
| `uo-shadows` | `ssevcikm-spec/uo-shadows` | **ano** |

Lokální klon pro práci: `..\games\uo-shadows\`.

## Tajemství — kam patří

| Tajemství | Kde žije |
|---|---|
| Cloudflare API token (deploy) | GitHub Secrets orchestra |
| WEBHOOK_SECRET, NTFY_TOPIC, TELEGRAM_BOT_TOKEN | Cloudflare Secrets |
| GitHub PAT (dispatch/PR) | Cloudflare Secrets + lokálně `.secrets/` |
| Klíče free LLM (mistral/gemini/…) | GitHub Secrets herních repů |

> **Proč klíče zůstávají v herních repech:** LLM volání běží v Actions runneru
> toho repa hry (GitHub ToS — agent smí pracovat jen na svém repu), takže klíč
> se tam čte lokálně. Je to **jedna hodnota klíče na N repů** (GitHub Secrets
> jsou per-repo a `ssevcikm-spec` je uživatel, ne organizace — nejsou žádné
> „org secrets"). Otočení klíče = aktualizace v N repech; `providers.json` to
> ale řešit neumí, proto je řetězec single-source a klíče zůstávají data.

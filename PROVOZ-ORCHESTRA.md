# Provoz orchestra — architektura, invarianty, nástroje a slepá místa

**Co tenhle dokument JE:** **projektová znalost ORCHESTRY** — to, co potřebuješ,
když měníš conductora, domácí uzel, šablonu herního repa (`repo/`) nebo když
vyhodnocuješ, proč se něco nedaří. Nejsou to pravidla (ta jsou v `AGENTS.md`)
ani stav (ten je v `HANDOFF.md`).

**Odkud brát dnešní stav:** `HANDOFF.md` (stav a nejnovější záznamy),
`KRONIKA-PROJEKTU.md` (historie), `AGENTS.md` (pravidla), a **běhy bran**
(`python _analyza\g3-brany.py`, `node tools\validate-all.mjs`).

> **⚠ ODKUD SE SEM PŘESUNUL (7. 10. 2026):** tenhle obsah byl do té doby ve
> **skillu `orchestra`** (38,7 kB). Skill se ale načítá v **každé** session, kde
> je potřeba orchestra — tedy i v session o hře nebo o obrázcích, kde je celý
> zbytečný. Skill teď drží **jen operativu** (stav, přepnutí hry, diagnostika
> „orchestra nic nedělá") a **odkazuje sem**.
>
> **Brány hry** (`.forge/check-schema.py`, `vision.mjs`, `baseline.py` a jejich
> slepá místa) **tady nejsou** — patří projektu hry:
> `E:\Workspaces\uo-shadows\docs\BRANY-HRY.md`.

---

## ⚠️ Sousední hry jsou ŽIVÉ (a pletou se s tou naší)

Ověřeno přes GitHub API 1. 10. 2026 — **`ssevcikm-spec` má pět repozitářů a dva
z nich vypadají jako „ta naše hra"**:

| Repo | Push | Pages | Pozor |
|---|---|---|---|
| **`uo-shadows`** | aktivní | **ANO** → `ssevcikm-spec.github.io/uo-shadows/` | **na téhle orchestra pracuje** |
| `forge-quest` | 30. 9. 2026 | **ANO** → `…github.io/forge-quest/` | **samostatná živá hra, ne mrtvá minulost** |
| `forge-orchestra` | 30. 9. 2026 | ne | orchestra sama |
| `idle-realms`, `IdleFantasy_Bart` | 30. 9. 2026 | ne | další hry |

**Nebezpečí, které z toho plyne (naměřeno):** v `release.yml` byl v poznámkách
k vydání odkaz na `…/forge-quest/` — tedy na **jinou hru**. Uživatel, který ho
otevřel, hrál forge-quest a ptal se, proč „naše" hra vypadá jinak, než má.
**Odkaz na hru se odvozuje z NÁZVU REPA**, nikdy se neopisuje z historie.

**Další poučení: webová verze se staví z `main`.** Workflow `release.yml` se
spouští na každý push do `main` a dělá rolling Release `latest` + nasazení na
Pages. **Co není pushnuté, na Pages neběží** — lokální necommitnutá práce
v klonu hry tedy nikdy nebude to, co uživatel vidí v prohlížeči. Když se
někdo diví, že „hra vypadá jinak", první otázka je **odkud ji pouští**
(Pages = stav gitu, ne disku).

## Architektura (zkratka)

- **Conductor** (Cloudflare Worker + D1, cron `* * * * *`): tabulky
  `tasks`/`runs`/`workers`/`games`/`roadmap`. Sám **nevolá žádné LLM** — jen
  dispatchuje GitHub Actions a posílá notifikace (Telegram). Jediná jeho
  externí volání jsou GitHub API a Telegram.
- **Modelový řetězec** žije v **herním repu** (`pick-provider.mjs`), ale
  `providers.json` si stahuje **za běhu** z orchestra
  (`raw.githubusercontent.com/.../repo/.forge/providers.json`); lokální kopie
  v repu hry je jen záloha. **Mrtvý model se opraví jednou v orchestra** a
  všechny hry ho uvidí. Zkouší se popořadě, první odpoví → vyhrává (ne paralelně).
- **Silné modely** (`strongModels` u providera): granule s `model: strong`
  (typicky `size_lines > 60`) smí zpracovat jen model z tohohle seznamu.
  Conductor pošle `model` do workflow, ten nastaví `FORGE_MIN_STRONG=strong`
  a pick-provider vybírá jen z strongModels. Slabý model silnou granuli nedostane.
- **Conductor v2**: čte z granule `size_lines`/`model`/`done`/`acceptance`;
  dispatch nese `max_lines`+`model` (brána auto-merge posuzuje limit podle
  granule), dále `grain` (podle něj workflow vybere soubory k editaci)
  a `attempt` (číslo pokusu — podle něj se posouvá pořadí modelů).
  Selhané granule se vracejí do fronty po cooldownu `RETRY_HOURS` (**3 h**) —
  free modely mají denní limity, okamžitý retry jen pálí pokusy.
  **Ale pozor: tentýž guard zpožďuje i NOVOU granuli o 3 h (invariant 15)
  a u selhání přes `/report` se naopak neuplatní (invariant 16).**
  Hotová granule se pozná i podle sloučeného PR (konec smyčky „conductor vydává
  hotovou granuli znovu").
- **Zámky**: `owns` (soubory) a `depends_on`. Klíč zámku je `{repo}/{soubor}`,
  takže dvě hry se stejným souborem se neblokují. Granule ve stejné vlně mají
  disjunktní `owns` → mohou běžet paralelně. **Pozor: v dispatch smyčce je
  porovnání klíčů rozbité (invariant 17) — zámek tam neblokoval nic.**

## Invarianty (naučené draze — neporušovat)

1. **roadmap.json má klíč `grains`** (s volitelnými `owns`/`depends_on`/
   `acceptance`/`done`), NE `tasks`.
2. **item_id v D1 = `{game_id}/{grain_id}`** — jinak se granule dvou her srazí.
3. **Klíče free LLM = jedna hodnota na N repů.** GitHub ToS: LLM volání běží
   v runneru herního repa, takže klíč musí být v Secrets **toho repa**; org
   secrets neexistují (`ssevcikm-spec` je uživatel). `providers.json` se NESMÍ
   kopírovat jako zdroj — jen runtime fetch.
4. **Repo hry se bere z úlohy** (`payload.repo`), ne z tvrdého řetězce.
   `wrangler.toml` má `GITHUB_REPO` jen jako fallback pro starý režim.
5. **Při přidání hry**: nejdřív ji zaregistrovat (`POST /game`), pak teprve
   nasazovat změny schématu — jinak cron tikne s prázdným registrem.
6. **Git/TLS na téhle stanici**: git volej přes `tools\git.cmd`
   (OpenSSL backend; schannel padá na `SEC_E_NO_CREDENTIALS`). TLS požadavky
   přes **Node `fetch`** — PowerShell `Invoke-RestMethod` i `curl.exe` na HTTPS
   ven selžou.
   **Push s PAT**: `git -c http.extraHeader="AUTHORIZATION: basic <b64(x-access-token:PAT)>" push origin main`
   (PAT čti ze souboru, nepiš ho do historie příkazů).
7. **Deploy conductora jen z gitu.** Push do `conductor/**` na `main` →
   `deploy.yml` (wrangler-action + `preCommands schema.sql`).
   **Lokální `wrangler.cmd deploy` NEFUNGUJE** — uložené `wrangler login` má
   vypršelý token a Cloudflare vrací „Invalid access token" (ověřeno 30. 9. 2026).
   Navíc wrangler v sandboxu spadne na `spawn EPERM`.
   **D1 přes REST API taky nejde** — čti registry přes HTTP endpointy conductora.
   Změny schématu D1: idempotentní samomigrace v kódu workeru (`ALTER` v tiku
   s polknutou chybou „duplicate column") — `CREATE TABLE IF NOT EXISTS`
   existující sloupec nepřidá.
8. **Roadmapa je soubor v repu hry**, orchestra si ji čte přes GitHub API.
   Když je rozbitá (neescapované uvozovky v promptu), orchestra na hře
   nepracuje — proto se po každé editaci validuje JSON.
9. **CI logy páruj podle „Job defined at"**, ne podle titulku — špatné párování
   už jednou vyrobilo falešnou „regresi".
10. **`blocked` je terminální stav.** Úklid jím označuje osiřelé úlohy a
    stale-recovery ho musí respektovat, jinak se úloha resurrectuje a dispatchuje
    dokola. `DELETE FROM tasks` NELZE použít — tabulka `runs` má
    `task_id REFERENCES tasks(id)` a Worker vrátí 500 (i po dávkách).
11. **Workers free mají 10 ms CPU na invokaci.** `DELETE`/`UPDATE` s poddotazem
    přes `tasks`×(stovky řádků) na to narazí. U velkých zásahů nejdřív přečíst
    ID a pak pracovat po dávkách.
12. **Agent musí mít soubor v EDITOVATELNÉM chatu.** `--read` = jen ke čtení,
    `--file` = editovatelné. Aiderův prompt doslova říká, že editace souboru
    mimo chat se musí odmítnout („ask them to add the files to the chat. End
    your reply and wait for their approval") — model tedy **poslechne a nic
    neudělá**. Soubory se berou z `owns` granule (`--file`) a z `owns` jejích
    závislostí (`--read`) přes `.forge/files-to-edit.mjs`. Neexistující soubor
    se založí prázdný, jinak ho model v chatu nemá.
13. **Cooldown se vynucuje ČASEM, ne `status`em.** Dispatch smyčka nevydá
    `ready` úkol, jehož řádek v roadmapě se změnil v posledních `RETRY_HOURS`.
    Podmínka se nesmí ptát na `rm.status='failed'` — polling u opakovatelného
    selhání zapisuje `'queued'`, takže by se guard vůbec neuplatnil (naměřeno:
    běhy se opakovaly každé 2 minuty místo za 3 h).
    **POZOR — ta oprava má dvě naměřené díry (1. 10. 2026), viz invariant 15
    a 16.** Tenhle invariant platí pro *opakované* selhání, ne pro novou granuli.
14. **`MAX_ATTEMPTS` NENÍ mrtvý kód** (dřív to tu stálo a byla to nepravda).
    Načítá se na **dvou místech** (`index.ts:328`, `:679`) a rozhoduje na
    **dvou dalších** (`:394` návrat do fronty, `:1338` → `failed`); `:709` ho
    používá v `WHERE attempts < ?`. **Ověřeno 1. 10. 2026** (dřívější seznam
    „:394, :709, :1329" byl nepřesný — čísla řádků se posunuly).
    Zastaralé jsou jen **komentáře v conductoru** (`:31`, `:233`), které tvrdí
    opak — **a pořád tam jsou**, protože jejich oprava je změna kódu, ne
    dokumentace. Když je uvidíš, nevěř jim; věř tomuhle invariantu.
    **Co ale nefunguje, je jeho účel:** strop je na **úkol**, kdežto smyčka je
    na **granuli** — `roadmapTick` zakládá pro každý retry **nový úkol
    s `attempts=0`**, takže granule jede **donekonečna**.
    Watchdog `ESCALATE_AFTER` (výchozí 8) **jen notifikuje** (záměr) — ale
    protože je prah 8 > strop 5 a počítá **běhy úkolu**, **nikdy se nespustí.**
    Stav je vidět v `/tick`. **(B3a to opravil: watchdog je dnes na granuli —
    viz `tools\test-watchdog-granule.py`, 17 kontrol, a `_analyza\b3-mutace.py`.)**
15. **Nová granule se `RETRY_HOURS` (3 h) NEVYDÁ — naměřeno.** `roadmapTick`
    zakládá řádek roadmapy s `updated_at = now` (`:643-646`), ale dispatch guard
    (`:796-804`) se ptá **jen na čas** — tedy na tentýž sloupec jako cooldown po
    selhání. Replika SQL v SQLite: nová granule → `[]`, týž řádek starý 4 h →
    `[1]`. Navenek to vypadá jako „orchestra nic nedělá", a `/queue` přitom
    hlásí `ready`. **Než začneš řešit „proč se nic neděje", zkontroluj tohle.**
16. **Cooldown se u selhání přes `/report` OBCHÁZÍ.** `/report` (`:1329-1336`)
    u opakovatelného selhání zapíše **jen `tasks`**, `roadmap.updated_at` ne
    (`pollRuns` to dělá správně, `:403-405`). Projev: granule se zkouší každé
    2 minuty a spálí 5 pokusů za čtvrt hodiny.
    **(B2 to opravil: `tools\test-report-cooldown.py`, 8 kontrol, `_analyza\b2-mutace.py`.)**
17. **Zámek souborů v dispatch smyčce neblokoval nic — OPRAVENO 1. 10. 2026.**
    `locked` se plnilo z **holých jmen**, ale `:806` porovnává s klíči
    `${repo}/${soubor}` (`lockKeys`, `:308`) → množiny se **nikdy neprotly**.
    Dvě granule se stejnými `owns` se rozjely paralelně. Nově se klíč bere
    z téhož místa jako při porovnání (`lockKeys(r.payload, env)`).
    **Regresní test:** `tools\test-zamek-owns.py` (8 kontrol, vytahuje
    `lockKeys` ze zdrojáku, je ověřen **mutačním testem**). Když v conductoru
    změníš plnění `locked`, tenhle test to musí chytit — když nechytí, je
    slabý, ne zelený.
    **`tools\lint-roadmapa.py`** u kolize `owns` tvrdí „poběží sériově" —
    **po opravě je to pravda** (před ní nebyla).
    **Obecné poučení:** dva tvary téhož klíče na dvou místech je vada, kterou
    žádný test nevidí, dokud se nezeptáš, jestli se množiny mohou protnout.
18. **`listGames` fallback je nebezpečný.** Když je registr her prázdný,
    conductor si vystačí s `env.GITHUB_REPO` (`:447-454`) → **vypnutí poslední
    registrované hry orchestra nezastaví.** A `/tasks/cleanup` bere jen aktivní
    hry (`:1120`), takže s vypnutou hrou **smaže cache roadmapy** (`:1184`) —
    přitom doporučený postup v témž kódu (`:1107-1108`) je „nejdřív hru vypni,
    pak cleanup, pak zapni". **Před `/tasks/cleanup` si přečti těch pár řádků.**
    **(B4 to opravil: `tools\test-listgames.py`, 10 kontrol, `_analyza\b4-mutace.py`.)**
19. **Brána v CI si musí dovézt SVOJE závislosti — a conductor to nepozná.**
    Naměřeno 1. 10. 2026: `check-schema.py:386` importuje `PIL` **uvnitř
    funkce** a jen když hra má sprity; `ci.yml` v tom kroku Pillow
    **neinstaloval** (kroky na `:70` a `:119` ho měly). Následek:
    `ModuleNotFoundError: No module named 'PIL'` → **první brána celého CI
    spadla**, `main` zezelenal nikdy a orchestra **7,5 h nevydala ani granuli**.
    **Proč to nikdo nepoznal (a to je to poučení):** `/failed` conductora je
    **prázdné** (selhaly *běhy*, ne *úlohy*) a `/health` hlásí **`ok: true`**.
    **Zelený conductor nad červeným repem** je nová třída tichého selhání.
    **Než začneš řešit „proč orchestra nic nedělá", zkontroluj poslední CI běh
    na `main` cílové hry** — ne jen conductora.
    Opraveno v obou kopiích `ci.yml`; obrana do budoucna je návrh **N0.2**
    (brána na závislosti bran) a **N0.3** (stav CI v `/health`).
    **(N0.3 je hotové: `tools\test-health-cile.mjs` + `_analyza\n03-mutace.py`
    a dnes i v `validate-all`. Invariant drží jako historie — viz `HANDOFF.md`.)**
20. **Strop pokusů je na granuli, ne na úkolu** (B3b, 6. 10. 2026): `roadmap`
    má vlastní strop; test `tools\test-grain-cap.py` (22 kontrol) a mutace
    `_analyza\b3b-mutace.py`. Když se mění rozhodování o `attempts`, musí to
    chytit **tenhle** test, ne jen `test-cooldown.py`.

## Údržba stavu (dvě věci, které se rozbily)

**Změna ID granulí v roadmapě** (např. přechod `default/*` → `{game}/*` po
registraci hry): staré řádky v D1 zůstanou a conductor se jimi dál řídí —
dispatchuje granule, které v souboru už nejsou. Poznáš to tak, že se granule
`model: strong` pouštějí slabému modelu a úloha má desítky pokusů.

```powershell
node tools\roadmap-reset.mjs     # smaže stav; další tik ho postaví znovu
```

**Osiřelé úlohy** po resetu: ve frontě `ready` zůstanou úlohy bez vazby na
`roadmap`. Postup: vypnout hru → `POST /tasks/cleanup {}` → zapnout hru.
Dry-run: `POST /tasks/cleanup {"dry_run": true}`.
Endpoint úlohy **nemaže**, jen je označí `blocked`.

**Zaseknuté běhy na GitHubu** (`in_progress` navěky): runner umřel, aniž by něco
poslal. Zruš je `node tools\cancel-stale-runs.mjs --provest` (skript
sahá jen na běhy pojmenované `Forge #N`, cron nikdy neruší).

## Ověřený stav modelového řetězce (30. 9. 2026)

| Poskytovatel | Stav |
|---|---|
| **mistral** `codestral-latest` | funguje, umí dobře diff. Nejspolehlivější. |
| **cerebras** `gpt-oss-120b` | jede z **trial kreditu $5/30 dní** — trvalý free tier zrušen, vyžaduje kartu. Je v `strongModels`, takže jeho výpadkem přijdou silné granule o článek. |
| **groq** `openai/gpt-oss-120b` | **funguje**, klíč v Secrets je (ověřeno běhy #100–#102). Free 30 RPM/1000 RPD. |
| **openrouter** `:free` | poslední záchrana, ~50 dotazů/den. |
| **gemini** | `skromny: true` — jen ~20 dotazů/model/den, proto se zkouší **na konci**. |

Denní kontrola: `model-check.yml` v herním repu (založí issue, když model zmizí).

## PC jako domácí uzel (worker)

Tento počítač je pull-worker conductora (`worker.cmd` v repu orchestry, uzel
`pc-domaci`). Whitelist kinds `assets,test,build`; krok `shell:` se VŽDY ptá y/N.
Konfigurace v `.forge\node\.env` (gitignored) — včetně `FORGE_GODOT`, který míří
na **`E:\Tools\godot\Godot_v4.7.2-stable_win64_console.exe`** (obecný nástroj
stanice; cesta `tools\godot\` **už neexistuje**).
**Stav 30. 9. 2026: uzel je off** (naposledy 29. 9. 20:03). Práci berou cloudové
úlohy; `oracle-frankfurt` je v pořádku.

**Kroky, které uzel zná:** `worker.mjs` umí jen `shell`, `godot-import`,
`godot-test`, `godot-export`, `python`, `make-dir` — **`blender:` mezi nimi
není**, 3D → 2D render se skládá přes `shell:` (a ten se vždy ptá y/N).
`worker.mjs` má navíc mrtvý default `FORGE_CMD` na smazaný `forge.cmd` — krok
`forge:` je v praxi nepoužitelný. Upřesnění měřením (1. 10. 2026): ten default
**nemíří** na `…\gameforge\forge.cmd` (jak se píše v komentáři `:80-82`), ale na
`C:\Users\Ssevc\Local-Deepseek\forge.cmd` — `path.join` čtvrté `..` nezkrátí.
Ani jeden z těch souborů neexistuje.

**Domácí uzel nemá test své logiky.** `self-test.mjs` ověří jen happy path
(`make-dir` + `status === 'success'`); consent u `shell:`, neznámé kroky,
selhání kroku, timeouty ani selhání reportu **netestuje nic**.
`test-local.ps1` (E2E) je navíc **rozbitý** — používá nedefinovanou `$Game`,
parametr je `$Project`. A `worker.cmd` by dnes spadl na chybějící
`.forge\node\.env` (dřív `games\uo-shadows\…`, dnes `E:\Workspaces\uo-shadows\…` —
ověřeno 6. 10. 2026: soubor **neexistuje**, adresář `.forge\node` ano).

## Analýza a diagnostika (nástroje ze 30. 9. 2026)

Když je potřeba zjistit, **proč** běhy selhávají, sahají se tyhle:

| Nástroj | K čemu |
|---|---|
| `tools\stav-conductora.mjs` | health + roadmap + failed (řeší BOM v `.env`) |
| `tools\fronta.mjs` | fronta úkolů: stav, pokusy, granule |
| `tools\analyza-posledni.mjs [N]` | poslední běh každého tasku: model, tokeny, brána, testy |
| `tools\analyza-chyb.mjs` | kategorizace parse chyb napříč běhy |
| `tools\analyza-stavu.mjs` | souhrn: hotové/selhané, poměr úspěchů |
| `tools\analyza-modelu-pokusu.mjs` | kdo se potkal s opakovaným pokusem (rotace modelů) |
| `tools\log-usek.mjs <run> "<od>" "<do>"` | vytáhne úsek logu z běhu podle regexu |
| `tools\stahni-patch.mjs <run>` | stáhne `agent.patch` — **co agent skutečně napsal** |
| `tools\kontrola-driftu.mjs` | šablona vs. klon hry; u YAML porovnává STRUKTURU, ne text |
| `tools\lint-roadmapa.py` | statický lint plánu (8 druhů vad DAG) — **spouštěj před dispatchem** |
| `tools\simulace-dag.py` | co odblokuje dokončení které granule (kritická cesta) |
| `tools\test-cooldown.py` | offline test SQL logiky cooldownu. **Stav 6. 10. 2026: OPRAVENO** — SQL guardu **vytahuje ze zdrojáku** conductora (`vytahni_guard_sql`), má `assert` i `sys.exit`: **10 kontrol, 0 chyb**. ⚠ **Historické varování (1. 10. 2026)** — „nemá assert, končí vždy 0, SQL opsané, slepý vůči invariantu 15" — **už neplatí** a je tu jen proto, aby někdo nehledal vadu, která je zavřená. |
| `tools\test-eskalace.py` | ⚠ **ZASTARALÉ (6. 10. 2026):** testoval watchdog, který počítal běhy **JEDNOHO úkolu** a prah měl **natvrdo 8** — tedy stav, který conductor neumí vyrobit (strop 5). Logiku nahradil watchdog **na granuli** (B3a) a ten měří `tools\test-watchdog-granule.py` (17 kontrol; SQL, prah i rozhodnutí **ze zdrojáku**) s mutačním důkazem `_analyza\b3-mutace.py`. Soubor zůstává kvůli odkazům; smazat/přepsat ho patří do fáze C. |
| `tools\test-tick-offline.mjs` | **rozhodovací logika conductora** — volá **skutečný `POST /tick` a `POST /report`** (a od 7. 10. 2026 i `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`) nad zbundlovaným conductorem s falešnou D1 (na neznámý dotaz **spadne**) a stubovaným GitHubem: **100 kontrol** (dispatch a `MAX_CONCURRENT`, `pollRuns` včetně cooldownu a `awaiting_human`, stale-recovery, `/report`, tajemství, chybějící hlavičky uzlu, prohraný optimistický zámek, dry-run, pojistka „roadmapa se nedá načíst → nemažu"). Mutační důkaz `_analyza\tick-mutace.py` (**15 vrat / 31 kontrol**, mezi nimi historické vady **B1** a **A1**). |
| `tools\mereni-poskytovatelu.mjs` | změří dostupnost a velikost výstupu providerů |

> **⚠ OPRAVENO 6. 10. 2026 — conductor UŽ test rozhodovací logiky MÁ;
> a 7. 10. 2026 (P24) je rozšířený i na endpointy, které netestoval NIKDO.**
> `tools\test-tick-offline.mjs` volá **skutečný `POST /tick`** a `POST /report`
> nad zbundlovaným conductorem (`wrangler deploy --dry-run`, bez sítě
> a přihlášení), s falešnou D1, která **na neznámý dotaz spadne**, a se
> stubovaným GitHubem: **100 kontrol** a **15 vrat** v `_analyza\tick-mutace.py`
> (31 kontrol) — mezi nimi i historické vady **B1** a **A1**.
> **Co ještě neprochází žádným handlerem:** `mock-conductor.mjs` je pořád jen
> mock pro ruční zkoušení (netýká se to `test-tick-offline.mjs`, který volá
> skutečné handlery).
> ⚠ Text níž **platil do 6. 10. 2026** a drží se jako historie („co bylo
> naměřeno, zůstává naměřené") — **nečti ho jako dnešní stav**.
>
> ~~**Conductor nemá test své rozhodovací logiky.** Dva `.py` testy výš logiku
> **opisují**, `mock-conductor.mjs` neumí `/tick`, `/poll`, `/roadmap`,
> `/roadmap/reset` ani `/tasks/cleanup` (tedy místa, kde rozhodování bydlí),
> a `validate-all.mjs` se na `index.ts` dívá jen **bajtovým porovnáním** s kopií
> v repu. **Když se v conductoru změní SQL, neozve se nic.**~~

**Užitečné postupy:**
- **Agent psal nesmysly?** `stahni-patch.mjs` dá přesný text, který model
  vygeneroval — to je jediný spolehlivý zdroj (logy obsahují i shell workflowu).
- **Testy hlásí „zasekly se"?** Hledej v `agent.log` poslední `[test] OK` řádek;
  co následuje, je místo, kde se `_run()` přerušil.
- **Opakované pokusy zkouší stejný model?** `analyza-modelu-pokusu.mjs` to
  ukáže; příčina bývá, že rotace se u granulí `any` nepoužívá (viz invariant 12).

## Co orchestra NEMÁ (a je potřeba s tím počítat)

- **Bezpečné vypnutí hry.** Fallback `listGames` znamená, že vypnutí poslední
  registrované hry orchestra nezastaví (invariant 18) — **OPRAVENO B4
  (6. 10. 2026, `tools\test-listgames.py`)**, text tu zůstává jako historie.
- **Funkční zámek souborů při dispatchi.** ~~Chyběl~~ → **OPRAVENO
  1. 10. 2026** (invariant 17, commit `6d2a856`, nasazeno; regresní test
  `tools\test-zamek-owns.py`). Už to sem nepatří — je to tady jen proto, aby
  někdo nehledal vadu, která je zavřená.
- **Test rozhodovací logiky conductora.** ~~Chyběl~~ → **OPRAVENO 6. 10. 2026**:
  `tools\test-tick-offline.mjs` (**100 kontrol**) volá **skutečný `/tick`
  i `/report`** nad zbundlovaným conductorem a má mutační důkaz
  `_analyza\tick-mutace.py` (**15 vrat**, mezi nimi historické vady **B1**
  a **A1**). `test-cooldown.py` SQL **vytahuje ze zdrojáku**;
  `test-eskalace.py` je **zastaralé** (viz tabulka výš).
  **Vzor pro nové brány** zůstává `tools\test-zamek-owns.py` — vytahuje funkci
  ze `index.ts` a spouští její skutečný text.
- **Provider fallback v DSH** — s tímhle projektem nesouvisí, ale ověřeno:
  DSH žádný nemá. Když DeepSeek vypadne, model se musí přepnout ručně.
- **Lokální dokumentaci k nastavení.** `FREE-TIERY-2026.md`, `ORCHESTR.md`,
  `ORCHESTR-NASTAVENI.md`, `PLAN.md`, `STANICE.md` byly 30. 9. 2026 smazány
  spolu s GameForge a **nebyly v gitu** — ztratily se. Živý stav je v README
  a v `repo/` šabloně.
- **Trackovanou šablonu, která odpovídá disku.** ~~Chyběla~~ → **OPRAVENO
  1. 10. 2026 (F0)**. Naměřeno dnes:
  `git ls-files repo/.forge` → **21**, `git ls-files tools` → **70** (a na disku
  je taky 70), roadmapa šablony má **0 granul** a `vision-profile.json` má
  `hra: null`. `release.yml` **odvozuje odkaz z názvu repa**
  (`…/NAZEV-REPA/`) — na `forge-quest` už neodkazuje.
  **Co z toho plyne pro hru, která vznikne zítra:** dostane prázdnou roadmapu
  a obecný profil, ne pozůstatky cizí hry. Kdyby se do šablony dostala
  konkrétní hodnota, zdědí ji každá nová hra — proto se to hlídá
  (`kontrola-driftu.mjs` má seznam souborů, které se **záměrně
  nesynchronizují**).

## Kam pro detaily

- `README.md` (orchestra) — struktura, deploy, API, přepnutí hry, **jak agent
  dostane soubory**, opakované pokusy a cooldown, watchdog, nástroje.
- **`ANALIZA-ARCHITEKTURY-ORCHESTRA.md`** — **analýza architektury
  z 1. 10. 2026**: tři třídy tichých selhání, tabulka 16 tříd selhání
  (S1–S16), odpovědi na 15 otázek, co je rozhodnutí a co historický nános,
  a co analýza **nezjistila**. Čti, než začneš v orchestra něco měnit —
  obsahuje naměřené vady conductoru (invarianty 14–18).
- **`ANALIZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`** — úplné podklady
  k té analýze: audit conductora po řádcích, inventura `tools/` (co je a není
  v gitu), audit domácího uzlu, **spustitelný skript, kterým se měří cooldown**.
- `repo/CONVENTIONS.md` — poučky, které agent dostává přes `--read`.
  **§1g** je klíčový: soubor granule musí začít `extends Node`, `class_name`
  nesmí být i jménem vnořené class, `_init()` bez povinného argumentu.
- `HANDOFF.md` — živý stav a nejnovější záznamy; starší historie je
  v `KRONIKA-PROJEKTU.md` a v `_archiv\`.
- **Brány hry** (`.forge/check-schema.py`, `check-assets.py`, `vision.mjs`,
  `baseline.py`, jejich slepá místa a past „TIŠE PŘESTALA MĚŘIT"):
  `E:\Workspaces\uo-shadows\docs\BRANY-HRY.md` + `AGENTS.md` hry.
- `~\.dsh\skills\game-developer\SKILL.md` — jak rozpadnout hru na granule (DAG),
  velikost granule podle modelu, brány a ověření; **past s podmíněným testem**
  (tiše zelený test, který se nikdy nezapne).

# Analýza architektury Forge orchestra

> **Co tenhle dokument JE:** analýza. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Kdo to psal:** session z 1. 10. 2026, večer — **nová session, která ten kód
nepsala** (jak žádalo zadání `ARCHITEKTURA-ANALYZA-ZADANI.md`).
**Rozsah:** pouze čtení a měření. **Kód orchestra nebyl změněn, nic nebylo
pushnuto.** Jediné zápisy: `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (tento soubor)
a dočasná složka `.tmp\brany-test\` pro ověření brány Godotu.

**Jak čti tenhle dokument:** každé tvrzení je označené, odkud je.

| Značka | Znamená |
|---|---|
| **měřeno** | Spustil jsem to a vidím výsledek (příkaz je u nálezu). |
| **kód** | Přečtený řádek zdrojáku — `soubor:řádek`. Ověřitelné očima. |
| **odvozeno** | Logický důsledek měření a kódu; není to přímý výstup nástroje. |
| **nevím** | Nedohlédl jsem. Je to v §6. |

---

## 1. Verdikt

**Orchestra má tři vrstvy a každá je na tom jinak.** Jádro (conductor +
modelový řetězec + vision/baseline) je promyšlené a místy výborné. Obálka
(šablona, git, onboarding) je nedokončená. A **provozní smyčka má tři naměřené
vady, které přímo brzdí práci** — z nich nejdražší je, že **nová granule se tři
hodiny nevydá**, a to se navenek tváří jako „orchestra nic nedělá". Pro druhou
hru a pro jiný engine než Godot je dnes orchestra nepoužitelná — a to kvůli
onboardingu, ne kvůli jádru.

Chyby se ztrácejí tiše ve **třech** strukturálních místech:

1. **Rozchod mezi „co je na disku" a „co je v gitu"** (měřeno): šablona
   `orchestra/repo/` má **8 změněných trackovaných souborů** a **4 důležité
   soubory vůbec netrackované**. `release.yml` v gitu **hlásí odkaz na
   `forge-quest`** — na jinou živou hru (`git show HEAD:repo/.github/workflows/release.yml`
   → řádky 82 a 135). Kdo orchestra naklonuje, dostane tuto verzi.
2. **Nástroje se množily místo aby se nahrazovaly** (měřeno): v orchestra
   existují **dvě různá schémata kontroly téhož** — `tools/kontrola-schematu.py`
   (stará, slepá) a `repo/.forge/check-schema.py` (nová, opravená). A
   `validate-all.mjs` pouští **tu starou** (`validate-all.mjs:186`) a tiskne
   doslova `level.gd: výchozí cell=[], fallback=[]` — přesně ten řádek, který
   v zadání figuruje jako podpis tichého selhání. Nástroj na ověřování orchestra
   tedy sám měří špatnou kopii.
3. **Chybějící onboarding nové hry** (měřeno): cesta, kterou se zakládá nová
   hra, je dnes **nefunkční**. `install-into-repo.ps1:36-38` vyžaduje
   `projects\<Projekt>`, ale `projects/` neexistuje (smazáno s GameForge);
   `install-into-repo.ps1:86` posílá uživatele na smazaný `forge.cmd`;
   a `repo/.forge/roadmap.json` — který se nové hře zkopíruje — obsahuje
   **31 granul staré hry** (`chest-unlock2`, `minimap`, `lives-hud`, …).

**Největší strukturální riziko** není žádná z těch tří věcí jednotlivě, ale
jejich souhrn: **šablona `repo/` je zároveň „zdroj pravdy" i „kopie, která se
rozešla"**, a **není žádné místo, které by řeklo, která verze platí**. Tři
synchronizační nástroje se třemi seznamy (fakt 2.2/5 zadání) jsou symptom;
skutečná vada je, že **nikde není deklarováno, co je kontrakt a co je kopie**.

**A jedna věc, která je horší než všechny tři — naměřená a nezávisle
reprodukovaná:** orchestra **zdrží každou novou granuli o `RETRY_HOURS`
(3 hodiny)** a **strop pokusů neváže granuli, ale úkol**. Obojí plyne z téhož:
`roadmapTick` zakládá pro granuli **nový úkol** s `updated_at = now`
(`index.ts:634-647`) a dispatch se ptá **jen na čas** (`index.ts:796-804`).
**měřeno** (přesná replika obojího SQL v SQLite; skript níž):

| stav | výsledek dispatch dotazu |
|---|---|
| A) nová granule — přesně to, co zapíše `roadmapTick` | **`[]` — nevydá se** |
| B) týž řádek starý 4 h | `[1]` — vydá se |
| C) po `/report` u opakovatelného selhání | `[1]` — **cooldown se obchází** |

Měření je reprodukovatelné bez sítě a bez orchestra — stačí SQLite a dvě
tabulky (celý skript je v `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`, §1.2):

```python
db.execute("INSERT INTO tasks (status) VALUES ('ready')")
db.execute("INSERT INTO roadmap (item_id, task_id, status, updated_at)"
           " VALUES ('h/g1', 1, 'queued', datetime('now'))")   # jako roadmapTick:643-646
db.execute("""SELECT id FROM tasks WHERE status='ready' AND target='cloud'
   AND NOT EXISTS (SELECT 1 FROM roadmap rm WHERE rm.task_id = tasks.id
                     AND rm.updated_at > datetime('now', ?))
  ORDER BY id LIMIT 25""", ("-3 hours",)).fetchall()
# → []            (a po posunu updated_at o 4 h zpět → [(1,)])
```

Důsledek pro uživatele: **orchestra po přidání granule 3 hodiny nic nedělá,
a `/queue` přitom hlásí `ready`.** To není „tichá chyba v bráně" — to je tichá
chyba v srdci orchestra, a je to **nejcennější nález téhle analýzy**.

### 1.1 Odpověď na tři otázky z doprovodného zadání

**A) Je orchestra univerzální, a šlo by to zdarma?**
**Jádro ano, obálka ne.** Naměřeno rozdělením šablony: **17 z 24 souborů
`.forge` je na enginu nezávislých** — mluví o datech (`spec.json`,
`levels/*.json`, `manifest.json`, `roadmap.json`), ne o Godotu:

| Vrstva | Soubory | Vázané na Godot? |
|---|---|---|
| Data a jejich kontrola | `check-schema.py`, `check-assets.py`, `verify-level-render.py` | **ne** — čtou JSON a PNG |
| „Oči" a paměť | `vision.mjs`, `baseline.py`, `vision-profile.json` | **ne** |
| Orchestrace běhu | `pick-provider.mjs`, `provider-choice.mjs`, `files-to-edit.mjs`, `report.mjs`, `providers.json` | **ne** |
| Model volby LLM | `providers.json` (5 poskytovatelů, `providers.json:32-100`) | **ne** |
| Engine | `install-godot.sh`, krok `godot-*` v `worker.mjs:213-223` | **ano** |
| Engine | `check-wiring.py` — parsuje `func` v `scripts/*.gd` a hledá výskyty v `*.gd`/`*.tscn`/`*.tres` (`check-wiring.py:44,73,84-89`) | **ano** |
| Engine | `agent.yml` krok *Kontrola parsování* — `godot --check-only --script` (`agent.yml:294`) | **ano** |
| Engine | `agent.yml` krok *Import assetů* — `--import` (`agent.yml:373`) | **ano** |

**Kolik by stálo přidat druhou technologii (např. Python/Pygame nebo web):**
- **zdarma:** data-vrstva, vision, baseline, modelový řetězec, conductor,
  roadmapa, auto-merge — beze změny.
- **levné:** vyměnit tři engine brány za jejich ekvivalenty a v
  `baseline.py:60` (`SLEDOVANE`) a `check-wiring.py:84-89` (přípony) udělat
  **deklaraci místo konstanty**.
- **drahé (a proto se to nevyplatí dělat teď):** dnešní kontrakt je **„cesty
  v repu"**, ne „deklarovaný soubor". Každý soubor, který hra dostane, je
  **vidlice** (fork), kterou je pak potřeba synchronizovat. To je přesně to,
  co dnes bolí u `agent.yml`.

**Závěr A:** modularita je **dosažitelná za jednotky hodin, ale jen jednou
cestou — inverzí směru kopírování.** Dnes se všechno kopíruje ze šablony do
hry a každá kopie se rozejde. Správně má být: **jádro je balíček, hra má jen
deklaraci** (`forge.config.json`: kde je spec, kde sprity, které brány, které
přípony). To je změna, kterou je **teď levné udělat a za měsíc drahá** —
proto je v §5 mezi strukturálními, ne mezi „hned".

**B) Je orchestra očištěná od původní hry `forge-quest`?**
**Herní repo ano, orchestra ne — a rozdíl je důležitý.** Naměřeno `git grep`
v obou repech:

| Kde | Co tam je | Je to vada? |
|---|---|---|
| `conductor/src/index.ts` (1359 řádků) | **0 výskytů** `forge-quest`, `gameforge`, `uo-sandbox`, `forge.cmd`, `--router`. Dvě zmínky „z éry GameForge" (`:1095`, `:1118`) jsou **komentáře s naměřenými čísly** u funkční opravy | **ne — conductor je čistý** |
| `orchestra/repo/` (šablona) | **0 výskytů** `uo-shadows` | **ne** |
| `games/uo-shadows` (kód) | `release.yml:136-137` a `docs/ARCHITEKTURA.md:7` — **komentáře vysvětlující historii**; `forge.json:5` „puvodne gameforge/pipeline/forge.py"; `tools/blender/_analyze.py:5` — **mrtvá absolutní cesta** do smazaného `gameforge\projects\uo-sandbox\` | komentáře **ne**; mrtvá cesta **ano** (nástroj mimo hru) |
| `orchestra` **v gitu (HEAD)** | `repo/.github/workflows/release.yml:82,135` — **natvrdo `…/forge-quest/`**; `install-into-repo.ps1:8,11,167`; `bin/task.mjs:12,40`; `wrangler.cmd:6-8`; `tools/test-local.ps1:34-36` | **ANO** — tohle je to dědictví |
| `orchestra/repo/.forge/roadmap.json` | **31 granul staré hry** + `_popis` odkazující na smazaný `forge plan` (`roadmap.json:19`) | **ANO** — a **kopíruje se do každé nové hry** |
| `orchestra/tools/` | **47 ze 75 souborů má `uo-shadows` zapsané v kódu**; **57 ze 72 skriptů má absolutní cestu** `C:\Users\Ssevc\Local-Deepseek\` | **ANO** — nástroje jsou jednohrové a nepřenosné |
| `research/`, `_retired/`, `dsh-*` | historie s revizními hlavičkami | **ne** — archiv, je označený |

**Mechanismus, kterým nová hra dědí pozůstatky** (jádro otázky B):
`install-into-repo.ps1:94-97` kopíruje `repo\.forge\*` **rekurzivně a bez
filtru** → nová hra dostane (1) roadmapu s 31 granulemi staré hry, (2)
`vision-profile.json` s **natvrdo `"hra": "uo-shadows"`**
(`vision-profile.json:16`), (3) `.env` s reálným `FORGE_SECRET`
(ověřeno: soubor existuje, `.gitignore` hry **`.env` nezná** — měřeno
`git check-ignore` → nenalezeno) a (4) `release.yml`, který v gitu stále
odkazuje na `forge-quest`.

**Přesná odpověď:** orchestra **není** kontaminovaná obsahem staré hry uvnitř
své logiky — conductor i šablona jsou na hru vázané jen konfigurací, ne kódem.
Kontaminované je **to, co se kopíruje do nové hry** (roadmapa, profil, `.env`)
a **nástroje, kterými se orchestra obsluhuje** (47 jednohrových + 57
nepřenosných). To první je pár souborů; to druhé je systémová vlastnost.

**C) Je orchestra dobře navržená pro různorodou práci?**
**Na jednu hru a jeden engine: ano — a místy výborně.** Tři věci jsou nad
průměrem a je vidět, že vznikly z konkrétní chyby:

- `check-schema.py:246-262` rozlišuje **„kontrola neproběhla"** (vada) od
  **„není co měřit"** (poznámka) a prázdno vypisuje jako *nezměřeno*.
- `check-schema.py:348-356` pojmenovává **mrtvou větev** (smazaný `world.gd`).
- `baseline.py:69-94,97-127` pojmenovává **meze vlastního nástroje** (phash
  je slepý na barvu, degeneruje u jednolitého obrázku) a doplňuje je.

Pro různorodou práci ale chybí tři věci: **deklarovaný kontrakt** (co je
jádro a co kopie), **deklarované brány** (které se pouští a proti čemu), a
**funkční onboarding**. Bez nich je každá nová hra ruční práce a každá nová
technologie vidlice.

---

## 2. Tabulka tříd selhání

| # | Třída selhání | Konkrétní místo (kód / měření) | Jak se to pozná dnes | Co by to odhalilo |
|---|---|---|---|---|
| **S1** | **Brána měří jinou kopii, než jaká se používá** | `validate-all.mjs:186` pouští `tools/kontrola-schematu.py`; v CI běží `repo/.forge/check-schema.py` (`ci.yml:53`). **měřeno:** starý tiskne `level.gd: výchozí cell=[], fallback=[]` + „Schéma je v souladu" (exit 0); nový vypíše `96×48px` a tři pojmenované poznámky | **vůbec** — obě cesty hlásí zelenou a `validate-all.mjs` u ní kontroluje jen `exit ∈ {0,1}` (`validate-all.mjs:187`) | Jeden nástroj, dvě jména → smazat starou. Test, který čte **výstup** nástroje, ne jen exit kód |
| **S2** | **Netrackovaný soubor = zmizí při klonování** | **měřeno:** v `repo/` je 23 trackovaných a 4 netrackované soubory, které hra potřebuje: `.forge/check-schema.py`, `.forge/baseline.py`, `.forge/vision-profile.json`, `.forge/node/vision.test.mjs`. Navíc `assets/asset-registry.json` (netrackovaný) a `tools/` — **9 z 40 `.mjs`** v gitu | Nijak. Na tomto stroji soubory jsou, takže vše zelené | `git ls-files` v CI orchestra. Vada: „šablona v gitu je neúplná" |
| **S3** | **Zelená bez měření (prázdný seznam)** | `check-assets.py:232-252` hledá `assets/sprites/walk_*.png`, **měřeno 0 souborů** (chůze je v `tools/blender/sprites/body_d0_f*.png`, naměřeno 8) → `min_silhouette_iou: 0.80` ze specu se **nikdy neuplatní**. `check-assets.py:102-107` — hudba se neměří, dokud není manifest (**měřeno:** manifest není). `validate-all.mjs:141-145,164` — celá sekce J se přeskočí, když registr chybí | **poznámkou** („animace chůze v projektu není – přeskočeno"), kterou nikdo nečte jako vadu | Pravidlo: každá přeskočená kontrola musí být **pojmenovaná poznámka s počtem** („0 z 8 framů") a v CI `::warning`, ne tichý `continue` |
| **S4** | **Brána závislá na tvaru kódu** | `check-schema.py:212-213` hledá `scripts/level.gd` a `scripts/world.gd` **podle jména**; `verify-level-render.py:209,251` hledá `../spec.json` a `../tiles` **podle umístění**; `check-wiring.py:73` čte jen `scripts/*.gd` (**měřeno:** ze 7 `.gd` v `scripts/` kontroluje 7, ale `_retired/world.gd` a `tools/make_spriteframes.gd` jsou mimo); `baseline.py:60` má `SLEDOVANE = ["assets/sprites", "tools/blender/sprites"]` natvrdo | **měřeno:** po migraci na izometrii brána tiše přestala měřit (fakt 2.1 zadání); dnes se `world.gd` přesunul do `_retired/` a kontroly na něj jsou mrtvé — `check-schema.py:353-356` to aspoň hlásí | Deklarace v konfiguraci hry („vstupní bod vykreslování je X", „sprity jsou v Y"), ne konstanta v nástroji |
| **S5** | **Zdroj pravdy není deklarovaný** | Tři nástroje, tři seznamy: `kontrola-driftu.mjs:21-34` (12 souborů, směr šablona→hra), `sync-sablona-hra.py:23-26` (2 soubory, **různé směry**), `sjednot-sablonu.py` (`agent.yml` zvlášť textovými náhradami). **měřeno:** `kontrola-driftu.mjs` dnes hlásí **1 rozdíl** — `agent.yml` | Jen tím, že se na to někdo podívá; `validate-all.mjs` drift nekontroluje | Jeden manifest `prepisy.json`: soubor → směr → kdo je zdroj. Přidání souboru do `.forge/` je pak **změna manifestu**, ne zapomenutí |
| **S6** | **Dokumentace popírá kód** | `conductor/src/index.ts:31` a `:233` tvrdí, že „`MAX_ATTEMPTS` je v provozu mrtvý kód, protože rozhoduje `pollRuns`, který strop nezná". **kód:** `index.ts:328`, `:394`, `:679`, `:709`, `:1329` ho používají. Skill `orchestra` totéž (invariant 14). `wrangler.toml` má `MAX_ATTEMPTS = "5"` | Nijak — dokumentace je čtenáři zdrojem pravdy | Komentář, který popisuje stav, musí být **u kódu, který ten stav mění**. Tohle je opak pravidla „statická kontrola musí číst kód, ne komentáře" |
| **S7** | **Tichý přenos tajemství do cizího repa** | `install-into-repo.ps1:94-97` kopíruje `.forge` rekurzivně; `.forge/node/.env` **obsahuje reálný `FORGE_SECRET`** (měřeno: soubor existuje, `.gitignore` orchestra ho ignoruje). `.gitignore` hry **`.env` nezná** (měřeno `git check-ignore` → nenalezeno). V herním repu `.forge/node/.env` není, takže **únik ještě nenastal** | Nijak — `git add -A` v agentovi by ho vzal do patche i do PR | Přidat `.env` a `.forge/node/.env` do `.gitignore`, který generuje `install-into-repo.ps1:116-145` |
| **S8** | **Návěstí pro běh orchestra (agent.yml) nemá žádný test** | `test-ci-workflow.mjs` testuje **jen `ci.yml`** (`:39`) — čte `ci.yml` pro hru i šablonu. `agent.yml` **netestuje nic**, přitom je to workflow, který dělá veškerou práci. `validate-all.mjs:91-98` z něj kontroluje **6 řádků textu** | Částečně: `kontrola-driftu.mjs` porovná **strukturu** — a **měřeno, přehlédne chybu**: `FORGE_ATTEMPT` je v šabloně v kroku *Vyber poskytovatele* (`agent.yml:119`) a ve hře v kroku *Spusť agenta* (`games/uo-shadows/.github/workflows/agent.yml:147`); obojí je „env klíč", takže množiny jsou shodné | Test `agent.yml` jako `test-ci-workflow.mjs`: kroky, pořadí, **a že každý `FORGE_*` je v kroku, který ho čte** |
| **S9** | **Kontrola, která čte jen část kódu** | `check-wiring.py:83-89` hledá použití funkce v **celém repu** včetně `tests/`. `games/uo-shadows/tests/run_tests.gd` má **27 podmíněných kontrol** (`if main.has_method(...)` — měřeno grepem). Funkce zmíněná v testu se počítá jako „použitá" | Ne — hlásí „každá funkce je odněkud volaná" (**měřeno**, exit 0, 57 funkcí v 7 souborech) | Testy vyloučit z korpusu „kdo to volá" (nebo je počítat jako **slabší** důkaz a pojmenovat to) |
| **S10** | **Cache, která v CI nemůže nikdy platit** | `vision.mjs:309-334` se ptá `baseline.py kontrola <obrázek>`; `baseline.py:252-253` vyžaduje, aby obrázek byl **uvnitř repa hry**. **měřeno:** `{"v_cache": false, "duvod": "mimo repo hry"}` pro snímek mimo repo; `{"v_cache": true, ...}` pro `assets/sprites/player.png`. V CI se snímek píše do `/tmp/frames` (`ci.yml:109`) | Ne | Vědět a napsat, že „LGTM cache" je **lokální optimalizace**; v CI je vision volána vždy (a to je správně) |
| **S11** | **Dvě hry souběžně: co praskne první** | `index.ts:538-547` — `ROADMAP_MAX_PRS` se počítá **přes všechny hry dohromady**; `wrangler.toml` `MAX_ATTEMPTS/ROADMAP_MAX_PRS/MAX_CONCURRENT` jsou **globální hodnoty**; `index.ts:447-454` — fallback na `env.GITHUB_REPO` = **jedno repo pro všechny**, když registr selže; klíče free LLM jsou **per-repo** (invariant 3) | Až to nastane: druhá hra se přestane dispatchovat, protože první drží PR limit | Zdroj pravdy o limitech **per `game_id`** v tabulce `games`; fallback vypnout (radši nemakat než makat na špatné hře) |
| **S12** | **Nová granule se 3 hodiny nevydá** — **naměřeno, nejsilnější nález** | `index.ts:643-646` zapisuje `updated_at = datetime('now')` při **založení** řádku; dispatch `index.ts:796-804` se ptá **jen na čas** (`rm.updated_at > datetime('now','-3 hours')`). **měřeno:** nová granule → `dispatch: []`; týž řádek starý 4 h → `[1]` | Nijak — `/queue` hlásí `ready`, orchestra prostě 3 h nic nedělá | Rozlišit „řádek vznikl" od „naposledy selhal": budiž `naposledy_selhalo` jako vlastní sloupec, nebo při založení `updated_at = NULL` |
| **S13** | **Cooldown se u selhání přes `/report` obchází** | `index.ts:1329-1336` — `/report` u opakovatelného selhání zapíše **jen `tasks`**, `roadmap.updated_at` **ne**. **měřeno:** stav C → `dispatch: [1]`. `pollRuns` tutéž díru zavřenou má (`:403-405`), `/report` ne | Nijak. Projevuje se jako „granule se zkouší každé 2 minuty a spálí 5 pokusů za čtvrt hodiny" — **přesně to, co měl cooldown zastavit** | Stejný zápis roadmapy v `/report` jako v `pollRuns` |
| **S14** | **Strop pokusů váže úkol, ne granuli → watchdog se nikdy nespustí** | **kód:** `MAX_ATTEMPTS` se čte na `:328`, `:394`, `:679`, `:709`, `:1329` (tedy **není mrtvý kód**, jak tvrdí komentář `:31`,`:233`). Ale `roadmapTick` zakládá pro každý retry **nový úkol** (`:634-640`) s `attempts=0` → smyčka je na **granuli**. Watchdog `ESCALATE_AFTER=8` (`:246`) > `MAX_ATTEMPTS=5` a počítá **běhy úkolu** (`:251`) → **nikdy nedosáhne prahu** | Nijak. Naměřená historie („#128 i #131 měly 5 pokusů") je **pod prahem 8** | Strop a watchdog na **`item_id` granule**, ne na `task_id`; a prah < strop |
| **S15** | **Zámek souborů v dispatch smyčce neblokuje nic** | `index.ts:774-776` staví `locked` z **holých jmen** (`owns` z payloadu), ale `:806` porovnává s **repo-scoped** klíči z `lockKeys` (`:308`, `${repo}/${f}`). Nikdy se neshodují. V `roadmapTick` je tatáž dvojice **správně** (`:558` vs. `:625`) | Nijak — dnes to nemá následek, protože roadmapa hry **nemá žádnou kolizi `owns`** (18 granulí, 0 duplicit) | `locked.add(k)` z `lockKeys` i ve dispatch smyčce. A `lint-roadmapa.py:64` přestane lhát („poběží sériově") |
| **S16** | **Watchdog a stavy, které se zapisují a nikdo je nečte** | `roadmap.status='queued'` (`:646`) — **nikde se na něj neptá**; `runs.status='dispatch_failed'` (`:829`) čte jen `/status` jako text; `syncWithRoadmap` je **odkaz na funkci, která neexistuje** (`:1083`) | Nijak | Buď stav číst, nebo ho nepsat. Mrtvý odkaz v komentáři smazat |

---

## 3. Odpovědi na otázky ze zadání §3

### Blok A — brány a jejich tichá selhání

#### A1. Kolik bran existuje a kde běží

**měřeno** (`git ls-files` + čtení workflow). Brány jsou tři druhy: **tvrdé**
(blokují), **poradní** (neblokují) a **ověřovací** (kontrolují orchestra samu).

| Brána | Kde běží | Co se stane, když se neprovede |
|---|---|---|
| `check-schema.py` | `ci.yml:53` (tvrdá) + `agent.yml`? **ne** — v `agent.yml` není | nic se nezkontroluje, CI zelená → **tichá** (přesně fakt 2.1) |
| Testy hry (`tests/run_tests.gd`) | `ci.yml:59`, `agent.yml:386` | `exit 1`; agent to pozná (`agent.yml:390-423`) |
| `check-assets.py` | `ci.yml:71` (tvrdá) | `exit 1` — ale viz S3: přeskočí, co nenajde |
| `check-wiring.py` | `ci.yml:79` (tvrdá) | `exit 1` — ale viz S9 |
| Smoke (`SCRIPT ERROR`) | `ci.yml:89-94`, `agent.yml:432-437` | `exit 1`. **Pozor:** exit kód hry s chybou je 0, proto se grepuje výstup (`ci.yml:82-84`) |
| `verify-level-render.py` | `ci.yml:120` | `exit 1`, pokud souhlas < 75 %. **měřeno:** funguje; prázdno hlásí selhání (`:296,305-307`) |
| `vision.mjs` | `ci.yml:150` | **neblokuje** (`continue-on-error: true`, `ci.yml:136`) — záměr, zdůvodněný na `ci.yml:127-131` |
| Kontrola parsování GDScript | `agent.yml:265-318` (hra: `:266-362`) | `exit 1`. **měřeno na živém Godotu:** `--check-only` vrátil **exit 1** pro rozbitý skript a **exit 0** pro správný, s textem `SCRIPT ERROR: Parse Error: …` — brána tedy funguje |
| `check-licence.py` | `tools/`, volaná z `validate-all.mjs:167` | **netrackovaná** (měřeno) → při klonu zmizí |
| `validate-all.mjs` | ručně | **měřeno: `✗ NALEZENO 3 PROBLÉMŮ`, ale exit kód 0** → v CI by to prošlo jako úspěch |
| `test-check-schema.py` (17 testů) | `validate-all.mjs:198` | neprojde → `CHYBA` (ale exit kód orchestra je 0) |
| `test-ci-workflow.mjs` (36 testů) | `validate-all.mjs:221` | totéž |
| `baseline.py testy` (24) | `validate-all.mjs:228` | **měřeno:** padá na `PermissionError WinError 5` v sandboxu (viz skill `dsh-prostredi`) — **není to vada testu** |
| `vision.test.mjs` (34) | `validate-all.mjs:202` | **měřeno:** padá na `FileNotFoundError` v tempu — taktéž sandbox |
| `kontrola-driftu.mjs` | ručně | **měřeno: 1 rozdíl, exit 1** |

**Nález A1 (nový):** `validate-all.mjs` — nástroj, který má být jedním během
přes všechny validátory — **končí exit kódem 0 i když najde problémy**
(`validate-all.mjs:252-253` tiskne výsledek, ale nikde nenastaví
`process.exitCode`). V CI ani ve skriptu se tedy nedá spolehnout na jeho
návratový kód. **měřeno:** `EXIT=0` při `✗ NALEZENO 3 PROBLÉMŮ`.

#### A2. Které brány závisí na tvaru kódu

**kód**, seřazeno od nejkřehčí:

| Brána | Na čem visí | Co ji vypne |
|---|---|---|
| `check-schema.py:212-213` | `scripts/level.gd`, `scripts/world.gd` | přesun/přejmenování souboru → **poznámka, ne vada** (`:313,353-356`) |
| `baseline.py:60` | `assets/sprites`, `tools/blender/sprites` | jiná struktura hry → cache tiše neplatí pro nic |
| `check-wiring.py:73,84-89` | `scripts/*.gd`, přípony `.gd/.tscn/.tres` | jiný engine → **kontrola měří 0 souborů a hlásí zelenou** (`:75` vrací prázdné `vady`) |
| `verify-level-render.py:209,251` | `../spec.json`, `../tiles` | jiné umístění → spadne na vestavěné palety (`:258`) a měří špatně |
| `check-schema.py:91-92` | regex na `var|const …cell… := N` | nový tvar deklarace → **dnes hlášeno jako vada** (`:252-257`) — to je opravené |
| `agent.yml:280,334-336` | `git status --porcelain` + `awk '{print $NF}'` | cesta s mezerou → `awk` vrátí jen poslední slovo, soubor se **tiše nezkontroluje** |

**Nejnebezpečnější je `check-wiring.py`**, protože při jiném enginu **nespadne
a neohlásí se** — vrátí `[], ["ve složce scripts nejsou žádné .gd soubory"], ...`
(`check-wiring.py:75`) a `main` vytiskne *„Vše v pořádku: každá funkce je
odněvud volaná."* s `exit 0` (`:169`). To je přesně třída S3.

#### A3. Která brána umí skončit zeleně, aniž něco změřila

Vzory, které jsem hledal a **našel**:

| Vzor | Místo | důsledek |
|---|---|---|
| prázdný seznam bez hlášky | `check-wiring.py:73-75` | „v pořádku" nad 0 soubory |
| `continue` v cyklu | `check-schema.py:390-391` (sprite chybí → přeskoč), `check-assets.py:246` (náhledy), `baseline.py:246` (`_` prefix) | kontrola proběhne nad menším vzorkem, než si člověk myslí |
| přeskočení bez měření | `check-assets.py:232,252` (animace), `:102-107` (hudba); `check-schema.py:208-209` (žádné mapy) | gate se neuplatní |
| podmíněná sekce | `validate-all.mjs:141-145` (registr), `:164` | celá sekce J zmizí |
| `catch` polykající chybu | `index.ts:506` (stav PR se nezjistil → jede se dál), `:548-550` (stav PR → pokračuj), `:604` (`.catch(() => undefined)` u UPSERT) | rozhodnutí o hotovém uděláno bez dat |

**Proti tomu stojí dobré vzory, které je fér vyzdvihnout** (`check-schema.py`):
`:252-257` — nečitelný tvar je **vada**, ne ticho; `:263-266` — chybějící
fallback je **poznámka** s vysvětlením, proč to není vada; `:348-356` —
mrtvá větev je **pojmenovaná**. To je nejlepší část orchestra.

#### A4. Má každá brána offline test se známým chybným případem?

**měřeno** (`Get-ChildItem` v `tools/` a `repo/.forge/node/`):

| Brána | Offline test | Známý chybný případ? |
|---|---|---|
| `check-schema.py` | **ano** — `tools/test-check-schema.py`, 17 testů | **ano** — `_gd_stary_ctverec(16)`, `_gd_nectitelny()`, špatná šířka/výška (`test-check-schema.py` sekce 2–5) |
| `ci.yml` / struktura | **ano** — `tools/test-ci-workflow.mjs`, 36 testů | částečně — testuje strukturu, ne chování |
| `vision.mjs` | **ano** — `.forge/node/vision.test.mjs`, 34 testů (mock API) | ano |
| `baseline.py` | **ano** — `baseline.py testy`, 24 testů včetně mezí `phash` | ano |
| `check-licence.py` | **ano** — `tools/test-licence.py`, 9 scénářů | ano |
| `worker.mjs` | **jen happy path** — `self-test.mjs` ověří `make-dir` a `status === 'success'`; consent, neznámé kroky, timeouty a selhání reportu **netestuje nic** | **ne** |
| `agent.yml` | **žádný test** (test-ci-workflow čte jen `ci.yml`) | **ne** |
| `check-assets.py` | **žádný** | **ne** |
| `check-wiring.py` | **žádný** | **ne** |
| `verify-level-render.py` | **žádný** | **ne** |
| `test-local.ps1` | je to E2E, ale **rozbitý** — `:77-78,84` používají nedefinovanou `$Game` (parametr je `$Project`, `:26`) | — |
| `install-into-repo.ps1` | **žádný** | **ne** |

**Odvozeno:** všech pět bran bez testu je z těch, které v zadání 2.3 figurují
jako slepá místa. To není náhoda — **brána bez testu se nedá poznat jako
nefunkční**, takže zůstane nefunkční.

### Blok B — kdo je zdroj pravdy

#### B5. Proč tři synchronizační nástroje se třemi seznamy?

**kód:** protože každý z nich vznikl pro **jednu konkrétní poruchu** a každá
měla jiný směr:

- `kontrola-driftu.mjs:1-8` — „opraví se šablona a zapomene synchronizovat hra"
  → 12 souborů, směr **šablona → hra**.
- `sync-sablona-hra.py:1-11` — „drift šel na obě strany" → 2 soubory,
  **různé směry** (`CONVENTIONS.md` hra → šablona, `worker.mjs` opačně).
- `sjednot-sablonu.py:1-14` — „do `agent.yml` se zasahuje po blocích" →
  textové náhrady (`:25-71`), protože YAML se nedá bezpečně sloučit.

**Co se stane, když se přidá nový soubor do `.forge/`:** **nikdo si ho
nevšimne.** Všechny tři seznamy jsou ruční (`kontrola-driftu.mjs:21`,
`sync-sablona-hra.py:23`), takže nový soubor `check-schema.py` — což je přesně
to, co se stalo — se do žádného nedostal. Dnes je **měřeno** v seznamu 12
souborů, ale `check-schema.py`, `baseline.py`, `vision.mjs`,
`verify-level-render.py` a `vision-profile.json` v něm **nejsou**.

Důsledek je dnes **neviditelný jen náhodou**: měření hashů ukázalo, že všech
14 kontrolovaných dvojic je dnes **shodných** — protože je někdo ručně
zkopíroval. **Žádné pravidlo to nevynucuje.**

#### B6. Co je zdrojem pravdy pro `providers.json`?

**kód `pick-provider.mjs:27-72`** — a je to promyšlenější, než zadání
naznačuje. Nejde o „runtime fetch vs. lokální kopie", ale o **rozdělení podle
rychlosti změny**:

- **z orchestra (runtime, `raw.githubusercontent`)** — `models`, `baseUrl`,
  `keyEnv` (řádky 39, 62-66): to, co se mění často.
- **z lokální kopie v repu hry** — `anyPriority`, `skromny` (řádky 43-57): to,
  co **rozhoduje o směrování**, a kde CDN cache `raw.githubusercontent`
  způsobila reálnou vadu (komentář `:32-38` uvádí, že stará verze poslala
  granuli `any` na gemini s ~20 dotazy/den).

**Co se stane, když orchestra nebude dostupná** (`:68-72`): `config = LOKALNI`
a vypíše se `providers.json: lokální kopie (orchestra nedostupná)`. To je
**správné chování** — a je **měřitelné**, protože se to hlásí.

**Nález B6 (odvozeno):** tohle rozdělení ale znamená, že **změna směrování
(`anyPriority`) se musí propisovat do každé hry zvlášť** — a to dělá právě
`kontrola-driftu.mjs`, který `providers.json` **v seznamu nemá**
(`kontrola-driftu.mjs:21-34`). Takže dnes: `providers.json` je v obou repech
shodný (**měřeno** hashem), ale **nic to nevynucuje**.

#### B7. Je šablona `repo/` v gitu úplná?

**Ne. měřeno** (`git ls-files repo/` = 23 souborů, `Get-ChildItem` = 27 bez
`__pycache__`):

**Netrackované, a hra je potřebuje:**
- `repo/.forge/check-schema.py` → `ci.yml:53` ho volá → **brána zmizí z CI**
- `repo/.forge/baseline.py` → `vision.mjs:312-313` ho hledá; když není,
  `vCache` vrátí `{v_cache: false}` → vision volá model vždy (funkčně to
  nespadne, ale baseline v nové hře **neexistuje**)
- `repo/.forge/vision-profile.json` → nová hra dostane profil s cizí hrou
- `repo/.forge/node/vision.test.mjs` → 34 testů vision zmizí

**Změněné proti HEAD (8 souborů, `git diff --stat repo/`):** `vision.mjs`
(+422 řádků!), `verify-level-render.py` (+64), `pick-provider.mjs` (+15),
`provider-choice.mjs` (+28), `ci.yml` (+49), `release.yml` (+12),
`provider-choice.test.mjs`, `termux-setup.sh`.

**Co by se stalo, kdyby někdo orchestra naklonoval z gitu a založil novou
hru** (poskládané z měření výše):
1. `python3 .forge/check-schema.py .` v CI → **soubor neexistuje** → CI padne
   hned na prvním kroku brány. **Tvrdé selhání, ne tiché** — a to je dobrá
   zpráva: chybějící soubor je vidět.
2. `vision.mjs` by byl **stará verze** (git HEAD je o 422 řádků zpět) — a ta
   stará verze je ta, u které **testy vision procházejí** (`validate-all.mjs:202`
   dnes padá jen na sandbox, ale nová verze s testem je jen na disku).
3. `release.yml` by v poznámkách k vydání **poslal hráče na `forge-quest`** —
   na jinou hru (`git show HEAD:repo/.github/workflows/release.yml`, řádek 82).
4. `roadmap.json` by dal nové hře **31 granul staré hry**.
5. `install-into-repo.ps1` by **neprošel** — `projects\demo1` neexistuje
   (`:36-38`).

#### B8. Jak se pozná, že hra má zastaralou kopii brány?

**Dnes to pozná jen `kontrola-driftu.mjs`, pro 12 souborů, mezi nimiž brány
nejsou** (potvrzeno měřením `kontrola-driftu.mjs:21-34`). A i tam, kde je
kontrola, kontroluje **jen strukturu u YAML** (`:44-71`) — což **měřeno
propustilo skutečnou chybu** (S8: `FORGE_ATTEMPT` v jiném kroku).

Pro brány samotné existuje **jedna** pojistka: `test-check-schema.py`
kontroluje shodu šablony a hry hashem (`test-check-schema.py`, sekce 0).
Je to **dobrý vzor** — ale je **jen pro jeden soubor** a běží **jen ručně**
(`validate-all.mjs:198`), ne v CI.

### Blok C — orchestra jako systém, který se sám řídí

#### C9. Smyčka dispatch → běh → verdikt → další krok

**kód `index.ts:672-844`**, pořadí v jednom tiku (cron `* * * * *`,
`wrangler.toml`):

1. `pollRuns` (`:689`) — výsledky běžících cloudových úloh z GitHubu.
2. `escalateStuckTasks` (`:693`) — watchdog.
3. Stale-recovery (`:696-717`) — běhy `running` starší než `STALE_MINUTES`
   (90 min) → `timeout`; úkol zpět na `ready` **jen dokud `attempts < maxAttempts`**
   (`:707-711`), jinak `failed` (`:712-716`).
4. `roadmapTick` (`:730`) — doplní granule z roadmapy her.
5. Invariant zombie (`:742-754`) — úkol bez řádku v `roadmap` → `blocked`.
6. Dispatch smyčka (`:764-841`) — dokud je kapacita (`MAX_CONCURRENT`, 5) a
   je `ready` úloha s volnými `owns`.

**Kde může úloha tiše zůstat viset nebo se opakovat** (všechno **kód**):

| Místo | Co se stane |
|---|---|
| `pollRuns:361-363` | Běh se hledá podle `run_key` v `run.name` nebo `display_title`. Když ho tam GitHub nedá, `continue` → úloha zůstane `running` až do `STALE_MINUTES` (max ~90 min, **ne navěky** — to je poctivé) |
| `pollRuns:342` | `per_page=50` **bez stránkování**. Když je v repu víc než 50 dispatchů, běh se nenajde → timeout → **práce se dělá znovu** |
| `roadmapTick:634-647` | Každý tik zakládá nové úlohy pro všechny `ready` granule; starý řádek se přepíše (`ON CONFLICT … task_id=excluded.task_id`) → původní úloha osiří a příští tik ji zablokuje (`:742`) |
| **`roadmapTick:646` + `index.ts:796-804`** | **S12 — nová granule se 3 h nevydá.** Zápis `updated_at=datetime('now')` při vzniku řádku vs. guard, který se ptá jen na čas. **měřeno** (viz verdikt) |
| **`index.ts:1329-1336`** | **S13 — `/report` u opakovatelného selhání neobnoví `roadmap.updated_at`** → cooldown se obchází. `pollRuns` to dělá správně (`:403-405`) |
| `index.ts:707-711` | Poddotaz na `runs.status='timeout'` **není časově omezený** → vyprší-li jinde jiný běh, přepíše se i úkol, jehož současný běh normálně běží → duplicitní dispatch (a zámky se uvolní, protože `locked` se čte z `status='running'`) |
| `index.ts:826-833` | Neúspěšný dispatch vrátí úkol na `ready` **bez ohledu na `attempts`** a běh zapíše jako `dispatch_failed`, který `pollRuns` nečte (`:332`) → opakuje se každý tik bez stropu (scénář „workflow v repu je zakázaný, conductor to nepozná") |
| `index.ts:1329` | `MAX_ATTEMPTS` **živý** — po 5 pokusech `failed` |
| `escalateStuckTasks:245-269` | `ESCALATE_AFTER` **jen notifikuje**, nic nevypíná — a to **záměrně** (`:239-241`). **Ale nikdy se nespustí:** prah 8 > strop 5 a počítá běhy **úkolu**, ne granule (S14) |

**Hlavní nález C9 (kód + měření):** `MAX_ATTEMPTS` **není mrtvý kód.**
Používá se na `index.ts:328`, `:394`, `:679` (stale-recovery) a `:1329`
(report). Mrtvý je jen **komentář**, který to tvrdí (`:31`, `:233`). To je
třída S6 — a je to **horší než mrtvý kód**, protože dokumentace i skill
`orchestra` (invariant 14) na tom staví doporučení.

**Druhý nález C9 (a závažnější): strop i watchdog jsou na špatné entitě.**
Strop `MAX_ATTEMPTS` platí na **úkol**, ale smyčka je na **granuli** —
`roadmapTick` zakládá pro každý retry **nový úkol s `attempts = 0`**
(`:634-640`; nikde se `attempts` nepřenáší ani neresetuje). Granule tedy jede
**donekonečna** a watchdog, který má přesně na to upozornit, má prah 8
a počítá běhy jednoho úkolu (nejvýš 5) → **nikdy nedosáhne**. To je ta
„smyčka, která se opakuje" ze zadání C9 — a **není zastavená ničím**.

**Třetí nález C9:** `roadmap.status='queued'` se zapisuje (`:646`) a **nikde
se na něj nečte** (dispatch čte jen `rm.updated_at`, roadmapTick jen
`'failed'`/`'done'`). Podobně `runs.status='dispatch_failed'`. A komentář
`:1083` odkazuje na funkci **`syncWithRoadmap`, která v celém repu
neexistuje** (logika je inline v `tick:742-755`).

#### C10. Kdo rozhoduje o sloučení?

**kód:** `agent.yml:570-681` — **workflow v repu hry**, ne conductor.
Conductor se jen **ptá**, jestli PR existuje (`pollRuns:370-376`), a to pro
označení „sloučeno automaticky" v notifikaci.

Pravidla (`agent.yml:585-635`): (1) jen `scripts/*` a `assets/*`, (2) nikdy
`tests/`, `.github/`, `.forge/`, `project.godot`, (3) `add+del <= max_lines`
z granule, (4) nezávisle zelené CI `Testy a build` (`:637-664`).

**Jaké změny projdou bez člověka** (kód): malé změny v `scripts/` a `assets/`.
**Odvozeno (a je to vážné):** `assets/*` zahrnuje **i `assets/spec.json`** —
tedy soubor, který je **zdrojem pravdy pro všechny brány**. Model, kterému se
nepovede sprite, si může „opravit" spec a auto-merge to propustí, pokud je
změna do limitu. **`vision.mjs` to nezachytí**, protože neblokuje
(`ci.yml:136`). To je nejkonkrétnější důsledek kombinace „auto-merge pouští
`assets/*`" + „vision neblokuje".

**Pokryté to je?** Částečně: `agent.yml:620` chrání `.forge/`, `tests/`,
`.github/`, `project.godot` — ale **`assets/spec.json` ne**.

#### C11. Co se stane, když selže model uprostřed řetězu?

**kód `pick-provider.mjs:196-219`:** zkouší poskytovatele popořadě, uvnitř
poskytovatele modely popořadě; první odpoví → vyhrává. Když **žádný**
neodpoví, `process.exit(1)` (`:215-219`) → krok *Vyber poskytovatele* padne →
`agent` job padne → `pull-request` se **nespustí** (`agent.yml:492`
`if: needs.agent.outputs.status == 'success'`).

**Kdo to pozná:** `pollRuns` uvidí `conclusion != success` a pošle
notifikaci (`:411-413`); úkol jde zpět na `ready` nebo `failed` podle
`MAX_ATTEMPTS` (`:394`). Stav je vidět v `/failed` a `/queue`
(`index.ts:914-925`).

**Co to udělá s granulí:** `roadmap.updated_at` se zapíše (`:403-405`) →
**cooldown `RETRY_HOURS` (3 h) platí**. Komentář `:397-402` vysvětluje, že bez
toho se granule vydávala za 2 minuty místo za 3 h.

**Nález C11 (kód):** uvnitř jednoho běhu je druhý pokus **jen když model
nezmění kód** (`agent.yml:246-263`). Když běh spadne na **vyčerpané kvótě**,
druhý poskytovatel se **záměrně nezkouší** (`:254-256`) — zdůvodněno měřením
(9 z 13 běhů na rate-limitu). To je dobré rozhodnutí, ale znamená to, že
**výpadek kvóty vypadá stejně jako výpadek modelu** — v notifikaci to
rozeznáte jen podle textu `::warning`.

#### C12. Kde jsou mrtvé části

| Co | Kde | Nález |
|---|---|---|
| `FORGE_CMD` default na smazaný `forge.cmd` | `worker.mjs:83` | Potvrzeno, ale **upřesnění:** default **nemíří** na `…\gameforge\forge.cmd`. `path.join` čtvrté `..` nezkrátí, takže vychází `C:\Users\Ssevc\Local-Deepseek\forge.cmd` — **měřeno `Test-Path` → False**. `gameforge\forge.cmd` je jen v komentáři (`:28`, `:80-82`). Krok `forge:` je nepoužitelný |
| krok `blender:` | `worker.mjs:210-232` | **Neexistuje** (výčet kroků). Skládá se přes `shell:`, a ten se **vždy ptá** (`:300-310`) |
| `kind` nic neřídí | `schema.sql` `tasks.kind`; `agent.yml:539` ho jen tiskne do PR | **Potvrzeno.** `conductor/index.ts:636` ho bere z granule; `worker.mjs` filtruje `FORGE_KINDS`, ale **kroky** ne |
| `test-local.ps1` | `:77-78,84` | **Rozbitý:** nedefinovaná `$Game` (parametr je `$Project`, `:26`) |
| `test-local.ps1:42`, `install-into-repo.ps1:37,86` | odkazují na `forge.cmd new/pull` | **Mrtvé** — `forge.cmd` smazán |
| `install-into-repo.ps1:141` | `/C:*Users*` jako „pojistka proti cestě k secretu" | **Nefunkční vzor** — v gitignore to není platný glob |
| `worker.cmd` | spouští `repo\.forge\node\worker.mjs` | **měřeno:** `games\uo-shadows\.forge\node\.env` **neexistuje** → worker skončí na „Chybí FORGE_URL nebo FORGE_SECRET" (`worker.mjs:394-398`) |
| `bin/task.mjs:12,40` | `gameforge/orchestra/.env` | mrtvá cesta v textu chyby → uživatel hledá neexistující soubor |
| `wrangler.cmd:6-8` | `gameforge\orchestra\wrangler.cmd login` | mrtvé příklady |
| `index.ts:1083` | odkaz na `syncWithRoadmap` | **funkce v repu neexistuje** — mrtvá reference v komentáři |
| `index.ts:646`, `:829` | `roadmap.status='queued'`, `runs.status='dispatch_failed'` | zapisují se, **nikdo je nečte** |
| `over-dokumentaci.py:152` | vyžaduje, aby v `MOZNOSTI-AGENTA.md` stálo „`gameforge\tools\venv\Scripts\python.exe` **neexistuje**" | **kontrola fixuje mrtvou cestu v dokumentaci** — kdo ji uklidí, tomu kontrola spadne |
| `verify-setup.py:11,75` | `router` je v seznamu **očekávaných** složek | penzionovaný zbytek, ale kontrola o něm tvrdí „OK" |
| `tools/git.cmd:4` | `Pouziti: gameforge\tools\git.cmd status` | **jediná nápověda k použití je mrtvá cesta** |
| `tools/test-check-schema.py:44` | cesta `games/uo-shadows` natvrdo | nástroj je **jednohrový** |
| 57 ze 72 skriptů v `tools/` | absolutní `C:\Users\Ssevc\Local-Deepseek\` | **nepřenosné**; `bin/`, `conductor/`, `repo/` a všechny `*.md` jsou přenosné (0 výskytů) |
| `tools/prehled-pokusu.mjs` | čte `.tmp/tasky.json` | **soubor neexistuje** → nástroj nemá vstup |
| `tools/kontrola-schematu.py` | celý soubor | **duplikát** `check-schema.py` **bez opravy** (305 vs. 461 řádků, jiný hash); používá ho `validate-all.mjs` (S1) |
| `tools/test-cooldown.py` | `:39` kopíruje SQL **včetně staré verze** `rm.status = 'failed'`; **nemá assert ani `sys.exit`** → končí vždy 0; scénář `:57` tvrdí „řádek je done", ale vkládá `queued` | test nemůže nic zachytit — a scénářem 6 **posvěcuje** právě vadu S12 |
| `tools/test-eskalace.py` | `:19` `PRAH = 8` natvrdo; `:69-78` podává 8–20 běhů na úkol | testuje **nedosažitelný stav** (S14) → S14 nechytí |
| `tools/mock-conductor.mjs` | neumí `/tick`, `/poll`, `/roadmap`, `/roadmap/reset`, `/tasks/cleanup` | místa s rozhodovací logikou netestuje |
| `kontrola-driftu.mjs:2` | `#!/usr/bin/env node` | kosmetika — ale `validate-all.mjs` ho **nikdy nevolá** |

### Blok D — architektura jako rozhodnutí

#### D13. Co je rozhodnutí a co historický nános

**Rozhodnutí** (má zdůvodnění v kódu a drží):
- **Tvrdá brána vs. poradní kontrola** (`ci.yml:37-51` vs. `:127-131`) —
  zdůvodněné chybovostí vision.
- **Dva joby v `agent.yml`** (`:13-16`) — job s klíči jen čte, job bez klíčů
  zapisuje. Skutečné bezpečnostní rozhodnutí.
- **Soubory granule jako `--file`, závislosti jako `--read`** (`agent.yml:167-223`)
  — vzniklo z naměřené 0% úspěšnosti.
- **Rotace modelů podle `run_key`/`attempt`** (`pick-provider.mjs:122-135`).
- **Cooldown vynucený časem, ne `status`em** (`index.ts:781-804`).
- **`providers.json` rozdělený na „čerstvé" a „směrovací"** (`pick-provider.mjs:32-38`).
- **`blocked` je terminální** (`index.ts:1324-1327`).

**Historický nános** (přežilo svůj důvod):
- `repo/.forge/roadmap.json` — **31 granul hry, která se už nevyvíjí**.
- `install-into-repo.ps1` — celý je postavený na `projects/<Projekt>` a
  `forge.cmd`, tedy na smazané GameForge. **Hlavní onboardingová cesta orchestra
  je mrtvá větev.**
- `bin/task.mjs`, `wrangler.cmd`, `tools/test-local.ps1` — cesty `gameforge\…`.
- `release.yml` v gitu — `forge-quest` (na disku opraveno, necommitnuto).
- `tools/kontrola-schematu.py` — stará verze brány, kterou **validate-all
  stále pouští**.
- `worker.mjs` — `FORGE_CMD` a `blender` mezera.
- `AUTO_MERGE` v `agent.yml` — historicky `inputs.max_lines` (default 60)
  vs. `size_lines` granule; dnes čte `inputs.max_lines`, ale **roadmapa hry
  v `size_lines` nic nemá** — **měřeno:** granule `uo-shadows` `size_lines`
  nemají → limit je vždy 60.

**Konkrétně po GameForge (smazána 30. 9. 2026)** zůstaly jako mrtvé větve:
`install-into-repo.ps1` (celý), `worker.mjs:83`, `bin/task.mjs:12,40`,
`wrangler.cmd:6-8`, `test-local.ps1:34-36,42`, `tools/kontrola-schematu.py`,
`repo/.forge/roadmap.json`.

#### D14. Kdyby orchestra měla vést druhou hru souběžně, co by se rozbilo první?

**Co je správně** (kód): item_id je `{game_id}/{grain_id}` (`index.ts:589`);
zámky `owns` jsou `{repo}/{soubor}` (`:625`, `lockKeys` `:302`); roadmapa se
čte per hra (`:567`); `listGames` vrací jen `active=1` (`:443-446`).

**Co by se rozbilo** (kód + odvozeno):

| Co | Kde | Důsledek |
|---|---|---|
| **Globální strop otevřených PR** | `index.ts:538-547` | `open += prs.length` přes **všechny hry**; komentář to přiznává („limit se hlídá přes všechny hry"). Druhá hra sežere limit první → **první hra se zastaví** |
| **Fallback na jedno repo** | `index.ts:447-454` | `listGames` vrátí při **prázdném nebo nedostupném** registru `[{ game_id: "default", repo: env.GITHUB_REPO, … }]` (`wrangler.toml:28` → `ssevcikm-spec/uo-shadows`). Dva následky: (1) orchestra **dispatchuje dál, i když je hra vypnutá** — vypnutí poslední registrované hry tedy nezabere, přesně proti varování ve skillu; (2) `/tasks/cleanup` pak bere jen aktivní hry (`:1120`), takže s vypnutou hrou **vymaže celou cache roadmapy** (`:1184`) a zablokuje úlohy (`:1174`) — a to i přesto, že `:1107-1108` radí „nejdřív hru vypni, pak cleanup, pak zapni" |
| **Klíče free LLM = jedna hodnota na N repů** | invariant 3 | `providers.json` je společný, ale klíče žijí v Secrets **každého repa**. Denní kvóta je **per klíč**, takže druhá hra **nezdvojnásobí kapacitu** — jen si ji rozdělí. To je **vlastnost free tieru, ne architektury** |
| **Modelový řetězec i workflow jsou jedna hodnota** | `repo/.forge/providers.json`; `WORKFLOW_FILE` (`index.ts:178,811`) | Dvě hry nemůžou mít různý řetězec ani jiný název workflow — tabulka `games` sloupec `workflow` nemá (`schema.sql:73-79`) |
| **`pollRuns` hledá v posledních 50 dispatchech** | `index.ts:342` | Dvě hry → dvojnásobek dispatchů → **běh vypadne z okna** → timeout → práce znovu |
| **`STALE_MINUTES` = 90 vs. timeout kroku = 60 min** | `wrangler.toml`, `worker.mjs:170` | Dlouhý krok na domácím uzlu může conductor prohlásit za mrtvý a **přidělit ho znovu** → dvakrát stejná práce |
| **`worker.mjs` nemá timeout na `fetch`** | `worker.mjs:155-166` | Nedostupný conductor → worker visí navěky |
| **Watchdog a endpointy bez kontextu hry** | `index.ts:263-271` (notifikace), `:930-936` (`/roadmap`), `:943-945` (`/failed`) | U dvou her se z notifikace ani z výpisu **nepozná, které hry se to týká** |

**Verdikt D14:** orchestra je **navržená pro N her v datech** (item_id, owns,
roadmapa per hra) a **pro jednu hru v limitech** (PR strop, kapacita, modelový
řetězec, workflow) i **v úklidu** (fallback a cleanup se chovají nebezpečně,
když je hra vypnutá). Přidat druhou hru je **bezpečné pro souběh souborů**
a **nebezpečné pro kapacitu**; a fallback `GITHUB_REPO` je jediná věc, která
může poslat práci **na špatnou hru** — nebo smazat cache té správné.

**Doplněk k D14 (kód, platí i pro jednu hru):** souborový zámek v dispatch
smyčce je **rozbitý** — `index.ts:774-776` staví `locked` z holých jmen, ale
`:806` porovnává s klíči `${repo}/${soubor}` (`lockKeys`, `:308`). Nikdy se
neshodují, takže **dvě granule se stejnými `owns` se rozjedou paralelně**.
Dnes to nemá následek (roadmapa hry nemá kolizi), ale `tools/lint-roadmapa.py:64`
u kolize tvrdí „poběží sériově, ne paralelně" — což **není pravda**.

#### D15. Je orchestra navržená, aby se dala ověřit, nebo provozovat?

**Obojí, ale ověření je soustředěné do jednoho špatného místa.**

**Ověřitelná je** — a to poctivě: 17 + 36 + 34 + 24 + 9 = **120 offline testů**
(`test-check-schema.py`, `test-ci-workflow.mjs`, `vision.test.mjs`,
`baseline.py testy`, `test-licence.py`), plus `test-cooldown.py` (6 scénářů)
a `test-eskalace.py` (10 scénářů) pro SQL logiku conductora. To je
nadstandardní.

**Ale to ověření je ukotvené v `validate-all.mjs`** — jediném nástroji, který
je má spojit. A ten:

1. **pouští špatnou kopii brány schématu** (`:186`, S1),
2. **končí exit 0 i při `✗ NALEZENO 3 PROBLÉMŮ`** (měřeno),
3. **netestuje `agent.yml`** (S8),
4. **netestuje `worker.mjs`** (jen `make-dir` happy path),
5. **netestuje `install-into-repo.ps1`** — onboarding,
6. **neobsahuje `kontrola-driftu.mjs`**.

**Odvozeno:** kdyby `validate-all.mjs` byl v CI orchestra na `main`,
zachytil by dnes **3 problémy** — a jakmile by se opravil exit kód, **zastavil
by se každý push**. To je přesně ta „brána, která neproběhla", jen o úroveň
výš: **ověření orchestra existuje, ale nemá jak selhat.**

---

## 4. Co je dobré a nemá se to ztratit

Aby analýza nebyla jen výčet vad — tohle je nadstandard a je vidět, že každý
bod vznikl z konkrétní naměřené chyby:

1. **`check-schema.py:246-266`** rozlišuje *„kontrola neproběhla"* (vada) od
   *„není co měřit"* (poznámka). Tuhle distinkci většina systémů nemá.
2. **`check-schema.py:348-356`** pojmenovává mrtvou větev po smazaném souboru.
3. **`baseline.py:69-127`** dokumentuje **meze vlastního nástroje** (phash
   slepý na barvu; degenerace u jednolitého obrázku) a doplňuje je dvěma
   mechanismy. To je přesně pravidlo „hash je nástroj, jehož meze se musí
   změřit".
4. **`agent.yml:13-16`** — oddělení jobu s klíči od jobu se zápisem.
5. **`pick-provider.mjs:32-38`** — rozdělení konfigurace podle rychlosti změny
   kvůli CDN cache.
6. **`test-check-schema.py`** — offline test brány se **známým správným
   i známým chybným** případem, a navíc **kontrolou shody šablony a hry**.
   Tohle je vzor, který by měly mít všechny brány.
7. **`index.ts:781-795`** — komentář, který vysvětluje **dvě iterace téže
   opravy** (první verze se ptala na `rm.status='failed'`, což byla díra).
   Historie rozhodnutí u kódu, ne v changelogu.

---

## 5. Doporučení

### 5.1 Levné a hned (hodiny, žádná změna architektury)

| # | Co | Co to zabrání | Jak se pozná, že to funguje |
|---|---|---|---|
| **L1** | `validate-all.mjs`: nastavit `process.exitCode = chyb ? 1 : 0` a vyměnit `:186` na `repo/.forge/check-schema.py` | Tichá zelená orchestra (S1) i jejího validátoru | `node tools/validate-all.mjs; echo $LASTEXITCODE` → **1** při `✗ NALEZENO`. Dnes (měřeno) → 0 |
| **L2** | Smazat `tools/kontrola-schematu.py` (a všechny `oprav-check-schema-*.py`, které ho ještě potřebují) | Dvě verze jednoho pravidla (S1) | `grep -r kontrola-schematu` v `tools/` → 0 nálezů |
| **L3** | Commitnout šablonu: 8 změněných + 4 netrackované soubory (`check-schema.py`, `baseline.py`, `vision-profile.json`, `vision.test.mjs`) + `assets/asset-registry.json` | Klon orchestra bez bran (S2); `release.yml` s odkazem na `forge-quest` | `git ls-files repo/.forge \| wc -l` → **21** (dnes 17). `git show HEAD:repo/.github/workflows/release.yml \| grep forge-quest` → 0 |
| **L4** | Nahradit `repo/.forge/roadmap.json` **prázdnou roadmapou s komentářem** (ne 31 granul staré hry) | Nová hra dědí cizí plán | Nový klon + `jq '.grains \| length'` → 0 |
| **L5** | Do `.gitignore`, který generuje `install-into-repo.ps1:116-145`, přidat `.env` a `.forge/node/.env` | Tajemství v PR (S7) | `git -C <hra> check-ignore .forge/node/.env` → cesta |
| **L6** | Doplnit `kontrola-driftu.mjs:21-34` o **všech 21 souborů** `repo/.forge/` + `.github/workflows/` — odvozeně z `git ls-files`, ne ručním seznamem | Přidání souboru si nikdo nevšimne (S5) | Přidat nový soubor do šablony → `kontrola-driftu.mjs` ho ohlásí **bez editace seznamu** |
| **L7** | Opravit komentáře `index.ts:31` a `:233` (+ skill `orchestra` invariant 14): `MAX_ATTEMPTS` **živý** | Dokumentace popírá kód (S6) | `grep -n MAX_ATTEMPTS conductor/src/index.ts` → použití na 328, 394, 679, 709, 1329 |
| **L8** | Do `ci.yml` (obojí) přidat `::warning` s **počtem** u každé přeskočené kontroly („animace: 0 z 8 framů") | Zelená bez měření (S3) | Na `uo-shadows` se v CI objeví 2 varování; ve hře, kde animace je, zmizí |
| **L9** | Do `agent.yml:620` (chráněné soubory) přidat `assets/spec.json` | Agent si „opraví" vlastní zdroj pravdy (C10) | PR měnící `spec.json` → komentář „chráněný soubor" |
| **L10** | `test-local.ps1`: `$Game` → `$Project` (`:77-78,84`) nebo smazat | Rozbitý E2E test | `pwsh tools/test-local.ps1 -WhatIf` projde |
| **L11** | **Rozdělit guard v `index.ts:796-804`:** přidat do `roadmap` sloupec `naposledy_selhalo` (NULL při založení) a guard postavit na něm, ne na `updated_at` | **S12 — 3hodinové zpoždění každé nové granule** (nejdražší nález) | Založit granuli → v dalším tiku je dispatchovaná (dnes až za 3 h). Ověřitelné `POST /tick` + `/queue` |
| **L12** | **Doplnit zápis roadmapy do `/report`** (`index.ts:1329-1336`) stejně, jako ho má `pollRuns` (`:403-405`) | **S13 — obcházení cooldownu** | Simulovat selhání přes `/report` → granule se nevydá dřív než za `RETRY_HOURS` |
| **L13** | **Opravit zámek v dispatch smyčce:** `locked.add(k)` z `lockKeys` (`index.ts:774-776`) | **S15 — zámek neblokuje nic** | Dvě granule se stejným `owns` → druhá se nevydá, dokud první běží |
| **L14** | **Přesunout strop a watchdog na `item_id` granule** (a `ESCALATE_AFTER` < `MAX_ATTEMPTS`) | **S14 — watchdog se nikdy nespustí, granule jede donekonečna** | Granule, která selže 6×, se **ohlásí** (dnes ne) |
| **L15** | **Nepoužívat `listGames` fallback k dispatchi:** když je registr prázdný, orchestra **nemá pracovat** | Vypnutá hra se pořád dispatchuje; `/tasks/cleanup` maže cache aktivní hry | `POST /game/active {active:false}` → `/health` `games=0` a orchestra nic nevydá |
| **L16** | Smazat `test-cooldown.py` a `test-eskalace.py`, **nebo** je přepsat tak, aby četly SQL z conductora a měly `assert` + `sys.exit` | Dva testy, které nic netestují a jeden scénář **posvěcuje vadu** | Záměrně rozbít guard v conductoru → test **FAIL** (dnes: projde) |
| **L17** | **Do skillu `dsh-prostredi` doplnit novou past** (naměřena při téhle analýze, viz §6 bod 18) | Falešný negativ při hledání v `.forge` a `.github` — a to je **přesně ta chyba, kterou `AGENTS.md` už jednou zaplatil** u `Select-String` | `grep FORGE_CMD` nad `orchestra/` → **0 nálezů**; nad `orchestra/repo/.forge/` → **5 nálezů**; `Test-Path` soubor **existuje** |

**Poznámka k L3:** `validate-all.mjs` i `test-check-schema.py` obsahují
**absolutní cesty** `C:\Users\Ssevc\Local-Deepseek\…` (např.
`validate-all.mjs:5-6`, `test-check-schema.py:43-44`). Commit je nezničí, ale
**jsou to další místa, kde orchestra není přenosná** — viz §6.

### 5.2 Strukturální (dny, mění kontrakt)

| # | Co | Co to zabrání | Jak se pozná, že to funguje |
|---|---|---|---|
| **ST1** | **`orchestra/prepisy.json`** — jeden manifest: `soubor → směr → kdo je zdroj`. `kontrola-driftu.mjs`, `sync-sablona-hra.py` a `sjednot-sablonu.py` čtou **tenhle jeden soubor** | Tři seznamy, tři směry (S5) | Přidání souboru = jedna řádka manifestu; `sync` i `drift` se chovají shodně |
| **ST2** | **Deklarovaný kontrakt hry: `forge.config.json`** — kde je `spec.json`, kde sprity, které brány se pouští, jaké přípony má kód, kde je vstupní bod vykreslování | `check-wiring.py:73`, `baseline.py:60`, `check-schema.py:212-213`, `verify-level-render.py:209,251` — čtyři natvrdo zapsané cesty (S4) | Nová hra s jiným rozložením složek projde branami bez editace nástrojů |
| **ST3** | **Rozdělit šablonu na `core/` a `tools/<engine>/`** — `core` je engine-agnostický (17 souborů), `tools/godot` je vyměnitelný (3 soubory + 3 kroky) | Univerzálnost za astronomické náklady (otázka A) | Smazat `tools/godot/` → brány `core` pořád běží; přidat `tools/other/` → běží s ním |
| **ST4** | **Test `agent.yml`** — rozšířit `test-ci-workflow.mjs` na oba workflows: kroky, pořadí a **že každý `FORGE_*` je v kroku, který ho čte** | S8 (dnes propuštěná chyba s `FORGE_ATTEMPT`) | Záměrně přesunout `FORGE_ATTEMPT` do jiného kroku → test **FAIL** (dnes: `kontrola-driftu.mjs` OK) |
| **ST5** | **Offline testy pro `check-assets.py`, `check-wiring.py`, `verify-level-render.py`** — vzorem `test-check-schema.py` (fixtura + známý správný i chybný stav) | Tři brány bez testu (A4); všechny tři dnes mají slepá místa | U každé: fixtura, kde kontrola **musí** hlásit vadu, a fixtura, kde nesmí |
| **ST6** | **Onboarding nové hry jako test**: skript, který v tempu založí hru z šablony a pustí všechny brány | `install-into-repo.ps1` je mrtvá větev (D13) | Test projde → onboarding funguje. Dnes neprojde (`projects/` neexistuje) |
| **ST7** | **Limity per `game_id`** v tabulce `games` (`max_prs`, `max_concurrent`, `retry_hours`) a **vypnout fallback** `env.GITHUB_REPO` | D14: druhá hra sežere limit první; fallback pošle práci na špatnou hru | Registr se dvěma hrami → každá má vlastní strop; vypnutý registr → orchestra **nemaká** (místo aby makala na `uo-shadows`) |
| **ST8** | **`STALE_MINUTES` > timeout nejdelšího kroku** (dnes 90 vs. 60 min) nebo srdíčko z workera během kroku | Dvojí práce na domácím uzlu | Worker pošle heartbeat i uprostřed kroku → stale-recovery ho nevyhlásí |
| **ST9** | **Conductor jako testovatelná jednotka:** vytáhnout SQL a rozhodovací funkce do modulu, který jde importovat (`cooldownGuard()`, `watchdog()`, `shouldRequeue()`), a testy psát proti **němu**, ne proti opsané kopii | S12/S13/S14 jsou přesně to, co opakovaně uniká (dva testy dnes opisují SQL a nic nezachytí) | Změnit SQL v conductoru → test **spadne** (dnes: projde, protože test má vlastní kopii) |
| **ST10** | **Parametrizovat `game_id` ve všech nástrojích, které ho mají v kódu** (47 ze 75 souborů, většina 1–3 řádky; vzorem je `status.mjs:18`) a **odstranit absolutní cesty** (57 ze 72 skriptů) — především u `validate-all.mjs` a `zjisti-pages.mjs`, kde by jinak tvrdily, že „stav orchestra = stav `uo-shadows`" | Nástroje jsou jednohrové a nepřenosné; ověření druhé hry by lhalo | Spustit `validate-all.mjs` s `--hra <jiná>` → měří ji; spustit orchestra z jiné složky → nástroje fungují |

**Poznámka k prioritě:** **L1–L4 jsou podmínkou pro cokoli dalšího.** Dokud
`validate-all.mjs` měří špatnou kopii a končí nulou, nemá žádná strukturální
změna jak se ověřit. **L11–L14 jsou ale naléhavější než strukturální práce** —
jsou to hodiny a odstraňují tři vady, které dnes přímo brzdí provoz
(3h zpoždění, obcházení cooldownu, nefunkční zámek).

**Jak se pozná, že je oprava S12/S13 skutečně provedená:** zopakovat měření
z §3 C9 — replika obojího SQL v SQLite. Dnes vychází `[]` / `[1]` / `[1]`;
po opravě musí vyjít **`[1]` / `[1]` / `[]`**. To je test, který se dá napsat
offline a je proti čemu regresi hlídat.

**Poznámka k metodě:** nálezy S12–S15 a C9 jsem **nechal ověřit nezávisle**
(podagent, který kód jen čte a SQL replikuje v SQLite) a **klíčový nález S12
jsem reprodukoval sám** — spustitelný skript je součástí důkazů v §1.2
přílohy. Důvod je v `AGENTS.md`: analýzu má dělat někdo, kdo ten kód nepsal.
Ani jeden z nás ho nepsal, ale **shoda dvou nezávislých čtení je silnější
důkaz než jedno**. Úplné podklady jsou
v `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`.

---

## 6. Co analýza NEZJISTILA

Tenhle oddíl je povinný a je myšlen vážně. Co jsem **neměřil** nebo **nevím**:

1. **Nikdy jsem neviděl orchestra běžet.** Nezavolal jsem `/tick`, nedispatchoval
   úlohu a neotevřel PR. Všechno o conductoru je **čtení kódu** (`index.ts`)
   a **offline replika jeho SQL v SQLite** (to je u S12/S13 skutečné měření,
   ale ne pozorování v provozu). **Že S12 v produkci opravdu nastává, jsem
   nedokázal** — doložené je, že ten SQL takto vrací prázdno, a že `roadmapTick`
   zapisuje právě ten čas. Že to autor nemyslel jako „3h rozestup vlny", se
   z kódu poznat nedá.
2. **Nezjistil jsem, kde dnes reálně běží domácí uzel `pc-domaci`.** `worker.cmd`
   by spadl na chybějící `.env` v herním repu (měřeno: soubor není). Žádný
   jiný spouštěč v repu není. **Nevím, jestli uzel vůbec běží.**
3. **Nezměřil jsem timeout, který zabíjí potomky visícího Godotu.**
   `worker.mjs:174-176` posílá SIGTERM shellu (`shell: true`); zda Godot
   skutečně umře, jsem netestoval (vyžadovalo by to spuštění hry s nekonečnou
   smyčkou).
4. **Nezměřil jsem `per_page=50` v `pollRuns` na reálných datech.** Odvození,
   že při > 50 dispatchech běh vypadne z okna, je z kódu — ale nevím, jak
   daleko je `uo-shadows` od toho limitu.
5. **Nevím, jestli `run-name: "Forge #${{ inputs.task_id }} [${{ inputs.run_key }}]"`
   (`agent.yml:6`) dává `run_key` spolehlivě do `name` i `display_title`** ve
   všech fázích běhu. Kód `pollRuns:361-362` spoléhá na obojí.
6. **Nedotazoval jsem se conductora** (`/health`, `/queue`, `/failed`,
   `/roadmap`). Bylo by to možné (`orchestra/.env`), ale znamenalo by to síťový
   požadavek na běžící systém — a to není čtení. **Stav fronty ani živé D1 tedy
   neznám**, a proto ani N1/N2 nejsou potvrzené z provozu.
7. **Nevím, jestli je `assets/asset-registry.json` zamýšlený jako trackovaný.**
   Je netrackovaný a **měřeno:** bez něj `validate-all.mjs` **tiše přeskočí
   celou sekci J** (6 kontrol). Jestli je to nedopatření, nebo záměr, se
   z kódu poznat nedá.
8. **Nezměřil jsem vision na skutečném snímku.** Model bych zavolat mohl
   (klíče nejsou v `.secrets/`, ale v prostředí), ale **vision je poradní
   a neblokuje**, takže by to nezměnilo žádný nález — a stálo by to kvótu.
   **Přesnost vision tedy zůstává nezměřená** (kód ji sám přiznává: dva běhy
   téhož modelu se mohou rozejít, `vision.mjs:376-384`).
9. **Nezměřil jsem, jak přesně se `kontrola-driftu.mjs` chová u `.json`.**
   U YAML porovnává strukturu (`:44-71`), u ostatních text. U
   `vision-profile.json` tedy porovnává **text** — a to je citlivé na
   kosmetiku. **Nezkontroloval jsem to měřením.**
10. **Nevím, kolik ze 120 offline testů je v CI orchestra.** `deploy.yml`
    je jediný workflow orchestra (`orchestra/.github/workflows/`); **obsah
    jsem nečetl.** `validate-all.mjs` je ruční nástroj, a `test-cooldown.py`
    s `test-eskalace.py` nejsou součástí žádné brány.
11. **Nevím, jestli `research/gameforge-*.md` (historické plány) obsahují
    rozhodnutí, která stále platí.** Četl jsem je jen přes `grep`; je jich
    sedm a mají revizní hlavičky.
12. **Nevím, proč je v orchestra 75 souborů v `tools/`, z nichž jen 24 je
    v gitu.** Může to být záměr (jedenáct z nich jsou jednorázové záplaty)
    nebo nedopatření. **Odvozené riziko:** klon orchestra má **61 z 215
    souborů**. Z 51 netrackovaných v `tools/` je **24 trvalých nástrojů, které
    projekt používá nebo dokumentace předepisuje** (mj. `git.cmd`, `status.mjs`,
    `validate-all.mjs`, `zjisti-pages.mjs`, `kontrola-diakritiky.py`) — to je
    nález, ne kosmetika.
13. **Nespustil jsem ani jednu z jedenácti jednorázových záplat** (zapisují).
    Že jsou idempotentní, je **posouzené staticky** z jejich guardů a z toho,
    že markery už v cílech jsou — nemám bitovou reprodukci „druhý běh nemění
    soubor".
14. **Nezměřil jsem konce řádků u záplat.** Devět z deseti zapisuje
    `write_text` bez `newline=''`, což u LF souboru vyrobí CRLF. Které
    konkrétní soubory by to přeformátovalo, jsem neměřil (vyžadovalo by běh
    se zápisem).
15. **Nepotvrdil jsem, jak GitHub API reaguje na dispatch s nedeklarovaným
    vstupem.** Předpoklad, že vrátí chybu a conductor spadne do cesty
    „dispatch failed se opakuje bez stropu", jsem nedohledal.
16. **Nevím, kdo dnes volá `POST /task`.** Úloha založená mimo roadmapu je
    v dalším tiku zablokovaná zombie invariantem (`index.ts:742-746`), protože
    tabulku `roadmap` plní **jen** `roadmapTick`. Dopad závisí na klientech
    (telefon, CI), které z workspace nevidím.
17. **Nedíval jsem se na roadmapy ostatních her** (`forge-quest`, `idle-realms`,
    `IdleFantasy_Bart`), takže nevím, jestli v nich jsou kolize `owns` — tedy
    jestli se rozbitý zámek (S15) někde projeví.
18. **Naměřil jsem novou past nástroje, která sama způsobuje falešné negativy**
    (a proto ji uvádím jako doporučení L17, ne jen jako zajímavost):
    **`grep` tool přeskakuje skryté složky, když se hledá z rodičovského
    adresáře.** Reprodukovatelné třemi příkazy:

    | hledání | výsledek |
    |---|---|
    | `grep "FORGE_CMD"` nad `orchestra/` | **0 nálezů** |
    | `grep "FORGE_CMD"` nad `orchestra/repo/` | **0 nálezů** |
    | `grep "FORGE_CMD"` nad `orchestra/repo/.forge/` | **5 nálezů** |
    | `Test-Path orchestra/repo/.forge/node/worker.mjs` | **True** |

    Soubor tedy **existuje** a text v něm **je** — hledání z rodiče ho ale
    tiše přeskočí. Totéž pro `.github` (`grep "actions/checkout"` nad
    `orchestra/repo/` → 0; nad `orchestra/repo/.github/` → 5).
    **Důsledek pro orchestra:** celá orchestra bydlí v `.forge/` a `.github/`,
    takže **nejdůležitější soubory projektu jsou pro tohle hledání neviditelné.**
    Je to stejný podpis, jaký má v `AGENTS.md` zapsaný `Select-String`
    (`-SimpleMatch` tiše přeskočí soubory) — jen u jiného nástroje.
    Do té doby platí: **hledej nad konkrétní složkou, nebo soubor přečti celý.**

---

## 7. Závěr ve třech větách

Architektura orchestra **není špatná — je nedokončená v místě, kde se to
nejhůř pozná**: v tom, co je zdroj pravdy a co kopie. Tři nejcennější
vlastnosti (brána se přizná, že neměřila; mrtvá větev se pojmenuje; mez
nástroje se změří) jsou hotové a je třeba je rozšířit na **zbytek bran** —
a to je levné. Co je drahé a mělo by se rozhodnout dřív než později, je
**kontrakt hry** (`forge.config.json` + `prepisy.json`), protože bez něj je
každá nová hra ruční práce a každá nová technologie vidlice.

**A co bych udělal první, kdybych měl jednu hodinu:** opravit guard cooldownu
(`index.ts:796-804` + `:1329-1336`) a zámek (`:774-776`). Jsou to hodiny
práce, odstraňují tři vady, které dnes přímo brzdí každou granuli — a měření
v §3 C9 je zároveň testem, že oprava sedla.

---

## 8. Dodatek: nálezy z 1. 10. 2026 (odpoledne)

**Kdo to psal:** **jiná session, než která psala §1–§7** — a je to záměr: autor
analýzy není nezávislý reviewer svých vlastních závěrů (`AGENTS.md`, „Kdy práce
patří do nové session"). **Rozsah:** jen doplnění. Je to **dodatek, ne přepis** —
původní znění §1–§7 **zůstává beze změny**, včetně míst, která tenhle dodatek
zpřesňuje. **Značky:** stejné jako v úvodu dokumentu (**měřeno** / **kód** /
**odvozeno** / **nevím**).

Sedm nálezů, které v době psaní §1–§7 k dispozici nebyly. Dva z nich zakládají
**nové třídy selhání** (S17 a S18 v §8.8), ostatní jsou **instance tříd z §2** —
a to je samo nález: třídy popsané ráno čtením kódu se odpoledne potvrdily
**v provozu**.

| # | Nález | Třída |
|---|---|---|
| **8.1** | Běh #241 spadl na konstantách z Godotu 3 → `hud.gd` se nikdy nedostal do repa | **S17 (nová)** |
| **8.2** | Zelený conductor nad červeným repem | **S18 (nová)** |
| **8.3** | Tři mrtvé brány, které se tváří jako živé | S16 (instance) |
| **8.4** | `check-schema.py` tiše přestal měřit — dnes opraveno a hlídané | S3 + S4 (instance) |
| **8.5** | Tři verze `vision.test.mjs` pod stejným jménem | S5 (instance) |
| **8.6** | Dvě jména téhož pole: `popis_stylu` vs. `styl_popis` | S5 (instance, obecná past kontraktů) |
| **8.7** | Odkaz na projekt se odvozuje z názvu repa | L3 (potvrzení v provozu) |

**odvozeno:** zařazení do tříd je přiřazení autora dodatku k řadě z §2; číslování
**S17/S18 navazuje** na S1–S16 a původní řada se nemění.

### 8.1 Běh #241: model použil konstanty z Godotu 3 v projektu na Godotu 4

**měřeno:** běh **#241** (`agent.yml`) selhal na
`Cannot find member "ALIGN_LEFT" in base "Label"`. Model napsal konstanty
z **Godotu 3** do projektu na **Godotu 4**; `scripts/hud.gd` se proto **nikdy
nedostal do repa** (granule `ui.hud`; `CONVENTIONS.md` to zaznamenává i s řádky —
`ALIGN_LEFT` na `:8`, `VALIGN_TOP` na `:9`).

**Následek (kód):** do `CONVENTIONS.md` — do **obou kopií** (šablona
`orchestra/repo/` i hra `games/uo-shadows/`) — přibyla sekce **§1h** „Konstanty
z Godotu 3 v Godotu 4 NEEXISTUJÍ" s tabulkou překladu:

| Godot 3 | Godot 4 |
|---|---|
| `ALIGN_LEFT` / `ALIGN_CENTER` / `ALIGN_RIGHT` | `HORIZONTAL_ALIGNMENT_LEFT` / `…_CENTER` / `…_RIGHT` |
| `VALIGN_TOP` / `VALIGN_CENTER` / `VALIGN_BOTTOM` | `VERTICAL_ALIGNMENT_TOP` / `…_CENTER` / `…_BOTTOM` |
| `Label.align` / `Label.valign` | `Label.horizontal_alignment` / `Label.vertical_alignment` |
| `Label.autowrap` (bool) | `Label.autowrap_mode` (`TextServer.AUTOWRAP_*`) |
| `connect("signal", self, "_on_x")` | `signal.connect(_on_x)` |
| `yield(x, "signal")` / `yield(x, "completed")` | `await x.signal` / `await x.completed` |
| `export var` / `onready var` | `@export var` / `@onready var` |
| `OS.get_ticks_msec()` | `Time.get_ticks_msec()` |
| `instance()` | `instantiate()` |
| `PoolStringArray` a ostatní `Pool*Array` | `PackedStringArray` a ostatní `Packed*Array` |

a pravidlo **„nepoužij konstantu, kterou jsi neviděl v tomhle repu"**.

**Nová třída selhání (S17): agent neumí poznat verzi enginu z kontextu, když ji
konvence neuvádí.** Projekt je Godot 4, model měl ale v trénovacích datech víc
Godotu 3 — a nic v repu mu neřeklo, která verze platí, dokud to neuhodl špatně.
**odvozeno:** tohle selhání je **hlasité** (parse error shodí běh, nezůstane tichá
zelená) — cena je v ušlém běhu a v tom, že soubor do repa nedorazí, protože běh
skončil dřív.

### 8.2 Zelený conductor nad červeným repem (nová třída tichého selhání)

**měřeno živě 1. 10. 2026.** `main` hry měl **7,5 h červené CI** — a conductor
přitom hlásil:

| Co conductor hlásil | Jaký byl stav cíle |
|---|---|
| `/health` → **`ok: true`** | `main` hry **červené 7,5 h** |
| `/health` → **`ready: 7`** | každá z těch granul by spadla ve stejném kroku |
| `/failed` → **prázdné** | selhaly **běhy**, ne **úlohy** — v `/failed` není co vidět |

**Důvod (kód + měření):** conductor **stav CI cílové hry vůbec nezná**. Sleduje
své úlohy a běhy, ale ne to, jestli je repo, do kterého posílá práci, zelené.
Zelený řídicí systém tedy není důkaz, že práce probíhá — je to jen důkaz, že
*o stavu cíle* neříká nic.

**odvozeno:** dodatek zároveň částečně uzavírá §6 bod 6 („nedotazoval jsem se
conductora"). `/health` a `/failed` byly tentokrát dotázané **živě** — a přesně
to ukázalo rozdíl mezi „zeleným conductorem" a „červeným repem".

**Obrana do budoucna** (návrhy z `PLAN-ORCHESTRA-AI-AGENTI.md` §N0, oba
**otevřené**):

| # | Co | Co to zabrání |
|---|---|---|
| **N0.2** | **Brána na závislosti bran** — každá brána, která importuje knihovnu mimo stdlib, ji musí mít v kroku, který ji pouští | Konkrétní podnět: `check-schema.py` importoval `PIL` **uvnitř funkce** a `ci.yml` ho v tom kroku **neinstaloval** → brána spadla vždy a vypadalo to jako vada měřeného projektu |
| **N0.3** | Conductor si **drží poslední běh CI na `main`** a zveřejní ho v `/health` | `/health` bude moct ukázat `main_ci: failure` místo `ok: true` |

### 8.3 Tři mrtvé brány, které se tváří jako živé

**měřeno** — tři místa, která vypadají jako rozdělaná práce, ale nikdo je nečte:

| „Brána" | Co je naměřeno | Proč nemůže nic udělat |
|---|---|---|
| **LGTM baseline** (`games/uo-shadows/.forge/vision/baseline.json`) | **272 položek** se `schvalil: agent-init` (tytéž hlásí `baseline.py stav` jako „272 schválených"), nad nimi příznak `_ceka_na_lgtm: true` | schválil je **agent**, ne člověk — a čeká se na LGTM, které nikdo nedá |
| **role `worker` / `judge`** (`vision-profile.json`) | **nečte je žádný kód** (`vision.mjs` ji nikde nečte; sám profil to v `_poskytovatele` přiznává: „`role` je dnes jen dokumentace") | dvě role = jen popis záměru; řetěz je obyčejný fallback |
| **verdikt visionu** | pouští se **jen v `ci.yml`** a s `continue-on-error: true` | **agent ho nikdy nedostane** — nemá ho odkud přečíst (§3 C10 to má jako „vision neblokuje"; tohle je druhý důsledek téhož) |

**Navíc (měřeno):** `acceptance` a `provides` z roadmapy **nečte žádný kód** —
v orchestra se `acceptance` vyskytuje jedinkrát, a to jako vysvětlivka formátu
v `_popis` (`roadmap.json`); čtenáře nemá.

**Zařazení:** instance **S16** („stavy, které se zapisují a nikdo je nečte"),
rozšířená z dat na **konfiguraci a brány**. Je to přesně ta „brána, která čeká na
vstup, jenž nikdy nepřijde" — vypadá jako rozdělaná práce, takže se s ní počítá.

### 8.4 `check-schema.py` tiše přestal měřit — a pojistka, která to už hlídá

**měřeno.** Brána hledala `var cell := 16`; po izometrické migraci je v kódu
`const CELL_W_DEFAULT := 96` a `CELL_H_DEFAULT := 48` → **regexy nenašly nic** →
cyklus proběhl nad **prázdným seznamem** → **zelená**. Přesně vzor z §3 A3.

**Prozrazoval to jediný řádek:** `level.gd: výchozí cell=[], fallback=[]` — kde
`[]` vypadá jako **naměřená nula**, ne jako „neměřeno". Je to táž past, kterou má
`AGENTS.md` zapsanou jako „nula a ‚nezměřeno' nejsou úspěch".

**Už je to opraveno** — ale patří to do tříd selhání (instance **S3 + S4**),
protože kdyby to nikdo nezahlédl, brána by dál hlásila zelenou nad nulou.

**Pojistka (kód):** `orchestra/tools/test-check-schema.py` — **17 offline testů**
se **známým správným i známým chybným** repem, zapojený do `validate-all.mjs`. Je
to týž vzor, který §4 bod 6 označuje za vzor pro všechny brány — teď je u něj
i **naměřený důvod, proč vznikl**.

**Při psaní těch testů se odhalilo (měřeno):**

| Co | Kolik | Co to bylo |
|---|---|---|
| chyby ve **vlastním regexu** testu | **4** | case sensitivity, záměna os, první vs. poslední deklarace, `\b` po podtržítku |
| **skutečná vada** | **1** | šablona `orchestra/repo/` a herní repo se **rozešly** — proto test hlídá i **shodný hash obou kopií** |

**Poznámka k metodě:** test, který při psaní nic nenajde, je slabý test. Tady
našel čtyři vady v sobě a jednu ve skutečnosti — a ta jedna je přesně ta
„kontraktní brána" z §4 bodu 6, jen tentokrát **měřená**.

### 8.5 Tři verze `vision.test.mjs` pod stejným jménem — a nejsou rovnocenné

**Naměřeno SPUŠTĚNÍM, ne odhadem** (1. 10. 2026):

| Soubor | Velikost | Výsledek spuštění | Poznámka |
|---|---|---|---|
| `vision.test.mjs` (root workspace) | 11 983 B | **5 OK / 23 chyb** | osiřelá rozbitá kopie; padá na `Cannot find module 'C:\Users\Ssevc\vision.mjs'`; **kandidát na smazání** |
| `orchestra/repo/.forge/node/vision.test.mjs` | 17 576 B | **36/36** | šablona |
| `games/uo-shadows/.forge/node/vision.test.mjs` | 13 318 B | **28/28** | starší kopie; chybí jí **8 testů** včetně testů na `popis_stylu` |

**Kód** `vision.mjs` je v obou kopiích **shodný** (SHA256
`ce67762da1631d61d7c7d151800a52e2da91a373f6d7ca631e3d0eaeeec57e6c`) — rozešly se
tedy **jen testy**. A `vision.test.mjs` **není** v seznamu souborů, které hlídá
`kontrola-driftu.mjs` (**ověřeno: 0 výskytů**) — proto si driftu nevšiml.
Instance **S5**.

**Dvě věci, které z toho plynou:**

1. **Stejné jméno souboru nic neznamená.** Tři soubory téhož jména mají tři různé
   obsahy a dva z nich nejsou rovnocenné (36 vs. 28 testů). Kdo si přečte jen ten
   nejbližší, měří něco jiného, než si myslí.
2. **Rozpor s §3 — VYŘEŠEN 1. 10. 2026 večer, a §3 měl pravdu:** §3 A1 a §3 D15
   uvádějí u `vision.test.mjs` **34 testů**; spuštění dává **36/36**. **Není to
   rozpor, ale čas:** analýza vznikla **před** commitem `ebaabea`, a ten sám
   v commit message říká doslova *„+ 2 nové testy (**34 → 36**)"* (testy
   „profil s `popis_stylu` styl NESMÍ ztratit" a „profil bez stylu nespadne").
   **Důkaz (měřeno):** `git show eac2790:repo/.forge/node/vision.test.mjs`
   je starší verze a `git show ebaabea -- repo/.forge/node/vision.test.mjs`
   hlásí **+24 řádků, změněn jen tenhle soubor**.
   **Poučení, které platí pro každou takovou kontrolu:** než označíš cizí číslo
   za zastaralé, podívej se do **historie souboru** — rozdíl 34 vs. 36 nebyl
   chyba dokumentu, ale **doklad, že F0.3 přidal dva testy**. (Táž past jako
   „počet testů se nečte staticky": statický počet `test(` dává 40/42, tedy
   nesedí ani na jednu verzi — čte se **výstup běhu**.)

### 8.6 Dvě jména téhož pole: `popis_stylu` vs. `styl_popis`

**kód + měřeno:** šablona psala **jedno** jméno, `vision.mjs` četl **jen to
druhé**. Hra by o styl přišla **tiše** — žádná chyba, žádný červený běh, jen
prázdný popis stylu, který nikdo nepostrádal.

**Opraveno:** kód čte **obě jména** (`vision.mjs:140,144`) + **2 nové testy**.

**Tohle je obecná past kontraktů, ne orchestra-specifická:** kde jeden soubor
zapisuje a druhý čte a **nikde není deklarováno, jak se to pole jmenuje**,
rozejití se nepozná — stejná třída jako S5, jen o úroveň níž (uvnitř jedné
dvojice souborů). Hlídá to jen test se známým správným **i** chybným stavem
(§4.6).

### 8.7 Odkaz na projekt se odvozuje z názvu repa

**měřeno:** v `release.yml` byl **natvrdo** odkaz na `…/forge-quest/`. To je
**jiná živá hra** s vlastními GitHub Pages — uživatel, který odkaz otevřel,
**hrál jinou hru**, než kterou si chtěl zahrát.

**Dnes (kód):** `release.yml` používá `…/NAZEV-REPA/` — v šabloně doslova
`NAZEV-REPA`, ve hře se dosadí název repa (`uo-shadows`). §1 a L3 to měly vedené
jako „v gitu je stará verze"; dodatek přidává, **co to znamenalo pro uživatele** —
nebyl to mrtvý odkaz, byl to odkaz na jinou živou hru.

### 8.8 Nové třídy selhání (pokračování řady z §2)

| # | Třída selhání | Naměřené místo | Jak se to pozná dnes | Co by to odhalilo |
|---|---|---|---|---|
| **S17** | **Model neumí poznat verzi enginu z kontextu** — píše konstanty z jiné major verze | běh **#241**: `Cannot find member "ALIGN_LEFT" in base "Label"` (`scripts/hud.gd:8`, `VALIGN_TOP` na `:9`); `hud.gd` se **nikdy nedostal do repa** | **hlasitě** — parse error shodí běh (to je dobrá zpráva); cena je ušlý běh a soubor, který do repa nedorazí | Verze enginu **uvedená v konvencích** + tabulka překladu (§1h) + pravidlo „nepoužij konstantu, kterou jsi neviděl v tomhle repu" |
| **S18** | **Zelený řídicí systém nad červeným cílem** | conductor: `/health` → `ok: true`, `ready: 7`, `/failed` prázdné; `main` hry: **7,5 h červené CI**; selhaly **běhy**, ne **úlohy** | **vůbec** — conductor stav CI cílové hry nezná; jeho vlastní stav je zelený a vypadá to jako „nemá co dělat" | **N0.3** — poslední běh CI na `main` v `/health` |

**odvozeno — proč to nejsou jen dvě další položky do seznamu:** S17 ukazuje, že
**konvence je taky brána** (co v ní není, model neuhodne); S18 ukazuje, že **stav
řídicího systému není stav práce** — a to je poprvé, co se ta třída potvrdila na
živém systému, ne čtením kódu.

---

**Poznámka k původu (povinná):** Tenhle dodatek **nepsala** session, která psala
§1–§7. Je to záměr — *autor analýzy není nezávislý reviewer* svých vlastních
závěrů (`AGENTS.md`, „Kdy práce patří do nové session"). A je to **dodatek, ne
přepis**: původní znění §1–§7 **zůstává**, včetně míst, která dodatek zpřesňuje
nebo doplňuje; kde se obojí rozchází, je to řečeno na místě (§8.5 bod 2).

**Poznámka k datu — VYŘEŠENO 1. 10. 2026 večer (dřív tu stálo „nevím"):**
hlavička §1 říká „1. 10. 2026, večer"; `HANDOFF.md` ji označuje za hotovou
**ráno** a soubor měl při vzniku dodatku mtime **9:34**. **Rozhodující důkaz je
uvnitř dokumentu samotného:** §1 popisuje stav **před F0** — „8 změněných
trackovaných souborů", „**31 granul** staré hry", `repo/.forge/vision-profile.json`
s natvrdo `"hra": "uo-shadows"`, a §521 to říká výslovně: *„`release.yml` v gitu —
`forge-quest` (na disku opraveno, **necommitnuto**)"*. To je stav, který padl
commity `eac2790`, `ebaabea` a `525d45b` **během téhož dne**.
**Závěr:** analýza je z **1. 10. 2026 dopoledne** (mtime 9:34) a slovo „večer"
v hlavičce §1 je **nepřesné** — patří k němu dovětek: *analýza popisuje stav
před F0; kde se její čísla rozcházejí s dneškem, je to tím, a ne že by byla
špatně měřená.* Původní text hlavičky se nemění, protože rozdíl je vysvětlený
tady (a mtime je ověřitelný: `Get-Item` na tom souboru).

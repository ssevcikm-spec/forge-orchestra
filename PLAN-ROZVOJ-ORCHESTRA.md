# Plán rozvoje Forge orchestra — NÁVRH K REVIZI

> **Co tenhle dokument JE:** plán. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 1. 10. 2026 · **Stav:** 🟢 **F0 HOTOVÁ** (F0.1–F0.6, commitnuto
a pushnuto); **F1–F5 neschválené, neimplementované**
**Vzniklo z:** `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (nálezy S1–S16) +
`ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` (podklady) + studium odborných
zdrojů (§1)

> **Jak tenhle dokument číst.** Je to **návrh k ladění**, ne zadání. Každá
> kapitola má na konci **„K rozhodnutí"** — otázku, na kterou má odpovědět
> uživatel, ne agent. Nic z toho se neimplementuje, dokud fáze neschválíš.
>
> **Co v plánu záměrně NENÍ:** termíny a odhady v hodinách. Namísto toho je
> u každé fáze **„Hotovo znamená"** (měřitelná podmínka) a **„Co to blokuje"**.
> Odhad času u práce, kterou jsem sám neprováděl, by byl dohad.

---

## 0. Shrnutí pro netrpělivé

| Otázka | Odpověď v jedné větě |
|---|---|
| Co je hlavní problém? | **Není deklarováno, co je jádro a co kopie** — a tak se každá kopie rozejde a každá brána může tiše přestat měřit. |
| Co je hlavní technický dluh? | **Přetížený `updated_at`** v tabulce `roadmap` (nese „vzniklo" i „naposledy selhalo") → odtud 3h zpoždění každé nové granule a obcházení cooldownu. |
| Opravit nejdřív, nebo přestavět? | **Opravit.** Tři provozní vady jsou hodiny práce a přímo brzdí každou granuli — přestavba by se stavěla na rozbitém základu. |
| Je orchestra univerzální? | **Jádro ano (17 z 24 souborů), obálka ne.** Univerzalitu nedrží kód, ale **nedeklarovaný kontrakt** + **jednohrové nástroje** (47 ze 75) + **nepřenosné cesty** (57 ze 72 skriptů). |
| Je orchestra očištěná od `forge-quest`? | **Conductor ano (0 výskytů).** Obálka už taky: roadmapa šablony je **prázdná** (bylo 31 granul staré hry), `vision-profile.json` **nemá žádné** cizí údaje, `release.yml` odkaz odvozuje z názvu repa. |
| Co je nejlevnější, co odemkne nejvíc? | **Deklarovaný kontrakt** (`forge.config.json` + `prepisy.json`). Hodiny práce, a řeší třídy S2/S4/S5 naráz. |
| Co je nejdražší a má se rozhodnout teď? | **Kdo vlastní soubory v herním repu** (šablona vs. hra). Rozhodnutí je zdarma, jeho odklad ne. |
| Co dělat PRVNÍ | **Fáze 0** (§3): commitnout šablonu, aby „zdroj pravdy" vůbec existoval. **✅ HOTOVO 1. 10. 2026** — všech šest kroků F0.1–F0.6 je commitnutých a pushnutých. **Další na řadě je F1** (smyčka), ale je to zásah do běžícího orchestra → rozhodnutí uživatele. |
| Co je past, do které se dá snadno spadnout? | Vyrobit z orchestra **platformu** (registr brán, plugin systém, abstrakce nad enginy) dřív, než je opravená smyčka a než existuje druhá hra, která by abstrakci ospravedlnila. |

---

## 1. Co říká obor (a co z toho plyne pro orchestra)

Prošel jsem čtyři oblasti, které odpovídají našim čtyřem problémům. **Není to
teorie pro teorii — u každé je hned důsledek pro orchestra.**

### 1.1 Architektonické „fitness functions"

Zdroj: [Building Evolutionary Architectures — fitness functions](https://raw.githubusercontent.com/MahatmaFatalError/learning-notes/refs/heads/master/architecture-design/Architectural-fitness-functions.md)
(Neal Ford, Rebecca Parsons, Patrick Kua).

Myšlenka: kromě testů, že systém **funguje**, existují kontroly, že si systém
**drží architektonické vlastnosti**. Dělí se na:

| Dimenze | Význam pro orchestra |
|---|---|
| **atomická vs. holistická** | atomická = „brána měří X"; **holistická = „brána se vůbec spustila a změřila aspoň něco"** ← přesně to, co nám chybělo (S3, S12) |
| **spouštěná vs. spojitá** | naše brány jsou spouštěné v CI; chybí **spojitá** (watchdog, který se nikdy nespustí = S14) |
| **statická vs. dynamická** | náš strop pokusů je statická hodnota; správně má být **dynamický** (8 pokusů je hodně pro kód, málo pro flaky test) |
| **automatická vs. ruční** | `read_image` a kontaktní arch jsou legitimně **ruční** fitness funkce (a je fér to tak nechat) |

**Důsledek pro orchestra:** dnešní brány jsou **všechny atomické**. Chybí
holistická funkce „**každá brána musí doložit, že proběhla a kolik toho
změřila**". To je přímá odpověď na nejdražší nález analýzy (S12: brána tiše
přestala měřit) a je to **levné** — viz F2.

### 1.2 Šablony a jejich rozpad (template drift)

Zdroj: [cruft](https://cruft.github.io/cruft/) — nástroj, který vznikl přesně
pro náš problém. Autor to popisuje slovy: *„většina nástrojů na tvorbu projektů
ze šablony vám nechá zkopírovaný kód na celý život projektu… cruft je jiný:
pomáhá tu boilerplate spravovat."*

Co cruft dělá (a co je přenositelné jako **návrhový vzor**, ne jako závislost):

| Prvek cruftu | Co řeší u nás |
|---|---|
| `.cruft.json` v **každém** downstream projektu, s **commitem šablony**, ze kterého projekt vznikl | dnes neexistuje — **nikdo neví, z které verze šablony ta která hra je** (S5) |
| `cruft check` → nenulový exit, když projekt zaostal | dnes `kontrola-driftu.mjs` zná 12 souborů ze 24 a **není v `validate-all.mjs`** (S5/B8) |
| `skip` seznam (i glob vzory) — soubory, které se **nikdy neaktualizují** | dnes tři nástroje se třemi seznamy a **různými směry** (S5). Skip seznam je ta chybějící půlka: „tohle je vaše, do toho nesahej" |
| `cruft diff` — přesně co se rozešlo | dnes `kontrola-driftu.mjs` u YAML **přehlédne i skutečnou chybu** (S8) |

**Důsledek pro orchestra:** řešení není „lépe synchronizovat" — je to
**deklarovat vlastnictví**. Každá hra musí mít soubor, který říká: „jsem
z šablony `forge-orchestra` v commitu X, tyhle soubory jsou moje a na ty
nesahej". To je i odpověď na *„nové hry dědí pozůstatky"*: co je označené jako
**vlastněné hrou**, se do nové hry nekopíruje.

### 1.3 Sdílená konfigurace napříč repy

Zdroj: [Renovate — shareable config presets](https://docs.renovatebot.com/config-presets/)
a [presets](https://docs.renovatebot.com/key-concepts/presets/).

Renovate řeší totéž, co naše `providers.json` (jedna konfigurace, N repozitářů),
a má na to vyzrálý model:

- konfigurace **žije v jednom repu** a ostatní na ni odkazují
  (`github>vlastnik/repo`, `github>vlastnik/repo//cesta/soubor`),
- dá se **připnout na tag** (`#1.2.3`) — tedy „beru vědomě tuhle verzi",
- `ignorePresets` umožní **cíleně vynechat** část sdílené konfigurace,
- a hlavně: **kdo odkazuje, nemusí nic kopírovat.**

**Důsledek pro orchestra:** `pick-provider.mjs` už dělá něco velmi podobného
(runtime fetch `providers.json` z orchestra + lokální fallback) — **a je to
jedna z nejlépe navržených částí orchestra** (analýza B6). Vzor je tedy
správný a je potřeba ho **rozšířit, ne vymyslet znovu**: hra má dostávat
konfiguraci z orchestra, a to, co drží lokálně, má být výslovně označené jako
„vědomá odchylka".

### 1.4 Kontraktní testy proti divergenci

Zdroj: [Preventing API Drift with Contract Tests](https://adamwathan.me/2016/02/01/preventing-api-drift-with-contract-tests/)
(a obecně praxe contract testingu). Princip: když existují **dvě
implementace téhož**, nesmí se kontrolovat každá zvlášť — kontroluje se
**shoda mezi nimi**.

**Důsledek pro orchestra:** máme **dvě kopie brány** (`repo/.forge/check-schema.py`
a `games/uo-shadows/.forge/check-schema.py`) a **dvě kopie šablony** (disk a git).
Kontraktní test je přesně to, co dělá `test-check-schema.py` (hlídá **shodný
hash** obou kopií) — to je nejlepší vzor v celé orchestra a má se zobecnit.

### 1.5 Co z toho **neberu** (a proč)

Aby se z plánu nestala platforma:

| Vzor | Proč ho nepoužiju |
|---|---|
| Cookiecutter/cruft jako **závislost** | orchestra je Node + Python bez build systému; přidávat Python nástroj na generování projektů je další pohyblivá část. **Vezmu vzor, ne nástroj** |
| Backstage / IDP (interní portál) | pro dvě hry je to absurdní. Katalog her je tabulka `games` a ta funguje |
| Monorepo (sloučit orchestra + hry) | herní repa **musí** být samostatná — je to podmínka použití GitHub Actions zdarma (analýza, invariant 3) |
| Plugin systém pro enginy | **předčasné.** Až bude druhý engine, vysvitne, kde je skutečný šev. Dnes víme jen, že jich je 17 z 24 souborů nezávislých — což je dobrý předpoklad, ne důkaz |
| Vlastní DSL pro roadmapu | YAML/JSON s `grains` funguje a je validovaný. DSL by přidal parser, který se taky může tiše rozbít |

---

## 2. Rozhodovací kritérium: co je „zdarma" a co je „astronomické"

Uživatel zadal: *„pokud je to levné či zdarma, měla by umět přepínat mezi
technologiemi, koncepty, modely; ale ne za cenu astronomických nákladů."*

Navrhuji **jedno měřitelné kritérium**, aby se „levné" nehádalo:

> **Změna je levná, když se vejde do jednoho souboru a nevyžaduje
> synchronizaci na N místech.** Je drahá, když se musí projevit v každé hře
> zvlášť.

Podle toho:

| Věc | Cena dnes | Podle kritéria |
|---|---|---|
| Přidat poskytovatele LLM | 1 soubor (`providers.json` v orchestra) | **zdarma** — hry si ho stáhnou za běhu |
| Přidat bránu (např. licenční) | 1 soubor + řádek v `ci.yml` **v každé hře** | **levné, ale ne zdarma** — roste s počtem her |
| Vyměnit Godot za jiný engine | 3 soubory + 3 kroky, **ale dnes zadrátované cesty** | **střední** — a šlo by to na zdarma, kdyby existoval kontrakt |
| Přidat druhou hru | registr + roadmapa + **~35 nástrojů o 1–3 řádcích** + **57 absolutních cest** | **drahé** — a to je ta pravá „astronomie", kterou je potřeba odstranit |
| Přidat jiný *druh práce* (ne hra) | dnes nemožné | **mimo rozsah** — orchestra má v názvu hry a je to fér |

**Z toho plyne hlavní teze plánu:** *univerzalita orchestra se nezvyšuje
přidáváním schopností, ale odstraňováním nutnosti synchronizovat.* Každá
nová schopnost, která se musí zapsat do každé hry, je **daň z počtu her** —
a přesně ta daň dnes dělá druhou hru drahou.

---

## 3. Fáze plánu

Pořadí není podle zajímavosti, ale podle **závislostí**: co musí existovat,
aby šlo něco ověřit.

> **Kam se dívat, když jdeš implementovat:** tenhle oddíl (§3) říká, **co k čemu
> patří** — fáze F0–F5. **Prováděcí pořadí je v §3.5** (níž, za F5) a liší se
> v jednom bodě: **krok A1 je předpoklad F1**, ne součást F2 — bez něj není čím
> měřit, že oprava smyčky funguje.

```
F0  Základ:     zdroj pravdy musí existovat        (blokuje všechno)
      ↓
F1  Smyčka:     conductor nesmí zdržovat a lhát    (blokuje důvěru v měření)
      ↓
F2  Měření:     brána musí doložit, že proběhla    (blokuje ověřitelnost F3+)
      ↓
F3  Kontrakt:   co je jádro a co kopie             (blokuje F4)
      ↓
F4  Převzetí:   hry vlastní soubory, šablona jádro (blokuje druhou hru)
      ↓
F5  Druhá hra:  ověření, že to funguje             (teprve tady má smysl)
```

### F0 — Základ: aby „zdroj pravdy" vůbec existoval

**Proč první:** analýza S2. Klon orchestra z gitu **nemá brány**
(`check-schema.py`, `baseline.py`, `vision-profile.json`, `vision.test.mjs`
jsou netrackované) a `release.yml` v gitu odkazuje na **jinou hru**. Dokud
„co je v gitu" není to, co se používá, nemá žádná další fáze co měřit.

| Krok | Co | Hotovo znamená |
|---|---|---|
| F0.1 | Commitnout `orchestra/repo/` (8 změněných + 4 netrackované) | ✅ **HOTOVO** — `git ls-files repo/.forge` = **21** (bylo 17). Commit `eac2790` |
| F0.2 | Nahradit `repo/.forge/roadmap.json` **prázdnou roadmapou s vysvětlením** (ne 31 granul staré hry) | ✅ **HOTOVO** — `grains` → **0**; `_popis` navíc opraven (nelhal o „po jedné" ani o smazaném `forge plan`) |
| F0.3 | Z `repo/.forge/vision-profile.json` odstranit natvrdo `"hra": "uo-shadows"` → šablona má **vzor**, hra svou hodnotu | ✅ **HOTOVO** — `hra: null`, `popis_stylu: ""`, zákazy 3→1. **Navíc** dvoujmenny fallback v `vision.mjs` + 2 testy |
| F0.4 | Commitnout `tools/` — **rozhodnout u 51 untracked, které jsou trvalé** (návrh: 24 trvalých ano, 27 jednorázových smazat) | ✅ **HOTOVO** — `git ls-files tools/` = **78**; klíčové nástroje ověřeny `ls-files --error-unmatch` |
| F0.5 | **Smazat 10 jednorázových záplat** (`oprav-*.py`, `migrace-schema.py`) — analýza ověřila, že jsou hotové a idempotentní | ✅ **HOTOVO** — smazáno **8** souborů (742 řádků), commit `525d45b`. `oprav-ps1-kodovani.py` **zůstává** (používá se dál). Před smazáním u každého ověřeno, že jeho oprava je zapečená **v šabloně i ve hře** |
| F0.6 | Do `.gitignore`, který generuje `install-into-repo.ps1`, přidat `.env` a `.forge/node/.env` | ✅ **HOTOVO** — `git -C <hra> check-ignore .forge/node/.env` → cesta; kontraktní test `tools\test-gitignore-tajemstvi.py` (**15 kontrol**, mutačně ověřen) |

**Co to blokuje:** všechno. **Co to neblokuje:** nic.
**K rozhodnutí:** *Smím commitnout orchestra (bez push)?* Analýza i tuhle
přípravu jsem dělal bez zápisu do gitu — commit je změna stavu, kterou má
schválit uživatel, ne agent (viz `AGENTS.md`, „nepushovat bez vyžádání";
commit je o stupeň slabší, ale pořád zápis do historie).

### F1 — Smyčka: conductor nesmí zdržovat a lhát

**Proč druhá:** analýza S12–S14. Dokud nová granule čeká 3 h a strop pokusů
nefunguje, **každé měření v F2+ bude měřit rozbitý systém** — a bude vypadat,
že orchestra „nic nedělá".

| Krok | Co | Hotovo znamená |
|---|---|---|
| F1.1 | **Oddělit „vzniklo" od „naposledy selhalo"**: do `roadmap` přidat sloupec `naposledy_selhalo` (NULL při založení) a guard postavit na něm | Měření z analýzy §3 C9 dá po opravě **`[1]`, `[1]`, `[]`** (dnes `[]`, `[1]`, `[1]`) |
| F1.2 | Doplnit zápis roadmapy do `/report` (stejně, jako ho má `pollRuns:403-405`) | Simulované selhání přes `/report` → granule se nevydá dřív než za `RETRY_HOURS` |
| F1.3 | Opravit zámek: `locked.add(k)` z `lockKeys` (`index.ts:774-776`) | Dvě granule se stejným `owns` → druhá se nevydá, dokud první běží |
| F1.4 | Strop a watchdog na **`item_id` granule**; `ESCALATE_AFTER` < `MAX_ATTEMPTS` | Granule, která selže 6×, se **ohlásí** (dnes se nikdy neohlásí) |
| F1.5 | Fallback `listGames` **nesmí dispatchovat** — prázdný registr = orchestra nepracuje | `POST /game/active {active:false}` → `/health` `games=0` a žádný dispatch |
| F1.6 | `STALE_MINUTES` > timeout nejdelšího kroku (nebo heartbeat z workera) | Worker pošle heartbeat i uprostřed kroku |

**Ověření F1 je hotové už teď** — skript z analýzy §1.2 (příloha) je
**regresní test**, který se dá pustit offline v SQLite. To je první krok
k tomu, aby conductor měl testovatelnou logiku (F2.3).

**K rozhodnutí:** *Mám na tyhle změny sahat?* Mění to chování orchestra
a `conductor` se nasazuje pushem (deploy z gitu). Analýza doporučuje je dělat
**především ostatním**, ale je to zásah do běžícího systému.

### F2 — Měření: brána musí doložit, že proběhla

**Proč třetí:** analýza S1, S3, A4. Tohle je **jádro odpovědi na zadání**
(„která rozhodnutí způsobují, že se chyby ztrácejí tiše").

| Krok | Co | Hotovo znamená |
|---|---|---|
| F2.1 | **Holistická fitness funkce: „každá brána doloží, že proběhla a kolik změřila."** Každá brána vypíše strojově čitelný řádek `ZMERENO: <co>=<počet>`; `validate-all.mjs` (resp. CI) padne, když některá brána nevykáže měření | Když se z `check-assets.py` odebere hledání animace, **CI to ohlásí** (dnes: tichá poznámka) |
| F2.2 | `validate-all.mjs`: `process.exitCode = chyb ? 1 : 0`; pustit **správnou** kopii brány schématu; přidat `kontrola-driftu.mjs` | `node tools/validate-all.mjs; echo $LASTEXITCODE` → **1** při nálezu (dnes 0) |
| F2.3 | **Conductor jako testovatelná jednotka:** vytáhnout SQL a rozhodovací funkce do modulu, testy proti **němu**, ne proti opsané kopii | Změním SQL v conductoru → test **spadne** (dnes projde: `test-cooldown.py` má vlastní kopii a nemá ani `assert`) |
| F2.4 | Offline testy pro `check-assets.py`, `check-wiring.py`, `verify-level-render.py` — vzorem `test-check-schema.py` (fixtura + známý správný i chybný stav) | U každé: fixtura, kde **musí** hlásit vadu, a fixtura, kde nesmí |
| F2.5 | Test `agent.yml` (dnes netestovaný — `test-ci-workflow.mjs` čte jen `ci.yml`); hlídat **i to, že každý `FORGE_*` je v kroku, který ho čte** | Záměrné přesunutí `FORGE_ATTEMPT` do jiného kroku → test **FAIL** (dnes `kontrola-driftu.mjs` OK) |
| F2.6 | Vrátit `assets/spec.json` mezi chráněné soubory v auto-merge | PR měnící `spec.json` → „chráněný soubor" |

**K rozhodnutí:** *Je `ZMERENO:` řádek přijatelný formát?* Je to zásah do
všech bran (ale malý — jeden `print`). Alternativa je JSON výstup
(`--json` už brány mají) a čtení z něj.

### F3 — Kontrakt: co je jádro a co kopie

**Proč čtvrtá:** analýza S4, S5. Tohle je **strukturální jádro** plánu
a odpověď na „modulární architektura?".

| Krok | Co | Hotovo znamená |
|---|---|---|
| F3.1 | **`orchestra/prepisy.json`** — jeden manifest: `soubor → směr → kdo je zdroj`, s `skip` seznamem (vzor cruft). Čtou ho `kontrola-driftu.mjs`, `sync-sablona-hra.py` i `sjednot-sablonu.py` | Přidání souboru = **jedna řádka manifestu**; drift i sync se chovají shodně; tři seznamy zmizí |
| F3.2 | **`.forge/zdroj.json` v každé hře** — „jsem z `forge-orchestra` v commitu X", se seznamem souborů **vlastněných hrou** (vzor `.cruft.json`) | `kontrola-driftu.mjs` řekne „hra je z commitu X, šablona je v Y" — dnes to nikdo neví |
| F3.3 | **`forge.config.json` v každé hře** — deklarace: kde je `spec.json`, kde sprity, které brány se pouští, jaké přípony má kód, kde je vstupní bod vykreslování | Nová hra s jiným rozložením složek projde branami **bez editace nástrojů** |
| F3.4 | Brány čtou z F3.3 místo konstant: `check-wiring.py:73` (přípony), `baseline.py:60` (`SLEDOVANE`), `check-schema.py:212-213` (cesty), `verify-level-render.py:209,251` | Změna struktury hry v konfiguraci → brány ji respektují |
| F3.5 | Rozdělit šablonu na **`core/`** (17 souborů nezávislých na enginu) a **`tools/<engine>/`** (Godot: `install-godot.sh` + 3 kroky) | Smazat `tools/godot/` → brány `core` pořád běží |

**K rozhodnutí (nejdůležitější v celém plánu):**
1. *Jsou cesty v `forge.config.json`, nebo se mají odvozovat konvencí?*
   Deklarace je robustnější, ale přidává soubor, který se může rozejít.
2. *Je `zdroj.json` v herním repu, nebo stačí v orchestra?* V herním repu
   znamená, že ho agent může vidět (a **nesmí** ho měnit — patří do
   chráněných souborů).

### F4 — Převzetí: hry vlastní soubory, šablona jádro

**Proč pátá:** analýza S10, D13. Tohle je **odpověď na „nové hry dědí
pozůstatky"** a na „proč je onboarding mrtvá větev".

| Krok | Co | Hotovo znamená |
|---|---|---|
| F4.1 | **Onboarding jako test:** skript, který v tempu založí hru z šablony a pustí všechny brány | Test projde (dnes neprojde: `projects/` neexistuje) |
| F4.2 | `install-into-repo.ps1`: odstranit závislost na `projects/<Projekt>` a na `forge.cmd`; přepsat chybové hlášky | Skript projde na prázdné složce z `repo/` |
| F4.3 | Rozhodnout a **zapsat**, které soubory patří hře (a tedy se v šabloně neaktualizují) — návrh: `roadmap.json`, `vision-profile.json`, `providers.json` (lokální záloha), `spec.json`, CONVENTIONS.md | V `zdroj.json` je to vidět; drift kontrola na ně nehlásí rozdíl jako vadu |
| F4.4 | Nástroje: parametrizovat `game_id` (47 souborů, většinou 1–3 řádky; vzorem je `status.mjs:18`) a **odstranit absolutní cesty** (57 ze 72 skriptů) | `node tools/validate-all.mjs --hra <jiná>` funguje; orchestra jde spustit z jiné složky |
| F4.5 | `zjisti-pages.mjs` a `validate-all.mjs` **nesmí tvrdit, že stav orchestra = stav `uo-shadows`** | S druhou hrou výstup neříká jen `uo-shadows` |

**K rozhodnutí:** *Které soubory jsou „hry"?* To je věcné rozhodnutí
o vlastnictví a má ho udělat uživatel — agent může navrhnout, ne rozhodnout.

### F5 — Druhá hra: ověření, že to funguje

**Proč poslední:** dokud neexistuje druhá hra, je každá abstrakce **hypotéza**.
Tohle je fáze, kde se hypotézy měří.

| Krok | Co | Hotovo znamená |
|---|---|---|
| F5.1 | Založit **nejmenší možnou druhou hru** (i prázdný Godot projekt s jednou granuli) | Registrovaná v `games`, dispatchuje se |
| F5.2 | Limity per `game_id` (tabulka `games`: `max_prs`, `max_concurrent`, `retry_hours`) | Dvě hry se navzájem nevyhladoví |
| F5.3 | Ověřit, že se zámky a `item_id` chovají správně pro dvě hry | Soubory se stejným jménem v obou hrách se neblokují |
| F5.4 | **Změřit daň z druhé hry** — kolik souborů se muselo změnit | Pokud > 5, kontrakt v F3 byl nedostatečný → vrátit se |

**K rozhodnutí:** *Má být druhá hra reálná, nebo testovací?* Reálná spotřebuje
free kvótu (**klíče jsou per-repo a denní limit je per klíč — druhá hra
kapacitu nezdvojnásobí**, jen si ji rozdělí). Testovací je poctivější.

---

## 3.5 Implementační plán — pořadí, kterým se to má dělat

*(Následuje po fázích F0–F5; ty říkají, **co k čemu patří**, tenhle oddíl
říká, **čím se začne**.)*

**Datum revize:** 1. 10. 2026 (večer) · **Stav:** F0 hotová, **fáze A HOTOVÁ
a ověřená**, fáze B–D nezačaté (B a D1 čekají na rozhodnutí)
**Proč je tenhle oddíl samostatně:** §3 je návrh podle **fází** (co k čemu patří).
Tohle je pořadí podle **závislostí a dnešního stavu** — a v jednom bodě se liší:
**krok A1 není součást F2, ale předpoklad F1.** Dokud `validate-all.mjs` hlásí
zelenou při nálezu a měří starou kopii brány, **nemá F1 čím dokázat, že funguje**.

### Fáze A — Změřitelnost ✅ HOTOVÁ (1. 10. 2026)

| # | Krok | Hotovo znamená | Stav (naměřeno) |
|---|---|---|---|
| **A1** | **L1** — `process.exitCode` a volat **`repo/.forge/check-schema.py`** místo `tools/kontrola-schematu.py` (`validate-all.mjs`) | čistý stav → exit **0**; zavedená vada → exit **1** | ✅ **HOTOVO** — mutační test proveden: se sabotáží **exit 1**, po odstranění **exit 0**. Stará kopie se už nevolá |
| **A2** | **L2** — smazat `tools/kontrola-schematu.py` (stará slepá verze) | žádný kód na ni nesahá; brány projdou | ✅ **HOTOVO** — smazáno **305 řádků**; `test-check-schema.py` **17/17**; zbývají jen zmínky v **textu** (viz „Co po A zbývá") |
| **A3** | **ST9-část** — vzít SQL guardu z conductora do testu (neopsat) | změna SQL v `index.ts` → test spadne | ✅ **HOTOVO** — SQL se **vytahuje ze zdrojáku**, test má `assert` i `sys.exit`. **Rovnou naměřil vadu S12** → je červený a je to správně; opraví ho **B1** |

**Brána fáze A — SPLNĚNA.** `validate-all.mjs` vrací **1 při nálezu** (dokázáno
mutačním testem) a `test-cooldown.py` měří **skutečný SQL** z conductora.

> **Vedlejší důsledek, který je potřeba vědět:** `validate-all.mjs` je od
> 1. 10. 2026 **červený — hlásí 1 problém, a tím je S12.** Není to regrese:
> je to poprvé, co validátor **nelže**. Do té doby hlásil „✗ NALEZENO 3
> PROBLÉMŮ" a **stejně skončil exit 0**.

### Co po fázi A zbývá (a proč se to neudělalo hned)

| Co | Kde | Proč to není hotové |
|---|---|---|
| Zastaralý návod v docstringu brány | `check-schema.py:22-23` v **šabloně i ve hře** — obě kopie odkazují na smazaný `orchestra/tools/kontrola-schematu.py` | **Musí se změnit OBĚ stejně** (test hlídá shodný hash). Změna jen v šabloně test rozbije; změna obou mění **pracovní strom herního repa**, který je dnes čistý. Je to text → patří do nejbližšího commitu hry |
| Zastaralý komentář | `games/uo-shadows/scripts/level.gd:24` a `:107` | Týž důvod — herní repo se v této session nemění |
| `test-eskalace.py` | `orchestra/tools/` | **NENÍ vada, jak tvrdil plán.** Ověřeno: **má `sys.exit(0 if vse_ok else 1)`** (`:121`). Slabší je jen to, že `watchdog()` je **opsaná kopie** a `PRAH = 8` je natvrdo místo čtení `ESCALATE_AFTER` → práce pro **C2** |

> **Oprava nepravdivého tvrzení:** plán i `HANDOFF.md` tvrdily, že
> „`test-cooldown.py` **a** `test-eskalace.py` lžou zelenou". **Naměřeno
> 1. 10. 2026: `test-eskalace.py` exit kód MÁ** a jeho scénáře procházejí
> správně (`VŠE OK`, exit 0). „Lže zelenou" se týkalo **jen** `test-cooldown.py`.

### Fáze B — Tři vady conductoru (hodiny; zásah do běžícího systému)

| # | Krok | Soubor | Hotovo znamená | Riziko |
|---|---|---|---|---|
| **B1** | **L11 (S12)** — `roadmap` dostane sloupec `naposledy_selhalo` (NULL při založení) a guard se ptá **na něj**, ne na `updated_at` | `conductor/src/index.ts` (guard `:796-804`, `roadmapTick` `:643-646`), `schema.sql` | Replika SQL z `ANALYZA-PODKLADY` §1.2 dá po opravě **`[1]`, `[1]`, `[]`** (dnes `[]`, `[1]`, `[1]`). Nová granule se vydá v **následujícím tiku** | **Vysoké** — mění dispatch. Nasazovat **po jednom kroku**, měřit před/po. Migrace sloupce: `ALTER` v tiku s polknutou chybou (vzor už v kódu) |
| **B2** | **L12 (S13)** — `/report` zapíše i `roadmap`, stejně jako `pollRuns:403-405` | `conductor/src/index.ts:1338` | Simulované selhání přes `/report` → granule se nevydá dřív než za `RETRY_HOURS` | ✅ **HOTOVO 7. 10. 2026** — vadu opravil už **B1**; chyběla jí **brána**, tu dodal `tools/test-report-cooldown.py` (8/0) + `_analyza/b2-mutace.py` (9/0). Nasazeno v `598e207` |
| **B3** | **L14 (S14)** — strop a watchdog na **`item_id` granule**; `ESCALATE_AFTER` < `MAX_ATTEMPTS` | `conductor/src/index.ts:246,251,328,679,1338` | Granule, která selže 6×, se **ohlásí** (dnes nikdy) | ✅ **HOTOVO A NASAZENO 7. 10. 2026** — **B3a** (watchdog na granuli, prah 3) + **B3b** (strop `GRAIN_MAX_RUNS`, **výchozí vypnuto** = druhý krok). **Živě ověřeno:** `/tick` → `watchdog: 2 ohlášeno (prah 3)`. Brány: `test-watchdog-granule` 17/0 + 11/0, `test-grain-cap` 22/0 + 11/0 | | a **8. 10. 2026 strop ZAPNUT na `"8"` a NASAZEN** (push `07169c7` → `deploy.yml` #34 `success`) — ověřeno živě: `/health` ok, `/roadmap` 21 granul, **0 blokovaných** (strop blokuje až od 8 běhů) |
| **B4** | **L15 (S16/inv. 18)** — `listGames` fallback **nesmí dispatchovat** | `conductor/src/index.ts:447-454` | `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch** | ✅ **HOTOVO A NASAZENO 7. 10. 2026** (`598e207`) — fallback pryč **a** dispatch smyčka se ptá na aktivní hry. Brána `tools/test-listgames.py` (10/0) + `_analyza/b4-mutace.py` (9/0) + test tiku offline (kontroly A a C). ⚠ **Zbývá ověřit živě** vypnutím hry (`POST /game/active {active:false}`) — plán to má jako acceptance |
| **B5** | **L17 komentář** — opravit komentáře `:31`, `:233` (`MAX_ATTEMPTS` živý) | `conductor/src/index.ts` | `grep -n "mrtvý kód" conductor/src/index.ts` → **0** | ✅ **HOTOVO 7. 10. 2026** — naměřeno **0 výskytů**; nasazeno v `598e207` |

**Brána fáze B:** `POST /tick` → nová granule se vydá **do jednoho tiku**;
`/health` po vypnutí hry hlásí `games=0`. **Deploy conductora je z gitu** (push do
`conductor/**`) — a to je **rozhodnutí uživatele**.

### Fáze C — Brány, které lžou (hodiny)

| # | Krok | Soubor | Hotovo znamená |
|---|---|---|---|
| **C1** | **L16** — `test-cooldown.py`: `assert` + `sys.exit` (a scénář 6, který dnes **posvěcuje vadu**, předělat) | `orchestra/tools/` | Vypíše `CHYBA` → **exit 1** |
| **C2** | **`test-eskalace.py`** — `watchdog()` je **opsaná kopie** logiky a `PRAH = 8` je natvrdo místo čtení `ESCALATE_AFTER` ze zdrojáku | tamtéž | Test čte prah ze zdroje, ne z konstanty v sobě. **POZOR: exit kód už MÁ** (`:121`) — „lže zelenou" se ho netýkalo |
| **C3** | **ST4** — test `agent.yml` (dnes netestovaný; `test-ci-workflow.mjs` čte **jen `ci.yml`**) | `orchestra/tools/test-ci-workflow.mjs` | Přesunutí `FORGE_ATTEMPT` do jiného kroku → test **FAIL** |
| **C4** | **L9** — `assets/spec.json` mezi chráněné soubory v `agent.yml` | oba `agent.yml` | PR měnící `spec.json` → komentář „chráněný soubor" |
| **C5** | **ST5** — offline testy `check-assets.py`, `check-wiring.py`, `verify-level-render.py` | `orchestra/tools/` | U každé fixtura, kde **musí** hlásit vadu, i kde nesmí |

### Fáze D — Obálka a onboarding

| # | Krok | Soubor | Hotovo znamená |
|---|---|---|---|
| **D1** | **NOVÉ: `NAZEV-REPA`** — `release.yml` použije `${{ github.repository }}` (nebo substituci v instalátoru) | `orchestra/repo/.github/workflows/release.yml` | Simulace instalátoru → v novém repu **žádný** zástupný text; odkaz vede na existující repo | ✅ **HOTOVO 1. 10. 2026** — `github.repository` na **obou** místech (`:82` i krok „Označit nasazený web"), YAML ověřen parserem, simulace `Copy-Item` → zástupný text **0×**. **Pozor:** v `.forge/node/termux-setup.sh:97-98` zástupný text **zůstává záměrně** — je to návod pro člověka („nahraď repem hry"), ne kód, který se má nahradit sám |
| **D2** | **L6** — `kontrola-driftu.mjs` čte seznam z `git ls-files`, ne z ručního seznamu | `orchestra/tools/kontrola-driftu.mjs` | Přidání souboru do šablony → drift ho ohlásí **bez editace seznamu** |
| **D3** | **ST6** — onboarding jako **test** (založí hru z šablony a pustí brány) | nový test + `install-into-repo.ps1:36-38,86` | Test projde (dnes neprojde: `projects/` neexistuje) |
| **D4** | **ST10** — parametrizovat `game_id` (47 souborů, 1–3 řádky) a odstranit absolutní cesty (57 ze 72) | `orchestra/tools/` | `validate-all.mjs --hra <jiná>` funguje; orchestra jde spustit z jiné složky |
| **D5** | **ST1/ST2** — `prepisy.json` a `forge.config.json` | nové soubory | Přidání souboru = 1 řádka manifestu; nová hra s jiným rozložením projde branami |

**Poznámka k fázi D:** D1 je **nejlevnější a nejkonkrétnější** — je to jeden
řádek a dnes to znamená, že každá nová hra dostane nefunkční odkaz v release.
D2–D5 jsou „dny práce" z §5.2 analýzy.

### Co v implementaci NEDĚLAT

- **Nepřestavovat orchestra na platformu** (plugin systém, registr bran) — §4 a
  past z §0. Abstrakce přijdou na řadu až ve F5 s druhou hrou.
- **Nesahat na `index.ts` a dokumentaci současně** — komentáře v kódu a text
  v dokumentaci se rozešly už dvakrát (S6). Kdo mění chování, mění i komentář
  u toho kódu.
- **Nemazat komentáře s naměřenými čísly.** `forge-quest` v `release.yml:88,141`
  je **text o opravě**, ne vada (viz `ORCHESTRA-STAV-A-ANALYZA.md` §3.2).
- **Nepushovat bez vyžádání.** Fáze B znamená deploy conductora — to je
  rozhodnutí uživatele.

---

---

## 4. Co tenhle plán vědomě NEŘEŠÍ

Aby se dalo revidovat i to, co v něm chybí:

| Věc | Proč ne |
|---|---|
| **Auto-merge a `vision.mjs` neblokuje** | Je to vědomé rozhodnutí s dobrým zdůvodněním (`ci.yml:127-131`: falešný poplach je dražší). Změnit to znamená **naměřit chybovost vision** na desítkách vzorků — to je samostatný úkol, ne fáze |
| **Chybějící brána na animaci** | Řeší ji F3.4 (cesty spritů z konfigurace). Do té doby je to **známé slepé místo**, ne přehlédnuté |
| **`kind` nic neřídí** | Až bude potřeba. Dnes všechny granule jsou `code` a nic to neblokuje |
| **Lokální generátor / Blender na uzlu** | Je to jiná osa (schopnosti), ne architektura. Patří do `FORGE-ORCHESTRA-MOZNOSTI.md`, ne sem |
| **Vizuální přesnost vision** | Měření, ne architektura |
| **Hudba se neměří** | Chybí manifest; je to stav hry, ne vada orchestra |
| **Push na GitHub** | Rozhodnutí uživatele, ne součást plánu |
| **Smazat `forge-quest`** | Je to **živá hra** — zakázáno (`AGENTS.md`) |

---

## 5. Rizika plánu (a jak je poznat včas)

| Riziko | Jak se projeví | Obrana |
|---|---|---|
| **Předčasná abstrakce** — stavíme plugin systém pro jeden engine | F3.5 přidá vrstvu, kterou nikdo nepoužije | F3.5 je **poslední krok F3** a má před sebou F5.1 (druhou hru). Když F5 nepřijde do rozumné doby, F3.5 se **nedělá** |
| **Kontrakt se sám stane zdrojem driftu** — `forge.config.json` se rozejde s realitou | brány čtou konfiguraci, ale hra má jiné cesty → tichý přeskočený krok | F2.1: brána musí vykázat `ZMERENO:`; a F3.3 má **validátor konfigurace** (jako `lint-roadmapa.py`) |
| **Oprava F1 rozbije běžící orchestra** | granule se začnou vydávat jinak | F1 se nasazuje **po jednom kroku** a měří se proti skriptu z §1.2 (offline, před i po) |
| **Zmizí znalost, proč co bylo** | někdo „uklidí" komentář s naměřeným číslem a přijde o důvod | Komentáře s naměřenými hodnotami **nejsou dluh** — jsou dokumentace rozhodnutí. Plán je nesmazává (a `AGENTS.md` to už říká) |
| **Plán zestárne během implementace** | fáze se dělají jinak, dokument lže | Dokument má **revizní hlavičku** a oddíl „Co se změnilo proti návrhu" (§7) |
| **Příliš mnoho najednou** | F0–F5 najednou = nic hotové | Každá fáze má vlastní „Hotovo znamená"; **fáze se schvalují jednotlivě** |

---

## 6. K rozhodnutí — stav k 1. 10. 2026 večer

Otázky níž měl zodpovědět uživatel. **Dvě jsou zodpovězené a hotové**, jedna
je částečně, zbytek **čeká** — a u každé je vidět, co se s ní stalo.

| # | Otázka | Stav | Co platí dnes |
|---|---|---|---|
| **O1** | Smím commitnout orchestra (bez push)? | ✅ **ZODPOVĚZENO — ANO** | F0 je commitnutá a pushnutá (`eac2790`, `525d45b`). **Ale:** v orchestra je teď **1 necommitnutá změna** — `README.md` (aktualizace „Stav obálky" z 1. 10. večer). Drift kontrola ho nesleduje, takže se s herním repem nerozejde |
| **O2** | Smím smazat 10 jednorázových záplat a 27 jednorázových nástrojů? | ✅ **ZODPOVĚZENO — smazáno 8 záplat** | Uživatel: *„Tak je smaž."* → `525d45b`. **Druhá půlka (27 nástrojů) se rozhodla opačně:** byly commitnuté jako trvalé (`tools/` = 70). Reálných kandidátů bylo 9, ne 10 — `oprav-ps1-kodovani.py` je živý nástroj |
| **O3** | Mám opravit vady conductoru? | ✅ **ZODPOVĚZENO A NASAZENO 8. 10. 2026** (P27) | Zámek (`L13`) už hotový dřív. Zbývá **B1 `naposledy_selhalo`, B2 `/report`, B3 strop na granuli, B4 `listGames`** + komentář (`B5`). **Nasazení conductora je z gitu → rozhodnutí uživatele** |
| **O4** | Je formát `ZMERENO: <co>=<počet>` přijatelný? | ⏳ **ČEKÁ** | Netýká se fáze A–C; je to F2.1. Alternativa (JSON z `--json`) je pořád otevřená |
| **O5** | Cesty v `forge.config.json`, nebo konvencí? | ✅ **ZODPOVĚZENO 8. 10. 2026** (P27, uživatel: „souhlasím“) | Fáze D5. Návrh agenta: **deklarace** |
| **O6** | Které soubory **patří hře**? | ✅ **ZODPOVĚZENO 8. 10. 2026** (P27, uživatel: „souhlasím“) | Fáze D. Návrh: `roadmap.json`, `vision-profile.json`, `spec.json`, `providers.json`, `CONVENTIONS.md`. **Agent to nesmí rozhodnout sám** |
| **O7** | Druhá hra reálná, nebo testovací? | ⏳ **ODLOŽENO S PRAVIDLEM 8. 10. 2026** (P27) | F5. Návrh: testovací (free kvóta se **sdílí, nedělí**) |
| **O8** | Fáze schvalovat jednotlivě, nebo F0–F2 jako celek? | ✅ **ZODPOVĚZENO 8. 10. 2026** (P27, uživatel) | Platí: F0 hotová, F1–F5 neschválené |
| **O9** | **NOVÉ:** Opravit `NAZEV-REPA` hned (`${{ github.repository }}`), nebo až v rámci onboardingu? | ✅ **HOTOVO A OVĚŘENO 8. 10. 2026** (P27) | Fáze D1. Návrh: **hned** — je to jeden řádek a dnes to znamená, že každá nová hra dostane nefunkční odkaz |
| **O10** | **NOVÉ:** Má být **ST9-část** (testy conductora čtou SQL ze zdrojáku) součástí fáze B, ne až F2? | ✅ **ZODPOVĚZENO 8. 10. 2026** (P27, uživatel: „souhlasím“) | Návrh: **ano** — bez toho B1–B3 nemají čím dokázat, že fungují. Je to **změna plánu**, proto se ptám |

**Co z toho vyplývá pro novou session:** fáze **A nepotřebuje žádné rozhodnutí**
(je to nástroj, ne chování orchestra). Fáze **B a D1 ano**. Doporučení je
**začít fází A** a rozhodnutí o B a D1 nechat na člověka.

---

### 6.1 ROZHODNUTÍ B5 — ROZSAH BRÁNY `over-skilly` (8. 10. 2026, P27)

**Otázka:** které cesty má brána `tools/over-skilly.py` měřit a proti kterému
projektu? Uživatel ji delegoval na agenta („Nevím podle čeho B5 rozhodnout.
Nerozumíš tomu lépe? Můžeš určit ty?“), takže rozhodnutí je tady **zapsané
i s důvodem**, aby se za měsíc nehádalo, proč to tak je.

**Naměřeno před rozhodnutím:** skill `game-developer` (STANIČNÍ, přepsaný cizí
session) odkazuje na `tools/plan-status.py` a `tools/roadmap-gen.py`; ty
existují v sourozenci `E:\Workspaces\game-clone`, ale brána znala jen
orchestra + hru → hlásila **3 mrtvé cesty** a shodila `g3` (2 nedeklarované
exity). To je **falešný poplach** — a ten nutil „opravovat“ správný text.

**ROZHODNUTÍ:** skilly jsou **STANIČNÍ**, ne projektové. Cesta se proto uzná,
když existuje v orchestře, ve hře, **nebo v některém sourozeneckém projektu**
(adresář v `REPO.parent` s `.git`). **Skutečně mrtvá cesta (nikde) bránu dál
SHODÍ** — o to jde. A co se našlo mimo orchestra/hru, brána **vypíše jako
poznámku** (rozsah musí být VIDĚT; tiché rozšíření rozsahu je táž vada, jakou
popisuje P25-K).

**Druhá část rozhodnutí:** slepé místo z `HANDOFF.md` §51.3 (brána měřila jiný
tvar cest, než dokumenty používají) zůstává **otevřené jako samostatná práce**
— dnešní oprava řeší **rozsah**, ne tvar cest.

## 7. Co se změnilo proti návrhu

*(Sem se zapisuje, když revize změní obsah, aby bylo vidět, co bylo rozhodnuto
a proč.)*

| Datum | Co se změnilo | Proč |
|---|---|---|
| 1. 10. 2026 | **F0.1 HOTOVÉ** (obě kopie) — commit `eac2790` za šablonu, `7cd14cb` za hru. `git ls-files repo/.forge` → **21** (plán chtěl 21) | Naměřeno: klon orchestra z gitu neměl brány |
| 1. 10. 2026 | **F0.4 HOTOVÉ** — `tools/` je v gitu: **70 souborů** (plán chtěl ≥ 48; 78 před smazáním záplat). Klíčové nástroje (`git.cmd`, `validate-all.mjs`, `status.mjs`, `zjisti-pages.mjs`, `test-check-schema.py`) ověřeny přes `ls-files --error-unmatch` | Naměřeno: 51 untracked |
| 1. 10. 2026 | **F0.2 HOTOVÉ** — roadmapa šablony má **0 granul** (bylo 31 z jiné, smazané hry). Zároveň opraven `_popis`, který lhal ve třech bodech: „pracuje se po jedné" (proti `MAX_CONCURRENT=5`), „až je zkontroluješ" (auto-merge) a „Plánovač (`forge plan`)" (GameForge smazán) | Uživatel: *„staré granule promazat"*. Každá nová hra dědila cizí plán |
| 1. 10. 2026 | **F0.3 HOTOVÉ** — `vision-profile.json` šablony nemá **žádná** data o konkrétní hře: `hra: null` (bylo `uo-shadows`), `popis_stylu: ""` (byl UO popis), zákazy 3→1 (obecný). Obecné věci o kontrole (`poskytovatele`, `self_consistency`, `cache`, `stropy`) zůstaly; doplněno `strict_poskytovatele`, které v šabloně chybělo, i když ho kód čte | Uživatel: *„vision nemá hledět na UO, ale má být přepínatelný, když na ní orchestra pracuje"* |
| 1. 10. 2026 | **Vedlejší nález z F0.3: dvě jména téhož pole.** Šablona používá `popis_stylu`, ale `vision.mjs` četl **jen** `styl_popis` → hra s novým jménem by o styl **tiše** přišla. Kód nyní čte obě jména; **+2 testy** (34 → 36) hlídají, že ani jedno se neztratí | Přesně třída chyby, kterou projekt řeší |
| 1. 10. 2026 | **Deklarace vlastnictví v `kontrola-driftu.mjs`.** Přidán seznam souborů, které se **záměrně nesynchronizují** (`vision-profile.json`, `roadmap.json`, `providers.json`) s důvodem u každého | Aby někdo nepřidal do `--sync` seznamu soubor, který patří hře |
| 1. 10. 2026 | ~~**F0.5 ROZHODNUTO OPAČNĚ (prozatím).**~~ → **PŘEKONÁNO týmž dnem:** záplaty byly nejdřív commitnuté (uživatel zadal „commitni všechno"), pak je uživatel nechal smazat („Tak je smaž"). Výsledek je v řádku „F0.5 HOTOVÉ" níž | Dvě zadání v jednom dni; rozhodující je to druhé |
| 1. 10. 2026 | **F0.6 HOTOVÉ — a byl to skutečný bezpečnostní nález, ne kosmetika.** `git check-ignore .forge/node/.env` → **nic**, přitom `install-into-repo.ps1` ten soubor do hry kopíruje s reálným `FORGE_SECRET`. Opraveno v generátoru, ve hře i v orchestra + kontraktní test | Nález S7/L5 analýzy |
| 1. 10. 2026 | **F0.5 HOTOVÉ** — smazáno 8 jednorázových záplat (742 řádků): `oprav-check-schema{,-iso,-komentare,-tilesize}.py`, `oprav-verify-iso.py`, `oprav-prompt-skills.py`, `oprav-testy-get.py`, `migrace-schema.py`. `oprav-ps1-kodovani.py` zůstává. **Před smazáním u každého ověřeno, že jeho oprava je zapečená v šabloně I ve hře** — jinak by se znalost ztratila pro každou další hru. Po smazání `validate-all.mjs` poprvé hlásí **„✓ VŠE V POŘÁDKU"** | Uživatel: *„Tak je smaž."* |
| 1. 10. 2026 | **⚠️ NALEZENO PŘI ZÁVĚREČNÉM OVĚŘOVÁNÍ: `vision.test.mjs` se rozešel — hra má 28 testů, šablona 36.** Zdrojový `vision.mjs` je přitom shodný. Root kopie (`vision.test.mjs`, 11 983 B) je **rozbitá: 5 OK / 23 chyb**. **Nový otevřený bod** — `vision.test.mjs` **není** v seznamu `kontrola-driftu.mjs`, takže ho `--sync` nesjednotí | Naměřeno spuštěním všech tří kopií |
| 1. 10. 2026 | **Nový vstup pro F0.1: „brána si musí dovézt závislost".** Krok `check-schema` potřeboval Pillow a `ci.yml` ho neinstaloval → `main` byl 7,5 h červený. Oprava je v commitu, ale **obrana proti třídě chyby patří do F2.1** (`ZMERENO:` + brána na závislosti) | Naměřeno: `ModuleNotFoundError: No module named 'PIL'` |
| 1. 10. 2026 | **Nový vstup pro F2:** `CONVENTIONS.md` je teď **shodný** v šabloně i ve hře (ověřeno hashem) a `kontrola-driftu.mjs` ho sleduje. Přidána **§1h** (Godot 3 konstanty) | Běh #241: `ALIGN_LEFT` → `hud.gd` nikdy nevznikl |
| 1. 10. 2026 | **FÁZE A HOTOVÁ a ověřená** — A1 (`validate-all.mjs`: `process.exitCode` + správná kopie brány), A2 (smazána stará `kontrola-schematu.py`, 305 řádků), A3 (`test-cooldown.py` vytahuje SQL ze zdrojáku, má `assert` i `sys.exit`). **Mutační test:** se zavedenou vadou **exit 1**, po odstranění **exit 0** | Uživatel: *„proveď co lze provést teď"*. Fáze A nepotřebovala žádné rozhodnutí — je to nástroj, ne chování orchestra |
| 1. 10. 2026 | **NÁLEZ: A3 rovnou naměřilo vadu S12.** Nový `test-cooldown.py` spouští **skutečný SQL** conductora a scénář „nová granule" vychází **nevydá se** (`čekáno=True, naměřeno=False`). `validate-all.mjs` je proto **od 1. 10. červený — hlásí 1 problém**. Není to regrese: je to **poprvé, co validátor nelže** (dřív hlásil „✗ NALEZENO 3 PROBLÉMŮ" a skončil `exit 0`). Opraví to **B1** | Naměřeno spuštěním; skript je spustitelný důkaz vady, ne odhad |
| 1. 10. 2026 | **D1 HOTOVÉ — `NAZEV-REPA` je opravené.** `release.yml` bere odkaz z `${{ github.repository }}` (na **obou** místech: `:82` i krok „Označit nasazený web"). YAML ověřen parserem; **simulace instalátoru** (`Copy-Item repo\.github\*`) → zástupný text **0×** (dřív 3×). V `.forge/node/termux-setup.sh:97-98` zástupný text **zůstává záměrně** — je to **návod pro člověka** („nahraď repem hry"), ne kód | Vada doložená simulací; oprava je jeden řádek a odblokuje každou novou hru |
| 1. 10. 2026 | **OPRAVA NEPRAVDIVÉHO TVRZENÍ: `test-eskalace.py` NElže zelenou.** Plán i `HANDOFF.md` tvrdily, že „oba testy lžou zelenou". Naměřeno: `test-eskalace.py` **má `sys.exit(0 if vse_ok else 1)`** (`:121`) a jeho scénáře procházejí (`VŠE OK`, exit 0). „Lže zelenou" se týkalo **jen `test-cooldown.py`**. V C2 zůstává jen pravda: `watchdog()` je opsaná kopie a `PRAH = 8` je natvrdo | Tvrzení se šířilo dvěma dokumenty; ověřeno čtením a spuštěním |
| 1. 10. 2026 | **Přidán §3.5 „Implementační plán"** — pořadí podle závislostí ve čtyřech fázích (A měřitelnost, B tři vady conductoru, C brány, které lžou, D obálka a onboarding) s „Hotovo znamená" u každého kroku. **§3 (fáze F0–F5) zůstává** jako věcné členění; §3.5 je prováděcí pořadí | Uživatel: *„aktualizuj plán implementace"* — §3 je návrh podle fází, ale neříká, čím začít, a v jednom bodě se liší: **A1 (L1) je předpoklad F1**, ne součást F2 |
| 1. 10. 2026 | **§6 převedena na stav rozhodnutí** — O1 a O2 zodpovězené a hotové, O3–O8 čekají, přidány **O9** (`NAZEV-REPA`) a **O10** (ST9-část do fáze B) | Aby nová session neotvírala otázky, které jsou zavřené, a viděla, které rozhodnutí ji blokuje |
| 1. 10. 2026 | **Nový nález mimo plán: `NAZEV-REPA`.** Oprava z F0 nahradila odkaz na cizí hru **placeholderem, který nikdo nenahrazuje** — `release.yml:82,143` jsou literály v `echo`, `install-into-repo.ps1` kopíruje `.github` bez substituce. Doloženo simulací: v novém repu zůstane `NAZEV-REPA` **3×** | Měření 1. 10. 2026 večer; detail `ORCHESTRA-STAV-A-ANALYZA.md` §3.1 |
| 1. 10. 2026 | **Nezávislé ověření F0 (jiná session) — F0 potvrzeno jako hotové.** Nalezeny tři nepřesnosti v tvrzeních o bězích, všechny opraveny v `HANDOFF.md`: dokument uváděl „běhy #355–#362" (GitHub API: **#235–#241**), „20 běhů celkem (4 úspěchy)" (`total_count` = **241**; v posledních 100 bězích 8 success / 92 failure) a „PR #26, #27 se sloučily samy" (`merged_by` = **uživatel**). **Důsledek pro F2:** ke každému číslu o bězích patří zdroj — různé čítače nesou stejné jméno a „samo" je tvrzení o mechanismu, které API vyvrací | Ověřování cizích čísel je jediná obrana proti tomu, aby se podle nepravdy plánovalo (stalo se dvakrát) |

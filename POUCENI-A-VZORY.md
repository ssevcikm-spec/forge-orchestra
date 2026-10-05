# POUCENI-A-VZORY — co funguje, co ne a co je optimální

> **Co tenhle dokument JE:** **souhrn napříč historií projektu** — katalog
> vzorů, anti-vzorů a postupů, **s naměřeným příkladem u každého tvrzení**.
> Odpovídá na tři otázky: *jaký design funguje*, *jaké postupy fungují*
> a *kde je optimum*.
>
> **Čím NENÍ:**
> - **Není kronika.** `KRONIKA-PROJEKTU.md` je **záznam** a **jen se doplňuje**.
>   Tenhle dokument je **souhrn**, a ten se **přepisuje celý** — když se změní
>   poznání. **Naměřené příklady v něm ale zůstávají s datem** (i kdyby jev
>   pominul), protože bez nich je pravidlo jen heslo.
> - **Není návrh.** Architektura je v `NAVRH-ORCHESTRA-NG.md`, plán
>   v `PLAN-ORCHESTRA-NG.md`. Tenhle dokument **nenavrhuje** — **vyhodnocuje**.
> - **Není stav.** Ten je v `HANDOFF.md`.
>
> **Datum vzniku:** 5. 10. 2026 (session P15).
> **Odkud brát současný stav:** `HANDOFF.md` + živé měření. **Tenhle dokument
> žádný stav netvrdí** — všechna čísla mají **zdroj a datum** a jsou
> **převzatá**, pokud není výslovně řečeno „vlastní čtení".
> **Datum spotřeby:** **nezaniká rozhodnutím, ale měřením.** Každé tvrzení,
> které se přeměří jinak, se **označí jako „ve svém čase správné"** a doplní se
> nový stav — **nepřepisuje se**. Kdo do dokumentu přidá vzor, **přidá k němu
> i naměřený případ** (soubor + číslo + datum); bez něj tam nepatří.

**Zdroje** (všechno naměřené dřívějšími session, s datem):

| Zdroj | Co z něj je |
|---|---|
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (1. 10.) | S1–S16, S17/S18, tři strukturální místa, ekonomie změny |
| `ANALYZA-HLOUBKOVA-ORCHESTRA.md` (1. 10.) | S19–S30, skutečný šev, ceny variant |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` (2. 10.) | S31–S37, dvě vrstvy mechanismu |
| `KRONIKA-PROJEKTU.md` | omyly 1–150, nálezy H/N/S/V/P/NA, trendy |
| `HANDOFF.md` | stav, běhy, měření konkrétních session |
| `ZADANI-A-KONEC-MERIDEL.md` + KRONIKA ř. 22 | **experiment typu A** (hypotéza nepotvrzena) |
| `OTEVRENA-TEMATA.md` | otevřená témata stanice |
| `C:\Users\Ssevc\Local-Deepseek\{ANALYZA-EFEKTIVITY-DSH,ANALYZA-VYVOJ-APLIKACI-A-HER}.md` (30. 9.–2. 10.) | ekonomika práce agenta |
| `conductor/src/index.ts`, `repo/.forge/*` | **vlastní čtení 5. 10. 2026** |

> **⚠ Jedno pravidlo, které platí pro celý dokument:** u každého vzoru je
> **signatura** — *jak se pozná, že jím trpím*. Vzor bez signatury se nedá
> použít, protože ho v cizím kódu nenajdeš. Signatura je to, co z pravidla
> dělá nástroj.

---

## 1. Verdikt v osmi větách

1. **Vyhráli jsme tam, kde jsme postavili protějšek** — kde stav má svědka
   (`done` = `ok && merged`), kde brána umí selhat (`exit 1`) a kde měření
   přizná, že neproběhlo („kontrola NEPROBĚHLA").
2. **Prohráli jsme tam, kde stav protějšek neměl** — kde se „hotovo" vyrobilo
   z PR, kde se `merged` načetlo a zahodilo, kde se `updated_at` použil jako
   dva různé údaje.
3. **Nejdražší jednotlivá chyba projektu není špatný kód, ale brána, která
   přestala měřit** — a to se stalo **nejméně patnáctkrát** jen u jednoho vzoru
   (ruční seznam místo projití složky).
4. **Přežili jsme díky tomu, že jsme odmítli stavět dřív, než to bylo potřeba**
   — platformu, plugin systém, monorepo, vlastní DSL, lokální model, druhou hru.
   Každé z těch „ne" ušetřilo dny a ani jedno nebrzdilo práci.
5. **Nejlepší investice s nejhorším poměrem slávy je měřidlo měřidla** —
   offline test se známým správným a známým chybným případem odhalil při prvním
   psaní **čtyři chyby ve vlastním regexu**.
6. **Dvě čísla vysvětlují většinu ztrát:** **55 %** selhaných běhů umíralo do
   **30 sekund** (tedy na překážce zjistitelné předem) a **11,3 %** běhů
   uspělo — tedy **na jednu úspěšnou granuli se spálilo ~9 běhů**.
7. **Nejlepší rozhodnutí projektu je zároveň nejnudnější:** `done` vzniká jen
   tehdy, když je práce **sloučená v `main`** — jedna podmínka, ~15 řádků,
   a zavřela celou řadu „hotovo bez práce".
8. **Optimum není „víc kontrol", ale „žádná tichá cesta"**: každý stav má
   svědka, každá brána umí selhat i přiznat, že neměřila, každé rozhodnutí je
   měřené, a **co stroj neumí, je vidět jako „čeká na člověka"** — ne jako
   odškrtnuté.

---

## 2. Šest čísel, která shrnují celou historii

*(Tohle je to nejcennější, co z projektu zůstalo — víc než kód.)*

| # | Číslo | Co znamená | Zdroj |
|---|---|---|---|
| 1 | **84 % omylů bylo v měřidle** a **7,8 omylu na session — plochých, ať se dělá cokoli** | problém není „agent dělá chyby", ale **kde je dělá**: v nástroji, který měří | `ZADANI-A-KONEC-MERIDEL` §0 |
| 2 | **73 % bran nechrání nic, co se dostane k uživateli** | brány měřily **přítomnost a sebe**, ne produkt | tamtéž |
| 3 | **Hypotéza „bez měřidel bude 0–2 omylů" NEPOTVRZENA: 11 omylů** | ani „nedělat měřidla" není odpověď; **měřidla nejsou příčina, jsou místo, kde se to projeví** | KRONIKA ř. 22 |
| 4 | **15× se opakoval týž vzor: ruční seznam místo projití složky (S27)** | opakovaný vzor není nepozornost, je to **návrhová vada projektu** | `tools/kontrola-diakritiky.py:267–269` |
| 5 | **3 PR prošla zeleným CI (39 kontrol, 0 selhání) a nemohla fungovat** | brána, která se ptá na přítomnost, **vyrábí falešné „hotovo"** | `OTEVRENA-TEMATA.md` ř. 70–84 |
| 6 | **7,5 h zelený conductor nad červeným repem** | **zdraví řídicího systému není zdraví cíle** | S18, `AGENTS.md` stanice |

> **Co z těch šesti čísel plyne dohromady:** projekt **není** případ „AI agent
> neumí programovat". Je to případ **„systém lhal sám sobě a nebylo to vidět"**.
> A to je chyba návrhu, ne modelu.

---

## 3. DESIGN — co funguje

*(Každý vzor: co to je · signatura · naměřený důkaz · proč to funguje.)*

### V1. **Každý stav má protějšek** (device)

**Co to je:** stav se neeviduje jako tvrzení, ale jako **dvojice** — tvrzení
**a** vnější fakt, který ho může vyvrátit.

**Signatura:** u každého stavu umíš říct **čím ho vyvrátíš**. Když ne, je to
tvrzení, ne stav.

**Naměřeno:** `done` se od 2. 10. 2026 (oprava **A1**) odvozuje z
`ok && merged` (`index.ts:385`, `:400–405`) — předtím bylo `done` v D1 u
`persist.save` (#139), `ui.hud` (#140) a `sim.mining` (#136), a **ani jeden
z těch PR neměl `merged_at`** a **ani jeden soubor nebyl v `origin/main`**.

**Proč to funguje:** chyba se **nedá vyrobit** — vznikne jen tam, kde existuje
i fakt. Je to jediná známá obrana proti třídě S29–S36 („zelená nad nepravdou").

### V2. **Brána má jak selhat — a ví se to o ní**

**Co to je:** každá kontrola má **nenulový exit** (nebo `fail` verdikt) jako
skutečnou možnost, a **existuje test, který to dokazuje** vrácením vady.

**Signatura:** hledej `echo "::error::"` bez `exit 1`, `continue-on-error`,
`catch {}` a `if not vady: print("OK")`. To jsou místa, kde brána nemá zuby.

**Naměřeno:** v `agent.yml` bylo **5× `exit 1`, ale všechny před krokem
auto-merge** — za krokem na ř. 687–693 **žádný**. Ověřeno proti nasazené verzi
(2. 10. 2026, 05:47 UTC, 33 425 bajtů). Opraveno **A3**.

**Proč to funguje:** „nesloučeno" přestane být **zelený běh**.

### V3. **Měření přizná, že neproběhlo**

**Co to je:** místo „prošlo / neprošlo" je **třetí a čtvrtý stav**:
`not_run` (nemám co měřit) a `unknown` (spadl jsem) — a **obojí je vidět**.

**Signatura:** prázdný seznam, který se tiše proiteruje; `[]` ve výpisu, které
vypadá jako naměřená nula; brána, která nad 0 souborů hlásí zelenou.

**Naměřeno:**
- `check-wiring.py:73` čte jen `scripts/*.gd`; nad **nulou** souborů vrátí
  prázdné `vady` a vytiskne *„Vše v pořádku: každá funkce je odněkud volaná."*
  s `exit 0` (`:169`).
- `check-assets.py:232–252` hledá `assets/sprites/walk_*.png`, kde je **0
  souborů** → kontrola `min_silhouette_iou: 0.80` ze specu se **nikdy neuplatní**,
  i když spec deklaruje `framy: 8`.
- `check-schema.py` **tiše přestal měřit** výchozí buňku: hledal `var cell := 16`,
  po migraci na izometrii je v kódu `const CELL_W_DEFAULT := 96` → regexy
  nenašly nic → cyklus nad prázdným seznamem → **zelená**. Prozrazoval to
  jediný řádek `level.gd: výchozí cell=[], fallback=[]`.

**Proč to funguje:** *„brána nic nehlásí" může znamenat „brána se na to
nedívá"* — a to je jiná věta než „je to v pořádku".

### V4. **Deklarace místo konvence**

**Co to je:** co je dnes konstanta v nástroji, je **záznam v datech projektu**.

**Signatura:** najdi v nástroji jméno souboru, příponu, cestu nebo číslo,
které patří konkrétnímu projektu. To je konvence, kterou nikdo nevynucuje.

**Naměřeno:**
- `check-schema.py:212–218` má **jména souborů jedné hry** (`scripts/level.gd`,
  `scripts/world.gd`) v **obecném** nástroji → u jiné hry (i v Godotu!) se
  kontrola jen „přeskočí" (`:318`).
- `check-assets.py:222–223` má **role `coin`/`chest`/`player` a poměry
  0.6/0.45/0.85 natvrdo v kódu**.
- `baseline.py:60` — `SLEDOVANE` natvrdo.
- Naopak **správně**: autorita schématu je **per-game `assets/spec.json`** hry
  (rozhodnutí uživatele 30. 9. 2026) — a to je jediné místo, kde to vyšlo.

**Proč to funguje:** konvence se **rozjede** a nikdo si toho nevšimne;
deklarace se dá **validovat** a její rozchod je **vidět**.

### V5. **Dva zdroje pravdy se musí potkat — jinak je to vada**

**Co to je:** když dva soubory nesou totéž pravidlo, existuje **test, který
tvrdí, že se rovnají**.

**Signatura:** dva nástroje, dva seznamy, dvě kopie téhož souboru
(`.forge/` v šabloně **a** ve hře).

**Naměřeno:**
- V orchestra existují **dvě `check-schema.py`**: `repo/.forge/` (**461 řádků,
  opravená**) a `tools/kontrola-schematu.py` (**305 řádků, stará a slepá**).
  `validate-all.mjs:186` pouštěl **tu starou** a tiskl doslova
  `level.gd: výchozí cell=[], fallback=[]` + „Schéma je v souladu".
- **Vzor, který to řeší správně:** `tools/test-check-schema.py` — 17 offline
  testů, které **hlídají i shodu hashe mezi šablonou a hrou**. Při psaní
  odhalil **čtyři chyby ve vlastním regexu** a **jednu skutečnou**: šablona
  a hra se rozešly.

**Proč to funguje:** rozchod dvou kopií je **tichý**; test na shodu je **hlasitý**.

### V6. **Nástroj se testuje na známém správném I známém chybném**

**Co to je:** každé měřidlo má **fixturu**, na které **musí** projít, a fixturu,
na které **musí** spadnout.

**Signatura:** nástroj, který nikdy nespadl; test, který nikdy nezčervenal.

**Naměřeno:**
- `tools/test-check-schema.py` — 17 testů, **při psaní odhalil 4 chyby ve
  vlastním regexu** (case sensitivity, záměna os, první vs. poslední deklarace,
  `\b` po podtržítku).
- **Protipříklad:** `tools/test-cooldown.py` vypsal `CHYBA` a skončil **`exit 0`**;
  `test-eskalace.py` testoval stav, který conductor **nemůže vyrobit** (8–20
  běhů na úkol při stropu 5), takže nechytil, že watchdog **nikdy nevystřelí**.
- `sabotuj.mjs` rozlišuje **tři** výsledky: sabotáž se neuložila / brána je
  slepá / brána nefunguje. To je správná granularita.

**Proč to funguje:** „prošlo to" bez známého chybného případu **neznamená nic**.

### V7. **Vše se odvozuje, nic se neopisuje**

**Co to je:** cesty, čísla a odkazy se **počítají** (`__file__`,
`import.meta.url`, `rev-parse`), nikdy neopisují z historie.

**Signatura:** absolutní cesta v kódu; odkaz na projekt v konfiguraci, který
vznikl v jiném projektu; číslo zkopírované z dokumentu.

**Naměřeno:**
- V `release.yml` zůstal odkaz na **`forge-quest`** — **jinou živou hru**.
  Kdo ho otevřel, **hrál něco jiného** (30. 9. 2026). Pravidlo: odkaz se
  odvozuje **z názvu repa**.
- Před přesunem mělo **57 ze 72** skriptů absolutní cestu
  `C:\Users\Ssevc\Local-Deepseek\`; po přesunu se cesty v **45 souborech**
  `tools/` začaly odvozovat a ověření dalo „vše sedí **na bajt**".
- **Chybějící `AGENTS.md` v repu orchestra** (`.git` True, `AGENTS.md` False) —
  protože se projektový root hledá podle `.git`, orchestra **nedostávala žádná
  projektová pravidla**. Odvození nepomůže tam, kde chybí soubor.

**Proč to funguje:** opisovaná hodnota **zestárne tiše**; odvozená **spadne
nahlas** — a to je přesně to, co chceš.

### V8. **Nezávislé ověření (autor není reviewer)**

**Co to je:** co napsala jedna session, ověřuje **jiná**; co napsal jeden
model, kontroluje **jiný**; analýza se **nepíše v session, která opravuje kód**.

**Signatura:** jeden člověk/agent píše i schvaluje; dokument „potvrzuje"
svého autora.

**Naměřeno:**
- **2. 10. 2026: tři session psaly tytéž soubory** (`HANDOFF.md` psaly **dvě
  současně**) → vznikly **tři dokumenty, každý s jiným „dnešním stavem"**
  (nález N8).
- Session, která napsala analýzu **i** podle ní opravovala kód, měla za dvě
  hodiny **5 tvrzení, která přestala platit**.
- **Vzor, který to řeší:** návrh se zapíše **hned** (aby se neztratil kontext),
  ale **rozhodne o něm až příští session** (NA12).

**Proč to funguje:** autor **nevidí, co předpokládá** — a to se nedá vyřešit
snahou, jen oddělením.

### V9. **Bezpečnostní rozhodnutí v kódu, ne v konvenci**

**Co to je:** to, co se nesmí, je **vynucené mechanicky**, ne popsané.

**Naměřeno:**
- **Dva joby v `agent.yml`** (`:13–16`): job s klíči jen **čte**, job bez klíčů
  **zapisuje** → klíč se **nemůže** dostat do commitu.
- **Pull-worker místo self-hosted runneru** (`index.ts:8–10`) — telefon za NAT,
  žádné otevírání portů.
- **Agent nesmí měnit vlastní brány** (`agent.yml:625–631`: `tests/*`,
  `.github/*`, `.forge/*`, `project.godot`).
- **`.env` v generovaném `.gitignore`** (L5) — do té doby kopírování `.forge`
  rekurzivně přenášelo **reálný `FORGE_SECRET`** do cizího repa (S7).

**Proč to funguje:** konvence se poruší omylem; **mechanismus** se poruší jen
tehdy, když ho někdo vypne.

### V10. **Levná kontrola první (a je to pořadí, ne seznam)**

**Co to je:** brány jsou seřazené **podle ceny**, ne podle důležitosti —
a nejlevnější je **deklarace vs. skutečnost**.

**Signatura:** CI, které nejdřív testuje a pak zjišťuje, že si projekt
odporuje v zadání.

**Naměřeno:** `PLAN-VISION` rozhodl: **schéma je tvrdá brána a je první**
(*„když si hra odporuje v zadání, nemá smysl měřit ani kreslit"*), a vision je
**poslední a neblokuje**. Pořadí v CI se navíc **testuje**
(`tools/test-ci-workflow.mjs`): import assetů → schéma → testy → assety →
wiring → smoke → snímek → vision.

**Proč to funguje:** každá vrstva měří **proti něčemu**; když je to „něco"
rozbité, všechny další měří špatnou věc — jen draze.

### V11. **Poctivost je funkce, ne slušnost**

**Co to je:** konkrétní pravidla, která zabraňují tomu, aby měření lhalo:
komentáře se před hledáním vzorců **odstraní**; **poslední** deklarace
vyhrává; mrtvá větev se **pojmenuje**; „nedá se posoudit" **není** vada;
`null` („nevíme") **není** prázdný set.

**Naměřeno:**
- `check-schema.py:221–225` — *„Komentář popisující vadu nesmí vypadat jako
  vada."* (Bez toho kontrola hlásila vadu **i po opravě** a nutila „opravovat"
  správný kód.)
- `check-schema.py:63–78` — bere **poslední** deklaraci; „kdyby se bral první
  výskyt, hlásila by kontrola vadu i po opravě – a to je falešný poplach."
- `check-schema.py:353–361` — když `world.gd` zmizel, větve na něj „jsou
  **mrtvá, ne splněná**."
- `index.ts:506–512` — `null ≠ []`: *„Když se strom nepodaří načíst, je `null`
  = NEVÍME. Nesmí se to zaměnit s prázdným setem – to by zastavilo celou
  roadmapu."*

**Proč to funguje:** **falešný poplach je dražší než přehlédnutí** — vede
k „opravě" správného kódu, a tím ke ztrátě důkazu.

### V12. **Watchdog se hlásí i s nulou**

**Co to je:** stav hlídače je ve výstupu **vždy**, i když nic nenašel.

**Naměřeno:** `index.ts:873–876` — *„Stav watchdogu se hlásí VŽDYCKY (i s nulou),
aby bylo z odpovědi tiku vidět, že opravdu běžel a s jakým prahem – jinak by se
jeho výpadek poznal jen tak, že by chyběla notifikace, což se snadno přehlédne."*

**Proč to funguje:** u hlídače je **ticho nerozlišitelné od smrti**.

Všechno ostatní, co se osvědčilo, je v tabulce §7.

---

## 4. DESIGN — co nefunguje

### A1. **Stav bez protějšku** (nejdražší vzor projektu)

**Signatura:** stav, u kterého **neumíš říct, čím ho vyvrátíš**. `done` bez
artefaktu, `blocked` bez důvodu, „čeká se" bez termínu a vlastníka.

**Naměřeno:**
- `merged` se v `index.ts` **načítal** (`:367`, `:375`) a **rozhodovalo se jen
  podle `ok`** (`:386`); použil se **jen v textu notifikace** (`:409`) — a ta
  dokonce psala „(sloučeno automaticky)" u něčeho, co sloučeno nebylo. **S33:
  informace v systému BYLA, jen se zahodila.**
- `roadmap.updated_at` nesl **dva významy** („vzniklo" i „naposledy selhalo") →
  oprava jednoho rozbila druhý (**S12 → B1 → S38**).

**Cena:** tři PR visela, `done` lhalo u 3 granul, a vada se **přenesla**, ne
zmizela: *„kdyby se opravilo jen `index.ts:385` a ne `agent.yml:683–691`,
systém by dál vyráběl zelené běhy nad nesloučenými PR — jen by o tom `done`
nelhal."*

### A2. **Dva zapisovatelé téhož stavu**

**Signatura:** dvě cesty, které zapisují totéž; jedna z nich „něco navíc".

**Naměřeno:**
- `/report` (`:1329–1336`) u opakovatelného selhání zapsal **jen `tasks`**,
  `roadmap` ne → **cooldown se obcházel** a granule se zkoušela **každé
  2 minuty** místo za 3 h (spálila 5 pokusů za čtvrt hodiny). Dnes **opraveno**
  (`:1464–1472` píše `naposledy_selhalo` v obou větvích).
- **`stale-recovery`** (`:829–833`) nastaví `tasks.status='failed'` a
  `updated_at=now`, ale **`roadmap.naposledy_selhalo` nezapíše** → guard padne
  na fallback `r.rfail || r.tupd` (`:618`) → po 3 h vznikne **nový úkol
  s `attempts=0`** (`:751`) → **granule jede donekonečna**. *(vlastní čtení
  5. 10. 2026 — třída S38)*

**Cena:** strop pokusů **neplatí** na cestě přes timeout; watchdog se nikdy
nespustí (`ESCALATE_AFTER=8 > MAX_ATTEMPTS=5`, a počítá **běhy úkolu**).

### A3. **Brána, která měří přítomnost místo chování**

**Signatura:** `has_method(...)`, `if load(...) != null:`, hledání řetězce
ve zdroji, `contains("...")`.

**Naměřeno:** tři PR prošla zeleným CI (**39 kontrol, 0 selhání**) a
**nemohla fungovat**:
- `hud.gd` se v `_ready()` rozbil (Godot 3 API `margin_left`) → label se
  **nikdy nepřidal**; test se ptal jen `has_method("update")`.
- `save.gd` uložil **35 B** (jen pozici hráče) a **vrátil `true`**.
- `mining.gd` spadl na `node.has()` (Godot 3) a `/root/Skills` (neexistuje).

**Cena:** nepoznané „hotovo" — a hlavně **naučená nedůvěra k zelené**, která
pak brzdí i správné věci.

### A4. **Ruční seznam místo projití složky**

**Signatura:** `SOUBORY = [...]` v nástroji; seznam, který se musí doplňovat
při každém novém souboru.

**Naměřeno:** **patnáctý** výskyt téhož vzoru zaznamenán 2. 10. 2026
(`tools/kontrola-diakritiky.py:267–269`). Konkrétní škody:
- kontrola diakritiky měla **57 dokumentů**, ale v kořeni jich bylo **39**
  a v `_analyza` **45** → zelená nad **28 dokumenty, které nikdy neotevřela** —
  mezi nimi **sám audit**, podle kterého se opravovalo;
- dvě různé `check-schema.py` (S1) — ověřovací nástroj měřil **tu slepou**;
- **tři** různé seznamy pro synchronizaci šablona↔hra
  (`kontrola-driftu.mjs` 12 souborů, `sync-sablona-hra.py` 2, `sjednot-sablonu.py`
  textové náhrady) → *„co se stane, když se přidá nový soubor do `.forge/`:
  **nikdo si ho nevšimne**."*

**Cena:** každý nový soubor je **neviditelný**, dokud ho někdo ručně nepřidá —
a zelená vypadá stejně jako u zkontrolovaného.

### A5. **Nula a prázdno jako úspěch**

**Signatura:** `for x in seznam:` nad seznamem, který může být prázdný, bez
pojmenované poznámky; `[]` ve výpisu; brána, která nad 0 souborů hlásí OK.

**Naměřeno:** tři nezávislé případy v §3/V3 a k tomu
`validate-all.mjs`, které **končí `exit 0` i při `✗ NALEZENO 3 PROBLÉMŮ`**
(nenastavuje `process.exitCode`) — opraveno **A1**.

**Cena:** vypadá to jako **naměřená nula**, ale je to **neměřený stav**.

### A6. **Statická metrika, která nic nespustí**

**Signatura:** počet vzorů v souboru, ze kterého se dělá závěr o chování.

**Naměřeno:** čtenář chtěl ověřit tvrzení „testy 36/36" a **staticky spočítal
volání `test(`** → vyšlo **42** → „dokument lže". Po **spuštění** vyšlo
**36/36** — dokument měl pravdu **do puntíku**. A táž past: `git log
--diff-filter=D` **hlásí i přesuny**, takže se do dokumentace zapsalo
„smazáno" u souboru, který byl **přesunut a použitelný**.

**Cena:** vede k **„opravě" správného dokumentu** — tedy ke ztrátě důkazu.

### A7. **Brána, která čte citaci místo tvrzení** (a nastražená brána)

**Signatura:** vzor, který zabere na **citaci** dřívější vady v uvozovkách;
test, který zakazuje řetězec, jenž v kódu **je odjakživa**.

**Naměřeno:**
- Vzor `(\d+)\s+sloupc` zabral na **„32 sloupců"** = **citaci** chybného
  tvrzení, a skutečné tvrzení („správně je 39") **neměřil vůbec** → brána
  hlásila **6 „rozchodů" a ani jeden nebyl o dnešku** (`exit 1` byl správný
  výsledek ze špatného důvodu).
- **Nastražená brána:** test zakazoval `level.has_method("iso_position")`,
  což `player.gd:40` obsahuje **odjakživa** — a `level.gd` tu metodu **vůbec
  nemá**, takže větev je **mrtvá**. Test netvrdil nic o izometrii; měřil
  **přítomnost textu**.
- Měření „kolik je záznam a co tvrzení" mělo okno **5 441 znaků se sedmi daty**
  → jedno datum kdekoli v něm **umlčelo celý oddíl**.

**Cena:** **falešný nález o správném kódu** je horší než slepé místo — nutí
„opravovat" fungující věc.

### A8. **Kopírovaná logika místo čtení zdroje**

**Signatura:** test, který má **opsané** SQL / opsanou funkci; prah **natvrdo**
v testu.

**Naměřeno:** `test-cooldown.py` a `test-eskalace.py` logiku **opisují**; druhý
má `PRAH = 8` natvrdo a podává **8–20 běhů na úkol**, což conductor **nemůže
vyrobit** (strop 5) → **nechytí**, že watchdog nikdy nevystřelí. Kdežto
`tools/test-zamek-owns.py` **vytahuje `lockKeys()` ze zdrojáku** a spouští
**skutečný text funkce** — a to je jediný správný vzor v projektu.

**Cena:** test chrání **kopii**, ne systém; změna kódu ho **tiše mine**.

### A9. **Komentář, který obhajuje vadu**

**Signatura:** komentář, který vysvětluje, **proč je to takhle správně** —
u místa, které je špatně.

**Naměřeno:** `index.ts:372–374`: *„`run.status === completed` znamená, že
doběhl CELÝ workflow – tedy i krok automatického sloučení. Stav mergnutí je
proto v tuhle chvíli už konečný a dá se věřit."* **Není to pravda:** když gate
nastaví `ok=0`, krok sloučení se **vůbec nespustí** (`if:` na `agent.yml:677`)
a job přesto skončí **`success`**. *„Není to vada kódu ani vada komentáře — je
to **zdůvodnění, které zakonzervovalo vadu**."* (S34)

**Cena:** budoucí čtenář **neopraví** to, co je vysvětlené jako správné.

### A10. **Deklarace, kterou nikdo nečte**

**Signatura:** klíč v konfiguraci, ke kterému najdeš **0 čtenářů** v kódu.

**Naměřeno (a je to soubor vedle sebe):**
- `acceptance` a `provides` v roadmapě — **0 čtenářů** (S22).
- `done_note` — pole, které říká *„POZOR: v D1 hotovo, ale PR NENÍ sloučené"*,
  a **0 čtenářů**; systém **ví, že lže**, zapíše to — a **nemá jak to vynutit**
  (S35).
- `kind` granule **nic neřídí** (jen notifikace).
- `runs.artifacts` — mrtvý sloupec.
- `roadmap.status='queued'` se zapisuje a **nikde se na něj neptá**.
- role `worker`/`judge` ve `vision-profile.json` — profil sám přiznává
  *„`role` je dnes jen dokumentace"*.

**Cena:** vypadá to jako funkce. **Stav bez čtenáře je horší než chybějící
stav** — ten aspoň nikoho neuklidní.

### A11. **Mrtvá brána, která se tváří jako živá**

**Signatura:** brána, která má **všechna razítka** a žádného **člověka**;
kontrola, jejíž podmínka **nikdy nenastane**.

**Naměřeno:** `baseline.json` má **272 položek** se `schvalil: agent-init`
a razítka v **jedné minutě**; nad nimi `_ceka_na_lgtm: true`. Verdikt visionu
má jen `continue-on-error` → *„agent ho nikdy nedostane"*.
**A druhá polovina téhož:** *„LGTM cache je **LOKÁLNÍ optimalizace** — v CI
neplatí nikdy"* (`baseline.py:252` vyžaduje obrázek **uvnitř repa hry**,
ale CI píše snímek do `/tmp/frames`) → v CI se vision ptá **vždy**.

**Cena:** 272 „schválených" položek, které nikdo neschválil → **falešná
jistota**, a to je horší než žádná.

### A12. **Ladění modelu místo příčiny**

**Signatura:** rotace modelů u selhání, které s modelem **nesouvisí**.

**Naměřeno:**
- Úloha #40: **tři pokusy, stejný model, stejné selhání** (`nochange`).
- Task #128 i #131: **5× mistral/codestral**, stejné selhání.
- **95 běhů** skončilo „agent nic nezměnil" — a to je **vada editovatelné
  plochy nebo zadání** (aider odmítne editovat soubor, který v chatu není, a
  **poslechne** — *„ask them to add the files to the chat. End your reply and
  wait for their approval"*), **ne modelu**.
- **82 selhání na testech** = vada zadání nebo brány; **27 na parsování** =
  formát odpovědi, který nikdo nevynucuje.

**Cena:** spálená kvóta (a ta je **vzácnější než čas**) a **naučený falešný
závěr** „free modely jsou slabé", který je ve skutečnosti „posíláme špatné
zadání".

### A13. **Neposlaný kontext a nevejitý prompt**

**Signatura:** model, který opakuje chybu z jiné verze technologie; prompt,
který se do modelu nevejde.

**Naměřeno:**
- Běh **#241**: model napsal **konstanty z Godotu 3** do projektu na **Godotu 4**
  (`Cannot find member "ALIGN_LEFT" in base "Label"`) — konvence **neuváděla
  verzi enginu** (S17).
- **Groq:** `Request too large` s `TPM: Limit 8000`, `Requested` **~14,4 tis.**
  — hláška **9×**, a ve třech různých číslech (**14 398 / 14 377 / 14 402**).
  Náš prompt se do Groqu **nevejde a nevejde se ani po opakování**.

**Cena:** jeden celý běh (a běh je „jeden výstřel" — **1 volání modelu na běh**).

### A14. **Dokument, který tvrdí, že je stav — a je záznam**

**Signatura:** soubor, který se „přepisuje", ale v praxi se **jen přidává**;
hlavička, která říká jiné datum než poslední oddíl.

**Naměřeno:** `HANDOFF.md` má **6 214 řádků / 487 kB**, ale jeho **hlavička je
zastaralá** (tvrdí „Datum 2. 10. 2026 · Poslední session §16", přitom nejnovější
oddíly jsou §31 a §32 z 4.–5. 10.). A **ve workspace se sešlo pět dokumentů,
každý s jiným „dnešním stavem"** — protože ani jeden v hlavičce neřekl, **čím je**.

**Cena:** kdo hledá pravdu, čte ten **nejnovější podle data souboru** — a to je
náhoda, ne pravidlo.

---

## 5. POSTUPY — co funguje

*(Postup = co **dělat**, když něco děláš. Vzory z §3 jsou „jak to postavit",
postupy jsou „jak pracovat".)*

| # | Postup | Naměřený důkaz, že funguje |
|---|---|---|
| **P1** | **Než začneš opravovat, zjisti, co je špatně — nástroj, nebo předpoklad testu.** | `test-zamek-owns.py` vznikl jako **regresní test k opravě**, ne jako nová brána |
| **P2** | **Vrať vadu do kódu a podívej se, že test spadne** (mutační test). A **zkontroluj, že mutace proběhla** — jinak tvrdí totéž co ta, která projde. | `a1-a2-over.py` **23 kontrol, 4 mutace chyceny**; `test-p14a-mutace.py` **13 kontrol, 5 vad shodí** |
| **P3** | **Měř na známém správném i známém chybném.** | `tools/test-check-schema.py`: 17 testů, **odhalil 4 chyby ve vlastním regexu** |
| **P4** | **Plošné skeny dělej walkem (Python), ne grepem** — a **hledej nad konkrétní složkou, i skrytou**. | `grep` nad `orchestra/` → **0** absolutních cest; **Python walk → 80 v 59 souborech**. A `grep "FORGE_CMD"` nad `orchestra/` → **0**, nad `orchestra/repo/.forge/` → **5** |
| **P5** | **Piš skript, ne dojem** — každé měření je soubor, který se dá spustit znovu. | celý `_analyza/` (222 souborů), `hl-priciny.mjs`, `hl-vytizeni.mjs`, `p18-prompt-tokeny.py` |
| **P6** | **Když výstup vypadá jako vada souboru, přečti soubor jinudy — o kódování rozhoduje BAJT.** | `Get-Content` rozsypal češtinu, soubor byl v pořádku (`read_bytes().decode('utf-8')` prošel) |
| **P7** | **Když se dva zdroje rozcházejí, hledej, ČÍM se liší** — ne který „je správný". | `merged_by` v seznamu PR = `null`, v **detailu** = `ssevcikm-spec`; kdo měří seznamem, udělá závěr „sloučil to robot" — přesně obráceně |
| **P8** | **U každého čísla napiš, ODKUD je** (který endpoint, který čítač). | „běhy #355–#362" vs. `run_number` **#235–#241**; „20 běhů celkem" vs. `total_count` **241** |
| **P9** | **Hotovo = soubor je v `main` A ZAVOLEJ to, co od něj voláš** — pouhý výskyt souboru **není** důkaz. | doloženo na `assist.gd`: soubor **je**, API **chybí** (`evaluate()` vypíše `SCRIPT ERROR` a vrátí `[]`) |
| **P10** | **Ověř nasazení třemi kroky** (push dorazil → build na **správném** commitu → server posílá **nový** artefakt). `HTTP 200` **není** důkaz. | doloženo třikrát: `rev-list --count` = 0 · `release.yml #68 completed/success head:194735d` · `last-modified` **76 s po** pushi |
| **P11** | **Před destruktivní operací dry-run a radši nemazat.** | `/roadmap/reset?dry_run`, `/tasks/cleanup?dry_run` a pojistka `503` místo mazání, když se roadmapa nenačte |
| **P12** | **Zapisuj do workspace, ne do tempu — a když nástroj tvrdí, že zapsal, ověř, že soubor existuje.** | Godot `--write-movie "$env:TEMP\..."` doběhl **úspěšně** a **žádné soubory nevznikly**; po přesměrování do workspace fungoval bez další změny |
| **P13** | **Vizuální změnu ověř POHLEDEM.** | při migraci na izometrii byl **hráč překrytý dlaždicemi**; testy, schéma i assety byly **zelené** — chybu našel až snímek |
| **P14** | **Nové téma = nová session** (ať už kvůli nezávislosti pohledu, nebo kvůli ceně). | saturace kontextu ztrojnásobí cenu requestu ($0,0023 → $0,0068); **8 nasycených sessions = 62 % účtu** |
| **P15** | **Ukládej verdikty a slepé uličky, ne důkazy.** | ~150 tokenů vs. 5–50 k; „kdo ukládá důkazy, platí je znovu v každém requestu" |
| **P16** | **Nepřenášet skilly ani pluginy hromadně.** | katalog skillů je **prefix kontextu**; jeho změna **bourá cache** (naměřeno: 61 cache-bustů, 26,2 mil. tokenů za plnou cenu) |
| **P17** | **Zálohu ověř obnovou, ne tím, že vznikla.** | `_analyza/_archiv/` (333+ souborů) je **gitignorovaný, nezálohovaný a je to jediná cesta zpět** — opakuje se v pěti sekcích napříč třemi dny |
| **P18** | **Historická čísla se nepřepisují** — označí se „ve svém čase správná". | „10 výskytů" bylo ve svém čase správně; kdo to přepíše, **smaže důkaz** |
| **P19** | **Každý dokument v hlavičce řekne, ČÍM JE** a odkud brát stav; analytický navíc **datum spotřeby**. | jinak se ve workspace sejde pět dokumentů s pěti „dnešními stavy" (nález NA21 / N8) |
| **P20** | **Než označíš cizí číslo za nepravdivé, zopakuj ho TÝMŽ postupem.** | „34 vs 36 testů" nebyl rozpor, ale **čas** — commit sám v message říká „+ 2 nové testy (34 → 36)" |

---

## 6. POSTUPY — co nefunguje

| # | Postup (anti) | Naměřený důkaz škody |
|---|---|---|
| **N1** | **„Ověř si všechno."** | nedá se podle něj postupovat, splnit ani nesplnit; zadání musí být **vykonatelné, zastavitelné a kontrolovatelné** |
| **N2** | **Spustit test a věřit zelené.** | test vypsal `CHYBA` a skončil **`exit 0`**; jiný nad 0 souborů hlásil „Vše v pořádku" |
| **N3** | **Spočítat vzory v souboru a udělat závěr o chování.** | 42 vs. **36/36** — a vedlo to k „opravě" správného dokumentu |
| **N4** | **Hledat `Select-String`em.** | **tiše přeskočí soubory** → falešný negativ („nikde to není", přitom 2×) |
| **N5** | **Věřit exit kódu nástroje.** | Godot vrací **exit 0 i s Python tracebackem** na stderr; Blender totéž; hra s chybou ve skriptu skončí `exit=0` a chybu jen vypíše (**PR #9** takhle tiše přišel o všechny nepřátele a CI hlásilo úspěch) |
| **N6** | **Opravovat podle dokumentu bez přeměření.** | dokument tvrdil „32 sloupců", správně **39** — a číslo bylo chybné **už při zápisu**; přes **šest session** si toho nikdo nevšiml |
| **N7** | **Věřit tvrzení o stavu z dokumentu.** | dokument tvrdil, že dva commity **nejsou pushnuté**; API vrátilo jeden z nich jako **HEAD repa** |
| **N8** | **Věřit `git log --diff-filter=D`.** | hlásí i **přesuny** → do dokumentace se zapsalo „smazáno" a ztratilo se, že kód existuje |
| **N9** | **Počítat řádky z `git show` přes `Measure-Object -Line`.** | u `ci.yml` hlásil **166**, správně **182** (soubor nekončí newline) — a vypadalo to jako necommitnutá změna, která neexistuje |
| **N10** | **Věřit `Get-PSDrive` bez ohledu na oprávnění.** | v read-only sandboxu hlásí **`Free=0`** (a `Get-CimInstance` je „Access denied", takže nula **vypadá potvrzeně**) — málem z toho byl **blokující nález o nemožnosti přesunu**; správně `Free=869273522176` |
| **N11** | **Předpokládat, že „cíl junctiony" znamená totéž u všech objektů.** | u **hardlinku** vrací `Target` **cestu souboru samého**; kód, který se ptal „kam vede", jím **přepsal skutečný soubor** → **14 souborů zničeno** (naštěstí v karanténě) |
| **N12** | **Měnit model/skilly/nástroje uprostřed session.** | **70 z 89** změn hlaviček requestu bylo v `config`; 75 % cache-bustů vzniklo **v aktivní session** |
| **N13** | **Zvýšit paralelismus, aby to bylo rychlejší.** | ne dřív než po opravě zámku — jinak se **vyrábějí závody o soubory**, které auto-merge slije jako „cizí přepis" |
| **N14** | **Postavit bránu na nezměřené metrice.** | vision blokující sloučení: *„přesně ta chyba, kterou `AGENTS.md` zakazuje"* — nejdřív **změřit přesnost** |
| **N15** | **Nechat v kódu pole, které nic neřídí.** | `kind`, mrtvý `FORGE_CMD`, `runs.artifacts`, `done_note` — „budí důvěru" |
| **N16** | **Nefunkční metriku nechat ležet.** | *„Nefunkční metriku smazat, ne nechat ležet — budí důvěru."* ALE: **až po mutačním testu** — jinak se maže měřidlo, které fungovalo |
| **N17** | **Vyrobit platformu / abstrakci pro druhého konzumenta, který neexistuje.** | `PLAN-ROZVOJ` §1.5 to zamítl jako **předčasné**; *„když F5 nepřijde do rozumné doby, F3.5 se nedělá"* |
| **N18** | **Kupovat placený model / hardware „na zrychlení orchestra".** | orchestra platí za modely **0** → *„vyměnit nulu za nulu"* je nejdražší způsob, jak to zjistit |
| **N19** | **Předělávat cizí hotové věci „preventivně".** | *„nepředělávej hotové a otestované soubory — když najdeš vadu v tarifní logice, **nejdřív spusť `test-tarif.mjs`**: řekne ti, jestli je vada v kódu, nebo v tvém předpokladu"* |
| **N20** | **Věřit hvězdám a tvrzením z repozitářů.** | prázdný **0bajtový** repo s hvězdami; „11 000+ pluginů" **neověřeno**; maintainer Token Savioru **stáhl vlastní benchmark**, když zjistil, že z **143 sessions** nástroj zavolala **jedna jediná** |

---
## 7. Kde jsme vyhráli

*(Co · čím je to doložené · co to stálo / přineslo. **Cena je součást tvrzení** —
bez ní se „výhra" nedá srovnat s jinou.)*

| # | Výhra | Doložení | Cena / přínos |
|---|---|---|---|
| **W1** | **`done` = `ok && merged`** (A1) | `index.ts:385`, `:400–405`; naměřeno na #139/#140/#136 (všechny `merged_at: null`, ani jeden soubor v `origin/main`) | **~15 řádků, 1 soubor.** Zavřelo celou řadu „hotovo bez práce" (S29/S31/S33). **Nejlepší poměr ceny a dopadu v projektu.** |
| **W2** | **Stav `awaiting_human`** | `index.ts:406–417` | ~20 řádků. Agent svou práci udělal → **nepočítá se jako pokus** (jinak granule po `maxAttempts` zbytečně přejde do `failed` za to, že si ji nikdo nepřečetl) |
| **W3** | **Zámek `owns` skutečně blokuje** (invariant 17) | commit `6d2a856` + **regresní test 8/8** (`test-zamek-owns.py`, čte `lockKeys()` ze zdrojáku) | nález: dvě **různé reprezentace téhož klíče** (holé jméno vs. `{repo}/{soubor}`) — množiny se **nikdy neprotly**. Obecné poučení: *dva tvary téhož klíče na dvou místech je vada, kterou žádný test nevidí, dokud se nezeptáš, jestli se množiny mohou protnout* |
| **W4** | **`naposledy_selhalo` místo `updated_at`** (B1) | `index.ts:543`, `:613`, `:930`; nasazeno 2. 10., deploy #32 `head:7c11b2d50` | oddělil **dva významy jednoho sloupce**. *(⚠ zbytková díra: cesta přes timeout ten sloupec neplní — S38)* |
| **W5** | **Auto-merge brána má `exit 1`** (A3) | `agent.yml:698`; ověřeno proti nasazené verzi (5× `exit 1`, všechny před krokem sloučení) | „nesloučeno" přestalo být zelený běh. **Pozor na pořadí:** `exit 1` **nesmí** být před A1, jinak vznikne smyčka (PR nesloučen → běh červený → úloha zpět `ready`) |
| **W6** | **Pull-worker místo self-hosted runneru** | `index.ts:8–10`, `worker.mjs:8–12` | bezpečnostní rozhodnutí s odůvodněním (telefon za NAT, žádné porty, GitHub varuje u veřejného repa) |
| **W7** | **Polling místo reportu z workflowu** | `index.ts:287–291` | conductor vidí i běh, který spadne **dřív**, než by poslal report; **v repu hry nejsou další tajemství** |
| **W8** | **Dva joby: klíče vs. zápis** | `agent.yml:13–16` | klíč z LLM jobu se **nemůže** dostat do commitu |
| **W9** | **Optimistický zámek na claim** | `index.ts:942–946`, `:988–992` | souběh řešený **v DB**, ne v aplikaci → dispatch je bezpečný i při tiku každou minutu |
| **W10** | **`null ≠ []` u stromu `origin/main`** | `index.ts:506–512` | „nevíme" se nesmí zaměnit s „nic tam není" — jinak by se **zastavila celá roadmapa** |
| **W11** | **Vytažení rozhodovací logiky do testů místo opisování** (A3) | `validate-all.mjs` pouští `test-cooldown.py`, který **spouští skutečné SQL conductora** | hned při prvním běhu **naměřilo vadu S12** — a ta se pak dala opravit (B1) |
| **W12** | **Přesun na `E:` s odvozováním cest a se zákazem junctiony** | `PLAN-SEPARACE` §11: 45 souborů `tools/` odvozuje cestu; ověřeno „vše sedí **na bajt**"; **junctiona záměrně NE** („cesty mají spadnout nahlas") | odstranilo třídu vady „nepřepsaná absolutní cesta tiše funguje dál" |
| **W13** | **`AGENTS.md` do repa projektu** | `.git` True + `AGENTS.md` False **před** přesunem; po přesunu v obou repech (D2/P9) | orchestra **nedostávala žádná projektová pravidla** — a nikdo si toho nevšiml, protože se „nějaká" pravidla načítala (obecná) |
| **W14** | **Vision jako poradní + LGTM cache** | `ci.yml:143–147` (`continue-on-error`, zdůvodněno chybovostí), `baseline.py` (schválený a nezměněný obrázek = **0 volání modelu**, doloženo testem) | **falešný poplach je dražší než přehlédnutí** — a je to jediná brána, která to má přiznané |
| **W15** | **Měření mezí vlastního nástroje** | `baseline.py`: phash je **slepý na barvu** (červená i modrá se stejnými bloky → stejný hash `f8f8f8f0f0070707`) a **degeneruje u jednolitého** obrázku (`8000000000000000`) → doplněn barevný podpis a `sha256` | bez toho by **změněný asset prošel jako nezměněný** — tichá chyba horší než žádná cache |
| **W16** | **Zamítnutí předčasných abstrakcí** | `PLAN-ROZVOJ` §1.5 (plugin systém, Backstage/IDP, monorepo, vlastní DSL), `PLAN-ORCHESTRA-AI` §10.3 A1–A5 | každé „ne" ušetřilo dny a **ani jedno nebrzdilo práci** |
| **W17** | **Odmítnutí brány na nezměřené metrice** | `PLAN-ORCHESTRA-AI` §10.3 A2 — vision blokující sloučení **NE**, dokud se nezměří přesnost | přesně ta chyba, kterou `AGENTS.md` zakazuje |
| **W18** | **Experiment typu A („konec měřidel")** | `ZADANI-A` + KRONIKA ř. 22: **hypotéza NEPOTVRZENA** (11 omylů místo 0–2), testy hry **65 → 89 kontrol**, `_dukaz-assist.gd` **exit 1 → 0** | **i nepotvrzená hypotéza je výhra**, protože dala číslo: *měřidla nejsou příčina, jsou místo, kde se to projeví* |
| **W19** | **Nalezení pasti v podmíněném testu** (typ A) | test se zapne, až hráč dostane `move()`: `main` bez granule = **59 kontrol, 0 selhání**; `main` + třířádkový `move()` = **60 kontrol, 1 selhání** | rozdíl **1 kontrola** je jediná, která se dřív vůbec nespustila. **Metoda: vlož minimální artefakt do kopie a sleduj, kolik kontrol se zapne** — když nula, brána o té smlouvě netvrdí nic |
| **W20** | **Nalezení bloku omylů, který neviděla žádná brána** | KRONIKA ř. 22: blok zapsaný jako `### 24.16` místo `### 8x.` — **žádná brána ho neviděla** → opraveno a přidána **kontrola, která se ptá naopak** („má každý nadpis v dokumentu kotvu v bráně?") | vada byla nalezena **tím, že se hledala opačná otázka** |

---

## 8. Kde jsme selhali

| # | Selhání | Doložení | Cena |
|---|---|---|---|
| **L1** | **7,5 h orchestra nevydala ani granuli — a conductor hlásil `ok: true`** | S18, měřeno živě 1. 10.: `/health ok:true`, `ready: 7`, `/failed` **prázdné**; `main` hry měl **7,5 h červené CI** | příčina byla **mimo** conductor: `check-schema.py:386` importoval `PIL` **uvnitř funkce** a `ci.yml` ho v tom kroku neinstaloval. **Zelený conductor nad červeným repem je nová třída tichého selhání** — a `/failed` bylo prázdné, protože **selhaly běhy, ne úlohy** |
| **L2** | **Tři PR prošla zeleným CI a nemohla fungovat** | `OTEVRENA-TEMATA` ř. 70–84: `hud.gd` spadl v `_ready()`, `save.gd` uložil **35 B** a vrátil `true`, `mining.gd` spadl na Godot 3 API | CI hlásilo **39 kontrol, 0 selhání**. Náprava: **41 → 59 kontrol** funkčních místo `has_method`; s vrácenými vadami **13 selhání** (`exit 13`) |
| **L3** | **`done` u práce, která v `main` nebyla** | `world.map` i `entity.player` byly `done` v roadmapě **i** v D1; `c651368` přesunul `world.gd` do `_retired/`; `entity.player` dodal **jen `project.godot`** (+4 řádky) | **stav v plánu není důkaz** — a staví se na něm celý DAG. *„Před stavbou na cizí granuli najdi její soubor v `main` a ZAVOLEJ to, co od ní voláš."* |
| **L4** | **Prázdný artefakt prošel** | `world.nodes` dodán jako **PRÁZDNÝ soubor (0 B)** a CI to nechytilo | brána na „soubor existuje" nestačí; musí být i **nenulový a funkční** |
| **L5** | **Granule nesla smlouvu bez tvaru dat** | `JAK-PSAT` §4.3: kontrakt „Hráč → `move()`, inventář, `die()`“ **nedefinoval typy ani volajícího** → `mining.gd` čte `resource_id`/`difficulty`/`cell`, ale **mapa nemá markery surovin — 0** | agent si **vymyslí rozhraní** a vymyslí ho jinak než sousední granule. Slovo `acceptance` se v `DESIGN.md` ani `ARCHITEKTURA.md` nevyskytovalo **0×** |
| **L6** | **Zadání granule odkazovalo na API, které už neexistuje** | `JAK-PSAT` §4.4: zadání `engine.shell` odkazovalo na `world.iso_position`, ale izometrie je dnes v `level.gd` | *„zadání granule je taky dokument a musí se udržovat"* |
| **L7** | **Pět tvrzení analýzy zestaralo vlastní prací** | analýza vznikla **05:45**, podle ní se **08:38–08:52** provedly kroky A1–A4 → **5 tvrzení přestalo platit**; ověřeno nástrojem `n8-zastarala-analyza.py` | o dvě hodiny později se analýza četla jako **popis dneška**. Ironie: analýza *„stavu, který si systém hlásí sám"* se **sama stala takovým stavem** |
| **L8** | **Tři session psaly tytéž soubory** | 2. 10.: `7cd67c66` (analýza), `7db45275` (jazyk), `eb127abd` (provedení); `HANDOFF.md` psaly **dvě současně** | vznikly **tři dokumenty, každý s jiným „dnešním stavem"**; jedna session **přepsala** verzi, které chyběla rozhodnutí druhé (N8) |
| **L9** | **Číslo bylo chybné už při zápisu a nikdo si toho nevšiml šest session** | `AGENTS.md` tvrdil **32 sloupců**, správně **39**; schéma se přitom **neměnilo** | chyba v **autoritě** se neprojeví jako chyba — projeví se jako **důsledek na pěti jiných místech** |
| **L10** | **Brána měřila jinou kopii pravidla** | dvě `check-schema.py` (461 opravená vs. 305 slepá); `validate-all.mjs:186` pouštěl **tu slepou** | „nástroje se množily místo aby se nahrazovaly" — jedno ze **tří strukturálních míst**, kde se chyba ztrácí |
| **L11** | **Šablona v gitu byla neúplná (disk ≠ git)** | S2: `repo/` měl **8 změněných trackovaných** a **4 důležité soubory vůbec netrackované**; `release.yml` v gitu odkazoval na **`forge-quest`** (jinou živou hru) | kdo orchestra naklonuje, dostane **jinou verzi**, než jaká běžela — a **nic to neohlásí** |
| **L12** | **Onboarding nové hry byl mrtvá větev** | `install-into-repo.ps1:36–38` vyžaduje `projects\<Projekt>` (neexistuje), `:86` posílá na smazaný `forge.cmd`; nová hra **zdědí** 31 granul cizí hry, `"hra": "uo-shadows"` v profilu a `.env` s reálným `FORGE_SECRET` | třetí strukturální místo: nová hra se zakládá **ručním kopírováním** a dědí pozůstatky |
| **L13** | **Prompt se nevešel do modelu a spálil pokus** | Groq `TPM: Limit 8000` vs. `Requested` ~14,4 tis., hláška **9×**; tři různá čísla téhož (14 398 / 14 377 / 14 402) | a **zmenšit granuli nepomůže** — pevná část promptu (`CONVENTIONS.md` 3 839 t. + systémový prompt ~2 166 t.) je **většina vstupu** |
| **L14** | **Rotace modelů u selhání, které nebylo modelu** | úloha #40: **3 pokusy se stejným modelem**, stejné selhání; task #128 i #131: **5× mistral/codestral** | **kvóta je vzácnější než čas** — a „free modely jsou slabé" byl **falešný závěr** z pravdivých dat |
| **L15** | **`ESCALATE_AFTER=8 > MAX_ATTEMPTS=5`, a počítá běhy úkolu** | `index.ts:246`, `:251`; `wrangler.toml:58` vs. `:55` | watchdog **nikdy nevystřelí** → granule, která selhává pořád, jede dál a **nikdo se to nedozví** |
| **L16** | **Grafické chyby, které žádná brána nevidí** | 30. 9.: při migraci na izometrii byl **hráč překrytý dlaždicemi**; testy, schéma i assety **zelené** — našel to až **snímek** | `check-assets.py` je spokojený (38×95 px, 1103 barev, 0 děr) a **neumí říct, jestli je na spritu to, co má být** |
| **L17** | **Čtrnáct souborů zničeno „opravou"** | 1. 10.: `Target` u **hardlinku** vrací cestu souboru **samého**; kód podle ní objekt přepsal → **14 souborů** nahrazeno junctionami (vráceno z karantény a ověřeno hashem) | *„„oprava" je taky zásah do dat. Jeden zdroj pravdy stačí na čtení; na mazání a přepisování nestačí."* |
| **L18** | **Málem blokující nález o nemožnosti přesunu** | 4. 10.: `Get-PSDrive E:` v **read-only sandboxu** hlásí `Free=0 / Used=0` a `Get-CimInstance` je „Access denied" → **nula vypadá potvrzeně**; správně `Free=869273522176` | *„z 0 GB vznikne blokující nález o nemožnosti přesunu"* — a stačilo měřit **dvěma způsoby** a zapsat **oprávnění** |
| **L19** | **Ledger otevřených témat zestaral a nikdo ho nepřeměřil** | `OTEVRENA-TEMATA.md`: ř. 522 tvrdí „`validate-all.mjs` je ČERVENÝ" (dnes zelený), ř. 448 „zavírá se, až session doběhne" (**splněno**), ř. 502 „zbývá kontrolovat strom" (**APLIKOVÁNO celé**) | je to **přesně ta vada „stav, který si systém hlásí sám"**, kterou projekt celou dobu řeší — a postihla **jeho vlastní ledger** |
| **L20** | **Vada měřidla, kterou nikdo neměl jak najít** | H70: `zadani-kontrola.py:196` iteruje **slovník** a rozbaluje ho na dvojici → `ValueError: too many values to unpack`; **ve zdravém stavu se větev nikdy nezavolá** | *„bezpečnostní síť spadne při prvním skutečném použití"* — protože **o větev, která se nikdy nezavolá, neexistuje důkaz** |

---

## 9. Ekonomie: co je levné, co drahé a kde je páka

### 9.1 Ekonomie změny (kolik co stojí)

| Změna | Naměřená cena | Zdroj |
|---|---|---|
| Změnit **jeden údaj v jednom souboru** | **hodiny**, nulové riziko | A1 (`done`): 1 soubor, ~15 řádků; A2: ~20 řádků |
| Přidat **granuli do plánu** | 1 řádek — **ale nikdo neřekne, že chybí** (`size_lines` chybí u **13 z 18**) | HLOUBKOVA-2 §O7 |
| Přidat **soubor do `.forge/`** | **3 ruční seznamy** (12 / 2 / textové náhrady) → *„nikdo si ho nevšimne"* | ARCHITEKTURY §5.1 |
| Přidat **bránu** | **1 soubor v KAŽDÉ hře** (dvě kopie se rozejdou) | 1. kolo §O4 |
| Vyměnit **engine** | „vyměnit obálku" — `.github/workflows` + 3 godot brány + 2 infra soubory; **jádro se nemění** | ARCHITEKTURY §1.1; **vlastní čtení 5. 10.** |
| Přidat **druhou hru** | **≥ 27 souborů + 5 tajemství** a **kapacita se nezdvojnásobí, jen rozdělí** (klíče jsou per-repo) | 1. kolo §O4, invariant 3 |

**Pravidlo, které z toho plyne (a je měřené):**
> **Změna je levná, když se vejde do jednoho souboru a nevyžaduje synchronizaci
> na N místech.** Univerzalita se nezvyšuje **přidáváním schopností**, ale
> **odstraňováním nutnosti synchronizovat.**

### 9.2 Žebřík ceny vady (čím později ji chytíš, tím dráž)

| # | Kde se vada chytí | Naměřená cena | Příklad |
|---|---|---|---|
| 1 | **V kontraktu** (tvar dat, přijímací kritérium) | **~0** | kdyby `Hráč` měl v designu tvar dat, `mining.gd` by si nevymyslel `resource_id` (L5) |
| 2 | **V plánovací bráně** (před dispatchem) | minuty | chybějící `size_lines` u 13 granul — dnes to **hlásí**, ale `exit 0` |
| 3 | **V syntaxi** (`--check-only`) | jeden běh | 27 selhání na parsování |
| 4 | **V testech** | jeden běh + kvóta | 82 selhání na testech |
| 5 | **V bráně zapojení / chování** | jeden běh | 3 PR, která prošla a nemohla fungovat (L2) |
| 6 | **V CI na `main`** | **7,5 h odstávky celé orchestra** | chybějící Pillow v jednom kroku (L1) |
| 7 | **Při lidské kontrole PR** | člověk + **86 % PR sloučených ručně** | nejisté kvůli tokenu (`merged_by` je u všech `ssevcikm-spec`) |
| 8 | **V produktu u hráče** | **nejdražší** | hráč nebyl vidět za dlaždicemi (L16) |

> **Optimum je v tom žebříku vidět:** každou vrstvu, kterou **přeskočíš**,
> zaplatíš **o patro výš** — a patro 6 stojí **hodiny celého systému**,
> zatímco patro 1 stojí **nula**.

### 9.3 Kde utíkají peníze (měřeno na DSH, 30. 9. – 2. 10.)

| Páka | Naměřeno | Podíl |
|---|---|---|
| **Výběr modelu** | `deepseek-v4-pro` = **23 % requestů a 70 % účtu** ($43,53 z $62,22) | **81 %** úsporného potenciálu |
| Práce mimo špičku | špička 01–04 a 06–10 UTC, Po–Pá | 9 % |
| Nebourat cache | **61 cache-bustů** = 26,2 mil. tokenů za plnou cenu | 6 % |
| Nižší `reasoningEffort` | reasoning = 49 % výstupu | 3 % |
| **Celkem dosažitelné** | $62,22 → **$13,34** | **−79 %** |

**Tři strukturální pravidla z toho:**

1. **Délka session je nákladová páka, ne kosmetika.** Session se 1676 kroky
   zaplatí ~1,2 mld. token-readů; **deset session po 168 krocích** se stejným
   obsahem práce zaplatí **zlomek** — každá začíná s prázdným kontextem.
2. **Cache-HIT vstup je největší jednotlivá položka účtu (52 %)**, ne „téměř
   zdarma" — cache zlevní **jednotkovou** cenu 50×, ale **objem přeteče
   všechno ostatní** (průměrný request nese **294 561** tokenů kontextu).
3. **Reasoning se platí dvakrát** (jednou jako výstup, podruhé znovu při
   každém dalším requestu z cache) — **každý reasoning token se průměrně
   přečte 196–232×**.

> **A jedno pravidlo, které platí pro orchestraci:** **indikátory pro MODEL
> jsou drahé a často bez efektu** — každé rozšíření promptu se platí
> **v každém requestu**. Užitečná je cesta **měřit a zobrazovat člověku**:
> čte se to z logu, **stojí 0 tokenů a nemůže to halucinovat**.

---

## 10. Co je optimální

*(Syntéza. Tohle je odpověď na „co je optimální" — a je to **seznam
podmínek**, ne jedna věta.)*

### 10.1 Dvanáct pravidel, která se vyplatila všude, kde se použila

| # | Pravidlo | Naměřený důkaz |
|---|---|---|
| **O1** | **Žádný stav bez protějšku.** Ke každému stavu umíš říct, **čím ho vyvrátíš**. | A1 (`done` = `ok && merged`) — nejlepší poměr ceny a dopadu (§7/W1); opak = S29–S36 |
| **O2** | **Žádná tichá cesta.** Každá brána umí **selhat** i **přiznat, že neměřila**; každý `catch` je událost. | 3 PR zeleně a nefunkční; `check-wiring` nad 0 souborů „Vše v pořádku" |
| **O3** | **Rozhodnutí se měří, netvrdí.** „Silný model", „limit modelu", „je to hotové" — všechno jsou **měřené veličiny s datem a důkazem**. | `strongModels` je seznam, ne měření; „32 sloupců" vydrželo 6 session (L9) |
| **O4** | **Diagnostikuj před opakováním.** Opakování je funkce **příčiny**, ne času ani rotace. | 95× „nic nezměnil", 82× testy, 27× parsování (L14) |
| **O5** | **Jeden zdroj pravdy na jeden údaj — a je deklarovaný.** | dva tvary téhož klíče (W3), dvě `check-schema.py` (L10), `updated_at` se dvěma významy (W4) |
| **O6** | **Deklarace místo konvence; projití místo seznamu.** | S27 **patnáctkrát** (A4) |
| **O7** | **Levná kontrola první.** Pořadí bran podle ceny, ne podle důležitosti. | schéma před vision; `--check-only` před testy |
| **O8** | **Falešný poplach je dražší než přehlédnutí.** Brána, která obviňuje správný kód, je horší než slepá. | nastražená brána (A7); vision neblokuje (W14) |
| **O9** | **Co neumí stroj, je vidět jako „čeká na člověka".** Nikdy tiše odškrtnuté. | obsah spritu, hratelnost, kontaktní arch — „ruční fitness funkce zůstávají ruční a **musí zůstat vidět**" |
| **O10** | **Autor není reviewer.** Co napsala jedna session, ověřuje jiná. | 5 tvrzení zestaralo (L7), tři session nad jedním workspace (L8) |
| **O11** | **Zálohu ověř obnovou; cestu odvozuj, nikdy neopisuj.** | 14 souborů zničeno (L17); `_archiv` nezálohovaný (P17); 57 ze 72 skriptů s absolutní cestou před přesunem |
| **O12** | **Nic nestav, dokud to nemá druhého konzumenta — nebo dokud nemáš falzifikátor.** | W16 (zamítnuté abstrakce); a **kontrakt sám je hypotéza**, proto se měří (≤ 5 souborů) |

### 10.2 Optimální proporce (kde utrácet úsilí)

**Podle naměřených pák, v tomto pořadí:**

| Priorita | Kam dát úsilí | Proč (naměřeno) |
|---|---|---|
| **1** | **Do feasibility před dispatchem** | **55 %** běhů umíralo do **30 s** — největší jednotlivá ztráta a **nejlevnější** ji odstranit (neposlat) |
| **2** | **Do kontraktu a přijímacího kritéria** | vada z patra 1 žebříku (§9.2) stojí ~0; z patra 6 stojí **7,5 h celého systému** |
| **3** | **Do protějšku u stavu** | `done` bez `merged` = tři falešná „hotovo"; oprava = 15 řádků |
| **4** | **Do brán, které měří chování** | 3 PR zeleně a nefunkční → 41 → 59 kontrol |
| **5** | **Do měřidla měřidla** | **84 % omylů bylo v měřidle** — a offline test se dvěma fixturami odhalil 4 chyby ve vlastním regexu |
| **6** | **Do viditelnosti „čeká na člověka"** | protože **86 % PR sloučil člověk** (nejisté) a obsah **nikdo jiný** posoudit neumí |

> **A jedna věc, do které se nevyplácí dávat úsilí:** do **přesvědčování
> modelu**, aby byl spolehlivější. Naměřeno: hlavní ztráty nejsou v tom, že
> model **neumí**, ale v tom, že **nedostal** (tvar dat, verzi enginu, soubor
> v chatu, vejitý prompt) — to jsou vady **zadání**, ne modelu.

### 10.3 Rozhodovací tabulka (když X, tak Y)

| Situace | Co dělat | Proč |
|---|---|---|
| Něco **nefunguje** a nevím proč | **Nejdřív zjisti, jestli kontrola vůbec proběhla** | „brána nic nehlásí" může znamenat „brána se na to nedívá" |
| Řídicí systém je **zelený** a práce **stojí** | **Ptej se na stav CÍLE**, ne na stav řidiče | 7,5 h zeleného conductora nad červeným repem (L1) |
| Selhání se **opakuje** | **Diagnostikuj třídu** — a teprve pak opakuj (a nejspíš **něco jiného**) | 3× a 5× stejný model, stejné selhání (L14) |
| Chci **přidat abstrakci** | **Spočítej konzumenty DNES.** Když je jeden, je to hypotéza — a potřebuje **falzifikátor** | W16, O12 |
| Chci **přidat bránu** | **Nejdřív dokaž, že ta stávající umí selhat** | „nová brána nad zeleným systémem nic nezmění" |
| Mám **dvě čísla, která si odporují** | **Hledej, čím se liší** (čas, čítač, endpoint) — ne, které „je správné" | P7, P8, P20 |
| Test **prošel** a mám z toho radost | **Vrať do kódu vadu** a podívej se, že spadne. A ověř, že **mutace proběhla** | P2 |
| Nástroj **tvrdí, že zapsal** | **Ověř, že soubor existuje** | P12 (Godot do tempu) |
| Nechci **nic rozhodnout za uživatele** | Zapiš návrh, ale **rozhodni až příští session** | NA12 (autor není reviewer) |
| Mám **zdokumentovat stav** | Napiš **datum, zdroj čísla a čím dokument je** | A14, P19, NA21 |
| Něco **vypadá jako vada logiky** | Nejdřív ověř **nástroj, kódování a oprávnění** | skill `dsh-prostredi`: EPERM, BOM/CRLF, cp1252, junctiony, `Get-PSDrive` |

### 10.4 Optimální design v pěti vrstvách (a co v každé rozhoduje)

```
1. KONTRAKT     co je hotovo, jaký je tvar dat, co je zakázané   <- rozhoduje o ~0 nákladů
2. ZADÁNÍ       strukturované, s rozpočtem, vejde se do modelu    <- rozhoduje o 55 % běhů
3. PROVEDENÍ    kdo to udělá (model/uživatel) + co umí            <- rozhoduje o ceně
4. OVĚŘENÍ      brány 4 stavů + pokrytí + nezávislé potvrzení     <- rozhoduje o důvěře
5. PRODUKT      přijímací kritéria + lidská fitness funkce        <- rozhoduje o hodnotě
```
**Co je v tom optimu neobvyklé:** vrstva **1** je nejlevnější a rozhoduje
nejvíc; vrstva **3** („který model") je ta, na kterou se nejvíc myslí —
a v měření je to **až třetí** páka.

---

## 11. Kontrolní seznam pro nový projekt (co postavit první den)

*(Odvozeno z toho, co se v tomto projektu **muselo dodatečně opravovat**.)*

| Den | Co postavit | Protože bez toho |
|---|---|---|
| **1** | **Repozitář jako jediný zdroj pravdy** — co je na disku, je i v gitu (`git ls-files` = disk) | S2: 4 důležité soubory netrackované; klon = jiná verze |
| **1** | **`AGENTS.md` v repu** (+ ověřit, že se **skutečně načítá**: `.git` True **a** `AGENTS.md` True) | orchestra nedostávala pravidla a nikdo si toho nevšiml |
| **1** | **Jeden deklarovaný soubor projektu** (cesty, brány, příkazy, co agent nesmí) | konstanty v 6 nástrojích + 3 ruční seznamy |
| **1** | **Procházení složky místo ručních seznamů** u **každé** kontroly | S27 **patnáctkrát** |
| **2** | **Brány se čtyřmi stavy** (`pass/fail/not_run/unknown`) + **pokrytí** `ran/declared` | S3, S27, „zelená nad prázdnem" |
| **2** | **Ke každé bráně dvě fixtury** (správná, chybná) + **prázdná** | bez nich „prošlo to" neznamená nic |
| **2** | **Brána, která má jak selhat** (nenulový exit) | S32: „NALEZENO 3 PROBLÉMŮ" a `exit 0` |
| **3** | **Definice hotovo s protějškem** (artefakt v `main` **a** zavolané chování) | S29/S31: `done` bez práce v `main` |
| **3** | **Zákaz stavu bez čtenáře** (a kontrola, že každý klíč má konzumenta) | 6 mrtvých polí a bran (A10/A11) |
| **4** | **`/health` cílů, ne řidiče** (+ test, že **umí zčervenat**) | S18: `ok: true` nad 7,5 h červeným cílem |
| **4** | **Watchdog, který jedná** — a jeho strop je na **jednotce práce**, ne na pokusu | S14: prah 8 > strop 5 → nikdy nevystřelí |
| **5** | **Měření schopností, ne seznam** (co který model/nástroj **naměřeně** umí, s datem a důkazem) | `strongModels` jako seznam; limity v komentářích |
| **5** | **Diagnostika před opakováním** (třída selhání → jiná reakce) | 95× „nic nezměnil" a rotace modelů |
| **6** | **Jedna stránka stavu pro člověka** (z logu, 0 tokenů) | indikátory v promptu jsou drahé a nevedou k rozhodnutí |
| **6** | **Viditelná fronta „čeká na člověka" s vlastníkem** | obsah a hratelnost **nikdo jiný** neposoudí |

---

## 12. Poctivost a falzifikátory

### 12.1 Co tenhle dokument neví

1. **Nic jsem sám nepřeměřil** kromě `conductor/src/index.ts` (vlastní čtení
   5. 10. 2026). Všechna ostatní čísla jsou **citace s datem a zdrojem**.
2. **Živý stav orchestra neznám** — nevolal jsem `/health` ani `/roadmap`.
3. **Čísla se v čase mění a některá jsou nejistá:** „86 % PR sloučil ručně" je
   **nejisté** (kvůli tokenu nelze odlišit člověka od `gh pr merge`), „82,7 %
   mrtvá" je z **1. 10.** a nebylo přepočteno, „120 offline testů" je součet,
   ne měření.
4. **Některé vzory jsou odvozené z jednoho případu** (§3/V12 watchdog je jeden
   komentář; §5/P9 je doložený jedním případem a jedním protipříkladem).
   **Jeden případ není zákon** — je to **kandidát na pravidlo**.
5. **Nevím, které vzory platí i pro projekt, který ještě neexistuje** — a to je
   test, kterým se má každé pravidlo prohnat, než se z něj stane šablona.

### 12.2 Co by tenhle dokument vyvrátilo

| # | Pozorování | Co by padlo |
|---|---|---|
| **F1** | Kdyby se ukázalo, že **`done` = `ok && merged` nezpůsobilo pokles falešných „hotovo"** | W1 by byl jen kosmetická oprava |
| **F2** | Kdyby **přehrání historie** ukázalo, že **nefeasibilní dispatche nejsou** tou příčinou (většina běhů do 30 s padala z důvodu, který předem poznat nelze) | priorita **1** v §10.2 je špatně a optimum je jinde |
| **F3** | Kdyby se ukázalo, že **většina omylů vzniká v práci, ne v měřidle** (opak čísla 84 %) | celá kapitola o měřidlech by byla přehnaná |
| **F4** | Kdyby **brány se čtyřmi stavy** nezvýšily počet odhalených vad | O2 by byl formalismus |
| **F5** | Kdyby **dva nezávislí agenti na téže úloze** produkovali shodný výsledek **i** shodné chyby | O10 (autor není reviewer) by ztratilo smysl |

### 12.3 Jedna věta na závěr

> **Nevyhráli jsme tím, že jsme psali lepší kód. Vyhráli jsme tím, že jsme
> postupně odstranili místa, kde si systém mohl lhát sám sobě** — a prohráli
> jsme všude, kde takové místo ještě zbylo. Kód byl skoro vždycky v pořádku;
> **lhala evidence.**

---

**Konec dokumentu.** Související: `NAVRH-ORCHESTRA-NG.md` (co z toho postavit),
`PLAN-ORCHESTRA-NG.md` (v jakém pořadí), `KRONIKA-PROJEKTU.md` (záznam,
odkud příklady jsou), `HANDOFF.md` (stav).

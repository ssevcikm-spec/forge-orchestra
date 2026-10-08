# Jak psát design dokumenty a plánovat vývoj (pro AI pipeline)

**Co tenhle dokument JE:** pracovní podklad pro **celkovou revizi skillu
`game-developer`** a pro **plánovaný přepis designu `uo-shadows`**. Není to
hotová metodika — je to **rostoucí dokument**. Každá session, která narazí na
nově **naměřenou** vadu designu nebo plánování, sem přidá oddíl (§7).

**Založeno:** 2. 10. 2026 · **Stav:** 1. sezení, **6 naměřených případů**
**Zadání (uživatel, 2. 10. 2026):** „zapiš poučky, abychom tomuto předešli…
dovyvinout s novými poznatky, jak psát design dokumenty a jak plánovat vývoj…
další sessiony ať tento dokument budují jako přípravu pro celkovou revizi skillu
(a také plánovaný přepis celého designu UO-Shadows, protože není dostatečný —
alespoň ne pro naši AI pipeline).“

**Jak číst čísla:** každý případ má **soubor, číslo a datum**. Co je bez měření,
je označené jako *(názor, ne měření)* — a nemá se z toho stát pravidlo.

---

## 1. Proč to existuje: tři PR prošla zeleným CI a nemohla fungovat

Naměřeno 2. 10. 2026 na `uo-shadows` (Godot 4.7.2, spuštěním souborů):

| Co | Naměřeno | Co to znamenalo |
|---|---|---|
| `hud.gd` (PR #29) | `_label.margin_left = 10` — `Control.margin_left` **v Godotu 4 neexistuje** (je `offset_*`) → `_ready()` se přerušil → **label se nikdy nepřidal** | HUD nebyl vidět; CI zelené (`39 kontrol, 0 selhání`) |
| `save.gd` (PR #28) | hledal komponenty ve skupinách, které nikdo nezakládá → zapsal **35 B** (jen pozici hráče) a **vrátil `true`** | „Uloženo“ bez uložení; chyba by se projevila až u hráče |
| `mining.gd` (#30) | `node.has()` — **Godot 3 API**; služby na `/root/Skills`, což neexistuje (`project.godot` nemá autoload) | `gather()` vždy spadlo, testy to neviděly |

**Společná příčina není „model udělal chybu“.** Model dostal granuli, jejíž
*smlouva nebyla v designu popsaná tvarem dat*, a bránu, která měřila
**přítomnost metody**, ne její chování. To jsou vady **plánování**, ne kódu.

---

## 2. Co musí design dokument obsahovat, aby se z něj daly vydávat granule

Každá položka je psaná jako **kontrolní otázka** — když na ni design neodpovídá,
granule se z něj vydat nedá (a agent si odpověď vymyslí).

1. **Kdo co poskytuje — a JAKÝ JE TVAR TÝCH DAT.**
   Kontrakt `Hráč → move(), inventář, die()` je jméno bez obsahu. Musí tam být:
   *jaké vlastnosti a jakých typů* ten objekt má (`hp: int`, `inventory: Array`
   předmětů s `id`/`trvanlivost`) a **kdo to volá**.
   *Naměřeno:* `entity.player` měl v kontraktu „inventář“, agent dodal jen
   `project.godot`; dnes `assist.gd` čte `player.hp/max_hp/mana/max_mana/target`
   a `economy.gd` volá `player.add_item/remove_item` — tedy **jiné komponenty
   už to volají, ale v designu to není**.
2. **Přijímací kritérium u každé schopnosti** — konkrétní volání, které musí
   projít (`gather(uzel_s_rudou, obtížnost 5) == 6`), ne „funguje to“.
   *Naměřeno:* `acceptance: ["tests","wiring"]` je v roadmapě u každé granule,
   ale slovo `acceptance` se v `docs/DESIGN.md` ani `docs/ARCHITEKTURA.md`
   nevyskytuje **0×** — takže „čím se to ověří“ se nevymýšlí z designu, ale
   v zadání granule.
3. **Definice „hotovo“.** „PR je sloučené“ **není** hotovo. Hotovo = soubor je
   v `main` **a** brána jeho funkci **zavolala**.
   *Naměřeno:* `world.map` i `entity.player` jsou `done` v roadmapě **i v D1**,
   ale jejich práce v repu není (viz §4.2).
4. **Non-goals (co je mimo rozsah) — explicitně.** Jinak si agent domyslí
   sousední vrstvu a vznikne druhý zdroj pravdy.
   *Naměřeno:* `world.gd` nesl vlastní `const cell: int = 32` vedle izometrické
   mřížky `level.gd` (96×48) — a musel být přesunut do `_retired/`.
5. **Vlastnictví souborů (`owns`) a co je zakázané** (`tests/`, `.forge/`,
   `project.godot`). Bez toho se dvě granule poperou o jeden soubor.
6. **Pořadí a závislosti** — „závisí na X“ musí znamenat **„X je hotové a jeho
   API existuje“**, ne „X je v DAGu“ (§3.2).

**Kontrolní seznam před vydáním granule** (6 otázek, každá musí mít odpověď
v designu, ne v hlavě plánovače):

- [ ] Vím, **jaký tvar dat** moje granule dostane a vrátí — a je to v designu?
- [ ] Vím, **kdo ji zavolá** (a existuje ten volající, nebo vznikne později)?
- [ ] Mám **konkrétní** přijímací kritérium (volání + očekávaná hodnota)?
- [ ] Je v zadání **co NEDĚLAT** (aby agent neopsal cizí vrstvu)?
- [ ] Vlastní granule **disjunktní soubory** s běžícími granulemi?
- [ ] Umí brána **selhat**, když to, co má vzniknout, nevznikne (§3.3)?

---

## 3. Jak plánovat vývoj

### 3.1 Velikost granule se řídí modelem — a musí být DEKLAROVANÁ

`size_lines` + `model` patří do roadmapy u každé granule, jejíž změna přesahuje
60 řádků. **Naměřeno 2. 10. 2026:** u `sim.mining`, `persist.save` a `ui.hud`
deklarace chyběla → platil výchozích 60 → auto-merge je (správně) zamítl a tři
PR zůstaly viset. `lint-roadmapa.py` to hlásí jako `[5]` — u **13 z 21** granul.

### 3.2 Závislost znamená „hotové a funkční“, ne „je v DAGu“

`engine.shell` měl v `depends_on` hotové granule — a přesto by se stavěl nad
dírami: `world.map` je `done`, ale vrstva uzlů surovin nikde není; `entity.player`
je `done`, ale `move()` a inventář neexistují. **Kontrola, kterou je potřeba
dělat před stavbou na cizí granuli:** najdi v `main` její soubor a **zavolej**
to, co od ní voláš. *(Nástroj: `_analyza\over-main-po-merge.py` — porovnává
bloby v `main` s měřenými soubory.)*

### 3.3 Brána, která nemá jak selhat, není brána

Tři naměřené podoby téhož (všechny na `uo-shadows`):

| Podoba | Příklad |
|---|---|
| ptá se na **přítomnost**, ne na chování | `_check(mn.has_method("gather"))` — projde i nad funkcí, která vždy spadne |
| **tiše přeskočí** to, co mělo měřit | `if load("res://scripts/save.gd") != null:` — nenačtený soubor = zelená |
| **zelená nad prázdným seznamem** | `check-schema.py` hledal tvar `var cell := 16`, po migraci nenašel nic → cyklus nad prázdnem → zelená (opraveno 1. 10. 2026) |

**Pravidlo:** u každé brány se ptej **„proběhla?“**, ne jen **„neprotestovala?“** —
a když soubor, který součástí hry být MÁ, chybí, musí to být **selhání**.

### 3.4 Podmíněný test je tiše zelený

`if main.has_method("component"):` … `if player.has_method("move"):` — kontrola se
**nikdy nezapne**, dokud funkce neexistuje, a nikdo se to nedozví. Naměřeno:
`run_tests.gd` měl takto podmíněné kontroly u `save/hud/mining` — a byly zelené
i nad vadnými soubory. **Řešení:** pro soubory, které už existovat mají, podmínku
odstraň a testuj natvrdo; pro ty, které teprve vzniknou, veď „čeká se“ jako
**viditelný** stav (např. `_check(true, "… zatím není – granule není hotová")`),
ne jako ticho.

### 3.5 Checklist při přebírání PR od agenta

1. **Přečti diff** a hledej API, která v projektu neexistují (`margin_*`,
   `node.has()`, `has_property()`, `/root/…`, cizí jména skupin).
2. **Spusť to.** Godot umí `--headless --script`; postav zkušební kostru
   s registrem komponent (`_analyza\fixcheck\test.gd` je hotový vzor).
3. **Vrať do kódu vadu** a podívej se, že test spadne (mutační test).
4. **Ověř v `main`**, že je to, co jsi měřil — bajt po bajtu (`git show` →
   hash), a **ne** podle zelené CI.
5. Teprve pak sloučit — a **zapsat do roadmapy `done_note`** s datem a číslem PR.

---

## 4. Šest naměřených případů (2. 10. 2026, `uo-shadows`)

### 4.1 Tři PR prošla zeleným CI (viz §1)
`39 kontrol, 0 selhání` nad kódem, který se v `_ready()` rozbil. Log běhů #89/#90.

### 4.2 Dvě granule `done` bez práce v repu
- `world.map` („PR #21 sloučené 30. 9.“): `scripts/world.gd` **přesunut** do
  `_retired/world.gd` (`c651368`, záměrně — druhé číslo mřížky). S ním ale
  zmizela i vrstva uzlů surovin (`resources`, `gather()`, `RESPAWN_TIME`,
  `_respawn_resource()`), a `level.gd` ji nemá. `mining.gd` tedy nemá komu říct
  „uzel je vytěžený“ a `save.gd` nemůže uložit stav světa.
- `entity.player` („PR #25 sloučené 1. 10.“): PR změnil **jen `project.godot`**
  (+4 řádky). `git log --all -S"func move"` je **prázdný** — API nikdy neexistovalo.

### 4.3 Kontrakt bez tvaru dat → agent si vymyslel rozhraní
`mining.gd` čte z uzlu `resource_id`, `difficulty`, `cell`. To není v žádném
designovém dokumentu — plyne to jen z kódu jednoho agenta. **Mapa navíc nemá
markery surovin:** `assets/levels/main.json` obsahuje markery
`spawn, coin, coin, exit` — **nula** surovin. Granule „uzly surovin“ se tedy
nedala vydat, dokud se nerozhodlo, **odkud uzly jsou** (mapa vs. procedurálně).

### 4.4 Zadání granule odkazovalo na API, které už neexistuje
`engine.shell` měl v zadání `world.iso_position` — to bylo API přesunutého
`world.gd`. Izometrie je dnes v `level.gd` (`cell_center`, `cell_at`).
**Zadání granule je dokument** a musí se udržovat stejně jako design.

### 4.5 `acceptance` se v designu nevyskytuje
V `docs/DESIGN.md` (3 962 B, sám se hlásí jako *historický* a *zmrazený*)
i v `docs/ARCHITEKTURA.md` (15 848 B) je počet výskytů slova `acceptance` **0**.
Přitom roadmapa ho používá u každé granule. **Přijímací kritérium je přitom to
jediné, co brání „hotovo na papíře“.**

### 4.6 Měření, které odpovídá na jinou otázku
- `git log --diff-filter=D` hlásí i **přesuny** → `world.gd` se tvářil jako
  smazaný (autorita je `git show --stat` s `-M`).
- `grep` tool z rodičovské složky **tiše přeskočí skryté složky** — nad
  `orchestra/` vrátil 0 absolutních cest, Python walk jich našel 80.
- `git show | Measure-Object -Line` nedopočítá poslední řádek bez newline
  (166 vs. 182) — autorita je `git cat-file -s`.
**Pravidlo:** když výsledek vypadá jako „nic tam není“, první otázka je
**„proběhlo to měření?“**, ne „je to prázdné“.

---

## 5. UO-Shadows: co v designu chybí (měřeno 2. 10. 2026)

| Vrstva | Stav | Co z toho plyne |
|---|---|---|
| `docs/DESIGN.md` (3 962 B) | **zmrazená historie** — sám se tak označuje („Původní obsah (zmrazený)“, „Plán prací (starý — orchestr ho nepoužívá)“) | Není to zdroj pro granule. Drží jen vizi a vzhled. |
| `docs/ARCHITEKTURA.md` (15 848 B) | živý kontrakt: pilíře, požadavky, schopnosti, tabulka smluv (17 řádků), granule, DAG | **Smlouvy jsou jednořádkové** (`Hráč → move(), inventář, die()`), tvar dat chybí |
| `assets/levels/main.json` | markery: spawn, coin, coin, exit | Chybí deklarace uzlů surovin → svět nemá co těžit |
| `scripts/player.gd` | jen pohyb klávesami + `flash()` | Chybí stav (`hp/mana/target`) i inventář, který jiné komponenty volají |
| `acceptance` v designu | **0×** | „Čím se ověří“ se nevymýšlí z designu |

**Závěr (názor podložený výše):** design UO-Shadows není nedostatečný proto, že by
byl krátký, ale proto, že **popisuje vrstvy, ne smlouvy** — a AI pipeline
potřebuje smlouvy (tvar dat + přijímací kritérium), protože agent nevidí nic
jiného než zadání granule.

### 5.1 Návrh přepisu (pořadí, ne obsah)

1. **Smlouvy s tvarem dat** — u každé komponenty: poskytuje (jméno, signatura,
   typy, kdo volá) / spotřebovává / **co nesmí**.
2. **Datové formáty** — co je v `levels/*.json` (včetně markerů surovin), co
   v `assets/data/*.json`; a **která brána to ověřuje** (`check-schema.py` dnes
   o surovinách neví **nic** — naměřeno: 0 zmínek).
3. **Přijímací kritéria** ke každé schopnosti z §0.3, spustitelná.
4. **Definice hotovo** (soubor v `main` + brána zavolala funkci) — do
   `CONVENTIONS.md`, který agent dostává do kontextu.
5. **Až potom** roadmapa: granule se z ní odvodí, ne naopak.

---

## 6. Co z toho vzniklo 2. 10. 2026 (provedeno)

Tři nové granule v roadmapě hry (`main = aad1c8d`), protože stará id
`world.map` a `entity.player` mají v D1 řádek `done` a chování `roadmapTick` při
rozporu „soubor ne-done / D1 done“ **není naměřené**:

| Granule | Co dodá | Vlastní |
|---|---|---|
| `world.nodes` | uzly surovin + `gather()` + respawn + `snapshot/restore` | `scripts/world.gd`, `assets/levels/main.json` |
| `entity.player.api` | `move()`, stav (`hp/max_hp/mana/max_mana/target`), inventář, `die()` | `scripts/player.gd` |
| `persist.save.state` | inventář hráče a stav uzlů světa v `save.gd` | `scripts/save.gd` |

`engine.shell` dostal obě první do `depends_on` a v zadání opravený odkaz
(`world.iso_position` → `level.cell_center` / `world.is_walkable`).

**Testy:** `tests/run_tests.gd` má místo `has_method` funkční kontroly
(zkušební registr `component(id)`, opravdu se volá `save/load/update/gather`) —
**41 → 59 kontrol**; s vrácenými vadami hlásí **13 selhání** (`exit 13`).

---

## 7. Jak tenhle dokument budovat — POKYN PRO DALŠÍ SESSIONY

**Tohle je zadání, ne přání.** Dokument je **příprava pro celkovou revizi skillu
`game-developer`** a pro **přepis designu UO-Shadows** (§5.1).

1. **Kdo doplňuje:** každá session, která při práci narazí na **naměřenou** vadu
   designu nebo plánování. Přidá oddíl do §4 (případ) a případně upraví §2 nebo §3.
2. **Jak:** soubor + číslo + datum + **čím to bylo naměřeno**. Bez měření to sem
   nepatří (patří to do `OTEVRENA-TEMATA.md` jako otázka).
3. **Co sem NEPATŘÍ:** historie jedné session (to je `HANDOFF.md`), jednorázové
   opravy kódu a konkrétní stav orchestra.
4. **Kdy se z případu stane pravidlo:** když se stejný vzor objeví **dvakrát**
   nezávisle → patří do `AGENTS.md` (trvalá pravidla). Když je to metodika pro
   agentní vývoj → do skillu `game-developer`.
5. **Kdy je dokument zralý k revizi skillu:** až §2 a §3 nebudou potřebovat
   změnu při dalších **dvou** případech (dnes: 6 případů, 1. sezení).
   Pak se skill přepíše tak, aby **odkazoval sem** (dokument zůstává živý, skill
   je stabilní postup).
6. **Přepis designu UO-Shadows:** zadání pro samostatnou session — výstupem je
   nový `docs/ARCHITEKTURA.md` podle §5.1 (smlouvy s tvarem dat + přijímací
   kritéria + datové formáty + definice hotovo). **Nedělat v session, která
   zároveň opravuje kód** (`AGENTS.md`: autor není nezávislý reviewer).
7. **Ověření dokumentu:** po každé editaci spustit `kontrola-diakritiky.py`
   a `over-dokumentaci.py`; odkazy na soubory musí existovat
   (`Test-Path`), jinak je to tvrzení, které nikdo neověří.

---

## 8. Otevřené otázky (k rozhodnutí člověkem)

- **Kolik granul má nést jeden „milník“?** Dnes je v roadmapě 21 granul a `done`
  je 12; nové tři se vydají po jedné. *(názor, ne měření)*
- **Má `check-schema.py` validovat i markery surovin** (že `resource_id` je
  v `materials.json` a marker leží na průchozím poli)? Dnes o surovinách neví nic.
- **Má `CONVENTIONS.md` nést definici hotovo**, nebo stačí design? (Agent ho
  dostává do kontextu jako `--read`, takže je to nejúčinnější místo.)
- **Kdo schvaluje `done`?** Dnes ho zapisuje conductor z běhu; kdyby ho směl
  zapsat jen člověk po kontrole v `main`, zmizela by celá třída §4.2.

---

## 9. Naměřené případy 8. 10. 2026 (P28): PROČ GRANULE SELHÁVAJÍ — a co k tomu potřebuje ZADÁNÍ

> **Odkud čísla (všechno spustitelné):** `_analyza/p28-sonda-granule.mjs`
> (stav fronty a selhaných úloh), `_analyza/p29-sonda-fronta-vs-roadmapa.mjs`
> (osiřelé v cache, kontrakt polí), `_analyza/p29-sonda-selhani.mjs`
> (běhy `agent.yml` z GitHubu), `_analyza/p29-sonda-agenta.mjs` (log kroku agenta).
> **Datum spotřeby:** **8. 10. 2026, 20:0x +02:00**, hra `8fe57ce`. Do hry píše
> **souběžná session**, takže čísla se mají **přeměřit**, ne opsat.

### 9.1 Fronta neselhává na FORMULACI — selhává na KVÓTĚ (a je to měřené)

Poslední **čtyři** běhy agenta (`Forge #240`, `#241`, `#242`, `#243`) skončily
`failure` a **ve všech čtyřech** je v logu:

```
litellm.RateLimitError: RateLimitError: OpenAIException - Tokens per minute
litellm.RateLimitError: RateLimitError: OpenAIException - Request too large for …
```

Workflow to hlásí jako krok „**Agent nic nezměnil** → hlásíme neúspěch“.
**Verdikt je správný, ale důvod leží jinde:** model nedostal odpověď, protože ho
poskytovatel odmítl. Dva různé tvary téhož:

* `Tokens per minute` = **vyčerpaná kvóta za minutu** (TPM),
* `Request too large for …` = **jeden požadavek je větší, než free tier dovolí**
  (aider posílá repo-mapu + obsah dotčených souborů; `scripts/game.gd` má
  naměřeno **12 567 B**).

**A jeden běh měl ROZBITÝ název modelu:** `Model: openai/openai/gpt-oss-120b`
(dvojitý prefix `openai/`) — u běhu, který začínal na `groq`. Není to kosmetika:
jiný řetězec = jiné směrování.

**Druhá měřená mez:** `/failed` vrací **prázdný `log_tail`**, takže orchestra
**neumí říct, proč běh selhal** — důvod je jen v logu Actions. Kdo to řeší, musí
sáhnout po `p29-sonda-selhani.mjs` / `p29-sonda-agenta.mjs`.

### 9.2 Proč na tom zadání ZÁLEŽÍ (i když to není „formulace“)

| Pole granule | Co s ním orchestra dělá | Naměřený důsledek, když chybí / je špatně |
|---|---|---|
| `model` | vybere **poskytovatele**; `strong` zužuje na `mistral, cerebras, groq` | **10 z 21** granul `strong` → perou se o **tutéž free kvótu**; **11 z 21** `model` nemá |
| `size_lines` | gate auto-merge: změna nad deklarovaný limit se **zamítne** (výchozí **60**) | **6 z 21** ho nemá (`data.content`, `core.attributes`, `core.skills`, `entity.item`, `sim.economy`, `sim.assist`) → větší změna = zamítnutý PR |
| `owns` | vlastněné soubory; dva vlastníci téhož souboru = **sériově** | `scripts/player.gd` i `scripts/save.gd` mají **2 vlastníky** (lint: problém **[3]**) |
| `depends_on` | kdy smí granule běžet | `done: true` je **nespolehlivé** (H105) → viz §3.2 |
| `acceptance` | co se ověří | **0 z 21** chybí — tohle je v pořádku |
| `prompt` | text pro agenta | jeho délka + velikost dotčeného souboru rozhoduje o `Request too large` |

**První pravidlo pro architekta:** velikost granule **není jen „kolik řádků“**,
ale **kolik kontextu si agent přečte**. Granule, která má přepsat 12kB soubor,
selže na free tieru **bez ohledu na to, jak je napsaná**.

### 9.3 VÝMĚNA ROADMAPY JE OPERACE — a nesmí nechat sirotky

Naměřeno po přepisu roadmapy hry: soubor má **21 granul**, ale **cache D1 má
25 řádků** → **5 osiřelých** (`entity.enemy`, `entity.npc`, `entity.player.api`,
`tests.harness`, `world.map`). Fronta drží **44 blokovaných úloh** a jednu
**`failed` s 5 pokusy** (`entity.npc`) — tedy práci na granulích, **které
v roadmapě už nejsou**.

Důsledek je vidět v branách orchestra: `validate-all` hlásí
`cache neobsahuje osiřelé řádky — osiřelé=5` a `cache není větší než soubor`;
`g3` kvůli tomu končí **nedeklarovaným nenulovým exitem**. Nikdo nic neporušil —
**chyběla procedura**.

**Procedura při výměně roadmapy (dělej ji jako krok, ne mimochodem):**
1. **Před** přepisem: `node _analyza\p29-sonda-fronta-vs-roadmapa.mjs` → vypíše osiřelé.
2. Granule, které končí, **ukončit explicitně** — přesunout do `_retired/`
   (ne smazat) a doběhnout/odblokovat jejich úlohy (`/tasks/cleanup`, `/roadmap/reset`).
3. **Po** přepisu: sonda znovu → **osiřelé musí být 0** a `validate-all` zelený.
4. Nové `done: true` **jen s prací v `main`** (§3.2) — jinak vznikne „hotová“
   granule, na kterou čekají ostatní.

### 9.4 Checklist pro zadání granule (zkopíruj a vyplň)

```yaml
- id: engine.input                 # jednoznačné, bez diakritiky
  title: "Vstup — záměr pohybu z myši a kláves (M1)"
  kind: code                       # code | assets | docs | test
  model: strong                    # strong = free „silné“ (mistral/cerebras/groq)
  size_lines: "<= 80"              # ⚠ VŽDY; bez něj platí 60 a větší změna se zamítne
  owns: ["scripts/input.gd"]       # ⚠ JEDEN vlastník na soubor
  depends_on: ["engine.registry"]  # jen na HOTOVÉ a FUNGUJÍCÍ
  acceptance: ["tests", "wiring"]  # co se má ověřit (jména testů)
  prompt: |
    Vytvoř/uprav scripts/input.gd — POUZE vzorkuje vstup a vrací ZÁMĚR pohybu
    (nerozhoduje o pozici, neplní frontu příkazů — dva pisatele = kolize).
    CO JE TAM TEĎ: <...>            # ⚠ bez toho agent nic nezmění a běh selže
    ROZHRANÍ: <přesné názvy funkcí a návratové typy>
    HOTOVO ZNAMENÁ: <test, který to ověří>
```

**Anti-vzory (každý má naměřený důsledek):**

* **„Vytvoř X“, když X už existuje a je hotové** → agent nemá co měnit →
  „agent nic nezmění“ = `failure`, i když je kód v pořádku. Naměřeno:
  `engine.shell` vlastní `scripts/game.gd`, které **existuje**.
* **Obří prompt + celý velký soubor** → `Request too large` (free tier).
* **Všechny granule `model: strong`** → vyčerpají TPM jednoho poskytovatele;
  u malých granul `model` **vůbec nedávej** (výchozí řetězec je širší).
* **Chybějící `size_lines` u velké granule** → PR se zamítne pravidlem 60.
* **Dvě granule vlastnící týž soubor** → pojedou sériově (lint **[3]**).
* **Výměna roadmapy bez ukončení granul** → osiřelé v cache, blokované úlohy
  a červené brány orchestra (§9.3).

**Kontrola před předáním orchestra (spustitelné):**

```powershell
python tools\lint-roadmapa.py E:\Workspaces\uo-shadows   # blokující + poradní nálezy
node _analyza\p29-sonda-fronta-vs-roadmapa.mjs            # osiřelé v cache + kontrakt polí
node _analyza\p28-sonda-granule.mjs                       # co je ve frontě a proč selhalo
```


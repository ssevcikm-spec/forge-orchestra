# Plán rozvoje orchestra pro provoz s AI agenty — NÁVRH K REVIZI

> **Co tenhle dokument JE:** plán. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 1. 10. 2026 · **Stav:** 🟡 **NÁVRH — neschváleno, neimplementováno**
**Navazuje na:** `PLAN-ROZVOJ-ORCHESTRA.md` (F0–F5, architektura a kontrakt) —
**tenhle dokument ho neruší, ale doplňuje o osu, kterou tam vědomě nebylo.**
**Vzniklo z:** vlastního měření (1. 10. 2026), `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`,
tří auditů (zdroje, paralelizace, vazby na okolí) a **živého dotazu na conductora**.

> **Jak tenhle dokument číst.** Uživatelovo podezření bylo: *„orchestra je
> naplánovaná a funkční, ale nezohledňuje, že je čistě automatická s AI agenty
> namísto týmu vývojářů."* **Podezření je správné a je doložené** — §2 ukazuje
> konkrétní místa. Zároveň platí, že **paralelizace už postavená je** (§3) a že
> systém **není funkční z jiného důvodu** (§1), který se musí opravit první.
>
> Každá kapitola má **„K rozhodnutí"** — otázku pro uživatele, ne pro agenta.

---

## 0. Shrnutí pro netrpělivé

| Otázka | Odpověď |
|---|---|
| Běží orchestra teď? | **Conductor ano, práce ne.** `/health` → `ready: 7, running: 0, games: 1`. Poslední dispatch **01:34**, tedy **7,5 h** před dotazem. |
| Proč nic nevydává? | **`main` hry je ČERVENÝ.** CI #80 na `0519d1a` selhalo na kroku „Kontrola vizuálního schématu": `ModuleNotFoundError: No module named 'PIL'`. Každá nová granule by spadla ve stejném kroku. |
| **Je to nová třída selhání?** | **Ano.** `/health` hlásí `ok: true` a `/failed` je **prázdné**, přesto orchestra 7,5 h nevydala nic. **Zelený conductor nad červeným repem** — analýza tuhle třídu neměla. |
| Je to drahé? | **Ne, je to jedna řádka** — doplnit `pip install pillow` do kroku, který ho potřebuje (§1). |
| Je paralelizace postavená? | **ANO, a víc, než se čekalo** — `MAX_CONCURRENT=5`, `ROADMAP_MAX_PRS=5`, `agent.yml` má concurrency per `run_key` (§3). Brzdí ji **zámek, který neblokuje** a **červené CI**. |
| Je orchestra navržená jako lidský tým? | **Ano, ve třech vrstvách** — a je to naměřené, ne dojem (§2). |
| Můžeme zapojit lokální model? | **Ano, ale nejsilnější přínos není inference** — je to **generování assetů** (Blender, ComfyUI). Lokální LLM je na tuhle práci moc slabý a moc drahý na čas (§4.2). |
| Můžeme zapojit telefon? | **Ne jako LLM uzel** — měření to diskvalifikuje (§4.3). Jako **extrakční/embedding sidecar** ano. |
| Má cenu plánovat dokoupený hardware? | **Ano, a je to největší dostupná páka** — ale je to volba *druhu práce*, ne *zrychlení stávající* (§4.4). |
| Co dělat PRVNÍ? | **F0 zelený `main`** (§7, krok N0). Bez něj nemá zbytek co měřit — a to je přesně past, na kterou upozorňoval už `PLAN-ROZVOJ-ORCHESTRA.md` ve F0. |

---

## 1. Živý stav — co analýza nemohla vědět

`ANALYZA-ARCHITEKTURY-ORCHESTRA.md` §6 bod 6 přiznává: *„Nedotazoval jsem se
conductora… stav fronty ani živé D1 tedy neznám."* Tady je doplněno.

| Co | Hodnota | Odkud |
|---|---|---|
| `/health` | `ready: 7`, `running: 0`, `games: 1`, `ok: true` | `GET /health`, 1. 10. 09:09 UTC |
| Registry her | 1 hra (`uo-shadows`, `active: 1`) | `GET /games` |
| Fronta selhání | **prázdná** | `GET /failed` |
| Poslední dispatch | **`2026-10-01 01:34`** (úlohy 135, 136, 137 — tři naráz) | `GET /status` |
| Výsledek | všechny tři **`failure`**, každá do 2 minut | tamtéž |
| Nezralé granule | `persist.save`, `sim.assist` — `updated_at = 01:36`, `attempts: 0` | `GET /roadmap` |
| Domácí uzel | `pc-domaci` naposledy **29. 9. 20:03** (2226 min ≈ 37 h) → **off** | `/health` |
| Cloudový uzel | `oracle-frankfurt` — `minutes_ago: 0` → **žije** | `/health` |

### 1.1 Kořenová příčina — a je triviální

`main` hry (`0519d1a`) má **červené CI**. Z logu běhu #80:

```
Run python3 .forge/check-schema.py .
Traceback (most recent call last):
  File ".../.forge/check-schema.py", line 386, in zkontroluj
    from PIL import Image  # lokální import: bez spritů není potřeba
ModuleNotFoundError: No module named 'PIL'
##[error]Process completed with exit code 1.
```

Proč to nastalo (všechno ověřeno v souborech):

| # | Fakt | Soubor |
|---|---|---|
| 1 | `check-schema.py` importuje `PIL` uvnitř `zkontroluj()` — **jen když existují sprity a `role`** | `.forge/check-schema.py:385-386` |
| 2 | U `uo-shadows` sprity **jsou** → import se provede vždy | `assets/sprites/` |
| 3 | `ci.yml` instaluje `pillow` ve **dvou** krocích — u assetů a u renderu | `ci.yml:70`, `ci.yml:119` |
| 4 | **V kroku „Kontrola vizuálního schématu" (`:53`) ho neinstaluje** | `ci.yml:48-53` |
| 5 | Ten krok je **první brána celého CI** a má `timeout-minutes: 2` | `ci.yml:52` |
| 6 | Selhává i **v šabloně** i ve **hře** (obě kopie stejné) | obě `ci.yml` |

**Oprava:** do kroku na `ci.yml:53` (v **obou** kopiích — šablona i hra) doplnit
`python3 -m pip install --quiet pillow`, stejně jako to mají kroky na `:70`
a `:119`. **Jedna řádka × 2 soubory.**

> **Proč je to poučení, a ne jen oprava:** brána, která si sama nedoveze
> závislost, **vypadá jako vada hry**. Tři granule selhaly za 2 minuty a
> orchestra od té doby mlčí — a nikdo to nepoznal, protože `/failed` je
> **prázdné** (selhaly *běhy*, ne *úlohy*) a `/health` hlásí `ok: true`.
> To je **nová třída tichého selhání**, kterou analýza neměla: **zelený
> conductor nad červeným repem.**

### 1.2 Druhá tichá vrstva: `attempts: 0` a 7,5 h klidu

`persist.save` a `sim.assist` mají `attempts: 0` a čekají od 01:36. Podle
invariantu 15 (cooldown 3 h) se měly vydat ~04:36 — **nevydaly se**, protože
`main` je červený a každý pokus by spadl ve stejném kroku.

**Co z toho plyne pro plán:** dokud je `main` červený, **každé měření
paralelizace měří rozbitý systém** a bude vypadat, že orchestra „nic nedělá".
Proto je N0 (§7) předpokladem všeho ostatního.

### 1.3 Třetí tichá vrstva: tři granule selhaly a `/failed` je prázdné

V 01:34 conductor vydal **tři úlohy naráz** (135, 136, 137) — paralelizace
tedy **funguje**. Všechny tři selhaly do 2 minut. Přesto:

| Endpoint | Co hlásí | Co to znamená |
|---|---|---|
| `/failed` | `{"tasks": []}` | **Nic neselhalo** — protože selhaly *běhy*, ne *úlohy* |
| `/health` | `ok: true`, `ready: 7` | **Vše je v pořádku** |
| realita | 7 granul čeká 7,5 h, `main` je červený | |

**Tohle je nová třída tichého selhání a je systematičtější, než vypadá:**
orchestra má tři různá místa, kde se dá zjistit, že něco nefunguje — a **ani
jedno z nich nemluví o stavu repa, na kterém pracuje.** Conductor je zelený,
protože *jeho* vlastní stav je v pořádku; že cílová hra má červené CI, se
nikde neprojeví. Proto je N0.3 v plánu **brána, ne kosmetika**.

---

## 2. Je orchestra navržená jako tým vývojářů? — ANO, naměřeno

Podezření je správné. Není to ale jeden problém, jsou to **tři různé vrstvy**
a každá se řeší jinak. Rozdíl je důležitý: **jedna je neškodná, jedna je drahá
a jedna je mrtvá.**

### 2.1 Vrstva A — systém sám oslovuje člověka (neškodné, ale je to „mrtvý muž")

Tohle je nejčistší důkaz, protože to nejsou komentáře — to je **kód, který
někomu říká, co má udělat**, a ten někdo neexistuje:

| Kde | Co říká | Problém |
|---|---|---|
| `index.ts:408-410` | `"\n(čeká na tvé sloučení – nesplnilo pravidla)"` | Notifikace oslovuje člověka, který PR nesloučí |
| `index.ts:537-547` | `čeká se na kontrolu ${open} otevřených PR (limit ${maxPrs})` | **Jediná věc, která dnes reálně omezuje počet vydaných granul** — a je to limit na člověka |
| `index.ts:420-423` | „…jen po jedné položce a jen **dokud uživatel nezkontroluje** otevřené PR" | |
| `agent.yml:673-681` | krok *„Když pravidla neprošla – nechá se k ruční kontrole"* + „**Podívej se na ni prosím ručně.**" | |
| `agent.yml:543-545` | PR body: „**Co zkontrolovat před mergem:** … Agent pracoval bez dohledu" | Nikdo ho nečte; agent ho **platí tokeny** |
| `worker.mjs:84-87` | `shell:` se **vždy zeptá y/N** | Bezobslužný render proto není možný |
| `repo/.forge/roadmap.json:3-14` | „…když nemá nic **od tebe**… conductor počká, **až je zkontroluješ**" | Šablona plánu mluví na uživatele |

**Verdikt:** tahle vrstva **není sama o sobě drahá** — horší je, že **má
následky**: `ROADMAP_MAX_PRS = 5` (§2.2) a nemožnost bezobslužného `shell:`
(§4.3). Opravit se má **následek**, ne text.

> **Ověřeno dvakrát, že v systému NENÍ:** žádný `CODEOWNERS`, žádné
> `gh pr review` / `reviewer` / `assignee` / `approved`, žádná branch protection.
> **Jediný „review" krok v celém systému je deterministické CI — žádný model
> nic nereviewuje.**

### 2.2 Vrstva B — rozhodovací kritéria odvozená od člověka (drahá)

Tohle je ta skutečná daň a je měřitelná:

| Místo | Kritérium | Proč je to pro AI-agenty špatně |
|---|---|---|
| `index.ts:537-547` | `ROADMAP_MAX_PRS = 5`, komentář: *„Nezahrnout uživatele hromadou pull requestů"* | **Uživatel nekontroluje žádný** — bezpečné změny slučují auto-merge. Limit drží kapacitu, kterou nikdo nevyužívá, a **je to jediný reálný strop fronty** |
| `wrangler.toml:32` | `MAX_CONCURRENT = 5` | Není odvozený z ničeho měřeného — je to číslo, které „zní rozumně". U 18granulového DAG to znamená **4 vlny** |
| `agent.yml:560` | „Uživatel většinu pull requestů kontrolovat nebude" | Rozhodnutí je správné, ale je to **náhrada člověka automatem** — a to je třeba doříct |

**Jak to změřit (návrh, ne hotová věc):** místo „kolik PR stíhá člověk" se má
strop odvozovat od **měřené propustnosti** — kolik granul dokončí 1 běh, jak
dlouho běh trvá, kolik jich padá na kvótu. To je **F2.3** z
`PLAN-ROZVOJ-ORCHESTRA.md` (conductor jako testovatelná jednotka); teprve pak
lze strop nastavit na datech. **Dnes to nejde — viz N0.1.**

### 2.3 Vrstva C — mrtvé brány, které se tváří jako živé (nejhorší)

**Nejčistší nález celého auditu.** `baseline.py` je postavený na tom, že
**schválení přijde od člověka** — a nikdo ho nikdy neschválil:

| Fakt | Hodnota | Kde |
|---|---|---|
| Co je LGTM | *„Baseline je ten referenční bod a **schvaluje ho člověk**, ne model."* | `baseline.py:2-6` |
| Výchozí schvalovatel | `--kdo` má default **`"clovek"`** | `baseline.py:527` |
| Schválených položek | **272** | `uo-shadows/.forge/vision/baseline.json` |
| Kdo je „schválil" | **všech 272: `"schvalil": "agent-init"`** + „PŘEVZATO AGENTEM — **čeká na lidskou kontrolu**" | tamtéž |
| Následek | `vision.mjs:339-340` u nich **vypne kontrolu** („Schváleno (LGTM) a nezměněno – kontrola se přeskakuje.") → model se vůbec nevolá | |

**Důsledek:** LGTM je **proces, který čeká na vstup, který nemá přijít** —
a protože je zapsaný jako „čeká", **vypadá to jako rozdělaná práce.** To je
horší než kdyby tam nebyl: budí dojem, že se na to nezapomnělo.

**Druhá mrtvá věc téhož druhu — role ve visionu:**

| Co profil deklaruje | Co kód dělá |
|---|---|
| `vision-profile.json:29-46` deklaruje `"role": "worker"` (deepseek-flash) a `"role": "judge"` (gemini) | `vision.mjs` **`role` nikde nečte** — jediný výskyt `role` je `{ role: 'user', content: … }` na `:246`. `sestavRetez()` z nich udělá **obyčejný fallback řetěz**, ne rozdělení úloh |

**A třetí — verdikt, který nikdo nečte:**

| Fakt | Důsledek |
|---|---|
| `vision.mjs` běží **jen** v `ci.yml:122-151` s `continue-on-error: true`, **nikdy v `agent.yml`** | Agent výstup visionu **nikdy nedostane** |
| Žádný workflow neparsuje `---JSON---` / `v_cache` / `shoda` | Vision je **fire-and-forget zápis do logu** |
| `acceptance` a `provides` z roadmapy **nečte žádný kód** (2 nezávislé grepy) | Plán deklaruje, čím se granule ověřuje — a **žádná brána se z toho neodvozuje** |

> **Tohle je jádro odpovědi na uživatelovu otázku.** Systém nemá „mírně lidský
> design" — má **tři mrtvé brány, které se tváří jako živé**: LGTM, role
> worker/judge a verdikt visionu. Stejný podpis měl i `vision.mjs` před
> zapojením (nález 1 v `FORGE-ORCHESTRA-MOZNOSTI.md`: hotový kód, který nikdo
> nevolal). **Vzor se opakuje — a to je ta pravá diagnóza.**

**Co s tím (tři možnosti, k rozhodnutí):**

| # | Možnost | Kdy má smysl |
|---|---|---|
| C-a | **Zrušit LGTM** a `baseline.py` postavit na „schváleno při prvním zeleném průchodu branami" | Když vizuální soud nemá dělat nikdo |
| C-b | **Nahradit člověka nezávislým modelem** — druhý model dostane dva obrázky a řekne, který je schválený stav; neshoda → eskalace | Když chceme vizuální soud, ale ne člověka |
| C-c | **Nechat jako vědomě ruční bránu** a zapsat to tak, aby to nevypadalo jako fronta | Když chce uživatel vzhled opravdu schvalovat sám |

**Návrh agenta: C-b — ale až po N3.5.** Dnes **není změřeno, jak přesná vision
je** (analýza to přiznává, §6 bod 8), a postavit na nezměřené metrice bránu,
která má něco blokovat, je přesně ta chyba, kterou `AGENTS.md` zakazuje.
**Do té doby se má LGTM pojmenovat jako mrtvá brána** — ne tiše nechat.

### 2.4 Systematický nález: `acceptance` existuje, ale nic ho nečte

Tohle přesahuje LGTM a je to **obecná vada kontraktu**:

| Co roadmapa deklaruje | Kdo to čte |
|---|---|
| `acceptance: ["tests", "wiring", "assets"]` | **nikdo** (grep nad `orchestra/repo/.forge/` → 0 výskytů) |
| `provides` (smlouvy) | **nikdo** (tamtéž 0) |
| `role`, `judge`, `worker` ve vision profilu | **nikdo** |

`game-developer` skill staví metodiku na tom, že **`acceptance` je „jak se
pozná hotovo"** a `provides` je smlouva, ze které se generuje zadání. Kód
orchestra **obojí ignoruje** — takže plán a provedení se mohou rozejít, aniž by
to cokoli zachytilo. **To je vada kontraktu, ne dokumentace** a patří do F3
(`PLAN-ROZVOJ-ORCHESTRA.md`).

---

## 3. Paralelizace — postavená, ale zablokovaná

Uživatelův předpoklad byl *„zkusit, jestli je paralelizace možná"*.
**Odpověď: je nejen možná, je implementovaná.** A to je dobrá i zlá zpráva.

### 3.1 Co už existuje (vše ověřeno v kódu)

| Vrstva | Co je hotové | Soubor |
|---|---|---|
| Conductor | dispatch **smyčka**, dokud je kapacita a je připravená úloha s volnými `owns` | `index.ts:761-808` |
| Conductor | `MAX_CONCURRENT = "5"` | `wrangler.toml:32` |
| Conductor | `ROADMAP_MAX_PRS = "5"` | `wrangler.toml:43` |
| GitHub Actions | concurrency **per běh** (`forge-agent-${{ inputs.run_key }}`), `cancel-in-progress: false` — komentář výslovně říká, že dřív společná skupina paralelní dispatch **sama rušila** | `agent.yml:58-64` |
| Roadmapa | `owns` + `depends_on` → DAG; granule jedné vlny mají disjunktní `owns` | `game-developer` skill, §5 |
| Models | rotace podle `run_key`, `attempt` posouvá pořadí | `pick-provider.mjs` |

**Měřeno živě:** v 01:34 conductor vydal **tři úlohy naráz** (135, 136, 137).
Paralelizace tedy **reálně běží** — jen ty tři spadly na `PIL`.

### 3.2 Co ji brzdí — tři věci

| # | Blokátor | Dopad | Oprava |
|---|---|---|---|
| **P1** | **Zámek souborů neblokuje nic** (invariant 17): `:774-776` staví `locked` z **holých jmen**, `:806` porovnává s klíči `{repo}/{soubor}` (`lockKeys`, `:308`) | **Dnes bez následku** (roadmapa nemá kolizi `owns`), ale **paralelizaci to činí nebezpečnou** — jakmile se `owns` potkají, dva agenti si přepíšou soubor a nebude to vidět | `locked.add(k)` z `lockKeys` — **L13** analýzy, jeden řádek |
| **P2** | `ROADMAP_MAX_PRS = 5` zdůvodněné kapacitou člověka | Strop, který není odvozený z měření | Odvodit z `attempts`/trvání běhů; doladit po F2.3 |
| **P3** | **Červené `main`** | Každý paralelní běh spadne na `PIL` | §1.1 |

> **Pořadí je závazné: P1 před zvýšením paralelismu.** Zvýšit počet souběžných
> běhů nad rozbitý zámek znamená **vyrábět závody o soubory** — a ty se
> v auto-merge projeví jako „PR, který přepsal cizí práci". To je dražší chyba
> než pomalý běh.

### 3.3 Může víc API klíčů znamenat víc paralelismu?

**Částečně — a je tu past, která se nevidí.**

| Úroveň | Platí rotace? | Proč |
|---|---|---|
| **Agenti orchestra** (v GitHub Actions) | **ANO** | Každé volání LLM jde z runneru herního repa. **Klíče jsou per-repo** (invariant 3). Paralelní běhy **různých granulí** používají klíče nezávisle — `pick-provider` volí podle `run_key`, takže se rovnají šanci. **Tohle je jediné místo, kde rotace dává smysl.** |
| **Agent v DSH** (tahle session) | **NE — a je to změřené** | `README.md` (root) dokumentuje, proč byl router vyřazen: **přepnutí providera bourá prompt cache** a cache-hit je 25–50× zlevnění. Naměřeno: **~98 % cache-hit** → efektivní vstup ~4,6 % plné ceny. Rotace by ten zisk zničila. |

**Past:** obě rozhodnutí jsou **správná pro svůj kontext** a bydlí ve stejném
workspace — proto si je agent přečte obě a vzniká dojem, že si odporují.
Rozbor a plán řešení: `PLAN-SEPARACE-WORKSPACE.md` §2.3.

**Odpověď na „můžeme použít různé klíče paralelně":**
- **Pro orchestra (hry): ano, a už to dělá.** Víc klíčů = víc paralelních granulí
  bez vyčerpání kvóty. Ale pozor: **denní limit je per klíč** — víc klíčů
  kapacitu **nezdvojnásobí**, jen ji **rozdělí** mezi běhy. To už správně
  upozorňuje `PLAN-ROZVOJ-ORCHESTRA.md` §F5.
- **Pro DSH session: ne.** Rotace modelů uprostřed session je ekonomicky
  sebevražedná (bourá cache). Slabší model se má použít **na začátku úlohy**
  (delegace), ne **uprostřed** (rotace).

### 3.4 K rozhodnutí (paralelizace)

| # | Otázka | Návrh agenta |
|---|---|---|
| **A1** | Zvýšit `MAX_CONCURRENT` / `ROADMAP_MAX_PRS` nad 5? | **Ne dřív než po P1 a po F2.3.** Nejdřív měřit, kolik granul reálně dokončí 1 běh |
| **A2** | Smí se granule stejné vlny dotknout stejného souboru? | **Ne** — `owns` zůstává výlučné. Opravit zámek, ne pravidlo |
| **A3** | Má být strop per-hra (sloupec v tabulce `games`)? | **Ano** — už to navrhuje F5.2; dnes je globální |

---

## 4. Výpočetní zdroje — co reálně jde zapojit

Tohle je odpověď na *„lokální slabý model, model z telefonu, budoucí hardware"*.
**Naměřeno auditem zdrojů** (1. 10. 2026).

### 4.1 Co stanice je

| Co | Hodnota | Poznámka |
|---|---|---|
| CPU | AMD Ryzen 5 2600, 6C/12T @ 3,4 GHz | |
| GPU | **AMD Radeon RX 6600, 8 GB VRAM** (`gfx1032`) | Registry tvrdí 4 GiB — **lže** (WMI 32-bit zkrácení); torch hlásí 8176 MB |
| RAM | ~16 GB | dnes volných ~4,4 GB |
| Disky | C: 139 GB free, D: 174 GB, **E: 813 GB**, F: 2,3 TB free | |
| Ollama | `deepseek-local` = **DeepSeek-R1-0528-Qwen3-8B Q4_K_M** (5,03 GB), `qwen3:14b` (9,28 GB — **nevejde se do VRAM**) | server dnes **neběží** |
| ComfyUI + SDXL | `D:\ComfyUI` — **Juggernaut-XL v9** (6,62 GB) | 512² ≈ **31 s**, 1024² ≈ **138 s**; VRAM **sdílená s Ollamou** |
| Blender 5.2.1 | `C:\Program Files\Blender Foundation\Blender 5.2\` | headless, ověřeno |

### 4.2 Lokální model jako LLM pro orchestra — **nedoporučuji**

| | Hodnota | Důsledek |
|---|---|---|
| Nejsilnější reálně provozovatelný model | **8B Q4_K_M** | Na 8 GB VRAM je to strop (26B nepojede) |
| Propustnost | **~37 tok/s** (100 % GPU); při přetečení na CPU **~6 tok/s** | |
| Kontext | **8192 tokenů** = strop, ne volba | Víc = přetečení VRAM = řádové zpomalení |
| Latence u reasoning modelu | ~3000 tokenů uvažování ≈ **80 s**, než začne jednat | Bezobslužný agent na tom nestojí |
| Náklady orchestry za model | **0** (free tiery) | Lokální model **neušetří peníze** |

**Verdikt:** orchestra dnes platí za modely **nulu** a její úzké místo je
**kvalita a kvóta**, ne cena. Vyměnit free cloudový model za 8B lokální by
znamenalo **vyměnit nulu za nulu** a přidat 80s latenci, 8k kontext a závislost
na tom, že je PC zapnuté. **To je zhoršení, ne zlepšení.**

**Kde lokální LLM smysl MÁ** (a je to jinde, než se čekalo):

| Použití | Proč to jde |
|---|---|
| **Extrakce a klasifikace** — „vytáhni z PR diffu seznam změněných souborů", „zařaď selhání do kategorie" | Malý výstup, velký vstup, dá se dávkovat, nevadí latence |
| **Kontrola konzistence** — „říká tenhle soubor totéž co spec?" | Deterministické, ověřitelné, nezávislé na kvótě |
| **Lokální běh agenta v DSH** (ne orchestra) | Už je zapojený jako `deepseek-local`; hodí se na úlohy, kde **nevadí čas** a vadí **kvóta** |

> **Pozor na nesplněný předpoklad:** `qwen3:14b` je stažený, ale **do 8 GB VRAM
> se nevejde** → poběží ~8 tok/s. Kdo ho použije, bude čekat 4× dýl, než čekal.

### 4.3 Domácí uzel — hotový kód, nula vykonané práce

**Tohle je největší „mrtvá investice" v celém projektu** a je to nejlepší
kandidát na oživení:

| Fakt | Hodnota |
|---|---|
| Kód | `worker.mjs` (415 řádků) — **hotový a funkční**: heartbeat → claim → kroky → report |
| Design | **pull**, ne push — obchází riziko self-hosted runneru (ten na veřejném repu může přes fork PR spustit cizí kód) |
| Vykonaná práce | **NULA.** `forge\logs\` má jen `tools.log` a `have.log`; `forge\work\` je prázdný |
| Naposledy živý | **29. 9. 20:03** (37 h) — potvrzeno i `/health` |
| Chybí pro Blender | krok `blender:` neexistuje; `shell:` se **vždy ptá y/N** → bezobslužný render nejde |
| Chybí pro obrázky | krok `img:` neexistuje |
| Mrtvé | default `FORGE_CMD` → smazaný `forge.cmd`; `kinds` v `.env` je naplněn, ale **`kind` v orchestra nic neřídí** |

**Bezpečnostní fakt, který se musí rozhodnout vědomě:**
`shell:` je libovolný příkaz a **kdo zná `FORGE_SECRET`, má RCE na této stanici.**
Whitelist `FORGE_KINDS` + `--no-shell` + `FORGE_WINDOW` je minimum, ne volba.

### 4.4 Telefon — jako LLM uzel ne

Naměřeno v `research\redmi-note8-server-2026.md`:

| Limit | Důsledek |
|---|---|
| Snapdragon 665 — **chybí `dotprod`, `fp16` i `i8mm`** | llama.cpp jede jen baseline NEON |
| Adreno 610 — **žádný GPU/NPU offload** (llama.cpp OpenCL začíná na Adreno 750) | Vše na CPU |
| **Tokeny/s pro SD665 nejsou naměřené** — jen odhady (~6–10 t/s pro 0.5B, 1–2 t/s pro 3B, chybová lišta ~1,6×) | Nelze na tom stavět plán |
| 3B se do 4 GB RAM „vejde na hraně nebo za ní" | |
| Termux na Androidu 12+ **zabíjí procesy** (signal 9); bez rootu žádný docker/systemd | |
| Trvale na 100 % + teplo = **doložená degradace baterie** | |

**Kde telefon použitelný JE:** extrakční/embedding sidecar (0.5–1.5B), LAN cache
a artefaktový uzel, `sshd` na 8022, ntfy, Tailscale. **A to je cenné** — orchestra
už pro něj má napsaný `termux-setup.sh` (114 řádků, čeká na `.env`).

> **Pozor:** self-hosted runner na **veřejný** repo je dokumentovaný
> anti-pattern. Kdyby telefon měl být runner, jen na **privátní** repo.

### 4.5 Dokoupený hardware — největší páka, ale ne na zrychlení

Aby to nebylo doporučení „kup si GPU":

| Co by přineslo | Přínos | Proč to není zrychlení orchestry |
|---|---|---|
| **Víc VRAM (16–24 GB)** | `qwen3:14b` na 100 % GPU; SDXL 1024² bez tlak na VRAM; Ollama a ComfyUI **současně** | Orchestra dnes za modely platí **0**; zrychlí se **lokální generování assetů**, ne dispatch |
| **Víc RAM** | Větší modely, víc paralelních procesů | |
| **Rychlejší disk / víc místa** | Dnes 1,75 TB free (E+F) — **není problém** | |

**Pravdivé doporučení:** dokoupení hardware zrychlí **tvorbu assetů** (Blender
render, SDXL dávky, 3D → 2D pipeline), což je dnes **ruční a úzké místo**.
Nezrychlí **dispatch ani kvalitu kódu** — tam je úzké místo kvóta a kvalita
free modelů. **Kupovat hardware na zrychlení orchestra by byl omyl.**

### 4.6 K rozhodnutí (zdroje)

| # | Otázka | Návrh agenta |
|---|---|---|
| **B1** | Zapnout uzel `pc-domaci`? | **Ano**, ale nejdřív rozhodnout consent (§4.3). Přínos: Blender a SDXL přestanou být ruční |
| **B2** | Přidat krok `blender:` do `worker.mjs`? | **Ano** — bez něj nejde bezobslužný render (`shell:` se ptá) |
| **B3** | Má lokální LLM vstupovat do orchestra? | **Jen na extrakci/klasifikaci, nikdy jako autor granulí.** Na to je 8B/8k málo |
| **B4** | Telefon jako LLM uzel? | **Ne.** Jako sidecar (extrakce, cache, ntfy) **ano** |
| **B5** | Dokoupit GPU/RAM? | **Ano, pokud je úzké místo tvorba assetů.** Ne jako „zrychlení orchestra" |

---

## 5. Optimalizace komunikace mezi agenty

Klíčové zjištění: **komunikace v orchestra neexistuje** — v tom smyslu, že by
si agenti něco sdělovali. Systém je **stigmergický**: agenti spolu mluví
**přes artefakty v gitu** (patch, PR, roadmapa), ne přes zprávy.

To je **silná stránka** a je potřeba ji nezkazit. Ale má tři konkrétní slabiny:

| # | Slabina | Důkaz | Návrh |
|---|---|---|---|
| **K1** | **Zadání granule je próza v JSONu**, ne strojový kontrakt | `roadmap.json: prompt` je volný text; `lint-roadmapa.py` ho validuje jen na JSON | Zadání **generovat ze schématu** (`owns`, `provides`, `acceptance`), jak to předepisuje `game-developer` §4.5 — *„Ručně psané zadání v próze se rozjíždí (naměřeno)"* |
| **K2** | **Výsledek agenta se čte z logu, ne z artefaktu** | `stahni-patch.mjs` tahá `agent.patch` **proto**, že logy obsahují i shell workflowu; skill `orchestra` to doporučuje jako „jediný spolehlivý zdroj" | Agent má **povinně** zapsat strojový výsledek (JSON) jako artefakt; log je lidská stopa, ne zdroj pravdy |
| **K3** | **PR komentář je pro člověka** | `agent.yml` (šablona PR komentáře) | Zkrátit na strojový souhrn + odkaz; ušetří tokeny **každému** běhu |

**Co je naopak správně a nemá se měnit:** `owns`/`depends_on` jako **strojové**
vyjádření závislosti (ne próza) — to je přesně to, co `game-developer` vznikl
řešit („kaskáda vznikla z toho, že závislost byla schovaná ve větě").

---

## 6. Optimalizace promptování pro AI agenty

### 6.1 Inventura — kde dnes prompt vůbec je

| Zdroj | Co obsahuje | Kdo ho dostane |
|---|---|---|
| `repo/CONVENTIONS.md` | Poučky vzniklých chyb; **§1g** je kritický (`extends Node`, `class_name`, `_init()`) | Agent přes `--read` |
| `agent.yml` (~681 řádků) | Instrukce **inline ve workflow** — jak volat aider, jaké přepínače, co s chybami | Agent nepřímo (přes příkazy) |
| `roadmap.json: prompt` | Zadání granule v próze | Agent jako `--message` |
| `providers.json` | Modelový řetězec | `pick-provider.mjs` |
| `--map-tokens 0` | Repo-mapa se **vypíná** (~1k tokenů a slabé modely se v ní „snaží editovat") | Rozhodnutí je správné |

**Zjištění:** orchestra **nemá centrální prompt**. Instrukce jsou rozptýlené
mezi `CONVENTIONS.md`, `agent.yml` a `roadmap.json`. To znamená, že
**optimalizovat prompt znamená nejdřív ho najít** — a dnes ho nikdo na jednom
místě nevidí.

### 6.2 Kam patří úsilí (podle měřeného dopadu)

| # | Změna | Proč to má dopad |
|---|---|---|
| **PR1** | **Zadání granule generovat ze schématu**, ne psát v próze | `game-developer` §4.5: ruční próza se rozjíždí. Dnes je `prompt` volný text — a `lint-roadmapa.py` ho **nekontroluje** |
| **PR2** | **`CONVENTIONS.md` rozdělit podle druhu granule** | Dnes dostane agent **všechny** poučky na **každou** granuli. Granule, která vytváří nový soubor, nepotřebuje poučku o `SEARCH/REPLACE` v cizím souboru. **Méně kontextu = lepší výsledek u slabého modelu** |
| **PR3** | **Deklarovat `size_lines` a `model` u každé granule** | Už to jde (`game-developer` §4.1), ale roadmapa to nemá všude → `any`/`<= 60` platí mlčky |
| **PR4** | **Strojový formát výsledku** (viz K2) | Agent dnes hlásí prózou; ověřitelnost je slabá |
| **PR5** | **Prompt pro `kind`** — dnes `kind` nic neřídí (nález 4) | Buď ho zapojit, nebo smazat. **Nechat pole, které nic neřídí, je horší než ho nemít** |

### 6.3 Co se musí změřit, než se podle toho bude řídit

Tohle je varování, ne úkol: **nesmí se stavět na nezměřených metrikách.**

| Metrika | Stav | Jak ji změřit bezpečně |
|---|---|---|
| **Přesnost vision** | **neměřeno** — analýza to přiznává (§6 bod 8) | `vision.mjs` na N vzorcích se známým správným i chybným stavem (vzor: `test-check-schema.py`) |
| **Úspěšnost modelů podle granule** | částečně (`analyza-modelu-pokusu.mjs`) | doplnit o `size_lines` a `kind` |
| **Propustnost 1 běhu** | **neměřeno** | kolik granul za hodinu dokončí 1 dispatch |
| **Náklady na běh** | **neměřeno** (free tiery) | počet volání LLM na běh — **kvóta je to, co se spotřebovává** |

---

## 7. Fáze — co dělat v jakém pořadí

Pořadí je podle **závislostí**. Fáze N jsou **nové**; F0–F5 zůstávají
v `PLAN-ROZVOJ-ORCHESTRA.md` a **neschvalují se znovu**.

```
N0  Zelený main        ← BLOKUJE VŠECHNO (dnes: orchestra nevydá ani granuli)
     ↓
N1  Zámek + strop      ← teprve teď je paralelizace bezpečná
     ↓
N2  Komunikace         ← výsledek jako artefakt, ne log
     ↓
N3  Promptování        ← zadání ze schématu, CONVENTIONS po druzích
     ↓
N4  Uzel pc-domaci     ← lokální výpočet (Blender, SDXL) — volitelné, ale velký přínos
     ↓
N5  Hardware           ← až když N4 ukáže, kde je úzké místo
```

### N0 — Zelený `main` (blokuje všechno)

> **Stav 1. 10. 2026:** **N0.1 je HOTOVÉ, COMMITNUTÉ A PUSHNUTÉ** — CI na `main`
> je **zelené** a orchestra **je zpátky v provozu** (první dispatch po 8,5 h).
> **N0.2 a N0.3 jsou otevřené** a jsou důležitější než N0.1: oprava jedné řádky
> zmizí, ale třída chyby („brána si nedoveze závislost", „conductor neví o stavu
> repa") zůstane.

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N0.1** | Doplnit `python3 -m pip install --quiet pillow` do kroku „Kontrola vizuálního schématu" v `ci.yml` — **v obou kopiích** (šablona i hra) | ✅ **HOTOVO** — hra: commit `7cd14cb` pushnut, CI **success**. Šablona: oprava na disku, **čeká na commit šablony** (viz níž) |
| **N0.2** | Zavést **bránu na závislosti bran**: každá brána, která importuje knihovnu mimo stdlib, ji musí mít v kroku, který ji pouští | Přidání `import X` do brány → CI to ohlásí (dnes: spadne až v produkci) |
| **N0.3** | **Naučit orchestra rozeznat „zelený conductor nad červeným repem"** — stav posledního CI běhu na `main` dát do `/health` | `/health` ukáže `main_ci: failure` (dnes hlásí `ok: true`) |

> **N0.2 a N0.3 jsou důležitější než N0.1.** Oprava jedné řádky zmizí; ale
> **třída chyby „brána si nedoveze závislost" a „conductor lže o stavu repa"
> zůstane.** Tohle je přesně ta práce, kterou má plán dělat — ne jen hasit.

### N1 — Zámek a strop (aby paralelizace byla bezpečná)

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N1.1** | Opravit zámek: `locked.add(k)` z `lockKeys` (`index.ts:774-776`) | ✅ **Hotovo** — ověřeno testem `tools\test-zamek-owns.py` (8/8) i mutačním testem |
| **N1.2** | `lint-roadmapa.py` u kolize `owns` **přestane tvrdit „poběží sériově"** (dnes to není pravda) nebo začne tvrdit pravdu | ✅ **Hotovo zdarma** — po opravě zámku je výrok poprvé pravdivý, text se měnit nemusel |
| **N1.3** | Zdůvodnění `ROADMAP_MAX_PRS` přepsat z „co stíhá uživatel" na měřený důvod | Dokument nepopírá provoz |
| **N1.4** | Zavést per-hra strop (sloupec v `games`) | Dvě hry se navzájem nevyhladoví |

### N2 — Komunikace

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N2.1** | Agent zapisuje výsledek jako **strojový artefakt** (JSON) | `stahni-patch.mjs` přestane být „jediný spolehlivý zdroj" |
| **N2.2** | PR komentář zkrátit na strojový souhrn | Měřitelně méně tokenů na běh |
| **N2.3** | Zdroj pravdy o výsledku = artefakt; log = lidská stopa | Dokumentace to říká |

### N3 — Promptování

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N3.1** | Zadání granule **generovat ze schématu** (PR1) | `prompt` v roadmapě je odvozený, ne psaný |
| **N3.2** | `CONVENTIONS.md` rozdělit podle druhu granule (PR2) | Agent dostane jen relevantní poučky |
| **N3.3** | `size_lines` + `model` **povinné** v roadmapě (PR3) | Validátor to vyžaduje |
| **N3.4** | Rozhodnout `kind` — zapojit, nebo smazat (PR5) | Nikde nezůstane pole, které nic neřídí |
| **N3.5** | Změřit přesnost vision na vzorcích (§6.3) | Je číslo, ne dojem — **teprve pak** má smysl C-b z §2.3 |

### N4 — Lokální uzel (volitelné, ale největší provozní přínos)

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N4.1** | Rozhodnout consent: whitelist `kinds`, `--no-shell`, `FORGE_WINDOW` | Riziko RCE je vědomé rozhodnutí, ne náhoda |
| **N4.2** | Přidat krok `blender:` do `worker.mjs` (s ověřením, že PNG **existuje** — `blender.exe` vrací 0 i s tracebackem) | Bezobslužný render projde |
| **N4.3** | Smazat mrtvý `FORGE_CMD` (míří na smazaný `forge.cmd`) | Krok `forge:` buď funguje, nebo neexistuje |
| **N4.4** | Zapnout uzel a vydat **jednu** úlohu `target: lan` | `forge\logs\` má první log s `run_key` (dnes **nula**) |
| **N4.5** | Teprve potom krok `img:` (SDXL) | Až N4.2 funguje — riziko VRAM je vyšší |

### N5 — Hardware

| Krok | Co | Hotovo znamená |
|---|---|---|
| **N5.1** | Změřit, kde je úzké místo (čas na granuli vs. čas na asset) | Je číslo |
| **N5.2** | Teprve pak rozhodnout o VRAM/RAM | Rozhodnutí stojí na měření |

---

## 8. Co tenhle plán vědomě NEŘEŠÍ

| Věc | Proč ne |
|---|---|
| **F1 (tři vady conductoru: 3h zpoždění, obcházení cooldownu, strop/watchdog)** | Patří do `PLAN-ROZVOJ-ORCHESTRA.md` §F1. **Nezdvojuji to** — ale upozorňuji, že N0 je jeho předpoklad taky |
| **F3/F4 (kontrakt, převzetí souborů)** | Rozpracované tamtéž; **separace workspace je jejich předpoklad** (`PLAN-SEPARACE-WORKSPACE.md` §3) |
| **Separace workspace a její provedení** | Vlastní dokument: `PLAN-SEPARACE-WORKSPACE.md`. **Tenhle plán na ni jen odkazuje**, neopisuje ji — jinak by vznikly dvě verze téhož |
| **Náhodné generování her** | Uživatel: jen když je zdarma a nerozbije kapacitu. **Je zdarma** — viz §9 |
| **Smazat `forge-quest`** | Je to živá hra — zakázáno (`AGENTS.md`) |
| **Push, commit, deploy** | Rozhodnutí uživatele |
| **Přesnost vision** | Měření, ne plán — ale je to **vstup** pro N3.5 a C-b |
| **Tajemství a jejich ACL** (`.secrets` má stejná práva jako workspace) | Není to o orchestra ani o AI-agentech — je to nález o stanici. Zapsáno v `PLAN-SEPARACE-WORKSPACE.md` §2.5 |

---

## 9. Náhodné generování her — proč je zdarma (a proč počká)

Uživatel řekl: *„prozatím se zaměř jen na generování z komplexního design
dokumentu, ledaže by náhodné generování jako možnost bylo zdarma."*

**Je — a je to levnější, než to vypadá.** Důvod je architektonický:

```
        design dokument ──┐
                          ├──► roadmap.json (DAG granulí) ──► conductor ──► agenti
        náhodný generátor ┘
```

**Conductor neví a nemůže vědět, odkud roadmapa přišla.** Čte `.forge/roadmap.json`
z repa hry (`roadmap_file` v tabulce `games`). Náhodné generování je tedy
**jiný producent téhož artefaktu** — nula změn v conductoru, nula změn v branách.

**Co by to reálně znamenalo:**

| Část | Práce |
|---|---|
| Generátor roadmapy | **Nová** — bere design dokument *nebo* semínko a plodí `grains` |
| Conductor | **Nic** |
| Brány | **Nic** |
| Validace | `lint-roadmapa.py` už existuje a kontroluje DAG — **použije se beze změny** |

**Proč to přesto počká:** generovat hru bez design dokumentu znamená generovat
**i smlouvy** (`provides`/`consumes`) — a právě na rozjetých smlouvách
(`game-developer` §2 a §4.5) padá celý zbytek. Náhodný generátor, který vyrobí
18 granul s vymyšleným API, vyrobí **18 spálených pokusů**.

**Návrh:** zařadit jako **N6** (za N3), kdy už bude existovat generátor zadání
ze schématu (N3.1) — pak je to **totéž zařízení s jiným vstupem**, ne nový
systém. Do té doby to je **vědomě odloženo**, ne přehlédnuto.

---

## 10. Můj závěr — co vím, co bych zavedl a čím bych se řídil

Tohle je část, kterou uživatel vyžádal od agenta: *„jestli máš sám znalosti,
specifikace a nápady jak se dál řídit vývojem a jaké nové technologie nebo
postupy zařadit."*

### 10.1 Tři věci, které bych zavedl hned (a nejsou v žádném plánu)

| # | Postup | Proč právě tenhle |
|---|---|---|
| **Z1** | **Každá brána vypíše `ZMERENO: <co>=<počet>`** a `validate-all.mjs` padne, když některá nevykáže měření | Řeší **celou třídu** tichých selhání (S1, S3, S12) naráz. Už to navrhuje F2.1 toho druhého plánu — ale je to **nejdůležitější jednotlivá změna v projektu** a chci ji podpořit explicitně |
| **Z2** | **Kontraktní test mezi dvěma kopiemi jako standard** — dnes to dělá jen `test-check-schema.py` (hlídá shodný hash šablony a hry) | Je to **nejlepší vzor v celé orchestra** (analýza §4.6). Všechno, co existuje dvakrát, musí mít test na **shodu mezi kopiemi**, ne dva testy na každou zvlášť |
| **Z3** | **„Nezměřeno" musí být vidět.** Nikdy `[]`, `0` ani `None` bez pojmenování | `AGENTS.md` to má jako pravidlo; v kódu to není vymahatelné. `ZMERENO:` z Z1 je mechanizmus, jak to vynutit |

### 10.2 Co bych zařadil jako nový postup (a dnes to nikde není)

| # | Postup | Zdroj inspirace |
|---|---|---|
| **P1** | **Fitness funkce holistického typu** — ne „brána měří X", ale „**brána se spustila a kolik toho změřila**" | `PLAN-ROZVOJ-ORCHESTRA.md` §1.1 (Ford/Parsons/Kua) |
| **P2** | **Deklarované vlastnictví souborů** (`zdroj.json` v každé hře, vzor `.cruft.json`) | §1.2 tamtéž |
| **P3** | **Kontraktní testy proti divergenci** — kontroluje se **shoda mezi implementacemi**, ne každá zvlášť | §1.4 tamtéž |
| **P4** | **Zadání generované ze schématu** — prompt není próza, ale derivát kontraktu | `game-developer` §4.5 |
| **P5** | **Strojový artefakt jako zdroj pravdy o výsledku** (ne log) | §5 K2 tohohle dokumentu |
| **P6** | **Test závislostí bran** — brána, která importuje knihovnu, ji musí mít v kroku, který ji pouští | §1.1 tohohle dokumentu (**nové**, z naměřené chyby) |
| **P7** | **„Stav repa" jako součást zdraví orchestra** — conductor musí vědět, že `main` je červený | §1.1 tohohle dokumentu (**nové**) |

### 10.3 Čemu bych se naopak vyhnul

| # | Anti-vzor | Proč |
|---|---|---|
| **A1** | **Vyrobit z orchestra platformu** — registr bran, plugin systém pro enginy, abstrakce nad enginy | Dokud není druhá hra, je to hypotéza. `PLAN-ROZVOJ-ORCHESTRA.md` to má jako hlavní riziko a **souhlasím** |
| **A2** | **Postavit bránu na nezměřené metrice** (např. vision blokuje) | Přesně ta chyba, kterou `AGENTS.md` zakazuje. Nejdřív N3.5 |
| **A3** | **Zvyšovat paralelismus před opravou zámku** | Vyrobí závody o soubory, které auto-merge slije jako „cizí přepis" |
| **A4** | **Vyměnit free model za lokální kvůli ceně** | Cena je **nula** na obou stranách; lokální přidá latenci a ubere kontext |
| **A5** | **Nechat v kódu pole, které nic neřídí** (`kind`, mrtvý `FORGE_CMD`) | Budí důvěru. `AGENTS.md`: *„Nefunkční metriku smazat, ne nechat ležet"* |

### 10.4 Co bych měřil jako první, aby se dalo rozhodovat

| Co | Proč to |
|---|---|
| **Propustnost 1 běhu** (granul/hodina) | Bez toho se `MAX_CONCURRENT` nedá nastavit na datech |
| **Spotřeba kvóty na běh** (volání LLM) | Kvóta je to, co se reálně spotřebovává — ne peníze |
| **Přesnost vision** na vzorcích | Vstup pro rozhodnutí C-b |
| **Rozpad selhání podle druhu** (`analyza-chyb.mjs` + `kind` + `size_lines`) | Ukáže, které granule mají být `strong` a které rozpadnout |
| **Čas na asset vs. čas na granuli** | Rozhodne N5 (hardware) |

---

## 11. K rozhodnutí — souhrn pro revizi

| # | Otázka | Fáze | Návrh agenta |
|---|---|---|---|
| **R1** | Smím opravit `ci.yml` (Pillow) a nechat to ověřit zeleným CI? | N0 | **Ano — to je jedna řádka a odblokuje celý provoz** |
| **R2** | Zavést bránu na závislosti bran (N0.2)? | N0 | **Ano** — oprava jedné řádky zmizí, tahle třída chyb ne |
| **R3** | Má `/health` hlásit stav CI na `main` (N0.3)? | N0 | **Ano** — conductor dnes hlásí `ok: true` nad červeným repem |
| **R4** | Opravit zámek `owns` (N1.1)? | N1 | **Ano, a před jakýmkoli zvýšením paralelismu** |
| **R5** | Zvýšit `MAX_CONCURRENT`/`ROADMAP_MAX_PRS`? | N1 | **Ne dřív než po R4 a po měření propustnosti** |
| **R6** | Má být strop per-hra? | N1 | **Ano** |
| **R7** | Zavést strojový artefakt jako zdroj pravdy o výsledku (N2)? | N2 | **Ano** |
| **R8** | Generovat zadání granule ze schématu (N3.1)? | N3 | **Ano** — dnes je to próza, která se rozjíždí |
| **R9** | Co s `kind` — zapojit, nebo smazat? | N3 | **Zapojit**, jinak smazat. Nechat ležet ne |
| **R10** | Co s LGTM / `_ceka_na_lgtm` u 272 položek? | N3 | **Nahradit nezávislým modelem (C-b), ale až po změření vision.** Do té doby to **pojmenovat jako mrtvou bránu** |
| **R11** | Zapnout `pc-domaci` a rozhodnout consent? | N4 | **Ano** — kód je hotový a má **nula** vykonané práce |
| **R12** | Přidat krok `blender:`? | N4 | **Ano** — bez něj nejde bezobslužný render |
| **R13** | Má lokální LLM vstupovat do orchestra? | — | **Jen na extrakci/klasifikaci.** Ne jako autor |
| **R14** | Dokoupit GPU/RAM? | N5 | **Až po měření** (N5.1). Zrychlí assety, ne orchestra |
| **R15** | Zařadit náhodné generování her? | N6 | **Ano, ale až po N3.1** — do té doby by generovalo rozjeté smlouvy |

---

## 12. Co se změnilo proti návrhu

*(První dvě změny jsou provedené opravy — plán by jinak lhal o stavu.)*

| Datum | Co se změnilo | Proč |
|---|---|---|
| 1. 10. 2026 | **N0.1 hotové, commitnuté a pushnuté** — `pip install --quiet pillow` v obou `ci.yml`. Hra: commit `7cd14cb` → CI **success**. Šablona: na disku, čeká na commit šablony | Naměřeno: `ModuleNotFoundError: No module named 'PIL'` v CI #80; orchestra 7,5 h nevydala ani granuli |
| 1. 10. 2026 | **N1.1 hotové, commitnuté, pushnuté A NASAZENÉ** — zámek `owns` opraven (`conductor/src/index.ts`, commit `6d2a856`), Deploy conductor na `c0edbb0` → **success** | Naměřeno replikou: holá jména vs. klíče `{repo}/{soubor}` se nikdy neprotly |
| 1. 10. 2026 | **N1.2 hotové zdarma** — `lint-roadmapa.py` u kolize `owns` tvrdí „poběží sériově"; **po opravě zámku je to poprvé pravda** | Před opravou to byl nepravdivý výrok; oprava ho spravila, aniž se musel měnit text |
| 1. 10. 2026 | **N0.2 a N0.3 zůstávají otevřené** — brána na závislosti bran a stav CI v `/health` | Oprava jedné řádky zmizí; **třída chyby zůstává.** Proto jsou v plánu i po opravě |
| 1. 10. 2026 | **Nová fáze N6 (návrh): zobecňování do skillů.** Vznikly skill `overovani` (spustitelný sabotér + `zmen.py`) a rozšíření `dsh-usage` o `analyza.mjs` | Vzory ověřování a měření se nemají znovu objevovat; DSH na ně má dosáhnout sám |
| 1. 10. 2026 | **F0.1 dokončeno i pro šablonu** — commit `eac2790` (12 souborů, 2120 insertions); `repo/.forge` má v gitu **21** souborů. Součástí je oprava `release.yml`, který odkazoval na **jinou živou hru** (`forge-quest`) | Naměřeno: klon orchestra z gitu neměl brány a odkaz mířil na cizí hru |
| 1. 10. 2026 | **L5/F0.6 hotové — a byl to skutečný nález.** `install-into-repo.ps1` kopíruje do hry `.env` s reálným `FORGE_SECRET`, ale `.gitignore` hry `.env` **neobsahoval** (`git check-ignore .forge/node/.env` → nic). Opraveno v **třech** místech (generátor, hra, orchestra) + **kontraktní test** `test-gitignore-tajemstvi.py` (15 kontrol, ověřen mutačním testem) | Nález je v analýze jako S7 |
| 1. 10. 2026 | **Nový nález N3: model používá Godot 3 konstanty.** Běh #241 (`ui.hud`) spadl na `Cannot find member "ALIGN_LEFT" in base "Label"` — **`hud.gd` se nikdy nedostal do repa**. `CONVENTIONS.md` ty konstanty neobsahoval vůbec → doplněn **§1h** s tabulkou Godot 3 → 4 | Log běhu #241 |
| 1. 10. 2026 | **Nový nález N4: `echo` ve workflowech se zpětnými apostrofy.** Bash je bere jako substituci, text se pokusí spustit a **utopí skutečnou chybu** (`var: command not found`). Opraveno v obou `agent.yml` + nový `kontrola-echo-substituci.py`, který rozlišuje **vadu** od **záměru** (`$( )`) | Log běhu #241. **Mechanismus NEDOKÁZÁN** — nereprodukoval jsem ho |
| 1. 10. 2026 | **`N0.2` a `N0.3` zůstávají otevřené** — i po opravě Pillow. Třída chyby („brána si nedoveze závislost", „conductor neví o stavu repa") se tím nevyřešila | — |

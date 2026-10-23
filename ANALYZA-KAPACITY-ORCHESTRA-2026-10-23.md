# ANALÝZA — KAPACITA ORCHESTRA: jak daleko dojde od nuly k plně naskinované hře

> **Co tenhle dokument JE:** **analýza (kapacitní mapa)** — co orchestra umí
> dnes, kam dojde VLASTNÍMI silami a co musí dodat stanice (Blender/SDXL) nebo
> člověk (vkus, licence, sehrání). **Není to plán granulí** (ten patří hře
> a píše se z `docs/TDD.md` smluv) **ani záznam o provedení**.
> **Vzniklo:** 23. 10. 2026, session orchestra (pokračování K11b po dokončení
> syncu a M0/M1 dne 19.–20. 10. 2026).
> **Odkud brát stav:** živý conductor (`/health`, `/status`, `/queue`), oba
> repa (`E:\Workspaces\forge-orchestra`, `E:\Workspaces\uo-shadows`), běhy
> GitHub Actions. **Čísla jsou naměřená k 23. 10. 2026**; u starších je datum
> uvedeno („naměřeno 20. 10.“). Co je převzaté z dokumentace, je tak označené.
> **Datum spotřeby:** dokument platí do první z těchto změn: zapojení P2
> (asset-fetch do pipeline), přidání Blenderu do CI, změna `check-assets.py`
> nebo `vision`, nový plán hry (`.forge/roadmap.json`). Po každé z nich se
> musí přeměřit §1 a §3.
> **Co se z něj (zatím) provedlo:** nic — je to podklad k rozhodnutí. Co se
> provede, se dopíše sem (append-only).

---

## 0. Odpověď v pěti řádcích

1. **Z nuly na funkční hru orchestra dojde** — po dodání plánu a testů zvládne
   kód, data, JSON levely a procedurální placeholdery (M0–M5); z 21 připravených
   granulí je 18 kód/data.
2. **Plně naskinovanou hru sama neudělá.** Aider píše jen text a auto-merge
   pustí jen `scripts/` a `assets/`; sprity, zvuk, UI a fonty jsou binárky.
   Blender v cloudu není a vkus nikdo neměří.
3. **Materiál na skin na stanici existuje** (~1 GB free knihovny, Blender 5.2.1,
   SDXL/ComfyUI), ale chybí zapojení (P2) a člověk (LGTM, sehrání).
4. **Hudba je blokovaná zvlášť**: chybí nástroj `forge music` a brána
   `check-assets.py` vyžaduje manifest s měřením melodie; free hudba je navíc
   ruční licence, ne automatický fetch.
5. **Godot a shipování jsou vyřešené** (import, testy, snímek, vision, export
   Windows/Linux/Web, Release + Pages live) — strop je v obsahu a vzhledu,
   ne v enginu.

**Věta pro rozhodování:** „Orchestra je vykonavatel, ne autor vzhledu ani
chuti.“ Co je potřeba k plné hře, je v §4 (P1–P6); co z toho patří uživateli,
je v §6.

---

## 1. Naměřená mapa

### 1.1 Výkonný stroj orchestra

| Co | Naměřeno | Doklad / postup |
|---|---|---|
| Conductor | Cloudflare Worker (free), cron **každou minutu**, 1 440 tiků/den; sám nevolá LLM | `conductor/wrangler.toml` `[triggers] crons`; `PROVOZ-ORCHESTRA.md` |
| Kapacita práce | **`MAX_CONCURRENT=5`** souběžných cloudových úloh, **`ROADMAP_MAX_PRS=5`** otevřených PR | `conductor/wrangler.toml` `[vars]` |
| Stropy pokusů | `MAX_ATTEMPTS=5`, `GRAIN_MAX_RUNS=8`, `ESCALATE_AFTER=3`, `RETRY_HOURS=0.5` (30 min) | `conductor/wrangler.toml` |
| Doba běhu | #559 **1 min**, #560 **4 min** (agent + merge); CI/release ~2–3 min | `node tools/status.mjs` + `/status` (23. 10. 13:24) |
| Posledních 20 běhů | **2 success, 1 failed, 17 failure** — okno 16. 10. se starým workflow; po syncu jen 2 běhy: #274 PARSE fail, #275 success | `GET /status` (23. 10. 13:24 +02:00); podrobně `HANDOFF.md` §77.9–77.10 |
| Fronta | 0 ready, 0 running; 50 historických tasků (`done`/`blocked`); roadmapa **11/11 done** | `GET /health`, `GET /queue`, `GET /roadmap` |
| Modelový řetězec | mistral **625 000 TPM**, cerebras **30 000**, groq **8 000**, openrouter ~50/den, gemini (vision, malá kvóta), deepseek **bez klíče** | `repo/.forge/providers.json` `limits`; `HANDOFF.md` §77.6 |
| Placené | orchestra dnes jede **bez placeného klíče** (DeepSeek secret není; poskytovatel se přeskočí) | CI log #140: `DEEPSEEK_API_KEY:` prázdné |

**Co z toho plyne:** průchodnost neomezuje compute ani peníze, ale **kvalita
zadání a testů** (selhání jsou PARSE/„agent nic nezměnil“, ne kvóta) a lidský
strop 5 otevřených PR. Při 5 paralelních bězích a ~5–15 min na granuli je
teoreticky desítek granulí denně; reálně je brzdí chybovost free modelů
(naměřeno historicky ~10 % úspěšnosti u slabých zadání, `wrangler.toml`
u `MAX_ATTEMPTS`).

### 1.2 Co orchestra umí zapsat — a co ne

| Vrstva | Orchestra (cloud) | Doklad |
|---|---|---|
| Kód GDScript, JSON data, levely, `spec.json`, docs | **ano** (text) | `repo/.forge/files-to-edit.mjs` — aider dostane jen `.gd/.json/.md/.cfg/.tscn/.tres/.godot` |
| Obrázky, zvuk, fonty, modely (binárky) | **ne** — aider píše text; binárku nevyrobí | totéž; `ASSETY-PLAN.md` („fetch nesmí přes LLM“) |
| Testy | **ne** — auto-merge vylučuje `tests/`, `.forge/`, `.github/`, `project.godot` | `repo/.github/workflows/agent.yml` (pravidla auto-merge) |
| Vlastní pipeline (workflow, nástroje) | **ne** — `.forge/` a `.github/` jsou z auto-merge vyloučené | tamtéž |
| Velikost změny | do `max_lines` granule, výchozí **60 řádků**; větší jen s `size_lines` a `model: strong` | `agent.yml`; `repo/.forge/roadmap.json` (formát granule) |

**Důsledek pro kapacitu:** orchestra **nemůže sama sobě vylepšit pipeline ani
napsat test**, který by její práci změřil. Testy a plán musí dodat plánovací
session; orchestra je jen vykoná. To je naměřený důvod, proč M0/M1 skončily
ručním dotažením (H238) a proč PR #39 prošel zeleně s vadou (H240).

### 1.3 Godot: plná podpora v cloudu

Naměřeno v CI #140 (`3e1592b`, 19. 10. 21:24 UTC) a v `release.yml`:

| Krok | Stav |
|---|---|
| Godot 4.7.2 + exportní šablony (1,2 GB) | `install-godot.sh`, cache `~/.cache/forge` |
| Import assetů, `check-schema`, testy, `check-assets`, `check-wiring`, smoke | všechny `success` |
| **Snímek hry** | `xvfb` + softwarové OpenGL, 480×270, 20 framů → `snímek: /tmp/frames/frame00000019.png`; **terén sedí 207/207 = 100,0 %** (`verify-level-render.py`) |
| **Vision** | gemini-3.8-flash, režim `presence`, **dva běhy se neshodly** („verdikt je nejistý, rozhodni lidsky“), krok **neblokuje** |
| Export | Windows/Linux/Web (release i CI), rolling Release + GitHub Pages; **Pages live 200, `last-modified` 19. 10. 21:25:43** |

**Verdikt:** engine, testování, vizuální měření i shipování jsou vyřešené.
Kapacitní strop není v Godotu.

### 1.4 Herní assety dnes (stav `uo-shadows`, `HEAD 3e1592b`)

| Co | Naměřeno 23. 10. (čtení stromu) |
|---|---|
| `assets/` | **57 souborů, 4,2 MB**; 16 PNG spritů (8 rolí + 8 předmětů), 7 dlaždic, 5 datových JSON |
| `assets/audio/` | **neexistuje** (kód na `assets/audio/sfx/` a `assets/audio/music/%s.wav` sahá a tiše nenajde) |
| `assets/ui/`, font | **neexistují**; hra používá vestavěný font Godotu |
| `tools/blender/sprites/` | **260 PNG**, z toho 4 vrstvy × 4 směry × 8 framů pro hráče i NPC (128/role) — **hra je nepoužívá** (používá ploché sprity) |
| Vrstvená grafika | 1 kus výbavy = **32 obrázků** (4 směry × 8 framů); 8 slotů = **256/role**; dnes 128/role; M6 je vědomě odložené rozhodnutí `A-1` |
| Obsah vs. GDD §10 | dnes 4 materiály / 4 dovednosti / 3 recepty / 1 nestvůra / 2 předměty; cíl `M` = 11 / 6 / 8 / 3 / 7 + mapa 4 oblastí, UI, zvuk |
| Plán | M0+M1 hotové (**11/11** granulí `done`); na M2–M6 připraveno **21 granulí** (M2 5, M3 3, M4 5, M5 5, M6 3) | 

### 1.5 Orchestra a free assety: nástroje hotové, zapojení chybí

| Vrstva | Stav (naměřeno 23. 10.) |
|---|---|
| Registr zdrojů | `assets/asset-registry.json`: Poly Haven (CC0, API + md5), Kenney (CC0, ZIP pin), Google Fonts (OFL), ruční zdroje (OpenGameArt, Freesound, Incompetech, Mixamo — licence per asset) |
| Fetch | `tools/asset-fetch.mjs` — stahuje, ověřuje hash, píše `assets/asset-lock.json` a `CREDITS.md`; **živě ověřeno** (Poly Haven, Kenney), 2 assety v registru |
| Licence | `tools/check-licence.py` — 9 scénářů testu; **v žádném workflow** a **ve hře není** `asset-lock.json` ani `CREDITS.md` |
| Zapojení do pipeline (P2) | **NE** — `ASSETY-PLAN.md` („Stav: neimplementováno“); žádný krok workflow fetch nepouští |
| Lokální knihovna stanice | **~1 GB**: Kenney 19 ZIP (UI, RPG audio, interface sounds, **music jingles**, fonty, mini-dungeon), Poly Haven 216/290 MB, Quaternius 63/190 MB (animované 3D + Universal Animation Library), izo dlaždice 3 827/95 MB, fonty 17 |

**Co z toho plyne:** orchestra dnes **neumí přidat jediný cizí asset**, i když
na to má hotový nástroj. Chybí ~1–2 sezení práce (P2) a lidské rozhodnutí.

### 1.6 Blender: jen na stanici — a co to znamená

| Co | Stav | Doklad |
|---|---|---|
| Blender na stanici | **5.2.1 LTS** (`C:\Program Files\Blender Foundation\Blender 5.2\blender.exe`) | `blender --version` (23. 10.) |
| Pipeline v herním repu | `tools/blender/build_character.py` + `postprocess.py`; postavy z primitiv, rig 14 kostí, chůze, 4 směry × 8 framů, vrstvy zvlášť | `docs/ADD.md` §7.1 |
| Blender v CI | **není** a žádný workflow ho neinstaluje; dokumentace tvrdí, že v orchestra „být nemůže“ („ubuntu-latest ho nemá a instalace je drahá“) — **v CI to NENÍ změřené** | `docs/BRANY-HRY.md` §3D→2D; `grep` workflowů (23. 10.: 0 zmínek) |
| Domácí uzel `pc-domaci` | **off 446 h**; `worker.cmd` existuje, `.forge/node/.env` **chybí**; kinds `assets,test,build` | `/health` (23. 10.); PROVOZ-ORCHESTRA §PC uzel |
| Krok `blender:` ve workeru | **není**; worker umí `shell`, `godot-import`, `godot-test`, `godot-export`, `python`, `forge`, `make-dir`; `shell:` se vždy ptá y/N (bezobslužně se přeskočí) | `repo/.forge/node/worker.mjs` |
| `oracle-frankfurt` | **žije** (kinds `test,build,assets`), hardware a přítomnost Blenderu **neznámé** | `/health` |
| Lan úlohy | `POST /task` umí `target:"lan"`; roadmapa ale zakládá **jen `target='cloud'`** | `conductor/src/index.ts` |
| Spolehlivost renderu | „jeden běh Blenderu spadne po ~10 renderech“; renderer není reprodukovatelný; skripty nepinují verzi | skill `tovarna-assetu`; `docs/ADD.md` §7.1 |

**Co z toho plyne:** skin (postava, animace, ikony) **technicky jde**, ale jen
na stanici nebo na uzlu, který Blender má — a to dnes **není zapojené**.
Cloud agenti renderovat neumí.

### 1.7 Vizuální a zvukové brány: co měří a kde jsou slepá místa

| Brána | Co měří | Slepé místo (naměřené) |
|---|---|---|
| `check-schema.py` | deklarace vs. mapy vs. kód vs. dlaždice | `world.gd` prázdný → jedna kontrola jen poznámka |
| `check-assets.py` | sprity vs. `spec.json` (výška, okraj, díry, barvy, poměry), hudba z manifestu | **animace se neměří** (`walk_*.png` v `assets/sprites` nejsou), **hudba bez manifestu = přeskočeno**, sprity mimo `spec.role` se neměří; **nemá offline test** |
| `vision.mjs` | obsah snímku (presence) / diff | **neblokuje**; dva běhy se můžou neshodnout; LGTM cache v CI **neplatí** (snímek je mimo repo) |
| `baseline.py` | schválené vizuální položky (272), cache | **`_ceka_na_lgtm: true`** — schválil je agent 30. 9. 2026, na člověka se čeká |

**Naměřeno v CI #140:** `poznámka: animace chůze v projektu není – přeskočeno`
a `poznámka: hudba ve hře není – měření hudby přeskočeno`. Vizuální kvalita
tedy **nemá v pipeline žádné vynucení** — rozhoduje člověk.

### 1.8 Hudba a zvuk — zvláštní kapitola

- **Zvuk (SFX):** orchestra ho *může* dodat jako free asset (Kenney CC0: RPG
  audio, interface sounds — lokálně i v registru) a `check-assets.py` ho
  **neměří** (měří jen hudbu). Chybí jen zapojení (P2) a kód, který ho přehraje.
- **Hudba:** kód čeká `assets/audio/music/%s.wav`; brána čeká
  `assets/audio/music/manifest.json` s `melody_stats` (kroky, skoky, motiv,
  rozsah, dlouhé noty) a `motif_audio` (repetition, kontrast). **Manifest
  v repu není a nástroj `forge music`, na který brána odkazuje, na stanici
  neexistuje** (hledáno v `dsh-dev`, `assets`, skillech — 0 implementací).
- **Navíc naměřeno čtením kódu:** `check-assets.py` audio **neotevírá** —
  kontroluje jen existenci `.wav` a čísla z manifestu. „Změřeno“ je tedy
  tvrzení skladatele, ne důkaz ze vzorků.
- **Free hudba** je ruční zdroj (Incompetech CC-BY, Musopen PD, OpenGameArt);
  Kenney má CC0 **music jingles** (krátké, ne ambientní smyčky).

**Co z toho plyne:** hudba je blokovaná **dvakrát** — chybějícím nástrojem
a branou, která vyžaduje jeho výstup. Je to jediná assetová vrstva, kterou
nejde vyřešit ani P2, ani Blenderem.

### 1.9 Plán a testy: co orchestra nedodá

- **Plán granulí** píše ten, kdo navrhuje hru (session se skillou
  `game-developer`), ne orchestra. Dnes je roadmapa hotová (11/11) a **orchestra
  je idle**, protože nemá co dělat — to je správný stav, ne porucha.
- **Testy** jsou z auto-merge vyloučené; hotovo navíc znamená „funkci volá
  produkční kód a brána ji změřila konkrétní hodnotou“ (`GDD` §12). Když test
  chybí nebo je slabý (`has_method`), orchestra může sloučit mrtvý kód —
  přesně to se stalo u PR #39 (H240).

---

## 2. Tři stropy — kam až to dojde

| Vrstva | Strop 0: dnes | Strop 1: + P2 (fetch) | Strop 2: + Blender (stanice/uzel) | Strop 3: plná hra |
|---|---|---|---|---|
| Kód, simulace, smlouvy (M2–M5) | **orchestra** (18 granulí) | totéž | totéž | totéž |
| Data (materiály, předměty, recepty, dovednosti) | **orchestra** (JSON) | totéž | totéž | totéž |
| Levely/mapa | **orchestra** (JSON), design = session | totéž | totéž | + lidský vkus na mapu |
| Dlaždice a textury | jen procedurální (kód/Pillow) | **free CC0 fetch** (Poly Haven/Kenney) | + render/konverze na 96×48 | + sjednocení stylu |
| Postava a vrstvy (skin) | **ne** | **ne** | **Blender** (8 slotů × 32 = 256/role) | + rozhodnutí `A-1` (kolik slotů/směrů) |
| Animace (idle/útok/smrt) | **ne** | **ne** | **Blender** (dnes jen chůze) | + vkus |
| Ikony předmětů, nestvůry | **ne** (jen procedurální) | free/SDXL na stanici | SDXL (~100 s/obrázek) nebo Blender | + sjednocení |
| UI (rámeček, panel, ikony) | kód ano, **grafika ne** | **free CC0 UI** (Kenney) | + layout | + vkus |
| Font | **ne** | **Google Fonts (OFL)** | — | + volba |
| Zvuk (SFX) | **ne** | **Kenney CC0 audio** | — | + mix |
| Hudba | **ne** | **ne** (chybí skladatel i manifest) | **ne** bez nástroje/rozhodnutí | + licence/kompozice |
| Export a shipování | **orchestra/CI** (Win/Linux/Web, Pages) | totéž | totéž | totéž |
| Vizuální QA | měření ano, **vynucení ne** | + licence | + LGTM | **člověk (LGTM, sehrání)** |
| Ladění čísel a chuti | čísla ano, **chuť ne** | totéž | totéž | **člověk (sehrání 1–5)** |

**Odpověď na otázku „jak daleko od 0 do plné naskinované nastavené hry“:**

- **0 → hratelná kostra:** `tools/forge-new.mjs` (šablona + skeleton + generátor
  placeholerů `skeleton/tools/make-assets.py`) — minuty, dělá stanice.
- **0 → funkční hra (M0–M5):** orchestra po dodání plánu a testů; 11 granulí už
  hotových, 18 připravených kód/data. Tohle je **reálný strop orchestry dnes**.
- **funkční → naskinovaná (M6):** stanice (Blender/SDXL) + free assety + člověk;
  orchestra jen zapojí hotové soubory.
- **naskinovaná → nastavená:** hraní a vkus (sehrání u každého milníku),
  orchestra implementuje zadaná čísla, ale „je to zábava“ nezměří.

**Bez změn orchestra dojde k funkční hře s placeholdery. K plně naskinované hře
nedojde — chybí jí binárky, Blender a vkus. S P2 se strop posune na „funkční
hra s CC0 UI/zvukem/fonty“; s Blenderem na „naskinovaná hra“, ale pořád
s člověkem u LGTM a sehrání.**

---

## 3. Čísla, limity a cena

### 3.1 Průchodnost a stropy

| Veličina | Hodnota | Poznámka |
|---|---|---|
| Souběžné úlohy | 5 | `MAX_CONCURRENT`; konfigurace, ne měření |
| Otevřené PR | 5 | `ROADMAP_MAX_PRS` |
| Běhů na granuli | 8 | `GRAIN_MAX_RUNS` |
| Pokusů na úlohu | 5 | `MAX_ATTEMPTS` |
| Cooldown selhané granule | 30 min | `RETRY_HOURS=0.5` |
| Doba běhu | 1–4 min (agent), CI+release 2–3 min | #559/#560; #140 |
| Velikost změny | 60 řádků (výchozí), výš jen `size_lines` | auto-merge pravidla |

### 3.2 Kvóty a peníze

| Co | Hodnota | Poznámka |
|---|---|---|
| GitHub Actions | repo je **veřejné** (API `private=False`) → standardní hosted runnery bez minutového stropu | politika GitHubu, ne naše měření |
| Cloudflare Workers | free plán: 100 000 požadavků/den, 10 ms CPU na invokaci; tik 1 440/den | `wrangler.toml` komentáře, invariant 11 |
| Poskytovatelé | mistral 625 000 TPM, cerebras 30 000, groq 8 000, openrouter ~50/den, gemini vision malá kvóta | `providers.json`, `PROVOZ-ORCHESTRA.md` |
| Placený klíč | **žádný** (DeepSeek secret není) | CI log #140 |
| Repo hry | 5 979 KB (API), lokálně `.git` 42,9 MB | `/repos` API; `Get-ChildItem .git` |

**Cena orchestrace je $0** (free platformy + free modely); platí se jen čas
session a případné placené modely, pokud je uživatel přidá. To je naměřený
rozdíl proti ručnímu vývoji — ale **neznamená to, že práce je zdarma**: úzké
místo je lidské rozhodování a počet pokusů, ne peníze.

### 3.3 Co je hotové (kontext)

- M0+M1: **11/11 granulí `done`**; testy **130/0** (20. 10.), CI #140 `success`,
  release #99 `success`, Pages live.
- Sync šablony do hry hotový (drift **0 rozdílů**, 1 záměrný); orchestra
  **prokazatelně** vytvořila a sloučila PR #39 na free modelu (mistral,
  request 18 576 t) — pak se ručně našla vada H240 a opravila.
- Orchestra je teď **idle**, protože hra nemá další granule — to je stav
  plánu, ne porucha.

---

## 4. Co doplnit (priorita, cena, riziko)

| # | Co | Kdo | Cena | Co odemkne / riziko |
|---|---|---|---|---|
| **P1** | Napsat plán M2–M5 z TDD smluv (21 granulí, testy předem) | session (stanice) | 1 sezení | orchestra má co dělat; bez toho je idle |
| **P2** | P2-A/B: asset-fetch + check-licence do šablony a workflow; jeden reálný CC0 zvuk/UI | session | 1–2 sezení | UI/SFX/fonty/dlaždice/textury; rizika: limit 60 řádků u locku, síť v runneru, auto-merge binárek neověřen |
| **P3** | Hudba: rozhodnout skladatele vs. free CC-BY + manifest; případně nástroj `forge music`/generátor manifestu | session + uživatel | 1–2 sezení | odblokuje hudbu; jinak zůstává „hudba se neměří“ |
| **P4** | Změřit Blender variantu: (a) CI headless render (1 běh, xvfb, měřit čas), (b) domácí uzel/oracle (`/task target:'lan'`, má Blender?) | session | hodiny + 1 běh CI | rozhodne, zda skin umí cloud, nebo jen stanice |
| **P5** | Lidské LGTM baseline (272 položek) + sehrání po milnících | uživatel | 15–45 min/milník | vizuální kvalita dostane soudce |
| **P6** | Rozhodnout M6/A-1: kolik z 8 slotů a zda 4/8 směrů | uživatel | rozhodnutí | cena: 32–64 obrázků na kus výbavy |

**Doporučené pořadí:** P1 (aby orchestra nezahálela) → P6 (rozhodnutí, co se
vlastně vyrábí) → P2 (levné rozšířeníassetů) → P3 → P4 → P5 (průběžně).

---

## 5. Co zůstává neměřeno (a jak to změřit)

1. **Blender v CI** — dokumentace tvrdí „nemůže“; **neměřeno**. Měření: 1 běh
   workflow s Blenderem 5.2 headless + `xvfb`, render `--preview` a 1 směr ×
   8 framů, měřit čas a úspěšnost. Cena: 1 běh CI (řádově 10 min).
2. **Hardware `oracle-frankfurt`** (Blender? GPU? disk?) — neznámé. Měření:
   lan úloha s `python:` krokem, který vypíše `shutil.which("blender")`,
   `platform`, RAM. Cena: jedna úloha, bez rizika.
3. **Trvalá zátěž kvót** (kolik granulí/den free řetězec skutečně unese) —
   neměřeno; odhad z TPM a RPD je jen odhad.
4. **Úspěšnost po syncu** — vzorek 2 běhy; nelze z něj dělat trend.
5. **P2 auto-merge binárek** — návrh (ASSETY-PLAN B), ne ověřený stav.
6. **Render čas a reprodukovatelnost** — skill uvádí „~10 renderů na běh“;
   konkrétní časy pro 8 slotů nejsou změřené.

---

## 6. Co čeká na uživatele (rozhodnutí, ne agent)

| Rozhodnutí | Možnosti | Cena / co tím zemře | Doporučení |
|---|---|---|---|
| **M6/A-1: kolik slotů a směrů** | 4 sloty (dnes) / 8 slotů; 4 nebo 8 směrů | 32–64 obrázků na kus výbavy; víc slotů = víc renderů | začít 4 sloty, 8 slotů až po sehrání M5 |
| **Hudba** | skladatel `forge music` / free CC-BY s atribucí / CC0 jingly (Kenney) | vlastní nástroj = práce navíc; CC-BY = povinná atribuce; jingly nejsou ambient | nejdřív rozhodnout, zda hudba vůbec patří do M6, nebo až po sehrání |
| **P2 (asset fetch)** | zapojit / nezapojovat | 1–2 sezení; riziko locku a sítě | doporučuji zapojit — odemkne UI/SFX/fonty/dlaždice bez LLM |
| **Blender experiment** | 1 běh CI / jen stanice | 1 běh CI vs. ruční práce | doporučuji změřit (levné, rozhodne strop) |
| **LGTM + sehrání** | schválit baseline, hrát po milnících | čas 15–45 min/milník | bez toho „hotovo“ není hotovo (nový pracovní model) |

---

## 7. Jak čísla zopakovat

```powershell
# stav orchestra (živě)
cd E:\Workspaces\forge-orchestra
node tools\status.mjs

# conductor: health, fronta, běhy (secret je v .env, nikdy ho nevypisuj)
$env:FORGE_SECRET = ((Get-Content .env -Encoding utf8 | Where-Object { $_ -like 'FORGE_SECRET=*' }) -replace '^FORGE_SECRET=','').Trim()
$env:FORGE_URL    = ((Get-Content .env -Encoding utf8 | Where-Object { $_ -like 'FORGE_URL=*' }) -replace '^FORGE_URL=','').Trim()
node -e "const h={'x-forge-secret':process.env.FORGE_SECRET}; for (const p of ['/health','/queue','/roadmap','/status']) { const r=await fetch(process.env.FORGE_URL+p,{headers:h}); console.log(p, r.status); }"

# assety hry
cd E:\Workspaces\uo-shadows
(Get-ChildItem assets -Recurse -File | Measure-Object Length -Sum) | Select-Object Count,Sum
(Get-ChildItem tools\blender -Recurse -File -Include *.png | Measure-Object).Count
python .forge\check-assets.py .

# Blender na stanici
& 'C:\Program Files\Blender Foundation\Blender 5.2\blender.exe' --version

# lokální knihovna free assetů
Get-ChildItem E:\Workspaces\assets -Directory | ForEach-Object { $f=Get-ChildItem $_.FullName -Recurse -File | Measure-Object Length -Sum; "{0}: {1} souborů, {2:N1} MB" -f $_.Name,$f.Count,($f.Sum/1MB) }
```

**Doklady z tohoto měření (k 23. 10. 2026):** `wrangler.toml`; `tools/status.mjs`;
`GET /health`, `/queue`, `/roadmap`, `/status`; CI běh #140 (log s `snímek:`);
`repo/.forge/providers.json`; herní `.forge/roadmap.json`; `assets/` (počty);
`docs/ADD.md` §6–§8, §12; `docs/BRANY-HRY.md`; `ASSETY.md`, `ASSETY-PLAN.md`;
skill `tovarna-assetu`; `blender --version`; GitHub API `/repos`.

---

## 8. Co se z dokumentu provede (append-only)

- **23. 10. 2026:** dokument vznikl jako podklad; **nic se z něj neprovedlo**.
  Provedené kroky se sem dopíšou i s datem a odkazem na commit.

# Plán separace orchestra z workspace `Local-Deepseek` — NÁVRH K REVIZI

> **Co tenhle dokument JE:** plán. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 1. 10. 2026 · **Stav:** 🟡 **NÁVRH fází G0–G5 — neschváleno, neimplementováno**
**⚠ DOPLNĚNO 4. 10. 2026:** jedna část separace **provedena je** — přesun
**obecných pravidel** z `Local-Deepseek\AGENTS.md` do `DSH_HOME\AGENTS.md`
(§9). Fáze G0–G5 (přesun repozitářů) **provedené nejsou**.
**Zadání uživatele:** *„Aktuálně orchestra sedí ve workspace local-deepseek —
obávám se ale, že se to kvůli tomu bije s veškerým kontextem, který v tom
workspacu také bydlí — ověř to a je-li to pravda, naplánuj separaci do nového
workspace, jinak mě informuj a ignoruj úkol."*

> **Jak tenhle dokument číst.** Ověření **dopadlo napůl**: mechanická kolize
> (společný git, sdílený adresář stromu) **NENÍ** — tvrzení v té podobě je
> vyvrácené měřením. **Sémantická a provozní kolize JE** a je doložená.
> Proto dokument obsahuje **plán separace**, ale jiný, než by čekal ten, kdo
> hledal rozpletené repozitáře: **nic se nerozplétá, jen se přesune a zbaví
> cizího provozu.**
>
> **A jedno měření mluví proti původnímu zdůvodnění:** orchestra **není
> zahlcovaná okolím — je to největší nájemník workspace** (73,4 % bytů).
> Důvod k separaci tedy není „okolí překáží orchestře", ale **„orchestra
> předpokládá, že je středem workspace"** — což je jiná, a horší, vada.

---

## 1. Verdikt

| Otázka | Odpověď | Důkaz |
|---|---|---|
| Bydlí orchestra ve stejném **git repu** jako okolí? | **NE.** Workspace root **není git repo**; `orchestra` i `games/uo-shadows` jsou **dva samostatné repy** s vlastními remoty | `Test-Path .git` → `False`; `git -C orchestra rev-parse --show-toplevel` → `C:/Users/Ssevc/Local-Deepseek/orchestra`; remote `ssevcikm-spec/forge-orchestra` |
| Míchá se do stavu orchestra cizí nepořádek? | **NE.** Všech 75 řádků `git status` v orchestra míří dovnitř orchestra | `git -C orchestra status --porcelain` → 75 (15 `M` + 60 `??`); 0 řádků s `..` |
| Sahá orchestra ven z workspace (výstup o úroveň)? | **NE.** 0 výskytů `..\..` v orchestra | Sken celého stromu: jediné `..\..` je ve hře |
| Sahá **hra** ven? | **ANO, jednou.** `hra.cmd` hledá Godot v orchestra | `games\uo-shadows\hra.cmd:13` → `%HRA%..\..\orchestra\tools\godot\...` |
| Je orchestra zahlcená cizím **objemem**? | **NE — je to obráceně.** orchestra = **1 070 MB z 1 458 MB** workspace, tj. **73,4 % bytů a 60,4 % souborů** | Měření velikostí; největší položka workspace (`ollama`, 2 815 MB) je navíc junction na `E:`, takže v workspace fyzicky neleží |
| Je orchestra zahlcená cizím **kódem a instrukcemi**? | **ANO, měřeno.** 25 z jejích 80 absolutních cest míří **ven** (ve 22 z 59 souborů) a `verify-setup.py` **vyžaduje 9 sourozeneckých složek** | §2.4 |
| Bije se orchestra s okolím **provozně**? | **ANO — a to je hlavní důvod k separaci.** Čtyři doložené kolize | §2.3 |
| Je tajemství orchestra izolované od okolí? | **NE.** `.secrets` má **stejná ACL jako celý workspace**, včetně sandbox-write SID s právem zápisu | §2.5 |

**Jednou větou:** orchestra **není** provázaná s okolím technicky (git je čistý),
ale **je napsaná tak, jako by vlastnila celý workspace** — a zároveň **bydlí
v pracovním prostoru, který patří jinému projektu se dvěma protichůdnými
rozhodnutími.** To se projevuje každou session.

---

## 2. Co je naměřeno (podklad pro rozhodnutí)

### 2.1 Git topologie — čistá, nic se nerozplétá

```
C:\Users\Ssevc\Local-Deepseek\          ← NENÍ git repo (žádný .git)
├── orchestra\        ← samostatný repo → ssevcikm-spec/forge-orchestra
├── games\uo-shadows\ ← samostatný repo → ssevcikm-spec/uo-shadows
└── (zbytek: modelová stanice, archivy, obrázky, nástroje)
```

Hloubkový sken (3 úrovně) našel **právě dva** `.git` a **žádný** `.git` soubor
(worktree/submodule pointer). `orchestra\.gitignore` ani
`games\uo-shadows\.gitignore` neodkazují ven z repa; `.gitmodules` neexistuje;
`git worktree list` má jedinou položku; gitlinky (`160000`) v indexu → **0**.

**Důsledek:** separace je **přesun složky**, ne rozplétání historie. To je
nejlepší možná zpráva pro plán — a proto je plán krátký.

### 2.2 Míra promíchání obsahu

Workspace bez obsahu ollama junctionu: **7 763 souborů / 1 458,3 MB**.

| Složka / soubor | MB | Souborů | Co to je |
|---|---:|---:|---|
| `ollama/` (junction → `E:`) | 2 814,6 | 996 | běhový engine — **fyzicky mimo workspace** |
| **`orchestra/`** | **1 070,0** | **4 692** | **náš projekt — 73,4 % bytů workspace** |
| `obrazky/` | 338,9 | 682 | generátor obrázků, knowledge-base — jiný projekt |
| `games/` | 15,5 | 1 577 | **naše hra** (1 klon) |
| `_asar_probe/` | 4,2 | 564 | extrahovaný DSH kód — diagnostika |
| `dsh-consolidation/` | 2,7 | 161 | archiv pluginů, migrace |
| `research/`, `_analyza/`, `dsh-update-0.2.0/`, `router/`, `_retired/`, zbytek | ~0,6 | ~40 | historie a jednorázovky |
| `python-installer.exe` (v rootu) | 25,7 | 1 | pozůstatek instalace (jediný soubor > 1 MB v rootu) |

Uvnitř orchestra bydlí objem v `.npm-cache` (604 MB) a `conductor\node_modules`
(202 MB); `tools\godot` má 172,5 MB. **Generovaný obsah** (`node_modules`,
`.godot`, `__pycache__`) dělá **3 601 souborů / 381 MB** — to je legitimní
provoz, ne nepořádek.

V rootu je **15 složek a 33 souborů**; **13 z 15 složek** a ~17 ze 33 souborů
s orchestrou nesouvisí. Z **16 volných `.md`** jich orchestra zmiňuje **12**
(dohromady 441,7 KB), ale **4 ji nezmiňují vůbec** (145,3 KB) — a to jsou
dokumenty modelové stanice a DSH.

**Přesné číslo, o které jde** — souborů **zdrojového typu** (kód, konfigurace,
dokumentace; bez binárek a `node_modules`):

| Kde | Souborů | Řádků |
|---|---:|---:|
| `orchestra/` | **142** | 18 098 |
| `games/uo-shadows/` | **71** | 12 213 |
| **celkem orchestra + hra** | **213** | **30 311** |
| zbytek workspace | ~3 071 souborů (z toho ~2 700 zdrojového typu) | — |

> **Pozor na výklad:** tohle **není** „orchestra je oběť". Agent, který hledá
> něco o orchestře, projde ~13× víc cizích souborů — to je **trvalá daň**, ale
> **orchestra je zároveň ten, kdo do workspace sype nejvíc**. Obojí je pravda
> a obojí mizí separací.

### 2.3 Čtyři provozní kolize (toto je skutečný důvod k separaci)

Nejsou to dojmy — každá je doložená souborem nebo měřením.

#### Kolize 1 — Dvě protichůdná rozhodnutí o modelech ve stejném prostoru

| Kde | Rozhodnutí | Zdroj |
|---|---|---|
| `README.md` (workspace, root) | **„Router skončil"** — přepínání providerů bourá prompt cache, cache-hit je 25–50× zlevnění. DeepSeek přímo, **žádná rotace** | `README.md:268-288` |
| `orchestra/README.md` | **„Zkouší se popořadě, první odpoví, vyhrává"** — rotace free providerů je *záměr* orchestra | `orchestra/README.md:130-144` |

Obě rozhodnutí jsou **správná pro svůj projekt** a obě mají naměřené
odůvodnění. Jenže bydlí v jednom pracovním prostoru, kde si je agent přečte
obě — a `README.md` v rootu je při čtení z cwd **první**, co uvidí.

**Tohle je ta „rána", kterou uživatel tušil.** Není to technická vazba, je to
**konflikt místního konsenzu**.

#### Kolize 2 — Jeden `AGENTS.md` pro šest témat

DSH načítá instrukce **od projektového rootu k cwd**, kde projektový root
pozná podle markeru **`.git`**. Naměřeno:

| Fakt | Hodnota |
|---|---|
| `C:\Users\Ssevc\.dsh\AGENTS.md` (uživatelský baseline) | **NEEXISTUJE** |
| `.git` nad `Local-Deepseek` (`Local-Deepseek`, `C:\Users\Ssevc`, `C:\Users`, `C:\`) | **nikde** |
| `AGENTS.md` v celém stromě | **přesně jeden** — `Local-Deepseek\AGENTS.md` (8 083 B) |

**Důsledek:** všechny session dostanou **stejných 8 083 B pravidel** — ať
pracují na orchestra, na hře, na Ollamě nebo na DSH. Naměřeno na titulech
session: z **48 session** s `cwd = Local-Deepseek` se orchestra týká **3 (6,2 %)**
a hry 2 (4,2 %); ostatní jsou DSH, Ollama/LiteLLM, obrázky a jiné (68,8 %).

> **A tady je past, kterou separace sama vytvoří, kdyby se udělala bezmyšlenkovitě:**
> `orchestra\` **má `.git`**, ale **NEMÁ `AGENTS.md`**. Kdyby se session
> otevřela s cwd v orchestra, projektový root by se našel hned v cwd a řetězec
> by byl **orchestra** — takže root `AGENTS.md` by se **přestal načítat**
> a agent by o všechny instrukce **přišel**. *(Toto je predikce z dokumentované
> logiky `projectRootMarkers=['.git']` + měření, ne empiricky spuštěný test —
> proto je krok G4.2 v plánu **povinný**, ne volitelný.)*

#### Kolize 3 — Sandbox a schvalování platí na obojí naráz

DSH má **jeden sandbox na session**, odvozený od workspace
(`permission.defaultPreset: workspace-write`, `approval: ask`). Práce na
orchestře tak:

- nemůže zapisovat mimo `Local-Deepseek` (proto se dřívější session musely
  přepínat na `danger-full-access` — viz `HANDOFF.md`, „Environment"),
- a zároveň **každá** operace s okolím (aktualizace skillu v `~\.dsh\skills\`,
  zápis do `E:\`) spouští schvalovací dialog, i když s orchestrou nesouvisí.

#### Kolize 4 — Jméno workspace lže o tom, co v něm je

Workspace se jmenuje **`Local-Deepseek`** a jeho `README.md` začíná
*„Lokální DeepSeek na tomto PC"*. Je to **dokumentace modelové stanice**
(Ollama, junctiony na `E:`, VRAM, tok/s) — a zároveň **pracovní prostor
orchestra**. Důsledky, které se už staly:

- `worker.mjs` má komentář o *„lokální pipeline, plánování přes Ollama"* a
  mrtvý default `FORGE_CMD` na `C:\Users\Ssevc\Local-Deepseek\forge.cmd` —
  cesta, která vznikla **jen tím**, že projekt bydlí tady.
- Venkoncem **tři různá jména téhož**: `uo-shadows` (repo), `uo-sandbox`
  (v `project.godot`), `forge-quest` (jiná živá hra).
- Skill `orchestra` i `AGENTS.md` musejí psát absolutní cesty
  `C:\Users\Ssevc\Local-Deepseek\…`. **Tím se orchestra stává nepřenosnou.**

### 2.4 Absolutní cesty a tvrdé vazby — kolik práce přesun obnáší

Sken (Python walk; `grep` tool tu **selhal** — viz past níže):

| Vzor | orchestra | hra |
|---|---:|---:|
| Absolutní cesta na `Local-Deepseek` | **80 výskytů / 59 souborů** | **1** (mrtvá cesta na smazaný `gameforge`) |
| z toho **míří ven** z orchestra | **25 výskytů / 22 souborů** | — |
| výstup o dvě úrovně (`..\..`) | **0** | **1** (`hra.cmd:13`) |
| odkazy na `games/` jménem | 38× / 27 souborů | — |

Z 25 cest ven: `games` 17×, root workspace 5×, mrtvý `gameforge` 3×.

> **Past, kterou tenhle sken odhalil — a je nejdrsnější, co jsme viděli:**
> `grep` tool nad `orchestra/` vrátil **0 nálezů** absolutních cest.
> Python jich našel **80**. Je to táž past, kterou má `dsh-prostredi` zapsanou
> (skryté složky se z pozice rodiče přeskakují) — **80 ku 0.**

**Tvrdé vazby, které separace rozbije (ověřeno čtením souboru):**

| # | Co | Proč to spadne |
|---|---|---|
| 1 | `games\uo-shadows\hra.cmd:13` → `..\..\orchestra\tools\godot\...exe` | Launcher hry po přesunu orchestra **nepoběží**. Je to **jediné `..\..` v celém stromu** |
| 2 | `orchestra\tools\verify-setup.py:7,11-12` | `W = r"C:\Users\Ssevc\Local-Deepseek"` + **pevný seznam 9 sourozenců**: `orchestra`, `games`, `games/uo-shadows`, `research`, `router`, `_retired`, `obrazky`, `ollama`, `session-handoff`. Po separaci nahlásí **6× CHYBI** a skončí `NEJAKE PROBLEMY`, **exit 1** |
| 3 | **21 nástrojů** s absolutní cestou ven (`validate-all.mjs:5-6`, `kontrola-driftu.mjs:17`, `kontrola-diakritiky.py:11`, `over-dokumentaci.py:165`, `sync-sablona-hra.py:18`, `test-ci-workflow.mjs:33-34`, `compare-game.mjs:8`, `zjisti-pages.mjs:13`, `lint-roadmapa.py:23`, `simulace-dag.py:13`, `stav-dag.py:11,13`, `migrace-schema.py:28`, `baseline-poznamka.py:20`, `oprav-*.py` (7), `install-into-repo.ps1:8,11`) | Po přesunu přestanou fungovat |
| 4 | **47 souborů** s vlastní absolutní cestou (`tools\analyza*.mjs` — 11 skriptů s `const ORCH = '...'`, `fronta.mjs`, `stahnni-patch.mjs`, `mereni-*.mjs`, `overit-branu.mjs`, …) | Musí projít editací |
| **5** | **`process.cwd()` se v `orchestra\tools\*` nevyskytuje ANI JEDNOU** (0 ze 74 souborů) | **Vazba nejde přes cwd, ale přes literální cesty — takže „změnit cwd" nestačí.** Musí se editovat soubory. To je pro separaci horší varianta a je potřeba to vědět předem |

**Z toho plyne rozsah:** **59 souborů / 80 výskytů** musí projít editací, i kdyby
se orchestra jen přesunula. Z toho **55 cest do vlastního rootu je čistě
mechanických** (odvodí se z umístění souboru), **17 cest do `games/` se musí
rozhodnout** (§4, S2) a **3 cesty na smazaný `gameforge/` se mají smazat**.

### 2.5 Tajemství nejsou izolovaná (nález, který není o separaci, ale patří sem)

| Fakt | Hodnota |
|---|---|
| `orchestra\.secrets\` | 6 souborů + `gh-config` (PAT, klíče Groq/OpenRouter, Telegram token, `cf-secrets.json`) |
| ACL | **Stejná práva jako celý workspace** — děděná z `PRACOVNA\Ssevc` |
| Navíc | `S-1-4-957149736-827513059` s právem **Write + Delete** (sandbox-write SID, který DSH materializuje pro workspace root) |
| Kde | Tentýž SID je na rootu workspace (`inherited=False`) a **dědí se do `orchestra`, `orchestra\.secrets` i `games\uo-shadows`** |

**Důsledek:** *kdo smí zapisovat do workspace, smí zapisovat i do `.secrets`.*
Ochrana je dnes **jen `.gitignore`**, ne ACL. `.env` soubory jsou **4 a všechny
v orchestra** (hra nemá ani jeden — ověřeno `Test-Path`); hra má naopak
v `.gitignore` „pojistku" proti rozbité cestě k secretu, což je obrana proti
úniku, který **už jednou nastal**.

**To není důvod k separaci** (separace to neopraví — SID se dědí z rootu).
Je to **samostatný nález k rozhodnutí** a je zapsaný v §4 jako S9.

---

## 3. Rozhodnutí: separovat, nebo ne?

**Doporučení: ANO, separovat — ale ne z důvodu, který byl vysloven.**

Kdyby platilo původní zdůvodnění („bije se to s kontextem, protože je to
v jednom stromě"), odpověď by byla **ne**: git je čistý, vazby ven nejsou
a hledání je cílené. Oddělovat něco, co technicky oddělené je, by byla práce
nadarmo.

Separace má ale **tři důvody, které měření doložilo** a které se odkladem
zhoršují:

1. **Konflikt konsenzu o modelech** (§2.3, kolize 1) — dva protichůdné závěry
   v jednom prostoru. Tohle je věc, kterou **kód neopraví**; opraví ji až
   hranice.
2. **Sandbox a schvalování na obojí naráz** (§2.3, kolize 2) — dokud je to
   jeden workspace, každá práce na orchestra platí daň za cizí provoz
   a naopak.
3. **Přenositelnost** (§2.3, kolize 3) — orchestra nemůže být přenosná, dokud
   její nástroje ukazují na adresu modelové stanice. **Separace je předehrou
   k F3 (kontrakt) a F4 (převzetí)** z `PLAN-ROZVOJ-ORCHESTRA.md`: bez nového
   umístění nemá smysl cesty parametrizovat, protože není kam je parametrizovat.

**Co separace NENÍ:** není to oprava tichých selhání, není to F1, není to
náhrada `PLAN-ROZVOJ-ORCHESTRA.md`. Je to **předpoklad**, aby cesty mohly být
relativní a aby kontext workspace patřil jednomu projektu.

---

## 4. Rozhodovací otázky (na uživatele)

| # | Otázka | Návrh agenta | Proč je to otázka pro člověka |
|---|---|---|---|
| **S1** | **Kam orchestra?** | `C:\Users\Ssevc\Forge\` jako nový workspace, v něm `orchestra\` a `games\` | Je to volba umístění na disku; zároveň musí být dost místa (dnes `orchestra` 1,07 GB) |
| **S2** | **Jde klon hry s orchestrou?** | **ANO** — `games\uo-shadows\` **do** nového workspace, ne vedle | Kdyby zůstal mimo, nástroje orchestra (17 cest) i `hra.cmd` by na něj musely dosáhnout **přes hranici sandboxu**. Uvnitř workspace je to zdarma |
| **S3** | **Přesunout, nebo kopírovat a pak smazat?** | **Přesunout** (`robocopy /MOVE /XJ`), ale až po ověření, že nový strom je kompletní | Kopie = dvě pravdy o jednom repu, což je vada, kterou se tenhle projekt už jednou popálil (šablona vs. disk) |
| **S4** | **Nechat na starém místě junction (zpětnou kompatibilitu)?** | **NE** — a to je záměr | Junction by **tiše skryl** každou nepřepsanou cestu. Chceme, aby 55 cest **spadlo nahlas**, ne aby fungovalo dál a rozbilo se až jindy. (`dsh-prostredi` má tuhle past zapsanou: nástroj, který zapíše a nic neřekne) |
| **S5** | **Kdo vlastní Godot?** (`orchestra\tools\godot\`, ~50 MB, cílí na něj i `hra.cmd`) | **Přenést s orchestrou** a v `hra.cmd` nahradit cestu proměnnou `FORGE_GODOT` (ta už existuje v `.forge\node\.env`) | Godot je nástroj orchestra; hra ho jen používá. Dnešní `..\..\orchestra\...` je **jediná vazba hra→orchestra** a je to vazba špatným směrem |
| **S6** | **Co s 12 cestami na smazaný `gameforge/`?** | **Smazat ten kód**, ne přesouvat | Je to mrtvá větev; přesun by jí dal druhý život |
| **S7** | **Má nový workspace vlastní `AGENTS.md`?** | **ANO — a je to POVINNÉ, ne volitelné** | Ověřeno: `orchestra\` **má `.git`, ale NEMÁ `AGENTS.md`**. Kdyby se session otevřela s cwd v orchestra, DSH najde projektový root hned v cwd a root `AGENTS.md` **přestane načítat** → agent přijde o všech 8 083 B pravidel a **nedostane nic místo nich** |
| **S8** | **Kdy?** | Až po opravě červeného `main` (viz §6) | Přesun rozbitého systému je horší než přesun funkčního — nešlo by poznat, co rozbil přesun a co bylo rozbité už před ním |
| **S9** | **Co s `.secrets`?** (samostatný nález, separace ho neřeší) | **Zpřísnit ACL** na úzký okruh účtů; dnes má `.secrets` **stejná práva jako celý workspace** včetně sandbox-write SID s právem zápisu a mazání | *Kdo smí zapisovat do workspace, smí zapisovat i do `.secrets`.* Ochrana je dnes **jen `.gitignore`**. Separace to neopraví — SID se dědí z rootu workspace |

---

## 5. Fáze separace

Pořadí je podle **rizika**, ne podle pohodlí. Každá fáze má vlastní „Hotovo
znamená" a **nic se nepřesouvá, dokud není hotová fáze předchozí**.

### G0 — Zelený `main` (předpoklad, ne součást separace)

**Proč první:** dnes je `main` hry **červený** a orchestra kvůli tomu nevydá
ani granuli (změřeno, viz §6). Přesouvat systém, o kterém se nedá říct
„fungoval předtím", znamená ztratit schopnost rozlišit příčinu.

| Krok | Hotovo znamená |
|---|---|
| G0.1 | Opravit krok „Kontrola vizuálního schématu" v `ci.yml` (obě kopie) — doplnit `python3 -m pip install --quiet pillow` | CI #81 na `main` → **success** |
| G0.2 | Zapsat do dokumentace, že `main` byl červený a proč | V `HANDOFF.md` je to vidět |

### G1 — Příprava: měřit, než se sáhne

| Krok | Co | Hotovo znamená |
|---|---|---|
| G1.1 | Zapsat **inventuru cest** (80 výskytů / 59 souborů, z toho 25 ven / 22 souborů) do souboru, který bude sloužit jako kontrolní seznam | Soubor existuje; počty odpovídají skenu |
| G1.2 | Ověřit, že oba repy jsou **čisté nebo commitnuté** (`git status`) — přesun s necommitnutou prací je hazard | `git -C games\uo-shadows status --porcelain` → **0** (dnes splněno); u orchestra rozhodnout, co s **15 `M` + 60 `??`** |
| G1.3 | Zjistit volné místo na cílovém disku | ≥ 2 GB (orchestra 1 070 MB + hra) |
| G1.4 | **Rozhodnout, co s 47 soubory, které mají vlastní absolutní cestu** — opravit, nebo smazat (řada z nich jsou jednorázové záplaty `oprav-*.py`, které F0.5 toho druhého plánu navrhuje smazat) | U každého souboru je rozhodnutí: opravit / smazat |

### G2 — Přesun stromu

| Krok | Co | Hotovo znamená |
|---|---|---|
| G2.1 | Vytvořit `C:\Users\Ssevc\Forge\` | existuje |
| G2.2 | `robocopy` s `/MOVE /XJ /E` pro `orchestra\` i `games\uo-shadows\` | Počet souborů v novém stromu = počet před přesunem (měřeno **před** i **po**) |
| G2.3 | **Ověřit, že oba `.git` jsou v pořádku** a `git status` dává totéž co před přesunem | `git -C <nová cesta> rev-parse --show-toplevel` sedí; `git status --short` má stejný počet řádků |
| G2.4 | **Nedělat junction** na staré místo (S4) | `Test-Path C:\Users\Ssevc\Local-Deepseek\orchestra` → **False** |

### G3 — Oprava cest (tady se to musí rozbít nahlas)

**Princip:** nástroj si **sám najde, kde je**, místo aby tvrdil, kde bydlí.
Vzor, který v orchestra **už existuje** a je označený jako jedna z nejlepších
částí (`pick-provider.mjs` — konfigurace se dohledá za běhu, nekopíruje se).

| Krok | Co | Hotovo znamená |
|---|---|---|
| G3.1 | Nahradit **47 souborů** s cestou `C:/Users/Ssevc/Local-Deepseek/orchestra` odvozením z umístění souboru (`fileURLToPath(import.meta.url)` v `.mjs`, `pathlib.Path(__file__).resolve().parents[1]` v `.py`) | `grep` nad `orchestra/tools/` na `Local-Deepseek` → **0** |
| G3.2 | **21 nástrojů** s cestou do `games/uo-shadows` nahradit **jedním pojmenovaným parametrem** (`--hra`, proměnná `FORGE_HRA`) s výchozí hodnotou `..\games\uo-shadows` | Nástroje jdou spustit z jiné složky i pro jinou hru |
| G3.3 | Smazat cesty na `gameforge/` (mrtvý kód — 3 výskyty, např. `tools\git.cmd` v komentáři) | Soubory/řádky neexistují; `validate-all.mjs` se nerozbil |
| G3.4 | `games\uo-shadows\hra.cmd:13` → `FORGE_GODOT` (z `.forge\node\.env`), ne `..\..\orchestra\...` | `grep` na `\.\.\\\.\.\\orchestra` ve hře → **0** |
| G3.5 | **`verify-setup.py` přepsat** — jeho seznam 9 sourozenců (`research`, `router`, `_retired`, `obrazky`, `ollama`, `session-handoff`) po separaci **6× nahlásí CHYBI** a skončí `exit 1` | Skript po separaci skončí **OK** — a kontroluje jen to, co orchestře patří |
| G3.6 | **Ověření:** spustit, co je spustitelné offline, a porovnat s dnešním stavem | Výsledky v §7 sedí na čísla z `HANDOFF.md` |

> **Proč to musí spadnout nahlas:** přesně tomuhle se `AGENTS.md` věnuje
> v pravidle *„Nula a ‚nezměřeno' nejsou úspěch"*. Kdyby se cesty „nějak
> našly" (junction, fallback, `cwd`), vypadalo by to zeleně a chyba by se
> projevila až u jiné hry nebo v CI — tedy v místě, kde se to ladí nejhůř.
>
> **A pozor na jednu vlastnost, která mění postup:** v `orchestra\tools\*` se
> **`process.cwd()` nevyskytuje ani jednou** (0 ze 74 souborů). Vazba tedy
> **nejde přes pracovní adresář, ale přes literální cesty** — takže „spustit
> to z jiné složky" **nestačí** a soubory se musí skutečně editovat. Kdo by
> čekal, že si stačí změnit cwd, narazí.

### G4 — Rozdělení kontextu (vlastní smysl separace)

| Krok | Co | Hotovo znamená |
|---|---|---|
| G4.1 | Vytvořit nový DSH workspace na `C:\Users\Ssevc\Forge` (v GUI Web klienta je na to `WorkspacePicker` / `::add-workspace`) | `~\.dsh\storages\workspace.json` má **4** záznamy v `workspaceIds`; nová session má `cwd` v `Forge` |
| G4.2 | **POVINNÉ: napsat `C:\Users\Ssevc\Forge\AGENTS.md`** — pravidla **pro orchestra**, ne pro modelovou stanici | Soubor existuje **a je načtený** (ověřeno v nové session) |
| G4.3 | Z `Local-Deepseek\AGENTS.md` **odstranit** části, které patří orchestra (sekce „Jak ověřit nasazení na GitHub Pages", orchestra cesty) | Root `AGENTS.md` popisuje jen modelovou stanici a DSH |
| G4.4 | Přenést orchestra dokumenty (`FORGE-ORCHESTRA-MOZNOSTI.md`, `PLAN-ROZVOJ-ORCHESTRA.md`, `PLAN-ORCHESTRA-AI-AGENTI.md`, `ANALYZA-*`) do nového workspace | V `Local-Deepseek` nezůstane žádný dokument, který je **jen** o orchestra |
| G4.5 | Upravit **3 soubory skillů** s absolutní cestou na `Local-Deepseek` — ověřeno auditem: `imagegen-local\SKILL.md`, `imagegen-local\run.cmd`, `orchestra\SKILL.md` | `grep` na `Local-Deepseek` v `~\.dsh\skills\` → **0** |
| G4.6 | Opravit **už dnes mrtvý odkaz** v `orchestra\SKILL.md:460` na `Local-Deepseek\forge.cmd` (neexistuje) | Odkaz vede na živý soubor, nebo není |

> **G4.2 není kosmetika — je to záchrana kontextu.** DSH hledá projektový root
> podle markeru **`.git`** (default `projectRootMarkers: ['.git']`) a instrukce
> načítá **od projektového rootu k cwd**. Naměřeno: `orchestra\` **má `.git`,
> ale nemá `AGENTS.md`** — takže po otevření session s cwd v orchestra by se
> root `AGENTS.md` **přestal načítat** a agent by přišel o všech 8 083 B
> pravidel, aniž by cokoli dostal místo nich. *(Predikce z dokumentované logiky
> + měření; empiricky netestováno.)*
>
> **Tohle je druhá, tišší půlka téhož problému:** orchestra dnes **nemá vlastní
> kontext** — jen zděděný z modelové stanice. Separace bez G4.2 by tedy
> **zhoršila** to, co měla zlepšit.

### G5 — Zpětná kontrola

| Krok | Co | Hotovo znamená |
|---|---|---|
| G5.1 | Spustit celou sadu ověření z §6 z **nového** umístění | Všechna čísla sedí na referenci |
| G5.2 | Spustit jednu úlohu orchestra end-to-end (dispatch → PR) | PR vznikne; conductor hlásí `running: 0` po dokončení |
| G5.3 | Zapsat, co se změnilo, do `PLAN-ROZVOJ-ORCHESTRA.md` §7 | Řádek v tabulce „Co se změnilo proti návrhu" |
| G5.4 | **Teprve teď** zvážit smazání starých složek v `Local-Deepseek` | `Test-Path` na staré cesty → False; nic v orchestra na ně neodkazuje |

---

## 6. Rizika a co je blokuje

| Riziko | Jak se projeví | Obrana |
|---|---|---|
| **Přesun rozbije víc, než se čekalo** | některý nástroj tiše přestane nacházet soubory | G3.1–G3.4 dělají z každé cesty **jedno** místo; „Hotovo znamená" je grep na **0**, ne „funguje to" |
| **Nepodaří se rozlišit příčinu** | po přesunu něco nefunguje a není jasné, co to způsobilo | **G0 především** — přesun se dělá na zeleném systému |
| **`robocopy /MOVE` selže uprostřed** | část stromu je na obou místech | Před přesunem zapsat počet souborů a velikost; po přesunu porovnat. `git status` v obou repozitářích je druhý nezávislý důkaz |
| **Nová cesta mine sandbox** | session v `Forge` nemůže zapsat do `orchestra/` | Session **cwd musí být workspace root** (`Forge`), ne jeho podadresář (viz vlastnost DSH v G4) |
| **Ztratí se znalost, proč co bylo** | někdo „uklidí" komentář s naměřeným číslem | `AGENTS.md`: komentáře s naměřenými hodnotami **nejsou dluh**. Přesun je nesmí smazat — jen přenést |
| **Hra a orchestra se rozejdou** | dvě kopie šablony, dvě pravdy | Už dnes existuje `kontrola-driftu.mjs`; po přesunu musí běžet s **novými** cestami a hlásit 1 rozdíl (jako dnes) |
| **Mrtvý kód se přesune s projektem** | 12 cest na `gameforge` žije dál | G3.3 je **maže**, nepřesouvá |

**Blokující závislost celého plánu:** G0. Dokud je `main` červený, nedá se
ověřit ani krok G5.2 — a bez toho by separace končila dojmem, ne měřením.

---

## 7. Jak ověřit, že to po separaci funguje

Referenční čísla jsou z `HANDOFF.md` (naměřeno před separací). Po přesunu
se musí **shodovat**; když se některé rozejde, je to regrese přesunu.

S `$env:PYTHONIOENCODING='utf-8'`, z nového workspace rootu:

| Co | Příkaz | Očekáváno |
|---|---|---|
| Skilly | `python orchestra\tools\over-skilly.py` | 9 skillů, 0 chyb |
| Dokumentace | `python orchestra\tools\over-dokumentaci.py` | 63 kontrol, 0 chyb |
| Diakritika | `python orchestra\tools\kontrola-diakritiky.py` | VŠE OK |
| Brána schématu | `python orchestra\tools\test-check-schema.py` | 17/17 |
| Drift šablona↔hra | `node orchestra\tools\kontrola-driftu.mjs` | 1 rozdíl (`agent.yml`, necommitnutá divergence) |
| ⚠️ Baseline | `python orchestra\repo\.forge\baseline.py testy` | 24/24 (potřebuje širší oprávnění) |
| ⚠️ Vision testy | `cd orchestra\repo; node .forge\node\vision.test.mjs` | 34/34 (potřebuje širší oprávnění) |
| Schéma hry | `cd games\uo-shadows; python .forge\check-schema.py` | „Schéma je v souladu" + `výchozí buňka=96×48px` |
| Assety hry | `cd games\uo-shadows; python .forge\check-assets.py .` | „Vše v pořádku" + 2 poznámky o přeskočených kontrolách |
| Zapojení | `cd games\uo-shadows; python .forge\check-wiring.py .` | 57 funkcí v 7 souborech |
| Testy hry | `& '<godot>' --headless --path games\uo-shadows --script res://tests/run_tests.gd` | 36 kontrol, 0 selhání |

**Nové ověření, které po separaci platí a před ní nešlo:** `grep` na
`Local-Deepseek` v `orchestra\` i `games\uo-shadows\` → **0 nálezů**
(dnes **80 + 1**). A `python orchestra\tools\verify-setup.py` → **vše OK**
(dnes by po přesunu hlásilo 6× CHYBI a `exit 1`).

---

## 8. Co se změnilo proti návrhu

*(Prázdné — plán je v prvním znění.)*

| Datum | Co se změnilo | Proč |
|---|---|---|
| — | — | — |

---

## 9. PROVEDENO 4. 10. 2026 — přesun obecných pravidel do `DSH_HOME`

> **Co tenhle oddíl JE:** **záznam o provedení**, ne návrh. Nevznikl
> plánováním, ale rozhodnutím uživatele: *„chci mít nějakou dokumentaci
> obecnou (pro stanici) a lokální (pro orchestru)"* → *„přesunout"*.

**Co se přesunulo:** obecné části `Local-Deepseek\AGENTS.md` →
**`DSH_HOME\AGENTS.md`** (`~\.dsh\AGENTS.md`) — soubor, který DSH načítá
**jako první v řetězci instrukcí pro každou session v každém workspace**.

| Sekce původního `AGENTS.md` | Bytů | Kam |
|---|---:|---|
| Prostředí (pasti nástrojů a kódování) | 2 460 | `DSH_HOME` |
| Jak ověřovat (metoda) | ~8 000 | `DSH_HOME` |
| Jak dokumentovat (pravidla) | ~2 000 | `DSH_HOME` + skill `dokumentace` |
| Jak ověřit nasazení (obecný princip) | 849 | `DSH_HOME` (příkazy zůstaly projektu) |
| Kdy práce patří do nové session | 808 | `DSH_HOME` |
| Jazyk (pravidlo) | ~1 500 | `DSH_HOME` (naměřená tabulka zůstala projektu) |
| Co nikdy (obecné) | ~600 | `DSH_HOME` |
| Než začneš (obecné) | ~250 | `DSH_HOME` |
| **Zbytek** (Kam pro co, brány projektu, měření, projektové pasti) | ~22 000 | **zůstává projektu** |

**Výsledek v bajtech** (⚠ měřeno `Get-Item … .Length`, **ne** `len(text)`
v Pythonu — u českého textu jsou to **dvě různá čísla**: `len()` počítá
**znaky**, diakritika má v UTF-8 dva bajty):

| Soubor | Před | Po |
|---|---:|---:|
| `Local-Deepseek\AGENTS.md` (projekt) | 42 173 B | **23 727 B** |
| `DSH_HOME\AGENTS.md` (obecná) | — | **18 052 B** |
| **řetězec v session o orchestře** | 42 173 B (64,4 % rozpočtu) | **41 779 B (63,7 %)** |
| **řetězec v session o JINÉM projektu** | 42 173 B (64,4 %) | **18 052 B (27,5 %)** |

> **⚠ Poučení, které stojí za zapsání:** pro **orchestra session se neušetřilo
> téměř nic** (64,4 % → 63,7 %) — a je to správně: ta session potřebuje obecná
> pravidla **i** pravidla projektu. **Úspora je pro všechny OSTATNÍ workspace**
> (hra, stanice, DSH): **64,4 % → 27,5 % rozpočtu instrukcí.**
> Kdo by čekal úsporu v orchestra session, měří jinou věc, než co se stalo.

**Nový skill:** `~\.dsh\skills\dokumentace\SKILL.md` (8 933 B) — druhy
dokumentů, datum spotřeby, citace vs. tvrzení, checklist před odevzdáním,
oddělená sekce s naměřenými příklady. Katalog skillů: **12 → 13**.
Cena v každé session: **jeden řádek katalogu**, dokud se nenačte.

### 9.1 Co to rozbilo — a co se s tím udělalo

Na texty, které se přesouvaly, byly **navázané brány**. Naměřeno **před**
přesunem: z **15 textů**, které `over-dokumentaci.py` vyžaduje v root
`AGENTS.md`, jich **13 bydlelo v přesouvaných sekcích**. Kdyby se přesun udělal
bez přepojení, brána by po něm hlásila **13 chyb u souboru, který je
v pořádku** — a kdo by je „opravil" vrácením textu, **vrátil by i duplikaci**.

| # | Co se přepojilo | Jak |
|---|---|---|
| 1 | `orchestra\tools\over-dokumentaci.py` | jeden blok na `AGENTS.md` → **dva**: obecný proti `DSH_HOME`, projektový proti workspace. **63 → 65 kontrol** |
| 2 | `_analyza\ag-over-cisla.py` | tvrzení se hledají ve **dvou dokumentech** a vypíše se, **odkud** je vzal. Důkaz: po přesunu hlásí `INFO: 1 tvrzení se našlo v OBECNÝCH pravidlech` (tvrzení o `ci.yml`). Bez toho by spadl na `NENAŠEL JSEM TVRZENÍ` |
| 3 | `orchestra\tools\kontrola-diakritiky.py` | `DSH_HOME\AGENTS.md` přidán do **ručního seznamu** — jinak by nejčtenější dokument stanice nebyl kontrolovaný (vada **S27**) |
| 4 | `_analyza\_inventar.json` | přegenerován (měnily se `.py` soubory) |

⚠ **`over-dokumentaci.py` má nově 65 kontrol, ne 63.** Kdo to číslo vidí
v `HANDOFF.md` §1.3 nebo §7.5, čte **zestárlé číslo**, ne nepravdu — brána
vyrostla, ne že by dřív lhala.

### 9.2 Čím je přesun doložený (ne dojmem)

| Důkaz | Nástroj | Výsledek |
|---|---|---|
| Nic nezmizelo | `python _analyza\ag-presun-uplnost.py` | **47/47 pravidel** nalezeno, **0 zmizelých**; 2 kalibrační sondy se nenašly (hledá se správně) |
| Čísla v pravidlech sedí | `python _analyza\ag-over-cisla.py` | `exit 0` — 5 v pořádku, 2 historická, **0 rozchodů**, 0 nenalezených |
| Brána pořád chytá vadu | `python _analyza\ag-mutace.py` | **2 mutace, 2 chyceny** |
| Texty na místě | `python orchestra\tools\over-dokumentaci.py` | **65 kontrol, 0 chyb** |
| Diakritika | `python orchestra\tools\kontrola-diakritiky.py` | VŠE OK |
| Skilly se načítají | `python orchestra\tools\over-skilly.py` | **13 skillů, 0 chyb** |
| Návrat je možný | `_analyza\zaloha\AGENTS.md.pred-presunem-2026-10-04.md` | 42 173 B, SHA-256 shodné se zdrojem před přesunem |

### 9.3 Past, která se při tom našla (a je nová)

**Brána zachytila zalomený text.** První verze obecného souboru měla frázi
„nic nesmí zmizet" **zalomenou přes dva řádky** — takže ji `zkontroluj()`
(hledá **doslovný řetězec v jednom souboru**) nenašel a brána ohlásila
`CHYBÍ TEXT`. Správná reakce byla **opravit text, ne bránu**. Je to táž past,
kterou má `over-dokumentaci.py` popsanou v komentáři u skillu `dsh-prostredi`
(„hledaný text musí být na jednom řádku") — a platí i pro přesun.

**Pravidlo, které z toho plyne (obecné, patří do skillu `dokumentace`):**
*Přesun textu, na který visí brány, není přesun textu — je to **změna
měřidel**.* Kdo přesouvá pravidla, musí **napřed najít, kdo je čte**, a teprve
pak stěhovat.

### 9.4 Co tím ještě NENÍ vyřešené

- **Fáze G0–G5** (přesun repozitářů orchestra a hry do `E:\Workspaces\…`) —
  nedotčeno; uživatel rozhodl, že **všechny budoucí projekty mají být na `E:`**.
- **Lokální `AGENTS.md` pro orchestra a pro hru** — vzniknou až s novými
  workspace; dnes je projektový `AGENTS.md` v rootu `Local-Deepseek`.
  **Musí vzniknout dřív, než se session otevře s cwd v repu** — jinak se
  projektový root najde v repu a **root `AGENTS.md` se přestane načítat**
  (ověřeno: `.git` v `orchestra\` existuje, `AGENTS.md` tam není).
- **`E:\Workspaces\game-clone` a `C:\idle-realm`** — oba jsou git repy bez
  `AGENTS.md`, takže jejich session dnes nedostanou **žádná** workspace
  pravidla (jen ta obecná z `DSH_HOME`).
- **13 dokumentů o stanici** (`README.md`, `POZOR-E-DSH-NEMAZAT.md`,
  `ANALYZA-EFEKTIVITY-DSH.md`, …) leží dál v rootu projektu orchestra —
  rozdělení *dokumentů* (ne pravidel) je další krok.

---

## 10. PLÁN PŘESUNU REPOZITÁŘŮ NA `E:` — ✅ **ZVALIDOVÁNO 4. 10. 2026, STÁLE NEPROVEDENÉ**

> **Co tenhle oddíl JE:** **plán**, který prošel validací. Vznikl 4. 10. 2026
> po rozhodnutí uživatele: *„Chci mít všechny budoucí projekty v E workspaces."*
> **Nic z něj není provedené** — validace na datech **nesáhla**.
>
> **⚠ Datum spotřeby (PŮVODNÍ):** čísla v §10.1–§10.6 jsou naměřená
> **4. 10. 2026 19:5x UTC** nad `orchestra = c2f730f` a `uo-shadows = 0fdc784`
> a jsou **ve svém čase správná** — nepřepisují se. **Co z nich přestalo
> platit, je v §10.2b** (přeměřeno 4. 10. 2026 20:0x UTC, tytéž commity).
>
> **✅ VALIDACE PROBĚHLA 4. 10. 2026 (19:5x–20:1x UTC)** — plánovací session,
> devět bodů V1–V9 spuštěním (ne čtením). Výsledek: **plán je proveditelný**,
> ale **čtyři jeho čísla a dva kroky byly opraveny** a **všechna rozhodnutí
> D1–D9 jsou rozhodnutá uživatelem** (§10.3). Záznam o validaci: **§10.7**.
> Zadání pro prováděcí session: `NEXT-SESSION-INSTRUKCE.md`.

### 10.1 Cíl

| Repo | Dnes | Cíl |
|---|---|---|
| orchestra | `C:\Users\Ssevc\Local-Deepseek\orchestra` | `E:\Workspaces\forge-orchestra` |
| hra UO | `C:\Users\Ssevc\Local-Deepseek\games\uo-shadows` | `E:\Workspaces\uo-shadows` |
| projektové dokumenty a `_analyza\` | `C:\Users\Ssevc\Local-Deepseek\` (root, **není git repo**) | s orchestrou (§10.3 D3) |
| stanice (DSH, Ollama, obrázky, pluginy) | `C:\Users\Ssevc\Local-Deepseek\` | **zůstává** |

**Obě cílové složky uživatel založil** (4. 10. 2026, obě prázdné).

### 10.2 Naměřená cena přesunu — a proč je vyšší, než plán tvrdil

Plán výš (§2.4) počítal **70 výskytů absolutních cest** — ale **jen uvnitř
`orchestra/`**. Sken celého workspace (`_analyza\sken-cest-celek.py`, Python
walk) našel **325 výskytů ve 218 souborech**, z toho:

| Typ | Výskytů | Kde |
|---|---:|---|
| **KÓD** (musí se opravit) | **208** | `_analyza/` **138** · `orchestra/` 61 · root 6 · stanice 2 · hra 1 |
| DOKUMENTY (smí zestárnout) | 117 | root 73 · `_analyza/` 21 · `orchestra/` 15 · stanice 8 |

> **Rozdíl je 3× a je to jiná práce.** 138 výskytů je v `_analyza\` — tedy
> v **analytických nástrojích**, které sahají na **oba** repy zároveň
> (`WS / "orchestra"` i `WS / "games" / "uo-shadows"`). Ty se nedají opravit
> „odvozením z umístění souboru": potřebují **dvě** cesty, a ty po separaci
> leží ve **dvou různých workspaces**.
>
> **A druhá půlka téhož:** dokument, který **cituje historickou cestu**, se
> **NEPŘEPISUJE** — je to záznam (pravidlo „historická čísla se nepřepisují").
> Kdo začne „opravovat" cesty ve `ANALYZA-*` a `HANDOFF.md`, maže důkazy
> o tom, kde co bylo.

### 10.2b PŘEMĚŘENO 4. 10. 2026 (20:0x UTC) — validace

**Postup:** `python _analyza\sken-cest-celek.py` (tytéž příkazy, tytéž commity
`c2f730f` / `0fdc784`). Tabulka výš zůstává jako **záznam o tom, co platilo
v 19:5x**; tady je, co platí teď.

| Veličina | §10.2 (19:5x) | **Naměřeno 20:0x** | Rozdíl |
|---|---:|---:|---|
| **KÓD celkem** | **208** | **208** | ✅ **sedí přesně** |
| KÓD `_analyza/` | 138 | **138** | ✅ sedí |
| KÓD `orchestra/` | 61 | **61** | ✅ sedí |
| KÓD root / stanice / hra | 6 / 2 / 1 | 6 / 2 / 1 | ✅ sedí |
| DOKUMENTY | 117 | **128** | ⚠ **+11** |
| Souborů celkem | 218 | **219** | ⚠ +1 |
| Výskytů celkem | 325 | **336** | ⚠ +11 |

**Rozdíl je jen v DOKUMENTECH — a je to růst, ne nepravda.** Dokumenty smějí
zestárnout (jsou to citace), takže se cena práce nemění. Přírůstek jde celý do
root workspace (73 → 84) a je z větší části **v dokumentech, které vznikly
nebo se přepsaly po 19:5x** — tedy i v samotném tomhle plánu a v zadání
(`PLAN-SEPARACE-WORKSPACE.md` sám nese 12 výskytů, `NEXT-SESSION-INSTRUKCE.md` 1).
**Měřidlo, které měří dokumenty o přesunu, měří i sebe.**

#### ⚠ Pracovní jednotka nejsou VÝSKYTY, ale SOUBORY

Sken počítá **výskyty**; práce se ale dělá **po souborech**. Naměřeno
(stejný sken, rozdělení na soubory):

| Oblast | Souborů s cestou | Výskytů | Na soubor |
|---|---:|---:|---:|
| **`_analyza/`** | **117** | 138 | **1,2** |
| `orchestra/` | **51** | 61 | 1,2 |
| root workspace | 5 | 6 | 1,2 |
| nástroje stanice | 2 | 2 | 1,0 |
| `games/` | 1 | 1 | 1,0 |
| **CELKEM** | **176** | **208** | 1,2 |

**Dvě čísla, která z toho plynou a kterými se má řídit P1:**
**176 souborů** musí projít editací (ne 208 výskytů) — a **v `_analyza\` je to
117 souborů, z nichž každý má v průměru 1,2 výskytu** (typicky jedna konstanta
`WS = Path(r"C:\Users\Ssevc\Local-Deepseek")`).

#### ⚠ A past v tom měřidle: „výskyt" není totéž co „cesta"

Ověřeno dvěma přísnějšími počty. Sken hledá **řetězec `Local-Deepseek`**, takže
mu **projde i zmínka v próze** („workspace `Local-Deepseek`") — a naopak
**přísnější vzor „musí následovat oddělovač" mine kořenové cesty**, protože
`Path(r"C:\...\Local-Deepseek")` končí na konci řetězce. Naměřeno:

| Počet | KÓD | DOKUMENTY |
|---|---:|---:|
| volný (jak měří sken) | 208 | 128 |
| přísný (`Local-Deepseek` + oddělovač) | 100 | 82 |

**Ani jedno z těch čísel není „cena přesunu"** — volné nadsazuje (počítá prózu),
přísné podhodnocuje (ztrácí kořenové cesty). **Správná odpověď je počet
souborů (176)**; obě krajní čísla se sem zapisují proto, aby je nikdo nebral
jako jedinou pravdu. Postup je zopakovatelný a je v §10.7.

**Co z toho plyne pro P1:** inventura se nedělá podle „208 výskytů", ale
**podle 176 souborů** — a u každého je rozhodnutí `opravit` / `archivovat`.

### 10.3 Rozhodnutí, která musela padnout PŘED přesunem — ✅ **ROZHODNUTA** (§10.3b)

| # | Otázka | Návrh | Proč to není samozřejmé |
|---|---|---|---|
| **D1** | Jména cílových složek | **`forge-orchestra`** a **`uo-shadows`** (shodná s názvy rep na GitHubu) | Titulek workspace je kosmetický, ale **cesta je identita** — pozdější přejmenování složky odpojí sessiony (`Re-adding a directory starts fresh`) |
| **D2** | Je workspace root = kořen repa? | **ANO** pro oba | `AGENTS.md` se načítá **od projektového rootu k cwd** a projektový root se hledá podle `.git`. Kdyby byl workspace „kontejner" a repo v podadresáři, `AGENTS.md` v kořeni workspace **se nenačte** |
| **D3** | Kam s projektovými dokumenty (`HANDOFF.md`, `KRONIKA-PROJEKTU.md`, `PLAN-*`, `ANALYZA-*`, `ZADANI-*`, `_analyza\`)? | **Do repa orchestra a COMMITNOUT** | Dnes **nejsou v žádném gitu** (root workspace není repo) → přesun je jediná šance je verzovat. `_analyza\` do repa **nevadí**: šablona pro hry je jen `orchestra\repo\**`, takže se do her nezkopíruje. Přechodné věci (`_inventar.json`, `snapshot-*`, `tmp-*`) patří do `.gitignore` |
| **D4** | Tvar odkazu orchestra → hra | `FORGE_HRA` (env) + `--hra`, výchozí **`..\uo-shadows`** (sourozenec) | Dnes `games/uo-shadows` (potomek). Po přesunu je to **sourozenec** — a **4 nástroje do hry zapisují** (`sync-sablona-hra.py:45`, `kontrola-driftu.mjs:148,186`, `install-into-repo.ps1:96–109`, `asset-fetch.mjs:157`) → zápis **mimo workspace** = schvalování |
| **D5** | Co se 138 cestami v `_analyza\`? | **Triage, ne plošná oprava:** (1) které nástroje jsou živé (`_analyza\_registr-bran.json`, odkazy z `AGENTS.md`/`HANDOFF.md`), (2) pro živé zavést **jeden modul `_analyza\cesty.py`** (env → config → odvození), (3) mrtvé jednorázovky z 2. 10. **archivovat, ne opravovat** | Plošná oprava 138 výskytů je drahá a většina těch skriptů se už nikdy nespustí. **Archivace je taky rozhodnutí** — a patří do něj zapsat, co se archivovalo |
| **D6** | Které dokumenty jdou s orchestrou a které zůstanou stanici? | S orchestrou: `HANDOFF`, `KRONIKA`, `PLAN-*`, `ANALYZA-*ORCHESTRA*`, `IMPLEMENTACE-*`, `ZADANI-*`, `NEXT-SESSION-INSTRUKCE`, `PLAN-DALSI-KROK`, `ORCHESTRA-STAV-A-ANALYZA`, `FORGE-ORCHESTRA-MOZNOSTI`, `SKILLY-AKTUALIZACE`, `PROMPT-NOVA-SESSION`, `SOUBEH-SESSION-NALEZY`, `JAK-PSAT-DESIGN-*`<br>Zůstává stanici: `README`, `POZOR-E-DSH-NEMAZAT`, `ANALYZA-EFEKTIVITY-DSH`, `DEPLOY-VYLEPSENI`, `token-saving-*`, `sdxl-*`, `RESEARCH-public-repos`, `ANALYZA-VYVOJ-APLIKACI-A-HER`, `ZADANI-CREATOR-INDIKATORY` | ⚠ **Pozor na tři dokumenty, které projektová pravidla citují:** `MOZNOSTI-AGENTA.md`, `OTEVRENA-TEMATA.md`, `PREDAVANI-SESSION.md`. Když zůstanou stanici, musí na ně orchestra odkazovat **absolutní cestou** — a to je vědomé rozhodnutí, ne opomenutí |
| **D7** | Godot | Jde s orchestrou (`orchestra\tools\godot\`, ~172 MB); v `hra.cmd:13` nahradit fallback `..\..\orchestra\...` proměnnou `FORGE_GODOT` (už existuje) | Dnes je to **jediná vazba hra → orchestra** a je to vazba špatným směrem |
| **D8** | `.secrets` | Jde s orchestrou (je v jejím repu, kryté `.gitignore`) | ACL se tím **neopraví** — SID se dědí z rootu workspace (nález **S9**). Samostatný nález, ne součást přesunu |
| **D9** | Co s `E:\Workspaces\game-clone` a `C:\idle-realm`? | Mimo tenhle přesun; jen **napsat `AGENTS.md`** (oba jsou git repy bez něj → jejich session dnes nedostanou žádná projektová pravidla) | Je to jiná práce, ale je to **tatáž vada**, kterou přesun řeší u orchestry |

### 10.3b ✅ ROZHODNUTÍ UŽIVATELE (4. 10. 2026, ~20:0x UTC) — **závazná**

> **Co je v tabulce níž:** rozhodnutí, která **padla** — ne návrh. U každého je
> **čím je doložené** a **co se stane, kdyby se rozhodlo opačně**. Tabulka
> v §10.3 zůstává jako záznam o tom, co se navrhovalo.

| # | **ROZHODNUTO** | Doloženo měřením (4. 10. 2026) | Kdyby opačně |
|---|---|---|---|
| **D1** | Složky **`forge-orchestra`** a **`uo-shadows`** — shodné s názvy rep | Obě cílové složky existují a jsou **prázdné** (0 položek); repa na GitHubu se jmenují `forge-orchestra` a `uo-shadows` | Přejmenování **později** uživatel nedělá — dokumentace: *„a moved or deleted folder — cannot join and stays ungrouped"* a *„Re-adding a directory starts fresh"*. Session se **odpojí**, ne přesune |
| **D2** | **DVA samostatné workspaces**, každý = kořen svého repa | Dokumentace `dsh-agent-instructions`: `projectRootMarkers` default **`['.git']`** a řetězec se načítá **od projektového rootu k cwd**. Repo bez `AGENTS.md` → **nenačte se nic** (kromě obecných pravidel z `DSH_HOME`) | Kdyby workspace byl „kontejner" a repo v podadresáři, `AGENTS.md` v kořeni **se nenačte** — a agent přijde o projektová pravidla |
| **D4** | `FORGE_HRA` (env) + `--hra`, **výchozí `..\uo-shadows`** (sourozenec) | ⚠ **Oprava plánu:** `FORGE_HRA` **v kódu neexistuje** (nalezen jen v dokumentech) — zavádí se nově. Výchozí hodnota v §5 G3.2 (`..\games\uo-shadows`) je **po přesunu neplatná cesta**; platí `..\uo-shadows` | Zápis do hry zůstane uvnitř jednoho workspace jen tehdy, kdyby oba repa byla v jednom workspace — což D2 zamítlo |
| **D4b** | **Zápis mimo workspace = schvalování U 3 nástrojů, ne 4** | **Naměřeno:** `install-into-repo.ps1:34` odvozuje `$ProjDir` z **rodiče repa** (`Split-Path $PSScriptRoot -Parent`) → dnes by hledal `C:\Users\Ssevc\Local-Deepseek\projects\<Projekt>\project.godot`, a **`projects\` v workspace NEEXISTUJE** (nikde ve stromě) → nástroj **dnes neběží vůbec**. Živé jsou **3**: `sync-sablona-hra.py:45`, `kontrola-driftu.mjs:148,186`, `asset-fetch.mjs:157–158` | Kdyby se `install-into-repo.ps1` opravil a používal, přibyl by **čtvrtý** zápis mimo workspace — a **odvozená** cesta, kterou sken přímých cest **nevidí** |
| **D5** | **Archivovat 99, opravit 18 živých** + zavést `_analyza\cesty.py` | **Naměřeno:** v `_analyza\` má pevnou cestu **117 kódových souborů** (1,2 výskytu na soubor); v `AGENTS.md` je jako živých zmíněno **18**; **99 nezmíněných**; `_registr-bran.json` zná 12 bran | Plošná oprava 117 souborů platí za kód, který se už nikdy nespustí — a oddaluje přesun |
| **D6** | **Dokumenty stanice zůstávají stanici**; brány orchestra dostanou **druhý root `STANICE`** | Smíšenost naměřena: `MOZNOSTI-AGENTA.md` **9** zmínek orchestra, `OTEVRENA-TEMATA.md` **23** orchestra + **26** DSH, `PREDAVANI-SESSION.md` **2**. Zároveň je čtou **dvě brány orchestra** přes jeden `WS` root (`kontrola-diakritiky.py:16–153` ruční seznam, `over-dokumentaci.py:137,181`) | Kdyby šly s orchestrou, stanice přijde o ledger otevřených témat (týká se i DSH a obrázků); kdyby zůstaly **a** brány nedostaly druhý root, obě brány po přesunu **spadnou na `NENAŠEL`** |
| **D7** | **Godot se stává OBECNÝM nástrojem stanice** → `E:\Tools\godot\` (mimo oba repa); `hra.cmd` dostane **funkční fallback** + `FORGE_GODOT` jako override | **Naměřeno, že je to levné:** CI na `tools/godot/` **nezávisí** — `.forge\install-godot.sh` si Godot stahuje a nastavuje `FORGE_GODOT`, všechny workflow používají `"$FORGE_GODOT"`, `worker.mjs:79` čte `process.env.FORGE_GODOT`. Na pevnou cestu `tools\godot\` sahají **4 živá místa**: `test-local.ps1:54–56`, `validate-all.mjs:118`, `verify-setup.py:37`, `hra.cmd:13` (+ README, `.gitignore`, 3 komentáře v testech hry) | ⚠ **Opačná varianta (jen `FORGE_GODOT`) by launcher ROZBILA:** hra **nemá** `.forge\node\.env` (existuje jen v `orchestra\repo\.forge\node\.env`, a v herním repu je `.forge/node/.env` **gitignorováno**) a `hra.cmd` **.env vůbec nečte** → v čerstvém klonu by proměnná byla prázdná a `hra.cmd` by skončil „Godot nenalezen" |
| **D8** | `.secrets` **jde s orchestrou** (je v jejím repu, kryté `.gitignore`); **ACL se tím NEOPRAVÍ** — samostatný nález | **Naměřeno `icacls`:** `orchestra\.secrets` má **stejná** děděná práva jako root workspace, včetně sandbox-write SID `S-1-4-957149736-827513059` s právy **`(W,D,DC)`** = zápis, mazání, mazání potomka | Kdokoli smí zapisovat do workspace, smí zapisovat i do `.secrets`. Ochrana je dnes **jen `.gitignore`** — a to je vlastnost **rootu**, ne projektu |
| **D9** | `E:\Workspaces\game-clone` a `C:\idle-realm` = **samostatný úkol, teď ne** | Oba mají `.git`, oba **`AGENTS.md` nemají** → jejich session dostanou jen obecná pravidla. (`E:\Workspaces\game-recovery` **není** repo — je to adresář s jediným `acl-report-*.jsonl`.) | Kdyby se psaly během přesunu, mísí se dvě práce a nedá se rozlišit, co rozbil přesun |

**Co validace **ne**rozhodla a proč:** nic. Všech devět je rozhodnutých;
u **D4b** a **D7** měření **změnilo obsah rozhodnutí** (ne počet nástrojů a ne
umístění Godotu) — přesně proto se validace dělá před přesunem.

### 10.4 Kroky (pořadí je závazné)

| # | Krok | Hotovo znamená |
|---|---|---|
| **P0** | **Předpoklad: čisté pracovní stromy.** Dnes orchestra **2 necommitnuté soubory** (`tools/over-dokumentaci.py`, `tools/kontrola-diakritiky.py` — přepojení bran ze 4. 10.). Commitnout **s vyžádaným souhlasem** | `git status --porcelain` → prázdné v **obou** repech |
| **P1** | Zapsat **inventuru cest** do souboru (kontrolní seznam): 208 výskytů v kódu, u každého rozhodnutí `opravit`/`archivovat` | Soubor existuje; počty sedí na `_analyza\sken-cest-celek.py` |
| **P2** | Rozhodnout **D1–D9** (uživatelem) a zapsat rozhodnutí sem | Tabulka rozhodnutí je vyplněná, ne „návrh" |
| **P3** | **Změřit a zapsat** počet souborů a velikost obou stromů (`orchestra` ~1,07 GB / 4 692 souborů; hra 15,5 MB / 1 577) | Čísla **před** přesunem zapsaná |
| **P4** | **Ověřit cílové cesty** (`Resolve-Path`, že jsou to prázdné adresáře na `E:`) a volné místo (E: 810 GB) | Cesta je ověřená **před** zápisem, ne po něm |
| **P5** | **Přesun** `robocopy /MOVE /XJ /E` pro oba stromy | Počet souborů a velikost **po** = čísla z P3 |
| **P6** | **Ověřit oba `.git`**: `rev-parse --show-toplevel` sedí na novou cestu, `git status` má stejný počet řádků jako před přesunem | Oba repy v pořádku, historie nedotčená |
| **P7** | **Žádná junctiona na staré místo** (záměr): cesty mají **spadnout nahlas**, ne fungovat dál | `Test-Path C:\Users\Ssevc\Local-Deepseek\orchestra` → **False** |
| **P8** | **Opravit cesty** podle P1 (jen `opravit`), včetně `FORGE_HRA` a `verify-setup.py` | `grep` na `Local-Deepseek` v kódu obou rep → **0** (kromě archivovaných) |
| **P9** | **`AGENTS.md` do obou repů**: orchestra = projektová pravidla z rootu `Local-Deepseek` (přesun, ne kopie); hra = nová, malá (design, smlouvy, brány hry) | Soubory existují **a jsou načtené** (ověřeno v nové session) |
| **P10** | **Zaregistrovat workspace** (`E:\Workspaces\forge-orchestra`, `E:\Workspaces\uo-shadows`) a **otevřít v nich nové session** | Nová session vidí správná pravidla; staré session zůstávají v `Local-Deepseek` (přesunout je **nelze** — §10.5) |
| **P11** | **Spustit brány z nového místa** a porovnat s referencí (`HANDOFF.md` §6) | Čísla sedí; co nesedí, je regrese přesunu |
| **P12** | Zapsat provedení sem (§11) + do `KRONIKA-PROJEKTU.md` | Záznam existuje |

#### Co validace mění v krocích P0–P12 (jinak platí tabulka výš)

| Krok | Změna | Proč (naměřeno) |
|---|---|---|
| **P0** | **Beze změny** — orchestra má **2** necommitnuté soubory (`tools\kontrola-diakritiky.py`, `tools\over-dokumentaci.py`) | ✅ ověřeno živě: `git status --porcelain` v orchestra = 2× ` M`, hra čistá. *(Plán §5 G1.2 mluví o „15 M + 60 ??“ — to bylo 1. 10., dnes neplatí.)* |
| **P1** | Inventura **po SOUBORECH (176)**, ne po výskytech (208); u každého `opravit` / `archivovat` | §10.2b: `_analyza\` 117, `orchestra\` 51, root 5, stanice 2, hra 1 |
| **P1b** | **NOVÝ KROK: dohledat ODVOZENÉ cesty** — skript, který hledá `PSScriptRoot`, `Split-Path … -Parent`, `import.meta.url`, `__file__`, `parents[1]` a **vypíše, kam odvozují** | Sken přímých cest **nemůže** vidět `install-into-repo.ps1:34` (`$ProjDir` z rodiče repa) — a přesně ten je dnes mimo provoz, protože `projects\` neexistuje |
| **P3** | Přeměřit velikosti **znovu** — čísla v P3 jsou zastaralá | Naměřeno 4. 10. 20:0x: orchestra **5 447 souborů / 1 176,4 MB** (plán tvrdil ~4 692 / ~1,07 GB), hra **1 787 souborů / 16,1 MB** (plán 1 577 / 15,5 MB) |
| **P4** | Volné místo na `E:` = **810,8 GB** ✅ (změřeno `System.IO.DriveInfo`; ⚠ `Get-PSDrive E` hlásí u této stanice **0 GB** — je to artefakt, ne stav disku). Cílové složky **existují a jsou prázdné** ✅ | `E:\Workspaces` navíc obsahuje `game-clone` (repo) a `game-recovery` (JSONL, není repo) |
| **P5** | **PŘED přesunem** vyndat `orchestra\tools\godot\` (172 MB) do `E:\Tools\godot\` (D7) — ať se nepřesouvá dvakrát | `orchestra\.gitignore:38` `tools/godot/`; Godot **není** v gitu (nad limit GitHubu 100 MB/soubor) |
| **P8** | Navíc: `FORGE_GODOT` do `test-local.ps1`, `validate-all.mjs:118`, `verify-setup.py:37`, `hra.cmd:13` (D7) a **druhý root `STANICE`** do `kontrola-diakritiky.py` + `over-dokumentaci.py` (D6) | D6/D7 |
| **P8b** | **NOVÝ KROK: archivace** `_analyza\_archiv\` (99 souborů) **před** opravou cest + `_analyza\cesty.py` pro živé | D5 |
| **P8c** | **NOVÝ KROK: `.gitignore`** pro `_analyza\`: `_inventar.json`, `snapshot-*`, `ci-rozbal*`, `tmp-*`, `*-scratch\`, `_zaloha*`, `handoff-pred-*`, `*vystup.txt` | Jinak by se do **veřejného** repa commitly CI logy, snapshoty a zálohy handoffu (naměřeno: `_inventar.json` 1×, `a-ukol-scratch\.forge\vision\baseline.json` **272×** 64znakový hash, `ci-rozbal2\ci-*` logy) |
| **P9** | Dokumenty **+ 18 živých nástrojů** commitnout; archiv **gitignorovat** (D3) | Oba repa jsou **VEŘEJNÁ** (`private=false`). Sken tajemství: **čistý** — skutečná tajemství jsou jen v `orchestra\.secrets\` (gitignorováno), v kandidátech jen SHA-256 hashe a zmínky o `cf-secrets.json` |
| **P10** | **Dva** workspaces (`E:\Workspaces\forge-orchestra`, `E:\Workspaces\uo-shadows`) — session se **nepřesouvají**, staré zůstanou v `Local-Deepseek` | D2 |

### 10.5 Co přesun NEUDĚLÁ (a nesmí se od něj čekat)

- **Nepřesune existující session.** Dokumentace `@deepseek-ai/dsh-workspace`:
  session patří projektu podle **zaznamenaného adresáře** a *„a session from
  another directory cannot be moved in"*. Staré session zůstanou
  v `Local-Deepseek`; nové vzniknou v nových workspaces.
- **Nezlepší orchestra session.** Naměřeno: řetězec instrukcí je dnes
  **41 779 B (63,7 % rozpočtu)** a po přesunu bude v orchestra session
  **stejný** (obecná + projektová pravidla potřebuje pořád). Úspora je pro
  **ostatní** workspaces (64,4 % → 27,5 %).
- **Nevyřeší souběh session.** Ten je o domluvě, ne o cestách.
- **Nesmí se dělat po částech.** Přesun s polovinou cest opravených je horší
  než nepřesunuté — nedá se rozlišit, co rozbil přesun a co bylo rozbité před ním.

### 10.6 Rizika a návrat

| Riziko | Obrana |
|---|---|
| `robocopy /MOVE` selže uprostřed → část stromu na obou místech | Čísla z P3 zapsaná předem; po přesunu porovnat. `git status` v obou repech je druhý nezávislý důkaz |
| Nástroj tiše přestane nacházet soubory | P8 má za „Hotovo znamená" **grep na 0**, ne „funguje to" |
| Ztratí se znalost, proč co bylo | Dokumenty se **přesouvají**, ne přepisují; historické citace cest se nechávají |
| Návrat | **Před P5 zkopírovat** `_analyza\zaloha\` (včetně `AGENTS.md.pred-presunem-2026-10-04.md`) mimo oba stromy; `robocopy /MOVE` je vratný přesunem zpět, dokud se necommituje |

**Rollback jedné věty:** dokud se necommitne a nepushne, je návrat `robocopy /MOVE` opačným směrem.

---

### 10.7 ZÁZNAM O VALIDACI (4. 10. 2026, 19:5x–20:1x UTC) — ✅ **plán je proveditelný**

> **Co tenhle oddíl JE:** **záznam o provedení** validace — co se spustilo,
> co to naměřilo a co to vyvrátilo. Není to plán ani stav. Zadání bylo
> v `NEXT-SESSION-INSTRUKCE.md` (verze pro plánovací session).
> **Data se nedotčeno:** přesun se neprováděl, nic se nepřesunulo ani nesmazalo.

**Devět bodů V1–V9 ze zadání — spuštěno, ne čteno:**

| # | Tvrzení | Příkaz | Výsledek |
|---|---|---|---|
| **V1** | Obecná pravidla jsou v `DSH_HOME` a nic nezmizelo | `python _analyza\ag-presun-uplnost.py` | ✅ **47/47**, 0 zmizelých, **2 kalibrační sondy se nenašly** (hledá se správně) |
| **V2** | Brány po přesunu pořád měří | `python _analyza\ag-over-cisla.py` + `ag-mutace.py` | ✅ `exit 0`; **2 mutace, 2 chyceny**; `INFO: 1 tvrzení … v OBECNÝCH pravidlech` |
| **V3** | Cena přesunu | `python _analyza\sken-cest-celek.py` | ⚠ **KÓD 208 ✅**, ale DOKUMENTY **128** (ne 117), celkem **336/219** (ne 325/218). **Přeměřeno dvěma přísnějšími vzory** → §10.2b |
| **V4** | Do hry zapisují 4 nástroje | `python _analyza\skryte-vazby-na-hru.py` + **čtení souborů** | ⚠ **13 kandidátů; potvrzeny 4 — ale jen 3 jsou živé.** `install-into-repo.ps1` **dnes neběží** (`projects\` neexistuje). Ověřeno čtením: `sync-sablona-hra.py:45` (`cil = HRA / rel`), `kontrola-driftu.mjs:148,186` (`b = join(cil, f)`, `cil = ROOT/games/<hra>`), `asset-fetch.mjs:157–158` (`writeFileSync(cil, data)`) |
| **V5** | `.git` v obou repech, `AGENTS.md` ani v jednom | `Test-Path` na 4 cesty | ✅ `.git` **True/True**, `AGENTS.md` **False/False** |
| **V6** | Cílové složky existují a jsou prázdné | `Get-ChildItem -Force` | ✅ **0 položek** v obou |
| **V7** | Session nelze přesunout mezi workspaces | `_asar_probe\readmes\dsh__node_modules__@deepseek-ai__dsh-workspace__README.md` | ✅ řádek **172**: *„a session from another directory cannot be moved in"*; řádek **173**: přesunutý/smazaný adresář → session *„stays ungrouped"*; řádek **176**: *„Re-adding a directory starts fresh"*. Registry umí create/order/delete/archive/restore, **přesun session mezi projekty neexistuje** |
| **V8** | Rozpočet instrukcí po přesunu | `Get-Item … .Length` | ✅ root **23 727 B** + `DSH_HOME` **18 052 B** = **41 779 B** = **63,7 %** z 65 536 |
| **V9** | Živý stav obou repů | `git rev-parse HEAD`, `git status --porcelain`, `node orchestra\tools\zjisti-pages.mjs` | ✅ orchestra **`c2f730f` + 2 změněné** (` M tools/kontrola-diakritiky.py`, ` M tools/over-dokumentaci.py`), hra **`0fdc784` čistá**, `origin/main..HEAD = 0/0`; poslední `release.yml` **#76 completed/success** na `0fdc784` |

#### Co validace VYVRÁTILA nebo OPRAVILA (to je její výsledek)

| # | Co plán tvrdil | Naměřeno | Druh vady |
|---|---|---|---|
| **1** | „4 nástroje do hry zapisují" | **3 živé**; čtvrtý (`install-into-repo.ps1`) **dnes neběží**, protože `projects\` v workspace **neexistuje** | **zastaralé** |
| **2** | `FORGE_HRA` je „odkaz orchestra → hra" | v **kódu neexistuje** — jen v dokumentech (i ve dvou snapshotech). Zavádí se **nově** | **nepřesné** |
| **3** | Výchozí hodnota `..\games\uo-shadows` (§5 G3.2) | po přesunu je to **neplatná cesta**; platí `..\uo-shadows` (§10.3 D4) | **rozpor uvnitř plánu** |
| **4** | Godot „nahradit proměnnou `FORGE_GODOT` (ta už existuje)" | existuje **jen v `orchestra\repo\.forge\node\.env`**; **hra `.env` NEMÁ** a `hra.cmd` ho **nečte** → opačná varianta by launcher **rozbila** | **neúplné** |
| **5** | DOKUMENTY 117 / celkem 325 / 218 souborů | **128 / 336 / 219** (rozdíl jen v dokumentech — smějí zestárnout) | **zastaralé** |
| **6** | P3: orchestra ~4 692 souborů / ~1,07 GB | **5 447 / 1 176,4 MB**; hra **1 787 / 16,1 MB** | **zastaralé** |
| **7** | „Cena přesunu = 208 výskytů v kódu" | **208 je počet výskytů, ne práce.** Pracovní jednotka je **176 souborů**; navíc volný vzor počítá i prózu (208), přísný míjí kořenové cesty (100) | **měřidlo je slabé** |
| **8** | Krok P1 = „inventura cest" | chybí **odvozené cesty** (`Split-Path -Parent`, `PSScriptRoot`) — přesně ta třída, která dnes drží `install-into-repo.ps1` mimo provoz | **chybějící krok** |

**Co se naopak POTVRDILO (a je to dobrá zpráva):**
`KÓD 208` přesně (reconcile: 142 výskytů v `_analyza` KOD − 4 ve `snapshot-*`,
které sken přeskakuje = **138** ✅); `.git`/`AGENTS.md`; prázdné cíle;
nemožnost přesunu session; rozpočet instrukcí; živý stav repů i Pages;
`E: 810,8 GB` volných; **`.secrets` má stejná práva jako root včetně sandbox SID
`(W,D,DC)`** (nález S9 — potvrzen `icacls`); **CI na `tools/godot/` nezávisí**.

#### Vlastní omyly téhle validace (do `HANDOFF.md` §8)

| # | Co jsem si myslel | Naměřeno |
|---|---|---|
| **129** | „Přesun rozbije `install-into-repo.ps1`" (odvozená cesta z rodiče repa) | **Nerozbije — je rozbitý už dnes:** `projects\` v workspace neexistuje. Hypotéza byla správná o třídě vady a **špatná o jejím důsledku**; zapsal jsem ji jako „zastaralé", ne jako „přesun to zlomí" |
| **130** | „`Get-PSDrive E` → **0 GB volných**, přesun je nemožný" | Artefakt: `Get-PSDrive` u této stanice hlásí `Free=0/Used=0`, kdežto `System.IO.DriveInfo` **810,8 GB**. **Málem jsem z toho udělal blokující nález** — zachránilo to druhé měření (`Get-CimInstance`/`Get-Volume` jsou navíc v sandboxu `Access denied`) |
| **131** | „Přísné měřidlo (`Local-Deepseek` + oddělovač) je ta správná cena" | **Také ne:** mine kořenové cesty `Path(r"C:\...\Local-Deepseek")`, kterých je v `_analyza` většina. Obě krajní čísla (208 / 100) jsou špatná; správná jednotka je **počet souborů** |

#### Jak validaci zopakovat (spustitelné)

```
python _analyza\ag-presun-uplnost.py          # 47/47, 0 zmizelých
python _analyza\ag-over-cisla.py              # exit 0, 0 rozchodů
python _analyza\ag-mutace.py                  # 2 mutace, 2 chyceny
python _analyza\sken-cest-celek.py            # KÓD 208, DOKUMENTY 128
python _analyza\skryte-vazby-na-hru.py        # 13 kandidátů
node   orchestra\tools\zjisti-pages.mjs       # release.yml #76 na 0fdc784
```
Měření pracovní jednotky (176 souborů) a obou přísnějších počtů je v §10.2b;
postup je tam popsaný větou, ne odkazem na skript — je to **jednorázové
přeměření**, ne nový nástroj.

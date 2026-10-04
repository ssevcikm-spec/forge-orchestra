
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
## 21. Provedeno 2. 10. 2026 (16:1x–19:0x UTC) — AKČNÍ session: granule `tests.harness`, projití složky, úklid

> **Co je tenhle oddíl:** **záznam o provedení**. Není to plán ani stav —
> je to doklad, **co se změnilo, čím to bylo změřeno a co se změřit NEDALO**.
> **Zadání** bylo `NEXT-SESSION-INSTRUKCE.md` (verze z 16:10, `1a1ff48` /
> `c40bdd5`); **jeho kontrola obstála** (`zadani-kontrola.py` → `exit 0`,
> tvrzené commity = živé HEADy) — ale **tři jeho tvrzení o číslech neseděla**
> (§21.1). **Vlastní omyly této session jsou v §8h (72–79).**

### 21.1 Kontrola zadání — hlavička sedí, tři čísla ne

| Co zadání tvrdilo | Naměřeno | Verdikt |
|---|---|---|
| `orchestra` = `1a1ff48`, `uo-shadows` = `c40bdd5`, oba pushnuté a čisté | `1a1ff4860` a `c40bdd556`; `origin/main..HEAD = 0`; `status --porcelain` **prázdný** v obou | **OK** |
| `kronika-kontrola.py` → „musí vyjít exit 0 (**62 omylů**)" (§1.3) | `exit 0`, ale **66 omylů** (13+10+5+6+11+10+11) | **číslo v zadání je zastaralé** — 62 bylo naměřeno před připsáním omylů 61–71 (§8g). Není to vada: **počet omylů roste s každou session** |
| `g3-brany.py` → „**29 bran, 1 nenulový exit**" (§1.3) | **29 bran, 2 nenulové exity** — navíc `validate-all (CELEK)` | **NEPRAVDA** — a je to **prostředí**, ne kód: viz §21.6 |
| `mutace A: pres-level` = „**65/1**" (§2.1) a „`1-baseline` **59/0**" (§18.3) | tenhle runner dává základ **61/0** a s mutací **61/1** | **jiný čítač téhož jména**: `a-mutace-run.py` testuje **jen Úkol A** vlastním patchem, klon má navíc blok Úkolu B (§8h, omyl **79**) |
| `orchestra` = **`f5b1ea0`** (§3 Úkol 2 a §6) | `f5b1ea0` **existuje** (`cat-file -t` → `commit`), ale **není HEAD** — je to předchůdce `1a1ff48` | **zadání si na dvou místech odporuje** (hlavička `1a1ff48`, §3/§6 `f5b1ea0`); platí hlavička |
| `git worktree list` = „tři záznamy" (§3 Úkol 4) | **tři** (hlavní, `a-ukol-scratch`, `merge-scratch`) | **OK** |
| `roadmap.json` má 21 granul, žádnou s „harness" (§3 Úkol 1) | **21**, „harness" 0× | **OK** |
| baseline `lint-roadmapa` = „11× `[5]`, 13 z 21" (§3 Úkol 1) | **14 problémů**: 3× `[3]` + **11× `[5]`**, `13 z 21` bez `size_lines` | **OK do puntíku** |

**Postup:** `python _analyza\zadani-kontrola.py` → `exit 0` · `python _analyza\kronika-kontrola.py` → `exit 0` · `python _analyza\handoff-kontrola-uplnost.py` → **83/83** · `git rev-parse HEAD` v obou repech · `python orchestra\tools\lint-roadmapa.py` (před změnou).

> **Pravidlo, které z toho plyne (a je měřené):** zadání psané plánovací session
> **neslo tři čísla, která v době čtení neplatila** — a **všechna tři vypadala
> jako měření**. Ani jedno nebylo lež: dvě zestárla (počty rostou) a jedno bylo
> **z jiného čítače**. Kdo je čte bez postupu, buď jim uvěří, nebo je „opraví"
> špatně.

### 21.2 Úkol 1 — granule `tests.harness` a lék na M3 (nález H12)

**A) Granule je v `.forge/roadmap.json` (22 granul, dřív 21):**

| Pole | Hodnota |
|---|---|
| `id` | `tests.harness` |
| `owns` | `["tests/run_tests.gd"]` — a **nic ze `scripts/`** |
| `size_lines` | `"<= 1200"` (soubor má **1 205** řádků, po mé úpravě) |
| `model` | `strong` |
| `acceptance` | `["tests"]` |
| `depends_on` | `["sim.combat", "core.attributes", "core.skills"]` |
| `prompt` | **2 080 znaků**, všech 7 naměřených pastí (VOLAT kód, každá kontrola umí spadnout, atrapa v rozporu, netestovat granule, které nejsou `done`, zákaz `scripts/`, naměřená hodnota v hlášení, `SceneTree._process()`, nenulový exit) |

`lint-roadmapa.py` **před** → 21 granul, 14 problémů (3× `[3]`, 11× `[5]`), `13 z 21`.
`lint-roadmapa.py` **po** → 22 granul, **14 problémů (tytéž)**, `13 z 22`. **Počet varování se nezměnil** (kritérium zadání) — a je vidět, že **nová granule je v přehledu** (`strong: 8 → 9`, `core.skills` a `sim.combat` mají o jednoho čekajícího víc).

**B) Lék na M3 je v `tests/run_tests.gd` — a je doložený mutací:**

Kontrola „atributy přes `hodnota(attr)`" dřív tvrdila jen `damage > 0`. To **splní i hodnota 4**, takže mutace M3 (vypuštění větve `hodnota()`) prošla — nález **H2/H12**. Teď je tam **atrapa v rozporu se sebou samou**:

```
TestAtributyHodnota:  hodnota("Str") = 100   vs.   vlastnost Str = 10
TestSkillyHodnota:    hodnota("boj_na_blizko") = 100  vs.  vlastnost 0
```

- **s větví `hodnota()`** → `sila = 100` → `1 + 100/10 = 11`, `+3` zbraň, `−1` zbroj → **damage = 13**
- **bez větve** (jen vlastnost) → `sila = 10` → `1 + 1 = 2` → **damage = 4**

Kontrola teď tvrdí **rovnost 13** (ne „> 0") a přidává **druhý, nezávislý důkaz**: čítač `vetev_hodnota` uvnitř atrapy. **Nula znamená „ta větev se nevolala"** — i kdyby obě dávaly stejné číslo.

**Důkaz vlastním spuštěním** — `python _analyza\t1-m3-brana.py` (nový nástroj, `exit 0`; běží nad **vlastním** worktree `_analyza\t1-kladna`, klonu se nedotkne):

| Běh | Co je v `combat.gd` | Naměřeno |
|---|---|---|
| A | zdravý kód, **bajt na bajt z klonu** | **65 kontrol, 0 selhání** (`exit 0`) |
| B | **M3**: vypuštěná větev `if komponenta.has_method("hodnota")` | **65 kontrol, 2 selhání** (`exit 2`) — `damage = 4` místo 13 a `volání: 0` |
| C | návrat zdravého kódu | **65 kontrol, 0 selhání** (`exit 0`) |

**Měřená podmínka se ověřuje PŘED během i PO něm** (`M3_NAJDI not in cti(COMBAT)`) — bez toho by „mutace se tiše neprovedla" vypadalo jako „brána je slepá". **Běh C je tam proto, aby rozchod nebyl ve stromě, ale v bráně.**

**Klidný stav klonu po celou dobu:** testy v klonu dávají **65/0** (před úpravou **64/0** — kontrola se **zpřesnila a jedna přidala**, ne že by jich ubylo).

### 21.3 Úkol 3 — ruční seznamy nahrazeny projitím složky (nález S27, po dvanácté)

**A) `_analyza\g1-diakritika-novych.py` — seznam 190 cest ZRUŠEN, prochází se složka.**

| Kořen | Vzory |
|---|---|
| kořen workspace | `*.md` |
| `_analyza/` | `*.md`, `*.py`, `*.mjs`, `*.json`, `*.gd`, `*.txt`, `*.ps1` |
| `orchestra/tools/` | `*.py`, `*.mjs` |

**Naměřeno: `ZMĚŘENO: textových souborů=405, přeskočeno jako binární=5, vad=0`** (dřív se kontrolovalo **127** souborů ze seznamu). Binární soubory se **vypíšou počtem** — tiché přeskočení je přesně ta vada, před kterou ten skript vznikl.

**B) `orchestra\tools\kontrola-diakritiky.py` — skilly projitím `~\.dsh\skills\*\SKILL.md`.** Ručních 12 cest nahradil `sorted(SKILLS_DIR.glob("*/SKILL.md"))`; prázdná složka **není ticho** (vypíše `CHYBA … žádné skilly k projití`). **Naměřeno: 12 skillů na disku = 12 otevřených** (dřív jich seznam měl **5** — chyběl i `overovani`, do kterého táž session psala).

**C) Dva NALEZENÉ NÁLEZY (ne falešné poplachy) — a jsou to vady podle `AGENTS.md`:**

| Nález | Co | Kde |
|---|---|---|
| **H14** | **Doslovná ukázka rozbitého kódování v docstringu** — `AGENTS.md` ji zakazuje a přesně kvůli tomu pravidlo vzniklo | `orchestra\tools\oprav-ps1-kodovani.py` (řádek 7) a `orchestra\tools\over-dokumentaci.py` (řádek 4) |
| **H15** | **Brána diakritiky neviděla 7 z 12 skillů** (ruční seznam 5 cest) | `orchestra\tools\kontrola-diakritiky.py` |

Oba nálezy **opraveny**: ukázky jsou popsané **slovem** („z jednoho písmene s diakritikou se stanou dva znaky") a skilly se procházejí. Po opravě `g1` → `vad=0`, `kontrola-diakritiky.py` → `VŠE OK`.

> **⚠ Jak se to odlišilo od falešného poplachu (a stálo to tři kola, omyly 72–74):**
> brány **samy** obsahují rozbité znaky **jako vzorek** (musí, jinak by neměly co
> hledat). Kritérium proto **není tvar** („dva znaky po sobě") ani **parser**
> (půlparser selhal na jednosloupcových uvozovkách), ale **význam**: smí to být
> jen na řádku, který vzorek **definuje nebo používá** (`radky_se_vzorkem()`).
> Ukázka v docstringu tam nepatří — a to je vada.

### 21.4 Úkol 3.3 — mutační test kroniky S FIXTUROU (nález H12 → návrh NA15)

**Co chybělo:** `h17-kronika-mutace.py` testoval bránu **jen na ŽIVÉ kronice** — a ta v době testu neměla tvar, na kterém brána selhala (tabulka **nálezů** ve výřezu bloku omylů). Proto vada **prošla** a v praxi se projevila až u měření (**54 omylů místo 10**, §18.15).

**Nový nástroj: `python _analyza\t3-kronika-mutace.py`** → **`exit 0`**; fixtura má **tabulku nálezů** i **tabulku omylů**, takže ten tvar je v testu **řízeně**:

| Případ | Co se mění | Očekáváno | Naměřeno |
|---|---|---|---|
| **A** | zdravá fixtura (66 omylů) | `exit 0` | **`exit 0`** |
| **M1** | počet omylů 8g: 11 → 7 | spadne (část A) | **`exit 1`** — „kronika tvrdí 7, v HANDOFF.md je 11" |
| **M2** | doplněný **konec** nadpisu 8d | **projde** (kotva je prefix, 6 omylů) | **`exit 0`** |
| **M3** | do brány vpraveno kritérium **tvaru** `count("\|") != 4` | spadne | **`exit 1`** — všech 6 bloků hlásí 0 |
| **M4** | nález H2 → H99 v HANDOFFu | spadne (část B) | **`exit 1`** |
| **M5** | dvě tabulky za blokem 8g (omylů 11 + nálezů 3) | **projde** (počítá se 11) | **`exit 0`** |

**A při psaní toho testu se našla DVĚ další omezení brány (omyl 78) — obě opravena:**

1. **Chybějící nadpis bloku byl „naměřená nula".** `blok()` vrátí `""`, `pocet_omylu("")` vrátí **0** — a brána to vypsala jako **skutečný počet omylů: 0**. Přitom je to **NEZMĚŘENO**. Teď se přítomnost nadpisu (i koncové kotvy) měří **zvlášť** a nepřítomnost se hlásí jako `NEZMĚŘENO`.
2. **Blok v `HANDOFF.md`, který v kronice §3 řádek NEMÁ, se tiše přeskakoval** (`continue`). Přitom je to **přesně ta ztráta, kterou kronika hlídá** — ne zapsaný omyl zmizí navždy. Teď je to **ROZCHOD**.
3. **`%d` na `None` shazoval bránu tracebackem** místo aby rozchod vypsal. Brána, která na nález spadne, **hlásí míň** než brána, která ho vypíše.

**Živá kronika po všech opravách: `exit 0`** — `omylů 66, nálezů H 13, sessions 16, odkazů 15`.

### 21.5 Úkol 4 — úklid pracovního stromu

```powershell
& orchestra\tools\git.cmd -C games\uo-shadows worktree remove --force "$PWD\_analyza\merge-scratch"
& orchestra\tools\git.cmd -C games\uo-shadows worktree prune
```

- **Cesta ověřena PŘED smazáním** (`Resolve-Path` → `C:\Users\Ssevc\Local-Deepseek\_analyza\merge-scratch`, `rev-parse --short HEAD` → `aad1c8d`) — `AGENTS.md`: u mazání se cíl ověřuje, ne odhaduje.
- `merge-scratch` **odstraněn** (`exit 0`, složka na disku **neexistuje**).
- **`a-ukol-scratch` ZŮSTÁVÁ** — používá ho `g3-brany.py` a `a-mutace-run.py`.
- `t1-kladna` je **můj** worktree pro důkaz M3; uklizen na konci session (§21.8).
- `git status --porcelain` v klonu hry je **stejný jako před prací** — jen **2 soubory**, které jsem změnil **já** (`tests/run_tests.gd`, `.forge/roadmap.json`).

### 21.6 Brány — co každá otevřela (past S27)

`python _analyza\g3-brany.py` → **29 bran, 2 nenulové exity**:

| Brána | Otevřela | Výsledek |
|---|---|---|
| `testy hry (Godot)` — klon | **65 kontrol** | 0 selhání (**před úpravou 64/0**) |
| `mutace A (5 běhů)` | **61 kontrol** | `exit 0` |
| `mutace A: pres-level` | 61 kontrol | **`exit 1` — a to je SPRÁVNĚ** (mutace se má chytit) |
| `diakritika nových souborů` | **405 souborů** (dřív 127 ze seznamu) | `exit 0`, `vad=0` |
| `diakritika (brána)` | **36 299 znaků** | `exit 0` (skilly projitím složky) |
| `kronika úplnost` | **66 omylů** | `exit 0` |
| `kronika mutace (5 běhů)` | **6 případů** | `exit 0` |
| `lint-roadmapa` | **22 granul** | `exit 0` — **14 problémů, 11× `[5]`, 13 z 22** |
| `validate-all (CELEK)` | sekce A–L | **`exit 1` — NEPROBĚHLO (PROSTŘEDÍ)** |
| ostatní (C1, C2, n1, a1–a2, a3, n8, b5, ag-over, tsc, deploy, handoff, zadání…) | viz §18.13 | `exit 0` |

> **⚠ `validate-all` `exit 1` NENÍ REGRESE — je to třetí stav.** Naměřeno: padá na
> `PermissionError [WinError 5]` při zápisu do **přesměrovaného tempu sandboxu**
> (`…\Temp\dsh-…\schema-test-…\a-iso\assets\levels`) — tedy **před** tím, než
> dojde na kód. Je to **tatáž past** jako `dsh-prostredi` §4 a **není to červená**
> (brána, která neproběhla, je **nezměřená**). Zapsáno proto, aby to nikdo
> nečetl jako „validate-all se rozbil" — a aby se to **neopravovalo**.
> **Zadání tvrdilo „1 nenulový exit"; správně jsou dva** — a druhý je prostředí.

### 21.7 Co se ověřit NEDALO (přiznaná mez)

1. **Že `validate-all` projde mimo sandbox** — tvrdí to §18.13 (`✓ VŠE V POŘÁDKU`, 209× OK) a **nic tomu neodporuje**, ale v `workspace-write` jsem to **nezopakoval** (padá na tempu). Je to **nezávislé měření z jiného oprávnění**, ne moje.
2. **Že Aiderův obal má 5 357 tokenů** — je to **dopočet** z jednoho reálného běhu (§18.18), ne měření obalu.
3. **Že `prompt` granule `tests.harness` je pro agenta srozumitelný** — to se projeví až **během** granule. Text je měřený (2 080 znaků, 7 pastí), ale **srozumitelnost měřidlo nemá**.
4. **Budoucnost #145/#146** — rozhoduje conductor a čas (`RETRY_HOURS`).

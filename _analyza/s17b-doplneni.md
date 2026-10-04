
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 17.11 Doplněno na konci session — a jeden vlastní omyl, který vznikl PRÁVĚ TÍM

**1) Inventář jazyka jsem musel přegenerovat — a je to praktický důkaz §17.9/5.**
Naměřeno: po editaci `orchestra\tools\kontrola-diakritiky.py`
a `~\.dsh\skills\overovani\SKILL.md` (obojí je **vstupem skeneru**) spadly
**dvě brány**:

```
python _analyza\c2-mutace.py   → „1) ZDRAVÝ INVENTÁŘ … CHYBA: INVENTÁŘ JE
                                   ZASTARALÝ / NEZMĚŘENÝ … exit=1"
                                   → „brána neprojde ani ve zdravém stavu; končím" (exit 2)
python _analyza\n1-over-inventar.py → exit=2
```

**To NENÍ vada nástroje** — to je **přesně to chování, které má nastat**
(AGENTS.md: „nástroj nesmí tiše měřit zastaralý snapshot"). Opraveno
přegenerováním:

```
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
  → zapsáno: _analyza\_inventar.json (2075 nálezů)
python _analyza\hl-rizika-jazyka.py
  → otisk vstupů SEDÍ: 8b63136727b0194d (772 souborů) — inventář je z TOHOHLE kódu
  → PŘEJEDNANÝCH MÍST: 11, z toho VRÁCENÝCH: 0 → exit 0
```

> **⚠ POUČENÍ, které je zároveň nález:** stal jsem se **prvním, kdo na to
> narazil** — a **zabralo to jeden krok navíc, protože jsem věděl, co to je.**
> Kdo to neví, hledá vadu v nástroji. To je **silný argument pro §17.9/5**
> (pravidlo do `AGENTS.md`), protože jinak tahle zkušenost zůstane
> **jen v tomhle handoffu**, tedy ve **stavu**.

**2) Finální souhrn všech bran** (`python _analyza\g3-brany.py` na konci session):

| Brána | Otevřela | Výsledek |
|---|---|---|
| testy hry (Godot) — **klon** | **64 kontrol** | 0 selhání |
| mutace A | 5 běhů | 4× OK, 1× očekávaný `exit 1` |
| mutace B (combat) | 2 mutace | **2/2 chyceno** |
| C1: `a3-kontrola` | 50 úloh / 16 řádků | OK |
| C2: mutace N1 | 5 běhů | **5/5 dle očekávání** |
| diakritika (brána) | **34 803 znaků** (44 souborů, **12 skillů**) | `exit 0` |
| diakritika nových souborů (`g1`) | **52 souborů** | `exit 0` |
| handoff úplnost | **83 bodů** | **83/83** |
| zadání kontrola | 314 řádků zadání | `exit 0` |
| `over-dokumentaci` | 10 kontrol / **63 kontrol** | `exit 0` |
| `over-skilly` | **12 skillů** | `exit 0` |
| `lint-roadmapa` | 21 granul | **11× `[5]`, 13 z 21** |
| `check-schema` (hra) | **2026** | **`exit 1` — neproběhlo (prostředí)** |
| `test-cooldown` | 10 kontrol | 0 chyb |
| deploy B1 | GitHub API + živý conductor | `✓ VŠE V POŘÁDKU` |
| `ag-over-cisla` | 7 tvrzení (5+2) | 0 rozchodů |
| `validate-all (CELEK)` | sekce A–L | **`exit 1` — 3 problémy, všechny „neproběhlo (prostředí)"** |
| `tsc` (conductor) | typová kontrola | `exit 0` |

**`brán celkem: 27, s nenulovým exit: 3`** — a **všechny tři jsou
vysvětlené**: `mutace A: pres-level` má **správně** spadnout (je to mutace),
`check-schema` a `validate-all` jsou **„neproběhlo (prostředí)"** (mimo
sandbox dávají 17/24/36 kontrol a `exit 0`).

**3) Do brány diakritiky doplněny VŠECHNY skilly.** Naměřeno při přidávání:
na disku je **12 skillů**, ale v seznamu brány bylo **5** — chyběl i
**`overovani`**, tedy ten, do kterého táž session právě psala (§8.1/§8.2).
Brána by ho **nikdy neotevřela** a hlásila „VŠE OK". Doplněno
(`kontrola-diakritiky.py`, u každého je teď vidět počet znaků) — a je to
**po jedenácté** táž vada **S27** (ruční seznam).

**4) Nové dokumenty zapsané v obou branách** (a ověřeno, že je **vidí**):
`_analyza\s17-novy-oddil.md`, `_analyza\s8f-novy-oddil.md`,
`_analyza\s17b-doplneni.md`, `_analyza\c2-sonda-uvozovky.py` a všechny
`_analyza\h17-*` nástroje. `g1` teď kontroluje **56 souborů** (bylo 48)
a `kontrola-diakritiky.py` **44 souborů** (bylo 42).

**5) Poslední omyl téhle session (č. 59) stojí za zapsání zvlášť.**
Po editaci `kontrola-diakritiky.py` (přidání 7 skillů) jsem **musel inventář
přegenerovat ZNOVU** — protože i ten soubor je vstupem skeneru. Naměřeno:
`otisk vstupů` se posunul `8b63136727b0194d` → **`4f3d76c133c4d9c6`**.
**Není to vada** — je to **přesně to, co má nastat** — ale je to **druhý
výskyt téhož kroku v jedné session**, což je nejsilnější možný argument pro
pravidlo z §17.9/5: **kdo edituje kód, musí na konci přegenerovat inventář
(a někdy i dvakrát).**

**6) Všechny `*.md` oddíly a `h17-*` nástroje jsou v `g1`** — brána, která
se ptá **konkrétních souborů**, ne seznamu: naměřeno `VŠE OK — 56 souborů`
(bylo 48 před touhle session).

---

### 17.12 DODATEK (12:2x–12:5x UTC) — trvalá paměť projektu a postupu

> **Co je tenhle dodatek:** práce, kterou zadal **uživatel** po skončení
> ověření — a **není to ověřování cizí práce**, je to **změna postupu**.
> Proto je zapsaná zvlášť a s vlastním zdůvodněním.

**Nález, který to spustil (uživatel to pojmenoval přesně):**
*„Vím, že už se něco částečně dělá, ale nemám přehled."* Naměřeno: příběh
projektu se dal přečíst **jen z `HANDOFF.md`, který se při každém předání
přepisuje** — takže historie přežila **jen v odkazech** a v `SKILLY-AKTUALIZACE.md`
(který je o skillech, ne o projektu). **Přehled na jednom místě neexistoval.**

| # | Co vzniklo | Kde | Čím je to ověřené |
|---|---|---|---|
| **1** | **`KRONIKA-PROJEKTU.md`** — trvalá paměť: **14 sessions**, evidence nálezů (N/H/S/V/P), **evidence omylů s trendem**, 12 poučení s naměřenými případy, **12 návrhů se stavem**, mapa „kam se co zapisuje" | workspace root | `python _analyza\kronika-kontrola.py` → **`exit 0`** |
| **2** | **`_analyza\kronika-kontrola.py`** — měřidlo kroniky | `_analyza\` | Ověřeno **tím, že našlo dva skutečné rozchody** (viz omyl **60**) |
| **3** | **Stavový řádek 🟢/🟡/🔴** na konci každé session | `PREDAVANI-SESSION.md` **§2.1** | zapsáno do povinného výstupu (§2 bod 5, §7) |
| **4** | **Dvoukrokový proces návrhů** — session **zapíše**, příští **rozhodne** (`NEOVĚŘENO` → `APLIKOVÁNO`/`ZAMÍTNUTO`/`ODLOŽENO`) | `PREDAVANI-SESSION.md` **§2.2** + kronika §5 | Odůvodněno daty: **76 % omylů** vzniklo v měřidle (§3 kroniky) → „mně to přijde správné" je důkaz, který tu opakovaně selhal |
| **5** | **Závěrečná fáze Z1–Z3** — validační session → **cyklus validace/oprav** → uzavírací session se **shrnoutím, lessons learned, analýzou příběhu a revizí nástrojů a skillů** | `PREDAVANI-SESSION.md` **§2.3** + `PLAN-DALSI-KROK.md` **§6** | podmínka vstupu do Z3 je měřitelná: **žádný nález ve stavu `NEOVĚŘENO`** |
| **6** | **Pravidlo o inventáři** zapsáno jako **návrh NA1** (ne rovnou do `AGENTS.md`) | kronika §5 | **Nový proces se aplikoval sám na sebe** — plánovací session o pravidle nerozhodla, jen ho navrhla |
| **7** | Kronika a nová pravidla **v obou branách diakritiky** | `kontrola-diakritiky.py`, `g1-diakritika-novych.py` | `g1` **63 souborů** (bylo 56), brána **45 souborů** |

**A jeden nález, který vznikl při měření effortu (odpověď na dotaz uživatele):**

* `reasoningEffort` je **globální nastavení profilu** — naměřeno
  `profiles/desktop/cordis.patch.yml:27–28`: `model: deepseek-flash`,
  `reasoningEffort: max`. V `request/header` **téhle session** pole
  `reasoningEffort` **NENÍ** (je tam jen `model`), takže se effort
  **ze session logu nedá změřit** — a DSH ho **nepředává subagentům**.
  → **„Jiný effort pro jinou činnost" dnes není k dispozici**; přepnutí
  znamená přepnout profil pro **vše**. Zapsáno jako **L11** v kronice.
* A druhý: náklad reasoningu **není jednorázový** — každý reasoning token se
  průměrně **přečte 196–232×** z cache (`ANALYZA-EFEKTIVITY-DSH.md` §2.6).
  Thinking je **22,8 % účtu** Flashe. Zapsáno jako **L12**.



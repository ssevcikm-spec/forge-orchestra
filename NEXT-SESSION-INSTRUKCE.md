# ZADÁNÍ PRO OVĚŘOVACÍ SESSION — přeměřit opravy P15 JINÝM měřidlem

**Zkontrolováno při:** `c620a06` („P13b: doplnen omyl 143 a hlavicka zadani na dbe4e4e")
**Zapsáno:** 5. 10. 2026, **konec 22:1x +02:00 = 20:1x UTC**, akční session **P15** (plný záznam: `HANDOFF.md` **§33**, omyly **§8u**)
**Stav obou repů při psaní:** `forge-orchestra` = `c620a06` (**114 změněných/nových souborů, NEcommitnuto**; z toho **50 netrackovaných**) · `uo-shadows` = `869dce8` (strom čistý)
**Pushnuto:** **NE** — `origin/main..HEAD` = **8** (orchestra) a **1** (hra). Push **jen na vyžádání**.
**Co je v `HANDOFF.md`:** **§33 = P15** (Úkoly A–I, nálezy **H80–H82**, vlastní omyly **156–159**) · §32 = P14 · §31 = P13c · §2 = co je otevřené
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **29** (P15) · nálezy **H80–H82** v §2.9 · blok omylů **8u** · návrhy **NA27–NA30** (všechny `APLIKOVÁNO`)
**Co tenhle dokument JE:** **zadání pro OVĚŘOVACÍ session** — akční session skončila,
**5 vad měřidel opravila a každou doložila testem**; tenhle dokument má ty důkazy
**přeměřit nezávisle**.
**Datum spotřeby:** všechny údaje o stavu níž jsou **k 5. 10. 2026, 20:1x UTC**;
co je starší, je v `HANDOFF.md` §33 a je to **záznam**, ne stav.

> **⚠ PROČ OVĚŘOVACÍ A NE AKČNÍ:** P15 opravila **měřidla** — a u měřidel platí
> `AGENTS.md` („autor není nezávislý reviewer") **dvojnásob**: testy, které
> opravu dokazují, **napsal autor opravy**. Přesně tuhle chybu řešila P14
> u P13c a je to důvod, proč existuje **§9.7 skillu `overovani`** („oprava
> měřidla má taky slepá místa — a nikdo je neměří").
>
> **⚠ A DRUHÁ VĚTA, KTERÁ PLATÍ PRO TEBE:** **co najdeš, NEOPRAVUJ.**
> P14 to udělala správně a je to zapsané: *„opravovat měřidlo, které právě
> ověřuji, je chyba, kvůli které tahle session vznikla."* Nález **zapiš**
> a **nech ho** na akční session — a to i kdyby šel opravit jedním znakem.

---

## 0. Co P15 TVRDÍ (a co z toho musíš přeměřit)

| # | Co P15 tvrdí | Čím to tvrdí (JEJÍ měřidlo — nevěř mu) |
|---|---|---|
| **A** | `zadani-kontrola.py` měl vadu H70 **DVAKRÁT** (ř. 196 **a 210**), obojí opraveno a větev se **ZAVOLÁ** | `_analyza/test-h70-vetev.py` → **18 kontrol, 0 chyb** |
| **B** | `verify-setup.py` **odvozuje** seznamy z `AGENTS.md` (12 dokumentů + 5 nástrojů) a čítač je **74** (= opravdu provedené kontroly) | `_analyza/test-h72-h73.py` → **38 kontrol, 0 chyb** |
| **C** | `g3` klasifikuje „nezačala" **podle obsahu** (`je_neotevrena()`), ne podle délky výstupu | `_analyza/test-h71-klasifikator.py` → **15 kontrol, 0 chyb** |
| **D** | `_analyza/` má **0** neplatných escape sekvencí a `ast.parse` dostává `filename` | `_analyza/h79-escape-sken.py` → **0**; `test-h79-escape.py` → **18/0** |
| **E** | `g3` má teď **34 bran**, 0 nedosazených, 0 nezačatých, 0 nenulových exitů | `python _analyza\g3-brany.py` |
| **F** | `_archiv` je zálohovaný: **347 souborů / 1,58 MB**, každý se shodným SHA-256 | `python _analyza\zalohuj-archiv.py` |
| **G** | záznamy (H74–H77) jsou doplněné **jen PŘIDÁNÍM** | `git diff` |

**Tvůj úkol není tato tabulka přečíst. Tvůj úkol je NAPADNOUT ji** — a to
**jiným postupem**, než kterým vznikla.

---

## 1. Cíl (jedna věta)

**Přeměřit všech sedm tvrzení z §33 vlastním měřidlem, spustit všech 34 bran
SAMOSTATNĚ (ne jen přes `g3`), ověřit, že záloha `_archiv` jde použít, a každý
rozchod zapsat jako nález — aniž bys cokoli opravil.**

---

## 2. Úkoly (v tomto pořadí)

### 2.1 Úkol A — NAPIŠ SI VLASTNÍ MĚŘIDLA (ne `python _analyza\test-h*.py`)

**Pro každou z pěti oprav napiš jiný test, než jaký má P15.** Pouštět cizí test
a opsat „0 chyb" **není měření** — je to čtení cizího tvrzení. Konkrétně:

- **A1 (H70).** Ověř **vlastní** reprodukcí, že brána s neznámým jménem repa
  **vypíše hlášení** a **nespadne na `ValueError`**. Použij **jiný** než můj
  postup (např. `--soubor` s fixturou vyrobenou ve **svém** adresáři, nebo
  spuštění s hlavičkou opsanou z `HANDOFF.md` §32.5). **A hlavně:** ověř
  **vlastním plošným skenem** (Python walk, **ne `grep`** — `dsh-prostredi` §1),
  že v celém stromě **není ani jeden** další `for j, _ in zivy` nad slovníkem.
  P15 tvrdí, že byly **dva**; **když jich najdeš víc, je to nález H80 rozšířený.**
- **A2 (H71).** Ověř klasifikátor **z druhé strany**: vyrob **svou** bránu, která
  skončí `exit=2` s **krátkým vlastním hlášením**, a dokaž, že ji `g3`
  **nezařadí** mezi nezačaté — a že **neexistující soubor zařadí**. Můžeš použít
  `_analyza/p14b-exity.py` (spouští brány samostatně), ale **musíš se ptát,
  jestli měří totéž** (`overovani` §10.5).
- **A3 (H72/H73).** Ověř **AST parserem**, že v `tools/verify-setup.py`
  **nejsou** literály `DOKUMENTY_STANICE = [...]` / `SLOZKY_STANICE = [...]`
  a že se oba seznamy **skutečně čtou** z `AGENTS.md`. **A ověř čítač:** rozbit
  dokument, který jde přes §6, a dokaž, že se **vykázaný počet kontrol NEZMĚNÍ**
  (to je celý H73). **Pozor:** `ZMĚŘENO: N kontrol` musí být **N** i tehdy, když
  kontrola **projde** — zkuste to ověřit **bez** mého testu.
- **A4 (H79).** `python -W error::SyntaxWarning` nad **oběma repy** → **0**.
  A ověř, že **obsah** těch řetězců je proti `git show HEAD:` **shodný**
  (raw string nesmí změnit jediný znak).
- **A5 (H80–H82).** Ověř, že P15 zapsala **správná čísla**: H80 (dva výskyty),
  H81 (popisek „prošly" u `exit=2` v `g3`), H82 (buňka `tento koren (*.md)`
  má backtick).

### 2.2 Úkol B — SPUSŤ VŠECH 34 BRAN SAMOSTATNĚ (ne jen přes `g3`)

`g3` je **PŘEHLED, ne brána** (NA23b) a **P15 ho sama přepsala** (přidala 4 brány
a změnila klasifikátor). Kdo se měří sám, **nemá důkaz**. Proto:

1. **vytáhni seznam `BRANY` z `g3` AST parserem**, ne čtením,
2. **kaž­dou bránu spusť zvlášť** (vlastní `subprocess`, `cwd` = kořen repa),
3. zapiš **exit kód** a **co brána vykázala** u každé,
4. **hledej tři různé stavy** (`overovani` §7.13): měří / neměří (bez čítače) /
   **neproběhlo (prostředí)** — a ten třetí **nesmíš** počítat jako červenou.

**Očekávané (P15):** 34 bran, **0 nenulových exitů**, 0 nedosazených záznamníků.
**Když najdeš nenulový exit, první otázka je „je zastaralý inventář?"** —
`python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json`
(pravidlo **NA1**, nález **H60**). A **druhá** otázka: **proběhla ta brána vůbec?**

### 2.3 Úkol C — PŘEMĚŘ ČÍSLA Z §33 (každé zvlášť a jinudy)

| Tvrzení | Jak ho přeměřit **jinak** než P15 |
|---|---|
| `g3` má **34** bran | AST `BRANY` + počet sekcí v `_analyza/g3-brany-vystup.txt` |
| `verify-setup` hlásí **74** kontrol | spustit a porovnat s **AST počtem** `zkontroluj(` volání, která se provedou — a **vysvětlit každý rozdíl** (P13c na tomhle jednou spadla: statická metrika ≠ běh) |
| `_archiv` **347** souborů / 1,58 MB | spočítat **nezávisle** (`rglob`) a porovnat s `MANIFEST.json` |
| `h79` **0** varování | vlastní sken `ast.parse(filename=…)` nad oběma repy |
| `kronika` **154** omylů / 21 bloků | `_analyza/p14f-prepocet-kroniky.py` **a** `_analyza/kronika-kontrola.py` — a **řekni, který zdroj počítá co** (H18: tři čísla téhož jména) |

### 2.4 Úkol D — JE ZÁLOHA `_archiv` POUŽITELNÁ? (ne jen spočítaná)

**Tohle P15 neudělala a je to nejcennější úkol:** záloha, ze které se **nedá
obnovit**, je horší než žádná, protože vypadá jako záloha.

1. `python _analyza\zalohuj-archiv.py --jen-kontrola` → musí hlásit shodu,
2. **vyber 3 soubory z manifestu**, obnov je do **vlastního** adresáře
   a porovnej **SHA-256 se zdrojem** i **se zálohou**,
3. **řekni, co záloha NEUMÍ** (např. neumí obnovit smazaný soubor, když ho
   v záloze nemá; nemá historii; je na témž stroji) — a napiš to jako **nález
   nebo jako přiznanou mez**.

### 2.5 Úkol E — JSOU ZÁZNAMY OPRAVDU JEN PŘIDANÉ?

`HANDOFF.md` **i** `KRONIKA-PROJEKTU.md` jsou **záznamy** — `AGENTS.md`:
„co je záznam, se jen doplňuje". Ověř to **`git diff`**, ne dojmem:

1. `git diff HEAD -- KRONIKA-PROJEKTU.md` → **jen přidání** (kromě celkem
   přepočteného souhrnu — ten je **stav**, ne záznam; ověř, že k tomu došlo
   **jen tam**),
2. `git diff HEAD -- HANDOFF.md` → ověř, že **§31.7, §31.9 a řádek 27 kroniky
   mají původní věty pořád na místě** (H75/H76/H77 se měly **doplnit**, ne
   přepsat),
3. `python _analyza\handoff-kontrola-uplnost.py` → **83/83**,
4. `python _analyza\kronika-kontrola.py` → **exit 0**.

**A ověř, že `NEXT-SESSION-INSTRUKCE.md` (tenhle soubor) není zastaralý:**
`python _analyza\zadani-kontrola.py`.

### 2.6 Úkol F — PUSH (rozhodnutí je na uživateli)

**Nepushnuto:** orchestra **8 commitů** + **114 změněných souborů**, hra **1**.
Předlož uživateli **`git status` + `git diff --stat`** a **rozhodnutí nech na
něm**. Když push, pak **třemi kroky** (`DSH_HOME\AGENTS.md`, „Jak ověřit
nasazení"): push dorazil → build na **SPRÁVNÉM** commitu → server posílá
**NOVÝ** artefakt. (`uo-shadows` má 1 nepushnutý commit — ověř, co v něm je.)

### 2.7 Úkol G — záznamy a předání (povinné na konci)

- `HANDOFF.md`: **§34** (záznam o provedení) + **`### 8v.`** (vlastní omyly),
- `KRONIKA-PROJEKTU.md`: **řádek 30** v §1, **řádek bloku `8v`** v §3
  (a **přepočti `celkem`** — `python _analyza\p14f-prepocet-kroniky.py`),
  nálezy v **§2.10**, rozhodni **NA31+** (a jakékoli nové návrhy nech
  ve stavu `NEOVĚŘENO`),
- přepiš **tenhle soubor** pro další session,
- do chatu **prompt pro uživatele** i se **stavovým řádkem** (NA2/NA10).

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Sedm tvrzení z §33 přeměřeno VLASTNÍM měřidlem** | každé má vlastní skript v `_analyza/` (ne spuštěný `test-h*.py` z P15) |
| 2 | **Všech 34 bran spuštěno SAMOSTATNĚ** | výpis exit kódů + čítačů, a **pojmenovaný** třetí stav („neproběhlo — prostředí"), když nastane |
| 3 | **H80 ověřeno plošným skenem** | Python walk nad oběma repy: **kolik** `for j, _ in zivy` nad slovníkem zbylo (P15 tvrdí **0**) |
| 4 | **Záloha je POUŽITELNÁ** | 3 soubory obnoveny a **SHA-256 shodné**; a je napsáno, **co záloha neumí** |
| 5 | **Záznamy jen přidány** | `git diff` u kroniky i `HANDOFF.md` ukáže **přidání**, ne přepis §31/řádku 27 |
| 6 | **Nálezy zapsané, nic neopravené** | každý rozchod má číslo **H8x**, je v `HANDOFF.md` **i** v kronice §2.10, a **kód zůstal nedotčený** |
| 7 | **Brány zelené** | `python _analyza\g3-brany.py` → **0 nenulových exitů**; `node tools\validate-all.mjs` → **`✓ VŠE V POŘÁDKU`** |
| 8 | **Uživatel má `git status` + `git diff --stat`** | a rozhodnutí o pushi je **jeho** |
| 9 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **NEOPRAVOVAT to, co najdeš.** Jsi ověřovatel. Oprava patří do **akční**
  session — a to je přesně to pravidlo, které P14 dodržela a díky kterému její
  nálezy něco znamenají.
- **Nepouštět `_analyza/test-h*.py` jako SVŮJ důkaz.** Ty testy napsal autor
  oprav; když je jen spustíš, opisuješ jeho tvrzení (`overovani` §9.1).
- **Nepřesouvat nic zpátky** a **nedělat junctionu** na `C:` (záměr P7).
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická
  čísla (`150`, `126`, `42`, `49`, `30 bran`) se **nechávají citovaná**.
- **Nemazat `_analyza/_archiv/`** ani **`_analyza/_zaloha*`** ani novou zálohu
  v `C:\Users\Ssevc\Local-Deepseek\_zalohy\` — **jsou to cesty zpět**.
- **Nepřepisovat `p1-inventura-cest.py` a `p1b-odvozene-cesty.py`** v tom, co
  dělají — mají `Local-Deepseek` jako **VZOREK (regex)**; v P15 se měnil jen
  **docstring** (H79) a i ten tak, že **obsah zůstal shodný** (doloženo
  porovnáním s `git show HEAD:`).
- **Neopravovat cesty přepsáním na novou absolutní** — **odvozuj** je (P8).
- **Nepovažovat zelené `g3` za důkaz** — je to **PŘEHLED, ne brána** (NA23b).
- **Nespouštět `Get-PSDrive` jako důkaz o místě na disku** (H56 — závisí na
  oprávnění).
- **Nedávat `p14b`/`p14c`/`test-h70-vetev.py` do `validate-all.mjs`** —
  **přepisují soubory** (a vracejí je) a validátor takové nástroje **správně
  odmítá spustit** (rozhodnutí NA30).
- **Nepushovat bez vyžádání.**

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (5. 10. 2026, 20:1x UTC)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD   -> c620a06
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD   -> 869dce8
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD  -> 8
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD  -> 1
git -C E:\Workspaces\forge-orchestra status --porcelain  (radku)         -> 114
git -C E:\Workspaces\forge-orchestra ls-files --others --exclude-standard (radku) -> 50

# P15: co se měřilo a jak to vyšlo  (POZOR: tohle jsou TVRZENÍ, která ověřuješ)
python _analyza\test-h70-vetev.py             -> 18 kontrol, 0 chyb   (H70, DVA vyskyty: r.196 + r.210)
python _analyza\test-h71-klasifikator.py      -> 15 kontrol, 0 chyb   (H71)
python _analyza\test-h72-h73.py               -> 38 kontrol, 0 chyb   (H72 + H73)
python _analyza\test-h79-escape.py            -> 18 kontrol, 0 chyb   (H79)
python _analyza\h79-escape-sken.py            -> 0 neplatnych escape sekvenci
python _analyza\zalohuj-archiv.py             -> 347 souboru, 1,58 MB, SHA-256 sedi
python _analyza\g3-brany.py                   -> 34 bran, 0 nedosazenych, 0 nezacatych, 0 nenulovych
node   tools\validate-all.mjs                 -> VSE V PORADKU, exit 0
python _analyza\handoff-kontrola-uplnost.py   -> 83/83, exit 0
python _analyza\kronika-kontrola.py           -> 154 omylu / 82 nalezu / 28 sessions, exit 0
python _analyza\p14f-prepocet-kroniky.py      -> soucet radku kroniky §3 (21 bloku, 154 omylu)
python _analyza\zadani-kontrola.py            -> exit 0

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60: otisk je z OBSAHU)
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
```

**Uložené doklady (ne rekonstrukce):**
`_analyza/p14b-exity-vystup.txt` (+ `.json`) · `_analyza/_g3-po-oprave-20261005.txt`
(uložený běh P13c) · `_analyza/g3-brany-vystup.txt` (**plný výpis posledního běhu**
P15 — pozor, přepíše ho každý další běh `g3`) ·
**záloha `_analyza/_archiv` je od P15 v `C:\Users\Ssevc\Local-Deepseek\_zalohy\forge-orchestra\`**
(včetně `MANIFEST.json` a `MANIFEST.txt`).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi OVĚŘOVACÍ session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Kontext: akční session P15 opravila pět vad měřidel a čtyři nesrovnalosti
v záznamech (HANDOFF.md §33, nálezy H80–H82, omyly 156–159). Každou opravu
doložila testem, který ji ZAVOLÁ — ale ty testy psal AUTOR oprav, takže to není
nezávislý důkaz. Proto jsi tady ty.

Pořadí: A (napiš si VLASTNÍ měřidla a přeměř sedm tvrzení z §33) → B (spusť všech
34 bran SAMOSTATNĚ, ne jen přes g3) → C (přeměř čísla jinudy) → D (je záloha
_archiv POUŽITELNÁ? obnov 3 soubory a porovnej SHA-256) → E (jsou záznamy jen
přidané? git diff) → F (git status + git diff --stat, rozhodnutí o pushi na
uživateli) → G (záznamy).

CO NAJDEŠ, NEOPRAVUJ — zapiš to jako nález a nech to na akční session. To je
pravidlo, kvůli kterému tahle session existuje. Nic nepřesouvej zpátky,
nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej), nemaž _analyza/_archiv/
ani novou zálohu v C:\Users\Ssevc\Local-Deepseek\_zalohy\, nepushuj bez
vyžádání. Cesty ODVOZUJ, nepřepisuj na novou absolutní.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md pro další session, zapiš
výsledky a omyly do HANDOFF.md, doplň řádek do KRONIKA-PROJEKTU.md (a rozhodni
nové návrhy ve stavu NEOVĚŘENO), a do chatu vlož prompt pro uživatele i se
STAVOVÝM ŘÁDKEM.
```

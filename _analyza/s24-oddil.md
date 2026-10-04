
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

---

## 24. Ověření práce §23 — PLÁNOVACÍ (ověřovací) session 2. 10. 2026 (16:4x–17:1x UTC)

**Zadání:** `ZADANI-PO-AUDITU.md` (samostatný dokument, **NE**
`NEXT-SESSION-INSTRUKCE.md` — ten patří souběžné session, viz §23.7 a **§24.9**).
**Kontrola zadání před prací:** `git -C orchestra rev-parse HEAD` = `d1cde9bbf`,
`git -C games\uo-shadows rev-parse HEAD` = `279f58486` → **obojí sedí** s hlavičkou
zadání; `origin/main..HEAD = 0` v obou repech. Šest příkazů z §1.3 zadání
proběhlo, **pět z nich `exit 0`** (výjimkou je `audit-snapshot.py`, který
**správně** hlásí „hnulo se to" — viz §24.4).

**Hlavní výsledek: práce §23 OBSTÁLA.** Ze **9 měřitelných tvrzení** jich
**7 sedí beze zbytku**, **1 je zastaralé** (ne nepravdivé) a **1 je nepřesné**.
**Hlavní riziko zadání (slepost `audit2b`) se VYVRÁTIT NEPODAŘILO** — a to je
výsledek, ne selhání: mutační test to doložil **měřením** (§24.3).

### 24.1 Devět tvrzení z §2.1 zadání — naměřeno spuštěním

| # | Co session tvrdila | Co vyšlo | Verdikt |
|---|---|---|---|
| **1** | `AGENTS.md:63` už neodporuje sám sobě | `audit2a-schema.py` → **`exit 0`**, `výskytů=25 (souhlasí=3, záznamů=19, citací=3, ROZCHODŮ=0)` | ✅ **sedí** |
| **2** | `ag-mutace.py` proběhne a je v `g3` | `exit 0`, **`mutací=2, chyceno=2`**, `tvrzení_v_dokumentu=27`, `řádků_s_číslem=116`; v `BRANY` na ř. 118 | ✅ **sedí** |
| **3** | `ag-mutace.py` umí spadnout | `audit2a-mutace.py` → **4 mutace, 4 chyceny** (M1–M3 spadly, M4 zelená), `AGENTS.md` vrácen **bit po bitu**; `ag-mutace.py` → **2/2** | ✅ **sedí** |
| **4** | `audit2b` už nehlásí rozchod u `granulí` | `audit2b-over.py` → **`exit 0`**, 4 běhy, 2 mutace chyceny, `granulí` **0 rozchodů**, `HANDOFF.md` bit po bitu | ✅ **sedí** |
| **5** | `HANDOFF.md` je **NEDOTČENÝ** (hash `451fc02aeea55000…`) | hash `451fc02aeea55000…` je v **obou** snapshotech (18:12 i 18:32); **dnešní disk = `fb266565a52ef976…`, 303 104 B** | ⚠ **ZASTARALÉ** — ne nepravdivé (§24.4) |
| **6** | oba „neproběhnuvší" testy mají hlavičku a pořád neprobíhají | `audit3-hlavicky-over.py` → **`exit 0`**, `souborů=2`, každý parsován **i spuštěn**, `0 souhrnů testů` | ✅ **sedí** |
| **7** | všechny brány otevřely, co měly; **30 bran, 1 nenulový exit** | `g3-brany.py` → **30 bran**, ale **2 nenulové exity** (`mutace A: pres-level` správně + `validate-all (CELEK)` = **neproběhlo — prostředí**) | ⚠ **NEPŘESNÉ** (§24.6) |
| **8** | dokumenty odpovídají zdrojům | `hl-rizika-jazyka.py` → `exit 0` (0 očekávaných, 11 přejednaných, 0 vrácených) · `g1-diakritika-novych.py` → `exit 0`, **480** textových souborů, 0 vad | ✅ **sedí** (počty **vyrostly**, viz §24.8) |
| **9** | inventář přegenerovaný, `snapshot` se nepočítá jako dokument | `audit1-inventar.py` → `exit 0`, **104** dokumentů (79 živých / 11 sirotků / 8 záloh / 6 kopií), `bez hlavičky: 75`, **žádný sloupec prázdný** | ✅ **sedí**; „101" je dnes **104** |

> **Ke každému číslu patří postup** (A2): všechny výše uvedené hodnoty jsou
> opsané z **výstupu běhu**, ne z dokumentu. Kdo je chce zopakovat, spustí
> tentýž příkaz — proto jsou u každého.

### 24.2 Třináct opatření z `AUDIT-DOKUMENTACE.md` §6 — stav a VLASTNÍK

Zadání to žádalo jako samostatný bod (**nález H26**: dvě opatření nebyla
přidělena žádné session). **Vlastník je opsán z `ZADANI-DOKONCENI-AUDITU.md` §6**,
kde jsou session **B**, **C** a **D** — a **žádná z nich neproběhla**.

| # | Opatření | Stav 2. 10. 2026 | Vlastník | Doklad |
|---|---|---|---|---|
| **1** | `AGENTS.md:62` označit časem | ✅ **HOTOVO** | Úkol 1 (§23) | ř. 63: `**39** (stav před B1; dnes **40**)`; `audit2a` → 0 rozchodů |
| **2** | opravit popisek v `ag-over-cisla.py:155` | ✅ **HOTOVO** | **NIKDO** (H26) — §6 ho nezmiňuje; session ho udělala dobrovolně | ř. 157–164: popisek `"sloupců D1"` **bez čísla**; komentář cituje vadu `OK 39 … = 40` |
| **3** | `ag-over-cisla.py` rozšířit na řádek 62 | ❌ **NENÍ** — zůstává | **NIKDO** (H26) | nástroj ověřuje **5 + 2** tvrzení z **27**; částečně kryto `audit2a` (čte prózu) |
| **4** | `HANDOFF.md`: pravidla zkrátit na odkaz | ❌ **NENÍ** | **session C** | dokument má **3 852 řádků / 303 104 B** a **roste** |
| **5** | oddíly §10–§22 přesunout do kroniky | ❌ **NENÍ** | **session C** | `## 10.`–`## 22.` je v `HANDOFF.md` **pořád** (13 oddílů, ř. 801–3 468) |
| **6** | ruční seznam v `kontrola-diakritiky.py` → projití složky | ✅ **HOTOVO — touto session** (zadání to NEDOPORUČOVALO, viz §24.7) | **session B** (ale uděláno) | projití **+197 souborů** (kořen + `_analyza`) → **305** kontrolovaných; **28 dokumentů, které brána nikdy neotevřela**, je teď vidět |
| **7** | doplnit hlavičky 62 dokumentům | ⚠ **ČÁSTEČNĚ** (zhoršilo se) | **session B** | `bez hlavičky:` **62 z 98** (audit) → **76 z 105** (dnes); dokumenty v `_analyza` přibývají |
| **8** | zavést verzování dokumentace | ❌ **NENÍ** | **session B** | `git ls-files HANDOFF.md` → **`exit 1`** (není v gitu); kořen workspace **není repozitář** |
| **9** | zmrazit snapshot před dalším auditem | ✅ **HOTOVO** | Úkol 0 (§23) | **dva** snapshoty: `snapshot-20261002-181237` a `-183213`, oba **71 souborů** s SHA-256 |
| **10** | zrušit/ztlumit brány, které nic nevykázaly | ❌ **NENÍ** | **session D** | `g3` má **3×** `otevřela: —` (`C1: důkaz selhání`, `C2: mutace N1`, `tsc`) |
| **11** | opravit vzor v `ag-mutace.py` + přidat do `g3` | ✅ **HOTOVO** | Úkol 2 (§23) | kotva `40 sloupců`; `g3` **29 → 30 bran** |
| **12** | doplnit mutační testy 9 branám bez důkazu | ❌ **NENÍ** | **session D** | `audit6-brany-mutace.py` → **10 z 30** bran bez jakéhokoli důkazu |
| **13** | `h17-mutace-a.py` a `mutace-testu.py` označit jako NEPROBĚHLO | ✅ **HOTOVO** | Úkol 3 (§23) | oba mají hlavičku, oba padají týmž důvodem, `0 souhrnů testů` |

**Souhrn: 5 hotovo (1, 2, 9, 11, 13) · 1 hotovo navíc (6) · 1 částečně a zhoršuje
se (7) · 6 neprovedeno (3, 4, 5, 8, 10, 12).** Vlastníky **má 10 opatření**
(session B: 6–8; session C: 4–5; session D: 10 a 12) — **a dvě (2 a 3) neměla
žádného**, což je nález **H26 potvrzený**.

### 24.3 ⚠ HLAVNÍ RIZIKO ZADÁNÍ VYVRÁCENO: `audit2b` NENÍ slepý na append-only dokumenty

Zadání §2.3 bod 2 to označilo za „největší šanci na nález": `audit2b` má
v docstringu **přiznanou mez**, že nehlídá append-only dokumenty. **Ověřeno
mutačním testem, ne čtením:**

| Měření | Postup | Výsledek |
|---|---|---|
| **VÝCHOZÍ STAV** | `audit2b` na zdravém `HANDOFF.md` | `exit 1`, `ROZCHODŮ: 29`, v bloku **29** řádků |
| **A — NEDATOVANÝ oddíl** | do `## 0. Co se stalo …` (ř. 38) vloženo *„schéma `conductor` má **54 sloupců**"* (zdroj **40**) | rozchody **29 → 30**, vložené tvrzení **je v ROZCHODECH** → **brána ho OHLÁSÍ** |
| **B — DATOVANÝ oddíl** (kontrolní vzorek) | totéž do `## 10. Session 2. 10. 2026 …` | rozchody **29 → 29**, ale tvrzení **je ve výstupu** (jako ZÁZNAM) |
| **NÁVRAT** | `HANDOFF.md` zapsán zpět | **`fb266565a52ef976…` = bit po bitu původní** |

**Verdikt: NENÍ to slepota.** `audit2b` **vidí i v append-only dokumentu** —
jen datované oddíly **správně** zařazuje jako záznam (A2). Nástroje:
`_analyza\s24-slepota-audit2b.py` (hrubé měření) a
**`_analyza\s24-slepota-audit2b-presne.py`** (přesné: čte **čítač ze souhrnu**,
ne výskyt ve výpisu — první verze měřila špatně, viz omyl **98**).

> **A jedna past, která se při tom odhalila:** hrubá verze usoudila „brána to
> nehlásí", protože vložené číslo **nebylo ve výpisu**. Jenže `audit2b` tiskne
> ze ZÁZNAMŮ jen **prvních 40** (`histor[:40]`) — „není ve výpisu" tedy **není**
> „brána to nevidí". Je to `overovani` §9.4: *naměřeno 0 má tři různé významy.*

### 24.4 ⚠ TVRZENÍ 5 JE ZASTARALÉ, NE NEPRAVDIVÉ — a je to druhý výskyt H28

Zadání tvrdí „`HANDOFF.md` je NEDOTČENÝ, hash `451fc02aeea55000…`".
**Naměřeno:**

| Co | Hodnota |
|---|---|
| `451fc02aeea550001a7b5340…` | **oba** snapshoty — `18:12:37` **i** `18:32:13` → **v tom okně se nezměnil** |
| hash na disku teď | **`fb266565a52ef9762a2325ca…`**, **303 104 B** (v snapshotu **282 130 B**) |
| co se připsalo | **§8j** (omyl **96**) a **§23** — tedy **přesně to, co zadání Úkolem 6c nařizovalo** |

**Tvrzení bylo ve svém čase správné** (v 18:12 i 18:32 hash seděl) a **zestárlo
vlastním provedením zadání**. Není to nepravda — je to **čas** (A2). Zapsáno
proto jako **zastaralé**, ne jako vada session.

> **A podruhé týž den, nezávisle:** `NEXT-SESSION-INSTRUKCE.md` měl při startu
> téhle session `mtime` **18:48:08**, v **19:01:14** se pohnul — a **hash
> obsahu je pořád `9c05c6b434d5d026…`, 17 841 B**. Hnul jím **mutační test**
> (`zadani-mutace.py`), který ho spouští `audit6-brany-mutace.py`.
> **Druhý výskyt téhož nálezu H28 v jedné session** — a důkaz, že NA20 není
> formalita: kdo se ptá na `mtime`, řekne „pracuje v tom jiná session".

### 24.5 ⚠ NÁLEZ **H29** — `audit2b` MÁ 25 FALEŠNÝCH ROZCHODŮ Z 31 (a je to táž vada, kterou vytkl auditu)

`audit2b` je **správný v tom, co vidí**, ale **nesprávný v tom, co s tím dělá**:
veličina `kontrol` srovnává **jedno číslo z jedné brány** s **všemi** výskyty
`(\d+)\s+kontrol` v jádru. **Naměřeno** (`python _analyza\audit2b-cisla-proti-zdroji.py`):

| Veličina | Rozchodů | Falešných | Proč |
|---|---|---|---|
| `kontrol` | **19** | **19** | zdroj je **65** (jedna brána Godotu); jiné brány **správně** hlásí 19, 23, 38, 60, 63 |
| `sloupců` | **4** | **4** | všechny jsou **citace** `„32 sloupců"` |
| `dokumentů` | 3 | 3 | `HANDOFF.md` §8 — záznamy bez data v okně |
| `omylů` | 3 | 3 | dtto |
| (vlastní texty o rozchodech) | 2 | 2 | každý dokument, který o rozchodech píše, přidá výskyt |

**Rozhodující důkaz, že jde o vadu a ne o názor:** `PREDAVANI-SESSION.md:193`
zní *„naměřeno u „32 sloupců" v `AGENTS.md`, nález **N9**"* — tedy **citace**.
`audit2a-schema.py` **tentýž řádek** správně zařadí jako `[citace]`
(citací=**3**), ale `audit2b` ho hlásí jako **ROZCHOD** (sloupců=**4**).
**Dvě měřidla téhož čísla si odporují** — a to je horší stav než jedno slepé,
protože **není poznat, kterému věřit**. Je to **přesně vada, kterou audit
vytkl `audit2-rozpory.py`** — a `audit2b`, který měl být tou lepší variantou,
ji má taky. **Návrh NA22 potvrzen měřením** (§24.10).

### 24.6 ⚠ TVRZENÍ 7 JE NEPŘESNÉ: `g3` má **2** nenulové exity, ne 1 — a druhý je „neproběhlo"

`g3-brany.py` naměřeno: **30 bran, 2 nenulové exity**:

| Brána | exit | Verdikt |
|---|---|---|
| `mutace A: pres-level` | 1 | **správně červená** (známá vada, záměrná) |
| `validate-all (CELEK)` | 1 | **NEPROBĚHLO — PROSTŘEDÍ**, třetí stav (`overovani` §7.13) |

**Proč to není regrese:** `validate-all` padá na **3 problémech** a **všechny tři
jsou prostředí**, ne kód: 2× `PermissionError [WinError 5]` při `mkdir`
v **přesměrovaném tempu** sandboxu (`schema-test-…/a-iso`, `baseline-test-…/.forge`)
a 1× `spawn EPERM` ve `vision.test.mjs`. `HANDOFF.md` §16.5 má obě ty brány
**změřené jako zelené mimo sandbox** (17/0 a 36/0) — a §23.3 správně poznamenalo,
že „neproběhlo" se pod **`danger-full-access`** změní na zelenou.
**Tahle session běží v `workspace-write`** → stav je zpátky „neproběhlo".
**Baseline je tedy závislý na oprávnění** a musí se tak číst.

### 24.7 ⚠ NÁLEZ **H30** — „čtvrtý stav" brány: `exit 1` nad VLASTNÍM VÝSTUPNÍM SOUBOREM
`g1-diakritika-novych.py` skončil `exit 1` s jedinou vadou:
`_tmp-g1.txt … NELZE PŘEČÍST: UnicodeDecodeError`. **Vadou byl můj vlastní
výstupní soubor** — PowerShell přesměruje výstup jako **UTF-16LE**
(`dsh-prostredi` §5b) a `g1` ho **ohlásí jako vadu**.
**Audit tuhle past zná a má na ni nástroj** (`audit-cleanup.py`, §8 auditu:
„první běh `g1` skončil `exit 1` a jediná vada byl můj vlastní výstupní soubor").
**Je to počtvrté, co se to stalo** — a poučení je: **výstup brány nepatří
do složky, kterou brána prochází**; ukládej ho mimo, nebo ho před dalším
během ukliď.

### 24.8 Co se od §23 ZMĚNILO (a proč čísla vyrostla)

| Veličina | §23 (18:5x) | Teď (17:0x) | Proč |
|---|---|---|---|
| textových souborů v `g1` | 466 | **480** | + §24 dokumenty a nové nástroje |
| dokumentů v inventáři | 101 | **104** | + `ZADANI-OPRAVA-MERIDEL.md`, + dokumenty téhle session |
| `záloh` v inventáři | 8 | **8–9** | moje záložní kopie před mutacemi |
| rozchodů v `audit2b` | 27 (audit) | **31** | + vlastní texty o rozchodech |
| bran v `g3` | 30 | **30** | beze změny |
| kontrolovaných dokumentů v bráně diakritiky | 57 (ruční seznam) | **305 (projití složky)** | opatření **6** provedeno |

### 24.9 Proč je i tohle zadání v NOVÉM souboru, a co to dokazuje o H28

Zadání pro **akční** session je v **`ZADANI-OPRAVA-MERIDEL.md`**.
`NEXT-SESSION-INSTRUKCE.md` **nebyl přepsán** — patří souběžné session
(`session-76e5d192`, „Dokončení auditu: tři vady dokumentace", doběhla
**16:48:44**; ověřeno `_analyza\dsh-session-prehled.mjs`, **24 session za 24 h**,
z toho **21 skutečných**).

**A je tu měřený důkaz, že rozhodnutí bylo správné:** ten soubor měl během téhle
session **změněný `mtime`** (18:48:08 → **19:01:14**) a **nezměněný obsah**
(`9c05c6b434d5d026…`, 17 841 B). Kdyby se session řídila kritériem z H28
(„porovnej `mtime`"), **přepsala by cizí zadání** — a ztratila by ho přesně
tak, jak to dokumentuje `SOUBEH-SESSION-NALEZY.md`.

**A totéž se stalo vlastnímu `HANDOFF.md`:** jeho `mtime` se pohnul
(18:44:58 → **19:32:26**) a **hash je pořád `fb266565a52ef976…`, 303 104 B**
— protože do něj sáhly **mutační testy téhle session** a vrátily ho **bit po
bitu**. **Třetí výskyt H28 v jedné session.**

### 24.10 Návrhy NA17–NA23 — ROZHODNUTY (povinná část, ne dobrovolná)

Úplné znění rozhodnutí je v **`KRONIKA-PROJEKTU.md` §6**. Zkráceně:

| Návrh | Rozhodnutí | Proč (naměřeno) |
|---|---|---|
| **NA17** | **`APLIKOVÁNO`** (v rozsahu: kontrola + výpis zdrojů) | brána kroniky zná **8** bloků, v dokumentu je **10** (`8i`, `8j`); **nová brána `s24-meridla-over.py` to měří** — a její **první verze byla slepá** (viz omyl **99**) |
| **NA18** | **`APLIKOVÁNO`**, zúžené | hlavičky této session mají **měřený** čas (`datetime.now(timezone.utc)`, `git log --format=%cI`); „zóna u každého údaje" **zamítnuto** jako neproveditelné — historické zápisy se nepřepisují (A2) |
| **NA19** | **`APLIKOVÁNO`** | naměřeno **6** odkazů na kroniku §5 (5 ze zadání + 1 nový) — opraví se **ukazatele**, ne číslování |
| **NA20** | **`APLIKOVÁNO`** v úzkém rozsahu | **druhý a třetí** výskyt H28 v jedné session (§24.4, §24.9) — `mtime` **rozhoduje špatně**; hash je autorita |
| **NA21** | **`APLIKOVÁNO`** | vyloučení `snapshot-*` **ověřeno v běhu** (inventář je **104**, ne 159) |
| **NA22** | **`APLIKOVÁNO`** — totéž jako NA17, měřeno | **19 z 19** rozchodů u `kontrol` je falešných; `audit2a` a `audit2b` si u téhož čísla **odporují** (§24.5) |
| **NA23** | **`APLIKOVÁNO`** (obě části) | **(a)** `g3` u `validate-all` vypisuje **`3`**, což je **„NALEZENO 3 PROBLÉMŮ"** — **třetí** výskyt tvaru, ne počet souborů (horší, než audit viděl: tam bylo **prázdno**); **(b)** baseline **závisí na oprávnění** (§24.6) |

### 24.11 Nové nástroje téhle session (v `_analyza\`, mimo CI)

| Nástroj | Co dělá | Ověřeno |
|---|---|---|
| `s24-slepota-audit2b.py` | hrubé měření slepoty (vloží tvrzení, sleduje výpis) | našlo vadu **svého měření** (omyl 98) |
| **`s24-slepota-audit2b-presne.py`** | **přesné** měření: čte **čítač ze souhrnu**, ne výskyt ve výpisu | rozchody **29 → 30** (nedatovaný), **29 → 29** (datovaný), soubor vrácen bit po bitu |
| `s24-opatreni-dukazy.py` | sběr důkazů ke **13 opatřením** §6 | našel, že opatření **6** je hotové a **7** se zhoršilo |
| `s24-opatreni6-pokryti.py` | kolik dokumentů brána diakritiky **vidí** a které **ne** | **57 v seznamu vs. 84 existujících** → **28 neviditelných** |
| **`s24-meridla-over.py`** | **brána na zadání** — ověřuje **10 faktů (F1–F10)** | **`exit 0`**, 12 kontrol, 0 chyb |
| **`s24-meridla-mutace.py`** | **mutační test té brány** | **2 mutace, 2 chyceny** + kontrolní běh zelený |

### 24.12 Co se OVĚŘIT NEDALO (přiznaná mez)

1. **`danger-full-access`** — `validate-all` a dvě brány z §16.5 se **nedají**
   v `workspace-write` dokončit. Ověřeno jen to, že **vadou je prostředí**
   (typ chyby), ne že by kód byl zelený.
2. **`audit2b` po opravě** — oprava je **úloha** pro akční session; měřeno je
   jen **zadání**, ne výsledek.
3. **Odpovědi na tři otázky pro člověka** (6 sirotků, 3 dokumenty
   v `OTEVRENA-TEMATA.md`, 251 nezapojených skriptů) — **agent je nemá
   zodpovídat sám**.

### 24.13 Vlastní omyly téhle session

**Pět, všechny v měřidlech nebo v postupu měření** — zapsané v **§8k**
(omyl **97–101**). **Dva z nich (`99`, `100`) by neodhalilo čtení kódu**;
odhalil je až **mutační test**. Podíl omylů v měřidle se tedy **opět
nezlepšil** — a to i přesto, že tahle session dělala **jen ověřování**.

### 24.14 Co si z téhle session odnést

1. **„Přiznaná mez" je taky tvrzení, které se ověřuje.** `audit2b` měl
   v docstringu, že nehlídá append-only dokumenty — **není to pravda**
   (má heuristiku, ne exempci). Kdo by to opsal, **vyrobil by si slepé místo
   tam, kde žádné není**.
2. **Dvě měřidla téhož čísla si mohou odporovat** — a to je **horší** než jedno
   slepé. `audit2a` a `audit2b` se u `„32 sloupců"` **rozešly** (§24.5).
3. **Mutace musí obrátit MĚŘENOU PODMÍNKU** — ne jen změnit soubor. Tahle
   session to zkusila **třikrát** na jedné kontrole, než našla správný směr
   (omyl **99**).
4. **Výstup brány nepatří do složky, kterou brána prochází** (§24.7).

---

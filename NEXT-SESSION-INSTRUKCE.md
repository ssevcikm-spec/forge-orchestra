# ZADÁNÍ PRO DALŠÍ SESSION — PŘEMĚŘIT P28 A VZÍT JEDNU VĚCNOU PRÁCI Z NABÍDKY

**Co tenhle dokument JE:** **zadání pro session P29**. Nahrazuje zadání P28
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, nejnovější oddíl **§59**)
ani kronika (ta je v `KRONIKA-PROJEKTU.md`, nejnovější **řádek 43**,
nálezy **§2.21**).

**Stav obou repů při psaní:** `forge-orchestra` = `fffc8e7` · `uo-shadows` = `8fe57ce`
(hra patří **cizí session**, která ji **během psaní tohohle zadání posunula
TŘIKRÁT**: `bc51e46` → `33d320b` → `d2976f3` → `8fe57ce`, a nechává v ní
netrackované soubory; P28 do hry nezapsala ani bajt).
`origin/main` orchestry je **`fffc8e7`** (P27 pushnuta); **necommitnutá je
práce P28** (`tools/`, `_analyza/`, dokumenty — **žádný soubor pod `conductor/**`**).
**Zkontrolováno při:** **8. 10. 2026, ~20:3x +02:00 = 18:3x UTC**

> **⚠ DATUM MĚŘENÍ SE NEOPISUJE ZE ZADÁNÍ — BERE SE Z HODIN** (nález P27-O;
> v P28 se to vyplatilo: session začala 15:45 a končila po 19:00).

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `fffc8e7` · `uo-shadows` = `8fe57ce`

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` v obou repech
> a **ověř živý stav** — `git fetch` v sandboxu padá (`.git/FETCH_HEAD`),
> použij **`git ls-remote`** (`tools\git.cmd`), **ne text zadání**.
>
> **⚠ DRUHÁ:** **`git.cmd` ŽERE `^`** → `git show <sha>^` vrátí stav **PO**
> commitu; používej **`~1`** nebo `git.exe` (skill `dsh-prostredi` §5c).
>
> **⚠ TŘETÍ:** **`.py` NESMÍ MÍT BOM** (omyl **189**) a **`.ps1` BOM mít MUSÍ**;
> po zápisu zkontroluj **první tři bajty**. `.env` a `.secrets/cf-secrets.json`
> BOM **MAJÍ** → čti je jako `utf-8-sig` (nález P27-H).
>
> **⚠ ČTVRTÁ:** **`python -c` NEPOUŽÍVEJ na český text ani na „→“** — PowerShell
> ho rozbije a výsledek vypadá jako „v souboru to není“ (naměřeno P28: `→` vrátil
> **0 výskytů** místo 4). **Piš skript do souboru.**
>
> **⚠ PÁTÁ:** **BĚHEM PLNÉHO BĚHU MĚŘIDLA DO STROMU NEPIŠ.** Obsahový otisk
> vstupů je citlivý na **obsah** (i na stejně velkou změnu) → `g3`/`validate-all`
> hlásí pojmenovaný stav „INVENTÁŘ JE ZASTARALÝ“. Měřidlo P28 proto inventář
> **před** `g3` přegenerovává — a je to **měřená věc**, ne detail.
>
> **⚠ ŠESTÁ:** **DVA GATE SE VYLUČUJÍ:** `zadani-kontrola.py` chce kotvu = živý
> `HEAD`, ale `p25-b-mutace.py` chce **čistý strom** u pěti souborů; pořadí je
> **commit → doklad → záznamy → inventář → `g3` → `validate-all` → hlavička zadání**.
>
> **⚠ SEDMÁ:** **MUTUJ PŘES `_analyza\_mutace.py`** (`mutuj`) — a když kotva není
> v celém dokumentu unikátní (např. `83/83` je v `HANDOFF.md` **15×**), **označ
> místo sentinelem** a mutuj sentinel; **kotva mimo měřený oddíl vyrobí falešný
> nález o měřidle** (naměřeno v P28, omyl P28-H/2).

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

### 0.1 P28 — Úkol A: přeměření P27 VLASTNÍM měřidlem — HOTOVO

| # | Co se ověřovalo | Výsledek |
|---|---|---|
| **A1** | umí měřidlo P27 spadnout? | **ANO, doloženo diferenciálem**: posunuté číslo v **§56** (`83/83` → `82/83`) → měřidlo spadne na kontrole „úplnost handoffu“; kopie `g3` s 50. branou → spadne A6; `ov-g` bez hlášení rozsahu → spadne A5; `p27-b` **27/0**. **NÁLEZ:** tvrzení P27 **„133/0“ dnes neplatí** → naměřeno **139/5 + 5× NEZMĚŘENO** (příčiny: **pořadí** A6 vs. inventář, 14. skill mimo repo) |
| **A2** | volá test tiku sedm endpointů? | **ANO — ale doloženo JINAK než v P27**: v kopii zdroje se poškodí **HODNOTA v odpovědi** endpointu; u **každého** ze sedmi zčervenala aspoň jedna kontrola **jeho skupiny** a **žádná** z ostatních šesti; `A: /tick odpoví 200` zůstala zelená |
| **A3** | tvrdí testy TVAR i OBSAH? | **ANO**: poškození **TEXTU dotazu** zčervenalo kontroly, které poškození hodnoty nechalo zelené (`AC: čte se CELÝ řádek`, `AD: a filtr active=1 tam NENÍ`) |
| **A4** | čísla v §57/§58 sedí? | **NEVŠECHNA — a to je nález**: `test-tick-offline` **205/0** ✓, `handoff` **83/83** ✓, `ov-g` **99 řádků** ✓, `g3` **49 bran** ✓ · **ROZCHODY:** `over-skilly` **13/0 → 14/0** (přibyl 14. skill), `validate-all` **VŠE V POŘÁDKU → 2 problémy** (stav HRY/D1), `p26-b` **26/0 → 26/2**, živě `/health ready=1 → 2`, `/roadmap 21/0 → 22/1` |
| **A5** | rozsah `ov-g-neovereno` | **POTVRZENO vlastním počítadlem**: **99 řádků Hxx** (1 v `HANDOFF.md` + 98 v archivu), mimo živé zdroje **139 v 7**; fixtury: `NEOVĚŘENO` → `exit 1`, prázdno → **NEMĚŘENO** |
| **A6** | nic se nerozbilo ani neztratilo | **NALEZEN ZTRACENÝ ZÁZNAM**: v kronice **chyběl řádek session 24** (smazal ho commit `c3ee946`); **obnoven** a `kronika-kontrola` **nově hlídá kontinuitu id** (mutace: chybí řádek 30 → `exit 1`) |
| **A7** | inventář a brány po sobě | **POTVRZENO**: otisk počítá **obě repa**, **vlastní přepočet** otisku ze záznamů = uložený `sha256`, vzorek 80 souborů sedí na **dnešní bajty**; **změna OBSAHU se stejnou velikostí** bránu shodí pojmenovaným stavem; doklad `*-vystup.txt` otisk **nemění** |

**Doklad:** `_analyza/p28-a-overeni.py --plne` → **122 kontrol, 14 chyb**
(19 červených = **19 pojmenovaných ROZDÍLŮ**, ne 19 vad kódu — každý je v §2.21)
+ `_analyza/p28-a1-vystup.txt` (diferenciál A1) + `_analyza/p28-b-mutace.py`
(27/0 — tři mutace v kopiích, každá s diferenciálem).

### 0.2 P28 — Úkol B5: SLEPÉ MÍSTO BRÁNY `over-skilly` — HOTOVO

`tools/over-skilly.py` **vidělo 71 zmínek** cest, v dokumentech jich je **90** —
**16** bylo v ``` bloku, za `python `/`node ` nebo v `--json …` (sonda
`_analyza/p28-sonda-cesty.py`). **„0 mrtvých cest“ tedy nebylo důkaz.**
Vzor je rozšířen (cesta **kdekoliv na řádku**), brána **vypisuje** počet zmínek
mimo backticky a **tři cesty skillu `vision`** dostaly **deklarovanou výjimku**
(šablona pro projekt s vlastním `.python`; skill to říká slovem „v repu“) —
**táž cesta v jiném skillu bránu pořád shodí** (měřeno). Mutační test
`_analyza/test-over-skilly-delegovane.py` **8/0 → 17/0**.

### 0.3 ⚠ CO JE VE STROMĚ NECOMMITNUTÉ (stav při psaní zadání)

| Soubor | Co to je |
|---|---|
| `tools/over-skilly.py` | **oprava B5** (rozsah tvarů cest + výjimky) |
| `_analyza/kronika-kontrola.py` | nová kontrola **kontinuity id** (P28-E) |
| `_analyza/test-over-skilly-delegovane.py` | +9 kontrol pro nový tvar cest |
| `_analyza/p20-d-doklady.py` | sonda P28 v `PRESKIP` |
| `_analyza/p28-*.py`, `_analyza/p28-*.mjs` | **měřidlo P28**, mutační důkaz, obnova kroniky, sonda, čtení živé služby |
| `_analyza/p28-*-vystup.txt`, `p28-vzdy-*.txt` | **doklady** (gitignorované, vyloučené z otisku) |
| `KRONIKA-PROJEKTU.md` | řádek **43** + **§2.21** + **obnovený řádek 24** |
| `HANDOFF.md` | **§59** (tahle session) |
| `NEXT-SESSION-INSTRUKCE.md` | **tohle zadání** (hlavička se záměrně necommituje) |
| `_analyza/_registr-bran.json` | **generovaný** `g3` — needituj ho rukou |

---

## 1. Cíl (jedna věta)

**Přeměřit práci P28 vlastním měřidlem a vzít si JEDNU věcnou práci z nabídky
§2.2** — P28 zavřela slepé místo `over-skilly` (B5), takže na řadě je
`.gitattributes` (**B2**), acceptance `B4` na živé službě (**B3**), nebo
rozhodnutí o dvou problémech `validate-all`, které patří **stavu HRY**.

**Proč to patří nové session:** P28 si psala záznamy **i měřidlo** sama a
`AGENTS.md` je v tom jednoznačné: *„autor není nezávislý reviewer“*.

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — přeměřit P28 VLASTNÍM postupem

| # | Co ověřit | Jak (návrh; klidně vlastní) |
|---|---|---|
| **A1** | umí měřidlo P28 spadnout? | Spusť `p28-a-overeni.py --plne` a `p28-b-mutace.py`; pak **v kopiích** uber to, co měřidlo hlídá (posuň číslo v §59, vypni hlášení rozsahu v `ov-g`, přidej 50. bránu do `g3`) a ověř **diferenciál** |
| **A2** | volá test tiku sedm endpointů? | **Jinak než P28** (ta poškozovala odpověď): např. **zarážkou v handleru** (vzor `p27-a-overeni.py` etapa A2) — a ověř, že zarážka zapne aspoň jednu kontrolu **své** skupiny |
| **A3** | tvrdí testy tvar i obsah? | V **KOPII** testu přinuť falešnou D1 vracet prázdné výsledky a měř, které kontroly zčervenají a které „… odpoví 200“ zůstanou zelené |
| **A4** | čísla v §59 sedí | Každý tvrzený čítač **znovu spusť** (včetně **živé služby** — jen čtení!) a porovnej s číslem **přečteným z dokumentu**; co nesedí, zapiš jako nález |
| **A5** | sedí rozsah `ov-g` i kontinuita id | Vlastním počítadlem: **99 řádků Hxx** (1 + 98) a **id 1..43 bez děr**; fixtura bez řádku → `exit 1` |
| **A6** | oprava B5 měří, co tvrdí | Ověř, že `over-skilly` **vidí nový tvar** (``` blok) a že **deklarovaná výjimka neprosakuje** do jiného skillu — a že starý tvar se nezhoršil |
| **A7** | inventář a brány po sobě | Pořadí **inventář → `g3` → `validate-all`**, mezi tím nic nezapisuj; ověř, že `g3`/`validate-all` hlásí **jen pojmenované stavy** (dnes: 1 nedeklarovaný exit = `validate-all` kvůli **hře**) |

**Doklad:** vlastní skript v `_analyza/` (název `p29-*`), spuštěný a **uložený
i s výstupem**, a **musí umět selhat** (mutační test — vzor `p28-b-mutace.py`).
Kdo přidá doklad do `_analyza/`, **přidá ho i do `_analyza/p20-d-doklady.py`**
(vzor `VZOR` ho bere sám — ověř to) a sondu do `PRESKIP`.

### 2.2 Úkol B — VĚCNÁ PRÁCE (vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **B2** | **Rozhodnout a nasadit `.gitattributes`** (P24-B) | `HANDOFF.md` §54.3 bod 2, §59.4 | `git checkout` dnes **tiše rozbíjí vícřádkové kotvy mutací** (CRLF); návrh je hotový, chybí **rozhodnutí** |
| **B3** | **Ověřit `B4` na ŽIVÉ službě** — `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**, pak hru vrátit | `HANDOFF.md` §45, §59.4, `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 (B4) | **Dočasně zastaví orchestra** → chce výslovné „ano“ uživatele. ⚠ Dnešní měření: **strop 8 nikoho neblokuje** (max pokusů **5**), takže acceptance „strop zastaví“ **není čím doložit** |
| **B4** | **Dva problémy `validate-all`** (cache hry 22 vs soubor 21 granul, 5 osiřelých řádků) | `HANDOFF.md` §59.2 bod 6 | Je to **stav HRY/D1** — patří session, která vede hru; orchestra to **neopravuje**. Rozhodni, jestli to má být **pojmenovaný stav** v bráně, nebo práce pro hru |
| **B5** | **Kontinuita id i pro ostatní evidence** (nálezy Hxx, omyly, PR) | `KRONIKA-PROJEKTU.md` §2.21 (P28-E) | U řádků session to dnes hlídá `kronika-kontrola`; u **nálezů Hxx** a **bloků omylů** ji nehlídá nikdo — a přesně tam vzniká „tichá ztráta“ |

**Podmínky:** vybrat **JEDNU** a říct kterou · než začneš měnit kód, **změř
současný stav** (ne z dokumentu) · u conductoru **zavolej živou službu** a ukaž
vadu na její odpovědi · **`done` je tvrzení, ne důkaz** · ověř nasazení **třemi
kroky** (`HTTP 200` není důkaz).

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

```
# PŘED finálním během (jinak g3/validate-all hlásí pojmenovaný STAV):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány PO SOBĚ (ne současně — obě sahají na _inventar.json):
python _analyza\g3-brany.py                 -> 49 bran, 1 deklarovaný exit
node tools\validate-all.mjs                 -> dnes 2 problémy = stav HRY
python _analyza\kronika-kontrola.py         -> SEDÍ + "chybějící id: (žádné)"
python _analyza\handoff-kontrola-uplnost.py -> úplnost handoffu
python _analyza\ov-g-neovereno.py           -> 0 NEOVĚŘENO, rozsah 99 řádků Hxx
python _analyza\p28-a-overeni.py --plne     -> 122 kontrol (14 = pojmenované rozdíly)
python _analyza\p28-b-mutace.py             -> tři mutace, každá s diferenciálem
python _analyza\p28-obnov-kroniku.py --kontrola
python _analyza\p28-zapis-zaznamu.py --kontrola
node tools\test-tick-offline.mjs            -> 205/0
python _analyza\tick-mutace.py              -> 20 vrat, 41/0
python tools\over-skilly.py                 -> 90 zmínek, 0 mrtvých
python _analyza\test-over-skilly-delegovane.py -> 17/0
python tools\over-dokumentaci.py            -> 64/0
python _analyza\zadani-kontrola.py          -> kontroluje KOTVU tohohle zadání
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem. **⚠ „Zastaralý inventář“
NENÍ deklarovatelný stav** — náprava je přegenerovat.
**⚠ KDO MĚNÍ `_analyza/g3-brany.py`, MĚNÍ I `tools/validate-all.mjs`.**
**⚠ AUTORITA SEZNAMU ŽIVÝCH BRAN JE `BRANY` v `_analyza\g3-brany.py`** — ne
ruční výčet v `HANDOFF.md` §6 (ten je **záznam z 2. 10. 2026**).

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje)
   — a **datum měření ber z hodin**.
2. **Zapiš výsledky** do `HANDOFF.md` (**nový oddíl §60**, jen **přidávej**)
   a do `KRONIKA-PROJEKTU.md`: **řádek session** (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**, a **id musí být 44** — kontinuitu hlídá `kronika-kontrola`) a
   **nálezy** do §2.
   ⚠ **OMYLY SE OD 6. 10. 2026 NEVEDOU** — do sloupce omylů patří **`—`**.
   Řádky piš **skriptem** (vzor: `_analyza/p28-zapis-zaznamu.py`): řádky mají
   **přes 2000 znaků** a kotva z načteného řádku ho **zkrátí** (omyly 194, 206).
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — měřidlem `python _analyza\ov-g-neovereno.py`
   (**ne** hledáním slova) **a zkontroluj jeho ROZSAH** (musí hlásit **99 řádků Hxx**).
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE SOUČASNĚ**),
   inventář **jako POSLEDNÍ krok**.
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Práce P28 je přeměřená, ne odsouhlasená** | A1: měřidlo projde **a** po vrácení vady spadne (diferenciál) |
| 2 | **Sedm endpointů je doložených i DRUHÝM postupem** | A2: zarážka v handleru zapne kontroly u **každého** z nich |
| 3 | **Čísla v §59 sedí** | A4: každý tvrzený čítač naměřen znovu; co nesedí, je zapsaný nález |
| 4 | **Kontinuita id a rozsah `ov-g`** | A5: **99 řádků Hxx** a **id 1..43 bez děr** |
| 5 | **Nic se nepřepsalo** | `git diff --numstat HEAD` u `HANDOFF.md`/`KRONIKA` = **0 smazaných řádků** |
| 6 | **Nic se nerozbilo** | `g3` → 49 bran, jen **pojmenované** exity; `validate-all` → **jen stav HRY** |
| 7 | **Věcná práce je VYBRANÁ a hotová** (nebo pojmenovaná jako čekající na uživatele) | §2.2: jedna položka, se stavem před/po |
| 8 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 9 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEDĚLEJ Z KONTROLY CÍL.** Ověřit máš **práci P28**, ne přidávat další
  měřidla. Nová brána je na místě **jen** tam, kde je doložená vada měření.
- **⚠ NESAHEJ NA ROZDĚLANOU PRÁCI SOUBĚŽNÉ SESSION** — necommituj ji, neopravuj
  ji, nemaž ji; její je i obsah `_analyza/_registr-bran.json` (generovaný).
- **Nesahej na hru** (`uo-shadows`) — dnes je sice **v sync s `origin/main`**,
  ale vede ji cizí session. **Nemaž `_acl-recovery/`** (netrackovaný artefakt).
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§56 = P26, §57/§58 = P27, §59 = P28).
- **Nemaž `_analyza/p2[4-8]-*`, `*-mutace.py`, `tick-mutace.py` ani `ov-*`** —
  jsou to **doklady**; a **nemaž `_archiv`** (cesta zpět, **98** řádků Hxx).
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ** (obě sahají na inventář).
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM) a **nepoužívej `python -c`**
  s českým textem ani s `→`.
- **⚠ NEPŘERUŠUJ MUTAČNÍ BĚH** — po přerušení zůstanou mutanti v živém zdroji
  (a **ze hry** zůstane viset `tools/gates/mutace-tests.py`; když po přerušení
  zůstane, ověř `git status` ve hře a proces ukonči **až po** kontrole stromu).
- **⚠ POZOR NA `git checkout` NAD `conductor/src/index.ts`** — CRLF a rozbité
  vícřádkové kotvy.
- **Nepřesouvej nic zpátky na `C:`** a nemaž `E:\Workspaces\_acl-oprava-*`.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (8. 10. 2026, ~19:2x +02:00)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD            -> fffc8e7
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0 (P27 PUSHNUTA)
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD            -> 8fe57ce
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD -> 0 (CIZI session pushla)
tools\git.cmd ls-remote origin refs/heads/main   # zivy stav bez zapisu do .git

# ziva sluzba (8. 10. 2026, ~19:0x +02:00) - JEN CTENI
node _analyza\p28-ziva-sluzba.mjs
#   /health ok=true ready=2 running=0 games=1 · /roadmap 22 granul (19 done, 2 queued,
#   1 blocked), max pokusu 5 · 6 chranenych endpointu: bez tajemstvi 401, s nim 200

# brany po P28
python _analyza\p28-a-overeni.py --plne     -> 122 kontrol, 14 chyb (= pojmenovane rozdily)
python _analyza\p28-b-mutace.py             -> tri mutace v kopiich, kazda s diferencialem
node tools\test-tick-offline.mjs            -> 205/0
python _analyza\tick-mutace.py              -> 20 vrat, 41/0
python _analyza\g3-brany.py                 -> 49 bran, 1 deklarovany + 1 NEDEKLAROVANY exit
node tools\validate-all.mjs                 -> 2 problemy (cache hry 22 vs soubor 21; 5 osirelych)
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI (43 radku, zadna dira)
python _analyza\handoff-kontrola-uplnost.py -> uplnost handoffu
python _analyza\ov-g-neovereno.py           -> 0 NEOVERENO, ROZSAH 99 radku Hxx
python tools\over-skilly.py                 -> 14 skillu, 0 chyb, 90 zminek, 0 mrtvych
python _analyza\test-over-skilly-delegovane.py -> 17/0
python tools\over-dokumentaci.py            -> 64/0

# NALEZY P28, ktere usetri cas (kazdy dolozen merenim):
#  * p27-a --plne ma dnes 139/5 + 5x NEZMENENO (tvrzeni 133/0) — 3 chyby jsou VADA
#    PORADI (A6 pousti g3/validate-all nad inventarem, ktery si run sam zneplatnil).
#  * p26-b ma 26/2: jeho diferencial zhazuje TRVALE cervena p26-a (14. skill mimo repo).
#  * validate-all 2 problemy = stav HRY/D1 (cache vs soubor), ne orchestra.
#  * strop 8 NEBLOKUJE (max pokusu 5) -> acceptance B4 neni cim dolozit.
#  * kronika mela ZTRACENY radek 24 (smazal c3ee946) — obnoven, kontinuita id hlidana.
#  * dve brany maji RŮZNY TVAR CITACE: "Kontrol: N, chyb: M" vs "N kontrol, M chyb".
#  * kotva mutace MUSI lezet v merenem oddilu (83/83 je v HANDOFF.md 15x).
#  * python -c s "→" v PowerShellu vraci 0 vyskytu -> pis skript do souboru.

# ⚠ TRIK PRO PUSH (PAT se NIKDY nevypisuje):
#   $pat = (Get-Content .secrets\github_pat.txt -Raw).Trim()
#   $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$pat"))
#   & .\tools\git.cmd -c "http.extraHeader=AUTHORIZATION: basic $b64" push origin main
```

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P29. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows  (vede ji CIZI session — jen ověřuj, nepiš do ní)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P28 PŘEMĚŘILA práci P27 vlastním měřidlem (p28-a-overeni.py,
122 kontrol; 14 červených = 14 POJMENOVANÝCH ROZDÍLŮ) a OPRAVILA slepé místo
brány over-skilly (viděla 71 zmínek cest, v dokumentech jich je 90 — 16 bylo
v ``` bloku nebo za `python …`). Navíc se našel ZTRACENÝ ZÁZNAM: v kronice
chyběl řádek session 24 (smazal ho commit c3ee946) — je obnoven bajt na bajt
a kronika-kontrola teď hlídá kontinuitu id.

DŮLEŽITÉ, CO P28 NAMĚŘILA: tvrzení P27 "p27-a --plne → 133/0" DNES NEPLATÍ —
naměřeno 139/5 + 5× NEZMĚŘENO; tři z těch chyb jsou VADA POŘADÍ (měřidlo P27
pouští g3 a validate-all poté, co si jeho vlastní etapy zneplatnily inventář).
validate-all dnes hlásí 2 problémy, ale oba jsou o STAVU HRY (cache 22 řádků vs
soubor 21 granul, 5 osiřelých), ne o orchestra. Strop granulí 8 NIKOHO NEBLOKUJE
(max pokusů 5), takže acceptance B4 pořád není čím doložit.

POZOR: ve workspace může pracovat SOUBĚŽNÁ session — její práci necommituj,
neopravuj a nemaž. Před commitem kontroluj INDEX (git show :soubor). Nepoužívej
git show <sha>^ (git.cmd žere ^). Needituj .py přes Set-Content (přidá BOM).
NEPŘERUŠUJ mutační běh. BĚHEM PLNÉHO BĚHU MĚŘIDLA NEPIŠ DO STROMU (obsahový
otisk vstupů se rozjede). Kotvu mutace ber z MĚŘENÉHO ODDÍLU (83/83 je
v HANDOFF.md 15×). A nepoužívej python -c s českým textem ani s "→".

Než začneš: git status --porcelain v obou repech a ověř ŽIVÝ stav — git fetch
v sandboxu padá (.git/FETCH_HEAD), použij `tools\git.cmd ls-remote`. A DATUM
MĚŘENÍ BER Z HODIN, ne ze zadání.

TVŮJ ÚKOL: přeměř P28 vlastním měřidlem (§2.1 A1–A7) a pak si vyber JEDNU věcnou
práci (§2.2) — na řadě je B2 (.gitattributes), B3 (acceptance B4 živě — chce
"ano" uživatele), B4 (dva problémy validate-all = stav hry) nebo B5 (kontinuita
id i pro nálezy Hxx a bloky omylů).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky do HANDOFF.md
(nový oddíl §60) a do KRONIKY (řádek 44 + nálezy; omyly = "—"), ověř, že
nezůstalo NEOVĚŘENO (měřidlem ov-g-neovereno.py VČETNĚ ROZSAHU, ne hledáním
slova), přegeneruj inventář JAKO POSLEDNÍ KROK, spusť g3 a pak validate-all
(ne současně) a do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

---

**STAVOVÝ ŘÁDEK (8. 10. 2026, ~20:3x +02:00):** orchestra **`fffc8e7`**
= `origin/main` (**P27 PUSHNUTA**, 0 nepushnutých) + **necommitnutá práce P28**
(`tools/over-skilly.py`, `_analyza/kronika-kontrola.py`, `_analyza/p20-d-doklady.py`,
`_analyza/test-over-skilly-delegovane.py`, `_analyza/p28-*`, `KRONIKA-PROJEKTU.md`,
`HANDOFF.md`) · hra **`8fe57ce`** = `origin/main` (cizí session píše PRŮBĚŽNĚ;
P28 do ní nezapsala) · živá služba `/health` →
`ok=true ready=2 running=0 games=1`, `/roadmap` **22 granul** (19 done, 2 queued,
1 blocked; **max pokusů 5**) · brány: `g3` **49 bran / 1 deklarovaný + 1
NEDEKLAROVANÝ exit** (`validate-all` kvůli **stavu HRY**), `validate-all`
**2 problémy** (oba o hře/D1), `test-tick-offline` **205/0**, `over-skilly`
**90 zmínek / 0 mrtvých** (B5), mutační dvojče **17/0**, `kronika-kontrola`
**SEDÍ** (43 řádků, kontinuita id) · inventář **čerstvý** (přegenerován poslední).

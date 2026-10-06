# ZADÁNÍ PRO DALŠÍ SESSION — NEZÁVISLE OVĚŘIT DOPLNĚNÉ ZÁZNAMY (a neztratit, co se doplnilo)

**Co tenhle dokument JE:** **zadání pro session P23**. Nahrazuje zadání z P21
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md` — dnešní stav je **§2.12**,
nejnovější záznam **§40**) ani kronika (ta je v `KRONIKA-PROJEKTU.md`).

**Stav obou repů při psaní:** `forge-orchestra` = `db1b926` · `uo-shadows` = `44dd454`
`origin/main` orchestry = **`db1b926`** (**pushnuto**, `origin/main..HEAD` = **0**) ·
`origin/main` hry = **shodná**, strom orchestry má **jen necommitnuté záznamy**
**Zkontrolováno při:** **6. 10. 2026, 17:5x +02:00 = 15:5x UTC**

<!--
⚠ PROČ TENHLE KOMENTÁŘ EXISTUJE (naměřeno 6. 10. 2026, při psaní tohohle zadání):
`_analyza/zadani-kontrola.py` hledá tvrzený commit vzorem
`` `?([A-Za-z0-9_-]+)`?\s*=\s*`?([0-9a-f]{7,40})`? `` — tedy **`<repo> = <sha>`**.
Formulace „`db1b926` = forge-orchestra“ (sha první) mu **neunikne jako nález**:
vypíše `zadání netvrdí žádný commit` a `exit 1`. Dvě kola jsem hledal chybu
v regexu (a v `python -c`, kde se vzor rozbil o PowerShell) — správná odpověď
je **napsat to, co brána hledá**: kotva se píše ve tvaru `<repo> = <sha>`.
Tenhle komentář je proto i NÁVOD pro příští session: **drž tvar, ne vzor.**
-->

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `db1b926` · `uo-shadows` = `44dd454`
**Kotva pro měření:** `db1b926` (na něm se měřilo; **po každém dalším commitu
bude `zadání kontrola` hlásit „přibylo commitů" — a to je správně**, nález NA31)

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech — a **ověř `origin/main..HEAD` ŽIVĚ** (`git ls-remote`), ne
> podle tohohle textu. Tenhle dokument je **stav v čase psaní**.
>
> **⚠ DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu (skill `dsh-prostredi` §5c). Používej **`~1`**, nebo **`git.exe`**.
>
> **⚠ TŘETÍ:** **`Set-Content -Encoding utf8` v PowerShellu přidá do `.py` BOM**
> → soubor přestane být zkompilovatelný (omyl **189**). Kód edituj
> **`edit`/`write` toolem**; po zápisu zkontroluj **první tři bajty**
> (`.py` **NESMÍ** mít BOM, `.ps1` **MUSÍ**).
>
> **⚠ ČTVRTÁ:** **NEDĚLEJ KOTVU Z ŘÁDKU, KTERÝ SE TI NAČTE ZKRÁCENÝ.** Řádky
> v `KRONIKA-PROJEKTU.md` mají **přes 2000 znaků**; „vložení" kotvou z načteného
> řádku **nahradí celý řádek** zkráceným textem (omyly **194**, **206**).
> Zápisy do dokumentů veď **programově** (vzory: `_analyza/p21-zapis-kroniky.py`,
> `_analyza/p22-zapis-zaznamu.py` — oba **idempotentní**).

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

| # | Co se udělalo | Doklad |
|---|---|---|
| **P20/P21** | `g3` soudí červené (`OCEKAVANE_NENULOVE` **s kódem**), BOM v `.py` zakázán, H101 (tichá díra v H79) opraven, P20 dohledána a **pushnuta** | `HANDOFF.md` **§38**, **§39** |
| **P22** | **Optimalizace KB: 10 z 24 bodů** — mrtvé cesty **45 → 7**, brána na **pravdivost KB** (`over-skilly.py`), `.py` BOM v `DSH_HOME`, pojistka proti zápisu v `p20-d`, tři vyvrácená tvrzení, `_mutace.py` + sabotážní test, `g3` bere `FORGE_STANICE`/`FORGE_HRA`, rejstřík a tombstone | `HANDOFF.md` **§40**, `KRONIKA` **řádek 36** |
| **Záznamy P22** | P22 **nezapsala záznamy** („P22" bylo v `HANDOFF.md` i `KRONIKA` **0×**) → dopsáno: **§40**, **řádek 36**, **2.16**, blok omylů **`8za`** (omyly **211–213**) | `_analyza/p22-zapis-zaznamu.py` (**35/0**) |
| **Brány po zápisech** | `kronika-kontrola` → **`KRONIKA SEDÍ` (208 omylů / 27 bloků / 35 sessions)** · `handoff-kontrola-uplnost` → **83/83** · `over-skilly` → **13/0, 0 mrtvých cest** · `over-dokumentaci` → **67/0** | `HANDOFF.md` §40.3 |

**⚠ CO SE ZMĚNILO NA BRANÁCH (a je to důležité pro čtení čísel):**
`_analyza/kronika-kontrola.py` má **nově vzor bloku omylů `8[a-z]{0,2}`** (bylo
`8[a-z]?`) — bez toho by nešel zapsat blok **`8za`** (jednoznakové názvy jsou
obsazené). **A je k tomu naměřená past:** první pokus použil `{1,2}`, což
**ZTRATILO základní blok `## 8.`** a s ním **13 omylů** (součet spadl
205 → 195). Našla to **brána**, ne oko. **Kdo bude vzor měnit, ať ví, že `?` je
„0 nebo 1" a `{1,2}` je „1 nebo 2".**

---

## 1. Cíl (jedna věta)

**Nezávisle přeměřit práci, kterou jsem zapsal sám (záznamy P22 + doplnění),
a ověřit, že se při ní NIC NEZTRATILO — a teprve pak se vrátit k věcné práci.**

**Proč to patří nové session:** ty záznamy psal **autor téže session, která je
i ověřovala** — a `AGENTS.md` je v tom jednoznačné: *„autor není nezávislý
reviewer"*. Navíc se do dokumentů přidalo **~13 tis. znaků** (dva bloky omylů,
dvě sekce, oddíl, řádek, plus **změna brány**), tedy přesně ten druh zásahu,
u kterého se „nic nezmizelo" **dokazuje hledáním, ne pamětí**.

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — nezávislé přeměření doplněných záznamů

Každý bod měř **jiným postupem**, než jak vznikl (ne „přečtu to a souhlasím"):

| # | Co ověřit | Jak (návrh, klidně si zvol vlastní) |
|---|---|---|
| **A1** | **Omyly 211–213 jsou doložené, ne vymyšlené** | Hlavička `REVIZE-PRACOVNIHO-RITUALU.md` tvrdí **tři** vlastní chyby P22 (neuznaný typ session; starý název sekce ve skriptu; skript čte živý soubor místo zadaného). Ověř, že (a) každá z nich je **měřitelná** — např. že `kronika-kontrola.py:374` opravdu zná **pět** typů, (b) že v `HANDOFF.md` §8za **nejsou jiné** než ty tři, (c) že v `REVIZE` **nejsou zmíněné další** vlastní chyby (hledej slova „omyl", „chyba", „neuznaný", „skript"). Když najdeš čtvrtou, **dopiš ji** (blok `8za` se rozšíří, součet v kronice §3 se přepočítá) |
| **A2** | **Součet 208 sedí na řádky, ne na tvrzení** | `python _analyza\kronika-kontrola.py` → musí hlásit **208** a **vypisovat, které bloky sečetl** (27). Pak **vlastním skriptem** sečti sloupec „Počet omylů" tabulky §3 — obě čísla musí být **208**. A ověř, že blok **`1–13` je v součtu** (přesně ten se ztratil při chybě `{1,2}`) |
| **A3** | **Brána umí OBĚ strany té změny** | Vzor `8[a-z]{0,2}` musí brát **základní `## 8.`**, **jednoznakové `8b`** i **dvouznakové `8za`**. Dokaž to **fixturou** (ne dojmem): vezmi **kopii** `HANDOFF.md`, uber z ní nadpis `### 8za.` a spusť bránu s tou kopií (`kronika-kontrola.py <KRONIKA> <HANDOFF>`) — musí hlásit rozchod. Totéž pro uberení `## 8.` |
| **A4** | **Nic nezmizelo** | `python _analyza\handoff-kontrola-uplnost.py` → **83/83, CHYBÍ 0**; a **nezávisle**: `git diff --stat` proti `db1b926` musí ukázat **jen přidání** (`+`), žádné mazání obsahu. U kroniky porovnej **řádky 1–35** proti `git show db1b926:KRONIKA-PROJEKTU.md` — musí být **bajt na bajt** |
| **A5** | **Hra a conductor nejsou dotčené** | `git diff --name-only db1b926..HEAD` nesmí obsahovat nic z `conductor/`; `uo-shadows` musí být `44dd454` a čistý. (Kdyby v `conductor/` něco bylo, **deploy.yml se spustí** — a to je nasazení živé služby) |
| **A6** | **Odkazy v nových textech existují** | Všechny soubory zmíněné v §40, §2.16 a `8za` (`REVIZE-PRACOVNIHO-RITUALU.md`, `OPTIMALIZACE-KNOWLEDGE-BASE.md`, `_tools\over-cesty-v-kb.mjs`, `_analyza\_mutace.py`, `p22-test-mutace.py`, `_tools\rozpad-session.mjs`) **fyzicky existují** — ověř `Test-Path`/`is_file`, ne grep |
| **A7** | **Tvrzení o pushi je dnešní** | `git ls-remote origin refs/heads/main` = **`HEAD`**, `origin/main..HEAD` = **0**. (Tři dokumenty stanice tvrdily „nepushnuto" a byly opraveny — ověř, že **dnešní** text nikde netvrdí opak) |

**Doklad:** vlastní skript v `_analyza/` (název `p23-*`), spuštěný a **uložený
i s výstupem**; **a musí umět selhat** (mutační test: uber v kopii dokumentu
jeden nadpis omylů a sleduj, že skript spadne). Kdo přidá doklad do `_analyza/`,
**přidá ho i do `_analyza/p20-d-doklady.py`** — jinak shnije.

### 2.2 Úkol B — VĚCNÁ PRÁCE (teprve po Úkolu A)

**⚠ Zbývající body KB NEPROVÁDĚJ bez rozhodnutí uživatele** — tři z nich mění
**trvalá pravidla** a jeden **přesouvá 569 tis. znaků historie**; zadání je
`C:\Users\Ssevc\Local-Deepseek\ZADANI-OPTIMALIZACE-KB.md`.

**Nabídka věcné práce (vyber JEDNU a řekni kterou):**

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **C1** | **conductor: O3 — opravit vady a nasadit** (B1 `naposledy_selhalo`, B2 `/report`, B3 strop a watchdog, B4 `listGames`, B5 komentáře `:31`/`:233`) | `HANDOFF.md` **§2.2**, `PLAN-ROZVOJ-ORCHESTRA.md` **§3.5 (fáze B)** | Conductor je **živá služba** a jeho vady se projeví v **každém běhu agenta** |
| **C2** | **conductor: N0.3 — stav CI cílové hry v `/health`** | `HANDOFF.md` **§2.5** | Bez toho conductor **nevidí**, že cíl má červené CI. Naměřeno **1. 10. 2026: 7,5 h bez práce** kvůli červenému CI cíle — a conductor přitom hlásil `ok: true` |
| **O1** | **orchestra: rozhodnout O10 a O5–O8** | `PLAN-ROZVOJ-ORCHESTRA.md` **§6** | Jsou to **rozhodnutí**, ne kód — hodí se, když se nemá sahat na živou službu |
| **K1** | **KB: 14 zbývajících bodů** (`§6.4`, `§6.5`, `§6.6`, `§6.8`, `§6.11`, `§6.14`, `§6.15`) | `ZADANI-OPTIMALIZACE-KB.md` | **Ale POZOR:** `§6.5`, `§6.6`, `§6.8` se smí dělat **jen jako PŘESUN** (auditovy důvody byly vyvráceny **3 ze 3**) a `§6.11` je **přepis stavu** — chce rozhodnutí uživatele |

**Podmínky:** vybrat **JEDNU** a říct kterou · než začneš měnit kód, **změř
současný stav** (ne z dokumentu) · u conductoru **zavolej živou službu** a ukaž
vadu na její odpovědi · **`done` je tvrzení, ne důkaz** · ověř nasazení
**třemi kroky** (`HTTP 200` není důkaz).

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

Po P22 a po dopsání záznamů je **stav bran jiný** — tohle je nový baseline:

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány PO SOBĚ (ne současně — obě sahají na _inventar.json):
python _analyza\g3-brany.py                 -> 37 bran, 1 nenulový (zadani kontrola,
                                               DEKLAROVANY), exit 0
node tools\validate-all.mjs                 -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI (208 omylu / 27 bloku / 35 sessions)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\ov-g-neovereno.py           -> 0 ve stavu NEOVERENO
python tools\over-skilly.py                 -> 13 skillu, 0 chyb, 0 mrtvych cest
python _analyza\p20-d-doklady.py            -> doklady vc. p22-zapis-zaznamu.py; cerveny
                                               zustava H103 (falesny poplach, NEOPRAVOVAT)
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem.
**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`.**
**⚠ `p20-d-doklady.py` spouští i ZAPISUJÍCÍ skripty** (`p21-*`, `p22-*` píšou
do `KRONIKA-PROJEKTU.md`) — dávka to **vypíše** (pojistka z P22). Změna
dokumentu v dávce **není sama o sobě vada**, ale musí být vidět.

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje).
2. **Zapiš výsledky a omyly** do `HANDOFF.md` (**nový oddíl**, jen **přidávej**)
   a do `KRONIKA-PROJEKTU.md`: **řádek session** do §1 (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**, omyl **211**), **nálezy** do §2, **omyly** do §3 tabulky
   **a do `HANDOFF.md` §8** (nový blok `8zb`), **souhrn `celkem`**.
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE SOUČASNĚ**),
   inventář **jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Doplněné záznamy jsou PŘEMĚŘENÉ, ne odsouhlasené** | každý bod A1–A7 má **vlastní měření** (skript), ne čtení |
| 2 | **Brána umí selhat i na té změně** | fixtura A3: uberený nadpis bloku → brána **ohlásí rozchod** |
| 3 | **Nic nezmizelo** | `handoff-kontrola-uplnost` **83/83**; `git diff` u kroniky = **jen přidání**; řádky 1–35 **bajt na bajt** |
| 4 | **Součty sedí** | kronika §3 = **součet řádků** = čítač brány (**208**) |
| 5 | **Nic se nerozbilo** | `g3` → `exit 0` (37 bran, 1 deklarovaný); `validate-all` → `✓ VŠE V POŘÁDKU` |
| 6 | **Žádné `NEOVĚŘENO`** | ověřeno **skriptem** |
| 7 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEZAČÍNEJ DALŠÍM MĚŘIDLEM** — pokud to není **fixtura k Úkolu A3**.
  Fronta technického dluhu je dočerpaná; kdo začne „ještě jednou kontrolou
  bran", **neposune projekt**.
- **Nesahej na hru** — uživatel ji **záměrně pozastavil** (chystá přepis
  architektury zadání hry); H1/H2 **nejsou na řadě**.
- **Neopravuj `tools/lint-roadmapa.py:30`** — je to **doložený falešný poplach**
  (H103).
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§2.10 = k P19, §2.11 = k P20, §2.12 = k P21).
- **Nemaž `_analyza/p16*`–`p22*` ani `ov-*`** (jsou to **doklady**) a **nemaž
  `_archiv`** (je to cesta zpět).
- **Nepřesouvej nic zpátky na `C:`**; zálohu v `C:\...\Local-Deepseek\_zalohy\` nemařit.
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ**.
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM — omyl **189**).
- **Nepoužívej `python - <<'PY'`** (heredoc v PowerShellu neexistuje) ani
  `python -c` s regexy nebo `$()` — **piš skript do souboru**.
- **⚠ NEMĚŇ VZOR BLOKU OMILŮ V BRÁNĚ, DOKUD SI NEUJISTÍŠ KVANTIFIKÁTOR** —
  `?` je **0 nebo 1**, `{1,2}` je **1 nebo 2**. Chyba `{1,2}` stála 13 omylů
  a odhalila ji až brána.
- **Nespoléhej na to, „co tvrdí P22 nebo tenhle zápis"** — **každé tvrzení
  přeměř**. Tenhle zápis psal autor, který sám sebe ověřoval.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (6. 10. 2026, 15:5x UTC = 17:5x +02:00)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD         -> db1b926
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main   -> db1b926
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD          -> 44dd454 (= origin/main)

# brany po doplnenych zaznamech (session, ktera je psala)
python _analyza\kronika-kontrola.py          -> KRONIKA SEDI (208 omylu / 27 bloku / 35 sessions)
python _analyza\handoff-kontrola-uplnost.py  -> 83/83, CHYBI 0
python _analyza\p22-zapis-zaznamu.py         -> 35 kontrol, 0 chyb (idempotentni)
python tools\over-skilly.py                  -> 13 skillu, 0 chyb, 40 zminek cest, 0 mrtvych
python tools\over-dokumentaci.py             -> 67 kontrol, 0 chyb

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ IZOLACE (plati dal): `git worktree` MUSI lezet uvnitr `E:\Workspaces`
#   a MUSI mit junction `uo-shadows` na zivou hru; a NESMI lezet v merenem stromi.
# ⚠ BRANY POTREBUJI PRAVO ZAPISU MIMO WORKSPACE (stavi si pracovni kopie
#   v `_analyza\a-ukol-scratch\`) — v omezenem sandboxu spadnou na PermissionError.
```

**Uložené doklady, které k tomu patří:** `_analyza/p22-zapis-zaznamu.py`
(**35/0**, idempotentní zápis řádku session 36, sekce 2.16, bloku `8za` a oddílu
§40 — bere kotvy **z disku**, ne ze zkráceného čtení) a `_analyza/p22-test-mutace.py`
(**19/0**, sabotážní test mutační knihovny).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P23. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — nesahej na ni)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P22 udělala 10 z 24 bodů optimalizace znalostní báze (mrtvé cesty
45 -> 7, brána na pravdivost KB v over-skilly.py, .py BOM do DSH_HOME, pojistka
proti zápisu v p20-d, _mutace.py se sabotážním testem, g3 bere FORGE_STANICE/FORGE_HRA)
— ale NEZAPSALA záznamy: v HANDOFF.md ani KRONIKA-PROJEKTU.md nebylo slovo "P22"
ani jednou. Dopsalo se to dodatečně (HANDOFF §40, kronika řádek 36 + 2.16 + blok
omylů 8za s omyly 211-213) a všech 10 commitů P22 je PUSHNUTÝCH (db1b926).

TVŮJ ÚKOL JE NEPŘÍJEMNÝ, ALE DŮLEŽITÝ: ty záznamy psal autor, který sám sebe
ověřoval — a AGENTS.md říká "autor není nezávislý reviewer". Přeměř je VLASTNÍM
měřidlem (§2.1 A1-A7): jsou omyly 211-213 doložené? sedí součet 208 na řádky
tabulky? umí brána OBĚ strany změny vzoru (fixtura: uber nadpis a čekej rozchod)?
nezmizelo nic (handoff 83/83 + diff jen přidání + řádky 1-35 bajt na bajt)?

Pozor: změna vzoru bloku omylů v kronika-kontrola.py na 8[a-z]{0,2} — první pokus
s {1,2} ZTRATIL základní blok ## 8. a 13 omylů. ? je "0 nebo 1", {1,2} je "1 nebo 2".

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS).
Nepoužívej git show <sha>^ (git.cmd žere ^), needituj .py přes Set-Content (přidá
BOM) a nedělej kotvu z řádku, který se ti načte zkrácený (omyl 206).

Zbývající body KB (ZADANI-OPTIMALIZACE-KB.md) NEPROVÁDĚJ bez rozhodnutí uživatele:
tři z nich mění trvalá pravidla a jeden přesouvá 569 tis. znaků historie. A POZOR:
§6.5/6.6/6.8 se smí dělat JEN jako PŘESUN — audit tvrdil, že ta místa duplikují
jiná, a přeměření to vyvrátilo ve 3 ze 3 případů.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky a omyly do
HANDOFF.md (nový oddíl + nový blok omylů) a do KRONIKY (řádek session + nálezy
+ souhrn celkem), ověř, že nezůstalo NEOVĚŘENO, přegeneruj inventář JAKO POSLEDNÍ
KROK, spusť g3 a pak validate-all (ne současně) a do chatu vlož prompt pro
uživatele i se STAVOVÝM ŘÁDKEM.
```

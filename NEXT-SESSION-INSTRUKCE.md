# ZADÁNÍ PRO DALŠÍ SESSION — DOKONČIT SLEPÁ MÍSTA ROZHODOVACÍ LOGIKY (a nespálit při tom živou službu)

**Co tenhle dokument JE:** **zadání pro session P25**. Nahrazuje zadání z P24
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, nejnovější oddíl **§54**)
ani kronika (ta je v `KRONIKA-PROJEKTU.md`, nejnovější řádek **39**,
nálezy **§2.17**).

**Stav obou repů při psaní:** `forge-orchestra` = `4925f64` · `uo-shadows` = `44dd454`
`origin/main` orchestry = **`c664dde`** — **1 nepushnutý commit** (`4925f64`,
archivace 25 nástrojů = práce **SOUBĚŽNÉ session**; **není moje a necommituj ji**).
`origin/main` hry = **shodná**, strom orchestry má **necommitnutou práci P24**
(viz §0.3) a průběžně i práci souběžné session.
**Zkontrolováno při:** **7. 10. 2026, 10:0x +02:00 = 08:0x UTC**

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `4925f64` · `uo-shadows` = `44dd454`
**Kotva pro měření:** `4925f64` (na něm se měřilo; **po každém dalším commitu
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
> **⚠ ČTVRTÁ (NOVÁ, naměřená 7. 10. 2026, P24):** **`git checkout` TICHE ROZBIJE
> MUTAČNÍ DOKLADY.** Repo orchestra **nemá kořenový `.gitattributes`** (má ho jen
> šablona `repo/`) a `core.autocrlf=true` → checkout přepíše `.ts` na **CRLF**,
> vícřádkové kotvy mutací (`…\n               naposledy_selhalo …`) pak hlásí
> **„kotva v souboru NENÍ"**, což vypadá jako vada TESTU — a **`git status` je
> přitom čistý**. Stav se opravuje obnovením **bajtů z blobu** (LF). Podrobně
> `HANDOFF.md` §54.3 bod 2.
>
> **⚠ PÁTÁ (NOVÁ):** **`git checkout`/`git restore` na `conductor/src/index.ts`
> nikdy nespouštěj „jen tak"** — viz čtvrtá. A **PowerShell `>` píše UTF-16LE**;
> evidenční soubory si nech zapisovat **programem** (UTF-8), ne přes `>`.
>
> **⚠ ŠESTÁ (NOVÁ):** **PŘERUŠENÝ MUTAČNÍ BĚH NENÍ NEHODA, JE TO STAV.** V P24
> zůstaly po pádu pipeline **čtyři mutanty v živém `conductor/src/index.ts`**.
> Než začneš mutovat, ověř `git status`; po každém skriptu zkontroluj návrat.
> `_analyza/p24-a-overeni.py` to dělá za tebe (A3 + A4).

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

### 0.1 P24 — nezávislé přeměření nasazení P23 (Úkol A) — HOTOVO

| # | Co se ověřilo | Výsledek |
|---|---|---|
| **A1** | živá služba běží na commitu, který se tvrdí | **POTVRZENO**: poslední úspěšný `deploy.yml` = **#33** na `head_sha 598e207`; `598e207` je poslední commit měnící `conductor/**`; **bloby** `index.ts` i `wrangler.toml` v něm a v `HEAD` **shodné**; živé `/health` vrací `targets[]` |
| **A2** | watchdog eskaluje | **POTVRZENO s výhradou**: `/tick` → `watchdog: 0 ohlášeno (prah 3)`; prah **3 = zdroj** a je **POD** `MAX_ATTEMPTS=5`. ⚠ **Stav granul v D1 je NEZMĚŘENO** — conductor `roadmap.eskalovano` **nikde nevrací** a D1 přes REST nejde |
| **A3** | v commitech nejsou mutanty | **POTVRZENO**: 40 kotv z 21 mutačních skriptů ověřeno v **blobech** `598e207`, `7f0b2f8`, `HEAD`; `disk == index == HEAD` |
| **A4** | brány umí selhat | **POTVRZENO**: 6 důkazů zelených + ruční mutace mimo knihovnu branu shodila |
| **A5** | nic nezmizelo | **POTVRZENO**: handoff **83/83**; kronika v rozsahu P23 = **0 smazaných řádků**; v posledních 6 commitech **žádný smazaný řádek session** |
| **A6** | čísla v plánech sedí na kód | **POTVRZENO**: 12 bran znovu spuštěno, čítače přesně odpovídají (21/0+11/0, 17/0+11/0, 8/0+9/0, 10/0+9/0, 22/0+11/0, 40/0+17/0) |
| **A7** | souběh se souběžnou session | **POTVRZENO, ale OTÁZKA ZADÁNÍ BYLA ŠPATNÁ** (ptala se na průnik, rozhoduje pořadí: `f8595de` je potomek `598e207`) |
| **A8** | hra nedotčená | **POTVRZENO**: `44dd454`, čistá, 0 nepushnutých, v rozsahu P23 nic z cesty do hry |

**Doklad:** `_analyza/p24-a-overeni.py` (**99 kontrol, 0 chyb**) +
`_analyza/p24-b-mutace.py` (**17 kontrol, 0 chyb** — dokazuje, že měřidlo umí
spadnout). Záznam: `HANDOFF.md` **§54**, kronika **řádek 39** a **§2.17**.

### 0.2 P24 — Úkol B3: endpointy, které netestoval NIKDO — HOTOVO

`tools/test-tick-offline.mjs` nově volá **skutečný handler** i pro `/poll`,
`/claim`, `/heartbeat`, `/tasks/cleanup` a `/roadmap/reset`:
**100 kontrol, 0 chyb** (bylo 40). Mutační důkaz `_analyza/tick-mutace.py` má
**15 vrat / 31 kontrol, 0 chyb** (bylo 8/17) — včetně `dry_run`, který nesmí mazat,
a pojistky „roadmapa se nedá načíst → nemažu".

### 0.3 ⚠ CO JE V STROMĚ NECOMMITNUTÉ (stav k 7. 10. 2026, 10:0x)

**Moje (P24), čeká na rozhodnutí o commitu:**

| Soubor | Co to je |
|---|---|
| `_analyza/p24-a-overeni.py` | měřidlo A1–A8 (**nový**) |
| `_analyza/p24-b-mutace.py` | jeho mutační důkaz (**nový**) |
| `_analyza/p24-sonda-site.py`, `_analyza/p24-sonda-m2.py` | jednorázové sondy (**nové**, v `p20-d-doklady.py` jsou v `PRESKOCIT`) |
| `_analyza/p24-radek-kroniky.py` | zápis záznamů (**nový**) |
| `tools/test-tick-offline.mjs` | +304 řádků (endpointy) |
| `_analyza/tick-mutace.py` | +7 vrat |
| `_analyza/p20-d-doklady.py` | `VZOR` bere i `p2[0-9]-`, sondy v `PRESKOCIT` |
| `HANDOFF.md`, `KRONIKA-PROJEKTU.md` | §54, řádek 39, §2.17 |

**Cizí (souběžná session, generalizace nástrojů):** `_analyza/_registr-bran.json`
(jeho obsah je **generovaný** — přepsal ho běh `g3`). **Nepatří mi** — ale je to
**generovaný** soubor, takže „necommitovat" znamená jen „nerozhodovat o něm".

---

## 1. Cíl (jedna věta)

**Dokončit slepá místa rozhodovací logiky conductora — tedy ta, která ještě
nevolá žádný test — a přitom ani jednou nesáhnout na živou službu bez vědomí
uživatele.**

**Proč to patří nové session:** P24 zavřela **pět** endpointů, ale **handler
jich má devatenáct**. Zbylé (`/task`, `/game`, `/game/active`, `/queue`,
`/workers`, `/games`, `/failed`, `/status`, `/health`) **neměří žádný test** —
a dva z nich (`/task`, `/game/active`) **zapisují do D1 a mění chování služby**.
To je stejná třída jako §50.3: *vada, kterou nikdo nezměří, se pozná až tím, že
se něco stane*.

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — přeměřit P24 VLASTNÍM postupem

Zadání P24 psal autor, který si je i ověřoval; **P24 to udělala pro P23 —
a proto se to musí udělat i pro P24.** Každý bod měř **jinak, než jak vznikl**:

| # | Co ověřit | Jak (návrh; klidně si zvol vlastní) |
|---|---|---|
| **A1** | **Měřidlo P24 opravdu měří** | Spusť `python _analyza\p24-a-overeni.py`. Pak **vrať do kopie** některé jeho tvrzení vadu (např. v kopii `PLAN-ROZVOJ-ORCHESTRA.md` uber `\| **B4** \|`) a ověř, že **spadne** — a že `p24-b-mutace.py` to hlásí jako nález, ne jako OK |
| **A2** | **Nezávisle na měřidle P24**: `N > 0` u watchdogu je nastražená otázka | Ověř, že `roadmap.eskalovano` je **trvalá** značka (najdi SQL ve **zdroji** a dokaž, že se z ní neodstraňuje) — a že by tedy kontrola „ohlásil něco“ **shodila zdravou službu** |
| **A3** | **Test tiku opravdu VOLÁ endpointy** (ne jen existuje) | Do **kopie** conductora vlož do jednoho z pěti handlerů zarážku (např. změň odpověď `/claim` na `{task: null}`) a sleduj, **které kontroly se zapnou**. Když se jich zapne **nula**, test o té smlouvě netvrdí nic |
| **A4** | **Čísla v §54 sedí** | `grep`/skriptem najdi v `HANDOFF.md` §54 tvrzené čítače (99/0, 17/0, 100/0, 15 vrat/31/0, 48 bran) a **každý naměřený znovu spusť** |
| **A5** | **Krátká historie se nepřepsala** | `git diff 4925f64~1 HEAD` (až bude HEAD dál) u `KRONIKA-PROJEKTU.md` musí mít **0 smazaných řádků session**; `python _analyza\kronika-kontrola.py` → SEDÍ |
| **A6** | **Sondy nejsou brány** | Ověř, že `p24-sonda-*` **nejsou** v `BRANY` (`g3`) ani ve `spust()` (`validate-all.mjs`) a že jsou v `PRESKOCIT` — a že to není „uklizení dokladu pod koberec“ (tj. že měřidla, která měřit mají, v `g3` **jsou**) |

**Doklad:** vlastní skript v `_analyza/` (název `p25-*`), spuštěný a **uložený
i s výstupem**; **a musí umět selhat** (mutační test — vzor: `p24-b-mutace.py`).
Kdo přidá doklad do `_analyza/`, **přidá ho i do `_analyza/p20-d-doklady.py`**.

### 2.2 Úkol B — VĚCNÁ PRÁCE (vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **B1** | **Dopsat testy pro zbylé endpointy**: zejména **`POST /task`** (zakládá úlohu!) a **`POST /game` / `/game/active`** (mění registr her = mění, co orchestra dělá) | `HANDOFF.md` **§54.3** bod 10, `orders` ve `conductor/src/index.ts:1422+`, `:1644+` | Je to **pokračování Úkolu B3** a **největší zbylé slepé místo**; jde to **bez nasazení** |
| **B2** | **Rozhodnout návrh `.gitattributes`** (P24-B) | `HANDOFF.md` **§54.3** bod 2 | `git checkout` dnes **tiše rozbíjí mutační doklady**; návrh je hotový, chybí **rozhodnutí** (a je to změna, která se dotkne celého repa) |
| **B3** | **Ověřit B4 na ŽIVÉ službě** — `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**, pak hru vrátit | `HANDOFF.md` **§45**, `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 (B4) | Kód i brány hotové, **acceptance na živé službě neproběhlo**. ⚠ **Dočasně zastaví orchestra** — chce výslovné „ano" uživatele |
| **B4** | **Zapnout strop na granuli** (`GRAIN_MAX_RUNS = "5"`) — druhý krok B3b | `HANDOFF.md` **§46** | Až bude vidět, že watchdog stačí. ⚠ Je to **změna chování živé služby** = nasazení |
| **B5** | **Opravit slepé místo `over-skilly.py`** („0 mrtvých cest“, a přitom 24 odkazů na neexistující layout prošlo) | `HANDOFF.md` **§51.3** | Fáze C: „brány, které lžou“. ⚠ **Soubor má rozdělanou práci souběžné session** — nejdřív se domluv, nebo sáhni jinam |
| **O1** | **Rozhodnout `O3`, `O10`, `O5–O8`** | `PLAN-ROZVOJ-ORCHESTRA.md` **§6** | Jsou to **rozhodnutí**, ne kód — hodí se, když se nemá sahat na živou službu |

**Podmínky:** vybrat **JEDNU** a říct kterou · než začneš měnit kód, **změř
současný stav** (ne z dokumentu) · u conductoru **zavolej živou službu** a ukaž
vadu na její odpovědi · **`done` je tvrzení, ne důkaz** · ověř nasazení
**třemi kroky** (`HTTP 200` není důkaz).

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

Baseline po P24 (počet bran **48** — souběžná session zrušila duplicitní `a3-over`):

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány PO SOBĚ (ne současně — obě sahají na _inventar.json):
python _analyza\g3-brany.py                 -> 48 bran, 0 bez čítače,
                                               1 deklarovaný nenulový exit
                                               (zadání kontrola = 1), exit 0
node tools\validate-all.mjs                 -> VŠE V POŘÁDKU (exit 0)
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\p24-a-overeni.py            -> 99/0   (A1-A8)
python _analyza\p24-b-mutace.py             -> 17/0
node tools\test-tick-offline.mjs            -> 100/0
python _analyza\tick-mutace.py              -> 31/0 (15 vrat)
python _analyza\ov-g-neovereno.py           -> 35 návrhů + 99 nálezů, 0 ve stavu NEOVĚŘENO
python tools\over-skilly.py                 -> 13 skillu, 0 chyb
python tools\over-dokumentaci.py            -> 67 kontrol, 0 chyb
python _analyza\p20-d-doklady.py            -> spustí i doklady P24
python _analyza\zadani-kontrola.py          -> kontroluje KOTVU tohohle zadani
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem.
**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`.**
**⚠ POČET VRAT NEPIŠ DO NÁZVU BRÁNY** — zestaral dvakrát (3 → 6 → 8); čítač
vykazuje test sám a registr `g3`.
**⚠ KDO MĚNÍ `_analyza/g3-brany.py`, MĚNÍ I `tools/validate-all.mjs`.**

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje).
2. **Zapiš výsledky** do `HANDOFF.md` (**nový oddíl**, jen **přidávej**) a do
   `KRONIKA-PROJEKTU.md`: **řádek session** do §1 (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**) a **nálezy** do §2.
   ⚠ **OMYLY SE OD 6. 10. 2026 NEVEDOU** — uživatel rozhodl **„omyly nepiš"**;
   do sloupce omylů patří **`—`** a **souhrn §3 se nepřepočítává**.
   Řádky piš **skriptem** (vzor: `_analyza/p24-radek-kroniky.py`): řádky mají
   **přes 2000 znaků** a kotva z načteného řádku ho **zkrátí** (omyly **194**, **206**).
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — měřidlem `python _analyza\ov-g-neovereno.py`
   (**ne** hledáním slova v textu: v P24 to dalo 17 falešných poplachů, z toho
   15 legitimních zmínek v historii).
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE SOUČASNĚ**),
   inventář **jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Práce P24 je přeměřená, ne odsouhlasená** | A1: měřidlo projde **a** po vrácení vady spadne |
| 2 | **Nastražená otázka je doložená** | A2: SQL dokazuje trvalost značky `eskalovano` |
| 3 | **Test tiku endpointy opravdu VOLÁ** | A3: zarážka v handleru zapne aspoň jednu kontrolu |
| 4 | **Čísla v §54 sedí** | A4: každý tvrzený čítač naměřen znovu |
| 5 | **Nic se nepřepsalo** | A5: 0 smazaných řádků session + `kronika-kontrola` SEDÍ |
| 6 | **Nic se nerozbilo** | `g3` → 48 bran, jen **deklarované** exity; `validate-all` → **VŠE V POŘÁDKU** |
| 7 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEDĚLEJ Z KONTROLY CÍL.** Ověřit máš **práci P24**, ne přidávat další
  měřidla. Nová brána je na místě **jen** tam, kde je doložená vada měření.
- **⚠ NESAHEJ NA ROZDĚLANOU PRÁCI SOUBĚŽNÉ SESSION** — necommituj ji, neopravuj
  ji, nemaž ji. Když ti překáží, **řekni to**. (Její je i obsah
  `_analyza/_registr-bran.json` — je **generovaný**.)
- **Nesahej na hru** — uživatel ji **záměrně pozastavil**; `uo-shadows` musí
  zůstat na `44dd454` a čistá.
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§53 = nasazení P23, §54 = ověření P24).
- **Nemaž `_analyza/p24-*`, `n03*-mutace.py`, `b*-mutace.py`, `tick-mutace.py`,
  `n03d-radek-kroniky.py` ani `ov-*`** — jsou to **doklady**; a **nemaž
  `_archiv`** (je to cesta zpět).
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ** (obě sahají na inventář).
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM) a **nepoužívej
  `python -c`** s regexy ani `$(...)` — **piš skript do souboru**.
- **⚠ NEPŘERUŠUJ MUTAČNÍ BĚH.** Když ho přerušíš, **ověř strom** — v P24
  v něm zůstaly **čtyři mutanty**.
- **⚠ POZOR NA `git checkout` NAD `conductor/src/index.ts`** — přepíše ho na
  CRLF a rozbije vícřádkové kotvy mutací (a `git status` bude čistý).
- **⚠ NEPIŠ EVIDENCI PŘES `>`** — PowerShell tím vyrobí **UTF-16LE**.
- **Nepřesouvej nic zpátky na `C:`** a nemaž `E:\Workspaces\_acl-oprava-20261006\`
  ani `E:\Workspaces\_acl-oprava-20261007\` (rollbacky oprav ACL).
- **Nepřebírej tvrzení z §54** — psal je autor, který si je i ověřoval.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (7. 10. 2026, 10:0x +02:00 = 08:0x UTC)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD            -> 4925f64
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main      -> c664dde
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 1
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD             -> 44dd454

# ziva sluzba (7. 10. 2026, 09:0x UTC)
deploy.yml beh #33 na head_sha 598e207            -> completed / success
GET  /health  -> ok=true ready=2 running=0 games=1
                 targets[0]: main_ci: success (ci.yml #117, head 44dd454)
                             forge.ok=false, selhani_v_rade=20
POST /tick    -> watchdog: 0 ohlášeno (prah 3)     <- 0 je SPRÁVNĚ (trvalá značka)

# brany po P24
python _analyza\g3-brany.py                  -> 48 bran, 0 bez citace, exit 0
node tools\validate-all.mjs                  -> VSE V PORADKU, exit 0
python _analyza\handoff-kontrola-uplnost.py  -> 83/83, CHYBI 0
python _analyza\p24-a-overeni.py             -> 99 kontrol, 0 chyb
python _analyza\p24-b-mutace.py              -> 17 kontrol, 0 chyb
node tools\test-tick-offline.mjs             -> 100 kontrol, 0 chyb
python _analyza\tick-mutace.py               -> 31 kontrol, 0 chyb (15 vrat)
python _analyza\ov-g-neovereno.py            -> 0 ve stavu NEOVERENO (35 navrhu, 99 nalezu)
python tools\over-skilly.py                  -> 13 skillu, 0 chyb

# ⚠ TRIK PRO PUSH (PAT se NIKDY nevypisuje):
#   $pat = (Get-Content .secrets\github_pat.txt -Raw).Trim()
#   $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$pat"))
#   & .\tools\git.cmd -c "http.extraHeader=AUTHORIZATION: basic $b64" push origin main

# ⚠ PRED COMMITEM: kontrola STAGOVANEHO blobu na znacky mutantu
#   git show :conductor/src/index.ts   (hledej: if (false) break;, merged = true;, ...)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ MERIDLO P24: síť z Pythonu JDE, ale Cloudflare blokuje `Python-urllib`
#   (403 error code: 1010) — posílej User-Agent prohlížeče.
```

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P25. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — nesahej na ni)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P24 NEZÁVISLE PŘEMĚŘILA nasazení P23 (Úkol A: A1–A8 vlastním
měřidlem _analyza/p24-a-overeni.py = 99/0, s mutačním důkazem p24-b-mutace.py =
17/0) a dokončila Úkol B3 — offline test tiku teď volá i /poll, /claim,
/heartbeat, /tasks/cleanup a /roadmap/reset (100 kontrol, bylo 40; mutační
důkaz tick-mutace.py = 15 vrat / 31 kontrol). Záznam je v HANDOFF.md §54
a v kronice řádek 39 + §2.17. Od 6. 10. 2026 se OMYLY NEVEDOU — do sloupce
omylů patří "—" a souhrn §3 kroniky se nepřepočítává.

TVŮJ ÚKOL JE NEPŘÍJEMNÝ, ALE DŮLEŽITÝ: záznamy P24 psal autor, který si je sám
ověřoval — a AGENTS.md říká "autor není nezávislý reviewer". Přeměř to VLASTNÍM
měřidlem (§2.1 A1–A6): měří p24-a-overeni.py opravdu to, co tvrdí? je pravda,
že N>0 u watchdogu je NASTRAŽENÁ otázka (trvalá značka eskalovano)? VOLÁ test
tiku ty endpointy doopravdy? Pak si vyber JEDNU věcnou práci (§2.2) — nejvýš
je na řadě dopsat testy pro POST /task a /game/active.

POZOR: ve workspace pracuje SOUBĚŽNÁ session (generalizace nástrojů) — její
práci necommituj, neopravuj a nemaž. Před commitem kontroluj INDEX
(git show :soubor), ne pracovní strom. Nepoužívej git show <sha>^ (git.cmd žere ^)
a needituj .py přes Set-Content (přidá BOM). NEPŘERUŠUJ mutační běh — v P24 po
přerušení zůstaly čtyři mutanty v živém conductor/src/index.ts. A POZOR:
git checkout nad conductor/src/index.ts ho přepíše na CRLF a tiše rozbije
vícřádkové kotvy mutací (git status přitom bude čistý).

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS),
a ověř origin/main..HEAD ŽIVĚ, ne podle zadání.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky do HANDOFF.md
(nový oddíl) a do KRONIKY (řádek session + nálezy; omyly = "—"), ověř, že
nezůstalo NEOVĚŘENO (měřidlem ov-g-neovereno.py, ne hledáním slova), přegeneruj
inventář JAKO POSLEDNÍ KROK, spusť g3 a pak validate-all (ne současně) a do chatu
vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

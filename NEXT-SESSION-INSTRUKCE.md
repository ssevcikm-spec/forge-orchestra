# ZADÁNÍ PRO DALŠÍ SESSION — DOKONČIT SLEPÁ MÍSTA CONDUCTORA (7 endpointů bez testu)

**Co tenhle dokument JE:** **zadání pro session P27**. Nahrazuje zadání z P26
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, nejnovější oddíl **§56**)
ani kronika (ta je v `KRONIKA-PROJEKTU.md`, nejnovější **řádek 41**,
nálezy **§2.19**).

**Stav obou repů při psaní:** `forge-orchestra` = **`ef58327`** · `uo-shadows` = **`125b062`**.
`origin/main` orchestry je **`92aa80a`** (**`ef58327` je NEPUSHNUTÝ** — práce P25,
commitla ji P25 a nepushla), `origin/main` hry je **`932dc6f`** (**3 commity hry
jsou NEPUSHNUTÉ**).
Práce P26 je **v pracovním stromě** (commit dělá session na konci).
**Zkontrolováno při:** **7. 10. 2026, 16:2x +02:00 = 14:2x UTC**

> **⚠ DO HRY PÍŠE SOUBĚŽNÁ SESSION (naměřeno P26).** `uo-shadows` se během
> session P26 posunul z `932dc6f` na **`125b062`** — přibyly **tři commity**
> (`6796188` 15:50, `43a2004` 15:58, `125b062` 16:02 +02:00, **nepushnuté**)
> a netrackovaný **`_acl-recovery/`**. **Není to práce P26** a **nesahalo se
> na to.** Důsledek pro měření: `p24-a-overeni.py` hlásí **99/3** (tři červené
> `A8`) místo `99/1`. **A druhý důsledek:** inventář počítá otisk **I DRUHÉHO
> REPA** (`KOREN_REPA`), takže **zápis do hry zneplatní inventář uprostřed
> běhu** — `g3` a `validate-all` pak hlásí pojmenovaný STAV „zastaralý
> inventář“, ne vadu. Náprava je **přegenerovat a spustit znovu**.

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `ef58327` · `uo-shadows` = `125b062`

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> (přes `tools\git.cmd` — schannel padá) v obou repech a **ověř
> `origin/main..HEAD` ŽIVĚ** (`git ls-remote` / `rev-list`), ne podle textu.
> **Naměřeno v P26:** zadání P25 tvrdilo „práce P25 je v pracovním stromě
> (necommitnutá)" — a přitom P25 už měla **commit `ef58327`**. Hlavička zadání
> je **snapshot, ne stav**; kdo ji čte, měří.
>
> **⚠ DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu (skill `dsh-prostredi` §5c). Používej **`~1`** nebo `git.exe`.
>
> **⚠ TŘETÍ:** **`Set-Content -Encoding utf8` přidá do `.py` BOM** (omyl **189**)
> → soubor je pro brány nekompilovatelný. Piš `edit`/`write` toolem a po zápisu
> zkontroluj **první tři bajty** (`.py` **NESMÍ** BOM, `.ps1` **MUSÍ**).
>
> **⚠ ČTVRTÁ:** **`git checkout` nad `conductor/src/index.ts` ho přepíše na CRLF**
> a tiše rozbije vícřádkové kotvy mutací (`git status` bude přitom čistý).
> Stav se opravuje obnovením **bajtů z blobu** (LF). Podrobně `HANDOFF.md` §54.3.
>
> **⚠ PÁTÁ:** **PŘERUŠENÝ MUTAČNÍ BĚH JE STAV, NE NEHODA.** Po pádu zůstanou
> mutanti v živém `conductor/src/index.ts`. Před mutováním i po něm ověř
> `git diff`; `_analyza/p26-a-overeni.py` to dělá za tebe (hash disku vs. HEAD
> před i po **každé** ze tří zarážek).
>
> **⚠ ŠESTÁ (naměřeno P26 znovu, 7. 10. 2026):** **ZÁPIS PODPROCESEM MŮŽE BÝT
> ODEMČENÝ.** V `workspace-write` nešel zapsat soubor **podprocesem** do
> žádného podadresáře workspace — a tentokrát to **nespadlo**, ale **ZAMRZLO**
> (čekalo na schválení). `git fetch` padal na `.git/FETCH_HEAD: Permission
> denied`. Nástroj `write` (harness) přitom do podadresáře zapsal.
> **Není to vada skriptu** — pomohlo **přepnutí session na plný přístup**.
> Past: skill `dsh-prostredi` §4e, nález `P26-J`.

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

### 0.1 P26 — Úkol A: přeměření práce P25 VLASTNÍM měřidlem — HOTOVO

| # | Co se ověřovalo | Výsledek |
|---|---|---|
| **A1** | měří měřidlo P25 opravdu to, co tvrdí? | **POTVRZENO**: **čtyři kontramutace v KOPIÍCH** přes přepínače `--kronika/--g3/--zdroj/--handoff` — každá shodí měřidlo **z jiného důvodu** (řádek 39, SONDa v BRANY, MAŽE se značka, chybí §54) |
| **A2** | **VOLÁ test tiku `/task`, `/game`, `/game/active`?** | **POTVRZENO — a POPRVÉ**: zarážka **V HANDLERU** zapnula **9 `T:`**, **6 `U:`** a **5 `V:`** kontrol; kontrolní `A: /tick odpoví 200` zůstala pokaždé **zelená**. ⚠ **P25 to nezměřila** — její zarážka byla jen v ROUTERU a v 42 červených **nejsou žádné `T`/`U`/`V`/`W`** |
| **A3** | **vázané hodnoty** opravdu jdou do D1 | **POTVRZENO**: v KOPII testu vypnutý záznam `bind()` → **12 červených** (T: 5, V: 2), konkrétně `T: \`title\` jde do INSERTu` a `V: do DB jde \`active = 0\` (ne 1)` |
| **A4** | čísla v §55 sedí | **POTVRZENO**: každý tvrzený čítač znovu naměřen a **souhlasí** (viz §5). **Jedno číslo NESEDÍ — ale je ze ZADÁNÍ, ne z §55** (viz nález 1 níž) |
| **A5** | **nález P25-K je pravdivý** | **POTVRZENO a OPRAVENO**: verze z `HEAD` čte **1** řádek Hxx, živá po opravě **99** (1 + 98); měřidlo teď **vypisuje, které soubory otevřelo**, a hlásí i rozsah mimo ně |
| **A6** | nic se nerozbilo ani neztratilo | `g3` → **49 bran, 1 deklarovaný exit, exit 0**; `validate-all` → **VŠE V POŘÁDKU**; `handoff-kontrola-uplnost` → **83/83**; `kronika-kontrola` → **SEDÍ**; `ov-g-neovereno` → **0× NEOVĚŘENO nad 99 řádky** |

**Doklad:** `_analyza/p26-a-overeni.py` (dávka = A1, A4, A5, A6; `--plne` =
i A2, A3, `g3`, `validate-all`) + mutační důkaz `_analyza/p26-b-mutace.py`
(tři mutace **v kopiích**, každá s **diferenciálem**).

### 0.2 P26 — Úkol B1: oprava brány, která tiše zúžila rozsah (P25-K) — HOTOVO

`_analyza/ov-g-neovereno.py` **četl jen `HANDOFF.md`**, kde po optimalizaci KB
(`92aa80a`) zbyl **1** řádek Hxx; zbylých **98** se přesunulo do
`_archiv/HANDOFF-HISTORIE.md`. Měřidlo tedy hlásilo zelenou **nad 1 % rozsahu**
a **nikdo to nepoznal** (čítač vypsalo, ale rozsah ne).

**Opraveno:** zdroje se **odvozují** (ne zapečený seznam), **vypisují se**
po souborech, počítá se **rozsah mimo živé zdroje** (zmrazené kopie a zálohy —
139 řádků v 7 souborech, **záměrně se nečtou**, jinak by se týž nález počítal
víckrát), **prázdný rozsah je `NEMĚŘENO` (exit 1)**, a je tam přepínač
`--handoff` **kvůli mutačnímu důkazu**. Navíc opraven **lživý popisek**:
skript tvrdil „hledám NEOVĚŘENO ve sloupci Stav" — **žádný takový sloupec
neexistuje** (tabulky mají 2–3 buňky), hledalo se **kdekoli na řádku**.

### 0.3 ⚠ CO JE V STROMĚ NECOMMITNUTÉ (stav při psaní zadání)

| Soubor | Co to je |
|---|---|
| `_analyza/p26-a-overeni.py`, `_analyza/p26-b-mutace.py` | měřidlo P26 a jeho mutační důkaz (**nové**) |
| `_analyza/p26-sonda-zapis.py`, `_analyza/p26-sonda-rozsah.py` | jednorázové sondy (sandbox §4e; rozsah tabulek Hxx) — **jsou v `PRESKOCIT` dávky `p20-d`** |
| `_analyza/ov-g-neovereno.py` | **OPRAVA P25-K** (rozsah 1 → 99) |
| `_analyza/p20-d-doklady.py` | `PRESKOCIT` + dvě sondy P26 |
| `HANDOFF.md`, `KRONIKA-PROJEKTU.md`, `NEXT-SESSION-INSTRUKCE.md` | §56, řádek 41 + §2.19, tohle zadání |
| `_analyza/_registr-bran.json` | **generovaný** `g3` (49 bran) — needituj ho rukou |

---

## 1. Cíl (jedna věta)

**Dopsat testy pro ZBÝVAJÍCÍCH SEDM endpointů conductora** (`/health`, `/queue`,
`/roadmap`, `/failed`, `/status`, `/workers`, `/games`) — dnes je **nevolá
žádný test**, a to jsou endpointy, které orchestra používá pro diagnostiku
i pro člověka.

**Proč to patří nové session:** P24 zavřela pět endpointů (`/poll`, `/claim`,
`/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`), P25 tři zapisující
(`/task`, `/game`, `/game/active`) — a **P26 doložila zarážkou v handleru, že je
test opravdu volá**. Zbylých sedm nevolá **nikdo**: naměřeno `grep`em v P26
(`post(mod, env, '/health'|'/queue'|…` → **0 výskytů**). Je to táž třída jako
§50.3: *vada, kterou nikdo nezměří, se pozná až tím, že se něco stane.*

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — přeměřit P26 VLASTNÍM postupem

P26 si **sama psala záznamy i měřidlo** — a `AGENTS.md` je v tom jednoznačné:
*„autor není nezávislý reviewer"*. Každý bod měř **jinak, než vznikl**:

| # | Co ověřit | Jak (návrh; klidně vlastní) |
|---|---|---|
| **A1** | měřidlo P26 opravdu měří | Spusť `python _analyza\p26-a-overeni.py --plne` a `python _analyza\p26-b-mutace.py`. Pak **v kopii** uber tvrzení, které měřidlo hlídá (např. v kopii `HANDOFF.md` přejmenuj `\| \*\*41\*\* \|`), a ověř, že **spadne** (měřidlo má `--handoff`, `--ovg`, `--g3`) |
| **A2** | **VOLÁ test tiku i sedm zbývajících endpointů?** | Po Úkolu B to **změř zarážkou v handleru** (vzor: `p26-a-overeni.py` A2 — tři zarážky, hash před/po). Když zarážka nezapne **ani jednu** kontrolu, test o té smlouvě **netvrdí nic** |
| **A3** | vázané hodnoty u nových endpointů | `/queue`, `/workers`, `/games`, `/status`, `/failed` **čtou** — ověř, že test tvrdí **TVAR i OBSAH** odpovědi, ne jen `status === 200` |
| **A4** | čísla v §56 sedí | Každý tvrzený čítač **znovu spusť** a porovnej; číslo, které nesedí, je **nález** (a patří zapsat) |
| **A5** | oprava P25-K je správná a **měří** | `python _analyza\ov-g-neovereno.py` → rozsah **99**; a **fixtura**: soubor s řádkem `\| **H900** \| … NEOVĚŘENO \|` → **exit 1**; **prázdná** fixtura → `NEMĚŘENO`, `exit 1` |
| **A6** | nic se nerozbilo ani neztratilo | `g3` → **49 bran, jen deklarované exity**; `validate-all` → **VŠE V POŘÁDKU**; `handoff-kontrola-uplnost` → **83/83**; `kronika-kontrola` → **SEDÍ**; `ov-g-neovereno` → 0× NEOVĚŘENO **včetně ROZSAHU** (musí hlásit **99** řádků Hxx) |
| **A7** | **inventář a brány po sobě** | Pořadí **inventář → `g3` → `validate-all`** a **mezi tím nic nezapisuj** (ani doklad!): naměřeno P26, že **jeden nový `.txt`** v `_analyza/` shodí `n1-over-inventar` (`exit 2`) a `C2: mutace N1` se objeví v „brány bez čítače“. Doklady proto patří na jména podle vylučovacího vzoru (`_analyza/*-vystup.txt`) |

**Doklad:** vlastní skript v `_analyza/` (název `p27-*`), spuštěný a **uložený
i s výstupem**; a **musí umět selhat** (mutační test — vzor: `p26-b-mutace.py`).
Kdo přidá doklad do `_analyza/`, **přidá ho i do `_analyza/p20-d-doklady.py`**
(vzor `VZOR = re.compile(r"^(ov-|p1[6-9]-|p2[0-9]-)")` ho bere sám — ověř to).

### 2.2 Úkol B — VĚCNÁ PRÁCE (vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **B1** | **Dopsat testy pro sedm endpointů, které nevolá NIKDO**: `/health`, `/queue`, `/roadmap`, `/failed`, `/status`, `/workers`, `/games` | `HANDOFF.md` §56.2/9, `conductor/src/index.ts` (řádky 1246, 1296, 1303, 1315, 1351, 1361, 1369) | Pokračování P24+B1 P25; jde to **bez nasazení** a je to **nejvýš na řadě** (P26 to naměřila) |
| **B2** | **Rozhodnout návrh `.gitattributes`** (P24-B) | `HANDOFF.md` §54.3 bod 2 | `git checkout` dnes **tiše rozbíjí mutační doklady**; návrh je hotový, chybí **rozhodnutí** |
| **B3** | **Ověřit B4 na ŽIVÉ službě** — `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**, pak hru vrátit | `HANDOFF.md` §45, `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 (B4) | Kód i brány hotové, **acceptance na živé službě neproběhlo**. ⚠ **Dočasně zastaví orchestra** → chce výslovné „ano" uživatele |
| **B4** | **Zapnout strop na granuli** (`GRAIN_MAX_RUNS = "5"`) | `HANDOFF.md` §46 | Až bude vidět, že watchdog stačí. ⚠ Změna chování živé služby = nasazení |
| **B5** | **Opravit slepé místo `over-skilly.py`** (fáze C) | `HANDOFF.md` §51.3 | ⚠ Pozor: soubor má **rozdělanou práci souběžné session** (`test-over-skilly-delegovane.py`) — nejdřív se domluv, nebo sáhni jinam |
| **O1** | **Rozhodnout `O3`, `O10`, `O5–O8`** | `PLAN-ROZVOJ-ORCHESTRA.md` §6 | Jsou to **rozhodnutí**, ne kód |

**Podmínky:** vybrat **JEDNU** a říct kterou · než začneš měnit kód, **změř
současný stav** (ne z dokumentu) · u conductoru **zavolej živou službu** a ukaž
vadu na její odpovědi · **`done` je tvrzení, ne důkaz** · ověř nasazení **třemi
kroky** (`HTTP 200` není důkaz).

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány PO SOBĚ (ne současně — obě sahají na _inventar.json):
python _analyza\g3-brany.py                 -> 49 bran, 0 bez čítače,
                                               1 deklarovaný nenulový exit
                                               (zadání kontrola), exit 0
node tools\validate-all.mjs                 -> VŠE V POŘÁDKU (exit 0)
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\p26-a-overeni.py            -> dávkový režim (A1, A4, A5, A6)
python _analyza\p26-a-overeni.py --plne     -> A1-A6 včetně zarážek, g3, validate-all
python _analyza\p26-b-mutace.py             -> tři mutace v kopiích + diferenciál
python _analyza\p25-a-overeni.py            -> dávkový režim (A2,A5,A6)
python _analyza\p25-a-overeni.py --plne     -> A1-A6: 53/0
python _analyza\p25-b-mutace.py             -> 27/0
python _analyza\p24-a-overeni.py            -> 99/3 (A8: hra na 125b062, necisty
                                               strom, 3 nepushnute commity —
                                               soubezna session; 99/2 po pushi)
python _analyza\p24-b-mutace.py             -> 17/0
node tools\test-tick-offline.mjs            -> 146/0
python _analyza\tick-mutace.py              -> 20 vrat, 41/0
python _analyza\ov-g-neovereno.py           -> 0 NEOVERENO a ROZSAH 99 radku Hxx
                                               (1 v HANDOFF.md + 98 v _archivu)
python tools\over-skilly.py                 -> 13 skillu, 0 chyb
python tools\over-dokumentaci.py            -> 64 kontrol, 0 chyb
python _analyza\zadani-kontrola.py          -> kontroluje KOTVU tohohle zadani
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem. **A pozor: „zastaralý
inventář“ NENÍ deklarovatelný stav** — náprava je přegenerovat (nález P25-H).
**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`** (a sondu
do `PRESKOCIT`).
**⚠ POČET VRAT NEPIŠ DO NÁZVU BRÁNY** — doklad ho od P25 **vypisuje sám**
(`vrat: N`) a registr `g3` ho nese.
**⚠ KDO MĚNÍ `_analyza/g3-brany.py`, MĚNÍ I `tools/validate-all.mjs`.**
**⚠ AUTORITA SEZNAMU ŽIVÝCH BRAN JE `BRANY` v `_analyza\g3-brany.py`** —
**ne** ruční výčet v `HANDOFF.md` §6 (ten je **záznam z 2. 10. 2026**
s předpřesunovými cestami `orchestra\tools\…` a čísly 63/12).
**⚠ DVA GATE SE VYLUČUJÍ (naměřeno P26):** `zadani-kontrola.py` chce
**kotva zadání = živý `HEAD`**, ale `p25-b-mutace.py` chce **ČISTÝ strom**
(necommitnuté záznamy vykáže jako mutanty). Pořadí, které projde: **commit →
doklad → záznamy → inventář → `g3` → `validate-all` → hlavička zadání
(necommitnutá)**. `p25-b` červené před commitem **není vada kódu**.

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje).
2. **Zapiš výsledky** do `HANDOFF.md` (**nový oddíl**, jen **přidávej**) a do
   `KRONIKA-PROJEKTU.md`: **řádek session** do §1 (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**) a **nálezy** do §2.
   ⚠ **OMYLY SE OD 6. 10. 2026 NEVEDOU** — do sloupce omylů patří **`—`**
   a **souhrn §3 se nepřepočítává**.
   Řádky piš **skriptem** (vzor: `_analyza/p25-radek-kroniky.py` nebo
   `_analyza/p26-*`): řádky mají **přes 2000 znaků** a kotva z načteného řádku
   ho **zkrátí** (omyly **194**, **206**).
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — měřidlem `python _analyza\ov-g-neovereno.py`
   (**ne** hledáním slova) — **a zkontroluj jeho ROZSAH** (musí hlásit
   **99 řádků Hxx**; kdyby hlásil 1, je rozbitá oprava P25-K).
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE
   SOUČASNĚ**), inventář **jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Práce P26 je přeměřená, ne odsouhlasená** | A1: měřidlo projde **a** po vrácení vady spadne (diferenciál) |
| 2 | **Test tiku volá i nové endpointy** | A2: zarážka v handleru zapne aspoň jednu kontrolu u **každého** nového endpointu |
| 3 | **Čísla v §56 sedí** | A4: každý tvrzený čítač naměřen znovu; co nesedí, je zapsaný nález |
| 4 | **Rozsah měřidla `ov-g-neovereno` je 99, ne 1** | A5: 99 řádků Hxx + fixtury (NEOVĚŘENO → `exit 1`, prázdno → `NEMĚŘENO`) |
| 5 | **Nic se nepřepsalo** | 0 smazaných řádků session + `kronika-kontrola` SEDÍ + `handoff-kontrola-uplnost` 83/83 |
| 6 | **Nic se nerozbilo** | `g3` → 49 bran, jen **deklarované** exity; `validate-all` → **VŠE V POŘÁDKU** |
| 7 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEDĚLEJ Z KONTROLY CÍL.** Ověřit máš **práci P26**, ne přidávat další
  měřidla. Nová brána je na místě **jen** tam, kde je doložená vada měření.
- **⚠ NESAHEJ NA ROZDĚLANOU PRÁCI SOUBĚŽNÉ SESSION** — necommituj ji, neopravuj
  ji, nemaž ji. Když ti překáží, **řekni to**. (Její je i obsah
  `_analyza/_registr-bran.json` — je **generovaný**.)
- **Nesahej na hru** — uživatel ji **záměrně pozastavil**, ale **souběžná
  session do ní píše** (P26 naměřila tři commity 15:50–16:02). Ověř ji, ale
  **nepiš do ní**, **necommituj její práci** a **nemaž `_acl-recovery/`**
  (netrackovaný artefakt té session — je to její věc, ne smetí).
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§53 = nasazení P23, §54 = ověření P24, §55 = P25,
  §56 = P26). **`HANDOFF.md` §6 je ZÁZNAM z 2. 10. 2026, ne seznam živých bran.**
- **Nemaž `_analyza/p2[456]-*`, `n03*-mutace.py`, `b*-mutace.py`,
  `tick-mutace.py` ani `ov-*`** — jsou to **doklady**; a **nemaž `_archiv`**
  (je to cesta zpět, i `_archiv/HANDOFF-HISTORIE.md` s **98** řádky Hxx —
  **na tom rozsahu stojí oprava P25-K**).
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ** (obě sahají na inventář).
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM) a **nepoužívej `python -c`**
  s regexy ani `$(...)` — **piš skript do souboru**.
- **⚠ NEPŘERUŠUJ MUTAČNÍ BĚH** — po přerušení zůstanou mutanti v živém zdroji.
- **⚠ POZOR NA `git checkout` NAD `conductor/src/index.ts`** — CRLF a rozbité
  vícřádkové kotvy (a `git status` bude čistý).
- **⚠ NEPIŠ EVIDENCI PŘES `>`** — PowerShell tím vyrobí **UTF-16LE**.
- **Nepřesouvej nic zpátky na `C:`** a nemaž `E:\Workspaces\_acl-oprava-*`
  (rollbacky oprav ACL, včetně `_acl-oprava-20261007b` z P25).
- **Nepřebírej tvrzení z §56** — psal je autor, který si je i ověřoval.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (7. 10. 2026, 16:2x +02:00 = 14:2x UTC)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD            -> ef58327
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main      -> 92aa80a
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 1 (P25; +1 P26)
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD             -> 125b062
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD -> 3 (CIZI session)

# ziva sluzba (7. 10. 2026, ~13:0x UTC)
/health  -> ok=true ready=2 running=0 games=1
POST /tick -> watchdog: 0 ohlášeno (prah 3)     <- 0 je SPRÁVNĚ (trvalá značka)

# brany po P26 (po přegenerování inventáře)
python _analyza\g3-brany.py                  -> 49 bran, 1 deklarovaný exit, exit 0
node tools\validate-all.mjs                  -> VSE V PORADKU, exit 0
python _analyza\handoff-kontrola-uplnost.py  -> 83/83, CHYBI 0
python _analyza\kronika-kontrola.py          -> KRONIKA SEDI
python _analyza\p26-a-overeni.py --plne      -> A1-A6 vse (viz §56.1)
python _analyza\p26-b-mutace.py              -> 3 mutace v kopiich + diferencial
python _analyza\p25-a-overeni.py             -> davka 17/0
python _analyza\p25-a-overeni.py --plne      -> 53/0
python _analyza\p25-b-mutace.py              -> 27/0
python _analyza\p24-a-overeni.py             -> 99/3 (A8: hra 125b062, necisty strom,
                                                3 nepushnute = cizi session)
python _analyza\p24-b-mutace.py              -> 17/0
node tools\test-tick-offline.mjs             -> 146/0
python _analyza\tick-mutace.py               -> 20 vrat, 41/0
python _analyza\ov-g-neovereno.py            -> 0 NEOVERENO, ROZSAH 99 radku Hxx
python tools\over-skilly.py                  -> 13 skillu, 0 chyb
python tools\over-dokumentaci.py             -> 64 kontrol, 0 chyb
                                               (⚠ 67 v zadání P26 bylo ZASTARALE)

# NALEZ P26: zarážka V HANDLERU (ne v routeru!) pro /task, /game, /game/active:
#   /task          -> 9 cervenych `T:`, kontrolni `A: /tick odpoví 200` ZELENA
#   /game          -> 6 cervenych `U:`, kontrolni ZELENA
#   /game/active   -> 5 cervenych `V:`, kontrolni ZELENA
#   (P25 mela zarazku jen v ROUTERU a v 42 cervenych nejsou zadne T/U/V/W)
# SELEP bind() v KOPII testu -> 12 cervenych (T: 5, V: 2)

# ⚠ TRIK PRO PUSH (PAT se NIKDY nevypisuje):
#   $pat = (Get-Content .secrets\github_pat.txt -Raw).Trim()
#   $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$pat"))
#   & .\tools\git.cmd -c "http.extraHeader=AUTHORIZATION: basic $b64" push origin main

# ⚠ PRED COMMITEM: kontrola STAGOVANEHO blobu na znacky mutantu
#   git show :conductor/src/index.ts   (hledej: if (false) break;, zarazka-p26, ...)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ MERIDLA P24/P25/P26: síť z Pythonu JDE, ale Cloudflare blokuje `Python-urllib`
#   (403 error code: 1010) — posílej User-Agent prohlížeče.
# ⚠ Měřidla P25 i P26 mají DÁVKOVÝ režim a PLNÝ (--plne): plný mutuje živý zdroj
#   (P26 tři zarážky) a pouští g3, takže do dávky `p20-d` patří jen dávkový režim.
```

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P27. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — jen ověřuj, nepiš do ní)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P26 PŘEMĚŘILA práci P25 vlastním měřidlem (_analyza/p26-a-overeni.py
+ mutační důkaz p26-b-mutace.py, tři mutace v KOPIÍCH s diferenciálem) a dokončila
Úkol B1 — opravila bránu ov-g-neovereno.py, která tiše zúžila rozsah z 99 řádků
Hxx na 1 (nález P25-K). Záznam je v HANDOFF.md §56 a v kronice řádek 41 + §2.19.
Od 6. 10. 2026 se OMYLY NEVEDOU — do sloupce omylů patří "—" a souhrn §3 kroniky
se nepřepočítává.

DŮLEŽITÉ, CO P26 NAMĚŘILA: P25 sice tvrdila, že test tiku volá POST /task, /game
a /game/active — ale její zarážka byla jen v ROUTERU a v 42 červených nejsou
žádné kontroly T/U/V/W. P26 to změřila ZARÁŽKOU V HANDLERU: /task zapne 9 kontrol
`T:`, /game 6 `U:`, /game/active 5 `V:` — a kontrolní `A: /tick odpoví 200`
zůstane pokaždé zelená. Čísla §55 jinak SEDÍ (53/0, 27/0, 146/0, 41/0, 49 bran).
Jedno číslo NESEDÍ, ale je ze zadání: over-dokumentaci.py dává 64/0, ne 67/0.

POZOR — DO HRY PÍŠE SOUBĚŽNÁ SESSION: uo-shadows se posunul z 932dc6f na 125b062
(tři cizí commity 15:50-16:02, nepushnuté) + netrackovaný _acl-recovery/. Proto
p24-a-overeni.py hlásí 99/3 místo 99/1. A inventář počítá otisk I DRUHÉHO REPA,
takže zápis do hry ho zneplatní uprostřed běhu — pořadí inventář -> g3 ->
validate-all dělej bez zápisu mezi kroky a doklady pojmenuj *-vystup.txt.

TVŮJ ÚKOL: přeměř P26 VLASTNÍM měřidlem (§2.1 A1–A7) a pak si vyber JEDNU věcnou
práci (§2.2) — nejvýš je na řadě B1: dopsat testy pro SEDM endpointů, které dnes
nevolá žádný test (/health, /queue, /roadmap, /failed, /status, /workers, /games).

POZOR: ve workspace může pracovat SOUBĚŽNÁ session — její práci necommituj,
neopravuj a nemaž. Před commitem kontroluj INDEX (git show :soubor), ne pracovní
strom. Nepoužívej git show <sha>^ (git.cmd žere ^) a needituj .py přes
Set-Content (přidá BOM). NEPŘERUŠUJ mutační běh. A POZOR: git checkout nad
conductor/src/index.ts ho přepíše na CRLF a tiše rozbije vícřádkové kotvy
mutací (git status přitom bude čistý).

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS),
a ověř origin/main..HEAD ŽIVĚ, ne podle zadání. A všimni si: když podproces
nemůže zapsat soubor v podadresáři workspace, je to STAV sandboxu, ne vada
skriptu — a v P26 to místo chyby ZAMRZLO; pomohlo přepnutí na plný přístup
(skill dsh-prostredi §4e).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky do HANDOFF.md
(nový oddíl) a do KRONIKY (řádek session + nálezy; omyly = "—"), ověř, že
nezůstalo NEOVĚŘENO (měřidlem ov-g-neovereno.py VČETNĚ ROZSAHU, ne hledáním
slova), přegeneruj inventář JAKO POSLEDNÍ KROK, spusť g3 a pak validate-all
(ne současně) a do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

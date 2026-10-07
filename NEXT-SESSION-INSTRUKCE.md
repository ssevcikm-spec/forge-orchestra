# ZADÁNÍ PRO DALŠÍ SESSION — DOKONČIT SLEPÁ MÍSTA (a jednu bránu, která tiše zúžila rozsah)

**Co tenhle dokument JE:** **zadání pro session P26**. Nahrazuje zadání z P25
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, nejnovější oddíl **§55**)
ani kronika (ta je v `KRONIKA-PROJEKTU.md`, nejnovější řádek **40**,
nálezy **§2.18**).

**Stav obou repů při psaní:** `forge-orchestra` = **`92aa80a`** ·
`uo-shadows` = **`932dc6f`**. `origin/main` orchestry = **`92aa80a`**
(**shodná**), `origin/main` hry = **`932dc6f`** (**shodná**).
**Práce P25 je v pracovním stromě** (necommitnutá — commit dělá session na
konci; **kdo to čte, ověří `git status` a `git log` ŽIVĚ**, ne podle tohohle
textu).
**Zkontrolováno při:** **7. 10. 2026, 14:2x +02:00 = 12:2x UTC**

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `92aa80a` · `uo-shadows` = `932dc6f`

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> (přes `tools\git.cmd` — schannel padá) v obou repech a **ověř
> `origin/main..HEAD` ŽIVĚ** (`git ls-remote` / `rev-list`), ne podle textu.
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
> `git diff`; `_analyza/p25-a-overeni.py` to dělá za tebe (A3 + kontrola hashe).
>
> **⚠ ŠESTÁ (NOVÁ, naměřená P25):** **ZÁPIS PODPROCESEM MŮŽE BÝT ODEMČENÝ**
> i ve `workspace-write` — `PermissionError [Errno 13]` ve **všech
> podadresářích** workspace, ale v **kořeni** zápis projde, zatímco nástroj
> `write` (harness) zapíše i do podadresáře. **Není to vada skriptu** — spadne
> na tom celé měřidlo i `git fetch`. Opravný skript ACL vrátí
> `NOT_THIS_CLASS`; pomůže **plný přístup** session. Past: skill
> `dsh-prostredi` §4e, nález `P25-J`.

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

### 0.1 P25 — Úkol A: přeměření práce P24 VLASTNÍM měřidlem — HOTOVO

| # | Co se ověřovalo | Výsledek |
|---|---|---|
| **A1** | měří měřidlo P24 opravdu to, co tvrdí? | **POTVRZENO**: vada do **kopie** tvrzení (`\| **B4** \|`) měřidlo shodí; **sabotované** měřidlo (bez kontroly B4) projde → kontrola B4 je to, co vadu chytá |
| **A2** | je `N > 0` u watchdogu **nastražená otázka**? | **POTVRZENO Z KÓDU**: značka `eskalovano` má **právě jeden** zápis a **žádné** mazání; živé `/tick` hlásí **0** (prah 3 < strop 5) → `N>0` by shodilo **zdravou** službu |
| **A3** | VOLÁ test tiku ty endpointy doopravdy? | **POTVRZENO**: zarážka v routeru (5 endpointů → `599`) zapnula **právě 5** cílených kontrol ze **42** červených; `A: /tick odpoví 200` zůstala **zelená**. Zarážka uvnitř handleru `cleanup` zapnula **právě 1** kontrolu |
| **A4** | čísla v §54 sedí | **POTVRZENO s posunem stavu**: `p24-a-overeni.py` dnes **99/1** (na kotvě `4925f64` **99/0**); jediná červená je **A8** — hra je na `932dc6f`, ne `44dd454`. Ostatní čítače §54 sedí (`17/0`, `100/0`→ dnes `146/0`, `31/0`→ dnes `41/0`) |
| **A5** | nepřepsala se historie | **POTVRZENO**: `kronika-kontrola` SEDÍ, **0 smazaných řádků session** v 8 commitech, necommitnutá změna kroniky taky 0 |
| **A6** | sondy nejsou brány a doklady nejsou pod kobercem | **POTVRZENO**: `p24-sonda-*` nejsou v `BRANY` (49) ani ve `spust()`; `VZOR` dávky `p20-d` bere i `p24-*`; negativní kontrola predikátu vady **najde** |

**Doklad:** `_analyza/p25-a-overeni.py` (**53 kontrol, 0 chyb**) +
`_analyza/p25-b-mutace.py` (**27 kontrol, 0 chyb** — pět mutací **v kopiích**).
Záznam: `HANDOFF.md` **§55**, kronika **řádek 40** a **§2.18**.

### 0.2 P25 — Úkol B1: endpointy, které ZAPISUJÍ a MĚNÍ CHOVÁNÍ — HOTOVO

`tools/test-tick-offline.mjs` nově volá i `POST /task`, `POST /game`
a `POST /game/active` a **ověřuje vázané hodnoty** (`bind`), ne jen tvar SQL:
**146/0** (bylo 100/0). Mutační důkaz `_analyza/tick-mutace.py` má
**20 vrat / 41/0** (bylo 15/31) — nová vrata **M16–M20**.
Nejsilnější nová kontrola je **W**: po `/game/active {active:false}` tik
**NEDISPATCHUJE**, po zapnutí dispatchuje **právě jednou**.

### 0.3 ⚠ CO JE V STROMĚ NECOMMITNUTÉ (stav při psaní zadání)

| Soubor | Co to je |
|---|---|
| `_analyza/p25-a-overeni.py`, `_analyza/p25-b-mutace.py`, `_analyza/p25-radek-kroniky.py` | měřidlo P25, jeho mutační důkaz a zápis záznamů (**nové**) |
| `tools/test-tick-offline.mjs` | +~300 řádků (T/U/V/W) |
| `_analyza/tick-mutace.py` | +5 vrat (M16–M20) a tisk `vrat: N` |
| `HANDOFF.md`, `KRONIKA-PROJEKTU.md`, `NEXT-SESSION-INSTRUKCE.md` | §55, řádek 40 + §2.18, tohle zadání |
| `_analyza/_registr-bran.json` | **generovaný** `g3` (49 bran) — needituj ho rukou |

---

## 1. Cíl (jedna věta)

**Zavřít poslední slepá místa conductora — a opravit jednu bránu, která po
přesunu záznamů TIŠE ZÚŽILA SVŮJ ROZSAH (nález P25-K).**

**Proč to patří nové session:** P25 zavřela tři zapisující endpointy; handler
jich má devatenáct. Zbylé (`/queue`, `/workers`, `/games`, `/game`, `/failed`,
`/status`, `/health`) **neměří žádný test**, a `ov-g-neovereno.py` dnes
kontroluje **1 řádek** místo **99** (tabulky Hxx se přesunuly do
`_archiv/HANDOFF-HISTORIE.md`). To je stejná třída jako §50.3: *vada, kterou
nikdo nezměří, se pozná až tím, že se něco stane.*

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — přeměřit P25 VLASTNÍM postupem

P25 si **sama psala záznamy i měřidlo** — a `AGENTS.md` je v tom jednoznačné:
*„autor není nezávislý reviewer"*. Každý bod měř **jinak, než vznikl**:

| # | Co ověřit | Jak (návrh; klidně vlastní) |
|---|---|---|
| **A1** | měřidlo P25 opravdu měří | Spusť `python _analyza\p25-a-overeni.py --plne` a `python _analyza\p25-b-mutace.py`. Pak **v kopii** uber tvrzení, které měřidlo hlídá (např. v kopii `KRONIKA-PROJEKTU.md` přejmenuj `\| **40** \|`), a ověř, že **spadne** (měřidlo má `--kronika <cesta>`); totéž pro `--zdroj`, `--g3`, `--validate`, `--p20d` |
| **A2** | **VOLÁ test tiku nové endpointy** (ne jen že existují) | Vlož do **kopie** conductora zarážku do `/task` (např. `if (false)` u validace `title/prompt`) a sleduj, **které kontroly se zapnou**; když nula, test o té smlouvě netvrdí nic. (P25 to dělá pro `/poll`…`/roadmap/reset` — pro `/task` to **nikdo nezměřil**) |
| **A3** | **vázané hodnoty** opravdu jdou do D1 | Ověř, že `vazby` v `fakeDb` **skutečně** zachycuje `bind()` (vlož do kopie testu `bind: () => api(sql)` bez záznamu → kontroly `T`/`V` musí spadnout) |
| **A4** | čísla v §55 sedí | Každý tvrzený čítač (`53/0`, `27/0`, `146/0`, `41/0`, `20 vrat`, `49 bran`, `99/1`) **znovu spusť**; porovnej s §55 |
| **A5** | **nález P25-K je pravdivý** | Ověř sám: `ov-g-neovereno.py` čte **jen `HANDOFF.md`** (řádek 48) a v něm je **1** řádek Hxx; v `_archiv/HANDOFF-HISTORIE.md` je **98** řádků Hxx. Změř i to, kolik z nich má `NEOVĚŘENO` — a rozhodni, jak měřidlo opravit |
| **A6** | nic se nerozbilo ani neztratilo | `g3` → **49 bran, jen deklarované exity**; `validate-all` → **VŠE V POŘÁDKU**; `handoff-kontrola-uplnost` → **83/83**; `kronika-kontrola` → **SEDÍ**; `ov-g-neovereno` → 0× NEOVĚŘENO (**a u toho zkontroluj ROZSAH**, viz A5) |

**Doklad:** vlastní skript v `_analyza/` (název `p26-*`), spuštěný a **uložený
i s výstupem**; a **musí umět selhat** (mutační test — vzor: `p25-b-mutace.py`).
Kdo přidá doklad do `_analyza/`, **přidá ho i do `_analyza/p20-d-doklady.py`**
(vzor `VZOR = re.compile(r"^(ov-|p1[6-9]-|p2[0-9]-)")` ho bere sám — ověř to).

### 2.2 Úkol B — VĚCNÁ PRÁCE (vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **B1** | **Opravit `ov-g-neovereno.py`, aby čítal i archiv** (nebo aspoň vypsal, KTERÉ soubory otevřel) — nález **P25-K** | `HANDOFF.md` §55.2/11, kronika §2.18/P25-K | Je to **brána, která tiše zúžila rozsah z 99 na 1** — přesně třída „zelená nad ničím“. Malý zásah, velký dopad |
| **B2** | **Dopsat testy pro zbylé endpointy**: `/queue`, `/workers`, `/games`, `/game`, `/failed`, `/status`, `/health` | `HANDOFF.md` §55.2/9, `conductor/src/index.ts` | Pokračování B1 (P24+B1 zavřely 8 z 19); jde to **bez nasazení** |
| **B3** | **Rozhodnout návrh `.gitattributes`** (P24-B) | `HANDOFF.md` §54.3 bod 2 | `git checkout` dnes **tiše rozbíjí mutační doklady**; návrh je hotový, chybí **rozhodnutí** |
| **B4** | **Ověřit B4 na ŽIVÉ službě** — `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**, pak hru vrátit | `HANDOFF.md` §45, `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 (B4) | Kód i brány hotové, **acceptance na živé službě neproběhlo**. ⚠ **Dočasně zastaví orchestra** → chce výslovné „ano" uživatele |
| **B5** | **Zapnout strop na granuli** (`GRAIN_MAX_RUNS = "5"`) | `HANDOFF.md` §46 | Až bude vidět, že watchdog stačí. ⚠ Změna chování živé služby = nasazení |
| **B6** | **Opravit slepé místo `over-skilly.py`** (fáze C) | `HANDOFF.md` §51.3 | ⚠ Pozor: soubor má **rozdělanou práci souběžné session** (`test-over-skilly-delegovane.py`) — nejdřív se domluv, nebo sáhni jinam |
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
python _analyza\p25-a-overeni.py            -> dávkový režim (A2,A5,A6)
python _analyza\p25-a-overeni.py --plne     -> A1-A6: 53/0
python _analyza\p25-b-mutace.py             -> 27/0
python _analyza\p24-a-overeni.py            -> 99/1 (A8 = hra na 932dc6f)
python _analyza\p24-b-mutace.py             -> 17/0
node tools\test-tick-offline.mjs            -> 146/0
python _analyza\tick-mutace.py              -> 20 vrat, 41/0
python _analyza\ov-g-neovereno.py           -> 0 ve stavu NEOVĚŘENO
                                               ⚠ a ZKONTROLUJ ROZSAH (P25-K)
python tools\over-skilly.py                 -> 13 skillu, 0 chyb
python tools\over-dokumentaci.py            -> 67 kontrol, 0 chyb
python _analyza\zadani-kontrola.py          -> kontroluje KOTVU tohohle zadani
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem. **A pozor: „zastaralý
inventář“ NENÍ deklarovatelný stav** — náprava je přegenerovat (nález P25-H).
**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`.**
**⚠ POČET VRAT NEPIŠ DO NÁZVU BRÁNY** — doklad ho od P25 **vypisuje sám**
(`vrat: N`) a registr `g3` ho nese.
**⚠ KDO MĚNÍ `_analyza/g3-brany.py`, MĚNÍ I `tools/validate-all.mjs`.**

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje).
2. **Zapiš výsledky** do `HANDOFF.md` (**nový oddíl**, jen **přidávej**) a do
   `KRONIKA-PROJEKTU.md`: **řádek session** do §1 (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**) a **nálezy** do §2.
   ⚠ **OMYLY SE OD 6. 10. 2026 NEVEDOU** — do sloupce omylů patří **`—`**
   a **souhrn §3 se nepřepočítává**.
   Řádky piš **skriptem** (vzor: `_analyza/p24-radek-kroniky.py` nebo
   `_analyza/p25-radek-kroniky.py`): řádky mají **přes 2000 znaků** a kotva
   z načteného řádku ho **zkrátí** (omyly **194**, **206**).
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — měřidlem `python _analyza\ov-g-neovereno.py`
   (**ne** hledáním slova) — **a zkontroluj, kolik řádků to měřidlo otevřelo**
   (nález **P25-K**: dnes 1 místo 99).
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE
   SOUČASNĚ**), inventář **jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Práce P25 je přeměřená, ne odsouhlasená** | A1: měřidlo projde **a** po vrácení vady spadne |
| 2 | **Test tiku endpointy opravdu VOLÁ** | A2: zarážka v handleru zapne aspoň jednu kontrolu (i pro `/task`) |
| 3 | **Vázané hodnoty se měří** | A3: vypnutý záznam `bind()` shodí kontroly `T`/`V` |
| 4 | **Čísla v §55 sedí** | A4: každý tvrzený čítač naměřen znovu |
| 5 | **Nález P25-K je ověřený a rozhodnutý** | A5: rozsah měřidla změřen; B1 (nebo vysvětlení, proč ne) |
| 6 | **Nic se nepřepsalo** | 0 smazaných řádků session + `kronika-kontrola` SEDÍ + `handoff-kontrola-uplnost` 83/83 |
| 7 | **Nic se nerozbilo** | `g3` → 49 bran, jen **deklarované** exity; `validate-all` → **VŠE V POŘÁDKU** |
| 8 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 9 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEDĚLEJ Z KONTROLY CÍL.** Ověřit máš **práci P25**, ne přidávat další
  měřidla. Nová brána je na místě **jen** tam, kde je doložená vada měření
  (P25-K je jedna z nich).
- **⚠ NESAHEJ NA ROZDĚLANOU PRÁCI SOUBĚŽNÉ SESSION** — necommituj ji, neopravuj
  ji, nemaž ji. Když ti překáží, **řekni to**. (Její je i obsah
  `_analyza/_registr-bran.json` — je **generovaný**.)
- **Nesahej na hru** — uživatel ji **záměrně pozastavil**, i když do ní souběžná
  session 7. 10. 2026 přidala commit `932dc6f`. Ověř ji, ale **nepiš do ní**.
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§53 = nasazení P23, §54 = ověření P24, §55 = P25).
- **Nemaž `_analyza/p2[45]-*`, `n03*-mutace.py`, `b*-mutace.py`,
  `tick-mutace.py` ani `ov-*`** — jsou to **doklady**; a **nemaž `_archiv`**
  (je to cesta zpět, i `_archiv/HANDOFF-HISTORIE.md` s 98 řádky Hxx).
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ** (obě sahají na inventář).
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM) a **nepoužívej `python -c`**
  s regexy ani `$(...)` — **piš skript do souboru**.
- **⚠ NEPŘERUŠUJ MUTAČNÍ BĚH** — po přerušení zůstanou mutanti v živém zdroji.
- **⚠ POZOR NA `git checkout` NAD `conductor/src/index.ts`** — CRLF a rozbité
  vícřádkové kotvy (a `git status` bude čistý).
- **⚠ NEPIŠ EVIDENCI PŘES `>`** — PowerShell tím vyrobí **UTF-16LE**.
- **Nepřesouvej nic zpátky na `C:`** a nemaž `E:\Workspaces\_acl-oprava-*`
  (rollbacky oprav ACL, včetně `_acl-oprava-20261007b` z P25).
- **Nepřebírej tvrzení z §55** — psal je autor, který si je i ověřoval.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (7. 10. 2026, 14:2x +02:00 = 12:2x UTC)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD            -> 92aa80a
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main      -> 92aa80a
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD             -> 932dc6f

# ziva sluzba (7. 10. 2026, ~12:1x UTC)
/health  -> ok=true ready=2 running=0 games=1
            targets[0]: main_ci ci.yml #118 (head 932dc6f), forge.ok=false,
                        selhani_v_rade=20
POST /tick -> watchdog: 0 ohlášeno (prah 3)     <- 0 je SPRÁVNĚ (trvalá značka)

# brany po P25 (po přegenerování inventáře)
python _analyza\g3-brany.py                  -> 49 bran, 1 deklarovaný exit, exit 0
node tools\validate-all.mjs                  -> VSE V PORADKU, exit 0
python _analyza\handoff-kontrola-uplnost.py  -> 83/83, CHYBI 0
python _analyza\p25-a-overeni.py --plne      -> 53 kontrol, 0 chyb
python _analyza\p25-b-mutace.py              -> 27 kontrol, 0 chyb
python _analyza\p24-a-overeni.py             -> 99 kontrol, 1 chyb (A8: hra 932dc6f)
python _analyza\p24-b-mutace.py              -> 17 kontrol, 0 chyb
node tools\test-tick-offline.mjs             -> 146 kontrol, 0 chyb
python _analyza\tick-mutace.py               -> 20 vrat, 41 kontrol, 0 chyb
python _analyza\ov-g-neovereno.py            -> 0 NEOVERENO (ale pozor: 1 radek Hxx!)
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

# ⚠ MERIDLA P24/P25: síť z Pythonu JDE, ale Cloudflare blokuje `Python-urllib`
#   (403 error code: 1010) — posílej User-Agent prohlížeče.
# ⚠ Měřidla P25 mají DÁVKOVÝ režim (A2,A5,A6) a PLNÝ (--plne): plný mutuje živý
#   zdroj a pouští g3, takže do dávky `p20-d` patří jen dávkový režim.
```

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P26. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — jen ověřuj, nepiš do ní)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P25 PŘEMĚŘILA práci P24 vlastním měřidlem
(_analyza/p25-a-overeni.py = 53/0, mutační důkaz p25-b-mutace.py = 27/0,
pět mutací v KOPIÍCH) a dokončila Úkol B1 — offline test tiku teď volá
i POST /task, /game a /game/active včetně vázaných hodnot a integrační
kontroly, že vypnutá hra zastaví dispatch (146/0, bylo 100/0; mutační důkaz
tick-mutace.py = 20 vrat / 41/0). Záznam je v HANDOFF.md §55 a v kronice
řádek 40 + §2.18. Od 6. 10. 2026 se OMYLY NEVEDOU — do sloupce omylů patří "—"
a souhrn §3 kroniky se nepřepočítává.

TVŮJ ÚKOL JE NEPŘÍJEMNÝ, ALE DŮLEŽITÝ: záznamy P25 psal autor, který si je sám
ověřoval — a AGENTS.md říká "autor není nezávislý reviewer". Přeměř to VLASTNÍM
měřidlem (§2.1 A1–A6). Zvlášť ověř DVĚ věci: (a) že test tiku opravdu VOLÁ
i nové endpointy /task, /game, /game/active (zarážka v handleru), a (b) nález
P25-K: ov-g-neovereno.py dnes čte JEN HANDOFF.md, kde zbyl 1 řádek Hxx, zatímco
98 jich je v _archiv/HANDOFF-HISTORIE.md — ověř to a rozhodni, jak měřidlo
opravit. Pak si vyber JEDNU věcnou práci (§2.2) — nejvýš je na řadě oprava
toho měřidla (B1) nebo testy pro zbylé endpointy (B2).

POZOR: ve workspace může pracovat SOUBĚŽNÁ session — její práci necommituj,
neopravuj a nemaž. Před commitem kontroluj INDEX (git show :soubor), ne pracovní
strom. Nepoužívej git show <sha>^ (git.cmd žere ^) a needituj .py přes
Set-Content (přidá BOM). NEPŘERUŠUJ mutační běh. A POZOR: git checkout nad
conductor/src/index.ts ho přepíše na CRLF a tiše rozbije vícřádkové kotvy
mutací (git status přitom bude čistý).

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS),
a ověř origin/main..HEAD ŽIVĚ, ne podle zadání. A všimni si: když podproces
nemůže zapsat soubor v podadresáři workspace (PermissionError 13) a do kořene
ano, je to STAV sandboxu, ne vada skriptu — řekni to uživateli (skill
dsh-prostredi §4e).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky do HANDOFF.md
(nový oddíl) a do KRONIKY (řádek session + nálezy; omyly = "—"), ověř, že
nezůstalo NEOVĚŘENO (měřidlem ov-g-neovereno.py VČETNĚ ROZSAHU, ne hledáním
slova), přegeneruj inventář JAKO POSLEDNÍ KROK, spusť g3 a pak validate-all
(ne současně) a do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

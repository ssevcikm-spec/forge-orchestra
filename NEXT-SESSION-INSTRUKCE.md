# ZADÁNÍ PRO DALŠÍ SESSION — NEZÁVISLE OVĚŘIT NASAZENÍ A ZÁZNAMY (a neztratit, co se nasadilo)

**Co tenhle dokument JE:** **zadání pro session P24**. Nahrazuje zadání z P23
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).
**Co NENÍ:** stav projektu (ten je v `HANDOFF.md` — nejnovější záznamy jsou
**§52** (předání) a **§53** (nasazeno a ověřeno živě)) ani kronika (ta je
v `KRONIKA-PROJEKTU.md`, nejnovější řádek **38**).

**Stav obou repů při psaní:** `forge-orchestra` = `7f0b2f8` · `uo-shadows` = `44dd454`
`origin/main` orchestry = **`7f0b2f8`** (**pushnuto**, `origin/main..HEAD` = **0**) ·
`origin/main` hry = **shodná**, strom orchestry má **necommitnutou práci SOUBĚŽNÉ
session** (viz §0.2).
**Zkontrolováno při:** **7. 10. 2026, 06:1x UTC = 08:1x +02:00**

**Kotva pro měření (tvar, který čte `_analyza/zadani-kontrola.py`):**
`forge-orchestra` = `7f0b2f8` · `uo-shadows` = `44dd454`
**Kotva pro měření:** `7f0b2f8` (na něm se měřilo; **po každém dalším commitu
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
> **⚠ ČTVRTÁ (NOVÁ, naměřená 7. 10. 2026):** **V REPU, KDE BĚŽÍ MUTAČNÍ TESTY,
> KONTROLUJ PŘED COMMITEM INDEX, NE PRACOVNÍ STROM.** Mutace **M8**
> (`_analyza/tick-mutace.py`) zůstala ve **stageované** verzi
> `conductor/src/index.ts` (`if (false) {`) — `git diff` ji **neukázal**,
> protože disk byl správně. Zachránila to až kontrola **`git show :soubor`**
> na známé značky mutantů. Kdyby se to podepsalo, odešel by do světa
> **vypnutý invariant 10** (`blocked` je terminální). Podrobně §53.3.

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

### 0.1 Práce session P23 (N0.3 + fáze B conductoru) — NASZENO

| # | Co se udělalo | Doklad |
|---|---|---|
| **N0.3** | `/health` hlásí stav **cíle**: `targets[]` s `main_ci` **i** `forge.ok`/`selhani_v_rade`; „nezměřeno" = `null`, ne „v pořádku" | `HANDOFF.md` **§42**, brána `tools/test-health-cile.mjs` (21/0) + `_analyza/n03-mutace.py` (11/0) |
| **B3a** | watchdog počítá běhy **granule** (dřív jeden úkol) a prah je **pod** stropem (`ESCALATE_AFTER` 8 → 3); značka v `roadmap.eskalovano` | **§43**, `tools/test-watchdog-granule.py` (17/0) + `b3-mutace.py` (11/0) |
| **B2 + B5** | `/report` → cooldown má bránu; nepravdivé komentáře o `MAX_ATTEMPTS` pryč (`grep "mrtvý kód"` → 0) | **§44**, `tools/test-report-cooldown.py` (8/0) + `b2-mutace.py` (9/0) |
| **B4** | bez **aktivní** hry se nedispatchuje (fallback na `GITHUB_REPO` pryč, dispatch smyčka se ptá na aktivní hry) | **§45**, `tools/test-listgames.py` (10/0) + `b4-mutace.py` (9/0) |
| **B3b** | strop na granuli `GRAIN_MAX_RUNS` — **výchozí `"0"` = VYPNUTO** (zapnutí je samostatný krok) | **§46**, `tools/test-grain-cap.py` (22/0) + `b3b-mutace.py` (11/0) |
| **Test rozhodovací logiky** | `tools/test-tick-offline.mjs` volá **skutečný `/tick` i `/report`** nad zbundlovaným conductorem s falešnou D1 (na neznámý dotaz **spadne**): **40 kontrol** | **§48–§50**, `_analyza/tick-mutace.py` (**8 vrat**, 17/0) |
| **Měřidla** | `c2-mutace.py` nově vykazuje čítač; deklarovaná výjimka `OCEKAVANE_BEZ_CITACE` zrušena; počet v **názvu** brány zrušen (zestarával) | **§47**, `_analyza/_registr-bran.json` |
| **Dokumentace** | skill `orchestra` + `README.md`: opraveny lži o nástrojích a **24 odkazů na neexistující layout** | **§51**, `over-skilly.py` → 54 zmínek, 0 mrtvých |

**Nasazení (obojí pushnuto, `origin/main` = `7f0b2f8`):**

| Commit | Co | Deploy |
|---|---|---|
| **`598e207`** | conductor: N0.3 + fáze B (25 souborů, +3714/−109) | **#33 → success** |
| **`7f0b2f8`** | kronika §1/**38**, plány N0.3/B2–B5 na HOTOVO, `HANDOFF.md` **§53** | dokumentace, nic nenasazuje |

**Živě ověřeno po nasazení (7. 10. 2026, 06:08 UTC):**
`/health` → `targets[0]`: `main_ci: success (ci.yml #117)`, **`forge.ok: false`**,
**`selhani_v_rade: 20`** · `/tick` → **`watchdog: 2 ohlášeno (prah 3)`**,
`spusteno: 1 úloh`, `zombie zablokováno: 1`.

### 0.2 ⚠ SOUBĚŽNÁ SESSION PRACUJE VE STEJNÉM STROMĚ

Ve workspace je **necommitnutá práce druhé session** (generalizace nástrojů —
nahrazuje zapečené cesty `C:\Users\Ssevc\…` za `DSH_HOME`/`HOME`): změněné
`_analyza/ag-over-cisla.py`, `_analyza/b-mutace.py`, `_analyza/kronika-kontrola.py`,
`_analyza/n8-zastarala-analyza.py`, `_analyza/ov-*.py` (8 souborů),
`_analyza/p22-test-mutace.py`, `_analyza/zadani-kontrola.py`,
`tools/over-dokumentaci.py`, `tools/over-skilly.py`.
**Patří jí — necommituj ji a neopravuj ji.** Zároveň: **kvůli ní průběžně
zestarává `_analyza/_inventar.json`** (je to vstup skeneru) — to není vada.

---

## 1. Cíl (jedna věta)

**Nezávisle přeměřit, že nasazená práce SKUTEČNĚ dělá to, co o ní záznamy
tvrdí — a že se při ní nic neztratilo ani nepodepsalo.**

**Proč to patří nové session:** záznamy **§52/§53** i řádek kroniky psal **autor
téže session, která práci i nasazovala** — a `AGENTS.md` je v tom jednoznačné:
*„autor není nezávislý reviewer"*. Navíc šlo do živé služby **355 řádků
`index.ts`** a **6 nových bran**; „nic se nerozbilo" se u toho **dokazuje
měřením, ne pamětí**. A je tu **konkrétní naměřená stopa**, že se to podepsat
mohlo: mutant M8 zůstal ve stageované verzi (§53.3) — kdo ví, co ještě.

---

## 2. Úkoly

### 2.1 Úkol A (POVINNÝ) — nezávislé přeměření nasazení a záznamů

Každý bod měř **jiným postupem**, než jak vznikl (ne „přečtu to a souhlasím"):

| # | Co ověřit | Jak (návrh, klidně si zvol vlastní) |
|---|---|---|
| **A1** | **Živá služba běží na tom commitu, který se tvrdí** | Ne z dokumentu: zjisti z GitHub API poslední **úspěšný** běh `deploy.yml` a jeho `head_sha`; porovnej s `HEAD`. Pak **zavolej živý `/health`** a ověř, že vrací `targets[]` (to umí **jen** kód z `598e207`). Tvrzení i měření zapiš |
| **A2** | **Watchdog opravdu eskaluje (B3a)** | Dvě nezávislé cesty: (a) `/tick` a jeho věta `watchdog: N ohlášeno (prah P)`; (b) **stav v D1** — kolik granul má `roadmap.eskalovano` a jaké. Když k D1 nemáš přístup, **řekni to** (`nezměřeno` ≠ 0) |
| **A3** | **V commitu NEJSOU mutanty** (a to ani v indexu) | Projdi **oba commity** (`598e207`, `7f0b2f8`): u každého souboru, který mutační testy mutují (`conductor/src/index.ts`, `conductor/wrangler.toml`, `AGENTS.md`), hledej **známé značky mutantů** (`if (false) {`, `merged = true;`, `selhani_v_rade: 0,`, `ESCALATE_AFTER = "9"`, …). Postup ber z **blobů** (`git show <sha>:<soubor>`), ne z pracovního stromu |
| **A4** | **Brány umí selhat i po nasazení** | Spusť **6 nových mutačních důkazů** (`n03`, `b3`, `b2`, `b4`, `b3b`, `tick`) a ověř, že **každý** hlásí `0 chyb` a že po něm je `index.ts` **bajt na bajt** zpět (`git status` čistý u těch souborů). Pak **jednu** mutaci provedl ručně mimo knihovnu a sleduj, že test **spadne** (kontrola, že knihovna není ta, kdo měří) |
| **A5** | **Nic nezmizelo** | `python _analyza\handoff-kontrola-uplnost.py` → **83/83, CHYBÍ 0**; **nezávisle**: `git diff --stat 598e207~1 7f0b2f8` musí u `KRONIKA-PROJEKTU.md` ukázat **jen přidání** a **řádky 1–37 musí být bajt na bajt** jako v `git show 598e207~1:KRONIKA-PROJEKTU.md` |
| **A6** | **Čísla v plánech sedí na kód** | `PLAN-ORCHESTRA-AI-AGENTI.md` u **N0.3** a `PLAN-ROZVOJ-ORCHESTRA.md` u **B2–B5** teď tvrdí HOTOVO — ověř, že to **odpovídá kódu** (`grep` na `main_ci`, `eskalovano`, `GRAIN_MAX_RUNS`, `listGames`), a že tvrzené čítače brán (21/11, 17/11, 8/9, 10/9, 22/11, 40/17) **naměříš znovu stejně** |
| **A7** | **Tvrzení o souběhu je dnešní** | Ověř, že soubor změn ze §0.2 **ještě platí** (`git status --porcelain`), a že v mém commitu **nejsou** soubory té druhé session (`git show --stat 598e207` je nesmí obsahovat) |
| **A8** | **Hra a její CI nejsou dotčené** | `uo-shadows` = `44dd454`, strom **čistý**; `git diff --name-only 598e207~1 7f0b2f8` nesmí obsahovat **nic** z cesty do hry |

**Doklad:** vlastní skript v `_analyza/` (název `p24-*`), spuštěný a **uložený
i s výstupem**; **a musí umět selhat** (mutační test: uber v kopii dokumentu
jeden nadpis a sleduj, že skript spadne). Kdo přidá doklad do `_analyza/`,
**přidá ho i do `_analyza/p20-d-doklady.py`** — jinak shnije.

### 2.2 Úkol B — VĚCNÁ PRÁCE (teprve po Úkolu A; vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **B1** | **Ověřit B4 na ŽIVÉ službě** — `POST /game/active {active:false}` → `/health` `games=0` a **žádný dispatch**, pak hru vrátit zpět | `HANDOFF.md` **§45**, `PLAN-ROZVOJ-ORCHESTRA.md` §3.5 (B4) | Kód i brány jsou hotové, **acceptance ještě na živé službě neproběhlo**. ⚠ **Dočasně zastaví orchestra** — chce výslovné „ano" uživatele |
| **B2** | **Zapnout strop na granuli** (`GRAIN_MAX_RUNS = "5"`) — druhý krok B3b | `HANDOFF.md` **§46** | Až bude vidět, že watchdog stačí. ⚠ Je to **změna chování živé služby** = nasazení |
| **B3** | **Rozšířit offline test tiku** na endpointy, které **nemá** žádný test: `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset` | `HANDOFF.md` **§50.3** | Je to **největší zbylé slepé místo** rozhodovací logiky — a jde to **bez nasazení** |
| **B4** | **Opravit slepé místo `over-skilly.py`** („0 mrtvých cest“, a přitom 24 odkazů na neexistující layout prošlo) | `HANDOFF.md` **§51.3** | Fáze C: „brány, které lžou“. ⚠ **Soubor má rozdělanou práci souběžné session** — nejdřív se domluv, nebo sáhni jinam |
| **O1** | **Rozhodnout `O3`, `O10`, `O5–O8`** | `PLAN-ROZVOJ-ORCHESTRA.md` **§6** | Jsou to **rozhodnutí**, ne kód — hodí se, když se nemá sahat na živou službu |

**Podmínky:** vybrat **JEDNU** a říct kterou · než začneš měnit kód, **změř
současný stav** (ne z dokumentu) · u conductoru **zavolej živou službu** a ukaž
vadu na její odpovědi · **`done` je tvrzení, ne důkaz** · ověř nasazení
**třemi kroky** (`HTTP 200` není důkaz).

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

Nový baseline po P23 (počet bran vzrostl z 37 na **49**):

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány PO SOBĚ (ne současně — obě sahají na _inventar.json):
python _analyza\g3-brany.py                 -> 49 bran, 0 bez čítače,
                                               2 nenulové exity (zadani kontrola
                                               DEKLAROVANY + validate-all), exit 1
node tools\validate-all.mjs                 -> po pushi 0 problému; před pushi
                                               1 (E. lokální kód = repo)
python _analyza\kronika-kontrola.py         -> KRONIKA SEDI (208 omylu / 27 bloku / 36 sessions)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python tools\over-skilly.py                 -> 13 skillu, 0 chyb, 54 zminek, 0 mrtvych
python tools\over-dokumentaci.py            -> 67 kontrol, 0 chyb
python _analyza\zadani-kontrola.py          -> kontroluje KOTVU tohohle zadani
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem.
**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`.**
**⚠ POČET VRAT NEPIŠ DO NÁZVU BRÁNY** — zestaral dvakrát (3 → 6 → 8); čítač
vykazuje test sám a registr `g3`.
**⚠ KDO MĚNÍ `_analyza/g3-brany.py`, MĚNÍ I `tools/validate-all.mjs`** (dva
seznamy živých bran) — a oba se musí shodovat s během.

### 2.4 Úkol D — ZÁZNAMY (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session (jen jedno existuje).
2. **Zapiš výsledky** do `HANDOFF.md` (**nový oddíl**, jen **přidávej**) a do
   `KRONIKA-PROJEKTU.md`: **řádek session** do §1 (typ z nabídky
   `akční`/`plánovací`/`ověřovací`/`analýza`/`rozhodovací` — **jiný brána
   neuzná**) a **nálezy** do §2.
   ⚠ **OMYLY SE OD 6. 10. 2026 NEVEDOU** — uživatel rozhodl **„omyly nepiš"**;
   do sloupce omylů patří **`—`** a **souhrn §3 se nepřepočítává**
   (není to nula, je to vědomě nevedený sloupec). Řádky piš **skriptem**
   (vzor: `_analyza/n03d-radek-kroniky.py`, **12/0**): řádky mají **přes 2000
   znaků** a kotva z načteného řádku ho **zkrátí** (omyly **194**, **206**).
3. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
4. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all` (**NE SOUČASNĚ**),
   inventář **jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
5. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená“ pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Nasazení je přeměřené, ne odsouhlasené** | A1: `head_sha` úspěšného deploye = `HEAD`; živé `/health` vrací `targets[]` |
| 2 | **Watchdog je doložený dvěma cestami** | A2: věta z `/tick` **i** stav v D1 (nebo přiznané `nezměřeno`) |
| 3 | **V commitech nejsou mutanty** | A3: kontrola **blobů**, ne pracovního stromu; A4: 6 mutačních důkazů zelených a strom po nich čistý |
| 4 | **Nic nezmizelo** | A5: `handoff-kontrola-uplnost` **83/83**; `git diff` = jen přidání; řádky 1–37 kroniky **bajt na bajt** |
| 5 | **Čísla v plánech sedí na kód** | A6: naměřené čítače = tvrzené |
| 6 | **Nic se nerozbilo** | `g3` → 49 bran, jen **deklarované** exity; `validate-all` → **0 problémů** (po pushi) |
| 7 | **Push je ROZHODNUTÍ uživatele** | u `conductor/**` navíc **nasadí živou službu** |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEDĚLEJ Z KONTROLY CÍL.** Ověřit máš **nasazení a záznamy**, ne přidávat
  další měřidla. Nová brána je na místě **jen** tam, kde je doložená vada
  měření (jako §51.3) — ne „pro jistotu".
- **⚠ NESAHEJ NA ROZDĚLANOU PRÁCI SOUBĚŽNÉ SESSION** (§0.2) — necommituj ji,
  neopravuj ji, nemaž ji. Když ti překáží, **řekni to**.
- **Nesahej na hru** — uživatel ji **záměrně pozastavil**; `uo-shadows` musí
  zůstat na `44dd454` a čistá.
- **Nepřepisuj `HANDOFF.md` ani `KRONIKU`** — jen **přidávej**; historická čísla
  se **nechávají citovaná** (§52 = plán nasazení, §53 = co se nasadilo).
- **Nemaž `_analyza/n03*-mutace.py`, `b*-mutace.py`, `tick-mutace.py`,
  `n03d-radek-kroniky.py` ani `ov-*`** — jsou to **doklady**; a **nemaž
  `_archiv`** (je to cesta zpět).
- **Nespouštěj `g3` a `validate-all` SOUČASNĚ** (obě sahají na inventář).
- **Neupravuj `.py` přes `Set-Content`** (přidá BOM) a **nepoužívej
  `python -c`** s regexy ani `$(...)` — **piš skript do souboru**.
- **Nepřesouvej nic zpátky na `C:`** a nemaž `E:\Workspaces\_acl-oprava-20261006\`
  (rollback opravy ACL z 6. 10. 2026).
- **⚠ PŘED COMMITEM KONTROLUJ INDEX, NE PRACOVNÍ STROM** (mutant M8, §53.3).
- **Nepřebírej tvrzení z §52/§53** — psal je autor, který si je i ověřoval.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (7. 10. 2026, 06:1x UTC = 08:1x +02:00)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD           -> 7f0b2f8
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main     -> 7f0b2f8
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD            -> 44dd454

# deploy a ziva sluzba (7. 10. 2026, 06:06-06:08 UTC)
deploy.yml beh #33 na head_sha 598e207            -> completed / success
GET  /health  -> ok=true ready=1 running=0 games=1
                 targets[0]: main_ci: success (ci.yml #117)
                             forge.ok=false, selhani_v_rade=20
POST /tick    -> spusteno: 1 uloh; watchdog: 2 ohlášeno (prah 3)

# brany po nasazeni (session, ktera to nasazovala)
python _analyza\g3-brany.py                  -> 49 bran, 0 bez citace
python _analyza\kronika-kontrola.py          -> KRONIKA SEDI (208 / 27 / 36)
python _analyza\handoff-kontrola-uplnost.py  -> 83/83, CHYBI 0
python tools\over-skilly.py                  -> 13 skillu, 0 chyb, 54 zminek, 0 mrtvych
python tools\over-dokumentaci.py             -> 67 kontrol, 0 chyb
python tools\kontrola-diakritiky.py          -> VSE OK (256/300, 0 chyb)

# ⚠ TRIK PRO PUSH (PAT se NIKDY nevypisuje):
#   $pat = (Get-Content .secrets\github_pat.txt -Raw).Trim()
#   $b64 = [Convert]::ToBase64String([Text.Encoding]::ASCII.GetBytes("x-access-token:$pat"))
#   & .\tools\git.cmd -c "http.extraHeader=AUTHORIZATION: basic $b64" push origin main

# ⚠ PRED COMMITEM: kontrola STAGOVANEHO blobu na znacky mutantu
#   git show :conductor/src/index.ts   (hledej: if (false) {, merged = true;, ...)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
```

**Uložené doklady, které k tomu patří:** `_analyza/tick-mutace.py` (**8 vrat,
17/0** — včetně historických vad **B1** a **A1**), `tools/test-tick-offline.mjs`
(**40 kontrol**, volá skutečný `/tick` i `/report`), šest mutačních důkazů
(`n03`, `b3`, `b2`, `b4`, `b3b`, `tick`) a `_analyza/n03d-radek-kroniky.py`
(**12/0**, zápis řádku 38).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session P24. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — nesahej na ni)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (Úkol A) a §3 (hotovo znamená).

Kontext: session P23 nasadila do ŽIVÉ služby N0.3 (stav cíle v /health) a celou
fázi B conductoru (B2, B3a, B3b, B4, B5) — commity 598e207 + 7f0b2f8, deploy #33
success, živě ověřeno: /health targets[0] = main_ci success, forge.ok false,
selhani_v_rade 20; /tick = "watchdog: 2 ohlášeno (prah 3)". Od 6. 10. 2026 se
OMYLY NEVEDOU (uživatel rozhodl "omyly nepiš") — do sloupce omylů patří "—"
a souhrn §3 kroniky se nepřepočítává.

TVŮJ ÚKOL JE NEPŘÍJEMNÝ, ALE DŮLEŽITÝ: ty záznamy i nasazení dělal autor, který
sám sebe ověřoval — a AGENTS.md říká "autor není nezávislý reviewer". Přeměř to
VLASTNÍM měřidlem (§2.1 A1-A8): běží živá služba na tom commitu, který se tvrdí?
eskaluje watchdog opravdu (dvěma cestami)? nejsou v commitech MUTANTY (u P23
jeden zůstal ve stageované verzi index.ts — viz §53.3)? nezmizelo nic
(handoff 83/83 + diff jen přidání + řádky 1-37 kroniky bajt na bajt)?

POZOR: ve workspace pracuje SOUBĚŽNÁ session (generalizace nástrojů) — její
necommitnutou práci necommituj, neopravuj a nemaž; kvůli ní průběžně zestarává
_inventar.json (to není vada). Před commitem kontroluj INDEX (git show :soubor),
ne pracovní strom. Nepoužívej git show <sha>^ (git.cmd žere ^) a needituj .py
přes Set-Content (přidá BOM).

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS),
a ověř origin/main..HEAD ŽIVĚ, ne podle zadání.

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky do HANDOFF.md
(nový oddíl) a do KRONIKY (řádek session + nálezy; omyly = "—"), ověř, že
nezůstalo NEOVĚŘENO, přegeneruj inventář JAKO POSLEDNÍ KROK, spusť g3 a pak
validate-all (ne současně) a do chatu vlož prompt pro uživatele i se STAVOVÝM
ŘÁDKEM.
```

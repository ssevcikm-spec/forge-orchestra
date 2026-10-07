# HANDOFF — orchestra: stav po AKČNÍ session (Úkoly A–D a B1)

> **Co tenhle dokument JE:** stav. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 2. 10. 2026 · **Poslední session:** **AKČNÍ** (Úkoly A–D, B1,
11:0x–11:2x UTC — **§16**) · **Předchozí:** `eb127abd` („Hluboká kontrola
a plán úprav", §15) · `7cd67c66` (analýza, S31–S37) a `7db45275` (jazyk v kódu)

> ## Jak tenhle handoff číst
>
> Tenhle soubor je **jediný vstupní bod** — byl **sjednocen** 2. 10. 2026 po
> tom, co v jednom workspace pracovaly **tři session** a stav se rozpadl na
> tři dokumenty, které si navzájem odporovaly. Sekce:
>
> | § | Co v ní je |
> |---|---|
> | **1** | **Co je hotové** (a čím je to doložené — spuštěním, ne čtením) |
> | **2** | **Co je otevřené** (nic se nemaže; i to, co „nikdo neřeší") |
> | **3** | **Nové nálezy N1–N9** z provádění — včetně **mých vlastních omylů** |
> | **4** | **Mapa zdrojů** — který dokument je autorita pro co |
> | **5** | **Running state** (živý stav, měřený) |
> | **6** | **Jak ověřit** (spustitelné příkazy) |
> | **7** | **PICK UP HERE** — zadání pro novou session **+ výzva k ověření mé práce** |
> | **8** | **Vlastní omyly** — všech session, včetně téhle |
> | **9** | **Co už otevřené NENÍ** |
> | **10** | **Tahle session: PR #28–#31 — co bylo vadné, co je sloučené, co je připravené** |
> | **11** | **Stav pro session, která čekala na push** (co je pushnuté, co ne, co se změnilo) |
> | **12–14** | předchozí zadání a provedení (push, granule, N1/N3, nástroje) |
> | **15** | **OVĚŘENÍ PRÁCE SESSION `eb127abd`** (plánovací session 2. 10. 2026) — 11 tvrzení, 5 nových nálezů P1–P6, co zestaralo |
> | **16** | **PROVEDENO AKČNÍ SESSION** (2. 10. 2026, 11:0x–11:2x UTC) — Úkoly A–D, **B1 nasazen**, §16.7 co se nepovedlo, **§16.8 omyly**, §16.10 co ověřit |
>
> **⚠ Pro novou session:** **nejnovější stav je §16** (§16.10 = co je nutné
> ověřit, §16.7 = co zůstává otevřené). **§15** je ověření práce předchozí
> session — **nerekonstruuj ji**. Zadání pro **plánovací** session je
> v `NEXT-SESSION-INSTRUKCE.md`; plán je v `PLAN-DALSI-KROK.md`.
> **Výzva k ověření v §7.2 je SPLNĚNÁ** — její výsledek je v **§7.5**.

---

## 0. Co se stalo (a proč je tenhle handoff sjednocený)

**Naměřeno 2. 10. 2026:** v jednom workspace běžely **tři session** a psaly
**tytéž soubory**:

| Session | Co dělala | Kdy |
|---|---|---|
| `7cd67c66` | druhé kolo hloubkové analýzy (S31–S37) | 05:39–06:10 UTC |
| `7db45275` | jazykový inventář a plán Z1–Z8 | ~06:00–06:35 |
| **`eb127abd`** | **provedení A1–A4 + Z1–Z8** (tahle) | 06:45–09:0x |

**Následek, který je potřeba vidět:** `HANDOFF.md` psaly **dvě session
současně** (jedna ho přepsala verzí, které chyběla rozhodnutí té druhé),
a **třetí session** (tahle) nad ním provedla změny, které **zastaraly
analýzu**, jež je jinak výchozím bodem. Vznikly **tři dokumenty, každý
s jiným „dnešním stavem"** — tedy přesně vada, o které ta analýza je.

**Co s tím tahle session udělala:**
1. **Sjednotila zdroje** — každý dokument teď v hlavičce říká, **čím je**
   (zadání / snapshot / záznam o provedení), a odkud brát současný stav.
2. **Změřila, co je zastaralé** (`_analyza\n8-zastarala-analyza.py`) — místo
   aby se to hádalo.
3. **Napsala, co je hotové a jak to ověřit** (níž), včetně **výzvy k ověření**.

**Poučení pro příště (napsané, aby se nemuselo objevit znovu):** dvě session
nad jedním workspace si musí **předem** říct, kdo píše `HANDOFF.md` — a kdo
provede analýzu, musí **do její hlavičky zapsat datum spotřeby**. Bez toho se
analýza za dvě hodiny čte jako popis dneška (nález **N8**).

---

## 1. Co je HOTOVÉ (doloženo spuštěním, ne čtením)

### 1.1 Provedeno touto session — kód (nepushnuto, necommitnuto)

| Plán | Položky | Doklad |
|---|---|---|
| **A1** `done` jen při `ok && merged` + stav `awaiting_human` | ✅ | `_analyza\a1-a2-over.py` — **23 kontrol**, **4 mutace chyceny** (číslo opraveno 2. 10. 2026 ve 20:4x UTC; brána mezitím vyrostla z 19) |
| **A2** `owns` ověřeno proti `origin/main` (+ cache s TTL 10 min) | ✅ | tamtéž |
| **A3** `exit 1` v **obou** `agent.yml` | ✅ | `_analyza\a3-over.py` — **6×** (bylo 5×) |
| **A4a** lint hlásí chybějící `size_lines` | ✅ | `lint-roadmapa.py` → **13 z 18**, `exit 0` |
| **A4b** zastaralý text varování `[5]` | ✅ | text opraven |
| **Z1–Z8** hranice jazyka (11 míst) | ✅ | `hl-rizika-jazyka.py` → **0 očekávaných, 11 přejednaných, 0 vrácených** |

**Změněné soubory** (`git status`): orchestra **10**, hra **6**.
**`HEAD` obou repů beze změny** (`3a2e691`, `d0bf4f9`) — **nic není commitnuté.**

### 1.2 Ověřeno touto session — že KROK 1 ZADÁNÍ BYL SPLNĚN

`ANALYZA-HLOUBKOVA-2-ZADANI.md` („prompt k poslední hluboké kontrole") byl
**v repu celou dobu** a je **splněný**: `_analyza\hl2-kontrola.py` →
**9/9 bodů „Hotovo znamená", `exit 0`**; brána **umí selhat**
(`hl2-mutace-kontrola.py` → **6/6 mutací**).

> **Tuhle session to zprvu tvrdilo opak** („prompt nedorazil") — protože
> **převzala tvrzení z `HANDOFF.md` §8.4, aniž soubor otevřela**. Je to
> **můj omyl č. 5** níž a je to poučení, ne historka.

### 1.3 Brány — stav po všech změnách (`exit 0`, pokud není řečeno jinak)

```
skener jazyka (23/23) · hl-rizika-jazyka (0/11/0) · A1/A2 (23 kontrol, 4 mutace)
A3 obě kopie · kontrola-diakritiky · over-dokumentaci (63/0) · over-skilly (12/0)
test-eskalace · lint-roadmapa · sjednot-sablonu · check-schema (obě kopie)
tsc --noEmit · testy hry (65 kontrol, 0 selhání) · parser témat (--test)
```
> **⚠ ČÍSLA O KONTROLÁCH OPRAVENA 2. 10. 2026 ve 20:4x UTC** (B1 i A1/A2):
> `testy hry` bylo **38**, dnes je **65**; `A1/A2` bylo **19**, dnes je **23`.
> Obě čísla **zestarala růstem bran**, ne že by byla lživá (A2) — a odhalil to
> až `audit2b-cisla-proti-zdroji.py`, protože **ta čísla nevydává jedna brána**.
> Naměřeno: `audit2b` u `kontrol` srovnává **registr šesti bran** (65, 63, 61,
> 59, 23, 10) — kdo si přečte jen jedno z nich, hlásí tři čtvrtiny správných
> čísel jako rozchod (nález **H29**).

**`kontrola-driftu.mjs` = `exit 1`, 1 rozdíl** — **známý** rozdíl **tří kroků**
(šablona je má, hra ne). **Není to regrese** a **není to kritérium dokončení
A3**; ověřeno, že A3 ten rozdíl **nezvětšil**.

---

## 2. Co je OTEVŘENÉ (nic se nemaže)

### 2.1 Nové z této session (N1–N9)

Všechno v **`IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md`**, s postupem u každého:

| # | Nález | Proč to je otevřené |
|---|---|---|
| **N1** | **`hl-rizika-jazyka.py` měří ZASTARALÝ snapshot** — inventář si vygeneruje jen když chybí | Naměřeno: inventář 08:01, rename 08:38 → hlásil **7 vad, které už byly opravené**. **Nástroj vypadá, že měří.** |
| **N2** | `hl-rizika-jazyka.py` **není** samostatné měření (čte meziprodukt) | `IMPLEMENTACE-HRANICE-JAZYKA.md` §5 to neříká → falešný poplach při doslovném plnění |
| **N3** | **NOVÁ TŘÍDA:** kontrola projde na obou místech **z různých důvodů** | V herním repu nese `FORGE_ATTEMPT` **jiný krok** než v šabloně |
| **N4** | `kontrola-driftu.mjs` je **slepá k `env`** kroků | Porovnává jen **jména** kroků, ne obsah |
| **N5** | ~~komentář `index.ts:372-374` odporoval kódu~~ | **OPRAVENO** v této session |
| **N6** | A4 tvrdí „7 varování `[5]`", naměřeno **10** | **Rozdíl v ČASE**, ne nepravda — patří k tomu čas, ne přepis |
| **N7** | ~~cache `origin/main` bez TTL~~ | **OPRAVENO** — **vlastní omyl**, viz §8 |
| **N8** | **ANALÝZA SE ROZEŠLA S KÓDEM** (5 tvrzení) | Kdo ji čte jako popis dneška, **čte jiný stav**. Hlavička to už přiznává |
| **N9** | **`AGENTS.md` tvrdil „32 sloupců", správně je 39** | **Chybné od zápisu**, ne zestaralé — přes **šest session** si toho nikdo nevšiml. **Opraveno** + nástroj `_analyza\ag-over-cisla.py` (**mutačně 5/5**) + pravidlo „i trvalá pravidla se přeměřují" |

### 2.2 Čeká na rozhodnutí uživatele (z 1. kola — beze změny)

- **O3 — opravit vady conductoru?** Fáze B. Deploy je z gitu → rozhodnutí.
  **Návrh:** nasadit **B1 po částech** (první deploy jen přidá sloupec a začne
  do něj zapisovat; teprve druhý přepne guard).
  **Pozor:** A1–A4 se týkaly **téhož souboru** (`index.ts`) → **rozhodnout
  O3 a A1–A4 společně** dávalo smysl; **A1–A4 jsou teď provedené**, takže
  O3 se rozhoduje **sám**.
- **O10 — má být ST9-část (testy conductora čtou SQL ze zdrojáku) součástí
  fáze B?** Návrh: **ano**.
- **O5, O6, O7, O8** — cesty v konfiguraci, vlastnictví souborů, druhá hra,
  způsob schvalování fází. Vše v `PLAN-ROZVOJ-ORCHESTRA.md` §6.

### 2.3 ~~Tři visící PR~~ — **VYŘEŠENO 2. 10. 2026, otevřené už nejsou**

> **⚠ ZASTARALÉ, ZACHOVÁNO JAKO ZÁZNAM (ověřeno 2. 10. 2026 v 10:4x UTC):**
> PR **#28, #29, #30 i #31 jsou SLOUČENÉ** — #30 v **07:40**, #29/#28 v **07:56**,
> #31 v **08:02** UTC. **Otevřených PR je 0 z 31.** Podrobně (co bylo vadné
> a proč to CI nevidělo) **§10**. Text níž je popis stavu **před** sloučením.

PR **#28** (`save.gd`, `persist.save`, +91), **#29** (`hud.gd`, `ui.hud`, +77),
**#30** (`mining.gd`, `sim.mining`, +67) — všechny `open`, `merged_at: null`.
**Příčina naměřená:** ani jedna z těch granul **nemá `size_lines`** → platí
výchozích **60** → gate je správně zamítl. `size_lines` chybí u **13 z 18**.
**Důsledek:** `main` **nemá ukládání, HUD ani těžbu**, ačkoli je conductor
vedl jako `done` (**A1 to teď už nezapíše** — to je celý smysl opravy).
**A `engine.shell`** na všechny tři čeká. **Možnosti:** (a) sloučit ručně,
(b) doplnit `size_lines` a nechat projet znovu, (c) nechat být a vědět o tom.

### 2.4 Otevřené otázky k A1–A4 (zůstávají)

- **Má `lint-roadmapa.py` u `[5]` skončit nenulově?** Dnes `exit 0`.
  Kdyby skončil nenulově **teď**, začne padat na granulích, které jsou
  v pořádku. → **rozhodnout člověku.**
- **Má A2 varovat, nebo jen mlčet?** (Kolik notifikací je ještě užitečných.)
  Dnes **varuje** (`notify` + `console.log`) — dá se vypnout.

### 2.5 Otevřené technické body (s dnešním stavem)

- **N0.2 — brána na závislosti bran.** Pillow se opravil, **třída chyby
  zůstala** (S18). Návrh: krok v `ci.yml`, který ověří dostupnost importů bran.
- **N0.3 — stav CI cílové hry v `/health`.** Conductor hlásí `ok: true` nad
  čímkoli. **Obrana proti S18** — a nově i proti S29/S31.
- **Tři různé `vision.test.mjs`** (N12) — **neměřeno** (sandbox `EPERM`).
  Čísla „36/36", „28/28", „5 OK / 23 chyb" jsou **z předchozích session,
  neověřená**. Statické počty `test(` **nejsou počet testů**.
- **`Z8`/`Z9` nehotové:** `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` tvrdí
  „27 untracked jednorázových" a cituje `migrace-schema.py`, které už
  neexistuje; `PLAN-SEPARACE-WORKSPACE.md` vznikl před F0.4/F0.5.
- **Tajemství nemají izolované ACL** (N10) — separace to neopraví, SID se dědí
  z rootu workspace.
- **`index.ts:31` a `:233` pořád tvrdí, že `MAX_ATTEMPTS` je mrtvý kód** —
  naměřeno: načítá se a rozhoduje → **B5**.
- **Dva plány k revizi:** `PLAN-ORCHESTRA-AI-AGENTI.md` (N0–N5, R1–R15) má
  hotové N0.1 a N1.1; `PLAN-SEPARACE-WORKSPACE.md` (G0–G5, S1–S9) nedotčený.
- **`CONVENTIONS.md` šablony nemá pravidlo o jazyce** — jediný bod „Hotovo
  znamená" z `IMPLEMENTACE-HRANICE-JAZYKA.md` §8, který **zůstal nehotový**.
- **Fáze B–D nezačaté.** Stav: **F0 hotová · fáze A hotová a ověřená ·
  B–D nezačaté.** Celý plán v `PLAN-ROZVOJ-ORCHESTRA.md` §3.5.

| Fáze | Co | Blokuje rozhodnutí? |
|---|---|---|
| **B** | **B1** `naposledy_selhalo` místo `updated_at` (S12) · **B2** `/report` zapíše roadmapu (S13) · **B3** strop a watchdog na `i_id` (S14/S21) · **B4** `listGames` fallback · **B5** komentáře `:31`, `:233` | **ANO — O3, O10** |
| **B + nové** | **S29** po `success` ověřit `merged_at` — **✅ provedeno jako A1** · **S30** chybějící řádek v D1 u `done:true` **založit** a hlásit | **A1 hotové** |
| **C** | **C2** `test-eskalace.py` (opsaný `watchdog()`) · **C3** test `agent.yml` · **C4** `spec.json` chráněný · **C5** offline testy tří bran | částečně |
| **C + nové** | **S29 v CI**: auto-merge při `ok=0` skončit nenulově — **✅ provedeno jako A3** | ne |
| **D** | **D2** drift z `git ls-files` · **D3** onboarding jako test · **D4** `game_id` a absolutní cesty · **D5** `prepisy.json` + `forge.config.json` | **ANO — O5, O6, O9** |

### 2.6 Nálezy z předchozích session, POŘÁD otevřené

- **Tři mrtvé brány** (N11): **LGTM** — 272 položek, všech 272
  `schvalil: agent-init`, razítka v **jedné minutě**; role `worker`/`judge`,
  kterou `vision.mjs` nečte; verdikt visionu má jen `continue-on-error`.
  Navíc `acceptance` a `provides` nečte žádný kód.
- **`orchestra` je největší nájemník workspace** (N5): 73,4 % bytů, 60,4 % souborů.
- **`grep` tool vrátil 0 absolutních cest, Python walk našel 80 v 59 souborech**
  (N6) — past v obou skillech.
- **`verify-setup.py:11-12` vyžaduje 9 sourozeneckých složek** (N8) — dnes
  `VSE OK`, ale po separaci by hlásil 6× CHYBI.

### 2.7 Deferred (vědomě odloženo)

- **Bootstrap objektů ve hře** — `main.json` má 4 markery, hra kreslí dvě
  postavy a minci. Kdo je vytváří, **není dohledané**.
- **`sprites.json`** v repu hry je zastaralý template (16 barev, „green slime").
- **`--resolution 480x270` v `ci.yml`** je zavádějící (nemá vliv) — naměřeno:
  dva běhy daly **bit po bitu stejné framy**; *neškodné, ale matoucí*.
- **Krok `blender:` v `worker.mjs`** a mrtvý default `FORGE_CMD` (míří na
  neexistující `forge.cmd`) — čeká na rozhodnutí o uzlu `pc-domaci`.
- **Ruční fitness funkce zůstávají ruční** — `read_image` a kontaktní arch
  jsou jediné dvě věci, které orchestra **nemá** umět sama. Musí zůstat vidět.

### 2.8 Mimo tuhle práci (a proč sem nepatří)

| Téma | Kde je | Proč to sem nepatří |
|---|---|---|
| **Náklady DSH** (11 opatření, −79 %) | `DEPLOY-VYLEPSENI.md` | Je o **tom, jak draze pracujeme**, ne o orchestra. Patří do **Creator session** |
| **Cizí pluginy na viditelnost** | `OTEVRENA-TEMATA.md` | Rozhodnutí **uživatele** („důvěřovat, nebo neinstalovat") |
| **`reasoningEffort` z `max`** | tamtéž | **Neprokázaná páka** — nejdřív měřit |
| **`ast-grep`** | tamtéž | Vyplatí se, až se bude dělat **v kódu** |

**Pravidlo:** když se tohle téma objeví, **zapiš ho do `OTEVRENA-TEMATA.md`
a jdi dál.**

---

### 2.9 Dva nové otevřené body z práce typu A (3. 10. 2026)

**Oba vznikly tím, že se práce na hře udělala pořádně** — a nejsou to vady
měřidel, jsou to **důsledky dodání kódu**. Zapsané proto, aby se na ně
nezapomnělo: každý z nich **blokuje** něco jiného.

#### A) `entity.player` závisí na `world.map`, která NIKDY hotová nebyla

**Naměřeno** (`_analyza\a3-roadmapa-over.py`, proti blobům v `origin/main`):

- `entity.player` má v `depends_on` **`world.map`** — a ta je od 3. 10. 2026
  **`done: false`**, protože její práce (`scripts/world.gd`, `gather()`,
  respawn) v `main` **nikdy nebyla** (`c651368` ho přesunul do `_retired/`).
- **Důsledek:** conductor `entity.player` **nevydá** — čeká na granuli, která
  hotová není.
- **A přitom lze vydat hned:** `entity.player.api` (granule, která stejnou práci
  dodává) čeká na `core.attributes`, `core.skills`, `entity.item`, `world.level`
  — **všechny čtyři jsou `done: true`**.

**Co rozhodnout:** má stará granule `entity.player` mít `world.map`
v závislostech dál? Práce, kterou dodává `entity.player.api`, `world.map`
**nepotřebuje** (bere `level.is_walkable_at`, tedy `world.level`).
**Je to ale zásah do DAG** — rozhodnout vědomě, ne mimochodem.

#### B) `persist.save.state` — kdo vlastní POZICI hráče

**Naměřeno** (nový stav vznikl prací typu A):

- `scripts/save.gd:52` ukládá pozici **podmíněně** `if hrac != null and
  "position" in hrac:` a `:84` ji stejně podmíněně načítá.
- **Do 3. 10. 2026 tenhle test nikdy neprošel** — hráč pozici neměl „viditelnou"
  tak, jak kód čekal. **Teď projde**, protože `player.gd` stav dostal.
- **Následek:** `load()` **přepíše spawn** pozicí ze souboru. To je změna
  chování ukládání, kterou nikdo nenaplánoval.

**Co rozhodnout:** vlastní pozici `player.gd` (a `save.gd` ji jen ukládá), nebo
se má hráč po načtení vracet na `level.spawn_cell`? **Patří to do smlouvy**
(`ARCHITEKTURA.md` §2.1), ne do kódu potichu.

### 2.10 Stav otevřených bodů po P19 (6. 10. 2026) — a co se OD TÉ DOBY ZAVŘELO

> **Proč to tu je:** oddíly **2.1–2.9** jsou **záznam** (nemažou se); tenhle
> odstavec je **stav k P19** a je **jediný, který se přepisuje**. Podrobný
> záznam je v **§37**, rozhodovací session.

| Co bylo otevřené | Stav po P19 |
|---|---|
| **Push orchestry (P17+P18)** z §36.12 | **VYŘEŠENO** — rozhodl uživatel, pushnuto **6 commitů** (`ce49234..19a2195`), ověřeno **třemi kroky** (§37.1) |
| **H93** (`snapshot-*/` v NA32) | **OPRAVENO** — snapshoty i pracovní kopie se vylučují a **vykazují vlastním čítačem** (§37.2) |
| **H94** (4 mrtvé podpisy v `g3`) | **ROZHODNUTO A OPRAVENO** — seznam zúžen na **4 živé**, odebrané **pojmenované** v komentáři (§37.3) |
| **`g3` jako brána** | **ROZHODNUTO** — `g3` **spadne jen za sebe** (nezačatá brána / brána bez čítače mimo deklarovaný stav), o **červených nerozhoduje**; **NA23b zůstává otevřený** (§37.4) |
| **Nová: H99 (BOM v `.py`)** | **ZAPSÁNO, nerozhodnuto** — věc konvence, dnes ho hlásí obě brány shodně (§37.6) |

### 2.11 Stav otevřených bodů po P20 (6. 10. 2026) — **TADY JE DNEŠNÍ STAV**

> **⚠ §2.10 VÝŠ JE ZÁZNAM K P19, NE STAV.** Dvě jeho položky (**`g3` jako brána**
> a **H99**) tam stojí jako **otevřené** — a **P20 je zavřela**. Nechávají se
> (historie se nepřepisuje), ale **kdo hledá dnešní stav, čte tuhle tabulku.**
> Podrobný záznam je v **§38**.

| Co bylo otevřené | Stav po P20 |
|---|---|
| **`g3` a červené brány (NA23b)** | **VYŘEŠENO** — `g3` **soudí i červené**: `OCEKAVANE_NENULOVE = {"zadání kontrola": 1}`; nedeklarovaný nenulový exit = `exit 1`, deklarovaný = projde, visutý záznam = `exit 1` (§38.1) |
| **BOM v `.py` (H99)** | **VYŘEŠENO — ZAKÁZÁN**, pravidlo v `AGENTS.md` (`.ps1` BOM **mít musí**, `.py` **nesmí**); obě brány se **nerozcházejí**, ověřeno fixturou v živém stromě (§38.2) |
| **Zařazení ověřovacích skriptů do `g3`** | **ROZHODNUTO** — **ani jeden** z 8 kandidátů tam nejde (dva nemají čítač, pět zapisuje do stromu); zůstávají **doklady** a hlídá je `_analyza/p20-d-doklady.py` (§38.4) |
| **Nové: H101 (tichá díra v H79)** | **OPRAVENO** — nečitelné `.py` se počítají a pojmenovávají; mrtvý `utf-8-sig` fallback odebraný (§38.3) |
| **Nové: H102 (doklad P18 tvrdil `>= 6` podpisů)** | **OPRAVENO** — `ov-d-klasifikator.py` **40/0** (§38.6) |
| **Nové: H103 (H92 sken = falešný poplach)** | **DOLOŽENO, NEopravováno** — `lint-roadmapa.py:30` je **premisa fallbacku**, nástroj funguje; **neopravovat** (§38.6) |
| **Push orchestry (P20)** | **NEPUSHNUTO** — P20 se **nepushovala** (push je rozhodnutí uživatele); hra **nedotčená** (`44dd454`) |

### 2.12 Stav otevřených bodů po DOKONČENÍ P20 (6. 10. 2026) — **TADY JE DNEŠNÍ STAV**

> **⚠ §2.11 VÝŠ JE ZÁZNAM K P20, NE STAV.** Jedna jeho položka (**push P20**)
> tam stojí jako nepushnutá — a **session P21 ji zavřela**. Nechává se
> (historie se nepřepisuje), ale **kdo hledá dnešní stav, čte tuhle tabulku.**
> Podrobný záznam je v **§39**.

| Co bylo otevřené | Stav po dokončení P20 (6. 10. 2026) |
|---|---|
| **Push orchestry (P20)** | **VYŘEŠENO** — P20 byla nejdřív **commitnuta** (`b2fd758`, 23 souborů, +2327/−296), pak **pushnuta** (`b781c84..b2fd758`); **živě ověřeno** `ls-remote` → `b2fd758`, `origin/main..HEAD` = **0**. Push **vyžádal uživatel** |
| **H104 (zadání P20 tvrdilo, že P20 je commitnutá)** | **VYŘEŠENO** — nález i doklad v **§39.1**; čísla a postup v **§39.4** |
| **H105 (nabídka H1 stojí na neplatném předpokladu)** | **OTEVŘENO** — `save.gd` se ve hře **nikdy nevolá** (jediný volající je test), takže „spawn přepíše pozici" **nenastává**. H1 je odteď **„zapojit persist do hry"**, ne „opravit spawn" |
| **Věcná práce (co dál)** | **NEVYBRÁNA** — uživatel zvolil **orchestra + conductor**; nabídka a zadání jsou v **`NEXT-SESSION-INSTRUKCE.md`** |
| **Hra (`uo-shadows`)** | **ZÁMĚRNĚ POZASTAVENA** (rozhodnutí uživatele: chystá **přepis architektury zadání hry**) → nabídky **H1/H2 nejsou na řadě**. Hra je `44dd454`, **nedotčená** a v sync s `origin/main` |
| **Brány po commitu P20** | naměřeno **§39.7**: `g3` → **37 bran, 1 nenulový** (`zadání kontrola` = **DEKLAROVANÝ**, protože po commitu hlásí „přibylo commitů"), `exit 0`; `validate-all` → **`✓ VŠE V POŘÁDKU`** |
| **H103** | **neopravovat** — `ov-g-h92-sken.py` je **doložený falešný poplach** (`tools/lint-roadmapa.py:30` je premisa fallbacku) |

## 3. Nové nálezy N1–N9 — kde jsou a co z nich plyne

**Autorita:** `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` (každý nález má
spustitelný důkaz, cenu, riziko a „co NEDĚLAT").

**Tři nejdůležitější věty:**

1. **N1 + N8 jsou táž vada ve dvou vrstvách:** nástroj (inventář) i dokument
   (analýza) **si nesou starý stav a nikdo to neporovnává s realitou.**
   To je přesně téma, které analyzovalo druhé kolo — a **projevilo se na jeho
   vlastních výstupech.**
2. **N3 je nová třída selhání:** kontrola projde, ale **v každé kopii z jiného
   důvodu.** Dosud se hledaly brány, které *neumí selhat*; tahle **umí
   selhat — jen ne na tom, na čem si myslíš.**
3. **N7 je vlastní omyl, který našel jen druhý pohled** (ne test, protože ta
   vlastnost nebyla měřená). Zapsaný proto, že **komentář tvrdící chování je
   tvrzení, které se ověřuje.**

---

## 3b. Jazyk v kódu — měření a poučení (bývalá §10, práce session `7db45275`)

**Provedeno** (Z1–Z8), ale **měření a poučení se nemažou** — jsou to
nejcennější části, protože se na nich staví příště.

**Naměřeno** (`_analyza\hl-neanglicky-v-kodu.py`): **161 souborů, 2 002 nálezů,
0 nepokrytých.** Třídí nálezy podle **kontextu v AST**, ne podle dojmu.
**Verdikt: dokumentace je v pořádku, riziko bylo v 10 místech kódu.**

| Vrstva | Naměřeno | Verdikt |
|---|---|---|
| Názvy souborů a cest | 113 souborů, non-ASCII v názvu **0** | bez rizika |
| Sloupce D1 (`schema.sql`) | 5 tabulek, **40 sloupců**, českých **0** | serverová vrstva čistá |
| Klíče CI | `task_id`, `run_key`, `FORGE_*` — ASCII | bez rizika |
| Diakritika v `.md` orchestra | 2 533 z 44 781 znaků = **5,7 %** | zbytek je ASCII kód |
| **Čeština jako IDENTIFIKÁTOR** | **10 míst** (11 po zahrnutí patche) | **riziko → opraveno** |

**Ze 172 „rizikových" nálezů klasifikátoru bylo 12 skutečných:** 30 jsou známé
falešné poplachy fallbacků a **130 jsou hlášky a texty promptů**, které
klasifikátor nazval „klíč objektu", ale ve zdroji to **nejsou jména**.

**Poučení, které stálo pět kol oprav (a platí obecně):** **kde je po ruce
skutečný nástroj, nemá se psát vlastní.** Ruční lexer selhal **čtyřikrát
za sebou**; parser TypeScriptu napoprvé. A **scanner TypeScriptu nestačí** —
na vadném souboru se rozsype, kdežto **parser se vzpamatuje**. Páté kolo bylo
v **klasifikaci**: kdyby se rizika nechala na „klíč objektu", bylo by jich 172
a skutečný nález by se v šumu ztratil.

**Nástroje (zůstávají, jsou použitelné dál):**

| Soubor | Co měří |
|---|---|
| `_analyza\hl-neanglicky-v-kodu.py` | úplný inventář neanglických textů; čte **AST/parser**, ne regex |
| `_analyza\js-tokeny.mjs` | analyzátor JS/TS přes **parser TypeScriptu** |
| `_analyza\test-neanglicky-skener.py` | **mutační test skeneru** (23 kontrol) |
| `_analyza\hl-rizika-jazyka.py` | **finální seznam rizik** + kontrola úplnosti |
| `_analyza\_inventar.json` | **pozor: MEZIPRODUKT, ne měření** — viz nález **N1** |

**Co se ZÁMĚRNĚ nepřejmenovává:** `games/uo-shadows/assets/spec.json` →
`styl.zmenšování` — je to **lidský popis**, 0 čtenářů v kódu.
**A české hlášky, komentáře a dokumentace** — brány je **hledají** (§4 plánu).

---

## 4. Mapa zdrojů (který dokument je autorita pro co)

**Tohle je odpověď na „unifikuj zdroje" — každý soubor teď říká, čím je:**

| Soubor | Co to JE | Kdy ho číst |
|---|---|---|
| **`HANDOFF.md`** | **stav práce** (tenhle soubor) | **VŽDY první** |
| `AGENTS.md` | **trvalá pravidla** (závazná) | vždy druhé |
| `ANALYZA-HLOUBKOVA-2-ZADANI.md` | **zadání** — ✅ **splněné, neopakovat** | jen jako vzor zadání |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` | **SNAPSHOT k 05:45 UTC** (S31–S37) | jako historické měření; **ne jako dnešní stav** |
| `_analyza\HLOUBKOVA-MERENI-3.md` | **surová čísla** k tomu snapshotu | když se analýza a podklady rozejdou, **platí podklady** |
| `ANALYZA-HLOUBKOVA-ORCHESTRA.md` | 1. kolo (S1–S30) | jako historii |
| `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` | **záznam o provedení A1–A4** | co a proč se změnilo |
| `IMPLEMENTACE-HRANICE-JAZYKA.md` | **záznam o provedení Z1–Z8** | co a proč se změnilo |
| `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` | **N1–N9, plán (neprovedený)** | **odkud pokračovat** |
| `OTEVRENA-TEMATA.md` | **ledger** všech otevřených témat | při zakládání nového tématu |
| `PLAN-ROZVOJ-ORCHESTRA.md` | **plán fází A–D** (autorita pro O3/O10) | před fází B |
| `SOUBEH-SESSION-NALEZY.md` | co proklouzlo souběhem session | při souběhu |
| `MOZNOSTI-AGENTA.md` | co agent umí (měřené) | než tvrdíš, že něco nejde |

**Pravidlo, které z toho plyne:** **analytický dokument má v hlavičce DATUM
SPOTŘEBY a co z něj bylo provedeno.** Bez toho se za dvě hodiny čte jako
popis dneška (N8).

---

## 5. Running state (měřeno touto session)

- **Repozitáře:** `orchestra` → `HEAD 3a2e691`, **10 změněných souborů**,
  `origin/main..HEAD = 1`. `games\uo-shadows` → `HEAD d0bf4f9`,
  **6 změněných souborů**, `origin/main..HEAD = 1`.
  **Nic není commitnuté ani pushnuté.**
- **Conductor:** měřen dřív touto session — `ok: true`, `ready: 2`,
  `running: 0`, `games: 1`; `/failed` = 1 úloha (task #141 `entity.enemy`).
  ⚠ **Po A1–A4 se chování mění**, ale **dokud se nenasadí, běží stará verze**
  (deploy je z gitu). **Tohle je důvod, proč se A1–A4 zatím neprojeví.**
- **D1 `/roadmap`:** 14 řádků, 11 `done` (z toho 3 bez práce v `main`).
- **Domácí uzly:** `oracle-frankfurt` žije; `pc-domaci` ~57,6 h offline.
- **Dev servery / porty:** žádné. Conductor běží na Cloudflare.
- **Background procesy:** **žádné.**

---

## 6. Jak ověřit, že to funguje (spustitelné)

Z `C:\Users\Ssevc\Local-Deepseek`, s `$env:PYTHONIOENCODING='utf-8'`:

| Příkaz | Očekáváno |
|---|---|
| `python _analyza\a1-a2-over.py` | **23 kontrol**, `exit 0` (bylo 19 — brána vyrostla) |
| `python _analyza\a3-over.py` | `exit 0`, **6× `exit 1`** v obou kopiích |
| `python _analyza\n8-zastarala-analyza.py` | **5 zastaralých ze 7** (2 kontrolní vzorky aktuální) |
| `python _analyza\hl-rizika-jazyka.py` | **0 očekávaných, 11 přejednaných, 0 vrácených** |
| `python _analyza\hl2-kontrola.py` | **9/9 bodů** zadání 2. kola |
| `python _analyza\hl2-mutace-kontrola.py` | **6/6 mutací** |
| `python _analyza\test-neanglicky-skener.py` | **23 kontrol, 0 chyb** |
| `python orchestra\tools\kontrola-diakritiky.py` | **VŠE OK** |
| `python orchestra\tools\over-dokumentaci.py` | **63 kontrol, 0 chyb** |
| `python orchestra\tools\over-skilly.py` | **12 skillů, 0 chyb** |
| `python orchestra\tools\lint-roadmapa.py games\uo-shadows` | 10× `[5]`, **13 z 18 bez `size_lines`**, `exit 0` |
| `node orchestra\tools\kontrola-driftu.mjs` | ⚠️ **`exit 1`, 1 rozdíl — ZNÁMÝ** (tři kroky) |

**Mutační testy (jediný důkaz, že brány měří):**
`a1-a2-over.py` (3 mutace), `n8-zastarala-analyza.py` (kontrolní vzorky),
`hl-rizika-jazyka.py` (vrácení `ohlášeno` → `exit 1`), `a3-over.py`
(odstranění `exit 1` → `exit 1`), `sjednot-sablonu.py` (odstranění
`FORGE_ATTEMPT` → `exit 1`).

---

## 7. PICK UP HERE

### 7.1 Co je hotové a **nezačínej znovu**

- **A1–A4** (ukotvení stavu) — provedeno, ověřeno, **nepushnuto**.
- **Z1–Z8** (hranice jazyka) — provedeno, ověřeno, **nepushnuto**.
- **Druhé kolo hloubkové analýzy** — hotové (9/9).
- **Krok 1 zadání uživatele** — ✅ **byl splněn**; tahle session to jen ověřila.

### 7.2 ⚠ VÝZVA K OVĚŘENÍ MÉ PRÁCE (toto je hlavní úkol nové session)

> ## ✅ SPLNĚNO 2. 10. 2026 — **neplň to znovu**
>
> **Všech 12 bodů má výsledek: 12× prošlo, 0 vyvráceno.** Naměřeno spuštěním,
> u každého je příkaz a výstup: **`HANDOFF.md` §7.5**. Při tom ověření se našly
> **tři slepá místa v měřidlech** (nálezy **V1/V2/V3**, §7.6) — **kód obou repů
> je přitom správný**.
>
> **Tabulka níž je historické zadání** (co se ověřovalo) — **čti ji jako
> záznam, ne jako úkol.** Bod **8** v ní už neplatí (PR jsou sloučené, viz §10).

**Tuhle session napsal analytik, který zároveň opravoval kód.** Podle
`hlouchkova-analyza` §1 to **není nezávislý pohled** — a proto **nesmíš
věřit §1 výš**. Každé tvrzení v něm **má spustitelný důkaz**, a tvůj úkol je
**zkusit je vyvrátit**:

| # | Co ověřit | Jak | Co je nález |
|---|---|---|---|
| **1** | **A1 opravdu rozhoduje podle `merged`** | vlož do `index.ts` zpět `if (ok)` (jen `ok`, bez `merged`) a spusť `a1-a2-over.py` | když test **nespadne**, je slepý |
| **2** | **A2 rozlišuje `null` (nevím) od prázdného stromu** | změň `stromMain !== null && owns.length > 0` na `owns.length > 0` | test musí spadnout |
| **3** | **A3 je v OBOU kopiích, ne jen v jedné** | smaž `exit 1` v **herní** kopii `agent.yml` a spusť `a3-over.py` | musí hlásit chybu **ve hře** |
| **4** | **Z4/Z7 mají shodné hashe** | `Get-FileHash` na obou dvojicích | **531AE859…** a **FE639998…** |
| **5** | **Analýza je opravdu zastaralá v 5 tvrzeních** | přečti 5 tvrzení z `n8-zastarala-analyza.py` a **ověř je v kódu sám** | kdyby bylo zastaralých víc/míň, je nález o **mém** měření |
| **6** | **N1 je pravda** (inventář se sám negeneruje) | přegeneruj inventář, změň soubor, spusť `hl-rizika-jazyka.py` **bez** regenerace | musí hlásit vady, které nejsou |
| **7** | **N3 je pravda** (jiný krok v herním repu) | `python _analyza\z8-probe.py` | musí ukázat **dva různé kroky** |
| **8** | ~~**Tři visící PR jsou pořád nesloučené**~~ | ~~`node _analyza\hl2-s29-s30.mjs`~~ | ⚠ **ZASTARALÉ — ověřeno 2. 10. 2026 v 10:4x UTC: všechny tři jsou SLOUČENÉ** (#30 v 07:40, #29/#28 v 07:56, #31 v 08:02; otevřených PR je **0 z 31**). **Neznovej je slučovat.** Podrobně §10 |
| **9** | **Nic není pushnuté** | `git rev-list --count origin/main..HEAD` v obou repech | **1** v každém |
| **10** | **Brány nejsou slepé** | spusť **všechny** z §6 a u **každé** ověř, že soubor **vůbec otevřela** | past S27 — zelená nad neotevřeným souborem není zelená |

**Když najdeš rozpor, je to výsledek — ne tvoje chyba.** Dvě session přede mnou
měly **osm** vlastních omylů a většinu našel až **mutační test nebo kontrola
úplnosti**. **Počítej, že i moje čísla budou někde mimo.** Do §8 doplň svůj
omyl, až na nějaký přijdeš — je to nejsilnější důkaz, že se měřilo.

### 7.3 Co má nová session udělat

1. **Ověřit §7.2** (10 bodů) a **napsat, co neprošlo**.
2. **Projít N1–N9** z `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` a **rozhodnout,
   co se opraví** — nebo to předat jako zadání.
3. **Rozhodnout O3** (sáhnout na conductora?) — **A1–A4 jsou hotové**, takže
   je to samostatné rozhodnutí. **Nasadit znamená pushnout.**
4. **Rozhodnout tři visící PR** (#28/#29/#30) — ručně sloučit, nebo doplnit
   `size_lines`.
5. **Před commitem i pushem ukázat `git status` a `git diff --stat`.**

### 7.4 Jak dovolat session (změřeno 2. 10. 2026)

| Cesta | Funguje? | Proč |
|---|---|---|
| **`send_message` toolem** | ❌ | umí **jen podagenty** této session; jiná session je **sourozenec** |
| **`dsh` z příkazové řádky** | ❌ | shim míří na **neexistující** `bin.js` (je uvnitř `app.asar`) |
| **Přepnout v GUI** | ✅ | každá session je **samostatná konverzace** |
| **Nový chat + tenhle handoff** | ✅ **doporučeno** | je psaný přesně pro tohle |

**Rozlišení session:** `node _analyza\dsh-session-prehled.mjs`
(bez něj se session rozlišují jen podle názvu složky, což **nejde**).

**Tři pasti při čtení session logů** (naměřené): soubor je **multi-frame zstd**
(1,3 MB = 997 rámců; `zstdDecompressSync` vrátí **jen první** a tvrdí úspěch);
složka **není** session ID (je o prefix kratší); hloubka `0` = session,
`1` = podagent. Nástroj: `_analyza\hl2-rozbal-session2.mjs`.

---

### 7.5 ✅ VÝSLEDEK OVĚŘENÍ §7.2 (provedeno 2. 10. 2026, nová session)

**Ověřeno spuštěním, ne čtením.** Všech **12 bodů** (prompt jich čísluje 12,
handoff 10 — tabulka níž je proti promptu) má výsledek. **Nic nebylo
vyvráceno jako nepravdivé** — ale **tři brány jsou slabší, než jejich zelená
tvrdí**, a to je nález.

| # | Co ověřit | Výsledek | Čím |
|---|---|---|---|
| 1 | A1 rozhoduje podle `merged` | ✅ **prošlo** | `a1-a2-mutace.py`: 5 mutací, jádro chyceno |
| 2 | A2 rozlišuje `null` od prázdna | ✅ **prošlo** | tamtéž — ale viz nález **V2** |
| 3 | A3 je v OBOU kopiích | ✅ **prošlo** | `a3-mutace.py`: vada v herní kopii → `exit 1` |
| 4 | Z4/Z7 mají shodné hashe | ✅ **prošlo na puntík** | `531AE859F670…` a `FE639998F30A…`, obě 24222/17296 B |
| 5 | Analýza je zastaralá v 5 tvrzeních | ✅ **prošlo** | `b5-over-tvrzeni.py` — 5/5 nezávisle na `n8-*` |
| 6 | N1 — inventář se sám negeneruje | ✅ **prošlo (potvrzeno)** | `n1-over-inventar.py` |
| 7 | N3 — jiný krok v herním repu | ✅ **prošlo** | `z8-probe.py`: „Spusť agenta" vs. „Vyber bezplatného poskytovatele LLM" |
| 8 | Tři PR jsou nesloučené | ✅ **prošlo** | `hl2-s29-s30.mjs`: otevřené 3, `mergeable_state=clean` |
| 9 | Nic není pushnuté | ✅ **prošlo** | `rev-list --count origin/main..HEAD` = **1** v obou repech |
| 10 | Brány nejsou slepé (S27) | ✅ **prošlo** | všechny brány §6 + ověřeno, že soubory otevřely |
| 11 | Čísla v `AGENTS.md` sedí | ✅ **prošlo** | **5 v pořádku, 2 historická, 0 rozchodů** |
| 12 | Ten nástroj sám měří správně | ✅ **prošlo** | `ag-mutace.py`: vada 39→32 spadne; přeformulování → „NENAŠLA SE TVRZENÍ" |

**Bod 9 — čas:** ověřeno 2. 10. 2026 ~09:5x UTC; `orchestra` `3a2e691`
(10 změněných), `games\uo-shadows` `d0bf4f9` (6 změněných). **Stav se od
handoffu nezměnil.**

**Bod 10 — co brány skutečně otevřely** (to je ta část, kterou „exit 0" netvrdí):
`over-dokumentaci` → **63 kontrol**; `over-skilly` → **12 skillů**;
`kontrola-diakritiky` → **35 souborů** (oba nové dokumenty 2. kola **v seznamu
jsou**); `kontrola-driftu` → **12 souborů, 1 známý rozdíl** (tři kroky);
`hl-rizika-jazyka` → **0 očekávaných, 11 přejednaných, 0 vrácených**.

---

### 7.6 ⚠ TŘI NÁLEZY O BRANÁCH — **VŠECHNY TŘI OPRAVENY 2. 10. 2026**

> **Stav:** V1, V2 i V3 jsou **opravené a mutačně ověřené** (viz §9 a §13).
> Text níž je **popis vady v době nálezu** — nechává se jako důkaz, že se měřilo.
> „Jak to bylo špatně" je stejně cenné jako oprava: kdo tu vadu pochopí, pozná
> ji i v jiném nástroji.

Všechny tři mají stejný tvar jako **S27**: zelená, která **vypadá jako měření**.
Kód obou repů je přitom **správný** — hashe všech mutovaných souborů jsou před
i po shodné. **Vady jsou v měřidlech.**

| # | Nález | Naměřeno | Nástroj |
|---|---|---|---|
| **V1** | **`hl2-kontrola.py` měří PŘÍTOMNOST řetězců, ne obsah.** Z analýzy se udělala „kostra" — nadpisy, markery a devět řádků `\| **Cena** \| X \|` (12,5 % textu) — a brána hlásila **9/9, `exit 0`** | **9/9 nad 12,5 % dokumentu** | `_analyza\hl2-kostra-test.py`, `hl2-kostra-kalibrace.py` |
| **V2** | **`a1-a2-over.py` je slepý ke 3 z 5 mutací:** (a) přejmenovaná konstanta TTL, (b) TTL se **přestal používat** (`expiruje: ted + 999999999`), (c) `awaiting_human` přejmenovaný v zápisu do D1. Jádro A1/A2 **chytá správně** | **chyceno 2 z 5** | `_analyza\a1-a2-mutace.py` |
| **V3** | **`n8-zastarala-analyza.py` hledá řetězce, ne funkci:** (a) přejmenovaný stav v D1 → tvrzení 4 se tváří zastarale, i když v kódu je; (b) přejmenovaná **jen definice** `filesInOriginMain` (volání zůstalo = **kód je rozbitý**) → skript to **nevidí** | **2 slepá místa ze 3 testovaných** | `_analyza\n8-mutace.py` |

**Proč na tom záleží:** `hl2-kontrola.py` je **jediný důkaz**, že zadání 2. kola
bylo splněno (9/9). Kdyby někdo smazal 88 % analýzy a nechal nadpisy, zůstane
zelená. **V1 to neruší** — analýza obsah má a 9/9 platí — ale **ta zelená
neznamená to, co se zdá.** *(Po opravě V1 to znamená: „9/9" je 10/10 a měří
i obsah.)*

**N9 — pokrytí `ag-over-cisla.py`:** v `AGENTS.md` je **80 řádků s číslem**,
z toho **16 s jednotkou** (tedy tvrzení o stavu). Nástroj kontroluje **5 + 2
historická**. Zbytek **není kontrolován** — částečný nástroj budí dojem
úplnosti (přesně to píše prompt v Kroku 2).

---

### 7.7 Co se ověřit NEDALO (přiznaná mez)

- **Rubrika `hl2-kontrola.py` proti SMRTI obsahu:** V1 měří „kolik toho brána
  zkontroluje", ne „jak kvalitní analýza je". **Kvalitu analýzy tenhle test
  nezměřil** — jen to, že brána ji neměří.
- **Bod 4 (hashe) — jen proti dokumentu:** `531AE859…`/`FE639998…` jsou
  v `IMPLEMENTACE-HRANICE-JAZYKA.md` a shodují se. **Nezávisle proti GitHubu
  ověřeno nebylo** (vyžadovalo by push, který je zakázaný bez vyžádání).
- **Tři PR:** ověřeno přes GitHub API, že jsou otevřené. **Jejich budoucnost
  (sloučit / doplnit `size_lines`) je rozhodnutí člověka** — neověřitelné.
- **`--resolution 480x270` v `ci.yml`** (handoff §2.7): neověřováno znovu,
  vyžadovalo by dva běhy Godotu.

---

### 7.8 Nástroje vzniklé tímhle ověřením (v `_analyza\`, mimo CI)

| Soubor | Co dokazuje |
|---|---|
| `a1-a2-mutace.py` | 5 mutací proti živému `index.ts` (nález V2) |
| `a3-mutace.py` | mutace v **herní** kopii `agent.yml` (bod 3) |
| `n8-mutace.py` | 3 mutace + 2 slepá místa `n8-*` (nález V3) |
| `b5-over-tvrzeni.py` | 5 tvrzení ověřených **nezávisle** na `n8-*` (bod 5) |
| `n1-over-inventar.py` | **N1 potvrzen**: nástroj hlásí vadu, která na disku není |
| `ag-mutace.py` | vada 39→32 + přeformulování (bod 12) + pokrytí (N9) |
| `hl2-kostra-test.py`, `hl2-kostra-kalibrace.py` | **V1**: 9/9 nad 12,5 % dokumentu |

**Žádný z nich není v `validate-all.mjs` ani v CI** — je to týž stav, před
kterým varuje prompt (Krok 2). Rozhodnutí, které tam patří, je na člověku.

---

## 8 — Vlastní omyly: ⚠ PŘESUNUTO (7. 10. 2026)

> **⚠ NADPIS JE ZÁMĚRNĚ BEZ TEČKY ZA `8`** (`## 8 —`, ne `## 8.`). Důvod je
> naměřený: `_analyza\kronika-kontrola.py` hledá nadpisy bloků omylů vzorem
> `^#{2,3}\s+8[a-z]{0,2}\.\s` a **ukazatel** by se mu počítal jako další blok
> `8` — čímž by v součtu vznikla **kolize klíčů** (naměřeno 7. 10. 2026:
> „do součtu se dostalo 27 z 28 bloků"). Ukazatel není blok omylů.

**Tabulky omylů (bloky `8a`–`8zz`) žijí od 7. 10. 2026 v `_archiv\HANDOFF-OMYLY.md`.**
Důvod: tenhle soubor měl **674 723 znaků** a **93,8 % z toho byla historie** —
stav se v něm hledal špatně. **Nic se nezmazalo:** text je v archivu **bajt na
bajt** a ověřují to `_analyza\handoff-kontrola-uplnost.py` (83 klíčů, hledá
v `HANDOFF.md` **i** v archivech) a `_analyza\kronika-kontrola.py` (počty omylů
proti kronice §3 čte z archivu). **Nový omyl se zapisuje do archivu** —
`_analyza\p22-zapis-zaznamu.py` tam blok vkládá i ověřuje (spuštěno 7. 10. 2026:
**37 kontrol, 0 chyb**; soubor i archiv zůstaly beze změny = idempotentní).

## 9. Co už otevřené NENÍ

- ~~F0.1–F0.6~~ → hotové a pushnuté.
- ~~Zámek `owns`~~ → opraven (`6d2a856`), nasazen, regresní test 8/8.
- ~~`main` hry červený~~ → zelený.
- ~~„Nic není pushnuto"~~ → vyvráceno.
- ~~Analýza architektury~~ → hotová + §8 dodatek se S17/S18.
- ~~Zadání Z1–Z7~~ → hotové (Z8/Z9 zůstávají).
- ~~**Fáze A (A1, A2, A3)**~~ → hotová a ověřená spuštěním.
- ~~**`NAZEV-REPA`**~~ → opraveno a commitnuto (`3a2e691`).
- ~~**`test-cooldown.py` lže zelenou**~~ → opraveno.
- ~~**„PR se sloučily samy"**~~ → vyvráceno detailem PR (`merged_by` = člověk).
- ~~**Hloubková analýza (1. kolo)**~~ → hotová.
- ~~**Druhé kolo hloubkové analýzy**~~ → hotové 2. 10. 2026 (S31–S37, 9/9 bodů).
- ~~**A1–A4 (ukotvení stavu)**~~ → **provedeno 2. 10. 2026** (tahle session).
- ~~**Z1–Z8 (hranice jazyka)**~~ → **provedeno 2. 10. 2026** (tahle session).
- ~~**N5, N7**~~ → opraveno v této session.
- ~~**„Nová dokumentace není v bráně diakritiky"**~~ → doplněno
  (i `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md`).
- ~~**„Krok 1 zadání nebyl splněn"**~~ → **byl**; tahle session to ověřila
  (byl to **omyl č. 5**).
- ~~**Výzva k ověření §7.2**~~ → **splněna 2. 10. 2026** (12/12 bodů,
  `HANDOFF.md` §7.5). **Nic se nevyvrátilo** — všechny brány zelené.
- ~~**`ANALYZA-HLOUBKOVA-2-ZADANI.md` — je opravdu splněné?**~~ → **je**;
  ověřeno nezávisle (bod 5, `b5-over-tvrzeni.py`) a **nezávisle na té bráně**.
- ~~**V1** — `hl2-kontrola.py` nevidí obsah~~ → **OPRAVENO 2. 10. 2026**:
  přidán **10. bod** (obsahová kritéria: každá ze 12 sekcí musí mít ≥ 4 řádky
  a ≥ 200 znaků). Ověřeno **třemi** způsoby: dokument projde **10/10**; obě
  kostry (11,7 % i 12,5 % textu) **spadnou**; dokument se smazanou sekcí
  „Co je dobré" **spadne**. „9/9" je teď tvrzením **o obsahu**.
- ~~**V2** — `a1-a2-over.py` chytí 2 z 5 mutací~~ → **OPRAVENO**: brána má
  **23 kontrol** (bylo 19) — TTL konstanta se musí **skutečně použít**, cache
  nesmí jít do nevypršitelného času, chybový zápis musí mít krátký TTL a stav
  `awaiting_human` musí být **zapsaný v D1**. Mutačně **4 ze 4**.
- ~~**V3** — `n8-zastarala-analyza.py` má 2 slepá místa~~ → **OPRAVENO**: ptá se
  na **zapsaný stav** (prochází všech 17 zápisů do `tasks`, ne první) a na
  **funkci** (deklarace **i** volání). Mutačně **3 ze 3**, a test porovnává
  **množinu** zasažených tvrzení, ne jen jejich počet.

**A co zůstává otevřené (rozhodnutí člověka):**

- **Zařazení nástrojů do CI:** **žádný z 8 nových nástrojů** (`_analyza\*mutace*.py`,
  `b5-over-tvrzeni.py`, `n1-over-inventar.py`, `hl2-kostra-*.py`) **není
  ve `validate-all.mjs` ani v CI.** Které tam patří, je na člověku.
- **N1, N3, N4, N6, N8, N9** — viz `NEXT-SESSION-INSTRUKCE.md` §2 (Úkol A5).
- **A rozhodnutí (Krok 2 promptu):** **žádný z 8 nových nástrojů není
  ve `validate-all.mjs` ani v CI.** Které tam patří, je na člověku.

---

## 10.–39. Záznamy session 2.–6. 10. 2026 — ⚠ PŘESUNUTO (7. 10. 2026)

**Záznamy §10–§39 (jednotlivé session, ověřování a opravy) žijí od 7. 10. 2026
v `_archiv\HANDOFF-HISTORIE.md`.** Bylo to **84 % souboru** a žádný z nich nebyl
stav — příběh projektu je v `KRONIKA-PROJEKTU.md`. **Nic se nezmazalo** (text je
v archivu bajt na bajt; ověřuje `_analyza\handoff-kontrola-uplnost.py`, která
hledá v `HANDOFF.md` **i** v archivech).

**Kde je dnešní stav:** §0–§7 a §9 tady, nejnovější záznamy §40–§54 níž,
historie v `KRONIKA-PROJEKTU.md` a v `_archiv\`.

## 40. P22 — OPTIMALIZACE ZNALOSTNÍ BÁZE (6. 10. 2026, mimo zadání) — a DODATEČNÝ ZÁPIS ZÁZNAMŮ

**Co tenhle oddíl JE:** **záznam o provedení** session **P22** — a zároveň
**záznam o tom, že se P22 nevešla do záznamů** a dopisuje se dodatečně.
**Nejde z něj číst dnešní stav** — ten je v **§2.12** (a novější body níž).
**Datum spotřeby:** údaje jsou k **6. 10. 2026, 15:0x–17:5x +02:00
(= 13:0x–15:5x UTC)**; co je starší, je **záznam**.

**Zadání:** `NEXT-SESSION-INSTRUKCE.md` z P21 žádalo **věcnou práci na
conductoru** (C1/C2/O1). **Uživatel to změnil** a zadal **optimalizaci
znalostní báze** (`OPTIMALIZACE-KNOWLEDGE-BASE.md` + `REVIZE-PRACOVNIHO-RITUALU.md`).
**Kód conductora se nedotkl ANI JEDEN soubor** — `deploy.yml` má filtr
`paths: conductor/**`, takže **žádné nasazení živé služby se nekonalo**
(ověřeno seznamem změněných souborů, ne odhadem).

### 40.1 Co je hotové (doloženo spuštěním)

| Co | Naměřeno | Kde je důkaz |
|---|---|---|
| **Mrtvé cesty v KB** | **45 → 23 → 7** (16 opraveno) | `_tools\over-cesty-v-kb.mjs` (nový nástroj; odlišuje **historickou zmínku** od **vady**) |
| **Brána na PRAVDIVOST KB** | `over-skilly.py` **13/0, 0 mrtvých cest**; mutant → **`exit 1`**, zdravý stav → **`exit 0`** | `tools\over-skilly.py` — do P22 se na cesty **neptal** a byl zelený nad **23 neexistujícími** |
| **`.py` NESMÍ BOM** | pravidlo v `DSH_HOME\AGENTS.md`; rozpočet řetězce **38 867 / 65 536 B** | `over-dokumentaci.py` **67/0**; dřív to bylo **jen** v projektovém `AGENTS.md`, kde se to čte **opačně** |
| **Pojistka proti zápisu** | `p20-d-doklady.py` vypíše **15 zápisových skriptů** a hlídá hash **3 dokumentů**; mutant → **`⚠ ZMĚNĚN: KRONIKA-PROJEKTU.md`** | dávka dřív **spouštěla zapisovače do kroniky** bez kontroly (riziko auditu nástrojů) |
| **Tři živě vyvrácená tvrzení** | `README.md` (cesty `E:\DSH*`), `DEPLOY-VYLEPSENI.md` (opatření **8 a 9 JSOU nasazená**), komentář ve `validate-all.mjs` | ověřeno v `package.json` profilu, ne dojmem |
| **`_mutace.py` + sabotážní test** | `p22-test-mutace.py` **19/0**; sabotáž (vypnutá kontrola v knihovně) → **`CHYBA`, `exit 1`** | test **mutuje živou bránu** `tools\over-skilly.py`, spustí ji a ověří, že **verdikt se změnil** (ne jen text) |
| **`g3` bere cesty z prostředí** | `FORGE_STANICE` / `FORGE_HRA` s **týmiž defaulty**; bez override **stejný běh** (`g3` 37 bran, `exit 0`; self-testy `h71` 15/0, `h87` 18/0) | vzor override **už v repu byl** (`FORGE_GODOT`, `verify-setup.py`) — `g3` ho jen nepoužíval |
| **Rejstřík a tiché díry** | `POUCENI-A-VZORY.md` (64,7 kB, **0 odkazů ve 622 `.md`**) zaregistrován; prázdný `NEXT-SESSION-INSTRUKCE.md` v kořeni stanice → **tombstone** | obojí přidáno do kontroly diakritiky a **mutačně ověřeno**, že je vidí |

### 40.2 ⚠ NÁLEZ P22-B: AUDIT PŘECENIL DUPLICITY VE TŘECH ZE TŘÍ PŘÍPADŮ

Návrh `OPTIMALIZACE-KNOWLEDGE-BASE.md` chtěl **zkrátit** tři místa s odůvodněním
„duplikuje jinde“ (dohromady ~27 kB). **Přeměřeno plošným skenem a ani jeden
případ neobstál:**

| Bod | Co audit tvrdil | Co naměřeno |
|---|---|---|
| **§6.8** `orchestra` skill | blok o branách hry duplikuje `uo-shadows/AGENTS.md` | **8 z 9** vzorů je **JEN ve skillu**; hra má **2**, orchestra `AGENTS.md` **0**, `HANDOFF` **1** |
| **§6.6** `overovani` §7 | §7.1–7.14 duplikuje `dsh-prostredi` a `DSH_HOME` | **9 ze 14** pastí je **JEN v `overovani`** |
| **§6.5** `DSH_HOME` §„Jak ověřovat“ | 7,6 kB → 2,2 kB, příklady patří do `overovani` | **15 z 18** klíčových frází je **JEN v `DSH_HOME`** |

**Proč se to stalo:** audit porovnával **TÉMATA** („obě místa mluví
o ověřování“), ne **OBSAH**. **Důsledek: ty tři body se NESMÍ dělat jako
„zkrácení“** — jen jako **PŘESUN s ověřením, že každá věta zůstala dohledatelná**
(zadání: `ZADANI-OPTIMALIZACE-KB.md`).

### 40.3 Proč tenhle oddíl vzniká DODATEČNĚ (a co to znamená)

**Naměřeno 6. 10. 2026 při dopisování:** `HANDOFF.md` **0 výskytů „P22“**,
`KRONIKA-PROJEKTU.md` **0 výskytů „P22“**, poslední blok omylů `8z` (P20),
poslední řádek session **35**. **Práce byla pushnutá, záznam žádný.**

Zapsáno dodatečně: **řádek 36** v kronice §1, sekce **2.16**, blok omylů **`8za`**
(omyly **211–213**, všechny tři ze **zápisu**, doložené v hlavičce
`REVIZE-PRACOVNIHO-RITUALU.md`) a **tenhle oddíl**. Nic se nepřepisovalo.

> **⚠ POUČENÍ, KTERÉ JE DRAŽŠÍ NEŽ TEN ZÁZNAM:** **brány kontrolují jen to, co je
> ZAPSANÉ.** `kronika-kontrola.py` i `handoff-kontrola-uplnost.py` byly po celou
> dobu P22 **zelené** (`SEDÍ`, `83/83`) — a přitom v obou dokumentech **chyběla
> celá session**. Chybějící záznam **není rozchod**, který by brána viděla:
> je to **ticho**. Kdo chce tuhle třídu chytit, musí se ptát **naopak** („má
> každý pushnutý commit svůj záznam?“), jako to dělá `s24-meridla-over.py`
> u bloků omylů.

### 40.4 Co zůstává OTEVŘENÉ (po P22)

* **Zbývající body KB** — `§6.4` (projektová znalost z `orchestra` skillu do
  projektu), `§6.11` (**569 tis. znaků historie** z `HANDOFF.md`; dnes 20. oddíl
  navíc), `§6.5`/`§6.6`/`§6.8` (jen jako **PŘESUN**), `§6.14` (jedna autorita
  seznamu živých), `§6.15` (zobecnění měřidel) — zadání je
  `ZADANI-OPTIMALIZACE-KB.md`.
* **Revíze rituálu** — zavedeny **jen** body 2 a 7 (`_mutace.py`,
  `_tools\rozpad-session.mjs`); **1, 3, 4, 5, 6 čekají na rozhodnutí**, protože
  mění **postup předávání** nebo **trvalá pravidla** (`REVIZE-PRACOVNIHO-RITUALU.md` §5).
* **`otevrena-temata`** — **7 nezaškrtnutých položek leží v sekci „Uzavřené“**
  (sekce tvrdí jedno, značky druhé) a **dvě témata jsou prokazatelně vyřešená**,
  jen neuzavřená; to je **drobnost, ale je to táž vada** jako §2.10–§2.12.
* **Údržba měřidel** — `g3` **37 bran, 1 deklarovaný nenulový** (`zadání
  kontrola`), `validate-all` **`✓ VŠE V POŘÁDKU`**; `ov-g-h92-sken.py` zůstává
  **červený jako doložený falešný poplach** (H103 — **neopravovat**).

## 41. SCHVÁLENÉ PRÁCE 6. 10. 2026 (P23k) — REVIZE RITUÁLU, DROBNOSTI A JEDNA AUTORITA REGISTRU

**Co tenhle oddíl JE:** **záznam o provedení** session, která dělala
**schválené** (ne navržené) práce: uživatel 6. 10. 2026 rozhodl
**„omyly nepiš, zbytek KB souhlasím, body revize rituálu schvaluji, drobnosti
rozhodni sám“**.
**Nejde z něj číst dnešní stav** — ten je v **§2.12** a v kronice.

### 41.1 Revize rituálu — body 1, 3, 5, 6 SCHVÁLENY A APLIKOVÁNY

Aplikováno do **`C:\Users\Ssevc\Local-Deepseek\PREDAVANI-SESSION.md`**
(není to soubor v repu — je to **postup předávání**, společný celé stanici):

| Bod | Co se změnilo | Kde to je |
|---|---|---|
| **1** | **Subagent jako nezávislý ověřovatel** (místo celé nové session) — s **povinným ověřením vzorku** jeho tvrzení | §2.4 |
| **3** | **`SOUHRN:` s pojmenovanými čítači**, třetí stav **`NEZMĚŘENO`** a **velikost okna** měření; mutace jednou funkcí | §2.5 |
| **5** | **Granule i pro práci session** (vlastní ověření, delegovatelnost) | §2.6 |
| **6** | **`goal` pro cíle přesahující session** | §2.7 |

**Checklist §7** má čtyři nové **povinné** položky (subagent → vzorek, `SOUHRN:`
+ `NEZMĚŘENO`, granule samostatně, `goal` pro dlouhý cíl). **Body 2 a 7** byly
hotové už dřív (`_analyza/_mutace.py`, `_tools/rozpad-session.mjs`), **bod 4**
je částečný (programové zápisy — dnes obstály `p22-zapis-zaznamu.py` i
`p22c-bunka-kroniky.py`).

### 41.2 Drobnosti — rozhodnuto a provedeno (měřením, ne dojmem)

| # | Rozhodnutí | Doklad |
|---|---|---|
| **1** | **`ag-over-cisla.py` PATŘÍ do `validate-all.mjs`** (ne ručně) — čte tvrzení **z `AGENTS.md`** a porovnává se ZDROJEM. ⚠ **Jeho mez je v popisu kontroly**: pokrývá **5 měřených čísel**, zbytek **NEhlídá** — kdo do `AGENTS.md` přidá číslo, přidá i kontrolu | `node tools\validate-all.mjs` → `✓ VŠE V POŘÁDKU`; kontrola `trvalá pravidla: čísla v AGENTS.md proti ZDROJI` → `exit=0` |
| **2** | **`lint-roadmapa.py` u `[5]` zůstává `exit 0` — a je to ROZHODNUTÍ, ne opomenutí.** Naměřeno: `[5]` hlásí **13 z 16** položek, protože `done: true` je v roadmapě **nespolehlivé** (H105). Blokující by padalo na **13 místech, která jsou v pořádku**. Nově je proto **oddělené**: `Nalezeno problémů: 3` (blokující) + **`PORADNÍ (neblokující, 13)`**, a souhrn vypisuje obojí. **Blokujícím se smí stát, až `done` pochází z reálného stavu** (A1: `ok && merged`) | `python tools\lint-roadmapa.py` → `ZMĚŘENO: 22 granulí zkontrolováno, 3 problémů (+13 poradních)`, `exit 0` |
| **3** | **Chybějící buňka v kronice** (blok `1–13`, sloupec „nálezů o cizím kódu“): hodnota se **NEDOMÝŠLÍ** → `neurčeno` + vysvětlení pod tabulkou. Souhrn `54` zůstává **citovaný** (historická čísla se nepřepisují), ale už není bez vysvětlení | `python _analyza\p22c-bunka-kroniky.py` → **11/0**; `kronika-kontrola.py` → `KRONIKA SEDÍ` |
| **3b** | **Nástroj `_tools\over-souhrn-kroniky.mjs` měl DVĚ vady čtení** a obě vypadaly jako nález o datech: (a) vzor bloku bral **jedno** písmeno → přeskakoval `8za` (součet **192** místo **208**); (b) buňka `—` se četla jako nevyplněná, ale po rozhodnutí je v ní **`neurčeno`** → `NaN` a **řádek by tiše zmizel**. Obě opraveny a **mutačně ověřeny** | `node _tools\test-over-souhrn-kroniky.mjs` → **7/0** (zdravý stav 27 bloků `208 = 208`; M1 uber `8za` → 205 vs 208; M2 zpět `—`; M3 rozbitý souhrn) |

### 41.3 §6.14 — JEDNA AUTORITA SEZNAMU ŽIVÝCH (registr generuje `g3`)

**Do 6. 10. 2026 existovaly tři seznamy a ani jeden se neshodoval s během:**
`_analyza\_registr-bran.json` (ruční, `"kdy": "2026-10-02 22:06"`, s **předpřesunovou**
cestou `C:\Users\Ssevc\Local-Deepseek\orchestra`), ruční výčet v `HANDOFF.md` §6
a devět nástrojů v `AGENTS.md` (tři nikde neběžely).

**Náprava:** `g3` — který brány **skutečně spouští** — **zapisuje registr sám**.
Registr tím přestal být **tvrzení** a je **výstup běhu**: 37 bran s `exit`,
čítačem, příkazem a seznamy deklarovaných výjimek. `AGENTS.md` to uvádí jako
**jedinou autoritu** a říká, že se **needituje rukou**.

**⚠ Dvě věci, které k tomu patří (a jsou naměřené):**
* Registr se **nezapisuje v režimu `--soubor`** (`_POUZE_VYSTUP`) — v něm si
  doklady a mutační testy **mění `BRANY`**, takže by se uložil **zmrzačený
  seznam z mutace**.
* **Co se nezměnilo:** inventář se musí přegenerovat **po každé editaci kódu**,
  ne po každém běhu `g3` — ověřeno: otisk vstupů je **před i po** běhu `g3`
  shodný (`125d8fa1…`), protože registr je z otisku **vyloučený** (`_analyza\_[^/]*\.json`).

### 41.4 Co zůstává OTEVŘENÉ (a proč to není lenost, ale postup)

Uživatel **schválil** i zbytek KB, ale ty čtyři body **nejdou udělat bezpečně
v jedné session s autorem** — `AGENTS.md` a `PREDAVANI-SESSION.md` §2.2:
**navrhne jedna session, ověří druhá**, a „nic nesmí zmizet“ se **dokazuje
hledáním**, ne pamětí autora. Zadání je hotové: `ZADANI-OPTIMALIZACE-KB.md`.

| Bod | Co je to | Proč vlastní session |
|---|---|---|
| **§6.4 + §6.8** | **přesun projektové znalosti z `orchestra` skillu do hry** (~11,6 kB, **jeden a týž blok textu**) | mění **18 textů**, které z toho skillu **vyžaduje `over-dokumentaci.py`** — přesun bez úpravy brány ji shodí |
| **§6.5 + §6.6** | **PŘESUN** (ne zkrácení!) `DSH_HOME` §„Jak ověřovat“ a `overovani` §7 | dotýká se **trvalých pravidel**; auditovy důvody „duplikuje jinde“ byly **vyvráceny ve 3 ze 3 případů** |
| **§6.11** | **přesun historie z `HANDOFF.md`** (569 tis. znaků z 656 kB) | je to **přepis stavu**: `kronika-kontrola.py` **čte omyly z §8**, takže přesun §8 znamená **upravit i bránu** |
| **§6.9** | nepravdivé číslo „**27 podmíněných kontrol**“ (`game-developer` + `AGENTS.md` hry) | naměřeno dnes: **`has_method` na 23 řádcích** → patří k §6.8 (přesun do hry) |

---

## 42. N0.3 — STAV CÍLE V `/health` (6. 10. 2026, pokračování práce na conductoru)

**Co tenhle oddíl JE:** **záznam o provedení** — co se udělalo, čím je to doložené
a co ještě **NENÍ** hotové (nasazení). **Nejde z něj číst dnešní stav** — ten je
v `§2.x` a v kronice.

### 42.1 Proč přišlo na řadu zrovna tohle (živé měření, ne plán)

Předání `PREDANI-ORCHESTRA-SESSION.md` nechalo na výběr **C1** (B2–B5) / **C2**
(N0.3) / **O1** (rozhodnutí). Zvoleno **C2 = N0.3**, protože táž třída (**S18**)
se 6. 10. 2026 naměřila **ZNOVU a živě**:

| Co | Hodnota (6. 10. 2026, 19:39–21:26 UTC) | Odkud |
|---|---|---|
| `/health` | `ok: true`, `ready: 1`, `running: 0`, `games: 1` | `GET /health` |
| běhy `agent.yml` | **9 v řadě `failure`** (poslední 19:36:01Z); poslední úspěch = PR #37 (5. 10. 02:04) | GitHub API (`jobs` + anotace check-runů) |
| selhaný krok | vždy **první tvrdá brána na výstup agenta** — `Kontrola parsování` 6×, `Testy hry` 3× | `jobs` API |
| soubory granulí | `scripts/npc.gd` a `scripts/enemy.gd` v `main` **NEJSOU** (nikdy nebyly) | raw 404 + `commits?path=` → `[]` |
| `/failed` | **1 úloha** (#229 `entity.enemy`, 5 běhů) | `GET /failed` |
| `/queue` | 50 úloh, z toho **49× „NPC — obchodník“** (48× `blocked`, `attempts=0` — nikdy se nespustily) | `GET /queue` |
| `/roadmap` | `entity.npc` = #234 `ready` (att=3), `entity.enemy` = #229 `failed` (att=5), zbytek `done` | `GET /roadmap` |

→ **Conductor hlásil `ok: true` přes 22 hodin, ve kterých nevzniklo nic.** Přesně
tomu má N0.3 zabránit: „zelený conductor nad mrtvým cílem“ musí být vidět na
jednom místě.

### 42.2 Co je hotové (kód + brána + mutační důkaz)

| Co | Kde | Doklad |
|---|---|---|
| `/health` nově nese `targets[]`: `main_ci`, `forge.ok`, `forge.selhani_v_rade`, `error` + cache (2 min; 30 s po chybě) | `conductor/src/index.ts` | `tsc --noEmit` → **exit 0** |
| nová brána: nechá conductora **zbundlovat** (`wrangler deploy --dry-run`, bez sítě a bez přihlášení) a zavolá **skutečný** `/health` s falešnou D1 a stubovaným GitHubem | `tools/test-health-cile.mjs` | **21 kontrol, 0 chyb**, `exit 0` |
| **mutační důkaz** brány (5 vrat: `selhani_v_rade`=0, `forge.ok`=true, bez `targets`, cache bez TTL, cíl z `GITHUB_REPO`) | `_analyza/n03-mutace.py` | **11 kontrol, 0 chyb** — 5× brána **spadla**, soubor vždy vrácen **bajt na bajt** |
| registrace bran | `_analyza/g3-brany.py` (`BRANY`), `tools/validate-all.mjs`, `tools/kontrola-diakritiky.py` | `g3`: **39 bran** (bylo 37), registr přegenerován |

**Rozhodnutí v designu (a proč):** `ok` zůstává „**služba žije**“ (hlídá ho
monitoring dostupnosti) — stav cíle je **oddělený** v `targets`, aby se
„dostupnost“ a „cíl maká“ nedaly splést. `forge.ok` je `null`, když žádný běh
neskončil — „**nezměřeno**“ se nesmí číst jako „v pořádku“. Když GitHub neodpoví,
je to vidět (`error` + `null`), ne ticho.

### 42.3 Brány: co je zelené a co je červené SCHVÁLNĚ

* `kontrola-diakritiky.py` → `VŠE OK` (otevřeno 246 z 290, 0 chyb) · `over-dokumentaci.py` → **67/0** · `over-skilly.py` → **13 skillů / 0 chyb**, 40 zmínek o nástrojích, **0 mrtvých cest**.
* `g3-brany.py` → **39 bran**, nenulový exit **2**: `zadání kontrola` (**deklarovaný** — kotva vs. nový HEAD) a `validate-all` (**nečekaný**).
* `validate-all.mjs` → **1 problém**: `E. lokální kód = repo` (**78 631 B vs 74 492 B**). To je „**změna ještě není v gitu**“ — porovnává se lokální `conductor/src/index.ts` s verzí **na GitHubu**; zavře se **až schváleným pushem**. Ostatní sekce (A–D, F…) zelené.

### 42.4 Nové nálezy (k dočíslování — čísla H přiděluje až nezávislé ověření)

| # | Nález | Doklad |
|---|---|---|
| **1** | **`C2: mutace N1` běží a je zelená, ale NEVYPISUJE ČÍTAČ** → registr neví, **co** změřila (`g3` to hlásí jako „běžela, ale vzor nic nenašel“, 3303 B) | `python _analyza/c2-mutace.py` → `VÝSLEDEK: brána měří — zastaralý i nezměřený inventář SHODÍ nástroj` (žádné „N kontrol, M chyb“) |
| **2** | **Fronta je zahlcená osiřelými duplikáty**: 49 úloh na jednu granuli, `attempts=0`, `blocked` — podklad pro **B3** (strop a watchdog na `item_id`) | `GET /queue` (6. 10. 21:2x UTC) |
| **3** | **Past prostředí (stanice):** kořen workspace ztratil právo **měnit vlastníka** → DSH nemohlo provisionovat zápis a **každý příkaz** spadl na `SetNamedSecurityInfoW failed (Win32 5): grantWrite(E:\Workspaces\forge-orchestra)` — vypadá to jako vada nástroje, je to stav oprávnění | opraveno skriptem skillu `diagnose-windows-sandbox-acl`; `before {writeDac:true, writeOwner:false}` → `after {…, writeOwner:true}`; rollback v `E:\Workspaces\_acl-oprava-20261006\` |

### 42.5 Co NENÍ hotové (nečti to jako hotové)

* **NENASAZENO.** Push do `conductor/**` = nasazení **živé služby** → rozhodnutí
  uživatele. Do té doby platí: `E. lokální kód = repo` je červená **schválně**
  a **živé** `/health` `targets` ještě **nemá** (naměřeno 21:26 UTC).
* **Kronika a plán** (řádek do `KRONIKA-PROJEKTU.md`, přepis N0.3
  v `PLAN-ORCHESTRA-AI-AGENTI.md` na HOTOVO) patří **až po nasazení** — a s důkazem
  z živé služby, ne z tohoto textu.
* **B3** (strop a watchdog na `item_id`) — podklad změřený (42.1 a 42.4/2), práce nezačatá.

---

## 43. B3a — WATCHDOG NA GRANULI (6. 10. 2026, pokračování práce na conductoru)

**Co tenhle oddíl JE:** **záznam o provedení** (druhý krok téhož pokračování jako
§42). **Nejde z něj číst dnešní stav** — ten je v `§2.x` a v kronice.

### 43.1 Živé měření vady (ne z dokumentu)

| Co | Hodnota (6. 10. 2026, 21:2x UTC) | Odkud |
|---|---|---|
| `entity.npc` — spálené běhy | **8** napříč **DVĚMA** úkoly (#228: 5, #234: 3) | `GET /queue` (součet `attempts`) |
| `entity.enemy` — spálené běhy | **5** (#229) | `GET /queue` + `GET /failed` |
| `payload.eskalovano` | **není ani u jedné** → watchdog **nikdy** neohlásil | `GET /failed` (klíče payloadu) |
| úloh na jednu granuli ve frontě | **49×** „NPC — obchodník“ (48× `blocked`, `attempts=0`) | `GET /queue` |
| prah vs. strop | `ESCALATE_AFTER=8` **>** `MAX_ATTEMPTS=5` → **nedosažitelný stav** | `wrangler.toml` |

**Proč to bylo slepé:** `escalateStuckTasks` počítal `COUNT(runs) WHERE r.task_id = t.id`
— tedy běhy **JEDNOHO úkolu** — a značku „už ohlášeno“ si nesl v `payload.eskalovano`.
Retry ale zakládá **nový úkol s `attempts=0`**, takže prah 8 se na jednom úkolu
nemohl naplnit (strop je 5) a značka by se při dalším pokusu ztratila.

### 43.2 Co je hotové

| Co | Kde | Doklad |
|---|---|---|
| počítadlo **na granuli** přes všechny její úkoly; klíč `{game}/{grain}` se skládá na **jednom místě** | `conductor/src/index.ts` | test **A**: 5+3 = **8**; starý dotaz na jeden úkol vidí max 5 (známý chybný případ) |
| okno `runs.started_at >= roadmap.created_at` → **`roadmap-reset` je cesta zpět** | tamtéž | test **B**: po resetu se počítá 1, ne 5 |
| prah z `ESCALATE_AFTER`, výchozí **3** (pod stropem 5) | `index.ts` + `wrangler.toml` | test **F** (kód i konfigurace) |
| značka v **`roadmap.eskalovano`** (+ sloupec v `schema.sql` a samomigrace) | `index.ts`, `schema.sql` | test **D** (žádný spam) a **G** |
| rozhodnutí jako **čistá funkce** `shouldEscalate` — test ji VOLÁ, neopisuje | `index.ts` | test **E** (5 případů: 2/3/8/0/undefined) |
| brána čte SQL, prah i rozhodnutí **ze zdrojáku** | `tools/test-watchdog-granule.py` | **17 kontrol, 0 chyb** |
| **mutační důkaz** (5 vrat: počítadlo úkolů místo běhů · vypuštěný časový filtr · vypuštěná značka · `shouldEscalate` vždy `true` · prah nad stropem) | `_analyza/b3-mutace.py` | **11 kontrol, 0 chyb** — 5× brána **spadla**, soubor vždy vrácen bajt na bajt |
| registrace bran | `_analyza/g3-brany.py`, `tools/validate-all.mjs`, `tools/kontrola-diakritiky.py` | `g3`: **41 bran** (bylo 39) |
| starý test označen | `tools/test-eskalace.py` | hlavička **⚠ ZASTARALÉ** — měří odstraněnou logiku; smazat/přepsat patří do **C2** (drží ho 20+ odkazů) |

### 43.3 Co se cestou rozbilo — a bylo to VIDĚT (to je pointa)

* **`ag-over-cisla.py` shodilo sama sebe:** do `schema.sql` přibyl sloupec, takže
  D1 má **41 sloupců**, ale `AGENTS.md` tvrdilo **40**. Opraveno včetně data
  a důvodu (`+1 sloupec 6. 10. 2026 (B3a): roadmap.eskalovano`) — trvalá pravidla
  jsou taky měřidlo.
* **`ag-mutace.py` ohlásilo „mutace se neprovedla“:** jeho kotva byla `40 sloupců`
  natvrdo. Kotva aktualizována a **historie kotvy zapsána** (39→40 dne 2. 10.,
  40→41 dne 6. 10.) — jinak by se táž past opakovala potřetí.
* **Dvě vady v MÉM testu** (obě odhalené spuštěním, ne čtením): (a) nekonečná
  rekurze při nahrazování konstanty sama sebou → `RecursionError`; (b) špatný
  předpoklad, že prah filtruje SQL (filtruje ho rozhodnutí v JS) → přepsáno na
  volání skutečné funkce `shouldEscalate`.

### 43.4 Co NENÍ hotové (nečti to jako hotové)

* **NENASOZENO** — čeká na rozhodnutí uživatele; **dva kroky**: `N0.3` (§42) a `B3a` (tenhle oddíl).
* **B3b = strop na granuli** (zastavit vydávání po `MAX_ATTEMPTS` spálených běhech)
  — záměrně **druhý krok** (plán: „nasadit po částech“). B3a jen **hlásí**, nezastavuje.
* **Kronika a plán** (řádek do `KRONIKA-PROJEKTU.md`, přepis B3/N0.3 v plánech na HOTOVO)
  patří **až po nasazení** a s důkazem z živé služby.

### 43.5 Brány (stav po B3a)

* zelené: `kontrola-diakritiky` (otevřeno 248 z 292, 0 chyb) · `over-dokumentaci` **67/0** ·
  `over-skilly` **13/0** (40 zmínek o nástrojích, **0 mrtvých cest**) · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` **5 v pořádku / 0 rozešlých** · `ag-mutace` **2/2 chyceno**.
* `g3` → **41 bran**, nenulové exity **2**: `zadání kontrola` (**deklarovaný**) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` (**81 445 B vs 74 492 B**) = nepushnutá změna.
* známá výjimka beze změny: `C2: mutace N1` běží zeleně, ale **nevypisuje čítač** (nález 42.4/1).

---

## 44. B5 UZAVŘENO + B2 ZMĚŘENO (6. 10. 2026, třetí krok pokračování na conductoru)

**Co tenhle oddíl JE:** **záznam o provedení**. Nejde z něj číst dnešní stav —
ten je v `§2.x` a v kronice.

### 44.1 B5 — nepravdivé komentáře: UZAVŘENO

Plán žádal: `grep -n "mrtvý kód" conductor/src/index.ts` → **0**. Naměřeno:
**0 výskytů** (předtím 2: `Env` a `escalateStuckTasks`, oba tvrdily, že
`MAX_ATTEMPTS` je v provozu nežívá konstanta — naměřeno nepravda).

⚠ **A jedna past, která se při tom ukázala:** první verze mého komentáře tu
nepravdu **citovala** — a tím držela zakázaný řetězec v souboru, takže by
přijímací `grep` **nikdy nezezelel**. Musel jsem ji přeformulovat. Je to táž
past, kterou projekt zná od `test-zamek-owns.py` („kontrola, která hledá
řetězec v celém souboru, ho najde i v komentáři, který vadu popisuje").

### 44.2 B2 — `/report` a cooldown: vada je OPRAVENÁ, ale NEBYLA MĚŘENÁ

**Stav vady:** `/report` dřív zapsal jen `tasks`, ne `roadmap` → selhaná granule
se vrátila do fronty **okamžitě** a spálila všechny pokusy za čtvrt hodiny
(naměřeno 30. 9. 2026: `#128` měl 5 pokusů za 16 minut). **Opravil to B1**
(`roadmap.naposledy_selhalo`) — a `index.ts:1606–1617` to má i s komentářem.

**Co chybělo:** **žádná brána to neměřila.** `tools/test-cooldown.py` kryje
cestu **dispatche**, ne zápis z `/report` — takže kdyby někdo ten zápis smazal,
neozvalo by se nic.

| Co je nové | Kde | Doklad |
|---|---|---|
| brána: simuluje selhání přes `/report` a ptá se **skutečného** dispatch guardu (obě SQL se vytahují ze zdrojáku, `RETRY_HOURS` z `wrangler.toml`) | `tools/test-report-cooldown.py` | **8 kontrol, 0 chyb** |
| **mutační důkaz** (4 vrat: `/report` nezapíše `naposledy_selhalo` · guard porovnává opačně · `RETRY_HOURS=0` · poslední pokus nezapíše) | `_analyza/b2-mutace.py` | **9 kontrol, 0 chyb** — 4× brána **spadla**, soubor vždy vrácen bajt na bajt |
| registrace | `g3-brany.py`, `validate-all.mjs`, `kontrola-diakritiky.py` | `g3`: **43 bran** (bylo 41) |

**Co brána tvrdí (Hotovo znamená plánu):** po čerstvém selhání přes `/report`
guard úkol **nevydá**; po uplynutí `RETRY_HOURS` **vydá**; **známý chybný případ**
(bez zápisu `naposledy_selhalo`) ho vydá **okamžitě** — to je měřená vada S13.

### 44.3 Co NENÍ hotové

* **B4** (`listGames` fallback **nesmí dispatchovat**, invariant 18) — **nezačato**.
  Změřeno dřív: fallback sahá na `env.GITHUB_REPO`, takže vypnutí poslední hry
  orchestra nezastaví. Acceptance plánu: `POST /game/active {active:false}` →
  `/health` `games=0` a **žádný dispatch**. Je to **změna chování** (plán ji sám
  označuje jako zamýšlené „radši nemakat“) → patří do samostatného kroku.
* **NENASOZENO** — pořád platí: `N0.3` (§42), `B3a` (§43) a k tomu **B5** (komentář)
  čekají na rozhodnutí o pushi; `B2` je **jen test + registrace**, běhový kód nemění.
* **B3b** (strop, který vydávání zastaví) — druhý krok B3, čeká na nasazení B3a.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 44.4 Brány (stav po B2/B5)

* zelené: `kontrola-diakritiky` · `over-dokumentaci` · `over-skilly` (0 mrtvých cest) ·
  `handoff` **83/83** · `kronika` **SEDÍ** · `ag-over-cisla` **5/0** · `ag-mutace` **2/2**.
* `g3` → **43 bran**; nenulové exity: `zadání kontrola` (**deklarovaný**) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 45. B4 — BEZ AKTIVNÍ HRY SE NEDISPATCHUJE (6. 10. 2026, čtvrtý krok)

**Co tenhle oddíl JE:** **záznam o provedení**. Nejde z něj číst dnešní stav —
ten je v `§2.x` a v kronice.

### 45.1 Vada nejdřív ZMĚŘENÁ (brána byla před opravou červená)

`listGames` měl „zpětnou kompatibilitu“: když registr neměl **aktivní** hru,
vrátil `[{game_id: "default", repo: env.GITHUB_REPO}]`. Důsledek (invariant 18):
**vypnutí poslední registrované hry orchestra nezastavilo.**

Naměřeno bránou `tools/test-listgames.py` **PŘED opravou** → **7 kontrol, 3 CHYB**:

```
CHYBA B: vypnutá hra (SQL nic nevrátí) → PRÁZDNÝ seznam = žádný dispatch
      cekano: []   dáno: [{'game_id': 'default', 'repo': 'fallback/nesmi-se-pouzit', …}]
CHYBA B: fallback na env.GITHUB_REPO se NEPOUŽIL      cekano: False  dáno: True
CHYBA D: v KÓDU `listGames` není `env.GITHUB_REPO`    cekano: False  dáno: True
```

**A druhá polovina vady, kterou samotný `listGames` neřeší:** dispatch smyčka
čte úlohy z **D1** (`SELECT * FROM tasks WHERE status='ready' AND target='cloud'`),
takže i s prázdným registrem by hotové úlohy dál odcházely. Acceptance plánu zní
„`/health` `games=0` a **žádný dispatch**“ — proto jsou potřeba **oba** guardy.

### 45.2 Co je hotové

| Co | Kde | Doklad |
|---|---|---|
| `listGames` **bez fallbacku** — žádná aktivní hra = prázdný seznam + zpráva do logu | `conductor/src/index.ts` | brána **10 kontrol, 0 chyb** (před opravou 7/3) |
| `tick` si aktivní hry načte **z registru** a bez nich se **nedispatchuje** (guard na začátku dispatch smyčky) ani neběží `roadmapTick` | tamtéž | brána, kontroly **E** |
| tik to **řekne** ve své odpovědi (`| POZOR: žádná AKTIVNÍ hra → nedispatchuji (B4)`) | tamtéž | kód (ticho by bylo past) |
| brána: SQL běží ve **skutečném SQLite**, funkce se **volá** (Node `--experimental-strip-types`), guardy se čtou z **KÓDU bez komentářů** | `tools/test-listgames.py` | **10 kontrol, 0 chyb** |
| **mutační důkaz** (4 vrat: dispatch bez guardu · dotaz bez `active = 1` · starý fallback · `roadmapTick` i bez hry) | `_analyza/b4-mutace.py` | **9 kontrol, 0 chyb** — 4× brána **spadla**, soubor vždy vrácen bajt na bajt |
| registrace | `g3-brany.py`, `validate-all.mjs`, `kontrola-diakritiky.py` | `g3`: **45 bran** (bylo 43) |

**Pojistka, která se ověřovala taky:** `/tasks/cleanup` **nemaže**, když je
`platne` prázdné (`503 „žádná platná granule – roadmapy jsou prázdné, nemažu“`) —
takže prázdný registr tam nic nesmaže. Zkontrolováno čtením kódu **před** opravou.

### 45.3 Co NENÍ hotové

* **NENASOZENO**: `N0.3` (§42), `B3a` (§43) a nově **`B4`** čekají na rozhodnutí
  o pushi; `B5` (komentář) a `B2` (testy) běhový kód nemění.
  ⚠ **B4 je první změna, která MŮŽE orchestra zastavit** (zamýšleně — plán:
  „radši nemakat“), takže se nabízí nasadit ji **samostatně** a ověřit, že
  s vypnutou hrou tik opravdu nic nespustí.
* **B3b** (strop na granuli) — druhý krok B3.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 45.4 Brány (stav po B4)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **45 bran**; nenulové exity: `zadání kontrola` (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 46. B3b — STROP NA GRANULI (6. 10. 2026, pátý krok; poslední vada fáze B)

**Co tenhle oddíl JE:** **záznam o provedení**. Nejde z něj číst dnešní stav —
ten je v `§2.x` a v kronice.

### 46.1 Co to je a proč ZÁMĚRNĚ VYPNUTÉ

Watchdog (B3a) granuli jen **ohlásí** — nic nezastaví. Naměřeno na živé službě:
`entity.npc` spálil **8 běhů** napříč dvěma úkoly a ve frontě na to vzniklo
**49 osiřelých úloh** na tutéž granuli. Strop (B3b) je ta druhá polovina:
po `GRAIN_MAX_RUNS` spálených bězích se granule **přestane vydávat**
(`status='blocked'` + notifikace jednou).

**Proč je výchozí hodnota `"0"` (vypnuto):** plán žádá nasazovat **po částech**
a měřit před/po. Kdyby se strop zapnul naráz s watchdogem, **nebylo by z čeho
měřit, že watchdog opravdu hlásí** (dnešní granule už jsou nad prahem i nad
stropem). Proto: *deploy 1* = watchdog (hlásí), *deploy 2* = `GRAIN_MAX_RUNS = "5"`
(zastaví).

### 46.2 Co je hotové

| Co | Kde | Doklad |
|---|---|---|
| `grainCap` — strop z konfigurace; **nesmysl/záporné/`0` = vypnuto** („strop, který se nedá přečíst, nesmí tiše zastavit orchestra“) | `conductor/src/index.ts` | brána **22 kontrol, 0 chyb** |
| `grainCapped` — čisté rozhodnutí (test ho VOLÁ) | tamtéž | kontroly **A/B** |
| `grainKeyOf` — klíč granule `{game}/{grain}` z payloadu | tamtéž | kontrola **C** |
| **shoda obou tvarů klíče** (JS `grainKeyOf` × SQL `GRAIN_KEY_SQL`) | tamtéž | kontrola **C** — přesně to, co u invariantu 17 chybělo |
| strop je v **obou** cestách, kterými granule odchází: filtr `ready` v `roadmapTick` i dispatch smyčka | tamtéž | kontroly **D** |
| počítadlo se měří **jednou za tik** a jde do watchdogu, roadmapy i dispatche (jedno číslo pro všechny tři) | tamtéž | kontrola **D** |
| konfigurace `GRAIN_MAX_RUNS = "0"` s vysvětlením dvou kroků | `conductor/wrangler.toml` | kontrola **E** (test VYPÍŠE, že je strop vypnutý) |
| **mutační důkaz** (5 vrat) | `_analyza/b3b-mutace.py` | **11 kontrol, 0 chyb** — 5× brána **spadla**, soubor vždy vrácen bajt na bajt |
| registrace | `g3-brany.py`, `validate-all.mjs`, `kontrola-diakritiky.py` | `g3`: **47 bran** (bylo 45) |

### 46.3 Vlastní vada, kterou brána odhalila sama

První běh brány skončil **22 kontrol, 1 CHYBA** — a nebyl to conductor, ale
**můj regex**: hledal za `=>` otevírací závorku, kterou tam filtr `ready` nemá.
Brána to ohlásila jako **„nenašel jsem filtr `ready` — test je slepý“**, tedy
přesně tak, jak má: **nemlčela**. To je rozdíl proti bráně, která nad
nenalezeným vzorem projde zeleně (`overovani` §7.10).

### 46.4 Co NENÍ hotové

* **NENASOZENO**: `N0.3` (§42), `B3a` (§43), `B4` (§45) a nově **`B3b`** čekají na
  rozhodnutí o pushi. `B3b` je navíc **inertní**, dokud se nepřepne
  `GRAIN_MAX_RUNS` — takže prvním deployem se chování nemění.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.
* **Fáze B je tím hotová** (B1 ✅ · B2 ✅ · B3a ✅ · B3b ✅ čeká na zapnutí ·
  B4 ✅ · B5 ✅). Zbytek fází C a D zůstává na rozhodnutí (`O3`, `O10`, `O5–O8`).

### 46.5 Brány (stav po B3b)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **47 bran**; nenulové exity: `zadání kontrola` (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 47. ČÍTAČ BRÁNY `C2: mutace N1` (6. 10. 2026) — poslední „nevíme, co změřila“

**Co tenhle oddíl JE:** **záznam o provedení** drobnosti z §42.4/1. Nejde z něj
číst dnešní stav — ten je v `§2.x` a v kronice.

### 47.1 Vada a její náprava

`g3` u téhle brány **pořád** hlásil `běžela, ale vzor nic nenašel (3 303 B)`:
`_analyza/c2-mutace.py` sice měřil pět scénářů a správně padal, ale **nikdy
nevypsal čítač** (`N kontrol, M chyb`), takže registr bran **nevěděl, CO změřil**.

| Co | Doklad |
|---|---|
| skript vypisuje `SOUHRN: N kontrol, M chyb`; **počet se bere z toho, co proběhlo** (krok „smazaný inventář“ se umí přeskočit na oprávněních → správně 4, ne 5; natvrdo psaná pětka by lhala — vada S27) | `python _analyza\c2-mutace.py` → `SOUHRN: 5 kontrol, 0 chyb`, `exit 0` |
| **deklarovaná výjimka se ruší**: `OCEKAVANE_BEZ_CITACE = set()` (držet ji dál by znamenalo, že nová ztráta čítače u téže brány projde jako „deklarovaná“) | `_analyza/g3-brany.py` |
| registr to teď VÍ: `{"nazev":"C2: mutace N1 (5 běhů)","exit":0,"otevřela":"5 / 0","ma_citac":true}` | `_analyza/_registr-bran.json` |
| `g3` už varování nehlásí a sám řekl, že výjimka není potřeba | `BRÁNY BEZ ČÍTAČE mimo deklarovaný stav: 0` + `(poznámka: v OCEKAVANE_BEZ_CITACE už není potřeba: C2: mutace N1 (5 běhů) — brána teď čítač vykazuje)` |

### 47.2 Dvě pasti, které se přitom ukázaly

* **Editace brány zestarala inventář** — `c2-mutace.py` je vstupem jazykového
  skeneru, takže první běh po editaci spadl na `INVENTÁŘ JE ZASTARALÝ / NEZMĚNĚNÝ`
  ve scénáři 1. **To je správné chování** (ne vada brány ani nástroje): inventář
  se přegeneruje a běh je zelený. Projekt to zná a píše to v `AGENTS.md`
  („počítej s tím víckrát za session“).
* **Čítač nesmí být konstanta.** Krok 4 (smazaný inventář) se umí přeskočit
  v sandboxu; kdyby skript tiskl natvrdo „5“, hlásil by víc, než změřil.

### 47.3 Co NENÍ hotové

* **NENASOZENO** — beze změny: `N0.3` (§42), `B3a` (§43), `B4` (§45) a inertní
  `B3b` (§46) čekají na rozhodnutí o pushi. Tenhle oddíl běhový kód nemění.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 47.4 Brány (stav po §47)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **47 bran**, **0 bran bez čítače** (dřív 1); nenulové exity: `zadání
  kontrola` (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 48. TIK OFFLINE — první test ROZHODOVACÍ LOGIKY conductora (6. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení**. Nejde z něj číst dnešní stav —
ten je v `§2.x` a v kronice.

### 48.1 Proč

Projekt o sobě sám psal (skill `orchestra`, `README.md`): *„Conductor **nemá test
své rozhodovací logiky.** Dva `.py` testy logiku **opisují**, `mock-conductor.mjs`
neumí `/tick`, `/poll`, `/roadmap`… a `validate-all.mjs` se na `index.ts` dívá jen
**bajtovým porovnáním** — **když se v conductoru změní SQL, neozve se nic.**“*

Naměřeno 6. 10. 2026: i brána `B4` kontrolovala jen `listGames` a guardy
**staticky** — a „staticky to tam je“ **není** totéž jako „tik to neudělá“
(dispatch smyčka čte úlohy z D1).

### 48.2 Co je hotové

`tools/test-tick-offline.mjs` volá **skutečný `POST /tick`** nad conductorem
zbundlovaným přes `wrangler deploy --dry-run` (bez sítě a bez přihlášení),
s falešnou D1 a stubovaným GitHub API. Falešná D1 má **router podle SQL a na
NEZNÁMÝ dotaz SPADNE** — kdyby conductor začal dělat nový dotaz, test to řekne,
místo aby tiše měřil něco jiného.

| Kontrola | Co tvrdí | Doklad |
|---|---|---|
| **A** | registr bez AKTIVNÍ hry → tik **nedispatchuje**, hlásí „žádná aktivní hra“ i „roadmapu neřeším“ a roadmapu **ani nečte** | `spusteno: 0 úloh`, 0× `/dispatches`, 0× `/contents/` |
| **B** | s aktivní hrou a jednou připravenou granulí dispatchuje **právě jednou**, úlohu claimne a založí běh | 1× `/dispatches` na `agent.yml`, `taskClaimed=1`, `runy=1` |
| **C** | když UŽ jeden běh běží, `MAX_CONCURRENT=1` další dispatch **nepustí** | 0× `/dispatches` (a úloha přitom zůstává `ready`) |
| | **mutační důkaz** (3 vraty: dispatch bez guardu · `MAX_CONCURRENT` vypnutý · `roadmapTick` i bez hry) | `_analyza/tick-mutace.py` → **7 kontrol, 0 chyb**, 3× brána spadla |
| | registrace | `g3` → **49 bran** (bylo 47) |

⚠ **Dvě kontroly jsem musel ZPEVNIT, protože by prošly i s vratou vadou:**
kontrola C původně nastavila úlohu na `running`, takže by neprošla kvůli
*žádnému kandidátovi*, ne kvůli `MAX_CONCURRENT` — dnes je „běží jiný běh“
oddělený od stavu úlohy. A kontrola „roadmapa se ani nečetla“ neměla jak
selhat, protože bez aktivní hry by `roadmapTick` stejně nic neudělal; dnes se
měří i **zpráva o přeskočení** (ta je falsifikovatelná).

### 48.3 Co je tím ZASTARALÉ (a musí se opravit)

* Skill `~\.dsh\skills\orchestra\SKILL.md` a `README.md` **tvrdí, že conductor
  test rozhodovací logiky NEMÁ** — po tomhle oddílu to **není pravda**.
  Nechal jsem to zatím být (skill je mimo repo a `over-skilly.py` hlídá jeho
  cesty); **patří to opravit** — dokud to tam stojí, čte to každá session jako
  fakt a **nehledá**, co už existuje.

### 48.4 Co NENÍ hotové

* **NENASOZENO** — beze změny: `N0.3` (§42), `B3a` (§43), `B4` (§45) a inertní
  `B3b` (§46) čekají na rozhodnutí o pushi. Tenhle oddíl běhový kód nemění.
* Test pokrývá **čtyři** cesty tiku (hry, roadmapa, dispatch, `MAX_CONCURRENT`);
  **nepokrývá** `pollRuns` (výsledky běhů), stale-recovery a `/report` — to je
  materiál pro další kolo.
  > **⚠ OD 6. 10. 2026 TO UŽ NEPLATÍ pro `pollRuns` a stale-recovery — viz §49.**
  > Zůstává **`/report`** (endpoint má vlastní bránu `B2` na úrovni SQL, ale
  > **handler** `/report` zatím nezavolal žádný test).
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 48.5 Brány (stav po §48)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **49 bran**, **0 bez čítače**; nenulové exity: `zadání kontrola`
  (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 49. TIK OFFLINE — ROZŠÍŘENÍ NA `pollRuns` A STALE-RECOVERY (6. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** (pokračování §48). Nejde z něj
číst dnešní stav — ten je v `§2.x` a v kronice.

### 49.1 Proč zrovna tyhle cesty

**V `pollRuns` bydlely dvě z nejdražších vad projektu** a ani jedna neměla test,
který by **zavolal kód** — testy je jen opisovaly:

* **B1** — cooldown se ptal na `updated_at`, což je i čas VZNIKU řádku, takže se
  nová granule **3 h nevydala** (vada S12).
* **A1** — `done` se zapsalo i u PR, které se **NESLOUČILO**; naměřeno
  2. 10. 2026: tři granule byly `done`, jejich PR měly `merged_at: null`
  a soubory v `main` nebyly (S29/S31).

### 49.2 Co je nové

`tools/test-tick-offline.mjs` má **25 kontrol** (bylo 13) a kryje nově:

| Kontrola | Co tvrdí | Co by to chytilo |
|---|---|---|
| **D** | běh na GitHubu selhal → úloha zpět na `ready`, běh dostal výsledek a **`roadmap.naposledy_selhalo` se ZAPSAL** | regresi vady **B1** |
| **E** | běh uspěl **a PR je sloučený** → úloha i granule `done` | — |
| **F** | běh uspěl, **PR sloučený NENÍ** → `awaiting_human`, a `done` se **nezapíše** | regresi vady **A1** |
| **G** | zaseknutý běh → `timeout` a úloha zpět **jen dokud má pokusy** (`attempts < ?`), jinak `failed` | smyčku #107–#109 (30. 9. 2026) |
| **G2** | **bez** zaseknutých běhů se stav úloh nemění | „sahá to na úlohy, i když není co řešit“ |

Falešná D1 se rozšířila na **stavový model** a **zapisuje si provedené dotazy** —
tvrzení stojí na skutečném SQL, které tik poslal, ne na dojmu.

**Mutační důkaz je rozšířený na 6 vrat** (`_analyza/tick-mutace.py`, **13 kontrol,
0 chyb**), a to včetně **dvou historických regresí**:

* **M4** — `/poll` nezapíše `naposledy_selhalo` (vada B1) → brána spadne,
* **M5** — „úspěch = sloučeno“ (vada A1) → brána spadne.

To je poprvé, co má projekt **spustitelný důkaz**, že B1 a A1 by se po vrácení
poznaly — do 6. 10. 2026 je hlídaly jen testy, které si logiku opisovaly.

### 49.3 Co NENÍ hotové

* **`/report` handler** zatím nezavolal žádný test (brána `B2` měří jen SQL,
> které handler používá). Patří to do dalšího kola.
* **Skill `orchestra` a `README.md` pořád tvrdí, že conductor test rozhodovací
  logiky nemá** (§48.3) — neopraveno.
* **NENASOZENO** — beze změny: `N0.3` (§42), `B3a` (§43), `B4` (§45), inertní
  `B3b` (§46) čekají na rozhodnutí o pushi. Tenhle oddíl běhový kód nemění.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 49.4 Brány (stav po §49)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **49 bran** (počet se nezměnil — rozšířily se stávající brány),
  **0 bez čítače**; nenulové exity: `zadání kontrola` (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 50. `/report` V TESTU TIKU — poslední netestovaná rozhodovací cesta (6. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** (třetí díl testu z §48/§49).
Nejde z něj číst dnešní stav — ten je v `§2.x` a v kronice.

### 50.1 Co je nové

`tools/test-tick-offline.mjs` má **40 kontrol** (bylo 25) a volá **skutečný
`POST /report`** — endpoint, který dřív netestoval **nikdo** (brána `B2` měřila
jen SQL, které používá). Nové scénáře:

| Kontrola | Co tvrdí | Co by to chytilo |
|---|---|---|
| **H** | selhání s pokusy → úloha zpět na `ready`, **`naposledy_selhalo` se zapíše**, granule se **NEoznačí** `failed` | vadu **B1** na druhé cestě |
| **I** | poslední pokus → úloha i granule `failed` (+ čas selhání) | chybějící terminální stav |
| **J** | úspěch → úloha i granule `done` | — |
| **K** | neznámý `run_key` → **404 a žádné zápisy** | „zapíše, i když běh nezná“ |
| **L** | špatné tajemství → **401 a žádné zápisy** | nechráněný endpoint |
| **M** | `blocked`/`done` je **TERMINÁLNÍ** — report ho nevzkřísí | **invariant 10** (osiřelá úloha se po úklidu vrací a dispatchuje dokola) |

**Mutační důkaz je rozšířený na 8 vrat** (`_analyza/tick-mutace.py`, **17 kontrol,
0 chyb**): nově **M7** (`/report` nezapíše čas selhání = B1) a **M8** (`/report`
vzkřísí `blocked` úlohu = invariant 10).

### 50.2 Vlastní vada, kterou to odhalilo (a poučení)

**Počet vrat jsem měl v NÁZVU brány — a dvakrát zestaral** (3 → 6 → 8), protože
se test rozšiřoval. Je to táž vada, kterou projekt zná jako „ztráta čítače“ a
„různé čítače nesou stejné jméno“: **jméno, které tvrdí počet, je další místo,
kde vzniká nepravda.** Název je proto nově bez počtu (`tik offline: mutace brány`)
a skutečný počet hlásí test i registr `g3` — ty se měří, neopisují.

### 50.3 Co NENÍ hotové

* **Skill `orchestra` + `README.md` pořád tvrdí, že conductor test rozhodovací
  logiky nemá** (§48.3) — **neopraveno**; je to poslední známá lež o nástrojích.
* Test volá `/tick` a `/report`; **`/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`
  a `/roadmap/reset`** handlerem zatím neprochází žádný test.
* **NENASOZENO** — beze změny: `N0.3` (§42), `B3a` (§43), `B4` (§45), inertní
  `B3b` (§46) čekají na rozhodnutí o pushi. Tenhle oddíl běhový kód nemění.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 50.4 Brány (stav po §50)

* zelené: diakritika · `over-dokumentaci` · `over-skilly` · `handoff` **83/83** ·
  `kronika` **SEDÍ** · `ag-over-cisla` · `ag-mutace`.
* `g3` → **49 bran**, **0 bez čítače**; nenulové exity: `zadání kontrola`
  (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 51. DOKUMENTACE, KTERÁ POPÍRALA VLASTNÍ NÁSTROJE (6. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** — oprava skillu `orchestra`
a `README.md`. Nejde z něj číst dnešní stav — ten je v `§2.x` a v kronice.

### 51.1 Nejdřív MĚŘENÍ (a ukázalo, že dvě varování jsou nepravdivá)

| Co dokument tvrdil | Co naměřeno |
|---|---|
| `README.md` i skill: *„`test-cooldown.py` **nemá assert ani `sys.exit`** → končí vždy 0, SQL má **opsané**“* | **NEPRAVDA (6. 10. 2026):** soubor **má** `assert` i `sys.exit` (`:240`, `:242`) a SQL guardu **vytahuje ze zdrojáku** (`vytahni_guard_sql`, `:79`) → **10 kontrol, 0 chyb**, `exit 0` |
| skill: *„Conductor **nemá test své rozhodovací logiky** … když se v conductoru změní SQL, neozve se nic“* | **NEPRAVDA od §48–§50:** `tools\test-tick-offline.mjs` volá skutečný `/tick` i `/report` (**40 kontrol**) a má **8 vrat** v `_analyza\tick-mutace.py` |
| skill, Klíčové cesty: `orchestra/conductor/`, `orchestra/repo/`, `orchestra/tools/`… | **24 odkazů na layout, který na disku NENÍ** — `orchestra\tools` → `False`, `tools` → `True` (repo se 4. 10. 2026 přesunul na `E:`) |
| skill: `test-eskalace.py` = „offline test watchdogu“ | **měří odstraněnou logiku** (prah natvrdo 8, počítání po úkolech) — hlavička souboru to od §43 hlásí |

### 51.2 Co je opravené

| Soubor | Změna | Doklad |
|---|---|---|
| `~\.dsh\skills\orchestra\SKILL.md` | řádek `test-cooldown` opraven (a staré varování označeno jako **historie**), `test-eskalace` označen **ZASTARALÉ**, přidán řádek pro `test-tick-offline.mjs`, blok „nemá test rozhodovací logiky“ **nahrazen pravdou** (starý text zůstal přeškrtnutý jako historie), opravena položka v „co orchestra NEMÁ“ | `over-skilly.py` → **13 skillů / 0 chyb**, **54 zmínek, 0 mrtvých** (bylo 48) |
| tamtéž — **Klíčové cesty** | přepsáno na stav po přesunu: root repa `E:\Workspaces\forge-orchestra\`, `conductor/`, `repo/`, `tools/`, `_analyza/`, `.secrets/`, `.env`, hra jako **sourozenec** `E:\Workspaces\uo-shadows\`; **24 předpřesunových odkazů sníženo na 2 legitimní** (historická poznámka + dnešní `forge-orchestra\repo\`) | `grep 'orchestra[/\\]'` → jen ř. 25 (historie) a ř. 470 (dnešní cesta) |
| `README.md` | `test-cooldown` opraven, `test-eskalace` označen ZASTARALÉ, **doplněno 6 řádků** pro nové brány (`B2`, `B3a`, `B3b`, `B4`, `N0.3`, tik offline) | `kontrola-diakritiky.py` → **VŠE OK** (256/300, 0 chyb) · `over-dokumentaci.py` → **67/0** |

### 51.3 Nový nález: BRÁNA NA CESTY V DOKUMENTACI JE SLEPÁ K TOMU, CO HLEDÁ

`over-skilly.py` **celou dobu hlásil „0 mrtvých cest“** — a přitom skill
obsahoval **24 odkazů na neexistující layout** (`orchestra/tools/`, `orchestra/repo/`).
Naměřeno: `Test-Path orchestra\tools` → **False**, `tools` → **True**.
Brána tedy měří jiný tvar cest, než jaký v dokumentu skutečně je (adresářový tvar
`orchestra/…` a prefix uvnitř delší ukázky jí uniká). **Patří to do fáze C**
(„brány, které lžou“) — dokud to tak je, „0 mrtvých cest“ **není důkaz**.

### 51.4 Co NENÍ hotové

* **Slepé místo `over-skilly` z §51.3** — neopraveno (patří do fáze C).
* **NENASOZENO** — beze změny: `N0.3` (§42), `B3a` (§43), `B4` (§45), inertní
  `B3b` (§46) čekají na rozhodnutí o pushi. Tenhle oddíl běhový kód nemění.
* **Kronika a plán** — až po nasazení, s důkazem z živé služby.

### 51.5 Brány (stav po §51)

* zelené: diakritika **VŠE OK** · `over-dokumentaci` **67/0** · `over-skilly`
  **13/0** (54 zmínek, 0 mrtvých) · `handoff` **83/83** · `kronika` **SEDÍ** ·
  `ag-over-cisla` · `ag-mutace`.
* `g3` → **49 bran**, **0 bez čítače**; nenulové exity: `zadání kontrola`
  (deklarovaný) a `validate-all`.
* `validate-all` → **1 problém**: `E. lokální kód = repo` = nepushnutá změna.

---

## 52. PŘEDÁNÍ — CO JE HOTOVÉ, CO ČEKÁ A JAK TO OVĚŘIT (6. 10. 2026)

**Co tenhle oddíl JE:** **předání stavu práce** pro session (nebo člověka),
který tuhle práci převezme. Je to jediné místo, kde je pohromadě **co je hotové,
co je připravené k nasazení a co zůstává otevřené**; podrobný záznam je
v oddílech **§42–§51**.
>
> **⚠ 7. 10. 2026: PRÁCE JE NASZENÁ A OVĚŘENÁ ŽIVĚ — viz §53.** Tabulka 52.2 je
> **záznam plánu nasazení**, ne dnešní stav; „NENASOZENO" níž už neplatí.

### 52.1 Hotovo v téhle session (vše ověřené bránami)

| # | Co | Kde je záznam | Doklad |
|---|---|---|---|
| 1 | **N0.3** — `/health` hlásí stav **cíle** (`main_ci`, `forge.ok`, `selhani_v_rade`, `error`) | §42 | brána `test-health-cile.mjs` **21/0** + mutace **11/0** |
| 2 | **B3a** — watchdog počítá běhy **granule** (přes všechny úkoly), prah **pod** stropem | §43 | `test-watchdog-granule.py` **17/0** + `b3-mutace.py` **11/0** |
| 3 | **B5** + **B2** — nepravdivé komentáře pryč; `/report` → cooldown má bránu | §44 | `test-report-cooldown.py` **8/0** + `b2-mutace.py` **9/0** |
| 4 | **B4** — bez aktivní hry se **nedispatchuje** (ani nečte roadmapa) | §45 | `test-listgames.py` **10/0** + `b4-mutace.py` **9/0** |
| 5 | **B3b** — strop na granuli (`GRAIN_MAX_RUNS`, **výchozí vypnuto**) + shoda obou tvarů klíče | §46 | `test-grain-cap.py` **22/0** + `b3b-mutace.py` **11/0** |
| 6 | **Čítač brány `C2: mutace N1`** + zrušená deklarovaná výjimka | §47 | registr `5 / 0`, `ma_citac: true` |
| 7 | **Test rozhodovací logiky conductora** — skutečný `/tick` i `/report` nad zbundlovaným conductorem | §48–§50 | **40 kontrol** + `tick-mutace.py` **8 vrat / 17/0** |
| 8 | **Dokumentace, která popírala nástroje** — skill `orchestra` + `README` | §51 | `over-skilly` **54 zmínek, 0 mrtvých** |

### 52.2 Připraveno k NASAZENÍ (a co to udělá s živou službou)

Push do `conductor/**` spouští `deploy.yml` = **nasazení živé služby**. Doporučené
pořadí (plán: „nasadit po částech a měřit před/po“):

| Krok | Co obsahuje | Dopad na provoz | Riziko |
|---|---|---|---|
| **1** | `B2` + `B5` + §47 (jen testy, komentář, čítač) | **žádný** | nulové |
| **2** | `N0.3` (§42) | `/health` přidá `targets[]` | nízké (2 volání GitHubu na 2 min cache) |
| **3** | `B3a` (§43) | watchdog začne hlásit; **dnes pošle 2 notifikace** (`entity.npc` 8 běhů, `entity.enemy` 5) a v `/tick` bude `watchdog: 2 ohlášeno (prah 3)` | nízké |
| **4** | `B4` (§45) — **samostatně** | bez aktivní hry se **přestane dispatchovat** (zamýšleno) → ověřit, že vypnutá hra opravdu nic nespustí | střední |
| **5** | `B3b` (§46) — **nic nezapínat** | inertní; teprve `GRAIN_MAX_RUNS = "5"` (samostatný krok) strop **zapne** | nulové |

**Ověření po nasazení** (co má být vidět): `/health` má `targets[0].main_ci`
a `targets[0].forge` (`ok: false`, `selhani_v_rade ≈ 10`) · `/tick` hlásí
`watchdog: …` · notifikace o granulích · s vypnutou hrou `spusteno: 0 úloh`.

### 52.3 Otevřené (nic není zapomenuté, jen neudělané)

* **Nasazení** — rozhodnutí uživatele (viz 52.2). **Nic jsem nepushnul.**
* **Kronika a plán** — řádek do `KRONIKA-PROJEKTU.md` a přepis `N0.3`/`B3`/`B4`
  v plánech na HOTOVO patří **až po nasazení** a s důkazem z **živé** služby.
* **Netestované endpointy handlerem:** `/poll`, `/claim`, `/heartbeat`,
  `/tasks/cleanup`, `/roadmap/reset` (§50.3).
* **Slepé místo brány `over-skilly.py`:** hlásí „0 mrtvých cest“, ale 24 odkazů
  na neexistující layout jí prošlo (§51.3) — patří do fáze C („brány, které lžou“).
* **Fáze C a D** celé — čekají na rozhodnutí `O3`, `O10`, `O5–O8`
  (`PLAN-ROZVOJ-ORCHESTRA.md` §6).

### 52.4 Jak to ověřit (jeden příkaz + co má být červené)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json   # inventář POSLEDNÍ
python _analyza\g3-brany.py          # 49 bran, 0 bez čítače
node tools\validate-all.mjs          # 1 problém: "E. lokální kód = repo"
```

⚠ **Červená `E. lokální kód = repo` je SPRÁVNĚ**, dokud práce není v gitu —
kontrola porovnává lokální `conductor/src/index.ts` s verzí **na GitHubu**.
Zmizí prvním schváleným pushem. Kdyby byla červená **jiná** kontrola, je to vada.

**Stav stromu:** **13 změněných + 12 nových souborů**, necommitnuto (čeká na
rozhodnutí o pushi); do hry `uo-shadows` jsem **nesáhl**.

---

## 53. NASZENO A OVĚŘENO ŽIVĚ (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** — uživatel schválil
„commit i push hned“ a doplnění kroniky. Stav je v `§2.x` + `KRONIKA §1/38`.

### 53.1 Co se stalo

| Krok | Důkaz |
|---|---|
| Uživatel schválil commit i push | „Určitě můžeš commit i push hned co všechno čeká a doplň kroniku.“ |
| **Commit** | **`598e207`** — 25 souborů, **+3714/−109** (tělo zprávy v commitu) |
| **Push** | `48eebd8..598e207 main -> main`; `git rev-list --count origin/main..HEAD` → **0** |
| **Deploy** | běh **#33** (`Deploy conductor (Cloudflare)`) na `head_sha = 598e207` → **completed / success** (job `deploy`: success) |
| **Kronika** | řádek **38** vložen skriptem `_analyza/n03d-radek-kroniky.py` (**12 kontrol, 0 chyb**); `kronika-kontrola.py` → **SEDÍ**; omyly = `—` (uživatel je nechce vést), §3 se nepřepočítává |
| **Plány** | `PLAN-ORCHESTRA-AI-AGENTI.md` **N0.3** → ✅ HOTOVO; `PLAN-ROZVOJ-ORCHESTRA.md` **B2/B3/B4/B5** → ✅ HOTOVO (s živými důkazy) |

### 53.2 Živé ověření po nasazení (měřeno, ne odhad)

```
/health: ok=true ready=1 running=0 games=1 time=2026-10-07T06:08:21.760Z
targets[0]: repo=ssevcikm-spec/uo-shadows error=null measured_at=2026-10-07T06:08:20.860Z
  main_ci: success (ci.yml, run #117)
  forge:   ok=false  selhani_v_rade=20
/tick: spusteno: 1 úloh; polling: zadny cloudovy beh nebezi;
       z roadmapy založeno 1 granulí, zombie zablokováno: 1,
       watchdog: 2 ohlášeno (prah 3)
```

* **N0.3 funguje:** `/health` nese stav **cíle** — `main_ci` i `forge.ok`.
  ⚠ **Předpověď v §52.2 byla „`selhani_v_rade ≈ 10`“, naměřeno `20`** — smyčka
  jela dál přes noc; předpověď byla o řád vedle, ne na místě.
* **B3a funguje:** watchdog ohlásil **2 granule** (`entity.npc`, `entity.enemy`) —
  přesně jak §52.2 předpovědělo. Do 6. 10. 2026 se **nespustil ani jednou**.

### 53.3 Vlastní past, kterou tenhle commit málem přinesl

Před commitem byl ve **stageované** verzi `conductor/src/index.ts` na ř. 1702
**`if (false) {`** — zbytek mutace **M8** z `_analyza/tick-mutace.py`
(`_mutace.mutuj` ji měl vrátit; **disk byl správně, index ne**).
Odhalila to až kontrola **stageovaného blobu** (`git show :soubor`) na známé
značky mutantů — `git diff` ji neukázal.
**Poučení: v repu, kde běží mutační testy, se před commitem kontroluje INDEX,
ne pracovní strom.** Zapsáno i v kronice (řádek 38).

### 53.4 Co zůstává otevřené

* **B3b zapnout strop** (`GRAIN_MAX_RUNS = "5"`) — samostatný krok, až bude
  vidět, že watchdog stačí.
* **B4 ověřit živě** vypnutím hry (`POST /game/active {active:false}`) — kód
  i brány jsou hotové, acceptance „žádný dispatch“ ještě neproběhlo na živé službě.
* **Netestované endpointy handlerem:** `/poll`, `/claim`, `/heartbeat`,
  `/tasks/cleanup`, `/roadmap/reset`.
* **Slepé místo `over-skilly.py`** (24 odkazů na neexistující layout prošlo) — §51.3.
* **Fáze C a D** — čekají na `O3`, `O10`, `O5–O8`.
* **⚠ V workspace pracuje souběžná session (generalizace nástrojů, 7. 10. 2026)** —
  její rozdělanou práci (`_analyza/ag-over-cisla.py`, `tools/over-skilly.py`,
  `tools/over-dokumentaci.py`, `_analyza/ov-*.py`, …) jsem **ZÁMĚRNĚ
  necommitoval**; v `AGENTS.md` je z ní jen jednořádková aktualizace počtu bran.


---

## 54. P24 — NEZÁVISLÉ PŘEMĚŘENÍ NASAZENÍ A ROZŠÍŘENÍ TESTU TIKU (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** — co P24 naměřila a co udělala.
**Stav** je v `§53` (nasazení P23) a v novém oddílu **55** (stav po P24);
**pravidla** v `AGENTS.md`; **historie** v `KRONIKA-PROJEKTU.md` (řádek **39**,
nálezy **§2.17**). Zadání P24 je v `NEXT-SESSION-INSTRUKCE.md`
(`git log -1 NEXT-SESSION-INSTRUKCE.md` = `d998190`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 08:3x–09:5x +02:00**. Tvrzení
> o **stavu** (HEAD, fronta, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\p24-a-overeni.py`).

### 54.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Nezávislé přeměření nasazení P23 a záznamů** (zadání §2.1, body A1–A8) — vlastním měřidlem, ne čtením §53 | `_analyza/p24-a-overeni.py` → **99/0** (99 kontrol, 0 chyb); `_analyza/p24-b-mutace.py` → **17/0** (dokazuje, že měřidlo UMÍ spadnout) |
| **B3** | **Offline test tiku rozšířen na endpointy, které netestoval NIKDO**: `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset` | `tools/test-tick-offline.mjs` → **100/0** (100 kontrol, 0 chyb; bylo **40/0**) |
| **B3** | **Mutační důkaz k novým cestám** — 7 nových vrat (M9–M15) | `_analyza/tick-mutace.py` → **31/0** (15 vrat, 31 kontrol, 0 chyb; bylo 8 vrat / **17/0**) |
| **C** | Brány po sobě | `g3` → **48 bran, 0 bez čítače, 0 nenulových exitů**, `exit 0` · `validate-all` → **VŠE V POŘÁDKU** (exit 0) · `handoff-kontrola-uplnost` → **83/83** · `kronika-kontrola` → **SEDÍ** · `zadání kontrola` → **exit 0** (kotva `4925f64` = živý HEAD) |

> ⚠ **POŘADÍ JE SOUČÁST VÝSLEDKU:** první `g3` po dávce dokladů byl **ČERVENÝ**
> (`ag-over-cisla`, `ag-mutace`, `validate-all (CELEK)`) — protože běžel nad
> **registrem přepsaným harnessem** (`bran_celkem: 1`, bod 11 níž) a správný
> registr zapisuje **až na konci**. Teprve **druhý běh** je zelený (48 bran,
> 0 nenulových exitů). **Kdo čte jen první běh, vidí vadu měření, ne stav.**

### 54.2 Co A1–A8 naměřily (a co se ROZEŠLO s §52/§53)

| # | Tvrzení záznamu | Nezávislé měření P24 | Verdikt |
|---|---|---|---|
| **A1** | živá služba = `598e207`, deploy #33 success | GitHub API: poslední **úspěšný** `deploy.yml` = **#33** na `head_sha 598e207`; `598e207` je **poslední commit, který změnil `conductor/**`**; **bloby** `index.ts` i `wrangler.toml` v něm a v `HEAD` jsou **shodné**; živé `/health` vrací `targets[]` (což umí JEN ten kód) | **POTVRZENO** |
| **A1** | — | `/health` dnes: `ok=true ready=2 running=0 games=1`; `targets[0].main_ci = success (ci.yml #117, head 44dd454)`, `forge.ok=false`, **`selhani_v_rade=20`** | číslo `ready` je dnes **2** (v §53 bylo 1) — fronta roste |
| **A2** | `/tick` → `watchdog: 2 ohlášeno (prah 3)` | dnes `/tick` → **`watchdog: 0 ohlášeno (prah 3)`**; prah **3** = hodnota ve ZDROJI a je **POD** stropem `MAX_ATTEMPTS=5` (přesně to byla vada B3a) | **POTVRZENO s výhradou**: `2` platilo při PRVNÍM tiku; značka `eskalovano` je **TRVALÁ**, takže `0` je SPRÁVNĚ, ne „nespustilo se“ |
| **A2** | stav granul v D1 | **NEZMĚŘENO** — conductor **nemá endpoint**, který by `roadmap.eskalovano` vracel (ověřeno čtením SELECTu handleru `/roadmap` ve zdroji) a D1 přes REST nejde (invariant 7) | **přiznané nezměřeno** (není to nula a není to zelená) |
| **A3** | v commitu nejsou mutanty | 40 kotv z **21** mutačních skriptů ověřeno v **blobech** `598e207`, `7f0b2f8` i `HEAD`; `disk == index == HEAD` u všech čtyř mutovaných souborů | **POTVRZENO** |
| **A4** | brány umí selhat | všech **6** mutačních důkazů zelených, po KAŽDÉM je strom zpět; navíc **ruční mutace MIMO knihovnu** (`selhani_v_rade: 0,`) branu shodila (`exit 1`) | **POTVRZENO** |
| **A5** | nic nezmizelo | `handoff-kontrola-uplnost` **83/83, CHYBÍ 0**; KRONIKA v rozsahu `598e207~1..7f0b2f8` = **0 smazaných řádků**; v posledních 6 commitech se **nesmazal žádný řádek session** | **POTVRZENO** |
| **A6** | čísla v plánech sedí na kód | **12 bran znovu spuštěno** a jejich čítače **přesně** odpovídají tvrzením v dokumentech: 21/0+11/0 (N0.3), 17/0+11/0 (B3a), 8/0+9/0 (B2), 10/0+9/0 (B4), 22/0+11/0 (B3b), 40/0+17/0 (tik offline); `grep "mrtvý kód"` → **0** | **POTVRZENO** |
| **A7** | v mém commitu nejsou soubory druhé session | `598e207` a `f8595de` mají průnik **2 soubory** (`_analyza/_registr-bran.json`, `tools/validate-all.mjs`) — **a přesto nic neuniklo**: `f8595de` je **POTOMEK** `598e207`, takže souběžná session na ně sáhla **POZDĚJI** | **POTVRZENO, ale otázka zadání byla špatná** (ptala se na průnik, ne na pořadí) |
| **A8** | hra nedotčená | `uo-shadows` = **`44dd454`**, strom **čistý**, 0 nepushnutých; v rozsahu `598e207~1..7f0b2f8` **není nic** z cesty do hry (29 souborů) | **POTVRZENO** |

### 54.3 Nálezy P24 (každý doložený měřením)

1. **⚠ PŘERUŠENÝ MUTAČNÍ BĚH NECHAL V ŽIVÉM ZDROJI ČTYŘI MUTANTY.** První běh
   měřidla byl spuštěn s `Tee-Object`, které **neumělo otevřít výstupní soubor**;
   pipeline se přerušila **uprostřed** `tick-mutace.py` a `finally` knihovny
   `_mutace.mutuj` se **nevykonal**. V `conductor/src/index.ts` zůstaly
   `expiruje: 0`, `merged = true;`, requeue **bez stropu** a `if (false) break;`.
   Odhalila to **A3** (`disk != index`/`HEAD`) — a to je celý důvod, proč se
   mutované soubory mají měřit **hashem**, ne okem. Strom byl obnoven z blobu
   (`git checkout HEAD -- conductor/src/index.ts`) a stavově ověřen.
   **Poučení: přerušený mutační běh je STAV, který se musí ověřit — ne nehoda,
   která „se nějak srovnala“.** Měřidlo teď (a) **odmítne mutovat nečistý strom**
   a (b) kontroluje návrat **po každém** skriptu.
2. **⚠ `git checkout` TICHE ROZBIJE MUTAČNÍ DOKLADY.** Repo orchestra **nemá
   kořenový `.gitattributes`** (má ho jen šablona `repo/`) a `core.autocrlf=true`
   → checkout přepíše `conductor/src/index.ts` na **CRLF**. Vícřádkové kotvy
   mutací (`…\n               naposledy_selhalo …`) pak hlásí
   **„kotva v souboru NENÍ“** — tedy vadu TESTU, která žádná není.
   A `git status` je přitom **čistý** (git normalizuje při čtení), takže nic
   nevaruje. Náprava stavu: obnovit soubor **z blobu bajty** (LF).
   **Návrh (k rozhodnutí): doplnit kořenový `.gitattributes` jako v šabloně.**
3. **⚠ PowerShell `>` PÍŠE UTF-16LE.** `python skript.py > vystup.txt` vyrobil
   soubor začínající `FF FE`; `read` tool ho odmítl přečíst jako binárku.
   Je to **tatáž past jako `git show > soubor`** (`dsh-prostredi` §5b), jen
   u obyčejného programu. Měřidlo si proto výstup **zapisuje samo** (UTF-8).
4. **⚠ CLOUDFLARE BLOKUJE `Python-urllib` PODLE User-Agenta** — vrací
   `403 error code: 1010`, což **vypadá jako výpadek služby nebo špatný klíč**.
   S User-Agentem prohlížeče odpovídá `200`. Naměřeno sondou
   `_analyza/p24-sonda-site.py` (Node `fetch` tuhle past nemá — má vlastní UA).
5. **⚠ BRÁNA SE PTALA NA PRŮNIK MNOŽIN, ALE ROZHODUJE POŘADÍ.** „Neobsahuje
   soubory druhé session“ se v zadání myslelo jako průnik seznamů; průnik
   vyšel **2**, a přesto **nic neuniklo** — druhá session commitovala **později**
   (`merge-base --is-ancestor 598e207 f8595de` = pravda). Kdo se ptá jen na
   průnik, hlásí **falešný nález o správném commitu**.
6. **⚠ `N > 0` U WATCHDOGU JE NASTRAŽENÁ OTÁZKA.** Značka `eskalovano` je
   **trvalá**: po prvním ohlášení je počet ohlášených **navždy 0**, takže
   kontrola „ohlásil něco“ by shodila **správnou** službu. Místo toho se měří
   **prah < strop** (to byla skutečná vada B3a) a prah **proti zdroji**.
7. **⚠ KONTROLA TVARU DOKUMENTU MUSÍ MÍŘIT NA NADPIS, NE NA FRÁZI.** A6 tvrdila
   `„Fáze B“ in dokument` — a to platí i po smazání oddílu, protože táž fráze
   stojí ve větě „Fáze B znamená deploy conductora“. **Odhalil to až mutační
   test** `p24-b-mutace.py` (případ 2). Dnes se hledá `### Fáze B`.
8. **⚠ „PŘEDPONA STARÉHO OBSAHU“ NENÍ SPRÁVNÁ OTÁZKA PRO KRONIKU.** Řádek 38 se
   vkládá **doprostřed** tabulky §1, takže starý obsah **není** předponou nového —
   a přesto se nic neztratilo. Správná otázka je **„byl smazán nějaký ŘÁDEK
   SESSION?“**; smazat se smí jen **souhrnný** řádek (`| **celkem** |`, `| **1–N** |`),
   protože to je stav, ne záznam.
9. **⚠ DVĚ NOVÉ MUTACE NEBYLY CHYCENY — A OBĚ BYLY VADY MÝCH NOVÝCH KONTROL,
   NE KÓDU.** (a) M2 `MAX_CONCURRENT` zacyklil falešný svět (dispatch claim
   nepřepnul stav úlohy) a Node spadl na **`exit 134`**; harness čeká `CHYBA`
   ve výstupu, takže to vyhodnotil jako „nechyceno“. (b) M13 (`cleanup` bez
   pojistky) prošel, protože **obě** pojistky vrací 503 a slovo „nemažu“ je
   v **obou** hláškách — kontrola byla měkká. Po opravě: **31 kontrol, 0 chyb**.
10. **Test rozhodovací logiky už nekryje jen `/tick` a `/report`.** Nově volá
    i `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`
    včetně **tajemství** (401), **chybějící hlavičky uzlu** (400), **prohraného
    optimistického zámku**, **dry-runu, který nesmí mazat**, a **pojistky
    „roadmapa se nedá načíst → nemažu“** (503).
11. **⚠ DÁVKA DOKLADŮ PŘEPSALA ŽIVÝ REGISTR BRAN — a `validate-all` by kvůli
    tomu četl lež.** Naměřeno 7. 10. 2026 po `python _analyza\p20-d-doklady.py`:
    `_analyza/_registr-bran.json` měl **`bran_celkem: 1`** a jedinou bránu
    **`A1: zdravá`** (fixtura z harnessu), přitom živých bran je **48**.
    Viník je **`_analyza/p19-d-kontroly.py`** — staví si **kopii `g3`
    s vlastními fixturami** a pouštěl ji **bez `--soubor`**, takže si kopie
    zapsala registr (přesně vada z `AGENTS.md`/§6.14, kterou `p20-d-doklady.py`
    **ohlásí, ale neopraví**). **OPRAVENO**: `p19-d-kontroly.py` nově předává
    `FORGE_BEZ_REGISTRU=1`. **Poučení pro pořadí: po dávce dokladů se `g3`
    pouští VŽDY** — jinak je registr z fixtur a `validate-all` („bran v registru
    = 48“) spadne na správném repu. **A druhý důsledek, který se nesmí přehlédnout:
    `g3` sám je nad zkaženým registrem ČERVENÝ** (`ag-over-cisla` měří „bran
    v registru = 48“, `ag-mutace` na tom staví svůj výchozí krok) — a správný
    registr zapíše **až na konci svého běhu**. **Proto se po dávce dokladů pouští
    `g3` DVAKRÁT** (nebo se před ním registr opraví ručně — což se nemá, je
    generovaný). Naměřeno 7. 10. 2026: 1. běh `exit 1` (3 nedeklarované červené),
    2. běh `exit 0` (48 bran, 0 nenulových exitů).
12. **⚠ DÁVKA DOKLADŮ MÁ TŘI ČERVENÉ, KTERÉ NEJSOU MOJE — a jeden z nich jsem
    opravil jen z poloviny.** `python _analyza\p20-d-doklady.py` → **27 dokladů,
    3 s nenulovým exit** (kromě P24, které je zelené): `ov-g-h92-sken.py`
    (doložený **falešný poplach**, nález **H103** — rozhodnuto **NEOPRAVOVAT**),
    `p19-c-h94-podpisy.py` (**27 kontrol, 1 chyb** — čeká řádek
    `OCEKAVANE_BEZ_CITACE` v harnessu `g3`, který se od P20 změnil) a
    `p19-d-kontroly.py` (dobový doklad z P19). **Jsou to doklady jiných session
    a jejich verdikt jsem NEOPRAVOVAL** — u `p19-d` jsem opravil jen to, že
    přepisoval živý registr (bod 11). **Kdo je bude opravovat, ať nejdřív změří,
    co přesně zestaralo** („neopravovat nástroj dřív, než je jasné, co je
    špatně“).

### 54.4 Živý stav při zápisu (7. 10. 2026, ~09:5x +02:00)

```
orchestra: HEAD 4925f64 · origin/main c664dde · nepushnutých commitů 1
           (ten commit je ARCHIVACE 25 nástrojů — práce SOUBĚŽNÉ session)
hra:       HEAD 44dd454 · strom čistý · 0 nepushnutých
živá služba: /health → targets[0] main_ci success (ci.yml #117), forge.ok false,
             selhani_v_rade 20 · /tick → watchdog: 0 ohlášeno (prah 3)
```

### 54.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p24-a-overeni.py          # A1-A8: 99 kontrol, 0 chyb
python _analyza\p24-b-mutace.py           # umí to spadnout? 17 kontrol, 0 chyb
node tools\test-tick-offline.mjs          # 100 kontrol, 0 chyb
python _analyza\tick-mutace.py            # 15 vrat, 31 kontrol, 0 chyb
python _analyza\g3-brany.py               # 48 bran, 0 bez čítače
node tools\validate-all.mjs               # VŠE V POŘÁDKU
```


---

## 55. P25 — PŘEMĚŘENÍ P24 A TESTOVÁNÍ ZAPISUJÍCÍCH ENDPOINTŮ (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P25 + stav po P25**. Plní i slot,
na který §54 **visutě odkazoval** („stav je v novém oddílu 55“) — oddíl 55 do
P25 **neexistoval** a to je samo nález (níž, bod 1). **Pravidla** v `AGENTS.md`,
**projektová znalost** v `PROVOZ-ORCHESTRA.md`, **historie** v
`KRONIKA-PROJEKTU.md` (řádek **40**, nálezy **§2.18**). Zadání P25 je
v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 13:0x–14:2x +02:00**. Tvrzení
> o **stavu** (HEAD, hra, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\p25-a-overeni.py --plne`).

### 55.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Přeměření práce P24 VLASTNÍM měřidlem** (A1–A6, každý bod jiným postupem, než vznikl) | `_analyza/p25-a-overeni.py` → **53 kontrol, 0 chyb** (první běh měl 6 chyb — všechny typu „číslo se změnilo, a ještě není zapsané“; to je správné chování, po zapsání tohoto oddílu 0) |
| **A** | **Důkaz, že i tohle měřidlo umí spadnout** — 5 mutací v **KOPIÍCH** + diferenciál + rozhodovací funkce A3 | `_analyza/p25-b-mutace.py` → **27 kontrol, 0 chyb** |
| **B1** | **Testy pro endpointy, které ZAPISUJÍ do D1 a MĚNÍ CHOVÁNÍ služby**: `POST /task`, `POST /game`, `POST /game/active` — včetně integrační kontroly, že vypnutá hra zastaví dispatch | `tools/test-tick-offline.mjs` → **146/0** (146 kontrol, 0 chyb; bylo **100/0**) |
| **B1** | **Mutační důkaz k novým cestám** — 5 nových vrat (M16–M20) | `_analyza/tick-mutace.py` → **20 vrat / 41/0** (bylo 15 vrat / 31/0) |
| **C** | Brány po sobě (po přegenerování inventáře) | `g3` → **49 bran**, 1 deklarovaný nenulový exit (`zadání kontrola`), `exit 0` · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |

### 55.2 Nálezy P25 (každý doložený měřením)

1. **§54 OBSAHUJE VISUTÝ ODKAZ NA ODDÍL 55, KTERÝ NEEXISTOVAL.** §54 tvrdí
   „stav je v `§53` … a v novém oddílu **55** (stav po P24)“ — a `## 55.`
   v `HANDOFF.md` nebylo (nejvyšší oddíl byl 54). Tenhle oddíl slot plní, ale
   jako záznam **P25**. **Poučení: odkaz na oddíl je TVRZENÍ o dokumentu**
   a `handoff-kontrola-uplnost` kontroluje klíče, ne cíle odkazů.
2. **DOBOVÁ KOTVA P24 PŘESTALA PLATIT, PROTOŽE SE ZMĚNIL STAV — ne proto, že
   by měřidlo lhalo.** `p24-a-overeni.py` dnes vrací **99/1** (na kotvě
   `4925f64` naměřila **99/0**): jediná červená je **A8** — `uo-shadows` je dnes
   **`932dc6f`**, ne `44dd454`. To je **správné chování** měřidla: měří živý
   stav, ne zamrzlý text (A8 je v P24 označená jako `DOBOVÉ`). První dnešní běh
   dal **99/4** — další tři červené byly A6 („dokument netvrdí naměřené 146/0
   a 41/0“), tedy **následek mojí vlastní práce B1**; po zapsání tohoto oddílu
   zmizely.
   **Co hru změnilo:** souběžná session (generalizace nástrojů) do ní
   **7. 10. 2026 přidala commit** `932dc6f` (`AGENTS.md` + `docs/BRANY-HRY.md`)
   a **pushla ho**, i když uživatel hru pozastavil. **Není to moje práce** —
   je to zapsané jako změna stavu, která P24inu A8 dělá dobově neplatnou.
3. **ZARÁŽKA V ROUTERU ZAPNE PRÁVĚ TY KONTROLY, KTERÉ MÁ — a `/tick` zůstane
   zelený.** A3 vložila do živého `conductor/src/index.ts` (v `try/finally`,
   s ověřením hashe před i po) návrat `599` pro pět endpointů: test tiku vykázal
   **42 červených**, mezi nimi **všech 5 cílených** (`N`, `O`, `P`, `Q`, `R`),
   a **kontrolní `A: /tick odpoví 200` zůstala zelená**. Druhá zarážka
   **uvnitř handleru** `/tasks/cleanup` (změna hlášky pojistky) zapnula
   **právě 1** kontrolu (`Q2: a řekne PROČ`) a `Q2: nenačtená roadmapa → 503`
   zůstala zelená. **Tím je doloženo, že test endpointy opravdu VOLÁ** a že
   kontroly nejsou měkké (past P24-I).
4. **⚠ SABOTÁŽ SE TICHE NEPROVEDLA — a odhalil to až DIFFERENCIÁL.** Vlastní
   měřidlo mělo spustit `p24-b-mutace.py` nad **oslabenou** kopií měřidla (bez
   kontroly `B4`). Kotva v cizím skriptu je ale **`ANALYZA` (s Y)**, ne
   `ANALIZA` (s I) — `replace()` tedy **nic nenahradil** a sabotovaný důkaz
   hlásil `17/0` nad **NEZMĚNĚNÝM** skriptem. Přesně past `overovani` §7.9
   („mutace, která se tiše neprovede, vypadá jako úspěch“). Zachytil to
   **diferenciál** (originál na téže vadě spadne, oslabená kopie projde);
   měřidlo dnes **explicitně kontroluje, že sabotáž míří na oslabenou kopii**.
5. **VLASTNÍ MĚŘIDLO MĚLO TŘI VADY A VŠECHNY ODHALIL JEHO BĚH** (ne čtení):
   (a) práh „aspoň 20 kontrol“ v režimu `--jen-dokumenty`, který měří **8**;
   (b) A2 klasifikoval **JS literály** (`, watchdog: ${eskalovano}` a log-prefix
   `roadmap.eskalovano: `) jako SQL → falešný poplach „nesklasifikovaný zápis“;
   (c) jednoduchý vzor `[^…\n]` **nenašel víceřádkový SQL literál** → falešný
   poplach „nikde není výběr kandidátů“. Všechny tři jsou **falešné poplachy
   nad správným zdrojem** — nejdražší druh vady (`overovani` §8.3).
6. **TRVALOST ZNAČKY `eskalovano` JE DOKÁZANÁ Z KÓDU, NE Z DOJMU.** Vlastní
   čtení **SQL literálů po odstranění komentářů** našlo: samomigraci
   `ALTER TABLE roadmap ADD COLUMN eskalovano TEXT`, **právě jeden** zápis
   (`SET eskalovano = datetime('now')`), **žádné** mazání a filtr kandidátů
   `status <> 'done' AND (eskalovano IS NULL OR eskalovano = '')`. Živé `/tick`
   pak hlásí **`0 ohlášeno` (prah 3 < strop 5)** — kontrola „ohlásil něco“
   (`N > 0`) by tedy **shodila zdravou službu**. Negativní kontrola: po vložení
   mazacího `UPDATE` do KOPIE zdroje predikát vadu **ohlásí**.
7. **`tick-mutace.py` NEVYKAZOVAL POČET VRAT.** Číslo „15 vrat“ žilo jen
   v dokumentech. Měřidlo ho proto odvozuje **dvěma nezávislými cestami** (AST
   zdroje: počet `MUTATIONS`; aritmetika z běhu: `1 + 2×vrat`) a doklad ho od
   P25 **vypisuje sám** (`vrat: 20`).
8. **NENULOVÝ EXIT NENÍ VŽDY NÁLEZ — MŮŽE BÝT STAV.** Po přidání dokladů měl
   `g3` **6 nenulových exitů**: tři byly **zastaralý inventář** (náprava je
   přegenerovat, **ne deklarovat** — deklarace by z trvalé vady udělala
   „očekávaný stav“) a dva **moje vlastní chyba v textu skillu** (`tools\…`
   v tabulce vzal `over-skilly` jako mrtvou cestu). Po nápravě **49 bran,
   1 deklarovaný exit**. Měřidlo proto „nedeklarovaný exit“ **rozlišuje** na
   nález a na pojmenovaný stav.
9. **`/task`, `/game` a `/game/active` UŽ MAJÍ TEST — a test měří i CHOVÁNÍ.**
   Nově se ověřuje, že payload jde do D1 jako **JSON řetězec**, že `target: lan`
   se opravdu uloží jako `lan`, že registrace hry ji **ZAPNE** (`active = 1`),
   že vypnutí zapíše **`active = 0`** (a ne 1), že neznámá hra vrátí **404** —
   a hlavně **integrační kontrola W**: po `/game/active {active:false}` tik
   **NEDISPATCHUJE** a po zapnutí dispatchuje **právě jednou**.
10. **⚠ SANDBOX ODEMKL ZÁPIS PODPROCESŮM V PODADRESÁŘÍCH.** V první polovině
    session nešlo zapsat soubor podprocesem do **žádného** podadresáře
    workspace (`PermissionError [Errno 13]`), zatímco do kořene ano; nástroj
    `write` (harness) přitom zapsal i do podadresáře. **Nebyla to vada
    skriptů** — spadlo na tom celé měřidlo P24 (11 `PermissionError`, mutace se
    vůbec neprovedly) a `git fetch` (`.git/FETCH_HEAD`). Opravný skript ACL
    vrátil `VERDICT=NOT_THIS_CLASS`; pomohlo až **přepnutí session na plný
    přístup**. Past je zapsaná ve skillu `dsh-prostredi` §4e.
11. **⚠ MĚŘIDLO `ov-g-neovereno.py` TIŠE ZÚŽILO ROZSAH — z 99 řádků na 1.**
    Zadání P25 §2.4 bod 3 nařizuje ověřit `NEOVĚŘENO` **tímhle měřidlem**. Ono
    dnes (po optimalizaci KB souběžné session, 7. 10. 2026 ~13:09) čte **jen
    `HANDOFF.md`** — a tam zbyl **1** řádek tabulky Hxx. Zbylých **98** řádků se
    přesunulo do **`_archiv/HANDOFF-HISTORIE.md`** (1 + 98 = **99**, přesně
    tolik, kolik jich P24 naměřila). **Měřidlo ten soubor neotevírá**, takže jeho
    verdikt „žádný nález ve stavu NEOVĚŘENO“ dnes **tvrdí něco o 1 řádku, ne
    o 99** — a nikdo to nepozná, protože měřidlo sice vypíše čítač, ale
    **rozsah ne**. **Co jsem naměřil nezávisle:** v `_archiv/HANDOFF-HISTORIE.md`
    je **98** řádků Hxx a **0** z nich má `NEOVĚŘENO` → otevřený bod se tedy
    **neztratil** (a soubor je **trackovaný v gitu**, ne ignorovaný).
    **Náprava (pro P26):** měřidlo má číst i archiv — nebo aspoň vypsat, KTERÉ
    soubory otevřelo; jinak je jeho zelená nad 1 % původního rozsahu.

### 55.3 Živý stav při zápisu (7. 10. 2026, ~14:2x +02:00)

```
orchestra: HEAD 92aa80a · origin/main 92aa80a · nepushnutých commitů 0
           (e401f6f, 22cebce i 92aa80a jsou práce SOUBĚŽNÉ session — P24inu
            práci commitla a pushla ONA, ne já)
hra:       HEAD 932dc6f · origin/main 932dc6f · strom čistý · 0 nepushnutých
živá služba: /health → ok=true ready=2 running=0 games=1 · targets[0] main_ci
             (ci.yml #118 na 932dc6f), forge.ok=false, selhani_v_rade=20
             /tick → watchdog: 0 ohlášeno (prah 3)
brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0
```

### 55.4 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p25-a-overeni.py --plne   # A1-A6: 53 kontrol, 0 chyb
python _analyza\p25-b-mutace.py           # umí to spadnout? 27 kontrol, 0 chyb
node tools\test-tick-offline.mjs          # 146/0
python _analyza\tick-mutace.py            # 20 vrat / 41/0
python _analyza\p24-a-overeni.py          # 99/1 (A8: hra je na 932dc6f, ne 44dd454)
python _analyza\p24-b-mutace.py           # 17/0
python _analyza\g3-brany.py               # 49 bran, 1 deklarovaný exit
node tools\validate-all.mjs               # VŠE V POŘÁDKU
```
## 56. P26 — PŘEMĚŘENÍ P25, ZARÁŽKA V HANDLERU A OPRAVA ROZSAHU MĚŘIDLA (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P26 + stav po P26**. **Co NENÍ:**
pravidla (`AGENTS.md`), projektová znalost (`PROVOZ-ORCHESTRA.md`), historie
(`KRONIKA-PROJEKTU.md` — řádek **41**, nálezy **§2.19**). Zadání P26 je
v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 13:1x–16:2x +02:00**. Tvrzení
> o **stavu** (HEAD, hra, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\p26-a-overeni.py --plne`).
>
> **⚠ POZOR NA SOUBĚŽNOU SESSION:** do hry zapisoval **NĚKDO JINÝ** — mezi
> 15:50 a 16:02 +02:00 přibyly v `uo-shadows` **tři commity** (`6796188`,
> `43a2004`, `125b062`, **nepushnuté**) a netrackovaný `_acl-recovery/`.
> **Není to práce P26** a **nesahalo se na to**.

### 56.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Přeměření práce P25 VLASTNÍM měřidlem** (A1–A6, každý bod jiným postupem, než vznikl) | `_analyza/p26-a-overeni.py --plne` → **90 kontrol, 0 chyb** (0× `NEZMĚŘENO`), uložený výstup `p26-a-plne-vystup.txt` |
| **A** | **Důkaz, že i tohle měřidlo umí spadnout** — tři mutace **v KOPIÍCH**, každá s **diferenciálem** (originál spadne / oslabená kopie projde) | `_analyza/p26-b-mutace.py` → **26 kontrol, 0 chyb** |
| **B1** | **Oprava brány, která tiše zúžila rozsah z 99 řádků Hxx na 1** (nález P25-K) | `_analyza/ov-g-neovereno.py` → rozsah **1 → 99**, vypisuje KTERÉ soubory otevřel; fixtury: `NEOVĚŘENO` → `exit 1`, prázdno → `NEMĚŘENO` |
| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) | `g3` → **49 bran, 1 deklarovaný nenulový exit** (`zadání kontrola`), **exit 0** · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |

### 56.2 Nálezy P26 (každý doložený měřením)

1. **P25 NETVRDILA PRAVDU O TOM, CO ZMĚŘILA — a nebyla to lež, byla to
   MEZERA.** §55 (bod 9 i tabulka 55.1) tvrdí, že test tiku volá `POST /task`,
   `/game` a `/game/active`. **P25 to ale nedoložila:** její jediná zarážka byla
   v **ROUTERU** a mířila na pět **jiných** endpointů (`/poll`…`/roadmap/reset`)
   — v jejích **42 červených kontrolách nejsou žádné `T:`/`U:`/`V:`/`W:`**.
   P26 to změřila zarážkou **UVNITŘ HANDLERU** (tři mutace živého zdroje,
   v `try/finally` a s ověřením hashe před i po):
   `/task` → **9 červených `T:`** (mj. `T: /task odpoví 200`),
   `/game` → **6 červených `U:`**,
   `/game/active` → **5 červených `V:`** —
   a kontrolní `A: /tick odpoví 200` zůstala **pokaždé zelená**.
   **Poučení: „test endpoint volá" se dokazuje zarážkou V HANDLERU, ne
   v routeru** — routerová zarážka zapne i kontroly, které s handlerem nesouvisí.
2. **VÁZANÉ HODNOTY SE OPRAVDU MĚŘÍ.** V **KOPII** testu se vypnul záznam
   `bind()` → **12 červených** (T: 5, V: 2), konkrétně ``T: `title` jde do
   INSERTu`` a ``V: do DB jde `active = 0` (ne 1)``. Kdyby test tvrdil jen
   **tvar** SQL (`log`), zůstaly by zelené — přesně past „přítomnost ≠ chování".
3. **NÁLEZ P25-K JE PRAVDA A JE OPRAVENÝ.** Verze měřidla z `HEAD` čte
   **1 řádek Hxx** (`HANDOFF.md`), živá po opravě **99** (1 + 98
   z `_archiv/HANDOFF-HISTORIE.md`) → zelená byla **nad 1 % rozsahu**.
   Oprava: zdroje se **odvozují** (ne zapečený seznam), **vypisují se po
   souborech**, počítá se i rozsah **mimo** ně (**139** řádků v **7** zmrazených
   kopiích — záměrně se nečtou, jinak by se týž nález počítal víckrát, past
   H93/H98) a **prázdný rozsah je `NEMĚŘENO` (`exit 1`)**.
4. **MĚŘIDLO MĚLO LŽIVÝ POPISEK.** `ov-g-neovereno.py` tvrdil „hledám
   `NEOVĚŘENO` **ve sloupci Stav**" — **tabulky Hxx žádný sloupec `Stav`
   nemají** (2 buňky v `HANDOFF.md`, 3 v archivu: `# | Nález | Doklad`).
   Hledalo se **kdekoli na řádku**, takže by chytilo i **CITACI** („bylo
   NEOVĚŘENO, dnes APLIKOVÁNO"). Dnes je takových řádků **0** (naměřeno ve
   všech **9** souborech s tabulkou Hxx) — ale popisek je opravený a rozpad na
   buňky se vypisuje.
5. **ČÍSLA §55 SEDÍ — VŠECHNA.** Znovu naměřeno **spuštěním**, ne čtením:
   `p25-a --plne` **53/0** · `p25-b-mutace` **27/0** · `test-tick-offline`
   **146/0** · `tick-mutace` **20 vrat / 41/0** · `g3` **49 bran** ·
   `p24-b-mutace` **17/0** · `handoff-kontrola-uplnost` **83/83** ·
   `kronika-kontrola` **SEDÍ**.
6. **JEDNO ČÍSLO NESEDÍ — A JE ZE ZADÁNÍ, NE Z §55.** Zadání P26 §2.3 tvrdilo
   `over-dokumentaci.py -> 67 kontrol`; **živé měření je 64/0**. Příčina je
   **naměřená, ne odhadnutá**: brána přičítá **+1 za každé volání, jehož CESTA
   obsahuje „skills"** (frontmatter skillu); commit `92aa80a` (optimalizace KB)
   přesunul **tři** bloky z `SKILLS/orchestra` do `PROVOZ`/`BRANY_HRY`, takže
   `52 + 15 = 67` se změnilo na `52 + 12 = 64`. **Není to ztráta pokrytí**
   (obsah se přesunul s blokem) — je to **číslo bez svého běhu** (past
   `AGENTS.md`). Zadání je opravené a měřidlo P26 to číslo teď **hlídá**.
7. **ZADÁNÍ P25 BYLO ZASTARALÉ VE STAVU.** Tvrdilo „práce P25 je v pracovním
   stromě (necommitnutá)" a `HEAD = origin/main = 92aa80a`; **živě** bylo
   `HEAD = ef58327` (P25 svou práci **commitla**) a `origin/main..HEAD = 1`.
   **Hlavička zadání je SNAPSHOT, ne stav.**
8. **NEÚSPĚŠNÝ BĚH MĚŘIDLA VYPADÁ JAKO NÁLEZ.** Můj vlastní přepínač `--vystup`
   čtl `args` v bloku `__main__`, kde **není** (je lokální v `main()`) →
   `NameError` → měřidlo končilo **`exit 1` i s 0 chybami**. Odhalil to až
   **diferenciál** v `p26-b-mutace.py`. **Poučení: verdikt se čte z ČÍTAČE, ne
   z exit kódu** — a `exit != 0` není totéž co „našlo vadu".
9. **VLASTNÍ ÚPRAVA SEZNAMU TIŠE SMAZALA DVĚ POLOŽKY.** Při přidávání sond P26
   do `PRESKOCIT` (`p20-d-doklady.py`) jsem **přepsal řádek s `p24-sonda-site.py`
   a `p24-sonda-m2.py`** → z `PRESKOCIT` **vypadly**. Chytila to **cizí brána**
   `p25-a-overeni.py` A6 („sondy nejsou v PRESKOCIT dávky") — přesně to, k čemu
   nezávislé měřidlo je. **Poučení: seznam se PŘIDÁVÁ, nepřepisuje.**
10. **ZASTARALÝ INVENTÁŘ SE NEDEKLARUJE — a shodí ho i JEDEN NOVÝ SOUBOR.**
    Naměřeno ostře: po přegenerování inventáře stačilo **přidat jeden `.txt`**
    do `_analyza/` a `n1-over-inventar` spadl (`exit 2`); v `g3` se pak
    `C2: mutace N1` ocitl v „brány bez čítače" (správně odmítá měřit nad
    zastaralým inventářem). **A druhý, dražší důvod:** otisk vstupů
    (`KOREN_REPA = {"orchestra": WS, "games/uo-shadows": HRA}`) počítá **I DRUHÉ
    REPO** — takže **zápis souběžné session do hry zneplatní inventář uprostřed
    běhu**. Náprava je vždy **přegenerovat jako POSLEDNÍ krok** a doklady
    pojmenovat podle vylučovacího vzoru (`_analyza/*-vystup.txt`, který
    `ARTEFAKT_RE` vylučuje z otisku).
11. **SANDBOX ZNOVU ODEMKL ZÁPIS PODPROCESŮM — a tentokrát to ZAMRZLO.**
    Podproces nešel zapsat do **žádného** podadresáře workspace; `git fetch`
    padal na `.git/FETCH_HEAD: Permission denied` a sonda nad `_analyza`
    **čekala** (žádný `PermissionError`, jen ticho), dokud ji nástroj nepřesunul
    na pozadí. `write` (harness) přitom do podadresáře zapsal. Pomohlo
    **přepnutí session na plný přístup** — **stav prostředí, ne vada skriptu**
    (skill `dsh-prostredi` §4e).
12. **DO HRY ZAPISOVALA SOUBĚŽNÁ SESSION.** Mezi 15:50 a 16:02 +02:00 přibyly
    v `uo-shadows` **tři commity** (`6796188`, `43a2004`, `125b062`,
    **nepushnuté**) a netrackovaný `_acl-recovery/`. **Důsledek pro měření:**
    `p24-a-overeni.py` má proto **99/3** (tři červené `A8`: HEAD ≠ `44dd454`,
    strom není čistý, 3 nepushnuté commity) místo dřívějšího **99/1** — a to
    **není vada měřidla**: A8 měří **živý stav hry** (P25 to zapsala jako
    „dobová kotva"). **Na práci té session se nesahalo.**
13. **DVA GATE SE VYLUČUJÍ — naměřeno, ne odvozeno.** `zadani-kontrola.py`
    vyžaduje, aby **kotva zadání = živý `HEAD`** (jinak hlásí „zadání je
    zastaralé"), ale `p25-b-mutace.py` vyžaduje **ČISTÝ pracovní strom**
    (jinak svou kontrolou „živé soubory zůstaly BEZ mutací" vykáže **moje
    legitimní necommitnuté záznamy jako mutanty**). **Obojí současně nejde:**
    po commitu se `HEAD` posune a kotva zadání přestane sedět. Naměřeno v P26
    dvakrát (`p25-b` → 27/**1** se dvěma necommitnutými soubory; po commitu
    zase 27/**0**). **Řešení zvolené P26:** doklad i `p25-b` se měří na
    **čistém** stromě (commit `d451905`) a hlavička zadání se doplňuje
    **NEcommitnutá** — proto zůstává `NEXT-SESSION-INSTRUKCE.md` v pracovním
    stromě jako jediná změna. Kdo pustí `p25-b` před commitem, uvidí tuhle
    falešnou červenou — **není to vada kódu**.

### 56.3 Živý stav při zápisu (7. 10. 2026, ~16:2x +02:00)

```
orchestra: HEAD ef58327 · origin/main 92aa80a · nepushnutých commitů 1 (práce P25)
hra:       HEAD 125b062 · origin/main 932dc6f · nepushnutých 3 (SOUBĚŽNÁ session,
           15:50/15:58/16:02) · strom není čistý (netrackovaný `_acl-recovery/`)
živá služba: /health → ok=true ready=1 running=0 games=1 · targets[0] forge.ok=false,
             selhani_v_rade=20, poslední běh run_number 323 (failure, 12:16:33Z)
             /tick → spusteno: 0 úloh; watchdog: 0 ohlášeno (prah 3)
brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0
           (naměřeno po přegenerování inventáře; viz nález 10 výše)
p24-a:     99/3 — všechny tři červené jsou `A8` (dobový stav hry), 99/2 pokud
           souběžná session svou práci pushne
```

### 56.4 Co čeká na tebe (uživatel)

- **PUSH — rozhodnutí uživatele.** P26 **commitla, nepushla**; `origin/main..HEAD`
  bude **2** (P25 + P26). P26 měnila **jen `_analyza/` a dokumenty**, žádný
  soubor pod `conductor/**` — **deploy živé služby to tedy nemění** (ověř
  `git diff --name-only origin/main..HEAD`). Cesta zpět: `git reset --soft`.
- **`_acl-recovery/` v `uo-shadows`** je **cizí, netrackovaný** artefakt
  souběžné session (ACL oprava, 15:41). **Nemažu ho** a **necommituju** —
  patří té session.
- **`HANDOFF.md` §6 je ZÁZNAM z 2. 10. 2026**, ne seznam živých bran
  (má předpřesunové cesty `orchestra\tools\…` a čísla 63/12). Autorita je
  `BRANY` v `_analyza\g3-brany.py`.
- **B4 na živé službě** (`/game/active {active:false}` → `games=0`, žádný
  dispatch) — čeká na výslovné **„ano"**, protože **dočasně zastaví orchestra**.

### 56.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p26-a-overeni.py --plne   # A1-A6: zarážky v handleru, vazby, g3
python _analyza\p26-b-mutace.py           # umí to spadnout? 26 kontrol, 0 chyb
python _analyza\ov-g-neovereno.py         # rozsah 99 řádků Hxx, 0 NEOVĚŘENO
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json  # POSLEDNÍ
python _analyza\g3-brany.py               # 49 bran, 1 deklarovaný exit, exit 0
node tools\validate-all.mjs               # VŠE V POŘÁDKU
python _analyza\p25-a-overeni.py --plne   # 53/0
python _analyza\p25-b-mutace.py           # 27/0
python _analyza\p24-a-overeni.py          # 99/3 (A8 = stav hry, 99/2 po pushi)
node tools\test-tick-offline.mjs          # 146/0
python _analyza\tick-mutace.py            # 20 vrat / 41/0
```

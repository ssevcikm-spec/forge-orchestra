# HANDOFF — orchestra: stav po provedení A1–A4 a Z1–Z8

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 2. 10. 2026 · **Poslední session:** `eb127abd` („Hluboká kontrola
a plán úprav") · **Předchozí dvě:** `7cd67c66` (analýza, S31–S37)
a `7db45275` (jazyk v kódu)

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
>
> **⚠ Pro novou session:** **nejnovější stav je §15** (a §15.7 = co zůstává
> otevřené). **§12** odkazuje na zadání `NEXT-SESSION-INSTRUKCE.md`, které
> **plánovací session přepsala pro akční session** — čti **to přepsané**.
> **Výzva k ověření v §7.2 je SPLNĚNÁ** — její
> výsledek je v **§7.5**. Nerekonstruuj ji znovu.

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
| **A1** `done` jen při `ok && merged` + stav `awaiting_human` | ✅ | `_analyza\a1-a2-over.py` — **19 kontrol**, **3 mutace chyceny** |
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
skener jazyka (23/23) · hl-rizika-jazyka (0/11/0) · A1/A2 (19 kontrol, 3 mutace)
A3 obě kopie · kontrola-diakritiky · over-dokumentaci (63/0) · over-skilly (12/0)
test-eskalace · lint-roadmapa · sjednot-sablonu · check-schema (obě kopie)
tsc --noEmit · testy hry (38 kontrol, 0 selhání) · parser témat (--test)
```

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
| Sloupce D1 (`schema.sql`) | 5 tabulek, **39 sloupců**, českých **0** | serverová vrstva čistá |
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
| `python _analyza\a1-a2-over.py` | **19 kontrol**, `exit 0` |
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

## 8. Vlastní omyly (všech session — tabulka je společná)

> **Autorství:** `7cd67c66` = analýza (S31–S37) · `7db45275` = jazyk ·
> **`eb127abd` = tahle session (provedení A1–A4, Z1–Z8)**.

| # | Kdo | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|---|
| 1 | `7cd67c66` | `sim.mining` má `size_lines` → „vyvracím 1. kolo" | **Nemá** (patří `sim.crafting`); hypotéza 1. kola **platí pro všechny tři** | Přehlédl jsem řádek v tabulce, kterou jsem si sám vypsal |
| 2 | `7cd67c66` | lint o chybějícím `size_lines` **mlčí** | **Varuje** (7× `[5]`), ale `exit 0` a text **zastaralý** | Přečetl jsem jen „vady 1–4: žádné" |
| 3 | `7cd67c66` | Mutační test mé kontroly umí spadnout | **První verze byla slepá** — mutace přes `-replace` s em-dash se **tiše neprovedla** | Diakritika v konzoli |
| 4 | `7db45275` | Druhá session převzala mou §10 „beze změny" | **Převzala jen část** — §8.2 (mandát) jí chybělo | Souběh dvou session nad jedním `HANDOFF.md` |
| **5** | **`eb127abd`** | **„Prompt k hluboké kontrole nedorazil"** | **Byl v repu a byl splněný (9/9)** | **Převzal jsem tvrzení z `HANDOFF.md` §8.4, aniž jsem soubor otevřel.** Označil jsem za chybějící něco, co jsem nezkontroloval |
| **6** | **`eb127abd`** | Cache `origin/main` „drží výsledek na dobu jednoho tiku" | **Modulová proměnná bez TTL** žije, dokud žije izolát — **libovolně dlouho** | Napsal jsem komentář, který tvrdil chování, a **neověřil ho**. Našel to až druhý pohled na vlastní diff, **ne test** |
| **7** | **`eb127abd`** | Kontrola A1 je hotová | **Hlásila falešný poplach na správném kódu** — `if (ok) {` je v souboru 2× a ta první je správná | Test hledal vzorec **bez kontextu**; opraveno vázáním na `UPDATE tasks status='done'` |
| **8** | **`eb127abd`** | Inventář jazyka je měření | **Je to meziprodukt, který zestaral** → hlásil **7 vad, které už byly opravené** | Nástroj si ho generuje jen když **chybí** (nález **N1**) |
| **9** | **`eb127abd`** | Můj skript na zastaralost analýzy měří | **Měl obrácenou podmínku** → hlásil „0 zastaralých" u kódu, který jsem **sám změnil** | Odhalilo se **jen tím, že jsem znal správný výsledek** — „známý chybný případ" z `AGENTS.md` |
| **10** | **`eb127abd`** | Diakritika brána nad novým dokumentem nic nehlásí | **Skutečný výsledek byl `exit=-1`** (artefakt PowerShell pipeline), správně **`exit=1` + jméno souboru** | Měřil jsem přes `Select-String` v pipeline; **musel jsem to změřit znovu pořádně** |
| **11** | **`eb127abd`** | `split("\n")` mi dá počet řádků blobu | **Dal 183 u souboru, který má 182** (končí newline → prázdný prvek na konci). **`AGENTS.md` měl pravdu, skript ne** | Je to **tatáž past**, před kterou `AGENTS.md` varuje u `Measure-Object -Line` (166 vs 182) — a **spadl jsem do ní znovu**, vlastním nástrojem, který měl `AGENTS.md` kontrolovat |
| **12** | **`eb127abd`** | Můj nástroj `ag-over-cisla.py` kontroluje čísla v `AGENTS.md` | **Tvrzená čísla měl NAPSANÁ NAPEVNO** → měřil zdroj a porovnával ho **sám se sebou**; vrácená vada v dokumentu (39 → 32) mu **prošla** (`exit 0`) | **Brána zelená nad dokumentem, který nikdy neotevřela (S27) — v nástroji, který měl S27 hlídat.** Odhalil to až **mutační test** |
| **13** | **`eb127abd`** | `AGENTS.md` tvrdí 32 sloupců → našel jsem chybu v autoritě | **Bylo to 39 a `AGENTS.md` jsem opravil — správně.** Ale **původní závěr „32" jsem nejdřív převzal jako fakt** a označil ho za chybu **až po přeměření**; do té doby to byl jen dojem z jednoho grepu | Postup byl správný, **ale jen náhodou** — kdybych měřil špatně (jako v omylu 11), „opravil" bych správný dokument (přesně ta past, před kterou varuje `AGENTS.md`) |

**Vzor, který je vidět napříč všemi třinácti:** každý omyl vypadal jako
**nález o systému** („chybí zadání", „kód je slepý", „analýza je v pořádku")
a **většina z nich byla vada měření.** A **devět ze třinácti** je z téhle session —
což je přesně to, co `AGENTS.md` předpovídá: *„počítej, že i tvoje první číslo
bude někde mimo."*

---

### 8b. Omyly ověřovací session (2. 10. 2026, podle `PROMPT-NOVA-SESSION.md`)

> **Devět z deseti bylo vadou MĚŘENÍ, ne nálezem o systému** — a **šest z nich
> vzniklo v mnou napsaném testovacím skriptu**. Týž vzor, jen o kolo dál.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **14** | V workspace je git repo → `git status` ochrání dokumenty | **Není.** `fatal: not a git repository`; pod gitem je jen `orchestra\`. `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` **není verzovaný** | Zjistil jsem to **těsně před** spuštěním `hl2-mutace-kontrola.py`, který ten dokument přepisuje na místo a bez zálohy. Kdyby spadl uprostřed, **není ho odkud vzít** |
| **15** | „Nepodařilo se mutovat" = „brána je slepá" | **Dvě různé věci.** Dvakrát se mutace neprovedla a harness to **rovným dílem** nahlásil jako slepou bránu | Slil jsem „vada testovacího skriptu" a „vada brány" do jednoho výsledku → **falešný nález o cizím kódu** |
| **16** | `re.compile("if (ok && merged) {")` hledá ten řetězec | **Hledá `if ok && merged {`** — závorky jsou **skupina**, ne literál. Vzor hlásil „0× v souboru", **přitom tam byl** | Neescapoval jsem vzory ve svých harnessech, **ačkoli skripty projektu to dělají správně**. Stálo to ~8 diagnostických běhů a málem vyrobilo „nález", že se soubory nevracejí |
| **17** | `re.findall` vrací počet shod | **Vrací capture groupy.** U vzoru se skupinou vrátil `['ok && merged']` → `len()` **není** počet shod | Počítal jsem shody funkcí, která vrací obsah. Správně `finditer` |
| **18** | Mutace `filesInOriginMain` → `…XX` změní jméno | **Ne.** `filesInOriginMainXX` **obsahuje** `filesInOriginMain` → skript hledající podřetězec rozdíl nevidí; **já** jsem to nahlásil jako „skript nereaguje" | Nový název musí být **úplně jiný** (`loadMainTree`) — jinak testuješ něco jiného, než si myslíš |
| **19** | Harness na `n8-*` mám hotový napoprvé | **Tři kola oprav:** (a) `spust()` vracel 2 hodnoty, rozbaloval jsem 3; (b) mutace (a2) měnila **totéž** co mutace 1 → **nebyl to nezávislý test**; (c) vzor `exit 1` s 10 mezerami je v souboru **2×** | Každou vadu odhalil **až běh**, ne čtení |
| **20** | Mutace `AGENTS.md` přes `python -c "…'39 sloupců'…"` proběhne | **Neproběhla** — PowerShell rozbil f-string (`SyntaxError`), soubor zůstal netknutý a brána vrátila `exit 0`. **Málem jsem to zapsal jako „brána je slepá"** | Tatáž past, před kterou varuje skill `overovani` §7.9: **mutace, která se tiše neprovede, tvrdí totéž co mutace, která projde.** Odhalilo to jen porovnání hashe před/po |
| **21** | „35 souborů" v bráně diakritiky = 35 dokumentů | **Dva z těch 35 jsou vnořené soubory projektu** (`.forge\check-schema.py`, `.forge\vision-profile.json`) → **33 dokumentů + 2 soubory projektu** | Počet **řádků výstupu** jsem použil jako počet **dokumentů** — dva čítače téhož jména |
| **22** | `Get-Content` přečte UTF-8 dokument správně | **Ne** — načetl ho jako **cp1252**, rozbil diakritiku, vzor nenašel a **tabulka mi vyšla jako 0 řádků** | Vypadalo to jako nález („dokument má prázdnou tabulku"); správně je **16 datových řádků**. Číst přes `[System.IO.File]::ReadAllBytes` + UTF-8 |
| **23** | „9 z 9 bodů" znamená, že analýza je v pořádku | **Neznamená.** Brána projde nad **12,5 % dokumentu** s `\| **Cena** \| X \|` místo obsahu | Nebyl to omyl ve **výpočtu**, ale v tom, **co to číslo tvrdí** — a to je horší druh, protože se neprojeví jako chyba |

**Vzor, který je z těch deseti vidět:** šest (**16, 17, 18, 19, 20, 21**) bylo
v **mém vlastním měřidle** — a **každé vypadalo jako nález o cizím kódu**
(„brána je slepá", „skript nereaguje", „dokument má prázdnou tabulku").
`PROMPT-NOVA-SESSION.md` předpovídá, že *„většina z nich bude vada měření"* —
**potvrdilo se to i na mě.**

---

### 8c. Omyly session 2. 10. 2026 (11:3x–12:0x UTC) — push, granule, N1/N3

> **Tři z pěti vznikly ve MĚŘIDLE a jeden z nich málem vedl ke zbytečnému
> zásahu do herního repa.** Týž vzor, jen o kolo dál.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **29** | **„V herním repu chybí 2 brány, které šablona má"** — a nabídl jsem to uživateli jako možnost k rozhodnutí | **Hra je MÁ.** Kontrolu stínění `class_name` má **uvnitř** kroku parsování (`agent.yml:344–373`) a **navíc** tip na konstanty Godotu 3 (`:337–339`). Drift hlásí „jen v šabloně" proto, že porovnává **jména kroků** — a hra má kroky sloučené a pojmenované jinak | **Přečetl jsem výstup měřidla (drift) jako popis skutečnosti**, místo abych otevřel soubor. Přesně to, před čím varuje `AGENTS.md` („převezmeš tvrzení, aniž soubor otevřeš") — a stalo se to **znovu**, po omylu č. 5 |
| **30** | Oprava driftu „porovnávat `env` po krocích podle pozice" je správná | **Byla slepá na posun:** kopie mají **různý počet kroků** (šablona 21, hra 20), takže indexy nesedí a nástroj hlásil **4 falešné rozdíly** u kroků, které s věcí nesouvisí (`Report při selhání`, `Ulož patch a log`, …) | Odhalil to až **mutační test** — bez něj bych odevzdal měřidlo, které sice chytí hledanou vadu, ale utopí ji v šumu. Opraveno na porovnání **podle klíče**, ne podle pozice |
| **31** | Když jsem viděl, že nový nástroj vrací 4 `CHYBA`, byl jsem hotový s výčtem | **Nebyl jsem:** musel jsem rozlišit **příčinu** — tři selhání jsou **pre-existující** (dokázáno spuštěním téhož nástroje nad čistým `be41964` v `git worktree`), jedno je **sandbox** (`PermissionError WinError 5` na přesměrovaném tempu), a `test-cooldown.py` je **červený správně** (měří vadu S12) | Málem jsem je shrnul jako „brány neprošly" — což by bylo tvrzení o cizím kódu, které jsem neměl čím doložit |
| **32** | „Přesun `FORGE_ATTEMPT`" je jednoduchý `edit` | **Čtyři editace za sebou nic neopravily** — tool hlásil úspěch, ale výsledek byl pořád rozbitý (překlep „nesp uštěna", závorka na špatném místě). Opravil to až **skript, který po zápisu ověří syntaxi** (`node --check`) | **Tatáž past jako u V1** („čtyřikrát jsem upravoval kontrolu, kterou jsem sám přidal") — a poučení je stejné: **ověřuj VÝSTUP, ne návratovou hodnotu nástroje** |
| **33** | Když mi podagent poslal „C2 HOTOVO", mohl jsem se zeptat, co našel | **Musel jsem si to ověřit sám** — a jeho klíčový nález (`player.gd:40` obsahuje řetězec, který test zakazuje, takže po dodání `move()` test spadne) jsem **nezávisle potvrdil mutací** (59/0 → 60/1) | Není to omyl, je to **nález**: dva nezávislé pohledy (čtení kódu vs. spuštění) daly totéž. Kdyby se rozešly, byl by to výsledek — ne chyba |

**Vzor z těch pěti:** **čtyři z pěti** byly v **měřidle nebo v jeho výstupu** —
a **dva vypadaly jako nález o cizím kódu** („chybí brány" → nechybí; „brány
neprošly" → prošly jindy a jinde). A ten první **málem vedl k zápisu do herního
repa podle nesprávného závěru** — zachránilo to jen to, že jsem se zeptal
a uživatel zvolil širší variantu, u které se vada **musela** ověřovat čtením
souboru.

---

### 8d. Omyly PLÁNOVACÍ session 2. 10. 2026 (10:1x–10:3x UTC) — ověření 11 tvrzení

> **Dva z pěti vypadaly jako nález o cizím kódu a jeden málem odešel jako
> „červená brána".** Týž vzor, jen o kolo dál — a znovu to, co předpovídá
> `AGENTS.md`: *„počítej, že i tvoje první číslo bude někde mimo."*

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **34** | **„Brána `check-schema.py` je červená i v šabloně"** (`exit 1`, „chybí `assets/spec.json`") | **Není to vada.** `validate-all.mjs:194` ji pouští **nad hrou** (`games/uo-shadows`), ne nad šablonou — ta žádné assety nemá a mít nemá. Nad hrou vychází `exit 0` | Spustil jsem nástroj s vlastním argumentem, aniž jsem se podíval, **jak ho pouští ten, kdo ho zná**. Falešný nález o cizím kódu — a odhalilo to až dohledání volání, ne test |
| **35** | Můj mutační skript `p7-mutace-pojistky.py` je hotový | **Dvakrát spadl na `sha(<bytes>)`** — vypisoval `AttributeError` **po** provedené mutaci. Kdybych věřil návratové hodnotě, vypadalo by to jako „mutace se nepovedla" | Chyba byla v **mém** nástroji, ne v měřeném. Zachytil to `assert`, že se text skutečně změnil (past z `overovani` §7.9) — bez něj bych měl „nález o bráně", který je o mně |
| **36** | Když brána padá i s `TMP` ve workspace, blokuje sandbox i workspace | **Neblokuje.** Skutečná příčina je `os.mkdir(p, 0o700)` (což `tempfile.mkdtemp()` používá) → adresář, do kterého nejde zapsat ani ho smazat. Prokázalo to až **oddělené** měření `0700` vs. výchozích `0777` | Měřil jsem **dvě věci naráz** (přesměrovaný temp + chování nástroje) a první vysvětlení jsem málem zapsal jako nález o prostředí |
| **37** | Pro sondy stačí `_analyza\tmp-sandbox` | **Zůstaly v něm 3 adresáře, které NEJDE smazat** (`c700`, `schema-test-*`, `probe2-*`) — `Remove-Item`, `cmd /c rd`, `takeown` i `icacls` hlásí „Access is denied" | Sondoval jsem past **tím, že jsem ji vyrobil** — a to, že po sobě nezůstane uklizeno, je její součást. Zapsáno jako nález (P3) i s tím, že po sobě zanechává odpad |
| **38** | „9 výskytů `.has(`" ze zadání je měření | **Je jich 10** (`scripts/*.gd`) a **18** v celém herním repu. Zadání vypisuje 2 vady + 6 Dictionary/Array + 2 komentáře = **10**, ale součet uvádí **9** | Sečetl jsem položky, které zadání samo vyjmenovalo — rozpor je **uvnitř zadání**, ne v kódu. (Týž postup jako u „32 sloupců": číslo bez postupu se nedá ověřit.) |
| **39** | Do nového zadání můžu napsat, **jak vypadají znaky rozbitého kódování** (jako ukázku vzoru, kterým jsem dokument kontroloval) | **Brána diakritiky to ohlásila jako vadu dokumentu** — `NALEZENY CHYBY (1)`, přesně podle `AGENTS.md` („ukázku rozbitého kódování popisuj **slovem**"). Opraveno slovy | Znal jsem to pravidlo a **přesto ho porušil** — protože jsem psal o *nástroji*, ne o *textu*. A je to zároveň důkaz, že brána ten nový dokument **otevřela** (což „exit 0" netvrdí) |

**Vzor z těch pěti:** **pět z pěti** byly v **měřidle nebo ve mně** — a **dva
vypadaly jako nález o cizím kódu** („brána je červená" → není; „sandbox blokuje
i workspace" → neblokuje). U **34** to zachránilo jen to, že jsem si našel, jak
nástroj pouští někdo jiný.

---

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

## 10. Session 2. 10. 2026 (dopoledne) — PR #28/#29/#30/#31

**Zadání:** „Projdi volné PR v UO shadows a jsou-li ok, mergni je.“
**Odpověď: nebyly ok — a zelená CI to neukazovala.** Vše ověřeno spuštěním.

### 10.1 Hotovo (doloženo spuštěním, ne čtením)

| Co | Stav | Doklad |
|---|---|---|
| #30 `mining.gd` | sloučil **uživatel ručně** v 07:40 (`d72bf4d`) | `merged_by` v detailu PR |
| #28 `save.gd`, #29 `hud.gd` | změřeno → vadné → **opraveno** → sloučeno (`eba7315`, `6235a99`) | `_analyza\over-main-po-merge.py` — `main` == měřené soubory, bajt po bajtu |
| #31 `mining.gd` (nový PR) | oprava → sloučeno (`0435d3e`) | tamtéž |
| `main` hry | `0435d3ea5a`; CI #98 **41 kontrol, 0 selhání**; `release.yml` #64 `success`; Pages `last-modified 07:57:22` | `_analyza\ci-cekej.mjs`, `zjisti-pages.mjs` |
| roadmapa hry | srovnána se skutečností (7 úprav: 5 + 2 zpřesněné po novém měření) | `_analyza\srovnej-roadmapu.py`, `_analyza\zpresni-roadmapu.py` — každá náhrada 1×, JSON validní |
| **funkční testy** | `tests/run_tests.gd`: místo `has_method` se staví **zkušební registr `component(id)`** a opravdu se volá `save`, `load`, `update`, `gather`; **41 → 59 kontrol** | `_analyza\dopln-testy.py`; **mutační test**: s vrácenými vadnými soubory **13 selhání, `exit 13`** (`_analyza\mutace-testu.py`) — se starými testy byly tytéž soubory zelené |
| větev `priprava/srovnani-roadmapy` | **PUSHNUTA do `main`** (fast-forward `0435d3e..4b0fc8c`, tři commity: rebase `d0bf4f9`, necommitnuté změny + roadmapa, testy); v klonu zůstává jako ref | CI #99 `success` (v logu `59 kontrol, 0 selhání`), `release.yml` #66 na `head:4b0fc8c`, Pages `last-modified 08:16:20` |

Srovnání roadmapy: `sim.mining` dostal `done` (PR #30), `persist.save`/`ui.hud`
už neříkají „PR NENÍ sloučené“, `world.map` a `entity.player` **přiznávají, že
jejich práce v `main` není**.

### 10.2 Co bylo vadné (a proč to CI nevidělo)

| Vada | Naměřeno (Godot 4.7.2) |
|---|---|
| `hud.gd:21` `margin_left` — **Godot 4 zná `offset_*`** | `_ready()` se přeruší → label se nikdy nepřidá (0 dětí) → **HUD není vidět vůbec** |
| `hud.gd:33,64` `has_property()` | `SCRIPT ERROR` při každém hráči ve scéně |
| `save.gd` bere služby ze skupin `attributes`/`skills`/`economy`/`world` | žádná není založená → `save()` zapíše 35 B (jen pozici hráče) a **vrátí `true`** |
| `mining.gd:17` `node.has()` + `/root/Skills` | `SCRIPT ERROR` (Godot 3 API); oba `/root/*` uzly neexistují |

**Proč zelená:** testy volají jen `has_method(...)` a soubor, který se nenačte,
se **tiše přeskočí** (`if load(...) != null:`). V logu to vypadá jako měření:
`[test] OK save.gd poskytuje save/load`, `39 kontrol, 0 selhání`.

### 10.3 Nové nálezy (zapsané v `OTEVRENA-TEMATA.md`)

1. **Brány měří PŘÍTOMNOST metod, ne chování** → do `tests/run_tests.gd` patří
   funkční kontroly se stub registrem; chybějící soubor, který součástí hry být
   MÁ, má **selhat**, ne se přeskočit.
2. **Roadmapa vede `done` u práce, která v `main` není:** `world.map` —
   `scripts/world.gd` **není smazaný, je přesunutý do `_retired/`** (`c651368`,
   záměrně: nesl *druhé číslo mřížky*, což byl konflikt; izo projekce správně
   přešla do `level.gd`) — ale **uzly surovin, `gather()` a respawn nikde
   nejsou** (`level.gd` je nemá). A `entity.player`: PR #25 změnil **jen
   `project.godot`**; `move()`, inventář ani `die()` nebyly nikdy v žádné větvi
   — a **jiné komponenty je už volají**: `assist.gd` čte
   `hp/max_hp/mana/max_mana/target`, `economy.gd` volá `add_item/remove_item`.
3. **Smlouva komponent chybí v zadání `engine.shell`** — komponenty berou
   služby z `component(id)` na **rodiči**.
4. **Pasti prostředí** (dopsány do skillu `dsh-prostredi`): Godot 4.7.2
   **ignoruje `--user-data-dir`** → `user://` jde do `%APPDATA%`, což sandbox
   blokne a zápis **tiše selže**; funguje `$env:APPDATA`. `git clone` v sandboxu
   padá (`sh.exe … signal pipe`) → použij `git worktree`.

### 10.4 Pozor při čtení cizích čísel

- Merge #28/#29/#31 provedla **tato session** přes PAT uživatele, takže GitHub
  ukazuje `merged_by: ssevcikm-spec` — **není to ruční kliknutí člověka**
  (u #30 naopak ruční bylo).
- První pokus ověřit `main` vrátil `0 B` → to bylo **selhané měření** (špatná
  cesta ke gitu v jednořádkovém volání), ne chybějící soubor. Skript
  `over-main-po-merge.py` teď prázdný blob hlásí jako „MĚŘENÍ NEPROBĚHLO“.
- **Vlastní omyl z téhle session (do tabulky omylů patří):** `git log
  --diff-filter=D -- scripts/world.gd` hlásí ten soubor jako **smazaný**, i když
  ho commit jen **přesunul** (`{scripts => _retired}/world.gd`). Do dokumentů
  jsem proto nejdřív napsal „smazán“ — a bylo to nepřesné. **Autorita je
  `git show --stat` (s `-M`), ne `--diff-filter=D`.** Opraveno tady, v ledgeru
  i v roadmapě hry.
- **Lokální klon hry je po pushi „pozadu, ale nic v něm není unikátní“**
  (ověřeno `git diff --stat origin/main`: jen chybějící soubory). Srovná se
  jedním příkazem — `git fetch && git reset --hard origin/main` — a nic se
  přitom neztratí (necommitnuté změny jsou součástí `main`).

---

## 11. Stav pro session, která čekala na push (2. 10. 2026, 08:35 UTC)

**Odpověď na „je to pushnuté?“: herní repo ANO a klon je srovnaný; orchestra NE.**

| Repo | Stav | Co to znamená |
|---|---|---|
| `games\uo-shadows` | `origin/main` = lokální `HEAD` = **`aad1c8d`**, strom čistý, `0/0` | **Nic nečeká.** Nemá smysl pushovat znovu ani znovu slučovat PR (otevřených je **0**) |
| `orchestra` | `origin/main` = `525d45b`, lokální `HEAD` = **`3a2e691`** (`1 ahead`) + **10 změněných souborů** | **Jediné, co ještě není pushnuté** — včetně `conductor/src/index.ts` (A1–A4). Deploy conductora je samostatné rozhodnutí (O3) |

**Co se stalo s tím, na co session čekala:**

- Nepushnutý commit `d0bf4f9` je v `main` jako **`7bbb62b`** (rebase; obsah
  stejný, **hash jiný** — starý hash nepushovat). Necommitnuté změny z klonu
  jsou v **`2858c7e`**, dvě zpřesnění roadmapy + **funkční testy** v **`4b0fc8c`**,
  **tři nové granule** v **`aad1c8d`**. Klon byl srovnán na `origin/main`
  (`reset --hard`, předem ověřeno, že v pracovním stromu není nic unikátního).
- CI na `main`: #96, #98, #99, #100 — všechny `success`; v posledním logu
  **`59 kontrol, 0 selhání`**. `release.yml` #67 na `head:aad1c8d`, Pages
  `last-modified 08:29:04`.

**Co je v herním repu nového (kdo by na tom stavěl, ať počítá s tím):**

- **Tři nové granule** (`world.nodes`, `entity.player.api`, `persist.save.state`);
  `engine.shell` čeká na první dvě. Nová granule se nevydá hned — platí
  `RETRY_HOURS` (invariant 15), takže ~3 h zpoždění **není** porucha.
- `scripts/save.gd`, `hud.gd`, `mining.gd` opravené: služby berou z **registru
  `component(id)` na rodiči**, Godot 4 API, a `save()` už **nevrací `true`** nad
  neuloženým stavem.
- `tests/run_tests.gd`: **funkční** kontroly se zkušebním registrem
  (**41 → 59 kontrol**); s vrácenými vadami hlásí **13 selhání**.

**Co se změnilo v dokumentaci** (aby to nikdo nevrátil ani neduplikoval):

- `AGENTS.md`: 4 nová pravidla (`done` je tvrzení; brána, která se ptá na
  přítomnost; `git log --diff-filter=D` hlásí i přesuny; design dokument musí
  nést tvar dat) + nový dokument v tabulce „Kam pro co“.
- `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` (**nový**): podklad pro revizi skillu
  `game-developer` a pro přepis designu UO-Shadows; **§7 je pokyn, jak ho
  budovat** (každá session přidává naměřené případy).
- `OTEVRENA-TEMATA.md`: +3 témata, nové téma „DOKONČIT REVIZI SKILLU + PŘEPSAT
  DESIGN“; **13 otevřených / 23 uzavřených**.
- Skilly (mimo workspace): `game-developer` — odkaz u §2 + oddíl „Příprava na
  revizi tohoto skillu“; `dsh-prostredi` — past s `--user-data-dir` (Godot ho
  ignoruje, použij `$env:APPDATA`) a `git clone` → `git worktree`.
- `orchestra\tools\kontrola-diakritiky.py` (uncommitted): nový dokument přidán
  do pevného seznamu — jinak by ho brána nikdy neotevřela (vada S27).

---

## 12. ZADÁNÍ PRO NOVOU SESSION (2. 10. 2026, 10:4x UTC)

**→ `NEXT-SESSION-INSTRUKCE.md`** — samostatný dokument (konvence `*ZADANI.md`),
protože `AGENTS.md` říká, že zadání pro novou session patří do vlastního souboru,
ne do handoffu. Tenhle handoff zůstává **stav**; tamto je **co dělat**.

**Stav po ověřovací session (měřeno 2. 10. 2026, 10:4x UTC):**

| Co | Naměřeno |
|---|---|
| Herní repo | `HEAD` = `origin/main` = **`aad1c8d`**, strom **čistý**, `0/0`. Otevřených PR **0** z 31 |
| `orchestra` | `origin/main` = `525d45b`, `HEAD` = **`3a2e691`** (**1 ahead**) + **10 změněných** souborů |
| Conductor | `/health` → `ok: true`, `ready: 3`, `running: 0`; `/failed` **prázdné** |
| `/roadmap` | **16 řádků** — 10 `done`, 6 `queued` |
| Brány | všech 9 spuštěných **`exit 0`** (diakritika, dokumentace, skilly, handoff 83/83, `ag-over-cisla`, `hl-rizika-jazyka`, A1/A2, A3, N8) |

**Tři fronty práce (nemíchat je — zadání je má rozdělené na Úkol A/B/C):**

1. **Provést teď:** opravit **dvě zastaralá tvrzení v tomhle handoffu** (řádky
   **140** a **384** tvrdí, že PR #28–#30 jsou `open` — jsou **sloučené** 07:40–08:02;
   a řádek **27** posílá novou session na §7.2, která je **splněná**) ·
   rozhodnout **push `orchestra`** (= O3) · ověřit, že nové granule vydal
   conductor **a že jejich běhy nejsou zelené nad nefunkčním kódem** ·
   opravit **V1/V2/V3** · **N1**, **N3**.
2. **Zadokumentovat:** výsledky do handoffu, vlastní omyly do §8b, nové dokumenty
   do `kontrola-diakritiky.py` (nový `NEXT-SESSION-INSTRUKCE.md` je tam už zapsaný).
3. **Připravit pro plánovací session:** přepis `games\uo-shadows\docs\ARCHITEKTURA.md`
   podle `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` §5.1 — a **prototyp tvaru smlouvy**
   na jednom skutečném případě (`scripts\player.gd` / `economy.gd`). **Nedělat
   plánovací session v téže session, která opravuje kód.**

---

## 13. Provedeno 2. 10. 2026 (10:4x–11:3x UTC) — opravy V1/V2/V3 a zastaralých tvrzení

**Zadání:** `NEXT-SESSION-INSTRUKCE.md`. **Provedeno: Úkol A1 (zastaralá tvrzení)
a Úkol A4 (V1/V2/V3).** Úkol A2 (push/O3) a A3 (granule) **čekají na rozhodnutí
člověka** — push nešel provést bez vyžádání.

### 13.1 Co je hotové (doloženo spuštěním)

| Co | Před | Po | Doklad |
|---|---|---|---|
| **A1** zastaralá tvrzení v handoffu | §2.3 a §7.2/8 tvrdily `open` | označeno jako **zastaralé**, s odkazem na §10; §7.2 má hlavičku „SPLNĚNO" | `handoff-kontrola-uplnost.py` → **83/83** |
| **V1** `hl2-kontrola.py` | 9 bodů, jen přítomnost řetězců | **10 bodů** — každá ze 12 sekcí musí mít **≥ 4 řádky a ≥ 200 znaků** | dokument **10/10**; kostry (11,7 % a 12,5 %) **spadnou**; smazaná sekce **spadne** |
| **V2** `a1-a2-over.py` | **19 kontrol**, chytil 2 z 5 mutací | **23 kontrol**, chytí **4 ze 4** | `a1-a2-mutace.py` → `exit 0` |
| **V3** `n8-zastarala-analyza.py` | hledal slovo a jméno | ptá se na **zapsaný stav** (všech 17 zápisů) a na **funkci** (deklarace i volání) | `n8-mutace.py` → **3/3**; porovnává **množinu**, ne počet |

**Všechny brány po opravách: `exit 0`** — včetně obou kalibrací, které teď
správně **selhávají** nad kostrou.

### 13.2 Vlastní omyly při těch opravách (č. 24–28) — každý vypadal jako nález o cizím kódu

| # | Co jsem si myslel | Naměřeno | Jak to vzniklo |
|---|---|---|---|
| **24** | Kontrola „konstanta TTL se používá" funguje | **Falešný poplach na správném kódu** — hledal jsem jen `expiruje =`, ale v kódu je `expiruje:` (vlastnost objektu) | Napsal jsem vzor pro přiřazení do proměnné; cache je ale **objektový literál**. Falešný poplach je stejná vada jako slepé místo, jen se hůř hledá |
| **25** | „Nepodařilo se zmutovat" = „brána je slepá" | **Podruhé v téže session.** Tentokrát u `filesInOriginMain` (2 výskyty) | *Tatáž chyba jako omyl **15***. Neopravil jsem **třídu** chyby, jen její výskyt |
| **26** | Přejmenování konstanty `ORIGIN_MAIN_TTL_MS` → `…CACHE_MS` je vada | **Není.** Po přejmenování **obou** výskytů dělá kód totéž — brána, která projde, má **pravdu** | Do seznamu mutací patří jen **skutečné vady**. „Sémanticky neutrální" změna není vada a hlásit ji jako slepou bránu je **falešný nález** |
| **27** | `re.search` mi dá, jaký stav se do D1 zapisuje | **Dal `done`** (první výskyt), ne `awaiting_human` — a tvrzení 4 tím vyšlo jako „aktuální", i když zastaralé **je** | V `index.ts` je **17 zápisů stavu**; na „jaké stavy se zapisují" se musí ptát `findall`, ne `search`. Odhalil to až **známý správný výsledek** (5 zastaralých), ne test |
| **28** | Sekce dokumentu skončí na dalším nadpisu | **Ne pro tuhle kontrolu** — sekce začínající podsekcemi (`### 3.1`, `### Varianta A`) vyšla jako **prázdná**, protože jsem přestal na **jakémkoli** nadpisu | Falešný poplach na správném dokumentu: brána prošla body 1–9 a **spadla na 10** — kdybych ji „opravil" podle sebe, smazal bych obsahovou kontrolu, kterou jsem sám přidal |

**Vzor, který je z těch pěti vidět:** **pět z pěti** byly v **mém měřidle** —
a **čtyři z nich vypadaly jako nález o dokumentu nebo o bráně** („sekce je
prázdná", „brána je slepá", „stav tam není"). Přesně to, co předpovídá
`AGENTS.md`: *„počítej, že i tvoje první číslo bude někde mimo."*

**A poučení, které stojí za zapsání zvlášť:** **opravovat měřidlo je stejně
náchylné k chybě jako psát ho.** U V1 jsem *čtyřikrát* upravoval kontrolu, kterou
jsem sám právě přidal — a **třikrát** z toho byl falešný poplach. Co to chytilo:
**znalost správného výsledku** („12 sekcí má obsah") a **kalibrace na kostře**.
Bez nich bych „opravil" správný dokument.

---

## 14. Provedeno 2. 10. 2026 (11:3x–12:0x UTC) — push, granule, N1/N3, nástroje

**Zadání:** uživatel, čtyři body: *push orchestra* · *ověřit nové granule (A3)* ·
*N1 a N3 (A5)* · *rozhodnout, které z 8 nových nástrojů patří do
`validate-all.mjs`* · *C pro plánovací session*.

### 14.1 Push orchestra — ✅ provedeno a nasazeno

| Co | Naměřeno |
|---|---|
| Push | `525d45b..be41964`, `origin/main` = **`be41964`**, `rev-list --count` = **0** |
| Commity | `2df4ece` (Z1–Z8, 4 soubory) · `be41964` (A1–A4 + N3, 6 souborů) |
| **Deploy** | **`#31 completed/success` na `head:be419647d`** (10:23:48 UTC) → **A1–A4 jsou ŽIVÉ** |
| Živý stav | `/health` → `ok: true`, `ready: 5`, `running: 0`; `/roadmap` 16 řádků |

Nástroj: **`_analyza\a3-kontrola.mjs`** (nový) — ptá se na **konkrétní commit**,
ne na „poslední deploy"; jinak by zelená mohla být z deploye před pushem.

### 14.2 A3 — nové granule: ✅ práce v `main` NENÍ, a brána je nezavolá

**Odpověď na zadání je „ne" u všech tří** — a je to **správný stav**, protože
jsou `queued` a ještě nebyly vydány. Podrobně (surový záznam:
`_analyza\a3-brany-novych-granuli.md`):

| Granule | Práce v `main`? | Zavolala ji brána? |
|---|---|---|
| `world.nodes` | **NE** — `scripts/world.gd` v `main` **není** (`c651368` ho přesunul do `_retired/`); `main.json` má **4 markery** (`spawn`/`coin`/`exit`), **0 surovinových**. `git log --all -S"func gather"` nic | **NE** — `mining.gd` volá `world.gather(cell)` na **atrapě `TestSvet`**, která jen počítá volání. Reálný `world.gd` se neinstancuje |
| `entity.player.api` | **NE** — `player.gd` (2353 B) má `_step`, `_physics_process`, `flash()`; **`move()`, `hp`, `max_hp`, `mana`, `inventory`, `die()` nikdy v žádné větvi** (`git log --all -S"func move("` = prázdný) | **NE** — blok kontrol je podmíněný `if player.has_method("move")` a **tiše se přeskakuje** |
| `persist.save.state` | **NE** — `save()` v `main` je verze z PR #28 (3825 B); **`snapshot()`/`restore()` nikdy nikde** | **NE** — kostra v testech má `Attributes`, `Skills`, `Economy`, `Player`; **`World` v ní NENÍ**, takže se snapshot nevolá |

**Jak je to doložené (a je to nová metoda, ne čtení kódu):** do **kopie** hry se
vložil **třířádkový `move()`** — nic víc, žádné `hp`/`inventory`/`die()` — a testy
přešly z **`59 kontrol, 0 selhání` (exit 0)** na **`60 kontrol, 1 selhání`
(exit 1)**:

```
[test] FAIL player volá izo projekci přes world, ne přes level
[test] 60 kontrol, 1 selhání
```

**Co to znamená:** rozdíl je **jediná kontrola, která se dosud vůbec
nespustila**. A je to **falešný poplach na legitimním kódu** — zakazuje řetězec
`level.iso_position`, který `scripts/player.gd:40` obsahuje odjakživa, a
`level.gd` `iso_position` **nemá**, takže ta větev je mrtvá. **Brána o izometrii
netvrdí nic; měří přítomnost řetězce.** (Nezávisle na tom našel totéž
i podagent pro Úkol C — čtením kódu.)

> **A1 to naštěstí řeší z druhé strany:** `done` se teď zapíše jen při
> `ok && merged`, takže se nemůže zopakovat případ `world.map`/`entity.player`,
> kdy byla granule `done`, a práce v `main` nebyla.

**Stav conductoru k tomu:** `/roadmap` má `world.nodes` i `entity.player.api`
`queued` a v `/tasks` k nim **není žádná úloha** — `persist.save.state`
v `/roadmap` **není vůbec** (16 řádků; čeká na `world.nodes` + `entity.player.api`).
Zpoždění není porucha (`RETRY_HOURS`, invariant 15).

### 14.3 N1 — ✅ doloženo spuštěním: nástroj čte ZASTARALÝ inventář

`_analyza\n1-over-inventar.py` → **`VYSLEDEK: N1 JE PRAVDA`**, `exit 0`:
inventář (506 892 B) byl z 08:01, po přegenerování má 516 455 B; nástroj pak
ohlásil `ohlášeno` jako „VRÁTILO SE", **ačkoli na disku už není**. Uklid ověřen
(sha256 inventáře i zdrojového souboru zpět).

**Doporučení (rozhodnutí je na člověku):**
- **Nástroj si inventář generuje sám, když je starší než vstupní soubory**
  (jinak měří jiný strom, než jaký je na disku),
- **a vypíše jeho stáří**; při chybějícím inventáři **nesmí mlčet zeleně**.

### 14.4 N3 — ✅ VYŘEŠENO: v herním repu byla rotace modelů MRTVÁ

**Nález je hlubší, než jak byl zapsaný** (a to se vyplatilo změřit znovu):

- `FORGE_ATTEMPT` je v obou kopiích **1×** a v obou je na **úrovni kroku**.
- **`env:` na úrovni kroku platí JEN pro ten krok.** V herním repu byl na kroku
  **„Vyber bezplatného poskytovatele LLM"**, ale hodnotu čte
  **`.forge/pick-provider.mjs:129,132`** (`rotateByAttempt(…, FORGE_ATTEMPT)`) —
  a krok **„Spusť agenta"**, ve kterém se pouští i **druhý pokus**, ji neměl.
- **Důsledek:** rotace modelů podle čísla pokusu — tedy přesně to, co mělo
  zabránit opakování téhož modelu — **v herním repu nikdy nefungovala**.
  V šabloně je hodnota na správném kroku.
- **Opraveno a pushnuto:** `games\uo-shadows` `aad1c8d..194735d` (`194735d`).
  Změna je **jeden řádek + jeho komentář** (ne kopie celého souboru — hra má
  v `agent.yml` vlastní odchylky, které jsou v pořádku).

**Opraveno i měřidlo, které to nedokázalo vidět** (`kontrola-driftu.mjs`):
`env` se srovnával jako **jeden plochý seznam klíčů** → obě kopie měly
**33 výskytů, 16 unikátních klíčů, množiny SHODNÉ** → přesun klíče na jiný krok
byl **neviditelný** a drift hlásil `OK (struktura)`. Nově se bere
**mapa „klíč → na kterém kroku je"**. Mutačně ověřeno
(`_analyza\n3-mutace-driftu.py`):

| Stav | Drift hlásí |
|---|---|
| opraveno | `jen v šabloně (kroky): …` (známý strukturální rozdíl) — o `env` **ani slovo** |
| vada vrácena | navíc **`env FORGE_ATTEMPT: šablona: Spusť agenta` / `hra: Vyber bezplatného poskytovatele LLM`** |

**A nález o dokumentaci:** komentář v `sjednot-sablonu.py` tvrdil, že
„obě kopie dnes projdou, ale z různých důvodů". **Neprojdou** — nástroj
kontroluje **jen šablonu**, takže o herním repu netvrdí nic. Komentář opraven.

**Co N3 NENÍ (vyvráceno měřením):** herní `agent.yml` **nemá chybějící brány.**
Drift hlásí 3 kroky „jen v šabloně", ale hra má kontrolu stínění `class_name`
**uvnitř** kroku parsování (`:344–373`) a **navíc** tip na konstanty Godotu 3
(`:337–339`). Je to **strukturální rozdíl, ne chybějící funkce** — kdo by slepě
zkopíroval šablonu, o tyhle dvě věci hru **připraví**.

### 14.5 ✅ Rozhodnutí: 4 nástroje do `validate-all.mjs`, ostatní NE

**Zařazeny (nová sekce `L`)** — všechny čtyři jsou **pouze čtoucí**
(`write_text` se v nich nevyskytuje ani jednou):

| Nástroj | Co hlídá |
|---|---|
| `a1-a2-over.py` | `done` jen při `ok && merged`; `owns` proti `origin/main`; cache s TTL |
| `a3-over.py` | `exit 1` v kroku „Když pravidla neprošla" v **obou** `agent.yml` |
| `n8-zastarala-analyza.py` | stárnutí analýzy (tvrzení proti **kódu**, ne dokumentu) |
| `b5-over-tvrzeni.py` | týchž 5 tvrzení **nezávisle** na `n8-*` |

**Nezařazeny** (a proč): `a1-a2-mutace.py`, `a3-mutace.py`, `n8-mutace.py`,
`ag-mutace.py`, `n1-over-inventar.py`, `hl2-kostra-test.py`,
`hl2-kostra-kalibrace.py` — **schválně přepisují soubory a vrací je**; spouštět
je z validátoru znamená riskovat pracovní strom. Patří k ručnímu ověřování.

**Pojistka, která je v tom schválně:** sekce `L` u každého nástroje **nejdřív
ověří, že jeho zdroj neobsahuje zápis**; kdyby ho někdo přidal, validátor nástroj
**odmítne spustit a řekne to**. Ověřeno mutačně: 4 čtoucí → `PUSTIT`,
7 zapisujících → `ODMITNOUT`, `ag-over-cisla.py` → čtoucí.

> **⚠ ALE — a to je důležitější než samo zařazení:** `orchestra` má
> v `.github\workflows\` **jen `deploy.yml`**. **Žádné CI tenhle validátor
> nespouští** (jediné zmínky o `validate-all` jsou v dokumentaci).
> `validate-all.mjs` je **ruční nástroj vývojáře**: potřebuje PAT
> (`orchestra\.secrets\`), `.env` s `FORGE_URL`/`FORGE_SECRET`, naklonovanou hru
> a absolutní cesty na tuhle stanici. Sekce `L` je proto **výrazně užitečnější
> než dřív, ale pořád ji musí někdo spustit** — sama se nespustí.
>
> **Skutečné brány jsou v `agent.yml`** (běží u každé granule) a v CI hry
> (`.forge/*` v `orchestra\repo\.github\workflows\ci.yml`). Tam patří rozhodnutí
> o **automatickém** hlídání.

### 14.6 Brány — stav po všech změnách

`exit 0`: a1-a2-over (23 kontrol) · a3-over (obě kopie) · n8-zastarala
(5 z 7 zastaralých) · **validate-all sekce L** (4/4) · diakritika (37 souborů) ·
over-dokumentaci (63/0) · over-skilly (12/0) · ag-over-cisla (5+2, 0 rozchodů) ·
handoff-uplnost (83/83) · testy hry **59 kontrol, 0 selhání**.

**Známé červené (NEOVĚŘENÉ v této session, všechny PRE-EXISTUJÍ — ověřeno
spuštěním téhož nástroje nad čistým `be41964` v `git worktree`, výsledky
identické):** `test-check-schema.py` (exit 1) · `vision.test.mjs` (exit 1) ·
`test-cooldown.py` (exit 1 — **správně**, měří vadu S12 → B1) ·
`baseline.py testy` (**sandbox**: `PermissionError WinError 5` na
přesměrovaném tempu — past z `dsh-prostredi` §4, ne vada) ·
`kontrola-driftu.mjs` (exit 1 — známý strukturální rozdíl kroků).

### 14.7 Úkol C — ✅ podklad hotov (v session, která NEOPRAVOVALA kód)

`_analyza\C-PODKLAD-SMLOUVY.md` (36 854 B). **Dělal ho podagent** — tedy
nezávisle na téhle session, která zároveň opravovala kód (pravidlo `AGENTS.md`).
Obsahuje: prototyp smlouvy `Player` (typy, výchozí hodnoty, **kdo to volá**
s čísly řádků, 5 spustitelných přijímacích kritérií včetně negativních, hranice
granule) · tabulku **13 granul bez `size_lines`** · dva naměřené případy ·
**co v designu chybí** (14 bodů) · tabulku **32 tvrzení → příkaz → výsledek**.

Integrita: `ARCHITEKTURA.md` má **shodný SHA-256** před i po
(`356F060B…B25BF3CB5`), `git status --porcelain` v herním repu prázdný.

**Nálezy nad zadání (nejdůležitější):**
- **Past, kterou je potřeba opravit ZÁROVEŇ s granulí:** `player.gd:40` obsahuje
  řetězec, který test zakazuje → **jakmile granule dodá `move()`, test se zapne
  a spadne na stávajícím kódu**. (Táž věc, kterou jsem naměřil mutací v §14.2.)
- **Trojitý rozpor o izometrii** (`roadmap.json:90` vs `:231` vs
  `run_tests.gd:838–840` vs `roadmap.json:220`) — a `level.gd` `iso_position`
  **nemá**, takže větev je mrtvá.
- **`acceptance: ["tests","wiring"]`, ale agent NESMÍ měnit `tests/`** — kdo ten
  test napíše, design neřeší.
- **`check-wiring.py` tuhle smlouvu neověří** — neobsahuje ani jeden výskyt
  `player`/`has_method`.
- **D1 má 16 řádků na 21 granul** — chybí `core.attributes`, `entity.item`,
  `sim.offline`, `engine.shell`, `persist.save.state`.
- **`combat.gd:19,25` volá `has()`** (Godot 3 API — táž vada, na které spadl
  `mining.gd`). **Nespouštěno, jen čteno** → kandidát na ověření.

### 14.8 Co je z otevřených bodů nově VYŘEŠENÉ

- ~~**A2** (push / O3)~~ → **pushnuto a nasazeno** (`#31 success`, §14.1).
- ~~**A3** (granule)~~ → **změřeno**; odpověď je „práce v `main` není a brána ji
  nezavolá", doloženo mutací (§14.2).
- ~~**N1**~~ → doloženo; zbývá rozhodnutí o opravě nástroje (§14.3).
- ~~**N3**~~ → **opraveno v obou roli** (kód hry + měřidlo driftu), §14.4.
- ~~**Zařazení nástrojů do `validate-all.mjs`**~~ → **rozhodnuto a zavedeno**
  (§14.5), včetně pojistky proti zápisu.
- ~~**C** (podklad pro plánovací session)~~ → hotovo (§14.7).

### 14.9 Co zůstává otevřené (a čí je to rozhodnutí)

1. **N1 — opravit nástroj?** (§14.3) Návrh je hotový, změna kódu ne.
2. **`test-check-schema.py` a `vision.test.mjs` jsou červené** a **nikdo
   neví proč** — nejsou v žádném seznamu otevřených bodů. Pre-existují.
   → **nový nález, patří prošetřit.**
3. **`combat.gd` volá `has()`** (Godot 3 API) — kandidát na stejnou vadu, jakou
   měl `mining.gd`. Neověřeno spuštěním.
4. **Brány nových granul jsou slepé** (A3): testy nevolají `hp`/`inventory`/
   `die()`/`snapshot()`/`restore()` a `world.gd` testují na atrapě.
   → patří do `tests\run_tests.gd`, ale **ten agent měnit nesmí** → musí to
   udělat člověk nebo nová granule s `owns: tests/`.
5. **O3** (zbytek fáze B), **O10**, **O5–O8** — beze změny (§2.2).
6. **`_analyza\` není verzovaný** — 4 zařazené brány i podklad C v něm žijí
   mimo oba repozitáře. Kdo je chce mít v gitu, musí je přenést.

### 14.10 Jak pokračovat (změna postupu předávání)

**Nové: `PREDAVANI-SESSION.md`** — postup, jak volat další session ve **dvou
krocích** (plánovací → akční), se **šablonami promptů ke zkopírování**,
„Hotovo znamená" pro každou session a **naměřenými pastmi předávání**.

**Proč to vzniklo:** dosavadní předání bylo „přečti `HANDOFF.md` a pokračuj",
což mělo **dvě měřené vady** — (1) **nikdo neověřoval práci předchozí session**
(a ta se třikrát mýlila; vždy to našel až druhý pohled nebo mutační test),
(2) zadání bylo psané pro agenta, ne pro člověka bez znalosti kódu.

**Zásada, na které to stojí:** *nová session nezačíná tím, že by věřila
handoffu — začíná tím, že se ho pokusí vyvrátit.* Handoff je **svědectví**,
ne důkaz.

**`PROMPT-NOVA-SESSION.md` je odteď historický** (jeho Krok 1 je splněný 12/12,
bod 8 v něm neplatí) — má v hlavičce varování a odkaz sem. **Nespouštět znovu.**

### 14.11 Změna postupu předávání na žádost uživatele (2. 10. 2026, 12:0x UTC)

**Uživatel upozornil na vadu, kterou jsem přehlédl — a byla naměřená:**
kdyby se psala zadání pro **oba** kroky dopředu, **akční session by dostala
zastaralé podklady**. Doklad: `NEXT-SESSION-INSTRUKCE.md` tvrdil „pushnuto
`525d45b..be41964`" a **o hodinu později** byl `HEAD` **`5a8f91a`** — o **tři
commity** dál; dokument měl 6 přeškrtnutých (už neplatných) odstavců.

**Přijaté řešení (uživatelovo, lepší než moje):** **řetěz vždy jen o JEDEN krok
dopředu** — každá session na konci **přepíše `NEXT-SESSION-INSTRUKCE.md`** jako
zadání pro session, která přijde, a **vloží do chatu prompt ke zkopírování**.

**A k tomu jedna věc, kterou uživatelův návrh sám neřeší:** ani zadání psané
„na konci" není aktuální ve chvíli, kdy ho někdo čte. Proto **není řešením
aktuálnost, ale to, že si zadání nese, PROTI ČEMU bylo měřeno** (commit + čas),
a session **prvním krokem ověří, že to ještě platí**. Když ne, **přeměří**
a zapíše nález — zadání se nezahazuje.

**Nové nástroje:**
| Nástroj | Co dělá |
|---|---|
| `_analyza\zadani-kontrola.py` | porovná tvrzený commit z hlavičky zadání se **živým stavem**; `exit 1` = zadání zastaralé. **Mutačně ověřeno 4/4** (`zadani-mutace.py`) |
| `_analyza\zadani-mutace.py` | mutační test toho nástroje (2 mutace + kontrola návratu souboru) |

> **Vlastní omyl při psaní té kontroly (do §8c patří):** první verze hledala
> **první sha v hlavičce** — a když se tvrzený commit změnil, našla sha z řádku
> „Zkontrolováno při:" (který zůstal) a hlásila **`exit 0` nad zastaralým
> zadáním**. Odhalil to **mutační test**. A při jeho psaní se **mutace sama
> tiše neprovedla** (PowerShell rozbil zpětné apostrofy) — což vypadalo jako
> slepá kontrola, ale byla to neprovedená mutace. Zachytil to **`assert`**.
> Dva různé omyly, oba by odešly jako „hotové".

### 14.12 Nový nález: `combat.gd` je rozbitý a **nikdo ho nikdy nezavolal**

**Naměřeno spuštěním** (sonda v `_analyza`, uklizena):
`combat.gd:19,25` volá `attacker.has("zbran")` / `defender.has("armor_rating")`,
ale **`Node.has()` v Godotu 4 neexistuje**:

```
SCRIPT ERROR: Invalid call. Nonexistent function 'has' in base 'Node'.
```

**Ověřeno zvlášť, aby to nebyl falešný poplach:**
`Node.has()` → **false** · `Dictionary.has()` → **true** · `Array.has()` → **true**.

> **⚠ Zásadní rozlišení, které zachraňuje před falešným poplachem:**
> `grep '\.has('` najde v herním repu **9 výskytů** a **jen 2 jsou vada**.
> `skills.gd:9,13`, `level.gd:81,221,280`, `game.gd:257` jsou
> **`Dictionary.has()` / `Array.has()`** — v Godotu 4 **fungují** a opravovat
> je by byla chyba. Dva výskyty v `mining.gd` jsou **komentáře**.

**Proč to nikdo neviděl:** `combat.gd` **není v `game.gd` instancovaný** (nikdo
ho nevolá) a testy se ptají **jen na přítomnost metody**
(`_check(cb.has_method("resolve"))`) — **nikdy `resolve()` nezavolají**.
Táž třída jako `mining.gd` (PR #31) a `hud.gd` (PR #29).
**Zadáno k rozhodnutí** (`NEXT-SESSION-INSTRUKCE.md` §3.1).

---

## 15. Ověření práce session `eb127abd` — plánovací session 2. 10. 2026

**Co tenhle oddíl JE:** **výsledek nezávislého ověření** 11 tvrzení ze zadání
(`NEXT-SESSION-INSTRUKCE.md`, verze z 12:11) — **měřením, ne čtením**.
Zadání psala session, která sama opravovala kód, takže podle `AGENTS.md`
**není nezávislý pohled**.

**Proti čemu je měřen:** `orchestra` = `5a8f91a` · `uo-shadows` = `194735d` ·
oba **pushnuté a čisté** (`origin/main..HEAD = 0`, `git status --porcelain`
prázdný). **Čas měření:** 2. 10. 2026, 10:1x–10:3x UTC (hodiny stanice ověřeny
proti `Date` z GitHub API — shoda na sekundu).

### 15.1 Všech 11 tvrzení — výsledek

| # | Tvrzení | Verdikt | Příkaz a výstup (zkráceně) |
|---|---|---|---|
| **1** | `orchestra` pushnutý a nasazený (`be41964`, deploy #31) | **PROŠLO s výhradou** | `node _analyza\a3-kontrola.mjs be419647dd…` → **`exit 1`**, ale jen proto, že předaný sha **už není hlavní commit** (`GitHub main = 5a8f91a69 vs be419647d`). Věcná část prošla: `#31 completed/success head:be419647d 2026-10-02T09:23:48Z`, `poslední změna conductor/src/index.ts = be419647d`, `OK kód conductora z main je nasazený`. Pozdější commity (`b2e1ee1`, `5a8f91a`) deploy nepotřebují — nemění `conductor/**`. **Pozor: sekce D téhož nástroje měří neexistující endpoint (P1 níž).** |
| **2** | `uo-shadows` pushnutý a nasazený (`194735d`) | **PROŠLO** (tři kroky důkazu) | `rev-list --count origin/main..HEAD` = **0** · `zjisti-pages.mjs` → `release.yml #68 completed/success head:194735d` · HTTP HEAD `index.png` → **`200`, `last-modified Fri, 02 Oct 2026 09:30:47 GMT`** (push 09:29:49Z) |
| **3** | N3 opravena: `FORGE_ATTEMPT` na kroku „Spusť agenta" | **PROŠLO** | `python _analyza\n3-kde-je-forge-attempt.py` → **v obou kopiích** `kroků s env: FORGE_ATTEMPT: ['Spusť agenta']`, `env JOBU: False` |
| **4** | Měřidlo driftu to umí chytit | **PROŠLO** | `n3-mutace-driftu.py --vrat` → `kontrola-driftu.mjs` vypíše `env FORGE_ATTEMPT: šablona: Spusť agenta / hra: Vyber bezplatného poskytovatele LLM`; `--obnov` → hash `615AE624D72E1D175734C7D1…` **zpět**, `git status` hry čistý |
| **5** | A3: práce nových granul NENÍ v `main` | **PROŠLO** | `python _analyza\a3-zaznam.py` → `main`: **`59 kontrol, 0 selhání`** (`exit 0`); se sentinelem `move()`: **`60 kontrol, 1 selhání`** (`exit 1`) |
| **6** | N1 platí (nástroj čte zastaralý inventář) | **PROŠLO** | `python _analyza\n1-over-inventar.py` → **„N1 JE PRAVDA"**; po testu inventář i zdroj **vráceny bajt po bajtu** (sha256 shodné) |
| **7** | 4 nástroje v `validate-all.mjs` + pojistka proti zápisu | **PROŠLO** (sekce L **4/4**) | `node orchestra\tools\validate-all.mjs` → sekce L: 4× `OK … exit=0`. **Pojistka ověřena mutací** (`p7-mutace-pojistky.py`): slovo `write_text` v komentáři `b5-over-tvrzeni.py` → `CHYBA … NEBYL spuštěn — zdroj obsahuje zápis`, problémů **4 → 5**; hash po obnově shodný. **Ale celek validátoru je `exit 1` se 4 problémy** (§15.2 P6) |
| **8** | Brány jsou zelené (`HANDOFF.md` §14.6) | **PROŠLO s výhradou** | Všech 10 položek ověřeno znovu, každá `exit 0`, u každé zjištěno, **co otevřela** (§15.1a). **Tři čísla v §14.6 přitom zestarala** (§15.3) |
| **9** | Tři červené brány jsou PRE-EXISTUJÍCÍ, ne regrese | **PROŠLO, ale z JINÉHO důvodu** | `git worktree add --detach _analyza\scratch-orch HEAD` (čistý strom, 0 změněných) → **obě brány se chovají identicky**. Příčina ale **není** „pre-existující vada": brány **neproběhly ani jednu kontrolu** (P2) |
| **10** | Čísla v `AGENTS.md` sedí | **PROŠLO** | `python _analyza\ag-over-cisla.py` → `5 v pořádku / 2 historická / 0 ROZEŠLO SE / 0 NENAŠLA SE`, `exit 0`. **Pokrytí je 5 + 2 z 105 řádků s číslem** (viz P5) |
| **11** | Handoff je úplný | **PROŠLO** | `python _analyza\handoff-kontrola-uplnost.py` → **83/83**, `exit 0` |

**Co otevřela která brána (past S27 — „exit 0" to netvrdí):**
`kontrola-diakritiky` **40 souborů** · `over-dokumentaci` **63 kontrol** ·
`over-skilly` **12 skillů** · `kontrola-driftu` **12 souborů, 1 známý rozdíl** ·
`hl-rizika-jazyka` **0 očekávaných / 11 přejednaných / 0 vrácených**
(nad inventářem z 08:01 — viz P5) · `a1-a2-over` **23 kontrol** ·
`ag-over-cisla` **5 + 2** · `handoff-uplnost` **83 klíčů** · `hl2-kontrola`
**10/10** · `test-neanglicky-skener` **23 kontrol** · `lint-roadmapa`
**21 granul** (13 bez `size_lines`) · testy hry **59 kontrol** · `tsc --noEmit`
`exit 0` · `test-eskalace`, `sjednot-sablonu`, `parser témat` `exit 0` ·
`check-schema` **nad hrou** `exit 0`.

> **Ani jedno z 11 tvrzení se nevyvrátilo jako nepravdivé.** Ale **pět věcí
> zadání nevědělo** a jedno z nich (P5) má **termín**.

### 15.2 Co zadání nevědělo (pět nálezů, každý spuštěním)

| # | Nález | Naměřeno | Důsledek |
|---|---|---|---|
| **P1** | **`/tasks` NENÍ endpoint** — vrací `HTTP 200` s rozcestníkem služby (`{"service":"forge-conductor","endpoints":[…]}`). `a3-kontrola.mjs` z něj čte `tasks` → vždy prázdné → hlásí „(žádná úloha)" | `/roadmap`: `world.nodes → task_id 145`, `entity.player.api → 146`, obě **`task_status=ready`**; `/queue` je vypisuje (#145, #146, vznik 08:28:54, `attempts=0`). Nástroj: `p10-endpoints.mjs`, `p11-granule-ulohy.mjs` | **§14.2 tvrdí nepravdu** („v `/tasks` k nim není žádná úloha"). Prázdný seznam vypadal jako naměřená nula. Věta „zpoždění není porucha" vysvětlovala něco, co nenastalo |
| **P2** | **Dvě „červené brány" nikdy neproběhly** | `test-check-schema.py` → `PermissionError [WinError 5]` **před první kontrolou**; `vision.test.mjs` → `Error: spawn EPERM` (`execFile`, `:147`), **0 kontrol**. V čistém worktree na `5a8f91a` totéž. `baseline.py testy` padá stejně | Nejsou to vady kódu → **neopravovat je**. Patří spustit **mimo sandbox**; do té doby je nelze nazvat ani zelenými, ani červenými |
| **P3** | **Mechanika P2 je reprodukovatelná:** `os.mkdir(p, 0o700)` → adresář, do kterého **nejde zapsat ani ho smazat** (ani `icacls`); `os.mkdir(p)` (výchozích `0777`) funguje. `tempfile.mkdtemp()` používá `0700` | Změřeno v `_analyza\tmp-sandbox`: `c700` (nepřístupný) vs. `c777` (funguje) | Past **není v žádném skillu**. A zanechává **neumazatelný odpad** (3 adresáře zůstaly; `Remove-Item`, `cmd /c rd`, `takeown`, `icacls` → „Access is denied") |
| **P4** | **Časy označené „UTC" nesedí** | Deploy #31 = `2026-10-02T09:23:48Z` (GitHub), §14.1 píše „**10:23:48 UTC**"; hlavička starého zadání tvrdí „**11:5x UTC**", soubor byl zapsán v **10:11 UTC** (mtime). Hodiny stanice jsou přitom správně (`Date` z GitHubu = lokální UTC) | Čas je součástí každého tvrzení o stavu; „číslo bez zdroje" se nedá ověřit ani vyvrátit |
| **P5** | **Testy nových granul mají zaručeně červený výsledek** — kontrola `tests/run_tests.gd:838–839` zakazuje řetězec, který `player.gd:40` obsahuje, **a prompt granule `entity.player.api` ten kód přikazuje zachovat** („ZACHOVEJ stávající `_step` … a `_physics_process`") | `a3-zaznam.py`: `59/0` → **`60/1`**; `p8-static.py`: `hp` 0×, `inventory` 0×, `die(` 0×, `snapshot` 0×, `restore` 0× v **kódu** testů. Úloha **#146 je `ready`** | Splnit prompt a projít testem se **vylučuje**. Opravit **test**, ne `player.gd:40` (je to legitimní fallback) |
| **P6** | **`validate-all.mjs` je jako celek `exit 1` se 4 problémy** (2× prostředí, 1× prostředí `baseline`, 1× **správně červený** `test-cooldown` = vada S12), ale §14.6 ho má v seznamu „exit 0" jako „validate-all sekce L (4/4)" | `node orchestra\tools\validate-all.mjs` → `✗ NALEZENO 4 PROBLÉMŮ` | Sekce L zelená je, **celek ne** — a reader to z §14.6 nepozná |

### 15.3 Čísla, která zestarala (nebyla nepravdivá — změnil se stav)

| Kde | Tvrdí | Naměřeno teď | Čím |
|---|---|---|---|
| §14.6 | diakritika **37 souborů** | **40** | `kontrola-diakritiky.py` (3 dokumenty přibyly commitem `5a8f91a`) |
| §6 | lint **10× `[5]`**, **13 z 18** | **11× `[5]`**, **13 z 21** | `lint-roadmapa.py games\uo-shadows` (3 nové granule) |
| §6 | `hl2-kontrola` **9/9** | **10/10** | `_analyza\hl2-kontrola.py` (§7.6 to už uvádí správně) |
| §7.6 | `AGENTS.md` **80 řádků s číslem / 16 s jednotkou** | **105 / 22** | `_analyza\ag-mutace.py` — **týž postup, který to číslo vyrobil** |
| §14.3 | inventář po regeneraci **516 455 B** | **519 381 B** | `_analyza\n1-over-inventar.py` |
| §5 | `/failed` = 1 úloha (#141) | **`/failed` prázdné**; #141 je v `/queue` jako `blocked` | `p9-live.mjs` |
| §6/§7.2 | „zastaralých 5 z 7" | **5 z 7** (beze změny) | `n8-zastarala-analyza.py` |

**Historická čísla se nepřepisují** — patří k nim **čas**, ne přepis
(`AGENTS.md`).

### 15.4 Co se ověřit NEDALO (přiznaná mez)

- **Skutečný výsledek `test-check-schema.py` a `vision.test.mjs`** — v sandboxu
  se nespustí (P2). „Nevím, co by řekly" **není** totéž jako „jsou červené".
- **Budoucnost granul #145/#146** — je v rukou conductora a rozhodnutí člověka.
- **Tři různé `vision.test.mjs` (N12)** a **`--resolution 480x270`** — neměřeno
  (první potřebuje běh mimo sandbox, druhé dva běhy Godotu).
- **Kvalita obsahu `C-PODKLAD-SMLOUVY.md`** — ověřena jen existence, velikost
  a hash `ARCHITEKTURA.md`; obsah jsem neposuzoval (to je práce pro plánovací
  session nad designem).

### 15.5 Nástroje vzniklé touhle session (v `_analyza\`, mimo CI)

| Soubor | Co měří |
|---|---|
| `p7-mutace-pojistky.py` | mutační test **pojistky proti zápisu** v sekci L (vloží `write_text` do komentáře a vrátí soubor) |
| `p8-static.py` | statické kontroly k tvrzením: `.has(`, kdo volá `combat`, `world.gd`, markery `main.json`, metody `player.gd`, co volají testy, kolik nástrojů zapisuje, čísla v `AGENTS.md` |
| `p9-live.mjs` | živý stav conductoru + **`Date` z GitHubu** (kontrola hodin) |
| `p10-endpoints.mjs` | co vrací `/tasks` (rozcestník) a co `/queue` (úlohy) |
| `p11-granule-ulohy.mjs` | mapování **granule → úloha v D1** (`/roadmap` × `/queue`) |

**Žádný z nich není v CI ani ve `validate-all.mjs`** — ruční měřidla, stejný
stav, před kterým varuje `NEXT-SESSION-INSTRUKCE.md` §2.6.

### 15.6 Co tahle session změnila ve workspace (a co vrátila)

- **Nic necommitnuto, nic pushnuto.** `git status --porcelain` v obou repech
  **prázdný** před i po.
- **Dočasné mutace, všechny vráceny a ověřeny hashem:** `b5-over-tvrzeni.py`
  (pojistka), `games\uo-shadows\.github\workflows\agent.yml` (drift),
  `_analyza\_inventar.json` a `orchestra\tools\pridej-eskalaci.py` (N1),
  `AGENTS.md` (`ag-mutace.py`), `conductor\src\index.ts` (A1/A2 mutace).
- **Nové soubory:** `PLAN-DALSI-KROK.md` (plán), `_analyza\p7..p11` (měřidla).
- **`_analyza\scratch-orch`** (dočasný worktree) **odstraněn**;
  `git worktree list` v orchestře má zpět jen hlavní strom.
- ⚠ **Zůstaly 3 neumazatelné adresáře** v `_analyza\tmp-sandbox`
  (`c700`, `schema-test-*`, `probe2-*`) — přímý důsledek P3. Jsou to **já**, kdo
  je vyrobil (omyl **37** v §8d), a nejde je smazat bez širšího oprávnění.

### 15.7 Co zůstává otevřené (a kdo to rozhodne)

**Všechno z §14.9 zůstává v platnosti**, pokud není níž řečeno jinak.
Nově nebo zpřesněně:

1. **Falešný poplach v `tests/run_tests.gd:836–840`** (P5) — **blokuje vydání
   `entity.player.api` (#146)**. Rozhoduje **člověk: kdo smí psát `tests/`**.
2. **`combat.gd`** — opravit, ale nejdřív **rozhodnout tvar dat** (nikdo v repu
   neposkytuje `hodnota("Dex")` i `hodnota("boj_na_blizko")` zároveň). Rozhoduje
   člověk + design.
3. **Dvě brány, které nikdy neproběhly** (P2) — spustit **mimo sandbox**
   (rozšířené oprávnění). Rozhoduje uživatel (schválení běhu).
4. **N1** — oprava návrhu hotová, změna kódu **ne** (a má nový důsledek: zapisující
   nástroj pojistka sekce L odmítne).
5. **`a3-kontrola.mjs` čte neexistující endpoint** (P1) — opravit měřidlo.
6. **O3, O10, O5–O8** — beze změny (§2.2); `PLAN-DALSI-KROK.md` §2 D5 k nim
   přidává doporučení.
7. **`AGENTS.md` a `HANDOFF.md` nejsou v žádném repu** (kořen workspace není git
   repo) — „trvalá pravidla" a „stav" nemají historii. Nové zjištění, patří do
   plánu separace.
8. **`_analyza\merge-scratch` je zaregistrovaný worktree herního repa**
   (detached na `aad1c8d`) + 12 dalších pomocných složek v `_analyza\` — úklid,
   není priorita.

**Rozhodnutí téhle session (co dělat a v jakém pořadí):**
**`PLAN-DALSI-KROK.md`** — včetně toho, co **NEDOPORUČUJE** dělat.
**Zadání pro akční session:** `NEXT-SESSION-INSTRUKCE.md` (přepsané,
s hlavičkou proti zastaralosti).




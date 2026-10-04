# Hloubková analýza orchestra — druhé kolo: „stav, který si systém hlásí sám"

> **Co tenhle dokument JE:** analýza. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

> ## ⚠ TOTO JE SNAPSHOT K 2. 10. 2026 05:45 UTC — NE POPIS SOUČASNOSTI
>
> **Přečti tenhle rámeček dřív než tabulky níž.** Analýza popisuje stav **kódu
> v čase měření**. Dne **2. 10. 2026 v 08:38–08:52 UTC** provedla jiná session
> plán `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` (**A1–A4**) a **kód změnila**.
> Tím se **5 tvrzení téhle analýzy rozešlo s kódem** — naměřeno spuštěním
> `_analyza\n8-zastarala-analyza.py`:
>
> | Tvrzení analýzy | Dnes (po A1–A4) |
> |---|---|
> | §3.1/⑪ `tasks.status='done'` **není ukotveno** | **je** — `ok && merged` (A1) |
> | §3.2 `auto-merge` při neúspěchu **skončí zeleně** | **skončí `exit 1`** (A3) |
> | §⑪/2 `roadmap.status='done'` se **neověřuje** | **ověřuje se** proti `origin/main` (A2) |
> | §⑪/15 „PR sloučen" se bere z `conclusion` (S33) | bere se z `merged_at`; nový stav `awaiting_human` |
> | §3.2 gate: lint o chybějícím `size_lines` **nehlásí** | **hlásí** (A4a) |
>
> **Dvě tvrzení naopak PLATÍ dál** (kontrolní vzorky, A1–A4 se jich nedotkly):
> `done_note` je mrtvé pole (0 čtenářů) a `runs.artifacts` je mrtvý sloupec.
>
> **Co z toho plyne — a je to ironie, kterou stojí za to vidět:** analýza
> *„stavu, který si systém hlásí sám"* se **sama stala takovým stavem**.
> Kdo ji čte jako popis dneška, **čte jiný stav, než jaký je.** Proto:
>
> - **Tabulky níž ber jako historické měření** (a je to jejich správná funkce —
>   bez nich by nešlo změřit, co se opravilo).
> - **Současný stav** ber z `HANDOFF.md` a z `git diff`, ne odsud.
> - **S37 a A4** jsou jediné, co analýza sama označila za „dodatek".
>
> **Není to vada dokumentu** — je to jeho **datum spotřeby**, a tenhle rámeček
> ho přiznává. Přesně to `AGENTS.md` žádá: *„ke každému číslu patří postup
> a čas."*

**Měřeno:** 2. 10. 2026, 05:39–05:45 UTC · **Analytik:** session, která orchestra
nepsala, neopravovala ani neanalyzovala v prvním kole.
**Podklady:** `_analyza\HLOUBKOVA-MERENI-3.md` (surová čísla s příkazy a časy).
**Výchozí bod:** `ANALYZA-HLOUBKOVA-ORCHESTRA.md` (1. kolo, 1 624 řádků) — revidován, ne opsán.
**Značky:** `měřeno` (spustil jsem) · `kód` (`soubor:řádek`) · `odvozeno` · `nevím`.
**Provedeno z ní:** A1–A4 (`IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md`) — 2. 10. 2026, 08:38–08:52 UTC.


---

## ① Verdikt v pěti větách

> **1.** Orchestra je systém, který si o svém stavu **vede dvojí účetnictví**:
> soubor `roadmap.json` a databáze D1 tvrdí totéž dvakrát, ale **nikde se
> neporovnávají** — a od 1. 10. se rozešly.
> **2.** Všechna tři `done` u nesloučených granul vznikají **jedním řetězem**:
> agent pošle `success` hned po vytvoření PR (`agent.yml:565`), gate při
> neúspěchu **neskončí chybou, jen komentuje** (`agent.yml:683-691`), a conductor
> se ptá na `run.conclusion`, **ne na `merged_at`** (`index.ts:365,385`) —
> hodnotu `merged` si sice přečte, ale **použije ji jen v textu notifikace**
> (`index.ts:409`).
> **3.** Nejde o tři náhody: **13 z 18 granul nemá `size_lines`** a **`done_note`,
> ve kterém si systém sám napsal varování, nečte žádný kód** — systém tedy
> vyrábí tvrzení, o kterých **sám ví, že mohou být nepravdivá**, a nemá jak to
> zjistit.
> **4.** Příčina není „chybí kontrola" — je to **absence protějšku**: každý stav
> (`done`, `status`, `active`, `jobs_done`) žije **jen uvnitř systému** a nemá
> druhou stranu, proti které by se dal ukotvit.
> **5.** Doporučuji **variantu A** (ukotvit každý stav v gitu/PR — 1–2 dny) a
> **odmítnout variantu B** (jednotný registr stavů), protože ta přidává třetí
> zdroj pravdy k dvěma, které se už rozešly.

*(Přepsáno na konci v §13 — verdikt se **změnil**: viz tam.)*

---

## ② Co je orchestra — mapa

```
                        ┌──────────────────────────────────────────┐
   ČLOVĚK ──ručně──►    │  roadmap.json  (v repu HRY)              │
                        │  ← SOUBOR JE AUTORITA                    │
                        │    10× done:true, 2× done_note "POZOR"   │
                        └───────────────┬──────────────────────────┘
                                        │ čte (GitHub Contents API, index.ts:567)
                                        ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  CONDUCTOR  (Cloudflare Worker, orchestra\conductor\src\index.ts)  │
   │  1368 řádků · cron * * * * * · 17 endpointů                        │
   │                                                                    │
   │   roadmapTick()  ──►  D1 tabulka `roadmap` (CACHE)                 │
   │                         14 řádků · 11 done                         │
   │                                                                    │
   │   pollRuns()  ◄── čte run.conclusion z GitHub API                  │
   │        │              (NE merged_at!)                              │
   │        └──► tasks.status='done'   (index.ts:386)                   │
   │        └──► roadmap.status='done' (index.ts:389)                   │
   │        └──► notifikace: "(sloučeno automaticky)" ← JEDINÉ použití  │
   │                        proměnné `merged`   (index.ts:409)          │
   └────────────────────────┬───────────────────────────────────────────┘
                            │ dispatch
                            ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  GitHub Actions  .github/workflows/agent.yml  (691 řádků)          │
   │                                                                    │
   │   job agent ──► job pull-request ──► ┌─ report.mjs success ──► D1   │
   │                                      │   ★ HOTOVO UŽ TADY          │
   │                                      │   agent.yml:565             │
   │                                      └─ PR otevřen                    │
   │                                                                    │
   │   job auto-merge (SAMOSTATNÝ, needs: [agent, pull-request])        │
   │     gate:  ok=0 při velké změně  →  ★ exit 0, job ZELENÝ           │
   │     ci:    poll 30×20 s na "Testy a build"                          │
   │     merge: if ok==1 && ci==ok  →  gh pr merge                       │
   │     else:  ★ jen `gh pr comment`, ŽÁDNÝ exit 1  (agent.yml:683-691) │
   └────────────────────────────────────────────────────────────────────┘
                            │
                            ▼
   ┌────────────────────────────────────────────────────────────────────┐
   │  CO JE SKUTEČNĚ VIDĚT                                              │
   │  origin/main/scripts: 9 .gd souborů                                │
   │  save.gd  NENÍ · hud.gd  NENÍ · mining.gd  NENÍ                    │
   │  PR #28, #29, #30 — všechny OPEN, merged_at = null, state = clean  │
   └────────────────────────────────────────────────────────────────────┘
```

**Tři místa, kde se tvrzení a skutečnost rozcházejí — a nikde mezi nimi není
spoj:**

| tvrzení | kde je zapsané | skutečnost | kdo to porovnává |
|---|---|---|---|
| `tasks.status='done'` | D1 (task #136, #139, #140) | PR open | **nikdo** |
| `roadmap.status='done'` | D1 `/roadmap` | práce není v `main` | **nikdo** |
| `done: true` | `roadmap.json` | totéž | **nikdo** |
| `done_note: "POZOR…"` | `roadmap.json:183,194` | pravda | **nikdo** (0 čtenářů v kódu) |

---

## ③ Inventura vlastností

### 3.1 Stavy a kde žijí (jádro druhého kola)

**Pět tabulek D1, 39 sloupců** (`orchestra\conductor\schema.sql`), **plus šest
stavů mimo D1**:

| # | stav | kde žije | kdo zapisuje | kdo čte | ukotveno proti vnějšímu faktu? |
|---|---|---|---|---|---|
| 1 | `tasks.status` | D1 `tasks:15` | **16 míst** v `index.ts` | 26 míst | **NE** — jen `run.conclusion` (stav běhu, ne práce) |
| 2 | `tasks.attempts` | D1 `tasks:16` | `:823, :869` | `:392, :708` | ne |
| 3 | `runs.status` | D1 `runs:29` | 8 míst | 11 míst | **ANO** — `run.conclusion` z GitHub API (`:365`) |
| 4 | `roadmap.status` | D1 `roadmap:60` | 8 míst | 4 místa | **jen částečně** — `:389` z `conclusion`; `:601` ze **souboru** |
| 5 | `roadmap.updated_at` | D1 `roadmap:62` | 9 míst | 3 místa | ne — a **nese dva významy** (stav i selhání) |
| 6 | `workers.jobs_done` | D1 `workers:49` | **jen `:1351`** | **jen `:995`** (`SELECT *`) | **NE — čistě sebehlášené** |
| 7 | `workers.jobs_failed` | D1 `workers:50` | **jen `:1351`** | **jen `:995`** | **NE — čistě sebehlášené** |
| 8 | `games.active` | D1 `games:77` | `:1012, :1032` | `:445, :897` | **NE** — nikdo neověří, že `repo` existuje |
| 9 | `runs.artifacts` | D1 `runs:35` | `:1315` | **0 čtenářů** | — **mrtvý sloupec** |
| 10 | `done` (granule) | **`roadmap.json`** | `srovnej-roadmap-done.py` (jednorázový) | `index.ts:590, :621` | **NE** — a **přebije** D1 (`:601`) |
| 11 | `done_note` | **`roadmap.json`** | týž skript | **0 čtenářů** | **NE — varování, které stroj nevidí** |
| 12 | `schvalil` | `vision\baseline.json` | `baseline.py:298`, `baseline-poznamka.py:33` | `baseline.py:218,234,395` | **NE** — 272× `agent-init` v jedné minutě |
| 13 | `_ceka_na_lgtm` | `vision\baseline.json` | `baseline-poznamka.py:38` | **0 čtenářů** | **NE — mrtvé pole** |
| 14 | `acceptance` / `provides` | `roadmap.json` | ručně | **0 čtenářů v kódu** | — (první kolo: S22) |

**Odpověď na otázku Q1 ze zadání:** z 39 sloupců D1 je **odvozených 2**
(`runs.status`, `roadmap.status` u cesty `pollRuns` — opírají se o GitHub API),
**čistě opsaných (sebehlášených) 5** (`tasks.status`, `workers.jobs_done`,
`workers.jobs_failed`, `games.active`, `roadmap.status` u cesty ze souboru)
a **1 mrtvý** (`runs.artifacts`). **U žádného neexistuje porovnání s druhým
zdrojem.**

### 3.2 Brány

| brána | co měří | odkud bere vstup | ukotvení |
|---|---|---|---|
| `check-schema.py` | schéma scén | soubory v repu | **17 offline testů, ověřeno mutačně** (jediná doložená) |
| `test-zamek-owns.py` | zámek `owns` | **čte funkci ze zdroje** | ověřeno mutačně |
| gate v `agent.yml:595` | velikost a cesty změny | `max_lines` z granule | **`size_lines` chybí u 13/18 granul → výchozích 60** |
| `ci` v `agent.yml:647` | „Testy a build" | `statusCheckRollup` | poll 30×20 s, pak `ci=timeout` |
| **`auto-merge`** | **nic** | — | **při neúspěchu `exit 0` + komentář** ← jádro S29 |

### 3.3 Rozhraní

- **Conductor → GitHub:** `pollRuns` čte `run.conclusion` (`:365`) a `merged_at`
  (`:375`). **Druhá hodnota se zahodí.**
- **Workflow → conductor:** `report.mjs success` (`agent.yml:565`) — **posílá se
  před** rozhodnutím o sloučení.
- **Soubor → D1:** `roadmapTick` (`index.ts:588-608`) — `done:true` **přebije**
  stav v D1.

---

## ④ Katalog tříd selhání — S31–S37 (pokračuji v číslování)

První kolo skončilo na **S30**. Následuje **sedm nových tříd**.
*(S31–S36 vznikly z analýzy; **S37 je dodatek** — naměřil jsem ho až při psaní
implementačního zadání, kdy jsem si ověřoval tvrzení z §O7.)*

### S31 — `done` vzniká ve chvíli, kdy vznikne PR, ne kdy je práce sloučená

**Kde:** `agent.yml:557-565` (report `success`) vs. `agent.yml:676-691`
(sloučení v **samostatném** jobu).
**Jak se to pozná dnes:** nijak — oba joby skončí `success`.
**Co by to odhalilo:** `done` navázat na `merged_at`, ne na `conclusion`
(viz S34).
**Doklad:** `měřeno` — 3 otevřené PR (#28, #29, #30), `merged_at=null`,
a přitom 3× `done` v D1. `kód` `agent.yml:565`.

### S32 — Neúspěch brány je **zelený** (brána, která nemá jak selhat)

**Kde:** `agent.yml:642-645` (`ok=0`, ale `exit 0`), `agent.yml:683-691`
(komentář místo `exit 1`).
**Jak se to pozná dnes:** jen komentářem na PR a tím, že PR visí otevřený.
**Co by to odhalilo:** krok auto-merge musí při `ok != 1` **skončit nenulově**.
**Doklad:** `kód`. **Tohle je třetí nezávislý případ téhož vzoru** z `AGENTS.md`
(`check-schema.py`, `test-cooldown.py`, statická kontrola v komentáři) — a první,
kde je brána **celý CI job**.

### S33 — `merged` je mrtvá hodnota: systém stav **zná**, ale nepoužije ho

**Kde:** `index.ts:367` (`let merged = false`), `:375` (načte `merged_at`),
**`:386` rozhoduje jen podle `ok`**, `:409` (`merged` se použije **jen v textu
notifikace**).
**Jak se to pozná dnes:** nikdy — notifikace dokonce napíše „(sloučeno
automaticky)" u něčeho, co sloučeno není.
**Co by to odhalilo:** `if (ok && merged)` na `:385`.
**Doklad:** `kód` — `merged` se v celém `index.ts` vyskytuje na **ř. 367, 375, 409**
(grep, 14 výskytů řetězce `merged`, z toho 11 je `mergedTasks`/`mergedTitlesByRepo`).
**Tohle je nejsilnější nález kola:** informace **v systému je**, jen se zahodí.

### S34 — Komentář v kódu tvrdí opak toho, co kód dělá

**Kde:** `index.ts:372-374`:
> „`run.status === completed` znamená, že doběhl CELÝ workflow – tedy i krok
> automatického sloučení. Stav mergnutí je proto v tuhle chvíli už konečný a
> dá se věřit."

**Proč to není pravda:** když gate nastaví `ok=0`, krok sloučení se **vůbec
nespustí** (`if:` na `agent.yml:677`) a job přesto skončí **`success`** (S32).
**Doklad:** `kód` + `měřeno` (tři PR).
**Proč je to nová třída:** není to vada kódu ani vada komentáře — je to
**zdůvodnění, které zakonzervovalo vadu**. Kdo čte jen komentář, je přesvědčen,
že je to v pořádku. (Obdoba pasti „vada v komentáři" z `AGENTS.md`, ale obráceně:
komentář **obhajuje** vadu.)

### S35 — Varování, které si systém napíše sám do sebe a sám ho ignoruje

**Kde:** `roadmap.json:183, 194` — `done_note: "POZOR: v D1 hotovo (task 139),
ale PR NENÍ sloučené – práce není v main"`.
**Měřeno:** čtenářů `done_note` v kódu = **0**; zapisovatel je jednorázový
`_analyza\srovnej-roadmap-done.py`; v `index.ts`, `worker.mjs` ani `agent.yml`
se řetězec nevyskytuje.
**Proč je to nová třída:** S22 (1. kolo) je „smlouva, kterou nikdo nečte".
Tohle je **silnější**: systém **ví, že lže**, zapíše to — a **nemá jak to
vynutit**. Znalost existuje a je mrtvá.

### S36 — Soubor v repu je autorita, ale **nikdo ho neporovná s realitou**

**Kde:** `index.ts:588-608` — `done: true` bezpodmínečně zapíše `done` do D1
a `continue` (granule se nikdy nevydá).
**Navíc:** `index.ts:1123-1126` tvrdí „soubor je autorita, D1 je cache",
ale `index.ts:738-740` tvrdí „zdroj pravdy je tabulka `roadmap`".
**Dva komentáře v témž souboru si odporují.**
**Doklad:** `kód` + `měřeno` (`sim.mining` je `done` v D1, ale není `done`
v souboru — tedy se to rozchází **i v tom druhém směru**).

### S37 — Nástroj varuje **správně**, ale radí **zastaralou opravu** a skončí zeleně

**Naměřeno 2. 10. 2026, 06:00 UTC** (až po dopsání §④ — proto je S37 dodatek):

```
python orchestra\tools\lint-roadmapa.py games\uo-shadows
  → 7 varování [5] "…MUSÍ mít řádek v D1, jinak závislosti zůstanou viset
                   (conductor dělá jen UPDATE, ne INSERT)"
  → exit 0
```

**Dvě vady v jednom nástroji:**
1. **Text je nepravdivý.** `index.ts:600-603` dělá
   **`INSERT … ON CONFLICT(item_id) DO UPDATE`** — komentář na `:592-596`
   to dokonce datuje („opraveno 30. 9. 2026"). Lint tedy radí opravu,
   **která je už dávno hotová**. (Tatáž past jako u `NAZEV-REPA` a
   `kontrola-schematu.py`.)
2. **Varuje a nezabrání** — `exit 0`. V CI tedy sedm varování nic nezastaví.

**Proč je to nová třída:** S27 je „brána kontroluje seznam, ne strom"
(nic neotevře). S37 je **opačná**: brána **otevře, najde, vypíše — a přesto
projde**. A její text je **zastaralý**, takže kdo jí uvěří, bude „opravovat"
`INSERT`, který tam je.

**Oprava mého vlastního tvrzení:** v §O7 jsem napsal, že lint o chybějícím
`size_lines` **mlčí**. **Není to pravda** — mlčí jen o `size_lines`; o granulích
`done: true` bez řádku v D1 varuje. **Opraveno v zadání A4** (A4a + A4b).

---

## ⑤ Co je dobré a nemá se ztratit

1. **`check-schema.py`** — 17 offline testů s fixturami, **ověřeno mutačně**.
   Jediná brána, u které je doloženo, že umí spadnout.
2. **`test-zamek-owns.py`** — čte funkci **ze zdroje**, ne opsanou logiku.
3. **`test-cooldown.py`** (po fázi A) — SQL ze zdrojáku, `assert` i `sys.exit`,
   správně červený (našel S12).
4. **`run_key` párování** (`index.ts:361`) — **ukotvené ID**, ne titulek.
   Záchranná cesta přes titulek (`:502`) je jen záloha.
5. **Komentář `agent.yml:655-659`** — vysvětluje, **proč** se filtruje jen
   „Testy a build" (naměřeno u PR #21). To je znalost patřící k příkladu.
6. **`index.ts:592-599`** — komentář k `core.attributes`/`entity.item` popisuje
   přesně S30 a **přiznává**, že DAG držel „šťastnou shodou okolností".

---

## ⑥ Architektura v devíti optikách

### O1 — Tok hodnoty
Tok: granule → `roadmapTick` → `tasks` → dispatch → `agent.yml` → PR → **report
`success`** → `done`. **Zastaví se na dvou místech:** (a) když `size_lines`
chybí a změna je > 60 řádků (**13/18 granul**), (b) když se PR nesloučí —
a **ani jedno se neprojeví jako chyba**.
**Plyne pro návrh:** `done` musí být **důsledek** mergu, ne jeho předpoklad.

### O2 — Zdroje pravdy a vlastnictví *(důraz zadání)*
**Sedm zdrojů** (1. kolo) — **a nově: dva z nich si v témž souboru odporují**
(`index.ts:1123` vs. `:738`, S36). **Kolik je jen v D1:** `workers.jobs_done`,
`workers.jobs_failed`, `games.active`, `runs.artifacts` — **čtyři**, a ani jeden
nemá vnější protějšek. **Co se stane, když se kopie rozejdou:** nic — **a je to
naměřené**: `sim.mining` je `done` v D1 a není v souboru (jeden rozchod), tři
granule jsou `done` v souboru i D1 a nejsou v `main` (druhý rozchod).

### O3 — Smlouvy *(důraz zadání)*
- **Deklarované:** `run_key` (UUID, párování `:361`), `schema.sql` (nasazuje se).
- **Odvozené z konvence:** **`done:true` v souboru** (konvence „soubor je
  autorita"), **`size_lines`** (konvence, kterou **13/18 granul porušuje**),
  **titulek PR** (`:502`, string match), **`done_note`** (proseba).
- **Co se stane, když konvence přestane platit:** `size_lines` chybí → limit 60
  → **tři PR visí**; titulek se změní → granule se „ztratí" (S30).
- **Plyne pro návrh:** každá smlouva odvozená z konvence musí mít **výchozí
  hodnotu, která je bezpečná** — dnes je výchozí `60`, což je pro model „strong"
  špatně.

### O4 — Hranice a vrstvy
Skutečný šev je **„orchestrace × engine"** (1. kolo). **Nově:** druhý šev je
**„conductor × GitHub Actions"** — a **není to šev, je to díra**: conductor
nevidí, co se stalo v jobu `auto-merge`, protože se ptá na `conclusion`
**celého workflow** (`:365`), což S32 zneplatnilo.

### O5 — Tichá selhání *(důraz zadání)*
**Společný mechanismus S29–S36 je jiný než u S1–S18.** U starých vad se chyba
**ztratila** (prázdný seznam, přepsaný test). U nových se **stav vyrobí
a nikdo ho neporovná**:

| | staré (S1–S18) | nové (S29–S36) |
|---|---|---|
| co se ztratí | **měření** (brána nic nezměřila) | **protějšek** (stav nemá druhou stranu) |
| projev | zelená nad prázdnem | zelená nad nepravdou |
| kdo si toho všimne | nikdo, dokud se nepodívá | **nikdo, protože není proti čemu** |
| příklad | `check-wiring.py` nad 0 souborů | `done` bez `merged_at` |

**To je odpověď na Q5 ze zadání.** Není to tatáž vada — je to **další vrstva
téhož principu**: systém, který si stav jen hlásí, nemá jak zjistit, že se mýlí.

### O6 — Testovatelnost *(důraz zadání)*
**Co by šlo ověřit offline a dnes to nejde:**
- **Pravidlo `done`** — funkce závisí na `(conclusion, merged_at)`; obojí je
  **vstup**, ne volání sítě → **jde testovat offline** (vzor `hl-sql.py`).
- **`maxLinesOf()`** — čistá funkce nad `size_lines` → offline test
  (a hned by ukázal, že 13/18 granul spadne na 60).
- **Rozchod soubor × D1** — `roadmapTick` je deterministický; šel by pustit nad
  fixturou a **tvrdit, že se rozejdou**.
**Kde je test jen opsaná logika:** 1. kolo našlo `test-eskalace.py`
(s opsaným `watchdog()`); **nově** `auto-merge` nemá **žádný** test.

### O7 — Ekonomie změny
**Naměřeno:** `size_lines` chybí u **13 z 18** granul → limit 60. Přidat
`size_lines` **jedné** granuli = 1 řádek; **ale nikdo neřekne, že chybí**.
**Plyne pro návrh:** chybějící `size_lines` musí být **vidět** (varování v
`lint-roadmapa.py`), ne tiše nahrazeno 60.

> ⚠ **Oprava (naměřeno 2. 10. 2026, 06:00 UTC):** napsal jsem, že lint o tom
> **mlčí**. **Není to pravda** — `lint-roadmapa.py` vypíše **7 varování `[5]`**
> o granulích `done: true`, na které čekají závislosti, a **skončí `exit 0`**.
> O `size_lines` opravdu mlčí; o `done: true` bez řádku v D1 **ne**.
> **A jeho text je zastaralý** (radí `INSERT`, který kód už dělá) → zapsáno
> jako **S37** a promítnuto do A4a/A4b v `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md`.

### O8 — Provoz a lidé
**Co člověk dělá ručně:** slučuje PR, které neprošly gate (24 z 28 sloučených =
**86 % ručně** — `merged_by` = `ssevcikm-spec`). **Naměřeno:** 3 otevřené PR
čekají právě teď. **Nikde není stav „čeká na člověka"** — D1 tvrdí `done`.
**3:00 ráno:** conductor hlásí `ok:true`, `/failed` má 1 úlohu, a **nikdo se
nedozví, že tři granule jsou „hotové" bez kódu**.

### O9 — Druhá hra jako test návrhu
**Nově:** druhá hra by **zdvojnásobila** oba rozchody — `roadmap.json` je per
repo, ale `games.active` je globální a **`workers.jobs_done` je per uzel, ne per
hra**. S31–S36 se **nezmění**, protože jsou v cestě `report → done`, která je
společná.

---

## ⑦ Návrh kontraktů

### 7.1 `done` musí být **odvozené**, ne tvrzené

```
Dnes:   agent.yml:565  report success  ──►  tasks.status='done'
        (bez ohledu na merge)

Má být: report ──► tasks.status='pr_open'        (práce existuje, není sloučená)
        pollRuns ──► if (run.conclusion==success && pr.merged_at)
                       tasks.status='done'
                     else
                       tasks.status='awaiting_human'   ← NOVÝ STAV
```
**Kde:** `index.ts:365-390` — stačí změnit podmínku na `:385` z `if (ok)` na
`if (ok && merged)` a **přidat stav `awaiting_human`**.
**Cena:** 1 soubor, ~15 řádků. **Riziko:** nízké — `merged` se **už načítá**
(`:375`) a nic se podle něj nemění.

### 7.2 `roadmap.json` musí mít **protějšek v gitu**

```
Dnes:   done:true v souboru ──► D1 'done'   (bez kontroly)

Má být: done:true v souboru ──► ověř, že `owns` soubor JE v origin/main
                                (GitHub Contents API na dané cestě)
                                když není ──► varovat a NEzapsat 'done'
```
**Kde:** `index.ts:588-608`. **Cena:** 1 soubor, ~20 řádků (volání API už
v souboru je — `:567`).

### 7.3 `auto-merge` musí **umět selhat**

```yaml
# agent.yml:683-691 — místo komentáře:
- name: Když pravidla neprošla
  run: |
    gh pr comment "$PR" --body "🤖 …"
    echo "::error::PR #$PR nebyl sloučen (pravidla nesplněna)"
    exit 1        # ← chybí
```
**Ale pozor:** `exit 1` tady **nesmí** shodit `done` — proto musí být
**S31 opraveno první**, jinak se rozbité PR začne hlásit jako selhání běhu
a conductor pošle úlohu znovu (a vznikne smyčka). **Pořadí je závazné.**

### 7.4 Kontrakt chybějícího `size_lines`

```
Dnes:   chybí ──► tiše 60        (13/18 granul)
Má být: chybí ──► lint-roadmapa.py varuje
                  conductor při size_lines chybějícím u 'strong' modelu
                  použije 120, ne 60
```

---

## ⑧ Dvě varianty

### Varianta A — „Ukotvi každý stav" (doporučená)

**Co:** každé tvrzení o stavu dostane **protějšek, který existuje nezávisle**:
`done` ← `merged_at` (7.1); `done:true` ← soubor v `origin/main` (7.2);
`auto-merge` ← `exit 1` (7.3, **až po 7.1**); `size_lines` ← varování (7.4).

| | |
|---|---|
| **Cena** | **1–2 dny.** 2 soubory kódu (`index.ts`, `agent.yml`) + 1 lint. ~60 řádků. |
| **Riziko** | **Nízké.** `merged` se už načítá; `check-schema.py` se nemění. |
| **Co NEDĚLÁ** | Nezavádí nový registr, nemění schéma D1, neřeší S1–S28, **nezachrání** tři PR, které visí teď (ty musí sloučit člověk). |
| **Podmínka selhání** | **Když po nasazení zůstane `done` u PR bez `merged_at`** — pak je cesta, kterou jsem nenašel, a analýza je neúplná. |
| **Měřitelné** | Po nasazení: `SELECT count(*) FROM roadmap WHERE status='done'` musí být ≤ počet granul s `owns` v `origin/main`. |

### Varianta B — „Jednotný registr stavů" (nedoporučuji)

**Co:** jeden nový soubor (`stav.json` / tabulka), který je **jediným** zdrojem
a z něhož se **generuje** `roadmap.json` i D1.

| | |
|---|---|
| **Cena** | **8–12 dní.** Nový formát, migrace, generátor, změna `roadmapTick`. |
| **Riziko** | **Vysoké.** Přidává **třetí** zdroj k dvěma, které se rozešly. |
| **Co NEDĚLÁ** | Neřeší, **odkud** se bere pravda — jen přesune místo sporu. |
| **Podmínka selhání** | **Když generátor poběží z D1** (jak dnes `roadmapTick`), vznikne táž vada o vrstvu výš. |
| **Proč ne** | „Kontrakt pro jednoho konzumenta je abstrakce" (1. kolo). Dnes je konzument **jeden** a vada je v **ukotvení**, ne v počtu zdrojů. |

---

## ⑨ Co NEDĚLAT

1. **Neopravovat S32 před S31.** `exit 1` v auto-merge bez opravy `done`
   vyrobí smyčku: PR nesloučen → běh červený → úloha `ready` → znovu.
2. **Nezavádět `awaiting_human` do `roadmap.json`** — soubor je autorita a
   rozšířil by se počet stavů, které nikdo neporovnává.
3. **Nemazat `done_note`** — je to jediné **čititelné** svědectví o S29.
   Místo smazání ho nechat **číst** (varovat, když je `done_note` „POZOR").
4. **Nespoléhat na „soubor je autorita"** (S36) — dva komentáře si odporují;
   nejdřív rozhodnout, který platí, a druhý smazat.
5. **Nepřidávat další bránu**, dokud `auto-merge` neumí selhat (S32) — nová
   brána nad zeleným systémem nic nezmění.

---

## ⑩ Co analýza NEZJISTILA

> **Poznámka bokem — S27 se potvrdila na tomto dokumentu (naměřeno 2. 10. 2026, 05:50 UTC).**
> `kontrola-diakritiky.py` má **pevný seznam** cest; z hloubkových dokumentů zná
> `ANALYZA-HLOUBKOVA-ORCHESTRA.md` (ř. 32) a zadání `ANALYZA-HLOUBKOVA-2-ZADANI.md`
> (ř. 35) — **ale `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` ani `HLOUBKOVA-MERENI-3.md`
> v něm nejsou.** Brána přesto hlásí **„VŠE OK, exit 0"**. Totéž vyšlo
> z `_analyza\hl-diakritika.py` — ten `_analyza` prochází, ale **moje dva nové
> soubory nejmenuje**.
> **Ověřil jsem je proto samostatně** (vlastní kontrola: 0 rozbitých vzorů,
> non-ASCII 8,7 % resp. 5,3 %). **Bez toho bych měl zelenou od brány, která můj
> dokument nikdy neotevřela** — přesně past S27 z 1. kola.
> **Pravidlo pro příště:** „brána je zelená" u **nového** dokumentu neznamená nic,
> dokud se neověří, že ho brána **má v seznamu.**

**A druhá poznámka téhož druhu — vlastní brána musí projít mutačním testem.**
Napsal jsem `_analyza\hl2-kontrola.py`, který kontroluje všech 9 bodů „Hotovo
znamená" ze zadání. **První verze jeho mutačního testu byla slepá**: mutaci jsem
dělal v PowerShellu přes `-replace` s **em-dash `—`**, ten se v konzoli rozbil,
**replace tiše neudělal nic** a test „prošel". Po přesunu mutací do Pythonu
(`hl2-mutace-kontrola.py`) je výsledek **6/6 mutací chyceno**. *Kdybych to
neudělal, odškrtl bych „Hotovo znamená" na základě slepé kontroly.*

- **Nepřepočítal jsem využití orchestra** (82,7 % mrtvá) — vyžaduje stažení
  247 běhů. **Číslo z 1. 10. platí pro 1. 10.**
- **Nevím, proč PR #30 neprošel gate** — hypotéza „`size_lines` chybí → 66 > 60"
  **sedí na čísla**, ale **nepřečetl jsem komentář na PR ani log běhu**, takže
  to není potvrzené. *(Přiznaná úroveň 2, ne 3.)*
- **Nepřečetl jsem živé schéma D1** — `wrangler d1 execute` padá na `EPERM`
  v sandboxu. Všechna tvrzení o schématu jsou z `schema.sql`.
- **Nezavolal jsem `/tick`** — změnil by živý stav.
- **Nezjistil jsem, zda je 86% ruční slučování** opravdu podíl **ruční** práce —
  `merged_by` je u všech `ssevcikm-spec`, ale **nevím, jestli tím „člověkem"
  není tentýž PAT**, kterým slučuje `gh pr merge` v auto-merge. **To je
  nejslabší místo mé argumentace o O8.** *(1. kolo na to narazilo taky: „všechny
  commity mají autora `ssevcikm-spec` → jméno nic nedokazuje".)*

---

## ⑪ Tabulka „tvrzení systému o sobě → čím je ukotveno" *(jádro kola)*

| # | tvrzení systému o sobě | kde je zapsané | **čím je dnes ukotveno** | čím by ukotveno být mohlo |
|---|---|---|---|---|
| 1 | `tasks.status='done'` | D1 `tasks:15` | **ničím** — `run.conclusion` (stav běhu) | `pr.merged_at` (už se načítá, `:375`) |
| 2 | `roadmap.status='done'` | D1 `roadmap:60` | `conclusion` nebo **soubor** | `owns` soubor v `origin/main` |
| 3 | `done: true` | `roadmap.json` | **ruční zápis** | tentýž test na `origin/main` |
| 4 | `done_note: "POZOR…"` | `roadmap.json:183,194` | **ničím — 0 čtenářů** | stal by se varováním brány |
| 5 | `workers.jobs_done` | D1 `workers:49` | **ničím** — sám si to posílá (`:1351`) | počet dokončených běhů v GitHubu |
| 6 | `workers.jobs_failed` | D1 `workers:50` | **ničím** — totéž | totéž |
| 7 | `games.active = 1` | D1 `games:77` | **ničím** | existence `repo` (API `:567` už se volá) |
| 8 | `runs.status` | D1 `runs:29` | **`run.conclusion`** ✅ | (v pořádku) |
| 9 | `runs.artifacts` | D1 `runs:35` | **nil — 0 čtenářů** | — (smazat) |
| 10 | `schvalil: agent-init` (272×) | `baseline.json` | **ničím** — razítka v jedné minutě | podpis člověka / časová prodleva |
| 11 | `_ceka_na_lgtm: true` | `baseline.json` | **nil — 0 čtenářů** | brána, která to vynutí |
| 12 | `acceptance` / `provides` | `roadmap.json` | **nil — 0 čtenářů v kódu** | spustit jako test granule |
| 13 | `ci=ok` | `agent.yml:667` | **`statusCheckRollup`** ✅ | (v pořádku) |
| 14 | `ok=1` (gate) | `agent.yml:645` | výpočet nad PR ✅ | (v pořádku) |
| 15 | **„PR sloučen"** | — | **`conclusion` workflow** ❌ (S32/S34) | `merged_at` (S33) |
| 16 | `roadmap.updated_at` | D1 `roadmap:62` | **`datetime('now')`** — dva významy | oddělit „změna stavu" a „selhání" |

**Součet: z 16 stavů je ukotveno 3 (`runs.status`, `ci`, `ok`), neukotveno 12
a 1 je mrtvý.** To je odpověď na ústřední otázku zadání.

---

## ⑫ Co by tuhle analýzu vyvrátilo

1. **Kdyby `agent.yml` v nasazené verzi měl `exit 1`** v kroku „Když pravidla
   neprošla" — padá S32 a tím i jádro řetězu. **OVĚŘENO PROTI NASazené VERZI
   (2. 10. 2026, 05:47 UTC, GitHub Contents API `Accept: application/vnd.github.raw`,
   `.github/workflows/agent.yml`, 33 425 bajtů):**

   | řádek v nasazené verzi | obsah |
   |---|---|
   | 604 | `id: gate` |
   | 652 | `id: ci` |
   | 685 | `run: gh pr merge "$PR" --squash --delete-branch` |
   | 687 | `- name: Když pravidla neprošla – nechá se k ruční kontrole` |
   | 693 | `gh pr comment "$PR" --body "🤖 **Automatické sloučení neproběhlo** …"` |

   `exit 1` se v celém souboru vyskytuje **5×** — na ř. **340, 372, 438, 454, 486**,
   tedy **všechny před ř. 604**. **Za krokem na ř. 687–693 žádný `exit 1` není.**
   → **S32 potvrzena v nasazené verzi, ne jen v šabloně.** Nález drží.

   *(Tím se zároveň zužuje „nasazená verze se liší od šablony": počet kroků a
   číslování ano — šablona má krok na ř. 683-691, nasazená na 687-693 — ale
   **rozhodovací logika auto-merge je v obou stejná**.)*
2. **Kdyby `merged` někde rozhodovalo** — padá S33. *(`grep`: 3 výskyty, žádné
   v podmínce.)*
3. **Kdyby tři otevřené PR měly `merged_at`** — padá celý S29 v tomto kole.
   *(Měřeno 05:44 UTC: `null`.)*
4. **Kdyby `done_note` někdo četl** — padá S35. *(0 čtenářů, walk.)*
5. **Kdyby `sim.mining` mělo `size_lines`** — padá vysvětlení, proč #30 visí.
   *(Měřeno: nemá. **A pozor — tuhle chybu jsem sám udělal a opravil**; viz §10
   podkladů.)*
6. **Kdyby `merged_by` nebyl člověk** — padá O8. *(8/8 kontrolovaných = `ssevcikm-spec`,
   ale viz mez v §10: nevím, jakého tokenu je to jméno.)*
7. **Kdyby se `roadmap.json` a D1 nerozcházely** — padá Q3. *(Měřeno: `sim.mining`
   `done` v D1, není v souboru.)*

---

## ⑬ Verdikt znovu (přepsaný na konci)

Verdikt z §① **se změnil v jednom bodě**: původně jsem čekal, že najdu
**několik nezávislých** míst, kde si systém lže. Měření ukázalo **jedno** —
`report success` → `done` — a **všechna tři** nesloučená PR jdou skrz něj.
Zbytek je **následek**: `done_note` (varování), `merged` (mrtvá hodnota),
`conclusion` (špatně zvolený důkaz) jsou **čtyři pohledy na tutéž vadu**.

**Co to mění pro návrh:** nestačí opravit `done` — je potřeba **odstranit
možnost tvrdit stav bez protějšku**. Proto je varianta A (ukotvení) správná
a varianta B (registr) špatná.

**A co zůstává jako varování:** kdyby se opravilo **jen** `index.ts:385`
a ne `agent.yml:683-691`, systém by dál vyráběl **zelené běhy nad nesloučenými
PR** — jen by o tom `done` nelhal. **Vada by se přesunula, ne zmizela.**

---

## ⑭ Odpovědi na otázky zadání (6 z 10)

| # | otázka | odpověď | doklad |
|---|---|---|---|
| **1** | Kolik polí v D1 je odvozených a kolik opsaných? | **2 odvozená, 5 sebehlášených, 1 mrtvé.** Autorita: `runs.status` = GitHub; `tasks.status` = **nikdo**; `workers.jobs_done` = sám uzel | §3.1, §⑪ |
| **2** | Co se stane, když se D1 smaže a postaví znovu? | `roadmapTick` staví ze **souboru** (`:588`) — **ztratí se `sim.mining`** (je `done` jen v D1), **a naopak se obnoví tři granule jako `done`**, i když práce není v `main`. Reset tedy **zkopíruje lež** | `měřeno` `sim.mining`; `kód` `:588-608` |
| **3** | Kde je stav ve DVOU místech a neporovnává se? | **`sim.mining`** (D1 `done` / soubor ne) — **1 rozchod**; **tři granule** (`persist.save`, `ui.hud`, `sim.mining`) `done` vs. `origin/main`; `schvalil` vs. člověk | §2.1 |
| **4** | Jak by se poznalo, že PR se sloučil, kdyby ho nikdo nesloučil? | **Nepoznalo.** Dnes se to bere z `run.conclusion` (`:365`) — což je stav **běhu**, a S32 ho zneplatnil. `merged_at` se **načte a zahodí** (`:375` vs. `:409`) | `kód` |
| **5** | Která brána měří něco, co si sama vyrobila? | **`auto-merge`** — měří `conclusion` **vlastního workflow**, jehož neúspěch je zelený (S32). A `workers.jobs_done` měří sám sebe | §3.2, §⑪ |
| **9** | Která z vad S19–S30 je tatáž vada v jiné vrstvě? | **S29 a S30 jsou táž vada** (stav bez protějšku) v **různých vrstvách**: S29 = „hotovo" bez práce; S30 = „čeká" bez řádu. Doplněno: **S31–S36 jsou všechny toutéž vadou** v šesti vrstvách | §④, §O5 |
| **10** | Co by se muselo stát, aby se S29 a S30 už nikdy neopakovaly? | **`done` musí být odvozené z `merged_at`** a **`done:true` ověřené proti `origin/main`** (7.1, 7.2). Nic menšího nestačí — S32 ukazuje, že i „opravená" brána zůstane zelená | §⑦ |

**Neodpovězeno (4):** Q6 (kolik granul je hotových jen na papíře — částečně
§2.1, ale bez historie), Q7 (co dělá člověk ručně — §O8, ale nejisté kvůli
tokenu), Q8 (autorita o hotovém díle — částečně §⑪, rozpor dvou komentářů
nevyřešen).

# PLAN DALŠÍCH KROKŮ — co dělat, v jakém pořadí a co NE

**Co tenhle dokument JE:** plán — **co dělat, v jakém pořadí, proč a co NEDĚLAT**.
Není to stav (ten je v `HANDOFF.md` **§24**) ani zadání (to je
v **`ZADANI-OPRAVA-MERIDEL.md`**).

**Zkontrolováno při:** `orchestra` = **`d1cde9b`** · `uo-shadows` = **`279f584`**
(oba `HEAD == origin/main`, `origin/main..HEAD = 0`) · **2. 10. 2026, 17:03 UTC**
(měřeno `datetime.now(timezone.utc)`, **ne odhadem** — nález H22 / NA18)
**Zpracoval:** **plánovací (ověřovací)** session — ověření práce akční session
z 18:1x–19:0x UTC (`HANDOFF.md` **§24**).

> **⚠ DATUM SPOTŘEBY — co z tohohle dokumentu ještě platí**
>
> Tenhle plán je **snapshot k 2. 10. 2026 17:03 UTC**. Platí, dokud platí:
>
> | Co | Stav při zápisu | Co to zneplatní |
> |---|---|---|
> | `orchestra` HEAD | `d1cde9b`, `origin/main..HEAD = 0` | jakýkoli push do orchestra |
> | `uo-shadows` HEAD | `279f584`, čistý strom | jakýkoli commit ve hře |
> | Bran v `g3-brany.py` | **30** | přidání/ubrání brány |
> | Nenulové exity v `g3` | **2**: `mutace A: pres-level` (**správně**) · `validate-all (CELEK)` = **neproběhlo (prostředí)** | změna oprávnění sandboxu |
> | Omyly v `HANDOFF.md` | **96** v **10 blocích**; brána zná **8** → hlásí **75** | připsání dalšího bloku omylů |
> | Rozchody v `audit2b` | **31**, z toho **25 falešných** (počítáno z výpisu `_tmp-analyza-audit2b.py`) | oprava podle kroku 1 |
> | Dokumenty v inventáři | **105** (79 živých, 11 sirotků, 9 záloh, 6 kopií), **76 bez hlavičky** | nový dokument, nový snapshot |
>
> **Kdo podle plánu pracuje později, ať nejdřív spustí:**
> ```powershell
> $env:PYTHONIOENCODING='utf-8'
> python _analyza\g3-brany.py                     # 30 bran, 2 nenulové exity
> python _analyza\s24-slepota-audit2b-presne.py   # audit2b NENÍ slepý (A: 29 -> 30)
> python _analyza\audit2b-cisla-proti-zdroji.py   # 29 rozchodu (23 falesnych)
> ```

---

## 1. Odkud plán vychází (naměřeno, ne odhadnuto)

Ověřovací session přeměřila **9 tvrzení** akční session z 18:1x–19:0x
(`HANDOFF.md` §24.1) a **13 opatření** z `_analyza\AUDIT-DOKUMENTACE.md` §6
(§24.2):

| Zjištění | Čím je doložené |
|---|---|
| **7 z 9 tvrzení sedí beze zbytku** | §24.1, u každého je výstup |
| **1 tvrzení je zastaralé, ne nepravdivé** (č. 5, hash `HANDOFF.md`) | `451fc02a…` je hash z **obou** snapshotů (18:12 i 18:32); dnešní je `fb266565…` — dokument **správně** narostl o §8j a §23 |
| **1 tvrzení je nepřesné** (č. 7: „1 nenulový exit" → **2**) | `g3`: `validate-all (CELEK)` = **neproběhlo (prostředí)**, ne regrese |
| **Riziko 2 (slepost `audit2b`) je VYVRÁCENO** | mutační test: vložené nepravdivé tvrzení do nedatovaného oddílu → rozchody **29 → 30**, dokument vrácen **bit po bitu** |
| **ALE `audit2b` MÁ jinou vadu: 25 z 31 rozchodů je falešných** | `PREDAVANI-SESSION.md:193` je **citace**; `audit2a` ji zná, `audit2b` ne |
| **H26 potvrzeno a zpřesněno** | opatření **2 a 3 nemá v `ZADANI-DOKONCENI-AUDITU.md` §6 žádný vlastník**; opatření 2 session udělala dobrovolně, **3 zůstalo** |
| **4 z 13 opatření hotovo, 9 ne** | §24.2 — u každého stav **a vlastník** |

**Co z toho plyne:** prioritou **není** velký úklid dokumentace (§10–§22
z `HANDOFF.md`), ale **dokončení měřidel** — každé další měření na nich stojí
a **23 falešných rozchodů** učí člověka bránu ignorovat.

---

## 2. Pořadí kroků (a proč právě takhle)

### KROK 1 — `audit2b`: přestat hlásit falešné rozchody 🔴 NEJVYŠŠÍ

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 1**.

**Proč první:** je to **jediná vada, která aktivně škodí** — brána s 25 falešnými
nálezy z 31 se přestane číst. Naměřeno (`_analyza\_tmp-analyza-audit2b.py`):

| Veličina | Rozchodů | Z toho falešných | Proč |
|---|---|---|---|
| `kontrol` | **19** | **19** | srovnává se s **65** (jedna brána); jiné brány **správně** hlásí 19, 23, 38, 60, 63 |
| `sloupců` | **4** | **4** | všechny jsou **citace** `„32 sloupců"` |
| `omylů` | 3 | 3 | záznamy bez data v okně (`PLAN-DALSI-KROK.md`, `NEXT-SESSION-INSTRUKCE.md`) |
| `dokumentů` | 3 | 3 | `HANDOFF.md` §8 — dtto |
| **nově po `Úkolu 2`** | +2 | +2 | vlastní texty téhle session o **počtu rozchodů** — `audit2b` **počítá i ta čísla** |

**Rozhodující důkaz, že je to vada a ne názor:** `PREDAVANI-SESSION.md:193`
zní *„naměřeno u „32 sloupců" v `AGENTS.md`, nález **N9**"* — tedy **citace**.
`audit2a-schema.py` ten **týž řádek** správně zařadí jako `[citace]` (mezi
„citací=3"), ale `audit2b` ho hlásí jako **ROZCHOD**. **Dvě měřidla téhož
čísla si odporují** — a to je horší než jedno slepé.

**Riziko:** nízké (mění se měřidlo, ne dokument). **Ale:** oprava měřidla je
sama měření → **musí mít mutační test** (`overovani` §9.7).

**Hotovo znamená:** `audit2b` u **každé** veličiny vypíše, **který zdroj** ji
měří a **kolik rozchodů z toho je**; veličinu, která srovnává nesrovnatelné,
**přizná v docstringu** místo falešného nálezu; mutační test **spadne** na
vrácenou vadu (citace → tvrzení). Cíl: **rozchodů ≤ 6, všechny doložené**.

---

### KROK 2 — tři rezidua oprav, která nikdo neměří 🟠 VYSOKÁ

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 2**.

**Proč hned po kroku 1:** jsou **levné, jednoznačné** a každé je přesně ta
třída, kterou projekt **už třikrát naměřil** (reziduum opravy, které spadlo
na falešný poplach):

| # | Co | Naměřeno 2. 10. 2026 |
|---|---|---|
| **NA23** | `g3` u `validate-all` vypsal **`otevřela: 3`** — což je **„NALEZENO 3 PROBLÉMŮ"**, tedy **třetí** výskyt téhož tvaru, ne počet otevřených souborů. (V auditu tam bylo **prázdno** — past zůstala, jen změnila projev) | `g3-brany.py:128`, vzor `NALEZENO (\d+)\|VŠE V PO` |
| **NA19** | **5 ukazatelů** v `PREDAVANI-SESSION.md` (ř. **84, 129, 286, 317, 334**) posílá na **§5** kroniky, kde jsou **Poučení**; návrhy jsou v **§6** | `grep '§5\|§6' PREDAVANI-SESSION.md` |
| **NA17** | Brána kroniky zná **8 bloků** → hlásí **75 omylů**; v `HANDOFF.md` je **10 bloků** (`8i` = 81–86, `8j` = 87–96) | `kronika-kontrola.py`: `BLOKY = [… "### 8h. …"]` |

**Riziko:** **nízké** u NA23 a NA19. U **NA17 střední**: rozšíření brány
o bloky `8i`+`8j` **sníží** „75" na **„85"** (6 + **10** řádků; `8j` má **10**
id, ne 7) — a **každé číslo o omylech se musí přepsat s datem**. Tabulka
v kronize navíc uvádí **89** jako *součet řádků 10 bloků*, ale skutečný součet
řádků tabulek je **97** — i to je nález, ne kosmetika (omyl **86** v bloku `8i`
už na tuhle třídu upozorňuje).

**Hotovo znamená:** `kronika-kontrola.py` **vypíše, KTERÉ bloky zahrnul**
(NA17) a projde s aktuálním počtem; `g3` u brány bez čítače vypíše **`—`**,
nikdy číslo z chybové hlášky; `PREDAVANI-SESSION.md` má **0** odkazů na §5
v souvislosti s návrhy.

---

### KROK 3 — dokončit `audit2b-over.py` na nové měřidlo 🟠 VYSOKÁ

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 3**.

**Proč:** `audit2b-over.py` je **jediný důkaz**, že oprava z kroku 1 měří
(`overovani` §9.7: „opravuješ-li měřidlo, mutačně ověř **opravu**").
Dnes má **2 mutace** (nadpis oddílu + datum v bloku) a **fixturu s citací
nemá** — tedy tvar, na kterém vada vzniká. Test, jehož fixtura neobsahuje
tvar vady, **projde i s vadou**.

**Riziko:** nízké. **Pozor:** test mutuje `HANDOFF.md` (303 kB, **append-only**,
**není v gitu**) → **`try/finally` + záloha kopií** (`overovani` §10.6).

---

### KROK 4 — 3 z 10 bran bez mutačního testu 🟡 STŘEDNÍ

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 4** — **jen 3 z nich**.

**Proč jen 3 a proč až teď:** `audit6-brany-mutace.py` naměřil **10 z 30** bran
**bez jakéhokoli důkazu**. Napsat 10 testů je **velký objem s malým ověřením**
(u `tsc` mutace nedává smysl). Vybrané tři jdou **levně a bez rizika**:

| Brána | Jak se ověří |
|---|---|
| `handoff úplnost` | smaž z `HANDOFF.md` jednu kotvu → musí hlásit **82/83** |
| `over-dokumentaci` | změň kontrolovaný výraz v dokumentu → musí hlásit vadu |
| `b5-over-tvrzeni` | přepiš jedno z **13** ověřovaných tvrzení → musí spadnout |

**Riziko:** nízké. **Past:** `HANDOFF.md` **není v gitu** (`git ls-files` →
`exit 1`) → **záloha kopií je povinná**.

---

### KROK 5 — opatření 7 (hlavičky) + opatření 3 (`ag-over-cisla` na prózu) 🟡 STŘEDNÍ

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 5**.

**Proč až tady:** je to **úklid s jasným kritériem**, ale **bez vlivu na
správnost měření** — a objem je velký (**76 z 105** dokumentů bez hlavičky).
Opatření 3 je do značné míry **kryté** novým `audit2a-schema.py` (ten tvrzení
v próze **už čte**), takže stačí **doložit, co zbývá** — ne psát nový nástroj.

**Riziko:** nízké. **Past:** dokumenty v `_analyza` jsou z velké části
**zálohy a pracovní kopie** (`_zaloha-*`, `*-pred-*`, `handoff-pred-*`) —
**záloze se hlavička nedává**, ta se má poznat **jako záloha** (NA21).

---

### KROK 6 — opatření 6 (ruční seznam vs. projití složky) 🟢 NÍZKÁ priorita

**Co:** `ZADANI-OPRAVA-MERIDEL.md` **Úkol 6** — **doložit**, ne opravovat.

**Proč až nakonec:** naměřeno, že **`g1-diakritika-novych.py` už prochází
složku** (478 souborů) a **je v `g3`** — takže S27 je **krytá jinde**. Ale
`kontrola-diakritiky.py` **pořád obsahuje ruční seznam 57 dokumentů** a ten
**nevidí 28 z nich** (11 v kořeni, 17 v `_analyza`). Je to **měřená mez**,
která patří do zápisu — **ne slepota k dohnání hned**.

**Hotovo znamená:** je **napsané**, kolik dokumentů která brána vidí a které
ne — **s příkazem**. **Ne** „nahradit seznam" bez rozmyslu.

---

## 3. Co NEDOPORUČUJI dělat (výslovně)

| # | Co | Proč NE |
|---|---|---|
| **1** | **Přesunout `HANDOFF.md` §10–§22 do kroniky** (opatření 5; 3 056 řádků, 84,5 % dokumentu) | **Nejvyšší riziko v celém auditu.** `HANDOFF.md` **není v gitu** → zálohou je **jen kopie souboru**. Kritérium je **rovnost množiny** klíčových bodů (ne počtu) a dnešní brána `83/83` stojí na **ručním seznamu**. To je **samostatná session C** s vlastním zadáním — a **až po** krocích 1–3, až budou brány důvěryhodné |
| **2** | **Zavést git pro kořen workspace** (opatření 8; 39 `.md` v kořeni, 0 v gitu) | **Architektonické rozhodnutí uživatele**, ne agenta: nový repozitář, pravidla pro 105 dokumentů, snapshoty a `.secrets`. **Není to blokující** — ochrannou funkci plní snapshoty (opatření 9, hotové) |
| **3** | **Verdikty u 6 sirotků a 251 nezapojených skriptů v `_analyza`** | **Otázka pro člověka, ne pro skript** — audit to přiznává sám (§7 bod 5). Agent, který si ji zodpoví sám, **rozhodne o cizí práci** |
| **4** | **Rušit nebo ztišovat brány, které nic nevykázaly** (opatření 10) | **Jen po mutačním testu PŘED zrušením.** A **stav je dnes jiný, než audit viděl**: `validate-all` **není zelená** — je to **neproběhlo (prostředí)**, třetí stav (`overovani` §7.13) |
| **5** | **Cokoli opravovat podle čísel z `AUDIT-DOKUMENTACE.md` bez přeměření** | Dokument je **snapshot ze 17:4x** a od té doby vznikla §23 a §24. Naměřeno: `audit2b` má dnes **29** rozchodů (audit i §23 uvádějí **27**), `g1` vidí **478** souborů (audit **453**, §23 **466**) |
| **6** | **Přepisovat `NEXT-SESSION-INSTRUKCE.md`** | Patří **souběžné session** (session `76e5d192` doběhla 16:48:44). Jeho obsah je **platné zadání** a hash se **nezměnil ani o bajt** (`9c05c6b4…`) — **i když se `mtime` pohnul na 19:01** (hnul jím mutační test; **druhý** výskyt H28, naměřený touhle session) |

---

## 4. Cena a užitek (naměřeno, ne odhad)

| Krok | Co stojí | Co přinese |
|---|---|---|
| **1** `audit2b` | 1 nástroj + 1 mutační test | **23 falešných nálezů zmizí**; brána se dá zase číst |
| **2** rezidua | 3 malé opravy | číslo o omylech **přestane lhát** (75 vs. 96); `g3` přestane vydávat **chybovou hlášku za počet** |
| **3** `audit2b-over` | 2 fixtury | oprava z kroku 1 je **doložená**, ne tvrzená |
| **4** 3 mutační testy | 3 testy | bran bez důkazu **10 → 7** |
| **5** hlavičky + opatření 3 | objemné, ale mechanické | dokumenty se dají **číst s kontextem** |
| **6** doložit pokrytí | 1 zápis | **přiznaná mez** místo tichého „VŠE OK" |

**Co plán NEDĚLÁ:** nezmenšuje `HANDOFF.md` (a je to tak správně — je to jediné
místo, kde žijí otevřené body) a **nezavádí nový repozitář**.

---

## 5. Vazba na ostatní dokumenty

| Dokument | Co v něm je |
|---|---|
| **`ZADANI-OPRAVA-MERIDEL.md`** | **zadání pro akční session** — kroky 1–6 s měřitelným „Hotovo znamená" |
| `HANDOFF.md` **§24** | **výsledky ověření** (9 tvrzení, 13 opatření, nálezy **H29–H31**) |
| `HANDOFF.md` **§8k** | **vlastní omyly** téhle ověřovací session (**97–101**) |
| `KRONIKA-PROJEKTU.md` **§6** | rozhodnuté návrhy **NA17–NA23** (s důvodem) |
| `NEXT-SESSION-INSTRUKCE.md` | **NEPŘEPISOVAT** — zadání souběžné session (viz §3 bod 6) |
---

## P29 (9. 10. 2026) — ROZHODNUTÍ O KONCEPTU A CO DÁL

> **Datum spotřeby:** 9. 10. 2026, ~07:4x +02:00. Platí pro stav po P29;
> kdo to čte později, **přeměří** (`python _analyza\p29-a-overeni.py`).

**Vstup:** koncept „Orchestrace vývoje hry pomocí AI" (docx od uživatele,
převod `_analyza/_archiv/p29-gemini-architektonika.txt`) + měření P29.

**Rozhodnutí (ne návrh):** **architekturu orchestra NEPŘEDĚLÁVAT.** Koncept
popisuje **tutéž** architekturu (architekt → mozek → dělníci → sklady; kvalitní
model plánuje, free modely vykonávají, stav drží databáze, brány rozhodují),
jen ji navrhuje na **dražší a křehčí** infrastruktuře (Oracle + R2 + PM2 +
Python). Orchestra ji má **levněji a ověřeně** (Cloudflare Worker + D1 + cron +
GitHub Actions + 49 bran) — měnit ji kvůli konceptu by bylo **zhoršení**.

**Co z konceptu PŘEVZÍT (v tomto pořadí):**

1. **Čestné hlášení selhání** — „tik nic nespustil" musí být **vysvětlené**.
   → **APLIKOVÁNO v P29 (B6)**: pojmenované přeskočení (strop granule, zámek,
   cooldown) + automatický úklid osiřelých řádků. Bez nasazení neúčinkuje.
2. **Řetěz poskytovatelů při `RateLimitError`** (koncept: Tier 1→2→3, vypínač
   placeného API, hibernace). **ODLOŽENO na P30** — měřeno: živý `agent.yml`
   je **ve hře** a jeho větev pro kvótu fallback **zakazuje**; orchestra do hry
   nepíše (nabídka **B7**).
3. **Proces design dokumentů** = „super-prompt pro architekta" + sokratovský
   dialog (koncept: Ideation Bot → GCD → schválení → architekt).
   **ODLOŽENO na P30** (nabídka **B8**): ověřit `JAK-PSAT-…` §9 a přenést do
   skillu `game-developer`; §9.3 (výměna roadmapy) je **nedostatečná** —
   pořadí je vypnout hru → push → `/tasks/cleanup` → sonda a `/roadmap/reset`
   **NENÍ** totéž co cleanup.
4. **Pět vrstev pro sandbox** (micro/macro LOD, kombinatorické itemy,
   automatický balanc simulací, knihovna UI komponent, centrální stav od 1. dne)
   → **patří do design dokumentů** nové hry, ne do orchestry. **ODLOŽENO**.
5. **`task_type` modularita** (code / lore / asset / review jako tentýž řetěz)
   → **ODLOŽENO** — měřeno: orchestra dnes **neumí ani číst `acceptance`**
   (H116), takže další vrstvy by jen přidaly pole, která nikdo nečte.

**Co z konceptu ZAMÍTnout (a proč):**
- **Oracle Cloud + R2 + PM2 + Python orchestrátor** → nahrazuje funkční
  a ověřený stack dražší a křehčí variantou (server k údržbě, druhý stavový
  sklad, vlastní CI mimo GitHub).
- **RAG / vektorová paměť, dashboard, audio automatizace** → hra má dnes
  `scripts/game.gd` ~12,5 kB a 21 granulí; RAG by řešil problém, který nemáme,
  a dashboard je nahrazen `g3` + `/health` + notifikacemi.
- **Milníkové revize generující tikety** → orchestra **už** staví na branách
  a PR recenzi; přidávat k tomu druhou roli „revizor" znamená dvě místa, která
  rozhodují o tomtéž (a koncept sám říká, že AI nemá přepisovat hotový kód).

**Nejbližší práce (P30):** (1) nasadit B6 (push + `wrangler deploy`) a přečíst
novou odpověď tiku → rozhodne H111; (2) `entity.move.smooth` (H{P7});
(3) B8 — návod pro architekta; (4) B7 — jen jako nabídka pro session, která
vede hru.
---

## P30 (9. 10. 2026) — CO JE NASAZENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, ~10:0x +02:00. Platí pro stav po P30;
> kdo to čte později, **přeměří** (`python _analyza\p30-a-overeni.py`).

**Hotovo a nasazeno (neopakovat):** oprava **B6** je v živé službě — tik sám
uklízí osiřelé řádky cache (naměřeno **5 → 0**) a **pojmenovává**, co přeskočil
(`v cooldownu 3 úloh: #241, #242, #243`). Nález **H111** je rozhodnutý
(**strop granule**, ne zámek), **H114** taky (`entity.move.smooth` čeká na
`engine.input`). **Nasazení jde z pushe** — lokální `wrangler deploy` není
potřeba (a dnes naštěstí funguje taky).

**Nejbližší práce (P31) — v tomto pořadí:**

1. **Zavádějící komentáře v conductu** (`index.ts:1558–1559` „nejdřív vypni hru,
   pak cleanup“ a `:1489–1493` „reset vrátí úlohy do fronty“) — **jsou to
   tvrzení, která kód neplní**; oprava = změna textu + nasazení z pushe.
2. **`p28-b-mutace.py` je dnes 27/2** (H123) — měřidlo P28 stojí na kotvě
   v CELÉM dokumentu a na společné chybě obou noh; buď opravit měřidlo
   (kotva vázaná na oddíl), nebo tvrzení v §60 označit za neplatné.
3. **Měřidlo P29 neuklízí mutanty** (H124) — dokud to neopraví, každý plný běh
   A1 zanechá v `_analyza/` 186 kB mutanta a rozhodí inventář.
4. **B7 (řetěz poskytovatelů při kvótě)** — patří **session, která vede hru**
   (živý `agent.yml` je ve hře, orchestra do ní nepíše).
5. **B3 (`/game/active {active:false}`)** — čeká na výslovné „ano“ uživatele.

**Co NEDĚLAT:** neměnit architekturu orchestra kvůli konceptu od Gemini
(rozhodnuto v P29); nepsat do hry; nepřidávat do skillu `game-developer`
schéma granule (druhý zdroj pravdy).
---

## P31 (9. 10. 2026) — CO JE OPRAVENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, ~14:2x +02:00. Platí pro stav po P31;
> kdo to čte později, **přeměří** (`python _analyza\p31-a-overeni.py`).

**Hotovo (neopakovat):** obě vady měřidel z nabídky P31 jsou **zavřené** —
**C1** (`p28-b-mutace.py` **27/2 → 30/0**; H131 kotva v celém dokumentu,
H132 dvouprvkový záznam fixtury) a **C2** (H124: měřidlo P29 uklízí mutanty
v `try/finally` a samo to kontroluje). Důkaz: `_analyza/p31-mutace.py` → **24/0**.
**P30 je přeměřená** (`p31-a-overeni.py` → 54/1/2 ROZDÍLY, 0 NEZMĚŘENO);
jediná neshoda je `p30-a` **35/0 → 32/3** (H135: dvě příčiny z opravy C2,
jedna dobová kontrola nasazení na živém HEAD). **H130 je doložené až
TŘETÍM během dávky** (H138: pojistka nově jmenuje viníka; šest nástrojů
dostalo `FORGE_BEZ_REGISTRU`, `p27-oprav-datum.py` je v `PRESKIP`) —
a teprve pak platí „žádný z 4 sledovaných dokumentů se nezměnil“.

**Nový otevřený bod (H139):** `p22-test-mutace.py` **běží, ale jeho mutace nic
nemění** — `tools/over-skilly.py` uznává cesty i v sourozeneckých projektech
(`REPO.parent`), takže přepsaný `REPO` mu nevadí; test proto hlásí „výstup
nehlásí mrtvé cesty“ (19 kontrol / 1 chyba). **Mutace, která prokazatelně nic
nemění, není test** — opravit ji patří do P32 (spolu s dvojím `REPO`
v `tools/over-skilly.py:28,56`).

**Nejbližší práce (P32) — v tomto pořadí:**

1. **`p28-a-overeni.py` A6 čeká `g3 → exit 0`** (H133) — dnes **trvale 1 chyba**
   baseline, protože `g3` končí `exit 1` za **pojmenovaný** stav (1 brána bez
   čítače). Buď to deklarovat jako `OCEKAVANE_*`, nebo vázat na ten stav.
2. **`p27-dopln-zaznamy.py` zapisuje i bez kotvy** (H136) — `PRESKIP` ho jen
   schová; oprava = zápis **až po ověření kotvy** + test, který to zavolá.
3. **Zavádějící komentáře v conductu** (`index.ts:1558–1559`, `:1489–1493`) —
   změna textu + **nasazení z pushe** (ne lokální wrangler).
4. **H112 — brána „cron běží (čas)“ nemůže selhat** (`validate-all` testuje jen
   `!!h.time`) — a přesně ten tik se 9. 10. zastavil.
5. **B3 (`/game/active {active:false}`)** — čeká na výslovné „ano“ uživatele.

**Co NEDĚLAT:** nepouštět `g3` z harnessu bez `FORGE_REGISTR` (H137); nepsat
do hry; nemazat `E:\Workspaces\_acl-oprava-p31\` (cesta zpět k oprávněním).
---

## P32 (9. 10. 2026) — CO JE OPRAVENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, **~20:23 +02:00**. Platí pro stav po P32;
> kdo to čte později, **přeměří** (`python _analyza\p32-a-overeni.py --plne`).

**Hotovo (neopakovat):** P31 je **přeměřená vlastním měřidlem**
(`_analyza/p32-a-overeni.py` → **51/0**, 2 ROZDÍLY, 0 NEZMĚŘENO) a jsou
**zavřené tři vady**:

1. **C3′/H139 → H140 + H141:** kontrola v `p22-test-mutace.py` se nechala
   uspokojit **podřetězcem** (`"0 mrtvých"` je v `"40 mrtvých"`); dnes se čítač
   **parsuje z měřeného řádku** → **20/0** (bylo 19/1). Závěr P31 *„mutace nic
   nemění“* je **vyvrácený** (sonda `p32-sonda-h139.py`: 92/0 → 43/40).
2. **C2′/H136 → H142:** `p27-dopln-zaznamy.py` **zapisoval i bez kotvy**; dnes
   se kotvy ověří PŘED zápisem a při neshodě se **nezapisuje** →
   `p32-test-zapis-kotvy.py` **16/0** (s diferenciálem).
3. **H145:** **vlastní záznam P31 zdvojil kotvu** `test-tick-offline → 215/0`,
   čímž shodil `p30-mutace.py` (ValueError) a diferenciál A1; dnes je kotva
   z **MĚŘENÉHO oddílu** §60 a dvojznačná kotva se hlásí pojmenovaně →
   `p30-mutace.py` **16/0**, `p31-a-overeni.py --jen A1 --plne` **11/0**.

**Nejbližší práce (P33) — v tomto pořadí:**

1. **H133 — `p28-a-overeni.py` A6 čeká `g3 → exit 0`**, ale `g3` končí `exit 1`
   **pojmenovaně** (1 brána bez čítače: `mutace B (combat)`). Baseline A6 má proto
   **trvale 1 chybu**; buď stav deklarovat (`OCEKAVANE_*`-style), nebo vázat na
   pojmenovaný stav.
2. **H112 — brána „cron běží (čas)“ nemůže selhat** (`validate-all` testuje jen
   `!!h.time`) — a přesně ten tik se 9. 10. zastavil.
3. **C4′ — ✅ OPRAVENO, NASAZENO A OVĚŘENO** (9. 10. 2026, na pokyn uživatele):
   přepsal se **jen text** dvou komentářů v `conductor/src/index.ts` a nasadil:
   `deploy.yml` **#36 na `0b86c2d`** `completed/success`, nahraná verze
   **`bb32fe74-2e50-47a3-9677-70a77469d4e1`**, ověřeno třemi kroky
   (`_analyza/p32-cf-verze-vystup.txt`). Nasazený kód je odteď **`0b86c2d`**
   (dřív `cf1f280`); **chování kódu se nezměnilo** (změnil se text). Nález **H148**.
4. **B3 — ✅ OVĚŘENO 9. 10. 2026 (P32)** na živé službě (uživatel dal „ano“):
   hra vypnuta → tik **nedispatchuje** a hlásí **„nedispatchuji (B4)“**
   (`spusteno: 0 úloh`), `/tasks/cleanup` → **503** (H128 potvrzeno ŽIVĚ =
   **H147**); hra **vrácena AKTIVNÍ** (sonda `_analyza/p32-sonda-b3.mjs`, **8/0**).
   **Na uživatele tu tedy nic nečeká** — zbývá jen rozhodnutí o C4′ (bod 3).
5. **H143/H144 zůstávají jako poučení**: čísla o výskytech kotvy a o počtu řádků
   se **měří**, neopisují do záznamu (a záznam, který kotvu cituje, mění
   jednoznačnost kotev měřidel).

**Co NEDĚLAT:** nepsat do hry; nepouštět harness z `g3` bez
`FORGE_REGISTR`/`FORGE_BEZ_REGISTRU` (H137); nemazat
`E:\Workspaces\_acl-oprava-p31\`; **needitovat záznamy** (HANDOFF/KRONIKA se jen
doplňují) — měřidlo se opravuje, záznam ne.

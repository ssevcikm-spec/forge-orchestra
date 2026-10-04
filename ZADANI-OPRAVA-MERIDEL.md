# ZADÁNÍ PRO AKČNÍ SESSION

**Zkontrolováno při:** `orchestra` = **`d1cde9b`** („Projití složky místo ručních
seznamů + ukázky rozbitého kódování slovem") · `uo-shadows` = **`279f584`**
(„Granule `tests.harness` + lék na M3 (nález H12)") · **2. 10. 2026, 17:03 UTC**
**Stav obou repů při psaní:** `orchestra` = `d1cde9b` · `uo-shadows` = `279f584`
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0` v obou repech
**Necommitnuté:** `orchestra` **1 soubor** (`M tools/kontrola-diakritiky.py`) ·
`uo-shadows` **čistý**
**Co je v `HANDOFF.md`:** **§24** (výsledky ověření) · **§8k** (vlastní omyly
**97–101**) · **§2** (co je otevřené)
**Co tenhle dokument JE:** zadání pro **akční** session, která přijde.
Není to stav (ten je v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).

> ## ⚠ PŘEČTI TYHLE DVĚ VĚCI PRVNÍ
>
> **1. `NEXT-SESSION-INSTRUKCE.md` NENÍ tvoje zadání.** Patří **souběžné
> session** (její session `76e5d192` doběhla 16:48:44) a jeho obsah se
> **nezměnil ani o bajt** (SHA-256 `9c05c6b434d5d026…`, 17 841 B).
> **Tvoje zadání je tenhle soubor.** Proč je oddělený, vysvětluje
> `HANDOFF.md` **§23.7** — nález **H28**.
>
> **2. Předchozí zadání mělo NESPLNITELNÉ kritérium** (`HANDOFF.md` **§23.2**,
> nález **H24**) a i to **tohle** zadání tvrdí čísla, která **zestárnou**.
> **Tvůj první úkol je ověřovat, ne věřit** — a platí to i na **tenhle** dokument.

---

## 1. Než začneš (povinné)

1. Přečti `AGENTS.md`, `HANDOFF.md` **§24** a **§8k**, `PLAN-DALSI-KROK.md`
   a `PREDAVANI-SESSION.md` **§5** a **§6.2**.
2. Načti skilly **`dsh-prostredi`** a **`overovani`** `skill` toolem.
   **V `overovani` je §10** (24 pastí měřidel) — **přečti ji dřív, než začneš
   psát měřidlo**, protože **krok 1 je oprava měřidla**.
3. **Ověř, že tohle zadání sedí na skutečnost** (jinak se v tom bodě zastav
   a zapiš to jako nález):
   ```powershell
   $env:PYTHONIOENCODING='utf-8'
   python _analyza\s24-meridla-over.py             # brána na tohle zadání, musí být exit 0
   python _analyza\zadani-kontrola.py              # exit 0
   python _analyza\g3-brany.py                     # 30 bran, 2 nenulové exity
   & orchestra\tools\git.cmd -C orchestra rev-parse HEAD
   & orchestra\tools\git.cmd -C games\uo-shadows rev-parse HEAD
   ```

---

## 2. Naměřená fakta, na kterých zadání stojí (s příkazy)

| # | Fakt | Příkaz, kterým to ověříš | Co vyjde |
|---|---|---|---|
| **F1** | `audit2b` hlásí **31 rozchodů**, z toho **25 falešných** (⇒ **po Úpravě 1 se čeká ≤ 6**) | `python _analyza\audit2b-cisla-proti-zdroji.py` | `ROZCHODŮ: 31`; `kontrol` **19**, `sloupců` **4**, `dokumentů` **3**, `omylů` **3**, +2 z textů o rozchodech |
| **F2** | **4 rozchody u `sloupců` jsou CITACE** a `audit2a` je zná **jako citace** | `python _analyza\audit2a-schema.py` vs. `audit2b` | `audit2a`: 25 výskytů = 3 souhlasí + 19 záznamů + **3 citace** + **0 rozchodů** |
| **F3** | `audit2b` **NENÍ slepý** na append-only dokumenty | `python _analyza\s24-slepota-audit2b-presne.py` | nedatovaný oddíl: rozchody **29 → 30**; datovaný: **29 → 29** (správně záznam) |
| **F4** | Omyly: `HANDOFF.md` má **10 bloků / 96 id**, brána zná **8 / 75** | `python _analyza\kronika-kontrola.py` | `omylů celkem (skutečnost): 75` |
| **F5** | `g3` u `validate-all` vypíše **`otevřela: 3`** = **„NALEZENO 3 PROBLÉMŮ"** | `python _analyza\g3-brany.py` | řádek `exit=1   validate-all (CELEK)   otevřela: 3` |
| **F6** | `validate-all` **není zelená** — je to **neproběhlo (prostředí)** | `node orchestra\tools\validate-all.mjs` | `exit 1`, **3 problémy**: 2× `PermissionError WinError 5` v tempu, 1× `spawn EPERM` |
| **F7** | **5 odkazů na §5** v `PREDAVANI-SESSION.md` (ř. 84, 129, 286, 317, 334) — plus **jeden nový v ř. 157** vznikl touhle session (**6**); `SELECT`-like ověření: 7 výskytů `§5`, z toho 1 míří na `PLAN-DALSI-KROK.md` **správně** | `python _analyza\s24-meridla-over.py` (sekce F7 vypíše řádky) | vada je **jen tam, kde jde o NÁVRHY v kronize** — návrhy jsou v **§6** |
| **F8** | `kontrola-diakritiky.py` má **ruční seznam 57 dokumentů** a **nevidí 28** | `python _analyza\s24-opatreni6-pokryti.py` | 11 z kořene + 17 z `_analyza` není v bráně |
| **F9** | **10 z 30** bran nemá mutační test | `python _analyza\audit6-brany-mutace.py` | `Brány BEZ jakéhokoli důkazu: 10`; `exit 1` (**správně** — R6) |
| **F10** | **76 z 105** dokumentů je bez hlavičky | `python _analyza\audit1-inventar.py` | `dokumentů celkem: 105` · `bez hlavičky: 76` |

---

## 3. ÚKOLY (v tomto pořadí — pořadí je závazné)

### Úkol 1 — `audit2b`: přestat hlásit falešné rozchody

**Co je špatně (naměřeno, F1 + F2):** veličina `kontrol` srovnává **jedno číslo
z jedné brány** (`65`, běh Godotu) se **všemi** výskyty `(\d+)\s+kontrol`
v jádru. Různé brány ale hlásí **různé počty kontrol SPRÁVNĚ** (19, 23, 38,
60, 63…) — přesně vada, kterou audit vytkl `audit2-rozpory.py`. A `sloupců`
hlásí **4 citace** `„32 sloupců"`, z toho jednu v `PREDAVANI-SESSION.md:193`,
kterou `audit2a-schema.py` **správně** zařadí jako `[citace]`.

**Co udělat (jedna ze dvou cest — vyber a zapiš proč):**

* **(A) Rozpadnout veličinu na `kontrol:<brána>`** — u každého výskytu
  dohledat, **která brána** to číslo vydala, a srovnávat **jen s ní**.
  Náročnější, ale **zachová pokrytí**.
* **(B) Veličinu `kontrol` z nástroje vyřadit** a **přiznat to v docstringu**
  (jako se to udělalo u `audit2-rozpory.py`). Levnější, ale **ztratí** pokrytí —
  což se musí napsat, ne zamlčet.

**Navíc povinně (obojí):**
1. **CITACE se musí rozpoznat** — `audit2b` má konstantu `CITACE`, ale
   `„32 sloupců"` v uvozovkách jí **neprojde**. Doplň pravidlo na **číslo
   v uvozovkách / v kódovém rozpětí** (`„32 sloupců"`, `` `32 sloupců` ``).
2. **Výpis musí u každé veličiny říct, KTERÝ ZDROJ ji měří a kolik rozchodů
   z toho je** (návrh **NA17** — „celkem N" bez seznamu zdrojů je neověřitelné).

**Hotovo znamená (měřitelné):**
- `python _analyza\audit2b-cisla-proti-zdroji.py` → **rozchodů ≤ 6**
  a u **každého** zbylého je ve výpisu **citace řádku + zdroj**;
- `python _analyza\s24-meridla-over.py` → **`exit 0`** (kontroluje právě tohle);
- **mutační test `audit2b-over.py` spadne na vrácené vadě** — a to na **nové
  fixtuře s citací** (dnes ji nemá, F2). Ukaž výstup.

### Úkol 2 — tři rezidua oprav (NA23, NA19, NA17)

**2a — NA23 (`g3-brany.py`, kosmetika s dopadem):** u brány bez čítače se
vypisuje **prázdný řetězec**, a u `validate-all` se vypisuje **`3`**, což je
**„NALEZENO 3 PROBLÉMŮ"** — tedy **třetí** výskyt tvaru `NALEZENO (\d+)`,
ne počet otevřených souborů (F5). **Co udělat:** vzor **zúžit** tak, aby
netrefil chybovou hlášku, a když čítač není, vypsat **`—`** (nikdy prázdno
ani cizí číslo). **Hotovo:** `g3` u `validate-all` vypíše **`—`** a u brány
bez čítače taky `—`; **žádný** řádek nemá `otevřela:` prázdné ani cizí číslo.

**2b — NA19 (ukazatele):** **5 odkazů** v `PREDAVANI-SESSION.md` (ř. **84,
129, 286, 317, 334**) posílá na `KRONIKA-PROJEKTU.md` **§5**, kde jsou
**Poučení**; tabulka návrhů je v **§6** (F7). **Co udělat:** opravit
**ukazatele**, **ne** přečíslovat sekce kroniky. **Hotovo:** `0` odkazů na §5
v souvislosti s návrhy; ověř `read`em u každého z pěti řádků.

**2c — NA17 (brána kroniky):** `kronika-kontrola.py` má **pevný seznam 8 kotev**
(`BLOKY = […]` končí na `### 8h.`), takže bloky **`8i`** (81–86) a **`8j`**
(87–96) **nevidí** — a hlásí „omylů celkem **75**", ačkoli v dokumentu je
**96 id v 10 blocích** (F4). **Co udělat:**
1. **Rozšířit bránu** o bloky `8i` a `8j` (a **vypisovat, KTERÉ bloky do počtu
   zahrnula** — to je jádro NA17);
2. **přepsat čísla o omylech s DATEM** tam, kde jsou (kronika §1 řádek 19,
   `AGENTS.md`, `HANDOFF.md` **§24** zapsaný touhle prací) — **historická čísla
   se nepřepisují, označují se jako „ve svém čase správná"** (A2);
3. **změřit a zapsat**, kolik je **řádků tabulek** (naměřeno **97**), kolik
   **unikátních id** (**96**) a kolik **vidí brána** (bude **85**, ne 75) —
   **tři čísla, tři otázky, každé pojmenované**.

**Hotovo znamená:** `kronika-kontrola.py` → **`exit 0`** a ve výstupu je
**vypsaný seznam bloků**, které sečetl; v dokumentech je u každého čísla
o omylech **řečeno, které zdroje do něj patří**.

### Úkol 3 — `audit2b-over.py`: fixtura s citací

**Co je špatně:** test ověřuje **2 mutace** (nadpis oddílu, datum v bloku),
ale **fixturu s citací nemá** — tedy tvar, na kterém falešný nález vzniká (F2).
Test, jehož fixtura neobsahuje tvar vady, **projde i s vadou**.

**Co udělat:** doplnit **2 mutace**: (a) **citace se stane tvrzením**
(odstraň uvozovky u `32 sloupců` v `AGENTS.md:62`) → `audit2b` to **musí**
ohlásit; (b) **dvě různé brány** — změň číslo u jedné brány a ověř, že se
**neohlásí** u brány jiné (to je jádro opravy z Úkolu 1).

**Hotovo znamená:** `python _analyza\audit2b-over.py` → **`exit 0`**,
**4 mutace, 4 chyceny**, a `HANDOFF.md` **bit po bitu původní**
(ověřeno hashem, **ne** `mtime` — nález H28 / NA20).

### Úkol 4 — tři mutační testy (ze 10 bran bez důkazu)

**Co:** `audit6-brany-mutace.py` hlásí **10 z 30** bran bez jakéhokoli důkazu
(F9). Napsat všech 10 je **velký objem s malým ověřením** — udělej **jen tyhle
tři** a zapiš, že ostatní zůstávají:

| Brána | Mutace | Co musí nastat |
|---|---|---|
| `handoff úplnost` | smaž z `HANDOFF.md` **jednu** kotvu | hlásí **82/83** |
| `over-dokumentaci` | změň **kontrolovaný výraz** v dokumentu | hlásí vadu |
| `b5-over-tvrzeni` | přepiš jedno z **13** ověřovaných tvrzení | `exit 1` |

**Hotovo znamená:** `audit6-brany-mutace.py` → **„Brány BEZ jakéhokoli důkazu:
7"** (bylo 10) a **každý** nový test je vidět ve výstupu **s počtem**.

> **⚠ POVINNÉ u všech mutací:** záloha **kopií** (`HANDOFF.md` **není v gitu**),
> **`try/finally`** a **assert, že se mutace opravdu provedla** (`overovani`
> §7.9, §7.12, §10.6). Mutace, která se tiše neprovede, **tvrdí totéž co
> mutace, která projde**.

### Úkol 5 — hlavičky dokumentů (opatření 7) + opatření 3

**5a:** doplnit hlavičku „Co tenhle dokument JE" dokumentům, které ji nemají —
naměřeno **76 z 105** (F10), převážně **7 analýz a 4 plány** v kořeni.
**Zálohám a pracovním kopiím** (`_zaloha-*`, `*-pred-*`, `handoff-pred-*`)
hlavičku **NEDÁVEJ** — mají se poznat **jako zálohy** (NA21), a to zapiš.
**Hotovo:** `audit1-inventar.py` → `bez hlavičky` **≤ 20** a **je vypsané,
které zůstaly a proč**.

**5b (opatření 3, nález H26 — **opatření bez vlastníka**):**
`ag-over-cisla.py` čte **jen řádek 337** svého dokumentu, ne **62**. Nový
`audit2a-schema.py` tvrzení v próze **už čte**, takže **neduplikuj nástroj** —
**dolož měřením**, která tvrzení o sloupcích zůstávají **nekrytá oběma**
nástroji, a napiš to do `AGENTS.md`. **Hotovo:** existuje výpis
„tvrzení o `schema.sql` / kryté `ag-over-cisla` / kryté `audit2a` / **nekryté**"
a u nekrytých je rozhodnutí (doplnit / zamítnout s důvodem).

### Úkol 6 — doložit pokrytí brány diakritiky (opatření 6)

**Co:** `kontrola-diakritiky.py` má **ruční seznam 57 dokumentů** a **nevidí
28** dalších (11 v kořeni, 17 v `_analyza`, F8); `g1-diakritika-novych.py`
naproti tomu **prochází složku** (478 souborů) a **je v `g3`**.

**Co udělat:** **nic neopravovat** — jen **zapsat měřenou mez**: kolik dokumentů
která brána **otevře**, které **ne**, a **čím je to kryté** (`g1` v `g3`).
Zdůvodni, proč to dnes **není** vada S27.

**Hotovo:** v `HANDOFF.md` je tabulka „brána → kolik souborů otevřela → co
neotevřela" **s příkazem** u každého řádku.

---

## 4. HOTOVO ZNAMENÁ (měřitelné — celá session)

- [ ] **Úkol 1:** `audit2b` rozchodů **≤ 6**, každý se zdrojem; `s24-meridla-over.py` → **`exit 0`**
- [ ] **Úkol 1:** mutační test `audit2b-over.py` **spadne** na vrácené vadě (citace → tvrzení)
- [ ] **Úkol 2a:** `g3` má u `validate-all` **`—`**, ne `3`; žádné `otevřela:` prázdné
- [ ] **Úkol 2b:** `PREDAVANI-SESSION.md` → **0** odkazů na §5 u návrhů (5 opraveno)
- [ ] **Úkol 2c:** `kronika-kontrola.py` → **`exit 0`**, **vypisuje seznam bloků**; čísla o omylech mají datum
- [ ] **Úkol 3:** `audit2b-over.py` → **4 mutace, 4 chyceny**, `HANDOFF.md` bit po bitu původní
- [ ] **Úkol 4:** bran bez důkazu **10 → 7**, každý nový test **s počtem** ve výstupu
- [ ] **Úkol 5:** `audit1-inventar.py` → `bez hlavičky` **≤ 20**; opatření 3 **doložené**
- [ ] **Úkol 6:** tabulka pokrytí brány diakritiky **s příkazem**
- [ ] **U KAŽDÉ spuštěné brány** je ověřeno, že **soubor otevřela** (kolik) — past S27
- [ ] `python _analyza\s24-meridla-over.py` → **`exit 0`**
- [ ] `python _analyza\handoff-kontrola-uplnost.py` → **83/83** (nic nezmizelo)
- [ ] `python _analyza\kronika-kontrola.py` → **`exit 0`**
- [ ] `python _analyza\g1-diakritika-novych.py` → **`exit 0`**
- [ ] Nový/změněný dokument → **do seznamu v `kontrola-diakritiky.py`**
- [ ] `_analyza\_inventar.json` **přegenerovaný** (`python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json`)
- [ ] `HANDOFF.md` — nová sekce s výsledky, **vlastní omyly do §8**, nic nezmizelo
- [ ] `KRONIKA-PROJEKTU.md` — **řádek**; návrhy **NA17–NA23** už rozhodnuté jsou
- [ ] Před commitem/pushem **ukázáno `git status` + `git diff --stat`** a **čekáno**

---

## 5. CO NEDĚLAT

- **NEPŘEPISUJ `NEXT-SESSION-INSTRUKCE.md`** — patří souběžné session
  (hash `9c05c6b4…` se nezměnil; `mtime` se pohnul, ale to **není** změna obsahu).
  Zadání pro další session napiš do **nového souboru** (`ZADANI-<téma>.md`).
- **NEPŘESOUVEJ `HANDOFF.md` §10–§22 do kroniky** (opatření 5) — je to
  **samostatná session C** s nejvyšším rizikem. Důvody: `PLAN-DALSI-KROK.md` §3.
- **NEZAVÁDĚJ git pro kořen workspace** (opatření 8) — rozhodnutí uživatele.
- **NEDÁVEJ verdikty 6 sirotkům ani 251 nezapojeným skriptům** — otázka pro člověka.
- **NERUŠ brány, které nic nevykázaly** — nejdřív mutační test.
- **NEPŘEPISUJ historická čísla** (A2) — rozdíl je **čas**, ne nepravda.
  `HANDOFF.md` a `KRONIKA-PROJEKTU.md` jsou **append-only**.
- **NEOPRAVUJ `validate-all`** kvůli `exit 1` — naměřeno (F6): je to
  **neproběhlo (prostředí)**, třetí stav (`overovani` §7.13). Není to regrese.
- **NEMAŽ `_analyza\s24-*.py`** ani `_analyza\snapshot-*` — jsou to doklady
  ověření, ne odpad.
- **NEPUSHUJ bez vyžádání** — nejdřív `git status` a `git diff --stat` a **čekej**.

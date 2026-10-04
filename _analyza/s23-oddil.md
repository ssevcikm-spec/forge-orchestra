
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
## 23. Provedeno 2. 10. 2026 (18:1x–19:0x) — AKČNÍ session: DOKONČENÍ AUDITU

**Zadání:** `ZADANI-DOKONCENI-AUDITU.md` (samostatný dokument, **NE**
`NEXT-SESSION-INSTRUKCE.md` — ten patří souběžné session, viz §23.7).
**Kontrola zadání před prací:** `git -C orchestra rev-parse HEAD` = `d1cde9bbf`,
`git -C games\uo-shadows rev-parse HEAD` = `279f58486` → **obojí sedí** s hlavičkou
zadání. Tři klíčová tvrzení ověřena **spuštěním** (`_analyza\audit7-overeni-zadani.py`
→ `exit 0`, „Všechna ověřená tvrzení zadání SEDÍ na skutečnost").

**Co je hotové — měřeno, ne tvrzeno:**

| Úkol | Stav | Čím je doložený |
|---|---|---|
| **0** zmrazit snapshot | ✅ | `_analyza\snapshot-20261002-181237\manifest.json` — **71 souborů, každý s SHA-256**, prázdných hashů **0**; nezávisle přepočítáno z disku `audit-snapshot-over.py` → **71/71 hashů sedí** |
| **1** opravit R1 | ✅ | `AGENTS.md:63` má `**39** (stav před B1; dnes **40**)`; `audit2a-schema.py` → **`exit 0`**, 0 rozchodů. **Ale zadání se v tomhle bodě mýlilo — viz §23.2** |
| **2** opravit R5 | ✅ | `ag-mutace.py` kotva `40 sloupců` → **`exit 0`, 2 mutace, 2 chyceny**; **zařazen do `BRANY` v `g3-brany.py`** (brán **29 → 30**) |
| **2b** vložit vadu ručně | ✅ | vada `40 → 32` vložena do `AGENTS.md:338` **rukou** → `ag-over-cisla.py` **`exit 1`** (`✗ ROZEŠLO SE sloupců D1 tvrdí 32, naměřeno 40`) **i** `audit2a-schema.py` **`exit 1`**; pak vráceno |
| **3** pojmenovat R6 | ✅ | hlavičky v `h17-mutace-a.py` a `mutace-testu.py`; `audit3-hlavicky-over.py` → **oba spuštěny, `exit 1`, 0 souhrnů testů** (tedy „neproběhlo", ne nález) |
| **4** opravit `audit2b` | ✅ | **`granulí` 0 rozchodů** (bylo 11 falešných); `HANDOFF.md:1143` zařadil **nadpis oddílu**; `audit2b-over.py` → 2 mutace, obě chyceny, **`HANDOFF.md` bit po bitu původní** |
| **5** spustit všechno | ✅ | viz §23.4 |
| **6** zápisy a inventář | ✅ | inventář přegenerován (**2 080 nálezů**), `hl-rizika-jazyka.py` → `exit 0`; `ZADANI-DOKONCENI-AUDITU.md` přidán do `kontrola-diakritiky.py` (**brána ho OTEVŘELA: 15 749 znaků**) |

**Hotovo znamená (13 bodů ze zadání §4): 13 ze 13.** U dvou z nich je ale
splnění **jiné, než zadání čekalo** — a to je zapsané níž, ne zamlčené.

---

### 23.1 `HANDOFF.md` je NEDOTČENÝ — doloženo DVĚMA nezávislými měřeními

Zadání to žádalo jako samostatný bod (nález R3 se **neopravuje v datech**).
Doloženo dvakrát, různými nástroji:

| Měření | Výsledek |
|---|---|
| `audit2b-over.py` (krok 0 a znovu po mutacích) | SHA-256 **`451fc02aeea55000…`** = hash ze snapshotu Úkolu 0 → **SHODA** |
| `audit-snapshot.py` (porovnání dvou snapshotů) | `HANDOFF.md` je v kategorii **„jen mtime"** — **velikost 282 130 B beze změny**, obsah stejný |

**Druhé měření je přitom přesnější než to první** a stojí za zapamatování:
`HANDOFF.md` **má jiný `mtime`** (18:27:42 místo 17:33:28), protože do něj
sáhly **mutační testy** (`audit2b-over.py` při M1 a `zadani-mutace.py`) —
zapsaly ho a **vrátily bajt po bitu**. Kdo by se ptal na `mtime`, řekl by
„soubor se změnil"; **kdo se ptá na hash, ví, že se nezměnil ani o bajt.**
Je to táž past, na kterou `AGENTS.md` upozorňuje u `Measure-Object -Line`:
**autorita je obsah, ne časová značka.**

### 23.2 ⚠ NÁLEZ: ZADÁNÍ MĚLO U ÚKOLU 1 NESPLNITELNÉ KRITÉRIUM — a mířilo vedle

**Tohle je nejdůležitější nález téhle session a je naměřený.**

Zadání (Úkol 1) říká: *„Co je špatně: číslo 39 je tam v přítomném čase a bez
značky času. Hotovo: `audit2a-schema.py` → `exit 0` (dnes `exit 1`)."*
Předpokládá tedy, že brána padá **kvůli tomu 39**.

**Naměřeno po provedení předepsané opravy (`exit 1` zůstal, 6 rozchodů):**

| # | Kde | Co to je | Byl to rozchod? |
|---|---|---|---|
| 1 | `AGENTS.md:62` „**„32 sloupců"**" | **CITACE** dřívějšího chybného tvrzení | ne |
| 2 | `KRONIKA-PROJEKTU.md:36` „39 sloupců, ne 32" | **datovaný záznam** | ne |
| 3–6 | `HANDOFF.md:127, 558, 581, 628` | **citace** v tabulkách omylů | ne |

**Ani jeden z těch šesti nebyl tvrzení o dnešku.** A ta horší polovina:
vzor brány `(\d+)\s+sloupc` potřebuje slovo „sloupců" **hned za číslem** —
takže na skutečné tvrzení („správně je **39**") **vůbec nedosáhl**. Brána
u `AGENTS.md:62` hlásila **„tvrdí 32"**, tedy četla **citaci**, a **vadu R1
nikdy neměřila**. `exit 1` byl **správný výsledek ze špatného důvodu**.

**Co jsem udělal (a proč to nebylo „víc, než zadání"):** bez opravy brány
nebylo kritérium „`exit 0`" dosažitelné **jinak než přepsáním datovaných
záznamů** — což zadání na třech místech zakazuje („Nemaž nic", „Nepřepisuj
historická čísla", „nic v `HANDOFF.md`"). Opravil jsem proto **měřidlo**,
stejně jako to zadání předepisuje u Úkolu 4:

* **nové pravidlo:** proti živému zdroji se měří **AUTORITA** (`AGENTS.md`);
  `HANDOFF.md` a `KRONIKA-PROJEKTU.md` jsou **append-only záznamy** (A2),
  takže se vypíšou jako `[záznam]`, ale **nepočítají se jako rozchod**;
* **citace** (číslo v uvozovkách / kódovém rozpětí) a **záznam se značkou
  času** (`stav před B1`, `dnes`) se rozlišují od tvrzení;
* **přidán druhý vzor na tvrzení v PRÓZE** (`správně je **39**`, `dnes **40**`) —
  jinak by vada R1 zůstala neviditelná i po opravě;
* **mutačně ověřeno: 4 mutace, 4 chyceny** (`audit2a-mutace.py`), včetně
  **vrácení `39` bez značky času** — tedy přesně vady R1, kterou původní
  brána **nikdy neviděla**.

**A jeden nález navíc, který patří k R1** (audit ho uvádí jako „tu horší část"):
`ag-over-cisla.py` tiskl `OK 39 sloupců D1 = 40` — **popisek a hodnota si
odporovaly v jednom řádku**, protože popisek byl zastaralý text napevno.
Popisek je opraven (`sloupců D1`, bez čísla, které sám neověřuje).

### 23.3 ⚠ NÁLEZ: `audit6` MĚL PRAVDU I V TOM, ŽE PADÁ — a můj první dojem byl špatný

Dvě věci, které vypadaly jako regrese a **nejsou**:

1. **`ag-mutace.py` v `audit6-brany-mutace.py`: `exit=1` → `exit=0`.**
   Není to změna kódu v `ag-mutace.py`, ale **oprava kotvy** (§23 Úkol 2):
   skript hledal `39 sloupců`, což v dokumentu **není ani jednou**, takže
   `pocet != 1` a **obě mutace se tiše neprovedly**.
2. **`validate-all (CELEK)`: `exit 1` → `exit 0`.** Tohle **není oprava**.
   V auditu to bylo `exit 1` s poznámkou **„NEPROBĚHLO — PROSTŘEDÍ"**; teď
   je sandbox **`danger-full-access`** místo `workspace-write`, takže validátor
   **může doběhnout**. Je to přesně ten **třetí stav** z `overovani` §7.13:
   *„neproběhlo" se pod širším oprávněním změní na zelenou* — a kdo to neví,
   čte to jako opravu.

**Baseline se tedy posunul, ale ne regresí:** 29 bran → **30** (přidán
`ag-mutace (autorita)`, Úkol 2), nenulových exitů **2 → 1**
(`mutace A: pres-level` — a ten je červený **SPRÁVNĚ**).

### 23.4 Všechny brány po session — a co která OTEVŘELA

| Brána | Výsledek | Co otevřela |
|---|---|---|
| `audit2a-schema.py` | **`exit 0`** | 12 výskytů: 2 souhlasí, 7 záznamů, 3 citace, **0 rozchodů** |
| `ag-mutace.py` | **`exit 0`** | `mutací=2, chyceno=2`, 27 tvrzení z 116 řádků s číslem |
| `handoff-kontrola-uplnost.py` | **83/83** | 0 chybí |
| `kronika-kontrola.py` | **`exit 0`** | 75 omylů, 23 nálezů, 18 sessions, 15 odkazů |
| `audit1-inventar.py` | **`exit 0`** | 101 dokumentů, **žádný sloupec prázdný**; mutační test **3/3** |
| `audit6-brany-mutace.py` | `exit 1` (správně) | 8 testů mimo `g3`: **6 `exit 0`**, 2 problémy = **R6, pojmenované**; brány bez důkazu **10** (beze změny) |
| `g1-diakritika-novych.py` | **`exit 0`** | **466 textových souborů**, 0 vad |
| `g3-brany.py` | **30 bran, 1 nenulový exit** | `ag-mutace (autorita)` → **`2 / 2`** (otevřela a změřila) |
| `audit-snapshot.py` | `exit 1` (správně) | **3 soubory změněné obsahem** (`AGENTS.md`, `overovani/SKILL.md`, `AGENTS.md` jako jádro+koren), **2 jen `mtime`** (`HANDOFF.md`) |
| `hl-rizika-jazyka.py` | **`exit 0`** | 0 očekávaných, **11 přejednaných, 0 vrácených** |
| `audit2a-mutace.py` | **`exit 0`** | 4 mutace, **4 chyceny** |
| `audit2b-over.py` | **`exit 0`** | 4 běhy brány, 2 mutace, `granulí` 0 rozchodů |
| `audit3-hlavicky-over.py` | **`exit 0`** | 2 soubory parsovány **i spuštěny**, 0 souvisejících běhů |
| `audit-snapshot-over.py` | **`exit 0`** | **71/71 hashů přepočítáno z disku** |

> **⚠ `g3-brany.py` SÁM NEMÁ `sys.exit`** — je to **přehled**, ne brána.
> Přidat do něj test tedy znamená, že se jeho stav **objeví ve výpisu**,
> **ne** že něco spadne. Zapsáno jako past do `AGENTS.md` i skillu `overovani`
> (§10.8) — a je to naměřené: `g3` skončil `exit 0` i s jedním nenulovým řádkem.

### 23.5 Co zůstává OTEVŘENÉ

- **`audit2b` má 27 rozchodů, z toho většina je falešných** — veličina
  **`kontrol`** (`(\d+)\s+kontrol`) porovnává **různé brány, které hlásí různé
  počty kontrol SPRÁVNĚ** (23, 59, 61, 65…). Je to **tatáž vada, jakou audit
  vytkl `audit2-rozpory.py`** — a `audit2b` ji má taky, jen o vrstvu níž.
  **Neopravoval jsem to** (zadání žádalo jen `granulí`) a je to **návrh NA22**.
- **`OPATŘENÍ 2 A 3 Z AUDITU NEBYLA ZADÁNÍM PŘIDĚLENA ŽÁDNÉ SESSION** —
  ověřeno: `ZADANI-DOKONCENI-AUDITU.md` §6 je nezmiňuje. **Opatření 2** (popisek
  v `ag-over-cisla.py`) jsem provedl, protože patří k R1 (viz §23.2);
  **opatření 3** (`ag-over-cisla.py` rozšířit na řádek 62) **zůstává otevřené** —
  částečně je kryje nový `audit2a-schema.py`, který tvrzení v próze **už čte**.
- **`audit1-inventar.py` viděl 101 dokumentů, z toho 51 v `_analyza`** a **73 bez
  hlavičky** — číslo proti auditu (**62 z 98**) vzrostlo, protože auditem
  navržené opatření 7 (hlavičky) **není provedené** a dokumenty v `_analyza`
  přibývají. Patří do session B.
- **`g3-brany.py` má 3 řádky s `otevřela: —`** (`C1: důkaz selhání`,
  `C2: mutace N1 (5 běhů)`, `tsc (conductor)`) a **`validate-all (CELEK)` má
  `otevřela:` PRÁZDNÉ** — vzor `NALEZENO (\d+)|VŠE V PO` má druhou alternativu
  **bez skupiny**, takže se vypíše prázdný řetězec místo počtu. Je to
  **kosmetická vada zobrazení** (ne slepota — brána prošla), ale „`exit 0` bez
  počtu je ticho" platí i tady. Zapsáno jako **návrh NA23**.

### 23.6 Vlastní omyly téhle session

**Sedm, všechny v měřidlech — zapsané v §8j.** Dva z nich (`87`, `88`) by
**neodhalilo čtení kódu**; odhalil je až **mutační test**. To je nejlepší
doklad pravidla „napsal jsi test? vrať do kódu vadu a podívej se, že spadne" —
a zároveň **nepříjemný údaj do trendu**: podíl omylů v měřidle se **nezlepšil**.

### 23.7 Proč je zadání pro příští session v NOVÉM souboru, a ne v `NEXT-SESSION-INSTRUKCE.md`

**Změřeno, a rozhodnutí se opírá o obsah, ne o časovou značku:**

| Měření | Výsledek |
|---|---|
| `mtime` souboru při startu session | **17:38:17** |
| `mtime` souboru teď | **18:32:22** — tedy **změnil se** |
| **SHA-256 obsahu** ve snapshotu Úkolu 0 (18:12) | `9c05c6b434d5d026…`, 17 841 B |
| **SHA-256 obsahu** ve snapshotu z 18:32 | `9c05c6b434d5d026…`, 17 841 B |
| **SHA-256 obsahu** na disku teď | `9c05c6b434d5d026…`, 17 841 B |

**Obsah se nezměnil ani o bajt** — `mtime` hnul **mutační test**
(`_analyza\zadani-mutace.py:50` do souboru zapisuje a řádky 100/115/129 ho
vrací zpět), který spouští `audit6-brany-mutace.py`. **Žádná jiná session
v tom souboru nepracuje** — nejsou ani žádné aktivní (nejnovější session
v přehledu je tahle, `16:32:50` UTC).

**Rozhodnutí:** postupoval jsem podle **litery zadání** („když se `mtime`
změnil, napiš nový soubor") a zároveň podle jeho **účelu** (nezašlápnout cizí
práci): zadání pro příští session je v **`ZADANI-PO-AUDITU.md`** a
`NEXT-SESSION-INSTRUKCE.md` zůstal **nedotčený** — jeho obsah je platné zadání
souběžné session a zahodit ho by byla přesně ta škoda, kterou dokumentuje
`SOUBEH-SESSION-NALEZY.md`.

> **⚠ A je to nález o ZADÁNÍ, ne jen o souboru:** kritérium „porovnej `mtime`
> s 17:38" **samo selhalo** — dalo by odpověď „pracuje v něm jiná session",
> která **není pravdivá**. Správné kritérium je **hash obsahu** (dvojice
> snapshotů ho má). Zapsáno jako **návrh NA20**.

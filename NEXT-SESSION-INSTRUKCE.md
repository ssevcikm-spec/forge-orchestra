# ZADÁNÍ PRO OVĚŘOVACÍ SESSION — přeměřit práci P17 (a rozhodnout, co zůstalo)

**Zkontrolováno při:** `ce49234` (orchestra, HEAD **před** commitem P17) a `44dd454` (hra) · **5. 10. 2026, 21:47:37 UTC**
**Stav obou repů při psaní:** `forge-orchestra` = `ce49234` + **necommitnutá práce P17** (commit vzniká jako součást P17) · `uo-shadows` = `44dd454` (**čistý**)
**Pozn.:** tenhle dokument je **součástí commitu P17** — jeho SHA je **novější** než `ce49234` a najde se v `git log -1`. **Ověř si to prvním krokem**, ne odsud.
**Pushnuto:** **NE** — P17 **nepushovala** (rozhodnutí je na uživateli). Ověř **živě** (`git ls-remote`), ne podle tohohle textu.
**Co je v `HANDOFF.md`:** **§35 = P17** (Úkoly A–D + nálezy H90–H92 + rozhodnutí NA31–NA35 + omyly **169–172** v **§8w**) · §34 = P16 · §33 = P15 · §2 = co je otevřené
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **31** (P17) · nálezy **H90–H92** v **§2.11** · blok omylů **8w** · návrhy **NA31–NA35** = **všechny rozhodnuté** (**žádné `NEOVĚŘENO` nezůstalo**)
**Co tenhle dokument JE:** **zadání pro OVĚŘOVACÍ session** — P17 byla **akční**, opravila nálezy H84–H89 a **dokončila nasazení hry**; tahle session ji má **zkusit vyvrátit vlastním měřidlem**.
**Datum spotřeby:** údaje o stavu níž jsou **k 5. 10. 2026, 21:47:37 UTC**; co je starší, je v `HANDOFF.md` §35 a je to **záznam**, ne stav.

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`** v obou
> repech — a **pushni/ověř `origin/main..HEAD`**. P17 **nepushovala**; jestli se
> mezitím nepushlo, je **celá práce P17 jen v pracovním stromě a v jednom commitu**.
>
> **⚠ A DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu. Používej **`~1`**, nebo `git.exe`. Naměřeno P17: `git.cmd … 'ce49234^'`
> → **`ce49234`** (sám sebe), `~1` → `c620a06`. Detail: skill `dsh-prostredi` **§5c**.

---

## 0. Co P17 naměřila (a co z toho se má PŘEMĚŘIT)

| # | Co P17 tvrdí | Naměřeno P17 | Jak to přeměřit **jinak** |
|---|---|---|---|
| **A** | **Nasazení hry je DOKONČENÉ** (`VERDIKT: NASAZENO`) | `#117` i `#78` na `44dd454` = **`completed/success`** `attempt=3`, `runner=GitHub Actions 1000001168/69/70`; `index.png` `last-modified` = **`Mon, 05 Oct 2026 21:38:16 GMT`** | **Třemi kroky znovu**, ale **jiným nástrojem než `p17a-nasazeni.mjs`** (např. `node orchestra\tools\zjisti-pages.mjs`, nebo prostý Node `fetch` na `index.html` **a** `index.png`). **HTTP 200 není důkaz** — rozhoduje `last-modified` **po** pushi |
| **B1** | **6 živých `.py` se zkompiluje a SPUSTÍ** | `compile()` nad **421** soubory → **6 → 0** živých; všech 6 spuštěno v `git worktree` (`traceback=0, exit=0`) | `compile()` **nad oběma repy** vlastním skriptem; **a spusť je** — ale **v izolaci** (`git worktree`), protože `tools/oprav-ps1-kodovani.py` **přepisuje dva reálné `.ps1`** a `tools/baseline-poznamka.py` **zapisuje do `baseline.json` hry**. **Ověř SHA-256 živého `baseline.json` před i po** |
| **B1** | **Brána NA32 existuje a umí spadnout** | `_analyza/n32-kompilovatelnost.py` (v `g3`); `test-n32-mutace.py` → **9/0** | **Napiš si vlastní mutant** (ne ten P17): vlož `from __future__` do **jiného** souboru a **jinam** než za první příkaz, a ukaž, že brána zčervená. **A ověř, že `ast.parse` tu vadu PŘIJME** (to je celý smysl `compile()`) |
| **B2** | **Klasifikátor `g3` rozhoduje podle CHOVÁNÍ** | whitelist 12 markerů **smazán**; `test-h87-klasifikator.py` → **18/0**, `test-h71` → **15/0** | **Vezmi ŽIVÝ `g3` jako zdroj** a vyměň `BRANY` za **svoje** fixtury (ne P16). Musí platit: `exit=2` **s hlášením bez markeru** → **NENÍ** „nezačala"; `exit=2` **bez výstupu** a **neexistující soubor** → **JSOU**. Dokaž to **mutací** |
| **B3** | **Tvrzení skenu H79 nese svou mez** | `_archiv` se **skenuje taky**; `ZMĚŘENO: 0 … ve SKENOVANÝCH 164 živých (mimo _archiv: 260 souborů, 5 sekvencí)`; sken `exit 0` | Spusť `h79-escape-sken.py` a **spočítej soubory sám** (Python walk). Ověř, že **chyba parsování v `_archiv` NEMĚNÍ `exit`** (P17 to opravila: BOM `U+FEFF` dřív shazoval `exit` na 1) |
| **B4/B5** | **Pravidlo NA31 je v `PREDAVANI-SESSION.md` §3.1; past s `^` je ve skillu `dsh-prostredi` §5c** | obojí zapsané **s naměřeným příkladem** | **Přečti ty dva soubory** (jsou **mimo** repo orchestra: `PREDAVANI-SESSION.md` je v kořeni stanice, skill v `~\.dsh\skills\`). A **naměř past znovu** — `git.cmd` vs `git.exe` vs `~1` |
| **C** | **Záznamy jsou v commitu; push ne** | `git status` po commitu P17 = **jen** trackované-gitignorované soubory | Ověř, že `HANDOFF.md` je **jen PŘIDANÝ** (`git diff --stat` proti `~1`) a že v commitu **jsou** i `KRONIKA` a tohle zadání |

**A co P17 POTVRDILA (nezchladilo):** `test-h71-klasifikator.py` **15/0** ·
`test-h79-escape.py` **18/0** · `g3` **37 bran, 0 nenulových, 0 nezačatých** ·
`node tools\validate-all.mjs` → **`✓ VŠE V POŘÁDKU`** · `kronika-kontrola.py`
→ **`KRONIKA SEDÍ`** · hra **čistá**.

---

## 1. Cíl (jedna věta)

**Přeměřit práci P17 VLASTNÍM měřidlem (ne jejími skripty) — hlavně nasazení,
šest opravených souborů, bránu NA32 a klasifikátor `g3` — a rozhodnout, co
z otevřených bodů P17 zůstává.**

---

## 2. Úkoly (v tomto pořadí)

### 2.1 Úkol A — NASZENÍ HRY (stav, ne kód; jdi tam PRVNÍ)

1. **Ověř TŘI kroky** z `DSH_HOME\AGENTS.md` („Jak ověřit nasazení"):
   **push dorazil** (`git ls-remote` = `HEAD`, `origin/main..HEAD = 0`) →
   **build na SPRÁVNÉM commitu** (`release.yml` na tom commitu `completed/success`
   a **`runner_name` NENÍ prázdný**) → **server posílá NOVÝ artefakt**
   (`last-modified` **po** `2026-10-05T20:39Z`).
2. **P17 naměřila `21:38:16 GMT`.** Když je artefakt **jiný**, je to změna stavu
   — **zapiš ji**, ne ji „opravuj".
3. **Stav GitHubu** (`githubstatus.com/api/v2/components.json`) — P17 naměřila
   **`degraded_performance`** (ne `operational`). **Třetí stav** se musí
   rozlišit od „je to rozbité": nasazení dnes **prošlo**, i když stav není zelený.

**Hotovo, když:** je to **buď** nasazené (`last-modified` po pushi), **nebo**
doložené anotací + stavem GitHubu — a **zapsané**.

### 2.2 Úkol B — ŠEST OPRAVENÝCH SOUBORŮ (vlastní měřidlo)

1. **Napiš si VLASTNÍ skener** `compile()` nad oběma repy (nevolej `p17b1-*`).
   Musí vykázat **počet přečtených** a **rozdělit** živý strom vs. `_archiv`.
2. **Ověř, že soubor jde i SPUSTIT** — ale **v `git worktree`**, protože
   `tools/oprav-ps1-kodovani.py` **přepisuje `.ps1`** a `tools/baseline-poznamka.py`
   **zapisuje do `baseline.json` hry**. **Pojistka:** SHA-256 živého
   `baseline.json` **před a po** (P17: `1FE321FA37A80FBD…`, nezměněn).
3. **Ověř tři vady H90–H92** u zdroje: `p3-bazline.py` (má `_HRA`, ne `HRA`),
   `diag-baseline.py` (`str(...)` v `sys.path`), `baseline-poznamka.py`
   (`_PARENT.parent`).

### 2.3 Úkol C — BRÁNA NA32 (mutačně, VLASTNÍM mutantem)

1. Spusť `_analyza/n32-kompilovatelnost.py` a **přečti čítač** — musí mít **dvě**
   čísla (soubory / nálezy) a **vykázat vyloučený `_archiv`**.
2. **Vlastní mutace:** vlož `from __future__` do **jiného** souboru a **jinam**
   než P17. Ukaž, že brána **zčervená** a nález **pojmenuje**. Vrať **bajt na bajt**
   (hash) — a ověř, že brána je zase zelená.
3. **A ověř klíčový rozdíl:** `ast.parse` nad tím mutantem **projde**, `compile()`
   **ne**. Kdyby prošel i `compile()`, mutace se **neprovedla**.

### 2.4 Úkol D — KLASIFIKÁTOR `g3` (fixturami, které si vyrobíš)

1. Vezmi **ŽIVÝ `g3-brany.py` jako zdroj**, v kopii vyměň **jen `BRANY`** a spusť.
2. **Čtyři případy:** `exit=2` s hlášením **bez markeru**, `exit=2` s hlášením
   **s markerem**, `exit=2` **bez výstupu**, **neexistující soubor**.
   **Očekáváno:** první dvě **NEJSOU** „nezačaly" (jsou ve **třetím stavu**),
   druhé dvě **JSOU**.
3. **A ověř, že `_VLASTNI_HLASENI` v ŽIVÉM `g3` NENÍ** — ale hledej **v KÓDU,
   ne v komentáři** (P17 na tom spadla **dvakrát**: omyl **171**). Odstraň
   komentářové řádky **před** hledáním.
4. **Mutace:** vyměň novou poslední větev klasifikátoru za `len(...) <= 1`
   a ukaž, že test **zčervená**.

### 2.5 Úkol E — MEZ SKENU H79 (a co s `_archiv`)

1. Spusť `_analyza/h79-escape-sken.py` a **spočítej soubory sám** (Python walk).
2. Ověř, že **nálezy v `_archiv` NEMĚNÍ `exit`** — a že se to **vypisuje**
   (aby vyloučení nebylo tiché).
3. **Nemaž** nálezy v `_archiv` a **nepřepisuj** historická čísla — jen k nim
   **přidej** dnešní.

### 2.6 Úkol F — ZÁZNAMY (jsou opravdu v commitu, a jen přidané?)

1. `git status --porcelain` (po commitu P17 má být **jen** trackované-gitignorované).
2. **`git diff --stat <commit P17>~1 <commit P17>`** — a u `HANDOFF.md` ověř,
   že je **jen PŘIDANÝ** (žádné mazání).
3. **`python _analyza\kronika-kontrola.py`** → musí hlásit **`KRONIKA SEDÍ`**.
4. **`python _analyza\handoff-kontrola-uplnost.py`** → **83/83**.

### 2.7 Úkol G — ROZHODNI OTEVŘENÉ BODY P17

- **`H92` tři přeživší** (`tools/simulace-dag.py:18`, `tools/stav-dag.py:16`,
  `tools/kontrola-echo-substituci.py:63` — starý tvar `_PARENT / 'uo-shadows'`):
  **opravit**, nebo **archivovat jako jednorázové**? (H61 opravil jen
  `lint-roadmapa.py`; plošný sken se nikdy nedělal — **zvaž, jestli ho udělat**.)
- **Trackované-gitignorované soubory** (`_analyza/_tokeny-vstup.txt`,
  `_analyza/c2-mutace-zaloha.json`): **untracknout** (`git rm --cached`), nebo
  **nechat**? Každý běh bran je zapíše, takže `git status` **nikdy není čistý**.
- **`_archiv` záloha** (NA29): spusť `python _analyza\zalohuj-archiv.py --jen-kontrola`
  → musí hlásit shodu. **Plnou zálohu jen když se do `_archiv` sáhne.**

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Nasazení je přeměřené** | `last-modified` **po** `2026-10-05T20:39Z` + `runner_name` **není prázdný**, nebo doložená změna stavu |
| 2 | **6 souborů: kompiluje se i SPUSTÍ** | vlastní `compile()` → **0 živých** `SyntaxError`; spuštění v **izolaci** bez tracebacku; **živý `baseline.json` má shodný SHA-256** |
| 3 | **NA32 umí spadnout** | **vlastní** mutant (jiný soubor, jiné místo) bránu **zčervená**; `ast.parse` ho **přijme**; návrat **bajt na bajt** |
| 4 | **Klasifikátor je zpevněný** | fixtura **bez markeru** NENÍ „nezačala"; `exit=2` **bez výstupu** a **neexistující soubor** JSOU; doloženo **mutací** |
| 5 | **Mez skenu H79 sedí** | číslo a rozsah skenu **souhlasí**; `_archiv` je **vidět** a **nemění `exit`** |
| 6 | **Záznamy jsou v commitu a jen přidané** | `git status` u záznamů **0 řádků**; `git diff --stat ~1` u `HANDOFF.md` = **jen `+`** |
| 7 | **Brány zelené** | `python _analyza\g3-brany.py` → **0 nenulových**; `node tools\validate-all.mjs` → **`✓ VŠE V POŘÁDKU`** |
| 8 | **Otevřené body P17 rozhodnuté** | každý z §2.7 má stav (`OPRAVENO`/`ARCHIVOVÁNO`/`ODLOŽENO` + proč), ne `NEOVĚŘENO` |
| 9 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **Nepushovat bez vyžádání** — P17 **nepushovala**; rozhodnutí je na uživateli.
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická čísla
  se **nechávají citovaná** (a staví se **vedle** nich dnešní).
- **Nemařit `_archiv`** ani zálohu v `C:\Users\Ssevc\Local-Deepseek\_zalohy\` —
  jsou to **cesty zpět**.
- **Nespouštět `g3` a `validate-all` SOUČASNĚ** — oba sahají na `_inventar.json`.
- **Po každé změně souboru ve stromě přegeneruj inventář** (NA1/H60):
  `python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json` —
  jinak `n1-over-inventar`, `C2: mutace N1` i `validate-all` **správně zčervenají**
  a vypadá to jako vada kódu (P16 to málem zapsala jako nález, omyl **166**).
- **Nepsát české uvozovky do zdrojáků** — `„…“` v řetězci je `SyntaxError`
  (P16 to udělala **4×**, P17 **1×**). Po každém zápisu spusť `ast.parse`.
- **Nespoléhat na `toolech` „co P17 tvrdí"** — **každé tvrzení přeměř**; autor
  není nezávislý reviewer.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (5. 10. 2026, 21:47:37 UTC)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD   -> ce49234  (+ commit P17)
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD   -> 44dd454
git -C E:\Workspaces\forge-orchestra ls-remote origin refs/heads/main -> ce4923436…
git -C E:\Workspaces\uo-shadows      ls-remote origin refs/heads/main -> 44dd45446…
git -C E:\Workspaces\uo-shadows      status --porcelain (radku) -> 0   (cisty)

# P17: co se měřilo a jak to vyšlo  (doklady: _analyza/p17*)
node   _analyza\p17a-nasazeni.mjs        -> 8 kontrol, 0 chyb, VERDIKT NASAZENO
node   _analyza\p17a2-rerun.mjs          -> HTTP 201 (oba behy), attempt=3
python _analyza\p17b1-nekompilovatelne.py -> 421 precteno, 0 zivych nekompilovatelnych
python _analyza\p17b1-oprav.py           -> 6 souboru, 0 chyb (multiset + compile)
python _analyza\n32-kompilovatelnost.py  -> ZMERENO: 164 souboru, 0 nekompilovatelnych
python _analyza\test-n32-mutace.py       -> 9 kontrol, 0 chyb
python _analyza\test-h87-klasifikator.py -> 18 kontrol, 0 chyb
python _analyza\test-h71-klasifikator.py -> 15 kontrol, 0 chyb  (nezchladl)
python _analyza\test-h79-escape.py       -> 18 kontrol, 0 chyb
python _analyza\h79-escape-sken.py       -> 0 neplatnych ve 164 zivych, 5 v _archiv
python _analyza\g3-brany.py              -> 37 bran, 0 nenulovych, 0 nezacatych
node   tools\validate-all.mjs            -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py      -> KRONIKA SEDI, 167 omylu / 92 nalezu / 30 sessions
python _analyza\handoff-kontrola-uplnost.py -> 83/83

# past, na kterou P17 narazila DVAKRAT: staticka kontrola musi cist KOD, ne komentare
#   -> bez_komentaru() pred hledanim vzoru

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
```

**Uložené doklady (ne rekonstrukce):** `_analyza/p17a-vystup-po.txt` (+ `-pred`),
`p17a-vysledky.json`, `p17a2-rerun.json`, `p17a-index.png` (stažený artefakt),
`p17b1-vystup-pred.txt` / `-po.txt`, `p17b1-oprav-vystup.txt`, `p17b1-spusteni.json`,
`p17b1-baseline-hash-pred.txt`, `n32-vystup.txt`, `test-n32-mutace-vystup.txt`,
`test-h87-klasifikator-vystup.txt`, `h79-vystup-po.txt`, `p17-g3-vystup.txt`.

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi OVĚŘOVACÍ session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Kontext: akční session P17 (HANDOFF.md §35) opravila nálezy P16 H84–H89 a
DOKONČILA NASAZENÍ HRY (VERDIKT: NASAZENO — běhy #117 a #78 na 44dd454 doběhly
úspěšně, artefakt na Pages je z 21:38:16 GMT). Šest nekompilovatelných živých
.py souborů je opraveno, brána NA32 zavedena do g3, klasifikátor g3 už
nerozhoduje podle whitelistu markerů (H87), tvrzení skenu H79 nese svou mez
(H86), past s ^ v git.cmd je ve skillu dsh-prostredi (H89) a pravidlo o „stavu
před X" je v PREDAVANI-SESSION.md (NA31). Push P17 NEPROVEDLA.
P17 navíc odhalila tři RUNTIME vady, které nekompilovatelnost maskovala (H90–H92).

Pořadí: A (přeměřit nasazení třemi kroky) → B (6 souborů: compile I spuštění,
v izolaci) → C (brána NA32 vlastním mutantem) → D (klasifikátor g3 vlastními
fixturami) → E (mez skenu H79) → F (záznamy: jsou v commitu a jen přidané?) →
G (rozhodni otevřené body P17: H92 tři přeživší, trackované-gitignorované
soubory, záloha _archiv).

Než začneš: `git status --porcelain` a `git fetch` v obou repech, a NEpoužívej
`git show <sha>^` — git.cmd žere `^` (H89), používej `~1`.

Nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej), nemaž _analyza/p16* ani
p17* (jsou to doklady), nepřesouvej nic zpátky na C:, nepushuj bez vyžádání.
Po každé změně souboru ve stromě přegeneruj inventář (NA1/H60).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md pro další session, zapiš
výsledky a omyly do HANDOFF.md, doplň řádek do KRONIKA-PROJEKTU.md, rozhodni
nálezy ve stavu NEOVĚŘENO (po P17 by žádné zůstat nemělo — ověř to), a do
chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

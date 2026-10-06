# ZADÁNÍ PRO DALŠÍ SESSION — rozhodnout, co s ověřenou prací (P17 + P18)

**Zkontrolováno při:** `8011f83` (orchestra — **měření P18 proběhlo na tomto commitu P17**) a `44dd454` (hra) · **6. 10. 2026, 05:23:39 UTC**
**Stav obou repů při psaní:** `forge-orchestra` = `8011f83`, vzdálená `origin/main` je o **4 commity zpět** na `ce49234` (**nepushnuto: P17 + P18, P18b, P18c**) · `uo-shadows` = `44dd454`, vzdálená `origin/main` je **shodná**, strom **čistý**
**Ověřeno živě:** `git ls-remote origin refs/heads/main` → orchestra **`ce49234`**, hra **`44dd454`**
**GIT (živě, při předání):** `HEAD` = **`4506b2c`**, `origin/main..HEAD` = **4 commity** (P17 `8011f83` + **P18, P18b, P18c** — všechny tři jsou záznamy/doklady, ne kód navíc), pracovní strom **čistý (0 řádků)**

> **⚠ P18 JE COMMITNUTÁ — a `zadani-kontrola.py` proto SPRÁVNĚ VARUJE.**
> Uživatel 6. 10. 2026 rozhodl **„commitni vše, co můžeš"**, takže záznamy
> (`HANDOFF.md` §36 + §8x, `KRONIKA-PROJEKTU.md` řádek 32 a §2.12), **doklady
> `_analyza/ov-*`**, opravené nástroje i **tohle zadání** jsou **v jednom
> commitu P18** (vznikl nad `8011f83`). **Tím vzniká `přibylo commitů: 1`** —
> a to **není vada zadání ani session**: je to **vlastnost odkazu na vlastní
> commit** (SHA commitu závisí na jeho obsahu). `zadani-kontrola.py` to hlásí
> jako **varování** a **právě to má dělat** — nutí příští session **přeměřit
> stav živě** místo věřit hlavičce. **Historie to má stejně** (P15, P16 i P17
> commitly zadání; u P16 to bylo součástí nálezu **H88**).
> **Co z toho plyne pro tebe:** než začneš pracovat, udělej
> **`git status --porcelain` + `git fetch`** a **přeměř `origin/main..HEAD`** —
> číslo v hlavičce je **stav v čase měření**, ne dnešek.

> **⚠ PROČ JE V HLAVIČCE `8011f83`, A NE COMMIT P18 — a je to ZÁMĚR.**
> `8011f83` je **commit, na kterém P18 SKUTEČNĚ MĚŘILA** (a je to i **rodič**
> commitu P18), takže je to **správná kotva měření** — ne omyl v zápisu.
> Kdyby tu stálo SHA commitu P18, odkazovalo by dokument na commit, jehož obsah
> **závisí na tomhle textu** — a `zadani-kontrola.py` by po každé opravě zadání
> hlásil jiné číslo. **Jednou to tak je a bude** (`přibylo commitů: 1`), a je to
> **vidět**: hlavička se **neopravuje na dnešek**, protože pak by přestala být
> záznamem o tom, **proti čemu se měřilo** (nález **NA31**).

**Co je v `HANDOFF.md`:** **§36 = P18** (Úkoly A–G + nálezy H93–H96 + rozhodnutí otevřených bodů P17 + omyly **173–184** v **§8x**) · §35 = P17 · §34 = P16 · **§2 = co je otevřené**
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **32** (P18) · nálezy **H93–H96** v **§2.12** · blok omylů **8x** · **souhrn: 24 bloků, 31 sessions, 178 omylů (152 = 85 %), 52 nálezů**
**Co tenhle dokument JE:** **zadání pro ROZHODOVACÍ session** — P18 byla **ověřovací** a **všechna tvrzení P17 potvrdila**; nic k opravě po ní **nezbylo povinného**. Zbývá **rozhodnout**, co s ověřenou prací (push) a co s **dvěma neškodnými, ale matoucími** nálezy.
**Datum spotřeby:** údaje o stavu níž jsou **k 6. 10. 2026, 05:23:39 UTC**; co je starší, je v `HANDOFF.md` **§36** a je to **záznam**, ne stav.

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech — a **ověř `origin/main..HEAD` ŽIVĚ** (`git ls-remote`), ne
> podle tohohle textu. Uživatel mohl mezitím pushnout, nebo se stav změnil.
>
> **⚠ A DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu. Používej **`~1`**, nebo **`git.exe`**. Naměřeno P17: `git.cmd … 'ce49234^'`
> → **`ce49234`** (sám sebe), `~1` → `c620a06`. Detail: skill `dsh-prostredi` **§5c**.

---

## 0. Co P18 naměřila a co je HOTOVÉ (neopakuj to znovu)

**Všechna tvrzení P17 byla přeměřena VLASTNÍM měřidlem a VŠECHNA POTVRZENA.**
Tabulka je tu proto, aby se **nemuselo měřit znovu** — a aby bylo vidět, **co
za tím tvrzením stojí**. Kdo chce přeměřovat, ať **použije jiný nástroj**, než
jaký je v posledním sloupci.

| # | Co P18 naměřila | Čím (doklad v `_analyza/`) |
|---|---|---|
| **A** | **`VERDIKT: NASAZENO`** — 10 kontrol, 0 chyb. `origin/main..HEAD = 0` (hra) · běh **`#78`** na `44dd454` **`completed/success`** s **NEprázdným `runner_name`** (`GitHub Actions 1000001168`/`1170`) · `index.html` **i** `index.png` `last-modified` = **`Mon, 05 Oct 2026 21:38:16 GMT`** (po `20:39Z`) | `ov-a-nasazeni.mjs`, `ov-a-vystup.txt`, `ov-a-vysledky.json` |
| **A′** | **Změna stavu:** `githubstatus.com` hlásí u **všech pěti** sledovaných složek **`operational`** — P17 měřila **`degraded_performance`** | totéž |
| **B** | **0 živých nekompilovatelných**; **6/6 opravených souborů SPUŠTĚNO** (`traceback=0`, `exit=0`) v **izolaci** (`git worktree` + **junction na hru**); živý `baseline.json` **bajt na bajt shodný** (`1FE321FA37A80FBD…`) | `ov-b1-compile.py`, `ov-b2-spusteni.py`, `ov-b2-spusteni.json` |
| **C** | **NA32 umí spadnout** — 18 kontrol, 0 chyb: vlastní mutant (`ov-b1-compile.py:12`) bránu **zčervenal**, nález **pojmenovala**, `ast.parse` ho **přijal** a `compile()` **odmítl**, návrat **bajt na bajt** | `ov-c-n32-mutant.py`, `ov-c-vysledky.json` |
| **D** | **Klasifikátor `g3` je zpevněný** — 38 kontrol, 0 chyb: fixtura **bez markeru** NENÍ „nezačala", `exit=2` **bez výstupu** a **neexistující soubor** **JSOU**; `_VLASTNI_HLASENI` **0× v KÓDU**; **tři mutace** odhaleny | `ov-d-klasifikator.py`, `ov-d-vysledky.json` |
| **E** | **Mez skenu H79 sedí** — 17 kontrol, 0 chyb: vlastní počet souborů **souhlasí** (**173** živých / **260** `_archiv`), vlastní sken **0 / 5** souhlasí, a **mutace OBĚMA SMĚRY**: vadný soubor v `_archiv` `exit` **NEMĚNÍ** (a je vidět), **totéž** v živém stromě `exit` **MĚNÍ** | `ov-e-h79-mez.py`, `ov-e-vysledky.json` |
| **F** | **Záznamy:** `KRONIKA SEDÍ` · `handoff-kontrola` **83/83** · HANDOFF má **5 ubraných řádků**, ale **nic se neztratilo** (tatáž věta je v novém na ř. 6675 jako „**PŮVODNÍ STAV: nepushnuto**") | `git diff --numstat 8011f83~1 8011f83` |
| **G** | **H92 tři přeživší OPRAVENY** (naměřeno: cesta vedla na **neexistující** `…\forge-orchestra\uo-shadows`; po opravě všechny tři **exit 0**) · **trackované-gitignorované soubory UŽ NEJSOU** (P17 je untrackla) · **`ZÁLOHA SEDÍ`** (347 souborů, shodný SHA-256) | `ov-g-h92-sken.py`, `ov-g-neovereno.py` |
| **brány** | `g3` **37 bran, 0 nenulových, 0 nezačatých, 0 nedosazených** · `validate-all` **`✓ VŠE V POŘÁDKU`** · inventář přegenerován | `ov-g3-vystup.txt`, `ov-validate-all-vystup.txt` |
| **NEOVĚŘENO** | **0** — ověřeno vlastním skriptem: **35 návrhů** (NA1–NA35) má stav a **83 nálezů** v HANDOFF žádné `NEOVĚŘENO` | `ov-g-neovereno.py`, `ov-g-neovereno-vystup.txt` |

---

## 1. Cíl (jedna věta)

**Rozhodnout, co s ověřenou prací P17 + P18 — pushnout commity, a rozhodnout
dva neškodné nálezy P18 (H93, H94) a otázku blokujícího `g3` — a zapsat rozhodnutí.**

---

## 2. Úkoly (v tomto pořadí)

### 2.1 Úkol A — PUSH (rozhodnutí uživatele; bez něj je všechno jen lokálně)

1. **Nejdřív `git status --porcelain` a `git diff --stat`** v obou repech a **ukázat
   je uživateli** — pravidlo `AGENTS.md`: *nepushovat bez vyžádání*.
2. **Co je k pushi:** `forge-orchestra` má **`origin/main..HEAD = 4`** — commit
   `8011f83` (**P17**, 66 souborů), **`233e502`** (**P18**: záznamy + doklady +
   opravené nástroje + tohle zadání) a **dva navazující `P18b`/`P18c`** (poučení
   o inventáři). Hra je **v sync** (`44dd454`), **nic k pushi**.
3. **P18 JE UŽ COMMITNUTÁ** (rozhodnutí uživatele 6. 10. 2026: „commitni vše,
   co můžeš") — takže **k pushi jsou všechny čtyři commity** a **žádné rozhodování
   o commitu už nezbývá**. Zkontroluj jen, že ve stromě **nezůstalo nic
   necommitnutého** kromě případných nových změn.
4. **Push přes PAT ze souboru** (`.secrets/github_pat.txt`) — **nikdy ho nevypisuj**
   ani nepiš do historie příkazů. Git přes schannel padá → `orchestra\tools\git.cmd`.
5. **Po pushi ověř TŘEMI kroky** (`DSH_HOME\AGENTS.md`, „Jak ověřit nasazení"):
   push dorazil (`ls-remote` = `HEAD`, `origin/main..HEAD = 0`) → build na
   **správném** commitu → server posílá **nový** artefakt (`last-modified` **po**
   čase pushi). **`HTTP 200` není důkaz.**

**Hotovo, když:** je **rozhodnuto** (pushnuto, nebo výslovně NE s důvodem)
a stav je **přeměřený živě**.

### 2.2 Úkol B — H93: `snapshot-*/` ve vylučovacím seznamu brány NA32

**Nález (zapsaný, NEopravený):** `_analyza/n32-kompilovatelnost.py` vylučuje
`.git` a `_archiv`, ale **ne** archivní snapshoty — takže
**`_analyza/snapshot-20261002-181237/skill/overovani/zmen.py`** a
**`…-183213/…`** se počítají jako **ŽIVÝ kód**.

1. **Přeměř to sám:** spočítej `.py` v orchestra s vylučovacím seznamem NA32
   a bez snapshotů. P18 naměřila **176** vs **162** (rozdíl **14**; **2** jsou
   snapshoty, zbytek dělá jiný filtr `_archiv`). Hledej **soubor po souboru**,
   ne jen součty.
2. **Rozhodni:** přidat `snapshot-*` do vylučovacího seznamu, nebo to nechat
   a **jen to vykázat**? Argumenty: oba snapshoty jsou **zmrazené kopie**
   (needitují se), takže „vadný živý soubor" v nich je **falešný poplach** —
   ale taky **neškodí**, protože `n32` **vykazuje**, kolik souborů zkontroloval.
3. **Když budeš měnit bránu, dolož to mutantem** (vlož vadný `.py` **do snapshotu**
   → brána **nesmí** zčervenat; vlož ho **do živého stromu** → **musí**).
   **A vrať to bajt na bajt.**
4. **Po každé změně souboru ve stromě přegeneruj inventář** (NA1/H60).

### 2.3 Úkol C — H94: čtyři mrtvé podpisy v klasifikátoru `g3`

**Nález (zapsaný, NEopravený):** `_PODPIS_CHYBEJICIHO_SOUBORU` má **8 podpisů**,
ale na této stanici mohou zabrat **jen 4**:
`can't open file`, `Cannot find module`, `MODULE_NOT_FOUND`,
`No such file or directory`. **Mrtvé jsou:** `no such file or directory`
(malá písmena), `WinError 2`, `The system cannot find the file`, `is not recognized`.

1. **Přeměř to sám** — spusť `python` **i** `node` nad neexistující cestou
   a porovnej **skutečný** výstup se seznamem. **Nevěř P18.**
2. **Pozor na klíčovou věc:** `can't open file` a `No such file or directory`
   chytají **TENTÝŽ případ** (oba jsou ve výstupu Pythonu). Odebrat **jeden**
   tedy **nic nezmění** — P18 to naměřila. Když budeš mutovat, **uber všechny živé**.
3. **Rozhodni:** nechat (obrana do budoucna, kdyby se text interpretu změnil),
   nebo **zúžit na živé** a **mrtvé pojmenovat**? Argument pro zúžení: **mrtvá
   položka v seznamu je slepé místo** — vypadá jako pokrytí, ale nechytá nic.
   Argument proti: jsou to **jiné texty**, ne záloha — při změně Pythonu/Node
   by pomohly jen náhodou.
4. **Ať rozhodneš jakkoli, napiš k seznamu, KTERÉ podpisy jsou na této stanici
   živé a čím to bylo naměřeno** — dnes to v kódu není.

### 2.4 Úkol D — má `g3` být BLOKUJÍCÍ brána?

`g3-brany.py` **nemá `sys.exit`** — je to **přehled**, ne brána (ví to i komentář
v něm). Nález **NA23b** říká, že kdyby se měl stát blokujícím, musí znát **které**
nenulové exity jsou **správné** (dnes `C2: mutace N1` končí `exit=0`, ale
`? BRÁNY, KTERÉ BĚŽELY, ALE NEVYKÁZALY ČÍTAČ (1)` je **přiznaný** stav).

1. **Přečti si, co dnes `g3` vykazuje** a **co z toho je „správně nenulové"**.
2. **Rozhodni:** nechat jako přehled (a **napsat to do dokumentace**), nebo
   zavést **baseline očekávaných exitů** a `sys.exit` doplnit.
3. **Když zavedeš `sys.exit`, MUSÍŠ doložit, že umí spadnout** — jinak je to
   „brána, která nemá jak selhat".

### 2.5 Úkol E — ZÁZNAMY A OVĚŘENÍ STAVU (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session.
2. **Zapiš výsledky a omyly do `HANDOFF.md`** (nový oddíl; **jen přidávej**).
3. **Doplň řádek do `KRONIKA-PROJEKTU.md`** (tabulka sessions + tabulka omylů
   + její `celkem` — **všechny tři**, jinak se součet rozejde).
4. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
5. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all`
   (**NE SOUČASNĚ** — oba sahají na `_inventar.json`).
6. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **O pushi je ROZHODNUTO** | buď `origin/main..HEAD = 0` u obou repů (a **přeměřeno živě**), nebo zapsané NE s důvodem |
| 2 | **H93 rozhodnutý** | `snapshot-*` buď vyloučen (s mutantem), nebo výslovně ponechán s důvodem |
| 3 | **H94 rozhodnutý** | seznam podpisů buď zúžen, nebo ponechán — a **vždy** s vypsanými živými podpisy a jejich měřením |
| 4 | **`g3` má rozhodnutí** | přehled vs. blokující, zapsané v dokumentaci |
| 5 | **Záznamy sedí** | `kronika-kontrola.py` → **`KRONIKA SEDÍ`**; `handoff-kontrola-uplnost.py` → **83/83** |
| 6 | **Brány zelené** | `g3` → **0 nenulových, 0 nezačatých**; `validate-all` → **`✓ VŠE V POŘÁDKU`** |
| 7 | **Žádné `NEOVĚŘENO`** | ověřeno skriptem, ne dojmem |
| 8 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **Nepushovat bez vyžádání** — P17 ani P18 nepushovaly; rozhodnutí je na uživateli.
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická čísla
  se **nechávají citovaná** (a staví se **vedle** nich dnešní).
- **Nemazat `_analyza/p16*`, `p17*` ani `ov-*`** — jsou to **doklady**.
- **Nepřesouvat nic zpátky na `C:`**; `_archiv` a zálohu v
  `C:\Users\Ssevc\Local-Deepseek\_zalohy\` **nemařit** (jsou to cesty zpět).
- **Nespouštět `g3` a `validate-all` SOUČASNĚ** — oba sahají na `_inventar.json`.
- **Po každé změně souboru ve stromě přegeneruj inventář** (NA1/H60):
  `python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json`
  — jinak `n1-over-inventar`, `C2: mutace N1` i `validate-all` **správně zčervenají**
  a vypadá to jako vada kódu (P16 to málem zapsala jako nález, omyl **166**;
  **P18 to zažila taky** a vyřešilo to druhé přegenerování).
- **Nepsát české uvozovky do zdrojáků** — `„…“` v řetězci je `SyntaxError`.
  Po každém zápisu spusť `ast.parse`.
- **Nepoužívat `python - <<'PY'`** (heredoc v PowerShellu **neexistuje**) ani
  `python -c` s regexy/`$()` — **piš skript do souboru** (`dsh-prostredi` §3d/§3e/§3f).
- **Nespoléhat na to, „co P18 tvrdí"** — **každé tvrzení přeměř**; autor není
  nezávislý reviewer. **A platí to i na tenhle dokument.**

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (6. 10. 2026, 05:23:39 UTC — PŘED commitem P18)
#   ⚠ hodnoty níž jsou STAV V ČASE MĚŘENÍ; po commitu P18 se HEAD posunul.
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD      -> 8011f83  (commit P17 = kotva měření P18)
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main -> ce49234
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 1   (NEPUSHNUTO)  [po commitu P18: 2]
git -C E:\Workspaces\forge-orchestra status --porcelain (radku)  -> 21  (doklady a zaznamy P18)  [po commitu P18: 0]
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD      -> 44dd454
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD -> 0   (v sync)
git -C E:\Workspaces\uo-shadows      status --porcelain (radku)  -> 0   (cisty)
git ls-remote (orchestra) -> ce4923436…   (git ls-remote (hra) -> 44dd45446…)

# PO COMMITU P18 (naměřeno 6. 10. 2026 před zápisem tohohle zadání)
git -C E:\Workspaces\forge-orchestra log --oneline -2
  -> <P18> P18: ověření práce P17 vlastním měřidlem, oprava H92 a nálezy H93–H96
  -> 8011f83 P17: oprava nálezů H84–H89, dokončení nasazení hry a zpevnění bran
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 2   (NEPUSHNUTO)
git -C E:\Workspaces\forge-orchestra status --porcelain -> 0 radku (cisto)

# P18: co se měřilo a jak to vyšlo  (doklady: _analyza/ov-*)
node   _analyza\ov-a-nasazeni.mjs          -> 10 kontrol, 0 chyb, VERDIKT NASAZENO
python _analyza\ov-b1-compile.py           -> 163 zivych precteno, 0 nekompilovatelnych (260 _archiv, 4 nalezy)
python _analyza\ov-b2-spusteni.py          -> 6/6 spusteno, 0 tracebacku, baseline.json shodny
python _analyza\ov-c-n32-mutant.py         -> 18 kontrol, 0 chyb
python _analyza\ov-d-klasifikator.py       -> 38 kontrol, 0 chyb
python _analyza\ov-e-h79-mez.py            -> 17 kontrol, 0 chyb
python _analyza\ov-g-h92-sken.py           -> 57 SPRÁVNĚ, 0 RIZIKO (1 falesny poplach = lint-roadmapa fallback)
python _analyza\ov-g-neovereno.py          -> 35 navrhu a 83 nalezu, 0 NEOVĚŘENO
python _analyza\n32-kompilovatelnost.py    -> ZMERENO: 176 souboru, 0 nekompilovatelnych, 260 vylouceno
python _analyza\g3-brany.py                -> 37 bran, 0 nenulovych, 0 nezacatych, 0 nedosazenych
node   tools\validate-all.mjs              -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py        -> KRONIKA SEDI, 178 omylu / 96 nalezu / 31 sessions
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\zalohuj-archiv.py --jen-kontrola -> ZALOHA SEDI (347 souboru, shodny SHA-256)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ IZOLACE: `git worktree` MUSÍ ležet uvnitř `E:\Workspaces` (jinak se změní
# `_REPO.parent` a `baseline-poznamka.py` spadne na FileNotFoundError), a MUSÍ
# mít junction `uo-shadows` na živou hru. A NESMÍ ležet v měřeném stromě
# (kontaminuje počty) — patří do gitignorované `_analyza/*-scratch/`.
```

**Uložené doklady (ne rekonstrukce):** `_analyza/ov-a-nasazeni.mjs`, `ov-a-vystup.txt`,
`ov-a-vysledky.json`, `ov-a-index.html`, `ov-b1-compile.py`, `ov-b1-vystup.txt`,
`ov-b2-spusteni.py`, `ov-b2-vystup.txt`, `ov-b2-spusteni.json`, `ov-c-n32-mutant.py`,
`ov-c-vystup.txt`, `ov-c-vysledky.json`, `ov-d-klasifikator.py`, `ov-d-vystup.txt`,
`ov-d-vysledky.json`, `ov-e-h79-mez.py`, `ov-e-vystup.txt`, `ov-e-vysledky.json`,
`ov-f-rozdil-poctu.py`, `ov-f-rozdil-vystup.txt`, `ov-g-h92-sken.py`, `ov-g-h92-vystup.txt`,
`ov-g-neovereno.py`, `ov-g-neovereno-vystup.txt`, `ov-g3-vystup.txt`,
`ov-validate-all-vystup.txt`.

**⚠ Šest ověřovacích skriptů `ov-*` NENÍ zařazeno do `g3`** — rozhodnutí uživatele
6. 10. 2026: **zůstávají doklady** (`ov-a` je **stavová** brána, `ov-f` je
jednorázová diagnostika). Kdyby se měly zařadit, patří tam **jen ty opakovatelné**
(`ov-b1`, `ov-e`, `ov-g-h92-sken`, `ov-g-neovereno`).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi ROZHODOVACÍ session. Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ.

Kontext: ověřovací session P18 (HANDOFF.md §36) PŘEMĚŘILA práci P17 vlastním
měřidlem a VŠECHNA její tvrzení POTVRDILA: nasazení hry je dokončené (běh #78 na
44dd454 completed/success s reálným runnerem, artefakt na Pages z 21:38:16 GMT),
0 živých nekompilovatelných souborů a všech 6 opravených se i SPUSTÍ, brána NA32
umí spadnout vlastním mutantem, klasifikátor g3 rozhoduje podle chování, mez
skenu H79 sedí (mutace oběma směry), záznamy jsou v commitu a KRONIKA SEDÍ.
P18 navíc OPRAVILA tři přeživší z H92 a zjistila, že trackované-gitignorované
soubory už P17 untrackla. Push P17 ANI P18 NEPROBĚHL (origin/main..HEAD = 4 —
P17 i P18 JSOU COMMITNUTÉ, jen nepushnuté).
P18 odhalila dva neškodné, ale matoucí nálezy: H93 (brána NA32 nezná snapshot-*/)
a H94 (klasifikátor g3 má 8 podpisů, ale živé jsou jen 4).

Pořadí: A (rozhodnout push a ověřit ho třemi kroky) → B (H93: snapshot-*/) →
C (H94: mrtvé podpisy) → D (má být g3 blokující?) → E (záznamy a ověření stavu).

Než začneš: `git status --porcelain` a `git fetch` v obou repech, a NEpoužívej
`git show <sha>^` — git.cmd žere `^` (H89), používej `~1`.

Nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej), nemaž _analyza/p16*, p17*
ani ov-* (jsou to doklady), nepřesouvej nic zpátky na C:, nepushuj bez vyžádání.
Po každé změně souboru ve stromě přegeneruj inventář (NA1/H60).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md pro další session, zapiš
výsledky a omyly do HANDOFF.md, doplň řádek do KRONIKA-PROJEKTU.md (včetně
souhrnu celkem), rozhodni nálezy ve stavu NEOVĚŘENO (ověř, že žádné nejsou),
a do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

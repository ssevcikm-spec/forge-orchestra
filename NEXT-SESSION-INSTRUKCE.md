# ZADÁNÍ PRO DALŠÍ SESSION — vrátit se k VĚCNÉ PRÁCI (hra / conductor), měřidla jsou dočerpaná

**Zkontrolováno při:** `b781c84` (orchestra — **commit, na kterém měřila P20**, a zároveň její rodič) · hra `44dd454` · **6. 10. 2026, 13:2x UTC**
**Stav obou repů při psaní:** `forge-orchestra` = `b781c84`, `origin/main` = **`b781c84`** · `uo-shadows` = `44dd454`, `origin/main` **shodná**, strom **čistý** · **P20 NENÍ PUSHNUTÁ** (push je rozhodnutí uživatele) — po commitu P20 se `HEAD` posune o **1** a `origin/main..HEAD` bude **1**
**Ověřeno živě:** `git ls-remote origin refs/heads/main` — orchestra **`b781c84`**, hra **`44dd454`** (měřeno **před** commitem P20; po něm viz „přibylo commitů" níž)
**GIT (živě, při předání):** `HEAD` orchestry je **`b781c84`** + **1 commit P20** (záznamy + doklady `p20-*` + opravené brány `g3`/`h79` + opravené doklady) — **NEPUSHNUTÝ**

**Co je v `HANDOFF.md`:** **§38 = P20** (Úkoly A–D + nálezy **H101–H103** + rozhodnutí + omyly **195–210** v **§8z**) · **§2.11 = stav otevřených bodů po P20** (**tady je dnešní stav**; §2.10 je záznam k P19 a dvě jeho položky už neplatí) · §37 = P19 · §36 = P18
**Co je v `KRONIKA-PROJEKTU.md`:** řádek **34** (P20) · nálezy **H101–H103** v **§2.14** · blok omylů **8z** · **souhrn: 26 bloků, 33 sessions, 205 omylů (178 = 87 %), 54 nálezů**
**Co tenhle dokument JE:** **zadání pro ROZHODOVACÍ session P21** — P20 **rozhodla a provedla** všechny tři zbývající věci z fronty technického dluhu (`g3` soudí červené, BOM v `.py`, zařazení ověřovacích skriptů). **Fronta měřidel je tím VYČERPANÁ.** Další session má dělat **věcnou práci** — ne další měřidla.
**Datum spotřeby:** údaje o stavu níž jsou **k 6. 10. 2026, 13:2x UTC**; co je starší, je v `HANDOFF.md` **§38** a je to **záznam**, ne stav.

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech — a **ověř `origin/main..HEAD` ŽIVĚ** (`git ls-remote`), ne
> podle tohohle textu. Uživatel mohl mezitím pushnout, nebo se stav změnil.
>
> **⚠ A DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu. Používej **`~1`**, nebo **`git.exe`**. Detail: skill `dsh-prostredi` **§5c**.
>
> **⚠ A TŘETÍ:** **`Set-Content -Encoding utf8` v PowerShellu přidá do `.py` BOM**
> → soubor přestane být zkompilovatelný a **NA32 ho právem vykáže** (omyl **189**).
> Kód edituj **`edit`/`write` toolem**; po zápisu zkontroluj **první tři bajty**
> (`.py` **NESMÍ** mít BOM, `.ps1` **MUSÍ** — od P20 je to **pravidlo v `AGENTS.md`**).
>
> **⚠ A ČTVRTÁ (nově z P20, omyl 206):** **NEDĚLEJ KOTVU Z ŘÁDKU, KTERÝ SE TI
> NAČTE ZKRÁCENÝ.** Při vkládání řádku do kroniky se mi řádek načetl jen po
> **2000 znacích**, takže jsem „vložením" **nahradil celý řádek** zkráceným
> textem. Když je řádek delší než okno, **veď zápis programově** (vzor:
> `_analyza/p20-oprav-kroniku.py` bere řádek **z blobu v `HEAD`**).

---

## 0. Co P20 naměřila a co je HOTOVÉ (neopakuj to znovu)

| # | Co P20 udělala | Výsledek (doklad v `_analyza/`) |
|---|---|---|
| **A** | **`g3` SOUDÍ ČERVENÉ** (NA23b vyřešen) | `OCEKAVANE_NENULOVE = {"zadání kontrola": 1}` — **kód v deklaraci je naměřený** (brána umí `0` i `1`). `p20-a-kody-bran.py` **7/0**, `p20-a-kontroly.py` **18/0** (nedeklarovaná → `1`, deklarovaná → `0`, jiný kód → `1`, visutá → `1`, zelená → poznámka) |
| **B** | **BOM v `.py` ZAKÁZÁN** | `p20-b-bom-mereni.py` **16/0** — spuštění funguje, `compile()` **i `ast.parse()`** ho odmítnou; fixtura v **živém** stromě hry → **NA32 i H79** `exit 1`. Pravidlo v **`AGENTS.md`** |
| **B2** | **H101 — tichá díra v H79** (nový nález) | Nečitelný `.py` se **tiše vynechával** (H79 `exit 0`, NA32 `exit 1` o témž stromě). Opraveno: počítá a pojmenovává; mrtvý `utf-8-sig` fallback odebraný. `p20-b2-necitelne.py` **12/0**, `p20-b2-kontroly.py` **12/0** |
| **C** | **8 kandidátů rozhodnuto — ani jeden do `g3`** | Dva nemají čítač, pět zapisuje do stromu. `g3` zůstává na **37 branách**. **Doklady se ale hlídají:** `p20-d-doklady.py` pouští **všech 21** (jeden červený = H103, falešný poplach) |
| **C2** | **Rozhodnutí A rozbilo 3 starší doklady** | `ov-e` **17/0**, `p19-d` **18/0**, `p19-c` **28/0**, `ov-d` **40/0** — všechny opraveny (byly to doklady, které zestaraly se smlouvou) |
| **D** | **Brány a záznamy** | `g3` **37 bran, 1 nenulový (deklarovaný), exit 0** · `validate-all` **✓ VŠE V POŘÁDKU** · `KRONIKA SEDÍ` (**201/103/33**) · handoff **83/83** · **`NEOVĚŘENO` = 0** · inventář přegenerován **jako poslední krok** |
| **nálezy** | **H101** (tichá díra H79) · **H102** (doklad P18 tvrdil `>= 6` podpisů, P19 jich má 4) · **H103** (H92 sken = **falešný poplach** na `lint-roadmapa.py:30`) | `HANDOFF.md` §38.6, `KRONIKA-PROJEKTU.md` §2.14 |

**⚠ FALEŠNÝ POPLACH, KTERÝ ZŮSTÁVÁ ČERVENÝ (H103) — NEOPRAVUJ HO:**
`python _analyza\ov-g-h92-sken.py` končí **`exit 1`** a hlásí
`tools\lint-roadmapa.py:30` jako riziko. **Není to vada**: ten řádek je
**premisa fallbacku** na sourozence repa (o pár řádků níž se použije) a nástroj
**funguje** (`ZMĚŘENO: 22 granulí zkontrolováno`, `exit 0`).

---

## 1. Cíl (jedna věta)

**Přestat měřit měřidla a udělat věcnou práci na projektu — uživatel vybere,
kterou z nabídky v §2 (hra / conductor / orchestra).**

---

## 2. Úkoly

### 2.1 Úkol A — NABÍDKA VĚCNÉ PRÁCE (uživatel vybere; agent ji provede)

**Fronta technického dluhu z ověřovacích session je dočerpaná.** P20 zavřela
poslední tři položky. **Další session proto NEMÁ začínat dalším měřidlem** —
má vzít **jednu** z nabídek níž a **dokončit ji** (včetně ověření a záznamu).

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **H1** | **hra: pozice hráče ve smlouvě `save.gd`** — dnes ji `save()` uloží, ale **spawn ji přepíše** | `HANDOFF.md` **§2.9 B** | Je to **známá vada chování**, ne chybějící funkce: hráč po načtení začíná na spawnu. Malý, uzavřený, ověřitelný kus |
| **H2** | **hra: DAG u `entity.player`** — dovršit granule z roadmapy | `.forge/roadmap.json`, `docs/ARCHITEKTURA.md` | `entity.player` je **`done`**, ale jeho práce v repu je částečná (vzor „`done` je tvrzení, ne důkaz" — `AGENTS.md`) |
| **C1** | **conductor: O3 — opravit vady conductoru a nasadit** | `HANDOFF.md` §2, `PLAN-ROZVOJ-ORCHESTRA.md` | Conductor je **živá služba**; jeho vady se projeví v každém běhu agenta |
| **C2** | **conductor: N0.3 — stav CI cílové hry v `/health`** | `PLAN-ROZVOJ-ORCHESTRA.md` §6 | Bez toho conductor **nevidí**, že cíl má červené CI (naměřeno 1. 10. 2026: 7,5 h bez práce kvůli červenému CI cíle) |
| **O1** | **orchestra: otevřené otázky O5–O8** | `PLAN-ROZVOJ-ORCHESTRA.md` §6 | Jsou to **rozhodnutí**, ne kód — hodí se na session, která nechce sahat do kódu |

**Podmínky pro tuhle část (platí pro všechny nabídky):**

1. **Vybrat JEDNU** a **říct, kterou** (ne „začnu a uvidím").
2. **Než začneš měnit kód, ZMĚŘ současný stav** — ne z dokumentu. U **H1**
   to znamená **spustit hru** (nebo test) a **ukázat**, že se pozice opravdu
   přepíše spawnem.
3. **`done` JE TVRZENÍ, NE DŮKAZ.** Než postavíš na cizí granuli, **najdi její
   soubor v `main` a ZAVOLEJ to, co od ní voláš** (`AGENTS.md`).
4. **Ověř vizuální změnu POHLEDEM** (`read_image` nebo skill `vision`), ne jen
   testy — v projektu se takhle už jednou našel hráč překrytý dlaždicemi.
5. **Zapiš to jako přírůstek** do `HANDOFF.md` (nový oddíl) a `KRONIKA-PROJEKTU.md`
   (řádek session + blok omylů, pokud nějaké byly).

### 2.2 Úkol B — POKUD UŽIVATEL VYBRAL CONDUCTOR: **NEPUSHOVAT BEZ VYŽÁDÁNÍ**

Změna `conductor/**` **spouští `deploy.yml`** — tedy **nasazení živé služby**.
Pravidla platí beze změny:

1. **Před pushí ukázat `git status` a `git diff --stat`** a **vyžádat rozhodnutí**.
2. **Ověřit nasazení TŘEMI kroky** (obecný princip v `DSH_HOME\AGENTS.md`):
   push dorazil (`origin/main..HEAD` = 0) → **build běžel na SPRÁVNÉM commitu**
   (ne „nějaký build") → **server posílá NOVÝ artefakt** (`last-modified`/hash
   je **po** pushi). **HTTP 200 není důkaz.**
3. **Konkrétní příkazy** jsou v `AGENTS.md` → „Jak ověřit nasazení na GitHub
   Pages" a v skillu `orchestra`.

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

**Nedělej z toho program.** Měřidla jsou po P20 v rovnováze; tohle je jen
seznam toho, co **má** být zelené, aby se poznalo, když se to rozbije:

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány (PO SOBĚ, ne současně — oba sahají na _inventar.json):
python _analyza\g3-brany.py            -> 37 bran, 1 nenulovy (zadani kontrola,
                                          DEKLAROVANY), 0 nezacatych, exit 0
node tools\validate-all.mjs            -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py    -> KRONIKA SEDI
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\ov-g-neovereno.py      -> 0 ve stavu NEOVERENO
python _analyza\p20-d-doklady.py       -> 21 dokladu; JEDEN cerveny je H103
                                          (falesny poplach, viz §0)
```

**⚠ `zadání kontrola` má po každém commitu `exit 1` a je to SPRÁVNĚ** (zadání
je záměrně kotvené na commitu měření, nález **NA31**). Je **deklarovaný**
v `OCEKAVANE_NENULOVE`, takže `g3` kvůli němu **nespadne** — ale **vypíše ho**.

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem (brána může mít víc
nenulových stavů; `zadání kontrola` má `0` i `1`).

**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`** —
jinak zůstane mimo dosah a shnije.

### 2.4 Úkol D — ZÁZNAMY A OVĚŘENÍ STAVU (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session.
2. **Zapiš výsledky a omyly do `HANDOFF.md`** (nový oddíl; **jen přidávej**)
   a **přepiš §2.11** (stav otevřených bodů — je to **jediný oddíl, který se
   přepisuje celý**; nic z něj nesmí zmizet bez zapsání do „Co už otevřené NENÍ").
3. **Doplň řádek do `KRONIKA-PROJEKTU.md`** (tabulka sessions + tabulka omylů
   + její `celkem` — **všechny tři**, jinak se součet rozejde).
4. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
5. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all`
   (**NE SOUČASNĚ** — oba sahají na `_inventar.json`).
   **⚠ Inventář přegeneruj jako POSLEDNÍ krok** (jeho otisk počítá **i `.md`**).
6. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Věcná práce je VYBRANÁ a dokončená** | uživatel vybral z §2.1; práce je hotová **a ověřená spuštěním** (u hry **i pohledem na snímek**) |
| 2 | **Nic se nerozbilo** | `g3` → **`exit 0`** (37 bran, 1 **deklarovaný** nenulový); `validate-all` → **`✓ VŠE V POŘÁDKU`** |
| 3 | **Záznamy sedí** | `kronika-kontrola.py` → **`KRONIKA SEDÍ`**; `handoff-kontrola-uplnost.py` → **`83/83`** |
| 4 | **Žádné `NEOVĚŘENO`** | ověřeno **skriptem**, ne dojmem |
| 5 | **Inventář je přegenerovaný jako POSLEDNÍ krok** | `hl-rizika-jazyka.py` → `exit 0` |
| 6 | **Push je ROZHODNUTÍ uživatele** | ne automatika; bez vyžádání se nepushuje |
| 7 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEZAČÍNEJ DALŠÍM MĚŘIDLEM.** Fronta technického dluhu je **dočerpaná**
  a P20 zavřela poslední tři položky. Kdo začne „ještě jednou kontrolou bran",
  **neudělá za session nic, co by projekt posunulo** — a to je přesně to, před
  čím tohle zadání varuje.
- **Nepushovat bez vyžádání** — **P20 pushnutá NENÍ**; další push je **zase
  rozhodnutí**, ne automatika. U **conductoru** to navíc **nasazuje živou službu**.
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická
  čísla se **nechávají citovaná**. **Konkrétně:** řádky **H93/H94** v kronize
  §2.12 zůstávají ve znění P18 a **H99** v §2.13 ve znění P19 (i s tou
  nepřesností o `ast.parse` — oprava je v **§2.14**) — a **§2.10** v `HANDOFF.md`
  zůstává jako záznam k P19, i když dvě jeho položky P20 zavřela (dnešní stav
  je **§2.11**).
- **Nemazat `_analyza/p16*`, `p17*`, `p18*`, `p19*`, `p20*` ani `ov-*`** — jsou
  to **doklady**.
- **Nepřesouvat nic zpátky na `C:`**; `_archiv` a zálohu v
  `C:\Users\Ssevc\Local-Deepseek\_zalohy\` **nemařit** (jsou to cesty zpět).
- **Nespouštět `g3` a `validate-all` SOUČASNĚ** — oba sahají na `_inventar.json`.
- **⚠ Needitovat `.py` přes `Set-Content`** (přidá BOM — omyl **189**); a **nikdy
  nepsat české uvozovky do zdrojáků**. Po každém zápisu `.py` spusť `ast.parse`
  **a zkontroluj první tři bajty**.
- **Nepoužívat `python - <<'PY'`** (heredoc v PowerShellu **neexistuje**) ani
  `python -c` s regexy, zpětnými apostrofy nebo `$()` — **piš skript do souboru**
  (`dsh-prostredi` §3d/§3e/§3f; v P20 to stálo **dvě kola**, omyl **197**).
- **⚠ NEOPRAVOVAT `tools/lint-roadmapa.py:30`** — je to **doložený falešný
  poplach** (H103), ne vada. Nástroj funguje.
- **Nespoléhat na to, „co P20 tvrdí"** — **každé tvrzení přeměř**. **A platí to
  i na tenhle dokument.** P20 přitom **opravila tvrzení P19** (H99: `ast.parse`
  BOM **taky** odmítne) — přesně to má příští session dělat taky.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (6. 10. 2026, 13:2x UTC — PŘED commitem P20)
#   ⚠ hodnoty níž jsou STAV V ČASE MĚŘENÍ; po commitu P20 se HEAD posunul o 1.
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD        -> b781c84  (kotva měření P20)
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main -> b781c84  (P20 NEPUSHNUTÁ)
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0   (PŘED commitem P20)  [po něm: 1]
git -C E:\Workspaces\forge-orchestra status --porcelain (radku)    -> 24  [po commitu: 0]
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD        -> 44dd454
git -C E:\Workspaces\uo-shadows      rev-list --count origin/main..HEAD -> 0   (v sync, strom čistý)

# P20: co se měřilo a jak to vyšlo  (doklady: _analyza/p20-*)
python _analyza\p20-a-kody-bran.py     -> 7 kontrol, 0 chyb   (zadání kontrola umí exit 0 I 1)
python _analyza\p20-a-kontroly.py      -> 18 kontrol, 0 chyb  (g3 soudí červené; oba směry)
python _analyza\p20-b-bom-mereni.py    -> 16 kontrol, 0 chyb  (spustit vs zkompilovat; obě brány shodně)
python _analyza\p20-b2-necitelne.py    -> 12 kontrol, 0 chyb  (H79 tichá díra — měřeno před opravou)
python _analyza\p20-b2-kontroly.py     -> 12 kontrol, 0 chyb  (H79 po opravě; starší doklad P19 pořád sedí)
python _analyza\p20-c-kandidati.py     -> 8 kandidátů: exit, doba, čítač, zápis (NENÍ brána)
python _analyza\p20-d-doklady.py       -> 19 dokladů, 0 chyb   (1 červený je H103 = falešný poplach)
python _analyza\g3-brany.py            -> 37 bran, 1 nenulovy (zadani kontrola — DEKLAROVANY),
                                          0 nezacatych, 0 bez citace mimo deklaraci, exit 0
node   tools\validate-all.mjs          -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py    -> KRONIKA SEDI (205 omylu / 103 nalezu / 33 sessions)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\ov-g-neovereno.py      -> 0 ve stavu NEOVERENO
python _analyza\zadani-kontrola.py     -> exit 1 s 1 varovanim ("pribylo commitu") — OCEKAVANE (NA31)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ IZOLACE (z P18/P19, plati dal): `git worktree` MUSÍ ležet uvnitř `E:\Workspaces`
# a MUSÍ mít junction `uo-shadows` na živou hru; a NESMÍ ležet v měřeném stromě.
# ⚠ A GENEROVANÝ HARNESS si nesmí odvozovat cesty z umístění — do kopie se vkládá
#   ABSOLUTNÍ root (viz `p20-a-kontroly.py` a `p20-oprav-kroniku.py`).
# ⚠ A KOTVA PRO VLOŽENÍ ŘÁDKU se bere Z BLOBU V `HEAD`, ne z načteného (zkráceného)
#   řádku — omyl 206 (`p20-oprav-kroniku.py`).
```

**Uložené doklady (ne rekonstrukce):** `_analyza/p20-a-kody-bran.py`,
`p20-a-kontroly.py`, `p20-b-bom-mereni.py`, `p20-b2-necitelne.py`,
`p20-b2-kontroly.py`, `p20-c-kandidati.py`, `p20-d-doklady.py`,
`p20-zapis-omylu.py`, `p20-oprav-kroniku.py`
(a **`p20-scratch/`** je gitignorovaný: fixtury a harnessy — **není v repu**).
**Jednorázové diagnostiky** z P20 (`p20-sonda-jmena.py`, `p20-sonda-klicu.py`)
jsou **v `_analyza/_archiv/`** — nejsou to opakovatelné brány a v `_analyza/`
by vypadaly jako měřidla, která nikdo nepouští.

**Opravené doklady P18/P19 (a proč):** `ov-e-h79-mez.py` (četl starý formát
souhrnu H79), `p19-d-kontroly.py` (tvrdil staré pravidlo „červenou neposuzuje"),
`p19-c-h94-podpisy.py` (opisovalo jméno brány ručně), `ov-d-klasifikator.py`
(tvrdilo `>= 6` podpisů, P19 jich má 4).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session pro VĚCNOU PRÁCI (ne měřidla). Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (nabídka věcné práce).

Kontext: P20 (HANDOFF.md §38) zavřela POSLEDNÍ tři položky fronty technického
dluhu: g3 teď soudí i červené (OCEKAVANE_NENULOVE, s KÓDEM v deklaraci, protože
zadání kontrola umí exit 0 i 1), BOM v .py je ZAKÁZÁN (pravidlo v AGENTS.md)
a osm ověřovacích skriptů zůstává doklady (dva nemají čítač, pět zapisuje do
stromu). Navíc P20 našla H101: H79 měla TICHOU DÍRU — nečitelný .py tiše
vynechala a tvrdila "0 neplatných sekvencí", kdežto NA32 tentýž soubor vykázal;
opraveno. A H99 P19 bylo v DŮVODU nepřesné: ast.parse() BOM taky odmítne.

Fronta měřidel je DOČERPANÁ. Proto: NEZAČÍNEJ dalším měřidlem. Vyber z §2.1
jednu věcnou práci (hra: pozice hráče ve smlouvě save.gd / DAG u entity.player;
conductor: O3 nebo N0.3; orchestra: O5–O8) a DOKONČI ji — včetně ověření
spuštěním (u hry i pohledem na snímek) a záznamu.

Než začneš: git status --porcelain a git fetch v obou repech. Pozor: P20 NENÍ
pushnutá. A nepoužívej git show <sha>^ (git.cmd žere ^), používej ~1. Needituj
.py přes Set-Content (přidá BOM). A nedělej kotvu z řádku, který se ti načte
zkrácený (omyl 206).

Nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej; dnešní stav je §2.11),
nemaž _analyza/p16*–p20* ani ov-* (jsou to doklady), nepushuj bez vyžádání.
NEOPRAVUJ tools/lint-roadmapa.py:30 — je to doložený falešný poplach (H103).
Po každé změně souboru ve stromě přegeneruj inventář — a naposledy až jako
POSLEDNÍ krok (otisk počítá i .md).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky a omyly do
HANDOFF.md, přepiš §2.11, doplň řádek do KRONIKA-PROJEKTU.md (včetně souhrnu
celkem), rozhodni nálezy ve stavu NEOVĚŘENO (ověř, že žádné nejsou), a do chatu
vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.
```

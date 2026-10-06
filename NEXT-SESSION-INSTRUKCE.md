# ZADÁNÍ PRO DALŠÍ SESSION — VĚCNÁ PRÁCE NA CONDUCTORU (hra je POZASTAVENÁ)

**Co tenhle dokument JE:** **zadání pro session P22**. Nahrazuje zadání z P20
(to je **záznam**, ne stav — `git log -1 NEXT-SESSION-INSTRUKCE.md`).

**Stav obou repů při psaní:** `forge-orchestra` = `b2fd758`, `origin/main` = **`b2fd758`** (P20 **pushnutá**) · `uo-shadows` = `44dd454`, `origin/main` **shodná**, strom **čistý**
**Zkontrolováno při:** **6. 10. 2026, 12:1x–12:4x UTC = 14:1x–14:4x +02:00**; k tomu v orchestra ještě **necommitnuté záznamy P21** (řádek session v kronice, nálezy **H104–H107**, oddíly **§39** a **§2.12** v `HANDOFF.md`, tento dokument) — **živý `HEAD` si ověř sám**

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech — a **ověř `origin/main..HEAD` ŽIVĚ** (`git ls-remote`), ne
> podle tohohle textu. Tenhle dokument je **stav v čase psaní**.
>
> **⚠ A DRUHÁ:** **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO**
> commitu. Používej **`~1`**, nebo **`git.exe`**. Detail: skill `dsh-prostredi` **§5c**.
>
> **⚠ A TŘETÍ:** **`Set-Content -Encoding utf8` v PowerShellu přidá do `.py` BOM**
> → soubor přestane být zkompilovatelný a **NA32 ho právem vykáže** (omyl **189**).
> Kód edituj **`edit`/`write` toolem**; po zápisu zkontroluj **první tři bajty**
> (`.py` **NESMÍ** mít BOM, `.ps1` **MUSÍ**).
>
> **⚠ A ČTVRTÁ (omyl 206):** **NEDĚLEJ KOTVU Z ŘÁDKU, KTERÝ SE TI NAČTE ZKRÁCENÝ.**
> Řádky v `KRONIKA-PROJEKTU.md` mají **přes 2000 znaků**, takže „vložení" kotvou
> z načteného řádku **nahradí celý řádek** zkráceným textem. Zápis do kroniky veď
> **programově** (vzor: `_analyza/p21-zapis-kroniky.py` — bere řádek z disku
> a je **idempotentní**).
>
> **⚠ A PÁTÁ (H106):** **čas vždy s pásmem.** Hlavička minulého zadání psala
> „13:2x UTC", ale byl to čas **lokální** (+02:00) — kdo porovná `mtime` souboru
> s hlavičkou, dostane dvouhodinový rozpor.

---

## 0. Co je HOTOVÉ (neopakuj to znovu)

| # | Co se udělalo | Doklad |
|---|---|---|
| **P20** | `g3` **soudí červené** (`OCEKAVANE_NENULOVE = {"zadání kontrola": 1}`), **BOM v `.py` zakázán** (pravidlo v `AGENTS.md`), **H101** (tichá díra v H79) opraveno, **H102/H103** dořešeny | `HANDOFF.md` **§38** |
| **P21** | **P20 byla NEBYLA commitnutá** (H104) → ověřeny **všechny brány**, P20 **commitnuta** (`b2fd758`, 23 souborů) a **pushnuta**; nálezy **H104–H106** | `HANDOFF.md` **§39** |
| **Brány** | `g3` → **37 bran, 0 nezačatých**, `validate-all` → **`✓ VŠE V POŘÁDKU`**, `kronika` → **SEDÍ (205/106/34)**, `handoff` → **83/83**, `NEOVĚŘENO` → **0** | `HANDOFF.md` §39.2 |

**⚠ `zadání kontrola` je od commitu P21 zase ČERVENÁ — a je to SPRÁVNĚ.** Je
záměrně kotvená na commitu, na kterém se měřilo (nález **NA31**), takže po každém
dalším commitu hlásí „přibylo commitů". Je **deklarovaná** v `OCEKAVANE_NENULOVE`,
takže `g3` kvůli ní **nespadne** — jen ji vypíše.

---

## 1. Cíl (jedna věta)

**Udělat jednu věcnou věc na conductoru nebo orchestře — a dokončit ji
(včetně ověření a záznamu). Nezačínat dalším měřidlem.**

---

## 2. Úkoly

### 2.1 Úkol A — NABÍDKA VĚCNÉ PRÁCE (vyber JEDNU a řekni kterou)

| # | Nabídka | Kde je zapsaná | Proč je na řadě |
|---|---|---|---|
| **C1** | **conductor: O3 — opravit vady conductoru a nasadit** | `HANDOFF.md` **§2.2**, `PLAN-ROZVOJ-ORCHESTRA.md` **§3.5 (fáze B)** | Conductor je **živá služba** a jeho vady se projeví v **každém běhu agenta**. Fáze B = **B1** `naposledy_selhalo` místo `updated_at`, **B2** `/report` zapíše roadmapu, **B3** strop a watchdog na `i_id`, **B4** `listGames` fallback, **B5** komentáře `:31` a `:233` (tvrdí, že `MAX_ATTEMPTS` je mrtvý kód — **není**) |
| **C2** | **conductor: N0.3 — stav CI cílové hry v `/health`** | `HANDOFF.md` **§2.5** | Bez toho conductor **nevidí**, že cíl má červené CI. Naměřeno **1. 10. 2026: 7,5 h bez práce** kvůli červenému CI cíle — conductor přitom hlásil `ok: true` |
| **O1** | **orchestra: rozhodnout O10 a O5–O8** | `PLAN-ROZVOJ-ORCHESTRA.md` **§6** | Jsou to **rozhodnutí**, ne kód — hodí se, když nechceš sahat do živé služby |

**Podmínky (platí pro všechny):**

1. **Vybrat JEDNU** a **říct, kterou** (ne „začnu a uvidím").
2. **Než začneš měnit kód, ZMĚŘ současný stav** — **ne z dokumentu**. U C1 to
   znamená **zavolat živý conductor** a ukázat vadu **na jeho odpovědi**.
3. **`done` JE TVRZENÍ, NE DŮKAZ.** Než postavíš na cizí granuli nebo na tvrzení
   z `HANDOFF`, **najdi její soubor v `main` a ZAVOLEJ to, co od ní voláš**.
4. **Ověř nasazení TŘEMI kroky** (viz §2.2) — **HTTP 200 není důkaz**.
5. **Zapiš to jako přírůstek** do `HANDOFF.md` (nový oddíl) a `KRONIKA-PROJEKTU.md`
   (řádek session; nález → §2; omyl → §3 + `HANDOFF.md` §8).

### 2.2 Úkol B — CONDUCTOR JE ŽIVÁ SLUŽBA: **NEPUSHOVAT BEZ VYŽÁDÁNÍ**

Změna `conductor/**` **spouští `deploy.yml`** — tedy **nasazení živé služby**:

1. **Před pushem ukázat `git status` a `git diff --stat`** a **vyžádat rozhodnutí**.
2. **Ověřit nasazení TŘEMI kroky:** push dorazil (`origin/main..HEAD` = **0**) →
   **build běžel na SPRÁVNÉM commitu** (ne „nějaký build") → **server posílá NOVÝ
   artefakt**. **⚠ `deploy.yml` má filtr `paths: conductor/**`** — commit, který
   conductor nemění, deploy **správně nemá** (to už jednou vyrobilo falešný poplach,
   omyl **70**).
3. **Konkrétní příkazy a past** jsou v `AGENTS.md` a ve skillu **`orchestra`**.

### 2.3 Úkol C — ÚDRŽBA MĚŘIDEL (jen to, co se samo ozve)

**Nedělej z toho program.** Měřidla jsou po P21 v rovnováze; tohle je jen seznam
toho, co **má** být zelené, aby se poznalo, když se to rozbije:

```
# po KAŽDÉ změně souboru ve stromě (NA1/H60) — a naposledy jako POSLEDNÍ krok:
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# brány (PO SOBĚ, ne současně — oba sahají na _inventar.json):
python _analyza\g3-brany.py            -> 37 bran, 1 nenulovy (zadani kontrola,
                                          DEKLAROVANY), 0 nezacatych, exit 0
node tools\validate-all.mjs            -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py    -> KRONIKA SEDI (205/106/34)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\ov-g-neovereno.py      -> 0 ve stavu NEOVERENO
python _analyza\p20-d-doklady.py       -> 22 dokladu; JEDEN cerveny je H103
                                          (falesny poplach — NEOPRAVOVAT)
```

**⚠ KDO PŘIDÁ BRÁNU S LEGITIMNĚ NENULOVÝM EXITEM, PŘIDÁ JI I DO
`OCEKAVANE_NENULOVE` — A S KÓDEM**, ne jen se jménem.

**⚠ KDO PŘIDÁ DOKLAD DO `_analyza/`, PŘIDÁ HO I DO `p20-d-doklady.py`** —
jinak zůstane mimo dosah a shnije.

### 2.4 Úkol D — ZÁZNAMY A OVĚŘENÍ STAVU (povinné na konci)

1. **Přepiš `NEXT-SESSION-INSTRUKCE.md`** pro další session.
2. **Zapiš výsledky a omyly do `HANDOFF.md`** (nový oddíl; **jen přidávej**)
   a **přidej nový stavový oddíl `§2.13`** (dnešní stav je **§2.12**; starší
   stavové oddíly se **nechávají** jako záznam).
3. **Doplň řádek do `KRONIKA-PROJEKTU.md`** (tabulka sessions + nálezy do §2
   + omylů do §3 + **souhrn `celkem`** — **všechny tři**, jinak se součet rozejde).
4. **Ověř, že nezůstalo `NEOVĚŘENO`** — vlastním skriptem, ne grepem.
5. **Přegeneruj inventář** a spusť `g3` **a pak** `validate-all`
   (**NE SOUČASNĚ**). **⚠ Inventář přegeneruj jako POSLEDNÍ krok** (jeho otisk
   počítá **i `.md`**).
6. **Do chatu vlož prompt pro uživatele i se STAVOVÝM ŘÁDKEM.**

---

## 3. „Hotovo znamená" pro tuhle session

| # | Podmínka | Jak se to pozná |
|---|---|---|
| 1 | **Věcná práce je VYBRANÁ a dokončená** | vybráno z §2.1; práce hotová **a ověřená spuštěním** (u conductoru **proti živé službě**) |
| 2 | **Nic se nerozbilo** | `g3` → **`exit 0`** (37 bran, 1 **deklarovaný** nenulový); `validate-all` → **`✓ VŠE V POŘÁDKU`** |
| 3 | **Záznamy sedí** | `kronika-kontrola.py` → **`KRONIKA SEDÍ`**; `handoff-kontrola-uplnost.py` → **83/83** |
| 4 | **Žádné `NEOVĚŘENO`** | ověřeno **skriptem**, ne dojmem |
| 5 | **Inventář je přegenerovaný jako POSLEDNÍ krok** | `hl-rizika-jazyka.py` → `exit 0` |
| 6 | **Push je ROZHODNUTÍ uživatele** | u conductoru navíc **nasadí živou službu** |
| 7 | V chatu je **prompt pro uživatele** i **stavový řádek** | ke zkopírování |

---

## 4. Co NEDĚLAT

- **⚠ NEZAČÍNEJ DALŠÍM MĚŘIDLEM.** Fronta technického dluhu je **dočerpaná**
  (P20 zavřela poslední tři položky) a P21 k tomu přidala jen **dokončení commitu
  a push**. Kdo začne „ještě jednou kontrolou bran", **neposune projekt**.
- **Nepushovat bez vyžádání** — u **conductoru** to navíc **nasazuje živou službu**.
- **Nesahej na hru.** Uživatel ji **záměrně pozastavil** (chystá přepis
  architektury zadání hry) — nabídky **H1/H2 nejsou na řadě**.
- **⚠ NEOPRAVUJ `tools/lint-roadmapa.py:30`** — je to **doložený falešný poplach**
  (H103). Nástroj funguje.
- **Nepřepisovat `HANDOFF.md` ani `KRONIKU`** — jen **přidávat**; historická
  čísla se **nechávají citovaná** (§2.10 = záznam k P19, §2.11 = k P20,
  §2.12 = k P21).
- **Nemazat `_analyza/p16*`–`p21*` ani `ov-*`** — jsou to **doklady**.
- **Nepřesouvat nic zpátky na `C:`**; `_archiv` a zálohu v
  `C:\Users\Ssevc\Local-Deepseek\_zalohy\` **nemařit** (jsou to cesty zpět).
- **Nespouštět `g3` a `validate-all` SOUČASNĚ** — oba sahají na `_inventar.json`.
- **⚠ Needitovat `.py` přes `Set-Content`** (přidá BOM — omyl **189**); a **nikdy
  nepsat české uvozovky do zdrojáků**. Po každém zápisu `.py` spusť `ast.parse`
  **a zkontroluj první tři bajty**.
- **Nepoužívat `python - <<'PY'`** (heredoc v PowerShellu **neexistuje**) ani
  `python -c` s regexy nebo `$()` — **piš skript do souboru**.
- **Nespoléhat na to, „co P21 tvrdí"** — **každé tvrzení přeměř**. P21 přitom
  **vyvrátila tvrzení P20** (H104: „P20 je commitnutá") — přesně to má příští
  session dělat taky.

---

## 5. Naměřená východiska (aby se nemusela měřit znovu)

```
# hlavička a stav (6. 10. 2026, 12:1x UTC = 14:1x +02:00)
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD        -> b2fd758  (P20, PUSHNUTÁ)
git -C E:\Workspaces\forge-orchestra rev-parse --short origin/main -> b2fd758
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD -> 0  [po commitu P21: 1]
git -C E:\Workspaces\uo-shadows      rev-parse --short HEAD        -> 44dd454  (= origin/main, clean)

# P21: co se měřilo a jak to vyšlo
python _analyza\g3-brany.py            -> 37 bran, 0 nenulovych (PRED commitem P21), exit 0
                                          [PO commitu: 1 nenulovy = zadani kontrola, DEKLAROVANY]
node tools\validate-all.mjs            -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py    -> KRONIKA SEDI (205 omylu / 106 nalezu / 34 sessions)
python _analyza\handoff-kontrola-uplnost.py -> 83/83
python _analyza\ov-g-neovereno.py      -> 0 ve stavu NEOVERENO
python _analyza\p20-d-doklady.py       -> 22 dokladu (pridano p21-zapis-kroniky.py);
                                          1 cerveny = H103 (falesny poplach)
python _analyza\p21-zapis-kroniky.py   -> 18/0 (idempotentni zapis do kroniky)

# inventar se MUSI pregenerovat po kazde zmene souboru ve stromu (H60/NA1)
#   a jako POSLEDNI krok (otisk pocita i .md):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json

# ⚠ IZOLACE (plati dal): `git worktree` MUSI lezet uvnitr `E:\Workspaces`
#   a MUSI mit junction `uo-shadows` na zivou hru; a NESMI lezet v merenem stromi.
# ⚠ A KOTVA PRO VLOZENI RADKU se bere Z DISKU (ne z nacteneho zkraceneho radku).
# ⚠ BRANY POTREBUJI PRAVO ZAPISU MIMO WORKSPACE (stavi si pracovni kopie
#   v `_analyza\a-ukol-scratch\`) — v omezenem sandboxu spadnou na PermissionError.
```

**Uložené doklady P21:** `_analyza/p21-zapis-kroniky.py` (idempotentní zápis
řádku session, nálezů H104–H106 a souhrnu do kroniky; **18/0**).

---

## 6. Prompt pro uživatele (zkopíruj do nového chatu)

```text
Jsi session pro VĚCNOU PRÁCI NA CONDUCTORU (ne měřidla). Repa jsou na E:
  orchestra = E:\Workspaces\forge-orchestra
  hra       = E:\Workspaces\uo-shadows   (POZASTAVENÁ — nesahej na ni)

Zadání pro tebe je v E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md
— přečti ho CELÝ, hlavně §2.1 (nabídka věcné práce).

Kontext: P20 (HANDOFF.md §38) zavedla, že g3 soudí i červené (OCEKAVANE_NENULOVE
s KÓDEM), zakázala BOM v .py a opravila tichou díru v H79. P21 (§39) pak zjistila,
že P20 NEBYLA commitnutá (H104) — ověřila všechny brány, P20 commitnula (b2fd758)
a pushnula. Navíc našla H105: nabídka "save.gd" stojí na neplatném předpokladu
(save.gd se ve hře nikdy nevolá) a H106 (čas bez pásma v hlavičce zadání).

Fronta měřidel je DOČERPANÁ. Proto: NEZAČÍNEJ dalším měřidlem. Vyber z §2.1 jednu
věcnou práci (conductor: O3 vady a nasazení / N0.3 stav CI v /health; orchestra:
rozhodnutí O10 a O5-O8) a DOKONČI ji — včetně ověření proti ŽIVÉ službě a záznamu.

Než začneš: git status --porcelain a git fetch v obou repech (git.cmd kvůli TLS).
Pozor: conductor/** spouští deploy.yml — nepushuj bez vyžádání. A nepoužívej
git show <sha>^ (git.cmd žere ^), používej ~1. Needituj .py přes Set-Content
(přidá BOM). A nedělej kotvu z řádku, který se ti načte zkrácený (omyl 206).

Nepřepisuj HANDOFF.md ani KRONIKU (jen přidávej; dnešní stav je §2.12),
nemaž _analyza/p16*-p21* ani ov-* (jsou to doklady).
NEOPRAVUJ tools/lint-roadmapa.py:30 — je to doložený falešný poplach (H103).
Po každé změně souboru ve stromě přegeneruj inventář — a naposledy až jako
POSLEDNÍ krok (otisk počítá i .md).

Na konci povinně: přepiš NEXT-SESSION-INSTRUKCE.md, zapiš výsledky a omyly do
HANDOFF.md (nový oddíl + stavový §2.13), doplň řádek do KRONIKA-PROJEKTU.md
(včetně souhrnu celkem), ověř, že nezůstalo NEOVĚŘENO, a do chatu vlož prompt
pro uživatele i se STAVOVÝM ŘÁDKEM.
```

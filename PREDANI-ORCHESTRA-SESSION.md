# PŘEDÁNÍ — ORCHESTRA (workspace `E:\Workspaces\forge-orchestra`)

**Co tenhle dokument JE:** **předání kontextu** pro session, která si tenhle
workspace převezme a půjde dělat **na orchestra dál sama**. Není to stav
projektu (stav je v `HANDOFF.md`) ani zadání (to je
`NEXT-SESSION-INSTRUKCE.md`). Je to **jediné, co přežije přechod session**:
kde jsme, co je hotové, čím to ověřit a co je další krok.

**Napsáno:** 6. 10. 2026, 23:0x +02:00 = 21:0x UTC · **session:** P23k (stanice)
**Kotva (živý stav při psaní):** `forge-orchestra` = **`c87db93`**, `origin/main`
= **`c87db93`**, `origin/main..HEAD` = **0**, strom **čistý** ·
`uo-shadows` = **`44dd454`**, `origin/main` shodná, **0** commitů k pushi

> **⚠ Tohle předání je jedno ze DVOU a jsou pro různé workpaces.**
> Druhé je **`C:\Users\Ssevc\Local-Deepseek\PREDANI-GENERALIZACE-NASTROJU.md`**
> — pro session, která dělá **generalizaci a optimalizaci nástrojů a pouček**
> (to je o stanici, ne o orchestře). Kdo si plete obě, začne v orchestře
> přesouvat skilly.
>
> **A druhá věc, která se plete:** `E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md`
> je **jiné zadání** (nezávisle přeměřit doplněné záznamy, A1–A7). Tohle
> předání ho **neruší** — je to další vstup vedle něj.

> **⚠ PRVNÍ VĚC, KTEROU UDĚLEJ:** `git status --porcelain` a **`git fetch`**
> v obou repech a ověř `origin/main..HEAD` **živě** (`git ls-remote`) — tenhle
> text je **stav v čase psaní**.

---

## Kde to začalo (a co si tenhle workspace nese)

Orchestra je **cloudový projekt, který vyvíjí hry pomocí bezplatných LLM**
(conductor na Cloudflare + agenti v GitHub Actions). Je to **živá služba**:
`push` do `conductor/**` spouští `deploy.yml`, tedy **nasazení**.

**Uživatel 6. 10. 2026 řekl:** *„Conductor — to záleží na okolnostech. Nyní jsme
v DEV prostředí, protože orchestra není dokončená a běží testovací projekt."*
→ To je **odpověď na O1/O3** z `PLAN-ROZVOJ-ORCHESTRA.md` §6: **na conductora
se sáhnout smí** (jsme v DEV, cíl je testovací projekt). **Push do
`conductor/**` ale zůstává rozhodnutím uživatele** — nasazuje živou službu.

---

## Co je hotové (a čím to je doložené)

| Co | Stav | Doklad |
|---|---|---|
| **Fáze F0 + A** | hotové a ověřené | `a1-a2-over.py` (23 kontrol), `a3-over.py` |
| **`g3` soudí i červené** | hotové (P20) | `OCEKAVANE_NENULOVE` s **kódem**; `p20-a-kontroly.py` 18/0 |
| **BOM v `.py` zakázán** | pravidlo v `AGENTS.md` | `p20-b-bom-mereni.py` 16/0 |
| **Záznamy P22 dopsány** | hotové (dnes) | `HANDOFF.md` **§40**, kronika **řádek 36** + **2.16** + blok **`8za`** |
| **Schválené práce (rituál, drobnosti, §6.14)** | hotové (dnes) | `HANDOFF.md` **§41**; `PREDAVANI-SESSION.md` §2.4–§2.7 |
| **Registr bran = jedna autorita** | hotové (dnes) | `_analyza/_registr-bran.json` **generuje `g3`** (37 bran); `AGENTS.md` to uvádí |
| **Brány** | zelené | `g3` **37 bran / 1 deklarovaný / `exit 0`** · `validate-all` **`✓ VŠE V POŘÁDKU`** · `kronika SEDÍ` (208/27/36) · `handoff` **83/83** |

---

## Prostředí (pasti, které tě budou mást)

- **`git.cmd` ŽERE `^`** — `git show <sha>^` tiše vrátí stav **PO** commitu.
  Používej **`~1`**, nebo `git.exe` přímo. (skill `dsh-prostredi` §5c)
- **`.py` NESMÍ mít BOM** (omyl **189**): `Set-Content -Encoding utf8` ho přidá
  a soubor **přestane být zkompilovatelný**. Piš `edit`/`write` toolem a po
  zápisu zkontroluj **první tři bajty**.
- **Na GitHub jen přes PAT ze souboru** (`.secrets/github_pat.txt`), přes
  `GIT_CONFIG_VALUE_0` (env), nikdy do argumentů ani do výstupu.
- **Cesty se ODVOZUJÍ**, neopisují: `g3` bere `FORGE_STANICE`/`FORGE_HRA`
  z prostředí (defaulty sedí).
- **`_analyza/_inventar.json` je gitignorovaný a generovaný** — jeho otisk se
  mění s **každou editací kódu** (i s každým `g3` během). Proto:
  **inventář přegeneruj jako POSLEDNÍ krok** a teprve pak `g3` a `validate-all`
  (**ne současně** — oba na inventář sahají).
- **Kdo si staví harness z `g3`** (fixtury, mutační testy), musí dát
  **`FORGE_REGISTR=<scratch cesta>`** nebo **`FORGE_BEZ_REGISTRU=1`** — jinak
  přepíše **živý** registr svým seznamem. Naměřeno dnes: skončila v něm
  **jedna fixtura** (`A1: zdravá`, `bran_celkem: 1`) a běh byl přitom „zelený";
  pozná se to **jen měřením obsahu souboru** (`p20-d-doklady.py` ho proto hlídá).
- **Kotva zadání se píše ve tvaru `<repo> = <sha>`** — `_analyza/zadani-kontrola.py`
  jiný tvar nevidí (a hlásí „zadání netvrdí žádný commit").

---

## Objective k re-arm (žádný `goal` tu neběží)

Pro tuhle práci **není potřeba `goal`** — je to jeden krok řetězu, ne
vícekrokový cíl. Kdybys ale dělal **fázi B celou** (B1–B5), je to práce na víc
session → pak `create_goal` s textem:

> „Opravit vady conductora (B1–B5) po částech, každou ověřit proti ŽIVÉ službě
> a nasadit; nic nepushovat do `conductor/**` bez vyžádání uživatele."

---

## Background procesy a subagenti

**Žádné.** V této session neběžel žádný background job ani subagent.
(Předchozí session P22 použila 4 subagenty na audit KB — jejich **výstupy jsou
v dokumentech**, ale jejich handle jsou mrtvé.)

---

## Running state

- **Dev servery / porty:** žádné (conductor běží na Cloudflare, ne lokálně).
- **Worktrees / větve:** žádné otevřené. `_analyza/*-scratch/` jsou pracovní
  kopie bran (gitignorované) — **nejsou to doklady**.
- **Repa:** `E:\Workspaces\forge-orchestra` (orchestra) a
  `E:\Workspaces\uo-shadows` (**hra, záměrně pozastavená** — uživatel chystá
  přepis architektury zadání hry; **nesahej na ni**).

---

## Jak ověřit, že to ještě platí

```powershell
# stav (živě, ne z dokumentu)
git -C E:\Workspaces\forge-orchestra fetch origin
git -C E:\Workspaces\forge-orchestra rev-list --count origin/main..HEAD   # -> 0
git -C E:\Workspaces\forge-orchestra rev-parse --short HEAD               # -> c87db93 (nebo novější)

# brány (po sobě!)
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json    # inventář PRVNÍ
python _analyza\g3-brany.py           # -> 37 bran, 1 deklarovaný (zadání kontrola), exit 0; zapíše registr
node tools\validate-all.mjs           # -> VSE V PORADKU, exit 0
python _analyza\kronika-kontrola.py   # -> KRONIKA SEDI (208 omylu / 27 bloku / 36 sessions)
python _analyza\handoff-kontrola-uplnost.py   # -> 83/83, CHYBI 0
python _analyza\p20-d-doklady.py      # -> 23 dokladu, 1 cerveny = H103 (dolozeny falesny poplach)
python _analyza\zadani-kontrola.py    # -> po kazdem commitu exit 1 (kotva vs. novy HEAD) = SPRAVNE
```

**Když `validate-all` hlásí `INVENTÁŘ JE ZASTARALÝ`:** nejsi v chybě — sáhl jsi
na kód po regeneraci. Pustit skener, ne „opravovat" bránu.

---

## Doklady, které k tomu patří (a kde jsou)

- `E:\Workspaces\forge-orchestra\HANDOFF.md` — **stav** (dnešní je **§2.12**);
  **§40** a **§41** jsou **záznamy** o tom, co se dnes udělalo.
- `E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md` — **paměť projektu**
  (append-only; řádky 36 a 37 jsou dnes).
- `E:\Workspaces\forge-orchestra\NEXT-SESSION-INSTRUKCE.md` — **zadání pro
  session P23** (nezávisle přeměřit doplněné záznamy, A1–A7). **Cíl je
  ověřovací, ne vývojový** — a je pořád platné.
- `E:\Workspaces\forge-orchestra\ZADANI-OPTIMALIZACE-KB.md` — zadání pro
  **jinou** session (KB), **tenhle workspace si ho nebere**.
- `_analyza/p22-zapis-zaznamu.py` (34/0), `_analyza/p23-zapis-schvalene.py` (8/0),
  `_analyza/_archiv/_jednorazove-P16-P17/p23k-radek-kroniky.py` (9/0),
  `_analyza/p22c-bunka-kroniky.py` (11/0)
  — idempotentní zápisy, které se dají pustit znovu.
  ⚠ `p23k-radek-kroniky.py` byl **7. 10. 2026 archivován** (DOPLNĚNÍ 14
  v `PREDANI-GENERALIZACE-NASTROJU.md`), proto vede cesta do `_archiv\`.

---

## Odložené a otevřené otázky

**Odložené (vědomě):**
- **Hra (`uo-shadows`)** — uživatel ji pozastavil (chystá přepis architektury
  zadání hry). Nabídky H1/H2 **nejsou na řadě**; `save.gd` se ve hře **nikdy
  nevolá** (H105), takže „opravit spawn" by opravovalo kód, který se nespouští.
- **H103** — `ov-g-h92-sken.py` zůstává **červený jako doložený falešný
  poplach**; **neopravovat** `tools/lint-roadmapa.py:30`.
- **KB body §6.4/6.5/6.6/6.8/6.9/6.11** — **schválené uživatelem**, ale patří
  session s **nezávislým ověřením** (mění trvalá pravidla / přesouvají
  historii). Zadání: `ZADANI-OPTIMALIZACE-KB.md`.

**Otevřené (potřebuje uživatele):**
- **Co dělat na conductoru první** — nabídka **C1** (B1–B5: vady a nasazení),
  nebo **C2** (stav CI cílové hry v `/health`, nález N0.3: conductor **nevidí**,
  že cíl má červené CI — naměřeno 1. 10. 2026 **7,5 h bez práce**) — nebo **O1**
  (rozhodnout O10 a O5–O8, což je jen rozhodnutí, žádný kód).
- **Push do `conductor/**`** = nasazení živé služby → **vyžádat rozhodnutí**
  (i v DEV).

---

## Pick up here

**Vyber JEDNU věcnou práci na conductoru** (C1, C2, nebo O1 — viz „Otevřené"
výš), **změř její vadu na ŽIVÉ službě** (ne z dokumentu) a proveď ji **po
částech**: `HANDOFF.md` **§2.2** a `PLAN-ROZVOJ-ORCHESTRA.md` **§3.5 (fáze B)**
jsou podklad. Před commitem záznamů přegeneruj inventář jako poslední krok
a **push nech na uživateli** (u `conductor/**` nasazuje).

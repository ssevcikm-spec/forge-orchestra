
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 19.1 Push obou repů — PROVEDENO 2. 10. 2026 (13:16 UTC)

**Zadání:** uživatel. **Doslova:** *„Pushni to a zapiš do instrukcí, že akční
sezení může provést commit i push, ale až po tom, co ověří správnost."*

**Co to změnilo proti `AGENTS.md`:** obecné pravidlo *„Nepushovat bez vyžádání"*
bylo **vyžádáním naplněno** — a uživatel k němu přidal **podmínku pořadí**:
**nejdřív ověřit, pak commitnout, pak pushnout.** To je zapsané v
`NEXT-SESSION-INSTRUKCE.md` §4 i §3 Úkol 2.

**Provedeno v tom pořadí:**

| Krok | Co se udělalo | Výstup |
|---|---|---|
| **1. OVĚŘIT** | brány + testy hry + drift | `handoff-uplnost` **0** · `kronika` **0** · `hl-rizika` **0** · `diakritika` **0** · `g1` **0** · `ag-over-cisla` **0** · **testy hry `64 kontrol, 0 selhání`** · drift **1 rozdíl — ZNÁMÝ** (šablona má 21 kroků, hra 20: `Kontrola class_name` je ve hře uvnitř kroku parsování) |
| **2. COMMITNOUT** | dva commity, zvlášť za každý rep | `orchestra` **`593e25c`** (1 soubor, +125) · `uo-shadows` **`c40bdd5`** (4 soubory, +377 −41) |
| **3. PUSHNOUT** | `git -C <repo> -c http.extraHeader=… push origin HEAD:main`, PAT ze souboru | `7c11b2d..593e25c` a `194735d..c40bdd5` — **oba `exit 0`** |

**Tři kroky důkazu nasazení (povinné podle `AGENTS.md`):**

| # | Krok | Naměřeno |
|---|---|---|
| **1** | push dorazil | `rev-list --count origin/main..HEAD` = **0** v **obou** repech |
| **2** | workflow na **tom** commitu | `uo-shadows` (`c40bdd556b67f9ac95a82b6c1c8798f926f431fd`): **`release.yml` #69 `completed/success`** a **`CI` #102 `completed/success`**, oba `head:c40bdd556` · `orchestra`: **deploy #32 na `7c11b2d` — a to je SPRÁVNĚ** (viz níž) |
| **3** | server posílá **nový** build | `index.png`, `index.html`, `index.wasm`, `index.pck` → **`last-modified Fri, 02 Oct 2026 13:18:06 GMT`**; push byl **13:16:50 UTC** → **build je 76 s po pushi a je novější než ten z 09:30:47** |

> **⚠ Past, na kterou jsem při tom sám naletěl (omyl 69, §8g):** filtr
> `?head_sha=c40bdd5` vrátil **`total_count: 0`** — a **26 minut** jsem čekal na
> běh, který už dávno skončil. **GitHub v `head_sha` krátký sha NEODFILTRUJE**
> (nevrátí chybu, vrátí **prázdno**). Se **plným** sha to vrátí **2 běhy**
> (`#102`, `#69`, oba `success`). **Prázdný výsledek filtru vypadá jako
> „ještě nezačalo"** — a je to při tom **naměřená nula s jiným důvodem**.

> **⚠ `orchestra` NEMÁ nový deploy — a není to chyba.** `deploy.yml` má filtr
> `paths: conductor/**` a commit `593e25c` mění **jen `tools/kontrola-diakritiky.py`**.
> Nasadit tedy **není co** — a nástroj `f3-over-deploy.mjs` to hlásí přesně:
> `CHYBA deploy běžel na tomto commitu — na 593e25c85 žádný deploy — push
> nezměnil conductor/**?` **To je správné chování brány**, ne nález: ptá se na
> konkrétní commit a řekne, že na něm deploy neběžel. **Kód conductora z `main`
> zůstává nasazený** (`#32` na `7c11b2d`, což je poslední změna `conductor/**`).

**Co se tím uzavřelo:**

- ~~**H9** — „necommitnuto vs. nepushnuto"~~ → **vyřešeno**: práce Úkolů A i B
  je **v `main` a pushnutá** (`c40bdd5`), ne jen v pracovním stromě.
- ~~**H7/H11** — `docs/ARCHITEKTURA.md` §2.1 není v repu~~ → **vyřešeno**:
  je v `main` (commit `c40bdd5`), takže `roadmap.json:3`, který se na ten
  dokument odvolává, **už odkazuje na něco, co v repu je**.
- ~~**„čtyři necommitnuté soubory čekají na schválení"**~~ → **nečekají**;
  byly commitnuty a pushnuty.

**Vlastní omyl, který při tom vznikl (a je zapsaný v §8g jako č. 69):**
`orchestra` a `uo-shadows` mají **různé filtry cest** v deploy workflow.
Kdo se ptá „nasadilo se to?" **jedním** nástrojem na **oba** repy, dostane
u jednoho `CHYBA` — a **vypadá to jako selhaný deploy**, přitom je to
**správně neprovedený deploy** (push se kódu conductora netýkal).

**A druhý omyl téhož kroku:** filtr běhů `?head_sha=<krátký sha>` vrátil
`total_count: 0` a já **26 minut** čekal na běh, který **už skončil**.
**GitHub krátký sha v tom filtru neodfiltruje — vrátí prázdno bez chyby.**
Je to **tatáž past**, před kterou `overovani` varuje: **prázdný výsledek
filtru vypadá jako „ještě nic"**, ale je to **naměřená nula s jiným důvodem**.
**Pravidlo: na `head_sha` posílej PLNÝ 40znakový sha.**

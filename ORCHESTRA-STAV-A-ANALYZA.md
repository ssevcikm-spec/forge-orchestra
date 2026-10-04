# Orchestra — stav doporučení a analýza pro přepracování

> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 1. 10. 2026 (večer) · **Autor:** session, která dnes ověřovala `HANDOFF.md`
a dělala F0-verifikaci · **Vztah k ostatním dokumentům:** tohle **není** náhrada
`ANALYZA-ARCHITEKTURY-ORCHESTRA.md` ani `PLAN-ROZVOJ-ORCHESTRA.md` — je to
**stavová vrstva nad nimi**. Co je hotové, co ne, a kde se jejich pořadí rozchází
s měřením.

> **Proč tenhle dokument vznikl.** Analýza architektury je z **1. 10. 2026
> dopoledne** a popisuje stav **před F0** (`ANALYZA-ARCHITEKTURY-ORCHESTRA.md`
> §8 to přiznává). Její doporučení (L1–L17, ST1–ST10) se tím pádem čtou jako
> „co udělat", ale **není u nich vidět, co z toho už hotové je** — a dvě hotová
> jsou. Bez téhle vrstvy se plánuje znovu to, co je udělané, a přehlédne se to,
> co je nejdůležitější.

**Jak to bylo měřeno:** `node _analyza\stav-doporuceni.mjs` (bez sítě, čte
soubory a `git`). Každý řádek tabulky níž má u sebe, čím byl ověřen. Kde jsem
měřil jen staticky, je to řečeno.

---

## 1. Co je hotové a co ne (měřeno 1. 10. 2026 večer)

| # | Doporučení (analýza §5) | Stav | Naměřeno |
|---|---|---|---|
| **L1** | `validate-all.mjs`: nastavit `process.exitCode` + pouštět **správnou** kopii brány | ❌ **CHYBÍ** | `process.exitCode` v souboru **není**; `validate-all.mjs` volá `tools/kontrola-schematu.py` (1×) a ten soubor **pořád existuje** |
| **L2** | Smazat `tools/kontrola-schematu.py` (a `oprav-check-schema-*`) | ❌ **CHYBÍ** | `kontrola-schematu.py` existuje; `oprav-check-schema*` = **0** (ty smazány ve F0.5) |
| **L3** | Commitnout šablonu (brány, `release.yml` bez cizí hry) | ⚠️ **ČÁSTEČNĚ** | `git ls-files repo/.forge` = **21** ✅; `release.yml` má `forge-quest` **2×** — ale **oba výskyty jsou text o opravě**, ne odkaz (viz §3) |
| **L4** | Prázdná roadmapa šablony | ✅ **HOTOVO** | `grains = 0` (bylo 31) |
| **L5** | `.env` do `.gitignore` generátoru | ✅ **HOTOVO** | `git check-ignore .forge/node/.env` → vrací cestu (bylo „nic") |
| **L7** | Opravit komentáře `index.ts:31,233` (`MAX_ATTEMPTS` živý) | ❌ **CHYBÍ** | komentáře tvrdící „mrtvý kód" jsou tam **2×** (`:31`, `:233`); kód ho používá na `:328`, `:679` a rozhoduje na `:394`, `:1338` |
| **L9** | `assets/spec.json` mezi chráněné soubory v `agent.yml` | ❌ **CHYBÍ** | `spec.json` v `agent.yml` (šablona i hra) = **0×** |
| **L10** | `test-local.ps1`: `$Game` → `$Project` | ❌ **CHYBÍ** | `$Game` = **2×** |
| **L11** | Rozdělit guard: `naposledy_selhalo` místo `updated_at` | ❌ **CHYBÍ** | neimplementováno (S12 trvá) |
| **L12** | Doplnit zápis roadmapy do `/report` | ❌ **CHYBÍ** | neimplementováno (S13 trvá) |
| **L13** | Opravit zámek v dispatch smyčce | ✅ **HOTOVO** | commit `6d2a856` + regresní test (8 kontrol) |
| **L14** | Strop a watchdog na `item_id` granule | ❌ **CHYBÍ** | neimplementováno (S14 trvá) |
| **L15** | Vypnout `listGames` fallback pro dispatch | ❌ **CHYBÍ** | neimplementováno (invariant 18 trvá) |
| **L16** | `test-cooldown.py` / `test-eskalace.py`: přepsat, nebo smazat | ❌ **CHYBÍ** | `test-cooldown.py`: `sys.exit` **0×**, `assert` **0×** — a přesto vypíše `CHYBA` a skončí `exit 0` |
| **L17** | Past s `grep` nad skrytými složkami do skillu `dsh-prostredi` | ✅ **HOTOVO** | ve skillu je (i s naměřeným 80 ku 0) |
| **ST1** | `orchestra/prepisy.json` (jeden manifest) | ❌ **CHYBÍ** | soubor neexistuje |
| **ST2** | `forge.config.json` (deklarovaný kontrakt hry) | ❌ **CHYBÍ** | soubor neexistuje |
| **ST3** | Rozdělit šablonu na `core/` a `tools/<engine>/` | ❌ **CHYBÍ** | nezačato (plán to má až jako F3.5, poslední krok F3) |
| **ST4** | Test `agent.yml` | ❌ **CHYBÍ** | `test-ci-workflow.mjs` zmiňuje `agent.yml` **0×** |
| **ST5** | Offline testy `check-assets.py`, `check-wiring.py`, `verify-level-render.py` | ❌ **CHYBÍ** | nezačato |
| **ST6** | Onboarding jako test | ❌ **CHYBÍ** | test neexistuje; `install-into-repo.ps1` je pořád mrtvá větev (`projects/` neexistuje) |
| **ST7** | Limity per `game_id` | ❌ **CHYBÍ** | nezačato |
| **ST8** | `STALE_MINUTES` > timeout nejdelšího kroku | ❌ **CHYBÍ** | nezačato |
| **ST9** | Conductor jako testovatelná jednotka | ❌ **CHYBÍ** | nezačato |
| **ST10** | Parametrizovat `game_id`, odstranit absolutní cesty | ❌ **CHYBÍ** | nezačato |

**Souhrn: ze 13 strojově kontrolovaných doporučení jsou hotová 2 (L4, L5).**
Zbylá jsou hodnocena ručně podle stavu souborů a kódu.

---

## 2. Kde se plán a analýza rozcházejí v POŘADÍ (a co z toho plyne)

Tohle je to podstatné pro přepracování. Oba dokumenty mají vlastní pořadí a
**v jednom bodě si odporují**:

| | `ANALYZA-ARCHITEKTURY` (§5.2, poznámka k prioritě) | `PLAN-ROZVOJ` (§3) |
|---|---|---|
| První | **L1–L4 jsou podmínkou pro cokoli dalšího** (dokud validátor měří špatnou kopii a končí nulou, nemá se strukturální změna jak ověřit) | **F1 Smyčka** (3h zpoždění, cooldown, strop) — „dokud nová granule čeká 3 h, každé měření v F2+ měří rozbitý systém" |
| Druhé | **L11–L14 jsou naléhavější než strukturální práce** | F2 Měření, pak F3 Kontrakt |
| Shoda | L13 = F1.3 (hotovo), L11 = F1.1, L12 = F1.2, L14 = F1.4, L15 = F1.5 | totéž |

**Naměřený stav k tomu:**

- **Oba mají pravdu v tom, že jejich „první" je nehotové.** L1 chybí, F1 chybí.
- **Rozpor je jen zdánlivý, ale má důsledek:** analýza chce **nejdřív ověřitelnost
  (L1)**, plán chce **nejdřív smyčku (F1)**. Nejsou to alternativy — `validate-all.mjs`
  je nástroj, kterým se F1 bude ověřovat. **Dokud L1 není hotové, F1 se nedá
  změřit** (a plán to sám říká u F2.3 a u F1: „Ověření F1 je hotové už teď —
  skript z analýzy §1.2 je regresní test").
- **Konkrétní důsledek pro přepracování:** pořadí má být
  **L1 → F1 (L11/L12/L14/L15) → F2 (L16, ST4, ST5) → F3 (ST1, ST2) → F4 (ST6, ST10) → F5**.
  To je totéž, co oba dokumenty říkají, jen se to nesmí číst jako „L1 je součást F2" —
  **L1 je předpoklad F1**, protože bez něj není čím měřit.

### 2.1 Jedna závislost, kterou analýza nepojmenovává

Analýza má **ST9** (conductor jako testovatelná jednotka) jako **strukturální**
(dny). Plán má **F2.3** totéž. Ale **F1.1, F1.2 a F1.4 jsou změny SQL v conductoru**
— a podle měření dnes **neexistuje test, který by je zachytil**: `test-cooldown.py`
má SQL **opsané** (a nemá ani `assert`), `test-eskalace.py` taky, a
`validate-all.mjs` porovnává `index.ts` s kopií jen **bajtově**.

**Praktický důsledek:** kdo udělá F1.1 (nový sloupec `naposledy_selhalo`) bez
ST9, **nemá jak dokázat, že to funguje** — leda ručním `POST /tick` na živém
conductoru. To je přesně situace, před kterou varuje `AGENTS.md`
(„naměřeno" vs. „vypadá to dobře"). **Doporučení: ST9 udělat jako součást F1,
ne až ve F2** — nebo alespoň `test-zamek-owns.py` vzorem (vytáhnout SQL ze
zdrojáku a spouštět skutečný text funkce).

> **Tohle je „odvozeno", ne „měřeno".** Ověřeno je jen to, že ty testy dnes
> logiku nečtou ze zdrojáku (`test-cooldown.py` má vlastní SQL, `sys.exit` 0×).
> Že to při F1 bude skutečně blokovat, je **úsudek** — a patří k nezávislému
> ověření, ne k rozhodnutí.

---

## 3. Dva nálezy, které v analýze ani v plánu nejsou

### 3.1 Šablona vydává release s doslovným `NAZEV-REPA`

**měřeno + doloženo simulací 1. 10. 2026:**

| Krok | Zjištění |
|---|---|
| Kde | `orchestra/repo/.github/workflows/release.yml:82` a `:143` — `https://ssevcikm-spec.github.io/NAZEV-REPA/` (a `:88` o tom mluví v textu) |
| Je to proměnná? | **Ne.** Je to **literál v `echo`**, ne `${{ github.repository }}` — GitHub Actions ho nechá být |
| Nahrazuje ho instalátor? | **Ne.** `install-into-repo.ps1:42` + `:96 Copy-Item -Recurse` kopíruje `.github` bez substituce; `NAZEV-REPA` **nikde nenahrazuje** (Python walk celé `orchestra/`: jediný další výskyt je komentář v `repo/.forge/node/termux-setup.sh:97-98`) |
| Důkaz | Simulace přesně toho, co dělá instalátor (`Copy-Item repo\.github\* → cíl`): v novém repu zůstane `NAZEV-REPA` **3× doslovně** |
| Důsledek | **Každá nová hra z šablony dostane v poznámkách release nefunkční odkaz.** A je to tiché — CI je zelené, release se vydá |
| Proč to není vidět dnes | `games/uo-shadows` má v `release.yml:82,139` **správné** `…/uo-shadows/`, protože to někdo **ručně** přepsal. Živý release skutečně posílá správnou URL (ověřeno GitHub API) |

**Tohle je posun symptomu, ne oprava.** Před F0 odkazoval `release.yml` na
**cizí živou hru** (`forge-quest`); dnes odkazuje na **neexistující repo**.
Vada („odkaz se neodvozuje") trvá — jen se z „matoucí" stala „nefunkční".
**Patří to k F4.1/F4.2 (onboarding)** a je to nejlepší argument pro to, aby
onboarding byl **test**, ne skript: test, který založí hru z šablony a projde
všechny brány, by na to narazil.

### 3.2 Past: `forge-quest` v `release.yml` vypadá jako nesplněné L3

**měřeno:** naivní hledání `forge-quest` v `release.yml` najde **2 výskyty**
(`:88`, `:141`) — a vypadá to jako „F0 to neopravilo". **Oba jsou ale text
o opravě** („Dřív tu bylo natvrdo `.../forge-quest/` — tedy JINÝ, živý
repozitář"). Kód je správně.

**Proč to sem píšu:** je to **přesně ta past, před kterou varuje `AGENTS.md`**
(„statická kontrola musí číst KÓD, ne komentáře") — a tentokrát by vedla
k opačné chybě: **smazat komentář, který vysvětluje, proč je odkaz odvozený**.
Komentáře s naměřenými hodnotami a historií rozhodnutí **nejsou dluh**.

> **Stejná past z opačné strany, naměřená dnes:** počet volání `test(` v souboru
> (42) vedl k závěru, že dokument lže o počtu testů (36/36). Po **spuštění**
> vyšlo 36/36 — dokument měl pravdu. Statická metrika, která nic nespustí, je
> stejně slabá jako kontrola čtoucí komentáře.

---

## 4. Co jsem naměřil o PROVOZU (kontext pro rozhodování)

| Co | Naměřeno 1. 10. 2026 |
|---|---|
| Conductor | `/health` → `ok: true`, `ready: 6`, `running: 0`, `games: 1` |
| Domácí uzel | `pc-domaci` **off** (naposledy 29. 9. 20:03); `oracle-frankfurt` žije |
| CI cílové hry na `main` | **success** na `807803e` (3/3 check-runs) |
| Poslední práce orchestra | běhy **#235–#241**, poslední 10:09 (6 granul: 2 success, 4 failure) |
| Celkem běhů `agent.yml` | **241**; v posledních 100 je **8 success / 92 failure** |
| PR #26, #27 | **MERGED**, ale `merged_by: ssevcikm-spec` — **člověk**, ne auto-merge |
| Brány dokumentace | `over-dokumentaci.py` 63/0, `over-skily.py` **11**/0, diakritika OK |
| Oba repy | **0 změn** v pracovním stromě (orchestra měla jen `README.md` z této session) |

> **Pozor na výklad „8 success / 92 failure":** to číslo je z **okna posledních
> 100 běhů**, a velká část těch selhání je z **7,5 h výpadku** (červené CI hry),
> ne z vady orchestra. Není to míra kvality orchestra — je to míra velikosti
> toho výpadku. **A to je samo nález:** kdyby conductor stav CI znal (N0.3),
> nebylo by potřeba to dopočítávat z historie běhů.

---

## 5. Doporučené pořadí (1. 10. 2026 večer)

| Pořadí | Co | Proč teď | Riziko, když se to odloží |
|---|---|---|---|
| **1** | **L1** — `process.exitCode` + správná kopie brány v `validate-all.mjs` | Je to **předpoklad měření** F1; hodiny práce | Každé další ověření se dělá nástrojem, který lže zelenou |
| **2** | **ST9 (část)** — testy conductora čtou SQL ze zdrojáku | Bez toho F1 **nemá čím dokázat**, že funguje | F1 se „ověří" ručním tiketem a za týden se neví, co platí |
| **3** | **F1 / L11, L12, L14, L15** — smyčka | Přímo brzdí každou granuli (3 h) a watchdog se nikdy nespustí | Orchestra dál zdržuje každou novou granuli a tváří se, že nic nedělá |
| **4** | **L16, ST4, ST5** — testy, které nic netestují | Dva testy dnes **posvěcují vadu** | Zelená, které se nedá věřit |
| **5** | **F3 / ST1, ST2** — kontrakt | Až po F1/F2 (plán to tak má správně) | — |
| **6** | **F4 / ST6, ST10 + `NAZEV-REPA`** — onboarding | Až když je kontrakt | Nová hra se pořád nedá založit |
| **7** | **F5** — druhá hra | Teprve tady mají abstrakce co měřit | — |

**Co z toho plyne pro „přepracování orchestry":** není to přestavba. Je to
**pět konkrétních oprav** (L1, ST9-část, L11/L12/L14/L15, L16/ST4/ST5, `NAZEV-REPA`),
z nichž **dvě jsou hodiny práce** a **zbytek je dnešní nehotová práce plánu**.
Analýza to říká správně: *„Opravit. Tři provozní vady jsou hodiny práce a přímo
brzdí každou granuli — přestavba by se stavěla na rozbitém základu."*

---

## 6. Co tenhle dokument NEtvrdí

- **Není to nezávislá analýza kódu conductora.** Čísla o `index.ts` (L11–L14)
  přebírám z `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` a z invariantů skillu
  `orchestra`; **sám jsem je neměřil**. Co jsem měřil, je **stav doporučení**
  (existuje/neexistuje soubor, je/není `process.exitCode`), ne jejich obsah.
- **Neověřoval jsem, že S12 (3h zpoždění) v produkci skutečně nastává.** Analýza
  to sama označuje za neprokázané (§6 bod 1) a platí to dál. Doloženo je, že ten
  SQL vrací prázdno a že `roadmapTick` zapisuje právě ten čas.
- **Nerozhoduje o vlastnictví souborů** (F4.3, otázka O6) — to je věcné
  rozhodnutí uživatele, ne agenta.
- **Nenavrhuje novou architekturu.** Kdyby se ukázalo, že orchestra má být
  postavená jinak, tenhle dokument k tomu nedává podklad — jen říká, co je
  hotové a co ne.

**Zdroje:** `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (+ §8 dodatek),
`PLAN-ROZVOJ-ORCHESTRA.md`, `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`,
`HANDOFF.md`, skill `orchestra`.
**Měřicí nástroje:** `_analyza\stav-doporuceni.mjs` (stav doporučení),
`_analyza\stav-ci.mjs` (CI obou repů), `_analyza\stav-agent.mjs` (běhy agenta),
`_analyza\stav-release.mjs` (poznámky release — kde vznikl nález `NAZEV-REPA`).

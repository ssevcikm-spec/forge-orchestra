# Zadání: analýza architektury Forge orchestra

> **Co tenhle dokument JE:** zadání. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Pro koho:** nová session (čistý kontext), která tuhle analýzu provede.
**Kdo to zadává:** session z 1. 10. 2026, která orchestra *nepsala*, ale dnes
v ní opravila jednu bránu a sloučila migraci hry. Zadání je proto psané jako
**otázky s naměřenými fakty**, ne jako „podívej se na orchestra".

**Proč nová session:** analýzu má dělat někdo, kdo ten kód nepsal. Zadávající
session dnes sama upravovala `check-schema.py` — není nezávislá.

---

## 0. Jak začít (a co si NEČÍST jako pravdu)

1. Přečti `C:\Users\Ssevc\Local-Deepseek\AGENTS.md` (**pravidla**) — je krátký.
2. Přečti `HANDOFF.md` (**stav** poslední session).
3. **Nepřebírej tvrzení z dokumentace jako fakt.** Naměřené je jen to, co je
   v tomhle zadání označené jako *změřeno*; zbytek je dokumentace, tedy
   potenciálně zastaralá. Kde můžeš, ověř to kódem.
4. Než začneš psát skripty, načti skill **`dsh-prostredi`** (pasti Windows +
   sandboxu; ušetří ti desítky minut).

**Co NEDĚLAT:**
- Neměnit kód orchestra. Výstupem je **analýza**, ne oprava.
- Nepushovat nic nikam.
- Nepředpokládat, že „je to v dokumentaci" = „je to pravda". Dnešek přinesl
  případ, kdy brána v dokumentaci popsaná jako hotová **tiše neměřila**.

---

## 1. Cíl analýzy

Odpovědět na jednu otázku: **která architektonická rozhodnutí Forge orchestra
způsobují, že se chyby ztrácejí tiše — a která naopak drží?**

Nejde o výčet souborů ani o popis toku dat. Jde o **třídy selhání**:
místa, kde něco může přestat fungovat, aniž si toho kdokoli všimne.

Formuluj nálezy jako **„kdyby X, stalo by se Y a nepoznal by to Z"**.

---

## 2. Naměřená fakta z 1. 10. 2026 (tohle je ověřené)

### 2.1 Konkrétní případ tichého selhání (modelový příklad třídy)

`.forge/check-schema.py` je **tvrdá brána** v CI, běží před vision. Kontroloval
výchozí buňku v `scripts/level.gd` vzorcem `var cell := 16`. Po migraci hry na
izometrii je v kódu `const CELL_W_DEFAULT := 96`:

- regexy nenašly **nic** → cyklus proběhl nad **prázdným seznamem** →
  **brána hlásila zelenou**;
- prozrazoval to jediný řádek `level.gd: výchozí cell=[], fallback=[]`,
  kde `[]` vypadá jako **naměřená nula**;
- opraveno (měří oba tvary, hlásí vadu, když číst nelze), přidán offline test
  `orchestra\tools\test-check-schema.py` (17 testů) do `validate-all.mjs`.

**Zobecnění, které má analýza prozkoumat:** vázne brána na **tvaru kódu**
(regex, konkrétní cesta, konkrétní jméno)? Pak ji refaktoring tiše vypne.
**Kolik dalších bran orchestra má tuhle vlastnost?**

### 2.2 Nalezené konkrétní nesrovnalosti (nezapsané jako opravené)

| # | Co | Naměřeno |
|---|---|---|
| 1 | **`agent.yml` driftuje** a driftová kontrola to hlásí | šablona `repo/` má kroky navíc: *„Kontrola class_name (staticky, Godot to nepozná)"*, *„Kontrola parsování GDScriptu (rychlá brána)"*; hra má kratší varianty. **Hra tedy nemá `class_name` kontrolu.** |
| 2 | **Nové soubory brány a vision nejsou v gitu orchestra** | `git ls-files repo/.forge` je **neobsahuje**: `check-schema.py`, `baseline.py`, `node/vision.test.mjs`, `vision-profile.json` jsou `??` (netrackované). Šablona je tedy v gitu **neúplná**. |
| 3 | **Driftová kontrola zná 12 souborů, brány v ní nejsou** | `orchestra\tools\kontrola-driftu.mjs` `SOUBORY` obsahuje `check-assets.py` a `check-wiring.py`, ale **ne** `check-schema.py`, `baseline.py`, `vision.mjs`, `verify-level-render.py`, `vision-profile.json`. |
| 4 | **Shoda, která je dílem náhody** | Všech 6 souborů z bodu 3 je dnes **shodných** (`sha256` ověřeno) — ale proto, že je někdo dnes ručně zkopíroval (taky já). **Žádné pravidlo to nevynucuje.** Obecné pravidlo: *shoda, kterou nic nehlídá, je náhoda s dobrým jménem.* |
| 5 | **Kdo je zdroj pravdy, není jeden** | `sync-sablona-hra.py` zná 2 soubory s **různými směry** (`CONVENTIONS.md` hra → šablona, `worker.mjs` šablona → hra); `kontrola-driftu.mjs` zná 12 souborů směrem šablona → hra; `sjednot-sablonu.py` řeší `agent.yml` zvlášť. **Tři nástroje, tři seznamy, žádný jediný zdroj.** |

### 2.3 Slepá místa bran, která už byla naměřená dřív

- **Animace:** `check-assets.py` hledá `assets/sprites/walk_*.png`, kde je
  **0 souborů** (chůze je po vrstvách v `tools/blender/sprites/body_d0_f*.png`)
  → kontrola `min_silhouette_iou: 0.80` ze specu se **nikdy neuplatní**.
  Brána to hlásí jako poznámku, ale kdyby se chůze rozbila, CI to nepozná.
- **Hudba:** neměří se, dokud není `assets/audio/music/manifest.json`.
- **`kind` nic neřídí:** v `agent.yml` je jen v šabloně PR komentáře; všechny
  granule roadmapy mají `"kind": "code"`.
- **`MAX_ATTEMPTS` je mrtvý kód** (rozhoduje `pollRuns`), watchdog
  `ESCALATE_AFTER` **jen notifikuje** — strop pokusů neexistuje.

> ### ⚠️ OPRAVA TOHOTO BODU (1. 10. 2026, analýza architektury)
>
> **Tvrzení „`MAX_ATTEMPTS` je mrtvý kód" je NEPRAVDA** — a protože stojí
> v oddíle označeném jako *ověřené*, je potřeba to tady opravit, ne jen
> zmínit v analýze. Naměřeno čtením kódu: `MAX_ATTEMPTS` se **používá** na
> `conductor/src/index.ts:328`, `:394`, `:679`, `:709` a `:1329` a rozhoduje
> o návratu úlohy do fronty i o stavu `failed`. Mrtvý je jen **komentář**
> v conductoru (`:31`, `:233`), který to tvrdí — a ten se ještě neopravil
> (je to změna kódu, ne dokumentace).
>
> **Co je pravda místo toho:** strop **existuje, ale váže úkol, ne granuli.**
> `roadmapTick` zakládá pro každý retry **nový úkol s `attempts=0`**, takže
> smyčka na úrovni granule je nekonečná. Watchdog `ESCALATE_AFTER` (prah 8)
> **jen notifikuje** (což je záměr), ale protože je prah větší než strop (5)
> a počítá běhy **úkolu**, **nikdy se nespustí** — takže „nikdo se to nedozví"
> platí dál, jen z jiného důvodu.
>
> **Zdroj:** `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (S6, S14) a
> `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` §1.2 a §1.3.
>
> **Poučení, které platí pro každé zadání:** i oddíl „tohle je ověřené" je
> jen tak dobrý, jako jeho poslední kontrola. Tvrzení o **kódu** se ověřuje
> **v kódu** — ne převzetím, ani z dokumentace, ani ze zadání.

### 2.4 Mezery `phash` (už zavřené, ale jsou to taky „tiché chyby")

`phash` je slepý na barvu (přebarvený asset = stejný hash) a degeneruje
u jednolitého obrázku. Řešení: barevný podpis + fallback na `sha256`.
**Poučení:** hash je nástroj, jehož meze se musí změřit — tichá chyba
„nezměněno" u změněného assetu je horší než žádná cache.

### 2.5 Rozsah orchestra (pro orientaci, měřeno)

| Co | Počet |
|---|---|
| Nástroje `.mjs` v `orchestra/tools/` | **40** |
| Nástroje `.py` v `orchestra/tools/` | **32** |
| Soubory v šabloně `orchestra/repo/.forge/` | **24** celkem, z toho **17 trackovaných** v gitu a **4 netrackované** (+ `__pycache__`) |
| Hry v registru | `uo-shadows` (aktivní), `forge-quest` (živá, mimo orchestra) |
| Zdroj conductora | `orchestra/conductor/src/index.ts` (Cloudflare Worker + D1) |

---

## 3. Otázky k zodpovězení (jádro zadání)

Odpovídej **jednu po druhé**, každou s odkazem na konkrétní soubor a řádek.
Kde odpověď není v kódu jednoznačná, napiš to — nehádej.

### Blok A — brány a jejich tichá selhání

1. **Kolik bran orchestra existuje a kde všude běží?** (CI v herním repu,
   `agent.yml`, domácí uzel, `validate-all.mjs`, ruční nástroje.) Udělej
   tabulku: brána → kde běží → **co se stane, když se neprovede**.
2. **Které brány závisí na tvaru kódu** (regex, konkrétní jméno souboru, přesná
   cesta) a tedy se dají refaktoringem tiše vypnout? Jdi to ověřit do kódu —
   `check-assets.py`, `check-wiring.py`, `verify-level-render.py`,
   `check-schema.py`.
3. **Která brána umí skončit „zeleně", aniž něco změřila?** Hledej vzory:
   prázdný seznam bez hlášky, `continue` uvnitř cyklu, `try/except` polykající
   chybu, návrat `0`/`None` bez rozlišení.
4. **Má každá brána offline test se známým chybným případem?** Které ne?
   (Vzor, jak to má vypadat: `orchestra\tools\test-check-schema.py`.)

### Blok B — kdo je zdroj pravdy (šablona vs. hra vs. orchestra)

5. **Proč jsou tři synchronizační nástroje se třemi seznamy?** Co se stane,
   když se přidá nový soubor do `.forge/` — kdo si ho všimne?
6. **Co je skutečně zdrojem pravdy pro `providers.json`** (runtime fetch
   z orchestra vs. lokální kopie v repu hry)? Co se stane, když orchestra
   nebude dostupná?
7. **Je šablona `repo/` v gitu úplná?** (Viz fakt 2.2/2 — netrackované
   `check-schema.py`, `baseline.py`, `vision-profile.json`, `vision.test.mjs`.)
   Co by se stalo, kdyby někdo orchestra naklonoval z gitu a založil novou hru?
8. **Jak se pozná, že hra má zastaralou kopii brány?** Dnes to pozná jen
   `kontrola-driftu.mjs`, a to pro 12 souborů, mezi nimiž brány nejsou.

### Blok C — orchestra jako systém, který se sám řídí

9. **Jaká je smyčka dispatch → běh → verdikt → další krok?** Kde v ní může
   úloha tiše zůstat viset nebo se opakovat? (Pozor: `MAX_ATTEMPTS` je mrtvý
   kód, cooldown je 3 h a vynucuje se časem, ne `status`em.)
10. **Kdo rozhoduje o sloučení?** Jaké změny projdou bez člověka a je to
    pokryté? (Pozor: auto-merge pouští `assets/*` a vizuální kontrola
    **neblokuje** — `vision.mjs` má `continue-on-error`.)
11. **Co se stane, když selže model uprostřed řetězu?** Kdo to pozná, kde to
    je vidět a co to udělá s granulí?
12. **Kde jsou v orchestra „mrtvé" části kódu nebo konfigurace?** (Známý
    příklad: `worker.mjs` má `FORGE_CMD` default na smazaný `forge.cmd`;
    `kind` nic neřídí.) Najdi další.

### Blok D — architektura jako rozhodnutí

13. **Která dnešní vlastnost orchestra je důsledek rozhodnutí a která
    historického nánosu?** (GameForge byla 30. 9. 2026 smazána; co po ní
    zůstalo jako mrtvá větev?)
14. **Kdyby orchestra měla zítra vést druhou hru souběžně, co by se rozbilo
    první?** (Zámky `owns` jsou klíčované `{repo}/{soubor}`, modelový řetězec
    je jedna hodnota na N repů, limity free LLM jsou per-repo.)
15. **Je orchestra navržená tak, aby se dala ověřit, nebo tak, aby se dala
    provozovat?** (Rozdíl: první má testy na svou logiku, druhá má logy.)

---

## 4. Řešení, která už existují (neobjevuj je znovu)

| Nástroj | K čemu |
|---|---|
| `orchestra\tools\validate-all.mjs` | jeden běh přes všechny validátory — **ověřeno „✓ VŠE V POŘÁDKU"** |
| `orchestra\tools\kontrola-driftu.mjs` | šablona vs. hra (u YAML **struktura**, ne text) |
| `orchestra\tools\test-check-schema.py` | vzor offline testu brány (17 testů, známý správný i chybný stav) |
| `orchestra\tools\test-ci-workflow.mjs` | 36 testů struktury CI a **pořadí kroků** |
| `orchestra\repo\.forge\node\vision.test.mjs` | 34 offline testů vision proti mock API |
| `orchestra\repo\.forge\baseline.py` | LGTM + cache (24 offline testů, včetně mezí `phash`) |
| `orchestra\tools\zjisti-pages.mjs` | pravda o repech a Pages přes GitHub API |
| `orchestra\tools\status.mjs` | stav orchestra na jednom místě |

---

## 5. Výstup, který má vzniknout

Jeden soubor v session workspace, např. `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`:

1. **Verdikt na začátek** (3–5 vět): kde se chyby ztrácejí tiše a co je
   největší strukturální riziko.
2. **Tabulka tříd selhání**: třída → konkrétní místa → jak se to pozná dnes →
   co by to odhalilo.
3. **Odpovědi na otázky z §3** — každá s odkazem na soubor a řádek.
4. **Doporučení** rozdělená na „levné a hned" vs. „strukturální".
   U každého: co to zabrání a jak se pozná, že to funguje.
5. **Co analýza NEZJISTILA** — otevřené otázky a místa, kam jsi nedohlédl.
   (Tenhle oddíl je povinný. „Nevím" je hodnotný výsledek.)

**Co do výstupu nepatří:** popis toho, co je v které složce, výčet souborů,
obecné rady o testování. Cílem je **rozhodnutí**, ne inventura.

---

## 6. Návrh promptu pro nový chat

> Přečti `C:\Users\Ssevc\Local-Deepseek\ARCHITEKTURA-ANALYZA-ZADANI.md`
> a proveď analýzu podle něj. Nejdřív `AGENTS.md` (pravidla) a skill
> `dsh-prostredi`, pak teprve kód. Výstupem je
> `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`. Kód orchestra neměň a nic nepushuj.

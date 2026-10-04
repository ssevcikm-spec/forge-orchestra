
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
---

## 17. Ověření práce AKČNÍ session — PLÁNOVACÍ session 2. 10. 2026 (11:4x–12:4x UTC)

> **Co je tenhle oddíl:** **výsledek nezávislého ověření** práce akční session
> (§16, omyly 40–50). **Není to stav** — ten se mění — ale je to **doklad,
> co z tvrzení §16 obstálo a co ne**. Každé tvrzení níž má **vlastní** příkaz
> a výstup; **žádné číslo není opsané z §16**.
>
> **Zadání bylo ověřeno PŘED prací** (`python _analyza\zadani-kontrola.py`
> → `exit 0`; oba commity seděly: `orchestra` `7c11b2d`, `uo-shadows` `194735d`).
> **Během práce se stav nezměnil** — pracovalo se jen v pracovních stromech
> (`_analyza\h17-kladna`, `_analyza\h17-klidna`), klon uživatele zůstal
> se **4 změněnými soubory** (ověřeno `git status --porcelain` na začátku i na konci).

### 17.1 Zadání sedí na skutečnost (kontrola hlavičky)

| Co zadání tvrdilo | Naměřeno (`_analyza\zadani-kontrola.py`, `exit 0`) |
|---|---|
| `orchestra` = `7c11b2d` | **`7c11b2d50`** — OK |
| `uo-shadows` = `194735d` | **`194735d9b`** — OK |
| `orchestra` pushnuto | `origin/main..HEAD` = **0** — OK |
| `uo-shadows` nepushnuto | `origin/main..HEAD` = **0**, ale **4 změněné soubory** — OK (záměr) |
| B1 nasazeno | `_analyza\f3-over-deploy.mjs 7c11b2d` → **`✓ VŠE V POŘÁDKU`**, deploy **#32** `head:7c11b2d50` |

**Nic z hlavičky nebylo v rozporu se skutečností.** Jediný rozdíl proti §16:
`/health` hlásilo **`ready:4`** (11:33 UTC) místo `ready:7` — to je **stav,
ne vada** (úlohy se mezitím vydaly a selhaly, čekají v cooldownu).

### 17.2 Úkol 1 — Úkol A ověřen NEZÁVISLE ✅ (a jedno zpřesnění)

**Nejdřív to, kvůli čemu je celý §16.8 omyl 50 — jsou změny v KLONU?**
Naměřeno `_analyza\h17-kontrola-klonu.py` (vlastní nástroj, jiné otázky než
`b-sonda-65.py`; porovnává **obsah bajt na bajt** + SHA-256):

| Soubor | klon | scratch | shodné |
|---|---|---|---|
| `scripts/combat.gd` | 5 292 B, `9b6aeba1894b2f70` | 5 292 B, `9b6aeba1894b2f70` | **ANO** |
| `tests/run_tests.gd` | 48 423 B, `dbf19ba206597720` | 48 423 B, `dbf19ba206597720` | **ANO** |
| `scripts/player.gd` | 2 353 B, `21afc6f3d5fff0df` | 2 353 B, `21afc6f3d5fff0df` | **ANO** |
| `.forge/roadmap.json` | 24 215 B | 23 125 B | **NE** |
| `docs/ARCHITEKTURA.md` | 17 960 B | 15 848 B | **NE** |

→ **Práce Úkolů A i B je v klonu** (omyl 50 je napravený). Dva soubory se
liší **správně**: jsou to dokumenty, které akční session psala **až po** měření
ve scratchi (§16.2 je psal do klonu). **Není to nález** — ale je to důvod,
proč se „hotovo" u **dokumentů** nedá dokazovat scartchem.

Navíc ověřeno, že znaky obou Úkolů jsou **v kódu** (ne v komentářích):
`TestUrovenBezIzo` ✅ · `izo_pokusu == 0` ✅ · `player.move(` ✅ · starý zakázaný
vzor `contains("level.iso_position")` **není** ✅ · `func resolve(` ✅ ·
`"armor_rating" in defender` ✅ · `attacker.has(` **není** ✅ ·
`komponenta.has_method("hodnota")` ✅ · `cb.resolve(` ✅.

**Vlastní mutační běhy** (`_analyza\h17-mutace-a.py`, 6 běhů nad **čerstvým**
`git worktree` `_analyza\h17-kladna`, `exit 0`):

| Běh | Co je v kódu | Naměřeno |
|---|---|---|
| `1-baseline` | `origin/main`, původní test, žádné `move()` | **59 kontrol, 0 selhání** (`exit 0`) |
| `2-opraveny-test` | **celý** soubor testů z klonu, `move()` není | **64 kontrol, 0 selhání** + **pojmenovaná poznámka** o tom, že se kontrola NEMĚŘÍ |
| `3-pres-level` | opravený test + `move()` se ptá úrovně na izo | **65 kontrol, 1 selhání** (`exit 1`) — `izo_pokusu: 1` |
| `4-zdravy` | opravený test + zdravé `move()` | **65 kontrol, 0 selhání** — `izo_pokusu: 0` |
| `5-pres-walk` | opravený test + `move()` se ptá úrovně na **průchodnost** | **65 kontrol, 0 selhání** — `izo_pokusu: 0` |
| `6-stary-pres-level` | **původní** test + `move()` přes úroveň | **60 kontrol, 1 selhání** (`exit 1`) |

**Běh 5 je odpověď na otázku ze zadání** („netestuje moje mutace něco jiného,
než tvrdím?"): `move()` **se úrovně ptá** — a test **přesto projde**, protože
`izo_pokusu` zůstane 0. Kdyby brána měřila „ptá se úrovně", spadla by tady.
**Naměřená podmínka je přesně „ptá se na IZO PROJEKCI", ne „ptá se úrovně".**

**Proč 64 v klonu a 60 ve scratchi — naměřeno, ne odvozeno:** blok Úkolu B volá
`cb.resolve()`, což je **5 nových kontrol** (64 − 59 = 5). Scratch má Úkol B
**vypnutý** (jeho runner si testy staví patchem, viz komentář
`a-mutace-run.py:108–114`), proto 60. V bězích 2–5 je 64 + 1 nová kontrola
Úkolu A = **65**, resp. 64 bez `move()`. **Všechna čísla sedí na vysvětlení,
které se dá spočítat.**

**Odpověď na otázku „oslabil jsem bránu?" — NE, a je to doložené:**

1. Starý test **není slepý, je nastražený**: naměřeno (běh 6) vadu „`move()`
   přes úroveň" **chytí taky** (`60/1`). Není tedy pravda, že by oprava něco
   ztratila — jen starý test měřil **přítomnost textu** a zakazoval
   `player.gd:40`, což je **legitimní kód** (prompt granule ho přikazuje
   zachovat), a **dnes je ta větev živá**: `level.gd` (viz níž) metodu nemá,
   takže `else` na `player.gd:45` se v běžící hře **provede**.
2. Nový test měří **chování** (zavolá `move()` a počítá, na co se ptal),
   takže legitimní fallback nezablokuje.
3. **Cesta „izo přes `world`" se neuzavírá** — je zapsaná jako smlouva
   v roadmape (`world.nodes`) i v `docs/ARCHITEKTURA.md`. Nedá se ale
   **vynutit testem**, dokud neexistuje **poskytovatel**: `iso_position` žije
   jen v `_retired/world.gd` (naměřeno `grep`, 1 soubor, mimo `scripts/`)
   a `game.gd` registr `component()` nemá (v `scripts/` ho poskytuje **jen
   atrapa** `TestKostra` v `run_tests.gd:1043`). Vynutit ji dnes = vynutit
   **mrtvý kód** — přesně to, před čím varuje `AGENTS.md`.

### 17.3 Úkol 2 — Úkol B ověřen ✅, ale jedna vada NEBYLA chycena ⚠

**Vlastní mutační běhy** (`_analyza\h17-mutace-b.py`, nad klonem, `exit 0`
s výjimkou M3 — viz níž):

| Mutace v `combat.gd` | Naměřeno |
|---|---|
| zdravý kód (přesně z klonu) | **64 kontrol, 0 selhání** |
| **M1** `"armor_rating" in defender` → `defender.has(...)` | **5 selhání** → CHYCENO (`Nonexistent function 'has' in base 'Node2D (TestBojovnik)'`) |
| **M2** čtení `zbran.damage` → `zbran.has("damage")` | **4 selhání** → CHYCENO (`... in base 'Node (TestZbran)'`) |
| **M3** vypuštění větve `hodnota(attr)` | **0 selhání** → **NECHYCENO** |
| **M4** vzorec `1 + Str/10` → `1 + Str/5` | **1 selhání** → CHYCENO |
| **M5** `zbroj = defender.armor_rating` → `zbroj = 0` | **1 selhání** → CHYCENO |

> **⚠ NÁLEZ (vlastní, ne z §16): brána je slabá v tom, co si nárokuje.**
> M3 **nechá testy zelené**. Není to tím, že by se větev `hodnota()` nevolala —
> naměřeno sondou `_analyza\h17-sonda-vetve.py` (do `_cislo()` se vložily
> čítače obou větví): **větev A se volá 2×, větev B 9×**. Je to tím, že
> **obě větve vracejí totéž číslo**: jediná větev A, která se v testech použije,
> je `TestSkilly.hodnota("boj_na_blizko")`, a ten objekt **vlastnost
> `boj_na_blizko` nemá** — takže i větví B vyjde `0`. **Test tedy nedokáže
> rozlišit „metoda první" od „vlastnost první".**
>
> **Co to znamená prakticky:** `resolve()` v produkci sáhne na `hodnota()`
> jako první (`combat.gd:97–98`), ale **test to neověřuje** — projde i varianta,
> která metodu ignoruje. Pořadí větví je přitom **to, co drží smlouvu**
> („atributy se čtou přes `hodnota(Dex)`").
>
> **Jak to ověřit je jedna kontrola:** dát do testu atrapu, kde je `hodnota("Str")`
> **v rozporu** s vlastností `Str` (např. 100 vs. 10). Sonda to zkusila
> (`h17-sonda-vetve.py`, druhá část): s větví A vrátí `resolve()` `damage = 13`;
> bez větve A se běh rozpadne na **33 kontrol, 1 selhání**. **Lék je známý
> a je levný** — patří do nové granule `tests.harness` (§17.9 otázka 1).

**Tvar smlouvy — ověřeno v obou místech čtením diffu:**

* `.forge/roadmap.json` → `sim.combat.prompt` nese **typy, odkud čísla
  (registr komponent), vzorec i přijímací kritérium**; `done_note` má datum
  opravy. Diff: `2 +2 −2`.
* `docs/ARCHITEKTURA.md` → řádek Boj s **tvarem dat** + **nová §2.1**
  („Tvar dat a přijímací kritérium u smluv") s třemi pravidly. Diff: `38 +1 −1`.

**`lint-roadmapa` — ověřeno MNOŽINOVĚ, ne jen počtem** (`_analyza\h17-lint-roadmapa.py`,
dva stromy: `_analyza\h17-klidna` = čistý `origin/main`, a pracovní strom klonu):

```
A) origin/main (roadmapa PŘED Úkolem B):  exit=0  problémů=14  [5]=11  [3]=3  size_lines=13/21
B) pracovní strom klonu (PO Úkolu B):     exit=0  problémů=14  [5]=11  [3]=3  size_lines=13/21
ROZDÍL: jen v A [5] 0 · jen v B [5] 0 · jen v A [3] 0 · jen v B [3] 0
```

→ **Tvrzení §16.2 sedí** (11× `[5]`, 13 z 21) a je **silnější**, než tvrdilo:
lišily by se i jednotlivé řádky, ne jen počty.

### 17.4 Úkol 3 — obě měřidla (C1, C2) ověřena VLASTNÍM měřením ✅

**C1 (`a3-kontrola.mjs`)** — namísto podvrhu přepsáním souboru (jak to dělá
`c1-dukaz-selhani.py`) jsem si postavil **lokální HTTP server**, který
odpovídá **živými daty** ze skutečného conductora, ale `/queue` vrátí to, co
vracel neexistující endpoint `/tasks` — **rozcestník služby**
(`_analyza\h17-podvrh-conductor.mjs`, port 8791). Do repa se **nesáhlo**.
Vlastní měřidlo `_analyza\h17-over-c1.mjs`:

```
1) ŽIVÝ CONDUCTOR      → /queue 50 úloh, /roadmap 16 řádků  →  ✓ VŠE V POŘÁDKU   (exit=0)
2) PODVRH              → /queue 0 úloh
   CHYBA /queue nevrátil parsovatelný seznam úloh:
     {"service":"forge-conductor","endpoints":[...],"poznamka":"PODVRH pro H17..."}
                          →  ✗ NALEZENO 1 PROBLÉMŮ   (exit=1)
```

→ **Podmínka umí selhat** — a to je tvrzení, které `exit 0` sám o sobě netvrdí.
Živý stav v témž běhu: `world.nodes` → úloha **#145** `stav=ready pokusů=1`,
`entity.player.api` → **#146** `stav=ready pokusů=1`, `persist.save.state`
a `engine.shell` v `/roadmap` **nejsou**.

**C2 (`hl-rizika-jazyka.py`)** — vlastní podvrh otisku vstupů
(`_analyza\h17-over-c2.py`), cíleně, ne přegenerováním:

| Běh | Naměřeno |
|---|---|
| 1) zdravý inventář | `otisk vstupů SEDÍ: 7957a61c058c85de (772 souborů)`, **`exit 0`** |
| 2) `otisk_vstupu.sha256` přepsán na `0000…` | `CHYBA: INVENTÁŘ JE ZASTARALÝ / NEZMĚŘENÝ` — `otisk VSTUPŮ se rozešel`, **`exit 1`** |
| 3) návrat na původní bajty | **`exit 0`**, sha256 inventáře **`88132937cf2fe659`** = původní |

→ **Měřidlo pozná zastaralost** a **úklid je bajt na bajt** (ověřeno hashem,
ne dojmem). Past ze zadání („přegenerováním zastaralost zmizí") jsem obešel
tím, že jsem přepsal **jen otisk uvnitř** inventáře.

**Sekce L validátoru nástroj SPOUŠTÍ a neodmítá ho** — naměřeno spuštěním
`node orchestra\tools\validate-all.mjs`:

```
  OK   N1: inventář se hlásí stářím a otiskem vstupů; zastaralý SHODÍ nástroj
       — hl-rizika-jazyka.py → exit=0
```

**A rozhodnutí o `c2-mutace.py` je správné** — naměřeno **spuštěním pojistky**,
ne čtením: zdroj `_analyza\c2-mutace.py` obsahuje `write_bytes` (přepisuje
`_inventar.json` a vrací ho), takže by ho pojistka
(`zapisuje = /write_text|write_bytes|copyfile|copy2|writeFileSync/`,
`validate-all.mjs:344`) **odmítla**. `c2-mutace.py` do sekce L **nepatří**.

### 17.5 Úkol 4 — B1 v provozu ✅ a #146 ❌ (a hlavní nález téhle session)

**1) `validate-all.mjs` po deployi B1 — NENÍ „0 problémů".** Naměřeno
`node orchestra\tools\validate-all.mjs` → **`✗ NALEZENO 3 PROBLÉMŮ`, `exit 1`**:

| Brána | Otevřela | Výsledek |
|---|---|---|
| `test-check-schema.py` | **17 kontrol** (mimo sandbox) | `exit 0` |
| `vision.test.mjs` (šablona) | **36 kontrol** (mimo sandbox) | `exit 0` |
| `baseline.py testy` (šablona) | **24 kontrol** (mimo sandbox) | `exit 0` |

V sandboxu padají **všechny tři před první kontrolou**:
`PermissionError: [WinError 5] … \Temp\dsh-pQac9S\schema-test-…` a
`Error: spawn EPERM` (`execFile`, `vision.test.mjs:147`). → **Jsou to
„neproběhlo (prostředí)", ne „červená"** — a to je **třetí stav**, který
`AGENTS.md` i skill `overovani` §7.13 vyžadují zapisovat.

> **⚠ Zpřesnění proti §16.6:** tvrzení „B1 měl odstranit ten jediný problém"
> **platí jen o cooldownu**. Cooldown guard je po B1 **zelený** (naměřeno:
> všech 5 scénářů OK, `SQL ze zdrojáku: 7 řádků`, `NOT EXISTS` v něm je).
> Zbylé 3 problémy **s B1 nesouvisely** — v `§16.9` byly vedené jako
> „Neproběhlo (prostředí): po Úkolu D už nic", což **nebylo správně**:
> `baseline.py testy` v tom výčtu **vůbec nebyl** (a je zelený, 24/24).

**2) PR #146 — NEEXISTUJE. A ani žádný PR z těch pěti běhů.**

Naměřeno GitHub API (`actions/runs`, `pulls`): běhy **#142–#146** vznikly
**2. 10. 11:12:56–11:13:07 UTC**, **všechny `completed/failure`**. Otevřených
PR je **0 z 31**; poslední sloučený je **#31** (2. 10. 08:02).

| Běh | Na čem selhal | `[test]` v logu |
|---|---|---|
| **#146** | krok „Agent nic nezměnil → hlásíme neúspěch" | **59 kontrol, 0 selhání** |
| **#145** | „Kontrola parsování" (`scripts/world.gd`) | — |
| **#144** | „Kontrola parsování" (`scripts/enemy.gd`) | — |
| **#143** | „Kontrola parsování" (`scripts/crafting.gd`) | — |
| **#142** | „Kontrola parsování" (`scripts/npc.gd`) | — |

> **⚠⚠ HLAVNÍ NÁLEZ: hypotéza ze zadání je VYVRÁCENÁ.**
> §16.7 i §2.6 zadání tvrdily, že **#146 selhala proto, že worker pracoval
> proti commitu BEZ opravy testu** a spadla na **kontrole izo projekce**.
> **Naměřeno z logu běhu:**
>
> 1. **Kontrola izo projekce tu vůbec nebyla spuštěna** — v běhu #146 je
>    `[test] 59 kontrol, 0 selhání`: to je **přesně baseline z `origin/main`**
>    (naměřeno vlastním během 1: 59/0), kde nová kontrola ještě není a `move()`
>    v repu není. Testy tedy **prošly** — což znamená, že **agent nezměnil kód**.
> 2. **Skutečná příčina #146 je jiná: rate limit poskytovatele.** V logu
>    je **8×** `litellm.RateLimitError`:
>    `Request too large for model openai/gpt-oss-120b … on tokens per minute
>    (TPM): Limit 8000, Requested 14398` → Aider **žádnou editaci neprovedl**.
>    Navíc se model jmenoval **`openai/openai/gpt-oss-120b`** (dvojitý prefix)
>    a Aider ho neznal: `Warning … Unknown context window size` +
>    `Did you mean one of these? … openrouter/openai/gpt-oss-120b`.
> 3. **Ani ostatní čtyři běhy neselhaly na opravě testu** — spadly na
>    **„Kontrola parsování"** u čtyř **různých** souborů, které si agenti
>    vyrobili sami: `world.gd` (`Cannot infer the type of "cell_arr"`),
>    `enemy.gd` (`Identifier "id" not declared`, `"Combat" not declared`),
>    `crafting.gd` (`Cannot call non-static function "hodnota()" on the class
>    "res://scripts/skills.gd" directly`), `npc.gd` (`Member "position"
>    redefined`) — u tří z nich **`Could not find type "Economy"`**.
>
> **Důsledek:** „oprava testu přišla včas, nebo pozdě?" je **špatná otázka** —
> **v žádném z pěti běhů se k tomu testu nedošlo**. Push opravy by na tyhle
> běhy neměl vliv. A `stary-test-pres-level` v §16.1, který se tvářil jako
> „starý test vadu chytí", platí dál — jen to **není to, co #146 zabilo**.

**3) Tři cesty zápisu `naposledy_selhalo` — čtením SQL, seřazené podle toku:**

| # | Cesta | Místo | Kdy |
|---|---|---|---|
| 1 | `pollRuns` → `/ticked`, **opakovatelné selhání** | `index.ts:432–435` | `nextStatus` = `queued` (pokusy < `MAX_ATTEMPTS`) |
| 2 | `pollRuns` → `/ticked`, **poslední pokus** | tamtéž | `nextStatus` = `failed` |
| 3 | **`/report`**, opakovatelné selhání | `index.ts:1470–1472` | `nextStatus` ≠ `failed` |
| 3b | **`/report`**, poslední pokus | `index.ts:1465–1468` | `nextStatus` = `failed` |

**Čtou ho dva guardy** (oba po B1): `index.ts:930` (dispatch smyčka,
`rm.naposledy_selhalo > datetime('now', ?)`) a `roadmapTick`
(§16.6 uváděl `index.ts:907` — po B1 je to **:930**). Samomigrace sloupce
je na `:546`. **`tsc --noEmit` → `exit 0`** (spuštěno přes
`node orchestra\conductor\node_modules\typescript\bin\tsc`, protože `npx`
na téhle stanici neprojde: „running scripts is disabled").

> **Co z tvrzení o B1 se ověřit NEDALO** (a proč): **že se sloupec plní
> cestou `/report` za běhu.** Cesty 3/3b jsou ověřené **čtením SQL** a `tsc`;
> spustit je znamená **nechat úlohu reálně selhat** a protlačit ji `/report`em,
> což by spotřebovalo pokus živé granulе. **Nevyzkoušeno zůstává i to, že
> v běhu #146 selhalo 5 úloh naráz** — jestli je to záměr (dávka v jednom
> tiku) nebo chybějící pojistka, se z jednoho pozorování určit nedá.

### 17.6 Co se ověřit NEDALO (přiznaná mez)

1. **Že opravený test projde implementací, kterou dodá worker** — worker
   **žádnou nedodal** (všech 5 běhů selhalo před editací nebo na parsování).
   Ověřeno je jen to, že projde na `main` (64/0) a spadne na `move()` přes
   úroveň (65/1).
2. **Že `naposledy_selhalo` plní i `/report`** — jen čtením SQL a `tsc`.
3. **Že pět úloh v jednom tiku je záměr** — jedno pozorování, ne měření.
4. **`hl-rizika-jazyka.py` v CI** — sekce L validátoru je ruční nástroj;
   jestli ho pouští i `ci.yml`, **jsem neměřil**.

### 17.7 Brány — co každá otevřela (past S27)

| Brána | Otevřela | Výsledek |
|---|---|---|
| `_analyza\h17-kontrola-klonu.py` | 5 souborů (obsah + 15 znaků) | `exit 0` |
| `_analyza\h17-mutace-a.py` | **6 běhů** testů hry | `exit 0`, 5× OK + 1× očekávané `exit 1` |
| `_analyza\h17-mutace-b.py` | **6 běhů** (1 zdravý + 5 mutací) | `exit 0` po opravě očekávání; **M3 nechycena** (nález) |
| `_analyza\h17-sonda-vetve.py` | 2 sondy + 2 běhy | `exit 0` — větev A 2×, větev B 9× |
| `_analyza\h17-lint-roadmapa.py` | **2 stromy** (21 granul každý) | `exit 0` — množinově shodné |
| `_analyza\h17-over-c1.mjs` | 2 adresy (živý + podvrh) | `exit 0` — 0 → **1** |
| `_analyza\h17-over-c2.py` | **3 běhy** `hl-rizika-jazyka.py` | `exit 0` — 0 → **1** → 0 |
| `_analyza\c2-sonda-uvozovky.py` | 4 kontroly (2 vzorky + oprava + podmínka) | `exit 0` (obnovený soubor, viz §17.8) |
| `_analyza\g1-diakritika-novych.py` | **48 souborů** | `exit 0` |
| `orchestra\tools\kontrola-diakritiky.py` | **42 souborů** (+2 nové) | `exit 0` |
| `python orchestra\tools\test-check-schema.py` | **17 kontrol** (mimo sandbox) | `exit 0` |
| `node orchestra\repo\.forge\node\vision.test.mjs` | **36 kontrol** (mimo sandbox) | `exit 0` |
| `python orchestra\repo\.forge\baseline.py testy` | **24 kontrol** (mimo sandbox) | `exit 0` |
| `node orchestra\tools\validate-all.mjs` | sekce A–L | `exit 1` — **3 problémy, všechny „neproběhlo (prostředí)"** |
| `node orchestra\tools\lint-roadmapa.py` | 21 granul | `exit 0` — **11× `[5]`, 13 z 21** |
| `tsc --noEmit` (conductor, přes `node`) | typová kontrola | `exit 0` |
| `node _analyza\f3-over-deploy.mjs 7c11b2d` | GitHub API + živý conductor | `✓ VŠE V POŘÁDKU` |
| `python _analyza\zadani-kontrola.py` | hlavička zadání vs. živý stav | `exit 0` |
| `python _analyza\handoff-kontrola-uplnost.py` | 83 klíčových bodů | **83/83**, `exit 0` |

**„Neproběhlo (prostředí)"** — 3 brány v `validate-all.mjs` (výš).
Mimo sandbox byly spuštěny **jednorázově** (uživatel to předem schválil)
a **všechny tři daly `exit 0`** s 17, 36 a 24 kontrolami. **Kód se neměnil.**

### 17.8 Nové nálezy téhle session

| # | Nález | Doklad |
|---|---|---|
| **H1** | **`_analyza\c2-sonda-uvozovky.py` NEEXISTOVAL**, ačkoli na něj odkazovaly **dva** dokumenty (`HANDOFF.md` §16.11 a `g1-diakritika-novych.py`) — a `g1` kvůli tomu končil `exit 1` | `Test-Path` → **False**; `Get-ChildItem _analyza -Filter 'c2-*'` → soubor není. **Doklad, který se ztratil.** Obnoven v téhle session a ověřen vlastním spuštěním |
| **H2** | **Test Úkolu B nedokáže rozlišit „metoda první" od „vlastnost první"** — M3 (vypuštění větve `hodnota()`) testy **neshodí** | `h17-mutace-b.py` M3 → **0 selhání**; `h17-sonda-vetve.py` → větev A 2×, B 9×, obě vracejí totéž |
| **H3** | **Souběh pěti úloh v jednom tiku** (#142–#146 v 11:12:56–11:13:07) a **všech pět selhalo** — čtyři na parsování, jedna na TPM limitu | GitHub API `actions/runs` + logy |
| **H4** | **`FORGE_MODEL: openai/gpt-oss-120b` + `FORGE_PROVIDER: groq`** → Aider dostane **`openai/openai/gpt-oss-120b`**, který nezná | log #146: `Model: openai/openai/gpt-oss-120b`, `Warning … Unknown context window size` |
| **H5** | **Groq free tier má TPM 8 000, ale prompt + kontext mají 14 398 tokenů** → úloha přidělená Groqu **nemůže uspět** | log #146: `Limit 8000, Requested 14398`, **8×** opakováno |
| **H6** | **§16.9 tvrdilo „Neproběhlo (prostředí): po Úkolu D už nic"** — a přitom `baseline.py testy` v tom výčtu nebyl a padá | `validate-all.mjs` → 3 problémy; `baseline.py testy` mimo sandbox **24/0** |
| **H7** | **Aktualita testu Úkolu B je nulová, dokud se herní repo nepushne** — prompt #146 posílá agenta na `docs/ARCHITEKTURA.md`, ale `acceptance` čte `tests` | `acceptance: ["tests", "wiring"]` v roadmape; `viz §2.1` je v **nepushnutém** diffu |

**Sedm nálezů, z toho šest o měřidlech nebo o dokumentaci** — a **ani jeden
není vada kódu, který akční session opravovala**. To je pro tuhle session
podstatné: **její opravy obstály**, selhalo to, co se o nich **tvrdilo**.

### 17.9 Rozhodnutí o pěti otevřených otázkách (ze zadání §3 Úkol 5)

**1) Kdo smí psát do `tests/`? → nová granule `tests.harness`, jedno id, jeden soubor.**
Uživatel rozhodl, že do `tests/` píše **nová granule**. Konkrétně navrhuji:

* **id:** `tests.harness` · **owns:** `["tests/run_tests.gd"]` · **size_lines:** `...`
  (musí být **deklarované**, protože soubor má **1 153 řádků** — výchozích 60
  by auto-merge zamítlo, přesně jako u #28–#30 v §2.3) · **model:** `strong`;
* **co NESMÍ** (aby si nepsala testy na sebe): **nesmí vlastnit `scripts/`** —
  jinak si upraví testovaný kód, aby její test prošel. To je táž vada jako
  „brána, která si najde své vlastní vzory" (`overovani` §7.14);
* **co musí prompt obsahovat:** (a) testy **VOLAJÍ** kód, ne `has_method`;
  (b) **každá kontrola musí umět spadnout** (doložit mutací); (c) **nesmí
  testovat granule, které nejsou `done`** — `engine.shell`, `persist.save.state`;
* **potřebuje `tests/` víc souborů?** Dnes **ne**: v `tests/` je **jediný**
  soubor `run_tests.gd` (1 153 řádků) a je to **jeden spustitelný vstup**
  (`--script res://tests/run_tests.gd`), na který odkazuje CI i `agent.yml`.
  Rozdělení by znamenalo měnit **obě** kopie workflow. **Rozhodnutí: jeden
  soubor**, ale s **deklarovaným `size_lines`**;
* **první úkol té granule** je z nálezu **H2**: přidat do bloku Úkolu B atrapu,
  kde je `hodnota("Str")` **v rozporu** s vlastností `Str` — tím se M3 stane
  chycenou. **Doklad, že to zabere, je změřený** (`h17-sonda-vetve.py`).

**2) `TestAtributy` sjednotit? → NE. Dvojí tvar v `combat.gd` zůstává.**
Naměřeno (H2): obě větve se volají, `combat.gd` tedy **není** práce navíc —
je to **jediná cesta, jak fungovat s oběma tvary**, které v repu reálně jsou
(`attributes.gd` má `hodnota()`, `TestAtributy` i `TestSkilly` ne).
**Sjednocení by nic nezískalo** (žádná kontrola dnes `hodnota()` nevyžaduje)
a **ubralo by**: `attributes.gd` i `skills.gd` ji mají, takže varianta
„vlastnost napřed" by se v produkci **nikdy nepoužila** a kód by nesl dvě
cesty bez důvodu. **Co je slabé, není ten dvojí tvar — je to TEST** (H2),
a ten se opravuje v granuli `tests.harness`.

**3) Rozhodnutí u Úkolu A → SPRÁVNÉ, nemá se trvat na „izo přes `world`".**
Doklady: (a) starý test vadu chytil **taky** (vlastní běh 6: `60/1`), takže
se nic neztratilo; (b) nový měří **chování** místo **přítomnosti textu**;
(c) vynutit „izo přes `world`" by dnes znamenalo vynutit **mrtvý kód**
(`iso_position` je jen v `_retired/world.gd`; `component()` poskytuje jen
atrapa); (d) běh 5 dokazuje, že brána neměří „ptá se úrovně", ale „bere izo
projekci z úrovně". **Smlouva zůstává zapsaná** v roadmape i v designu —
jen se **nevynucuje testem, dokud nemá poskytovatele**.

**4) #145 a #146 → PUSHNOUT opravu hned; čekat na jejich PR nemá smysl.**
Naměřeno: **žádný PR z těch pěti běhů nevznikl** a **příčina selhání s testem
nesouvisí** (H3–H5). Otázka „počkat na výsledek jejich PR" tím **zanikla**.
Navíc **H7**: dokud se herní repo nepushne, posílá prompt granulе agenta
na `docs/ARCHITEKTURA.md`, který v repu **není** — takže **nepushnutí je
samo příčinou dalšího neúspěchu**. Doporučení je i tak **ukázat `git status`
a `git diff --stat` a počkat na vyžádání** (`AGENTS.md`).

> **⚠ POZOR na `acceptance`:** v roadmape je u `sim.combat`
> `"acceptance": ["tests", "wiring"]`, kdežto **zadání tvrdilo „přijímací
> kritérium"** jako text. **`acceptance` nečte žádný kód** (známý nález N11).
> Tvar smlouvy se tedy dostane k agentovi **jen promptem** — a ten je
> v **nepushnutém** diffu. To je další důvod pushnout.

**5) Má se `_analyza\` verzovat? → ANO, ale jen `_inventar.json` — a rozhodně
nevypínat kontrolu.** Naměřeno dnes: měřidlo **umí selhat** (C2: `exit 1`
při rozchodu otisku) a **zachránilo dřív skutečný nález** (7 vad, které už
byly opravené — nález N1). Vypnout ho = vrátit ticho. Tři možnosti:

| Varianta | Co to znamená | Verdikt |
|---|---|---|
| **(a) verzovat `_inventar.json`** | zastaralost je vidět jako **změna v gitu**, ne až spadnutím brány | **DOPORUČUJI** |
| (b) nechat, jak je | inventář je generovaný a necommitovaný → **každá session měnící kód vidí červenou**, která vypadá jako vada nástroje | dnešní stav, drahý |
| (c) vypnout kontrolu | zmizí i to, co dnes funguje | **NEDOPORUČUJI** |

**A konkrétní úkol pro akční session:** přidat do `AGENTS.md` (a do
`PREDAVANI-SESSION.md` §6.2 D) větu *„každá session, která mění kód, musí
přegenerovat `_analyza\_inventar.json`"* — dnes to ví jen `HANDOFF.md` §16.10
bod 4, tedy **stav, ne pravidlo**.

### 17.10 Nové nástroje téhle session (v `_analyza\`, mimo CI)

| Nástroj | Co dělá |
|---|---|
| `h17-kontrola-klonu.py` | obsah klon vs. scratch (bajt + SHA-256) + znaky obou Úkolů v kódu |
| `h17-mutace-a.py` | **6 běhů** Úkolu A nad čerstvým worktree; měří i `izo_pokusu` |
| `h17-mutace-b.py` | **6 běhů** Úkolu B (zdravý + M1–M5); odhalil H2 |
| `h17-sonda-vetve.py` | čítače obou větví `_cislo()` + atrapa v rozporu s vlastností |
| `h17-lint-roadmapa.py` | `lint-roadmapa` nad **dvěma stromy**, množinově |
| `h17-over-c1.mjs` + `h17-podvrh-conductor.mjs` | C1: lokální podvrh conductora **bez zásahu do repa** |
| `h17-over-c2.py` | C2: vlastní podvrh otisku + ověření úklidu hashem |
| `h17-behy.mjs`, `h17-log-behu.mjs`, `h17-vsechny-behy.mjs`, `h17-beh145.mjs` | čtení běhů a logů z GitHub API (odhalily H3–H5) |
| `c2-sonda-uvozovky.py` | **obnovený** doklad z §16.11 (H1) — čistě čtoucí, ověřeno hashem |

> **Po sobě uklizeno:** pracovní stromy `_analyza\h17-kladna` a
> `_analyza\h17-klidna` jsou **zaregistrované** (`git worktree list`) — záměrně,
> aby se daly zopakovat běhy; **zrušit je má akční session** (`git worktree
> remove --force`), až je nebude potřebovat. Sonda `h17-podvrh-conductor.mjs`
> běžela na pozadí a byla ukončena. `_analyza\_inventar.json` je **bajt na bajt**
> původní (sha256 `88132937cf2fe659`).

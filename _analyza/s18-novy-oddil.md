
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
---

## 18. Ověření práce AKČNÍ session — PLÁNOVACÍ session 2. 10. 2026 (12:2x–13:3x UTC)

> **Co je tenhle oddíl:** **výsledek nezávislého ověření** práce akční session
> (§16, omyly 40–50), kterou o krok dřív ověřovala jiná plánovací session (§17).
> **Není to stav** — ten se mění. Je to **doklad, co obstálo, co ne, a čím to
> bylo změřeno**. **Žádné číslo níž není opsané** z §16 ani z §17; každé má
> vlastní příkaz a výstup.
>
> **Zadání bylo ověřeno PŘED prací** (`python _analyza\zadani-kontrola.py`
> → `exit 0`; oba commity seděly: `orchestra` `7c11b2d`, `uo-shadows` `194735d`).
> **Klon uživatele zůstal nedotčený** — všechny mutace běžely v pracovních
> stromech; `git status --porcelain` na začátku i na konci: orchestra
> **1 soubor**, hra **4 soubory** (tytéž).

### 18.1 Zadání sedí na skutečnost — až na JEDNO tvrzení

| Co zadání tvrdilo | Naměřeno | Verdikt |
|---|---|---|
| `orchestra` = `7c11b2d` | **`7c11b2d50`** | **OK** |
| `uo-shadows` = `194735d` | **`194735d9b`** | **OK** |
| **`uo-shadows` NEPUSHNUTO** (`origin/main..HEAD` = 0, 4 změny) | **`origin/main..HEAD` = 0** a **`194735d` JE na `origin/main`** (`git branch -r --contains` → `origin/main`) | **NEPRAVDA** — repo **je pushnuté**; „4 změněné soubory" jsou **necommitnuté úpravy**, ne nepushnuté commity |
| `orchestra` pushnuto | `0` | **OK** |
| B1 nasazeno | `f3-over-deploy.mjs 7c11b2d` → **`✓ VŠE V POŘÁDKU`**, deploy **#32** `head:7c11b2d50` | **OK** |

> **⚠ NÁLEZ H9 — zadání míchá „nepushnuto" a „necommitnuto".** §17.1 to
> vyhodnotilo jako „OK (záměr)", ale **není to totéž**: nepushnutý commit by
> **zmizel** s klonem, necommitnutá změna taky — ale jen to druhé se dá opravit
> pushem. Konkrétně: **`194735d` (oprava N3) je pushnutá a nasazená**, kdežto
> **`docs/ARCHITEKTURA.md` §2.1 a blok Úkolu A/B v `tests/` jsou jen v pracovním
> stromě**. Pro Úkol 2 zadání (push) to znamená, že **push sám o sobě nestačí** —
> musí se **nejdřív commitnout**.

### 18.2 Hlavní úkol — jsou změny Úkolů A i B SKUTEČNĚ v klonu?

**Naměřeno dvěma nezávislými nástroji** (vlastní `h17-kontrola-klonu.py` i cizí
`b-sonda-65.py`, oba `exit 0`):

| Soubor | klon | scratch | shoda |
|---|---|---|---|
| `scripts/combat.gd` | 5 292 B, `9b6aeba1894b2f70` | 5 292 B, `9b6aeba1894b2f70` | **ANO** |
| `tests/run_tests.gd` | 48 423 B, `dbf19ba206597720` | 48 423 B, `dbf19ba206597720` | **ANO** |
| `scripts/player.gd` | 2 353 B, `21afc6f3d5fff0df` | 2 353 B, `21afc6f3d5fff0df` | **ANO** |

→ **Omyl 50 je napravený: práce Úkolů A i B je v klonu** (ne jen ve scratchi).
Navíc ověřeno, že v klonu jsou **znaky obou Úkolů v KÓDU** (ne v komentářích):
`TestUrovenBezIzo` ✅ · `izo_pokusu == 0` ✅ · `player.move(` ✅ · starý zakázaný
vzor `contains("level.iso_position")` **není** ✅ · `func resolve(` ✅ ·
`"armor_rating" in defender` ✅ · `attacker.has(` **není** ✅ · `cb.resolve(` ✅.

**A ještě jeden důkaz, který nic neopravoval:** testy dávají v **klonu**
i ve **scratchi** stejné číslo — **64 kontrol, 0 selhání** (vlastní běh,
`b-sonda-65.py`). Kdyby blok Úkolu B chyběl v klonu, klon by dal **60/0**
(naměřeno v §17.2). **Rozdíl 64 − 60 = 4–5 kontrol** je přesně blok Úkolu B.

### 18.3 Úkol A — oba směry mutace, VLASTNÍM spuštěním ✅

`python _analyza\h17-mutace-a.py` → **`exit 0`** (6 běhů nad čerstvým worktree
`_analyza\h17-kladna`; soubor testů se bere **celý z klonu**, ne patchem):

| Běh | Co je v kódu | Naměřeno |
|---|---|---|
| `1-baseline` | `origin/main`, původní test, žádné `move()` | **59 kontrol, 0 selhání** |
| `2-opraveny-test` | opravený test z klonu, `move()` není | **64 / 0** + **pojmenovaná poznámka**, že se kontrola NEMĚŘÍ |
| `3-pres-level` | opravený test + `move()` se ptá úrovně na izo | **65 / 1** (`exit 1`) — `izo_pokusu: 1` |
| `4-zdravy` | opravený test + zdravé `move()` | **65 / 0** — `izo_pokusu: 0` |
| `5-pres-walk` | opravený test + `move()` se ptá úrovně na **průchodnost** | **65 / 0** — `izo_pokusu: 0` |
| `6-stary-pres-level` | **původní** test + `move()` přes úroveň | **60 / 1** (`exit 1`) |

**Běh 5 je ta odpověď, kterou `exit 0` sám netvrdí:** `move()` **se úrovně ptá**
— a test **přesto projde**, protože `izo_pokusu` zůstane 0. Kdyby brána měřila
„ptá se úrovně", spadla by tady. **Měřená podmínka je „bere izo projekci
z úrovně", ne „ptá se úrovně".**

### 18.4 Úkol B — mutace M1–M5, VLASTNÍM spuštěním ✅ (a M3 NECHYCENA)

`python _analyza\h17-mutace-b.py` → **`exit 1` — a to je SPRÁVNĚ**: runner hlásí
rozchod jen u M3, což je **známý nález H2** (viz 18.5). Všechna ostatní čísla
sedí na §17.3:

| Mutace v `combat.gd` | Naměřeno | Verdikt |
|---|---|---|
| zdravý kód (bajt na bajt z klonu) | **64 / 0** | — |
| **M1** `"armor_rating" in defender` → `defender.has(…)` | **5 selhání** (`Nonexistent function 'has' in base 'Node2D (TestBojovnik)'`) | **CHYCENO** |
| **M2** `zbran.damage` → `zbran.has("damage")` | **4 selhání** (`… in base 'Node (TestZbran)'`) | **CHYCENO** |
| **M3** vypuštění větve `hodnota(attr)` | **0 selhání** | **NECHYCENO** |
| **M4** `1 + Str/10` → `1 + Str/5` | **1 selhání** (`naměřeno: 5`) | **CHYCENO** |
| **M5** `zbroj = defender.armor_rating` → `zbroj = 0` | **1 selhání** (`naměřeno: 5`) | **CHYCENO** |

**Každá mutace se po zápisu přečetla z disku a ověřila**, že měřená podmínka
skutečně přestala platit (`assert najdi not in cti(COMBAT)`) — to je poučení
z `overovani` §7.14 a je to jediný důvod, proč se „M3 nechycená" dá odlišit od
„mutace se tiše neprovedla".

### 18.5 Nález H2 (slabá brána) — PŘÍČINA POTVRZENA, ne opsána

`python _analyza\h17-sonda-vetve.py` → `exit 0`:

```
  volání větve A (`hodnota(attr)`) : 2      → obě pro klíč "boj_na_blizko"
  volání větve B (vlastnost)       : 9      → Dex, boj_na_blizko, Str, …

  SONDA 2 — jak se chová resolve(), když je `hodnota()` v ROZPORU s vlastností
     S větví A (hodnota napřed)    64 kontrol, 0 selhání   → damage = 13
     BEZ větve A (jen vlastnost)   33 kontrol, 1 selhání
```

→ **Příčina je v ČÍSLECH, ne v tom, že by se větev nevolala** (volá se 2×).
Obě větve vracejí totéž číslo, protože jediná atrapa s `hodnota()` je
`TestSkilly.hodnota("boj_na_blizko")` — a ta objekt **vlastnost `boj_na_blizko`
nemá**, takže i větví B vyjde `0`. **Lék je změřený:** atrapa v rozporu
(`hodnota("Str") = 100` vs. vlastnost `Str = 10`) → s větví A `damage = 13`,
bez větve A se běh rozpadne (`33 / 1`). **Patří do granule `tests.harness`.**

### 18.6 Měřidla C1 a C2 — obě ověřena VLASTNÍM měřením ✅

**C1 (`a3-kontrola.mjs`, sekce D)** — `node _analyza\h17-over-c1.mjs` proti
**živému** conductora a proti **lokálnímu podvrhu** (`h17-podvrh-conductor.mjs`,
port 8791; do repa se **nesáhlo**):

```
1) ŽIVÝ     /queue 50 úloh, /roadmap 16 řádků → ✓ VŠE V POŘÁDKU      (exit=0)
            world.nodes → #145 stav=ready pokusů=1
            entity.player.api → #146 stav=ready pokusů=1
            persist.save.state, engine.shell → v /roadmap NEJSOU
2) PODVRH   /queue 0 úloh
            CHYBA /queue nevrátil parsovatelný seznam úloh: {"service":"forge-conductor",…}
            → ✗ NALEZENO 1 PROBLÉMŮ                                  (exit=1)
```

**C2 (`hl-rizika-jazyka.py`)** — `python _analyza\h17-over-c2.py` → `exit 0`:

| Běh | Naměřeno |
|---|---|
| 1) zdravý inventář | `otisk vstupů SEDÍ: 0ac061f1dc34aa36 (772 souborů)`, **`exit 0`** |
| 2) `otisk_vstupu.sha256` přepsán na `0000…` | `CHYBA: INVENTÁŘ JE ZASTARALÝ / NEZMĚŘENÝ`, **`exit 1`** |
| 3) návrat na původní bajty | **`exit 0`**, sha256 inventáře **`e3e988f86fef6b50`** = původní |

→ **Obě měřidla měří** a **úklid C2 je bajt na bajt** (ověřeno hashem, ne dojmem).

### 18.7 Úkol 1 zadání (změřit prompt a limity) — ZMĚŘENO, a je to horší, než se čekalo

Nástroj: **`python _analyza\p18-prompt-tokeny.py`** (nový). Měří **přesně to,
co jde do chatu** podle `agent.yml:224–235` (`--read CONVENTIONS.md`,
`--read` závislosti, `--file owns`, `--message prompt`). Aiderův vlastní
systémový prompt **změřit offline nelze** → je v součtu jako **označený odhad**
(6 500 znaků), ne jako měření.

| Granule | `--file owns` | `--read` závislosti | prompt | **CELKEM vstup** |
|---|---|---|---|---|
| `entity.player.api` | 2 291 znaků | 11 951 znaků (4 soubory) | 1 362 znaků | **33 623 znaků ≈ 11 207 tokenů** |
| `world.nodes` | 1 652 znaků | 11 602 znaků (6 souborů) | 1 805 znaků | **33 078 znaků ≈ 11 026 tokenů** |
| `sim.combat` | 5 119 znaků | 1 918 znaků (3 soubory) | 1 262 znaků | **26 318 znaků ≈ 8 772 tokenů** |

**Pevná část (tu platí každý běh):** `CONVENTIONS.md` **11 519 znaků ≈ 3 839
tokenů** + Aiderův systémový prompt (~2 166 tokenů, odhad).

**Srovnání s limity poskytovatelů:**

| Poskytovatel | Limit | Odkud to je | Vejde se 11 207 tokenů? |
|---|---|---|---|
| **groq** | **TPM 8 000** | **NAMĚŘENO** v logu #146 | **NE** |
| mistral | **?** | **v `providers.json` NENÍ** | **neví se** |
| cerebras | **?** | tamtéž | **neví se** |
| gemini | **?** | tamtéž (~20 dotazů/den) | **neví se** |
| openrouter | **?** | tamtéž (50 požadavků/den) | **neví se** |

> **⚠ NÁLEZ H10 — zadání tvrdí „porovnej s limity poskytovatelů v
> `providers.json`", a ty tam NEJSOU.** Naměřeno: `providers.json` obsahuje
> u poskytovatelů `name`, `baseUrl`, `keyEnv`, `anyPriority`, `models`,
> `strongModels` a **komentáře o denních stropech** — **žádné číslo TPM**.
> Jediné změřené TPM v celém projektu je **Groqovo** (z `litellm.RateLimitError`
> v logu běhu). **Důsledek:** u ostatních poskytovatelů se „vejde / nevejde"
> **tvrdit nedá** — a kdo to tvrdí, měří jinou veličinu (denní strop místo TPM).

**Odpověď na „proč se model jmenoval `openai/openai/gpt-oss-120b`":**
`agent.yml:227` skládá `--model "openai/${FORGE_MODEL}"`, a `FORGE_MODEL` sám je
`openai/gpt-oss-120b` → **dvojitý prefix**. Naměřeno v logu: Aider dostal
`Model: openai/openai/gpt-oss-120b with diff edit format` a varoval
`Unknown context window size and costs` + `Did you mean one of these?`. **Není to
příčina selhání #146**, ale znamená to, že **Aider si bere „sane defaults"** —
tedy měří jinak, než si systém myslí.

### 18.8 Hlavní nález §17.5 byl PŘEMĚŘEN a OBSTÁL (včetně čísla 14 398)

Běh #146 (vlastní měření, `node _analyza\h17-vsechny-behy.mjs` + stažený CELÝ
log `_analyza\p18-stahni-log.mjs` → `_analyza\p18-log-36999784822.txt`, 111 435 B):

```
#146   run_number=269  název "Forge #146 [a3c27581-…]"  head:194735d9b
       selhal-krok = "Agent nic nezměnil → hlásíme neúspěch"
       [test] 59 kontrol, 0 selhání        ← PŘESNĚ baseline origin/main
       TPM: Limit 8000, Requested 14398    ← 9× v logu
       model `openai/gpt-oss-120b` (Aider: openai/openai/gpt-oss-120b)
       Parse Error: Could not find type "Economy"
```

| Co §17.5 tvrdilo | Naměřeno teď | Verdikt |
|---|---|---|
| „59 kontrol, 0 selhání" v #146 | **`[test] 59 kontrol, 0 selhání`** | **OK** |
| „8× `litellm.RateLimitError`" | **9×** | **zpřesněno** (bylo 8) |
| „`TPM: Limit 8000, Requested 14398`" | **`Limit 8000, Requested 14398`** (v logu 9×) | **OK** |
| „z těch pěti běhů nevznikl ani jeden PR; otevřených PR 0 z 31" | **otevřených PR = 0**; poslední PR je **#31** (sloučen 08:02) | **OK** |
| „čtyři další běhy spadly na Kontrola parsování u 4 různých souborů" | **`world.gd`, `enemy.gd`, `crafting.gd`, `npc.gd`** | **OK** |

**A dvě věci, které §17.5 nevědělo:**

1. **Běhy #142–#146 jsou v GitHubu `run_number` #265–#269**, ne #142–#146.
   **`#146` v názvu běhu je ID ÚLOHY CONDUCTORA.** Je to **tatáž past, před
   kterou varuje `AGENTS.md`** („různé čítače nesou stejné jméno": „běh #355"
   vs. `run_number` #241). Kdo hledá „běh #146" v GitHub Actions, nenajde ho.
2. **`/failed` má pořád jedinou úlohu — #142 `entity.npc`, `attempts=5`** (tedy
   vyčerpané pokusy). #145 a #146 v `/failed` **nejsou**.

### 18.9 B1 v provozu — ověřeno ŽIVĚ a je to vidět na časové ose

`node _analyza\a3-kontrola.mjs` (12:39 UTC) a `node _analyza\p18c-stav-uloh.mjs`:

| Úloha | Stav | Pokusů | `updated_at` | Co z toho plyne |
|---|---|---|---|---|
| **#145** `world.nodes` | `ready` | **1** | **11:17:53** | první pokus **selhal**; guard ho drží |
| **#146** `entity.player.api` | `ready` | **1** | **11:15:54** | tamtéž |

→ **B1 funguje v praxi** (naměřeno jako **účinek**, ne odvozením): před B1 se
guard ptal na `updated_at`, do kterého se zapisuje i **vznik** granule — a obě
úlohy vznikly **08:28:54**, tedy „dávno". Po B1 se ptá na `naposledy_selhalo`,
které se poprvé vyplnilo **až skutečným selháním** (11:15/11:17). `RETRY_HOURS`
je 3 → další pokus **nejdřív ~14:15–14:17 UTC**. Do té doby je `ready` u nich
**správný stav**, ne porucha.

**Co se ověřit NEDALO:** že sloupec plní i cesta **`/report`** — jen čtením SQL
a `tsc` (§17.5 to samé). A **`/roadmap` sloupec `naposledy_selhalo` vůbec
nevrací** (naměřeno: klíč v odpovědi není) — takže „je prázdný" by se z něj
**nedalo** poznat; správný zdroj je `/queue` + `updated_at`.

### 18.10 Rozhodnutí o pozastavení #146 — NELZE, a je to doložené

Uživatel pozastavení schválil, akční session ho neprovedla a zapsala proč
(§16.7: conductor nemá endpoint). **Ověřeno nezávisle** — výčtem endpointů
z kódu (`index.ts:1489–1494`) i z živého rozcestníku:

```
endpoints: ["/health", "/tick", "/poll", "/queue", "/status", "/workers",
            "/games", "/game", "/heartbeat", "/claim", "/task", "/report", "/failed"]
```

→ **„pause"/„block task" mezi nimi NENÍ.** Zapsané alternativy jsou horší:
`/tasks/cleanup` maže **jen osiřelé** úlohy a #146 v roadmape **je**;
`/roadmap/reset` smaže cache **celé hry** a vynuluje `attempts` i u `entity.npc`
(#142, **5 pokusů**).

**ROZHODNUTÍ TÉHLE SESSION:** **bod se uzavírá jako NEPROVEDITELNÝ**, ne jako
opomenutý. **Důvod pozastavení navíc zanikl** — Úkol A ten test opravil a opravený
test projde i bez `move()` (naměřeno 64/0). **Co zůstává otevřené** je jen
případná **funkce** (`POST /task/state`), a ta je **návrh do kroniky §5**, ne
úkol akční session. **Nezakládat ji bez rozhodnutí uživatele.**

### 18.11 Co bylo v zadání NEPŘESNÉ (a je to nález, ne poznámka pod čarou)

| # | Co zadání tvrdilo | Naměřeno | Proč to je nález |
|---|---|---|---|
| **H8** | `g3-brany.py` má bránu „check-schema (hra)" | Volala `validate-all.mjs --jen hra` — a **`--jen` NENÍ přepínač** (v souboru **0 výskytů**, validátor **nečte `process.argv`**). Spustil se tedy **CELÝ validátor** a výsledek se vypsal pod jménem „check-schema (hra)" — **tatáž komanda jako „validate-all (CELEK)" o dva řádky níž** | **Dva řádky přehledu měřily totéž a ani jeden neměřil `check-schema`.** Kdo se podle přehledu rozhodoval, viděl dvě zelené tam, kde byla jedna. **OPRAVENO** — brána teď volá `python orchestra/repo/.forge/check-schema.py games/uo-shadows` (tak to dělá `validate-all.mjs:194`) |
| **H10** | „porovnej s limity poskytovatelů v `providers.json`" | V `providers.json` **žádné TPM není** — jen poznámky o denních stropech | Nešlo to splnit podle zadání; muselo se to změřit **z logu** (§18.7) |
| **H11** | „prompt granulе `entity.player.api` posílá agenta na `docs/ARCHITEKTURA.md`" (§2.4 a §17.8/H7) | **Neposílá.** Prompt (1 362 znaků) zmiňuje `CONVENTIONS.md` a `scripts/mining.gd`; `ARCHITEKTURA.md` se v něm **nevyskytuje** (`grep` → 0) | **H7 je v tomhle bodě nepřesný.** Co platí dál: **`ARCHITEKTURA.md` §2.1 je skutečně jen v pracovním stromě** (v `origin/main` → **0 výskytů**) a `roadmap.json:3` se na ten dokument **odvolává** jako na zdroj DAG. **Ale smlouvu pro `entity.player.api` nese PROMPT** (typy, kdo to volá, co zachovat) — a ten je v roadmapě, tedy i v repu. **Push tedy není blokátor smlouvy; je blokátor dokumentace, na kterou se roadmapa odvolává** |
| **H12** | „Úkol B je doložený mutací 2/2" je uzavřený | **M3 zůstává nechycená** (potvrzeno 18.4) — a je to **nález o bráně**, ne o kódu | Zůstává otevřené → granule `tests.harness` |

### 18.12 Co se ověřit NEDALO (přiznaná mez)

1. **Že `naposledy_selhalo` plní cesta `/report`** — jen čtením SQL a `tsc`.
   Spustit to znamená nechat úlohu reálně selhat a spálit pokus živé granulе.
2. **Jaký TPM mají mistral, cerebras, gemini a openrouter** — v repu to není
   a dohledávat to u poskytovatelů je změna zadání; proto jsou v tabulce `?`.
3. **Že Aiderův systémový prompt má ~6 500 znaků** — je to **odhad** a je tak
   označený. Skutečné číslo by dal jen běh Aideru.
4. **Budoucnost #145/#146** — rozhoduje conductor a čas (`RETRY_HOURS`).

### 18.13 Brány — co každá otevřela (past S27)

`python _analyza\g3-brany.py` na konci session: **29 bran, s nenulovým exit 1** —
a ten jeden je **`mutace A: pres-level`**, který **správně spadnout má**.

| Brána | Otevřela | Výsledek |
|---|---|---|
| testy hry (Godot) — **klon** | **64 kontrol** | 0 selhání |
| `h17-mutace-a.py` | **6 běhů** | `exit 0` — všech 6 dle očekávání |
| `h17-mutace-b.py` | **6 běhů** | `exit 1` — **jen M3 nechycena (nález H2)** |
| `h17-sonda-vetve.py` | 2 sondy + 2 běhy | `exit 0` — A 2×, B 9×, rozpor 13 vs. 33/1 |
| `h17-kontrola-klonu.py` | 5 souborů + 15 znaků | `exit 0` |
| `h17-over-c1.mjs` + podvrh | 2 adresy | `exit 0` — živý 0, podvrh **1** |
| `h17-over-c2.py` | **3 běhy** | `exit 0` — 0 → **1** → 0, úklid bajt na bajt |
| `p18-prompt-tokeny.py` | **4 granule** + 5 poskytovatelů | `exit 0` |
| `p18-sonda-tpm.py` + `p18-stahni-log.mjs` | log #146, **111 435 B** | `exit 0` |
| `p18b-jmena-behu.mjs` | 4 workflow + 20 běhů + 5 ID | `exit 0` |
| `p18c-stav-uloh.mjs` | 2 úlohy + `/failed` | `exit 0` |
| `kontrola-diakritiky.py` | **36 299 znaků** | `exit 0` |
| `g1-diakritika-novych.py` | **71 souborů** | `exit 0` |
| `handoff-kontrola-uplnost.py` | **83 klíčových bodů** | **83/83** |
| `kronika-kontrola.py` | 55 omylů | `exit 0` |
| `lint-roadmapa.py` | 21 granul | `exit 0` — **11× `[5]`, 13 z 21** |
| `check-schema.py` (nově správně nad hrou) | schéma hry | **`exit 0`** — „Schéma je v souladu" |
| `validate-all.mjs` | sekce A–L, **209× `OK`** | **`✓ VŠE V POŘÁDKU`, `exit 0`** |
| `ag-over-cisla.py` | 7 tvrzení | **5 + 2 historická, 0 rozchodů** |
| `tsc --noEmit` (conductor) | typová kontrola | `exit 0` |

> **⚠ A to nejzajímavější: tři brány, které byly vedené jako „neproběhlo
> (prostředí)", teď PROBĚHLY** — `test-check-schema.py` **17 kontrol, 0 chyb**,
> `vision.test.mjs` **36 kontrol, 0 chyb**, `baseline.py testy` **24 kontrol,
> 0 chyb** — a **`validate-all.mjs` je `✓ VŠE V POŘÁDKU`**.
> **Není to oprava** (kód se neměnil, sandbox se změnil na `danger-full-access`):
> je to **třetí stav** z `overovani` §7.13 v praxi — **brána, která neproběhla,
> není červená, je nezměřená** — a po změně prostředí se z nezměřené stala
> **zelená**. **Zapsáno proto, aby to nikdo nečetl jako „ty tři brány byly
> opraveny".**

### 18.14 Co tahle session změnila (a co ne)

**Změněno (4 soubory, všechny v workspace, žádný v repu):**

| Soubor | Změna |
|---|---|
| `AGENTS.md` | **nové pravidlo** o přegenerování inventáře (+ proč víckrát za session) |
| `PREDAVANI-SESSION.md` | **§6.2 D1** — totéž pravidlo pro akční session |
| `orchestra\tools\kontrola-diakritiky.py` | **+6 nových souborů** do seznamu (S27, po dvanácté) |
| `_analyza\g1-diakritika-novych.py` | **+6 nových souborů** |
| `_analyza\g3-brany.py` | **OPRAVA brány „check-schema (hra)"** (nález H8) |
| `HANDOFF.md` | §18 (tenhle oddíl) + §8g (vlastní omyly) — **jen přidáno, nic nesmazáno** |

**Necommitnuto, nepushnuto** — a to je záměr (`AGENTS.md`: nepushovat bez
vyžádání). **`_analyza\_inventar.json` přegenerován** (2 075 nálezů; otisk
vstupů se posunul, protože vstupem skeneru je i ta brána a každý skill).

**Pracovní stromy:** `_analyza\h17-kladna` a `_analyza\h17-klidna` **ODSTRANĚNY**
(`git worktree remove --force`, pak `worktree prune`) — `git worktree list` má
zpět jen hlavní strom, `a-ukol-scratch` a `merge-scratch`.
**⚠ Důsledek, který je potřeba říct nahlas:** `h17-mutace-a.py`,
`h17-mutace-b.py` a `h17-sonda-vetve.py` **nad odstraněným worktree nespadnou
srozumitelně — spadnou na `assert WT.is_dir()`**. Kdo je bude chtít zopakovat,
musí worktree **znovu založit**:
```powershell
& orchestra\tools\git.cmd -C games\uo-shadows worktree add --detach "$PWD\_analyza\h17-kladna" origin/main
Copy-Item games\uo-shadows\.godot _analyza\h17-kladna\.godot -Recurse -Force
```

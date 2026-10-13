# K3 — kontext nové hry se musí vejít do stropu poskytovatele

> **Co tenhle dokument JE:** **záznam o provedení + stav** session K3
> (12. 10. 2026). Vznikl jako **vlastní dokument** proto, že oddíl v `HANDOFF.md`
> patří session **P41** (ve stromě má 14 necommitnutých souborů) — `HANDOFF.md`
> jsem proto **NEEDITOVAL** ani jedním bajtem.
>
> **Co NENÍ:** stav projektu (to je `HANDOFF.md`) a kronika
> (`KRONIKA-PROJEKTU.md`). **Zadání:** `PREDANI-K3-NOVA-HRA.md`.
> **Předchozí krok:** `PREDANI-OTUKANI-2026-10-12.md` (K1+K2 — hotové, pushnuté,
> neopakoval jsem je).
>
> **Datum spotřeby:** všechno, co je tu o **stavu** (HEAD, tik, běhy, počty bran),
> se musí **živě přeměřit** — naměřeno v jednu chvíli 12. 10. 2026. Co je tu
> o **mechanismu** (jak se konvence rozdělily a jak se počítá rozpočet), platí,
> dokud platí kód v `repo/`.

---

## 1. Výstupy ze zadání §3 — stav

| # | Výstup | Stav | Doloženo |
|---|---|---|---|
| 1 | `CONVENTIONS.md` po krátkých sekcích | **HOTOVO** — 9 sekcí v `repo/CONVENTIONS/`, každá ≤ **761 t** (strop 1 200), `CONVENTIONS.md` je rozcestník (836 t) | `_analyza/k3-over-konvence-split.mjs` → **41 kontrol, 0 chyb**; mutace **14/14** |
| 2 | Mechanismus „posílá se jen deklarovaná sekce“ | **HOTOVO** — granule deklaruje `"konvence": [...]`, workflow z toho udělá `--read`, rozpočet to započítá | `repo/.forge/files-to-edit.mjs` (`--konvence`), `repo/.github/workflows/agent.yml`, `_analyza/k3-suchy-beh.mjs` **14/0** |
| 3 | Pilotní roadmapa 2–5 granulí, každá `REQUEST_FITS` | **HOTOVO** — `repo/.forge/roadmap.pilot.json`, 5 granul, **5× REQUEST_FITS** (5 443–5 667 t ze 8 000) | `node .forge/node/rozpocet-granuli.mjs --roadmap .forge/roadmap.pilot.json --poskytovatel groq --model openai/gpt-oss-120b` → `exit 0` |
| 4 | Pilotní běh v CI (end-to-end) | **NENÍ — BLOKOVÁNO** (viz §4) | tik je mrtvý, nové repo hry neexistuje, chybí skeleton i `FORGE_PAT` |
| 5 | Protizkouška: nafouknuté zadání → `REQUEST_TOO_LARGE` | **HOTOVO** — dvě různé vady, obě spadnou | P1 (všechny sekce + monolit 300 řádků) → **13 289 t → exit 1**; P2a (cesta k dokumentu, stav před K1) → **31 401 t → exit 1** |

**Co jsem záměrně NEDĚLAL:** nezaložil novou hru (čeká na jméno a scope od
uživatele, zadání §7.1/§7.2), nezvedl `GRAIN_MAX_RUNS` ani `MAX_ATTEMPTS`,
nezapsal ani bajt do `E:\Workspaces\uo-shadows` (jen čtení), necommitoval
soubory P41, nedal do žádného zadání cestu k souboru.

---

## 2. Naměřená zjištění (co se cestou našlo a v zadání NEBYLO)

Tohle je hodnota session větší než samotný výstup: **pět vad měřidel**, každá
doložená spuštěním.

### F1 — Testovací sada K1/K2 byla ČERVENÁ a `g3` ji vůbec nespouštěl

`node repo\.forge\node\priprava.test.mjs` → **31/32** (jedna kontrola červená),
a přitom v seznamu bran `_analyza\g3-brany.py` **nebyla ani jedna** z obou sad
(`priprava.test.mjs`, `probe-provider.test.mjs`). Klasická past projektu
„brána, která neproběhne, není brána“ — červený test nikdo neviděl.

**Příčina červené kontroly byla jiná, než vypadala:** kalibrační kontrola
(„16 000 znaků se při 3,03 znaku/token NEVEJDE“) vycházela jako *vejde se*.
Nebyl to vadný test — **chyběla veličina** (viz F2).

**Náprava:** obě sady jsou v `BRANY` (`priprava.test.mjs` **51/51** nově,
`probe-provider.test.mjs` **14/14**), kalibrační kontrola je posunutá do pásma,
kde se starý a nový odhad **rozejdou** (13 000 znaků), a k tomu sedm nových
kontrol cesty „deklarace → sekce → rozpočet“ + pozitivní důkaz, že brána
roadmapy měří i **velikost** souboru.

### F2 — Rozpočet podhodnocoval request: chyběl **obal zadání** (~2 000 t)

`REZIE_HARNESSU` (1 800 t) je **systémový prompt** aideru. Jenže aider posílá
i druhý kus, který v našem součtu nebyl: instrukce k diff formátu, seznam
souborů v chatu, JSON obálka requestu a escapování konců řádků.

**Naměřeno aiderem 0.86.2 proti falešnému poskytovateli** (`_analyza/k3-mer-requestu.mjs`):

| Běh | Co posílá | Reálný request | Model bez obalu | Neobjasněno |
|---|---|---|---|---|
| A | 2 deklarované sekce + prázdný soubor | 14 897 zn. ≈ **4 917 t** | 14 102 zn. | 795 zn. |
| B | celý dokument před K3 | 23 871 zn. ≈ **7 879 t** | 22 410 zn. | 1 461 zn. |
| D | monolit + registry + celý dokument | 41 974 zn. ≈ **13 853 t** | 39 550 zn. | 2 424 zn. |

**Náprava:** nová, samostatně pojmenovaná konstanta **`REZIE_CHATU = 2500`**
(NE přepsání `REZIE_HARNESSU` — jedno jméno nesmí znamenat dvě veličiny,
omyl #71). Po ní je model **konzervativní ve všech třech měřitelných bězích**:
A 5 506 ≥ 4 917, B 8 397 ≥ 7 879, D 14 034 ≥ 13 853.

**A tady je nejcennější důsledek:** starý tvar (celý `CONVENTIONS.md`) vychází
**8 397 t > 8 000** — tedy i **malá** granule by byla odmítnuta. Rozdělení
konvencí není kosmetická úspora, je to rozdíl mezi „projde“ a „neprojde“.

### F3 — Hygiena zadání SAMA NESTAČÍ (a to se dosud tvrdilo nepřímo)

Běh **D** je totéž zadání M0 po hygiene: request **13 853 t**, tedy **pořád
přes strop**. Hygiena ušetřila ~23 320 t (připnuté dokumenty — ověřeno
**obsahem** requestu, ne délkou: fragmenty z `docs/TDD.md` i `docs/ARCHITEKTURA.md`
se v requestu opravdu objevily), ale zbývají dvě věci: **soubor o 377 řádcích**
a **celý dokument konvencí**. K3 tedy muselo sáhnout na **tvar granule**
a na **velikost konvencí**, ne jen na zadání.

Zakázaný tvar granule je tím **změřený**, ne odvozený: „přepiš soubor o 300
řádcích“ se nevejde, i když je zadání hygienické a konvence deklarované.

### F4 — `kontrola-driftu.mjs --sync` by ZNIČIL konvence hry

Rozdělením `CONVENTIONS.md` vznikla past: brána driftu sama radí
„Spusť s `--sync` pro sjednocení (šablona → hra)“ — a to by u `uo-shadows`
**přepsalo celý dokument (3 893 t) rozcestníkem (836 t)**, tedy tichá ztráta
všech pouček. Náprava: dvě **pojmenované záměrné výjimky**, každá s důvodem
a s **měřenou podmínkou**:

* `CONVENTIONS.md` — patří HŘE (rozhodnutí uživatele **O6/P27**, 8. 10. 2026)
  a hra je zmrazená; směr je hra → šablona (`tools/sync-sablona-hra.py`),
* `.forge/files-to-edit.mjs` — výjimka platí, **jen dokud hra v `agent.yml`
  nemá `--konvence`** (jakmile K3 převezme, výjimka zmizí sama).

Výsledek driftu: **1 rozdíl** (`agent.yml`, známý stav) + **2 záměrné**
(vypsané i s důvodem). Před K3 byly rozdíly **2**, z toho jeden nikdo
neopravoval — číslo v `AGENTS.md` („známý rozdíl je jeden“) teď **odpovídá
měření**.

### F5 — `AGENTS.md` tvrdil 49 bran, naměřeno 55

Po registraci 6 nových bran se rozešlo číslo v **trvalých pravidlech**
(`ag-over-cisla.py`: „bran v registru: tvrdí 49, naměřeno 55“) → spadl
`validate-all`. Číslo v `AGENTS.md` je **měření, ne pravidlo** — přeměřil jsem
ho a zapsal i s důvodem (+6 bran, a proč). **Kdyby to uživatel chtěl jinak,
je to jedno číslo v `AGENTS.md`.**

### F6 — H79 hlásila vadu CIZÍHO balíčku (falešný poplach)

Brána na neplatné escape sekvence hlásila **4 nálezy** — a všechny čtyři byly
`pydub/utils.py` z **aiderského venv** v `.tmp/otukani/venv/Lib/site-packages/`,
který si 12. 10. 2026 postavila K1 pro měření režie. Skener skenoval 7 411
„živých“ souborů, z toho ~7 164 byl vendorovaný kód. `.tmp` je podle konvence
**lokální scratch** → přidán do `SKIP`. Ověřeno, že vyloučení **není slepé**:
pozitivní kontrola testu (`_h79-sonda-escape.py`) leží v `_analyza/`, tedy mimo
`.tmp` — kdyby vyloučení bylo široké, sonda by zmizela a test by zčervenal
(`test-h79-escape.py` → **18/0**, statická brána **0 nálezů** ze 247 živých souborů).

### F7 — Tik tiká, ale NEVYDÁVÁ („zelený systém není důkaz práce“)

`/health` v 19:15Z: tik mrtvý **252 min**. Ve 20:07Z: **tiká** (`last_cron` se
posouvá, `zdroj=cron`) — a přesto se za 2,5 minuty **fronta nehnula**
(`ready` 3 → 3, `running` 0 → 0, `selhani_v_rade` 20 → 20, poslední běh pořád
#366 z 9. 10.). Obnovu tiku jsem nezpůsobil (nenasazoval jsem nic).

**Poučení pro předání:** „tik tiká“ a „orchestra pracuje“ jsou **dvě různé
věci** — a rozdíl je vidět jen na **frontě**, ne na tepu. Kdo čte jen
`last_cron`, napíše „opraveno“.

---

## 3. Jak to funguje (a jak si to ověřit)

```
roadmapa (granule)                    workflow (agent.yml)              rozpočet
"konvence": ["01-typy",          →    files-to-edit --konvence     →    request-budget
             "06-soubor-granule"]      --read CONVENTIONS/01-typy.md      --konvence <seznam>
                                       --read CONVENTIONS/06-…md          → REQUEST_FITS / TOO_LARGE
```

**Tři věty, které to drží:**

1. **Co se má poslat, je vlastnost GRANULE** — ne odhad podle klíčových slov
   v zadání (odhad = věštění a věštění se nedá měřit).
2. **Deklarace je povinná** — `rozpocet-granuli.mjs` ji vynucuje (`exit 1`,
   když granule `konvence` nemá). Most pro staré hry: `files-to-edit --konvence`
   pošle **vše**, co je k dispozici, a **nahlas to řekne** — tichý přechod na
   „žádné konvence“ by byl horší (model by dostal zadání bez pouček).
3. **Rozpočet vidí TOTÉŽ, co aider** — `--konvence "$KONVENCE"` je v obou
   voláních `request-budget.mjs` (první pokus i rotace poskytovatele). Do K3
   tam `--konvence` nebylo vůbec, i když aider `--read CONVENTIONS.md` dostával:
   brána byla slepá přesně v tom, co rozhoduje.

**Ověření (dvě minuty, bez sítě a bez klíče):**

```powershell
cd E:\Workspaces\forge-orchestra
node _analyza\k3-over-konvence-split.mjs        # 41 kontrol: nic se neztratilo, sekce <= 1 200 t
node _analyza\k3-suchy-beh.mjs                  # 14 kontrol: suchý běh workflow + 2 protizkoušky
cd repo
node .forge\node\rozpocet-granuli.mjs --roadmap .forge\roadmap.pilot.json --poskytovatel groq --model openai/gpt-oss-120b
node .forge\node\rozpocet-granuli.mjs --seznam-sekci   # velikosti sekcí (neopisují se do dokumentů)
```

**Reálné měření aiderem** (potřebuje `.tmp\otukani\venv` z K1 — je to
**měřidlo, ne brána**, proto v `g3` není):
`node _analyza\k3-mer-requestu.mjs` → 4 běhy, 10 kontrol, 0 chyb.

> **Doklady obou měření jsou v `.tmp/`** (`k3-suchy/vysledek.json`,
> `k3-mer/mer-requestu.json`) — a `.tmp/` je **gitignorovaný**, takže se
> necommitnou. Kdo je chce, **spustí nástroje** (jsou v repu a oba si scratch
> vyrobí samy). Je to stejný režim jako u dokladů K1 v `.tmp/otukani/`.


---

## 4. Co NENÍ hotové: výstup 4 (pilot v CI)

**Pilot se NEDAL spustit — a stav se přitom v průběhu session ZMĚNIL.** Proto
jsou tu **dvě měření** téhož:

| Blokátor | Naměřeno | Kdo to vlastní |
|---|---|---|
| **Tik conductora** | ~~19:15Z: `last_cron` 15:04:00Z = **mrtvý 252 min**~~ → **20:07Z: ŽIVÝ** — dva vzorky 75 s od sebe: `last_cron` 20:06:29Z → **20:07:29Z**, `zdroj=cron`, `min=1`, `ok=true` | **P41** (H197/H201); korelace s deployem #42 je v `PREDANI-K3-NOVA-HRA.md` §6 — **vyřešeno v průběhu K3** (ne mnou: nenasazoval jsem) |
| **Nové repo hry neexistuje** | uživatel nerozhodl jméno ani scope (zadání §7.1); `HEAD` orchestry = `origin/main` = `8495d8a` | **uživatel** |
| **Šablona neumí vyrobit běžící hru** | `git ls-files repo` = **31 souborů**: jen `.forge/`, `.github/`, `.gitattributes`, `CONVENTIONS.md` — **žádný `project.godot`, `main.tscn`, `tests/`, `scripts/`, `assets/spec.json`**. Workflow přitom pouští `res://tests/run_tests.gd` a importuje assety → bez skeletonu **každý běh spadne na „testy hry“** | **uživatel** (§7.2: založení hry + oprava `install-into-repo.ps1`, který počítá s neexistujícím `projects\<název>` a `forge new`) |
| **Chybí `FORGE_PAT`** | fine-grained token (Contents RW + PR RW, ≥ 90 dní) pro repo nové hry | **uživatel** |

**⚠ Důsledek oživeného tiku — a JE TO TŘETÍ STAV, ne „opraveno“:** tik sice
tiká, ale **práce nevzniká**. Naměřeno dvěma vzorky 2,5 minuty od sebe
(20:08:53Z → 20:11:24Z, `last_cron` se posunul 20:08:28Z → 20:10:28Z):

| Veličina | T0 | T1 |
|---|---|---|
| `last_cron` | 20:08:28Z | 20:10:28Z (**tiká**) |
| `ready` | 3 | **3** (nezměněno) |
| `running` | 0 | **0** |
| `selhani_v_rade` | 20 | **20** |
| poslední běh | #366, `failure`, 9. 10. 19:42Z | **totéž** (žádný nový) |

**Tik tiká, ale conductor úlohy NEVYDÁVÁ.** To je třetí stav vedle „mrtvý tik“
a „vydává“ — a přesně ta past, kterou má projekt pojmenovanou:
*„zelený řídicí systém není důkaz, že práce probíhá“*. Mezi 19:15Z a 20:07Z se
tik obnovil (nenasazoval jsem nic), ale fronta stojí dál.

Proč se nevydává, jsem **neměřil** — `/queue`, `/status` i `/failed` vracejí
`401 bad secret` a já s tajemstvím conductora nepracuji. **Hypotéza
(NEOVĚŘENO):** v `/health` je u cíle `forge.ok: false` a `selhani_v_rade: 20`,
takže conductor může čekat na lidský zásah nebo na rotaci. **Tohle patří P41** —
je to její doména a bez secretu to nemám jak rozhodnout.

**Důsledek pro K3:** tři staré `ready` úlohy (#244–#246) na `uo-shadows` se
zatím **nevydaly** (fronta se nehnula). Kdyby se vydaly, hra má **starý
workflow** (celý `CONVENTIONS.md`, rozpočet bez obalu zadání) a její request je
**naměřeno 7 879 t reálně / 8 397 t modelem** → **nad stropem 8 000**, takže by
selhaly na velikosti. Kdo je vlastní, ať je zruší, nebo hře nasadí K3.


**Co místo pilotu je:** `_analyza/k3-suchy-beh.mjs` pouští **přesně ty příkazy,
které pouští `agent.yml`**, v kopii šablony (`.tmp/k3-suchy/`, klíče se
nekopírují) — plus dvě protizkoušky. *Nenahrazuje* běh v CI; nahrazuje jen
„změřit ticho“.

**Poznámka k pořadí:** pilot má smysl **až po založení hry se skeletonem** —
jinak conductor úlohu vydá a spadne to na chybějících testech hry, což vypadá
jako vada granule, ale je to chybějící základ. Tik už není blokátor.


---

## 5. Brány: co bylo spuštěno a co vyšlo

**Pořadí (a proč):** `inventář → g3 → inventář → validate-all`. Mezi krok 2 a 3
se **nesmí nic vložit**: `g3` spouští brány, které do `_analyza/` **zapisují**,
a tím inventář zestarají (nález **H176** — „zastaralý inventář“ se **přegeneruje**,
nede klaruje se jako výjimka).

`python _analyza\g3-brany.py` (s `FORGE_REGISTR` mimo repo) → **55 bran,
0 bran, které vůbec nezačaly**, nenulových exitů **5** (z toho **1 deklarovaný**).
**Nové a nově registrované brány — všechny zelené:**

| Brána | Výsledek |
|---|---|
| `K3: konvence rozdělené na sekce` | **41 / 0** |
| `K3: mutace rozdělení konvencí (4 vraty)` | **14 / 14** |
| `K3: suchý běh workflow + protizkouška` | **14 / 0** |
| `K3: mutace rozpočtu a deklarací (5 vrat)` | **17 / 17** |
| `K1/K2/K3: nástroje přípravy` (nově v seznamu) | **51 / 51** |
| `otukání: měření stropu poskytovatele` (nově v seznamu) | **14 / 14** |

**Zbylé červené brány — u každé je doložená příčina a NENÍ to regrese K3:**

| Brána | Stav | Příčina (doložená) |
|---|---|---|
| `mutace B (combat)` | exit 2 | **brána HRY**: její zdravý kód hlásí `92 kontrol, 1 selhání`, takže mutace nemá co dokazovat. Vlastní ji session hry. |
| `B3b: strop na granuli` + `B3b: mutace brány` | exit 1 | **necommitnutá práce P41** v `conductor/src/index.ts` (`+12/−1`): brána čeká „týž map se předává do `roadmapTick`“ a dostává `False`. Na ten soubor nesahám. |
| `zadání kontrola` | exit 1 | **deklarovaný** nenulový exit (hlavička zadání se píše až po posledním commitu). |
| `validate-all (CELEK)` | exit 1 | **3 problémy, všechny o `conductor/src/index.ts`** („lokální kód = repo“ 113 572 vs 113 013 B + dvě B3b) → totéž jako výš, práce P41. Po `ag-over-cisla` je **zelená**: „čísla v AGENTS.md odpovídají zdroji“. |

**Opravené brány (byly červené kvůli K1, ne kvůli obsahu projektu):**

* `H79 statická` → **0 nálezů** ze 247 živých souborů a `H79 mutace` → **18/0**
  (dřív 4 nálezy z cizího `pydub` balíčku — viz F6),
* `n1-over-inventar` a `C2: mutace N1` → zelené po přegenerování inventáře
  (správné chování, H126),
* **`priprava.test.mjs` a `probe-provider.test.mjs` se konečně měří** (51/51,
  14/14) — do K3 nebyly v `g3` vůbec (F1).

**Další brány (samostatně):** `kontrola-diakritiky.py` **313/357, 0 chyb** ·
`over-dokumentaci.py` **64/0** · `over-skilly.py` **15 skillů, 96 zmínek,
0 mrtvých** · `g1-diakritika-novych.py` **882 souborů, 0 vad** ·
`kronika-kontrola.py` **SEDÍ** · `handoff-kontrola-uplnost.py` **83/83**
(`HANDOFF.md` jsem needitoval) · `hl-rizika-jazyka.py` **SEZNAM SEDÍ** ·
`kontrola-driftu.mjs` **1 rozdíl + 2 záměrné** (exit 1 = známý stav `agent.yml`).

**Co jsem v bránách změnil:** `_analyza/g3-brany.py` (+6 registrací s komentářem
proč), `tools/kontrola-driftu.mjs` (záměrné výjimky; `--sync` je přeskočí),
`_analyza/h79-escape-sken.py` (`.tmp` do `SKIP`), `AGENTS.md` (**přeměřené
číslo** 49 → 55, viz F5). Tři jsou měřidla, jedno je měření v trvalých
pravidlech.

> ⚠ **Zásah do cizího stromu, který patří do předání P41:** `g3` spouští brány,
> které zapisují `_analyza/ov-*.json` — a tím se přepsaly i soubory, které měla
> P41 **necommitnuté** (`ov-b2-spusteni.json`, `ov-c-vysledky.json`,
> `ov-e-vysledky.json`; naměřeno: mtime 21:47–21:49, rozdíly symetrické 11/11,
> obsah je generovaný). `ov-d-vysledky.json` jsem **vrátil na `HEAD`**, protože
> ten P41 nezměnila a zmodifikoval ho až můj běh `g3`. Je to vlastnost `g3`
> (nález **H138**), ne moje volba — a je to přesně to, co řeší
> `SOUBEH-SESSION-NALEZY.md`.


---

## 6. Co čeká na tebe (rozhoduje uživatel, ne agent)

1. **Jméno a scope nové hry** (zadání §7.1). Scope je páka: čím menší hra, tím
   jistěji se granule vejdou pod 8 000 t. Pilot je navržený na **5 granulí /
   5 souborů** (mapa → hráč → mince → HUD → scéna).
2. **Založit novou hru + opravit `install-into-repo.ps1`** (§7.2). Dnes je
   skript **zastaralý** (počítá s `projects\<název>` a `forge new`, což v layoutu
   na `E:` neexistuje) a **šablona nemá skeleton** (viz §4) — bez obojího pilot
   v CI spadne na „testy hry“, i kdyby tik běžel.
3. **Zdroj pro novou hru: Groq (zdarma, 8 000 TPM, bez karty), nebo nejdřív
   změřit strop Mistralu/Cerebrasu?** Klíče máš jen ty; měření je
   `node .forge\node\probe-provider.mjs --jen <poskytovatel> --stdout` (5 minut)
   a s větším stropem se rozpočet uvolní. **Gate K3 je postavený na Groqu** —
   s větším stropem projde totéž, ale s rezervou.
4. **Číslo v `AGENTS.md`: 55 bran** (F5) — potvrdit, nebo vrátit.
5. **`PILOT` vs `roadmap.json`:** ukázka je v `repo/.forge/roadmap.pilot.json`;
   až hra vznikne, zkopíruje se na `roadmap.json` a přepíše obsahem hry
   (jinak by v repu ležely dva plány — vada S4/S5).
6. **Vědomé rozhodnutí k `--sync`:** drift hlásí **1 rozdíl** (`agent.yml`
   šablona vs. hra). Do hry **nezapisuji** (je zmrazená); kdo ji odemkne,
   rozhodne, jestli si vezme i nový workflow s `--konvence`.

---

## 7. Prompt pro další session (ke zkopírování)

> **Pozn.:** `NEXT-SESSION-INSTRUKCE.md` je **P41** — tenhle prompt patří sem,
> ne do něj.

```text
Jsi session K4. Repo orchestra = E:\Workspaces\forge-orchestra.
Hra uo-shadows = E:\Workspaces\uo-shadows je ZMRAZENÁ — jen čti, nepiš do ní.
Ve stromě může být necommitnutá práce P41 — nesahej na ni.

Kontext: K3 (12. 10. 2026) rozdělila CONVENTIONS.md na sekce, zavedla deklaraci
"konvence" v granulích a přidala bránu na rozpočet celé roadmapy. Záznam,
naměřená čísla i prompt, který čteš, jsou v K3-ROZDELENI-KONVENCI.md — přečti ho
CELÉ (zejména §4 „Co NENÍ hotové“ a §6 „Co čeká na tebe“).

NEJDŘÍV (v tomto pořadí, každé měř, nečti z dokumentu):
1) git rev-parse HEAD + git rev-list --count origin/main..HEAD
2) /health conductora: https://forge-conductor.ssevcikm.workers.dev/health
   → last_cron starší než 10 min = TIK JE MRTVÝ a orchestra nevydá ani úlohu.
   ⚠ Ve K3 se stav ZMĚNIL uprostřed session: v 19:15Z byl mrtvý 252 min,
   ve 20:07Z ŽIVÝ (dva vzorky 75 s od sebe se posunuly). Ověř to DVĚMA vzorky,
   ne jedním čtením — a všimni si `ready`: byly tam 3 staré úlohy na uo-shadows
   se STARÝM workflow (request 7 879 t reálně / 8 397 t modelem > 8 000),
   takže se `selhani_v_rade` může znovu naplnit. (Tik vlastní P41.)
3) git status --porcelain → kolik necommitnutých souborů má P41.

PAK podle stavu:
A) Tik běží A existuje repo nové hry se skeletonem → spusť PILOTNÍ GRANULI
   end-to-end (roadmap.pilot.json → roadmap.json, registrace hry v conductoru)
   a ověř: request <= 7 000 t naměřeno poskytovatelem, v /status je POJMENOVANÁ
   příčina, PR vznikne (nebo se pojmenuje, proč ne).
B) Tik běží, ale hra/skeleton nejsou → to je práce pro uživatele (§7.2 zadání):
   navrhni `forge-*.mjs` pro založení hry (opakovatelné a ověřené testem),
   ale NEZAKLÁDEJ ji bez rozhodnutí o jménu a scope.
C) Tik je mrtvý → nezkoušej dispatchovat; ověř, že brány K3 jsou zelené
   (node _analyza\k3-over-konvence-split.mjs, k3-suchy-beh.mjs, priprava.test.mjs)
   a připrav, co půjde udělat okamžitě po obnovení tiku.

BRÁNY na konci (v tomto pořadí, nic mezi tím):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\g3-brany.py                     # POZOR: FORGE_REGISTR mimo repo, pokud stavíš harness
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
node tools\validate-all.mjs
python tools\kontrola-diakritiky.py ; python tools\over-dokumentaci.py ; python tools\over-skilly.py
node tools\kontrola-driftu.mjs                  # očekávej 1 rozdíl + 2 záměrné (viz F4)

NEDĚLEJ: nezvedej GRAIN_MAX_RUNS/MAX_ATTEMPTS, necommituj soubory P41,
nespouštěj kontrola-driftu.mjs --sync (hra je zmrazená), nedávej do zadání granulí
cesty k souborům (přitáhne celý dokument — naměřeno 14 097 t vs strop 8 000).
```

---

## 8. Co je hotové na disku a NENÍ commitnuté (a proč)

**Nezakládal jsem commit ani push** — projektové pravidlo zní „nepushovat bez
vyžádání“ a **ve stromě je 15 necommitnutých souborů P41**. `git add -A` by je
smíchalo do jednoho commitu, a to je přesně to, před čím mě zadání varovalo.

**Moje soubory (kandidát na commit) — 20 položek (19 souborů + složka
`repo/CONVENTIONS/` s 9 sekcemi):**

```
AGENTS.md                                     (jen přeměřené číslo 49 -> 55)
_analyza/_registr-bran.json                   (generovaný g3: 55 bran)
_analyza/g3-brany.py                          (+6 registrací)
_analyza/h79-escape-sken.py                   (.tmp do SKIP)
_analyza/k3-mer-requestu.mjs                  (nový)
_analyza/k3-mutace-konvence-split.py          (nový)
_analyza/k3-mutace-rozpoctu.py                (nový)
_analyza/k3-over-konvence-split.mjs           (nový)
_analyza/k3-suchy-beh.mjs                     (nový)
K3-ROZDELENI-KONVENCI.md                      (nový)
repo/CONVENTIONS.md                           (rozcestník)
repo/CONVENTIONS/                             (9 nových sekcí)
repo/.forge/files-to-edit.mjs                 (--konvence)
repo/.forge/node/priprava.test.mjs            (51/51)
repo/.forge/node/request-budget.mjs           (obal zadání + navic_t)
repo/.forge/node/rozpocet-granuli.mjs         (nový)
repo/.forge/roadmap.json                      (formát + ukázka)
repo/.forge/roadmap.pilot.json                (nový)
repo/.github/workflows/agent.yml              (deklarované sekce)
tools/kontrola-driftu.mjs                     (záměrné výjimky)
```

**Patří P41 (NEcommitovat s mými):** `.gitignore`, `NEXT-SESSION-INSTRUKCE.md`,
`_analyza/b3b-mutace.py`, `_analyza/ov-b2-spusteni.json`, `_analyza/ov-c-vysledky.json`,
`_analyza/ov-e-vysledky.json`, `_analyza/p41-*.{mjs,py,json,txt}`,
`_analyza/p36-g3-registr.json`, `conductor/src/index.ts`.

```powershell
# commit JEN mých souborů (nevypisovat `git add -A`):
cd E:\Workspaces\forge-orchestra
git add AGENTS.md _analyza/_registr-bran.json _analyza/g3-brany.py `
  _analyza/h79-escape-sken.py _analyza/k3-*.mjs _analyza/k3-*.py `
  K3-ROZDELENI-KONVENCI.md repo/CONVENTIONS.md repo/CONVENTIONS `
  repo/.forge/files-to-edit.mjs repo/.forge/node/priprava.test.mjs `
  repo/.forge/node/request-budget.mjs repo/.forge/node/rozpocet-granuli.mjs `
  repo/.forge/roadmap.json repo/.forge/roadmap.pilot.json `
  repo/.github/workflows/agent.yml tools/kontrola-driftu.mjs
git status --short          # zkontroluj, že P41 soubory zůstaly M/?? a nejsou ve stage
git commit -m "K3: konvence po sekcich, deklarace v granuli, rozpocet cele roadmapy"
```

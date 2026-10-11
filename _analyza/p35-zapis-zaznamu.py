# -*- coding: utf-8 -*-
r"""P35 — ZÁPIS ZÁZNAMŮ: `HANDOFF.md` §66 + `KRONIKA-PROJEKTU.md` řádek 50 a §2.28.

PROČ SKRIPTEM: `KRONIKA-PROJEKTU.md` je tabulka s **pěti svislítky** (ne sedmi
jako záhlaví) a ruční vkládání dlouhého řádku do ní opakovaně rozbilo čítače
(`kronika-kontrola.py`). Skript navíc:
  * je **IDEMPOTENTNÍ** (když §66 / řádek 50 / §2.28 už jsou, nic nepřidá),
  * **NEPŘEPISUJE** nic, co tam bylo (záznam se jen doplňuje),
  * po zápisu spustí `kronika-kontrola.py` i `handoff-kontrola-uplnost.py`
    a **selže**, když kontrola nesedí.

Použití: python _analyza\p35-zapis-zaznamu.py [--jen HANDOFF|KRONIKA]
"""

import argparse
import json
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
ENV = dict(__import__("os").environ, PYTHONIOENCODING="utf-8")

kontrol = 0
chyb = []


def zk(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def spust(cmd, timeout=600):
    r = subprocess.run([str(a) for a in cmd], cwd=str(WS), env=ENV,
                       capture_output=True, timeout=timeout)
    return r.returncode, ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")


# ── §66 do HANDOFF.md ───────────────────────────────────────────────────────
SEKCE_66 = r"""

## 66. P35 — NASAZENÍ P34 OVĚŘENO A TIK ZLEVNĚN (H165) (11. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P35 + stav po P35**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**50**, nálezy **§2.28**), plán (`PLAN-DALSI-KROK.md`). Zadání P35 je v
`NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **11. 10. 2026 09:27 – 12:2x UTC** (živý čas
> z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba) platí
> k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.28), aby každý nález byl dohledatelný
> z HANDOFF.md — ZÁMĚRNĚ JAKO PRÓZA, ne tabulkou** (tabulkový řádek `| **Hxx** |`
> by zvedl počítadlo „řádků Hxx“ a shodil `ov-g` i měřidla P28):
> **H165** = **tik platil 3,66 ms za přepis base64 „po znacích“** (funkce na
> každý znak v `Uint8Array.from(atob(…), (c) => c.charCodeAt(0))`), což je
> 3,66 z 4,06 ms celého čtení roadmapy — a tik se pouští každou minutu;
> indexovaný cyklus stojí **0,10 ms** a je **bajtově ekvivalentní** · **H166** =
> **VLASTNÍ OMYL P35: spuštění CIZÍHO měřidla bez přesměrování výstupu přepíše
> jeho doklady** (`p34-a-overeni-levny-vystup.txt`, `p34-health-vystup.txt` —
> gitignorované, tedy NEVRATNÉ), a **seam `P34_HEALTH` na neexistující soubor
> vyrobí falešně červené měřidlo** (47/1), zatímco **týž seam jednu kontrolu
> VYNECHÁ** (čítač 50/0 se pak falešně shoduje s tvrzením §65) · **H167** =
> **ŽIVÝ CPU PROFIL SLUŽBY**: cron `cpuTime` **24–36 ms** (medián 26,5; n=12)
> před zlevněním a **18–29 ms** (medián 20; n=4) po něm, `/tick` 15–25 ms,
> `/health` 2–7 ms, `/poll` **0 ms** — a **všechny cron eventy končí
> `outcome=ok`**, takže dokumentovaných **10 ms NENÍ tvrdý limit** (H164 se tím
> **dořešuje měřením**, ne převzetím) · **H168** = **MĚŘIDLA P34 ZESTÁRLA, A NENÍ
> TO VADA JEJICH PRÁCE**: `p34-a-overeni.py --plne` dnes **93/5** (P34 tvrdí
> 96/0) a `p34-mutace.py` **23/4** (P34 tvrdí 23/0) — protože (a) si tvrzení
> čtou z `NEXT-SESSION-INSTRUKCE.md`, které **P34 ve svém závěru sama přepsala**
> (jiné formulace), a (b) fixture mají **absolutní časy** (`04:59:30Z`), které
> po hodinách přestanou být „zdravé“.

### 66.1 Úkol A — NASAZENÍ P34 JE ŽIVÉ (tři kroky) A `/health` POSÍLÁ POKUS

**Tři kroky (HTTP 200 není důkaz), vše s PLNÝM sha:**
1. **KROK 1** — `deploy.yml` **#38 na `f983dace0f9f0750398b5a5ac17441f7c3f1352f`**
   → `completed/success` (2026-10-11T07:46:35Z). Commit se **nehledal
   v dokumentu**, ale v gitu (`git log` podle předmětu `P34: H156`).
2. **KROK 2** — verze z **LOGU nasazení**: `Current Version ID:
   e0a939e6-e459-4124-90d1-ee4b8bf727d3`.
3. **KROK 3 (křížová kontrola)** — **tatáž verze** je v `scriptVersion.id`
   **ŽIVÉHO** `wrangler tail` (47 eventů, doklad `_analyza/p35-tail-raw-vystup.txt`).

**`/health` posílá POKUS:** `last_cron_pokus` + `last_cron_pokus_min` (živá pole
P34) **a `last_cron` nezmizel** (význam „tik DOBĚHL“ se nemění). Živý stav při
měření: `last_cron = 2026-10-11T09:35:24.773Z` (0 min), `last_cron_pokus`
o 2 s dřív, `ready = 3`, `running = 0` — **tik DOBÍHÁ**.

**Brána umí spadnout i projít (A3):** `tools/test-cron-pokus.mjs` → **9/0** a
**tři vady v KOPIÍCH** (bajt na bajt shodných s živými): (a) predikát bez větve
„tik NEDOBÍHÁ“ → brána spadne **právě na fixtuře 1**; (b) predikát bez větve
„pokus v BUDOUCNOSTI“ → spadne **právě na fixtuře 4**; (c) **SLABÁ KONTROLA**
(fixtura 4 se ptá jen `ok === false`) nad **toutéž vadou (b) PROJDE** (exit 0),
kdežto silná spadne (exit 1) — **H158 je tím potvrzené jako měřený jev**, ne
jako tvrzení.

**Čísla z §65 NESEDÍ VE DVOU BODECH — a oba rozdíly jsou POJMENOVANÉ:**
* **levný běh: 51/0 vs. tvrzených 50/0.** Rozdíl je **po sekcích** (doklad P34
  → dnes): `A0 13→13 · A1 22→22 · A2 8→5 · A5 2→2 · A8 3→4 · B1 5→5`. **A8**
  měla v P34 **3× OK + 2× NÁLEZ** (tep byl červený — výpadek), dnes **4× OK +
  0× NÁLEZ** (predikát je OK) — tedy **+1 kontrol přesně tam, kde se změnil stav
  služby** (H164). `A2` je jiná jen proto, že v P34 **plném** dokladu běžela A2
  v drahém režimu (8 OK) a tady levně (5 OK + 1 NEZMĚŘENO). **A0/A1/A5/B1 se
  nezměnily.**
* **plný běh: 88/12 vs. tvrzených 96/0** (a **druhý běh téhož měřidla dal
  93/5** — počet chyb měřidla P34 **NENÍ stabilní**, protože čte tvrzení
  z přepisovaného dokumentu a pouští živé brány). Většina chyb je
  `TVRZENÍ NENALEZENO` v bloku „OSTATNÍ BRÁNY PŘI ZÁPISU“, protože ta čísla si
  měřidlo P34 čte z **`NEXT-SESSION-INSTRUKCE.md`** — a to P34 **ve svém závěru
  sama přepsala** pro P35 (jiné formulace: `1 NEDEKLAROVANÝ` místo
  `0 NEDEKLAROVANÝCH`, `2 problémy` místo `0 problémů`, `p29-a A1M13` bez
  `--jen`, `p28-b-mutace` v novém zadání není). **Práce P34 je v pořádku;
  zestárlo měřidlo** (H168). Stejná příčina shodí i precondition
  `p34-mutace.py`, jehož **druhá** polovina chyb je z fixture s **absolutním
  časem** (`04:59:30Z`) — dnes **23/4** místo **23/0**.

### 66.2 Úkol B — ZLEVNĚNÍ TIKU (H165): MĚŘENÍ → OPRAVA → NASAZENÍ → DOPAD

**Vybráno: ZLEVNIT TIK** (z pěti nabídek §2.2) — a měřilo se **DŘÍV**, než se
hledalo tvrzení (H155):

1. **ŽIVÝ CPU PROFIL** (`_analyza/p35-profil-cpu.mjs` + `p35-tail-rozbor.py`,
   47 invokací): `cron` **24–36 ms** (medián 26,5; n=12, `outcome=ok`, **0×
   `exceededCpu`**), `POST /tick` 15/19/25 ms, `GET /health` 2–7 ms,
   `POST /poll` **0 ms**. Cloudflare Analytics za 24 h: `success` **2957**,
   `exceededResources` **1054** v **21 oknech** — ale hodiny **`08Z` i `09Z`
   hlásí 0** (výpadek skončil nasazením #38).
2. **ROZKLAD GITHUB ČÁSTI TIKU** (`p35-rozklad-tiku.mjs`, živá data): tik tahá
   **665 441 B (650 kB) každou minutu** ve třech voláních a jejich `JSON.parse`
   stojí **7,93 ms** = **42 % naměřeného CPU tiku**.
3. **ROZKLAD ČTENÍ ROADMAPY** (`p35-rozklad-roadmapy.mjs`, medián z 21 běhů):
   celkem **4,06 ms**, z toho `JSON.parse` obálky 0,07 ms, `atob` 0,02 ms,
   **`Uint8Array.from(atob(…), mapFn)` 3,66 ms** ← vina, `TextDecoder` 0,12 ms,
   `JSON.parse` roadmapy 0,19 ms. **Indexovaný cyklus: 0,10 ms** (úspora
   3,56 ms); cesta přes `Accept: …raw` by ušetřila 3,98 ms.

**OPRAVA (`conductor/src/index.ts`):** `Uint8Array.from(atob(…), (c) =>
c.charCodeAt(0))` nahrazen **indexovaným cyklem** (`bin.charCodeAt(i)`).
Chování se **nemění**, jen cena — dekódování je **bajtově ekvivalentní**.

**TEST, KTERÝ OPRAVU ZAVOLÁ (`tools/test-tick-offline.mjs`, nový scénář AF):**
podstrčí roadmapu hry s **vícebajtovou češtinou** (`grain.žluťoučký` /
`Příliš žluťoučký kůň`, base64 → bajty → UTF-8) a tvrdí **CELÝ obsah ve vázaných
hodnotách** `INSERT INTO roadmap`/`INSERT INTO tasks` — zkrácený nebo rozbitý
dekodér to shodí. Stav: **215/0 → 218/0**.

**NASAZENÍ A DOPAD:** commit **`3143f31d6a37ed8d90bf06f5c03df9a407ae00ea`**,
`deploy.yml` **#39 na tom commitu** → `completed/success` (09:42:11Z), verze
z logu **`3985379c-4f45-424c-8400-2e26b54cae23`** == `scriptVersion.id` živého
tailu (doklad `_analyza/p35-tail-po-vystup.txt`). **cron `cpuTime` před/po:**
medián **26,5 → 20 ms** (n=12 → n=4; rozsahy 24–36 → 18–29). **Počet vzorků po
nasazení je malý (4)** — je to **naměřený posun, ne důkaz o jediné změně**.

**PRÁCE SE STEJNĚ NEVYDÁVÁ** — a **není to CPU**: tik hlásí `spusteno: 0 úloh`
a `přeskočeno: #244 … STROP GRANULE 8/8 (uo-shadows/engine.input); #245 …
(world.bodies); #246 …` při `ready = 3`, `running = 0`. Je to **záměrná brzda**
(`GRAIN_MAX_RUNS = 8`).

### 66.3 Co zůstalo OTEVŘENÉ (a co se NEMĚŘILO)

* **PRÁCE SE NEVYDÁVÁ kvůli STROPU GRANULE 8/8** — **rozhodnutí uživatele**
  (zvednout strop, nebo granule opravit). **Není to už CPU.**
* **Rozhodnutí o PLÁNU:** tik chce **18–36 ms CPU**, dokumentace uvádí **10 ms**
  pro cron na free plánu — a **přesto tiky dobíhají** a Analytics hlásí od
  nasazení #38 **0 `exceededResources`** (H167). **Free plán tedy dnes stačí**;
  další zlevňování (zbývá hlavně **GitHub část = 42 % CPU**) by znamenalo
  **odkládat čtení PR/roadmapy** (detekce sloučení by se zpozdila o minuty) —
  to je **rozhodnutí, ne technický detail**, a P35 ho **nedělá**.
* **H133** (`p28-a-overeni.py` A6 čeká `g3 → exit 0`) — **nezměněno**.
* **Dávka dokladů (`p20-d-doklady.py`) NEDOBĚHLA ani v P35** (už v P33 a P34).
* **`fakeDb` v `tools/test-tick-offline.mjs` nezná SQL tabulky `state`** —
  naměřeno znovu (218/0, ale v logu je `tep (manual) selhal: … neznámý dotaz →
  CREATE TABLE IF NOT EXISTS state …`). Je to **slepé místo**: harness tvrdí
  218/0, a přitom zápis tepu **neproběhl**. (P35 ho **neopravovala** — byla to
  jiná z pěti nabídek; zapsáno jako otevřené.)
* **DOKLADY P34 PŘEPSANÉ (H166):** `p34-a-overeni-levny-vystup.txt` a
  `p34-health-vystup.txt` už neobsahují běh P34, ale běh P35. **Není to
  ztracené měření** (plný doklad `p34-a-overeni-vystup.txt` zůstal), ale
  **doklad P34 k těm dvěma číslům už neexistuje** — a je to **nevratné**
  (gitignorováno). Příště: cizí měřidlo jen s `--vystup` a se zálohou dokladů.
* **MĚŘIDLA P34 ZESTÁRLA (H168)** — `p34-a-overeni --plne` **93/5**, `p34-mutace`
  **23/4**. **Práce P34 tím není zpochybněná** (všechny chyby jsou „TVRZENÍ
  NENALEZENO“ v zadání, které P34 přepsala, a fixture s absolutním časem).
  **Oprava by byla změna cizích měřidel** — P35 ji **nedělá** (to by bylo
  „opravovat nástroj, který měří práci někoho jiného, a tím si přizpůsobit
  verdikt“); zapsáno jako práce pro P36, pokud se má P34 ještě někdy měřit.

### 66.4 Živý stav při zápisu

```
orchestra: HEAD 3143f31d · origin/main = HEAD (PUSHNUTO) · hra = e4dccdb (cizí
           session; do hry se NESAHALO)
           ⚠ NASAZENÍ P35: deploy #39 na 3143f31d (completed/success 09:42:11Z),
             verze 3985379c-… == scriptVersion.id živého tailu
brány:     g3 → 49 bran · 1 NEDEKLAROVANÝ nenulový exit (validate-all (CELEK) —
           měřeno PŘED rekordem) · validate-all → po pushi VŠE V POŘÁDKU
           (cron BĚŽÍ — H160 se tím uzavírá STAVEM, ne opravou)
           · vlastní měřidlo P35 74/0 plně (levně 52/0) · p35-mutace 33/0
           · test-cron-pokus 9/0 · test-tick-offline 218/0
           · p34-a-overeni levně 51/0 a plně 88/12 (druhý běh 93/5 — NESTABILNÍ;
             ROZDÍLY vs §65: 50/0 a 96/0 — pojmenované: A8 3→4 OK = tik dobíhá;
             většina chyb = TVRZENÍ NENALEZENO v přepsaném zadání = H168)
           · p34-mutace 23/4 (H168: přepsané zadání + absolutní čas ve fixtuře)
           · ŽIVÝ TEP: last_cron tiká (D1 09:40:24Z, pokus o 2 s dřív, zdroj cron)
```

### 66.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p35-a-overeni.py                  # LEVNÉ (A0,A1,A2,A3,B1; ~1 min)
python _analyza\p35-a-overeni.py --plne           # i A4,A5,A6,A7 (dlouhé nohy)
python _analyza\p35-mutace.py                     # důkaz, že měřidlo umí spadnout (33/0)
node tools\test-cron-pokus.mjs                    # 9 fixtur „nedorazil“ vs „nedoběhl“
node tools\test-tick-offline.mjs                  # 218 kontrol (scénář AF = česká base64)
node tools\validate-all.mjs                       # po pushi 0 problémů
python _analyza\g3-brany.py                       # 49 bran (POZOR: s FORGE_REGISTR v harnessu)
python _analyza\p35-sonda-health.mjs              # živý /health: last_cron + POKUS
python _analyza\p35-sonda-d1.py                   # uložený tep z D1 (READ-ONLY)
node _analyza\p35-profil-cpu.mjs --tik --n 3      # ŽIVÝ CPU profil (POZOR: POST /tick = zásah!)
node _analyza\p35-rozklad-tiku.mjs                # rozklad GitHub části tiku
node _analyza\p35-rozklad-roadmapy.mjs            # rozklad čtení roadmapy (H165)
python _analyza\p35-tail-rozbor.py _analyza\p35-tail-raw-vystup.txt   # CPU podle endpointu
node conductor\node_modules\wrangler\bin\wrangler.js tail forge-conductor --format json
```

### 66.6 Co čeká na tebe (uživatel)

* **ROZHODNUTÍ 1 — STROP GRANULE.** Práce se **nevydává** (`ready = 3`,
  `running = 0`) a **není to CPU**: `#244/#245/#246` jsou nad stropem
  `GRAIN_MAX_RUNS = 8`. Možnosti: **zvednout strop** (práce se rozjede, ale
  spálí se další běhy), nebo **opravit ty granule**. Doporučení P35:
  **nejdřív se podívat, proč tytéž granule selhaly 8×** — strop je **brzda,
  která funguje**; jeho zvednutí problém neřeší, jen ho přesune do kvóty.
* **ROZHODNUTÍ 2 — PLACENÝ PLÁN vs. FREE + ZLEVŇOVÁNÍ.** Naměřeno: tik potřebuje
  **18–36 ms CPU** na invokaci, dokumentace uvádí **10 ms**, a přesto tik
  **dobíhá** a od nasazení #38 nejsou **žádné** `exceededResources` (H167).
  **Placený plán tedy dnes NENÍ potřeba** — a kdyby se výpadky vrátily, další
  zlevnění je **odkládání GitHub čtení** (42 % CPU), což je **viditelná změna
  chování** (detekce sloučení po minutách místo hned). **Rozhodnutí je na tobě**;
  P35 nic z toho nezavedla.
* **Nic jiného.** P35 **neměnila chování práce**: jediná změna v conductoru je
  **cena dekódování**, a je nasazená s testem, který ji volá.
"""

# ── řádek 50 do přehledové tabulky ──────────────────────────────────────────
RADEK_50 = (
    "| **50** | **11. 10. 2026** (09:2x – 12:2x +02:00) | **ověřovací (Úkol A: "
    "nasazení P34 třemi kroky + vlastní měřidlo) + akční (Úkol B: H165 — ZLEVNĚNÍ "
    "TIKU) + nálezová** | **NASAZENÍ P34 OVĚŘENO TŘEMI KROKY A TIK ZLEVNĚN.** "
    "**A:** `deploy.yml` **#38 na `f983dace0f9f`** → `completed/success`; "
    "`Current Version ID e0a939e6-…` z logu == `scriptVersion.id` **živého** "
    "`wrangler tail` (47 eventů); `/health` posílá `last_cron_pokus` a tik "
    "**DOBÍHÁ** (`last_cron` 0 min, `ready=3`, `running=0`). Brána "
    "`test-cron-pokus` **9/0** a **tři vady v KOPIÍCH** ji shodí — včetně "
    "důkazu, že **slabá kontrola** (`ok === false`) nad toutéž vadou **projde** "
    "(H158). Měřidlo P34 dnes **51/0** vs. §65 **50/0** → rozdíl **pojmenovaný "
    "po sekcích** (A8 3→4 OK: predikát je OK, protože tik dobíhá; A2 8→5 = jiný "
    "režim). **B (H165):** tik platil **3,66 ms** za přepis base64 **po znacích** "
    "(`Uint8Array.from(atob(…), mapFn)`) z 4,06 ms čtení roadmapy — a pouští se "
    "**každou minutu**; **indexovaný cyklus 0,10 ms**, bajtově ekvivalentní. "
    "Živý CPU profil (47 invokací): **cron 24–36 ms** (med 26,5) před a "
    "**18–29 ms** (med 20) po nasazení, `/tick` 15–25 ms, `/health` 2–7 ms, "
    "`/poll` **0 ms** — dokumentovaných **10 ms tedy NENÍ tvrdý limit** (H164 "
    "dořešeno měřením); GitHub část tiku = **650 kB/min a 7,93 ms = 42 % CPU**. "
    "Oprava nasazena: **deploy #39 na `3143f31d`**, verze `3985379c-…` == živý "
    "tail; `test-tick-offline` **215/0 → 218/0** (nový scénář AF s vícebajtovou "
    "češtinou z base64). **PRÁCE SE STEJNĚ NEVYDÁVÁ — a není to CPU:** "
    "`STROP GRANULE 8/8` (#244/#245/#246) · vlastní měřidlo P35 **52/0** levně a "
    "**74/0** plně, **p35-mutace 33/0** · a **měřidla P34 ZESTÁRLA, ne práce P34 "
    "(H168):** `p34-a-overeni` plně **88/12** (druhý běh 93/5 — NESTABILNÍ; P34 "
    "tvrdí 96/0, většina chyb je „TVRZENÍ NENALEZENO“ v zadání, které P34 sama "
    "přepsala) a `p34-mutace` **23/4** (fixture s absolutním časem `04:59:30Z`) "
    "| **—**"
)

# ── §2.28 do KRONIKY ───────────────────────────────────────────────────────
SEKCE_228 = """### 2.28 Nálezy z P35 (11. 10. 2026) — tik platil za přepis base64 a cizí měřidlo přepsalo doklady

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P36.

| # | Nález | Doklad |
|---|---|---|
| **H165** | **TIK PLATIL 3,66 ms ZA PŘEPIS BASE64 „PO ZNACÍCH“ — a je to trvalý odběr z 10ms rozpočtu.** Když se P35 zeptala, KDE tik mizí CPU, vyšlo najevo, že čtení roadmapy hry (35 kB base64) stojí **4,06 ms** a z toho **3,66 ms** je `Uint8Array.from(atob(…), (c) => c.charCodeAt(0))` — **funkce volaná na KAŽDÝ ZNAK**. Indexovaný cyklus (`for` + `charCodeAt(i)`) stojí **0,10 ms**; `Accept: application/vnd.github.raw` by ušetřil 3,98 ms. **Dekódování je přitom bajtově EKVIVALENTNÍ**, takže se nemění chování, jen cena — a tik se pouští **každou minutu** (1 440×/den). Oprava nasazena (`deploy.yml` #39) a krytá novým scénářem **AF** v `test-tick-offline.mjs` (vícebajtová čeština z base64; **215/0 → 218/0**). Dopad měřen: cron `cpuTime` medián **26,5 → 20 ms** (n=12 → 4). | `_analyza/p35-rozklad-roadmapy.mjs`, `_analyza/p35-rozklad-roadmapy-vystup.txt`, `_analyza/p35-tail-rozbor.py`, `_analyza/p35-tail-po-vystup.txt`, `_analyza/p35-a-overeni-vystup.txt` |
| **H166** | **VLASTNÍ OMYL P35: SPUŠTĚNÍ CIZÍHO MĚŘIDLA PŘEPÍŠE JEHO DOKLADY — A SEAM MĚNÍ ČÍTAČ.** (a) `python _analyza\\p34-a-overeni.py` bez `--vystup` přepsalo **doklady P34** `p34-a-overeni-levny-vystup.txt` i `p34-health-vystup.txt` (oba **gitignorované** → **nevratné**; plný doklad P34 zůstal). Pravidlo: **cizí měřidlo se pouští s `--vystup` (a s záložkou dokladů)**. (b) Týž nástroj se seamem `P34_HEALTH` na **neexistující** soubor hlásil **47/1** — a to je **vada měřidla, ne měřené práce**. (c) A tentýž seam **jednu kontrolu VYNECHÁ** (větev `m.ok_(HEALTH_LIVE.is_file(), …)` je jen bez seamu), takže s ním čítač vyšel **50/0** a **falešně se shodoval s tvrzením §65** — naměřeno, že rozdíl dělá **režim měření, ne stav**. Táž třída jako H145/H150 („kontrola se nechala uspokojit“). | `_analyza/p35-a-overeni.py` (sekce A4 komentuje obojí), `_analyza/p35-pocty-sekci.py`, `_analyza/p35-a4-levny-vystup.txt` |
| **H167** | **ŽIVÝ CPU PROFIL SLUŽBY: 10 ms NENÍ TVRDÝ LIMIT — měřeno, ne převzato.** `p35-profil-cpu.mjs` + `wrangler tail` (47 invokací): `cron` **24–36 ms** (medián 26,5; n=12; **všechny `outcome=ok`**, 0× `exceededCpu`), `POST /tick` **15–25 ms**, `GET /health` **2–7 ms**, `POST /poll` **0 ms**. Cloudflare Analytics za 24 h: `success` 2957, `exceededResources` **1054 v 21 oknech** — ale hodiny **`08Z` a `09Z` hlásí 0** (výpadek skončil nasazením #38). **Deset milisekund je CITACE z dokumentace; 24–36 ms je MĚŘENÍ** — a služba při něm funguje, takže „free plán nutně potřebuje placený“ **není doložené**. Zároveň: **42 % CPU tiku jde na GitHub** (650 kB/min, 7,93 ms parsování) — to je zbývající páka, ale **mění chování** (odklad detekce sloučení), takže patří uživateli. | `_analyza/p35-profil-cpu.mjs`, `_analyza/p35-profil-cpu-vystup.txt`, `_analyza/p35-tail-rozbor-data-vystup.txt`, `_analyza/p35-cf-analytika-vystup.txt` |
| **H168** | **MĚŘIDLA P34 ZESTÁRLA — A NENÍ TO VADA JEJICH PRÁCE (dva nezávislé mechanismy).** P35 naměřila `p34-a-overeni.py --plne` → **93/5** (P34 tvrdí 96/0) a `p34-mutace.py` → **23/4** (P34 tvrdí 23/0). **(a) TVRZENÍ Z PŘEPISOVANÉHO DOKUMENTU:** všech pět chyb merila je `TVRZENÍ NENALEZENO` v bloku „OSTATNÍ BRÁNY PŘI ZÁPISU“ — ta čísla si `p34-a-overeni.py` čte z **`NEXT-SESSION-INSTRUKCE.md`**, což je zadání, které **P34 ve svém vlastním závěru přepsala** pro P35; formulace se změnily (`1 NEDEKLAROVANÝ` místo `0 NEDEKLAROVANÝCH`, `2 problémy` místo `0 problémů`, `p29-a A1M13` bez `--jen`, `p28-b-mutace` v novém zadání není). **Měřidlo, které si bere tvrzení z dokumentu přepisovaného každou session, zestárne v okamžiku, kdy jeho session skončí** — a nikdo to nepozná, protože chyba vypadá jako „chybí tvrzení“. **(b) ABSOLUTNÍ ČAS VE FIXTUŘE:** `p34-mutace.py` má fixture `zdravy` s časy `04:59:30Z`/`05:00:00Z` psanými NAPEVRDO, takže po ~7 h „zdravý stav“ (správně) neprojde — a test hlásí, že měřidlo „neumí projít“. **Pravidlo: fixture má mít čas RELATIVNÍ k `now` a měřidlo si nemá brát tvrzení z cizího/přepisovaného dokumentu** (nebo si je má umět vzít z commitu, který měří). Souvisí s H166 (měřidlo čte jiný zdroj, než si myslí). | `_analyza/p35-p34a-plny-vystup.txt`, `_analyza/p35-p34mutace-vystup.txt`, `_analyza/p35-a-overeni-vystup.txt` |
"""


def zapis_handoff():
    txt = HANDOFF.read_text(encoding="utf-8")
    if re.search(r"^## 66\.", txt, re.M):
        zk(True, "HANDOFF: §66 už je zapsaný (idempotentní — nepřidávám)")
        return
    zk("## 65." in txt, "HANDOFF: §65 existuje (kam se přidává §66)")
    pred = len(txt.encode("utf-8"))
    novy = txt.rstrip("\n") + "\n" + SEKCE_66 + "\n"
    HANDOFF.write_text(novy, encoding="utf-8")
    po = len(novy.encode("utf-8"))
    zk(po > pred, "HANDOFF: §66 přidán (blob %d → %d B)" % (pred, po))
    zk(re.search(r"^## 66\.", novy, re.M) is not None, "HANDOFF: §66 je v souboru")


def zapis_kroniku():
    radky = KRONIKA.read_text(encoding="utf-8").splitlines(keepends=True)
    if any(r.startswith("| **50** |") for r in radky):
        zk(True, "KRONIKA: řádek 50 už je (idempotentní — nepřidávám)")
    else:
        i49 = next((i for i, r in enumerate(radky) if r.startswith("| **49** |")), None)
        zk(i49 is not None, "KRONIKA: řádek 49 existuje (za něj se vkládá 50)")
        if i49 is None:
            return
        radky.insert(i49 + 1, RADEK_50 + "\n")
        zk(RADEK_50.count("|") == 5,
           "KRONIKA: nový řádek má 5 svislítek (jako řádky 43–49, ne 8 jako záhlaví)")

    txt = "".join(radky)
    if re.search(r"^### 2\.28 ", txt, re.M):
        zk(True, "KRONIKA: §2.28 už je (idempotentní — nepřidávám)")
    else:
        kotva = "\n## 3. Počty omylů"
        zk(txt.count(kotva) == 1, "KRONIKA: kotva „## 3. Počty omylů“ je PRÁVĚ 1×")
        txt = txt.replace(kotva, "\n" + SEKCE_228 + kotva, 1)
        zk(re.search(r"^### 2\.28 ", txt, re.M) is not None, "KRONIKA: §2.28 je v souboru")
    KRONIKA.write_text(txt, encoding="utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, choices=["HANDOFF", "KRONIKA"])
    args = ap.parse_args()
    print("=" * 86)
    print("P35 — ZÁPIS ZÁZNAMŮ (HANDOFF §66, KRONIKA řádek 50 + §2.28)")
    print("=" * 86)
    sha_h = __import__("hashlib").sha256(HANDOFF.read_bytes()).hexdigest()
    sha_k = __import__("hashlib").sha256(KRONIKA.read_bytes()).hexdigest()
    print("\n0) PŘED")
    print("   HANDOFF  %d B (%s)" % (HANDOFF.stat().st_size, sha_h[:12]))
    print("   KRONIKA  %d B (%s)" % (KRONIKA.stat().st_size, sha_k[:12]))

    print("\n1) HANDOFF")
    if args.jen != "KRONIKA":
        zapis_handoff()
    print("\n2) KRONIKA")
    if args.jen != "HANDOFF":
        zapis_kroniku()

    print("\n3) KONTROLY (nesmí to rozbít čítače)")
    kod, out = spust(["python", str(ANALYZA / "kronika-kontrola.py")])
    posledni = [l for l in out.splitlines() if l.strip()][-1:] or [""]
    zk(kod == 0, "kronika-kontrola.py → exit 0 (%s)" % posledni[0][:90])
    for l in out.splitlines():
        if "SEDÍ" in l or "řádk" in l or "nález" in l:
            print("      %s" % l.strip()[:150])
    kod, out = spust(["python", str(ANALYZA / "handoff-kontrola-uplnost.py")])
    zk(kod == 0, "handoff-kontrola-uplnost.py → exit 0 (%s)"
       % (out.strip().splitlines() or [""])[-1][:90])
    kod, out = spust(["python", str(ANALYZA / "ov-g-neovereno.py")])
    zk(kod == 0, "ov-g-neovereno.py → exit 0 (%s)" % (out.strip().splitlines() or [""])[-1][:90])

    (ANALYZA / "p35-zapis-stav-vystup.txt").write_text(json.dumps({
        "cas": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "handoff": {"pred": sha_h, "po": __import__("hashlib").sha256(HANDOFF.read_bytes()).hexdigest()},
        "kronika": {"pred": sha_k, "po": __import__("hashlib").sha256(KRONIKA.read_bytes()).hexdigest()},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n" + "=" * 86)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
    for c in chyb:
        print("   CHYBA %s" % c)
    print("=" * 86)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

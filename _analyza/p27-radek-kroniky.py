# -*- coding: utf-8 -*-
r"""P27 — zápis záznamů: HANDOFF §57, KRONIKA řádek 42 + §2.20.

PROČ SKRIPTEM: řádky mají **přes 2 000 znaků** a kotva z načteného řádku ho
zkrátí (omyly 194, 206). Skript navíc po zápisu OVĚŘÍ, že nic nezmizelo,
že čísla, která čtou měřidla P24/P25/P26 (`205/0`, `205 kontrol`, `41/0`, …),
v dokumentech SKUTEČNĚ JSOU — a že souhrn §3 kroniky zůstal NEPŘEPOČÍTANÝ.

Použití: python _analyza/p27-radek-kroniky.py
"""

import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
H = WS / "HANDOFF.md"
K = WS / "KRONIKA-PROJEKTU.md"

# ── 1) HANDOFF: §57 ─────────────────────────────────────────────────────────
ODDIL_57 = r"""## 57. P27 — PŘEMĚŘENÍ P26 A TESTY PRO SEDM ENDPOINTŮ BEZ TESTU (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P27 + stav po P27**. **Co NENÍ:**
pravidla (`AGENTS.md`), projektová znalost (`PROVOZ-ORCHESTRA.md`), historie
(`KRONIKA-PROJEKTU.md` — řádek **42**, nálezy **§2.20**). Zadání P27 je
v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, večer +02:00**. Tvrzení o **stavu**
> (HEAD, hra, živá služba) platí k tomu okamžiku; kdo to čte později,
> **přeměří** (`python _analyza\p27-a-overeni.py --plne`).
>
> **⚠ POZOR NA SOUBĚŽNOU SESSION:** do hry (`uo-shadows`) **zapsal NĚKDO JINÝ**
> tři commity (`6796188`, `43a2004`, `125b062`, **nepushnuté**) a nechal tam
> netrackovaný `_acl-recovery/`. **Není to práce P27** a **nesahalo se na to**;
> stav hry se proti P26 **nezměnil** (P27 do hry nezapsala ani bajt).

### 57.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Přeměření práce P26 VLASTNÍM měřidlem** (A1–A7, každý bod jiným postupem, než vznikl) | `_analyza/p27-a-overeni.py --plne` → **140 kontrol, 0 chyb** (0× `NEZMĚŘENO`), uložený výstup `p27-a-plne-vystup.txt` |
| **A** | **Důkaz, že i tohle měřidlo umí spadnout** — tři mutace **v KOPIÍCH**, každá s **diferenciálem** (originál spadne / oslabená kopie projde) | `_analyza/p27-b-mutace.py` → **27 kontrol, 0 chyb** |
| **B1** | **Testy pro SEDM endpointů, které dnes nevolal žádný test** (`/health`, `/queue`, `/roadmap`, `/failed`, `/status`, `/workers`, `/games`) — TVAR i OBSAH odpovědi | `tools/test-tick-offline.mjs` → **205/0** (bylo **146/0**, **+59 kontrol**); zarážka v HANDLERU u každého zvlášť (A2) |
| **B1** | Dvě sondy, které měřily, NA ČEM Úkol B1 stojí | `_analyza/p27-sonda-endpointy.py` (které endpointy test volá) a `_analyza/p27-sonda-inventar.py` (co je v otisku vstupů) — obě v `PRESKOCIT` dávky `p20-d` |
| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) | `g3` → **49 bran, 1 deklarovaný nenulový exit** (`zadání kontrola`), **exit 0** · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |

### 57.2 Nálezy P27 (každý doložený měřením)

1. **SEDM ENDPOINTŮ BEZ TESTU — a nové testy je OPRAVDU VOLAJÍ.** P26 to
   naměřila staticky; P27 to doložila **zarážkou UVNITŘ HANDLERU** (sedm
   zarážek, hash před i po, `try/finally`): `/health` → **18 červených**
   (z toho `X:` **12**), `/queue` → **6** (`Y:` 5), `/roadmap` → **5** (`Z:` 4),
   `/failed` → **11** (`AA:` 8), `/status` → **5** (`AB:` 4), `/workers` → **5**
   (`AC:` 4), `/games` → **5** (`AD:` 4) — a kontrolní `A: /tick odpoví 200`
   zůstala **pokaždé zelená**. Když zarážka nezapne ani jednu kontrolu, test
   o té smlouvě **netvrdí nic**.
2. **TESTY TVRDÍ OBSAH, NE JEN `status === 200`.** V **KOPII** testu se falešná
   D1 přinutila vracet **prázdné výsledky** (`all()` → `{results: []}`):
   **55 červených** — a všech sedm kontrol „… odpoví 200" zůstalo **ZELENÝCH**.
   To je celý rozdíl mezi **přítomností** a **chováním**: kdyby testy tvrdily
   jen stavový kód, byly by zelené nad prázdnou odpovědí.
3. **OPRAVA P25-K MĚŘÍ CELÝ ROZSAH — ověřeno VLASTNÍM počítadlem.** Rozsah
   **99 řádků Hxx** se počítá **vlastním průchodem souborů** (1 v `HANDOFF.md`
   + 98 v `_archiv/HANDOFF-HISTORIE.md`), ne čtením výpisu brány; součet po
   souborech i rozsah **mimo** živé zdroje (**139** řádků v **7** souborech)
   sedí na vlastní měření; **verze z `HEAD`** měří taky 99 (oprava je
   **commitnutá**, ne jen v pracovním stromě); fixtura s `NEOVĚŘENO` → `exit 1`
   a **prázdná** fixtura → `NEMĚŘENO` (`exit 1`).
4. **ČÍSLA §56 SEDÍ — VŠECHNA, a jedno se POSUNULO mou prací.** Znovu naměřeno
   **spuštěním**: `p26-b-mutace` **26/0** · `p25-b-mutace` **27/0** · `p24-b-mutace`
   **17/0** · `handoff-kontrola-uplnost` **83/83** · `kronika-kontrola` **SEDÍ** ·
   `ov-g-neovereno` **0 NEOVĚŘENO nad 99 řádky** · `over-dokumentaci` **64/0** ·
   `over-skilly` **13/0** (to číslo §56 **netvrdí** — měří se, neporovnává) ·
   `tick-mutace` **20 vrat / 41/0** · `g3` **49 bran**, 1 deklarovaný exit,
   **exit 0** · `validate-all` **VŠE V POŘÁDKU** · **živá služba**: `/health`
   `ok=true ready=1 running=0 games=1` (přesně jako snapshot v §56) a **šest
   chráněných endpointů** vrátí **bez tajemství 401** a **s ním 200**.
   **POSUN:** `test-tick-offline` **146/0 → 205/0** — to je **můj vlastní**
   důsledek (B1 přidala 59 kontrol). Tvrzení §56 je **ve svém čase správné**:
   dobově se to měří na verzi z commitu `3d57783` → **146/0** (naměřeno).
5. **NÁLEZ O MĚŘIDLE P26: ČTE TVRZENÍ Z JEDNOHO HISTORICKÉHO ODDÍLU.** Jeho A4
   porovnává číslo přečtené z **§55** s **živým** měřením — takže po každé
   legitimní změně čítače testu je červená **přesně ta jedna kontrola**
   (a nic jiného). Naměřeno: `p26-a --plne` → **90 kontrol, 1 chyba**, a ta
   jediná je `A4 test-tick-offline.mjs = tvrzených 146/0`. **Dobová kotva se
   musí měřit na stromě, o kterém tvrzení platí.**
6. **ČÍTAČ MĚŘIDLA P26 ZÁVISÍ NA STAVU INVENTÁŘE: 90 vs 86.** Nad **čerstvým**
   inventářem má `p26-a --plne` **90 kontrol**, nad **zastaralým 86** — jeho A6
   totiž u zastaralého inventáře hlásí **pojmenovaný STAV** místo čtyř
   `check(...)` (g3 exit, g3 bez čítače, validate-all ×2). Naměřeno **oběma
   směry**. Kdo to nezměří, zapíše „čítač nesedí" jako vadu měřidla.
7. **PŘEPÍNAČ `--g3` MĚŘIDLA P26 JE V DÁVKOVÉM REŽIMU MRTVÝ.** Kopie `g3`
   s **50. branou** v `BRANY` nezmění dávkový běh A4 (`exit 0`) — kontrola počtu
   bran je až **za** `if not plne: return`. Není to vada chování, je to
   **neviditelná hranice režimu**; kdo ji nezná, myslí si, že přepínač měří.
8. **`.env` MÁ BOM — a hledání klíče TICHE SELHALO.** Kontrola živé služby
   hlásila „chybí `FORGE_URL`", protože klíč se načetl jako `"\ufeffFORGE_URL"`.
   Náprava je číst `.env` (i `.secrets/cf-secrets.json`) jako **`utf-8-sig`**.
   Je to **nová instance pasti s BOM**, tentokrát v **datovém** souboru, kde ji
   nikdo nečeká (u `.py`/`.ps1` se hlídá).
9. **`ANALYZA` vs `ANALIZA` — ZNÁMÁ PAST SE V P27 OPAKOVALA, DVAKRÁT.** Kotvy
   v měřidlech používaly `ANALIZA` (s **I**), kód má `ANALYZA` (s **Y**)
   — táž past, kterou má P25 zapsanou v §2.18. Poprvé to **tiše** odmítl nástroj
   `edit` („kotva nenalezena", ačkoli v souboru je — **oko ji přečte jako
   ANALIZA**), podruhé to spadlo nahlas (`NameError: name 'ANALIZA' is not
   defined` v `p27-b-mutace.py`). **Poučení: kotvu ověřuj VÝPISEM KÓDŮ ZNAKŮ
   (`ord()`/hex), ne okem** — Rozdíl je jediný znak a obě varianty vypadají
   stejně.
10. **DIFERENCIÁL CHYTIL „SPADLO, ALE Z JINÉHO DŮVODU".** V mutaci M3 ležela
    zúžená kopie `ov-g-neovereno.py` v **PODSLOŽCE** — a ten skript si kořen repa
    odvozuje jako `Path(__file__).parents[1]`, takže hledal
    `_analyza/KRONIKA-PROJEKTU.md` a spadl na `FileNotFoundError`. Měření
    „originál na té vadě SPADL" tím **prošlo** (a bylo to špatně); odhalila to až
    **oslabená kopie**, která spadla taky. **„Spadlo to" není důkaz — důkaz je
    diferenciál.**
11. **BRÁNA S PREDIKÁTEM, KTERÝ JE SPLNĚNÝ I V ZELENÉM STAVU.** První verze A7
    tvrdila „výstup obsahuje `ZASTARAL`/`NEZMĚNĚN`" — a v **zeleném** výstupu je
    slovo „nezměněno" v próze („řetězce jako ‚schváleno a nezměněno'"), takže
    kontrola procházela **falešně pozitivně**. Opraveno na konkrétní hlášení
    `INVENTÁŘ JE ZASTARALÝ` **plus negativní kontrola** nad čerstvým inventářem.
    **A druhá věc téhož: ZÁLEŽÍ NA POŘADÍ** — brána se musí měřit v **okně mezi**
    přidáním souboru a přegenerováním; kdo po přidání hned přegeneruje, měří
    čerstvý inventář a „brána nespadla" je falešný nález.
12. **DVA GATE SE VYLUČUJÍ (nález P26-L se potvrdil).** `p25-b-mutace.py` čistí
    **pět konkrétních souborů** — a protože jsem do `_analyza/p20-d-doklady.py`
    přidal sondy P27, hlásilo **27/1**; po commitu **27/0**. Před commitem je
    tedy `p25-b` červené **stavem stromu**, ne vadou kódu.
13. **SANDBOX: BEZ ZAMRZNUTÍ, ALE `git fetch` POŘÁD NEPROJDE.** V režimu
    `workspace-write` padal `git fetch` na `.git/FETCH_HEAD: Permission denied`
    a testy tiku na `spawn EPERM` (wrangler) — po přepnutí na **plný přístup**
    šlo obojí. Živý stav obou repů se proto ověřil **`git ls-remote`**
    (orchestra `92aa80a`, hra `932dc6f`) — ten se obejde bez zápisu do `.git`.
    Je to **stav prostředí**, ne vada skriptu (`dsh-prostredi` §4e).

### 57.3 Živý stav při zápisu (7. 10. 2026, večer +02:00)

```
orchestra: HEAD 1bdc982 + záznamy · origin/main 92aa80a · nepushnutých 5 (P25, 3× P26, P27)
hra:       HEAD 125b062 · origin/main 932dc6f · nepushnuté 3 (SOUBĚŽNÁ session,
           15:50/15:58/16:02) · netrackovaný `_acl-recovery/` (cizí, nesahalo se)
živá služba: /health → ok=true ready=1 running=0 games=1 · cíl měřen (`targets`)
           /tick se NEVOLAL (mění stav) — jen čtení sedmi endpointů
brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0
           validate-all → VŠE V POŘÁDKU
p27-a:     --plne → 140 kontrol, 0 chyb
test-tick-offline: 205/0 (bylo 146/0; +59 kontrol z B1)
p24-a:     99/x — každá červená je `A8` (dobový stav HRY, ne vada orchestra)
```

### 57.4 Co čeká na tebe (uživatel)

- **PUSH — rozhodnutí uživatele.** P27 **commitla, nepushla**; `origin/main..HEAD`
  bude **5** (P25, tři commity P26, P27). P27 mění **`tools/`**, **`_analyza/`**
  a **dokumenty** — **žádný soubor pod `conductor/**`**, takže **deploy živé
  služby to nemění** (ověř `git diff --name-only origin/main..HEAD`).
  Cesta zpět: `git reset --soft`.
- **SEDM ENDPOINTŮ JE ZAVŘENO** (`HANDOFF.md` §57.1, B1) — což zbývá z nabídky
  §2.2 zadání: **B2** rozhodnout `.gitattributes` (P24-B; dnes `git checkout`
  tiše rozbíjí vícřádkové kotvy mutací), **B3** ověřit B4 na ŽIVÉ službě
  (`/game/active {active:false}` → `games=0`) — ⚠ **dočasně zastaví orchestra**,
  takže na výslovné „ano", **B4** zapnout strop `GRAIN_MAX_RUNS`, **B5** slepé
  místo `over-skilly.py` (má rozdělanou práci souběžné session).
- **`_acl-recovery/` v `uo-shadows`** je **cizí, netrackovaný** artefakt
  souběžné session. **Nemaže se** a **necommituje** — patří té session.
- **`HANDOFF.md` §6 je ZÁZNAM z 2. 10. 2026**, ne seznam živých bran
  (má předpřesunové cesty a čísla 63/12). Autorita je `BRANY`
  v `_analyza\g3-brany.py`.

### 57.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p27-a-overeni.py --plne   # A1-A7: zarážky, obsah, rozsah, g3
python _analyza\p27-b-mutace.py           # umí to spadnout? 27 kontrol, 0 chyb
node tools\test-tick-offline.mjs          # 205/0 (bylo 146/0)
python _analyza\p27-sonda-endpointy.py    # které endpointy test volá (15/15)
python _analyza\p27-sonda-inventar.py     # co je v otisku vstupů inventáře
python _analyza\ov-g-neovereno.py         # rozsah 99 řádků Hxx, 0 NEOVĚŘENO
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json  # POSLEDNÍ
python _analyza\g3-brany.py               # 49 bran, 1 deklarovaný exit, exit 0
node tools\validate-all.mjs               # VŠE V POŘÁDKU
python _analyza\p26-a-overeni.py --plne   # 90 kontrol; 1 červená = §55 tvrdí 146/0
python _analyza\p25-a-overeni.py --plne   # 53/0
python _analyza\p24-a-overeni.py          # 99/x (A8 = stav hry)
python _analyza\tick-mutace.py            # 20 vrat / 41/0
```
"""

# ── 2) KRONIKA: řádek 42 ────────────────────────────────────────────────────
RADEK_42 = (
    "| **42** | **7. 10. 2026** (odpoledne – večer +02:00) | "
    "**ověřovací (Úkol A) + akční (Úkol B1)** | **Přeměřit práci P26 VLASTNÍM "
    "měřidlem — a dopsat testy pro SEDM endpointů, které nevolal žádný test.** "
    "Zadání P27 §2.1: záznamy i měřidlo P26 psal autor, který si je sám "
    "ověřoval („autor není nezávislý reviewer“). Provedeno: **A1–A7 vlastním "
    "postupem** (`_analyza/p27-a-overeni.py --plne`) + **důkaz, že to měřidlo "
    "umí spadnout** (`p27-b-mutace.py`, **27/0**, tři mutace v KOPIÍCH "
    "s diferenciálem) a **Úkol B1** — testy pro `/health`, `/queue`, `/roadmap`, "
    "`/failed`, `/status`, `/workers`, `/games` (TVAR i OBSAH odpovědi) "
    "| **Brány:** `test-tick-offline` **205/0** (bylo **146/0**, +59 kontrol) · "
    "`g3` **49 bran**, 1 deklarovaný nenulový exit (`zadání kontrola`), "
    "**exit 0** · `validate-all` **VŠE V POŘÁDKU** · `handoff-kontrola-uplnost` "
    "**83/83** · `kronika-kontrola` **SEDÍ** · `ov-g-neovereno` **0 NEOVĚŘENO "
    "nad 99 řádky** · `p26-b-mutace` **26/0** · `p25-b-mutace` **27/0** · "
    "`p24-b-mutace` **17/0** · `tick-mutace` **20 vrat / 41/0** · "
    "`over-dokumentaci` **64/0** · `over-skilly` **13/0** · **A2 POPRVÉ PRO "
    "SEDM ENDPOINTŮ:** `/health` → **18 červených (`X:` 12)**, `/queue` → "
    "**6 (`Y:` 5)**, `/roadmap` → **5 (`Z:` 4)**, `/failed` → **11 (`AA:` 8)**, "
    "`/status` → **5 (`AB:` 4)**, `/workers` → **5 (`AC:` 4)**, `/games` → "
    "**5 (`AD:` 4)** — kontrolní `A: /tick odpoví 200` **pokaždé zelená** · "
    "**A3:** prázdná falešná D1 → **55 červených**, a všech sedm kontrol "
    "„… odpoví 200“ zelených · **A5:** rozsah **99** ověřen VLASTNÍM počítadlem "
    "| **—** | **Nálezy a poučení:** (1) **SEDM ENDPOINTŮ BEZ TESTU JE ZAVŘENO** "
    "a je to doložené **zarážkou V HANDLERU** u každého zvlášť (sedm zarážek, "
    "hash před i po). (2) **Testy tvrdí OBSAH, ne jen `status === 200`:** "
    "s prázdnou falešnou D1 zčervenalo 55 kontrol, ale všech sedm „odpoví 200“ "
    "zůstalo ZELENÝCH — **přítomnost ≠ chování**. (3) **Čísla §56 SEDÍ**; jedno "
    "se **posunulo mou prací**: `test-tick-offline` 146/0 → **205/0** (+59), "
    "a §56 platí **o verzi z commitu `3d57783`** (dobově naměřeno 146/0). "
    "(4) **NÁLEZ O MĚŘIDLE P26:** jeho A4 čte tvrzení z **jednoho historického "
    "oddílu** (§55) a porovnává je s **živým** měřením → po každé legitimní "
    "změně čítače testu je červená **přesně ta jedna kontrola** `p26-a --plne` "
    "= **90 kontrol, 1 chyba**. (5) **Čítač `p26-a` závisí na stavu inventáře:** "
    "**90** nad čerstvým, **86** nad zastaralým (4 kontroly se změní na "
    "pojmenovaný STAV) — naměřeno oběma směry; kdo to nezměří, zapíše „čítač "
    "nesedí“ jako vadu měřidla. (6) **Přepínač `--g3` měřidla P26 je v dávkovém "
    "režimu mrtvý** (kontrola počtu bran je až za `if not plne: return`) — "
    "naměřeno kopií g3 s 50. branou. (7) **`.env` má BOM** a hledání klíče "
    "**tiše selhalo** (`\"\\ufeffFORGE_URL\"`); čti `.env` jako **`utf-8-sig`** — "
    "nová instance pasti s BOM v **datovém** souboru. (8) **`ANALYZA` vs "
    "`ANALIZA` — známá past se opakovala DVAKRÁT:** kotvy používaly `ANALIZA` "
    "(s I), kód má `ANALYZA` (s Y); jednou to tiše odmítl nástroj `edit`, "
    "podruhé spadlo na `NameError`. **Kotvu ověřuj výpisem kódů znaků, ne "
    "okem.** (9) **Diferenciál chytil „spadlo, ale z jiného důvodu“:** zúžená "
    "kopie v PODSLOŽCE spadla na `FileNotFoundError` (kořen repa se odvozuje "
    "jako `parents[1]`), takže „originál spadl“ prošlo — a bylo to špatně. "
    "(10) **Brána s predikátem splněným i v zeleném stavu:** „obsahuje "
    "ZASTARAL/NEZMĚNĚN“ procházelo i nad zeleným výstupem (slovo „nezměněno“ "
    "v próze) — opraveno na konkrétní hlášení **plus negativní kontrola**; "
    "a **záleží na POŘADÍ** (měřit v okně mezi přidáním souboru "
    "a přegenerováním). (11) **Dva gate se vylučují (P26-L potvrzen):** "
    "`p25-b` hlásilo **27/1**, protože jsem přidal sondy do "
    "`_analyza/p20-d-doklady.py`; po commitu **27/0**. (12) **Sandbox:** "
    "`git fetch` padá na `.git/FETCH_HEAD` a testy tiku na `spawn EPERM` "
    "(wrangler) — s plným přístupem projdou; živý stav repů ověřen "
    "`git ls-remote`. **Co zůstává:** testy pro sedm endpointů jsou HOTOVÉ; "
    "na řadě je **B2** (`.gitattributes`), **B3** (B4 živě — chce „ano“), "
    "**B4** (strop granulí), **B5** (slepé místo `over-skilly`); a **push "
    "P25+P26+P27** (rozhodnutí uživatele; P27 nemění `conductor/**`, takže "
    "deploy nic nemění) |"
)

# ── 3) KRONIKA: §2.20 ───────────────────────────────────────────────────────
ODDIL_220 = r"""### 2.20 Nálezy z P27 (7. 10. 2026) — sedm endpointů bez testu a měřidlo, které čte jeden historický oddíl

**Vznikly tím, že se PRÁCE P26 PŘEMĚŘILA JINÝM MĚŘIDLEM** (ne čtením §56) a že
se dodělal Úkol B1 — testy pro endpointy, které nevolal **nikdo**. Záznam:
`HANDOFF.md` **§57**; měřidlo: `_analyza/p27-a-overeni.py` a jeho mutační důkaz
`_analyza/p27-b-mutace.py` (**27/0**, tři mutace v KOPIÍCH s diferenciálem).

| # | Co hrozilo / co se tvrdilo | Co naměřeno | Stav |
|---|---|---|---|
| **P27-A** | „Endpointy `/health`, `/queue`, `/roadmap`, `/failed`, `/status`, `/workers`, `/games` netestuje nikdo.“ | **Pravda — a staticky doložená** (`p27-sonda-endpointy.py`: 0 volání u všech sedmi). Po B1: **205/0** (bylo **146/0**, +59 kontrol) | **UZAVŘENO (B1)** + doloženo **zarážkou V HANDLERU** u každého zvlášť: `/health` → 18 červených (`X:` 12), `/queue` → 6 (`Y:` 5), `/roadmap` → 5 (`Z:` 4), `/failed` → 11 (`AA:` 8), `/status` → 5 (`AB:` 4), `/workers` → 5 (`AC:` 4), `/games` → 5 (`AD:` 4); `A: /tick odpoví 200` pokaždé **zelená** |
| **P27-B** | „Test, který ověří `status === 200`, tu smlouvu měří.“ | V **KOPII** testu se falešná D1 přinutila vracet **prázdné výsledky** → **55 červených**, ale všech **sedm** kontrol „… odpoví 200“ zůstalo **ZELENÝCH** | **DOLOŽENO, ŽE MĚŘÍ OBSAH.** Stavový kód je **přítomnost**, ne **chování** — test proto tvrdí i klíče, počty a hodnoty z D1 |
| **P27-C** | „Když `ov-g-neovereno.py` hlásí 0× NEOVĚŘENO nad 99 řádky, je to celý rozsah.“ | **Ověřeno DVĚMA nezávislými cestami:** vlastním průchodem souborů (1 + 98) i součtem po souborech z brány; rozsah **mimo** živé zdroje (**139** řádků v **7** souborech) sedí na vlastní měření; **verze z `HEAD`** měří taky 99 (oprava je commitnutá) | **POTVRZENO** + fixtury: `NEOVĚŘENO` → `exit 1`, **prázdný** rozsah → `NEMĚŘENO` (`exit 1`) |
| **P27-D** | „Čísla §56 sedí, protože je P26 naměřila.“ | Znovu **spuštěno, ne přečteno**: `p26-b` **26/0**, `p25-b` **27/0**, `p24-b` **17/0**, `handoff` **83/83**, `kronika` **SEDÍ**, `ov-g` **99**, `over-dokumentaci` **64/0**, `over-skilly` **13/0** (§56 to číslo netvrdí), `tick-mutace` **20 vrat / 41/0**, `g3` **49 bran** / 1 deklarovaný exit, `validate-all` **VŠE V POŘÁDKU**, **živá služba** `ok=true ready=1 running=0 games=1` | **SEDÍ.** Jedno číslo se **posunulo mou prací**: `test-tick-offline` **146/0 → 205/0**; §56 platí **o verzi z `3d57783`** (dobově naměřeno **146/0**) |
| **P27-E** | „Měřidlo, jehož číslo nesedí, je vadné.“ | `p26-a --plne` je dnes **90 kontrol, 1 chyba** — a ta jediná je `A4 test-tick-offline.mjs = tvrzených 146/0`. Měřidlo P26 čte tvrzení z **JEDNOHO historického oddílu** (§55) a porovnává je s **živým** měřením | **NÁLEZ O MĚŘIDLE, NE VADA KÓDU.** Po každé legitimní změně čítače je červená **přesně ta jedna kontrola**; **dobová kotva se měří na stromě, o kterém tvrzení platí** |
| **P27-F** | „Čítač měřidla je konstanta.“ | `p26-a --plne` má **90** kontrol nad **čerstvým** inventářem a **86** nad **zastaralým** (4 kontroly se změní na pojmenovaný STAV: g3 exit, g3 bez čítače, validate-all ×2) — naměřeno **oběma směry** | **ČÍTAČ ZÁVISÍ NA STAVU.** Kdo to nezměří, zapíše „čítač nesedí“ jako vadu měřidla (`overovani` §7.13) |
| **P27-G** | „Přepínač `--g3` v měřidle P26 něco mění.“ | Kopie `g3` s **50. branou** v `BRANY` nezměnila **dávkový** běh A4 (`exit 0`) — kontrola počtu bran je až **za** `if not plne: return` | **V DÁVCE JE MRTVÝ.** Neviditelná hranice režimu: kdo ji nezná, myslí si, že přepínač měří |
| **P27-H** | „Když soubor s klíči existuje, klíč se načte.“ | `.env` má **UTF-8 BOM**, takže klíč vyšel jako `"\ufeffFORGE_URL"` a hledání **tiše selhalo** (kontrola živé služby hlásila „chybí FORGE_URL“) | **OPRAVENO:** `.env` i `.secrets/cf-secrets.json` se čtou jako **`utf-8-sig`**. **BOM škodí i v DATOVÉM souboru**, kde ho nikdo nehlídá |
| **P27-I** | „Kotva `ANALIZA` je v kódu.“ | **Není — kód má `ANALYZA`** (s Y). Táž past, kterou má P25 v §2.18, se v P27 opakovala **dvakrát**: jednou to **tiše** odmítl nástroj `edit` („kotva nenalezena“), podruhé spadlo na `NameError: name 'ANALIZA' is not defined` | **POUČENÍ: kotvu ověřuj VÝPISEM KÓDŮ ZNAKŮ (`ord()`/hex), ne okem.** Rozdíl je jediný znak a obě varianty vypadají stejně |
| **P27-J** | „Když měřidlo na vrácené vadě spadne, vadu chytilo.“ | V mutaci M3 ležela zúžená kopie `ov-g-neovereno.py` v **PODSLOŽCE**; skript si kořen repa odvozuje jako `Path(__file__).parents[1]`, takže hledal `_analyza/KRONIKA-PROJEKTU.md` a spadl na `FileNotFoundError`. Měření „originál na té vadě SPADL“ tím **prošlo** | **ODHALIL DIFERENCIÁL** (oslabená kopie spadla taky). **„Spadlo to“ není důkaz — důkaz je diferenciál** |
| **P27-K** | „Kontrola, která hledá `ZASTARAL`/`NEZMĚNĚN`, rozliší zelenou od červené.“ | V **zeleném** výstupu je slovo „nezměněno“ v próze („řetězce jako ‚schváleno a nezměněno‘“) → kontrola procházela **falešně pozitivně** | **OPRAVENO** na konkrétní hlášení `INVENTÁŘ JE ZASTARALÝ` **plus negativní kontrola** nad čerstvým inventářem. **A záleží na POŘADÍ:** měřit v okně mezi přidáním souboru a přegenerováním |
| **P27-L** | „Dva gate se vylučují jen v P26.“ | Přidání sond P27 do `_analyza/p20-d-doklady.py` (jeden z **pěti** souborů, které `p25-b-mutace.py` hlídá) → **27/1**; po commitu **27/0** | **POTVRZENO (P26-L).** Před commitem je `p25-b` červené **stavem stromu**, ne vadou kódu |
| **P27-M** | „Když `git fetch` nejde, stav repů neověřím.“ | V `workspace-write` padá `git fetch` na `.git/FETCH_HEAD: Permission denied` a testy tiku na `spawn EPERM` (wrangler); po **plném přístupu** projde obojí | **STAV PROSTŘEDÍ, NE VADA SKRIPTU** (`dsh-prostredi` §4e). Živý stav jde ověřit **`git ls-remote`** (orchestra `92aa80a`, hra `932dc6f`) — bez zápisu do `.git` |
| **P27-N** | „Do hry teď nikdo nepíše (je pozastavená).“ | **Píše** (jako v P26): `125b062` + tři nepushnuté commity + netrackovaný `_acl-recovery/`; P27 do hry **nezapsala ani bajt** a stav se **nezměnil** | **ZAPSÁNO JAKO STAV.** Na práci té session se nesahalo |
"""

kontrol = 0
chyb = []


def k(ok: bool, popis: str) -> None:
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'}  {popis}")
    if not ok:
        chyb.append(popis)


print("=" * 78)
print("P27 — zápis záznamů (HANDOFF §57, KRONIKA řádek 42 + §2.20)")
print("=" * 78)

# ── HANDOFF ─────────────────────────────────────────────────────────────────
h_text = H.read_bytes().decode("utf-8")
k("\r" not in h_text, "HANDOFF má LF")
k("## 56. P26 —" in h_text, "§56 (záznam P26) zůstal")
if "## 57. P27 —" in h_text:
    print("  OK    §57 už v HANDOFFu je — nepřidávám")
    kontrol += 1
else:
    H.write_bytes((h_text.rstrip("\n") + "\n\n" + ODDIL_57).encode("utf-8"))
    h_text = H.read_bytes().decode("utf-8")
    k("## 57. P27 —" in h_text, "§57 vložen na KONEC (nic se nepřepisovalo)")
for kotva, popis in (("NEZÁVISLÉ PŘEMĚŘENÍ", "§54"), ("TESTOVÁNÍ ZAPISUJÍCÍCH ENDPOINTŮ", "§55"),
                     ("PŘEMĚŘENÍ P25, ZARÁŽKA V HANDLERU", "§56"),
                     ("NASZENO A OVĚŘENO ŽIVĚ", "§53")):
    k(kotva in h_text, f"{popis} zůstal")
k("watchdog: 0 ohlášeno (prah 3)" in h_text, "§53 nese své PŮVODNÍ živé měření")
k(not H.read_bytes().startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")
# Čísla, která musí být v dokumentu ZAPSANÁ (čtou je měřidla P24/P25/P26):
for cislo in ("205/0", "205 kontrol", "53/0", "27/0", "41/0", "20 vrat", "49 bran",
              "99/3", "99/2", "83/83", "64/0", "26 kontrol", "99 řádky", "27/0"):
    k(cislo in h_text, f"HANDOFF tvrdí naměřené `{cislo}`")
k("140 kontrol" in h_text, "HANDOFF tvrdí čítač měřidla P27 (140 kontrol)")

# ── KRONIKA ─────────────────────────────────────────────────────────────────
puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF")
k("### 2.19 Nálezy z P26" in text, "§2.19 (nálezy P26) zůstala")

zmena = False
if any(r.startswith("| **42** |") for r in radky):
    print("  OK    řádek 42 už v kronice je — nevkládám")
    kontrol += 1
else:
    i41 = next((n for n, r in enumerate(radky) if r.startswith("| **41** |")), None)
    k(i41 is not None, "kotva: řádek session 41")
    if i41 is not None:
        konec = "\n" if radky[i41].endswith("\n") else ""
        radky.insert(i41 + 1, RADEK_42 + konec)
        zmena = True
        k(any(r.startswith("| **42** |") for r in radky), "řádek 42 vložen ZA řádek 41")

if "### 2.20 Nálezy z P27" in text:
    print("  OK    §2.20 už v kronice je — nevkládám")
    kontrol += 1
else:
    i3 = next((n for n, r in enumerate(radky) if r.startswith("## 3. ")), None)
    k(i3 is not None, "kotva: nadpis §3")
    if i3 is not None:
        radky.insert(i3, ODDIL_220 + "\n")
        zmena = True
        k(any("### 2.20 Nálezy z P27" in r for r in radky), "§2.20 vložen PŘED §3")

if zmena:
    nove = "".join(radky).encode("utf-8")
    K.write_bytes(nove)
    print(f"  ZAPSÁNO: KRONIKA-PROJEKTU.md ({len(puvodni)} → {len(nove)} B)")
else:
    print("  beze změny")

zpet = K.read_bytes()
k(zpet.count(b"\r\n") == 0, "v kronice nejsou CRLF")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
t2 = zpet.decode("utf-8")
for kotva, popis in (("| **39** |", "řádek 39"), ("| **40** |", "řádek 40"),
                     ("| **41** |", "řádek 41"), ("| **42** |", "řádek 42")):
    k(kotva in t2, f"{popis} zůstal / je v dokumentu")
k("### 2.18 Nálezy z P25" in t2, "§2.18 zůstala")
k("### 2.19 Nálezy z P26" in t2, "§2.19 zůstala")
k("### 2.20 Nálezy z P27" in t2, "dokument obsahuje §2.20")
# ⚠ SOUHRN SE NEPŘEPOČÍTÁVÁ (omyly se od 6. 10. 2026 nevedou).
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t2,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN (omyly se nevedou)")
k(re.search(r"^\| \*\*42\*\* \|.*\| \*\*—\*\* \|", t2, re.M) is not None,
  "řádek 42 má ve sloupci omylů `—`")

# ── NEOVĚŘENO: měřidlem, ne hledáním slova ──────────────────────────────────
print()
print("--- NEOVĚŘENO: měří se STAV návrhů (NAxx) a nálezů (Hxx) ---")
r = subprocess.run([sys.executable, "-B", str(WS / "_analyza" / "ov-g-neovereno.py")],
                   cwd=str(WS), capture_output=True, timeout=300)
v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
k(r.returncode == 0, "ov-g-neovereno.py → žádný návrh ani nález ve stavu NEOVĚŘENO")
m_nav = re.search(r"návrhů celkem:\s*(\d+)", v)
m_nal = re.search(r"nálezů \(řádků tabulek Hxx\) CELKEM:\s*(\d+)", v)
print("      měřeno: návrhů %s, nálezů %s"
      % (m_nav.group(1) if m_nav else "?", m_nal.group(1) if m_nal else "?"))
k(m_nav is not None and int(m_nav.group(1)) > 0, "měřidlo opravdu otevřelo nějaké návrhy")
# ⚠ ROZSAH SE KONTROLUJE taky — jinak je „0 NEOVĚŘENO“ zelená nad ničím (P25-K).
k(m_nal is not None and int(m_nal.group(1)) == 99,
  "měřidlo měřilo CELÝ rozsah (99 řádků Hxx, ne 1)")

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
print("=" * 78)
for c in chyb:
    print("  CHYBA: %s" % c)
print("HANDOFF sha256: %s" % hashlib.sha256(H.read_bytes()).hexdigest()[:16])
print("KRONIKA sha256: %s" % hashlib.sha256(K.read_bytes()).hexdigest()[:16])

sys.exit(1 if chyb else 0)

# -*- coding: utf-8 -*-
r"""P26 — zápis záznamů: HANDOFF §56, KRONIKA řádek 41 + §2.19.

PROČ SKRIPtem: řádky mají **přes 2 000 znaků** a kotva z načteného řádku ho
zkrátí (omyly 194, 206). Skript navíc po zápisu OVĚŘÍ, že nic nezmizelo.

Použití: python _analyza/p26-radek-kroniky.py
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

# ── 1) HANDOFF: §56 ─────────────────────────────────────────────────────────
ODDIL_56 = r"""## 56. P26 — PŘEMĚŘENÍ P25, ZARÁŽKA V HANDLERU A OPRAVA ROZSAHU MĚŘIDLA (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P26 + stav po P26**. **Co NENÍ:**
pravidla (`AGENTS.md`), projektová znalost (`PROVOZ-ORCHESTRA.md`), historie
(`KRONIKA-PROJEKTU.md` — řádek **41**, nálezy **§2.19**). Zadání P26 je
v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 13:1x–16:2x +02:00**. Tvrzení
> o **stavu** (HEAD, hra, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\p26-a-overeni.py --plne`).
>
> **⚠ POZOR NA SOUBĚŽNOU SESSION:** do hry zapisoval **NĚKDO JINÝ** — mezi
> 15:50 a 16:02 +02:00 přibyly v `uo-shadows` **tři commity** (`6796188`,
> `43a2004`, `125b062`, **nepushnuté**) a netrackovaný `_acl-recovery/`.
> **Není to práce P26** a **nesahalo se na to**.

### 56.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Přeměření práce P25 VLASTNÍM měřidlem** (A1–A6, každý bod jiným postupem, než vznikl) | `_analyza/p26-a-overeni.py --plne` → **«PLNE» kontrol, 0 chyb** |
| **A** | **Důkaz, že i tohle měřidlo umí spadnout** — tři mutace **v KOPIÍCH**, každá s **diferenciálem** (originál spadne / oslabená kopie projde) | `_analyza/p26-b-mutace.py` → **26 kontrol, 0 chyb** |
| **B1** | **Oprava brány, která tiše zúžila rozsah z 99 řádků Hxx na 1** (nález P25-K) | `_analyza/ov-g-neovereno.py` → rozsah **1 → 99**, vypisuje KTERÉ soubory otevřel; fixtury: `NEOVĚŘENO` → `exit 1`, prázdno → `NEMĚŘENO` |
| **C** | Brány po sobě (**inventář → `g3` → `validate-all`**, ne současně) | `g3` → **49 bran, 1 deklarovaný nenulový exit** (`zadání kontrola`), **exit 0** · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |

### 56.2 Nálezy P26 (každý doložený měřením)

1. **P25 NETVRDILA PRAVDU O TOM, CO ZMĚŘILA — a nebyla to lež, byla to
   MEZERA.** §55 (bod 9 i tabulka 55.1) tvrdí, že test tiku volá `POST /task`,
   `/game` a `/game/active`. **P25 to ale nedoložila:** její jediná zarážka byla
   v **ROUTERU** a mířila na pět **jiných** endpointů (`/poll`…`/roadmap/reset`)
   — v jejích **42 červených kontrolách nejsou žádné `T:`/`U:`/`V:`/`W:`**.
   P26 to změřila zarážkou **UVNITŘ HANDLERU** (tři mutace živého zdroje,
   v `try/finally` a s ověřením hashe před i po):
   `/task` → **9 červených `T:`** (mj. `T: /task odpoví 200`),
   `/game` → **6 červených `U:`**,
   `/game/active` → **5 červených `V:`** —
   a kontrolní `A: /tick odpoví 200` zůstala **pokaždé zelená**.
   **Poučení: „test endpoint volá" se dokazuje zarážkou V HANDLERU, ne
   v routeru** — routerová zarážka zapne i kontroly, které s handlerem nesouvisí.
2. **VÁZANÉ HODNOTY SE OPRAVDU MĚŘÍ.** V **KOPII** testu se vypnul záznam
   `bind()` → **12 červených** (T: 5, V: 2), konkrétně ``T: `title` jde do
   INSERTu`` a ``V: do DB jde `active = 0` (ne 1)``. Kdyby test tvrdil jen
   **tvar** SQL (`log`), zůstaly by zelené — přesně past „přítomnost ≠ chování".
3. **NÁLEZ P25-K JE PRAVDA A JE OPRAVENÝ.** Verze měřidla z `HEAD` čte
   **1 řádek Hxx** (`HANDOFF.md`), živá po opravě **99** (1 + 98
   z `_archiv/HANDOFF-HISTORIE.md`) → zelená byla **nad 1 % rozsahu**.
   Oprava: zdroje se **odvozují** (ne zapečený seznam), **vypisují se po
   souborech**, počítá se i rozsah **mimo** ně (**139** řádků v **7** zmrazených
   kopiích — záměrně se nečtou, jinak by se týž nález počítal víckrát, past
   H93/H98) a **prázdný rozsah je `NEMĚŘENO` (`exit 1`)**.
4. **MĚŘIDLO MĚLO LŽIVÝ POPISEK.** `ov-g-neovereno.py` tvrdil „hledám
   `NEOVĚŘENO` **ve sloupci Stav**" — **tabulky Hxx žádný sloupec `Stav`
   nemají** (2 buňky v `HANDOFF.md`, 3 v archivu: `# | Nález | Doklad`).
   Hledalo se **kdekoli na řádku**, takže by chytilo i **CITACI** („bylo
   NEOVĚŘENO, dnes APLIKOVÁNO"). Dnes je takových řádků **0** (naměřeno ve
   všech **9** souborech s tabulkou Hxx) — ale popisek je opravený a rozpad na
   buňky se vypisuje.
5. **ČÍSLA §55 SEDÍ — VŠECHNA.** Znovu naměřeno **spuštěním**, ne čtením:
   `p25-a --plne` **53/0** · `p25-b-mutace` **27/0** · `test-tick-offline`
   **146/0** · `tick-mutace` **20 vrat / 41/0** · `g3` **49 bran** ·
   `p24-b-mutace` **17/0** · `handoff-kontrola-uplnost` **83/83** ·
   `kronika-kontrola` **SEDÍ**.
6. **JEDNO ČÍSLO NESEDÍ — A JE ZE ZADÁNÍ, NE Z §55.** Zadání P26 §2.3 tvrdilo
   `over-dokumentaci.py -> 67 kontrol`; **živé měření je 64/0**. Příčina je
   **naměřená, ne odhadnutá**: brána přičítá **+1 za každé volání, jehož CESTA
   obsahuje „skills"** (frontmatter skillu); commit `92aa80a` (optimalizace KB)
   přesunul **tři** bloky z `SKILLS/orchestra` do `PROVOZ`/`BRANY_HRY`, takže
   `52 + 15 = 67` se změnilo na `52 + 12 = 64`. **Není to ztráta pokrytí**
   (obsah se přesunul s blokem) — je to **číslo bez svého běhu** (past
   `AGENTS.md`). Zadání je opravené a měřidlo P26 to číslo teď **hlídá**.
7. **ZADÁNÍ P25 BYLO ZASTARALÉ VE STAVU.** Tvrdilo „práce P25 je v pracovním
   stromě (necommitnutá)" a `HEAD = origin/main = 92aa80a`; **živě** bylo
   `HEAD = ef58327` (P25 svou práci **commitla**) a `origin/main..HEAD = 1`.
   **Hlavička zadání je SNAPSHOT, ne stav.**
8. **NEÚSPĚŠNÝ BĚH MĚŘIDLA VYPADÁ JAKO NÁLEZ.** Můj vlastní přepínač `--vystup`
   čtl `args` v bloku `__main__`, kde **není** (je lokální v `main()`) →
   `NameError` → měřidlo končilo **`exit 1` i s 0 chybami**. Odhalil to až
   **diferenciál** v `p26-b-mutace.py`. **Poučení: verdikt se čte z ČÍTAČE, ne
   z exit kódu** — a `exit != 0` není totéž co „našlo vadu".
9. **VLASTNÍ ÚPRAVA SEZNAMU TIŠE SMAZALA DVĚ POLOŽKY.** Při přidávání sond P26
   do `PRESKOCIT` (`p20-d-doklady.py`) jsem **přepsal řádek s `p24-sonda-site.py`
   a `p24-sonda-m2.py`** → z `PRESKOCIT` **vypadly**. Chytila to **cizí brána**
   `p25-a-overeni.py` A6 („sondy nejsou v PRESKOCIT dávky") — přesně to, k čemu
   nezávislé měřidlo je. **Poučení: seznam se PŘIDÁVÁ, nepřepisuje.**
10. **ZASTARALÝ INVENTÁŘ SE NEDEKLARUJE — a shodí ho i JEDEN NOVÝ SOUBOR.**
    Naměřeno ostře: po přegenerování inventáře stačilo **přidat jeden `.txt`**
    do `_analyza/` a `n1-over-inventar` spadl (`exit 2`); v `g3` se pak
    `C2: mutace N1` ocitl v „brány bez čítače" (správně odmítá měřit nad
    zastaralým inventářem). **A druhý, dražší důvod:** otisk vstupů
    (`KOREN_REPA = {"orchestra": WS, "games/uo-shadows": HRA}`) počítá **I DRUHÉ
    REPO** — takže **zápis souběžné session do hry zneplatní inventář uprostřed
    běhu**. Náprava je vždy **přegenerovat jako POSLEDNÍ krok** a doklady
    pojmenovat podle vylučovacího vzoru (`_analyza/*-vystup.txt`, který
    `ARTEFAKT_RE` vylučuje z otisku).
11. **SANDBOX ZNOVU ODEMKL ZÁPIS PODPROCESŮM — a tentokrát to ZAMRZLO.**
    Podproces nešel zapsat do **žádného** podadresáře workspace; `git fetch`
    padal na `.git/FETCH_HEAD: Permission denied` a sonda nad `_analyza`
    **čekala** (žádný `PermissionError`, jen ticho), dokud ji nástroj nepřesunul
    na pozadí. `write` (harness) přitom do podadresáře zapsal. Pomohlo
    **přepnutí session na plný přístup** — **stav prostředí, ne vada skriptu**
    (skill `dsh-prostredi` §4e).
12. **DO HRY ZAPISOVALA SOUBĚŽNÁ SESSION.** Mezi 15:50 a 16:02 +02:00 přibyly
    v `uo-shadows` **tři commity** (`6796188`, `43a2004`, `125b062`,
    **nepushnuté**) a netrackovaný `_acl-recovery/`. **Důsledek pro měření:**
    `p24-a-overeni.py` má proto **99/3** (tři červené `A8`: HEAD ≠ `44dd454`,
    strom není čistý, 3 nepushnuté commity) místo dřívějšího **99/1** — a to
    **není vada měřidla**: A8 měří **živý stav hry** (P25 to zapsala jako
    „dobová kotva"). **Na práci té session se nesahalo.**

### 56.3 Živý stav při zápisu (7. 10. 2026, ~16:2x +02:00)

```
orchestra: HEAD ef58327 · origin/main 92aa80a · nepushnutých commitů 1 (práce P25)
hra:       HEAD 125b062 · origin/main 932dc6f · nepushnutých 3 (SOUBĚŽNÁ session,
           15:50/15:58/16:02) · strom není čistý (netrackovaný `_acl-recovery/`)
živá služba: /health → ok=true ready=1 running=0 games=1 · targets[0] forge.ok=false,
             selhani_v_rade=20, poslední běh run_number 323 (failure, 12:16:33Z)
             /tick → spusteno: 0 úloh; watchdog: 0 ohlášeno (prah 3)
brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0
           (naměřeno po přegenerování inventáře; viz nález 10 výše)
p24-a:     99/3 — všechny tři červené jsou `A8` (dobový stav hry), 99/2 pokud
           souběžná session svou práci pushne
```

### 56.4 Co čeká na tebe (uživatel)

- **PUSH — rozhodnutí uživatele.** P26 **commitla, nepushla**; `origin/main..HEAD`
  bude **2** (P25 + P26). P26 měnila **jen `_analyza/` a dokumenty**, žádný
  soubor pod `conductor/**` — **deploy živé služby to tedy nemění** (ověř
  `git diff --name-only origin/main..HEAD`). Cesta zpět: `git reset --soft`.
- **`_acl-recovery/` v `uo-shadows`** je **cizí, netrackovaný** artefakt
  souběžné session (ACL oprava, 15:41). **Nemažu ho** a **necommituju** —
  patří té session.
- **`HANDOFF.md` §6 je ZÁZNAM z 2. 10. 2026**, ne seznam živých bran
  (má předpřesunové cesty `orchestra\tools\…` a čísla 63/12). Autorita je
  `BRANY` v `_analyza\g3-brany.py`.
- **B4 na živé službě** (`/game/active {active:false}` → `games=0`, žádný
  dispatch) — čeká na výslovné **„ano"**, protože **dočasně zastaví orchestra**.

### 56.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p26-a-overeni.py --plne   # A1-A6: zarážky v handleru, vazby, g3
python _analyza\p26-b-mutace.py           # umí to spadnout? 26 kontrol, 0 chyb
python _analyza\ov-g-neovereno.py         # rozsah 99 řádků Hxx, 0 NEOVĚŘENO
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json  # POSLEDNÍ
python _analyza\g3-brany.py               # 49 bran, 1 deklarovaný exit, exit 0
node tools\validate-all.mjs               # VŠE V POŘÁDKU
python _analyza\p25-a-overeni.py --plne   # 53/0
python _analyza\p25-b-mutace.py           # 27/0
python _analyza\p24-a-overeni.py          # 99/3 (A8 = stav hry, 99/2 po pushi)
node tools\test-tick-offline.mjs          # 146/0
python _analyza\tick-mutace.py            # 20 vrat / 41/0
```
"""

# ── 2) KRONIKA: řádek 41 ────────────────────────────────────────────────────
RADEK_41 = (
    "| **41** | **7. 10. 2026** (13:1x – 16:2x +02:00) | "
    "**ověřovací (Úkol A) + akční (Úkol B1)** | **Přeměřit práci P25 VLASTNÍM "
    "měřidlem — a opravit bránu, která tiše zúžila rozsah z 99 řádků na 1.** "
    "Zadání P26 §2.1: záznamy P25 psal autor, který si je sám ověřoval "
    "(„autor není nezávislý reviewer“). Provedeno: **A1–A6 vlastním postupem** "
    "(`_analyza/p26-a-overeni.py --plne`) + **důkaz, že to měřidlo umí spadnout** "
    "(`p26-b-mutace.py`, **26/0**, tři mutace v KOPIÍCH s diferenciálem) a "
    "**Úkol B1** — oprava `ov-g-neovereno.py` (rozsah **1 → 99** řádků Hxx). "
    "| **Brány:** `g3` **49 bran**, 1 deklarovaný nenulový exit (`zadání "
    "kontrola`), **exit 0** · `validate-all` **VŠE V POŘÁDKU** · "
    "`handoff-kontrola-uplnost` **83/83** · `kronika-kontrola` **SEDÍ** · "
    "`ov-g-neovereno` **0 NEOVĚŘENO nad 99 řádky** · `p25-a --plne` **53/0** · "
    "`p25-b-mutace` **27/0** · `test-tick-offline` **146/0** · `tick-mutace` "
    "**20 vrat / 41/0** · `over-dokumentaci` **64/0** · `over-skilly` **13/0** · "
    "**A2 POPRVÉ DOLOŽENO ZARÁŽKOU V HANDLERU:** `/task` → **9 červených `T:`**, "
    "`/game` → **6 `U:`**, `/game/active` → **5 `V:`**, a kontrolní "
    "`A: /tick odpoví 200` **pokaždé zelená** (P25 měřila jen router!) · "
    "**A3:** vypnutý záznam `bind()` v KOPII testu → **12 červených** (T: 5, V: 2) "
    "| **—** | **Nálezy a poučení:** (1) **P25 nedoložila, co tvrdila:** §55 bod 9 "
    "říká, že test volá `/task`, `/game`, `/game/active` — její zarážka ale byla "
    "jen v **ROUTERU** pro pět jiných endpointů a v 42 červených nejsou žádné "
    "`T`/`U`/`V`/`W`. **„Test endpoint volá“ se dokazuje zarážkou V HANDLERU.** "
    "(2) **Nález P25-K je pravda a je opravený:** verze měřidla z `HEAD` čte "
    "**1** řádek Hxx, živá **99** (1 + 98 v `_archiv/HANDOFF-HISTORIE.md`) → "
    "zelená byla nad **1 % rozsahu**; oprava odvozuje zdroje, **vypisuje, které "
    "soubory otevřela**, hlásí rozsah **mimo** ně (139 řádků v 7 zmrazených "
    "kopiích) a **prázdný rozsah je `NEMĚŘENO` (`exit 1`)**. "
    "(3) **Měřidlo mělo lživý popisek:** tvrdilo „hledám NEOVĚŘENO ve sloupci "
    "Stav“ — **takový sloupec neexistuje** (2–3 buňky), hledalo se kdekoli na "
    "řádku, takže by chytilo i CITACI; dnes 0 takových řádků. "
    "(4) **Jedno číslo NESEDÍ a je ze ZADÁNÍ:** `over-dokumentaci` hlásilo 67, "
    "živě **64** — brána přičítá +1 za volání, jehož CESTA obsahuje „skills“, "
    "a commit `92aa80a` přesunul tři bloky ze `SKILLS/orchestra` do "
    "`PROVOZ`/`BRANY_HRY` (52+15=67 → 52+12=64). Není to ztráta pokrytí, je to "
    "**číslo bez svého běhu**. (5) **Neúspěšný běh měřidla vypadá jako nález:** "
    "můj přepínač `--vystup` čtl v `__main__` proměnnou `args`, která je lokální "
    "v `main()` → `NameError` → **`exit 1` i s 0 chybami**; odhalil to až "
    "diferenciál. **Verdikt se čte z ČÍTAČE, ne z exit kódu.** "
    "(6) **Vlastní úprava seznamu tiše smazala dvě položky:** při přidávání sond "
    "do `PRESKOCIT` vypadly `p24-sonda-site.py` a `p24-sonda-m2.py` — chytila to "
    "**cizí** brána `p25-a` A6. **Seznam se přidává, nepřepisuje.** "
    "(7) **Zastaralý inventář shodí i JEDEN nový soubor** (naměřeno: přidání "
    "`.txt` → `n1-over-inventar` `exit 2`); a otisk počítá **I DRUHÉ REPO** "
    "(`KOREN_REPA`), takže **zápis souběžné session do hry zneplatní inventář "
    "uprostřed běhu** — náprava je přegenerovat jako POSLEDNÍ krok a doklady "
    "pojmenovat `*-vystup.txt` (vylučovací vzor). (8) **Sandbox znovu odemkl "
    "zápis podprocesům a tentokrát to ZAMRZLO** (žádný `PermissionError`, jen "
    "ticho; `git fetch` padal na `.git/FETCH_HEAD`) — pomohl plný přístup; "
    "**stav prostředí, ne vada skriptu** (skill `dsh-prostredi` §4e). "
    "**Co zůstává:** **sedm endpointů bez testu** (`/health`, `/queue`, "
    "`/roadmap`, `/failed`, `/status`, `/workers`, `/games` — naměřeno: nevolá je "
    "NIKDO); rozhodnutí o `.gitattributes` (P24-B); slepé místo `over-skilly` "
    "(fáze C, má rozdělanou práci souběžné session); **B4 ověřit živě** a **B3b "
    "zapnout strop**; a **push P25+P26** (rozhodnutí uživatele; P26 nemění "
    "`conductor/**`, takže deploy nic nemění) |"
)

# ── 3) KRONIKA: §2.19 ───────────────────────────────────────────────────────
ODDIL_219 = r"""### 2.19 Nálezy z P26 (7. 10. 2026) — zarážka v HANDLERU a brána, která měřila 1 % rozsahu

**Vznikly tím, že se PRÁCE P25 PŘEMĚŘILA JINÝM MĚŘIDLEM** (ne čtením §55), a že
se opravila brána, kterou sama P25 **označila za zúženou**. Záznam: `HANDOFF.md`
**§56**; měřidlo: `_analyza/p26-a-overeni.py` a jeho mutační důkaz
`_analyza/p26-b-mutace.py` (**26/0**, tři mutace v KOPIÍCH s diferenciálem).

| # | Co hrozilo / co se tvrdilo | Co naměřeno | Stav |
|---|---|---|---|
| **P26-A** | „P25 doložila, že test tiku volá `/task`, `/game` a `/game/active`.“ | **Nedoložila.** Její jediná zarážka byla v **ROUTERU** (pět jiných endpointů: `/poll`…`/roadmap/reset`) a v **42 červených kontrolách nejsou žádné `T:`/`U:`/`V:`/`W:`** | **DOLOŽENO P26** zarážkou **V HANDLERU**: `/task` → **9 červených `T:`**, `/game` → **6 `U:`**, `/game/active` → **5 `V:`**, kontrolní `A: /tick odpoví 200` pokaždé **zelená**. **Routerová zarážka nestačí** — zapne i kontroly, které s handlerem nesouvisí |
| **P26-B** | „Když test tvrdí, že hodnota jde do D1, měří to.“ | V **KOPII** testu se vypnul záznam `bind()` → **12 červených** (T: 5, V: 2), konkrétně ``T: `title` jde do INSERTu`` a ``V: do DB jde `active = 0` (ne 1)`` | **POTVRZENO**: test měří **vázané hodnoty**, ne jen tvar SQL (`overovani`: přítomnost ≠ chování) |
| **P26-C** | „`ov-g-neovereno.py` čte celý záznam, když hlásí 0× NEOVĚŘENO.“ | Verze z `HEAD` čte **1 řádek Hxx** (`HANDOFF.md`); zbylých **98** je v `_archiv/HANDOFF-HISTORIE.md`. Zelená byla nad **1 % rozsahu** — a **nikdo to nepoznal**, protože měřidlo sice vypsalo čítač, ale **ne rozsah** | **OPRAVENO (B1)**: zdroje se odvozují a **vypisují po souborech**, rozsah **mimo** ně se hlásí (139 řádků v 7 zmrazených kopiích), **prázdný rozsah = `NEMĚŘENO` (`exit 1`)** |
| **P26-D** | „Měřidlo hledá `NEOVĚŘENO` ve sloupci Stav.“ | **Takový sloupec NEEXISTUJE** — tabulky Hxx mají 2 buňky (`HANDOFF.md`) nebo 3 (`# \| Nález \| Doklad`). Hledalo se **kdekoli na řádku**, takže by chytilo i **CITACI** („bylo NEOVĚŘENO, dnes APLIKOVÁNO“) | **POPISEK OPRAVEN** + rozpad na buňky se vypisuje. Dnes je takových řádků **0** (naměřeno ve všech **9** souborech s tabulkou Hxx) |
| **P26-E** | „Zadání je stav.“ | Zadání P25 tvrdilo „práce P25 je v pracovním stromě (necommitnutá)“ a `HEAD = 92aa80a`; **živě** `HEAD = ef58327` a `origin/main..HEAD = 1`. A zadání P26 §2.3 tvrdilo `over-dokumentaci -> 67`, **živě 64** | **SNAPSHOT, NE STAV.** Číslo 67 vzniklo takto: brána přičítá **+1 za volání, jehož CESTA obsahuje „skills“**, a commit `92aa80a` přesunul **tři** bloky ze `SKILLS/orchestra` do `PROVOZ`/`BRANY_HRY` → `52+15=67` na `52+12=64`. **Není to ztráta pokrytí**, je to číslo bez svého běhu; v zadání opraveno a **měřidlo P26 to hlídá** |
| **P26-F** | „Když měřidlo skončí `exit 1`, našlo vadu.“ | Můj přepínač `--vystup` čtl v `__main__` proměnnou `args` (lokální v `main()`) → `NameError` → měřidlo končilo **`exit 1` i s 0 chybami** | **ODHALENO DIFERENCIÁLEM** (oslabená kopie „prošla“ jen zdánlivě). **Verdikt se čte z ČÍTAČE, ne z exit kódu** |
| **P26-G** | „Seznam v cizím souboru přepíšu a nic se nestane.“ | Při přidávání sond P26 do `PRESKOCIT` (`p20-d-doklady.py`) jsem **přepsal řádek** a `p24-sonda-site.py` + `p24-sonda-m2.py` z něj **vypadly** | **CHYTILA CIZÍ BRÁNA** (`p25-a-overeni.py` A6: „sondy nejsou v PRESKOCIT“). **Seznam se PŘIDÁVÁ, nepřepisuje** — a kdo mění cizí měřidlo, ať ho hned spustí |
| **P26-H** | „Zastaralý inventář se dá deklarovat jako očekávaný stav.“ | Po přegenerování inventáře stačilo **přidat JEDEN `.txt`** do `_analyza/` a `n1-over-inventar` spadl (`exit 2`); v `g3` se pak `C2: mutace N1` ocitl v „brány bez čítače“ (správně odmítá měřit nad zastaralým inventářem) | **NEDEKLAROVAT — PŘEGENEROVAT.** A pozor: otisk vstupů počítá **I DRUHÉ REPO** (`KOREN_REPA`), takže **zápis souběžné session do hry zneplatní inventář uprostřed běhu**; doklady patří na `*-vystup.txt` (vylučovací vzor) |
| **P26-I** | „Měřidlo, které nikdo nepoužije, je neškodné.“ | Dvě vady měřidel P25/P24 se projevily **jen tím, že je P26 spustila**: `p25-a` A6 odhalil smazané položky `PRESKOCIT` a `p24-a` A8 ukázal, že do hry zapsala **souběžná session** | **NEZÁVISLÉ SPUŠTĚNÍ JE JEDINÁ OBRANA.** Záznam P25 byl v číslech **pravdivý**, ale v **důkazu** měl mezeru (A2) |
| **P26-J** | „Když podproces nemůže zapsat soubor, spadne na `PermissionError`.“ | V `workspace-write` nešlo zapsat podprocesem do **žádného** podadresáře workspace — a tentokrát to **ZAMRZLO** (ticho, žádná chyba); `git fetch` padal na `.git/FETCH_HEAD: Permission denied`, `write` (harness) přitom zapsal | **STAV PROSTŘEDÍ, NE VADA SKRIPTU** — pomohlo **přepnutí session na plný přístup**; past ve skillu `dsh-prostredi` **§4e** |
| **P26-K** | „Do hry teď nikdo nepíše (je pozastavená).“ | **Píše.** Mezi 15:50 a 16:02 +02:00 přibyly v `uo-shadows` **tři commity** (`6796188`, `43a2004`, `125b062`, **nepushnuté**) a netrackovaný `_acl-recovery/`; `p24-a` proto hlásí **99/3** (tři červené `A8`) místo **99/1** | **ZAPSÁNO JAKO STAV** (`A8` měří živý stav hry — P25 to zapsala jako „dobová kotva“). **Na práci té session se nesahalo**; `_acl-recovery/` se needituje, necommituje a nemaže |
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
print("P26 — zápis záznamů (HANDOFF §56, KRONIKA řádek 41 + §2.19)")
print("=" * 78)

# ── HANDOFF ─────────────────────────────────────────────────────────────────
h_text = H.read_bytes().decode("utf-8")
k("\r" not in h_text, "HANDOFF má LF")
k("## 55. P25 —" in h_text, "§55 (záznam P25) zůstal")
if "## 56. P26 —" in h_text:
    print("  OK    §56 už v HANDOFFu je — nepřidávám")
    kontrol += 1
else:
    H.write_bytes((h_text.rstrip("\n") + "\n" + ODDIL_56).encode("utf-8"))
    h_text = H.read_bytes().decode("utf-8")
    k("## 56. P26 —" in h_text, "§56 vložen na KONEC (nic se nepřepisovalo)")
k("§54" in h_text and "NEZÁVISLÉ PŘEMĚŘENÍ" in h_text, "§54 zůstal")
k("§55" in h_text and "TESTOVÁNÍ ZAPISUJÍCÍCH ENDPOINTŮ" in h_text, "§55 zůstal")
k("§53" in h_text and "NASZENO A OVĚŘENO ŽIVĚ" in h_text, "§53 zůstal")
k("watchdog: 0 ohlášeno (prah 3)" in h_text, "§53 nese své PŮVODNÍ živé měření")
k(not H.read_bytes().startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")
# Čísla, která musí být v dokumentu ZAPSANÁ (čte je A4 měřidla P25 i P26):
for cislo in ("53/0", "27/0", "146/0", "41/0", "20 vrat", "49 bran",
              "99/3", "99/2", "83/83", "64/0", "26 kontrol"):
    k(cislo in h_text, f"HANDOFF tvrdí naměřené `{cislo}`")

# ── KRONIKA ─────────────────────────────────────────────────────────────────
puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF")
k("### 2.18 Nálezy z P25" in text, "§2.18 (nálezy P25) zůstal")

zmena = False
if any(r.startswith("| **41** |") for r in radky):
    print("  OK    řádek 41 už v kronice je — nevkládám")
    kontrol += 1
else:
    i40 = next((n for n, r in enumerate(radky) if r.startswith("| **40** |")), None)
    k(i40 is not None, "kotva: řádek session 40")
    if i40 is not None:
        konec = "\n" if radky[i40].endswith("\n") else ""
        radky.insert(i40 + 1, RADEK_41 + konec)
        zmena = True
        k(any(r.startswith("| **41** |") for r in radky), "řádek 41 vložen ZA řádek 40")

if "### 2.19 Nálezy z P26" in text:
    print("  OK    §2.19 už v kronice je — nevkládám")
    kontrol += 1
else:
    i3 = next((n for n, r in enumerate(radky) if r.startswith("## 3. ")), None)
    k(i3 is not None, "kotva: nadpis §3")
    if i3 is not None:
        radky.insert(i3, ODDIL_219 + "\n")
        zmena = True
        k(any("### 2.19 Nálezy z P26" in r for r in radky), "§2.19 vložen PŘED §3")

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
k("| **39** |" in t2, "řádek 39 zůstal (nic se nepřepsalo)")
k("| **40** |" in t2, "řádek 40 zůstal")
k("| **41** |" in t2, "dokument obsahuje řádek 41")
k("### 2.18 Nálezy z P25" in t2, "§2.18 zůstalo")
k("### 2.19 Nálezy z P26" in t2, "dokument obsahuje §2.19")
# ⚠ SOUHRN SE NEPŘEPOČÍTÁVÁ (omyly se od 6. 10. 2026 nevedou).
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t2,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN (omyly se nevedou)")
# OMYLY = „—" (od 6. 10. 2026 se nevedou) — řádek 41 to musí mít.
k(re.search(r"^\| \*\*41\*\* \|.*\| \*\*—\*\* \|", t2, re.M) is not None,
  "řádek 41 má ve sloupci omylů `—`")

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

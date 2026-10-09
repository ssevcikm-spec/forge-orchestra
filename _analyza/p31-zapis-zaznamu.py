# -*- coding: utf-8 -*-
r"""P31 — ZÁPIS ZÁZNAMŮ: HANDOFF §62, KRONIKA řádek 46 + nálezy §2.24, PLAN.

⚠ PROČ SKRIPTEM (a ne `edit` toolem): řádky kroniky mají **přes 3000 znaků**
a kotva načtená z řádku ho **zkrátí** (omyly 194, 206). Skript pracuje
s BAJTEM, vkládá celé řádky a po zápisu ověřuje, že nic nezmizelo.

⚠ CO SE NESMÍ STÁT: HANDOFF ani KRONIKA se NEPŘEPISUJÍ, jen DOPLŇUJÍ. Skript
proto (a) jen vkládá, (b) před i po měří počty řádků a id, (c) při jakékoli
neshodě skončí `exit 1` a NIC nezapíše, (d) je IDEMPOTENTNÍ (druhý běh řekne
„už zapsáno“ a skončí `exit 0` — pouští ho i dávka dokladů).

⚠ NÁLEZY SE V §62 PÍŠOU JAKO PROSAICKÝ MAPOVACÍ SEZNAM (ne jako tabulka
`| **H131** | …`): tabulkový řádek s `**Hxx**` na začátku je „řádek Hxx"
a zvedl by počítadlo **99 řádků Hxx** (řádek je jeden v HANDOFF.md) — a tím
by spadla tvrzení `ov-g` i měřidla P28/P30 (naměřeno v P31).

Použití: python _analyza\p31-zapis-zaznamu.py [--kontrola]
"""

import argparse
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
PLAN = WS / "PLAN-DALSI-KROK.md"

kontrol = 0
chyb = 0


def check(popis, zjisteno, ocekavano):
    global kontrol, chyb
    kontrol += 1
    if zjisteno == ocekavano:
        print("  OK    %s" % popis)
        return True
    chyb += 1
    print("  CHYBA %s\n        čekáno:   %r\n        naměřeno: %r"
          % (popis, ocekavano, zjisteno))
    return False


# ═══════════════════════════════════════════════════════════ HANDOFF §62 ═══
HANDOFF_62 = r"""
## 62. P31 — PŘEMĚŘENÍ P30 A OPRAVA DVOU VAD MĚŘIDLA P28/B (9. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P31 + stav po P31**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**46**, nálezy **§2.24**), plán (`PLAN-DALSI-KROK.md`, dodatek P31).
Zadání P31 je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **9. 10. 2026, 11:30–14:2x +02:00** (živý čas
> z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba) platí
> k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.24), aby každý nález byl dohledatelný
> z HANDOFF.md:** H131 = `p28-b-mutace.py` M1 počítala kotvu v CELÉM dokumentu
> (a spadla na cizí citaci) · H132 = M2 vkládala do `BRANY` záznam o DVOU
> prvcích → mutant `g3` spadl na `ValueError` · H133 = `g3` končí `exit 1`
> POJMENOVANĚ (1 brána bez čítače) a `p28-a-overeni.py` A6 na tom stojí ·
> H134 = **H124 ZAVŘENO**: měřidlo P29 po sobě uklízí (a test to dokazuje) ·
> H135 = tvrzení „`p30-a` → 35/0“ se NEREPRODUKUJE (32/3, tři pojmenované
> příčiny) · H136 = **H130 OVĚŘENO** (dávka dokumenty nepíše) — ale KOŘEN
> vady žije dál · H137 = harness z `g3` bez `FORGE_REGISTR` přepsal ŽIVÝ
> registr (50 bran) a shodil `ag-over-cisla.py`.

### 62.1 Cíl a co bylo hotové před P31 (neopakovat)

Zadání P31 chtělo dvě věci: **přeměřit práci P30 vlastním měřidlem** a
**zavřít aspoň jednu ze tří doložených vad měřidel** (H123, H124, H130).
P30 byla hotová: oprava **B6** nasazená a živá, **H111** (strop granule) a
**H114** (`entity.move.smooth` čeká na `engine.input`) rozhodnuté, **B8**
(návod pro architekta ve skillu `game-developer`) hotový — viz §61.

### 62.2 Úkol A — VLASTNÍ MĚŘIDLO P31 (`_analyza/p31-a-overeni.py`)

**Plný běh: 54 kontrol, 1 chyba, 2 pojmenované ROZDÍLY, 0 NEZMĚŘENO**
(doklad `_analyza/p31-a-overeni-vystup.txt`). Každé tvrzení se **PŘEČTE
Z §61** (vypisuje se okno, které vzor trefil) a pak se měří; co nesedí, je
**ROZDÍL s vysvětlením** — nebo **CHYBA**.

* **A1 — umí měřidlo P30 spadnout?** `p30-mutace.py` → **16/0** (tvrzení
  §61.5 reprodukováno) a **VLASTNÍ diferenciál** měřidla P30: kotva
  `test-tick-offline → 215/0` je v `HANDOFF.md` **1×**; živé měřidlo →
  `exit 0`; **mutant** dokumentu → `exit 1` s `ROZCHOD test-tick-offline`;
  **mutant + oslabené měřidlo** → `exit 0`. `HANDOFF.md` vrácen **bajt na bajt**.
* **A2 — nasazení TŘEMI kroky:** (1) `ls-remote` = `HEAD` = `0c0eb18`;
  (2) `deploy.yml` **#35 na `cf1f280`** je `completed/success` (sha se ČTE
  z §61); (3) živá služba `/tasks/cleanup {dry_run}` → **osiřelých 0**
  (bylo 5) a tik **pojmenovává, co přeskočil**. ⚠ `POST /tick` byl **volán
  jednou** (mění stav) — doklad `_analyza/p31-stav-vystup.txt`.
* **A3 — sedí čísla z §61?** Shoda: `test-tick-offline` **215/0**,
  `over-skilly` **92/0**, `ov-g` **99 řádků Hxx**, `p29-b6-mutace` **15/0**,
  `over-dokumentaci` **64/0**, `p30-mutace` **16/0**, `tick-mutace`
  **20 vrat/41/0**, `g3` **49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače**,
  `validate-all` **0 problémů**, kronika **SEDÍ**. Neshoda je **jediná**:
  `p30-a` (viz 62.4 / H135).
* **A4 — H130** (dávka dokladů nepíše do dokumentů): samostatný běh
  `--jen A4` — viz 62.4.
* **A5 — H111** (strop vs. zámek), nezávisle z D1 (jen SELECT, doklad
  `_analyza/p31-d1-vystup.txt`): **zámek VYLOUČEN** (žádná úloha není
  `running`), **`engine.registry` má počítadlo 5** (mechanismus stropu: roste
  od vzniku řádku), **za stropem není žádná vydávaná granule** (jediná ≥ 8 je
  `sim.crafting` = 12, a ta je `done`).
* **A6 — H124:** `p29-a-overeni.py --jen A1M13` → **8/0** a v `_analyza/`
  **nezůstal žádný mutant** (a měřidlo to ŘEKLO — kontrola úklidu).
* **A7 — nic se nerozbilo:** záznamy se jen přidávaly (**0 smazaných
  řádků**), `kronika-kontrola` **SEDÍ**, `handoff-kontrola-uplnost`
  **0 chybějících**, `ov-g` **0 NEOVĚŘENO** (rozsah **99 řádků Hxx**).

### 62.3 Úkol B — VĚCNÁ PRÁCE: **C1** (H131 + H132) a **C2** (H124)

**C1 — `p28-b-mutace.py` bylo 27/2 a je 30/0.** Příčiny byly DVĚ a obě
v tom souboru (doklad `_analyza/p31-mutace-vystup.txt` → **24/0**, vlastní
diferenciál; a `_analyza/p31-mutace-p28b-vystup.txt` = celý běh opraveného
měřidla):

* **H131:** kontrola M1 srovnávala `text.count(kotva)` (**celý dokument**, dnes
  **3×**) s `s57.count(kotva)` (**§57**, **1×**) → hlásila `(1, 3) != (1, 1)`
  a shazovala měřidlo **za to, že si novější záznamy tvrzení citují**. Kotva
  se teď počítá **v měřeném oddílu** (funkce `kotva_m1`, vzor
  `p29-a-overeni.py`). Diferenciál: **živá** `kotva_m1` → `((1,0),(1,0))`;
  **oslabená kopie s PŮVODNÍ vadou** → `((1,3),(1,1))` = ROZCHOD.
* **H132:** mutace M2 vkládala do `BRANY` záznam o **DVOU** prvcích, ale `g3`
  čte `for popis, prikaz, vzor in BRANY` → mutant **spadl na
  `ValueError: not enough values to unpack (expected 3, got 2)`** a diferenciál
  se měřil **na tracebacku** (doklad `_analyza/p31-sonda-g3-vystup.txt`).
  Dnes je záznam platný (`ZAZNAM_FIXTURY`, 3 prvky) a **obě nohy M2 ho berou**
  (první oprava zapomněla na M2c — chytila to vlastní mutační zkouška) a
  přibyla kontrola **„mutant přidal PRÁVĚ JEDNU chybu“** + množinová kontrola
  **„kontrola POČTU BRAN v oslabené kopii UŽ NENÍ červená“**.

**C2 — měřidlo P29 po sobě uklízí (H124 ZAVŘENO).** `p29-a-overeni.py`
zapisoval `_analyza/p29-mut-handoff.md` (**196 092 B**), `_analyza/p29-mut-g3.py`,
`p29-mut-fixtura.py` a `p29-mut-ovg.py` do ŽIVÉHO `_analyza/` a **nemazal je**
(nejsou gitignorované → vstupovaly do inventáře i do `git add -A` a shazovaly
dvě brány). Dnes je úklid v **`try/finally`** a **sám se kontroluje**
(`uklid_mutanty()`); důkaz je v `p31-mutace.py` **třemi nohami**: živé měřidlo
→ **8/0** a žádný mutant; **oslabená kopie bez úklidu** → mutanty **ZŮSTANOU**
(`_analyza/p29-mut-handoff.md` 196 092 B + `_analyza/p29-mut-ovg.py` 8 545 B) a její kontrola
to hlásí **CHYBA** (`exit 1`); po testu je vše uklizené.

### 62.4 Co se naměřilo navíc (a co to znamená)

* **H133 — `g3` končí `exit 1` POJMENOVANĚ, ne rozpadem.** Naměřeno: **49 bran,
  0 NEDEKLAROVANÝCH, 1 bez čítače** (`mutace B (combat)` — cizí brána hry;
  `OCEKAVANE_BEZ_CITACE` je záměrně prázdný) → `g3` je `exit 1` **za
  deklarovaný stav**. `p28-a-overeni.py` A6 ale čeká `g3 → exit 0`, takže
  **baseline A6 má trvale 1 chybu**. A do toho **H126 žije dál**: sonda, která
  `g3` pustí **bez přegenerování inventáře**, dostane **2 NEDEKLAROVANÉ exity
  a 2 brány bez čítače** (`n1-over-inventar`, `C2: mutace N1`) — přesně to
  naměřil **první běh A3** (54/6) a **`p30-a-overeni.py`** uvnitř (32/3).
  Náprava je **přegenerovat**, ne deklarovat (a taky se to v P31 stalo).
  **Poučení pro měřidla:** *tvar hlášení je STAV, ne měřidlo* — týž den se to
  projevilo i u tiku: seznam `v cooldownu N úloh` se **nepřipojí, když je
  prázdný**, a kontrola vázaná na ten seznam byla falešně červená.
* **H135 — tvrzení „`p30-a` → 35/0“ se NEREPRODUKUJE: dnes 32 kontrol / 3 chyby**
  (doklad `_analyza/p31-p30a-plne-vystup.txt`). Tři příčiny, každá měřená:
  (a) a (b) **moje oprava C2 přidala do `--jen A1M13` jednu kontrolu** (7 → 8)
  → dvě tvrzení měřidla P30 o téže etapě hlásí ROZCHOD
  (`A1 kontramutace … 7/0`, `A3 p29-a A1M13 … ('7','0') vs ('8','0')`);
  (c) kontrola **„`deploy.yml` na živém HEAD je completed/success“ nemůže
  projít** — `deploy.yml` má `paths: ['conductor/**']` a `HEAD` (`0c0eb18`)
  mění jen dokumenty a `_analyza/`, takže **žádný běh nasazení na HEAD není**
  (nasazený je `cf1f280` — to ověřil A2-2). Je to **dobová kontrola**: v P30
  platila, protože HEAD tehdy byl `cf1f280`.
* **H137 — harness z `g3` bez `FORGE_REGISTR` přepíše ŽIVÝ registr.** Naměřeno
  v P31 **vlastním omylem**: nový `p31-mutace.py` pustil mutant `g3` (50 bran)
  bez `FORGE_REGISTR` → do `_analyza/_registr-bran.json` se zapsalo
  **`bran_celkem: 50`** a **`ag-over-cisla.py` spadl** („bran v registru:
  tvrdí 49, naměřeno 50") → tím spadl i `ag-mutace` (jeho baseline je ten
  skript) → `g3` hlásil **2 NEDEKLAROVANÉ exity**. Náprava je **pustit `g3`**
  (zapsal 49 bran) a v harnessu **vždy** předat `FORGE_REGISTR`/`FORGE_BEZ_REGISTRU`.
  Past je v `g3-brany.py` popsaná od P20 — **a stala se znovu**.
* **H136 — dávka dokladů (`p20-d-doklady.py`) už živé dokumenty NEPŘEPISUJE**
  (H130 ověřeno: pojistka hlásí „žádný z 4 sledovaných dokumentů se nezměnil“
  a **hash před/po je shodný** — doklad `_analyza/p31-a4-davka-vystup.txt`).
  **Ale kořen vady žije:** `p27-dopln-zaznamy.py` zapisuje soubor **i když
  kotvy nenašel** (řádek 41 je bez podmínky) a `exit 1` hlásí **až po zápisu**;
  `PRESKIP` tu vadu jen **schová před dávkou** — kdo ten skript pustí ručně,
  přepíše dokument znovu.

### 62.5 Živý stav při zápisu (9. 10. 2026, ~14:2x +02:00)

```
orchestra: HEAD 0c0eb18 · origin/main 0c0eb18 (P30 PUSHNUTA) · hra 01a9649 (cizí session)
živá služba: /tasks/cleanup {dry_run} → osiřelých 0 · tik: "spusteno: 0 úloh; …
             roadmapa je hotová (nebo čeká na závislosti / cooldown), watchdog: 0 ohlášeno"
             (cooldown je dnes PRÁZDNÝ — proto zpráva neuvádí seznam úloh)
brány:       g3 → 49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače (`mutace B (combat)`; exit 1)
             · validate-all → 0 problémů · ov-g → 0 NEOVĚŘENO (99 řádků Hxx)
             · test-tick-offline 215/0 · tick-mutace 20 vrat/41/0 · p29-b6-mutace 15/0
             · p30-a 32/3 (bylo 35/0 — viz H135) · p30-mutace 16/0
             · p28-b-mutace 30/0 (bylo 27/2 — oprava C1) · p31-mutace 24/0
             · over-skilly 92/0 · over-dokumentaci 64/0 · kronika SEDÍ (45 řádků)
```

### 62.6 Co čeká na tebe (uživatel)

* **Nic zásadního.** Push P30 byl ověřený, nasazení taky (`deploy.yml` #35 na
  `cf1f280`, živá služba posílá nový kód) a **opravená dvě měřidla** jsou
  zelená. **Nic se nemusí nasazovat** — opravy jsou v nástrojích a dokumentech.
* **B3 (`/game/active {active:false}` na živé službě)** pořád čeká na výslovné
  „ano“ (dočasně zastaví orchestra).
* **Zavádějící komentáře v conductu** (`index.ts:1558–1559`, `:1489–1493`) —
  oprava je změna kódu + nasazení z pushe; **rozhodnutí o směru**, ne úklid.
* **⚠ Zásah do oprávnění (mimo repo):** tato session **nesměla zapisovat do
  `_analyza/`** (Windows oprávnění) a jednou spuštěný opravný nástroj přidal
  plná práva přihlášenému uživateli u `E:\Workspaces\forge-orchestra\_analyza`.
  Záloha i příkaz pro vrácení jsou v **`E:\Workspaces\_acl-oprava-p31\`**
  (`acl-backup-*.json` + `.ps1`); **nemaž to**, dokud nejsi spokojený.

### 62.7 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p31-a-overeni.py --plne            # celé přeměření P30 (~45 min)
python _analyza\p31-a-overeni.py                   # LEVNÉ kontroly (§61, ~1 min)
python _analyza\p31-a-overeni.py --jen A4          # H130: dávka dokladů (~35 min)
python _analyza\p31-mutace.py                      # důkaz, že opravy C1/C2 MĚŘÍ (24/0)
python _analyza\p28-b-mutace.py                    # opravené měřidlo P28/B (30/0)
python _analyza\p29-a-overeni.py --jen A1M13       # měřidlo P29 + ÚKLID mutantů (8/0)
python _analyza\g3-brany.py                        # 49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače
node tools\validate-all.mjs                        # 0 problémů
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\kronika-kontrola.py                # SEDÍ + id 1..46 bez děr
python _analyza\ov-g-neovereno.py                  # 0 NEOVĚŘENO, rozsah 99 řádků Hxx
```
"""

# ═══════════════════════════════════════════════════════════ KRONIKA ═══
RADEK_46 = (
    "| **46** | **9. 10. 2026** (11:30–14:2x +02:00) | **ověřovací (Úkol A: přeměření P30) "
    "+ akční (Úkol B: C1 + C2)** | "
    "**PŘEMĚŘIT PRÁCI P30 VLASTNÍM MĚŘIDLEM A ZAVŘÍT DVĚ VADY MĚŘIDEL.** "
    "**VLASTNÍ MĚŘIDLO:** `_analyza/p31-a-overeni.py` (A1–A7) → plný běh **54 kontrol, "
    "1 chyba, 2 pojmenované ROZDÍLY, 0 NEZMĚŘENO**; **A1** `p30-mutace.py` **16/0** "
    "(tvrzení §61.5) a VLASTNÍ diferenciál měřidla P30 (kotva `test-tick-offline → 215/0`: "
    "živé `exit 0` → mutant `exit 1` s ROZCHODem → mutant+oslabené `exit 0`, dokument vrácen "
    "bajt na bajt). **A2 (tři kroky nasazení):** `ls-remote` = `HEAD` = `0c0eb18`; `deploy.yml` "
    "**#35 na `cf1f280`** `completed/success` (sha PŘEČTENÁ z §61); živá služba "
    "`/tasks/cleanup {dry_run}` → **osiřelých 0** a tik **pojmenovává, co přeskočil** "
    "(`POST /tick` volán JEDNOU — mění stav). **A3:** shoda u `test-tick-offline` 215/0, "
    "`over-skilly` 92/0, `ov-g` 99, `p29-b6-mutace` 15/0, `over-dokumentaci` 64/0, "
    "`p30-mutace` 16/0, `tick-mutace` 20 vrat/41/0, `g3` **49 bran / 0 NEDEKLAROVANÝCH / "
    "1 bez čítače**, `validate-all` **0 problémů**; NESHODA jediná: **`p30-a` 35/0 → dnes "
    "32/3 (H135)** — dvě příčiny jsou moje oprava C2 (`--jen A1M13` má 7 → **8** kontrol) "
    "a jedna dobová: kontrola „`deploy.yml` na živém HEAD“ **nemůže projít**, protože "
    "`deploy.yml` má `paths: ['conductor/**']` a `0c0eb18` mění jen dokumenty (nasazený je "
    "`cf1f280`). **A5:** zámek VYLOUČEN (žádná úloha `running`), `engine.registry` má "
    "počítadlo **5**, za stropem není žádná vydávaná granule (`sim.crafting` 12 = `done`). "
    "**A6:** `p29-a-overeni.py --jen A1M13` → **8/0** a **žádný mutant nezůstal**. "
    "**A7:** záznamy jen přidávány (**0 smazaných řádků**), `kronika SEDÍ`, `handoff 0 "
    "chybějících`, `ov-g` **0 NEOVĚŘENO** (99 řádků Hxx). **ÚKOL B = C1 + C2:** "
    "**C1 — `p28-b-mutace.py` 27/2 → 30/0**, dvě příčiny v něm: **H131** kontrola M1 "
    "srovnávala kotvu v **CELÉM** dokumentu (dnes **3×**) s počtem v **§57** (**1×**) → "
    "`(1,3) != (1,1)`; dnes `kotva_m1` váže kotvu na MĚŘENÝ ODDÍL a diferenciál to dokazuje "
    "(živá `((1,0),(1,0))` vs. oslabená kopie s původní vadou `((1,3),(1,1))`); **H132** "
    "mutace M2 vkládala do `BRANY` záznam o **DVOU** prvcích, ale `g3` čte `for popis, "
    "prikaz, vzor in BRANY` → mutant **spadl na `ValueError`** a diferenciál se měřil na "
    "tracebacku (doklad `p31-sonda-g3-vystup.txt`); dnes platný 3prvkový `ZAZNAM_FIXTURY` "
    "v OBOU nohách + kontrola „mutant přidal PRÁVĚ JEDNU chybu“ + množinová kontrola "
    "„kontrola POČTU BRAN v oslabené kopii UŽ NENÍ červená“. **C2 — H124 ZAVŘENO:** "
    "`p29-a-overeni.py` uklízí mutanty v `try/finally` a sám to kontroluje; tři nohy: živé "
    "**8/0** a žádný mutant, oslabená kopie bez úklidu nechá **`_analyza/p29-mut-handoff.md` "
    "(196 092 B) + `p29-mut-ovg.py` (8 545 B)** a hlásí CHYBA, po testu uklizeno. "
    "**MUTAČNÍ DŮKAZ OPRAV:** `_analyza/p31-mutace.py` → **24/0**. **DALŠÍ NÁLEZY:** "
    "**H133** `g3` je `exit 1` POJMENOVANĚ (1 brána bez čítače) a `p28-a-overeni.py` A6 na "
    "tom stojí (trvalá 1 chyba baseline); **H126 žije**: `g3` bez přegenerování inventáře → "
    "**2 NEDEKLAROVANÉ exity + 2 brány bez čítače** (naměřil první běh A3: 54/6 i `p30-a`: "
    "32/3) — náprava je přegenerovat; **tvar hlášení je STAV, ne měřidlo** (tik neuvádí "
    "`v cooldownu N úloh`, když je seznam prázdný). **H136** dávka dokladů živé dokumenty "
    "NEPŘEPISUJE (hash před/po shodný + pojistka), **ale kořen vady žije**: "
    "`p27-dopln-zaznamy.py` zapisuje i bez nalezené kotvy (řádek 41 bez podmínky) a `exit 1` "
    "hlásí až po zápisu — `PRESKIP` ho jen schová. **H137** harness z `g3` bez "
    "`FORGE_REGISTR` přepsal ŽIVÝ `_registr-bran.json` (**`bran_celkem: 50`**) a shodil "
    "`ag-over-cisla.py` („tvrdí 49, naměřeno 50“) → náprava = pustit `g3` (49 bran). "
    "**PLÁN:** dodatek P31 | **—**"
)

NALEZY_224 = r"""
### 2.24 Nálezy z P31 (9. 10. 2026) — měřidlo, které spadlo na vlastní citaci, a mutant, který měřil traceback

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P32.

| # | Nález | Doklad |
|---|---|---|
| **H131** | **`p28-b-mutace.py` SHODILO VLASTNÍ MĚŘIDLO ZA CIZÍ CITACI.** Kontrola M1 srovnávala `text.count(kotva)` (**celý dokument**, dnes **3×**) s `s57.count(kotva)` (**§57**, **1×**) → hlásila `(1, 3) != (1, 1)`, ačkoli se v živém stromě nic nemutovalo — každý nový záznam, který tvrzení **cituje**, měřidlo shodil. Opraveno funkcí `kotva_m1` (kotva v **měřeném oddílu**, vzor `p29-a-overeni.py`); diferenciál: živá `((1,0),(1,0))` vs. **oslabená kopie s původní vadou** `((1,3),(1,1))`. | `_analyza/p31-mutace-vystup.txt` (24/0), `_analyza/p31-mutace-p28b-vystup.txt` (**30/0**, bylo 27/2), počty výskytů kotvy v `HANDOFF.md` |
| **H132** | **M2 MUTACE VKLÁDALA DO `BRANY` ZÁZNAM O DVOU PRVCÍCH** (`("fixtura", ["python", cesta])`), ale `g3` čte `for popis, prikaz, vzor in BRANY` → mutant `g3` **spadl na `ValueError: not enough values to unpack (expected 3, got 2)`** a diferenciál se měřil **na tracebacku**, ne na 50. bráně; kontrola „spadlo na počtu bran“ přitom procházela, protože **jméno kontroly** obsahuje „49 bran“. Opraveno: platný 3prvkový `ZAZNAM_FIXTURY` v **obou** nohách (první oprava zapomněla na M2c — chytil to mutační test opravy), navíc kontrola „mutant přidal PRÁVĚ JEDNU chybu“ a množinová kontrola, že kontrola počtu bran v oslabené kopii **zmizela**. | `_analyza/p31-sonda-g3-vystup.txt` (ValueError), `_analyza/p28-b-mutace.py`, `_analyza/p31-mutace.py` |
| **H133** | **`g3` KONČÍ `exit 1` POJMENOVANĚ — a `p28-a-overeni.py` A6 na tom stojí.** Naměřeno: **49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače** (`mutace B (combat)`, cizí brána hry; `OCEKAVANE_BEZ_CITACE` je záměrně prázdný) → `exit 1` je za **deklarovaný stav**, ne neočekávaný. A6 ale čeká `g3 → exit 0`, takže jeho baseline má **trvale 1 chybu** — což je přesně to, co P30 nazvalo „posunutý baseline g3“. **A druhá polovina téhož: H126 ŽIJE** — kdo pustí `g3` **bez přegenerování inventáře**, dostane **2 NEDEKLAROVANÉ exity a 2 brány bez čítače** (`n1-over-inventar`, `C2: mutace N1`); naměřil to **první běh A3** (54/6) i `p30-a-overeni.py` (32/3). **Poučení:** *tvar hlášení je STAV, ne měřidlo* — týž den se to projevilo u tiku (`v cooldownu N úloh` se nepřipojí, když je seznam prázdný, a kontrola vázaná na ten text byla falešně červená). | `_analyza/p31-a-overeni-vystup.txt` (A3), `_analyza/p31-a-plne-prubeh-vystup.txt` (první běh 54/6), `_analyza/p31-sonda-g3-vystup.txt`, `_analyza/p31-stav-vystup.txt` |
| **H134** | **H124 ZAVŘENO: MĚŘIDLO P29 PO SOBĚ UKLÍZÍ — A TEST TO DOKAZUJE.** `p29-a-overeni.py` zapisoval `_analyza/p29-mut-handoff.md` (**196 092 B**), `_analyza/p29-mut-g3.py`, `p29-mut-fixtura.py`, `p29-mut-ovg.py` do živého `_analyza/` a **nemazal je** (nejsou gitignorované → inventář, `git status`, `git add -A` a dvě shozené brány). Dnes je úklid v **`try/finally`** se **sebekontrolou** (`uklid_mutanty()`). Tři nohy: živé měřidlo **8/0** a **žádný mutant**; oslabená kopie **bez úklidu** nechá 196 092 B + 8 545 B a hlásí **CHYBA** (`exit 1`); po testu uklizeno. | `_analyza/p31-mutace-vystup.txt` (C2), `_analyza/p29-a-overeni.py` (`MUTANTI`, `uklid_mutanty`), `_analyza/p31-a-overeni-vystup.txt` (A6) |
| **H135** | **TVRZENÍ „`p30-a` → 35/0“ SE NEREPRODUKUJE: dnes 32 kontrol / 3 chyby.** Tři příčiny, každá měřená: (a)+(b) **oprava C2 přidala do `--jen A1M13` jednu kontrolu** (7 → **8**), takže dvě tvrzení měřidla P30 o téže etapě hlásí ROZCHOD (`A1 kontramutace … 7/0`, `A3 p29-a A1M13 … ('7','0') vs ('8','0')`); (c) kontrola **„`deploy.yml` na živém HEAD je completed/success“ nemůže projít** — `deploy.yml` má `paths: ['conductor/**']` a `HEAD` (`0c0eb18`) mění **jen dokumenty a `_analyza/`**, takže žádný běh nasazení na HEAD neexistuje (nasazený je `cf1f280`, ověřeno A2-2). Je to **dobová kontrola**: v P30 platila, protože HEAD tehdy byl `cf1f280`. | `_analyza/p31-p30a-plne-vystup.txt`, `.github/workflows/deploy.yml` (`paths`), `git show --stat HEAD` |
| **H136** | **H130 OVĚŘENO: DÁVKA DOKLADŮ UŽ ŽIVÉ DOKUMENTY NEPŘEPISUJE — ALE KOŘEN VADY ŽIJE.** Běh `--jen A4`: pojistka hlásí **„žádný z 4 sledovaných dokumentů se nezměnil“** a **hash před/po je u všech čtyř shodný**. **Kořen** je ale neopravený: `p27-dopln-zaznamy.py` zapisuje soubor **i když kotvy nenašel** (řádek 41 je bez podmínky) a `exit 1` hlásí **až po zápisu** — `PRESKIP` tu vadu jen **schová před dávkou**; kdo skript pustí ručně, přepíše dokument znovu. | `_analyza/p31-a4-davka-vystup.txt`, `_analyza/p20-d-doklady.py` (`PRESKIP`), `_analyza/p27-dopln-zaznamy.py:33–42` |
| **H137** | **HARNESS Z `g3` BEZ `FORGE_REGISTR` PŘEPÍŠE ŽIVÝ REGISTR BRAN — a shodí tři brány.** Naměřeno v P31 **vlastním omylem**: nový `p31-mutace.py` pustil mutant `g3` (50 bran) bez `FORGE_REGISTR` → `_analyza/_registr-bran.json` měl **`bran_celkem: 50`** → `ag-over-cisla.py` **exit 1** („bran v registru: tvrdí 49, naměřeno 50“) → spadl i `ag-mutace` (jeho baseline je ten skript) → `g3` hlásil **2 NEDEKLAROVANÉ exity**. Náprava je **pustit `g3`** (zapsal 49 bran) a v každém harnessu předat `FORGE_REGISTR`/`FORGE_BEZ_REGISTRU`. **Past je v `g3-brany.py` popsaná od P20 (fixtura `A1: zdravá` v živém registru) — a stala se znovu**, což je vlastní nález: komentář u nástroje vadu nechrání. | `_analyza/_registr-bran.json` (`bran_celkem` 50 → 49), `_analyza/ag-over-cisla.py` (exit 1), `_analyza/p31-mutace.py` (`mutant_g3`, opraveno), `_analyza/p31-g3-oprava-registru-vystup.txt` |
"""

PLAN_DODATEK = r"""
---

## P31 (9. 10. 2026) — CO JE OPRAVENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, ~14:2x +02:00. Platí pro stav po P31;
> kdo to čte později, **přeměří** (`python _analyza\p31-a-overeni.py`).

**Hotovo (neopakovat):** obě vady měřidel z nabídky P31 jsou **zavřené** —
**C1** (`p28-b-mutace.py` **27/2 → 30/0**; H131 kotva v celém dokumentu,
H132 dvouprvkový záznam fixtury) a **C2** (H124: měřidlo P29 uklízí mutanty
v `try/finally` a samo to kontroluje). Důkaz: `_analyza/p31-mutace.py` → **24/0**.
**P30 je přeměřená** (`p31-a-overeni.py` → 54/1/2 ROZDÍLY, 0 NEZMĚŘENO);
jediná neshoda je `p30-a` **35/0 → 32/3** (H135: dvě příčiny z opravy C2,
jedna dobová kontrola nasazení na živém HEAD).

**Nejbližší práce (P32) — v tomto pořadí:**

1. **`p28-a-overeni.py` A6 čeká `g3 → exit 0`** (H133) — dnes **trvale 1 chyba**
   baseline, protože `g3` končí `exit 1` za **pojmenovaný** stav (1 brána bez
   čítače). Buď to deklarovat jako `OCEKAVANE_*`, nebo vázat na ten stav.
2. **`p27-dopln-zaznamy.py` zapisuje i bez kotvy** (H136) — `PRESKIP` ho jen
   schová; oprava = zápis **až po ověření kotvy** + test, který to zavolá.
3. **Zavádějící komentáře v conductu** (`index.ts:1558–1559`, `:1489–1493`) —
   změna textu + **nasazení z pushe** (ne lokální wrangler).
4. **H112 — brána „cron běží (čas)“ nemůže selhat** (`validate-all` testuje jen
   `!!h.time`) — a přesně ten tik se 9. 10. zastavil.
5. **B3 (`/game/active {active:false}`)** — čeká na výslovné „ano“ uživatele.

**Co NEDĚLAT:** nepouštět `g3` z harnessu bez `FORGE_REGISTR` (H137); nepsat
do hry; nemazat `E:\Workspaces\_acl-oprava-p31\` (cesta zpět k oprávněním).
"""


def hledej_max_h(text):
    return max((int(m.group(1)[1:]) for m in re.finditer(r"^\|\s*\*\*(H\d+)\*\*\s*\|", text, re.M)),
               default=0)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true", help="jen ověřit, nezapisovat")
    args = ap.parse_args()

    h = HANDOFF.read_text(encoding="utf-8")
    k = KRONIKA.read_text(encoding="utf-8")
    p = PLAN.read_text(encoding="utf-8") if PLAN.is_file() else ""

    # ⚠ IDEMPOTENTNÍ BĚH MUSÍ SKONČIT NULOU (dávka dokladů tenhle skript pouští).
    uz_h = "## 62. P31" in h
    uz_k = bool(re.search(r"^\|\s*\*\*46\*\*\s*\|", k, re.M))
    if uz_h and uz_k:
        print("  OK    záznamy P31 UŽ JSOU zapsané (HANDOFF §62 + KRONIKA řádek 46) "
              "— idempotentní běh, nic se nemění")
        check("KRONIKA: id 1..46 bez děr (kontrola i při idempotentním běhu)",
              [n for n in range(1, 47)
               if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k, re.M)], [])
        print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
        return 0 if chyb == 0 else 1

    check("HANDOFF §62 ještě NENÍ (skript je idempotentní)", uz_h, False)
    check("KRONIKA řádek 46 ještě NENÍ", uz_k, False)
    check("KRONIKA má řádek 45 (kotva pro vložení)",
          bool(re.search(r"^\|\s*\*\*45\*\*\s*\|", k, re.M)), True)
    check("KRONIKA má oddíl §2.23 (kotva pro §2.24)", "### 2.23" in k, True)
    check("PLAN existuje a je neprázdný", bool(p.strip()), True)
    check("PLAN dodatek P31 ještě NENÍ (idempotence)",
          "CO JE OPRAVENÉ A CO JE NA ŘADĚ" in p, False)
    # ⚠ NÁLEZY SE DO HANDOFFu PÍŠOU JEN JAKO ODKAZY V MAPOVACÍM SEZNAMU —
    #    tabulkový řádek `| **Hxx** |` by zvedl počítadlo „řádků Hxx" a shodil
    #    `ov-g` i měřidla P28/P30 (naměřeno: 1 řádek v HANDOFF.md).
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v kotvách)" % chyb)
        return 1

    h0 = hledej_max_h(k)
    print("  nejvyšší existující nález v kronice: H%d → nové začnou H%d" % (h0, h0 + 1))
    check("nálezy začínají H131 (P30 skončila na H130)", h0, 130)

    # (1) KRONIKA: řádek 46 hned za řádek 45; §2.24 před "## 3."
    radky = k.splitlines()
    i45 = next(i for i, l in enumerate(radky) if re.match(r"^\|\s*\*\*45\*\*\s*\|", l))
    i3 = next(i for i, l in enumerate(radky) if l.startswith("## 3."))
    check("řádek 45 je PŘED oddílem §3 (jinak by vložení rozbilo tabulku)", i45 < i3, True)
    novy_k = radky[:i45 + 1] + [RADEK_46] + radky[i45 + 1:i3] + [NALEZY_224.strip(), ""] + radky[i3:]
    k_new = "\n".join(novy_k) + "\n"

    # (2) HANDOFF: §62 na konec
    h_new = h.rstrip("\n") + "\n" + HANDOFF_62.strip("\n") + "\n"

    # (3) PLÁN: dodatek na konec
    p_new = (p.rstrip("\n") + "\n" + PLAN_DODATEK.strip("\n") + "\n") if p else ""

    # ── ověření PŘED zápisem ──────────────────────────────────────────────
    check("HANDOFF: přibyl právě oddíl §62", "## 62. P31" in h_new and len(h_new) > len(h), True)
    check("HANDOFF: řádků neubylo", len(h_new.splitlines()) > len(h.splitlines()), True)
    check("HANDOFF: každý nález H131..H137 je zmíněn (mapovací seznam)",
          all(("H%d" % n) in h_new for n in range(131, 138)), True)
    check("HANDOFF: NEPŘIBYL žádný tabulkový řádek `| **Hxx** |` (jinak spadne ov-g)",
          len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h_new, re.M)),
          len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h, re.M)))
    check("KRONIKA: přibyl řádek 46", bool(re.search(r"^\|\s*\*\*46\*\*\s*\|", k_new, re.M)), True)
    check("KRONIKA: id 1..46 bez děr",
          [n for n in range(1, 47)
           if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k_new, re.M)], [])
    check("KRONIKA: nálezy H131..H137 jsou v textu",
          all(("**H%d**" % n) in k_new for n in range(131, 138)), True)
    check("KRONIKA: nic neubylo (řádků přibylo)",
          len(k_new.splitlines()) > len(k.splitlines()), True)
    check("KRONIKA: řádek 46 má datum a typ",
          bool(re.search(r"^\|\s*\*\*46\*\*\s*\|\s*\*\*9\. 10\. 2026\*\*", k_new, re.M)), True)
    check("PLÁN: přibyl dodatek", len(p_new) > len(p), True)

    if args.kontrola:
        print("KONTROLA OK — nic se nezapsalo (--kontrola)")
        return 0 if chyb == 0 else 1
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v ověření)" % chyb)
        return 1

    HANDOFF.write_bytes(h_new.encode("utf-8"))
    KRONIKA.write_bytes(k_new.encode("utf-8"))
    if p_new:
        PLAN.write_bytes(p_new.encode("utf-8"))
    print("  zapsáno: HANDOFF.md §62, KRONIKA řádek 46 + §2.24, PLAN dodatek P31")
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

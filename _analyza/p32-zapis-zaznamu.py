# -*- coding: utf-8 -*-
r"""P32 — ZÁPIS ZÁZNAMŮ: HANDOFF §63, KRONIKA řádek 47 + §2.25, PLAN dodatek P32.

PROČ SKRIPTEM: texty mají přes 3000 znaků a **kotva vzatá z načteného řádku ho
zkrátí** (omyly 194, 206) — vkládá se proto podle KRÁTKÉ kotvy (`## 3.`), ne
podle textu.

⚠ `NEXT-SESSION-INSTRUKCE.md` tenhle skript **NEZAPISUJE**: hlavička zadání musí
nést commit, který vznikne **až commitem** (a zůstává záměrně necommitnutá —
vzor P31). Zapíše se po commitu.

⚠ Je v `PRESKIP` dávky `p20-d-doklady.py` — ta má **pojistku proti zápisu**
a tenhle skript je jediný, kdo do dokumentů zapisuje ZÁMĚRNĚ.

Použití: python _analyza\p32-zapis-zaznamu.py [--kontrola]
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
chyb = []


def check(popis, zjisteno, ocekavano):
    global kontrol
    kontrol += 1
    print("  %s  %s" % ("OK  " if zjisteno == ocekavano else "CHYBA", popis))
    if zjisteno != ocekavano:
        chyb.append(popis)
        print("        čekáno:   %r\n        naměřeno: %r" % (ocekavano, zjisteno))


# ═══════════════════════════════════════════════════════════ HANDOFF §63 ═══
HANDOFF_63 = r"""
## 63. P32 — PŘEMĚŘENÍ P31 VLASTNÍM MĚŘIDLEM A TŘI ZAVŘENÉ VADY (9. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P32 + stav po P32**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**47**, nálezy **§2.25**), plán (`PLAN-DALSI-KROK.md`, dodatek P32).
Zadání P32 je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **9. 10. 2026, 17:56–20:23 +02:00** (živý čas
> z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba) platí
> k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.25), aby každý nález byl dohledatelný
> z HANDOFF.md:** H140 = kontrola v `p22-test-mutace.py` hledala `"0 mrtvých"`
> **PODŘETĚZCEM** a `"40 mrtvých"` ji uspokojilo (prošlo by i 10/20/30) ·
> H141 = **závěr P31 „mutace `REPO` nic nezmění“ je VYVRÁCENÝ** (měřeno: verdikt
> se MĚNÍ, `92 zmínek, 0 mrtvých` → `43 zmínek, 40 mrtvých`) ·
> H142 = **KOŘEN H130 ZAVŘEN**: `p27-dopln-zaznamy.py` zapisoval soubor i bez
> nalezené kotvy · H143 = §62.5 tvrdí u kroniky **45 řádků**, naměřeno **46** ·
> H144 = kotva `99 řádků Hxx` je dnes v `HANDOFF.md` **5×** (v §57 **1×**);
> P31 psala 3× · H145 = **VLASTNÍ ZÁZNAM P31 ZDVOJIL KOTVU**
> `test-tick-offline → 215/0` → `p30-mutace.py` spadl na `ValueError` a plný běh
> P31 se **NEREPRODUKUJE** · H146 = **H124 MĚLA DÍRU**: plný běh
> `p29-a-overeni.py` (jak ho pouští dávka dokladů) nechal v živém `_analyza/`
> `p29-kopie-tick.mjs` (**75 395 B**) — úklid byl jen v A1M/A1M13, kopie se ale
> tvoří až v A3; dnes je úklid v `finally` i tam.

### 63.1 Úkol A — VLASTNÍ MĚŘIDLO P32 (`_analyza/p32-a-overeni.py`)

**Plný běh: 51 kontrol, 0 chyb, 2 pojmenované ROZDÍLY, 0 NEZMĚŘENO**
(doklad `_analyza/p32-a-overeni-vystup.txt`). Každé tvrzení se **PŘEČTE
Z §62** (vypisuje se okno, které vzor trefil) a pak se měří; co nesedí, je
**ROZDÍL s vysvětlením** — nebo **CHYBA**. Měření má **VLASTNÍ diferenciály**,
ne opisy těch P31:

* **B1 — umí opravy P31 spadnout?** (a) **H131:** živá funkce `kotva_m1`
  z živého `p28-b-mutace.py` nad živým dokumentem + mutovanou kopií §57 →
  **SHODA `((1,0),(1,0))`**; **oslabená kopie s PŮVODNÍ vadou** (kotva v CELÉM
  dokumentu) → **ROZCHOD `((1,5),(1,1))`** (kotva je dnes v dokumentu **5×**,
  v §57 **1×**). (b) **H124:** živé `p29-a-overeni.py --jen A1M13` → **8/0**
  (14 s) a **žádný** `p29-mut-*`; oslabená kopie **bez úklidu** nechá
  `_analyza/p29-mut-handoff.md` (**211 226 B**) + `_analyza/p29-mut-ovg.py` (8 545 B) a hlásí
  **CHYBA** → kontrola úklidu tedy MĚŘÍ. (c) **vlastní běh**
  `p28-b-mutace.py` → **30/0** (1 106 s). (d) `p31-mutace.py` (povinný běh A1
  v této session) → **24/0** (doklad `_analyza/p31-mutace-vystup.txt`).
* **B2 — co P31 nasadila? Nic.** `git show --name-only` u `41aa981` (21 souborů)
  i `d3f1a48` (1 soubor) → **0 souborů** z `conductor/` nebo `.github/`;
  `ls-remote` = `HEAD` = `d3f1a48`; nasazený kód je **`cf1f280`**
  (`deploy.yml` **#35** `completed/success`); živá služba
  `/tasks/cleanup {dry_run}` → **osiřelých 0**.
* **B3 — sedí čísla z §62?** Shoda: `test-tick-offline` **215/0**,
  `over-skilly` **92/0**, `p29-b6-mutace` **15/0**, `over-dokumentaci` **64/0**,
  `p28-b-mutace` **30/0**, `ov-g` **99 řádků Hxx** a **0 NEOVĚŘENO**, registr
  bran **49** (`ag-over-cisla` `exit 0`), `kronika SEDÍ`, `handoff 0 chybějících`.
  **ROZDÍL je jediný:** §62.5 tvrdí u kroniky **45 řádků**, naměřeno **46**
  (H143) — záznam P31 vznikl **před** zápisem vlastního řádku session.
* **B4 — opravy P32:** `p22-test-mutace.py` → **20/0** (měřený diferenciál
  `(92,0) → (43,40)`), `p32-test-zapis-kotvy.py` → **16/0**.
* **B5 — integrita:** registr bran je živý (49), dokumenty čitelné;
  dávku dokladů měří **povinný běh A4** (viz 63.4).

### 63.2 PŘEMĚŘENÍ P31 — CO SE NEREPRODUKUJE (H145)

* **`p31-mutace.py` → 24/0** (tři nohy; C1-a 30/0 za 1 058 s, C1-c
  `brán celkem: 50`, C2-b 211 226 B + 8 545 B) — **tvrzení §62.3 reprodukováno**.
* **`p31-a-overeni.py --plne` → 43 kontrol, 5 chyb, 2 ROZDÍLY, 1 NEZMĚŘENO.**
  §62.2 tvrdí **54/1/2/0** → **NEREPRODUKUJE SE** a má to **jeden kořen**:
  P31 do §62.2 **citovala** přesně kotvu `test-tick-offline → 215/0`; tím ji
  v dokumentu **ZDVOJILA** (kotva byla 2×) → `mutuj` vyhodil
  `ValueError: kotva je v souboru 2×` → `p30-mutace.py` **exit 1 bez čítače**
  a diferenciál A1 se stal **NEZMĚŘENÝM**. **Čtyři z pěti chyb** jsou tento
  jediný kořen (A1: `p30-mutace` exit, diferenciál `None`, kotva 2×; A3:
  `p30-mutace` exit). Pátá je **H135** (`p30-a` 32/3 — známá, zdokumentovaná).
* **DŮSLEDEK PRO PRAVIDLO:** je to **tatáž past jako H131**, jen na kotvě
  **DOKUMENTU** místo kotvy v kódu: *záznam, který tvrzení cituje, rozbije
  měřidlo vázané na jediný výskyt v CELÉM dokumentu.* A druhá polovina téhož:
  **měřidlo, které na to spadne, přijde o CELÝ diferenciál** — místo pojmenované
  chyby vypsalo `ValueError` („brána, která na nález spadne, hlásí míň“).
* **OPRAVA (H145):** kotva se bere **z MĚŘENÉHO ODDÍLU §60** a nese i okolní
  text (`... (bylo 205/0) · tick-mutace → 20 vrat, 41/0`); `P0` navíc ověřuje
  **obojí** (1× v dokumentu **a** 1× v §60) v **jedné** kontrole schválně —
  přidání další kontroly by posunulo čítač 16 → 17 a tím i baseline tvrzení
  v §61 (přesně ten churn, který projekt platil jako **H135**). Dvojznačná kotva
  se **hlásí pojmenovaně** a zbytek testu doběhne.
  **Důkaz:** `p30-mutace.py` **16/0** (před opravou `exit 1` + `ValueError`)
  a `p31-a-overeni.py --jen A1 --plne` **11/0** (před opravou 3 chyby +
  1 NEZMĚŘENO) — doklad `_analyza/p31-a1-po-oprave-vystup.txt`.

### 63.3 Úkol B — TŘI ZAVŘENÉ VADY (C2′, C3′, H145)

* **C3′ — H139 → H140 + H141 (kontrola, která se nechala uspokojit „40 mrtvými“).**
  `p22-test-mutace.py` byl **19/1** a P31 zapsala, že *„mutace `REPO` nic
  nezmění“*. **To se NEREPRODUKOVALO** (sonda `_analyza/p32-sonda-h139.py`):
  zdravá brána hlásí `92 zmínek, 0 mrtvých`, zmutovaná `43 zmínek, 40 mrtvých`
  → **verdikt se MĚNÍ**. Vadná byla **KONTROLA**: `"0 mrtvých" not in v1` je
  **podřetězcová** podmínka a `"40 mrtvých"` řetězec `"0 mrtvých"` **obsahuje**
  (prošlo by i 10/20/30 — každé číslo končící nulou). Dnes se čítač
  z **MĚŘENÉHO ŘÁDKU** parsuje a porovnává se jeho hodnota → **20/0**.
  Kontrola se přitom neptá na zdravý stav jen tak: `zdravá (92, 0)` se ověřuje
  taky, takže „diferenciál“ je vidět.
* **C2′ — H136/KOŘEN H130 (patcher zapisoval i bez kotvy).**
  `p27-dopln-zaznamy.py` měl `cesta.write_bytes(...)` **bez podmínky**: když
  kotvu nenašel, soubor **přesto zapsal** (a `exit 1` hlásal až potom) — dávka
  i ruční běh tím přepsaly živý dokument a převedly konce řádků. Dnes se kotvy
  ověří **PŘED** zápisem, při neshodě se **nezapisuje vůbec** a i blok §57 je
  hlídaný. **Důkaz:** `_analyza/p32-test-zapis-kotvy.py` → **16/0** — živý
  patcher nad fixturami s chybějícími kotvami: `exit 1` a **fixtura bajt na
  bajt nedotčená**; **oslabená kopie s PŮVODNÍM `vymen()`** fixturu **ZAPÍŠE**
  (CRLF → LF) → kontrola měří. Živý běh nad reálnými dokumenty: `exit 1`
  (kotvy už byly spotřebované P27) a **hash před/po shodný** — tedy 0 zapsaných
  bajtů.
* **H145 — regrese z vlastního záznamu P31** (viz 63.2).
* **H146 — H124 měla díru (zavřeno).** Při kontrole pracovního stromu před
  commitem zůstal **necommitnutý artefakt** `_analyza/p29-kopie-tick.mjs`
  (**75 395 B**, mtime 20:14:11): `p29-a-overeni.py` uklízí mutanty jen
  v etapách **A1M/A1M13**, ale kopie testu tiku se tvoří **až v etapě A3** —
  a **dávka dokladů pouští plný (výchozí) režim**, kde A3 je (naměřeno v A4:
  `exit=1 p29-a-overeni.py 423.0s`). **Pojistka dávky to vidět nemohla** — hlídá
  4 dokumenty, ne `_analyza/`. P31 přitom **H124 zapsala jako ZAVŘENO**, a její
  důkaz (`--jen A1M13`) tenhle kód **vůbec nespustí**: zavření platilo jen pro
  jednu větev téhož nástroje. **Opraveno:** úklid je v `finally` i v A3
  a kontrola úklidu je součástí výsledku → `python _analyza\p29-a-overeni.py
  --jen A3` → **17/0** a kopie po běhu **neexistuje**.

**MUTAČNÍ DŮKAZ OPRAV:** `_analyza/p32-mutace.py` → **18/0**. Nohy: (M1) měřidlo
`p32-a-overeni.py` nad **zmutovanou KOPIÍ** `HANDOFF.md` (`over-skilly 92/0` →
`93/0`, přes `P32_HANDOFF`) **spadne** na té kontrole a **živý dokument se
nezmění**; (M2) kontrola v kopii `p22-test-mutace.py` oslabená na `(0, 0)` →
test **spadne**; (M3) `p32-test-zapis-kotvy.py` projde **a jeho diferenciál je
v důkazu vidět**.

### 63.4 A4 — DÁVKA DOKLADŮ (H130/H138) — POŘÁD ZAVŘENÉ

**`p31-a-overeni.py --jen A4` → 3 kontroly, 0 chyb, 2 048 s** (34 min; doklad
`_analyza/p31-a4-davka-vystup.txt`). Pojistka hlásí **„žádný z 4 sledovaných
dokumentů se nezměnil“**, **hash před/po je u všech čtyř shodný**, sekce
**„KDO ZAPSAL“ je PRÁZDNÁ** a ve výstupu není ani jedno **„ZMĚNĚN“**.
Dávka přitom pustila **57 dokladů** (18 s nenulovým exit — to je **stav**, ne
vada této session) — a **bere i nový doklad `p32-a-overeni.py`** (vzor
`p3[0-9]-`): **OK, 39 kontrol, 0 chyb, 33 s**, tedy **v dávce do dokumentů
nezapisuje**. Tím je **H130/H138 pořád zavřené** a zároveň je vidět, že pojistka
(jmenuje viníka po každém dokladu) funguje dál.

### 63.5 Živý stav při zápisu (9. 10. 2026, ~20:23 +02:00)

```
orchestra: HEAD d3f1a48 · origin/main d3f1a48 (P31 PUSHNUTA) · hra e4dccdb (cizí session)
           ⚠ P32 NIC NENASADILA: `41aa981` i `d3f1a48` mají 0 souborů z `conductor/`
             a `.github/`; nasazený kód je `cf1f280` (`deploy.yml` #35 completed/success)
živá služba: /tasks/cleanup {dry_run} → osiřelých 0 · tik (volán JEDNOU v A3):
             "spusteno: 0 úloh; … v cooldownu 3 úloh: #244, #245, #246"
brány:       g3 → 49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače (`mutace B (combat)`; exit 1)
             · validate-all → 0 problémů · ov-g → 0 NEOVĚŘENO (99 řádků Hxx)
             · test-tick-offline 215/0 · tick-mutace 20 vrat/41/0 · p29-b6-mutace 15/0
             · over-skilly 92/0 · over-dokumentaci 64/0 · ag-over-cisla 49 bran
             · p28-b-mutace 30/0 · p31-mutace 24/0 · p32-a-overeni 51/0
             · p32-mutace 18/0 · p22-test-mutace 20/0 (bylo 19/1) · p30-mutace 16/0
             · p32-test-zapis-kotvy 16/0 · p30-a 32/3 (H135)
             · kronika SEDÍ · handoff 0 chybějících
```

### 63.6 Co čeká na tebe (uživatel)

* **Nic zásadního.** P32 **nenasadila nic** (měřidla a dokumenty) — nasazený kód
  i živá služba jsou beze změny (`cf1f280`).
* **B3 (`/game/active {active:false}` na živé službě)** pořád čeká na výslovné
  „ano“ (dočasně zastaví orchestra).
* **Zavádějící komentáře v conductu** (`index.ts:1558–1559`, `:1489–1493`) —
  oprava textu je **změna kódu + nasazení z pushe**; **rozhodnutí o směru**.
* **H133 (`p28-a-overeni.py` A6 čeká `g3 → exit 0`)** zůstává otevřené (P32
  zavřela tři jiné vady) — buď stav deklarovat, nebo vázat na pojmenovaný stav.
* **H112** (brána „cron běží (čas)“ nemůže selhat) zůstává otevřené.

### 63.7 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p32-a-overeni.py --plne           # vlastní měřidlo P32 (~35 min)
python _analyza\p32-mutace.py                     # důkaz, že měřidlo umí spadnout (18/0)
python _analyza\p31-mutace.py                     # důkaz oprav P31 (24/0, ~18 min)
python _analyza\p31-a-overeni.py --plne           # přeměření P31 (~45 min)
python _analyza\p31-a-overeni.py --jen A1 --plne  # jen diferenciál A1 (11/0)
python _analyza\p31-a-overeni.py --jen A4         # dávka dokladů, pojistka (~35 min)
python _analyza\p22-test-mutace.py                # 20/0 (H140/H141 zavřeno)
python _analyza\p32-test-zapis-kotvy.py           # 16/0 (H136 zavřeno)
python _analyza\p30-mutace.py                     # 16/0 (H145 zavřeno)
python _analyza\p28-b-mutace.py                   # 30/0
python _analyza\p29-a-overeni.py --jen A1M13      # 8/0 + úklid mutantů
python _analyza\p32-sonda-h139.py                 # sonda H139/H140/H141
python _analyza\g3-brany.py                       # 49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače
node tools\validate-all.mjs                       # 0 problémů
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\kronika-kontrola.py               # SEDÍ + id 1..47 bez děr
python _analyza\handoff-kontrola-uplnost.py       # 0 chybějících
python _analyza\ov-g-neovereno.py                 # 0 NEOVĚŘENO, rozsah 99 řádků Hxx
python _analyza\zadani-kontrola.py                # kotva zadání P33 vs. živý HEAD
```
"""

# ═══════════════════════════════════════════════════════════ KRONIKA ═══
RADEK_47 = (
    "| **47** | **9. 10. 2026** (17:56–20:23 +02:00) | **ověřovací (Úkol A: "
    "přeměření P31) + akční (Úkol B: C2′, C3′ + H145)** | "
    "**PŘEMĚŘIT PRÁCI P31 VLASTNÍM MĚŘIDLEM A ZAVŘÍT TŘI VADY.** "
    "**VLASTNÍ MĚŘIDLO:** `_analyza/p32-a-overeni.py` (B0–B5) → plný běh "
    "**51 kontrol, 0 chyb, 2 pojmenované ROZDÍLY, 0 NEZMĚŘENO**; **B1** VLASTNÍ "
    "diferenciály (ne opisy P31): živá `kotva_m1` `((1,0),(1,0))` vs. oslabená "
    "kopie s PŮVODNÍ vadou `((1,5),(1,1))` (kotva je dnes v dokumentu 5×, v §57 1×); "
    "vlastní běh `p28-b-mutace.py` **30/0** (1 106 s); živé `p29-a --jen A1M13` "
    "**8/0** a ŽÁDNÝ mutant vs. oslabená kopie bez úklidu (`_analyza/p29-mut-handoff.md` "
    "**211 226 B** + `_analyza/p29-mut-ovg.py` 8 545 B, hlásí CHYBA); **B2** P32 NIC "
    "NENASADILA: `41aa981` i `d3f1a48` mají **0** souborů z `conductor/` a "
    "`.github/`, `ls-remote` = `HEAD` = `d3f1a48`, nasazený kód `cf1f280` "
    "(`deploy.yml` #35 `completed/success`), živá služba `/tasks/cleanup {dry_run}` "
    "→ **osiřelých 0**; **B3** shoda u `test-tick-offline` 215/0, `over-skilly` 92/0, "
    "`p29-b6-mutace` 15/0, `over-dokumentaci` 64/0, `p28-b-mutace` 30/0, `ov-g` "
    "99 řádků Hxx a 0 NEOVĚŘENO, registr 49 bran, `kronika SEDÍ`, `handoff 0 "
    "chybějících`; ROZDÍL jediný: §62.5 tvrdí u kroniky **45 řádků**, naměřeno "
    "**46** (H143). **PŘEMĚŘENÍ P31:** `p31-mutace.py` **24/0** (1 058 s) a "
    "`p31-a-overeni.py --plne` **43 kontrol, 5 chyb, 2 ROZDÍLY, 1 NEZMĚŘENO** — "
    "tvrzení §62 „54/1/2/0“ se **NEREPRODUKUJE** (H145): **4 z 5 chyb mají JEDEN "
    "kořen** — P31 do §62 **citovala** kotvu `test-tick-offline → 215/0`, čímž ji "
    "ZDVOJILA → `p30-mutace.py` spadl na `ValueError` (exit 1, žádný čítač) a "
    "diferenciál A1 se stal NEZMĚŘENÝM; pátá chyba je **H135** (`p30-a` 32/3). "
    "**ÚKOL B — TŘI ZAVŘENÉ VADY:** **C3′/H139 → H140+H141:** `p22-test-mutace.py` "
    "**19/1 → 20/0** — kontrola hledala `0 mrtvých` PODŘETĚZCEM a `40 mrtvých` ji "
    "uspokojilo (zdravá `92 zmínek, 0 mrtvých` → zmutovaná `43 zmínek, 40 mrtvých`); "
    "závěr P31 „mutace nic nemění“ je VYVRÁCENÝ. **C2′/H136 → H142:** "
    "`p27-dopln-zaznamy.py` dnes ověří kotvy PŘED zápisem a při neshodě NEZAPISUJE "
    "(`p32-test-zapis-kotvy.py` **16/0** s diferenciálem: oslabená kopie fixturu "
    "ZAPÍŠE, CRLF → LF; živý běh nad reálnými dokumenty: exit 1 a **0 zapsaných "
    "bajtů**). **H145:** kotva vzata z MĚŘENÉHO oddílu §60 + P0 ověřuje obojí "
    "v JEDNÉ kontrole (přidání další by posunulo baseline §61 — churn H135) + "
    "dvojznačná kotva se hlásí POJMENOVANĚ → `p30-mutace.py` **16/0** (bylo exit 1) "
    "a `p31-a-overeni.py --jen A1 --plne` **11/0** (bylo 3 chyby + 1 NEZMĚŘENO). "
    "**MUTAČNÍ DŮKAZ OPRAV:** `_analyza/p32-mutace.py` → **18/0** (měřidlo nad "
    "zmutovanou KOPIÍ §62 spadne a živý dokument se nezmění; kontrola P22 oslabená "
    "na `(0,0)` spadne; patcher má diferenciál). **H146:** plný běh `p29-a-overeni.py` (jak ho pouští dávka dokladů) nechal v živém `_analyza/` `p29-kopie-tick.mjs` (**75 395 B**) — úklid H124 byl jen v A1M/A1M13, ale kopie se tvoří až v A3; dnes je úklid v `finally` i tam (`--jen A3` → **17/0**). **PLÁN:** dodatek P32 | **—**"
)

NALEZY_225 = r"""
### 2.25 Nálezy z P32 (9. 10. 2026) — vlastní záznam rozbil dvě měřidla a kontrola, kterou uspokojilo „40 mrtvých“

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P33.

| # | Nález | Doklad |
|---|---|---|
| **H140** | **KONTROLA V `p22-test-mutace.py` SE NECHTĚLA USPOKOJIT PODŘETĚZCEM.** Podmínka `"0 mrtvých" not in v1` je **podřetězcová** — a `"40 mrtvých"` řetězec `"0 mrtvých"` **obsahuje**, takže test hlásil CHYBA i nad SPRÁVNĚ zmutovanou bránou; prošlo by i 10/20/30 mrtvých (každé číslo končící nulou). Naměřeno: zdravá brána `92 zmínek, 0 mrtvých`, zmutovaná `43 zmínek, 40 mrtvých` (exit 0 → 1). **Opraveno:** čítač se **PARSuje z MĚŘENÉHO řádku** (`Cesty k nástrojům: N zmínek, M mrtvých`) a porovnává se jeho hodnota; přibyla i kontrola zdravého stavu `(92, 0)` → **20/0** (bylo 19/1). Je to táž past, kterou projekt zná jako „brána našla řetězec na jiném místě“ (§10.1 skillu `overovani`). | `_analyza/p22-test-mutace.py`, `_analyza/p32-sonda-h139-vystup.txt`, `_analyza/p32-mutace-vystup.txt` (M2), `_analyza/p32-a-overeni-vystup.txt` (B4) |
| **H141** | **ZÁVĚR P31 „MUTACE `REPO` NIC NEZMĚNÍ“ JE VYVRÁCENÝ.** H139 tvrdila, že mutace `REPO` v `tools/over-skilly.py` nic nemění, protože brána uznává cesty i v sourozeneckých projektech. **Sonda `_analyza/p32-sonda-h139.py` naměřila opak:** zdravá brána `92 zmínek, 0 mrtvých` (exit 0) → zmutovaná `43 zmínek, 40 mrtvých` (exit 1) — **verdikt se MĚNÍ**, mutace tedy MĚŘENOU VĚC zasahuje. Vadná byla **KONTROLA** (H140), ne mutace. **Poučení:** *„mutace nic nemění“ je tvrzení o KONTROLE, dokud se nezměří i to, co kontrola tvrdí* — a rozdíl je vidět jen tam, kde se čítač čte z měřeného řádku. | `_analyza/p32-sonda-h139.py` (tvary NFC/NFD + čítač řádku), `_analyza/p32-sonda-h139-vystup.txt`, `_analyza/p22-test-mutace.py` |
| **H142** | **KOŘEN H130 ZAVŘEN: PATCHER ZAPISOVAL I BEZ NALEZENÉ KOTVY.** `p27-dopln-zaznamy.py` měl v `vymen()` zápis `cesta.write_bytes(...)` **bez podmínky** — když kotvu nenašel, soubor **přesto zapsal** (a `exit 1` hlásal až potom); dávka dokladů i ruční běh tím přepsaly živý dokument a **převedly konce řádků** (CRLF → LF). `PRESKIP` tu vadu jen schovával před dávkou. **Opraveno:** kotvy se ověří **PŘED** zápisem, při neshodě se **nezapisuje vůbec** (a hlásí se to); i blok, který vkládá nálezy do §57, je
hlídaný markerem. **Test, který to ZAVOLÁ:** `p32-test-zapis-kotvy.py` → **16/0** — živý patcher nad fixturami s chybějícími kotvami: `exit 1` a fixtura **bajt na bajt nedotčená**; **oslabená kopie s PŮVODNÍM `vymen()`** fixturu **ZAPÍŠE** (bajty se změní) → kontrola měří. Živý běh nad reálnými dokumenty: `exit 1` a **hash před/po shodný** = 0 zapsaných bajtů. | `_analyza/p27-dopln-zaznamy.py` (`vymen`), `_analyza/p32-test-zapis-kotvy.py`, `_analyza/p32-a-overeni-vystup.txt` (B4), `_analyza/p20-d-doklady.py` (`PRESKIP`) |
| **H143** | **§62.5 TVRDÍ U KRONIKY 45 ŘÁDKŮ, NAMĚŘENO 46.** Záznam P31 vznikl **před zápisem vlastního řádku session** (řádek 46 = P31), takže jeho stavový blok uvádí počet o jedna nižší; totéž číslo vypisuje i `p31-a-overeni.py` A3 jako pevnou poznámku („řádek 46 přibude v této session“). **Není to vada nástroje** — je to **vnitřní nesouhlas záznamu** a doklad pravidla, že stav se čte z živého měření, ne z dokumentu. P32 to zapsala jako ROZDÍL, ne jako chybu. | `_analyza/p32-a-overeni-vystup.txt` (B3, okno §62.5), `_analyza/kronika-kontrola.py` (46 → po P32 47), `_analyza/p31-a-overeni.py` (A3 poznámka) |
| **H144** | **KOTVA `99 řádků Hxx` JE V `HANDOFF.md` 5×, V §57 1× — P31 PSALA 3×.** P31 v §62.2 tvrdila, že kotva je v dokumentu 3×; její **vlastní záznam si dvě přidala** (cituje ji). Diferenciál opravy H131 proto dnes měří `((1,5),(1,1))` místo `((1,3),(1,1))` — **mechanika opravy je potvrzená** (kotva se počítá v MĚŘENÉM oddílu), ale **číslo v záznamu zestárlo**. Je to argument pro to, aby čísla o výskytech kotvy byla **měřená**, ne psaná do záznamu. | `_analyza/p32-a-overeni-vystup.txt` (B0/B1a), `_analyza/p31-mutace-vystup.txt` (C1-b), `HANDOFF.md` §57 vs. celý dokument |
| **H145** | **VLASTNÍ ZÁZNAM P31 ZDVOJIL KOTVU — A DVĚ MĚŘIDLA TÍM PŘIŠLA O DIFERENCIÁL.** P31 do §62.2 **citovala** přesně kotvu `test-tick-offline → 215/0` → kotva byla v dokumentu **2×** → `mutuj` vyhodil `ValueError: kotva je v souboru 2×` → `p30-mutace.py` skončil **exit 1 bez čítače** a diferenciál `p31-a-overeni.py` A1 se stal **NEZMĚŘENÝM**. **Plný běh P31 se proto NEREPRODUKUJE: 54/1/2/0 → 43/5/2/1** (4 z 5 chyb = tento kořen, pátá = H135). Je to **tatáž past jako H131**, jen na kotvě DOKUMENTU: *záznam, který tvrzení cituje, rozbije měřidlo vázané na jediný výskyt v CELÉM dokumentu* — a druhá polovina: **měřidlo, které na to spadne, hlásí míň** (traceback místo pojmenované chyby). **Oprava:** kotva z MĚŘENÉHO oddílu §60 + kontrola, že leží v něm, **v jedné** kontrole (aby se neposunul čítač 16 → 17 a baseline §61 — churn H135) + dvojznačná kotva se hlásí **pojmenovaně** a zbytek testu doběhne. **Důkaz:** `p30-mutace.py` **16/0** (před: exit 1 + ValueError), `p31-a-overeni.py --jen A1 --plne` **11/0** (před: 3 chyby + 1 NEZMĚŘENO). | `_analyza/p31-a-overeni-p32-vystup.txt` (43/5/2/1), `_analyza/p31-a1-po-oprave-vystup.txt` (11/0), `_analyza/p30-mutace.py` (`KOTVA_DOK`, `sekce("60")`), `_analyza/p30-mutace-vystup.txt` (16/0) |
| **H146** | **H124 MĚLA DÍRU: PLNÝ BĚH `p29-a-overeni.py` NECHTE V ŽIVÉM `_analyza/` KOPII TESTU TIKU.** Naměřeno 9. 10. 2026 v P32 **jako necommitnutý artefakt** (`git status` → `?? _analyza/p29-kopie-tick.mjs`, **75 395 B**, mtime 20:14:11): úklid mutantů (`uklid_mutanty()`) byl jen v etapách **A1M** a **A1M13**, ale kopie `p29-kopie-tick.mjs` se tvoří **až v etapě A3** — a **dávka dokladů `p20-d-doklady.py` pouští plný (výchozí) režim**, kde A3 je. Pojistka dávky to **nemohla vidět**: hlídá **4 dokumenty**, ne `_analyza/`. P31 přitom H124 zapsala jako **ZAVŘENO** — a její důkaz (`--jen A1M13`) tenhle kód **vůbec nespustí**, takže zavření platilo jen pro jednu větev. **Opraveno:** úklid je v `finally` i v A3 a jeho kontrola je součástí výsledku → `python _analyza\p29-a-overeni.py --jen A3` → **17/0** a kopie po běhu **neexistuje**. **Poučení:** *„vada je zavřená“ je tvrzení o CESTĚ, kterou jsem měřil* — zbytek téhož nástroje je pořád nezměřený. | `git status --porcelain` (`?? _analyza/p29-kopie-tick.mjs`, 75 395 B), `_analyza/p31-a4-davka-vystup.txt` (`exit=1 p29-a-overeni.py 423.0s`), `_analyza/p29-a-overeni.py` (A3 `finally`), běh `--jen A3` → **17/0** |
"""

PLAN_DODATEK = r"""
---

## P32 (9. 10. 2026) — CO JE OPRAVENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, **~20:23 +02:00**. Platí pro stav po P32;
> kdo to čte později, **přeměří** (`python _analyza\p32-a-overeni.py --plne`).

**Hotovo (neopakovat):** P31 je **přeměřená vlastním měřidlem**
(`_analyza/p32-a-overeni.py` → **51/0**, 2 ROZDÍLY, 0 NEZMĚŘENO) a jsou
**zavřené tři vady**:

1. **C3′/H139 → H140 + H141:** kontrola v `p22-test-mutace.py` se nechala
   uspokojit **podřetězcem** (`"0 mrtvých"` je v `"40 mrtvých"`); dnes se čítač
   **parsuje z měřeného řádku** → **20/0** (bylo 19/1). Závěr P31 *„mutace nic
   nemění“* je **vyvrácený** (sonda `p32-sonda-h139.py`: 92/0 → 43/40).
2. **C2′/H136 → H142:** `p27-dopln-zaznamy.py` **zapisoval i bez kotvy**; dnes
   se kotvy ověří PŘED zápisem a při neshodě se **nezapisuje** →
   `p32-test-zapis-kotvy.py` **16/0** (s diferenciálem).
3. **H145:** **vlastní záznam P31 zdvojil kotvu** `test-tick-offline → 215/0`,
   čímž shodil `p30-mutace.py` (ValueError) a diferenciál A1; dnes je kotva
   z **MĚŘENÉHO oddílu** §60 a dvojznačná kotva se hlásí pojmenovaně →
   `p30-mutace.py` **16/0**, `p31-a-overeni.py --jen A1 --plne` **11/0**.

**Nejbližší práce (P33) — v tomto pořadí:**

1. **H133 — `p28-a-overeni.py` A6 čeká `g3 → exit 0`**, ale `g3` končí `exit 1`
   **pojmenovaně** (1 brána bez čítače: `mutace B (combat)`). Baseline A6 má proto
   **trvale 1 chybu**; buď stav deklarovat (`OCEKAVANE_*`-style), nebo vázat na
   pojmenovaný stav.
2. **H112 — brána „cron běží (čas)“ nemůže selhat** (`validate-all` testuje jen
   `!!h.time`) — a přesně ten tik se 9. 10. zastavil.
3. **C4′ — zavádějící komentáře v conductu** (`index.ts:1558–1559`,
   `:1489–1493`): změna textu = **změna kódu → nasazení z pushe** (tři kroky).
4. **B3 (`/game/active {active:false}`)** — čeká na výslovné „ano“ uživatele.
5. **H143/H144 zůstávají jako poučení**: čísla o výskytech kotvy a o počtu řádků
   se **měří**, neopisují do záznamu (a záznam, který kotvu cituje, mění
   jednoznačnost kotev měřidel).

**Co NEDĚLAT:** nepsat do hry; nepouštět harness z `g3` bez
`FORGE_REGISTR`/`FORGE_BEZ_REGISTRU` (H137); nemazat
`E:\Workspaces\_acl-oprava-p31\`; **needitovat záznamy** (HANDOFF/KRONIKA se jen
doplňují) — měřidlo se opravuje, záznam ne.
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--kontrola", action="store_true", help="jen ověřit, nezapisovat")
    args = ap.parse_args()

    h = HANDOFF.read_text(encoding="utf-8")
    k = KRONIKA.read_text(encoding="utf-8")
    p = PLAN.read_text(encoding="utf-8") if PLAN.is_file() else ""

    uz_h = "## 63. P32" in h
    uz_k = bool(re.search(r"^\|\s*\*\*47\*\*\s*\|", k, re.M))
    if uz_h and uz_k:
        print("  OK    záznamy P32 UŽ JSOU zapsané (HANDOFF §63 + KRONIKA řádek 47) "
              "— idempotentní běh, nic se nemění")
        chybejici = [n for n in range(1, 48)
                     if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k, re.M)]
        check("KRONIKA: id 1..47 bez děr (i při idempotentním běhu)", chybejici, [])
        print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
        return 0 if not chyb else 1

    check("HANDOFF §63 ještě NENÍ (skript je idempotentní)", uz_h, False)
    check("KRONIKA řádek 47 ještě NENÍ", uz_k, False)
    check("KRONIKA má řádek 46 (kotva pro vložení)",
          bool(re.search(r"^\|\s*\*\*46\*\*\s*\|", k, re.M)), True)
    check("KRONIKA má oddíl §2.24 (kotva pro §2.25)", "### 2.24" in k, True)
    check("PLAN existuje a je neprázdný", bool(p.strip()), True)
    check("PLAN dodatek P32 ještě NENÍ (idempotence)", "## P32 (9. 10. 2026)" in p, False)
    hxx_pred = len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h, re.M))
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v kotvách)" % len(chyb))
        return 1

    # (1) KRONIKA: řádek 47 hned za řádek 46; §2.25 před "## 3."
    radky = k.splitlines()
    i46 = next(i for i, l in enumerate(radky) if re.match(r"^\|\s*\*\*46\*\*\s*\|", l))
    i3 = next(i for i, l in enumerate(radky) if l.startswith("## 3."))
    check("řádek 46 je PŘED oddílem §3 (jinak by vložení rozbilo tabulku)", i46 < i3, True)
    novy_k = radky[:i46 + 1] + [RADEK_47] + radky[i46 + 1:i3] + [NALEZY_225.strip(), ""] + radky[i3:]
    k_new = "\n".join(novy_k) + "\n"

    # (2) HANDOFF: §63 na konec
    h_new = h.rstrip("\n") + "\n" + HANDOFF_63.strip("\n") + "\n"

    # (3) PLÁN: dodatek na konec
    p_new = (p.rstrip("\n") + "\n" + PLAN_DODATEK.strip("\n") + "\n") if p else ""

    # ── ověření PŘED zápisem ──────────────────────────────────────────────
    check("HANDOFF: přibyl právě oddíl §63", "## 63. P32" in h_new and len(h_new) > len(h), True)
    check("HANDOFF: řádků neubylo", len(h_new.splitlines()) > len(h.splitlines()), True)
    check("HANDOFF: každý nález H140..H145 je zmíněn (mapovací seznam)",
          all(("H%d" % n) in h_new for n in range(140, 146)), True)
    check("HANDOFF: NEPŘIBYL žádný tabulkový řádek `| **Hxx** |` (jinak spadne ov-g)",
          len(re.findall(r"^\|\s*\*\*H\d+\*\*\s*\|", h_new, re.M)), hxx_pred)
    check("KRONIKA: přibyl řádek 47",
          bool(re.search(r"^\|\s*\*\*47\*\*\s*\|", k_new, re.M)), True)
    check("KRONIKA: id 1..47 bez děr",
          [n for n in range(1, 48)
           if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k_new, re.M)], [])
    check("KRONIKA: nálezy H140..H145 jsou v textu",
          all(("**H%d**" % n) in k_new for n in range(140, 146)), True)
    check("KRONIKA: nic neubylo (řádků přibylo)",
          len(k_new.splitlines()) > len(k.splitlines()), True)
    check("KRONIKA: řádek 47 má datum a typ",
          bool(re.search(r"^\|\s*\*\*47\*\*\s*\|\s*\*\*9\. 10\. 2026\*\*", k_new, re.M)), True)
    check("KRONIKA: řádek 47 má uvedený typ z nabídky",
          any(t in RADEK_47 for t in ("akční", "plánovací", "ověřovací", "analýza",
                                      "rozhodovací")), True)
    check("PLÁN: přibyl dodatek", len(p_new) > len(p), True)

    if args.kontrola:
        print("KONTROLA OK — nic se nezapsalo (--kontrola)")
        return 0 if not chyb else 1
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v ověření)" % len(chyb))
        return 1

    HANDOFF.write_bytes(h_new.encode("utf-8"))
    KRONIKA.write_bytes(k_new.encode("utf-8"))
    if p_new:
        PLAN.write_bytes(p_new.encode("utf-8"))
    print("  zapsáno: HANDOFF.md §63, KRONIKA řádek 47 + §2.25, PLAN dodatek P32")
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
    return 0 if not chyb else 1


if __name__ == "__main__":
    sys.exit(main())

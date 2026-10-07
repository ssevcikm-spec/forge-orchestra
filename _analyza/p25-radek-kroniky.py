# -*- coding: utf-8 -*-
r"""P25 — zápis záznamů: HANDOFF §55, KRONIKA řádek 40 + §2.18, kontrola NEOVĚŘENO.

PROČ SKRIPTEM: řádky tabulky §1 kroniky mají **přes 2000 znaků**, takže kotva
z načteného řádku by ho NAHRADILA zkráceným textem (omyl **194**, **206**).
Skript vkládá CELÝ text a je **idempotentní** (podruhé jen ověří, že tam je).

Co zapisuje:
  1. `HANDOFF.md` — nový oddíl **§55** (záznam o provedení P25 + stav) na KONEC;
  2. `KRONIKA-PROJEKTU.md` — řádek **40** do §1 (ZA řádek 39) a oddíl **§2.18**
     s nálezy (PŘED §3);
  3. kontrolu, že nezůstalo `NEOVĚŘENO` — měřidlem `ov-g-neovereno.py`.

⚠ OMYLY SE OD 6. 10. 2026 NEVEDOU: do sloupce omylů patří `—` a souhrn §3
se **nepřepočítává** (P25 ho proto jen ověří, že zůstal doslova).

Použití: python _analyza/p25-radek-kroniky.py
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

# ── 1) HANDOFF §55 ──────────────────────────────────────────────────────────
ODDIL_55 = r"""

---

## 55. P25 — PŘEMĚŘENÍ P24 A TESTOVÁNÍ ZAPISUJÍCÍCH ENDPOINTŮ (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P25 + stav po P25**. Plní i slot,
na který §54 **visutě odkazoval** („stav je v novém oddílu 55“) — oddíl 55 do
P25 **neexistoval** a to je samo nález (níž, bod 1). **Pravidla** v `AGENTS.md`,
**projektová znalost** v `PROVOZ-ORCHESTRA.md`, **historie** v
`KRONIKA-PROJEKTU.md` (řádek **40**, nálezy **§2.18**). Zadání P25 je
v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 13:0x–14:2x +02:00**. Tvrzení
> o **stavu** (HEAD, hra, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\p25-a-overeni.py --plne`).

### 55.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Přeměření práce P24 VLASTNÍM měřidlem** (A1–A6, každý bod jiným postupem, než vznikl) | `_analyza/p25-a-overeni.py` → **53 kontrol, 0 chyb** (první běh měl 6 chyb — všechny typu „číslo se změnilo, a ještě není zapsané“; to je správné chování, po zapsání tohoto oddílu 0) |
| **A** | **Důkaz, že i tohle měřidlo umí spadnout** — 5 mutací v **KOPIÍCH** + diferenciál + rozhodovací funkce A3 | `_analyza/p25-b-mutace.py` → **27 kontrol, 0 chyb** |
| **B1** | **Testy pro endpointy, které ZAPISUJÍ do D1 a MĚNÍ CHOVÁNÍ služby**: `POST /task`, `POST /game`, `POST /game/active` — včetně integrační kontroly, že vypnutá hra zastaví dispatch | `tools/test-tick-offline.mjs` → **146/0** (146 kontrol, 0 chyb; bylo **100/0**) |
| **B1** | **Mutační důkaz k novým cestám** — 5 nových vrat (M16–M20) | `_analyza/tick-mutace.py` → **20 vrat / 41/0** (bylo 15 vrat / 31/0) |
| **C** | Brány po sobě (po přegenerování inventáře) | `g3` → **49 bran**, 1 deklarovaný nenulový exit (`zadání kontrola`), `exit 0` · `validate-all` → **VŠE V POŘÁDKU** · `kronika-kontrola` → **SEDÍ** · `handoff-kontrola-uplnost` → **83/83** |

### 55.2 Nálezy P25 (každý doložený měřením)

1. **§54 OBSAHUJE VISUTÝ ODKAZ NA ODDÍL 55, KTERÝ NEEXISTOVAL.** §54 tvrdí
   „stav je v `§53` … a v novém oddílu **55** (stav po P24)“ — a `## 55.`
   v `HANDOFF.md` nebylo (nejvyšší oddíl byl 54). Tenhle oddíl slot plní, ale
   jako záznam **P25**. **Poučení: odkaz na oddíl je TVRZENÍ o dokumentu**
   a `handoff-kontrola-uplnost` kontroluje klíče, ne cíle odkazů.
2. **DOBOVÁ KOTVA P24 PŘESTALA PLATIT, PROTOŽE SE ZMĚNIL STAV — ne proto, že
   by měřidlo lhalo.** `p24-a-overeni.py` dnes vrací **99/1** (na kotvě
   `4925f64` naměřila **99/0**): jediná červená je **A8** — `uo-shadows` je dnes
   **`932dc6f`**, ne `44dd454`. To je **správné chování** měřidla: měří živý
   stav, ne zamrzlý text (A8 je v P24 označená jako `DOBOVÉ`). První dnešní běh
   dal **99/4** — další tři červené byly A6 („dokument netvrdí naměřené 146/0
   a 41/0“), tedy **následek mojí vlastní práce B1**; po zapsání tohoto oddílu
   zmizely.
   **Co hru změnilo:** souběžná session (generalizace nástrojů) do ní
   **7. 10. 2026 přidala commit** `932dc6f` (`AGENTS.md` + `docs/BRANY-HRY.md`)
   a **pushla ho**, i když uživatel hru pozastavil. **Není to moje práce** —
   je to zapsané jako změna stavu, která P24inu A8 dělá dobově neplatnou.
3. **ZARÁŽKA V ROUTERU ZAPNE PRÁVĚ TY KONTROLY, KTERÉ MÁ — a `/tick` zůstane
   zelený.** A3 vložila do živého `conductor/src/index.ts` (v `try/finally`,
   s ověřením hashe před i po) návrat `599` pro pět endpointů: test tiku vykázal
   **42 červených**, mezi nimi **všech 5 cílených** (`N`, `O`, `P`, `Q`, `R`),
   a **kontrolní `A: /tick odpoví 200` zůstala zelená**. Druhá zarážka
   **uvnitř handleru** `/tasks/cleanup` (změna hlášky pojistky) zapnula
   **právě 1** kontrolu (`Q2: a řekne PROČ`) a `Q2: nenačtená roadmapa → 503`
   zůstala zelená. **Tím je doloženo, že test endpointy opravdu VOLÁ** a že
   kontroly nejsou měkké (past P24-I).
4. **⚠ SABOTÁŽ SE TICHE NEPROVEDLA — a odhalil to až DIFFERENCIÁL.** Vlastní
   měřidlo mělo spustit `p24-b-mutace.py` nad **oslabenou** kopií měřidla (bez
   kontroly `B4`). Kotva v cizím skriptu je ale **`ANALYZA` (s Y)**, ne
   `ANALIZA` (s I) — `replace()` tedy **nic nenahradil** a sabotovaný důkaz
   hlásil `17/0` nad **NEZMĚNĚNÝM** skriptem. Přesně past `overovani` §7.9
   („mutace, která se tiše neprovede, vypadá jako úspěch“). Zachytil to
   **diferenciál** (originál na téže vadě spadne, oslabená kopie projde);
   měřidlo dnes **explicitně kontroluje, že sabotáž míří na oslabenou kopii**.
5. **VLASTNÍ MĚŘIDLO MĚLO TŘI VADY A VŠECHNY ODHALIL JEHO BĚH** (ne čtení):
   (a) práh „aspoň 20 kontrol“ v režimu `--jen-dokumenty`, který měří **8**;
   (b) A2 klasifikoval **JS literály** (`, watchdog: ${eskalovano}` a log-prefix
   `roadmap.eskalovano: `) jako SQL → falešný poplach „nesklasifikovaný zápis“;
   (c) jednoduchý vzor `[^…\n]` **nenašel víceřádkový SQL literál** → falešný
   poplach „nikde není výběr kandidátů“. Všechny tři jsou **falešné poplachy
   nad správným zdrojem** — nejdražší druh vady (`overovani` §8.3).
6. **TRVALOST ZNAČKY `eskalovano` JE DOKÁZANÁ Z KÓDU, NE Z DOJMU.** Vlastní
   čtení **SQL literálů po odstranění komentářů** našlo: samomigraci
   `ALTER TABLE roadmap ADD COLUMN eskalovano TEXT`, **právě jeden** zápis
   (`SET eskalovano = datetime('now')`), **žádné** mazání a filtr kandidátů
   `status <> 'done' AND (eskalovano IS NULL OR eskalovano = '')`. Živé `/tick`
   pak hlásí **`0 ohlášeno` (prah 3 < strop 5)** — kontrola „ohlásil něco“
   (`N > 0`) by tedy **shodila zdravou službu**. Negativní kontrola: po vložení
   mazacího `UPDATE` do KOPIE zdroje predikát vadu **ohlásí**.
7. **`tick-mutace.py` NEVYKAZOVAL POČET VRAT.** Číslo „15 vrat“ žilo jen
   v dokumentech. Měřidlo ho proto odvozuje **dvěma nezávislými cestami** (AST
   zdroje: počet `MUTATIONS`; aritmetika z běhu: `1 + 2×vrat`) a doklad ho od
   P25 **vypisuje sám** (`vrat: 20`).
8. **NENULOVÝ EXIT NENÍ VŽDY NÁLEZ — MŮŽE BÝT STAV.** Po přidání dokladů měl
   `g3` **6 nenulových exitů**: tři byly **zastaralý inventář** (náprava je
   přegenerovat, **ne deklarovat** — deklarace by z trvalé vady udělala
   „očekávaný stav“) a dva **moje vlastní chyba v textu skillu** (`tools\…`
   v tabulce vzal `over-skilly` jako mrtvou cestu). Po nápravě **49 bran,
   1 deklarovaný exit**. Měřidlo proto „nedeklarovaný exit“ **rozlišuje** na
   nález a na pojmenovaný stav.
9. **`/task`, `/game` a `/game/active` UŽ MAJÍ TEST — a test měří i CHOVÁNÍ.**
   Nově se ověřuje, že payload jde do D1 jako **JSON řetězec**, že `target: lan`
   se opravdu uloží jako `lan`, že registrace hry ji **ZAPNE** (`active = 1`),
   že vypnutí zapíše **`active = 0`** (a ne 1), že neznámá hra vrátí **404** —
   a hlavně **integrační kontrola W**: po `/game/active {active:false}` tik
   **NEDISPATCHUJE** a po zapnutí dispatchuje **právě jednou**.
10. **⚠ SANDBOX ODEMKL ZÁPIS PODPROCESŮM V PODADRESÁŘÍCH.** V první polovině
    session nešlo zapsat soubor podprocesem do **žádného** podadresáře
    workspace (`PermissionError [Errno 13]`), zatímco do kořene ano; nástroj
    `write` (harness) přitom zapsal i do podadresáře. **Nebyla to vada
    skriptů** — spadlo na tom celé měřidlo P24 (11 `PermissionError`, mutace se
    vůbec neprovedly) a `git fetch` (`.git/FETCH_HEAD`). Opravný skript ACL
    vrátil `VERDICT=NOT_THIS_CLASS`; pomohlo až **přepnutí session na plný
    přístup**. Past je zapsaná ve skillu `dsh-prostredi` §4e.

### 55.3 Živý stav při zápisu (7. 10. 2026, ~14:2x +02:00)

```
orchestra: HEAD 92aa80a · origin/main 92aa80a · nepushnutých commitů 0
           (e401f6f, 22cebce i 92aa80a jsou práce SOUBĚŽNÉ session — P24inu
            práci commitla a pushla ONA, ne já)
hra:       HEAD 932dc6f · origin/main 932dc6f · strom čistý · 0 nepushnutých
živá služba: /health → ok=true ready=2 running=0 games=1 · targets[0] main_ci
             (ci.yml #118 na 932dc6f), forge.ok=false, selhani_v_rade=20
             /tick → watchdog: 0 ohlášeno (prah 3)
brány:     g3 → 49 bran, 1 deklarovaný nenulový exit (zadání kontrola), exit 0
```

### 55.4 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p25-a-overeni.py --plne   # A1-A6: 53 kontrol, 0 chyb
python _analyza\p25-b-mutace.py           # umí to spadnout? 27 kontrol, 0 chyb
node tools\test-tick-offline.mjs          # 146/0
python _analyza\tick-mutace.py            # 20 vrat / 41/0
python _analyza\p24-a-overeni.py          # 99/1 (A8: hra je na 932dc6f, ne 44dd454)
python _analyza\p24-b-mutace.py           # 17/0
python _analyza\g3-brany.py               # 49 bran, 1 deklarovaný exit
node tools\validate-all.mjs               # VŠE V POŘÁDKU
```
"""

# ── 2) KRONIKA: řádek 40 ────────────────────────────────────────────────────
RADEK_40 = (
    "| **40** | **7. 10. 2026** (13:0x – 14:2x +02:00) | "
    "**ověřovací (Úkol A) + akční (Úkol B1)** | **Přeměřit práci P24 VLASTNÍM "
    "měřidlem — a zavřít slepá místa endpointů, které ZAPISUJÍ do D1.** Zadání "
    "P25 §2.1: záznamy P24 psal autor, který si je sám ověřoval („autor není "
    "nezávislý reviewer“), takže se musí přeměřit i ony. Provedeno: **A1–A6 "
    "vlastním postupem** (`_analyza/p25-a-overeni.py`, 53/0) + **důkaz, že to "
    "měřidlo umí spadnout** (`p25-b-mutace.py`, 27/0, pět mutací v KOPIÍCH) a "
    "**Úkol B1** — testy pro `POST /task`, `/game`, `/game/active` | **Brány:** "
    "`test-tick-offline` **146/0** (bylo 100/0) · `tick-mutace` **20 vrat / "
    "41/0** (bylo 15/31) · `g3` **49 bran**, 1 deklarovaný nenulový exit "
    "(`zadání kontrola`), exit 0 · `validate-all` **VŠE V POŘÁDKU** · "
    "`kronika-kontrola` **SEDÍ** · `handoff-kontrola-uplnost` **83/83** · "
    "**A2 doloženo ze KÓDU:** `eskalovano` je trvalá značka (jeden zápis, žádné "
    "mazání) → `N>0` by shodilo zdravou službu · **A3:** zarážka v routeru "
    "zapnula **právě 5** cílených kontrol (42 červených) a `A: /tick odpoví 200` "
    "zůstala zelená | **—** | **Nálezy a poučení:** (1) **§54 odkazoval na "
    "oddíl 55, který NEEXISTOVAL** — odkaz na oddíl je tvrzení o dokumentu a "
    "nikdo ho neměřil. (2) **Dobová kotva P24 přestala platit: `p24-a-overeni.py` "
    "dnes 99/1** (na `4925f64` 99/0) — jediná červená je A8, protože souběžná "
    "session přidala do hry commit `932dc6f` a pushla ho; měřidlo tím měří "
    "ŽIVÝ stav, ne zamrzlý text. (3) **Sabotáž se tiše neprovedla:** kotva v "
    "cizím skriptu je `ANALYZA` (s Y), ne `ANALIZA` (s I) → `replace()` nic "
    "nenahradil a důkaz hlásil 17/0 nad NEZMĚNĚNÝM skriptem; odhalil to až "
    "diferenciál (originál spadne / oslabená kopie projde). (4) **Vlastní "
    "měřidlo mělo tři vady a všechny odhalil jeho BĚH:** práh 20 vs. 8 kontrol, "
    "JS literály počítané jako SQL a víceřádkový SQL literál, který vzor bez "
    "`\\n` nenašel — všechny tři falešné poplachy nad správným zdrojem. "
    "(5) **`tick-mutace.py` nevykazoval počet vrat** — číslo žilo jen "
    "v dokumentech; dnes ho doklad vypisuje sám (`vrat: 20`). (6) **Nenulový "
    "exit není vždy nález:** ze 6 červených `g3` byly tři zastaralý inventář a "
    "dva moje chyba v textu skillu (`tools\\…` jako mrtvá cesta) — deklarovat "
    "zastaralý inventář by z trvalé vady udělalo „očekávaný stav“. "
    "(7) **Sandbox odemkl zápis podprocesů v podadresářích** (`PermissionError "
    "13` v `tools`, `_analyza`, `conductor/src`, ale ne v kořeni) — spadlo na "
    "tom celé měřidlo P24 (11 chyb) a `git fetch`; skript ACL vrátil "
    "`NOT_THIS_CLASS`, pomohl až plný přístup; past je ve skillu "
    "`dsh-prostredi` §4e. **Co zůstává:** `/queue`, `/workers`, `/games`, "
    "`/game`, `/failed`, `/status`, `/health` handlerem netestuje žádný test; "
    "slepé místo `over-skilly` (fáze C); rozhodnutí o `.gitattributes` (P24-B); "
    "**B4 ověřit živě** a **B3b zapnout strop** |"
)

# ── 3) KRONIKA: §2.18 ───────────────────────────────────────────────────────
ODDIL_218 = r"""### 2.18 Nálezy z P25 (7. 10. 2026) — přeměření P24 a zavření zapisujících endpointů

**Vznikly tím, že se PRÁCE P24 PŘEMĚŘILA JINÝM MĚŘIDLEM** (ne čtením §54) a že
se test tiku rozšířil na cesty, které **zapisují do D1**. Záznam: `HANDOFF.md`
**§55**; měřidlo: `_analyza/p25-a-overeni.py` (**53/0**) a jeho mutační důkaz
`_analyza/p25-b-mutace.py` (**27/0**).

| # | Co hrozilo / co se tvrdilo | Co naměřeno | Stav |
|---|---|---|---|
| **P25-A** | „§54 je záznam o provedení a stav je v oddílu 55.“ | **Oddíl `## 55.` v `HANDOFF.md` NEEXISTOVAL** — §54 na něj visutě odkazoval. `handoff-kontrola-uplnost` kontroluje klíče, ne **cíle odkazů**, takže to nechytila žádná brána | **DOPLNĚNO**: §55 existuje (tenhle záznam); nález platí pro každý odkaz na oddíl |
| **P25-B** | „P24 naměřila 99/0, takže to platí.“ | Dnes **99/1** (první běh **99/4**): červená je **A8** — hra má `932dc6f`, ne `44dd454`. Další tři byly A6 (dokument netvrdil `146/0` a `41/0`), tedy **následek mojí práce B1**, který zmizel po zapsání záznamu | **SPRÁVNÉ CHOVÁNÍ**: měřidlo měří živý stav; dobová kotva se musí číst s datem |
| **P25-C** | „Když je v handleru zarážka, test to pozná.“ | Zarážka v **routeru** (5 endpointů → `599`) vykázala **42 červených**, mezi nimi **všech 5 cílených**, a `A: /tick odpoví 200` zůstala **zelená**. Zarážka **uvnitř handleru** `cleanup` (změna hlášky) zapnula **právě 1** kontrolu a `503` zůstala zelená | **DOKÁZÁNO**: test endpointy opravdu VOLÁ a kontroly jsou konkrétní, ne měkké |
| **P25-D** | „Oslabená kopie měřidla dokáže, že mutační důkaz umí hlásit nález.“ | **Sabotáž se tiše neprovedla:** kotva v `p24-b-mutace.py` je **`ANALYZA` (s Y)**, ne `ANALIZA` (s I) → `replace()` nic nenahradil a důkaz hlásil `17/0` nad **NEZMĚNĚNÝM** skriptem | **ODHALENO DIFFERENCIÁLEM** (originál spadne, oslabená kopie projde); měřidlo nově kontroluje, že sabotáž **míří na oslabenou kopii** |
| **P25-E** | „Když měřidlo projde, měří to, co tvrdí.“ | **Tři vady vlastního měřidla, všechny odhalil jeho BĚH:** (a) práh „20 kontrol“ v režimu, který měří **8**; (b) A2 počítal **JS literály** (`, watchdog: ${eskalovano}`, log-prefix) jako SQL; (c) vzor `[^…\n]` **nenašel víceřádkový SQL literál** → „nikde není výběr kandidátů“ | **OPRAVENO**; všechny tři byly **falešné poplachy nad správným zdrojem** (`overovani` §8.3) |
| **P25-F** | „`N > 0` u watchdogu znamená, že watchdog funguje.“ | Vlastní čtení **SQL literálů bez komentářů**: samomigrace + **právě jeden** zápis `SET eskalovano = datetime('now')` + **žádné mazání** + filtr `eskalovano IS NULL`. Živé `/tick` hlásí **0 ohlášeno** (prah 3 < strop 5) | **NASTRAŽENÁ OTÁZKA POTVRZENA Z KÓDU**: `N>0` by shodilo zdravou službu; negativní kontrola (mazací `UPDATE` v kopii) vadu **ohlásí** |
| **P25-G** | „Počet vrat mutačního důkazu je 15 (z dokumentu).“ | `tick-mutace.py` počet vrat **nevypisoval** — žil jen v dokumentech. Měřidlo ho odvozuje ze **zdroje** (AST) i z **běhu** (`1 + 2×vrat`) a doklad ho od P25 vypisuje sám (`vrat: 20`) | **OPRAVENO**; číslo bez vykazujícího čítače je opis, ne měření |
| **P25-H** | „Když je `g3` zelený, jsou deklarace exitů v pořádku.“ | Po přidání dokladů měl `g3` **6 nenulových exitů**: tři = **zastaralý inventář**, dva = **moje chyba v textu skillu** (`tools\…` vzal `over-skilly` jako mrtvou cestu). Po nápravě **49 bran, 1 deklarovaný exit** | **ROZLIŠENO**: měřidlo dělí nenulové exity na **nález** a na **pojmenovaný STAV** — deklarovat zastaralý inventář by z vady udělalo „očekávaný stav“ |
| **P25-I** | „Endpointy `/task`, `/game`, `/game/active` netestuje nikdo.“ | Nově je volá skutečný handler: **146/0** (bylo 100/0) — payload jako **JSON řetězec**, `target: lan` uložené jako `lan`, registrace hry ji **ZAPNE** (`active = 1`), vypnutí zapíše **`active = 0`**, neznámá hra **404** — a **integrační kontrola W**: vypnutá hra → tik **NEDISPATCHUJE**, zapnutá → dispatchuje **právě jednou** | **UZAVŘENO** (Úkol B1); mutační důkaz **M16–M20** (20 vrat / 41/0) |
| **P25-J** | „Když podproces nemůže zapsat soubor ve workspace, je to vada skriptu.“ | V `workspace-write` nešlo zapsat podprocesem do **žádného podadresáře** (`PermissionError 13`), ale do **kořene ano**; `write` (harness) zapsal i do podadresáře. Spadlo na tom celé měřidlo P24 (**11 chyb**, mutace se neprovedly) a `git fetch` (`.git/FETCH_HEAD`). Skript `diagnose-windows-sandbox-acl` vrátil `NOT_THIS_CLASS` | **STAV, NE VADA**: pomohlo přepnutí session na **plný přístup**; past ve skillu `dsh-prostredi` **§4e** |
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
print("P25 — zápis záznamů (HANDOFF §55, KRONIKA řádek 40 + §2.18)")
print("=" * 78)

# ── HANDOFF ─────────────────────────────────────────────────────────────────
h_text = H.read_bytes().decode("utf-8")
k("\r" not in h_text, "HANDOFF má LF")
k("## 54. P24 —" in h_text, "§54 (záznam P24) zůstal")
if "## 55. P25 —" in h_text:
    print("  OK    §55 už v HANDOFFu je — nepřidávám")
    kontrol += 1
else:
    H.write_bytes((h_text.rstrip("\n") + "\n" + ODDIL_55).encode("utf-8"))
    h_text = H.read_bytes().decode("utf-8")
    k("## 55. P25 —" in h_text, "§55 vložen na KONEC (nic se nepřepisovalo)")
k("§53" in h_text and "NASZENO A OVĚŘENO ŽIVĚ" in h_text, "§53 zůstal")
k("watchdog: 2 ohlášeno (prah 3)" in h_text, "§53 nese své PŮVODNÍ živé měření")
k(not H.read_bytes().startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")
# Čísla, která musí být v dokumentu ZAPSANÁ (čte je A4 měřidla P25 i A6 P24):
for cislo in ("99/1", "99/4", "17/0", "146/0", "146 kontrol", "41/0",
              "20 vrat", "49 bran", "53 kontrol", "27 kontrol"):
    k(cislo in h_text, f"HANDOFF tvrdí naměřené `{cislo}`")

# ── KRONIKA ─────────────────────────────────────────────────────────────────
puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF")
k("### 2.17 Nálezy z P24" in text, "§2.17 (nálezy P24) zůstal")

zmena = False
if any(r.startswith("| **40** |") for r in radky):
    print("  OK    řádek 40 už v kronice je — nevkládám")
    kontrol += 1
else:
    i39 = next((n for n, r in enumerate(radky) if r.startswith("| **39** |")), None)
    k(i39 is not None, "kotva: řádek session 39")
    if i39 is not None:
        konec = "\n" if radky[i39].endswith("\n") else ""
        radky.insert(i39 + 1, RADEK_40 + konec)
        zmena = True
        k(any(r.startswith("| **40** |") for r in radky), "řádek 40 vložen ZA řádek 39")

if "### 2.18 Nálezy z P25" in text:
    print("  OK    §2.18 už v kronice je — nevkládám")
    kontrol += 1
else:
    i3 = next((n for n, r in enumerate(radky) if r.startswith("## 3. ")), None)
    k(i3 is not None, "kotva: nadpis §3")
    if i3 is not None:
        radky.insert(i3, ODDIL_218 + "\n")
        zmena = True
        k(any("### 2.18 Nálezy z P25" in r for r in radky), "§2.18 vložen PŘED §3")

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
k("| **40** |" in t2, "dokument obsahuje řádek 40")
k("### 2.17 Nálezy z P24" in t2, "§2.17 zůstalo")
k("### 2.18 Nálezy z P25" in t2, "dokument obsahuje §2.18")
# ⚠ SOUHRN SE NEPŘEPOČÍTÁVÁ (omyly se od 6. 10. 2026 nevedou) — ověřuje se
# jen to, že zůstal DOSLOVA (kdyby ho někdo „opravil“, je to nález).
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t2,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN (omyly se nevedou)")

# ── NEOVĚŘENO: měřidlem, ne hledáním slova ──────────────────────────────────
print()
print("--- NEOVĚŘENO: měří se STAV návrhů (NAxx) a nálezů (Hxx) ---")
r = subprocess.run([sys.executable, "-B", str(WS / "_analyza" / "ov-g-neovereno.py")],
                   cwd=str(WS), capture_output=True, timeout=300)
v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
k(r.returncode == 0, "ov-g-neovereno.py → žádný návrh ani nález ve stavu NEOVĚŘENO")
m_nav = re.search(r"návrhů celkem:\s*(\d+)", v)
m_nal = re.search(r"nálezů \(řádků tabulek Hxx\):\s*(\d+)", v)
print("      měřeno: návrhů %s, nálezů %s"
      % (m_nav.group(1) if m_nav else "?", m_nal.group(1) if m_nal else "?"))
k(m_nav is not None and int(m_nav.group(1)) > 0, "měřidlo opravdu otevřelo nějaké návrhy")

print()
print("=" * 78)
print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
print("=" * 78)
for c in chyb:
    print("  CHYBA: %s" % c)
print("HANDOFF sha256: %s" % hashlib.sha256(H.read_bytes()).hexdigest()[:16])
print("KRONIKA sha256: %s" % hashlib.sha256(K.read_bytes()).hexdigest()[:16])

sys.exit(1 if chyb else 0)

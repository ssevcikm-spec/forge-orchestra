# -*- coding: utf-8 -*-
r"""P29 — ZÁPIS ZÁZNAMŮ: HANDOFF §60, KRONIKA řádek 44 + nálezy §2.22, PLÁN.

⚠ PROČ SKRIPTEM (a ne `edit` toolem): řádky kroniky mají **přes 4000 znaků**
a kotva načtená z řádku ho **zkrátí** (omyly 194 a 206). Skript pracuje
s BAJTY, vkládá celé řádky a po zápisu ověřuje, že se nic neztratilo.

⚠ CO SE NESMÍ STÁT: HANDOFF ani KRONIKA se NEPŘEPISUJÍ, jen DOPLŇUJÍ.
Skript proto (a) jen vkládá, (b) před i po měří počty řádků a id,
(c) při jakékoli neshodě skončí `exit 1` a NIC nezapíše.

Použití: python _analyza\p29-zapis-zaznamu.py [--kontrola]
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


# ═══════════════════════════════════════════════════════════ HANDOFF §60 ═══
HANDOFF_60 = r"""
## 60. P29 — PŘEMĚŘENÍ P28 VLASTNÍM MĚŘIDLEM, OPRAVA OSIŘELÝCH GRANULÍ A KONCEPT OD GEMINI (9. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P29 + stav po P29**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**44**, nálezy **§2.22**), plán (`PLAN-DALSI-KROK.md`).
Zadání P29 je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **9. 10. 2026, 00:2x–07:3x +02:00** (živý čas
> z hodin, ne ze zadání — nález P27-O). Tvrzení o **stavu** (HEAD, hra, živá
> služba) platí k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ ŽIVÁ SLUŽBA SE BĚHEM P29 ZASTAVILA V DISPATCHI** (nález P29-D níž):
> ruční `/tick` vrátil `spusteno: 0 úloh` a poslední běh v `/status` byl
> z **8. 10. 21:12 UTC**. To je **stav před opravou** — kód, který to umí
> pojmenovat, je v této session hotový, ale **NENÍ NASAZENÝ** (čeká na push).

### 60.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A1** | **Umí měřidlo P28 spadnout?** — reprodukován jeho vlastní důkaz a přidány **tři VLASTNÍ kontramutace**, každá se **třemi nohami** (živé → baseline; mutant → spadne NA TÉ kontrole; mutant + oslabené měřidlo → projde) | `p28-b-mutace.py` → **27/0** (přeměřeno, tvrzení §59.1 sedí); `p28-a-overeni.py --plne` → **122/14** (přeměřeno, **15,3 min**, tvrzení sedí); vlastní mutace: **M1** (§57 `99 řádků Hxx` → `98`) a **M3** (ov-g hlásí nulový rozsah) → `p29-a1m13-vystup.txt` **7/0**; **M2** (g3 s 50. branou) → `p29-a1m-vystup.txt` (dvě nohy OK, třetí noha doběhla s (12,4) → (11,3)) |
| **A2** | **Volá test tiku sedm endpointů?** — ZARÁŽKOU V HANDLERU (P28 poškozovala odpověď) **a nově i IZOLACÍ**: zarážka na jednom endpointu nesmí zčervenat skupinu jinou | všech 7 endpointů: `X: 12`, `Y: 5`, `Z: 4`, `AA: 8`, `AB: 4`, `AC: 4`, `AD: 4` červených ve SVÉ skupině, **jiné skupiny: —**; `A: /tick odpoví 200` vždy zelená; zdroj conductora na konci **čistý (disk == HEAD)** |
| **A3** | **Tvrdí testy TVAR i OBSAH?** — kopie testu s **PRÁZDNOU falešnou D1** (P28 poškozovala text dotazu) | čítač **(205, 55)** při prázdné D1: u **každé** ze sedmi skupin zčervenaly obsahové kontroly a **TVAROVÁ zůstala zelená** (`/health`: „jde BEZ tajemství", „hlásí `ok: true`"; ostatní: „odpoví 200") |
| **A4** | **Sedí čísla v §59?** — každý tvrzený čítač **znovu spuštěn**, čísla **čtena z dokumentu** (a u dvou i ze zadání), u každého tvrzení se **vypisuje okno, které vzor trefil** | **6 pojmenovaných ROZDÍLŮ** (60.2): `test-tick-offline` **205/0 → 215/0** (moje práce, +10 kontrol), `p28-obnov-kroniku --kontrola` čítač **nevypisuje** (jiná větev), živě `/health` `ready=2 → 5`, živě `/roadmap` `22/19/2/1/5 → 25/20/4/1/5`, běhy #240–#243 = **9, ne 4**, `RateLimitError` **6/9, ne 9/9** |
| **A5** | **Rozsah `ov-g` a kontinuita id** vlastním počítadlem | **99 řádků Hxx** (1 + 98) vlastním průchodem, brána hlásí totéž, mimo živé zdroje **139 v 7**; kronika **43 řádků, id 1..43 bez děr**; fixtura bez řádku 30 → `exit 1` a id **pojmenuje**; prázdná fixtura → **NEMĚŘENO** a `exit 1` |
| **A6** | **Oprava B5 měří, co tvrdí** — fixtury přes `FORGE_SKILLS` | cesta v ``` bloku se počítá **STEJNĚ** jako tatáž cesta inline (fixtura 49+1 = 50 v obou); **mrtvá** cesta v bloku bránu **shodí**; starý tvar se nezhoršil; **deklarovaná výjimka NEPROSÁKNE** do jiného skillu (`tools\vision.py` v cizím skillu → `exit 1`) |
| **A7** | **Inventář → `g3` → `validate-all`** v tomto pořadí, nic mezi tím | `g3` **49 bran**, **1 NEDEKLAROVANÝ** exit (`validate-all (CELEK)`) a každý **pojmenovaný**; `validate-all` **2 problémy** (oba o stavu HRY/D1); inventář **čerstvý** — a to **dvěma nezávislými přepočty**: (a) uložený `sha256` = přepočet z uložených záznamů, (b) `--otisk` z dnešních bajtů = uložený |
| **B6** | **OSIŘELÉ GRANULE SE UKLÍZEJÍ SAMY + tik ŘEKNE, PROČ NIC NESPUSTIL** (dvě opravy v `conductor/src/index.ts`) | `_analyza/p29-b6-patch.py` (7 záměn, každá ověřená: kotva právě 1×); `tsc` **exit 0**; `tools/test-tick-offline.mjs` **205/0 → 215/0** (10 nových kontrol `AE*`); mutační důkaz `_analyza/p29-b6-mutace.py` → **15/0** (tři vraty, každá dvě nohy, soubor vrácen **bajt na bajt**) |
| **C** | Doklady a sondy: `p29-a-overeni.py`, `p29-b6-mutace.py`, `p29-b6-patch.py`, `p29-sonda-ulohy.mjs`, `p29-sonda-tik.mjs`, `p29-sonda-ntfy.mjs`, `p29-sluzba-rows.mjs`, `p29-docx-vytah.py`; **všechny doklady zapsané BAJTY (UTF-8)**, ne přesměrováním v PowerShellu | registrace v `_analyza/p20-d-doklady.py`: `p29-a-overeni.py` i `p29-b6-mutace.py` bere `VZOR` sám (ověřeno), `p29-b6-patch.py` a `p29-docx-vytah.py` jsou v `PRESKIP` (patcher se v dávce spouštět nesmí) |
| **D** | **Posouzení konceptu „Gemini architektonika"** (docx od uživatele) proti současnému designu orchestry | `_analyza/p29-gemini-architektonika.txt` (převod vstupu) + rozhodnutí v **KRONIKA §2.22** a v `PLAN-DALSI-KROK.md` — **architekturu NEPŘEDĚLÁVAT**, převzít 4 věci (60.4) |

### 60.2 Nálezy P29 (každý doložený měřením; plné znění v kronice §2.22)

1. **DOKLAD, KTERÝ §59.1 UVÁDÍ, NENÍ DOKLADEM PLNÉHO BĚHU.** `p28-a-overeni-vystup.txt`
   obsahoval **jen dílčí běh A5** (11 kontrol), ne tvrzených 122/14 — P28 si ho
   přepsala vlastním dílčím během (přesně ta vada, kterou sama pojmenovala u P27).
   Zachován jako `_analyza/p29-p28a-doklad-jaky-byl.txt` (sha256 v kronice).
   **Číslo 122/14 je správné** — přeměřeno vlastním plným během (15,3 min).
2. **TŘI DOKLADY P28 JSOU V UTF-16LE** (`p28-b-mutace-vystup.txt`,
   `p28-baseline-p27a-vystup.txt`, `p28-p26b-dnes-vystup.txt`): vznikly
   přesměrováním v PowerShellu, `read` tool je odmítne jako binárku. V `_analyza`
   je takových `.txt` **48** (naměřeno). Nové doklady se zapisují bajty (UTF-8).
3. **TVRZENÍ §59.6 „poslední 4 běhy (#240–#243) a VŠECHNY na `RateLimitError`"
   NEPLATÍ.** Sonda `p29-sonda-ulohy.mjs` páruje běhy podle **ID ÚLOHY v názvu**
   (ne podle pořadí) a v posledních 60 bězích našla **9 běhů** těchto úloh:
   **všechny `failure`**, ale `litellm.RateLimitError` jen v **6 z 9**; mezi
   selhavšími kroky jsou **„Kontrola parsování (rychlá brána)"**, **„Testy hry
   (Godot headless)"** a **„Agent nic nezměnil"**. Navíc: **`#240–#243` jsou ID
   ÚLOH, kdežto `#341` je `run_number`** — dva čítače téhož jména (past projektu).
4. **⚠ ŽIVÁ SLUŽBA NEDISPATCHUJE A NEŘEKNE PROČ** (nález **P29-D**): ruční
   `POST /tick` (9. 10. 2026, 23:02:16 UTC) → **`spusteno: 0 úloh`**, přitom
   `/health` `ready=5 running=0`; poslední běh v `/status` je z **21:12:57 UTC**.
   **Cooldown (3 h) vysvětluje 4 z 5** úloh (#240–#243 selhaly 21:02–21:23),
   ale **NE #239**: ta selhala 11:40:55 (cooldown vypršel 14:40:55), má
   `attempts=2 < 8` a nic neběží. Dvě **pojmenované** možné příčiny v kódu:
   (a) **strop granule** (`GRAIN_MAX_RUNS=8`, počítadlo se nikdy neresetuje
   a `/roadmap` ho nevydává), (b) **zámek souboru** od úlohy, která zůstala
   v `tasks.status='running'` (a `/queue` je `LIMIT 50`, takže ji nevidí).
   **Obě jsou TICHÉ** — a proto je oprava B6 pojmenovává (60.1).
   **Další měření, které to rozhodne:** přečíst D1 (`wrangler d1 execute --remote`)
   nebo nasadit opravu a přečíst novou odpověď tiku.
5. **BRÁNA „cron běží (čas)" NEMŮŽE SELHAT:** `tools/validate-all.mjs` testuje
   jen `!!h.time` — tedy že `/health` odpovídá. O tom, jestli tik opravdu běží,
   netvrdí **nic** (a přitom je to právě ten stav, který se 9. 10. zastavil).
6. **OSIŘELÉ ŘÁDKY POTVRZENY ŽIVĚ** (`POST /tasks/cleanup?dry_run`): 21 granulí
   v souborech, **25 řádků v cache, 5 osiřelých, 5 osiřelých úkolů**, 0 úloh bez
   vazby. Z toho `entity.enemy` = úloha **#239 `ready`**.
7. **V SOUBORU JE GRANULE, KTEROU CACHE NEMÁ:** `entity.move.smooth` (opačný
   rozpor, než popisuje P28) — **nevyřešeno**, patří do P30 (čeká na závislosti,
   nebo se ztratila?).
8. **CIZÍ PRÁCE VE HŘE MÁ VLASTNÍ PŘÍČINU SELHÁNÍ** (měřeno sondou + nezávislou
   analýzou): živý `agent.yml` je **ve HŘE** (`uo-shadows/.github/workflows/`),
   a jeho `:197` zakládá **PRÁZDNÝ soubor** granule (`: > "$f"`), který kontrola
   „změnil agent něco?" (`:236–243`, `:464`) **počítá jako práci** → rate-limitovaný
   běh se hlásí jako **success** a spadne až na jobu „Otevři pull request"
   (chybějící credential, `exit 128`; **6 z posledních 24 běhů**). Větev, která má
   kvůli kvótě přejít na dalšího poskytovatele (`:253`), fallback **ZAKAZUJE**.
   → **do orchestra to nepatří** (orchestra do hry nepíše); nabídka B7 pro session,
   která hru vede.
9. **POLE, KTERÉ NIKDO NEČTE, NENÍ KONTRAKT:** `acceptance` je ve všech 21
   granulích, ale `dispatchWorkflow` je **neposílá** (posílá `task_id`, `run_key`,
   `kind`, `title`, `prompt`, `max_lines`, `model`, `grain`, `attempt`).
   „Je to v souboru" ≠ „má to účinek" — patří do procesu design dokumentů (B8).
10. **VLASTNÍ OMYLY P29 (4, všechny o měření):** (a) `oslab_check` nahrazoval
    jen PRVNÍ řádek víceřádkové kontroly → oslabená kopie spadla na `SyntaxError`
    a její prázdný výstup vypadal jako „kontrola zmizela"; (b) `_leg` pouštěl
    **živé** měřidlo místo oslabené kopie → třetí noha byla prázdná; (c) kotva
    `99 řádků Hxx` je v dokumentu **5×** (v §57 2×) → mutace musí být vázaná na
    **měřený oddíl** a na **první** výskyt; (d) `kronika-kontrola.py` bere cestu
    **POZICIONÁLNĚ** — `--kronika <cesta>` skončí `CHYBA: --kronika neexistuje`
    a `exit 1`, což vypadá jako nalezená vada (první verze mého A5 na tom měla
    falešně zelenou kontrolu).

### 60.3 Živý stav při zápisu (9. 10. 2026, ~07:4x +02:00)

```
orchestra: HEAD ef04912 · origin/main ef04912 · nepushnutých 0 (P28 pushnuta)
           + práce P29 (necommitnutá): conductor/src/index.ts, tools/test-tick-offline.mjs,
             HANDOFF.md, KRONIKA-PROJEKTU.md, PLAN-DALSI-KROK.md, NEXT-SESSION-INSTRUKCE.md,
             _analyza/p29-* (doklady, sondy, patcher, mutační důkaz)
hra:       HEAD 01a9649 (při MĚŘENÍ); vede ji CIZÍ session, která ji posunula 5×
           (bc51e46 → … → 01a9649); P29 do ní nezapsala ani bajt
živá služba: /health ok=true ready=5 running=0 games=1 · /roadmap 25 řádků
           (done 20, queued 4, blocked 1; max pokusů 5) · /queue 50 úloh
           (ready 5, failed 1, blocked 44) · 6 chráněných endpointů bez tajemství 401,
           s tajemstvím 200 · POSLEDNÍ BĚH 21:12:57 UTC (dispatch stojí)
brány:     g3 → 49 bran, 1 NEDEKLAROVANÝ exit (`validate-all (CELEK)`) ·
           validate-all → 2 problémy (oba o stavu HRY/D1) ·
           test-tick-offline → 215/0 (bylo 205/0) · tick-mutace → 20 vrat, 41/0 ·
           over-skilly → 90 zmínek, 0 mrtvých · kronika SEDÍ · ov-g → 99 řádků Hxx
```

### 60.4 Co čeká na tebe (uživatel)

- **PUSH je ROZHODNUTÍ UŽIVATELE** — a u `conductor/**` navíc **nasadí živou
  službu** (`npx wrangler deploy` z `conductor/`). **Bez nasazení oprava B6
  neúčinkuje**: živá služba běží starý kód (dispatch stojí, nález P29-D).
  Před pushnutím: `git status` + `git diff --stat` (vyžádáno pravidly).
- **Koncept od Gemini (docx) — rozhodnutí o publikaci:** převod vstupu leží
  v `_analyza/_archiv/p29-gemini-architektonika.txt` (přesunu do archivu se
  dočkej při úklidu). **Repo je veřejné** → publikovat cizí dialog s AI je
  **tvoje** rozhodnutí, ne moje. Věcné závěry jsou v KRONICE §2.22 (bez citací).
- **Okamžitá záplata bez nasazení** (kdybys chtěl uklidit hned): `POST /tasks/cleanup`
  s tajemstvím smaže 5 osiřelých řádků a zablokuje jejich úlohy. Nedělal jsem to
  sám — je to **zásah do živého stavu** (a chtěl jsem ti nechat i doklad vady).
- **B3 (acceptance `B4` na živé službě) pořád čeká na „ano"** — dočasně zastaví orchestra.
- **Strop granule je tichý** — dokud se nenasadí B6, nedozvíš se, která granule
  a proč se přestala vydávat.

### 60.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
# 1) vlastní měřidlo P29 (A2–A7) a jeho doklady
python _analyza\p29-a-overeni.py                 # A2,A3,A5,A6,A7,A4 (~10 min)
python _analyza\p29-a-overeni.py --jen A1M13     # dvě levné kontramutace P28 (7/0)
python _analyza\p29-b6-mutace.py                 # mutační důkaz opravy B6 (15/0)
# 2) oprava B6 a její testy
node tools\test-tick-offline.mjs                 # 215/0 (bylo 205/0)
node conductor\node_modules\typescript\bin\tsc --noEmit -p conductor
# 3) záznamy a brány PO SOBĚ (ne současně; inventář jako poslední)
python _analyza\kronika-kontrola.py              # SEDÍ + "chybějící id: (žádné)"
python _analyza\handoff-kontrola-uplnost.py      # úplnost handoffu
python _analyza\ov-g-neovereno.py                # 0 NEOVĚŘENO, rozsah 99 řádků Hxx
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\g3-brany.py                      # 49 bran
node tools\validate-all.mjs                      # 2 problémy = stav HRY
```
"""

# ═══════════════════════════════════════════════════════════ KRONIKA ═══
RADEK_44 = (
    "| **44** | **9. 10. 2026** (00:2x–07:3x +02:00) | **ověřovací (Úkol A) + "
    "akční (Úkol B6) + rozhodovací (koncept od Gemini)** | "
    "**Přeměřit práci P28 VLASTNÍM měřidlem, opravit tiše stojící frontu a posoudit "
    "koncept orchestra od Gemini.** Zadání P29 §2.1 chtělo měřidlo, které umí spadnout; "
    "vzniklo `_analyza/p29-a-overeni.py` (A1–A7) s **třemi vlastními kontramutacemi "
    "měřidla P28** (M1 §57 `99 řádků Hxx`→`98`, M2 g3 s 50. branou, M3 ov-g s nulovým "
    "rozsahem), každá se **třemi nohami** — a ukázalo se, že **dvě z nich první verze "
    "měřidla měřila falešně** (`_leg` pouštěl živé měřidlo místo oslabené kopie; "
    "`oslab_check` nahrazoval jen první řádek víceřádkové kontroly → oslabená kopie "
    "spadla na `SyntaxError` a její prázdný výstup vypadal jako „kontrola zmizela“). "
    "**A1**: `p28-b-mutace.py` **27/0** a `p28-a-overeni.py --plne` **122/14** "
    "(15,3 min) — obě tvrzení §59.1 **reprodukována**, ale **doklad, který §59.1 "
    "uvádí, byl jen dílčí běh A5** (11 kontrol) → zachován jako "
    "`p29-p28a-doklad-jaky-byl.txt`. **A2** zarážkou v handleru **+ IZOLACÍ** (jiná "
    "skupina nesmí zčervenat): 7 endpointů, 12/5/4/8/4/4/4 červených ve své skupině, "
    "jiné skupiny 0. **A3** kopií testu s prázdnou falešnou D1: 55 červených, ale u "
    "každé skupiny zůstala **TVAROVÁ** kontrola zelená (`/health` „jde BEZ tajemství“, "
    "ostatní „odpoví 200“). **A5** vlastním počítadlem: **99 řádků Hxx**, mimo živé "
    "zdroje **139 v 7**, kronika **43 řádků / id 1..43 bez děr**, fixtura bez řádku 30 "
    "→ `exit 1` a id pojmenuje (a `--kronika` je **past**: cesta se bere POZICIONÁLNĚ, "
    "jinak `CHYBA: --kronika neexistuje` + `exit 1` = falešně zelená kontrola). "
    "**A6** fixturami: cesta v ``` bloku se počítá stejně jako inline (49+1=50 v obou), "
    "mrtvá cesta v bloku bránu shodí a **deklarovaná výjimka neprosákne** do jiného "
    "skillu. **A7** inventář → g3 → validate-all v pořadí: **49 bran**, 1 pojmenovaný "
    "nedeklarovaný exit, **2 problémy validate-all** (oba o hře), otisk ověřen **dvěma "
    "nezávislými přepočty**. **A4** našel **6 pojmenovaných rozdílů** — mj. že tvrzení "
    "§59.6 („poslední 4 běhy #240–#243 a VŠECHNY na RateLimitError“) **neplatí**: "
    "sonda páruje běhy podle ID ÚLOHY a našla **9 běhů, 9× failure, ale jen 6× "
    "RateLimitError**; mezi selhavšími kroky je „Kontrola parsování“, „Testy hry“ "
    "i „Agent nic nezměnil“ — a `#341` je `run_number`, kdežto `#240` je ID úlohy. "
    "**ŽIVÝ NÁLEZ, KTERÝ ZADÁNÍ NEČEKALO:** ruční `POST /tick` vrátil "
    "**`spusteno: 0 úloh`** při `ready=5 running=0`, poslední běh **21:12:57 UTC** — "
    "cooldown vysvětluje 4 úlohy, ale **ne #239** (selhala 11:40:55, strop granule "
    "8 pokusů, nic neběží) → dispatch **tiše zahazuje práci a neřekne proč**. "
    "Oprava **B6** proto dělá dvě věci: (1) `roadmapTick` **sám uklízí osiřelé řádky "
    "cache** (měřeno živě: 21 granulí v souborech, 25 řádků v cache, **5 osiřelých**, "
    "z toho `entity.enemy` s úlohou **#239 `ready`**) — úklid existoval jen ruční "
    "a nikdo ho nevolal; (2) tik **pojmenuje, co přeskočil** (`STROP GRANULE 9/8`, "
    "`v cooldownu #240, #241`, `ZÁMEK …`). Deset nových kontrol `AE*` v "
    "`tools/test-tick-offline.mjs` (**205/0 → 215/0**) má **mutační důkaz 15/0** "
    "(tři vraty, každá dvě nohy, soubor vrácen bajt na bajt). **Koncept od Gemini**: "
    "posouzen jako **mapa, ne plán** — architektura orchestra (role architekt/mozek/"
    "dělníci/sklady) je **tatáž**, jen ji má orchestra levněji a ověřeně (Cloudflare "
    "Worker + D1 + GitHub Actions místo Oracle + R2 + PM2); jeho **tři věcné body** "
    "(řetěz poskytovatelů při kvótě, circuit breaker, „nespravuj kód, zakládej tikety“) "
    "jsou **už dnes na seznamu prací** a jeho **pět vrstev pro sandbox** patří do "
    "procesu design dokumentů (B8). Do hry orchestra nezasahuje: živý `agent.yml` je "
    "**ve hře** a jeho `:197` (prázdný soubor jako „práce agenta“) dělá z rate-limitu "
    "**success** a z běhu pád na chybějícím credentialu (**6 z 24 běhů**) |"
)

NALEZY_222 = r"""
### 2.22 Nálezy z P29 (9. 10. 2026) — tichý dispatch, dílčí doklad a koncept jako mapa

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P30.

| # | Nález | Doklad |
|---|---|---|
| **H{P1}** | **DOKLAD UVEDENÝ V §59.1 NENÍ DOKLADEM PLNÉHO BĚHU.** `p28-a-overeni-vystup.txt` obsahoval jen dílčí běh A5 (11 kontrol), ne tvrzených 122/14 — P28 si ho přepsala vlastním dílčím během (tatáž vada, kterou sama pojmenovala u P27). | zachováno `_analyza/p29-p28a-doklad-jaky-byl.txt`; tvrzení **122/14 přeměřeno** vlastním plným během (15,3 min) |
| **H{P2}** | **TŘI DOKLADY P28 JSOU UTF-16LE** (PowerShell redirect) — `read` tool je odmítne jako binárku. V `_analyza` je takových `.txt` **48**. | `p28-b-mutace-vystup.txt` (první bajty `FF FE`), `p28-baseline-p27a-vystup.txt`, `p28-p26b-dnes-vystup.txt`; nové doklady zapsané **bajty (UTF-8)** |
| **H{P3}** | **TVRZENÍ §59.6 O PŘÍČINĚ SELHÁNÍ NEPLATÍ.** Sonda páruje běhy podle **ID ÚLOHY v názvu**: 9 běhů úloh #240–#243 za 60 běhů, **9× failure**, ale `litellm.RateLimitError` jen **6/9**; selhavší kroky jsou i „Kontrola parsování“ a „Testy hry (Godot headless)“. Navíc **`#240` je ID úlohy, `#341` je `run_number`** — dva čítače téhož jména. | `_analyza/p29-sonda-ulohy.mjs` → `p29-a4-behy-uloh-vystup.txt`; čítače v `p29-a1m-vystup.txt` (A4) |
| **H{P4}** | **⚠ ŽIVÁ SLUŽBA NEDISPATCHUJE A NEŘEKNE PROČ.** `POST /tick` → `spusteno: 0 úloh` při `ready=5 running=0`; poslední běh 21:12:57 UTC. Cooldown (3 h) vysvětluje #240–#243, **ne #239** (cooldown vypršel 14:40:55, `attempts=2`, nic neběží). Kandidáti: **strop granule** (`GRAIN_MAX_RUNS=8`, počítadlo bez resetu) nebo **zámek** od úlohy visící v `tasks.status='running'` — oba **tiché**. | `_analyza/p29-sonda-tik.mjs --tik`; `/health`, `/queue`, `/status`; kód `index.ts` (dispatch smyčka) — **rozhodne až čtení D1 nebo nasazená oprava** |
| **H{P5}** | **BRÁNA „cron běží (čas)“ NEMŮŽE SELHAT** — testuje jen `!!h.time`, tedy že `/health` odpovídá; o běhu tiku netvrdí nic (a přesně ten se 9. 10. zastavil). | `tools/validate-all.mjs` (test na `/health`) vs. měřený stav (H{P4}) |
| **H{P6}** | **OSIŘELÉ ŘÁDKY CACHE POTVRZENY ŽIVĚ**: 21 granulí v souborech, **25 řádků v cache, 5 osiřelých, 5 osiřelých úkolů**; `entity.enemy` = úloha **#239 `ready`**. Úklid existoval jen jako ruční endpoint. | `POST /tasks/cleanup {dry_run:true}` → `_analyza/p29-sonda-tik.mjs`; opraveno **B6** (mutační důkaz 15/0) |
| **H{P7}** | **V SOUBORU JE GRANULE, KTEROU CACHE NEMÁ**: `entity.move.smooth` (opačný rozpor, než popisuje P28). **Otevřeno** — patří do P30. | vlastní výpočet v A4 (`p29-a1m-vystup.txt`) |
| **H{P8}** | **ŽIVÝ `agent.yml` JE VE HŘE A MÁ VLASTNÍ PŘÍČINU SELHÁNÍ**: `:197` zakládá prázdný soubor granule a kontrola „změnil agent něco?“ ho počítá jako práci → rate-limitovaný běh hlásí **success** a spadne až na jobu „Otevři pull request“ (chybí credential, `exit 128`; **6 z 24 běhů**). Větev pro kvótu (`:253`) fallback **zakazuje**. | sonda `p29-sonda-agenta.mjs` + nezávislá analýza logů (GitHub API) — **mimo dosah orchestra** (do hry se nezasahuje) |
| **H{P9}** | **POLE, KTERÉ NIKDO NEČTE, NENÍ KONTRAKT**: `acceptance` je ve všech 21 granulích, ale `dispatchWorkflow` je neposílá (posílá 9 jiných polí). | čtení `conductor/src/index.ts` (dispatchWorkflow) + kontrakt roadmapy (A4) |
| **H{P10}** | **KONCEPT OD GEMINI JE MAPA, NE PLÁN.** Role (architekt/mozek/dělníci/sklady) jsou **tatáž architektura**, kterou orchestra má; technologicky ji má **levněji a ověřeně** (Worker + D1 + Actions vs. Oracle + R2 + PM2). Jeho tři věcné body jsou už na seznamu prací; jeho **pět vrstev pro sandbox** (micro/macro LOD, kombinatorické itemy, auto-balanc simulací, knihovna UI komponent, centrální stav od 1. dne) patří do **procesu design dokumentů**. | `_analyza/p29-gemini-architektonika.txt` + rozhodnutí v `PLAN-DALSI-KROK.md` |
| **H{P11}** | **VLASTNÍ OMYLY P29 (4, všechny o měření)**: (a) `oslab_check` nahrazoval jen první řádek víceřádkové kontroly → oslabená kopie spadla na `SyntaxError` a prázdný výstup vypadal jako „kontrola zmizela“; (b) `_leg` pouštěl **živé** měřidlo místo oslabené kopie; (c) kotva `99 řádků Hxx` je v dokumentu **5×** (v §57 2×) → mutace patří do **měřeného oddílu** a na **první** výskyt; (d) `kronika-kontrola.py` bere cestu **POZICIONÁLNĚ** → `--kronika <cesta>` vypadá jako nalezená vada. | `p29-a1m13-vystup.txt` (7/0), `p29-a-overeni.py` (komentáře u `oslab_check`/`_leg`/`_m1_handoff`) |
"""

PLAN_DODATEK = r"""
---

## P29 (9. 10. 2026) — ROZHODNUTÍ O KONCEPTU A CO DÁL

> **Datum spotřeby:** 9. 10. 2026, ~07:4x +02:00. Platí pro stav po P29;
> kdo to čte později, **přeměří** (`python _analyza\p29-a-overeni.py`).

**Vstup:** koncept „Orchestrace vývoje hry pomocí AI" (docx od uživatele,
převod `_analyza/p29-gemini-architektonika.txt`) + měření P29.

**Rozhodnutí (ne návrh):** **architekturu orchestra NEPŘEDĚLÁVAT.** Koncept
popisuje **tutéž** architekturu (architekt → mozek → dělníci → sklady; kvalitní
model plánuje, free modely vykonávají, stav drží databáze, brány rozhodují),
jen ji navrhuje na **dražší a křehčí** infrastruktuře (Oracle + R2 + PM2 +
Python). Orchestra ji má **levněji a ověřeně** (Cloudflare Worker + D1 + cron +
GitHub Actions + 49 bran) — měnit ji kvůli konceptu by bylo **zhoršení**.

**Co z konceptu PŘEVZÍT (v tomto pořadí):**

1. **Čestné hlášení selhání** — „tik nic nespustil" musí být **vysvětlené**.
   → **APLIKOVÁNO v P29 (B6)**: pojmenované přeskočení (strop granule, zámek,
   cooldown) + automatický úklid osiřelých řádků. Bez nasazení neúčinkuje.
2. **Řetěz poskytovatelů při `RateLimitError`** (koncept: Tier 1→2→3, vypínač
   placeného API, hibernace). **ODLOŽENO na P30** — měřeno: živý `agent.yml`
   je **ve hře** a jeho větev pro kvótu fallback **zakazuje**; orchestra do hry
   nepíše (nabídka **B7**).
3. **Proces design dokumentů** = „super-prompt pro architekta" + sokratovský
   dialog (koncept: Ideation Bot → GCD → schválení → architekt).
   **ODLOŽENO na P30** (nabídka **B8**): ověřit `JAK-PSAT-…` §9 a přenést do
   skillu `game-developer`; §9.3 (výměna roadmapy) je **nedostatečná** —
   pořadí je vypnout hru → push → `/tasks/cleanup` → sonda a `/roadmap/reset`
   **NENÍ** totéž co cleanup.
4. **Pět vrstev pro sandbox** (micro/macro LOD, kombinatorické itemy,
   automatický balanc simulací, knihovna UI komponent, centrální stav od 1. dne)
   → **patří do design dokumentů** nové hry, ne do orchestry. **ODLOŽENO**.
5. **`task_type` modularita** (code / lore / asset / review jako tentýž řetěz)
   → **ODLOŽENO** — měřeno: orchestra dnes **neumí ani číst `acceptance`**
   (H{P9}), takže další vrstvy by jen přidaly pole, která nikdo nečte.

**Co z konceptu ZAMÍTnout (a proč):**
- **Oracle Cloud + R2 + PM2 + Python orchestrátor** → nahrazuje funkční
  a ověřený stack dražší a křehčí variantou (server k údržbě, druhý stavový
  sklad, vlastní CI mimo GitHub).
- **RAG / vektorová paměť, dashboard, audio automatizace** → hra má dnes
  `scripts/game.gd` ~12,5 kB a 21 granulí; RAG by řešil problém, který nemáme,
  a dashboard je nahrazen `g3` + `/health` + notifikacemi.
- **Milníkové revize generující tikety** → orchestra **už** staví na branách
  a PR recenzi; přidávat k tomu druhou roli „revizor" znamená dvě místa, která
  rozhodují o tomtéž (a koncept sám říká, že AI nemá přepisovat hotový kód).

**Nejbližší práce (P30):** (1) nasadit B6 (push + `wrangler deploy`) a přečíst
novou odpověď tiku → rozhodne H{P4}; (2) `entity.move.smooth` (H{P7});
(3) B8 — návod pro architekta; (4) B7 — jen jako nabídka pro session, která
vede hru.
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

    check("HANDOFF §60 ještě NENÍ (skript je idempotentní)", "## 60. P29" in h, False)
    check("KRONIKA řádek 44 ještě NENÍ", bool(re.search(r"^\|\s*\*\*44\*\*\s*\|", k, re.M)), False)
    check("KRONIKA má řádek 43 (kotva pro vložení)",
          bool(re.search(r"^\|\s*\*\*43\*\*\s*\|", k, re.M)), True)
    check("KRONIKA má oddíl §2.21 (kotva pro §2.22)", "### 2.21" in k, True)
    check("PLAN existuje a je neprázdný (dodatek se přidává na konec)",
          bool(p.strip()), True)
    check("PLAN dodatek P29 ještě NENÍ (idempotence)",
          "ROZHODNUTÍ O KONCEPTU A CO DÁL" in p, False)
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v kotvách)" % chyb)
        return 1

    # nálezy: čísla H se dopočítají, ať se nic neduplikuje
    h0 = hledej_max_h(k)
    print("  nejvyšší existující nález v kronice: H%d → nové začnou H%d" % (h0, h0 + 1))
    nalezy = (NALEZY_222
              .replace("{P1}", str(h0 + 1)).replace("{P2}", str(h0 + 2))
              .replace("{P3}", str(h0 + 3)).replace("{P4}", str(h0 + 4))
              .replace("{P5}", str(h0 + 5)).replace("{P6}", str(h0 + 6))
              .replace("{P7}", str(h0 + 7)).replace("{P8}", str(h0 + 8))
              .replace("{P9}", str(h0 + 9)).replace("{P10}", str(h0 + 10))
              .replace("{P11}", str(h0 + 11)))
    plan = PLAN_DODATEK.replace("{P9}", str(h0 + 9)).replace("{P4}", str(h0 + 4))

    # (1) KRONIKA: řádek 44 hned za řádek 43; §2.22 před "## 3."
    radky = k.splitlines()
    i43 = next(i for i, l in enumerate(radky) if re.match(r"^\|\s*\*\*43\*\*\s*\|", l))
    i3 = next(i for i, l in enumerate(radky) if l.startswith("## 3."))
    check("řádek 43 je PŘED oddílem §3 (jinak by vložení rozbilo tabulku)", i43 < i3, True)
    novy_k = (radky[:i43 + 1] + [RADEK_44] + radky[i43 + 1:i3] + [nalezy.strip(), ""]
              + radky[i3:])
    k_new = "\n".join(novy_k) + "\n"

    # (2) HANDOFF: §60 na konec
    h_new = h.rstrip("\n") + "\n" + HANDOFF_60.strip("\n") + "\n"

    # (3) PLÁN: dodatek na konec
    p_new = (p.rstrip("\n") + "\n" + plan.strip("\n") + "\n") if p else ""

    # ── ověření PŘED zápisem ──────────────────────────────────────────────
    check("HANDOFF: přibyl právě oddíl §60 (počet znaků roste)",
          len(h_new) > len(h), True)
    check("HANDOFF: řádků neubylo", len(h_new.splitlines()) > len(h.splitlines()), True)
    check("KRONIKA: přibyl řádek 44", bool(re.search(r"^\|\s*\*\*44\*\*\s*\|", k_new, re.M)), True)
    check("KRONIKA: id 1..44 bez děr",
          [n for n in range(1, 45)
           if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k_new, re.M)], [])
    check("KRONIKA: nálezy H%d..H%d jsou v textu" % (h0 + 1, h0 + 11),
          all(("**H%d**" % (h0 + i)) in k_new for i in range(1, 12)), True)
    check("KRONIKA: nic neubylo (řádků přibylo)",
          len(k_new.splitlines()) > len(k.splitlines()), True)
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
    print("  zapsáno: HANDOFF.md §60, KRONIKA řádek 44 + §2.22, PLAN dodatek P29")
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

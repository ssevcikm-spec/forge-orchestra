# -*- coding: utf-8 -*-
r"""P36 — ZÁPIS ZÁZNAMŮ (HANDOFF §67, KRONIKA řádek 51 + §2.29).

PROČ SKRIPTEM (`AGENTS.md`): „Řádek kroniky má 5 svislítek (ne 8 jako záhlaví);
piš řádky **skriptem** — vzor `p35-zapis-zaznamu.py`, je **idempotentní**.“
Ruční zápis rozbil čítače už dvakrát (kronika je append-only záznam).

CO SE ZAPISUJE:
  * `HANDOFF.md` — nový oddíl **§67** (jen se PŘIDÁVÁ na konec; nic se nemaže),
  * `KRONIKA-PROJEKTU.md` — **řádek 51** přehledové tabulky (vkládá se za 50;
    `RADEK_51.count("|") == 5`, což se ověřuje) a **§2.29** Nálezy z P36
    (vkládá se před `## 3. Počty omylů`, tedy PŘED tabulku omylů).

Použití: python _analyza\p36-zapis-zaznamu.py [--jen HANDOFF|KRONIKA]
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = __import__("pathlib").Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"

kontrol = 0
chyb = []


def zk(ok, popis):
    global kontrol
    kontrol += 1
    print("  %s %s" % ("OK   " if ok else "CHYBA", popis))
    if not ok:
        chyb.append(popis)


def spust(cmd, timeout=900):
    r = subprocess.run([str(a) for a in cmd], cwd=str(WS),
                       env={**os.environ, "PYTHONIOENCODING": "utf-8"},
                       capture_output=True, timeout=timeout)
    return r.returncode, ((r.stdout or b"") + (r.stderr or b"")).decode("utf-8", "replace")


SEKCE_67 = r"""
## 67. P36 — PŘEMĚŘENÍ P35 A PŘÍČINA, PROČ SE NEVYDÁVÁ PRÁCE (H170–H174) (11. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P36 + stav po P36**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**51**, nálezy **§2.29**), plán (`PLAN-DALSI-KROK.md`). Zadání P36 je v
`NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **11. 10. 2026 12:0x–13:0x UTC** (živý čas z hodin).
> Tvrzení o **stavu** (HEAD, hra, živá služba, běhy na GitHubu) platí k tomu
> okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.29), aby každý nález byl dohledatelný
> z HANDOFF.md — ZÁMĚRNĚ JAKO PRÓZA, ne tabulkou** (tabulkový řádek `| **Hxx** |`
> by zvedl počítadlo „řádků Hxx“ a shodil `ov-g` i měřidla P28):
> **H170** = **VLASTNÍ MĚŘIDLO P36 PŘEMĚŘILO P35** a rozdíl je pojmenovaný:
> doklad P35 má **74/0**, dnes **73/0** (jediná chybějící kontrola je noha A5
> „Cloudflare Analytics“, která ve 12:33Z vrátila **HTTP 401** a v 12:40Z
> **HTTP 200** týmž nástrojem a týmž configem → NEZMĚŘENO) — **a ZADÁNÍ P36
> tvrdí 71/0**, což je číslo DŘÍVĚJŠÍHO běhu, ne dnešní stav · **H171** =
> **ORCHESTRA NEVYDÁVÁ PRÁCI ŠEST DNÍ A STROP GRANULE TO JEN ZAMASKOVAL**:
> poslední ÚSPĚŠNÝ běh agenta je **#297 z 5. 10. 02:01Z**; z posledních 100 běhů
> je **95 `failure`** a čtyři měřené příčiny (49× parse brána, 15× „agent nic
> nezměnil“ = TPM 8000, 15× push PR bez pověření, 15× testy hry) leží **MIMO**
> strop · **H172** = **`fakeDb` NEZNAL TABULKU `state`** → harness tvrdil 218/0,
> a přitom se **zápis tepu vůbec neprovedl** a `/health` čítal svou `catch` větev;
> zavřeno (model `state` + scénář **AG**, **218/0 → 231/0**) · **H173** =
> **VLASTNÍ OMYL P36: `--vystup` NENÍ TRANZITIVNÍ** — `p35-a-overeni.py --plne`
> s přesměrovaným výstupem přesto přepsalo doklady svých vnitřních noh
> (`p35-d1-state-vystup.txt` 902 → 256 B, `p35-cf-analytika-vystup.txt`) ·
> **H174** = **ŠABLONA A HRA MAJÍ `agent.yml` ROZDÍLNÝ, A BĚŽÍ TA VERZE VE HŘE**
> (bloby `d48746b` vs `10b07ec`, 78 změněných řádků) — 95 % změřených selhání
> se děje v kódu ve hře, takže oprava šablony sama nic nezlepší.

### 67.1 Úkol A — P35 PŘEMĚŘENA VLASTNÍM MĚŘIDLEM (`p36-a-overeni.py`)

**VLASTNÍ MĚŘIDLO:** `_analyza/p36-a-overeni.py` (A0–A7) — **26 kontrol, 3 pojmenované
ROZDÍLY** (0 NEZMĚŘENO). **MUTAČNÍ DŮKAZ:** `_analyza/p36-mutace.py` → **45/0**
(sedm vrat, každé v KOPII přes seam; u každé se měří i to, že ZDRAVÝ stav projde).
Měřidlo čte **tvrzení z dokumentu** (`HANDOFF.md` §66 + `NEXT-SESSION-INSTRUKCE.md`)
a **nenalezené tvrzení je CHYBA** (H155).

| # | Co se měřilo | Naměřeno |
|---|---|---|
| **A0** | pojistky | `origin/main == HEAD` = **`b07c237`** (P35 pushnutá); strom čistý; 10 starých `*scratch/` adresářů (17–128 h) **není** náš leftover; hra `e4dccdb` (jen čteno) |
| **A1** | nasazení P35 **třemi kroky** | `deploy.yml` **#39 na `3143f31d6a37ed8d90bf06f5c03df9a407ae00ea`** → `completed/success` (2026-10-11T09:42:11Z); verze z **LOGU** `3985379c-4f45-424c-8400-2e26b54cae23` == `scriptVersion.id` **ŽIVÉHO** tailu (**72 eventů**) |
| **A2** | je oprava H165 v KÓDU a má test, který ji zavolá? | v KÓDU (bez komentářů) **NENÍ** `Uint8Array.from(atob(…), mapFn)` a **JE** indexovaný cyklus `charCodeAt(i)`; scénář **AF** s vícebajtovou češtinou existuje; `test-tick-offline.mjs` → **231/0** |
| **A3** | sedí čísla z §66? | `p35-a-overeni.py --plne` → **73/0** (3 ROZDÍLY, 1 NÁLEZ); **ROZDÍL**: §66 tvrdí **74/0**; **ROZDÍL**: zadání tvrdí **71/0** (zastaralé) — viz H170 |
| **A4** | je tik živě zlevněný? | živý tail: `cron` `cpuTime` **n=22**, medián **21,5 ms**, rozsah **18–25 ms**, **0×** `outcome != ok` — §66 tvrdí medián 20 ms (jiný vzorek) |
| **A5** | nová pole v `/health` a v D1 | `/health` posílá `last_cron_pokus` **i** `last_cron` (0–1 min); D1 `state` má oba klíče |
| **A6** | uklízí se měřidla po sobě? | `p35-mutace.py` → **33/0**; žádný soubor, který P35 měnila, není rozejitý (kontrola **BEZ filtru přípon**, H169) |
| **A7** | nic se nerozbilo | `g3` → **49 bran** (exit 1, 2 NEDEKLAROVANÉ exity — viz 67.4); `validate-all` **exit 1** PŘED regenerací inventáře (jediná příčina: zastaralý inventář — po regeneraci 0 problémů); `kronika SEDÍ`; `handoff` **všech 83 bodů**; `ov-g` **0 NEOVĚŘENO** |

**Co z P35 OBSTÁLO:** nasazení (tři kroky, křížová kontrola verze), oprava v kódu
i test, který ji volá, živé zlevnění tvaru tiku a úklid měřidel. **Co se
POSUNULO:** čítač měřidla (74 → 73) a číslo v zadání (71) — obojí pojmenované.

### 67.2 Úkol B — PROČ SE NEVYDÁVÁ PRÁCE: ŠEST DNÍ A ČTYŘI PŘÍČINY MIMO STROP

**Vybráno: STROP GRANULE** (doporučená stopa §2.2 zadání) — a odpověď je jiná,
než zadání čekalo: **strop není příčina, je následek.**

1. **STROP JE NAMĚŘENÝ A FUNGUJE.** D1 (11. 10.): tři úlohy `ready`
   — **#244** `engine.input`, **#245** `world.bodies`, **#246** `engine.shell`
   (každá `attempts=3`); řádky v `roadmap` vznikly **8. 10. 16:51**, `naposledy_selhalo`
   je **9. 10. 19:44–19:45**. Počítadlo **tímtéž SQL, jaké používá conductor**
   (`SQL_GRANULE_RUNS`): `world.bodies` **8**, `engine.shell` **8**,
   `engine.input` **8** — přesně na `GRAIN_MAX_RUNS = 8`.
2. **TĚCH 8 BĚHŮ JE ZNÁMÝCH:** 5 běhů úloh **#241/#242/#243** (8. 10. 16:52 →
   9. 10. 09:20) + 3 běhy **#244/#245/#246** (9. 10. 12:05 → 19:41).
3. **PŘÍČINA NENÍ V D1.** Všechny mají `summary = 'GitHub Actions: failure'`
   a **`log_tail` PRÁZDNÝ** — D1 o příčině neví nic. Je v bězích GitHub Actions
   **v repu hry** (`payload.repo = ssevcikm-spec/uo-shadows`).
4. **ZMĚŘENO Z GITHUB API (29 běhů úloh #240–#246, VŠECHNY `failure`):**
   * **14× job „Otevři pull request“** — job agenta **USPĚL** (práce vznikla!),
     ale `peter-evans/create-pull-request` spadl na
     `fatal: could not read Username for 'https://github.com'` (**exit 128**)
     při `git push --force-with-lease`; akce si přitom hlavičku
     `http.https://github.com/.extraheader AUTHORIZATION: basic ***` NASTAVILA,
     takže push byl odmítnut (401) → git se ptal na uživatele a v CI se nemá koho
     zeptat. **Práce ze 14 běhů byla ZAHOZENA.**
   * **8× „Agent nic nezměnil → hlásíme neúspěch“** — aider narazil na
     `litellm.RateLimitError: Request too large … service tier 'on_demand' on
     tokens per minute (TPM): Limit 8000, Requested …` → model nevrátil nic.
   * **6× „Kontrola parsování (rychlá brána)“** — vygenerovaný GDScript se neparsuje.
   * **1× „Testy hry (Godot headless)“**.
5. **CELÁ POSLEDNÍ STOVKA BĚHŮ** (2. 10. 11:13Z – 9. 10. 19:42Z):
   **95 `failure` / 5 `success`** — třídy: **49× parse brána**, 15× „nic nezměnil“,
   **15× push PR (auth)**, 15× testy hry, 1× auto-merge nechal PR k ruční kontrole.
6. **POSLEDNÍ ÚSPĚŠNÝ BĚH AGENTA JE `#297` z `2026-10-05T02:01:00Z`.**
   Od té doby orchestr **nevydal ani jednu granuli** — šest dní. Strop granulí
   9. 10. v 19:45 utnul poslední tři granule, ale **výpadek je o čtyři dny starší
   a širší než strop**.

**ZÁVĚR PRO ROZHODNUTÍ:** **zvednout strop bez opravy znamená spálit další běhy
na tytéž vady** (95% selhání). Strop je **brzda, která funguje** — a je to
jediné místo, kde je výpadek pojmenovaný (`přeskočeno: #244 … STROP GRANULE 8/8`).
Viditelnost tiku přitom funguje správně: `spusteno: 0 úloh` **není** tichá nula.

### 67.3 ZAVŘENÁ VADA — `fakeDb` NEZNAL TABULKU `state` (218/0 → 231/0)

**Zadání to pojmenovalo jako slepé místo a P36 ho zavřela** (H172):

* conductor zakládá a plní tabulku `state` (`zajistiTepTabulku`, `zapisPokus`,
  `zapisTep`) a `/health` ji čte (`SELECT k, v FROM state …`);
* `fakeDb` v `tools/test-tick-offline.mjs` ty dotazy **neznal** → `run()`/`all()`
  hodily „neznámý dotaz“ → conductor to **chytá** (`tep (manual) selhal: …`)
  a jede dál → **zápis tepu se neprovedl** a `/health` čítal svou `catch` větev
  (`last_cron: null` VŽDY);
* test tedy hlásil **218/0**, a přitom **každá kontrola o tepu měřila něco jiného,
  než si myslela**;
* **oprava:** `fakeDb` modeluje `state` a přibyl scénář **AG** (13 kontrol):
  ruční tik zapíše `last_tick` + `last_tick_zdroj=manual` a **NEOBNOVÍ `last_cron`**
  (H112 — bránu cronu nejde uspokojit tlačítkem); plánovaný tik zapíše
  **`cron_pokus` PŘED tikem** (H156) i `last_cron`; `/health` obojí **PŘEČTE z D1**;
* **stav: 218/0 → 231/0**;
* **mutační důkaz:** `p36-mutace.py` **M7** vrátí v KOPII testu slepost
  (`SELECT k, v FROM state` se nikdy netrefí) → test spadne a **5 kontrol AG**
  to pojmenuje.

### 67.4 Co zůstalo OTEVŘENÉ

* **PUSH PR BEZ POVĚŘENÍ (15 běhů)** — v `agent.yml` ve hře je
  `token: ${{ secrets.FORGE_PAT }}`; **validitu secretu z této stanice ZMĚŘIT
  NELZE** (GitHub vrací jen JMÉNA secretů: `FORGE_PAT` změněn 2026-09-29T12:12:15Z),
  takže zapsané je **měření selhání**, ne tvrzení o příčině. První auth selhání
  je z **7. 10.**, pak 8. 10. (5×) a 9. 10. (9×) — **do 7. 10. žádné nebylo**.
* **PARSE BRÁNA (49×)** — nejčastější příčina; oprava je v promptu/`agent.yml`
  **ve hře**, ne v orchestra.
* **TESTY HRY (15×)** a **TPM 8000 (8×)** — tamtéž.
* **ŠABLONA vs. HRA (`agent.yml`)** — H174; drift je deklarovaný, ale rozhoduje
  verze ve hře.
* **STROP GRANULE** — pojmenovaný a změřený (67.2); **rozhodnutí uživatele**.
* **H133** (`p28-a-overeni.py` A6 čeká `g3 → exit 0`), **dávka dokladů**
  (`p20-d-doklady.py` — P36 do ní přidala `p36-*` do `PRESKOCIT`), **GitHub
  throttle** (42 % CPU tiku) a **H168** (měřidla P34) — **nezměněno**.
* **H173 (vlastní omyl) — neopraveno ZÁMĚRNĚ:** oprava by znamenala měnit cizí
  měřidla P34/P35; místo toho je zapsané pravidlo (zálohovat celé `_analyza/`).
* **`g3` hlásí 2 NEDEKLAROVANÉ nenulové exity** (P35 měla 1 = `validate-all (CELEK)`
  měřený před rekordem). Jmenovitě se to neověřilo — po regeneraci inventáře
  a po commitu se `g3` pouští znovu a stav je v dokladu.

### 67.5 Živý stav při zápisu

```
orchestra: HEAD b07c237 (P35) · origin/main = HEAD (PUSHNUTO) · hra = e4dccdb
           (cizí session; do hry se NESAHALO — na remote je ale origin/main =
           01a9649, tedy DVA lokální commity hry NEJSOU pushnuté; je to stav
           cizí session, ne práce P36)
           ⚠ NASAZENÍ P35 OVĚŘENO TŘEMI KROKY: deploy #39 na 3143f31d
             (completed/success 09:42:11Z), verze 3985379c-… == živý tail (72 eventů)
brány:     g3 → 49 bran (2 NEDEKLAROVANÉ exity) · validate-all → 0 problémů PO
           regeneraci inventáře · test-tick-offline 231/0 (bylo 218/0)
           · p35-mutace 33/0 · p36-a-overeni 26/3 (3 ROZDÍLY) · p36-mutace 45/0
           · kronika SEDÍ · handoff 83/83 · ov-g 0 NEOVĚŘENO
ŽIVÝ TEP:  last_cron tiká (0–1 min, zdroj cron), cron cpuTime medián 21,5 ms
           (n=22), VŠECHNY cron eventy outcome=ok
```

**P36 NEMĚNILA CHOVÁNÍ ORCHESTRY.** Jediné změny jsou: model `state` v testovacím
harnessu (`tools/test-tick-offline.mjs`, +13 kontrol) a registrace dokladů
(`_analyza/p20-d-doklady.py`). **Conductor se needitoval, nic se nenasazovalo.**

### 67.6 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p36-a-overeni.py --plne        # A0–A7 (A7 ~5,5 min: g3 + validate-all)
python _analyza\p36-mutace.py                  # 45/0 — 7 vrat, každé v KOPII
node tools\test-tick-offline.mjs               # 231/0 (scénář AG = tep se ZAPÍŠE)
python _analyza\p36-strop-sonda.py             # D1: proč se nevydává (STROP GRANULE)
node _analyza\p36-agent-behy.mjs --vsechny     # GitHub API: čím selhaly běhy agenta
node _analyza\p36-cf-token-sonda.mjs           # CF tokeny (oauth vs. API token)
python _analyza\g3-brany.py                    # 49 bran (POZOR: FORGE_REGISTR v harnessu)
node tools\validate-all.mjs                    # po regeneraci inventáře 0 problémů
```

### 67.7 Co čeká na tebe (uživatel)

* **ROZHODNUTÍ 1 — CO OPRAVIT PRVNÍ.** Orchestr **šest dní nevydal práci**
  (poslední úspěch 5. 10. 02:01Z). Čtyři příčiny a jejich cena:
  **(a) push PR bez pověření** — 15 běhů, oprava = platný `FORGE_PAT` v repu hry
  (a to je zásah do cizí služby/nastavení = **tvoje**);
  **(b) parse brána** — 49 běhů, oprava promptu/`agent.yml` **ve hře** (vede ji
  cizí session);
  **(c) testy hry** — 15 běhů; **(d) TPM 8000** — 8 běhů, tj. menší granule
  nebo slabší model.
  **Doporučení P36: (a) je nejlevnější a vrací 15 zahOZENÝCH prací** — ale je to
  změna secretu, tedy tvoje.
* **ROZHODNUTÍ 2 — STROP GRANULE.** Možnosti: **nezvedat** (práce zůstane
  stát, ale nic se nespálí), **zvednout** (spálí se další běhy na tytéž vady),
  nebo **resetovat řádky granulí** (`roadmap-reset` — cesta zpět je v kódu).
  **Doporučení P36: nezvedat, dokud není opravená aspoň (a).**
* **ROZHODNUTÍ 3 — HRA.** `uo-shadows` má **dva lokální commity, které nejsou
  na remote** (`origin/main` = `01a9649`, lokálně `e4dccdb`). P36 do hry
  **nesahala** — je to stav cizí session. **Nic jsem tam neměnil a nic jsem
  nepushoval.**
* **Cesta zpět:** P36 je jeden commit v orchestra; `git revert <sha>` vrátí
  testovací harness i registraci dokladů. Nasazení ani D1 se nedotklo.
"""

RADEK_51 = (
    "| **51** | **11. 10. 2026** (12:0x – 14:0x UTC) | **ověřovací (Úkol A: "
    "přeměření P35 vlastním měřidlem) + akční (Úkol B: PROČ SE NEVYDÁVÁ PRÁCE "
    "— čtyři příčiny MIMO strop) + nálezová** | **PŘEMĚŘIT P35 A ZJISTIT, PROČ "
    "ORCHESTRA NEVYDÁVÁ PRÁCI.** Zadání P36 §2.1 žádalo vlastní měřidlo („autor "
    "není nezávislý reviewer“) a §2.2 hlavní stopu: `ready=3`, `running=0`, "
    "`STROP GRANULE 8/8` na #244/#245/#246. **A:** `p36-a-overeni.py` (A0–A7) → "
    "**26 kontrol, 3 pojmenované ROZDÍLY**, `p36-mutace.py` **45/0** (7 vrat "
    "v KOPIÍCH). Nasazení P35 ověřeno TŘEMI KROKY: `deploy.yml` **#39 na "
    "`3143f31d`** `completed/success`, verze z logu **`3985379c-…`** == "
    "`scriptVersion.id` **živého** tailu (72 eventů); oprava H165 je v KÓDU "
    "(indexovaný cyklus, bez `Uint8Array.from(atob…)`) a `test-tick-offline` "
    "**218/0 → 231/0** (nový scénář **AG**). `p35-a-overeni.py --plne` dnes "
    "**73/0** (3 ROZDÍLY, 1 NÁLEZ) vs. doklad P35 **74/0** — rozdíl POJMENOVANÝ "
    "(noha A5 Cloudflare Analytics: ve 12:33Z **HTTP 401**, v 12:40Z **HTTP 200** "
    "týmž nástrojem) — a **zadání tvrdí 71/0**, což je číslo dřívějšího běhu. "
    "**B — PŘÍČINA JE JINDE, NE VE STROPU:** strop je naměřený a FUNGUJE "
    "(počítadlo granulí 8/8 týmž SQL jako conductor; 8 běhů = 5× #241/#242/#243 "
    "+ 3× #244/#245/#246, 8. 10. 16:52 → 9. 10. 19:41); v D1 mají VŠECHNY "
    "`summary='GitHub Actions: failure'` a `log_tail` PRÁZDNÝ. GitHub API přes "
    "**29 běhů úloh #240–#246 (všechny `failure`)**: **14× push PR** "
    "(`fatal: could not read Username for 'https://github.com'`, exit 128 — "
    "job agenta USPĚL a práce byla ZAHOZENA), **8× „agent nic nezměnil“** "
    "(`RateLimitError … TPM Limit 8000`), **6× parse brána**, **1× testy hry**. "
    "Posledních **100 běhů: 95 `failure` / 5 `success`** (49 parse · 15 nic "
    "nezměnil · 15 PR auth · 15 testy hry · 1 auto-merge ručně) a **poslední "
    "ÚSPĚŠNÝ běh agenta je #297 z 5. 10. 02:01Z** → orchestr nevydal práci "
    "**šest dní**. **ZAVŘENÁ VADA:** `fakeDb` neznal tabulku `state` → harness "
    "tvrdil 218/0, a přitom se **zápis tepu vůbec neprovedl** a `/health` čítal "
    "svou `catch` větev; dnes model `state` + scénář **AG** (13 kontrol) a "
    "mutace M7 to dokazuje "
    "| **—**"
)

SEKCE_229 = """### 2.29 Nálezy z P36 (11. 10. 2026) — šestidenní výpadek, který strop granulí jen zamaskoval

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P37.

| # | Nález | Doklad |
|---|---|---|
| **H170** | **VLASTNÍ MĚŘIDLO P36 PŘEMĚŘILO P35 — a ZADÁNÍ MÁ ZASTARALÉ ČÍSLO.** `p35-a-overeni.py --plne` dnes **73 kontrol, 0 chyb** (3 ROZDÍLY, 1 NÁLEZ); doklad P35 `p35-a-overeni-vystup.txt` má **74/0**; **zadání P36 tvrdí 71/0 se 2 ROZDÍLY**, což je číslo DŘÍVĚJŠÍHO běhu téhož měřidla — zadání si tedy odporuje s dokladem, na který odkazuje (`analytický dokument musí mít datum spotřeby`). Rozdíl 74 → 73 je **POJMENOVANÝ po sekcích**: chybí jediná kontrola — noha **A5 „Cloudflare Analytics (48 h)“**, která ve **12:33Z** vrátila **HTTP 401 „Authentication error“ (kód 10000)** a **v 12:40Z týž nástroj s týmž configem HTTP 200** (5 784 řádků) → hlásila **NEZMĚŘENO** (a to je správně, není to nula). Příčina (stav OAuth tokenu z wrangler configu; `expiration_time` = `2026-10-11T13:33:12Z`) **nebyla změřena** — je to pozorování, ne tvrzení. | `_analyza/p36-a-overeni-vystup.txt`, `_analyza/p36-p35a-plne-vystup.txt`, `_analyza/p35-a-overeni-vystup.txt`, `_analyza/p36-p35a-a5-vystup.txt`, `_analyza/p36-cf-token-vystup.txt` |
| **H171** | **ORCHESTRA NEVYDÁVÁ PRÁCI ŠEST DNÍ A STROP GRANULE TO JEN ZAMASKOVAL — všechny čtyři příčiny jsou MIMO strop.** D1: tři úlohy `ready` (#244 `engine.input`, #245 `world.bodies`, #246 `engine.shell`), řádky `roadmap` z 8. 10. 16:51, `naposledy_selhalo` 9. 10. 19:44–19:45; počítadlo **týmž SQL jako conductor** (`SQL_GRANULE_RUNS`) je u všech tří **8/8** (= `GRAIN_MAX_RUNS`). Těch 8 běhů = 5 běhů #241/#242/#243 (8. 10. 16:52 → 9. 10. 09:20) + 3 běhy #244/#245/#246 (9. 10. 12:05 → 19:41); v D1 mají **VŠECHNY** `summary='GitHub Actions: failure'` a **`log_tail` PRÁZDNÝ**, takže příčina v D1 NENÍ. GitHub API, **29 běhů úloh #240–#246, všechny `failure`**: **14× „Otevři pull request“** (job agenta USPĚL, ale `create-pull-request` spadl na `fatal: could not read Username for 'https://github.com'`, **exit 128** — práce ze 14 běhů byla ZAHOZENA), **8× „Agent nic nezměnil“** (`litellm.RateLimitError: Request too large … TPM: Limit 8000`), **6× kontrola parsování**, **1× testy hry**. Celá poslední stovka (2. 10. 11:13Z – 9. 10. 19:42Z): **95 `failure` / 5 `success`** (49 parse · 15 nic nezměnil · 15 PR auth · 15 testy hry · 1 auto-merge ručně). **Poslední ÚSPĚŠNÝ běh agenta = #297 z `2026-10-05T02:01:00Z`** → šest dní bez vydané práce. **Strop je brzda, která funguje** — zvednout ji bez opravy znamená spálit další běhy na tytéž vady. | `_analyza/p36-strop-vystup.txt` (D1, READ-ONLY), `_analyza/p36-agent-behy-vystup.txt` (GitHub API, klasifikace podle selhaného kroku), `_analyza/p36-pat-sonda-vystup.txt` (jména secretů), `_analyza/p36-log-job-113995319876-vystup.txt` (celý log jobu PR) |
| **H172** | **`fakeDb` NEZNAL TABULKU `state`: HARNESS TVRDIL 218/0, A PŘITOM SE ZÁPIS TEPU VŮBEC NEPROVEDL (zavřeno).** Conductor zakládá a plní `state` (`zajistiTepTabulku`/`zapisPokus`/`zapisTep`) a `/health` ji čte (`SELECT k, v FROM state …`); `fakeDb` v `tools/test-tick-offline.mjs` ty dotazy **neznal** → `run()`/`all()` hodily „neznámý dotaz“ → conductor to **chytá** (`tep (manual) selhal: …`) a jede dál → zápis se neprovedl a `/health` čítal svou `catch` větev (`last_cron: null` VŽDY) → **každá kontrola o tepu měřila něco jiného, než si myslela** (přesně slepé místo, které P35 §66.3 pojmenovala pro P36). **Oprava:** model `state` v `fakeDb` + scénář **AG** (13 kontrol) — ruční tik zapíše `last_tick` + `last_tick_zdroj=manual` a **NEOBNOVÍ `last_cron`** (H112), plánovaný tik zapíše **`cron_pokus` PŘED tikem** (H156) i `last_cron`, a `/health` obojí **PŘEČTE z D1** včetně `last_cron_pokus_min`. **218/0 → 231/0.** Mutační důkaz: `p36-mutace.py` **M7** vrátí slepost v KOPII testu → test spadne a **5 kontrol AG** ji pojmenuje. | `tools/test-tick-offline.mjs` (scénář AG), `_analyza/p36-mutace.py` (M7), `_analyza/p36-mutace-vystup.txt` |
| **H173** | **VLASTNÍ OMYL P36: `--vystup` NENÍ TRANZITIVNÍ — měřidlo s přesměrovaným výstupem pouští vnitřní nástroje s PEVNOU cestou.** `python _analyza\\p35-a-overeni.py --plne --vystup _analyza\\p36-p35a-plne-vystup.txt` (tj. S ochranou podle H166) přesto přepsalo doklady **vnitřních noh**: `p35-cf-analytika-vystup.txt` (dnes 155 B: `CHYBY: [{"code":10000,"message":"Authentication error"}]`), `p35-d1-state-vystup.txt` (**902 → 256 B**), `p34-mereno-vystup.txt`, `p33-*`, `p34-health-*`. U `p34-cf-analytika-vystup.txt` si P35 zálohu **dělá** (soubor zůstal 1 231 267 B, jen s novým `mtime`) — ale `--vystup` tu ochranu **nepředává dál**. K tomu dva vlastní omyly téhož druhu: `p32-sonda-cf-verze.mjs` puštěný bez třetího argumentu přepsal `p32-cf-verze-vystup.txt` (gitignorovaný = NEVRATNÝ) a `p35-sonda-health.mjs` přepsal `p35-health-vystup.txt`. **Pravidlo: měřidlo s vnitřními nohami se pouští se ZÁLOHOU celého `_analyza/`, ne jen svého výstupu.** | `_analyza/p35-cf-analytika-vystup.txt`, `_analyza/p35-d1-state-vystup.txt` (256 B), `_analyza/p34-cf-analytika-vystup.txt` (1 231 267 B, záloha P35), výpis `Get-ChildItem _analyza -File` s `LastWriteTime` |
| **H174** | **ŠABLONA A HRA MAJÍ `agent.yml` ROZDÍLNÝ — A BĚŽÍ TA VERZE VE HŘE.** Blob `repo/.github/workflows/agent.yml` (orchestra) = `d48746bacf02d7242df8876f6c391af523246ce0`, blob `.github/workflows/agent.yml` (hra) = `10b07ec14ae9b780454849c9edf34669c3a85df9`; normalizovaný diff (po odstranění CRLF) má **78 změněných řádků** (jiný tvar komentářů u parse brány, statická kontrola `class_name` sloučená do téhož kroku). Drift je **deklarovaný** (`tools/kontrola-driftu.mjs` zná „šablona má o tři kroky víc“), ale pro orchestra je rozhodující něco jiného: **95 % změřených selhání se děje v kódu VE HŘE**, takže oprava šablony sama nic nezlepší — a hru vede **cizí session** (P36 do ní nesahala). | `git hash-object` obou souborů, `git rev-parse HEAD:<cesta>` v obou repech, normalizovaný `difflib` diff |
"""


def zapis_handoff():
    txt = HANDOFF.read_text(encoding="utf-8")
    if re.search(r"^## 67\.", txt, re.M):
        zk(True, "HANDOFF: §67 už je zapsaný (idempotentní — nepřidávám)")
        return
    zk(re.search(r"^## 66\.", txt, re.M) is not None, "HANDOFF: §66 existuje (za něj se přidává §67)")
    pred = len(txt.encode("utf-8"))
    novy = txt.rstrip("\n") + "\n" + SEKCE_67 + "\n"
    HANDOFF.write_text(novy, encoding="utf-8", newline="\n")
    po = len(novy.encode("utf-8"))
    zk(po > pred, "HANDOFF: §67 přidán (blob %d → %d B)" % (pred, po))
    zk(re.search(r"^## 67\.", novy, re.M) is not None, "HANDOFF: §67 je v souboru")


def zapis_kroniku():
    radky = KRONIKA.read_text(encoding="utf-8").splitlines(keepends=True)
    if any(r.startswith("| **51** |") for r in radky):
        zk(True, "KRONIKA: řádek 51 už je (idempotentní — nepřidávám)")
    else:
        i50 = next((i for i, r in enumerate(radky) if r.startswith("| **50** |")), None)
        zk(i50 is not None, "KRONIKA: řádek 50 existuje (za něj se vkládá 51)")
        if i50 is None:
            return
        radky.insert(i50 + 1, RADEK_51 + "\n")
        zk(RADEK_51.count("|") == 5,
           "KRONIKA: nový řádek má 5 svislítek (jako řádky 43–50, ne 8 jako záhlaví)")

    txt = "".join(radky)
    if re.search(r"^### 2\.29 ", txt, re.M):
        zk(True, "KRONIKA: §2.29 už je (idempotentní — nepřidávám)")
    else:
        kotva = "\n## 3. Počty omylů"
        zk(txt.count(kotva) == 1, "KRONIKA: kotva „## 3. Počty omylů“ je PRÁVĚ 1×")
        txt = txt.replace(kotva, "\n" + SEKCE_229 + kotva, 1)
        zk(re.search(r"^### 2\.29 ", txt, re.M) is not None, "KRONIKA: §2.29 je v souboru")
    KRONIKA.write_text(txt, encoding="utf-8", newline="\n")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--jen", default=None, choices=["HANDOFF", "KRONIKA"])
    args = ap.parse_args()

    print("=" * 96)
    print("P36 — ZÁPIS ZÁZNAMŮ (HANDOFF §67, KRONIKA řádek 51 + §2.29)")
    print("=" * 96)
    sha_h = hashlib.sha256(HANDOFF.read_bytes()).hexdigest()
    sha_k = hashlib.sha256(KRONIKA.read_bytes()).hexdigest()
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

    (ANALYZA / "p36-zapis-stav-vystup.txt").write_text(json.dumps({
        "cas": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "handoff": {"pred": sha_h, "po": hashlib.sha256(HANDOFF.read_bytes()).hexdigest()},
        "kronika": {"pred": sha_k, "po": hashlib.sha256(KRONIKA.read_bytes()).hexdigest()},
    }, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print("\n" + "=" * 96)
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, len(chyb)))
    for c in chyb:
        print("   CHYBA %s" % c)
    print("=" * 96)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

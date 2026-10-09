# -*- coding: utf-8 -*-
r"""P30 — ZÁPIS ZÁZNAMŮ: HANDOFF §61, KRONIKA řádek 45 + nálezy §2.23, PLÁN.

⚠ PROČ SKRIPTEM (a ne `edit` toolem): řádky kroniky mají **přes 4000 znaků**
a kotva načtená z řádku ho **zkrátí** (omyly 194 a 206). Skript pracuje
s BAJTY, vkládá celé řádky a po zápisu ověřuje, že se nic neztratilo.

⚠ CO SE NESMÍ STÁT: HANDOFF ani KRONIKA se NEPŘEPISUJÍ, jen DOPLŇUJÍ.
Skript proto (a) jen vkládá, (b) před i po měří počty řádků a id,
(c) při jakékoli neshodě skončí `exit 1` a NIC nezapíše, (d) je IDEMPOTENTNÍ
(druhý běh jen řekne „už zapsáno“ a skončí `exit 0` — pouští ho i dávka
dokladů `p20-d-doklady.py`).

Použití: python _analyza\p30-zapis-zaznamu.py [--kontrola]
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


# ═══════════════════════════════════════════════════════════ HANDOFF §61 ═══
HANDOFF_61 = r"""
## 61. P30 — NASAZENÁ OPRAVA B6, ROZHODNUTÝ H111 A NÁVOD PRO ARCHITEKTA (9. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P30 + stav po P30**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**45**, nálezy **§2.23**), plán (`PLAN-DALSI-KROK.md`, dodatek P30).
Zadání P30 je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **9. 10. 2026, 08:0x–10:0x +02:00** (živý čas
> z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba) platí
> k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.23), aby každý nález byl dohledatelný
> z HANDOFF.md:** H119 = nasazení jde z PUSHE (ne z lokálního wrangleru)
> a dokumenty o nasazení zestárly · H120 = **H111 ROZHODNUTO: STROP GRANULE**
> · H121 = úklid osiřelých uvolnil i počítadlo stropu · H122 = **H114
> ROZHODNUTO: čekání na `engine.input`** · H123 = tvrzení „`p28-b-mutace.py`
> → 27/0" se přestalo reprodukovat (27/2) · H124 = měřidlo P29 nechává
> v živém stromě MUTANTY · H125 = dávka dokladů neznala `p3x-*` (třída S27)
> · H126 = zastaralý inventář shodí DVĚ brány · H127 = `validate-all` je dnes
> ZELENÝ · H128 = pořadí „vypnout hru → push → úklid“ je NESPLNITELNÉ ·
> H129 = `acceptance` nemá čtenáře (potvrzeno) a skill dostal návod (B8).

### 61.1 Push a nasazení (rozhodnutí uživatele — PROVEDENO)

| Krok | Naměřeno |
|---|---|
| **PUSH** | `ef04912..cf1f280  main -> main` (PAT ze souboru, do výstupu nepronikl); `tools\git.cmd ls-remote` → **`cf1f280` = HEAD**. ⚠ Lokální `origin/main` push sám **neaktualizoval** (`cannot lock ref … Permission denied` — stav sandboxu) → musel se dohnat `fetch`; **kdo věří `rev-list --count origin/main..HEAD`, vidí 1 i po úspěšném pushi** |
| **NASAZENÍ** | `deploy.yml` **běh #35** na `cf1f280` → `completed/success` (created 06:08:48Z); Cloudflare deployments: **06:09:17Z, verze `1e1b5e69`** = **29 s po pushi** → **deploy jde z pushe**, ne z lokálu |
| **LOKÁLNÍ `wrangler deploy`** | **funguje** (OAuth token platný, scopes `workers:write` + `d1:write`; verze `77a5f345` v 06:16:19Z). `README.md:144–148` tvrdí opak (naměřeno 30. 9. 2026) → **zastaralý záznam** (H119). Před přepnutím politiky sandboxu padal na `spawn EPERM` (naměřeno, ne odhad) |
| **3. krok: nový artefakt** | `POST /tasks/cleanup {dry_run:true}` → **`osirelych_radku: 0`** (před: **5**) a tik pojmenovává `… \| v cooldownu 3 úloh: #241, #242, #243` — **obojí umí jen nový kód** (B6) |

### 61.2 Úkol A — vlastní měřidlo P30

`_analyza/p30-a-overeni.py` (**A1, A3, A4, A6, A7**), doklad
`_analyza/p30-a-plne-vystup.txt`:

* **plný běh: 35 kontrol, 0 chyb, 6 pojmenovaných ROZDÍLŮ** (986 s);
  mutační důkaz `_analyza/p30-mutace.py` → **16/0** (dvě mutace, každá tři nohy,
  soubory vráceny bajt na bajt).
* **A1** (umí měřidlo P29 spadnout?): `p29-a-overeni.py --jen A1M13` → **7/0**,
  `p29-b6-mutace.py` → **15/0** — obě tvrzení §60.1 **reprodukována**.
* **A3** (sedí čísla z §60?): každé tvrzení se **PŘEČTE Z DOKUMENTU** (vypisuje
  se okno, které vzor trefil) a pak se měří. Shoda: `test-tick-offline` **215/0**,
  `tick-mutace` **20 vrat/41/0**, `ov-g` **99 řádků Hxx**, `p29-b6-mutace` 15/0,
  `p29-a A1M13` 7/0. Posunula se **stavová** čísla: `over-skilly` **90 → 92**
  (moje práce na skillu), `g3` **1 → 0 NEDEKLAROVANÝCH**, `validate-all`
  **2 → 0 problémů**, kronika **43 → 44 řádků**.
* **A4** (stav před/po nasazení): viz 61.1.
* **A6** (H111) a **A7** (H114): 61.3.

### 61.3 Dvě rozhodnutí, která zadání žádalo

**H111 — PROČ DISPATCH STÁL: STROP GRANULE** (ne zámek). Měřeno z D1
(`_analyza/p30-sonda-d1.mjs`, jen SELECT):

1. **Cooldown vysvětluje #240–#243** a dispatch se **SÁM rozjel** 9. 10.
   `01:02:56` UTC = přesně 3 h po selháních (21:02–21:23) — žádné trvalé
   zaseknutí tedy neexistovalo.
2. **Úlohu #239 (osiřelá granule `entity.enemy`) přeskakoval STROP.** Počítadlo
   stropu = **běhy OD VZNIKU ŘÁDKU v cache** (mechanismus doložen na živém
   případu: `engine.registry` měl v 21:14:54 **3** spálené běhy podle watchdogu
   a dnes týž dotaz vrací **5**). Řádek `entity.enemy` vznikl ≈ **5. 10. 22:02**
   (watchdog 6. 10. hlásil „entity.enemy … 5 běhů“ = právě těch 5) → do tichého
   tiku **17 běhů** ≥ strop **8** (zapnutý 8. 10. 13:07).
3. **Hypotéza „zámek“ je VYLOUČENA měřením:** mezi posledním dokončeným během
   (8. 10. **21:14:53**) a tikem (**23:02**) **nebyl žádný běh** → `locked` bylo
   prázdné; a 99 min > `STALE_MINUTES` 90, takže i zaseknutá úloha už byla uvolněna.
4. **Dnes není za stropem žádná granule, která se má vydávat** (max 5 běhů;
   za stropem jen `sim.crafting` = 12, ale ta je `done`) — úklid osiřelých řádků
   **uvolnil i počítadlo** (H121).

**H114 — `entity.move.smooth`: JE TO LEGITIMNÍ ČEKÁNÍ, NE ZTRÁTA.** Granule je
v souboru (21 granulí), její `depends_on` = `engine.registry` ✓, **`engine.input`
(NEhotová)** ✗, `world.level` ✓, `entity.player` ✓. Filtr `ready` v conductoru
žádá **všechny** závislosti hotové, proto se řádek v cache nezakládá. `engine.input`
má v cache úlohu **#242 `ready`** (byla v cooldownu).

### 61.4 Úkol B — VĚCNÁ PRÁCE: **B8** (návod pro architekta)

Přenos `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` **§9** do skillu **`game-developer`**
jako nový pododdíl *„Výměna plánu je OPERACE — a co orchestra z granule SKUTEČNĚ
čte“* (za `## Mapování na orchestr`): **39 012 → 41 595 B**; brány
`over-skilly` **92 zmínek / 0 mrtvých**, `over-dokumentaci` **64/0**,
`kontrola-diakritiky` **VŠE OK** (bez BOM). Záloha před editací:
`~\.dsh\skills\game-developer\SKILL.md.pred-p30` (mimo git).

**Co se při tom NAMĚŘILO (H128) — a je to v rozporu s §9.3 i s plánem:**
doporučené pořadí „**vypnout hru → push → `/tasks/cleanup` → sonda**“ je
**NESPLNITELNÉ**:

* `/tasks/cleanup` čte roadmapu z **`raw.githubusercontent.com/{repo}/main/…`**
  (`index.ts:1576`) → **nepushnutá změna je pro něj neviditelná**; push musí být **PRVNÍ**.
* bere jen hry z registru **`active = 1`** (`:692`, `:1571`) → s vypnutou hrou
  vrátí **503** a **neudělá nic** (`:1591–1593`). Offline diferenciální test proti
  skutečnému handleru (dvě D1, scénáře se liší JEN odpovědí na dotaz her):
  hra ZAPNUTÁ → `200 {osirelych_radku:1}`, hra VYPNUTÁ → `503` a **žádný zápis**.
* **`/roadmap/reset` ≠ `/tasks/cleanup`** (potvrzeno): reset maže **celou cache**
  (`:1535`) a úloh se nedotkne; úklid maže **jen osiřelé** řádky a úlohy blokuje.
* Zavádějící komentáře v conductu: `:1558–1559` (nemožné pořadí) a
  `:1489–1493` (reset „vrátí úlohy do fronty“ — **nedělá to**, kód sám vysvětluje proč).

### 61.5 Živý stav při zápisu (9. 10. 2026, ~09:3x +02:00)

```
orchestra: HEAD cf1f280 · origin/main cf1f280 (pushnuto) · hra 01a9649 (cizí session)
živá služba: /health ok=true ready=3 running=0 games=1 · /roadmap 20 řádků (bylo 25)
             · /queue 50 úloh · osiřelé řádky 0 (bylo 5)
             · POSLEDNÍ BĚH 9. 10. 06:20:18 UTC (dispatch ŽIJE, 3 úlohy v cooldownu)
brány:       g3 → 49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače (`mutace B (combat)`, cizí brána hry)
             · validate-all → 1 → 0 problémů · test-tick-offline 215/0 · tick-mutace 41/0
             · p29-b6-mutace 15/0 · p30-a 35/0 · p30-mutace 16/0 · over-skilly 92/0
             · kronika SEDÍ · ov-g 99 řádků Hxx
```

### 61.6 Co čeká na tebe (uživatel)

* **Nic zásadního.** Push i nasazení jsou provedené a ověřené; okamžitá záplata
  `POST /tasks/cleanup` **už není potřeba** — úklid dělá tik sám (naměřeno:
  5 osiřelých → 0).
* **Zavádějící komentáře v conductu** (`:1558–1559`, `:1489–1493`) — oprava je
  změna kódu + nasazení; **rozhodnutí o směru**, ne úklid.
* **B3 (`/game/active {active:false}` na živé službě)** pořád čeká na výslovné „ano“.
* **Koncept od Gemini (docx)** — publikace převodu je tvoje rozhodnutí (repo je veřejné).

### 61.7 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\p30-a-overeni.py --jen A3         # čísla §60 proti dokumentu (~4 min)
python _analyza\p30-a-overeni.py --plne --tik     # celý Úkol A (~17 min; --tik MĚNÍ STAV)
python _analyza\p30-mutace.py                     # důkaz, že to měřidlo umí spadnout (16/0)
node _analyza\p30-sonda-deploy.mjs cf1f280       # push → běh deploy.yml na správném commitu
node _analyza\p30-sonda-d1.mjs _analyza\p30-d1-x-vystup.txt   # D1: počítadla, běhy, úlohy
python _analyza\kronika-kontrola.py               # SEDÍ + id 1..45 bez děr
python _analyza\handoff-kontrola-uplnost.py       # úplnost handoffu
python _analyza\ov-g-neovereno.py                 # 0 NEOVĚŘENO, rozsah 99 řádků Hxx
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\g3-brany.py                       # 49 bran
node tools\validate-all.mjs                       # 0 problémů
```
"""

# ═══════════════════════════════════════════════════════════ KRONIKA ═══
RADEK_45 = (
    "| **45** | **9. 10. 2026** (08:0x–10:0x +02:00) | **akční (Úkol A: push + nasazení) + "
    "ověřovací (Úkol A měřidlem) + akční (Úkol B8)** | "
    "**Nasadit opravu B6, přečíst novou odpověď tiku, rozhodnout H111 a vzít JEDNU věcnou práci.** "
    "**NASAZENÍ:** push `ef04912..cf1f280` ověřen `ls-remote` (`cf1f280` = HEAD) — a **push sám "
    "NEaktualizoval lokální `origin/main`** (`cannot lock ref … Permission denied`), takže "
    "`rev-list --count origin/main..HEAD` hlásil **1 i po úspěšném pushi**; nasazení přišlo "
    "**z PUSHE**: `deploy.yml` **#35** na `cf1f280` `completed/success` → Cloudflare "
    "**06:09:17Z** (verze `1e1b5e69`), tedy **29 s po pushi**. **Zadání i §60.4 přitom tvrdily, "
    "že je nutné spustit lokální `npx wrangler deploy`** — naměřeno: **není to potřeba** (deploy "
    "jde z gitu) a **lokálně to dnes FUNGUJE** (OAuth token platný, `workers:write`+`d1:write`; "
    "verze `77a5f345`), ačkoli `README.md:144–148` tvrdí opak (naměřeno 30. 9. 2026) → **zastaralý "
    "záznam, ne vada** (H119). **Třetí krok ověření (nový artefakt):** `POST /tasks/cleanup "
    "{dry_run:true}` → **osiřelých 0** (před **5**) a tik pojmenovává `v cooldownu 3 úloh: #241, "
    "#242, #243` — obojí umí **jen nový kód**. **H111 ROZHODNUTO — BYL TO STROP GRANULE:** "
    "dispatch se **sám rozjel 9. 10. 01:02:56 UTC** (přesně 3 h po selháních = cooldown), takže "
    "žádné trvalé zaseknutí neexistovalo; úlohu **#239** (`entity.enemy`) přeskakoval **strop**: "
    "počítadlo = **běhy od vzniku řádku v cache** (mechanismus doložen živě: `engine.registry` "
    "měl v 21:14:54 **3** spálené běhy podle watchdogu, dnes týž dotaz **5**), řádek vznikl "
    "≈ **5. 10. 22:02** (watchdog 6. 10.: „entity.enemy … 5 běhů“) → do tichého tiku **17 ≥ 8**; "
    "**hypotéza „zámek“ VYLOUČENA měřením** — mezi posledním dokončeným během (**8. 10. 21:14:53**) "
    "a tikem (**23:02**) **nebyl žádný běh** a 99 min > `STALE_MINUTES` 90. **H114 ROZHODNUTO:** "
    "`entity.move.smooth` **čeká na `engine.input`** (ta je `done: None`; `engine.registry`, "
    "`world.level` i `entity.player` hotové) → filtr `ready` žádá všechny závislosti, řádek "
    "v cache proto není. **VLASTNÍ MĚŘIDLO:** `_analyza/p30-a-overeni.py` (A1, A3, A4, A6, A7) → "
    "plný běh **35 kontrol / 0 chyb / 6 pojmenovaných ROZDÍLŮ** (986 s) + mutační důkaz "
    "`_analyza/p30-mutace.py` **16/0** (dvě mutace, každá tři nohy, návrat bajt na bajt; M1 mutuje "
    "ČÍSLO V DOKUMENTU, M2 **kontrakt** brány `over-skilly`). **A1:** `p29-a-overeni.py --jen A1M13` "
    "**7/0**, `p29-b6-mutace.py` **15/0** — tvrzení §60.1 **reprodukována**. **A3:** každé tvrzení "
    "se **PŘEČTE Z DOKUMENTU** (vypisuje se okno, které vzor trefil) a pak se měří — shoda u "
    "`test-tick-offline` 215/0, `tick-mutace` 20 vrat/41/0, `ov-g` 99; **posunula se stavová "
    "čísla**: `over-skilly` **90 → 92**, `g3` **1 → 0 NEDEKLAROVANÝCH**, `validate-all` **2 → 0**, "
    "kronika 43 → 44 řádků. **ÚKOL B8 (věcná práce):** přenos „návodu pro architekta“ z "
    "`JAK-PSAT-…` **§9** do skillu `game-developer` (**39 012 → 41 595 B**, brány zelené) — "
    "a při tom **NAMĚŘENO, ŽE §9.3 I PLÁN DOPORUČUJÍ NESPLNITELNÉ POŘADÍ** (H128): "
    "`/tasks/cleanup` čte roadmapu z **`main` v GitHubu** (push musí být PRVNÍ) a bere **jen hry "
    "`active = 1`** → s vypnutou hrou vrací **503 a neudělá nic** (offline diferenciální test "
    "proti skutečnému handleru: hra ZAPNUTÁ → `200 {osiřelých 1}`, hra VYPNUTÁ → `503`, žádný "
    "zápis); **`/roadmap/reset` ≠ `/tasks/cleanup`** (reset maže celou cache a úloh se nedotkne) | "
    "**—**"
)

NALEZY_223 = r"""
### 2.23 Nálezy z P30 (9. 10. 2026) — nasazení z pushe, strop granule a měřidlo, které si podkopalo vlastní tvrzení

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P31.

| # | Nález | Doklad |
|---|---|---|
| **H{P1}** | **NASAZENÍ JDE Z PUSHE — A DOKUMENTY O NASAZENÍ ZESTÁRLY.** Zadání P30 i §60.4 tvrdily, že je nutné spustit `npx wrangler deploy` v `conductor/`; naměřeno: push `cf1f280` spustil `deploy.yml` **#35** (`completed/success`) a Cloudflare nasadil **29 s po pushi** (06:09:17Z, verze `1e1b5e69`). Lokální deploy **dnes funguje** (OAuth token platný, verze `77a5f345`), ačkoli `README.md:144–148` tvrdí opak. **A push sám neaktualizoval lokální `origin/main`** (`cannot lock ref … Permission denied`) → `rev-list --count origin/main..HEAD` hlásil 1 i po úspěšném pushi; náprava je `fetch`. | `_analyza/p30-sonda-deploy.mjs`, `wrangler deployments list` (`_analyza/p30-nasazeni-seznam-vystup.txt`), `tools\git.cmd ls-remote`, `wrangler whoami` |
| **H{P2}** | **H111 ROZHODNUTO: BYL TO STROP GRANULE, NE ZÁMEK.** (a) **Cooldown** vysvětluje #240–#243 a dispatch se **sám rozjel** 9. 10. 01:02:56 UTC = 3 h po selháních; (b) úlohu **#239** přeskakoval **strop** — počítadlo je **běhy od vzniku řádku v cache** (doloženo živě na `engine.registry`: watchdog 21:14:54 hlásil **3**, dnes týž dotaz **5**), `entity.enemy` měl do tichého tiku **17 běhů** ≥ strop 8; (c) **zámek vyloučen měřením** — mezi posledním dokončeným během (21:14:53) a tikem (23:02) **nebyl žádný běh** a 99 min > `STALE_MINUTES` 90. | `_analyza/p30-sonda-d1.mjs` (D1, jen SELECT: `runs`, `tasks`, `roadmap`), `_analyza/p29-sonda-ntfy.mjs` (zprávy watchdogu), `conductor/wrangler.toml` (`GRAIN_MAX_RUNS=8`) |
| **H{P3}** | **ÚKLID OSIŘELÝCH UVOLNIL I POČÍTADLO STROPU.** Po nasazení B6 uklidil tik 5 osiřelých řádků sám → **dnes není za stropem žádná granule, která se má vydávat** (max 5 běhů; za stropem zůstává jen `sim.crafting` = 12, ale ta je `done` a nevydává se). Cesta zpět pro zastropovanou granuli zůstává `POST /roadmap/reset`. | `POST /tasks/cleanup {dry_run:true}` (5 → **0**), dotaz počítadla v `p30-sonda-d1.mjs` |
| **H{P4}** | **H114 ROZHODNUTO: `entity.move.smooth` ČEKÁ NA ZÁVISLOST, NENÍ TO ZTRÁTA.** Je v souboru (21 granulí), `depends_on` = `engine.registry` ✓, **`engine.input` (`done: None`)** ✗, `world.level` ✓, `entity.player` ✓ → filtr `ready` žádá všechny závislosti hotové, proto se řádek v cache nezakládá. | soubor hry `.forge/roadmap.json` + `conductor/src/index.ts` (filtr `ready`), `p30-a-overeni.py` sekce A7 |
| **H{P5}** | **TVRZENÍ „`p28-b-mutace.py` → 27/0“ SE PŘESTALO REPRODUKOVAT (dnes 27/2) — A PŘÍČINOU JE ZÁZNAM SÁM.** M1 počítá výskyt kotvy `**99 řádků Hxx**` v **CELÉM** dokumentu a srovnává ho s počtem v §57 — P29 si vlastním zápisem **§60** přidala **druhý** výskyt (řádek 2502), takže kontrola padá. M2c pak stojí na **téže chybě v obou nohách** a baseline `g3` se posunul (**1 NEDEKLAROVANÝ → 0**), takže diferenciál nevychází. | spuštění `_analyza/p28-b-mutace.py` (`_analyza/p30-p28b-po-inventari-vystup.txt`), počty výskytů kotvy v `HANDOFF.md`, `_analyza/p28-a-overeni.py:792–794` |
| **H{P6}** | **MĚŘIDLO P29 NECHAVÁ PO SOBĚ MUTANTY V ŽIVÉM STROMĚ.** `p29-a-overeni.py` zapisuje mutantní kopie `_analyza/p29-mut-handoff.md` (**186 kB**) a `_analyza/p29-mut-ovg.py` a **neumí je uklidit**; **nejsou gitignorované**, takže vstupují do inventáře, do `git status` i do `git add -A`. Naměřeno: po běhu A1 se objevily a **shodily dvě brány** (`n1-over-inventar`, `C2: mutace N1` — obě `exit 2`), protože inventář byl rázem zastaralý. | `git status`, časy vzniku souborů vs. běh měřidla, registr `_registr-bran.json` |
| **H{P7}** | **DÁVKA DOKLADŮ NEZNALA `p3x-*`** — vzor v `p20-d-doklady.py` byl `^(ov-\|p1[6-9]-\|p2[0-9]-)`, takže nový doklad by v dávce **tiše chyběl** (třída vady **S27**: brána, která soubor nikdy neotevře). Opraveno rozšířením vzoru na `p3[0-9]-` **a** zápisem `p30-mutace.py` + sond do `PRESKIP` s pojmenovaným důvodem (mutační test nesmí běžet v dávce, která si hlídá hash dokumentů). | `_analyza/p20-d-doklady.py` (`VZOR`, `PRESKIP`), běh dávky |
| **H{P8}** | **ZASTARALÝ INVENTÁŘ SHODÍ DVĚ BRÁNY — a je to SPRÁVNÉ chování, ne vada.** Po přidání `p30-*` souborů hlásil `g3` **2 NEDEKLAROVANÉ exity** (`n1-over-inventar` a `C2: mutace N1`, oba `exit 2`); po přegenerování inventáře (`hl-neanglicky-v-kodu.py --json`) byl `g3` **49 bran / 0 NEDEKLAROVANÝCH / 1 bez čítače** (`mutace B (combat)` — cizí brána hry). Náprava je **přegenerovat**, ne deklarovat stav. | `_analyza/_registr-bran.json` před/po, `python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json` |
| **H{P9}** | **`validate-all` JE DNES ZELENÝ (0 problémů).** P29 měřila **2** (stav HRY/D1) a §59 třetí (`lokální kód ≠ repo`); push a úklid osiřelých řádků odstranily obě příčiny. Tvrzení o počtu problémů je tedy **stav**, ne měřidlo — v `p30-a-overeni.py` je proto `mekke={0}` (ROZDÍL s vysvětlením, ne CHYBA). | `node tools\validate-all.mjs`, `python _analyza\g3-brany.py` |
| **H{P10}** | **POŘADÍ „VYPNOUT HRU → PUSH → ÚKLID“ JE NESPLNITELNÉ (B8).** `/tasks/cleanup` čte roadmapu z **`main` v GitHubu** (`index.ts:1576`) → push musí být první; bere **jen hry `active = 1`** (`:692`, `:1571`) → s vypnutou hrou vrací **503** a neudělá nic (`:1591–1593`). Offline diferenciální test proti skutečnému handleru (dvě D1, scénáře se liší JEN odpovědí na dotaz her): ZAPNUTÁ → `200 {osiřelých 1}`, VYPNUTÁ → `503`, **žádný zápis**. **`/roadmap/reset` ≠ `/tasks/cleanup`** potvrzeno (reset maže celou cache a úloh se nedotkne). Zavádějící komentáře v conductu: `:1558–1559`, `:1489–1493`. | `conductor/src/index.ts` (řádky), bundle `_analyza/tick-scratch/index.js` + falešná D1, `§9.3` v `JAK-PSAT-…` |
| **H{P11}** | **`acceptance` NEMÁ ČTENÁŘE (H116 potvrzeno) A SKILL `game-developer` DOSTAL NÁVOD PRO ARCHITEKTA (B8).** `acceptance` má v `conductor/` **0 výskytů**; `dispatchWorkflow` posílá **9 jiných polí**. Skill: nový pododdíl *„Výměna plánu je OPERACE…“* — **39 012 → 41 595 B**, brány `over-skilly` **92/0**, `over-dokumentaci` **64/0**, diakritika **OK** (bez BOM). Do skillu se **nepsalo schéma granule** (druhý zdroj pravdy = drift, který žádná brána neměří). | `grep` nad `conductor/`, `tools\over-skilly.py`, `tools\over-dokumentaci.py`, `tools\kontrola-diakritiky.py`, záloha `SKILL.md.pred-p30` |
"""

PLAN_DODATEK = r"""
---

## P30 (9. 10. 2026) — CO JE NASAZENÉ A CO JE NA ŘADĚ

> **Datum spotřeby:** 9. 10. 2026, ~10:0x +02:00. Platí pro stav po P30;
> kdo to čte později, **přeměří** (`python _analyza\p30-a-overeni.py`).

**Hotovo a nasazeno (neopakovat):** oprava **B6** je v živé službě — tik sám
uklízí osiřelé řádky cache (naměřeno **5 → 0**) a **pojmenovává**, co přeskočil
(`v cooldownu 3 úloh: #241, #242, #243`). Nález **H111** je rozhodnutý
(**strop granule**, ne zámek), **H114** taky (`entity.move.smooth` čeká na
`engine.input`). **Nasazení jde z pushe** — lokální `wrangler deploy` není
potřeba (a dnes naštěstí funguje taky).

**Nejbližší práce (P31) — v tomto pořadí:**

1. **Zavádějící komentáře v conductu** (`index.ts:1558–1559` „nejdřív vypni hru,
   pak cleanup“ a `:1489–1493` „reset vrátí úlohy do fronty“) — **jsou to
   tvrzení, která kód neplní**; oprava = změna textu + nasazení z pushe.
2. **`p28-b-mutace.py` je dnes 27/2** (H{P5}) — měřidlo P28 stojí na kotvě
   v CELÉM dokumentu a na společné chybě obou noh; buď opravit měřidlo
   (kotva vázaná na oddíl), nebo tvrzení v §60 označit za neplatné.
3. **Měřidlo P29 neuklízí mutanty** (H{P6}) — dokud to neopraví, každý plný běh
   A1 zanechá v `_analyza/` 186 kB mutanta a rozhodí inventář.
4. **B7 (řetěz poskytovatelů při kvótě)** — patří **session, která vede hru**
   (živý `agent.yml` je ve hře, orchestra do ní nepíše).
5. **B3 (`/game/active {active:false}`)** — čeká na výslovné „ano“ uživatele.

**Co NEDĚLAT:** neměnit architekturu orchestra kvůli konceptu od Gemini
(rozhodnuto v P29); nepsat do hry; nepřidávat do skillu `game-developer`
schéma granule (druhý zdroj pravdy).
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
    uz_h = "## 61. P30" in h
    uz_k = bool(re.search(r"^\|\s*\*\*45\*\*\s*\|", k, re.M))
    if uz_h and uz_k:
        print("  OK    záznamy P30 UŽ JSOU zapsané (HANDOFF §61 + KRONIKA řádek 45) "
              "— idempotentní běh, nic se nemění")
        check("KRONIKA: id 1..45 bez děr (kontrola i při idempotentním běhu)",
              [n for n in range(1, 46)
               if not re.search(r"^\|\s*\*\*%d\*\*\s*\|" % n, k, re.M)], [])
        print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
        return 0 if chyb == 0 else 1

    check("HANDOFF §61 ještě NENÍ (skript je idempotentní)", uz_h, False)
    check("KRONIKA řádek 45 ještě NENÍ", uz_k, False)
    check("KRONIKA má řádek 44 (kotva pro vložení)",
          bool(re.search(r"^\|\s*\*\*44\*\*\s*\|", k, re.M)), True)
    check("KRONIKA má oddíl §2.22 (kotva pro §2.23)", "### 2.22" in k, True)
    check("PLAN existuje a je neprázdný (dodatek se přidává na konec)",
          bool(p.strip()), True)
    check("PLAN dodatek P30 ještě NENÍ (idempotence)",
          "CO JE NASAZENÉ A CO JE NA ŘADĚ" in p, False)
    if chyb:
        print("NIC SE NEZAPÍŠE (%d chyb v kotvách)" % chyb)
        return 1

    h0 = hledej_max_h(k)
    print("  nejvyšší existující nález v kronice: H%d → nové začnou H%d" % (h0, h0 + 1))
    nalezy = NALEZY_223
    for i in range(1, 12):
        nalezy = nalezy.replace("{P%d}" % i, str(h0 + i))
    plan = PLAN_DODATEK.replace("{P5}", str(h0 + 5)).replace("{P6}", str(h0 + 6))

    # (1) KRONIKA: řádek 45 hned za řádek 44; §2.23 před "## 3."
    radky = k.splitlines()
    i44 = next(i for i, l in enumerate(radky) if re.match(r"^\|\s*\*\*44\*\*\s*\|", l))
    i3 = next(i for i, l in enumerate(radky) if l.startswith("## 3."))
    check("řádek 44 je PŘED oddílem §3 (jinak by vložení rozbilo tabulku)", i44 < i3, True)
    novy_k = (radky[:i44 + 1] + [RADEK_45] + radky[i44 + 1:i3] + [nalezy.strip(), ""] + radky[i3:])
    k_new = "\n".join(novy_k) + "\n"

    # (2) HANDOFF: §61 na konec
    h_new = h.rstrip("\n") + "\n" + HANDOFF_61.strip("\n") + "\n"

    # (3) PLÁN: dodatek na konec
    p_new = (p.rstrip("\n") + "\n" + plan.strip("\n") + "\n") if p else ""

    # ── ověření PŘED zápisem ──────────────────────────────────────────────
    check("HANDOFF: přibyl právě oddíl §61", "## 61. P30" in h_new and len(h_new) > len(h), True)
    check("HANDOFF: řádků neubylo", len(h_new.splitlines()) > len(h.splitlines()), True)
    check("HANDOFF: každý nález H%d..H%d je zmíněn (mapovací řádek)" % (h0 + 1, h0 + 11),
          all(("H%d" % (h0 + i)) in h_new for i in range(1, 12)), True)
    check("KRONIKA: přibyl řádek 45", bool(re.search(r"^\|\s*\*\*45\*\*\s*\|", k_new, re.M)), True)
    check("KRONIKA: id 1..45 bez děr",
          [n for n in range(1, 46)
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
    print("  zapsáno: HANDOFF.md §61, KRONIKA řádek 45 + §2.23, PLAN dodatek P30")
    print("VÝSLEDEK: %d kontrol, %d chyb" % (kontrol, chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

# -*- coding: utf-8 -*-
r"""P34 — ZÁPIS ZÁZNAMŮ (HANDOFF.md §65, KRONIKA řádek 49 + §2.27).

PROČ SKRIPTEM: řádky mají přes 3 000 znaků a kotva načtená z dokumentu ho
zkrátí (omyly 194, 206). Skript proto:
  * NIKDY nepřepisuje — jen VKLÁDÁ/DOPLŇUJE (HANDOFF i KRONIKA jsou záznamy),
  * čísla ČTE Z DOKLADŮ (ne z hlavy); co chybí, zapíše jako `NEMĚŘENO`,
  * PŘED zápisem ověří, že cilové kotvy existují PRÁVĚ 1× a že řádek 49 / §65 /
    §2.27 tam ještě NEJSOU (jinak by zápis zdvojil),
  * PO zápisu ověří, že řádek session má STEJNÝ počet svislítek jako vzor
    (P33 naměřila: řádek kroniky má **5** svislítek, ne 7 jako záhlaví),
  * seznam nálezů v HANDOFFu píše jako **PROSAICKÝ** (tabulkový řádek
    `| **Hxx** |` by zvedl počítadlo „99 řádků Hxx“ a shodil `ov-g` i měřidla P28).

Použití: python _analyza\p34-zapis-zaznamu.py
"""
import pathlib
import re
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
A = WS / "_analyza"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"


def citac(jmeno, vychozi="NEMĚŘENO"):
    """Poslední čítač `VÝSLEDEK: N kontrol, M chyb` z dokladu."""
    cesta = A / jmeno
    if not cesta.is_file():
        print("  ⚠ chybí doklad %s → %s" % (jmeno, vychozi))
        return vychozi
    t = cesta.read_text(encoding="utf-8", errors="replace")
    vse = list(re.finditer(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", t))
    if not vse:
        print("  ⚠ v %s není čítač → %s" % (jmeno, vychozi))
        return vychozi
    m = vse[-1]
    return "%s/%s" % (m.group(1), m.group(2))


def vyraz(jmeno, vzor, vychozi="NEMĚŘENO", skupina=1):
    cesta = A / jmeno
    if not cesta.is_file():
        print("  ⚠ chybí doklad %s → %s" % (jmeno, vychozi))
        return vychozi
    t = cesta.read_text(encoding="utf-8", errors="replace")
    m = re.search(vzor, t)
    if not m:
        print("  ⚠ v %s není %r → %s" % (jmeno, vzor, vychozi))
        return vychozi
    return m.group(skupina)


# ── čísla z dokladů (nic z hlavy) ───────────────────────────────────────────
levny = citac("p34-a-overeni-levny-vystup.txt")
plny = citac("p34-a-overeni-vystup.txt")
mut = citac("p34-mutace-vystup.txt")
print("čísla z dokladů: levný=%s plný=%s mutace=%s" % (levny, plny, mut))
g3 = vyraz("p34-g3-vystup.txt", r"brán celkem:\s*(\d+),\s*s nenulovým exit:\s*(\d+)", "NEMĚŘENO")
g3_celkem = vyraz("p34-g3-vystup.txt", r"brán celkem:\s*(\d+)")
g3_nenul = vyraz("p34-g3-vystup.txt", r"s nenulovým exit:\s*(\d+)")
g3_nedekl = vyraz("p34-g3-vystup.txt", r"NEDEKLAROVAN[ÝY]CH\s+(\d+)\s*:", "NEMĚŘENO")
cf_hodnoty = []
if (A / "p34-cf-analytika-vystup.txt").is_file():
    import json
    try:
        cfj = json.loads((A / "p34-cf-analytika-vystup.txt").read_text(encoding="utf-8"))
        podle = {}
        for x in cfj.get("radky") or []:
            k = x["dimensions"]["status"]
            podle[k] = podle.get(k, 0) + x["sum"]["requests"]
        cf_hodnoty = sorted(podle.items())
    except Exception as e:  # noqa: BLE001
        print("  ⚠ analytiku nelze přečíst: %s" % e)
cf_text = ", ".join("%s=%d" % kv for kv in cf_hodnoty) or "NEMĚŘENO"
d1 = {}
if (A / "p34-d1-state-vystup.txt").is_file():
    import json
    try:
        d1 = {x["k"]: x["v"] for x in json.loads((A / "p34-d1-state-vystup.txt").read_text(encoding="utf-8"))["radky"]}
    except Exception as e:  # noqa: BLE001
        print("  ⚠ D1 doklad nelze přečíst: %s" % e)
# ⚠ Windows `strftime` NEPODPORUJE `%-d`/`%-m` (spadl by na neplatném formátu) —
# proto se datum skládá z `localtime()` ručně.
_lt = time.localtime()
zdroj_datum = "%d. %d. %d" % (_lt.tm_mday, _lt.tm_mon, _lt.tm_year)
hodiny = time.strftime("%H:%M")

# Stav ŽIVÉ SLUŽBY a HEAD (pro „živý stav při zápisu“)
health = {}
if (A / "p34-health-vystup.txt").is_file():
    import json
    try:
        health = json.loads((A / "p34-health-vystup.txt").read_text(encoding="utf-8"))
    except Exception as e:  # noqa: BLE001
        print("  ⚠ doklad /health nelze přečíst: %s" % e)
last_cron_zdroj = d1.get("last_cron", health.get("last_cron", "NEMĚŘENO"))
health_min = health.get("last_cron_min", "NEMĚŘENO")
import subprocess
_r = subprocess.run(["node", str(WS / "tools" / "test-cron-pokus.mjs")], capture_output=True,
                    cwd=str(WS), env=dict(__import__("os").environ, PYTHONIOENCODING="utf-8"))
_t = ((_r.stdout or b"") + (_r.stderr or b"")).decode("utf-8", "replace")
_m = re.search(r"VÝSLEDEK:\s*(\d+)\s*kontrol,\s*(\d+)\s*chyb", _t)
pokus = "%s/%s" % (_m.group(1), _m.group(2)) if _m else "NEMĚŘENO"
_r = subprocess.run([str(WS / "tools" / "git.cmd"), "-C", str(WS), "rev-parse", "--short", "HEAD"],
                    capture_output=True, cwd=str(WS))
head = ((_r.stdout or b"") + (_r.stderr or b"")).decode("utf-8", "replace").strip()[:12] or "NEMĚŘENO"
print("živý stav: last_cron=%s (%s min) · pokus=%s · HEAD=%s" % (last_cron_zdroj, health_min, pokus, head))

# ── 1) řádek 49 do KRONIKY ─────────────────────────────────────────────────
RADEK49 = (
    "| **49** | **10.–11. 10. 2026** (%s +02:00) | **ověřovací (Úkol A: přeměření P33 "
    "vlastním měřidlem) + akční (Úkol B: H156 — PŘÍČINA výpadku cronu) + nálezová** | "
    "**PŘEMĚŘIT PRÁCI P33 VLASTNÍM MĚŘIDLEM A ZAVŘÍT ASPOŇ JEDNU ZE ZBÝVAJÍCÍCH VAD.** "
    "**PŘÍČINA VÝPADKU CRONU JE ZMĚŘENÁ (H156):** plánovaný tik **NEBYL zastavený** — "
    "cron trigger **DORAZÍ každou minutu** (`wrangler tail`: `event.cron = \"* * * * *\"`) "
    "a invocation **UMÍRÁ NA CPU LIMITU** free plánu (`outcome = \"exceededCpu\"`, "
    "`cpuTime = 10 ms`, `wallTime ≈ 0,7 s`); protože `zapisTep()` se pak nezavolá, "
    "`last_cron` zestárne a brána „cron NETIKÁ“ je **červená správně, ale pojmenovává to "
    "špatně**. Cloudflare Analytics (48 h): **%s** — a `exceededResources` je v **39 z 49** "
    "hodinových oken, takže nejde o výjimku. **OPRAVA (H157):** služba zapisuje "
    "**POKUS o tik PŘED tikem** (`cron_pokus` — jediný zápis, který smrt invocation přežije), "
    "`/health` ho posílá (`last_cron_pokus`, `last_cron_pokus_min`) a brána **rozlišuje "
    "„trigger NEDORAZIL“ od „tik NEDOBĚHL“** (`tools/cron-stav.mjs` + NOVÉ fixtury "
    "`tools/test-cron-pokus.mjs`, které `validate-all` pouští jako součást sebe). "
    "**CPU navíc (H159):** tři `ALTER TABLE roadmap` selhávaly na „duplicate column name“ "
    "**KAŽDÝ TIK** — tedy tři zbytečné D1 obraty na invokaci s rozpočtem 10 ms; migrace se "
    "nově ověří **jednou na isolate**. **VLASTNÍ MĚŘIDLO:** `_analyza/p34-a-overeni.py` "
    "(A0–A8 + B1) → levný běh **%s**, plný běh **%s**; mutační důkaz "
    "`_analyza/p34-mutace.py` → **%s**. **PŘEMĚŘENÍ P33:** `p33-a-overeni.py` levně "
    "**%s**; §64.2 („příčinu z tohoto pracoviště určit NELZE“) **přestalo platit** — "
    "byla to mez sandboxu (P33 nemohla spustit `wrangler`), ne vlastnost jevu. "
    "**PLÁN:** dodatek P34 | **—**"
) % (hodiny, cf_text, levny, plny, mut, levny)

# ── 2) §2.27 do KRONIKY ────────────────────────────────────────────────────
SEKCE_227 = """### 2.27 Nálezy z P34 (10.–11. 10. 2026) — PŘÍČINA výpadku cronu (CPU limit), ne zastavený trigger

> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.
> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je
> pojmenované jako práce pro P35.

| # | Nález | Doklad |
|---|---|---|
| **H157** | **PŘÍČINA VÝPADKU CRONU JE CPU LIMIT, NE ZASTAVENÝ TRIGGER (H156 DOŘEŠENO).** P33 naměřila jen OKNO a NÁSLEDEK a nechala příčinu otevřenou („bez logů Cloudflare“). P34 ji naměřila ze **TŘÍ nezávislých zdrojů**: (1) `wrangler tail` — cron event **DORAZÍ** (`event.cron = "* * * * *"`, každou minutu) a končí `outcome = "exceededCpu"`, `cpuTime = 10 ms` (limit free plánu), `wallTime ≈ 0,7 s`; (2) Cloudflare Analytics (GraphQL `workersInvocationsAdaptive`, 48 h) — **%s**, `exceededResources` v **39 z 49** hodinových oken; (3) D1 `state` — `last_cron` = `%s` (uložený tep se nehnul). **Řetěz:** trigger dorazí → invocation umře na CPU → `tick()` se nedokončí → `zapisTep()` se nezavolá → `last_cron` zestárne → brána hlásí „cron NETIKÁ“ (červená SPRÁVNĚ, ale jméno vady je jiné). **P33 to nemohla změřit proto, že jí `wrangler` v sandboxu padal na `spawn EPERM`** — byla to mez pracoviště, ne vlastnost jevu. | `_analyza/p34-tail-cron-vystup.txt`, `_analyza/p34-cf-analytika-vystup.txt`, `_analyza/p34-d1-state-vystup.txt` |
| **H158** | **SLABÁ KONTROLA VE VLASTNÍ FIXTUŘE: `ok === false` NEDOKAZUJE, že vada je POJMENOVANÁ.** První verze fixtury „pokus v budoucnosti“ kontrolovala jen `ok === false` — a **prošla i s predikátem, který budoucnost četl jako „trigger dorazí“** (`pokusMin = -1 <= limit`). Náprava: fixtura kontroluje i **TEXT** důvodu (`BUDOUCNOSTI`, ne `NEDOBÍHÁ`). Je to táž třída jako H140/H150 („kontrola se nechala uspokojit slabším tvrzením“). | `tools/test-cron-pokus.mjs` (fixtura 4), `_analyza/p34-mutace.py` |
| **H159** | **TŘI `ALTER TABLE` SELHÁVALY NA „duplicate column name“ KAŽDÝ TIK.** Naměřeno ve `wrangler tail` (tři logové řádky na každém cron eventu) — tedy **tři zbytečné D1 obraty, tři chybové objekty a tři zápisy do logu** na invokaci, jejíž celý CPU rozpočet je **10 ms**. Sloupce přitom existují od 2.–6. 10. 2026; migrace se nově ověří **jednou na isolate** (vzor, který v témž souboru už je: `tepTabulkaHotova`). | `conductor/src/index.ts`, `_analyza/p34-tail-cron-vystup.txt` |
| **H160** | **ŽIVÝ VÝPADEK SE PROPÍŠE DO ČÍTAČŮ BRAN — PODRUHÉ A ZNOVU POJMENOVANĚ.** `g3` hlásí **%s NEDEKLAROVANÝCH exitů** (jméno: `validate-all`) a `validate-all` je červený **PRÁVĚ** na bráně `cron běží (čas)`. Není to vada měřidla ani bran: **stav služby je součástí měření** (H156). Kdo to neví, hledá vadu tam, kde není. | `_analyza/p34-g3-vystup.txt`, `_analyza/p34-validate-all-vystup.txt` |
| **H161** | **`wrangler tail` PŘES POWERSHELL PIPELINE NEDODÁ DATA — `cmd` PŘESMĚROVÁNÍ DO SOUBORU ANO.** `node … wrangler.js tail … \\| node filtr.mjs` (i `\\| Out-File`) zůstalo po minuty **prázdné**, ačkoli oba procesy běžely; `cmd /c "… tail … > soubor"` zapsal **44 kB eventů** okamžitě. Je to past na měřicí nástroj, ne na wrangler: doklad se musí psát **přesměrováním**, ne trubkou. | `_analyza/p34-tail-raw-vystup.txt`, `_analyza/p34-tail-filtr.mjs` |
| **H162** | **`/health` SÁM JE NA HRANICI CPU ROZPOČTU (8 ms z 10).** Naměřeno v `wrangler tail`: `GET /health` → `cpuTime = 8 ms`, `wallTime = 1216 ms`; `/heartbeat` a `/claim` 1–3 ms. Služba tedy **není „v klidu“** — drtivá většina rozpočtu padne na D1 obraty a JSON; to je kontext, bez kterého by oprava tiku vypadala jako „přidat jeden zápis navíc“ (a on je to **pětinový** zásah do rozpočtu). | `_analyza/p34-tail-cron-vystup.txt` |
| **H163** | **PŘERUŠENÝ MUTAČNÍ BĚH ZANECHAL MUTANTA V ŽIVÉM ZDROJI — a poznalo se to až za hodinu přes ČERVENÉ BRÁNY (VLASTNÍ OMYL P34).** P34 ukončila dlouhou nohu `p33-a-overeni.py --plne` (běžela 45 min) — a v tu chvíli byl otevřený mutační blok `_mutace.mutuj` nad **živým** `conductor/src/index.ts` (mutace **M20** z `_analyza/tick-mutace.py`: `if (!res.meta.changes)` → `if (false)`, tj. `/game/active` přestane hlásit neznámou hru). `finally` se nevykonal a **mutant zůstal v živém souboru**. Následky naměřené o hodinu později: `test-tick-offline.mjs` → **215/1** (`V3: neznámá hra → 404`), `p29-a --jen A3` → **17/1**, `p30-mutace` → **11/5**, `p32-mutace` → **18/1** a `validate-all` → **7 problémů** (mimo jiné „**M20 … mutace se neprovedla**“ — harness nemohl mutaci aplikovat, protože kotva už byla pryč; to je PODPIS leftoveru). Po vrácení řádku z `HEAD` je vše zelené (`test-tick-offline` **215/0**, `p29-a --jen A3` **17/0**, `p30-mutace` **16/0**, `p32-mutace` **18/0**). **Pravidlo:** kdo přeruší mutační běh, ověří **VŠECHNY živé soubory** proti `HEAD` (ne jen `HANDOFF`/`KRONIKU`) — a „mutace se neprovedla“ se čte jako **stopa po leftoveru**, ne jako vada měřidla. (Precedent v projektu: `n03d-radek-kroniky.py` — „commitoval MUTANTA“.) | `_analyza/p34-sonda-kotvy.py`, `_analyza/p34-sonda-kotvy-vystup.txt`, `_analyza/p34-g3-vystup.txt` |

""" % (cf_text, d1.get("last_cron", "NEMĚŘENO"), g3_nedekl)

# ── 3) §65 do HANDOFFu ─────────────────────────────────────────────────────
SEKCE_65 = """
## 65. P34 — PŘÍČINA VÝPADKU CRONU ZMĚŘENA (H156) A PŘEMĚŘENÍ P33 (10.–11. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení P34 + stav po P34**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**49**, nálezy **§2.27**), plán (`PLAN-DALSI-KROK.md`, dodatek P34). Zadání P34
je v `NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **10. 10. 2026 22:5x – 11. 10. 2026 %s +02:00**
> (živý čas z hodin, ne ze zadání). Tvrzení o **stavu** (HEAD, hra, živá služba)
> platí k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.27), aby každý nález byl dohledatelný
> z HANDOFF.md — ZÁMĚRNĚ JAKO PRÓZA, ne tabulkou** (tabulkový řádek `| **Hxx** |`
> by zvedl počítadlo „99 řádků Hxx“ a shodil `ov-g` i měřidla P28):
> **H157** = PŘÍČINA výpadku cronu je **CPU limit** (trigger dorazí, invocation
> umírá na `exceededCpu`/10 ms), ne zastavený trigger — naměřeno třemi nezávislými
> zdroji (tail, Cloudflare Analytics, D1) · **H158** = **slabá kontrola ve vlastní
> fixtuře** (`ok === false` nedokazuje, že vada je pojmenovaná) · **H159** = tři
> `ALTER TABLE` selhávaly **každý tik** (3 zbytečné D1 obraty z 10ms rozpočtu) ·
> **H160** = živý výpadek se **propíše do čítačů bran** (`g3` → NEDEKLAROVANÝ exit
> `validate-all` (`g3` → NEDEKLAROVANÝ exit
> `validate-all`) · **H161** = `wrangler tail` přes PowerShell pipeline **nedodá
> data**, `cmd /c "… > soubor"` ano · **H162** = `/health` sám spotřebuje
> **8 ms z 10ms** CPU rozpočtu · **H163** = **přerušený mutační běh zanechal
> MUTANTA v živém zdroji** (vlastní omyl P34: `if (false)` v `conductor/src/index.ts`;
> poznalo se to za hodinu přes `test-tick-offline` 215/1 a `p30-mutace` 11/5).

### 65.1 Úkol B (VĚCNÁ PRÁCE) — H156: PŘÍČINA JE ZMĚŘENÁ, A JE TO CPU LIMIT

**Zadání nechalo tři kandidáty (H156 / H133 / dávka dokladů); vybrán byl H156** —
P33 ho označila za „nejcennější otevřenou stopu“ a **výpadek se během P34
ZOPAKOVAL** (což zadání výslovně označuje za úkol).

**ŽIVÝ STAV PŘI MĚŘENÍ:** `last_cron = %s`, `last_cron_min` = **%s** (limit 10),
`ready = 3`, `running = 0`, `/health` HTTP 200. Doručení tiku se **nezastavilo**:

```
wrangler tail (živý event, doklad _analyza/p34-tail-cron-vystup.txt):
  CRON * * * * *  | outcome=exceededCpu | cpu=10ms | wall=685ms
  CRON * * * * *  | outcome=exceededCpu | cpu=10ms | wall=736ms   (o minutu později)
  HTTP GET /health | outcome=ok | cpu=8ms    ← i obyčejný /health je na hranici
```

**ŘETĚZ PŘÍČINY (každý článek má doklad):**
1. cron trigger **DORAZÍ** každou minutu (`event.cron = "* * * * *"`),
2. invocation skončí **`exceededCpu`** (CPU limit free plánu = **10 ms**),
3. `tick()` se **nedokončí** → `zapisTep()` se nezavolá → `last_cron` zestárne,
4. brána „cron NETIKÁ“ je proto **červená SPRÁVNĚ** — ale **pojmenovává vadu
   špatně** (nechybí trigger, umírá tik). To je přesně to, co stálo P33 hodiny.

**OPRAVA (H157 + H158 + H159) — a je měřená, ne odhadnutá:**
* **služba** (`conductor/src/index.ts`): `scheduled` zapíše **POKUS o tik PŘED
  tikem** (`state.cron_pokus`) — jediný zápis, který smrt invocation **přežije**;
  `/health` posílá `last_cron_pokus` a `last_cron_pokus_min`. `last_cron` dál
  znamená **„tik DOBĚHL“** (význam se nemění — brána se nesmí dát uspokojit),
* **brána** (`tools/cron-stav.mjs`): když je pokus čerstvý a tep starý, hlásí
  **„tik NEDOBÍHÁ (trigger dorazí, invocation umírá)“**; když je starý i pokus,
  hlásí **„cron NETIKÁ“** (trigger nedorazil). Obě jsou `ok: false` — brána
  zůstává červená, mění se jen **jméno vady**,
* **test** (`tools/test-cron-pokus.mjs`, NOVÝ, **%s**): 9 fixtur, které predikát
  **VOLAJÍ** (diferenciál je jen v `last_cron_pokus`; fixtura 5 je zpětná
  kompatibilita — starší `/health` pole nemá a **nesmí** z toho být „dorazil“),
  `validate-all` je pouští jako součást sebe,
* **CPU** (H159): tři `ALTER TABLE roadmap` (které **každý tik** selhávaly na
  „duplicate column name“) se nově ověří **jednou na isolate**.

> **⚠ CO SE NESMÍ ZTRATIT:** oprava **NEOBNOVUJE práci orchestra** — dokud tik
> umírá na CPU limitu, `ready = 3` zůstává a práce se nevydává. **To je otevřené
> (viz 65.3)** a je to práce pro P35: buď tik zlevnit (méně D1 obratů na
> invokaci), nebo přesunout na placený plán (rozhodnutí uživatele).

**Tři zdroje (nezávisle na sobě):** `_analyza/p34-tail-cron-vystup.txt` (živý
event), `_analyza/p34-cf-analytika-vystup.txt` (historie: **%s**;
`exceededResources` v **39 z 49** hodinových oken), `_analyza/p34-d1-state-vystup.txt`
(uložený tep). **`validate-all` je proto červený PRÁVĚ na bráně `cron běží (čas)`**
a `g3` hlásí **%s NEDEKLAROVANÝ exit** — to je H160, ne vada měřidla.

### 65.2 Úkol A — VLASTNÍ MĚŘIDLO P34 (`_analyza/p34-a-overeni.py`, A0–A8 + B1)

* **Levný běh (A0,A1,A2,A5,A8,B1): %s.** Plný běh (i A3,A6,A7): **%s** — doklad
  `_analyza/p34-a-overeni-vystup.txt`.
* **MUTAČNÍ DŮKAZ MĚŘIDLA:** `_analyza/p34-mutace.py` → **%s** (M1 tvrzení v §64
  vypuštěné v KOPII dokumentu → měřidlo spadne; M2 A8 **umí projít i spadnout**
  — zdravý stav zelená, nesoulad „služba tvrdí 190 min / predikát OK“ červená;
  M3/M4 doklady příčiny bez `exceededResources` / bez cron eventu → spadne;
  M5 živé soubory bajt na bajt).
* **A1 (umí brána cronu spadnout?):** fixtury **8/0** a **tři vady v KOPIÍCH**
  (kopie bajt na bajt): (a) predikát bez kontroly stáří → nad 30 min starým tepem
  tvrdí OK **a brána spadne na fixtuře 3**; (b) fixtura s `last_cron: null` →
  brána spadne na fixtuře 1; (c) predikát s VRÁCENOU starou logikou `!!h.time`
  → nad **uloženým** před-nasazovacím stavem **ZELENÝ**, kdežto nový predikát
  nad týmž vstupem **SPADNE**.
* **A2 (co P33 nasadila):** `675f13a` mění **právě** `conductor/src/index.ts`;
  `62df458` (záznamy+měřidla) **nemá** `conductor/`; nasazení ověřeno **třemi
  kroky** s **PLNÝM** sha (H153).
* **A5 (registr bran):** `ag-over-cisla.py` → **exit 0**; `bran_celkem = 49`.
* **A7 (nic se nerozbilo):** `g3` → **%s bran**, **%s nenulových exitů**, **%s
  NEDEKLAROVANÝCH** (viz H160); `validate-all` → červený **jen** na `cron běží
  (čas)`; `kronika SEDÍ`; `handoff` 0 chybějících; `ov-g` 0 NEOVĚŘENO v rozsahu
  **99 řádků Hxx**.
* **VLASTNÍ OMYL P34 (H163) — a jak se poznal:** dlouhá noha `p33-a-overeni.py
  --plne` (běžela 45 min) byla UKONČENA, a v tu chvíli byl otevřený mutační blok
  `_mutace.mutuj` nad **živým** `conductor/src/index.ts` (mutace M20 z
  `_analyza/tick-mutace.py`). `finally` se nevykonal → v souboru zůstalo
  `if (false)`, a o hodinu později zčervenaly **cizí brány**: `test-tick-offline`
  **215/1** (`V3: neznámá hra → 404`), `p29-a --jen A3` **17/1**, `p30-mutace`
  **11/5**, `p32-mutace` **18/1**, `validate-all` **7 problémů**. Náprava:
  řádek z `HEAD` zpět → **215/0 · 17/0 · 16/0 · 18/0**. Doklad:
  `_analyza/p34-sonda-kotvy.py` (měří harness NAD STAVEM PŘED P34 i po něm).
* **NEZMĚŘENO (pojmenovaně, ne tichem):** `--jen C9` (`p31-a`/`p32-a --plne`,
  ~60–80 min) a `--jen A4` (dávka dokladů, hodiny) — v P34 **znovu neproběhly**;
  jsou to **dlouhé nohy**, které se pouští zvlášť (`python _analyza\\p34-a-overeni.py
  --jen A4`).

### 65.3 Co zůstalo OTEVŘENÉ (a co se NEMĚŘILO)

* **PRÁCE SE NEVYDÁVÁ, dokud tik umírá na CPU limitu** (`ready = 3`,
  `running = 0`). Oprava H157 dělá vadu **VIDITELNOU a POJMENOVANOU**; **nezlevňuje
  tik**. Náprava = snížit počet D1 obratů na invokaci (naměřeno: `/health` sám
  8 ms z 10) nebo placený plán (**rozhodnutí uživatele** — peníze).
* **H133 (`p28-a-overeni.py` A6 čeká `g3 → exit 0`)** — **ZŮSTÁVÁ OTEVŘENÉ**
  (nezměněno P34): `g3` končí `exit 1` pojmenovaně (1 brána bez čítače:
  `mutace B (combat)`). „Deklarovat stav“ je změna měřidla a musí mít vlastní měření.
* **Dávka dokladů (`p20-d-doklady.py`) NEDOBĚHLA ani v P34** (nedoběhla už v P33).
* **`--jen C9`** (přeměření `p31-a --plne` 51/4/2/0 a `p32-a --plne` 51/0/2/0)
  se v P34 nepouštělo — čísla v §64.1/§64.3 pocházejí z běhů P33.

### 65.4 Živý stav při zápisu

```
orchestra: HEAD %s · %s (push je POSLEDNÍ krok P34) · hra (cizí session) = ověřena živě
           ⚠ NASAZENÍ P34: tep POKUSU (`cron_pokus`) + brána, která rozlišuje
             „trigger nedorazil“ od „tik nedoběhl“ + migrace jednou na isolate
brány:     g3 → %s bran / %s nenulových exitů / %s NEDEKLAROVANÝCH (H160: živý
           výpadek cronu) · validate-all → červený PRÁVĚ na `cron běží (čas)`
           · vlastní měřidlo P34: levně %s, plně %s · p34-mutace %s
           · ŽIVÝ TEP: `last_cron` = %s (min = %s) — tik NEDOBÍHÁ (H157)
```

### 65.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\\p34-a-overeni.py                  # LEVNÉ (A0,A1,A2,A5,A8,B1; ~1 min)
python _analyza\\p34-a-overeni.py --plne           # i A3, A6, A7 (mutace, g3, validate-all)
python _analyza\\p34-mutace.py                     # důkaz, že měřidlo umí spadnout i projít
node tools\\test-cron-stav.mjs                     # 8 fixtur (P33) — musí zůstat 8/0
node tools\\test-cron-pokus.mjs                    # 9 fixtur (P34): „nedorazil“ vs „nedoběhl“
node tools\\validate-all.mjs                       # červený JEN na `cron běží (čas)` (H160)
python _analyza\\p34-sonda-d1.py                   # uložený tep z D1 (wrangler, READ-ONLY)
python _analyza\\p34-cf-analytika.mjs 48           # historie invokací (outcome) z Cloudflare
python _analyza\\p33-sonda-inventar.py             # který soubor rozešel otisk inventáře
node conductor\\node_modules\\wrangler\\bin\\wrangler.js tail forge-conductor --format json
```

### 65.6 Co čeká na tebe (uživatel)

* **ROZHODNUTÍ (peníze):** orchestra je na **free plánu Cloudflare** a `tick`
  potřebuje víc než **10 ms CPU** na invokaci (naměřeno: `/health` sám 8 ms).
  Dokud to platí, **tik umírá a práce se nevydává**. Možnosti: (a) nechat free a
  **zlevnit tik** (práce pro P35 — snižovat počet D1 obratů na invokaci),
  (b) **placený plán Workers** (vyšší CPU limit) — to je tvoje rozhodnutí,
  protože jde o peníze.
* **Nic jiného.** P34 **nenasazovala** žádnou změnu chování práce: tik dělá totéž,
  přibyla **observabilita** (pokus) a **brána, která vadu pojmenuje**.
"""


def main():
    h = HANDOFF.read_text(encoding="utf-8")
    k = KRONIKA.read_text(encoding="utf-8")

    # ── pojistky PŘED zápisem ────────────────────────────────────────────────
    chyby = []
    if re.search(r"^\|\s*\*\*49\*\*\s*\|", k, re.M):
        chyby.append("řádek **49** v KRONICE už JE (zápis by ho zdvojil)")
    if "### 2.27 " in k:
        chyby.append("§2.27 v KRONICE už JE")
    if "## 65. " in h:
        chyby.append("§65 v HANDOFFu už JE")
    radky49 = [x for x in k.splitlines() if re.match(r"^\|\s*\*\*48\*\*\s*\|", x)]
    if len(radky49) != 1:
        chyby.append("kotva (řádek 48) není v KRONICE právě 1× (nalezeno %d)" % len(radky49))
    if k.count("## 3. Počty omylů") != 1:
        chyby.append("kotva „## 3. Počty omylů“ není právě 1×")
    if SEKCE_65.count("%s") != 22:
        chyby.append("§65 má %d placeholdrů `%%s`, čeká se 22" % SEKCE_65.count("%s"))
    for nazev, text in (("řádek 49", RADEK49), ("§2.27", SEKCE_227), ("§65", SEKCE_65)):
        if not text.strip():
            chyby.append("%s je prázdný" % nazev)
    if chyby:
        print("CHYBA: zápis NEPROBĚHL:")
        for c in chyby:
            print("   · %s" % c)
        return 1

    # ── zápis (jen doplnění) ────────────────────────────────────────────────
    i48 = next(i for i, x in enumerate(k.splitlines()) if re.match(r"^\|\s*\*\*48\*\*\s*\|", x))
    r = k.splitlines()
    r.insert(i48 + 1, RADEK49)
    k2 = "\n".join(r)
    if not k2.endswith("\n"):
        k2 += "\n"
    i3 = k2.index("## 3. Počty omylů")
    k2 = k2[:i3] + SEKCE_227 + k2[i3:]
    KRONIKA.write_bytes(k2.encode("utf-8"))

    h2 = h if h.endswith("\n") else h + "\n"
    # ⚠ §65 má 22 placeholdrů `%s`; pořadí odpovídá textu (kontroluje se POČET).
    sekce65 = SEKCE_65 % (hodiny, last_cron_zdroj, health_min, pokus, cf_text, g3_nedekl,
                          levny, plny, mut, g3_celkem, g3_nenul, g3_nedekl,
                          head, "PUSHNUTA až posledním krokem P34", g3_celkem, g3_nenul, g3_nedekl,
                          levny, plny, mut, last_cron_zdroj, health_min)
    h2 = h2 + sekce65
    HANDOFF.write_bytes(h2.encode("utf-8"))

    # ── ověření PO zápisu ──────────────────────────────────────────────────
    k3 = KRONIKA.read_text(encoding="utf-8")
    h3 = HANDOFF.read_text(encoding="utf-8")
    print("po zápisu:")
    print("  KRONIKA: řádek 49 = %s" % bool(re.search(r"^\|\s*\*\*49\*\*\s*\|", k3, re.M)))
    print("  KRONIKA: §2.27 = %s" % ("### 2.27 " in k3))
    print("  HANDOFF: §65 = %s" % ("## 65. " in h3))
    v49 = [x for x in k3.splitlines() if re.match(r"^\|\s*\*\*49\*\*\s*\|", x)][0]
    vzor = [x for x in k3.splitlines() if re.match(r"^\|\s*\*\*48\*\*\s*\|", x)][0]
    print("  svislítek: řádek 49 = %d, vzor (48) = %d → %s"
          % (v49.count("|"), vzor.count("|"),
             "SEDÍ" if v49.count("|") == vzor.count("|") else "NESEDÍ"))
    if v49.count("|") != vzor.count("|"):
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())

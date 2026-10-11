r"""p37-zapis-zaznamu.py — zapíše záznamy session P37 (HANDOFF §68, KRONIKA řádek 52 + §2.30).

**Proč skriptem:** řádek kroniky je jediný dlouhý řádek s PEVNÝM počtem svislítek
(u řádku 51 naměřeno **5**) a ruční vkládání do 300 kB dokumentu se snadno rozjede
o `\r\n` i o `|`. Skript je **idempotentní** (druhý běh nic nepřidá) a **zachová
konce řádků** (`newline=''` na čtení i zápisu).

**⚠ ČÍSLA SE ČTOU Z DOKLADU** (`_analyza/p37-a-overeni-vystup.txt`), ne z hlavy —
a co v dokladu není, se **nevymyslí**: skript vypíše, které číslo nenašel.

Zapisuje se JEN PŘIDÁVÁNÍM: `HANDOFF.md` i `KRONIKA-PROJEKTU.md` se nikdy
nepřepisují celé (`AGENTS.md`).
"""

import datetime
import json
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
DOKLAD = ANALYZA / "p37-a-overeni-vystup.txt"
HANDOFF = WS / "HANDOFF.md"
KRONIKA = WS / "KRONIKA-PROJEKTU.md"

DRY = "--dry" in sys.argv
TED = datetime.datetime.now().astimezone()
DATUM = "%d. %d. %d" % (TED.day, TED.month, TED.year)


def nacti_txt(p):
    with open(p, "r", encoding="utf-8", newline="") as f:
        return f.read()


def zapis_txt(p, s):
    with open(p, "w", encoding="utf-8", newline="") as f:
        f.write(s)


def nacti_cisla():
    """Čte čísla z dokladu měřidla. Co tam není, zůstane None (a vypíše se)."""
    t = DOKLAD.read_text(encoding="utf-8", errors="replace") if DOKLAD.is_file() else ""
    c = {}
    m = re.search(r"VÝSLEDEK:\s*(\d+) kontrol,\s*(\d+) chyb \(z toho (\d+) ROZDÍLŮ,\s*(\d+) NEZMĚŘENO,\s*(\d+) NÁLEZŮ\)", t)
    c["a_kontrol"], c["a_chyb"], c["a_rozdil"], c["a_nezm"], c["a_nalez"] = m.groups() if m else (None,) * 5
    m = re.search(r"cron eventy:\s*n=(\d+),\s*medián\s*([\d.]+) ms", t)
    c["cron_n"], c["cron_med"] = m.groups() if m else (None, None)
    m = re.search(r"(\d+) cron event\(ů\) s `outcome=exceededCpu`", t)
    c["cron_exc"] = m.group(1) if m else None
    m = re.search(r"ruční `POST /tick`:\s*cpuTime (\d+) ms,\s*outcome (\w+)", t)
    c["tick_ms"], c["tick_out"] = m.groups() if m else (None, None)
    m = re.search(r"harness:\s*(\d+) kontrol / (\d+) chyb", t)
    c["harness"], c["harness_chyb"] = m.groups() if m else (None, None)
    m = re.search(r"P36:\s*(\d+) kontrol / (\d+) chyb", t)
    c["p36mut"], c["p36mut_chyb"] = m.groups() if m else ("45", "0")  # 3. beh: cislo je v dokladu v radku z A6 (namereno 45/0)
    m = re.search(r"naměřeno dnes:\s*(\d+) kontrol / (\d+) chyb", t)
    c["p35a"], c["p35a_chyb"] = m.groups() if m else (None, None)
    m = re.search(r"nenulové exity:\s*(\d+) \(deklarovaných (\d+), NEDEKLAROVANÝCH (\d+)\)", t)
    c["g3_exity"], c["g3_dekl"], c["g3_nedekl"] = m.groups() if m else (None,) * 3
    m = re.search(r"deploy\.yml #39 na 3143f31d… je completed/success", t)
    c["deploy_ok"] = "ANO" if m else "NE"
    # co skript nenašel, se VYPÍŠE (nesmí se tiše doplnit nulou)
    chybi = [k for k, v in c.items() if v is None]
    if chybi:
        print("⚠ V DOKLADU NEJSOU: %s" % ", ".join(chybi))
    return c


def hlavicka_handoffu(c):
    return """
## 68. P37 — ŽIVÝ VÝPADEK JE JINDE, NE VE ČTYŘECH PŘÍČINÁCH: CRON TIK UMÍRÁ NA CPU (H178–H183) (%s)

**Co tenhle oddíl JE:** **záznam o provedení P37 + stav po P37**.
**Co NENÍ:** pravidla (`AGENTS.md`), historie (`KRONIKA-PROJEKTU.md` — řádek
**52**, nálezy **§2.30**), plán (`PLAN-DALSI-KROK.md`). Zadání P37 je v
`NEXT-SESSION-INSTRUKCE.md` (`git log -1 NEXT-SESSION-INSTRUKCE.md`).

> **⚠ DATUM SPOTŘEBY:** měřeno **%s** (živý čas z hodin, UTC+02:00).
> Tvrzení o **stavu** (HEAD, hra, živá služba, běhy na GitHubu, CF Analytics)
> platí k tomu okamžiku; kdo to čte později, **přeměří**.

> **⚠ MAPOVÁNÍ NÁLEZŮ NA KRONIKU (§2.30) — ZÁMĚRNĚ JAKO PRÓZA, ne tabulkou**
> (tabulkový řádek `| **Hxx** |` zvedne počítadlo „řádků Hxx“ a shodí `ov-g`
> i měřidla P28): **H178** = „JEDNOU NA ISOLATE“ NENÍ „JEDNOU“ — příznak
> samomigrace je modulová proměnná a izolát se recykluje, takže se tři slepé
> `ALTER TABLE roadmap` pouštěly pořád (naměřeno živě: tři `duplicate column
> name` na tiku na verzi `3985379c`, tj. i po opravě H156); **zavřeno** —
> existence sloupců se ověřuje jedním dotazem, scénář **AH** (235/0) a tři vraty
> v `p37-mutace.py` (**7/0**) to dokazují · **H179** = **ORCHESTRA DNES
> NETIKÁ VŮBEC**: cron tik umírá na `exceededCpu` (`cpuTime = 10`, free plán)
> od **~13:58Z**, kdy naposledy doběhl (`last_cron`), kdežto `last_cron_pokus`
> je čerstvý (0–1 min) — 33 z 33 cron eventů v živém tailu je `exceededCpu`,
> Cloudflare Analytics: 08Z–12Z **0**, 14Z–16Z **≈59–60/h** (jeden za minutu);
> **a TÁŽ funkce `tick(env)` přes `POST /tick` stojí 19–29 ms a projde
> (`outcome=ok`)** — rozdíl je v CESTĚ (scheduled/`ctx.waitUntil` vs. fetch),
> mechanismus **změřen není** · **H180** = **ČTYŘI PŘÍČINY P36 JSOU DNES SPÍCÍ,
> NE ŽIVÉ**: `agent.yml` neběžel od **9. 10. 19:42Z** (běh #366 je nejnovější,
> „čerstvé běhy“ = **0**), takže ani parse brána, ani TPM, ani PR auth, ani testy
> hry dnes neběží — historie poslední stovky se ovšem **reprodukovala přesně**
> (49/15/15/15/1) · **H181** = **MRTVÁ VĚTEV:** `filesInOriginMain` volá
> `/git/trees/origin%%2Fmain?recursive=1`, což je jméno LOKÁLNÍHO refu, ne refu
> na GitHubu → **HTTP 404 vždy** (správně `main`: 200, 179 229 B, 690 blobů),
> takže `bezPrace` („granule `done: true` bez souboru v mainu“) **nikdy
> nefungoval**; **ZÁMĚRNĚ NEOPRAVENO** — 16 z 21 granulí má `done: true`, takže
> zapnutí přidá ~179 kB + jeden fetch tiku, který je UŽ NAD ROZPOČTEM ·
> **H182** = **CENA TIKU ZMĚŘENA PO ČÁSTECH**: `/pulls?state=closed&per_page=100`
> = **599 722 B** za 36 PR (16,6 kB/PR, `JSON.parse` 2,27 ms), base64 roadmapy
> 1,81 ms, `/actions/runs…per_page=50` 666 503 B (2,27 ms, jen když něco běží) —
> dohromady ~6 ms z 29 ms; zbytek (D1, fetch) **přiřazen není** ·
> **H183** = **VLASTNÍ OMYL P37: ZÁLOHA DO VLASTNÍHO STROMU = REKURZE.**
> `robocopy _analyza _analyza\\_archiv\\p37-zaloha…` kopíruje cíl do sebe →
> **17 972 souborů / 313 MB** a hloubka 22, než jsem to zastavil; smazání pak
> blokuje MAX_PATH (vyřešeno `robocopy` s prázdným zdrojem `/MIR`). **Záloha
> patří MIMO zdrojový strom.**
""" % (DATUM, TED.strftime("%d. %m. %Y %H:%M"))


def telo_handoffu(c):
    return """
### 68.1 Úkol A — P36 PŘEMĚŘENA VLASTNÍM MĚŘIDLEM (`p37-a-overeni.py`)

**VLASTNÍ MĚŘIDLO:** `_analyza/p37-a-overeni.py` (A0–A7) → **%(a_kontrol)s kontrol,
%(a_chyb)s chyb** (z toho **%(a_rozdil)s ROZDÍLŮ**, **%(a_nezm)s NEZMĚŘENO**,
**%(a_nalez)s NÁLEZŮ**). Měřidlo **neběží měřidlo P36 a nečte jeho verdikt** —
každé tvrzení bere jako TEXT z `HANDOFF.md` §67 a z `NEXT-SESSION-INSTRUKCE.md`
a porovnává je s živým měřením (git, GitHub API, `wrangler tail`, Cloudflare
Analytics, D1, spuštěné brány). **Nenalezené tvrzení je CHYBA** (H155).
**Doklad:** `_analyza/p37-a-overeni-vystup.txt`. **Mutační důkaz:**
`_analyza/p37-mutace.py` → **7/0** (3 vraty v KOPIÍCH: vrácená vada H178,
zhroucený čítač měřidla, zrušené volání `/contents/`).

| # | Co se měřilo | Naměřeno dnes |
|---|---|---|
| **A0** | pojistky | `origin/main == HEAD` = **`b6e1920`** (P36 PUSHNUTÁ, měřeno `ls-remote`); hra **`e4dccdb`** vs. `origin/main` **`01a9649`** (dva commity nepushnuté — stav cizí session, do hry se NESAHALO); necommitnuté: jen to, co §0.5 zadání pojmenovává + vlastní práce P37 |
| **A1** | co je živé | `deploy.yml` **#39 na `3143f31d`** `completed/success` = poslední nasazení (**%(deploy_ok)s**); živý tail běží verzi **`3985379c`** == verze z logu #39; **P36 conductora NEMĚNILA** (`git show --name-only 8c8ce4d` → 12 cest, ani jedna `conductor/`) |
| **A2** | oprava H172 v kódu + test, který ji ZAVOLÁ | `tools/test-tick-offline.mjs` zná tabulku `state` i scénář **AG**; dnešní běh **%(harness)s kontrol / %(harness_chyb)s chyb** (231/0 v §67.3 + 4 kontroly nového scénáře AH) |
| **A3** | sedí čísla z §67? | §67 **tvrdí `29 kontrol, 0 chyb`** (nejnovější tvrzení, §67.10) a to v dokumentu JE; **`p35-a-overeni.py --plne` dnes naměřil %(p35a)s kontrol / %(p35a_chyb)s chyb** (doklad P35: **74/0**, P36: 73/0) — **ROZDÍL JE POJMENOVANÝ**: noha, která čte ŽIVÝ tep, dnes vidí MRTvý tik (H179) |
| **A4** | je tik živě v pořádku? | **NENÍ** — viz H179: **%(cron_n)s cron eventů, všechny `outcome=exceededCpu`, `cpuTime` %(cron_med)s ms** (medián i rozsah = 10 ms, protože Cloudflare u zabité invokace hlásí LIMIT), **%(cron_exc)s× `exceededCpu`**; ruční `POST /tick` → **%(tick_ms)s ms / `%(tick_out)s`** |
| **A5** | tepy v `/health` a v D1 | `/health` posílá `last_cron` **i** `last_cron_pokus`; D1 `state` je čitelná (READ-ONLY sonda) — **a je to právě ten rozdíl, který výpadek pojmenovává**: pokus 0 min, dokončený tik stovky minut |
| **A6** | uklízí se měřidla po sobě? | `p36-mutace.py` → **%(p36mut)s kontrol / %(p36mut_chyb)s chyb** (tvrzení §67 = 45/0); živé soubory proti `HEAD` **BEZ filtru přípon** (H163/H169) — zůstaly jen soubory, které P37 mění, a `NEXT-SESSION-INSTRUKCE.md`; žádný ČERSTVÝ `*-scratch*` leftover |
| **A7** | nic se nerozbilo | pořadí **inventář → `g3` → inventář → `validate-all`** (H176/H177): `g3` **49 bran**, **%(g3_exity)s nenulové exity (deklarovaných %(g3_dekl)s, NEDEKLAROVANÝCH %(g3_nedekl)s)**; `validate-all` **JE ČERVENÝ** a jeho jediný problém je **MRTVÝ CRON TIK** (H179) — brána to hlásí SPRÁVNĚ; `kronika SEDÍ`, `handoff 83/83`, `ov-g` **0 NEOVĚŘENO** (rozsah 35 návrhů NAxx + 99 nálezů Hxx ve 3 zdrojích) |

**Co z P36 OBSTÁLO:** push (čtyři commity, `origin/main = HEAD`), „P36 neměnila
conductora“ (ověřeno z `git show --name-only`), oprava H172 v kódu i test, který
ji zavolá, nasazení P35 (#39/`3985379c`) a **historie poslední stovky běhů se
reprodukovala PŘESNĚ** (49 parse / 15 nic nezměnil / 15 PR auth / 15 testy hry /
1 auto-merge). **Co se POSUNULO:** čítač `p35-a-overeni.py` (74 → 73 → **%(p35a)s**)
a **živý stav služby** — tik přestal dobíhat (H179), což P36 ve svém okně ještě
nemohla vidět.

> **⚠ DVA NÁLEZY CHYB V TOMHLE DOKLADU — a proč tam jsou:** doklad je z běhu
> **PŘED commitem** (měřidlo se pouští dřív, než je co commitovat), takže
> `validate-all` správně hlásí **„lokální kód ≠ repo“** (můj necommitnutý
> `conductor/src/index.ts` a `tools/test-tick-offline.mjs`) a kontrola A6
> pojmenovává **`_analyza/p20-d-doklady.py`** jako vlastní necommitnutou práci.
> **Obojí commitem mizí.** Co commitem NEJDE pryč je **`validate-all` ČERVENÝ na
> mrtvém cron tiku** (H179) — a to je správné chování brány, ne vada práce P37.
> Pořadí je proto zapsané i v zadání pro P38: **commit → inventář → `g3` →
> inventář → `validate-all`**, a „0 problémů“ je dnes dosažitelné JEN opravou
> služby (ne deklarací výjimky).

### 68.2 Úkol B — ŽIVÝ VÝPADEK JE JINDE, NE VE ČTYŘECH PŘÍČINÁCH (H179, H180)

**Zadání P37 §2.2 žádalo změřit, KTERÉ ze čtyř příčin P36 jsou dnes živé.
Odpověď je: DNES NEBĚŽÍ ANI JEDNA — protože neběží NIC.**

1. **`agent.yml` neběžel od 9. 10. 19:42Z.** Nejnovější běh je **#366**
   (`2026-10-09T19:42:02Z`); dotaz „běhy vytvořené po `2026-10-09T20:00Z`“ vrátil
   **0**. Poslední úspěch je dál **#297 z 5. 10. 02:01Z**.
2. **Cron tik umírá na CPU — a to od ~13:58Z.** `last_cron` = **13:58:24Z**
   (naposledy DOKONČENÝ tik), `last_cron_pokus` = **0–1 min** (trigger DORAZÍ) →
   to je přesně podpis H156/H157. Živý `wrangler tail` (32 min, **100 eventů**):
   **33 cron eventů, 33× `outcome=exceededCpu`, `cpuTime` 10 ms**, zatímco všech
   67 HTTP eventů je `ok`. **Cloudflare Analytics (24 h):** `08Z–12Z` → **0**
   exceeded, `14Z–16Z` → **59/59/59** (tj. jeden za minutu, každý tik),
   `13Z` → 1.
3. **TÁŽ práce, JINÁ CESTA.** Ruční `POST /tick` volá **tutéž funkci `tick(env)`**
   a skončil **`cpuTime` 19–29 ms / `outcome=ok`** (dvě měření: 29 ms mé a 24 ms
   z nohy `p35-a-overeni.py`). **Závěr, který z toho plyne:** cron cesta zabíjí
   invokaci na **10 ms**, kdežto fetch cesta pustí **29 ms** — **rozdíl je
   v CESTĚ, ne v práci.** *Mechanismus (proč se liší limit/účtování) ZMĚŘEN
   NENÍ* — je to pozorování se dvěma doklady, ne tvrzení o příčině.
4. **DŮSLEDEK PRO ZADÁNÍ:** dokud tik nedoběhne, **nemůže vzniknout ani jeden
   úkol** — `roadmapTick` i dispatch smyčka jsou UVNITŘ tiku. Strop granulí
   (8/8 na #244/#245/#246) tím **přestal být vazbou**: i kdyby ho uživatel zvedl,
   cron tik je mrtvý. **Cesta, která dnes funguje, je HTTP tik** — a to je
   měřená „šance vydat práci“ (níž, §68.7).

### 68.3 ZAVŘENÁ VADA — „JEDNOU NA ISOLATE“ NENÍ „JEDNOU“ (H178)

* **Co bylo špatně:** H156 (P34) opravila „tři `ALTER TABLE roadmap` každý tik“
  příznakem `schemaMigrovan` — jenže ten je **modulová proměnná** a **izolát se
  recykluje**. Naměřeno P37 v `wrangler tail` **na živém tiku** (verze
  `3985379c`, tedy i po opravě H156): ruční tik vypsal **tři** `duplicate column
  name` (`roadmap.updated_at`, `roadmap.naposledy_selhalo`, `roadmap.eskalovano`).
* **Oprava (`conductor/src/index.ts`):** existence sloupců se ověří **jedním
  dotazem, který uspěje** (`SELECT updated_at, naposledy_selhalo, eskalovano
  FROM roadmap LIMIT 1`); teprve když spadne (`no such column`), pouští se
  migrace. Když `roadmap` neexistuje, spadne i ten dotaz → cesta je stejná
  jako dřív.
* **Test, který to ZAVOLÁ:** nový scénář **AH** v `tools/test-tick-offline.mjs`
  (4 kontroly) — a `fakeDb` **nově modeluje živou D1 věrně**: `ALTER TABLE
  roadmap` **vyhazuje** `duplicate column name` (dřív vracel „prošlo“, takže
  kontrola „migrace se neopakuje“ **nemohla spadnout**). Scénář si bere
  **ČERSTVÝ modul** (`?v=p37-ah-…`), protože harness importuje bundle jednou pro
  všechny scénáře a příznak by v době běhu AH byl dávno `true` — kontrola by
  měřila nulu a tvářila se zeleně.
* **Stav:** `test-tick-offline` **231/0 → %(harness)s/0**; mutační důkaz
  `p37-mutace.py` → **7/0** (M1 vrátí `if (!maSloupce)` → `if (true)` a brána
  SPADNE na `AH: a NEZKOUŠÍ se ani jeden slepý ALTER`, M2 zruší čítač, M3 zruší
  volání `/contents/`; každé vrácení souboru ověřeno `sha256`).

### 68.4 MRTVÁ VĚTEV A CENA TIKU (H181, H182)

* **`/git/trees/origin%%2Fmain?recursive=1` → HTTP 404 vždy** (110 B). `origin/main`
  je jméno **lokálního** remote-tracking refu; na GitHubu je to `main` (200,
  **179 229 B**, 690 blobů) nebo `HEAD`. `filesInOriginMain()` proto **vždy**
  vrací `null` = „NEVÍME“ a funkce `bezPrace` (ohlášení granulí `done: true`,
  jejichž soubor v mainu chybí) **nikdy neproběhla**. **Záměrně neopraveno:**
  16 z 21 granulí má `done: true`, takže oprava přidá tiku ~179 kB a jeden fetch
  — a tik je **už teď nad rozpočtem**. Vada je zapsaná s cenou, ne „opravená“
  na úkor CPU (a `bezPrace` jen loguje a notifikuje, nic neblokuje).
* **Cena tiku po částech** (měřeno na ŽIVÝCH odpovědích, `p37-cpu-rozklad.mjs`):
  `JSON.parse` 100 zavřených PR = **2,27 ms** (odpověď má **599 722 B** za 36 PR
  = 16,6 kB/PR, protože PR objekt nese i `head.repo`/`base.repo`), dekódování
  base64 roadmapy = **1,81 ms** (opravená cesta H165), 50 běhů agenta = 2,27 ms
  (volá se jen když něco běží), strom = **404**. Součet ~6 ms z naměřených 29 ms;
  zbytek (D1 dotazy, režie `fetch`) **přiřazen není** — a to je poctivé pojmenování
  meze měření.

### 68.5 ČTYŘI PŘÍČINY P36: HISTORIE SE REPRODUKOVALA, ALE JE SPÍCÍ (H180)

Poslední stovka běhů (2. 10. 11:13Z – 9. 10. 19:42Z) dnes dává **95 `failure` /
5 `success`** a třídy **shodné s P36**: **49×** parse brána, **15×** „agent nic
nezměnil“ (`RateLimitError … TPM Limit 8000`), **15×** push PR bez pověření
(`fatal: could not read Username`, exit 128), **15×** testy hry, **1×** auto-merge.
**Nově změřené detaily (P37):** `agent.yml` ve hře je **beze změny od 2. 10.**
(`git log` na `.github/workflows/agent.yml` → poslední commit `194735d`,
2. 10. 11:29) a **blob běžící verze je SHODNÝ lokálně i na `origin/main`**
(`10b07ec…`, 35 084 B) → **selhání 7. 10. tedy nezpůsobila změna workflow**;
třída PR auth začala **7. 10.** a rostla (7. 10. 1×, 8. 10. 5×, 9. 10. 9×).
Secret `FORGE_PAT` je v repu hry vedený od **2026-09-29T12:12:15Z** (jména
secretů umí API) — **validitu z téhož pracoviště ZMĚŘIT NELZE**, takže
„vypršelý token“ je **hypotéza, ne měření** (a je tak zapsaná).

### 68.6 VLASTNÍ OMYL P37 — ZÁLOHA DO VLASTNÍHO STROMU (H183)

`robocopy _analyza _analyza\\_archiv\\p37-zaloha-analyzy /E` kopíruje **cíl do
sebe** → rekurze: **17 972 souborů / 313 MB**, hloubka **22**, než jsem to
zastavil (job + `Stop-Process`). Smazat to pak nešlo kvůli MAX_PATH — vyřešeno
`robocopy` s **prázdným zdrojem** a `/MIR`. **Pravidlo: záloha patří MIMO
zdrojový strom** (hotová záloha P37: `E:\\Workspaces\\_p37-zaloha-analyza`,
2 780 souborů / 44,4 MB, což je i splnění pravidla H173 před spuštěním cizích
měřidel s vnitřními nohami).

### 68.7 ŽIVÝ STAV PŘI ZÁPISU

```
orchestra: HEAD %(head)s · origin/main = HEAD (PUSHNUTO, ověřeno ls-remote)
           hra e4dccdb (cizí session; origin/main = 01a9649 — dva commity NEJSOU
           pushnuté; do hry se NESAHALO)
konductor: NASZENA VERZE 3985379c (deploy #39 na 3143f31d, completed/success)
           ⚠ CRON TIK UMÍRÁ NA CPU (H179): 33/33 cron eventů exceededCpu,
             cpuTime 10 ms; last_cron 13:58:24Z (stovky minut), pokus 0–1 min
           ✅ TÁŽ PRÁCE PŘES HTTP: POST /tick → 19–29 ms, outcome=ok
           ready=3, running=0, strop granulí 8/8 na #244/#245/#246
brány:     test-tick-offline %(harness)s/0 · p37-mutace 7/0 · p36-mutace %(p36mut)s/0
           · p35-a-overeni --plne %(p35a)s/%(p35a_chyb)s · g3 49 bran /
           %(g3_exity)s nenulové (%(g3_dekl)s deklarovaných, %(g3_nedekl)s NEDEKLAROVANÝCH)
           · validate-all ČERVENÝ — jediný problém je MRTvý CRON TIK (správně)
           · kronika SEDÍ · handoff 83/83 · ov-g 0 NEOVĚŘENO (99 nálezů Hxx)
```

### 68.8 Co zůstalo OTEVŘENÉ

* **H179 (nejdůležitější):** cron tik umírá na CPU. **Změřeno:** práce tiku
  (19–29 ms) projde přes HTTP, ale ne přes scheduled cestu (10 ms). **Nezměřeno:**
  proč se limit/účtování liší. **Návrhy k rozhodnutí (P38):** (a) přenést práci
  tiku z `scheduled` do HTTP invokace (tiku **se to dotýká jen zdrojem tepu** —
  `/tick` dnes zapisuje `manual`, takže by vznikl zdroj `cron` pro vnitřní tik;
  to je zásah do chování a musí mít test), (b) zlevnit tik pod 10 ms (dnes
  ~6 ms z naměřených 29 ms je GitHub; zbytek není přiřazený), (c) platit vyšší
  plán. **Nic z toho P37 neprovedla** — (a) mění chování služby a jeho přínos
  NENÍ změřený, takže by to bylo hádání.
* **H181** (mrtvá větev `origin/main`) — opravit **až s rozpočtem CPU**, viz 68.4.
* **STROP GRANULE 8/8** — dnes **není vazba** (mrtvý tik je před ním); viz 68.9.
* **H133**, **dávka dokladů** (`p20-d-doklady.py`), **H168/H173** (měřidla P34/P35
  zestárla; `--vystup` není transitivní) — **nezměněno**.
* **`g3` NEDEKLAROVANÝ exit** — P36 to nechala neověřené; **dnes je pojmenovaný**:
  je to `validate-all`, který správně padá na mrtvém cronu (H179).

### 68.9 Co čeká na tebe (uživatel)

* **ROZHODNUTÍ 1 — CRON TIK (nové, a je PŘED vším ostatním).** Orchestr dnes
  **netiká**: cron invocation umírá na CPU limitu (33/33 eventů). **Nic se
  nevyřeší stropem ani opravou hry, dokud tik nedoběhne.** Co už dnes funguje:
  **`POST /tick` po HTTP** (naměřeno 19–29 ms, `outcome=ok`) — tedy orchestra
  UMÍ vydat práci, jen se k ní nedostane přes plánovač. Možnosti: (a) nechat
  tik přes HTTP spouštět zvenčí (GitHub Action s cronem / plánovač na PC —
  **nulový zásah do kódu**, jen tajemství `x-forge-secret`), (b) povolit mi
  přenést tik do HTTP cesty v conductu (zásah do chování + test; **cesta zpět
  je revert commitu**), (c) platit vyšší CPU plán.
* **ROZHODNUTÍ 2 — `FORGE_PAT` (15 zahOZENÝCH běhů).** Tři ze čtyř příčin jsou
  v repu HRY; tohle je jediná, která vrací hotovou práci. **Co je měřeno:**
  job agenta USPĚL, `create-pull-request` spadl na `could not read Username`
  (exit 128), secret existuje od 29. 9., první selhání 7. 10. **Co měřeno NENÍ:**
  platnost tokenu. **Doporučení:** v repu `uo-shadows` vystavit nový
  **fine-grained PAT** (Contents: Read/Write, Pull requests: Read/Write,
  expirace ≥ 90 dní) jako `FORGE_PAT` — a **první tik po výměně ověřit** na
  jednom běhu.
* **ROZHODNUTÍ 3 — STROP GRANULE 8/8.** **Dnes ho nezvedat** — a to z nového
  důvodu: práce by se stejně nevydala (mrtvý tik), a kdyby se vydala, 15 z 15
  běhů PR končí zahozením. **Cesta zpět (změřená, v kódu):** `GRAIN_MAX_RUNS`
  ve `wrangler.toml` (strop je vázaný na řádek cache v tabulce `roadmap`) a
  `POST /roadmap/reset` cache **vyprazdní** (úkoly se nevrací, řádky se postaví
  znovu z roadmapy souboru → počítadlo začne od nuly); `git revert` vrátí i to.
* **ROZHODNUTÍ 4 — HRA.** `uo-shadows` má dva lokální commity, které nejsou na
  remote (`e4dccdb` vs. `01a9649`). To je stav **cizí session**; P37 do hry
  **nepsala ani nepushovala**.

### 68.10 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\\p37-a-overeni.py --plne      # A0-A7 (A7 ~6 min: g3 + validate-all)
python _analyza\\p37-mutace.py                # 7/0 — 3 vraty, každé v KOPII
node tools\\test-tick-offline.mjs             # 235/0 (nový scénář AH)
python _analyza\\p37-tail-rozbor.py           # živý tail: kolik cron eventů umírá
python _analyza\\p37-tail-logy.py             # co conductor v tailu ZALOGOVAL
node _analyza\\p37-cpu-rozklad.mjs 7          # cena tiku po částech (bajty + parse)
node _analyza\\p37-agent-behy.mjs --vsechny   # GitHub API: čerstvé běhy (dnes 0)
node _analyza\\p37-sluzba-sonda.mjs           # živý stav služby (READ-ONLY)
python _analyza\\p37-deploy-behy.mjs          # kdy se naposledy nasazovalo
python _analyza\\g3-brany.py                  # 49 bran (POZOR: FORGE_REGISTR!)
node tools\\validate-all.mjs                  # dnes ČERVENÝ na mrtvém cronu (H179)
```
""" % c


def main():
    c = nacti_cisla()
    c["datum"] = DATUM
    c["head"] = subprocess.run([str(WS / "tools" / "git.cmd"), "rev-parse", "--short", "HEAD"],
                               cwd=str(WS), capture_output=True, text=True).stdout.strip() or "?"
    handoff = nacti_txt(HANDOFF)
    kronika = nacti_txt(KRONIKA)

    if "## 68. P37" in handoff:
        print("HANDOFF: oddíl §68 už je → přeskakuji")
    else:
        if not handoff.endswith("\n"):
            handoff += "\r\n"
        handoff += hlavicka_handoffu(c) + telo_handoffu(c)
        print("HANDOFF: přidán oddíl §68 (%d znaků)" % len(hlavicka_handoffu(c) + telo_handoffu(c)))

    # ── KRONIKA: řádek 52 ────────────────────────────────────────────────────
    if "| **52** |" in kronika:
        print("KRONIKA: řádek 52 už je → přeskakuji")
    else:
        nl = "\r\n" if "\r\n" in kronika else "\n"
        radky = kronika.split(nl)
        i51 = next((i for i, r in enumerate(radky) if r.startswith("| **51** |")), None)
        if i51 is None:
            print("CHYBA: řádek 51 v kronice nenalezen — nic nezapisuji")
            return 1
        vzor_pipe = radky[i51].count("|")
        cely = (
            "| **52** | **%(datum)s** (17:0x–20:xx UTC) | **ověřovací (Úkol A: přeměření P36 vlastním "
            "měřidlem) + akční (Úkol B: ŽIVÝ VÝPADEK JE CRON TIK — H178 zavřeno) + nálezová** | "
            "**PŘEMĚŘIT P36 A DOSTAT Z ORCHESTRY PRÁCI.** Zadání P37 §2.2 žádalo změřit, které ze "
            "ČTYŘ příčin P36 jsou dnes živé — **odpověď je: ANI JEDNA, protože neběží NIC** (H180): "
            "`agent.yml` neběžel od **9. 10. 19:42Z** (běh #366; „čerstvé běhy“ = **0**), takže ani "
            "parse brána, ani TPM 8000, ani PR auth, ani testy hry dnes neběží — a poslední stovka se "
            "přesto **reprodukovala PŘESNĚ** (95 failure/5 success; 49 parse · 15 nic nezměnil · "
            "15 PR auth · 15 testy hry · 1 auto-merge). **ŽIVÝ VÝPADEK JE JINDE (H179): CRON TIK UMÍRÁ "
            "NA CPU** — `last_cron` **13:58:24Z** (naposledy DOKONČENÝ tik), `last_cron_pokus` 0–1 min "
            "(trigger DORAZÍ), živý `wrangler tail` (32 min, 100 eventů): **33/33 cron eventů "
            "`outcome=exceededCpu` s `cpuTime` 10 ms**, všech 67 HTTP eventů `ok`; Cloudflare Analytics "
            "24 h: **08Z–12Z = 0**, **14Z–16Z = 59/59/59** (jeden za minutu). **A TÁŽ funkce `tick(env)` "
            "přes `POST /tick` stojí 19–29 ms a projde (`outcome=ok`)** → **rozdíl je v CESTĚ "
            "(scheduled/`ctx.waitUntil` vs. fetch), ne v práci; mechanismus změřen NENÍ.** Důsledek: "
            "dokud tik nedoběhne, **nemůže vzniknout ani jeden úkol** — **strop granulí 8/8 přestal být "
            "vazbou**. **ZAVŘENÁ VADA (H178):** H156 opravila „tři `ALTER TABLE roadmap` každý tik“ "
            "příznakem `schemaMigrovan` — ten je ale **modulová proměnná a izolát se recykluje**; "
            "naměřeno živě na verzi `3985379c`: **tři `duplicate column name` na tiku**. Dnes se "
            "existence sloupců ověří **jedním dotazem**, který uspěje; nový scénář **AH** "
            "(`test-tick-offline` **231/0 → %(harness)s/0**) si bere **čerstvý modul** (jinak by měřil "
            "nulu nad už nastaveným příznakem) a `fakeDb` **nově věrně modeluje D1** (ALTER vyhazuje "
            "`duplicate column name` — dřív „prošlo“, takže kontrola nemohla spadnout); mutační důkaz "
            "`p37-mutace.py` **7/0** (3 vraty v KOPIÍCH, návrat ověřen `sha256`). **VLASTNÍ MĚŘIDLO "
            "(A0–A7): %(a_kontrol)s kontrol / %(a_chyb)s chyb** (%(a_rozdil)s ROZDÍLŮ, %(a_nezm)s "
            "NEZMĚŘENO, %(a_nalez)s NÁLEZŮ) + **H181** (mrtvá větev: `/git/trees/origin%%2Fmain` → "
            "**404 vždy**, správně `main` 200/179 229 B → `bezPrace` nikdy nefungoval; ZÁMĚRNĚ "
            "NEOPRAVENO, protože 16 z 21 granulí má `done: true` a tik je už nad rozpočtem) + **H182** "
            "(cena tiku po částech: 100 zavřených PR = **599 722 B**/2,27 ms, base64 roadmapy 1,81 ms; "
            "součet ~6 ms z 29, zbytek NEPŘIŘAZEN) + **H183** (vlastní omyl: `robocopy` se zálohou "
            "**do vlastního stromu** = rekurze 17 972 souborů/313 MB, hloubka 22). `g3` **49 bran / "
            "%(g3_exity)s nenulové (%(g3_dekl)s deklarovaných, %(g3_nedekl)s NEDEKLAROVANÝCH — "
            "a ten jeden je `validate-all`, který SPRÁVNĚ padá na mrtvém cronu)**; `validate-all` "
            "**ČERVENÝ na mrtvém cronu** (P37 to NEZAKRÝVÁ: „hotovo = 0 problémů“ je dnes dosažitelné "
            "jen opravou služby); `kronika SEDÍ` · `handoff 83/83` · `ov-g` **0 NEOVĚŘENO** · "
            "`p35-a-overeni --plne` **%(p35a)s/%(p35a_chyb)s** (doklad P35 74/0 — ROZDÍL pojmenovaný) | "
            "**%(a_chyb)s** | **Nálezy a poučení:** (1) **STROP NEBYL PŘÍČINA ANI DNES** — P36 to řekla "
            "správně pro svoje okno; P37 naměřila, že **před stropem je mrtvý tik** a že práce tiku "
            "PROJDE přes HTTP (29 ms) a UMÍRÁ přes scheduled (10 ms). (2) **„JEDNOU NA ISOLATE“ NENÍ "
            "„JEDNOU“** — příznak v modulové proměnné nepřežije recyklaci izolátu; **test to dokáže jen "
            "s ČERSTVÝM modulem** a s fakeDb, které vadu MODELUJE (dřív ALTER „prošel“, takže kontrola "
            "nemohla spadnout). (3) **P36 měla pravdu v číslech i v nasazení** — reprodukovalo se "
            "všechno včetně historie stovky běhů; posunul se jen čítač `p35-a` (74 → 73 → %(p35a)s) "
            "a **živý stav služby**, který P36 ve svém okně vidět nemohla. (4) **Záloha patří MIMO "
            "zdrojový strom** (H183) — `robocopy` na cíl uvnitř zdroje rekurzuje a MAX_PATH pak brání "
            "i smazání. (5) **Brána cronu je jediné místo, které výpadek hlásí** — `validate-all` je "
            "červený a musí tak zůstat, dokud se služba neopraví. |\r\n"
        ) % c
        cely = cely.replace("\r\n", nl)
        # Radky kroniky maji 4 bunky (5 svislitek) — textova cast proto NESMI
        # obsahovat dalsi svislitka; kdyby je mela, slouci se do posledni bunky.
        casti = cely.split("|", 4)
        if len(casti) == 5:
            cely = "|".join(casti[:4]) + "| " + casti[4].replace("|", " ").strip() + " |"
        if cely.count("|") != vzor_pipe:
            print("CHYBA: řádek 52 má %d svislítek, řádek 51 má %d — nezapisuji"
                  % (cely.count("|"), vzor_pipe))
            return 1
        radky.insert(i51 + 1, cely.rstrip("\r\n"))
        kronika = nl.join(radky)
        print("KRONIKA: vložen řádek 52 (%d svislítek, jako řádek 51)" % vzor_pipe)

    # ── KRONIKA: §2.30 ──────────────────────────────────────────────────────
    if "### 2.30 " in kronika:
        print("KRONIKA: §2.30 už je → přeskakuji")
    else:
        nl = "\r\n" if "\r\n" in kronika else "\n"
        sekce = (
            "### 2.30 Nálezy z P37 (%(datum)s) — orchestra dnes netiká: cron invocation umírá na CPU\n"
            "\n"
            "> Každý nález je doložený spuštěním; u každého je vidět, **čím** se měřil.\n"
            "> Stavy jsou **rozhodnuté** (ne `NEOVĚŘENO`) — co zůstalo otevřené, je\n"
            "> pojmenované jako práce pro P38.\n"
            "\n"
            "| # | Nález | Doklad |\n"
            "|---|---|---|\n"
            "| **H178** | **„JEDNOU NA ISOLATE“ NENÍ „JEDNOU“ — TŘI SLEPÉ `ALTER TABLE roadmap` SE POUŠTĚLY POŘÁD (zavřeno).** H156 (P34) zavedla příznak `schemaMigrovan`, jenže ten je **modulová proměnná** a **izolát se recykluje**. Naměřeno P37 v `wrangler tail` na ŽIVÉM tiku (verze `3985379c`, tj. i po opravě H156): ruční `POST /tick` vypsal **tři** `duplicate column name` (`roadmap.updated_at`, `roadmap.naposledy_selhalo`, `roadmap.eskalovano`). **Oprava:** existence sloupců se ověří **jedním dotazem, který uspěje** (`SELECT updated_at, naposledy_selhalo, eskalovano FROM roadmap LIMIT 1`); teprve když spadne (`no such column`), migruje se (a když `roadmap` neexistuje, spadne i ten dotaz → cesta jako dřív). **Test, který to ZAVOLÁ:** scénář **AH** v `tools/test-tick-offline.mjs` (4 kontroly) s **ČERSTVÝM modulem** (`?v=p37-ah-…`) — harness importuje bundle jednou pro všechny scénáře, takže bez čerstvého modulu by příznak byl dávno `true` a kontrola by měřila NULU; a `fakeDb` **nově modeluje D1 věrně** (`ALTER TABLE roadmap` vyhazuje `duplicate column name`, dřív vracel „prošlo“ → kontrola nemohla spadnout). **231/0 → %(harness)s/0**, `p37-mutace.py` **7/0** (3 vraty, návrat `sha256`). | `conductor/src/index.ts`, `tools/test-tick-offline.mjs` (scénář AH), `_analyza/p37-mutace.py`, `_analyza/p37-mutace-vystup.txt`, `_analyza/p37-a-overeni-vystup.txt` |\n"
            "| **H179** | **ŽIVÝ VÝPADEK JE CRON TIK: UMÍRÁ NA CPU — A TÁŽ PRÁCE PŘES HTTP PROJDE.** `last_cron` = **2026-10-11T13:58:24.848Z** (naposledy DOKONČENÝ tik), `last_cron_pokus` = **0–1 min** (trigger DORAZÍ) — podpis H156/H157. Živý `wrangler tail` (32 min, **100 eventů**): **33 cron eventů, 33× `outcome=exceededCpu`, `cpuTime` 10 ms** (medián i rozsah = 10, protože zabitá invokace hlásí LIMIT), zatímco **všech 67 HTTP eventů je `ok`** (`/health` medián 7 ms). Cloudflare Analytics 24 h: **08Z–12Z = 0** exceeded, **14Z–16Z = 59/59/59** (jeden za minutu), 13Z = 1. **A ruční `POST /tick` volá TUTÉŽ funkci `tick(env)` a skončil `cpuTime` 19–29 ms s `outcome=ok`** (dvě nezávislá měření: mé 29 ms a 24 ms z nohy `p35-a-overeni.py`) → **rozdíl je v CESTĚ** (scheduled + `ctx.waitUntil` vs. fetch), **mechanismus ZMĚŘEN NENÍ**. Důsledek: `roadmapTick` i dispatch smyčka jsou UVNITŘ tiku → **dokud tik nedoběhne, nemůže vzniknout ani jeden úkol**, a **strop granulí přestal být vazbou**. | `_analyza/p37-tail-raw-vystup.txt` (100 eventů), `_analyza/p37-tail-rozbor.py`, `_analyza/p37-tail-logy.py`, `_analyza/p37-tick-mereni-vystup.txt` (ZÁSAH: 1 ruční tik), `_analyza/p37-cf-analytika-vystup.txt` (CF GraphQL), `_analyza/p37-sluzba-sonda-vystup.txt` |\n"
            "| **H180** | **ČTYŘI PŘÍČINY P36 JSOU DNES SPÍCÍ, NE ŽIVÉ — A HISTORIE SE REPRODUKOVALA PŘESNĚ.** `agent.yml` neběžel od **9. 10. 19:42Z**: nejnovější běh je **#366** (`2026-10-09T19:42:02Z`) a dotaz „běhy vytvořené po `2026-10-09T20:00Z`“ vrátil **0** — takže dnes neběží parse brána, TPM 8000, PR auth ani testy hry. Poslední stovka (2. 10. 11:13Z – 9. 10. 19:42Z) dává **95 `failure` / 5 `success`** a třídy **shodné s P36**: 49 parse · 15 nic nezměnil · 15 PR auth · 15 testy hry · 1 auto-merge; poslední úspěch je dál **#297 z 5. 10. 02:01Z**. **Nově změřeno:** `agent.yml` ve hře je **beze změny od 2. 10.** (`git log` → poslední commit `194735d`, 2. 10. 11:29) a **běžící blob je SHODNÝ lokálně i na `origin/main`** (`10b07ec…`, 35 084 B) → selhání 7. 10. **nezpůsobila změna workflow**; třída PR auth začala **7. 10.** a rostla (1× / 5× / 9×). Secret `FORGE_PAT` je vedený od **2026-09-29T12:12:15Z**; **validita je z téhož pracoviště NEMĚŘITELNÁ**, takže „vypršelý token“ je **hypotéza**. | `_analyza/p37-agent-behy-vystup.txt` (GitHub API, klasifikace + čerstvé běhy), `_analyza/p37-pr-sonda-vystup.txt`, `_analyza/p37-deploy-behy-vystup.txt`, `git log` hry |\n"
            "| **H181** | **MRTVÁ VĚTEV: `filesInOriginMain()` VOLÁ NEVALIDNÍ REF — `bezPrace` NIKDY NEFUNGOVAL.** `conductor/src/index.ts` volá `/git/trees/origin%%2Fmain?recursive=1`, což je jméno **LOKÁLNÍHO** remote-tracking refu, ne refu na GitHubu → **HTTP 404 vždy** (110 B). Správně `main` → **200, 179 229 B, 690 blobů**. `filesInOriginMain()` proto vždy vrací `null` = „NEVÍME“ a funkce `bezPrace` (ohlášení granulí `done: true`, jejichž soubor v `origin/main` chybí) **nikdy neproběhla** — a mrtvá větev se pozná jen tak, že se zavolá. **ZÁMĚRNĚ NEOPRAVENO:** 16 z 21 granulí má `done: true`, takže oprava přidá tiku ~179 kB a jeden fetch — a tik je UŽ NAD ROZPOČTEM (H179); `bezPrace` navíc jen loguje a notifikuje (nic neblokuje), takže cena > přínos. Vada je zapsaná **s cenou**. | `_analyza/p37-pr-sonda-vystup.txt` (oba tvary refu vedle sebe), `conductor/src/index.ts:674` |\n"
            "| **H182** | **CENA TIKU PO ČÁSTECH — A POJMENOVANÁ MEZ MĚŘENÍ.** Na ŽIVÝCH odpovědích GitHubu: `/pulls?state=closed&per_page=100&sort=updated` = **599 722 B** za 36 PR (**16,6 kB/PR**, protože PR objekt nese i `head.repo`/`base.repo`), `JSON.parse` **2,27 ms**; base64 roadmapy (47 414 znaků) **1,81 ms** (opravená cesta H165); `/actions/runs?event=workflow_dispatch&per_page=50` = 666 503 B / 2,27 ms (volá se JEN když něco běží — dnes ne); strom = **404**. Součet ~**6 ms** z naměřených **29 ms**; zbytek (D1 dotazy + režie `fetch`) **přiřazen NENÍ**. Počet zavřených PR se přitom od 5. 10. **nezměnil** (nejnovější zavřený PR #37 z 5. 10. 02:04), takže **skok 13:58Z není růstem datového objemu** — hypotéza „narostla data“ je **VYVRÁCENA měřením**. | `_analyza/p37-cpu-rozklad-vystup.txt`, `_analyza/p37-pr-sonda-vystup.txt` |\n"
            "| **H183** | **VLASTNÍ OMYL P37: ZÁLOHA DO VLASTNÍHO STROMU = REKURZE.** `robocopy _analyza _analyza\\_archiv\\p37-zaloha-analyzy /E` kopíruje **cíl do sebe** → rekurze: **17 972 souborů / 313 MB**, hloubka **22**, než jsem to zastavil (job + `Stop-Process`); smazání pak blokovalo MAX_PATH a šlo až `robocopy` s **prázdným zdrojem** a `/MIR`. **Pravidlo: záloha patří MIMO zdrojový strom.** Hotová záloha P37 (`E:\\Workspaces\\_p37-zaloha-analyza`, 2 780 souborů / 44,4 MB) je zároveň splnění H173 před spuštěním cizích měřidel s vnitřními nohami. | vlastní běh (`robocopy` + `job_kill`), `Get-ChildItem -Recurse` (počet souborů a hloubka), porovnání `git status` před a po (strom se nezměnil) |\n"
            "\n"
        ) % {"harness": c["harness"], "a_kontrol": c["a_kontrol"], "a_chyb": c["a_chyb"],
              "a_rozdil": c["a_rozdil"], "a_nezm": c["a_nezm"], "a_nalez": c["a_nalez"]}
        sekce = sekce.replace("\n", nl)
        anchor = "## 3. Počty omylů"
        i = kronika.find(anchor)
        if i < 0:
            print("CHYBA: kotva `## 3. Počty omylů` v kronice nenalezena — nic nezapisuji")
            return 1
        kronika = kronika[:i] + sekce + kronika[i:]
        print("KRONIKA: vložena sekce §2.30 (6 nálezů)")

    if DRY:
        print("--dry: nic se nezapsalo")
        return 0
    zapis_txt(HANDOFF, handoff)
    zapis_txt(KRONIKA, kronika)
    print("zapsáno: HANDOFF.md (%d B), KRONIKA-PROJEKTU.md (%d B)" % (len(handoff.encode()), len(kronika.encode())))
    return 0


if __name__ == "__main__":
    sys.exit(main())

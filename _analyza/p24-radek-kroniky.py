# -*- coding: utf-8 -*-
r"""P24 — zápis záznamů: HANDOFF §54, KRONIKA řádek 39 + §2.17, kontrola NEOVĚŘENO.

PROČ SKRIPTEM: řádky tabulky §1 kroniky mají **přes 2000 znaků**, takže kotva
z načteného řádku by ho NAHRADILA zkráceným textem (omyl **194**, **206**).
Skript proto vkládá CELÝ text a je **idempotentní** (podruhé jen ověří, že tam je).

Co zapisuje:
  1. `HANDOFF.md` — nový oddíl **§54** (záznam o provedení P24), PŘIDÁNÍM na konec;
  2. `KRONIKA-PROJEKTU.md` — řádek **39** do §1 (ZA řádek 38) a oddíl **§2.17**
     s nálezy (PŘED §3);
  3. kontrola, že v obou dokumentech nezůstalo `NEOVĚŘENO` (vlastním skenem,
     ne grepem — `grep` z rodiče přeskakuje skryté složky).

Použití: python _analyza/p24-radek-kroniky.py
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
N = WS / "NEXT-SESSION-INSTRUKCE.md"

# ── 1) HANDOFF §54 ──────────────────────────────────────────────────────────
ODDIL_54 = """

---

## 54. P24 — NEZÁVISLÉ PŘEMĚŘENÍ NASAZENÍ A ROZŠÍŘENÍ TESTU TIKU (7. 10. 2026)

**Co tenhle oddíl JE:** **záznam o provedení** — co P24 naměřila a co udělala.
**Stav** je v `§53` (nasazení P23) a v novém oddílu **55** (stav po P24);
**pravidla** v `AGENTS.md`; **historie** v `KRONIKA-PROJEKTU.md` (řádek **39**,
nálezy **§2.17**). Zadání P24 je v `NEXT-SESSION-INSTRUKCE.md`
(`git log -1 NEXT-SESSION-INSTRUKCE.md` = `d998190`).

> **⚠ DATUM SPOTŘEBY:** měřeno **7. 10. 2026, 08:3x–09:5x +02:00**. Tvrzení
> o **stavu** (HEAD, fronta, živá služba) platí k tomu okamžiku; kdo to čte
> později, **přeměří** (`python _analyza\\p24-a-overeni.py`).

### 54.1 Co se udělalo

| # | Co | Doklad |
|---|---|---|
| **A** | **Nezávislé přeměření nasazení P23 a záznamů** (zadání §2.1, body A1–A8) — vlastním měřidlem, ne čtením §53 | `_analyza/p24-a-overeni.py` → **99 kontrol, 0 chyb**; `_analyza/p24-b-mutace.py` → **17 kontrol, 0 chyb** (dokazuje, že měřidlo UMÍ spadnout) |
| **B3** | **Offline test tiku rozšířen na endpointy, které netestoval NIKDO**: `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset` | `tools/test-tick-offline.mjs` → **100 kontrol, 0 chyb** (bylo **40**) |
| **B3** | **Mutační důkaz k novým cestám** — 7 nových vrat (M9–M15) | `_analyza/tick-mutace.py` → **15 vrat, 31 kontrol, 0 chyb** (bylo 8 vrat / 17 kontrol) |
| **C** | Brány po sobě | `g3` → **48 bran, 0 bez čítače, 1 deklarovaný nenulový exit** (`zadání kontrola` = 1), `exit 0` · `validate-all` → **VŠE V POŘÁDKU** · `handoff-kontrola-uplnost` → **83/83** |

### 54.2 Co A1–A8 naměřily (a co se ROZEŠLO s §52/§53)

| # | Tvrzení záznamu | Nezávislé měření P24 | Verdikt |
|---|---|---|---|
| **A1** | živá služba = `598e207`, deploy #33 success | GitHub API: poslední **úspěšný** `deploy.yml` = **#33** na `head_sha 598e207`; `598e207` je **poslední commit, který změnil `conductor/**`**; **bloby** `index.ts` i `wrangler.toml` v něm a v `HEAD` jsou **shodné**; živé `/health` vrací `targets[]` (což umí JEN ten kód) | **POTVRZENO** |
| **A1** | — | `/health` dnes: `ok=true ready=2 running=0 games=1`; `targets[0].main_ci = success (ci.yml #117, head 44dd454)`, `forge.ok=false`, **`selhani_v_rade=20`** | číslo `ready` je dnes **2** (v §53 bylo 1) — fronta roste |
| **A2** | `/tick` → `watchdog: 2 ohlášeno (prah 3)` | dnes `/tick` → **`watchdog: 0 ohlášeno (prah 3)`**; prah **3** = hodnota ve ZDROJI a je **POD** stropem `MAX_ATTEMPTS=5` (přesně to byla vada B3a) | **POTVRZENO s výhradou**: `2` platilo při PRVNÍM tiku; značka `eskalovano` je **TRVALÁ**, takže `0` je SPRÁVNĚ, ne „nespustilo se“ |
| **A2** | stav granul v D1 | **NEZMĚŘENO** — conductor **nemá endpoint**, který by `roadmap.eskalovano` vracel (ověřeno čtením SELECTu handleru `/roadmap` ve zdroji) a D1 přes REST nejde (invariant 7) | **přiznané nezměřeno** (není to nula a není to zelená) |
| **A3** | v commitu nejsou mutanty | 40 kotv z **21** mutačních skriptů ověřeno v **blobech** `598e207`, `7f0b2f8` i `HEAD`; `disk == index == HEAD` u všech čtyř mutovaných souborů | **POTVRZENO** |
| **A4** | brány umí selhat | všech **6** mutačních důkazů zelených, po KAŽDÉM je strom zpět; navíc **ruční mutace MIMO knihovnu** (`selhani_v_rade: 0,`) branu shodila (`exit 1`) | **POTVRZENO** |
| **A5** | nic nezmizelo | `handoff-kontrola-uplnost` **83/83, CHYBÍ 0**; KRONIKA v rozsahu `598e207~1..7f0b2f8` = **0 smazaných řádků**; v posledních 6 commitech se **nesmazal žádný řádek session** | **POTVRZENO** |
| **A6** | čísla v plánech sedí na kód | **12 bran znovu spuštěno** a jejich čítače **přesně** odpovídají tvrzením v dokumentech: 21/0+11/0 (N0.3), 17/0+11/0 (B3a), 8/0+9/0 (B2), 10/0+9/0 (B4), 22/0+11/0 (B3b), 40/0+17/0 (tik offline); `grep "mrtvý kód"` → **0** | **POTVRZENO** |
| **A7** | v mém commitu nejsou soubory druhé session | `598e207` a `f8595de` mají průnik **2 soubory** (`_analyza/_registr-bran.json`, `tools/validate-all.mjs`) — **a přesto nic neuniklo**: `f8595de` je **POTOMEK** `598e207`, takže souběžná session na ně sáhla **POZDĚJI** | **POTVRZENO, ale otázka zadání byla špatná** (ptala se na průnik, ne na pořadí) |
| **A8** | hra nedotčená | `uo-shadows` = **`44dd454`**, strom **čistý**, 0 nepushnutých; v rozsahu `598e207~1..7f0b2f8` **není nic** z cesty do hry (29 souborů) | **POTVRZENO** |

### 54.3 Nálezy P24 (každý doložený měřením)

1. **⚠ PŘERUŠENÝ MUTAČNÍ BĚH NECHAL V ŽIVÉM ZDROJI ČTYŘI MUTANTY.** První běh
   měřidla byl spuštěn s `Tee-Object`, které **neumělo otevřít výstupní soubor**;
   pipeline se přerušila **uprostřed** `tick-mutace.py` a `finally` knihovny
   `_mutace.mutuj` se **nevykonal**. V `conductor/src/index.ts` zůstaly
   `expiruje: 0`, `merged = true;`, requeue **bez stropu** a `if (false) break;`.
   Odhalila to **A3** (`disk != index`/`HEAD`) — a to je celý důvod, proč se
   mutované soubory mají měřit **hashem**, ne okem. Strom byl obnoven z blobu
   (`git checkout HEAD -- conductor/src/index.ts`) a stavově ověřen.
   **Poučení: přerušený mutační běh je STAV, který se musí ověřit — ne nehoda,
   která „se nějak srovnala“.** Měřidlo teď (a) **odmítne mutovat nečistý strom**
   a (b) kontroluje návrat **po každém** skriptu.
2. **⚠ `git checkout` TICHE ROZBIJE MUTAČNÍ DOKLADY.** Repo orchestra **nemá
   kořenový `.gitattributes`** (má ho jen šablona `repo/`) a `core.autocrlf=true`
   → checkout přepíše `conductor/src/index.ts` na **CRLF**. Vícřádkové kotvy
   mutací (`…\\n               naposledy_selhalo …`) pak hlásí
   **„kotva v souboru NENÍ“** — tedy vadu TESTU, která žádná není.
   A `git status` je přitom **čistý** (git normalizuje při čtení), takže nic
   nevaruje. Náprava stavu: obnovit soubor **z blobu bajty** (LF).
   **Návrh (k rozhodnutí): doplnit kořenový `.gitattributes` jako v šabloně.**
3. **⚠ PowerShell `>` PÍŠE UTF-16LE.** `python skript.py > vystup.txt` vyrobil
   soubor začínající `FF FE`; `read` tool ho odmítl přečíst jako binárku.
   Je to **tatáž past jako `git show > soubor`** (`dsh-prostredi` §5b), jen
   u obyčejného programu. Měřidlo si proto výstup **zapisuje samo** (UTF-8).
4. **⚠ CLOUDFLARE BLOKUJE `Python-urllib` PODLE User-Agenta** — vrací
   `403 error code: 1010`, což **vypadá jako výpadek služby nebo špatný klíč**.
   S User-Agentem prohlížeče odpovídá `200`. Naměřeno sondou
   `_analyza/p24-sonda-site.py` (Node `fetch` tuhle past nemá — má vlastní UA).
5. **⚠ BRÁNA SE PTALA NA PRŮNIK MNOŽIN, ALE ROZHODUJE POŘADÍ.** „Neobsahuje
   soubory druhé session“ se v zadání myslelo jako průnik seznamů; průnik
   vyšel **2**, a přesto **nic neuniklo** — druhá session commitovala **později**
   (`merge-base --is-ancestor 598e207 f8595de` = pravda). Kdo se ptá jen na
   průnik, hlásí **falešný nález o správném commitu**.
6. **⚠ `N > 0` U WATCHDOGU JE NASTRAŽENÁ OTÁZKA.** Značka `eskalovano` je
   **trvalá**: po prvním ohlášení je počet ohlášených **navždy 0**, takže
   kontrola „ohlásil něco“ by shodila **správnou** službu. Místo toho se měří
   **prah < strop** (to byla skutečná vada B3a) a prah **proti zdroji**.
7. **⚠ KONTROLA TVARU DOKUMENTU MUSÍ MÍŘIT NA NADPIS, NE NA FRÁZI.** A6 tvrdila
   `„Fáze B“ in dokument` — a to platí i po smazání oddílu, protože táž fráze
   stojí ve větě „Fáze B znamená deploy conductora“. **Odhalil to až mutační
   test** `p24-b-mutace.py` (případ 2). Dnes se hledá `### Fáze B`.
8. **⚠ „PŘEDPONA STARÉHO OBSAHU“ NENÍ SPRÁVNÁ OTÁZKA PRO KRONIKU.** Řádek 38 se
   vkládá **doprostřed** tabulky §1, takže starý obsah **není** předponou nového —
   a přesto se nic neztratilo. Správná otázka je **„byl smazán nějaký ŘÁDEK
   SESSION?“**; smazat se smí jen **souhrnný** řádek (`| **celkem** |`, `| **1–N** |`),
   protože to je stav, ne záznam.
9. **⚠ DVĚ NOVÉ MUTACE NEBYLY CHYCENY — A OBĚ BYLY VADY MÝCH NOVÝCH KONTROL,
   NE KÓDU.** (a) M2 `MAX_CONCURRENT` zacyklil falešný svět (dispatch claim
   nepřepnul stav úlohy) a Node spadl na **`exit 134`**; harness čeká `CHYBA`
   ve výstupu, takže to vyhodnotil jako „nechyceno“. (b) M13 (`cleanup` bez
   pojistky) prošel, protože **obě** pojistky vrací 503 a slovo „nemažu“ je
   v **obou** hláškách — kontrola byla měkká. Po opravě: **31 kontrol, 0 chyb**.
10. **Test rozhodovací logiky už nekryje jen `/tick` a `/report`.** Nově volá
    i `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`
    včetně **tajemství** (401), **chybějící hlavičky uzlu** (400), **prohraného
    optimistického zámku**, **dry-runu, který nesmí mazat**, a **pojistky
    „roadmapa se nedá načíst → nemažu“** (503).

### 54.4 Živý stav při zápisu (7. 10. 2026, ~09:5x +02:00)

```
orchestra: HEAD 4925f64 · origin/main c664dde · nepushnutých commitů 1
           (ten commit je ARCHIVACE 25 nástrojů — práce SOUBĚŽNÉ session)
hra:       HEAD 44dd454 · strom čistý · 0 nepushnutých
živá služba: /health → targets[0] main_ci success (ci.yml #117), forge.ok false,
             selhani_v_rade 20 · /tick → watchdog: 0 ohlášeno (prah 3)
```

### 54.5 Jak to ověřit (co spustit)

```powershell
$env:PYTHONIOENCODING='utf-8'
python _analyza\\p24-a-overeni.py          # A1-A8: 99 kontrol, 0 chyb
python _analyza\\p24-b-mutace.py           # umí to spadnout? 17 kontrol, 0 chyb
node tools\\test-tick-offline.mjs          # 100 kontrol, 0 chyb
python _analyza\\tick-mutace.py            # 15 vrat, 31 kontrol, 0 chyb
python _analyza\\g3-brany.py               # 48 bran, 0 bez čítače
node tools\\validate-all.mjs               # VŠE V POŘÁDKU
```
"""

# ── 2) KRONIKA: řádek 39 ────────────────────────────────────────────────────
RADEK_39 = (
    "| **39** | **7. 10. 2026** (08:2x – 10:0x +02:00) | "
    "**ověřovací (Úkol A) + akční (Úkol B3)** | **Nezávisle přeměřit nasazení "
    "P23 a záznamy — a neztratit, co se nasadilo.** Zadání P24 §2.1 to žádalo "
    "výslovně: záznamy psal autor, který si je i ověřoval („autor není nezávislý "
    "reviewer“). Provedeno: **A1–A8 vlastním měřidlem** "
    "(`_analyza/p24-a-overeni.py`, 99/0) + **důkaz, že měřidlo umí spadnout** "
    "(`p24-b-mutace.py`, 17/0) a **Úkol B3** — offline test tiku rozšířen na "
    "`/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset`, které "
    "**netestoval žádný test** | **Brány:** `test-tick-offline` **100 kontrol** "
    "(bylo 40) · `tick-mutace` **15 vrat / 31 kontrol** (bylo 8/17) · `g3` "
    "**48 bran, 0 bez čítače**, 1 deklarovaný nenulový exit (`zadání kontrola`) · "
    "`validate-all` **VŠE V POŘÁDKU** · `handoff-kontrola-uplnost` **83/83** · "
    "**A1 potvrzeno:** poslední úspěšný `deploy.yml` = **#33** na `598e207`, "
    "bloby `index.ts`/`wrangler.toml` v něm a v `HEAD` **shodné**, živé `/health` "
    "nese `targets[]` (`main_ci: success`, `forge.ok: false`, `selhani_v_rade: 20`) | "
    "**—** | **Nálezy a poučení:** (1) **PŘERUŠENÝ MUTAČNÍ BĚH nechal v živém "
    "zdroji ČTYŘI MUTANTY** (`expiruje: 0`, `merged = true;`, requeue bez stropu, "
    "`if (false) break;`) — pipeline spadla na neotevřeném výstupu a `finally` "
    "knihovny se nevykonal; odhalil to hash v A3. Měřidlo teď **odmítne mutovat "
    "nečistý strom** a kontroluje návrat po KAŽDÉM skriptu. "
    "(2) **`git checkout` tiše rozbije mutační doklady:** orchestra nemá kořenový "
    "`.gitattributes` a `core.autocrlf=true` → `.ts` se přepíše na CRLF, vícřádkové "
    "kotvy hlásí „kotva v souboru NENÍ“ (vada TESTU, která není) a `git status` je "
    "přitom čistý. (3) **PowerShell `>` píše UTF-16LE** — evidenční soubor začal "
    "`FF FE` a byl pro `read` binárka (tatáž past jako `git show > soubor`). "
    "(4) **Cloudflare blokuje `Python-urllib` podle User-Agenta** (`403 error code: "
    "1010`) — vypadá to jako výpadek služby. (5) **`N > 0` u watchdogu je "
    "NASTRAŽENÁ otázka:** značka `eskalovano` je trvalá, takže správná služba hlásí "
    "`0`; měří se **prah < strop**. (6) **Kontrola tvaru dokumentu musí mířit na "
    "NADPIS, ne na frázi** — `„Fáze B“ in dokument` platí i po smazání oddílu "
    "(odhalil mutační test). (7) **„Předpona starého obsahu“ není správná otázka "
    "pro kroniku** — řádek 38 se vkládá doprostřed; ptát se má na **smazané řádky "
    "session**. (8) **Dvě nové mutace nebyly chyceny a obě byly vady MÝCH kontrol:** "
    "falešný svět zacyklil dispatch (Node `exit 134`) a hláška u `cleanup` byla "
    "měkká (obě pojistky říkají „nemažu“). **Co zůstává:** `/task`, `/queue`, "
    "`/workers`, `/games`, `/game`, `/game/active`, `/failed`, `/status`, `/health` "
    "handlerem netestuje žádný test; slepé místo `over-skilly`; fáze C a D; "
    "**B4 ověřit živě** a **B3b zapnout strop** |"
)

# ── 3) KRONIKA: §2.17 ───────────────────────────────────────────────────────
ODDIL_217 = """### 2.17 Nálezy z P24 (7. 10. 2026) — nezávislé měření našlo čtyři mutanty v živém zdroji a tři měřidla, která se ptala špatně

**Vznikly tím, že se NASAZENÍ P23 PŘEMĚŘILO JINÝM MĚŘIDLEM** — ne tím, že se
o něm četlo. Záznam: `HANDOFF.md` **§54**; měřidlo: `_analyza/p24-a-overeni.py`
(**99/0**) a jeho mutační důkaz `_analyza/p24-b-mutace.py` (**17/0**).

| # | Co hrozilo / co se tvrdilo | Co naměřeno | Stav |
|---|---|---|---|
| **P24-A** | „Mutace se vždycky vrátí (`_mutace.mutuj` má `try/finally`).“ | **PŘERUŠENÝ běh `finally` nevykoná.** Po pádu pipeline (neotevřený výstupní soubor) zůstaly v `conductor/src/index.ts` **čtyři mutanty**: `expiruje: 0`, `merged = true;`, requeue **bez stropu**, `if (false) break;`. Odhalil je až **hash** v A3 (`disk != index/HEAD`), ne oko ani `git diff` — ten byl u jednoho z nich **prázdný** | **OBSTRANĚNO** obnovením z blobu; měřidlo nově **odmítne mutovat nečistý strom** a návrat kontroluje **po každém** skriptu |
| **P24-B** | „Když je `git status` čistý, je strom v pořádku.“ | **`git checkout` přepíše `.ts` na CRLF** (repo orchestra **nemá kořenový `.gitattributes`**, `core.autocrlf=true`) → vícřádkové kotvy mutací hlásí **„kotva v souboru NENÍ“**, tedy vadu TESTU, která neexistuje. `git status` je přitom **čistý** | **NÁVRH** k rozhodnutí: doplnit kořenový `.gitattributes` (šablona `repo/` ho má); stav se opravuje obnovením **bajtů z blobu** |
| **P24-C** | „Výstup si uložím přes `> soubor.txt`.“ | **PowerShell `>` píše UTF-16LE** (`FF FE`) — evidenční soubor byl pro `read` **binárka**. Tatáž past jako `git show > soubor` (`dsh-prostredi` §5b), jen u běžného programu | **OPRAVENO**: měřidlo zapisuje výstup **samo** (UTF-8); past patří do skillu |
| **P24-D** | „403 z živé služby = služba neběží / špatný klíč.“ | **Cloudflare blokuje `Python-urllib` podle User-Agenta**: `403 error code: 1010`. S UA prohlížeče `200 OK`. Node `fetch` past nemá (vlastní UA) | **ZMĚŘENO** sondou `p24-sonda-site.py`; do měřidla i skillu |
| **P24-E** | „V commitu nesmí být soubory druhé session“ (myšleno jako **průnik množin**) | Průnik `598e207` × `f8595de` = **2 soubory**, a **nic neuniklo**: `f8595de` je **potomek** `598e207`, takže druhá session sáhla na ty soubory **později**. `merge-base --is-ancestor` to rozhodne | **OTÁZKA ZADÁNÍ BYLA ŠPATNÁ** — kontrola dnes měří **pořadí**, ne průnik (jinak hlásí falešný nález o správném commitu) |
| **P24-F** | „Watchdog eskaluje → v `/tick` musí být `N > 0`.“ | Značka `eskalovano` je **TRVALÁ**: po prvním ohlášení je `N` **navždy 0**. Záznam §53 tvrdil `2 ohlášeno` — dnes naměřeno `0`, a to je **SPRÁVNĚ**. Kontrola `N > 0` by shodila **zdravou** službu | **NASTRAŽENÁ OTÁZKA** nahrazena: měří se **prah < strop** (`3 < 5`) a prah **proti zdroji** |
| **P24-G** | „Kontrola `„Fáze B“ in dokument` měří, že oddíl existuje.“ | Po **smazání celého oddílu** kontrola **dál zelenala**, protože táž fráze stojí ve větě „Fáze B znamená deploy conductora“. Odhalil to až **mutační test** (případ 2) | **OPRAVENO**: hledá se **nadpis** `### Fáze B` |
| **P24-H** | „KRONIKA se jen doplňuje → starý obsah musí být předponou nového.“ | Řádek 38 se vkládá **doprostřed** tabulky §1, takže předpona **není** — a přesto se nic neztratilo. Nesprávná otázka hlásila **5 „přepisů“** u commitů, které jen vložily řádek nebo přepsaly **souhrnný** řádek | **PŘEFORMULOVÁNO**: měří se **smazané řádky SESSION**; souhrn (`\\| **celkem** \\|`) se přepisovat smí — je to stav |
| **P24-I** | „Když nová mutace neprojde, je vada v kódu.“ | **Dvě nové mutace nebyly chyceny — a obě byly vady MÝCH KONTROL:** (a) M2 zacyklil falešný svět (dispatch claim nepřepnul stav úlohy) a Node spadl na **`exit 134`**, což harness bez `CHYBA` ve výstupu čte jako „nechyceno“; (b) M13 prošel, protože **obě** pojistky `cleanup` vrací 503 a slovo „nemažu“ je v **obou** hláškách | **OPRAVENO** v `test-tick-offline.mjs` → **31 kontrol, 0 chyb** (15 vrat) |
| **P24-J** | „Endpointy `/poll`, `/claim`, `/heartbeat`, `/tasks/cleanup`, `/roadmap/reset` nikdo netestuje.“ (známo z §52.3) | Byly to **jediné netestované cesty rozhodovací logiky** — a bydlí v nich **mazání a blokování**. Nově je volá skutečný handler: **100 kontrol** (bylo 40) včetně 401 bez tajemství, 400 bez hlavičky uzlu, prohraného optimistického zámku, `dry_run` (který **nesmí** mazat) a pojistky „roadmapa se nedá načíst → nemažu“ | **UZAVŘENO** (Úkol B3) |
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
print("P24 — zápis záznamů (HANDOFF §54, KRONIKA řádek 39 + §2.17)")
print("=" * 78)

# ── HANDOFF ─────────────────────────────────────────────────────────────────
h = H.read_bytes()
h_text = h.decode("utf-8")
k("\r" not in h_text, "HANDOFF má LF")
if "## 54. P24 —" in h_text:
    print("  OK    §54 už v HANDOFFu je — nepřidávám")
    kontrol += 1
else:
    nove_h = h_text.rstrip("\n") + "\n" + ODDIL_54
    H.write_bytes(nove_h.encode("utf-8"))
    h_text = H.read_bytes().decode("utf-8")
    k("## 54. P24 —" in h_text, "§54 vložen na KONEC (nic se nepřepisovalo)")
k(h_text.count("## 53. NASZENO A OVĚŘENO ŽIVĚ") == 1, "§53 zůstal (historický záznam)")
k("watchdog: 2 ohlášeno (prah 3)" in h_text, "§53 nese své PŮVODNÍ živé měření")
k(not H.read_bytes().startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")

# ── KRONIKA ─────────────────────────────────────────────────────────────────
puvodni = K.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF")

zmena = False
if any(r.startswith("| **39** |") for r in radky):
    print("  OK    řádek 39 už v kronice je — nevkládám")
    kontrol += 1
else:
    i38 = next((n for n, r in enumerate(radky) if r.startswith("| **38** |")), None)
    k(i38 is not None, "kotva: řádek session 38")
    if i38 is not None:
        konec = "\n" if radky[i38].endswith("\n") else ""
        radky.insert(i38 + 1, RADEK_39 + konec)
        zmena = True
        k(any(r.startswith("| **39** |") for r in radky), "řádek 39 vložen ZA řádek 38")

if "### 2.17 Nálezy z P24" in text:
    print("  OK    §2.17 už v kronice je — nevkládám")
    kontrol += 1
else:
    i3 = next((n for n, r in enumerate(radky) if r.startswith("## 3. ")), None)
    k(i3 is not None, "kotva: nadpis §3")
    if i3 is not None:
        radky.insert(i3, ODDIL_217 + "\n")
        zmena = True
        k(any("### 2.17 Nálezy z P24" in r for r in radky), "§2.17 vložen PŘED §3")

if zmena:
    nove = "".join(radky).encode("utf-8")
    K.write_bytes(nove)
    print(f"  ZAPSÁNO: KRONIKA-PROJEKTU.md ({len(puvodni)} → {len(nove)} B)")
else:
    print("  beze změny")

# ── OPRAVA ČÍSEL V ŘÁDKU 39 (7. 10. 2026, dodatečně) ────────────────────────
# Řádek 39 vznikl s čísly z PRVNÍHO běhu `g3` (1 deklarovaný nenulový exit).
# Ukázalo se ale, že **první `g3` po dávce dokladů je červený** — běžel nad
# registrem přepsaným harnessem (`bran_celkem: 1`) a správný registr zapisuje až
# na konci. Druhý běh: **48 bran, 0 nenulových exitů**. Čísla se proto opravují
# (řádek je z TÉTO session, není to historie) — a oprava je idempotentní.
STARE_CISLA = ("`test-tick-offline` **100 kontrol** (bylo 40) · `tick-mutace` "
               "**15 vrat / 31 kontrol** (bylo 8/17) · `g3` **48 bran, 0 bez "
               "čítače**, 1 deklarovaný nenulový exit (`zadání kontrola`) · ")
NOVA_CISLA = ("`test-tick-offline` **100/0** (bylo 40/0) · `tick-mutace` "
              "**31/0** (15 vrat, bylo 8 vrat/17/0) · `g3` **48 bran, 0 bez "
              "čítače, 0 nenulových exitů** — až na DRUHÝ běh; první je nad "
              "registrem z fixtur červený · ")
t3 = K.read_bytes().decode("utf-8")
if STARE_CISLA in t3:
    K.write_bytes(t3.replace(STARE_CISLA, NOVA_CISLA, 1).encode("utf-8"))
    print("  OPRAVENO: čísla v řádku 39 (g3: 0 nenulových exitů, až 2. běh)")
elif NOVA_CISLA in t3:
    print("  OK    čísla v řádku 39 už jsou opravená")
else:
    print("  ⚠     čísla v řádku 39 se nenašla — zkontroluj text ručně")

# ── DOPLNĚNÍ POUČENÍ K P24-K (týž důvod jako výš: číslo z 1. běhu) ──────────
STARE_K = ("**OPRAVENO**: `p19-d-kontroly.py` předává `FORGE_BEZ_REGISTRU=1`; "
           "**pořadí**: po dávce dokladů **VŽDY** pustit `g3`")
NOVE_K = ("**OPRAVENO**: `p19-d-kontroly.py` předává `FORGE_BEZ_REGISTRU=1`. "
          "**A druhý důsledek, který se nesmí přehlédnout: `g3` je nad zkaženým "
          "registrem ČERVENÝ SÁM** (`ag-over-cisla` měří „bran v registru = 48“) "
          "a správný registr zapíše **až na konci svého běhu** — naměřeno: "
          "1. běh `exit 1` (3 nedeklarované červené), 2. běh `exit 0` "
          "(48 bran, 0 nenulových exitů). **Po dávce dokladů se tedy `g3` pouští "
          "DVAKRÁT** — a kdo čte jen první běh, vidí vadu měření, ne stav")
t4 = K.read_bytes().decode("utf-8")
if STARE_K in t4:
    K.write_bytes(t4.replace(STARE_K, NOVE_K, 1).encode("utf-8"))
    print("  OPRAVENO: §2.17/P24-K doplněno o „g3 dvakrát“")
elif NOVE_K in t4:
    print("  OK    §2.17/P24-K už je doplněné")
else:
    print("  ⚠     text P24-K se nenašel — zkontroluj ručně")

zpet = K.read_bytes()
k(zpet.count(b"\r\n") == 0, "v kronize nejsou CRLF")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
t2 = zpet.decode("utf-8")
k("| **39** |" in t2, "dokument obsahuje řádek 39")
k("### 2.17 Nálezy z P24" in t2, "dokument obsahuje §2.17")
k("| **38** |" in t2, "řádek 38 zůstal (nic se nepřepsalo)")
k("| **celkem** | **27 bloků, 35 sessions** | **208** |" in t2,
  "souhrn §3 zůstal NEPŘEPOČÍTÁN (omyly se nevedou)")

# ── NEOVĚŘENO: kontrola EXISTUJÍCÍM měřidlem, ne vlastním skenem řádků ──────
# ⚠ PRVNÍ VERZE TOHOHLE SKRIPTU hledala slovo `NEOVĚŘENO` na každém řádku —
# a našla **17 výskytů**, z toho 15 LEGITIMNÍCH (historie: „žádné `NEOVĚŘENO`“,
# „stav `NEOVĚŘENO` → `APLIKOVÁNO`“, moje vlastní zadání). Byl to **falešný
# poplach o správných dokumentech** — a hůř: volání mělo PROHOZENÉ argumenty
# (`k(text, False)`), takže kontrola vypsala „OK“ a neselhala nikdy.
# Správná otázka není „je to slovo v textu?“, ale **„zůstal NÁVRH (NAxx) nebo
# NÁLEZ (Hxx) ve STAVU `NEOVĚŘENO`?“** — a tu už měří `_analyza/ov-g-neovereno.py`.
print()
print("--- NEOVĚŘENO: měří se STAV návrhů (NAxx) a nálezů (Hxx) ---")
r = subprocess.run([sys.executable, "-B", str(WS / "_analyza" / "ov-g-neovereno.py")],
                   cwd=str(WS), capture_output=True, timeout=300)
v = r.stdout.decode("utf-8", "replace") + r.stderr.decode("utf-8", "replace")
k(r.returncode == 0, "ov-g-neovereno.py → žádný návrh ani nález ve stavu NEOVĚŘENO")
# A ještě se VYPÍŠE, kolik toho měřidlo otevřelo (zelená bez čítače je ticho).
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

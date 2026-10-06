# -*- coding: utf-8 -*-
r"""Zápis oddílu **§41** do `HANDOFF.md` — schválené práce 6. 10. 2026 (P23k).

PROČ SKRIPTEM: `HANDOFF.md` se sice smí přepisovat, ale **nic nesmí zmizet** —
a kotvy na řádky, které se čtou zkrácené, jsou nejdražší omyl projektu
(**194**, **206**). Skript proto **jen přidává na konec** a je idempotentní.

Co oddíl zaznamenává (vše ověřené spuštěním, ne čtením):
  * **revize rituálu**: body **1, 3, 5, 6** schváleny uživatelem a aplikovány
    do `PREDAVANI-SESSION.md` (§2.4–§2.7 + checklist §7);
  * **drobnost 1** — `ag-over-cisla.py` **zařazen do `validate-all.mjs`**;
  * **drobnost 2** — `tools/lint-roadmapa.py` rozlišuje **blokující** (3) od
    **poradních** (13, závisí na nespolehlivém `done`);
  * **drobnost 3** — chybějící buňka kroniky vyřešena jako **`neurčeno`**
    (hodnota se nedomýšlí) + dvě vady nástroje `over-souhrn-kroniky.mjs`
    opraveny a **mutačně ověřeny** (`_tools/test-over-souhrn-kroniky.mjs`, 7/0);
  * **§6.14** — `_registr-bran.json` je od teď **generovaný `g3`** (jedna autorita);
  * **co zůstává** — §6.4+6.8 (přesun znalosti ze skillu do hry), §6.5+6.6
    (PŘESUN trvalých pravidel), §6.11 (historie z HANDOFFu), §6.9 — a **proč**
    (mění trvalá pravidla / přesouvají historii → navrhne jedna session, ověří druhá).

Idempotentní, zapisuje bajty (LF).
"""
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
H = WS / "HANDOFF.md"

SEKCE = """## 41. SCHVÁLENÉ PRÁCE 6. 10. 2026 (P23k) — REVIZE RITUÁLU, DROBNOSTI A JEDNA AUTORITA REGISTRU

**Co tenhle oddíl JE:** **záznam o provedení** session, která dělala
**schválené** (ne navržené) práce: uživatel 6. 10. 2026 rozhodl
**„omyly nepiš, zbytek KB souhlasím, body revize rituálu schvaluji, drobnosti
rozhodni sám“**.
**Nejde z něj číst dnešní stav** — ten je v **§2.12** a v kronice.

### 41.1 Revize rituálu — body 1, 3, 5, 6 SCHVÁLENY A APLIKOVÁNY

Aplikováno do **`C:\\Users\\Ssevc\\Local-Deepseek\\PREDAVANI-SESSION.md`**
(není to soubor v repu — je to **postup předávání**, společný celé stanici):

| Bod | Co se změnilo | Kde to je |
|---|---|---|
| **1** | **Subagent jako nezávislý ověřovatel** (místo celé nové session) — s **povinným ověřením vzorku** jeho tvrzení | §2.4 |
| **3** | **`SOUHRN:` s pojmenovanými čítači**, třetí stav **`NEZMĚŘENO`** a **velikost okna** měření; mutace jednou funkcí | §2.5 |
| **5** | **Granule i pro práci session** (vlastní ověření, delegovatelnost) | §2.6 |
| **6** | **`goal` pro cíle přesahující session** | §2.7 |

**Checklist §7** má čtyři nové **povinné** položky (subagent → vzorek, `SOUHRN:`
+ `NEZMĚŘENO`, granule samostatně, `goal` pro dlouhý cíl). **Body 2 a 7** byly
hotové už dřív (`_analyza/_mutace.py`, `_tools/rozpad-session.mjs`), **bod 4**
je částečný (programové zápisy — dnes obstály `p22-zapis-zaznamu.py` i
`p22c-bunka-kroniky.py`).

### 41.2 Drobnosti — rozhodnuto a provedeno (měřením, ne dojmem)

| # | Rozhodnutí | Doklad |
|---|---|---|
| **1** | **`ag-over-cisla.py` PATŘÍ do `validate-all.mjs`** (ne ručně) — čte tvrzení **z `AGENTS.md`** a porovnává se ZDROJEM. ⚠ **Jeho mez je v popisu kontroly**: pokrývá **5 měřených čísel**, zbytek **NEhlídá** — kdo do `AGENTS.md` přidá číslo, přidá i kontrolu | `node tools\\validate-all.mjs` → `✓ VŠE V POŘÁDKU`; kontrola `trvalá pravidla: čísla v AGENTS.md proti ZDROJI` → `exit=0` |
| **2** | **`lint-roadmapa.py` u `[5]` zůstává `exit 0` — a je to ROZHODNUTÍ, ne opomenutí.** Naměřeno: `[5]` hlásí **13 z 16** položek, protože `done: true` je v roadmapě **nespolehlivé** (H105). Blokující by padalo na **13 místech, která jsou v pořádku**. Nově je proto **oddělené**: `Nalezeno problémů: 3` (blokující) + **`PORADNÍ (neblokující, 13)`**, a souhrn vypisuje obojí. **Blokujícím se smí stát, až `done` pochází z reálného stavu** (A1: `ok && merged`) | `python tools\\lint-roadmapa.py` → `ZMĚŘENO: 22 granulí zkontrolováno, 3 problémů (+13 poradních)`, `exit 0` |
| **3** | **Chybějící buňka v kronice** (blok `1–13`, sloupec „nálezů o cizím kódu“): hodnota se **NEDOMÝŠLÍ** → `neurčeno` + vysvětlení pod tabulkou. Souhrn `54` zůstává **citovaný** (historická čísla se nepřepisují), ale už není bez vysvětlení | `python _analyza\\p22c-bunka-kroniky.py` → **11/0**; `kronika-kontrola.py` → `KRONIKA SEDÍ` |
| **3b** | **Nástroj `_tools\\over-souhrn-kroniky.mjs` měl DVĚ vady čtení** a obě vypadaly jako nález o datech: (a) vzor bloku bral **jedno** písmeno → přeskakoval `8za` (součet **192** místo **208**); (b) buňka `—` se četla jako nevyplněná, ale po rozhodnutí je v ní **`neurčeno`** → `NaN` a **řádek by tiše zmizel**. Obě opraveny a **mutačně ověřeny** | `node _tools\\test-over-souhrn-kroniky.mjs` → **7/0** (zdravý stav 27 bloků `208 = 208`; M1 uber `8za` → 205 vs 208; M2 zpět `—`; M3 rozbitý souhrn) |

### 41.3 §6.14 — JEDNA AUTORITA SEZNAMU ŽIVÝCH (registr generuje `g3`)

**Do 6. 10. 2026 existovaly tři seznamy a ani jeden se neshodoval s během:**
`_analyza\\_registr-bran.json` (ruční, `"kdy": "2026-10-02 22:06"`, s **předpřesunovou**
cestou `C:\\Users\\Ssevc\\Local-Deepseek\\orchestra`), ruční výčet v `HANDOFF.md` §6
a devět nástrojů v `AGENTS.md` (tři nikde neběžely).

**Náprava:** `g3` — který brány **skutečně spouští** — **zapisuje registr sám**.
Registr tím přestal být **tvrzení** a je **výstup běhu**: 37 bran s `exit`,
čítačem, příkazem a seznamy deklarovaných výjimek. `AGENTS.md` to uvádí jako
**jedinou autoritu** a říká, že se **needituje rukou**.

**⚠ Dvě věci, které k tomu patří (a jsou naměřené):**
* Registr se **nezapisuje v režimu `--soubor`** (`_POUZE_VYSTUP`) — v něm si
  doklady a mutační testy **mění `BRANY`**, takže by se uložil **zmrzačený
  seznam z mutace**.
* **Co se nezměnilo:** inventář se musí přegenerovat **po každé editaci kódu**,
  ne po každém běhu `g3` — ověřeno: otisk vstupů je **před i po** běhu `g3`
  shodný (`125d8fa1…`), protože registr je z otisku **vyloučený** (`_analyza\\_[^/]*\\.json`).

### 41.4 Co zůstává OTEVŘENÉ (a proč to není lenost, ale postup)

Uživatel **schválil** i zbytek KB, ale ty čtyři body **nejdou udělat bezpečně
v jedné session s autorem** — `AGENTS.md` a `PREDAVANI-SESSION.md` §2.2:
**navrhne jedna session, ověří druhá**, a „nic nesmí zmizet“ se **dokazuje
hledáním**, ne pamětí autora. Zadání je hotové: `ZADANI-OPTIMALIZACE-KB.md`.

| Bod | Co je to | Proč vlastní session |
|---|---|---|
| **§6.4 + §6.8** | **přesun projektové znalosti z `orchestra` skillu do hry** (~11,6 kB, **jeden a týž blok textu**) | mění **18 textů**, které z toho skillu **vyžaduje `over-dokumentaci.py`** — přesun bez úpravy brány ji shodí |
| **§6.5 + §6.6** | **PŘESUN** (ne zkrácení!) `DSH_HOME` §„Jak ověřovat“ a `overovani` §7 | dotýká se **trvalých pravidel**; auditovy důvody „duplikuje jinde“ byly **vyvráceny ve 3 ze 3 případů** |
| **§6.11** | **přesun historie z `HANDOFF.md`** (569 tis. znaků z 656 kB) | je to **přepis stavu**: `kronika-kontrola.py` **čte omyly z §8**, takže přesun §8 znamená **upravit i bránu** |
| **§6.9** | nepravdivé číslo „**27 podmíněných kontrol**“ (`game-developer` + `AGENTS.md` hry) | naměřeno dnes: **`has_method` na 23 řádcích** → patří k §6.8 (přesun do hry) |
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
print("Zápis §41 do HANDOFF.md (idempotentní)")
print("=" * 78)

puvodni = H.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "HANDOFF má LF (zapisuje se bajty)")

if any(r.startswith("## 41. ") for r in radky):
    print("  OK    oddíl §41 už v HANDOFFu je — nevkládám")
    kontrol += 1
else:
    # Kotva: konec oddílu §40 (poslední řádek před koncem souboru).
    k(any(r.startswith("## 40. ") for r in radky), "v HANDOFFu je oddíl §40 (kotva)")
    if radky and not radky[-1].endswith("\n"):
        radky[-1] = radky[-1] + "\n"
        k(radky[-1].endswith("\n"), "doplněn konec řádku na konci souboru")
    # ⚠ NADPIS MUSÍ BÝT NA ZAČÁTKU ŘÁDKU (`startswith`) — kdyby se vložil jako
    # `"\\n" + SEKCE` JEDEN prvek, je na řádku `"\n## 41. …"` a `startswith`
    # (i `grep`) ho NENAJDE. Přesně to se stalo u §40 (omyl zapsaný v komentáři
    # `p22-zapis-zaznamu.py`) — tady se to dělá jako DVA prvky.
    radky.append("\n")
    radky.append(SEKCE)
    k(any(r.startswith("## 41. ") for r in radky),
      "oddíl §41 přidán na konec (nadpis na začátku řádku)")

nove = "".join(radky).encode("utf-8")
if nove != puvodni:
    H.write_bytes(nove)
    print(f"  ZAPSÁNO: HANDOFF.md ({len(puvodni)} → {len(nove)} B)")
else:
    print("  HANDOFF beze změny")

zpet = H.read_bytes()
k(zpet == nove, "soubor na disku odpovídá zapsanému")
k(not zpet.startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")
k(zpet.count(b"\r\n") == 0, "v HANDOFFu nejsou CRLF")
t2 = zpet.decode("utf-8")
k("## 41. " in t2, "oddíl §41 je v dokumentu")
k("navrhne jedna session, ověří druhá" in t2, "oddíl nese důvod, proč zbytek čeká")
k("§2.12" in t2, "oddíl odkazuje na dnešní stav (§2.12)")

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)

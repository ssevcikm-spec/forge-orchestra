# -*- coding: utf-8 -*-
r"""P22 — zápis CHYBĚJÍCÍCH záznamů po session P22 (kronika + HANDOFF §8/§40).

PROČ TENHLE SKRIPT EXISTUJE: session P22 (6. 10. 2026, KB optimalizace) skončila
**commitnutou a pushnutou prací, ale bez záznamů** — v `HANDOFF.md` i
`KRONIKA-PROJEKTU.md` nebylo slovo „P22" ani jednou (naměřeno `git log --name-only`
nad pushnutými commity a `t.count("P22") == 0`). Zadání P22 (bod 2.4) při tom
žádalo **řádek session, nálezy a omyly** — tedy přesně to, co dělá kroniku
kronikou. Záznam se dopisuje **dodatečně, ale dodatečně se NEPŘEPISUJE nic**.

PROČ SKRIPTEM (a ne `edit` toolem): řádky tabulky v kronice mají **přes 2000
znaků**, takže „vložení" kotvou z načteného (zkráceného) řádku by celý řádek
NAHRADILO zkráceným textem — to je omyl **206** (P20) a **194** (P19). Skript
proto bere kotvy **z disku** a vkládá VEDLE nich.

IDEMPOTENTNÍ: co už v dokumentu je, se nechá být (a skript to vypíše).
Konci řádků se NEMĚNÍ: čte se po bajtech a zapisuje `write_bytes`,
protože `write_text()` by `\n` přeložil na `\r\n` (skill `dsh-prostredi` §3).

Použití: python _analyza/p22-zapis-zaznamu.py
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
HANDOFF = WS / "HANDOFF.md"
GATE = WS / "_analyza" / "kronika-kontrola.py"

# ── 1) OMYLY 211–213 ────────────────────────────────────────────────────────
# Tři omyly P22 jsou VŠECHNY ze zápisu do kroniky (ne z kódu) a jsou doložené
# v hlavičce `REVIZE-PRACOVNIHO-RITUALU.md`: „dnes vznikly tři vlastní chyby
# (neuznaný typ session; starý název sekce v mém vlastním skriptu; skript,
# který vždy četl živý soubor místo zadaného). Všechny tři odhalila brána,
# ne autor."
#
# ⚠ PROČ BLOK `8za` A NE `8a`: všechny jednoznakové názvy (`8a`–`8z`) jsou
# OBSAZENÉ — ne proto, že by jich bylo 25, ale protože `8a` v dokumentu NIKDY
# nevzniklo a `8z` je poslední použité. Blok `8z` navíc NENÍ volný (má 16 omylů
# z P20). Gate proto musí umět DVOUZNAKOVÝ suffix; to je rozšíření vzoru
# `8[a-z]?` → `8[a-z]{1,2}`, které STÁLE platí i pro jednoznakové bloky
# (kronika má vlastní vzor `8[a-z]+`, ten dvě písmena bere už dnes).
BLOK_8ZA = """### 8za. Omyly **211–213** — ROZHODOVACÍ session 6. 10. 2026 (P22: DOPSÁNÍ ZÁZNAMŮ, KTERÉ P22 NEZAPSALA)

**Tyhle tři omyly NEVZNIKLY v kódu — vznikly v ZÁPISU do kroniky** (a to je
téma, kterým se P22 celou dobu zabývala). Všechny tři odhalila **brána**
(`kronika-kontrola.py`), **ne autor** — a to je i důvod, proč se sem dopisují
až teď: bez zápisu by nebyly vidět vůbec.

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **211** | „Typ session `prováděcí` brána uzná.“ | `kronika-kontrola.py:374` zná **pět** typů (`akční`, `plánovací`, `ověřovací`, `analýza`, `rozhodovací`) a `prováděcí` mezi nimi **není** → `2 řádků session nemá uvedený typ`, `exit 1` | **Slovník brány jsem neotevřel.** Vymyslel jsem si typ podle sebe a zapsal ho jako fakt — táž třída jako „předpoklad zapsaný jako kontrola“ (omyl **195**) |
| **212** | „Název sekce si v zápisovém skriptu napíšu z hlavy (`## 4. Evidence omylů`).“ | Sekce se v P19 **přečíslovala** (`§3 Počty omylů` / `§4 Evidence omylů`); skript hledal kotvu, která **v dokumentu je**, ale **ne tam, kde jsem myslel** — a zapsal jinam, než měl | **Kotva opsaná z paměti místo z dokumentu.** Naměřeno už dřív jako past „kotva, která usne“ (§21.4) — a stejně se to stalo znovu |
| **213** | „Skript si živý soubor načte sám, je to jedno.“ | Skript dostal **cestu argumentem** (fixtura), ale **vždy četl živý soubor** — takže měřil něco jiného, než co mu bylo zadáno, a **na fixtuře by hlásil o živém stromě** | **Vstupy se mají číst TAM, KAM UKAZUJÍ, ne tam, kde je po ruce.** Táž třída jako `kronika-kontrola.py`, který bere cesty argumenty právě proto (ř. 52) |

**Poučení (a je to totéž, co hlásá `REVIZE-PRACOVNIHO-RITUALU.md` §3.4):**
**zápisy do dokumentů se dělají PROGRAMOVĚ** (`p21-zapis-kroniky.py` obstál
napoprvé) — ruční editace řádků delších, než je okno čtení, vyrobí chybu, kterou
**vidí jen brána**. Dvě z těch tří chyb (211, 212) jsou přesně to.
"""

# ── 2) ŘÁDEK SESSION 36 v kronice §1 ────────────────────────────────────────
RADEK_36 = (
    "| **36** | **6. 10. 2026** (13:0x–15:5x UTC = 15:0x–17:5x +02:00) | "
    "**rozhodovací (mimo zadání)** | **P22: OPTIMALIZACE ZNALOSTNÍ BÁZE** — session "
    "měla podle `NEXT-SESSION-INSTRUKCE.md` dělat **věcnou práci na conductoru** "
    "(C1/C2/O1), ale uživatel zadal **KB**: projít skilly, pravidla a dokumenty a "
    "opravit, co je nepravdivé. Provedeno **10 z 24 bodů** návrhu "
    "`OPTIMALIZACE-KNOWLEDGE-BASE.md` | "
    "mrtvé cesty v KB **45 → 23 → 7** (nový nástroj `_tools\\over-cesty-v-kb.mjs` "
    "odlišuje historickou zmínku od vady) · **brána na PRAVDIVOST KB** v "
    "`tools\\over-skilly.py` (dřív zelená nad **23 neexistujícími cestami**) — "
    "mutačně ověřena **oběma směry** · **`.py` NESMÍ BOM** v `DSH_HOME\\AGENTS.md` "
    "(dřív se to četlo opačně); rozpočet řetězce **38 867 / 65 536 B** · "
    "**pojistka proti zápisu** v `p20-d-doklady.py` (dávka spouštěla zapisovače do "
    "kroniky — mutačně ověřeno: mutant v kronize ohlášen) · **tři živě vyvrácená "
    "tvrzení** opravena · `_analyza\\_mutace.py` (jedna funkce proti tiché mutaci) "
    "se sabotážním testem `p22-test-mutace.py` **19/0**, který mutuje **živou "
    "bránu** a ověří, že **verdikt se změnil** · `g3` bere `FORGE_STANICE`/`FORGE_HRA` "
    "z prostředí (vzor override **už v repu byl**) · `POUCENI-A-VZORY.md` "
    "zaregistrován, prázdné zadání v kořeni stanice → **tombstone** | "
    "**211–213** (`8za`) | "
    "**NÁLEZ (audit KB přecenil duplicity ve TŘECH ZE TŘÍ případů):** návrh chtěl "
    "**zkrátit** `orchestra` skill (§6.8), `overovani` §7 (§6.6) a `DSH_HOME` "
    "§„Jak ověřovat“ (§6.5) s odůvodněním „duplikuje jinde“; plošný sken ukázal "
    "**8 z 9**, **9 ze 14** a **15 z 18** vzorů/frází **JEN na těch místech** → "
    "**škrtnutí by znalost zničilo**, správný postup je PŘESUN s ověřením. "
    "Audit porovnával **TÉMATA**, ne **OBSAH** · a samotný tahle session měla "
    "**nulový zápis do záznamů** — dohnalo se to dodatečně (oddíl **§40** a tenhle "
    "řádek) |"
)

SEKCE_216 = """### 2.16 Nálezy z P22 (6. 10. 2026) — audit KB přecenil duplicity a `over-skilly` byl zelený nad 23 mrtvými cestami

**Vznikly tím, že se AUDIT ZNALOSTNÍ BÁZE PŘEMĚŘIL** — a to je celý jejich
význam. Nejde o nové H-číslo: jsou to **tvrzení o měření**, která obstála jen
do chvíle, než se změřila jinak (vzor H97/H100). Záznam: `HANDOFF.md` **§40**;
podklad: `OPTIMALIZACE-KNOWLEDGE-BASE.md` (hlavička) a
`REVIZE-PRACOVNIHO-RITUALU.md`.

| # | Co audit tvrdil | Co naměřeno | Stav |
|---|---|---|---|
| **P22-A** | **`over-skilly.py` je zelený → skilly jsou v pořádku.** Gate měřil **front-matter, počet řádků a délku description** — na **cesty** se neptal vůbec | `_tools\\over-cesty-v-kb.mjs`: **23 cest, které neexistují**, v **10 ze 17 souborů** (`hlouchkova-analyza` 4, `dsh-prostredi` 5, `orchestra` 4, `dokumentace` 2, `dsh-usage` 2, `otevrena-temata` 2, `game-assets` 1, `game-developer` 1, oba `AGENTS.md` 1) — a **zelená byla celou dobu** | **OPRAVENO (P22)** — `over-skilly.py` nově **kontroluje existenci cest k nástrojům**; mutant → 1 mrtvá cesta a **`exit 1`**, zdravý stav → **0 mrtvých, `exit 0`**. Zbylých **7** zmínek je legitimních (text sám říká, že cesta neexistuje) a nástroj je odlišuje |
| **P22-B** | **„Duplikát se má zkrátit.“** Návrh §6.5/§6.6/§6.8 tvrdil, že tři místa duplikují jiná, a proto je lze ořezat — vypadalo to jako úspora **~27 kB** | Plošný sken devíti vzorů: `orchestra` skill má **8 z 9** vzorů o branách hry, hra (`uo-shadows\\AGENTS.md`) jen **2**, orchestra `AGENTS.md` **0**, `HANDOFF` **1**; `overovani` §7: **9 ze 14** pastí je **jen tam**; `DSH_HOME` §„Jak ověřovat“: **15 z 18** frází je **jen tam** | **VYVRÁCENO U VŠECH TŘÍ — a je to PRAVIDLO PRO RITUÁL:** „duplikát“ je **tvrzení, které se měří**, a měřit se má **PŘED** škrtáním. Audit, který duplicity vyjmenuje **podle tématu**, vyrábí **nebezpečný podklad**. Správný postup je **PŘESUN s ověřením, že každá věta zůstala dohledatelná** (`ZADANI-OPTIMALIZACE-KB.md`) |
| **P22-C** | **Záznamy se píšou na konci session — takže po P22 jsou.** | `HANDOFF.md` i `KRONIKA-PROJEKTU.md` měly **0 výskytů „P22“** a poslední řádek kroniky byl **35** (P20/P21). Práce byla **pushnutá**, záznam **žádný** | **DOPLNĚNO DODATEČNĚ** (oddíl **§40**, řádek **36**, blok **`8za`**). Zároveň je to **třetí měřený případ téhož**: záznam zapsaný po commitu zůstane ve stromě (H88), zadání tvrdí commit, který není (H104) — a tady **záznam chybí úplně, a nikdo si toho nevšiml, protože brány kontrolují jen to, co je zapsané** |
"""

# ── 3) SOUHRNNÝ ŘÁDEK §3 ────────────────────────────────────────────────────
STARY_CELKEM = "| **celkem** | **26 bloků, 34 sessions** | **205** | **178 = 87 %** | **54** |"
NOVY_CELKEM = "| **celkem** | **27 bloků, 35 sessions** | **208** | **181 = 87 %** | **54** |"
RADEK_8ZA = "| **8za** | rozhodovací **6. 10. 2026** (P22: **dopsání záznamů, které P22 nezapsala**) | **3** | **3** | **0** |"

RADEK_35_PREFIX = "| **35** |"
RADEK_8Z_PREFIX = "| **8z** |"
RADEK_36_PREFIX = "| **36** |"
SEKCE_216_PREFIX = "### 2.16 "
SEKCE_8ZA_PREFIX = "### 8za. "
SEKCE_40_PREFIX = "## 40. "

# ── 4) ODDÍL §40 v HANDOFF.md ───────────────────────────────────────────────
SEKCE_40 = """## 40. P22 — OPTIMALIZACE ZNALOSTNÍ BÁZE (6. 10. 2026, mimo zadání) — a DODATEČNÝ ZÁPIS ZÁZNAMŮ

**Co tenhle oddíl JE:** **záznam o provedení** session **P22** — a zároveň
**záznam o tom, že se P22 nevešla do záznamů** a dopisuje se dodatečně.
**Nejde z něj číst dnešní stav** — ten je v **§2.12** (a novější body níž).
**Datum spotřeby:** údaje jsou k **6. 10. 2026, 15:0x–17:5x +02:00
(= 13:0x–15:5x UTC)**; co je starší, je **záznam**.

**Zadání:** `NEXT-SESSION-INSTRUKCE.md` z P21 žádalo **věcnou práci na
conductoru** (C1/C2/O1). **Uživatel to změnil** a zadal **optimalizaci
znalostní báze** (`OPTIMALIZACE-KNOWLEDGE-BASE.md` + `REVIZE-PRACOVNIHO-RITUALU.md`).
**Kód conductora se nedotkl ANI JEDEN soubor** — `deploy.yml` má filtr
`paths: conductor/**`, takže **žádné nasazení živé služby se nekonalo**
(ověřeno seznamem změněných souborů, ne odhadem).

### 40.1 Co je hotové (doloženo spuštěním)

| Co | Naměřeno | Kde je důkaz |
|---|---|---|
| **Mrtvé cesty v KB** | **45 → 23 → 7** (16 opraveno) | `_tools\\over-cesty-v-kb.mjs` (nový nástroj; odlišuje **historickou zmínku** od **vady**) |
| **Brána na PRAVDIVOST KB** | `over-skilly.py` **13/0, 0 mrtvých cest**; mutant → **`exit 1`**, zdravý stav → **`exit 0`** | `tools\\over-skilly.py` — do P22 se na cesty **neptal** a byl zelený nad **23 neexistujícími** |
| **`.py` NESMÍ BOM** | pravidlo v `DSH_HOME\\AGENTS.md`; rozpočet řetězce **38 867 / 65 536 B** | `over-dokumentaci.py` **67/0**; dřív to bylo **jen** v projektovém `AGENTS.md`, kde se to čte **opačně** |
| **Pojistka proti zápisu** | `p20-d-doklady.py` vypíše **15 zápisových skriptů** a hlídá hash **3 dokumentů**; mutant → **`⚠ ZMĚNĚN: KRONIKA-PROJEKTU.md`** | dávka dřív **spouštěla zapisovače do kroniky** bez kontroly (riziko auditu nástrojů) |
| **Tři živě vyvrácená tvrzení** | `README.md` (cesty `E:\\DSH*`), `DEPLOY-VYLEPSENI.md` (opatření **8 a 9 JSOU nasazená**), komentář ve `validate-all.mjs` | ověřeno v `package.json` profilu, ne dojmem |
| **`_mutace.py` + sabotážní test** | `p22-test-mutace.py` **19/0**; sabotáž (vypnutá kontrola v knihovně) → **`CHYBA`, `exit 1`** | test **mutuje živou bránu** `tools\\over-skilly.py`, spustí ji a ověří, že **verdikt se změnil** (ne jen text) |
| **`g3` bere cesty z prostředí** | `FORGE_STANICE` / `FORGE_HRA` s **týmiž defaulty**; bez override **stejný běh** (`g3` 37 bran, `exit 0`; self-testy `h71` 15/0, `h87` 18/0) | vzor override **už v repu byl** (`FORGE_GODOT`, `verify-setup.py`) — `g3` ho jen nepoužíval |
| **Rejstřík a tiché díry** | `POUCENI-A-VZORY.md` (64,7 kB, **0 odkazů ve 622 `.md`**) zaregistrován; prázdný `NEXT-SESSION-INSTRUKCE.md` v kořeni stanice → **tombstone** | obojí přidáno do kontroly diakritiky a **mutačně ověřeno**, že je vidí |

### 40.2 ⚠ NÁLEZ P22-B: AUDIT PŘECENIL DUPLICITY VE TŘECH ZE TŘÍ PŘÍPADŮ

Návrh `OPTIMALIZACE-KNOWLEDGE-BASE.md` chtěl **zkrátit** tři místa s odůvodněním
„duplikuje jinde“ (dohromady ~27 kB). **Přeměřeno plošným skenem a ani jeden
případ neobstál:**

| Bod | Co audit tvrdil | Co naměřeno |
|---|---|---|
| **§6.8** `orchestra` skill | blok o branách hry duplikuje `uo-shadows/AGENTS.md` | **8 z 9** vzorů je **JEN ve skillu**; hra má **2**, orchestra `AGENTS.md` **0**, `HANDOFF` **1** |
| **§6.6** `overovani` §7 | §7.1–7.14 duplikuje `dsh-prostredi` a `DSH_HOME` | **9 ze 14** pastí je **JEN v `overovani`** |
| **§6.5** `DSH_HOME` §„Jak ověřovat“ | 7,6 kB → 2,2 kB, příklady patří do `overovani` | **15 z 18** klíčových frází je **JEN v `DSH_HOME`** |

**Proč se to stalo:** audit porovnával **TÉMATA** („obě místa mluví
o ověřování“), ne **OBSAH**. **Důsledek: ty tři body se NESMÍ dělat jako
„zkrácení“** — jen jako **PŘESUN s ověřením, že každá věta zůstala dohledatelná**
(zadání: `ZADANI-OPTIMALIZACE-KB.md`).

### 40.3 Proč tenhle oddíl vzniká DODATEČNĚ (a co to znamená)

**Naměřeno 6. 10. 2026 při dopisování:** `HANDOFF.md` **0 výskytů „P22“**,
`KRONIKA-PROJEKTU.md` **0 výskytů „P22“**, poslední blok omylů `8z` (P20),
poslední řádek session **35**. **Práce byla pushnutá, záznam žádný.**

Zapsáno dodatečně: **řádek 36** v kronice §1, sekce **2.16**, blok omylů **`8za`**
(omyly **211–213**, všechny tři ze **zápisu**, doložené v hlavičce
`REVIZE-PRACOVNIHO-RITUALU.md`) a **tenhle oddíl**. Nic se nepřepisovalo.

> **⚠ POUČENÍ, KTERÉ JE DRAŽŠÍ NEŽ TEN ZÁZNAM:** **brány kontrolují jen to, co je
> ZAPSANÉ.** `kronika-kontrola.py` i `handoff-kontrola-uplnost.py` byly po celou
> dobu P22 **zelené** (`SEDÍ`, `83/83`) — a přitom v obou dokumentech **chyběla
> celá session**. Chybějící záznam **není rozchod**, který by brána viděla:
> je to **ticho**. Kdo chce tuhle třídu chytit, musí se ptát **naopak** („má
> každý pushnutý commit svůj záznam?“), jako to dělá `s24-meridla-over.py`
> u bloků omylů.

### 40.4 Co zůstává OTEVŘENÉ (po P22)

* **Zbývající body KB** — `§6.4` (projektová znalost z `orchestra` skillu do
  projektu), `§6.11` (**569 tis. znaků historie** z `HANDOFF.md`; dnes 20. oddíl
  navíc), `§6.5`/`§6.6`/`§6.8` (jen jako **PŘESUN**), `§6.14` (jedna autorita
  seznamu živých), `§6.15` (zobecnění měřidel) — zadání je
  `ZADANI-OPTIMALIZACE-KB.md`.
* **Revíze rituálu** — zavedeny **jen** body 2 a 7 (`_mutace.py`,
  `_tools\\rozpad-session.mjs`); **1, 3, 4, 5, 6 čekají na rozhodnutí**, protože
  mění **postup předávání** nebo **trvalá pravidla** (`REVIZE-PRACOVNIHO-RITUALU.md` §5).
* **`otevrena-temata`** — **7 nezaškrtnutých položek leží v sekci „Uzavřené“**
  (sekce tvrdí jedno, značky druhé) a **dvě témata jsou prokazatelně vyřešená**,
  jen neuzavřená; to je **drobnost, ale je to táž vada** jako §2.10–§2.12.
* **Údržba měřidel** — `g3` **37 bran, 1 deklarovaný nenulový** (`zadání
  kontrola`), `validate-all` **`✓ VŠE V POŘÁDKU`**; `ov-g-h92-sken.py` zůstává
  **červený jako doložený falešný poplach** (H103 — **neopravovat**).
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
print("P22 — dodatečný zápis záznamů (kronika + HANDOFF §8/§40), idempotentní")
print("=" * 78)

k(KRONIKA.is_file(), f"kronika existuje: {KRONIKA}")
k(HANDOFF.is_file(), f"handoff existuje: {HANDOFF}")
k(GATE.is_file(), f"brána existuje: {GATE}")

# ── A) gate: rozšířit vzor bloku omylů na DVOUZNAKOVÝ suffix (8za) ──────────
# ⚠ ZAPSANÝ VLASTNÍ OMYL (a není v kronize, protože je z DOPISOVÁNÍ záznamů):
# první verze téhle opravy použila `8[a-z]{1,2}` — a to je **jiný jazyk, než
# jsem si myslel**: `?` znamená „0 nebo 1“, ale `{1,2}` znamená „1 nebo 2“,
# takže zápis **ZTRATIL základní blok `## 8.`** (a s ním 13 omylů z tabulky
# `1–13`). Součet spadl z **205 na 195** a brána ohlásila rozchod
# „kronika §3 má řádek `1–13`, ale v HANDOFF.md pro něj NENÍ nadpis bloku“.
# **Našla to brána, ne oko** — a správný zápis je `{0,2}`.
gt = GATE.read_text(encoding="utf-8")
if "8[a-z]{0,2}" in gt:
    print("  OK    vzor bloku v bráně už je `{0,2}` — neměním")
    kontrol += 1
else:
    bylo = "8[a-z]{1,2}" in gt
    if bylo:
        print("  (nález: vzor je `{1,2}` — tím se ztratil základní blok `## 8.`; opravuji na `{0,2}`)")
    else:
        k("8[a-z]?" in gt, "v bráně je očekávaný jednoznakový vzor bloku")
    gt2 = gt.replace("8[a-z]{1,2}", "8[a-z]{0,2}").replace("8[a-z]?", "8[a-z]{0,2}")
    GATE.write_bytes(gt2.encode("utf-8"))
    k("8[a-z]{0,2}" in GATE.read_text(encoding="utf-8"),
      "vzor bloku je `8[a-z]{0,2}` (základní `8` i dvouznakový `8za` platí)")
    k(not GATE.read_bytes().startswith(b"\xef\xbb\xbf"), "brána nemá BOM")

# ── B) KRONIKA ──────────────────────────────────────────────────────────────
puvodni = KRONIKA.read_bytes()
text = puvodni.decode("utf-8")
radky = text.splitlines(keepends=True)
k("\r" not in text, "kronika má LF (zapisuje se zpět bajty)")

# B1) řádek session 36
uz36 = any(r.startswith(RADEK_36_PREFIX) for r in radky)
if uz36:
    print("  OK    řádek 36 už v kronice je — nevkládám")
    kontrol += 1
else:
    idx35 = next((i for i, r in enumerate(radky) if r.startswith(RADEK_35_PREFIX)), None)
    k(idx35 is not None, "kotva: řádek session 35 v §1")
    if idx35 is not None:
        konec = "\n" if radky[idx35].endswith("\n") else ""
        radky.insert(idx35 + 1, RADEK_36 + konec)
        k(any(r.startswith(RADEK_36_PREFIX) for r in radky), "řádek 36 vložen ZA řádek 35")

# B2) sekce 2.16 (před §3)
uz216 = any(r.startswith(SEKCE_216_PREFIX) for r in radky)
if uz216:
    print("  OK    sekce 2.16 už v kronice je — nevkládám")
    kontrol += 1
else:
    idx3 = next((i for i, r in enumerate(radky) if r.startswith("## 3. Počty omylů")), None)
    k(idx3 is not None, "kotva: `## 3. Počty omylů`")
    if idx3 is not None:
        radky.insert(idx3, SEKCE_216 + "\n")
        k(any(r.startswith(SEKCE_216_PREFIX) for r in radky), "sekce 2.16 vložena před §3")

# B3) řádek bloku 8za v tabulce §3 (za 8z)
uz8za = any(r.startswith("| **8za** |") for r in radky)
if uz8za:
    print("  OK    řádek bloku 8za v §3 už je — nevkládám")
    kontrol += 1
else:
    i8z = next((i for i, r in enumerate(radky) if r.startswith(RADEK_8Z_PREFIX)), None)
    k(i8z is not None, "kotva: řádek bloku 8z v tabulce §3")
    if i8z is not None:
        konec = "\n" if radky[i8z].endswith("\n") else ""
        radky.insert(i8z + 1, RADEK_8ZA + konec)
        k(any(r.startswith("| **8za** |") for r in radky), "řádek bloku 8za vložen ZA 8z")

# B4) souhrnný řádek
i_cel = next((i for i, r in enumerate(radky) if r.startswith("| **celkem** |")), None)
k(i_cel is not None, "souhrnný řádek `celkem` nalezen")
if i_cel is not None:
    if NOVY_CELKEM in radky[i_cel]:
        print("  OK    souhrn už je přepočítaný (27 bloků / 35 sessions / 208) — neměním")
        kontrol += 1
    else:
        k(STARY_CELKEM in radky[i_cel], "souhrn má očekávaný tvar (26 bloků / 34 sessions / 205)")
        if STARY_CELKEM in radky[i_cel]:
            radky[i_cel] = radky[i_cel].replace(STARY_CELKEM, NOVY_CELKEM)
            k(NOVY_CELKEM in radky[i_cel], "souhrn přepsán na 27 bloků / 35 sessions / 208")

novy = "".join(radky).encode("utf-8")
if novy != puvodni:
    KRONIKA.write_bytes(novy)
    print(f"  ZAPSÁNO: KRONIKA-PROJEKTU.md ({len(puvodni)} → {len(novy)} B)")
else:
    print("  kronika beze změny (vše už zapsané)")

zpet = KRONIKA.read_bytes()
k(zpet == novy, "kronika na disku odpovídá zapsanému")
k(not zpet.startswith(b"\xef\xbb\xbf"), "kronika nemá BOM")
k(zpet.count(b"\r\n") == 0, "v kronize nejsou CRLF")

# nezávislé ověření obsahu (hledáním, ne pamětí)
t2 = zpet.decode("utf-8")
k("| **36** |" in t2, "kronika obsahuje řádek session 36")
k("### 2.16 " in t2, "kronika obsahuje sekci 2.16")
k("| **8za** |" in t2, "kronika obsahuje řádek bloku 8za")
k("**27 bloků, 35 sessions**" in t2, "souhrn §3 uvádí 27 bloků / 35 sessions")

# ── C) HANDOFF: blok omylů 8za + oddíl §40 ─────────────────────────────────
puvodni_h = HANDOFF.read_bytes()
th = puvodni_h.decode("utf-8")
rh = th.splitlines(keepends=True)
k("\r" not in th, "handoff má LF (zapisuje se zpět bajty)")

uz8za_h = any(r.startswith(SEKCE_8ZA_PREFIX) for r in rh)
if uz8za_h:
    print("  OK    blok 8za v HANDOFFu už je — nevkládám")
    kontrol += 1
else:
    i8z_h = next((i for i, r in enumerate(rh) if r.startswith("### 8z.")), None)
    k(i8z_h is not None, "kotva: nadpis `### 8z.` v HANDOFFu")
    if i8z_h is not None:
        rh.insert(i8z_h, BLOK_8ZA + "\n")
        k(any(r.startswith(SEKCE_8ZA_PREFIX) for r in rh), "blok 8za vložen PŘED blok 8z")

uz40 = any(r.startswith(SEKCE_40_PREFIX) for r in rh)
if uz40:
    print("  OK    oddíl §40 v HANDOFFu už je — nevkládám")
    kontrol += 1
else:
    # ⚠ DRUHÝ ZAPSANÝ OMYL TOHOHLE SKRIPTU: první verze přidala `"\n" + SEKCE_40`
    # jako JEDEN prvek seznamu. Když soubor nekončí newline, vznikne z toho
    # `…text## 40. P22 — …` — nadpis NENÍ na začátku řádku a brána (i `grep`)
    # ho nenajde. **Našla to vlastní kontrola skriptu**, ne oko.
    if rh and not rh[-1].endswith("\n"):
        rh[-1] = rh[-1] + "\n"
        k(rh[-1].endswith("\n"), "doplněn konec řádku na konci HANDOFFu")
    rh.append("\n" + SEKCE_40)
    k(any(r.startswith(SEKCE_40_PREFIX) for r in rh),
      "oddíl §40 přidán na konec HANDOFFu (nadpis na začátku řádku)")

novy_h = "".join(rh).encode("utf-8")
if novy_h != puvodni_h:
    HANDOFF.write_bytes(novy_h)
    print(f"  ZAPSÁNO: HANDOFF.md ({len(puvodni_h)} → {len(novy_h)} B)")
else:
    print("  HANDOFF beze změny (vše už zapsané)")

zpet_h = HANDOFF.read_bytes()
k(zpet_h == novy_h, "HANDOFF na disku odpovídá zapsanému")
k(not zpet_h.startswith(b"\xef\xbb\xbf"), "HANDOFF nemá BOM")
k(zpet_h.count(b"\r\n") == 0, "v HANDOFFu nejsou CRLF")
th2 = zpet_h.decode("utf-8")
k("### 8za. " in th2, "HANDOFF obsahuje blok omylů 8za")
k("## 40. " in th2, "HANDOFF obsahuje oddíl §40")
k("| **213** |" in th2, "HANDOFF obsahuje omyl 213")

# ── D) VOLÁNÍ BRÁNY (autorita, ne vlastní vzor) ────────────────────────────
import subprocess  # noqa: E402

r = subprocess.run([sys.executable, str(GATE)], capture_output=True, text=True,
                   encoding="utf-8", errors="replace", cwd=str(WS))
v = (r.stdout or "") + (r.stderr or "")
m = re.search(r"omylů celkem \(skutečnost\):\s*(\d+)", v)
nalezeno = int(m.group(1)) if m else None
m2 = re.search(r"sessions v kronice:\s*(\d+)", v)
sessions = int(m2.group(1)) if m2 else None
print()
print(f"  (brána: omylů celkem {nalezeno}, sessions {sessions}, exit {r.returncode})")
k(nalezeno == 208, f"brána počítá 208 omylů (naměřeno {nalezeno})")
# ⚠ SESSIONS SE NEKOTVÍ NA PEVNÉ ČÍSLO (opraveno 6. 10. 2026 večer):
# doklad vznikl, když bylo sessions **35**; o hodinu později přibyl **řádek 37**
# (schválené práce P23k) a kontrola spadla — na **správném** dokumentu.
# Je to táž třída jako omyl **209** („doklad s kotvou natvrdo“): doklad závislý
# na STAVU dokumentu zastará **spolu s ním**. Kontroluje se proto jen to, co má
# smysl: **že se řádek P22 (session 36) počítá** — ne kolik jich je dnes.
k(sessions is not None and sessions >= 36,
  f"brána vidí aspoň 36 sessions (naměřeno {sessions})")
k(bool(re.search(r"^\|\s*\*\*36\*\*\s*\|", t2, re.M)), "kronika §1 obsahuje řádek 36")

for radek in v.splitlines():
    if "8za" in radek and "kronika tvrdí" in radek:
        print(f"  ({radek.strip()})")
k("8za" in v, "blok 8za je v součtu brány (jinak by se nepočítal)")
k(r.returncode == 0, f"brána `kronika-kontrola.py` končí exit 0 (naměřeno {r.returncode})")

# ── E) OVĚŘENÍ, ŽE SE NIC NEZTRATILO (druhá brána) ────────────────────────
r2 = subprocess.run([sys.executable, str(WS / "_analyza" / "handoff-kontrola-uplnost.py")],
                    capture_output=True, text=True, encoding="utf-8",
                    errors="replace", cwd=str(WS))
v2 = (r2.stdout or "") + (r2.stderr or "")
m3 = re.search(r"nalezených:\s*(\d+)", v2)
m4 = re.search(r"CHYBÍ:\s*(\d+)", v2)
print(f"  (handoff úplnost: nalezených {m3.group(1) if m3 else '?'}, "
      f"CHYBÍ {m4.group(1) if m4 else '?'}, exit {r2.returncode})")
k(m4 is not None and m4.group(1) == "0", "handoff úplnost: CHYBÍ 0 (nic nezmizelo)")
k(r2.returncode == 0, f"handoff úplnost končí exit 0 (naměřeno {r2.returncode})")

# surový počet znaků, ne interpretace: kolik P22 v dokumentech přibylo
k(th2.count("P22") >= 5, f"HANDOFF zmiňuje P22 {th2.count('P22')}× (bylo 0)")
k(t2.count("P22") >= 5, f"kronika zmiňuje P22 {t2.count('P22')}× (bylo 0)")

print()
print("=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
print("=" * 78)
for c in chyb:
    print(f"  CHYBA: {c}")

sys.exit(1 if chyb else 0)

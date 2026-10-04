"""Zapíše do `HANDOFF.md` blok omylů `8n` a oddíl `26` (výsledky session typu A).

PROČ SKRIPTEM A NE RUČNĚ: `HANDOFF.md` má 4 300+ řádků a je append-only záznam;
ruční zápis českého textu do PowerShellu dvakrát v tomhle projektu rozbil
diakritiku (`dsh-prostredi` §3d) a jednou z toho byl **prázdný oddíl** (omyl 58
v handoffu). Skript čte a píše `utf-8`, ověří, že text po zápisu v souboru JE,
a nic nepřepisuje — jen vkládá.

Vkládá se PŘED první výskyt kotvy `_KOTVA` (blok omylů `8m` končí, `8n` musí
být hned za ním, aby ho viděla brána kroniky — ta hledá nadpisy `### 8x.`).
"""
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HANDOFF = Path(__file__).resolve().parent.parent / "HANDOFF.md"

KOTVA = "## 25. Provedeno 2. 10. 2026 (20:1x–21:0x UTC) — AKČNÍ session: OPRAVA PĚTI MĚŘIDEL"

OMYLY = """### 8n. Omyly AKČNÍ session 3. 10. 2026 — **113–123** (typ A: „konec měřidel")

**Kontext:** session měla podle zadání `ZADANI-A-KONEC-MERIDEL.md` **nepostavit
ani jedno nové měřidlo** a dát všechno úsilí do dodávaného artefaktu. Hypotéza
byla, že tím vznikne **0–2 omyly** místo 7,8 (protože „není co zpackat").
**Naměřeno: 11 omylů** — hypotéza tedy **nepotvrzena** (viz §26.4).

**A poučení je v tom, KDE vznikly:** **osm z jedenácti je v měřidle nebo
v postupu měření** — a to i přesto, že „měřidla" v tomhle projektu vznikala
jen jako **pomocné sondy k jedné otázce** (ne brány do CI). Týž podpis jako
bloky `8e`–`8m`: **měřidlo odpovídá na jinou otázku, než jsem si myslel.**

| # | Co jsem si myslel | Naměřeno (pravda) | Jak to vzniklo |
|---|---|---|---|
| **113** | „Do PowerShellu můžu poslat skript heredocem" (`python - <<'PY'`) | **Nejde** — `The '<' operator is reserved for future use` a zbytek skriptu se parsuje jako PowerShell | Znal jsem pravidlo (`dsh-prostredi` §3f) a **přesto** jsem ho použil. Náprava: skript do souboru |
| **114** | „Když se `move()` zeptá `is_inside_tree()`, je měření chráněné před clampem" | **Není.** Ochrana prošla a clamp **přesto** posun zkrátil — viewport je v rané fázi `(0,0)`, takže `clampf(8, -8)` stlačí pozici na okraj | Ověřoval jsem **předpoklad**, ne **měřenou veličinu**. Pojistka, která projde, ještě neznamená, že je co hlídat |
| **115** | „Atrapa s vlastním `offset` je pro měření pohybu lepší než skutečná mapa" | **Horší** — hráče vystrčila mimo obrazovku, clamp posun zkrátil a **sklon vyšel 0,1211 místo 0,5000**. Vypadalo to jako vada izometrie | Měřil jsem na pohodlnějším vstupu, ne na tom, na kterém záleží. Opraveno měřením na **skutečném hráči a skutečné úrovni** |
| **116** | „Dvě kontroly HUD v jednom bloku jsou v pořádku" | **Parse error:** `There is already a variable named "hud_sc"` — vnější blok ukládání ji deklaruje taky | Názvy proměnných v GDScriptu platí pro **celou funkci**, ne pro blok |
| **117** | „Odstranit obejití `has_method("get_hp")` je lokální změna v `hud.gd`" | **Není** — atrapa `TestHrac` byla `extends Node2D` **bez jediné vlastnosti**, takže `hud.update()` spadl na `Invalid access to property 'hp'` a **tři správné kontroly HUD spadly** | Přehlédl jsem, že smlouva má **víc čtenářů než jednoho**: kdo ji mění, musí projít i **atrapy**, které ji předstírají |
| **118** | „Snímek ověří HUD, i když ho dám pod uzel hráče" | **Neověří** — `hud.gd` hledá komponenty přes `get_parent().component(id)`, takže pod hráčem vrátí `null` → **HP: 0** a snímek by ukázal nulu jako hotovou věc | Skoro jsem **předal snímek, který dokládá opak** toho, co jsem tvrdil. Zachytila to až kontrola `prvni.contains("HP: %d")` ve sondě |
| **119** | „`var _kostra := null` je obyčejná deklarace" | **Parse error:** `Cannot infer the type of "_kostra" variable because the value is "null"` | GDScript neumí odvodit typ z `null`; musí být `var _kostra: Node = null` |
| **120** | „Sonda vypíše výsledek jednou" | **Pětkrát** — `_process()` se volá každý frame a výpis nebyl ničím podmíněný | Výstup vypadal jako pět měření téhož; číslo se tím nedá číst. Opraveno příznakem `_zkontrolovano` |
| **121** | „Skript na roadmapu je hotový" | Zůstal v něm **nepoužitý seznam `ZMENY`** a mrtvá podmínka `if "CHYBA" in text[:0]` (nikdy nenastane) | Kód, který nic nedělá, vypadá jako práce — a při čtení někým dalším je to past |
| **122** | „Do tabulky očekávaných směrů napíšu `vlevo = (-1, +0.5)`" | **Špatně** — správně je `(-1, -0.5)` (naměřeno `(-1,9379; -0,9690)`). Sonda to **správně ohlásila jako FAIL** | Opsal jsem znaménko od sousedního řádku místo abych ho odvodil. **Kód byl správný, test ne** |
| **123** | „Když `move()` dá izometrické osy, je to totéž co mrtvá větev" | **Není — a to je nález.** Sonda ukázala, že mrtvá větev se **nikdy nepoužila**, takže se hráč celou dobu hýbal **1:1 podle obrazovky** (sklon 0 při dlaždicích 2:1). Rozdíl jsem **podcenil v návrhu** a odhalilo ho až měření PŘED a PO | Napsal jsem do kódu „vychází to nastejno" a **neověřil to**. Kdybych sondu nepostavil, „opravil" bych kód a nikdo by nevěděl, že se změnilo ovládání |

**Vzor z těch jedenácti:** **osm** vzniklo v **měřidle nebo v postupu měření**
(114, 115, 118, 120, 122, 123 + částečně 116, 121) a **tři vypadaly jako nález
o cizím kódu** (115 „izometrie je vadná", 117 „HUD je rozbitý", 118 „HUD
neukazuje HP") — **ani jeden z těch tří nebyl nález o cizím kódu.**

**A jeden omyl, který má cenu zvlášť (`123`):** je to **přesně ta past, před
kterou varuje `AGENTS.md`** — „neopravovat nástroj dřív, než je jasné, co je
špatně". Tady se to potkalo s **rozhodnutím uživatele**: naměřený rozdíl jsem
mu předložil **dřív**, než jsem ho zapsal do smlouvy, a on zvolil izometrické
osy. Kdybych se nezeptal, zapsal bych do `ARCHITEKTURA.md` smlouvu, kterou
nikdo neodsouhlasil — a soutisk s dlaždicemi by zůstal jiný.

"""

ODDIL_26 = """## 26. Provedeno 3. 10. 2026 — AKČNÍ session typu A: „KONEC MĚŘIDEL, PRÁCE NA HŘE"

**Co je tenhle oddíl:** **záznam o provedení** podle `ZADANI-A-KONEC-MERIDEL.md`.
**Co z něj ještě platí:** čísla jsou naměřená **touto** session; co zestará,
je označeno. **Není to stav** (ten je v §5 a §1) ani plán (ten je
v `PLAN-DALSI-KROK.md`).

**Výchozí stav ověřen před první změnou (zadání §1 bod 3):** `orchestra`
= `d1cde9b`, `uo-shadows` = `279f584`, testy hry **65 kontrol, 0 selhání**,
`_dukaz-assist.gd` → **exit 1**. **Všechno sedělo** na to, co zadání tvrdilo.

### 26.1 Úkol 1 — stav hráče, který jiné komponenty UŽ VOLALY

| Co | Před | Po | Doklad |
|---|---|---|---|
| `player.gd` stav | `hp`, `max_hp`, `mana`, `max_mana`, `target` **nebyly** | **jsou** (+ `inventory`, `add_item`, `remove_item`, `equipped`, `die`) | `tests/run_tests.gd` → 7 nových kontrol na klíče + 3 na metody |
| `_dukaz-assist.gd` | **`exit 1`** — `assist.evaluate()` vrátil `[]` a vypsal `SCRIPT ERROR` | **`exit 0`** — `VŠECHNY klice JSOU` | spuštěno, výstup níž |
| obejití v `hud.gd` | `has_method("get_hp")` → `elif "hp" in _player:` → **HP: 0** | **přímé `_player.hp`** | `HUD zobrazuje skutečné HP hráče (text začíná 'HP: 77')` |
| `assist.evaluate()` se **rozhoduje** | jen `has_method("evaluate")` | 4 kontroly: plné zdraví = nic, nízké hp/mana/mrtvý cíl = akce | tamtéž |

**Výstup `_dukaz-assist.gd` po opravě:**
```
[dukaz] hrac ma 'hp'?          true
[dukaz] hrac ma 'max_hp'?      true
[dukaz] hrac ma 'mana'?        true
[dukaz] hrac ma 'max_mana'?    true
[dukaz] VŠECHNY klice JSOU -> vada NENI (stav hrace je doplneny)
exit 0
```

**Soubor `_dukaz-assist.gd` se NEMAŽE** (zadání ho nechávalo na rozhodnutí):
zůstává jako **spustitelný doklad smlouvy** — dnes `exit 0`, a kdyby někdo stav
hráče odstranil, spadne na `exit 1`. Není to měřidlo projektu (není v CI ani
v `agent.yml`), je to **vstup k jednomu nálezu**.

### 26.2 Úkol 2 — mrtvá kontrola nad hráčem OŽIVENA

**Smlouva rozhodnuta a zapsána do `docs/ARCHITEKTURA.md` §2.2** (nová sekce,
tvar dat + přijímací kritérium, jak žádá §2.1 téhož dokumentu):

- **Smlouva je `move(dir, delta)`** — a `_physics_process` ji **volá**.
  Nejsou to dvě cesty k témuž: rozhraní je jedno a jen jedno místo mění pozici.
- **Izometrii nese `level.gd`** (`cell_center`/`cell_at`); `world.gd` ji nesmí
  opisovat.

**⚠ CO SE PŘITOM ZJISTILO — a je to viditelná změna ovládání (rozhodl uživatel):**
`player.gd` měl **MRTVOU** izometrickou větev `if level.has_method("iso_position")`
— `level.gd` tu metodu **nikdy neměl** (má ji jen `_retired/world.gd`). Vždy se
tedy použila větev `else` a **hráč chodil 1:1 podle obrazovky**, zatímco dlaždice
se kreslí 2:1. Naměřeno sondou `tests/_sonda-pohyb.gd`:

| směr | PŘED (1:1) | PO (izo osy) |
|---|---|---|
| vpravo | (2,167; 0) sklon **0** | (1,938; 0,969) sklon **0,5** |
| vlevo | (−2,167; 0) sklon **0** | (−1,938; −0,969) sklon **0,5** |
| vpravo+dolů | (1,532; 1,532) **45°** | (0; 2,167) **svisle** |

Osa dlaždice je `(48, 24)` → sklon **0,5**. **Hráč teď jde po dlaždicích.**
Uživatel to 3. 10. 2026 potvrdil jako správnou smlouvu (dotázán **před**
zápisem do dokumentace).

| Co | Před | Po | Doklad |
|---|---|---|---|
| kontroly hry | **65**, 0 selhání | **89**, 0 selhání | Godot `run_tests.gd` |
| řádek „kontrola izo projekce se NEMĚŘÍ" | **byl** | **NENÍ** | výstup testů |
| kontrola umí spadnout | — | **ANO** | `_analyza\\a2-mutace-izo.py`: zdravý 89/0 → s vadou **89/1** → zpět 89/0 |

**Jak kontrola měří (a proč ne přes konstantu):** `move()` ZAVOLÁ, změří POSUN
a porovná jeho sklon se sklonem osy dlaždice, který si **přečte
z `level.cell_center`**. Kdyby dlaždice někdo předělal na 1:1, kontrola spadne
i s kódem, který se nezměnil — konstanta opsaná do testu by to nezachytila.

**Mutační důkaz (přesně ta vada, kterou kontrola hlídá — vypuštění izo přepočtu):**
```
[test] 89 kontrol, 0 selhání          (zdravý kód)
[test] FAIL player.move() jde po ose dlaždic ve všech měřených směrech
       (sklon dlaždice 0.5000, chyb 4: ["(1.0, 0.0) sklon 0.0000", ...])
[test] 89 kontrol, 1 selhání          (s vrácenou vadou)
[test] 89 kontrol, 0 selhání          (po návratu)
```

### 26.3 Úkol 3 — roadmapa vs. `origin/main`

**Metoda:** každá granule ověřena proti **blobu v `origin/main`**
(`git show origin/main:<cesta>`), ne proti disku — pracovní strom měl
neopushnuté změny, takže disk **není** to, co je v repu. Nástroj:
`_analyza\\a3-roadmapa-over.py` (čte soubor, API i volající).

| Granule | Bylo | Naměřeno | Je |
|---|---|---|---|
| `world.map` | `done: true` | `scripts/world.gd` v `main` **NENÍ** (`c651368` ho přesunul do `_retired/`); `gather()`/`is_walkable()`/respawn nikde | **`done: false`** |
| `entity.player` | `done: true` | soubor v `main` **je** (71 řádků), ale `move()`, `add_item()`, `die()` v něm **nejsou** — a `economy.gd:39,47` je volá | **`done: false`** |
| `core.attributes` | bez `done` | `attributes.gd` (416 B) s `hodnota()` i `derived()` v `main` je; PR #19 (`738a77d`) | **`done: true`** |
| `entity.item` | bez `done` | `item.gd` (1111 B) s `use()`/`repair()`/`broken()` v `main` je; PR #20 (`f1e2899`) | **`done: true`** |

**`size_lines` doplněny u 5 granulí** — a **není to kosmetika:** naměřeno
2. 10. 2026, že `save.gd` (+91), `hud.gd` (+77) a `mining.gd` (+67) skončily
jako **visící PR**, protože granule velikost nedeklarovala a gate auto-merge
použil výchozích 60. Doplněné hodnoty jsou **změřené velikosti souborů v `main`**
(`splitlines()`): `world.level` 283 → `<= 300`, `sim.combat` 127 → `<= 130`,
`persist.save` 99 → `<= 100`, `ui.hud` 89 → `<= 100`, `sim.mining` 72 → `<= 80`.

> **⚠ „13 granulí bez `size_lines`" NENÍ vada a NEDOPLŇUJE SE.**
> `lint-roadmapa.py:104–110` to říká výslovně: `size_lines` mají jen granule
> pro **silný model** a u slabého je výchozích 60 **SPRÁVNĚ**. Plošné doplnění
> by o granulích tvrdilo něco, co neplatí. Po opravě zůstává **8 granulí bez
> `size_lines`** — a všechny jsou `model: any`.

**Vedlejší nález (doložený, ne opravený):** `lint-roadmapa.py` hlásí **14
problémů** — a **stejných 14 hlásil i před změnou** (ověřeno spuštěním téhož
nástroje nad zálohou). Změnilo se jen **složení**: `entity.player` a `world.map`
ubylo (už nelžou) a `core.attributes` s `entity.item` přibylo (pravdivé `done`
se konečně kontroluje). **Žádný problém jsem nezpůsobil ani neodstranil.**

**Nový nález o DAG (zapsán jako otevřený, neopravován):** granule
`entity.player` má v `depends_on` **`world.map`** — tedy závisí na granuli,
která je nově `done: false` a **nikdy hotová nebyla**. Conductor ji proto
nevydá. Naměřeno: `entity.player.api` čeká na `core.attributes, core.skills,
entity.item, world.level` → **všechny čtyři jsou `done: true`** → **vydat ji lze
hned**. Oprava `depends_on` u `entity.player` (vypustit `world.map`) je
rozhodnutí pro další session — sahá na DAG.

### 26.4 Úkol 4 — HYPOTÉZA Z §0 ZADÁNÍ: **NEPOTVRZENA**

| Co zadání tvrdilo | Naměřeno |
|---|---|
| „session bez nového měřidla → **0–2 omyly** místo 7,8" | **11 omylů** (§8n, id 113–123) |
| „protože není co zpackat" | **8 z 11** vzniklo v **měřidle nebo v postupu měření** |

**Hypotéza tedy padá** — a podle zadání je to **stejně cenné**: znamená to, že
**únava není z měřidel.** Session přitom **žádné nové měřidlo nepostavila**
(všechny nové soubory jsou **sondy k jedné otázce**, mimo CI i mimo
`validate-all.mjs`; jediná „brána" navíc je **kontrola uvnitř `run_tests.gd`**,
což je hra, ne proces).

**Co z toho plyne (a je to poučení, ne výmluva):** i **pomocná sonda k jedné
otázce je měřidlo** — a platí na ni tytéž pasti jako na bránu do CI. Tři
z těch osmi (`114`, `115`, `118`) přitom **vypadaly jako nález o kódu hry**
(„izometrie je vadná", „HUD je rozbitý", „HUD neukazuje HP") a **byly to vady
měření**. To je přesně týž podpis, jaký `AGENTS.md` popisuje u `S27`.

**Silnější závěr než „omylů je 7,8":** rozhoduje **postup**, ne druh práce.
Sonda, která měří PŘED a PO (jako `_sonda-pohyb.gd`), je sama sobě kontrolou —
a právě ona zachytila omyl `123`, tedy **změnu ovládání, kterou jsem já sám
považoval za neškodnou**.

### 26.5 VZHLED — ověřeno POHLEDEM (ne jen testy)

`AGENTS.md`: „vizuální změnu ověř pohledem (`read_image`), ne jen testy."
Snímek: **`_analyza\\a-snimek-hp.png`** (960×540), nástroj
`games\\uo-shadows\\tests\\_snimek-hp.gd`.

**Co je na snímku vidět:** vlevo nahoře `HP: 100`, `Str: 10  Dex: 10  Int: 10`,
`Dovednosti – tezba: 0, drevorubectvi: 0, kovarstvi: 0, boj: 0`, `Zlato: 0`,
`Vybaveno: —`; pod tím **izometrická mapa** z `assets/levels/main.json`.

**Naměřená mez, která se musí říct nahlas:** `scripts/game.gd` je **pořád
monolit** (granule `engine.shell` není hotová), takže komponentu `hud.gd`
**hra sama neinstancuje**. Snímek proto staví **skutečný `level.gd` + skutečný
`main.json` + skutečného hráče + skutečný `hud.gd`** nad zkušební registr.
Dokládá tedy **„HUD zobrazuje HP"**, **ne** „komponentní HUD je nasazen ve hře".
**Ve hře, kterou si uživatel zahraje, se `hud.gd` zatím neobjeví** — to je
práce granule `engine.shell`.

**A sonda při tom odhalila vlastní vadu (omyl 118):** první verze dala `hud.gd`
pod uzel **hráče**, kde `get_parent().component(id)` vrací `null` → **HP: 0**.
Snímek by tedy ukázal nulu jako hotovou věc. Zachytila to až kontrola
`prvni.contains("HP: %d" % hrac.hp)` — **ne oko**.

### 26.6 Co je hotové a co NE (stav ke konci session)

**Hotové a spuštěním doložené:** všechny 4 úkoly zadání; testy hry **89/0**;
sonda pohybu **6/0**; `_dukaz-assist.gd` **exit 0**; mutační test izometrie
**chyceno**; roadmapa srovnána (4 změny `done`, 5 `size_lines`); smlouva
v `ARCHITEKTURA.md` §2.2; snímek HUD s HP.

**NENÍ hotové (a patří do další session):**
- **Nic z toho není commitnuté ani pushnuté** — `git status` níž, čeká se na
  vyjádření uživatele.
- **`engine.shell`** — dokud nebude, komponentní `hud.gd` se ve hře neobjeví.
- **`world.nodes`**, **`persist.save.state`** — práce v `main` není.
- **`persist.save.state` má nový blokátor:** `save.gd:84` vyžaduje
  `"position" in hrac`; `player.gd` teď `position` MÁ (od `Area2D`), takže
  `load()` **přepíše spawn**. Musí se rozhodnout, kdo pozici vlastní.
- **`entity.enemy` / `monsters.json`** — zadání výslovně zakázalo zahrnout.
- **`entity.player` má v `depends_on` `world.map`** (viz §26.3) → nevydá se.
- **Opatření 3 a 6** z `ZADANI-DODELAT-MERIDLA.md` — zůstávají otevřená
  (zadání je z téhle session vyloučilo).

### 26.7 Co se NEDODRŽELO ze zadání (přiznaná mez)

- **„NEPOSTAV ANI JEDNO NOVÉ MĚŘIDLO"** — dodrženo v tom smyslu, že **nic
  nového nevstoupilo do CI ani do `validate-all.mjs`**; ale vznikly **4 pomocné
  sondy** (`_sonda-pohyb.gd`, `_snimek-hp.gd`, `_kostra-snimku.gd`,
  `_analyza\\a2-mutace-izo.py`) a **jedna kontrola v `run_tests.gd`**. Beru to
  jako **nedodržení ducha zadání** a je to přesně to, co vysvětluje §26.4.
- **„NEDOPLŇUJ seznamy v branách"** — dodrženo: nové soubory do pevného seznamu
  `kontrola-diakritiky.py` **přidány nebyly**; diakritika ověřena **ručně týmž
  vzorem** (13 souborů, `rozbito: ne` u všech).

"""


def main() -> int:
    if not HANDOFF.exists():
        print("CHYBA: %s neexistuje" % HANDOFF)
        return 2
    puvodni = HANDOFF.read_text(encoding="utf-8")
    if "### 8n. Omyly AKČNÍ session 3. 10. 2026" in puvodni:
        print("CHYBA: blok 8n uz v dokumentu je — nic se nezdvojuje")
        return 2
    if KOTVA not in puvodni:
        print("CHYBA: kotva pro vlozeni nenalezena")
        return 2
    if puvodni.count(KOTVA) != 1:
        print("CHYBA: kotva je v dokumentu %dx" % puvodni.count(KOTVA))
        return 2

    novy = puvodni.replace(KOTVA, OMYLY + KOTVA, 1)
    novy = novy.rstrip("\n") + "\n\n" + ODDIL_26
    HANDOFF.write_text(novy, encoding="utf-8", newline="")

    # Ověření PO ZÁPISU: text tam opravdu je (ne jen „soubor vznikl").
    zpet = HANDOFF.read_text(encoding="utf-8")
    for kont in ["### 8n. Omyly AKČNÍ session 3. 10. 2026",
                 "## 26. Provedeno 3. 10. 2026",
                 "113", "123", "_analyza\\a-snimek-hp.png",
                 "HYPOTÉZA Z §0 ZADÁNÍ: **NEPOTVRZENA**"]:
        assert kont in zpet, "po zapisu chybi: %s" % kont
    assert zpet.count("### 8n.") == 1, "blok 8n je tam vickrat"
    assert len(zpet) > len(puvodni), "dokument se nezvetsil"

    print("ZAPSANO do HANDOFF.md")
    print("  pred : %d znaku, %d radku" % (len(puvodni), len(puvodni.splitlines())))
    print("  po   : %d znaku, %d radku" % (len(zpet), len(zpet.splitlines())))
    print("  kotva 25. zustala na miste: %s" % ("ANO" if KOTVA in zpet else "NE"))
    return 0


if __name__ == "__main__":
    sys.exit(main())

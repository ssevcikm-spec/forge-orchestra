---
name: game-developer
description: "Metodika agentního vývoje her — rozpad shora dolů od cíle, přes architekturu a smlouvy (kontrakty), až po granule (atomické jednotky) s DAG závislostí, branami a ověřením proti cíli. Rozpadne hru na celistvé kousky, které zvládne i slabý model, aniž by vybočil z plánu, a které můžou agenti stavět paralelně. Velikost granule se řídí modelem — výchozích ≤ 60 řádků zvládne každý; větší soudržný celek smí jen silný model a musí být deklarovaný (size_lines/model v roadmapě)."
whenToUse: Když se navrhuje nová hra nebo milník; když se roadmapa rozpadá na úkoly pro orchestr/agenty; když agenti selhávají na závislostech (volají funkci, která ještě neexistuje), šlapou si na stejný soubor, nebo když uživatel chce projekt „granularizovat" na atomické celistvé kousky.
---

# Game Developer — agentní vývoj her

Metodika pro stavbu hry (zejména v Godotu) řízenou agentem/orchestrem.
Cíl: **každou granuli vezme jakýkoliv model a dokončí ji bez vybočení z plánu**,
a zároveň **agent může pracovat na více nezávislých granulech současně**.

## Zlaté pravidlo

```
Cíl → Požadavky → Architektura → Smlouvy → Granule → DAG → Brány → Ověření proti cíli
```

Všechno jde v tomhle pořadí — **shora dolů**, od jednoho cíle k malým kouskům,
a na konci zpátky k ověření, že celek stále plní cíl. Kdo přeskakuje úrovně
(např. píše granule bez smluv), dostane přesně ty chyby, které tahle metodika
odstraňuje.

---

## Proč to existuje (konkrétní selhání, která to řeší)

1. **Kaskáda závislostí** — úloha 70 volá `_zlepsi_skill()` z úlohy 69, ale
   orchestr ji zařadil dřív, než 69 existovala. Řešení: `depends_on` strojově,
   conductor nevydá granuli, dokud předchůdci nejsou sloučené.
2. **Konflikt o soubor** — 12 úloh sahá do jednoho `game.gd`. Řešení:
   1 granule = 1 soubor (`owns`), souběh jen s disjunktními `owns`.
3. **Drift agenta** — agent si vymyslí pole API, stav UI nebo chybový formát,
   protože to nebylo nikde zapsané. Řešení: smlouvy (kontrakty) jako zdroj pravdy.
4. **„Funguje to, ale nic nedělá"** — kód se zkompiluje a testy projdou, ale
   funkce není nikde volaná. Řešení: brány (check-wiring, check-assets).

---

## 0. Cíl první — rozpad shora dolů (top-down)

Nezačínej architekturou ani kódem. Začni **jedním cílem** a rozbíjej ho dolů,
krok po kroku, až jsou kousky „stravitelné" pro jednoho agenta.

1. **Cíl** — jedna věta: co hráč dělá a jaký je zážitek.
   _Př.: „Izometrický sandbox, kde každý předmět a čin mají důsledek
   a dovednosti rostou používáním."_
2. **Požadavky / mechaniky** — z cíle odvozené, co hra umí (sběr, těžba, kování,
   NPC, denní cyklus…).
3. **Schopnosti (capabilities)** — každý požadavek rozpadni na ověřitelné věty:
   „hráč vytěží rudu", „hráč vytaví ingot". Schopnost je to, co se dá otestovat.
4. **Systémy / komponenty** — schopnosti seskup do systémů (svět, simulace…),
   každá komponenta = jeden soubor.
5. **Granule** — každá schopnost se stane jednou nebo víc granulemi (§4).

**Pravidlo rozpadu:** každý krok je JEN rozbití předchozího na menší kousky.
Nic se nepřeskakuje a nic se nepřidává z kódu. Když se v kroku objeví něco, co
nemá předka o úroveň výš, je to **drift** — buď doplň cíl, nebo to zahoď.

**Stop, když** je kousek stravitelný: jeden soubor, ~60 řádků, jednoznačné
zadání, ověřitelný výsledek. To je granule. 60 řádků je výchozí míra **pro
slabý model** — kdy a jak smí granule tuhle míru přesáhnout, říká §4.1
(velikost granule se řídí modelem, ne naopak).

## 1. Architektura první

Nejdřív mapa celé hry — systémy a **směry závislostí** (kdo smí záviset na kom).
Piš ji vrstvově, ne jako seznam funkcí.

Příklad (izometrický sandbox):

| Vrstva | Odpovědnost | Příklad souborů |
|---|---|---|
| engine | běh, smyčka, vstup, okno | `main.tscn`, `scripts/game.gd` (jen kostra) |
| svět | mapa, dlaždice, izo projekce, průchodnost | `scripts/world.gd`, `scripts/level.gd` |
| entity | hráč, NPC, nepřátelé, předměty | `scripts/player.gd`, `scripts/npc.gd` |
| simulace | dovednosti, těžba, kování, denní cyklus | `scripts/skills.gd`, `scripts/crafting.gd` |
| prezentace | HUD, kamera, efekty | `scripts/hud.gd` |
| persistence | ukládání/načítání stavu | `scripts/save.gd` |
| nástroje | brány ověřující vzhled a zapojení | `.forge/check-*.py` |

Pravidlo závislosti: **shora dolů** (prezentace smí záviset na simulaci, ne naopak).
Kruhové závislosti = chyba architektury.

## 2. Smlouva první (contract-first)

Každá komponenta má **rozhraní**: co **poskytuje** (`provides`) a co **spotřebovává**
(`consumes`). Agent nesmí hádat názvy — bere je ze smlouvy.

```
provides:  Skills.add(skill: String, n: int) -> void
           Skills.get(skill: String) -> int
consumes:  HUD.update()   (po každé změně)
```

Zásada: **přes rozhraní, ne přes vnitřek** jiné komponenty. Agent volá jen
deklarované `provides`, nikdy nečte cizí privátní proměnné.

## 3. Testy jako spustitelná smlouva

Test je jediná věc, kterou orchestr i CI **věří bez přemýšlení**. Proto:

- Test píše **před** implementací (z kontraktu), ne po ní.
- Agent **nesmí měnit `tests/`** — testy jsou spec, ne cíl úprav.
- „Implementace prošla testy" nestačí — proto existují brány v §6.

### Failing-first v orchestrách s nepřetržitým CI

Když orchestr pracuje na hře kontinuálně, čisté failing-first (test selže,
dokud granule nedoběhne) by rozbilo CI na `main` uprostřed vlny a zablokovalo
auto-merge všech ostatních granulí. Proto se testy na granule píšou jako
**podmíněné**:

- kontrola se zapne sama, až artefakt granule v projektu JE (soubor existuje,
  uzel má metodu z kontraktu, ve zdroji je hledaný řetězec),
- kontroluje jen smluvní `provides` (přes `has_method`/`get`), nikdy soukromá
  pole — jinak by drobná implementační volba agenta shodila celou sadu,
- dokud granule neexistuje, kontrola se **přeskočí** a CI zůstává zelené;
  jakmile granule přistane, test začne platit okamžitě (na uo-shadows: 24 → 26
  kontrol bez jediného selhání uprostřed vlny).

Chybové hlášky „File not found" z podmíněného `load()` jsou součást vzoru,
ne vada — testy se díky nim nemusí párovat s vlnami ručně.

### Past: podmíněný test, který NIKDY nezapne, je tiše zelený

Podmíněnost má jednu zákeřnou podobu — když se kontrola ptá špatně, nezeptá se
„nesplněno", ale **pořád se přeskočí**, a to vypadá jako úspěch. Naměřeno
30. 9. 2026 na `uo-shadows`, granule `core.skills`:

```gdscript
# Test se ptá se DVĚMA argumenty, smlouva má jeden
var t0 = sk.get("tezba", 0)
```

Skript si definoval vlastní `get(skill: String)`, čímž přebil `Object.get()`.
Dovolat se s druhým argumentem = fatální chyba enginu → přeruší CELÝ běh testů →
běh visí do limitu → v logu je jen „testy se zasekly". Navíc `has_method("get")`
u skriptu bez vlastního `get()` kontrolu tiše přeskočilo, takže test byl zelený,
i když smlouva splněná nebyla. Granule se pak pokusila sloučit **5×** a pokaždé
to shodil test, ne model.

> **Naměřeno 1. 10. 2026 — kolik takových míst ta hra má:** v
> `games/uo-shadows/tests/run_tests.gd` je **27 podmíněných kontrol**
> (`if main.has_method(...)`, `if attrs.has_method("get") and ...`, …).
> To má dva důsledky, které je dobré znát **před** plánováním granulí:
>
> 1. **CI je zelené i bez implementovaných funkcí** — chybějící funkce se
>    přeskočí, ne ohlásí. Test tedy neříká „hra funguje", ale „co existuje,
>    funguje". Pro plánování to znamená: **hotová granule se nepozná podle
>    zelených testů, ale podle toho, že funkce existuje a je volaná.**
> 2. **Brána `check-wiring.py` tím ztrácí část síly** — hledá použití funkce
>    v celém repu **včetně `tests/`**, takže funkce zmíněná jen v podmíněném
>    testu se počítá jako „použitá", i když ji hra nikdy nezavolá.
>
> Praktické pravidlo: **u granulí, které mají něco zpřístupnit, trvej na
> nepodmíněné kontrole** (nebo na tom, že funkci volá produkční kód) —
> jinak máš zelenou, která nic neznamená.

Pravidla, která z toho plynou:

1. **Volej metody smlouvy přesně tak, jak jsou deklarované** — stejný počet
   argumentů. `get(skill: String)` se volá s jedním, ne s defaultem.
2. **Když metoda chybí nebo vrátí `null`, řekni to nahlas** (`print` s názvem
   granule). Tiché přeskočení je v pořádku jen dokud artefakt neexistuje;
   jakmile existuje, musí být vidět, že smlouva nesedí.
3. **Obecná jména (`get`, `set`) si nenechávej pro sebe** — přebijí engine
   a rozbijí i testy, které chtěly jen číst vlastnost. Použij konkrétní jméno
   (`hodnota`) nebo vlastnost samotnou.
4. **Soubor granule musí začít `extends Node`** a `class_name` nesmí být zároveň
   jménem vnořené `class` v témž souboru — vnořená třída přebije globální jméno,
   `new()` vrátí ji, smluvní metody „neexistují" a `free()` na RefCounted shodí
   běh testů.
5. **Pomocná funkce pro instanci granule** (jednou, ne v každém bloku):

```gdscript
func _instantiate(oblast: String, cesta: String):
    var sc = load(cesta)
    if sc == null:
        return null
    var obj = sc.new()
    if obj != null and not (obj is Node):
        print("[test]      %s: %s nevrací potomka Node, ale %s"
            % [oblast, cesta, obj.get_class()])
    return obj

func _zavri(obj) -> void:
    if obj is Node:
        obj.free()
    # Potomek RefCounted se uvolní sám; `free()` na něm vyhodí chybu
    # a přeruší CELÝ běh testů.
```

### Past: dvě jména téhož pole = tichá ztráta dat

**Naměřeno 1. 10. 2026 v projektu orchestra.** Šablona psala do konfiguračního
souboru klíč `popis_stylu`, ale kód `vision.mjs` četl **POUZE** `styl_popis`:

| Kdo | Jméno klíče |
|---|---|
| šablona (zápis) | `popis_stylu` |
| `vision.mjs` (čtení) | `styl_popis` |

Hra, která by použila nové jméno, by o svůj styl vizuální kontroly **tiše**
přišla — žádná chyba, žádné varování, jen kontroly, které běží bez stylu.
Rozdíl se neprojeví u zápisu, ale až u otázky „proč ta kontrola nefunguje?".

**Oprava:** kód čte **obě** jména (staré i nové) a **pro každé z nich existuje
test**. Obecné pravidlo:

> **Když měníš jméno klíče v konfiguraci, kód musí číst obě jména a pro každé
> musí existovat test** — jinak je přejmenování tichá ztráta dat.

**Navazující pravidlo: než z konfigurace něco SMAŽEŠ, najdi všechna místa, kde
se to čte.** Smazaný klíč, na který ještě někdo sahá, je tatáž tichá ztráta
z opačné strany — a hůř se hledá, protože po něm nezůstane ani stopa.

### Past: statická metrika, která nic nespustí, je slepá

**Naměřeno 1. 10. 2026.** Čtenář dokumentu chtěl ověřit tvrzení „testy 36/36"
a **staticky spočítal volání `test(` ve zdrojáku** → vyšlo **42**, tedy
„dokument lže". Po skutečném **SPUŠTĚNÍ** testů vyšlo **36/36** — dokument měl
pravdu do puntíku.

Počet testů nesedí na počet vzorů v souboru: testy se sdružují do skupin,
používají pomocné funkce a jiné názvy, než jaké vzor hledá.

| Metrika | Co naměřila | Závěr, který z toho plyne |
|---|---|---|
| spočítaná volání `test(` ve zdrojáku | **42** | „dokument lže" — špatný |
| výstup skutečného **běhu** testů | **36/36** | dokument měl pravdu |

> **Počet testů a výsledky se čtou z VÝSTUPU BĚHU, ne z počtu vzorů ve
> zdrojáku.**

Statická metrika je stejně slabá jako kontrola, která čte komentáře — a navíc
**svádí k „opravě" správného dokumentu**, což je horší než nic: správné číslo se
přepíše špatným a zmizí tím i důkaz.

**Platí to i pro ověřování cizích tvrzení.** Než něčí číslo označíš za
nepravdivé, **zopakuj ho TÝMŽ postupem, jakým vzniklo** — a když postup neznáš,
nemáš co vyvracet, jen jinou metriku, která odpovídá na jinou otázku.

## 4. Granule (atomická pracovní jednotka)

Granule = nejmenší kus práce, který je **sám o sobě celistvý** (smysluplný
výsledek) a **samostatně ověřitelný**. Schéma:

```json
{
  "id": "skills.core",
  "title": "Dovednosti — model a přičítání",
  "component": "sim/skills",
  "owns": ["scripts/skills.gd"],
  "depends_on": [],
  "provides": [{"name": "Skills.add", "sig": "add(skill: String, n: int) -> void"}],
  "consumes": ["HUD.update"],
  "acceptance": ["tests", "wiring"],
  "size_lines": "<= 60",
  "model": "any"
}
```

`size_lines` a `model` jsou volitelné — bez nich platí `<= 60` a `any`.
`done: true` = sloučená granule (orchestr ji přeskočí a počítá jako hotovou
i pro `depends_on` ostatních granulí — nezávisle na tom, jestli její PR ještě
vidí).

Pravidla granule:

1. **1 granule = 1 soubor** (výjimečně 2 úzce svázané). `owns` je výlučné —
   žádná jiná granule ve stejné vlně nesmí vlastnit stejný soubor.
2. **`depends_on`** = id granulí, které musejí být **sloučené** dřív.
3. **`provides`/`consumes`** = rozhraní, přes které se granule napojuje.
4. **`acceptance`** = jak se pozná hotovo (testy, wiring, assets, render).
5. **Prompt se generuje ze schématu**, nepíše se ručně — tak je konzistentní
   i pro slabý model. Ručně psané zadání v próze se rozjíždí (naměřeno).
6. **Změna existujícího souboru je aditivní** — granule smí přidávat
   `provides`, ale nesmí mazat stávající API, na kterém stojí testy nebo
   monolit, dokud nedoběhne integrační granule. Př.: `entity.player` zachovává
   `_step()`/`_physics_process`, dokud `engine.shell` nepřepojí scénu. Do
   promptu se to píše VÝSLOVNĚ („ZACHOVEJ …"), jinak i silný model funkční
   kód smaže a CI spadne mezi vlnami.

## 4.1 Velikost granule se řídí modelem (ne naopak)

60 řádků není dogma, ale **výchozí míra pro slabý model**. Někdy je soudržná
jednotka větší a rozsekání by vytvořilo **umělý šev** — např. stav entity +
pravidla smrti + inventář patří k sobě, a když je rozdělíš, agent lepí
polovičaté API, které stejně vyjde na víc řádků a víc chyb. Tehdy je správné
granuli zvětšit — ale jen za dvou podmínek:

1. **Dostatečně silný model** — granule deklaruje `"model": "strong"`
   a orchestr ji vydá jen silnému modelu. Slabému se nevydá, i kdyby fronta
   stála.
2. **Důvod je pojmenovaný umělý šev**, ne pocit — „nejde to rozsekat, aniž by
   se rozpadlo rozhraní", ne „agent to zvládne".

| model | rozsah granule | kdy |
|---|---|---|
| `any` (slabý/free) | 1 soubor, `<= 60` řádků | výchozí — zvládne ji jakýkoliv model |
| `strong` | 1 soubor, `<= 120–150` řádků | rozsekání vytvoří umělý šev |
| `strong` | výjimečně 2–3 úzce svázané soubory | vazba 1:1 (model + jeho data) |

Pravidla:

- **Velikost neurčuje model, ale soudržnost.** Model určuje jen to, kolik
  soudržnosti smí jedna granule nést. Jde-li kousek rozsekat bez umělého švu,
  rozseká se — i pro silný model.
- Granule nad ~60 řádků **musí** deklarovat `size_lines` a `model` v roadmapě.
  Bez deklarace platí `<= 60` a `any`.
- **Brány se řídí deklarací granule, ne globální konstantou.** Auto-merge limit
  „do 60 řádků" musí u granule s `size_lines > 60` použít její limit (nebo PR
  vědomě počká na lidské sloučení — a to je záměr, ne překvapení). Jinak velké
  granule systematicky visí v ruční frontě.
- **Protipožární pojistka:** silný model neomlouvá slabý rozpad. Když orchestr
  žádný silný model nemá (jen free rotace), granule s `model: strong` zůstávají
  ve frontě — a plán buď dostane silný model, nebo se granule přerozloží
  na `<= 60`.

## 5. DAG a vlny (paralelizace)

Granule tvoří **orientovaný acyklický graf** (DAG). Dvě granule můžou běžet
**současně**, právě když:

- obě mají všechny `depends_on` hotové **a**
- jejich `owns` množiny jsou **disjunktní** **a**
- nesdílí žádný soubor, do kterého obě píší (např. obě potřebují zaregistrovat
  se v `game.gd` — pak je potřeba zřetězit, nebo vyčlenit registraci).

„Vlna" = množina granulí, které můžou běžet naráz. Správně rozložená hra má
více nezávislých větví (simulace × prezentace × svět), ne jeden řetěz.

## 6. Brány (gates)

Automatické sloučení PR propustí jen práci, která projde **všemi** branami.
Brány vynucují smlouvy — „CI zelené" nestačí.

| Brána | Co hlídá | Nástroj |
|---|---|---|
| **schéma** (tvrdá) | **deklarace vs. skutečnost** — `spec.json`, mapy, vykreslování a dlaždice musí říkat totéž číslo | `.forge/check-schema.py` |
| testy | chování | `tests/run_tests.gd` (Godot headless) |
| zapojení | žádný mrtvý kód; `_on_*` připojené k signálu | `.forge/check-wiring.py` |
| assety | měřítko, díry, okraje, shoda siluet | `.forge/check-assets.py` |
| render | hra vykresluje mapu podle JSON | `.forge/verify-level-render.py` |
| běh | hra se spustí bez SCRIPT ERROR | smoke test |
| **vzhled (lidská)** | **obsah** — je to ta postava? sedí styl? není useknutá? | `read_image` (mimo CI), `.forge/vision.mjs` (v CI) |

**Schéma je tvrdá brána a je první, protože je nejlevnější.** Když si hra
odporuje v zadání (`spec.json` slibuje izometrii 96×48, ale `level.gd` kreslí
16px čtverce), nemá smysl měřit ani kreslit — všechno ostatní měří proti
něčemu jinému, než co je schválené. U `uo-shadows` se takhle rozešly **čtyři
zdroje pravdy** a nikdo si toho nevšiml, protože se to nikde neporovnávalo.
Autorita je **`assets/spec.json` té které hry** (ne globální konstanta —
side-scroller má jiné dlaždice než izometrie), nástroj v něm nesmí mít nic
zadrátované.

**Brány měří, ale nevidí.** `check-assets.py` pozná „mince je 0,67× truhly"
a „v truhle prosvítá díra" — nepozná ale „postavě chybí obličej" ani „ten meč
je z úplně jiné hry". Přesně tenhle rozdíl se podcenil u `uo-shadows`, kde
primitivní postava z Blenderu prošla všemi měřeními. Proto má tabulka poslední
řádek: **na obsah se musí někdo podívat**. V session to jde nástrojem
`read_image` (zdarma, okamžitě); v CI runneru `read_image` není, tam slouží
`.forge/vision.mjs` s klíčem Gemini.

**Pozor na falešný poplach:** u inkrementálního vývoje je funkce často „API pro
příští úlohu". Brána zapojení proto hlásí nepoužitou **veřejnou** funkci jako
poznámku, ne vadu; tvrdě kontroluje jen `_on_*` handlery.

**Statická kontrola musí číst KÓD, ne komentáře.** `check-schema.py` hledal
v `level.gd` starý chybný vzorec — a našel ho **ve vlastním komentáři**, který
ho citoval jako historii. Hlásil vadu i po opravě, takže nutil „opravovat"
správný kód. Řešení: komentáře se před hledáním vzorců odstraní
(`radek.split("#", 1)[0]`). Platí to pro každý statický lint: **text, který
vadu jen popisuje, nesmí vypadat jako vada.**

### Brána, která neproběhne, není brána

Nejdůležitější pravidlo celé metodiky: **u každé brány se ptej „proběhla
skutečně?", ne jen „neprotestovala?"**. Dva reálné případy z `uo-shadows`:

| Případ | Co se dělo |
|---|---|
| **Animace** | `check-assets.py` hledá `assets/sprites/walk_*.png`, kde je **0 souborů** — chůze je rozložená po vrstvách v `tools/blender/sprites/body_d0_f*.png`. Kontrola `min_silhouette_iou: 0.80` ze specu se tedy **nikdy neuplatní**, i když spec deklaruje `framy: 8`. Brána to poctivě napíše jako poznámku, ale kdyby se chůze rozbila, CI to nepozná. |
| **Výchozí měřítko** | `check-schema.py` hledal v `level.gd` vzorec `var cell := 16`. Po migraci na izometrii je v kódu `const CELL_W_DEFAULT := 96`, takže regexy nenašly nic, cyklus proběhl nad **prázdným seznamem** — a brána hlásila zelenou. Naměřeno 1. 10. 2026: `výchozí cell=[], fallback=[]`. |

**Nula a „nezměřeno" nejsou úspěch.** Když se nic nezměřilo, musí to být
vidět — vrať `None`/`NaN` a **pojmenuj to**. Prázdný seznam, který se tiše
proiteruje, je nejhorší varianta: vypadá jako naměřená nula.

**Praktická pravidla pro psaní brány:**

1. **Když kontrola nemá co měřit, řekne to** — vada, nebo aspoň poznámka.
   Nikdy ticho.
2. **Ptej se na jméno, ne na tvar.** Určovat osu (šířka/výška) křehkým
   regexem s lookaheadem se nevyplatilo; jméno deklarace (`CELL_H_DEFAULT`)
   je jednoznačné a dá se na něm testovat.
3. **Platí poslední deklarace.** Když soubor nese historii i dnešní stav,
   brát první výskyt znamená hlásit vadu i po opravě.
4. **Nefunkční metriku smazat, ne nechat ležet** — budí důvěru.
5. **Mrtvá větev je taky slepé místo.** Když soubor zmizí (u `uo-shadows` se
   při migraci smazal `world.gd`), větve, které na něj sahají, se už nikdy
   nespustí. Brána to má pojmenovat, ne mlčet.

**Jak si to ověřit (a je to povinné):** každá brána má mít **offline test se
známým správným i známým chybným případem**. „Prošlo to" bez toho neznamená
nic. Příklad, který se vyplatil: `orchestra/tools/test-check-schema.py` —
17 testů, které pouští bránu na záměrně rozbitá i správná repa. Když se psal,
**odhalil čtyři chyby ve vlastním regexu** (case sensitivity, záměna os,
první vs. poslední deklarace, `\b` po podtržítku) — tedy přesně to, co měl
hledat.

### Vizuální změna se neověřuje testy

Naměřeno 30. 9. 2026 při migraci `uo-shadows` na izometrii: **hráč nebyl na
obrazovce.** Dlaždice měly `z_index` od 0 výš a hráč má `+5`, takže ho
překryly. Přitom:

- testy hry: **zelené** (36 kontrol, 0 selhání)
- `check-schema.py`: **zelené**
- `check-assets.py`: **zelené**

Chybu našel až **pohled na snímek** (`read_image`). Poučení: u vizuální změny
je „testy prošly" slabý důkaz — testy ověřují logiku, ne to, co je vidět.
Ke každé vizuální změně patří snímek a podívat se na něj. Přesně proto
existuje vizuální vrstva (`read_image` v session, `.forge/vision.mjs` v CI).

## 7. Ověření proti cíli (uzavření smyčky)

Brány (§6) ověří **granuli**. Tahle vrstva ověří **celou hru proti cíli**.

1. **Stopovatelnost:** každá granule má předka — schopnost → požadavek → cíl.
   Piš tabulku `granule → schopnost → požadavek`. Žádná granule nesmí být
   „sama od sebe" a žádný požadavek nesmí zůstat bez granule. Tím se pozná,
   že rozpad je úplný a nic se neztratilo.
2. **Hratelná kontrola:** celá hra se spustí a dělá to, co říká cíl — ne jen
   „prošly testy". Uživatel dá známku 1–5.
3. **Zpětná smyčka:** když ověření najde nesoulad, opraví se NEJPRVE o úroveň
   výš (cíl / požadavek / smlouva), teprve pak granule. Jinak se kód a záměr
   rozjedou a drift se hromadí.

## Pravidla pro agenta (patří do CONVENTIONS/roadmapy)

1. **Neměň smlouvy tiše.** Když implementace odhalí díru, oprav nejdřív smlouvu
   a test, teprve pak kód.
2. **Piš jen do `owns`** své granule. Nikdy do `tests/`, `.github/`, `.forge/`,
   `project.godot`.
3. **Používej existující `provides`** — vymyšlený název = spálený pokus.
4. **Testy jsou spec.** Nepiš test, který jen zrcadlí implementaci.
5. **Granule je malá** (~60 řádků; výjimka je jen deklarovaná granule
   `model: strong` — viz §4.1). Velká změna bez téhle deklarace = granule je
   špatně rozložená.

## Mapování na orchestr (Forge orchestra)

- `roadmap.json` → DAG granulí (ne lineární seznam).
- conductor čte `depends_on`, vydává jen připravené granule, povoluje N
  souběžných větví, hlída `owns` (zámek souboru).
- conductor čte i `size_lines`/`model`: granule s `model: strong` jde do fronty
  silného modelu a brána auto-merge posuzuje velikost změny podle deklarace
  granule, ne podle jedné globální konstanty.
- Brány běží v CI na každém PR; bezpečné malé změny se slučují samy.
- **Závislosti nikdy do prózy** — vždy do `depends_on`. (Kaskáda dnes vznikla
  právě z toho, že závislost byla schovaná ve větě.)

## Hra v Godotu — konvence navíc

- GDScript je typovaný; `var x :=` s chybou typu oprav na `var x =`.
- Signály přes `connect(_on_x.bind(...))` — každý `_on_*` musí být připojený.
- Testy spouští `godot --headless --path . --script res://tests/run_tests.gd`.
- Izometrie 2:1: `screen = offset + Vector2((cx-cy)*cell/2, (cx+cy)*cell/4)`.
- **Jeden `game.gd` je brzda paralelizace** — rozpadni ho na komponenty
  (`skills.gd`, `mining.gd`, `crafting.gd`, `npc.gd`, `world.gd`…).

## Zdroje (současné standardy, 2026)

**Assety (grafika, hudba, zvuky, 3D, fonty) → skill `game-assets`** — tenhle
skill je o metodice kódu a rozpadu; kde vzít free asset nebo jak ho vygenerovat
(SDXL/Gemini/Blender) řeší samostatný skill, ať se to nemíchá.

- [ContractSpec — contract-first, test-driven, AI-safe workflow](https://github.com/Pluviobyte/ContractSpec) — smlouvy napříč vrstvami, „testy jsou spustitelná smlouva", brány (contract/binding/failing-test/implementation/verification).
- [Agent-first Driven Development (AFD)](https://zenodo.org/records/18649254) — bottom-up metodika pro věk AI agentů.
- [Design-First Governance for Reliable AI-Assisted Software Development (IEEE)](https://ieeexplore.ieee.org/document/11641193) — design-first jako zábrana proti driftu agentů.

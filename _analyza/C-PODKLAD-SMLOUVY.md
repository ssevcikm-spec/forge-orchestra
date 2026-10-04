# C — Podklad pro plánovací session (prototyp smlouvy + nedopsané kontrakty)

**Co tenhle dokument JE:** podklad pro session, která přepíše `games\uo-shadows\docs\ARCHITEKTURA.md`.
Je to **prototyp tvaru smlouvy** (na jednom skutečném případu — `Player`) a **seznam
naměřených rozporů**, které ta smlouva musí vyřešit.

**Co NENÍ:** zadání ani záznam o provedení; a **NENÍ to přepis designu** (ten dělá až
plánovací session). Není to ani návrh nové architektury — jen měření dnešního stavu.

**Datum a čas měření:** 2. 10. 2026, **09:20–09:31 UTC** (lokální čas stanice 11:20–11:31).

**Naměřeno session, která byla podagent** (delegovaná session `C2`, rodičovská session
`session-84bb93e1`). **V této session jsem needitoval žádný kód ani dokument hry** —
zapsán byl jediný soubor, tenhle (`_analyza\C-PODKLAD-SMLOUVY.md`). Godot jsem nespouštěl,
`save.cfg` jsem neměnil, necommitoval ani nepushoval.

**Jak číst značky v tomhle dokumentu:**

| Značka | Znamená |
|---|---|
| *(měřeno)* | Přečetl jsem soubor/blob nebo spustil příkaz — příkaz je v §5 |
| *(odvozeno z měření)* | Přímý důsledek přečteného kódu; **nespouštěl jsem to** (Godot jsem nesměl pustit) |
| **(názor, ne měření)** | Návrh nebo úsudek, který z měření nevyplývá |

**Kontrolní souřadnice, ke kterým se celý dokument vztahuje** *(měřeno)*:

- `games\uo-shadows` je na commitu `aad1c8d96743a243b9796b71c18791c5215bea56`,
  `HEAD == origin/main`, `git status --porcelain` **prázdný** → **pracovní strom = `main`**
  (proto je čtení z disku totéž jako čtení z `main`).
- `docs\ARCHITEKTURA.md` = **247 řádků**, `.forge\roadmap.json` = **245 řádků, 21 granul**
  (`done: 11`, `model: strong: 8`, `bez size_lines: 13`).

---

## 1. Prototyp smlouvy (Player)

**Proč zrovna Player:** je to jediná komponenta, u které je **měřitelné, že smlouva byla
jméno bez obsahu** — jiné komponenty její API **už volají**, ale v `main` neexistuje
(§3.2). Zároveň je to případ, kde je dnes **vlastnictví souboru rozdělené mezi dvě granule**.

**Soubor:** `scripts/player.gd` — **dnes 71 řádků, blob 2353 B v `origin/main`** *(měřeno)*.
**Předek:** `extends Area2D` (`player.gd:1`) — **ne `Node`**; na tuhle vlastnost se váže
chování scény (`game.gd:267–283` skript věší na `Area2D` uzel) *(měřeno)*.
**Dnešní obsah celý (nic víc tam není):** `signal collected(what: String)` (`:8`),
`const SPEED := 130.0` (`:10`), `var velocity` (`:12`), `var level: Node2D` (`:13`),
`_ready()` (`:16`), `_physics_process(delta)` (`:28`), `_step(target) -> Vector2` (`:54`),
`flash()` (`:67`).

### 1.1 Vlastnosti

Sloupec „čte" = **kdo to dnes v `main` skutečně čte** (soubor:řádek) *(měřeno)*.
Sloupec „v `main`" = existuje ta vlastnost v blobu `origin/main:scripts/player.gd`?

| Vlastnost | Typ (návrh) | Výchozí (návrh) | Kdo to čte dnes | V `main`? |
|---|---|---|---|---|
| `hp` | `int` | ? — **viz otázka O1** | `assist.gd:11`, `hud.gd:42–43` (a přes `get_hp()` `hud.gd:40–41`) | **NE** |
| `max_hp` | `int` | ? — **viz otázka O1** | `assist.gd:11` | **NE** |
| `mana` | `int` | `Int` z `attributes.derived()["mana"]` (`attributes.gd:19`) | `assist.gd:13` | **NE** |
| `max_mana` | `int` | ? — **viz otázka O1** | `assist.gd:13` | **NE** |
| `target` | `Node` nebo `null` | `null` | `assist.gd:15` (`player.target.hp <= 0`) | **NE** |
| `inventory` | `Array` | `[]` | `economy.gd:39,47` nepřímo (volá metody); `save.gd:14` (komentář: uložit nelze) | **NE** |
| `equipped` | `Node`/`GameItem` nebo `null` | `null` | `hud.gd:46–47` (a přes `get_equipped()` `hud.gd:44–45`) | **NE** |
| `position` | `Vector2` | z `Area2D` | `save.gd:52–53,84–85`, `tests\run_tests.gd:186,210,211,510` | ano (dědí se) |
| `velocity` | `Vector2` | `Vector2.ZERO` | **nikdo mimo soubor** *(měřeno: 4 výskyty, všechny v `player.gd` `:12,44,46,47`)* | ano |
| `level` | `Node2D` | `null` | jen sám `player.gd:40,57` | ano |

**Zdroj každého řádku:** typy a jména **nejsou v designu ani v roadmape** — jediný zdroj
je **kód volajícího** (např. `assist.gd:11` je jediné místo, které řekne, že `max_hp`
existuje a že se násobí `0.3`). To je jádro nálezu: **kdo smlouvu píše, musí ji číst
z volajících, ne z designu** — protože v designu jsou jen jména (§4, bod 1).

**Otázka O1 (k plánovací session):** `attributes.gd:14–20` (`derived()`) vrací `mana`,
`carry`, `damage`, `hit_chance`, `attack_speed` — ale **`max_hp` nemá v projektu žádný
zdroj** *(měřeno: `derived()` je jediná funkce s odvozenými staty a `max_hp` v ní není)*.
Buď ho má vlastnit `Player`, nebo se musí doplnit do `derived()`. **Rozhodnutí patří do
designu; dnes ho neudělal nikdo** *(měřeno: v `ARCHITEKTURA.md` se `max_hp` nevyskytuje
ani jednou)*.

**Past na tichý výsledek** *(odvozeno z měření)*: `assist.gd:11` počítá
`player.hp < player.max_hp * 0.3`. Když bude `max_hp == 0`, výraz je `hp < 0` → **nikdy
nepravda** → asistence neudělá nic a **nic neohlásí**. Smlouva proto musí říct
**rozsah** (`max_hp >= 1`), ne jen typ.

### 1.2 Metody

| Signatura | Co dělá | Co vrací v chybovém stavu | Kdo ji volá |
|---|---|---|---|
| `move(dir: Vector2) -> void` | posun hráče o `dir` | nic (void) | **dnes NIKDO** *(měřeno plošným skenem: volání `.move(` = **0 výskytů** v celém repu; jediný výskyt slova je `has_method("move")` v `tests\run_tests.gd:836`)* → prvním volajícím bude `engine.shell` (`roadmap.json:209`) |
| `add_item(item) -> void` | vloží předmět do inventáře | — | `economy.gd:39` (`buy()`) |
| `remove_item(item) -> void` | odebere předmět z inventáře | — | `economy.gd:47` (`sell()`) |
| `die() -> void` | mrtvola s předměty z těla, hráč ke spawnu | — | **dnes NIKDO** *(měřeno: `die(` má v celém repu 4 výskyty — `roadmap.json:86,90,231` a `ARCHITEKTURA.md:134`; v `scripts\` ani `tests\` **ani jeden**)* |
| `get_hp() -> int` *(nepovinné)* | alternativa ke `hp` | — | `hud.gd:40–41` — **jen když metoda existuje**, jinak `hud.gd:42` sáhne na `hp` |
| `get_equipped()` *(nepovinné)* | alternativa ke `equipped` | — | `hud.gd:44–45` |
| `_step(target: Vector2) -> Vector2` | posun se zdí (klouzání) | `position` (když ani jedna osa nejde), `target` (bez levelu) | **`tests\run_tests.gd:211` — volá se PŘÍMO** |
| `flash() -> void` | bliknutí po zásahu | — | *nikdo v `main`* (API pro `engine.shell`) |
| `_physics_process(delta: float)` | pohyb z kláves (dnes jediná reálná cesta pohybu) | — | **engine Godot** |

**Typová past, kterou smlouva musí vyřešit** *(odvozeno z měření)*: `move()` se má podle
`roadmap.json:90` počítat „přes `world.iso_position` (2:1, **ne volá level**)", ale
`roadmap.json:231` (`entity.player.api`) říká „izometrické osy ber **z levelu**" a
`tests\run_tests.gd:838–840` **zakazuje** řetězce `level.iso_position` i
`level.has_method("iso_position")`. Naměřená realita: **`scripts/level.gd` žádné
`iso_position` nemá** (má `cell_center:146`, `cell_at:156`, `is_walkable_at:237`) a
`iso_position` existuje **jen v `_retired/world.gd:19`** *(měřeno)*.
→ **Větev `player.gd:40–44` je dnes MRTVÁ** *(odvozeno z měření: `level` je uzel se
skriptem `level.gd` — `game.gd:155–161` — a ten `iso_position` neumí, takže
`level.has_method("iso_position")` je vždy `false` a pohyb jde vždy větví `:45–46`)*.
→ A **`player.gd:40` obsahuje doslova zakázaný řetězec** `level.has_method("iso_position")`.
Jakmile granule dodá `move()`, test na `run_tests.gd:836` se **zapne** a **spadne na
dnešním řádku 40** *(odvozeno z měření — textový `contains`, ne sémantika)*.
**To je nejcennější jednotlivý nález v téhle sekci: granule, která jen přidá `move()`,
rozsvítí test, který na stávajícím kódu selže.**

### 1.3 Přijímací kritérium (návrh; **(názor, ne měření)** — v této session nespouštěno)

**Pravidlo, ze kterého kritérium vychází:** kritérium **NESMÍ být „metoda existuje"** —
musí **kód zavolat a ověřit výsledek**. Živý doklad, že to projekt už jednou udělal
špatně, je v jeho vlastních testech: `tests\run_tests.gd:836` je
`if player != null and player.has_method("move"):` — **dokud `move()` není, kontrola se
tiše přeskočí** *(měřeno)*. A `hud.gd:8–9` to přiznává slovem: „testy to nepoznaly, protože
volají jen `has_method("update")`" *(měřeno)*.

**Čím se spouští** *(měřeno v `games\uo-shadows\.github\workflows\ci.yml`)*:

| Jméno v `acceptance` | Skutečný příkaz | Řádek |
|---|---|---|
| `tests` | `timeout 150 "$FORGE_GODOT" --headless --path . --script res://tests/run_tests.gd` | `ci.yml:74` |
| `wiring` | `python3 .forge/check-wiring.py .` | `ci.yml:94` |
| `assets` | `python3 .forge/check-assets.py .` | `ci.yml:86` |
| `render` | `xvfb-run -a "$FORGE_GODOT" … --write-movie …` + `verify-level-render.py` | `ci.yml:125,135` |

**Pozor — `wiring` tuhle smlouvu neověří** *(měřeno: `check-wiring.py` neobsahuje ani
jeden výskyt `player`/`Player`/`has_method`; kontroluje jen, že každá **funkce** je
odněkud volaná, a nepoužité funkce hlásí jako **poznámku**, `check-wiring.py:117–127`)*.
Chybějící vlastnost (`hp`) tedy **žádná dnešní brána nechytí** — musí to udělat `tests`.

**K1 — stav postavy (co volá `assist.gd`):**

```gdscript
var p = _instantiate("player", "res://scripts/player.gd")   # vzor: run_tests.gd:576
var a = _instantiate("assist", "res://scripts/assist.gd")
a.add_rule("hp < X", "vypij lektvar")
p.max_hp = 100
p.hp = 20
_check(a.evaluate(p) == ["vypij lektvar"], "assist spustí pravidlo při hp < 30 % (dostal %s)" % str(a.evaluate(p)))
```
**Negativní případ (musí být v testu taky):**
```gdscript
p.hp = 90
_check(a.evaluate(p).is_empty(), "assist NESPUSTÍ pravidlo při hp 90 %")
a.add_rule("target dead", "prepni cil")
p.target = null
_check(a.evaluate(p).is_empty(), "s target == null se 'target dead' nesmí spustit")
p.target = _nepritel_s_hp(0)     # uzel s hp <= 0
p.hp = 90
_check(a.evaluate(p) == ["prepni cil"], "'target dead' se spustí, jen když cíl existuje a má hp <= 0")
```
Proč přesně takhle *(měřeno)*: `assist.gd:15` je `player.target != null and
player.target.hp <= 0` — obojí je součástí kritéria; test, který ověří jen první
půlku, projde i s implementací, která čte `target.hp` bez kontroly na `null`.

**K2 — inventář (co volá `economy.gd`):**
```gdscript
var e = _instantiate("economy", "res://scripts/economy.gd")
var it = _instantiate("item", "res://scripts/item.gd")
p.inventory = []
e.set("_gold", 1000)
e.buy(p, it)
_check(p.inventory.has(it), "buy() vloží předmět do inventáře hráče")
e.sell(p, it)
_check(not p.inventory.has(it), "sell() předmět z inventáře odebere")
```
**Negativní případ:** `e.sell(p, it)` s předmětem, který hráč **nemá**, nesmí spadnout
ani inventář změnit; `e.buy(p, it)` s `_gold = 0` nesmí předmět přidat (dnes jen
`push_error`, `economy.gd:41` — *(měřeno)*; testy hlásí `push_error` jako selhání
v Godotu, ale **jen když se skutečně spustí**).

**K3 — pohyb a zachování `_step`:**
```gdscript
var p2 = _instantiate("player", "res://scripts/player.gd")
var start: Vector2 = p2.position
p2.move(Vector2(1, 0))
_check(p2.position != start, "move() skutečně posunul hráče (před %s, po %s)" % [str(start), str(p2.position)])
_check(p2._step(Vector2(9999, 9999)) is Vector2, "_step() zůstal volatelný a vrací Vector2")
```
Proč: `_step` volá **přímo test** (`run_tests.gd:211`) a **musí zůstat beze změny** —
proto se v kritériu **zavolá**, ne jen zkontroluje.
`move()` **bez levelu** (žádný uzel ve skupině `level`) nesmí spadnout — dnešní chování
`_step` je `return target` (`player.gd:57–58`) *(měřeno)*.

**K4 — smrt a mrtvola:**
```gdscript
# POZOR: musí běžet nad uzlom v STROMĚ (main), protože die() přidává mrtvolu jako uzel.
p.inventory = [it]
p.die()
_check(p.get_tree().get_nodes_in_group("corpse").size() == 1, "die() vytvořilo právě jednu mrtvolu")
_check(p.inventory.is_empty(), "hráč po smrti přišel o vše na těle")
```
**Negativní případ:** druhé volání `die()` **nesmí** vytvořit druhou mrtvolu a nesmí
spadnout. Jméno skupiny `corpse` **není v designu** — je jen v roadmape
(`roadmap.json:231`) *(měřeno)*; design zná jen „mrtvola" (`ARCHITEKTURA.md:52,134`).

**K5 — kritérium na to, že se kritéria nevynechávají** *(návrh)*: přepsat
`run_tests.gd:836` z `if player != null and player.has_method("move"):` na
**podmínku bez `if`** (kontrola se musí spustit vždy) a **odstranit zakázaný řetězec
z `player.gd:40`** (jinak nový test spadne na starém kódu).
**(názor, ne měření):** tenhle krok patří do **téže granule** jako `move()` — jinak vznikne
PR, který rozsvítí červený test.

### 1.4 Co NESMÍ (hranice granule)

1. **NESMÍ měnit `tests/`, `.forge/`, `.github/`, `project.godot`** — zakázáno dvakrát:
   v pravidlech roadmapy (`roadmap.json:8`) i v promptu granule (`roadmap.json:231`), a
   **vynuceno bránou**: `agent.yml:637` takový PR odmítne (`!! chráněný soubor`).
   **⚠ To je naměřený rozpor, který musí plánovací session vyřešit:** `acceptance`
   u `entity.player.api` je `["tests","wiring"]` (`roadmap.json:230`), ale **agent
   nesmí sáhnout na `tests/`**. Kdo tedy napíše ten test?
   **(názor, ne měření):** buď se má test psát do `owns`, nebo má acceptance `tests`
   znamenat „test už v repu je a musí projít", a pak **musí existovat před granuli**.
2. **NESMÍ předělat `_physics_process` na něco jiného** — dokud `game.gd` nepředá pohyb
   `move()`, je to **jediná cesta, jak se hráč hýbe** (design to říká sám,
   `ARCHITEKTURA.md:213–215`).
3. **NESMÍ změnit `extends Area2D`** — `game.gd:267–283` věší skript na `Area2D` a
   připojuje `CollisionShape2D`; `player.gd:16–22` ho vytváří sám *(měřeno)*.
4. **NESMÍ odebrat `add_to_group("player")`** (`player.gd:17`) — čte ho `game.gd:143`
   při úklidu scény mezi úrovněmi *(měřeno)*.
5. **NESMÍ si přivlastnit soubor, který vlastní jiná granule.** Naměřeno lintem
   (`lint-roadmapa.py:66`): `scripts/player.gd` vlastní **`entity.player` i
   `entity.player.api`**, a **`entity.player` je v D1 `done`** — tedy souběh
   „hotové" a „čekající" granule nad jedním souborem.
6. **NESMÍ číst cizí vnitřek** — služby se berou z registru rodiče
   (`get_parent().component(id)`, vzor `mining.gd:67–72`, `hud.gd:81–89`,
   `save.gd:94–99`) *(měřeno)*; „nikdy z `/root/`" (`roadmap.json:231`), protože
   projekt **nemá ani jeden autoload** (`mining.gd:6–8`) *(měřeno tvrzením v kódu;
   `project.godot` v `main` jsem neotvíral)*.

---

## 2. Granule bez `size_lines`

**Zdroj jmen:** spuštění `python orchestra\tools\lint-roadmapa.py games\uo-shadows`
(2. 10. 2026, `$env:PYTHONIOENCODING='utf-8'`) — sekce
`=== GRANULE BEZ 'size_lines' (platí výchozích 60 řádků) ===`, řádek
`13 z 21: data.content, core.attributes, core.skills, world.level, world.map,
entity.item, sim.combat, sim.mining, sim.economy, entity.npc, sim.assist, persist.save, ui.hud`
*(měřeno; jména jsem opsal z výstupu, ne ze zadání)*.

**Počet řádků** = počet řádků **blobu** v `origin/main` (Python `splitlines()` nad
`git show origin/main:<cesta>` — **ne** `Measure-Object -Line`, která nedopočítá
poslední řádek bez koncového newline).

| id | soubor(y) v `owns` | řádků v `main` | `model: strong` | `done`? |
|---|---|---|---|---|
| `data.content` | `assets/data/materials.json`<br>`skills.json`<br>`recipes.json`<br>`monsters.json`<br>`items.json` | 22<br>18<br>33<br>11<br>14 — **celkem 98** | **nemá** | **ano** (PR #14) |
| `core.attributes` | `scripts/attributes.gd` | 21 | **nemá** | ne |
| `core.skills` | `scripts/skills.gd` | 15 | **nemá** | **ano** |
| `world.level` | `scripts/level.gd` | **283** | **nemá** | **ano** |
| `world.map` | `scripts/world.gd` | **V `MAIN` NENÍ** (git exit 128); `_retired/world.gd` = 47 | **nemá** | **ano** |
| `entity.item` | `scripts/item.gd` | 39 | **nemá** | ne |
| `sim.combat` | `scripts/combat.gd` | 29 | **nemá** | **ano** |
| `sim.mining` | `scripts/mining.gd` | 72 | **nemá** | **ano** |
| `sim.economy` | `scripts/economy.gd` | 47 | **nemá** | **ano** |
| `entity.npc` | `scripts/npc.gd` | **V `MAIN` NENÍ** (git exit 128) | **nemá** | ne |
| `sim.assist` | `scripts/assist.gd` | 17 | **nemá** | **ano** |
| `persist.save` | `scripts/save.gd` | 99 | **nemá** | **ano** |
| `ui.hud` | `scripts/hud.gd` | 89 | **nemá** | **ano** |

**Doplňující měření k téže tabulce:**

- **`model: strong` nemá ani jedna z těch 13** *(měřeno: filtr
  `model == "strong" and not size_lines` → prázdný seznam; `strong` má v roadmape všech
  8 granulí a **všechny** mají `size_lines`)*.
- **10 z těch 13 je `done`** *(měřeno z `roadmap.json`)*.
- **4 ze 13 souborů už dnes přesahují výchozích 60 řádků**: `level.gd` 283,
  `save.gd` 99, `hud.gd` 89, `mining.gd` 72 *(měřeno)*.
- **Design tvrdí totéž číslo, ale z jiného důvodu:** `ARCHITEKTURA.md:178` píše
  „Ostatních 13 granulí zůstává na `<= 60` — zvládne je slabý model" *(měřeno)*.

**Co z toho plyne pro plánovací session (jedna věta):**
`size_lines` **není** popis velikosti souboru, ale **limit velikosti ZMĚNY** — brána
počítá `add + del` proti `inputs.max_lines` (`agent.yml:646`), který conductor bere
z `grain.size_lines` a bez deklarace dosadí **60** (`conductor\src\index.ts:182–188,741`)
*(měřeno)* — takže **deklarace chybí přesně tam, kde je dnes soubor největší**
(`level.gd` 283 řádků), a každá budoucí granule nad ním **spadne do ruční fronty
a nikdo se to předem nedozví**; plánovací session musí buď doplnit `size_lines`/`model`
podle **očekávané změny**, nebo přiznat, že u těch granulí bude ruční schvalování
(a to napsat do designu, protože dnes to tam není).

---

## 3. Dva naměřené případy

### 3.1 `world.gd` se PŘESUNUL, ale historie to hlásí jako smazání

**Co jsem spustil a co to vrátilo** *(měřeno)*:

| Příkaz | Výsledek |
|---|---|
| `git show --stat -M c651368` | řádek `{scripts => _retired}/world.gd \| 0` — **přesun, 0 změněných řádků** |
| `git log --oneline --diff-filter=D -- scripts/world.gd` | `c651368 forge: izometricka migrace + oprava brany schematu` |
| `git cat-file -e origin/main:scripts/world.gd` | `fatal: path 'scripts/world.gd' does not exist in origin/main` (**exit 128**) |
| `git show origin/main:_retired/world.gd` | **47 řádků**, blob **1597 B**; na disku také **1597 B** |
| `Test-Path games\uo-shadows\_retired\world.gd` | `True` |

**Co v tom přesunutém souboru je** *(měřeno čtením `_retired/world.gd`)*: `iso_position()`
(`:19`), `cell_at()` (`:22`), `gather(cell) -> bool` (`:27`), `_respawn_resource()` (`:39`),
`is_walkable(pos) -> bool` (`:42`), `RESPAWN_TIME = 60.0` (`:4`) — tedy **přesně to, co
roadmapa po granuli `world.nodes` žádá** (`roadmap.json:220`), včetně odpovědi „pro to
samé pole podruhé vrátí `false`" (`:29–37`).

**Kde už to v repu stojí špatně** *(měřeno)* — chybná věta je **zapsaná v kódu** jako
komentář, ne jen v dokumentaci:

- `scripts\mining.gd:7–8`: „…a `scripts/world.gd` byl navíc **smazán** při izometrické
  migraci (c651368)".
- `scripts\save.gd:15–16`: „…a `scripts/world.gd` v repu **není** (**smazán** při izometrické
  migraci, commit c651368)".

**Co z toho plyne pro plánování** **(názor, ne měření):** kdo plánuje podle „smazáno",
**plánuje znovu vynalézat hotové** — a v tomhle případě to není hypotéza: granule
`world.nodes` (`roadmap.json:212–221`) je dnes `queued` a její zadání je **napsat znovu
soubor, který v repu leží** (jen v `_retired/`) *(měřeno: `roadmap.json:215` ji vlastní
`scripts/world.gd` + `assets/levels/main.json`; D1 ji hlásí `queued`)*.
**Pravidlo pro design:** u každého „smazaného" souboru se design musí ptát
**`git show --stat -M`, ne `--diff-filter=D`** — a vůbec poprvé se ptát, **jestli kód
neleží v `_retired/`**.

### 3.2 `done` je tvrzení, ne důkaz

**Dvě nezávislá měření téhož dne** (roadmapa je soubor v repu, D1 je živý stav orchestra):

| Zdroj | `entity.player` | `world.map` |
|---|---|---|
| `roadmap.json:85–86` / `:65–66` | `"done": true`, `done_note` s odkazem na **PR #25** | `"done": true`, `done_note`: „kód je v `_retired/world.gd`… práce v main není" |
| **D1 živě** (endpoint `/roadmap`, 2. 10. 2026 09:27 UTC) | `done`, `task=done` | `done`, `task=done` |

**A co je v repu** *(měřeno)*:

- `git show --stat e4be7c2` (commit `forge: Hráč — pohyb, inventář, smrt (mrtvola) (#25)`,
  1. 10. 2026) → **`1 file changed, 4 insertions(+)` — a tím souborem je `project.godot`**.
  Ty 4 řádky jsou `[input]` + `input_devices=PackedStringArray("keyboard", "mouse")` —
  **nic o pohybu, inventáři ani smrti**.
- `git log --all -S"func move("` → **prázdný výstup** (napříč všemi refs).
- `git show origin/main:scripts/player.gd` → 71 řádků, **`hp`, `max_hp`, `mana`,
  `max_mana`, `target`, `inventory`, `add_item`, `remove_item`, `die`, `equipped`,
  `move` se v něm nevyskytují ani jednou**.

**Čím se to ověřuje (odpověď na otázku ze zadání):**
**najdi soubor v `main` a ZAVOLEJ to, co od něj jiné komponenty volají.**
Konkrétně u `Player` to znamená tři kroky *(měřeno, třetí krok jsem spustit nesměl)*:

1. **Najdi volající:** `assist.gd:11,13,15` (čte `hp`/`max_hp`/`mana`/`max_mana`/`target`),
   `economy.gd:39,47` (volá `add_item`/`remove_item`), `hud.gd:40–47`, `save.gd:52,84`.
2. **Najdi soubor v `main`:** `git cat-file -e origin/main:scripts/player.gd` → **exit 0**
   (soubor je tam — což je přesně past: *soubor existuje a je „hotovo"*).
3. **Zavolej to:** `assist.evaluate(player)` nad hráčem z `main`
   **(odvozeno z měření, nespouštěno):** `assist.gd:11` sahá na `player.hp`; `player.gd`
   vlastnost `hp` **nedeklaruje** → hlášení „Invalid get index 'hp'" a další komponenty
   se nedostanou ke slovu. **Neznamená to „něco chybí" — znamená to „smlouva je jméno
   bez obsahu" a ověří se to jen spuštěním.**

**Třetí doklad téhož druhu, který jsem našel mimochodem** *(měřeno čtením; **nespouštěno**)*:
`scripts\combat.gd` je `done` (PR #26) a na `:19` a `:25` volá `attacker.has("zbran")`
a `defender.has("armor_rating")`. Podle měření zapsaného v `mining.gd:10–13` **`Object.has()`
v Godotu 4 neexistuje** (je to Godot 3 API) — a `mining.gd` na tom 2. 10. 2026 **skutečně
spadlo**. **(názor, ne měření):** `combat.resolve()` proto pravděpodobně spadne dřív, než
se dostane k poškození — a **žádný test to nevidí**, protože testy kontrolují jen
`has_method("resolve")`. **Nespouštěl jsem to** (Godot jsem v této session nesměl pustit);
uvádím to jako **stopu k ověření**, ne jako nález.

---

## 4. Co v designu chybí (seznam k dopsání)

Všechno níže je **měřeno** proti `games\uo-shadows\docs\ARCHITEKTURA.md` (247 řádků).

| # | Co chybí | Doklad |
|---|---|---|
| 1 | **Slovo `acceptance` se v designu nevyskytuje ani jednou** (0×), přitom roadmapa ho má u **všech 21** granulí. Design neříká, čím se „hotovo" ověřuje | `ARCHITEKTURA.md`: 0 výskytů; `roadmap.json`: 22 výskytů (1× popis, 21× granule) |
| 2 | **Smlouvy jsou jména bez typů, výchozích hodnot a volajících.** Řádek Hráče je `move()`, „inventář", `die()` (mrtvola) — bez typu parametru, bez návratové hodnoty, bez toho, kdo to volá | `ARCHITEKTURA.md:134`; chybějící typy doloženy §1.1–1.2 (jediný zdroj je kód volajícího) |
| 3 | **Design neuvádí ani jednoho volajícího** kteréhokoli API | `ARCHITEKTURA.md:126–145` (tabulka má jen „poskytuje/spotřebovává"); `move()` má v repu **0 volajících** |
| 4 | **Řádek „Svět" odkazuje na API, které v tom souboru není**: design slibuje `iso_position(cx,cy)`, `cell_at(pos)` u `scripts/world.gd` | `ARCHITEKTURA.md:132`; `iso_position` je **jen** v `_retired/world.gd:19`; `scripts/world.gd` v `main` **není** (exit 128) |
| 5 | **Design tvrdí `get(attr)` u Atributů** — ale `attributes.gd` žádné `get()` nemá (má `hodnota()`), a roadmapa **definici `get()` výslovně zakazuje** (koliduje s `Object.get`) | `ARCHITEKTURA.md:129` vs. `attributes.gd:7` a `roadmap.json:35,46` |
| 6 | **Design je o 3 granule pozadu**: zná 18 granulí, roadmapa má 21 | `ARCHITEKTURA.md:180–197` (18 položek), `:234` („18 granulí v 6 vlnách"); `roadmap.json` = 21; chybí `world.nodes`, `entity.player.api`, `persist.save.state` (`roadmap.json:212–243`) |
| 7 | **Tvrzení „zbylých 13 zvládne slabý model" je nepodložené u 4 z nich** — soubory už dnes mají 283 / 99 / 89 / 72 řádků | `ARCHITEKTURA.md:178` vs. bloby `level.gd`, `save.gd`, `hud.gd`, `mining.gd` |
| 8 | **Design neříká, kde se bere `hp`/`max_hp`/`mana`/`max_mana`.** `attributes.derived()` obsahuje jen `mana` a `carry`; `max_hp` nemá v projektu žádný zdroj | `attributes.gd:14–20`; `ARCHITEKTURA.md`: `max_hp` 0× |
| 9 | **Design nezná kontrakt mrtvoly** (skupina `corpse`, co je v ní, co se stane při druhém `die()`). Zná jen slovo „mrtvola" | `ARCHITEKTURA.md:52,134` vs. `roadmap.json:231` (skupina `corpse`, přesun na spawn) |
| 10 | **Design neřeší vlastnictví souboru dvěma granulemi** (3 případy) — a neříká, že pak nemůžou běžet paralelně | lint `[3]` ×3: `player.gd`, `save.gd`, `world.gd`; `lint-roadmapa.py:66` |
| 11 | **Design neříká, kdo smí psát testy.** `acceptance` u granulí je `["tests","wiring"]`, ale agent **nesmí** měnit `tests/` — zakázáno v roadmape i vynuceno bránou | `roadmap.json:8,230,231`; `agent.yml:637` |
| 12 | **Design neuvádí, jaký je limit velikosti změny** (a že se počítá jako `add + del`), ani že bez deklarace platí 60 | `ARCHITEKTURA.md:152–159` mluví o „60 řádcích" bez jednotky změny; `agent.yml:646`, `conductor\src\index.ts:186` |
| 13 | **Design nepojmenovává brány tak, jak se skutečně jmenují** (`tests`/`wiring`/`render` jsou jen v roadmape) a neuvádí k nim příkazy | `ARCHITEKTURA.md`: `acceptance` 0×; příkazy v `ci.yml:74,94,135` |
| 14 | **Design nezná `_retired/`** — u přesunutých souborů neříká, že kód existuje a je použitelný jako základ | `ARCHITEKTURA.md`: `_retired` 0×; soubor `_retired/world.gd` (47 řádků) v `main` je |

**Dvě varování, která patří do designu jako pasti** (obojí doložené):

- **„Metoda existuje" není kritérium.** `has_method("save")` projde i nad souborem, který
  v `_ready()` spadne. V **tomhle** repu je živý exemplář: `tests\run_tests.gd:836`
  (`if … has_method("move"):`) — dokud metoda není, kontrola se **tiše přeskočí**.
  Naměřený důsledek téhož druhu je zapsaný v `save.gd:7–10`: `save()` zapsalo **35 B**
  (jen pozici hráče) **a přesto vrátilo `true`**. *(Měření „35 B" je z 2. 10. 2026 a je
  zapsané v komentáři souboru; **v této session jsem ho neopakoval** — Godot jsem nesměl
  pustit.)*
- **Zachování je součást smlouvy.** `scripts/player.gd` je **`extends Area2D`** (ne `Node`)
  a má **`_step(target)` + `_physics_process`**, které **testy volají přímo**
  (`run_tests.gd:211`) *(měřeno)*. Smlouva musí vyjmenovat, co zůstává **beze změny** —
  jinak granule „modernizuje" a rozbije testy, které na těch funkcích stojí.

---

## 5. Čím je každé tvrzení doložené

**Společný kontext všech příkazů:** spuštěno 2. 10. 2026, 09:20–09:31 UTC, v
`C:\Users\Ssevc\Local-Deepseek`, `games\uo-shadows` na `aad1c8d` = `origin/main`,
`git status --porcelain` prázdný. Git volán **jen** přes `orchestra\tools\git.cmd`.
Python spouštěn s `$env:PYTHONIOENCODING='utf-8'`.

| # | Tvrzení | Příkaz | Výsledek |
|---|---|---|---|
| 1 | Pracovní strom = `main` | `git rev-parse HEAD` / `rev-parse origin/main` | obojí `aad1c8d96743a243b9796b71c18791c5215bea56` |
| 2 | `player.gd` existuje a má 71 řádků | `git show origin/main:scripts/player.gd` + `cat-file -s` | 71 řádků, blob **2353 B** |
| 3 | `move` nebyl nikdy v žádné větvi | `git log --all -S"func move("` | **prázdný výstup** |
| 4 | `hp`, `max_hp`, `mana`, `max_mana`, `target`, `inventory`, `add_item`, `remove_item`, `die`, `equipped` v `player.gd` nejsou | přečten celý blob (71 řádků) | **ani jeden výskyt** |
| 5 | `assist.gd` čte `hp`/`max_hp`/`mana`/`max_mana`/`target` | `grep` nad `scripts\*.gd` | `assist.gd:11,13,15` |
| 6 | `economy.gd` volá `add_item`/`remove_item` | `grep` nad `scripts\*.gd` | `economy.gd:39,47` |
| 7 | `hud.gd` čte `hp`/`equipped` s fallbackem na `get_hp()`/`get_equipped()` | přečten `hud.gd` | `:40–47` (výchozí `hp = 0` na `:37`) |
| 8 | Testy volají `_step` přímo | `grep` nad `tests\*.gd` | `tests\run_tests.gd:211` |
| 9 | Test na `move()` je podmíněný (a tedy dnes neběží) a `move()` nemá volajícího | **plošný sken přes Python walk** (včetně skrytých složek) na `.move(` a `has_method("move")` | `.move(` = **0×**; `has_method("move")` = **1×** (`run_tests.gd:836`) |
| 10 | `player.gd:40` obsahuje řetězec, který test zakazuje | `grep` `level\.has_method` v `player.gd` + přečtení `run_tests.gd:838–840` | `player.gd:40` = `level.has_method("iso_position")`; test zakazuje `level.has_method("iso_position")` |
| 11 | `level.gd` `iso_position` nemá | `grep` `^func ` v `level.gd` | má `cell_center:146`, `cell_at:156`, `is_walkable_at:237`; **`iso_position` žádné** |
| 12 | `iso_position` existuje jen v `_retired/world.gd` | `grep` `iso_position` nad celým `games\uo-shadows` | 8 výskytů: `ARCHITEKTURA.md:132`, `_retired\world.gd:17,19`, `run_tests.gd:567,834,838,839`, `player.gd:40` |
| 13 | `world.gd` se **přesunul** (ne smazal) | `git show --stat -M c651368` | `{scripts => _retired}/world.gd \| 0` |
| 14 | `--diff-filter=D` hlásí totéž jako smazání | `git log --oneline --diff-filter=D -- scripts/world.gd` | `c651368 …` |
| 15 | `scripts/world.gd` v `main` není | `git cat-file -e origin/main:scripts/world.gd` | `fatal: … does not exist` (**exit 128**) |
| 16 | `_retired/world.gd` je použitelný základ | `git show origin/main:_retired/world.gd` + `Test-Path` | 47 řádků, **1597 B** v blobu i na disku; `iso_position/cell_at/gather/respawn/is_walkable` |
| 17 | PR #25 nedodal práci granule `entity.player` | `git show --stat e4be7c2` | `1 file changed, 4 insertions(+)` → **`project.godot`** (`[input]`, `input_devices=…`) |
| 18 | `entity.player` i `world.map` jsou `done` **v D1** | `GET $FORGE_URL/roadmap` s `x-forge-secret` (Node `fetch`, čteno z `orchestra\.env`; **tajemství jsem nevypisoval**) | `uo-shadows/entity.player → done/task=done`, `uo-shadows/world.map → done/task=done` (16 řádků, HTTP 200) |
| 19 | 13 granul bez `size_lines` a jejich jména | `python orchestra\tools\lint-roadmapa.py games\uo-shadows` | `13 z 21: data.content, core.attributes, core.skills, world.level, world.map, entity.item, sim.combat, sim.mining, sim.economy, entity.npc, sim.assist, persist.save, ui.hud` |
| 20 | Počty řádků blobů v tabulce §2 | Python: `git show origin/main:<cesta>` + `splitlines()` | viz §2 (např. `level.gd` 283, `save.gd` 99, `hud.gd` 89, `mining.gd` 72; `world.gd` a `npc.gd` exit 128) |
| 21 | `model: strong` nemá ani jedna z 13 | Python nad `roadmap.json` | `strong bez size_lines: []`; celkem `21 granul, 11 done, 8 strong, 13 bez size_lines` |
| 22 | Vlastnictví souboru dvěma granulemi (3×) | výstup lintu, sekce `SOUBORY Vlastněné VÍC GRANULEMI` | `player.gd` (`entity.player`, `entity.player.api`), `save.gd` (`persist.save`, `persist.save.state`), `world.gd` (`world.map`, `world.nodes`) |
| 23 | Limit změny je `add + del` proti `size_lines` (default 60) | `agent.yml:646`, `conductor\src\index.ts:182–188,741` | `if [ $((add + del)) -gt ${{ inputs.max_lines }} ]`; default `60` |
| 24 | PR se `tests/`, `.forge/`, `.github/`, `project.godot` je odmítnut | `agent.yml:637` | `tests/*\|.github/*\|.forge/*\|project.godot) echo "  !! chráněný soubor"; ok=0` |
| 25 | `acceptance` v designu 0×, v roadmape 22× | Python: `text.count('acceptance')` | `ARCHITEKTURA.md` **0**, `roadmap.json` **22**, `tests\run_tests.gd` **0** |
| 26 | Brána `wiring` smlouvu neověří | `grep` `player\|Player\|has_method\|provides` v `check-wiring.py` | **žádný výskyt**; kontrola řeší jen volání funkcí (`:117–127`) |
| 27 | Příkazy bran podle jmen v `acceptance` | `ci.yml` | `tests` → `:74`, `assets` → `:86`, `wiring` → `:94`, `render` → `:125,135` |
| 28 | `hp`/`max_hp` nemá v projektu zdroj | `attributes.gd:14–20` (`derived()`) + `ARCHITEKTURA.md` | `derived()` vrací `damage, hit_chance, attack_speed, mana, carry`; `max_hp` v designu 0× |
| 29 | Design zná 18 granulí, roadmapa 21 | `ARCHITEKTURA.md:180–197` (18 položek), `:234`; `roadmap.json` | 18 vs. **21** |
| 30 | `combat.gd` volá `has()` (Godot 3 API) | přečten `combat.gd`; měření téhož jevu v `mining.gd:10–13` | `combat.gd:19,25` — **stopa k ověření, nespouštěno** |
| 31 | Počty výskytů API (i ve skrytých složkách) | **plošný sken Python walk** přes `games\uo-shadows` (bez `.git`), tokeny počítány v `.gd/.py/.mjs/.json/.yml/.md/.tscn/.godot` — `grep` tool z rodiče skryté složky přeskakuje (naměřeno v `AGENTS.md`) | `.move(` **0** · `has_method("move")` **1** (`run_tests.gd:836`) · `die(` **4** (3× `roadmap.json`, 1× `ARCHITEKTURA.md:134`; v `scripts\`/`tests\` 0) · `max_hp` **3** (`assist.gd:11` + 2× roadmap) · `max_mana` **3** (`assist.gd:13` + 2× roadmap) · `add_item` **4** (`economy.gd:39` + 3× roadmap) · `remove_item` **3** (`economy.gd:47` + 2× roadmap) · `player.hp` **2** (`assist.gd:11`, `hud.gd:43`) · `player.target` **1** (`assist.gd:15`) · `player.equipped` **1** (`hud.gd:47`) · `velocity` **4** (jen `player.gd:12,44,46,47`) |
| 32 | `max_hp` a `_retired` v designu nejsou; `hp` je tam jednou (u nepřítele) | Python: `text.count(...)` nad `ARCHITEKTURA.md` | `_retired` **0×**, `max_hp` **0×**, `inventory` **0×**, `corpse` **0×**, `tests` **0×**, `wiring` **1×**, `hp` **1×** (řádek 175, `entity.enemy`) |

### Ověření na konci práce (povinné)

| Kontrola | Příkaz | Výsledek |
|---|---|---|
| `player.gd` existuje | `Test-Path games\uo-shadows\scripts\player.gd` | **`True`** |
| Hash designu **na začátku** | `Get-FileHash games\uo-shadows\docs\ARCHITEKTURA.md -Algorithm SHA256` | `356F060B16C2D6937E92E4C6A9982BCCA2A21A5CB24E38FA0CD6913B25BF3CB5` |
| Hash designu **na konci** | týž příkaz po veškeré práci | `356F060B16C2D6937E92E4C6A9982BCCA2A21A5CB24E38FA0CD6913B25BF3CB5` |
| **Změnil jsem design?** | porovnání obou hashů | **NE — oba hashe jsou shodné, znak po znaku** |
| Repo beze změn | `& orchestra\tools\git.cmd -C games\uo-shadows status --porcelain` | **prázdný výstup** (žádná změna, žádný nový soubor) |
| Zapsaný soubor | `Test-Path _analyza\C-PODKLAD-SMLOUVY.md` | jediný soubor, který tahle session zapsala (před prací **neexistoval**) |

**Co jsem v této session NEMOHL ověřit** (a plánovací session to musí vědět):

1. **Nespustil jsem Godot** (zákaz zadání) → všechna „přijímací kritéria" v §1.3 jsou
   **návrh, ne měření**, a tvrzení označená *(odvozeno z měření)* **jsou inference
   z přečteného kódu, ne z běhu**. Zejména **není spuštěno**: `assist.evaluate(player)`
   nad hráčem z `main`, chování `combat.resolve()` a měření „35 B" u `save()`.
2. **Nespustil jsem testy hry** → nevím, kolik kontrol dnes `tests\run_tests.gd` hlásí
   (počet se čte z běhu, ne z počtu vzorů v souboru).
3. **D1 jsem četl jako snapshot** v 09:27 UTC (endpoint `/roadmap`) — je to stav
   **jednoho okamžiku**, ne trvalá vlastnost.
4. **Neotevřel jsem `project.godot`** → tvrzení „projekt nemá ani jeden autoload" je
   **převzaté z komentáře** `mining.gd:6–8`, ne mé měření.
5. **Nezjišťoval jsem, kdo má napsat test**, když agent nesmí do `tests/` — to je
   **rozhodnutí pro plánovací session**, ne měřitelná věc (§1.4 bod 1, §4 bod 11).

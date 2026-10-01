# Konvence pro agenty (čti před každou změnou)

Tenhle soubor je **jen ke čtení** – agent ho dostává do kontextu a nemá ho měnit.
Vznikl z konkrétních chyb, které už jednou prošly a shodily testy. Každé
pravidlo má dole důvod, proč tam je.

## 1. GDScript: typy piš výslovně, `:=` jen když je typ známý

Nejčastější chyba free modelů: `var cil := uzel.position + uzel.smer * 40 * delta`.
Uzel z `get_nodes_in_group()` **nemá typ**, takže Godot ohlásí
`Cannot infer the type of "cil" variable because the value doesn't have a set type`,
skript hry se vůbec nenačte a **celá hra přestane existovat** (testy pak hlásí
„skript hry jde načíst" jako FAIL).

```gdscript
# ŠPATNĚ – spadne na parsování
for uzel in get_tree().get_nodes_in_group("enemy"):
    var cil := uzel.position + uzel.smer * 40.0 * delta

# SPRÁVNĚ – výslovný typ, uzel zůstává bez typu
for uzel in get_tree().get_nodes_in_group("enemy"):
    var cil: Vector2 = uzel.position + uzel.smer * 40.0 * delta
    uzel.position = cil
```

Platí to i pro `get_tree().get_first_node_in_group(...)`, `get_node_or_null(...)`
a cokoli dalšího, co vrací `Node`/`Variant` bez konkrétního typu.

## 1b. Do uzlu vytvořeného `Area2D.new()` nejde přidat vlastní vlastnost

```gdscript
# ŠPATNĚ – runtime chyba a nepřítel se vůbec nepřidá do scény
var e := Area2D.new()
e.smer = Vector2(1, 0)      # Invalid assignment of property or key 'smer' …

# SPRÁVNĚ – vlastnost deklaruje vlastní skript (scripts/enemy.gd)
var e := Area2D.new()
e.set_script(load("res://scripts/enemy.gd"))
e.smer = Vector2(1, 0)
```

Chyba uvnitř `_make_*` funkce **přeruší celou funkci**, takže se uzel nevrátí
a ve hře prostě chybí. Testy to poznají jen díky kontrole „hra vytvořila
nepřátele" – kdyby v projektu chyběla, vypadá to jako úspěch.

Alternativa bez nového souboru je `e.set_meta("smer", …)` / `e.get_meta("smer")`,
ale vlastní skript je čitelnější.

## 1c. `File` a `json` NEEXISTUJÍ – Godot má `FileAccess` a `JSON`

Nejčastější chyba modelů, které znají Python: sáhnou po `File`, `open()` nebo
`json.load()`. V GDScriptu nic z toho není a **skript se vůbec nenačte**:

```gdscript
# ŠPATNĚ – Parse Error: Identifier "File" not declared in the current scope
var file = File.new()
file.open("res://assets/data/items.json", File.READ)
var data = json.load(file)

# SPRÁVNĚ – Godot 4
var text := FileAccess.get_file_as_string("res://assets/data/items.json")
if text.is_empty():
    push_error("items.json nejde načíst")
    return
var data: Variant = JSON.parse_string(text)
if typeof(data) != TYPE_DICTIONARY:
    push_error("items.json není objekt")
    return
```

Pozor i na `json.parse()` (Python) vs `JSON.parse_string()` (Godot) a na to, že
`JSON.parse_string()` vrací `null` při chybě – **vždy zkontroluj výsledek**,
jinak dostaneš `Cannot infer the type` nebo pád na `null`.

## 1d. Rezervovaná a globální jména tříd

`class_name` vytváří **globální** jméno v celém projektu. Když se trefí do
jména, které už používá Godot, parsování skriptu selže:

```gdscript
# ŠPATNĚ – Parse Error: Class "Item" hides a global script class.
class_name Item

# SPRÁVNĚ – konkrétnější jméno
class_name GameItem
```

Naměřeno 30. 9. 2026: granule `entity.item` psala `class_name Item` a shodila
tím celý běh (testy pak hlásily jen „překročen tvrdý limit 90 s").

**Nepoužívej jako `class_name`:** `Item`, `Node`, `Object`, `Resource`, `Timer`,
`Camera`, `Light`, `Shape`, `Curve`, `Animation`, `Environment`, `Material`,
`Texture`, `Image`, `Font`, `Label`, `Button`, `Panel`, `Window`, `File`,
`Directory`, `JSON`, `Input`, `Engine`, `OS`, `Time`, `RandomNumberGenerator`.

Buď jméno projektu předřaď (`GameItem`, `UoItem`), nebo – ještě lépe – žádné
`class_name` nedávej a přistupuj k souboru přes `preload()`/`load()`.

## 1e. Než začneš psát, zkontroluj, že soubor není jen kostra

Když granule říká „vytvoř `scripts/x.gd`", **nejdřív zjisti, jestli už
existuje** a co v něm je. Přepisovat existující funkční soubor je zakázané
(viz §6) – a slepé `class_name` do souboru, který ho už má, je okamžitá chyba.

## 1f. `get()`, `set()`, `name` — kolize s vestavěnými členy uzlu

I když je název „hezký", může kolidovat s tím, co má každý uzel od enginu.
Naměřeno 30. 9. 2026 (po nasazení §1c/§1d tyhle chyby zbyly jako poslední):

```gdscript
# ŠPATNĚ – Parse Error: The method "get()" overrides a method from native
# class "Object".  (a „function signature doesn't match the parent")
func get(attr: String) -> int:
    return atributy[attr]

# ŠPATNĚ – Parse Error: Member "name" redefined (original in native class 'Node')
var name := ""

# SPRÁVNĚ – vlastní, konkrétní názvy
func hodnota(attr: String) -> int:
    return atributy[attr]

var nazev := ""
var jmeno := ""
```

**Nikdy nepoužívej jako název funkce:** `get`, `set`, `free`, `queue_free`,
`connect`, `emit`, `call`, `has`, `is_class`, `duplicate`, `print`.
**Nikdy nepoužívej jako název proměnné:** `name`, `owner`, `position`, `scale`,
`rotation`, `visible`, `modulate`, `script`, `process_mode`, `children`, `size`.
**Nikdy nepoužívej jako `class_name`:** `Item`, `Node`, `Object`, `Resource`,
`Timer`, `Camera`, `Light`, `Shape`, `Curve`, `Animation`, `Environment`,
`Material`, `Texture`, `Image`, `Font`, `Label`, `Button`, `Panel`, `Window`,
`File`, `Directory`, `JSON`, `Input`, `Engine`, `OS`, `Time`.

Když potřebuješ metodu „na získání hodnoty", pojmenuj ji česky nebo konkrétně
(`hodnota`, `vypocitej`, `get_damage`) — nikdy holé `get`.

## 1g. Soubor granule se instancuje přes `load(...).new()` – musí to být `extends Node`

Testy berou každý soubor granule takhle:

```gdscript
var sc = load("res://scripts/item.gd")   # musí jít načíst
var obj = sc.new()                       # musí jít zavolat BEZ argumentů
obj.use()                                # smluvní metody musí existovat na té instanci
```

Z toho plynou tři pravidla, která Godot sám nezkontroluje (parse projde, testy
pak spadnou na „překročen tvrdý limit 90 s" a příčina není vidět):

1. **Soubor začíná `extends Node`.** Když je to `Resource` nebo `RefCounted`,
   `new()` sice projde, ale instance není uzel – a uvolnění v testech (`free()`)
   na RefCounted vyhodí chybu, která **přeruší celý běh testů**.
2. **`class_name` NIKDY nesmí být i jméno vnořené `class` ve stejném souboru.**

   ```gdscript
   # ŠPATNĚ – vnořená třída přebije globální jméno; new() vrátí ji,
   # ta nemá use/repair/broken a není to Node
   class_name GameItem

   class GameItem extends Resource:
       func use() -> void: …

   # SPRÁVNĚ – soubor SÁM JE ta třída
   extends Node
   class_name GameItem

   func use() -> void: …
   ```

   Naměřeno 30. 9. 2026 na granulí `entity.item` (běh #122): model napsal přesně
   první tvar, brána na parsování vrátila exit 0 **a přesto to bylo špatně**.
   Orchestr teď tenhle tvar odchytí staticky, ale psát se to nemá vůbec.
3. **`_init()` nesmí mít povinný argument.** `new()` se volá bez parametrů;
   data načítej v `_ready()` nebo vlastní metodou `nacti(cesta)`.

## 1h. Konstanty z Godotu 3 v Godotu 4 NEEXISTUJÍ (a je to častá chyba)

Model má v trénovacích datech spoustu Godotu 3 a píše jeho konstanty. Godot 4
je přejmenoval na delší a významově jiná jména – a **parse to odhalí**:

```
# ŠPATNĚ – Parse Error: Cannot find member "ALIGN_LEFT" in base "Label".
label.align = Label.ALIGN_LEFT
label.valign = Label.VALIGN_TOP
label.autowrap = true

# SPRÁVNĚ – Godot 4
label.horizontal_alignment = HORIZONTAL_ALIGNMENT_LEFT
label.vertical_alignment = VERTICAL_ALIGNMENT_TOP
label.autowrap_mode = TextServer.AUTOWRAP_WORD_SMART
```

| Godot 3 | Godot 4 |
|---|---|
| `ALIGN_LEFT` / `ALIGN_CENTER` / `ALIGN_RIGHT` | `HORIZONTAL_ALIGNMENT_LEFT` / `…_CENTER` / `…_RIGHT` |
| `VALIGN_TOP` / `VALIGN_CENTER` / `VALIGN_BOTTOM` | `VERTICAL_ALIGNMENT_TOP` / `…_CENTER` / `…_BOTTOM` |
| `Label.align` / `Label.valign` | `Label.horizontal_alignment` / `Label.vertical_alignment` |
| `Label.autowrap` (bool) | `Label.autowrap_mode` (`TextServer.AUTOWRAP_*`) |
| `connect("signal", self, "_on_x")` | `signal.connect(_on_x)` |
| `yield(x, "signal")` / `yield(x, "completed")` | `await x.signal` / `await x.completed` |
| `export var` / `onready var` | `@export var` / `@onready var` |
| `OS.get_ticks_msec()` | `Time.get_ticks_msec()` |
| `instance()` | `instantiate()` |
| `PoolStringArray` a ostatní `Pool*Array` | `PackedStringArray` a ostatní `Packed*Array` |

**Naměřeno 1. 10. 2026:** granule `ui.hud` (běh #241) na tomhle spadla –
`Cannot find member "ALIGN_LEFT" in base "Label"` na `scripts/hud.gd:8` a
`VALIGN_TOP` na `:9`. Soubor se kvůli tomu **nikdy nedostal do repa** a HUD
nemá stavovou lištu.

**Pravidlo: nepoužívej konstantu, kterou jsi neviděl v tomto repu.** Když si
nejsi jistý jménem, sáhni po tématu, které v repu UŽ JE (`scripts/level.gd`,
`scripts/player.gd`) a napiš to stejně. Když tam není, napiš kód tak, aby
konstantu nepotřeboval (např. nastav vlastnost jen číslem nebo vynech).

**Pozor na past, která to zhoršuje:** tyhle chyby vypadají jako „vada brány",
protože jich model udělá víc najednou a první z nich je často jen následek
(`Identifier X not declared`). **Oprav vždy první chybu v souboru** — další
často zmizí samy.

## 2. Když se skript hry nenačte, poznáš to hned

Testy to řeknou („skript hry jde načíst"), ale **spustit si je musí CI** – ty
sám Godot nemáš. Proto: změnu dělej malou, v jednom souboru, a nikdy
nepřepisuj celý soubor, když měníš pár řádků.

## 3. Hra je postavená programově

Celá scéna se staví v `scripts/game.gd` (uzly se vytvářejí v kódu, žádné
ukládané `.tscn` kromě `main.tscn`). Když přidáváš uzel:

- dej mu `name` (testy a hledání podle skupin se o to opírají),
- přidej ho do skupiny (`coin`, `enemy`, `chest`, `player`), když se s ním má
  něco dít,
- nepřidávej nové soubory, když to jde udělat v `scripts/game.gd`.

## 4. Mapa (úroveň) – jak se ptát, kudy se dá chodit

Mapu spravuje uzel `Level` ve skupině `level` (`scripts/level.gd`):

| Metoda | Co vrací |
|---|---|
| `is_walkable_at(pozice: Vector2) -> bool` | je na té pozici průchozí políčko? |
| `is_walkable_cell(cx: int, cy: int) -> bool` | totéž pro políčko v mřížce |
| `cell_center(cx: int, cy: int) -> Vector2` | střed políčka ve světových souřadnicích |
| `marker_positions("coin"\|"spawn"\|"exit") -> Array` | pozice značek z mapy |
| `spawn_cell -> Vector2i`, `width`, `height`, `cell` | rozměry mřížky |

Nový předmět **nikdy neumisťuj na náhodnou pozici** – s mapou by mohl skončit ve
zdi. Použij `_safe_spot(vp)` (už v `game.gd` je) nebo `marker_positions()`.

## 5. Co agent nesmí měnit

`tests/`, `.github/`, `.forge/`, `project.godot` – to jsou pravidla hry
a automatického sloučení. Když agent sáhne na testy, ztratí tím páku, která
hlídá jeho vlastní práci. Automatické sloučení navíc pustí jen změny
v `scripts/` a `assets/` do 60 řádků. Výjimka: granule s deklarovaným
`size_lines > 60` (`model: strong`) smí být větší — limit se bere z granule
(vstup `max_lines`), a když orchestr nic nepředá, PR z takové granule čeká
na ruční sloučení (záměr, ne chyba).

## 6. Styl

- Komentáře a texty v UI **česky** (HUD, hlášky), kód anglicky podle okolí.
- Změna musí být **aditivní**: nic nemaž a nepřejmenovávej, co funguje.
- Když si nejsi jistý, udělej méně – malý správný krok je lepší než velký
  rozbitý.

## 7. Ověření

Testy běží v CI na každý PR (`Godot --headless`): 26 kontrol, počet roste
s každou granulí (kontroly na komponenty se zapínají samy, až soubor granule
v projektu je). Když něco nevyjde, je to vidět v logu jako `[test] FAIL …` –
čti ten řádek, ne celý log.

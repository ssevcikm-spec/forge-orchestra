# ÚKOL A — pracovní záznam (falešný poplach v `tests/run_tests.gd:836–840`)

**Co tenhle dokument JE:** pracovní záznam akční session z 2. 10. 2026 —
naměřená fakta, mutační běhy a rozhodnutí u Úkolu A. **Není to stav**
(ten je v `HANDOFF.md` §16) **ani zadání** (to je v `NEXT-SESSION-INSTRUKCE.md`).

**Proti čemu je měřeno:** `uo-shadows` = `194735d` (origin/main, čistý strom).
Běhy probíhaly v pracovním stromu `_analyza\a-ukol-scratch` (`git worktree`, HEAD
`194735d`), takže **klon uživatele se neměnil**.

---

## 1. Zadání versus naměřená skutečnost

Zadání (`NEXT-SESSION-INSTRUKCE.md` §2.4 a §3 Úkol A) říká:

* kontrola `tests/run_tests.gd:838–839` zakazuje **řetězce v celém souboru**
  `level.iso_position` a `level.has_method("iso_position")`;
* `scripts/player.gd:40` ten řetězec **obsahuje** (v `_physics_process`);
* prompt granule `entity.player.api` (`roadmap.json:90`) přikazuje ten kód
  **zachovat** → splnit prompt a projít testem se vylučuje;
* **opravit test, ne `player.gd`**.

To sedí — **až na dvě věci, které zadání nevědělo** a které mění podobu opravy.

### 1.1 `level.gd` metodu `iso_position` VŮBEC NEMÁ (měřeno)

Python walk nad `games/uo-shadows/scripts/level.gd` (grep tool by tu mohl tiše
přeskočit; walk ne):

```
func iso_position  → v level.gd NENÍ
```

`iso_position(cx, cy)` žije **jen** v `_retired/world.gd:19`. **Větev
`player.gd:40–44` je tedy mrtvá** — `dir` je směrový vektor, ne buňka mřížky
(`iso_position` bere `cx, cy` a násobí je `cell`), takže i kdyby ji level měl,
byl by to nesmysl. Test, který ji zakazuje, **netvrdí nic o izometrii** —
měří přítomnost textu. To je přesně popis „nastražené brány" z `AGENTS.md`.

### 1.2 ⚠ `game.gd` NEMÁ registr `component(id)` — a prompt to tvrdí jako dnešní stav

Naměřeno `python _analyza\a-kdo-ma-registr.py` (Python walk, komentáře odstraněny):

```
-- soubory v scripts/, které DEKLARUJÍ `func component(` --
   ŽÁDNÝ
-- soubory v scripts/, které `component(` VOLAJÍ --
   ['hud.gd', 'mining.gd', 'save.gd']
-- game.gd (kostra): deklaruje `func component(`: False
-- .forge/roadmap.json: engine.shell  done=None  owns=['scripts/game.gd']
```

**Důsledek, který mění Úkol A:** `hud.gd`, `mining.gd` a `save.gd` hledají
služby přes `get_parent().component(id)` — a v **živé hře dostanou `null`**.
Že to v testech funguje, je jen tím, že si testy staví **atrapu**
`TestKostra` (`run_tests.gd:895`), která `component()` má. **Registr existuje
jen v testech.** To je táž třída vady jako `world.gd` v `_retired/`: funkce,
která je zelená v testu a mrtvá ve hře.

**A proto má „cesta přes `world`" háček:** granule `entity.player.api` má
`depends_on` bez `world.nodes`, ale hlavně — i kdyby `world` existoval, hráč
ho v živé hře **nenajde**, protože kostra registr nemá (`engine.shell` je
`done=None`, tj. nehotová). Test, který by „cestu přes `world`" vyžadoval,
by tedy vynutil kód, který **ve hře nikdy neproběhne**.

**Rozhodnutí:** Úkol A opravuje **falešný poplach**, ne zavádí novou smlouvu.
Test bude měřit **chování `move()`**, ale nesmí vynutit víc, než co je dnes
dosažitelné. Vynucení izo projekce přes `world` patří granuli `world.nodes`
a `engine.shell`, ne sem.

---

## 2. Jak je test opravený

Původní kontrola (řádky 834–840) čte **zdrojový text**:

```gdscript
var player_zdroj := FileAccess.get_file_as_string("res://scripts/player.gd")
_check(not player_zdroj.contains("level.iso_position")
    and not player_zdroj.contains("level.has_method(\"iso_position\")"), …)
```

Nová kontrola **volá `move()`** a měří, **na kom se izo projekce ptala**:

* `TestUrovenBezIzo` — atrapa úrovně, která izo projekci **NEMÁ**, ale
  **počítá**, kolikrát se ji někdo pokusil zavolat (`izo_pokusu`) a kolikrát
  se ptal na průchodnost (`walk_dotazu`). Neimplementuje `iso_position`,
  takže případné volání shodí `move()`.
* Kontrola po zavolání `player.move(Vector2(1, 0))` tvrdí:
  `izo_pokusu == 0` — hráč **nesmí** brát izo projekci z úrovně.

**Proč to není slabší než původní test:** původní hledal řetězec v **celém
souboru** (tedy i v `_physics_process`, což prompt přikazuje zachovat) a byl
**podmíněný** — dnes se tiše přeskakuje. Nový měří **chování voláním** a je
citlivý na obě strany (viz §4).

---

## 3. Základní stav (bez mutace)

```
$ python _analyza\a-mutace-run.py zaklad
[test] 59 kontrol, 0 selhání      exit=0
```

Souhlasí se zadáním (§2.4: „main: 59 kontrol, 0 selhání").

> **Past, na kterou jsem při tom narazil:** v **čerstvém `git worktree`** dá
> stejný příkaz **`57 kontrol, 3 selhání`** — protože `.godot/` je
> v `.gitignore` a **import cache se do worktree nezkopíruje**. Padají
> „všechny assety jdou načíst (3 OK, 16 chybí)", „mapa má dlaždici pro každé
> políčko (0)" a „dlaždicové pozadí je ve scéně". **Není to regrese kódu** —
> je to nezměřený strom. Řešení: `Copy-Item games\uo-shadows\.godot
> _analyza\a-ukol-scratch\.godot -Recurse` (574 souborů), pak 59/0.

---

## 4. Mutace (důkaz, že test měří)

Mutace se zapisují **do souboru v Pythonu** (`_analyza\a-mutace-run.py`),
ne přes `python -c` — jinak se cestou konzole rozpadne diakritika a mutace se
**tiche neprovede** (skill `overovani` §7.9/§7.12). Skript po každém zápisu
**přečte soubor z disku** a `assert`-em ověří, že obsah je skutečně jiný.

| # | Mutace | Co se vloží do `player.gd` | Očekávání |
|---|---|---|---|
| M0 | žádná | — | 59/0, kontrola se nespustí (hlášená poznámka) |
| M1 | `move()` bere izo z **úrovně** | `level.iso_position`-větev (přesně to, co test zakazuje) | **FAIL** na nové kontrole |
| M2 | `move()` **neexistuje** | nic (`origin/main`) | 59/0, poznámka „chybí move()" |

*(Výsledky doplní tento dokument po spuštění — viz §5.)*

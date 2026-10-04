
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
Stejná vada jako v #28/#29, ale v souboru, který **už je v `main`** (sloučeno jako #30). Našel jsem ji, když jsem po sloučení ověřoval, jestli se komponenty domluví na tom, jak hledají služby.

## Co je naměřeno (Godot 4.7.2, spuštěním souboru — ne čtením)

| # | Vada | Naměřeno |
|---|---|---|
| 1 | `node.has("resource_id")` na `:17` — **`Object.has()` v Godotu 4 neexistuje** (Godot 3 API) | `SCRIPT ERROR: Invalid call. Nonexistent function 'has' in base 'Node (Uzel)'` → `gather()` se přeruší **dřív, než se dostane na skill** |
| 2 | Služby bere z `/root/Skills` a `/root/World` | obojí `false` — `project.godot` **nemá ani jeden autoload** a `scripts/world.gd` byl smazán při izometrické migraci (`c651368`) |
| 3 | Důsledek | `gather()` vrátí **0** a push_error; těžba nefunguje |

Testy to nevidí: kontrolují jen `has_method("gather")` (v CI `[test] OK mining.gd poskytuje gather(node)`), tedy **přítomnost metody, ne že něco udělá**.

## Co oprava mění

- `"resource_id" in node` místo `node.has(...)` — Godot 4 API.
- Služby z **registru kostry**: `component(id) -> Node` (`docs/ARCHITEKTURA.md:145`), stejně jako opravené `save.gd` (#28) a `hud.gd` (#29).
- Když `Skills` v registru není, vrátí 0 **a ohlásí to** (`push_error`) — tichá nula je horší než chyba.
- `World` je volitelný: `world.gather(cell)` se zavolá, jen když komponenta existuje (dnes neexistuje — `world.gd` v repu není).

## Jak je to ověřené

- Zkušební kostra s registrem (`_analyza\fixcheck\test.gd`, mimo repo): **32 kontrol, 0 chyb, 0 SCRIPT ERROR** — z toho 6 na mining: výtěžek `1 + (55-5)/10 = 6`, skill 55 → 56, `world.gather(cell)` se zavolalo se správným polem, dřevo jde na `drevorubectvi`, a **negativní kontrola**: bez registru vrátí 0 a ohlásí to.
- Testy hry na této větvi: **41 kontrol, 0 selhání**; `check-wiring.py` → „Vše v pořádku".
- Předchozí verze souboru na tom samém měřidle: `gather()` spadlo na `has()` (viz tabulka výše).

## Co to neřeší (a patří jinam)

- `scripts/world.gd` v repu **není**, ale roadmapa vede granuli `world.map` jako `done` („PR #21 sloučené 30. 9."). Kontrola `check-schema.py` to hlásí jako mrtvou větev: *„na jeho větve se NEDOSTANE"*. Těžba tedy nemá kam zapsat „vytěženo", dokud svět nevznikne.
- `world.map` a `entity.player` (inventář, `move()`, `die()`) jsou v roadmapě `done`, ale jejich práci v `main` nenacházím — to je nález mimo tenhle PR.

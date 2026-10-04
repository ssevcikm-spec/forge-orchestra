# ZADÁNÍ B — CO DÁL (a co NE)

> **✅ SPLNĚNO 3. 10. 2026 (session 23, 20:5x–22:0x UTC) — tenhle dokument je
> SPOTŘEBOVANÉ ZADÁNÍ, ne dnešní stav.** Provedeno: **krok 0** (commit + push
> obou repů), **Úkol 1** (DAG u `entity.player`), **Úkol 2** (brána kroniky),
> **Úkol 4** (smlouva o pozici hráče). **Neuděláno:** Úkol 3 (`engine.shell` —
> blokují ho 4 nehotové závislosti), Úkol 5 (`world.nodes` — práce nezačata,
> soubor v `main` je **prázdný**), Úkol 6 (zbylá měřidla).
> Výsledky a měření: `HANDOFF.md` **§27**, vlastní omyly **§8o**, nálezy
> **H33–H36** v `KRONIKA-PROJEKTU.md` §2.6.
>
> **Stav obou repů po provedení:** `orchestra` = `c2f730f` · `uo-shadows` = `ffe9bd8`
>
> **⚠ A jedna oprava zadání (nález H36):** §2 tvrdí, že `entity.player` **i**
> `entity.player.api` mají v `depends_on` `world.map`. `entity.player.api` ho
> **nemá** (má `core.attributes, core.skills, entity.item, world.level`) —
> ověřeno parserem nad `roadmap.json`.
>
> **⚠ Čísla v hlavičce NÍŽ (`d1cde9b`, `279f584`) jsou stav PŘI PSANÍ ZADÁNÍ** —
> ve svém čase správná (A2), dnes už neplatí.

**Zkontrolováno při:** `orchestra` = **`d1cde9b`** · `uo-shadows` = **`279f584`**
**Stav obou repů při psaní:** `orchestra` = `d1cde9b` (`M tools/kontrola-diakritiky.py`) ·
`uo-shadows` = `279f584` + **5 změněných/nových souborů** (viz §1)
**Pushnuto:** **oba ANO** — `origin/main..HEAD = 0`; práce typu A je **necommitnutá**
**Kdo to píše:** akční session typu A (3. 10. 2026), která provedla
`ZADANI-A-KONEC-MERIDEL.md`. **Výsledky jsou v `HANDOFF.md` §26**, omyly v **§8n**.

**Co tenhle dokument JE:** **zadání pro další session** — plánovací, nebo akční.
Není to stav (ten je v `HANDOFF.md`) ani plán (ten je v `PLAN-DALSI-KROK.md`).
`NEXT-SESSION-INSTRUKCE.md` byl **záměrně nezměněn** (hash `9c05c6b434d5d026…`,
17 841 B) — patřil souběžné session; proto tenhle soubor.

---

## 0. NEJDŘÍV: práce z minulé session není commitnutá

**Naměřeno** (`git status --porcelain`):

```
uo-shadows: M .forge/roadmap.json      M scripts/hud.gd
            M scripts/player.gd        M tests/run_tests.gd
            M docs/ARCHITEKTURA.md
            ?? tests/_dukaz-assist.gd  ?? tests/_kostra-snimku.gd
            ?? tests/_sonda-pohyb.gd   ?? tests/_snimek-hp.gd
orchestra : M tools/kontrola-diakritiky.py   (to NENÍ z téhle práce)
```

**Zadání A zakazovalo pushovat bez vyžádání** — a to platí dál.
**První krok další session: ukázat `git status` + `git diff --stat` a zeptat se.**

> **⚠ POZOR NA JEDNU VĚC, KTERÁ SE NESMÍ SLÉČT S OSTATNÍMI:** změna v `player.gd`
> **mění ovládání hry** (hráč teď chodí po izometrických osách dlaždic, ne 1:1
> podle obrazovky). Rozhodl o tom uživatel 3. 10. 2026, ale je to **viditelná
> změna pro hráče** — při pushi to patří do popisu commitu.

---

## 1. CO JE HOTOVÉ (a nezačínej znovu)

| Co | Doklad | Kde je to zapsané |
|---|---|---|
| **Úkol 1** — stav hráče (`hp`, `max_hp`, `mana`, `max_mana`, `target`, `inventory`, `equipped`, `add_item`, `remove_item`, `die`) | `_dukaz-assist.gd` → **exit 0**; testy **89/0** | `HANDOFF.md` §26.1 |
| **Úkol 1** — obejití v `hud.gd` odstraněno | `HUD zobrazuje skutečné HP hráče (text začíná 'HP: 77')` | tamtéž |
| **Úkol 2** — `move(dir)` je smluvní API a `_physics_process` ho volá | `_analyza\a2-mutace-izo.py` → **MUTACE CHYCENA** (89/0 → 89/1 → 89/0) | §26.2 |
| **Úkol 2** — smlouva zapsaná | `games\uo-shadows\docs\ARCHITEKTURA.md` **§2.2** | tamtéž |
| **Úkol 3** — roadmapa vs. `origin/main` | `_analyza\a3-roadmapa-over.py`; 2× `done` opraveno, 2× doplněno, 5× `size_lines` | §26.3 |
| **Úkol 4** — hypotéza změřena | **11 omylů** místo čekaných 0–2 → **hypotéza NEPOTVRZENA** | §26.4, §8n |
| **VZHLED** — ověřeno pohledem | `_analyza\a-snimek-hp.png` (`read_image`) | §26.5 |

---

## 2. ÚKOLY PRO DALŠÍ SESSION (v tomto pořadí)

### Úkol 1 — Rozhodnout DAG u `entity.player` (blokuje vydání granule)

**Naměřeno:** granule `entity.player` (i `entity.player.api`) mají v `depends_on`
**`world.map`** — a `world.map` je od 3. 10. 2026 **`done: false`**, protože jeho
práce (`scripts/world.gd`, `gather()`, respawn) **v `main` nikdy nebyla**
(`c651368` ho přesunul do `_retired/`).

**Důsledek:** conductor `entity.player` **nevydá** — čeká na granuli, která
hotová není a nikdy nebyla.

**Co je potřeba rozhodnout:** `entity.player.api` čeká na
`core.attributes, core.skills, entity.item, world.level` — **všechny čtyři jsou
`done: true`**, takže **vydat ji lze hned**. Má `entity.player` (stará granule,
kterou nahrazuje) mít `world.map` v závislostech dál?
**Návrh:** ne — práce, kterou `entity.player.api` dodává, `world.map` nepotřebuje
(bere `level.is_walkable_at`, tedy `world.level`). Ale **je to zásah do DAG**,
tak ho rozhodni vědomě a zapiš.

### Úkol 2 — Doplnit blok `8n` do brány kroniky

**Naměřeno:** `python _analyza\kronika-kontrola.py` hlásí **„omylů celkem: 107"**,
ale součet řádků tabulky v `KRONIKA-PROJEKTU.md` §3 je **118** — session 22 připsala
blok **`8n` (11 omylů: 113–123)** a `BLOKY` v bráně ho **nezná**.
**Je to záměrné** (zadání A zakazovalo doplňovat seznamy v branách) a je to
poznamenané v kronice i v §26.

**Co udělat:** doplnit `("8n", "### 8n. Omyly AKČNÍ session")` do `BLOKY`,
přepočítat souhrnný řádek a ověřit, že **řádky tabulky = brána**.
**Tohle je pátý výskyt téhož vzorce** (`8i`–`8m`, `8n`) — zvaž, jestli nemá brána
projít **všechny** nadpisy `### 8x.` v dokumentu místo pevného seznamu.

### Úkol 3 — `engine.shell` (tím se HUD dostane do HRY)

**Proč:** komponentní `hud.gd` je hotový a **měřený**, ale `scripts/game.gd` je
pořád **monolit** a `hud.gd` **neinstancuje** — takže **hráč ho ve hře neuvidí**.
Snímek v §26.5 to říká nahlas.

**Pozor:** granule `engine.shell` je velká (`size_lines: "<= 120"`, `model: strong`)
a má 19 závislostí. Zkontroluj, které z nich jsou `done`, než ji vydáš.

### Úkol 4 — `persist.save.state`: kdo vlastní pozici hráče

**Naměřeno (nový blokátor, vznikl prací typu A):** `scripts/save.gd:84,52` ukládá
i načítá `player.position` **podmíněně přes `"position" in hrac`**. Do 3. 10. 2026
tenhle test **nikdy neprošel** (`player.gd` dědí z `Area2D`, ale vlastnost
`position` v něm nebyla „vidět" tak, jak kód čekal). Teď **projde** — takže
`load()` **přepíše spawn pozicí ze souboru**.

**Rozhodni:** má pozici vlastnit `player.gd` (a `save.gd` ji má jen ukládat), nebo
se má hráč po smrti/načtení vracet na `level.spawn_cell`?
**Neboduj to potichu** — je to smlouva (§2.1 `ARCHITEKTURA.md`).

### Úkol 5 — `world.nodes` (odblokuje `world.map` i těžbu)

`scripts/world.gd` v `main` **není**; `mining.gd` volá `world.gather(cell)` na
**atrapě** v testech. Zadání A tuhle granuli **výslovně vyloučilo** — je to
samostatná práce.

### Úkol 6 (nezávislý) — Zbylá měřidla

`ZADANI-DODELAT-MERIDLA.md` §3: **Úkol 5b** (krytí `schema.sql`) a **Úkol 6**
(tabulka pokrytí diakritiky) — obě zadání A **vyloučilo**, zůstávají otevřená.

---

## 3. CO NEDĚLAT

- **NEPUSHOVAT bez vyžádání** — nejdřív `git status` + `git diff --stat` a čekat.
- **NEPŘEPISOVAT `NEXT-SESSION-INSTRUKCE.md`** (hash `9c05c6b434d5d026…`,
  17 841 B) — patřil souběžné session.
- **NEPŘEPISOVAT historická čísla** — `HANDOFF.md` i `KRONIKA-PROJEKTU.md` jsou
  **append-only**. Číslo „107" v kronize je **stav před blokem `8n`**, ne lež.
- **NEMAZAT `tests/_dukaz-assist.gd`** — je to spustitelný doklad smlouvy
  (dnes `exit 0`; kdyby stav hráče zmizel, spadne na `exit 1`).
- **NEPŘESOUVAT `HANDOFF.md` §10–§22 do kroniky** (opatření 5) — samostatná
  session s nejvyšším rizikem.
- **NEZAHRNOVAT `entity.enemy`** do práce na `entity.player.api`.

---

## 4. HOTOVO ZNAMENÁ (měřitelné)

- [ ] `git status` + `git diff --stat` **ukázáno** a čekáno na vyjádření
- [ ] `entity.player` / `entity.player.api`: `depends_on` **rozhodnuto a zapsáno**
- [ ] `kronika-kontrola.py` hlásí **118** a součet řádků tabulky s ním **souhlasí**
- [ ] testy hry **≥ 89 kontrol, 0 selhání** (a po každé změně kódu **mutační důkaz**)
- [ ] `_dukaz-assist.gd` → **exit 0**
- [ ] `_analyza\a2-mutace-izo.py` → **MUTACE CHYCENA**
- [ ] `_analyza\handoff-kontrola-uplnost.py` → **83/83** (po každém přepisu handoffu)
- [ ] `docs/ARCHITEKTURA.md`: **každá nová smlouva má TVAR DAT + PŘIJÍMACÍ KRITÉRIUM**
- [ ] vizuální změna ověřena **pohledem** (`read_image`), ne jen testy

---

## 5. JAK SI TO OVĚŘIT (spustitelné, z `C:\Users\Ssevc\Local-Deepseek`)

```powershell
$env:PYTHONIOENCODING='utf-8'
$env:APPDATA = "$PWD\_analyza\a-godot-user"
$godot = 'orchestra\tools\godot\Godot_v4.7.2-stable_win64_console.exe'

# testy hry — ocekavej "89 kontrol, 0 selhání" a exit 0
& $godot --headless --path games\uo-shadows --script res://tests/run_tests.gd

# dukaz smlouvy assist -> player — ocekavej exit 0
& $godot --headless --path games\uo-shadows --script res://tests/_dukaz-assist.gd

# sonda pohybu — ocekavej "6 kontrol, 0 chyb" a exit 0
& $godot --headless --path games\uo-shadows --script res://tests/_sonda-pohyb.gd

# mutacni dukaz, ze kontrola izometrie MERI — ocekavej "MUTACE CHYCENA"
python _analyza\a2-mutace-izo.py

# roadmapa vs origin/main (cte BLOBY, ne disk)
python _analyza\a3-roadmapa-over.py

# nic nezmizelo z handoffu — ocekavej 83/83
python _analyza\handoff-kontrola-uplnost.py

# brana kroniky — DNES zamerne hlasi 107 (viz Ukol 2)
python _analyza\kronika-kontrola.py

# snapshot HUD s HP -> pak se na nej PODIVEJ pres read_image
& $godot --path games\uo-shadows --rendering-driver opengl3 --resolution 960x540 `
    --script res://tests/_snimek-hp.gd
```

**Když některé číslo nesedí, je to výsledek — ne tvoje chyba.** Zapiš ho.
Předchozí session měla **11 vlastních omylů** (§8n) a **8 z nich bylo v měřidle**;
hypotéza „bez měřidla bude 0–2 omylů" se **nepotvrdila**.

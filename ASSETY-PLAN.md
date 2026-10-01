# Plán P2 — zapojení assetů do pipeline

Návrh, **jak** přestat assety tahat ručně. P0 + P1 (registr, fetch, brána) je
hotové a ověřené, ale běží jen na zavolání. P2 z toho dělá součást orchestra.

> **Stav: neimplementováno.** Tenhle soubor je návrh k odsouhlasení.

## Zásadní zjištění: conductor se měnit NEMUSÍ

Ověřeno v kódu, ne odhadem:

| Co | Kde | Důsledek pro P2 |
|---|---|---|
| `kind` se bere z granule a posílá do workflow bez validace | `conductor/src/index.ts:636`, `:204` | nový druh `pack` projde beze změny conductora |
| `agent.yml` deklaruje `kind` jako volný řetězec (`'code \| assets \| build \| research'` je jen nápověda) | `repo/.github/workflows/agent.yml:28` | nic se nerozbije, jen se přidá větev |
| brána auto-merge pouští `scripts/*` a `assets/*`, binárky počítá jako 0 řádků | `agent.yml:597,616` | stažený `.ogg`/`.png` **limit nespotřebuje** |
| `check-assets.py` kontroluje JEN sprity z `spec.role` a hudbu v `assets/audio/music/manifest.json` | `repo/.forge/check-assets.py:189,100` | zvuky v `assets/audio/ui/` a textury projdou **bez úpravy specu** |
| `files-to-edit.mjs` filtruje `.gd\|json\|md\|cfg\|tscn\|tres\|godot` | `repo/.forge/files-to-edit.mjs:42` | binárky do aideru nejdou – fetch nesmí přes LLM |

**Celý P2 tedy jde bez nasazení conductora.** To je největší úspora rizika:
žádný `wrangler`, žádný deploy z gitu, žádná změna D1.

## Pravidlo, na kterém to stojí

Fetch assetu **není práce pro model**. Je to stažení a ověření hashe. Model
dostane až hotový soubor a jeho cestu – a to jako malou granuli `code`, která
asset zapojí do hry. Důvod je naměřený: free modely padají na formátu odpovědi
(„SEARCH blok bez `<<<<<<<`"), ne na tom, že by nezvládly přečíst URL.
Granule `pack` proto **aider vůbec nespouští** – ušetří kvótu a odstraní
nejnespolehlivější článek.

## P2-A: šablona (nulové riziko pro hru)

Mění se jen `orchestra/repo/**`, tedy šablona. Do hry se to dostane až sync
nástrojem, a to zvlášť.

| # | Soubor | Změna |
|---|---|---|
| A1 | `repo/.forge/check-licence.py` | **nový** – kopie `orchestra/tools/check-licence.py` (kanonická verze zůstává v orchestra, stejně jako u `worker.mjs`) |
| A2 | `repo/.forge/asset-fetch.mjs` | **nový** – kopie `orchestra/tools/asset-fetch.mjs` + `repo/assets/asset-registry.json` (běh v runneru nemá orchestra po ruce) |
| A3 | `repo/.github/workflows/agent.yml` | krok **„Stáhni assety"** (`if: inputs.kind == 'pack'`) – pouští fetch z granule, padá hned při neshodě hashe |
| A4 | `repo/.github/workflows/agent.yml` | krok **„Kontrola licencí"** – pouští se VŽDY, nezávisle na druhu granule |
| A5 | `repo/.github/workflows/agent.yml` | u `kind: pack` **přeskočit** `pick-provider`, `Spusť agenta` a všechny LLM kroky (`if: inputs.kind != 'pack'`) |
| A6 | `repo/.github/workflows/agent.yml` | verdikt: u `pack` stačí úspěšný fetch + testy + neprázdná změna (žádné „agent nic nezměnil") |
| A7 | `repo/.github/workflows/ci.yml` | krok „Kontrola licencí a původu assetů" – nezávisle na agentovi (brána auto-merge čeká na `Testy a build`, takže bez toho by se PR nesloučil sám) |
| A8 | `repo/.gitattributes` | `*.glb`, `*.gltf` do sekce binárek (kvůli budoucím 3D assetům) |
| A9 | `repo/CONVENTIONS.md` | jak se do hry přidává asset: nikdy ručně, vždy přes fetch; `spec.role` se aktualizuje, jen když má být sprite měřený |

**Postup ověření A (bez hry):** `kontrola-driftu.mjs` šablona vs. klon → 0
rozdílů; lokální běh `agent.yml` nasucho není možný, takže se ověřuje až v P2-B
na jedné hře.

**Proč A9:** brána `check-assets.py` je slepá na sprity, které nejsou v `spec.role`
(naměřeno: chůze leží v `tools/blender/sprites/`, ale hledá se
`assets/sprites/walk_*.png` → kontrola shody siluet se nikdy neuplatní). Když se
tedy sprite stáhne a nezapíše do `role`, **projde bez měření** – a nikdo se to
nedozví. To je stejná třída vady jako „zelený test, který se nikdy nezapne".

## P2-B: první reálný asset ve hře (jeden, ověřitelný konec)

Cíl: **jeden** zvuk z Kenney projde celou cestou až do sloučeného PR. Ne víc –
dokud není ověřený jeden, nemá smysl jich dělat deset.

| # | Co | Detail |
|---|---|---|
| B1 | sync šablony do `games/uo-shadows` | `sync-sablona-hra.py` + `kontrola-driftu.mjs` |
| B2 | `assets/fetch-plan.json` ve hře | plán, co se stahuje: `{ "ui.coin": { "pak": "kenney/interface-sounds", "extract": ["Audio/coin_001.ogg"], "kam": "assets/audio/ui/" } }` (v souboru, ne v promptu – musí být čitelný a reviewovatelný) |
| B3 | granule v roadmapě | `id: audio.ui`, `kind: pack`, `owns: ["assets/audio/ui/coin_001.ogg", "assets/asset-lock.json", "assets/CREDITS.md"]`, `depends_on: []`, `size_lines: 60` |
| B4 | ověření zvuku v Godot | `AudioStreamPlayer` s `res://assets/audio/ui/coin_001.ogg` se musí načíst (jinak `.ogg` v Godotu 4.7 nefunguje a celý plán padá) |
| B5 | `ASSETY.md` + `game-assets` skill | zápis postupu a ověřených zdrojů |

**Proč `owns` obsahuje i `asset-lock.json`:** conductor podle `owns` zamyká
souběh. Kdyby lock nebyl v `owns`, mohly by dvě granule `pack` běžet paralelně
a přepsat si lock navzájem.

**Pozor na past:** `owns` je zámek souboru **v repu**, ale lock v okamžiku
plánování ještě neexistuje. Ověřeno: `lockKeys()` z payloadu nic neexistujícího
nevyžaduje – zámek je jen klíč, takže to funguje.

## P2-C: rozšíření (až po ověření B)

| # | Co | Proč až teď |
|---|---|---|
| C1 | textura z Poly Haven do hry | jiná cesta než ZIP (API + md5) – chce vlastní ověření |
| C2 | font z Google Fonts | OFL vyžaduje i `LICENSE` soubor fontu v projektu |
| C3 | `pack` do whitelistu domácího uzlu (`worker.cmd`) | lokální fetch: bez GitHub minut a bez LLM. Dnes je uzel **off** a whitelist má jen `assets,test,build` |
| C4 | `size_lines` u `pack` granulí | `maxLinesOf()` čte `size_lines` z granule; `max_lines` u `pack` řídí jen bránu, ne dispatch |

## Posloupnost a brány

```
P2-A  šablona ──► drift 0 ──► P2-B  sync + 1 granule ──► merge PR ──► P2-C
      (nikdo to nepoužívá)         (jedna hra, jedna cesta)         (šířka)
```

Každý krok má bránu, která musí projít před dalším:

1. **A → B:** `kontrola-driftu.mjs` hlásí 0 rozdílů mezi šablonou a hrou.
2. **B → C:** granule `audio.ui` má sloučený PR **bez ručního zásahu** a zvuk
   se ve hře skutečně přehraje.
3. **C:** každý typ assetu (textura, font) má vlastní ověření, ne „mělo by to jít".

## Rizika (pojmenovaná, ne skrytá)

| Riziko | Proč vzniká | Jak se pozná |
|---|---|---|
| **Lock spolkne limit 60 řádků** | lock je text, počítá se celý (~13 řádků/asset) | PR se nesloučí sám a dostane komentář „velká změna" |
| **Zvuk se v Godotu nenačte** | `.ogg` import v headless režimu není ověřený | test „assety jdou načíst" hlásí chybějící soubor |
| **Nová `.ogg.import` v `tools/`** | Godot si `.import` píše sám, i mimo `assets/` | brána auto-merge přeskakuje `.import` PRVNÍ → nemá to vadit |
| **Fetch padne na síti** | runner nemá přístup na `dl.polyhaven.org` | krok fetch padá s HTTP chybou, granule spálí pokus |
| **Sprite bez zápisu do `spec.role`** | brána ho pak neměří | zelené CI, ale sprite nikdo nezkontroloval (A9) |
| **Dvě granule `pack` na jeden lock** | lock je jeden soubor | souběh řeší `owns` (B3); jinak `git apply` konflikt |

## Co NEDĚLAT

- **Neposílat fetch modelu.** Ani jako „malý úkol" – je to stahování souboru.
- **Nestahovat celé balíky.** 100 souborů v repu, které hra nenačte, je jen
  horší review a větší repo.
- **Nezapisovat `CREDITS.md` ručně.** Generuje se a brána porovnává; ruční
  editace u CC-BY znamená špatnou atribuci.
- **Nepřidávat `cc-by-sa`.** Vynucuje stejnou licenci na celou hru.
- **Nezapínat hru kvůli testu assetů.** `uo-shadows` je aktivní; práce navíc
  na pozadí pálí free kvótu (naměřeno 30. 9. 2026).

## Co musí platit před pushem

`orchestra` má **necommitnuté změny z minulé session** (`conductor/src/index.ts`,
`wrangler.toml`, `README.md`, `pick-provider.mjs`, spousta untracked `tools/`).
Před jakýmkoli pushem: `git fetch` + `rebase`, a commitovat **jen soubory P2**,
ne všechno, co je v pracovní kopii. Push do `conductor/**` spouští deploy.

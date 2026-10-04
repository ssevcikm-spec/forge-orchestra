# Forge Orchestra × nové možnosti agenta — jak to do sebe zapadá

> **Co tenhle dokument JE:** rejstřík. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 30. 9. 2026 · **Navazuje na:** `MOZNOSTI-AGENTA.md` (co agent umí a čím
je to ověřené) · **Stav orchestra:** 6/18 granul hotových, hra `uo-shadows`

Zkratky: **CI** = GitHub Actions runner (cloud, `ubuntu-latest`) ·
**uzel** = domácí pull-worker `pc-domaci` na tomto PC · **session** = tato
agentní session v DSH na tomto PC.

---

## 1. Verdikt (čti tohle, zbytek jsou detaily)

| Nová možnost | Vejde se do orchestra? | Kde poběží | Přínos | Náklad |
|---|---|---|---|---|
| **Čtu obrázky sám** (`read_image`) | **ANO** | jen **session** | **vysoký** — chybí vrstva „je na tom snímku to, co má být?" | nulový (nic se nenasazuje) |
| **Blender headless** | **ANO, ale ne do cloudu** | **uzel** (nebo session) | střední — u `uo-shadows` je 3D už hotové a schválené | střední (uzel musí běžet) |
| **Lokální generátor** (ComfyUI/SDXL) | **ANO, ale ne do cloudu** | **uzel** (GPU) | střední | střední, blokuje VRAM |

**Jednou větou:** ani jedna z těch věcí **nemůže** běžet v cloudovém CI — a to
není omezení orchestra, to je vlastnost runneru. Orchestra na to už má správnou
odpověď: **domácí uzel** (`target='lan'`) a `kind` úlohy. Chybí jen dokončit to,
co je rozdělané.

### Co je potřeba rozhodnout (než se cokoli nasadí)

1. **Zapnout uzel `pc-domaci`?** Bez něj jsou Blender i lokální generátor mimo
   hru — orchestra zůstane cloud-only.
2. **Smí se assety slučovat samy?** Auto-merge gate dnes pouští `assets/*` bez
   jakékoli vizuální kontroly (viz §7, nález 3).
3. **Kdo schvaluje vzhled?** Dnes to nedělá nikdo — ani agent, ani Gemini, ani
   člověk. Přitom u `uo-shadows` **už jednou schválený byl** (`assets/spec.json`,
   `_stav`: „MILNÍK 1 (cesta A) SCHVÁLEN 5/5").

---

## 2. Co orchestra umí dnes — a co jí chybí

Aby se to nepletlo: orchestra **měří** vzhled už teď. Neměří ale **obsah**.

| Vrstva | Nástroj | Stav |
|---|---|---|
| chování | `tests/run_tests.gd` + `ci.yml` | ✅ funguje, 34 kontrol |
| zapojení kódu | `.forge/check-wiring.py` | ✅ běží v CI |
| **měření assetů** | `.forge/check-assets.py` | ✅ běží v CI — měřítko, díry, okraje, siluety, hudba |
| **vzhled scény** | `.forge/verify-level-render.py` | ✅ běží v CI — vyrenderuje snímek hry (xvfb) a porovná s mapou |
| **obsah / „je to ono?"** | — | ❌ **NIC** |
| 3D → 2D sprity | — | ⚠️ hotové, ale mimo repo a jen ručně |

**Naměřeno 30. 9. 2026** (`check-assets.py` na `uo-shadows`):

```
player  postava 38× 95 px na plátně 128  barev 1103  okraj 0 %  děr 0
poměry: coin/chest 0.50×, coin/player 0.25×, chest/player 0.51×
Vše v pořádku: assety odpovídají specu.
```

To je silný výsledek — a přesně ukazuje hranici: brána umí říct „měřítka sedí,
žádné díry, žádné zbytky pozadí", ale **neumí říct, jestli je na spritu to, co
má být**. (Že je postava slepenec primitiv, je v `uo-shadows` **záměr**
schváleného milníku — postava se v UO stylu skládá z vrstev a obličej přijde
jako vrstva `head`. Nejde tedy o vadu, ale o důkaz, že vzhled schvaluje člověk,
ne brána.)

Dvě věci, které jsou v repu **hotové a nevyužité**:

- **`.forge/vision.mjs`** — plnohodnotné „oči" pro CI (Gemini, klíč
  `GEMINI_API_KEY`, fallback mezi modely, `exit 1` nezhodí běh). Grep potvrdil:
  **žádný workflow ho nikdy nezavolal.** Mrtvý kód čekající na zapojení.
- **`ci.yml` snímek hry vyrábí a zahazuje.** Krok „Vizuální kontrola" pustí
  Godot pod `xvfb` a nechá ho vypsat framy do `/tmp/frames/frame*.png`. Číselná
  shoda s mapou se spočítá; **na snímek se nikdo nepodívá.**

To je celý trik téhle integrace: **spojit dvě hotové věci, které se zatím
minuly.**

---

## 3. Návrh 1 — Zapojit `vision.mjs` do CI (nejlepší poměr přínos/náklad)

**Co:** za krok „Vizuální kontrola" přidat krok, který nad **už vyrenderovaným
snímkem** zavolá `vision.mjs`.

**Kde:** `repo/.github/workflows/ci.yml` (+ synchronizovat do `uo-shadows`).

**Proč právě tam:** snímek už existuje, `xvfb` je vyzkoušený, klíč
`GEMINI_API_KEY` už je v Secrets (používá ho `agent.yml` i `model-check.yml`).
Nepřidává se žádná infrastruktura — jen se nad hotovým artefaktem položí otázka.

```yaml
      - name: Vizuální kontrola – rozumí snímku (Gemini)
        # MĚŘENÍ vs POCHOPENÍ: verify-level-render.py ověří, že snímek ODPOVÍDÁ
        # mapě (shoda pixelů). Neověří ale, že je na něm vidět hráč, dlaždice
        # a mince – tedy to, co hráč opravdu vidí.
        #
        # NEBLOKUJE: vision.mjs vrací 1, když kvóta/model selže. Kdyby krok
        # blokoval, výpadek free kvóty by zastavil slučování všech PR.
        # Proto `|| true` + ::warning. Až se osvědčí, dá se z toho udělat
        # tvrdá brána pro granule kind=assets.
        if: always()
        continue-on-error: true
        env:
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY || vars.GEMINI_API_KEY }}
        run: |
          SNIMEK=$(ls /tmp/frames/frame*.png 2>/dev/null | tail -1 || true)
          [ -n "$SNIMEK" ] || { echo "::warning::snímek není, kontrola přeskočena"; exit 0; }
          node .forge/vision.mjs "$SNIMEK" \
            "Herní screenshot. Odpověz česky a stručně: 1) Je vidět hráč? 2) Jsou vidět dlaždice terénu? 3) Je něco zjevně rozbité (černá obrazovka, chybějící textura, všechno přes sebe)? 4) Vypadá to jako hratelná scéna?" \
            || echo "::warning::vizuální kontrola nedostupná (kvóta/model)"
```

**Co to reálně chytí** (a čísla ne): černý snímek s exit 0 · hráč pod dlaždicemi ·
rozbitý HUD přes celou obrazovku · prázdná scéna bez mincí. Přesně ta třída chyb,
kterou popisuje `HANDOFF.md` — „všechno to prošlo, protože se to nikde neměřilo".

**Riziko:** kvóta Gemini. `vision.mjs` zkouší modely popořadě a při neúspěchu se
jen ohradí. Při denním provozu jde o jednotky volání na běh.

---

## 4. Návrh 2 — Kontaktní arch: vizuální kontrola pro session

**Co:** jeden PNG s mřížkou spritů, na který se agent podívá **jedním**
`read_image`. Pro 256 souborů je to jediná proveditelná vizuální kontrola.

**Stav: hotovo a vyzkoušeno** — `orchestra/tools/kontaktni-arch.py`.

```powershell
# celá sada jedním pohledem
python orchestra\tools\kontaktni-arch.py games\uo-shadows\tools\blender\sprites `
    --recurse --cell 56 --cols 16 --out orchestra\.tmp\arch.png

# čitelný detail s popisky
python orchestra\tools\kontaktni-arch.py games\uo-shadows\tools\blender\sprites `
    --cell 96 --cols 8 --label --filter body_d0 --out orchestra\.tmp\arch-body.png
```

**Důkaz** (256 spritů → arch 896×896 px, přečteno `read_image`):

![Kontaktní arch – 256 spritů uo-shadows](orchestra/.tmp/kontaktni-arch-npc.png)

![Detail: 8 framů chůze s popisky](orchestra/.tmp/arch-body.png)

Na archu je vidět to, co čísla neřeknou: postava je **sestavená z vrstev**
(`body`/`legs`/`torso`/`weapon`), každá zvlášť, takže se ve hře skládají přes
sebe — a v detailu je vidět, že **chůze je plynulá** (nožičky se střídají,
těžiště neujíždí).

Do CI se **nedává**: `read_image` v runneru neexistuje a arch by tam neměl kdo
přečíst. Je to nástroj pro **session a pro člověka**.

### Kde to v procesu orchestra použít

| Kdy | Co udělat |
|---|---|
| Po běhu agenta, který měnil `assets/` | arch změněných spritů a podívat se |
| Před sloučením PR s novými sprity | arch **jen změněných** souborů jako lidská kontrola |
| Po Blender renderu | arch porovnat s minulým stavem (`_compare.png`) |
| Při ladění stylu | arch z `imagegen-local --matrix` dávek — 24 variant v jednom obrázku |

**Změnový arch** (jen to, co PR mění):

```powershell
$zmenene = gh pr view <PR> --json files --jq '.files[].path' | Select-String '\.png$'
# → filtruj --filter podle jmen, nebo arch rovnou stavěj z výpisu cest
```

---

## 5. Návrh 3 — Blender jako úloha domácího uzlu

**Proč ne v CI:** `ubuntu-latest` Blender nemá, instalace je ~300 MB a render
3D scény na softwarovém OpenGL runneru je pomalý. **Nedělej to.**

**Proč to jde na uzlu:** uzel je tento počítač — Blender 5.2.1 LTS tu je,
Godot taky, a pipeline pro `uo-shadows` je hotová i schválená.

### Co tomu dnes chybí (tři konkrétní věci)

1. **Uzel je off** (naposledy 29. 9. 20:03) → `orchestra\worker.cmd`.
2. **`worker.mjs` nezná krok `blender:`.** Povolené kroky jsou jen `shell`,
   `godot-import`, `godot-test`, `godot-export`, `python`, `forge`, `make-dir`.
   Obejít se to dá krokem `shell:` — ale ten se **vždy ptá y/N**, takže
   bezobslužný render (Task Scheduler) neproběhne.
3. **`worker.mjs` má mrtvý default:** `FORGE_CMD` míří na `forge.cmd`, smazaný
   s GameForge → krok `forge:` je nepoužitelný.

### Nejmenší rozumná změna

Do `worker.mjs` přidat **deterministický krok** (bez ptaní, jako `godot-*`):

```js
// tvar: blender:<skript.py>[:<args za -->]
// Bez tohohle kroku se render skládá z `shell:`, a ten se VŽDY ptá y/N –
// bezobslužný render na uzlu tím pádem není možný.
case 'blender': {
  const [skript, ...dalsi] = rest;
  if (!skript) throw new Error('blender potřebuje skript .py');
  const bin = process.env.FORGE_BLENDER || 'blender';
  return run([quote(bin), '-b', '-P', skript, ...(dalsi.length ? ['--', ...dalsi] : [])]);
}
```

a do `repo\.forge\node\.env`:

```
FORGE_KINDS=assets,test,build
FORGE_BLENDER=C:\Program Files\Blender Foundation\Blender 5.2\blender.exe
```

> **Past:** `blender.exe` vrací **exit 0 i s tracebackem** ve skriptu. Krok proto
> musí kromě exit kódu ověřit, že vznikl očekávaný PNG — jinak uzel nahlásí
> úspěch a spritů se vyrobí nula.

### Jak se taková úloha zadá

Conductor umí cíl úlohy nastavit — `POST /task` bere `target`:

```json
POST /task {
  "title": "Render sady NPC (4 směry × 8 framů)",
  "kind": "assets",
  "target": "lan",
  "prompt": "Spusť tools/blender/build_npc.py a odevzdej sprites/npc/",
  "payload": { "steps": ["blender:tools/blender/build_npc.py"] }
}
```

`target: "lan"` je klíčové — bez něj conductor úlohu dispatchne do GitHubu
(`target='cloud'`), kde Blender není.

### Kdy to má smysl (a kdy ne)

| Má smysl | Nemá smysl |
|---|---|
| konzistentní 3D sada (postava × 4 směry × 8 framů) | jednotlivý 2D sprite (SDXL/Gemini je rychlejší) |
| **stejná kamera a světlo** napříč sadou (vrstvy na sebe) | pixel-art 32×32 |
| opakovaný render po změně rig | jednorázový obrázek do dokumentace |

---

## 6. Návrh 4 — Lokální generátor (ComfyUI/SDXL) na uzlu

Stejná logika jako Blender, ale **jiný problém**: nejde o chybějící binárku
(Gemini to umí taky), ale o **kvótu a reprodukovatelnost**.

| | Gemini (cloud) | ComfyUI (uzel) |
|---|---|---|
| kde běží | kdekoli, i v CI | jen na uzlu |
| kvóta | ano (~20–50/den) | **žádná** |
| reprodukovatelnost | ne | **ano (seed)** |
| dávka | drahá | ~100 s/obrázek na RX 6600 |
| VRAM | — | **konkuruje Ollamě** (8 GB sdílených) |

**Praktický důsledek:** lokální generátor je vhodný na **dávky variant**, které
se pak vybírají (a kde se na výsledek musí podívat člověk/agent — `read_image`
na arch z `--matrix`). Není vhodný jako krok každého běhu agenta: 100 s na
obrázek × desítky obrázků = hodiny a sebere VRAM Ollamě.

**Kde to dnes je:** `obrazky\img.cmd` (skill `imagegen-local`), nezávisle na
orchestře. Napojení by znamenalo krok `img:` v `worker.mjs` — ale **nedoporučuju
to dělat dřív než u Blenderu**, protože přínos je menší a riziko větší.

---

## 7. Nálezy (ne návrhy — věci, které jsem našel a nikdo o nich nevěděl)

1. **`.forge/vision.mjs` je mrtvý kód.** Existuje, má fallback mezi modely
   i korektní chování při chybě — a **žádný workflow ho nevolá**. Buď ho zapojit
   (Návrh 1), nebo smazat. Nechat ho ležet je nejhorší varianta: vypadá jako
   hotová kontrola.
2. **CI vyrábí snímek hry a zahazuje ho.** `ci.yml` platí ~6 minut (apt-get,
   xvfb, Godot) za framy, ze kterých se počítá jen číselná shoda s mapou.
   Chybí jediný řádek s `vision.mjs`.
3. **Brána animace nikdy nic nezkontroluje** — a testy animace přitom **projdou**.
   `check-assets.py` hledá `walk_*.png` v `assets/sprites/`, kde **žádné nejsou**
   (0 souborů); chůze je v `tools/blender/sprites/body_d0_f*.png`. Brána to
   správně ohlásí jako poznámku („animace chůze v projektu není – přeskočeno"),
   takže se nic netváří jako ověřené — ale **kontrola `min_silhouette_iou: 0.80`
   se nikdy neuplatní**, i když má spec `framy: 8`.
   **Změřeno ručně:** IoU sousedních framů je 0.834–0.908, posun těžiště
   0.46–0.99 px (limit 3.0) → animace je **v pořádku**. Není to tedy vada hry,
   ale **slepé místo brány**: kdyby se chůze rozbila, CI to nepozná.
   Stejně tak **hudba**: „hudba ve hře není – měření hudby přeskočeno".
4. **`kind` nic neřídí.** `inputs.kind` je v `agent.yml` jen v šabloně PR
   komentáře (jediný výskyt); všechny granule v roadmapě mají `"kind": "code"`.
   Rozdíl `code | assets | build | research` existuje jen v dokumentaci.
5. **`worker.mjs` odkazuje na smazanou GameForge** (`FORGE_CMD` → `forge.cmd`),
   takže krok `forge:` je nepoužitelný a nikdo to nepozná, dokud ho nepoužije.
6. **`over-skilly.py` padá na vlastním výstupu** — na `cp1252` konzoli vyhodí
   `UnicodeEncodeError` při tisku „řádků". Bez zásahu do skriptu:
   `$env:PYTHONIOENCODING='utf-8'`. Pak hlásí 8/8 OK.
7. **Schéma hry se rozešlo na čtyři čísla** — `spec.json` deklaruje izometrii
   96×48, `level.gd` kreslil 16px čtverce, dlaždice byly 32px a `world.gd` měl
   32px s izometrií, kterou nikdo nepoužíval. **Vyřešeno rozhodnutím uživatele:**
   schéma je **per-game** a autoritou je `assets/spec.json` hry. Nástroj
   `orchestra/tools/kontrola-schematu.py` (= `.forge/check-schema.py`) to hlásí
   jako **tvrdou bránu v CI před vision**; **migrace hry je hotová** (viz
   `PLAN-VISION-ORCHESTRA.md`).
8. **Odkaz na hru v `release.yml` mířil na JINOU hru.** V poznámkách k vydání
   bylo `…github.io/forge-quest/`, ale herní repo je `uo-shadows`. A
   **`forge-quest` je živý repozitář s vlastní hrou i vlastními GitHub Pages**
   (ověřeno přes API: push 30. 9. 2026, pages ANO) — takže kdo odkaz otevřel,
   **hrál jinou hru** a divil se, proč ta „naše" vypadá špatně. Opraveno; odkaz
   se odvozuje z **názvu repa**, nikdy se neopisuje z historie.
9. **Na GitHub Pages běží jen to, co je na `main`.** `release.yml` se spouští na
   push do `main` a staví web + rolling Release. **Necommitnutá práce v klonu
   hry se v prohlížeči nikdy neobjeví** — což je přesně důvod, proč uživatel
   viděl starou (neizometrickou) verzi, i když jsem měl migraci hotovou na disku.
10. **Klon hry je 2 commity pozadu a upstream změnil i `project.godot`.** Na
   `main` přibyl hráč (PR #25, `e4be7c2`) a do `project.godot` sekce `[input]`;
   `window/size` tam **zůstalo na 480×270**. Při sloučení se **nesmí přepsat
   `viewport 960×540`**, jinak se izometrická migrace tiše vrátí.
11. **Tvrdá brána schématu TIŠE PŘESTALA MĚŘIT — a to až PO migraci, kterou
    sama měla hlídat.** Naměřeno 1. 10. 2026 při ověřování této dokumentace:
    `check-schema.py` hledal výchozí buňku v `scripts/level.gd` vzorcem
    `var cell := 16`. Migrace na izometrii z toho udělala
    `const CELL_W_DEFAULT := 96` + `const CELL_H_DEFAULT := 48`, takže regexy
    nenašly **nic**, cyklus proběhl nad **prázdným seznamem** — a kontrola
    hlásila „Schéma je v souladu". Jediné, co to prozrazovalo, byl řádek
    `level.gd: výchozí cell=[], fallback=[]`; `[]` přitom vypadá jako
    naměřená nula.
    **Proč je to poučení pro orchestra:** brána nebyla rozbitá v logice, ale
    v **předpokladu o tvaru kódu** — a nikdo si toho nevšiml, protože zelená
    od brány se čte jako „prošlo", ne jako „proběhlo". Opraveno (měří oba
    tvary, hlásí vadu, když číst nelze, rozlišuje šířku a výšku) + offline test
    `orchestra\tools\test-check-schema.py` (17 testů se známým správným
    i chybným repem) zapojený do `validate-all.mjs`. Test při psaní odhalil
    i **drift mezi šablonou `repo/` a herním repem** — proto hlídá shodný hash.
    **Pozor:** oprava je zatím jen v pracovním stromu klonu; dokud se
    necommitne, CI ve hře vidí pořád tu slepou verzi.

12. **Conductor je čistý, ale jeho provozní smyčka má tři naměřené vady.**
    Naměřeno 1. 10. 2026 (analýza architektury). Nejdřív dobrá zpráva:
    `conductor/src/index.ts` (1359 řádků) **neobsahuje ani jeden výskyt**
    `forge-quest`, `gameforge`, `uo-sandbox`, `forge.cmd` ani `--router` —
    dědictví po GameForge je v orchestra jen v **nástrojích a šabloně**, ne
    v mozku. Co ale v mozku nefunguje:
    - **Nová granule se 3 h nevydá.** `roadmapTick` zapíše řádek roadmapy
      s `updated_at = now` (`:643-646`), ale dispatch guard se ptá **jen na
      čas** (`:796-804`) — tedy na tentýž sloupec jako cooldown po selhání.
      Replika obojího SQL v SQLite: nová granule → `[]`, týž řádek starý 4 h
      → `[1]`. **Navenek to vypadá jako „orchestra nic nedělá", a `/queue`
      přitom hlásí `ready`.** Vzniklo opravou `621c312`, která z guardu
      odstranila `rm.status='failed'` (správně) — ale guard tím začal chytat
      i čas založení.
    - **Cooldown se u selhání přes `/report` obchází.** `/report` (`:1329-1336`)
      zapíše jen `tasks`, `roadmap.updated_at` ne; `pollRuns` to dělá správně
      (`:403-405`).
    - **Strop pokusů váže úkol, ne granuli.** `MAX_ATTEMPTS` **žije** (`:328`,
      `:394`, `:679`, `:709`, `:1329`) — mrtvý je jen komentář `:31`/`:233`,
      který tvrdí opak. Ale `roadmapTick` zakládá pro každý retry **nový úkol
      s `attempts=0`**, takže granule jede donekonečna — a watchdog
      `ESCALATE_AFTER` (prah 8 > strop 5, počítá běhy úkolu) **se nikdy
      nespustí.**
    - **Zámek souborů v dispatch smyčce neblokuje nic.** `:774-776` staví
      `locked` z holých jmen, `:806` porovnává s klíči `{repo}/{soubor}`.
      Následek dnes nulový (roadmapa hry nemá kolizi `owns`), ale
      `lint-roadmapa.py` u kolize tvrdí „poběží sériově" — **není pravda.**
    - **`listGames` fallback** (`:447-454`) znamená, že vypnutí poslední
      registrované hry orchestra **nezastaví**; a `/tasks/cleanup` s vypnutou
      hrou **smaže cache roadmapy** (`:1120`, `:1184`).
    **Poučení pro orchestra:** tohle není „brána, která neměří" — to je
    **chyba v tom, co je zdroj pravdy o čase** (`updated_at` nese dvě různé
    věci: „vzniklo" i „naposledy selhalo"). Celý rozbor:
    `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`, podklady:
    `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`.
13. **Tvrdá brána, na kterou se orchestra sama odvolává, se neměří tou
    správnou kopií.** `orchestra/tools/kontrola-schematu.py` je **jiný
    a starší** soubor než nasazený `.forge/check-schema.py` (305 vs. 461
    řádků, jiný hash — chybí mu hlášení mrtvé větve `world.gd`) — a
    `validate-all.mjs:186` pouští **právě ten starý**. Naměřeno: tiskne
    `level.gd: výchozí cell=[], fallback=[]` a „Schéma je v souladu" s exit 0,
    tedy přesně ten podpis tichého selhání, který tahle session opravovala.
    Navíc `validate-all.mjs` **končí exit 0 i při `✗ NALEZENO 3 PROBLÉMŮ`**
    (měřeno), takže se na něj nedá spolehnout ani v CI.
14. **Šablona `repo/` v gitu není to, co je na disku.** Naměřeno: **8
    změněných** trackovaných souborů (z toho `vision.mjs` +422 řádků) a **4
    netrackované**, které hra potřebuje — `.forge/check-schema.py`,
    `.forge/baseline.py`, `.forge/vision-profile.json`,
    `.forge/node/vision.test.mjs`. `release.yml` **v gitu** navíc stále
    odkazuje na `…github.io/forge-quest/` (na disku opraveno, necommitnuto).
    Kdo orchestra naklonuje, dostane šablonu bez bran, s cizím odkazem a
    s roadmapou plnou granul staré hry (nález 15). V `tools/` je to stejné:
    **51 untracked**, z toho **24 trvalých nástrojů** (mj. `git.cmd`,
    `status.mjs`, `validate-all.mjs`, `zjisti-pages.mjs`).
15. **Roadmapa v šabloně je plán STARÉ hry.** `orchestra/repo/.forge/roadmap.json`
    obsahuje **31 granul** (`chest-unlock2`, `minimap`, `lives-hud`, `exit-win2`…)
    a `_popis` odkazuje na smazaný `forge plan`. Protože
    `install-into-repo.ps1:94-97` kopíruje `.forge` **rekurzivně a bez filtru**,
    **každá nová hra tenhle plán zdědí** — a to je přesně mechanismus, kterým
    se „pozůstatky forge-quest" dostávají do nových her (spolu s
    `vision-profile.json`, který má natvrdo `"hra": "uo-shadows"`).
16. **Zakládání nové hry je mrtvá větev.** `install-into-repo.ps1:36-38`
    vyžaduje `projects\<Projekt>`, ale `projects/` **neexistuje** (smazáno
    s GameForge); `:86` posílá uživatele na smazaný `forge.cmd pull`.
    Onboarding tedy dnes neexistuje — což je i důvod, proč se nová hra zakládá
    ručním kopírováním a dědí pozůstatky.
17. **`.env` s reálným `FORGE_SECRET` se kopíruje do hry, která ho neignoruje.**
    `repo/.forge/node/.env` obsahuje skutečný secret a `install-into-repo.ps1`
    ho přenese; `.gitignore` hry (generovaný `:116-145`) ale `.env`
    **neobsahuje** (ověřeno `git check-ignore`). V herním repu dnes ten soubor
    **není**, takže k úniku ještě nedošlo — ale `git add -A` v agentovi by ho
    vzal do patche i do PR. **Přidat `.env` do generovaného `.gitignore`.**

> **Stav k 1. 10. 2026:** nálezy 1–2, 7–8 jsou **vyřešené** (vision v `ci.yml`,
> kontrola schématu před ním, migrace hotová, odkazy opravené), **11 je
> opravený v herním repu i v šabloně na disku** (měřeno: obě kopie mají shodný
> hash a brána hlásí `výchozí buňka=96×48px`), 3–6 čekají na
> rozhodnutí, 9–10 jsou provozní fakta. **12–17 jsou nové nálezy analýzy
> architektury z 1. 10. 2026** a **žádný z nich není opravený** — 12 jsou
> provozní vady conductoru (nejdražší: 3h zpoždění každé nové granule),
> 13–17 jsou vady obálky (git, onboarding, kopírování). Rozbor, doporučení
> a co analýza **nezjistila**: `ANALYZA-ARCHITEKTURY-ORCHESTRA.md`.

---

## 8. Co orchestra dělat NEBUDE

| Nápad | Proč ne |
|---|---|
| Blender v `ubuntu-latest` | ~300 MB instalace, render na softwarovém OpenGL, 60min timeout — lokální uzel vyhraje vždy |
| `read_image` v CI | runner nemá vision; v CI je `vision.mjs` (Gemini) — jiná věc se stejným účelem |
| Generovat assety v běhu agenta | agent v CI nemá GPU ani Blender; smí editovat jen soubory, které dostane |
| Nechat auto-merge slučovat assety bez kontroly | gate pustí `assets/*` a dnes to nikdo nevidí (rozhodnutí 2 v §1) |
| Přidat `kind: assets` a čekat, že se něco stane | `kind` dnes nic neřídí (nález 4) |

---

## 9. Pořadí, v jakém bych to dělal

| # | Krok | Kde se mění | Riziko | Ověření |
|---|---|---|---|---|
| 1 | Zjistit stav orchestra a hry | nic | — | `node orchestra\tools\status.mjs` |
| 2 | Kontaktní arch na dnešní assety | **hotovo** (`tools\kontaktni-arch.py`) | — | arch vizuálně zkontrolován |
| 3 | `vision.mjs` do `ci.yml` (Návrh 1) | `repo/` + `uo-shadows` | nízké (`continue-on-error`) | CI na PR a vidět verdikt |
| 4 | Doplnit bránu animace (nález 3) | `check-assets.py` nebo cesty spritů | nízké | `check-assets.py` začne měřit IoU |
| 5 | Uzel nahoru + krok `blender:` | `repo\.forge\node\` | střední (uzel je živý proces) | jedna LAN úloha se spritem |
| 6 | Tvrdá brána pro `kind: assets` | `agent.yml` | střední (může blokovat slučování) | až po několika zelených bězích |
| 7 | Lokální generátor jako krok uzlu | `worker.mjs` | vyšší (VRAM, čas) | jen když 5 funguje |

Nasazení conductora se **nikdy** nedělá lokálním `wrangler deploy` — jen pushem
do `main` v `orchestra/conductor/**` (viz `orchestra/README.md`). Změny v `repo/`
a v herním repu jdou normálním pushem.

---

## 10. Kam pro související věci

| Dokument | Co v něm je |
|---|---|
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` (workspace) | **analýza architektury z 1. 10. 2026** — tři třídy tichých selhání, 16 tříd selhání (S1–S16), odpovědi na 15 otázek, co je rozhodnutí a co nános, co analýza nezjistila |
| `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md` (workspace) | úplné podklady: audit conductora po řádcích, inventura `tools/`, audit domácího uzlu, spustitelný měřič cooldownu |
| `ARCHITEKTURA-ANALYZA-ZADANI.md` (workspace) | zadání té analýzy — vzor, jak psát zadání pro novou session |
| `MOZNOSTI-AGENTA.md` (workspace) | co agent umí — `read_image`, Blender, ověřené cesty a důkazy |
| `orchestra/README.md` | struktura, deploy, API, jak agent dostane soubory, cooldown, watchdog |
| `orchestra/repo/.forge/check-assets.py` | jak vypadá měření assetů (spec, brány, hudba) |
| `orchestra/repo/.forge/vision.mjs` | „oči" pro CI (Gemini) — **zapojené** do `ci.yml` jako neblokující krok (`continue-on-error`) |
| `orchestra/repo/.github/workflows/ci.yml` | kde se vyrábí snímek hry (krok „Vizuální kontrola") a kde na něj navazuje vision |
| `orchestra/tools/test-check-schema.py` | offline testy tvrdé brány schématu (nález 11) — známý správný i chybný případ |
| `AGENTS.md` (workspace) | **trvalá pravidla** pro agenty (jak ověřovat, pasti prostředí, co se nesmí) |
| `~\.dsh\skills\dsh-prostredi\SKILL.md` | pasti prostředí, které vypadají jako chyba logiky |
| `games/uo-shadows/assets/spec.json` | `_stav`: co je schválené (milník 1) a co je plán |
| `~\.dsh\skills\game-assets\SKILL.md` | kdy stáhnout / vygenerovat / vymodelovat, Blender headless |
| `~\.dsh\skills\orchestra\SKILL.md` | operativa orchestra, invarianty, „assety a oči orchestra" |
| `HANDOFF.md` (workspace) | historie: 8 vad orchestra a jak se našly |

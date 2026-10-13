# K4 — nová hra Coin-Picker: skeleton, registrace a pilot end-to-end

> **Co tenhle dokument JE:** **záznam o provedení + stav** session K4
> (13. 10. 2026). Navazuje na `K3-ROZDELENI-KONVENCI.md`.
> **Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, vlastní ho P41) ani kronika
> (`KRONIKA-PROJEKTU.md`) — `HANDOFF.md` jsem **needitoval**.
>
> **Datum spotřeby:** co je tu o stavu (commity, běhy, aktivní hra, pokusy),
> se musí **živě přeměřit**. Naměřeno 13. 10. 2026 mezi 11:45 a 12:10 UTC.

---

## 1. Co je hotové

| # | Výstup | Stav | Doloženo |
|---|---|---|---|
| 1 | Nová hra jako repozitář | **HOTOVO** — `ssevcikm-spec/coin-picker` (public), workspace `E:\Workspaces\coin-picker`, `main` = `ef2107d` | `git rev-parse origin/main` |
| 2 | Běžící skeleton (ne prázdná šablona) | **HOTOVO** — mapa 15×8 s dlaždicemi, hráč s pohybem a kolizí, skóre přes signál do HUD, 2 sprity, generátor assetů | `tests/run_tests.gd` **33/33**, `check-schema` / `check-assets` / `check-wiring` **exit 0** |
| 3 | CI hry zelené | **HOTOVO** — běh `ci.yml` **#3** (`success`): testy · schéma · assety · zapojení · smoke · **vizuální kontrola 120/120 políček** · export Linux+Web | https://github.com/ssevcikm-spec/coin-picker/actions/runs/38392173544 |
| 4 | Secrety a proměnná hry | **HOTOVO** — secrety `FORGE_PAT`, `FORGE_WEBHOOK_SECRET`, `GROQ_API_KEY`, `OPENROUTER_API_KEY`; proměnná `FORGE_CONDUCTOR_URL` | `GET /actions/secrets` (jen jména) |
| 5 | Registrace v conductoru | **HOTOVO** — `POST /game` → `active=1`; `uo-shadows` **deaktivována** (`active=0`) | `GET /games` |
| 6 | **Pilotní granule end-to-end** | **HOTOVO** — `world.coin`: request **5 794 t**, `REQUEST_FITS`, testy **33/33**, PR **#1 automaticky sloučen** (commit `496d366`) | běh https://github.com/ssevcikm-spec/coin-picker/actions/runs/38393453056 |

**Pilotní běh v číslech** (výpis z logu, ne odhad):

```
ROZPOCET: ~5794 tokenu (zadani 365 + editace 0 + cteni 0 + konvence 1129 + rezie 1800 + obal zadani 2500)
STROP (groq/openai/gpt-oss-120b, mereno): 8000 tokenu | zbyva 2206   → TRIDA=REQUEST_FITS
Vybráno: groq → openai/gpt-oss-120b        (granule model=strong → zužuje se na strongModels)
[test] 33 kontrol, 0 selhání
skutecne zmeny: scripts/coin.gd            klasifikace: OK
```

**Brána před dispatchem předpověděla 5 794 t — a běh naměřil 5 794 t.** To je
kalibrace celého K3 mechanismu na reálném CI (ne na modelu).

**Kritéria zadání §3/4 a jak dopadla:**

| Kritérium | Výsledek |
|---|---|
| request ≤ 7 000 t naměřeno poskytovatelem | **5 794 t** ✅ |
| v `/status` pojmenovaná příčina, ne `GitHub Actions: failure` | ✅ log nese `TRIDA=REQUEST_FITS` / `klasifikace: OK`; klasifikátor K2 funguje |
| PR vznikne, nebo se pojmenuje proč ne | ✅ **PR #1 vzniklo a automaticky se sloučilo** |
| při vypnutém prvním zdroji nastoupí druhý | ⚠ **NEOVĚŘENO** — rotace se spouští až po neúspěchu (nochange/selhání); úspěšný běh ji nevyvolá. Kód cesty je K2 a kryjí ho testy klasifikátoru, ale **během** to doložené není |

---

## 2. Nálezy (každý z měření, ne z dojmu)

### F1 — Deklarace konvencí se musí volit podle toho, CO granule dělá

**První pilotní běh** (`world.coin`, run 38393167445) vyrobil `scripts/coin.gd`
a **spadl na parse bráně**:

```
Parse Error: Invalid argument for "connect()" function: argument 2 should be "Callable" but is "res://scripts/coin.gd"
Parse Error: Cannot pass a value of type "String" as "int"
```

Model napsal **Godot 3** `connect("body_entered", self, "_on_body_entered")`.
A to je přesně pravidlo, které je v sekci **`05-godot3-konstanty`** — kterou
jsem té granulе **neposlal** (deklaroval jsem `06-soubor-granule`
a `07-uzel-a-kostra`). Nebyl to model, kdo selhal: **byla to moje deklarace.**

**Náprava (změřeno, ne odhadnuto):** `world.coin` i `entity.enemy` deklarují
`01-typy` + `05-godot3-konstanty` (1 129 t, vejde se pod strop 1 200 t), kontrakt
o syntaxi Godotu 4 je **v zadání** (jedna věta) a tentýž běh po opravě prošel.
Poučení je obecné: **`konvence` není formalita — je to volba toho, které
známé pasti model dostane. Když ji uděláš špatně, dostaneš chybu, kterou
projekt už má popsanou.**

### F2 — `export_presets.cfg` v šabloně CHYBÍ, takže každá nová hra spadne na posledním kroku CI

`ci.yml` exportuje presety **jménem** (`--export-release "Linux"`, `"Web"`).
Soubor s presety ale v `repo/` není → běh #1 i #2 měly všechny brány zelené
a **CI červené na „Export buildů“**. Coin-Picker ho má; **do šablony patří taky.**

Navíc: `include_filter="assets/levels/*.json"` je podstatný — mapa je obyčejný
JSON, ne importovaný resource; bez filtru by se do buildu nedostala a hra by
mapu v exportu nenašla (a CI by přitom bylo zelené).

### F3 — Dvě z pěti bran hry se LOKÁLNĚ ověřit nedají

* **vizuální kontrola** potřebuje vyrenderovaný snímek (lokálně jsem ho dostal
  přes `--write-movie`, ale je to mimo CI postup),
* **export** potřebuje exportní šablony, které stahuje `install-godot.sh` v CI.

Naměřeno na vlastní kůži: skeleton měl lokálně „vše zelené“ a v CI spadl
**dvakrát** (render, pak export). **„Zelené lokálně“ není totéž co „hra je
v pořádku“** — a platí to i pro brány, které vypadají jako totéž.

### F4 — Conductor má token bez `Actions: write`

`/status` nese pojmenovanou příčinu (což je správně, K2):

```
GitHub dispatch 403: {"message":"Resource not accessible by personal access token",
 "documentation_url":"https://docs.github.com/rest/actions/workflows#create-a-workflow-dispatch-event"}
```

Conductor **roadmapu hry přečetl a granule naplánoval** (`ready: 3 → 5`,
úlohy #247 `world.coin`, #248 `entity.enemy`), ale **nedispečuje**. Token vidí
repo (roadmapu přečte) a neumí zapsat obsah ani dispatchnout — chybí mu
**Actions: Read and write**. Oprava je **jedno pole v nastavení toho tokenu**
(hodnota se nemění, takže se nemusí nic přenastavovat v Cloudflare).

⚠ **Každý tik = +1 pokus granule** (`#247` mělo po ~4 minutách `attempts: 4`),
takže jsem hru **dočasně deaktivoval**, aby 403 nespálila pokusy (strop je 8).

### F5 — `depends_on` je i KONTEXT, ne jen pořadí

Workflow čte soubory závislostí přes `--read`, takže **každá závislost se platí
tokeny**. Naměřeno (při opravě brány v K3): integrační granule se čtyřmi
závislostmi měla request **9 822 t > 8 000**; se smlouvou v zadání místo čtení
dalších souborů **6 937 t**. `rozpocet-granuli.mjs` proto nově počítá
i **soubor závislosti, který ještě neexistuje** (při běhu existovat bude).

### F6 — `validate-all` je postavený na JEDNÉ hře (a přepnutí hry ho rozsvítí)

Po registraci druhé hry a deaktivaci `uo-shadows` (obojí schválené zadáním)
`node tools\validate-all.mjs` hlásí **7 problémů** místo 3. Čtyři nové mají
jeden kořen — **validátor předpokládá, že aktivní hra je `uo-shadows`**:

| Kontrola | Co naměřila | Proč to není vada dat |
|---|---|---|
| `je registrovaná hra` / `je aktivní` | `games=0`, `active=0` | `uo-shadows` je záměrně vypnutá; aktivní je `coin-picker` |
| `cache neobsahuje osiřelé řádky` | `osiřelé=2` | **nejsou osiřelé** — jsou to granule DRUHÉ hry |
| `cache není větší než soubor` | `cache=22, soubor=21` | 20 řádků `uo-shadows/*` + **2 řádky `coin-picker/*`** |

**Doloženo živě** (`GET /roadmap`, 22 řádků): `coin-picker/world.coin`,
`coin-picker/entity.enemy` + 20× `uo-shadows/*`. Mechanismus „orchestra se
přepíná mezi hrami“ **existuje** (`POST /game/active`) — validátor o něm ale
neví a měří cache proti souboru jedné hry. **Není to regrese, je to slepé
místo brány** (třída S27: kontrola, která se ptá na jiný stav, než jaký
ve stromě je).

**A jedna věc, která naopak sedí:** `coin-picker/world.coin` má v D1
`attempts=5` (spálily je 403 na dispatch), ale v souboru je `done: true` →
conductor ji přeskočí. Doloženo kódem: `conductor/src/index.ts:1130`
(`if (i.done === true …) continue;`) a `:1150` (`i.done !== true` ve filtru
připravených).

---

## 3. Co je BLOKOVANÉ a co je další krok

**Blokované (na uživateli, jedno kliknutí):**

1. **Token conductora → `Actions: Read and write`** (fine-grained PAT, který
   conductor používá jako `GITHUB_TOKEN` v Cloudflare). Bez toho conductor
   granule naplánuje, ale nevydá.
2. **Hra je DEAKTIVOVANÁ** (`active=0`) — po opravě tokenu ji aktivovat:
   `POST /game/active {"game_id":"coin-picker","active":true}`.
   Pak conductor vydá zbylé tři granule (`entity.enemy`, `world.spawner`,
   `core.wiring`) sám; `world.coin` je označená `done: true`, takže ji přeskočí.

**Další krok (můj, nezávislý na tokenu):**

3. **Zobecnit `forge new`** — hru jsem postavil ručně (kopie šablony + skeleton
   + roadmapa). Generátor s testem znamená, že další hra je **jeden příkaz**;
   součástí je i doplnění šablony o to, co tahle hra odhalila jako chybějící:
   `export_presets.cfg` a skeleton (`project.godot`, `main.tscn`,
   `tests/run_tests.gd`, `assets/spec.json` + minimální assety).
4. **Doplnit `kontrola-driftu.mjs`** o nástroje `.forge/node/*` — při zakládání
   hry se kopírují, ale drift je nehlídá, takže se šablona a hra mohou rozejít
   (naměřeno v K4: musel jsem je synchronizovat ručně).
5. **`validate-all` naučit, která hra je aktivní** (nález F6) — dnes hlásí
   4 problémy, které nejsou vadami dat. Buď ať se ptá `/games` (aktivní hra),
   nebo ať cache srovnává **po hrách** (`{game}/*`), ne proti jednomu souboru.
   Do té doby platí: **4 z 7 problémů `validate-all` jsou o přepnutí hry,
   ne o kódu** — a to je přesně tahle věta, kterou je potřeba číst, aby se
   nezačalo „opravovat“ zdravý strom.

---

## 4. Prompt pro další session

```text
Jsi session K5. Repo orchestra = E:\Workspaces\forge-orchestra.
Hra uo-shadows = E:\Workspaces\uo-shadows je ZMRAZENÁ — jen čti, nepiš do ní.
Nová hra = E:\Workspaces\coin-picker (repo ssevcikm-spec/coin-picker), hra JE ŽIVÁ.
Ve stromě orchestry může být necommitnutá práce P41 — nesahej na ni.

Kontext: K3 rozdělila konvence na sekce a zavedla rozpočet requestu; K4 postavila
hru Coin-Picker a provedla pilot (request 5 794 t naměřeno, PR #1 sloučeno).
Záznamy: K3-ROZDELENI-KONVENCI.md a K4-PILOT-COIN-PICKER.md — přečti OBA CELÉ.

NEJDŘÍV (měř, nečti z dokumentu):
1) /health conductora: last_cron (dva vzorky 60 s od sebe) + /games (je coin-picker
   aktivní?) + /queue (kolik granul je ready a jaké mají attempts).
2) Je v novém repu opravený token? Ověř to BĚHEM, ne dohadem: `/status` conductora
   buď ukazuje dispatch_failed s 403 (token pořád chybí), nebo běžící úlohu.
3) git status --porcelain v orchestra i v coin-pickeru (co je necommitnuté).

PAK podle stavu:
A) Token opravený → conductor vydá zbylé granule sám. Sleduj `entity.enemy`,
   `world.spawner`, `core.wiring`: u každé ověř request (ROZPOCET … TRIDA=REQUEST_FITS),
   že se rozsvítily její kontroly v testech, a že PR vzniklo/sloučilo se.
   ⚠ `core.wiring` je navržený jako STRESOVÝ případ (rozpočet 7 388 t z 8 000) —
   když neprojde, je to nález o rozpočtu, ne o modelu.
B) Token pořád chybí → neposílej nic naprázdno (každý tik spálí pokus);
   udělej krok 3–4 z §3 (forge new + drift) a připrav, co půjde po opravě.

BRÁNY (v tomto pořadí, nic mezi tím):
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
python _analyza\g3-brany.py            # POZOR: FORGE_REGISTR mimo repo, stavíš-li harness
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
node tools\validate-all.mjs
python tools\kontrola-diakritiky.py ; python tools\over-dokumentaci.py ; python tools\over-skilly.py
node tools\kontrola-driftu.mjs          # očekávej 1 rozdíl + 2 záměrné (viz K3 §5)
a v HRĚ: node .forge\node\rozpocet-granuli.mjs --poskytovatel groq --model openai/gpt-oss-120b

NEDĚLEJ: nezvedej GRAIN_MAX_RUNS/MAX_ATTEMPTS, necommituj soubory P41,
nespouštěj kontrola-driftu.mjs --sync (uo-shadows je zmrazená), nedávej do zadání
granulí cesty k souborům (přitáhne celý dokument) a NEODSTRANUJ `done: true`
u `world.coin` (pilot ji dokončil).
```

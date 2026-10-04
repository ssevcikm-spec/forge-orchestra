# Plán: vizuální kontrola (vision) ve Forge Orchestra

> **Co tenhle dokument JE:** plán. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

**Datum:** 30. 9. 2026 · **Stav:** schváleno; **F-1, F0 a F1 HOTOVÉ** (viz §13)
**Navazuje na:** `FORGE-ORCHESTRA-MOZNOSTI.md` (možnosti), `MOZNOSTI-AGENTA.md`
(co agent umí), `games/uo-shadows/docs/ARCHITEKTURA.md` + `assets/spec.json`
(závazné téma projektu)

---

## 0. Shrnutí pro netrpělivé

| Otázka | Odpověď v jedné větě |
|---|---|
| Jaký význam má vision? | Doplňuje **třetí vrstvu**, kterou dnes orchestra nemá: „je na tom obrázku to, co tam má být?" — měření a testy to neumí. |
| Jaký dopad? | Reálný, ale **menší, než se čeká** — u `uo-shadows` by dnes nechytila nic, protože projekt je ve fázi kódu, ne vzhledu. Přínos přichází s fází assetů. |
| Jak volat, aby to bylo přesné? | **Neposílat dotaz, posílat očekávání.** Model nemá hodnotit, má vypisovat, co vidí, a porovnat to se seznamem z `main.json`. Plus 2 běhy na self-consistency. |
| Kdo to čte? | **DeepSeek jako dělník** (rutinní kontroly, tisíce obrázků), **Gemini jako rozhodčí** (styl, diff, sporné případy). Ne naopak. |
| Kam to zapadne? | 4 nová kontrolní místa; **jen jedno je automatické v CI** (nad snímkem hry, který se už vyrábí). Ostatní jsou pro session a uzel. |
| Lze cachovat a schvalovat? | **Ano — a je to podmínka, ne vylepšení.** Bez cache a bez zámků to spálí kvótu a sebere ti kontrolu. Mechanismus je v §8. |
| Co ještě zvážit? | 12 rizik v §9 — nejvážnější je **Goodhart**: systém se začne učit procházet kontrolou místo aby vypadal dobře. |
| Další nástroje? | Většina nejužitečnějších **není vision** — pHash, SSIM, ΔE v CIELAB, CLIP embedding, optický tok. Vision je jen jedna z pěti vrstev (§10.1). |
| **Je schéma per-game?** | **ANO a je to tak navržené** (odpověď uživatele 30. 9. 2026). Autorita je `assets/spec.json` **té které hry**; nástroje v něm nesmí mít nic zadrátované — ověřeno testem, který pouští vision na hře s čtvercovou projekcí a dlaždicí 24 px. |
| **Co dělat PRVNÍ** | ~~Rozhodnout rozpor v zadání~~ → **vyřešeno**: platí `spec.json` jako per-game deklarace. Zbývá domigrovat `main.json`, `level.gd`, `world.gd` a dlaždice (§4.2b). |

---

## 13. Co je HOTOVÉ (30. 9. 2026) — stav proti původnímu plánu

| Fáze | Stav | Co konkrétně |
|---|---|---|
| **F-1** sjednotit schéma | **HOTOVO CELÉ** | Nástroj `orchestra/tools/kontrola-schematu.py` = `.forge/check-schema.py`, **tvrdá brána v `ci.yml` před vision** — a **migrace hry provedena**: `spec.json` je autorita, mapa i dlaždice a renderer jsou s ním v souladu. Kontrola hlásí **„Schéma je v souladu"** (exit 0). ⚠️ 1. 10. 2026 se ukázalo, že kontrola výchozí buňky v `level.gd` po migraci **tiše přestala měřit** — opraveno, viz past 4 níž. |
| **F0** vision v CI s Gemini | **HOTOVO** | Krok „Vizuální kontrola – obsah snímku (vision)" v `ci.yml` (herní repo **i** šablona). `continue-on-error: true`, `\|\| echo`, přeskočí se bez klíče. |
| **F1** prompty L2/L3 + self-consistency | **HOTOVO** | `.forge/vision.mjs` přepsán: režimy `presence`/`diff`, očekávání **počítané z mapy**, BOM-safe, **timeout na volání** (60 s), řetěz DeepSeek→Gemini z profilu. |
| **Per-game profil** | **HOTOVO** | `.forge/vision-profile.json` – **bez** dlaždic a projekce (ty jsou ve `spec.json`), se zákazy soudů v promptu a se stropy. |
| Offline testy vision | **HOTOVO** | `.forge/node/vision.test.mjs` → **34 testů** proti mock API (bez sítě a bez klíčů); 28 bylo před přidáním testů cache (F0b/F2). |
| Test CI workflow | **HOTOVO** | `orchestra/tools/test-ci-workflow.mjs` → **36 testů** (YAML, existence volaných souborů, kritické pořadí kroků). |
| **F0b** baseline + LGTM cache | **HOTOVO (nástroj)** | `.forge/baseline.py` — `init`/`stav`/`schval`/`zamitni`/`kontrola`, **24 offline testů**. Cache je zapojená do `vision.mjs` a **ověřená měřením**: schválený obrázek = **0 volání modelu**. ⏳ Zbývá jen tvé LGTM (viz níž). |
| **F2** cache (pHash) | **HOTOVO** | `imagehash` doinstalován; cache používá **phash + barevný podpis** (viz dvě mezery níž). Zamítnuté se re-checkuje vždy. |
| **F3** DeepSeek jako dělník | **připraveno** | Je v profilu jako první článek řetězu; klíč do Secrets herního repa se doplní, až F0 ukáže potřebu. |
| F4–F7 | **NE** | V pořadí podle §11. |

### Migrace na izometrii — provedena (30. 9. 2026)

Rozhodnutí uživatele: **„Migrovat hru na izometrii 96×48 (podle spec.json)"**.
Provedeno a ověřeno:

| Co | Bylo | Je |
|---|---|---|
| `project.godot` viewport | 480×270 | **960×540** (sprites 128 px a dlaždice 96 px na sebe teď pasují) |
| `main.json` `cell` | 16 | **96** (+ `viewport` 960×540) |
| `main.json` mřížka | 30×16 znaků | **beze změny** — mřížka je projekčně neutrální |
| `assets/tiles/*.png` | 32×32 čtverce | **96×48 kosočtverce** (6 dlaždic, `make_iso_tiles.py`) |
| `scripts/level.gd` | osově zarovnané čtverce | **izometrie 2:1**, schéma čte ze `spec.json` |
| `scripts/world.gd` | 32 px + nepoužívaná `iso_position` | **přesunut do `_retired/`** (mrtvý kód s druhým číslem mřížky) |
| `game.gd` | — | volá `level.vystredni_na_spawn(...)` — spawn byl v izometrii pod obrazovkou |

**Ověřeno měřením, ne dojmem:**

| Kontrola | Výsledek |
|---|---|
| Testy hry (Godot headless) | **36 kontrol, 0 selhání** — včetně nových testů projekce 2:1 (krok 48/24 px) a zpětného převodu `cell_at` |
| `check-assets.py` | „Vše v pořádku: assety odpovídají specu" |
| `check-wiring.py` | „každá funkce je odněkud volaná" (54 funkcí v 6 souborech) |
| `check-schema.py` | **„Schéma je v souladu"** (exit 0) — poprvé v historii projektu |
| `verify-level-render.py` | **99,5 % shody** (207/208 políček) — vykreslená mapa odpovídá JSONu |
| Vizuální kontrola (`read_image`) | na snímku 960×540 je **hráč i NPC vycentrovaní na spawnu**, mince vpravo dole, mapa je izometrická 2:1 |

**Čtyři pasti, které se při migraci našly** (všechny by prošly jako „hotovo"):

1. **Hráč nebyl vidět.** Izometrické dlaždice dostaly `z_index = (x+y)*2` (od 0 výš),
   ale hráč má `z_index = 5` a mapa `-1` → dlaždice hráče překryly. Na snímku byla
   krásná izometrická mapa a **žádný hráč**. Řešení: dlaždice od `-2000`.
   *Nebýt vizuální kontroly, tvrdil bych, že migrace je hotová.*
2. **Metrika švu měřila něco jiného, než tvrdila** — třikrát. Nejdřív počítala
   přechod do průhledných rohů (šev 8–16), pak hledala pixely na krajních
   sloupcích kosočtverce, kde žádné nejsou (**0,00 pro všechno** – nula vypadá
   jako dokonalý výsledek, ale je to důkaz, že se nic nezměřilo), a potřetí
   skládala arch do obdélníkové mřížky, kde se kosočtverce nepotkávají (18–33).
   Teprve čtvrtá verze — poměr švu k vnitřku dlaždice na správně složeném archu —
   dala použitelná čísla (0,27–1,43).
3. **Kontrola schématu hlásila falešný poplach i po opravě**, protože hledala
   starý text – a nakonec ho našla **ve vlastním komentáři**, který starý vzorec
   citoval jako historii. Statická kontrola musí číst KÓD, ne komentáře.
4. **Tvrdá brána po migraci TIŠE PŘESTALA MĚŘIT** (nalezeno 1. 10. 2026 při
   ověřování dokumentace). Kontrola výchozí buňky v `level.gd` hledala vzorec
   `var cell := 16`; migrace z něj udělala `const CELL_W_DEFAULT := 96`, takže
   regexy nenašly nic, cyklus proběhl nad **prázdným seznamem** – a brána
   hlásila „Schéma je v souladu". Prozrazoval to jen řádek
   `level.gd: výchozí cell=[], fallback=[]`, protože `[]` vypadá jako naměřená
   nula. **Ironie je zásadní:** brána, kterou F-1 zavedla, aby rozpor odhalila,
   po vlastní migraci přestala měřit – a všechny ostatní kontroly (testy,
   assety, render) zůstaly zelené, protože měřily proti schématu, které už
   nikdo neověřoval.
   **Opraveno:** měří oba tvary deklarace, **hlásí vadu**, když buňku přečíst
   nelze („kontrola NEPROBĚHLA" není totéž jako „je to v pořádku"), rozlišuje
   šířku od výšky (u izometrie 96×48 se liší) a pojmenovává **mrtvé větve**
   (po přesunu `world.gd` do `_retired/` se kontroly na něj už nikdy nespustí).
   **Pojistka:** `orchestra/tools/test-check-schema.py` – 17 offline testů se
   známým správným i chybným repem, spouští `validate-all.mjs`. Test při psaní
   odhalil **čtyři chyby ve vlastním regexu** a **drift mezi šablonou `repo/`
   a herním repem**, proto hlídá i shodný hash obou kopií.
   ⚠️ Oprava je zatím pouze v pracovním stromu klonu hry – **do commitu patří**
   (`games/uo-shadows/.forge/check-schema.py`), jinak v CI běží pořád ta slepá
   verze.

**Poučení:** u vizuální změny je „testy prošly" slabý důkaz. Hráč nebyl vidět,
testy byly zelené, kontrola schématu byla zelená — a přesto hra vypadala špatně.
Zachránil to až pohled na snímek.

### Dvě mezery `phash`, které se našly měřením (a obě jsou zavřené)

`phash` vypadal jako hotová věc. Není — a bez měření by obě mezery prošly do
provozu jako **tiché „nezměněno" u změněného assetu**, což je přesně ta chyba,
které má baseline bránit.

| Mezera | Naměřeno | Řešení |
|---|---|---|
| **Je slepý na BARVU** — je to DCT přes odstupňovou škálu (`convert("L")`) | červená + bílé/černé bloky → `f8f8f8f0f0070707`<br>modrá + tytéž bloky → `f8f8f8f0f0070707` **stejné!** | `.forge/baseline.py` ukládá i **barevný podpis** (průměrné RGB 4×4, kvantované); cache vyžaduje shodu **obojího** |
| **Degeneruje u jednolitého obrázku** — DCT nemá co měřit | plná červená `8000000000000000`<br>plná modrá `8000000000000000` **stejné!** | `phash()` vrací `None` a porovnává se **přesný `sha256`** |

Reálné assety `uo-shadows` mez č. 2 nemají (dlaždice std 12–41, sprity 47–94),
ale jednolitá textura je běžná věc — a přebarvení (týmové barvy, jiný materiál)
je v herní grafice taky běžné.

**Proč to nikdo neviděl:** obě meze se projeví jen na obrázcích, které se liší
**výhradně barvou**. Testovací fixtures byly původně jednolité barvy — což
mezeru omylem odhalilo, ale taky způsobilo, že testy zpočátku hlásily chybu
nástroje, i když nástroj měřil správně. Fixtures proto teď mají strukturu.

### Jak se LGTM používá

```powershell
cd games\uo-shadows
python .forge\baseline.py stav                    # co je nové / změněné (exit 1 = čeká)
python .forge\baseline.py init                    # baseline = dnešní stav (tvé LGTM)
python .forge\baseline.py schval assets/sprites   # schválit konkrétní sadu
python .forge\baseline.py zamitni cesta.png --duvod "hlava je moc velká"
```

A v `vision.mjs` se cache uplatní automaticky: schválený a nezměněný obrázek
**model vůbec neosloví** (doloženo testem: 0 promptů na mock serveru).
Vynutit kontrolu i tak jde přepínačem `--force`.

### Co se za pochodu změnilo proti schválenému plánu

1. **Schéma je per-game** (tvoje odpověď). Původní plán mluvil o „sjednocení
   rozporu 96×48 vs 16×16"; správné znění je **„autorita je `spec.json` té hry
   a nástroje v něm nesmí mít nic zadrátované"**. Profil proto dlaždice ani
   projekci **neobsahuje** – a test to hlídá (kdyby je někdo přidal, schéma by
   se rozešlo přesně jako to dnešní).
2. **Kontrola schématu je tvrdá brána, ne warning.** Původní plán ji neměl
   vůbec; při ověřování se ukázalo, že rozpor v zadání je objektivní fakt
   (blokovat smí), kdežto vision je názor modelu (blokovat nesmí). Rozdělení
   „tvrdé vs. poradní" tedy kopíruje přesně to, co je falzifikovatelné.
3. **Vision se v CI pouští jen v režimu `presence`.** Režim `diff` (dva
   obrázky) patří na uzel a do session – v CI není s čím porovnávat, dokud
   neexistuje baseline (F0b).
4. **Přidán timeout na volání modelu.** Nebyl v plánu, ale při testech se
   ukázalo, že volání vision modelu umí viset – bez timeoutu by to spálilo celý
   CI krok (stejná past, kterou už řeší `agent.yml` u aideru).
5. **BOM-safe čtení JSON.** PowerShell a editory na Windows přidávají UTF-8 BOM
   a `JSON.parse` na něm spadne. Stejná past už jednou potkala `orchestra/.env`.

### Dvě chyby, které odhalily až testy (a stály za to)

- **Deadlock v testu.** Mock API běželo ve stejném procesu jako test, ale
  `execFileSync` blokuje event loop → rodič nemohl odpovědět dítěti, které
  čekalo na rodiče. Test visel 3× a vypadal jako „pomalý". Řešení: asynchronní
  `execFile` + `connection: close` v mock serveru.
- **Chybný předpoklad v testu.** Test čekal `5× floor / 3× wall`, ale
  `'0011' + '1111'` je 6 a 2. Nástroj počítal správně, test byl špatně –
  a to je přesně rozdíl, který je potřeba rozlišit, než se začne „opravovat"
  nástroj.

---

## 1. Jaký význam a dopad má vision — poctivá inventura

### 1.1 Vision není „lepší měření". Je to jiná otázka.

Dnešní kontroly odpovídají na **měřitelné** otázky:

| Nástroj | Otázka |
|---|---|
| `tests/run_tests.gd` | Chová se logika správně? |
| `check-wiring.py` | Je každá funkce odněkud volaná? |
| `check-assets.py` | Sedí výška, díry, okraje, siluety, motiv? |
| `verify-level-render.py` | Odpovídá snímek mapě (shoda pixelů)? |

Vision odpovídá na **významovou** otázku: **„je na tom obrázku to, co tam má
být?"** To se měřením nahradit nedá — pixelová shoda 89 % neřekne, jestli je
hráč vidět, ani jestli dlaždice nevypadají jako bláto.

### 1.2 Taxonomie vizuálních vad (a kdo je dnes chytá)

| # | Druh vady | Příklad | Chytá dnes | Vision? |
|---|---|---|---|---|
| V1 | **Prázdný / rozbitý snímek** | černá obrazovka, chybějící textura | částečně (shoda pixelů) | ✅ snadno |
| V2 | **Chybí očekávaný prvek** | hráč není vidět, mince se nevykreslily | ❌ | ✅ snadno |
| V3 | **Prvek je na špatném místě** | hráč stojí mimo dlaždici | částečně | ⚠️ hrubě |
| V4 | **Vrstvy nesedí na sebe** | zbraň plave mimo ruku | ❌ | ⚠️ jen hrubě |
| V5 | **Vizuální kolize** | sprite splývá s podlahou | ✅ (`min_contrast_vs_floor: 150`) | ➖ zbytečné |
| V6 | **Useknutý / přetékající sprite** | postavě chybí nohy | ✅ měřením | ➖ zbytečné |
| V7 | **Stylová nekonzistence** | UO postava + SDXL meč z jiné hry | ❌ | ✅ (s baseline) |
| V8 | **Věcná chyba obsahu** | „meč" je ve skutečnosti sekera | ❌ | ✅ |
| V9 | **Estetická kvalita** | „vypadá to jako slepenec" | ❌ | ⚠️ subjektivní, nespolehlivé |

**Zásada: vision se nasazuje na V1, V2, V7, V8. Na V5 a V6 se nepoužívá** —
numerická kontrola je přesnější a zdarma. Vision, který dělá práci měření, je
vyhozená kvóta a horší výsledek.

### 1.3 Dopad na `uo-shadows` — konkrétně a bez iluzí

Hra je dnes ve fázi **kódu**: roadmapa má 18 granul, všechny `kind: code`,
hotovo 6/18, fronta stojí na `core.skills`. Assety jsou hotové a **schválené**
(`spec.json`, `_stav`: „MILNÍK 1 SCHVÁLEN 5/5").

**Poctivý závěr: kdyby vision běžel dnes, nechytil by nic.** Ne proto, že je
zbytečný, ale protože se právě nic negeneruje. Přínos přichází ve chvíli, kdy
přijdou na řadu:

- **vrstva `head`** (obličej — dnes je hlava koule bez rysů),
- **přepracování meče** (`spec.json`: „meč = PROZATÍMNÍ kandidát", SDXL u dlouhých
  čepelí dělá vady),
- **další materiály a monstra** z plánu.

To je přesně fáze, kdy vzniká V7 (stylová nekonzistence) a V8 (věcná chyba) —
a to jsou vady, které **ani CI, ani ty nepoznáš z čísel**.

> **Pozor na jeden mýtus:** „meč z jiné hry" u `uo-shadows` **nevzniklo proto, že
> nikdo neviděl obrázek**. Vzniklo mixem dvou nástrojů (SDXL + Blender) proti
> pravidlu „jednu sadu dělá jeden nástroj". Vision by to **odhalil dřív**, ale
> nezpůsobil by to, že se to nestane. Procesní pravidlo je levnější než kontrola.

---

## 2. Metoda volání — jak dostat nejpřesnější výsledek

Tohle je jádro plánu. Kvalita odpovědi závisí víc na **tvaru dotazu** než na
volbě modelu.

### 2.1 Čtyři úrovně dotazu (L1–L4)

| Úr. | Tvar | Kdy | Příklady vad | Cena |
|---|---|---|---|---|
| **L1** | „Vypiš, co vidíš" (volný popis) | ladění, explorace | — | 1 volání |
| **L2** | „Vypiš, co vidíš" **+ očekávaný seznam** | rutinní kontrola | V1, V2, V8 | 1 volání |
| **L3** | dva obrázky (baseline + kandidát) + „co se změnilo" | změnová kontrola | V4, V7 | 1 volání, 2 obrázky |
| **L4** | **2× stejný dotaz** → shoda? + druhý poskytovatel | sporné / P1 | všechno | 3–4 volání |

**Klíčové pravidlo: neposílat hodnocení, posílat očekávání.**
Model, který dostane „vypiš, co vidíš", má tendenci být zdvořilý a vidět to, co
má. Model, který dostane **seznam očekávaných objektů**, jen přiřazuje
přítomen/nepřítomen — to je snazší úloha, takže je **přesnější i levnější**.

### 2.2 Šablony dotazů (konkrétně)

**L2 — přítomnost obsahu (nahrazuje „vypadá to dobře?"):**

```
Jsi kontrolor herního screenshotu. Nedělej estetický posudek.

Očekávaný obsah podle mapy: hráč, 3 kameny, 2 stromy, 1 truhla.
Odpověz POUZE JSON:
{"videno": ["..."], "chybi": ["..."], "navic": ["..."],
 "popis_1_veta": "..."}
```

Proč to funguje: model **nejdřív vypíše**, pak teprve (v jiném volání) hodnotí.
Když vypíše „vidím hráče" a hráč tam není, je to **falzifikovatelné** — a to se
dá odhalit porovnáním dvou běhů (§2.3).

**L3 — změnový diff (dva obrázky):**

```
Obrázek 1 = schválený stav, obrázek 2 = nový stav.
Vypiš POUZE rozdíly, které mění vzhled:
{"zmeny": ["..."], "co_zustalo": ["..."], "mozna_regrese": ["..."]}
Nehodnoť, jen porovnej.
```

### 2.3 Pět technik, které zvyšují přesnost (a jsou zdarma)

1. **Obrázek před textem.** Google i OpenAI dokumentují lepší výsledky, když je
   obrázek v promptu první. U víc obrázků platí totéž.
2. **Strukturovaný výstup** (JSON s pevnými klíči, `response_format`/`json_mode`).
   Zabraňuje „omáčce", která se nedá automaticky vyhodnotit.
3. **Self-consistency: 2 běhy, teplota > 0.** Když se dvě odpovědi neshodnou,
   je to **signál nejistoty** — a to je přesně moment, kdy má rozhodnout člověk.
   Stojí to 2× víc a zachrání to nejvíc.
4. **Kontrola proti baseline.** Bez schváleného referenčního obrázku nelze měřit
   drift — jen hádat. Baseline je vstup, ne výstup (§7).
5. **Souhlas dvou poskytovatelů jako trojúhelník.** DeepSeek a Gemini mají
   nezávislé chyby. Když se shodnou, věř tomu; když ne, eskaluj.

### 2.4 Kolikrát volat stejný model a proč nestačí jednou

Naměřeno u vision modelů obecně: **jeden běh má chybovost v jednotkách až
desítkách procent** podle typu úlohy. Pro bránu, která má blokovat slučování, je
to nepoužitelné. Proto:

| Režim | Volání | Chybovost | Použití |
|---|---|---|---|
| 1× levný model | 1 | vysoká | `::warning` v CI, nic neblokuje |
| 2× levný (shoda) | 2 | nižší | poradní verdikt |
| 2× levný + 1× drahý | 3 | nízká | sporné případy |
| **člověk** | 0 | ≈0 | **finální schválení** |

**Vision v tomhle návrhu nikdy nerozhoduje sám o sobě.** Buď je poradní, nebo
k němu patří lidské „LGTM".

### 2.5 Kde vision NEBUDE použit (a je to důležité)

| Úloha | Proč ne | Čím místo toho |
|---|---|---|
| počítání mnoha objektů | modely systematicky selhávají u velkých čísel | spočítat z `main.json` |
| přesná pozice na dlaždici | odhadne jen hrubě | izometrický přepočet v kódu |
| barvy / paleta | nepozná hex | histogram + ΔE v CIELAB (§11) |
| pixelová shoda před/po | horší a dražší | SSIM / pHash |
| animace v čase | vidí jen jeden frame | GIF nebo Godot test |
| hudba a zvuk | vision neumí audio | měření motivu (`check-assets.py`) + lidský poslech |
| „líbí se mi to" | nedá se zopakovat | **ty** |

---

## 3. Kdo to čte — řetěz poskytovatelů

Kvalita rozpoznávání se mezi modely **liší podle typu úlohy**, ne globálně.
Proto se nevybírá „nejlepší model", ale **role**.

| Role | Kdo | Proč | Cena |
|---|---|---|---|
| **Dělník** (rutina, tisíce obrázků) | **DeepSeek** `deepseek-flash` | ~384 tokenů/obrázek → **~$0,0001/obrázek**; ceník Flash je 20–50× nižší než u konkurence | placené, ale zanedbatelné |
| **Rozhodčí** (styl, diff, sporné) | **Gemini** (flash → pro) | silnější na scénu a vztahy; zdarma do ~20 dotazů/model/den | zdarma, kvóta |
| **Záložní dělník** | Gemini | když DeepSeek vypadne | zdarma |
| **Nouzový, offline** | lokální VLM (viz §11) | soukromí, žádná kvóta — **dnes není nainstalovaný** | zdarma, ale VRAM |
| **Poslední instance** | **agent v session** (`read_image`) | umí se podívat sám, zdarma, neomezeně | zdarma |

**Proč DeepSeek jako dělník a ne naopak:** je 20–50× levnější, takže unese
objem (tisíce obrázků). Gemini má lepší scénové uvažování, ale free kvóta je
~20 dotazů/den — kdyby dělal rutinu, vyčerpá se a na sporné případy nic nezbude.
**Drahý model se šetří na těžké otázky.**

**Naměřeno a ověřeno (30. 9. 2026):** `deepseek-flash` **vision umí** (u
`deepseek-v4-pro` je „Not supported"), obrázek jde jako `image_url` v `content`
array, `detail: low|high|auto`, formát je OpenAI kompatibilní. Zdroj:
[oficiální ceník](https://api-docs.deepseek.com/quick_start/pricing),
[formát volání](https://apidog.com/blog/deepseek-v4-1-flash-vision-api/).

**Konfigurace řetězu** (jeden soubor, `visionModels.json` ve `.forge/`):

```json
{
  "chain": [
    { "name": "deepseek", "role": "worker",   "keyEnv": "DEEPSEEK_API_KEY",
      "baseUrl": "https://api.deepseek.com", "model": "deepseek-flash" },
    { "name": "gemini",   "role": "judge",    "keyEnv": "GEMINI_API_KEY",
      "baseUrl": "https://generativelanguage.googleapis.com/v1beta/openai",
      "model": "gemini-3.8-flash" },
    { "name": "local",    "role": "offline",  "baseUrl": "http://127.0.0.1:11434/v1",
      "model": "qwen2.5-vl:7b", "_stav": "NENI nainstalovano – viz §11" }
  ],
  "policy": {
    "L1_L2": ["deepseek"],
    "L3_L4": ["gemini", "deepseek"],
    "critically": "2x stejny model + druhy poskytovatel pri neshode"
  }
}
```

**Kde klíč žije:** `DEEPSEEK_API_KEY` patří do **Secrets herního repa** (stejné
pravidlo jako u free LLM — volání běží v runneru toho repa, viz
`orchestra/README.md`, „Tajemství — kam patří"). `read_image` **žádný klíč
nepotřebuje** — to je čistě lokální věc session.

---

## 4. Kam to zapadne v pipeline

### 4.1 Čtyři kontrolní místa

| # | Místo | Kdo spouští | Co kontroluje | Blokuje? |
|---|---|---|---|---|
| **C1** | Po renderu snímku hry v CI | `ci.yml` (runner) | V1, V2 — prázdná scéna, chybí hráč | ❌ `::warning` |
| **C2** | Po změně `assets/` v PR | `agent.yml` / nový krok | V7, V8 — změnový diff proti baseline | ❌ poradní |
| **C3** | Po Blender renderu na uzlu | `worker.mjs` (krok `blender:`) | V1, V2, V4 — render dopadl, vrstvy sedí | ❌ report |
| **C4** | Schvalovací brána před sloučením | **ty** (nebo agent v session) | V9 — „tohle chci" | ✅ **ano** |

**Jen C1 je plně automatické** — a je to nejlepší poměr přínos/náklad, protože
snímek se **už vyrábí** a zahazuje (`ci.yml`, krok „Vizuální kontrola", ~6 minut
za xvfb + framy). Zbytek jsou nová místa s novými náklady.

### 4.2 Kam přesně do `ci.yml`

Za stávající krok „Vizuální kontrola (snímek hry vs mapa)":

```yaml
      - name: Vizuální kontrola – obsah snímku (vision)
        if: always()                     # i když číselná kontrola spadne
        continue-on-error: true          # NIKDY neblokuje slučování
        env:
          DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY }}
          GEMINI_API_KEY: ${{ secrets.GEMINI_API_KEY || vars.GEMINI_API_KEY }}
        run: |
          SNIMEK=$(ls /tmp/frames/frame*.png 2>/dev/null | tail -1 || true)
          [ -n "$SNIMEK" ] || { echo "::warning::snímek není"; exit 0; }

          # Očekávaný obsah se odvozuje z DAT HRY, ne opisuje ručně – jinak
          # kontrola zestárne s první změnou mapy.
          #
          # POZOR: `assets/levels/main.json` není seznam objektů. Je to textová
          # mřížka: klíč `grid` (řádky řetězců), `legend` (znak → druh pole)
          # a `tiles` (znak → dlaždice). Objekty se z ní POČÍTAJÍ.
          OCekAVANE=$(python3 -c "
import json, collections
d = json.load(open('assets/levels/main.json'))
leg, til = d['legend'], d.get('tiles', {})
p = collections.Counter(c for row in d['grid'] for c in row)
casti = [f\"{n}× {leg.get(c, til.get(c, c))}\" for c, n in sorted(p.items())]
print(', '.join(casti))")

          node .forge/vision.mjs "$SNIMEK" \
            "Jsi kontrolor herního screenshotu. Mapa obsahuje: $OCekAVANE. \
             Odpověz POUZE JSON: {\"videno\":[],\"chybi\":[],\"navic\":[],\"popis\":\"\"}. \
             Nedělej estetický posudek a nehodnoť počet barev." \
            || echo "::warning::vision nedostupná (kvóta/klíč)"
```

> **Tři věci, na kterých to stojí:** (1) očekávaný obsah se **počítá z dat hry**,
> neopisuje ručně; (2) `continue-on-error: true` — výpadek kvóty nesmí zastavit
> slučování; (3) prompt **zakazuje počet barev**, protože `spec.json` kvantizaci
> výslovně zapovídá a model by k ní sváděl.

### 4.2b Co jsem při psaní tohohle plánu našel (a je to vážnější než vision)

Když jsem ověřoval, jak z mapy odvodit očekávaný obsah, narazil jsem na
**rozpor v zadání projektu**. Uživatel ho 30. 9. 2026 rozhodl: **schéma je
per-game a autoritou je `assets/spec.json` hry.** Tím je směr daný — a rozpor
se tím mění z „které číslo platí" na „co je potřeba domigrovat":

| Zdroj | Dlaždice | Viewport | Stav po rozhodnutí |
|---|---|---|---|
| `assets/spec.json` (`_popis`, `tile`, `viewport`) | **96×48** (izo diamant) | **960×540** | ✅ **AUTORITA** (per-game) |
| `docs/DESIGN.md` (ř. 48–51) | izometrie **2:1**, „ne retro pixely" | — | ✅ v souladu se spec |
| `assets/levels/main.json` (skutečnost) | **16×16** (`cell: 16`) | **480×270** | ❌ **domigrovat** |
| `assets/tiles/*.png` + `manifest.json` | **32×32** | — | ❌ **domigrovat** |
| `scripts/level.gd` | **16** (výchozí i fallback) | — | ❌ **domigrovat** (a umět izometrii) |
| `scripts/world.gd` | **32** + `iso_position` | — | ❌ **rozhodnout**: zapojit, nebo smazat |
| `docs/ARCHITEKTURA.md` | neurčuje | neurčuje | ➖ neurčuje (mezera v závazném dokumentu) |

**Proč to patří do plánu o vision:** vision umí říct „tenhle sprite je z jiné
hry". **Neumí rozhodnout, který ze čtyř čísel platí.** Kdyby se vision nasadil
do projektu s tímhle rozporem, hlásil by buď neustálé nekonzistence (měřeno
proti `spec.json`), nebo nic (měřeno proti `main.json`) — a v obou případech by
to nikam nevedlo.

**Řešení není „srovnat čísla ručně", ale mít na to kontrolu.** Proto vznikl
`.forge/check-schema.py` (`orchestra/tools/kontrola-schematu.py`), který se
pouští **jako tvrdá brána v CI před vision** a hlásí přesně tuhle třídu vady.
Dnes nachází **6 rozporů** — a to je správně: hra si skutečně odporuje.

**Proč per-game a ne globální konstanta:** ne každá hra je izometrická.
Side-scroller má obdélníkové dlaždice, top-down čtvercové, izometrie 2:1
kosočtverec. Kdyby nástroj měl „96×48" nebo „izometrická" zadrátované, druhá
hra by buď nefungovala, nebo by se tiše měřila špatně. Proto:

- `spec.json` **hry** deklaruje schéma (projekce, dlaždice, viewport, styl),
- `vision-profile.json` **hry** deklaruje jen *chování kontroly* (co je
  očekávaný obsah, jaké zákazy v promptu, jaké stropy) — **a schéma v něm
  záměrně NENÍ**,
- test to hlídá: `.forge/node/vision.test.mjs` pouští vision na vymyšlené hře
  s **čtvercovou projekcí a dlaždicí 24 px** a ověřuje, že si je nástroj přečte
  odtud. Kdyby někdo schéma do nástroje vrátil, test spadne.

### 4.3 Stavový diagram assetové granule

```
                    ┌─────────────────────────────────────────┐
                    │                                         │
  grain(assets)     │                                         │
      │             ▼                                         │
      ├─► generuj (Blender / SDXL / Gemini, seed)             │
      │        │                                              │
      │        ▼                                              │
      │   check-assets.py ── FAIL ──► oprav (bez vision) ─────┤
      │        │ OK                                           │
      │        ▼                                              │
      │   vision L2 (DeepSeek, 2×) ── neshoda ──► eskaluj ────┤
      │        │ shoda                                        │
      │        ▼                                              │
      │   vision L3 (Gemini, diff vs baseline) ── regrese ────┤
      │        │ OK                                           │
      │        ▼                                              │
      │   PR → CI (C1) → auto-merge (jen scripts/assets)      │
      │        │                                              │
      │        ▼                                              │
      └─► LIDSKÉ LGTM ──► baseline se aktualizuje ────────────┘
              │ NE
              └─► zapiš do zamítnutých (aby se to nezkoušelo zas)
```

**Klíčové:** vision je **mezi měřením a PR**, ne před měřením. Numerická
kontrola je řádově levnější, takže filtruje první — vision dostane jen to, co
už prošlo čísly. (Opačné pořadí je nejčastější chyba návrhu: platíš model za
něco, co odhalí skript za 0,3 s.)

---

## 5. Implementační cyklus pro vizuální změny

Dnes vizuální změna nemá proces — vzniká ad hoc a schvaluje se dojmem. Navržený
cyklus (kopíruje to, co už funguje pro kód: granule + brány + auto-merge):

| Krok | Co se děje | Kdo/kde | Výstup |
|---|---|---|---|
| **1. Zadání** | co a proč („vrstva `head` pro 4 směry") | ty → roadmapa | granule `kind: assets` |
| **2. Smlouva** | čísla PŘED generováním: `size`, `colors`, `seed`, tolerance | `spec.json` | měřitelné zadání |
| **3. Generování** | deterministicky, se seedem | uzel (Blender/SDXL) | PNG + záznam do KB |
| **4. Měření** | `check-assets.py` | skript | vady / OK |
| **5. Vision L2** | obsah proti očekávání | DeepSeek 2× | shoda / neshoda |
| **6. Vision L3** | diff proti baseline | Gemini | změny / regrese |
| **7. Návrh** | **kontaktní arch + verdikty + čísla** | session | jeden PNG + report |
| **8. LGTM** | schválíš / zamítneš / pošleš zpět | **ty** | zápis do cache |
| **9. Sloučení** | PR, CI, auto-merge | orchestra | nová baseline |

**Kolik iterací:** doporučuji strop **3 kola na granuli** (dnes u kódu je
cooldown 3 h a watchdog po 8 spálených bězích — pro assety by měl být strop
tvrdší, protože každé kolo stojí GPU čas, ne jen kvótu). Po 3 kolech: eskaluj
člověku, nezkoušej dál. Bez stropu vznikne přesně to, čeho se bojíš — systém
jede vlastním směrem a pálí zdroje.

**Co se musí stát deterministickým:** seed, verze promptu, verze Blenderu a
verze modelu. Bez toho se „stejný" render nedá zopakovat a ladění je házení
kostkou. `spec.json` už seed podporuje (`sprites.json`: „pevný seed =
reproducibilní výsledek").

---

## 6. Grafické téma projektu (závazně)

Z `docs/ARCHITEKTURA.md`, `docs/DESIGN.md` a `assets/spec.json` — tohle je
**jediný zdroj pravdy** a vision ho musí respektovat:

| Vlastnost | Hodnota |
|---|---|
| **Žánr** | izometrický fantasy sandbox RPG („moderní Ultima Online") |
| **Vzhled** | 2.5D izometrie **2:1**, pohled shora, dojem „zmenšeného skutečného světa" |
| **Technika** | **3D model → render do 2D spritu** (Blender headless). NE 3D engine, NE retro pixel art |
| **Rozlišení** | viewport `960×540`, celočíselné 2× na 1080p |
| **Dlaždice** | izometrický diamant `96×48` |
| **Postava** | 96 px, 4 směry, 8 framů chůze, canvas 128 |
| **Barvy** | **plné (stovky až tisíce)**, žádná kvantizace, žádný dithering |
| **Zmenšování** | **Lanczos / bilineární**, NE nearest |
| **Světlo** | skutečné (render), měkké stínování; stín se kreslí v kódu (elipsa, krytí 0.35) |
| **Kompozice** | postava je **skládaná z vrstev** (`body, legs, feet, torso, cloak, head, shield, weapon`) — obličej přijde jako vrstva `head` |
| **Zakázané** | 16barevná paleta, dithering, pixelové hrany, přehnané fantasy proporce |
| **Proporce** | lidské a praktické — „zbraň musí vypadat použitelně, ne jako dekorace" |

**Dvě věci, které z toho plynou pro vision** (a jsou neintuitivní):

1. **Vision nesmí soudit „styl" obecně** — musí soudit **proti baseline**, protože
   téma je specifické (UO pre-render, ne pixel art, ne moderní 3D). Obecný model
   má tendenci doporučovat „hezčí", což znamená jinam, než kam projekt míří.
2. **Kontrola palety je protichůdná s běžnou radou.** „Méně barev = lepší sprite"
   tady **neplatí** — `spec.json` explicitně zakazuje kvantizaci. Vision by
   k tomu mohl svádět; do promptu proto patří „nehodnoť počet barev".

`sprites.json` v repu je **zastaralý template** z prvního nástřelu (16 barev,
64 px, „green slime") — neodpovídá `spec.json`. Buď ho smazat, nebo označit jako
historii; dnes mate.

> ⚠️ **A pozor: téma není v projektu jednotné.** Níže uvedená čísla jsou
> z `spec.json` a `DESIGN.md`, ale **skutečná mapa používá jiná** (16×16 dlaždice,
> 480×270). Rozpor je rozepsaný v §4.2b — a musí se vyřešit **před** nasazením
> vision, protože určuje, proti čemu se měří.

---

## 7. Baseline: co je „schváleno" a jak to vzniká

Bez baseline se drift měřit nedá. Zavádím proto pojem **schválená sada**:

```
.forge/vision/
  baseline/                     # SCHVÁLENÉ sprity (referenční body)
    player_d0_f0.png …
  baseline.json                 # co je schváleno, kdy, čím, s jakým hashem
  verdicts.jsonl                # historie verdiktů (audit)
  rejected.jsonl                # co bylo zamítnuto a proč
```

`baseline.json`:

```json
{
  "verze": 1,
  "prompt_verze": "uo-iso-2to1-v3",
  "schvaleno": "2026-09-30T21:40:00Z",
  "polozky": {
    "player_d0_f0.png": {
      "sha256": "…", "phash": "…", "seed": 12345,
      "schvalil": "clovek",
      "poznamka": "milnik 1, cesta A"
    }
  }
}
```

**Na začátku je baseline to, co už schválené je** — `spec.json` říká „MILNÍK 1
SCHVÁLEN 5/5", takže dnešní sprity **jsou** baseline. Nic se nevymýšlí.

---

## 8. Cache a schvalování — jak si udržet kontrolu

**Ano, cachovat lze a je to podmínka.** Bez toho se za (a) spálí kvóta, (b)
zaplatíš za stejné obrázky opakovaně, (c) ztratíš přehled, co jsi schválil.

### 8.1 Tři vrstvy cache (každá řeší jiný problém)

| Vrstva | Klíč | Co ušetří |
|---|---|---|
| **V1 – nezměněný soubor** | `sha256` + `phash` obrázku + `prompt_verze` + model | celé volání: stejný obrázek se neposílá dvakrát |
| **V2 – schváleno (LGTM)** | `phash` + `baseline.verze` | přeskakuje kontrolu u toho, co jsi už odklepl |
| **V3 – zamítnuto** | `seed` + `prompt_verze` | neztrácí čas opakováním téhož, co už neprošlo |

**Proč `phash` a ne jen `sha256`:** PNG se může přeuložit s jinými metadaty
a stejný obrázek má jiný `sha256`. Percepční hash pozná „je to vizuálně totéž",
co je přesně to, co potřebuješ. (`imagehash` na stanici **není** — viz §11.)

### 8.2 Jak vypadá LGTM v praxi

```
1. Agent připraví návrh   →  orchestra/.tmp/navrh-<grain>.png   (kontaktní arch)
                             + report (čísla + verdikty vision)
2. Ty se podíváš a řekneš  →  "LGTM" / "ne, hlava je moc velká" / "zkus jiný seed"
3. Zápis                    →  baseline.json (schváleno) NEBO rejected.jsonl
4. Teprve teď                →  PR vznikne / se sloučí
```

**Tvrdé pravidlo, které brání „rozjetí vlastním směrem":**

> **Co není v baseline, nesmí do hry.** Auto-merge pro `assets/**` se zapne až
> tehdy, když je změna **proti baseline** a vision nehlásí regresi. Změna bez
> baseline (nový typ assetu) jde **vždy** na člověka.

Tím se stropuje riziko: systém může produkovat, ale **nemůže sám rozšířit, co je
považováno za správné**. To je přesně ta pojistka, kterou hledáš — a je to
analogie `done: true` a `acceptance` u granulí kódu, ne nový mechanismus.

### 8.3 Rozpočtové stropy (aby to neuteklo)

| Strop | Navržená hodnota | Co se stane po dosažení |
|---|---|---|
| vision volání na PR | 4 (2× DeepSeek + 2× Gemini) | další se přeskočí, jen čísla |
| vision volání na den | 200 | `::warning`, jede jen numerická část |
| kol na granuli | 3 | eskaluj člověku |
| placené (DeepSeek) na den | ~$0,02 | tvrdý stop, eskaluj |
| neúspěchů v řadě | 3 | zastav generování téhle sady |

---

## 9. Další body, které je třeba zvážit (a snadno se přehlédnou)

Pořadí podle vážnosti:

1. **Goodhartův zákon — největší riziko celého plánu.** Jakmile se z vision
   stane brána, systém se začne učit **procházet kontrolou**, ne vypadat dobře.
   (Přesně to se už děje u kódu: `check-wiring.py` nutí agenta volat funkce,
   i když nedávají smysl.) **Ochrana:** baseline schvaluje člověk, vision je
   poradní, a prompty se needitují podle toho, co zrovna neprošlo.

2. **Falešná pozitiva blokují práci.** Vision, který blokuje slučování, umí
   zastavit projekt na nesmyslu. Proto: **P0 smí blokovat jen to, co je
   falzifikovatelné** (prázdný obrázek, soubor se nenačetl). Všechno ostatní je
   poradní, dokud nemáme naměřenou chybovost aspoň na 50 vzorcích.

3. **Nezávislé ověření verdiktu.** Vision je **jeden názor**, ne pravda.
   U důležitých rozhodnutí druhé volání jiným modelem nebo `read_image` v session.

4. **Soukromí a licence.** Obrázky poslané DeepSeeku/Gemini opouštějí stanici.
   U herních spritů to nevadí, u čehokoli jiného ano. `read_image` a lokální VLM
   data neodesílají.

5. **Kvóta a klíče.** Gemini free ~20 dotazů/den/model (naměřeno) je pro
   rutinu málo. DeepSeek klíč musí do Secrets **herního repa** (ne orchestra).
   `read_image` nepotřebuje klíč žádný.

6. **Verzování promptu.** Změna promptu zneplatní všechny staré verdikty i
   cache. Proto `prompt_verze` **v klíči cache** — jinak se tiše míchají
   neporovnatelné výsledky.

7. **Vision nevidí čas.** Animace je jen sled framů; „je chůze plynulá" z
   jednoho obrázku nepozná. Na to je GIF (§11) nebo Godot test.

8. **Latence** — každé volání přidá sekundy až desítky sekund k běhu.
   Do cesty kritické pro slučování to nepatří.

9. **Náklady na falešné poplachy jsou vyšší než na přehlédnutí.** U herního
   vývoje je „ošklivý sprite projde" mnohem levnější chyba než „dobrý sprite
   se zablokuje a nikdo neví proč". **Nastav to jako poradní a nech to tak.**

10. **Vypínač.** Vision musí jít vypnout **bez změny kódu** (chybějící klíč =
    přeskočeno). Nikdy nesmí být jediná cesta k zelenému CI.

11. **Neopakovat chybu s mrtvým kódem.** Dnes je `.forge/vision.mjs` hotový a
    nikdo ho nevolá. Plán proto **nekončí nástrojem** — končí zapojením,
    ověřením a záznamem, že to běží.

12. **Pozor na „další vrstvu zdarma".** Každá vrstva přidá místo, kde se dá
    něco rozbít. Vision je **volitelná** vrstva; orchestra musí fungovat i bez
    ní — a dnes funguje.

---

## 10. Nástroje, které pomohou (generování, analýza, úprava, rozpoznávání)

**Inventura stanice** (`orchestra/tools/inventura-vize.py`, spusť kdykoli):

| Vrstva | Nástroj | Stav | K čemu |
|---|---|---|---|
| **měření** | `Pillow` 12.3 | ✅ je | načtení, arch, zmenšení |
| | `numpy` 2.5 | ✅ je | matice pixelů, histogramy |
| | `scipy` | ❌ chybí | `binary_fill_holes` (dnes vlastní BFS v `check-assets.py`) |
| | `imagehash` | ❌ chybí | **pHash — klíč cache (V1/V2)** |
| | `scikit-image` | ❌ chybí | **SSIM, kontury, prahování** |
| | `opencv-python` | ❌ chybí | template matching, **optický tok (animace)**, ORB |
| | `rembg` | ❌ chybí | odstranění pozadí neuronkou (dnes podle barvy) |
| **rozpoznávání** | `read_image` (session) | ✅ je | podívat se sám, zdarma |
| | DeepSeek `deepseek-flash` | ✅ klíč je | **dělník** |
| | Gemini vision | ✅ klíč je | **rozhodčí** |
| | `.forge/vision.mjs` | ⚠️ hotové, nezapojené | „oči" pro CI |
| | `pytesseract` + Tesseract | ❌ chybí | OCR (text v HUD, chybové hlášky) |
| | `torch` + `transformers` + CLIP | ❌ chybí | **embeddingový drift stylu (§11)** |
| | lokální VLM (`qwen2.5-vl:7b`) | ❌ chybí | offline vision, soukromí |
| **generování** | Blender 5.2.1 headless | ✅ je | 3D → 2D, konzistentní sada |
| | ComfyUI + SDXL | ✅ je | 2D předměty, deterministicky |
| | Gemini imagegen | ✅ je | pixel-art, rychlé |
| **úprava** | `ffmpeg` | ✅ je | **GIF z framů chůze** (kontrola animace okem) |
| | ImageMagick (`magick`) | ❌ chybí | dávkové úpravy, montáže, diffs |
| | Godot 4.7.2 headless | ✅ je | render scény, testy animace |
| | `tools/blender/postprocess.py` | ✅ je | zmenšení, zarovnání, skládání |

### 10.1 Pět vrstev, kde vision je jen jedna

Nejužitečnější doplněk **není vision**:

| Vrstva | Nástroj | Chytá | Vision? |
|---|---|---|---|
| 1 | **numerické metriky** (dnes) | V5, V6 | ne |
| 2 | **pHash / SSIM** | „změnilo se to vůbec?" | ne — a zdarma |
| 3 | **CLIP embedding** | **V7 stylový drift** — porovnání s baseline v embeddingu | ne, ale *měří to, co vision jen popisuje* |
| 4 | **vision (VLM)** | V1, V2, V8 | **ano** |
| 5 | **člověk** | V9 | — |

**CLIP je nejzajímavější nález:** umí vzít baseline sprity a kandidáta, udělat
embeddingy a říct **„jak daleko je to od schváleného stylu"** jako jedno číslo.
To je přesně V7 — a na rozdíl od vision je to **deterministické, zdarma,
lokální a dá se na to dát práh do CI**. Stálo by za pilot: CLIP (~600 MB) se
vejde do 8 GB VRAM vedle Ollamy, nebo poběží na CPU.

---

## 11. Fázovaný plán (co dělat v jakém pořadí)

| Fáze | Co | Kde | Riziko | Přínos |
|---|---|---|---|---|
| **F-1** | **Sjednotit schéma dlaždic** (96×48 vs 16×16) — viz §4.2b | `spec.json` nebo `main.json` | — | **bez toho nemá vision proti čemu měřit** |
| **F0** | Spustit C1 s Gemini zdarma, `continue-on-error` | `ci.yml` | nízké | hned vidíš, co to hlásí na živých snímcích — **a máš data pro rozhodnutí o DeepSeeku** |
| **F0b** | Zavést baseline + `baseline.json` z dnešních schválených spritů | `.forge/vision/` | nízké | bez toho nelze měřit drift |
| **F1** | Prompty L2 + L3, self-consistency 2× | `.forge/vision.mjs` | nízké | přesnost místo dojmu |
| **F2** | Cache V1 (pHash) + V3 (zamítnuté) | `.forge/` | nízké | šetří kvótu i čas |
| **F3** | Dle naměřené chybovosti: DeepSeek jako dělník nebo není třeba | `visionModels.json` | nízké | — |
| **F4** | LGTM brána: `assets/**` do auto-merge **jen proti baseline** | `agent.yml` | **střední** | kontrola zůstane u tebe |
| **F5** | Pilot CLIP driftu (§10.1) | lokálně | nízké | V7 měřitelně, zdarma |
| **F6** | Krok `blender:` v `worker.mjs` + uzlový C3 | uzel | střední | render + kontrola v jednom |
| **F7** | Lokální VLM jako offline fallback | Ollama | nízké | soukromí, žádná kvóta |

**Doporučené pořadí zdůvodnění:** F-1 první, protože **vision nemá proti čemu
měřit, dokud si dva dokumenty odporují** — a to je práce na minuty, ne na dny.
Pak F0: **odpoví na tvou otázku o DeepSeeku daty.** Uvidíš, jak často Gemini na
kvótu narazí a jaké verdikty vlastně dává. Teprve pak má smysl platit za
dělníka — kupovat ho před měřením je nejdražší způsob, jak zjistit, že není
potřeba.

---

## 12. Rozhodnutí (stav 30. 9. 2026)

| # | Rozhodnutí | Stav |
|---|---|---|
| **0** | **Schéma je PER-GAME, autoritou je `assets/spec.json` hry** | ✅ **rozhodnuto uživatelem.** Nástroje v něm nesmí mít nic zadrátované — `kontrola-schematu.py` ho jen čte a porovnává se skutečností; `vision.mjs` z něj bere projekci i dlaždice. Ověřeno testem na hře s čtvercovou projekcí 24 px. |
| 1 | Vision v CI | ✅ **hotovo** — jen jako `::warning`, `continue-on-error` |
| 2 | Baseline = dnešní schválené sprity | 🟡 **nástroj hotový, čeká na tvé LGTM** — `spec.json` `_stav` říká „MILNÍK 1 SCHVÁLEN 5/5", ale `init` musí spustit člověk (je to tvrzení, že stav je správný). Dnes: 272 položek čeká. |
| 3 | Auto-merge pro `assets/**` proti baseline | ⏳ **čeká** — doporučení: nejdřív vždy člověk |
| 4 | Platit DeepSeek | ⏳ **až po F0** — v profilu je připravený jako první článek; klíč se doplní podle potřeby |
| 5 | Strop kol na vizuální granuli | ✅ **v profilu** (`stropy.kol_na_granuli: 3`, `volani_na_den: 200`) |
| 6 | Zastaralý `sprites.json` | ⏳ **čeká** — označit jako historii (je to stopa vzniku) |

### Zbývající práce na hře (ne na nástroji)

Kontrola schématu hlásí **6 rozporů** a než se srovnají, vision v CI poběží
naprázdno (očekávaný obsah z mapy bude mluvit o dlaždicích, které hra nekreslí
podle specu). Pořadí migrace:

1. **Rozhodnout cílové číslo** — `spec.json` říká 96×48 a 960×540; mapa a
   dlaždice jsou na 16, resp. 32 px. Buď se `main.json` přegeneruje na 96×48
   (a dlaždice se vyrenderují znovu), nebo se `spec.json` přepíše na 32×32 —
   ale pak padá i izometrie 2:1, protože ta dlaždici 2:1 vyžaduje.
2. **`level.gd` musí umět izometrii.** Dnes staví `s.position = offset + Vector2(x*cell, y*cell)`
   se `scale` 1:1 — to je osově zarovnaný čtverec. Izometrický diamond 2:1
   znamená jiný přepočet pozice a jiné měřítko.
3. **`world.gd` se musí rozhodnout.** Buď se stane skutečným nositelem izometrie
   (a `level.gd` ho použije), nebo se jeho `iso_position` smaže — dnes je to
   **mrtvý kód s druhou představou o mřížce** (32 px), který testy ověřují
   samy proti sobě, takže projde, i když se nikde nepoužívá.
4. **Dlaždice** — `tiles/manifest.json` a PNG jsou 32 px; po změně schématu se
   musí vygenerovat znovu (a `seam` zůstane pod limitem).

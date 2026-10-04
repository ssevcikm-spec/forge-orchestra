# ZADÁNÍ PRO IMPLEMENTAČNÍ SESSION — ukotvení stavu orchestra (A1–A4)

> **Co tenhle dokument JE:** zadání. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).

> ## ✅ PROVEDENO 2. 10. 2026 — TENHLE DOKUMENT JE ZÁZNAM, NE ZADÁNÍ
>
> **Provedla** session `eb127abd` („Hluboká kontrola a plán úprav"),
> **08:38–08:52 UTC**. **Pořadí A1 → A2 → A3 → A4 dodrženo** (§0 — A3 před A1
> by vyrobilo smyčku). **Nepushnuto, necommitnuto** (`HEAD` obou repů beze změny).
>
> | # | Co | Stav | Doklad (spuštěním, ne čtením) |
> |---|---|---|---|
> | **A1** | `done` jen při `ok && merged`; nový stav `awaiting_human` | ✅ | `_analyza\a1-a2-over.py` — **19 kontrol**, 3 mutace chyceny |
> | **A2** | `owns` proti `origin/main` (+ cache s TTL 10 min) | ✅ | tamtéž (`null` ≠ prázdný strom) |
> | **A3** | `exit 1` v **obou** `agent.yml` | ✅ | `_analyza\a3-over.py` — **6×** `exit 1` (bylo 5×) |
> | **A4a** | lint hlásí chybějící `size_lines` | ✅ | `lint-roadmapa.py` → **13 z 18**, `exit 0` |
> | **A4b** | zastaralý text varování `[5]` (radil `INSERT`, kód ho už dělá) | ✅ | text opraven |
>
> **Navíc (nad zadání, protože to bylo potřeba):**
> - **Nadpis notifikace** už nelže: `ok && !merged` posílá „Forge: čeká na tvé
>   sloučení" místo „Forge: hotovo" (`index.ts:433-444`). Zadání to zmiňovalo
>   jen jako **otevřenou otázku** — bez toho by oprava lhala v jiné vrstvě.
> - **Cache `origin/main` má TTL.** První verze byla modulová proměnná **bez
>   expirace** a komentář tvrdil „na dobu jednoho tiku", což **nebyla pravda**
>   (izolát Cloudflare se recykluje, kdy chce on). **Vlastní omyl** — viz
>   `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` **N7**.
>
> **Dvě věci, které zadání předpovídalo správně:**
> 1. **„Drift prochází" NENÍ kritérium dokončení A3** — drift je pořád červený
>    (**1 rozdíl**, tři kroky které šablona má a hra ne). **Ověřeno, že A3 ten
>    rozdíl nezvětšil** (`_analyza\z8-probe.py` + rozbor kroků).
> 2. **`exit 1` se ověřuje na řádku, ne grepem** — v souboru je **6×**; hledání
>    v celém souboru by našlo i těch 5 starých.
>
> ⚠ **Co zůstává otevřené** (rozhodnutí člověka, ne práce): tři visící PR
> (#28/#29/#30), `awaiting_human` v notifikaci (vyřešeno výše), a **zda má
> `lint-roadmapa.py` u `[5]` skončit nenulově** — dnes `exit 0`.
>
> ⚠ **Pozor na datum:** text níž popisuje stav **PŘED** provedením. Čísla
> (např. „11 `done` v D1", „7 varování `[5]`") byla správná **ve svém čase** —
> `roadmap.json` se mezitím změnil (**naměřeno 10**, ne 7). **Nepřepisovat**;
> patří k nim čas.

---

> ## ⚠ MANDÁT JE UDĚLEN — TENHLE DOKUMENT SE OD 2. 10. 2026 ČTE JINAK
>
> Text níž (`:3–5`) vznikl v session, pro kterou platilo, že **kód orchestra se
> měnit nesmí**. **To už neplatí.** Uživatel na přímý dotaz 2. 10. 2026 odpověděl:
>
> > **„Ano — další session smí měnit kód v obou repech."**
>
> **Závazné znění je `HANDOFF.md` §8.2.** Co z mandátu plyne:
> - **A1–A4 se smí provést** — včetně `conductor/src/index.ts` a herního repa.
> - **Nepushovat bez vyžádání**; před commitem i pushem ukázat `git status`
>   a `git diff --stat`.
> - **Zakázané zůstává:** zakládat druhou hru, mazat `forge-quest`, vypisovat PAT.
> - **Rozhodnutí o O3** (má se sáhnout na běžícího conductora?) **platí dál** —
>   mandát je k zápisu kódu, ne k rozhodnutí, jestli se nasadí.
>
> **Pozor na pořadí:** A1–A4 mění **týž soubor** jako plán jazyka Z1–Z8
> (`conductor/src/index.ts`). **A1–A4 první, Z1 po nich** — důvod je v
> `HANDOFF.md` §8.3.

**Kdo to má dostat:** session, která **má kontext** k orchestra (podle `AGENTS.md`
patří dokončení a ověření práce do session, která ji dělala — a **kód orchestra
mění ten, kdo k tomu byl vyzván**; vyzvání je v `HANDOFF.md` §8.2).

**Vychází z:** `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` (§⑦ návrh kontraktů, §⑧ varianty,
§⑨ co nedělat) a `_analyza\HLOUBKOVA-MERENI-3.md` (naměřená čísla).
**Varianta:** **A** — „ukotvi každý stav". Varianta B (jednotný registr) byla
zamítnuta, viz analýza §⑧.

---

## 0. Závazné pořadí (NENÍ kosmetické)

```
A1 ──► A2 ──► A3 ──► A4
```

**A3 se NESMÍ udělat před A1.** Naměřeno a zdůvodněno v analýze §⑨:
`exit 1` v auto-merge při nefunkčním `done` vyrobí **smyčku** —
PR nesloučen → běh červený → úloha zpět `ready` → dispatch znovu → PR nesloučen…

**Kdo pořadí otočí, rozbije živý systém.** Tohle je jediné pravidlo, které má zuby.

---

## A1 — `done` jen když je PR sloučený

**Soubor:** `C:\Users\Ssevc\Local-Deepseek\orchestra\conductor\src\index.ts`
**Místo:** `pollRuns()`, ř. **365–390** (podmínka na ř. **385**).

**Dnes:**
```ts
365:    const ok = run.conclusion === "success";
...
375:        merged = Boolean(prs?.[0]?.merged_at);
...
385:    if (ok) {
386:      await env.DB.prepare("UPDATE tasks SET status='done', updated_at=datetime('now') WHERE id=?")
```

**Má být:** rozhodovat podle `ok && merged`, a když se PR nesloučil, **nekončit
jako `done`** — dát najevo, že se čeká na člověka.

- `merged` se **už načítá** na ř. 375 → **žádné nové volání API není potřeba**.
- Pozor: `merged` se nastaví jen uvnitř `if (ok)` (ř. 368–377), takže
  `ok && merged` je bezpečné.
- **Nový stav** (`awaiting_human`) **nezavádět do `roadmap.json`** (analýza §⑨
  bod 2) — jen do `tasks.status`. Do D1 smí, soubor ne.

**Ověření (musí být spustitelné, ne „vypadá to dobře"):**
- **Mutační test:** odebrat `&& merged` → test musí spadnout.
- **Živý důkaz po nasazení:** `SELECT count(*) FROM roadmap WHERE status='done'`
  musí být ≤ počet granul, jejichž `owns` soubor **je** v `origin/main`.
  Dnes (2. 10. 2026, 05:44 UTC) je to **11 `done` v D1**, ale v `main` chybí
  `save.gd`, `hud.gd`, `mining.gd` → **11 vs. 8**.
- **Konkrétní tři úlohy**, na kterých se to pozná: `#136`, `#139`, `#140`.

---

## A2 — `done:true` v souboru se ověří proti `origin/main`

**Soubor:** tentýž, `roadmapTick()`, ř. **588–608** (`continue` na ř. 607).

**Dnes:** `done === true` v `roadmap.json` **bezpodmínečně** zapíše `done` do D1
a granuli **nikdy nevydá**.

**Má být:** než se `done` zapíše, ověřit, že alespoň jeden soubor z `owns`
**existuje v `origin/main`** dané hry. Když ne → **nezapsat `done`** a **ohlásit**
(viz A4).

- **Volání API už v souboru je** — `index.ts:567` čte `roadmap_file` přes
  GitHub Contents API. Ověření `owns` je totéž volání na jinou cestu.
- **Pozor na cenu:** granul je 18 a každá má 1–3 soubory v `owns`, ale
  `roadmapTick` běží **každou minutu** (cron `* * * * *`). **Neověřovat
  u granul, které už `done` v D1 mají** (`done.has(key)`) — jinak 1440 volání
  denně navíc. Tohle je reálné riziko free plánu, viz `wrangler.toml:11-12`.

**Ověření:** `core.attributes` a `entity.item` **mají sloučené PR #19 a #20**,
ale **řádek v D1 jim chybí** (S30). Po A2 se musí chovat stejně jako dnes
(nevydat je) — **ale z ověřeného důvodu**, ne šťastnou shodou.

---

## A3 — `auto-merge` musí umět selhat

**Soubory (DVA, a musí se změnit NARÁZ):**
- `C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.github\workflows\agent.yml`
  — krok „Když pravidla neprošla", ř. **683–691**
- `C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.github\workflows\agent.yml`
  — týž krok, ř. **687–693** (nasazená verze má jiné číslování!)

**Dnes:** `gh pr comment` a **`exit 0`** → celý job je zelený, i když se
nesloučilo. Naměřeno proti **nasazené** verzi (raw z GitHubu, 33 425 B):
`exit 1` je v celém souboru jen na ř. 340, 372, 438, 454, 486 — **všechny před
auto-merge**.

**Má být:** po komentáři `exit 1`.

⚠ **Tři věci, které se u toho musí ohlídat:**
1. **Pořadí** — až po A1 (§0).
2. **Drift kontrola** `kontrola-driftu.mjs` hlídá **12 cest** a `agent.yml` mezi
   nimi je. Obě kopie se **musí změnit společně**.
   **Naměřeno 2. 10. 2026, 05:59 UTC — drift je ČERVENÝ UŽ DNES** (`exit 1`,
   „Zkontrolováno souborů: 12, rozdílů: 1"), a to **nezávisle na A3**:
   ```
   ROZDÍL .github/workflows/agent.yml
     jen v šabloně: Kontrola parsování GDScriptu (rychlá brána),
                    Kontrola class_name (staticky, Godot to nepozná),
                    Import assetů (než se pustí brána a testy)
     jen ve hře:    Kontrola parsování (rychlá brána), Import assetů (než se pustí testy)
   ```
   To je **S „šablona obsahuje bránu, kterou herní repo NEMÁ"** z handoffu 1. 10.
   (§3.3) — **statická kontrola stínění `class_name` se na hře nikdy nespustí.**
   **Důsledek pro A3:** po změně obou kopií bude drift pořád červený (kvůli tomuhle
   rozdílu kroků), takže **„drift prochází" NENÍ správné kritérium dokončení A3.**
   Kritérium je: **rozdíl v kroku „Když pravidla neprošla" zmizel** a `agent.yml`
   se v obou kopiích liší **jen v těch třech krocích, co už tam byly**.
3. **Nasazená verze hry se aktualizuje až pushem.** Do té doby platí stará —
   a to je důvod, proč se A3 **neprojeví hned**.

**Ověření:** po změně musí `agent.yml` v **obou** kopiích obsahovat `exit 1`
za krokem „Když pravidla neprošla". **Ověřit na řádku, ne grepem celého
souboru** — v souboru je `exit 1` už 5× a hledání celého souboru najde je.

---

## A4 — chybějící `size_lines` musí být vidět

**Soubor:** `C:\Users\Ssevc\Local-Deepseek\orchestra\tools\lint-roadmapa.py`

**Naměřeno:** `size_lines` chybí u **13 z 18** granul → `maxLinesOf()` vrátí
výchozích **60** (`index.ts:149-153`). To je příčina **všech tří** visících PR
(`save.gd` +90, `hud.gd` +76, `mining.gd` +66 — všechny > 60).

⚠ **Oprava mého vlastního tvrzení (naměřeno 2. 10. 2026, 05:59 UTC).**
V analýze §O7 jsem napsal, že lint o chybějícím `size_lines` **mlčí**. **Není to
pravda** — `python orchestra\tools\lint-roadmapa.py games\uo-shadows` vypíše
**sedm varování `[5]`** o granulích `done: true`, na které čekají závislosti:

```
[5] world.map je 'done: true' a čeká na ni 4 granulí … – MUSÍ mít řádek v D1,
    jinak závislosti zůstanou viset (conductor dělá jen UPDATE, ne INSERT)
```

**A přesto skončí `exit 0`.** To je **nový a přesnější nález** — není to
„brána mlčí", ale **„brána varuje a stejně nezabrání"**, tedy **tatáž třída jako
S32** (neúspěch, který je zelený). A text těch varování je **zastaralý**:
tvrdí „conductor dělá jen UPDATE, ne INSERT", ale `index.ts:600-603` dělá
**`INSERT … ON CONFLICT DO UPDATE`** (opraveno 30. 9. 2026). **Sedm varování
tedy radí něco, co už kód dělá** — a to je přesně past „dokumentace, která
popírá vlastní nástroje".

**Má být (A4 ve dvou částech):**
- **A4a** — lint ať hlásí **i chybějící `size_lines`** (dnes ho nehlásí vůbec).
- **A4b** — text varování `[5]` ať odpovídá kódu (`INSERT … ON CONFLICT`),
  nebo ať varování zmizí. **Nenechávat varování, které radí špatnou opravu.**

**Pozor:** `size_lines` mají jen granule určené **silnému modelu**. U slabého
modelu je 60 správně. **Varování ano, chyba ne** — jinak lint začne blokovat
i to, co je v pořádku (a to je přesně „brána, která nemá jak selhat", obráceně).

**Otevřená otázka k rozhodnutí:** má lint u `[5]` skončit **nenulově**?
Dnes je `exit 0`, takže v CI nic nezastaví. Kdyby ale skončil nenulově **teď**,
začne padat na sedmi granulích, které jsou v pořádku — proto to patří
**rozhodnout člověku**, ne „opravit" v rámci A4.

---

## Co NEDĚLAT (z analýzy §⑨ — opsáno, protože se to snadno „vylepší")

1. **Neotáčet pořadí A1/A3.**
2. **Nezavádět `awaiting_human` do `roadmap.json`** — soubor je autorita a
   rozšířil by se počet stavů, které nikdo neporovnává.
3. **Nemazat `done_note`** — je to jediné **čitelné** svědectví o S29. Až ho
   bude číst brána, zůstane.
4. **Nespoléhat na „soubor je autorita"**, dokud se nerozhodne, který ze **dvou
   vzájemně si odporujících komentářů** platí (`index.ts:1123-1126` vs.
   `:738-740`). Jeden z nich je nepravdivý.
5. **Nepřidávat další bránu**, dokud A3 neumí selhat.
6. **Nepushovat ani nenasadit bez vyžádání** (`AGENTS.md`).

---

## Hotovo znamená

- [ ] A1: `merged` rozhoduje o `done`; mutační test to dokazuje.
- [ ] A2: `done:true` bez souboru v `origin/main` se **nezapíše** a je to vidět.
- [ ] A3: `exit 1` v **obou** kopiích `agent.yml`; drift kontrola prochází.
- [ ] A4: `lint-roadmapa.py` hlásí chybějící `size_lines`.
- [ ] Po A1: tři otevřené PR (#28, #29, #30) **nejsou** v D1 jako `done`.
- [ ] **Dvě negativní kontroly:** s vrácenou vadou testy spadnou; a u **nových**
      souborů ověřeno, že je brána vůbec otevřela (past S27).
- [ ] Ukázáno `git status` + `git diff --stat`, **nepushnuto**.

## Otevřené otázky, které musí rozhodnout člověk

- **Má se `awaiting_human` propsat do notifikace?** (Dnes notifikace píše
  „(sloučeno automaticky)" i u nesloučeného PR — `index.ts:409`.)
- **Má A2 varovat, nebo jen mlčet?** (Kolik notifikací je ještě užitečných.)
- **Sloučit tři visící PR ručně, nebo granulím doplnit `size_lines`** a nechat
  je projet znovu? **A1+A2 to nevyřeší** — jen přestanou lhát.

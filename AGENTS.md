# Pravidla pro agenty v tomto workspace (projekt orchestra)

> **Co tenhle soubor JE:** **trvalá pravidla projektu** — orchestra, její
> šablona a hry, které vyvíjí. Platí **napříč session**; `HANDOFF.md` je něco
> jiného (stav jedné session, přepisuje se při každém předání).
>
> **⚠ VZNIKL PŘESUNEM NA `E:` (4. 10. 2026).** Do té doby bydlela projektová
> pravidla v `C:\Users\Ssevc\Local-Deepseek\AGENTS.md` (root **stanice**), a to
> byl problém: root stanice **není git repo**, takže orchestra sama
> (`E:\Workspaces\forge-orchestra`) `AGENTS.md` **neměla** — kdo otevřel session
> s cwd v repu, DSH našel projektový root podle `.git` a root `AGENTS.md` se
> **přestal načítat**. Naměřeno před přesunem: `.git` **True**,
> `AGENTS.md` **False**.
>
> **⚠ OBECNÁ PRAVIDLA STANICE TU NEJSOU.** Prostředí (pasti nástrojů
> a kódování), metody ověřování, dokumentační pravidla, hranice jazyka
> a obecný princip nasazení jsou v **`DSH_HOME\AGENTS.md`**
> (`~\.dsh\AGENTS.md`) — načítá je **každá session v každém workspace**.
> Tady je jen to, co platí **pro tento projekt**.
>
> **Pasti prostředí** (grep, cp1252, BOM/CRLF, EPERM ze sandboxu, temp, TLS)
> jsou ve skillu **`dsh-prostredi`**; metody ověřování ve skillu **`overovani`**;
> jak psát dokumenty ve skillu **`dokumentace`**. Odsud na ně vede odkaz —
> **kdo je hledá tady, nenajde je a nesmí si myslet, že neplatí.**

**Ověřeno měřením.** Každé pravidlo níž vzniklo z konkrétní chyby, která něco
stála. Když si nejsi jistý, jdi po důkazu — ne po znění.

---

## ⚠ Kde co po přesunu leží (4. 10. 2026)

| Co | Kde |
|---|---|
| **tento repozitář** (orchestra) | `E:\Workspaces\forge-orchestra` |
| **hra UO** | `E:\Workspaces\uo-shadows` — **sourozenec** repa, ne potomek |
| **koren stanice** | `C:\Users\Ssevc\Local-Deepseek` — dokumenty, které zůstaly stanici |
| **Godot** | `E:\Tools\godot\Godot_v4.7.2-stable_win64_console.exe` — obecný nástroj, **ne** součást repa |

**Vazba orchestra → hra je `FORGE_HRA` (env) s výchozím `..\uo-shadows`.**
Dřív to byl potomek `games/uo-shadows`; to už neplatí. Nástroje, které do hry
zapisují, proto **zapisují mimo workspace** a vyžádají si schválení.

**Tři dokumenty zůstaly STANICI** (rozhodnutí D6) a odkazuje se na ně
**absolutní cestou**:
`C:\Users\Ssevc\Local-Deepseek\` + `MOZNOSTI-AGENTA.md`, `OTEVRENA-TEMATA.md`,
`PREDAVANI-SESSION.md`. Není to opomenutí — stanice je používá i pro DSH
a obrázky a `OTEVRENA-TEMATA.md` je ledger, který se týká celé stanice.

## Než začneš

- Přečti `HANDOFF.md` (**stav**) a tenhle soubor (**pravidla**). Handoff je
  jediný vstupní bod ke stavu; tenhle soubor k pravidlům projektu.
- **Obecná pravidla stanice** (`DSH_HOME\AGENTS.md`) dostaneš automaticky —
  **neopisuj je sem**. Když narazíš na past, která tam ani ve skillu není,
  **doplň ji do skillu** (`dsh-prostredi`, `overovani`, `dokumentace`).
- **Tvrdíš-li, že něco umíš nebo neumíš, OVĚŘ to.** Zdroj pravdy o schopnostech
  je `C:\Users\Ssevc\Local-Deepseek\MOZNOSTI-AGENTA.md`; je měřený, ne odhadovaný.
- Než začneš psát nebo spouštět skripty, načti skill **`dsh-prostredi`**.

## Brány a měření tohoto projektu

Seznam bran, jejich čísla a jak je spustit je v **`HANDOFF.md` §6** — je to
stav, ne pravidlo, takže se přeměřuje s každou session.

- **⚠ KDO MĚNÍ KÓD, PŘEGENERUJE `_analyza\_inventar.json` — a možná víckrát.**
  Inventář je **generovaný a necommitovaný meziprodukt** (`N1`), a
  `hl-rizika-jazyka.py` **pozná, že zestaral** → skončí `exit 1` s hláškou
  „INVENTÁŘ JE ZASTARALÝ / NEZMĚNĚNÝ". **To je správné chování, ne vada
  nástroje.** Náprava:
  ```
  python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json
  ```
  **Počítej s tím víckrát za session** — vstupem skeneru je **i ta brána sama
  a každý skill, do kterého píšeš**. **Kontrolu nevypínej** — je to jediná
  obrana proti tomu, aby se „0 vrácených" četlo jako měření.
- **⚠ `done` JE TVRZENÍ, NE DŮKAZ — a staví se na něm celý DAG.** Naměřeno
  2. 10. 2026 na `uo-shadows`: `world.map` i `entity.player` byly `done`
  v roadmapě **i v D1**, ale jejich práce v repu nebyla. **Před stavbou na cizí
  granuli najdi její soubor v `main` a ZAVOLEJ to, co od ní voláš.**
- **Brány tohoto projektu mají místy RUČNÍ SEZNAM souborů** (např.
  `kontrola-diakritiky.py` a `kontrola-driftu.mjs`). Nový dokument, který
  v seznamu není, projde zeleně, **aniž ho kontrola otevřela** (vada **S27**).
  **Kdo přidá dokument, přidá ho i do seznamu.**
- **Drift mezi šablonou a hrou** hlídá `node tools\kontrola-driftu.mjs`
  a **známý rozdíl je jeden** (šablona má o tři kroky víc). Není to regrese.
- **⚠ KÓDOVÁNÍ SOUBORŮ: `.ps1` BOM MÍT MÁ, `.py` NESMÍ.** Není to vkus, je to
  **naměřené** (`_analyza/p20-b-bom-mereni.py`, P20 6. 10. 2026) — a každá
  polovina má jiný důvod:

  | Soubor | BOM | Proč |
  |---|---|---|
  | `.ps1` | **MUSÍ** | Bez BOM čte PowerShell soubor jako cp1252, české znaky se rozbijí a parser hlásí chybu na řádku, který je správně |
  | `.py` | **NESMÍ** | `compile()` ho odmítne (`invalid non-printable character U+FEFF`) → soubor je pro brány nekompilovatelný |

  **Past, která to spojuje:** `python soubor.py` s BOM **funguje** (`exit 0`),
  ale `compile()` nad týmž textem **spadne** — „jde spustit?" a „jde
  zkompilovat?" jsou **dvě různé otázky** (nález **H99**). Spustitelnost tedy
  **není** důkaz, že je soubor v pořádku.
  **Kdo zapíše `.py` přes `Set-Content -Encoding utf8`, vyrobí vadu** (omyl
  **189**, naměřeno v P19) — a odhalí ji **NA32**. Piš `edit`/`write` toolem
  a po zápisu zkontroluj **první tři bajty** (`EF BB BF` = BOM).
  **A ověřeno je i to, že se obě brány nerozcházejí:** tentýž `.py` s BOM
  položený do živého stromu hry vykázaly **NA32 i H79** (`exit 1`) — naměřeno,
  ne odvozeno. Kdyby se někdy rozešly, je to vada brány, ne detail.
- **Dokumenty, které se kontrolují:** `kontrola-diakritiky.py`,
  `over-dokumentaci.py`, `over-skilly.py` — **po každé editaci je spusť.**
  Brána `over-dokumentaci.py` má **pevný seznam požadovaných textů**, a to
  i pro **obecná pravidla** v `DSH_HOME`: kdo pravidlo přeformuluje nebo
  přesune, **musí upravit i ji** — jinak hlásí chybu u souboru, který je
  v pořádku (naměřeno 4. 10. 2026 při přesunu obecných pravidel: 13 z 15
  textů bydlelo v přesouvaných sekcích).
- **⚠ MUTUJ PŘES `_analyza\_mutace.py` — NE vlastním `replace()`.** Naměřeno
  6. 10. 2026 (klasifikace **205 omylů**): **15 omylů** je „mutace se tiše
  neprovedla / nezměnila měřenou podmínku — a prošla"; dva z nich (omyly
  **#18** a **#106**) jsou **tentýž omyl dvakrát** (nové jméno obsahovalo staré
  jako **podřetězec**) a další čtyři (#138, #173, #190, #198) jsou čtyři různé
  způsoby, jak mutace „prošla" bez provedení. **Dřív mělo každé měřidlo vlastní
  opis — proto se vada opakovala.** Knihovna hlídá pět věcí: kotva je v souboru
  **právě 1×**, text se **skutečně změnil**, nový text **neobsahuje starý jako
  podřetězec**, soubor se **vždy vrátí** (`try/finally`) a návrat je
  **bajt na bajt** (`sha256`):
  ```python
  import sys; sys.path.insert(0, str(WS / "_analyza"))
  from _mutace import mutuj
  with mutuj(SOUBOR, "stary text", "novy text") as m:
      ...   # spustit bránu a ověřit, že SPADLA
  ```
  Použití je předvedené (a sabotáží ověřené, že měří) v
  `_analyza\p22-test-mutace.py` — **19/0**; test **zmutuje živou bránu**
  a ověří, že se její **verdikt změnil**.

## Jak dokumentovat (dokumenty tohoto projektu)

**Postup, druhy dokumentů a checklist: skill `dokumentace`.** Tady je jen to,
co je vázané na tento projekt:

- **`HANDOFF.md` je stav a přepisuje se; `KRONIKA-PROJEKTU.md` se NIKDY
  nepřepisuje, jen doplňuje** — je to jediné místo, kde přežije historie.
  Ověřuje `python _analyza\kronika-kontrola.py`.
- **Přepisuješ-li `HANDOFF.md`, nic nesmí zmizet.** Otevřené body jsou
  nejdražší položka předání. Po přepisu **vypiš, které body zůstaly**, a ověř
  je hledáním — nástrojem `python _analyza\handoff-kontrola-uplnost.py`.
  Co už otevřené není, se **přesune** do „Co už otevřené NENÍ" — **nemaže se**.
- **⚠ Zdroj pravdy o STAVU je živé měření, ne dokument.** Naměřeno 1. 10. 2026:
  handoff tvrdil, že dva commity **nejsou pushnuté**; GitHub API vrátilo jeden
  z nich jako **HEAD repa**. Nepravdivé tvrzení o stavu se čte jako fakt
  a **plánuje se podle něj**.
- **Zapíšeš-li do dokumentace ukázku rozbitého kódování, kontrola diakritiky to
  nahlásí jako vadu dokumentu.** Popisuj je **slovem**.

## Jazyk: kde česky a kde ne (změřeno 1. 10. 2026)

> **Pravidlo je v obecných pravidlech** (`DSH_HOME\AGENTS.md`): identifikátory,
> klíče a literály rozhraní ASCII; dokumentace a komentáře česky; výstup pro
> člověka česky, hodnota pro program anglicky. **Tady je jen měření tohoto
> projektu** — je to důkaz pravidla, ne pravidlo.

**Změřeno inventářem `_analyza\hl-neanglicky-v-kodu.py`.**

> **⚠ PŘEMĚŘENO 4. 10. 2026 PO PŘESUNU NA `E:`** — a je to **nález o měřidle,
> ne o kódu**: tabulka níž byla naměřená **1. 10. 2026** nad **161 soubory**,
> ale po přesunu měří tentýž nástroj **jiný rozsah** (3310 souborů): do repa se
> totiž přesunuly i **projektové dokumenty a `_analyza/`** (D3), které dřív
> v žádném gitu nebyly. Řádek o **názvech souborů** proto **přestal platit**
> (tvrdil 0 non-ASCII názvů, naměřeno **68**) — a odhalila to brána
> `ag-over-cisla.py`. **Historické hodnoty se nepřepisují** (jsou „ve svém čase
> správné"); co platí dnes, je u nich uvedené.

| Vrstva | Naměřeno 1. 10. (161 souborů) | Dnes (3310 souborů) | Verdikt |
|---|---|---|---|
| Názvy souborů a cest | 113 souborů, non-ASCII v názvu: **0** | **68** non-ASCII názvů | ⚠ **změna rozsahu** — `_analyza/` a dokumenty se přesunuly do repa; 68 názvů je v archivech a scratchích, ne v živém kódu |
| Názvy sloupců D1 (`conductor/schema.sql`) | 5 tabulek, **40 sloupců, českých 0** | **5 / 40 / 0** | ✅ nezměněno |
| Klíče a identifikátory CI | `task_id`, `run_key`, `FORGE_*` — ASCII | totéž | bez rizika |
| Diakritika v `.md` orchestra | 2 533 znaků ze 44 781 = **5,7 %** | **536 623 ze 7 476 476 = 7,2 %** | ⚠ **změna rozsahu** — `.md` se commitovaly (3a2e691) a přesunuly; **poměr zůstal**, jev je týž |
| Čeština jako IDENTIFIKÁTOR | **10 míst** | **0** (přejmenováno Z1–Z8) | ✅ vyřešeno |

> **⚠ TŘETÍ MĚŘENÍ — 4. 10. 2026 (P13c, po opravě měřidla):** skener měřil
> **jen soubory z gitu** (`git ls-files`), takže **necommitnutý nový kód pro
> jazykovou bránu NEEXISTOVAL** — a to je přesně ten kód, který se má před
> commitem zkontrolovat (nález **H52**). Navíc načetl **jen 205 z 1008** souborů,
> protože rozbitý `require` v `js-tokeny.mjs` hledal TypeScript ve **starém
> layoutu** → **68 JS/TS souborů** (včetně `conductor/src/index.ts`) skončilo
> v NEPOKRYTO. Dnešní naměřený stav:
>
> | Veličina | Hodnota |
> |---|---|
> | souborů zpracováno | **274** (z toho **14 NETRACKOVANÝCH** — dřív neviditelné) |
> | vyloučeno vzorem artefaktů | **11** (archiv, zálohy, cache, mezivýstupy skeneru) |
> | NEPOKRYTO | **0** (dřív 69) |
> | nálezů v inventáři | 5 504 |
> | **SKUTEČNÉ NÁLEZY identifikátorů** | **0** (13 textových/porovnávaných literálů je správně česky) |
>
> **Co z toho plyne pro pravidlo:** brána, která čte jen git, **nemůže zabránit
> commitnutí vady** — nový soubor je pro ni neviditelný, dokud ho někdo
> necommitne. Kontrola se proto dělá **před** commitem a čte i netrackované.

**Naměřené příklady (každý z kódu, ne z dojmu):**

> **⚠ DATUM SPOTŘEBY (doplněno 2. 10. 2026):** příklady níž jsou **naměřené
> důkazy pravidla, ne popis dnešního kódu.** Všechny uvedené identifikátory
> byly **2. 10. 2026 přejmenovány** (plán Z1–Z8). Kdo je půjde hledat do kódu,
> **nenajde je** — a to je správně. **Nemažou se:** bez nich by pravidlo
> nebylo doložené. Nový stav: `hl-rizika-jazyka.py` → **0 očekávaných,
> 11 přejednaných, 0 vrácených**.

- `conductor/src/index.ts:247` → `let ohlášeno = 0;` — jediný český
  identifikátor v jádře orchestra (ASCII varianta: **0 souborů**). Drží
  konzistentně i v patchi `tools/pridej-eskalaci.py:50`.
  **→ přejmenováno na `notified`** (Z1).
- **hra** `scripts/assist.gd:11–15` — **veřejné rozhraní
  `add_rule(trigger, action)` míchá jazyky**: `"hp < X"` a `"mana < X"`
  anglicky, ale `"cíl mrtev"` česky s diakritikou. Volající musí uhodnout jazyk.
- `tools/analyza-modelu.mjs:58` → `poz === '—'` — **porovnává se
  s pomlčkou, kterou si tentýž skript sám vykreslil jako prázdnou hodnotu.**
- `repo/.forge/check-schema.py:392` **a** hra `.forge/check-schema.py:392` →
  `nesedí = []`; `make_iso_tiles.py:261` → `pás`; **a taky `.forge/vision.mjs:42,47`**
  → `function vezmiPrepínac(...)`. **Táž past jako u `.gitattributes`:** soubory
  existují ve **dvou kopiích** (šablona + hra) a drift test hlídá shodný hash
  → přejmenovat se musí **obě naráz**.
- `tools/sjednot-sablonu.py:111` →
  `if s.get("name") == "Spusť agenta"` — **skript si z cizího `agent.yml`
  vyfiltruje krok podle DOSLOVNÉHO českého názvu.** Ověřeno 1. 10. 2026: název
  (`agent.yml:116`, resp. `:121`) **sedí**, takže dnes to funguje. Ale selhání
  je tiché: po přejmenování je `kroky` prázdný list → `env_ok = False` →
  skript to **vypíše a stejně skončí úspěšně**. „Brána, která nemá jak selhat."
- hra `assets/spec.json` → klíč `styl.zmenšování` je **jen
  v lidském popisu** (0 čtenářů v kódu) → **nechat být**; není to identifikátor.

## Jak ověřit nasazení na GitHub Pages (příkazy tohoto projektu)

> **Obecný princip** (HTTP 200 není důkaz; push → build na správném commitu →
> server posílá nový artefakt) je v `DSH_HOME\AGENTS.md`. **Tady jsou konkrétní
> příkazy a cesty** — ty patří projektu.

1. **Push dorazil:** `git rev-list --count origin/main..HEAD` → `0`.
2. **Workflow na správném commitu:** `node tools\zjisti-pages.mjs`
   → poslední `release.yml` má `head:<nový commit>` a `completed/success`.
3. **Server posílá nový build:** `last-modified` v HTTP hlavičkách je
   **po** pushi (Node `fetch` s `method: 'HEAD'` — z PowerShellu TLS nejde):
   ```powershell
   node -e "const r = await fetch('https://ssevcikm-spec.github.io/uo-shadows/index.png',{method:'HEAD'}); console.log(r.status, r.headers.get('last-modified'));"
   ```
   HTML stránky je jen shell s canvasem — **z HTML se verze nepozná.**

## Co nikdy (v tomto projektu)

- **Nepushovat bez vyžádání.** Předem ukázat `git status` a `git diff --stat`.
- **Nemazat cizí repozitáře ani jejich Pages.** `forge-quest` je **živá hra**,
  ne mrtvá minulost — a v konfiguraci už jednou zůstal odkaz na ni místo na
  tuhle hru (kdo ho otevřel, hrál něco jiného).
- **⚠ `E:\DSH` UŽ NEEXISTUJE — datový adresář se přestěhoval (1. 10. 2026).**
  `C:\Users\Ssevc\.dsh` → **`E:\DeepSeekHarness-data`**; stará data
  i `roaming` jsou v `E:\DSH-quarantine\20261001-144747\` (**to je rollback,
  nemaž ho, dokud nejsi spokojený**). Postup a měření:
  `C:\Users\Ssevc\Local-Deepseek\POZOR-E-DSH-NEMAZAT.md`.
- **Nepřebírat tvrzení o schopnostech** z dokumentace bez ověření.
- **Neopravovat nástroj dřív, než je jasné, co je špatně** — nástroj, nebo
  předpoklad testu.
- **⚠ Nedělat junctionu na staré místo.** Kdyby cesty po přesunu vedly přes
  junctionu zpátky na `C:\...\Local-Deepseek\orchestra`, každá nepřepsaná cesta
  by **tiše fungovala dál** — a to je přesně to, čemu se přesun vyhýbal.
  Cesty mají **spadnout nahlas**.

## Kam pro co

| Soubor | Co v něm je |
|---|---|
| `HANDOFF.md` | stav poslední session, „pick up here" |
| `KRONIKA-PROJEKTU.md` | **celý příběh projektu** — session po sessioni, nálezy (N/H/S/V/P), **omyly a jejich trend**, poučení s naměřenými případy, **návrhy se stavem** (`NEOVĚŘENO` → `APLIKOVÁNO`/`ZAMÍTNUTO`/`ODLOŽENO`). **Nikdy se nepřepisuje, jen doplňuje** — je to jediné místo, kde přežije historie. Ověřuje `python _analyza\kronika-kontrola.py`. **Návrh na zlepšení zapíše session hned, ale rozhodne o něm až ta příští** — autor není nezávislý reviewer. |
| `PREDAVANI-SESSION.md` (STANICE) | **jak volat další session** — dva kroky (plánovací → akční), šablony promptů ke zkopírování, „Hotovo znamená" pro každou session a naměřené pasti předávání. **Tenhle soubor říká JAK předávat; stav je v `HANDOFF.md`.** Leží v `C:\Users\Ssevc\Local-Deepseek\`. |
| `AGENTS.md` | tenhle soubor — trvalá pravidla projektu (obecná pravidla stanice jsou v `DSH_HOME\AGENTS.md`) |
| `MOZNOSTI-AGENTA.md` (STANICE) | co agent umí (měřené důkazy) a co ne |
| `JAK-PSAT-DESIGN-A-PLANOVAT-VYVOJ.md` | **jak psát design dokumenty a plánovat vývoj pro AI pipeline** — rostoucí podklad pro revizi skillu `game-developer` a pro přepis designu UO-Shadows; **každá session do něj doplňuje naměřené případy** |
| `NEXT-SESSION-INSTRUKCE.md` | **zadání pro PŘÍŠTÍ session** — přepisuje ho vždy ta session, která končí. **Není to stav ani plán:** stav je v `HANDOFF.md`, plán v `PLAN-DALSI-KROK.md`. Kdo ho čte, **ověří hlavičku** (`rev-parse HEAD` v obou repech) — když nesedí, přeměří **všechna** tvrzení o stavu. |
| `PLAN-DALSI-KROK.md` | **plán dalších kroků** — co dělat, v jakém pořadí a co **NE**. Má **hlavičku s datem spotřeby**: analytický dokument, ze kterého se něco provedlo, musí říct, **co z něj ještě platí** — jinak se čte jako popis dneška. |
| `PLAN-ROZVOJ-ORCHESTRA.md` | plán: architektura a kontrakt — fáze F0–F5, **§3.5 implementační plán (fáze A–D)**, otázky O1–O10 |
| `PLAN-ORCHESTRA-AI-AGENTI.md` | plán: provoz s AI agenty (N0–N5, otázky R1–R15) |
| `PLAN-SEPARACE-WORKSPACE.md` | plán: separace orchestra z workspace stanice (G0–G5, S1–S9) — **a záznam přesunu na `E:` (4. 10. 2026, §10–§11)** |
| `ANALYZA-ARCHITEKTURY-ORCHESTRA.md` | analýza architektury (16 tříd selhání S1–S16 + §8 dodatek se S17/S18) |
| `ANALYZA-HLOUBKOVA-ORCHESTRA.md` | **výsledek hloubkové analýzy (1. 10. 2026)** — 12 oddílů, třídy selhání **S19–S30**, 9 z 10 otázek, 2 varianty návrhu, vlastní omyly |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` | **výsledek DRUHÉHO kola (2. 10. 2026)** — **⚠ SNAPSHOT, ne popis dneška**. Sekce S31–S37. **Ověřeno `_analyza\n8-zastarala-analyza.py`** |
| `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` | **✅ ZÁZNAM O PROVEDENÍ A1–A4** (2. 10. 2026) — původně zadání; teď doklad, co a proč se změnilo. Drženo **závazné pořadí** (A3 před A1 = smyčka) |
| `IMPLEMENTACE-HRANICE-JAZYKA.md` | **✅ ZÁZNAM O PROVEDENÍ Z1–Z8** (2. 10. 2026) — hranice jazyka v kódu; 11 míst přejmenováno, obě kopie se shodným hashem |
| `IMPLEMENTACE-NOVE-NALEZY-Z-UKOTVENI.md` | **N1–N8 + plán (neprovedený)** — nálezy z provádění A1–A4/Z1–Z8, každý doložený spuštěním. **Odkud pokračovat.** |
| `PROMPT-NOVA-SESSION.md` | **prompt pro nový chat (2. 10. 2026)** — **výzva k ověření práce** předchozí session (10 měřitelných bodů, u každého příkaz) + co dál. |
| `SOUBEH-SESSION-NALEZY.md` | **co proklouzlo, když dvě session psaly tytéž soubory** (2. 10. 2026) |
| `POUCENI-A-VZORY.md` | **katalog vzorů a poučení (V1–V11)** — souhrn naučených vzorů z celého projektu. ⚠ **Do 6. 10. 2026 nebyl v ŽÁDNÉM rejstříku** — audit KB naměřil **0 odkazů ve všech 622 `.md`** obou stromů. Zaregistrován 6. 10. 2026. Překrývá se s `SKILLY-AKTUALIZACE.md` (obojí „co se naučilo"); ten drží KRONIKA §7, tenhle nikdo. |
| **dokumenty mimo tuhle tabulku** | `NAVRH-ORCHESTRA-NG.md`, `PLAN-ORCHESTRA-NG.md`, `PLAN-VISION-ORCHESTRA.md`, `ASSETY.md` + `ASSETY-PLAN.md`, `ORCHESTRA-STAV-A-ANALYZA.md`, `ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md`, `ANALYZA-HLOUBKOVA-ZADANI.md`, `ARCHITEKTURA-ANALYZA-ZADANI.md`, `FORGE-ORCHESTRA-MOZNOSTI.md`, `SKILLY-AKTUALIZACE.md`, 6× `ZADANI-*.md` — audit KB 6. 10. 2026 naměřil, že **~434 kB z nich má 0 odkazů v živých dokumentech** (nejvíc `NAVRH-ORCHESTRA-NG.md`, 91 kB). Jsou to **doklady měření**, ne smetí — patří do `_analyza\_archiv\`, **ne do koše**. Rozhodnutí, co archivovat, je v `OPTIMALIZACE-KNOWLEDGE-BASE.md` §5b a §6.12. |
| `_analyza\` | **analytické nástroje projektu** — brány, mutační testy, skeny a sondy. **Autorita seznamu živých bran je `BRANY` v `_analyza\g3-brany.py`** (+ `spust()` v `tools\validate-all.mjs` a vzor `VZOR` v `p20-d-doklady.py`); `g3` je taky **spouští** a vypisuje, co která otevřela. ✅ **`_analyza\_registr-bran.json` je od 6. 10. 2026 GENEROVANÝ `g3`**: `python _analyza\g3-brany.py` ho přepíše **výstupem běhu** (37 bran s `exit`, čítačem a příkazem + seznamy deklarovaných výjimek) — **needituj ho rukou**, kdo ho chce aktuální, **pustí `g3`**. Do 6. 10. 2026 to byl **ruční** soubor z **2. 10.** s **předpřesunovou** cestou `C:\Users\Ssevc\Local-Deepseek\orchestra` — tj. **tři seznamy živých a ani jeden se neshodoval s během** (nález §6.14). Totéž platí pro **ruční výčet v `HANDOFF.md` §6** (je to záznam, ne seznam živých). Zbytek nástrojů je v `_analyza\_archiv\` (D5). |
| `orchestra\repo\` → `repo\` | **šablona herního repa** — co orchestra dává nové hře |
| `tools\` | nástroje orchestra: `git.cmd` (OpenSSL backend), `zjisti-pages.mjs`, `kontrola-driftu.mjs`, `lint-roadmapa.py`, `sync-sablona-hra.py`, `asset-fetch.mjs`, `over-dokumentaci.py`, `kontrola-diakritiky.py`, `over-skilly.py` |
| `C:\Users\Ssevc\Local-Deepseek\OTEVRENA-TEMATA.md` (STANICE) | **ledger** všech otevřených témat (+ spustitelná kontrola tlaku na kontext) |
| `~\.dsh\skills\` | skilly (`dsh-prostredi`, `overovani`, `dokumentace`, `orchestra`, `game-developer`, `game-assets`, `vision`, …) |
| `DSH_HOME\AGENTS.md` | **obecná pravidla stanice** — platí v každém workspace, nejsou součástí tohoto projektu |

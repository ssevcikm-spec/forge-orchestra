# PLÁN ÚPRAV Z NOVÝCH NÁLEZŮ — implementace A1–A4 a Z1–Z8

> **Co tenhle dokument je.** Třetí krok zadání z 2. 10. 2026: *„napiš plán
> úprav z nových nálezů z kroku 1, pokud nějaké jsou."*
>
> ## ⚠ OPRAVA MÉHO VLASTNÍHO TVRZENÍ (2. 10. 2026, doplněno)
>
> **Napsal jsem sem, že „krok 1 (prompt) nedorazil". To bylo NEPRAVDA.**
> Prompt **v repu ležel celou dobu** — je to `ANALYZA-HLOUBKOVA-2-ZADANI.md`,
> a **je splněný**: ověřeno spuštěním `_analyza\hl2-kontrola.py` →
> **9/9 bodů „Hotovo znamená", `exit 0`**, a ta brána **umí selhat**
> (mutační test **6/6**).
>
> **Jak jsem k tomu špatnému závěru došel:** `HANDOFF.md` §8.4 tvrdí, že zadání
> je splněné, a já to **převzal, aniž jsem soubor otevřel**. Pak jsem napsal
> „prompt nedorazil" — tedy jsem **označil za chybějící něco, co jsem
> nezkontroloval**. Je to táž vada, kterou tenhle projekt dokumentuje pořád:
> *„Nevěřit číslům z handoffu bez ověření"* + *„než něco označíš za nepravdivé,
> zopakuj to týmž postupem."* **Neudělal jsem ani jedno.**
>
> **Co z toho plyne pro tenhle plán:** nálezy **N1–N8 jsou z mé vlastní práce**
> (provádění A1–A4 a Z1–Z8), **ne** z hloubkové kontroly. To je jejich mez —
> viz §0 níž, který to říkal správně, jen z nesprávného důvodu.
>
> **Datum:** 2. 10. 2026 · **Stav:** nálezy ZMĚŘENÉ, plán NEPROVEDENÝ (kromě N5, N7).
>
> ⚠ **Prázdný plán by byl taky výsledek — ale není prázdný.** Při provádění
> se našlo **8 nových nálezů**, z toho **tři s dopadem na důvěryhodnost
> měření** (N1, N2, N8) a **jeden vlastní omyl** (N7).


---

## 0. Jak tenhle plán vznikl (a co ho omezuje)

Nálezy níž **nevznikly hledáním vad** — vznikly jako **vedlejší produkt**
provádění plánu. To je jejich silná i slabá stránka:

- **Silná:** každý je doložený **spuštěním**, ne čtením (u každého je příkaz
  a naměřený výsledek).
- **Slabá:** **nejsou systematické.** Kdo hledá vady cíleně, najde jiné.
  Tenhle plán **nenahrazuje** hloubkovou kontrolu — je to její doplněk.

> **A jedna mez navíc, kterou je potřeba vidět:** N1–N8 **nejsou** výsledkem
> nezávislého pohledu. Napsal je **ten, kdo zároveň opravoval kód** — a
> `hlouchkova-analyza` §1 říká, že *„autor není nezávislý reviewer."*
> Proto je u každého nálezu **spustitelný důkaz**, aby se dal **vyvrátit
> bez toho, aby mi někdo věřil.** Nová session má za úkol přesně to.

**Co se v této session provedlo** (aby bylo jasné, proti čemu se nálezy měřily):

| Plán | Položky | Stav |
|---|---|---|
| `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` | **A1–A4** | **provedeno**, pořadí dodrženo |
| `IMPLEMENTACE-HRANICE-JAZYKA.md` | **Z1–Z8** | **provedeno** (Z3 = „neměnit", beze změny) |
| **Ověřeno, že krok 1 byl splněn** | `ANALYZA-HLOUBKOVA-2-ZADANI.md` | **9/9 bodů**, `hl2-kontrola.py` |

**Nepushnuto, necommitnuto** — dle `AGENTS.md`. `HEAD` obou repů beze změny
(`3a2e691`, `d0bf4f9`).


---

## N1 — Inventář jazyka měří ZASTARALÝ snapshot (nejdůležitější nález)

**Třída:** S27 („brána je zelená nad dokumentem, který nikdy neotevřela")
v nové vrstvě — **měřidlo, které tiše měří jiný čas, než si myslíš.**

**Co se naměřilo (2. 10. 2026, ~08:45):**

| Krok | Příkaz | Výsledek |
|---|---|---|
| 1 | `python _analyza\hl-neanglicky-v-kodu.py` (ráno) | zapsal `_inventar.json`, **08:01:23** |
| 2 | rename Z1/Z2/Z4/Z5/Z6/Z8 v kódu | soubory změněny **08:38–08:39** |
| 3 | `python _analyza\hl-rizika-jazyka.py` | **hlásí 7 nálezů, které už jsou přejmenované** |

Výpis tvrdil `orchestra/conductor/src/index.ts :: ohlášeno`, `…check-schema.py
:: nesedí` (2×), `assist.gd :: cíl mrtev`, `make_iso_tiles.py :: pás`,
`test-eskalace.py :: ohlášeno`, `analyza-modelu.mjs :: —` — **a všech sedm
v kódu už bylo opravených.**

**Proč to vzniklo:** `hl-rizika-jazyka.py` si `_inventar.json` vygeneruje
**jen když soubor CHYBÍ** (`if not INVENTAR.is_file()`). Když existuje,
**použije ho bez ohledu na stáří** — a nikde neřekne, k jakému času patří.

**Proč je to horší než obyčejná chyba:** nástroj **vypadá, že měří**.
Kdo po opravě spustí `hl-rizika-jazyka.py` a uvidí „CHYBÍ: ohlášeno",
udělá jeden ze dvou špatných závěrů:
- „rename se nepovedl" → **přejmenuje to znovu** (práce navíc), nebo
- „seznam nesedí, nástroj je rozbitý" → **přestane mu věřit** (a to je
  přesně ten stav, kdy ti unikne skutečný návrat češtiny).

**Má být (návrh):**
1. `hl-rizika-jazyka.py` ať **porovná `mtime` inventáře proti `mtime`
   nejnovějšího zdrojového souboru**; když je inventář starší, **řekne to**
   (a podle `--strict` buď spadne, nebo si inventář sám přegeneruje).
2. Do **výpisu** patří **čas vzniku inventáře** — jako u každého jiného
   měření v tomhle projektu (`AGENTS.md`: *„ke každému číslu patří postup
   a čas"*).
3. Stejná kontrola patří i k `_analyza\a1-a2-over.py` a `a3-over.py`
   (čtou zdroj, ale neověřují, že je „ten po změně").

**Ověření:** změň jeden soubor, nespusť inventář znovu → nástroj **musí**
hlásit „inventář je starší než kód". Mutační test na to je součástí opravy.

---

## N2 — `hl-neanglicky-v-kodu.py` a `hl-rizika-jazyka.py` nejsou jeden nástroj

**Třída:** táž jako N1, ale **rozhraní**: dva soubory, mezi nimiž je
**skrytý meziprodukt**, a nic nehlídá, že patří k sobě.

**Co se naměřilo:** `hl-rizika-jazyka.py` **není** samostatné měření — čte
`_analyza\_inventar.json`, který vyrábí `hl-neanglicky-v-kodu.py`. Po mých
renamenech stačilo **znovu vygenerovat inventář** a seznam okamžitě přešel
z `7 CHYBÍ` na **`0 očekávaných, 11 přejednaných, 0 vrácených`, `exit 0`**.

**Důsledek pro dokumentaci:** `IMPLEMENTACE-HRANICE-JAZYKA.md` §5 krok 2
předepisuje `python _analyza\hl-neanglicky-v-kodu.py` a krok 6 očekává
**„0 rozdílů"** — ale **neříká, že se inventář musí přegenerovat** mezi
renamem a kontrolou. Kdo plán plní doslova poprvé, dostane **falešný
poplach** (přesně to se stalo mně).

**Má být:** do `IMPLEMENTACE-HRANICE-JAZYKA.md` §5 doplnit, že kontrola rizik
**vyžaduje čerstvý inventář** — nebo (lépe) aby si ho nástroj vynutil sám
(viz N1). Do dokumentace patří i to, že **`hl-rizika-jazyka.py` je brána nad
meziproduktem**, ne nezávislé měření.

**Poznámka, která to zmírňuje:** `hl-rizika-jazyka.py` si inventář
**vygeneruje sám, když chybí** — takže „spustit z čistého klonu" funguje.
Vada je **jen v cestě „soubor existuje, ale je starý"**, což je v praxi
**ten častější případ**.

---

## N3 — `sjednot-sablonu.py` kontroluje krok, který v herním repu NENÍ ten správný

**Třída:** **NOVÁ** — „kontrola projde na obou místech, ale **z různých
důvodů**" (návaznost na S31: stav bez protějšku).

**Co se naměřilo** (`_analyza\z8-probe.py`, 2. 10. 2026):

| Repo | Krok s `FORGE_ATTEMPT` v `env` | `env_ok` dnes |
|---|---|---|
| **šablona** | `Spusť agenta` (step #6) | `True` |
| **hra** | **`Vyber bezplatného poskytovatele LLM`** (step #5) | `True` (ale jiný krok!) |

**Kontrola hledala krok podle názvu `"Spusť agenta"`.** V herním repu krok
toho jména **existuje** a `FORGE_ATTEMPT` v něm **je** — takže `env_ok` je
`True`. Jenže **`FORGE_ATTEMPT` nese i jiný krok**, a právě ten je v obou
souborech ten rozhodující. Kontrola tedy prochází **náhodou**: kdyby se
v herním repu přejmenoval `Vyber bezplatného poskytovatele LLM`, kód
`pick-provider.mjs` by o pokus přišel a **kontrola by nic nehlásila**.

**Druhá polovina téhož:** `sjednot-sablonu.py` kontroluje **jen šablonu**
(`SABLONA = orchestra/repo/.github/workflows/agent.yml`) a **vrací `0`
i když je `env_ok = False`** — takže i po opravě kritéria (Z8, provedeno)
byla původně zelená slepá. **Opraveno v rámci Z8** (`return 1`).

**Má být:**
1. Kontrola ať ověří **obě kopie** `agent.yml` (šablona **i** hra) — dnes
   jen šablonu. Hra je ta, která se skutečně nasazuje.
2. Ať ověří, že `FORGE_ATTEMPT` je **právě v jednom** kroku (provedeno),
   **a zároveň** že tím krokem je ten, který spouští agenta — jinak se
   `attempt` ztratí, i když je „někde".
3. Zvážit, jestli **není vada v datech**: dva různé kroky nesoucí
   `FORGE_ATTEMPT` v různých repech je **drift**, který `kontrola-driftu.mjs`
   nevidí (ten kontroluje jen **názvy kroků**, ne `env`).

**Cena:** malá (jeden soubor). **Riziko:** nízké.

---

## N4 — `kontrola-driftu.mjs` je slepá k `env` kroků

**Třída:** návaznost na S27/N3.

**Co se naměřilo:** `kontrola-driftu.mjs` u `agent.yml` hlásí
**„jen v šabloně (kroky): …, jen ve hře (kroky): …"** — tedy porovnává
**množinu jmen kroků**, ne jejich obsah. Když se změní `env`, `run` nebo
`if` u kroku, který v obou je, **rozdíl neuvidí**.

**Doloženo:** A3 přidal do **obou** kopií `exit 1` — drift to **nezaznamenal
jako nový rozdíl** (počet rozdílů zůstal `1`). To je v tomhle případě
**správně** (změna je symetrická), ale znamená to, že **drift by
nezachytil ani změnu jen v jedné kopii**, pokud by se netýkala jména kroku.

**Má být:** drift ať u společných kroků porovná i `env`/`run`/`if`
(normalizovaně), ne jen jméno. **Nebo** ať dokumentace výslovně řekne, že
drift hlídá **jen strukturu kroků**, a co tedy **není** pod kontrolou.

**Pozor na past:** `agent.yml` se dnes liší **třemi kroky** (class_name
kontrola se na hře nikdy nespustí) — plný obsahový diff bude **pořád
červený**. Oprava tedy musí rozlišit „známý rozdíl" od „nový rozdíl",
jinak vznikne brána, která **vždycky svítí** (a to je totéž jako nesvítit).

---

## N5 — Komentář `index.ts:372-374` (S34) je po A1 **zastaralý**

**Třída:** S34 („komentář tvrdí opak toho, co kód dělá") — **vrácená
vlastní opravou**, jen v jiné podobě.

**Co se naměřilo:** původní komentář tvrdil, že `run.status === completed`
znamená, že **doběhl i krok sloučení**, a že se stavu „dá věřit". To bylo
**nepravdivé** (S34) a A1 to vyvrátil. Komentář jsem **doplnil** o měření
(A1), ale **původní tři věty jsem nechal stát** — a ty jsou pořád
v rozporu s tím, co kód dělá.

**Má být:** původní tvrzení **přeformulovat nebo smazat**. Dnes si čtenář
přečte „dá se věřit" a **o tři řádky dál** „není to totéž co sloučeno".

**Cena:** kosmetická. **Riziko:** žádné — ale je to **přesně ta vada,
kterou má tenhle projekt nejradši**, a nechat ji po sobě by bylo pokrytecké.

---

## N6 — `lint-roadmapa.py` hlásí **10** varování `[5]`, ne 7

**Třída:** číslo bez postupu (`AGENTS.md`).

**Co se naměřilo:** `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` (A4) tvrdí
**„sedm varování `[5]`"**. Naměřeno 2. 10. 2026 **před** mými změnami:
**10** varování.

**Vysvětlení (není to lež):** dokument měřil v jiném čase — `roadmap.json`
se mezitím změnil (hra má dnes **10 granul `done: true`**, dřív 7).
**Rozdíl je tedy čas, ne nepravda** — přesně případ, kvůli kterému
`AGENTS.md` žádá **čas u každého čísla**.

**Má být:** do `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` doplnit
**„naměřeno k <času>: 7"** (a nepřepisovat na 10 — hodnota v dokumentu
byla správná **ve svém čase**). Stejně u „13 z 18" (to dnes **sedí**).

**Proč to sem patřím i tak:** je to **třetí** případ v jednom dni, kdy
číslo v dokumentu nesedí **proto, že se změnil stav** — a příště to někdo
označí za nepravdu a „opraví" správný dokument.

---

## N7 — VLASTNÍ OMYL: cache `origin/main` bez expirace (N1 v mém vlastním kódu)

**Třída:** **vlastní omyl** — zapsaný proto, že je to **tentýž vzorec jako N1**,
jen o vrstvu níž.

**Co se stalo:** v A2 jsem napsal cache stromu `origin/main` jako **modulovou
proměnnou bez expirace** a do komentáře napsal, že *„mezipaměť drží výsledek
na dobu jednoho tiku"*. **To nebyla pravda:** modulová proměnná žije tak
dlouho jako **izolát** Cloudflare, a ten se recykluje **tehdy, kdy chce on** —
ne kdy končí tik. V teplém izolátu by cache sloužila **libovolně dlouho**.

**Důsledek, kdyby to zůstalo:** po sloučení PR by conductor **ještě dlouho
tvrdil, že soubor v `main` není** — tedy tatáž vada, kterou A2 opravuje
(stav, který si systém hlásí sám, se rozešel s realitou), jen obráceně.

**Jak se to našlo:** **druhým pohledem na vlastní diff**, ne testem. Test to
nechytil, protože **tuhle vlastnost neměřil** — a to je poučení:
*vlastní kód potřebuje stejně tvrdý pohled jako cizí.* Komentář, který tvrdí
„na dobu jednoho tiku", je **tvrzení o chování**, a to se ověřuje.

**Opraveno v této session:** cache má **TTL 10 minut**; při neúspěchu se
needspiruje na plnou dobu (zkusí se za minutu).
**Doplněno do testu:** `_analyza\a1-a2-over.py` má teď **19 kontrol**
(bylo 16) — dvě na TTL a **čítač kontrol se počítá, neopisuje** (dřív ručně
`6 + len(...)`; ručně psané číslo zestárne při první změně).
**Mutační test:** odstranění `expiruje > ted` → **`exit 1`**.

---

## N8 — ANALÝZA SE ROZEŠLA S KÓDEM (nejdůležitější nález sjednocení)

**Třída:** **tatáž vada, o které analýza je** — jen namířená na dokument.
Tohle je „stav, který si systém hlásí sám", v nejčistší podobě.

**Co se naměřilo** (`_analyza\n8-zastarala-analyza.py`, 2. 10. 2026):

`ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` vznikla **05:45 UTC** a popisuje stav kódu
**v tom čase**. V **08:38–08:52** téhož dne jsem provedl **A1–A4** a kód
změnil. **5 tvrzení analýzy tím přestalo platit:**

| Tvrzení analýzy (05:45) | Stav po A1–A4 (08:52) |
|---|---|
| §3.1/⑪ `tasks.status='done'` **není ukotveno** | **je** — `ok && merged` |
| §3.2 `auto-merge` **skončí zeleně** | **`exit 1`** |
| §⑪/2 `roadmap.status` se **neověřuje** | **ověřuje se** proti `origin/main` |
| §⑪/15 „PR sloučen" z `conclusion` | z `merged_at` + `awaiting_human` |
| §3.2 lint o `size_lines` **nehlásí** | **hlásí** |

**Dvě tvrzení platí dál** (`done_note` mrtvé, `runs.artifacts` mrtvý) — jsou
v kontrole **schválně jako kontrolní vzorky**, aby se poznalo, že nástroj
neměří pořád totéž.

**Proč je to nález, a ne kosmetika:** analýza je **výchozí bod pro každou
další session** (`HANDOFF.md` §8.5). Kdo ji otevře a přečte si
„`tasks.status` není ukotveno", **naplánuje práci, která je hotová** — nebo
ještě hůř, **bude tvrdit, že oprava nefunguje**. Je to přesně past
*„dokument z minulosti"* z `hlouchkova-analyza` §4.

**Má být (návrh):**
1. **Každý analytický dokument má v hlavičce DATUM SPOTŘEBY**, ne jen datum
   vzniku — a co z něj bylo provedeno. *(Provedeno v této session u
   `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` a `ANALYZA-HLOUBKOVA-2-ZADANI.md`.)*
2. **Nástroj `n8-zastarala-analyza.py` je protějšek** — porovnává tvrzení
   analýzy s **kódem**, ne s dokumentem. Dá se rozšiřovat: přidáním dvojice
   `(popis, test na kód)` roste pokrytí.
3. **Obecné pravidlo do `AGENTS.md`:** *„Analýza, která byla provedena, musí
   to říct ve své hlavičce — jinak se za měsíc čte jako popis dneška."*

**Vlastní omyl v tom nálezu (a je poučný):** první verze skriptu měla
podmínku **obráceně** a hlásila „**0 zastaralých**" u kódu, který jsem **sám
změnil**. Odhalilo se to jen tím, že jsem **znal správný výsledek** — což je
přesně ten „známý chybný případ", který `AGENTS.md` u metrik vyžaduje.
**Bez něj bych měl zelenou od nástroje, který měří opak.**

---

## N9 — `AGENTS.md` tvrdil o schématu D1 číslo, které neplatí (a nikdo si toho nevšiml)

**Třída:** `AGENTS.md` *„Ke každému číslu patří postup, kterým vzniklo"* —
porušeno v pravidlech samotných.

**Co se naměřilo** (2. 10. 2026, při sjednocování zdrojů):

| Kde | Co tvrdí | Skutečnost |
|---|---|---|
| `AGENTS.md` § Jazyk | `conductor/schema.sql` → **„5 tabulek, 32 sloupců"** | **5 tabulek, 39 sloupců** |
| `ANALYZA-HLOUBKOVA-ORCHESTRA-2.md` §3.1 | **„Pět tabulek D1, 39 sloupců"** | **39** ✅ |

**Ověřeno:** `git log -- conductor/schema.sql` → poslední změna **30. 9. 2026**,
tedy **před** měřením v `AGENTS.md` (1. 10.). **Schéma se nezměnilo** — číslo
bylo chybné **už při zápisu**, ne zestaralo.

**Proč je to nález, a ne detail:** `AGENTS.md` je **trvalá autorita**, ze které
vycházejí všechny session. Kdo z něj počítá pokrytí schématu (a přesně to dělá
jazykový inventář), **počítá se špatným základem 32 místo 39** a jeho procenta
jsou mimo. **Chyba v autoritě se neprojeví jako chyba** — projeví se jako
důsledek na pěti jiných místech.

**Opraveno v této session** (`32` → `39`), s odůvodněním v `AGENTS.md`.

**Obecné poučení:** i **trvalá pravidla** mají čísla, která je potřeba
**periodicky remeřit**. `AGENTS.md` tvrdí, že je „ověřen měřením 1. 10. 2026" —
ale **jedno z těch čísel bylo špatné od začátku** a přes šest session si toho
nikdo nevšiml, protože se **nečetlo proti zdroji**.

---

## Co je hotové (aby se nehledalo znovu)

| Co | Stav | Doklad |
|---|---|---|
| **A1** `done` jen při `ok && merged` | **hotovo** | `_analyza\a1-a2-over.py` **19 kontrol**, 3 mutace chyceny |
| **A2** ověření `owns` proti `origin/main` | **hotovo** | tamtéž (`null` ≠ prázdný strom, cache s TTL) |
| **A3** `exit 1` v obou `agent.yml` | **hotovo** | `_analyza\a3-over.py`, **6×** `exit 1` v obou (bylo 5×) |
| **A4** `size_lines` + text `[5]` | **hotovo** | `lint-roadmapa.py` hlásí **13 z 18**, `exit 0` |
| **Z1–Z8** hranice jazyka | **hotovo** | `hl-rizika-jazyka.py` → **0 očekávaných, 11 přejednaných, 0 vrácených** |
| Obě kopie `check-schema.py`, `vision.mjs` | **shodné hashe** | `531AE859…`, `FE639998…` |
| Testy hry | **38 kontrol, 0 selhání** | Godot `run_tests.gd` |

**Brány po změnách (vše `exit 0`, 2. 10. 2026):** skener **23/23**,
`hl-rizika-jazyka`, `kontrola-diakritiky`, `over-dokumentaci` (**63/0**),
`over-skilly` (**12/0**), `test-eskalace`, `lint-roadmapa`,
`check-schema` (obě kopie), `tsc --noEmit`.
**`kontrola-driftu.mjs` = 1 rozdíl** — **známý** (tři kroky, které šablona
má a hra ne), **nezávislý na A3**; to je přesně to, co zadání A3 předpovídalo.

---

## Co NEDĚLAT (a proč)

1. **Nepřejmenovávat podle starého inventáře.** Kdo uvidí `CHYBÍ: ohlášeno`
   a přejmenuje to znovu, **nic neopraví** — vada je v měřidle (N1).
   **Nejdřív přegenerovat inventář, pak se ptát.**
2. **Nedělat z `hl-rizika-jazyka.py` bránu v CI**, dokud neumí říct stáří
   svého vstupu (N1/N2). Brána, která měří starý snapshot, je **horší než
   žádná** — hlásí vady, které nejsou, a tím se přestane číst.
3. **Nesahat na `agent.yml` v jedné kopii.** Dvě kopie, drift test.
4. **Nepřidávat `awaiting_human` do `roadmap.json`** (analýza §⑨) — patří
   jen do D1.
5. **Nepushovat ani necommitovat bez vyžádání.**
6. **Nedělat z N4 „plný diff" bez řešení známého rozdílu** — vznikla by
   brána, která svítí vždycky.

---

## Hotovo znamená

- [ ] **N1:** nástroj řekne **čas vzniku** inventáře a **spadne/varuje**,
      když je starší než kód. Mutační test: starý inventář → nenulový kód.
- [ ] **N2:** v `IMPLEMENTACE-HRANICE-JAZYKA.md` §5 je zapsáno, že kontrola
      rizik potřebuje **čerstvý inventář** (nebo to nástroj vynutí sám).
- [ ] **N3:** kontrola ověří **obě kopie** `agent.yml` a že `FORGE_ATTEMPT`
      je v **jednom** kroku a že je to krok spouštějící agenta.
- [ ] **N4:** rozhodnuto — buď drift porovnává i `env`, **nebo** je
      v dokumentaci, že hlídá **jen strukturu kroků**.
- [x] **N5:** komentář `index.ts:372-374` neodporuje kódu. — **hotovo 2. 10.**
- [ ] **N6:** u čísel v `IMPLEMENTACE-UKOTVENI-STAVU-ZADANI.md` je **čas
      měření** (nepřepisovat hodnoty).
- [x] **N7:** cache `origin/main` má **TTL**. — **hotovo 2. 10.** (test 19 kontrol)
- [ ] **N8:** každý provedený analytický dokument má v hlavičce **datum
      spotřeby** a co z něj bylo provedeno; `n8-zastarala-analyza.py` se
      rozšiřuje o další dvojice (tvrzení → test na kód).
- [ ] U **každé** změny: **dvě negativní kontroly** — s vrácenou vadou to
      spadne; a ověřeno, že brána soubor **vůbec otevřela** (past S27).

## Otevřené otázky, které musí rozhodnout člověk

- **N1:** má nástroj při starém inventáři **spadnout**, nebo si ho **sám
  přegenerovat**? (Přegenerování je pohodlnější, ale schová to, že měření
  je drahé — a náklad je součást rozhodnutí.)
- **N4:** stačí driftu **struktura kroků**, nebo má umět i obsah? (Plný
  obsahový diff je dnes **červený natrvalo** kvůli známému rozdílu.)
- **N8:** má se **datum spotřeby** vynutit branou (např. každý `ANALYZA-*.md`
  musí mít v hlavičce „co z něj bylo provedeno"), nebo stačí pravidlo
  v `AGENTS.md`? Brána by byla spolehlivější, ale je to další ruční seznam —
  a těch už má projekt **pět** (S27).

## ✅ Krok 1 zadání — OPRAVA: byl splněn, jen jsem ho neověřil

**Původně jsem sem napsal, že „prompt k poslední hluboké kontrole nebyl
dodán". To byla nepravda.** Prompt je `ANALYZA-HLOUBKOVA-2-ZADANI.md`, ležel
v repu, a **je splněný** — `_analyza\hl2-kontrola.py` → **9/9 bodů**.

**Co z toho plyne pro tenhle plán:** N1–N8 **jsou** z vlastní práce, ne
z nezávislého pohledu — ale z **jiného důvodu, než jsem napsal**: ne že by
zadání chybělo, nýbrž že **hloubková kontrola byla hotová dřív, než jsem
začal**, a **já ji neotevřel**. Kdo bude pokračovat, ať si tuhle mez přečte
takhle — je to **chyba provedení, ne chybějící zadání**.

# ANALÝZA — padá orchestra na FREE klíčích? Ověřeno měřením (19. 10. 2026)

> **Co tenhle dokument JE:** **záznam o měření** — odpověď na otázku uživatele
> „orchestra aktuálně nefunguje; je to kvůli FREE api klíčům?“, zadanou
> `E:\Workspaces\dsh-dev\_sprava\ZADANI-ORCHESTRA-FREE-KLICE-2026-10-19.md`.
> **Co NENÍ:** stav projektu (ten je v `HANDOFF.md`, nejnovější oddíl **§77**)
> ani návrh k provedení — §6 je **návrh**, který čeká na uživatele.
> **Datum měření:** 19. 10. 2026, 12:30–15:10 UTC (off-peak).
> **Co z něj bylo PROVEDENO:** v konfiguraci orchestra ani hry **nic** (zákaz
> zadání); měřilo se čtením cizího repa a v **odpojených git worktree**, které
> byly po měření odstraněny. Hlavní klon hry zůstal nedotčen (`c72b309`, čistý).
> **Odkud brát současný stav:** `HANDOFF.md` §77; historie `KRONIKA-PROJEKTU.md`.
> **Doklady:** `_analyza\k11b-free-klice-vystup.txt` (10 běhů z logů),
> `_analyza\k11b-deepseek-vystup.txt` (3 běhy na DeepSeek),
> `_analyza\k11b-patch-*.txt` (3 patche). **První dva jsou `*.txt` se
> `vystup` v názvu → jsou záměrně gitignorované** (konvence projektu pro
> naměřené výstupy, stejně jako `p29-*`/`p36-*-vystup.txt`); leží na disku,
> v gitu nejsou. Patche commitnuté jsou.

---

## 1. Odpověď v pěti řádcích (A1–A5)

- **A1 (Q1) — ANO, měřením doloženo:** prompt jedné granule má
  **31 462–33 803 tokenů** (tokencounteru Groqu) a model, který ho dostal,
  `openai/gpt-oss-120b` na free tieru, má strop **8 000 TPM** → požadavek je
  **3,9–4,2× nad stropem**. Živě přeměřeno dnes: hlavička Groq API
  `x-ratelimit-limit-tokens: 8000`.
- **A2 (Q2) — ANO, je to propustnost poskytovatele, a retry to nespraví:**
  chyba padá na **prvním** požadavku běhu (ne „po N požadavcích“); opakování
  proběhlo **9×** (u Groqu během 65 s s backoffem 0,2→32 s, u Cerebrasu během
  ~17 min, protože jeden pokus visí ~2 min), **vždy bez úspěchu** — požadavek
  se opakováním neztenčí. **Retry/backoff v orchestra kódu na úrovni požadavku
  NENÍ** (workflow po `RateLimitError` druhého poskytovatele **záměrně
  přeskočí**); backoff dělá jen knihovna litellm. Na úrovni granulí retry
  existuje (cooldown 0,5 h, 5 pokusů, strop 8 běhů) — ale posílá tentýž
  předlouhý prompt.
- **A3 (Q3) — NE, samotné velké kontextové okno to nespraví:** stejná granule
  (`entity.move.smooth`) na **DeepSeek flash i v4-pro (1M kontext, placené)**
  prošla sítem velikosti (33k tokenů přijato, žádný rate limit), patch se
  aplikoval a **parsuje**, ale **testy hry hlásí 2 selhání u obou modelů**
  (baseline na čistém HEAD: **113/0**). Příčina není poskytovatel — je
  v **kontradikci zadání granule a testů** (§4).
- **A4 (Q4) — neparsovatelný `scripts/game.gd` zapsal `codestral-latest`
  (mistral) v běhu #398;** ale příčina je **vadné tvrzení v zadání**, ne kvalita
  modelu: zadání i `CONVENTIONS.md` §1g tvrdí „soubor začíná `extends Node`“,
  skutečný soubor začíná **`extends Node2D`**; model poslechl a přepsal
  `Node2D`→`Node`, čímž rozbil 5 volání `get_viewport_rect()`.
  **U silnějšího modelu se to NEOPAKOVALO** (DeepSeek v4-pro na téže granulí
  `extends Node2D` zachoval → 0 parse errorů).
- **A5 (stav dnes, mimo zadání):** od **16. 10. 17:43** nevznikl **žádný** nový
  běh Forge (3 dny), i když conductor tiká (`last_cron` < 1 min, `/health`
  `ok=true`) a ve frontě jsou **3 připravené úlohy**. U granule
  `entity.move.smooth` je to **zamýšlený strop** (`GRAIN_MAX_RUNS=8`: 5 běhů
  tasku #272 + 3 běhy tasku #273 = 8/8). **Proč se nevydaly #270/#271,
  NEMĚŘENO** — změřit by to šlo jen plným `POST /tick`, který by dispatchoval
  běhy do **cizího repa**; to bez domluvy nedělám.

---

## 2. A1 — velikost promptu vs. strop poskytovatele

### 2.1 Co bylo v bězích #397–#406 (z logů GitHub Actions, stažené a rozebrané)

| běh | pokus | granule | model, který požadavek dostal | co se stalo (z logu) |
|---|---|---|---|---|
| #397 | 2 | shell.save | mistral/codestral → cerebras/gpt-oss-120b | codestral: 36k/38k tokenů **přijato**, edit „nochange“; cerebras **TPM 9×** |
| #398 | 3 | shell.nocoins | mistral/codestral-latest | 20k/1,7k tokenů, **Applied edit game.gd** → **parse gate 5 chyb** |
| #399 | 2 | entity.move.smooth | cerebras/gpt-oss-120b | **TPM 9×** (13:11:39–13:28:47) |
| #400 | 3 | shell.save | cerebras/gpt-oss-120b | **TPM 9×** (13:51:32–14:08:41) |
| #401 | 3 | entity.move.smooth | groq/openai/gpt-oss-120b | **Request too large 9×**, Limit **8000**, Requested **31 462–31 784** |
| #402 | 4 | entity.move.smooth | mistral/codestral → cerebras | codestral 33k **přijato**, nochange; cerebras **TPM 9×** |
| #403 | 5 | entity.move.smooth | mistral/codestral → cerebras | codestral 33k **přijato**, nochange; cerebras **TPM 9×** |
| #404 | 1 | entity.move.smooth (task #273) | groq/gpt-oss-120b | **Request too large 9×**, Requested **31 759–33 803** |
| #405 | 2 | entity.move.smooth | mistral/codestral → cerebras | codestral 33k **přijato**, nochange; cerebras **TPM 9×** |
| #406 | 3 | entity.move.smooth | groq/gpt-oss-120b | **Request too large 9×**, Requested **31 462–31 820** |

**Součet za 10 běhů:** 3× `Request too large`, 6× `Tokens per minute`,
1× neparsovatelný zápis — tj. **přesně to, co už bylo doložené v zadání**
(3 / 6–8 / 1). Tohle měření to jen rozmnožilo o přesná čísla.

### 2.2 Stropy poskytovatelů — měřené dnes, ne odhad

| poskytovatel | co říká API (19. 10. 2026) | zdroj |
|---|---|---|
| **groq** free, `openai/gpt-oss-120b` | `x-ratelimit-limit-tokens: 8000` (TPM), `limit-requests: 1000` | hlavičky reálné odpovědi API |
| **mistral**, `codestral-latest` | `max_context_length=256 000`, `x-ratelimit-limit-tokens-minute: 625 000`, 125 req/min | `/v1/models` + hlavičky |
| **cerebras**, `gpt-oss-120b` | dnes **HTTP 402** („payment required“) — trial kredit vyčerpán; v bězích 16. 10. vracel `Tokens per minute limit exceeded` **bez čísla** | přímý dotaz API |
| **deepseek** (placený, pro Q3) | kontext **1M**; cena off-peak vstup 0,15 USD/1M (cache miss), výstup 0,6 USD/1M | api-docs.deepseek.com/quick_start/pricing |

**Závěr A1:** `31 784 > 8 000` → **požadavek je 4× nad stropem**, ne jen blízko.
Mistral codestral (625k TPM) přitom **tentýž 32–38k tokenový požadavek
přijímal** (měřeno v #397/#402/#403/#405 i v mých bězích).

### 2.3 Z čeho se těch 32 000 tokenů bere (měřeno tiktokenem + mechanismus v aideru)

`aider --message` prochází **každý** vstup funkcí `check_for_file_mentions`
(`aider/coders/base_coder.py:919` ← `preproc_user_input`). Když zadání granule
zmíní **cestu k souboru** („podle `docs/GDD.md` §6“), aider si soubor **sám
přidá do chatu** (s `--yes` bez potvrzení) a pošle ho celý. To je pozorované
v každém logu jako řádek `docs/GDD.md` / `docs/TDD.md`.

| část promptu (granule `entity.move.smooth`) | tokenů (cl100k) |
|---|---|
| **`docs/GDD.md` (aider si ho přidal sám)** | **19 142** |
| `CONVENTIONS.md` (--read) | 5 305 |
| `scripts/level.gd` (--read) | 3 628 |
| `scripts/player.gd` (--file) | 2 486 |
| `scripts/registry.gd` (--read) | 1 951 |
| `scripts/input.gd` (--read) | 240 |
| zadání granule (prompt) | 324 |
| **součet** | **33 076** ≈ naměřeno 31 757 (Groq) / 33 000 (DeepSeek) |

→ **60 % promptu je dokumentace, kterou si aider přidal sám** proto, že ji
zadání jmenovalo cestou. U `shell.save`/`shell.nocoins` je to stejné s
`docs/TDD.md`.

**Druhá slepá místo, které to maskovalo:** `pick-provider.mjs` zkouší
poskytovatele dotazem `{"messages":[{"role":"user","content":"ping"}],
max_tokens:8}` (`pick-provider.mjs:152-156`) — **malý ping projde vždy**, i
když skutečný 32k požadavek spadne. Proto „Vybráno: cerebras → gpt-oss-120b“
a hned poté `Tokens per minute exceeded`. A proto je i denní „Kontrola modelů“
zelená: `model-check.yml` pouští `providers-check.mjs --no-ping` (dnešní běh:
„0 poskytovatelů OK, 1 mrtvých signálů“, přesto `success`).

---

## 3. A2 — je `Tokens per minute` propustnostní limit, a existuje retry?

### 3.1 Co říkají časová razítka (z logů, nikoli z názvů kroků)

| běh / model | časy selhání | rozestup | výklad |
|---|---|---|---|
| #401 groq | 14:00:24 → 14:01:29, **9×** | 0,2–32 s (exponenciální backoff) | první požadavek, rychlé selhání, 65 s marných pokusů |
| #399/#400/#402/#403/#405 cerebras | 9× během **~16–17 min** | ~120–125 s | každý pokus visí ~2 min (timeout), pak chyba; opakování po 2 min **nepomohlo** → požadavek se do minutového okna nevejde |

**Není to „po N požadavcích v krátkém okně“** — padá to na **prvním**
požadavku běhu. Je to limit velikosti/objemu na straně poskytovatele
(propustnost), ne vada aplikace: v logu není žádná chyba orchestra, jen
`litellm.RateLimitError` z API.

### 3.2 Kde retry/backoff v kódu je a kde není (měřeno čtením kódu)

| vrstva | retry/backoff | doklad |
|---|---|---|
| **workflow `agent.yml`** | **NE** — po `RateLimitError` se druhý poskytovatel **záměrně nezkouší** (šetří kvótu) | `agent.yml:253-255` („první pokus spadl na vyčerpané kvótě – druhý poskytovatel se nezkouší“) |
| **aider/litellm (knihovna)** | **ANO** — 8 pokusů, 0,2 / 0,5 / 1 / 2 / 4 / 8 / 16 / 32 s | všech 9 rate-limitových běhů: `Retrying in … seconds` |
| **conductor (scheduler)** | **ANO, ale na úrovni granulí** — `RETRY_HOURS=0.5` (30 min), `MAX_ATTEMPTS=5`, `GRAIN_MAX_RUNS=8`; opakování založí nový task | `conductor/wrangler.toml`; běhy #272 (5 pokusů) → task #273 (3 pokusy) |
| **klasifikace kvóty** | **NEFUNGUJE** — conductor má od K5 rychlou větev pro kvótu (`/QUOTA/i.test(summary)` → vrátí pokus a pošle za 10 min), ale `report.mjs` posílá pořád jen `"Testy po zasahu agenta selhaly"`; slovo QUOTA tam nikdy není | `conductor/src/index.ts:2201`, `uo-shadows/.forge/report.mjs:490` |

**Důsledek:** každé rate-limitové selhání se počítá jako **kvalitativní**
selhání → spálí pokus a po 5 pokusech granuli zablokuje. Což je přesně stav
`entity.move.smooth` (8/8 běhů, strop).

---

## 4. A3 — stejná granule na modelu s velkým kontextem

Běhy na **placeném DeepSeek** (OpenAI-kompatibilní endpoint, kontext **1M**),
na odpojeném worktree hry, **stejnými nástroji a argumenty jako `agent.yml`**:

| run | granule | model | tokeny (aider) | patch | parse | testy | cena off-peak |
|---|---|---|---|---|---|---|---|
| A | entity.move.smooth | deepseek-flash | **33k in / 33k out** (thinking) | +244/−22 | 0 chyb | **113 / 2 FAIL** | 0,025 USD |
| B | entity.move.smooth | deepseek-v4-pro | 33k in / 15k out | +67/−13 | 0 chyb | **113 / 2 FAIL** | 0,052 USD |
| C | shell.nocoins | deepseek-v4-pro | 21k in / 14k out | +4/−46 | 0 chyb | **112 / 2 FAIL** | 0,042 USD |
| — | baseline HEAD c72b309 | — | — | — | — | **113 / 0** | 0 |

**Odpověď A3 = NE, ale NE kvůli poskytovateli.** Velký kontext odstranil
rate-limit (33k tokenů prošlo), patch se aplikoval i parsuje — a přesto běh
neprojde, protože **zadání granule je v rozporu s testy hry**:

1. **entity.move.smooth:** `tests/run_tests.gd:1009` volá `player.move(smer)`
   s **jedním** argumentem a `:1013-1024` chce posun přesně `SPEED/60`;
   `:1032` chce v textu **doslova** `move(dir, delta)`. Zadání granule ale chce
   **vyhlazení** (první krok je menší než plný) a parametr jmenuje `smer`.
   Kdo splní zadání, poškodí test; kdo splní test, nesplní zadání.
   Oba DeepSeek modely selhaly na **týchž dvou** kontrolách — systematicky,
   ne náhodou.
2. **shell.nocoins:** `tests/run_tests.gd:79-95` chce **5 mincí** a HUD s „0“;
   zadání chce mince i skóre **odstranit** a HUD „—“/registr. A agent navíc
   **nesmí editovat `tests/`** (`CONVENTIONS.md` §5). Granule je neřešitelná
   jakýmkoli modelem.

**Důsledek pro otázku uživatele:** i kdyby zítra free klíče zázračně zmizely,
**tyhle granule nesplní žádný model** — dokud se nespraví zadání nebo testy.
To je druhá, nezávislá příčina „orchestra nefunguje“.

---

## 5. A4 — kdo zapsal neparsovatelný `scripts/game.gd`

- **Zapsal ho `codestral-latest` (mistral) v běhu #398** (task #270,
  `shell.nocoins`): log `Applied edit to scripts/game.gd`, pak parse gate:
  5× `SCRIPT ERROR: Parse Error: Function "get_viewport_rect()" not found in
  base self.` — **změna `extends Node2D` → `extends Node`** (log #398,
  SEARCH/REPLACE na řádcích 734/761).
- **Proč to model udělal:** zadání granule obsahuje tvrzení
  *„Soubor začíná `extends Node` — zachovej to.“* — **to je nepravda**;
  `scripts/game.gd:1` je `extends Node2D`. Stejné tvrzení má i
  `CONVENTIONS.md` §1g („soubor granule musí začít `extends Node`“).
  Model poslechl **zadání**, ne realitu souboru.
- **U silnějšího modelu se to NEOPAKOVALO:** DeepSeek v4-pro na **téže
  granulí** `extends Node2D` zachoval → **0 parse errorů** (run C výše).
  (Běh C ale stejně skončil na testech — viz §4.2.)

---

## 6. Co by se změnilo v konfiguraci (návrh s cenou, NEPROVEDENO)

> Návrh je připravený k rozhodnutí uživateli; **nic z toho jsem neprovedl**
> (zadání zakazuje měnit `providers.json`, workflowy i secrety bez uživatele).
> Ceny jsou z ceníku DeepSeek 19. 10. 2026 (off-peak = polovina špičky),
> spotřeba z mých tří měřených běhů.

| # | změna | kde | efekt (měřený) | cena |
|---|---|---|---|---|
| 1 | **Nedávat cesty k dokumentaci do zadání granule** (nebo je v `agent.yml` před předáním aideru odstranit) — aider si je jinak sám přidá celé | zadání granulí (roadmapa hry) / `agent.yml` | **−19 142 t z ~32 000 t** (60 % promptu); 32k → ~13k | **0 USD** |
| 2 | **Opravit tvrzení „extends Node“** v `CONVENTIONS.md` §1g a v zadáních: soubor může být `Node2D`; „zachovej existující `extends`“ | hra: `CONVENTIONS.md`, zadání granulí | odstraní třídu chyb „model poslechne nepravdu“ (#398) | **0 USD** |
| 3 | **Srovnat zadání granulí s testy** (shell.nocoins: buď upravit testy, nebo zrušit granuli; entity.move.smooth: doplnit do zadání smlouvu, kterou testy vyžadují) | session HRY (rozhodnutí uživatele; agent nesmí editovat `tests/`) | jinak **žádný model** granuli nesplní (měřeno: 2× DeepSeek, 2 selhání) | **0 USD** (práce, ne peníze) |
| 4 | **Vyřadit groq z strong řetězce pro agenta** (8 000 TPM < 20–33k, které aider reálně posílá; nemůže to nikdy projít) a případně i z `any` | orchestra `repo/.forge/providers.json` (+ synchronizace do her) | ukončí 3/10 běhů, které spadly na `Request too large`; ušetří kvótu | **0 USD** |
| 5 | **Guard na velikost požadavku v `pick-provider`**: probe posílat s realistickým stropem (`max_tokens` + odhad `wc -c` souborů / 3,5), nebo providera označit `maxRequestTokens` a přeskočit ho, když je odhad větší | `.forge/pick-provider.mjs` | provider se vybere podle **kapacity**, ne podle pingu; dnes ping projde a skutečný požadavek spadne | **0 USD** (malá změna kódu) |
| 6 | **Opravit klasifikaci kvóty**: `report.mjs` posílat `TRIDA=QUOTA` (nebo workflow posílat jinou summary), aby se využila K5 větev „vrátit pokus + 10 min“ | `report.mjs` + `agent.yml` | rate-limitové běhy **nespálí 5 pokusů** jako kvalitativní selhání | **0 USD** |
| 7 | **Kontrola modelů má pingovat** (dnes `--no-ping`, zelená i když skutečný požadavek neprojde) | `.github/workflows/model-check.yml` | denní kontrola začne odhalovat mrtvé free modely dřív než agent | **0 USD** |
| 8 | **Placený model pro krok agenta: DeepSeek** (stačí přidat providera + `DEEPSEEK_API_KEY` do Secrets; `pick-provider` už umí `baseUrl`/`keyEnv`) | orchestra `repo/.forge/providers.json`, `agent.yml` env, Secrets | **odstraní A1 i A2** (1M kontext, žádný 8k strop) | **měřeno: 2,5 ¢ / pokus** (flash, thinking zapnutý, off-peak; 5 ¢ ve špičce) · **s kroky 1–2 a thinking vypnutým ~0,5–1 ¢/pokus** · při dnešním tempu (16. 10.: 12 běhů/6 h) **15–25 USD/měsíc**; po opravě granulí a promptu **3–5 USD/měsíc** |
| 9 | Alternativa k 8: nechat **jen mistral/codestral** (625k TPM zdarma) a spravit zadání | providers.json + zadání | A1/A2 zmizí i zdarma — ale kvalita codestralu je měřená jako slabší (poslechl vadné zadání, „nochange“) | **0 USD**, riziko kvality |

**Doporučení:** body **1–2** a **4–7** udělat bez ohledu na placení (jsou
zdarma a řeší měřené příčiny), **3** předat session HRY, a **8** zapnout
s rozpočtem ~1 USD/den jako pojistku — po opravách bude stát jednotky dolarů
měsíčně. Body 8–9 jsou **rozhodnutí o penězích a cizích službách** → patří
uživateli.

---

## 7. Co NEBYLO naměřeno (a proč)

- **Číslo TPM limitu Cerebras** — dnes API vrací **402** (kredit vyčerpán),
  v bězích 16. 10. chybová zpráva číslo neobsahovala. NEMĚŘENO.
- **Proč se od 16. 10. 17:43 nevydaly úlohy #270 (`shell.nocoins`) a
  #271 (`shell.save`)**, i když jsou `ready` a jejich granule nejsou na
  stropu (3/8 běhů). Conductor tiká a `last_cron` je čerstvý; statická
  analýza dispatch smyčky (`conductor/src/index.ts:1459-1608`) nenašla
  podmínku, která by je vylučovala. Změřit by to šlo jen plným
  `POST /tick`, který by **dispatchoval běhy do cizího repa** → bez domluvy
  jsem to neudělal. **NEMĚŘENO** (a ne „nefunguje to“).
- **„U silnějšího modelu se to neopakuje“** je doloženo jen pro parse chybu
  (§5) na **jednom** běhu; testy u obou modelů padají stejně, takže
  „silnější model“ v kvalitě testů **rozdíl neudělal**.
- **Cena modelu pro 30 granul/den** není měřená, je to přepočet z měřené
  spotřeby jednoho běhu (uvedeno v §6).

## 8. Ponaučení

1. **Free tier není jen „pomalý“ — má strop na VELIKOST.** 8 000 TPM u Groqu
   je tvrdý strop na jeden požadavek; aider posílá 20–33k. Rate-limitové
   chyby proto nejsou náhodné a retry je nespraví (matematika, ne časování).
2. **Zadání granule je taky konfigurace.** Zmínka `docs/GDD.md` v textu
   přidala 60 % promptu (aider auto-add); tvrzení „extends Node“ rozbila
   parsování. Dvě z pěti měřených příčin jsou **v textu zadání**, ne v kódu.
3. **„Prošlo“ a „neměřilo se“ nejsou totéž.** Deník „Kontrola modelů“ je
   zelený každý den, ale neposílá ani jeden skutečný požadavek (`--no-ping`);
   zeleň bez měření je falešný signál.
4. **Nejdřív se ptát, jestli úloha jde splnit, potom jaký model ji má dělat.**
   Dvě granule jsou v rozporu s testy, které agent nesmí měnit — tam nepomůže
   ani placený model s 1M kontextem.

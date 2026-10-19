# NÁVRH — orchestra: co změnit v konfiguraci (free klíče + placený DeepSeek)

> **Co tenhle dokument JE:** **návrh k rozhodnutí** (ne stav, ne záznam), vznikl
> 19. 10. 2026 v session K11b na zadání
> `dsh-dev\_sprava\ZADANI-ORCHESTRA-FREE-KLICE-2026-10-19.md`.
> **Co NENÍ:** provedení. **Co už provedeno JE:** jen položka 1 níž (DeepSeek
> poskytovatel v **šabloně** `repo/`; nic se nenasadilo, secret neexistuje,
> do hry se nepsalo).
> **Měření, ze kterého to vychází:** `ANALYZA-FREE-KLICE-2026-10-19.md`.
> **Odkud brát stav:** `HANDOFF.md` §77.

---

## 0. Nejdřív to hlavní: opravy A1/A2 UŽ EXISTUJÍ — jen nejsou ve hře

Změřená příčina selhání #397–#406 (prompt 32k > strop 8k, TPM, pálení pokusů)
**je v orchestra vyřešená v šabloně `repo/`** (sessions K1–K5, P42) — ale
`uo-shadows` běží **starý workflow** bez toho:

| soubor v šabloně `repo/` | co dělá | je ve hře? |
|---|---|---|
| `.forge/node/prompt-hygiene.mjs` | nahradí cesty k souborům v zadání (`docs/GDD.md` → `[dokument]`), aby si aider nepřidal celý dokument; naměřeno 22 025 → 14 097 t | **NE** |
| `.forge/node/request-budget.mjs` | spočítá request PŘED voláním a porovná s **naměřeným** stropem poskytovatele; když se nevejde, **zkusí dalšího poskytovatele** (P42) | **NE** |
| `.forge/node/classify-agent-log.mjs` | rozliší `REQUEST_TOO_LARGE` / `QUOTA` / `AUTH` / `NOCHANGE`; rozhoduje o fallbacku (starý kód měl jen `grep RateLimitError`) | **NE** |
| `.forge/node/probe-provider.mjs` | měří skutečné stropy z hlaviček API (`x-ratelimit-*`) | **NE** |
| `.forge/node/rozpocet-granuli.mjs` | rozpočet/plánování granulí | **NE** |
| `repo/.forge/node/{priprava,probe-provider}.test.mjs` | testy nástrojů (v šabloně **55/55** a **14/14**) | **NE** |
| `repo/.forge/providers.json` → blok `limits` | naměřené stropy: mistral 625 000, cerebras 30 000, groq 8 000 TPM (12.–13. 10.) | **NE** (hra má starý soubor bez `limits`) |
| `repo/.github/workflows/agent.yml` | navíc 4 kroky (parse gate, class_name, import, **report s pojmenovanou příčinou**) + hygiena + rozpočet + timeout 300 s | **NE** (hra má starý) |

**Důsledek:** dokud se tohle nesynchronizuje do hry, běhy budou padat přesně
jako #397–#406 — a je jedno, kolik se zaplatí za klíče. **Sync do hry je
záležitost session HRY** (orchestra do hry nepíše); podklad:
`PREDANI-HRE-SYNC-A-OPRAVY-2026-10-19.md`.

## 1. PROVEDENO (jen v šabloně `repo/`, k odsouhlasení)

Placený model jako **volitelný** článek řetězce — bez klíče se chová jako dřív:

- `repo/.forge/providers.json`: nový poskytovatel **`deepseek`**
  (`https://api.deepseek.com/v1`, `models`/`strongModels` =
  `deepseek-flash`, `deepseek-v4-pro`, `anyPriority: 95` = pro `any` až na
  konci, ať se neplatí, když free zdroj stačí; `limits` jen s naměřeným
  poznámkovým blokem, **bez `tpm`** — TPM nezměřeno, request-budget tedy jen
  varuje).
- `repo/.github/workflows/agent.yml`: `DEEPSEEK_API_KEY: ${{ secrets.DEEPSEEK_API_KEY || vars.DEEPSEEK_API_KEY }}`
  na obou místech, kde jsou klíče poskytovatelů.

**Ověřeno:** `provider-choice.test.mjs` 21/0 · `probe-provider.test.mjs` 14/14 ·
`priprava.test.mjs` 55/55 · `request-budget` s 45 kB souborem: groq odmítne
(`REQUEST_TOO_LARGE`, exit 1), mistral projde (`REQUEST_FITS`, exit 0) ·
`providers.json` je platný JSON. **Co NENÍ ověřeno:** chování v CI (workflow
se v šabloně nespouští) — proto zůstává „k odsouhlasení“, ne nasazené.

## 2. Cena — měřená, ne odhad

Měřeno 19. 10. 2026 off-peak (ceník api-docs.deepseek.com), ceny za 1M tokenů:

| model | vstup miss/hit | výstup | měřený pokus (in/out) | cena/pokus |
|---|---|---|---|---|
| `deepseek-flash` | 0,15 / 0,003 USD | 0,60 USD | 33k / 33k (thinking) | **0,025 USD** |
| `deepseek-v4-pro` | 0,66 / 0,022 USD | 1,98 USD | 33k / 15k | **0,052 USD** |
| (peak = 2×, tj. 0,05 / 0,10 USD) | | | | |

- **Thinking mód je výchozí a tvoří ~80 % ceny** (33k výstupních tokenů).
  Vypnutím pro kódové úpravy odhad ceny klesne na **~0,005–0,01 USD/pokus**
  (dopočet z měřené spotřeby; vypnutí thinkingu jsem neměřil).
- **Měsíc:** při tempu 16. 10. (12 běhů / 6 h ≈ 20–50 běhů/den) =
  **15–25 USD/měsíc** při thinkingu a všech pokusech; po opravě promptu
  (hygiena) a granulí **3–5 USD/měsíc**. Vše off-peak; běhy ve špičce 2×.
- **Měření této session stálo 0,118 USD** (3 běhy DeepSeek).

## 3. Co zbývá (rozhodnutí uživatele / session HRY)

| # | krok | kdo | cena |
|---|---|---|---|
| A | **Přidat GitHub secret `DEEPSEEK_API_KEY`** do repa hry (`Settings → Secrets and variables → Actions → New repository secret`; klíč je v `E:\Users\…` uživatelském prostředí, do gitu NEPATŘÍ) | **uživatel** (agent secret nepřidává) | 0 |
| B | **Sync šablony do hry** (workflow + 5 nástrojů + providers.json + testy; podrobně v `PREDANI-HRE-…`) — bez toho placený model nemá jak pomoct | session HRY | 0 |
| C | **H230/H231** — srovnat granule s testy, opravit „extends Node“ | session HRY | 0 |
| D | **Roadmap reset** po opravě: všechny 3 granule jsou na stropu `GRAIN_MAX_RUNS=8` → orchestra je nevydá ani po opravě (nástroj `tools\roadmap-reset.mjs`, rozhodnutí uživatele) | session HRY / uživatel | 0 |
| E | *(volitelné)* `model-check.yml` pingovat místo `--no-ping` — dnes zelená, i když skutečný požadavek neprojde (H232) | orchestra (šablona) | 0 |

**Doporučené pořadí: B → C → D → A.** Až potom dává placený klíč smysl —
jinak platíte za pokusy, které padají na rozporech zadání a testů (měřeno:
2 modely × stejné 2 chyby testů).

## 4. Kdy to neplatí

Když se ukáže, že free zdroj (mistral 625 000 TPM po hygieně) stačí a kvalita
codestralu je dost — pak je placený model zbytečný a stačí ho nechat jako
vypnutou položku (bez secretu se přeskočí). A když se granule nespraví, žádný
model je nesplní (H230) — placení to neřeší.

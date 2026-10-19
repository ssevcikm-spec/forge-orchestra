# PŘEDÁNÍ HŘE — co orchestra potřebuje od `uo-shadows` (sync šablony + opravy zadání)

> **Co tenhle dokument JE:** **podklad pro session HRY** (ta jediná smí psát do
> `E:\Workspaces\uo-shadows`). Vznikl 19. 10. 2026 v orchestra session K11b
> **měřením** běhů #397–#406 a vlastních běhů na odpojeném worktree hry.
> **Co NENÍ:** pokyn a už vůbec ne zápis do hry — **do hry se nepsalo**
> (klon zůstal `c72b309`, čistý).
> **Měření a důkazy:** `ANALYZA-FREE-KLICE-2026-10-19.md`,
> `NAVRH-FREE-KLICE-KONFIGURACE-2026-10-19.md`, `HANDOFF.md` §77.

---

## 1. Proč to posílám: orchestra má opravy, hra je nemá

Orchestra v `repo/` (šablona) obsahuje od sessions K1–K5 a P42 vrstvu, která
**přesně řeší** měřené příčiny selhání #397–#406. Hra `uo-shadows` ale běží
**starý `agent.yml`** a nemá nástroje, na které se nový workflow odkazuje.
Drift gate ten rozdíl zná („jen v šabloně: 4 kroky“) a dosud ho vedl jako
známý — **je to ale příčina, ne kosmetika**: starý workflow nemá hygienu
zadání ani rozpočet requestu, takže posílá 32k-tokenové requesty na 8k strop
a pálí pokusy.

**Naměřeno 19. 10. 2026 (běhy #397–#406):** 3× `Request too large`
(request 31 462–33 803 t vs strop 8 000), 6× `Tokens per minute`, 1× parse
error; z toho 60 % promptu = `docs/GDD.md`, kterou si aider přidal kvůli
zmínce cesty v zadání. Všechny tři granule jsou dnes na **`GRAIN_MAX_RUNS`
8/8** (změřeno plným tikem conduktora: `#270 STROP GRANULE 8/8`,
`#271 STROP GRANULE 8/8`, `#273 STROP GRANULE 8/8`) — orchestra je přestala
vydávat, i když jsou „ready“.

## 2. Co přenést z šablony do hry (mechanické, s testy)

| # | soubor | směr | proč / co přináší |
|---|---|---|---|
| 1 | `.github/workflows/agent.yml` | šablona → hra | hygiena zadání + rozpočet requestu PŘED voláním (s failoverem na jiného poskytovatele) + klasifikátor selhání + timeout 300 s + 4 kroky navíc (parse gate, class_name, import, report s pojmenovanou příčinou). **Hra má starou verzi (698 řádků), šablona 826.** |
| 2 | `.forge/node/prompt-hygiene.mjs` | nový do hry | nahradí cesty (`docs/GDD.md` → `[dokument]`), aby si aider nepřidával celé dokumenty. A/B naměřeno **22 025 → 14 097 t**. |
| 3 | `.forge/node/request-budget.mjs` | nový do hry | spočítá request a porovná s **naměřeným** stropem z `providers.json`; když se nevejde, zkusí dalšího poskytovatele (P42). Ověřeno lokálně: 19k request → groq `REQUEST_TOO_LARGE` (exit 1), mistral `REQUEST_FITS` (exit 0). |
| 4 | `.forge/node/classify-agent-log.mjs` | nový do hry | rozliší `REQUEST_TOO_LARGE` / `QUOTA` / `AUTH` / `NOCHANGE` a podle toho řídí fallback i report conductorovi (ten pak vrací pokus u kvóty — K5). Starý kód měl jen `grep RateLimitError`. |
| 5 | `.forge/node/probe-provider.mjs` (+ `probe-provider.test.mjs`) | nový do hry | měření skutečných stropů z hlaviček API (recept v `providers.json._limity`). Bez něj se stropy hádají. |
| 6 | `.forge/node/priprava.test.mjs` | nový do hry | testy přípravy (v šabloně **55/55**); hlídají i kalibraci K6/K42. |
| 7 | `.forge/files-to-edit.mjs` | šablona → hra | přidává režim `--konvence` (nový workflow ho volá). Drift gate ho dosud vedl jako „záměrný“ jen proto, že starý workflow ten režim nepoužíval — **po sync workflow už záměrný není**. |
| 8 | `.forge/providers.json` | **MERGE**, ne kopie | přidat blok `limits` (naměřené stropy: mistral 625 000, cerebras 30 000, groq 8 000 TPM — 12.–13. 10.) a poskytovatele `deepseek` (placený, bez klíče se přeskočí). **Routing metadata (`anyPriority`, `skromny`) nechat z LOKÁLNÍ kopie** — `pick-provider.mjs` je bere odsud. |

**Co NEsynchronizovat:**
- **`CONVENTIONS.md`** — je **vlastnictvím hry** (rozhodnutí O6/P27) a liší se;
  sync by hru připravil o její pravidla. Naopak: nový workflow volá
  `files-to-edit.mjs --konvence`, takže hra potřebuje **rozdělení konvencí na
  sekce** (`CONVENTIONS/*.md`, v šabloně 9 souborů) a **`konvence: [...]`
  v granulích roadmapy**. To je práce session HRY (obsah je její) — do té doby
  workflow jen warning „granule nedeklaruje konvence“ a pošle zadání bez nich.
- `worker.mjs` — už shodný.
- `model-check.yml` — shodný (a i tak dnes nepingá, viz H232).

## 3. Co musí hra opravit sama (a orchestra to nespraví)

1. **H230 — dvě granule jsou v rozporu s testy** (agent nesmí editovat `tests/`,
   `CONVENTIONS.md` §5):
   - `shell.nocoins` chce mince i skóre **odstranit**, ale
     `tests/run_tests.gd:79-95` chce **5 mincí** a HUD s „0“.
   - `entity.move.smooth` chce **vyhlazení** (první krok menší), ale
     `tests:1009-1024` chce po `move(smer)` **plný krok** a `:1032` **doslovně**
     `move(dir, delta)`.
   Důkaz, že to není náhoda modelu: **dva placené modely** (DeepSeek flash
   i v4-pro, 1M kontext) selhaly na **týchž dvou** kontrolách; baseline
   čistého HEAD je **113/0**.
2. **H231 — `CONVENTIONS.md` §1g a zadání tvrdí „soubor začíná `extends Node`“,
   ale `scripts/game.gd:1` je `extends Node2D`.** V běhu #398 to codestral
   poslechl a přepsal → 5× parse error. Opravit na „zachovej existující
   `extends`; nový soubor začni `extends Node`“.
3. **Produkční vrstva `game.gd`** (vstup → záměr pohybu, PR #38) — hotové,
   testy zelené; jen ať to session HRY nevrátí zpět.

## 4. Po sync a opravách: orchestra se musí „odemknout“

Všechny tři granule mají **8/8** spotřebovaných běhů (`GRAIN_MAX_RUNS=8`,
`GRAIN_MAX_RUNS` ve `wrangler.toml` orchestra). Po opravě je orchestra
**nevydá**, dokud se strop neresetuje — nástroj
`forge-orchestra\tools\roadmap-reset.mjs` (mění stav roadmapy v D1; rozhodnutí
uživatele, ne agenta). To je poslední krok, aby se práce rozjela.

## 5. Jak ověřit, že sync je v pořádku

Ve hře (po přenosu):

```
node .forge/node/priprava.test.mjs          # 55/55
node .forge/node/probe-provider.test.mjs    # 14/14
node .forge/node/provider-choice.test.mjs   # 21/0
node .forge/files-to-edit.mjs --grain entity.move.smooth --konvence   # režim existuje
python .forge/check-schema.py .             # tvrdá brána hry
```

V orchestra:
```
node tools\kontrola-driftu.mjs              # agent.yml už nesmí být ROZDÍL
python _analyza\g3-brany.py                 # 58 bran / 0 nenulových
node tools\validate-all.mjs                 # vše v pořádku
```

## 6. Co je na straně orchestra (ne hry)

- **DeepSeek jako volitelný poskytovatel** už je v šabloně orchestra
  (`repo/.forge/providers.json` + `DEEPSEEK_API_KEY` v `repo/…/agent.yml`).
  Nasadí se až po pushi šablony a **přidání secretu** do repa hry
  (dělá uživatel; cena měřená 2,5 ¢/pokus, viz `NAVRH-FREE-KLICE-…`).
- Hra `coin-picker` je vypnutá a její workflow je jiná kopie — po sync
  šablony ji čeká totéž (ale to je na rozhodnutí uživatele, ne teď).

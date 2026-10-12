# Session Handoff — příprava orchestry: K1 (hygiena zadání + rozpočet) a K2 (klasifikace + záchrana)

> **Co tenhle dokument JE:** **předávací artefakt** pro session, která začne
> v čistém kontextu. Není to stav projektu (ten je v `HANDOFF.md`, nejnovější
> oddíl **§71**, a vede ho **souběžná session P41**) ani plán (`PLAN-DALSI-KROK.md`).
>
> **Proč to není `HANDOFF.md`:** ten je stav projektu a v tomhle stromě ho
> vlastní **souběžná session P41** (má v něm necommitnutou práci). Přepsat ho
> by znamenalo zahodit cizí záznam — což projekt zakazuje. Tenhle soubor je
> proto **samostatný** a je potřeba ho předat/odklidit, až P41 dokončí.
>
> **Napsáno:** 12. 10. 2026, ~16:4x UTC · session `session-fad22f83-bf67-4cd1-845c-0b9188180454`
> (kontext peak 406 k/1 M, 0 kompakcí, cache-hit 99,39 % — session byla zdravá;
> předání je **procesní**, ne tokenové: další kroky blokuje cizí strom a push).

## Where it started

Uživatel nejdřív chtěl **stav projektu** (bez zápisu), pak **ověřit, proč
nefungovalo generování kódu**, pak **plán oťukání poskytovatelů** a nakonec
řekl „**pracuj, dokud nebude vhodnější pokračovat novou session, pak připrav
předání**". Omezení, která platila celou dobu: **do repa hry se nesahá** (vede
ji cizí session) a **do orchestry se nesahá tam, kde pracuje P41**.

## Decisions locked + what shipped

**Jádro zjištění (měřené, 12. 10. 2026):** generování kódu nefungovalo proto,
že se model **nikdy nedozvěděl zadání** — request měl 25 065 / 27 557 / 39 167
tokenů proti stropu **8 000** (Groq zdarma). Příčiny byly dvě a obě se týkaly
toho, co posíláme, ne modelu:

1. **Aider si do chatu přidá soubory zmíněné v zadání.** Cesty typu
   `docs/TDD.md §1.1` přitáhly celé dokumenty. Doklad: artefakt běhu #366 má
   v `agent.log` soubory `docs/ARCHITEKTURA.md` a `project.godot`, i když je
   workflow nikdy nepředával.
2. **Nikde se neměřil rozpočet.** `pick-provider.mjs` posílá `max_tokens: 8`
   („poskytovatel odpovídá") a o minutu později request spadl; retry jel 9×
   s identickým requestem a fallback se kvůli jednomu `grep RateLimitError`
   **vypnul** — tedy přesně ta cesta, která mohla pomoct.

### Co je hotové (kód, necommitnuto — viz „Pick up here")

> **AKTUALIZACE 16:4x UTC: tohle už je COMMITNUTÉ — `709d1ef`** (10 souborů,
> +1 029 řádků). Commitnuto **cíleně** (`git add` na jednotlivé cesty), protože
> ve stromě je pořád **14 necommitnutých souborů P41** — ty se necommitovaly.
> **Nepushnuto:** `origin/main..HEAD = 1`; push čeká na vyžádání uživatele
> (pravidlo projektu). Do té doby zůstává červená `živý providers.json = lokální`
> a **v CI se strop Groqu nevynucuje** (běží tam stará verze `providers.json`
> z `raw.githubusercontent` → `limits` chybí → rozpočet jen varuje).

| Co | Kde | Doklad |
|---|---|---|
| **K1a hygiena zadání** — z textu zadání odstraní cesty (`[soubor]`/`[dokument]`) a vypíše, kolik tokenů by se přiložilo | `repo/.forge/node/prompt-hygiene.mjs` (nový) | A/B měření: **−7 928 tokenů** na request |
| **K1b rozpočet requestu** — spočítá request (zadání + soubory + konvence + režie) a porovná se stropem poskytovatele; **naměřený** strop vynutí, odhad jen varuje | `repo/.forge/node/request-budget.mjs` (nový) | CLI: groq → `REQUEST_TOO_LARGE` `exit 1`; nezmerený poskytovatel → varování, `exit 0` |
| **K2 klasifikace selhání** — 9 tříd (`REQUEST_TOO_LARGE / QUOTA / AUTH / PROVIDER_DOWN / PARSE / TESTS / SCRIPT_ERROR / NOCHANGE / OK`) + čísla z chyby | `repo/.forge/node/classify-agent-log.mjs` (nový) | 8 fixtur z reálných logů 9. 10. |
| **Oťukání poskytovatele** — čte limity z hlaviček `x-ratelimit-*` a z těla chyby (`Limit X, Requested Y`) | `repo/.forge/node/probe-provider.mjs` (nový) | živě na Groqu: `limit-tokens: 8000`, latence 91 ms |
| **Zapojení do workflow** — hygiena → rozpočet → `timeout 300 aider` → klasifikátor → fallback i při „request too large" → **report s pojmenovanou příčinou na VŠECH neúspěšných cestách** | `repo/.github/workflows/agent.yml` | YAML parsuje (15 kroků); jediná zmínka `RateLimitError` je v komentáři o starém kódu |
| **Naměřené limity v profilu** | `repo/.forge/providers.json` (`limits` u groq + `_limity`) | 8 000 TPM / 1 000 requestů/den; účtuje **skutečné** tokeny (ne rezervovaný výstup) |
| **Testy** | `repo/.forge/node/priprava.test.mjs` **32/32**, `repo/.forge/node/probe-provider.test.mjs` **14/14** | obsahuje i **kalibrační kontrolu** (případ, který by podle starého „znaky/4" prošel a podle měřeného nesmí) |
| **Poučení architekta (skill)** | `C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md` — nový **§4.1b „Rozpočet requestu"** + upravený popis v hlavičce | brány `over-skilly.py` (15 skillů, 0 chyb) a `kontrola-diakritiky.py` (VŠE OK) |

### Naměřené konstanty (použij je, ne odhady)

| Veličina | Hodnota | Jak změřeno |
|---|---|---|
| znaků na token na **reálném** českém kódu | **3,03** (2,91–3,16) | Groq `usage.prompt_tokens`: CONVENTIONS.md 12 290 B = 4 227 t; game.gd 12 317 B = 3 899 t; registry.gd 5 433 B = 1 820 t |
| **režie aideru** (systémový prompt) | **1 789 tokenů** (5 421 znaků) | aider 0.86.2 proti falešnému poskytovateli na localhostu |
| request A) původní zadání | 66 737 znaků ≈ **22 025 tokenů** | totéž měření (A/B) |
| request B) po hygieně | 42 715 znaků ≈ **14 097 tokenů** | totéž měření |
| `CONVENTIONS.md` sám | **~4 000 tokenů** = ~50 % stropu Groqu | `usage.prompt_tokens` |
| aider neposílá `max_tokens` | potvrzeno (tělo requestu: jen `model` + `temperature`) | zachycený request |

## Key files for next session

- `E:\Workspaces\forge-orchestra\repo\.forge\node\prompt-hygiene.mjs` — hygiena zadání
- `E:\Workspaces\forge-orchestra\repo\.forge\node\request-budget.mjs` — rozpočet (tady je konstanta `REZIE_HARNESSU = 1800`)
- `E:\Workspaces\forge-orchestra\repo\.forge\node\classify-agent-log.mjs` — klasifikace
- `E:\Workspaces\forge-orchestra\repo\.forge\node\probe-provider.mjs` + `.test.mjs` — oťukání
- `E:\Workspaces\forge-orchestra\repo\.forge\node\priprava.test.mjs` — test K1+K2
- `E:\Workspaces\forge-orchestra\repo\.github\workflows\agent.yml` — zapojení
- `E:\Workspaces\forge-orchestra\repo\.forge\providers.json` — naměřené limity
- `E:\Workspaces\forge-orchestra\.tmp\otukani\` — **měřicí dílna a doklady**:
  `mer-rezii-aideru.mjs` (A/B), `tokeny-realneho-textu.mjs`, `probe.mjs` (původní),
  `karty-groq.json`, `validate2.txt` + `validate3.txt`, `artefakt-366/agent.log`,
  `venv\` (**aider 0.86.2 nainstalovaný, funguje**)
- Handoff artefakt: `E:\Workspaces\forge-orchestra\PREDANI-OTUKANI-2026-10-12.md` (tento soubor)

## Environment

- Working directory: `E:\Workspaces\forge-orchestra`
- Python 3.12.10, Node 22; **aider 0.86.2** v `.tmp\otukani\venv\Scripts\python.exe -m aider`
- Souborová politika v době psaní: **danger-full-access** (dřív `workspace-write`,
  které blokovalo zápis podprocesům → inventář a `.py` skenery nešly spustit)
- **Souběžná session P41** pracuje ve stejném stromě (vlastní `conductor/src/index.ts`,
  `_analyza/p41-*`, `HANDOFF.md`, `KRONIKA-PROJEKTU.md`)

## Objective to re-arm

- Objective (text): **Dokončit F1 přípravy orchestry před generováním her: K1 (hygiena zadání + rozpočet requestu) a K2 (klasifikace chyb a záchrana fallbacku) v šabloně `repo/`, ověřit je, a jakmile bude vhodnější pokračovat v nové session, připravit úplné předání.**
- Re-arm: `create_goal` s textem výše; round cap **12**.
- Stav po téhle session: K1+K2 **hotové a otestované**, ale **necommitnuté** (viz níže), a **K3 nezačaté**.

## Background processes

- **Žádný neběží.** (Během session běžely jen měřicí joby: pip install aideru,
  měření tokenů, stažení artefaktu — všechny dokončené.)
- Trvalé jsou jen **nástroje**: `.tmp\otukani\venv\` (aider) a skripty v `.tmp\otukani\`.

## Subagents

- none (celou práci dělala tahle session; žádný teammate ani subagent)

## Running state

- Dev servery / porty: none
- **Conductor (Cloudflare, živý):** `https://forge-conductor.ssevcikm.workers.dev`
  - ⚠ **TIK OD 15:04:00Z NETIKÁ** (trigger dorazí, invocation umírá) — v 16:4x to
    bylo **>60 min**; brána `validate-all` to hlásí jako `CHYBA cron běží (čas)`.
    **Patří to P41** (H197/H201 měření fází tiku + `TICK_PROFIL=1` je nasazený).
  - `ready: 3`, `running: 0`, fronta má 3 připravené úlohy (#244/#245/#246).
- **Git:** `HEAD = 8613f1b` (**commit P41**), **22 změněných/untracked**, z toho
  **8 mých** (viz `git status`), **vše necommitnuté**.
  - ⚠ **Vlastní omyl této session:** omylem proběhl `git init/add/commit` v repu
    orchestry (selhalo `cd` do neexistující složky) a vznikl commit `35ecdea`
    „zaklad", který obsahoval **cizí necommitnutou práci P41**. Opraveno
    `git reset --mixed HEAD~1` → `HEAD` zpět na `8613f1b`, práce P41 je zase
    necommitnutá, commit zůstal jen v **reflogu** (`git reflog`), nic se neztratilo.
- **Soubory hry:** nedotčené (jediné čtení). `E:\Workspaces\uo-shadows` = `e4dccdb`.

## Verification — how to confirm things still work

```powershell
cd E:\Workspaces\forge-orchestra
# 1) Nástroje K1/K2 (očekáváno: 32/32 a 14/14, exit 0)
node repo\.forge\node\priprava.test.mjs
node repo\.forge\node\probe-provider.test.mjs
# 2) Rozpočet: naměřený strop Groqu MUSÍ request odmítnout (exit 1)
cd repo; node .forge\node\request-budget.mjs --zadani-text ("x" * 1800) --soubory "CONVENTIONS.md" --poskytovatel groq --model openai/gpt-oss-120b
# 3) Živá karta poskytovatele (potřebuje klíč: .secrets\groq_key.txt v orchestře)
node .forge\node\probe-provider.mjs --jen groq --bez-velkeho --stdout
# 4) A/B efekt hygieny (aider 0.86.2 v .tmp\otukani\venv)
cd ..; node .tmp\otukani\mer-rezii-aideru.mjs     # čekej A ~22 025 → B ~14 097 tokenů
# 5) Brány repa (POZOR: běží-li P41, nespouštěj g3 a validate-all současně)
python _analyza\hl-neanglicky-v-kodu.py --json _analyza\_inventar.json   # po KAŽDÉ změně .mjs/.py
node tools\validate-all.mjs
```

## Deferred + open questions

- **K3 — zmenšit kontext (nutné, ne volitelné):** i po hygieně se M0 úloha
  nevejde (14 097 > 8 000). `CONVENTIONS.md` je ~4 000 tokenů = polovina stropu;
  musí se **rozdělit na sekce** a posílat jen relevantní. Dále: 1 soubor na
  granuli, `read-deps` max 1–2 soubory, zadání ≤ ~1 400 znaků.
- **Commit a push:** můj strom je hotový, ale **nesmí se commitnout `git add -A`**
  — ve stromě je necommitnutá práce P41. Buď počkat na čistý strom, nebo
  commitnout **cíleně** (`git add repo/.forge/node/*.mjs repo/.github/workflows/agent.yml
  repo/.forge/providers.json _analyza/_inventar.json`) a **push nechat na vyžádání
  uživatele** (pravidlo projektu). Dokud se `providers.json` nepushne, hlásí
  `validate-all` `CHYBA živý providers.json = lokální`.
- **`validate-all` dnes není zelený a ne všechny chyby jsou moje:**
  `cron běží (čas)` = živý incident (P41) · `lokální kód = repo` = necommitnutý
  `conductor/src/index.ts` (P41) · `živý providers.json = lokální` = **moje**
  (vyřeší push) · mutační kontroly `B3b`/`D` padají na P41ho rozpracovaném kódu.
- **Zbytkový rozdíl, který se nepodařilo vysvětlit do konce:** CI hlásilo pro
  tutéž úlohu **27 557** tokenů, lokální A/B dává **22 025** (rozdíl ~20 %).
  Vysvětleno je: přiložený `docs/ARCHITEKTURA.md` + `project.godot` (doklad
  v artefaktu) a JSON obálka. Nedovysvětlený zbytek je nejspíš tokenizace
  (odhad 3,03 znaku/token vs skutečnost) — **další měření: nechat CI zalogovat
  `usage.prompt_tokens`** (dnes to aider nehlásí při neúspěchu).
- **Plán jako dokument není založený:** plán je zatím jen v chatu a v hlavičkách
  nástrojů. Patří založit (`PLAN-OTUKANI-A-PRIPRAVA-ORCHESTRY.md`) **spolu s novou
  hrou**, ne do stromu, kde běží P41.
- **Na uživateli:** `FORGE_PAT` (fine-grained, Contents + PR RW, ≥ 90 dní) do repa
  nové hry · rozhodnutí o scope nové hry · schválení pushu.
- **Registrace dokumentu:** tenhle soubor **není** v ručním seznamu
  `tools/kontrola-diakritiky.py` (byl by to zásah do souboru, který může měnit P41).
  Kdo s ním hne, ať ho tam doplní.

## Pick up here

**K1/K2 jsou hotové, otestované a commitnuté (`709d1ef`) — neopakuj je.** Další
kroky jsou tři a v tomto pořadí:

1. **Push** (čeká na vyžádání uživatele): `git push` → pak `validate-all` přestane
   hlásit `živý providers.json = lokální` a **v CI se začne vynucovat rozpočet**
   (do té doby jen varuje).
2. **Dorazit práci P41** — ve stromě je pořád **14 jejích necommitnutých souborů**
   (`conductor/src/index.ts`, `_analyza/p41-*`, `NEXT-SESSION-INSTRUKCE.md`,
   `.gitignore`, `ov-*.json`). Je to **její** práce: ať ji commitne ona, nebo se
   rozhodne, kdo ji převezme. **Nezametat ji vlastním commitem.**
3. **K3 — zmenšit kontext** (nutné před prvním generováním nové hry): napsat
   `CONVENTIONS.md` nové hry **po krátkých sekcích** a posílat jen relevantní
   (dnes je celý ~4 000 tokenů = polovina stropu Groqu). Pravidla pro to už jsou
   v skillu `game-developer` §4.1b — K3 je „převést je do nové hry".

**Odpověď na „mám u toho volat novou session?":** na **push a doraz P41 ne** —
to je práce s repem a dělá se to tady. Na **K3 + založení nové hry ano** — je to
nové téma s vlastní roadmapou, dokumenty a bránami, a přesně proto je tenhle
handoff psaný.

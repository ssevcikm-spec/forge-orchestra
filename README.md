# Forge Orchestra

Samostatný orchestr, který **vyvíjí hry** — plánuje, zadává úkoly bezplatným
modelům v GitHub Actions, testuje a bezpečné změny slučuje. Hra je pro něj jen
**herní dokument** (DESIGN.md + roadmapa), ne součást orchestra.

Orchestr ≠ vývoj forge (lokální pipeline `forge.cmd`). Tenhle projekt je druhá
půlka: běží 24/7 v cloudu a pracuje na herních repozitářích.

## Struktura

| Cesta | Co to je |
|---|---|
| `conductor/` | Mozek orchestra — Cloudflare Worker + cron + D1 (deployuje se sem) |
| `repo/` | Šablona, která se kopíruje do herních repů (`.forge/` + `.github/`) |
| `bin/task.mjs` | Ovládání orchestra z příkazové řádky |
| `tools/` | Pomocné nástroje (mock-conductor, telegram chat-id, test-local) |
| `install-into-repo.ps1` | Připraví herní repo (nakopíruje `.forge` a workflowy) |

## Deploy

Conductor se nasazuje **automaticky z gitu**: push do `main` ve složce
`conductor/` spustí `.github/workflows/deploy.yml` (wrangler-action) a nasadí
na Cloudflare. Potřebuje dvě GitHub Secrets:

- `CLOUDFLARE_API_TOKEN` — token s právy Workers Scripts → Edit a D1 → Edit
- `CLOUDFLARE_ACCOUNT_ID` — ID účtu z Cloudflare dashboardu

Runtime tajemství conductora (`WEBHOOK_SECRET`, `GITHUB_TOKEN`,
`TELEGRAM_BOT_TOKEN`, `NTFY_TOPIC`, …) **žijí v Cloudflare** (`wrangler secret
put`), nikdy v gitu — deployem se nemažou.

Lokální deploy (pro ladění):

```powershell
cd orchestra
.\wrangler.cmd login        # jednou, uloží OAuth do .wrangler/
.\wrangler.cmd deploy       # nasadí conductor/
```

## Modely (řetězec free LLM)

`repo/.forge/providers.json` je **jediný zdroj pravdy** pro řetězec bezplatných
poskytovatelů. Herní repy si ho **stahují za běhu** (`pick-provider.mjs` fetchně
čerstvou verzi z `raw.githubusercontent.com`), lokální kopie v repu hry je jen
záloha. Mrtvý model se proto opraví **jednou tady** a všechny hry ho uvidí.

Zkouší se **popořadě** (štědré rotované podle `run_key`, skromný gemini nakonec)
a první, kdo odpoví, vyhrává — nikoli paralelně.

- **Kontrola zdraví**: `node repo/.forge/node/providers-check.mjs`
- **Pravidelná kontrola**: `repo/.github/workflows/model-check.yml` (denně,
  založí issue, když model zmizí z katalogu)
- **Návrh pouček z chyb**: `tools/suggest-conventions.mjs`

## Tajemství — kam patří

| Tajemství | Kde žije |
|---|---|
| Cloudflare API token (deploy) | GitHub Secrets orchestra |
| WEBHOOK_SECRET, NTFY_TOPIC, TELEGRAM_BOT_TOKEN | Cloudflare Secrets |
| GitHub PAT (dispatch/PR) | Cloudflare Secrets + lokálně `.secrets/` |
| Klíče free LLM (mistral/gemini/…) | GitHub Secrets herních repů |

> **Proč klíče zůstávají v herních repech:** LLM volání běží v Actions runneru
> toho repa hry (GitHub ToS — agent smí pracovat jen na svém repu), takže klíč
> se tam čte lokálně. Je to **jedna hodnota klíče na N repů** (GitHub Secrets
> jsou per-repo a `ssevcikm-spec` je uživatel, ne organizace — nejsou žádné
> „org secrets"). Otočení klíče = aktualizace v N repech; `providers.json` to
> ale řešit neumí, proto je řetězec single-source a klíče zůstávají data.

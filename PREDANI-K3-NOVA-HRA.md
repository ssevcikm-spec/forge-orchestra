# Předání pro session K3 — nová hra musí mít kontext, který se vejde do stropu poskytovatele

> **Co tenhle dokument JE:** **předání + zadání pro session K3** (nová hra, menší
> scope). Nahrazuje `NEXT-SESSION-INSTRUKCE.md` (ten vlastní session **P41** a má
> v něm necommitnutou práci — **nesahej na něj**).
> **Co NENÍ:** stav projektu (ten je v `HANDOFF.md` §71, vlastní ho P41) ani
> kronika (`KRONIKA-PROJEKTU.md`).
>
> **Napsáno:** 12. 10. 2026, ~16:5x UTC. **Datum spotřeby:** co je tu o **stavu**
> (commity, tik, běhy), se musí **živě přeměřit** — handoff je psaný před
> dokončením pár kroků a čísla stárnou v hodinách.
> **Předchozí krok:** `PREDANI-OTUKANI-2026-10-12.md` (K1+K2 — hotové, commitnuté
> a pushnuté; **neopakuj to**).

---

## 1. Co je K3 a proč je nutné

K1 a K2 zafixovaly, že **request se nesmí poslat, když se nevejde** — jenže tím
samy o sobě orchestra **zastaví**: hygienické zadání M0 mělo **14 097 tokenů**
proti stropu **8 000** (Groq zdarma). Model se tedy zadání nikdy nedozvěděl a
všech 20 běhů posledního dne selhalo.

**K3 = upravit obsah tak, aby se vešel.** Ne model, ne poskytovatele — **zadání,
soubory a konvence**.

## 2. Naměřené konstanty (použij je, neodvozuj znovu)

| Veličina | Hodnota | Jak změřeno (nástroj) |
|---|---|---|
| znaků na token na českém kódu | **3,03** (2,91–3,16) | `usage.prompt_tokens` na Groqu, soubory hry |
| režie nástroje aider (systémový prompt) | **1 789 tokenů** | aider 0.86.2 proti falešnému API (`.tmp/otukani/mer-rezii-aideru.mjs`) |
| strop Groqu `openai/gpt-oss-120b` | **8 000 TPM**, 1 000 requestů/den | hlavička `x-ratelimit-limit-tokens` + tělo chyby 413 |
| `CONVENTIONS.md` celý | ~**4 000 tokenů** = polovina stropu | `usage.prompt_tokens` |
| soubor o 300 řádcích | ~**3 900 tokenů** | totéž |
| cesta k dokumentu v zadání | **+8 000 tokenů** | A/B měření (přitáhne celý dokument) |
| hygiena zadání (odstranění cest) | **−7 928 tokenů** | A/B měření |

**Rozpočet na granuli pro strop 8 000:** zadání ≤ 400 t (≈ 1 200 znaků, **bez
cest**) · editovaný soubor ≤ 1 500 t (~120 řádků) · závislosti ≤ 1 soubor ≤ 1 000 t
· konvence **jen relevantní sekce** ≤ 1 200 t · + režie 1 789 t.
→ **Použitelný obsah je ~5 700 tokenů.** Kdo to překročí, dostane `REQUEST_TOO_LARGE`.

Metodika (jak z toho odvodit tvar granulí) je v **skillu `game-developer` §4.1b**
— přečti ho; tam jsou i zakázané tvary granulí.

## 3. Co má K3 vyrobit (měřitelné)

| # | Výstup | Hotovo znamená |
|---|---|---|
| 1 | **`CONVENTIONS.md` nové hry po krátkých sekcích** (každá ≤ ~1 200 tokenů, nejlépe jako samostatné soubory v `CONVENTIONS/`) | `node .forge/node/request-budget.mjs` spočítá konvence jako **jednu sekci**, ne celý dokument |
| 2 | **Mechanismus, kterým se posílá jen relevantní sekce** — doporučení: **deklarace v granulí** (`"konvence": ["gdscript-api"]` v roadmapě) a workflow předá `--read CONVENTIONS/<sekce>.md`. **Nedělat odhad podle klíčových slov** v zadání: „co se má poslat" je vlastnost granule, ne věštění | roadmapa sekce deklaruje; workflow je čte; rozpočet je počítá |
| 3 | **Roadmapa nové hry s 2–5 pilotními granulemi**, každá 1 soubor ≤ ~120 řádků, se `size_lines` a deklarovanými sekcemi konvencí | `request-budget.mjs --poskytovatel groq` řekne u **každé** `REQUEST_FITS` (ne jen „mělo by") |
| 4 | **Pilotní běh v CI** — jedna granule end-to-end | request ≤ 7 000 t (naměřeno poskytovatelem) · při vypnutém prvním zdroji nastoupí druhý · v `/status` je **pojmenovaná příčina**, ne `GitHub Actions: failure` · PR vznikne nebo se pojmenuje, proč ne |
| 5 | **Protizkouška pilotu** | záměrně nafouknuté zadání (např. cesta k `docs/TDD.md`) **musí** skončit `REQUEST_TOO_LARGE` — jinak je hradlo slepé |

**Co NEDĚLAT:** nezakládat celou hru dřív, než projde pilot · nezvedat
`GRAIN_MAX_RUNS` ani `MAX_ATTEMPTS` · nepsat do hry `uo-shadows` (je zmrazená,
vede ji cizí session) · necommitovat soubory P41 (viz §6) · nedávat do zadání
cesty k souborům.

## 4. Nástroje, které na to jsou (a jak je spustit)

```powershell
cd E:\Workspaces\forge-orchestra
# Testy obou sad nástrojů (očekáváno 32/32 a 14/14)
node repo\.forge\node\priprava.test.mjs
node repo\.forge\node\probe-provider.test.mjs
# Rozpočet: tohle je brána, kterou musí každá granule projít (exit 1 = nevejde se)
cd repo
node .forge\node\request-budget.mjs --zadani-text "…" --soubory "scripts/x.gd" --konvence CONVENTIONS/gdscript-api.md --poskytovatel groq --model openai/gpt-oss-120b
# Hygiena zadání (co by se přiložilo a kolik to stojí)
node .forge\node\prompt-hygiene.mjs "Přepiš scripts/x.gd podle docs/TDD.md §1.1"
# Měření stropu poskytovatele (klíč z prostředí nebo z orchestry .secrets/<nazev>_key.txt)
node .forge\node\probe-provider.mjs --jen groq --bez-velkeho --stdout
# Klasifikace selhání z logu běhu
node .forge\node\classify-agent-log.mjs --log agent.log --zmena ne
```

**Doklady a měřicí dílna:** `E:\Workspaces\forge-orchestra\.tmp\otukani\`
(`mer-rezii-aideru.mjs`, `tokeny-realneho-textu.mjs`, `karty-groq.json`,
`validate*.txt`, `artefakt-366/agent.log`, `venv\` s aiderem 0.86.2).

## 5. Kde je co (absolutní cesty)

- `E:\Workspaces\forge-orchestra\repo\` — **šablona hry**; nová hra z ní vzniká.
  Tady se K3 projeví: `repo\CONVENTIONS.md` (rozdělit), `repo\.forge\roadmap.json`
  (tvar granulí), `repo\.forge\node\*` (nástroje), `repo\.github\workflows\agent.yml`.
- `E:\Workspaces\forge-orchestra\PREDANI-OTUKANI-2026-10-12.md` — co je hotové z K1/K2.
- `C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md` — **§4.1b rozpočet requestu** (metodika).
- `E:\Workspaces\uo-shadows` — **stará hra: jen čti.** Nová hra bude nový repozitář.
- `E:\Workspaces\forge-orchestra\install-into-repo.ps1` — ⚠ **je zastaralý**
  (počítá s `projects\<název>` a `forge new`, což v layoutu na `E:` neexistuje).
  Založení nové hry je proto **vlastní úkol** (viz §7).

## 6. Stav při psaní (přeměřit!)

- `HEAD` orchestry: **`9337577`** (K1+K2) — **pushnuto**; `origin/main..HEAD = 0`.
- **Ve stromě je 14 necommitnutých souborů P41** (`conductor/src/index.ts`,
  `_analyza/p41-*`, `NEXT-SESSION-INSTRUKCE.md`, `.gitignore`, `ov-*.json`).
  **Nezametat je vlastním commitem** — buď je commitne ona, nebo se rozhodne,
  kdo je převezme.
- ⚠ **Tik conductora byl mrtvý** (`last_cron` 15:04:00Z, v 16:4x to bylo 93+ min;
  trigger dorazí, invocation umírá). **Dokud je mrtvý, orchestra nevydá ani
  pilotní granuli** — ověř `https://forge-conductor.ssevcikm.workers.dev/health`
  (`last_cron` starší než 10 min = netiká). Patří to P41 (H197/H201), ne K3.
- `ready: 3` (staré úlohy #244/#245/#246), `running: 0`. Nová hra musí být
  v conductoru **zaregistrovaná** (`POST /game`) a nastavená jako aktivní.
- **Na uživateli:** `FORGE_PAT` (fine-grained, Contents RW + Pull requests RW,
  expirace ≥ 90 dní) do repa nové hry · jméno a scope nové hry · schválení pushů.

## 7. Otevřené otázky, které musí rozhodnout uživatel (ne agent)

1. **Jméno a rozsah nové hry** (scope je páka: čím menší, tím jistěji se granule
   vejdou pod 8 000 tokenů).
2. **Založit novou hru jako nový repozitář** — a opravit při tom
   `install-into-repo.ps1` (nebo napsat `forge-*.mjs`), aby založení bylo
   **opakovatelné a ověřené testem** (dnes je to ruční skript se starými cestami).
3. **Zda má nová hra jet na Groqu** (zdarma, ale 8 000 TPM a bez karty) nebo
   nejdřív změřit strop Mistralu/Cerebrasu (klíče má jen uživatel; měření je
   `probe-provider.mjs`, 5 minut) — s větším stropem se rozpočet uvolní.

## 8. Pick up here

**Nejdřív zkontroluj `/health` (tik) a `git log` (je P41 doCommitnutá?).** Pak
vezmi šablonu `repo/` a udělej **výstup 1 a 3 z §3**: rozděl `CONVENTIONS.md` na
sekce a napiš pilotní roadmapu tak, aby u **každé** granule prošel
`request-budget.mjs --poskytovatel groq` na `REQUEST_FITS`. Teprve až to platí,
řeš založení repa nové hry a pilotní běh — jinak vznikne hra, kterou orchestra
nedokáže vydat (přesně to se stalo 9. 10.).

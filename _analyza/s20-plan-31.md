
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 3.1 ⏸ ODLOŽENO — Groq limit 8k tokenů (+ dynamická úprava balíčku)

> **ROZHODNUTÍ UŽIVATELE (2. 10. 2026), doslova:**
> *„Zatím zapiš do plánu ODLOŽENO — Groq limit 8k tokenů — dynamicky
> assignovat/redukovat balíček pro omezené modely."*
>
> **Co to znamená:** **NIC SE S TÍM TEĎ NEDĚLÁ.** Ani se nevyřazuje Groq,
> ani se nemění `CONVENTIONS.md`, ani `agent.yml`. **Směr řešení je zapsaný**
> (dynamická úprava balíčku podle modelu) — ale **není to zadání pro akční
> session** a **nikdo ho nemá začít plnit bez nového pokynu.**

**Proč to není „zapomenuté":** je to v plánu **s podmínkou znovuotevření** (níž)
a s **naměřenými čísly**, takže až to bude potřeba, nezačíná se od nuly.

**Naměřeno (ať se to nemusí měřit znovu) — `HANDOFF.md` §18.17 a §18.18:**

| Co | Číslo | Odkud |
|---|---|---|
| Groq free limit | **`TPM: Limit 8000`**, hláška **`Request too large`** (na jeden request, ne minutová kvóta) | log běhu #146, **9×** |
| Skutečný request (Groq ho viděl) | **~14 400 tokenů** (tři různá čísla: 14 398 / 14 377 / 14 402) | tentýž log |
| **Pevná část** (platí pro každou granuli) | **9 196 tokenů** = `CONVENTIONS.md` 3 839 + obal Aideru **5 357** (dopočet) | `p19h-groq-presne.py` |
| Nejmenší granule v repu | **9 531 tokenů** (`core.attributes`; vlastní část jen 335) | `p19i-co-zmensit.py` |
| **Kolik granulí se vejde dnes** | **0 z 21** | tamtéž |
| Kdyby `CONVENTIONS.md` měl 3 000 znaků | vešlo by se **10 z 21** | tamtéž |
| Kdyby měl 6 000 znaků | vešlo by se **2 z 21** | tamtéž |
| Zlom pro nejmenší granuli | `CONVENTIONS.md` max **~6 900 znaků** (60 % dneška) | tamtéž |
| „Sekvenčně" | **nejde** — limit je na JEDEN request, Aider posílá celý kontext naráz | `p19-sonda-groq.py` |

**Směr řešení, který uživatel pojmenoval (zapsaný, neprovedený):**
**dynamicky assignovat / redukovat balíček pro omezené modely.** Konkrétně by to
znamenalo: spočítat velikost vstupu **před** výběrem poskytovatele a poslat úlohu
jen tomu, do jehož limitu se vejde — případně **zmenšit, co se posílá**
(např. `CONVENTIONS.md` jinak pro omezené modely). **To je zásah do
`pick-provider.mjs` a/nebo `agent.yml` — tedy přesně to, co se teď NEDĚLÁ.**

**Podmínka, kdy to znovu otevřít** (stačí jedna):

1. **nějaká úloha zase spadne na `Request too large`** (a spálí tím pokus), nebo
2. **dojde kvóta** u štědrých poskytovatelů (mistral / cerebras) a Groq by byl
   potřeba, nebo
3. uživatel řekne, že se na tom má pracovat.

**Co se s tím NEDĚLÁ teď (a je to součást rozhodnutí):**

- **Nevypínat Groq z rotace** — zůstává, jak je (`anyPriority: 30`).
- **Neměnit `CONVENTIONS.md`** kvůli limitu.
- **Neměnit `agent.yml`** (ani ten dvojitý prefix `openai/openai/…` — je to
  samostatná vada, ale taky **odložená**, aby se nepletla s tímhle).

### 3.1b Co z Úkolu 1 zadání zůstává otevřené (a je to NÁVRH, ne úkol)

| # | Co | Stav |
|---|---|---|
| **3.1.2** | Opravit `agent.yml:227` — `openai/` prefix navíc (nález **H4**) | **ODLOŽENO** (uživatel neřekl „ne", řekl „zatím") |
| **3.1.3** | Doplnit TPM limity do `providers.json` (návrh **NA14**) | **NEOVĚŘENO** — rozhodne příští session |
| — | Vyřadit Groq / zmenšit `CONVENTIONS.md` | **ODLOŽENO** (tahle sekce) |

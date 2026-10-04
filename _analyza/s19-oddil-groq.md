
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
### 18.17 Odpověď na otázku „není 8 000 tokenů nějak málo?" — a DVĚ VADY, které to odhalilo

**Otázka uživatele (2. 10. 2026):** *„Není 8k tokenů nějak málo? Neblbne to
náhodou?"* **Neblbne — ale otázka odhalila dvě vady v mém vlastním zápisu.**

Nástroj: `python _analyza\p19-sonda-groq.py` (nový) — čte **log běhu #146**,
ne dokumentaci.

**A) Limit není vymyšlený — hlásí ho sám poskytovatel, a je to LIMIT NA REQUEST:**

```
Request too large for model `openai/gpt-oss-120b` in organization `org_01m3…`
service tier `on_demand` on tokens per minute (TPM): Limit 8000, Requested
14398, please reduce your message size and try again.
Need more tokens? Upgrade to Dev Tier today at https://console.groq.com/settings/billing
The API provider has rate limited you. Try again later or check your quotas.
```

| Co log říká | Počet |
|---|---|
| `Request too large` | **9×** |
| `tokens per minute (TPM): Limit 8000` | **9×** |
| `tokens per day (TPD)` | **0×** |
| `requests per minute (RPM)` | **0×** |
| HTTP `429` | **0×** |
| `rate limit reached` | **1×** |

> **⚠ Zásadní rozlišení, které odpovídá na tu otázku:** hláška je **`Request too
> large`**, ne „rate limit reached". To znamená, že Groq **odmítne JEDEN
> request**, který se do limitu nevejde — **neznamená to, že vyčerpáme minutu**.
> Není to tedy „přepálená kvóta" ani náhoda: **náš request je větší než celý
> povolený objem na minutu.** Opakování nepomůže, protože další request je
> stejně velký. Proto je v logu **9 pokusů, všechny stejně neúspěšné.**

**B) VADA Č. 1 v mém zápisu — nebylo to jedno číslo, ale tři.**
`HANDOFF.md` §18.7 tvrdilo, že request měl **14 398 tokenů**. Log má ale
**tři různá `Requested`**: **14 398** (4×), **14 377** (2×) a **14 402** (2×).
Správné znění je **„request je ~14,4 tisíce tokenů"** — jedno číslo dělalo
z měření přesnější, než bylo. **Opraveno v §18.7.**

**C) VADA Č. 2 — a ta je zajímavější: repo má o Groqu číslo, které už neplatí.**
`providers.json` u Groqu tvrdí:

> *„Denní strop 200k tokenů a **jeden běh spálí ~6k** → ~33 běhů/den."*

**Naměřeno: ~14,4 tisíce na běh** — tedy **2,4× víc, než repo předpokládá**.
Důsledek: odhad **„~33 běhů/den" je nadsazený** — při 200k/den a 14,4k/běh to
vychází na **~13–14 běhů/den** (a to jen kdyby se do TPM vešly, což se
nevejdou). **Je to táž třída jako nález N1:** číslo v repu je **zastaralé
měření**, ne lež — a kdo se podle něj rozhoduje, rozhoduje se o jiném systému.

**D) A třetí věc, která se při tom změřila: můj odhad promptu byl DOLNÍ.**
Vlastní měření znaků dalo **≈ 11 207 tokenů** (§18.7); Groq naměřil **~14 400**.
Rozdíl **~3 200 tokenů** je to, co můj odhad **nepočítá**: přesný tokenizer
Aideru a obal chatu. **Není to chyba ani jednoho z měření** — odpovídají na
**jinou otázku** („kolik je znaků ÷ 3" vs. „co poslal tokenizer"). **Pro
rozhodování platí to větší číslo**, protože to je to, co poskytovatel vidí.
*(Vlastní číslo Aideru `Tokens: X sent, Y received` v logu **není** — naměřeno
0 výskytů; Aider vypíše jen `Unknown context window size … using sane defaults`,
protože model `openai/openai/gpt-oss-120b` nezná.)*

**E) Co z toho plyne pro rozhodnutí (a co je měření a co názor):**

| # | Tvrzení | Je to |
|---|---|---|
| 1 | Groq má `TPM: Limit 8000` a request má **~14 400 tokenů** | **MĚŘENÍ** (log, 9×) |
| 2 | Je to **`Request too large`** — odmítne se jeden request, ne minuta | **MĚŘENÍ** (text hlášky) |
| 3 | `providers.json` tvrdí „~6k/běh", skutečnost je **~14,4k** | **MĚŘENÍ** (rozpor dvou zdrojů) |
| 4 | **Groq se do našeho promptu nevejde a nevejde se tam ani po opakování** | **DŮSLEDEK** (1+2) |
| 5 | Vyřadit Groq z rotace pro velké granule (nebo zmenšit vstup) | **NÁZOR** — rozhoduje uživatel |
| 6 | Zmenšit **pevnou část** (CONVENTIONS.md + systémový prompt Aideru), ne prompt granule | **NÁZOR** — podložený tím, že pevná část je většina vstupu |

> **⚠ Poučení, které patří k téhle session:** uživatel se zeptal **„není to
> málo?"** — a **ta otázka našla dvě vady**, které by jinak zůstaly: jedno
> číslo místo tří a **2,4× podhodnocený odhad v repu**. Ani jednu z nich by
> neodhalil žádný z 29 bran — obě vypadaly jako **hotové měření**.
> Je to týž vzor jako celá kronika: **nebezpečná není chybějící znalost, ale
> číslo, které vypadá ověřeně.**

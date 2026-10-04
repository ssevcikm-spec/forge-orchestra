
> **Co tenhle dokument JE:** záznam o provedení. Hlavičku „Co tenhle dokument JE“
> doplnila session 2. 10. 2026 (opatření 7, Úkol 5a zadání
> `ZADANI-OPRAVA-MERIDEL.md`) — do té doby ji dokument neměl a musel se
> jeho druh hádat z názvu (nález **NA21**).
## 20. Rozhodnutí uživatele 2. 10. 2026 (14:0x UTC) — Groq ODLOŽEN

> **Co je tenhle oddíl:** **záznam rozhodnutí**, které změnilo plán. Není to
> měření ani plán — je to **pokyn**, který je potřeba dohledat, až se k tématu
> někdo vrátí.

**Rozhodnutí uživatele, doslova:**

> *„Zatím zapiš do plánu ODLOŽENO — Groq limit 8k tokenů — dynamicky
> assignovat/redukovat balíček pro omezené modely."*

**Co to znamená:**

| # | Důsledek |
|---|---|
| **1** | **Groq se z rotace NEVYŘAZUJE.** Zůstává, jak je (`anyPriority: 30`, `strongModels: ["openai/gpt-oss-120b"]`) |
| **2** | **`CONVENTIONS.md` se NEMENŠUJE** kvůli limitu |
| **3** | **`agent.yml` se NEMĚNÍ** — ani dvojitý prefix `openai/openai/…` (nález H4) |
| **4** | **Směr řešení je zapsaný** (dynamická úprava balíčku podle modelu) — ale **není to zadání** |
| **5** | Z plánu se stává: **první krok je granule `tests.harness`** (dřív „rozhodnout o Groqu") |

**Směr, který uživatel pojmenoval (neprovedený):** *„dynamicky assignovat /
redukovat balíček pro omezené modely."* Konkrétně by to znamenalo spočítat
velikost vstupu **před** výběrem poskytovatele a poslat úlohu jen tomu, do jehož
limitu se vejde — případně **zmenšit, co se posílá**. To je zásah do
`pick-provider.mjs` a/nebo `agent.yml`.

**Podmínka, kdy to znovu otevřít** (stačí jedna):

1. nějaká úloha **zase spadne na `Request too large`** (a spálí pokus),
2. **dojde kvóta** u štědrých poskytovatelů (mistral / cerebras) a Groq by byl potřeba,
3. **uživatel řekne**, že se na tom má pracovat.

**Naměřená čísla k tomu (aby se nemusela měřit znovu) — §18.17 a §18.18:**

```
Groq free:  TPM Limit 8000, hláška "Request too large" (na JEDEN request)
Request:    ~14 400 tokenů  (14 398 / 14 377 / 14 402 — tři různá čísla)
Pevná část:  9 196 tokenů  (CONVENTIONS.md 3 839 + obal Aideru 5 357 — dopočet)
Nejmenší granule:  9 531 tokenů  (core.attributes)
→ vejde se 0 z 21 granulí
Kdyby CONVENTIONS.md měl 3 000 znaků → vešlo by se 10 z 21
Kdyby měl 6 000 znaků → vešlo by se 2 z 21
"Sekvenčně" nejde — limit je na JEDEN request, Aider posílá celý kontext naráz
```

**Co se tím NEMĚNÍ:** nález **H5** (Groq limit je skutečný) platí dál, stejně
jako nálezy **H4** (dvojitý prefix) a **H13** (`providers.json` má o Groqu
zastaralé číslo „~6k/běh", naměřeno ~14,4k). **Odloženo je PROVEDENÍ, ne
zjištění.** Až se k tomu někdo vrátí, **začíná od změřených čísel výš**, ne od
nuly.

**Zapsáno i do:** `PLAN-DALSI-KROK.md` **§3.1** (celá sekce `ODLOŽENO`
s podmínkou znovuotevření), **§4 zákaz č. 9** („nezačínej řešit Groq"),
**§5 pořadí** (krok 1 = granule `tests.harness`), a `KRONIKA-PROJEKTU.md`
§5 návrh **NA16**.

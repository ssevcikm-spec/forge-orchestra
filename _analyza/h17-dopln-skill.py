# -*- coding: utf-8 -*-
"""Připojí nové pasti do skillu `overovani` (§7.15, §7.16).

PROČ SKRIPTEM: soubor je mimo workspace (`~\\.dsh\\skills\\`) a zápis textu
ruční editací umí zahodit BOM / přepsat konce řádků (skill `dsh-prostredi`
§2). Tenhle nástroj zapisuje **bajty** a před/po ověří, že původní obsah
zůstal prefixem.
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CIL = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\overovani\SKILL.md")

NOVY = """

---

## 8. Osmá a devátá past — naměřeno 2. 10. 2026 (ověřování cizí práce)

### 8.1 „VYDALO SE" NENÍ „PODAŘILO SE" — a stav úlohy to nerozliší

**Naměřeno 2. 10. 2026.** Pět granulí (`#142`–`#146`) se v jednom tiku
**vydalo** workerovi — stav v `/queue` byl `running`, `attempts=1`, a to se
četlo jako úspěch opravy (guard přestal držet úlohy v cooldownu). O pár minut
později byly **zpátky `ready` s `attempts=1`**: **všech pět selhalo.**

| Co měřidlo tvrdilo | Co byla pravda |
|---|---|
| `/queue` → `stav=running pokusů=1` | úloha se **vydala**, ale **nesplnila se** |
| `/roadmap` → `status=queued` | práce **není hotová**, jen se na ni znovu čeká |

**Pravidlo:** stav úlohy (`ready`/`running`) je **stav fronty**, ne **výsledek
práce**. Výsledek je v **běhu** (GitHub Actions: `conclusion`) a v **PR**
(`merged_at`). Kdo z `running` usoudí „funguje to", měří **frontu**.
**A totéž platí obráceně:** „PR nevznikl" **není** totéž jako „úloha selhala
na testech" — může selhat **před** editací.

### 8.2 BĚH MŮŽE SELHAT ZPŮSOBEM, KTERÝ NENÍ ANI ZELENÝ, ANI ČERVENÝ

**Naměřeno 2. 10. 2026** (běh `#146`). Čtyři různé druhy selhání téhož kroku,
každý se čte jinak:

| Druh | Jak to vypadá v logu | Co to znamená |
|---|---|---|
| **rate limit poskytovatele** | `litellm.RateLimitError … tokens per minute (TPM): Limit 8000, Requested 14398` | agent **needitoval**; kód je netknutý, testy dávají **baseline** |
| **parse error kódu agenta** | `Parse Error: Cannot infer the type of …` | agent **editoval**, ale kód se neparsuje |
| **žádná změna** | krok „Agent nic nezměnil" | agent **nedostal odpověď** (limit, kvóta, timeout) |
| **neproběhlo (prostředí)** | `PermissionError [WinError 5]`, `spawn EPERM` | **neměřilo se nic** — třetí stav (viz §7.13) |

**Pravidlo: u selhaného běhu se VŽDY čte `[test] N kontrol, M selhání`
z LOGU, ne jen `conclusion`.** Když v logu svítí **baseline** (počet kontrol
jako na `main`), agent **nic nezměnil** — a hledat příčinu v testech je slepá
ulička. Naměřeno: `#146` dal `59 kontrol, 0 selhání`, což je **přesně**
baseline `origin/main` — a zadání přesto tvrdilo, že úloha „spadla na kontrole
izo projekce". **Nespadla; ta kontrola se vůbec nespustila.**

**A ještě jedna věc téhož druhu: jméno modelu se slepuje z PROVIDERu a MODELu.**
Naměřeno: `FORGE_PROVIDER: groq` + `FORGE_MODEL: openai/gpt-oss-120b`
→ Aider dostal `openai/openai/gpt-oss-120b` a hlásil
`Warning … Unknown context window size and costs, using sane defaults`.
Když nástroj řekne „použiju rozumné výchozí hodnoty", **měří jinak, než si
systém myslí** — a čísla o tokenech pak nejsou o skutečném modelu.
"""

puvodni = CIL.read_text(encoding="utf-8")
if "## 8. Osmá a devátá past" in puvodni:
    print("CHYBA: oddíl 8 už ve skillu je — nepřidávám dvakrát")
    sys.exit(2)

spojeny = puvodni.rstrip("\n") + "\n" + NOVY
assert spojeny.startswith(puvodni.rstrip("\n")), "PUVODNI OBSAH NENI PREFIXEM"
CIL.write_bytes(spojeny.encode("utf-8"))
zpet = CIL.read_text(encoding="utf-8")
assert zpet == spojeny, "ZAPSANY OBSAH NESEDI"

print("  %s: %d -> %d znaků (+%d)"
      % (CIL.name, len(puvodni), len(zpet), len(zpet) - len(puvodni)))
for k in ["## 1.", "## 7. Sedm pastí", "## 8. Osmá a devátá past",
          "TPM", "VYDALO SE"]:
    print("  %-28s %s" % (k, "OK" if k in zpet else "CHYBI"))

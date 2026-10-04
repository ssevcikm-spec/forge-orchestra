# -*- coding: utf-8 -*-
r"""Doplní do `NEXT-SESSION-INSTRUKCE.md` zákaz „nezačínej s Groqem"
a opraví „Hotovo znamená" + §6 (kde jsme v projektu).

PROČ: uživatel Groq **odložil** — a zadání to musí říct **výslovně v zákazech**,
jinak si příští session přečte §2.2 („Groq se nevejde") a **začne to řešit**.

Použití:  python _analyza\s20e-zadani-doplnky.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ZAPIS = "--zapis" in sys.argv

text = ZADANI.read_text(encoding="utf-8")
puvodni = text

# ── 1) §4: zákaz č. 1 — Groq je odložený ──────────────────────────────────
KOTVA4 = "## 4. Co NEDĚLAT\n\n"
assert text.count(KOTVA4) == 1, "kotva §4"
ZAKAZ = """## 4. Co NEDĚLAT

- **⏸ SE GROQEM NEDĚLEJ NIC — uživatel to ODLOŽIL** (2. 10. 2026):
  *„Zatím zapiš do plánu ODLOŽENO — Groq limit 8k tokenů — dynamicky
  assignovat/redukovat balíček pro omezené modely."*
  **Nevyřazuj Groq z rotace. Nemenši `CONVENTIONS.md`. Nemeň `agent.yml`
  (ani ten dvojitý prefix `openai/openai/…` z nálezu H4).**
  Naměřená čísla i směr řešení jsou v `HANDOFF.md` **§20**
  a `PLAN-DALSI-KROK.md` **§3.1** — přečti je, ale **neprováděj**.
  Otevře se to znovu, až (a) úloha zase spadne na `Request too large`,
  (b) dojde kvóta štědrým poskytovatelům, nebo (c) uživatel řekne.
"""
text = text.replace(KOTVA4, ZAKAZ, 1)
assert text != puvodni, "§4 se nezměnil"
print("  1) §4: přidán zákaz 'se Groqem nic'")

# ── 2) §4: oprava odkazu na §8h → §8g (nový blok omylů je 8g) ─────────────
text = text.replace("do `HANDOFF.md` **§19 i §8h**", "do `HANDOFF.md` **§21 i §8h**")
print("  2) opravena čísla oddílů pro zápis (§21, §8h)")

# ── 3) §5: doplnit odložení Groqu mezi „Hotovo znamená" ───────────────────
KOTVA5 = "- [ ] **Úkol 1** hotový: konkrétní návrh (soubor, řádek, hodnota) s čísly\n      a s vyznačením „měření vs. názor\"; **nenasazeno**.\n"
if KOTVA5 in text:
    text = text.replace(
        KOTVA5,
        "- [ ] **Úkol 1** hotový: granule `tests.harness` je v roadmape\n"
        "      s `size_lines` i promptem a **vrácení vady M3 ji shodí**.\n", 1)
    print("  3) §5: Úkol 1 = granule (dřív Groq)")
else:
    print("  3) §5: kotva Úkolu 1 se nenašla — kontroluji ručně")

# ── 4) §5: opravit formulaci o pushi (už je hotový) ──────────────────────
text = text.replace(
    "- [ ] **Úkol 2** hotový: **nejdřív ověřeno** (`git status`, `git diff --stat`,\n"
    "      brány zelené), **pak commitnuto** (dva commity), **pak pushnuto** —\n"
    "      a ověřeny **tři** kroky nasazení, každý s výstupem.",
    "- [ ] **Úkol 2** — **už je hotový** (push 2. 10. 2026). **Zkontroluj to**\n"
    "      (`rev-list --count origin/main..HEAD` = 0 v obou) a **použij stejné\n"
    "      pořadí** (ověřit → commitnout → pushnout) na to, co změníš ty.", 1)

# ── 5) §6: aktuální stav kroků ───────────────────────────────────────────
KOTVA6 = "## 6. Kde jsme v projektu"
i = text.find(KOTVA6)
assert i > 0, "kotva §6"
NOVY6 = """## 6. Kde jsme v projektu (odvozeno z `PLAN-DALSI-KROK.md` §5)

| Krok | Stav |
|---|---|
| 1. **granule `tests.harness`** (zavírá nález **H12**) | **nezačato** ← *další krok* |
| 2. ruční seznamy → projití složky | nezačato |
| 3. uklidit `merge-scratch` | nezačato |
| ⏸ **Groq limit 8k** (dynamická úprava balíčku) | **ODLOŽENO uživatelem** 2. 10. 2026 (`HANDOFF.md` §20) |
| ✅ commit + push obou repů | **HOTOVO** (`orchestra` `f5b1ea0`, `uo-shadows` `c40bdd5`) |

**Až budou hotové kroky 1–3**, řetěz se přepne do **závěrečné fáze**
(`PREDAVANI-SESSION.md` §2.3): **validační session → cyklus validace/oprav →
uzavírací session se shrnutím, lessons learned a revizí nástrojů a skillů.**
"""
text = text[:i] + NOVY6
assert text != puvodni, "§6 se nezměnil"
assert "ODLOŽENO uživatelem" in text, "ODLOŽENO se nevepsalo"
print("  4) §6: aktuální stav kroků (Groq = ODLOŽENO, push = HOTOVO)")

assert text.startswith(puvodni[:600]), "HLAVIČKA SE ZMĚNILA (nemá se)"
if ZAPIS:
    ZADANI.write_bytes(text.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(puvodni.encode("utf-8")), len(text.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

# -*- coding: utf-8 -*-
r"""Aktualizuje `PLAN-DALSI-KROK.md`: pořadí v §5 a zákaz v §4.

PROČ: rozhodnutím uživatele („ODLOŽENO — Groq limit 8k") se **změnil plán**:
krok 1 byl „rozhodnout o Groqu" a už je rozhodnutý (odloženo) → **na prvním
místě je teď něco jiného**. Nechat v §5 „rozhodnout o Groqu" znamená, že plán
posílá příští session dělat věc, která je hotová.

Použití:  python _analyza\s20b-plan-poradi.py [--zapis]
"""

import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
PLAN = WS / "PLAN-DALSI-KROK.md"
ZAPIS = "--zapis" in sys.argv

text = PLAN.read_text(encoding="utf-8")

# ── 1) §5 — nové pořadí ────────────────────────────────────────────────────
STARE5 = """| **1** | §3.1 rozhodnout o Groqu (+ jméno modelu) | malá | střední | **ANO** — každý další běh spálí pokusy |
| **2** | §3.2 commit + push obou repů (**čeká na uživatele**) | malá | střední | **ANO** — `ARCHITEKTURA.md` §2.1 v repu není |
| **3** | §3.3 granule `tests.harness` | střední | nízké | Ne — ale bez ní zůstane H12 otevřený |
| **4** | §3.4 ruční seznamy → projití složky | malá | nízké | Ne — ale každá další session na to narazí |
| **5** | §3.5 uklidit `merge-scratch` | malá | nízké | Ne |"""

NOVE5 = """| **1** | §3.3 granule `tests.harness` | střední | nízké | Ne — ale bez ní zůstane **H12** otevřený |
| **2** | §3.4 ruční seznamy → projití složky | malá | nízké | Ne — ale každá další session na to narazí |
| **3** | §3.5 uklidit `merge-scratch` | malá | nízké | Ne |
| ⏸ | §3.1 **Groq (ODLOŽENO uživatelem)** | — | — | **Ne** — otevře se, až úloha zase spadne na `Request too large` |
| ✅ | §3.2 commit + push obou repů | — | — | **HOTOVO** (2. 10. 2026; `orchestra` `14d1daf`, `uo-shadows` `c40bdd5`) |

**Změna pořadí proti minulému plánu (a proč):** krok **1** byl „rozhodnout
o Groqu" — **uživatel rozhodl 2. 10. 2026 ODLOŽIT**, takže **není co dělat**
a na první místo se posouvá **granule `tests.harness`** (jediná věc, která
zavírá otevřený nález **H12**). **Krok 2 (push) je hotový** — oba repy jsou
pushnuté a čisté."""

assert text.count(STARE5) == 1, "kotva §5 není právě 1× (nalezeno %d)" % text.count(STARE5)
novy = text.replace(STARE5, NOVE5, 1)
assert novy != text, "ZÁZNAM §5 NEPROBĚHL"
print("  1) §5: nové pořadí (1 = granule tests.harness)")

# ── 2) §4 — nový zákaz ─────────────────────────────────────────────────────
STARE4 = "| **8** | **Nasadit cokoli do conductora bez schválení** | Deploy do živé automatizace je zásah, který vidí uživatel |"
NOVE4 = """| **8** | **Nasadit cokoli do conductora bez schválení** | Deploy do živé automatizace je zásah, který vidí uživatel |
| **9** | **Začít řešit Groq limit** (vyřadit Groq, zmenšit `CONVENTIONS.md`, opravit `agent.yml:227`) | **Uživatel to 2. 10. 2026 ODLOŽIL** („Zatím zapiš do plánu ODLOŽENO — Groq limit 8k tokenů — dynamicky assignovat/redukovat balíček pro omezené modely"). **Směr je zapsaný** (§3.1), ale **není to zadání** — čeká na nový pokyn nebo na to, až úloha zase spadne na `Request too large` |"""

assert text.count(STARE4) == 1, "kotva §4 není právě 1×"
novy2 = novy.replace(STARE4, NOVE4, 1)
assert novy2 != novy, "ZÁZNAM §4 NEPROBĚHL"
print("  2) §4: přidán zákaz č. 9 (nezačínat Groq)")

assert novy2.count("ODLOŽENO") >= 3, "slovo ODLOŽENO je v plánu málo"
assert novy2.startswith(text[:4096]), "PŘEDCHOZÍ OBSAH SE ZMĚNIL"

print()
print("  PŘED: %d B   PO: %d B" % (len(text.encode("utf-8")), len(novy2.encode("utf-8"))))
if ZAPIS:
    PLAN.write_bytes(novy2.encode("utf-8"))
    print("  ZAPSÁNO.")
else:
    print("  (dry-run — spusť s --zapis)")

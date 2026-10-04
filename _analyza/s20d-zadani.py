# -*- coding: utf-8 -*-
r"""Aktualizuje `NEXT-SESSION-INSTRUKCE.md` po rozhodnutí o Groqu.

CO SE MĚNÍ (a proč):
  * **hlavička** — commity, čas, počty omylů/nálezů/poučení (zestárly pushi),
  * **Úkol 1** („zastavit plýtvání běhy") → **ODLOŽENO uživatelem**, nahrazuje
    ho **granule `tests.harness`** (dosud Úkol 3),
  * **Úkol 2** (push) → označen jako **HOTOVÝ**,
  * **Úkol 3** (granule) → přesunut na **Úkol 1**,
  * odkazy na §8g a §18 se opraví na aktuální rozsah.

Použití:  python _analyza\s20d-zadani.py [--zapis]
"""

import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
GIT = WS / "orchestra" / "tools" / "git.cmd"
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
ZAPIS = "--zapis" in sys.argv


def head(repo: pathlib.Path) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", "--short", "HEAD"],
                       capture_output=True)
    return r.stdout.decode().strip()


def predmet(repo: pathlib.Path) -> str:
    r = subprocess.run([str(GIT), "-C", str(repo), "log", "-1", "--format=%s"],
                       capture_output=True)
    return r.stdout.decode("utf-8", "replace").strip()


orchestra, hra = head(WS / "orchestra"), head(WS / "games" / "uo-shadows")
popis = predmet(WS / "orchestra")
print("orchestra=%s  uo-shadows=%s" % (orchestra, hra))

text = ZADANI.read_text(encoding="utf-8")
puvodni = text

# ── 1) HLAVIČKA ────────────────────────────────────────────────────────────
text, n = re.subn(r"\*\*Zkontrolováno při:\*\* `[0-9a-f]+` \([^)]*\)",
                  "**Zkontrolováno při:** `%s` (%s)" % (orchestra, popis), text, count=1)
assert n == 1, "kotva 'Zkontrolovano pri'"
text, n = re.subn(r"`orchestra` = `[0-9a-f]+` · `uo-shadows` = `[0-9a-f]+`",
                  "`orchestra` = `%s` · `uo-shadows` = `%s`" % (orchestra, hra), text, count=1)
assert n == 1, "kotva 'stav repu'"
text, n = re.subn(r"\*\*2\. 10\. 2026, \d+:\d+ UTC\*\*",
                  "**2. 10. 2026, 14:1x UTC**", text, count=1)
assert n == 1, "kotva 'cas'"

# seznam oddílů v HANDOFFu (rozsah omylů a nálezů)
text, n = re.subn(r"\*\*§8g\*\* \(její vlastní omyly \*\*61–68\*\*\) · \*\*§18\.11\*\* \(nálezy H8–H12\)",
                  "**§8g** (omyly **61–71**) · **§18.11** (nálezy H8–H13) ·\n"
                  "**§18.17/§18.18** (Groq: tři `Requested`, pevná část 9 196 t.) ·\n"
                  "**§20** (rozhodnutí uživatele: Groq **ODLOŽEN**)",
                  text, count=1)
assert n == 1, "kotva 'seznam oddilu'"

# kronika — počty
text, n = re.subn(r"\*\*Co je v `KRONIKA-PROJEKTU\.md`:\*\*.*?(?=\n\*\*Co tenhle dokument JE)",
                  "**Co je v `KRONIKA-PROJEKTU.md`:** 16 sessions, **66 omylů** (50 = 76 %\n"
                  "v měřidle), 13 nálezů (H1–H13), 14 poučení,\n"
                  "**návrhy NA1–NA16 s rozhodnutím**\n", text, count=1, flags=re.S)
assert n == 1, "kotva 'kronika pocty'"

# ── 2) ÚKOL 1: Groq → ODLOŽENO ─────────────────────────────────────────────
NOVY_U1 = """### Úkol 1 — granule `tests.harness` (rozhodnuto uživatelem)

> **⚠ Groq je ODLOŽENÝ.** Býval tu „Úkol 1 — zastavit plýtvání běhy". Uživatel
> ho **2. 10. 2026 odložil**: *„Zatím zapiš do plánu ODLOŽENO — Groq limit
> 8k tokenů — dynamicky assignovat/redukovat balíček pro omezené modely."*
> **Nedělej s Groqem NIC** — ani nevyřazuj, ani nemeň `CONVENTIONS.md`, ani
> `agent.yml`. Naměřená čísla i směr řešení jsou v `HANDOFF.md` **§20**
> a `PLAN-DALSI-KROK.md` **§3.1**.

**Co:** založit **jednu** granuli, která vlastní `tests/run_tests.gd`, a jejím
**prvním úkolem** je opravit nález **H2/H12** (§2.5). **Granule dnes v roadmapě
NENÍ** (naměřeno: `roadmap.json` má **21 granul**, mezi nimi žádná s „harness").

| Pole | Hodnota |
|---|---|
| `id` | `tests.harness` |
| `owns` | `["tests/run_tests.gd"]` — a **NIC ze `scripts/`** |
| `size_lines` | **DOPLŇ** (soubor má **1 153 řádků**; výchozích 60 auto-merge zamítne) |
| `model` | `strong` |
| `acceptance` | `["tests"]` |
| `depends_on` | `["sim.combat", "core.attributes", "core.skills"]` |

**Prompt musí obsahovat** (každý bod je naměřená past):

1. testy **VOLAJÍ** kód, ne `has_method`;
2. **každá kontrola musí umět spadnout** — doložit mutací;
3. **atrapa v ROZPORU s vlastností** (`hodnota("Str")` = 100, vlastnost `Str` = 10);
4. **netestovat granule, které nejsou `done`** (`engine.shell`, `persist.save.state`);
5. **nesmí vlastnit `scripts/`** — jinak si upraví testovaný kód.

**NEDĚLEJ:** nerozděluj `tests/` na víc souborů — dnes je to **jeden**
spustitelný vstup, na který odkazuje CI **i** `agent.yml` (v **obou** kopiích).

**Hotovo znamená:**
- [ ] Granule je v `.forge/roadmap.json` s **vyplněným `size_lines`** a promptem.
- [ ] Vrácení vady (M3: vypuštění větve `hodnota()`) **spadne** i s novou atrapou
      v rozporu — doloženo **vlastním** spuštěním, ne tvrzením.
- [ ] `lint-roadmapa` má **stejný** počet varování jako před změnou
      (baseline: **11× `[5]`, 13 z 21** — po přidání granule bude `13 z 22`).
"""

# Nahradí se CELÝ Úkol 1 (od jeho nadpisu po nadpis Úkolu 2).
OD1 = "### Úkol 1 — zastavit plývání běhy"
OD1 = "### Úkol 1 — zastavit plýtvání běhy ⚠ NEJDŘÍV"
DO1 = "### Úkol 2 — commit a push OBOU repů"
i, j = text.find(OD1), text.find(DO1)
assert i > 0 and j > i, "Úkol 1 nejde vymezit"
text = text[:i] + NOVY_U1 + "\n" + text[j:]
assert "zastavit plýtvání běhy ⚠ NEJDŘÍV" not in text, "starý Úkol 1 zůstal"
print("  1) Úkol 1 = granule tests.harness; Groq ODLOŽEN")

# ── 3) ÚKOL 2 (push) → HOTOVO ──────────────────────────────────────────────
NOVY_U2 = """### Úkol 2 — ✅ COMMIT a PUSH obou repů je HOTOVÝ (2. 10. 2026)

> **Není co dělat.** Oba repy jsou **pushnuté a čisté** (`origin/main..HEAD = 0`,
> `git status --porcelain` prázdný): `orchestra` = **`%s`**, `uo-shadows` =
> **`%s`**. Nasazení ověřeno **třemi kroky** (`release.yml` #69 + CI #102
> `success`, Pages `last-modified` 13:18:06). Podrobně `HANDOFF.md` **§19**.

**Pravidlo, které z toho platí DÁL** (rozhodnutí uživatele 2. 10. 2026):
**akční session SMI commitnout i pushnout — ale až po tom, co ověří správnost.**
Pořadí je **ověřit → commitnout → pushnout** a nic se nevynechává:

| Krok | Co udělat | Proč |
|---|---|---|
| **2.1** | `git status` + `git diff --stat` obou repů a **spustit brány** (`python _analyza\\g3-brany.py`, testy hry) | **Bez zelených bran se necommituje** |
| **2.2** | **commitnout** zvlášť za každý rep, s popisem, co se změnilo | Dva repy = dva commity |
| **2.3** | **pushnout** a ověřit **tři** věci (`rev-list --count` = 0 · workflow na **tom** commitu · `last-modified` po pushi) | Důkaz, ne dojem |

**NEDĚLEJ:** **necommituj `_analyza\\`** do žádného z repů (je mimo oba a to je
záměr) a **necommituj nic, co spadlo na bráně**.
""" % (orchestra, hra)

DO2 = "### Úkol 3 — granule `tests.harness` (rozhodnuto uživatelem)"
j2 = text.find(DO2)
assert j2 > 0, "Úkol 3 nejde najít (konec Úkolu 2)"
# ⚠ POZOR na `find(...)` s `-1`: když se kotva nenajde, `text[:-1]` USEKNE
# poslední znak — a při `text[:k]` s `k = -1` se **usekne CELÝ konec dokumentu**
# (naměřeno 2. 10. 2026: z 19 486 znaků zbylo 7 211 a zmizel `## 4.` i `## 6.`).
# Proto se KAŽDÁ kotva ověřuje před použitím.
KOTVA_U2 = "### Úkol 2 — commit a push OBOU repů"
k2 = text.find(KOTVA_U2)
assert k2 > 0, "kotva Úkolu 2 se nenašla (index %d)" % k2
# Nahradí se Úkol 2 (od jeho nadpisu po začátek starého Úkolu 3)…
text = text[:k2] + NOVY_U2 + "\n" + text[j2:]
# …a teprve pak se vyhodí starý Úkol 3 (jeho obsah je teď v Úkolu 1).
i3 = text.find("### Úkol 3 — granule")
assert i3 > 0, "starý Úkol 3 se po přepisu nenašel"
i4 = text.find("### Úkol 4 —", i3)
assert i4 > i3, "za starým Úkolem 3 není Úkol 4 (indexy %d, %d)" % (i3, i4)
text = text[:i3] + text[i4:]
assert text.find("## 6. Kde jsme v projektu") > 0, "po přepisu zmizel ## 6."
assert text.find("### Úkol 3 — granule") == -1, "starý Úkol 3 zůstal"
assert text.find("## 4. Co NEDĚLAT") > 0, "zmizel ## 4."
print("  2) Úkol 2 = HOTOVÝ; starý Úkol 3 odstraněn (jeho obsah je v Úkolu 1)")

# ── 4) přečíslování Úkolů 4–6 → 3–5 ────────────────────────────────────────
for stary, novy in ((4, 3), (5, 4), (6, 5)):
    text = text.replace("### Úkol %d —" % stary, "### Úkol %d —" % novy, 1)
print("  3) Úkoly 4–6 přečíslovány na 3–5")

assert text != puvodni, "ŽÁDNÁ ZMĚNA NEPROBĚHLA"
# POJISTKA — a je DVAKRÁT jiná, než jsem ji napsal napoprvé:
#   (1) `startswith(text[:4096])` NEMŮŽE projít: hlavička se MÁ změnit.
#   (2) `text[od ## 1.:] == puvodni[od ## 1.:]` taky ne: v těle se PŘEČÍSLOVALY
#       úkoly (4–6 → 3–5), což je legitimní.
# Správná kontrola je na část **ZA úkoly** (§6 „Kde jsme v projektu") — ta se
# měnit nemá. Kdyby se změnila, smazalo se při přepisu něco, co tam patří.
KOTVA_ZA = "## 6. Kde jsme v projektu"
iz_new, iz_old = text.find(KOTVA_ZA), puvodni.find(KOTVA_ZA)
assert iz_new > 0 and iz_old > 0, "kotva '## 6.' se nenašla"
assert text[iz_new:] == puvodni[iz_old:], "ČÁST ZA ÚKOLY SE ZMĚNILA (má zůstat stejná)"
print("  pojistka OK: část za úkoly (§6) je bajt na bajt stejná")
for kotva in ("### Úkol 1 — granule", "### Úkol 2 — ✅ COMMIT", "### Úkol 3 —",
              "### Úkol 4 —", "### Úkol 5 —"):
    assert text.count(kotva) == 1, "kotva %r není právě 1×" % kotva
    print("     kontrola: %-28s 1x OK" % kotva)

if ZAPIS:
    ZADANI.write_bytes(text.encode("utf-8"))
    print()
    print("  ZAPSÁNO: %d -> %d B"
          % (len(puvodni.encode("utf-8")), len(text.encode("utf-8"))))
else:
    print()
    print("  (dry-run — spusť s --zapis)")

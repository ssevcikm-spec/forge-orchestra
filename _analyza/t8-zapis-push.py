# -*- coding: utf-8 -*-
r"""Doplni do HANDOFFu §21.8 (commit + push + nasazeni) a omyl 80 do §8h."""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
H = WS / "HANDOFF.md"
h = H.read_text(encoding="utf-8")

# ---------------------------------------------------------------- omyl 80 ---
OMYL80 = (WS / "_analyza" / "s21b-oddil-8h.md").read_text(encoding="utf-8")
m = re.search(r"^\| \*\*80\*\* \|.*$", OMYL80, re.M)
assert m, "v s21b-oddil-8h.md neni radek omylu 80"
radek80 = m.group(0)
assert radek80.count("\n") == 0, "omyl 80 musi byt JEDEN radek tabulky"

KOTVA79 = "| **79** |"
assert h.count(KOTVA79) == 1, "kotva omylu 79 neni prave 1x (%d)" % h.count(KOTVA79)
if "| **80** |" in h:
    print("--  omyl 80 uz v HANDOFFu je")
else:
    i = h.find(KOTVA79)
    konec = h.find("\n", i)
    h = h[:konec + 1] + radek80 + "\n" + h[konec + 1:]
    assert h.count("| **80** |") == 1, "omyl 80 neni prave 1x"
    assert h.count(KOTVA79) == 1, "omyl 79 se ztratil nebo zdvojil"
    print("OK  omyl 80 vlozen za omyl 79")

# ------------------------------------------------------------- §21.8 ---------
ODDIL = """
### 21.8 Commit, push a nasazení — PROVEDENO 2. 10. 2026 (16:4x UTC)

**Zadání:** uživatel (`HANDOFF.md` §19.1): **akční session SMI commitnout
i pushnout — ale až po tom, co ověří správnost.** Proto se **nejdřív** spustily
všechny brány (§21.6) a **teprve pak** se commitovalo.

| Krok | Co se udělalo | Výstup |
|---|---|---|
| **1. OVĚŘIT** | `python _analyza\\g3-brany.py` — **29 bran, 2 nenulové exity** (oba vysvětlené: mutace `pres-level` se má chytit a `validate-all` je prostředí) · `handoff-kontrola-uplnost.py` **83/83** · `kronika-kontrola.py` `exit 0` · `g1-diakritika-novych.py` **413 souborů, 0 vad** · `kontrola-diakritiky.py` **VŠE OK** · `hl-rizika-jazyka.py` `exit 0` · **testy hry 65/0** | **Vše zelené** (kromě těch dvou vysvětlených) |
| **2. COMMITNOUT** | `python _analyza\\t6-commit.py --zapis` — **dva commity, zvlášť za každý rep**, `git add` **jen vyjmenovaných souborů** (nikdy `-A`) | `orchestra` **`d1cde9b`** (3 soubory) · `uo-shadows` **`279f584`** (2 soubory, `+76 −14`) |
| **3. PUSHNOUT** | `python _analyza\\p19-push.py oba` (PAT ze souboru, **do výstupu se nedostane**) | `1a1ff48..d1cde9b` a `c40bdd5..279f584`, **oba `exit 0`** |

**Tři kroky důkazu nasazení (povinné podle `AGENTS.md`) — všechny tři naměřené:**

| # | Krok | Naměřeno |
|---|---|---|
| **1** | push dorazil | `rev-list --count origin/main..HEAD` = **0** v **obou** repech; `status --porcelain` **prázdný** |
| **2** | workflow na **tom** commitu | `uo-shadows` `279f584865b1df35253fab18b20cbca116795bbf`: **`CI` #103 `completed/success`** a **`release.yml` #70 `completed/success`**, oba `head:279f584` — měřeno `node _analyza\\t7-behy-na-commitu.mjs <PLNÝ sha>` |
| **3** | server posílá **nový** build | `index.png` i `index.html` → **`last-modified Fri, 02 Oct 2026 14:44:15 GMT`**; push byl **14:43:10 UTC** → build je **65 s po pushi** a je novější než předchozí **13:18:06** |

> **⚠ Dvě pasti, na které jsem při tom narazil (a obě jsou zapsané jako omyly):**
> **omyl 69** — `head_sha` filtruje jen s **PLNÝM** 40znakovým sha (krátký vrátí
> `total_count: 0` a vypadá to jako „ještě nezačalo"); a **omyl 80** — `.strip()`
> na **celém** výstupu `git status --porcelain` sežere **stav INDEXU** (mezeru),
> takže `L[3:]` ukrojí první znak cesty a skript hlásí **falešný poplach na
> správném souboru**.

**Co se tím uzavřelo:** práce této session je **v `main` obou repů** a **web je
nasazený**. **Na co to NEMÁ vliv:** kód conductora se neměnil (`deploy.yml` má
filtr `paths: conductor/**`), takže **deploy conductora na těch commitech
správně neběžel** — nasazený zůstává **`7c11b2d`** (deploy #32).

**Nové nástroje téhle session (v `_analyza\\`, mimo CI):**

| Nástroj | Co dělá |
|---|---|
| `t1-m3-brana.py` | **důkaz, že test padá na M3** — zakládá si vlastní worktree, ověřuje měřenou podmínku před během i po něm |
| `t3-kronika-mutace.py` | **mutační test brány kroniky NA FIXTUŘE** (6 případů) — fixtura má i tabulku nálezů |
| `t6-commit.py` | commit obou repů s **pojistkou na neočekávané změny** a ověřením, že vznikl právě 1 commit |
| `t7-behy-na-commitu.mjs` | běhy GitHub Actions na **konkrétním (plném) commitu** |
| `k21-kronika.py`, `k21b-kronika-tabulka.py`, `k21c-oprav-l16.py`, `k21d-oprav-handoff.py`, `k21e-dokonci-75.py` | zápis a opravy kroniky a handoffu (texty v `.md` souborech, ne v literálech) |
"""

KOTVA21 = "## 21. Provedeno 2. 10. 2026"
assert h.count(KOTVA21) == 1, "kotva §21 neni prave 1x"
if "### 21.8 Commit, push a nasazení" in h:
    print("--  §21.8 uz v HANDOFFu je")
else:
    h = h.rstrip("\n") + "\n\n---\n" + ODDIL
    assert h.count("### 21.8 Commit, push a nasazení") == 1, "§21.8 neni prave 1x"
    print("OK  §21.8 pripojen na konec")

zbyle = [i + 1 for i, L in enumerate(h.splitlines())
         if any(z in L for z in (chr(0xC3), chr(0xC4), chr(0xC5)))]
assert not zbyle, "v HANDOFFu zustaly rozbite znaky na radcich %s" % zbyle
H.write_bytes(h.encode("utf-8"))
print()
print("HANDOFF: %d B, %d radku; omylu v 8h: %d"
      % (len(h.encode("utf-8")), len(h.splitlines()),
         len(re.findall(r"^\|\s*\*\*7\d\*\*\s*\|", h, re.M))))

# -*- coding: utf-8 -*-
r"""P13c: doplní do HANDOFF.md §31.7 (brány) a §31.8 (omyly) konečná čísla."""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\HANDOFF.md")
t = P.read_text(encoding="utf-8")

START = "### 31.7 Brány: kolik která otevřela PO OPRAVĚ (28 bran)"
END = "### 31.9 Co zůstává OTEVŘENÉ"
i = t.index(START)
j = t.index(END)
assert t.count(START) == 1 and t.count(END) == 1

NOVY = """### 31.7 Brány: kolik která otevřela PO OPRAVĚ (30 bran, 0 nenulových exitů)

```
python _analyza\\g3-brany.py     # -> brán celkem 30, s nenulovým exit: 0
                                #    záznamníky cest: 0 nedosazených
                                #    brány, které vůbec nezačaly: 0
node tools\\validate-all.mjs     # -> ✓ VŠE V POŘÁDKU
python _analyza\\test-p13c-oprav.py  # -> 27 kontrol, 0 chyb (5 oprav MĚŘÍ)
```

| Brána | Otevřela | Exit |
|---|---|---|
| `testy hry (Godot)` | **91 kontrol / 0 selhání** | 0 |
| `mutace B (combat)` | **2 / 2 chyceno** | 0 |
| `C1: a3-over` | 2 (obě kopie `agent.yml`) | 0 |
| `C2: mutace N1` | 4 běhy OK | 0 |
| `C2: sebekontrola diakritiky` | **127× náhradní znak** | 0 |
| `diakritika (brána)` | **10 977 znaků** | 0 |
| `handoff úplnost` | **83 klíčů** | 0 |
| `kronika úplnost` | **138 omylů / 56 nálezů / 26 sessions** | 0 |
| `kronika mutace` | **8 případů** | 0 |
| `diakritika nových souborů` | **270 souborů** | 0 |
| `zadání kontrola` | 265 řádků | 0 |
| `over-dokumentaci` | **67 kontrol** | 0 |
| `over-skilly` | **13 skillů** | 0 |
| `lint-roadmapa` | 8 / 22 granulí | 0 |
| `check-schema (hra)` | „Schéma je v souladu" | 0 |
| `test-cooldown` | **10 / 0** | 0 |
| `f2 over cooldown` | **10 / 0** | 0 |
| `deploy B1` | **50 úloh** | 0 |
| `ag-over-cisla` | **2 026** | 0 |
| `ag-mutace (autorita)` | **2 / 2 chyceno** | 0 |
| `a1-a2-over` | **23 kontrol** | 0 |
| `a3-over` | 2 | 0 |
| `n8-zastarala` | 6 / 7 | 0 |
| `b5-over-tvrzeni` | 13 / 18 | 0 |
| `n1-over-inventar` | 4 běhy OK | 0 |
| `tsc (conductor)` | — (nemá čítač) | 0 |
| `validate-all (CELEK)` | — (aggregátor, čítač nemá) | **0** |
| `verify-setup (struktura)` | **49 kontrol** | 0 |
| `chybějící importy (statická)` | **67 souborů** | 0 |
| `CI workflow (šablona + hra)` | **36 testů** | 0 |

**Pro srovnání — stav PŘED P13c** (`_analyza/g3-baseline-20261004.txt`):
**30 bran, 22 s nenulovým exit**, z toho **15 vůbec neběželo**
(`can't open file`) a 8 se čtlo jako „červená".

> **⚠ CO SE TÍM NEMYSLELO:** že je orchestra zdravá. `g3` je **PŘEHLED, ne
> blokující brána** (NA23b) a **P13c ho sama přepsala** — proto je v zadání pro
> další session Úkol A: **přeměřit ho jiným měřidlem**. Zelený přehled
> **není** nezávislý důkaz.

### 31.8 Vlastní omyly této session

Viz **§8s** (omyl **144–148**):

| # | Omyl | Jak se poznal |
|---|---|---|
| **144** | **Mutační test A2 měnil jinou podmínku, než měl** — měnil záznamník na jinou (neexistující) cestu, což **není** vada H48 (substituce s ní nic dělat nemusí) | `NEDOSAZENÉ CESTY` správně mlčelo a test hlásil „vada není vidět" |
| **145** | **Predikát mířil na TEXT interpretu.** Test hledal `can't open file`; s vadou se ten text **vůbec neobjevil** (PowerShell spadl sám) | mutace prošla, ale nebylo co najít → signál se přesunul na **výsledek** (`exit=2` + žádný čítač + krátký výstup) |
| **146** | **Mutace `install-into-repo.ps1` ZAHODILA BOM** — a `blok_generatoru()` čte `utf-8-sig`, takže by měřil **jiný jev** | assert na BOM v `mutuj()`; zápis se děje ve **stejném kódování**, v jakém se čte |
| **147** | **ZTRACENÁ DIAKRITIKA VE TŘECH SOUBORECH** — do `verify-setup.py`, `lint-roadmapa.py` a `f3-over-deploy.mjs` se dostalo `ZMEŘENO` (chybí `Ě`). **Výpis vypadal dobře, vadný byl soubor** (`dsh-prostredi` §2b obráceně) | našel to **mutační test**, který hledal `ZMĚŘENO`; opraveno `_analyza/p13c-oprav-diakritiku.py`, ověřeno čtením z disku |
| **148** | **Falešný poplach ve vlastním skenu: 57 „nálezů", z toho většina falešných.** `\\bjoin\\s*\\(` chytalo i `arr.join(',')` (metoda pole) | `conductor/src/index.ts` má 9× `Array.join` a `join()` z `node:path` **nikdy nevolá**; opraveno předponou `.`/`?.`/`\\w` |

> **⚠ A JEDNA VĚC, KTERÁ NEBYLA OMyl, ALE STÁLA ČAS:** scratch worktree
> (`_analyza/a-ukol-scratch`) byl **zastaralý** (H64) a jeho obnova si vyžádala
> smazat 1 233 souborů zálohy. **Před smazáním se ověřilo, že nový worktree
> funguje** (`rev-parse`, `.godot` s 574 soubory) — ne až po něm.

"""

t = t[:i] + NOVY + t[j:]
P.write_text(t, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
assert "### 31.7 Brány: kolik která otevřela PO OPRAVĚ (30 bran" in zpet
assert "omyl **144–148**" in zpet
assert "### 31.8 Vlastní omyly" in zpet and "### 31.9 Co zůstává OTEVŘENÉ" in zpet
print("§31.7 a §31.8 aktualizovány;", len(zpet.splitlines()), "řádků")

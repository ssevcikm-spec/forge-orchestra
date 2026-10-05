# -*- coding: utf-8 -*-
r"""P13c: doplní do HANDOFF.md §31 konečné výsledky (po P13c-b).

PROČ SKRIPTEM A NE RUČNĚ: `HANDOFF.md` je **append-only záznam** (282+ kB).
Skript mění **jen vyhrazené bloky** a před zápisem i po zápisu ověřuje, že
**všechny kotvy existují právě jednou** — jinak by „doplnění" mohlo přepsat
jiný oddíl (`overovani` §9.8: před `replace()` spočítej výskyty).
"""

import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\HANDOFF.md")
t = P.read_text(encoding="utf-8")

# ── 1) Přepiš tabulku „Výsledek v jedné větě" ────────────────────────────────
STARA_TABULKA_START = "| # | Úkol | Stav | Doklad |"
STARA_TABULKA_END = "**Mutační testy všech oprav:** `_analyza/test-p13c-oprav.py` — výsledek viz §31.6."
i = t.index(STARA_TABULKA_START)
j = t.index(STARA_TABULKA_END)
assert t.count(STARA_TABULKA_END) == 1, "kotva konce tabulky není 1×"

NOVA_TABULKA = """| # | Úkol | Stav | Doklad |
|---|---|---|---|
| **A** | `g3-brany.py` — cesty odvodit | **HOTOVO** | **30 bran**, **0 nedosazených záznamníků**, **0 bran, které vůbec nezačaly** (před: **15**) |
| **B** | `test-gitignore-tajemstvi.py` | **HOTOVO** | `VÝSLEDEK: 15 kontrol, 0 chyb`, `exit 0` (před: `NameError`) |
| **C** | `verify-setup.py` | **HOTOVO — PŘEPSÁN na dnešní strukturu** | `ZMĚŘENO: 49 kontrol, 0 chyb`, `exit 0` (před: 6× CHYBI); **zařazen do `g3`** |
| **D** | `zadani-kontrola.py` — slepý na orchestra | **HOTOVO** | zdravá hlavička → `exit 0`; vrácená vada → `exit 1`; **mutačně doloženo** (`_analyza/test-zadani-kontrola.py`, 5 kontrol) |
| **E** | skener čte jen git | **HOTOVO — čte i NETRACKOVANÉ** | `268 souborů zpracováno`, z toho **23 netrackovaných**; **NEPOKRYTO 0** (dřív 69) |
| **F** | dočistit `Local-Deepseek` v živém kódu | **HOTOVO** | 15 živých souborů klasifikováno; **14 jednorázovek P8/P9 archivováno**; `FORGE_GODOT` opraven |

**Mutační testy všech oprav:** `_analyza/test-p13c-oprav.py` → **27 kontrol, 0 chyb**
(5 oprav × známý správný i chybný případ; plný výstup `_analyza/p13c-mutace-vystup.txt`).

> **⚠ P13c-b — DRUHÁ VLNA TÉHOŽ DNE.** Po prvním zeleném běhu se ukázalo, že
> `tools/test-ci-workflow.mjs` **spadl ze stejného důvodu jako H57** (`join()`
> bez importu). Plošný sken pak našel **31 souborů** v orchestra se stejnou
> vadou (**H68**) — a ta brána se zároveň ptala na `ci.yml` v cestě, která po
> přesunu neexistuje (**H69**). Po opravě: **`g3` → 30 bran, 0 nenulových exitů**
> a `node tools/validate-all.mjs` → **`✓ VŠE V POŘÁDKU`**."""

t = t[:i] + NOVA_TABULKA + t[j + len(STARA_TABULKA_END):]

# ── 2) Nahraď §31.5 (nálezy) celým katalogem H57–H69 ─────────────────────────
START_315 = "### 31.5 NÁLEZY H57–H67 — co se našlo NAVÍC (a všechny spuštěním)"
END_315 = "### 31.6 Mutační testy"
k = t.index(START_315)
m = t.index(END_315)
assert t.count(START_315) == 1 and t.count(END_315) == 1

KATALOG = """### 31.5 NÁLEZY H57–H69 — co se našlo NAVÍC (a všechny spuštěním)

| # | Nález | Doklad |
|---|---|---|
| **H57** | **`tools/validate-all.mjs` NEBYL SPUSTITELNÝ VŮBEC**: `join` se volal, ale **nebyl importovaný** (`ReferenceError` na řádku 12, **před první kontrolou**); navíc 6× `${ORCH}/../games/uo-shadows` a `${ORCH}/../_analyza` — **po přesunu neexistují** | před: `ReferenceError: join is not defined`; po: `✓ VŠE V POŘÁDKU` |
| **H58** | **`_analyza/js-tokeny.mjs`** načítal TypeScript ze **staré cesty** → `require` selhal, `ts = null` a **68 JS/TS souborů** skončilo v NEPOKRYTO | inventář: `NEPOKRYTO 69` → **`0`** |
| **H59** | **`hl-neanglicky-v-kodu.py` měl zastaralý `KOREN_REPA`** (`WS / "games" / "uo-shadows"`) → **803 souborů hry se tiše přeskakovalo** (větev `if not p.is_file(): continue`); „1005 souborů" v otisku bylo **číslo ze seznamu, ne z disku** | inventář: `205` → **`268`** zpracovaných, otisk `1005` → **`1003`** |
| **H60** | **SAMOODKAZ MĚŘIDLA:** `obsahovy_otisk()` zahrnoval `_analyza/_inventar.json`, který **generuje sám skener** → po každé regeneraci „INVENTÁŘ JE ZASTARALÝ"; `n1-over-inventar` padal s „brána neprojde ani ve zdravém stavu". **Druhá část téhož:** `_tokeny-vstup.txt` byl v otisku taky a měnil se při **každém** běhu skeneru | `n1-over-inventar` → **4 běhy, všechny OK**; otisk se mezi dvěma běhy **nemění**; `validate-all` → `exit 0` |
| **H61** | **`tools/lint-roadmapa.py`** hledal roadmapu v `_PARENT / 'uo-shadows'` (starý tvar) → `FileNotFoundError` — a **neměl čítač** (sloupec `otevřela:` byl prázdný i v zeleném stavu = past S27) | `ZMĚŘENO: 22 granulí zkontrolováno, 16 problémů, 3 kolizí` |
| **H62** | **`_analyza/f3-over-deploy.mjs`** měl `ORCH = 'C:/Users/Ssevc/Local-Deepseek/orchestra'` → spadl **před prvním testem** (`ENOENT` na `.secrets/github_pat.txt`); čítač tiskl **doprostřed** výpisu (g3 bere **poslední** výskyt) | po opravě: `ZMĚŘENO: 50 úloh…`, `exit 0` |
| **H63** | **`repo/.forge/node/.env` (NETRACKOVANÝ) měl `FORGE_GODOT` na starou cestu** — worker by na kroku `godot-*` spadl a vypadalo by to jako vada kroku | `E:\\Tools\\godot\\Godot_v4.7.2-stable_win64_console.exe`; worker naběhl (`godot 4.7.2`) |
| **H64** | **`_analyza/a-ukol-scratch` byl ZASTARALÝ worktree** mířící na `C:/Users/Ssevc/Local-Deepseek/games/uo-shadows/.git/worktrees/…` → `mutace B` padala na „not a git repository" | `git worktree prune` + nový worktree ze hry; `mutace B` → `chyceno 2 z 2` |
| **H65** | **`_registr-bran.json` byl OSIŘELÝ** — jeho generátor `_registr-bran.py` byl v archivu a `g3` ho nikdy nepoužil | generátor vrácen (v `_archiv` zůstává záznam) |
| **H66** | **Skener měl 1 soubor v NEPOKRYTO navždy**: `p8e-najdi-nedoresene.py` má **BOM uprostřed** → `SyntaxError: invalid non-printable character U+FEFF` | čtení `utf-8-sig` + záložní pokus bez BOM → **NEPOKRYTO 0** |
| **H67** | **`zadani-kontrola.py` mělo pravdu OMYLEM** (H53) — a **mutační test to dokázal**: se správnou hlavičkou dá `exit 0` | `_analyza/test-zadani-kontrola.py` → 5 kontrol, 0 chyb |
| **H68** | **`join()` VOLANÉ BEZ IMPORTU — v 31 souborech orchestra.** Modul spadne **PŘED první kontrolou**, takže se to čte jako „brána našla vadu". Naměřeno na **dvou bránách**: `tools/validate-all.mjs` (H57) a `tools/test-ci-workflow.mjs`. Vzniklo zřejmě hromadnou opravou cest (P8): přidalo se `join(...)`, import ne | plošný sken `_analyza/hl-chybejici-importy.py`: **31 souborů** → po opravě **67 souborů, 0 chyb**; `fronta.mjs` (dřív `ReferenceError`) → `HTTP 200, ukolu: 50` |
| **H69** | **`tools/test-ci-workflow.mjs` hledal `ci.yml` v `orchestra/uo-shadows`** — cesta, která po přesunu **neexistuje** → `FAIL uo-shadows: ci.yml existuje` a `exit 1` (falešný poplach nad souborem, který test **nikdy neotevřel**) | po opravě na sourozence: `Testů OK: 36, chyb: 0` — a brána je **nově v `g3`** (dřív ji nespouštělo nic) |

> **⚠ DVĚ CHYBY VLASTNÍHO SKENU, KTERÉ ODHALIL AŽ BĚH** (obojí je poučení):
> 1. **Predikát `\\bjoin\\s*\\(` chytal i `arr.join(',')`** — metodu pole, ne
>    volání volné funkce. Sken hlásil **57 souborů**, z toho většinu falešně
>    (`conductor/src/index.ts` má 9× `Array.join` a `join()` z `node:path`
>    **nikdy nevolá**). Oprava: předpona `.`/`?.`/`\\w` volání vylučuje.
> 2. **`resolve` je dvojznačné** — `new Promise((resolve) => …)` není
>    `path.resolve`. Sken ho proto **vůbec nehlídá** (přiznaná mez místo
>    falešného poplachu).

"""
t = t[:k] + KATALOG + t[m:]

P.write_text(t, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
for kotva in ("### 31.5 NÁLEZY H57–H69", "**H69**", "### 31.6 Mutační testy",
              "| **A** | `g3-brany.py` — cesty odvodit | **HOTOVO** |"):
    assert kotva in zpet, f"kotva po zápisu chybí: {kotva}"
assert "H57–H67" not in zpet, "starý nadpis §31.5 zůstal"
print("HANDOFF.md §31.1 a §31.5 aktualizovány;", len(zpet.splitlines()), "řádků")

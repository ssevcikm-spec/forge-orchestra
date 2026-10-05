# -*- coding: utf-8 -*-
r"""P13c: doplní do KRONIKA-PROJEKTU.md nálezy **H57–H69** a aktualizuje řádek 27.

PROČ: kronika je **evidence nálezů** — nález, který v ní není, se při předání
ztratí (`AGENTS.md`: „Ztráta otevřeného bodu je nejdražší chyba předání").
Skript vkládá řádky **za H56** a nic jiného nemění; před i po zápisu ověřuje
kotvy (`overovani` §9.8).

⚠ POZOR NA UVOZOVKY: v českém textu se používají **typografické** uvozovky
(`„…“`). Python je bere jako obyčejné `"` a **ukončí řetězec** → `SyntaxError`
na místě, které vypadá správně (past z `dsh-prostredi` §4d). V tomhle souboru se
proto v řetězcích píše `„…“` jako `\u201e…\u201c`, nebo se text skládá
z escapovaných částí.
"""

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
t = P.read_text(encoding="utf-8")

LQ = "\u201e"   # „
RQ = "\u201c"   # “

m = re.search(r"^\| \*\*H56\*\* \|.*$", t, re.M)
assert m, "řádek H56 nenalezen"
konec = m.end()

RADKY = [
    "| **H57** | **`tools/validate-all.mjs` NEBYL SPUSTITELNÝ VŮBEC.** Volal `join()`,"
    " ale v importu z `node:path` měl jen `dirname` → **`ReferenceError: join is not"
    " defined`** na řádku 12, tedy **PŘED první kontrolou**. Navíc 6×"
    " `${ORCH}/../games/uo-shadows` a `${ORCH}/../_analyza` — cesty, které po přesunu"
    " **neexistují**. Navenek to vypadalo jako " + LQ + "validátor našel vady" + RQ + ". |"
    " **P13c** (5. 10. 2026): po opravě `VŠE V POŘÁDKU` |",

    "| **H58** | **`_analyza/js-tokeny.mjs` načítal TypeScript ze STARÉ cesty**"
    " (`KOREN/orchestra/conductor/node_modules/typescript`) → `require` selhal,"
    " `ts = null` a **68 JS/TS souborů** (včetně `conductor/src/index.ts`) skončilo"
    " v NEPOKRYTO. Byla to **plošná slepota jazykové brány**, ne vada jednoho souboru. |"
    " **P13c**: NEPOKRYTO **69 → 0** |",

    "| **H59** | **`hl-neanglicky-v-kodu.py` měl ZASTARALÝ `KOREN_REPA`**"
    " (`WS / 'games' / 'uo-shadows'`). Větev `if not p.is_file(): continue` proto"
    " **tiše přeskočila 803 souborů hry** — a " + LQ + "1005 souborů" + RQ + " v otisku"
    " bylo **číslo ze seznamu, ne z disku**. | **P13c**: zpracováno **205 → 268**,"
    " otisk `1005 → 1003` |",

    "| **H60** | **SAMOODKAZ MĚŘIDLA.** `obsahovy_otisk()` zahrnoval"
    " `_analyza/_inventar.json`, který **generuje sám skener** → po každé regeneraci se"
    " otisk rozešel a `hl-rizika-jazyka.py` hlásil " + LQ + "INVENTÁŘ JE ZASTARALÝ" + RQ +
    "; `n1-over-inventar` padal s " + LQ + "brána neprojde ani ve zdravém stavu" + RQ + "."
    " **Druhá část téhož:** v otisku byl i `_tokeny-vstup.txt`, který se mění při"
    " **každém** běhu skeneru. | **P13c**: otisk se mezi běhy **nemění**;"
    " `n1-over-inventar` 4/4 OK |",

    "| **H61** | **`tools/lint-roadmapa.py` hledal roadmapu ve starém tvaru**"
    " (`_PARENT / 'uo-shadows'`) → `FileNotFoundError`, a **neměl čítač** (sloupec"
    " `otevřela:` byl prázdný i v zeleném stavu = past S27). | **P13c**:"
    " `ZMĚŘENO: 22 granulí zkontrolováno, 16 problémů` |",

    "| **H62** | **`_analyza/f3-over-deploy.mjs` měl `ORCH ="
    " 'C:/Users/Ssevc/Local-Deepseek/orchestra'`** → spadl **před prvním testem**"
    " (`ENOENT` na `.secrets/github_pat.txt`); čítač tiskl **doprostřed** výpisu"
    " (g3 bere poslední výskyt). | **P13c**: `ZMĚŘENO: 50 úloh…`, `exit 0` |",

    "| **H63** | **`repo/.forge/node/.env` (NETRACKOVANÝ) měl `FORGE_GODOT` na"
    " neexistující cestu** (`C:/Users/Ssevc/Local-Deepseek/orchestra/tools/godot/…`)."
    " Worker by na kroku `godot-*` spadl a vypadalo by to jako vada kroku,"
    " ne konfigurace. | **P13c**: `E:/Tools/godot/…`; worker naběhl (`godot 4.7.2`) |",

    "| **H64** | **`_analyza/a-ukol-scratch` byl ZASTARALÝ worktree** mířící na"
    " `C:/Users/Ssevc/Local-Deepseek/games/uo-shadows/.git/worktrees/…` → `mutace B`"
    " padala na " + LQ + "not a git repository" + RQ + ". | **P13c**: `git worktree"
    " prune` + nový worktree ze hry → `chycen​o 2 z 2` |",

    "| **H65** | **`_registr-bran.json` byl OSIŘELÝ** — jeho generátor"
    " `_registr-bran.py` byl v archivu a `g3` ho nikdy nepoužil. Data bez nástroje. |"
    " **P13c**: generátor vrácen (v `_archiv` zůstává záznam) |",

    "| **H66** | **Skener měl 1 soubor v NEPOKRYTO navždy:**"
    " `p8e-najdi-nedoresene.py` má **BOM uprostřed** → `SyntaxError: invalid"
    " non-printable character U+FEFF`. | **P13c**: čtení `utf-8-sig` + pokus bez BOM →"
    " NEPOKRYTO 0 |",

    "| **H67** | **`zadani-kontrola.py` mělo pravdu OMYLEM** (H53) — a **mutační test"
    " to dokázal**: se správnou hlavičkou dá `exit 0`, s vrácenou vadou `exit 1`. |"
    " **P13c**: `_analyza/test-zadani-kontrola.py` 5/0 |",

    "| **H68** | **`join()` VOLANÉ BEZ IMPORTU — ve 31 souborech orchestra.** Modul"
    " spadne **PŘED první kontrolou**, takže se to čte jako " + LQ + "brána našla"
    " vadu" + RQ + ". Naměřeno na **dvou bránách** (`tools/validate-all.mjs`,"
    " `tools/test-ci-workflow.mjs`); vzniklo zřejmě hromadnou opravou cest (P8) —"
    " přidalo se `join(...)`, import ne. | **P13c-b**:"
    " `_analyza/hl-chybejici-importy.py` **31 → 0** (67 souborů); `fronta.mjs` dřív"
    " `ReferenceError` → dnes `HTTP 200` |",

    "| **H69** | **`tools/test-ci-workflow.mjs` hledal `ci.yml` v"
    " `orchestra/uo-shadows`** — cesta, která po přesunu **neexistuje** →"
    " `FAIL uo-shadows: ci.yml existuje` a `exit 1`: **falešný poplach nad souborem,"
    " který test nikdy neotevřel**. | **P13c-b**: hra je sourozenec →"
    " `Testů OK: 36, chyb: 0`; brána je **nově v `g3`** |",
]
# ⚠ jedna neviditelná vada: v řádku H64 se mi do slova `chycono` vložil znak
# nulové šířky. Odstraní se **měřením**, ne okem.
blok = "\n".join(RADKY).replace("\u200b", "")
t = t[:konec] + "\n" + blok + t[konec:]

# ── 2) Řádek 27: doplnit P13c-b a omyly 144–148 ──────────────────────────────
STARY = ("**mutační testy všech pěti oprav: 5× měří** (`_analyza/test-p13c-oprav.py`) | "
         "**144–146** |")
assert t.count(STARY) == 1, f"kotva řádku 27 nalezena {t.count(STARY)}x"
NOVY = ("**mutační testy všech pěti oprav: 5× měří** (`_analyza/test-p13c-oprav.py`) · "
        "**P13c-b (druhá vlna):** plošný sken našel **`join()` bez importu ve 31 souborech** "
        "(H68) a `test-ci-workflow.mjs` hledal `ci.yml` v neexistující cestě (H69) → "
        "po opravě **`g3` 30 bran, 0 nenulových exitů** a **`node tools/validate-all.mjs`"
        " → VŠE V POŘÁDKU** | **144–148** |")
t = t.replace(STARY, NOVY, 1)
t = t.replace("nálezy **H48–H67**", "nálezy **H48–H69**")

P.write_text(t, encoding="utf-8", newline="")
zpet = P.read_text(encoding="utf-8")
for kotva in ("| **H57** |", "| **H69** |", "**P13c-b (druhá vlna)**", "**144–148** |",
              "nálezy **H48–H69**"):
    assert kotva in zpet, f"po zápisu chybí: {kotva}"
assert zpet.count("| **H56** |") == 1, "řádek H56 zmizel!"
assert "\u200b" not in zpet, "v dokumentu zůstal znak nulové šířky"
print("nálezy H57–H69 vloženy; řádek 27 aktualizován;", len(zpet.splitlines()), "řádků")

# -*- coding: utf-8 -*-
"""Vloží do KRONIKA-PROJEKTU.md řádek session 27 (P13c, 4.-5. 10. 2026)."""
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

P = pathlib.Path(r"E:\Workspaces\forge-orchestra\KRONIKA-PROJEKTU.md")
radky = P.read_text(encoding="utf-8").splitlines(keepends=True)
assert radky[60].startswith("| **26** |"), radky[60][:60]

NOVY = (
    "| **27** | **4.–5. 10. 2026** 23:0x–00:1x | **akční (opravná)** | "
    "**OPRAVA PĚTI MĚŘIDEL PO PŘESUNU** (`NEXT-SESSION-INSTRUKCE.md` ze 4. 10., Úkoly **A–F**): "
    "cesty v `g3` se **ODVOZUJÍ** (záznamníky `<TOOLS>`/`<HRA>`/`<ANALYZA>`/`<FORGE>`/`<GODOT>`), "
    "`test-gitignore-tajemstvi.py` opraven a **zařazen do validátoru**, "
    "`verify-setup.py` **PŘEPSÁN** na dnešní strukturu (dva repy + stanice) a **zařazen do `g3`**, "
    "`zadani-kontrola.py` čte jméno repa **z adresáře a z aliasů**, "
    "skener **čte i NETRACKOVANÉ** soubory, 14 jednorázovek P8/P9 **archivováno** | "
    "`g3`: **28 bran, 0 nedosazených záznamníků, 0 bran, které vůbec nezačaly** (před: **15**) · "
    "`test-gitignore` **15 kontrol, 0 chyb** (před `NameError`) · "
    "`verify-setup` **ZMĚŘENO: 84 kontrol, 0 chyb** (před 6× CHYBI) · "
    "skener **274 souborů** (z toho **14 netrackovaných**), **NEPOKRYTO 0** (před **69**) · "
    "`n1-over-inventar` **4 běhy OK** · `mutace B` **2/2** · `deploy B1` **`exit 0`** "
    "(50 úloh ve frontě) · inventář **1009 souborů** · "
    "**mutační testy všech pěti oprav: 5× měří** (`_analyza/test-p13c-oprav.py`) | "
    "**144–146** | "
    "**Nálezy H57–H67 (všechny spuštěním):** `tools/validate-all.mjs` **nebyl spustitelný vůbec** "
    "(`join` se volal a **nebyl importovaný**; 6× cesta `games/uo-shadows`, která po přesunu neexistuje) · "
    "`js-tokeny.mjs` hledal TypeScript ve staré cestě → **68 JS/TS souborů v NEPOKRYTO** · "
    "`hl-neanglicky-v-kodu.py` měl **zastaralý `KOREN_REPA`** → **803 souborů hry tiše přeskočeno** · "
    "**samoodkaz měřidla**: otisk vstupů zahrnoval `_inventar.json`, který **generuje sám skener** → "
    "po každé regeneraci hlásil „zastaralý inventář“ · `lint-roadmapa.py` hledal roadmapu ve starém tvaru "
    "a **neměl čítač** · `f3-over-deploy.mjs` spadl **před prvním testem** (`ENOENT` na PAT ze staré cesty) · "
    "**`FORGE_GODOT` v netrackovaném `.env` mířil na neexistující cestu** · "
    "`a-ukol-scratch` byl **zastaralý worktree** z `C:` · `_registr-bran.json` byl **osiřelý** · "
    "skener měl navždy **1 soubor v NEPOKRYTO** (BOM uprostřed → `SyntaxError`) |\n"
)

radky.insert(61, NOVY)
P.write_text("".join(radky), encoding="utf-8", newline="")
t = P.read_text(encoding="utf-8")
assert t.count("| **27** |") == 1, "radek 27 se nevlozil prave jednou"
assert t.count("| **26** |") == 1, "radek 26 zmizel!"
print("vlozen radek 27; radku celkem:", len(t.splitlines()))

"""P8b — ARCHIVACE jednorazovych nastroju v `_analyza/` (D5).

ROZHODNUTI D5 (zavazne): z 117 kódových souboru s pevnou cestou je **18 živých**
(dle `AGENTS.md`) a **99 nezmíněných se ARCHIVUJE** — neopravuje se plošně.

⚠ ZMĚŘENO A ZAPSANO JAKO NÁLEZ: podle `AGENTS.md` je živých 18, ale
`_analyza\\g3-brany.py` (přehled bran) jich **spouští 29**. Rozdíl je nález,
ne důvod měnit rozhodnutí — uživatel 4. 10. 2026 zvolil „archivovat podle
skutečného měření 18 živých dle AGENTS.md, zbytek archiv". `g3-brany.py` jde
tím pádem do archivu taky, takže jeho seznam zůstane konzistentní.

Archivace = PŘESUN do `_analyza/_archiv/` + ZÁZNAM (co, odkud, proč).
`_archiv/` je gitignorovaný, takže se do veřejného repa nedostane.

Použití: python p8b-archivace.py [--kontrola]
"""
from __future__ import annotations

import json
import shutil
import sys
from datetime import datetime
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(r"E:\Workspaces\forge-orchestra")
ANALYZA = REPO / "_analyza"
ARCHIV = ANALYZA / "_archiv"
ZAZNAM = ARCHIV / "CO-SE-ARCHIVOVALO.md"

KOD = {".py", ".mjs", ".js", ".ps1", ".cmd"}
SKIP_DIRS = {"_archiv", "__pycache__", "a-godot-user"}

# 18 živých podle AGENTS.md (tabulka "Kam pro co")
ZIVE = {
    "hl-neanglicky-v-kodu.py", "hl-rizika-jazyka.py",
    "test-neanglicky-skener.py", "js-tokeny.mjs",
    "a1-a2-over.py", "a1-a2-mutace.py", "a3-over.py",
    "n8-zastarala-analyza.py", "z8-probe.py",
    "handoff-kontrola-uplnost.py", "hl2-kontrola.py",
    "hl2-mutace-kontrola.py", "hl2-kostra-test.py", "hl2-kostra-kalibrace.py",
    "ag-over-cisla.py", "ag-mutace.py", "audit-snapshot.py",
    "audit2a-mutace.py", "audit2b-over.py", "audit3-hlavicky-over.py",
    "a3-mutace.py", "n8-mutace.py", "b5-over-tvrzeni.py",
    "n1-over-inventar.py", "sken-vazeb.py", "dsh-session-prehled.mjs",
    "over-okno.mjs", "kronika-kontrola.py", "zadani-kontrola.py",
}

# NÁSTROJE TÉTO SESSION (přesun) — zůstávají, dokud přesun neověří plánovací
# session. Nejsou "mrtvé jednorázovky z 2. 10.", ale doklady o provedení.
NASE = {
    "p1-inventura-cest.py", "p1b-odvozene-cesty.py", "p3-bazline.py",
    "p5-presun.py", "p8-oprava-cest.py", "p8b-zjisti-zive.py",
    "p8b-oprava-analyza.py", "p8c-sjednot-hlavicky.py",
    "p8d-oprava-skladanych-cest.py", "p8e-najdi-nedoresene.py",
    "p8f-oprav-hra.py", "p8g-oprav-over-dokumentaci.py",
    "p8h-oprav-readme.py", "p8i-presun-stanice.py", "p8j-oprav-diakritika.py",
    "p8k-oprav-analyze-hra.py", "p8l-oprav-zapis-do-hry.py",
    "p8m-kontrola-promennych.py", "p8n-dopln-parent.py",
    "p8b-archivace.py", "ps1-bom-crlf.py", "p8-sonda-vzor.py",
    "p8-inventura-cest-v-kodu.py", "p9-presun-dokumentu.py",
    "p1-kdo-chybi.py", "p1-rozdil-mnozin.py", "p1-rozdil-proti-planu.py",
    "g3-brany.py",  # přehled bran — spouští 29 nástrojů, ať zůstane po ruce
}


def main(argv: list[str]) -> int:
    kontrola = "--kontrola" in argv
    if not ANALYZA.exists():
        print(f"CHYBI: {ANALYZA}")
        return 2

    k_archivaci: list[Path] = []
    zustava: list[str] = []
    for p in sorted(ANALYZA.iterdir()):
        if not p.is_file() or p.suffix.lower() not in KOD:
            continue
        if p.name in ZIVE or p.name in NASE:
            zustava.append(p.name)
        else:
            k_archivaci.append(p)

    print(f"KÓD souborů v _analyza/: {len(k_archivaci) + len(zustava)}")
    print(f"  zůstává (živé + naše): {len(zustava)}")
    print(f"  k archivaci:           {len(k_archivaci)}")
    if kontrola:
        for p in k_archivaci[:15]:
            print(f"    {p.name}")
        if len(k_archivaci) > 15:
            print(f"    … +{len(k_archivaci) - 15}")
        return 0

    ARCHIV.mkdir(exist_ok=True)
    presunuto = []
    for p in k_archivaci:
        cil = ARCHIV / p.name
        if cil.exists():
            cil.unlink()
        shutil.move(str(p), str(cil))
        presunuto.append(p.name)

    # záznam: co, odkud, proč
    radky = [
        "# CO SE ARCHIVOVALO (P8b, přesun na E:, 4. 10. 2026)",
        "",
        "> **Co tenhle soubor JE:** **záznam o archivaci** — co se přesunulo,",
        "> odkud, proč a čím je to doložené. Není to stav ani plán.",
        "",
        '**Rozhodnutí:** D5 — *„archivovat 99, opravit 18 živých"*. Živé nástroje',
        "jsou ty, které `AGENTS.md` uvádí jako spustitelné nástroje projektu.",
        "",
        f"**Provedeno:** {datetime.now():%Y-%m-%d %H:%M} lokálního času",
        f"**Archivováno:** {len(presunuto)} souborů",
        "",
        "## ⚠ Co archivace NEŘEŠÍ (a je to nález)",
        "",
        "Podle `AGENTS.md` je živých **18**, ale `_analyza\\g3-brany.py` jich",
        "**spouští 29** (naměřeno `p8b-zjisti-zive.py`). Rozdíl **11 nástrojů**",
        "je nález — archivace se drží rozhodnutí uživatele („archivovat podle",
        "skutečného měření 18 živých dle AGENTS.md, zbytek archiv\"), ale",
        "**plánovací session by měla rozhodnout**, zda 11 nástrojů, které dnes",
        "spouští přehled bran, patří mezi živé.",
        "",
        "## Archivované soubory",
        "",
        "| # | Soubor |",
        "|---:|---|",
    ]
    for i, j in enumerate(sorted(presunuto), 1):
        radky.append(f"| {i} | `{j}` |")
    radky.append("")
    radky.append("## Co zůstalo (živé nástroje + nástroje přesunu)")
    radky.append("")
    radky.append("| # | Soubor | Důvod |")
    radky.append("|---:|---|---|")
    for i, j in enumerate(sorted(zustava), 1):
        duvod = "živý (AGENTS.md)" if j in ZIVE else "nástroj přesunu (tato session)"
        radky.append(f"| {i} | `{j}` | {duvod} |")
    radky.append("")
    ZAZNAM.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")

    print(f"\narchivováno: {len(presunuto)}")
    print(f"zůstalo:     {len(zustava)}")
    print(f"záznam:      {ZAZNAM}")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

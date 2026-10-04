# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""P1b — ODVOZENE CESTY: soubory, ktere cestu NEuvadeji, ale ODVOZUJI ji.

PROC TO EXISTUJE: sken primych cest (`sken-cest-celek.py`) hleda jen literaly
`Local-Deepseek`. Ale `install-into-repo.ps1:34` bere `$ProjDir` z
`Split-Path $PSScriptRoot -Parent` — tedy z RODICE repa. Dnes hleda
`…\\Local-Deepseek\\projects\\<Projekt>` (neexistuje → nastroj nebezi).
Po presunu bude hledat `E:\\Workspaces\\projects\\` — JINAM, a porad tise.

KLICOVE ROZLISENI (a to je hlavni vystup): odvozeni od SEBE je BEZPECNE,
odvozeni od RODICE je RIZIKO.

  `Path(__file__).parent`        → zustane spravne (soubor se presune s repem)
  `import.meta.url` + './x'      → zustane spravne
  `$PSScriptRoot\\..`             → JINAM (rozdil mezi dvema koreny)
  `Path(__file__).parents[2]`    → JINAM (nad repem)
  `Split-Path X -Parent`         → JINAM, pokud X neni uvnitr repa

Vystup: `_analyza\\P1B-ODVOZENE-CESTY.md` s verdiktem u kazdeho souboru.
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(_STANICE)
ANALYZA = WS / "_analyza"
VYSTUP = ANALYZA / "P1B-ODVOZENE-CESTY.md"

SKIP_DIRS = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__",
             ".tmp", ".wrangler", "snapshot-20261002-183213",
             "snapshot-20261002-181237", "_archiv", "a-ukol-scratch"}
SUFFIXY = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql", ".sh"}

# Sablony, ktere odvozuji od SOUBORU (bezpecne) vs. od RODICE (riziko).
#
# ⚠ POZOR NA VYVOJ VZORU (namereno pri psani tohohle nastroje): prvni verze
# hledala `dirname(...)` a `parents[N>=1]` jako "riziko" — a to je VADA
# MERIDLA. `pathlib.Path(__file__).parents[1]` z `_analyza/x.py` je
# `WS / "_analyza"/..` = **koren workspace** a po presunu sedi. Stejne
# `dirname(fileURLToPath(import.meta.url))` v Node je odvozeni od SEBE.
# Rozhoduje VYRAZ, ne pritomnost slova: riziko je jen to, co prekroci
# hranici repa (rodič repa = jine misto po presunu).
VZORY_BEZPECNE = [
    ("parents[0]", re.compile(r"\.parents\[\s*0\s*\]")),
    ("__file__", re.compile(r"__file__")),
    ("import.meta.url", re.compile(r"import\.meta\.url")),
    ("__dirname", re.compile(r"__dirname")),
    ("PSScriptRoot", re.compile(r"\$PSScriptRoot", re.I)),
]
# RIZIKO = odvozeni od RODICE repa. U kazdeho je nutne rict, KTERA cesta to je:
#   - `$PSScriptRoot\..` (z `orchestra\tools\` je to `orchestra\`, ale
#     z `orchestra\` je to uz RODIC repa → rozhoduje hloubka)
#   - `Split-Path <cesta v repu> -Parent` na urovni repa
#   - literál `gameforge` (nazev, ktery v tomto workspace NEEXISTUJE)
VZORY_RIZIKO = [
    ("Split-Path -Parent", re.compile(r"Split-Path[^\n]{0,90}?-Parent", re.I)),
    ("gameforge", re.compile(r"gameforge", re.I)),
    ("parents[>2]", re.compile(r"\.parents\[\s*(?P<n>[3-9]\d*)\s*\]")),
    ("\\.\\.\\\\\\.\\.", re.compile(r"\.\.[\\/]\.\.[\\/]\.\.")),
]
# Cesty, ktere v repu/workspace NEJSOU (overeno Test-Path) — kazda zminka
# znamena, ze nastroj dnes nebezi.
NEEXISTUJE = ["projects", "gameforge"]


def kam_odvodi(rel: str) -> str:
    """Verdikt: odvozuje od sebe (OK), nebo od rodice (RIZIKO)?"""
    return "OK"


def main() -> int:
    nalezy: list[dict] = []
    for p in WS.rglob("*"):
        if any(d in p.parts for d in SKIP_DIRS):
            continue
        if not p.is_file() or p.suffix.lower() not in SUFFIXY:
            continue
        if p.stat().st_size > 3_000_000:
            continue
        try:
            text = p.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        bezp = [j for j, v in VZORY_BEZPECNE if v.search(text)]
        riz = [j for j, v in VZORY_RIZIKO if v.search(text)]
        if not bezp and not riz:
            continue
        # verdikt: riziko prebiji; ale `dirname(..)` sam je slaby signal
        if riz:
            verdikt = "RIZIKO"
        else:
            verdikt = "OK (odvozuje od sebe)"
        rel = str(p.relative_to(WS))
        nalezy.append({"rel": rel, "bezpecne": bezp, "riziko": riz,
                       "verdikt": verdikt})

    if not nalezy:
        print("NIC NENALEZENO — to neni uspech, ale vada skenu.")
        return 2

    def oblast(rel: str) -> str:
        if rel.startswith("orchestra"):
            return "orchestra/"
        if rel.startswith("games"):
            return "games/"
        if rel.startswith("_analyza"):
            return "_analyza/"
        if (rel.startswith("dsh-plugins") or rel.startswith("session-handoff")
                or rel.startswith("dsh-consolidation")):
            return "nastroje stanice/"
        return "root workspace"

    riziko = [n for n in nalezy if n["verdikt"] == "RIZIKO"]
    po_oblasti: dict[str, int] = {}
    for n in nalezy:
        o = oblast(n["rel"])
        po_oblasti[o] = po_oblasti.get(o, 0) + 1

    r = [
        "# P1b — ODVOZENÉ CESTY (co sken přímých cest NEVIDÍ)",
        "",
        "> **Co tenhle dokument JE:** **kontrolní seznam** k přesunu na `E:`",
        "> (krok **P1b** zadání). Generuje `_analyza\\p1b-odvozene-cesty.py` —",
        "> **nepřepisuj ručně**, přegeneruj.",
        "> Nejde o soubory, které cestu **uvádějí**, ale o ty, které si ji",
        "> **odvozují z umístění sebe sama**. V `sken-cest-celek.py` se",
        "> **nevyskytnou**, protože v nich žádný literál `Local-Deepseek` není.",
        "",
        "## ⚠ Klíčové rozlišení: od SEBE (bezpečné) vs. od RODICE (riziko)",
        "",
        "| Odvození | Příklad | Po přesunu |",
        "|---|---|---|",
        "| **od sebe** | `Path(__file__).parent`, `import.meta.url`, `$PSScriptRoot` | **SPRÁVNĚ** — soubor se přesune s repem, odvozená cesta se posune s ním |",
        "| **od rodiče** | `$PSScriptRoot\\..`, `Split-Path … -Parent`, `parents[N≥1]` | **JINAM** — mezi starým a novým umístěním je **jiný rodič** (`Local-Deepseek` vs. `E:\\Workspaces`) |",
        "",
        "**Proč je RODIČ ta past:** dnes je rodičem obou repů `Local-Deepseek`",
        "(a v něm `projects\\`, `games\\`, `_analyza\\`). Po přesunu je rodičem",
        "`E:\\Workspaces` — a v něm je **jen dvojice repů-sourozenců**, žádné",
        "`projects\\` ani `games\\`. Nástroj, který odvozuje z rodiče, proto",
        "**nespadne — jen hledá jinam**, a to je přesně ta tichá vada, kterou",
        "chceme vidět.",
        "",
        "## Souhrn",
        "",
        f"- souborů s odvozenou cestou: **{len(nalezy)}**",
        f"- z toho **RIZIKO** (odvozuje od rodiče): **{len(riziko)}**",
        f"- z toho **OK** (odvozuje od sebe): **{len(nalezy) - len(riziko)}**",
        "",
        "| Oblast | Souborů s odvozenou cestou |",
        "|---|---:|",
    ]
    for o in sorted(po_oblasti):
        r.append(f"| `{o}` | {po_oblasti[o]} |")
    r.append(f"| **CELKEM** | **{len(nalezy)}** |")
    r.append("")
    r.append("## ⚠ RIZIKO — odvozuje od RODICE (po přesunu míří jinam)")
    r.append("")
    r.append("| # | Soubor | Vzory rizika |")
    r.append("|---:|---|---|")
    for i, n in enumerate(sorted(riziko, key=lambda x: x["rel"]), 1):
        r.append(f"| {i} | `{n['rel']}` | {', '.join(n['riziko'])} |")
    r.append("")
    r.append("## OK — odvozuje od SEBE (po přesunu správně)")
    r.append("")
    r.append("| # | Soubor | Vzory |")
    r.append("|---:|---|---|")
    ok = [n for n in nalezy if n["verdikt"] != "RIZIKO"]
    for i, n in enumerate(sorted(ok, key=lambda x: x["rel"]), 1):
        r.append(f"| {i} | `{n['rel']}` | {', '.join(n['bezpecne'])} |")
    r.append("")

    VYSTUP.write_text("\n".join(r), encoding="utf-8", newline="\n")

    print(f"ODVOZENYCH cest celkem: {len(nalezy)}")
    print(f"  RIZIKO (od rodice):   {len(riziko)}")
    print(f"  OK (od sebe):         {len(nalezy) - len(riziko)}")
    for o in sorted(po_oblasti):
        print(f"  {o:20} {po_oblasti[o]}")
    print(f"\nzapsano: {VYSTUP}")
    print("\n--- RIZIKO (od rodice) ---")
    for n in sorted(riziko, key=lambda x: x["rel"]):
        print(f"  {n['rel']:58} {', '.join(n['riziko'])}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

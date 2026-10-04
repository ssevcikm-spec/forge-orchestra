# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Kolik absolutnich cest na Local-Deepseek je v CELÉM workspace (nejen v orchestra).

PROC TO EXISTUJE: plan separace (PLAN-SEPARACE-WORKSPACE.md) merna cesty jen
uvnitr `orchestra/` (70 vyskytu) a uvnitr hry (1). Ale projektove dokumenty,
`_analyza/` nastroje a root skripty taky nesou absolutni cesty — a ty se pri
presunu rozbijou presne tak jako ty v orchestre. Bez tohoto cisla je odhad
ceny presunu dojem.

POSTUP: Python walk (ne `grep` tool — ten z rodicovske slozky tise preskoci
skryte slozky, namereno 80 ku 0). Pocita se vzor `Local-Deepseek` (jakykoli
tvar oddelovace) a zvlast vzory na oba repy.
"""
from __future__ import annotations

import re
import sys
from collections import Counter
from pathlib import Path

WS = Path(_STANICE)
SKIP_DIRS = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__",
             ".tmp", ".wrangler", "snapshot-20261002-183213", "snapshot-20261002-181237"}
SUFFIXY = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".md", ".json", ".yml", ".yaml", ".gd", ".sql"}

VZORY = {
    "cesta na orchestra": re.compile(r"Local-Deepseek[\\/]+orchestra", re.I),
    "cesta na hru (games)": re.compile(r"Local-Deepseek[\\/]+games", re.I),
    "cesta na _analyza": re.compile(r"Local-Deepseek[\\/]+_analyza", re.I),
    "cesta na root (jina)": re.compile(r"Local-Deepseek(?!\\?[\\/]?(orchestra|games|_analyza))", re.I),
}


def kam(rel: str) -> str:
    if rel.startswith("orchestra" + chr(92)) or rel.startswith("orchestra/"):
        return "orchestra/"
    if rel.startswith("games"):
        return "games/"
    if rel.startswith("_analyza"):
        return "_analyza/"
    if rel.startswith("dsh-plugins") or rel.startswith("session-handoff") or rel.startswith("dsh-consolidation"):
        return "nastroje stanice/"
    return "root workspace"


def main() -> int:
    po_oblastech: dict[str, Counter] = {}
    soubory: dict[str, set] = {}
    # KOD se musí opravit; DOKUMENT jen může zestárnout (zmínka v próze nic
    # nerozbije). Bez tohohle rozdělení vypadá cena přesunu 3× dražší.
    KOD = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}
    po_typu: dict[str, Counter] = {"KOD": Counter(), "DOKUMENT": Counter()}
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
        if "Local-Deepseek" not in text:
            continue
        rel = str(p.relative_to(WS))
        oblast = kam(rel)
        typ = "KOD" if p.suffix.lower() in KOD else "DOKUMENT"
        for jmeno, vzor in VZORY.items():
            n = len(vzor.findall(text))
            if n:
                po_oblastech.setdefault(oblast, Counter())[jmeno] += n
                soubory.setdefault(oblast + " | " + jmeno, set()).add(rel)
                po_typu[typ][oblast] += n

    if not po_oblastech:
        print("NIC NENALEZENO — to neni uspech, ale vada skenu. Postup:")
        print(f"  prohledano: {WS} (Python walk, preskoceno {sorted(SKIP_DIRS)})")
        return 2

    print("=" * 78)
    print("ABSOLUTNI CESTY NA Local-Deepseek — CELY workspace")
    print("=" * 78)
    celkem, celkem_soubory = 0, set()
    for oblast in sorted(po_oblastech):
        soucty = po_oblastech[oblast]
        n = sum(soucty.values())
        celkem += n
        print(f"\n{oblast}  —  {n} vyskytu")
        for jmeno, pocet in soucty.most_common():
            kolik_souboru = len(soubory.get(oblast + " | " + jmeno, ()))
            print(f"    {jmeno:24} {pocet:4}  v {kolik_souboru} souborech")
            for s in sorted(soubory.get(oblast + " | " + jmeno, ()))[:4]:
                print(f"        {s}")
        for klic, hodnoty in soubory.items():
            if klic.startswith(oblast + " |"):
                celkem_soubory |= hodnoty

    print()
    print(f"CELKEM: {celkem} vyskytu v {len(celkem_soubory)} souborech")
    print()
    print("ROZDĚLENÍ KÓD vs. DOKUMENT (co se musí OPRAVIT vs. co smí zestárnout):")
    for typ in ("KOD", "DOKUMENT"):
        soucet = sum(po_typu[typ].values())
        print(f"  {typ:9} {soucet:4} vyskytu   " +
              ", ".join(f"{o}={n}" for o, n in po_typu[typ].most_common()))
    print()
    print("POZOR na vyklad: soubor muze mit vic vzoru (napr. orchestra i hru).")
    print("Cilem je RÁDOVÝ odhad prace, ne presny soucet. A dokument, ktery")
    print("historickou cestu cituje, se NEPŘEPISUJE (je to záznam).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
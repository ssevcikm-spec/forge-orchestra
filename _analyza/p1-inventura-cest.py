# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""P1 — INVENTURA ABSOLUTNICH CEST PO SOUBORECH (ne po vyskutech).

PROC TO EXISTUJE: `sken-cest-celek.py` pocita VYSKYTY (208), ale prace se dela
po SOUBORECH. Plan (PLAN-SEPARACE-WORKSPACE.md §10.2b) nameril **176 souboru**:
117 `_analyza/`, 51 `orchestra/`, 5 root, 2 stanice, 1 hra. Tenhle skript to
cislo NEOPISUJE — pocita ho znovu, týmž filtrem jako sken (KOD = prislusne
suffixy, stejne SKIP_DIRS), a u kazdeho souboru rekne:
  - co je zac (KOD/DOKUMENT),
  - kolik ma vyskytu a na co miri (orchestra / games / _analyza / root),
  - ROZHODNUTI `opravit` / `archivovat` / `nechat` (D5 + D6).

ROZHODNUTI (D5, D6 — zavazna, plan §10.3b):
  - `_analyza\` KOD, ktery je ZIVY (v AGENTS.md / HANDOFF.md / _registr-bran.json)
    -> `opravit` (bere cesty z `_analyza\cesty.py`)
  - `_analyza\` KOD, ktery NENI zivy -> `archivovat` (do `_analyza\_archiv\`)
  - `orchestra\` KOD -> `opravit`
  - root workspace KOD -> `opravit`
  - `nastroje stanice\` a `games\` KOD -> `opravit` (stanice zustava stanici)
  - DOKUMENT -> `nechat` (historicka citace se NEPREPISUJE, pravidlo)

Vystup: `_analyza\P1-INVENTURA-CEST.md` (kontrolni seznam) + souhrn na stdout.
"""
from __future__ import annotations

import re
import sys
import unicodedata
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = Path(_STANICE)
ANALYZA = WS / "_analyza"
VYSTUP = ANALYZA / "P1-INVENTURA-CEST.md"

SKIP_DIRS = {".git", "node_modules", ".npm-cache", ".godot", "__pycache__",
             ".tmp", ".wrangler", "snapshot-20261002-183213",
             "snapshot-20261002-181237", "_archiv"}
SUFFIXY = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".md", ".json",
           ".yml", ".yaml", ".gd", ".sql"}
KOD_SUFFIXY = {".py", ".mjs", ".js", ".ts", ".ps1", ".cmd", ".gd", ".sql"}

VZORY = {
    "orchestra": re.compile(r"Local-Deepseek[\\/]+orchestra", re.I),
    "games": re.compile(r"Local-Deepseek[\\/]+games", re.I),
    "_analyza": re.compile(r"Local-Deepseek[\\/]+_analyza", re.I),
    "root": re.compile(
        r"Local-Deepseek(?!\\?[\\/]?(orchestra|games|_analyza))", re.I),
}

# ZIVE nastroje = presne tech, ktere dokumentuje `AGENTS.md` v sekci "Kam pro co"
# jako spustitelne nastroje projektu (D5: "archivovat 99, opravit 18 zivych").
#
# ⚠ ODKUD TAHLE MNOZINA JE (a co NENI): je to **rucni seznam**, ktery odpovida
# citaci v AGENTS.md — a je to prave ta vada (S27), na kterou se v projektu
# opakovane narazi. Proto se pocet NEOPSUJE: `p8b-zjisti-zive.py` meri, ze
# takovych odkazu je vic (28 zminenych + 3 spoustene + 3 z registru = 29)
# a ze `_analyza\g3-brany.py` jich spousti 29. Rozdil je **nalez**, ne duvod
# menit rozhodnuti D5: uzivatel 4. 10. 2026 zvolil "archivovat podle sccutecneho
# mereni 18 zivych dle AGENTS.md, zbytek archiv".
ZIVE = {
    "a1-a2-over.py", "a3-over.py", "n8-zastarala-analyza.py",
    "z8-probe.py", "handoff-kontrola-uplnost.py", "hl2-kontrola.py",
    "hl2-mutace-kontrola.py", "hl2-kostra-test.py", "hl2-kostra-kalibrace.py",
    "ag-over-cisla.py", "ag-mutace.py", "audit-snapshot.py",
    "audit2a-mutace.py", "audit2b-over.py", "audit3-hlavicky-over.py",
    "a1-a2-mutace.py", "a3-mutace.py", "n8-mutace.py",
    "b5-over-tvrzeni.py", "n1-over-inventar.py", "sken-vazeb.py",
    "dsh-session-prehled.mjs", "over-okno.mjs",
    # zminene v AGENTS.md jako zive nastroje (dalsi radky tabulky)
    "hl-neanglicky-v-kodu.py", "hl-rizika-jazyka.py",
    "test-neanglicky-skener.py", "js-tokeny.mjs", "hl2-soubeh.py",
    "hl2-casova-osa.py", "hl2-nic-nezmizelo.py", "hl2-rozbal-session2.mjs",
    "kronika-kontrola.py", "zadani-kontrola.py", "ag-presun-uplnost.py",
    "sken-cest-celek.py", "skryte-vazby-na-hru.py",
    "p1-inventura-cest.py", "p1b-odvozene-cesty.py", "p8b-zjisti-zive.py",
    "p1-rozdil-proti-planu.py", "p1-rozdil-mnozin.py", "p1-kdo-chybi.py",
}


def oblast(rel: str) -> str:
    if rel.startswith("orchestra" + chr(92)) or rel.startswith("orchestra/"):
        return "orchestra/"
    if rel.startswith("games"):
        return "games/"
    if rel.startswith("_analyza"):
        return "_analyza/"
    if (rel.startswith("dsh-plugins") or rel.startswith("session-handoff")
            or rel.startswith("dsh-consolidation")):
        return "nastroje stanice/"
    return "root workspace"


def rozhodni(rel: str, typ: str, jmeno: str) -> str:
    if typ == "DOKUMENT":
        return "nechat"
    if oblast(rel) == "_analyza/":
        return "opravit" if jmeno in ZIVE else "archivovat"
    return "opravit"


def main() -> int:
    kod_soubory: dict[str, dict] = {}
    dok_soubory: dict[str, dict] = {}
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
        typ = "KOD" if p.suffix.lower() in KOD_SUFFIXY else "DOKUMENT"
        cil = {k: len(v.findall(text)) for k, v in VZORY.items()}
        cil = {k: v for k, v in cil.items() if v}
        zaznam = {"rel": rel, "oblast": oblast(rel), "typy": cil,
                  "vyskyty": sum(cil.values()),
                  "rozhodnuti": rozhodni(rel, typ, p.name)}
        (kod_soubory if typ == "KOD" else dok_soubory)[rel] = zaznam

    if not kod_soubory:
        print("NIC NENALEZENO — to neni uspech, ale vada skenu.")
        return 2

    po_oblasti: dict[str, int] = {}
    po_rozhodnuti: dict[str, int] = {}
    for z in kod_soubory.values():
        po_oblasti[z["oblast"]] = po_oblasti.get(z["oblast"], 0) + 1
        po_rozhodnuti[z["rozhodnuti"]] = po_rozhodnuti.get(z["rozhodnuti"], 0) + 1

    radky = [
        "# P1 — INVENTURA ABSOLUTNÍCH CEST PO SOUBORECH",
        "",
        "> **Co tenhle dokument JE:** **kontrolní seznam** k přesunu na `E:`",
        "> (krok **P1** zadání). Generuje ho `_analyza\\p1-inventura-cest.py` —",
        "> **nepřepisuj ručně**, přegeneruj. Počty se neopisují z plánu, počítají",
        "> se týmž filtrem jako `sken-cest-celek.py`.",
        "",
        f"**Vygenerováno:** {__import__('datetime').datetime.now():%Y-%m-%d %H:%M} "
        "(lokální čas) · filtr: `Local-Deepseek` v souborech se suffixem "
        "kódu/dokumentu, mimo `.git`, `node_modules`, snapshoty a `_archiv`",
        "",
        "## Souhrn",
        "",
        "| Oblast (KÓD) | Souborů s cestou |",
        "|---|---:|",
    ]
    for o in sorted(po_oblasti):
        radky.append(f"| `{o}` | {po_oblasti[o]} |")
    radky.append(f"| **CELKEM KÓD** | **{len(kod_soubory)}** |")
    radky.append("")
    radky.append("| Rozhodnutí (KÓD) | Souborů |")
    radky.append("|---|---:|")
    for r in sorted(po_rozhodnuti):
        radky.append(f"| `{r}` | {po_rozhodnuti[r]} |")
    radky.append("")
    radky.append(f"**DOKUMENTŮ s cestou (jen se citují, needitují se):** "
                 f"{len(dok_soubory)}")
    radky.append("")
    radky.append("## KÓD — rozhodnutí po souborech")
    radky.append("")
    radky.append("| # | Soubor | Oblast | Výskytů | Míří na | Rozhodnutí |")
    radky.append("|---:|---|---|---:|---|---|")
    for i, z in enumerate(
            sorted(kod_soubory.values(), key=lambda x: (x["oblast"], x["rel"])), 1):
        radky.append(f"| {i} | `{z['rel']}` | {z['oblast']} | {z['vyskyty']} | "
                     f"{', '.join(sorted(z['typy']))} | **{z['rozhodnuti']}** |")
    radky.append("")
    radky.append("## DOKUMENTY — jen citace (needitují se)")
    radky.append("")
    radky.append("| # | Soubor | Oblast | Výskytů |")
    radky.append("|---:|---|---|---:|")
    for i, z in enumerate(
            sorted(dok_soubory.values(), key=lambda x: (x["oblast"], x["rel"])), 1):
        radky.append(f"| {i} | `{z['rel']}` | {z['oblast']} | {z['vyskyty']} |")
    radky.append("")

    VYSTUP.write_text("\n".join(radky), encoding="utf-8", newline="\n")

    print(f"KOD souboru s pevnou cestou: {len(kod_soubory)}")
    for o in sorted(po_oblasti):
        print(f"  {o:20} {po_oblasti[o]}")
    print("rozhodnuti:")
    for r in sorted(po_rozhodnuti):
        print(f"  {r:12} {po_rozhodnuti[r]}")
    print(f"DOKUMENTU: {len(dok_soubory)}")
    print(f"zapsano: {VYSTUP}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

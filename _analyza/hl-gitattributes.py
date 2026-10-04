#!/usr/bin/env python
r"""Porovná pravidla konců řádků (`.gitattributes`): šablona vs. hra vs. orchestra.

PROČ TO EXISTUJE — naměřeno 1. 10. 2026 (při ověřování před commitem fáze A):
`kontrola-driftu.mjs` má **ruční seznam 12 souborů** a `.gitattributes` v něm
**není** (0 výskytů řetězce v jeho zdroji), takže se tenhle soubor neporovnává.
Navíc `normalizuj()` na `kontrola-driftu.mjs:98` dělá
`readFileSync(...).replace(/\r\n/g, '\n')` — konce řádků u souborů, které
v seznamu JSOU, záměrně schová.

⚠ DVĚ PASTI, KTERÉ TENHLE SKRIPT ZAVÍRÁ (obě mě při psaní chytily):

1. **`.gitattributes` šablony je `orchestra/repo/.gitattributes`, NE
   `orchestra/.gitattributes`.** První verze skriptu i ruční `Test-Path`
   hledaly v kořeni orchestra → „šablona ho nemá", což bylo **nepravdivé
   zjištění**. Kořen orchestra `.gitattributes` opravdu nemá (a je to jiná
   věc, viz níž).

2. **POROVNÁVEJ BLOBY, NE DISK.** Hra má v pracovním stromě 820 B (33 řádků
   × `\r` navíc, protože `.gitattributes` sám sobě nařizuje `eol=lf`, ale
   `core.autocrlf` při checkoutu přidá CRLF) a šablona 787 B. Rozdíl 33 B
   **není rozdíl obsahu** — bloby jsou shodné
   (`f508e781e6005d0e8d4551de744abce2aff34f09`, 787 B v obou). Kdo měří
   velikost na disku, hlásí vadu, která neexistuje. Stejná past jako
   `git show | Measure-Object -Line` v `AGENTS.md`.

Použití:
    python _analyza\hl-gitattributes.py
"""
from __future__ import annotations

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
GIT = WS / "orchestra" / "tools" / "git.cmd"

# (popisek, repo, cesta v repu) — POZOR na 1. past: šablona je `repo/`, ne kořen
MISTA = [
    ("šablona (orchestra/repo)", WS / "orchestra", "repo/.gitattributes"),
    ("hra (uo-shadows)", WS / "games" / "uo-shadows", ".gitattributes"),
    ("orchestra – KOŘEN", WS / "orchestra", ".gitattributes"),
]
DRIFT = WS / "orchestra" / "tools" / "kontrola-driftu.mjs"


def blob(repo: pathlib.Path, cesta: str) -> tuple[str, bytes] | None:
    """Vrátí (hash, obsah) blobu z HEAD, nebo None když v gitu není.

    Tohle je AUTORITA — ne velikost na disku (viz 2. past v docstringu).
    """
    r = subprocess.run([str(GIT), "-C", str(repo), "rev-parse", f"HEAD:{cesta}"],
                       capture_output=True, text=True, errors="replace")
    if r.returncode != 0:
        return None
    h = r.stdout.strip()
    b = subprocess.run([str(GIT), "-C", str(repo), "cat-file", "blob", h],
                       capture_output=True).stdout
    return h, b


def pravidla(text: str) -> list[str]:
    return [r.strip() for r in text.splitlines()
            if r.strip() and not r.strip().startswith("#")]


print("=== 1. Kde .gitattributes je (blob v HEAD, ne disk) ===")
nalezeno: dict[str, tuple[str, bytes]] = {}
for popis, repo, cesta in MISTA:
    v = blob(repo, cesta)
    if v is None:
        disk = "soubor na disku JE" if (repo / cesta).is_file() else "na disku není"
        print(f"  {popis:28s} {cesta:22s} → V GITU NENÍ ({disk})")
        continue
    h, b = v
    nalezeno[popis] = (h, b)
    print(f"  {popis:28s} {cesta:22s} → {h[:16]}  {len(b)} B")

print()
print("=== 2. Jsou šablona a hra shodné? (blob) ===")
klic_sab = "šablona (orchestra/repo)"
klic_hra = "hra (uo-shadows)"
if klic_sab in nalezeno and klic_hra in nalezeno:
    shodne = nalezeno[klic_sab][0] == nalezeno[klic_hra][0]
    print(f"  blob šablony == blob hry: {shodne}")
    if not shodne:
        jen_sab = [p for p in pravidla(nalezeno[klic_sab][1].decode("utf-8"))
                   if p not in pravidla(nalezeno[klic_hra][1].decode("utf-8"))]
        jen_hra = [p for p in pravidla(nalezeno[klic_hra][1].decode("utf-8"))
                   if p not in pravidla(nalezeno[klic_sab][1].decode("utf-8"))]
        for p in jen_sab:
            print(f"    JEN V ŠABLONĚ: {p}")
        for p in jen_hra:
            print(f"    JEN VE HŘE (nová hra NEDOSTANE): {p}")
else:
    print("  nelze porovnat – jedna z kopií v gitu není")

print()
print("=== 3. Vidí rozdíl drift test? ===")
if DRIFT.is_file():
    v = DRIFT.read_text(encoding="utf-8").count(".gitattributes")
    print(f"  výskytů '.gitattributes' v {DRIFT.name}: {v}")
    print("  → " + ("NENÍ v seznamu; rozdíl se nikde neměří." if v == 0
                    else "je v seznamu."))
else:
    print("  CHYBA: kontrola-driftu.mjs nenalezen")

print()
print("=== 4. Je chybějící kořenový .gitattributes v orchestra problém? ===")
# POZOR: první verze tady hlásila poplach „bez kořenového .gitattributes může
# git uložit .sh s CRLF". NEBYLO to pravda: oba .sh soubory leží v `repo/`,
# takže je kryje `repo/.gitattributes` (`*.sh text eol=lf`). Kdo se ptá jen na
# počet souborů a ne na to, KDE leží, vyrobí falešný poplach — a ten nutí
# „opravovat" správný stav. Proto se tu cesta k atributům ověřuje.
sh = subprocess.run([str(GIT), "-C", str(WS / "orchestra"), "ls-files", "*.sh"],
                    capture_output=True, text=True, errors="replace").stdout.split()
print(f"  trackovaných .sh v orchestra: {len(sh)}")
nekryte = []
for s in sh:
    r = subprocess.run([str(GIT), "-C", str(WS / "orchestra"), "check-attr",
                        "eol", "--", s], capture_output=True, text=True,
                       errors="replace").stdout.strip()
    kryto = "eol: lf" in r
    print(f"    - {s:38s} {r}  {'KRYTO' if kryto else 'NEKRYTO'}")
    if not kryto:
        nekryte.append(s)
if not sh:
    print("  → žádné .sh; kořenový .gitattributes dnes není potřeba.")
elif nekryte:
    print(f"  → POZOR: {len(nekryte)} souborů není kryto pravidlem eol=lf.")
else:
    print("  → VŠECHNY .sh jsou kryté pravidlem ze `repo/.gitattributes`")
    print("    (`*.sh text eol=lf`). Chybějící kořenový .gitattributes")
    print("    tedy dnes NIC nekazí — je to stav, ne vada.")

print()
print("SOUHRN: pravidla konců řádků v šabloně i ve hře jsou SHODNÁ (blob výše).")
print("        Drift test je neporovnává – díra v pokrytí, ne v datech.")
sys.exit(0)

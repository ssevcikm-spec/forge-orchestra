#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 / ÚKOL A — NEZÁVISLÉ přeměření `g3-brany.py` (jiné měřidlo, ne `g3`).

PROČ: `g3-brany.py` přepsala v P13c ta samá session, která opravovala měřidla
(`AGENTS.md`: „autor není nezávislý reviewer"; `overovani` §9.7: „oprava měřidla
má taky slepá místa"). Tenhle skript proto:

  1. spočítá brány v `BRANY` **AST parserem** (`ast.parse`) — ne čtením textu
     a ne importem z `g3`;
  2. vytáhne z **plného výpisu** `_analyza/g3-brany-vystup.txt` seznam sekcí
     `### <popis>   (exit=N)` a porovná je **jméno po jménu a v pořadí**;
  3. z **TĚLA každé sekce** (ne z `g3`) rozhodne, jestli brána vůbec začala:
     hledá podpisy „soubor neexistuje" (`can't open file`, `Cannot find module`,
     `MODULE_NOT_FOUND`, `ENOENT`, `WinError 2`) a měří délku výstupu;
  4. **vlastním kódem** dosadí záznamníky cest (`<WS>`, `<TOOLS>`, …) a ověří,
     že každá cesta, která má být SOUBOR, na disku existuje — a že po dosazení
     nikde nezůstala ostrá závorka.

Nic nezapisuje (kromě volitelného `--json` do SVÉHO souboru) a nic nemutuje.
`exit 0` = obě čísla sedí a neexistujících cest je 0; `exit 1` = rozchod.

Použití (ověřeno i z jiného umístění přes `FORGE_WS`):
    python _analyza\p14a-g3-nezavisle.py
    FORGE_WS=E:\Workspaces\forge-orchestra python p14a-g3-nezavisle.py
"""
from __future__ import annotations

import ast
import os
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

# ── CESTY SE ODVOZUJÍ (P8), `FORGE_WS` je jen override pro běh mimo repo ─────
WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
FORGE = WS / "repo" / ".forge"
# Kořen stanice je JINÝ DISK → odvodit se nedá. Bere se z prostředí s touž
# dokumentovanou výchozí hodnotou, jakou má `tools/verify-setup.py:54`.
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
_NAZEV_GODOT = "Godot_v4.7.2-stable_win64_console.exe"
GODOT_KANDIDATI = [
    pathlib.Path(os.environ["FORGE_GODOT"]) if os.environ.get("FORGE_GODOT") else None,
    pathlib.Path(r"E:\Tools\godot") / _NAZEV_GODOT,
    WS.parent.parent / "Tools" / "godot" / _NAZEV_GODOT,
]
GODOT = next((k for k in GODOT_KANDIDATI if k and k.is_file()), GODOT_KANDIDATI[1])

ZNAMKY = {
    "<WS>": WS, "<HRA>": HRA, "<STANICE>": STANICE,
    "<ANALYZA>": ANALYZA, "<TOOLS>": TOOLS, "<FORGE>": FORGE, "<GODOT>": GODOT,
}
# Interprety: kdy je první prvek cesta k souboru, který musí existovat.
INTERPRETY = {"python", "python3", "py", "node", "node.exe"}
G3 = ANALYZA / "g3-brany.py"
VYSTUP = ANALYZA / "g3-brany-vystup.txt"

chyb = 0
kontrol = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global chyb, kontrol
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if detail and not ok:
        for r in str(detail).splitlines():
            print(f"        {r}")


# ── 1) AST: kolik bran je v seznamu BRANY a jaké příkazy nesou ───────────────
def ast_brany(cesta: pathlib.Path) -> list[tuple[str, list]]:
    """Vytáhne seznam `BRANY` z `g3-brany.py` **AST parserem**.

    Nerozbaluje f-stringy ani volání `str(...)` na text — vrací buňky AST;
    na text se převádí až v `na_text()` níž. Tím se nemůže stát, že by měřidlo
    „vidělo" jen to, co je vidět okem v textu souboru.
    """
    strom = ast.parse(cesta.read_text(encoding="utf-8"))
    for uzel in strom.body:
        if isinstance(uzel, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "BRANY" for t in uzel.targets):
            if not isinstance(uzel.value, ast.List):
                raise SystemExit("CHYBA: BRANY není seznam")
            out = []
            for elt in uzel.value.elts:
                if not isinstance(elt, ast.Tuple) or len(elt.elts) != 3:
                    raise SystemExit("CHYBA: prvek BRANY není 3-tice")
                popis = elt.elts[0]
                if not isinstance(popis, ast.Constant) or not isinstance(popis.value, str):
                    raise SystemExit("CHYBA: popis brány není literál")
                prikaz = elt.elts[1]
                if not isinstance(prikaz, ast.List):
                    raise SystemExit("CHYBA: příkaz brány není seznam")
                out.append((popis.value, prikaz.elts))
            return out
    raise SystemExit("CHYBA: v g3-brany.py jsem nenašel přiřazení BRANY")


def na_text(uzel: ast.AST) -> str:
    """Převede buňku AST příkazu na text (jen tvary, které v BRANY opravdu jsou)."""
    if isinstance(uzel, ast.Constant) and isinstance(uzel.value, str):
        return uzel.value
    if isinstance(uzel, ast.Name):
        return {"GODOT": str(GODOT), "HRA": str(HRA), "WS": str(WS)}.get(uzel.id, f"<{uzel.id}>")
    if isinstance(uzel, ast.Call) and isinstance(uzel.func, ast.Name) and uzel.func.id == "str":
        return na_text(uzel.args[0])
    if isinstance(uzel, ast.JoinedStr):
        # f-string: složíme jen z literálních částí + jmen (nic víc v BRANY není)
        return "".join(p.value if isinstance(p, ast.Constant) else na_text(p.value)
                       for p in uzel.values)
    return "<NEUMIM:PREVEST>"


def dosad(text: str) -> tuple[str, list[str]]:
    """Nahradí záznamníky VLASTNÍM kódem; vrátí (text, zbytky ostrých závorek)."""
    for znacka, cesta in ZNAMKY.items():
        text = text.replace(znacka, str(cesta).replace("\\", "/"))
    zbytky = re.findall(r"<[^>]{1,40}>", text)
    return text, zbytky


print("=" * 84)
print("ÚKOL A — `g3` přeměřený JINÝM MĚŘIDLEM (`p14a`, ne `g3`)")
print("=" * 84)
print(f"  WS      = {WS}")
print(f"  HRA     = {HRA}   (sourozenec)")
print(f"  STANICE = {STANICE}")
print(f"  GODOT   = {GODOT}   (existuje: {GODOT.is_file()})")
print(f"  g3      = {G3}")
print(f"  výpis   = {VYSTUP}")
print()

zkontroluj("zdroj `g3-brany.py` existuje", G3.is_file(), G3)
zkontroluj("plný výpis `g3-brany-vystup.txt` existuje", VYSTUP.is_file(), VYSTUP)
if not (G3.is_file() and VYSTUP.is_file()):
    sys.exit(1)

brany = ast_brany(G3)
vypis = VYSTUP.read_text(encoding="utf-8", errors="replace")

# ── 2) Sekce ve výpisu ───────────────────────────────────────────────────────
VZOR_SEKCE = re.compile(r"^### (?P<popis>.+?)   \(exit=(?P<exit>-?\d+)\)$", re.M)
sekce = list(VZOR_SEKCE.finditer(vypis))
print("--- 1) DVĚ ČÍSLA, KTERÁ SE MUSÍ ROVNAT ---------------------------------")
print(f"  bran v seznamu BRANY (AST)      : {len(brany)}")
print(f"  sekcí `### … (exit=N)` ve výpisu: {len(sekce)}")
zkontroluj(f"počet bran v AST ({len(brany)}) = počet sekcí ve výpisu ({len(sekce)})",
           len(brany) == len(sekce))
if len(brany) != len(sekce):
    print(f"        v AST: {[p for p, _ in brany]}")
    print(f"        ve výpisu: {[m.group('popis') for m in sekce]}")

# jména a pořadí — kdyby výpis patřil jiné (starší) verzi seznamu, je to VIDĚT
print()
print("--- 2) JMÉNA A POŘADÍ: patří výpis k TÉTO verzi seznamu? ----------------")
shod = 0
for i, (popis, _) in enumerate(brany):
    if i < len(sekce) and sekce[i].group("popis") == popis:
        shod += 1
    else:
        ma = sekce[i].group("popis") if i < len(sekce) else "(žádná sekce)"
        print(f"        ROZCHOD #{i + 1}: AST {popis!r} vs. výpis {ma!r}")
zkontroluj(f"jméno i pořadí sedí u {shod} z {len(brany)} bran", shod == len(brany))

# ── 3) Z TĚLA SEKCE: začala brána vůbec? ─────────────────────────────────────
print()
print("--- 3) PROBĚHLA? — měřeno Z TĚLA SEKCE (ne z g3) -------------------------")
PODPISY = {
    "soubor neexistuje (python)": re.compile(r"can't open file|No such file or directory"),
    "modul nenalezen (node)": re.compile(r"Cannot find module|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND"),
    "ReferenceError": re.compile(r"ReferenceError"),
    "WinError 2 / ENOENT": re.compile(r"WinError 2|ENOENT"),
    "SyntaxError": re.compile(r"SyntaxError"),
    "PermissionError / EPERM": re.compile(r"PermissionError|WinError 5|EPERM"),
}
tela = {}
for i, m in enumerate(sekce):
    zac = m.end()
    kon = sekce[i + 1].start() if i + 1 < len(sekce) else len(vypis)
    telo = vypis[zac:kon]
    # Oddělovač pod hlavičkou (`\n===…===\n`) NENÍ tělo brány. Bez tohohle
    # odstranění vypadá prázdné tělo jako 78 znaků `=` a kontrola „neotevřela
    # nic" je slepá (odhalil to až mutační test M4).
    telo = re.sub(r"^(?:\r?\n)?=+\r?\n", "", telo)
    tela[m.group("popis")] = (m.group("exit"), telo)

NESTARTOVALO = ("soubor neexistuje (python)", "modul nenalezen (node)",
                "WinError 2 / ENOENT")
prazdne, nestartovalo, prostredi, chybova_signatura = [], [], [], []
for popis, (exit_kod, telo) in tela.items():
    obsah = telo.strip()
    if not obsah:
        prazdne.append(popis)
        continue
    for nazev, vzor in PODPISY.items():
        if vzor.search(obsah):
            if nazev in NESTARTOVALO:
                nestartovalo.append((popis, nazev, exit_kod))
            elif nazev == "PermissionError / EPERM":
                prostredi.append((popis, nazev, exit_kod))
            else:
                chybova_signatura.append((popis, nazev, exit_kod))
            break
zkontroluj(f"žádná sekce nemá PRÁZDNÉ tělo ({len(prazdne)})", not prazdne,
           "prázdné tělo = brána nic neotevřela: " + ", ".join(prazdne))
zkontroluj(f"žádná sekce nenese podpis „soubor neexistuje“ ({len(nestartovalo)})",
           not nestartovalo,
           "\n".join(f"{p} (exit={e}): {n}" for p, n, e in nestartovalo))
print(f"  sekcí s chybovou signaturou (SyntaxError/ReferenceError): "
      f"{len(chybova_signatura)}")
for popis, nazev, exit_kod in chybova_signatura:
    print(f"        {popis}  (exit={exit_kod}): {nazev}")
print(f"  sekcí s podpisem PROSTŘEDÍ (PermissionError/EPERM): {len(prostredi)}"
      + ("  ← třetí stav, ne červená" if prostredi else ""))
for popis, nazev, exit_kod in prostredi:
    print(f"        {popis}  (exit={exit_kod}): {nazev}")
print(f"  nejkratší 3 těla (velikost v B): "
      f"{sorted(((len(t.strip()), p) for p, (_, t) in tela.items()))[:3]}")

# ── 4) EXISTENCE CEST: vlastním dosazením záznamníků ─────────────────────────
print()
print("--- 4) EXISTUJE TO, CO BRÁNY SPOUŠTĚJÍ? (dosazeno VLASTNÍM kódem) ------")
neexistuje, zbytky_celkem, bez_prikazu = [], [], []
for popis, elty in brany:
    casti = [dosad(na_text(e)) for e in elty]
    texty = [c[0] for c in casti]
    zbytky = [z for _, zb in casti for z in zb]
    zbytky_celkem.extend((popis, z) for z in zbytky)
    if not texty:
        bez_prikazu.append(popis)
        continue
    # Kandidáti na SOUBOR: první prvek je-li interpret → druhý; jinak první.
    kandidati = []
    if pathlib.PurePath(texty[0]).name.lower() in INTERPRETY and len(texty) > 1:
        kandidati.append(texty[1])
    else:
        kandidati.append(texty[0])
    # a každý další parametr, který má koncovku skriptu/knihovny
    for t in texty[1:]:
        if t.startswith("-"):
            continue
        if re.search(r"\.(py|mjs|js|cjs|ts|cmd|ps1|exe)$", t, re.I):
            kandidati.append(t)
    for k in kandidati:
        if not k or k.startswith("-") or k.startswith("res://"):
            continue
        p = pathlib.Path(k)
        if not p.is_absolute():
            p = WS / k
        if not p.is_file():
            neexistuje.append((popis, k, str(p)))

zkontroluj(f"po dosazení nezůstala ostrá závorka (nálezů {len(zbytky_celkem)})",
           not zbytky_celkem,
           "\n".join(f"{p}: {z}" for p, z in zbytky_celkem))
zkontroluj(f"každá brána má použitelný příkaz (bez příkazu: {len(bez_prikazu)})",
           not bez_prikazu, "\n".join(bez_prikazu))
print(f"  kontrolovaných cest, které mají být SOUBOR: "
      f"{sum(1 for p, e in brany if e)}  (neexistujících: {len(neexistuje)})")
for popis, k, cesta in neexistuje:
    print(f"        CHYBI  {popis}  →  {k}")
zkontroluj(f"neexistujících cest v BRANY: {len(neexistuje)}", not neexistuje)

# ── 5) Souhrn ────────────────────────────────────────────────────────────────
print()
print("=" * 84)
print(f"ZMĚŘENO: {kontrol} kontrol, {chyb} chyb")
print(f"  bran v BRANY (AST) = {len(brany)} | sekcí ve výpisu = {len(sekce)} | "
      f"neexistujících cest = {len(neexistuje)}")
nenulove = [(p, e) for p, (e, _) in tela.items() if e != "0"]
print(f"  sekcí s nenulovým exit ve výpisu: {len(nenulove)}"
      + (f" → {nenulove}" if nenulove else ""))
if chyb:
    print(f"ROZCHOD: {chyb}")
    sys.exit(1)
print("BEZ ROZCHODU — měřeno `p14a-g3-nezavisle.py` (AST + plný výpis + disk).")
sys.exit(0)

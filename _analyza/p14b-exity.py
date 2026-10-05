#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 / ÚKOL B — každou bránu spustit SAMOSTATNĚ: exit + čítač + verdikt.

PROČ: `g3` je PŘEHLED, ne brána, a jeho `exit=` sloupec napsal autor opravy.
Tenhle skript **nesahá na `g3`** (ani na jeho výstup): AST parserem si vezme
SEZNAM příkazů z `_analyza/g3-brany.py` a **každý spustí sám**, ve stejném
pracovním adresáři (`cwd=WS`), jak to dělá `g3` — a zapíše:

  * `exit` kód (autorita je návratový kód, ne text),
  * čítače, které brána sama vykázala (vlastní vzory, POJMENOVANÉ skupiny),
  * verdikt ve TŘECH stavech (`overovani` §7.13):
      „měří"        — exit 0 a je vidět, kolik toho změřila,
      „stav"        — nenulový exit, ale brána PROBĚHLA a hlásí stav,
      „neproběhlo"  — brána vůbec nezačala (chybí soubor / prostředí).

Plné výpisy všech bran se ukládají do `--vystup` (výchozí vedle skriptu),
aby se dalo měření zpětně ověřit bez opakovaného běhu.

Použití:
    python p14b-exity.py                     # spustí všech N bran
    python p14b-exity.py --jen "a3-over"     # jen brány, jejichž jméno to obsahuje
    python p14b-exity.py --nespoustet        # jen vypíše, co by spustil
"""
from __future__ import annotations

import ast
import json
import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
TOOLS = WS / "tools"
FORGE = WS / "repo" / ".forge"
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
_NAZEV_GODOT = "Godot_v4.7.2-stable_win64_console.exe"
GODOT = (pathlib.Path(os.environ["FORGE_GODOT"]) if os.environ.get("FORGE_GODOT")
         else pathlib.Path(r"E:\Tools\godot") / _NAZEV_GODOT)
ZNAMKY = {"<WS>": WS, "<HRA>": HRA, "<STANICE>": STANICE, "<ANALYZA>": ANALYZA,
          "<TOOLS>": TOOLS, "<FORGE>": FORGE, "<GODOT>": GODOT}
G3 = ANALYZA / "g3-brany.py"

# ── VLASTNÍ VZORY ČÍTAČŮ ────────────────────────────────────────────────────
# POJMENOVANÉ skupiny (`overovani` §10.7) — kdyby jich bylo víc, záměna pořadí
# je nemožná. Bere se POSLEDNÍ výskyt (souhrn je na konci výpisu) a vypíše se
# i to, kolik různých hodnot vzor našel (když víc, je to vidět).
# ⚠ MEZERA MUSÍ BÝT `[ \t]+`, NE `\s+` — `\s` přechází i PŘES KONEC ŘÁDKU.
# Naměřeno při psaní: `handoff úplnost` vypsal `chyb = 83`, protože `\s+`
# spojilo „nalezených: 83" (konec řádku) s „CHYBÍ:" na dalším řádku. Je to
# táž past jako zalomená hláška v logu z CI (`overovani` §8.4).
CITACE = [
    ("kontrol", re.compile(r"(?i)(?P<n>\d+)[ \t]+kontrol")),
    ("Kontrol:", re.compile(r"Kontrol:[ \t]*(?P<n>\d+)")),
    ("kontrolovanych_klice", re.compile(r"kontrolovaných klíčů:[ \t]*(?P<n>\d+)")),
    ("omylu_celkem", re.compile(r"omylů celkem \(skutečnost\):[ \t]*(?P<n>\d+)")),
    ("nalezu_v_kronice", re.compile(r"nálezů H v kronice:[ \t]*(?P<n>\d+)")),
    ("sessions_v_kronice", re.compile(r"sessions v kronice:[ \t]*(?P<n>\d+)")),
    ("mutaci_chyceno", re.compile(r"mutací=(?P<n>\d+), chyceno=(?P<m>\d+)")),
    ("z_z", re.compile(r"(?P<a>\d+) z (?P<b>\d+)")),
    ("chyb", re.compile(r"(?i)(?P<n>\d+)[ \t]+(?:chyb|CHYB|selhání)")),
    ("testu_ok", re.compile(r"Testů OK:[ \t]*(?P<n>\d+)")),
    ("testu_celkem", re.compile(r"PŘÍPADŮ CELKEM:[ \t]*(?P<n>\d+)")),
    ("skilly", re.compile(r"Skillů:[ \t]*(?P<n>\d+)")),
    ("znaku", re.compile(r"(?P<n>\d+)[ \t]+znaků")),
    ("souboru", re.compile(r"(?i)(?P<n>\d+)[ \t]+soubor")),
    ("radku", re.compile(r"(?P<n>\d+)[ \t]+řádků")),
    ("uloh", re.compile(r"(?P<n>\d+)[ \t]+úloh")),
    ("granuli", re.compile(r"(?P<n>\d+)[ \t]+granul")),
]

# Podpisy toho, že brána VŮBEC NEZAČALA (ne že našla vadu).
NEZACALA = [
    ("soubor neexistuje", re.compile(r"can't open file|No such file or directory")),
    ("modul nenalezen", re.compile(r"Cannot find module|MODULE_NOT_FOUND|ERR_MODULE_NOT_FOUND")),
    ("WinError 2", re.compile(r"WinError 2|ENOENT")),
]
# Podpisy PROSTŘEDÍ — třetí stav (`overovani` §7.13): brána běžet chtěla,
# ale sandbox jí to nedovolil. NENÍ to červená a NENÍ to vada kódu.
PROSTREDI = re.compile(r"PermissionError|WinError 5|EPERM|EACCES|Access is denied")


def ast_brany(cesta: pathlib.Path):
    strom = ast.parse(cesta.read_text(encoding="utf-8"))
    for uzel in strom.body:
        if isinstance(uzel, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "BRANY" for t in uzel.targets):
            return [(e.elts[0].value, e.elts[1].elts) for e in uzel.value.elts]
    raise SystemExit("CHYBA: BRANY nenalezeno")


def na_text(uzel):
    if isinstance(uzel, ast.Constant) and isinstance(uzel.value, str):
        return uzel.value
    if isinstance(uzel, ast.Name):
        return str(ZNAMKY.get(f"<{uzel.id}>", f"<{uzel.id}>"))
    if isinstance(uzel, ast.Call) and isinstance(uzel.func, ast.Name) and uzel.func.id == "str":
        return na_text(uzel.args[0])
    if isinstance(uzel, ast.FormattedValue):
        return na_text(uzel.value)
    return "<NEUMIM:PREVEST>"


def prikaz_z(elty) -> list[str]:
    out = []
    for e in elty:
        t = na_text(e)
        for znacka, cesta in ZNAMKY.items():
            t = t.replace(znacka, str(cesta).replace("\\", "/"))
        out.append(t)
    return out


def citace(vystup: str) -> dict:
    """Čítače, které brána sama vykázala — POJMENOVANÉ skupiny (`overovani` §10.7).

    Bere se POSLEDNÍ výskyt (souhrn bývá na konci) a vypíše se i to, kolik
    různých hodnot vzor našel — když víc, je to vidět (jinak by číslo
    z vnořené brány vypadalo jako číslo téhle).
    """
    nalezene = {}
    for jmeno, vzor in CITACE:
        vyskyty = list(vzor.finditer(vystup))
        if not vyskyty:
            continue
        hodnoty = ["/".join(g for g in m.groups() if g is not None)
                   for m in vyskyty]
        nalezene[jmeno] = hodnoty[-1] + (
            f"  (vzor nalezl {len(hodnoty)} výskytů: {hodnoty[:4]}…)"
            if len(hodnoty) > 1 else "")
    return nalezene


def verdikt(kod, vystup: str, cit: dict) -> tuple[str, str]:
    for nazev, vzor in NEZACALA:
        if kod != 0 and vzor.search(vystup):
            return "neproběhlo", f"brána vůbec nezačala — {nazev}"
    if kod != 0 and PROSTREDI.search(vystup):
        return "neproběhlo (prostředí)", "sandbox to nedovolil — NENÍ to červená"
    if kod == 0:
        if cit:
            return "měří", "exit 0 + vykázaný čítač"
        return "měří?", "exit 0, ale BEZ čítače (ticho, ne zelená)"
    # nenulový exit: proběhla, nebo nezačala?
    if cit:
        return "stav", "proběhla a hlásí stav (má čítač)"
    if len(vystup.strip()) > 200:
        return "stav?", "proběhla (dlouhý výstup), ale bez čítače"
    return "neproběhlo?", f"nenulový exit a krátký výstup ({len(vystup.strip())} B)"


def priprav_scratch() -> str:
    """To, co dělá `g3` před branou `mutace B` — bez toho měří jiný stav.

    Poznamenáno proto, aby bylo vidět, že se na přípravu nezapomnělo:
    `.godot/` je v `.gitignore` (do worktree se nezkopíruje, `dsh-prostredi`
    §4c) a `combat.gd`/`run_tests.gd` se synchronizují z klonu.
    """
    import shutil
    scratch = ANALYZA / "a-ukol-scratch"
    if not scratch.is_dir():
        return "scratch neexistuje"
    zdroj = HRA / ".godot"
    if zdroj.is_dir() and not (scratch / ".godot").is_dir():
        shutil.copytree(zdroj, scratch / ".godot")
    for rel in ("scripts/combat.gd", "tests/run_tests.gd"):
        z, c = HRA / rel, scratch / rel
        if z.is_file() and c.parent.is_dir():
            shutil.copyfile(z, c)
    return "scratch připraven"


def main() -> int:
    jen = None
    if "--jen" in sys.argv:
        jen = sys.argv[sys.argv.index("--jen") + 1]
    vystup_soubor = pathlib.Path(
        sys.argv[sys.argv.index("--vystup") + 1] if "--vystup" in sys.argv
        else pathlib.Path(__file__).resolve().parent / "p14b-exity-vystup.txt")
    nespoustet = "--nespoustet" in sys.argv

    brany = ast_brany(G3)
    print("=" * 92)
    print("ÚKOL B — každá brána SPUŠTĚNA SAMOSTATNĚ (ne přes `g3`)")
    print("=" * 92)
    print(f"  WS = {WS}")
    print(f"  bran v BRANY (AST): {len(brany)}")
    if jen:
        brany = [(p, e) for p, e in brany if jen in p]
        print(f"  filtr --jen {jen!r} → {len(brany)} bran")
    print()

    zaznamy, tela = [], []
    for i, (popis, elty) in enumerate(brany, 1):
        prikaz = prikaz_z(elty)
        poznamka = ""
        if not nespoustet and "a-ukol-scratch" in " ".join(prikaz):
            poznamka = priprav_scratch()
        print(f"[{i}/{len(brany)}] {popis}")
        print(f"        {' '.join(prikaz)[:150]}")
        if nespoustet:
            continue
        env = dict(os.environ)
        if "godot" in prikaz[0].lower():
            user_dir = ANALYZA / "a-godot-user"
            env["APPDATA"] = str(user_dir)
        t0 = time.time()
        try:
            r = subprocess.run(prikaz, cwd=str(WS), capture_output=True,
                               env=env, timeout=1800)
            kod = r.returncode
            v = (r.stdout.decode("utf-8", "replace")
                 + r.stderr.decode("utf-8", "replace"))
        except Exception as e:                                   # noqa: BLE001
            kod, v = None, f"CHYBA spuštění: {type(e).__name__}: {e}"
        trvani = time.time() - t0
        cit = citace(v)
        stav, duvod = verdikt(kod, v, cit)
        tela.append("=" * 92)
        tela.append(f"### {popis}   (exit={kod})   [{stav}]  {trvani:.1f}s")
        tela.append("=" * 92)
        tela.append(v)
        print(f"        exit={kod}  [{stav}]  {trvani:.1f}s  {poznamka}")
        print(f"        {duvod}")
        if cit:
            for k, val in cit.items():
                print(f"          {k} = {val}")
        zaznamy.append({"popis": popis, "prikaz": prikaz, "exit": kod,
                        "stav": stav, "duvod": duvod, "citace": cit,
                        "sekund": round(trvani, 1), "bajtu_vystupu": len(v)})
        print()

    if nespoustet:
        return 0

    vystup_soubor.write_bytes("\n".join(tela).encode("utf-8"))
    json_soubor = vystup_soubor.with_suffix(".json")
    json_soubor.write_text(json.dumps(zaznamy, ensure_ascii=False, indent=2),
                           encoding="utf-8")

    print("=" * 92)
    print("SOUHRN")
    print("=" * 92)
    podle = {}
    for z in zaznamy:
        podle.setdefault(z["stav"], []).append(z["popis"])
    for stav, sez in sorted(podle.items(), key=lambda kv: -len(kv[1])):
        print(f"  {stav:22} {len(sez)}")
        for p in sez:
            print(f"        {p}")
    nenulove = [z for z in zaznamy if z["exit"] not in (0, None)]
    print()
    print(f"  bran celkem: {len(zaznamy)}, s NENULOVÝM exit: {len(nenulove)}")
    for z in nenulove:
        print(f"     exit={z['exit']:>3}  [{z['stav']}]  {z['popis']}")
        print(f"              {z['duvod']}")
        if z["citace"]:
            print(f"              čítače: {z['citace']}")
    print()
    print(f"  plný výpis: {vystup_soubor}  ({vystup_soubor.stat().st_size} B)")
    print(f"  JSON:       {json_soubor}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

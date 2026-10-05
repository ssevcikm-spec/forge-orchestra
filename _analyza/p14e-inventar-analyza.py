#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 / ÚKOL E — skener: je vylučování artefaktů SPRÁVNĚ ÚZKÉ?

OTÁZKY ZE ZADÁNÍ (2.5):
  1. Vzít **skutečný seznam netrackovaných** souborů, které skener měří
     (v inventáři klíč `"netrackovane"`), a **projít je jeden po druhém**:
     které z nich **nejsou kód** a měřit se nemají (→ chybí vzor), a které
     **jsou kód** a měřit se MUSÍ (→ správně)?
  2. Skener má **278 zpracovaných** souborů, ale v otisku je **1010**.
     **Vysvětlit rozdíl** rozpadem podle suffixů — ne dohadem.

POSTUP (nic se nezakládá na dohadu):
  * `netrackovane` z inventáře se porovná s **živým** `git ls-files --others
    --exclude-standard` — když jsou množiny shodné, žádný netrackovaný soubor
    se cestou neztratil (a to je zároveň důkaz, že vylučování netrackované
    soubory nepolyká).
  * U každého netrackovaného souboru se zjistí, jestli ho skener **umí číst**:
    suffix se porovná s `PRIPONY`/`JS_TS_PRIPONY` **vytáhnutými AST parserem**
    ze zdrojáku skeneru (ne opisem).
  * Rozdíl 278 vs. 1010 se rozpadne podle suffixů; u každé skupiny se řekne,
    jestli ji skener parsuje, nebo jen vidí.
  * Zvlášť se změří, kolik souborů v otisku je **textových dokumentů** (`.md`)
    a kolik **assetů** (`.png`, `.import`, …) — protože právě ty dělají rozdíl
    mezi „kódem" a „stromem souborů".

Použití: FORGE_WS=E:\Workspaces\forge-orchestra python p14e-inventar-analyza.py
"""
from __future__ import annotations

import ast
import collections
import json
import os
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
HRA = WS.parent / "uo-shadows"
ANALYZA = WS / "_analyza"
SKENER = ANALYZA / "hl-neanglicky-v-kodu.py"
INVENTAR = ANALYZA / "_inventar.json"
GIT = WS / "tools" / "git.cmd"
KOREN_REPA = {"orchestra": WS, "games/uo-shadows": HRA}

kontrol = 0
chyb = 0
nalegy: list[str] = []


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
        nalegy.append(popis)
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:20]:
            print(f"        {r}")


def git_ls(*args: str, repo: pathlib.Path) -> list[str]:
    r = subprocess.run([str(GIT), "-C", str(repo), *args],
                       capture_output=True, text=True, encoding="utf-8")
    if r.returncode != 0:
        raise SystemExit(f"CHYBA: git {' '.join(args)} v {repo} selhalo: {r.stderr}")
    return [l for l in r.stdout.splitlines() if l.strip()]


def artefakt_re() -> "re.Pattern":
    """Vytáhne `ARTEFAKT_RE` ze zdrojáku skeneru (AST, ne opisem).

    ⚠ PROČ TO TU JE (a co to spravilo): první verze tohohle měřidla porovnávala
    množinu `netrackovane` z inventáře s **RAW** `git ls-files --others`.
    Jenže inventář je **už po filtraci artefaktů** (`netrackovane - vyloucene`),
    takže rozdíl je **správný stav**, ne nález. Naměřeno: 2 „nálezy", které
    způsobil **můj vlastní zálohovací soubor** `_analyza/_p14-g3-vystup-p13c-zaloha.txt`
    a výstup `p14b-exity-vystup.json` — oba vylučované **správně**.
    """
    strom = ast.parse(SKENER.read_text(encoding="utf-8"))
    for uzel in ast.walk(strom):
        if isinstance(uzel, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == "ARTEFAKT_RE" for t in uzel.targets):
            vzor = "".join(a.value for a in uzel.value.args if isinstance(a, ast.Constant))
            return re.compile(vzor)
    raise SystemExit("CHYBA: v ARTEFAKT_RE se nedá najít vzor")


def pripony_skeneru() -> tuple[set[str], set[str]]:
    """Suffixy, které skener PARSuje — vytáhnuto AST ze zdrojáku skeneru."""
    strom = ast.parse(SKENER.read_text(encoding="utf-8"))
    pripony: set[str] = set()
    js: set[str] = set()
    for uzel in ast.walk(strom):
        if isinstance(uzel, ast.Assign):
            for t in uzel.targets:
                if not isinstance(t, ast.Name):
                    continue
                if t.id == "PRIPONY" and isinstance(uzel.value, ast.Dict):
                    pripony |= {k.value for k in uzel.value.keys}
                if t.id == "JS_TS_PRIPONY" and isinstance(uzel.value, ast.Tuple):
                    js |= {e.value for e in uzel.value.elts}
    return pripony, js


d = json.loads(INVENTAR.read_text(encoding="utf-8"))
pripony, js = pripony_skeneru()
parsuje = pripony | js
print("=" * 92)
print("ÚKOL E — skener: co VIDÍ, co PARSuje a co VYLUČUJE")
print("=" * 92)
print(f"  skener   = {SKENER}")
print(f"  inventář = {INVENTAR}  ({INVENTAR.stat().st_size} B)")
print(f"  suffixy, které skener PARSuje (AST): {sorted(parsuje)}")
print()

# ── 1) Netrackované: inventář vs. ŽIVÝ git ──────────────────────────────────
print("── 1) NETRACKOVANÉ: inventář vs. živý `git ls-files --others` ───────────")
z_inventare = d["netrackovane"]
print(f"  v inventáři podle repa: "
      f"{ {r: len(s) for r, s in z_inventare.items()} }  "
      f"(celkem {sum(len(s) for s in z_inventare.values())})")
zive: dict[str, list[str]] = {}
for repo, koren in KOREN_REPA.items():
    zive[repo] = sorted(git_ls("ls-files", "--others", "--exclude-standard", repo=koren))
print(f"  živě z gitu:            { {r: len(s) for r, s in zive.items()} }  "
      f"(celkem {sum(len(s) for s in zive.values())})")
mnozina_inv = {f"{r}/{f}" for r, s in z_inventare.items() for f in s}
mnozina_ziva = {f"{r}/{f}" for r, s in zive.items() for f in s}
# Artefakty se z měření VYLUČUJÍ ZÁMĚRNĚ — do porovnání proto vstupují jen
# soubory, které vylučovací vzor netrefí. Jinak měřidlo hlásí „rozchod“ tam,
# kde je to správný stav (a to je falešný poplach na správných datech).
ART = artefakt_re()
mnozina_ziva_bez_artefaktu = {f for f in mnozina_ziva
                              if not ART.search(f.split("/", 1)[1])}
artefakty_v_gitu = sorted(mnozina_ziva - mnozina_ziva_bez_artefaktu)
print(f"  netrackovaných v gitu (raw): {len(mnozina_ziva)}"
      f"   z toho artefakty (vylučují se záměrně): {len(artefakty_v_gitu)}")
for f in artefakty_v_gitu:
    print(f"        VYLOUČENO ZÁMĚRNĚ: {f}")
print(f"  → ve skeneru jich má být: {len(mnozina_ziva_bez_artefaktu)}")
zkontroluj("množina netrackovaných v inventáři = živý stav gitu PO filtraci artefaktů",
           mnozina_inv == mnozina_ziva_bez_artefaktu,
           f"jen v inventáři: {sorted(mnozina_inv - mnozina_ziva_bez_artefaktu)}\n"
           f"jen v gitu:      {sorted(mnozina_ziva_bez_artefaktu - mnozina_inv)}")

# ── 2) Jeden po druhém: je to KÓD, nebo ne? ────────────────────────────────
print()
print("── 2) KAŽDÝ NETRACKOVANÝ SOUBOR: kód (→ měřit), nebo ne? ────────────────")
print(f"  {'soubor':<46} {'suffix':<8} {'B':>8}  verdikt")
tabulka = []
for klic in sorted(mnozina_ziva):
    repo, rel = klic.split("/", 1)
    p = KOREN_REPA[repo] / rel
    suffix = p.suffix.lower()
    velikost = p.stat().st_size if p.is_file() else -1
    je_artefakt = bool(ART.search(rel))
    je_kod = suffix in parsuje
    if je_artefakt:
        verdikt = "ARTEFAKT → vyloučen ZÁMĚRNĚ (správně)"
    elif je_kod:
        verdikt = "KÓD → měřit (správně)"
    else:
        verdikt = f"CHYBA: není kód a NENÍ vyloučen (suffix {suffix or 'žádný'})"
    tabulka.append((rel, suffix, velikost, je_kod, je_artefakt))
    print(f"  {rel:<46} {suffix:<8} {velikost:>8}  {verdikt}")
kod = [t for t in tabulka if t[3] and not t[4]]
artefakty = [t for t in tabulka if t[4]]
print(f"  → KÓD (skener ho parsuje): {len(kod)} · artefakty (vyloučené záměrně): "
      f"{len(artefakty)} · ANI JEDNO: {len(tabulka) - len(kod) - len(artefakty)}")
zkontroluj("každý netrackovaný soubor je BUĎ kód, NEBO záměrně vyloučený artefakt",
           len(kod) + len(artefakty) == len(tabulka),
           "\n".join(f"{r} ({s})" for r, s, _, k, a in tabulka if not k and not a))
zkontroluj("žádný netrackovaný soubor není v `_analyza/_*.json` (tj. artefakt)",
           not any(re.match(r"_analyza/_[^/]*\.json$", r) for r, *_ in tabulka),
           "\n".join(r for r, *_ in tabulka if re.match(r"_analyza/_[^/]*\.json$", r)))

# ── 3) Rozdíl 278 vs. 1010 podle suffixů ───────────────────────────────────
print()
print("── 3) ROZDÍL 278 (zpracováno) vs. 1010 (otisk): rozpad podle suffixů ────")
otisk = d["otisk_vstupu"]
vsechny_cesty = [(z["repo"], s["cesta"]) for z in otisk["repozitare"] for s in z["soubory"]]
pocet_otisk = len(vsechny_cesty)
print(f"  souborů v otisku (sečteno z `repozitare[].soubory`): {pocet_otisk} "
      f"(inventář tvrdí {otisk['souboru']})")
zkontroluj("součet v otisku = číslo, které inventář tvrdí",
           pocet_otisk == otisk["souboru"], f"{pocet_otisk} vs {otisk['souboru']}")
zpracovano = d["souboru_zpracovano"]
print(f"  souborů zpracováno: {zpracovano}")
zkontroluj(f"rozdíl {pocet_otisk} - {zpracovano} = {pocet_otisk - zpracovano} "
           f"je KLADNÝ (skener vidí víc, než parsuje)", pocet_otisk > zpracovano)

hist_pars = collections.Counter()
hist_ne = collections.Counter()
for repo, cesta in vsechny_cesty:
    s = pathlib.PurePosixPath(cesta).suffix.lower()
    (hist_pars if s in parsuje else hist_ne)[s or "(bez suffixu)"] += 1
print()
print(f"  PARSOVANÉ suffixy ({sum(hist_pars.values())} souborů):")
for s, n in hist_pars.most_common():
    print(f"      {s:<12} {n:>5}")
print(f"  NEPARSOVANÉ suffixy ({sum(hist_ne.values())} souborů) — jen se VIDÍ:")
for s, n in hist_ne.most_common(18):
    print(f"      {s:<12} {n:>5}")
if len(hist_ne) > 18:
    print(f"      … a dalších {len(hist_ne) - 18} suffixů")
zkontroluj("parsovaných souborů v otisku = `souboru_zpracovano`",
           sum(hist_pars.values()) == zpracovano,
           f"{sum(hist_pars.values())} vs {zpracovano}")

# ── 4) Kolik z toho jsou assety a kolik dokumenty ─────────────────────────
print()
print("── 4) CO JE TĚCH 1010: assety vs. dokumenty vs. kód ─────────────────────")
ASSETY = {".png", ".jpg", ".jpeg", ".webp", ".svg", ".ogg", ".wav", ".mp3",
          ".ttf", ".otf", ".ico", ".bmp", ".tres", ".tscn", ".res", ".import",
          ".glb", ".gltf", ".obj", ".blend", ".exr", ".hdr", ".bin", ".pck"}
DOKUMENTY = {".md", ".txt"}
pocet_assetu = sum(n for s, n in hist_ne.items() if s in ASSETY)
pocet_dok = sum(n for s, n in hist_ne.items() if s in DOKUMENTY)
pocet_jine = sum(hist_ne.values()) - pocet_assetu - pocet_dok
print(f"  assety (obrázky, zvuk, scény, fonty, .import): {pocet_assetu}")
print(f"  dokumenty (.md, .txt) — parsuje jen `AGENTS.md`? ne: patří mezi neparsované: {pocet_dok}")
print(f"  ostatní neparsované (config, .gitignore, .ps1…): {pocet_jine}")
print(f"  parsovaný kód: {sum(hist_pars.values())}")
print(f"  součet: {pocet_assetu + pocet_dok + pocet_jine + sum(hist_pars.values())}"
      f"  (má být {pocet_otisk})")
zkontroluj("rozpad pokrývá CELÝ otisk (nic nezmizelo)",
           pocet_assetu + pocet_dok + pocet_jine + sum(hist_pars.values()) == pocet_otisk)

# kolik z assetů je hra vs. orchestra
assety_repo = collections.Counter()
for repo, cesta in vsechny_cesty:
    if pathlib.PurePosixPath(cesta).suffix.lower() in ASSETY:
        assety_repo[repo] += 1
print(f"  assety podle repa: {dict(assety_repo)}")

# ── 5) NEPOKRYTO a vyloučené artefakty ─────────────────────────────────────
print()
print("── 5) NEPOKRYTO a VYLOUČENÉ ARTEFAKTY (přiznané stavy) ──────────────────")
print(f"  NEPOKRYTO: {len(d['nepokryto'])}  (když >0, inventář NENÍ úplný)")
print(f"  vyloučené artefakty: {d['vyloucene_artefakty']}")
zkontroluj("NEPOKRYTO je 0 (nic nekončí jako „neumím přečíst“)", not d["nepokryto"],
           json.dumps(d["nepokryto"], ensure_ascii=False)[:600])
# Vyloučené MUSÍ být vidět a musí to být artefakty (ne kód):
print("  ⚠ vyloučené soubory se v datech vypisují JEN počtem — což znamená, že")
print("    se u nich nedá ověřit, CO se vyloučilo. Ověřeno aspoň nepřímo:")
zkontroluj("vyloučeno je víc než 0 (vylučování skutečně funguje)",
           d["vyloucene_artefakty"].get("orchestra", 0) > 0)

print()
print("=" * 92)
print(f"  ZMĚŘENO: {kontrol} kontrol, {chyb} chyb")
print(f"  {pocet_otisk} (otisk) = {sum(hist_pars.values())} parsovaných + "
      f"{pocet_assetu} assetů + {pocet_dok} dokumentů + {pocet_jine} ostatních")
if chyb:
    print("NÁLEZY: " + "; ".join(nalegy))
    sys.exit(1)
print("Skener měří VŠECHNY netrackované soubory (jsou to samé skripty) a rozdíl")
print(f"  {pocet_otisk} vs. {sum(hist_pars.values())} je vysvětlený: "
      f"{pocet_otisk - sum(hist_pars.values())} neparsovaných přípon "
      f"(assety, dokumenty, config).")
print("  ⚠ Hodnoty 278 a 1010 platily pro strom PŘED touhle session (bez šesti")
print("    nových měřidel v `_analyza/`); obě čísla jsou správná, každé pro jiný strom.")
sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""Test pro NÁLEZY H72 + H73 — seznam z `AGENTS.md` a čítač, který počítá VŠE.

CO SE OPRAVILO (P14 to naměřil, tahle session opravila)
-------------------------------------------------------
**H72** — `tools/verify-setup.py` měl dva RUČNÍ literály (`DOKUMENTY_STANICE` 6,
`SLOZKY_STANICE` 5), ačkoli komentář nad nimi tvrdil, že se **čtou z `AGENTS.md`**.
Se seznamem v `AGENTS.md` se **neshodovaly** (**7 dokumentů** brána nehlídala)
a **úbytek pokrytí nikdo nehlásil** (mutace `DOKUMENTY_STANICE = []` → `exit 0`).
Dnes se seznam **skutečně odvozuje** z dokumentu, vzory se rozvíjejí a co
přečíst nejde, je **CHYBA**.

**H73** — kontroly z §5/§6/§7 šly **mimo čítač**: započítaly se, **jen když
spadly** (naměřeno `49 → 50`). Dnes se počítají vždy, takže `ZMĚŘENO: N kontrol`
je počet **opravdu provedených** kontrol.

JAK SE TO MĚŘÍ (fixtura! do živé stanice se NESAHÁ)
--------------------------------------------------
Fixtura je **vlastní kořen stanice** v `_analyza/fixtura-h72/` a předává se
bráně přes `FORGE_STANICE`. Seznam dokumentů do fixtury se **NEOPISUJE** —
**přečte se z výstupu brány** (`dokumenty (N): …` / `nástroje (N): …`), takže
test nemá druhou definici téhož (`overovani` §9.2: dvě okna = dvě pravdy).

PŘÍPADY (všechny spuštěním):
  1. zdravá fixtura → `exit 0` a vykázaný počet kontrol,
  2. deklarovaný dokument odebrán → `exit 1` a `CHYBI stanice/<jméno>`,
  3. **vzor (`token-saving-*.md`) bez shody** → `exit 1` (zestárlá deklarace
     nesmí být ticho),
  4. **řádek „dokumenty STANICE" v `AGENTS.md` chybí** → `exit 1` (ne zelená
     nad prázdným seznamem — přesně to byla vada H72),
  5. **seznam je prázdný** → `exit 1` (buňka `tento koren (*.md)` se nesmí
     stát „seznamem"),
  6. **H73**: rozbitý dokument v §6 **NESMÍ ZVÝŠIT** vykázaný počet kontrol
     (dřív `49 → 50`); rozdíl zdravá/rozbitá musí být **0**.

A tři **MUTACE** živé brány (kotva 1×, změna na disku, měřená podmínka
přestala platit, návrat bajt na bajt podle SHA-256):
  **M1** (H72) vypnutá kontrola odvození · **M2** (H73) úspěch se nepočítá ·
  **M3** (H72) vzor bez shody se nehlásí.

Použití:  python _analyza\test-h72-h73.py
"""
from __future__ import annotations

import hashlib
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
ANALYZA = WS / "_analyza"
BRANA = WS / "tools" / "verify-setup.py"
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
FIX = ANALYZA / "fixtura-h72"
PY = sys.executable

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:14]:
            print(f"        {r}")


def spust(stanice: pathlib.Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["FORGE_STANICE"] = str(stanice)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([PY, str(BRANA)], cwd=str(WS), capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


def citac(vystup: str) -> tuple[int, int]:
    m = re.search(r"ZMĚŘENO:\s*(\d+) kontrol,\s*(\d+) chyb", vystup)
    return (int(m.group(1)), int(m.group(2))) if m else (-1, -1)


def postav_fixturu(agents_text: str, dokumenty: list[str], slozky: list[str],
                   vynechat: set[str] | None = None) -> pathlib.Path:
    vynechat = vynechat or set()
    if FIX.exists():
        shutil.rmtree(FIX)
    FIX.mkdir(parents=True)
    (FIX / "AGENTS.md").write_text(agents_text, encoding="utf-8", newline="")
    for jmeno in dokumenty:
        if jmeno in vynechat or jmeno == "AGENTS.md":
            continue
        cil = FIX / jmeno
        cil.parent.mkdir(parents=True, exist_ok=True)
        cil.write_text(f"# fixtura: {jmeno}\n", encoding="utf-8", newline="")
    for jmeno in slozky:
        (FIX / jmeno).mkdir(parents=True, exist_ok=True)
    return FIX


print("=" * 92)
print("NÁLEZY H72 + H73 — odvozuje brána seznam z `AGENTS.md` a počítá VŠE?")
print("=" * 92)
print(f"  brána   = {BRANA}")
print(f"  STANICE = {STANICE}")
print(f"  fixtura = {FIX}  (vzniká a uklidí se, do živé stanice se nesahá)")
print()

agents_text = (STANICE / "AGENTS.md").read_text(encoding="utf-8")

# ── 0) Seznam se do fixtury PŘEBÍRÁ Z VÝSTUPU BRÁNY, ne opisem ───────────────
print("── 0) Seznam dokumentů/nástrojů se čte Z VÝSTUPU brány ─────────────────")
kod0, v0 = spust(STANICE)
zkontroluj(f"brána nad ŽIVOU stanicí: exit 0 (je {kod0})", kod0 == 0, v0[-800:])
m_dok = re.search(r"^\s+dokumenty \((\d+)\): (.+)$", v0, re.M)
m_slo = re.search(r"^\s+nástroje\s+\((\d+)\): (.+)$", v0, re.M)
zkontroluj("výstup brány vykazuje ODVOZENÝ seznam dokumentů i nástrojů",
           m_dok is not None and m_slo is not None, v0[-1200:])
dokumenty = [x.strip() for x in m_dok.group(2).split(",")] if m_dok else []
slozky = [x.strip() for x in m_slo.group(2).split(",")] if m_slo else []
print(f"      dokumenty odvozené bránou: {len(dokumenty)} → {dokumenty}")
print(f"      nástroje  odvozené bránou: {len(slozky)} → {slozky}")
zkontroluj(f"brána odvodila aspoň 12 dokumentů (dřív RUČNÍCH 6) — je {len(dokumenty)}",
           len(dokumenty) >= 12, str(dokumenty))
zkontroluj(f"brána odvodila aspoň 5 nástrojů — je {len(slozky)}", len(slozky) >= 5,
           str(slozky))
zkontroluj("mezi odvozenými dokumenty je i ten, který RUČNÍ seznam nehlídal "
           "(`ANALYZA-EFEKTIVITY-DSH.md`)",
           "ANALYZA-EFEKTIVITY-DSH.md" in dokumenty, str(dokumenty))
n_zdrava, ch_zdrava = citac(v0)
print(f"      čítač na živé stanici: {n_zdrava} kontrol, {ch_zdrava} chyb")

try:
    # ── 1) ZDRAVÁ FIXTURA ──────────────────────────────────────────────────
    print()
    print("── 1) ZDRAVÁ FIXTURA: všechny deklarované položky existují ────────────")
    postav_fixturu(agents_text, dokumenty, slozky)
    kod1, v1 = spust(FIX)
    n1, ch1 = citac(v1)
    zkontroluj(f"zdravá fixtura: exit 0 (je {kod1})", kod1 == 0, v1[-900:])
    zkontroluj(f"zdravá fixtura: vykázaný čítač ({n1} kontrol, {ch1} chyb)",
               n1 > 0 and ch1 == 0, v1[-400:])

    # ── 2) CHYBĚJÍCÍ DOKUMENT ──────────────────────────────────────────────
    print()
    print("── 2) DEKLAROVANÝ DOKUMENT ODEBRÁN ───────────────────────────────────")
    obet = next((f for f in dokumenty if f.endswith(".md") and f != "README.md"),
                dokumenty[0])
    postav_fixturu(agents_text, dokumenty, slozky, vynechat={obet})
    kod2, v2 = spust(FIX)
    zkontroluj(f"po odebrání `{obet}`: exit 1 (je {kod2})", kod2 == 1, v2[-900:])
    zkontroluj(f"brána to POJMENUJE (`CHYBI stanice/{obet}`)",
               f"CHYBI stanice/{obet}" in v2, v2[-900:])

    # ── 3) VZOR BEZ SHODY (zestárlá deklarace) ─────────────────────────────
    print()
    print("── 3) VZOR V DEKLARACI BEZ SHODY (nesmí být ticho) ───────────────────")
    vzor_bez = next((f for f in dokumenty if f.startswith("token-saving-")), "")
    zkontroluj("mezi odvozenými dokumenty je rozvinutý vzor `token-saving-*.md`",
               bool(vzor_bez), str(dokumenty))
    postav_fixturu(agents_text, dokumenty, slozky, vynechat={vzor_bez} if vzor_bez else set())
    kod3, v3 = spust(FIX)
    zkontroluj(f"vzor `token-saving-*.md` bez souboru → exit 1 (je {kod3})",
               kod3 == 1, v3[-900:])
    zkontroluj("brána to ŘEKNE („vzor bez souboru“)", "vzor bez souboru" in v3,
               v3[-900:])

    # ── 4) ŘÁDEK V AGENTS.md CHYBÍ ─────────────────────────────────────────
    print()
    print("── 4) `AGENTS.md` NEMÁ řádek „dokumenty STANICE“ ─────────────────────")
    bez_radku = "\n".join(l for l in agents_text.splitlines()
                          if "dokumenty STANICE" not in l) + "\n"
    zkontroluj("fixtura: řádek „dokumenty STANICE“ je z `AGENTS.md` odebrán",
               "dokumenty STANICE" not in bez_radku)
    # POZOR: soubory na disku zůstávají — jinak by brána spadla na §6
    # (`STANICE/README.md` neexistuje) a `exit 1` by byl **ze špatného důvodu**
    # (`overovani` §10.1). Měří se jen to, že DEKLARACE chybí.
    postav_fixturu(bez_radku, dokumenty, slozky)
    kod4, v4 = spust(FIX)
    zkontroluj(f"chybějící řádek → exit 1 (je {kod4})", kod4 == 1, v4[-900:])
    zkontroluj("brána to ŘEKNE („dokumenty STANICE“ v chybě)",
               "dokumenty STANICE" in v4 and "CHYBI" in v4, v4[-900:])
    zkontroluj("a NENÍ to náhodou kvůli chybějícímu souboru na disku",
               f"CHYBI stanice/{dokumenty[0]}" not in v4, v4[-900:])

    # ── 5) PRÁZDNÝ SEZNAM ──────────────────────────────────────────────────
    print()
    print("── 5) řádek JE, ale seznam je PRÁZDNÝ ────────────────────────────────")
    prazdny = re.sub(r"(\| \*\*dokumenty STANICE\*\* \|[^|]*\|)[^|]*(\|)",
                     r"\1 — \2", agents_text)
    zkontroluj("fixtura: buňka se seznamem je nahrazena pomlčkou",
               prazdny != agents_text and "—" in prazdny)
    # I tady soubory na disku ZŮSTÁVAJÍ (viz §4) — měří se jen prázdná deklarace.
    postav_fixturu(prazdny, dokumenty, slozky)
    kod5, v5 = spust(FIX)
    zkontroluj(f"prázdný seznam → exit 1 (je {kod5})", kod5 == 1, v5[-900:])

    # ── 6) H73: ČÍTAČ SE PŘI SELHÁNÍ NESMÍ ZVÝŠIT ──────────────────────────
    print()
    print("── 6) H73: rozbitý dokument v §6 NESMÍ ZVÝŠIT vykázaný počet kontrol ─")
    postav_fixturu(agents_text, dokumenty, slozky)
    kod6a, v6a = spust(FIX)
    n6a, ch6a = citac(v6a)
    (FIX / "README.md").write_bytes(b"# fixtura\n\xff\xfe rozbite bajty\n")
    kod6b, v6b = spust(FIX)
    n6b, ch6b = citac(v6b)
    print(f"      zdravá: {n6a} kontrol / {ch6a} chyb   ·   "
          f"rozbitá: {n6b} kontrol / {ch6b} chyb")
    zkontroluj(f"rozbitý dokument: exit 1 (je {kod6b})", kod6b == 1, v6b[-600:])
    zkontroluj("rozbitý dokument: `chyb` se zvýší (kontrola opravdu proběhla)",
               ch6b == ch6a + 1, v6b[-600:])
    zkontroluj("H73: vykázaný POČET KONTROL se přitom NEZMĚNÍ "
               "(dřív 49 → 50, protože úspěch se nepočítal)",
               n6a == n6b, f"zdravá {n6a} vs. rozbitá {n6b}")

    # ── 7) TŘI MUTACE ŽIVÉ BRÁNY ───────────────────────────────────────────
    print()
    print("── 7) MUTACE živé brány (záloha → změna → běh → návrat) ──────────────")
    orig = BRANA.read_bytes()
    orig_sha = hashlib.sha256(orig).hexdigest()[:16]

    def s_mutaci(popis: str, kotva: str, nahrada: str, scenar) -> None:
        kb, nb = kotva.encode("utf-8"), nahrada.encode("utf-8")
        pocet = orig.count(kb)
        zkontroluj(f"{popis}: kotva je v bráně 1× (je {pocet}×)", pocet == 1, kotva)
        try:
            BRANA.write_bytes(orig.replace(kb, nb))
            zpet = BRANA.read_bytes()
            zkontroluj(f"{popis}: mutace se propsala NA DISK", zpet != orig)
            zkontroluj(f"{popis}: měřená PODMÍNKA přestala platit", kb not in zpet)
            scenar(popis)
        finally:
            BRANA.write_bytes(orig)
        zkontroluj(f"{popis}: brána vrácena bajt na bajt (sha {orig_sha})",
                   hashlib.sha256(BRANA.read_bytes()).hexdigest()[:16] == orig_sha)

    def sc_m1(p: str) -> None:
        # Soubory na disku jsou — kdyby nebyly, spadne §6 a `exit 1` by byl
        # ze špatného důvodu.
        postav_fixturu(bez_radku, dokumenty, slozky)
        kod_m, v_m = spust(FIX)
        zkontroluj(f"{p}: chybějící řádek projde jako exit=0 (je {kod_m}) "
                   f"— test by ZČERVENAL", kod_m == 0, v_m[-800:])

    def sc_m2(p: str) -> None:
        postav_fixturu(agents_text, dokumenty, slozky)
        _, va = spust(FIX)
        na, _ = citac(va)
        (FIX / "README.md").write_bytes(b"# fixtura\n\xff\xfe rozbite bajty\n")
        _, vb = spust(FIX)
        nb2, _ = citac(vb)
        print(f"      s mutací: zdravá {na} kontrol, rozbitá {nb2} kontrol")
        zkontroluj(f"{p}: počet kontrol SKOČÍ o {nb2 - na} (správně 0) "
                   f"— test by ZČERVENAL", nb2 - na == 1,
                   f"zdravá {na}, rozbitá {nb2}")

    def sc_m3(p: str) -> None:
        postav_fixturu(agents_text, dokumenty, slozky,
                       vynechat={vzor_bez} if vzor_bez else set())
        kod_m, v_m = spust(FIX)
        zkontroluj(f"{p}: zestárlý vzor projde jako exit=0 (je {kod_m}) "
                   f"— test by ZČERVENAL", kod_m == 0, v_m[-800:])

    s_mutaci("M1 (H72): kontrola odvození vypnuta",
             'zkontroluj("`AGENTS.md` stanice: řádek „dokumenty STANICE“ se seznamem",\n'
             "           bool(_radek_dok) and bool(_polozky_dok),",
             'zkontroluj("`AGENTS.md` stanice: řádek „dokumenty STANICE“ se seznamem",\n'
             "           True,",
             sc_m1)
    s_mutaci("M2 (H73): úspěch v §6 se nepočítá",
             '    zkontroluj(f"{popis} je platné UTF-8", True)',
             "    pass  # mutace: úspěch se nepočítá",
             sc_m2)
    s_mutaci("M3 (H72): vzor bez shody se nehlásí",
             "                prazdne.append(kandidat)",
             "                pass  # mutace",
             sc_m3)

    # Po všech mutacích musí brána znovu měřit.
    postav_fixturu(bez_radku, [], slozky)
    kod_p, v_p = spust(FIX)
    zkontroluj("po návratu: chybějící řádek znovu dá exit 1 (brána měří)",
               kod_p == 1, v_p[-600:])
finally:
    shutil.rmtree(FIX, ignore_errors=True)
    zkontroluj("fixtura uklizena (v repu nezůstal žádný soubor navíc)",
               not FIX.exists())

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print(f"CHYBA: {chyb} — H72/H73 NENÍ dokázané")
    sys.exit(1)
print("H72 i H73 JSOU OPRAVENÉ A DOKÁZANÉ (fixtura + tři mutace).")
sys.exit(0)

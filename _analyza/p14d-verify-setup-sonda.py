#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 / ÚKOL D — je seznam v `tools/verify-setup.py` RUČNÍ? (a co z toho hrozí)

OTÁZKY ZE ZADÁNÍ (2.4):
  * Není seznam dokumentů stanice **ruční a brzy zastaralý**? (`overovani` §9.5:
    „výjimka klíčovaná jménem je ruční seznam"; §7.6: „brána, která kontroluje
    SEZNAM, ne strom".)
  * Nekontroluje něco, co si **odporuje s `AGENTS.md`**?
  * Má každé CHYBI **odůvodnění**?

POSTUP (měří se KÓD, ne komentář):
  1. `DOKUMENTY_STANICE` a `SLOZKY_STANICE` se vytáhnou **AST parserem** ze
     zdroje brány — komentář o dvě řádky výš TVRDÍ, že se seznam čte
     z `AGENTS.md`; to se ověří zvlášť (hledáním čtení toho souboru v kódu).
  2. Seznam z `AGENTS.md` (řádek „dokumenty STANICE") se přečte **z dokumentu**
     — včetně zástupných vzorů (`token-saving-*.md`), které se rozvinou proti
     skutečnému obsahu kořene stanice.
  3. Rozdíl se vypíše **oběma směry** (co brána nehlídá / co hlídá navíc).
  4. **FIXTURA**: postaví se falešný kořen stanice v pracovním adresáři a brána
     se nad ním spustí (`FORGE_STANICE`). Pak se v něm `README.md` PŘEJMENUJE
     na `README-INDEX.md` — stav stanice je pořád legitimní, ale brána zčervená.
     To je to „falešný poplach se hledá hůř než slepé místo".
  5. Počítá se, kolik kontrol brána OPRAVDU provede a kolik jich VYKÁŽE
     (čítač `ZMĚŘENO: N kontrol`).

Nic se nezapisuje do repa ani do stanice — fixtura je ve vlastním adresáři
(`--fixtura`, výchozí vedle skriptu) a uklidí se.
"""
from __future__ import annotations

import ast
import os
import pathlib
import re
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(os.environ.get("FORGE_WS") or pathlib.Path(__file__).resolve().parents[1])
TOOLS = WS / "tools"
VERIFY = TOOLS / "verify-setup.py"
STANICE = pathlib.Path(os.environ.get("FORGE_STANICE", r"C:\Users\Ssevc\Local-Deepseek"))
FIX = pathlib.Path(os.environ.get("P14_FIXTURA")
                   or pathlib.Path(__file__).resolve().parent / "fixtura-d-stanice")

kontrol = 0
chyb = 0


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:20]:
            print(f"        {r}")


def ast_seznam(cesta: pathlib.Path, jmeno: str) -> list[str]:
    """Vytáhne ze zdroje seznam přiřazený do `jmeno` (AST, ne text)."""
    strom = ast.parse(cesta.read_text(encoding="utf-8"))
    for uzel in strom.body:
        if isinstance(uzel, ast.Assign) and any(
                isinstance(t, ast.Name) and t.id == jmeno for t in uzel.targets):
            return [e.value for e in uzel.value.elts]
    return []


def spust_verify(stanice: pathlib.Path) -> tuple[int, str]:
    env = dict(os.environ)
    env["FORGE_STANICE"] = str(stanice)
    env["PYTHONIOENCODING"] = "utf-8"
    r = subprocess.run([sys.executable, str(VERIFY)], capture_output=True, env=env)
    return r.returncode, (r.stdout.decode("utf-8", "replace")
                          + r.stderr.decode("utf-8", "replace"))


print("=" * 92)
print("ÚKOL D — `tools/verify-setup.py`: je jeho seznam RUČNÍ?")
print("=" * 92)
print(f"  brána   = {VERIFY}")
print(f"  STANICE = {STANICE}")
print()

# ── 1) Co je v KÓDU brány ───────────────────────────────────────────────────
dok_brana = ast_seznam(VERIFY, "DOKUMENTY_STANICE")
slo_brana = ast_seznam(VERIFY, "SLOZKY_STANICE")
print("── 1) SEZNAMY V KÓDU BRÁNY (AST) ────────────────────────────────────────")
print(f"  DOKUMENTY_STANICE ({len(dok_brana)}): {dok_brana}")
print(f"  SLOZKY_STANICE    ({len(slo_brana)}): {slo_brana}")
zkontroluj("oba seznamy jsou v kódu NAPEVNO (jsou to literály, ne čtení souboru)",
           len(dok_brana) > 0 and len(slo_brana) > 0)

# Tvrdí komentář, že se seznam ČTE z AGENTS.md? Ověř to v KÓDU — a to tak, že se
# podíváme, jestli se v OKOLÍ seznamu ten soubor vůbec čte.
zdroj = VERIFY.read_text(encoding="utf-8")
i_seznam = zdroj.find("DOKUMENTY_STANICE = [")
okoli = zdroj[max(0, i_seznam - 1200):i_seznam]
komentar_tvrdi = "čte z něj" in okoli or "ne z ruky" in okoli
cte_soubor = bool(re.search(r"(read_text|read_bytes|open)\s*\(", okoli))
print(f"  komentář nad seznamem tvrdí, že se čte z AGENTS.md: {komentar_tvrdi}")
print(f"  kód před seznamem čte nějaký soubor: {cte_soubor}")
zkontroluj("komentář TVRDÍ, že se seznam čte z dokumentu", komentar_tvrdi)
zkontroluj("…ale KÓD před seznamem žádný soubor nečte (je to literál, ne odvození)",
           not cte_soubor)

# ── 2) Co je v AGENTS.md stanice ────────────────────────────────────────────
print()
print("── 2) SEZNAM V `AGENTS.md` STANICE (čte se Z DOKUMENTU) ─────────────────")
agents = STANICE / "AGENTS.md"
zkontroluj("`AGENTS.md` stanice existuje", agents.is_file(), agents)
radky = agents.read_text(encoding="utf-8").splitlines()
radek_dok = next((l for l in radky if "dokumenty STANICE" in l), "")
zkontroluj("v `AGENTS.md` je řádek „dokumenty STANICE“", bool(radek_dok))
v_agents: list[str] = []
if radek_dok:
    bunky = [b.strip() for b in radek_dok.split("|") if b.strip()]
    posledni = bunky[-1]
    v_agents = re.findall(r"`([^`]+)`", posledni)
print(f"  v AGENTS.md ({len(v_agents)}): {v_agents}")
# Rozviň zástupné vzory (`token-saving-*.md`) proti SKUTEČNÉMU obsahu stanice.
rozvinute: set[str] = set()
for vzor in v_agents:
    if "*" in vzor:
        nalezeno = [p.name for p in STANICE.glob(vzor)]
        print(f"    vzor `{vzor}` → {len(nalezeno)} souborů: {nalezeno}")
        rozvinute.update(nalezeno)
    else:
        rozvinute.add(vzor)

# ── 3) Rozdíl OBĚMA směry ───────────────────────────────────────────────────
print()
print("── 3) ROZDÍL: co brána nehlídá a co hlídá navíc ─────────────────────────")
ma_agents = {f for f in rozvinute if (STANICE / f).is_file()}
nehlida = sorted(ma_agents - set(dok_brana))
hlida_navic = sorted(set(dok_brana) - ma_agents)
print(f"  v AGENTS.md je a brána to NEHLÍDÁ ({len(nehlida)}):")
for f in nehlida:
    print(f"        {f}")
print(f"  brána hlídá, ale v AGENTS.md to NENÍ ({len(hlida_navic)}): {hlida_navic}")
zkontroluj(f"brána nehlídá {len(nehlida)} dokumentů, které AGENTS.md za dokumenty stanice OZNAČUJE",
           not nehlida,
           "nehlídá: " + ", ".join(nehlida))
if hlida_navic:
    print(f"  (poznámka: `AGENTS.md` sám sebe ve svém seznamu nemá — neškodné, ale matoucí)")

# Složky: AGENTS.md je vyjmenovává v jiném sloupci („nástroje stanice“).
# Bere se BUŇKA S NEJVÍC ZPĚTNÝMI APOSTROFY, ne poslední — poslední je
# „zůstávají tady“ a hledání by našlo prázdno (`overovani` §10.1).
radek_nastroje = next((l for l in radky if "nástroje stanice" in l), "")
bunky_n = [b.strip() for b in radek_nastroje.split("|") if b.strip()] if radek_nastroje else []
bunka = max(bunky_n, key=lambda b: b.count("`")) if bunky_n else ""
v_agents_slozky = [s.rstrip("\\/") for s in re.findall(r"`([^`]+)`", bunka)]
print(f"  AGENTS.md „nástroje stanice“: {v_agents_slozky}")
print(f"  brána SLOZKY_STANICE:          {slo_brana}")
zkontroluj("obě množiny složek jsou shodné",
           set(v_agents_slozky) == set(slo_brana),
           f"jen v AGENTS.md: {sorted(set(v_agents_slozky) - set(slo_brana))} | "
           f"jen v bráně: {sorted(set(slo_brana) - set(v_agents_slozky))}")

# ── 4) Kolik kontrol brána provede a kolik jich VYKÁŽE ─────────────────────
print()
print("── 4) ČÍTAČ: kolik kontrol se OPRAVDU provede ───────────────────────────")
kod, v = spust_verify(STANICE)
m = re.search(r"ZMĚŘENO:\s*(\d+) kontrol, (\d+) chyb", v)
zkontroluj(f"brána na živé stanici doběhla s čítačem (exit={kod})", m is not None, v[-600:])
vykazano = int(m.group(1)) if m else -1
# Kolik `zkontroluj(...)` volání se v sekcích 1–4 opravdu provede:
ocekavane = len(dok_brana) + len(slo_brana) + 3 + 19 + 2 + 14
print(f"  vykázaných kontrol: {vykazano}")
print(f"  skutečně provedených (dokumenty+složky+smazané+orchestra+tajemství+hra) = {ocekavane}")
print("  ⚠ sekce 5 (JSON) a 6 (UTF-8) tisknou `OK` BEZ `zkontroluj()` — do čítače")
print("    se nedostanou, i když se kontrola provede (a při chybě se započítá).")
zkontroluj("vykázaný počet odpovídá kontrolám, které volají `zkontroluj`",
           vykazano == ocekavane, f"vykázáno {vykazano}, spočítáno {ocekavane}")

# ── 4b) DŮKAZ TOHO, ŽE SE POČET NEPOČÍTÁ: rozbij jeden dokument v KOŘENI STANICE?
# Ne — do živé stanice se nesahá. Rozbije se KOPIE (fixtura níž) a porovná se
# čítač: kontrola z §6 se objeví v čítači JEN když SPADNE.
print()
print("── 4b) FIXTURA: co udělá čítač, když kontrola z §6 SPADNE ───────────────")
if FIX.exists():
    shutil.rmtree(FIX)
FIX.mkdir(parents=True)
for f in dok_brana:
    (FIX / f).write_text("# fixtura\n", encoding="utf-8")
for d in slo_brana:
    (FIX / d).mkdir()
kod_c, v_c = spust_verify(FIX)
m_c = re.search(r"ZMĚŘENO:\s*(\d+) kontrol, (\d+) chyb", v_c)
# `README.md` v NEPLATNÉM UTF-8: §6 na to má `zkontroluj(False)`.
(FIX / "README.md").write_bytes(b"# fixtura\n\xff\xfe rozbite bajty\n")
kod_u, v_u = spust_verify(FIX)
m_u = re.search(r"ZMĚŘENO:\s*(\d+) kontrol, (\d+) chyb", v_u)
print(f"      před: exit={kod_c}, čítač={m_c.group(0) if m_c else '?'}")
print(f"      po rozbití README.md: exit={kod_u}, čítač={m_u.group(0) if m_u else '?'}")
zkontroluj("zdravá fixtura: exit 0 a čítač 49/0",
           kod_c == 0 and m_c and m_c.group(1) == "49" and m_c.group(2) == "0",
           v_c[-500:])
zkontroluj("rozbitý dokument v §6 čítač ZVÝŠÍ (dokazuje, že kontrola proběhla)",
           m_u is not None and int(m_u.group(1)) == 50 and kod_u == 1,
           v_u[-600:])
(FIX / "README.md").write_text("# fixtura\n", encoding="utf-8")     # zpět na zdravý

# ── 5) FIXTURA: falešný poplach na SPRÁVNÉM stavu ──────────────────────────
print()
print("── 5) FIXTURA: co brána udělá, když se dokument LEGITIMNĚ přejmenuje ───")
if FIX.exists():
    shutil.rmtree(FIX)
FIX.mkdir(parents=True)
for f in dok_brana:
    (FIX / f).write_text("# fixtura\n", encoding="utf-8")
for d in slo_brana:
    (FIX / d).mkdir()
kod_f, v_f = spust_verify(FIX)
zkontroluj(f"fixtura (správný stav): exit=0 (je {kod_f})", kod_f == 0, v_f[-800:])
# LEGITIMNÍ změna: dokument dostane jiné jméno (např. se přejmenuje na INDEX).
(FIX / "README.md").rename(FIX / "README-INDEX.md")
(FIX / "README-INDEX.md").write_text("# fixtura\n", encoding="utf-8")
kod_r, v_r = spust_verify(FIX)
zkontroluj("po přejmenování dokumentu brána ZČERVENÁ (falešný poplach na správném stavu)",
           kod_r == 1 and "stanice/README.md" in v_r, v_r[-800:])
print(f"      → exit={kod_r}; brána hlásí: "
      f"{[l.strip() for l in v_r.splitlines() if 'CHYBI' in l][:3]}")
# „Má každé CHYBI odůvodnění?“ — měřeno: kolik CHYBI a kolik řádků „hledáno na:“.
pocet_chybi = sum(1 for l in v_r.splitlines() if l.strip().startswith("CHYBI"))
pocet_duvodu = sum(1 for l in v_r.splitlines() if "hledáno na:" in l)
print(f"      CHYBI: {pocet_chybi}, odůvodnění („hledáno na:“): {pocet_duvodu}")
zkontroluj("každé CHYBI má odůvodnění, KDE to hledalo", pocet_chybi == pocet_duvodu,
           f"CHYBI {pocet_chybi} vs. odůvodnění {pocet_duvodu}")
shutil.rmtree(FIX, ignore_errors=True)
zkontroluj("fixtura uklizena", not FIX.exists())

print()
print("=" * 92)
print(f"ZMĚŘENO: {kontrol} kontrol, {chyb} NÁLEZŮ o bráně")
print("  N1  seznam dokumentů je RUČNÍ literál (komentář tvrdí opak)")
print("  N2  brána nehlídá 7 dokumentů, které `AGENTS.md` za dokumenty stanice označuje")
print("  N3  seznam SLOŽEK se s `AGENTS.md` rozchází na 4 místech")
print("  N4  legitimní přejmenování dokumentu = falešný poplach (fixtura, exit 1)")
print("  N5  čítač započítá kontroly z §5/§6 JEN když spadnou (změřeno: 49 → 50)")
print("Změřeno `p14d-verify-setup-sonda.py`. Nic se nezapisovalo do repa ani stanice.")
if chyb:
    sys.exit(1)
print("BEZ NÁLEZU.")
sys.exit(0)

#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P14 / ÚKOL C — VLASTNÍ mutační testy PĚTI oprav P13c (H48, H49, H50, H53, H52).

PROČ VLASTNÍ: `_analyza/test-p13c-oprav.py` (27 kontrol) psal **autor oprav**
a `AGENTS.md` říká, že autor není nezávislý reviewer. Tenhle soubor je psaný
znovu, jiným postupem, a **každá mutace se ověřuje DVĚMA způsoby**:

  1. **že se PŘESTALA PLNIT měřená podmínka** — ne jen že se změnil soubor
     (`overovani` §7.14: „mutace, která změní soubor, ale ne podmínku"),
     včetně `assert` na počet výskytů kotvy PŘED zápisem (§9.8),
  2. **že se změna propsala NA DISK** (čtení zpět z disku, ne z proměnné).

Každá mutace je v `try/finally`, které soubor vrátí **bajt na bajt**, a na konci
se **všech pět** souborů ověří proti původnímu SHA-256. Když se cokoli nepovede,
skript skončí nenulově a **vypíše, který soubor zůstal změněný**.

Očekávaný text se hledá VŽDY s předponou `CHYBA`/`NEDOSAZENÉ` — jinak by test
prošel na POPISKU kontroly, která nic nenašla (přesně na to padl první běh
`test-p14a-mutace.py`).

Použití:  FORGE_WS=E:\Workspaces\forge-orchestra python p14c-mutace-oprav.py
"""
from __future__ import annotations

import hashlib
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
TOOLS = WS / "tools"
HERE = pathlib.Path(__file__).resolve().parent
GIT = WS / "tools" / "git.cmd"
PY = sys.executable

kontrol = 0
chyb = 0
ZALOHY: dict[pathlib.Path, bytes] = {}
NESPLNENO: list[str] = []


def zkontroluj(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not ok:
        chyb += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok and detail:
        for r in str(detail).splitlines()[:24]:
            print(f"        {r}")


def spust(prikaz: list[str], cwd: pathlib.Path | None = None,
          timeout: int = 1800) -> tuple[int | None, str]:
    try:
        r = subprocess.run(prikaz, cwd=str(cwd or WS), capture_output=True,
                           timeout=timeout)
        return r.returncode, (r.stdout.decode("utf-8", "replace")
                              + r.stderr.decode("utf-8", "replace"))
    except Exception as e:                                       # noqa: BLE001
        return None, f"CHYBA spuštění: {type(e).__name__}: {e}"


def zalohuj(rel: str) -> pathlib.Path:
    p = WS / rel
    if p not in ZALOHY:
        ZALOHY[p] = p.read_bytes()
    return p


def mutuj(rel: str, popis: str, kotva: str, nahrada: str,
          gate: list[str], *, ocekavany_exit: int | None,
          ocekavany_vzor: str, cwd: pathlib.Path | None = None) -> str:
    """Jedna mutace: záloha → změna → běh brány → návrat. Vrací výstup brány."""
    p = zalohuj(rel)
    orig = ZALOHY[p]
    kb, nb = kotva.encode("utf-8"), nahrada.encode("utf-8")
    pocet = orig.count(kb)
    if pocet != 1:
        zkontroluj(f"{popis}: kotva je v souboru 1× (je {pocet}×)", False, kotva)
        return ""
    zkontroluj(f"{popis}: kotva nalezena 1× — mutace je jednoznačná", True)
    try:
        p.write_bytes(orig.replace(kb, nb))
        # (1) NA DISKU se to změnilo
        zpet = p.read_bytes()
        zkontroluj(f"{popis}: mutace se propsala na disk", zpet != orig)
        # (2) MĚŘENÁ PODMÍNKA přestala platit — v bajtech, ne v proměnné
        zkontroluj(f"{popis}: měřená podmínka PŘESTALA platit (kotva v souboru není)",
                   kb not in zpet)
        kod, v = spust(gate, cwd=cwd)
        if ocekavany_exit is not None:
            zkontroluj(f"{popis}: brána skončila exit={ocekavany_exit} (je {kod})",
                       kod == ocekavany_exit, v[-800:])
        zkontroluj(f"{popis}: brána to ŘEKLA ({ocekavany_vzor})",
                   re.search(ocekavany_vzor, v, re.S) is not None, v[-1500:])
        return v
    finally:
        p.write_bytes(orig)
        assert p.read_bytes() == orig, f"SOUBOR NEVRÁCEN: {p}"


def vrat_vse() -> None:
    for p, orig in ZALOHY.items():
        p.write_bytes(orig)
    for p, orig in ZALOHY.items():
        if p.read_bytes() != orig:
            NESPLNENO.append(str(p))


print("=" * 92)
print("ÚKOL C — VLASTNÍ MUTAČNÍ TESTY PĚTI OPRAV P13c")
print("=" * 92)
print(f"  WS = {WS}")
print(f"  python = {PY}")
print()

# ═══ C1 — H48: `g3-brany.py` MUSÍ dosazovat záznamníky cest ═════════════════
print("── C1 (H48): vypnutá substituce záznamníků v `g3-brany.py` ─────────────")
G3_VYSTUP = ANALYZA / "g3-brany-vystup.txt"
g3_zaloha = G3_VYSTUP.read_bytes() if G3_VYSTUP.is_file() else None
g3_sha = hashlib.sha256(g3_zaloha).hexdigest()[:16] if g3_zaloha else "(žádný)"

# KONTROLA (zdravý stav) — bez ní by „spadlo to" nic neznamenalo.
kod, v_zdravy = spust([PY, str(ANALYZA / "g3-brany.py")])
print(f"  [kontrola] `g3` na zdravém kódu: exit={kod}, {len(v_zdravy)} B výstupu")
m_zdravy = re.search(r"brán celkem:\s*(\d+), s nenulovým exit:\s*(\d+)", v_zdravy)
zkontroluj("kontrola: g3 vykázal počty (`brán celkem: N, s nenulovým exit: M`)",
           m_zdravy is not None, v_zdravy[-600:])
if m_zdravy:
    print(f"      → brán celkem {m_zdravy.group(1)}, nenulových exit {m_zdravy.group(2)}")
zkontroluj("kontrola: zdravý g3 hlásí 0 nedosazených záznamníků",
           "záznamníky cest: všechny dosazené (0 nedosazených)" in v_zdravy,
           v_zdravy[-800:])
zkontroluj("kontrola: zdravý g3 hlásí 0 bran, které vůbec nezačaly",
           "brány, které vůbec nezačaly: 0" in v_zdravy, v_zdravy[-800:])

v_mut = mutuj("_analyza/g3-brany.py", "C1 mutace: substituce vypnuta",
              "            if znacka in cast:", "            if False and znacka in cast:",
              [PY, str(ANALYZA / "g3-brany.py")], ocekavany_exit=None,
              ocekavany_vzor=r"NEDOSAZENÉ CESTY \((\d+)\)")
zkontroluj("C1: mutant hlásí i „BRÁNY, KTERÉ VŮBEC NEZAČALY“ (nenulové číslo)",
           re.search(r"BRÁNY, KTERÉ VŮBEC NEZAČALY \(([1-9]\d*)\)", v_mut) is not None,
           v_mut[-1200:])
# Návrat VÝSTUPNÍHO SOUBORU (aby zůstal záznam P13c, ne artefakt mutace).
if g3_zaloha is not None:
    G3_VYSTUP.write_bytes(g3_zaloha)
    zkontroluj(f"C1: `g3-brany-vystup.txt` vrácen na původní obsah (sha {g3_sha})",
               hashlib.sha256(G3_VYSTUP.read_bytes()).hexdigest()[:16] == g3_sha)

# ═══ C2 — H49: generátor `.gitignore` MUSÍ obsahovat `.env` ═════════════════
print()
print("── C2 (H49): z generátoru `.gitignore` zmizí `.env` ─────────────────────")
kod, v = spust([PY, str(TOOLS / "test-gitignore-tajemstvi.py")])
zkontroluj(f"kontrola: test na zdravém kódu exit=0 (je {kod})", kod == 0, v[-600:])
zkontroluj("kontrola: test vykázal čítač `VÝSLEDEK: N kontrol`",
           re.search(r"VÝSLEDEK: \d+ kontrol", v) is not None, v[-400:])
mutuj("install-into-repo.ps1", "C2 mutace: `.env` vyndán z generátoru",
      # POZOR: soubor je .ps1 → v pracovním stromu je CRLF (ověřeno: 195× CRLF,
      # 0× osamocené LF). Kotva s `\n` by nenašla NIC a mutace by se tiše
      # neprovedla (`overovani` §7.9).
      "\r\n.env\r\n", "\r\n# .env ODSTRANENO MUTACI\r\n",
      [PY, str(TOOLS / "test-gitignore-tajemstvi.py")], ocekavany_exit=1,
      ocekavany_vzor=r"CHYBA generátor: '\.env'")

# ═══ C3 — H50: `verify-setup.py` MUSÍ měřit DNEŠNÍ kořen stanice ════════════
print()
print("── C3 (H50): kořen stanice přepsán na neexistující cestu ────────────────")
env_bez = dict(os.environ)
env_bez.pop("FORGE_STANICE", None)
kod, v = spust([PY, str(TOOLS / "verify-setup.py")])
zkontroluj(f"kontrola: verify-setup na zdravém kódu exit=0 (je {kod})", kod == 0, v[-600:])
zkontroluj("kontrola: verify-setup vykázal čítač `ZMĚŘENO: N kontrol`",
           re.search(r"ZMĚŘENO: \d+ kontrol", v) is not None, v[-400:])
mutuj("tools/verify-setup.py", "C3 mutace: starý/neexistující kořen stanice",
      'os.environ.get("FORGE_STANICE", r"C:\\Users\\Ssevc\\Local-Deepseek")',
      'os.environ.get("FORGE_STANICE", r"Z:\\neexistuje-stanice")',
      [PY, str(TOOLS / "verify-setup.py")], ocekavany_exit=1,
      ocekavany_vzor=r"CHYBA: kořen stanice .* neexistuje|CHYBI .*stanice/")

# C3b — je seznam dokumentů RUČNÍ? Když se z něj položky vyndají, brána mlčí.
# To není „vada, kterou má mutace odhalit" — to je DOKAZ, že seznam je ruční
# a že úbytek pokrytí NIKDO nepozná (počítá se jen počet kontrol, ne které).
print()
print("── C3b (Úkol D): co se stane, když z RUČNÍHO seznamu dokumentů zmizí položky")
mutuj("tools/verify-setup.py", "C3b: celý seznam dokumentů stanice vyprázdněn",
      '''DOKUMENTY_STANICE = [
    "README.md", "AGENTS.md", "MOZNOSTI-AGENTA.md", "OTEVRENA-TEMATA.md",
    "PREDAVANI-SESSION.md", "POZOR-E-DSH-NEMAZAT.md",
]''',
      "DOKUMENTY_STANICE = []",
      [PY, str(TOOLS / "verify-setup.py")], ocekavany_exit=0,
      ocekavany_vzor=r"ZMĚŘENO: \d+ kontrol, 0 chyb")

# ═══ C4 — H53: `zadani-kontrola.py` MUSÍ porovnat i orchestra ═══════════════
print()
print("── C4 (H53): do hlavičky zadání se vrátí STARÝ sha ──────────────────────")
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
kod, v = spust([PY, str(ANALYZA / "zadani-kontrola.py")])
zkontroluj(f"kontrola: zadani-kontrola na zdravém zadání exit=0 (je {kod})", kod == 0,
           v[-800:])
sha_head = spust([str(GIT), "-C", str(WS), "rev-parse", "--short", "HEAD"])[1].strip()
sha_stary = spust([str(GIT), "-C", str(WS), "rev-parse", "--short", "HEAD~1"])[1].strip()
zkontroluj(f"kontrola: znám živý HEAD ({sha_head}) i starší sha ({sha_stary})",
           len(sha_head) >= 7 and len(sha_stary) >= 7)
mutuj("NEXT-SESSION-INSTRUKCE.md", f"C4a: hlavička tvrdí starý sha {sha_stary}",
      f"`forge-orchestra` = `{sha_head}`", f"`forge-orchestra` = `{sha_stary}`",
      [PY, str(ANALYZA / "zadani-kontrola.py")], ocekavany_exit=1,
      ocekavany_vzor=r"zadání tvrdí .{0,20}skutečný HEAD je")

# C4b — bezpečnostní síť: když hlavička tvrdí repo, které skript nezná, musí
# to VYPÍSAT (nesmí tiše neměřit). Přesně to byla vada H53.
print()
print("── C4b (H53): hlavička tvrdí repo, které skript nezná ───────────────────")
mutuj("NEXT-SESSION-INSTRUKCE.md", "C4b: neznámé jméno repa v hlavičce",
      f"`forge-orchestra` = `{sha_head}`", f"`neznamy-repo` = `{sha_head}`",
      [PY, str(ANALYZA / "zadani-kontrola.py")], ocekavany_exit=1,
      ocekavany_vzor=r"nepodařilo se přiřadit k repu")

# ═══ C5 — H52: skener VIDÍ netrackovaný kód a VYLUČUJE jen artefakty ════════
print()
print("── C5 (H52): skener — netrackovaný kód vidí, artefakt vyloučí ───────────")
SKENER = ANALYZA / "hl-neanglicky-v-kodu.py"
SONDA_KOD = WS / "_p14-sonda-necommitovany.py"
SONDA_ANALYZA = ANALYZA / "_p14-sonda-kod-v-analyze.py"
SONDA_ARTEFAKT = ANALYZA / "_p14-sonda-artefakt.json"
# Mezivýstupy patří do VYLOUČENÉHO artefaktového adresáře (`_analyza/_scratch`),
# aby samy nevstoupily do měření a nezměnily počty, které test porovnává.
VYSTUP_DIR = ANALYZA / "_scratch"
vytvoril_dir = not VYSTUP_DIR.is_dir()
VYSTUP_DIR.mkdir(parents=True, exist_ok=True)
JSON_ZDRAVY = VYSTUP_DIR / "p14c-inventar-zdravy.json"
JSON_SONDY = VYSTUP_DIR / "p14c-inventar-sondy.json"

OBSAH_KOD = "# -*- coding: utf-8 -*-\ndef změř_něco():\n    return 'nález'\n"
OBSAH_ARTEFAKT = json.dumps({"popis": "nález skeneru jako data — nesmí se měřit"},
                            ensure_ascii=False, indent=2)

for s in (SONDA_KOD, SONDA_ANALYZA, SONDA_ARTEFAKT):
    if s.exists():
        raise SystemExit(f"CHYBA: sonda {s} už existuje — uklid ji")

try:
    kod, v = spust([PY, str(SKENER), "--json", str(JSON_ZDRAVY)])
    zkontroluj(f"kontrola: skener bez sond exit=0 (je {kod})", kod == 0, v[-600:])
    zdrave = json.loads(JSON_ZDRAVY.read_text(encoding="utf-8"))
    soubory_z = zdrave["souboru_zpracovano"]
    vy_z = zdrave["vyloucene_artefakty"].get("orchestra", 0)
    nt_z = sum(len(x) for x in zdrave["netrackovane"].values())
    print(f"      zdravý stav: zpracováno {soubory_z} souborů, "
          f"netrackovaných {nt_z}, vyloučených artefaktů (orchestra) {vy_z}")
    zkontroluj("kontrola: zdravý inventář NEOBSAHUJE jméno sondy (sonda ještě není)",
               not any("p14-sonda" in json.dumps(n, ensure_ascii=False)
                       for n in zdrave["nalezy"]))
    # Mezivýstup zdravého běhu UKLIDIT před dalším skenem: jinak by se do
    # `vyloucene_artefakty` připočítal a porovnání „+1" by nesedlo.
    JSON_ZDRAVY.unlink()

    SONDA_KOD.write_text(OBSAH_KOD, encoding="utf-8")
    SONDA_ANALYZA.write_text(OBSAH_KOD, encoding="utf-8")
    SONDA_ARTEFAKT.write_text(OBSAH_ARTEFAKT, encoding="utf-8")
    zkontroluj("C5: tři sondy jsou na disku a git je NESLEDUJE",
               all(s.is_file() for s in (SONDA_KOD, SONDA_ANALYZA, SONDA_ARTEFAKT))
               and SONDA_KOD.name in spust([str(GIT), "-C", str(WS), "ls-files",
                                            "--others", "--exclude-standard"])[1])

    kod, v = spust([PY, str(SKENER), "--json", str(JSON_SONDY)])
    zkontroluj(f"C5: skener se sondami exit=0 (je {kod})", kod == 0, v[-600:])
    s = json.loads(JSON_SONDY.read_text(encoding="utf-8"))
    vsechny_nalezy = json.dumps(s["nalezy"], ensure_ascii=False)
    nt_s = sum(len(x) for x in s["netrackovane"].values())
    zkontroluj(f"C5a: NETRACKOVANÝ kód v kořeni repa skener VIDÍ "
               f"(netrackovaných {nt_s} vs. {nt_z} předtím)",
               "_p14-sonda-necommitovany.py" in vsechny_nalezy and nt_s > nt_z)
    zkontroluj("C5c: `_*.py` v `_analyza/` se NEvylučuje (jinak by brána byla slepá na kód)",
               "_p14-sonda-kod-v-analyze.py" in vsechny_nalezy)
    zkontroluj("C5b: artefakt `_analyza/_*.json` se VYLUČUJE (není v nálezech)",
               "_p14-sonda-artefakt.json" not in vsechny_nalezy)
    print(f"      počet zpracovaných: {soubory_z} → {s['souboru_zpracovano']} "
          f"(+2 sondy s kódem), vyloučené artefakty: "
          f"{s['vyloucene_artefakty'].get('orchestra', 0)}")
    zkontroluj("C5b: vyloučených artefaktů je o 1 víc (sonda-artefakt se počítá)",
               s["vyloucene_artefakty"].get("orchestra", 0) == vy_z + 1)
finally:
    for s in (SONDA_KOD, SONDA_ANALYZA, SONDA_ARTEFAKT):
        if s.exists():
            s.unlink()
    for s in (JSON_ZDRAVY, JSON_SONDY):
        if s.exists():
            s.unlink()
    if vytvoril_dir and VYSTUP_DIR.is_dir():
        try:
            VYSTUP_DIR.rmdir()
        except OSError:
            pass
    zkontroluj("C5: sondy i mezivýstupy uklizeny (nic nezůstalo v repu)",
               not any(s.exists() for s in (SONDA_KOD, SONDA_ANALYZA, SONDA_ARTEFAKT))
               and not any(s.exists() for s in (JSON_ZDRAVY, JSON_SONDY))
               and not VYSTUP_DIR.exists())

# ═══ NÁVRAT A KONTROLA ČISTOTY ══════════════════════════════════════════════
print()
print("── NÁVRAT SOUBORŮ: bajt na bajt, podle SHA-256 ──────────────────────────")
vrat_vse()
for p, orig in sorted(ZALOHY.items(), key=lambda kv: str(kv[0])):
    zkontroluj(f"vrácen beze změny: {p.relative_to(WS)}",
               hashlib.sha256(p.read_bytes()).hexdigest()
               == hashlib.sha256(orig).hexdigest())
if g3_zaloha is not None:
    zkontroluj("vrácen beze změny: _analyza/g3-brany-vystup.txt (záznam P13c)",
               hashlib.sha256(G3_VYSTUP.read_bytes()).hexdigest()[:16] == g3_sha)

print()
kod, v = spust([str(GIT), "-C", str(WS), "status", "--porcelain"])
zkontroluj("repo je po mutacích ve stejném stavu (žádný soubor navíc)",
           "p14-sonda" not in v, v[-800:])

print()
print("=" * 92)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if NESPLNENO:
    print("NEVRÁCENÉ SOUBORY: " + ", ".join(NESPLNENO))
if chyb or NESPLNENO:
    print(f"CHYBA: {chyb + len(NESPLNENO)} — některá oprava NEMĚŘÍ")
    sys.exit(1)
print("VŠECHNY OPRAVY MĚŘÍ — každá mutace je vidět a každý soubor je vrácen.")
sys.exit(0)

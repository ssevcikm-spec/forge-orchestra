"""P8 — OPRAVA CEST V `_analyza\\` (nastroje projektu, ktere zustaly v repu).

PROC SAMOSTATNE: `_analyza/` bylo do repa presunuto CELY (D3) a jeho skripty
odkazuji stary koren dvema zpusoby:
  a) `WS = Path(r"C:\\Users\\Ssevc\\Local-Deepseek")` — koren STANICE, kde
     zustaly dokumenty (README, POZOR-E-DSH-NEMAZAT, ...). Tohle je D6.
  b) `WS` nebo `HRA` — cesta do repa,
     ktera se presunem ROZPADLA (orchestra je dnes root repa, hra je sourozenec).

ODVOZENI: `_analyza/x.py` je v `REPO/_analyza/`, takze
  REPO    = Path(__file__).resolve().parents[1]
  STANICE = Path(r"C:\\Users\\Ssevc\\Local-Deepseek")   (zustava)
  HRA     = REPO.parent / "uo-shadows"                   (sourozenec)

BEZPECNOST: stejna jako u `p8-oprava-cest.py` — po zapisu se parsuje
(`ast.parse` / `node --check`) a kontroluji se podezrela jmena; pri chybe se
soubor VRATI ze zalohy.

Pouziti: python p8b-oprava-analyza.py [--kontrola]
"""
from __future__ import annotations

import ast
import re
import shutil
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

REPO = Path(r"E:\Workspaces\forge-orchestra")
ANALYZA = REPO / "_analyza"
LOG = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\p8b-oprava-analyza-log.txt")
ZALOHA = Path(r"C:\Users\Ssevc\Local-Deepseek\_analyza\zaloha-p8b")

# jen zive nastroje (D5: 18 zivych dle AGENTS.md; ostatni se archivuji a jejich
# cesty se NEopravuji — plosna oprava mrtvych jednorazovek je presne to, co D5
# zamitlo)
ZIVE = {
    "a1-a2-over.py", "a1-a2-mutace.py", "a3-over.py", "a3-mutace.py",
    "n8-zastarala-analyza.py", "n8-mutace.py", "b5-over-tvrzeni.py",
    "n1-over-inventar.py", "ag-over-cisla.py", "ag-mutace.py",
    "ag-presun-uplnost.py", "audit-snapshot.py", "audit-snapshot-over.py",
    "audit2a-mutace.py", "audit2b-over.py", "audit3-hlavicky-over.py",
    "hl2-kontrola.py", "hl2-mutace-kontrola.py", "hl2-kostra-test.py",
    "hl2-kostra-kalibrace.py", "hl-neanglicky-v-kodu.py", "hl-rizika-jazyka.py",
    "test-neanglicky-skener.py", "js-tokeny.mjs", "hl2-soubeh.py",
    "hl2-casova-osa.py", "hl2-nic-nezmizelo.py", "hl2-rozbal-session2.mjs",
    "kronika-kontrola.py", "zadani-kontrola.py", "sken-cest-celek.py",
    "skryte-vazby-na-hru.py", "sken-vazeb.py", "z8-probe.py",
    "handoff-kontrola-uplnost.py", "dsh-session-prehled.mjs", "over-okno.mjs",
    "p1-inventura-cest.py", "p1b-odvozene-cesty.py", "p3-bazline.py",
    "p8-oprava-cest.py", "p9-presun-dokumentu.py", "ps1-bom-crlf.py",
    "p8b-oprava-analyza.py",
}

HLAVICKA_PY = (
    "# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze\n"
    "#   REPO    = root repa (_analyza/.. )\n"
    "#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)\n"
    "#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)\n"
    "import pathlib as _pl\n"
    "_REPO = _pl.Path(__file__).resolve().parents[1]\n"
    "_STANICE = _pl.Path(r\"C:\\Users\\Ssevc\\Local-Deepseek\")\n"
    "_HRA = _REPO.parent / \"uo-shadows\"\n"
)

radky: list[str] = []
chyby: list[str] = []


def zapis(t: str) -> None:
    print(t)
    radky.append(t)


def oprav(text: str, jmeno: str, je_py: bool) -> tuple[str, int]:
    """Nahradi literal cesty vyrazem. Vraci (text, pocet)."""
    vzor = re.compile(
        r"""[rR]?(?P<q>['"])"""
        r"""C:[\\/]Users[\\/]Ssevc[\\/]Local-Deepseek"""
        r"""(?P<zbytek>(?:[\\/][A-Za-z0-9_.\- ]+)*)"""
        r"""(?P=q)"""
    )

    def nahrad(m: re.Match) -> str:
        normal = "/" + m.group("zbytek").replace("\\", "/").strip("/")
        niz = normal.lower()
        if niz.startswith("/orchestra/repo"):
            return vyraz("_REPO", "/repo" + normal[len("/orchestra/repo"):], je_py)
        if niz.startswith("/orchestra"):
            return vyraz("_REPO", normal[len("/orchestra"):], je_py)
        if niz.startswith("/games/uo-shadows"):
            return vyraz("_HRA", normal[len("/games/uo-shadows"):], je_py)
        if niz.startswith("/games"):
            return vyraz("_REPO.parent", normal[len("/games"):], je_py)
        if niz.startswith("/_analyza"):
            return vyraz("_REPO", normal[len("/_analyza"):] and "/_analyza" + normal[len("/_analyza"):], je_py)
        # koren samotny = STANICE (zustal na C:)
        return vyraz("_STANICE", normal, je_py)

    pocet = len(vzor.findall(text))
    return vzor.sub(nahrad, text), pocet


def vyraz(zaklad: str, zbytek: str, je_py: bool) -> str:
    casti = [c for c in zbytek.replace("\\", "/").split("/") if c]
    if je_py:
        return zaklad + "".join(f" / {c!r}" for c in casti)
    return zaklad + "".join(f" + {'/' + c!r}" for c in casti)


def parsuje_ok(p: Path) -> tuple[bool, str]:
    if p.suffix.lower() == ".py":
        try:
            text = p.read_text(encoding="utf-8")
            ast.parse(text)
        except SyntaxError as e:
            return False, f"SyntaxError: {e}"
        spatne = [x for x in re.findall(r"\br_?\w+", text) if x.startswith("r_")]
        if spatne:
            return False, f"podezřelá jména: {sorted(set(spatne))}"
        return True, ""
    if p.suffix.lower() in (".mjs", ".js"):
        r = subprocess.run(["node", "--check", str(p)], capture_output=True,
                           text=True, encoding="utf-8", errors="replace")
        return (r.returncode == 0), (r.stderr or "")[:200]
    return True, ""


def main(argv: list[str]) -> int:
    kontrola = "--kontrola" in argv
    ZALOHA.mkdir(parents=True, exist_ok=True)
    zmenene = 0
    for p in sorted(ANALYZA.glob("*")):
        if not p.is_file() or p.name not in ZIVE:
            continue
        if p.suffix.lower() not in (".py", ".mjs", ".js"):
            continue
        text = p.read_text(encoding="utf-8")
        if "Local-Deepseek" not in text:
            continue
        je_py = p.suffix.lower() == ".py"
        novy, pocet = oprav(text, p.name, je_py)
        if pocet == 0 or novy == text:
            continue
        if "Local-Deepseek" in novy:
            # muze zustat jen v komentari/docstringu — to je v poradku, hlásíme
            zapis(f"  ~ {p.name}: {pocet} nahrad, zbytek 'Local-Deepseek' "
                  f"(komentar?)")
        if kontrola:
            zapis(f"  {p.name}: {pocet} nahrad (KONTROLA)")
            continue
        if je_py and "_STANICE = _pl.Path" not in novy:
            novy = HLAVICKA_PY + novy
        zal = ZALOHA / p.name
        shutil.copy2(p, zal)
        p.write_text(novy, encoding="utf-8", newline="")
        ok, msg = parsuje_ok(p)
        if not ok:
            shutil.copy2(zal, p)
            zapis(f"  ✗ {p.name}: VRÁCENO ({msg})")
            chyby.append(f"{p.name}: {msg}")
        else:
            zmenene += 1
            zapis(f"  ✓ {p.name}: {pocet} nahrad, parser OK")
    zapis("")
    zapis(f"změněno: {zmenene}, chyb: {len(chyby)}")
    for c in chyby:
        zapis(f"  CHYBA: {c}")
    LOG.write_text("\n".join(radky) + "\n", encoding="utf-8", newline="\n")
    return 1 if chyby else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))

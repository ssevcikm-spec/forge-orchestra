# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""Nic nezmizelo pri presunu obecnych pravidel z rootu do DSH_HOME.

PRAVIDLO, KTERE TO OVERUJE (`AGENTS.md` / skill `dokumentace`):
  „Pri prepsani stavu NIC NESMI ZMIZET. Po prepsani VYPIS, ktere body zustaly,
   a over je HLEDANIM, ne pameti."

POSTUP: kazde pravidlo z puvodniho souboru je reprezentovano klicovym
retezcem, ktery se v originale VYSKYTUJE. Skript hleda ten retezec v novych
domovech a vypise, KDE ho nasel. Kdyz ho nenajde nikde, je to nález.

  vstupy:  zaloha puvodniho AGENTS.md (_analyza/zaloha/…pred-presunem…)
  domovy:  root AGENTS.md + DSH_HOME AGENTS.md + 3 skilly

KALIBRACE (jako u kazde metriky): skript ma i DVE SONDY, ktere se najit
NESMI. Kdyby je nasel, hleda spatne (podretezec, cizi soubor) a jeho
„vsechno nalezeno" nic neznamena.
"""
from __future__ import annotations

import sys
from pathlib import Path

WS = Path(_STANICE)
DSH = Path(r"C:\Users\Ssevc\.dsh")
ZALOHA = WS / "_analyza" / "zaloha" / "AGENTS.md.pred-presunem-2026-10-04.md"

DOMOVY = [
    ("root AGENTS.md", WS / "AGENTS.md"),
    ("DSH_HOME AGENTS.md", DSH / "AGENTS.md"),
    ("skill dokumentace", DSH / "skills" / "dokumentace" / "SKILL.md"),
    ("skill dsh-prostredi", DSH / "skills" / "dsh-prostredi" / "SKILL.md"),
    ("skill overovani", DSH / "skills" / "overovani" / "SKILL.md"),
]

# (klicovy retezec z originale, kde ma byt - informativne)
PRAVIDLA: list[tuple[str, str]] = [
    # --- prostredi ---
    ("Select-String -SimpleMatch", "obecne"),
    ("PYTHONIOENCODING", "obecne"),
    ("UTF-8 BOM", "obecne"),
    ("TLS z PowerShellu nefunguje", "obecne"),
    ("nikdy ho nevypisuj", "obecne"),
    ("EPERM", "obecne"),
    ("Zapisuj do workspace", "obecne"),
    ("Measure-Object -Line", "obecne"),
    ("splitlines", "obecne"),
    # --- jak overovat ---
    ("známém správném", "obecne"),
    ("NAPSANÁ NAPEVNO", "obecne"),
    ("nezměřeno", "obecne"),
    ("proběhla?", "obecne"),
    ("odstraň komentáře", "obecne"),
    ("sys.exit", "obecne"),
    ("Vrať do kódu vadu", "obecne"),
    ("read_image", "obecne"),
    ("Mrtvá větev", "obecne"),
    ("Nefunkční metriku smazat", "obecne"),
    ("nemá jak selhat", "obecne"),
    ("CITACI MÍSTO TVRZENÍ", "obecne"),
    ("5 441", "obecne"),
    ("pojmenované skupiny", "obecne"),
    ("diff-filter=D", "obecne"),
    # --- dokumentace ---
    ("DATUM SPOTŘEBY", "obecne"),
    ("ČÍM JE", "obecne"),
    ("různé čítače", "obecne"),
    ("merged_by", "obecne"),
    ("NÁZVU REPA", "obecne"),
    ("ještě neexistuje", "obecne"),
    ("skill není šablona", "obecne"),
    ("Znalost patří k naměřenému příkladu", "obecne"),
    # --- jazyk / session / nikdy ---
    ("ROZHRANÍ = ASCII", "obecne"),
    ("nezávislosti pohledu", "obecne"),
    ("Nepushovat bez vyžádání", "obecne"),
    # --- projektove (zustava v rootu) ---
    ("forge-quest", "projekt"),
    ("KDO MĚNÍ KÓD, PŘEGENERUJE", "projekt"),
    ("JE TVRZENÍ, NE DŮKAZ", "projekt"),
    ("world.map", "projekt"),
    ("zjisti-pages.mjs", "projekt"),
    ("index.png", "projekt"),
    ("KRONIKA-PROJEKTU.md", "projekt"),
    ("handoff-kontrola-uplnost.py", "projekt"),
    ("hl-neanglicky-v-kodu.py", "projekt"),
    ("a1-a2-over.py", "projekt"),
    ("schema.sql", "projekt"),
    ("S27", "projekt"),
]

# Sondy: tyhle se NESMI najit. Kdyby se nasly, hleda skript spatne.
SONDY = [
    "TENTO RETEZEC V ZADNEM DOKUMENTU NENI",
    "forbiny-a-jine-vymysly",
]


def main() -> int:
    if not ZALOHA.is_file():
        print(f"CHYBA: zaloha neexistuje ({ZALOHA})")
        return 2
    obsah = {}
    for jmeno, cesta in DOMOVY:
        if not cesta.is_file():
            print(f"CHYBA: domov neexistuje: {jmeno} ({cesta})")
            return 2
        obsah[jmeno] = cesta.read_text(encoding="utf-8")
    original = ZALOHA.read_text(encoding="utf-8")

    print("=" * 78)
    print("NIC NEZMIZELO — přesun obecných pravidel (4. 10. 2026)")
    print("=" * 78)
    print(f"  original: {ZALOHA.name} ({len(original)} znaků)")
    for jmeno, text in obsah.items():
        print(f"  {jmeno:24} {len(text):7} znaků")
    print()

    # Kalibrace: sondy se nesmi najit nikde.
    for sonda in SONDY:
        kde = [j for j, t in obsah.items() if sonda in t]
        if kde:
            print(f"  ✗ KALIBRACE SELHALA: sonda {sonda!r} nalezena v {kde}")
            return 2
    print(f"  kalibrace: {len(SONDY)} sondy se nenašly nikde — hledá se správně")
    print()

    chybi = []
    for pravidlo, kam in PRAVIDLA:
        nalezeno = [j for j, t in obsah.items() if pravidlo in t]
        if not nalezeno:
            chybi.append(pravidlo)
            print(f"  ✗ ZMIZELO  {pravidlo!r}  (mělo by být: {kam})")
        else:
            print(f"  OK  {pravidlo[:38]:40} → {', '.join(nalezeno)[:60]}")

    print()
    print(f"  pravidel: {len(PRAVIDLA)} | nalezeno: {len(PRAVIDLA) - len(chybi)} | "
          f"ZMIZELO: {len(chybi)}")
    if chybi:
        print()
        print("ZÁVĚR: přesun ztratil obsah. Doplnit do správného domova —")
        print("a v dokumentu, odkud se přesouvalo, uvést, kam.")
        return 1
    print()
    print("ZÁVĚR: každé pravidlo z původního souboru je v některém z nových domovů.")
    print("(Kontrolují se KLÍČOVÉ věty, ne doslovné znění — text se při přesunu")
    print(" zkracoval tam, kde detail už nesl skill.)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
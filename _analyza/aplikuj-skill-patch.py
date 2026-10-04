"""Aplikuje záplaty skillů NAOSTRO — potřebuje zápis mimo workspace.

Skilly leží v `C:\\Users\\Ssevc\\.dsh\\skills`, tedy mimo workspace, a sandbox
`workspace-write` tam zápis odmítá. Tenhle skript je určený pro session
s **širším oprávněním** (rodičovská session / uživatel).

Spuštění:
    $env:PYTHONIOENCODING='utf-8'
    python _analyza\\aplikuj-skill-patch.py

Co dělá, v tomto pořadí (nic se nezapisuje dřív, než je všechno ověřené):
  1. pro každý skill spočítá cílové bajty a ověří **všechny anchory** (1x),
     frontmatter bajt na bajt a zachování konců řádků,
  2. když se cílové bajty rovnají současnému stavu → **už aplikováno**, přeskočí,
  3. zálohu uloží do `_analyza\\zaloha\\` (skills složka zůstane čistá),
  4. zapíše bajty a **přečte je zpátky** — ověří, že na disku opravdu jsou,
  5. na konci spustí `over-skilly.py` (stdio dědí, ne roury — ty sandbox blokuje).

Offline test (bez zápisu mimo workspace): `python _analyza\\test-skill-patch.py`
"""

import importlib.util
import os
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

TADY = pathlib.Path(__file__).resolve().parent

_spec = importlib.util.spec_from_file_location(
    "priprav_skill_patch", TADY / "priprav-skill-patch.py"
)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)

# Markery vložených podsekcí — poznají se podle nich soubory, kde záplata
# UŽ JE, ale liší se od ověřené záplaty (pak se nesmí aplikovat podruhé).
MARKERY = {
    "game-developer": [
        "### Past: dvě jména téhož pole",
        "### Past: statická metrika",
    ],
    "dsh-prostredi": [
        "### Různé čítače nesou stejné jméno",
        "### Dvě pasti při ověřování cizích čísel",
    ],
}


def main() -> int:
    koren = pathlib.Path(os.environ.get("SKILLS_ROOT", str(mod.SKILLS)))
    je_ostry = "SKILLS_ROOT" not in os.environ
    zaloha = TADY / "zaloha"

    print(f"Cíl: {koren}  ({'ostrý provoz' if je_ostry else 'TEST — jen kopie'})")
    print()

    # Fáze 1 — spočítat a ověřit VŠECHNO, teprve pak zapisovat.
    # Cílem je OVĚŘENÁ záplata z `_analyza\patch\`, ne přepočet naslepo:
    # druhé spuštění by jinak vložilo tytéž sekce podruhé (anchor „## 4." se
    # vložením nemaže, takže by pořád „seděl").
    plan = []
    for jmeno, zmeny in mod.ZAPLATY.items():
        cil = koren / jmeno / "SKILL.md"
        if not cil.exists():
            print(f"  CHYBA {jmeno}: {cil} neexistuje")
            return 1
        soucasne = cil.read_bytes()
        golden = (mod.OUT / jmeno / "SKILL.md").read_bytes()

        if soucasne == golden:
            radu = len(golden.decode("utf-8").splitlines())
            print(f"  {jmeno:16} už aplikováno   řádků {radu}")
            plan.append((jmeno, cil, soucasne, golden))
            continue

        if any(m.encode("utf-8") in soucasne for m in MARKERY[jmeno]):
            print(
                f"  CHYBA {jmeno}: v souboru je UŽ ČÁST záplaty, ale liší se od "
                f"ověřené záplaty — neaplikuji, vyřeš ručně"
            )
            return 1

        try:
            spocitane = mod.zaplat(soucasne, zmeny)
            mod.zkontroluj(jmeno, soucasne, spocitane)
        except SystemExit as e:
            print(f"  CHYBA {jmeno}: {e}")
            return 1

        if spocitane != golden:
            print(
                f"  CHYBA {jmeno}: soubor se liší od originálu, ze kterého záplata "
                f"vznikla — neaplikuji (nejdřív přepočti _analyza\\priprav-skill-patch.py)"
            )
            return 1

        radu_p = len(soucasne.decode("utf-8").splitlines())
        radu_n = len(golden.decode("utf-8").splitlines())
        print(f"  {jmeno:16} k aplikaci      řádků {radu_p} → {radu_n} (+{radu_n - radu_p})")
        plan.append((jmeno, cil, soucasne, golden))

    zmen = [p for p in plan if p[2] != p[3]]
    if not zmen:
        print("\nNic k zápisu — všechny záplaty jsou aplikované.")
    else:
        print()
        for jmeno, cil, soucasne, nove in zmen:
            if je_ostry:
                zaloha.mkdir(parents=True, exist_ok=True)
                (zaloha / f"{jmeno}-SKILL.md.pred").write_bytes(soucasne)
            cil.write_bytes(nove)
            # Ověř, že zápis opravdu proběhl (ne „nástroj tvrdí, že zapsal").
            zpet = cil.read_bytes()
            if zpet != nove:
                print(f"  CHYBA {jmeno}: zápis neproběhl — na disku je jiný obsah!")
                return 1
            print(f"  ZAPSÁNO {jmeno:16} {len(nove)} bajtů  → {cil}")
        if je_ostry:
            print(f"  záloha: {zaloha}")

    if je_ostry:
        print("\n=== python orchestra\\tools\\over-skilly.py ===")
        return subprocess.call(
            [sys.executable, str(TADY.parent / "orchestra" / "tools" / "over-skilly.py")]
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())

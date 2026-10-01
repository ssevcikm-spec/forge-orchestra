"""Kontrola diakritiky v dokumentech, které tahle session měnila.

PowerShell soubory s diakritikou jednou poškodil (dvojité kódování), takže se
kontrola dělá Pythonem – viz HANDOFF.md, „Pozor při editaci souborů
s diakritikou".
"""

import pathlib
import sys

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
SOUBORY = [
    WS / "AGENTS.md",
    WS / "ARCHITEKTURA-ANALYZA-ZADANI.md",
    WS / "HANDOFF.md",
    WS / "SKILLY-AKTUALIZACE.md",
    WS / "MOZNOSTI-AGENTA.md",
    WS / "FORGE-ORCHESTRA-MOZNOSTI.md",
    WS / "PLAN-VISION-ORCHESTRA.md",
    # 1. 10. 2026: analýza architektury a její podklady. Byly napsané bez
    # kontroly diakritiky — a to je přesně ta vada, kterou tenhle nástroj
    # hledá. Nový dokument se musí přidat SEM, jinak ho kontrola nevidí
    # (stejná past jako u netrackovaného souboru v gitu).
    WS / "ANALYZA-ARCHITEKTURY-ORCHESTRA.md",
    WS / "ANALYZA-PODKLADY-CONDUCTOR-A-NASTROJE.md",
    WS / "PLAN-ROZVOJ-ORCHESTRA.md",
    # 1. 10. 2026 (večer): hloubková analýza a její druhé kolo měření.
    # NAMĚŘENO PŘI PŘIDÁVÁNÍ: tenhle nástroj má PEVNÝ seznam, takže nový
    # dokument projde zeleně, i když ho kontrola nikdy neotevřela. Je to táž
    # vada jako `kontrola-driftu.mjs` s ručním seznamem 12 souborů — a je
    # zapsaná jako S27 v ANALYZA-HLOUBKOVA-ORCHESTRA.md §4.
    WS / "ANALYZA-HLOUBKOVA-ORCHESTRA.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI.md",
    WS / "_analyza" / "HLOUBKOVA-MERENI-2.md",
    WS / "ANALYZA-HLOUBKOVA-2-ZADANI.md",
    WS / "OTEVRENA-TEMATA.md",
    WS / "orchestra" / "repo" / ".forge" / "check-schema.py",
    WS / "orchestra" / "repo" / ".forge" / "vision-profile.json",
    WS / "orchestra" / "repo" / ".forge" / "baseline.py",
    WS / "orchestra" / "tools" / "test-check-schema.py",
    WS / "games" / "uo-shadows" / ".github" / "workflows" / "ci.yml",
    WS / "README.md",
    WS / "orchestra" / "README.md",
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\dsh-prostredi\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\vision\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-assets\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\game-developer\SKILL.md"),
    pathlib.Path(r"C:\Users\Ssevc\.dsh\skills\orchestra\SKILL.md"),
]

# Typické znaky dvojitého kódování UTF-8 přečtené jako Windows-1250
ROZBITE = ["Ã", "Ä", "Å"]

chyb = 0
for f in SOUBORY:
    if not f.exists():
        print(f"  CHYBA {f.name}: neexistuje")
        chyb += 1
        continue
    s = f.read_text(encoding="utf-8")
    nalezene = [z for z in ROZBITE if z in s]
    stav = "OK  " if not nalezene else "CHYBA"
    if nalezene:
        chyb += 1
    # Popisek musí nést i rodiče: jinak se v seznamu tři různé soubory jmenují
    # „SKILL.md" a není poznat, který je který.
    popis = f"{f.parent.name}\\{f.name}"
    print(f"  {stav} {popis:34} {len(s):7} znaků  "
          f"rozbito: {', '.join(nalezene) if nalezene else 'ne'}")

print()
print("VŠE OK" if chyb == 0 else f"NALEZENY CHYBY ({chyb})")
sys.exit(0 if chyb == 0 else 1)

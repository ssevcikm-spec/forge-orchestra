"""Doplní do šablony orchestra vstup `attempt` (spouští se jednou, je to nástroj).

PowerShell cestu jsem zkoušel a přepisoval diakritiku (Get-Content -Raw +
Set-Content mění kódování), takže se textové zásahy do souborů s českými znaky
dělají Pythonem s výslovným encoding='utf-8'.
"""

import pathlib
import sys
import yaml

SABLONA = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.github\workflows\agent.yml")

STARY_VSTUP = """      grain:
        description: 'ID granule v roadmapě (např. core.skills) – podle něj se bere owns, tedy soubory k editaci'
        required: false
        default: ''"""

NOVY_VSTUP = STARY_VSTUP + """
      attempt:
        description: 'Číslo pokusu (1 = první). Podle něj se posouvá pořadí modelů, aby opakovaný pokus nezkoušel stejný model.'
        required: false
        default: '1'"""


def main() -> int:
    text = SABLONA.read_text(encoding="utf-8")

    # Už tam je? (idempotence)
    data = yaml.safe_load(text)
    vstupy = data[True]["workflow_dispatch"]["inputs"] if True in data else \
        data["on"]["workflow_dispatch"]["inputs"]
    if "attempt" in vstupy:
        print("Vstup 'attempt' už v šabloně je – nic se nemění.")
        return 0

    if STARY_VSTUP not in text:
        print("CHYBA: hledaný blok vstupu 'grain' nenalezen.")
        return 1

    text = text.replace(STARY_VSTUP, NOVY_VSTUP, 1)
    SABLONA.write_text(text, encoding="utf-8")

    # Ověření, že YAML zůstal platný a vstup je opravdu vidět.
    data = yaml.safe_load(SABLONA.read_text(encoding="utf-8"))
    vstupy = data[True]["workflow_dispatch"]["inputs"] if True in data else \
        data["on"]["workflow_dispatch"]["inputs"]
    print("Vstupy v šabloně:", ", ".join(vstupy.keys()))
    print("'attempt' přidán:", "attempt" in vstupy)
    return 0


if __name__ == "__main__":
    sys.exit(main())

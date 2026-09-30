"""Ověří, že dokumentační změny sedí: frontmatter, diakritika, nové sekce.

Kontroluje se i to, že v souborech nezůstalo dvojité kódování češtiny
(„zaÄÃ­najÃ­") – přesně to jednou vzniklo, když se do souboru psalo
PowerShellem místo Pythonu.
"""

import pathlib
import re
import sys

SKILLS = pathlib.Path(r"C:\Users\Ssevc\.dsh\skills")
README = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek\orchestra\README.md")

# Typické znaky dvojitého kódování (UTF-8 přečtené jako Windows-1250)
ROZBITE = ["Ã", "Ä", "Å", "Å¡", "Ä›", "Ã¡", "Ã­", "Ã©"]

kontrol = 0
chyb = 0


def zkontroluj(cesta: pathlib.Path, pozadovane: list[str], popis: str) -> None:
    global kontrol, chyb
    if not cesta.exists():
        print(f"  CHYBA {popis}: soubor neexistuje ({cesta})")
        chyb += 1
        return
    text = cesta.read_text(encoding="utf-8")

    # 1) dvojité kódování
    nalezeno = [z for z in ROZBITE if z in text]
    if nalezeno:
        print(f"  CHYBA {popis}: rozbitá diakritika ({', '.join(nalezeno[:3])})")
        chyb += 1
    else:
        print(f"  OK   {popis}: diakritika v pořádku")
    kontrol += 1

    # 2) požadované texty
    chybejici = [p for p in pozadovane if p not in text]
    if chybejici:
        for p in chybejici:
            print(f"  CHYBA {popis}: chybí text {p[:60]!r}")
        chyb += 1
    else:
        print(f"  OK   {popis}: všech {len(pozadovane)} hledaných textů na místě")
    kontrol += 1

    # 3) YAML frontmatter u skillů
    if "skills" in str(cesta):
        if text.startswith("---"):
            konec = text.find("\n---", 3)
            if konec > 0:
                fm = text[3:konec]
                ma_name = bool(re.search(r"^name:\s*\S", fm, re.M))
                ma_desc = bool(re.search(r"^description:", fm, re.M))
                print(f"  {'OK  ' if ma_name and ma_desc else 'CHYBA'} {popis}: "
                      f"frontmatter (name={ma_name}, description={ma_desc})")
                if not (ma_name and ma_desc):
                    chyb += 1
            else:
                print(f"  CHYBA {popis}: frontmatter nekončí")
                chyb += 1
        else:
            print(f"  CHYBA {popis}: nezačíná frontmatterem")
            chyb += 1
        kontrol += 1


print("=== orchestra/README.md ===")
zkontroluj(README, [
    "Jak agent dostane soubory",
    "Opakované pokusy: každý zkusí jiný model",
    "Nástroje pro analýzu",
    "files-to-edit.mjs",
    "ESCALATE_AFTER",
    "--map-tokens 0",
    "watchdog: 0 ohlášeno (prah 8)",
], "README")

print("=== orchestra/SKILL.md ===")
zkontroluj(SKILLS / "orchestra" / "SKILL.md", [
    "Analýza a diagnostika",
    "(**3 h**)",
    "Cooldown se vynucuje ČASEM",
    "MAX_ATTEMPTS` je mrtvý kód",
    "soubor v EDITOVATELNÉM chatu",
], "orchestra skill")

print("=== game-developer/SKILL.md ===")
zkontroluj(SKILLS / "game-developer" / "SKILL.md", [
    "tiše zelený",
    "extends Node",
    "_instantiate",
    "stejný počet",
], "game-developer skill")

print()
print(f"Kontrol: {kontrol}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)

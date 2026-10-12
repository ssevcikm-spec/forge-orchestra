# p40-m-prejmenuj-identifikatory.py — OPRAVA VADY, KTEROU NAŠLA BRÁNA PŘI P40:
# `_analyza/p40-h189-test.py` měl ČESKÝ NÁZEV FUNKCE (`ukaž`) — a pravidlo
# projektu je, že IDENTIFIKÁTORY jsou ASCII anglicky (`hl-rizika-jazyka.py` to
# naměřilo: „z toho IDENTIFIKÁTORY: 1"). Test vznikl delegovanou prací a pravidlo
# jazyka v zadání neměl — to je nález o ZADÁNÍ delegace, ne o testu.
#
# ⚠ MĚŘENÁ VADA JE **DIAKRITIKA V IDENTIFIKÁTORU** (`ukaž`), ne „čeština“:
# brána `hl-rizika-jazyka.py` hlásí „z toho IDENTIFIKÁTORY: 1“ právě na `ukaž`
# a jména jako `zkontroluj`/`spust`/`fixtura` (ASCII, bez diakritiky) NECHAVÁ být —
# používají je i starší nástroje projektu (`zk`, `spust`). Přejmenovává se proto
# JEN to, co brána naměřila jako vadu; zbytek by byl churn v testu, který se má
# dát spustit.
#
# Použití: python _analyza/p40-m-prejmenuj-identifikatory.py
# Exit 0 = přejmenováno a ověřeno; 1 = nic k přejmenování / nesouhlasí.

import pathlib
import re
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")
WS = pathlib.Path(__file__).resolve().parents[1]
SOUBORY = [
    WS / "_analyza" / "p40-h189-test.py",
    WS / "_analyza" / "p40-h195-test.py",
]
PREJMENA = [("ukaž", "show")]

for cesta in SOUBORY:
    if not cesta.is_file():
        print(f"CHYBA: {cesta.name} neexistuje")
        sys.exit(1)
    puvodni = cesta.read_bytes()
    if puvodni[:3] == b"\xef\xbb\xbf":
        print(f"CHYBA: {cesta.name} má BOM — opravuje se jen bez BOM")
        sys.exit(1)
    text = puvodni.decode("utf-8")
    zmeny = []
    for stary, novy in PREJMENA:
        # přejmenovává se JEN jako identifikátor (ne uvnitř řetězců)
        vzor = re.compile(r"(?<![\w\"'])" + re.escape(stary) + r"(?![\w])")
        kolik = len(vzor.findall(text))
        if kolik:
            text = vzor.sub(novy, text)
            zmeny.append(f"{stary}→{novy} ({kolik}×)")
    if not zmeny:
        print(f"  {cesta.name}: nic k přejmenování")
        continue
    cesta.write_bytes(text.encode("utf-8"))
    # kontrola: žádné non-ASCII v DEFINICÍCH a žádný zbytek starých jmen
    zbylek = [s for s, _ in PREJMENA if re.search(r"(?<![\w\"'])" + re.escape(s) + r"(?![\w])", text)]
    definice = re.findall(r"^def ([^\s(]+)", text, re.M)
    nonascii = [d for d in definice if any(ord(c) > 127 for c in d)]
    print(f"  {cesta.name}: {', '.join(zmeny)}")
    print(f"    definice funkcí: {definice}")
    print(f"    non-ASCII v definicích: {nonascii or 'žádné'}"
          f" · zbytek starých jmen: {zbylek or 'žádný'}")
    if zbylek or nonascii:
        print("    CHYBA: nesouhlasí — nic dalšího se needituje")
        sys.exit(1)

print("\nHOTOVO: identifikátory v testech jsou ASCII. (Nutno přegenerovat inventář.)")
sys.exit(0)

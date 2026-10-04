r"""P7 — mutační test POJISTKY proti zápisu v sekci L `validate-all.mjs`.

CO SE DOKAZUJE (bod 7 zadání, druhá polovina): že validátor nástroj, jehož
zdroj obsahuje zápis, SKUTEČNĚ odmítne spustit — a řekne to.

Mutace je záměrně NEŠKODNÁ: do komentáře se vloží slovo `write_text`.
Chování nástroje se nemění, mění se jen to, co vidí pojistka. Kdyby pojistka
fungovala jen na skutečný zápis, tenhle test by ji nechytil — a to je taky
výsledek (uvede se v protokolu).

Použití:  python _analyza\p7-mutace-pojistky.py --vrat
          node orchestra\tools\validate-all.mjs   (ručně, hledá se řádek pojistky)
          python _analyza\p7-mutace-pojistky.py --obnov
          python _analyza\p7-mutace-pojistky.py --stav
"""
import hashlib
import pathlib
import shutil
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
CIL = WS / "_analyza" / "b5-over-tvrzeni.py"
ZALOHA = WS / "_analyza" / "_p7-zaloha-b5.py"
RADEK = "\n# write_text (MUTACE P7 — jen v komentáři, chování se nemění)\n"


def sha(p: pathlib.Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()[:16]


def main() -> int:
    akce = sys.argv[1] if len(sys.argv) > 1 else "--stav"
    if not CIL.is_file():
        print(f"CHYBA: {CIL} neexistuje")
        return 2

    if akce == "--vrat":
        puvodni = CIL.read_bytes()
        if ZALOHA.is_file() and b"MUTACE P7" in CIL.read_bytes():
            print("CHYBA: mutace uz je zapsana, napred --obnov")
            return 2
        ZALOHA.write_bytes(puvodni)
        novy = puvodni + RADEK.encode("utf-8")
        CIL.write_bytes(novy)
        # DUKAZ, ZE MUTACE PROBĚHLA (past z overovani §7.9/§7.12)
        zpet = CIL.read_bytes()
        assert zpet != puvodni, "MUTACE NEPROBĚHLA (obsah stejný)"
        assert b"MUTACE P7" in zpet, "MUTACE NEPROBĚHLA (znacka v souboru není)"
        print(f"  mutace zapsána: {sha(CIL)} (původní {hashlib.sha256(puvodni).hexdigest()[:16]})")
        print(f"  `write_text` ve zdroji: {zpet.count(b'write_text')}x")
        return 0

    if akce == "--obnov":
        if not ZALOHA.is_file():
            print("CHYBA: záloha neexistuje")
            return 2
        puvodni = ZALOHA.read_bytes()
        CIL.write_bytes(puvodni)
        zpet = CIL.read_bytes()
        assert zpet == puvodni, "OBNOVA NEPROBĚHLA"
        print(f"  obnoveno: {sha(CIL)}  `write_text` ve zdroji: {zpet.count(b'write_text')}x")
        ZALOHA.unlink()
        return 0

    print(f"  stav: {sha(CIL)}  `write_text` ve zdroji: "
          f"{CIL.read_bytes().count(b'write_text')}x  záloha: {ZALOHA.is_file()}")
    return 0


if __name__ == "__main__":
    sys.exit(main())

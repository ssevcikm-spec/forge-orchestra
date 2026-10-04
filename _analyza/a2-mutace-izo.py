"""MUTAČNÍ TEST kontroly izometrie hráče (Úkol 2 zadání, bod 3).

PROČ TO EXISTUJE: `AGENTS.md` — „Napsal jsi test? Vrať do kódu vadu a podívej
se, že spadne. Mutační test je jediný důkaz, že test měří." Kontrola, která
projde na zdravém kódu, nic neznamená, dokud se neukáže, že umí spadnout.

CO SE MUTUJE: vypuštění izometrického přepočtu v `player.move()` — tedy přesně
ta vada, kterou kontrola hlídá (vrácení mrtvé větve `else`: hráč by chodil
1:1 podle obrazovky, dlaždice jsou 2:1).

PASTI, KTERÉ JSOU TU OŠETŘENÉ (každá je naměřená, viz skill `overovani`):
  * §7.14 — mutace musí obrátit MĚŘENOU PODMÍNKU, ne jen změnit soubor:
    proto se před zápisem assertuje, že cíl v souboru je právě 1×.
  * §7.9/§7.12 — mutace, která se tiše neprovede, vypadá jako úspěch:
    proto se po zápisu soubor PŘEČTE Z DISKU a porovná.
  * §10.6 — mutační skript, který spadne mezi zápisem a návratem, nechá
    soubor zmutovaný: proto `try/finally`, které soubor vždy vrátí.
  * §2.1 — záloha KOPIÍ, ne `git checkout` (soubor má necommitnuté změny).

Spuštění:
  $env:PYTHONIOENCODING='utf-8'
  python _analyza\a2-mutace-izo.py
"""
import re
import subprocess
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

KOREN = Path(__file__).resolve().parent.parent
HRA = KOREN / "games" / "uo-shadows"
PLAYER = HRA / "scripts" / "player.gd"
GODOT = KOREN / "orchestra" / "tools" / "godot" / "Godot_v4.7.2-stable_win64_console.exe"
APPDATA = KOREN / "_analyza" / "a-godot-user"

# MUTACE: izometrické osy → směr podle obrazovky (mrtvá větev `else`).
# Nový text NESMÍ obsahovat ten starý (past §7.12 a omyl 106 v HANDOFF.md:
# `filesInOriginMainXX` obsahuje `filesInOriginMain`).
STARY = """	var iso := Vector2((d.x - d.y) * 0.5, (d.x + d.y) * 0.25)
	if iso.length() > 0.0:
		iso = iso.normalized()
	velocity = iso * SPEED"""
NOVY = """	var iso := d
	velocity = iso * SPEED"""


def spust_testy() -> tuple[int, str]:
    """Spustí testy hry a vrátí (exit kód, výstup)."""
    v = subprocess.run(
        [str(GODOT), "--headless", "--path", str(HRA),
         "--script", "res://tests/run_tests.gd"],
        capture_output=True, shell=False,
        env={"APPDATA": str(APPDATA), "PATH": "", "SYSTEMROOT": "C:\\Windows"},
    )
    vystup = (v.stdout or b"").decode("utf-8", "replace") + \
             (v.stderr or b"").decode("utf-8", "replace")
    return v.returncode, vystup


def souhrn(vystup: str) -> str:
    m = re.search(r"\[test\] (\d+) kontrol, (\d+) selhání", vystup)
    return "%s kontrol, %s selhání" % (m.group(1), m.group(2)) if m else "SOUHRN NENALEZEN"


def main() -> int:
    if not PLAYER.exists():
        print("CHYBA: %s neexistuje" % PLAYER)
        return 2

    orig: bytes = PLAYER.read_bytes()
    chyb = 0

    print("=== 1) ZDRAVY KOD: testy musi projit ===")
    kod, vystup = spust_testy()
    print("    exit=%d | %s" % (kod, souhrn(vystup)))
    if kod != 0:
        print("    CHYBA: testy neprojdou ani na zdravem kodu — mutace by nic nedokazala")
        return 2

    text = orig.decode("utf-8")
    pocet = text.count(STARY)
    print("\n=== 2) MUTACE: vypusteni izo prepoctu v move() ===")
    print("    kotva v souboru: %dx" % pocet)
    if pocet != 1:
        print("    CHYBA: kotva neni jednoznacna (%dx) — mutace by trefila jine misto" % pocet)
        return 2

    try:
        zmut = text.replace(STARY, NOVY)
        assert zmut != text, "MUTACE NEZMENILA TEXT"
        # MĚŘENÁ PODMÍNKA musí přestat platit (§7.14).
        assert STARY not in zmut, "stara podminka v souboru ZUSTALA"
        assert NOVY in zmut, "nova podminka v souboru NENI"

        PLAYER.write_bytes(zmut.encode("utf-8"))
        # Ověření, že se mutace opravdu propsala NA DISK (§7.9).
        na_disku = PLAYER.read_bytes()
        assert na_disku != orig, "MUTACE SE NEZAPSALA (soubor na disku je puvodni)"
        assert STARY.encode("utf-8") not in na_disku, "na disku je porad stary text"
        print("    mutace zapsana a overena na disku")

        kod2, vystup2 = spust_testy()
        print("    exit=%d | %s" % (kod2, souhrn(vystup2)))
        for radek in vystup2.splitlines():
            if "FAIL" in radek and ("izo" in radek or "dlaždic" in radek or "krok" in radek):
                print("    %s" % radek.strip())
        if kod2 == 0:
            print("    CHYBA: testy prosly I S VADOU -> kontrola je slepa")
            chyb += 1
        else:
            print("    OK: s vracenou vadou testy SPADLY")
    finally:
        PLAYER.write_bytes(orig)
        assert PLAYER.read_bytes() == orig, "SOUBOR NEVRACEN DO PUVODNI PODOBY!"
        print("\n=== 3) NAVRAT: soubor vracen (sha shoda) ===")

    kod3, vystup3 = spust_testy()
    print("    exit=%d | %s" % (kod3, souhrn(vystup3)))
    if kod3 != 0:
        print("    CHYBA: po navratu testy neprojdou")
        chyb += 1

    print("\nVYSLEDEK: %s" % ("MUTACE CHYCENA — kontrola meri" if chyb == 0
                              else "CHYBA — kontrola nemeri (%d)" % chyb))
    return 0 if chyb == 0 else 1


if __name__ == "__main__":
    sys.exit(main())

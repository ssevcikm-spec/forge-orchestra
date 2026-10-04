r"""Mutační test `_analyza\zadani-kontrola.py`.

CO SE DOKAZUJE: že kontrola zadání UMI SPADNOUT, když je zadání zastaralé —
a že nespadne na zdravém zadání. Bez toho by „zadání je použitelné" nic
neznamenalo.

PROČ VLASTNÍ SOUBOR A NE `python -c`: v zadání jsou zpětné apostrofy (`` ` ``)
a PowerShell je uvnitř `-c` bere jako escape/řídicí znak — text se rozbije
a mutace se **tiše neprovede**. Přesně to se stalo při psaní tohohle testu:
první verze hlásila `exit 0` na NEMUTOVANÉM souboru a vypadalo to jako slepá
kontrola. Je to past z `overovani` §7.9 — **mutace, která se neprovede, tvrdí
totéž co mutace, která projde.**

Proto se tady u KAŽDÉ mutace ověřuje, že se text skutečně změnil (assert),
a na konci se soubor vrací ze zálohy.

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\zadani-mutace.py
"""
import pathlib
import shutil
import subprocess
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(r"C:\Users\Ssevc\Local-Deepseek")
ZADANI = WS / "NEXT-SESSION-INSTRUKCE.md"
KONTROLA = WS / "_analyza" / "zadani-kontrola.py"
ZALOHA = WS / "_analyza" / "_zadani-mutace-zaloha.md"


def spust_kontrolu() -> tuple:
    r = subprocess.run([sys.executable, str(KONTROLA)],
                       capture_output=True, text=True, encoding="utf-8")
    zajimave = [l.strip() for l in ((r.stdout or "") + (r.stderr or "")).splitlines()
                if "VÝSLEDEK" in l or "přibylo" in l or "⚠" in l or "CHYBÍ" in l]
    return r.returncode, zajimave


def mutuj(popis: str, najdi: str, nahrad: str) -> bool:
    """Provede doslovnou náhradu a OVĚŘÍ, že proběhla."""
    puvodni = ZADANI.read_text(encoding="utf-8")
    if najdi not in puvodni:
        print(f"  CHYBA: vzor pro mutaci {popis!r} v zadání NENÍ — test by nic neměřil")
        return False
    novy = puvodni.replace(najdi, nahrad, 1)
    if novy == puvodni:
        print(f"  CHYBA: mutace {popis!r} text nezměnila")
        return False
    ZADANI.write_text(novy, encoding="utf-8")
    # DRUHÉ ověření: přečti z disku, ne z paměti
    if ZADANI.read_text(encoding="utf-8") == puvodni:
        print(f"  CHYBA: mutace {popis!r} se na disk nezapsala")
        return False
    print(f"  mutace {popis!r}: zapsána a ověřena")
    return True


print("=" * 78)
print("MUTAČNÍ TEST KONTROLY ZADÁNÍ (`zadani-kontrola.py`)")
print("=" * 78)

if not ZADANI.is_file() or not KONTROLA.is_file():
    print("CHYBA: chybí zadání nebo kontrola")
    sys.exit(2)

ZALOHA.write_bytes(ZADANI.read_bytes())
pocet_ok = 0
pocet_celkem = 0
try:
    # ── 0) KONTROLNÍ STAV: zdravé zadání musí PROJÍT ────────────────────────
    print("\n--- 0) zdravé zadání (musí projít, exit 0) ---")
    kod, radky = spust_kontrolu()
    for l in radky:
        print("   ", l[:100])
    if kod == 0:
        print("    OK: exit=0")
        pocet_ok += 1
    else:
        print(f"    CHYBA: exit={kod} na zdravém zadání — sprav nejdřív kontrolu")
    pocet_celkem += 1

    # ── 1) MUTACE: tvrzený commit o dva zpět ───────────────────────────────
    print("\n--- 1) mutace: tvrzený commit orchestra o 2 commity zpět ---")
    # Vzor se skládá z částí, aby v tomhle souboru nebyly zpětné apostrofy
    # v řetězci, který by rozbil shell.
    AP = chr(96)  # `
    if mutuj("tvrzený commit",
             f"{AP}orchestra{AP} = {AP}5a8f91a{AP}",
             f"{AP}orchestra{AP} = {AP}be41964{AP}"):
        kod, radky = spust_kontrolu()
        for l in radky:
            print("   ", l[:100])
        pocet_celkem += 1
        if kod == 1:
            print("    OK: exit=1 (kontrola vadu chytila)")
            pocet_ok += 1
        else:
            print(f"    CHYBA: exit={kod} — kontrola je SLEPÁ na zastaralý commit")
        ZADANI.write_bytes(ZALOHA.read_bytes())
        print("    (zadání vráceno ze zálohy)")

    # ── 2) MUTACE: chybějící hlavička ──────────────────────────────────────
    print("\n--- 2) mutace: smazaný řádek se stavem repů ---")
    if mutuj("hlavička", "**Stav obou repů při psaní:**", "**Poznámka:**"):
        kod, radky = spust_kontrolu()
        for l in radky:
            print("   ", l[:100])
        pocet_celkem += 1
        if kod == 1:
            print("    OK: exit=1 (chybějící hlavička je nález)")
            pocet_ok += 1
        else:
            print(f"    CHYBA: exit={kod} — chybějící hlavička prošla")
        ZADANI.write_bytes(ZALOHA.read_bytes())
        print("    (zadání vráceno ze zálohy)")

    # ── 3) KONTROLA, ŽE SE SOUBOR OPRAVDU VRÁTIL ───────────────────────────
    print("\n--- 3) zadání je zpět v původním stavu? ---")
    pocet_celkem += 1
    if ZADANI.read_bytes() == ZALOHA.read_bytes():
        print("    OK: bajt po bitu shodné se zálohou")
        pocet_ok += 1
    else:
        print("    CHYBA: zadání se nevrátilo!")
        shutil.copyfile(ZALOHA, ZADANI)
        print("    (vráceno dodatečně)")
finally:
    ZADANI.write_bytes(ZALOHA.read_bytes())
    if ZALOHA.is_file():
        ZALOHA.unlink()

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {pocet_ok} z {pocet_celkem} kontrol prošlo.")
sys.exit(0 if pocet_ok == pocet_celkem else 1)

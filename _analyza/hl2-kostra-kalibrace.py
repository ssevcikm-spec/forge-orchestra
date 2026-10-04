# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Kalibrace: projde brana, kdyz kostra dostane jen 2 chybejici radky?

Predchozi beh (`hl2-kostra-test.py`) spadl na bodech 2 a 7. To muze znamenat
dve veci:
  (a) brana obsah MĚŘÍ, nebo
  (b) kostra jen nemela ty spravne retezce a brana je test na pritomnost.

Rozhodne to tenhle test: do kostry se pridaji presne dva radky --
hlavicka tabulky s "cím je dnes ukotveno" a radky s markery
Cena/Riziko/Co NEDĚLÁ/Podmínka selhání. Pokud brana i tak projde (exit 0),
je (b) pravda a "9/9" je otazka pritomnosti retezcu, ne obsahu.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-kostra-kalibrace.py
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
DOK = WS / "ANALYZA-HLOUBKOVA-ORCHESTRA-2.md"
KONTROLA = WS / "_analyza" / "hl2-kontrola.py"

SEKCE = [
    "Verdikt v pěti větách", "Co je orchestra", "Inventura vlastností",
    "Katalog tříd selhání", "Co je dobré", "Architektura v devíti optikách",
    "Návrh kontraktů", "Dvě varianty", "Co NEDĚLAT", "Co analýza NEZJISTILA",
    "Tabulka", "Co by tuhle analýzu vyvrátilo",
]

original_bajty = DOK.read_bytes()
orig_text = original_bajty.decode("utf-8")
radky = orig_text.splitlines()


def je_nadpis(radek):
    return bool(re.match(r"^#{1,3} ", radek))


def je_marker(radek):
    if any(s in radek for s in SEKCE):
        return True
    if re.match(r"^### S\d+ ", radek):
        return True
    if re.match(r"^\| \*\*\d+\*\* \|", radek):
        return True
    return "VYVRÁCENO" in radek


zachovane = [r if (je_nadpis(r) or je_marker(r)) else "" for r in radky]

# DOPLNENI: presne ty dva druhy radku, ktere v kostre chybely
DOPLNIT = [
    "| # | tvrzení systému o sobě | kde je zapsané | **čím je dnes ukotveno** | čím by ukotveno být mohlo |",
    "| **Cena** | X |",
    "| **Riziko** | X |",
    "| **Co NEDĚLÁ** | X |",
    "| **Podmínka selhání** | X |",
    "| **Cena** | X |",
    "| **Riziko** | X |",
    "| **Co NEDĚLÁ** | X |",
    "| **Podmínka selhání** | X |",
]
kostra = "\n".join(zachovane + DOPLNIT) + "\n"

assert len(kostra) < len(orig_text) * 0.5, "kostra neni kostra"
for m in ["čím je dnes ukotveno", "**Cena**", "**Riziko**", "**Co NEDĚLÁ**", "**Podmínka selhání**"]:
    assert m in kostra, m

print("=== Kalibrace: kostra + 9 radku s markery ===\n")
print(f"  original : {len(orig_text):>7} znaku")
print(f"  kostra   : {len(kostra):>7} znaku  ({100*len(kostra)/len(orig_text):.1f} %)")
print("  Obsah: zadny. Jen nadpisy, markery a 9 radku tabulek.\n")

try:
    DOK.write_bytes(kostra.encode("utf-8"))
    r = subprocess.run([sys.executable, str(KONTROLA)],
                       capture_output=True, text=True, encoding="utf-8")
    print("--- vystup brany ---")
    print(r.stdout.rstrip())
    print("--------------------\n")
    kod = r.returncode
finally:
    DOK.write_bytes(original_bajty)
    assert DOK.read_bytes() == original_bajty, "original se nepodarilo vratit!"
    print("  original vracen z bajtu a overen shodou bajtu")

print()
if kod == 0:
    print("VYSLEDEK: brana PROSLA nad kostrou s 9 radky tabulek -> '9/9' je otazka")
    print("          PRITOMNOSTI RETEZCU, ne obsahu dokumentu.")
    sys.exit(1)
print(f"VYSLEDEK: brana SPADLA i po doplneni radku (exit={kod}).")
sys.exit(0)

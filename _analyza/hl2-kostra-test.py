# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Nezavisla mutace brany hl2-kontrola.py: projde brana nad DOKUMENTEM BEZ OBSAHU?

Proc to existuje: `hl2-mutace-kontrola.py` testuje 6 mutaci, ktere mazeji CELÉ
markery (nazvy oddilu, klicova slova). Netestuje ale to, co je u teto brany
nejpravdepodobnejsi vada: ze vsechny body "Hotovo znamena" se ptaji na
PRITOMNOST RETEZCE, ne na obsah. Tj. dokument, kde jsou nadpisy a markery
a jinak nic, by mohl projit.

Postup: z dokumentu se udela "kostra" -- zustane kazdy radek obsahujici
nektorou z 12 pozadovanych sekci, nadpisy `### Sxx`, markery variant
a radky tabulky odpovedi. Vsechno ostatni (telo oddilu) se nahradi prazdnym
radkem. Kostra se zapise do docasneho souboru a brana se spusti nad ni.

Brana ma KLICOVY soubor natvrdo v konstante DOK, takze se kostra zapise na
jeji misto -- a PUVODNI DOKUMENT SE PREDTIM ZALOHUJE a po testu se vraci
z bajtu. Kdyz by cokoli selhalo, zustane zaloha.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\hl2-kostra-test.py
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

# presne tyz seznam, ktery pozaduje brana (bod 1)
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
    """Radky, ktere si brana explicitne cte (aby kostra nebyla past na neco jineho)."""
    if any(s in radek for s in SEKCE):
        return True
    if re.match(r"^### S\d+ ", radek):
        return True
    if re.match(r"^\| \*\*\d+\*\* \|", radek):
        return True
    return "VYVRÁCENO" in radek


zachovane, nahradene = [], 0
for radek in radky:
    if je_nadpis(radek) or je_marker(radek):
        zachovane.append(radek)
    else:
        zachovane.append("")
        nahradene += 1
kostra = "\n".join(zachovane) + "\n"

# kontrola, ze mutace OPRAVDU probehla (past ze skillu overovani §7.9)
puvodni_znaku = len(orig_text)
kostra_znaku = len(kostra)
assert kostra_znaku < puvodni_znaku * 0.5, (
    f"mutace neprovedla to, co mela: kostra ma {kostra_znaku} znaku "
    f"z puvodnich {puvodni_znaku}"
)
for s in SEKCE:
    assert s in kostra, f"kostra ztratila marker, brana by spadla z jineho duvodu: {s}"

print("=== Nezavisla mutace: dokument O BEZ OBSAHU, jen nadpisy a markery ===\n")
print(f"  puvodni dokument : {puvodni_znaku:>7} znaku")
print(f"  kostra           : {kostra_znaku:>7} znaku  ({100*kostra_znaku/puvodni_znaku:.1f} %)")
print(f"  nahrazeno radku  : {nahradene:>7} z {len(radky)}")
print("  (mutace overena: kostra < 50 % originalu a vsechny markery zustaly)\n")

try:
    DOK.write_bytes(kostra.encode("utf-8"))
    r = subprocess.run([sys.executable, str(KONTROLA)],
                       capture_output=True, text=True, encoding="utf-8")
    print("--- vystup brany nad kostrou ---")
    print(r.stdout.rstrip())
    print("--------------------------------\n")
    kod = r.returncode
finally:
    DOK.write_bytes(original_bajty)   # vzdy vratit original (bajt po bajtu)
    vraceno = DOK.read_bytes()
    assert vraceno == original_bajty, "POZOR: original se nepodarilo vratit z bajtu!"
    print("  original vracen z bajtu a overen shodou bajtu")

print()
if kod == 0:
    print("VYSLEDEK: brana PROSLA nad dokumentem bez obsahu -> merit PRITOMNOST, ne obsah.")
    print("          Jeji '9/9' tedy znamena 'vsechny markery tam jsou', ne 'analyza je kvalitni'.")
    sys.exit(1)
print(f"VYSLEDEK: brana SPADLA nad kostrou (exit={kod}) -> obsah ji zajima.")
sys.exit(0)

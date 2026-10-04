# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""Mutační test A3: chytí brána `a3-over.py` odstranění `exit 1` v HERNÍ kopii?

Proč zvlášť: A3 bylo provedeno ve DVOU kopiích `agent.yml` (šablona + hra) a to
je přesně to, co se dá snadno udělat jen v jedné. Brána, která by kontrolovala
jen šablonu, by prošla — a v herním repu by vada zůstala.

Mutuje se jen HERNÍ kopie; šablona zůstává nedotčená, aby výsledek říkal
něco o tom, kterou kopii brána vidí. ´exit 1´ je na konci `run:` bloku kroku
"Když pravidla neprošla" — a to je jediné místo, kde na konci řádku stojí.

Spusteni:  $env:PYTHONIOENCODING='utf-8'; python _analyza\a3-mutace.py
"""
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
HRA = _HRA / ".github" / "workflows" / "agent.yml"
SABLONA = WS / "repo" / ".github" / "workflows" / "agent.yml"
BRANA = WS / "_analyza" / "a3-over.py"


def spust_branu():
    r = subprocess.run([sys.executable, str(BRANA)],
                       capture_output=True, text=True, encoding="utf-8")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


if not HRA.is_file():
    print(f"CHYBA: {HRA} neexistuje")
    sys.exit(2)

orig_bajty = HRA.read_bytes()
orig = orig_bajty.decode("utf-8")
sablona_orig = SABLONA.read_bytes()

# Vzor: posledni radek run bloku kroku s `exit 1`. V YAML je odsazeny 10 mezerami.
VZOR = re.compile(r"^(          exit 1)$", re.M)
nalezeno = VZOR.findall(orig)

print("=== Mutační test A3 (herní kopie) ===\n")
print(f"  `exit 1` na vlastním řádku v herní kopii: {len(nalezeno)}x")

kod, vystup = spust_branu()
print(f"  0) vychozi stav: exit={kod}")
if kod != 0:
    print("     POZOR: vychozi stav neprochazi.")
    sys.exit(1)

selhalo = []
try:
    # Mutace: odstranit VŠECHNY `exit 1` na vlastním řádku v herní kopii.
    # Kdyby jich bylo vic, je to taky nalez — proto se pocet hlasi.
    zmutovany, pocet = VZOR.subn("          true   # (smazano mutaci)", orig)
    assert pocet == len(nalezeno) and pocet > 0, "mutace neprovedla to, co mela"
    assert "\n          exit 1\n" not in zmutovany, "v herni kopii zustal exit 1"
    HRA.write_text(zmutovany, encoding="utf-8", newline="")
    kod, vystup = spust_branu()
    print(f"\n  1) smazano {pocet}x `exit 1` v HERNI kopii: exit={kod}")
    for l in vystup.splitlines():
        if "CHYBA" in l or "hra" in l.lower():
            print("        " + l.strip())
    ok = kod != 0
    print(f"     -> {'SPRAVNE SPADLA' if ok else 'SLEPA — vada v herni kopii ji nechala zelenou!'}")
    if not ok:
        selhalo.append("odstraneni exit 1 v herni kopii")
finally:
    HRA.write_bytes(orig_bajty)
    assert HRA.read_bytes() == orig_bajty, "herni agent.yml se nepodarilo vratit!"

# Kontrola, ze se šablona vubec nezmenila (mutovalo se jen ve hre)
assert SABLONA.read_bytes() == sablona_orig, "POZOR: zmenila se i sablona!"

kod, vystup = spust_branu()
print(f"\n  po vraceni originalu: exit={kod}")

print()
if selhalo:
    print(f"VYSLEDEK: brana je SLEPA: {'; '.join(selhalo)}")
    sys.exit(1)
print("VYSLEDEK: brana spravne spadla na vade v HERNI kopii a vychozi stav prochazi.")
sys.exit(0)

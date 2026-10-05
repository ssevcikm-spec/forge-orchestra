# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
"""A3: ověří, že krok "Když pravidla neprošla" končí `exit 1` v OBOU kopiích.

Proč vlastní skript a ne grep: v `agent.yml` je `exit 1` už 5x JINDE (všechny
před auto-merge), takže hledání v celém souboru najde je a nic nedokáže.
Kontroluje se NA ŘÁDKU, uvnitř `run:` bloku toho jednoho kroku.

Druhá past, na kterou se tu narazilo: porovnávat název kroku napevno
v řetězci prohání diakritiku konzolí. Proto se název hledá podle
BEZPEČNÉHO PREFIXU ("Když pravidla") a čte se z YAML, ne z textu.
"""

import io
import pathlib
import sys

sys.stdout.reconfigure(encoding="utf-8", errors="replace")

try:
    import yaml
except ImportError:
    print("CHYBA: chybí PyYAML")
    sys.exit(2)

KOPIE = [
    ("šablona", pathlib.Path(_REPO / 'repo' / '.github' / 'workflows' / 'agent.yml')),
    ("hra", pathlib.Path(_HRA / '.github' / 'workflows' / 'agent.yml')),
]

PREFIX = "Když pravidla"

chyby = []
kontrol = 0
for jmeno, cesta in KOPIE:
    if not cesta.exists():
        chyby.append(f"{jmeno}: soubor neexistuje: {cesta}")
        continue
    kontrol += 1
    data = yaml.safe_load(cesta.read_text(encoding="utf-8"))
    # POZOR: krok je v jobu `auto-merge`, NE v `agent`. Kdo hledá v `agent`,
    # najde 0 a vypadá to jako vrácená vada — což se při psaní tohohle
    # skriptu stalo. Proto se procházejí VŠECHNY joby.
    nalezene = []
    for jn, job in data["jobs"].items():
        for s in job.get("steps", []) or []:
            if str(s.get("name", "")).startswith(PREFIX):
                nalezene.append((jn, s))
    if len(nalezene) != 1:
        chyby.append(f"{jmeno}: kroků začínajících '{PREFIX}' je {len(nalezene)}, čekán 1")
        continue
    jn, krok = nalezene[0]
    run = krok.get("run", "")
    radky = [r for r in run.splitlines() if r.strip()]
    posledni = radky[-1].strip() if radky else ""
    # Počet `exit 1` v CELÉM souboru (pro kontext, není to kritérium).
    vsechny = cesta.read_text(encoding="utf-8").count("exit 1")
    print(f"{jmeno:8} job {jn!r} krok: {krok['name']!r}")
    print(f"         poslední řádek run: {posledni!r}   (exit 1 v celém souboru: {vsechny}x)")
    if posledni != "exit 1":
        chyby.append(f"{jmeno}: krok nekončí 'exit 1', ale {posledni!r}")

print()
if chyby:
    for c in chyby:
        print("CHYBA:", c)
    # Čítač i u vady — `g3-brany.py` ho čte jako „kolik toho brána otevřela".
    print(f"ZMĚŘENO: {kontrol} kontrol, {len(chyby)} chyb")
    sys.exit(1)
print("OK: obě kopie mají 'exit 1' na konci kroku 'Když pravidla neprošla'.")
# ⚠ P13c (4. 10. 2026): čítač se MUSÍ vytisknout, jinak `g3` u téhle brány
# ukazoval „otevřela: 1" — a to bylo **první číslo v díře ve výstupu**
# (mezera za `job`), ne počet kontrol. Přesně past z `overovani` §10.1.
print(f"ZMĚŘENO: {kontrol} kontrol, 0 chyb")
sys.exit(0)

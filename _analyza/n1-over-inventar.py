# P8b (presun na E:, 4. 10. 2026): `_analyza/` je v repu, takze
#   REPO    = root repa (_analyza/.. )
#   STANICE = alias na REPO (HANDOFF, KRONIKA i _analyza se presunuly do repa)
#   HRA     = sourozenec repa (byla `WS/games/uo-shadows`)
import pathlib as _pl
_REPO = _pl.Path(__file__).resolve().parents[1]
_STANICE = _REPO  # dokumenty projektu jsou v repu (presun na E:, 4. 10. 2026)
_HRA = _REPO.parent / "uo-shadows"
r"""N1 (bod 6 z §7.2) — měří, jestli nástroj POZNÁ zastaralý inventář.

━━ CO SE ZMĚNILO 2. 10. 2026 (a proč tenhle test vypadá jinak) ━━
Původní verze tohohle testu měřila jedinou věc: *„vygeneruje si
`hl-rizika-jazyka.py` inventář sám, když se kód změní?"* a **zelená znamenala
N1 JE PRAVDA** (což je vada). Jenže **N1 se tou dobou OPRAVIL** — nástroj dnes
stáří inventáře **pozná** (otisk vstupů) a při rozchodu **skončí nenulově**.
Tím se původní test obrátil: správné chování v něm vypadalo jako nález.

Přesně to je past, kterou popisuje `AGENTS.md`: *„Než označíš cizí číslo za
nepravdivé, zkopíruj postup, kterým vzniklo"* — a taky *„test je červený,
protože našel vadu → nechá se červený a POJMENUJE SE, co ho opraví"*.
Opravil ho krok **C2** (stáří + otisk vstupů + `exit 1`), a tenhle test se mu
proto **přizpůsobil**: už netvrdí „N1 je pravda/vyvrácen", ale **měří chování,
které má nástroj po opravě**.

━━ CO MĚŘÍ TEĎ (čtyři běhy, pořadí je závazné) ━━
  1. **ZDRAVÝ inventář**        → `exit 0` (jinak by další běhy nic nedokázaly)
  2. **OTISK PŘEPSÁN** (simulace: kód se od vzniku inventáře změnil)
                                → `exit 1` a text o zastaralosti
  3. **INVENTÁŘ BEZ OTISKU** (starší formát)  → `exit 1` (nezměřeno není zelená)
  4. **ZDRAVÝ inventář znovu**  → `exit 0` (návrat bajt na bajt)

⚠ **Co se tím NEMĚŘÍ:** to, jestli nástroj čte hodnoty ze zastaralého snapshotu
**tiše**. Po opravě je to bezpředmětné — zastaralý snapshot **zastaví běh**,
takže se z něj nikdy nečtou čísla jako platná. Kdo chce měřit „tiše", musí
nejdřív vypnout tu pojistku (a to je zásah do kódu, ne test).

Použití:  $env:PYTHONIOENCODING='utf-8'; python _analyza\n1-over-inventar.py
"""

import hashlib
import json
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(_STANICE)
INVENTAR = WS / "_analyza" / "_inventar.json"
RIZIKA = WS / "_analyza" / "hl-rizika-jazyka.py"

if not INVENTAR.is_file() or not RIZIKA.is_file():
    print("CHYBA: chybí %s nebo %s" % (INVENTAR, RIZIKA))
    sys.exit(2)

puvodni = INVENTAR.read_bytes()
otisk = hashlib.sha256(puvodni).hexdigest()[:16]
vysledky = []


def spust() -> tuple:
    r = subprocess.run([sys.executable, str(RIZIKA)], capture_output=True,
                       text=True, encoding="utf-8", cwd=str(WS))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def obnov() -> bool:
    INVENTAR.write_bytes(puvodni)
    return hashlib.sha256(INVENTAR.read_bytes()).hexdigest()[:16] == otisk


def zmen(uprav) -> None:
    d = json.loads(INVENTAR.read_text(encoding="utf-8"))
    uprav(d)
    INVENTAR.write_bytes(json.dumps(d, ensure_ascii=False, indent=2).encode("utf-8"))


def vypis(v: str) -> None:
    for radek in v.splitlines():
        if any(k in radek for k in ("INVENTÁŘ:", "otisk", "CHYBA", "ZASTARALÝ",
                                    "SEZNAM SEDÍ", "NELZE ověřit")):
            print("     " + radek.strip()[:120])


print("=== N1: pozná `hl-rizika-jazyka.py` ZASTARALÝ inventář? ===")
print("  inventář: %d B, sha256 %s…\n" % (len(puvodni), otisk))

# ── 1) zdravý stav ───────────────────────────────────────────────────────────
print("  1) ZDRAVÝ inventář (kontrola, že brána umí projít)")
kod, v = spust()
vypis(v)
vysledky.append(("zdravý", kod, 0))
print("     → exit=%d (očekáváno 0)\n" % kod)
if kod != 0:
    print("  CHYBA: brána neprojde ani ve zdravém stavu — další běhy by nic nedokázaly")
    sys.exit(2)

# ── 2) otisk přepsán ─────────────────────────────────────────────────────────
print("  2) OTISK V INVENTÁŘI PŘEPSÁN (simulace: kód se změnil)")
zmen(lambda d: d["otisk_vstupu"].__setitem__("sha256", "0" * 64))
kod, v = spust()
vypis(v)
vysledky.append(("přepsaný otisk", kod, 1))
print("     → exit=%d (očekáváno 1)\n" % kod)
if not obnov():
    print("  CHYBA: inventář se nevrátil")
    sys.exit(2)

# ── 3) inventář bez otisku ───────────────────────────────────────────────────
print("  3) INVENTÁŘ BEZ OTISKU (starší formát — stáří se nedá ověřit)")
zmen(lambda d: d.pop("otisk_vstupu", None))
kod, v = spust()
vypis(v)
vysledky.append(("bez otisku", kod, 1))
print("     → exit=%d (očekáváno 1)\n" % kod)
if not obnov():
    print("  CHYBA: inventář se nevrátil")
    sys.exit(2)

# ── 4) návrat ────────────────────────────────────────────────────────────────
print("  4) NÁVRAT do zdravého stavu (bajt na bajt)")
kod, v = spust()
vypis(v)
vysledky.append(("návrat", kod, 0))
print("     → exit=%d (očekáváno 0)\n" % kod)

# ── souhrn ───────────────────────────────────────────────────────────────────
if not obnov():
    print("CHYBA: inventář se nevrátil na konci!")
    sys.exit(2)

spatne = 0
print("  %-20s %-6s %s" % ("běh", "exit", "výsledek"))
for jmeno, kod, ocekavano in vysledky:
    ok = kod == ocekavano
    if not ok:
        spatne += 1
    print("  %-20s %-6d %s" % (jmeno, kod, "OK" if ok else "!! očekáváno %d" % ocekavano))

print()
if spatne == 0:
    print("VYSLEDEK: N1 JE OPRAVEN — zastaralý i nezměřený inventář SHODÍ nástroj")
    print("          (a zdravý projde). Nástroj nad zastaralým snapshotem")
    print("          netvrdí „0 vrácených“.")
    sys.exit(0)
print("VYSLEDEK: NĚCO NESEDÍ (%d běhů mimo očekávání) — viz tabulka výš." % spatne)
sys.exit(1)

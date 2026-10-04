#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""Úkol C2 (nález N1) — `hl-rizika-jazyka.py` čte zastaralý inventář a tvrdí „0 vrácených“.

CO BYLO NAMĚŘENO:
  Inventář `_analyza\\_inventar.json` se generuje JEN když CHYBÍ. Když existuje,
  nástroj ho použije, i kdyby byl libovolně starý — a nad zastaralým snapshotem
  vypíše zelené „0 očekávaných, 11 přejednaných, 0 vrácených“. Kontrola tvrdí
  něco jiného, než je pravda: nemůže vidět identifikátor, který se do kódu vrátil
  po vzniku inventáře.

CO DĚLÁ TENHLE PATCH:
  1. vypíše STÁŘÍ inventáře (a otisk vstupů, ze kterých vznikl),
  2. přepočítá AKTUÁLNÍ otisk vstupů (půjčí si ho ze skeneru přes `--otisk`),
  3. když se otisk rozešel → `exit 1` s návodem, jak inventář obnovit,
  4. když se nástroj nedokáže zeptat → taky `exit 1` (nezměřeno není zelená).

⚠ NÁSTROJ MUSÍ ZŮSTAT POUZE ČTOUCÍ. Sekce L validátoru (`validate-all.mjs:333`)
odmítne spustit každý nástroj, jehož zdroj obsahuje text spouštějící zápis
(`write_…`, `copyfile`, …) — naměřeno 2. 10. 2026: stačilo to slovo v KOMENTÁŘI
a validátor vypsal „NEBYL spuštěn“. Obnova inventáře proto zůstává na člověku
a tenhle nástroj ji jen OHLÁSÍ. (V komentáři je to popsané slovy schválně.)

Použití:
    python _analyza\\c2-oprav-n1.py            # zapíše
    python _analyza\\c2-oprav-n1.py --zpet     # vrátí zpět
"""

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ANALYZA = Path(__file__).resolve().parent
CIL = ANALYZA / "hl-rizika-jazyka.py"
ZALOHA = ANALYZA / "c2-hl-rizika-puvodni.py"

# ------------------------------------------------------------------ starý blok
STARY = '''if not INVENTAR.is_file():
    # MEZIPRODUKT SE GENERUJE SÁM. Naměřeno 1. 10. 2026 (test předání): po
    # smazání `_inventar.json` skript spadl s „chybí …“ — a nová session by
    # musela hádat, co pustit prvního. Nástroj, který se dá spustit jen
    # v určitém pořadí, je pro předání past; má si vstupy obstarat sám.
    print(f"  (inventář {INVENTAR.name} chybí — generuji ho, může to chvíli trvat…)")
    import subprocess
    r = subprocess.run([sys.executable, str(WS / "_analyza" / "hl-neanglicky-v-kodu.py"),
                        "--json", str(INVENTAR)], cwd=str(WS))
    if r.returncode != 0 or not INVENTAR.is_file():
        raise SystemExit(f"CHYBA: inventář se nepodařilo vygenerovat (exit {r.returncode})")
'''

# ------------------------------------------------------------------ nový blok
NOVY = '''SKENER = WS / "_analyza" / "hl-neanglicky-v-kodu.py"
INVENTAR_CMD = ("python _analyza\\\\hl-neanglicky-v-kodu.py --json "
                "_analyza\\\\_inventar.json")


def _otisk_z_skeneru():
    """Aktuální otisk vstupů — PŮJČENÝ ze skeneru, ne druhá implementace.

    Vrací (otisk, None) nebo (None, důvod). `hl-rizika-jazyka.py` musí zůstat
    POUZE ČTOUCÍ: sekce L validátoru odmítne spustit nástroj, jehož zdroj
    obsahuje text spouštějící zápis (naměřeno 2. 10. 2026 — stačilo to slovo
    v komentáři). Přepočet otisku proto dělá skener a tenhle nástroj si ho
    jen vyzvedne; kdyby tu byla vlastní kopie výpočtu, jednou se rozejde.
    """
    import subprocess
    if not SKENER.is_file():
        return None, f"skener {SKENER.name} není k dispozici"
    try:
        r = subprocess.run([sys.executable, str(SKENER), "--otisk"],
                           capture_output=True, text=True, encoding="utf-8",
                           cwd=str(WS), timeout=900)
    except Exception as e:                                  # noqa: BLE001
        return None, f"skener se nepodařilo spustit: {type(e).__name__}: {e}"
    if r.returncode != 0:
        return None, f"skener skončil exit {r.returncode}: {(r.stderr or '').strip()[:160]}"
    try:
        return json.loads(r.stdout.strip()), None
    except Exception as e:                                  # noqa: BLE001
        return None, f"výstup skeneru není JSON: {e}"


# ── STÁŘÍ INVENTÁŘE (nález N1) ────────────────────────────────────────────────
# PROČ: inventář se do 2. 10. 2026 generoval JEN když chyběl. Když existoval,
# použil se i libovolně starý — a nástroj nad ním vypsal zelené „0 vrácených“.
# To je tvrzení o KÓDU, které platí jen o snapshotu. Proto se teď stáří vypíše
# a nesouhlasný otisk vstupů shodí nástroj s nenulovým kódem.
import datetime as _dt

_stari_h = None
if INVENTAR.is_file():
    _stari_h = (time.time() - INVENTAR.stat().st_mtime) / 3600.0

if not INVENTAR.is_file():
    # MEZIPRODUKT SE GENERUJE SÁM. Naměřeno 1. 10. 2026 (test předání): po
    # smazání `_inventar.json` skript spadl s „chybí …“ — a nová session by
    # musela hádat, co pustit prvního. Nástroj, který se dá spustit jen
    # v určitém pořadí, je pro předání past; má si vstupy obstarat sám.
    #
    # ⚠ ALE NESMÍ SKONČIT ZELENĚ, KDYŽ SE TO NEPOVEDE (nález N1, 2. 10. 2026):
    # dřív se jen zavolal skener a při neúspěchu se spadlo — jenže když skener
    # prošel a soubor stejně nevznikl, pokračovalo se dál a výsledek vypadal
    # jako „0 vrácených“. Teď se každá z těch cest ukončí NENULOVĚ.
    print(f"  (inventář {INVENTAR.name} chybí — generuji ho, může to chvíli trvat…)")
    import subprocess
    r = subprocess.run([sys.executable, str(SKENER), "--json", str(INVENTAR)], cwd=str(WS))
    if r.returncode != 0:
        raise SystemExit(
            f"CHYBA: inventář se nepodařilo vygenerovat (skener exit {r.returncode}).\\n"
            f"       Nástroj nad chybějícím inventářem NIC nezměřil — končí nenulově,\\n"
            f"       aby se „0 vrácených“ nečetlo jako kladný nález.\\n"
            f"       Obnov ho ručně: {INVENTAR_CMD}")
    if not INVENTAR.is_file():
        raise SystemExit(
            f"CHYBA: skener skončil úspěšně, ale {INVENTAR} stejně nevznikl.\\n"
            f"       Nezměřeno není zelená — končím nenulově. Obnov ho ručně:\\n"
            f"       {INVENTAR_CMD}")
    _stari_h = (time.time() - INVENTAR.stat().st_mtime) / 3600.0

# Otisk se bere z inventáře; starší inventáře (bez otisku) se hlásí jako
# nezměřitelné stáří — ne jako „v pořádku“.
_otisk_inv = None
try:
    _otisk_inv = json.loads(INVENTAR.read_text(encoding="utf-8")).get("otisk_vstupu")
except Exception:                                            # noqa: BLE001
    _otisk_inv = None

_otisk_teď, _duvod = _otisk_z_skeneru()
_inv_popis = (f"stáří {_stari_h:.2f} h"
              if _stari_h is not None else "stáří NEZMĚŘENO")
if _otisk_inv is None:
    _inv_popis += ", otisk vstupů v něm NENÍ (starší formát)"

print("═" * 80)
print(f"INVENTÁŘ: {INVENTAR.name}  ({_inv_popis}, "
      f"{INVENTAR.stat().st_size} B)" if _stari_h is not None
      else f"INVENTÁŘ: {INVENTAR.name}  ({_inv_popis})")

_rozchod = None
if _otisk_inv is None:
    _rozchod = "inventář neobsahuje otisk vstupů — NELZE ověřit, že sedí s kódem"
elif _otisk_teď is None:
    _rozchod = f"aktuální otisk se nepodařilo zjistit ({_duvod})"
elif _otisk_inv.get("sha256") != _otisk_teď.get("sha256"):
    _rozchod = ("otisk VSTUPŮ se rozešel — kód se od vzniku inventáře změnil:\\n"
                f"       v inventáři: {_otisk_inv.get('sha256', '?')[:16]}"
                f"  ({_otisk_inv.get('souboru', '?')} souborů)\\n"
                f"       teď:         {_otisk_teď.get('sha256', '?')[:16]}"
                f"  ({_otisk_teď.get('souboru', '?')} souborů)")
else:
    print(f"  otisk vstupů SEDÍ: {_otisk_teď['sha256'][:16]} "
          f"({_otisk_teď['souboru']} souborů) — inventář je z TOHOHLE kódu")

if _rozchod:
    print("═" * 80)
    print()
    print("CHYBA: INVENTÁŘ JE ZASTARALÝ / NEZMĚŘENÝ")
    print(f"  {_rozchod}")
    print()
    print("  Slovy zadání: „nula a nezměřeno nejsou úspěch“. Nad tímhle")
    print("  inventářem se NEDÁ tvrdit „0 vrácených“ — chybí mu právě ty")
    print("  soubory, které se od jeho vzniku změnily.")
    print()
    print("  Obnov inventář a spusť to znovu:")
    print(f"    {INVENTAR_CMD}")
    print(f"    python _analyza\\\\{Path(__file__).name}")
    print()
    print("  (Automatická obnova je záměrně VYPNUTÁ: sekce L validátoru")
    print("   odmítne spustit nástroj, jehož zdroj obsahuje text spouštějící")
    print("   zápis — naměřeno 2. 10. 2026, stačilo to slovo v komentáři.)")
    sys.exit(1)
'''

# čas potřebujeme pro stáří inventáře
STARY_IMPORT = "import json\nimport pathlib\nimport re\nimport sys\n"
NOVY_IMPORT = "import json\nimport pathlib\nimport re\nimport sys\nimport time\n"


def main() -> int:
    zpet = "--zpet" in sys.argv
    text = CIL.read_text(encoding="utf-8")

    if zpet:
        if not ZALOHA.exists():
            print("CHYBA: záloha %s neexistuje" % ZALOHA)
            return 2
        puvodni = ZALOHA.read_text(encoding="utf-8")
        CIL.write_bytes(puvodni.encode("utf-8"))
        assert CIL.read_text(encoding="utf-8") == puvodni
        print("OK: vráceno ze zálohy (%d znaků)" % len(puvodni))
        return 0

    if NOVY in text:
        print("OK: oprava už v souboru je")
        return 0
    if text.count(STARY) != 1:
        print("CHYBA: starý blok nalezen %d× — očekávám 1×" % text.count(STARY))
        return 2
    if text.count(STARY_IMPORT) != 1:
        print("CHYBA: import blok nalezen %d× — očekávám 1×" % text.count(STARY_IMPORT))
        return 2

    if not ZALOHA.exists():
        ZALOHA.write_bytes(text.encode("utf-8"))
        print("záloha: %s" % ZALOHA.name)

    novy = text.replace(STARY, NOVY, 1).replace(STARY_IMPORT, NOVY_IMPORT, 1)
    assert novy != text, "MUTACE NEPROBĚHLA"
    CIL.write_bytes(novy.encode("utf-8"))

    z5 = CIL.read_text(encoding="utf-8")
    assert z5 == novy, "zapsaný obsah nesedí"
    assert "otisk_vstupu" in z5 and "INVENTÁŘ JE ZASTARALÝ" in z5
    # Pojistka: nástroj musí zůstat POUZE ČTOUCÍ (sekce L validátoru).
    for zakazane in ("write_text", "write_bytes", "copyfile", "copy2",
                     "writeFileSync", "write_text(", "shutil.copy"):
        if zakazane in z5:
            print("CHYBA: v souboru je %r — sekce L by nástroj odmítla spustit"
                  % zakazane)
            return 2
    print("OK: %s přepsán (%d → %d znaků)" % (CIL, len(text), len(z5)))
    return 0


if __name__ == "__main__":
    sys.exit(main())

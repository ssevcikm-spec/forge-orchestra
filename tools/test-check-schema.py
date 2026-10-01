"""Offline testy `check-schema.py` – brána, která 1. 10. 2026 tiše přestala měřit.

CO SE TÍM TESTOVALO A PROČ TO EXISTUJE
--------------------------------------
`check-schema.py` hledal výchozí buňku v `scripts/level.gd` vzorcem
`var cell := 16`. Po migraci hry na izometrii se z toho stalo
`const CELL_W_DEFAULT := 96` + `const CELL_H_DEFAULT := 48`. Regexy nenašly
nic, cyklus proběhl nad PRÁZDNÝM seznamem – a kontrola hlásila zelenou.
Kdo se na ni spoléhal, spoléhal se na nic.

Testy proto netvrdí jen „projde to". Mají **známý správný i známý chybný
případ** a u obojího se kontroluje, že to nástroj POJMENUJE:

    1. správná izometrie (const CELL_W_DEFAULT := 96, _H_ := 48) → 0 vad
    2. správná izometrie, ale ŠPATNÉ číslo (95)                    → vada
    3. starý čtvercový tvar (`var cell := 16`)                     → vada
    4. fallback přes `get("cell", N)` se přečte                    → 0 vad
    5. tvar, který přečíst NEJDE (identifikátor místo čísla)       → vada
       (ne ticho! právě ticho byla ta původní chyba)
    6. CLI vypíše nezměřený fallback jako „nezměřeno", ne jako `[]`
    7. pořadí: když je v souboru `var cell := 16` i `const CELL_W_DEFAULT := 96`,
       vyhrává POSLEDNÍ deklarace (jinak by test 3 procházel náhodou)

Použití:  python orchestra/tools/test-check-schema.py
Návratový kód: 0 = všechny testy prošly, 1 = některý ne.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

HERE = Path(__file__).resolve().parent
KANDIDATI = [
    HERE.parent / "repo" / ".forge" / "check-schema.py",
    HERE.parent.parent / "games" / "uo-shadows" / ".forge" / "check-schema.py",
]

ok = chyb = 0


def t(nazev: str, podminka: bool, detail: str = "") -> None:
    global ok, chyb
    if podminka:
        print(f"  OK   {nazev}")
        ok += 1
    else:
        print(f"  FAIL {nazev}{f' – {detail}' if detail else ''}")
        chyb += 1


def _najdi_nastroj() -> Path:
    for k in KANDIDATI:
        if k.is_file():
            return k
    print("CHYBA: check-schema.py nenalezen v žádné z očekávaných cest")
    sys.exit(1)


NASTROJ = _najdi_nastroj()

# Načte se STEJNÝ soubor, jaký se pouští v CI – ne kopie. Kdyby se načetl jiný,
# testy by hlídaly něco, co v provozu neběží.
_spec = importlib.util.spec_from_file_location("check_schema_testovany", NASTROJ)
mod = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(mod)


# ------------------------------------------------------------------ fixtury ----
def spec_json() -> dict:
    """Izometrické zadání – 96×48 dlaždice, viewport 960×540."""
    return {
        "projekce": {"typ": "izometricka", "dlazdice_sirka": 96,
                     "dlazdice_vyska": 48, "viewport": [960, 540]},
        "role": {},
    }


def _repo(tmp: Path, level_gd: str, *, cell: int = 96,
          viewport=(960, 540), tile_size=(96, 48)) -> Path:
    """Postaví minimální herní repo, na kterém jde schéma měřit."""
    (tmp / "assets" / "levels").mkdir(parents=True)
    (tmp / "assets" / "tiles").mkdir(parents=True)
    (tmp / "assets" / "sprites").mkdir(parents=True)
    (tmp / "scripts").mkdir(parents=True)
    (tmp / "assets" / "spec.json").write_text(
        json.dumps(spec_json(), ensure_ascii=False), encoding="utf-8")
    (tmp / "assets" / "levels" / "main.json").write_text(
        json.dumps({"cell": cell, "viewport": list(viewport),
                    "width": 10, "height": 10}), encoding="utf-8")
    (tmp / "assets" / "tiles" / "manifest.json").write_text(
        json.dumps({"tile_size": list(tile_size)}), encoding="utf-8")
    (tmp / "scripts" / "level.gd").write_text(level_gd, encoding="utf-8")
    return tmp


def _gd_iso(w: int = 96, h: int = 48) -> str:
    """Tvar, který hra používá DNES: dvě konstanty kvůli kosočtverci."""
    return (f"const CELL_W_DEFAULT := {w}\n"
            f"const CELL_H_DEFAULT := {h}\n"
            "var cell_w := CELL_W_DEFAULT\n"
            "var cell_h := CELL_H_DEFAULT\n"
            'var marker_cell: Array = m.get("cell", [0, 0])\n')


def _gd_iso_fallback(w: int = 96, h: int = 48) -> str:
    return _gd_iso(w, h) + 'var c: Array = m.get("cell", 96)\n'


def _gd_stary_ctverec(cell: int = 16) -> str:
    """Tvar PŘED migrací – na tom se ukázalo, že migrace je potřeba."""
    return (f"var cell := {cell}\n"
            "var grid := PackedStringArray()\n")


def _gd_nectitelny() -> str:
    """Platný GDScript, ale výchozí buňka je IDENTIFIKÁTOR, ne číslo.

    Přesně tenhle případ musí skončit hláškou „kontrola neproběhla" – kdyby
    skončil tichem, vrátila by se původní chyba v novém kabátě.

    POZOR: vzorek musí být nečitelný CELÝ. Kdyby tu zůstalo jediné čitelné
    číslo (`var cell_h := 48`), kontrola správně změří aspoň jednu osu a
    ohlásí jen chybějící šířku – což je jiný (a také správný) výsledek.
    """
    return ("const VELIKOST := 96\n"
            "var cell_w := VELIKOST\n"
            "var cell_h := VELIKOST\n")


print(f"=== test-check-schema.py – offline testy ({NASTROJ.name}) ===")
print(f"  nástroj: {NASTROJ}")
print(f"  sha256:  {hashlib.sha256(NASTROJ.read_bytes()).hexdigest()[:16]}")

# 0) ŠABLONA A HRA MUSÍ BÝT SHODNÉ. Drift mezi nimi je sám o sobě vada:
#    opraví se jedna kopie, druhá mlčky zůstane rozbitá – a příští hra dostane
#    tu starou. Přesně to se stalo při téhle opravě (test na to přišel).
if all(k.is_file() for k in KANDIDATI):
    hashe = [hashlib.sha256(k.read_bytes()).hexdigest() for k in KANDIDATI]
    t("šablona a herní repo mají SHODNÝ check-schema.py",
      len(set(hashe)) == 1,
      " | ".join(f"{k.parent.parent.parent.name}={h[:12]}"
                 for k, h in zip(KANDIDATI, hashe)))

tmp = Path(tempfile.mkdtemp(prefix="schema-test-"))
try:
    # 1) ZNÁMÝ SPRÁVNÝ STAV: izometrie 96×48 → žádná vada.
    r = _repo(tmp / "a-iso", _gd_iso())
    vady, varovani, poznamky, data = mod.zkontroluj(r)
    t("správná izometrie: žádné vady", not vady, "; ".join(vady)[:120])
    t("správná izometrie: výchozí buňka se PŘEČTE jako 96×48",
      data.get("level_gd", {}).get("vychozi") == {"sirka": 96, "vyska": 48},
      str(data.get("level_gd", {}).get("vychozi")))
    t("správná izometrie: fallback se čte jako nezměřený (v kódu není)",
      data.get("level_gd", {}).get("fallback") == {},
      str(data.get("level_gd", {}).get("fallback")))

    # 2) ZNÁMÝ CHYBNÝ STAV: správný tvar, ŠPATNÉ číslo.
    r = _repo(tmp / "b-95", _gd_iso(w=95))
    vady, *_ = mod.zkontroluj(r)
    t("špatná šířka (95 vs 96) se POJMENUJE",
      any("95" in v and "96" in v for v in vady), "; ".join(vady)[:120])
    t("špatná výška (47 vs 48) se POJMENUJE",
      any("47" in v and "48" in v
          for v in mod.zkontroluj(_repo(tmp / "b-47", _gd_iso(h=47)))[0]),
      "výška se neporovnává zvlášť")

    # 3) ZNÁMÝ CHYBNÝ STAV: starý čtvercový tvar (16 px) proti specu 96×48.
    r = _repo(tmp / "c-stary", _gd_stary_ctverec(16))
    vady, *_ = mod.zkontroluj(r)
    t("starý `var cell := 16` se POJMENUJE jako vada",
      any("16" in v for v in vady), "; ".join(vady)[:120])
    t("starý tvar: číslo se změří (ne prázdný seznam)",
      mod.zkontroluj(r)[3].get("level_gd", {}).get("vychozi") ==
      {"sirka": 16, "vyska": 16},
      str(mod.zkontroluj(r)[3].get("level_gd", {}).get("vychozi")))

    # 4) Fallback přes `get("cell", N)` se přečte.
    r = _repo(tmp / "d-fallback", _gd_iso_fallback())
    vady, varovani, poznamky, data = mod.zkontroluj(r)
    t("fallback `get(\"cell\", 96)` se PŘEČTE", not vady, "; ".join(vady)[:120])
    t("fallback se hlásí jako změřený",
      data.get("level_gd", {}).get("fallback") == {"sirka": 96},
      str(data.get("level_gd", {}).get("fallback")))

    # 5) NEČITELNÝ TVAR = VADA (ne ticho). Tohle je jádro celé opravy.
    r = _repo(tmp / "e-nectitelny", _gd_nectitelny())
    vady, varovani, poznamky, data = mod.zkontroluj(r)
    t("nečitelný tvar: kontrola HLÁSÍ, že neproběhla (vada)",
      any("NEPODAŘILO" in v for v in vady), "; ".join(vady)[:150])
    t("nečitelný tvar: šířka se netváří jako změřená",
      "sirka" not in data.get("level_gd", {}).get("vychozi", {}),
      str(data.get("level_gd", {}).get("vychozi")))

    # 6) CLI nesmí vypsat `[]` – prázdno vypadá jako naměřená nula.
    cli = subprocess.run([sys.executable, str(NASTROJ), str(tmp / "a-iso")],
                         capture_output=True, text=True, encoding="utf-8",
                         errors="replace")
    t("CLI vypíše nezměřený fallback jako „nezměřeno“",
      "nezměřeno" in cli.stdout and "[]" not in cli.stdout,
      cli.stdout.strip().splitlines()[-1][:100] if cli.stdout else "bez výstupu")
    t("CLI na správném repu končí exit 0", cli.returncode == 0,
      f"exit={cli.returncode}")

    cli_spatne = subprocess.run([sys.executable, str(NASTROJ), str(tmp / "b-95")],
                                capture_output=True, text=True, encoding="utf-8",
                                errors="replace")
    t("CLI na chybném repu končí exit 1", cli_spatne.returncode == 1,
      f"exit={cli_spatne.returncode}")

    # 7) POŘADÍ DEKLARACÍ: `var cell := 16` i `const CELL_W_DEFAULT := 96`
    #    v jednom souboru. Bere se poslední, která platí (jinak by test 3
    #    procházel jen náhodou a oprava by mohla být obcházena).
    kombinovane = _gd_stary_ctverec(16) + _gd_iso()
    r = _repo(tmp / "f-kombi", kombinovane)
    data = mod.zkontroluj(r)[3]
    t("při obou tvarech platí POSLEDNÍ deklarace (96×48)",
      data.get("level_gd", {}).get("vychozi") == {"sirka": 96, "vyska": 48},
      str(data.get("level_gd", {}).get("vychozi")))

    # 8) Pojistka proti mrtvé kontrole: smazaný `world.gd` musí být vidět.
    r = _repo(tmp / "g-bez-world", _gd_iso())
    poznamky = mod.zkontroluj(r)[2]
    t("chybějící world.gd se hlásí jako mrtvá kontrola",
      any("world.gd" in p for p in poznamky), "; ".join(poznamky)[:120])
finally:
    shutil.rmtree(tmp, ignore_errors=True)

print()
print(f"Testů OK: {ok}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)

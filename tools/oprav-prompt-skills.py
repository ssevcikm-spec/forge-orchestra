"""Chirurgická výměna promptu granule core.skills – beze změny formátování.

Předchozí verze použila json.dumps, což přeformátovalo celý soubor (265 řádků
diffu) – zbytečný šum v historii a riziko konfliktu při rebase. Nahrazuje se
proto jen text hodnoty `prompt` u dané granule, bajt po bajtu.
"""

import json
import pathlib
import sys

CESTA = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\roadmap.json")

NOVY = (
    "V scripts/skills.gd vytvoř dovednosti jako VLASTNOST s konkrétním jménem: "
    "var dovednosti: Dictionary = {\"tezba\": 0, \"drevorubectvi\": 0, "
    "\"kovarstvi\": 0, \"boj_na_blizko\": 0} (všechny začínají na 0). "
    "Přidej funkce add(skill: String, n: int) -> void (zvýší hodnotu, omezeno "
    "na 0–100) a hodnota(skill: String) -> int (vrátí hodnotu). "
    "DŮLEŽITÉ – JAK SE DOVEDNOSTI ČTOU: testy je čtou takto: var sk = "
    "load(\"res://scripts/skills.gd\").new() a pak sk.get(\"tezba\"). "
    "get() je metoda ENGINU (Object.get), která vrátí hodnotu vlastnosti podle "
    "jména – proto NEDEFINUJ žádnou vlastní funkci get() (kolidovala by "
    "s enginem a musela by sama řešit, co je klíč a co slovník; naměřeno "
    "30. 9. 2026: model ji definoval a vracela null). Když skript vlastní get() "
    "nemá, sk.get(\"tezba\") vrátí hodnotu vlastnosti. Klíče drž přesně: tezba, "
    "drevorubectvi, kovarstvi, boj_na_blizko. Struktura souboru: začni "
    "extends Node, žádné class_name, _init() bez povinného argumentu "
    "(CONVENTIONS.md §1f a §1g). Nic dalšího neměň."
)


def main() -> int:
    if not CESTA.exists():
        print(f"CHYBA: roadmapa nenalezena: {CESTA}")
        return 1
    text = CESTA.read_text(encoding="utf-8")
    data = json.loads(text)

    stary = None
    for g in data["grains"]:
        if g.get("id") == "core.skills":
            stary = g.get("prompt")
            break
    if stary is None:
        print("CHYBA: granule core.skills v roadmapě není.")
        return 1
    if "NEDEFINUJ žádnou vlastní funkci" in stary:
        print("Zadání už je zpřesněné – nic se nemění.")
        return 0

    stary_json = json.dumps(stary, ensure_ascii=False)
    novy_json = json.dumps(NOVY, ensure_ascii=False)
    if stary_json not in text:
        print("CHYBA: přesný text starého promptu v souboru nenalezen.")
        print("(prvních 120 znaků hledaného:", repr(stary_json[:120]), ")")
        return 1

    CESTA.write_text(text.replace(stary_json, novy_json, 1), encoding="utf-8")
    print("Prompt core.skills vyměněn (jen hodnota, formátování zůstalo).")
    print("  stará délka:", len(stary), "| nová délka:", len(NOVY))
    return 0


if __name__ == "__main__":
    sys.exit(main())

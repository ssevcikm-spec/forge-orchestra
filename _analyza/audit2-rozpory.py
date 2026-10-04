# -*- coding: utf-8 -*-
"""AUDIT 2 — ROZPORY: kde dva dokumenty tvrdí totéž jinak.

Zadání (plán, fáze 2 — „nejcennější fáze"):
  najít místa, kde **dva dokumenty tvrdí totéž jinak**, nebo kde dokument
  tvrdí něco, co **kód nepodporuje**. Každý rozpor musí mít
  **číslo řádku v obou dokumentech**, verdikt a důvod.

CO SKRIPT DĚLÁ:
  1. Vytáhne z dokumentů VŠECHNA tvrzení tvaru „<číslo> <veličina>"
     (kontrol, omylů, nálezů, bran, skillů, …) i s číslem řádku a okolím.
  2. Seskupí je podle veličiny.
  3. U veličin s VÍC NEŽ JEDNOU hodnotou vypíše všechny výskyty vedle sebe —
     to je pracovní seznam rozporů k rozhodnutí.

⚠ CO SKRIPT NEUMÍ (a je to vidět ve výstupu, ne zamlčené):
  * **Nerozliší tvrzení od CITACE.** Věta „AGENTS.md tvrdil „32 sloupců"" je
    citace STARÉ chyby, ne tvrzení o dnešku. Skript to zkusí odhadnout podle
    slov v okolí (tvrdil / dřív / bylo / opraveno) a označí to `[citace?]` —
    je to HEURISTIKA, ne měření. Rozhodnout to musí člověk.
  * **Nezná zdroj.** Číslo srovnává s jinými čísly v dokumentech, ne s kódem.
    Kde zdroj znám (schema.sql), měří ho `audit2a-schema.py`.

Použití:  python _analyza/audit2-rozpory.py [--json _analyza/audit2-rozpory.json]
Návrat:   0 = žádná veličina nemá víc hodnot | 1 = jsou tam rozpory k rozhodnutí
"""

import json
import pathlib
import re
import sys
from collections import defaultdict

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
SKILLS = pathlib.Path.home() / ".dsh" / "skills"

# Veličiny, které se v dokumentaci opakují a na kterých záleží.
# (klíč, vzor, co to je)
VELICINY = [
    ("kontrol",   r"(\d+)\s+kontrol",            "počet kontrol v bráně"),
    ("omylů",     r"(\d+)\s+omyl",               "počet omylů v kronice"),
    ("nálezů",    r"(\d+)\s+nález",              "počet nálezů"),
    ("bran",      r"(\d+)\s+bran",               "počet bran"),
    ("skillů",    r"(\d+)\s+skill",              "počet skillů"),
    ("dokumentů", r"(\d+)\s+dokument",           "počet dokumentů"),
    ("granulí",   r"(\d+)\s+granul",             "počet granulí"),
    ("sloupců",   r"(\d+)\s+sloupc",             "počet sloupců schématu"),
    ("bodů",      r"(\d+)\s+bod",                "počet bodů"),
    ("souborů",   r"(\d+)\s+soubor",             "počet souborů"),
    ("testů",     r"(\d+)\s+test",               "počet testů"),
    ("tabul",     r"(\d+)\s+tabul",              "počet tabulek"),
    ("úloh",      r"(\d+)\s+úloh",               "počet úloh"),
    ("řádků",     r"(\d+)\s+řád",                "počet řádků"),
    ("znaků",     r"(\d[\d\u00a0 ]{0,9}\d|\d+)\s+znak", "počet znaků"),
]

# Heuristika „tohle je citace minulosti, ne tvrzení o dnešku".
CITACE = re.compile(
    r"tvrdil|tvrdí|dřív|dř[íi]ve|bylo|býval|opraveno|histor|naměřeno\s+\d|"
    r"místo|než\s|chybn|zastaral|SNAPSHOT|před\s", re.I)


def dokumenty():
    out = []
    for f in sorted(WS.glob("*.md")):
        out.append(f)
    for f in sorted((WS / "_analyza").glob("*.md")):
        out.append(f)
    for f in sorted(SKILLS.glob("*/SKILL.md")):
        out.append(f)
    return [f for f in out if f.name != pathlib.Path(__file__).name]


def main() -> int:
    argv = sys.argv[1:]
    json_cesta = WS / "_analyza" / "audit2-rozpory.json"
    if "--json" in argv:
        json_cesta = pathlib.Path(argv[argv.index("--json") + 1])

    vyskyt = defaultdict(list)
    for f in dokumenty():
        try:
            s = f.read_text(encoding="utf-8")
        except (UnicodeDecodeError, OSError):
            continue
        for klic, vzor, _ in VELICINY:
            for m in re.finditer(vzor, s):
                cislo = m.group(1).replace("\u00a0", "").replace(" ", "")
                try:
                    hodnota = int(cislo)
                except ValueError:
                    continue
                radek = s[:m.start()].count("\n") + 1
                okoli = s[max(0, m.start() - 120):m.end() + 60].replace("\n", " ")
                vyskyt[klic].append({
                    "hodnota": hodnota,
                    "soubor": str(f.relative_to(WS)) if WS in f.parents else f.name,
                    "radek": radek,
                    "citace": bool(CITACE.search(okoli)),
                    "okoli": re.sub(r"\s+", " ", okoli).strip()[:150],
                })

    print("=" * 100)
    print("AUDIT 2 — ROZPORY: táž veličina, různé hodnoty")
    print("=" * 100)
    print("  dokumentů prohledáno: %d" % len(dokumenty()))
    print()

    rozpory = []
    for klic, _, popis in VELICINY:
        v = vyskyt.get(klic, [])
        if not v:
            continue
        hodnoty = sorted({x["hodnota"] for x in v})
        if len(hodnoty) < 2:
            print("  OK    %-12s jediná hodnota: %s  (%d výskytů)"
                  % (klic, hodnoty[0], len(v)))
            continue
        # Rozpor je jen tam, kde je víc hodnot v NECITACNÍM kontextu.
        necite = sorted({x["hodnota"] for x in v if not x["citace"]})
        je_rozpor = len(necite) > 1
        if je_rozpor:
            rozpory.append((klic, popis, necite))
        print()
        print("  %s %-12s hodnoty: %s   (necitovaných: %s)  — %s"
              % ("ROZPOR" if je_rozpor else "MOŽNÁ ", klic,
                 ", ".join(map(str, hodnoty)),
                 ", ".join(map(str, necite)) or "—", popis))
        for x in sorted(v, key=lambda y: (y["hodnota"], y["soubor"])):
            print("      %6d  %-46s :%-5d %s"
                  % (x["hodnota"], x["soubor"][:46], x["radek"],
                     "[citace?]" if x["citace"] else "          "))

    print()
    print("=" * 100)
    print("  ROZPORY K ROZHODNUTÍ: %d veličin" % len(rozpory))
    print("=" * 100)
    for klic, popis, hodnoty in rozpory:
        print("  %-12s %s   ← %s" % (klic, ", ".join(map(str, hodnoty)), popis))

    json_cesta.write_text(json.dumps({
        "veliciny": {k: v for k, v in vyskyt.items()},
        "rozpory": [{"velicina": k, "popis": p, "hodnoty": h} for k, p, h in rozpory],
    }, ensure_ascii=False, indent=2), encoding="utf-8")
    print()
    print("  JSON: %s" % json_cesta)
    return 1 if rozpory else 0


if __name__ == "__main__":
    sys.exit(main())

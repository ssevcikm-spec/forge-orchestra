#!/usr/bin/env python
r"""Mutační test skeneru `hl-neanglicky-v-kodu.py` — měří SKENER, ne kód.

PROČ TO EXISTUJE (AGENTS.md): „Napsal jsi test? Vrať do kódu vadu a podívej se,
že spadne. Mutační test je jediný důkaz, že test měří."

Skener nad repem může vrátit „0 rizikových nálezů" ze DVOU důvodů:
  a) v kódu fakt žádné nejsou, nebo
  b) skener je slepý (neumí ten formát, rozsype se na uvozovkách…).
Bez mutačního testu ty dva případy nerozeznám. Proto se tu skeneru podstrčí
VZORKY, u kterých předem vím, co má najít a co ne.

Použití:
    python _analyza\test-neanglicky-skener.py
Návratový kód: 0 = všechny případy sedí, 1 = skener je slepý někde, kde být nemá.
"""
from __future__ import annotations

import importlib.util
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

SKENER = pathlib.Path(__file__).with_name("hl-neanglicky-v-kodu.py")
spec = importlib.util.spec_from_file_location("skener", SKENER)
sk = importlib.util.module_from_spec(spec)
# skener má na konci `sys.exit(0)` pro --json; při importu by ukončil test.
# Načteme ho proto bez spuštění hlavní smyčky: přečteme a odstřihneme ji.
zdroj = SKENER.read_text(encoding="utf-8")
odriznuto = zdroj.split("# ─────────────────────────────── hlavní smyčka")[0]
modul = {"__file__": str(SKENER), "__name__": "skener"}
exec(compile(odriznuto, str(SKENER), "exec"), modul)

python_nalezy = modul["python_nalezy"]
js_nalezy = modul["js_nalezy"]
json_nalezy = modul["json_nalezy"]
yaml_nalezy = modul["yaml_nalezy"]

kontrol = 0
chyb = 0


def test(nazev: str, podminka: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    if not podminka:
        chyb += 1
    print(f"  {'OK  ' if podminka else 'CHYBA'} {nazev}" + (f"  — {detail}" if detail else ""))


def kontexty(nalezy: list[dict]) -> list[str]:
    return [n["kontext"] for n in nalezy]


print("=== 1. SABOTÉŘ: známé VADY, které skener MUSÍ najít ===")

# 1a) literál v porovnání = rozhraní, které musí volající uhodnout (nález z assist.gd)
kod = '''
extends Node
func evaluate(player):
    if rule.trigger == "cíl mrtev":
        return true
'''
n, chyba = js_nalezy(kod, "test.gd", "gdscript")
test("GDScript: porovnání s českým literálem", chyba is None and len(n) >= 1,
     f"nálezů={len(n)}, chyba={chyba}")

# 1b) český IDENTIFIKÁTOR v Pythonu
kod = 'def f():\n    ohlášeno = 0\n    return ohlášeno\n'
n, _ = python_nalezy(kod, "test.py")
test("Python: český identifikátor (jméno proměnné)",
     any("IDENTIFIKÁTOR" in c for c in kontexty(n)), f"kontexty={kontexty(n)}")

# 1c) český identifikátor v TypeScriptu (let ohlášeno = 0) — PŘESNĚ případ z conductoru
# POZOR: `ohlaseno` (bez diakritiky) NENÍ nález — je to ASCII. Test to hlídá taky.
kod = 'function f() {\n  let ohlášeno = 0;\n  return ohlášeno;\n}\n'
n, _ = js_nalezy(kod, "test.ts", "typescript")
test("TypeScript: český identifikátor `ohlášeno` se NAJDE",
     any("IDENTIFIKÁTOR" in c for c in kontexty(n)), f"kontexty={kontexty(n)}")

kod = 'function f() {\n  let ohlaseno = 0;\n  return ohlaseno;\n}\n'
n, _ = js_nalezy(kod, "test.ts", "typescript")
test("TypeScript: ASCII `ohlaseno` NENÍ nález", len(n) == 0, f"nálezů={len(n)} (má být 0)")

# 1d) český KLÍČ v datech (JSON)
kod = '{"kategorie": {"název": "Železný meč"}}'
n, chyba = json_nalezy(kod, "test.json")
test("JSON: český klíč v datech", chyba is None and any("KLÍČ" in c for c in kontexty(n)),
     f"kontexty={kontexty(n)}")

# 1e) česká HODNOTA v YAML (název kroku CI) — vidí ji člověk v logu
kod = 'jobs:\n  build:\n    steps:\n      - name: Kontrola schématu\n        run: echo hi\n'
n, chyba = yaml_nalezy(kod, "test.yml")
test("YAML: česká hodnota (název kroku) se najde", chyba is None and len(n) >= 1,
     f"nálezů={len(n)}, chyba={chyba}")

# 1f) český KLÍČ v YAML by byl identifikátor — ať to skener umí rozlišit.
# ⚠ POZOR NA VZOREK: „kroky“ je ČISTĚ ASCII (k,r,o,k,y) — kdyby tu stálo, test
# by hlásil chybu skeneru, ale chyba by byla ve VZORKU. Přesně to se stalo
# (naměřeno 1. 10. 2026, třetí omyl téhož druhu). Klíč musí mít diakritiku.
kod = 'jobs:\n  build:\n    fáze:\n      - run: echo hi\n'
n, chyba = yaml_nalezy(kod, "test.yml")
test("YAML: český KLÍČ se najde jako KLÍČ",
     chyba is None and any("KLÍČ" in c for c in kontexty(n)), f"kontexty={kontexty(n)}")

# 1g) a pro jistotu opak: ASCII klíč, který česky VYPADÁ, nález není
kod = 'jobs:\n  build:\n    kroky:\n      - run: echo hi\n'
n, chyba = yaml_nalezy(kod, "test.yml")
test("YAML: ASCII klíč „kroky“ NENÍ nález (čeština bez diakritiky není non-ASCII)",
     chyba is None and len(n) == 0, f"nálezů={len(n)} (má být 0)")

print()
print("=== 2. ZNÁMÝ SPRÁVNÝ PŘÍPAD: co skener NESMÍ hlásit ===")

# 2a) český KOMMENTÁŘ není nález (to byla vada mé první verze: 30 falešných nálezů)
kod = '// tohle je český komentář s diakritikou: ěščřžýáíé\nconst x = 1;\n'
n, _ = js_nalezy(kod, "test.ts", "typescript")
test("JS: český komentář NENÍ nález", len(n) == 0, f"nálezů={len(n)} (má být 0)")

kod = '# český komentář\nx = 1\n'
n, _ = python_nalezy(kod, "test.py")
test("Python: český komentář NENÍ nález", len(n) == 0, f"nálezů={len(n)} (má být 0)")

kod = 'jobs:\n  build:\n    # český komentář v YAML\n    runs-on: ubuntu-latest\n'
n, _ = yaml_nalezy(kod, "test.yml")
test("YAML: český komentář NENÍ nález (parser komentáře nevidí)", len(n) == 0,
     f"nálezů={len(n)} (má být 0)")

# 2b) čistě anglický kód
kod = 'export function compute(a, b) { return a + b; }'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: anglický kód → 0 nálezů", len(n) == 0, f"nálezů={len(n)}")

# 2c) diakritika v NÁZVU souboru se do obsahu neplete
kod = 'const path = "scripts/level.gd";'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: ASCII cesta → 0 nálezů", len(n) == 0, f"nálezů={len(n)}")

print()
print("=== 3. PASTI LEXERU (kde se láme naivní regex) ===")

# 3a) apostrof UVNITŘ české věty — naivní regex na uvozovky tady selže
kod = "console.log('vrátil jsem se');\nconst y = 'další';\n"
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: apostrof uvnitř české věty nerozsype lexer", len(n) == 2, f"nálezů={len(n)} (má být 2)")

# 3b) uvozovky uvnitř řetězce druhého typu
kod = 'const a = \'říká "ahoj"\';\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: uvozovky uvnitř řetězce", len(n) == 1, f"nálezů={len(n)} (má být 1)")

# 3c) escapovaná uvozovka
kod = 'const a = "říká \\"ahoj\\"";\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: escapovaná uvozovka", len(n) == 1, f"nálezů={len(n)} (má být 1)")

# 3d) víc řádků: číslo řádku musí sedět
kod = 'const a = 1;\nconst b = 2;\nconst c = "žluťoučký";\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: číslo řádku u nálezu sedí (3)", len(n) == 1 and n[0]["radek"] == 3,
     f"nálezy={[(x['radek'], x['text']) for x in n]}")

# 3e) ČESKÝ REGEX nesmí vypadat jako identifikátor.
# `tools/detail-behu.mjs:23` má /Kontroluji parsování|Agent nezměnil žádný/ —
# dokud se obsah regexu nepreskočil, skener hlásil 690 falešných identifikátorů.
kod = 'const vzor = /Kontroluji parsování|Agent nezměnil žádný/;\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
ident = [x for x in n if "IDENTIFIKÁTOR" in x["kontext"]]
test("JS: český REGEX není identifikátor", len(ident) == 0,
     f"identifikátorů={len(ident)} (má být 0), celkem nálezů={len(n)}")

# 3f) obsah šablony (backtick) taky není identifikátor
kod = 'const s = `Agent nezměnil žádný kód`;\nconst x = 1;\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
ident = [x for x in n if "IDENTIFIKÁTOR" in x["kontext"]]
test("JS: obsah šablony není identifikátor", len(ident) == 0,
     f"identifikátorů={len(ident)} (má být 0)")

# 3g) dělení (ne regex) nesmí spolknout zbytek souboru
kod = 'const pomer = a / b;\nconst jmeno = "příliš";\n'
n, _ = js_nalezy(kod, "test.mjs", "javascript")
test("JS: dělení `/` nerozbije lexer (nález po něm zůstane)", len(n) == 1,
     f"nálezů={len(n)} (má být 1)")

# 3h) REGEX PŘES NOVÝ ŘÁDEK v poli. Tohle je PŘIZNANÁ MEZ ručního lexeru:
# skutečný nástroj pro JS/TS je `_analyza/js-tokeny.mjs` (parser TypeScriptu).
# Ruční lexer se v nejednoznačném případě chová KONZERVATIVNĚ — radši nehlásí,
# než aby hlásil falešně (`AGENTS.md`: falešný poplach nutí opravovat správný kód).
kod = ('const vzory = [\n'
       '  /\\[test\\] (OK|FAIL)/,\n'
       '  /tvrdý limit|timeout/i,\n'
       '  /další český vzor/,\n'
       '  "skutečný řetězec s diakritikou",\n'
       '];\n')
n, _ = js_nalezy(kod, "test.mjs", "javascript")
ident = [x for x in n if "IDENTIFIKÁTOR" in x["kontext"]]
test("JS: regex v poli → ruční lexer NEHLÁSÍ identifikátory (konzervativně)",
     len(ident) == 0, f"identifikátorů={len(ident)}: {[x['text'] for x in ident]}")
test("JS: skutečný řetězec v tomtéž souboru se pořád najde", len(n) >= 1,
     f"nálezů={len(n)}")

print()
print("=== 4. PŘIZNANÁ MEZ: co skener NEUMÍ ===")
try:
    kod = 'const a = `šablona ${x} a český text`;\n'
    n, _ = js_nalezy(kod, "test.mjs", "javascript")
    test("JS: český text v šabloně (backtick) se najde", len(n) >= 1, f"nálezů={len(n)}")
except Exception as e:
    test("JS: český text v šabloně (backtick) se najde", False, f"spadl: {e}")

print()
print("─" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb")
if chyb:
    print("SKENER JE NĚKDE SLEPÝ — viz CHYBA výše. Neměřím s ním, dokud to nesedí.")
    sys.exit(1)
print("VŠE OK — skener nachází, co má, a nehlásí, co nemá.")
sys.exit(0)

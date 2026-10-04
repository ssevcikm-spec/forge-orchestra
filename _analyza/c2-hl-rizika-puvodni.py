#!/usr/bin/env python
r"""FINÁLNÍ seznam rizik z inventáře — s VYSVĚTLENÝM každým zařazením i vyřazením.

PROČ TO EXISTUJE (1. 10. 2026): inventář `hl-neanglicky-v-kodu.py` je záměrně
široký (chytí i to, co se ukáže jako falešný poplach), protože **vynechat
skutečný nález je horší než nahlásit falešný** — jenže pak se v 36 „rizicích"
ztratí těch 8 skutečných. Tenhle skript je **třetí krok**: vezme inventář
a ke každé kategorii řekne, jestli je to nález, nebo poplach, a **proč**.

Kritérium (z `AGENTS.md` § Jazyk):
    identifikátor / klíč / literál rozhraní = riziko
    text pro člověka, komentář, popis v datech = v pořádku

Použití:
    python _analyza\hl-rizika-jazyka.py
Návratový kód: 0 = seznam sedí s očekáváním, 1 = objevilo se něco nového
               (což je ZÁMĚR: nový nález se nesmí tiše přehlédnout).
"""
from __future__ import annotations

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
INVENTAR = WS / "_analyza" / "_inventar.json"

# ── ZNÁMÉ FALEŠNÉ POPLACHY: kontext popsal hrubý fallback, ne kód ──────────────
# Každý záznam: (soubor, důvod, proč to není nález)
POPLACHY = [
    ("orchestra/repo/.forge/baseline.py",
     "STROJOVĚ ČITELNÁ HODNOTA",
     "řetězce jako „schváleno a nezměněno“ jsou HLAŠKY pro člověka; "
     "klíč `stav` jen nese text — kód se podle textu nerozhoduje"),
    ("games/uo-shadows/.forge/baseline.py",
     "STROJOVĚ ČITELNÁ HODNOTA",
     "totéž (druhá kopie téhož souboru)"),
    ("orchestra/install-into-repo.ps1",
     "KLÍČ (jméno atributu)",
     "fallback chytá `:` v české větě (Write-Host \"Cíl: $Target\") — "
     "jsou to hlášky, ověřeno ručně u všech 7"),
    ("orchestra/tools/test-local.ps1",
     "KLÍČ (jméno atributu)",
     "totéž — komentáře a hlášky, ověřeno ručně u všech 4"),
    ("orchestra/conductor/schema.sql",
     "KLÍČ (jméno atributu)",
     "řádky začínají `--`, tedy SQL komentář; fallback `#` nezná"),
]

# ── SKUTEČNÉ NÁLEZY: co se má přejmenovat ─────────────────────────────────────
# POZOR: klíč je (soubor, text) a hodnota popis; KONTEXT se hlídá zvlášť níž,
# protože každý jazyk mu říká jinak (Python AST vs. parser TypeScriptu vs.
# fallback). Naměřeno 1. 10. 2026: dokud tu byl u `ohlášeno` kontext
# `IDENTIFIKÁTOR (deklarace jména)`, kontrola úplnosti hlásila „CHYBÍ" —
# a přitom pravda je `deklarace proměnné` (tak to pojmenovává js-tokeny.mjs).
# Byl to **třetí případ téhož omylu**: hledal jsem text, ale ptát se měl na data.
#
# ⚠ STAV 2. 10. 2026: **Z1–Z8 JSOU PROVEDENÉ** (A1–A4 také). Tenhle seznam byl
# původně „co ještě zbývá přejmenovat"; teď je z něj **záznam o provedené
# práci**. Prázdný `OCEKAVANE` je SPRÁVNÝ výsledek — každé jméno tu navíc by
# hlásilo „CHYBÍ" u nálezu, který už opravený je (a to je táž past, jakou
# popisuje komentář u `spec.json`: dvě místa pro tutéž věc).
# Původní obsah (10 míst) je v `PROVEDENE` níž — nemaže se, jen přesouvá.
OCEKAVANE = {}

# ── CO BYLO PŘEJMENOVÁNO (záznam, ne očekávání) ───────────────────────────────
# Drží se to proto, aby se dalo dohledat, CO se změnilo a na CO — a aby se
# omylem nevrátilo zpátky. Datum: 2. 10. 2026.
PROVEDENE = {
    ("orchestra/conductor/src/index.ts", "ohlášeno"):
        "Z1 → `notified` (3×: :247 deklarace, :278 výraz, :283 návrat)",
    ("orchestra/tools/test-eskalace.py", "ohlášeno"): "Z1 → `notified` (kopie logiky v testu)",
    ("orchestra/tools/pridej-eskalaci.py", "ohlášeno"): "Z1 → `notified` (patch, doslovná kopie)",
    ("orchestra/tools/analyza-modelu.mjs", "—"): "Z2 → rozhoduje se podle hodnoty, ne podle výplně",
    ("orchestra/repo/.forge/check-schema.py", "nesedí"): "Z4 → `mismatched` (šablona)",
    ("games/uo-shadows/.forge/check-schema.py", "nesedí"): "Z4 → `mismatched` (hra — DRUHÁ KOPIE)",
    ("games/uo-shadows/scripts/assist.gd", "cíl mrtev"): 'Z5 → "target dead" (literál rozhraní)',
    ("games/uo-shadows/tools/make_iso_tiles.py", "pás"): "Z6 → `strip` (nástroj hry)",
    ("orchestra/repo/.forge/vision.mjs", "vezmiPrepínac"): "Z7 → `readSwitch` (šablona)",
    ("games/uo-shadows/.forge/vision.mjs", "vezmiPrepínac"): "Z7 → `readSwitch` (hra — DRUHÁ KOPIE)",
    ("orchestra/tools/sjednot-sablonu.py", "Spusť agenta"):
        "Z8 → krok se hledá podle `env.FORGE_ATTEMPT`, ne podle českého názvu",
}


# Nálezy, které se ZÁMĚRNĚ nepřejmenovávají (nejsou identifikátor rozhraní).
NEPREJMENOVAT = {
    ("games/uo-shadows/assets/spec.json", "zmenšování"):
        "lidský popis stylu v datech; kód ho nečte (ověřeno: 0 čtenářů v kódu)",
}

if not INVENTAR.is_file():
    # MEZIPRODUKT SE GENERUJE SÁM. Naměřeno 1. 10. 2026 (test předání): po
    # smazání `_inventar.json` skript spadl s „chybí …" — a nová session by
    # musela hádat, co pustit prvního. Nástroj, který se dá spustit jen
    # v určitém pořadí, je pro předání past; má si vstupy obstarat sám.
    print(f"  (inventář {INVENTAR.name} chybí — generuji ho, může to chvíli trvat…)")
    import subprocess
    r = subprocess.run([sys.executable, str(WS / "_analyza" / "hl-neanglicky-v-kodu.py"),
                        "--json", str(INVENTAR)], cwd=str(WS))
    if r.returncode != 0 or not INVENTAR.is_file():
        raise SystemExit(f"CHYBA: inventář se nepodařilo vygenerovat (exit {r.returncode})")

# ⚠ JEDINÝ ZDROJ PRAVDY o tom, co je „rizikový kontext". Naměřeno 1. 10. 2026:
# tenhle skript měl VLASTNÍ seznam (`POROVNÁNÍ`, `IDENTIFIKÁTOR`…) a byl
# **case-sensitive**, kdežto skener má `porovnání` a `deklarace proměnné`.
# Výsledek: `ohlášeno` v jádře a `cíl mrtev` v rozhraní se do rizik vůbec
# nedostaly — a to jsou přesně dva nálezy, kvůli kterým se to celé měřilo.
# Dva seznamy téhož = pasti místo kontroly (tatáž třída jako S30).
_zdroj = (WS / "_analyza" / "hl-neanglicky-v-kodu.py").read_text(encoding="utf-8")
_i = _zdroj.find("RIZIKOVE = (")
_j = _zdroj.find("\n)", _i)
RIZ_KONTEXTY = tuple(re.findall(r'"([^"]+)"', _zdroj[_i:_j]))
if not RIZ_KONTEXTY:
    raise SystemExit("CHYBA: z hl-neanglicky-v-kodu.py se nepodařilo načíst RIZIKOVE")

data = json.loads(INVENTAR.read_text(encoding="utf-8"))
nalezy = data["nalezy"]

rizika = [x for x in nalezy if any(k in x["kontext"] for k in RIZ_KONTEXTY)]

poplach_keys = {(s, k) for s, k, _ in POPLACHY}
skutecne, poplachy = [], []
for x in rizika:
    if (x["soubor"], x["kontext"]) in poplach_keys:
        poplachy.append(x)
    else:
        skutecne.append(x)

# ── CO JEŠTĚ NENÍ NÁLEZ, I KDYŽ TO TAK KLASIFIKÁTOR NAZVAL ────────────────────
# `klíč objektu`, `návratová hodnota`, `deklarace proměnné` a `výraz` jsou
# v parseru TypeScriptu **široké kategorie**: chytí i `{ zprava: "hotovo" }`,
# text promptu pro vision a české hlášky. Naměřeno 1. 10. 2026: takhle se
# z 8 nálezů stalo 142 „rizik" — a v tom šumu by se skutečný nález ztratil.
#
# Kritérium, které to řeší (a je kontrolovatelné): u kontextů z parseru se
# **doptáme zdroje** — hledá se, jestli tam totéž jméno stojí jako deklarace
# (`let`/`const`/`function`/`class`), jako klíč objektu (`jméno:`) nebo jako
# vlastnost (`.jméno`). Když nic z toho, je to TEXT (hláška, prompt), ne jméno.
def je_identifikator_v_kodu(x: dict) -> bool:
    k = x["kontext"]
    if k.startswith("porovnání") or k == "POROVNÁNÍ" or k == "POROVNÁNÍ (case)":
        return True                      # podle textu se rozhoduje → nález
    if "IDENTIFIKÁTOR" in k or "STROJOVĚ" in k:
        return True
    soubor = WS / x["soubor"]
    if not soubor.is_file():
        return False
    try:
        zdroj = soubor.read_text(encoding="utf-8")
    except Exception:
        return False
    jmeno = re.escape(x["text"].strip())
    vzory = [
        rf"\b(?:let|const|var|function|def|class)\s+{jmeno}\b",
        rf"^\s*{jmeno}\s*:",
        rf"\.{jmeno}\b",
    ]
    return any(re.search(v, zdroj, re.M) for v in vzory)


# Zúžení: co zbylo po vyloučení známých poplachů, projde testem „je to JMÉNO?".
hlaseni = [x for x in skutecne if not je_identifikator_v_kodu(x)]
skutecne = [x for x in skutecne if je_identifikator_v_kodu(x)]

print("═" * 80)
print("FINÁLNÍ SEZNAM RIZIK — jazyk v kódu (1. 10. 2026)")
print("═" * 80)
print(f"  nálezů v inventáři:        {len(nalezy)}")
print(f"  z toho rizikové kontexty:  {len(rizika)}")
print(f"  ZNÁMÉ FALEŠNÉ POPLACHY:    {len(poplachy)}  (vysvětlené níž)")
print(f"  TEXTY A HLÁŠKY (ne jména): {len(hlaseni)}  (vysvětlené níž)")
print(f"  SKUTEČNÉ NÁLEZY:           {len(skutecne)}")
print()

print("── SKUTEČNÉ NÁLEZY (co má být ASCII) ────────────────────────────────────")
po_souboru: dict[str, list] = {}
for x in skutecne:
    po_souboru.setdefault(x["soubor"], []).append(x)
for s, v in sorted(po_souboru.items(), key=lambda kv: -len(kv[1])):
    print(f"\n  {s}  ({len(v)}×)")
    for x in v:
        print(f"     :{x['radek']}  [{x['kontext']}]  {x['text'][:70]}")

print()
print("── FALEŠNÉ POPLACHY (měření je vysvětluje, nic se nepřejmenovává) ────────")
for s, kontext, proc in POPLACHY:
    kolik = len([x for x in poplachy if x["soubor"] == s and x["kontext"] == kontext])
    print(f"\n  {s}  ({kolik}×)")
    print(f"     → {proc}")

print()
print("── TEXTY A HLÁŠKY, KTERÉ SE NEPŘEJMENOVÁVAJÍ ────────────────────────────")
print("   (klasifikátor je nazval „klíč objektu“ / „výraz“, ale ve zdroji to")
print("    není jméno — je to hláška pro člověka nebo text promptu)")
po_souboru_h: dict[str, int] = {}
for x in hlaseni:
    po_souboru_h[x["soubor"]] = po_souboru_h.get(x["soubor"], 0) + 1
for s, c in sorted(po_souboru_h.items(), key=lambda kv: -kv[1])[:15]:
    print(f"   {c:4d}x  {s}")
if len(po_souboru_h) > 15:
    print(f"   … a dalších {len(po_souboru_h) - 15} souborů")

print()
print("─" * 80)
# KONTROLA ÚPLNOSTI: každé očekávané místo musí v seznamu být.
# Shoda je podle PODŘETĚZCE, protože u JSONu je text cesta („$.styl → klíč …").
def je_v_seznamu(soubor: str, text: str) -> bool:
    return any(x["soubor"] == soubor and text in x["text"] for x in skutecne)

chybi = [f"{s} :: {t}  ({p})" for (s, t), p in OCEKAVANE.items() if not je_v_seznamu(s, t)]

# A naopak: co je v datech a není v očekávání = NOVÝ nález, který má být vidět.
neocekavane = [x for x in skutecne
               if not any(x["soubor"] == s and t in x["text"] for (s, t) in OCEKAVANE)]

print(f"  očekávaných míst: {len(OCEKAVANE)}, nalezeno: {len(OCEKAVANE) - len(chybi)}")

# ZÁZNAM O PROVEDENÉM (2. 10. 2026): každé přejmenované místo se ověří tak,
# že v datech UŽ NENÍ. Kdyby se některé vrátilo (např. patch vrátí `ohlášeno`),
# je to vidět tady — a to je jediná obrana proti tichému návratu češtiny.
vratilo_se = [f"{s} :: {t}  (bylo: {p})" for (s, t), p in PROVEDENE.items()
              if je_v_seznamu(s, t)]
print(f"  PŘEJEDNANÝCH MÍST: {len(PROVEDENE)}, z toho VRÁCENÝCH: {len(vratilo_se)}")
if vratilo_se:
    print("  ⚠ VRÁTILO SE (mělo být přejmenováno, ale je zpátky v datech):")
    for v in vratilo_se:
        print(f"     - {v}")

if chybi:
    print("  CHYBÍ (bylo očekáváno, není v datech):")
    for c in chybi:
        print(f"     - {c}")
if neocekavane:
    print(f"  NOVÉ / NEZAŘAZENÉ ({len(neocekavane)}) — projdi je, ať nic neuteče:")
    for x in neocekavane:
        print(f"     - {x['soubor']}:{x['radek']}  [{x['kontext']}]  {x['text'][:70]}")

print()
print("── CO SE ZÁMĚRNĚ NEPŘEJMENOVÁVÁ ─────────────────────────────────────────")
for (s, t), proc in NEPREJMENOVAT.items():
    print(f"  {s} :: {t}")
    print(f"     → {proc}")

if chybi or neocekavane or vratilo_se:
    print()
    print("SEZNAM NESEDÍ S OČEKÁVÁNÍM — to je signál, ne chyba. Projdi výpis výš.")
    sys.exit(1)

print()
print("SEZNAM SEDÍ: žádné očekávané místo nechybí, nic nového nepřibylo")
print("a žádné přejmenované místo se nevrátilo.")
sys.exit(0)

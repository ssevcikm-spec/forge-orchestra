"""Stav DAG: co je hotové, co je připravené, co blokují závislosti a model.

Odpovídá na otázku „dá se zlepšit úspěšnost" tím, že ukáže, kde přesně práce
stojí – a kolik granulí je odkázáno na úzký seznam strongModels.
"""

import json
import pathlib

ROADMAP = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\roadmap.json")
PROVIDERS = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\orchestra\repo\.forge\providers.json")

grains = json.loads(ROADMAP.read_text(encoding="utf-8"))["grains"]
prov = json.loads(PROVIDERS.read_text(encoding="utf-8"))["providers"]

silne = {p["name"]: p.get("strongModels", []) for p in prov if p.get("strongModels")}
slabe = [p["name"] for p in prov if not p.get("strongModels")]

hotove = {g["id"] for g in grains if g.get("done")}
print(f"Hotových granulí: {len(hotove)}/{len(grains)}  ->  {', '.join(sorted(hotove))}")
print()
print("Silné modely má:", ", ".join(f"{k} ({', '.join(v)})" for k, v in silne.items()))
print("BEZ silných modelů:", ", ".join(slabe) or "(žádný)")
print()

pripravene, blokovane, cekajici = [], [], []
for g in grains:
    if g.get("done"):
        continue
    chybi = [d for d in g.get("depends_on", []) if d not in hotove]
    if chybi:
        cekajici.append((g, chybi))
    else:
        pripravene.append(g)

print("=" * 78)
print(f"PŘIPRAVENÉ ({len(pripravene)}) – závislosti hotové, může se dispatchovat:")
for g in pripravene:
    model = g.get("model", "any")
    zdroje = ", ".join(silne) if model == "strong" else "všichni poskytovatelé"
    print(f"  {g['id']:<16} model={model:<7} size={str(g.get('size_lines','-')):<8} zdroje: {zdroje}")

print()
print(f"ČEKAJÍCÍ NA ZÁVISLOSTI ({len(cekajici)}) – teď se nedá dispatchovat:")
for g, chybi in cekajici:
    model = g.get("model", "any")
    print(f"  {g['id']:<16} model={model:<7} čeká na: {', '.join(chybi)}")

print()
strong_pripravene = [g for g in pripravene if g.get("model") == "strong"]
strong_cekajici = [g for g, _ in cekajici if g.get("model") == "strong"]
print(f"Z TOHO SILNÝCH: {len(strong_pripravene)} připravených, {len(strong_cekajici)} čekajících")
print(f"Silné granule mají k dispozici {len(silne)} poskytovatele; "
      f"když všichni tři vyčerpají kvótu, nemá je kdo zpracovat.")

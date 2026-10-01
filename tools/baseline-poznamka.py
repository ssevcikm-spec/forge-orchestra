"""Doplní do baseline.json poctivou poznámku: stav PŘEVZAT, čeká na kontrolu.

PROČ: `baseline.py init` zapíše `schvalil: clovek`, protože předpokládá, že ho
pustil člověk. Tady ho pustil agent a uživatel výslovně řekl „spusť init sám
s poznámkou ‚čeká na kontrolu'". Záznam to musí říkat nahlas – jinak by
v auditu vypadalo, že lidské schválení proběhlo, i když neproběhlo.

Použití: python orchestra/tools/baseline-poznamka.py
"""
from __future__ import annotations

import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

CESTA = pathlib.Path(
    r"C:\Users\Ssevc\Local-Deepseek\games\uo-shadows\.forge\vision\baseline.json")

POZNAMKA = ("PŘEVZATO AGENTEM 30. 9. 2026 – čeká na lidskou kontrolu. "
            "Sprity jsou ze schváleného milníku 1 (`assets/spec.json`, `_stav`), "
            "ale kontaktní arch ještě nikdo neprošel očima.")

d = json.loads(CESTA.read_text(encoding="utf-8-sig"))
polozky = d.get("polozky", {})
zmeneno = 0
for zaznam in polozky.values():
    if zaznam.get("schvalil") == "clovek":
        # `schvalil` se přepisuje na `agent-init`: tvrzení „schválil člověk"
        # by bylo nepravdivé a v auditu nebezpečné.
        zaznam["schvalil"] = "agent-init"
        zaznam["poznamka"] = POZNAMKA
        zmeneno += 1

d["_stav"] = POZNAMKA
d["_ceka_na_lgtm"] = True
CESTA.write_text(json.dumps(d, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

print(f"Zapsáno: {CESTA}")
print(f"  položek {len(polozky)}, přepsaných záznamů {zmeneno}")
print(f"  schvalil = agent-init, _ceka_na_lgtm = true")
print()
print("Až se na arch podíváš a bude to dobré, přepiš to na lidské schválení:")
print("  python .forge/baseline.py init   # (nebo `schval <slozka>` po úpravách)")

# -*- coding: utf-8 -*-
r"""P27 — SONDA: volá test tiku sedm endpointů, které dřív nevolal NIKDO?

PROČ TENHLE SOUBOR EXISTUJE (a proč je JEDNORÁZOVÁ)
--------------------------------------------------
Zadání P27 §1 tvrdilo, že `/health`, `/queue`, `/roadmap`, `/failed`, `/status`,
`/workers` a `/games` **nevolá žádný test** — a na tom stál celý Úkol B1.
To je tvrzení o KÓDU (statické) a musí se **změřit**, ne opsat. Tahle sonda
změří obojí: kolik VOLÁNÍ endpointu je v testu a kolik je k němu KONTROL
(prefix v `check(...)`).

Je to **jednorázová diagnostika**, ne brána: odpovídá na jednu otázku a ta je
odpovězená. Patří proto do `PRESKOCIT` dávky `p20-d-doklady.py`.

⚠ CO SONDA NEMĚŘÍ: že test endpoint volá **skutečný handler**. Statický počet
volání je slabý důkaz — ten pravý je **zarážka uvnitř handleru**
(`_analyza/p27-a-overeni.py` etapa A2: každá zarážka zapne kontroly svého
prefixu a kontrolní `A: /tick odpoví 200` zůstane zelená).

Použití: python _analyza/p27-sonda-endpointy.py
"""

import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
TEST = WS / "tools" / "test-tick-offline.mjs"

# prefix kontrol v testu ↔ cesta endpointu
ENDPOINTY = (("X", "/health"), ("Y", "/queue"), ("Z", "/roadmap"),
             ("AA", "/failed"), ("AB", "/status"), ("AC", "/workers"),
             ("AD", "/games"), ("N", "/poll"), ("O", "/claim"),
             ("P", "/heartbeat"), ("Q", "/tasks/cleanup"),
             ("R", "/roadmap/reset"), ("T", "/task"), ("U", "/game"),
             ("V", "/game/active"))

VOLANI = re.compile(r"(?:post|get)\(mod,\s*env,\s*'([^']+)'")

text = TEST.read_text(encoding="utf-8")
volani: dict[str, int] = {}
for cesta in VOLANI.findall(text):
    volani[cesta] = volani.get(cesta, 0) + 1

print("=" * 78)
print("P27 sonda — volá test tiku ty endpointy? (%s)" % TEST.name)
print("=" * 78)
print("  %-6s %-18s %8s %8s" % ("prefix", "endpoint", "volání", "kontroly"))
chybi = []
for pref, cesta in ENDPOINTY:
    pocet = volani.get(cesta, 0)
    kontroly = len(re.findall(r"check\(\s*'%s: " % re.escape(pref), text))
    print("  %-6s %-18s %8d %8d" % (pref, cesta, pocet, kontroly))
    if pocet == 0:
        chybi.append(cesta)
print()
print("  volání celkem (všechny endpointy): %d" % sum(volani.values()))
print("  endpointy BEZ volání: %s" % (chybi or "(žádné)"))
print("  endpointy bez kontroly: %s"
      % ([c for p, c in ENDPOINTY
          if not re.search(r"check\(\s*'%s: " % re.escape(p), text)] or "(žádné)"))
print()
print("VERDIKT: %s" % ("VŠECH 15 endpointů je voláno i kontrolováno"
                       if not chybi else
                       "BEZ TESTU zůstává: %s" % ", ".join(chybi)))
sys.exit(0)

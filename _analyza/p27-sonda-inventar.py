# -*- coding: utf-8 -*-
r"""P27 — SONDA: co je v otisku vstupů inventáře (a co v něm NENÍ)?

PROČ TENHLE SOUBOR EXISTUJE (a proč je JEDNORÁZOVÁ)
--------------------------------------------------
Nález P26/10 tvrdí tři věci, na kterých stojí pořadí „inventář → `g3` →
`validate-all`":
  1. otisk vstupů počítá **OBĚ repa** (`KOREN_REPA`), takže zápis do hry
     zneplatní inventář i orchestry;
  2. **doklad** `_analyza/*-vystup.txt` je z otisku **VYLOUČEN** (`ARTEFAKT_RE`);
  3. **jiný nový soubor** otisk změní, a brána pak hlásí pojmenovaný stav
     `INVENTÁŘ JE ZASTARALÝ` (ne ticho).

Sonda je **vypisuje** (jednorázová diagnostika), kdežto **měří** je
`_analyza/p27-a-overeni.py` etapa A7 — a to včetně negativní kontroly
(nad čerstvým inventářem se hlášení „JE ZASTARALÝ" objevit NESMÍ).

⚠ Sonda sama je soubor v `_analyza/`, který **otisk mění** — po jejím přidání
se inventář musí **přegenerovat** (`hl-neanglicky-v-kodu.py --json …`).

Použití: python _analyza/p27-sonda-inventar.py
"""

import json
import pathlib
import re
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
INVENTAR = WS / "_analyza" / "_inventar.json"
NEANGL = WS / "_analyza" / "hl-neanglicky-v-kodu.py"

if not INVENTAR.is_file():
    print("CHYBA: chybí %s" % INVENTAR)
    sys.exit(2)

d = json.loads(INVENTAR.read_text(encoding="utf-8-sig"))
ot = d.get("otisk_vstupu") or {}
print("=" * 78)
print("P27 sonda — otisk vstupů inventáře")
print("=" * 78)
print("  verze otisku:      %s" % ot.get("verze"))
print("  sha256:            %s" % ot.get("sha256"))
print("  souborů ve otisku: %s" % ot.get("souboru"))
# ⚠ VYPISUJEME JEN JMÉNA REP A POČTY, ne celý seznam souborů: ten má tisíce
# položek a jeho výpis zahltí konzoli (naměřeno 7. 10. 2026 v P27).
repa = ot.get("repozitare") or []
for r in repa:
    if isinstance(r, dict):
        jmeno = r.get("repo") or r.get("jmeno") or r.get("koren") or "?"
        pocet = len(r.get("soubory") or r.get("soubory") or [])
        print("  repo:              %-18s souborů: %s" % (jmeno, pocet))
    else:
        print("  repo:              %s" % (r,))
print("  vyloučených artefaktů: %s" % d.get("vyloucene_artefakty"))
print("  NEPOKRYTO:         %s" % (d.get("nepokryto") or "(nic)"))
print("  souborů zpracováno: %s" % d.get("souboru_zpracovano"))

# (1) obě repa
print()
print("  OTISK POČÍTÁ OBĚ REPA: %s" % (len(repa) == 2))
# (2) doklad `*-vystup.txt` je vyloučený
vzor = re.search(r"ARTEFAKT_RE = re\.compile\(\s*(.*?)\n\)", 
                 NEANGL.read_text(encoding="utf-8"), re.S)
vyloucen = "(vystup|zaloha|log)" in (vzor.group(1) if vzor else "")
print("  DOKLAD `*-vystup.txt` JE VYLOUČEN z otisku (vzor ARTEFAKT_RE): %s" % vyloucen)
print()
print("VERDIKT: sonda nic nemění — jen vypisuje. Měření (včetně negativní")
print("         kontroly) je v `_analyza/p27-a-overeni.py` etapa A7.")
sys.exit(0 if (len(repa) == 2 and vyloucen) else 1)

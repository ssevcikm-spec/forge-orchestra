# -*- coding: utf-8 -*-
"""P42: MUTAČNÍ DŮKAZ, že nová kontrola rozpočtové rotace v `priprava.test.mjs`
umí SPADNOUT. Bez toho by byla jen dalším tvrzením, které nemá jak selhat.

Měří se na ŠABLONĚ (`repo/.github/workflows/agent.yml`), protože brána
(`<FORGE>/node/priprava.test.mjs`) čte workflow právě z kořene šablony.

Dvě mutace:
  M-A: zruší rotaci v předběžné kontrole rozpočtu (`--next` zmizí z prvního
       výskytu) → první `--next` zůstane jen v rotaci po neúspěšném běhu,
       tedy ZA `TRIDA=REQUEST_TOO_LARGE` → kontrola to musí poznat.
  M-B: přejmenuje čítač smyčky `_pokus_rozpoctu` → kontrola „je to smyčka" musí
       spadnout (jinak měří jen přítomnost nějakého `--next` kdekoliv).

Soubor se vrací bajt na bajt (knihovna `_mutace` to hlídá sama).
"""
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / "_analyza"))
from _mutace import mutuj  # noqa: E402

WF = WS / "repo" / ".github" / "workflows" / "agent.yml"
BRANA = ["node", "repo/.forge/node/priprava.test.mjs"]

MUTACE = [
    ("M-A rotace v předběžném rozpočtu chybí",
     "if ! node .forge/pick-provider.mjs --next; then break; fi",
     "if false; then break; fi"),
    ("M-B smyčka rozpočtu přejmenovaná (kontrola na smyčku)",
     "_pokus_rozpoctu in 1 2 3 4",
     "_jina_smycka in 1 2 3 4"),
]

checks = 0
errors = 0


def spust():
    r = subprocess.run(BRANA, cwd=str(WS), capture_output=True, text=True,
                       encoding="utf-8", errors="replace")
    return r.returncode, (r.stdout or "") + (r.stderr or "")


kod, out = spust()
checks += 1
if kod != 0 or "55/55" not in out:
    errors += 1
    print(f"  CHYBA KONTROLA: nemutovaná brána není zelená (exit={kod})")
    print("        " + "\n        ".join(out.strip().splitlines()[-6:]))
else:
    print("  OK    KONTROLA: nemutovaná brána je zelená (55/55, exit 0)")

for nazev, stary, novy in MUTACE:
    try:
        with mutuj(WF, stary, novy) as m:
            kod, out = spust()
    except ValueError as e:
        checks += 1
        errors += 1
        print(f"  CHYBA {nazev}: mutace se neprovedla — {e}")
        continue
    spadla = kod != 0 and "CHYBA" in out
    checks += 1
    if not spadla:
        errors += 1
        print(f"  CHYBA {nazev} → brána NESPADLA (exit={kod})")
        print("        " + "\n        ".join(out.strip().splitlines()[-6:]))
    else:
        radek = [l for l in out.splitlines() if "P42" in l and "CHYBA" in l]
        print(f"  OK    {nazev} → brána SPADLA  ({radek[0].strip() if radek else 'CHYBA P42'})")
    checks += 1
    if m.hash_po_navratu != m.hash_pred:
        errors += 1
        print(f"  CHYBA {nazev}: soubor NEBYL vrácen bajt na bajt")
    else:
        print(f"  OK    {nazev} → soubor vracen bajt na bajt")

print(f"\nvrat: {len(MUTACE)}")
if errors:
    print(f"VYSLEDEK: {checks} kontrol, {errors} CHYB")
    sys.exit(1)
print(f"VYSLEDEK: {checks} kontrol, 0 chyb")

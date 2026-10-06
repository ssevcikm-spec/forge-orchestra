# -*- coding: utf-8 -*-
r"""P19 — důkaz, že rozšíření slovníku typů NEOSLABILO bránu kroniky.

CO SE ZMĚNILO: `kronika-kontrola.py` uměla typy `akční`/`plánovací`/`ověřovací`/
`analýza`; P19 přidala **`rozhodovací`** (session, jejímž obsahem je rozhodnutí
o nálezech — zadání i `HANDOFF` ji tak jmenují). **Brána, které se jen přidá
povolená hodnota, se snadno stane bránou, která nic nehlídá** — proto tenhle test:
řádek s **vymyšleným** typem musí pořád skončit rozchodem.

JAK: `KRONIKA-PROJEKTU.md` se **dočasně** zmutuje (typ řádku 33 se nahradí
nesmyslem) a **vrátí bajt na bajt** ve `finally` — s porovnáním SHA-256.
Použití: python _analyza/p19-kronika-typy.py
"""

import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
KRONIKA = WS / "KRONIKA-PROJEKTU.md"
BRANA = WS / "_analyza" / "kronika-kontrola.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def spust():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=600)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def pocet_bez_typu(vystup: str):
    m = re.search(r"bez typu \([^)]*\):\s*(\d+)", vystup)
    return int(m.group(1)) if m else None


print("=" * 78)
print("P19 — brána kroniky: přidání typu `rozhodovací` neoslabilo kontrolu")
print("=" * 78)

puvodni = KRONIKA.read_bytes()
sha_pred = hashlib.sha256(puvodni).hexdigest()
text = puvodni.decode("utf-8")
radek33 = next((l for l in text.splitlines() if l.startswith("| **33** |")), None)
zk(radek33 is not None, "v kronize je řádek 33 (P19)", (radek33 or "")[:60])
zk(radek33 is not None and "rozhodovací" in radek33,
   "řádek 33 má typ `rozhodovací`", "typ je v něm uvedený")

print("\n--- 1) zdravý stav: 0 řádků bez typu -------------------------------")
kod0, v0 = spust()
n0 = pocet_bez_typu(v0)
zk(kod0 == 0 and n0 == 0, "brána je zelená a `bez typu` je 0",
   f"exit={kod0}, bez_typu={n0}")

print("\n--- 2) MUTACE: typ nahrazen NESMYSLEM → musí to poznat --------------")
try:
    if radek33:
        # Nahraď JEN typ v tom jednom řádku (řádek je dlouhý, kotva je jistá).
        zmutovany = text.replace(radek33, radek33.replace("**rozhodovací**",
                                                          "**vymyslenytyp**", 1))
        zk(zmutovany != text, "mutace se SKUTEČNĚ provedla (text se změnil)",
           "řádek 33 má jiný typ")
        KRONIKA.write_bytes(zmutovany.encode("utf-8"))
        kod1, v1 = spust()
        n1 = pocet_bez_typu(v1)
        zk(n1 == 1, "brána hlásí PRÁVĚ 1 řádek bez typu", f"bez_typu={n1}")
        zk(kod1 == 1, "a skončí nenulově (rozchod)", f"exit={kod1}")
        zk("nemá uvedený typ" in v1, "důvod je pojmenovaný",
           "hledám 'nemá uvedený typ'")
finally:
    KRONIKA.write_bytes(puvodni)
    sha_po = hashlib.sha256(KRONIKA.read_bytes()).hexdigest()
    zk(sha_po == sha_pred, "kronika vrácena BAJT NA BAJT", f"{sha_po[:16]}…")

print("\n--- 3) po vrácení zelená ------------------------------------------")
kod2, v2 = spust()
zk(kod2 == 0 and pocet_bez_typu(v2) == 0, "brána je zase zelená",
   f"exit={kod2}, bez_typu={pocet_bez_typu(v2)}")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

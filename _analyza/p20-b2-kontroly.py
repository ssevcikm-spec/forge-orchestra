# -*- coding: utf-8 -*-
r"""P20 — Úkol B2: DŮKAZ PRO OPRAVU TICHÉ DÍRY V H79.

CO SE OPRAVILO (nález **H101**, naměřený P20): `h79-escape-sken.py` měl fallback
`utf-8` → `utf-8-sig`, a když selhal i ten, udělal **`continue`** — soubor tedy
**tiše vynechal**. Naměřeno: nečitelný `.py` v živém stromě → **H79 `exit 0`
a soubor ve výstupu VŮBEC NEBYL**, kdežto NA32 tentýž soubor vykázal
(`1 nepřečteno`) a skončil `exit 1`. Dvě brány, dva různé verdikty o témž stromě.

⚠ A DRUHÁ POLOVINA (taky naměřená): ten fallback **nemá co zachránit**.
`utf-8-sig` je striktní nadmnožina `utf-8` (BOM se v `utf-8` dekóduje na U+FEFF,
nepadá), takže každý soubor, který přečte `utf-8-sig`, přečte i `utf-8`.
Ověřeno na pěti vzorcích (ASCII, BOM, latin-1 bajt, neplatný 0xFF, české UTF-8):
**ani jeden případ, kde by fallback pomohl.** Je to „a zkus to ještě jednou".

CO SE ZMĚNILO: nečitelné soubory se **POČÍTAJÍ** a jsou **POJMENOVANÉ**;
`exit` se nemění (stejná konvence jako `_archiv`/`snapshot-*`/`*-scratch` —
doklad se neopravuje, ale NESMÍ být tichý). Nové pole jde **NA KONEC** souhrnu,
aby starší doklady (`p19-b2-kontroly-h79.py`) na tentýž řádek pořád sedly.

Použití: python _analyza/p20-b2-kontroly.py
"""

import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
HRA = WS.parent / "uo-shadows"
BRANA = WS / "_analyza" / "h79-escape-sken.py"
FIXTURA = HRA / "scripts" / "_p20_b2_necitelny.py"
GIT = str(WS / "tools" / "git.cmd")

# ⚠ Fixtura musí být NEPLATNÝ UTF-8 (0xE9 samo v UTF-8 znamená „následuje
# continuation byte"), ale jinak SYTAKTICKY SPRÁVNÝ Python — kdyby padala
# i syntaxe, měřili bychom něco jiného, než co zkoumáme.
BAJTY = b"# p20/b2 fixtura: latin-1 bajt\nX_BOD = 1  # \xe9\n"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def spust():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=900)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def souhrn(vystup: str) -> str:
    radky = [l for l in vystup.splitlines() if l.startswith("ZMĚŘENO")]
    return radky[-1] if radky else "(souhrn nenalezen)"


print("=" * 78)
print("P20/B2 — H79: nečitelné soubory už nejsou tiché")
print("=" * 78)

# ── 1) ZDRAVÝ stav: čítač musí být VYKÁZANÝ i v nule
rc0, v0 = spust()
s0 = souhrn(v0)
print(f"\n--- 1) zdravý strom ------------------------------------------------")
print(f"    exit={rc0}")
print(f"    {s0}")
zk(rc0 == 0, "zdravý strom → exit 0", f"exit={rc0}")
m0 = re.search(r"(\d+) nečitelných", s0)
zk(m0 is not None, "souhrn nese čítač nečitelných souborů")
zk(m0 and int(m0.group(1)) == 0, "ve zdravém stromě je nečitelných 0",
   f"naměřeno {m0.group(1) if m0 else '?'}")

# ── 2) ANI JEDEN nečitelný soubor nesmí zmizet
print("\n--- 2) nečitelný soubor v živém stromě -----------------------------")
FIXTURA.write_bytes(BAJTY)
zk(FIXTURA.read_bytes() == BAJTY, "fixtura je na disku (bajt na bajt)")
try:
    FIXTURA.read_text(encoding="utf-8")
    zk(False, "fixtura se NEDÁ přečíst jako utf-8")
except UnicodeDecodeError:
    zk(True, "fixtura se NEDÁ přečíst jako utf-8 (jinak by neměřila nic)")

rc1, v1 = spust()
s1 = souhrn(v1)
print(f"    exit={rc1}")
print(f"    {s1}")
for l in v1.splitlines():
    if "_p20_b2_necitelny" in l:
        print(f"    zmínka: {l.strip()[:150]}")
m1 = re.search(r"(\d+) nečitelných", s1)
zk(m1 is not None and int(m1.group(1)) == 1,
   "nečitelný soubor je v ČÍTAČI (dřív zmizel)",
   f"naměřeno {m1.group(1) if m1 else '?'}")
zk(FIXTURA.name in v1 or str(FIXTURA) in v1,
   "a je POJMENOVANÝ (aby se dal dohledat)", FIXTURA.name)

# ── 3) Zelený verdikt se NEMĚNÍ (doklad se neopravuje, jen se o něm ví)
zk(rc1 == 0, "exit zůstává 0 — nečitelný DOKLAD se neopravuje, ale nesmí být tichý",
   f"exit={rc1}")

# ── 4) ÚKLID a shoda s výchozím stavem
FIXTURA.unlink(missing_ok=True)
r = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                   capture_output=True, text=True, encoding="utf-8",
                   errors="replace", shell=True, timeout=120)
zk((r.stdout or "").strip() == "", "strom hry je po úklidu ČISTÝ",
   repr((r.stdout or "").strip()))
rc2, v2 = spust()
zk(rc2 == 0 and souhrn(v2) == s0, "stav je zpátky shodný s výchozím",
   f"{souhrn(v2)}")

# ── 5) STARŠÍ DOKLAD P19 musí na tentýž souhrn pořád sednout
# (nové pole je NA KONCI — kdyby se vložilo doprostřed, doklad by přestal měřit)
print("\n--- 5) starší doklad P19 na nový souhrn ---------------------------------")
VZOR_P19 = (r"ZMĚŘENO:\s*(?P<nalezu>\d+)\s*neplatných escape sekvencí ve "
            r"SKENOVANÝCH\s*(?P<zivych>\d+)\s*živých souborech"
            r".*?`snapshot-\*`\s*(?P<snap>\d+)/(?P<snapsek>\d+)"
            r".*?`\*-scratch`\s*(?P<scratch>\d+)/(?P<scrscratchsek>\d+)")
m = re.search(VZOR_P19, v2, re.S)
zk(m is not None, "vzor z `p19-b2-kontroly-h79.py` na novém souhrnu SEDÍ",
   "sonduju tentýž regex, jaký používá starší doklad")
if m:
    print(f"    {m.groupdict()}")
    zk(int(m.group("nalezu")) == 0 and int(m.group("zivych")) > 0,
       "a vydal SMYSLUPLNÁ čísla (ne nuly z nenašlého vzoru)")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

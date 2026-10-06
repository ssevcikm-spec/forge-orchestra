# -*- coding: utf-8 -*-
r"""P20 — Úkol B (část 2): má brána H79 TICHOU DÍRU v nečitelných souborech?

PODEZŘENÍ (odvozeno ze ČTENÍ kódu, proto se musí ZMĚŘIT): `h79-escape-sken.py`
má fallback `utf-8` → `utf-8-sig`, a když selže i ten, udělá **`continue`** —
tedy soubor **tiše vynechá**. Na rozdíl od `n32-kompilovatelnost.py`, který
nečitelné soubory **počítá** (`nectene`) a **končí nenulově**.

⚠ `utf-8-sig` je striktní nadbytek k `utf-8`: každý soubor, který přečte
`utf-8-sig`, přečte i `utf-8` (BOM se v `utf-8` dekóduje na U+FEFF, nepadá).
Fallback tedy **nikdy nepomůže** — chová se jen jako „a zkus to ještě jednou".
To je taky důvod, proč obě brány BOM hlásí: H79 se k němu vůbec nedostane.

MĚŘÍ SE:
  1. je `utf-8-sig` nadmnožina `utf-8`? (měřeno na kandidátských vzorcích)
  2. co udělá H79 nad souborem v ŽIVÉM stromě, který UTF-8 NENÍ (latin-1 bajt)
     — počítá ho, nebo ho tiše vynechá?
  3. co udělá NA32 nad TÍMŽ souborem? (má to být ve shodě, nebo aspoň vidět)

Fixtura se zakládá v živém stromě hry a HNEĎ se uklidí; `git status` se měří
před i po. Použití: python _analyza/p20-b2-necitelne.py
"""

import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
HRA = WS.parent / "uo-shadows"
GIT = str(WS / "tools" / "git.cmd")
NA32 = ANALYZA / "n32-kompilovatelnost.py"
H79 = ANALYZA / "h79-escape-sken.py"
FIXTURA = HRA / "scripts" / "_p20_necitelny_fixtura.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


def git_status() -> str:
    r = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                       capture_output=True, text=True, encoding="utf-8",
                       errors="replace", shell=True, timeout=120)
    return (r.stdout or "").strip()


def spust(skript: pathlib.Path):
    r = subprocess.run([sys.executable, "-B", str(skript)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=600)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


print("=" * 78)
print("P20/B2 — má H79 tichou díru v nečitelných souborech?")
print("=" * 78)

# ── 1) Je `utf-8-sig` striktní nadmnožina `utf-8`?
print("\n--- 1) čte `utf-8-sig` všechno, co přečte `utf-8`? -----------------")
vzorky = {
    "ASCII": b"x = 1\n",
    "BOM": b"\xef\xbb\xbfx = 1\n",
    "latin-1 bajt 0xE9": b"# k\xe9v\n",
    "neplatny UTF-8 0xFF": b"# \xff\n",
    "UTF-8 české": "# káv\n".encode("utf-8"),
}
for popis, bajty in vzorky.items():
    vys = {}
    for enc in ("utf-8", "utf-8-sig"):
        try:
            bajty.decode(enc)
            vys[enc] = "OK"
        except UnicodeDecodeError:
            vys[enc] = "SPADL"
    print(f"    {popis:22} utf-8={vys['utf-8']:6} utf-8-sig={vys['utf-8-sig']}")
    # `utf-8-sig` nesmí projít tam, kde `utf-8` spadl — jinak by fallback měl smysl.
    zk(not (vys["utf-8-sig"] == "OK" and vys["utf-8"] == "SPADL"),
       f"{popis}: `utf-8-sig` NENÍ nadmnožina (fallback tedy nemá co zachránit)")

# ── 2) Co udělají obě brány nad NEČITELNÝM souborem v živém stromě?
print("\n--- 2) nečitelný soubor v ŽIVÉM stromě hry --------------------------")
pred = git_status()
# 0xE9 = 'é' v latin-1; v UTF-8 je to neplatný bajt (sám o sobě).
FIXTURA.write_bytes(b"# p20 fixtura: latin-1 bajt\nx = 1  # \xe9\n")
zk(FIXTURA.read_bytes() == b"# p20 fixtura: latin-1 bajt\nx = 1  # \xe9\n",
   "fixtura je na disku s neplatným UTF-8 bajtem")
try:
    FIXTURA.read_text(encoding="utf-8")
    zk(False, "fixtura se NEDÁ přečíst jako utf-8 (jinak by neměřila nic)")
except UnicodeDecodeError:
    zk(True, "fixtura se NEDÁ přečíst jako utf-8 (to je to, co měříme)")

vysledky = {}
for nazev, skript in (("NA32", NA32), ("H79", H79)):
    kod, vystup = spust(skript)
    vysledky[nazev] = (kod, vystup)
    souhrn = [l for l in vystup.splitlines() if l.startswith("ZMĚŘENO")]
    zmin = [l for l in vystup.splitlines() if "_p20_necitelny_fixtura" in l]
    print(f"    {nazev}: exit={kod}")
    print(f"      {souhrn[-1] if souhrn else '(souhrn nenalezen)'}")
    for z in zmin:
        print(f"      zmínka: {z.strip()[:150]}")

FIXTURA.unlink(missing_ok=True)
po = git_status()
zk(not FIXTURA.exists(), "fixtura SMAZÁNA")
zk(pred == po, "`git status` hry je PŘED i PO stejný", f"pred={pred!r} po={po!r}")

# ── 3) Verdikt: je soubor VIDĚT ve výstupu, nebo zmizel?
print("\n--- 3) je nečitelný soubor VIDĚT? -----------------------------------")
n32_v = vysledky["NA32"][1]
h79_v = vysledky["H79"][1]
n32_vidi = "nepřečteno" in n32_v and not n32_v.split("nepřečteno")[-2].strip().endswith("0")
# Přesněji: přečti číslo z „N nepřečteno"
import re
m32 = re.search(r"(\d+) nepřečteno", n32_v)
pocet_n32 = int(m32.group(1)) if m32 else -1
print(f"    NA32 hlásí nepřečtených: {pocet_n32}")
zk(pocet_n32 == 1, "NA32 nečitelný soubor POČÍTÁ (a proto končí nenulově)",
   f"naměřeno {pocet_n32}")
zk(vysledky["NA32"][0] != 0, "NA32 kvůli němu končí NENULOVĚ",
   f"exit={vysledky['NA32'][0]}")

h79_vidi = "_p20_necitelny_fixtura" in h79_v
print(f"    H79 soubor zmiňuje: {h79_vidi}")
zk(h79_vidi,
   "⚠ H79 nečitelný soubor ZMIŇUJE — když ne, je to TICHÁ DÍRA (nález)",
   "když tu kontrola spadne, podezření z čtení kódu se POTVRDILO")

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

# -*- coding: utf-8 -*-
r"""P20 — Úkol A: DŮKAZ, ŽE `g3` UMÍ SPADNOUT I NA ČERVENÉ (a ne na očekávanou).

ZADÁNÍ: „Když zavedeš nový `sys.exit`, DOLOŽ, že umí spadnout. A dolož i opak:
že OČEKÁVANÝ nenulový exit `g3` NEshodí (jinak by brána padala po každém
commitu).“

CO SE ZAVEDLO (`OCEKAVANE_NENULOVE = {"zadání kontrola": 1}`):
  * deklarovaný nenulový exit  → `g3` ho pojmenuje jako očekávaný,
  * NEDEKLAROVANÝ nenulový     → `g3` → `exit 1`,
  * deklarovaný, ale dnes `0`  → poznámka, NE pád (zadání se neopravuje),
  * deklarace bez brány v `BRANY` (visutá) → `exit 1`.

JAK: ze ŽIVÉHO `g3-brany.py` se staví KOPIE s vlastními fixturami. Do kopie se
vkládá ABSOLUTNÍ root (jinak by se cesty odvodily z umístění kopie — omyl 191)
a `VYSTUP` se přesměruje, aby test nepřepsal živý `g3-brany-vystup.txt`.
Živý soubor se NEMUTUJE (kontroluje se hash před a po).

⚠ Omyl 193 (P19) se tu OPRAVUJE preventivně: vzory regexů se skládají
z RAW řetězců, kde je vidět, kolik zpětných lomítek opravdu vznikne — jinak
vznikne regex na LITERÁLNÍ lomítko, čítač se „nenajde“ a zdravá brána vypadá
jako brána bez čítače.

Použití: python _analyza/p20-a-kontroly.py
"""

import ast
import hashlib
import pathlib
import re
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
SCRATCH = ANALYZA / "p20-scratch"
FIX = SCRATCH / "a-fixtury"
HARNESS = SCRATCH / "p20-a-harness.py"

kontroly = []


def zk(ok: bool, popis: str, detail: str = "") -> None:
    kontroly.append((ok, popis, detail))
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))


print("=" * 78)
print("P20/A — soudí `g3` červené? (a padá jen za NEDEKLAROVANÉ?)")
print("=" * 78)

zdroj = G3.read_text(encoding="utf-8")
hash_pred = hashlib.sha256(G3.read_bytes()).hexdigest()
FIX.mkdir(parents=True, exist_ok=True)

# ── Fixtury: skutečné skripty. `exit` se NEPÍŠE do seznamu bran, ale do kódu
#    fixtury — kdyby se psal do seznamu, neměřil by se návratový kód brány.
(FIX / "a-zdrava.py").write_text(
    'print("VYSLEDEK: 3 kontrol, 0 chyb")\n', encoding="utf-8", newline="\n")
(FIX / "a-cervena.py").write_text(
    'print("VYSLEDEK: 3 kontrol, 1 chyb")\nraise SystemExit(1)\n',
    encoding="utf-8", newline="\n")
(FIX / "a-cervena2.py").write_text(
    'print("VYSLEDEK: 3 kontrol, 1 chyb")\nraise SystemExit(2)\n',
    encoding="utf-8", newline="\n")

m = re.search(r"^BRANY = \[.*?^\]\n", zdroj, re.M | re.S)
zk(m is not None, "v živém g3 se našel blok `BRANY`")


def postav(fixtury: str, deklarace: str = 'OCEKAVANE_NENULOVE = {}') -> str:
    h = zdroj[:m.start()] + fixtury + zdroj[m.end():]
    h = h.replace('VYSTUP = ANALYZA / "g3-brany-vystup.txt"',
                  'VYSTUP = ANALYZA / "p20-scratch" / "p20-a-harness-vystup.txt"')
    h = h.replace("WS = pathlib.Path(__file__).resolve().parent.parent",
                  f'WS = pathlib.Path(r"{WS}")')
    # ⚠ OMyl P20/4 (naměřeno tady): fixtury NAHRAZUJÍ celý blok `BRANY`, takže
    # v kopii není `zadání kontrola` — a deklarace `OCEKAVANE_NENULOVE`
    # s ním se stane VISUTOU. První běh testu proto hlásil `exit 1` i ve
    # ZDRAVÉM stavu: nespadl kvůli červené bráně, ale kvůli deklaraci.
    # (`exit 1` ze špatného důvodu — `overovani` §10.1.) Každý případ si proto
    # deklaraci nastavuje SÁM a základ je PRÁZDNÝ — jinak by test neměřil to,
    # co tvrdí, že měří.
    h = h.replace('OCEKAVANE_NENULOVE = {"zadání kontrola": 1}', deklarace)
    ast.parse(h)
    return h


def brana(popis: str, soubor: str) -> str:
    """Záznam brány pro KOPII `g3` (vzor je RAW — viz omyl 193 v docstringu)."""
    return (f'    ("{popis}", ["python", "<ANALYZA>/p20-scratch/a-fixtury/{soubor}"],\n'
            "     " + r'r"(\d+) kontrol"' + "),\n")


def spust(text: str) -> dict:
    HARNESS.write_text(text, encoding="utf-8", newline="\n")
    r = subprocess.run([sys.executable, "-B", str(HARNESS)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=900)
    return {"exit": r.returncode, "vystup": (r.stdout or "") + (r.stderr or "")}


# ── 1) ZDRAVÝ stav: jedna zelená brána → exit 0
print("\n--- 1) ZDRAVÝ stav (zelená brána) → exit 0 -----------------------")
h = postav("BRANY = [\n" + brana("A1: zdravá", "a-zdrava.py") + "]\n")
r = spust(h)
if r["exit"] != 0:
    # ⚠ Diagnostika se vypisuje VŽDY, když stav nesedí — „exit=1“ samo neřekne,
    # KTERÝ ze čtyř důvodů to způsobil (a to je přesně past `overovani` §10.1:
    # `exit 1` ze špatného důvodu vypadá jako správný nález).
    print("      --- výstup harnessu (exit=%d) ---" % r["exit"])
    for l in r["vystup"].splitlines()[-25:]:
        print("      " + l)
zk(r["exit"] == 0, "g3 → exit 0", f"exit={r['exit']}")
zk("žádný NEOČEKÁVANÝ nenulový exit" in r["vystup"],
   "výslovně řekne, že neočekávaný exit není", "hledám text ve VÝSLEDKU g3")

# ── 2) NEDEKLAROVANÁ červená → MUSÍ SPADNOUT (to je jádro NA23b)
print("\n--- 2) NEDEKLAROVANÁ červená brána → MUSÍ SPADNOUT ----------------")
h = postav("BRANY = [\n" + brana("A2: červená nedeklarovaná", "a-cervena.py") + "]\n")
# Kontrola, že v kopii NIC jiného nespadne: visutá deklarace by dala `exit 1`
# ze jiného důvodu a test by tvrdil něco, co nezměřil.
# ⚠ OMyl P20/5 (naměřeno tady): první verze hledala v TEXTU kopie řetězec
# `OCEKAVANE_NENULOVE = {}` — jenže ten je i v DEFINICI pomocné funkce
# (`deklarace: str = 'OCEKAVANE_NENULOVE = {}'`), takže kontrola hlásila chybu
# nad SPRÁVNĚ postavenou kopií. Statická kontrola textu se musí ptát na to,
# co má měřit — ne na řetězec, který se v souboru vyskytuje z jiného důvodu.
zk(('OCEKAVANE_NENULOVE = {"zadání kontrola": 1}' not in h)
   and ("OCEKAVANE_NENULOVE = {}" in h),
   "v kopii je deklarace PRÁZDNÁ (spadne se jen kvůli červené bráně)",
   "hledám PŘÍKAZOVÝ řádek, ne řetězec kdekoliv v souboru")
if not (("OCEKAVANE_NENULOVE = {}" in h)
        and ('OCEKAVANE_NENULOVE = {"zadání kontrola": 1}' not in h)):
    print("      --- řádky s `OCEKAVANE_NENULOVE` v kopii ---")
    for l in h.splitlines():
        if "OCEKAVANE_NENULOVE" in l:
            print("      " + repr(l))
r = spust(h)
zk(r["exit"] == 1, "g3 → exit 1 (nenulový exit mimo deklaraci)", f"exit={r['exit']}")
zk("NEOČEKÁVANÝ: A2" in r["vystup"], "bránu POJMENUJE jako neočekávanou",
   "hledám 'NEOČEKÁVANÝ: A2'")
zk("NENULOVÉ EXITY: 1" in r["vystup"] and "NEDEKLAROVANÝCH 1" in r["vystup"],
   "čítač rozliší deklarované a nedeklarované",
   "hledám 'NENULOVÉ EXITY: 1' a 'NEDEKLAROVANÝCH 1'")

# ── 3) TÁŽ červená, ale DEKLAROVANÁ → NESMÍ SPADNOUT (opak téhož)
print("\n--- 3) TÁŽ červená, ale DEKLAROVANÁ → exit 0 ---------------------")
h = postav("BRANY = [\n" + brana("A2: červená nedeklarovaná", "a-cervena.py") + "]\n",
           'OCEKAVANE_NENULOVE = {"A2: červená nedeklarovaná": 1}')
zk('OCEKAVANE_NENULOVE = {"A2' in h, "deklarace se v kopii SKUTEČNĚ změnila")
r = spust(h)
zk(r["exit"] == 0, "deklarovaný nenulový exit → exit 0 (g3 nepadá po commitu)",
   f"exit={r['exit']}")
zk("očekávaný:   A2" in r["vystup"], "a je VIDĚT, že je očekávaný",
   "hledám 'očekávaný:   A2'")
zk("NEDEKLAROVANÝCH 0" in r["vystup"], "nedeklarovaných je 0")

# ── 4) STEHNÉ JMÉNO, JINÝ KÓD → musí spadnout (proto je v deklaraci i KÓD)
print("\n--- 4) STEJNÉ jméno, JINÝ exit (2 místo 1) → MUSÍ SPADNOUT ---------")
h = postav("BRANY = [\n" + brana("A2: červená nedeklarovaná", "a-cervena2.py") + "]\n",
           'OCEKAVANE_NENULOVE = {"A2: červená nedeklarovaná": 1}')
r = spust(h)
zk(r["exit"] == 1, "g3 → exit 1: deklarace nese KÓD, ne jen jméno", f"exit={r['exit']}")
zk("NEOČEKÁVANÝ: A2" in r["vystup"], "rozdíl je pojmenovaný")

# ── 5) DEKLAROVÁNO, ALE DNES 0 → poznámka, NE pád
print("\n--- 5) deklarováno, ale dnes ZELENÁ → poznámka, ne pád -------------")
h = postav("BRANY = [\n" + brana("A1: zdravá", "a-zdrava.py") + "]\n",
           'OCEKAVANE_NENULOVE = {"A1: zdravá": 1}')
r = spust(h)
zk(r["exit"] == 0, "g3 → exit 0 (zadání se na dnešek neopravuje → nepadá)",
   f"exit={r['exit']}")
zk("už není potřeba: A1" in r["vystup"], "řekne to jako poznámku",
   "hledám 'už není potřeba: A1'")

# ── 6) VISUTÝ záznam (deklarace o bráně, která v BRANY není) → MUSÍ SPADNOUT
print("\n--- 6) VISUTÝ záznam v deklaraci → MUSÍ SPADNOUT -------------------")
h = postav("BRANY = [\n" + brana("A1: zdravá", "a-zdrava.py") + "]\n",
           'OCEKAVANE_NENULOVE = {"A1: zdravá": 1, "A9: nikdy nebyla": 1}')
r = spust(h)
zk(r["exit"] == 1, "g3 → exit 1: deklarace o bráně, která už není", f"exit={r['exit']}")
zk("VISUTÉ" in r["vystup"] and "A9" in r["vystup"],
   "visutý záznam je POJMENOVANÝ (jinak by tiše kryl jinou bránu)")

# ── 7) Červená BEZ ČÍTAČE zůstává stavem „běžela, ale nic nezměřila“
print("\n--- 7) živý g3 se NESMÍ změnit ------------------------------------")
hash_po = hashlib.sha256(G3.read_bytes()).hexdigest()
zk(hash_po == hash_pred, "živý `g3-brany.py` je bajt na bajt nezměněný", hash_po[:16])
HARNESS.unlink(missing_ok=True)

chyb = sum(1 for ok, _, _ in kontroly if not ok)
print("\n" + "=" * 78)
print(f"VÝSLEDEK: {len(kontroly)} kontrol, {chyb} chyb")
for ok, popis, d in kontroly:
    if not ok:
        print(f"   CHYBA {popis}  [{d}]")
print("=" * 78)
sys.exit(1 if chyb else 0)

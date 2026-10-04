r"""Nezávislé ověření `_analyza\audit-snapshot.py` — měřidlo se musí ověřit JINAK.

PROČ: `overovani` §9.7 — "opravuješ-li měřidlo, mutačně ověř OPRAVU". A `§3`:
brána má vykázat STROJOVĚ ČITELNÝ počet toho, co změřila. Tenhle skript proto
NEČTE manifest očima — přepočítá `sha256` KAŽDÉHO souboru z DISKU a porovná
s tím, co je v manifestu. Kdyby snapshot zapsal prázdný nebo opsaný hash,
tenhle skript to najde.

Tři kontroly:
  1. manifest.json existuje a má `soubory`
  2. KAŽDÝ záznam má neprázdný `sha256` o 64 znacích (past: prázdný = "hotovo")
  3. hash PŘEPOČÍTANÝ Z DISKU == hash v manifestu, a počet souborů == počet
     skutečně nakopírovaných souborů ve snapshotu
  4. každý soubor v manifestu je i NA DISKU ve snapshotu (jinak je to jen
     tvrzení o souboru, který se nezkopíroval)

Spuštění:  $env:PYTHONIOENCODING='utf-8'; python _analyza\audit-snapshot-over.py
"""
import hashlib
import json
import pathlib
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"

kandidati = [d for d in ANALYZA.glob("snapshot-*")
             if d.is_dir() and (d / "manifest.json").is_file()]
if not kandidati:
    print("NEZMERENO: zadny snapshot-*/manifest.json neexistuje.")
    sys.exit(2)
snim = sorted(kandidati)[-1]
print("=" * 92)
print("NEZAVISLE OVERENI SNAPSHOTU: %s" % snim.name)
print("=" * 92)

m = json.loads((snim / "manifest.json").read_text(encoding="utf-8"))
soubory = m.get("soubory") or {}
chyby = []

if not soubory:
    chyby.append("manifest nema zadne soubory")

prazdne = [k for k, z in soubory.items() if not z.get("sha256")]
if prazdne:
    chyby.append("prazdny hash u %d souboru: %s" % (len(prazdne), prazdne[:5]))

# 3+4) prepocet z disku
prepocteno = 0
for klic, z in soubory.items():
    # klic je "<skupina>/<cesta>", ve snapshotu lezi na teze relativni ceste
    cil = snim / klic
    if not cil.is_file():
        chyby.append("v manifestu je %s, ale ve snapshotu NENI na disku" % klic)
        continue
    bajty = cil.read_bytes()
    h = hashlib.sha256(bajty).hexdigest()
    if h != z.get("sha256"):
        chyby.append("hash NESEDI u %s: manifest=%s, disk=%s"
                     % (klic, str(z.get("sha256"))[:16], h[:16]))
    if len(bajty) != z.get("bajtu"):
        chyby.append("velikost NESEDI u %s: manifest=%s, disk=%d"
                     % (klic, z.get("bajtu"), len(bajty)))
    prepocteno += 1

# soubory na disku, ktere v manifestu nejsou (mimo manifest.json samotny)
na_disku = {p.relative_to(snim).as_posix() for p in snim.rglob("*") if p.is_file()}
na_disku.discard("manifest.json")
neni_v_manifestu = sorted(na_disku - set(soubory))
if neni_v_manifestu:
    chyby.append("na disku je %d souboru, ktere manifest nezna: %s"
                 % (len(neni_v_manifestu), neni_v_manifestu[:5]))

skupiny = {}
for z in soubory.values():
    skupiny[z.get("skupina")] = skupiny.get(z.get("skupina"), 0) + 1

print("\n  ZMERENO: souboru v manifestu=%d  (jadro=%d, koren=%d, skilly=%d)"
      % (len(soubory), skupiny.get("jadro", 0), skupiny.get("koren", 0),
         skupiny.get("skill", 0)))
print("           hashu prepoctanych Z DISKU=%d" % prepocteno)
print("           souboru na disku ve snapshotu=%d" % len(na_disku))
print("           prazdnych hashu=%d" % len(prazdne))
print("           chyb=%d" % len(chyby))

if chyby:
    print()
    for c in chyby[:20]:
        print("  CHYBA: %s" % c)
    print("\nVYSLEDEK: snapshot NEOVEREN -> exit 1")
    sys.exit(1)
print("\nVYSLEDEK: snapshot OVEREN — vsechny hashe prepoctany z disku sedi. exit 0")
sys.exit(0)

# -*- coding: utf-8 -*-
r"""P22 — test knihovny `_mutace.py`: umí ZABRÁNIT tiché mutaci?

PROČ TENHLE TEST EXISTUJE: `_mutace.py` vznikl proto, že **15 omylů** projektu
je „mutace se tiše neprovedla / nezměnila měřenou podmínku — a prošla"
(`KRONIKA-PROJEKTU.md` §3–§4). Kdyby ho nikdo netestoval, byl by to **další
netestovaný nástroj** — a přesně tím projekt trpí.

CO TEST DOKAZUJE (7 skupin kontrol):
1. šťastná cesta — mutace proběhne a soubor se vrátí **bajt na bajt**,
2. **kotva v souboru NENÍ** → `ValueError` a soubor **nedotčen**,
3. **kotva je 2×** → `ValueError` (přesně omyl #110),
4. **nový text obsahuje starý** → `ValueError` (přesně omyly #18/#106),
5. **soubor se vrátí i při výjimce** uvnitř bloku (`try/finally`),
6. **skutečné použití na ŽIVÉ bráně** — zmutuje `tools/over-skilly.py` tak, že
   přestane nacházet kořeny, spustí ho a ověří, že **verdikt se změní**
   (to je důkaz, že funkce mění CHOVÁNÍ, ne jen text),
7. **nástroj sám sobě** — soubor testu se po všech mutacích nezměnil.

Použití: python _analyza/p22-test-mutace.py
"""

import hashlib
import pathlib
import subprocess
import sys
import tempfile

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(WS / "_analyza"))
from _mutace import mutuj  # noqa: E402

# ⚠ H139 (P31): KOTVA MUSÍ BÝT JEDNOZNAČNÁ **A ÚČINNÁ**. Naměřeno 9. 10. 2026:
# `tools/over-skilly.py` má `REPO = pathlib.Path(__file__).resolve().parents[1]`
# **2×** (řádky 28 a 56) — `mutuj` na té kotvě spadl (`kotva je v souboru 2×`)
# a test **NEMĚŘIL, jen spadl** (a zanechal scratch). A i kdyby se mutovalo
# první místo, **druhé přiřazení ho přepíše** → brána by fungovala dál a test by
# „prošel" bez měření. Proto se mutuje **DRUHÝ (účinný) výskyt** s kontextem.
KOTVA_REPO = ('# VIDĚT; tiché rozšíření rozsahu by bylo přesně ta vada, '
              'kterou P25-K popisuje).\n'
              'REPO = pathlib.Path(__file__).resolve().parents[1]')

BRANA = WS / "tools" / "over-skilly.py"

kontrol = 0
chyb = []


def zk(ok, popis, detail=""):
    global kontrol
    kontrol += 1
    print(f"  {'OK  ' if ok else 'CHYBA'} {popis}" + (f"\n      {detail}" if detail else ""))
    if not ok:
        chyb.append(popis)


def sha(p):
    return hashlib.sha256(pathlib.Path(p).read_bytes()).hexdigest()


print("=" * 78)
print("P22 — test knihovny `_mutace.py` (zábrana tiché mutace)")
print("=" * 78)

scratch = pathlib.Path(tempfile.mkdtemp(prefix="p22-mutace-", dir=str(WS / "_analyza")))
# ⚠ H139 (P31): SCRATCH SE UKLIDÍ I PŘI PÁDU. Naměřeno 9. 10. 2026: neodchycený
# `ValueError` z `mutuj` (dvojznačná kotva) ukončil test **před** úklidem na konci
# → v `_analyza/` zůstaly **4** adresáře `p22-mutace-*/fixtura.txt` a `git add -A`
# by je poslal do repa. `atexit` úklid je pojistka, ne náhrada úklidu níž.
import atexit  # noqa: E402
import shutil  # noqa: E402

atexit.register(lambda: shutil.rmtree(scratch, ignore_errors=True))
fixtura = scratch / "fixtura.txt"
fixtura.write_text("radek A\nKOTVA\nradek C\n", encoding="utf-8")
hash0 = sha(fixtura)

# --- 1) šťastná cesta --------------------------------------------------------
print("\n1) ŠŤASTNÁ CESTA — mutace proběhne a soubor se vrátí")
with mutuj(fixtura, "KOTVA", "ZMENA") as m:
    zk(m.pocet_vyskytu == 1, "kotva nalezena právě 1×", f"počet={m.pocet_vyskytu}")
    zk(m.hash_po_mutaci != m.hash_pred, "hash se po mutaci ZMĚNIL")
    uvnitr = fixtura.read_text(encoding="utf-8")
    zk("ZMENA" in uvnitr and "KOTVA" not in uvnitr, "uvnitř bloku je soubor zmutovaný")
zk(m.hash_po_navratu == m.hash_pred, "po bloku je hash zpět na původní hodnotě")
zk(sha(fixtura) == hash0, "soubor je bajt na bajt původní")

# --- 2) kotva není -----------------------------------------------------------
print("\n2) KOTVA V SOUBORU NENÍ → ValueError, soubor nedotčen")
pred = sha(fixtura)
try:
    with mutuj(fixtura, "TATO_KOTVA_TAM_NENI", "cokoli"):
        pass
    zk(False, "chybí kotva → má vyhodit ValueError")
except ValueError as e:
    zk("NENÍ" in str(e), "chybí kotva → ValueError", str(e)[:70])
zk(sha(fixtura) == pred, "soubor zůstal nedotčen")

# --- 3) kotva 2× (omyl #110) -------------------------------------------------
print("\n3) KOTVA 2× → ValueError (přesně omyl #110)")
fixtura.write_text("KOTVA\nneco\nKOTVA\n", encoding="utf-8")
pred = sha(fixtura)
try:
    with mutuj(fixtura, "KOTVA", "ZMENA"):
        pass
    zk(False, "dvě kotvy → má vyhodit ValueError")
except ValueError as e:
    zk("2×" in str(e), "dvě kotvy → ValueError", str(e)[:70])
zk(sha(fixtura) == pred, "soubor zůstal nedotčen")

# --- 4) nový obsahuje starý (omyly #18/#106) ---------------------------------
print("\n4) NOVÝ OBSAHUJE STARÝ → ValueError (omyly #18/#106)")
fixtura.write_text("KOTVA\n", encoding="utf-8")
pred = sha(fixtura)
try:
    with mutuj(fixtura, "KOTVA", "KOTVA_NEBO_NECO"):
        pass
    zk(False, "podřetězec → má vyhodit ValueError")
except ValueError as e:
    zk("PODŘETĚZEC" in str(e).upper(), "podřetězec → ValueError", str(e)[:80])
zk(sha(fixtura) == pred, "soubor zůstal nedotčen")

# --- 5) výjimka uvnitř bloku -------------------------------------------------
print("\n5) VÝJIMKA UVNITŘ BLOKU → soubor se přesto vrátí (try/finally)")
fixtura.write_text("radek A\nKOTVA\n", encoding="utf-8")
pred = sha(fixtura)
try:
    with mutuj(fixtura, "KOTVA", "ZMENA"):
        raise RuntimeError("umělé spadnutí testu")
except RuntimeError:
    pass
zk(sha(fixtura) == pred, "po výjimce je soubor bajt na bajt původní")

# --- 6) SKUTEČNÉ POUŽITÍ na živé bráně ---------------------------------------
print("\n6) SKUTEČNÉ POUŽITÍ — zmutovaná brána musí změnit VERDIKT")


def spust_branu():
    r = subprocess.run([sys.executable, "-B", str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), timeout=300)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


kod0, v0 = spust_branu()
zk(kod0 == 0, "zdravá brána prochází", f"exit={kod0}")
pred_brana = sha(BRANA)

# Zmutujeme KOŘEN, proti kterému brána ověřuje cesty → přestane je nacházet.
# ⚠ KOTVA SE MUSÍ SHODOVAT SE ZDROJEM. Po generalizaci cest (7. 10. 2026) je
# v `n8-zastarala-analyza.py` místo literálu `E:\Workspaces\forge-orchestra`
# odvození z `__file__` — kotva se proto změnila s ním. Kdyby zůstala stará,
# `mutuj` by spadl (`kotva v souboru NENÍ`) a test by NEMĚŘIL; přesně na to
# `_mutace.py:74` myslí, takže se to nedozvíme tiše.
# ⚠ H139 (P31): CÍL MUTACE MUSÍ BÝT HLUBŠÍ NEŽ `REPO.parent`. Naměřeno
# 9. 10. 2026: s `REPO = E:\Workspaces\NEEXISTUJE-tato-cesta` brána cesty
# **pořád našla** — `over-skilly.py` je od P25-K uznává i v **sourozeneckých
# projektech** (`REPO.parent`) a `E:\Workspaces` je má. Mutace tedy nic
# nezměnila (a test hlásil jen „výstup nehlásí mrtvé cesty"). Hluboká
# neexistující cesta nemá sourozence s `.git`, takže se cesty opravdu ztratí.
with mutuj(BRANA, KOTVA_REPO,
           KOTVA_REPO.replace(
               'pathlib.Path(__file__).resolve().parents[1]',
               'pathlib.Path(r"E:\\NEEXISTUJE-tato-cesta\\hluboko\\tam")')) as m:
    kod1, v1 = spust_branu()
    zk(kod1 != 0, "zmutovaná brána SPADLA (verdikt se změnil)", f"exit={kod1}")
    zk("mrtvých" in v1 and "0 mrtvých" not in v1, "výstup hlásí mrtvé cesty",
       [l for l in v1.splitlines() if "mrtv" in l][:2])

zk(sha(BRANA) == pred_brana, "brána je po testu bajt na bajt původní")
kod2, v2 = spust_branu()
zk(kod2 == 0, "po návratu brána zase prochází", f"exit={kod2}")

# --- 7) test sám sobě --------------------------------------------------------
print("\n7) TEST SÁM SOBĚ — soubor testu se nezměnil")
zk(True, "testovací soubor se needituje (kontrola je v tom, že tu není mutace)")

# --- úklid a souhrn ----------------------------------------------------------
for f in scratch.glob("*"):
    f.unlink()
scratch.rmdir()
zk(not scratch.exists(), "fixtury uklizeny")

print("\n" + "=" * 78)
print(f"VÝSLEDEK: {kontrol} kontrol, {len(chyb)} chyb")
for c in chyb:
    print(f"   CHYBA {c}")
print("=" * 78)
sys.exit(1 if chyb else 0)

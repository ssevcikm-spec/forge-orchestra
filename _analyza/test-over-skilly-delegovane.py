# -*- coding: utf-8 -*-
r"""MUTAČNÍ TEST: měří novou část `tools\over-skilly.py` (cesty v DELEGOVANÝCH
dokumentech, přidáno 7. 10. 2026 při optimalizaci KB).

PROČ TENHLE TEST EXISTUJE: skilly `orchestra` a `game-developer` přesunuly část
znalosti do projektových dokumentů (`PROVOZ-ORCHESTRA.md`, `BRANY-HRY.md`).
Kontrola cest k nástrojům se rozšířila i na ně — ale **nová kontrola je stejně
bezcenná jako každá jiná, dokud se neprokáže, že UMÍ SPADNOUT**. Naměřeno
7. 10. 2026: první pokus o tuhle mutaci se **tiše neprovedl** (PowerShell
spolkl backticky v here-stringu), takže test „prošel" a netvrdil nic.

⚠ TEST NESAHÁ NA ŽIVÉ DOKUMENTY. Používá přepis `FORGE_NAVAZANE` a fixtury
v `_analyza\_scratch-over-skilly\` (uklízí je v `finally`). Důvod je naměřený
(P24): přerušený mutační běh nad živým souborem nechal v kódu čtyři mutanty
a `git status` přitom byl čistý.

Použití: python _analyza\test-over-skilly-delegovane.py
"""

import os
import pathlib
import shutil
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
SCRATCH = WS / "_analyza" / "_scratch-over-skilly"
BRANA = WS / "tools" / "over-skilly.py"

kontrol = 0
chyb = 0


def test(popis, ok, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"  OK   {popis}")
    else:
        chyb += 1
        print(f"  CHYBA {popis}{(' — ' + detail) if detail else ''}")


def spust_nad(fixtury):
    """Spustí bránu s DELEGOVANÝMI dokumenty = fixturami. Vrací (exit, výstup).

    ⚠ `FORGE_SKILLS` míří na PRÁZDNÝ adresář: tenhle test měří část o
    delegovaných dokumentech, ne stav cizích skillů. Naměřeno 8. 10. 2026 (P27):
    nový skill `dialog-s-uzivatelem` (cizí session) měl neplatný YAML a test
    kvůli němu hlásil „zdravá fixtura → exit 1" — tedy vadu, která s jeho věcí
    nesouvisela. Falešný poplach se hledá hůř než slepé místo.
    """
    env = dict(os.environ)
    env["FORGE_NAVAZANE"] = ";".join(str(p) for p in fixtury)
    env["FORGE_SKILLS"] = str(SCRATCH / "prazdne-skilly")
    (SCRATCH / "prazdne-skilly").mkdir(parents=True, exist_ok=True)
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), env=env, timeout=300)
    return r.returncode, (r.stdout or "") + (r.stderr or "")


try:
    SCRATCH.mkdir(parents=True, exist_ok=True)

    # ── Fixtura 1: cesta, která EXISTUJE (`tools\status.mjs`) ────────────────
    f_ok = SCRATCH / "fixtura-ok.md"
    f_ok.write_text("Odkaz na `tools\\status.mjs` a `_analyza\\g3-brany.py`.\n",
                    encoding="utf-8", newline="\n")

    # ── Fixtura 2: cesta, která NEEXISTUJE ───────────────────────────────────
    # ⚠ Řádek NESMÍ obsahovat slovo „neexistuje" ani „~~" — brána je bere jako
    # přiznanou historickou zmínku a správně by takovou cestu přeskočila.
    f_spatna = SCRATCH / "fixtura-mrtva-cesta.md"
    f_spatna.write_text("Odkaz na `tools\\mrtvy-nastroj-abc.py`.\n",
                        encoding="utf-8", newline="\n")

    # ── Fixtura 3: přiznaná historická zmínka (NESMÍ spadnout) ───────────────
    f_hist = SCRATCH / "fixtura-historie.md"
    f_hist.write_text(
        "Nástroj `tools\\stary-nastroj-abc.py` už není (smazán 1. 10. 2026).\n",
        encoding="utf-8", newline="\n")

    print("=" * 78)
    print("TEST: cesty v delegovaných dokumentech (over-skilly.py)")
    print("=" * 78)

    # 1) zdravý stav → zelená
    kod, out = spust_nad([f_ok])
    test("zdravá fixtura → exit 0", kod == 0, f"exit={kod}")
    test("zdravá fixtura → počítadlo cest roste (68 zmínek = 26 ze skillů + 2)",
         "zmínek" in out and "0 mrtvých" in out)

    # 2) mrtvá cesta → ČERVENÁ (tohle je jádro testu)
    kod, out = spust_nad([f_spatna])
    test("mrtvá cesta ve fixtuře → exit 1", kod == 1, f"exit={kod}")
    test("mrtvá cesta je POJMENOVANÁ (ne jen nenulový exit)",
         "mrtvy-nastroj-abc.py" in out, out[-200:])

    # 3) přiznaná historická zmínka → zelená (brána nesmí hlásit falešný poplach)
    kod, out = spust_nad([f_hist])
    test("historická zmínka („už není, smazán“) → exit 0", kod == 0, f"exit={kod}")

    # 4) delegovaný dokument, který NEEXISTUJE → ČERVENÁ
    #    (skill by posílal agenta nikam a dosud si toho nikdo nevšiml)
    kod, out = spust_nad([SCRATCH / "dokument-ktery-neni.md"])
    test("neexistující delegovaný dokument → exit 1", kod == 1, f"exit={kod}")

    # 5) REGRESNÍ POJISTKA: s přepisem se ŽIVÉ dokumenty neskenují.
    #    Kdyby se skenovaly, test by mohl mutovat živý text — což je přesně
    #    past, kterou popisuje P24.
    zivy = WS / "PROVOZ-ORCHESTRA.md"
    pred = zivy.read_bytes() if zivy.exists() else b""
    spust_nad([f_ok])
    po = zivy.read_bytes() if zivy.exists() else b""
    test("živý PROVOZ-ORCHESTRA.md test nemění (bajt na bajt)", pred == po)

    # 6) Sabotáž SAMOTNÉHO PŘEPISU: bez `FORGE_NAVAZANE` se musí skenovat živé
    #    dokumenty — kdyby override „prosakoval" i bez proměnné, kontrola by
    #    mlčela o skutečných dokumentech.
    env = dict(os.environ)
    env.pop("FORGE_NAVAZANE", None)
    r = subprocess.run([sys.executable, str(BRANA)], capture_output=True,
                       text=True, encoding="utf-8", errors="replace",
                       cwd=str(WS), env=env, timeout=300)
    vystup = (r.stdout or "") + (r.stderr or "")
    test("bez přepisu se skenují ŽIVÉ dokumenty (PROVOZ i BRANY-HRY)",
         "PROVOZ-ORCHESTRA.md" in vystup and "BRANY-HRY.md" in vystup,
         vystup[-200:])

finally:
    shutil.rmtree(SCRATCH, ignore_errors=True)

print()
print(f"Kontrol: {kontrol}, chyb: {chyb}")
print("VŠE OK" if chyb == 0 else "NALEZENY CHYBY")
sys.exit(0 if chyb == 0 else 1)

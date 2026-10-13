# -*- coding: utf-8 -*-
"""K3: MUTACNI DUKAZ, ze nove testy a brany rozpoctu skutecne MERI.

PROC: „51/51 zelenych“ nic neznamena, dokud se neukaze, ze to umi spadnout.
Kazda mutace vrati do ZIVEHO stromu jednu vadu a overi se, ze testovaci sada
skonci NENULOVE — a to na POJMENOVANEM testu, ne „nekde“.

Vady:
  M1  ZNAKU_NA_TOKEN 3,03 -> 4,0        -> spadne kalibracni kontrola
  M2  REZIE_CHATU 2 500 -> 0            -> spadne pin konstanty obalu zadani
  M3  `if (chybi.length)` -> `if (false)` v files-to-edit.mjs
                                        -> spadne „deklarovaná sekce není = exit 2“
  M4  `if (trida === 'TOO_LARGE')` -> `if (false)` v rozpocet-granuli.mjs
                                        -> spadne „velký soubor = REQUEST_TOO_LARGE“
  M5  `if (!deklar.length)` -> `if (false)` v rozpocet-granuli.mjs
                                        -> spadne „bez deklarace konvencí = VADA“

Vsechny mutace jdou pres `_mutace.mutuj` (kotva prave 1x, soubor se VZDY vrati,
navrat bajt na bajt) — ne pres vlastni `replace()`.

Pousteni:
    $env:PYTHONIOENCODING='utf-8'; python _analyza/k3-mutace-rozpoctu.py
"""

import pathlib
import subprocess
import sys

ANALYZA = pathlib.Path(__file__).resolve().parent
ORCH = ANALYZA.parent
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

NODE = ORCH / "repo" / ".forge" / "node"
SUITE = NODE / "priprava.test.mjs"
HYGIENA = NODE / "prompt-hygiene.mjs"
ROZPOCET = NODE / "request-budget.mjs"
FILES = ORCH / "repo" / ".forge" / "files-to-edit.mjs"
GRANULI = NODE / "rozpocet-granuli.mjs"

kontrol = 0
chyb = 0


def spust():
    r = subprocess.run([("node.exe" if sys.platform == "win32" else "node"), str(SUITE)],
                       capture_output=True, text=True, encoding="utf-8", errors="replace",
                       cwd=str(ORCH))
    return r.returncode, (r.stdout or "") + (r.stderr or "")


def test(nazev, ok, detail=""):
    global kontrol, chyb
    kontrol += 1
    if ok:
        print(f"ok     {nazev}")
    else:
        chyb += 1
        print(f"CHYBA  {nazev}" + (f"\n       {detail}" if detail else ""))


def pripad(nazev, soubor, stary, novy, cekany_test):
    try:
        with mutuj(soubor, stary, novy) as m:
            kod, vystup = spust()
    except ValueError as e:
        test(f"{nazev}: mutace se provedla", False, str(e))
        return
    test(f"{nazev}: soubor se vratil bajt na bajt", m.hash_po_navratu == m.hash_pred,
         f"{m.hash_pred[:12]} vs {m.hash_po_navratu[:12]}")
    test(f"{nazev}: sada SPADLA (exit != 0)", kod != 0, f"exit={kod}")
    hledany = f"CHYBA  {cekany_test}"
    test(f"{nazev}: spadla na POJMENOVANEM testu ({cekany_test!r})", hledany in vystup,
         "chybejici radek:\n       " + "\n       ".join(
             l for l in vystup.splitlines() if l.startswith("CHYBA")))


# ── kontrola: nezmutovany strom je zeleny ───────────────────────────────────
kod0, vystup0 = spust()
test("KONTROLA: nezmutovana sada = exit 0", kod0 == 0, f"exit={kod0}")
test("KONTROLA: sada ma citac VYSLEDEK", "=== VYSLEDEK:" in vystup0)

pripad("M1 znaky/token 4,0", HYGIENA,
       "export const ZNAKU_NA_TOKEN = 3.03;",
       "export const ZNAKU_NA_TOKEN = 4.0;",
       "KALIBRACNI KONTROLA: 13 000 znaku se pri 3,03 znaku/token NEVEJDE")

pripad("M2 obal zadani 0", ROZPOCET,
       "export const REZIE_CHATU = 2500;",
       "export const REZIE_CHATU = 0;",
       "obal zadani = namerena konstanta (aider posila i obal requestu)")

pripad("M3 chybějící sekce se nekontroluje", FILES,
       "if (chybi.length) {",
       "if (false) {",
       "K3: deklarovaná sekce, která v repu není, = tvrdá chyba (exit 2)")

pripad("M4 velikost přes strop se nekontroluje", GRANULI,
       "if (trida === 'TOO_LARGE') {",
       "if (false) {",
       "K3: granule s velkým souborem = REQUEST_TOO_LARGE (exit 1) — brána měří i velikost")

pripad("M5 chybějící deklarace konvencí se nekontroluje", GRANULI,
       "if (!deklar.length) {",
       "if (false) {",
       "K3: granule bez deklarace konvencí = VADA (exit 1), ne tichý průchod")

print(f"\n=== VYSLEDEK: {kontrol - chyb}/{kontrol} kontrol, {chyb} chyb ===")
sys.exit(1 if chyb else 0)

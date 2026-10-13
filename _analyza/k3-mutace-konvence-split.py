# -*- coding: utf-8 -*-
"""K3: MUTACNI DUKAZ, ze `k3-over-konvence-split.mjs` skutecne MERI.

PROC: brána, ktera se zelená, neni dukaz, ze neco meri. Tahle sada vraci do
ZIVEHO stromu ctyri vady a u kazde overuje, ze brána SPADLA — a to na
POJMENOVANE kontrole (ne „spadla nejak“). Kdyby spadla z jineho duvodu,
test to pozna (`CHYBA: cekana kontrola se v vystupu nevyskytuje`).

Vady (kazda na jine pravidlo):
  M1  ztraceny text v sekci        -> „text se rozesel“
  M2  vymysleny blok v sekci       -> „takovy blok v originalu NEBYL“
  M3  sekce pres 1 200 t           -> „<= 1200 t“
  M4  text sekce v indexu          -> „je v indexu“

Mutace jdou pres `_mutace.mutuj` (kotva prave 1x, soubor se VZDY vrati,
navrat bajt na bajt) — ne pres vlastni `replace()`.

Pousteni:
    $env:PYTHONIOENCODING='utf-8'; python _analyza/k3-mutace-konvence-split.py
"""

import pathlib
import subprocess
import sys

ANALYZA = pathlib.Path(__file__).resolve().parent
ORCH = ANALYZA.parent
sys.path.insert(0, str(ANALYZA))
from _mutace import mutuj  # noqa: E402

BRANA = ANALYZA / "k3-over-konvence-split.mjs"
SEKCE = ORCH / "repo" / "CONVENTIONS"
INDEX = ORCH / "repo" / "CONVENTIONS.md"

kontrol = 0
chyb = 0


def spust():
    r = subprocess.run([("node.exe" if sys.platform == "win32" else "node"), str(BRANA)],
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


def pripad(nazev, soubor, stary, novy, cekana_kontrola):
    """Zmutuje soubor, spusti branu, overi NAVRAT a POJMENOVANOU kontrolu."""
    try:
        with mutuj(soubor, stary, novy) as m:
            kod, vystup = spust()
            vratil_se = None
    except ValueError as e:
        test(f"{nazev}: mutace se provedla", False, str(e))
        return
    # `mutuj` uz soubor vratil (i kdyz brana spadla) — over to znovu:
    vratil_se = m.hash_po_navratu == m.hash_pred
    test(f"{nazev}: soubor se vratil bajt na bajt", vratil_se,
         f"{m.hash_pred[:12]} vs {m.hash_po_navratu[:12]}")
    test(f"{nazev}: brána SPADLA (exit != 0)", kod != 0, f"exit={kod}")
    obsahuje = cekana_kontrola in vystup
    test(f"{nazev}: spadla na POJMENOVANE kontrole ({cekana_kontrola!r})", obsahuje,
         "ocekavany text v vystupu neni:\n" + "\n".join(
             f"       {r}" for r in vystup.splitlines() if "CHYBA" in r))


# ── kontrola: nezmutovany strom je zeleny ───────────────────────────────────
kod0, vystup0 = spust()
test("KONTROLA: nezmutovany strom = exit 0", kod0 == 0, f"exit={kod0}")
test("KONTROLA: vystup ma citac ZMĚŘENO", "ZMĚŘENO:" in vystup0)

# ── M1: ztraceny text v sekci ───────────────────────────────────────────────
pripad("M1 ztraceny text", SEKCE / "01-typy.md",
       "Platí to i pro `get_tree().get_first_node_in_group(...)`",
       "Tenhle text v originalu nebyl.",
       "text se rozesel")

# ── M2: vymysleny blok v sekci ──────────────────────────────────────────────
# Kotva je CELY text, ktery se nahradi — novy text ji NESMI obsahovat
# (knihovna to odmitne, presne omyly #18/#106). Proto se kotva nahrazuje,
# ne obaluje.
pripad("M2 vymysleny blok", SEKCE / "08-meze-a-overeni.md",
       "- Když si nejsi jistý, udělej méně – malý správný krok je lepší než velký\n  rozbitý.",
       "## 99. Vymyšlená sekce\n\nTenhle blok v originále nebyl.",
       "takovy blok v originalu NEBYL")

# ── M3: sekce pres strop 1 200 t ────────────────────────────────────────────
pripad("M3 sekce pres strop", SEKCE / "01-typy.md",
       "Platí to i pro `get_tree().get_first_node_in_group(...)`",
       "x" * 3000,
       "<= 1200 t")

# ── M4: text sekce v indexu ─────────────────────────────────────────────────
# Vkladana cast je delsi nez okno kontroly (40 znaku) — jinak by test netvrdil
# nic o tom, co kontrola umi zachytit.
pripad("M4 text sekce v indexu", INDEX,
       "## Která sekce co řeší (a které § původního dokumentu obsahuje)",
       "## Která sekce co řeší (a které paragrafy původního dokumentu obsahuje)\n\n"
       "Nejčastější chyba free modelů: `var cil := uzel.position + uzel.smer * 40 * delta`.\n",
       "je v indexu")

print(f"\n=== VYSLEDEK: {kontrol - chyb}/{kontrol} kontrol, {chyb} chyb ===")
sys.exit(1 if chyb else 0)

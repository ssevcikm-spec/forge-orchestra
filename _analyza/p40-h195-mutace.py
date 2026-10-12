#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P40 / H195 — MUTAČNÍ BĚH: vrátí vadu do ŽIVÉ brány a doloží, že TEST SPADNE.

PROČ TO EXISTUJE
---------------
`_analyza/p40-h195-test.py` tvrdí, že měří úklid fixtury v CIZÍM repu hry.
Dokázat to jde jen tak, že se **vada vrátí do živé brány** a test zčervená
(`overovani` §1: „prošlo to" bez vrácené vady není důkaz).

CO SE MUTUJE
------------
Přesně naměřená vada H195: úklid fixtury byl **MIMO `finally`** (až na konci
skriptu). Mutace dá do `finally` `pass` a `unlink` postaví ZA blok:

    finally:                                finally:
        FIXTURA.unlink(missing_ok=True)  →      pass  # MUTACE
                                            FIXTURA.unlink(missing_ok=True)

⚠ ZNÁMÝ DRUHÝ DŮSLEDEK (hlásím ho, nezamlčuji): s vrácenou vadou zmizí i kotva
vnitřní mutace TESTU, takže test vykáže navíc `CHYBA mutace se provedla a
soubor vrátila`. To je artefakt mutace, ne druhá vada brány — proto se níž
ověřuje **PRVOTNÍ** důvod červené („fixtura po PŘERUŠENÍ v repu hry NENÍ")
a rozlišuje se od artefaktu.

Použití: python _analyza\p40-h195-mutace.py
Návrat:  0 = test s vrácenou vadou SPADL a brána je vrácena | 1 = nález | 2 = chyba
"""

import hashlib
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
BRANA = ANALYZA / "p20-b2-kontroly.py"
TEST = ANALYZA / "p40-h195-test.py"
HRA = WS.parent / "uo-shadows"
FIXTURA = HRA / "scripts" / "_p20_b2_necitelny.py"
GIT = str(WS / "tools" / "git.cmd")
PY = sys.executable

KOTVA_VADY = "    FIXTURA.unlink(missing_ok=True)"
VADA = ("    pass  # H195-MUTACE: uklid ODSUD VEN (puvodni vada)\n"
        "FIXTURA.unlink(missing_ok=True)")

kontrol = 0
chyb = 0


def zk(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok:
        chyb += 1
        if detail:
            for l in str(detail).splitlines()[-16:]:
                print(f"        {l}")


def git_status() -> str:
    r = subprocess.run([GIT, "-C", str(HRA), "status", "--porcelain"],
                       capture_output=True, shell=True, timeout=120)
    return (r.stdout or b"").decode("utf-8", "replace").strip()


def spust_test() -> tuple:
    r = subprocess.run([PY, "-B", str(TEST)], capture_output=True, cwd=str(WS),
                       timeout=1800)
    v = ((r.stdout or b"").decode("utf-8", "replace")
         + (r.stderr or b"").decode("utf-8", "replace"))
    return r.returncode, v


def spust_branu(vynut: bool = True) -> tuple:
    prikaz = [PY, "-B", str(BRANA)] + (["--vynut-vyjimku"] if vynut else [])
    r = subprocess.run(prikaz, capture_output=True, cwd=str(WS), timeout=900)
    v = ((r.stdout or b"").decode("utf-8", "replace")
         + (r.stderr or b"").decode("utf-8", "replace"))
    return r.returncode, v


def main() -> int:
    if not (BRANA.is_file() and TEST.is_file()):
        print(f"CHYBA: chybí {BRANA} nebo {TEST}")
        return 2

    sys.path.insert(0, str(ANALYZA))
    try:
        from _mutace import mutuj
    except ImportError as e:
        print(f"CHYBA: knihovna `_mutace` není k dispozici ({e})")
        return 2

    sha_pred = hashlib.sha256(BRANA.read_bytes()).hexdigest()
    zaklad = git_status()
    print("=" * 78)
    print("P40 / H195 — MUTAČNÍ BĚH: spadne test, když úklid vrátíme mimo `finally`?")
    print("=" * 78)
    print(f"  brána: {BRANA}")
    print(f"  fixtura: {FIXTURA}")
    print(f"  sha256 před: {sha_pred[:16]} · strom hry: {zaklad!r}")
    print()
    if FIXTURA.exists():
        print("CHYBA: fixtura už na začátku existuje — nejdřív ji ukliď")
        return 2

    # ── 0) NAD ZDRAVOU BRÁNOU TEST PROJDE ──────────────────────────────────
    print("--- 0) nad ZDRAVOU bránou test projde (jinak mutace nic nedokazuje) -")
    rc0, v0 = spust_test()
    zk("zdravá brána → test exit 0", rc0 == 0, v0)
    zk("a fixtura po něm v repu hry NENÍ", not FIXTURA.exists())

    # ── 1) MUTACE + TEST ───────────────────────────────────────────────────
    print()
    print("--- 1) vada se vrací do ŽIVÉ brány (úklid MIMO `finally`) ----------")
    rc_m, v_m = None, ""
    with mutuj(BRANA, KOTVA_VADY, VADA) as m:
        print(f"  kotva {m.pocet_vyskytu}× · sha256 {m.hash_pred[:16]} → "
              f"{m.hash_po_mutaci[:16]}")
        zk("mutace se PROPSALA (hash se změnil)", m.hash_po_mutaci != m.hash_pred)
        zk("vada je v souboru (úklid je za blokem, ne ve `finally`)",
           "H195-MUTACE" in BRANA.read_text(encoding="utf-8"))

        # 1a) PŘÍMÝ DŮKAZ VADY: přerušený běh nechá fixturu v CIZÍM repu
        rc_b, v_b = spust_branu(vynut=True)
        zk("vada: přerušený běh brány fixturu ZŮSTAVÍ (to je H195)",
           FIXTURA.exists(), f"existuje={FIXTURA.exists()}")
        zk("vada: a strom hry je tím PONIČENÝ",
           git_status() != zaklad, "git status: " + repr(git_status()))
        zk("vada: běh brány skončil nenulově (výjimka se nepolkla)", rc_b != 0,
           f"exit={rc_b}")
        # úklid po mutantovi — do cizího repa nesmí nic zůstat
        FIXTURA.unlink(missing_ok=True)
        zk("po ručním úklidu je strom hry zase ČISTÝ", git_status() == zaklad,
           repr(git_status()))

        # 1b) CELÝ TEST s vrácenou vadou MUSÍ SPADNOUT
        rc_m, v_m = spust_test()
    # tady už je brána vrácená knihovnou

    zk("s vrácenou vadou TEST SPADL (exit != 0)", rc_m != 0, f"exit={rc_m}\n" + v_m)
    zk("padla PRVOTNÍ kontrola „H195: po PŘERUŠENÍ fixtura v repu hry NENÍ“",
       "CHYBA H195: po PŘERUŠENÍ fixtura v repu hry NENÍ" in v_m, v_m)
    zk("padla i kontrola čistoty stromu hry po přerušení",
       "CHYBA H195: strom hry je po PŘERUŠENÍ ČISTÝ" in v_m, v_m)
    zk("(očekávaný artefakt mutace) padla i vnitřní mutační fáze testu",
       "CHYBA mutace se provedla a soubor vrátila" in v_m,
       "artefakt: s vrácenou vadou zmizela i kotva vnitřní mutace testu")

    # ── 2) NÁVRAT BAJT NA BAJT A ZDRAVÝ BĚH ───────────────────────────────
    print()
    print("--- 2) brána vrácena a test znovu projde ----------------------------")
    sha_po = hashlib.sha256(BRANA.read_bytes()).hexdigest()
    zk("brána vrácena BAJT NA BAJT (sha256 souhlasí)", sha_po == sha_pred,
       f"{sha_pred[:16]} vs {sha_po[:16]}")
    zk("vrácený soubor vadu NEOBSAHUJE",
       "H195-MUTACE" not in BRANA.read_text(encoding="utf-8"))
    zk("fixtura v repu hry NENÍ", not FIXTURA.exists())
    zk("strom hry je ČISTÝ", git_status() == zaklad, repr(git_status()))
    rc_z, v_z = spust_test()
    zk("po vrácení test zase projde (exit 0) — mutace nezanechala následek",
       rc_z == 0, v_z)

    print()
    print("=" * 78)
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb · test: zdravá brána exit={rc0}, "
          f"s vadou exit={rc_m}, po vrácení exit={rc_z}")
    print(f"          sha256 brány: {sha_po[:16]} (před {sha_pred[:16]}) · "
          f"strom hry {git_status()!r}")
    print("=" * 78)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

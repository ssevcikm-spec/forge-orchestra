#!/usr/bin/env python
# -*- coding: utf-8 -*-
r"""P40 / H189 — MUTAČNÍ BĚH: vrátí vadu do ŽIVÉ brány a doloží, že TEST SPADNE.

PROČ TO EXISTUJE
---------------
Test `p40-h189-test.py` tvrdí, že měří čtení dvojic z CELÉHO BLOKU hlavičky.
Dokázat to jde JEN tak, že se vada vrátí do ŽIVÉ brány (`_analyza/zadani-kontrola.py`)
a **test zčervená** — zelený test nad zdravým kódem neznamená nic
(`overovani` §1: „prošlo to" bez vrácené vady není důkaz).

CO SE MUTUJE (a proč PRÁVĚ tohle)
--------------------------------
Původní vada H189 byla: dvojice se čtou z JEDNOHO řádku (toho s klíčem).
Mutace proto bere text bloku z řádku s klíčem:

    text_bloku = "\n".join(blok)        →        text_bloku = radek_stavu or ""

⚠ Záměrně se NEMUTUJE `dvojice_bloku = … findall(text_bloku)` (kotva vnitřní
mutace testu): kdyby zmizela, spadly by i kontroly *uvnitř* testu a jeho
červená by byla **ze špatného důvodu** (`overovani` §10.1). Takhle padne
PRÁVĚ ta kontrola, která má padnout — „HRA SE SKUTEČNĚ POROVNALA (H189)" —
a vnitřní mutační fáze testu zůstane zelená (důkaz, že červená není artefakt).

Použití: python _analyza\p40-h189-mutace.py
Návrat:  0 = test s vrácenou vadou SPADL a brána je vrácena | 1 = nález | 2 = chyba běhu
"""

import hashlib
import pathlib
import subprocess
import sys

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parent.parent
ANALYZA = WS / "_analyza"
BRANA = ANALYZA / "zadani-kontrola.py"
TEST = ANALYZA / "p40-h189-test.py"
PY = sys.executable

# ⚠ KOTVA: `text_bloku` je text CELÉHO BLOKU (oprava H189). Vada = vzít ho
# z jednoho řádku. Kotva musí být v souboru právě 1× — hlídá `_mutace.mutuj`.
KOTVA_VADY = 'text_bloku = "\\n".join(blok)'
VADA = 'text_bloku = radek_stavu or ""'

kontrol = 0
chyb = 0


def zk(popis: str, ok: bool, detail: str = "") -> None:
    global kontrol, chyb
    kontrol += 1
    print(f"  {'OK   ' if ok else 'CHYBA'} {popis}")
    if not ok:
        chyb += 1
        if detail:
            for l in str(detail).splitlines()[-14:]:
                print(f"        {l}")


def spust_test() -> tuple:
    r = subprocess.run([PY, "-B", str(TEST)], capture_output=True, cwd=str(WS),
                       timeout=900)
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

    print("=" * 78)
    print("P40 / H189 — MUTAČNÍ BĚH: spadne test, když se vada vrátí?")
    print("=" * 78)
    sha_pred = hashlib.sha256(BRANA.read_bytes()).hexdigest()
    print(f"  brána: {BRANA}")
    print(f"  sha256 před: {sha_pred[:16]}  ({len(BRANA.read_bytes())} B)")
    print()

    # ── 0) KONTROLA: nad zdravou bránou musí test projít ────────────────────
    print("--- 0) nad ZDRAVOU bránou test projde (jinak by mutace nic nedokazovala)")
    rc0, v0 = spust_test()
    zk("zdravá brána → test exit 0", rc0 == 0, v0)

    # ── 1) MUTACE + BĚH TESTU ───────────────────────────────────────────────
    print()
    print("--- 1) do živé brány se vrací VADA (dvojice z jednoho řádku) -----")
    rc_m = None
    v_m = ""
    with mutuj(BRANA, KOTVA_VADY, VADA) as m:
        print(f"  kotva nalezena {m.pocet_vyskytu}× · sha256 po mutaci "
              f"{m.hash_po_mutaci[:16]} (před {m.hash_pred[:16]})")
        zk("mutace se PROPSALA na disk (hash se změnil)",
           m.hash_po_mutaci != m.hash_pred)
        zk("text bloku se bere Z JEDNOHO ŘÁDKU (vada je v souboru)",
           VADA in BRANA.read_text(encoding="utf-8"))
        rc_m, v_m = spust_test()
    # tady už je soubor vrácený knihovnou

    zk("s vrácenou vadou TEST SPADL (exit != 0)", rc_m != 0, f"exit={rc_m}\n" + v_m)
    # ⚠ Ne jen „spadl" — musí spadnout NA TÉ KONTROLE, kvůli které existuje.
    zk("padla PRÁVĚ kontrola „HRA SE SKUTEČNĚ POROVNALA (H189)“",
       "CHYBA HRA SE SKUTEČNĚ POROVNALA" in v_m, v_m)
    zk("a v detailu je vidět, že brána hru PŘESKOČILA "
       "(„uo-shadows: zadání netvrdí žádný commit“)",
       "uo-shadows: zadání netvrdí žádný commit" in v_m, v_m)
    zk("vnitřní mutační fáze testu zůstala ZELENÁ "
       "(červená tedy není artefakt chybějící kotvy)",
       "OK    MUTACE: hra se NEporovnala" in v_m, v_m)

    # ── 2) NÁVRAT BAJT NA BAJT ──────────────────────────────────────────────
    print()
    print("--- 2) brána vrácena a znovu měří ---------------------------------")
    sha_po = hashlib.sha256(BRANA.read_bytes()).hexdigest()
    zk("brána vrácena BAJT NA BAJT (sha256 souhlasí)", sha_po == sha_pred,
       f"{sha_pred[:16]} vs {sha_po[:16]}")
    zk("vrácený soubor už vadu NEOBSAHUJE", VADA not in BRANA.read_text(encoding="utf-8"))
    rc_z, v_z = spust_test()
    zk("po vrácení test zase projde (exit 0) — mutace nezanechala následek",
       rc_z == 0, v_z)

    print()
    print("=" * 78)
    print(f"VÝSLEDEK: {kontrol} kontrol, {chyb} chyb · "
          f"test nad zdravou bránou exit={rc0}, s vrácenou vadou exit={rc_m}, "
          f"po vrácení exit={rc_z}")
    print(f"          sha256 brány: {sha_po[:16]} (před {sha_pred[:16]})")
    print("=" * 78)
    return 1 if chyb else 0


if __name__ == "__main__":
    sys.exit(main())

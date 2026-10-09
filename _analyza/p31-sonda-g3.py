# -*- coding: utf-8 -*-
r"""P31 — SONDA: PROČ je druhá chyba v `p28-b-mutace.py` (a co dělá jeho M2).

JEDNORÁZOVÁ DIAGNOSTIKA (patří do `PRESKIP` v `p20-d-doklady.py`), ne doklad.

CO MĚŘÍ (nic nepředpokládá — obojí spouští a čte výstup):

  1. **Živé `g3`** (s `FORGE_REGISTR` do scratch, aby se nepřepsal živý registr):
     kolik bran, kolik NEDEKLAROVANÝCH exitů, kolik bran BEZ ČÍTAČE a jaký je
     `VÝSLEDEK g3` — tedy **proč `g3` končí nenulovým exitem**, když měřidlo
     P28 v A6 čeká `exit 0`.

  2. **M2 mutace `g3` TAK, JAK JI DĚLÁ `p28-b-mutace.py`** (vloží fixturu na
     začátek `BRANY`). Měří se, jestli mutant **vůbec vykázal 50 bran**, nebo
     spadl — protože „mutace, která se tiše neprovedla / spadla jinam, tvrdí
     totéž co mutace, která prošla" (`AGENTS.md`).

Použití: python _analyza/p31-sonda-g3.py
"""

import os
import pathlib
import re
import subprocess
import sys
import time

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WS = pathlib.Path(__file__).resolve().parents[1]
ANALYZA = WS / "_analyza"
G3 = ANALYZA / "g3-brany.py"
SCRATCH = ANALYZA / "p31-scratch"
DOKLAD = ANALYZA / "p31-sonda-g3-vystup.txt"

_vystup = []


def p(s=""):
    print(s)
    _vystup.append(s)


def spust(args, env=None, timeout=3600):
    e = {**os.environ, "PYTHONIOENCODING": "utf-8", **(env or {})}
    t0 = time.time()
    r = subprocess.run([str(a) for a in args], cwd=str(WS), env=e,
                       capture_output=True, timeout=timeout)
    out = (r.stdout or b"").decode("utf-8", "replace") + \
          (r.stderr or b"").decode("utf-8", "replace")
    return r.returncode, out, time.time() - t0


def main():
    SCRATCH.mkdir(parents=True, exist_ok=True)
    p("# P31 — SONDA `g3` (živý stav a M2 mutace) · %s" % time.strftime("%Y-%m-%d %H:%M:%S"))
    p("")

    # ── 1) živé g3 ───────────────────────────────────────────────────────────
    p("## 1) ŽIVÉ `g3` (registr do scratch, živý se nepřepíše)")
    # ⚠ NAMĚŘENO 9. 10. 2026 (tahle sonda, první běh): bez PŘEGENEROVÁNÍ inventáře
    # hlásí `g3` **2 NEDEKLAROVANÉ exity a 2 brány bez čítače** (`n1-over-inventar`,
    # `C2: mutace N1`) — a vypadá to jako vada `g3`. Je to přesně **H126**:
    # zastaralý inventář shodí DVĚ brány. Náprava je přegenerovat, ne deklarovat.
    kod_inv, out_inv, tr_inv = spust(
        [sys.executable, str(ANALYZA / "hl-neanglicky-v-kodu.py"),
         "--json", str(ANALYZA / "_inventar.json")])
    p("inventář přegenerován PŘED g3: exit=%d (%.0f s) — jinak g3 hlásí H126"
      % (kod_inv, tr_inv))
    reg = SCRATCH / "registr-sonda.json"
    kod, out, tr = spust([sys.executable, str(G3)], env={"FORGE_REGISTR": str(reg)})
    p("exit=%d (%.0f s)" % (kod, tr))
    for vzor in (r"brán celkem:.*", r"NENULOVÉ EXITY:.*", r"očekávaný:.*",
                 r"NEOČEKÁVANÝ:.*", r"BRÁNY BEZ ČÍTAČE.*",
                 r"NEOTEVŘENÉ BRÁNY.*", r"VÝSLEDEK g3:.*", r"VISUTÉ.*"):
        for m in re.finditer("^" + vzor, out, re.M):
            p("  " + m.group(0)[:200])
    p("")
    p("  (plný výstup: %d znaků)" % len(out))

    # ── 2) M2 mutace tak, jak ji dělá p28-b-mutace.py ────────────────────────
    p("")
    p("## 2) M2 mutace: fixtura vložená na začátek `BRANY` (jak to dělá P28/B)")
    fixtura = SCRATCH / "p31-fixtura-brana.py"
    fixtura.write_bytes(b'print("0 kontrol, 0 chyb")\n')
    mutant = SCRATCH / "g3-mutant-m2.py"
    # ⚠ KOPIE MUSÍ LEŽET VE STEJNÉM ADRESÁŘI JAKO ORIGINÁL? `g3` si kořen
    # odvozuje z `__file__` — proto se cesta nahrazuje absolutní (měřeno zde).
    zdroj = G3.read_text(encoding="utf-8")
    if zdroj.count("BRANY = [") != 1:
        p("  NEZMĚŘENO: `BRANY = [` je v g3 %d×" % zdroj.count("BRANY = ["))
    else:
        text_mut = zdroj.replace(
            "BRANY = [", 'BRANY= [("p31-fixtura", ["python", %r]),' % str(fixtura))
        text_mut = re.sub(r"^WS = .*$",
                          lambda m: "WS = pathlib.Path(r'%s')" % WS,
                          text_mut, count=1, flags=re.M)
        mutant.write_bytes(text_mut.encode("utf-8"))
        p("  mutant: %s" % mutant.relative_to(WS))
        p("  vložený text: %r" % 'BRANY= [("p31-fixtura", ["python", "<fixtura>"]),')
        p("  ⚠ formát ŽIVÝCH záznamů v `BRANY` je `(popis, prikaz, vzor)` — 3 prvky")
        p("  (ověřeno čtením `g3-brany.py`); vložený záznam má prvky 2.")
        kod2, out2, tr2 = spust([sys.executable, str(mutant)],
                                env={"FORGE_REGISTR": str(SCRATCH / "registr-m2.json")})
        p("  exit=%d (%.0f s)" % (kod2, tr2))
        m = re.search(r"brán celkem:\s*(\d+)", out2)
        p("  g3 hlásí 'brán celkem: %s'" % (m.group(1) if m else "— (NENAMĚŘENO)"))
        p("  ValueError v tracebacku: %s" % ("ANO" if "ValueError" in out2 else "NE"))
        p("  ... not enough values to unpack: %s"
          % ("ANO" if "not enough values to unpack" in out2 else "NE"))
        for l in out2.splitlines()[-6:]:
            p("    | " + l[:160])

    p("")
    p("## 3) M2 mutace s PLATNÝM záznamem (3 prvky) — co `g3` vykáže")
    mut2 = SCRATCH / "g3-mutant-platny.py"
    zapis = 'BRANY= [("p31-fixtura", ["python", %r], r"(\\d+)"),' % str(fixtura)
    text2 = G3.read_text(encoding="utf-8").replace("BRANY = [", zapis)
    text2 = re.sub(r"^WS = .*$", lambda m: "WS = pathlib.Path(r'%s')" % WS,
                   text2, count=1, flags=re.M)
    mut2.write_bytes(text2.encode("utf-8"))
    kod3, out3, tr3 = spust([sys.executable, str(mut2)],
                            env={"FORGE_REGISTR": str(SCRATCH / "registr-m2b.json")})
    p("  exit=%d (%.0f s)" % (kod3, tr3))
    for vzor in (r"brán celkem:.*", r"NENULOVÉ EXITY:.*", r"očekávaný:.*",
                 r"NEOČEKÁVANÝ:.*", r"BRÁNY BEZ ČÍTAČE.*", r"VÝSLEDEK g3:.*",
                 r"VISUTÉ.*", r"NEOTEVŘENÉ.*"):
        for m in re.finditer("^" + vzor, out3, re.M):
            p("  " + m.group(0)[:200])

    p("")
    p("## 4) REPRODUKCE M2c: mutant `g3` (50 bran) + OSLABENÉ měřidlo P28/A")
    p("   (hledá se DRUHÁ chyba, kterou P31 naměřilo jako `M2c … naměřeno: 2`)")
    P28A = ANALYZA / "p28-a-overeni.py"
    zdroj_a = P28A.read_text(encoding="utf-8")
    kotva = "int(m.group(1)) if m else None, 49)"
    kopie_a = ANALYZA / "_p31-sonda-m2c-meridlo.py"
    kopie_g = ANALYZA / "_p31-sonda-m2c-g3.py"
    if zdroj_a.count(kotva) != 1:
        p("  NEZMĚŘENO: kotva pro oslabení je v p28-a %d×" % zdroj_a.count(kotva))
    else:
        zdroj_g = G3.read_text(encoding="utf-8").replace(
            "BRANY = [", 'BRANY= [("p31-fixtura", ["python", %r], r"(\\d+)"),' % str(fixtura))
        zdroj_g = re.sub(r"^WS = .*$", lambda m: "WS = pathlib.Path(r'%s')" % WS,
                         zdroj_g, count=1, flags=re.M)
        kopie_g.write_bytes(zdroj_g.encode("utf-8"))
        kopie_a.write_bytes(zdroj_a.replace(
            kotva, "int(m.group(1)) if m else None, int(m.group(1)) if m else None)"
        ).encode("utf-8"))
        reg2 = SCRATCH / "registr-m2c.json"
        kod4, out4, tr4 = spust([sys.executable, str(kopie_a), "--plne", "--jen", "A6",
                                 "--g3", str(kopie_g), "--vystup",
                                 str(SCRATCH / "m2c-vystup.txt")],
                                env={"FORGE_REGISTR": str(reg2)})
        p("  exit=%d (%.0f s)" % (kod4, tr4))
        p("  ČERVENÉ KONTROLY:")
        for l in out4.splitlines():
            if "CHYBA" in l and "čekáno" not in l:
                p("    " + l.strip()[:170])
        p("  (plný výstup: p31-scratch/m2c-vystup.txt)")
        for q in (kopie_a, kopie_g):
            q.unlink(missing_ok=True)
        p("  kopie smazané: %s" % [q.name for q in (kopie_a, kopie_g) if q.exists()])

    p("")
    p("## ZÁVĚR SONDY")
    p("  1) živé g3 končí exit=%d — viz 'VÝSLEDEK g3' a 'BRÁNY BEZ ČÍTAČE' výš" % kod)
    p("  2) M2 mutant: viz 'brán celkem' a ValueError výš")
    p("  3) M2 s PLATNÝM záznamem: brán celkem=%s, NEDEKLAROVANÝCH=%s, exit=%d"
      % (re.search(r"brán celkem:\s*(\d+)", out3).group(1) if re.search(r"brán celkem:\s*(\d+)", out3) else "—",
         re.search(r"NEDEKLAROVANÝCH\s+(\d+)", out3).group(1) if re.search(r"NEDEKLAROVANÝCH\s+(\d+)", out3) else "—",
         kod3))
    DOKLAD.write_bytes(("\n".join(_vystup) + "\n").encode("utf-8"))
    print("\n[doklad] %s (%d B)" % (DOKLAD.relative_to(WS), DOKLAD.stat().st_size))
    return 0


if __name__ == "__main__":
    sys.exit(main())
